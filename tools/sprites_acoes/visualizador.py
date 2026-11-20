"""SPRITES_ACOES, missao M1: o visualizador das acoes novas, para o Matheus ver o Comer antes de ele ir para o jogo (2026-11-04).

Copia a pagina do atlas do UP (remaster/fonte/site/atlas_digimon_up.html) com os 60 Digimon das formas, cada um com as animacoes do
export do UP mais as novas do lote 1 (Comer, com a comida por cima, e Comer_sem_objeto; Feliz, Sacudir, Chamar e Emburrar, sem
objeto; e a previa da vista, <Tag>+vista: o clipe com os sobrepostos da vista por cima, o coracao, as gotas, o ! e a raiva das
grades de arte propria do jogo, web/app/src/grades.ts, e o tom escuro do Emburrar; os quadros do clipe nao mudam), e o modo de cada um no ancoras.json. A saida fica FORA
DO GIT, em remaster/acoes/visualizador/site (sao quadros do UP). Nada daqui entra no jogo: o Assets/digilab_atlas_up_clipes.json so e
regerado depois que o Matheus aprova aqui. Fora do pacote digilab/, entao pode usar Pillow. Falha alto.

Uso: python -I tools/sprites_acoes/visualizador.py [--prova]   (depois do gerar_acoes.py; sirva a saida com python -m http.server dentro dela)
"""
from __future__ import annotations

import json
import shutil
import time
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
TAGS_LOTE1 = ("Comer", "Feliz", "Sacudir", "Chamar", "Emburrar")
GRADES = AQUI.parents[1] / "web" / "app" / "src" / "grades.ts"
# a previa dos sobrepostos (so no visualizador; o jogo os desenha na vista): a grade, px por celula, a folga em cima dos quadros
# para o icone caber sobre a cabeca, e o tom do Emburrar. PROPOSTO, SEM FONTE.
SOBREPOSTO = {"Feliz": "coracao", "Sacudir": "gota", "Chamar": "exclam", "Emburrar": "raiva"}
ESCALA_ICONE = 2
FOLGA = 20
TOM_EMBURRAR = 0.7
PALETA = {"k": (29, 34, 51), "r": (232, 68, 90), "y": (245, 197, 66), "c": (127, 200, 240), "w": (255, 255, 255)}
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


def grades() -> dict[str, list[str]]:
    """As grades de arte propria do jogo (o objeto S de web/app/src/grades.ts) que os sobrepostos usam. Falha alto se faltar uma."""
    import re
    texto = GRADES.read_text(encoding="utf-8")
    g = {}
    for nome in SOBREPOSTO.values():
        m = re.search(r"^\s*" + nome + r": \[([^\]]*)\]", texto, re.M)
        if not m:
            raise ValueError(f"{GRADES}: sem a grade {nome}")
        g[nome] = re.findall(r'"([^"]*)"', m.group(1))
    return g


def icone(grade: list[str]) -> Image.Image:
    im = Image.new("RGBA", (len(grade[0]) * ESCALA_ICONE, len(grade) * ESCALA_ICONE), (0, 0, 0, 0))
    for y, linha in enumerate(grade):
        for x, ch in enumerate(linha):
            if ch != ".":
                if ch not in PALETA:
                    raise ValueError(f"cor {ch!r} sem paleta no visualizador")
                for dy in range(ESCALA_ICONE):
                    for dx in range(ESCALA_ICONE):
                        im.putpixel((x * ESCALA_ICONE + dx, y * ESCALA_ICONE + dy), PALETA[ch] + (255,))
    return im


def cabeca(im: Image.Image) -> tuple[int, int]:
    """O topo do personagem: (x medio dos pixels opacos das 6 linhas de cima, a linha de cima)."""
    bb = im.getbbox()
    if not bb:
        raise ValueError("quadro vazio")
    a = im.getchannel("A")
    xs = [x for y in range(bb[1], min(bb[1] + 6, bb[3])) for x in range(bb[0], bb[2]) if a.getpixel((x, y))]
    return sum(xs) // len(xs), bb[1]


def vista(tag: str, qs: list[tuple[Image.Image, int]], icones: dict[str, Image.Image]) -> list[tuple[Image.Image, int]]:
    """A previa de uma acao do lote 1 como o jogo a mostraria: o clipe (ja com a folga em cima) e o sobreposto dela por cima."""
    ic = icones[SOBREPOSTO[tag]]
    out = []
    for i, (im, ms) in enumerate(qs):
        c = im.copy()
        if tag == "Emburrar":   # o tom escuro da vista
            r, g, b, a = c.split()
            r, g, b = (ch.point(lambda v: int(v * TOM_EMBURRAR)) for ch in (r, g, b))
            c = Image.merge("RGBA", (r, g, b, a))
        hx, top = cabeca(im)
        bb = im.getbbox()
        if tag == "Feliz" and i >= 1:            # o coracao sobe e balanca
            c.alpha_composite(ic, (hx - ic.width // 2 + (i % 2), max(0, top - ic.height - 2 - i)))
        elif tag == "Sacudir" and i < len(qs) - 1:   # gotas saindo dos dois lados, cada vez mais longe
            meio = (bb[1] + bb[3]) // 2
            d = 2 + 2 * (i % 4)
            c.alpha_composite(ic, (max(0, bb[0] - ic.width - d), max(0, meio - 6 - (i % 3) * 3)))
            c.alpha_composite(ic, (min(c.width - ic.width, bb[2] + d), max(0, meio - 2 - ((i + 1) % 3) * 3)))
        elif tag == "Chamar":                    # o ! sobre a cabeca, pulando junto
            c.alpha_composite(ic, (hx - ic.width // 2, max(0, top - ic.height - 2)))
        elif tag == "Emburrar":                  # a raiva na testa, pulsando
            c.alpha_composite(ic, (hx - ic.width // 2 + (i % 2), max(0, top - ic.height + 4 - (i % 2))))
        out.append((c, ms))
    return out


def folga(qs: list[tuple[Image.Image, int]]) -> list[tuple[Image.Image, int]]:
    """Os quadros com FOLGA px transparentes em cima (para o icone sobre a cabeca); o pe e o resto ficam no lugar."""
    out = []
    for im, ms in qs:
        c = Image.new("RGBA", (im.width, im.height + FOLGA), (0, 0, 0, 0)); c.paste(im, (0, FOLGA)); out.append((c, ms))
    return out


def main() -> int:
    # --prova: aceita Digimon so com o Comer (o lote 1 gerado num Digimon de prova antes dos 60); sem ele, falta de tag levanta
    prova = "--prova" in sys.argv[1:]
    if set(sys.argv[1:]) - {"--prova"}:
        raise SystemExit(f"argumento desconhecido: {sys.argv[1:]}")
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
    icones = {n: icone(g) for n, g in grades().items()}
    indice, minis = {}, []
    for n in digimons:
        up, tags_up, caixa = quadros(EXPORT_UP / f"{n}.json", EXPORT_UP / f"{n}.png")
        ac, tags_ac, caixa_ac = quadros(EXPORT_ACOES / f"{n}.json", EXPORT_ACOES / f"{n}.png")
        ob, tags_ob, caixa_ob = quadros(EXPORT_ACOES / f"{n}_objeto.json", EXPORT_ACOES / f"{n}_objeto.png")
        if caixa_ac != caixa or caixa_ob != caixa:
            raise ValueError(f"{n}: export das acoes nao casa com o do UP ({caixa_ac}, {caixa_ob}, {caixa})")
        up, ac, ob = folga(up), folga(ac), folga(ob)
        caixa = (caixa[0], caixa[1] + FOLGA)
        faltam_tags = [t for t in TAGS_LOTE1 if t not in {x["name"] for x in tags_ac}]
        if faltam_tags and not (prova and "Comer" not in faltam_tags):
            raise ValueError(f"{n}: o export das acoes nao tem {faltam_tags} (rode tools/sprites_acoes/gerar_acoes.py)")
        objetos = {t["name"]: ob[t["from"]:t["to"] + 1] for t in tags_ob}   # so as acoes com objeto (o Comer)
        lista, tags = [], []
        for t in tags_up:
            tags.append([t["name"], len(lista) + t["from"], len(lista) + t["to"]])
        lista += up
        sem_objeto, previas = [], []
        for t in tags_ac:
            qs = ac[t["from"]:t["to"] + 1]
            if t["name"] in SOBREPOSTO:
                previas.append((t["name"] + "+vista", vista(t["name"], qs, icones)))
            if t["name"] in objetos:
                os_ = objetos.pop(t["name"])
                if [ms for _, ms in qs] != [ms for _, ms in os_]:
                    raise ValueError(f"{n}: o objeto de {t['name']} nao casa com a acao em quadros e ms")
                com = []
                for (a, ms), (o, _) in zip(qs, os_):
                    c = a.copy(); c.alpha_composite(o); com.append((c, ms))
                sem_objeto.append((t["name"] + "_sem_objeto", qs))
                qs = com
            tags.append([t["name"], len(lista), len(lista) + len(qs) - 1])
            lista += qs
        if objetos:
            raise ValueError(f"{n}: objeto sem a acao: {sorted(objetos)}")
        for nome, qs in previas + sem_objeto:
            tags.append([nome, len(lista), len(lista) + len(qs) - 1])
            lista += qs
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
        indice[n] = {"w": W, "h": H, "sw": folha.width, "sh": folha.height, "f": f, "t": tags, "modo": modos[n],
                    "l": ["sombra", "personagem", "comida"]}   # a pagina le A.l (as camadas); sem ele o play para
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
    # abre no Feliz com a previa da vista, a primeira acao nova do lote 1, em vez do Idle (as do UP e o Comer continuam na lista)
    if 'tag = A.t.find(t => t[0] === "Idle") || A.t[0];' not in html:
        raise ValueError("a pagina do atlas mudou: o ponto de abrir no Idle nao foi achado")
    html = html.replace('tag = A.t.find(t => t[0] === "Idle") || A.t[0];', 'tag = A.t.find(t => t[0] === "Feliz+vista") || A.t.find(t => t[0] === "Feliz") || A.t.find(t => t[0] === "Idle") || A.t[0];')
    # sem cache: o http.server nao manda no-cache, e o navegador mostrava o atlas antigo depois de regerar (2026-11-05)
    versao = str(int(time.time()))
    trocas = [
        ("<script>", f'<script>\nconst VERSAO = "{versao}";', 1),
        ('fetch("atlas/index.json")', 'fetch("atlas/index.json?v=" + VERSAO, {cache: "no-store"})', 1),
        ('im.src = "atlas/" + encodeURIComponent(n) + ".png";', 'im.src = "atlas/" + encodeURIComponent(n) + ".png?v=" + VERSAO;', 1),
        ('"url(atlas/miniaturas.png)"', '"url(atlas/miniaturas.png?v=" + VERSAO + ")"', 1),
        ('img.src.endsWith(encodeURIComponent(atual) + ".png")', 'img.src.includes("/" + encodeURIComponent(atual) + ".png")', 2),
    ]
    for antes, depois, n in trocas:
        if html.count(antes) != n:
            raise ValueError(f"a pagina do atlas mudou: {antes!r} aparece {html.count(antes)} vezes, esperado {n}")
        html = html.replace(antes, depois)
    (SAIDA / "index.html").write_text(html, encoding="utf-8")
    print(f"{len(indice)} Digimon em {SAIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
