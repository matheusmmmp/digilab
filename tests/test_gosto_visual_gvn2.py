"""A GVN-2 do GOSTO_VISUAL (docs/PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md): o script artifacts_v3_gosto_visual/gvn2/leitura.py, rodado
sobre os vidas.tar.gz das duas runs gravadas, reproduz o leitura.json byte a byte, com a conferencia C0 passando. Nenhuma vida roda."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "artifacts_v3_gosto_visual" / "gvn2"


def test_o_script_reproduz_a_leitura_byte_a_byte():
    saida = PASTA / "leitura.json"
    antes = saida.read_bytes()
    try:
        r = subprocess.run([sys.executable, "-I", str(PASTA / "leitura.py"), str(RAIZ)], capture_output=True, timeout=600)
        assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
        assert saida.read_bytes() == antes
    finally:
        saida.write_bytes(antes)


def test_a_conferencia_c0_passou_nas_duas_runs():
    res = json.loads((PASTA / "leitura.json").read_text(encoding="utf-8"))
    for run in ("gv3", "gv3b"):
        c0 = res[run]["C0"]
        assert c0["ok"] is True and c0["vidas"] == 216 and c0["replicas_conferidas"] == 4536
        assert res[run]["M4"]["status"] == "nao_mensuravel"
