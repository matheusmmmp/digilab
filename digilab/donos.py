"""Donos sinteticos (Etapa 2).

Todos os donos enxergam o pet pela mesma `Visao` e respondem com uma
lista de `AcaoUsuario`. Quem conta e impoe o orcamento e o simulador
(`digilab.treino.CanalDeInteracao`), nao o dono: um dono que devolva mais
acoes do que o permitido faz o simulador levantar erro.

Para que todos os bracos terminem com EXATAMENTE o mesmo numero de
interacoes, a `Visao` traz `minimo_obrigatorio`: quanto o dono precisa
gastar neste passo para ainda conseguir fechar o orcamento dado o teto
fisico por passo. Cada dono decide COMO completar esse minimo; o
simulador so verifica.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .config import CONFIG_DONOS, CONFIG_PADRAO, TICKS_POR_DIA, ConfigDonos
from .events import ACOES_V1, AcaoPet, AcaoUsuario

CUIDADOS = (AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR)


@dataclass(frozen=True)
class Visao:
    """O que o dono ve em cada passo. Montada pelo simulador."""

    estado: dict             # motor.estado(), inclui acao_atual
    passo: int               # indice do passo atual, 0..passos_totais-1
    passos_totais: int
    orcamento: int
    gasto: int
    minimo_obrigatorio: int
    maximo_permitido: int

    @property
    def restante(self) -> int:
        return self.orcamento - self.gasto

    @property
    def gasto_no_ritmo(self) -> float:
        """Quanto ja deveria ter sido gasto num ritmo uniforme ate este passo."""
        return self.orcamento * (self.passo + 1) / self.passos_totais

    @property
    def atrasado(self) -> bool:
        return self.gasto < self.gasto_no_ritmo


@runtime_checkable
class Dono(Protocol):
    nome: str

    def decidir(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        """Acoes deste passo. Tamanho entre minimo_obrigatorio e maximo_permitido."""


# ------------------------------------------------------------------ regras


def cuidados_necessarios(estado: dict, cfg: ConfigDonos) -> list[AcaoUsuario]:
    """Cuidado guiado por necessidade, em ordem de prioridade."""
    acoes: list[AcaoUsuario] = []
    if estado["fome"] < cfg.limiar_alimentar:
        acoes.append(AcaoUsuario.ALIMENTAR)
    if estado["higiene"] < cfg.limiar_limpar or estado["sujeira"] >= cfg.sujeira_para_limpar:
        acoes.append(AcaoUsuario.LIMPAR)
    if estado["humor"] < cfg.limiar_humor_brincar:
        acoes.append(AcaoUsuario.BRINCAR)
    return acoes


def julgar_acao(estado: dict, cfg: ConfigDonos) -> int:
    """Feedback coerente: +1 elogia, -1 repreende, 0 nada a dizer.

    E a definicao operacional de "comportamento adequado" usada pelo dono
    atencioso. E uma escolha de desenho, registrada aqui e em config.
    """
    acao = AcaoPet(estado["acao_atual"])
    energia = estado["energia"]
    menor_necessidade = min(estado["fome"], estado["higiene"])
    noite = CONFIG_PADRAO.e_noite(estado["tick_do_dia"])
    precisa_ajuda = menor_necessidade < cfg.limiar_necessidade_pedido_adequado
    cansado = energia < cfg.limiar_energia_sono_adequado

    if acao is AcaoPet.DORMIR:
        return 1 if (cansado or noite) else -1
    if acao is AcaoPet.CHAMAR_ATENCAO:
        return 1 if precisa_ajuda else -1
    if acao is AcaoPet.EMBURRAR:
        return -1
    if acao in (AcaoPet.BRINCAR, AcaoPet.EXPLORAR):
        return -1 if (cansado or precisa_ajuda) else 1
    if acao is AcaoPet.COMER:
        return 1 if estado["fome"] < cfg.limiar_alimentar else 0
    if acao is AcaoPet.OCIOSO:
        return 0
    if acao is AcaoPet.ALIVIAR:
        # o banheiro (TAREFA_V2_BANHEIRO, secao 5): o dono de cuidado nao julga onde o pet alivia (nem bronca nem elogio); o carinho
        # depois do banheiro e do DonoCarinhoBanheiro, fora do orcamento. Nas vidas de hoje o aliviar nao existe: nada muda
        return 0
    raise ValueError(f"acao do pet sem regra de julgamento: {acao}")  # pragma: no cover


def _feedback(sinal: int) -> AcaoUsuario:
    if sinal > 0:
        return AcaoUsuario.ELOGIAR
    if sinal < 0:
        return AcaoUsuario.REPREENDER
    raise ValueError("sinal zero nao vira feedback")


class _DonoBase:
    nome = "base"

    def __init__(self, cfg: ConfigDonos | None = None) -> None:
        self.cfg = cfg or CONFIG_DONOS

    def decidir(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        acoes = self._desejo(visao, rng)[: visao.maximo_permitido]
        while len(acoes) < visao.minimo_obrigatorio:
            acoes.append(self._preencher(visao, rng))
        return acoes

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        raise NotImplementedError

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        raise NotImplementedError


class DonoAtencioso(_DonoBase):
    """Cuida quando a necessidade cai; feedback coerente, no ritmo do orcamento."""

    nome = "atencioso"

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        acoes = cuidados_necessarios(visao.estado, self.cfg)
        if visao.atrasado:
            sinal = julgar_acao(visao.estado, self.cfg)
            if sinal != 0:
                acoes.append(_feedback(sinal))
        return acoes

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        sinal = julgar_acao(visao.estado, self.cfg)
        return _feedback(sinal) if sinal != 0 else AcaoUsuario.ACARICIAR


class DonoRelapso(_DonoBase):
    """Cuidado esparso no tempo: poucas visitas por dia, em rajada."""

    nome = "relapso"

    def __init__(self, cfg: ConfigDonos | None = None) -> None:
        super().__init__(cfg)
        self._visitas: set[int] = set()
        self._dia_planejado = -1

    def _planejar_dia(self, visao: Visao, rng: random.Random, passos_por_dia: int) -> None:
        dia = visao.passo // passos_por_dia
        if dia == self._dia_planejado:
            return
        inicio = dia * passos_por_dia
        fim = min(inicio + passos_por_dia, visao.passos_totais)
        self._visitas = set(rng.sample(range(inicio, fim), self.cfg.visitas_por_dia_relapso))
        self._dia_planejado = dia

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        passos_por_dia = TICKS_POR_DIA // self.cfg.passo_ticks
        self._planejar_dia(visao, rng, passos_por_dia)
        if visao.passo not in self._visitas:
            return []
        dias_totais = -(-visao.passos_totais // passos_por_dia)
        dias_futuros = dias_totais - 1 - visao.passo // passos_por_dia
        visitas_restantes = sum(1 for p in self._visitas if p >= visao.passo) + (
            self.cfg.visitas_por_dia_relapso * dias_futuros
        )
        cota = -(-visao.restante // visitas_restantes)  # teto da divisao
        rajada = [AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR]
        sinal = julgar_acao(visao.estado, self.cfg)
        if sinal != 0:
            rajada.append(_feedback(sinal))
        while len(rajada) < cota:
            rajada.append(AcaoUsuario.ACARICIAR)
        return rajada[:cota]

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        return AcaoUsuario.ACARICIAR


class DonoAleatorio(_DonoBase):
    """Controle critico: mesmo numero de interacoes, momentos e acoes sorteados."""

    nome = "aleatorio"

    def __init__(self, cfg: ConfigDonos | None = None) -> None:
        super().__init__(cfg)
        self._plano: list[int] | None = None

    def _planejar(self, visao: Visao, rng: random.Random) -> list[int]:
        contagem = [0] * visao.passos_totais
        colocadas = 0
        while colocadas < visao.orcamento:
            p = rng.randrange(visao.passos_totais)
            if contagem[p] < self.cfg.max_interacoes_por_passo:
                contagem[p] += 1
                colocadas += 1
        return contagem

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        if self._plano is None:
            self._plano = self._planejar(visao, rng)
        acoes = list(ACOES_V1)
        return [rng.choice(acoes) for _ in range(self._plano[visao.passo])]

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        return rng.choice(list(ACOES_V1))


class DonoIncoerente(_DonoBase):
    """Cuida como o atencioso, mas elogia e repreende sem relacao com a acao."""

    nome = "incoerente"

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        acoes = cuidados_necessarios(visao.estado, self.cfg)
        if visao.atrasado:
            acoes.append(self._sorteio(rng))
        return acoes

    def _sorteio(self, rng: random.Random) -> AcaoUsuario:
        return AcaoUsuario.ELOGIAR if rng.random() < self.cfg.prob_elogio_incoerente else AcaoUsuario.REPREENDER

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        return self._sorteio(rng)


FABRICAS_DONO = {
    "atencioso": DonoAtencioso,
    "relapso": DonoRelapso,
    "aleatorio": DonoAleatorio,
    "incoerente": DonoIncoerente,
}


def criar_dono(braco: str) -> Dono:
    if braco not in FABRICAS_DONO:
        raise KeyError(f"braco sem dono: {braco!r}")
    return FABRICAS_DONO[braco]()
