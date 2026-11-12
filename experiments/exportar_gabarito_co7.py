"""Gabarito da CO7 (docs/ESPEC_V3_COOPERACAO_CO7.md, missao CO7a; secao 6): as vidas do `Grupo` com a CO6 ligada e a CO7 desligada, com as
decisoes e os `estado_interno()` de cada cerebro. Gravado com o codigo da `main` depois da CO6 e ANTES da CO7b, num commit proprio: e o par
fixo do G2 da CO7 (desligada, as vidas saem byte a byte).

As vidas sao as da CO6a (experiments/exportar_gabarito_co6.py: o DigiBrain modular nos dois pets, o mundo do produto, o corpo da bancada),
refeitas com a ConfigCooperacao da CO6 ligada; o `estado_interno()` de cada cerebro inclui a chave `social` (a reputacao e o peso dos
deveres que o M-SENS leu), e o resumo da cooperacao, o `peso_dever` de cada pet.

    python experiments/exportar_gabarito_co7.py              # grava tests/gabaritos/co7_vidas_de_hoje.json.gz
    python experiments/exportar_gabarito_co7.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402

from digilab.config import CONFIG_COOPERACAO_CO6  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "co7_vidas_de_hoje.json.gz"
VIDAS = e6.VIDAS


def vida(v: tuple, cfg_cooperacao=CONFIG_COOPERACAO_CO6) -> dict:
    return e6.vida(v, cfg_cooperacao)


def gerar() -> dict:
    return {"fonte": "experiments/exportar_gabarito_co7.py", "braco": e6.BRACO, "dias": e6.DIAS, "vidas": [vida(v) for v in VIDAS]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito da CO7 mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        print(f"vida {v['semente']}: decisoes {[len(p['decisoes']) for p in v['pets'].values()]}, "
              f"peso_dever {v['cooperacao']['peso_dever']}, reputacao {v['cooperacao']['reputacao']}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
