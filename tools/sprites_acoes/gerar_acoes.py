"""SPRITES_ACOES, missao M1: gera o clipe Comer dos 60 Digimon das formas pelo Aseprite em linha de comando.

Le tools/sprites_acoes/ancoras.json e chama tools/sprites_acoes/gerar.lua uma vez por Digimon, no maximo 4 processos ao mesmo tempo
(V3-D8). Sai fora do git, em remaster/acoes/:
  aseprite/<Nome>_acoes.aseprite
  export/<Nome>.png/.json          (a acao: sombra e personagem; json_array, frameTags, sem corte, caixa do export do UP)
  export/<Nome>_objeto.png/.json   (so a camada comida, nas mesmas tags e ms)
Falha alto: qualquer Digimon que falhe derruba a geracao (codigo de saida 1), com a mensagem do Aseprite.

Uso: python tools/sprites_acoes/gerar_acoes.py [--remaster DIR] [--aseprite EXE] [Nome ...]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ANCORAS = AQUI / "ancoras.json"
LUA = AQUI / "gerar.lua"
REMASTER = AQUI.parents[2] / "remaster"   # D:\Trab\digilab\remaster, ao lado das worktrees
ASEPRITE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe")
PROCESSOS = 4                             # V3-D8: no maximo 4 processos


def parametros(nome: str, e: dict, anc: dict, remaster: Path) -> dict[str, str]:
    """Os --script-param do gerar.lua para um Digimon."""
    acoes = remaster / "acoes"
    pr = {
        # "fonte": um .aseprite derivado (fora do git, em remaster/acoes/bocas/), com os quadros do UP e os ajustados no fim
        "src": str(remaster / e["fonte"]) if "fonte" in e else str(remaster / "aseprite" / e["aseprite"]),
        "caixa": "{},{}".format(*e["caixa"]),
        "pe": str(e["pe_idle"]),
        "out_ase": str(acoes / "aseprite" / f"{nome}_acoes.aseprite"),
        "out_png": str(acoes / "export" / f"{nome}.png"),
        "out_json": str(acoes / "export" / f"{nome}.json"),
        "obj_png": str(acoes / "export" / f"{nome}_objeto.png"),
        "obj_json": str(acoes / "export" / f"{nome}_objeto.json"),
        "orientacao": e["orientacao"],
        "idle": "{},{}".format(e["idle"][0], e["idle"][1] - e["idle"][0] + 1),
    }
    if e["modo"] == "par":
        pr.update(modo="par", carne="{},{}".format(*e["carne"]), seq=";".join(",".join(map(str, q)) for q in e["seq"]))
    elif e["modo"] in ("prova1", "desenhar"):   # desenhar: provisorio pela prova 1 ate a boca desenhada (SA-9)
        pr.update(modo="prova1", boca="{},{}".format(*e["boca"]),
                  escala_inclinacao=str(e["escala_inclinacao"]), recuo_carne=str(e["recuo_carne"]),
                  carne_desl="{},{}".format(*anc["carne_deslocamento"][e["orientacao"]]),
                  tabela=";".join(",".join(map(str, q)) for q in anc["prova1"]))
    else:
        raise ValueError(f"{nome}: modo desconhecido {e['modo']}")
    return pr


def gerar(nome: str, e: dict, anc: dict, remaster: Path, exe: Path) -> tuple[str, str]:
    cmd = [str(exe), "-b"]
    for k, v in parametros(nome, e, anc, remaster).items():
        cmd += ["--script-param", f"{k}={v}"]
    cmd += ["--script", str(LUA)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    saida = (r.stdout + r.stderr).strip()
    if r.returncode != 0 or not r.stdout.strip().startswith("ok "):
        raise RuntimeError(f"{nome}: {saida}")
    return nome, saida


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--remaster", type=Path, default=REMASTER)
    ap.add_argument("--aseprite", type=Path, default=ASEPRITE)
    ap.add_argument("nomes", nargs="*", help="so estes Digimon (padrao: os 60)")
    a = ap.parse_args()
    anc = json.loads(ANCORAS.read_text(encoding="utf-8"))
    dig = anc["digimon"]
    nomes = a.nomes or sorted(dig)
    faltam = [n for n in nomes if n not in dig]
    if faltam:
        raise SystemExit(f"fora do ancoras.json: {faltam}")
    if not a.aseprite.exists():
        raise SystemExit(f"Aseprite nao encontrado: {a.aseprite}")
    for d in ("aseprite", "export"):
        (a.remaster / "acoes" / d).mkdir(parents=True, exist_ok=True)
    erros = []
    with ThreadPoolExecutor(PROCESSOS) as ex:
        futs = [ex.submit(gerar, n, dig[n], anc, a.remaster, a.aseprite) for n in nomes]
        for f in futs:
            try:
                n, s = f.result()
                print(f"{n}: {s}", flush=True)
            except RuntimeError as err:
                erros.append(str(err))
                print(f"FALHOU {err}", flush=True)
    if erros:
        print(f"{len(erros)} de {len(nomes)} falharam", file=sys.stderr)
        return 1
    print(f"{len(nomes)} Digimon gerados em {a.remaster / 'acoes'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
