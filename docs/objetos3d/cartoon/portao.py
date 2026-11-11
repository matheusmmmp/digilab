"""O portao da arena em cartoon, feito a mao por script (docs/TAREFA_V3_LUGARES_3D.md, secao 19; pedido do Matheus em 2026-11-10: "faz
tudo em estilo cartoon pra ver como fica"). Troca o portao da Meshy (a textura pintada, escura): o mesmo desenho do esboco 1
(docs/objetos3d/portao/esbocos/esboco_1_pedra_blocos.png: o arco de blocos de pedra, o portal ciano, as duas flamulas vermelhas e o
musgo), agora em formas lisas e cores chapadas, como o carro e a geladeira.

Nada vem da Meshy nem de imagem de terceiros: os pilares sao caixas, as pedras do arco sao prismas em cunha, o portal e um plano pintado
(a grade e o redemoinho) e as flamulas sao prismas finos. A mascara de luz (portao_luz.png) acende o portal quando o lugar abre. A frente
(as flamulas) em +z. A mesma entrada da sempre o mesmo arquivo.

uso (da raiz): python -I docs/objetos3d/cartoon/portao.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (CINZA, CINZA_ESC, CROMO, MUSGO, MUSGO_CLARO, OURO, PEDRA, PEDRA_CLARA, PEDRA_ESC, PEDRA_FUNDA, Peca, bloco, cor,  # noqa: E402
                   cupula, espelho, exportar, exportar_luz, mancha, pinta_musgo, por, prisma, rot_y, tons, triangulos, tubo, tufos)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
VAO, NASC = 0.42, 1.00                          # a meia largura do vao e a altura onde o arco nasce
R0, R1, PEDRAS = 0.42, 0.82, 7                  # o arco: o raio de dentro, o de fora e quantas pedras
FUNDO_Z = 0.27                                  # a meia espessura do arco
# os blocos de cada pilar, de baixo para cima: a altura, a largura, a profundidade, o desvio em x e o giro
PILAR = [(0.30, 0.54, 0.66, 0.02, 0.00), (0.24, 0.44, 0.56, 0.00, 0.05), (0.22, 0.47, 0.58, 0.01, -0.04), (0.25, 0.44, 0.55, -0.005, 0.03)]
PILAR_X = 0.645
FLAMULA = [(-0.11, 0.92), (0.11, 0.92), (0.11, 0.46), (0.0, 0.35), (-0.11, 0.46)]

PEDRA_QUENTE = (208, 202, 198)
CIANO, CIANO_CLARO, CIANO_ESC, CIANO_BRILHO = (58, 208, 204), (128, 238, 228), (30, 160, 176), (214, 255, 250)
VERM, VERM_ESC = (214, 74, 60), (166, 48, 48)
MUSGOS = [((0.60, 1.05, 0.24), 0.16, 0.4), ((-0.86, 0.32, 0.20), 0.15, 1.3), ((0.84, 0.30, -0.22), 0.16, 2.2), ((-0.44, 1.66, 0.27), 0.13, 3.1),
          ((0.30, 1.78, -0.27), 0.12, 3.9), ((-0.66, 0.98, -0.28), 0.15, 4.6), ((0.90, 0.10, 0.30), 0.14, 5.3), ((-0.50, 0.28, 0.33), 0.12, 0.9)]


def musgo_pintado(c, P):
    for ce, r, fa in MUSGOS:
        d = mancha(P, ce, r, fa)
        por(c, d < 1, MUSGO); por(c, d < 0.6, MUSGO_CLARO)
    return c


def pinta_bloco(c0, t, Rm, base):
    c0, t = np.asarray(c0, float), np.asarray(t, float)
    def f(P, N):
        loc = (P - c0) @ Rm
        d = np.sort(t / 2 - np.abs(loc), axis=1)
        c = tons(espelho(N), base, PEDRA_CLARA, PEDRA_ESC)
        por(c, d[:, 1] < 0.022, PEDRA_ESC); por(c, (d[:, 1] < 0.022) & (N[:, 1] > 0.5), base)      # o chanfro da quina
        por(c, (np.abs(loc[:, 0] - 0.3 * loc[:, 1] - 0.05) < 0.006) & (loc[:, 1] > 0.02) & (np.abs(N[:, 2]) > 0.5), PEDRA_FUNDA)   # uma trinca
        return musgo_pintado(c, P)
    return f


def pinta_cunha(a0, a1, r1, base):
    def f(P, N):
        x, y = P[:, 0], P[:, 1] - NASC
        r, a = np.hypot(x, y), np.arctan2(y, x)
        c = tons(espelho(N), base, PEDRA_CLARA, PEDRA_ESC)
        borda = np.minimum(np.minimum(np.abs(a - a0), np.abs(a - a1)) * r, np.minimum(r - R0, r1 - r))
        face = np.abs(N[:, 2]) > 0.5
        por(c, face & (borda < 0.022), PEDRA_ESC)
        por(c, ~face & (FUNDO_Z + 0.04 - np.abs(P[:, 2]) < 0.022), PEDRA_ESC)
        return musgo_pintado(c, P)
    return f


def portal_luz(P, N):
    """0..1: o quanto cada ponto do portal acende (a grade e o miolo mais fortes)"""
    x, y = P[:, 0], P[:, 1]
    r = np.hypot(x * 1.25, y - 0.92)
    grade = (np.abs(np.mod(x * 7.0 + 0.5, 1) - 0.5) < 0.05) | (np.abs(np.mod(y * 7.0, 1) - 0.5) < 0.05)
    return np.clip(0.55 + 0.45 * grade + 0.35 * (r < 0.30), 0, 1)


def pinta_portal(P, N):
    x, y = P[:, 0], P[:, 1]
    r, a = np.hypot(x * 1.25, y - 0.92), np.arctan2(y - 0.92, x * 1.25)
    c = cor(CIANO, len(P))
    espiral = np.sin(a * 2 + r * 13.0)                                      # o redemoinho em duas voltas
    por(c, espiral > 0.35, CIANO_ESC)
    por(c, r < 0.34, CIANO_CLARO); por(c, (r < 0.34) & (espiral > 0.6), CIANO)
    grade = (np.abs(np.mod(x * 7.0 + 0.5, 1) - 0.5) < 0.035) | (np.abs(np.mod(y * 7.0, 1) - 0.5) < 0.035)
    por(c, grade, CIANO_CLARO)
    por(c, r < 0.12, CIANO_BRILHO)
    for i, (px, py) in enumerate(((-0.22, 0.42), (0.26, 0.70), (-0.12, 1.24), (0.20, 1.12), (0.06, 0.30), (-0.30, 0.86))):
        por(c, np.hypot(x - px, y - py) < 0.022, CIANO_BRILHO)             # as fagulhas
    return c


def pinta_flamula(x0):
    def f(P, N):
        u = P[:, 0] - x0
        c = tons(N, VERM, VERM, VERM_ESC)
        por(c, np.abs(np.abs(u) - 0.065) < 0.016, OURO)
        por(c, (P[:, 1] > 0.88), VERM_ESC)
        return c
    return f


def pinta_metal(P, N):
    return tons(N, CINZA, CROMO, CINZA_ESC)


def portal() -> Peca:
    m = VAO + 0.03
    pts = [(-m, 0.01), (m, 0.01)] + [(m * math.cos(t), NASC + m * math.sin(t)) for t in np.linspace(0, math.pi, 13)]
    V = [(x, y, 0.0) for x, y in pts]
    F = [(0, i, i + 1) for i in range(1, len(V) - 1)]
    return Peca("portal", V, F, pinta_portal, N=np.tile((0.0, 0.0, 1.0), (len(V), 1)), dois_lados=True)


def pecas():
    ps = [portal()]
    for s in (-1, 1):
        y = 0.0
        for i, (h, w, d, dx, g) in enumerate(PILAR):
            c0, Rm = (s * (PILAR_X + dx), y + h / 2, 0.0), rot_y(s * g)
            ps.append(bloco(f"pilar_{s}_{i}", c0, (w, h, d), pinta_bloco(c0, (w, h, d), Rm, PEDRA if (i + (s > 0)) % 2 else PEDRA_QUENTE), R=Rm))
            y += h
        x0 = s * PILAR_X
        ps.append(prisma(f"flamula_{s}", FLAMULA, 0.292, 0.312, pinta_flamula(x0), origem=(x0, 0, 0)))
        ps.append(tubo(f"vara_{s}", [(x0 - 0.15, 0.925, 0.315), (x0 + 0.15, 0.925, 0.315)], (0, 1, 0), 0.02, 0.02, pinta_metal, n=5))
    passo = math.pi / PEDRAS
    for i in range(PEDRAS):
        a0, a1 = i * passo + 0.012, (i + 1) * passo - 0.012
        chave = i == PEDRAS // 2
        r1, z = (R1 + 0.06, FUNDO_Z + 0.04) if chave else (R1 - 0.02 * (i % 2), FUNDO_Z + 0.015 * (i % 2))
        pts = [(R0 * math.cos(a0), NASC + R0 * math.sin(a0)), (r1 * math.cos(a0), NASC + r1 * math.sin(a0)),
               (r1 * math.cos(a1), NASC + r1 * math.sin(a1)), (R0 * math.cos(a1), NASC + R0 * math.sin(a1))]
        ps.append(prisma(f"arco_{i}", pts, -z, z, pinta_cunha(a0, a1, r1, PEDRA_QUENTE if i % 2 else PEDRA)))
    for i, (x, y, z, r, h) in enumerate(((0.62, 1.50, 0.05, 0.13, 0.07), (-0.34, 1.75, -0.04, 0.11, 0.06), (-0.80, 0.30, 0.20, 0.10, 0.06))):
        ps.append(cupula(f"tufo_alto_{i}", (x, y - 0.02, z), (0, 1, 0), r, h, pinta_musgo, n=7, ondas=0.16, fase=i * 1.7))
    return ps + tufos([(-0.92, 0.36, 0.09, 0.06), (0.94, -0.34, 0.09, 0.06), (0.50, 0.38, 0.08, 0.05), (-0.48, -0.38, 0.08, 0.05)])


def main(saida: str) -> None:
    ps = pecas()
    print("PORTAO", exportar(ps, saida, "portao", PEDRA, "portao.py (DigiLab)"), "triangulos", triangulos(ps))
    exportar_luz(ps, {"portal": portal_luz}, saida, "portao")


if __name__ == "__main__":
    main(sys.argv[1])
