"""Politicas alternativas sob o Protocol `Politica`. Trocar de algoritmo e trocar de classe."""

from .bandit import PoliticaBandit
from .camada_unica import PoliticaCamadaUnica
from .lobos import PoliticaLobos

__all__ = ["PoliticaBandit", "PoliticaCamadaUnica", "PoliticaLobos"]
