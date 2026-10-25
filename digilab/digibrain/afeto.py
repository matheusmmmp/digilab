"""M-AFETO, os afetos e os moduladores (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.3). Esqueleto da etapa 0: sem equacao.

A modulacao do `g_apr` pela excitacao fica atras da subchave `ConfigDigibrain.modula_g_apr` (PE-4)."""
from __future__ import annotations

from ._comum import sem_equacao


class Afeto:
    def ler(self, sens):
        """as urgencias por receptor e os ganhos da aprendizagem e da exploracao"""
        raise sem_equacao("M-AFETO", "ler")

    def consequencia(self, pendencia):
        """o sinal homeostatico r da consequencia, a valencia e a excitacao"""
        raise sem_equacao("M-AFETO", "consequencia")

    def estado_interno(self) -> dict:
        raise sem_equacao("M-AFETO", "estado_interno")
