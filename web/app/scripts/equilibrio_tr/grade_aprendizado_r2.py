"""A grade da fase R2-2 (o aprendizado proprio do tempo real, DR2-5; docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md): cada ponto (alfa, prior) medido
no P-3 e no P-4 (fase3_estagio.ts --parte p34 --aprendizado), so nas sementes de calibracao da rodada 2, em no maximo 4 processos.
A nota (registrada antes de rodar): a soma da distancia do P-3 do Champion e do Ultimate ate [0,55; 0,70]; o ponto com o P-4 abaixo de
0,8 em algum estagio nao conta. Os JSON completos vao para <saida>/completo/ (fora do git; o relato os compacta num .tar.gz por fase);
o resumo de todos os pontos vai para <saida>/resumo.json.
uso (em web/app): python scripts/equilibrio_tr/grade_aprendizado_r2.py --saida scripts/medicoes/equilibrio_tr/r2_2/grade1 --alfa .2 .1 --prior 0 .05"""
import argparse, json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--saida", required=True)
ap.add_argument("--faixa", default="calibracao2")
ap.add_argument("--alfa", nargs="+", type=float, required=True)
ap.add_argument("--prior", nargs="+", type=float, required=True)
ap.add_argument("--bonus", nargs="+", type=float, default=[None])
ap.add_argument("--limiar", nargs="+", type=float, default=[None])
a = ap.parse_args()
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
C = os.path.join(a.saida, "completo")
os.makedirs(C, exist_ok=True)
npx = "npx.cmd" if os.name == "nt" else "npx"
pontos = [(al, pr, bo, li) for al in a.alfa for pr in a.prior for bo in a.bonus for li in a.limiar]


def roda(pt):
    al, pr, bo, li = pt
    apr = {"alfa": al, "prior": pr, **({"bonus": bo} if bo is not None else {}), **({"limiar": li} if li is not None else {})}
    p = os.path.join(C, f"a{al}_p{pr}" + (f"_b{bo}" if bo is not None else "") + (f"_l{li}" if li is not None else "") + ".json")
    if not os.path.exists(p):
        r = subprocess.run([npx, "tsx", "scripts/equilibrio_tr/fase3_estagio.ts", "--faixa", a.faixa, "--parte", "p34",
                            "--aprendizado", json.dumps(apr), "--saida", p], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr[-2000:])
    m = json.load(open(p, encoding="utf-8"))["metas"]
    p3, p4 = m["P-3"], m["P-4"]
    d = lambda x: max(0.0, .55 - x, x - .70)
    return {"alfa": al, "prior": pr, "bonus": bo, "limiar": li, "p3_champion": p3["champion"]["media"], "p3_ultimate": p3["ultimate"]["media"],
            "p3_formas": {**p3["champion"]["formas"], **p3["ultimate"]["formas"]},
            "p4_champion": p4["champion"]["qualificados"], "p4_ultimate": p4["ultimate"]["qualificados"],
            "nota": round(d(p3["champion"]["media"]) + d(p3["ultimate"]["media"]), 4),
            "p4_ok": p4["champion"]["qualificados"] >= .8 and p4["ultimate"]["qualificados"] >= .8, "p3_passa": p3["passa"]}


with ThreadPoolExecutor(4) as ex:
    rs = list(ex.map(roda, pontos))
json.dump({"gerado_por": "web/app/scripts/equilibrio_tr/grade_aprendizado_r2.py", "faixa": a.faixa, "pontos": rs},
          open(os.path.join(a.saida, "resumo.json"), "w", encoding="utf-8"), indent=1)
for r in sorted(rs, key=lambda r: (not r["p4_ok"], r["nota"])):
    print(f"alfa {r['alfa']:<5} prior {r['prior']:<5} bonus {r['bonus']} limiar {r['limiar']}  P-3 {r['p3_champion']:.3f} / {r['p3_ultimate']:.3f}  P-4 {r['p4_champion']:.3f} / {r['p4_ultimate']:.3f}  nota {r['nota']:.3f}{'' if r['p4_ok'] else '  (P-4 cai)'}")
