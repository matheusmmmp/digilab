"""A grade da fase R2-4 (as cartas; docs/PLANO_EQUILIBRIO_COMBATE_TR_R2.md, DR2-4): cada efeito candidato (--cartas da bancada) medido no I-4
(fase4_progressao.ts --parte i4), so nas sementes de calibracao da rodada 2, em no maximo 4 processos. A escolha (a regra do plano, secao
4): por carta, entre os pontos com o efeito medio >= 0,03, o de menor mudanca (o ritmo mais perto do do relogio; o guts e o teto mais
perto dos de hoje); sem nenhum, a carta fica como esta (nao fecha), e o relato da o ponto de maior efeito. Os JSON completos vao para <saida>/completo/ (fora do git); o resumo, para
<saida>/resumo.json.
uso (em web/app): python scripts/equilibrio_tr/grade_cartas_r2.py --saida scripts/medicoes/equilibrio_tr/r2_4/grade1 '{"carta_foco":{"ritmo":12}}' ..."""
import argparse, json, os, subprocess
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--saida", required=True)
ap.add_argument("--faixa", default="calibracao2")
ap.add_argument("pontos", nargs="+")
a = ap.parse_args()
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
C = os.path.join(a.saida, "completo")
os.makedirs(C, exist_ok=True)
npx = "npx.cmd" if os.name == "nt" else "npx"


def roda(i_pt):
    i, pt = i_pt
    p = os.path.join(C, f"p{i}.json")
    if not os.path.exists(p):
        r = subprocess.run([npx, "tsx", "scripts/equilibrio_tr/fase4_progressao.ts", "--faixa", a.faixa, "--parte", "i4", "--cartas", pt,
                            "--saida", p], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr[-2000:])
    m = json.load(open(p, encoding="utf-8"))["metas"]["I-4"]["cartas"]
    return {"cartas": json.loads(pt), "efeito": {k: v["efeito_medio"] for k, v in m.items()},
            "por_arena": {k: {ar: x["efeito"] for ar, x in v["arenas"].items()} for k, v in m.items()}}


with ThreadPoolExecutor(4) as ex:
    rs = list(ex.map(roda, enumerate(a.pontos)))
json.dump({"gerado_por": "web/app/scripts/equilibrio_tr/grade_cartas_r2.py", "faixa": a.faixa, "pontos": rs},
          open(os.path.join(a.saida, "resumo.json"), "w", encoding="utf-8"), indent=1)
for r in rs:
    print(json.dumps(r["cartas"]), {k: round(v, 4) for k, v in r["efeito"].items()})
