"""Gabarito das vidas de hoje para o orgao da visao (GOSTO_VISUAL, OV2; docs/ESPEC_V3_ORGAO_VISAO.md, secao 10). Gravado com o codigo de
antes da OV2, num commit proprio. Com a ConfigOrgao desligada (o padrao), estas vidas tem de sair iguais depois, byte a byte.

A OV2 toca o M-SENS, o M-AFETO, o M-ADAPT, a TV e o mundo. As familias com o olhar e o enjoo desligado ja tem gabarito proprio
(tests/gabaritos/gosto_visual_enjoo_vidas_de_hoje.json, conferido pelo tests/test_gabarito_gosto_visual_enjoo.py; e os do P1a e da web).
Aqui ficam as que faltam, com o enjoo LIGADO (a vida da GV3b e a imagem parada com o enjoo):
  - a vida da GV3b (`run_v3_gosto_visual.viver(..., enjoo=True)`): os dois genomas, os tres donos e as unidades das bases 101 e 202 (k = 0),
    3 dias, com a sonda das duas TVs no ultimo dia (2 replicas);
  - a imagem parada com o enjoo (`gabarito_gosto_visual_enjoo.viver_parada(..., cfg_enjoo_tela=CONFIG_ENJOO_TELA_LIGADA)`): as sementes
    101, 202 e 303, 2 dias.
De cada vida, a impressao do gabarito do enjoo (o sha256 do log, do estado, do corpo, do mundo e do cerebro); da sonda, o sha256 do dump.

    python tests/gabarito_orgao_visao.py     # grava tests/gabaritos/orgao_visao_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_gosto_visual_enjoo as G  # noqa: E402
import run_v3_gosto_visual as R  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402

from digilab.config import CONFIG_ENJOO_TELA_LIGADA  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "orgao_visao_vidas_de_hoje.json"
BASES = (101, 202)
DIAS_GV3B = 3
REPLICAS = 2
SEMENTES_PARADA = (101, 202, 303)
DIAS_PARADA = 2


def casos():
    for b in BASES:
        for g in R.GENOMAS:
            for d in R.DONOS:
                yield f"gv3b|{g}|{d}|{b}", ("gv3b", g, d, b)
    for s in SEMENTES_PARADA:
        yield f"parada_enjoo|{s}", ("parada_enjoo", None, None, s)


def vida_de_hoje(familia: str, genoma: str | None, dono: str | None, semente: int) -> dict:
    if familia == "gv3b":
        u = R.unidades([semente], 1)[0]
        m, fab, _ = R.viver(genoma, dono, u, DIAS_GV3B, enjoo=True)
        s = sd.sonda(m, fab, u["semente"], (DIAS_GV3B - 1,), REPLICAS)
        return {**G.impressao(m), "sonda": G._h(s)}
    if familia == "parada_enjoo":
        return G.impressao(G.viver_parada(semente, DIAS_PARADA, cfg_enjoo_tela=CONFIG_ENJOO_TELA_LIGADA))
    raise ValueError(f"familia desconhecida: {familia!r}")


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
