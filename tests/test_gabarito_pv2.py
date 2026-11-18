"""O gabarito do PV-2 (tests/gabarito_pv2.py): com a ConfigPV2 desligada (o padrao), as vidas do REL nos tres lugares da C4 saem iguais
as de antes da ConfigPV2, byte a byte (docs/futuro/integracao_cadeia_digibrain.md, secao 8.2)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_pv2 as gp  # noqa: E402


def test_o_gabarito_do_pv2_sai_igual_byte_a_byte():
    gravado = json.loads(gp.ARQUIVO.read_text(encoding="utf-8"))
    assert gp.gerar() == gravado


def test_a_cobertura_do_gabarito_do_pv2():
    gravado = json.loads(gp.ARQUIVO.read_text(encoding="utf-8"))
    assert len(gravado) == len(gp.LUGARES) * len(gp.SEMENTES) == 6
    assert all(int(k.rsplit("|", 1)[1]) in (101, 202) for k in gravado)
    # o cheiro decidiu de verdade nas vidas do `longe` (a busca pelo oraculo de hoje)
    assert all(v["decisoes_cheiro"] > 0 for k, v in gravado.items() if k.startswith("longe|"))
