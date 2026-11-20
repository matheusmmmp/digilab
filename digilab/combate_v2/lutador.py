"""Lutador = (CondicaoFisica, Estilo), duas entradas independentes.

- CondicaoFisica: hp_max, guts_inicial, regen_guts. No futuro vem do CUIDADO
  (estado de vida).
- Estilo: ListaGambits + epsilon. No futuro vem do COMPORTAMENTO APRENDIDO.

Nenhum campo de um depende do outro: e o que permite medir, na arena V2,
quanto do resultado vem de cada fonte (o confundidor da v1).
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..config import CONFIG_COMBATE_V2, ConfigCombateV2
from .gambits import ListaGambits, Motivo, decidir_gambits
from .regras import Acao, EstadoCombate


@dataclass(frozen=True)
class CondicaoFisica:
    hp_max: float
    guts_inicial: int
    regen_guts: int

    def __post_init__(self) -> None:
        if not self.hp_max > 0:
            raise ValueError(f"hp_max precisa ser positivo: {self.hp_max}")
        if not 0 <= self.guts_inicial <= CONFIG_COMBATE_V2.guts_max:
            raise ValueError(f"guts_inicial fora de 0..{CONFIG_COMBATE_V2.guts_max}: {self.guts_inicial}")
        if self.regen_guts < 0:
            raise ValueError(f"regen_guts negativo: {self.regen_guts}")

    @staticmethod
    def neutra(cfg: ConfigCombateV2 | None = None) -> "CondicaoFisica":
        cfg = cfg or CONFIG_COMBATE_V2
        return CondicaoFisica(cfg.hp_neutro, cfg.guts_inicial_neutro, cfg.regen_guts_neutro)

    def para_dict(self) -> dict:
        return {"hp_max": self.hp_max, "guts_inicial": self.guts_inicial, "regen_guts": self.regen_guts}


@runtime_checkable
class Decisor(Protocol):
    """Qualquer estilo: gambits (dentro da linguagem) ou referencia (fora)."""

    fora_da_linguagem: bool

    def decidir(self, estado: EstadoCombate, lado: int, rng: random.Random, cfg: ConfigCombateV2) -> tuple[Acao, Motivo]:
        ...

    def para_dict(self) -> dict:
        ...


@dataclass(frozen=True)
class Estilo:
    gambits: ListaGambits
    epsilon: float
    fora_da_linguagem: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.epsilon <= 1.0:
            raise ValueError(f"epsilon fora de [0, 1]: {self.epsilon}")

    def decidir(self, estado: EstadoCombate, lado: int, rng: random.Random, cfg: ConfigCombateV2) -> tuple[Acao, Motivo]:
        return decidir_gambits(self.gambits, self.epsilon, estado, lado, rng, cfg)

    def para_dict(self) -> dict:
        return {"tipo": "gambits", "epsilon": self.epsilon, "gambits": self.gambits.para_dict()}


@dataclass(frozen=True)
class Lutador:
    nome: str
    condicao: CondicaoFisica
    estilo: Decisor

    def hash(self) -> str:
        carga = {"nome": self.nome, "condicao": self.condicao.para_dict(), "estilo": self.estilo.para_dict()}
        return hashlib.sha256(json.dumps(carga, sort_keys=True).encode("utf-8")).hexdigest()
