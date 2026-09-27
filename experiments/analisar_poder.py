"""TAREFA_ANALISE_PODER, Etapas 2-4: componentes de variancia, dois desenhos de medida, curvas de poder.

    python experiments/analisar_poder.py --etapa 2     # artifacts_poder/variancia.json
    python experiments/analisar_poder.py --etapa 3     # artifacts_poder/desenhos.json
    python experiments/analisar_poder.py --etapa 4     # artifacts_poder/curvas_poder.json, tempos.json, recomendacao.json

Le o piloto (artifacts_poder/piloto/). So a comparacao principal (atencioso x aleatorio). So biblioteca padrao.

Componentes (por variante de condicao e por desenho):
  x_ik        pontos da partida k do ovo i (A: atencioso contra aleatorio; B: diferenca pareada
              atencioso - aleatorio contra o mesmo bot, mesma semente)
  y_i         media das partidas do ovo (A: taxa do par; B: diferenca das medias contra o painel)
  s2_1        sigma2_partida_1: variancia de UMA partida em torno da media do ovo (em B, em torno da media do
              par ovo x bot, porque o bot e fixo no painel e nao e ruido)
  s2_ovo      sigma2_ovo = var_entre_ovos(y) - s2_1 / M_efetivo (metodo dos momentos, piso 0)
  ICC         s2_ovo / (s2_ovo + s2_1)
  Var(est)    ~ s2_ovo / N + s2_1 / (N * M_efetivo)   (M_efetivo: partidas por ovo que entram em y)
Conferencia: (i) A: variancia entre as replicas do par principal (pets fixos, sorteios diferentes) contra
s2_1 / M; (ii) Var(est) da formula contra o bootstrap sobre ovos do piloto.
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
DIR = RAIZ / "artifacts_poder"
PIL = DIR / "piloto"
PRINCIPAL = "atencioso|aleatorio"
SEMENTE = 20260927
BOOT = 10000
DELTAS = (0.05, 0.10, 0.15)
NS = (10, 20, 40, 80, 160)
MS = (50, 100, 200, 400)
REPLICAS_SIM = 2000
ALFA = 0.05
PAINEL_BOTS = 32


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(nome: str, o) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    (DIR / nome).write_text(_dump(o) + "\n", encoding="utf-8", newline="\n")


def _ler(nome: str) -> dict:
    return json.loads((PIL / nome).read_text(encoding="utf-8"))


def _var(v: list[float]) -> float:
    return statistics.variance(v) if len(v) > 1 else 0.0


def _boot_var_media(v: list[float], rng: random.Random, n: int = BOOT) -> tuple[float, tuple[float, float]]:
    ms = sorted(statistics.fmean(rng.choices(v, k=len(v))) for _ in range(n))
    return statistics.variance(ms), (ms[int(0.025 * n)], ms[int(0.975 * n) - 1])


# ------------------------------------------------------------------ dados por desenho
def dados_a(por_ovo: dict) -> dict:
    """ovo -> lista de pontos do atencioso contra o aleatorio (partidas principais) e replicas."""
    return {s: {"x": r["A"][PRINCIPAL], "replicas": r["A_replicas_principal"]} for s, r in por_ovo.items()}


def dados_b(por_ovo: dict) -> dict:
    """ovo -> {bot: diferencas pareadas por partida (atencioso - aleatorio, mesma semente)}."""
    out = {}
    for s, r in por_ovo.items():
        at, al = r["B"]["atencioso"], r["B"]["aleatorio"]
        out[s] = {bot: [a - b for a, b in zip(at[bot], al[bot])] for bot in at}
    return out


def componentes_a(d: dict, rng: random.Random) -> dict:
    ys = [statistics.fmean(v["x"]) for v in d.values()]
    m = len(next(iter(d.values()))["x"])
    s2_1 = statistics.fmean(_var(v["x"]) for v in d.values())
    s2_ovo_bruto = _var(ys) - s2_1 / m
    s2_ovo = max(0.0, s2_ovo_bruto)
    # replicas: pets fixos, so o sorteio das partidas muda
    var_rep = statistics.fmean(_var([statistics.fmean(v["x"])] + [statistics.fmean(r) for r in v["replicas"]])
                               for v in d.values())
    n = len(ys)
    var_boot, ic = _boot_var_media(ys, rng)
    return {"N": n, "M_efetivo": m, "efeito_estimado": statistics.fmean(ys) - 0.5, "media_taxa": statistics.fmean(ys),
            "ic95_bootstrap_ovos_taxa": ic, "sigma2_partida_1": s2_1, "sigma2_ovo": s2_ovo,
            "sigma2_ovo_bruto": s2_ovo_bruto, "ICC": s2_ovo / (s2_ovo + s2_1) if s2_ovo + s2_1 else 0.0,
            "var_entre_ovos_y": _var(ys),
            "conferencia_replicas": {"var_entre_replicas_mesmos_pets": var_rep, "formula_s2_1_sobre_M": s2_1 / m,
                                     "razao": var_rep / (s2_1 / m) if s2_1 else None,
                                     "amplitude_media_das_replicas": statistics.fmean(
                                         max(statistics.fmean(r) for r in [v["x"]] + v["replicas"])
                                         - min(statistics.fmean(r) for r in [v["x"]] + v["replicas"]) for v in d.values())},
            "conferencia_var_estimador": {"formula": s2_ovo / n + s2_1 / (n * m), "bootstrap_ovos": var_boot},
            "fracao_var_estimador_por_partidas": (s2_1 / (n * m)) / (s2_ovo / n + s2_1 / (n * m)) if s2_ovo + s2_1 else None}


def componentes_b(d: dict, rng: random.Random) -> dict:
    ys, s2s = [], []
    m_bot = len(next(iter(next(iter(d.values())).values())))
    nbots = len(next(iter(d.values())))
    for s, bots in d.items():
        ys.append(statistics.fmean(statistics.fmean(z) for z in bots.values()))
        s2s.append(statistics.fmean(_var(z) for z in bots.values()))
    s2_1 = statistics.fmean(s2s)
    m_ef = nbots * m_bot
    s2_ovo_bruto = _var(ys) - s2_1 / m_ef
    s2_ovo = max(0.0, s2_ovo_bruto)
    n = len(ys)
    var_boot, ic = _boot_var_media(ys, rng)
    return {"N": n, "M_efetivo": m_ef, "partidas_por_bot": m_bot, "bots": nbots, "efeito_estimado": statistics.fmean(ys),
            "ic95_bootstrap_ovos_diferenca": ic, "sigma2_partida_1": s2_1, "sigma2_ovo": s2_ovo,
            "sigma2_ovo_bruto": s2_ovo_bruto, "ICC": s2_ovo / (s2_ovo + s2_1) if s2_ovo + s2_1 else 0.0,
            "var_entre_ovos_y": _var(ys),
            "conferencia_var_estimador": {"formula": s2_ovo / n + s2_1 / (n * m_ef), "bootstrap_ovos": var_boot},
            "fracao_var_estimador_por_partidas": (s2_1 / (n * m_ef)) / (s2_ovo / n + s2_1 / (n * m_ef)) if s2_ovo + s2_1 else None}


def etapa2() -> dict:
    out = {"descricao": "Etapa 2: componentes de variancia (comparacao principal atencioso x aleatorio)",
           "semente_bootstrap": SEMENTE, "reamostragens": BOOT, "variantes": {}}
    for var in ("neutra", "real"):
        por_ovo = _ler(f"partidas_{var}.json")["por_ovo"]
        rng = random.Random(SEMENTE)
        out["variantes"][var] = {"A": componentes_a(dados_a(por_ovo), rng), "B": componentes_b(dados_b(por_ovo), rng)}
    _gravar("variancia.json", out)
    return out


# ------------------------------------------------------------------ Etapa 3: os dois desenhos com os mesmos dados
def etapa3() -> dict:
    v = json.loads((DIR / "variancia.json").read_text(encoding="utf-8"))
    out = {"descricao": "Etapa 3: desenho A (confronto direto) x B (painel fixo), mesmos pets do piloto", "variantes": {}}
    for var, c in v["variantes"].items():
        a, b = c["A"], c["B"]
        out["variantes"][var] = {
            "A": {"efeito": a["efeito_estimado"], "se_bootstrap": math.sqrt(a["conferencia_var_estimador"]["bootstrap_ovos"]),
                  "ic95_taxa": a["ic95_bootstrap_ovos_taxa"], "partidas_por_ovo": a["M_efetivo"],
                  "razao_efeito_se": a["efeito_estimado"] / math.sqrt(a["conferencia_var_estimador"]["bootstrap_ovos"])},
            "B": {"efeito": b["efeito_estimado"], "se_bootstrap": math.sqrt(b["conferencia_var_estimador"]["bootstrap_ovos"]),
                  "ic95_diferenca": b["ic95_bootstrap_ovos_diferenca"], "partidas_por_ovo": 2 * b["M_efetivo"],
                  "razao_efeito_se": b["efeito_estimado"] / math.sqrt(b["conferencia_var_estimador"]["bootstrap_ovos"])},
            "leitura": "A mede atencioso contra aleatorio; B mede quanto cada um ganha contra o mesmo painel de bots "
                       "(diferenca pareada por ovo). A escolha do principal e do Matheus.",
        }
    _gravar("desenhos.json", out)
    return out


# ------------------------------------------------------------------ Etapa 4: poder
def _betacf(a, b, x):
    mx, eps, fp = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = fp if abs(d) < fp else d
    d = 1.0 / d
    h = d
    for m in range(1, mx + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = fp if abs(d) < fp else d
        c = 1.0 + aa / c; c = fp if abs(c) < fp else c
        d = 1.0 / d; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = fp if abs(d) < fp else d
        c = 1.0 + aa / c; c = fp if abs(c) < fp else c
        d = 1.0 / d; de = d * c; h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    return bt * _betacf(a, b, x) / a if x < (a + 1) / (a + b + 2) else 1 - bt * _betacf(b, a, 1 - x) / b


def t_cdf(t: float, df: int) -> float:
    x = df / (df + t * t)
    p = 0.5 * _ibeta(df / 2, 0.5, x)
    return 1 - p if t > 0 else p


def t_crit(df: int, alfa: float = ALFA) -> float:
    lo, hi = 0.0, 50.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if 1 - t_cdf(mid, df) > alfa / 2 else (lo, mid)
    return (lo + hi) / 2


def poder_formula(delta: float, s2_ovo: float, s2_1: float, n: int, m_ef: int) -> float:
    se = math.sqrt(s2_ovo / n + s2_1 / (n * m_ef))
    tc, nd = t_crit(n - 1), statistics.NormalDist()
    return nd.cdf(delta / se - tc) + nd.cdf(-delta / se - tc)


def poder_simulado(delta: float, s2_ovo: float, s2_1: float, n: int, m_ef: int, rng: random.Random) -> float:
    """y_i ~ N(delta, s2_ovo) + N(0, s2_1/M): teste t bilateral de media 0 sobre os N ovos."""
    tc, so, sm, rej = t_crit(n - 1), math.sqrt(s2_ovo), math.sqrt(s2_1 / m_ef), 0
    for _ in range(REPLICAS_SIM):
        ys = [delta + rng.gauss(0, so) + rng.gauss(0, sm) for _ in range(n)]
        sd = statistics.stdev(ys)
        if sd > 0 and abs(statistics.fmean(ys) / (sd / math.sqrt(n))) > tc:
            rej += 1
    return rej / REPLICAS_SIM


def etapa4() -> dict:
    v = json.loads((DIR / "variancia.json").read_text(encoding="utf-8"))
    meta = json.loads((PIL / "meta.json").read_text(encoding="utf-8"))
    tp = meta["tempos"]
    n_vidas = len(meta["ovos"]) * 5
    seg_vida = tp["vidas_s"] / n_vidas                       # parede, com o numero de processos do piloto
    # tempo de parede por partida com o pool do piloto (run_poder divide o tempo de parede pelo total de partidas)
    seg_partida = statistics.fmean([tp["segundos_por_partida_neutra"], tp["segundos_por_partida_real"]])
    tempos = {"processos": tp["processos"], "segundos_por_vida_parede": seg_vida,
              "segundos_por_partida_parede": seg_partida,
              "fonte": "artifacts_poder/piloto/meta.json (tempos medidos no piloto)"}
    _gravar("tempos.json", tempos)

    def custo_h(des: str, n: int, m: int) -> dict:
        vidas = 5 * n * seg_vida
        if des == "A":            # M = partidas por par; principal + os 9 pares secundarios
            princ, todas = n * m, n * m * 10
        else:                     # M = partidas por bot do painel (32 bots); 2 bracos no principal, 5 no total
            princ, todas = n * m * PAINEL_BOTS * 2, n * m * PAINEL_BOTS * 5
        return {"horas_principal": (2 * n * seg_vida + princ * seg_partida) / 3600,
                "horas_completa": (vidas + todas * seg_partida) / 3600}

    rng = random.Random(SEMENTE)
    curvas = {"descricao": "Etapa 4: curvas de poder (alfa 0,05 bilateral), formula e simulacao parametrica",
              "replicas_simulacao": REPLICAS_SIM, "semente": SEMENTE, "deltas": DELTAS, "N": NS, "M": MS,
              "leitura_M": {"A": "partidas por par (atencioso x aleatorio)",
                            "B": f"partidas por bot do painel ({PAINEL_BOTS} bots, por pet)"},
              "variantes": {}}
    recomendacao = {"descricao": "celula mais barata (horas da confirmatoria completa) com poder >= 0,8 para delta 0,10",
                    "variantes": {}}
    for var, c in v["variantes"].items():
        curvas["variantes"][var] = {}
        recomendacao["variantes"][var] = {}
        for des in ("A", "B"):
            comp = c[des]
            s2o, s21 = comp["sigma2_ovo"], comp["sigma2_partida_1"]
            celulas = []
            for d in DELTAS:
                for n in NS:
                    for m in MS:
                        m_ef = m if des == "A" else m * PAINEL_BOTS
                        celulas.append({"delta": d, "N": n, "M": m,
                                        "poder_formula": poder_formula(d, s2o, s21, n, m_ef),
                                        "poder_simulado": poder_simulado(d, s2o, s21, n, m_ef, rng),
                                        **custo_h(des, n, m)})
            curvas["variantes"][var][des] = celulas
            ok = [x for x in celulas if x["delta"] == 0.10 and min(x["poder_formula"], x["poder_simulado"]) >= 0.8]
            recomendacao["variantes"][var][des] = min(ok, key=lambda x: x["horas_completa"]) if ok else None
            print(var, des, "recomendada:", recomendacao["variantes"][var][des], flush=True)
    _gravar("curvas_poder.json", curvas)
    _gravar("recomendacao.json", recomendacao)
    return recomendacao


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", type=int, choices=(2, 3, 4), required=True)
    a = ap.parse_args(argv)
    r = {2: etapa2, 3: etapa3, 4: etapa4}[a.etapa]()
    if a.etapa != 4:
        print(_dump(r)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
