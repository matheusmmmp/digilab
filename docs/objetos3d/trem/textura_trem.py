"""A textura do vagao no trilho (o retrabalho dos objetos, docs/objetos3d/REFERENCIAS.md): a textura pintada da Meshy, sem achatar.

  1. o realce leve (a limpeza que a regra nova deixa): o lado claro do toon de dois tons estoura a saturacao, e o latao das escotilhas,
     o vidro, o musgo e a grama sumiam (o revisor, rodada 1); so essas faixas de cor ganham saturacao, e o metal cinza um tom de ferro;
  2. reduzida ao lado pedido (512: o orcamento de 300 KB do teste dos enfeites, com a malha);
  3. a mascara das ilhas da UV (onde a textura e usada): o enchimento fora delas fica chapado, para o PNG comprimir melhor;
  4. 256 cores com pontilhado (o PNG de paleta; no olho, igual ao RGB).
uso (da raiz): python -I docs/objetos3d/trem/textura_trem.py <trilho.gltf> <textura da Meshy> <saida.png> <lado> <cores>
"""
import json, sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
def realce(im):
    """o latao, o vidro, os verdes e o metal cinza, em HSV (graus, 0..1); o resto fica como veio. Numeros do olho: PROPOSTO, SEM FONTE"""
    a = np.asarray(im.convert("HSV")).astype(np.float32)
    h, s, v = a[..., 0] * 360 / 255, a[..., 1] / 255, a[..., 2] / 255
    latao = (h >= 28) & (h <= 52) & (s > 0.38) & (v > 0.4)
    s = np.where(latao, np.minimum(1, s * 1.35), s); v = np.where(latao, v * 0.88, v)
    verde = (h >= 50) & (h <= 140) & (s > 0.18)
    h = np.where(verde, h + (100 - h) * 0.5, h); s = np.where(verde, np.minimum(1, s * 1.6), s)
    vidro = (h >= 185) & (h <= 250) & (s > 0.06) & (v < 0.7)
    s = np.where(vidro, np.minimum(1, s * 1.8 + 0.05), s)
    out = np.stack([h * 255 / 360, s * 255, v * 255], -1).clip(0, 255).astype(np.uint8)
    rgb = np.asarray(Image.fromarray(out, "HSV").convert("RGB")).astype(np.int16)
    cinza = (np.asarray(im.convert("HSV"))[..., 1] < 28) & (np.asarray(im.convert("HSV"))[..., 2] > 40)
    rgb[cinza] += np.array([-4, 0, 8], dtype=np.int16)
    print("realce: latao", round(latao.mean(), 4), "verde", round(verde.mean(), 4), "vidro", round(vidro.mean(), 4), "cinza", round(cinza.mean(), 4))
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8), "RGB")

def mascara(gltf, lado, folga):
    g = json.load(open(gltf)); d = __import__("pathlib").Path(gltf).parent
    buf = open(d / g["buffers"][0]["uri"], "rb").read()
    def acc(i, tipo, n):
        a = g["accessors"][i]; v = g["bufferViews"][a["bufferView"]]; o = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(buf, dtype=tipo, count=a["count"] * n, offset=o).reshape(-1, n) if n > 1 else np.frombuffer(buf, dtype=tipo, count=a["count"], offset=o)
    p = g["meshes"][0]["primitives"][0]
    uv = acc(p["attributes"]["TEXCOORD_0"], np.float32, 2)
    ia = g["accessors"][p["indices"]]; idx = acc(p["indices"], {5123: np.uint16, 5125: np.uint32}[ia["componentType"]], 1).reshape(-1, 3)
    m = Image.new("L", (lado, lado), 0); dr = ImageDraw.Draw(m)
    for t in idx:
        dr.polygon([(uv[k][0] * lado, uv[k][1] * lado) for k in t], fill=255, outline=255)
    return m.filter(ImageFilter.MaxFilter(folga * 2 + 1))
if __name__ == "__main__":
    gltf, ent, sai, lado, cores = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    im = realce(Image.open(ent).convert("RGB")).resize((lado, lado), Image.LANCZOS)
    m = mascara(gltf, lado, 3)
    print("cobertura", round(np.asarray(m).mean() / 255, 3))
    media = tuple(int(c) for c in np.asarray(im)[np.asarray(m) > 0].mean(0))
    fundo = Image.new("RGB", (lado, lado), media); im = Image.composite(im, fundo, m)
    if cores <= 256:
        im = im.quantize(cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    im.save(sai, optimize=True)
    import os; print(sai, os.path.getsize(sai) // 1024, "KB")
