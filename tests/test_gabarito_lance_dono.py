"""A chave desligada do lance do dono (docs/TAREFA_V3_BOLA_BRINCAR.md, BB-8): o gabarito tests/gabaritos/lance_dono_de_hoje.json, gravado com
o codigo da main antes da `ConfigLanceDono`, esta em dia com o Python byte a byte. Com a chave desligada (o padrao), as vidas que passam pelo
Brincar do dono com o mundo (o REL com e sem o sono que segura, o A11, o roteiro do dono que brinca e os dois grupos) saem as de hoje: o
log, o estado interno do cerebro, o resumo do mundo fisico e, no grupo, o resumo do grupo."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lance_dono as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_o_brincar_do_dono():
    gravado = json.loads(TEXTO)
    n_orq = len(G.SONOS) * len(G.SEMENTES_ORQ) * len(G.DONOS) * len(G.LUGARES) + len(G.DONOS)
    assert len(gravado) == n_orq + 3 * len(G.SEMENTES_ROTEIRO) + 2 == 47
    assert {k.split("|")[0] for k in gravado} == {"orq", "roteiro", "grupo"}
    assert all(v["decisoes"] == G.DIAS * 96 for k, v in gravado.items() if not k.startswith("grupo"))
