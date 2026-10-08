"""G2 do banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 8): com a chave do banheiro desligada, as vidas de hoje saem byte a byte as de
`tests/gabaritos/banheiro_vidas_de_hoje.json`, gravado com o codigo da main antes de qualquer mudanca do banheiro
(`tests/gabarito_banheiro.py`, commit proprio)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_banheiro as gb  # noqa: E402

GABARITO = json.loads(gb.ARQUIVO.read_text(encoding="utf-8"))
CASOS = dict(gb.casos())


def test_gabarito_cobre_os_casos():
    assert set(GABARITO) == set(CASOS)
    assert len(GABARITO) == 176
    tipos = {k.split("|")[0] for k in GABARITO}
    assert tipos == {"bancada", "direto"}
    diretos = {tuple(k.split("|")[1:4]) for k in GABARITO if k.startswith("direto|")}
    assert {m for m, _, _ in diretos} == set(gb.DIRETOS) and {c for _, c, _ in diretos} == set(gb.CEREBROS)
    assert {s for k in GABARITO for s in [int(k.split("|")[-1])]} == set(gb.SEMENTES)


@pytest.mark.parametrize("chave", sorted(CASOS))
def test_vida_de_hoje_byte_a_byte(chave):
    assert gb.vida_de_hoje(*CASOS[chave]) == GABARITO[chave]
