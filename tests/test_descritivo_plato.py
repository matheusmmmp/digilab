"""V2, DESCRITIVO-PLATO (docs/TAREFA_V2_DESCRITIVO_PLATO.md): o descritivo pos hoc do plato de ~1/3.

O que se confere, so com as sementes dos testes: a classe da fruta pelo efeito vigente (o mutavel troca no tick da troca); a leitura de uma
vida fecha as contas (consumos por classe, ofertas de uma fruta so, escolhas com varias e a ruim presente); os pesos no fim saem do A e do C
com as tres classes; a conferencia contra medidas gravadas passa com as medidas da propria vida e falha alto com uma medida mudada.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import cerebro_c_bancada as cbc  # noqa: E402
import descritivo_plato as dp  # noqa: E402
import run_v2_comparacao_cerebros as ac  # noqa: E402

CFG = {"dias": 4, "orcamento": 64}


@pytest.fixture(scope="module")
def bancada():
    return ac.bancada_da_config(CFG)


def test_classe():
    assert dp.classe(0.1) == "boa" and dp.classe(0.0) == "neutra" and dp.classe(-0.1) == "ruim"


@pytest.mark.parametrize("mundo", dp.MUNDOS)
@pytest.mark.parametrize("cerebro", ["lobos", cbc.CEREBRO_C])
def test_leitura_fecha_as_contas(bancada, mundo, cerebro):
    v = bancada.vida(bv.EspecVida("atencioso", "P1", 101, 202, mundo, cerebro))
    m = v.motor
    r = dp.ler_vida(m, bancada.dias)                         # confere a classe de cada consumo contra o efeito aplicado
    assert sum(r[j]["n_consumos"] for j in dp.JANELAS) == len(m.consumos)
    so = sum(r[j]["uma_so"][k]["n"] for j in dp.JANELAS for k in dp.CLASSES)
    assert so == sum(1 for o in m.ofertas if len(o["presentes"]) == 1)
    for j in dp.JANELAS:
        ev = r[j]["escolha_varias"]
        if ev["n"]:
            assert 0.0 <= ev["ruim"] <= 1.0 and 0.0 < ev["acaso"] <= 0.5 and 0.0 <= ev["herdado"] <= 1.0
    if mundo == "mutavel":
        assert m.troca is not None
        t = m.troca["tick"]
        assert dp.efeitos_no_tick(m, t - 1) == m.troca["efeito_antes"] and dp.efeitos_no_tick(m, t) == m.troca["efeito_depois"]
    p = dp.pesos_no_fim(m.politica, m)
    assert set(p) == set(dp.CLASSES)
    chaves = {"escolha", "comer_presenca"} if cerebro == "lobos" else {
        "escolha_apetitivo", "escolha_aversivo", "escolha_liquido", "comer_apetitivo", "comer_aversivo", "comer_liquido"}
    assert all(set(x) == chaves for x in p.values())


def test_p0_sem_peso_aprendido(bancada):
    v = bancada.vida(bv.EspecVida("atencioso", "P0", 101, 202, "descasado"))
    assert all(x == {"escolha": 0, "comer_presenca": 0} for x in dp.pesos_no_fim(v.motor.politica, v.motor).values())


def test_conferencia_passa_e_falha_alto(bancada):
    v = bancada.vida(bv.EspecVida("atencioso", "P2", 303, 404, "mutavel"))
    gravada = bancada.medir(v, {"estados": 4, "amostras": 5, "semente": 1})
    dp.conferir(bancada, v, gravada, "teste")
    mudada = copy.deepcopy(gravada)
    mudada["frutas"]["consumos"] += 1
    with pytest.raises(dp.Divergiu):
        dp.conferir(bancada, v, mudada, "teste")


def test_tabelas_com_ic(bancada):
    linhas = []
    for s, g in ((101, 202), (303, 404), (505, 101)):
        v = bancada.vida(bv.EspecVida("atencioso", "P1", s, g, "descasado"))
        linhas.append({"cerebro": "A", "braco": "P1", "mundo": "descasado", "unidade": s, "leitura": dp.ler_vida(v.motor, bancada.dias),
                       "pesos": dp.pesos_no_fim(v.motor.politica, v.motor)})
    t = dp.tabelas(linhas)["A/P1/descasado"]
    assert t["unidades"] == 3 and set(t["final"]["fracao"]) == set(dp.CLASSES)
    assert "ruim_menos_outras" in t["final"]["uma_so"] and "ruim_menos_acaso" in t["final"]["escolha_varias"]
    assert set(t["pesos_no_fim_ruim_menos_outras"]) == {"escolha", "comer_presenca"}
