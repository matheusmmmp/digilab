"""LONGE_GEOMETRIA (docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, secao 4, item 1): os quatro estilos de hoje do `DonoComLugar` (`comedouro`,
`perto`, `longe` e `longe_fixo`) saem byte a byte como no gabarito gravado antes do `longe_ancora`
(tests/gabaritos/lugar_estilos_antes_lg.json). So as sementes dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lugar_estilos as gle  # noqa: E402
import gabarito_lugar_estilos_lg as glg  # noqa: E402

GABARITO = json.loads(glg.ARQUIVO.read_text(encoding="utf-8"))


def test_o_gabarito_cobre_os_quatro_estilos():
    assert len(GABARITO) == len(list(glg.casos())) == 48
    assert {k.split("|")[1] for k in GABARITO} == {"comedouro", "perto", "longe", "longe_fixo"}
    assert all(r["n_lugares"] > 0 for r in GABARITO.values())


@pytest.mark.parametrize("chave", sorted(GABARITO))
def test_os_estilos_de_hoje_saem_byte_a_byte(chave):
    caso = dict(glg.casos())[chave]
    assert gle.registro(*caso) == GABARITO[chave], chave
