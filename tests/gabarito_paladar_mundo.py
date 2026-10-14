"""Gabarito das vidas de hoje que o lado do mundo do Paladar vai tocar (docs/futuro/paladar.md, secao 6, etapa 1, do A): gravado com o
codigo da main (d0755c8) ANTES da `ConfigPaladar`. Com a chave desligada, estas vidas tem de sair iguais, byte a byte (G2).

As vidas reusam os casos de dois gabaritos de antes, que ja cobrem tudo o que a etapa toca (o consumo no `comer`, no "achou e comeu" e na
fruta na mao, e o registro do consumo):
- `tests/gabarito_pqp_mundo.py`: o mundo fisico nos dois layouts, sem o corpo e com o corpo quimico, o instinto, o P0 e o P1 com o alvo
  aprendido (48 vidas);
- `tests/gabarito_pet_que_pensa_plano.py`: o mundo do J5 ligado, com a fruta na mao e a troca de tipo no dia 2, o corpo quimico com e sem
  o metabolismo, o instinto, o P0, o P1 do plano e o P1 com o motivo (36 vidas).

O que se confere: a impressao do gabarito dos dois pets (log, estado, estado() com o corpo, acoes, rngs, politica, o registro do mundo
fisico inteiro, com os consumos) e o corpo inteiro (`Corpo.para_dict`), quando ha corpo.

    python tests/gabarito_paladar_mundo.py      # grava tests/gabaritos/paladar_mundo_vidas_de_hoje.json (so com o codigo de antes)
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

import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_pet_que_pensa_plano as gpl  # noqa: E402
import gabarito_pqp_mundo as gq  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "paladar_mundo_vidas_de_hoje.json"


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=repr).encode("utf-8")).hexdigest()


def casos():
    for chave, caso in gq.casos():
        yield f"mundo|{chave}", ("mundo", caso)
    for chave, caso in gpl.casos():
        yield f"j5|{chave}", ("j5", caso)


def impressao(fonte: str, caso, **kw) -> dict:
    if fonte == "mundo":
        v = gq.vida(*caso, **kw)
        m, d = v.motor, gdp.impressao(v.motor, v.interacoes)
    else:
        m, _, mudanca = gpl.vida(*caso, **kw)
        d = {**gdp.impressao(m), "mudanca": mudanca}
    corpo = getattr(m, "corpo", None)
    d["corpo"] = None if corpo is None else _sha(corpo.para_dict())
    return d


def gerar() -> dict:
    return {chave: impressao(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
