"""A textura do cais retrabalhado (docs/TAREFA_V3_LUGARES_3D.md, secao 16; docs/objetos3d/REFERENCIAS.md, secao 5): a textura pintada da
Meshy, sem achatar. O mesmo caminho do vagao (docs/objetos3d/trem/textura_trem.py, PR #710), para a mesma densidade em todos os objetos.

  1. o realce leve (a limpeza que a regra nova deixa): o azul do casco, o amarelo da borda e o musgo saem da Meshy mais apagados que no
     esboco 1; so essas faixas de cor ganham saturacao. A madeira sai mais escura e mais lisa que no esboco: o brilho dela vai para o do
     esboco e o contraste entre as tabuas sobe um pouco (revisor, rodada 1). O resto (a corda, a lona) fica como veio;
  2. reduzida ao lado pedido (512: o orcamento de 300 KB do test/lugares3d.test.ts, com a malha);
  3. a mascara das ilhas da UV (onde a textura e usada): o enchimento fora delas fica chapado, para o PNG comprimir melhor;
  4. ate 256 cores com pontilhado (o cais usa 192, para caber nos 300 KB) (o PNG de paleta; no olho, igual ao RGB; nao e o achatamento antigo de 3 a 12 cores lisas).
uso (da raiz): python -I docs/objetos3d/cais/textura_cais.py <cais.gltf com as UVs> <textura da Meshy> <saida.png> <lado> <cores>
"""
import json, os, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# os numeros do realce, do olho contra o esboco 1: PROPOSTO, SEM FONTE
AZUL, AMARELO, VERDE = (190, 230), (36, 58), (65, 150)   # faixas de matiz, em graus
GANHO_AZUL, GANHO_AMARELO, GANHO_VERDE = 1.25, 1.2, 1.5  # multiplicam a saturacao
# a madeira (o revisor, rodada 1: "marrom-escuro quase chapado"): medida nos pixels de madeira (matiz 10 a 45 graus), a mediana do brilho da
# textura da Meshy e 0,396 e a do esboco 1 e 0,522, e a faixa p10 a p90 do esboco e 1,5 vez a da textura. O brilho da madeira vai para a
# mediana do esboco e o contraste entre as tabuas sobe CONTRASTE_MADEIRA (menos que 1,5, para o pontilhado nao estourar). PROPOSTO, SEM FONTE
MADEIRA = (10, 45)
V_MADEIRA_MESHY, V_MADEIRA_ESBOCO, CONTRASTE_MADEIRA, GANHO_MADEIRA = 0.396, 0.522, 1.3, 1.1


def realce(im: Image.Image) -> Image.Image:
    a = np.asarray(im.convert("HSV")).astype(np.float32)
    h, s, v = a[..., 0] * 360 / 255, a[..., 1] / 255, a[..., 2] / 255
    azul = (h >= AZUL[0]) & (h <= AZUL[1]) & (s > 0.25) & (v > 0.25)
    amarelo = (h >= AMARELO[0]) & (h <= AMARELO[1]) & (s > 0.35) & (v > 0.45)
    verde = (h >= VERDE[0]) & (h <= VERDE[1]) & (s > 0.15)
    s = np.where(azul, s * GANHO_AZUL, s)
    s = np.where(amarelo, s * GANHO_AMARELO, s)
    s = np.where(verde, s * GANHO_VERDE, s)
    madeira = (h >= MADEIRA[0]) & (h <= MADEIRA[1]) & (s > 0.15) & (s < 0.75) & (v > 0.12) & ~amarelo
    v = np.where(madeira, V_MADEIRA_ESBOCO + (v - V_MADEIRA_MESHY) * CONTRASTE_MADEIRA, v)
    s = np.where(madeira, s * GANHO_MADEIRA, s)
    out = np.stack([h * 255 / 360, np.minimum(1, s) * 255, np.clip(v, 0, 1) * 255], -1).clip(0, 255).astype(np.uint8)
    print("realce: azul", round(float(azul.mean()), 4), "amarelo", round(float(amarelo.mean()), 4), "verde", round(float(verde.mean()), 4), "madeira", round(float(madeira.mean()), 4))
    return Image.fromarray(out, "HSV").convert("RGB")


def mascara(gltf: str, lado: int, folga: int) -> Image.Image:
    g = json.loads(Path(gltf).read_text(encoding="utf-8"))
    buf = (Path(gltf).parent / g["buffers"][0]["uri"]).read_bytes()

    def acc(i, tipo, n):
        a = g["accessors"][i]
        v = g["bufferViews"][a["bufferView"]]
        o = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        r = np.frombuffer(buf, dtype=tipo, count=a["count"] * n, offset=o)
        return r.reshape(-1, n) if n > 1 else r

    p = g["meshes"][0]["primitives"][0]
    uv = acc(p["attributes"]["TEXCOORD_0"], np.float32, 2)
    ia = g["accessors"][p["indices"]]
    idx = acc(p["indices"], {5123: np.uint16, 5125: np.uint32}[ia["componentType"]], 1).reshape(-1, 3)
    m = Image.new("L", (lado, lado), 0)
    dr = ImageDraw.Draw(m)
    for t in idx:
        dr.polygon([(uv[k][0] * lado, uv[k][1] * lado) for k in t], fill=255, outline=255)
    return m.filter(ImageFilter.MaxFilter(folga * 2 + 1))


if __name__ == "__main__":
    gltf, ent, sai, lado, cores = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    im = realce(Image.open(ent).convert("RGB")).resize((lado, lado), Image.LANCZOS)
    m = mascara(gltf, lado, 3)
    print("cobertura", round(float(np.asarray(m).mean() / 255), 3))
    media = tuple(int(c) for c in np.asarray(im)[np.asarray(m) > 0].mean(0))
    im = Image.composite(im, Image.new("RGB", (lado, lado), media), m)
    if cores > 256:
        raise SystemExit("o PNG de paleta vai ate 256 cores")
    # cores 0: so o realce, em RGB (a fonte de cor do voxel_cais.py, que pinta cada bloco com uma cor so)
    if cores > 0:
        im = im.quantize(cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    im.save(sai, optimize=True)
    print(sai, os.path.getsize(sai) // 1024, "KB")
