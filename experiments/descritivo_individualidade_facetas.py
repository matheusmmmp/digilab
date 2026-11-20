"""INDIVIDUALIDADE, o adendo 1 do plano (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md, secao 13): o Spearman da 4.4 dentro de cada dono,
so descritivo, sobre os artefatos do I2. Nenhuma vida roda aqui.

Uso: python experiments/descritivo_individualidade_facetas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_individualidade as ri  # noqa: E402

PASTA = RAIZ / ri.SAIDA
DONOS = ("atencioso", "relapso", "aleatorio")      # o incoerente fica fora: as vidas dele sao as do atencioso (D-IND-I2b-1)
SAIDA = "facetas_por_dono.json"


def descritivo(medidas: dict, boot: int = ri.BOOTSTRAP) -> dict:
    """a conta da 4.4 (`ri.facetas`, a mesma rng e o mesmo bootstrap) sobre os pets do REL+F de cada dono"""
    pets = [p for p in medidas.values() if p["braco"] == "REL+F"]
    donos = {p["dono"] for p in pets}
    if donos != set(ri.DONOS):
        raise RuntimeError(f"os donos do medidas.json nao sao os do plano: {sorted(donos)}")
    saida = {}
    for dono in DONOS:
        do_dono = [p for p in pets if p["dono"] == dono]
        if len(do_dono) != len(ri.BASES) * ri.K_POR_BASE:
            raise RuntimeError(f"{dono}: {len(do_dono)} pets, e nao {len(ri.BASES) * ri.K_POR_BASE}")
        saida[dono] = ri.facetas(do_dono, boot)
    return saida


def main() -> None:
    caminho = PASTA / "medidas.json"
    medidas = json.loads(caminho.read_text(encoding="utf-8"))
    resultado = {"adendo": "docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md, secao 13", "medidas_sha256": bv._sha(caminho),
                 "bootstrap": ri.BOOTSTRAP, "donos": list(DONOS), "por_dono": descritivo(medidas)}
    destino = PASTA / SAIDA
    if destino.exists():
        raise FileExistsError(f"{destino} ja existe: o adendo roda uma vez")
    bv._gravar(destino, bv._dump(resultado))
    print(json.dumps(resultado["por_dono"], indent=1, ensure_ascii=True))


if __name__ == "__main__":
    main()
