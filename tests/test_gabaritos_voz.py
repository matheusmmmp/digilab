"""O gabarito da voz propria para o jogo web (web/app/test/gabaritos/voz_python.json) esta em dia com o Python.
Se mudar historia.py ou a mentira, rode `python experiments/exportar_gabaritos_voz.py` e o teste do TS confere."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabaritos_voz as G  # noqa: E402


def test_gabarito_da_voz_em_dia():
    atual = json.loads(G.SAIDA.read_text(encoding="utf-8"))
    assert atual["mentira"] == json.loads(json.dumps(G.mentira()))
    assert atual["historia"] == json.loads(json.dumps(G.historia()))
