"""O trilho com o vagao em cartoon, feito a mao por script (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 18; pedido do Matheus em 2026-11-10:
"faz tudo em estilo cartoon pra ver como fica"). Troca o vagao da Meshy (a textura pintada, escura): o mesmo desenho do esboco 1
(docs/objetos3d/trem/esbocos/esboco_1_vagao_madeira.png: o vagao vermelho de tabuas, as tres escotilhas douradas, o teto de lona, um
trecho de trilho), agora em formas lisas e cores chapadas, como o carro e a geladeira.

Nada vem da Meshy nem de imagem de terceiros: as pecas sao caixas, cilindros e um prisma (o teto), e a pintura e uma funcao da posicao no
espaco. O trilho corre em x; o lado das escotilhas em +z e em -z. A mesma entrada da sempre o mesmo arquivo.

uso (da raiz): python -I docs/objetos3d/cartoon/trilho.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (BRILHO, CROMO, FERRO, FERRO_CLARO, MAD, MAD_CLARA, MAD_ESC, MUSGO, MUSGO_ESC, OURO, OURO_CLARO, OURO_ESC, bloco, cor, exportar,  # noqa: E402
                   mancha, por, prisma, tons, triangulos, tubo, tufos)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
COMP, BITOLA = 1.88, 0.30                       # o comprimento do trecho e o z de cada trilho
DORM = (-0.76, -0.38, 0.0, 0.38, 0.76)          # o x dos dormentes
RODA_R, RODA_X, RODA_Y = 0.19, 0.42, 0.32
CH_Y, CH_H = 0.50, 0.09                         # o chassi: o meio e a altura
CX, CZ, C0, C1 = 0.73, 0.37, 0.545, 1.245       # a caixa: as meias medidas em x e em z, o pe e o alto
ESC_X, ESC_Y, ESC_R = (-0.44, 0.0, 0.44), 0.94, 0.165   # as escotilhas
TETO_Z, TETO_H, TETO_X = 0.44, 0.21, 0.80

VERM, VERM_CLARO, VERM_ESC, VERM_GASTO = (214, 74, 60), (238, 112, 88), (166, 48, 48), (240, 150, 120)
LONA, LONA_ESC, LONA_CLARA = (246, 236, 208), (212, 196, 160), (255, 250, 232)
VIDRO, VIDRO_CLARO, ESCURO = (96, 124, 156), (150, 180, 206), (40, 44, 58)
MOLDURA, MOLDURA_ESC = (150, 152, 164), (110, 112, 128)


def pinta_dormente(P, N):
    c = tons(N, MAD_ESC, MAD, (104, 68, 46))
    por(c, (N[:, 1] > 0.5) & (np.sin(P[:, 2] * 34 + P[:, 0] * 9) > 0.86), (104, 68, 46))     # os veios
    return c


def pinta_trilho(P, N):
    c = tons(N, FERRO, FERRO_CLARO, (60, 66, 82))
    por(c, N[:, 1] > 0.5, CROMO)
    return c


def pinta_roda(x0, z0):
    def f(P, N):
        r, a = np.hypot(P[:, 0] - x0, P[:, 1] - RODA_Y), np.arctan2(P[:, 1] - RODA_Y, P[:, 0] - x0)
        c = cor(ESCURO, len(P))
        raio = np.abs(np.mod(a + math.pi / 6, math.pi / 3) - math.pi / 6) * r < 0.020      # seis raios
        por(c, raio & (r < 0.15), FERRO_CLARO)
        por(c, r > 0.142, FERRO); por(c, (r > 0.142) & (r < 0.158), FERRO_CLARO)
        por(c, r < 0.058, OURO_ESC); por(c, r < 0.034, OURO)
        por(c, np.abs(N[:, 2]) < 0.5, FERRO)                                                 # a banda
        return c
    return f


def pinta_chassi(P, N):
    return tons(N, FERRO, FERRO_CLARO, (60, 66, 82))


def pinta_caixa(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    c = tons(N, VERM, VERM, VERM_ESC, baixo=0.20)
    lado_z = np.abs(N[:, 2]) > 0.5
    ao_longo = np.where(lado_z, x, z)
    meia = np.where(lado_z, CX, CZ)
    t = (y - C0) / 0.14                                                   # as tabuas deitadas
    por(c, (np.mod(t, 1) > 0.60) & (np.sin(np.floor(t) * 2.4 + ao_longo * 3.1) > 0.2) & (N[:, 1] < 0.5), VERM_CLARO)
    for ce, r, fa in (((-0.50, 0.70, CZ), 0.11, 0.4), ((0.30, 1.12, CZ), 0.09, 1.7), ((0.56, 0.74, -CZ), 0.12, 2.6), ((-0.20, 1.10, -CZ), 0.09, 3.4),
                      ((CX, 0.86, 0.10), 0.10, 4.3), ((-CX, 0.98, -0.08), 0.10, 5.1)):
        por(c, mancha(P, ce, r, fa) < 1, VERM_GASTO)                      # a tinta gasta
    por(c, (np.mod(t, 1) < 0.10) & (N[:, 1] < 0.5), VERM_ESC)              # o vao entre as tabuas
    por(c, (meia - np.abs(ao_longo) < 0.07) & (N[:, 1] < 0.5), MOLDURA)    # as cantoneiras
    por(c, (meia - np.abs(ao_longo) < 0.012) & (N[:, 1] < 0.5), MOLDURA_ESC)
    por(c, (y < C0 + 0.07) & (N[:, 1] < 0.5), MOLDURA); por(c, (y < C0 + 0.012) & (N[:, 1] < 0.5), MOLDURA_ESC)   # a soleira
    por(c, (y > C1 - 0.05) & (N[:, 1] < 0.5), MOLDURA_ESC)
    for ce, r, fa in (((CX - 0.04, C0 + 0.03, CZ), 0.14, 0.9), ((-CX + 0.10, C0 + 0.02, -CZ), 0.13, 2.2), ((-CX, C0 + 0.05, CZ - 0.1), 0.10, 3.9)):
        d = mancha(P, ce, r, fa)
        por(c, d < 1, MUSGO); por(c, d < 0.55, MUSGO_ESC)                  # o musgo no pe
    # a janelinha de cada ponta
    ponta = np.abs(N[:, 0]) > 0.5
    dj = np.maximum(np.abs(z) - 0.15, np.abs(y - 0.98) - 0.13)
    por(c, ponta & (dj < 0.035), OURO); por(c, ponta & (dj < 0), VIDRO); por(c, ponta & (dj < 0) & (z + (y - 0.98) > 0.10), VIDRO_CLARO)
    return c


def pinta_escotilha(x0, lado):
    def f(P, N):
        r = np.hypot(P[:, 0] - x0, P[:, 1] - ESC_Y)
        c = cor(OURO, len(P))
        por(c, r > 0.148, OURO_ESC); por(c, (r > 0.118) & (r < 0.132), OURO_CLARO)
        por(c, r < 0.110, VIDRO)
        por(c, (r < 0.110) & ((P[:, 0] - x0) * lado * -1 + (P[:, 1] - ESC_Y) > 0.045), VIDRO_CLARO)   # o reflexo
        por(c, (r < 0.110) & (np.hypot(P[:, 0] - x0 + 0.045 * lado, P[:, 1] - ESC_Y - 0.05) < 0.022), BRILHO)
        por(c, np.abs(N[:, 2]) < 0.5, OURO_ESC)
        return c
    return f


def pinta_teto(P, N):
    x = P[:, 0]
    c = tons(N, LONA, LONA_CLARA, LONA_ESC, alto=0.80, baixo=0.25)
    por(c, (np.abs(np.abs(x) - 0.27) < 0.012) & (N[:, 1] > 0), LONA_ESC)     # as costuras
    por(c, N[:, 1] < -0.3, LONA_ESC)
    por(c, np.abs(N[:, 0]) > 0.5, LONA_ESC)
    return c


def pecas():
    ps = []
    for i, x in enumerate(DORM):
        ps.append(bloco(f"dormente_{i}", (x, 0.035, 0), (0.17, 0.07, 0.96), pinta_dormente))
    for s in (-1, 1):
        ps.append(bloco(f"trilho_{s}", (0, 0.10, s * BITOLA), (COMP, 0.06, 0.07), pinta_trilho))
    for i, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        x, z = sx * RODA_X, sz * BITOLA
        ps.append(tubo(f"roda_{i}", [(x, RODA_Y, z - 0.035), (x, RODA_Y, z + 0.035)], (0, 1, 0), RODA_R, RODA_R, pinta_roda(x, z), n=12))
    for sx in (-1, 1):
        ps.append(tubo(f"eixo_{sx}", [(sx * RODA_X, RODA_Y, -BITOLA), (sx * RODA_X, RODA_Y, BITOLA)], (0, 1, 0), 0.035, 0.035, pinta_chassi, n=5))
        ps.append(bloco(f"engate_{sx}", (sx * 0.83, CH_Y, 0), (0.12, 0.07, 0.16), pinta_chassi, fundo=True))
    ps.append(bloco("chassi", (0, CH_Y, 0), (1.56, CH_H, 0.66), pinta_chassi, fundo=True))
    ps.append(bloco("caixa", (0, (C0 + C1) / 2, 0), (2 * CX, C1 - C0, 2 * CZ), pinta_caixa))
    for s in (-1, 1):
        for x in ESC_X:
            ps.append(tubo(f"escotilha_{s}_{x}", [(x, ESC_Y, s * (CZ - 0.01)), (x, ESC_Y, s * (CZ + 0.035))], (0, 1, 0), ESC_R, ESC_R, pinta_escotilha(x, s), n=12))
    arco = [(TETO_Z * math.cos(t), C1 + TETO_H * math.sin(t)) for t in np.linspace(0, math.pi, 9)]
    ps.append(prisma("teto", arco + [(-TETO_Z, C1 - 0.035), (TETO_Z, C1 - 0.035)], -TETO_X, TETO_X, pinta_teto, eixo=0, suave=True))
    return ps + tufos([(-0.57, 0.40, 0.09, 0.06), (0.19, -0.40, 0.09, 0.06), (0.60, 0.38, 0.08, 0.05), (-0.20, -0.38, 0.08, 0.05), (0.84, -0.10, 0.07, 0.05)])


def main(saida: str) -> None:
    ps = pecas()
    print("TRILHO", exportar(ps, saida, "trilho", VERM, "trilho.py (DigiLab)"), "triangulos", triangulos(ps))


if __name__ == "__main__":
    main(sys.argv[1])
