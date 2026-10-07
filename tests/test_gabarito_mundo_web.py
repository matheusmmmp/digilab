"""O gabarito do mundo fisico para o jogo web (web/app/test/gabaritos/mundo_python.json, etapa 5) esta em dia com o Python.
Se mudar digilab/mundo.py, a ConfigMundo ou os layouts, rode `python experiments/exportar_gabarito_mundo.py`, e o teste do TS
(web/app/test/mundo.test.ts) confere a paridade."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_mundo as G  # noqa: E402


def test_gabarito_do_mundo_em_dia():
    atual = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    assert atual == json.loads(json.dumps(G.gerar(), sort_keys=True))


def test_gabarito_cobre_o_g_par():
    """o G-PAR da secao 10: a grade de casos e pelo menos 3 vidas inteiras, com os sorteios das arvores e da bola e os dois gestos"""
    g = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    assert len(g["vidas"]) >= 3
    ops = [o["op"] for v in g["vidas"] for o in v["traco"]]
    assert "deixar_comida" in ops and "deixar_bola" in ops
    assert all(v["resumo"]["quedas"] for v in g["vidas"])
    assert any(v["resumo"]["rolagens"] for v in g["vidas"])
    assert all(len(g["grade"]["contas"][k]) >= 150 for k in ("distancia", "deslocar", "cheiro", "direcao"))
