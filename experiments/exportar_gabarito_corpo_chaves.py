"""O gabarito de paridade das chaves da ablacao do corpo (docs/PLANO_ANALISE_V3_CORPO.md, secoes 2 e 7; D-CO-1), para o jogo web
reproduzir inteiro a inteiro (web/app/test/corpo_chaves.test.ts). Num arquivo proprio: nenhum gabarito de hoje muda.

- **A opcao E** (`ConfigDigestaoCorpo.inteira`, a comida que sobra com a fome em 0 vira combustivel), sozinha e com a D
  (`ConfigAcoplamentoCorpo` ligada), nos mesmos corpos, grades e operacoes do gabarito da D (experiments/exportar_gabarito_corpo_acoplamento.py):
  a grade de estados com cada operacao e uma sequencia longa num corpo so, com o sha256 de q, da janela, do resto e das contas depois de cada
  operacao. Sobre o gabarito da D, o caso entra com a fome sorteada baixa tambem (o excedente so aparece com a fome em 0).
- **A opcao C5** (`ConfigConsertoValuation.reflexo_suave`, o reflexo do sono vira peso no dormir): o `Arbitragem.escolher` com unidades,
  `g_exp` e a energia sorteados em volta de `lambda_sono`, sem as sondas; o `u` do sorteio sai de uma lista gravada (o TS le a mesma).

Uso: python experiments/exportar_gabarito_corpo_chaves.py     # grava tests/gabaritos/corpo_chaves_python.json
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
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_DIGESTAO_CORPO_INTEIRA,  # noqa: E402
                            CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO, CONFIG_REFLEXO_SUAVE)
from digilab.corpo import Corpo, quimicos_de  # noqa: E402
from digilab.digibrain.arb import Arbitragem  # noqa: E402
from digilab.state import Estado  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_chaves_python.json"
SEMENTE_CASOS = 20261119                 # so para sortear as grades e as sequencias do gabarito (nao e semente de vida)
CD = CONFIG_DIGESTAO_CORPO_INTEIRA
ACOES = ("comer", "dormir", "brincar", "explorar", "ocioso", "ir_tv")


def secao_e(cc, com_mundo: bool, receptores: tuple, ca, rng: random.Random) -> dict:
    casos = []
    for q, janela, resto in gd._estados(rng, cc, com_mundo):
        nomes = list(quimicos_de(cc, com_mundo))
        q = list(q)
        if rng.random() < 0.5:                      # a fome baixa: o excedente da comida aparece
            q[nomes.index("fome")] = rng.choice((0, rng.randrange(0, 30_000)))
        for op in gd._ops(com_mundo):
            c = Corpo(dict(zip(nomes, q)), CONFIG_PADRAO, cc, com_mundo=com_mundo, cfg_acoplamento=ca, cfg_digestao=CD)
            c.janela_tedio = list(janela)
            c.resto_combustivel = resto
            gab._aplicar_e6(c, op)
            rec = c.receptores()
            casos.append({"q": q, "janela": janela, "resto": resto, "op": op, "q_depois": gab._q(c), "janela_depois": list(c.janela_tedio),
                          "resto_depois": c.resto_combustivel, "contas": dict(c.contas_metabolismo),
                          "descartado": c.descartado_total, "receptores": [rec[r] for r in receptores]})
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo, cfg_acoplamento=ca, cfg_digestao=CD)
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
    return {"config": asdict(cc), "com_mundo": com_mundo, "quimicos": list(quimicos_de(cc, com_mundo)), "receptores": list(receptores),
            "casos": casos,
            "sequencia": {"ops": ops, "sha256": h.hexdigest(), "q_final": gab._q(c), "janela_final": list(c.janela_tedio),
                          "resto_final": c.resto_combustivel, "contas_final": dict(c.contas_metabolismo),
                          "descartado_final": c.descartado_total, "receptores_final": [c.receptores()[r] for r in receptores]}}


class _U:
    """a rng do sorteio, com os u gravados (o TS le a mesma lista)"""

    def __init__(self, us: list[float]) -> None:
        self.us, self.i = us, 0

    def random(self) -> float:
        u = self.us[self.i]
        self.i += 1
        return u


def secao_c5(rng: random.Random) -> list[dict]:
    S, lam = CONFIG_DIGIBRAIN_INATOS.escala, CONFIG_DIGIBRAIN_INATOS.lambda_sono
    casos = []
    for _ in range(400):
        n = rng.randrange(2, len(ACOES) - 1)          # o dormir e o ocioso sempre (o ocioso e a escolha sem peso)
        acoes = ["dormir", "ocioso"] + rng.sample([a for a in ACOES if a not in ("dormir", "ocioso")], n)
        rng.shuffle(acoes)
        unidades = [{"acao": a, "a": rng.choice((0, rng.randrange(-200, S + 1))), "chave": [a, j]} for j, a in enumerate(acoes)]
        g_exp = rng.randrange(0, S + 1)
        energia = rng.choice((0, lam - 1, lam, lam + 1, rng.randrange(0, S + 1)))
        us = [rng.random()]
        arb = Arbitragem(conserto=CONFIG_REFLEXO_SUAVE)
        arb.sondas = {}
        sens = {"leitura": {"energia": energia}, "contexto": {"dormindo": 0}, "social": None}
        reflexo = arb.reflexo(sens)
        out = arb.escolher([dict(x, chave=tuple(x["chave"])) for x in unidades], {"g_exp": g_exp, "urgencias": {"fome": 0}}, sens,
                           _U(us), reflexo=reflexo)
        casos.append({"unidades": unidades, "g_exp": g_exp, "energia": energia, "us": us, "reflexo": reflexo, "indice": out["indice"],
                      "u": out["u"], "pesos": out["pesos"], "suaves": arb.suaves, "sorteios": arb.sorteios, "reflexos": arb.reflexos})
    return casos


def gabarito() -> dict:
    rng = random.Random(SEMENTE_CASOS)
    corpos = {}
    for nome, (cc, mundo, rec) in gd._corpos().items():
        corpos[f"E_{nome}"] = secao_e(cc, mundo, rec, CONFIG_ACOPLAMENTO_CORPO, rng)
        corpos[f"DE_{nome}"] = secao_e(cc, mundo, rec, CONFIG_ACOPLAMENTO_CORPO_LIGADA, rng)
    return {"versao": 1, "digestao": asdict(CD), "acoplamento_d": asdict(CONFIG_ACOPLAMENTO_CORPO_LIGADA), "corpos": corpos,
            "reflexo_suave": {"peso": CONFIG_REFLEXO_SUAVE.peso_reflexo_suave, "lambda_sono": CONFIG_DIGIBRAIN_INATOS.lambda_sono,
                              "casos": secao_c5(rng)}}


def texto() -> str:
    return json.dumps(gabarito(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    ARQUIVO.write_text(texto(), encoding="utf-8", newline="\n")
    print(f"gravado {ARQUIVO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
