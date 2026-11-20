"""V2, CALIBRACAO-CEREBROS-B-C, o cerebro B (experiments/run_v2_calibracao_cerebro_b.py): as sementes que o orquestrador aceita, o teto de
vidas, as regras do adendo 1.1 em dados sinteticos e a fumaca de ponta a ponta (so as sementes dos testes)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_cerebro_b as cal  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v2_comparacao_cerebros/fumaca_B.json").read_text(encoding="utf-8"))
CALIB = json.loads((RAIZ / "experiments/configs/v2_comparacao_cerebros/calibracao_B.json").read_text(encoding="utf-8"))


def test_a_config_da_calibracao_e_a_do_adendo():
    modo, pares = cal.modo_e_pares(CALIB)
    assert modo == "calibracao" and len(pares) == 20
    assert {s for _, s, _ in pares} == {u["semente"] for u in bv.unidades_derivadas(bv.BASES_COMPARACAO["calibracao"], 4,
                                                                                     "comparacao-cerebros")}
    assert cal.vidas_planejadas(len(pares)) == 660 <= cal.TETO_VIDAS == 1260
    assert cal.GRADES == {"taxa_ator": (0.01, 0.03, 0.1), "taxa_critico": (0.01, 0.03, 0.1), "lambda_elegibilidade": (0.5, 0.8, 0.95),
                          "w0_info": (0.5, 1.0, 2.0)}
    assert cal.FIXOS_INICIAIS == {"taxa_critico": 0.03, "lambda_elegibilidade": 0.8, "w0_info": 0.0}


@pytest.mark.parametrize("troca", [
    {"unidades": {"bases": list(bv.BASES_COMPARACAO["validacao"]), "k": 4, "prefixo": "comparacao-cerebros"}},
    {"unidades": {"bases": [14101, 14202, 14303, 14404, 14505], "k": 4, "prefixo": "comparacao-cerebros"}},
    {"unidades": {"bases": list(bv.BASES_COMPARACAO["calibracao"]), "k": 5, "prefixo": "comparacao-cerebros"}},
    {"unidades": {"bases": list(bv.BASES_COMPARACAO["calibracao"]), "k": 4, "prefixo": "experimento-maior"}},
    {"plano": "docs/PLANO_CALIBRACAO_CONJUNTA_V2.md"},
    {"dias": 7},
    {"extra": 1},
])
def test_recusa_o_que_nao_e_o_adendo(troca):
    with pytest.raises((ValueError, bv.SementeSemPlano)):
        cal.modo_e_pares({**CALIB, **troca})


def test_fumaca_so_com_as_sementes_dos_testes():
    with pytest.raises(bv.SementeSemPlano):
        cal.modo_e_pares({**FUMACA, "sementes": [28101]})
    assert cal.modo_e_pares(FUMACA)[0] == "fumaca"


def test_regra_de_estabilidade():
    p = lambda lim, r: {"vidas_no_limite": lim, "razao_media": r}  # noqa: E731
    assert cal.regra_estabilidade({0.01: p(0, 1.5), 0.03: p(0, 1.2), 0.1: p(2, 1.0)}) | {} == {
        "escolhido": 0.03, "fechou": True, "regra": "nenhuma vida com logit no limite, menor razao da deriva; empate, o menor valor",
        "sem_limite": [0.01, 0.03]}
    assert cal.regra_estabilidade({0.01: p(0, 1.2), 0.03: p(0, 1.2)})["escolhido"] == 0.01          # empate: o menor valor
    r = cal.regra_estabilidade({0.01: p(3, 1.0), 0.03: p(1, 2.0), 0.1: p(1, 1.5)})                  # reserva
    assert r["escolhido"] == 0.1 and r["fechou"] is False
    assert cal.regra_estabilidade({0.01: p(0, None), 0.03: p(0, 3.0)})["escolhido"] == 0.03         # sem razao conta como infinita


def test_regra_de_manipulacao():
    i = lambda li: {"ic": {"ic_inferior": li}}  # noqa: E731
    assert cal.regra_manipulacao({0.5: i(0.05), 1.0: i(0.08), 2.0: i(0.3)})["escolhido"] == 1.0
    r = cal.regra_manipulacao({0.5: i(0.01), 1.0: i(0.06), 2.0: i(0.04)})
    assert r["escolhido"] == 1.0 and r["fechou"] is False
    assert cal.regra_manipulacao({0.5: i(None), 1.0: i(None), 2.0: i(None)})["escolhido"] == 0.5


def test_fracoes_por_unidade_juntam_as_condicoes():
    ms = [{"unidade": {"base": 1, "k": 0}, "a": 1, "b": 4}, {"unidade": {"base": 1, "k": 0}, "a": 1, "b": 6},
          {"unidade": {"base": 2, "k": 0}, "a": 0, "b": 0}]
    assert cal.por_unidade(ms, "a", "b") == [0.2, None]


def test_fumaca_de_ponta_a_ponta(tmp_path):
    """A fumaca roda as quatro etapas em cadeia e o piloto, com toda vida rejogada do disco (o Corredor confere), e grava o que o
    resultado le."""
    r = cal.rodar({**FUMACA, "saida": str(tmp_path / "fumaca")})
    assert set(r["etapas"]) == {"B-A", "B-B", "B-C", "B-D"}
    assert r["meta"]["vidas"] == cal.vidas_planejadas(2) == 66
    for e in ("B-A", "B-B", "B-C", "B-D"):
        assert (tmp_path / "fumaca" / e / "resultado.json").is_file()
    piloto = json.loads((tmp_path / "fumaca" / "piloto.json").read_text(encoding="utf-8"))
    assert set(piloto) >= {"deriva_dia14", "fracao_aprendido_decidiu", "nao_aprende", "motivos"}
    escolha = json.loads((tmp_path / "fumaca" / "escolha.json").read_text(encoding="utf-8"))
    assert escolha["ponto"]["taxa_ator"] in cal.GRADES["taxa_ator"] and escolha["ponto"]["w0_info"] in cal.GRADES["w0_info"]
    med = json.loads(next((tmp_path / "fumaca" / "pontos").glob("*/P1/medidas.json")).read_text(encoding="utf-8"))
    assert all(m["dias_deriva"] == [2, 4] and m["decisoes"] > 0 for m in med)
