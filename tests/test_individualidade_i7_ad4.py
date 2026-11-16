"""O adendo 4 do I7 da INDIVIDUALIDADE (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md, secao 18): o orquestrador
(experiments/run_v3_individualidade_i7_ad4.py): a trava, os momentos pelo humor em casos feitos a mao, o Delta_H e a leitura (18.4), a
leitura do passo igual ao replay do adendo 3, e os ramos de um pet de ponta a ponta com as conferencias G-AD4-0 a 5. Vidas so com as
sementes dos testes (101...505)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_individualidade_i7_ad3 as a3  # noqa: E402
import run_v3_individualidade_i7_ad4 as a4  # noqa: E402

CONFIG = RAIZ / "experiments/configs/v3_individualidade/individualidade_i7_ad4.json"
FUMACA = RAIZ / "experiments/configs/v3_individualidade/individualidade_i7_ad4_fumaca.json"


def _cfg(caminho=CONFIG) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


# ================================================================== a trava
def test_a_fumaca_passa_e_a_run_pede_o_adendo_e_o_registro():
    assert a4.modo_da_config(_cfg(FUMACA)) == "fumaca"
    texto = a4._plano()
    com = texto if a4.TITULO_REGISTRO in texto else texto + f"\n{a4.TITULO_REGISTRO}\n\no registro.\n"
    if a4.TITULO_REGISTRO not in texto:
        with pytest.raises(RuntimeError, match="registro do adendo 4"):
            a4.modo_da_config(_cfg())
    assert a4.modo_da_config(_cfg(), texto_plano=com) == a4.FASE
    with pytest.raises(RuntimeError, match="DECIDIDO"):
        a4.modo_da_config(_cfg(), texto_plano=com.replace(a4.MARCA_ADENDO, "**O adendo 4 (seção 18) está PROPOSTO"))
    errada = dict(_cfg(), unidades={**_cfg()["unidades"], "bases": [88101, 88202, 88303, 88404, 88505]})
    with pytest.raises(Exception, match="AD4-2"):
        a4.modo_da_config(errada, texto_plano=com)


def test_o_corte_e_o_da_secao_17():
    assert "o humor 0,5800" in a4._plano()
    assert a4.CORTE_HUMOR == 0.58


# ================================================================== os momentos (18.2)
def _leituras(humores: dict) -> dict:
    return {t: {"energia": 0.5, "fome": 0.5, "humor": h, "acao": "explorar"} for t, h in humores.items()}


def test_os_momentos_pelo_humor_a_mao():
    d = 1440                                                # o dia t = 2 cobre [1440, 2880)
    leit = _leituras({d: 0.7, d + 15: 0.6, d + 30: 0.5, d + 45: 0.4, d + 60: 0.9, 100: 0.1})
    dec = [{"tick": d + 1, "acao": "dormir"}, {"tick": d + 16, "acao": "explorar"}, {"tick": d + 47, "acao": "comer"},
           {"tick": d + 60, "acao": "explorar"}, {"tick": 101, "acao": "explorar"}]
    assert a4.passos_acordados(leit, dec, 2) == [d + 15, d + 45, d + 60]   # o passo d so tem o sono; o d + 30, nenhuma decisao
    assert a4.momentos_do_humor(leit, dec, 2) == (d + 45, d + 15)
    a4.conferir_momento(leit, dec, 2, d + 45, True)
    with pytest.raises(RuntimeError, match="G-AD4-5"):
        a4.conferir_momento(leit, dec, 2, d + 60, False)                # ja havia um passo acordado alto antes
    assert a4.momentos_do_humor(leit, dec, 3) == (None, None)


# ================================================================== o Delta_H e a leitura (18.4)
def _par(s, gb, ga):
    return {"semente": s, "grupo_b": gb, "grupo_a": ga}


def test_delta_e_leitura():
    ps = [_par(1, "afasta", "absorve"), _par(1, "absorve", "absorve"), _par(2, "afasta", "afasta"), _par(2, "misto", "afasta")]
    assert a4.delta(ps) == pytest.approx((2 - 1) / 3)
    assert a4.delta([_par(1, "misto", "afasta")]) is None
    assert a4.leitura([0.01, 0.2]) == "H-HUMOR"
    assert a4.leitura([-0.04, 0.03]) == "H-SINAL"
    assert a4.leitura([-0.2, -0.01]).startswith("o contrario")
    assert a4.leitura([-0.1, 0.1]) == "Delta_H nao se distingue nesta analise"
    ic = a4.bootstrap_delta([_par(s, "afasta", "absorve") for s in range(1, 6)], ("REL", "teste"), boot=200)
    assert ic == [1.0, 1.0]


# ================================================================== um pet de ponta a ponta
@pytest.fixture(scope="module")
def pet():
    return a4.tarefa_pet("REL", "relapso", {"semente": 101, "base": 101, "k": 0}, a4.DIAS, a4.ORCAMENTO_POR_DIA)


def test_um_pet_de_ponta_a_ponta(pet):
    assert pet["ramos"][0]["ramo"] == "G"
    ramos = {(r["ramo"], r["idade"]) for r in pet["ramos"]}
    assert {("N", None), ("G", None), ("R0", None)} <= ramos
    for t, ms in pet["momentos"].items():
        t = int(t)
        if ms["Rb"] is not None and ms["Ra"] is not None:
            assert ("Rb", t) in ramos and ("Ra", t) in ramos
        else:
            assert t in pet["sem_par_de_momentos"]
    for r in pet["ramos"]:
        if r["ramo"] in a4.RAMOS:
            h = r["leitura_no_momento"]["humor"]
            assert (h < a4.CORTE_HUMOR) == (r["ramo"] == "Rb")


def test_a_leitura_do_passo_e_a_do_replay(pet):
    """o estado lido no passo do dono e o do replay do adendo 3 no mesmo tick (o estado antes do tapa)"""
    import run_v2_memoria_autobio as ma
    motor, *_ = ma.viver("REL", "relapso", a4.LUGAR, 101, a4.DIAS, a4.ORCAMENTO_POR_DIA)
    texto = motor.log.para_jsonl()
    vistos = 0
    for r in pet["ramos"]:
        if r["ramo"] in a4.RAMOS and vistos < 3:
            e = a3.estado_no_momento("REL", "relapso", 101, texto, r["momento"])
            assert e == r["leitura_no_momento"]
            vistos += 1
    assert vistos > 0
