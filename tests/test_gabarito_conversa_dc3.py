"""O gabarito antes da DC3a (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, secoes 3.1 e 10): tests/gabaritos/conversa_dc3_de_hoje.json, gravado com o
codigo da main antes da subchave `fala_unidades` e do dono que atende, esta em dia com o Python byte a byte. Com a subchave desligada (o
padrao) e o dono de hoje (o que ignora), as vidas do LAB no comedouro saem as de hoje: o log, o estado interno do cerebro, as medidas do
orquestrador e as do corpo. Sementes: 101 a 505."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_conversa_dc3 as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_o_lab_no_comedouro_com_os_quatro_donos_e_as_cinco_sementes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.SEMENTES) * len(G.DONOS) == 20
    assert {k.split("|")[0] for k in gravado} == {"LAB"} and {k.split("|")[2] for k in gravado} == {"comedouro"}
    assert {k.split("|")[1] for k in gravado} == set(G.DONOS)
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} == {101, 202, 303, 404, 505}
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
