"""O orquestrador da run da opcao D (experiments/run_v3_corpo_acoplamento.py; docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md): o REL daqui e a
vida do REL da VALUATION byte a byte, o D muda so o corpo, a conferencia do corpo falha alto, a trava segura a run e a fumaca roda com a
analise da secao 5."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_corpo_acoplamento as R  # noqa: E402
import run_v3_valuation_conserto as VC  # noqa: E402
from digilab.config import CONFIG_ACOPLAMENTO_CORPO_LIGADA  # noqa: E402

DIAS = 1


@pytest.fixture(scope="module")
def vidas():
    return {b: R.viver(b, "atencioso", "longe_fixo", 101, DIAS, R.ORCAMENTO_POR_DIA) for b in R.BRACOS}


def test_o_rel_e_a_vida_da_valuation(vidas):
    motor, registro, _, _, baixas = vidas["REL"]
    m0, r0, _, _, b0 = VC.viver("REL", "atencioso", "longe_fixo", 101, DIAS, R.ORCAMENTO_POR_DIA)
    assert motor.log.para_jsonl() == m0.log.para_jsonl()
    assert baixas == b0 and motor.serie_corpo == m0.serie_corpo


def test_o_d_muda_so_o_corpo(vidas):
    (mr, rr, *_), (md, rd, *_) = vidas["REL"], vidas["D"]
    assert md.corpo.ca == CONFIG_ACOPLAMENTO_CORPO_LIGADA and mr.corpo.ca.ligada is False
    cr, cd = R.orq.cerebro_de(rr), R.orq.cerebro_de(rd)
    assert (cr.cd, cr.inatos, cr.m.arb.cv) == (cd.cd, cd.inatos, cd.m.arb.cv)
    for b in R.BRACOS:
        R.conferir_corpo(b, vidas[b][0])


def test_a_conferencia_do_corpo_falha_alto(vidas):
    md = vidas["D"][0]
    with pytest.raises(RuntimeError, match="acoplamento"):
        R.conferir_corpo("REL", md)
    md.contabil.ticks_falta += 1
    try:
        with pytest.raises(RuntimeError, match="falta de combustivel"):
            R.conferir_corpo("D", md)
    finally:
        md.contabil.ticks_falta -= 1


def test_as_medidas_do_acoplamento(vidas):
    motor, registro, _, _, baixas = vidas["D"]
    a = R.medidas_acoplamento(motor, registro, baixas)
    assert a["decisoes"] == DIAS * 96 and a["conflitos"] == a["ambas"] / a["decisoes"]
    assert a["cansaco_por_fonte"]["falta_combustivel"] == 0


def _cfg(nome: str) -> dict:
    return json.loads((RAIZ / "experiments" / "configs" / "v3_corpo_acoplamento" / nome).read_text(encoding="utf-8"))


def test_a_trava():
    run = _cfg("run.json")
    assert R.modo_da_config(_cfg("fumaca.json")) == "fumaca"
    assert R.modo_da_config(run) == R.FASE                     # o plano APROVADO e a faixa reservada
    with pytest.raises(R.bv.SementeSemPlano):
        R.modo_da_config({**run, "unidades": {**run["unidades"], "bases": [73101, 73202, 73303, 73404, 73505]}})
    with pytest.raises(ValueError, match="letra"):
        R.modo_da_config({**run, "dias": 7})
    with pytest.raises(RuntimeError, match="APROVADO"):
        R.exigir_aprovado("**Status: PROPOSTO.**")
    with pytest.raises(ValueError):
        R.rodar(_cfg("fumaca.json"), RAIZ / "nao_existe", R.MAX_PROCESSOS + 1)


def test_a_fumaca(tmp_path):
    cfg = {**_cfg("fumaca.json"), "unidades": {"bases": [101], "k": 1, "prefixo": R.PREFIXO}, "dias": DIAS}
    r = R.rodar(cfg, tmp_path / "f", 1)
    assert r["resultado"]["vidas"] == len(R.BRACOS) * len(R.CELULAS)
    v = r["resultado"]["veredito"]
    assert v["leitura"] in ("passa", "falha", "efeito trivial")
    assert set(r["resultado"]["criterios"]) == {"P", "G1", "G2", "G3"}
    with pytest.raises(FileExistsError):
        R.rodar(cfg, tmp_path / "f", 1)
    assert replace(CONFIG_ACOPLAMENTO_CORPO_LIGADA).ligada
