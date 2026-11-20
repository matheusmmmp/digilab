"""Gabarito das vidas com o metabolismo LIGADO, para o G2 do fator do gasto das atividades (o no `gasto_atividades` do #273; ME-3 e ME-7
da docs/TAREFA_V2_METABOLISMO.md), gravado com o codigo da main ANTES do fator (origin/main c62284d). Com o fator no padrao (1/1), estas
vidas tem de sair iguais depois, byte a byte:
  - pela bancada, o bloco do corpo com o metabolismo (A3.1): P0-q, P1-q, P0-c, P1-c, P1-c-tapa e P1-cw nos mundos `padrao`, `bola` e
    `iguais_frutas`;
  - direto, a etapa 6 com o metabolismo (`CONFIG_CORPO_METABOLISMO`) e o `DonoComGestos`: o instinto e o P1 do cerebro A nos mundos padrao,
    bola, frutas e fisico (o andar so existe la).
O log, o estado, o estado() do motor, as acoes, as rngs, o registro do mundo, o estado interno da politica e o corpo inteiro (q, o resto
da conversao e as contas do metabolismo).

    python tests/gabarito_metabolismo_ligado.py      # grava tests/gabaritos/metabolismo_ligado_vidas_de_hoje.json (so com o codigo de antes)
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

import bancada_v2 as bv  # noqa: E402
import gabarito_banheiro as gb  # noqa: E402
import test_metabolismo as tm  # noqa: E402
from digilab.config import CONFIG_CORPO_METABOLISMO  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "metabolismo_ligado_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
DONOS = ("atencioso", "aleatorio")
BANCADA = bv.Bancada(DIAS, 16 * DIAS)
BRACOS = ("P0-q", "P1-q", "P0-c", "P1-c", "P1-c-tapa", "P1-cw")
MUNDOS_BANCADA = ("padrao", "bola", "iguais_frutas")
MUNDOS_DIRETOS = ("padrao", "bola", "frutas", "fisico")
CEREBROS = ("instinto", "P1")


def impressao(motor, interacoes: int) -> dict:
    d = gb.impressao(motor, interacoes)
    d["corpo"] = hashlib.sha256(json.dumps(motor.corpo.para_dict(), sort_keys=True).encode()).hexdigest()
    return d


def casos():
    for mundo in MUNDOS_BANCADA:
        for braco in BRACOS:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"bancada|{mundo}|{braco}|{dono}|{s}", ("bancada", bv.EspecVida(dono, braco, s, None, mundo))
    for mundo in MUNDOS_DIRETOS:
        for cerebro in CEREBROS:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"direto|{mundo}|{cerebro}|{dono}|{s}", ("direto", (mundo, cerebro, dono, s))


def vida_de_hoje(tipo: str, arg) -> dict:
    if tipo == "bancada":
        v = BANCADA.vida(arg)
        assert v.motor.corpo.cc.metabolismo
        return impressao(v.motor, v.interacoes)
    mundo, cerebro, dono, s = arg
    v = tm._vida(mundo, cerebro, CONFIG_CORPO_METABOLISMO, dono, s, DIAS)
    return impressao(v.motor, v.interacoes)


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
