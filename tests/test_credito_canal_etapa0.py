"""A etapa 0 do credito por canal (docs/TAREFA_V2_V3_CREDITO_CANAL.md, secao 5): o gabarito das vidas de hoje (G2), gravado antes da
medicao das tabelas sombra."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_credito_canal as gc  # noqa: E402


def test_as_vidas_de_hoje_sao_as_do_gabarito():
    """G2: as vidas do T1 do J5 (P1 e P1-plan, sementes dos testes) saem iguais ao gabarito gravado antes da etapa 0"""
    gravado = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))
    assert gc.gerar() == gravado
