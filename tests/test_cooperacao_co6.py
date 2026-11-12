"""A CO6 da cooperacao (docs/ESPEC_V3_COOPERACAO_CO6.md): a reputacao e o peso dos deveres na percepcao, sem mudar a decisao.

O G2: com a CO6 desligada, as vidas do grupo de hoje (o modular nos dois pets, a cooperacao ligada) saem byte a byte contra o gabarito
gravado antes da mudanca (experiments/exportar_gabarito_co6.py, tests/gabaritos/co6_vidas_de_hoje.json.gz)."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402

GABARITO = json.loads(gzip.decompress(e6.ARQUIVO.read_bytes()).decode())


@pytest.mark.parametrize("i", range(len(e6.VIDAS)))
def test_g2_co6_desligada_vidas_de_hoje(i):
    v = e6.VIDAS[i]
    assert GABARITO["vidas"][i]["semente"] == v[0]
    assert json.loads(json.dumps(e6.vida(v), sort_keys=True)) == GABARITO["vidas"][i]
