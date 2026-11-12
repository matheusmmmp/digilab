"""Gabarito das vidas de hoje do DigiBrain modular antes das regras do E1 da rodada de equilibrio do cuidado
(docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, EQ-7; a regra da chave desligada). Gravado com o codigo do branch `v3-equilibrio-e1` ANTES da
`ConfigEquilibrioCuidado`, num commit proprio. Com a chave desligada (o padrao), estas vidas tem de sair iguais, byte a byte.

As duas regras do E1 mexem no M-ARB (a guarda da fome urgente no brincar: os pesos do brincar) e no M-IMPULSO (o bebe come com a fome dele:
o inato do comer). Por isso as vidas sao as do cerebro dos ovos de hoje do jogo (o REL com o sono que segura e o lance do dono, os v35 e v36)
e as de antes dele (o REL so com o sono que segura, e o REL de sempre):
  - pelo orquestrador do prototipo, os quatro donos, o `longe_fixo` e o comedouro, a semente 101, 3 dias;
  - pelo roteiro do dono que brinca (tests/gabarito_lance_dono.py: o Brincar a cada 2 h e a racao a cada 6 h), as sementes 101, 202 e 303.
De cada vida: o sha256 do log, o do estado interno do cerebro, o do resumo do mundo fisico e o numero de decisoes.

    python tests/gabarito_equilibrio_cuidado.py     # grava tests/gabaritos/equilibrio_cuidado_de_hoje.json (so com o codigo de antes)
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

from digilab.config import CONFIG_LANCE_DONO_LIGADA, CONFIG_SONO_SEGURA_LIGADA  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "equilibrio_cuidado_de_hoje.json"
DIAS = L.DIAS
SEMENTES_ORQ = (101,)
LUGARES = L.LUGARES
DONOS = orq.DONOS
SEMENTES_ROTEIRO = L.SEMENTES_ROTEIRO
# o cerebro: (o sono, o lance); o "+sono+lance" e o dos ovos de hoje do jogo
CEREBROS = {"REL": (None, None), "REL+sono": (CONFIG_SONO_SEGURA_LIGADA, None),
            "REL+sono+lance": (CONFIG_SONO_SEGURA_LIGADA, CONFIG_LANCE_DONO_LIGADA)}


def gerar() -> dict:
    out = {}
    for rotulo, (sono, lance) in CEREBROS.items():
        for semente in SEMENTES_ORQ:
            for dono in DONOS:
                for lugar in LUGARES:
                    motor, _, _ = orq.viver("REL", dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True, sono=sono, lance=lance)
                    out[f"orq|{rotulo}|{dono}|{lugar}|{semente}"] = L.impressao(motor)
        for semente in SEMENTES_ROTEIRO:
            fp, fm = orq.fabricas("REL", "atencioso", semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True, sono=sono, lance=lance)
            out[f"roteiro|{rotulo}|{semente}"] = L.impressao(L.roteiro(fp, fm, semente))
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
