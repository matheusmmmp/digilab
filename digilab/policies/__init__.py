"""Politicas alternativas sob o Protocol `Politica`. Trocar de algoritmo e trocar de classe."""

from .bandit import PoliticaBandit
from .lobos import PoliticaLobos

__all__ = ["PoliticaBandit", "PoliticaLobos"]
