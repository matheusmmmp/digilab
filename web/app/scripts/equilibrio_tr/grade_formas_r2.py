"""A grade da fase R2-1 (as formas; docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md): cada variante das listas (variantes_fase2.ts) medida nas
metas das formas (fase2_formas.ts: F-1 a F-7) e no T-2 (fase1_relogio.ts), so nas sementes de calibracao da rodada 2, em no maximo 4
processos. A nota (registrada antes de rodar) e a soma da distancia de cada meta a faixa dela:
  F-1: cada forma ate [0,40; 0,60]; F-2: o que passa de 0,20; F-4: cada linha do Champion e o sereno x arisco ate [0,40; 0,60]; F-5: o
  Champion e o Ultimate ate [0,45; 0,55]; F-6: o que cada passiva passa de 0,10; F-7: cada sombria ate [0,45; 0,65]; T-2: o que o pior
  par passa de 0,05. F-3 reprovado soma 1.
uso (em web/app): python scripts/equilibrio_tr/grade_formas_r2.py --saida scripts/medicoes/equilibrio_tr/r2_1/grade1 [variante ...]
  (sem variante: o candidato como esta, "base"). As variantes vao por cima das listas da primeira rodada (--listas v14r1): a escolhida
  (r2c_b) ja entrou nas LISTAS_V14"""
import argparse, json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--saida", required=True)
ap.add_argument("--faixa", default="calibracao2")
ap.add_argument("variantes", nargs="*")
a = ap.parse_args()
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.makedirs(a.saida, exist_ok=True)
npx = "npx.cmd" if os.name == "nt" else "npx"
vs = a.variantes or ["base"]


def tarefa(v, qual):
    var = [] if v == "base" else ["--variante", v]
    if qual == "formas":
        c = ["scripts/equilibrio_tr/fase2_formas.ts", "--faixa", a.faixa, "--listas", "v14r1", *var]
    else:
        c = ["scripts/equilibrio_tr/fase1_relogio.ts", "--faixa", a.faixa, "--base", "v14", "--listas", "v14r1", *var]
    p = f"{a.saida}/{v}_{qual}.json"
    if not os.path.exists(p):
        r = subprocess.run([npx, "tsx", *c, "--saida", p], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(" ".join(c) + "\n" + r.stderr[-2000:])
    return p


fx = lambda x, lo, hi: max(0.0, lo - x, x - hi)


def nota(v):
    f = json.load(open(f"{a.saida}/{v}_formas.json", encoding="utf-8"))["metas"]
    t = json.load(open(f"{a.saida}/{v}_relogio.json", encoding="utf-8"))["metas"]
    p = {"F-1": sum(fx(x, .4, .6) for x in f["F-1"]["forca"].values()), "F-2": max(0.0, f["F-2"]["distancia"] - .2),
         "F-3": 0.0 if f["F-3"]["passa"] else 1.0,
         "F-4": sum(fx(x, .4, .6) for x in f["F-4"]["champion"].values()) + fx(f["F-4"]["rookie_sereno_x_arisco"], .4, .6),
         "F-5": fx(f["F-5"]["champion_cacador_x_perto"], .45, .55) + fx(f["F-5"]["ultimate_longe_x_perto"], .45, .55),
         "F-6": sum(max(0.0, abs(x["efeito"]) - .1) for x in f["F-6"]["passivas"].values()),
         "F-7": sum(fx(x, .45, .65) for x in f["F-7"]["forca"].values()),
         "T-2": max(0.0, t["T-2"]["no_limite_pior_par"] - .05)}
    return round(sum(p.values()), 4), {k: round(x, 3) for k, x in p.items()}, {k: f[k]["passa"] for k in f} | {"T-2": t["T-2"]["passa"]}


with ThreadPoolExecutor(4) as ex:
    list(ex.map(lambda x: tarefa(*x), [(v, q) for v in vs for q in ("formas", "relogio")]))
for v in sorted(vs, key=lambda v: nota(v)[0]):
    n, p, ok = nota(v)
    print(f"{v:26s} nota {n:6.3f}  {p}  passam: {[k for k, x in ok.items() if x]}")
