"""Medida descritiva da IG1 (docs/TAREFA_V3_ILHA_AGUA.md, secao 12): quanto tempo o pet leva para comer a racao posta a uma distancia
do ninho, no mundo de hoje com agua (`CONFIG_MUNDO_MVP_AGUA`, 64 x 30) e na ilha grande (`CONFIG_MUNDO_GRANDE`, 128 x 60).

Nao e run de pesquisa: so as sementes dos testes, sem hipotese e sem gate. Serve para a IG-6 (a velocidade e os sentidos), que o Matheus
deixou para medir antes de mexer. O pet e o do gabarito da agua (o corpo, o A do v11, as chaves dos ovos de hoje, o controlador).

O dono: a cada `PASSO` ticks, com o pet acordado, leva o pet ao ninho e poe uma racao a `d` celulas a leste do ninho (o ponto fechado vai
para a terra mais perto, como no jogo). Mede-se, por racao, se o pet a comeu antes da racao seguinte (`PASSO` ticks, um terco de dia) e em quantos ticks. As distancias
alem do cheiro (24 celulas) so cabem a leste do ninho na ilha grande.

    python experiments/medir_ilha_grande.py      # grava docs/pranchas/ilha-grande/medida_ig1.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_ilha_agua as ag  # noqa: E402

from digilab.config import CONFIG_MUNDO_GRANDE, CONFIG_MUNDO_MVP_AGUA, TICKS_POR_DIA  # noqa: E402
from digilab.mundo import centro_da_celula  # noqa: E402

ARQUIVO = RAIZ / "docs" / "pranchas" / "ilha-grande" / "medida_ig1.json"
SEMENTES = (101, 202, 303, 404, 505)
DIAS, PASSO = 4, 480
MUNDOS = (("hoje_64x30", CONFIG_MUNDO_MVP_AGUA, (4, 12, 24, 36)), ("grande_128x60", CONFIG_MUNDO_GRANDE, (4, 12, 24, 36, 48, 56)))


def vida(cm, semente: int, d: int) -> dict:
    m = ag.motor(semente, cm)
    nx, ny = cm.layout.ninho
    ninho, alvo = centro_da_celula((nx, ny), cm), centro_da_celula((nx + d, ny), cm)
    postas, t0 = [], time.perf_counter()
    for t in range(PASSO, DIAS * TICKS_POR_DIA + 1, PASSO):
        if t > m._estado.tick:
            m.avancar(t - m._estado.tick)
        if m._estado.dormindo:
            continue
        m.levar_pet(*ninho)
        antes = set(m.mundo.comidas)
        m.deixar_comida("racao", *alvo)
        (novo,) = set(m.mundo.comidas) - antes
        postas.append({"tick": m._tm(t), "id": novo})
    if m._estado.tick < DIAS * TICKS_POR_DIA:
        m.avancar(DIAS * TICKS_POR_DIA - m._estado.tick)
    comidas = {c["id"]: c["tick"] for c in m.consumos_mundo}
    tempos = [comidas[p["id"]] - p["tick"] for p in postas if p["id"] in comidas and comidas[p["id"]] - p["tick"] <= PASSO]
    return {"postas": len(postas), "comidas_no_prazo": len(tempos), "ticks": sorted(tempos), "segundos": round(time.perf_counter() - t0, 2)}


def gerar() -> dict:
    saida = {"dias": DIAS, "passo": PASSO, "sementes": list(SEMENTES), "mundos": {}}
    for nome, cm, distancias in MUNDOS:
        por_d = {}
        for d in distancias:
            vidas = [vida(cm, s, d) for s in SEMENTES]
            ticks = sorted(t for v in vidas for t in v["ticks"])
            postas, comidas = sum(v["postas"] for v in vidas), sum(v["comidas_no_prazo"] for v in vidas)
            por_d[str(d)] = {"postas": postas, "comidas_no_prazo": comidas, "fracao": round(comidas / postas, 3) if postas else None,
                             "mediana_ticks": ticks[len(ticks) // 2] if ticks else None,
                             "segundos_por_vida": round(sum(v["segundos"] for v in vidas) / len(vidas), 2)}
        saida["mundos"][nome] = por_d
    return saida


if __name__ == "__main__":
    g = gerar()
    tempos = {n: {d: v.pop("segundos_por_vida") for d, v in por_d.items()} for n, por_d in g["mundos"].items()}
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    for nome, por_d in g["mundos"].items():
        for d, v in por_d.items():
            print(f"{nome} d={d:>2}: {v['comidas_no_prazo']}/{v['postas']} ({v['fracao']}), mediana {v['mediana_ticks']} ticks, {tempos[nome][d]} s por vida")
