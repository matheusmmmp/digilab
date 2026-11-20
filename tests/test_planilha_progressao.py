"""Planilha de progressao (TAREFA_PLANILHA_PROGRESSAO): gera do zero, duas vezes igual, toda entrada com fonte.

O gerador fica em tools/ (fora de digilab/) e usa openpyxl; sem openpyxl no ambiente, o teste pula.
"""
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("openpyxl")
pytest.importorskip("matplotlib")

RAIZ = Path(__file__).resolve().parents[1]


def test_planilha_regeneravel_e_com_fontes():
    r = subprocess.run([sys.executable, str(RAIZ / "tools" / "gerar_planilha_progressao.py"), "--verificar"],
                       cwd=RAIZ, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "duas geracoes identicas" in r.stdout

