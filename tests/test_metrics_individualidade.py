"""As metricas da INDIVIDUALIDADE em digilab/metrics.py (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md, secoes 4.1 a 4.6): os tracos de uma
janela, o ICC(1) com grupos desiguais, o eta2, o Spearman e a reta, cada um contra um caso feito a mao."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab import metrics as M  # noqa: E402


def _j(contagem: dict, latencia=None) -> dict:
    return {"n": sum(contagem.values()), "contagem": contagem, "latencia": latencia}


def _janelas(**troca) -> dict:
    base = {"nula": _j({"chamar_atencao": 2, "explorar": 1, "brincar": 1, "dormir": 4}),
            "comida_nova": _j({"comer": 1, "explorar": 3}, latencia=2),
            "longe": _j({"explorar": 4}),
            "bola": _j({"brincar": 3, "ocioso": 1}),
            "susto": _j({"emburrar": 2, "ocioso": 2})}
    base.update(troca)
    return base


def test_tracos_a_mao():
    t = M.tracos_individualidade(_janelas())
    assert t == {"apego": 0.5, "tedio": 0.25, "neofilia": 1.0, "ousadia": 0.0, "brincar": 0.75 - 0.25, "susto": 0.5 - 0.0}


def test_tracos_janela_que_dormiu_inteira_e_none():
    t = M.tracos_individualidade(_janelas(nula=_j({"dormir": 16}), longe=_j({"dormir": 16})))
    assert t["apego"] is None and t["tedio"] is None and t["brincar"] is None and t["susto"] is None and t["ousadia"] is None
    assert t["neofilia"] == 1.0


def test_tracos_falham_sem_as_cinco_janelas():
    j = _janelas()
    del j["bola"]
    with pytest.raises(ValueError):
        M.tracos_individualidade(j)


def test_icc_igual_ao_icc_um_fator_com_grupos_iguais():
    tabela = [[1.0, 2.0], [3.0, 4.0], [6.0, 8.0]]
    assert M.icc1_grupos(tabela)["r"] == pytest.approx(M.icc_um_fator(tabela))


def test_icc_desigual_a_mao():
    # N 3, k 2, media 3; QM_entre 6, QM_dentro 2; n0 = (3 - 5/3) / 1 = 4/3; s2_entre = (6 - 2) / (4/3) = 3; R = 3 / 5
    r = M.icc1_grupos([[1.0, 3.0], [5.0]])
    assert r["n0"] == pytest.approx(4 / 3) and r["s2_entre"] == pytest.approx(3.0) and r["r"] == pytest.approx(0.6)
    assert not r["truncado"]


def test_icc_trunca_em_zero():
    r = M.icc1_grupos([[1.0, 5.0], [2.0, 4.0]])
    assert r["r"] == 0.0 and r["truncado"]


def test_icc_falha_alto():
    for ruim in ([[1.0, 2.0]], [[1.0], []], [[1.0], [2.0]], [[1.0, 1.0], [1.0, 1.0]]):
        with pytest.raises(ValueError):
            M.icc1_grupos(ruim)


def test_eta2_a_mao():
    assert M.eta2_grupos([[1.0, 1.0], [3.0, 3.0]]) == pytest.approx(1.0)
    assert M.eta2_grupos([[1.0, 3.0], [1.0, 3.0]]) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        M.eta2_grupos([[2.0], [2.0]])


def test_spearman_a_mao():
    assert M.spearman([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)
    assert M.spearman([1, 1, 2], [1, 2, 3]) == pytest.approx(1.5 / math.sqrt(3.0))
    with pytest.raises(ValueError):
        M.spearman([1, 1, 1], [1, 2, 3])


def test_reta_a_mao():
    assert M.reta_mmq([0, 1, 2], [1, 3, 5]) == pytest.approx((1.0, 2.0))
