"""A textura do kit medico para o consertar_kit.py (docs/TAREFA_V3_ITENS_3D.md, secao 13).

A textura chapada da Meshy ocupa a imagem inteira e nao tem vermelho. Aqui ela encolhe para 96 % no canto de baixo a esquerda (o canto
u = v = 0 dos UVs; o consertar_kit.py encolhe os UVs do mesmo jeito), e na faixa livre de cima entra um quadrado vermelho da paleta, onde
caem os UVs da cruz. A faixa livre fica na cor da madeira, para o filtro de mipmap nao puxar outra cor nas bordas.

uso (da raiz): python -I docs/itens3d/kit/preparar_textura_kit.py <cor_achatada.png> <paleta.json> <saida.png>
"""
import json, sys
from PIL import Image

ENCOLHE, LADO = 0.96, 1024
QUADRADO = (994, 6, 1018, 30)   # x0, y0, x1, y1 (px; y para baixo), o centro em (1006, 18)


def main(ent: str, paleta_arq: str, sai: str) -> None:
    pal = json.load(open(paleta_arq, encoding="utf-8"))
    cor = dict(zip(pal["nomes"], (tuple(c) for c in pal["paleta"])))
    im = Image.open(ent).convert("RGB")
    if im.size != (LADO, LADO):
        raise SystemExit("a textura achatada devia ter %d px: %s" % (LADO, im.size))
    s = round(LADO * ENCOLHE)
    nova = Image.new("RGB", (LADO, LADO), cor["madeira"])
    nova.paste(im.resize((s, s), Image.NEAREST), (0, LADO - s))
    nova.paste(cor["cruz"], QUADRADO)
    nova.save(sai, optimize=True)
    print("TEXTURA_KIT", sai, "encolhida para", s, "px; o quadrado vermelho em", QUADRADO)


if __name__ == "__main__":
    main(*sys.argv[1:4])
