"""As chaves desligadas da TV no jogo (GOSTO_VISUAL, D-GV-TVJOGO): o gabarito tests/gabaritos/tv_jogo_vidas_de_hoje.json, gravado com o
codigo da main antes da etapa, esta em dia com o Python byte a byte. Com as chaves novas desligadas (o padrao), a TV de um pet so, o grupo
de dois pets e as listas que leem o `tuple(AcaoPet)` (a rede de si e a entrada social do A) saem as de hoje."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_tv_jogo as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_as_tres_familias():
    g = json.loads(TEXTO)
    assert sum(k.startswith("tv|") for k in g) == 4 and sum(k.startswith("grupo|") for k in g) == 3
    assert all(v["decisoes"] == 288 for k, v in g.items() if k.startswith("tv|"))
    assert len(g["rede_de_si"]["acoes"]) == 8 and len(g["rede_de_si"]["acoes_visiveis"]) == 8
