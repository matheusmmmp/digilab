"""Gabarito das vidas de hoje do M3* (o M3 do conserto, com as duas subchaves do cheiro) no `longe_fixo` e no comedouro
(docs/TAREFA_V3_REDECIDIR_EVENTO.md, secao 3.2: "o gabarito antes"). Gravado com o codigo da main (22cc251) ANTES da subchave
`redecidir_evento`, num commit proprio. Com ela desligada, estas vidas tem de sair iguais, byte a byte.

Os gabaritos ja commitados cobrem o M2 nas duas celulas (tests/gabarito_habito_intencao.py, sementes 101 a 505) e o M3* no comedouro,
no perto e no longe sorteado com as sementes 101 e 202 (tests/gabarito_digibrain_conserto.py); nenhum cobre o M3* no `longe_fixo`. Este
cobre o M3* nas duas celulas da C3 (o `longe_fixo` e o comedouro), os quatro donos e as cinco sementes dos testes (101 a 505), pelo
orquestrador do prototipo com as medidas do conserto.

De cada vida: o sha256 do log (o JSONL do motor), o do estado interno do cerebro e o das medidas do orquestrador, e o numero de decisoes.

    python tests/gabarito_redecidir_evento.py     # grava tests/gabaritos/redecidir_evento_de_hoje.json (so com o codigo de antes da mudanca)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_habito_intencao as H  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "redecidir_evento_de_hoje.json"
SEMENTES = H.SEMENTES
DIAS = H.DIAS
BRACOS = ("M3",)
LUGARES = H.LUGARES
DONOS = orq.DONOS


def gerar() -> dict:
    out = {}
    for braco in BRACOS:
        for semente in SEMENTES:
            for dono in DONOS:
                for lugar in LUGARES:
                    motor, reg, _ = orq.viver(braco, dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
                    out[f"{braco}|{dono}|{lugar}|{semente}"] = H.impressao(motor, reg, braco)
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
