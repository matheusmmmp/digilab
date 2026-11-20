"""Digilab v0 - motor de pet virtual, sem aprendizado.

v0 e deliberadamente a condicao de controle: estado + politica escrita a
mao + log reproduzivel. Aprendizado entra no v1, como troca de classe.
"""

from .config import CONFIG_PADRAO, TICKS_POR_DIA, Config
from .engine import Motor, reproduzir
from .events import AcaoPet, AcaoUsuario, Evento, LogDeEventos
from .policy import Observacao, Politica, PoliticaInstinto, Transicao
from .state import Estado

__all__ = [
    "CONFIG_PADRAO",
    "TICKS_POR_DIA",
    "Config",
    "Motor",
    "reproduzir",
    "AcaoPet",
    "AcaoUsuario",
    "Evento",
    "LogDeEventos",
    "Observacao",
    "Politica",
    "PoliticaInstinto",
    "Transicao",
    "Estado",
]
__version__ = "0.1.0"
