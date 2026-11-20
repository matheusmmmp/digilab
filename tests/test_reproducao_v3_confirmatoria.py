"""A V3 (educacao, braços fixos e personas da V3c) e a confirmatoria reproduzem os artefatos versionados.

DESIGN_VOZ_PROPRIA, parte 1: a mentira (ConfigMentira) entra desligada por padrao e nao pode mudar nenhuma
vida ja rodada. Este teste re-simula algumas vidas com o codigo atual e compara com `pets.json` dos artefatos
(discretos iguais; floats com erro relativo <= 1e-9, como o test_canonico_intacto fora do ambiente de origem).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_educacao  # noqa: E402
import run_poder  # noqa: E402

V3C = RAIZ / "artifacts_educacao_v3c"
CONF = RAIZ / "artifacts_confirmatoria"
DIAS = 14
# um de cada braco fixo em ovos diferentes, uma persona e um aleatorio (o braco que morre)
VIDAS_V3 = ("atencioso@70001", "permissivo@70002", "exigente@70003", "relapso@70004", "incoerente@70005",
            "lutador@70006", "aleatorio@70007", "persona:arara@70008")
VIDAS_CONF = ("atencioso@60001", "exigente@60002", "aleatorio@60003")


def _igual(a, b, caminho="") -> None:
    if isinstance(a, float) or isinstance(b, float):
        assert isinstance(a, (int, float)) and isinstance(b, (int, float)), caminho
        assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12), f"{caminho}: {a!r} != {b!r}"
    elif isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), f"{caminho}: chaves {sorted(set(a) ^ set(b))}"
        for k in a:
            _igual(a[k], b[k], f"{caminho}.{k}")
    elif isinstance(a, (list, tuple)):
        assert isinstance(b, (list, tuple)) and len(a) == len(b), caminho
        for i, (x, y) in enumerate(zip(a, b)):
            _igual(x, y, f"{caminho}[{i}]")
    else:
        assert a == b, f"{caminho}: {a!r} != {b!r}"


def _json(o):
    return json.loads(json.dumps(o, sort_keys=True, default=str))


@pytest.mark.parametrize("chave", VIDAS_V3)
def test_vida_v3c_reproduz(chave, tmp_path):
    ref = json.loads((V3C / "pets.json").read_text(encoding="utf-8"))[chave]
    cfg = json.loads((V3C / "meta.json").read_text(encoding="utf-8"))["config"]
    b, s = chave.rsplit("@", 1)
    _, _, dados, _ = run_educacao._vida((b, int(s), DIAS, str(tmp_path), cfg))
    _igual(_json(dados), ref, chave)


@pytest.mark.parametrize("chave", VIDAS_CONF)
def test_vida_confirmatoria_reproduz(chave, tmp_path):
    ref = json.loads((CONF / "pets.json").read_text(encoding="utf-8"))[chave]
    b, s = chave.rsplit("@", 1)
    _, _, _, dados, _ = run_poder._vida((b, int(s), DIAS, str(tmp_path)))
    _igual(_json(dados), ref, chave)
