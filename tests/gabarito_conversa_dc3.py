"""Gabarito das vidas de hoje do LAB (o braco REL da C4, `SUBCHAVES_AN["LAB"]`) no cenario da DC3 (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md,
secoes 2, 3.1 e 10: "o gabarito antes"). Gravado com o codigo da main (a066ac63) ANTES da subchave `fala_unidades` e do dono que atende,
num commit proprio. Com a subchave desligada e o dono que ignora (o de hoje), estas vidas tem de sair iguais, byte a byte.

O cenario e o da AN4 (o da C4): o motor que grava o corpo (`run_v2_longe_regular.MotorGravaCorpo`), so o comedouro, os quatro donos sem
ensino e as cinco sementes dos testes (101 a 505), pela vida do orquestrador da AN4 (`run_v3_acoes_novas.viver`). De cada vida: o sha256 do
log (o JSONL do motor), o do estado interno do cerebro, o das medidas do orquestrador do prototipo e o das medidas do corpo, e o numero de
decisoes.

    python tests/gabarito_conversa_dc3.py     # grava tests/gabaritos/conversa_dc3_de_hoje.json (so com o codigo de antes da mudanca)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v3_acoes_novas as an  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "conversa_dc3_de_hoje.json"
SEMENTES = (101, 202, 303, 404, 505)
DIAS = 3
BRACO = "LAB"
LUGAR = "comedouro"
DONOS = orq.DONOS


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def impressao(motor, registro) -> dict:
    c = orq.cerebro_de(registro)
    return {"log": _sha(motor.log.para_jsonl()), "estado": _sha(_texto(c.estado_interno())),
            "medidas": _sha(_texto(orq.medidas(motor, registro, BRACO, DIAS, conserto=True))),
            "corpo": _sha(_texto(lr.medidas_do_corpo(motor, registro, DIAS))), "decisoes": len(c.motivos)}


def gerar() -> dict:
    out = {}
    for semente in SEMENTES:
        for dono in DONOS:
            motor, reg, _, _ = an.viver(BRACO, dono, LUGAR, semente, DIAS, orq.ORCAMENTO_POR_DIA)
            out[f"{BRACO}|{dono}|{LUGAR}|{semente}"] = impressao(motor, reg)
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
