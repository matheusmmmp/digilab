"""Gabarito das vidas de hoje do MUNDO FISICO ligado, para o G2 do corpo no mundo (docs/TAREFA_V2_CORPO_DRIVES.md, secao 12; o MotorMundo
no MotorCorpo): gravado com o codigo da main ANTES de ligar o mundo no corpo (o snapshot de origin/main dc3ad90). Com o corpo desligado
na frente do MotorMundo, estas vidas tem de sair iguais depois, byte a byte: P0 (lobos e instinto), P0z, P1 e P3 nos mundos `fisico` e
`fisico_afastado`, pela bancada, nos tres lugares do dono, estado interno da politica e o registro do mundo incluidos.

    python tests/gabarito_corpo_mundo.py      # grava tests/gabaritos/corpo_mundo_vidas_de_hoje.json (so com o codigo de antes)
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
import gabarito_mundo as gm  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_mundo_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
MUNDOS = ("fisico", "fisico_afastado")
BRACOS = (("P0", "lobos"), ("P0", "instinto"), ("P0z", "lobos"), ("P1", "lobos"), ("P3", "lobos"))
DONOS = ("atencioso", "aleatorio")
LUGARES = ("comedouro", "perto", "longe")
BANCADAS = {"simples": bv.Bancada(DIAS, 16 * DIAS), "completa": bv.Bancada(DIAS, 16 * DIAS, montagem="completa")}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor, interacoes: int | None = None) -> dict:
    """a impressao do gabarito do mundo, mais o registro do mundo fisico inteiro (as rngs do mundo incluidas)"""
    d = gm.impressao(motor, interacoes)
    d["fisico"] = _sha(json.dumps(motor.resumo_mundo_fisico(), sort_keys=True, default=repr))
    return d


def casos():
    for nome_b in BANCADAS:
        for mundo in MUNDOS:
            for braco, cerebro in BRACOS:
                if nome_b == "completa" and (mundo != "fisico" or braco not in ("P1", "P3")):
                    continue
                for dono in DONOS:
                    for lugar in LUGARES:
                        for s in SEMENTES:
                            yield (f"{nome_b}|{mundo}|{braco}~{cerebro}|{dono}|{lugar}|{s}",
                                   (nome_b, bv.EspecVida(dono, braco, s, None, mundo, cerebro, lugar)))


def vida_de_hoje(nome_b: str, espec) -> dict:
    v = BANCADAS[nome_b].vida(espec)
    return impressao(v.motor, v.interacoes)


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
