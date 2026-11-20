"""A mascara da luz do poste (docs/TAREFA_V3_MUNDO_ENFEITES.md, etapa E1): branco onde a textura chapada tem a cor do vidro da paleta, preto
no resto. A vista (enfeites.ts) a usa como emissiveMap do material do poste, ligada so a noite: os vidros do lampiao acendem. Fica fora do
glTF (o gate G5 nao aceita mapa emissivo no arquivo), ao lado dele, como poste_luz.png.

uso (da raiz): python -I docs/enfeites/poste/mascara_luz.py <cor_chapada.png> <paleta.json> <saida.png>
"""
import json, sys
from PIL import Image

LADO = 256


def main(ent: str, paleta_arq: str, sai: str) -> None:
    pal = json.load(open(paleta_arq, encoding="utf-8"))
    vidro = tuple(dict(zip(pal["nomes"], pal["paleta"]))["vidro"])
    im = Image.open(ent).convert("RGB")
    m = Image.new("L", im.size, 0)
    px, pm = im.load(), m.load()
    n = 0
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            if px[x, y] == vidro:
                pm[x, y] = 255
                n += 1
    m.resize((LADO, LADO), Image.BILINEAR).save(sai, optimize=True)
    print("MASCARA_LUZ", n, "pixels do vidro;", LADO, "px")


if __name__ == "__main__":
    main(*sys.argv[1:4])
