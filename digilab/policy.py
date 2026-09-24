"""Camada 2: politica de comportamento.

O contrato `Politica` e o ponto onde bandit, Q tabular e planejador vao
entrar como IMPLEMENTACOES ALTERNATIVAS, nao como reescrita. Trocar de
algoritmo tem que ser trocar de classe. Enquanto o protocolo nao estiver
congelado, nenhum deles e a escolha oficial.

O v0 traz so `PoliticaInstinto`: regras escritas a mao, zero aprendizado.
Ela nao e um rascunho do modelo aprendido -- ela e o BRACO DE CONTROLE do
experimento. Se um pet treinado por gente nao vencer este aqui, a
hipotese morre.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .config import Config
from .events import AcaoPet
from .state import Estado


@dataclass(frozen=True)
class Observacao:
    """O que a politica enxerga. Congelado: virou entrada de modelo."""

    vetor_estado: tuple[float, ...]
    ticks_desde_cuidado: int
    total_cuidados: int

    @staticmethod
    def de_estado(estado: Estado) -> "Observacao":
        return Observacao(
            vetor_estado=estado.vetor(),
            ticks_desde_cuidado=estado.tick - estado.tick_ultimo_cuidado,
            total_cuidados=estado.total_cuidados,
        )


@dataclass(frozen=True)
class Transicao:
    """Entregue a politica depois de cada acao. No v0 ninguem usa."""

    observacao: Observacao
    acao: AcaoPet
    observacao_seguinte: Observacao
    recompensa: float | None = None


@runtime_checkable
class Politica(Protocol):
    nome: str

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        """Escolhe a proxima acao do pet."""

    def observar(self, transicao: Transicao) -> None:
        """Recebe o resultado. Politicas sem aprendizado ignoram."""

    def estado_interno(self) -> dict:
        """Parametros aprendidos, para inspecao e serializacao."""


class PoliticaInstinto:
    """Regras de prioridade escritas a mao. Determinista dada a rng.

    Nao aprende nada. Serve para tres coisas:
      1. o pet recem-nascido nao se comportar de forma aleatoria (cold start);
      2. ser a condicao de controle "sem aprendizado" da ablacao;
      3. ser o prior de onde as politicas aprendizes partem.
    """

    nome = "instinto"

    def __init__(self, cfg: Config | None = None) -> None:
        from .config import CONFIG_PADRAO

        self.cfg = cfg or CONFIG_PADRAO

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        fome, higiene, energia, humor, saude, sujeira, dormindo, hora = obs.vetor_estado

        # Sono tem precedencia: exaustao ou madrugada.
        if energia < 0.25:
            return AcaoPet.DORMIR
        if dormindo > 0.5 and energia < 0.85:
            return AcaoPet.DORMIR
        if self.cfg.e_noite(int(hora * 1440)) and energia < 0.55:
            return AcaoPet.DORMIR

        # Necessidades que o pet nao resolve sozinho: pede ajuda.
        if fome < 0.25 or higiene < 0.25:
            return AcaoPet.CHAMAR_ATENCAO

        # Abandono recente pesa no humor.
        if obs.ticks_desde_cuidado > self.cfg.janela_atencao_ticks:
            return AcaoPet.EMBURRAR if humor < 0.35 else AcaoPet.CHAMAR_ATENCAO

        if fome < 0.45:
            return AcaoPet.COMER if rng.random() < 0.5 else AcaoPet.CHAMAR_ATENCAO

        # Tempo livre: mistura ponderada, nunca uniforme.
        pesos = {
            AcaoPet.OCIOSO: 3.0,
            AcaoPet.EXPLORAR: 2.0 + 2.0 * energia,
            AcaoPet.BRINCAR: 1.0 + 3.0 * humor,
            AcaoPet.CHAMAR_ATENCAO: 1.0,
        }
        acoes = list(pesos)
        return rng.choices(acoes, weights=[pesos[a] for a in acoes], k=1)[0]

    def observar(self, transicao: Transicao) -> None:
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome, "parametros_aprendidos": 0}


def efeito_da_acao_do_pet(
    estado: Estado, acao: AcaoPet, cfg: Config, intervalo: int
) -> Estado:
    """Como a acao escolhida realimenta o estado no intervalo seguinte."""
    from dataclasses import replace

    from .state import _limitar

    if acao is AcaoPet.DORMIR:
        return replace(estado, dormindo=True)

    novo = replace(estado, dormindo=False)

    if acao is AcaoPet.BRINCAR:
        return replace(
            novo,
            humor=_limitar(novo.humor + cfg.humor_por_tick_brincando * intervalo),
            energia=_limitar(novo.energia - 0.02),
        )
    if acao is AcaoPet.EXPLORAR:
        return replace(
            novo,
            energia=_limitar(novo.energia - 0.015),
            humor=_limitar(novo.humor + 0.01),
        )
    if acao is AcaoPet.COMER:
        return replace(novo, fome=_limitar(novo.fome + 0.05))
    if acao is AcaoPet.EMBURRAR:
        return replace(novo, humor=_limitar(novo.humor - 0.01))

    return novo
