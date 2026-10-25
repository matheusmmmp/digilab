"""M-ESTADO, o estado dinamico (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.4). Esqueleto da etapa 0: sem equacao.

A persistencia da intencao fica atras da subchave `ConfigDigibrain.persistencia`."""
from __future__ import annotations

from ._comum import sem_equacao


class EstadoDinamico:
    def contexto(self):
        """a persistencia da intencao em curso e a frustracao, como caracteristica de contexto"""
        raise sem_equacao("M-ESTADO", "contexto")

    def escolhida(self, intencao) -> None:
        """a intencao que o M-ARB escolheu"""
        raise sem_equacao("M-ESTADO", "escolhida")

    def consequencia(self, pendencia) -> None:
        """o progresso, o fim da intencao (com a meta ou sem ela) e a frustracao"""
        raise sem_equacao("M-ESTADO", "consequencia")

    def estado_interno(self) -> dict:
        raise sem_equacao("M-ESTADO", "estado_interno")
