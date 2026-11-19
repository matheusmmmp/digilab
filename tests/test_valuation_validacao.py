"""A VALUATION V4 (docs/PLANO_ANALISE_V3_VALUATION_VALIDACAO.md): a baseline lida da calibracao da A1, as vidas dos tres bracos, a regra de
leitura escrita antes, a trava da run e uma fumaca do orquestrador (experiments/run_v3_valuation_validacao.py), com as sementes dos
testes."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_baseline_trivial as B  # noqa: E402
import run_v3_valuation_conserto as K  # noqa: E402
import run_v3_valuation_validacao as W  # noqa: E402


# ------------------------------------------------------------------ a baseline (VB-2)
def test_a_triv_e_o_ponto_da_calibracao_da_a1():
    lim, cal = W.limiares_da_a1()
    assert (lim.fome, lim.energia, lim.tedio) == (0.4, 0.1, 0.5)
    assert cal["escolhido"]["fome"] == 0.4 and len(cal["resultado_sha256"]) == 64


def test_uma_calibracao_que_nao_confere_falha_alto(tmp_path):
    copia = tmp_path / "cal"
    shutil.copytree(W.CALIBRACAO_A1, copia)
    r = json.loads((copia / "resultado.json").read_text(encoding="utf-8"))
    r["escolhido"]["fome"] = 0.8
    (copia / "resultado.json").write_text(json.dumps(r), encoding="utf-8")
    with pytest.raises(RuntimeError, match="nao confere"):
        W.limiares_da_a1(copia)


# ------------------------------------------------------------------ os bracos
def test_os_tres_bracos_e_as_vidas_de_cada_um():
    assert W.BRACOS == ("TRIV", "REL", "CON") and len(W.CELULAS) == 12
    lim, _ = W.limiares_da_a1()
    a, *_ = B.viver_triv(lim, "relapso", "longe_fixo", 101, 2, 16)
    b, *_ = B.viver_triv(lim, "relapso", "longe_fixo", 101, 2, 16)
    assert a.log.para_jsonl() == b.log.para_jsonl()
    rel, con = K.montar("REL"), K.montar("CON")
    assert not rel["conserto"].guarda_fome_reflexo and con["conserto"].guarda_fome_reflexo


# ------------------------------------------------------------------ a regra de leitura (3.2)
def _prim(classe):
    return {"classe": {"classe": classe}}


def test_a_regra_de_leitura_escrita_antes():
    assert W.leitura(_prim("> 0"))["leitura"] == "ganho"
    assert W.leitura(_prim("≈ 0"))["leitura"] == "nulo"
    assert W.leitura(_prim("< 0"))["leitura"] == "perda"
    assert W.leitura(_prim("indeterminado"))["leitura"] == "indeterminado"
    with pytest.raises(KeyError):
        W.leitura(_prim("outra"))


# ------------------------------------------------------------------ a trava
def _cfg(bases, k, dias=14):
    return {"descricao": "x", "plano": W.PLANO, "fase": W.FASE, "unidades": {"bases": list(bases), "k": k, "prefixo": W.PREFIXO},
            "dias": dias, "orcamento_por_dia": 16}


def test_a_trava_e_a_config():
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        W.exigir_aprovado("**Status: PROPOSTO.**\n")
    W.exigir_aprovado("**Status: APROVADO pelo Matheus em 2026-11-18** (x)\n")
    assert W.modo_da_config(_cfg((101, 202), 2, 3)) == "fumaca"
    with pytest.raises(bv.SementeSemPlano):
        W.modo_da_config(_cfg((73101,), 40))
    with pytest.raises(ValueError, match="fase"):
        W.modo_da_config({**_cfg((101,), 1, 2), "fase": "conserto"})
    cfg = json.loads((RAIZ / "experiments" / "configs" / "v3_valuation" / "validacao.json").read_text(encoding="utf-8"))
    assert tuple(cfg["unidades"]["bases"]) == W.BASES and cfg["unidades"]["k"] == W.K_POR_BASE and cfg["plano"] == W.PLANO
    with pytest.raises(ValueError, match="processos"):
        W.rodar(_cfg((101,), 1, 2), Path("nao_existe"), 5)


# ------------------------------------------------------------------ a fumaca
def test_a_fumaca_roda_os_tres_bracos_nas_12_celulas(tmp_path):
    r = W.rodar(_cfg((101,), 1, 2), tmp_path / "fum", 1)
    res, meta = r["resultado"], r["meta"]
    assert res["vidas"] == len(W.BRACOS) * 12 == 36
    assert res["limiares_triv"]["fome"] == 0.4 and meta["calibracao_a1"]["escolhido"]["energia"] == 0.1
    assert res["leitura"]["leitura"] in ("ganho", "nulo", "perda", "indeterminado")
    assert set(res["secundarias"]) == {"REL - TRIV, longe_fixo (a replica da A1)", "CON - TRIV, comedouro", "CON - TRIV, longe"}
    assert set(meta["artefatos_sha256"]) == {"medidas.json", "resultado.json", "vidas.tar.gz"}
    assert {reg["braco"] for reg in r["registros"]} == set(W.BRACOS)
    with pytest.raises(FileExistsError):
        W.rodar(_cfg((101,), 1, 2), tmp_path / "fum", 1)
