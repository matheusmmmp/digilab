"""O carro abandonado, feito a mao por script (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 15; pedido do Matheus em 2026-11-09: o carro
da Meshy, mesmo com a textura em cartoon, continuava "muito feio").

O desenho segue o esboco 1 (esbocos/esboco_1_hatch_retro.png: o hatch retro azul, a ferrugem, o musgo e o jardim no teto), mas nada vem
da Meshy nem de imagem de terceiros: a carroceria e uma superficie por secoes (secao), as pecas (rodas, para-choques, farois, molduras,
retrovisores, musgo, capim e flores) sao solidos simples, e a pintura (pinta_*) e uma funcao da posicao no espaco. A mesma entrada da
sempre o mesmo arquivo.

  - a malha: uma so, com as normais suaves por peca; a frente em +z, o chao em y = 0;
  - a textura: cada peca e cortada pela direcao da face (seis cartas por peca) e projetada no plano; o atlas e pintado triangulo a
    triangulo, pela posicao 3D de cada texel, no dobro do tamanho, e reduzido (as bordas do desenho saem suaves); as margens repetem a
    borda (o mipmap nao puxa o fundo).

uso (da raiz): python -I docs/objetos3d/carro/mao/carro_mao.py <pasta de saida>
"""
import json, math, struct, sys
from pathlib import Path
import numpy as np
from PIL import Image

LADO, SUPER, MARGEM = 1024, 2, 6   # o lado do atlas, a superamostragem da pintura e a margem de cada carta (texels do atlas)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
WM, CINTA, TOMBO = 0.56, 0.70, 0.30          # a meia largura, a altura da cinta (a base dos vidros) e o quanto a cabine fecha para cima
ZF = 0.985                                   # a ponta (a frente em +z, a traseira em -z)
TOPO = np.array([(-0.985, 0.60), (-0.93, 0.76), (-0.80, 0.88), (-0.45, 1.22), (0.14, 1.20), (0.42, 0.74), (0.70, 0.71), (0.90, 0.66),
                 (0.96, 0.62), (0.985, 0.58)])   # a linha de cima, de perfil: a traseira, o vidro de tras, o teto, o para-brisa, o capo
ESTACOES = [-0.985, -0.96, -0.92, -0.86, -0.80, -0.70, -0.60, -0.45, -0.30, -0.14, 0.0, 0.14, 0.24, 0.33, 0.42, 0.52, 0.62, 0.72, 0.80,
            0.87, 0.92, 0.96, 0.985]
RODA_R, RODA_L, RODA_Y, RODA_Z, RODA_X = 0.21, 0.16, 0.21, 0.60, 0.515   # o raio, a largura, a altura do eixo, o z dos eixos e o x do centro

AZUL, AZUL_CLARO, AZUL_ESC = (92, 168, 230), (140, 200, 244), (62, 128, 196)
TRACO = (28, 48, 78)
FERRUGEM, FERRUGEM_ESC = (190, 98, 48), (140, 62, 30)
MUSGO, MUSGO_ESC, MUSGO_CLARO = (112, 190, 66), (66, 146, 52), (170, 226, 110)
VIDRO, VIDRO_ESC, BRILHO = (176, 222, 240), (126, 186, 216), (244, 252, 255)
CINZA, CINZA_ESC, CROMO = (176, 186, 196), (104, 114, 128), (222, 228, 234)
PNEU, PNEU_CLARO, CAIXA_RODA = (44, 46, 58), (70, 72, 86), (26, 30, 42)
FAROL, FAROL_ESC, PISCA, LANTERNA = (255, 240, 170), (236, 200, 104), (250, 160, 50), (224, 66, 52)
TERRA, ROSA, MIOLO = (84, 52, 34), (246, 140, 210), (255, 226, 96)


def ytopo(z): return np.interp(z, TOPO[:, 0], TOPO[:, 1])


def ponta(z):
    """0 no meio do carro, 1 na ponta: o arredondado da frente e da traseira"""
    return np.clip((np.abs(z) - 0.62) / (ZF - 0.62), 0, 1)


def largura(z):
    u = ponta(z)
    return WM * (0.80 + 0.20 * np.cbrt(1 - u ** 3))


def ybaixo(z):
    u = ponta(z)
    return 0.22 + 0.06 * u * u * (3 - 2 * u)


def medidas(z):
    """da secao em z: a meia largura, o topo, o fundo, o ombro (onde a lateral vira capo ou coluna) e a meia largura do teto"""
    w, yt, yb = largura(z), ytopo(z), ybaixo(z)
    ws, ysh = w - 0.02, np.minimum(CINTA, yt - 0.09)
    wr = ws - TOMBO * np.maximum(0, yt - 0.03 - ysh)
    return w, yt, yb, ws, ysh, wr


def secao(z: float) -> np.ndarray:
    """os 19 pontos da secao em z, da soleira esquerda, por cima, ate a soleira direita"""
    w, yt, yb, ws, ysh, wr = (float(v) for v in medidas(z))
    yte = yt - 0.03
    lerp = lambda t: (wr + (ws - wr) * t, yte + (ysh - yte) * t)
    meia = [(0.0, yt), (0.5 * wr, yt - 0.004), (0.9 * wr, yt - 0.012), lerp(0.12), lerp(0.55), (ws, ysh), (w, ysh - 0.05),
            (w + 0.015, (ysh + yb) / 2), (w - 0.005, yb + 0.06), (w - 0.07, yb)]
    pts = [(-x, y, z) for x, y in reversed(meia[1:])] + [(x, y, z) for x, y in meia]
    return np.array(pts)


# ---------------------------------------------------------------- os solidos
def normais(V: np.ndarray, F: np.ndarray) -> np.ndarray:
    n = np.zeros_like(V)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3):
        np.add.at(n, F[:, k], fn)
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)


def orientar(V: np.ndarray, F: np.ndarray, centro=None) -> np.ndarray:
    """vira todas as faces se elas olham para dentro (a peca tem as faces num sentido so)"""
    c = V.mean(axis=0) if centro is None else np.array(centro)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    fora = (fn * (V[F].mean(axis=1) - c)).sum()
    return F if fora > 0 else F[:, ::-1].copy()


class Peca:
    def __init__(self, nome, V, F, pinta, N=None, centro=None, dois_lados=False):
        self.nome, self.V = nome, np.asarray(V, float)
        F = np.asarray(F, int)
        F = F if dois_lados else orientar(self.V, F, centro)
        self.N = normais(self.V, F) if N is None else np.asarray(N, float)
        self.F = np.vstack([F, F[:, ::-1]]) if dois_lados else F
        self.pinta = pinta


def carroceria() -> Peca:
    aneis = [secao(z) for z in ESTACOES]
    V, F, k = np.vstack(aneis), [], len(aneis[0])
    for i in range(len(aneis) - 1):
        for j in range(k - 1):
            a, b, c, d = i * k + j, i * k + j + 1, (i + 1) * k + j + 1, (i + 1) * k + j
            F += [(a, b, c), (a, c, d)]
    for i, dz in ((0, -0.012), (len(aneis) - 1, 0.012)):   # as tampas da traseira e da frente, em leque
        anel = aneis[i]
        centro = len(V)
        V = np.vstack([V, [[0, (anel[:, 1].min() + anel[:, 1].max()) / 2, anel[0, 2] + dz]]])
        par = [(centro, i * k + j, i * k + (j + 1) % k) for j in range(k)]
        F += par if i else [(a, c, b) for a, b, c in par]
    return Peca("carroceria", V, F, pinta_carroceria, centro=(0, 0.6, 0))


def tubo(nome, caminho, ref, ru, rv, pinta, n=8, escala=None, quina=2.0) -> Peca:
    """uma secao (a superelipse de raios ru e rv, com n lados) levada pelo caminho; ref escolhe o eixo de rv; as pontas fecham em leque"""
    P = np.asarray(caminho, float)
    V, F = [], []
    for i, p in enumerate(P):
        t = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]
        t /= np.linalg.norm(t)
        u = np.cross(ref, t); u /= np.linalg.norm(u)
        v = np.cross(t, u)
        e = 1.0 if escala is None else escala[i]
        for j in range(n):
            a = 2 * math.pi * (j + 0.5) / n
            c, s = math.cos(a), math.sin(a)
            c, s = math.copysign(abs(c) ** (2 / quina), c), math.copysign(abs(s) ** (2 / quina), s)
            V.append(p + u * (ru * e * c) + v * (rv * e * s))
    for i in range(len(P) - 1):
        for j in range(n):
            a, b, c, d = i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            F += [(a, b, c), (a, c, d)]
    for i, sinal in ((0, 1), (len(P) - 1, -1)):
        centro = len(V); V.append(P[i])
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            F.append((centro, b, a) if sinal > 0 else (centro, a, b))
    return Peca(nome, V, F, pinta)


def roda(nome, lado: int, z: float) -> Peca:
    n, xo, xi = 14, lado * (RODA_X + RODA_L / 2), lado * (RODA_X - RODA_L / 2)
    V, F = [], []
    for x, r in ((xi, RODA_R), (xo, RODA_R), (xo + lado * 0.012, RODA_R * 0.80)):
        for j in range(n):
            a = 2 * math.pi * j / n
            V.append((x, RODA_Y + r * math.sin(a), z + r * math.cos(a)))
    centro = len(V); V.append((xo + lado * 0.03, RODA_Y, z))
    for j in range(n):
        j1 = (j + 1) % n
        F += [(j, j1, n + j1), (j, n + j1, n + j), (n + j, n + j1, 2 * n + j1), (n + j, 2 * n + j1, 2 * n + j), (2 * n + j, 2 * n + j1, centro)]
    return Peca(nome, V, F, lambda P, N: pinta_roda(P, N, z), centro=(lado * RODA_X, RODA_Y, z))


def cupula(nome, c, eixo, r, h, pinta, n=10, ondas=0.0, fase=0.0) -> Peca:
    """uma calota de raio r e altura h em volta do eixo; ondas mexe o raio em volta (o musgo)"""
    c, eixo = np.asarray(c, float), np.asarray(eixo, float) / np.linalg.norm(eixo)
    u = np.cross(eixo, (0, 0, 1) if abs(eixo[2]) < 0.9 else (1, 0, 0)); u /= np.linalg.norm(u)
    v = np.cross(eixo, u)
    V, F = [], []
    for fr, fh in ((1.0, 0.0), (0.72, 0.62)):
        for j in range(n):
            a = 2 * math.pi * j / n
            rr = r * fr * (1 + ondas * math.sin(3 * a + fase) + 0.6 * ondas * math.sin(5 * a + 2 * fase))
            V.append(c + u * (rr * math.cos(a)) + v * (rr * math.sin(a)) + eixo * (h * fh))
    topo = len(V); V.append(c + eixo * h)
    for j in range(n):
        j1 = (j + 1) % n
        F += [(j, j1, n + j1), (j, n + j1, n + j), (n + j, n + j1, topo)]
    return Peca(nome, V, F, pinta, centro=c - eixo * r)


def caixa(nome, c, t, pinta) -> Peca:
    c, t = np.asarray(c, float), np.asarray(t, float) / 2
    V = [c + t * (sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    F = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return Peca(nome, V, F, pinta)


def folha(nome, base, ponta_, larg, pinta) -> Peca:
    """uma folha de capim: tres triangulos, uma dobra no meio, os dois lados"""
    b, p = np.asarray(base, float), np.asarray(ponta_, float)
    d = p - b
    s = np.cross(d, (0, 1, 0)); s = s / max(np.linalg.norm(s), 1e-9) * larg
    meio = b + d * 0.55 + np.array((d[0], 0, d[2])) * 0.18
    V = [b - s, b + s, meio - s * 0.7, meio + s * 0.7, p]
    F = [(0, 1, 3), (0, 3, 2), (2, 3, 4)]
    return Peca(nome, V, F, pinta, N=np.tile((0.0, 1.0, 0.0), (5, 1)), dois_lados=True)


# ---------------------------------------------------------------- a pintura (P e N por texel; devolve RGB 0..255)
def cor(c, k): return np.tile(np.array(c, float), (k, 1))


def por(base, mascara, c):
    base[mascara] = c
    return base


def ruido(P, f, fase):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    return (np.sin(f * (1.0 * x + 0.31 * y - 0.20 * z) + fase) + np.sin(f * 1.7 * (0.23 * x + 1.0 * y + 0.37 * z) + 2.1 * fase)
            + np.sin(f * 1.3 * (-0.29 * x + 0.17 * y + 1.0 * z) + 3.3 * fase)) / 3


def mancha(P, c, r, fase, f=13.0):
    """a distancia relativa a uma mancha de borda ondulada: < 1 dentro"""
    return np.linalg.norm(P - np.array(c), axis=1) / (r * (1 + 0.42 * ruido(P, 0.9 / r, fase) + 0.14 * ruido(P, 2.6 / r, 2 * fase)))


def poligono(z, y, pts):
    """a distancia com sinal a um poligono convexo no plano (negativa dentro); os pontos no sentido anti-horario"""
    d = np.full(z.shape, -1e9)
    for (az, ay), (bz, by) in zip(pts, pts[1:] + pts[:1]):
        ez, ey = bz - az, by - ay
        L = math.hypot(ez, ey)
        d = np.maximum(d, ((z - az) * ey - (y - ay) * ez) / L)
    return d


# as manchas de ferrugem e de musgo: o centro, o raio, a fase. PROPOSTO, SEM FONTE: espalhadas olhando o esboco 1
FERRUGENS = [((0.22, 0.71, 0.66), 0.10, 0.3), ((-0.30, 0.70, 0.52), 0.06, 1.1), ((0.57, 0.50, 0.12), 0.085, 2.0), ((0.57, 0.58, -0.80), 0.10, 2.7),
             ((-0.57, 0.52, -0.25), 0.08, 3.5), ((-0.57, 0.56, 0.70), 0.07, 4.2), ((-0.24, 1.21, 0.02), 0.07, 5.0), ((0.30, 0.95, -0.66), 0.07, 5.6),
             ((0.44, 0.50, 0.99), 0.05, 0.9), ((-0.20, 0.52, -0.99), 0.07, 1.9)]
MUSGOS = [((-0.24, 0.71, 0.62), 0.11, 0.5), ((0.30, 1.21, -0.34), 0.10, 1.4), ((-0.26, 1.21, -0.26), 0.08, 2.2), ((0.20, 0.74, 0.44), 0.07, 3.0),
          ((-0.30, 0.88, -0.80), 0.09, 3.9)]
BURACO = (0.02, -0.14, 0.16, 0.20)   # o buraco do teto, de onde sai o jardim: o x e o z do centro, os raios em x e em z
JANELA = [(0.33, 0.765), (0.105, 1.125), (-0.44, 1.14), (-0.66, 0.92), (-0.66, 0.765)]   # o vidro lateral, no plano (z, y)


def pinta_carroceria(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    ax = np.abs(x)
    w, yt, yb, ws, ysh, wr = medidas(z)
    lado = (np.abs(N[:, 0]) > 0.55) & (ax > 0.30)
    cima = N[:, 1] > 0.55
    c = cor(AZUL, len(P))
    por(c, N[:, 1] > 0.80, AZUL_CLARO)                         # o brilho chapado do que olha para cima
    por(c, (y < yb + 0.11) & (N[:, 1] < 0.3), AZUL_ESC)        # a saia mais escura
    por(c, lado & (y < ysh - 0.085) & (y > ysh - 0.115) & (np.abs(z) < 0.86), AZUL_CLARO)   # o friso claro no ombro
    # a ferrugem: a barra de baixo (a borda em onda), as manchas e a volta das caixas de roda
    onda = yb + 0.085 + 0.035 * np.sin(z * 17 + 1.3 * np.sign(x)) + 0.02 * np.sin(z * 41)
    por(c, (y < onda) & (N[:, 1] < 0.3), FERRUGEM)
    por(c, (y < onda - 0.05) & (N[:, 1] < 0.3), FERRUGEM_ESC)
    for centro, r, fase in FERRUGENS:
        d = mancha(P, centro, r, fase)
        por(c, d < 1, FERRUGEM)
        if abs(centro[0]) > 0.5:   # na lateral a ferrugem escorre
            por(c, lado & (np.abs(z - centro[2] - 0.2 * r) < 0.16 * r) & (y < centro[1]) & (y > centro[1] - 2.1 * r), FERRUGEM)
            por(c, lado & (np.abs(z - centro[2] + 0.45 * r) < 0.11 * r) & (y < centro[1]) & (y > centro[1] - 1.5 * r), FERRUGEM)
        nucleo = (centro[0] + 0.15 * r, centro[1] + 0.1 * r, centro[2] - 0.2 * r)
        por(c, (d < 1) & (mancha(P, nucleo, 0.55 * r, fase + 1.7) < 1), FERRUGEM_ESC)
    for zc in (RODA_Z, -RODA_Z):
        rr = np.hypot(z - zc, y - RODA_Y)
        por(c, lado & (rr < RODA_R + 0.10 + 0.035 * ruido(P, 21, zc)) & (y > RODA_Y - 0.02), FERRUGEM)
    # o musgo, so no que olha para cima
    for centro, r, fase in MUSGOS:
        d = mancha(P, centro, r, fase, 15.0)
        por(c, (d < 1) & (N[:, 1] > 0.25), MUSGO_ESC); por(c, (d < 0.78) & (N[:, 1] > 0.25), MUSGO)
    # as linhas da lataria: a porta, a macaneta, o corte do capo
    porta = lado & (y > yb + 0.03) & (y < CINTA + 0.02)
    por(c, porta & ((np.abs(z - 0.40) < 0.008) | (np.abs(z + 0.15) < 0.008)), TRACO)
    por(c, lado & (np.abs(z - 0.125) < 0.30) & (np.abs(y - (yb + 0.045)) < 0.006) & (z < 0.40) & (z > -0.15), TRACO)
    por(c, lado & (np.abs(z + 0.07) < 0.05) & (np.abs(y - 0.615) < 0.018), CROMO)
    capo = cima & (z > 0.45) & (z < 0.93)
    por(c, capo & (np.abs(ax - (ws - 0.11)) < 0.006), TRACO)
    por(c, cima & (np.abs(z - 0.45) < 0.006) & (ax < ws - 0.11), TRACO)
    por(c, cima & (np.abs(z - 0.93) < 0.005) & (ax < ws - 0.11), TRACO)
    # os vidros: o lateral (com a coluna do meio), o para-brisa e o de tras; a moldura escura em volta
    d = poligono(z, y, JANELA)
    coluna = np.abs(z + 0.15) < 0.028
    por(c, lado & (d < 0.028), TRACO)
    vl = lado & (d < 0) & ~coluna
    por(c, vl, VIDRO); por(c, vl & (y < 0.80 + 0.35 * (0.33 - z) * 0.25), VIDRO_ESC)
    risco = (z + 0.55 * y) % 0.46
    por(c, vl & ((risco < 0.045) | ((risco > 0.075) & (risco < 0.095))), BRILHO)
    topo = (y > yt - 0.075) & (np.abs(N[:, 0]) < 0.6)
    for z0, z1, folga, frente in ((0.165, 0.395, 0.075, True), (-0.775, -0.505, 0.09, False)):
        dz = np.minimum(z - z0, z1 - z)
        dx = (wr - folga) - ax
        dd = np.minimum(dz, dx)
        por(c, topo & (dd > -0.026), TRACO)
        v = topo & (dd > 0)
        por(c, v, VIDRO); por(c, v & ((z - z0) / (z1 - z0) < (0.34 if frente else 0.30) + 0.25 * x), VIDRO_ESC)
        risco = (x + 0.8 * z) % 0.52
        por(c, v & ((risco < 0.05) | ((risco > 0.085) & (risco < 0.105))), BRILHO)
        if frente:   # os limpadores
            for x0 in (-0.24, 0.02):
                t = (x - x0) / 0.22
                por(c, v & (t > 0) & (t < 1) & (np.abs(z - (z1 - 0.03 - 0.075 * t)) < 0.006), TRACO)
    # o buraco do teto: a terra dentro, a ferrugem em volta
    bx, bz, rx, rz = BURACO
    rb = np.hypot((x - bx) / rx, (z - bz) / rz) / (1 + 0.14 * np.sin(5 * np.arctan2(z - bz, x - bx) + 0.7))
    por(c, cima & (rb < 1.32) & (y > 1.1), FERRUGEM); por(c, cima & (rb < 1.14) & (y > 1.1), FERRUGEM_ESC); por(c, cima & (rb < 1) & (y > 1.1), TERRA)
    # as caixas de roda
    for zc in (RODA_Z, -RODA_Z):
        por(c, lado & (np.hypot(z - zc, y - RODA_Y) < RODA_R + 0.045), CAIXA_RODA)
    # a frente: a grade, o emblema, os piscas; a traseira: as lanternas e a placa
    fr = (N[:, 2] > 0.5) & (z > 0.93)
    g = fr & (ax < 0.20) & (y > 0.375) & (y < 0.475)
    por(c, fr & (ax < 0.215) & (y > 0.36) & (y < 0.49), CROMO); por(c, g, CAIXA_RODA); por(c, g & (((y - 0.375) / 0.025) % 1 < 0.32), CINZA)
    por(c, fr & (np.hypot(x, y - 0.535) < 0.022), CROMO)
    por(c, fr & (np.abs(ax - 0.33) < 0.05) & (np.abs(y - 0.375) < 0.016), PISCA)
    tr = (N[:, 2] < -0.5) & (z < -0.93)
    lan = tr & (np.abs(ax - 0.36) < 0.065) & (y > 0.42) & (y < 0.56)
    por(c, tr & (np.abs(ax - 0.36) < 0.078) & (y > 0.407) & (y < 0.573), TRACO); por(c, lan, LANTERNA); por(c, lan & (y > 0.515), PISCA)
    por(c, tr & (ax < 0.135) & (y > 0.385) & (y < 0.485), TRACO); por(c, tr & (ax < 0.12) & (y > 0.40) & (y < 0.47), (240, 236, 220))
    por(c, tr & (np.abs(y - 0.60) < 0.005) & (ax < 0.30), TRACO)
    return c


def pinta_roda(P, N, zc):
    r = np.hypot(P[:, 2] - zc, P[:, 1] - RODA_Y)
    ang = np.arctan2(P[:, 1] - RODA_Y, P[:, 2] - zc)
    face = np.abs(N[:, 0]) > 0.5
    c = cor(PNEU, len(P))
    por(c, ~face & ((ang * 9 / math.pi) % 1 < 0.38), PNEU_CLARO)            # os gomos da banda
    por(c, face & (r < RODA_R * 0.86) & (r > RODA_R * 0.80), PNEU_CLARO)   # o friso do pneu
    por(c, face & (r < RODA_R * 0.64), TRACO)
    por(c, face & (r < RODA_R * 0.60), CINZA)
    furo = np.hypot(r - RODA_R * 0.40, 0) < RODA_R * 0.085
    por(c, face & furo & ((ang * 5 / (2 * math.pi)) % 1 < 0.5), CINZA_ESC)
    por(c, face & (r < RODA_R * 0.22), CROMO)
    por(c, face & (r < RODA_R * 0.09), CINZA_ESC)
    return c


def pinta_parachoque(P, N):
    c = cor(CINZA, len(P))
    por(c, N[:, 1] > 0.5, CROMO); por(c, N[:, 1] < -0.3, CINZA_ESC)
    for centro, fase in (((0.34, 0.28, 1.0), 0.4), ((-0.12, 0.28, 1.03), 1.7), ((-0.30, 0.28, -1.0), 2.9), ((0.40, 0.28, -0.98), 4.4)):
        d = mancha(P, centro, 0.07, fase, 19.0)
        por(c, d < 1, FERRUGEM); por(c, d < 0.45, FERRUGEM_ESC)
    return c


def pinta_moldura(P, N):
    c = cor(AZUL_ESC, len(P))
    por(c, N[:, 1] > 0.45, AZUL)
    por(c, ruido(P, 23, 1.0) > 0.25, FERRUGEM)
    return c


def pinta_farol(P, N, c0, eixo, r):
    d = P - np.array(c0)
    fora = np.linalg.norm(d - np.outer(d @ eixo, eixo), axis=1) / r
    c = cor(FAROL, len(P))
    por(c, (d[:, 1] < -0.2 * r), FAROL_ESC)
    por(c, (np.hypot(d[:, 0] + 0.3 * r, d[:, 1] - 0.3 * r) < 0.26 * r), BRILHO)
    por(c, fora > 0.80, CROMO); por(c, fora > 0.93, CINZA_ESC)
    return c


def pinta_retrovisor(P, N):
    c = cor(AZUL, len(P))
    por(c, N[:, 1] > 0.5, AZUL_CLARO); por(c, N[:, 2] < -0.5, VIDRO); por(c, N[:, 1] < -0.5, AZUL_ESC)
    return c


def pinta_musgo(P, N):
    c = cor(MUSGO, len(P))
    por(c, N[:, 1] > 0.86, MUSGO_CLARO); por(c, N[:, 1] < 0.42, MUSGO_ESC)
    return c


def pinta_folha(y0, y1):
    """tres faixas chapadas pela altura, sem degrade"""
    return lambda P, N: por(por(cor(MUSGO, len(P)), (P[:, 1] - y0) / (y1 - y0) < 0.38, MUSGO_ESC), (P[:, 1] - y0) / (y1 - y0) > 0.72, MUSGO_CLARO)


def pinta_flor(P, N, c0, r):
    d = np.linalg.norm(P - c0, axis=1) / r
    return por(cor(ROSA, len(P)), d < 0.62, MIOLO)


# ---------------------------------------------------------------- o carro inteiro
def ysuperficie(x, z):
    """a altura da lataria em (x, z), no capo e no teto (para assentar o musgo)"""
    return float(ytopo(z)) - 0.012 * (abs(x) / max(float(medidas(z)[5]), 1e-6)) ** 2


def pecas() -> list[Peca]:
    ps = [carroceria()]
    for lado in (1, -1):
        for z in (RODA_Z, -RODA_Z):
            nome = f"{'d' if lado > 0 else 'e'}{'f' if z > 0 else 't'}"
            ps.append(roda("roda_" + nome, lado, z))
            arco = [(lado * (float(largura(z + (RODA_R + 0.055) * math.cos(a))) + 0.012), RODA_Y + (RODA_R + 0.055) * math.sin(a),
                     z + (RODA_R + 0.055) * math.cos(a)) for a in np.radians(np.linspace(-8, 188, 9))]
            ps.append(tubo("moldura_" + nome, arco, (lado, 0, 0), 0.030, 0.034, pinta_moldura, n=5, escala=[0.6] + [1] * 7 + [0.6]))
    for sinal, nome in ((1, "frente"), (-1, "tras")):
        xs = np.linspace(-0.49, 0.49, 9)
        caminho = [(x, 0.285, sinal * (1.035 - 0.115 * abs(x / 0.49) ** 3)) for x in xs]
        ps.append(tubo("parachoque_" + nome, caminho, (0, 1, 0), 0.050, 0.058, pinta_parachoque, n=8, escala=[0.7] + [1] * 7 + [0.7], quina=3.0))
    for lado in (1, -1):
        c0, eixo = np.array((lado * 0.325, 0.475, 0.968)), np.array((lado * 0.25, 0.12, 1.0))
        eixo = eixo / np.linalg.norm(eixo)
        ps.append(cupula("farol_" + ("d" if lado > 0 else "e"), c0, eixo, 0.108, 0.06,
                         lambda P, N, c0=c0, eixo=eixo: pinta_farol(P, N, c0, eixo, 0.108), n=12))
        ps.append(caixa("retrovisor_" + ("d" if lado > 0 else "e"), (lado * 0.615, 0.765, 0.36), (0.10, 0.075, 0.05), pinta_retrovisor))
        ps.append(caixa("haste_" + ("d" if lado > 0 else "e"), (lado * 0.555, 0.745, 0.365), (0.06, 0.025, 0.03), pinta_retrovisor))
    # o musgo em relevo: o x, o z, o raio, a altura, a fase; assentado na lataria
    for i, (x, z, r, h, fase) in enumerate([(-0.24, 0.62, 0.105, 0.06, 0.4), (0.30, -0.34, 0.095, 0.055, 1.3), (-0.27, -0.27, 0.075, 0.05, 2.2),
                                            (0.20, 0.46, 0.065, 0.045, 3.1), (-0.30, -0.80, 0.08, 0.05, 4.0), (0.10, -0.14, 0.11, 0.05, 5.2)]):
        ps.append(cupula(f"musgo_{i}", (x, ysuperficie(x, z) - 0.012, z), (0, 1, 0), r, h, pinta_musgo, n=8, ondas=0.16, fase=fase))
    # o jardim do teto: as folhas (o angulo, o afastamento da base, a altura, a inclinacao) e as flores
    bx, bz = BURACO[0], BURACO[1]
    y0 = ysuperficie(bx, bz) - 0.01
    folhas = [(0.3, 0.03, 0.34, 0.10), (1.2, 0.05, 0.27, 0.16), (2.0, 0.04, 0.36, 0.07), (2.9, 0.06, 0.24, 0.18), (3.7, 0.03, 0.31, 0.12),
              (4.5, 0.06, 0.26, 0.17), (5.3, 0.04, 0.38, 0.06), (0.8, 0.09, 0.18, 0.20), (2.5, 0.10, 0.17, 0.21), (4.1, 0.10, 0.19, 0.19),
              (5.8, 0.09, 0.20, 0.18), (3.3, 0.01, 0.40, 0.03)]
    pf = pinta_folha(y0, y0 + 0.36)
    for i, (a, af, h, inc) in enumerate(folhas):
        b = (bx + af * math.cos(a), y0, bz + af * math.sin(a))
        ps.append(folha(f"folha_{i}", b, (b[0] + inc * math.cos(a), y0 + h, b[2] + inc * math.sin(a)), 0.03, pf))
    for i, k in enumerate((0, 2, 4, 6)):
        a, af, h, inc = folhas[k]
        c = (bx + (af + inc) * math.cos(a), y0 + h - 0.012, bz + (af + inc) * math.sin(a))
        ps.append(cupula(f"flor_{i}", c, (math.cos(a) * 0.5, 1, math.sin(a) * 0.5), 0.062, 0.03, lambda P, N, c=np.array(c): pinta_flor(P, N, c, 0.062), n=6, ondas=0.22, fase=i))
    return ps


# ---------------------------------------------------------------- o atlas
def cartas(ps: list[Peca]):
    """corta cada peca pela direcao da face (seis cartas) e projeta no plano; devolve as cartas com o tamanho em unidades"""
    out = []
    for p in ps:
        fn = np.cross(p.V[p.F[:, 1]] - p.V[p.F[:, 0]], p.V[p.F[:, 2]] - p.V[p.F[:, 0]])
        eixo = np.abs(fn).argmax(axis=1)
        chave = eixo * 2 + (fn[np.arange(len(fn)), eixo] < 0)
        for k in np.unique(chave):
            faces = p.F[chave == k]
            e = int(k) // 2
            a, b = ((2, 1), (0, 2), (0, 1))[e]
            ids = np.unique(faces)
            uv = p.V[ids][:, (a, b)]
            mn = uv.min(axis=0)
            out.append({"peca": p, "ids": ids, "faces": faces, "uv": uv - mn, "tam": uv.max(axis=0) - mn})
    return out


def empacotar(cs, lado, margem):
    """prateleiras: procura a maior densidade (texels por unidade) em que todas as cartas cabem"""
    def tenta(d):
        x = y = alto = 0
        pos = []
        for c in sorted(cs, key=lambda c: -c["tam"][1]):
            w, h = int(math.ceil(c["tam"][0] * d)) + 2 * margem, int(math.ceil(c["tam"][1] * d)) + 2 * margem
            if x + w > lado:
                x, y, alto = 0, y + alto, 0
            if w > lado or y + h > lado:
                return None
            pos.append((c, x + margem, y + margem)); x += w; alto = max(alto, h)
        return pos
    lo, hi = 10.0, 4000.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if tenta(m) else (lo, m)
    return lo, tenta(lo)


def pintar(pos, d, lado):
    """pinta o atlas triangulo a triangulo, pela posicao e pela normal de cada texel; devolve a imagem e a mascara do que foi pintado"""
    img, feito = np.zeros((lado, lado, 3)), np.zeros((lado, lado), bool)
    for c, ox, oy in pos:
        p = c["peca"]
        mapa = {int(i): n for n, i in enumerate(c["ids"])}
        px = c["uv"] * d + (ox, oy)
        for f in c["faces"]:
            t = px[[mapa[int(i)] for i in f]]
            x0, y0 = np.floor(t.min(axis=0)).astype(int) - 1
            x1, y1 = np.ceil(t.max(axis=0)).astype(int) + 1
            x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, lado - 1), min(y1, lado - 1)
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            (ax, ay), (bx, by), (cx, cy) = t
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-12:
                continue
            w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
            w1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
            w2 = 1 - w0 - w1
            dentro = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
            if not dentro.any():
                continue
            W = np.stack([w0[dentro], w1[dentro], w2[dentro]], axis=1)
            P, N = W @ p.V[f], W @ p.N[f]
            N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
            yy, xx = np.nonzero(dentro)
            img[yy + y0, xx + x0] = p.pinta(P, N)
            feito[yy + y0, xx + x0] = True
    return img, feito


def sangrar(img, feito, passos):
    """estende a borda de cada carta para a margem (a media dos vizinhos ja pintados)"""
    for _ in range(passos):
        soma, n = np.zeros_like(img), np.zeros(feito.shape)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            f = np.roll(feito, (dy, dx), axis=(0, 1))
            soma += np.roll(img, (dy, dx), axis=(0, 1)) * f[..., None]; n += f
        novo = ~feito & (n > 0)
        img[novo] = soma[novo] / n[novo][:, None]
        feito = feito | novo
    return img, feito


def exportar(ps: list[Peca], saida: str, nome: str, fundo, gerador: str) -> dict:
    """pinta o atlas e escreve <nome>.gltf, <nome>.bin e <nome>_cor.png na pasta de saida; devolve as contas (a geladeira feita a mao usa a mesma)"""
    s = Path(saida); s.mkdir(parents=True, exist_ok=True)
    cs = cartas(ps)
    G = LADO * SUPER
    d, pos = empacotar(cs, G, MARGEM * SUPER)
    img, feito = pintar(pos, d, G)
    img, feito = sangrar(img, feito, MARGEM * SUPER)
    img[~feito] = fundo
    im = Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8), "RGB").resize((LADO, LADO), Image.LANCZOS)
    im = im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(s / f"{nome}_cor.png", optimize=True)

    Vs, Ns, Ts, Is, base = [], [], [], [], 0
    for c, ox, oy in pos:
        p = c["peca"]
        mapa = {int(i): n for n, i in enumerate(c["ids"])}
        Vs.append(p.V[c["ids"]]); Ns.append(p.N[c["ids"]]); Ts.append((c["uv"] * d + (ox, oy)) / G)
        Is.append(np.array([[mapa[int(i)] for i in f] for f in c["faces"]]) + base)
        base += len(c["ids"])
    V, N, T, I = (np.vstack(a) for a in (Vs, Ns, Ts, Is))
    V[:, 1] -= V[:, 1].min()   # o chao em y = 0 (os pneus)
    V, N, T, I = V.astype("<f4"), N.astype("<f4"), T.astype("<f4"), I.astype("<u2").reshape(-1)
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
    assert base < 65536, base
    partes = [V.tobytes(), N.tobytes(), T.tobytes(), I.tobytes() + b"\0" * (-len(I) * 2 % 4)]
    vistas, off = [], 0
    for b, alvo in zip(partes, (34962, 34962, 34962, 34963)):
        vistas.append({"buffer": 0, "byteLength": len(b), "byteOffset": off, "target": alvo}); off += len(b)
    vistas[3]["byteLength"] = len(I) * 2
    (s / f"{nome}.bin").write_bytes(b"".join(partes))
    g = {
        "asset": {"generator": gerador, "version": "2.0"},
        "scene": 0, "scenes": [{"name": "Scene", "nodes": [0]}], "nodes": [{"mesh": 0, "name": nome}],
        "materials": [{"name": nome, "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0}}],
        "meshes": [{"name": nome, "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2}, "indices": 3, "material": 0}]}],
        "textures": [{"sampler": 0, "source": 0}], "images": [{"mimeType": "image/png", "name": f"{nome}_cor", "uri": f"{nome}_cor.png"}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(V), "type": "VEC3", "max": [float(v) for v in V.max(axis=0)], "min": [float(v) for v in V.min(axis=0)]},
            {"bufferView": 1, "componentType": 5126, "count": len(V), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(V), "type": "VEC2"},
            {"bufferView": 3, "componentType": 5123, "count": len(I), "type": "SCALAR"}],
        "bufferViews": vistas, "samplers": [{"magFilter": 9729, "minFilter": 9987}],
        "buffers": [{"byteLength": off, "uri": f"{nome}.bin"}],
    }
    (s / f"{nome}.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"triangulos": len(I) // 3, "vertices": len(V), "texels_por_unidade": round(d / SUPER, 1),
                    "caixa": [[round(float(v), 3) for v in V.min(axis=0)], [round(float(v), 3) for v in V.max(axis=0)]],
                    "bytes": {a.name: a.stat().st_size for a in sorted(s.glob(f"{nome}*"))}}


def main(saida: str) -> None:
    print("CARRO", exportar(pecas(), saida, "carro", AZUL, "carro_mao.py (DigiLab)"))


if __name__ == "__main__":
    main(sys.argv[1])
