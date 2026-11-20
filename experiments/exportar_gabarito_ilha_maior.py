"""Gabarito da ida para a ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG4; a IG-7 do Matheus: o pet, a comida e a bola dos pets
vivos vao "deslocados junto com o lar"): vidas do pet que comecam no mundo do produto de hoje e passam, no meio da vida, para a ilha
grande (`CONFIG_MUNDO_GRANDE`, 128 x 60) pelo evento `mudar_ilha`. Os tres caminhos dos pets do jogo web:

- o pet v21 que nunca passou para a agua: do `CONFIG_MUNDO_MVP` (sem agua, sem o contrato) direto para a ilha grande;
- o pet v22, que nasceu na agua: do `CONFIG_MUNDO_MVP_AGUA` (com o controlador) para a ilha grande, com ele dormindo;
- o pet v21 que ja tinha passado para a agua: do MVP para o MVP com agua, e depois para a ilha grande.

O corpo, o A do v11, as chaves e os passos do roteiro sao os do gabarito da agua. Antes da ida o roteiro usa os pontos do mapa de 64 x 30
(exportar_gabarito_ilha_agua.py); depois, os da ilha grande (exportar_gabarito_ilha_grande.py). O gerador confere, com o `conferir` do
gabarito da agua, que depois da ida nada fica em celula fechada e que o pet cruza o rio pela ponte; e confere aqui que tudo andou o
deslocamento do ninho (o que caiu em terra livre ficou exatamente la) e que a ida tirou alguma coisa de uma celula fechada.

O G-PAR do laco do TS (web/app/test/ilha_maior.test.ts) confere o TS contra este arquivo. So as sementes dos testes.

    python experiments/exportar_gabarito_ilha_maior.py      # grava web/app/test/gabaritos/ilha_maior_python.json
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
import exportar_gabarito_ilha_grande as gg  # noqa: E402
import exportar_gabarito_mvp_mundo as e0  # noqa: E402

from digilab.config import CONFIG_MUNDO_GRANDE, CONFIG_MUNDO_MVP, CONFIG_MUNDO_MVP_AGUA, TICKS_POR_DIA  # noqa: E402
from digilab.mundo import centro_da_celula, no_mapa  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "ilha_maior_python.json"
GRANDE, AGUA = CONFIG_MUNDO_GRANDE.layout.nome, CONFIG_MUNDO_MVP_AGUA.layout.nome
# o ponto do mapa de 64 x 30 que, com o deslocamento do ninho (16 e 15 celulas), cai na celula (31, 21) da ilha grande: o carro
SOB_O_CARRO = centro_da_celula((gg.MARCO[0] - (CONFIG_MUNDO_GRANDE.layout.ninho[0] - CONFIG_MUNDO_MVP.layout.ninho[0]),
                                gg.MARCO[1] - (CONFIG_MUNDO_GRANDE.layout.ninho[1] - CONFIG_MUNDO_MVP.layout.ninho[1])), CONFIG_MUNDO_MVP)
# (o nome, a semente, o mundo e o contrato do comeco, as trocas (tick, destino), o pet dormindo na ida para a ilha grande): os ticks
# ficam fora dos passos do roteiro
VIDAS = (("a_v11_v21_direto_202", 202, CONFIG_MUNDO_MVP, None, ((250, GRANDE),), False),
         ("a_v11_v22_dormindo_505", 505, CONFIG_MUNDO_MVP_AGUA, ga.CC, ((367, GRANDE),), True),
         ("a_v11_v21_pela_agua_202", 202, CONFIG_MUNDO_MVP, None, ((130, AGUA), (700, GRANDE)), False))


def viver(semente: int, inicio, contrato, trocas: tuple):
    """a vida do roteiro com as trocas; devolve o motor e o que o roteiro pediu, com `troca` (a ida para a ilha grande) no formato que o
    `conferir` do gabarito da agua le"""
    m = ga.motor(semente, inicio, False, contrato)
    fim, agora, k = ga.DIAS * TICKS_POR_DIA, 0, {"c": 0, "l": 0, "p": 0}
    pedidos = {"comida": [], "levar": [], "bola": [], "ponte": [], "dormindo_em": [], "trocas": []}
    passos, rot, quando = (ga.ROTEIRO_COMIDA, ga.ROTEIRO_LEVAR, ga.ROTEIRO_PONTE), ga.ROTEIRO, dict(trocas)
    if any(t % p == 0 for t in quando for p in passos):
        raise ValueError(f"um tick de troca cai num passo do roteiro: {trocas}")

    def comida(t: int, x: int, y: int) -> None:
        antes = set(m.mundo.comidas)
        m.deixar_comida("racao", x, y)
        (novo,) = set(m.mundo.comidas) - antes
        c = m.mundo.comidas[novo]
        pedidos["comida"].append({"tick": t, "id": novo, "pedido": [x, y], "ficou": [c["x"], c["y"]]})

    for t in sorted({t for t in range(1, fim + 1) if any(t % p == 0 for p in passos)} | {fim} | set(quando) | {t - 1 for t, n in quando.items() if n == GRANDE}):
        m.avancar(t - agora)
        agora = t
        if quando.get(t + 1) == GRANDE:           # um tick antes da ida: uma racao que a ida leva para cima do carro (um marco fechado)
            comida(t, *SOB_O_CARRO)
        if t in quando:
            dormindo, pet, no_chao = m._estado.dormindo, list(m.pet), {i: [c["x"], c["y"]] for i, c in m.mundo.comidas.items()}
            m.mudar_ilha(quando[t])
            if quando[t] == GRANDE:
                rot = gg.ROTEIRO
                pedidos["troca"] = {"tick": t, "dormindo": dormindo, "pet_antes": pet, "no_chao": no_chao, **m.mundo.troca_maior}
            else:
                pedidos["trocas"].append({"tick": t, "dormindo": dormindo, **m.mundo.troca_ilha})
        if t % ga.ROTEIRO_COMIDA == 0:
            comida(t, *rot.comida[k["c"] % len(rot.comida)])
            k["c"] += 1
        if t % ga.ROTEIRO_LEVAR == 0:
            x, y = rot.levar[k["l"] % len(rot.levar)]
            if m._estado.dormindo:
                pedidos["dormindo_em"].append(t)
            else:
                k["l"] += 1
                m.levar_pet(x, y)
                pedidos["levar"].append({"tick": t, "pedido": [x, y], "ficou": list(m.pet)})
        if t % ga.ROTEIRO_PONTE == 0 and not m._estado.dormindo:
            de, para = rot.cabeceiras[k["p"] % 2], rot.cabeceiras[(k["p"] + 1) % 2]
            k["p"] += 1
            m.levar_pet(*de)
            comida(t, *para)
            pedidos["ponte"].append({"tick": t, "pet": list(de), "racao": list(para), "ficou": list(m.pet)})
    return m, pedidos


def conferir_ida(m, t: dict) -> dict:
    """a ida em si: cada coisa andou o deslocamento do ninho; a que caiu em terra livre ficou exatamente la, e a que caiu em celula
    fechada ou fora do mapa foi para a terra. Falha alto se nao."""
    cm, (dx, dy) = m.cmf, t["deslocamento"]
    if [dx, dy] != [(cm.layout.ninho[i] - CONFIG_MUNDO_MVP.layout.ninho[i]) * cm.sub for i in (0, 1)]:
        raise RuntimeError(f"o deslocamento nao e o do ninho: {t['deslocamento']}")
    exatos = tirados = 0
    coisas = [(c["de"], c["para"]) for c in t["comidas"]] + [(t["bola"]["de"], t["bola"]["para"]), (t["pet"]["de"], t["pet"]["para"])]
    if sorted(c["id"] for c in t["comidas"]) != sorted(t["no_chao"]) or any(c["de"] != t["no_chao"][c["id"]] for c in t["comidas"]):
        raise RuntimeError("a ida nao levou toda a comida que estava no chao")
    for de, para in coisas:
        alvo = list(no_mapa(de[0] + dx, de[1] + dy, cm))
        if not m.mundo.seca(*para):
            raise RuntimeError(f"depois da ida, em celula fechada: {de} -> {para}")
        if m.mundo.seca(*alvo) and para == alvo:
            exatos += 1
        elif m.mundo.seca(*alvo) and (de, para) != (t["pet"]["de"], t["pet"]["para"]):
            raise RuntimeError(f"o ponto livre {alvo} nao foi respeitado: {de} -> {para}")       # so o pet pode sair, pelo raio do corpo
        else:
            tirados += 1
    return {"exatos": exatos, "tirados": tirados, "comidas": len(t["comidas"])}


def _vida(nome: str, semente: int, inicio, contrato, trocas: tuple, dormindo: bool) -> dict:
    m, pedidos = viver(semente, inicio, contrato, trocas)
    t = pedidos["troca"]
    if t["dormindo"] is not dormindo:
        raise RuntimeError(f"{nome}: na ida o pet estava {'dormindo' if t['dormindo'] else 'acordado'}")
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "pontos_fixos", semente), "dias": ga.DIAS, "pedidos": pedidos,
            "conferido": ga.conferir(m, pedidos, gg.ROTEIRO), "ida": conferir_ida(m, t),
            "comeco": {"mundo": inicio.layout.nome, "contrato": contrato is not None, "trocas": [list(x) for x in trocas], "dormindo": dormindo}}


def gerar() -> dict:
    vidas = [_vida(*v) for v in VIDAS]
    if not all(v["ida"]["exatos"] and v["ida"]["tirados"] and v["ida"]["comidas"] for v in vidas):
        raise RuntimeError(f"o roteiro precisa de coisas levadas no ponto exato e de alguma tirada de celula fechada: {[v['ida'] for v in vidas]}")
    return {"versao": 1, "config": {**e0.config(), "dias": ga.DIAS, "mundo_mvp": json.loads(json.dumps(asdict(CONFIG_MUNDO_MVP))),
                                    "mundo_agua": json.loads(json.dumps(asdict(CONFIG_MUNDO_MVP_AGUA))),
                                    "mundo_grande": json.loads(json.dumps(asdict(CONFIG_MUNDO_GRANDE))), "contrato": asdict(ga.CC)},
            "vidas": vidas}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): {[(v['nome'], v['decisoes'], v['ida'], v['conferido']) for v in g['vidas']]}")
