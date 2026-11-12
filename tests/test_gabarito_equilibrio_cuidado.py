"""A chave desligada das regras do E1 (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, EQ-7): o gabarito tests/gabaritos/equilibrio_cuidado_de_hoje.json,
gravado com o codigo de antes da `ConfigEquilibrioCuidado`, esta em dia com o Python byte a byte. Com a chave desligada (o padrao), as vidas do
REL (o de sempre, com o sono que segura, e com o sono e o lance: o cerebro dos ovos de hoje) saem as de hoje: o log, o estado interno do
cerebro, o resumo do mundo fisico e as decisoes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_equilibrio_cuidado as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_os_tres_cerebros():
    gravado = json.loads(TEXTO)
    n = len(G.CEREBROS) * (len(G.SEMENTES_ORQ) * len(G.DONOS) * len(G.LUGARES) + len(G.SEMENTES_ROTEIRO))
    assert len(gravado) == n == 33
    assert {k.split("|")[1] for k in gravado} == set(G.CEREBROS)
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
