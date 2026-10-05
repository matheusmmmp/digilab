"""Gabarito das vidas de hoje para a BANCADA-LIGA-N6-N7 (docs/TAREFA_V2_BANCADA_LIGA_N6_N7.md, secao 2): gravado com o codigo da main
ANTES de ligar a memoria e o pedido na bancada. Os bracos antigos (P0 a P3, P2e, P2a), nos mundos de sempre e no iguais_frutas, e os
acoplados tem de sair iguais depois, estado interno incluido.

    python tests/gabarito_bancada_liga.py      # grava tests/gabaritos/bancada_liga_vidas_de_hoje.json (so com o codigo de antes)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "bancada_liga_vidas_de_hoje.json"
DONOS = ("atencioso", "aleatorio")
SEMENTES = ((101, None), (202, 202))     # so dos testes
MUNDOS_SIMPLES = ("padrao", "bola")
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel", "iguais_frutas")
# a de sempre (ponto L1) e o T3 com a informacao e o pedido no cerebro (w0_info, w0_pedido S/2: nos bracos sem pedido nao age)
BANCADAS = {"L1": bv.Bancada(4, 64), "T3": bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", {"w0_info": 512}))}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(vida) -> dict:
    return {"resumo": _sha(json.dumps(bv.resumo_motor(vida.motor), sort_keys=True, default=repr)),
            "politica": _sha(json.dumps(vida.motor.politica.estado_interno(), sort_keys=True, default=repr)),
            "interacoes": vida.interacoes}


def casos():
    for nome_b, bancada in BANCADAS.items():
        for mundo in MUNDOS_SIMPLES + MUNDOS_FRUTAS:
            bracos = ("P0", "P1", "P2", "P2e", "P2a", "P3") if mundo in MUNDOS_FRUTAS else ("P0", "P1", "P3")
            for dono in DONOS:
                for s, g in SEMENTES:
                    for b in bracos:
                        v = bancada.vida(bv.EspecVida(dono, b, s, g, mundo))
                        yield f"{nome_b}|{v.nome}", v
                        if b in ("P2", "P3") and mundo != "bola":
                            a = bancada.acoplar(v, "P0", "sem_ensino" if mundo in MUNDOS_FRUTAS else "sem_sinais")
                            yield f"{nome_b}|{a.nome}", a


def gravar() -> None:
    dados = {nome: impressao(v) for nome, v in casos()}
    ARQUIVO.write_text(json.dumps(dados, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(dados)} vidas em {ARQUIVO}")


if __name__ == "__main__":
    gravar()
