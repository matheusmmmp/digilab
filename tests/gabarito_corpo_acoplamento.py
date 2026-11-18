"""Gabarito das vidas de hoje antes da subchave da CORPO_ACOPLAMENTO (docs/TAREFA_V3_CORPO_ACOPLAMENTO.md, etapa 2; D-CA-2 e D-CA-5:
a falta de combustivel sobe a fome, e nao o cansaco, so com a chave ligada). Gravado com o codigo de ANTES da chave, num commit proprio.
Com a chave desligada (o padrao), estas vidas tem de sair iguais, byte a byte.

As vidas sao as da VALUATION (o `viver` da sonda, sem a instrumentacao: o MotorGravaCorpo, o cerebro do REL, o corpo do v11 com o
metabolismo), os quatro donos, o `longe_fixo` e o comedouro, a semente 101, 3 dias. De cada vida: o sha256 do log, o do estado interno
do cerebro, o do resumo do mundo fisico, o da serie do corpo (os cinco drives no comeco de cada tick) e o numero de decisoes.

    python tests/gabarito_corpo_acoplamento.py     # grava tests/gabaritos/corpo_acoplamento_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lance_dono as L  # noqa: E402
import sonda_v3_corpo_acoplamento as SA  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_acoplamento_de_hoje.json"
DIAS = L.DIAS
SEMENTES = (101,)
LUGARES = L.LUGARES
DONOS = L.DONOS
BRACO = "REL"


def impressao(motor) -> dict:
    serie = hashlib.sha256(json.dumps(motor.serie_corpo, separators=(",", ":")).encode()).hexdigest()
    return {**L.impressao(motor), "serie_corpo": serie}


def gerar(**kw) -> dict:
    """as vidas do gabarito; `kw` vai ao `viver` da sonda (o teste passa a chave desligada explicita)"""
    out = {}
    for semente in SEMENTES:
        for dono in DONOS:
            for lugar in LUGARES:
                motor, _, _ = SA.viver(BRACO, dono, lugar, semente, DIAS, instrumentar=False, **kw)
                out[f"{BRACO}|{dono}|{lugar}|{semente}"] = impressao(motor)
    return out


def texto(**kw) -> str:
    return json.dumps(gerar(**kw), sort_keys=True, indent=1) + "\n"


if __name__ == "__main__":
    ARQUIVO.write_text(texto(), encoding="utf-8", newline="\n")
    print(ARQUIVO)
