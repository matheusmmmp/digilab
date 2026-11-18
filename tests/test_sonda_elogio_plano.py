"""A sonda do plano do ELOGIO (experiments/sonda_elogio_plano.py): so as sementes dos testes, e o resumo com os campos da secao 2 do plano."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import sonda_elogio_plano as so  # noqa: E402


def test_a_sonda_so_usa_as_sementes_dos_testes():
    for s in (100, 506, 25101):
        with pytest.raises(ValueError):
            so.uma((s, 2))


def test_o_resumo_da_sonda():
    vidas = [so.uma((s, 4)) for s in (101, 102, 103)]
    r = so.resumo(vidas)
    assert r["n"] == 3 and set(r) >= {"E0", "imed", "sort", "imed_menos_sort_x1", "imed_menos_sort_x2", "p1_e0_pref_2a_menos_1a"}
    for v in vidas:
        assert v["E0"]["carinhos"] == 0 and v["imed"]["carinhos"] == v["sort"]["carinhos"]   # o par tem o mesmo numero de carinhos
        assert v["imed"]["x1"][0] <= v["imed"]["x1"][1]
