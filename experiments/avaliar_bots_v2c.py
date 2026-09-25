"""Avaliador rapido de desenhos de bots da V2C (TAREFA_CORRECAO_COMBATE, redesenho dos bots).

So sementes de CALIBRACAO e poucas partidas: serve para escolher o desenho; a bateria completa
(run_bateria_combate.py) e a validacao vem depois. Mede G1, G4, G5, G6b e G9 como a bateria.

    python experiments/avaliar_bots_v2c.py [--partidas 40]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.bots import ADAPTATIVO, FIXOS, ORACULO, TODOS, bot  # noqa: E402
from digilab.combate_v2.gambits import PESADO_AUTOMATICO  # noqa: E402
from digilab.combate_v2.lutador import CondicaoFisica, Lutador  # noqa: E402
from digilab.combate_v2.partida import jogar  # noqa: E402
from digilab.config import CONFIG_BATERIA_COMBATE, CONFIG_BATERIA_V2C, CONFIG_COMBATE_V2, ConfigCombateV2C  # noqa: E402
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SEM = (1101, 1202, 1303, 1404, 1505)


def cfg_v2c(**extra) -> ConfigCombateV2C:
    base = json.loads((RAIZ / "experiments" / "configs" / "v2c" / "c4o.json").read_text(encoding="utf-8"))["regras"]
    return ConfigCombateV2C(**{**asdict(CONFIG_COMBATE_V2), **base, **extra})


def rr(bots, nomes, n, cc, rot, decisoes=None, turnos=None, fins=None):
    conf = []
    for i, a in enumerate(nomes):
        for b in nomes[i:]:
            for s in SEM:
                for k in range(n):
                    sp = derivar_semente("aval", rot, s, a, b, k)
                    p = jogar(bots[a], bots[b], sp, cc) if k < n // 2 else jogar(bots[b], bots[a], sp, cc)
                    pts = p.pontos_a if k < n // 2 else 1.0 - p.pontos_a
                    conf.append((a, b, pts))
                    if turnos is not None:
                        turnos.append(p.turnos)
                        fins[p.motivo_fim] = fins.get(p.motivo_fim, 0) + 1
                    if decisoes is not None:
                        for ev in p.log:
                            if ev["tipo"] != "turno":
                                continue
                            for nome, ac, mo in ((p.nome_a, ev["a"], ev["ma"]), (p.nome_b, ev["b"], ev["mb"])):
                                if mo != PESADO_AUTOMATICO and ac != "pesado":
                                    decisoes.setdefault(nome, {}).setdefault(ac, 0)
                                    decisoes[nome][ac] += 1
    return matriz_taxas(conf)


def avaliar(n: int = 40, cc=None) -> dict:
    cc = cc or cfg_v2c(bots_v2c=True)
    cb, cv = CONFIG_BATERIA_COMBATE, CONFIG_BATERIA_V2C
    bots = {x: bot(x, cfg=cc) for x in TODOS}
    dec, tur, fins = {}, [], {}
    tx = rr(bots, list(TODOS), n, cc, "rr", dec, tur, fins)
    eq = equilibrio_simetrico(tx, list(FIXOS), cb.iteracoes_fictitious_play)
    sup = suporte(eq["estrategia"], cb.peso_minimo_suporte)
    dom = [x for x in FIXOS if all(tx[x][y] > 0.5 for y in FIXOS if y != x)]
    acoes = sorted({a for d in dec.values() for a in d})
    cont = {a: sum(dec.get(x, {}).get(a, 0) for x in sup) for a in acoes}
    tot = sum(cont.values())
    frac = {a: c / tot for a, c in cont.items()}
    escolhiveis = ("avancar", "recuar", "golpe_rapido", "preparar_pesado", "disparo", "defender", "esquivar", "carregar")
    mortas = [a for a in escolhiveis if frac.get(a, 0.0) < cb.fracao_min_acao]
    neutra = CondicaoFisica.neutra(cc)
    fav = CondicaoFisica(neutra.hp_max * 1.05, neutra.guts_inicial + 2, neutra.regen_guts)
    des = CondicaoFisica(neutra.hp_max * 0.95, neutra.guts_inicial - 2, neutra.regen_guts)
    g6b = {}
    for e in [x for x in FIXOS if x != "aleatorio"] + [ADAPTATIVO]:
        b2 = {"f": Lutador(e + "#fav", fav, bots[e].estilo), "d": Lutador(e + "#des", des, bots[e].estilo)}
        t = rr(b2, ["f", "d"], n // 2 * 2, cc, "g6b")
        g6b[e] = t["f"]["d"]
    nomes = list(TODOS)
    pares = [(a, b) for i, a in enumerate(nomes) for b in nomes[i + 1:]]
    dec005 = sum(tx[a][b] < .1 or tx[a][b] > .9 for a, b in pares) / len(pares)
    b02 = {x: Lutador(x, bots[x].condicao, replace(bots[x].estilo, epsilon=max(bots[x].estilo.epsilon, 0.2))) for x in nomes}
    t02 = rr(b02, nomes, n, cc, "g9")
    dec02 = sum(t02[a][b] < .1 or t02[a][b] > .9 for a, b in pares) / len(pares)
    extremos = sorted(f"{a}|{b} {t02[a][b]:.2f}" for a, b in pares if t02[a][b] < .1 or t02[a][b] > .9)
    lim = fins.get("limite", 0) / len(tur)
    res = {
        "G1": (not dom and len(sup) >= cb.suporte_minimo, dom, sup, {k: round(v, 3) for k, v in eq["estrategia"].items()}),
        "G2": (round(sum(tx[ORACULO][y] for y in FIXOS) / 5, 3), round(sum(tx[ADAPTATIVO][y] for y in FIXOS) / 5, 3),
               round(tx[ADAPTATIVO]["aleatorio"], 3)),
        "G4": (lim < cb.fracao_max_limite_turnos and 8 <= statistics.median(tur) <= 30, round(lim, 3), statistics.median(tur)),
        "G5": (not mortas, mortas, {k: round(v, 3) for k, v in frac.items()}),
        "G6b": (max(g6b.values()) <= cv.taxa_max_g6b, {k: round(v, 3) for k, v in g6b.items()}),
        "G9": (dec02 <= cv.fracao_max_g9, round(dec005, 3), round(dec02, 3), extremos),
        "matriz": {a: {b: round(tx[a][b], 2) for b in nomes} for a in nomes},
    }
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--partidas", type=int, default=40)
    ap.add_argument("--original", action="store_true", help="bots da V2 original (sem bots_v2c)")
    a = ap.parse_args()
    r = avaliar(a.partidas, cfg_v2c(bots_v2c=not a.original))
    for k, v in r.items():
        if k != "matriz":
            print(k, v)
    print("matriz")
    for x, lin in r["matriz"].items():
        print(f"  {x:12s}", " ".join(f"{lin[y]:.2f}" for y in r["matriz"]))
