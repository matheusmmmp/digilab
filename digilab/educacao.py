"""Educacao, lesoes e heranca no motor (educacao-v1).

docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, aprovado em 2026-09-28. Nada aqui altera engine.py nem o Estado v0:
  - MotorEducacao: subclasse do MotorTreino. Guarda a disciplina, a janela de travessura aberta e (depois)
    as lesoes. Sem nenhuma acao nova no log, rejoga igual ao MotorTreino, bit a bit (teste).
  - Acoes novas do dono (events.ACOES_EDUCACAO): so este motor aceita. Nos motores anteriores levantam erro.

Parte 1 da Fase 2: so a casca. As acoes novas levantam erro ate a parte que as implementa: falhar alto
e melhor do que uma acao sem efeito que parece funcionar.
"""

from __future__ import annotations

from .config import CONFIG_EDUCACAO, CONFIG_LESOES, ConfigEducacao, ConfigLesoes
from .events import ACOES_EDUCACAO, AcaoUsuario
from .obediencia import PoliticaBanditPersonalidade
from .temperamento import NEUTRO, Temperamento
from .treino_vida import MotorTreino


class AcaoAindaSemEfeito(NotImplementedError):
    """Acao de educacao que existe no enum, mas cuja regra ainda nao foi implementada."""


class MotorEducacao(MotorTreino):
    def __init__(self, politica=None, cfg=None, semente: int = 42, temperamento: Temperamento = NEUTRO,
                 especie: str = "brasa", obediencia_desligada: bool = False, cfg_treino=None, cfg_sombrio=None,
                 cfg_educacao: ConfigEducacao | None = None, cfg_lesoes: ConfigLesoes | None = None, **kw) -> None:
        super().__init__(politica, cfg, semente, temperamento, especie, obediencia_desligada, cfg_treino,
                         cfg_sombrio, **kw)
        self.ce = cfg_educacao or CONFIG_EDUCACAO
        self.cl = cfg_lesoes or CONFIG_LESOES
        self.disciplina = 0
        self.janela: dict | None = None          # travessura aberta: tipo, inicio, prazo

    def estado(self) -> dict:
        d = super().estado()
        d["educacao"] = {"disciplina": self.disciplina,
                         "janela": None if self.janela is None else dict(self.janela)}
        return d

    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if acao in ACOES_EDUCACAO:
            raise AcaoAindaSemEfeito(f"{acao.value}: regra ainda nao implementada (Fase 2, parte seguinte)")
        super()._aplicar_acao_usuario(acao)


def fabricas_educacao(semente: int, especie: str, temperamento: Temperamento, obediencia_desligada: bool = False,
                      ct=None, ce: ConfigEducacao | None = None, cl: ConfigLesoes | None = None):
    """(fabrica da politica, fabrica do motor) de uma vida com educacao; reusadas no replay."""
    fp = lambda cfg=None: PoliticaBanditPersonalidade(cfg, temperamento)  # noqa: E731
    fm = (lambda politica, cfg, s: MotorEducacao(politica, cfg, s, temperamento, especie,  # noqa: E731
                                                 obediencia_desligada=obediencia_desligada, cfg_treino=ct,
                                                 cfg_educacao=ce, cfg_lesoes=cl))
    return fp, fm
