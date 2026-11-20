"""O gabarito do contrato para o jogo web (web/app/test/gabaritos/contrato_python.json, a P4, etapa 2) esta em dia com o Python.
Se mudar digilab/contrato.py, o contrato no digilab/mundo.py ou a ConfigContrato, rode `python experiments/exportar_gabarito_contrato.py`,
e o teste do TS (web/app/test/contrato.test.ts, a G-PAR-CONTRATO) confere a paridade."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_contrato as G  # noqa: E402


def test_gabarito_do_contrato_em_dia():
    atual = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    assert atual == json.loads(json.dumps(G.gerar(), sort_keys=True))


def test_gabarito_cobre_a_g_par_contrato():
    """as chaves juntas e separadas, as paredes, o controlador chegando, parando pela hora e bloqueando, os contatos e o A* sem caminho"""
    g = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    assert len(g["vidas"]) == 7 and all(v["decisoes"] for v in g["vidas"])
    chaves = {(v["contrato"]["sensores"], v["contrato"]["controlador"], v["contrato"]["paredes"]) for v in g["vidas"]}
    assert chaves == {(True, True, False), (True, True, True), (True, False, False), (False, True, False)}
    andares = [c["andar"] for c in g["grade"]["controlar"]]
    assert {a["parou_por"] for a in andares} == {"chegou", "hora", "bloqueado"}
    assert sum(1 for a in andares if a["contatos"]) >= 10
    assert sum(1 for c in g["grade"]["caminho"] if c[-1] is None) >= 10
    regs = [r for v in g["vidas"] for r in v["resumo"].get("contrato_decisoes", [])]
    assert any(min(r["obstaculos"]) < 32 for r in regs)
