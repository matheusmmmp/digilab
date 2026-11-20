"""Gabarito das vidas de hoje do M1 e do M2 do conserto no `longe_fixo` e no comedouro (docs/TAREFA_V3_HABITO_INTENCAO.md, secao 3.2: "o
gabarito antes"). Gravado com o codigo da main (ea15189) ANTES da subchave `credito_corrida`, num commit proprio. Com ela desligada, estas
vidas tem de sair iguais, byte a byte.

O gabarito do conserto (tests/gabarito_digibrain_conserto.py) cobre os bracos nas celulas comedouro, perto e longe, com as sementes 101 e
202; nenhum gabarito cobre o `longe_fixo` com o cerebro. Este cobre as duas celulas da C2 (o `longe_fixo` e o comedouro), os quatro donos e
as cinco sementes dos testes (101 a 505), para o M1 e o M2 (SUBCHAVES_CONSERTO), pelo orquestrador do prototipo com as medidas do conserto.

De cada vida: o sha256 do log (o JSONL do motor), o do estado interno do cerebro e o das medidas do orquestrador, e o numero de decisoes.

    python tests/gabarito_habito_intencao.py     # grava tests/gabaritos/habito_intencao_de_hoje.json (so com o codigo de antes da mudanca)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "habito_intencao_de_hoje.json"
SEMENTES = (101, 202, 303, 404, 505)
DIAS = 3
BRACOS = ("M1", "M2")
LUGARES = ("longe_fixo", "comedouro")
DONOS = orq.DONOS


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def impressao(motor, registro, braco: str) -> dict:
    c = orq.cerebro_de(registro)
    return {"log": _sha(motor.log.para_jsonl()), "estado": _sha(_texto(c.estado_interno())),
            "medidas": _sha(_texto(orq.medidas(motor, registro, braco, DIAS, conserto=True))), "decisoes": len(c.motivos)}


def gerar() -> dict:
    out = {}
    for braco in BRACOS:
        for semente in SEMENTES:
            for dono in DONOS:
                for lugar in LUGARES:
                    motor, reg, _ = orq.viver(braco, dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
                    out[f"{braco}|{dono}|{lugar}|{semente}"] = impressao(motor, reg, braco)
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
