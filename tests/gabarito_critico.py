"""Gabarito do critico (docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md, secao 9.1, o G2 do C0): as vidas de hoje do pet v38 do Python, gravadas
com o codigo de ANTES da ConfigCritico, num commit proprio. Com a ConfigCritico desligada (o padrao), estas vidas tem de sair iguais,
byte a byte.

As vidas: o pet v38 do E0 (`run_v3_plasticidade_e0.viver("hoje", ...)`) nos bracos APRENDE e CONGELADO, os donos atencioso e relapso, os
lugares `comedouro` e `longe_fixo`, as sementes dos testes 101 e 202, 3 dias. De cada vida: o sha256 do log, do resumo do motor, do
estado de cada decisao e do estado interno do cerebro (com os motivos), e as contagens.

    python tests/gabarito_critico.py     # grava tests/gabaritos/critico_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_plasticidade_e0 as E0  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "critico_de_hoje.json"
SEMENTES = (101, 202)                                   # so as dos testes
DIAS = 3
BRACOS = ("APRENDE", "CONGELADO")
CELULAS = (("atencioso", "comedouro"), ("atencioso", "longe_fixo"), ("relapso", "comedouro"), ("relapso", "longe_fixo"))


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


def impressao(braco: str, dono: str, lugar: str, semente: int) -> dict:
    motor, registro, _ = E0.viver("hoje", braco, dono, lugar, semente, DIAS)
    c = orq.cerebro_de(registro)
    return {"log": _sha(motor.log.para_jsonl()), "motor": _sha(repr(bv.resumo_motor(motor))), "estados": _sha(_texto(registro.estados)),
            "cerebro": _sha(_texto(motor.politica.estado_interno())), "motivos": _sha(_texto(c.motivos)),
            "decisoes": len(c.motivos), "creditos_p2": c.m.plast.creditos}


def gerar() -> dict:
    return {f"{b}|{d}|{lugar}|{s}": impressao(b, d, lugar, s) for b in BRACOS for d, lugar in CELULAS for s in SEMENTES}


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes da ConfigCritico")
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO.write_text(json.dumps(gerar(), indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"gravado: {ARQUIVO.relative_to(RAIZ).as_posix()}")
