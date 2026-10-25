"""M-ARB, a arbitragem (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.7). Esqueleto da etapa 0: sem equacao.

O unico modulo que consome a rng de politica: uma chamada `rng.random()` por decisao com dois candidatos ou mais (a secao 1)."""
from __future__ import annotations

from ._comum import sem_equacao


class Arbitragem:
    def escolher(self, unidades, afeto, sens, rng):
        """a intencao escolhida (o comportamento e o objeto): o reflexo de seguranca ou o sorteio proporcional"""
        raise sem_equacao("M-ARB", "escolher")

    def estado_interno(self) -> dict:
        raise sem_equacao("M-ARB", "estado_interno")
