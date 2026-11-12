"""A chave desligada do sono que segura (docs/TAREFA_V3_SONO_SEGURA.md): o gabarito tests/gabaritos/sono_segura_de_hoje.json, gravado com o
codigo da main antes da `ConfigSonoSegura`, esta em dia com o Python byte a byte. Com a chave desligada (o padrao), as vidas dos quatro bracos
que leem o reflexo do sono (REL, M3+S, M3R e LAB+P) saem as de hoje: o log, o estado interno do cerebro e as medidas do orquestrador."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_sono_segura as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_os_quatro_bracos_do_reflexo():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.BRACOS) * len(G.SEMENTES) * len(G.DONOS) * len(G.LUGARES) == 64
    assert {k.split("|")[0] for k in gravado} == {"REL", "M3+S", "M3R", "LAB+P"}
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
