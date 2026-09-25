"""Memoria por espacos (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 1).

Inspirada no Dwarf Fortress: poucos espacos, uma memoria por categoria, a mais
forte vence; relembrar reaplica o efeito. Sem rng: relembrar segue um
cronograma fixo (a cada `relembrar_ticks_acordado` de tempo acordado).

Funcao pura dos eventos que ja chegam a politica (como a memoria B1):
  - acoes do dono: receber_acao_dono(acao, tick);
  - acoes do proprio pet: observar(transicao).
O replay reconstroi os espacos inteiros.

Regras (todas as comparacoes pela intensidade ORIGINAL da memoria):
  - curto prazo: `n_curto` espacos, no maximo um por categoria. Mesma categoria
    presente: a nova substitui se for mais forte ou igual (empate: vence a mais
    recente); senao e descartada. Categoria ausente e espacos cheios: substitui a
    mais fraca (empate entre as mais fracas: sai a mais antiga) se for mais forte
    ou igual a ela; senao e descartada.
  - apos `d_curto_ticks`, a memoria sai do curto e tenta o longo prazo
    (`n_longo` espacos, mesma regra); nao entrando, e descartada. Longo prazo e
    permanente ate ser substituido.
  - ativacao = intensidade * exp(-(tick - ultima relembranca) / tau). A cada
    `relembrar_ticks_acordado` de tempo acordado, todas as memorias sao
    relembradas (ativacao volta a intensidade). O tempo acordado e medido nas
    decisoes do pet (a cada `Config.intervalo` ticks), com o estado de sono da
    observacao.
Categorias: demora (latencia do dono num pedido; atendimento imediato nao gera
memoria; pedido perdido vale 1), bronca, elogio, carinho (acariciar ou brincar
do dono). sujeira e treino_forcado existem no catalogo mas ficam inativas.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .config import CONFIG_MEMORIA_ESPACOS, ConfigMemoriaEspacos
from .events import AcaoPet, AcaoUsuario
from .policies.bandit import PoliticaBandit
from .policy import Observacao, Transicao

FATORES_ESPACOS = ("demora", "bronca", "elogio", "carinho")
_ATENDE = {AcaoUsuario.ALIMENTAR: "fome", AcaoUsuario.LIMPAR: "higiene"}
_CATEGORIA_DA_ACAO = {AcaoUsuario.REPREENDER: "bronca", AcaoUsuario.ELOGIAR: "elogio",
                      AcaoUsuario.ACARICIAR: "carinho", AcaoUsuario.BRINCAR: "carinho"}
_IDX_DORMINDO = 6        # posicao de "dormindo" em Observacao.vetor_estado


class CategoriaInvalida(ValueError):
    pass


@dataclass(frozen=True)
class Memoria:
    categoria: str
    intensidade: float
    criada: int              # tick de criacao
    relembrada: int          # tick da ultima relembranca (ou da criacao)
    ref: int | None          # ordinal da acao do dono que criou a memoria (None: pedido perdido)

    def ativacao(self, tick: int, tau: float) -> float:
        return self.intensidade * math.exp(-max(0, tick - self.relembrada) / tau)

    def para_dict(self) -> dict:
        return {"categoria": self.categoria, "intensidade": self.intensidade, "criada": self.criada,
                "relembrada": self.relembrada, "ref": self.ref}


def inserir(espacos: list[Memoria], nova: Memoria, n: int) -> tuple[list[Memoria], str]:
    """Regra do adendo. Devolve (novos espacos, 'entrou'|'substituiu'|'descartada')."""
    mesma = [m for m in espacos if m.categoria == nova.categoria]
    if mesma:
        velha = mesma[0]
        if nova.intensidade >= velha.intensidade:
            return [nova if m is velha else m for m in espacos], "substituiu"
        return list(espacos), "descartada"
    if len(espacos) < n:
        return list(espacos) + [nova], "entrou"
    fraca = min(espacos, key=lambda m: (m.intensidade, m.criada))
    if nova.intensidade >= fraca.intensidade:
        return [nova if m is fraca else m for m in espacos], "substituiu"
    return list(espacos), "descartada"


class MemoriaEspacos:
    def __init__(self, cfg: ConfigMemoriaEspacos | None = None) -> None:
        self.cfg = cfg or CONFIG_MEMORIA_ESPACOS
        for c in self.cfg.ativas:
            if c not in self.cfg.categorias:
                raise CategoriaInvalida(f"categoria ativa fora do catalogo: {c!r}")
        self.curto: list[Memoria] = []
        self.longo: list[Memoria] = []
        self.n_dono = 0
        self.pendentes: dict[str, list[int]] = {"fome": [], "higiene": []}
        self.acordado = 0                 # ticks acordado acumulados
        self.tick = 0                     # ultimo tick processado
        self._dormindo = False
        self.relembrancas: list[int] = []  # ticks de relembranca (diagnostico/teste)
        self.contagem = {"entrou": 0, "substituiu": 0, "descartada": 0, "promovida": 0, "esquecida": 0}

    # ------------------------------------------------------------ tempo
    def avancar(self, tick: int, dormindo: bool | None = None) -> None:
        """Processa o tempo ate `tick` (tempo acordado, relembrancas e promocoes, em ordem) com o
        estado de sono ANTERIOR; `dormindo`, se dado, vale de `tick` em diante (e o estado que o pet
        observa na decisao desse tick)."""
        if tick < self.tick:
            raise ValueError(f"tempo voltou: {tick} < {self.tick}")
        cfg = self.cfg
        t = self.tick
        while t < tick:
            # proximo marco: relembranca (se acordado) ou promocao
            fim = tick
            if not self._dormindo:
                falta = cfg.relembrar_ticks_acordado - self.acordado % cfg.relembrar_ticks_acordado
                fim = min(fim, t + falta)
            promo = [m.criada + cfg.d_curto_ticks for m in self.curto if m.criada + cfg.d_curto_ticks > t]
            if promo:
                fim = min(fim, min(promo))
            if not self._dormindo:
                self.acordado += fim - t
            t = fim
            self._promover(t)
            if not self._dormindo and self.acordado % cfg.relembrar_ticks_acordado == 0 and self.acordado > 0:
                self._relembrar(t)
        self.tick = tick
        if dormindo is not None:
            self._dormindo = dormindo

    def _promover(self, tick: int) -> None:
        vencidas = sorted((m for m in self.curto if m.criada + self.cfg.d_curto_ticks <= tick),
                          key=lambda m: (m.criada, m.categoria))
        for m in vencidas:
            self.curto.remove(m)
            self.longo, r = inserir(self.longo, m, self.cfg.n_longo)
            self.contagem["promovida" if r != "descartada" else "esquecida"] += 1

    def _relembrar(self, tick: int) -> None:
        if self.relembrancas and self.relembrancas[-1] == tick:
            return
        self.relembrancas.append(tick)
        self.curto = [replace(m, relembrada=tick) for m in self.curto]
        self.longo = [replace(m, relembrada=tick) for m in self.longo]

    # ------------------------------------------------------------ eventos
    def lembrar(self, categoria: str, intensidade: float, tick: int, ref: int | None) -> None:
        if categoria not in self.cfg.categorias:
            raise CategoriaInvalida(f"categoria desconhecida: {categoria!r}")
        if categoria not in self.cfg.ativas:
            return                         # existe no catalogo, mas a tarefa que a liga ainda nao existe
        if not 0.0 < intensidade <= 1.0:
            raise ValueError(f"intensidade fora de (0, 1]: {intensidade}")
        self.avancar(tick)
        self.curto, r = inserir(self.curto, Memoria(categoria, intensidade, tick, tick, ref), self.cfg.n_curto)
        self.contagem[r] += 1

    def pedido(self, obs: Observacao, tick: int) -> None:
        fome, higiene = obs.vetor_estado[0], obs.vetor_estado[1]
        nec, valor = ("fome", fome) if fome <= higiene else ("higiene", higiene)
        if valor < self.cfg.limiar_necessidade_pedido:
            self.pendentes[nec].append(tick)

    def expirar(self, tick: int) -> None:
        for nec, ticks in self.pendentes.items():
            perdidos = [t for t in ticks if tick - t > self.cfg.janela_latencia_ticks]
            if perdidos:
                self.pendentes[nec] = [t for t in ticks if t not in perdidos]
                # pedido perdido: demora maxima, sem acao do dono de origem; a memoria nasce
                # quando o pet percebe (proximo evento), pois o tempo da memoria nao volta
                self.lembrar("demora", 1.0, max(tick, self.tick), None)

    def acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self.n_dono += 1
        self.expirar(tick)
        nec = _ATENDE.get(acao)
        if nec is not None and self.pendentes[nec]:
            lat = tick - self.pendentes[nec][0]
            self.pendentes[nec] = []
            if lat > 0:
                self.lembrar("demora", min(1.0, lat / self.cfg.janela_latencia_ticks), tick, self.n_dono)
        cat = _CATEGORIA_DA_ACAO.get(acao)
        if cat is not None:
            base = self.cfg.categorias[cat]
            self.lembrar(cat, base, tick, self.n_dono)
        self.avancar(tick)

    # ------------------------------------------------------------ leitura (pura)
    def features(self, tick: int) -> list[float]:
        tau = self.cfg.tau_ativacao_ticks
        return [min(1.0, sum(m.ativacao(tick, tau) for m in self.curto + self.longo if m.categoria == c))
                for c in FATORES_ESPACOS]

    def refs(self, tick: int | None = None) -> dict[str, int | None]:
        """categoria -> ordinal da acao do dono que criou a memoria mais ativa dela (ou None)."""
        tick = self.tick if tick is None else tick
        tau = self.cfg.tau_ativacao_ticks
        saida = {}
        for c in FATORES_ESPACOS:
            ms = [m for m in self.curto + self.longo if m.categoria == c]
            saida[c] = max(ms, key=lambda m: (m.ativacao(tick, tau), m.criada)).ref if ms else None
        return saida

    def para_dict(self) -> dict:
        return {"n_dono": self.n_dono, "tick": self.tick, "acordado": self.acordado, "dormindo": self._dormindo,
                "pendentes": {k: list(v) for k, v in self.pendentes.items()},
                "curto": [m.para_dict() for m in self.curto], "longo": [m.para_dict() for m in self.longo],
                "relembrancas": len(self.relembrancas), "contagem": dict(self.contagem)}


class PoliticaBanditEspacos(PoliticaBandit):
    """Bandit da v1 com as features da memoria por espacos (uma por categoria ativa)."""

    nome = "bandit_thompson_espacos"

    def __init__(self, cfg=None, cfg_bandit=None, cfg_memoria: ConfigMemoriaEspacos | None = None) -> None:
        self.memoria = MemoriaEspacos(cfg_memoria)
        super().__init__(cfg, cfg_bandit)

    def n_features(self) -> int:
        return super().n_features() + len(FATORES_ESPACOS)

    def _tick_de(self, obs: Observacao) -> int:
        return obs.ticks_desde_cuidado + self._tick_ultimo_cuidado

    def _features(self, obs: Observacao) -> list[float]:
        return super()._features(obs) + self.memoria.features(self._tick_de(obs))

    def agir(self, obs, rng):
        acao = super().agir(obs, rng)
        self._ultima_decisao["fatores_memoria"] = FATORES_ESPACOS
        self._ultima_decisao["refs_memoria"] = self.memoria.refs(self._tick_de(obs))
        return acao

    def observar(self, transicao: Transicao) -> None:
        super().observar(transicao)          # usa as features ANTES de registrar o proprio pedido
        tick = self._tick_ultima_decisao
        self.memoria.avancar(tick, dormindo=bool(transicao.observacao.vetor_estado[_IDX_DORMINDO] >= 0.5))
        self.memoria.expirar(tick)
        if transicao.acao is AcaoPet.CHAMAR_ATENCAO:
            self.memoria.pedido(transicao.observacao, tick)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        super().receber_acao_dono(acao, tick)
        self.memoria.acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        d = super().estado_interno()
        d["memoria_espacos"] = self.memoria.para_dict()
        return d
