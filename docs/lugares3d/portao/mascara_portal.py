"""A mascara do portal do portao da arena (docs/TAREFA_V3_LUGARES_3D.md, etapa P1), como a da luz do poste (docs/enfeites/poste/mascara_luz.py):
branco onde a textura chapada tem uma das cores do portal da paleta ("portal" e "portal claro"), preto no resto. A vista dos lugares
(ilha/lugares.ts, da frente UX_TELA_PET) a usa como emissiveMap do material do portao: apagado com o lugar trancado, aceso com ele aberto.
Fica fora do glTF (o gate G5 nao aceita mapa emissivo no arquivo), ao lado dele, como portao_luz.png.

uso (da raiz): python -I docs/lugares3d/portao/mascara_portal.py <cor_chapada.png> <paleta.json> <saida.png>
"""
import json, sys
from PIL import Image

LADO = 256
CORES = ("portal", "portal claro")


def main(ent: str, paleta_arq: str, sai: str) -> None:
    pal = json.load(open(paleta_arq, encoding="utf-8"))
    cor = dict(zip(pal["nomes"], (tuple(c) for c in pal["paleta"])))
    alvo = {cor[n] for n in CORES}
    im = Image.open(ent).convert("RGB")
    m = Image.new("L", im.size, 0)
    px, pm = im.load(), m.load()
    n = 0
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            if px[x, y] in alvo:
                pm[x, y] = 255
                n += 1
    m.resize((LADO, LADO), Image.BILINEAR).save(sai, optimize=True)
    print("MASCARA_PORTAL", n, "pixels do portal;", LADO, "px")


if __name__ == "__main__":
    main(*sys.argv[1:4])
