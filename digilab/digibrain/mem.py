"""M-MEM, a memoria minima: os episodios de alimentacao (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.6 e 9). Esqueleto da etapa 0: sem
equacao. Fica atras da subchave `ConfigDigibrain.m_mem`; o lugar lembrado chega ao motor pelo candidato `lembranca` do explorar (PE-14),
que nao entra nesta etapa."""
from __future__ import annotations

from ._comum import sem_equacao


class Memoria:
    def recuperar(self, sens, afeto):
        """no maximo um episodio recuperado, com o termo do lugar dele no explorar"""
        raise sem_equacao("M-MEM", "recuperar")

    def codificar(self, pendencia) -> None:
        """o consumo ou a visita a um lugar lembrado vira episodio"""
        raise sem_equacao("M-MEM", "codificar")

    def estado_interno(self) -> dict:
        raise sem_equacao("M-MEM", "estado_interno")
