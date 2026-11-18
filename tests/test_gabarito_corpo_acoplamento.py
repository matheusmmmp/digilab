"""A subchave da CORPO_ACOPLAMENTO desligada (docs/TAREFA_V3_CORPO_ACOPLAMENTO.md, etapa 2; D-CA-2 e D-CA-5): o gabarito
tests/gabaritos/corpo_acoplamento_de_hoje.json, gravado com o codigo de antes da `ConfigAcoplamentoCorpo`, esta em dia com o Python byte a
byte. Com a chave desligada (o padrao, ou passada explicita), as vidas da VALUATION saem as de hoje: o log, o estado interno do cerebro, o
resumo do mundo fisico, a serie do corpo e as decisoes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_corpo_acoplamento as G  # noqa: E402
from digilab.config import CONFIG_ACOPLAMENTO_CORPO  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == G.texto()


def test_a_chave_desligada_explicita_da_o_mesmo():
    assert TEXTO == G.texto(cfg_acoplamento=CONFIG_ACOPLAMENTO_CORPO)


def test_o_gabarito_cobre_as_vidas():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.SEMENTES) * len(G.DONOS) * len(G.LUGARES) == 8
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
