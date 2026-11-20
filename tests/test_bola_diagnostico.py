"""BOLA_DIAGNOSTICO (o replay R-b): o contador da cadeia do brincar (`experiments/diagnosticar_v3_bola.py`), em vidas pequenas com as
sementes dos testes. So o contador: nenhuma mecanica muda."""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import diagnosticar_v3_bola as bd  # noqa: E402
from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.mundo import fabricas_mundo  # noqa: E402

CM = CONFIG_MUNDO_LIGADA


class _SoBrinca:
    """o cerebro de teste que so escolhe brincar (o alvo e o padrao do motor: a bola a vista)"""

    nome = "teste"

    def agir(self, obs, rng):
        return AcaoPet.BRINCAR

    def observar(self, *a, **kw):
        return None

    def estado_interno(self):
        return {}


def _vida(cm, semente: int, passos: int):
    _, fm = fabricas_mundo(cm)
    m = fm(_SoBrinca(), CONFIG_PADRAO, semente)
    for _ in range(passos):
        m._estado = replace(m._estado, energia=1.0)
        m.avancar(15)
    return m


@pytest.mark.parametrize("semente", (101, 202))
def test_a_bola_longe_o_brincar_nao_tem_alvo(semente):
    """o mapa de hoje: a bola a 36 celulas do ninho; o pet que so brinca nunca a ve, nunca tem alvo e nunca chuta"""
    m = _vida(CM, semente, 40)
    c = bd.cadeia_do_pet(m, m.mundo, {})
    assert c["brincar"] == c["decisoes"] > 0
    assert c["brincar_bola_no_raio"] == c["brincar_com_alvo"] == c["chutes"] == 0
    assert c["brincar_por_distancia"] == {"alem": c["brincar"]} and c["alvo_do_brincar"] == {"None": c["brincar"]}
    assert c["brincar_por_regiao"] == {"casa": c["brincar"]} and c["d_min_celulas"] == 36.0


@pytest.mark.parametrize("semente", (101, 202))
def test_a_bola_ao_lado_a_cadeia_fecha(semente):
    """a bola no ninho, onde o pet nasce: a cadeia inteira aparece, e cada elo contado e o do registro do motor"""
    cm = replace(CM, layout=replace(CM.layout, bola_inicio=CM.layout.ninho))
    m = _vida(cm, semente, 60)
    c = bd.cadeia_do_pet(m, m.mundo, {})
    assert c["chutes"] == len(m.rolagens) > 0
    assert c["brincar"] >= c["brincar_com_alvo"] >= c["chutes"]
    assert c["no_raio_sem_alvo"] == 0                       # a bola no raio da visao da sempre o alvo ao brincar
    assert c["brincar_bola_no_raio"] + c["fora_do_raio_com_alvo"] == c["brincar_com_alvo"]
    assert c["tentativa_sem_chute"] == c["brincar_com_alvo"] - c["chutes"]
    assert sum(c["brincar_por_distancia"].values()) == c["brincar"]


def test_somar_e_resumir():
    m = _vida(CM, 101, 10)
    linhas = [bd.cadeia_do_pet(m, m.mundo, {"fonte": "c3_vida", "vida": "x", "pet": "unico", "braco": "CTRL", "dono": d, "lugar": "comedouro"})
              for d in ("atencioso", "relapso")]
    r = bd.resumir(linhas)
    assert r["por_fonte"]["c3_vida"]["vidas_de_pet"] == 2 and r["por_fonte"]["c3_vida"]["brincar"] == 20
    assert set(r["c3_vida_por_dono"]) == {"atencioso", "relapso"} and r["c3_vida_por_dono"]["relapso"]["vidas_que_nunca_viram_a_bola"] == 1
