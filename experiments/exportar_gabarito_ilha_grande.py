"""Gabarito da ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG1): vidas do pet no `CONFIG_MUNDO_GRANDE` (o mundo do produto com
128 x 60 celulas, o mar em volta, o rio com tres pontes, os lagos, e as arvores e os marcos como celulas fechadas), com o corpo, o A do
v11, as chaves dos ovos de hoje do jogo e o controlador do contrato (`CONFIG_CONTRATO_AGUA`), que e quem desvia do que e fechado. E o
mundo que o TS vai rodar na IG2: o G-PAR do laco do TS confere o TS contra este arquivo.

O roteiro e o do gabarito da agua (exportar_gabarito_ilha_agua.py: `viver` e `conferir`), com os pontos deste mapa: a racao e o pet
soltos na terra dos dois lados do rio, no rio, no lago, no mar, fora do mapa, em cima de uma arvore e em cima de um marco, e a travessia
pela ponte do meio. O `conferir` falha alto se uma comida, a bola ou o pet ficar numa celula fechada, ou se o pet nao cruzar a ponte;
este arquivo confere a mais que a racao e o pet soltos na arvore e no marco foram para a terra. So as sementes dos testes.

    python experiments/exportar_gabarito_ilha_grande.py      # grava web/app/test/gabaritos/ilha_grande_python.json
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_ilha_agua as ag  # noqa: E402
import exportar_gabarito_mvp_mundo as e0  # noqa: E402

from digilab.config import AGUA_POR_LAYOUT, ARVORE_FECHADA, CONFIG_MUNDO_GRANDE, MARCO_FECHADO  # noqa: E402
from digilab.mundo import solidos_da_agua  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "ilha_grande_python.json"
CM = CONFIG_MUNDO_GRANDE
CC = ag.CC
DIAS = ag.DIAS
ARVORE, MARCO = (33, 29), (31, 21)          # uma celula de arvore e uma de marco (o carro) do mapa; o `gerar` confere
# em subunidades (o mapa vai de 0 a 2047 e de 0 a 959); a ponte do meio fica nas colunas 81 e 82 das linhas 33 e 34
PONTE_MEIO = (81, 83, 33, 35)
CABECEIRAS = ((79 * 16 + 8, 34 * 16), (84 * 16 + 8, 34 * 16))
NA_ARVORE, NO_MARCO = (ARVORE[0] * 16 + 8, ARVORE[1] * 16 + 8), (MARCO[0] * 16 + 8, MARCO[1] * 16 + 8)
PONTOS_COMIDA = ((600, 480), (1352, 408), (1700, 500), (432, 656), (5, 5), NA_ARVORE, (1100, 300), NO_MARCO, (1800, 560), (2040, 950))
PONTOS_LEVAR = ((1280, 480), (1352, 410), (1700, 480), (-40, 120), (440, 660), (1000, -7), NA_ARVORE, (3000, 50), NO_MARCO, (0, 0))
ROTEIRO = ag.Roteiro(PONTOS_COMIDA, PONTOS_LEVAR, (), CABECEIRAS, PONTE_MEIO)
VIDAS = (("a_v11_grande_202", 202), ("a_v11_grande_505", 505))


def viver(semente: int):
    return ag.viver(semente, CM, rot=ROTEIRO)


def conferir(m, pedidos: dict) -> dict:
    """os gates da agua (o `conferir` do gabarito da agua) e os da ilha grande: a racao e o pet soltos em cima da arvore e do marco
    nao ficaram la"""
    c = ag.conferir(m, pedidos, ROTEIRO)
    fora = {nome: {k: [p for p in pedidos[k] if tuple(p["pedido"]) == ponto] for k in ("comida", "levar")}
            for nome, ponto in (("arvore", NA_ARVORE), ("marco", NO_MARCO))}
    for nome, por_tipo in fora.items():
        for k, ps in por_tipo.items():
            if not ps or any(p["ficou"] == p["pedido"] for p in ps):
                raise RuntimeError(f"o roteiro precisa de {k} solto em cima de {nome} e tirado de la: {ps}")
    return {**c, "tirados_da_arvore_e_do_marco": {nome: {k: len(ps) for k, ps in por_tipo.items()} for nome, por_tipo in fora.items()}}


def _vida(nome: str, semente: int) -> dict:
    m, pedidos = viver(semente)
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "pontos_fixos", semente), "dias": DIAS, "pedidos": pedidos,
            "conferido": conferir(m, pedidos)}


def gerar() -> dict:
    agua = AGUA_POR_LAYOUT[CM.layout.nome]
    if agua[ARVORE[1]][ARVORE[0]] != ARVORE_FECHADA or agua[MARCO[1]][MARCO[0]] != MARCO_FECHADO:
        raise RuntimeError("a arvore ou o marco do roteiro nao esta onde o roteiro espera")
    return {"versao": 1, "config": {**e0.config(), "dias": DIAS, "mundo": json.loads(json.dumps(asdict(CM))), "agua": list(agua),
                                    "contrato": asdict(CC), "solidos_da_agua": [[s.x0, s.y0, s.x1, s.y1] for s in solidos_da_agua(CM)],
                                    "roteiro": {"comida": ag.ROTEIRO_COMIDA, "levar": ag.ROTEIRO_LEVAR, "ponte": ag.ROTEIRO_PONTE,
                                                "cabeceiras": CABECEIRAS, "pontos_comida": PONTOS_COMIDA, "pontos_levar": PONTOS_LEVAR}},
            "vidas": [_vida(n, s) for n, s in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): {[(v['nome'], v['decisoes'], v['conferido']) for v in g['vidas']]}")
