"""GOSTO_VISUAL, a TV no jogo: o gabarito para a web (web/app/test/gabaritos/tv_jogo.json.gz, experiments/exportar_tv_jogo.py) e o que o
Python de hoje produz, igual em duas execucoes. O TS confere o mesmo arquivo em web/app/test/tv_jogo_paridade.test.ts. Sementes: as dos
testes."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_tv_jogo as T  # noqa: E402


@pytest.fixture(scope="module")
def texto() -> bytes:
    return T.texto()


def test_uma_execucao_nova_sai_igual_ao_gravado(texto):
    assert texto == gzip.decompress(T.ARQUIVO.read_bytes())


def test_duas_execucoes_saem_iguais(texto):
    assert T.texto() == texto


def test_as_vidas_tem_o_ir_ate_a_tv_o_olhar_e_a_tv_desligada(texto):
    g = json.loads(texto)
    assert len(g["vidas"]) == 3 and all(len(v["decisoes"]) == 288 and v["ir_tv"] > 0 and v["olhares"] > 0 for v in g["vidas"])
    assert all(sum(e["valor"] == "tv|desligada" for e in v["log"]) == T.DIAS for v in g["vidas"])
    assert len(g["grupos"]) == 2
    for vg in g["grupos"]:
        assert vg["cabecalho"]["tv"]["fonte"] == "evento"
        assert all("ir_tv" in p["acoes"] for p in vg["pets"].values())
