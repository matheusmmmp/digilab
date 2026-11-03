"""O G2 da subchave `memoria_autobio` (docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secao 9): o gabarito
tests/gabaritos/memoria_autobio_de_hoje.json, gravado com o codigo da main antes da subchave, esta em dia com o Python byte a byte. Com ela
desligada (o padrao), as vidas do M3* no `longe_fixo`, no longe sorteado e no comedouro saem as de hoje: o log, o estado interno do cerebro
e as medidas do orquestrador. Sementes: 101 a 505."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_memoria_autobio as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_o_m3_nas_tres_celulas_da_espec_com_as_cinco_sementes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.BRACOS) * len(G.SEMENTES) * len(G.DONOS) * len(G.LUGARES) == 60
    assert {k.split("|")[0] for k in gravado} == {"M3"}
    assert {k.split("|")[2] for k in gravado} == {"longe_fixo", "longe", "comedouro"}
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} == {101, 202, 303, 404, 505}
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
