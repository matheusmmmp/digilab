"""Gabarito das vidas de hoje para o G-OBS da rede de si (docs/TAREFA_V2_REDE_DE_SI.md, etapa 0), gravado com o codigo da main ANTES da
rede (origin/main b25f6c2). Com a rede observando pelo embrulho (`PoliticaComRede`), estas vidas tem de sair iguais, byte a byte:
  - os bracos do plano que a bancada ja monta (`docs/PLANO_ANALISE_V2_REDE_DE_SI.md`, secao 3): o P1-c, o P0-c e o P1-c-tapa no mundo da
    bola, e o P1-c e o P1+ped (o pedido do N7, ainda sem o corpo: o P1+ped-c e da etapa 3, do D) no `iguais_frutas`;
  - nas montagens simples e completa (o ponto T3; o plano usa a completa);
  - os donos atencioso (o do plano) e aleatorio, nas sementes 101 e 202, 3 dias.
O log, o estado, o estado() do motor (a quimica do corpo inclusive), as acoes, as rngs, o registro do mundo e o estado interno do cerebro.

    python tests/gabarito_rede_de_si.py      # grava tests/gabaritos/rede_de_si_vidas_de_hoje.json (so com o codigo de antes)
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
import gabarito_mundo as gm  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "rede_de_si_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
DONOS = ("atencioso", "aleatorio")
BRACOS = (("bola", "P1-c"), ("bola", "P0-c"), ("bola", "P1-c-tapa"), ("iguais_frutas", "P1-c"), ("iguais_frutas", "P1+ped"))


def bancadas(classe=bv.Bancada) -> dict:
    """as duas montagens; `classe` deixa o teste do G-OBS trocar a bancada pela que embrulha a politica com a rede"""
    return {"simples": classe(DIAS, 16 * DIAS),
            "completa": classe(DIAS, 16 * DIAS, montagem="completa", cfg_lobos=bv.cfg_lobos_do_ponto("T3"))}


def casos():
    for montagem in ("simples", "completa"):
        for mundo, braco in BRACOS:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"{montagem}|{mundo}|{braco}|{dono}|{s}", (montagem, bv.EspecVida(dono, braco, s, None, mundo))


def vida_de_hoje(bancada, espec) -> dict:
    v = bancada.vida(espec)
    return gm.impressao(v.motor, v.interacoes)


def gerar() -> dict:
    b = bancadas()
    return {chave: vida_de_hoje(b[montagem], espec) for chave, (montagem, espec) in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
