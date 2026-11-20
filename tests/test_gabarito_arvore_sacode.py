"""O gabarito das vidas de hoje antes do sacudir (docs/TAREFA_V3_ARVORE_SACODE.md, S1): com as chaves desligadas, as vidas do
tests/gabarito_arvore_sacode.py saem iguais ao tests/gabaritos/arvore_sacode_de_hoje.json, gravado antes da mudanca, inclusive as tres
que quebram no mundo com arvores (o A do v11 comendo a fruta do mundo, a AS-11)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_arvore_sacode as G  # noqa: E402

GRAVADO = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))


def test_as_vidas_de_hoje_saem_iguais():
    assert G.gerar() == GRAVADO


def test_o_gabarito_tem_as_quebras_da_as11():
    quebras = sorted(k for k, v in GRAVADO.items() if "erro" in v)
    assert quebras == ["ilha|a_v11|aleatorio|perto|202", "ilha|a_v11|aleatorio|perto|404", "ilha|a_v11|aleatorio|perto|505"]
    assert all("sub-decisao" in GRAVADO[k]["mensagem"] for k in quebras)
