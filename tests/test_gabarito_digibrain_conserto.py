"""O G2 da subchave `intencao_suspensa` (docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secao 5; o T-L2-1): o gabarito
tests/gabaritos/digibrain_conserto_de_hoje.json, gravado com o codigo da main antes da subchave, esta em dia com o Python byte a byte. Com
ela desligada (o padrao), as vidas dos 11 bracos do modular do conserto saem as de hoje: o log, o estado interno do cerebro e as medidas
do orquestrador. Sementes: so as dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_digibrain_conserto as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_do_conserto_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_os_bracos_do_conserto_e_as_celulas_so_com_as_sementes_dos_testes():
    gravado = json.loads(TEXTO)
    assert {k.split("|")[0] for k in gravado} == set(G.BRACOS) and "M3" in G.BRACOS and "M0" in G.BRACOS
    assert len(gravado) == len(G.BRACOS) * len(G.SEMENTES) * 12
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} <= set(bv.SEMENTES_TESTE)
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
