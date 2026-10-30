"""A grade da fase R2-3 (os lideres; docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md): cada variante das listas dos lideres (variantes_lideres_r2.ts;
"base" = a lista do candidato) com o fator da arena dela na grade 0,6 a 3,0, medida no G-1 (fase4_progressao.ts --parte g1), so nas
sementes de calibracao da rodada 2, em no maximo 4 processos. A escolha (registrada antes de rodar, a da fase 4): entre os pontos que
passam o G-1 da arena (sem treino <= 0,05, com o tipico >= 0,80, a pior forma >= 0,50), o de maior folga min(0,05 - sem, com - 0,80,
pior - 0,50); sem nenhum, o de maior folga (nao fecha). Os JSON completos vao para <saida>/completo/ (fora do git); o resumo, para
<saida>/resumo.json.
uso (em web/app): python scripts/equilibrio_tr/grade_lideres_r2.py --saida scripts/medicoes/equilibrio_tr/r2_3/grade1 --arena cidadela base l1_cid_carrega"""
import argparse, json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--saida", required=True)
ap.add_argument("--faixa", default="calibracao2")
ap.add_argument("--arena", required=True)
ap.add_argument("variantes", nargs="+")
a = ap.parse_args()
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
C = os.path.join(a.saida, "completo")
os.makedirs(C, exist_ok=True)
npx = "npx.cmd" if os.name == "nt" else "npx"
FATORES = [round(.6 + .1 * i, 1) for i in range(25)]


def roda(pt):
    v, f = pt
    p = os.path.join(C, f"{a.arena}_{v}_f{f}.json")
    if not os.path.exists(p):
        var = [] if v == "base" else ["--variante-lider", v]
        r = subprocess.run([npx, "tsx", "scripts/equilibrio_tr/fase4_progressao.ts", "--faixa", a.faixa, "--parte", "g1", *var,
                            "--fatores", json.dumps({"lider": {a.arena: f}}), "--saida", p], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr[-2000:])
    x = json.load(open(p, encoding="utf-8"))["metas"]["G-1"]["arenas"][a.arena]
    return {"variante": v, "fator": f, "sem": x["sem"], "com": x["com"], "pior": x["pior"], "pior_forma": x["pior_forma"], "passa": x["passa"],
            "folga": round(min(.05 - x["sem"], x["com"] - .8, x["pior"] - .5), 4)}


with ThreadPoolExecutor(4) as ex:
    rs = list(ex.map(roda, [(v, f) for v in a.variantes for f in FATORES]))
res = os.path.join(a.saida, "resumo.json")
antigo = json.load(open(res, encoding="utf-8")) if os.path.exists(res) else {"gerado_por": "web/app/scripts/equilibrio_tr/grade_lideres_r2.py", "faixa": a.faixa, "arenas": {}}
antigo["arenas"][a.arena] = rs
json.dump(antigo, open(res, "w", encoding="utf-8"), indent=1)
for v in a.variantes:
    pts = [r for r in rs if r["variante"] == v]
    ok = [r for r in pts if r["passa"]]
    b = max(ok or pts, key=lambda r: r["folga"])
    print(f"{a.arena} {v:18s} {'PASSA' if ok else 'nao fecha'} fator {b['fator']} sem {b['sem']} com {b['com']} pior {b['pior']} ({b['pior_forma']}) folga {b['folga']}")
