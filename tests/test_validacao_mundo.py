"""V2, MUNDO-VALIDACAO: o orquestrador da validacao do mundo fisico (experiments/run_v2_validacao_mundo.py). So as sementes dos testes:
o modo pela config, as categorias do G-MF1r, o Holm orientado, as inclinacoes e o G-DIST juntando as visitas por unidade, a leitura da
A1.5 e uma run minima de ponta a ponta (toda vida gravada e rejogada do disco)."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_validacao_mundo as rv  # noqa: E402

CFG_VALIDACAO = json.loads((RAIZ / "experiments/configs/v2_mundo/validacao.json").read_text(encoding="utf-8"))
CFG_FUMACA = json.loads((RAIZ / "experiments/configs/v2_mundo/fumaca_validacao.json").read_text(encoding="utf-8"))
BOOT = {"reamostragens": 2000, "semente": 4242, "nivel": 0.95}


# ------------------------------------------------------------------ o modo
def test_modo_da_config_validacao_e_fumaca():
    assert rv.modo_da_config(CFG_VALIDACAO) == "validacao"
    assert rv.modo_da_config(CFG_FUMACA) == "fumaca"


def test_validacao_presa_aos_numeros_da_a19():
    cal = json.loads((RAIZ / rv.CALIBRACAO).read_text(encoding="utf-8"))
    assert CFG_VALIDACAO["m"] == cal["m_escolhido"] == 1.0
    assert CFG_VALIDACAO["delta_mf"] == cal["delta_mf"]
    assert CFG_VALIDACAO["unidades"]["k"] == cal["n"]["k"] == 8
    for campo, valor in (("m", 2.0), ("delta_mf", 0.01)):
        c = copy.deepcopy(CFG_VALIDACAO)
        c[campo] = valor
        with pytest.raises(ValueError):
            rv.modo_da_config(c)
    c = copy.deepcopy(CFG_VALIDACAO)
    c["unidades"]["k"] = 4
    with pytest.raises(ValueError):
        rv.modo_da_config(c)
    c = copy.deepcopy(CFG_VALIDACAO)
    del c["plano"]
    with pytest.raises(ValueError):
        rv.modo_da_config(c)


def test_recusa_as_bases_da_calibracao_e_outras():
    c = copy.deepcopy(CFG_VALIDACAO)
    c["unidades"]["bases"] = [31101, 31202, 31303, 31404, 31505]
    with pytest.raises(bv.SementeSemPlano):
        rv.modo_da_config(c)
    c["unidades"]["bases"] = [99101]
    with pytest.raises(bv.SementeSemPlano):
        rv.modo_da_config(c)


def test_config_fora_do_plano_falha_alto():
    for mexer in (lambda c: c.update(holm={"alfa": 0.1}), lambda c: c.update(bracos_afastado=["P0"]),
                  lambda c: c.update(acoplados=[]), lambda c: c.update(extra=1)):
        c = copy.deepcopy(CFG_FUMACA)
        mexer(c)
        with pytest.raises(ValueError):
            rv.modo_da_config(c)


# ------------------------------------------------------------------ as categorias do G-MF1r (secao 8)
def _ic(i95, s95, i90, s90):
    return {"ic95": {"ic_inferior": i95, "ic_superior": s95, "nivel": 0.95},
            "ic90": {"ic_inferior": i90, "ic_superior": s90, "nivel": 0.90}}


@pytest.mark.parametrize("ics, esperada", [
    (_ic(0.002, 0.03, 0.004, 0.025), "ganha"),
    (_ic(0.001, 0.008, 0.002, 0.006), "ganha, abaixo de Delta"),
    (_ic(-0.03, -0.001, -0.025, -0.004), "perde"),
    (_ic(-0.009, 0.006, -0.006, 0.005), "equivalente"),
    (_ic(-0.02, 0.02, -0.015, 0.015), "inconclusivo"),
])
def test_categorias_g_mf1(ics, esperada):
    assert rv.categoria_g_mf1(ics, 0.0077)["categoria"] == esperada


def test_categoria_sem_ic_e_inconclusiva():
    assert rv.categoria_g_mf1({"ic95": None, "ic90": None}, 0.0077)["categoria"] == "inconclusivo"


# ------------------------------------------------------------------ as inclinacoes e o G-DIST por unidade
def _visita(perm, custo, taxa, censurada=False):
    return {"arvore": 0, "inicio": 0, "fim": perm, "permanencia": perm, "censurada": censurada, "custo_viagem": custo,
            "taxa_recente": taxa}


def _reg(semente, braco, visitas, mundo="fisico", razoes=()):
    return {"semente": semente, "braco": braco, "mundo": mundo, "visitas_lista": visitas, "razoes_abandono": list(razoes)}


def test_inclinacoes_juntam_as_visitas_da_unidade_e_orientam():
    regs = []
    for s in (1, 2, 3):
        # P0: permanencia = 10 + custo; P1: 10 + 3*custo - 2*taxa, com taxa = custo - 1, isto e, 12 + custo (a mesma inclinacao)
        regs.append(_reg(s, "P0", [_visita(10 + c, c, t, False) for c, t in ((1, 0), (2, 1))]))
        regs.append(_reg(s, "P0", [_visita(10 + 3, 3, 2), _visita(99, 5, 5, censurada=True)]))
        regs.append(_reg(s, "P1", [_visita(10 + 3 * c - 2 * t, c, t) for c, t in ((1, 0), (2, 1), (3, 2))]))
    r = rv.diferenca_inclinacoes(regs, "custo_viagem", 1, BOOT)
    assert r["n"] == 3 and r["sem_valor"] == 0
    # as visitas das linhas de cada unidade entram juntas: P0 (1, 11), (2, 12), (3, 13), a censurada fora; P1 (1, 13), (2, 14), (3, 15)
    p0 = rv.inclinacoes_por_unidade(regs, "P0", "custo_viagem")
    assert p0[1]["inclinacao"] == pytest.approx(1.0) and p0[1]["censuradas"] == 1
    p1 = rv.inclinacoes_por_unidade(regs, "P1", "custo_viagem")
    assert p1[1]["inclinacao"] == pytest.approx(1.0)
    rt = rv.diferenca_inclinacoes(regs, "taxa_recente", -1, BOOT)
    # na taxa: P0 (0, 11), (1, 12), (2, 13) -> 1; P1 (0, 13), (1, 14), (2, 15) -> 1: diferenca 0, orientada 0
    assert rt["p1_menos_p0"]["media"] == pytest.approx(0.0)


def test_orientacao_do_g_oport():
    regs = []
    for s, delta in ((1, -2.0), (2, -1.5), (3, -2.5), (4, -1.0)):
        regs.append(_reg(s, "P0", [_visita(10.0, 1, 0), _visita(10.0, 2, 1)]))
        regs.append(_reg(s, "P1", [_visita(10.0, 1, 0), _visita(10.0 + delta, 2, 1)]))
    r = rv.diferenca_inclinacoes(regs, "taxa_recente", -1, BOOT)
    assert r["p1_menos_p0"]["media"] == pytest.approx(-1.75)
    assert r["p1_menos_p0"]["ic95"]["ic_superior"] < 0          # a direcao predita: o P1 sai antes depois de dias ricos
    assert r["orientado"]["ic95"]["ic_inferior"] > 0 and r["orientado"]["p_unilateral"] == 0.0


def test_unidade_sem_inclinacao_fica_fora_contada():
    regs = [_reg(1, "P0", [_visita(10, 1, 0)]), _reg(1, "P1", [_visita(12, 1, 0), _visita(14, 2, 1)]),
            _reg(2, "P0", [_visita(10, 1, 0), _visita(11, 2, 1)]), _reg(2, "P1", [_visita(12, 1, 0), _visita(14, 2, 1)])]
    r = rv.diferenca_inclinacoes(regs, "custo_viagem", 1, BOOT)
    assert r["n"] == 1 and r["sem_valor"] == 1


def test_g_dist_por_unidade():
    regs = []
    for s in (1, 2, 3):
        regs += [_reg(s, "P0", [_visita(10, 1, 0)]), _reg(s, "P1", [_visita(10, 1, 0)]),
                 _reg(s, "P0@afastado", [_visita(12, 1, 0)], mundo="fisico_afastado"),
                 _reg(s, "P1@afastado", [_visita(15 + s, 1, 0)], mundo="fisico_afastado")]
    r = rv.g_dist(regs, BOOT)
    # [(15+s) - 10] - [12 - 10] = 3 + s
    assert r["media"] == pytest.approx(5.0) and r["sem_valor"] == 0


def test_razao_abandono_junta_as_razoes():
    regs = [_reg(1, "P0", [], razoes=(1.0, 3.0)), _reg(1, "P0", [], razoes=(2.0,)), _reg(1, "P1", [], razoes=(4.0,)),
            _reg(2, "P0", [], razoes=(1.0,)), _reg(2, "P1", [], razoes=())]
    r = rv.razao_abandono(regs, BOOT)
    assert r["sem_valor"] == 1 and r["p1_menos_p0"]["media"] == pytest.approx(2.0)


# ------------------------------------------------------------------ a leitura da A1.5
def test_leitura_a15():
    nao = {"passa": False}
    sim = {"passa": True}
    assert "nao e lido" in rv.leitura_a15(nao, {"categoria": "ganha"}, True)
    assert "e do pet" in rv.leitura_a15(sim, {"categoria": "ganha"}, True)
    assert "dono reagindo" in rv.leitura_a15(sim, {"categoria": "ganha, abaixo de Delta"}, False)
    for c in ("perde", "equivalente", "inconclusivo"):
        assert "nao aprende a procurar" in rv.leitura_a15(sim, {"categoria": c}, True)


# ------------------------------------------------------------------ a run minima de ponta a ponta
def test_run_minima_de_ponta_a_ponta(tmp_path):
    cfg = copy.deepcopy(CFG_FUMACA)
    cfg["unidades"] = {"bases": [101, 202], "k": 1, "prefixo": "mundo"}
    cfg["donos"], cfg["lugares"], cfg["dias"], cfg["orcamento"] = ["atencioso"], ["longe"], 2, 32
    cfg["sonda"] = {"estados": 4, "amostras": 10, "semente": 9001}
    cfg["bootstrap"] = {"reamostragens": 500, "semente": 4242, "nivel": 0.95}
    pasta = tmp_path / "val"
    saida = rv.rodar(cfg, pasta, 1)
    regs = saida["medidas"]
    assert len(regs) == 2 * 7                                    # 7 vidas por celula, 1 celula, 2 unidades
    rotulos = sorted({r["braco"] for r in regs.values()})
    assert rotulos == sorted(["P0", "P0z", "P1", rv.ROT_P0AC, rv.ROT_P1AC, "P0@afastado", "P1@afastado"])
    for r in regs.values():
        assert (r["mundo"] == "fisico_afastado") == r["braco"].endswith("@afastado")
        assert (pasta / "vidas" / f"{r['vida']}.jsonl").exists()
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert set(res["secundarios"]) == set(rv.HOLM)
    assert res["G-MF1r"]["categoria"] in ("ganha", "ganha, abaixo de Delta", "perde", "equivalente", "inconclusivo")
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert meta["modo"] == "fumaca" and set(meta["sha256"]) >= {"mundo.py", "engine.py", "plano"}
    with pytest.raises(FileExistsError):
        rv.rodar(cfg, pasta, 1)
