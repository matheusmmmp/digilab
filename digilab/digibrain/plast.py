"""M-PLAST, a plasticidade (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.4 e 4.8). Esqueleto da etapa 0: sem equacao.

O P1 (o modelo do desfecho) e o P2 (o habito hebbiano, atras da subchave `ConfigDigibrain.p2`, PE-2); o credito e por opcao (PE-3)."""
from __future__ import annotations

from ._comum import sem_equacao


class Plasticidade:
    def incentivo(self, sens, afeto):
        """o incentivo aprendido de cada unidade, o alivio previsto do corpo naquele estado"""
        raise sem_equacao("M-PLAST", "incentivo")

    def aprender(self, pendencia) -> None:
        """o P1 e o P2 com o r e a elegibilidade do comeco da intencao"""
        raise sem_equacao("M-PLAST", "aprender")

    def estado_interno(self) -> dict:
        raise sem_equacao("M-PLAST", "estado_interno")
