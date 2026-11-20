"""Gabarito do PV-2 (docs/PLANO_ANALISE_V3_PET_VIVO_PV2.md, secao 1.1; docs/futuro/integracao_cadeia_digibrain.md, secao 8.2): as vidas
de hoje do DigiBrain modular do braco REL, gravadas com o codigo de ANTES da ConfigPV2, num commit proprio. Com a ConfigPV2 desligada
(o padrao), estas vidas tem de sair iguais, byte a byte.

As vidas: o REL das fases do conserto (`orq.viver(..., conserto=True)`), o corpo do v11 da bancada, os 3 lugares da C4 (`comedouro`,
`longe_fixo` e `longe`), o dono `atencioso`, as sementes dos testes 101 e 202, 3 dias. De cada vida: o sha256 do log, do estado do motor
e do estado interno do cerebro (com os motivos), e as contagens.

    python tests/gabarito_pv2.py     # grava tests/gabaritos/pv2_de_hoje.json (so com o codigo de antes)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "pv2_de_hoje.json"
SEMENTES = (101, 202)                                   # so as dos testes
DIAS = 3
DONO = "atencioso"
LUGARES = ("comedouro", "longe_fixo", "longe")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


def impressao(lugar: str, semente: int) -> dict:
    motor, registro, _ = orq.viver("REL", DONO, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    cerebro = orq.cerebro_de(registro)
    comidas = [x["tipo"] for x in motor.consumos_mundo]
    cheiro = sum(1 for m in cerebro.motivos if m["escolha"][1:2] == ["cheiro"])
    return {"log": _sha(_texto([ev.para_dict() for ev in motor.log])), "estado": _sha(_texto(motor.estado())),
            "cerebro": _sha(_texto(cerebro.estado_interno())), "decisoes": cerebro.k, "racao": comidas.count("racao"),
            "decisoes_cheiro": cheiro}


def gerar() -> dict:
    return {f"{lugar}|{s}": impressao(lugar, s) for lugar in LUGARES for s in SEMENTES}


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes da ConfigPV2")
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
