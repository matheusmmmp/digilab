"""C1, etapa 1 (docs/TAREFA_V2_LONGE_REGULAR.md, secao 7): os estilos `comedouro`, `perto` e `longe` do `DonoComLugar` saem byte a byte
como no gabarito gravado antes do `longe_fixo` (tests/gabaritos/lugar_estilos_antes.json). So as sementes dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lugar_estilos as gle  # noqa: E402

GABARITO = json.loads(gle.ARQUIVO.read_text(encoding="utf-8"))


def test_o_gabarito_cobre_os_tres_estilos():
    assert len(GABARITO) == len(list(gle.casos())) == 36
    assert {k.split("|")[1] for k in GABARITO} == {"comedouro", "perto", "longe"}
    assert all(r["n_lugares"] > 0 for r in GABARITO.values())


@pytest.mark.parametrize("chave", sorted(GABARITO))
def test_os_estilos_de_hoje_saem_byte_a_byte(chave):
    caso = dict(gle.casos())[chave]
    assert gle.registro(*caso) == GABARITO[chave], chave
