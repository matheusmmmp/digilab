"""Gabarito do laco do pet com o mundo do produto no MVP (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 1; decisao do Matheus de
2026-10-24, a opcao 1): o mesmo exportador da etapa 0 (experiments/exportar_gabarito_mvp_mundo.py), as mesmas vidas, o mesmo dono com
lugar e o mesmo cerebro (o A do v11 sem as chaves do mundo, o alvo padrao do motor; e o instinto do mundo), so com o mundo do produto:
o `CONFIG_MUNDO_MVP` (o layout padrao sem arvores, so a racao do jogador). O G-PAR do pet v12 (web/app/test/mvp_mundo.test.ts) confere o
laco do TS contra este arquivo, decisao a decisao; o gabarito da etapa 0 (layout padrao) segue como o G-PAR do laco de pesquisa.
Gravado num commit proprio, antes do codigo do laco com este layout. So as sementes dos testes. Nenhuma mecanica nova.

    python experiments/exportar_gabarito_mvp_produto.py      # grava web/app/test/gabaritos/mvp_produto_python.json
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_mvp_mundo as e0  # noqa: E402

from digilab.config import CONFIG_MUNDO_MVP  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "mvp_produto_python.json"
CM = CONFIG_MUNDO_MVP
VIDAS = e0.VIDAS


def gerar() -> dict:
    return {"versao": 1, "config": {**e0.config(), "mundo": json.loads(json.dumps(asdict(CM)))},
            "vidas": [e0.vida(*v, cm=CM) for v in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): "
          f"{[(v['nome'], v['decisoes'], len(v['resumo']['consumos']), len(v['log'])) for v in g['vidas']]}")
