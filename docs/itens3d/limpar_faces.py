"""Uma cor por face na textura chapada de um item (docs/TAREFA_V3_ITENS_3D.md, secao 13; a ressalva do revisor no coco).

A textura da Meshy traz a sombra embutida, e o achatar_cores.py a leva para a cor escura da paleta em manchas dentro das voltas claras.
Aqui cada face fica com uma cor so: a mais comum dos pixels dentro do triangulo de UV dela; depois, RODADAS vezes, a face que discorda
da maioria dos vizinhos (uv_faces.py) passa para a cor deles. Cada triangulo e repintado com 3 px de margem, os maiores primeiro.

uso (da raiz): python -I docs/itens3d/limpar_faces.py <cor_chapada.png> <uv_faces.json> <saida.png>
"""
import json, sys
from collections import Counter
from PIL import Image, ImageDraw

RODADAS, MARGEM = 2, 3


def main(ent: str, faces_arq: str, sai: str) -> None:
    im = Image.open(ent).convert("RGB")
    w, h = im.size
    j = json.load(open(faces_arq, encoding="utf-8"))
    tris = [[(u * w, v * h) for u, v in t] for t in j["triangulos"]]
    px = im.load()
    cor = []
    for t in tris:
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).polygon(t, fill=255)
        caixa = m.getbbox()
        if caixa is None:   # triangulo menor que um pixel: o pixel do centro
            cx, cy = (min(int(sum(p[k] for p in t) / 3), lim - 1) for k, lim in ((0, w), (1, h)))
            cor.append(px[cx, cy])
            continue
        mp = m.load()
        c = Counter(px[x, y] for x in range(caixa[0], caixa[2]) for y in range(caixa[1], caixa[3]) if mp[x, y])
        cor.append(c.most_common(1)[0][0])
    mudou = 0
    for _ in range(RODADAS):
        nova = list(cor)
        for i, vs in enumerate(j["vizinhos"]):
            if not vs:
                continue
            c, n = Counter(cor[v] for v in vs).most_common(1)[0]
            if c != cor[i] and n * 2 > len(vs):
                nova[i] = c
                mudou += 1
        cor = nova
    d = ImageDraw.Draw(im)
    area = lambda t: abs((t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[2][0] - t[0][0]) * (t[1][1] - t[0][1]))
    for i in sorted(range(len(tris)), key=lambda i: -area(tris[i])):
        d.polygon(tris[i], fill=cor[i], outline=cor[i], width=MARGEM)
    im.save(sai, optimize=True)
    print("LIMPAR_FACES", len(tris), "faces;", mudou, "trocas pelos vizinhos; cores:", Counter(cor).most_common())


if __name__ == "__main__":
    main(*sys.argv[1:4])
