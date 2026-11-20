"""AN3 (docs/PLANO_ANALISE_V3_ACOES_NOVAS.md, secao 6): o artefato do poder da guarda G-COMEDOURO-AN sai igual, byte a byte, de uma
execucao nova do script, que so le os artefatos da C4 no git (nenhuma vida, nenhuma semente da faixa 78101...78505)."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import plano_an3_poder_acoes_novas as p  # noqa: E402


def test_o_artefato_gravado_e_o_de_uma_execucao_nova():
    novo = bv._dump(p.calcular(p.ler_medidas(), p.ler_meta()))
    gravado = p.SAIDA.read_bytes().decode("utf-8")
    assert novo == gravado


def test_a_margem_do_plano_e_a_do_artefato_com_k_200():
    import json
    d = json.loads(p.SAIDA.read_text(encoding="utf-8"))
    assert round(d["por_k"]["K=200"]["margem"], 3) == 0.018
    assert d["vidas_por_unidade_an4"] == 16
