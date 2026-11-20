"""Grava o gabarito das vidas do J5 com o adendo 7 (a fruta ao lado, a parada no T2, a oportunidade nova do T1), ANTES do adendo 8 mexer
na bancada e no mundo.

Para cada vida (braco, protocolo, semente) da fumaca da bancada do J5 com o adendo 7: o sha256 do log e o das medidas sem o custo. O
teste (tests/test_bancada_pqp_adendo8.py) confere que, sem a chave `adendo_8`, as vidas e as medidas saem iguais byte a byte.

    python tests/gabarito_pqp_adendo7.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_pqp_ao_lado as base  # noqa: E402

DESTINO = RAIZ / "tests" / "gabaritos" / "pqp_adendo7_vidas.json"


def config() -> dict:
    return {**base.config(), "adendo_7": True, "janela": 3}


def vidas(cfg: dict | None = None) -> dict:
    return base.vidas(cfg or config())


if __name__ == "__main__":
    DESTINO.write_text(json.dumps(vidas(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"gravado {DESTINO}")
