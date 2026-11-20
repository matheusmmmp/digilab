"""A textura e a mascara do portao da arena pela regra nova (docs/objetos3d/REFERENCIAS.md, secao 5; docs/TAREFA_V3_LUGARES_3D.md, secao 14).

Sem achatar: a textura pintada da Meshy fica. So a limpeza leve e os retoques do revisor:
  - as manchas brancas (pixels quase brancos e sem cor: falhas nas emendas) recebem a cor da vizinhanca;
  - o dourado e o vermelho dos estandartes mais vivos, e um realce leve das juntas dos blocos;
  - o portal: a Meshy o pintou em dezenas de ilhas pequenas de UV, com a borda escura e encostadas em pedra, que viravam pontos e linhas na
    tela. O acabar_portao.py da ao portal uma ilha so, na faixa livre a direita do atlas (o atlas aperta para `aperto` da largura). Aqui a
    imagem aperta igual, e a ilha nova (a `ranhura`) recebe o portal da multivista da Meshy (vistas/vista_1.png, a vista de frente, imagem
    gerada para o DigiLab), com a grade e a espiral do esboco. Os cantos do recorte fora do arco recebem o ciano em volta, para a borda
    da ilha nunca puxar pedra.
Depois o lado cai para LADO e o PNG vai a paleta de CORES_PALETA cores com difusao (o detalhe pintado fica; e so para caber no orcamento
de 300 KB).

A mascara do portal (o emissiveMap, LUGARES_LUZ.portao): os triangulos de UV das faces do portal (previa_portal_uv.json, do
acabar_portao.py), com um borrao leve, no lado LADO_LUZ. Sai dos UVs novos, entao fica alinhada por construcao.

uso (da raiz):
  python -I docs/objetos3d/portao/textura_portao.py <textura_base_color.png> <vista_1.png> <previa_portal_uv.json> <cor.png> <luz.png> [<lado>]
  (a ordem: o acabar_portao.py uma vez para gravar os UVs do portal, este script com eles, e o acabar_portao.py de novo com a cor final;
  a deteccao do portal no acabar_portao.py le so a textura crua, entao os UVs saem iguais nas duas rodadas)
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# o lado da mascara: 512, o mesmo da cor (com a ilha unica do portal, a de 256 px saia com menos de 1 KB, e o teste "nao vazia" de
# test/lugares3d.test.ts pede mais)
LADO_LUZ = 512
# as cores da paleta do PNG: 240 (e nao 256) para os arquivos do portao caberem nos 300 KB (PROPOSTO, SEM FONTE)
CORES_PALETA = 240
# o ciano do portal (PROPOSTO, SEM FONTE: medido na textura da Meshy e na multivista)
MATIZ = (0.44, 0.56)  # 158 a 202 graus
SAT_MIN, VAL_MIN = 0.30, 0.55
# os retoques do revisor (PROPOSTO, SEM FONTE: olhados na vitrine e no jogo): o dourado e o vermelho dos estandartes, e o realce das juntas
OURO, VERMELHO = 1.25, 1.12
REALCE = dict(radius=1.5, percent=60, threshold=3)
# a borda em volta da ranhura do portal que recebe o ciano da borda (px da textura de 2 048), para a filtragem nao puxar o cinza de fora
BORDA_RANHURA = 12


def hsv(a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    f = a[..., :3].astype(np.float32) / 255
    mx, mn = f.max(-1), f.min(-1)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    return h, s, v


def ciano(a: np.ndarray) -> np.ndarray:
    h, s, v = hsv(a)
    return (h >= MATIZ[0]) & (h <= MATIZ[1]) & (s >= SAT_MIN) & (v >= VAL_MIN)


def crescer(rgb: np.ndarray, vazio: np.ndarray, passos: int) -> np.ndarray:
    """preenche os pixels vazios com a media dos vizinhos cheios, um anel por passo"""
    rgb, vazio = rgb.astype(np.float32).copy(), vazio.copy()
    for _ in range(passos):
        soma = np.zeros_like(rgb); n = np.zeros(vazio.shape, np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                c = np.roll(np.roll(~vazio, dy, 0), dx, 1)
                soma += np.roll(np.roll(rgb, dy, 0), dx, 1) * c[..., None]
                n += c
        novo = vazio & (n > 0)
        rgb[novo] = soma[novo] / n[novo][:, None]
        vazio = vazio & ~novo
        if not vazio.any():
            break
    return rgb


def portal_da_vista(arq: str) -> Image.Image:
    """o portal da vista de frente: o recorte das colunas e linhas com ciano (as que tem mais de 30 % do maximo, o que deixa de fora as
    flores ciano nas pedras), e os pixels do recorte fora do ciano (os cantos de pedra acima do arco) recebem o ciano em volta"""
    a = np.asarray(Image.open(arq).convert("RGBA"))
    m = ciano(a) & (a[..., 3] > 0)
    col, lin = m.sum(0), m.sum(1)
    xs, ys = np.where(col > 0.3 * col.max())[0], np.where(lin > 0.3 * lin.max())[0]
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rec, mr = a[y0:y1, x0:x1, :3], m[y0:y1, x0:x1]
    cheio = crescer(rec, ~mr, max(rec.shape))
    print("PORTAL da vista: o recorte", (int(x0), int(y0), int(x1), int(y1)), "; fora do ciano", int((~mr).sum()), "px preenchidos")
    return Image.fromarray(np.clip(cheio, 0, 255).astype(np.uint8), "RGB")


def main(ent: str, vista: str, uvs: str, sai: str, luz: str, lado: int = 512) -> None:
    j = json.loads(Path(uvs).read_text(encoding="utf-8"))
    a = np.asarray(Image.open(ent).convert("RGBA"))
    L = a.shape[0]
    h, s, v = hsv(a)
    branco = (s < 0.06) & (v > 0.93) & (a[..., 3] >= 8)
    rgb = crescer(a[..., :3], branco | (a[..., 3] < 8), 12)
    print("LIMPAR manchas brancas", int(branco.sum()), "px")
    h, s, v = hsv(np.clip(rgb, 0, 255).astype(np.uint8))
    ouro = (h >= 30 / 360) & (h <= 60 / 360) & (s >= 0.40) & (v >= 0.35)
    verm = ((h <= 15 / 360) | (h >= 345 / 360)) & (s >= 0.45)
    rgb[ouro] *= OURO
    rgb[verm] *= VERMELHO
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    print("RETOQUE ouro", int(ouro.sum()), "px; vermelho", int(verm.sum()), "px")

    # o atlas apertado a esquerda e a ilha do portal na faixa da direita (as coordenadas da ranhura sao de UV: o v cresce para cima)
    larg = round(j["aperto"] * L)
    atlas = Image.new("RGB", (L, L))
    atlas.paste(Image.fromarray(rgb, "RGB").resize((larg, L), Image.LANCZOS), (0, 0))
    u0, v0, u1, v1 = j["ranhura"]
    px0, px1, py0, py1 = round(u0 * L), round(u1 * L), round((1 - v1) * L), round((1 - v0) * L)
    atlas.paste(portal_da_vista(vista).resize((px1 - px0, py1 - py0), Image.LANCZOS), (px0, py0))
    at = np.asarray(atlas).copy()
    fora = np.ones((L, L), bool)
    fora[:, :larg] = False
    fora[py0:py1, px0:px1] = False
    at = np.clip(crescer(at, fora, BORDA_RANHURA), 0, 255).astype(np.uint8)
    print("ATLAS", larg, "px de", L, "para a pintura da Meshy; a ilha do portal em", (px0, py0, px1, py1))
    cor = Image.fromarray(at, "RGB").resize((lado, lado), Image.LANCZOS).filter(ImageFilter.UnsharpMask(**REALCE))
    q = cor.quantize(colors=CORES_PALETA, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(sai, optimize=True)
    print("COR", lado, "px;", len(q.getpalette()) // 3, "cores na paleta")

    m = Image.new("L", (L, L), 0)
    d = ImageDraw.Draw(m)
    for t in j["triangulos_uv"]:
        d.polygon([(u * L, (1 - w) * L) for u, w in t], fill=255)
    n = int((np.asarray(m) > 0).sum())
    m.filter(ImageFilter.GaussianBlur(2)).resize((LADO_LUZ, LADO_LUZ), Image.BILINEAR).save(luz, optimize=True)
    print("MASCARA", n, "px do portal de", L * L, "(", round(n / L / L * 100, 1), "% )")


if __name__ == "__main__":
    main(*sys.argv[1:6], *([int(sys.argv[6])] if len(sys.argv) > 6 else []))
