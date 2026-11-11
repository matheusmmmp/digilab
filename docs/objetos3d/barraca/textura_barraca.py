"""A textura da barraca refeita (docs/objetos3d/REFERENCIAS.md, secao 5): a textura pintada da Meshy fica como veio, sem achatar; so o
escuro de dentro e pintado nas faces vistas pelo vao da porta (interior.json), que a Meshy deixou brancas. A cor de dentro vem do esboco
(paredes cinza-azuladas escuras, o chao malva que clareia perto da porta) e guarda a variacao de pincel da textura (a luminancia local).
Sai em 1024 px.
A barraca nao tem chao por dentro (o raio que entra pela porta passa por baixo da parede do fundo); o chao novo (acabar_barraca.py) usa
um pedaco da maior face de baixo da lona, que nunca aparece, pintada com o degrade do chao (claro na porta, escuro no fundo); as UVs dos
quatro cantos saem em <chao_uv.json>.
As cordas: a Meshy as pintou cor de salmao, e o esboco as quer laranja; as faces compridas (maior lado > 0,25) fora do domo, fora do
banquinho, ganham o laranja do esboco com a variacao de pincel (o parecer do revisor, item 2).
uso: python -I textura_barraca.py <textura_meshy.png> <faces.json> <interior.json> <saida.png> <chao_uv.json>"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ent, faces, interior, sai, chao_uv = sys.argv[1:6]
img = Image.open(ent).convert("RGB")
W, H = img.size
a = np.asarray(img).astype(float) / 255
fs = json.load(open(faces))
ids = json.load(open(interior))
lum = a.mean(2)
lum_borrada = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12))).astype(float) / 255
PAREDE_FUNDO, PAREDE_PORTA = np.array([0.13, 0.13, 0.17]), np.array([0.22, 0.21, 0.26])
CHAO_FUNDO, CHAO_PORTA = np.array([0.15, 0.12, 0.15]), np.array([0.36, 0.29, 0.32])
Y_PORTA, Y_FUNDO = -0.45, 0.55
saida = a.copy()
for i in ids:
    f = fs[i]
    uv = np.array([(u * W, (1 - v) * H) for u, v in f["uv"]])
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in uv], fill=255, outline=255)
    m = np.asarray(m.filter(ImageFilter.MaxFilter(5))) > 0  # 2 px a mais, para o filtro do mipmap nao trazer o branco
    t = min(max((f["c"][1] - Y_PORTA) / (Y_FUNDO - Y_PORTA), 0), 1)
    if f["n"][2] > 0.5:
        cor = CHAO_PORTA * (1 - t) + CHAO_FUNDO * t
    else:
        cor = PAREDE_PORTA * (1 - t) + PAREDE_FUNDO * t
    var = np.clip(1 + 0.6 * (lum[m] - lum_borrada[m]), 0.8, 1.2)[:, None]
    saida[m] = np.clip(cor[None, :] * var, 0, 1)
# as cordas
zmin = min(f["c"][2] for f in fs)
LARANJA = np.array([0.95, 0.47, 0.16])
def cor_media(f):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(u * W, (1 - v) * H) for u, v in f["uv"]], fill=1)
    m = np.asarray(m).astype(bool)
    return a[m].mean(0) if m.any() else np.zeros(3)
def eh_corda(f):
    x, y, z = f["c"]
    v = np.array(f["v"])
    banquinho = 0.38 < x < 0.62 and -0.94 < y < -0.66
    if max(abs(x), abs(y)) <= 0.64 or z < zmin + 0.05 or np.ptp(v, axis=0).max() <= 0.25 or banquinho:
        return False
    r, g, b = cor_media(f)
    return r > g + 0.1 and r > b + 0.2      # o salmao da corda, nao a lona nem o musgo
cordas = [i for i, f in enumerate(fs) if eh_corda(f)]
for i in cordas:
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(u * W, (1 - v) * H) for u, v in fs[i]["uv"]], fill=255, outline=255)
    m = np.asarray(m.filter(ImageFilter.MaxFilter(5))) > 0
    var = np.clip(1 + 0.8 * (lum[m] - lum_borrada[m]), 0.8, 1.2)[:, None]
    saida[m] = np.clip(LARANJA[None] * var, 0, 1)
print("cordas", cordas)
# o chao: a maior face de baixo da lona (normal para baixo, no chao)
zmin = min(f["c"][2] for f in fs)
baixo = max((f for f in fs if f["n"][2] < -0.9 and f["c"][2] < zmin + 0.04), key=lambda f: f["a"])
A, B, C = (np.array([u * W, (1 - v) * H]) for u, v in baixo["uv"])
m = Image.new("L", (W, H), 0)
ImageDraw.Draw(m).polygon([tuple(A), tuple(B), tuple(C)], fill=255, outline=255)
m = np.asarray(m.filter(ImageFilter.MaxFilter(5))) > 0
ys, xs = np.nonzero(m)
M = np.column_stack([B - A, C - A])
st = np.linalg.solve(M, np.vstack([xs - A[0], ys - A[1]]))  # (s, t) de cada pixel
T0, T1 = 0.1, 0.45
t = np.clip((st[1] - T0) / (T1 - T0), 0, 1)[:, None]
var = np.clip(1 + 0.6 * (lum[m] - lum_borrada[m]), 0.85, 1.15)[:, None]
saida[ys, xs] = np.clip((CHAO_PORTA[None] * (1 - t) + CHAO_FUNDO[None] * t) * var, 0, 1)
def uv_de(s_, t_):
    p = A + s_ * (B - A) + t_ * (C - A)
    return [p[0] / W, 1 - p[1] / H]
# os cantos: frente-esquerda, frente-direita, fundo-direita, fundo-esquerda
json.dump({"cantos": [uv_de(0.1, T0), uv_de(0.45, T0), uv_de(0.45, T1), uv_de(0.1, T1)], "face_de_baixo": fs.index(baixo)},
          open(chao_uv, "w"), indent=1)
out = Image.fromarray((saida * 255).round().astype(np.uint8)).resize((1024, 1024), Image.LANCZOS)
out.save(sai, optimize=True)
print("textura", sai, out.size, "faces de dentro", len(ids))
