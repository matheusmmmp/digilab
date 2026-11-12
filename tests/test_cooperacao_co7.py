"""A CO7 da cooperacao (docs/ESPEC_V3_COOPERACAO_CO7.md): os deveres como escudo, o teste da universalizacao e a culpa e a inveja.

O G2: com a CO7 desligada, as vidas do grupo com a CO6 ligada (o modular nos dois pets) saem byte a byte contra o gabarito gravado antes da
mudanca (experiments/exportar_gabarito_co7.py, tests/gabaritos/co7_vidas_de_hoje.json.gz)."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co7 as e7  # noqa: E402

GABARITO = json.loads(gzip.decompress(e7.ARQUIVO.read_bytes()).decode())


@pytest.mark.parametrize("i", range(len(e7.VIDAS)))
def test_g2_co7_desligada_vidas_com_a_co6(i):
    v = e7.VIDAS[i]
    assert GABARITO["vidas"][i]["semente"] == v[0]
    assert json.loads(json.dumps(e7.vida(v), sort_keys=True)) == GABARITO["vidas"][i]
