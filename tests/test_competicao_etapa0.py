"""A etapa 0 da competicao entre as regras urgentes (docs/TAREFA_V2_V3_COMPETICAO.md, secao 4): o gabarito das vidas de hoje (G2), gravado
antes da medicao sombra."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_competicao as gc  # noqa: E402


def test_as_vidas_de_hoje_sao_as_do_gabarito():
    """G2: as 20 vidas do v11 do E0 (4 donos x as sementes dos testes, 14 dias) saem iguais ao gabarito gravado antes da etapa 0"""
    gravado = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))
    assert gc.gerar() == gravado
