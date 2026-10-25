"""M-IMPULSO, os impulsos e os circuitos de comportamento (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.5). Esqueleto da etapa 0: sem
equacao. Sem estado: os pesos ficam no M-PLAST e no inato."""
from __future__ import annotations

from ._comum import sem_equacao


class Impulso:
    def unidades(self, sens, afeto, contexto, incentivo, memoria):
        """as unidades (comportamento, objeto) com a ativacao e os termos da soma"""
        raise sem_equacao("M-IMPULSO", "unidades")

    def estado_interno(self) -> dict:
        raise sem_equacao("M-IMPULSO", "estado_interno")
