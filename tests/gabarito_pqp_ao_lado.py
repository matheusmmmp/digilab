"""Grava o gabarito das vidas do J5 com a fruta ao lado da racao (o adendo 5), ANTES do adendo 7 mexer na bancada.

Para cada vida (braco, protocolo, semente) da fumaca da bancada do J5 com o paladar e a fruta ao lado: o sha256 do log e o das medidas sem
o custo (o tempo de CPU muda de vida para vida). O teste (tests/test_bancada_pqp_adendo7.py) confere que, sem a chave `adendo_7`, as vidas e
as medidas saem iguais byte a byte.

    python tests/gabarito_pqp_ao_lado.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402

DESTINO = RAIZ / "tests" / "gabaritos" / "pqp_ao_lado_vidas.json"
VIDAS = (("P1", "T1", 101), ("P1-plan", "T1", 202), ("P1", "T2", 202), ("P1-plan-desfecho", "T2", 101))


def config() -> dict:
    base = json.loads((RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "fumaca.json").read_text(encoding="utf-8"))
    return {**base, "paladar": True, "fruta_ao_lado": True, "consequencia": {"ganho": 4, "canais_ligados": True, "ganho_gosto": 512},
            "bracos": list(bv.BRACOS_PQP), "protocolos": ["T1", "T2"], "g_plano": 1024, "sementes": [101, 202]}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def vidas(cfg: dict | None = None) -> dict:
    bp = bv.bancada_pqp_da_config(cfg or config())
    out = {}
    for braco, protocolo, s in VIDAS:
        v = bp.vida(bv.EspecPQP(braco, protocolo, s))
        m = bp.medir(v)
        del m["custo"]
        out[v.nome] = {"log": _sha(v.motor.log.para_jsonl()), "medidas": _sha(json.dumps(m, sort_keys=True, ensure_ascii=False))}
    return out


if __name__ == "__main__":
    DESTINO.write_text(json.dumps(vidas(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"gravado {DESTINO}")
