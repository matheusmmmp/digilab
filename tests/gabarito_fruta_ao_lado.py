"""Gabarito das vidas de hoje que a fruta ao lado da racao vai tocar (o RP-2 de docs/futuro/paladar.md, decidido pelo Matheus em
2026-10-14: o dono poe a fruta ao lado da racao): gravado com o codigo da main (aedd5ea) ANTES da `ConfigFrutaAoLado`. Com a chave
desligada, estas vidas tem de sair iguais, byte a byte (G2).

As vidas:
- os casos de `tests/gabarito_paladar_mundo.py`: o mundo fisico (dois layouts, sem e com o corpo quimico, o instinto, o P0 e o P1 com o
  alvo aprendido) e o mundo do J5 com a fruta na mao e a troca de tipo (o corpo quimico com e sem o metabolismo) (84 vidas);
- a bancada do J5 com o Paladar ligado (a fumaca de tests/test_bancada_pqp_paladar.py): o P1 e o P1-plan nos protocolos T1 e T2, as
  sementes 101 e 202 (8 vidas), que e onde a fruta ao lado vai entrar.

O que se confere: a impressao do gabarito dos dois pets (log, estado, estado() com o corpo, acoes, rngs, politica, o registro do mundo
fisico inteiro, com os consumos e as comidas deixadas) e o corpo inteiro.

    python tests/gabarito_fruta_ao_lado.py      # grava tests/gabaritos/fruta_ao_lado_vidas_de_hoje.json (so com o codigo de antes)
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
import gabarito_paladar_mundo as gpm  # noqa: E402

from experiments import bancada_v2 as bv  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "fruta_ao_lado_vidas_de_hoje.json"
CONFIGS = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa"
S = 1024
BRACOS_J5 = ("P1", "P1-plan")
PROTOCOLOS = ("T1", "T2")
SEMENTES = (101, 202)                                   # so as dos testes


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=repr).encode("utf-8")).hexdigest()


def cfg_j5(braco: str, protocolo: str, semente: int) -> dict:
    """a fumaca da bancada do J5 com o Paladar (a de tests/test_bancada_pqp_paladar.py)"""
    base = json.loads((CONFIGS / "fumaca.json").read_text(encoding="utf-8"))
    cfg = {**base, "paladar": True, "consequencia": {"ganho": 4, "canais_ligados": True, "ganho_gosto": S},
           "bracos": [braco], "protocolos": [protocolo], "sementes": [semente]}
    if bv.BRACOS_PQP[braco].planejador:
        cfg["g_plano"] = S
    return cfg


def vida_j5(braco: str, protocolo: str, semente: int, **cfg_extra):
    bp = bv.bancada_pqp_da_config({**cfg_j5(braco, protocolo, semente), **cfg_extra})
    return bp.vida(bv.EspecPQP(braco, protocolo, semente))


def casos():
    for chave, caso in gpm.casos():
        yield f"paladar_mundo|{chave}", ("paladar_mundo", caso)
    for braco in BRACOS_J5:
        for protocolo in PROTOCOLOS:
            for s in SEMENTES:
                yield f"j5|{braco}|{protocolo}|{s}", ("j5", (braco, protocolo, s))


def impressao(fonte: str, caso, **kw) -> dict:
    if fonte == "paladar_mundo":
        return gpm.impressao(*caso, **kw)
    v = vida_j5(*caso, **kw)
    m = v.motor
    corpo = getattr(m, "corpo", None)
    return {**gdp.impressao(m), "tick_mudanca": v.tick_mudanca, "corpo": None if corpo is None else _sha(corpo.para_dict())}


def gerar() -> dict:
    return {chave: impressao(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
