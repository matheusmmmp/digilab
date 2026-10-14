"""A bancada da V2, módulo `vida`.

A especificação e o resultado de uma vida, o filtro do log, as contagens e o resumo do motor.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace

from digilab.ambiente import MotorAmbiente
from digilab.events import LogDeEventos
from digilab.frutas import MotorFrutas
from digilab.mundo import MotorMundo
from digilab.obediencia import MotorPersonalidade
from digilab.treino import MotorComFeedback


class ReplayDivergiu(RuntimeError):
    pass


# ------------------------------------------------------------------ a vida


@dataclass(frozen=True)
class EspecVida:
    dono: str
    braco: str
    semente: int
    genoma: int | None = None
    mundo: str = "padrao"
    cerebro: str = "lobos"
    lugar: str | None = None         # mundo fisico: onde o dono solta a racao (DonoComLugar; PMF-4); so nele, e obrigatorio nele

    @property
    def nome(self) -> str:
        m = "" if self.mundo == "padrao" else f"~{self.mundo}"
        g = "" if self.genoma is None else f"~g{self.genoma}"
        c = "" if self.cerebro == "lobos" else f"~{self.cerebro}"
        lg = "" if self.lugar is None else f"~{self.lugar}"
        return f"{self.dono}-{self.braco}{c}{m}{lg}{g}@{self.semente}"

    @property
    def celula(self) -> tuple:
        """O que define o par de vidas que se comparam entre bracos: tudo menos o braco (no mundo fisico, o lugar tambem)."""
        base = (self.dono, self.semente, self.genoma, self.mundo, self.cerebro)
        return base if self.lugar is None else base + (self.lugar,)

    @property
    def condicao(self) -> str:
        return mundo_de(self.mundo).condicao


@dataclass
class VidaBancada:
    espec: EspecVida
    motor: MotorComFeedback
    interacoes: int                  # acoes do dono no log, fora os eventos do mundo
    origem: str | None = None        # so no modo acoplado: o nome da vida de origem, o braco dela e o filtro
    origem_braco: str | None = None
    filtro: str | None = None
    broncas: int = 0                 # N7: as broncas do pedido no registro (repreender pelo canal do mundo, fora do orcamento)
    julgamentos: int = 0             # K4: os julgamentos da fruta no registro (elogiar/repreender pelo canal do mundo)
    retirados: int = 0               # mundo fisico: os sinais do dono que o filtro sem_ensino ao vivo nao deixou chegar (PMF-3); com os
    #                                  gestos: as broncas do modo sem tapa (SemGesto), que gastam o orcamento e nao chegam ao log
    carinhos: int = 0                # banheiro: os carinhos do DonoCarinhoBanheiro (acariciar pelo canal do mundo, fora do orcamento)
    gestos: dict | None = None       # corpo: o que o DonoComGestos trocou (acariciar, tapa, sem_gesto) e, no P1-c-tapaX, os tapas na fruta X

    @property
    def rotulo_braco(self) -> str:
        """O braco na tabela: "P3", ou "P0<P3:sem_sinais" para o P0 acoplado ao registro do P3 sem os sinais."""
        b = self.espec.braco if self.espec.cerebro == "lobos" else f"{self.espec.braco}~{self.espec.cerebro}"
        if self.origem is None:
            return b
        return f"{b}<{self.origem_braco}:{self.filtro}"

    @property
    def eventos_mundo(self) -> int:
        return contar_acoes(self.motor.log)[1]

    @property
    def informacoes(self) -> int:
        return contar_informacoes(self.motor.log)

    @property
    def pedidos(self) -> int:
        return contar_pedidos(self.motor.log)

    @property
    def nome(self) -> str:
        if self.origem is None:
            return self.espec.nome
        e = self.espec
        return replace(e, braco=f"{e.braco}~de-{self.origem_braco}-{self.filtro}").nome


def filtrar_log(log: LogDeEventos, retirar: frozenset) -> LogDeEventos:
    """O mesmo log sem as acoes do dono em `retirar` (valores de AcaoUsuario); avancos, eventos do mundo e as outras acoes nos
    mesmos ticks. Tirar um evento do mundo falha alto: o acoplado reproduz o mundo da origem."""
    if retirar & EVENTOS_DO_MUNDO:
        raise ValueError(f"o filtro tiraria eventos do mundo: {sorted(retirar & EVENTOS_DO_MUNDO)}")
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in retirar)])


def contar_acoes(log: LogDeEventos) -> tuple[int, int]:
    """(acoes do dono no orcamento, eventos do mundo). As informacoes (fora do orcamento, sem ser mundo) nao entram em nenhuma das
    duas: contar_informacoes."""
    dono = mundo = 0
    for e in log:
        if e.tipo == "acao_usuario":
            if str(e.valor) in EVENTOS_DO_MUNDO:
                mundo += 1
            elif str(e.valor) not in INFORMACOES and str(e.valor) not in PEDIDOS:
                dono += 1
    return dono, mundo


def contar_gestos_mundo(log: LogDeEventos) -> int:
    """Os gestos do dono no mundo fisico (deixar_comida, deixar_bola): eventos proprios do log, no orcamento do dono (CanalMundo)."""
    return sum(1 for e in log if e.tipo in ("deixar_comida", "deixar_bola"))


def contar_pedidos(log: LogDeEventos) -> int:
    return sum(1 for e in log if e.tipo == "acao_usuario" and str(e.valor) in PEDIDOS)


def contar_informacoes(log: LogDeEventos) -> int:
    return sum(1 for e in log if e.tipo == "acao_usuario" and str(e.valor) in INFORMACOES)


def resumo_motor(motor) -> tuple:
    """Tudo que uma vida produz: log, estado final, acoes do pet, as rngs e, no motor de personalidade, obediencia, recusas,
    desejos e vinculo."""
    extra = ()
    if isinstance(motor, MotorPersonalidade):
        extra = (motor._rng_obediencia.getstate(), [r.para_dict() for r in motor.recusas],
                 [d.para_dict() for d in motor.desejos], motor.vinculo.para_dict())
    if isinstance(motor, MotorAmbiente):
        bola = motor.resumo_bola() if motor.cb.ligada else {"ligada": False, "contagem": dict(motor.contagem_bola)}
        extra = extra + (bola, dict(motor.contagem), motor.morte)
    if isinstance(motor, MotorFrutas):
        extra = extra + (motor.resumo_frutas(),)
    if isinstance(motor, MotorFrutasMundo):
        extra = extra + (motor.resumo_mundo(),)
    if isinstance(motor, MotorMundo) and motor.cmf.ligada:
        extra = extra + (motor.resumo_mundo_fisico(),)
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9), motor._rng_politica.getstate(),
            motor._rng_ambiente.getstate(), *extra)


def _interno(motor) -> str:
    return json.dumps(motor.politica.estado_interno(), sort_keys=True)


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .mundos import EVENTOS_DO_MUNDO, MotorFrutasMundo, mundo_de  # noqa: E402
from .bracos import INFORMACOES, PEDIDOS  # noqa: E402
