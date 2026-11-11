"""O cais, feito a mao por script (docs/TAREFA_V3_LUGARES_3D.md, secao 18; pedido do Matheus em 2026-11-10, depois do carro e da
geladeira: "faca a mesma coisa com o cais").

O desenho segue o esboco 1 (../esbocos/esboco_1_pier_barco.png: o pier de tabuas com as estacas amarradas de corda, o musgo e o barquinho
de pesca azul e amarelo com a cabine), mas nada vem da Meshy nem de imagem de terceiros. O pier agora sai da areia para o mar (um L: a
passarela e a ponta mais larga), com o barco atracado ao lado. Os solidos, o atlas e a escrita do glTF sao os do carro
(docs/objetos3d/carro/mao/carro_mao.py). A mesma entrada da sempre o mesmo arquivo.

As medidas estao em celulas da ilha: +z e a terra (o jogo vira o cais para o norte), -z e o mar; y = 0 e a areia, e as estacas descem ate
o fundo do mar (FUNDO, o FUNDO_AGUA de web/app/src/telas/pet/ilha/grade.ts), onde o jogo poe o pe do modelo.

uso (da raiz): python -I docs/objetos3d/cais/mao/cais_mao.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "carro" / "mao"))
from carro_mao import (Peca, cor, cupula, exportar, folha, mancha, normais, por, ruido, tubo,  # noqa: E402
                       AZUL, AZUL_CLARO, AZUL_ESC, CINZA_ESC, FERRUGEM, FERRUGEM_ESC, MIOLO, MUSGO, MUSGO_CLARO, MUSGO_ESC, ROSA, TRACO, VIDRO, VIDRO_ESC)

# ---------------------------------------------------------------- as medidas (celulas). PROPOSTO, SEM FONTE
FUNDO, AGUA = -0.55, -0.22                 # o fundo do mar e o nivel da agua (grade.ts)
DECK, ESP = 0.55, 0.11                     # o alto das tabuas e a espessura delas
PX = 0.90                                  # a meia largura da passarela
Z0, Z1 = 2.05, -2.65                       # a passarela: da areia ate a ponta
ZL, XL = -0.94, -2.50                      # a ponta em L: de onde ela alarga e ate onde vai em x
PASSO, VAO = 0.427, 0.035                  # o passo das tabuas e o vao entre elas
BX, BZ0, BZ1, BOCA = 2.04, 0.00, -2.90, 0.78   # o barco: o x do meio, a popa, a proa e a meia boca

MAD, MAD_CLARA, MAD_ESC, MAD_FUNDA = (178, 124, 80), (212, 160, 108), (136, 90, 58), (92, 60, 42)
MAD2, MAD2_CLARA = (160, 116, 84), (196, 152, 112)       # a tabua mais cinza, gasta
CORDA, CORDA_ESC, CORDA_CLARA = (222, 190, 126), (170, 134, 80), (244, 222, 168)
AMARELO, AMARELO_ESC, AMARELO_CLARO = (250, 200, 70), (214, 152, 44), (255, 228, 130)
LONA, LONA_ESC = (246, 236, 208), (212, 196, 160)
LARANJA, LARANJA_ESC, BRANCO = (244, 112, 60), (200, 76, 40), (248, 246, 238)
FERRO, FERRO_CLARO = (84, 92, 108), (132, 142, 158)

# as estacas: o x, o z, a altura do topo, o raio, o tombo (dx, dz no topo) e se leva corda
ESTACAS = [(1.02, 1.55, 1.18, 0.170, (0.03, 0.02), False), (-1.02, 1.55, 1.30, 0.180, (-0.04, 0.01), True),
           (1.02, 0.02, 1.34, 0.185, (0.02, -0.03), True), (-1.02, -0.20, 1.14, 0.170, (-0.02, 0.03), False),
           (1.02, -2.72, 1.38, 0.190, (0.03, -0.04), True), (-2.62, -2.72, 1.26, 0.185, (-0.04, -0.03), True),
           (-2.62, -0.86, 1.40, 0.180, (-0.03, 0.03), False)]
CAB = (BX, BZ0 - 1.62, 0.40, 0.46, -0.06, 1.02)      # a cabine: o x, o z, as meias larguras em x e em z, o y do pe e o do teto

# o musgo pintado nas tabuas (o centro, o raio, a fase) e os tufos em relevo (o centro, o raio, a altura); as lascas do casco e da cabine
MUSGOS = [((-0.78, DECK, 1.30), 0.26, 0.4), ((0.80, DECK, 0.62), 0.22, 1.3), ((-0.86, DECK, -0.62), 0.20, 2.1), ((-2.36, DECK, -1.62), 0.26, 2.9),
          ((0.70, DECK, -2.28), 0.22, 3.6), ((-1.50, DECK, -2.56), 0.20, 5.0)]
TUFOS = [((-0.80, DECK, 1.32), 0.20, 0.10), ((0.84, DECK, 0.60), 0.17, 0.09), ((-2.38, DECK, -1.64), 0.20, 0.11), ((0.72, DECK, -2.30), 0.15, 0.08),
         ((-0.88, DECK, -0.63), 0.14, 0.07)]
FLORES = [((-0.70, DECK + 0.10, 1.40), ROSA), ((-0.92, DECK + 0.09, 1.20), (248, 246, 238)), ((0.90, DECK + 0.08, 0.68), (250, 200, 70)),
          ((-2.30, DECK + 0.10, -1.56), ROSA), ((-2.48, DECK + 0.09, -1.74), (250, 200, 70))]
LASCAS = [((BX - 0.74, 0.02, BZ0 - 0.80), 0.10, 0.5), ((BX - 0.66, 0.10, BZ0 - 1.96), 0.08, 1.4), ((BX + 0.76, 0.04, BZ0 - 0.52), 0.11, 2.2),
          ((BX + 0.70, 0.08, BZ0 - 1.73), 0.09, 3.1), ((BX - 0.30, 0.20, BZ0 - 2.71), 0.08, 3.9), ((BX + 0.3, 0.0, BZ0), 0.10, 4.6)]
LASCAS_CAB = [((BX - 0.40, 0.22, BZ0 - 1.45), 0.07, 0.8), ((BX + 0.40, 0.30, BZ0 - 1.82), 0.06, 1.9), ((BX + 0.2, 0.2, BZ0 - 1.62 + 0.46), 0.05, 2.5)]


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def bloco(nome, c, t, pinta, R=None, fundo=False) -> Peca:
    """uma caixa de quinas vivas (cada face com os vertices e a normal dela); sem a face de baixo, que ninguem ve"""
    c, t = np.asarray(c, float), np.asarray(t, float) / 2
    R = np.eye(3) if R is None else R
    V, N, F = [], [], []
    for e in range(3):
        for s in (-1, 1):
            if e == 1 and s < 0 and not fundo:
                continue
            a, b = [k for k in range(3) if k != e]
            n = np.zeros(3); n[e] = s
            base = len(V)
            for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                p = np.zeros(3); p[e] = s * t[e]; p[a] = sa * t[a]; p[b] = sb * t[b]
                V.append(c + R @ p); N.append(R @ n)
            F += [(base, base + 1, base + 2), (base, base + 2, base + 3)]
    # cada face olha para onde a normal dela olha: o orientar da Peca vira todas de uma vez, e aqui duas das cinco saiam de costas
    V, N, F = np.array(V, float), np.array(N, float), np.array(F)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    vira = (fn * N[F[:, 0]]).sum(axis=1) < 0
    F[vira] = F[vira][:, ::-1]
    p = Peca(nome, V, F, pinta, N=N, centro=c)
    p.F = F
    return p


# ---------------------------------------------------------------- a pintura (P e N por texel; devolve RGB 0..255)
def veio(P, fase, eixo):
    """os veios da madeira: linhas finas ao longo do eixo comprido da tabua, onduladas"""
    a, b = (P[:, 0], P[:, 2]) if eixo == 0 else (P[:, 2], P[:, 0])
    return np.sin((b + 0.035 * np.sin(a * 3.1 + fase)) * 46 + fase * 5)


def pinta_tabua(i, eixo, a0, a1, gasta, bc=None):
    """a tabua: o tom dela, os veios, as pontas mais escuras, os pregos, o musgo pintado"""
    base, clara = (MAD2, MAD2_CLARA) if gasta else (MAD, MAD_CLARA)

    def f(P, N):
        a, b = P[:, eixo], P[:, 2 if eixo == 0 else 0]
        c = cor(base, len(P))
        cima = N[:, 1] > 0.5
        v = veio(P, i * 1.7, eixo)
        por(c, cima & (ruido(P, 2.3, i * 0.9) > 0.42), clara)
        por(c, cima & (v > 0.88), MAD_ESC)
        por(c, cima & ((a - a0 < 0.06) | (a1 - a < 0.06)), MAD_ESC)
        if bc is not None:
            for ap in (a0 + 0.17, a1 - 0.17):           # os pregos
                por(c, cima & (np.hypot(a - ap, b - bc) < 0.030), FERRO)
        por(c, ~cima, MAD_ESC)
        por(c, N[:, 1] < -0.5, MAD_FUNDA)
        for centro, r, fase in MUSGOS:
            d = mancha(P, centro, r, fase)
            por(c, d < 1, MUSGO); por(c, d < 0.55, MUSGO_CLARO)
            por(c, (d < 1) & ~cima, MUSGO_ESC)
        return c
    return f


def pinta_viga(P, N):
    c = cor(MAD_ESC, len(P))
    por(c, N[:, 1] > 0.5, MAD); por(c, N[:, 1] < -0.5, MAD_FUNDA)
    return c


def pinta_estaca(x0, z0, r, fase):
    def f(P, N):
        y = P[:, 1]
        a = np.arctan2(P[:, 2] - z0, P[:, 0] - x0)
        c = cor(MAD_ESC, len(P))
        casca = np.sin(a * 5 + fase + 0.6 * np.sin(y * 7 + fase))
        por(c, casca > 0.35, MAD)                                                      # as ripas da casca, em pe
        por(c, casca > 0.9, MAD_CLARA)
        por(c, np.abs(np.sin(a * 2.5 + fase * 2 + y * 1.3)) < 0.06, MAD_FUNDA)         # as rachas
        cima = N[:, 1] > 0.6                                                           # o topo cortado: os aneis
        d = np.hypot(P[:, 0] - x0 - 0.02, P[:, 2] - z0 + 0.015) / r
        por(c, cima, MAD_CLARA)
        por(c, cima & (np.abs(np.sin(d * 9.5)) < 0.22), MAD)
        por(c, cima & (d < 0.16), MAD_ESC)
        onda = AGUA + 0.34 + 0.07 * np.sin(a * 3 + fase)                               # a parte molhada: escura e com limo
        por(c, ~cima & (y < onda), MAD_FUNDA)
        por(c, ~cima & (y < onda - 0.10 + 0.05 * np.sin(a * 5 + 2 * fase)), MUSGO_ESC)
        por(c, ~cima & (y < onda - 0.20 + 0.04 * np.sin(a * 4 + fase)) & (y > AGUA - 0.06), MUSGO)
        return c
    return f


def pinta_corda(y0, h, voltas=3):
    def f(P, N):
        t = (P[:, 1] - y0) / h * voltas
        fr = t - np.floor(t)
        c = cor(CORDA, len(P))
        por(c, fr < 0.2, CORDA_ESC); por(c, (fr > 0.5) & (fr < 0.78), CORDA_CLARA)
        por(c, np.abs(N[:, 1]) > 0.7, CORDA_ESC)
        return c
    return f


def pinta_cabo(P, N):
    """o cabo de amarrar: as voltas da corda em diagonal"""
    t = (P[:, 0] + P[:, 1] * 0.6 + P[:, 2]) * 30
    fr = t - np.floor(t)
    c = cor(CORDA, len(P))
    por(c, fr < 0.3, CORDA_ESC); por(c, N[:, 1] > 0.6, CORDA_CLARA)
    return c


def borda_casco(z):
    """o barco em z: (a meia boca, o y da borda, o y da quilha)"""
    t = np.clip((BZ0 - z) / (BZ0 - BZ1), 0, 1)                      # 0 na popa, 1 na proa
    b = BOCA * np.where(t < 0.45, 0.86 + 0.14 * np.sin(t / 0.45 * math.pi / 2), np.maximum(1 - (np.maximum(t - 0.45, 0) / 0.55) ** 2.1, 0) ** 0.62)
    borda = 0.30 + 0.05 * (1 - t) ** 2 + 0.30 * (np.maximum(t - 0.35, 0) / 0.65) ** 1.6
    quilha = -0.50 + 0.26 * (np.maximum(t - 0.55, 0) / 0.45) ** 2 + 0.05 * (1 - t) ** 3
    return np.maximum(b, 0.035), borda, quilha


def pinta_casco(P, N):
    y, z = P[:, 1], P[:, 2]
    b, borda, quilha = borda_casco(z)
    c = cor(AZUL, len(P))
    por(c, N[:, 1] < -0.25, AZUL_ESC)
    por(c, (y > borda - 0.20) & (y < borda - 0.15), AZUL_CLARO)                      # o friso claro
    por(c, y > borda - 0.085, AMARELO)                                                # a faixa amarela da borda
    por(c, (y > borda - 0.10) & (y <= borda - 0.085), TRACO)
    onda = AGUA + 0.10 + 0.02 * np.sin(z * 9)                                         # a linha da agua e o fundo vermelho
    for centro, r, fase in LASCAS:
        d = mancha(P, centro, r, fase)
        por(c, (d < 1) & (y < borda - 0.11), FERRUGEM)
        por(c, (d < 0.5) & (y < borda - 0.11), FERRUGEM_ESC)
    por(c, (N[:, 2] > 0.8) & (y <= borda - 0.10) & (np.abs(np.sin(y * 40)) < 0.12), AZUL_ESC)   # as tabuas do espelho de popa
    por(c, y < onda + 0.035, BRANCO); por(c, y < onda, FERRUGEM_ESC)
    return c


def pinta_dentro(P, N):
    x = P[:, 0] - BX
    c = cor(AZUL_ESC, len(P))
    piso = N[:, 1] > 0.7
    por(c, piso, MAD)
    por(c, piso & (np.abs(np.sin(x * 15.5)) < 0.10), MAD_ESC)                        # as tabuas do piso, no comprido
    por(c, piso & (ruido(P, 3.1, 0.7) > 0.45), MAD_CLARA)
    return c


def pinta_verdugo(P, N):
    c = cor(AMARELO, len(P))
    por(c, N[:, 1] > 0.6, AMARELO_CLARO); por(c, N[:, 1] < -0.3, AMARELO_ESC)
    return c


def pinta_cabine(P, N):
    cx, cz, lx, lz, y0, y1 = CAB
    x, y, z = P[:, 0] - cx, P[:, 1], P[:, 2] - cz
    lado = np.abs(N[:, 0]) > np.abs(N[:, 2])
    u = np.where(lado, z, x)                                # a coordenada ao longo da face
    c = cor(AZUL, len(P))
    por(c, np.abs(np.sin(u * 26)) < 0.07, AZUL_ESC)         # as tabuas da parede, em pe
    for centro, r, fase in LASCAS_CAB:
        por(c, mancha(P, centro, r, fase) < 1, FERRUGEM)
    por(c, y > y1 - 0.07, AZUL_CLARO)
    por(c, y < y0 + 0.14, AZUL_ESC)

    def janela(m, meia, ya, yb):
        d = np.maximum(np.abs(u) - meia, np.maximum(ya - y, y - yb))
        por(c, m & (d < 0.050), LONA); por(c, m & (d < 0.012), TRACO); por(c, m & (d < 0), VIDRO_ESC)
        risco = u + (y - ya) * 0.8
        por(c, m & (d < -0.025) & (risco > 0.02) & (risco < 0.12), VIDRO)
    janela(~lado & (N[:, 2] < 0), 0.24, 0.52, 0.86)         # a da frente (a proa, -z), larga
    janela(lado, 0.22, 0.54, 0.86)                          # as dos lados
    porta = ~lado & (N[:, 2] > 0)                           # a porta, para a popa
    d = np.maximum(np.abs(u) - 0.19, y - 0.86)
    por(c, porta & (d < 0.03), TRACO); por(c, porta & (d < 0), MAD); por(c, porta & (d < 0) & (np.abs(np.sin(u * 30)) < 0.1), MAD_ESC)
    por(c, porta & (np.hypot(u - 0.12, y - 0.42) < 0.03), AMARELO)
    return c


def pinta_lona(P, N):
    c = cor(LONA, len(P))
    por(c, (N[:, 1] >= 0.35) & (np.abs(np.sin((P[:, 0] - BX) * 9.5)) < 0.05), LONA_ESC)      # as costuras
    por(c, N[:, 1] < 0.35, LONA_ESC)
    por(c, N[:, 1] < -0.3, CINZA_ESC)
    return c


def pinta_barril(x0, z0, y0, h):
    def f(P, N):
        y = (P[:, 1] - y0) / h
        a = np.arctan2(P[:, 2] - z0, P[:, 0] - x0)
        c = cor(MAD, len(P))
        por(c, np.sin(a * 6 + 1.0) > 0.8, MAD_CLARA)
        por(c, np.abs(np.sin(a * 6)) < 0.13, MAD_ESC)
        for ya in (0.2, 0.8):
            por(c, np.abs(y - ya) < 0.055, FERRO); por(c, (np.abs(y - ya) < 0.055) & (y > ya + 0.015), FERRO_CLARO)
        cima = N[:, 1] > 0.6
        d = np.hypot(P[:, 0] - x0, P[:, 2] - z0)
        por(c, cima, MAD_CLARA); por(c, cima & (np.abs(np.sin((P[:, 0] - x0) * 22)) < 0.12), MAD); por(c, cima & (d > 0.15), MAD_ESC)
        return c
    return f


def pinta_caixote(c0, t, R):
    def f(P, N):
        q = np.abs((P - np.array(c0)) @ R) / (np.array(t) / 2)      # a posicao no caixote em pe, de 0 (o meio) a 1 (a borda)
        n = np.abs(N @ R)
        c = cor(MAD_CLARA, len(P))
        for e in range(3):
            m = n.argmax(axis=1) == e
            a, b = [k for k in range(3) if k != e]
            por(c, m & (np.abs(np.sin(q[:, b] * 5.2)) < 0.10), MAD)
            por(c, m & (np.abs(q[:, a] - q[:, b]) < 0.10), MAD)                # as ripas em X
            por(c, m & ((q[:, a] > 0.78) | (q[:, b] > 0.78)), MAD)              # a moldura
            por(c, m & (q[:, a] > 0.78) & (q[:, b] > 0.78), MAD_ESC)
        return c
    return f


def pinta_boia(c0, eixo, u, v):
    def f(P, N):
        d = P - np.array(c0)
        a = np.arctan2(d @ v, d @ u)
        c = cor(LARANJA, len(P))
        por(c, N @ eixo < -0.55, LARANJA_ESC)
        por(c, np.sin(a * 2 + 0.6) > 0.55, BRANCO)
        return c
    return f


def pinta_musgo(P, N):
    c = cor(MUSGO, len(P))
    por(c, N[:, 1] > 0.80, MUSGO_CLARO); por(c, N[:, 1] < 0.36, MUSGO_ESC)
    return c


def pinta_folha(y0, y1):
    return lambda P, N: por(por(cor(MUSGO, len(P)), (P[:, 1] - y0) / (y1 - y0) < 0.38, MUSGO_ESC), (P[:, 1] - y0) / (y1 - y0) > 0.72, MUSGO_CLARO)


def pinta_flor(c0, r, petala):
    return lambda P, N: por(cor(petala, len(P)), np.linalg.norm(P - np.array(c0), axis=1) / r < 0.6, MIOLO)


# ---------------------------------------------------------------- as pecas
def tabuas() -> list[Peca]:
    ps, z, i = [], Z0, 0
    while z - PASSO > Z1 - 0.05:
        zc = z - PASSO / 2
        x0, x1 = (XL if zc < ZL else -PX), PX
        # cada tabua com o comprimento, a altura e o giro um pouco diferentes; a 5 e quebrada (mais curta)
        x0, x1 = x0 + 0.05 * math.sin(i * 2.3), x1 + 0.05 * math.sin(i * 3.7 + 1)
        if i == 5:
            x0 = -PX + 0.62
        c = ((x0 + x1) / 2, DECK - ESP / 2 + 0.012 * math.sin(i * 1.9), zc)
        ps.append(bloco(f"tabua_{i}", c, (x1 - x0, ESP, PASSO - VAO), pinta_tabua(i, 0, x0, x1, i % 3 == 1, bc=zc), R=rot_y(math.radians(1.2 * math.sin(i * 4.1)))))
        z -= PASSO; i += 1
    # a rampa: duas tabuas compridas da areia ate a passarela
    zr0, zr1, yr0, yr1 = Z0 - 0.02, Z0 + 0.72, DECK - 0.02, 0.03
    L, ang = math.hypot(zr1 - zr0, yr1 - yr0), math.atan2(yr0 - yr1, zr1 - zr0)
    for k, xc in enumerate((-0.40, 0.42)):
        c = (xc, (yr0 + yr1) / 2 - ESP / 2 * math.cos(ang), (zr0 + zr1) / 2)
        ps.append(bloco(f"rampa_{k}", c, (0.74, ESP, L), pinta_tabua(20 + k, 2, zr0, zr1, k == 1, bc=xc), R=rot_x(ang)))
    return ps


def vigas() -> list[Peca]:
    ps = []
    for k, x in enumerate((-0.68, 0.68)):
        ps.append(bloco(f"viga_z{k}", (x, DECK - ESP - 0.08, (Z0 + Z1) / 2), (0.14, 0.16, Z0 - Z1 - 0.1), pinta_viga))
    for k, z in enumerate((ZL - 0.14, Z1 + 0.14)):
        ps.append(bloco(f"viga_x{k}", ((XL - PX) / 2 - 0.4, DECK - ESP - 0.08, z), (-XL - PX - 0.5, 0.16, 0.14), pinta_viga))
    return ps


def estacas() -> list[Peca]:
    ps = []
    for i, (x, z, topo, r, (dx, dz), corda) in enumerate(ESTACAS):
        caminho = [(x - dx * 0.4, FUNDO, z - dz * 0.4), (x + dx, topo - 0.035, z + dz), (x + dx, topo, z + dz)]
        ps.append(tubo(f"estaca_{i}", caminho, (1, 0, 0), r, r, pinta_estaca(x + dx, z + dz, r, i * 1.3), n=8, escala=[1.08, 1.0, 0.86]))
        if corda:
            y0, h, k = topo - 0.40, 0.19, 0.8
            ps.append(tubo(f"corda_{i}", [(x + dx * k, y0, z + dz * k), (x + dx * k, y0 + h / 2, z + dz * k), (x + dx * k, y0 + h, z + dz * k)], (1, 0, 0), r + 0.045, r + 0.045,
                           pinta_corda(y0, h), n=8, escala=[0.9, 1.0, 0.9]))
    return ps


def barco() -> list[Peca]:
    ps, zs, k = [], np.linspace(BZ0, BZ1, 10), 9

    def anel(z, dentro):
        b, borda, quilha = (float(v) for v in borda_casco(z))
        if dentro:   # as paredes de dentro e o piso
            bi, piso = max(b - 0.07, 0.012), max(-0.05, quilha + 0.10)
            return [(BX + s * w, y, z) for s, w, y in ((-1, bi, borda - 0.01), (-1, max(bi * 0.84, 0.01), piso), (0, 0, piso), (1, max(bi * 0.84, 0.01), piso), (1, bi, borda - 0.01))]
        pts = []
        for j in range(k):   # por fora: da borda de um lado, pela quilha, ate a borda do outro
            a = math.pi * j / (k - 1)
            cx, sy = math.cos(a), math.sin(a)
            pts.append((BX - b * math.copysign(abs(cx) ** 0.62, cx), borda - (borda - quilha) * abs(sy) ** 0.85, z))
        return pts
    for nome, dentro, pinta in (("casco", False, pinta_casco), ("casco_dentro", True, pinta_dentro)):
        aneis = [anel(z, dentro) for z in zs]
        n = len(aneis[0])
        V, F = [p for a in aneis for p in a], []
        for i in range(len(aneis) - 1):
            for j in range(n - 1):
                a, b, c, d = i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j
                F += [(a, b, c), (a, c, d)]
        if not dentro:   # o espelho de popa, em leque
            centro = len(V); V.append((BX, (aneis[0][0][1] + aneis[0][n // 2][1]) / 2, BZ0))
            F += [(centro, j + 1, j) for j in range(n - 1)]
        ps.append(Peca(nome, V, F, pinta, centro=(BX, 6.0 if dentro else 0.4, (BZ0 + BZ1) / 2)))
    if True:   # as faces de dentro olham para cima e para o meio: o orientar acima vira para fora do centro; aqui o centro fica no alto
        d = ps[-1]
        d.F = d.F[:, ::-1].copy(); d.N = normais(d.V, d.F)
    # o verdugo amarelo: uma regua em cima da borda, de cada lado, e a da popa
    for s in (-1, 1):
        caminho = [(BX + s * (float(borda_casco(z)[0]) - 0.03), float(borda_casco(z)[1]) + 0.012, z) for z in zs]
        ps.append(tubo(f"verdugo_{s}", caminho, (0, 1, 0), 0.062, 0.045, pinta_verdugo, n=4, quina=6))
    b0, y0, _ = (float(v) for v in borda_casco(BZ0))
    ps.append(tubo("verdugo_popa", [(BX - b0, y0 + 0.012, BZ0 - 0.02), (BX + b0, y0 + 0.012, BZ0 - 0.02)], (0, 1, 0), 0.062, 0.045, pinta_verdugo, n=4, quina=6))
    # a cabine e o teto de lona; o banco na popa
    cx, cz, lx, lz, y0, y1 = CAB
    ps.append(tubo("cabine", [(cx, y0, cz), (cx, y1, cz)], (0, 0, 1), lx, lz, pinta_cabine, n=8, quina=7))
    ps.append(tubo("lona", [(cx, y1 - 0.01, cz), (cx, y1 + 0.07, cz), (cx, y1 + 0.17, cz)], (0, 0, 1), lx + 0.09, lz + 0.09, pinta_lona, n=8, quina=5, escala=[1.0, 1.0, 0.55]))
    zb = BZ0 - 0.42
    ps.append(bloco("banco", (BX, 0.13, zb), (2 * float(borda_casco(zb)[0]) - 0.12, 0.05, 0.26), pinta_tabua(31, 0, BX - 1, BX + 1, False)))
    return ps


def cabos() -> list[Peca]:
    """os dois cabos: da borda do barco ate a corda de uma estaca, com a barriga"""
    ps = []
    for k, (zb, i) in enumerate(((BZ0 - 0.55, 2), (BZ0 - 2.40, 4))):
        x, z, topo, r, _tombo, _ = ESTACAS[i]
        b, borda, _q = (float(v) for v in borda_casco(zb))
        a, fim = np.array((BX - b + 0.02, borda + 0.05, zb)), np.array((x + r + 0.02, topo - 0.30, z + 0.02))
        caminho = [a + (fim - a) * t + np.array((0, -0.16 * math.sin(math.pi * t), 0)) for t in np.linspace(0, 1, 6)]
        ps.append(tubo(f"cabo_{k}", caminho, (0, 1, 0), 0.028, 0.028, pinta_cabo, n=4))
    return ps


def boia(cb, eixo, R, rr, n=10, m=5) -> Peca:
    """a boia: um anel (toro) de eixo dado; as faces conferidas contra o miolo do anel (o centro do toro e oco)"""
    cb, eixo = np.asarray(cb, float), np.asarray(eixo, float) / np.linalg.norm(eixo)
    u = np.cross(eixo, (0, 1, 0)); u /= np.linalg.norm(u)
    v = np.cross(eixo, u)
    V, F, Nn = [], [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = u * math.cos(a) + v * math.sin(a)
        for j in range(m):
            b = 2 * math.pi * j / m
            nb = d * math.cos(b) + eixo * math.sin(b)
            V.append(cb + d * R + nb * rr); Nn.append(nb)
    for i in range(n):
        for j in range(m):
            a, b, c, d = i * m + j, i * m + (j + 1) % m, ((i + 1) % n) * m + (j + 1) % m, ((i + 1) % n) * m + j
            F += [(a, b, c), (a, c, d)]
    V, F, Nn = np.array(V), np.array(F), np.array(Nn)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    if (fn * Nn[F].mean(axis=1)).sum() < 0:
        F = F[:, ::-1].copy()
    p = Peca("boia", V, F, pinta_boia(cb, eixo, u, v), N=Nn, dois_lados=True)
    p.F = F
    return p


def carga() -> list[Peca]:
    """o barril e o caixote na ponta; a boia encostada na estaca do canto"""
    ps = []
    x0, z0, h, r = -1.95, Z1 + 0.42, 0.52, 0.22
    ps.append(tubo("barril", [(x0, DECK, z0), (x0, DECK + h * 0.33, z0), (x0, DECK + h * 0.67, z0), (x0, DECK + h, z0)], (1, 0, 0), r, r, pinta_barril(x0, z0, DECK, h), n=8,
                   escala=[0.84, 1.0, 1.0, 0.84]))
    c0, t, R = (-1.36, DECK + 0.17, Z1 + 0.36), (0.40, 0.34, 0.40), rot_y(math.radians(14))
    ps.append(bloco("caixote", c0, t, pinta_caixote(c0, t, R), R=R))
    ps.append(boia((-2.38, DECK + 0.29, -1.16), (0.55, 0.50, -0.70), 0.24, 0.075))
    return ps


def verde() -> list[Peca]:
    ps = []
    for i, (c, r, h) in enumerate(TUFOS):
        ps.append(cupula(f"musgo_{i}", (c[0], c[1] - 0.01, c[2]), (0, 1, 0), r, h, pinta_musgo, n=8, ondas=0.16, fase=i * 1.1))
    for i, (c, petala) in enumerate(FLORES):
        ps.append(cupula(f"flor_{i}", c, (0.2 * math.sin(i * 2.0), 1, 0.2 * math.cos(i * 2.0)), 0.055, 0.03, pinta_flor(c, 0.055, petala), n=6, ondas=0.22, fase=i))
    # o capim no pe da rampa, na areia
    for i, (x, z, h, a) in enumerate(((-0.95, 2.55, 0.34, 0.4), (-1.08, 2.40, 0.26, 1.6), (-0.84, 2.66, 0.22, 2.9), (0.98, 2.50, 0.30, 4.0), (1.10, 2.36, 0.22, 5.2), (0.90, 2.64, 0.20, 0.9))):
        ps.append(folha(f"capim_{i}", (x, 0.0, z), (x + 0.10 * math.cos(a), h, z + 0.10 * math.sin(a)), 0.035, pinta_folha(0.0, h)))
    return ps


def pecas() -> list[Peca]:
    return tabuas() + vigas() + estacas() + barco() + cabos() + carga() + verde()


def main(saida: str) -> None:
    print("CAIS", exportar(pecas(), saida, "cais", MAD_ESC, "cais_mao.py (DigiLab)"))


if __name__ == "__main__":
    main(sys.argv[1])
