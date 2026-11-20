"""Achata a textura de cor da barraca na paleta do concept pelo matiz, nao pela cor (docs/TAREFA_V3_LUGARES_3D.md, secao 10).

A Meshy embutiu a sombra na textura do domo: o branco das listras saiu um lilas acinzentado (~165) e o verde-azulado, escuro. Pela cor mais
proxima (achatar_cores.py), a listra caia no cinza do prato, no azul dos livros ou na lona. Aqui cada pixel e classificado pelo matiz, pela
saturacao e pelo brilho (HSV, limiares PROPOSTOS, SEM FONTE, escolhidos olhando a previa) e pintado com a cor da paleta.json; um filtro de moda
limpa os pontinhos soltos.

uso (da raiz): python -I docs/lugares3d/barraca/achatar_barraca.py <entrada.png> <saida.png> <paleta.json>
"""
import json, sys
import numpy as np
from PIL import Image, ImageFilter

LADO = 1024
MODA = 7


def classe(h, s, v, nomes):
    """O indice da cor da paleta para cada pixel (h em graus, s e v de 0 a 1)."""
    i = {n: k for k, n in enumerate(nomes)}
    c = np.full(h.shape, i["verde-azulado"], dtype=np.uint8)
    teal = (h >= 160) & (h < 205)
    c[teal & (v < 0.5)] = i["verde-azulado sombra"]
    c[teal & (s > 0.45) & (v > 0.85)] = i["tela"]
    claro = s < 0.2
    c[claro & (v >= 0.6)] = i["branco"]
    c[claro & (v < 0.6)] = i["lilas"]
    c[claro & (v < 0.3)] = i["entrada"]
    quente = ((h < 50) | (h >= 330)) & (s >= 0.2)
    c[quente & (v < 0.6)] = i["madeira"]
    c[quente & (v >= 0.6)] = i["lona"]
    c[((h < 15) | (h >= 330)) & (s > 0.5) & (v > 0.5)] = i["livro vermelho"]
    c[(h >= 35) & (h < 70) & (s > 0.45) & (v > 0.6)] = i["livro amarelo"]
    c[(h >= 205) & (h < 260) & (s > 0.3)] = i["livro azul"]
    return c


def main(ent, sai, paleta_arq):
    j = json.load(open(paleta_arq, encoding="utf-8"))
    pal, nomes = j["paleta"], j["nomes"]
    im = Image.open(ent).convert("RGB").resize((LADO, LADO), Image.LANCZOS)
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32)
    c = classe(hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255, nomes)
    q = Image.fromarray(c, "P")
    q.putpalette([v for cor in pal for v in cor] + list(pal[0]) * (256 - len(pal)))
    q = q.filter(ImageFilter.ModeFilter(MODA))
    q.convert("RGB").save(sai, optimize=True)
    print("ACHATAR", sai, "cores usadas:", [(n, nomes[k]) for n, k in sorted(q.getcolors(), reverse=True)])


if __name__ == "__main__":
    main(*sys.argv[1:4])
