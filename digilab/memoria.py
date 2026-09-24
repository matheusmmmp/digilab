"""Memoria curta de vida (Parte B): features que mudam o comportamento.

Funcao pura dos eventos que JA chegam a politica, sem tocar engine.py:
  - acoes do dono: receber_acao_dono(acao, tick) (gancho do MotorComFeedback);
  - acoes do proprio pet: observar(transicao).
Nada e salvo fora do log: o replay reconstroi a memoria.

Features (cada uma com o ordinal da acao do dono que a originou, evento_ref;
ordinal k = k-esima acao do dono, convertido em indice do log por
motivo.indices_eventos_dono):
  latencia_fome     latencia do dono no ultimo pedido de comida (alimentar)
  latencia_higiene  latencia do dono no ultimo pedido de limpeza (limpar)
  repreensoes       repreensoes recentes, com decaimento
  elogios           elogios recentes, com decaimento
"Tempo desde a ultima interacao" ja e feature do bandit (tempo_sem_cuidado).

A memoria e ESTILO de vida: nunca entra em CondicaoFisica nem em nada do
combate V2 (um teste por AST garante que combate_v2/ nao importa este modulo).
"""

from __future__ import annotations

import math

from .config import CONFIG_MEMORIA, ConfigMemoria
from .events import AcaoPet, AcaoUsuario
from .policies.bandit import PoliticaBandit
from .policy import Observacao, Transicao

FATORES_MEMORIA = ("latencia_fome", "latencia_higiene", "repreensoes", "elogios")
# acao do dono esperada no evento de origem de cada feature
ORIGEM_ESPERADA = {
    "latencia_fome": AcaoUsuario.ALIMENTAR,
    "latencia_higiene": AcaoUsuario.LIMPAR,
    "repreensoes": AcaoUsuario.REPREENDER,
    "elogios": AcaoUsuario.ELOGIAR,
}
_ATENDE = {AcaoUsuario.ALIMENTAR: "fome", AcaoUsuario.LIMPAR: "higiene"}


class MemoriaCurta:
    def __init__(self, cfg: ConfigMemoria | None = None) -> None:
        self.cfg = cfg or CONFIG_MEMORIA
        self.n_dono = 0                        # ordinal da ultima acao do dono
        self.pendentes: dict[str, list[int]] = {"fome": [], "higiene": []}   # ticks dos pedidos
        self.latencia = {"fome": 0.0, "higiene": 0.0}
        self.ref_latencia: dict[str, int | None] = {"fome": None, "higiene": None}
        self.feedback = {"repreensoes": (0.0, 0), "elogios": (0.0, 0)}         # (valor, tick do valor)
        self.ref_feedback: dict[str, int | None] = {"repreensoes": None, "elogios": None}

    # ------------------------------------------------------------ eventos

    def pedido(self, obs: Observacao, tick: int) -> None:
        fome, higiene = obs.vetor_estado[0], obs.vetor_estado[1]
        necessidade, valor = ("fome", fome) if fome <= higiene else ("higiene", higiene)
        if valor < self.cfg.limiar_necessidade_pedido:
            self.pendentes[necessidade].append(tick)

    def expirar(self, tick: int) -> None:
        for nec, ticks in self.pendentes.items():
            vivos = [t for t in ticks if tick - t <= self.cfg.janela_latencia_ticks]
            if len(vivos) < len(ticks):
                self.latencia[nec] = 1.0          # dono nao veio dentro da janela
                self.ref_latencia[nec] = None     # nao ha acao do dono que origine isso
            self.pendentes[nec] = vivos

    def acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self.n_dono += 1
        self.expirar(tick)
        nec = _ATENDE.get(acao)
        if nec is not None and self.pendentes[nec]:
            lat = tick - self.pendentes[nec][0]
            self.latencia[nec] = min(1.0, lat / self.cfg.janela_latencia_ticks)
            self.ref_latencia[nec] = self.n_dono
            self.pendentes[nec] = []
        chave = {AcaoUsuario.REPREENDER: "repreensoes", AcaoUsuario.ELOGIAR: "elogios"}.get(acao)
        if chave is not None:
            self.feedback[chave] = (self._decaido(chave, tick) + 1.0, tick)
            self.ref_feedback[chave] = self.n_dono

    # ------------------------------------------------------------ leitura (pura)

    def _decaido(self, chave: str, tick: int) -> float:
        v, t0 = self.feedback[chave]
        return v * math.exp(-(tick - t0) / self.cfg.tau_feedback_ticks) if v else 0.0

    def features(self, tick: int) -> list[float]:
        return [
            self.latencia["fome"],
            self.latencia["higiene"],
            min(1.0, self._decaido("repreensoes", tick) / self.cfg.escala_feedback),
            min(1.0, self._decaido("elogios", tick) / self.cfg.escala_feedback),
        ]

    def refs(self) -> dict[str, int | None]:
        """fator -> ordinal da acao do dono que originou o valor atual (ou None)."""
        return {
            "latencia_fome": self.ref_latencia["fome"],
            "latencia_higiene": self.ref_latencia["higiene"],
            "repreensoes": self.ref_feedback["repreensoes"],
            "elogios": self.ref_feedback["elogios"],
        }

    def para_dict(self) -> dict:
        return {
            "n_dono": self.n_dono,
            "pendentes": {k: list(v) for k, v in self.pendentes.items()},
            "latencia": dict(self.latencia),
            "ref_latencia": dict(self.ref_latencia),
            "feedback": {k: list(v) for k, v in self.feedback.items()},
            "ref_feedback": dict(self.ref_feedback),
        }


class PoliticaBanditMemoria(PoliticaBandit):
    """Bandit da v1 com as features de memoria curta acrescentadas ao contexto.

    O prior (instinto) e o aprendizado sao os mesmos; a memoria so entra como
    features, entao o dono passa a poder moldar respostas a propria conduta
    (ex.: pedir de novo quando ele costuma demorar).
    """

    nome = "bandit_thompson_memoria"

    def __init__(self, cfg=None, cfg_bandit=None, cfg_memoria: ConfigMemoria | None = None) -> None:
        self.memoria = MemoriaCurta(cfg_memoria)
        super().__init__(cfg, cfg_bandit)

    def n_features(self) -> int:
        return super().n_features() + len(FATORES_MEMORIA)

    def _tick_de(self, obs: Observacao) -> int:
        return obs.ticks_desde_cuidado + self._tick_ultimo_cuidado

    def _features(self, obs: Observacao) -> list[float]:
        # leitura pura: expirar pedidos so acontece em observar/receber_acao_dono
        return super()._features(obs) + self.memoria.features(self._tick_de(obs))

    def agir(self, obs, rng):
        acao = super().agir(obs, rng)
        self._ultima_decisao["refs_memoria"] = self.memoria.refs()
        return acao

    def observar(self, transicao: Transicao) -> None:
        super().observar(transicao)          # usa as features ANTES de registrar o proprio pedido
        tick = self._tick_ultima_decisao
        self.memoria.expirar(tick)
        if transicao.acao is AcaoPet.CHAMAR_ATENCAO:
            self.memoria.pedido(transicao.observacao, tick)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        super().receber_acao_dono(acao, tick)
        self.memoria.acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        d = super().estado_interno()
        d["memoria"] = self.memoria.para_dict()
        return d
