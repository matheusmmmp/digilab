"""O dono com os gestos do corpo (V2; docs/TAREFA_V2_CORPO_DRIVES.md, secao 14; docs/PLANO_ANALISE_V2_CORPO_DRIVES.md, os blocos do corpo e
do tapa).

`DonoComGestos` embrulha um dono sintetico: o `elogiar` vira `acariciar` e o `repreender` vira `tapa` (modo "tapa") ou nada (modo
"sem_tapa"). O resto do dono e o orcamento ficam iguais: no modo sem tapa a bronca vira um `SemGesto`, que gasta a interacao do orcamento
sem chegar ao motor nem ao log (como o filtro sem_ensino ao vivo da bancada). E a forma mais direta de comparar "com tapa" e "sem tapa"
sobre o mesmo dono, com a mesma rng.

Os canais que aceitam o `SemGesto`: `CanalComGestos` (o CanalDeInteracao) e `CanalMundoComGestos` (o CanalMundo, com os gestos do mundo
fisico); `simular_vida_gestos` e o treino.simular_vida com o primeiro, e o mundo.simular_vida_mundo aceita o segundo (`canal_classe`). O
tapa e o carinho pelo corpo so existem no MotorCorpo com ConfigCorpo.gestos (digilab/motor_corpo.py); num motor sem a chave, o tapa
falha alto.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from .config import CONFIG_DONOS, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigDonos
from .donos import Visao
from .events import AcaoUsuario
from .mundo import CanalMundo, DeixarBola, DeixarComida
from .protocol import derivar_semente
from .treino import CanalDeInteracao, MotorComFeedback, OrcamentoExcedido, OrcamentoNaoConsumido, Vida

MODOS_GESTOS = ("tapa", "sem_tapa")


@dataclass(frozen=True)
class SemGesto:
    """A bronca do dono no modo sem tapa: gasta a interacao do orcamento e nao chega ao motor nem ao log. `acao` e a que o dono pediu."""

    acao: AcaoUsuario


class DonoComGestos:
    """Embrulha um dono (secao 14): `elogiar` -> `acariciar`; `repreender` -> `tapa` (modo "tapa") ou `SemGesto` (modo "sem_tapa"). O
    resto passa igual, na mesma ordem e com a mesma rng. `trocas` conta o que virou o que."""

    def __init__(self, base, modo: str) -> None:
        if modo not in MODOS_GESTOS:
            raise ValueError(f"modo de gestos desconhecido: {modo!r} (opcoes: {MODOS_GESTOS})")
        self.base = base
        self.modo = modo
        self.nome = getattr(base, "nome", type(base).__name__)
        self.trocas = {"acariciar": 0, "tapa": 0, "sem_gesto": 0}

    def decidir(self, visao: Visao, rng: random.Random) -> list:
        saida = []
        for acao in self.base.decidir(visao, rng):
            if acao is AcaoUsuario.ELOGIAR:
                saida.append(AcaoUsuario.ACARICIAR)
                self.trocas["acariciar"] += 1
            elif acao is AcaoUsuario.REPREENDER and self.modo == "tapa":
                saida.append(AcaoUsuario.TAPA)
                self.trocas["tapa"] += 1
            elif acao is AcaoUsuario.REPREENDER:
                saida.append(SemGesto(acao))
                self.trocas["sem_gesto"] += 1
            else:
                saida.append(acao)
        return saida


def _conferir_limites(canal, acoes: list, passo: int, passos_totais: int) -> None:
    minimo, maximo = canal.limites(passo, passos_totais)
    if len(acoes) > maximo:
        raise OrcamentoExcedido(f"passo {passo}: dono pediu {len(acoes)} interacoes, maximo {maximo} (gasto {canal.gasto}/{canal.orcamento})")
    if len(acoes) < minimo:
        raise OrcamentoNaoConsumido(f"passo {passo}: dono fez {len(acoes)} interacoes, minimo {minimo} para fechar o orcamento")


class CanalComGestos(CanalDeInteracao):
    """O CanalDeInteracao com o `SemGesto`: ele gasta o orcamento (`sem_gesto` conta) e nao chega ao motor."""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.sem_gesto = 0

    def aplicar(self, acoes: list, passo: int, passos_totais: int) -> None:
        _conferir_limites(self, acoes, passo, passos_totais)
        for acao in acoes:
            if isinstance(acao, SemGesto):
                self.sem_gesto += 1
            elif isinstance(acao, AcaoUsuario):
                aceita = getattr(self.motor, "aceita", None)
                if aceita is not None and not aceita(acao):
                    self.rejeitados += 1
                    continue
                self.motor.observar(acao)
            else:
                raise TypeError(f"acao invalida vinda do dono: {acao!r}")
            self.gasto += 1


class CanalMundoComGestos(CanalMundo):
    """O CanalMundo com o `SemGesto` (os gestos do mundo, `deixar_comida` e `deixar_bola`, como no CanalMundo)."""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.sem_gesto = 0

    def aplicar(self, acoes: list, passo: int, passos_totais: int) -> None:
        _conferir_limites(self, acoes, passo, passos_totais)
        for acao in acoes:
            if isinstance(acao, SemGesto):
                self.sem_gesto += 1
            elif isinstance(acao, DeixarComida):
                self.motor.deixar_comida(acao.tipo, acao.x, acao.y)
            elif isinstance(acao, DeixarBola):
                self.motor.deixar_bola(acao.x, acao.y)
            elif isinstance(acao, AcaoUsuario):
                aceita = getattr(self.motor, "aceita", None)
                if aceita is not None and not aceita(acao):
                    self.rejeitados += 1
                    continue
                self.motor.observar(acao)
            else:
                raise TypeError(f"acao invalida vinda do dono: {acao!r}")
            self.gasto += 1


def simular_vida_gestos(braco: str, dono, politica, semente_coorte: int, dias: int, orcamento: int, cfg: Config | None = None,
                        cfg_donos: ConfigDonos | None = None, rotulo_dono: str | None = None,
                        fabrica_motor: Callable | None = None) -> Vida:
    """treino.simular_vida com o CanalComGestos (o dono embrulhado pelo DonoComGestos). A rng do dono e a de sempre (`dono`, semente,
    rotulo): o mesmo dono, com a mesma rng, nos dois modos."""
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cfg_donos.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cfg_donos.passo_ticks
    fab = fabrica_motor or (lambda politica, cfg, semente: MotorComFeedback(politica=politica, cfg=cfg, semente=semente))
    motor = fab(politica, cfg, semente_coorte)
    rng_dono = random.Random(derivar_semente("dono", semente_coorte, rotulo_dono or braco))
    canal = CanalComGestos(motor, orcamento, cfg_donos.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cfg_donos.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
    canal.fechar()
    return Vida(braco=braco, semente_coorte=semente_coorte, motor=motor, interacoes=canal.gasto)
