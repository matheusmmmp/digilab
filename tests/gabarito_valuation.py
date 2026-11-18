"""Gabarito das vidas de hoje do DigiBrain modular antes das duas chaves de ablacao da VALUATION (docs/PLANO_ANALISE_V3_VALUATION.md,
secao 3; D-VAL-3: `ablacao_ve_z` e `ablacao_maior_peso`; a regra da chave desligada). Gravado com o codigo do branch `v3-valuation-v2`
ANTES das chaves, num commit proprio. Com as chaves desligadas (o padrao), estas vidas tem de sair iguais, byte a byte.

As chaves mexem no M-IMPULSO (o V e o E do z) e no M-ARB (o sorteio). As vidas sao as do REL da C4 e da A1 e as do M3 do conserto (o
modular sem a memoria autobiografica), pelo orquestrador do prototipo: os quatro donos, o `longe_fixo` e o comedouro, a semente 101, 3 dias.
De cada vida: o sha256 do log, o do estado interno do cerebro, o do resumo do mundo fisico e o numero de decisoes.

    python tests/gabarito_valuation.py     # grava tests/gabaritos/valuation_de_hoje.json (so com o codigo de antes)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "valuation_de_hoje.json"
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
