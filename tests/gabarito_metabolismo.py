"""Gabarito das vidas de hoje para o G2 do metabolismo (docs/TAREFA_V2_METABOLISMO.md, etapa 0 da secao 5), gravado com o codigo da main
ANTES de qualquer mudanca do metabolismo (origin/main b09793a: o corpo inteiro, o banheiro, os dois pets e a rede de si). Com a sub-chave
`metabolismo` desligada, estas vidas tem de sair iguais depois, byte a byte:
  - pela bancada, o bloco do corpo do plano (ME-6): P0-q, P1-q, P0-c, P1-c, P1-c-tapa e P1-cw nos mundos `padrao`, `bola` e
    `iguais_frutas`; no mundo `fisico`, o P1-quimica e o 2 x 2 do banheiro (P0-B00, P1-B0C, P0-BL0, P1-BLC);
  - direto, as vidas da etapa 6 do gabarito do banheiro (o instinto, o P1 e o P3 do cerebro A com o corpo inteiro e o DonoComGestos, nos
    mundos padrao, bola, frutas e fisico).
O log, o estado, o estado() do motor (a quimica do corpo inclusive), as acoes, as rngs, o registro do mundo e o estado interno da politica.

    python tests/gabarito_metabolismo.py      # grava tests/gabaritos/metabolismo_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_banheiro as gb  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "metabolismo_vidas_de_hoje.json"
DIAS = gb.DIAS
ORC = gb.ORC
SEMENTES = gb.SEMENTES                                  # so as dos testes
DONOS = gb.DONOS
BANCADA = bv.Bancada(DIAS, ORC)
BRACOS_CORPO = ("P0-q", "P1-q", "P0-c", "P1-c", "P1-c-tapa", "P1-cw")
MUNDOS_CORPO = ("padrao", "bola", "iguais_frutas")
FISICO = ("P1-quimica", "P0-B00", "P1-B0C", "P0-BL0", "P1-BLC")


def casos():
    for mundo in MUNDOS_CORPO:
        for braco in BRACOS_CORPO:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"bancada|{mundo}|{braco}|{dono}|{s}", ("bancada", bv.EspecVida(dono, braco, s, None, mundo))
    for braco in FISICO:
        for dono in DONOS:
            for s in SEMENTES:
                yield (f"bancada|fisico|{braco}|{dono}|perto|{s}",
                       ("bancada", bv.EspecVida(dono, braco, s, None, "fisico", "lobos", "perto")))
    for chave, caso in gb.casos():
        if caso[0] == "direto":
            yield chave, caso


def vida_de_hoje(tipo: str, arg) -> dict:
    if tipo == "bancada":
        v = BANCADA.vida(arg)
        return gb.impressao(v.motor, v.interacoes)
    v = gb._vida_direta(*arg)
    return gb.impressao(v.motor, v.interacoes)


def gerar() -> dict:
    # o 2 x 2 do banheiro com a area de antes da BN-8 (gravado com ela; tests/gabarito_banheiro_perto.py confere que so a area mudou)
    from gabarito_banheiro_perto import canto
    with canto():
        return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
