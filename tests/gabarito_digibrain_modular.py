"""Gabarito das vidas do DigiBrain modular de hoje (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 3, A3.7: o G2 das
subchaves `cheiro_inato` e `intencao_cheiro`): gravado com o codigo da main (fa09444) ANTES das duas subchaves. Com as duas desligadas,
estas vidas tem de sair iguais, byte a byte.

O gabarito das 196 vidas (tests/gabarito_digibrain.py) e o do MVP (web/app/test/gabaritos/mvp_produto_python.json) nao montam o
DigiBrain: so conferem que o motor de hoje nao muda. Estas vidas montam o cerebro modular, pelo orquestrador do prototipo
(experiments/run_v2_digibrain_prototipo.py), nos 8 bracos do modular, nas 12 celulas (dono x lugar), com as sementes dos testes:
  - o M4-emb le a serie E da vida M4 da outra semente, na mesma celula (a regra dos doadores com duas unidades);
  - o M4-con usa o g_apr fixo em G_APR_CON (o valor do teste do G1, tests/test_digibrain_vidas.py).

De cada vida: o sha256 do log (o JSONL do motor), o do estado interno do cerebro (os motivos de cada decisao, os modulos) e o das medidas
do orquestrador (sem o `custo`, que e o relogio), e o numero de decisoes.

    python tests/gabarito_digibrain_modular.py      # grava tests/gabaritos/digibrain_modular_de_hoje.json (so com o codigo de antes)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "digibrain_modular_de_hoje.json"
SEMENTES = (101, 202)
DIAS = 3
G_APR_CON = 1300
BRACOS = ("M0", "M1", "M2", "M3", "M3-sp", "M4", "M4-emb", "M4-con")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def impressao(motor, registro, braco: str) -> dict:
    c = orq.cerebro_de(registro)
    return {"log": _sha(motor.log.para_jsonl()), "estado": _sha(_texto(c.estado_interno())),
            "medidas": _sha(_texto(orq.medidas(motor, registro, braco, DIAS))), "decisoes": len(c.motivos)}


def gerar() -> dict:
    out = {}
    series = {}
    for braco in BRACOS:
        for semente in SEMENTES:
            for dono, lugar in orq.CELULAS:
                serie = None
                if braco == "M4-emb":
                    serie = series[(SEMENTES[1 - SEMENTES.index(semente)], dono, lugar)]
                motor, reg, _ = orq.viver(braco, dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, serie_e=serie,
                                          g_apr_con=G_APR_CON if braco == "M4-con" else None)
                if braco == "M4":
                    series[(semente, dono, lugar)] = tuple(orq.cerebro_de(reg).m.afeto.serie_e)
                out[f"{braco}|{dono}|{lugar}|{semente}"] = impressao(motor, reg, braco)
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
