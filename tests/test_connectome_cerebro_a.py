"""O protótipo do connectome do cérebro A (tools/connectome_cerebro_a.py; docs/futuro/connectome_cerebro_a.md), só nas sementes dos testes:
recusa a semente de pesquisa, gera o HTML de uma vida rejogada do disco e a contagem fecha com o cérebro."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))

import connectome_cerebro_a as cc  # noqa: E402


def test_recusa_semente_fora_dos_testes(tmp_path):
    for s in (45101, 49101, 7):
        with pytest.raises(ValueError):
            cc.principal(["--vida", "pqp", "--semente", str(s), "--saida", str(tmp_path / str(s))])


@pytest.mark.parametrize("vida", cc.VIDAS)
def test_gera_o_html_da_vida_rejogada(tmp_path, vida):
    dados = cc.principal(["--vida", vida, "--semente", "101", "--saida", str(tmp_path)])
    html = (tmp_path / "connectome.html").read_text(encoding="utf-8")
    assert "__DADOS__" not in html and cc.D3_CDN in html
    c = json.loads((tmp_path / "contagem.json").read_text(encoding="utf-8"))
    total = c["pesos_total"]
    assert total["pesos"] == c["n_pesos_do_cerebro"] == len(dados["arestas"])
    assert sum(t["pesos"] for t in c["pesos_por_tipo"].values()) == total["pesos"]
    assert total["nao_nulos_prior"] <= total["nao_nulos_na_vida"] and total["nao_nulos_fim"] <= total["nao_nulos_na_vida"]
    assert c["nos"] == len(dados["nos"]) == sum(c["nos_por_grupo"].values())
    assert c["decisoes"] == len(dados["decisoes"]) > 0
    # as decisões trazem as mudanças de peso em índices válidos
    assert all(0 <= i < len(dados["arestas"]) for d in dados["decisoes"] for i, _ in d["mud"])
    if vida == "dois_pets":
        assert c["nos_por_grupo"]["entrada:social"] > 0 and "s" in c["pesos_por_tipo"]
    else:
        assert "l:planejamento" in {n["id"] for n in dados["nos"]} and dados["meta"]["corpo"]["quimicos"] > 0
