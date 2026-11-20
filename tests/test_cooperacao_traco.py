"""COOPERACAO, CO2a (docs/TAREFA_V3_COOPERACAO.md): o gabarito do traco do grupo de dois pets, gravado antes do porte para o TS.

Confere que o `experiments/exportar_gabarito_grupo_traco.py` refaz, com o codigo de hoje, o `web/app/test/gabaritos/grupo_traco_python.json.gz`
gravado, e que o motor que grava o traco nao muda a vida: o sha256 do resumo de cada vida e o do gabarito da CO1."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_grupo as eg  # noqa: E402
import exportar_gabarito_grupo_traco as et  # noqa: E402

GRAVADO = json.loads(gzip.decompress(et.ARQUIVO.read_bytes()).decode())
CO1 = json.loads(gzip.decompress(eg.ARQUIVO.read_bytes()).decode())


def test_o_motor_que_grava_nao_muda_a_vida():
    assert [v["semente"] for v in GRAVADO["vidas"]] == [v["semente"] for v in CO1["vidas"]]
    for t, r in zip(GRAVADO["vidas"], CO1["vidas"]):
        assert t["resumo_sha256"] == r["resumo_sha256"], t["semente"]


def test_o_traco_tem_a_percepcao_social_e_o_tick_social():
    for v in GRAVADO["vidas"]:
        assert set(v["tracos"]) == {"A", "B"}
        for ident, traco in v["tracos"].items():
            decisoes = [op for op in traco if op["op"] == "decisao"]
            assert len(decisoes) == v["n_decisoes"][ident] > 0
            assert all("social" in op and "tick_social" in op and "tick_mundo" in op for op in decisoes)
            assert any(op["social"] is not None for op in decisoes), (v["semente"], ident)


def test_o_codigo_de_hoje_refaz_o_traco_byte_a_byte():
    refeito = json.loads(json.dumps(et.gerar(), sort_keys=True, separators=(",", ":")))
    assert refeito == GRAVADO
