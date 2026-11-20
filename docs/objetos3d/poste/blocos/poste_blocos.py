"""O poste de luz em blocos, feito a mao por script (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 14; a direcao C escolhida pelo Matheus em
2026-11-08: "mais fino", "uma estetica mais pixelada", "mais digital").

A forma segue o esboco 1 (esbocos/esboco_1_ferro_hera.png: o ferro verde, a lanterna de vidro quente, a hera e a base de pedra com musgo),
traduzida em caixas, como os postes de voxel das referencias (capturas fora do git, em capturas_objetos3d/poste/referencias_pixel/). Nada
vem da Meshy nem de imagem de terceiros: as caixas (CAIXAS) e a pintura de cada material (pintar) estao aqui, e a mesma entrada da sempre
o mesmo arquivo.

  - a malha: cada caixa com as 5 faces de cima e dos lados (a de baixo nao aparece: a camera fica sempre acima), normais chapadas (o bloco);
  - a textura: cada face ganha um retangulo proprio no atlas, com PX texels por bloco (a mesma densidade em tudo, REFERENCIAS secao 5,
    item 4), pintado em pixel art pela posicao do texel no mundo (as pedras, o ferro, a hera e o musgo continuam de uma face para a outra);
    o atlas e ampliado AMPLIA vezes sem filtro e o glTF pede o filtro "nearest" na ampliacao (os pixels ficam duros de perto); a margem
    de cada retangulo repete a borda (o mipmap de longe nao puxa a cor do vizinho);
  - a mascara da luz (poste_luz.png, o emissiveMap; fora do glTF, gate G5): o miolo dos vidros, no mesmo atlas.

uso (da raiz): python -I docs/objetos3d/poste/blocos/poste_blocos.py <pasta de saida> [quente|digital]
"""
import json, math, struct, sys
from pathlib import Path
import numpy as np
from PIL import Image

PX, AMPLIA, ESCALA = 4, 4, 0.05  # texels por bloco, a ampliacao sem filtro, metros por bloco (a vista normaliza a altura)

# as caixas (x0, x1, y0, y1, z0, z1) em blocos, y para cima, a frente em +z; o material. PROPOSTO, SEM FONTE: desenhado olhando o esboco 1
CAIXAS: list[tuple[tuple[float, ...], str]] = [
    ((-4, 4, 0, 3, -4, 4), "pedra"),          # a base de pedra
    ((-3, 3, 3, 4, -3, 3), "pedra"),          # o degrau de pedra
    ((-2, 2, 4, 6, -2, 2), "ferro"),          # o pe do poste
    ((-1.5, 1.5, 6, 8, -1.5, 1.5), "ferro"),  # o alargado do pe (o revisor: o poste pesava em cima)
    ((-1, 1, 8, 28, -1, 1), "ferro"),         # o fuste fino, 2 blocos
    ((-1.6, 1.6, 10, 11, -1.6, 1.6), "ferro"),  # os aneis
    ((-1.6, 1.6, 20, 21, -1.6, 1.6), "ferro"),
    ((-2.6, 2.6, 25, 26, -0.5, 0.5), "ferro"),  # os bracos curtos (o revisor: compridos pareciam placa)
    ((-3.2, -2.4, 24.7, 26.3, -0.6, 0.6), "ferro"),
    ((2.4, 3.2, 24.7, 26.3, -0.6, 0.6), "ferro"),
    ((-1.5, 1.5, 27, 29, -1.5, 1.5), "latao"),  # o colar de latao
    ((-3, 3, 29, 30, -3, 3), "ferro"),         # o prato da lanterna
    ((-2.5, 2.5, 30, 37, -2.5, 2.5), "vidro"),  # os vidros
    ((-2.9, -2.1, 30, 37, -2.9, -2.1), "ferro"),  # as quinas da lanterna
    ((2.1, 2.9, 30, 37, -2.9, -2.1), "ferro"),
    ((-2.9, -2.1, 30, 37, 2.1, 2.9), "ferro"),
    ((2.1, 2.9, 30, 37, 2.1, 2.9), "ferro"),
    ((-3.5, 3.5, 37, 38, -3.5, 3.5), "teto"),   # o teto em degraus
    ((-2.5, 2.5, 38, 39, -2.5, 2.5), "teto"),
    ((-1.5, 1.5, 39, 40, -1.5, 1.5), "teto"),
    ((-3.7, -3.0, 38, 38.8, -3.7, -3.0), "ferro"),  # as pontas das quinas do teto
    ((3.0, 3.7, 38, 38.8, -3.7, -3.0), "ferro"),
    ((-3.7, -3.0, 38, 38.8, 3.0, 3.7), "ferro"),
    ((3.0, 3.7, 38, 38.8, 3.0, 3.7), "ferro"),
    ((-0.6, 0.6, 40, 42, -0.6, 0.6), "ferro"),   # o pinaculo
    ((-0.35, 0.35, 42, 43.2, -0.35, 0.35), "latao"),
    ((-3.6, -2.0, 4, 4.5, 1.2, 3.0), "musgo"),     # os tufos de musgo no degrau
    ((1.4, 3.4, 4, 4.4, -3.4, -2.2), "musgo"),
    ((2.0, 3.6, 3, 3.5, 3.0, 4.2), "musgo"),
]
# as folhas da hera que saltam do fuste: (lado, altura, deslocamento no lado) em blocos; cada folha e uma placa de 1,4 x 1,2 x 0,3
FOLHAS = [("+x", 7.5, 0.4), ("+z", 10.0, -0.5), ("+z", 11.2, 0.5), ("-x", 13.0, 0.3), ("-z", 15.5, 0.5), ("+x", 18.0, -0.4),
          ("+x", 19.2, 0.5), ("+z", 21.8, 0.4), ("-x", 23.5, -0.3), ("-z", 26.0, -0.4)]

PAL = {  # pixel art: 3 a 4 tons por material (PROPOSTO, SEM FONTE; os verdes e o latao do esboco 1)
    "ferro": [(40, 92, 64), (60, 126, 84), (86, 160, 104), (136, 204, 140)],
    "teto": [(28, 66, 48), (44, 96, 66), (64, 128, 84), (104, 172, 114)],
    "pedra": [(84, 86, 82), (118, 118, 108), (150, 148, 134), (184, 180, 160)],
    "musgo": [(54, 108, 38), (86, 150, 48), (132, 190, 66), (176, 220, 98)],
    "latao": [(112, 74, 28), (170, 122, 48), (214, 168, 78), (248, 222, 144)],
    "folha": [(26, 60, 28), (56, 124, 42), (92, 166, 58), (148, 208, 88)],
    "vidro": [(244, 182, 82), (255, 214, 118), (255, 236, 170), (255, 251, 226)],
    "vidro_digital": [(40, 150, 170), (70, 200, 214), (130, 236, 236), (220, 255, 250)],
}
# a cor da mascara da luz no vidro quente (o miolo, o meio e a borda): a luz da vista (LUZ_NINHO x 1,6) saia branca-creme; o revisor pediu
# o ambar do esboco. Indexado por [miolo][meio]. PROPOSTO, SEM FONTE
LUZ_VIDRO = {True: {True: (255, 214, 150), False: (255, 214, 150)}, False: {True: (255, 150, 70), False: (230, 104, 36)}}


def h(*v: float) -> float:
    """um acaso fixo por posicao (0 a 1), para a pintura nao depender da ordem"""
    s = 0
    for x in v:
        s = (s * 1000003) ^ (int(math.floor(x * 97.0)) & 0xFFFFFFFF)
    s = (s ^ (s >> 13)) * 0x5BD1E995 & 0xFFFFFFFF
    return ((s ^ (s >> 15)) & 0xFFFF) / 65535.0


def hera(p: np.ndarray) -> int:
    """a hera pintada no fuste e no pe (0 nada, 1 o ramo, 2 a folha escura, 3 a folha clara): um ramo em espiral com folhas"""
    x, y, z = p
    if not (4.5 <= y <= 27.5) or max(abs(x), abs(z)) > 2.05:
        return 0
    th = math.atan2(z, x)
    alvo = 2.2 + (y - 4.5) * 0.36 + 0.4 * math.sin(y * 0.7)
    d = abs((th - alvo + math.pi) % (2 * math.pi) - math.pi)
    if d < 0.3:
        return 1
    for k in range(-1, 2):  # as folhas em pares, alternando de lado
        yc = math.floor(y / 2.2) * 2.2 + 1.1 + k * 2.2
        ac = 2.2 + (yc - 4.5) * 0.36 + 0.4 * math.sin(yc * 0.7) + (0.5 if int(yc / 2.2) % 2 else -0.5)
        dd = abs((th - ac + math.pi) % (2 * math.pi) - math.pi)
        if (dd / 0.6) ** 2 + ((y - yc) / 0.75) ** 2 < 1:
            return 3 if y > yc - 0.15 else 2
    return 0


def pintar(mat: str, p: np.ndarray, n: tuple[int, int, int], i: int, j: int, w: int, hh: int, vidro: str) -> tuple[tuple[int, int, int], bool]:
    """a cor de um texel (e se ele acende a noite): o material, a posicao no mundo, a normal da face e o texel na face"""
    x, y, z = p
    borda = i == 0 or j == 0 or i == w - 1 or j == hh - 1
    if mat in ("ferro", "teto"):
        P = PAL[mat]
        c = P[1]
        if n[1] == 1 or (j == 0 and n[1] == 0):
            c = P[2]                               # o de cima mais claro
        if j == 0 and n[1] == 0 and mat == "teto":
            c = P[3]
        if borda and n[1] == 0 and (i == 0):
            c = P[2]
        if borda and n[1] == 0 and (i == w - 1 or j == hh - 1):
            c = P[0]                               # a quina de baixo e da direita escura (o bisel)
        r = h(round(x * PX), round(y * PX), round(z * PX), 3)
        if r < 0.04:
            c = P[0]                               # o descascado
        elif r > 0.96:
            c = P[3]                               # o brilho
        hr = hera(p) if mat == "ferro" else 0
        if hr == 1:
            c = PAL["folha"][1]
        elif hr in (2, 3):
            c = PAL["folha"][3]                    # a folha num tom so (o revisor: menos ruido de dia)
        return c, False
    if mat == "latao":
        P = PAL["latao"]
        c = P[2] if (j == 0 or n[1] == 1) else P[1]
        if i == w - 1 or j == hh - 1:
            c = P[0]
        if h(round(x * PX), round(y * PX), round(z * PX), 5) > 0.9:
            c = P[3]
        return c, False
    if mat == "pedra":
        P, M = PAL["pedra"], PAL["musgo"]
        # as pedras: fiadas de 1,5 bloco, pedras de 2,5 blocos desencontradas; a junta escura
        fy = math.floor(y / 1.5)
        hor = x if abs(n[0]) == 0 else z
        if n[1] == 1:
            hor, fy = x, math.floor(z / 2.0)
        off = 1.25 if fy % 2 else 0
        pc = math.floor((hor + off) / 2.5)
        junta = ((y % 1.5) < 1.0 / PX and n[1] == 0) or (((hor + off) % 2.5) < 1.0 / PX)
        if n[1] == 1:
            junta = ((z % 2.0) < 1.0 / PX) or (((x + off) % 2.5) < 1.0 / PX)
        tom = 1 + int(h(pc, fy, n[0], n[2]) * 2.99)
        c = P[0] if junta else P[min(tom, 3)]
        if not junta and h(round(x * PX), round(y * PX), round(z * PX), 7) < 0.08:
            c = P[max(tom - 1, 0)]
        # o musgo: em cima quase todo, e escorrendo nas fiadas de cima dos lados
        r = h(round(x * PX), round(z * PX), 11)
        if n[1] == 1 and r < 0.62:
            c = M[1 + int(h(round(x * PX), round(z * PX), 13) * 2.99)]
        if n[1] == 0 and (3 - y) < 0.9 + 1.2 * h(round(x * PX), round(z * PX), 17) and y > 1.2:
            c = M[1 + int(h(round(x * PX), round(y * PX), round(z * PX), 19) * 1.99)]
        return c, False
    if mat == "musgo":
        M = PAL["musgo"]
        return M[2 + (h(round(x * PX), round(z * PX), 23) > 0.6)] if n[1] == 1 else M[1 + (j == 0)], False
    if mat == "folha":
        F = PAL["folha"]
        if n[1] == 1 or (i + j) < (w + hh) * 0.35:
            return F[3], False                     # a luz no alto e a esquerda
        if i == w - 1 or j == hh - 1:
            return F[1], False                     # a sombra embaixo e a direita
        return F[2], False
    if mat == "vidro":
        V = PAL["vidro_digital" if vidro == "digital" else "vidro"]
        if n[1] != 0:
            return PAL["ferro"][0], False
        if i == 0 or i == w - 1 or j == 0 or j == hh - 1:
            return PAL["ferro"][1], False
        # a chama no meio: o miolo claro e o resto quente, mais escuro embaixo e nas bordas
        cx, cy = (w - 1) / 2, (hh - 1) * 0.55
        d = ((i - cx) / (w * 0.22)) ** 2 + ((j - cy) / (hh * 0.24)) ** 2
        c = V[3] if d < 0.45 else V[2] if d < 1.4 else V[1] if j < hh - 3 else V[0]
        if vidro == "digital" and (i % 4 == 0 or j % 4 == 0) and d >= 0.45:
            c = V[1]                               # a grade digital no vidro
        if i == 2 and 2 <= j <= 5:
            c = V[3]                               # o reflexo
        return c, True
    raise SystemExit("material desconhecido: " + mat)


def faces(cx: tuple[float, ...]):
    """as 5 faces de uma caixa (sem a de baixo): normal, canto de cima a esquerda, eixo u (direita) e eixo v (para baixo), tamanhos"""
    x0, x1, y0, y1, z0, z1 = cx
    yield (0, 1, 0), (x0, y1, z0), (1, 0, 0), (0, 0, 1), x1 - x0, z1 - z0
    yield (0, 0, 1), (x0, y1, z1), (1, 0, 0), (0, -1, 0), x1 - x0, y1 - y0
    yield (0, 0, -1), (x1, y1, z0), (-1, 0, 0), (0, -1, 0), x1 - x0, y1 - y0
    yield (1, 0, 0), (x1, y1, z1), (0, 0, -1), (0, -1, 0), z1 - z0, y1 - y0
    yield (-1, 0, 0), (x0, y1, z0), (0, 0, 1), (0, -1, 0), z1 - z0, y1 - y0


def folhas() -> list[tuple[tuple[float, ...], str]]:
    out = []
    for lado, y, d in FOLHAS:
        r = 1.0
        if lado in ("+x", "-x"):
            s = 1 if lado == "+x" else -1
            out.append(((min(s * r, s * (r + 0.3)), max(s * r, s * (r + 0.3)), y - 0.6, y + 0.6, d - 0.7, d + 0.7), "folha"))
        else:
            s = 1 if lado == "+z" else -1
            out.append(((d - 0.7, d + 0.7, y - 0.6, y + 0.6, min(s * r, s * (r + 0.3)), max(s * r, s * (r + 0.3))), "folha"))
    return out


def main(saida: str, vidro: str = "quente") -> None:
    pasta = Path(saida); pasta.mkdir(parents=True, exist_ok=True)
    todas = CAIXAS + folhas()
    # os retangulos das faces, empilhados em prateleiras (com 1 texel de margem)
    rets = []
    for cx, mat in todas:
        for n, o, u, v, wu, hv in faces(cx):
            rets.append((n, np.array(o, float), np.array(u, float), np.array(v, float), wu, hv, mat,
                         max(1, round(wu * PX)), max(1, round(hv * PX))))
    LADO = 128
    while True:
        x = y = alto = 0; pos = []; ok = True
        for r in sorted(range(len(rets)), key=lambda k: -rets[k][8]):
            w, hh = rets[r][7] + 2, rets[r][8] + 2
            if x + w > LADO:
                x, y, alto = 0, y + alto, 0
            if y + hh > LADO:
                ok = False; break
            pos.append((r, x + 1, y + 1)); x += w; alto = max(alto, hh)
        if ok:
            break
        LADO *= 2
    cor = np.zeros((LADO, LADO, 3), np.uint8); luz = np.zeros((LADO, LADO, 3), np.uint8)
    P, N, U, IDX = [], [], [], []
    for r, px, py in pos:
        n, o, u, v, wu, hv, mat, w, hh = rets[r]
        for j in range(hh):
            for i in range(w):
                p = o + u * (i + 0.5) / w * wu + v * (j + 0.5) / hh * hv
                c, acende = pintar(mat, p, n, i, j, w, hh, vidro)
                cor[py + j, px + i] = c
                if acende:  # a mascara colorida: o emissiveMap multiplica a cor da luz canal a canal; ambar, mais claro no miolo
                    luz[py + j, px + i] = LUZ_VIDRO[sum(c) > 700][sum(c) > 640] if vidro == "quente" else c
        # a margem repete a borda
        cor[py - 1, px:px + w] = cor[py, px:px + w]; cor[py + hh, px:px + w] = cor[py + hh - 1, px:px + w]
        cor[py - 1:py + hh + 1, px - 1] = cor[py - 1:py + hh + 1, px]; cor[py - 1:py + hh + 1, px + w] = cor[py - 1:py + hh + 1, px + w - 1]
        base = len(P)
        cantos = [o, o + u * wu, o + u * wu + v * hv, o + v * hv]
        uvs = [(px, py), (px + w, py), (px + w, py + hh), (px, py + hh)]
        for c3, (a, b) in zip(cantos, uvs):
            P.append(c3 * ESCALA); N.append(n); U.append((a / LADO, b / LADO))
        a3, b3, c3 = cantos[0], cantos[1], cantos[2]
        if np.dot(np.cross(b3 - a3, c3 - a3), n) > 0:
            IDX += [base, base + 1, base + 2, base, base + 2, base + 3]
        else:
            IDX += [base, base + 2, base + 1, base, base + 3, base + 2]
    # o pe no y = 0 e o centro no x = z = 0 ja vem das caixas
    P = np.array(P, np.float32); N = np.array(N, np.float32); U = np.array(U, np.float32); I = np.array(IDX, np.uint16)
    print("BLOCOS", len(todas), "caixas;", len(I) // 3, "triangulos; atlas", LADO, "px ->", LADO * AMPLIA, "px")
    Image.fromarray(cor, "RGB").resize((LADO * AMPLIA,) * 2, Image.NEAREST).quantize(colors=256, dither=Image.Dither.NONE).save(
        pasta / "poste_cor.png", optimize=True)
    Image.fromarray(luz, "RGB").resize((LADO * AMPLIA,) * 2, Image.NEAREST).save(pasta / "poste_luz.png", optimize=True)
    blob = b"".join(a.tobytes() for a in (P, N, U)) + I.tobytes()
    blob += b"\0" * (-len(blob) % 4)
    (pasta / "poste.bin").write_bytes(blob)
    o1, o2, o3 = P.nbytes, P.nbytes + N.nbytes, P.nbytes + N.nbytes + U.nbytes
    g = {
        "asset": {"version": "2.0", "generator": "docs/objetos3d/poste/blocos/poste_blocos.py"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"name": "poste", "mesh": 0}],
        "meshes": [{"name": "poste", "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2}, "indices": 3, "material": 0}]}],
        "materials": [{"name": "poste", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0, "roughnessFactor": 1}}],
        "textures": [{"sampler": 0, "source": 0}], "images": [{"uri": "poste_cor.png"}],
        "samplers": [{"magFilter": 9728, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071}],
        "buffers": [{"uri": "poste.bin", "byteLength": len(blob)}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": P.nbytes, "target": 34962},
                        {"buffer": 0, "byteOffset": o1, "byteLength": N.nbytes, "target": 34962},
                        {"buffer": 0, "byteOffset": o2, "byteLength": U.nbytes, "target": 34962},
                        {"buffer": 0, "byteOffset": o3, "byteLength": I.nbytes, "target": 34963}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(P), "type": "VEC3", "min": P.min(0).tolist(), "max": P.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(N), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(U), "type": "VEC2"},
            {"bufferView": 3, "componentType": 5123, "count": len(I), "type": "SCALAR"}],
    }
    (pasta / "poste.gltf").write_text(json.dumps(g, separators=(",", ":")), encoding="utf-8")
    alt = float(P[:, 1].max())
    print("ALTURA", round(alt / ESCALA, 2), "blocos; o meio dos vidros a", round(33.5 / (alt / ESCALA), 3), "da altura")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "quente")
