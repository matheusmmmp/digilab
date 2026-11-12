"""A GV3b do GOSTO_VISUAL: o orquestrador da GV3 com o enjoo ligado (docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1.md).

- as configs novas (`piloto_enjoo.json` e `gosto_visual_enjoo.json`): a fase `gosto_visual_enjoo`, o adendo como plano, as bases e o K
  do adendo, os modos `piloto_enjoo` e `gosto_visual_enjoo`; a trava (o adendo PROPOSTO ou sem o registro, o plano da GV3 sem a marca,
  as bases da GV3 na fase nova e as da GV3b na fase velha recusam);
- as configs antigas seguem nos modos de antes (`piloto`, `gosto_visual`), e a vida sem o enjoo sai a mesma (o caminho de antes, sem o
  argumento; a vida da GV3 byte a byte fica no tests/test_gabarito_gosto_visual_enjoo.py);
- a faixa 90101...90505 reservada, confirmada pelo coordenador em 2026-11-12, sem cruzar outra; desde o adendo 2 (D-GV-GV3B-12 e
  D-GV-GV3B2-5) ela esta QUEIMADA, e as configs do adendo 1 sao recusadas pela trava. Os testes da trava do adendo 1 rodam com a tabela
  de queimadas de antes (a fixture `antes_da_queima`), para conferir a trava como ela era;
- a fumaca com o enjoo ligado (a semente 101, 2 dias): o corpo e o cerebro com o enjoo, o replay do disco (G1) e a sonda (G2) passam, e a
  vida sai diferente da vida sem o enjoo.
Sementes: as dos testes (101) e as derivadas delas. Nenhuma vida da faixa roda aqui.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_gosto_visual as R  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v3_gosto_visual"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / nome).read_text(encoding="utf-8"))


QUEIMADAS_ANTES = tuple(f for f in bv.FAIXAS_QUEIMADAS if (f[0], f[1]) != R.FAIXA_ENJOO)


@pytest.fixture
def antes_da_queima(monkeypatch):
    """a tabela de queimadas de antes do adendo 2 (sem a 90101...90505), so na trava do orquestrador"""
    monkeypatch.setattr(R, "FAIXAS_QUEIMADAS", QUEIMADAS_ANTES)


def _adendo(status: str = "**Status: APROVADO pelo Matheus em 2026-11-12.**", registro: bool = True) -> str:
    """um texto do adendo so com o que a trava le: o titulo, o status nas primeiras linhas e a secao do registro"""
    return "\n".join(["# adendo", "", status, "", "## 1. algo"] + ([R.TITULO_REGISTRO_ENJOO] if registro else []) + [""])


def test_as_configs_novas_seguem_o_adendo_e_as_antigas_os_modos_de_antes(antes_da_queima):
    for nome, bases in (("piloto_enjoo.json", R.BASES_PILOTO_ENJOO), ("gosto_visual_enjoo.json", R.BASES_RUN_ENJOO)):
        cfg = _cfg(nome)
        assert cfg["fase"] == R.FASE_ENJOO and cfg["plano"] == R.PLANO_ENJOO and tuple(cfg["unidades"]["bases"]) == bases
        assert cfg["dias"] == R.DIAS
    assert R.modo_da_config(_cfg("piloto_enjoo.json"), _adendo()) == "piloto_enjoo"
    assert R.modo_da_config(_cfg("gosto_visual_enjoo.json"), _adendo()) == "gosto_visual_enjoo"
    assert _cfg("piloto_enjoo.json")["unidades"]["k"] == R.K_PILOTO and _cfg("gosto_visual_enjoo.json")["unidades"]["k"] == R.K_RUN
    assert R.modo_da_config(_cfg("piloto.json")) == "piloto" and R.modo_da_config(_cfg("gosto_visual.json")) == "gosto_visual"
    # o adendo de verdade (APROVADO, com o registro): a trava passa
    assert R.modo_da_config(_cfg("piloto_enjoo.json")) == "piloto_enjoo"
    assert R.modo_da_config(_cfg("gosto_visual_enjoo.json")) == "gosto_visual_enjoo"
    assert not R.FASES[R.FASE]["enjoo"] and R.FASES[R.FASE_ENJOO]["enjoo"]


def test_a_trava_da_gv3b(antes_da_queima):
    cfg = _cfg("piloto_enjoo.json")
    with pytest.raises(RuntimeError, match="APROVADO"):
        R.modo_da_config(cfg, _adendo("**Status: PROPOSTO, a espera do Matheus.**"))
    with pytest.raises(RuntimeError, match="registro"):
        R.modo_da_config(cfg, _adendo(registro=False))
    with pytest.raises(ValueError):
        R.modo_da_config({**cfg, "dias": 13}, _adendo())
    with pytest.raises(ValueError):
        R.modo_da_config({**cfg, "unidades": {"bases": [90101, 90202], "k": 3}}, _adendo())
    with pytest.raises(ValueError):
        R.modo_da_config({**cfg, "plano": R.PLANO}, _adendo())
    with pytest.raises(bv.SementeSemPlano):                  # as bases da GV3 na fase nova, e as da GV3b na fase velha
        R.modo_da_config({**cfg, "unidades": {"bases": list(R.BASES_PILOTO), "k": 2}}, _adendo())
    with pytest.raises(bv.SementeSemPlano):
        R.modo_da_config({**_cfg("piloto.json"), "unidades": {"bases": list(R.BASES_PILOTO_ENJOO), "k": 2}})
    with pytest.raises(ValueError, match="fase"):
        R.modo_da_config({**cfg, "fase": "outra"}, _adendo())


def test_a_trava_da_gv3b_pede_o_plano_da_gv3_aprovado(monkeypatch, antes_da_queima):
    sem_marca = R._plano(R.PLANO).replace(R.MARCA_APROVADO, "**Status: PROPOSTO")
    real = R._plano
    monkeypatch.setattr(R, "_plano", lambda plano=R.PLANO: sem_marca if plano == R.PLANO else real(plano))
    with pytest.raises(RuntimeError, match="APROVADO"):
        R.modo_da_config(_cfg("piloto_enjoo.json"), _adendo())


def test_a_faixa_da_gv3b_esta_reservada_confirmada_e_nao_cruza_outra_nem_uma_queimada():
    faixas = [(lo, hi, f) for lo, hi, f in bv.FAIXAS_RESERVADAS if (lo, hi) == R.FAIXA_ENJOO]
    assert len(faixas) == 1 and "confirmada pelo coordenador, 2026-11-12" in faixas[0][2]
    assert "PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1" in faixas[0][2]
    lo, hi = R.FAIXA_ENJOO
    for a, b, _ in bv.FAIXAS_RESERVADAS:
        if (a, b) != R.FAIXA_ENJOO:
            assert b < lo or a > hi, f"a faixa cruza {a}...{b}"
    for a, b, _ in QUEIMADAS_ANTES:
        assert b < lo or a > hi
    assert all(lo <= b <= 90202 for b in R.BASES_PILOTO_ENJOO) and all(90303 <= b <= hi for b in R.BASES_RUN_ENJOO)
    us = R.unidades(R.BASES_PILOTO_ENJOO, R.K_PILOTO) + R.unidades(R.BASES_RUN_ENJOO, R.K_RUN)
    velhas = R.unidades(R.BASES_PILOTO, R.K_PILOTO) + R.unidades(R.BASES_RUN, R.K_RUN)
    valores = {u["semente"] for u in us} | {u["genoma"] for u in us}
    assert len(valores) == 2 * len(us) and not valores & ({u["semente"] for u in velhas} | {u["genoma"] for u in velhas})


def test_a_fumaca_com_o_enjoo_ligado(tmp_path):
    cfg = {"fase": R.FASE_ENJOO, "plano": R.PLANO_ENJOO, "unidades": {"bases": [101], "k": 1}, "dias": 2}
    assert R.modo_da_config(cfg) == "fumaca"
    out = R.rodar(cfg, tmp_path / "fumaca", 1, boot=20)
    r, meta = out["resultado"], out["meta"]
    assert r["modo"] == "fumaca" and r["fase"] == R.FASE_ENJOO and r["plano"] == R.PLANO_ENJOO
    assert r["vidas"] == len(R.GENOMAS) * len(R.DONOS)
    assert meta["enjoo_tela"]["ligada"] is True and meta["plano_base"] == R.PLANO and "corpo.py" in meta["sha256"]
    assert len(list((tmp_path / "fumaca" / "vidas").glob("*_sonda.json"))) == 6
    u = R.unidades([101], 1)[0]
    m1, _, _ = R.viver("proprio", "calmo", u, 2, enjoo=True)
    m0, _, _ = R.viver("proprio", "calmo", u, 2)
    c1, c0 = sd.cerebro_da_copia(m1), sd.cerebro_da_copia(m0)
    assert c1.ce is not None and c1.ce.ligada and c0.ce is None
    assert m1.corpo.enjoo and not m0.corpo.enjoo
    assert [x["olhar"] for x in c1.motivos] != [x["olhar"] for x in c0.motivos]   # o cerebro sai outro com o enjoo


def test_a_faixa_da_gv3b_esta_queimada_e_as_configs_do_adendo_1_sao_recusadas():
    """o adendo 2, secao 6 (D-GV-GV3B-12): a 90101...90505 nao volta"""
    q = [f for f in bv.FAIXAS_QUEIMADAS if (f[0], f[1]) == R.FAIXA_ENJOO]
    assert len(q) == 1 and "D-GV-GV3B-12" in q[0][2]
    reservada = [f for lo, hi, f in bv.FAIXAS_RESERVADAS if (lo, hi) == R.FAIXA_ENJOO]
    assert len(reservada) == 1 and reservada[0].startswith("QUEIMADA")       # queimada continua reservada
    for nome in ("piloto_enjoo.json", "gosto_visual_enjoo.json"):
        with pytest.raises(bv.SementeSemPlano, match="queimada"):
            R.modo_da_config(_cfg(nome))
        with pytest.raises(bv.SementeSemPlano, match="queimada"):
            R.modo_da_config(_cfg(nome), _adendo())
