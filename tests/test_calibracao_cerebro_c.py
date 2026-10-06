"""V2, CALIBRACAO-CEREBRO-C: o orquestrador da calibracao do cerebro C (experiments/run_v2_calibracao_cerebro_c.py). As regras do adendo 1.2
em pontos sinteticos com resposta conhecida, as recusas (sementes, grades, teto de vidas) e a fumaca de ponta a ponta nas sementes dos
testes (toda vida gravada e rejogada do disco pela bancada)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_cerebro_c as rc  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v2_calibracao_cerebro_c/fumaca.json").read_text(encoding="utf-8"))
CALIBRACAO = json.loads((RAIZ / "experiments/configs/v2_calibracao_cerebro_c/calibracao.json").read_text(encoding="utf-8"))


def _ponto(teto, razao):
    return {"vidas_no_teto": teto, "razao_media": razao}


def test_estabilidade_escolhe_a_menor_razao_entre_os_sem_teto():
    pontos = {32: _ponto(0, 1.6), 64: _ponto(0, 1.2), 128: _ponto(3, 1.0)}
    r = rc.regra_estabilidade(pontos)
    assert r["escolhido"] == 64 and r["fechou"] and r["sem_teto"] == [32, 64]


def test_estabilidade_empate_fica_com_o_menor_valor():
    r = rc.regra_estabilidade({1024: _ponto(0, 1.3), 4096: _ponto(0, 1.3), 16384: _ponto(0, 1.5)})
    assert r["escolhido"] == 1024 and r["fechou"]


def test_estabilidade_reserva_menos_vidas_no_teto_depois_razao():
    r = rc.regra_estabilidade({32: _ponto(5, 1.1), 64: _ponto(2, 1.9), 128: _ponto(2, 1.4)})
    assert r["escolhido"] == 128 and not r["fechou"] and r["regra"].startswith("reserva")
    # razao indefinida (deriva zero no dia 7) perde para qualquer razao
    r = rc.regra_estabilidade({32: _ponto(0, None), 64: _ponto(0, 3.0)})
    assert r["escolhido"] == 64


def _ic(inf, media):
    return {"ic": {"ic_inferior": inf, "media": media}}


def test_manipulacao_menor_valor_com_ic_inferior_acima_do_limiar():
    r = rc.regra_manipulacao({256: _ic(0.05, 0.10), 512: _ic(0.08, 0.15), 768: _ic(0.20, 0.30)}, 0.069)
    assert r["escolhido"] == 512 and r["fechou"] and r["passam"] == [512, 768]


def test_manipulacao_reserva_e_a_maior_fracao():
    r = rc.regra_manipulacao({256: _ic(0.01, 0.05), 512: _ic(0.02, 0.06), 768: _ic(0.03, 0.04)}, 0.069)
    assert r["escolhido"] == 512 and not r["fechou"]          # maior fracao, nao maior limite inferior
    r = rc.regra_manipulacao({256: _ic(None, None), 512: _ic(None, None)}, 0.069)
    assert r["escolhido"] == 256 and not r["fechou"]


def _m(semente, mundo, deriva, decisoes, aprendido):
    return {"mundo": mundo, "unidade": {"semente": semente}, "custo_da_plasticidade": {"deriva_por_dia": deriva},
            "cerebro_c": {"decisoes": decisoes, "aprendido_decidiu": aprendido, "decisoes_com_escolha": decisoes,
                          "aprendido_decidiu_com_escolha": aprendido, "pesos_no_teto": 0}}


BOOT = {"reamostragens": 500, "semente": 1, "nivel": 0.95}


def test_nao_aprende_pela_deriva_nula_e_pela_fracao():
    med = {f"{s}{c}": _m(s, c, [0.0, 0.0], 100, 0) for s in (1, 2, 3) for c in rc.CONDICOES}
    r = rc.nao_aprende(med, BOOT, 2)
    assert r["deriva_nula"] and r["muda_menos_de_1pct"] and r["nao_aprende"]
    med = {f"{s}{c}": _m(s, c, [0.01, 0.02 * s], 1000, 50 + s) for s in (1, 2, 3) for c in rc.CONDICOES}
    r = rc.nao_aprende(med, BOOT, 2)
    assert not r["deriva_nula"] and not r["muda_menos_de_1pct"] and not r["nao_aprende"]
    med = {f"{s}{c}": _m(s, c, [0.01, 0.02 * s], 1000, s) for s in (1, 2, 3) for c in rc.CONDICOES}
    r = rc.nao_aprende(med, BOOT, 2)
    assert r["muda_menos_de_1pct"] and r["nao_aprende"]       # aprende algo, mas muda menos de 1% das escolhas


def test_fracao_k3_por_unidade_soma_as_tres_condicoes():
    med = {}
    for s, (e, d) in {1: (10, 1), 2: (0, 0)}.items():
        for c in rc.CONDICOES:
            med[f"{s}{c}"] = {"mundo": c, "unidade": {"semente": s},
                              "cerebro_c": {"k3_elegiveis": e, "k3_decididas_pela_informacao": d}}
    assert rc.fracoes_k3(med) == [3 / 30, None]


def test_unidades_da_comparacao_seguem_a_regra_e3_com_o_prefixo():
    us = rc.unidades_comparacao(bv.BASES_COMPARACAO["calibracao"], 4)
    assert len(us) == 20
    assert us[5] == {"base": 28202, "k": 1, "semente": derivar_semente("comparacao-cerebros", 28202, 1),
                     "genoma": derivar_semente("comparacao-cerebros-genoma", 28202, 1)}
    vals = [u["semente"] for u in us] + [u["genoma"] for u in us]
    assert len(set(vals)) == 40 and not any(bv.na_faixa_reservada(v) for v in vals)
    # nao colide com as unidades da validacao da comparacao nem com as do experimento maior
    outros = [u[k] for u in rc.unidades_comparacao(bv.BASES_COMPARACAO["validacao"], 4) for k in ("semente", "genoma")]
    outros += [u[k] for f in ("calibracao", "validacao")
               for u in bv.unidades_derivadas(bv.BASES_EXPERIMENTO_MAIOR[f], 4) for k in ("semente", "genoma")]
    assert not set(vals) & set(outros)


def test_calibracao_aceita_so_as_bases_da_comparacao():
    modo, us = rc.modo_e_unidades(CALIBRACAO)
    assert modo == "calibracao" and len(us) == 20
    for bases in (bv.BASES_COMPARACAO["validacao"], bv.BASES_EXPERIMENTO_MAIOR["calibracao"], bv.BASES_EXPERIMENTO_MAIOR["validacao"],
                  bv.BASES_COMPARACAO["calibracao"][:4]):
        with pytest.raises(bv.SementeSemPlano):
            rc.modo_e_unidades({**CALIBRACAO, "unidades": {"bases": list(bases), "k": 4}})
    with pytest.raises(bv.SementeSemPlano):
        rc.modo_e_unidades({**FUMACA, "sementes": [29101]})
    with pytest.raises(bv.SementeSemPlano):
        rc.modo_e_unidades({k: v for k, v in CALIBRACAO.items() if k != "plano"})


def test_calibracao_recusa_outro_k_dias_ou_grade():
    with pytest.raises(ValueError):
        rc.modo_e_unidades({**CALIBRACAO, "unidades": {"bases": list(bv.BASES_COMPARACAO["calibracao"]), "k": 2}})
    with pytest.raises(ValueError):
        rc.modo_e_unidades({**CALIBRACAO, "dias": 7})
    with pytest.raises(ValueError):
        rc.modo_e_unidades({**CALIBRACAO, "grades": {"passo": [32, 64, 128]}})
    with pytest.raises(ValueError):
        rc.modo_e_unidades({**CALIBRACAO, "outra": 1})


def test_grade_do_adendo_cabe_no_teto_e_a_maior_falha_antes_de_rodar(tmp_path):
    plan = rc.vidas_planejadas(rc.GRADES_ADENDO, 20)
    assert plan == {"C-A": 180, "C-B": 120, "C-C": 240, "total": 540} and plan["total"] <= rc.TETO_VIDAS
    with pytest.raises(rc.GradeAcimaDoTeto):
        rc.rodar(FUMACA, tmp_path, teto_vidas=29)          # a fumaca pede 30 vidas
    assert not any(tmp_path.iterdir())                      # nada rodou


def test_fumaca_de_ponta_a_ponta(tmp_path):
    r = rc.rodar(FUMACA, tmp_path)
    assert r["vidas"] == r["vidas_planejadas"]["total"] == 30
    assert r["ponto"]["ganho"] == rc.ganho_da_k2() == 4
    esc = json.loads((tmp_path / "escolha.json").read_text(encoding="utf-8"))
    assert esc["ponto"] == r["ponto"]
    b = json.loads((tmp_path / "C-B" / "resultado.json").read_text(encoding="utf-8"))
    assert b["pontos"]["4096"]["reusado_de"] == f"C-A/passo{r['ponto']['passo']}"
    c = json.loads((tmp_path / "C-C" / "resultado.json").read_text(encoding="utf-8"))
    assert set(c["pontos"]) == {"512"} and c["referencia_w0_info_0_descritiva"]["ponto"]["w0_info"] == 0
    # toda vida gravada no disco (a bancada as rejogou dali bit a bit)
    assert len(list(tmp_path.glob("**/vidas/*.jsonl"))) == 30
    piloto = json.loads((tmp_path / "piloto.json").read_text(encoding="utf-8"))
    assert piloto["unidades"] == 2 and "nao_aprende" in piloto
