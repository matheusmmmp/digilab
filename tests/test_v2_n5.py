"""V2, N5: o orquestrador da calibracao e da validacao (experiments/run_v2_n5.py; docs/PLANO_ANALISE_V2_N5.md, adendo 1) e o rotulo das
unidades derivadas na bancada. So fumaca nas sementes dos testes: nenhuma faixa reservada."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_n5 as rn  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402


def test_rotulo_das_unidades():
    padrao = bv.unidades_derivadas([12101], 2)
    assert padrao == bv.unidades_derivadas([12101], 2, "experimento-maior")
    n5 = bv.unidades_derivadas([12101], 2, "n5")
    assert [u["semente"] for u in n5] == [derivar_semente("n5", 12101, k) for k in range(2)]
    assert [u["genoma"] for u in n5] == [derivar_semente("n5-genoma", 12101, k) for k in range(2)]
    assert not {u["semente"] for u in n5} & {u["semente"] for u in padrao}
    with pytest.raises(ValueError):
        bv.unidades_derivadas([12101], 2, "")
    base = {"bracos": ["P0"], "donos": ["atencioso"], "dias": 2, "orcamento": 32, "sonda": {}, "bootstrap": {}}
    bv.validar_config({**base, "unidades": {"bases": [101], "k": 1, "rotulo": "n5"}})
    with pytest.raises(ValueError):
        bv.validar_config({**base, "unidades": {"bases": [101], "k": 1, "outro": 1}})


def test_configs_e_recusas(tmp_path):
    cal = rn.carregar(RAIZ / "experiments/configs/v2_n5/calibracao.json")
    assert cal["bases"] == list(rn.BASES["calibracao"]) and cal["grade_w0"] == [0, 256, 512, 768]
    for ruim in ({**cal, "bases": [13101, 13202, 13303, 13404, 13505]}, {**cal, "w0_info": 512}, {**cal, "dias": 4},
                 {"conjunto": "validacao", "bases": list(rn.BASES["validacao"]), "k": 4, "saida": "x", "w0_info": 512},
                 {"conjunto": "fumaca", "bases": [12101], "k": 1, "saida": "x", "grade_w0": [0]}):
        with pytest.raises((ValueError, KeyError)):
            rn.validar(dict(ruim))
    val = rn.validar({"conjunto": "validacao", "bases": list(rn.BASES["validacao"]), "k": 2, "saida": "x", "w0_info": 512,
                      "delta": 0.1, "delta_ef": 5.0})
    (tmp_path / "ja").mkdir()
    with pytest.raises(RuntimeError):
        rn.executar(val, tmp_path / "ja", {})


def test_poder_simulado():
    d = [0.1, -0.2, 0.3, 0.0, -0.1, 0.2, 0.05, -0.05]
    assert rn.poder_simulado(d, 2.0, 30, 0.05 / 3, 200, 1) > 0.95
    assert rn.poder_simulado(d, 0.0, 30, 0.05 / 3, 200, 1) < 0.1
    assert rn.poder_simulado(d, 0.1, 30, 0.05 / 3, 200, 1) == rn.poder_simulado(d, 0.1, 30, 0.05 / 3, 200, 1)


def test_fumaca_de_ponta_a_ponta(tmp_path):
    cfg = rn.validar({"descricao": "fumaca", "conjunto": "fumaca", "bases": [101, 202], "k": 1, "saida": "x", "dias": 4,
                      "orcamento": 64, "sonda": {"estados": 8, "amostras": 8, "semente": 101}, "grade_w0": [0, 512]})
    out = rn.executar(cfg, tmp_path, {"config": "fumaca"})
    assert out["g2_w0_zero_p2_igual_p1"] is True                 # w0_info 0: o P2 vive como o P1
    assert out["escolha"]["w0_info"] == 512 and out["validacao"]["N_validacao"] % 5 == 0
    for f in ("meta.json", "escolha.json", "varredura.jsonl", "w0_0/resultado.json", "w0_512/resultado.json",
              "w0_512/resultado_vidas.json", "w0_512/medidas.json"):
        assert (tmp_path / f).is_file(), f
    r = json.loads((tmp_path / "w0_512/resultado.json").read_text(encoding="utf-8"))
    assert set(r["familia"]) == {"G_EF", "G_PIORA", "G_REC"} and set(r["holm"]) == set(r["familia"])
    vidas = json.loads((tmp_path / "w0_512/resultado_vidas.json").read_text(encoding="utf-8"))["vidas"]
    p2e = [v for v in vidas.values() if v["braco"] == "P2e"]
    assert p2e and all(len(v["w_info_por_dia"]) == 4 and v["w0_info"] == 512 for v in p2e)
    assert {v["braco"] for v in vidas.values()} >= {"P0", "P1", "P2", "P2e", "P2a", "P2<P2:sem_ensino", "P2e<P2e:sem_ensino"}
