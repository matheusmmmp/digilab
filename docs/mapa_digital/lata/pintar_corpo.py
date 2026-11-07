"""O corpo da lata gigante sem as manchas cinza e brancas (docs/TAREFA_V3_MAPA_DIGITAL.md, etapa D4).

A textura da Meshy borra o corpo em cinza claro em alguns lados, e o achatar_cores.py leva esses borroes para o aluminio da paleta; os
reflexos viram manchas brancas. O limpar_faces.py (uma cor por face) quebra as faixas onduladas em lascas, porque as faces do corpo sao
compridas. Aqui, so dentro dos triangulos do corpo (faces_corpo.py):
  - os pixels voltam a ser achatados sem as duas cores de aluminio;
  - o branco (o contorno das cerejas) so fica a ate PERTO pixels da cereja ou da folha; longe delas, o pixel volta a ser achatado so nas
    faixas pastel;
  - um filtro de moda (MODA) limpa os pontinhos, como no achatar_cores.py.
Fora do corpo (a tampa, o anel e o fundo), fica a textura achatada de entrada. Os numeros sao PROPOSTOS, SEM FONTE.

uso (da raiz): python -I docs/mapa_digital/lata/pintar_corpo.py <textura_meshy.png> <cor_achatada.png> <uv_faces.json> <faces_corpo.json> <paleta.json> <saida.png>
"""
import json, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

PERTO = 24
MODA = 9
MARGEM_TRI = 3


def achatar(im: Image.Image, pal: list[tuple[int, int, int]]) -> Image.Image:
    plano = Image.new("P", (1, 1))
    plano.putpalette([v for c in pal for v in c] + list(pal[0]) * (256 - len(pal)))
    return im.quantize(palette=plano, dither=Image.Dither.NONE).convert("RGB")


def mascara_de(im: Image.Image, cores: list[tuple[int, int, int]]) -> Image.Image:
    m = Image.new("L", im.size, 0)
    for c in cores:
        dif = ImageChops.difference(im, Image.new("RGB", im.size, c)).convert("L")
        m = ImageChops.lighter(m, dif.point(lambda v: 255 if v == 0 else 0))
    return m


def main(meshy: str, achatada: str, uv_arq: str, corpo_arq: str, paleta_arq: str, sai: str) -> None:
    P = json.load(open(paleta_arq, encoding="utf-8"))
    pal, nomes = [tuple(c) for c in P["paleta"]], P["nomes"]
    cor = dict(zip(nomes, pal))
    base = Image.open(achatada).convert("RGB")
    lado = base.size[0]
    orig = Image.open(meshy).convert("RGB").resize(base.size, Image.LANCZOS)
    tris = json.load(open(uv_arq))["triangulos"]
    corpo = json.load(open(corpo_arq))["corpo"]
    if len(tris) != len(corpo):
        raise SystemExit(f"faces diferentes: {len(tris)} no uv_faces, {len(corpo)} no faces_corpo")

    mascara = Image.new("L", base.size, 0)
    d = ImageDraw.Draw(mascara)
    for t, c in zip(tris, corpo):
        if c:
            pts = [(u * lado, v * lado) for u, v in t]
            d.polygon(pts, fill=255, outline=255, width=MARGEM_TRI)

    sem_aluminio = [c for c, n in zip(pal, nomes) if not n.startswith("aluminio")]
    q = achatar(orig, sem_aluminio)
    fruta = mascara_de(q, [cor["cereja"], cor["folha"]]).filter(ImageFilter.MaxFilter(2 * (PERTO // 2) + 1))
    branco_longe = ImageChops.subtract(mascara_de(q, [cor["contorno"]]), fruta)
    so_faixas = achatar(orig, [cor[n] for n in ("menta", "lilas", "amarelo", "rosa")])
    q = Image.composite(so_faixas, q, branco_longe).filter(ImageFilter.ModeFilter(MODA))
    saida = Image.composite(q, base, mascara)
    saida.save(sai, optimize=True)
    n = sum(corpo)
    print("PINTAR_CORPO", sai, f"{n} faces do corpo; brancos longe da fruta: {sum(1 for v in branco_longe.getdata() if v)} px")


if __name__ == "__main__":
    main(*sys.argv[1:7])
