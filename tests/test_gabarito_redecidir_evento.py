"""O G2 da subchave `redecidir_evento` (docs/TAREFA_V3_REDECIDIR_EVENTO.md, secao 3.2): o gabarito tests/gabaritos/redecidir_evento_de_hoje.json,
gravado com o codigo da main antes da subchave, esta em dia com o Python byte a byte. Com ela desligada (o padrao), as vidas do M3* no
`longe_fixo` e no comedouro saem as de hoje: o log, o estado interno do cerebro e as medidas do orquestrador. O M2 nas mesmas celulas esta
no tests/test_gabarito_habito_intencao.py. Sementes: 101 a 505."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_redecidir_evento as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_o_m3_nas_duas_celulas_da_c3_com_as_cinco_sementes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.BRACOS) * len(G.SEMENTES) * len(G.DONOS) * len(G.LUGARES) == 40
    assert {k.split("|")[0] for k in gravado} == {"M3"} and {k.split("|")[2] for k in gravado} == {"longe_fixo", "comedouro"}
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} == {101, 202, 303, 404, 505}
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
