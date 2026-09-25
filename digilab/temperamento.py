"""Temperamento inato (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md, secao 1).

Quatro eixos em [-1, 1]; 0 e neutro e reproduz o comportamento atual exatamente
(todo fator vale 1.0 com o eixo em 0). Muda COMO o pet aprende, nunca O QUE:
  curiosidade   escala a variancia da amostra de Thompson (exploracao)
  teimosia      reduz o peso das repreensoes no aprendizado; reduz obediencia
  sensibilidade > 0 responde mais a elogio, < 0 mais a repreensao
  rancor        escala o decaimento das memorias de demora e bronca (espacos)
Nenhum eixo altera o prior do instinto, o espaco de acoes ou a recompensa em si:
so a escala com que ela e usada.

Sorteio: stream propria `rng_ovo`, derivada da semente do ovo (a semente da
coorte). O mesmo ovo da o mesmo temperamento em todos os bracos (ovos pareados)
e a rng_ovo nao compartilha estado com ambiente, politica ou combate.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .config import CONFIG_TEMPERAMENTO, ConfigTemperamento
from .protocol import derivar_semente

EIXOS = ("curiosidade", "teimosia", "sensibilidade", "rancor")


@dataclass(frozen=True)
class Temperamento:
    curiosidade: float = 0.0
    teimosia: float = 0.0
    sensibilidade: float = 0.0
    rancor: float = 0.0

    def __post_init__(self) -> None:
        for e in EIXOS:
            v = getattr(self, e)
            if not -1.0 <= v <= 1.0:
                raise ValueError(f"temperamento.{e} fora de [-1, 1]: {v}")

    def para_dict(self) -> dict:
        return {e: getattr(self, e) for e in EIXOS}

    @property
    def neutro(self) -> bool:
        return all(getattr(self, e) == 0.0 for e in EIXOS)

    # ------------------------------------------------------------ efeitos (1.0 no neutro)
    def fator_variancia(self, cfg: ConfigTemperamento = CONFIG_TEMPERAMENTO) -> float:
        return math.exp(cfg.k_curiosidade * self.curiosidade)

    def peso_elogio(self, cfg: ConfigTemperamento = CONFIG_TEMPERAMENTO) -> float:
        return 1.0 + cfg.k_sensibilidade * self.sensibilidade

    def peso_repreensao(self, cfg: ConfigTemperamento = CONFIG_TEMPERAMENTO) -> float:
        return (1.0 - cfg.k_teimosia * self.teimosia) * (1.0 - cfg.k_sensibilidade * self.sensibilidade)

    def fator_tau_rancor(self, cfg: ConfigTemperamento = CONFIG_TEMPERAMENTO) -> float:
        return math.exp(cfg.k_rancor * self.rancor)


NEUTRO = Temperamento()


def rng_ovo(semente_ovo: int) -> random.Random:
    return random.Random(derivar_semente("ovo", semente_ovo))


def sortear(semente_ovo: int, cfg: ConfigTemperamento | None = None) -> Temperamento:
    """Uniforme em [-amplitude, amplitude] por eixo, independente (PROPOSTO)."""
    cfg = cfg or CONFIG_TEMPERAMENTO
    rng = rng_ovo(semente_ovo)
    a = cfg.amplitude
    return Temperamento(**{e: rng.uniform(-a, a) for e in EIXOS})
