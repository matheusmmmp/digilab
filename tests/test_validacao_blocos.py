"""V2, validação única (V1): os blocos da seção 4 do PLANO_CALIBRACAO_CONJUNTA_V2 no orquestrador do experimento maior e o adendo 2 (o
delta na escala de cada medida). So as sementes dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v2_experimento_maior/fumaca.json").read_text(encoding="utf-8"))
VALIDACAO = json.loads((RAIZ / "experiments/configs/v2_experimento_maior/validacao.json").read_text(encoding="utf-8"))
ADENDO = json.loads((RAIZ / "artifacts_v2_calibracao_conjunta/adendo_opcao_a.json").read_text(encoding="utf-8"))


def test_config_da_validacao_e_a_do_adendo_2():
    modo, unidades = em.modo_e_unidades(VALIDACAO)
    assert modo == "validacao" and len(unidades) == ADENDO["N"] == 30
    assert unidades == bv.unidades_derivadas(bv.BASES_EXPERIMENTO_MAIOR["validacao"], ADENDO["K_por_base"])
    assert (VALIDACAO["delta"], VALIDACAO["delta_p3"], VALIDACAO["delta_n6"], VALIDACAO["delta_n7"]) == \
        (ADENDO["delta"], ADENDO["delta_p3_consumos"], ADENDO["delta_n6"], ADENDO["delta_n7"])
    escolha = json.loads((RAIZ / "artifacts_v2_calibracao_conjunta/escolha.json").read_text(encoding="utf-8"))["ponto"]
    assert VALIDACAO["lobos"] == {"memoria_ganho": escolha["g"], "w0_pedido": escolha["w0_pedido"], "w0_info": escolha["w0_info"]}
    assert VALIDACAO["consequencia"]["ganho"] == escolha["ganho"] and VALIDACAO["consequencia"]["canais_ligados"] is True
    assert VALIDACAO["ponto"] == "T3" and VALIDACAO["blocos"] is True and VALIDACAO["dias"] == 14
    for k in ("delta_p3", "delta_n6", "delta_n7"):
        with pytest.raises(ValueError):
            em.modo_e_unidades({kk: v for kk, v in VALIDACAO.items() if kk != k})


def test_tamanho_com_o_delta_na_escala_da_medida():
    c = {"p1": {"valores": {"1": [0.1, 0.2, 0.0, 0.15]}}, "p3_consumos": {"valores": {"1": [10.0, 40.0, -5.0, 20.0]}}}
    um = em.tamanhos(c, 0.2, 0.05, 0.8)
    dois = em.tamanhos(c, 0.2, 0.05, 0.8, {"p3_consumos": 17.5})
    assert um["por_contraste"]["p1"] == dois["por_contraste"]["p1"]
    assert dois["por_contraste"]["p3_consumos"]["delta"] == 17.5
    assert dois["por_contraste"]["p3_consumos"]["n"] < um["por_contraste"]["p3_consumos"]["n"]


def test_fumaca_com_os_blocos(tmp_path):
    cfg = {**FUMACA, "blocos": True, "delta_p3": 17.5, "delta_n6": 0.19, "delta_n7": 0.2, "dias": 4, "orcamento": 64,
           "unidades": {"bases": [101, 202], "k": 1}, "lobos": {"memoria_ganho": 512, "w0_info": 256, "w0_pedido": 256},
           "sonda": {"estados": 8, "amostras": 8, "semente": 101}, "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95}}
    r = em.rodar(cfg, tmp_path)
    v = r["resumo"]["vidas"]
    assert v["frutas"] + v["padrao"] + v["blocos"] == 44 * 2          # os 44 por unidade da secao 4
    b = json.loads((tmp_path / "blocos.json").read_text(encoding="utf-8"))
    assert set(b) == {"n6", "n7", "ablacoes", "n5_descritivo"}
    assert set(b["n6"]["contrastes"]) == {"G-CAUSAL", "G-REC", "G-EMB"} and set(b["n7"]["contrastes"]) == {"G-EROSAO", "G-MARCA", "G-MARCA-E"}
    assert b["n6"]["G-M1_G-M2"]["passa"] and b["n7"]["G-URG"]["passa"]
    assert set(b["ablacoes"]) == {"memoria_descasado", "memoria_mutavel", "canais_descasado", "canais_mutavel"}
    # toda vida dos blocos foi gravada e rejogada do disco (G1, pela bancada)
    for nome in em.BLOCOS:
        assert list((tmp_path / "blocos" / nome / "vidas").glob("*.jsonl"))
