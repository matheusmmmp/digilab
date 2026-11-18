"""Gabarito das vidas de hoje do DigiBrain modular antes da chave do conserto da VALUATION (docs/PLANO_ANALISE_V3_VALUATION_CONSERTO.md,
secao 3; D-VAL-16: `guarda_fome_reflexo`; a regra da chave desligada). Gravado com o codigo do branch `v3-valuation-v3` ANTES da chave,
num commit proprio. Com a chave desligada (o padrao), estas vidas tem de sair iguais, byte a byte.

A chave mexe no reflexo do sono do M-ARB e no que o M-ADAPT passa a ele. As vidas sao as do gabarito da V2 (o REL da C4 e da A1 e o M3
do conserto), pelo orquestrador do prototipo: os quatro donos, o `longe_fixo` e o comedouro, a semente 101, 3 dias.

    python tests/gabarito_valuation_conserto.py     # grava tests/gabaritos/valuation_conserto_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lance_dono as L  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "valuation_conserto_de_hoje.json"
DIAS = L.DIAS
SEMENTES = (101,)
LUGARES = L.LUGARES
DONOS = orq.DONOS
CEREBROS = ("REL", "M3")


def gerar() -> dict:
    out = {}
    for braco in CEREBROS:
        for semente in SEMENTES:
            for dono in DONOS:
                for lugar in LUGARES:
                    motor, _, _ = orq.viver(braco, dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
                    out[f"{braco}|{dono}|{lugar}|{semente}"] = L.impressao(motor)
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
