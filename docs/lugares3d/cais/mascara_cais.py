"""A mascara do ciano do cais (docs/TAREFA_V3_LUGARES_3D.md, secao 11), como a do portal do portao (docs/lugares3d/portao/mascara_portal.py):
branco onde a textura chapada tem o "ciano" da paleta (os cristais e a boia de dados; a cor por face do pintar_tabuas.py), preto no resto. A vista
dos lugares (ilha/lugares.ts, da frente UX_TELA_PET) a usa como emissiveMap do material do cais: apagado com o lugar trancado, aceso com ele
aberto. Fica fora do glTF (o gate G5 nao aceita mapa emissivo no arquivo), ao lado dele, como cais_luz.png. A luz amarela da balsa fica de
fora: no achatamento ela caiu no mesmo amarelo da borda.

uso (da raiz): python -I docs/lugares3d/cais/mascara_cais.py <cor_chapada.png> <paleta.json> <saida.png>
"""
import json, sys
from PIL import Image

LADO = 256
CORES = ("ciano",)


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
    print("MASCARA_CAIS", n, "pixels do ciano;", LADO, "px")


if __name__ == "__main__":
    main(*sys.argv[1:4])
