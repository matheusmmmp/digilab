"""A exploracao descritiva do porque das GV3 negativas (docs/futuro/gosto_visual_porque_negativo.md, secao 3): o script
artifacts_v3_gosto_visual/porque/descritivo.py, rodado sobre os medidas.json das duas runs gravadas, reproduz o descritivo.json byte a
byte. Nenhuma vida roda."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "artifacts_v3_gosto_visual" / "porque"


def test_o_script_reproduz_o_descritivo_byte_a_byte():
    saida = PASTA / "descritivo.json"
    antes = saida.read_bytes()
    try:
        r = subprocess.run([sys.executable, "-I", str(PASTA / "descritivo.py"), str(RAIZ)], capture_output=True, timeout=600)
        assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
        assert saida.read_bytes() == antes
    finally:
        saida.write_bytes(antes)
