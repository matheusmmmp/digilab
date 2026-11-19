"""O gabarito de paridade da CORPO_ACOPLAMENTO, a opcao D (docs/TAREFA_V3_CORPO_ACOPLAMENTO.md, etapa 2; D-CA-2, D-CA-5 e D-CA-7): o
corpo com a `ConfigAcoplamentoCorpo` ligada (a falta de combustivel sobe a fome, e nao o cansaco), para o web/app/motor/corpo.ts reproduzir
inteiro a inteiro (web/app/test/corpo_acoplamento.test.ts). Num arquivo proprio: o tests/gabaritos/corpo_quimica_python.json (a chave
desligada) nao muda.

Os corpos: o do ponto do v11 (o dos pets do jogo e das vidas da VALUATION), sem e com o mundo fisico, e o da etapa 6 com o metabolismo
(`CONFIG_CORPO_METABOLISMO`), com o mundo. De cada um: a tabela do grafo e o relato, uma grade de estados em volta dos limiares do
metabolismo com cada operacao (o estado, o resto, as contas e os receptores depois) e uma sequencia longa num corpo so, do nascimento, com o
sha256 de q, da janela, do resto e das contas depois de cada operacao. As grades e as operacoes sao as do exportador do corpo
(experiments/exportar_gabarito_corpo.py); a rng e propria.

Uso: python experiments/exportar_gabarito_corpo_acoplamento.py     # grava tests/gabaritos/corpo_acoplamento_python.json
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
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_CORPO_METABOLISMO,  # noqa: E402
                            CONFIG_PADRAO)
from digilab.corpo import Corpo, grafo_do_corpo, quimicos_de, taxas_de  # noqa: E402
from digilab.corpo_grafo import checar  # noqa: E402
from digilab.state import Estado  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_acoplamento_python.json"
SEMENTE_CASOS = 20261118                 # so para sortear a grade e a sequencia do gabarito (nao e semente de vida)
CA = CONFIG_ACOPLAMENTO_CORPO_LIGADA


def _corpos() -> dict[str, tuple]:
    """nome -> (a ConfigCorpo, com o mundo fisico, os receptores conferidos)"""
    v11, receptores = gab._v11()
    return {"v11": (v11, False, receptores), "v11_mundo": (v11, True, receptores),
            "etapa6_mundo": (CONFIG_CORPO_METABOLISMO, True, receptores)}


def _estados(rng: random.Random, cc, com_mundo: bool) -> list:
    return gab._estados_m(rng, cc) if com_mundo else gab._estados_v11(rng, cc)


def _ops(com_mundo: bool) -> list[list]:
    return gab._ops_m() if com_mundo else gab._ops_v11()


def _marca(c: Corpo) -> bytes:
    return json.dumps([gab._q(c), c.janela_tedio, c.resto_combustivel, c.contas_metabolismo], sort_keys=True,
                      separators=(",", ":")).encode()


def secao(cc, com_mundo: bool, receptores: tuple, rng: random.Random) -> dict:
    g = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), com_mundo, cfg_acoplamento=CA)
    casos = []
    for q, janela, resto in _estados(rng, cc, com_mundo):
        for op in _ops(com_mundo):
            c = Corpo(dict(zip(quimicos_de(cc, com_mundo), q)), CONFIG_PADRAO, cc, com_mundo=com_mundo, cfg_acoplamento=CA)
            c.janela_tedio = list(janela)
            c.resto_combustivel = resto
            gab._aplicar_e6(c, op)
            rec = c.receptores()
            casos.append({"q": q, "janela": janela, "resto": resto, "op": op, "q_depois": gab._q(c), "janela_depois": list(c.janela_tedio),
                          "resto_depois": c.resto_combustivel, "contas": dict(c.contas_metabolismo),
                          "receptores": [rec[r] for r in receptores]})
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo, cfg_acoplamento=CA)
    escolhas = [op for op in _ops(com_mundo) if op[0] != "passo"]
    ops, h, tick = [], hashlib.sha256(), 0
    for _ in range(3000):
        if rng.random() < 0.8:
            op = ["passo", int(rng.random() < 0.3), rng.randrange(3), tick]
            tick += 1
        else:
            op = rng.choice(escolhas)
        gab._aplicar_e6(c, op)
        ops.append(op)
        h.update(_marca(c))
    return {"config": asdict(cc), "com_mundo": com_mundo, "quimicos": list(quimicos_de(cc, com_mundo)), "receptores": list(receptores),
            "grafo": {"tabela": gab._tabela_m(g), "relato": checar(g)}, "casos": casos,
            "sequencia": {"ops": ops, "sha256": h.hexdigest(), "q_final": gab._q(c), "janela_final": list(c.janela_tedio),
                          "resto_final": c.resto_combustivel, "contas_final": dict(c.contas_metabolismo),
                          "receptores_final": [c.receptores()[r] for r in receptores]}}


def gabarito() -> dict:
    rng = random.Random(SEMENTE_CASOS)
    return {"versao": 1, "acoplamento": asdict(CA), "padrao": asdict(CONFIG_ACOPLAMENTO_CORPO),
            "corpos": {nome: secao(cc, mundo, rec, rng) for nome, (cc, mundo, rec) in _corpos().items()}}


def texto() -> str:
    return json.dumps(gabarito(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    ARQUIVO.write_text(texto(), encoding="utf-8", newline="\n")
    print(f"gravado {ARQUIVO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
