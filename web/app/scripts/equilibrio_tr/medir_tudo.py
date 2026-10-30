"""A medida de todas as metas da rodada de equilibrio do tempo real com o candidato v14 (as bancadas das fases 1 a 4, as mesmas opcoes da
reconferencia da fase 4 e da conferencia unica), em no maximo 4 processos. Cada bancada grava o JSON dela em <saida>/.
uso (em web/app): python scripts/equilibrio_tr/medir_tudo.py --faixa calibracao2 --saida scripts/medicoes/equilibrio_tr/r2_0
  [--extra-fase2 "--variante x"] (opcoes a mais para a bancada da fase 2, por exemplo uma variante das listas)"""
import argparse, os, shlex, subprocess
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--faixa", required=True)
ap.add_argument("--saida", required=True)
ap.add_argument("--extra-fase2", default="")
a = ap.parse_args()
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
B, F, D = "scripts/equilibrio_tr/", ["--faixa", a.faixa], a.saida
cmds = [[B + "fase1_relogio.ts", *F, "--base", "v14", "--listas", "v14", "--saida", D + "/relogio.json"],
        [B + "fase2_formas.ts", *F, "--listas", "v14", *shlex.split(a.extra_fase2), "--saida", D + "/formas.json"]]
cmds += [[B + "fase3_estagio.ts", *F, "--parte", p, "--saida", f"{D}/estagio_{p}.json"] for p in ["p1", "p2", "p34"]]
cmds += [[B + "fase4_progressao.ts", *F, "--parte", p, "--saida", f"{D}/{p}.json"] for p in ["g1", "g2", "g3", "g4", "g5", "g6", "i2", "i3", "i4", "i5"]]
npx = "npx.cmd" if os.name == "nt" else "npx"


def roda(c):
    r = subprocess.run([npx, "tsx", *c], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(" ".join(c) + "\n" + r.stderr[-2000:])
    return c[0].split("/")[-1] + (" " + c[c.index("--parte") + 1] if "--parte" in c else "")


with ThreadPoolExecutor(4) as ex:
    for x in ex.map(roda, cmds):
        print("ok", x, flush=True)
