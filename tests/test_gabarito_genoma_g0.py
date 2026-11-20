"""A E0 do G0 da genetica (docs/TAREFA_V3_GENOMA_G0.md, secao 3.2): o gabarito tests/gabaritos/genoma_g0_vidas_de_hoje.json se regera igual
duas vezes (determinismo do proprio gabarito) e esta em dia com o codigo, byte a byte. Cobre os tres caminhos que o G0 toca (o mundo com o
corpo e o cerebro A, o mundo com o modular REL da C4 e o mundo com o paladar ligado), com as sementes 101 a 505."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_genoma_g0 as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def duas_geracoes():
    return G.gerar(), G.gerar()


def test_o_gabarito_se_regera_igual_duas_vezes(duas_geracoes):
    primeira, segunda = duas_geracoes
    assert G.serializar(primeira) == G.serializar(segunda)


def test_o_gabarito_esta_em_dia_byte_a_byte(duas_geracoes):
    assert TEXTO == G.serializar(duas_geracoes[0])


def test_o_gabarito_cobre_os_tres_caminhos_com_as_cinco_sementes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == 40
    por_caminho = {}
    for chave in gravado:
        por_caminho.setdefault(chave.split("|")[0], []).append(chave)
    assert {c: len(v) for c, v in por_caminho.items()} == {"A": 20, "REL": 10, "PAL": 10}
    assert all({int(k.rsplit("|", 1)[1]) for k in v} == {101, 202, 303, 404, 505} for v in por_caminho.values())


def test_cada_vida_tem_log_trajetoria_e_as_tres_partes():
    for chave, v in json.loads(TEXTO).items():
        assert set(v) == {"log", "trajetoria", "partes", "passos"}, chave
        assert set(v["partes"]) == {"decisoes", "estados", "resumo"}, chave
        assert v["passos"] > 0 and len(v["log"]) == len(v["trajetoria"]) == 64, chave
