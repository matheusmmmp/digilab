"""Simulador de vida com orcamento imposto.

Tres pecas:

  MotorComFeedback   - subclasse de Motor que avisa a politica quando o dono
                       age. engine.py nao muda: a unica coisa sobrescrita e o
                       gancho interno `_aplicar_acao_usuario`.
  CanalDeInteracao   - conta e IMPOE o orcamento. Mais que o permitido
                       levanta OrcamentoExcedido; fechar a vida sem gastar
                       tudo levanta OrcamentoNaoConsumido.
  simular_vida       - loop dono <-> motor com passo fixo.

`reproduzir_com_feedback` espelha `engine.reproduzir` usando a subclasse,
para que politicas que aprendem com o dono sejam reconstruidas do log. Um
teste garante que, para a PoliticaInstinto, os dois replays coincidem.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Protocol, runtime_checkable

from .config import CONFIG_DONOS, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigDonos
from .donos import Dono, Visao
from .engine import Motor
from .events import AcaoUsuario, LogDeEventos
from .policy import Politica
from .protocol import derivar_semente


class OrcamentoExcedido(RuntimeError):
    pass


class OrcamentoNaoConsumido(RuntimeError):
    pass


@runtime_checkable
class PoliticaTreinavel(Protocol):
    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """Chamado logo depois de cada acao do dono ser aplicada ao estado."""


class MotorComFeedback(Motor):
    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        tick = self._estado.tick
        super()._aplicar_acao_usuario(acao)
        if isinstance(self.politica, PoliticaTreinavel):
            self.politica.receber_acao_dono(acao, tick)


def reproduzir_com_feedback(
    log: LogDeEventos,
    politica_fabrica: Callable[[Config], Politica],
    cfg: Config | None = None,
    semente: int = 42,
    fabrica_motor: Callable | None = None,
) -> MotorComFeedback:
    """Mesmo contrato de engine.reproduzir, com o gancho de feedback ligado.

    `fabrica_motor(politica, cfg, semente)` troca a subclasse do motor (personalidade);
    o padrao e o MotorComFeedback de sempre."""
    cfg = cfg or CONFIG_PADRAO
    fab = fabrica_motor or (lambda politica, cfg, semente: MotorComFeedback(politica=politica, cfg=cfg, semente=semente))
    motor = fab(politica_fabrica(cfg), cfg, semente)
    for evento in log:
        if evento.tipo == "avanco":
            motor._avancar(int(evento.valor))
        elif evento.tipo == "acao_usuario":
            motor._aplicar_acao_usuario(AcaoUsuario(evento.valor))
        else:
            raise ValueError(f"tipo de evento desconhecido no log: {evento.tipo!r}")
    motor._log = LogDeEventos(list(log))
    return motor


class CanalDeInteracao:
    """Unica porta entre dono e motor. Conta tudo."""

    def __init__(self, motor: Motor, orcamento: int, max_por_passo: int) -> None:
        if orcamento <= 0 or max_por_passo <= 0:
            raise ValueError("orcamento e teto por passo precisam ser positivos")
        self.motor = motor
        self.orcamento = orcamento
        self.max_por_passo = max_por_passo
        self.gasto = 0
        self.rejeitados = 0          # toques de treino dentro do intervalo minimo (nao contam)

    def limites(self, passo: int, passos_totais: int) -> tuple[int, int]:
        restante = self.orcamento - self.gasto
        passos_depois = passos_totais - passo - 1
        minimo = max(0, restante - passos_depois * self.max_por_passo)
        maximo = min(restante, self.max_por_passo)
        return minimo, maximo

    def aplicar(self, acoes: list[AcaoUsuario], passo: int, passos_totais: int) -> None:
        minimo, maximo = self.limites(passo, passos_totais)
        if len(acoes) > maximo:
            raise OrcamentoExcedido(
                f"passo {passo}: dono pediu {len(acoes)} interacoes, maximo {maximo} "
                f"(gasto {self.gasto}/{self.orcamento})"
            )
        if len(acoes) < minimo:
            raise OrcamentoNaoConsumido(
                f"passo {passo}: dono fez {len(acoes)} interacoes, minimo {minimo} "
                f"para fechar o orcamento"
            )
        for acao in acoes:
            if not isinstance(acao, AcaoUsuario):
                raise TypeError(f"acao invalida vinda do dono: {acao!r}")
            # TAREFA_TREINO_SOMBRIO: toque de treino dentro do intervalo minimo e rejeitado; nao
            # consome orcamento nem entra no log (so a contagem muda; o limite continua o mesmo)
            aceita = getattr(self.motor, "aceita", None)
            if aceita is not None and not aceita(acao):
                self.rejeitados += 1
                continue
            self.motor.observar(acao)
            self.gasto += 1

    def fechar(self) -> None:
        if self.gasto != self.orcamento:
            raise OrcamentoNaoConsumido(f"vida terminou com {self.gasto}/{self.orcamento} interacoes")


@dataclass
class Vida:
    braco: str
    semente_coorte: int
    motor: MotorComFeedback
    interacoes: int

    @property
    def nome(self) -> str:
        return f"{self.braco}@{self.semente_coorte}"


def simular_vida(
    braco: str,
    dono: Dono,
    politica: Politica,
    semente_coorte: int,
    dias: int,
    orcamento: int,
    cfg: Config | None = None,
    cfg_donos: ConfigDonos | None = None,
    rotulo_dono: str | None = None,
    fabrica_motor: Callable | None = None,
) -> Vida:
    """`rotulo_dono` fixa a rng do dono independente do rotulo do braco.

    Na ablacao, `atencioso-bandit` e `atencioso-instinto` passam
    rotulo_dono="atencioso" e recebem o MESMO dono com a mesma rng; so a
    politica muda. Sem ele, a rng deriva do braco (comportamento da v1).
    """
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cfg_donos.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cfg_donos.passo_ticks

    # mesma semente de ambiente para todos os bracos da coorte; a rng do
    # dono e derivada a parte e nunca toca as rngs do motor
    fab = fabrica_motor or (lambda politica, cfg, semente: MotorComFeedback(politica=politica, cfg=cfg, semente=semente))
    motor = fab(politica, cfg, semente_coorte)
    rng_dono = random.Random(derivar_semente("dono", semente_coorte, rotulo_dono or braco))
    canal = CanalDeInteracao(motor, orcamento, cfg_donos.max_interacoes_por_passo)

    for passo in range(passos):
        motor.avancar(cfg_donos.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(
            estado=motor.estado(),
            passo=passo,
            passos_totais=passos,
            orcamento=orcamento,
            gasto=canal.gasto,
            minimo_obrigatorio=minimo,
            maximo_permitido=maximo,
        )
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)

    canal.fechar()
    return Vida(braco=braco, semente_coorte=semente_coorte, motor=motor, interacoes=canal.gasto)
