"""M-SENS, a codificacao sensorial (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.2). Esqueleto da etapa 0: sem equacao.

Le so a Observacao: o `obs.corpo`, o `obs.mundo` e, do `vetor_estado`, a hora e o dormindo. Nenhum arquivo do pacote importa o
digilab/corpo.py (a G-RECEPTOR)."""
from __future__ import annotations

from ._comum import sem_equacao


class Sens:
    def codificar(self, obs):
        """a interocepcao, o contexto, as linhas de objeto (classe, proximidade, novidade) e as conjuncoes"""
        raise sem_equacao("M-SENS", "codificar")

    def estado_interno(self) -> dict:
        """a habituacao por classe de objeto"""
        raise sem_equacao("M-SENS", "estado_interno")
