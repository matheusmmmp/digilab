"""Tira as manchas cor de lona e de corda da pedra da base do saco (docs/TAREFA_V3_ITENS_3D.md, secao 12; a ressalva do revisor visual).

A textura da Meshy tem manchas marrons e rosadas na pedra com musgo, e o achatar_cores.py as leva para a lona e a corda da paleta. Aqui,
so dentro dos triangulos de UV da pedra (uv_base.py, com 4 px de margem), a lona e a corda viram o musgo da paleta; o resto fica.

uso (da raiz): python -I docs/itens3d/saco/pintar_base.py <cor_chapada.png> <uv_base.json> <paleta.json> <saida.png>
"""
import json, sys
from PIL import Image, ImageDraw, ImageFilter


def main(ent: str, uvs: str, paleta_arq: str, sai: str) -> None:
    pal = json.load(open(paleta_arq, encoding="utf-8"))
    cor = dict(zip(pal["nomes"], (tuple(c) for c in pal["paleta"])))
    de, para = {cor["lona"], cor["corda"]}, cor["musgo e sombra do bambu"]
    im = Image.open(ent).convert("RGB")
    w, h = im.size
    mascara = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mascara)
    for t in json.load(open(uvs, encoding="utf-8"))["triangulos"]:
        d.polygon([(u * w, v * h) for u, v in t], fill=255)
    mascara = mascara.filter(ImageFilter.MaxFilter(9))
    px, m = im.load(), mascara.load()
    n = 0
    for y in range(h):
        for x in range(w):
            if m[x, y] and px[x, y] in de:
                px[x, y] = para
                n += 1
    im.save(sai, optimize=True)
    print("PINTAR_BASE", n, "pixels da lona e da corda viraram musgo")


if __name__ == "__main__":
    main(*sys.argv[1:5])
