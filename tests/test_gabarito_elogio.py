"""O gabarito do ELOGIO (tests/gabarito_elogio.py): com a ConfigElogio desligada (o padrao), as vidas do modular com o carinho pelo
corpo saem iguais as de antes do gancho, byte a byte (docs/TAREFA_V3_ELOGIO.md, secao 3)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_elogio as ge  # noqa: E402


def test_o_gabarito_do_elogio_sai_igual_byte_a_byte():
    gravado = json.loads(ge.ARQUIVO.read_text(encoding="utf-8"))
    assert ge.gerar() == gravado


def test_a_cobertura_do_gabarito():
    gravado = json.loads(ge.ARQUIVO.read_text(encoding="utf-8"))
    assert len(gravado) == len(ge.MUNDOS) * len(ge.CARINHOS) * len(ge.SEMENTES) == 12
    assert all(int(k.rsplit("|", 1)[1]) in (101, 202) for k in gravado)
    # o carinho chegou de verdade nas vidas com carinho, e as do casado comeram fruta
    assert all(v["carinhos"] > 0 for k, v in gravado.items() if "|cada4|" in k)
    assert all(v["frutas"] > 0 for k, v in gravado.items() if k.startswith("casado|"))
