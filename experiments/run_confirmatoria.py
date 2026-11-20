"""Run confirmatoria da hipotese central (docs/PLANO_ANALISE.md, congelado antes da run).

    python experiments/run_confirmatoria.py --processos 8
    python experiments/run_confirmatoria.py --fumaca --ovos 50001 50002 --painel 2 --partidas 2 --saida <pasta>   # fumaca

Desenho principal B (painel fixo), condicao NEUTRA: por ovo, diferenca (atencioso - aleatorio) da taxa media
contra os 32 bots do painel (8 formas adultas canonicas x 4 especies da bateria V21C), 50 partidas por bot.
Secundarias (Holm, alfa 0,05 no conjunto): relapso x aleatorio, incoerente x aleatorio, exigente x aleatorio e
exigente x atencioso, no desenho B, condicao neutra. Descritivos: desenho A (10 pares de bracos, M = 100) e a
condicao real.

Vidas e partidas: experiments/run_poder.executar (o mesmo codigo do piloto), sementes confirmatorias 60001-60160 e
rotulo de partida proprio. Estatistica: bootstrap percentil sobre ovos, 10000 reamostragens, semente 20260927;
p-valor pelo bootstrap (x 2); teste t de uma amostra como conferencia (p pela normal: N = 160). Uma unica analise,
depois de todas as partidas.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

from run_poder import CFG_PADRAO, _dump, _gravar, executar  # noqa: E402

SEMENTE_BOOT = 20260927
BOOT = 10000
DELTA = 0.10
ALFA = 0.05
M_A, M_B = 100, 50
PRINCIPAL = ("atencioso", "aleatorio")
SECUNDARIAS = (("relapso", "aleatorio"), ("incoerente", "aleatorio"), ("exigente", "aleatorio"), ("exigente", "atencioso"))


def taxa_painel(res_ovo: dict, braco: str) -> float:
    """taxa media do braco contra o painel (media das partidas de todos os bots)"""
    pts = [x for bot in res_ovo["B"][braco].values() for x in bot]
    return sum(pts) / len(pts)


def diferencas_b(por_ovo: dict, x: str, y: str) -> list[float]:
    return [taxa_painel(r, x) - taxa_painel(r, y) for _, r in sorted(por_ovo.items(), key=lambda kv: int(kv[0]))]


def taxas_a(por_ovo: dict, x: str, y: str) -> list[float]:
    out = []
    for _, r in sorted(por_ovo.items(), key=lambda kv: int(kv[0])):
        if f"{x}|{y}" in r["A"]:
            p = r["A"][f"{x}|{y}"]
            out.append(sum(p) / len(p))
        else:
            p = r["A"][f"{y}|{x}"]
            out.append(1.0 - sum(p) / len(p))
    return out


def bootstrap(valores: list[float], nula: float, semente: int) -> dict:
    """estimativa, IC 95% percentil, p bilateral pelo bootstrap e t de conferencia"""
    rng = random.Random(semente)
    n = len(valores)
    est = sum(valores) / n
    medias = sorted(sum(valores[rng.randrange(n)] for _ in range(n)) / n for _ in range(BOOT))
    ic = (medias[int(0.025 * BOOT)], medias[int(0.975 * BOOT) - 1])
    lado = sum(1 for m in medias if m <= nula) if est > nula else sum(1 for m in medias if m >= nula)
    p = min(1.0, 2 * lado / BOOT)
    dp = statistics.stdev(valores)
    t = (est - nula) / (dp / math.sqrt(n)) if dp > 0 else float("inf")
    p_t = 2 * (1 - statistics.NormalDist().cdf(abs(t)))
    return {"n": n, "estimativa": est, "ic95": list(ic), "p_bootstrap": p, "t": t, "p_t_normal": p_t}


def leitura(r: dict, delta: float = DELTA) -> str:
    """secao 5 do plano"""
    lo, hi = r["ic95"]
    if lo > 0 and r["estimativa"] >= delta / 2:
        return "SUSTENTADA"
    if (-delta < lo and hi < delta) or hi < 0:
        return "REFUTADA"
    return "INCONCLUSIVA"


def holm(ps: dict, alfa: float = ALFA) -> dict:
    ordem = sorted(ps, key=lambda k: ps[k])
    out, parou = {}, False
    for i, k in enumerate(ordem):
        limiar = alfa / (len(ordem) - i)
        rejeita = (not parou) and ps[k] <= limiar
        parou = parou or not rejeita
        out[k] = {"p": ps[k], "limiar_holm": limiar, "rejeita_nula": rejeita}
    return out


def analisar(resultados: dict) -> dict:
    neutra, real = resultados["neutra"], resultados["real"]
    x, y = PRINCIPAL
    princ = bootstrap(diferencas_b(neutra, x, y), 0.0, SEMENTE_BOOT)
    princ["leitura"] = leitura(princ)
    sec = {f"{a}-{b}": bootstrap(diferencas_b(neutra, a, b), 0.0, SEMENTE_BOOT + i + 1) for i, (a, b) in enumerate(SECUNDARIAS)}
    h = holm({k: v["p_bootstrap"] for k, v in sec.items()})
    for k in sec:
        sec[k]["holm"] = h[k]
    desc = {
        "B_real_atencioso-aleatorio": bootstrap(diferencas_b(real, x, y), 0.0, SEMENTE_BOOT + 11),
        "A_neutra_atencioso_contra_aleatorio": bootstrap(taxas_a(neutra, x, y), 0.5, SEMENTE_BOOT + 12),
        "A_real_atencioso_contra_aleatorio": bootstrap(taxas_a(real, x, y), 0.5, SEMENTE_BOOT + 13),
    }
    return {"principal": {"desenho": "B", "condicao": "neutra", "comparacao": f"{x}-{y}", "delta": DELTA, **princ},
            "secundarias_holm": sec, "descritivos": desc}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=str(CFG_PADRAO))
    ap.add_argument("--saida", default=str(Path(__file__).resolve().parents[1] / "artifacts_confirmatoria"))
    ap.add_argument("--ovos", type=int, nargs="*", help="padrao: sementes_confirmatorias do config (160)")
    ap.add_argument("--partidas", type=int, default=M_A, help="M por par no desenho A")
    ap.add_argument("--painel", type=int, default=M_B, help="partidas por bot do painel (desenho B)")
    ap.add_argument("--processos", type=int, default=None)
    ap.add_argument("--fumaca", action="store_true", help="teste do encanamento com ovos do piloto")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    ovos = a.ovos or cfg["sementes_confirmatorias"]
    if a.fumaca:
        # fumaca so com ovos do PILOTO (ja vistos): olhar um pedaco da confirmatoria antes da run e proibido pelo plano
        if not set(ovos) <= set(cfg["sementes_piloto"]) or Path(a.saida).resolve() == (RAIZ / "artifacts_confirmatoria").resolve():
            raise ValueError("fumaca: so ovos do piloto e fora de artifacts_confirmatoria/")
    else:
        if set(ovos) & (set(cfg["sementes_piloto"]) | set(cfg["sementes_antigas"])):
            raise ValueError("ovos da confirmatoria colidem com o piloto ou com runs antigas")
        if sorted(ovos) != sorted(cfg["sementes_confirmatorias"]):
            raise ValueError("a confirmatoria roda com TODAS as sementes registradas antes da run (uma unica analise)")
    saida = Path(a.saida)
    out = executar(cfg, saida, list(ovos), a.partidas, 0, a.painel, a.processos or cfg["processos"],
                   rotulo=cfg["rotulo_partidas_confirmatoria"])
    res = analisar(out["resultados"])
    res.update({"descricao": __doc__.strip().splitlines()[0], "ovos": len(ovos), "M_A": a.partidas, "M_B_por_bot": a.painel,
                "bootstrap": {"reamostragens": BOOT, "semente": SEMENTE_BOOT}, "plano": "docs/PLANO_ANALISE.md"})
    _gravar(saida / "resultado.json", _dump(res))
    p = res["principal"]
    print(f"principal (B, neutra, atencioso - aleatorio): {p['estimativa']:+.4f} IC95 [{p['ic95'][0]:+.4f}, {p['ic95'][1]:+.4f}] "
          f"p={p['p_bootstrap']:.4f} -> {p['leitura']}", flush=True)
    for k, v in res["secundarias_holm"].items():
        print(f"  {k}: {v['estimativa']:+.4f} [{v['ic95'][0]:+.4f}, {v['ic95'][1]:+.4f}] p={v['p_bootstrap']:.4f} "
              f"{'rejeita' if v['holm']['rejeita_nula'] else 'nao rejeita'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
