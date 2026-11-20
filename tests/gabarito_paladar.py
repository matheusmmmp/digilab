"""Gabarito das vidas de hoje para o G2 do Paladar, a parte do corpo e do cerebro (docs/futuro/paladar.md, secao 4 e etapas 2 e 3; PL-1 a
PL-9): gravado com o codigo da main d0755c8 ANTES de mexer no corpo, no grafo, no motor do corpo e no cerebro. Com a sub-chave `paladar`
desligada, tudo aqui tem de sair igual, byte a byte.

Duas partes:
- **o mundo fisico com e sem o corpo**: as vidas, os grupos e o corpo sozinho de tests/gabarito_orgaos.py (a mesma impressao, refeita
  com o codigo de agora);
- **os bracos do J5** pela bancada do pet que pensa (a fumaca, vidas curtas): P1 e P1-plan nos dois protocolos, sementes 101 e 202, com
  o log, o estado, o corpo (o metabolismo) e o estado interno do cerebro (os pesos, os modelos do mundo).

    python tests/gabarito_paladar.py      # grava tests/gabaritos/paladar_vidas_de_hoje.json (so com o codigo de antes)
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
import gabarito_orgaos as gor  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "paladar_vidas_de_hoje.json"
FUMACA_J5 = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "fumaca.json"
CURTA = {"d_a": 2, "janela": 1}
BRACOS_J5 = ("P1", "P1-plan")
PROTOCOLOS = ("T1", "T2")
SEMENTES = (101, 202)
G_PLANO = 1024                                  # S, o do adendo 1 do J5 (so no P1-plan)


def _sha(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=repr).encode()).hexdigest()


def vida_j5(braco: str, protocolo: str, semente: int) -> dict:
    cfg = {**json.loads(FUMACA_J5.read_text(encoding="utf-8")), **CURTA, "bracos": list(BRACOS_J5), "g_plano": G_PLANO}
    bp = bv.bancada_pqp_da_config(cfg)
    v = bp.vida(bv.EspecPQP(braco, protocolo, semente))
    m = v.motor
    return {"log": _sha(m.log.para_jsonl()), "estado": _sha(m.estado()), "corpo": _sha(m.corpo.para_dict()),
            "politica": _sha(m.politica.estado_interno()), "fisico": _sha(m.resumo_mundo_fisico())}


def gerar() -> dict:
    g = {f"orgaos|{k}": v for k, v in gor.gerar().items()}
    for braco in BRACOS_J5:
        for protocolo in PROTOCOLOS:
            for s in SEMENTES:
                g[f"j5|{braco}|{protocolo}|{s}"] = vida_j5(braco, protocolo, s)
    return g


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} casos")
