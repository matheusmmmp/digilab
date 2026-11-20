"""O gabarito do carater dos pets v11 para a web (experiments/exportar_gabarito_carater_v11.py -> web/app/test/gabaritos/carater_v11_python.json)
esta em dia, e e o do v11: as constantes da calibracao, as sondas com o corpo e as quatro vidas do gabarito dos lobos."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_carater_v11 as eg  # noqa: E402

pytestmark = pytest.mark.skipif(sys.version_info < (3, 12), reason="o gabarito usa o sum() compensado do Python 3.12+")


def test_gabarito_em_dia():
    gravado = json.loads(eg.ARQUIVO.read_text(encoding="utf-8"))
    assert json.loads(json.dumps(eg.gerar(), sort_keys=True)) == gravado


def test_gabarito_e_o_do_v11():
    g = json.loads(eg.ARQUIVO.read_text(encoding="utf-8"))
    cal = json.loads(eg.CALIBRACAO.read_text(encoding="utf-8"))
    assert (g["escala"], g["desloc"]) == (cal["escala_v11"], cal["desloc_v11"])
    assert len(g["sondas"]) == g["ccp"]["estados"] == 32
    assert all({"tedio", "solidao", "estresse", "dor", "susto"} <= set(s["corpo"]) for s in g["sondas"])
    assert [(v["dono"], v["semente"]) for v in g["vidas"]] == list(eg.eg.VIDAS_V11)
    assert all([m["quando"] for m in v["momentos"]] == ["adolescente", "adulto"] for v in g["vidas"])
