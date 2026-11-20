"""Gabarito das vidas de hoje para a BANCADA-K4-CANAIS (docs/TAREFA_V2_BANCADA_K4_CANAIS.md, secao 2): gravado com o codigo da main
ANTES de ligar o K4, os canais por braco e as ablacoes na bancada. Os bracos de antes (P0 a P3, P2e, P2a, os do N6 e do N7) e os
acoplados tem de sair iguais depois, estado interno incluido; o P3 sem o julgamento e o P3 de hoje.

    python tests/gabarito_bancada_k4.py      # grava tests/gabaritos/bancada_k4_vidas_de_hoje.json (so com o codigo de antes)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "bancada_k4_vidas_de_hoje.json"
SEMENTES = ((101, None), (202, 202))     # so dos testes
FRUTAS_MUNDOS = ("casado_frutas", "descasado", "mutavel", "iguais_frutas")
ANTIGOS = ("P0", "P1", "P2", "P2e", "P2a", "P3")
# a de sempre (L1) e o T3 com as pecas dos planos na config (informacao, memoria e pedido S/2)
BANCADAS = {"L1": bv.Bancada(4, 64),
            "T3": bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", {"w0_info": 512, "memoria_ganho": 512, "w0_pedido": 512}))}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(vida) -> dict:
    return {"resumo": _sha(json.dumps(bv.resumo_motor(vida.motor), sort_keys=True, default=repr)),
            "politica": _sha(json.dumps(vida.motor.politica.estado_interno(), sort_keys=True, default=repr)),
            "interacoes": vida.interacoes}


def casos():
    for nome_b, bancada in BANCADAS.items():
        def vida(dono, b, s, g, mundo):
            return bancada.vida(bv.EspecVida(dono, b, s, g, mundo))
        for s, g in SEMENTES:
            for dono in ("atencioso", "aleatorio"):
                for mundo in FRUTAS_MUNDOS + ("padrao",):
                    for b in (ANTIGOS if mundo != "padrao" else ("P0", "P1", "P3")):
                        v = vida(dono, b, s, g, mundo)
                        yield f"{nome_b}|{v.nome}", v
                        if b in ("P2", "P3") and mundo != "padrao":
                            a = bancada.acoplar(v, "P0", "sem_ensino")
                            yield f"{nome_b}|{a.nome}", a
            for mundo in ("descasado", "mutavel"):
                for b in ("M0", "MR", "MT", "ME"):
                    v = vida("atencioso", b, s, g, mundo)
                    yield f"{nome_b}|{v.nome}", v
            for mundo in ("iguais_frutas", "descasado"):
                for b in ("P0+ped", "P1+ped", "P3+ped"):
                    v = vida("atencioso", b, s, g, mundo)
                    yield f"{nome_b}|{v.nome}", v
                    if b == "P3+ped":
                        for destino, filtro in (("P0", "sem_ensino"), ("P3+ped", "nenhum")):
                            a = bancada.acoplar(v, destino, filtro)
                            yield f"{nome_b}|{a.nome}", a


def gravar() -> None:
    dados = {nome: impressao(v) for nome, v in casos()}
    ARQUIVO.write_text(json.dumps(dados, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(dados)} vidas em {ARQUIVO}")


if __name__ == "__main__":
    gravar()
