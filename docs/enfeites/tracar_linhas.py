"""Os tracos de nanquim na textura de um enfeite (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 11; pedido do Matheus em 2026-11-06: "mais
cartunesco, com tracos mais firmes, fortes, na textura mesmo", no jeito de Borderlands).

Sobre a textura ja chapada (achatar_cores.py e limpar_faces.py), um traco escuro em cada aresta da malha que e:
  - uma quina grande (o angulo entre as duas faces passa de LIMIAR graus, e a aresta tem pelo menos COMP_MIN de comprimento: com 38 graus
    e sem o comprimento, as facetas da Meshy davam riscos soltos e sujos, pelo revisor) ou uma borda solta;
  - uma divisa de cor (as duas faces tem cores diferentes; a cor de cada face e a mais comum no triangulo de UV dela).
O traco e desenhado no segmento de UV da aresta em cada face dos dois lados (arestas_uv.py), com a ESPESSURA em pixels da textura de
1024; metade dele cai dentro de cada triangulo. A cor e a tinta (TINTA), quase preta e quente. Os numeros sao PROPOSTOS, SEM FONTE.

uso (da raiz): python -I docs/enfeites/tracar_linhas.py <cor_chapada.png> <arestas_uv.json> <saida.png> [limiar] [espessura]
"""
import json, sys
from collections import Counter
from PIL import Image, ImageDraw

LIMIAR, ESPESSURA, TINTA, COMP_MIN = 70.0, 5, (43, 34, 32), 0.12


def cor_das_faces(im: Image.Image, tris: list) -> list:
    px, (w, h) = im.load(), im.size
    cores = []
    for t in tris:
        pts = [(u * w, v * h) for u, v in t]
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).polygon(pts, fill=255)
        cx = m.getbbox()
        if cx is None:
            x, y = (min(int(sum(p[k] for p in pts) / 3), lim - 1) for k, lim in ((0, w), (1, h)))
            cores.append(px[x, y])
            continue
        mp = m.load()
        cores.append(Counter(px[x, y] for x in range(cx[0], cx[2]) for y in range(cx[1], cx[3]) if mp[x, y]).most_common(1)[0][0])
    return cores


def main(ent: str, arestas_arq: str, sai: str, limiar: float = LIMIAR, espessura: int = ESPESSURA) -> None:
    im = Image.open(ent).convert("RGB")
    w, h = im.size
    j = json.load(open(arestas_arq, encoding="utf-8"))
    cores = cor_das_faces(im, j["triangulos"])
    d = ImageDraw.Draw(im)
    quinas = divisas = 0
    for a in j["arestas"]:
        fs = a["faces"]
        quina = a["angulo"] > limiar and (len(fs) != 2 or a["comp"] >= COMP_MIN)
        divisa = len(fs) == 2 and cores[fs[0]] != cores[fs[1]]
        if not (quina or divisa):
            continue
        quinas += quina
        divisas += divisa and not quina
        for (u0, v0), (u1, v1) in a["segs"]:
            d.line([(u0 * w, v0 * h), (u1 * w, v1 * h)], fill=TINTA, width=espessura)
            for u, v in ((u0, v0), (u1, v1)):   # a ponta redonda, para os tracos emendarem sem falha
                r = espessura / 2
                d.ellipse([u * w - r, v * h - r, u * w + r, v * h + r], fill=TINTA)
    im.save(sai, optimize=True)
    print("TRACAR_LINHAS", quinas, "quinas e", divisas, "divisas de cor; limiar", limiar, "graus, espessura", espessura, "px")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], *(float(x) for x in sys.argv[4:5]), *(int(x) for x in sys.argv[5:6]))
