"""O orquestrador da ablacao do corpo (experiments/run_v3_corpo.py; docs/PLANO_ANALISE_V3_CORPO.md): os bracos mudam so as suas chaves, o
CTRL e o REL da run da D, a conferencia falha alto, a regra de leitura escrita antes, a trava da config e uma fumaca dos dois blocos, nas
sementes dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_corpo as R  # noqa: E402
import run_v3_corpo_acoplamento as CA  # noqa: E402
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_CONSERTO_VALUATION, CONFIG_DIGESTAO_CORPO,  # noqa: E402
                            CONFIG_DIGESTAO_CORPO_INTEIRA, CONFIG_REFLEXO_SUAVE)

FUMACA = json.loads((RAIZ / "experiments/configs/v3_corpo/fumaca.json").read_text(encoding="utf-8"))
RUN = json.loads((RAIZ / "experiments/configs/v3_corpo/run.json").read_text(encoding="utf-8"))


def test_cada_braco_muda_so_a_sua_chave():
    ctrl = R.montar("CTRL")
    assert ctrl == {"acoplamento": CA.montar("REL")["acoplamento"], "digestao": CONFIG_DIGESTAO_CORPO, "conserto": CONFIG_CONSERTO_VALUATION}
    assert R.montar("D") == {**ctrl, "acoplamento": CONFIG_ACOPLAMENTO_CORPO_LIGADA}
    assert R.montar("DE") == {**R.montar("D"), "digestao": CONFIG_DIGESTAO_CORPO_INTEIRA}
    assert R.montar("DC5") == {**R.montar("D"), "conserto": CONFIG_REFLEXO_SUAVE}
    with pytest.raises(ValueError):
        R.montar("C1")


@pytest.mark.parametrize("braco_aqui, braco_la", [("CTRL", "REL"), ("D", "D")])
def test_o_ctrl_e_a_d_sao_as_vidas_da_run_da_d(braco_aqui, braco_la):
    a = R.viver(braco_aqui, "atencioso", "longe_fixo", 101, 2, 16)[0]
    b = CA.viver(braco_la, "atencioso", "longe_fixo", 101, 2, 16)[0]
    assert a.log.para_jsonl() == b.log.para_jsonl()


def test_a_conferencia_pega_a_chave_errada():
    motor, registro, _, _, baixas = R.viver("D", "atencioso", "comedouro", 101, 1, 16)
    with pytest.raises(RuntimeError, match="acoplamento"):
        R.conferir_vida("CTRL", motor, registro, baixas)
    with pytest.raises(RuntimeError, match="digestao"):
        R.conferir_vida("DE", motor, registro, baixas)
    with pytest.raises(RuntimeError, match="conserto"):
        R.conferir_vida("DC5", motor, registro, baixas)
    R.conferir_vida("D", motor, registro, baixas)


def _cb(classe_f, rejeita, b_passa=True, s_passa=True):
    return {"F": {"classe": {"classe": classe_f}, "holm": {"rejeita": rejeita}},
            "B": {"privacao_comedouro": {"passa": b_passa}}, "S": {"S1_chutes_por_dia": {"passa": s_passa}}}


@pytest.mark.parametrize("cb, leitura", [(_cb("> 0", True), "ganho"), (_cb("> 0", True, b_passa=False), "perda"),
                                         (_cb("> 0", True, s_passa=False), "perda"), (_cb("> 0", False), "nulo"),
                                         (_cb("≈ 0", False), "nulo"), (_cb("< 0", False), "nulo"), (_cb("indeterminado", False), "indeterminado")])
def test_a_regra_de_leitura_escrita_antes(cb, leitura):
    assert R.leitura_do_braco(cb)["leitura"] == leitura


def test_a_trava_e_a_config():
    assert R.modo_da_config(FUMACA) == "fumaca"
    assert tuple(RUN["unidades"]["bases"]) == R.BASES_I and tuple(RUN["pares"]["bases"]) == R.BASES_II
    assert RUN["unidades"]["k"] == RUN["pares"]["k"] == R.K_POR_BASE == 1
    errada = {**RUN, "unidades": {**RUN["unidades"], "bases": RUN["unidades"]["bases"][:-1]}}
    with pytest.raises(bv.SementeSemPlano):
        R.modo_da_config(errada)
    with pytest.raises(ValueError):
        R.modo_da_config({**FUMACA, "fase": "outra"})
    with pytest.raises(ValueError):
        R.modo_da_config({**FUMACA, "pares": {**FUMACA["pares"], "prefixo": "social_par"}})


def test_a_fumaca_roda_os_dois_blocos(tmp_path):
    cfg = {**FUMACA, "unidades": {**FUMACA["unidades"], "bases": [101]}, "pares": {**FUMACA["pares"], "bases": [101], "dias": 1}}
    r = R.rodar(cfg, tmp_path / "f", 1)
    assert r["resultado"]["vidas"] == len(R.BRACOS) * len(R.CELULAS) and r["resultado"]["pares"] == len(R.BRACOS)
    assert set(r["resultado"]["veredito"]["bracos"]) == set(R.TRATADOS)
    for n in ("medidas.json", "pares.json", "resultado.json", "vidas.tar.gz", "pares.tar.gz", "meta.json"):
        assert (tmp_path / "f" / n).exists()
    with pytest.raises(FileExistsError):
        R.rodar(cfg, tmp_path / "f", 1)
