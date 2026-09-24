"""Camada 3, versao minima: tracos como media movel lenta do comportamento.

So o necessario para a arena derivar stats. Sem evolucao visual, sem
estagios. O vetor de tracos e a EMA da frequencia de cada AcaoPet ao longo
da vida, com alfa pequeno de proposito (anti persona drift).
"""

from __future__ import annotations

from typing import Iterable

from .config import CONFIG_TRACOS, ConfigTracos
from .events import AcaoPet

ORDEM_TRACOS = tuple(AcaoPet)


def tracos_de_acoes(acoes: Iterable[AcaoPet], cfg: ConfigTracos | None = None) -> tuple[float, ...]:
    """EMA sobre one-hot da acao, partindo de uniforme. Deterministica."""
    cfg = cfg or CONFIG_TRACOS
    alfa = cfg.alfa_ema
    if not (0.0 < alfa <= 1.0):
        raise ValueError(f"alfa_ema fora de (0,1]: {alfa}")
    t = [1.0 / len(ORDEM_TRACOS)] * len(ORDEM_TRACOS)
    indice = {a: i for i, a in enumerate(ORDEM_TRACOS)}
    n = 0
    for a in acoes:
        if a not in indice:
            raise ValueError(f"acao desconhecida no historico: {a!r}")
        k = indice[a]
        for i in range(len(t)):
            t[i] = (1.0 - alfa) * t[i] + (alfa if i == k else 0.0)
        n += 1
    if n == 0:
        raise ValueError("historico vazio: pet sem vida nao tem tracos")
    return tuple(t)
