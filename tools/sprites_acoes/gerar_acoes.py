"""SPRITES_ACOES, missao M1: gera as acoes do lote 1 (Comer, Feliz, Sacudir, Chamar, Emburrar) dos 60 Digimon das formas pelo
Aseprite em linha de comando.

Le tools/sprites_acoes/ancoras.json (o Comer), tools/sprites_acoes/lote1.json (as outras quatro) e chama tools/sprites_acoes/gerar.lua uma vez por Digimon, no maximo 4 processos ao mesmo tempo
(V3-D8). Sai fora do git, em remaster/acoes/:
  aseprite/<Nome>_acoes.aseprite
  export/<Nome>.png/.json          (as acoes: sombra e personagem, as 5 tags; json_array, frameTags, sem corte, caixa do export do UP)
  export/<Nome>_objeto.png/.json   (so a camada comida, so a tag Comer, nos mesmos ms)
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
LOTE1 = AQUI / "lote1.json"
ACOES_LOTE1 = ("Feliz", "Sacudir", "Chamar", "Emburrar")   # a ordem das tags depois do Comer
REMASTER = AQUI.parents[2] / "remaster"   # D:\Trab\digilab\remaster, ao lado das worktrees
ASEPRITE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe")
PROCESSOS = 4                             # V3-D8: no maximo 4 processos


def quadros_lote1(nome: str, e: dict, lote: dict, remaster: Path) -> dict[str, str]:
    """Os --script-param acao_<Tag> de um Digimon: os quadros de cada acao do lote1.json, com o ajuste de pulo dele."""
    ajuste = lote["ajustes"].get(nome, {})
    desconhecidos = set(ajuste) - {"escala_pulo", "motivo"}
    if desconhecidos:
        raise ValueError(f"{nome}: ajuste desconhecido {sorted(desconhecidos)}")
    escala = ajuste.get("escala_pulo", 1.0)
    if not 0 < escala <= 1:
        raise ValueError(f"{nome}: escala_pulo {escala} fora de (0, 1]")
    if set(lote["acoes"]) != set(ACOES_LOTE1):
        raise ValueError(f"lote1.json: acoes {sorted(lote['acoes'])}, esperado {sorted(ACOES_LOTE1)}")
    poses = lote["poses"].get(nome)
    if poses is None:
        raise ValueError(f"{nome}: sem poses no lote1.json (os quadros do UP de cada papel, conferidos a mao)")
    up = json.loads((remaster / "export" / f"{nome}.json").read_text(encoding="utf-8"))
    t = {x["name"]: x for x in up["meta"]["frameTags"]}["Idle"]
    ms_idle = [int(f["duration"]) for f in up["frames"][t["from"]:t["to"] + 1]]
    if len(ms_idle) != e["idle"][1] - e["idle"][0] + 1:
        raise ValueError(f"{nome}: o Idle do export tem {len(ms_idle)} quadros, o ancoras.json diz {e['idle']}")
    i0, n = e["idle"][0], len(ms_idle)

    def resolver(fonte) -> tuple[int, int]:
        """(quadro do UP, quadro da sombra): um int e o deslocamento no Idle (a sombra dele); "pose:<papel>" e o quadro do papel no
        poses do Digimon (a sombra do 1o quadro do Idle, como no Comer par)."""
        if isinstance(fonte, int):
            return i0 + fonte % n, i0 + fonte % n
        if isinstance(fonte, str) and fonte.startswith("pose:"):
            papel = fonte[5:]
            if papel not in poses:
                raise ValueError(f"{nome}: sem a pose {papel!r} no lote1.json")
            return int(poses[papel]), i0
        raise ValueError(f"{nome}: fonte de quadro invalida {fonte!r}")

    pr = {}
    for acao in ACOES_LOTE1:
        a = lote["acoes"][acao]
        if "todo_idle" in a:
            ti = a["todo_idle"]
            qs = [[i, ti["dx"], ti["dy"], ti["sx"], ti["sy"], ti["k"], int(round(ms * ti["ms_fator"])), ti["abaixar"], ti["espelho"]]
                  for i, ms in enumerate(ms_idle)]
        else:
            qs = [list(q) for q in a["quadros"]]
        for i, q in enumerate(qs):
            if len(q) != 9 or not isinstance(q[6], int) or q[6] <= 0 or q[8] not in (0, 1):
                raise ValueError(f"{nome} {acao}: quadro invalido {q}")
            q[2] = int(round(q[2] * escala))   # o pulo (dy) na fracao do ajuste
            q[0], sombra = resolver(q[0])
            qs[i] = q + [sombra]
        pr["acao_" + acao] = ";".join(",".join(map(str, q)) for q in qs)
    return pr


def parametros(nome: str, e: dict, anc: dict, remaster: Path, lote: dict) -> dict[str, str]:
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
    pr.update(quadros_lote1(nome, e, lote, remaster))
    return pr


def gerar(nome: str, e: dict, anc: dict, remaster: Path, exe: Path, lote: dict) -> tuple[str, str]:
    cmd = [str(exe), "-b"]
    for k, v in parametros(nome, e, anc, remaster, lote).items():
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
    lote = json.loads(LOTE1.read_text(encoding="utf-8"))
    fora = set(lote["ajustes"]) - set(dig)
    if fora:
        raise SystemExit(f"lote1.json: ajustes fora do ancoras.json: {sorted(fora)}")
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
        futs = [ex.submit(gerar, n, dig[n], anc, a.remaster, a.aseprite, lote) for n in nomes]
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
