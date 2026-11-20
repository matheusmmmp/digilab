"""Achata a textura de cor de um item na paleta do concept (docs/TAREFA_V3_ITENS_3D.md, secao 4.1, etapa 6).

A textura do gerador traz a sombra embutida e borroes entre as cores; a ilha ja sombreia com o toon, entao a cor do item deve ser chapada.
Cada pixel vai para a cor mais proxima da paleta (RGB), e um filtro de moda limpa os pontinhos soltos. A paleta e as cores medianas das
regioes do concept escolhido, escritas a mao no JSON do item (PROPOSTO).

uso (da raiz): python -I docs/itens3d/achatar_cores.py <entrada.png> <saida.png> <paleta.json> [lado]
"""
import json, sys
from PIL import Image, ImageFilter


def main(ent: str, sai: str, paleta_arq: str, lado: int = 1024) -> None:
    pal = [tuple(c) for c in json.load(open(paleta_arq, encoding="utf-8"))["paleta"]]
    im = Image.open(ent).convert("RGB")
    if im.size != (lado, lado):
        im = im.resize((lado, lado), Image.LANCZOS)
    plano = Image.new("P", (1, 1))
    # o resto das 256 entradas repete a primeira cor: com zeros, o preto viraria uma cor da paleta
    plano.putpalette([v for c in pal for v in c] + list(pal[0]) * (256 - len(pal)))
    q = im.quantize(palette=plano, dither=Image.Dither.NONE)
    q = q.filter(ImageFilter.ModeFilter(9))
    q.convert("RGB").save(sai, optimize=True)
    usados = sorted(q.getcolors(), reverse=True)
    print("ACHATAR", sai, lado, "px; cores usadas:", [(n, pal[i]) for n, i in usados])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], *(int(x) for x in sys.argv[4:5]))
