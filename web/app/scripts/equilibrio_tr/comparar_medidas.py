"""A prova de reproducao da R3-0 (docs/PLANO_EQUILIBRIO_COMBATE_TR_R3.md, secao 3): confere, campo a campo, os JSON de duas medidas inteiras
(medir_tudo.py), menos o que muda de uma rodada para outra sem mudar a luta: a data, o commit, a versao do Node e o custo em segundos.
Falha alto (saida 1) na primeira lista de diferencas nao vazia; os dois diretorios tem de ter os mesmos arquivos.
uso (em web/app): python scripts/equilibrio_tr/comparar_medidas.py <dir_a> <dir_b> [--saida <arquivo.txt>]"""
import argparse
import json
import os
import sys

IGNORAR = {"data", "commit", "node", "custo_s"}


def diferencas(a, b, onde):
    """as diferencas entre dois valores JSON, como linhas 'caminho: a != b'"""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k in IGNORAR:
                continue
            if k not in a or k not in b:
                out.append(f"{onde}.{k}: so em {'b' if k not in a else 'a'}")
            else:
                out += diferencas(a[k], b[k], f"{onde}.{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{onde}: listas de tamanho {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diferencas(x, y, f"{onde}[{i}]")]
    return [] if a == b and type(a) is type(b) else [f"{onde}: {a!r} != {b!r}"]


ap = argparse.ArgumentParser()
ap.add_argument("dir_a")
ap.add_argument("dir_b")
ap.add_argument("--saida", default=None)
x = ap.parse_args()
nomes_a = sorted(f for f in os.listdir(x.dir_a) if f.endswith(".json"))
nomes_b = sorted(f for f in os.listdir(x.dir_b) if f.endswith(".json"))
if nomes_a != nomes_b:
    sys.exit(f"os arquivos nao sao os mesmos: {nomes_a} x {nomes_b}")
linhas, total = [f"comparar_medidas: {x.dir_a} x {x.dir_b} (ignorados: {', '.join(sorted(IGNORAR))})"], 0
for n in nomes_a:
    with open(os.path.join(x.dir_a, n), encoding="utf-8") as fa, open(os.path.join(x.dir_b, n), encoding="utf-8") as fb:
        d = diferencas(json.load(fa), json.load(fb), n)
    total += len(d)
    linhas.append(f"{n}: {'igual' if not d else str(len(d)) + ' diferencas'}")
    linhas += ["  " + s for s in d[:50]]
linhas.append(f"total: {len(nomes_a)} arquivos, {total} diferencas")
texto = "\n".join(linhas) + "\n"
if x.saida:
    with open(x.saida, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
print(texto, end="")
sys.exit(1 if total else 0)
