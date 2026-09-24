"""Motor.

Contrato com a interface, de proposito minusculo:

    motor.observar(acao)   -- o usuario fez algo
    motor.avancar(ticks)   -- passou tempo
    motor.estado()         -- snapshot para desenhar na tela
    motor.acoes_recentes() -- o que o pet fez desde a ultima leitura

A UI e burra. Unity, web ou terminal: nenhum deles sabe o que e uma
politica.

Determinismo e requisito, nao luxo. Mesma semente + mesmo log = mesma
vida, ate o ultimo float. E isso que faz o log de eventos virar dado de
pesquisa em vez de save file.
"""

from __future__ import annotations

import random
from dataclasses import asdict

from .config import CONFIG_PADRAO, Config
from .events import AcaoPet, AcaoUsuario, Evento, LogDeEventos, acao_usuario, avanco
from .policy import Observacao, Politica, PoliticaInstinto, Transicao, efeito_da_acao_do_pet
from .state import Estado, aplicar_acao_usuario, avancar_um_tick


class Motor:
    def __init__(
        self,
        politica: Politica | None = None,
        cfg: Config | None = None,
        semente: int = 42,
        estado_inicial: Estado | None = None,
    ) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.politica = politica or PoliticaInstinto(self.cfg)
        self.semente = semente

        # Duas rng separadas: ambiente e politica nunca disputam a mesma
        # sequencia. Sem isso, trocar de politica mudaria o clima do mundo
        # e a comparacao entre bracos da ablacao ficaria invalida.
        self._rng_ambiente = random.Random(semente)
        self._rng_politica = random.Random(semente + 1_000_003)

        self._estado = estado_inicial or Estado()
        self._log = LogDeEventos()
        self._acoes_pet: list[tuple[int, AcaoPet]] = []
        self._acao_atual: AcaoPet = AcaoPet.OCIOSO
        self._proxima_decisao = 0

    # ------------------------------------------------------------------ API

    def observar(self, acao: AcaoUsuario) -> None:
        self._log.anexar(acao_usuario(self._estado.tick, acao))
        self._aplicar_acao_usuario(acao)

    def avancar(self, ticks: int) -> list[tuple[int, AcaoPet]]:
        self._log.anexar(avanco(self._estado.tick, ticks))
        return self._avancar(ticks)

    def estado(self) -> dict:
        d = asdict(self._estado)
        d["acao_atual"] = self._acao_atual.value
        d["tick_do_dia"] = self._estado.tick_do_dia
        return d

    def acoes_recentes(self, limite: int = 20) -> list[tuple[int, AcaoPet]]:
        return self._acoes_pet[-limite:]

    @property
    def log(self) -> LogDeEventos:
        return self._log

    # -------------------------------------------------------------- interno

    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        self._estado = aplicar_acao_usuario(
            self._estado, acao, self.cfg, self._rng_ambiente
        )

    def _avancar(self, ticks: int) -> list[tuple[int, AcaoPet]]:
        produzidas: list[tuple[int, AcaoPet]] = []

        for _ in range(ticks):
            if self._estado.tick >= self._proxima_decisao:
                obs = Observacao.de_estado(self._estado)
                acao = self.politica.agir(obs, self._rng_politica)
                self._acao_atual = acao
                self._estado = efeito_da_acao_do_pet(
                    self._estado, acao, self.cfg, self.cfg.intervalo_decisao_ticks
                )
                self._acoes_pet.append((self._estado.tick, acao))
                produzidas.append((self._estado.tick, acao))
                self._proxima_decisao = self._estado.tick + self.cfg.intervalo_decisao_ticks

                self.politica.observar(
                    Transicao(
                        observacao=obs,
                        acao=acao,
                        observacao_seguinte=Observacao.de_estado(self._estado),
                        recompensa=None,  # v0 nao tem sinal de recompensa
                    )
                )

            self._estado = avancar_um_tick(self._estado, self.cfg, self._rng_ambiente)

        return produzidas


def reproduzir(
    log: LogDeEventos,
    politica_fabrica=PoliticaInstinto,
    cfg: Config | None = None,
    semente: int = 42,
) -> Motor:
    """Reconstroi um pet inteiro a partir do log.

    Falhar alto e melhor que falhar em silencio: um evento desconhecido
    levanta erro em vez de ser ignorado.
    """
    cfg = cfg or CONFIG_PADRAO
    motor = Motor(politica=politica_fabrica(cfg), cfg=cfg, semente=semente)

    for evento in log:
        if evento.tipo == "avanco":
            motor._avancar(int(evento.valor))
        elif evento.tipo == "acao_usuario":
            motor._aplicar_acao_usuario(AcaoUsuario(evento.valor))
        else:
            raise ValueError(f"tipo de evento desconhecido no log: {evento.tipo!r}")

    motor._log = LogDeEventos(list(log))
    return motor
