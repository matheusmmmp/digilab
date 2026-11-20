"""MUNDO-CALIBRACAO (PLANO_ANALISE_V2_MUNDO_FISICO, secao 6 e A1.4): o orquestrador da calibracao do mundo fisico. O modo pelas sementes
(a validacao recusada), a config da calibracao a letra do plano, as chaves novas desligadas, a analise em dados com resposta conhecida
(a estatistica por unidade, a regra do menor m, o K pelo poder simulado) e uma run minima de ponta a ponta nas sementes dos testes."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_mundo as rc  # noqa: E402

CFG = json.loads((RAIZ / "experiments/configs/v2_mundo/calibracao.json").read_text(encoding="utf-8"))
FUMACA = json.loads((RAIZ / "experiments/configs/v2_mundo/fumaca_calibracao.json").read_text(encoding="utf-8"))


def _mini() -> dict:
    cfg = json.loads(json.dumps(FUMACA))
    cfg.update({"unidades": {"bases": [101, 202], "k": 1, "prefixo": "mundo"}, "donos": ["atencioso"],
                "lugares": ["comedouro", "longe"], "dias": 2, "orcamento": 32,
                "sonda": {"estados": 4, "amostras": 4, "semente": 101},
                "bootstrap": {"reamostragens": 200, "semente": 4242, "nivel": 0.95}})
    cfg["poder"] = dict(cfg["poder"], replicas=50)
    return cfg


# ================================================================== o modo e a config
def test_o_modo_pelas_sementes():
    assert rc.modo_da_config(CFG) == "calibracao"
    assert rc.modo_da_config(FUMACA) == "fumaca"
    for bases in ([32101, 32202, 32303, 32404, 32505], [32101]):
        cfg = dict(CFG, unidades=dict(CFG["unidades"], bases=bases))
        with pytest.raises(bv.SementeSemPlano):
            rc.modo_da_config(cfg)
    with pytest.raises(bv.SementeSemPlano):
        rc.modo_da_config(dict(CFG, unidades=dict(CFG["unidades"], bases=[14101])))


def test_a_calibracao_segue_o_plano_a_letra():
    assert CFG["plano"] == rc.PLANO and (RAIZ / rc.PLANO).is_file()
    assert tuple(CFG["grade_m"]) == (0.5, 1.0, 2.0) and CFG["unidades"]["k"] == 4
    for mudanca in ({"grade_m": [0.5, 1.0]}, {"dias": 7}, {"plano": "docs/OUTRO.md"},
                    {"unidades": dict(CFG["unidades"], k=6)}, {"lugares": ["comedouro", "perto"]},
                    {"poder": dict(CFG["poder"], replicas=500)}, {"bootstrap": dict(CFG["bootstrap"], semente=1)}):
        with pytest.raises(ValueError):
            rc.modo_da_config(dict(CFG, **mudanca))
    with pytest.raises(ValueError):
        rc.modo_da_config(dict(CFG, mundo="fisico_afastado"))
    with pytest.raises(ValueError):
        rc.modo_da_config({k: v for k, v in CFG.items() if k != "chaves_desligadas"})
    # a fumaca e a mesma config, so com as sementes dos testes
    assert {k: v for k, v in FUMACA.items() if k not in ("descricao", "unidades")} == \
           {k: v for k, v in CFG.items() if k not in ("descricao", "unidades", "plano")}


def test_as_chaves_novas_desligadas_em_todo_braco():
    u = bv.unidades_derivadas([101], 1, "mundo")[0]
    for m in CFG["grade_m"]:
        cb = rc.config_bancada(CFG, m, ["P0", "P0z", "P1"], CFG["piloto"]["acoplados"])
        assert cb["mundo"] == {"mult_queda": m}
        b = bv.bancada_da_config(cb)
        assert b.cfg_mundo.mult_queda == m
        out = rc.conferir_desligadas(b, cb, u)
        assert set(out) == {"P0", "P0z", "P1"}
        assert not any(v for d in out.values() for v in d.values())
    b = bv.bancada_da_config(cb)
    b_ligada = replace(b, cfg_lobos=replace(b.cfg_lobos, presenca_fruta_mundo=True))
    with pytest.raises(RuntimeError):
        rc.conferir_desligadas(b_ligada, cb, u)
    with pytest.raises(RuntimeError):
        rc.conferir_desligadas(replace(b, julgamento_fruta=True), cb, u)


# ================================================================== a analise
def _reg(s, dono, lugar, braco, **med):
    return {"semente": s, "dono": dono, "lugar": lugar, "braco": braco, **med}


def test_a_estatistica_por_unidade_e_a_media_das_celulas():
    cel = [("a", "x"), ("a", "y")]
    regs = [_reg(1, "a", "x", "P0z", d_fe=0.5), _reg(1, "a", "x", "P0", d_fe=0.3),
            _reg(1, "a", "y", "P0z", d_fe=0.4), _reg(1, "a", "y", "P0", d_fe=0.4),
            _reg(2, "a", "x", "P0z", d_fe=0.1), _reg(2, "a", "x", "P0", d_fe=0.2),
            _reg(2, "a", "y", "P0z", d_fe=0.6), _reg(2, "a", "y", "P0", d_fe=0.3)]
    assert rc.por_unidade(regs, "P0z", "P0", "d_fe", cel) == pytest.approx({1: 0.1, 2: 0.1})
    with pytest.raises(RuntimeError):
        rc.por_unidade(regs[:-1], "P0z", "P0", "d_fe", cel)
    with pytest.raises(RuntimeError):
        rc.por_unidade(regs + [regs[0]], "P0z", "P0", "d_fe", cel)


def test_a_regra_pega_o_menor_m_que_passa():
    assert rc.escolher_m({0.5: {"passa": False}, 1.0: {"passa": True}, 2.0: {"passa": True}}) == 1.0
    assert rc.escolher_m({0.5: {"passa": True}, 1.0: {"passa": False}, 2.0: {"passa": True}}) == 0.5
    assert rc.escolher_m({0.5: {"passa": False}, 1.0: {"passa": False}, 2.0: {"passa": False}}) is None


def test_a_premissa_pelo_ic95():
    cel = [("a", "x")]
    regs = []
    for s in range(1, 21):
        regs += [_reg(s, "a", "x", "P0z", d_fe=0.40 + 0.001 * s), _reg(s, "a", "x", "P0", d_fe=0.30)]
    p = rc.premissa(regs, cel, {"reamostragens": 1000, "semente": 4242, "nivel": 0.95})
    assert p["passa"] and p["ic95"]["ic_inferior"] > 0 and p["media"] == pytest.approx(0.1105)
    regs_neg = [dict(r, d_fe=0.30 if r["braco"] == "P0z" else r["d_fe"] + 0.1) for r in regs]
    assert not rc.premissa(regs_neg, cel, {"reamostragens": 1000, "semente": 4242, "nivel": 0.95})["passa"]


def test_o_k_pelo_poder_simulado():
    poder = {"k_min": 4, "k_max": 10, "replicas": 400, "alvo": 0.8, "alfa": 0.025}
    difs = [0.01 * ((i % 5) - 2) for i in range(20)]           # dp ~0,014
    facil = rc.escolher_k(difs, 0.05, poder, 4242, 5)
    assert facil["k"] == 4 and facil["n"] == 20 and facil["chega_ao_alvo"] and facil["poder"] >= 0.8
    dificil = rc.escolher_k(difs, 0.001, poder, 4242, 5)
    assert dificil["k"] == 10 and dificil["n"] == 50 and not dificil["chega_ao_alvo"] and dificil["poder"] < 0.8
    assert [t["k"] for t in dificil["tabela"]] == list(range(4, 11))
    meio = rc.escolher_k(difs, 0.008, poder, 4242, 5)          # o primeiro K da tabela que chega ao alvo
    assert meio["chega_ao_alvo"] and meio["k"] == next(t["k"] for t in meio["tabela"] if t["poder"] >= 0.8)
    assert meio["tabela"][0]["poder"] < meio["tabela"][-1]["poder"]


# ================================================================== de ponta a ponta, minima
def test_run_minima_de_ponta_a_ponta(tmp_path, monkeypatch):
    cfg = _mini()
    monkeypatch.setattr(rc, "escolher_m", lambda premissas: 1.0)     # forca o piloto: a regra e testada acima
    pasta = tmp_path / "cal"
    out = rc.rodar(cfg, pasta, 1)
    res, med = out["resultado"], out["medidas"]
    assert res["m_escolhido"] == 1.0 and res["fechou"]
    assert set(med["grade"]) == {"0.5", "1", "2"}
    for m, regs in med["grade"].items():
        assert len(regs) == 2 * 2 * 2 and {r["braco"] for r in regs.values()} == {"P0", "P0z"}
        assert all(r["m"] == float(m) for r in regs.values())
        assert (pasta / "grade" / f"m_{m}" / "medidas.json").is_file()
        assert len(list((pasta / "grade" / f"m_{m}" / "vidas").glob("*.jsonl"))) == 8
    assert {r["braco"] for r in med["piloto"].values()} == {"P1", rc.ROT_P0AC, rc.ROT_P1AC}
    assert len(med["piloto"]) == 2 * 2 * 3
    assert all(r["origem"] is not None and "P0z" in r["origem"] for r in med["piloto"].values() if r["braco"] != "P1")
    assert res["delta_mf"] == pytest.approx(0.5 * res["premissa_por_m"]["1"]["media"])
    assert [t["k"] for t in res["n"]["tabela"]] == list(range(4, 11))
    assert set(res["poder_relato"]) == {"G-MF2r", "G-MF3r", "G-PERM, G-OPORT, G-DIST"}
    assert "validacao_estimada" in res["custo"] and res["custo"]["validacao_estimada"]["vidas"] == 2 * 2 * 5 * res["n"]["k"]
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["sha256"]) == {"mundo.py", "config.py", "lobos.py", "engine.py", "plano", "config"}
    assert meta["sha256"]["plano"] == rc._sha_arquivo(RAIZ / rc.PLANO)
    # os acoplados do piloto partem do P0z da grade (o mesmo log)
    for r in med["piloto"].values():
        if r["origem"]:
            assert (pasta / "grade" / "m_1" / "vidas" / f"{r['origem']}.jsonl").is_file()
    with pytest.raises(FileExistsError):
        rc.rodar(cfg, pasta, 1)


def test_sem_m_que_passe_para_sem_piloto(tmp_path, monkeypatch):
    cfg = _mini()
    cfg["grade_m"] = [1.0]
    monkeypatch.setattr(rc, "escolher_m", lambda premissas: None)
    out = rc.rodar(cfg, tmp_path / "cal", 1)
    assert not out["resultado"]["fechou"] and out["resultado"]["m_escolhido"] is None
    assert out["medidas"]["piloto"] == {} and not (tmp_path / "cal" / "piloto").exists()
    assert "delta_mf" not in out["resultado"]


# ================================================================== a E2 na dominancia do mundo fisico (o defeito que a fumaca achou)
def test_a_dominancia_do_mundo_fisico_segue_a_e2_do_cerebro():
    """No mundo fisico o motor avisa `fruta_comida` tambem no "achou e comeu" do explorar, e o cerebro credita esse explorar com o
    sinal do N3 (sem o humor). A medida da dominancia tem de seguir a mesma regra: com o humor no explorar, a conferencia com os canais
    divergia (a vida da fumaca, unidade da base 101, incoerente no longe, m = 1). Agora confere, e a vida tem explorar que comeu fruta."""
    u = bv.unidades_derivadas([101], 1, "mundo")[0]
    b = bv.bancada_da_config(rc.config_bancada(CFG, 1.0, ["P0", "P0z", "P1"], CFG["piloto"]["acoplados"]))
    v = b.vida(bv.EspecVida("incoerente", "P1", u["semente"], u["genoma"], "fisico", lugar="longe"))
    med = b.medir(v, {"estados": 4, "amostras": 4, "semente": 101})
    assert med["dominancia"]["conferido_com_canais"]
    regs = []

    def fab(cfg=None):
        reg = bv._Registro(b.politica(v.espec, cfg))
        regs.append(reg)
        return reg

    bv.reproduzir_mundo(bv.LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fab, semente=v.espec.semente,
                        fabrica_motor=b.fabrica_motor(v.espec))
    passos = regs[0].passos_sinal
    assert any(p["fruta"] is not None and p["acao"] == "explorar" for p in passos)
    assert all(bv.comeu_fruta_e2(p) == (p["fruta"] is not None and p["acao"] == "comer") for p in passos)
