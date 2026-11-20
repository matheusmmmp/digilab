"""Gabarito dos quatro estilos de hoje do `DonoComLugar` (`comedouro`, `perto`, `longe` e `longe_fixo`), gravado com o codigo da main ANTES
do estilo `longe_ancora` (LONGE_GEOMETRIA; docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, secoes 3.2 e 4). O estilo novo tem rng propria e nao
pode mudar nenhum sorteio dos outros quatro: estas vidas, rodadas depois, tem de sair iguais byte a byte (o log, o estado, as acoes, as rngs,
o estado da politica e os lugares onde cada racao caiu). Os casos sao os do gabarito da C1 (tests/gabarito_lugar_estilos.py), com o
`longe_fixo` a mais.

    python tests/gabarito_lugar_estilos_lg.py      # grava tests/gabaritos/lugar_estilos_antes_lg.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lugar_estilos as gle  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "lugar_estilos_antes_lg.json"
ESTILOS = ("comedouro", "perto", "longe", "longe_fixo")


def casos():
    for cerebro in gle.CEREBROS:
        for estilo in ESTILOS:
            for dono in gle.DONOS:
                for s in gle.SEMENTES:
                    yield f"{cerebro}|{estilo}|{dono}|{s}", (cerebro, estilo, dono, s)


def gerar() -> dict:
    return {chave: gle.registro(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} casos")
