"""A sonda do plano do ELOGIO (docs/PLANO_ANALISE_V3_ELOGIO.md, secao 2): so as sementes dos testes (101...160), nada daqui vai a
resultado. Por semente, o E0, o E-imed e o E-sorteado (o par) com a chave ligada nos valores padrao (g = S, W = 1), em `dias` dias: as frutas
comidas, as de X e as da preferida do genoma por metade da vida, e os carinhos.

    python experiments/sonda_elogio_plano.py --dias 36 --de 101 --ate 160 --processos 4
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import elogio as el  # noqa: E402
from digilab.config import CONFIG_ELOGIO_LIGADA, CONFIG_FRUTAS, TICKS_POR_DIA  # noqa: E402
from digilab.events import FRUTAS  # noqa: E402
from digilab.frutas import genoma_frutas  # noqa: E402


def _contagem(motor, dono, alvo: str, x: str, meio: int) -> dict:
    fr = [(r["tick"], r["tipo"]) for r in motor.consumos_mundo if r["tipo"] in FRUTAS]

    def conta(f, a, b):
        sel = [t for tk, t in fr if a <= tk < b]
        return [sum(1 for t in sel if t == f), len(sel)]
    return {"x1": conta(x, 0, meio), "x2": conta(x, meio, 10 ** 9), "p1": conta(alvo, 0, meio), "p2": conta(alvo, meio, 10 ** 9),
            "frutas": len(fr), "carinhos": 0 if dono is None else len(dono.carinhos)}


def uma(args) -> dict:
    s, dias = args
    if not 101 <= s <= 505:
        raise ValueError(f"a sonda so usa as sementes dos testes: {s}")
    meio = dias * TICKS_POR_DIA // 2
    pref, x = genoma_frutas(s, CONFIG_FRUTAS).fruta_preferida(), el.fruta_elogio(s)
    e0 = el.viver("E0", s, dias, CONFIG_ELOGIO_LIGADA)
    im, so = el.viver_par(s, dias, CONFIG_ELOGIO_LIGADA)
    return {"s": s, "E0": _contagem(e0[0], None, pref, x, meio), "imed": _contagem(im[0], im[2], pref, x, meio),
            "sort": _contagem(so[0], so[2], pref, x, meio)}


def resumo(vidas: list[dict]) -> dict:
    def fr(a):
        return a[0] / a[1] if a[1] else None

    def media_ep(v):
        return {"media": round(st.mean(v), 3), "ep": round(st.stdev(v) / math.sqrt(len(v)), 3), "n": len(v)}
    out = {"n": len(vidas)}
    for b in ("E0", "imed", "sort"):
        out[b] = {"frutas_mediana": st.median(v[b]["frutas"] for v in vidas),
                  "x_1a_mediana": st.median(v[b]["x1"][0] for v in vidas),
                  "x_1a_menos_de_5": sum(1 for v in vidas if v[b]["x1"][0] < 5),
                  "carinhos_mediana": st.median(v[b]["carinhos"] for v in vidas)}
    for k in ("x1", "x2"):
        d = [fr(v["imed"][k]) - fr(v["sort"][k]) for v in vidas if fr(v["imed"][k]) is not None and fr(v["sort"][k]) is not None]
        out[f"imed_menos_sort_{k}"] = media_ep(d)
    d = [fr(v["E0"]["p2"]) - fr(v["E0"]["p1"]) for v in vidas if fr(v["E0"]["p1"]) is not None and fr(v["E0"]["p2"]) is not None]
    out["p1_e0_pref_2a_menos_1a"] = media_ep(d)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, required=True)
    ap.add_argument("--de", type=int, default=101)
    ap.add_argument("--ate", type=int, default=160)
    ap.add_argument("--processos", type=int, default=4)
    a = ap.parse_args()
    if a.processos > 4:
        raise ValueError("no maximo 4 processos (V3-D8)")
    with ProcessPoolExecutor(a.processos) as ex:
        vidas = list(ex.map(uma, [(s, a.dias) for s in range(a.de, a.ate + 1)]))
    print(json.dumps(resumo(vidas), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
