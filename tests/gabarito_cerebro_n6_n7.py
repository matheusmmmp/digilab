"""Gabarito das vidas de hoje para o G2 da CEREBRO-N6-N7 (docs/TAREFA_V2_CEREBRO_N6_N7.md, secao 3): gravado com o codigo da main ANTES
da memoria (N6) e da arbitragem (N7). Com as chaves desligadas, toda vida daqui tem de sair igual, estado interno incluido.

    python tests/gabarito_cerebro_n6_n7.py      # grava tests/gabaritos/cerebro_n6_n7_vidas_de_hoje.json (so com o codigo de antes)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "cerebro_n6_n7_vidas_de_hoje.json"
DONOS = ("atencioso", "aleatorio")
SEMENTES = (101, 202)                    # so dos testes
MUNDOS_SIMPLES = ("padrao", "bola")
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel")
# duas bancadas: a de sempre (ponto L1) e o ponto T3 com a informacao ligada (w0_info S/2), para o caminho da entrada `info`
BANCADAS = {"L1": bv.Bancada(4, 64), "T3_info": bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", {"w0_info": 512}))}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor) -> dict:
    return {"resumo": _sha(json.dumps(bv.resumo_motor(motor), sort_keys=True, default=repr)),
            "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr))}


def casos():
    for nome_b, bancada in BANCADAS.items():
        for mundo in MUNDOS_SIMPLES + MUNDOS_FRUTAS:
            bracos = ("P0", "P1", "P2", "P2e", "P2a", "P3") if mundo in MUNDOS_FRUTAS else ("P0", "P1", "P3")
            for braco in bracos:
                for dono in DONOS:
                    for s in SEMENTES:
                        yield f"{nome_b}|{mundo}|{braco}|{dono}|{s}", bancada, bv.EspecVida(dono, braco, s, None, mundo)


def gerar() -> dict:
    return {chave: impressao(bancada.vida(espec).motor) for chave, bancada, espec in casos()}


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes")
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(len(g), "vidas")
