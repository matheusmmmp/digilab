"""A chave do conserto da VALUATION desligada (docs/PLANO_ANALISE_V3_VALUATION_CONSERTO.md, secao 3; D-VAL-16): o gabarito
tests/gabaritos/valuation_conserto_de_hoje.json, gravado com o codigo de antes de `guarda_fome_reflexo`, esta em dia com o Python byte a
byte. Com a chave desligada (o padrao), as vidas do REL e do M3 saem as de hoje: o log, o estado interno do cerebro, o resumo do mundo
fisico e as decisoes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_valuation_conserto as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_os_dois_cerebros():
    gravado = json.loads(TEXTO)
    n = len(G.CEREBROS) * len(G.SEMENTES) * len(G.DONOS) * len(G.LUGARES)
    assert len(gravado) == n == 16
    assert {k.split("|")[0] for k in gravado} == set(G.CEREBROS)
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
