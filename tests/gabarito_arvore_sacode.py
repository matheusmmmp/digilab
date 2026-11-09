"""Gabarito das vidas de hoje antes do sacudir a arvore (docs/TAREFA_V3_ARVORE_SACODE.md, S1; secao 3.5: a vida de hoje byte a byte).
Gravado com o codigo da main (34458db8) ANTES da ConfigSacudir, do CONFIG_MUNDO_ILHA e da subchave do A "a fruta do mundo como comida"
(AS-11), num commit proprio. Com as chaves desligadas, estas vidas tem de sair iguais depois da mudanca, inclusive as que quebram.

As vidas sao as do gabarito do mundo do produto (experiments/exportar_gabarito_mvp_mundo.py, `vida`: o A do v11 com o corpo, ou o
instinto, com o dono e o lugar da comida), 3 dias, as sementes dos testes, em dois mundos:
- `mvp`: o CONFIG_MUNDO_MVP de hoje (sem arvores, o mundo dos pets v12 a v19);
- `ilha`: o CONFIG_MUNDO_MVP com as arvores J1, J2 e J3 do layout padrao, montado aqui com o codigo de hoje (o que o CONFIG_MUNDO_ILHA
  vai ser). Nele o A do v11 quebra quando come uma fruta caida (o MV-10, a AS-11): o gabarito guarda a excecao e a mensagem.
De cada vida: o sha256 do retrato (o log, o traco das decisoes, o resumo do mundo, o corpo e o estado no fim, os proximos sorteios) e o
numero de decisoes; ou o tipo e a mensagem da excecao.

    python tests/gabarito_arvore_sacode.py     # grava tests/gabaritos/arvore_sacode_de_hoje.json (so com o codigo de antes da mudanca)
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

import exportar_gabarito_mvp_mundo as e0  # noqa: E402

from digilab.config import CONFIG_MUNDO_MVP, LAYOUT_MUNDO_PADRAO  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "arvore_sacode_de_hoje.json"
SEMENTES = (101, 202, 303, 404, 505)
ARVORES_ILHA = ("J1", "J2", "J3")
# (o cerebro, o dono, o lugar da comida)
BRACOS = (("a_v11", "atencioso", "comedouro"), ("a_v11", "aleatorio", "perto"), ("instinto", "atencioso", "comedouro"))


def mundo_ilha_de_hoje():
    """o CONFIG_MUNDO_MVP com as arvores J1, J2 e J3 do layout padrao, montado com o codigo de hoje"""
    arvores = tuple(a for a in LAYOUT_MUNDO_PADRAO.arvores if a[0] in ARVORES_ILHA)
    return replace(CONFIG_MUNDO_MVP, layout=replace(CONFIG_MUNDO_MVP.layout, nome="ilha", arvores=arvores))


MUNDOS = {"mvp": CONFIG_MUNDO_MVP, "ilha": mundo_ilha_de_hoje()}


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def impressao(cerebro: str, dono: str, lugar: str, semente: int, cm) -> dict:
    try:
        r = e0.vida("hoje", cerebro, dono, lugar, semente, cm=cm)
    except RuntimeError as ex:
        return {"erro": type(ex).__name__, "mensagem": str(ex)}
    return {"retrato": _sha(r), "decisoes": r["decisoes"]}


def gerar() -> dict:
    return {f"{nome}|{c}|{d}|{l}|{s}": impressao(c, d, l, s, cm)
            for nome, cm in MUNDOS.items() for c, d, l in BRACOS for s in SEMENTES}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO, sum("erro" in v for v in g.values()), "de", len(g), "quebram")
