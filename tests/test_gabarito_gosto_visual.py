"""O gabarito antes do P1 do GOSTO_VISUAL (docs/ESPEC_GOSTO_VISUAL_P1.md, secao 8): tests/gabaritos/gosto_visual_vidas_de_hoje.json, gravado
com o codigo de antes do P1 num commit proprio, esta em dia com o Python byte a byte. Com todas as chaves do P1 desligadas (o padrao), as
vidas do modular (o LAB no comedouro) e do A com o corpo e o mundo fisico saem as de hoje. Sementes: 101 a 505."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_gosto_visual as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_as_duas_familias_e_as_cinco_sementes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.SEMENTES) * (4 + len(G.DONOS_A)) == 30
    assert {k.split("|")[0] for k in gravado} == {"modular", "A"}
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} == set(G.SEMENTES)
    assert all(v["decisoes"] == G.DIAS * 96 for k, v in gravado.items() if k.startswith("modular"))
