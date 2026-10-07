"""Gabarito das vidas de hoje para o MUNDO FISICO (docs/TAREFA_V2_MUNDO_FISICO.md, secao 9, etapa 1; o G2 da secao 10): gravado com o
codigo da main ANTES de qualquer mudanca do mundo. Com a chave do mundo desligada, estas vidas tem de sair iguais depois, byte a byte:
P0, P1 e P3 nos mundos `padrao`, `bola`, `descasado` e `iguais_frutas`, pela bancada, na montagem simples (o ponto L1) e na completa (o
ponto T3 da K2, com o K4 e os canais), estado interno da politica incluido.

    python tests/gabarito_mundo.py      # grava tests/gabaritos/mundo_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "mundo_vidas_de_hoje.json"
SEMENTES = ((101, None), (202, 202))                 # so as dos testes; (semente, genoma)
MUNDOS = ("padrao", "bola", "descasado", "iguais_frutas")
BRACOS = ("P0", "P1", "P3")
DONOS = ("atencioso", "aleatorio")
LOBOS_K2 = {"w0_info": 256, "memoria_ganho": 512, "w0_pedido": 256}
BANCADAS = {
    "simples": bv.Bancada(4, 64),
    "completa": bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", LOBOS_K2), julgamento_fruta=True, montagem="completa",
                           cfg_consequencia=replace(CONFIG_CONSEQUENCIA, canais_ligados=True)),
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor, interacoes: int | None = None) -> dict:
    """O que tem de ficar igual: o log, o estado final, o estado() do motor, as acoes do pet, as rngs (as que o motor tem), o que o mundo
    registra (frutas, bola) e o estado interno da politica."""
    rngs = [motor._rng_politica.getstate(), motor._rng_ambiente.getstate()]
    for nome in ("_rng_fruta", "_rng_obediencia"):
        r = getattr(motor, nome, None)
        rngs.append(None if r is None else r.getstate())
    frutas = motor.resumo_frutas() if hasattr(motor, "resumo_frutas") else None
    bola = dict(motor.contagem_bola) if hasattr(motor, "contagem_bola") else None
    return {
        "motor": type(motor).__name__,
        "log": _sha(motor.log.para_jsonl()),
        "estado": _sha(repr(motor._estado)),
        "estado_motor": _sha(json.dumps(motor.estado(), sort_keys=True, default=repr)),
        "acoes": _sha(repr(motor.acoes_recentes(10**9))),
        "rngs": _sha(repr(rngs)),
        "mundo": _sha(json.dumps({"frutas": frutas, "bola": bola}, sort_keys=True, default=repr)),
        "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr)),
        "interacoes": interacoes,
    }


def casos():
    for nome_b in BANCADAS:
        for mundo in MUNDOS:
            for braco in BRACOS:
                for dono in DONOS:
                    for s, g in SEMENTES:
                        yield f"{nome_b}|{mundo}|{braco}|{dono}|{s}", (nome_b, bv.EspecVida(dono, braco, s, g, mundo))


def vida_de_hoje(nome_b: str, espec: bv.EspecVida) -> dict:
    v = BANCADAS[nome_b].vida(espec)
    return impressao(v.motor, v.interacoes)


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(g)} vidas -> {ARQUIVO}")
