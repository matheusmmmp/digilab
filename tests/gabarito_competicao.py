"""Gabarito das vidas de hoje para a etapa 0 da competicao entre as regras (docs/TAREFA_V2_V3_COMPETICAO.md, secoes 4 e 5): gravado com o
codigo da main ANTES da medicao sombra. A medicao embrulha o cerebro so para ler; toda vida daqui tem de sair igual com o embrulho, o
estado interno incluido (G2). As vidas sao as do E0: o A v11 (`experiments/exportar_gabarito_lobos.py`, `bancada_v11`), 4 donos x as
sementes dos testes, 14 dias.

    python tests/gabarito_competicao.py      # grava tests/gabaritos/competicao_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "competicao_vidas_de_hoje.json"
DIAS = 14
ORCAMENTO = 16 * DIAS
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = tuple(sorted(bv.SEMENTES_TESTE))     # so dos testes


def bancada():
    return gl.bancada_v11(DIAS, ORCAMENTO)


def espec(dono: str, semente: int):
    return bv.EspecVida(dono, gl.BRACO_V11, semente)


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor) -> dict:
    return {"log": _sha(motor.log.para_jsonl()),
            "resumo": _sha(json.dumps(bv.resumo_motor(motor), sort_keys=True, default=repr)),
            "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr))}


def casos():
    for dono in DONOS:
        for s in SEMENTES:
            yield f"v11|{dono}|{s}", dono, s


def gerar() -> dict:
    b = bancada()
    return {chave: impressao(b.vida(espec(dono, s)).motor) for chave, dono, s in casos()}


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes")
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(len(g), "vidas")
