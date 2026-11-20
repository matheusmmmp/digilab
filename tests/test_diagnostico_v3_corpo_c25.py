"""O diagnostico da C2.5 (experiments/diagnostico_v3_corpo_c25.py): a decomposicao da privacao numa serie sintetica. O replay das vidas
reais e conferido pelo proprio script (o log refeito e a privacao igual a do medidas.json, falha alta)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import diagnostico_v3_corpo_c25 as dg  # noqa: E402
from digilab.metrics import JANELA_8_14  # noqa: E402

C = 1000


def _linha(t, fome=0.5, energia=0.5, higiene=0.5, dormindo=False, comb=500, saude=1.0):
    return {"t": t, "fome": fome, "higiene": higiene, "energia": energia, "saude": saude, "dormindo": dormindo, "noite": False,
            "combustivel": comb, "q_fome": 0, "alimento": 0, "q_dano": 0}


def test_a_decomposicao():
    ini = JANELA_8_14[0]
    ls = [_linha(ini - 15, fome=0.0)]                                   # fora da janela: nao conta
    ls += [_linha(ini, fome=0.1, comb=100), _linha(ini + 15, energia=0.1), _linha(ini + 30, fome=0.1, energia=0.1, dormindo=True),
           _linha(ini + 45)]
    r = dg.resumir(ls, C)
    assert r["n"] == 4 and r["privacao"] == 0.75
    assert r["so_fome"] == 0.25 and r["so_energia"] == 0.25 and r["fome_e_energia"] == 0.25
    assert r["fome_baixa_acordado"] == 0.25 and r["fome_baixa_dormindo"] == 0.25
    assert r["fome_baixa_comb_abaixo"] == 0.25 and r["fome_baixa_comb_acima"] == 0.25
    assert r["acordou"] == 1


def test_sem_janela_falha_alto():
    with pytest.raises(ValueError):
        dg.resumir([_linha(0)], C)
