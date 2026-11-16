"""O gabarito antes da OV2 (GOSTO_VISUAL, o orgao da visao): tests/gabaritos/orgao_visao_vidas_de_hoje.json, gravado com o codigo de antes
num commit proprio, esta em dia com o Python byte a byte. Com a ConfigOrgao desligada (o padrao), a vida da GV3b e a imagem parada com o
enjoo saem as de hoje. Sementes: as dos testes (101, 202, 303) e as unidades derivadas delas."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_orgao_visao as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_as_familias():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.BASES) * 2 * 3 + len(G.SEMENTES_PARADA) == 15
    assert {k.split("|")[0] for k in gravado} == {"gv3b", "parada_enjoo"}
    assert all("sonda" in v for k, v in gravado.items() if k.startswith("gv3b"))
    assert sum(v["olhares"] for v in gravado.values()) > 0
