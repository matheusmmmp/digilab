"""Gabarito da troca de ilha (docs/TAREFA_V3_ILHA_AGUA.md, IA4; a IA-4 do Matheus: os pets vivos passam para a ilha nova): vidas do pet
que comecam no mundo do produto de hoje (`CONFIG_MUNDO_MVP`, sem agua e sem o contrato, o dos pets v21 do jogo web) e passam, no meio da
vida, para o mesmo mundo com a agua (`CONFIG_MUNDO_MVP_AGUA`) pelo evento `mudar_ilha`. O corpo, o A do v11, as chaves e o roteiro do
dono sao os do gabarito da agua (experiments/exportar_gabarito_ilha_agua.py): antes da troca o roteiro ja poe a racao e solta o pet em
pontos que depois sao agua, de proposito.

Cada vida troca num tick proprio (TROCAS): numa o pet esta acordado, na outra dormindo (o evento vale nos dois casos). O gerador confere,
com o `conferir` do gabarito da agua, que depois da troca nada fica na agua (a comida que estava no chao, a bola, o pet e tudo o que vem
depois) e que o pet cruza o rio pela ponte; e confere aqui que a troca tirou alguma coisa da agua.

O G-PAR do laco do TS (web/app/test/mudar_ilha.test.ts) confere o TS contra este arquivo. So as sementes dos testes.

    python experiments/exportar_gabarito_mudar_ilha.py      # grava web/app/test/gabaritos/mudar_ilha_python.json
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_ilha_agua as ga  # noqa: E402
import exportar_gabarito_mvp_mundo as e0  # noqa: E402

from digilab.config import CONFIG_MUNDO_MVP, CONFIG_MUNDO_MVP_AGUA  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "mudar_ilha_python.json"
ANTES, DEPOIS = CONFIG_MUNDO_MVP, CONFIG_MUNDO_MVP_AGUA
# (o nome, a semente, o tick da troca, o pet dormindo nela): os ticks ficam fora dos passos do roteiro e das decisoes
VIDAS = (("a_v11_troca_acordado_202", 202, 250, False), ("a_v11_troca_dormindo_505", 505, 367, True))


def _vida(nome: str, semente: int, tick: int, dormindo: bool) -> dict:
    m, pedidos = ga.viver(semente, DEPOIS, troca=(tick, ANTES))
    t = pedidos["troca"]
    if t["dormindo"] is not dormindo:
        raise RuntimeError(f"{nome}: no tick {tick} o pet estava {'dormindo' if t['dormindo'] else 'acordado'}")
    conferido = ga.conferir(m, pedidos)
    tirados = {"comidas": len(t["comidas"]), "bola": t["bola"]["de"] != t["bola"]["para"], "pet": t["pet"]["de"] != t["pet"]["para"]}
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "pontos_fixos", semente), "dias": ga.DIAS, "pedidos": pedidos, "conferido": conferido,
            "troca": {"tick": tick, "dormindo": dormindo, "tirados": tirados}}


def gerar() -> dict:
    vidas = [_vida(*v) for v in VIDAS]
    if not any(v["troca"]["tirados"]["comidas"] for v in vidas) or not any(v["troca"]["tirados"]["pet"] for v in vidas):
        raise RuntimeError(f"o roteiro precisa de uma comida e de um pet tirados da agua pela troca: {[v['troca'] for v in vidas]}")
    return {"versao": 1, "config": {**e0.config(), "dias": ga.DIAS, "mundo_antes": json.loads(json.dumps(asdict(ANTES))),
                                    "mundo_depois": json.loads(json.dumps(asdict(DEPOIS))), "contrato_depois": asdict(ga.CC)},
            "vidas": vidas}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): {[(v['nome'], v['decisoes'], v['troca'], v['conferido']) for v in g['vidas']]}")
