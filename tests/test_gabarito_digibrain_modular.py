"""O G2 das subchaves `cheiro_inato` e `intencao_cheiro` (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 3, A3.7): o
gabarito tests/gabaritos/digibrain_modular_de_hoje.json, gravado antes das subchaves, esta em dia com o Python byte a byte. Com as duas
desligadas (o padrao), as vidas do cerebro modular saem as de hoje: o log, o estado interno do cerebro e as medidas do orquestrador.
Sementes: so as dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_digibrain_modular as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_do_modular_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_os_bracos_e_as_celulas_so_com_as_sementes_dos_testes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.BRACOS) * len(G.SEMENTES) * 12
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} <= set(bv.SEMENTES_TESTE)
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())
