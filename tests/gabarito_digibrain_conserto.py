"""Gabarito das vidas do DigiBrain modular do conserto (docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secao 5: o G2 da subchave
`intencao_suspensa`). Gravado com o codigo da main (6075b30) ANTES da subchave, num commit proprio. Com ela desligada, estas vidas tem de
sair iguais, byte a byte.

O gabarito do modular de hoje (tests/gabarito_digibrain_modular.py) so cobre os bracos com o cheiro desligado (SUBCHAVES). Este cobre os
11 bracos do modular do conserto (SUBCHAVES_CONSERTO: os 8 com as duas subchaves do cheiro ligadas, o "M3" sendo o M3*, e o M3-sem-inato,
o M3-sem-intencao e o M3-420), pelo orquestrador do prototipo, com as medidas do conserto (`conserto=True`), nas 12 celulas (dono x
lugar), com as sementes dos testes:
  - o M4-emb le a serie E da vida M4 da outra semente, na mesma celula (a regra dos doadores com duas unidades);
  - o M4-con usa o g_apr fixo em G_APR_CON (o valor do gabarito do modular de hoje).

De cada vida: o sha256 do log (o JSONL do motor), o do estado interno do cerebro (os motivos de cada decisao, os modulos) e o das medidas
do orquestrador (sem o `custo`, que e o relogio), e o numero de decisoes.

    python tests/gabarito_digibrain_conserto.py     # grava tests/gabaritos/digibrain_conserto_de_hoje.json (so com o codigo de antes
                                                    # da mudanca)
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

ARQUIVO = RAIZ / "tests" / "gabaritos" / "digibrain_conserto_de_hoje.json"
SEMENTES = (101, 202)
DIAS = 3
G_APR_CON = 1300
BRACOS = orq.BRACOS_MODULAR_CONSERTO


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def impressao(motor, registro, braco: str) -> dict:
    c = orq.cerebro_de(registro)
    return {"log": _sha(motor.log.para_jsonl()), "estado": _sha(_texto(c.estado_interno())),
            "medidas": _sha(_texto(orq.medidas(motor, registro, braco, DIAS, conserto=True))), "decisoes": len(c.motivos)}


def gerar(bracos: tuple = BRACOS) -> dict:
    out = {}
    series = {}
    for braco in bracos:
        for semente in SEMENTES:
            for dono, lugar in orq.CELULAS:
                serie = None
                if braco == "M4-emb":
                    serie = series[(SEMENTES[1 - SEMENTES.index(semente)], dono, lugar)]
                motor, reg, _ = orq.viver(braco, dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, serie_e=serie,
                                          g_apr_con=G_APR_CON if braco == "M4-con" else None, conserto=True)
                if braco == "M4":
                    series[(semente, dono, lugar)] = tuple(orq.cerebro_de(reg).m.afeto.serie_e)
                out[f"{braco}|{dono}|{lugar}|{semente}"] = impressao(motor, reg, braco)
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
