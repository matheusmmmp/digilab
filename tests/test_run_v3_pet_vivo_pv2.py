"""As conferencias do orquestrador da run do PV-2 (experiments/run_v3_pet_vivo_pv2.py; o adendo 2 do plano): a trava, as contas da
leitura e uma vida com o contrafactual da SE-C nas sementes dos testes. Nenhuma vida da faixa."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_pet_vivo_pv2 as R  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402

CFG = json.loads((RAIZ / "experiments/configs/v3_pet_vivo/pv2.json").read_text(encoding="utf-8"))
FUMACA = json.loads((RAIZ / "experiments/configs/v3_pet_vivo/pv2_fumaca.json").read_text(encoding="utf-8"))


def test_a_config_e_a_do_plano():
    assert tuple(CFG["unidades"]["bases"]) == R.BASES and CFG["unidades"]["k"] == R.K_POR_BASE == 40
    assert CFG["dias"] == R.DIAS == 14 and CFG["plano"] == R.PLANO
    assert any((lo, hi) == R.FAIXA for lo, hi, _ in FAIXAS_RESERVADAS)
    assert R.modo_da_config(FUMACA) == "fumaca"


def test_a_trava_recusa_sem_o_aprovado_do_adendo_2():
    plano = (RAIZ / R.PLANO).read_text(encoding="utf-8")
    if R.STATUS_ADENDO_2 in plano:
        pytest.skip("o adendo 2 ja esta APROVADO")
    with pytest.raises(RuntimeError, match="adendo 2"):
        R.modo_da_config(CFG)
    R.exigir_aprovado(plano.replace("**Status do adendo 2: PROPOSTO.**", R.STATUS_ADENDO_2 + " em 2026-11-17.**"))


def test_a_trava_recusa_fora_do_plano(tmp_path):
    for mudar in ({"dias": 13}, {"fase": "outra"}, {"orcamento_por_dia": 8}):
        with pytest.raises((ValueError, RuntimeError)):
            R.modo_da_config({**CFG, **mudar})
    with pytest.raises(bv.SementeSemPlano):
        R.modo_da_config({**CFG, "unidades": {**CFG["unidades"], "bases": [26101]}})
    with pytest.raises(ValueError, match="processos"):
        R.rodar(FUMACA, tmp_path / "x", 5)
    (tmp_path / "existe").mkdir()
    with pytest.raises(FileExistsError):
        R.rodar(FUMACA, tmp_path / "existe", 1)


def test_o_numero_de_vidas():
    # 200 unidades x 6 bracos x 12 celulas, mais 40 unidades x 3 bracos x 8 celulas do v38
    assert R.esperadas(200, 40) == 14400 + 960


def _gates(longe, hora, forr, estado, ni):
    return {"G-PV2-LONGE": {"passa": longe}, "G-PV2-HORA": {"passa": hora}, "G-FORR": {"passa": forr},
            "G-ESTADO": {"passa": estado}, "G-ESTADO-NI": {"passa": ni}}


@pytest.mark.parametrize("longe,hora,forr,quer", [
    (True, True, True, "a quimiotaxia funciona e gira na hora certa"),
    (True, False, True, "ajuda, mas pelo numero de viradas"),
    (False, True, True, "sem ganho sobre a tropotaxia"),
    (True, True, False, "custa perto de casa"),
    (False, False, False, "custa perto de casa"),
])
def test_a_regra_de_leitura_da_secao_7(longe, hora, forr, quer):
    lt = R.leitura(_gates(longe, hora, forr, True, True))
    assert lt["quimiotaxia"]["leitura"] == quer
    assert R.leitura(_gates(longe, hora, True, False, True))["olf_g"]["leitura"] == "o ganho nao entra"
    assert R.leitura(_gates(longe, hora, True, True, True))["olf_g"]["leitura"] == "o ganho entra"


def test_uma_vida_com_o_contrafactual(tmp_path):
    """o OLF-DCV com k = 0: o leitor da SE-C liga, o G1 do replay (sem o leitor) passa, e a vida guarda o que a SE-C pede"""
    u = {"base": 101, "k": 0, "semente": 101}
    cfg = {**FUMACA, "dias": 1}
    v = R._vida(cfg, "OLF-DCV", "atencioso", "longe", u, str(tmp_path))
    assert v["contrafactual"] and {"canais", "A4", "RV"} <= set(v["se"])
    sem = R._vida(cfg, "OLF-DCV", "atencioso", "longe", {**u, "k": R.K_SUBAMOSTRA}, str(tmp_path / "b"))
    assert not sem["contrafactual"] and "se" not in sem
    assert v["pv2"] == sem["pv2"]                      # o leitor nao muda a vida
    v38 = R._vida(cfg, "OLF-DCV", "atencioso", "longe", u, str(tmp_path / "c"), v38=True)
    assert v38["grupo"] == "v38" and not v38["contrafactual"]
