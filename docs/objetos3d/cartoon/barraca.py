"""A barraca do Tamer em cartoon, feita a mao por script (docs/TAREFA_V3_LUGARES_3D.md, secao 19; pedido do Matheus em 2026-11-10: "faz
tudo em estilo cartoon pra ver como fica"). Troca a barraca da Meshy (a textura pintada, escura): o mesmo desenho do esboco 1
(docs/objetos3d/barraca/esbocos/esboco_1_domo_costuras.png: o domo turquesa de costuras, os remendos, a antena no alto, os estais e o
banquinho com os livros), agora em formas lisas e cores chapadas, como o carro e a geladeira.

Nada vem da Meshy nem de imagem de terceiros: o domo e uma casca de base quadrada arredondada, a porta e pintada (a entrada sem vao, como
antes), e a antena, os estais, as estacas, o banquinho e os livros sao solidos simples. A porta em +z. A mesma entrada da sempre o mesmo
arquivo.

uso (da raiz): python -I docs/objetos3d/cartoon/barraca.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (CINZA, CINZA_ESC, CROMO, MAD, MAD_CLARA, MAD_ESC, Peca, bloco, cor, espelho, exportar, por, revolucao, rot_x, rot_y, tons, triangulos,  # noqa: E402
                   tubo, tufos)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
R, ALTO, QUINA, LADOS = 0.80, 1.02, 2.6, 16
ELEV = (0, 16, 32, 48, 63, 77)                  # as elevacoes dos aneis do domo (graus)
PORTA_X, PORTA_Y = 0.27, 0.62                   # a meia largura e a altura da porta
ESTAIS = [(sx, sz) for sx in (-1, 1) for sz in (-1, 1)]
BANCO = (0.66, 0.70)                            # o x e o z do banquinho

TEAL, TEAL_CLARO, TEAL_ESC = (86, 196, 196), (146, 228, 222), (52, 152, 162)
DENTRO, DENTRO_CHAO = (22, 52, 66), (46, 92, 100)
REMENDO, REMENDO_ESC, LILAS, VERDE = (240, 206, 160), (196, 150, 104), (178, 150, 224), (150, 214, 130)
CORDA, CORDA_ESC = (222, 190, 126), (170, 134, 80)
BRANCO = (246, 246, 240)
LIVROS = ((214, 74, 60), (246, 236, 208), (120, 96, 190))


def casca(a, e):
    """o ponto do domo no angulo a (0 na frente, +z) e na elevacao e (radianos)"""
    c, s = math.cos(a), math.sin(a)
    q = 2 / QUINA
    r = R * math.cos(e)
    return (r * math.copysign(abs(s) ** q, s), ALTO * math.sin(e) ** 0.9, r * math.copysign(abs(c) ** q, c))


def domo() -> Peca:
    V, F, n = [], [], LADOS
    for e in ELEV:
        for j in range(n):
            V.append(casca(2 * math.pi * j / n, math.radians(e)))
    k = len(ELEV)
    for i in range(k - 1):
        for j in range(n):
            a, b, c, d = i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            F += [(a, b, c), (a, c, d)]
    topo = len(V); V.append((0, ALTO, 0))
    F += [((k - 1) * n + j, (k - 1) * n + (j + 1) % n, topo) for j in range(n)]
    return Peca("domo", V, F, pinta_domo, centro=(0, 0.3, 0))


def retalho(u, y, u0, y0, mu, my):
    """a distancia a um remendo retangular no pano desenrolado (negativa dentro)"""
    return np.maximum(np.abs(u - u0) - mu, np.abs(y - y0) - my)


def pinta_domo(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    a = np.arctan2(x, z)
    c = tons(espelho(N), TEAL, TEAL_CLARO, TEAL_ESC, alto=0.80, baixo=0.30)
    # as costuras: as quatro varetas nas quinas e uma faixa na saia, com os pontos claros
    quina = np.abs(np.abs(np.mod(a, math.pi / 2)) - math.pi / 4) * np.hypot(x, z)
    por(c, quina < 0.026, TEAL_ESC)
    por(c, (quina < 0.008) & (np.mod(y * 22, 1) < 0.55), TEAL_CLARO)
    por(c, y < 0.085, TEAL_ESC); por(c, (np.abs(y - 0.085) < 0.008) & (np.mod(a * 14, 1) < 0.55), TEAL_CLARO)
    # os remendos (o angulo e a altura do meio, as meias medidas)
    u = a * 0.62
    for u0, y0, mu, my, cr in ((0.40, 0.74, 0.075, 0.065, REMENDO), (-0.60, 0.30, 0.060, 0.060, LILAS), (-0.53, 0.25, 0.050, 0.050, VERDE),
                               (1.75, 0.50, 0.080, 0.070, REMENDO), (-2.2, 0.62, 0.065, 0.060, LILAS)):
        d = retalho(u, y, u0, y0, mu, my)
        por(c, d < 0, cr)
        por(c, (d < 0) & (d > -0.016) & (np.mod((u + y) * 40, 1) < 0.5), REMENDO_ESC)          # os pontos da costura
    # a porta: o escuro de dentro, o chao e a moldura
    frente = N[:, 2] > 0.25
    dp = (np.abs(x) / PORTA_X) ** 4 + (np.maximum(y - 0.26, 0) / (PORTA_Y - 0.26)) ** 4
    por(c, frente & (dp < 1.42) & (y > 0.02), TEAL_ESC)
    por(c, frente & (dp < 1.42) & (dp > 1.22) & (np.mod(y * 24 + np.abs(x) * 18, 1) < 0.5), TEAL_CLARO)
    por(c, frente & (dp < 1) & (y > 0.02), DENTRO)
    por(c, frente & (dp < 1) & (y > 0.02) & (y < 0.15), DENTRO_CHAO)
    return c


def pinta_rolo(P, N):
    c = tons(N, TEAL_CLARO, (190, 244, 236), TEAL, alto=0.75, baixo=0.20)
    por(c, np.abs(np.abs(P[:, 0]) - 0.17) < 0.022, CORDA); por(c, (np.abs(np.abs(P[:, 0]) - 0.17) < 0.022) & (N @ np.array((0, 0.6, 0.8)) < 0.3), CORDA_ESC)
    return c


def pinta_corda(P, N):
    return tons(N, CORDA, CORDA, CORDA_ESC)


def pinta_madeira(P, N):
    return tons(N, MAD, MAD_CLARA, MAD_ESC)


def pinta_prato(P, N):
    return cor(BRANCO, len(P))   # o prato tem os dois lados com a mesma normal: uma cor so


def pinta_metal(P, N):
    return tons(N, CINZA, CROMO, CINZA_ESC)


def pinta_livro(cl, y0):
    def f(P, N):
        c = tons(N, cl, cl, tuple(int(v * 0.72) for v in cl))
        por(c, (np.abs(N[:, 1]) < 0.5) & (np.abs(P[:, 1] - y0) < 0.009) & (N[:, 0] + N[:, 2] > 0.3), (250, 246, 232))   # as paginas
        return c
    return f


def antena() -> list:
    """o mastro, o prato (uma calota aberta, dos dois lados) virado para cima e para a frente, e o captador"""
    Rm = rot_y(math.radians(35)) @ rot_x(math.radians(52))
    base = np.array((0.0, ALTO + 0.13, 0.0))
    prato = revolucao("prato", [(0.02, 0.0), (0.09, 0.012), (0.155, 0.045), (0.20, 0.095)], pinta_prato, n=10)
    prato = Peca("prato", prato.V @ Rm.T + base, prato.F, pinta_prato, dois_lados=True)
    eixo = Rm @ np.array((0, 1, 0))
    return [tubo("mastro", [(0, ALTO - 0.02, 0), tuple(base)], (0, 0, 1), 0.022, 0.022, pinta_metal, n=5), prato,
            tubo("captador", [tuple(base), tuple(base + eixo * 0.17)], (1, 0, 0), 0.012, 0.012, pinta_metal, n=4),
            bloco("ponta", tuple(base + eixo * 0.18), (0.045, 0.045, 0.045), pinta_metal, R=Rm, fundo=True)]


def pecas():
    ps = [domo(),
          tubo("rolo", [(-0.30, PORTA_Y + 0.085, 0.655), (0, PORTA_Y + 0.095, 0.668), (0.30, PORTA_Y + 0.085, 0.655)], (0, 1, 0), 0.055, 0.055, pinta_rolo, n=7)]
    ps += antena()
    for i, (sx, sz) in enumerate(ESTAIS):
        topo, pe = casca(math.atan2(sx, sz), math.radians(34)), (sx * 0.90, 0.03, sz * 0.88)
        ps.append(tubo(f"estai_{i}", [topo, pe], (0, 1, 0), 0.011, 0.011, pinta_corda, n=4))
        ps.append(bloco(f"estaca_{i}", (pe[0], 0.05, pe[2]), (0.05, 0.13, 0.05), pinta_madeira, R=rot_y(0.6 * i) @ rot_x(0.35 * sz)))
    bx, bz = BANCO
    ps.append(bloco("assento", (bx, 0.215, bz), (0.25, 0.03, 0.22), pinta_madeira, fundo=True))
    for i, (sx, sz) in enumerate(ESTAIS):
        ps.append(bloco(f"perna_{i}", (bx + sx * 0.095, 0.10, bz + sz * 0.08), (0.03, 0.20, 0.03), pinta_madeira))
    for i, cl in enumerate(LIVROS):
        y = 0.23 + 0.018 + i * 0.04
        ps.append(bloco(f"livro_{i}", (bx + 0.01 * i, y, bz - 0.005 * i), (0.19 - 0.015 * i, 0.036, 0.14), pinta_livro(cl, y), R=rot_y(0.25 * i - 0.2), fundo=True))
    return ps + tufos([(-0.78, 0.80, 0.10, 0.07), (0.30, 0.86, 0.08, 0.05), (-0.86, -0.50, 0.09, 0.06), (0.84, -0.30, 0.09, 0.06), (0.20, -0.86, 0.09, 0.06)])


def main(saida: str) -> None:
    ps = pecas()
    print("BARRACA", exportar(ps, saida, "barraca", TEAL, "barraca.py (DigiLab)"), "triangulos", triangulos(ps))


if __name__ == "__main__":
    main(sys.argv[1])
