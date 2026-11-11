"""COOPERACAO, CO1 (docs/TAREFA_V3_COOPERACAO.md, secoes 3 e 4): o gabarito do grupo de dois pets, gravado antes de qualquer mudanca.

Confere que o `experiments/exportar_gabarito_grupo.py` refaz, com o codigo de hoje, exatamente o `web/app/test/gabaritos/grupo_python.json.gz`
gravado no commit da CO1. Com ele fixo, a CO2 (o `motor/grupo.ts`) tem um alvo; e a CO3 (a ConfigCooperacao desligada) nao pode mudar
nenhum numero do grupo (o G-HOJE do Python para dois pets; o de um pet e o tests/gabaritos/dois_pets_vidas_de_hoje.json)."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_grupo as eg  # noqa: E402

GRAVADO = json.loads(gzip.decompress(eg.ARQUIVO.read_bytes()).decode())


def test_o_gabarito_tem_as_vidas_e_as_ordens_do_exportador():
    assert [v["semente"] for v in GRAVADO["vidas"]] == [v[0] for v in eg.VIDAS]
    assert len(GRAVADO["ordem"]) == 2 * len(eg.SEMENTES_ORDEM)
    for caso in GRAVADO["ordem"]:
        assert len(caso["ordens"]) == eg.SORTEIOS_ORDEM
        assert all(sorted(o) == caso["ids"] for o in caso["ordens"])
    for v in GRAVADO["vidas"]:
        assert v["dias"] == eg.DIAS
        assert v["registro"]["cabecalho"]["semente"] == v["semente"]
        assert set(v["resumo"]["pets"]) == {"A", "B"}
        assert v["n_ordens"] == len(v["resumo"]["ordens"]) > 0
    # o comedouro comum faz a disputa aparecer em pelo menos uma vida (a CO3 precisa dela)
    assert sum(v["n_disputas"] for v in GRAVADO["vidas"]) >= 1


def test_o_codigo_de_hoje_refaz_o_gabarito_byte_a_byte():
    refeito = json.loads(json.dumps(eg.gerar(), sort_keys=True, separators=(",", ":")))
    assert refeito == GRAVADO
