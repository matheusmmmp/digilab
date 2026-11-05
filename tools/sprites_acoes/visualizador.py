"""SPRITES_ACOES, missao M1: o visualizador das acoes novas, para o Matheus ver o Comer antes de ele ir para o jogo (2026-11-04).

Copia a pagina do atlas do UP (remaster/fonte/site/atlas_digimon_up.html) com os 60 Digimon das formas, cada um com as animacoes do
export do UP mais as novas (Comer, com a comida por cima, e Comer_sem_objeto), e o modo de cada um no ancoras.json. A saida fica FORA
DO GIT, em remaster/acoes/visualizador/site (sao quadros do UP). Nada daqui entra no jogo: o Assets/digilab_atlas_up_clipes.json so e
regerado depois que o Matheus aprova aqui. Fora do pacote digilab/, entao pode usar Pillow. Falha alto.

Uso: python -I tools/sprites_acoes/visualizador.py   (depois do gerar_acoes.py; sirva a saida com python -m http.server dentro dela)
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]                                  # D:\Trab\digilab, ao lado das worktrees
EXPORT_UP = RAIZ / "remaster" / "export"
EXPORT_ACOES = RAIZ / "remaster" / "acoes" / "export"
PAGINA = RAIZ / "remaster" / "fonte" / "site" / "atlas_digimon_up.html"
CATALOGO = RAIZ / "Assets" / "catalogo_sprites_up.json"
ANCORAS = AQUI / "ancoras.json"
SAIDA = RAIZ / "remaster" / "acoes" / "visualizador" / "site"
COLUNAS = 8
TAM = 64                                                 # lado da miniatura


def quadros(json_path: Path, png_path: Path) -> tuple[list[tuple[Image.Image, int]], list[dict], tuple[int, int]]:
    j = json.loads(json_path.read_text(encoding="utf-8"))
    folha = Image.open(png_path).convert("RGBA")
    qs, dims = [], set()
    for f in j["frames"]:
        if f["rotated"] or f["trimmed"]:
            raise ValueError(f"{json_path.name}: quadro rotacionado ou cortado")
        r = f["frame"]
        dims.add((r["w"], r["h"]))
        qs.append((folha.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"])), int(f["duration"])))
    if len(dims) != 1:
        raise ValueError(f"{json_path.name}: quadros de tamanhos diferentes {dims}")
    return qs, j["meta"]["frameTags"], dims.pop()


def main() -> int:
    cat = json.loads(CATALOGO.read_text(encoding="utf-8"))
    digimons = sorted({e["digimon"] for e in cat["formas"].values()})
    anc = json.loads(ANCORAS.read_text(encoding="utf-8"))["digimon"]
    faltam = sorted(set(digimons) - set(anc))
    if faltam:
        raise ValueError(f"fora do ancoras.json: {faltam}")
    modos = {n: e["modo"] + (" (provisorio)" if e["provisorio"] else "") for n, e in anc.items()}
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    (SAIDA / "atlas").mkdir(parents=True)
    indice, minis = {}, []
    for n in digimons:
        up, tags_up, caixa = quadros(EXPORT_UP / f"{n}.json", EXPORT_UP / f"{n}.png")
        ac, tags_ac, caixa_ac = quadros(EXPORT_ACOES / f"{n}.json", EXPORT_ACOES / f"{n}.png")
        ob, _, caixa_ob = quadros(EXPORT_ACOES / f"{n}_objeto.json", EXPORT_ACOES / f"{n}_objeto.png")
        if caixa_ac != caixa or caixa_ob != caixa or len(ob) != len(ac):
            raise ValueError(f"{n}: export das acoes nao casa com o do UP ({caixa_ac}, {caixa_ob}, {caixa})")
        com_objeto = []
        for (a, ms), (o, ms2) in zip(ac, ob):
            if ms != ms2:
                raise ValueError(f"{n}: ms do objeto difere")
            c = a.copy(); c.alpha_composite(o); com_objeto.append((c, ms))
        lista, tags = [], []
        for t in tags_up:
            tags.append([t["name"], len(lista) + t["from"], len(lista) + t["to"]])
        lista += up
        for t in tags_ac:
            tags.append([t["name"], len(lista) + t["from"], len(lista) + t["to"]])
        lista += com_objeto
        for t in tags_ac:
            tags.append([t["name"] + "_sem_objeto", len(lista) + t["from"], len(lista) + t["to"]])
        lista += ac
        W, H = caixa
        linhas = (len(lista) + COLUNAS - 1) // COLUNAS
        folha = Image.new("RGBA", (COLUNAS * (W + 1), linhas * (H + 1)), (0, 0, 0, 0))
        f = []
        for i, (im, ms) in enumerate(lista):
            x, y = (i % COLUNAS) * (W + 1), (i // COLUNAS) * (H + 1)
            folha.paste(im, (x, y)); f.append([x, y, ms])
        folha.save(SAIDA / "atlas" / f"{n}.png", optimize=True)
        idle = next(t for t in tags if t[0] == "Idle")
        m = lista[idle[1]][0]
        bb = m.getbbox() or (0, 0, W, H)
        m = m.crop(bb); m.thumbnail((TAM, TAM), Image.NEAREST)
        minis.append(m)
        indice[n] = {"w": W, "h": H, "sw": folha.width, "sh": folha.height, "f": f, "t": tags, "modo": modos[n]}
    cols = 16
    mini = Image.new("RGBA", (cols * TAM, ((len(minis) + cols - 1) // cols) * TAM), (0, 0, 0, 0))
    for i, (n, m) in enumerate(zip(digimons, minis)):
        x, y = (i % cols) * TAM, (i // cols) * TAM
        mini.paste(m, (x + (TAM - m.width) // 2, y + (TAM - m.height))); indice[n]["th"] = [x, y]
    mini.save(SAIDA / "atlas" / "miniaturas.png", optimize=True)
    (SAIDA / "atlas" / "index.json").write_text(json.dumps({"tam": TAM, "w": mini.width, "h": mini.height, "d": indice},
                                                           ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    html = PAGINA.read_text(encoding="utf-8")
    html = html.replace('document.title = "Atlas DIGIMON UP";', 'document.title = "Atlas das ações";')
    # a pagina foi feita para o artifact (que poe o esqueleto); servida solta, precisa do charset
    html = '<!doctype html>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' + html.replace("<title>Atlas DIGIMON UP</title>", "<title>Atlas das ações</title>")
    # abre no Comer em vez do Idle (as animacoes do UP continuam na lista)
    if 'tag = A.t.find(t => t[0] === "Idle") || A.t[0];' not in html:
        raise ValueError("a pagina do atlas mudou: o ponto de abrir no Idle nao foi achado")
    html = html.replace('tag = A.t.find(t => t[0] === "Idle") || A.t[0];', 'tag = A.t.find(t => t[0] === "Comer") || A.t.find(t => t[0] === "Idle") || A.t[0];')
    (SAIDA / "index.html").write_text(html, encoding="utf-8")
    print(f"{len(indice)} Digimon em {SAIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
