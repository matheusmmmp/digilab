"""O que os objetos em cartoon feitos a mao por script tem em comum (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 18; pedido do Matheus em
2026-11-10: "faz tudo em estilo cartoon pra ver como fica"): os solidos, o atlas e a escrita do glTF sao os do carro
(docs/objetos3d/carro/mao/carro_mao.py) e a caixa de quinas vivas e a do cais (docs/objetos3d/cais/mao/cais_mao.py). Aqui fica o que
faltava: a superficie de revolucao, o prisma (um poligono levado por um eixo), o tronco de piramide, os tons pela normal e a mascara de
luz (o emissiveMap que fica ao lado do glTF, com os mesmos UVs).
"""
import math, sys
from pathlib import Path
import numpy as np
from PIL import Image

_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_D / "carro" / "mao")); sys.path.insert(0, str(_D / "cais" / "mao"))
import carro_mao as C  # noqa: E402
from carro_mao import Peca, caixa, cor, cupula, exportar, folha, mancha, por, ruido, tubo  # noqa: E402,F401
from carro_mao import CINZA, CINZA_ESC, CROMO, MUSGO, MUSGO_CLARO, MUSGO_ESC, ROSA, MIOLO, FAROL, FAROL_ESC, BRILHO  # noqa: E402,F401
from cais_mao import bloco, rot_x, rot_y  # noqa: E402,F401

# a paleta comum das pecas novas. PROPOSTO, SEM FONTE
MAD, MAD_CLARA, MAD_ESC = (178, 124, 80), (212, 160, 108), (136, 90, 58)
PEDRA, PEDRA_CLARA, PEDRA_ESC, PEDRA_FUNDA = (198, 200, 210), (230, 232, 238), (156, 160, 178), (118, 122, 146)
FERRO, FERRO_CLARO = (84, 92, 108), (132, 142, 158)
OURO, OURO_ESC, OURO_CLARO = (250, 200, 70), (214, 152, 44), (255, 228, 130)
LUZ_DIR = np.array((0.35, 0.85, 0.40)) / np.linalg.norm((0.35, 0.85, 0.40))


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def tons(N, base, clara, esc, alto=0.62, baixo=0.12):
    """a cor chapada em tres tons pela normal (a luz de cima, um pouco da frente e da direita)"""
    l = N @ LUZ_DIR
    return por(por(cor(base, len(N)), l > alto, clara), l < baixo, esc)


def espelho(N):
    """a normal com a frente e o fundo iguais (|z|): o objeto visto de tras recebe os mesmos tons que visto da frente"""
    return np.column_stack([N[:, 0], N[:, 1], np.abs(N[:, 2])])


def pinta_tons(base, clara, esc):
    return lambda P, N: tons(N, base, clara, esc)


def pinta_musgo(P, N):
    c = cor(MUSGO, len(P))
    por(c, N[:, 1] > 0.80, MUSGO_CLARO); por(c, N[:, 1] < 0.36, MUSGO_ESC)
    return c


def pinta_folha(y0, y1):
    return lambda P, N: por(por(cor(MUSGO, len(P)), (P[:, 1] - y0) / (y1 - y0) < 0.38, MUSGO_ESC), (P[:, 1] - y0) / (y1 - y0) > 0.72, MUSGO_CLARO)


def revolucao(nome, perfil, pinta, n=8, c=(0.0, 0.0), fase=0.0, fundo=False) -> Peca:
    """o perfil (o raio, a altura), de baixo para cima, girado em volta do eixo y que passa por c (x, z); o ultimo ponto fecha em leque se o
    raio dele for 0"""
    V, F = [], []
    fecha = perfil[-1][0] == 0
    aneis = perfil[:-1] if fecha else perfil
    for r, y in aneis:
        for j in range(n):
            a = 2 * math.pi * j / n + fase
            V.append((c[0] + r * math.sin(a), y, c[1] + r * math.cos(a)))
    k = len(aneis)
    for i in range(k - 1):
        for j in range(n):
            a, b, cc, d = i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            F += [(a, b, cc), (a, cc, d)]
    if fecha:
        topo = len(V); V.append((c[0], perfil[-1][1], c[1]))
        F += [((k - 1) * n + j, (k - 1) * n + (j + 1) % n, topo) for j in range(n)]
    if fundo:
        b = len(V); V.append((c[0], perfil[0][1], c[1]))
        F += [(b, (j + 1) % n, j) for j in range(n)]
    ys = [y for _, y in perfil]
    return Peca(nome, V, F, pinta, centro=(c[0], (min(ys) + max(ys)) / 2, c[1]))


def _faces_pela_normal(nome, V, N, F, pinta) -> Peca:
    """a peca de quinas vivas: cada face olha para onde a normal dela olha (o orientar da Peca vira tudo de uma vez so)"""
    V, N, F = np.array(V, float), np.array(N, float), np.array(F)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    vira = (fn * N[F[:, 0]]).sum(axis=1) < 0
    F[vira] = F[vira][:, ::-1]
    p = Peca(nome, V, F, pinta, N=N, centro=V.mean(axis=0))
    p.F = F
    return p


def prisma(nome, pts, a0, a1, pinta, eixo=2, suave=False, tampas=(True, True), R=None, origem=(0, 0, 0)) -> Peca:
    """um poligono convexo levado de a0 a a1 pelo eixo: eixo 2, os pontos sao (x, y) e o prisma vai em z; eixo 0, sao (z, y) e ele vai em x;
    eixo 1, sao (x, z) e ele sobe em y. Quinas vivas (cada face com os vertices dela), ou as laterais suaves. R e origem giram e levam a peca"""
    pts = [np.asarray(p, float) for p in pts]
    m = len(pts)
    cen = np.mean(pts, axis=0)

    def p3(p, a):
        return {2: (p[0], p[1], a), 0: (a, p[1], p[0]), 1: (p[0], a, p[1])}[eixo]

    def n3(nn):
        return {2: (nn[0], nn[1], 0), 0: (0, nn[1], nn[0]), 1: (nn[0], 0, nn[1])}[eixo]
    ns = []
    for i in range(m):
        e = pts[(i + 1) % m] - pts[i]
        nn = np.array((e[1], -e[0])); nn /= max(np.linalg.norm(nn), 1e-12)
        if nn @ ((pts[i] + pts[(i + 1) % m]) / 2 - cen) < 0:
            nn = -nn
        ns.append(nn)
    V, N, F = [], [], []
    for i in range(m):
        j = (i + 1) % m
        ni = ns[i] + ns[i - 1] if suave else ns[i]
        nj = ns[i] + ns[j] if suave else ns[i]
        ni, nj = ni / np.linalg.norm(ni), nj / np.linalg.norm(nj)
        b = len(V)
        V += [p3(pts[i], a0), p3(pts[j], a0), p3(pts[j], a1), p3(pts[i], a1)]
        N += [n3(ni), n3(nj), n3(nj), n3(ni)]
        F += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    for a, s, tem in ((a0, -1 if a0 < a1 else 1, tampas[0]), (a1, 1 if a0 < a1 else -1, tampas[1])):
        if not tem:
            continue
        b = len(V)
        V += [p3(p, a) for p in pts]
        N += [{2: (0, 0, s), 0: (s, 0, 0), 1: (0, s, 0)}[eixo]] * m
        F += [(b, b + i, b + i + 1) for i in range(1, m - 1)]
    V, N = np.array(V, float), np.array(N, float)
    if R is not None:
        V, N = V @ np.asarray(R).T, N @ np.asarray(R).T
    return _faces_pela_normal(nome, V + np.asarray(origem, float), N, F, pinta)


def tronco(nome, c, y0, m0, y1, m1, pinta, tampas=(False, True)) -> Peca:
    """um tronco de piramide de base quadrada, de quinas vivas: as meias larguras m0 em y0 e m1 em y1, em volta de c (x, z)"""
    V, N, F = [], [], []
    qs = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    for i in range(4):
        (ax, az), (bx, bz) = qs[i], qs[(i + 1) % 4]
        b = len(V)
        V += [(c[0] + ax * m0, y0, c[1] + az * m0), (c[0] + bx * m0, y0, c[1] + bz * m0), (c[0] + bx * m1, y1, c[1] + bz * m1), (c[0] + ax * m1, y1, c[1] + az * m1)]
        nn = np.array(((ax + bx) / 2, 0, (az + bz) / 2), float) * (y1 - y0) + np.array((0, m0 - m1, 0))
        N += [nn / np.linalg.norm(nn)] * 4
        F += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    for y, mm, s, tem in ((y0, m0, -1, tampas[0]), (y1, m1, 1, tampas[1])):
        if not tem:
            continue
        b = len(V)
        V += [(c[0] + ax * mm, y, c[1] + az * mm) for ax, az in qs]
        N += [(0, s, 0)] * 4
        F += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    return _faces_pela_normal(nome, V, N, F, pinta)


def tufos(lista, ys=0.0) -> list:
    """os tufos de musgo (o x, o z, o raio e a altura de cada um) com duas folhas de capim em volta"""
    out = []
    for i, (x, z, r, h) in enumerate(lista):
        out.append(cupula(f"musgo_{i}", (x, ys - 0.01, z), (0, 1, 0), r, h, pinta_musgo, n=7, ondas=0.16, fase=i * 1.3))
        for k in range(2):
            a = i * 2.3 + k * 2.6
            bx, bz, hh = x + 0.8 * r * math.cos(a), z + 0.8 * r * math.sin(a), h * (2.2 + 0.6 * k)
            out.append(folha(f"capim_{i}_{k}", (bx, ys, bz), (bx + 0.5 * r * math.cos(a + 1), ys + hh, bz + 0.5 * r * math.sin(a + 1)), 0.28 * r,
                             pinta_folha(ys, ys + hh)))
    return out


def triangulos(ps) -> int:
    return int(sum(len(p.F) for p in ps))


def exportar_luz(ps, luz: dict, saida: str, nome: str, lado: int = 512) -> None:
    """a mascara de luz (<nome>_luz.png), com os mesmos UVs do atlas: branca onde a peca acende. luz: o nome da peca -> a funcao (P, N) que
    devolve 0..1 por texel (ou None, a peca toda); as outras pecas ficam pretas. O empacotamento e o do exportar (a mesma malha)"""
    guardadas = [p.pinta for p in ps]
    try:
        for p in ps:
            if p.nome in luz:
                f = luz[p.nome]
                p.pinta = (lambda P, N, f=f: np.repeat((np.ones(len(P)) if f is None else np.asarray(f(P, N), float))[:, None] * 255.0, 3, axis=1))
            else:
                p.pinta = lambda P, N: np.zeros((len(P), 3))
        G = C.LADO * C.SUPER
        d, pos = C.empacotar(C.cartas(ps), G, C.MARGEM * C.SUPER)
        img, feito = C.pintar(pos, d, G)
        img[~feito] = 0
        im = Image.fromarray(np.clip(img[..., 0] + 0.5, 0, 255).astype(np.uint8), "L").resize((lado, lado), Image.LANCZOS)
        im.save(Path(saida) / f"{nome}_luz.png", optimize=True)
    finally:
        for p, f in zip(ps, guardadas):
            p.pinta = f
