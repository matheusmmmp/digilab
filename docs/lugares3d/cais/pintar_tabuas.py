"""Uma cor por face no cais e a madeira das faces de cima com a cor da tabua (docs/TAREFA_V3_LUGARES_3D.md, secao 11; as ressalvas do
revisor: as tabuas e os postes quase da mesma cor, e a mascara do ciano com pontinhos soltos).

Cada face fica com a cor mais comum dos pixels do triangulo de UV dela (como o limpar_faces.py, sem rodada de vizinhos, para os cristais e
as linhas ciano ficarem); depois, a face de cima (faces_tabuas.py) que ficou com uma das madeiras passa para a "tabua". Assim o tampo dos
deques fica claro e os postes ficam na madeira, e a mascara (mascara_cais.py) sai por face, sem os pontinhos.

uso (da raiz): python -I docs/lugares3d/cais/pintar_tabuas.py <cor_achatada.png> <uv_faces.json> <faces_tabuas.json> <paleta.json> <saida.png>
"""
import json, sys
from collections import Counter
from PIL import Image, ImageDraw

MARGEM = 3
MADEIRAS = ("madeira", "madeira sombra")


def main(ent, uv_arq, cima_arq, paleta_arq, sai):
    pal = json.load(open(paleta_arq, encoding="utf-8"))
    cor_de = dict(zip(pal["nomes"], (tuple(c) for c in pal["paleta"])))
    im = Image.open(ent).convert("RGB")
    w, h = im.size
    tris = [[(u * w, v * h) for u, v in t] for t in json.load(open(uv_arq, encoding="utf-8"))["triangulos"]]
    cima = set(json.load(open(cima_arq, encoding="utf-8"))["cima"])
    px = im.load()
    cor = []
    for t in tris:
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).polygon(t, fill=255)
        caixa = m.getbbox()
        if caixa is None:
            cx, cy = (min(int(sum(p[k] for p in t) / 3), lim - 1) for k, lim in ((0, w), (1, h)))
            cor.append(px[cx, cy])
            continue
        mp = m.load()
        cor.append(Counter(px[x, y] for x in range(caixa[0], caixa[2]) for y in range(caixa[1], caixa[3]) if mp[x, y]).most_common(1)[0][0])
    madeira = {cor_de[n] for n in MADEIRAS}
    trocas = 0
    for i in cima:
        if cor[i] in madeira:
            cor[i] = cor_de["tabua"]
            trocas += 1
    d = ImageDraw.Draw(im)
    area = lambda t: abs((t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[2][0] - t[0][0]) * (t[1][1] - t[0][1]))
    for i in sorted(range(len(tris)), key=lambda i: -area(tris[i])):
        d.polygon(tris[i], fill=cor[i], outline=cor[i], width=MARGEM)
    im.save(sai, optimize=True)
    print("TABUAS", trocas, "faces de cima para a tabua; cores:", Counter(cor).most_common())


if __name__ == "__main__":
    main(*sys.argv[1:6])
