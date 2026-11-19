"""O gabarito de paridade da ponte com teto (docs/PLANO_ANALISE_V3_CORPO_C3.md, secoes 2 e 7; D-C3-1 e D-C3-2), para o jogo web
reproduzir inteiro a inteiro (web/app/test/corpo_teto.test.ts). Num arquivo proprio: nenhum gabarito de hoje muda.

A D ligada (`ConfigAcoplamentoCorpo`) com cada teto (`ConfigTetoFomeCorpo`, o DTL no limiar da privacao e o DTB em C/2), nos mesmos corpos,
grades e operacoes do gabarito da D (experiments/exportar_gabarito_corpo_acoplamento.py): a grade de estados com cada operacao e uma
sequencia longa num corpo so, com o sha256 de q, da janela, do resto e das contas depois de cada operacao. Sobre o gabarito da D, o caso
entra com a fome sorteada em volta do teto e o combustivel abaixo da falta (onde o teto corta a ponte), e com o `ticks_teto`.

Uso: python experiments/exportar_gabarito_corpo_teto.py     # grava tests/gabaritos/corpo_teto_python.json
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_corpo as gab  # noqa: E402
import exportar_gabarito_corpo_acoplamento as gd  # noqa: E402
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_PADRAO, CONFIG_TETO_FOME_BAIXO,  # noqa: E402
                            CONFIG_TETO_FOME_LIMIAR)
from digilab.corpo import Corpo, quimicos_de  # noqa: E402
from digilab.state import Estado  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_teto_python.json"
SEMENTE_CASOS = 20261120                 # so para sortear as grades e as sequencias do gabarito (nao e semente de vida)
CA = CONFIG_ACOPLAMENTO_CORPO_LIGADA
TETOS = {"DTL": CONFIG_TETO_FOME_LIMIAR, "DTB": CONFIG_TETO_FOME_BAIXO}


def secao(cc, com_mundo: bool, receptores: tuple, ct, rng: random.Random) -> dict:
    casos = []
    nomes = list(quimicos_de(cc, com_mundo))
    for q, janela, resto in gd._estados(rng, cc, com_mundo):
        q = list(q)
        if rng.random() < 0.6:                      # em volta do teto e com a falta: onde o teto corta a ponte
            q[nomes.index("fome")] = max(0, min(cc.escala, ct.teto + rng.randrange(-1_500, 1_500)))
            q[nomes.index("combustivel")] = rng.randrange(0, cc.falta_limiar)
        for op in gd._ops(com_mundo):
            c = Corpo(dict(zip(nomes, q)), CONFIG_PADRAO, cc, com_mundo=com_mundo, cfg_acoplamento=CA, cfg_teto_fome=ct)
            c.janela_tedio = list(janela)
            c.resto_combustivel = resto
            gab._aplicar_e6(c, op)
            rec = c.receptores()
            casos.append({"q": q, "janela": janela, "resto": resto, "op": op, "q_depois": gab._q(c), "janela_depois": list(c.janela_tedio),
                          "resto_depois": c.resto_combustivel, "contas": dict(c.contas_metabolismo), "ticks_teto": c.ticks_teto,
                          "receptores": [rec[r] for r in receptores]})
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo, cfg_acoplamento=CA, cfg_teto_fome=ct)
    escolhas = [op for op in gd._ops(com_mundo) if op[0] != "passo"]
    ops, h, tick = [], hashlib.sha256(), 0
    for _ in range(3000):
        if rng.random() < 0.8:
            op = ["passo", int(rng.random() < 0.3), rng.randrange(3), tick]
            tick += 1
        else:
            op = rng.choice(escolhas)
        gab._aplicar_e6(c, op)
        ops.append(op)
        h.update(gd._marca(c))
    return {"config": asdict(cc), "com_mundo": com_mundo, "quimicos": nomes, "receptores": list(receptores), "teto": ct.teto,
            "casos": casos,
            "sequencia": {"ops": ops, "sha256": h.hexdigest(), "q_final": gab._q(c), "janela_final": list(c.janela_tedio),
                          "resto_final": c.resto_combustivel, "contas_final": dict(c.contas_metabolismo), "ticks_teto_final": c.ticks_teto,
                          "receptores_final": [c.receptores()[r] for r in receptores]}}


def gabarito() -> dict:
    rng = random.Random(SEMENTE_CASOS)
    corpos = {}
    for nome, (cc, mundo, rec) in gd._corpos().items():
        for braco, ct in TETOS.items():
            corpos[f"{braco}_{nome}"] = secao(cc, mundo, rec, ct, rng)
    return {"versao": 1, "acoplamento_d": asdict(CA), "tetos": {b: ct.teto for b, ct in TETOS.items()}, "corpos": corpos}


def texto() -> str:
    return json.dumps(gabarito(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    ARQUIVO.write_text(texto(), encoding="utf-8", newline="\n")
    print(f"gravado {ARQUIVO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
