"""Vinculo (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md, secao 2.1).

Funcao pura dos eventos da vida, valor em [0, 1], media movel:
    v += alfa * peso * (amostra - v)
Componentes (pesos em ConfigVinculo):
  atendimento  pedido do pet (chamar_atencao com necessidade baixa) atendido por um
               cuidado do dono: amostra 1 - latencia/janela; pedido perdido: 0
  coerencia    feedback do dono sobre a acao atual do pet: fracao dos feedbacks
               anteriores (na janela) sobre a MESMA acao com o mesmo sinal
               (elogiar e repreender o mesmo comportamento derruba)
  desejo       vontade do pet (secao 3) com uma acao do dono que a atende: 1 se o
               dono a atende na janela, 0 se expira
Cada atualizacao registra o indice do evento de log que a moveu (ou None).
Vinculo nunca entra em CondicaoFisica, Estilo nem em combate_v2 (teste por AST).
"""

from __future__ import annotations

from .config import CONFIG_MEMORIA_ESPACOS, CONFIG_VINCULO, ConfigVinculo
from .desejo import Desejo
from .events import AcaoPet, AcaoUsuario
from .policies.bandit import CUIDADOS_QUE_ATENDEM
from .policy import Observacao

# vontade do pet -> acao do dono que a atende (as outras vontades o dono nao tem como atender)
ATENDE_VONTADE = {"comer": AcaoUsuario.ALIMENTAR, "brincar": AcaoUsuario.BRINCAR,
                  "chamar_atencao": AcaoUsuario.ACARICIAR}


class Vinculo:
    def __init__(self, cfg: ConfigVinculo | None = None) -> None:
        self.cfg = cfg or CONFIG_VINCULO
        self.valor = self.cfg.inicial
        self.pedidos: list[int] = []
        self.feedbacks: dict[str, list[tuple[int, int]]] = {}     # acao do pet -> [(tick, sinal)]
        self.vontades: list[tuple[int, AcaoUsuario]] = []          # (tick, acao do dono que atende)
        self.serie: list[tuple[int, float, str, int | None]] = []   # (tick, valor, componente, ref)
        self.ultimo_ref_baixa: int | None = None                   # evento que por ultimo DERRUBOU o vinculo
        self.teto = 1.0                                            # forma sombria: nunca volta a confiar (0,6)

    def _amostra(self, tick: int, componente: str, amostra: float, peso: float, ref: int | None) -> None:
        antes = self.valor
        self.valor = min(self.teto, max(0.0, self.valor + self.cfg.alfa * peso * (amostra - self.valor)))
        if self.valor < antes:
            self.ultimo_ref_baixa = ref
        self.serie.append((tick, self.valor, componente, ref))

    def ajustar(self, tick: int, componente: str, delta: float, ref: int | None) -> None:
        """Variacao direta (treino forcado: -0,05), nao media movel."""
        antes = self.valor
        self.valor = min(self.teto, max(0.0, self.valor + delta))
        if self.valor < antes:
            self.ultimo_ref_baixa = ref
        self.serie.append((tick, self.valor, componente, ref))

    def limitar(self, tick: int, teto: float, componente: str) -> None:
        self.teto = teto
        if self.valor > teto:
            self.valor = teto
            self.serie.append((tick, self.valor, componente, None))

    # ------------------------------------------------------------ eventos
    def expirar(self, tick: int) -> None:
        c = self.cfg
        vivos = []
        for t in self.pedidos:
            if tick - t > c.janela_latencia_ticks:
                self._amostra(tick, "atendimento", 0.0, c.peso_atendimento, None)
            else:
                vivos.append(t)
        self.pedidos = vivos
        vivas = []
        for t, acao in self.vontades:
            if tick - t > c.janela_desejo_ticks:
                self._amostra(tick, "desejo", 0.0, c.peso_desejo, None)
            else:
                vivas.append((t, acao))
        self.vontades = vivas

    def decisao(self, obs: Observacao, acao: AcaoPet, tick: int, desejo: Desejo | None) -> None:
        self.expirar(tick)
        if acao is AcaoPet.CHAMAR_ATENCAO:
            fome, higiene = obs.vetor_estado[0], obs.vetor_estado[1]
            if min(fome, higiene) < CONFIG_MEMORIA_ESPACOS.limiar_necessidade_pedido:
                self.pedidos.append(tick)
        if desejo is not None and desejo.tipo == "vontade" and desejo.alvo in ATENDE_VONTADE:
            self.vontades.append((tick, ATENDE_VONTADE[desejo.alvo]))

    def acao_dono(self, acao: AcaoUsuario, tick: int, acao_pet: AcaoPet | None, ref: int) -> None:
        c = self.cfg
        self.expirar(tick)
        if acao in CUIDADOS_QUE_ATENDEM and self.pedidos:
            for t in self.pedidos:
                self._amostra(tick, "atendimento", 1.0 - (tick - t) / c.janela_latencia_ticks, c.peso_atendimento, ref)
            self.pedidos = []
        if acao in (AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER) and acao_pet is not None:
            sinal = 1 if acao is AcaoUsuario.ELOGIAR else -1
            hist = [(t, s) for t, s in self.feedbacks.get(acao_pet.value, []) if tick - t <= c.janela_coerencia_ticks]
            if hist:
                self._amostra(tick, "coerencia", sum(s == sinal for _, s in hist) / len(hist), c.peso_coerencia, ref)
            self.feedbacks[acao_pet.value] = hist + [(tick, sinal)]
        atendidas = [v for v in self.vontades if v[1] is acao]
        if atendidas:
            self.vontades = [v for v in self.vontades if v[1] is not acao]
            for _ in atendidas:
                self._amostra(tick, "desejo", 1.0, c.peso_desejo, ref)

    def para_dict(self) -> dict:
        return {"valor": self.valor, "atualizacoes": len(self.serie), "pedidos_pendentes": list(self.pedidos),
                "vontades_pendentes": [[t, a.value] for t, a in self.vontades]}
