"""O poste em cartoon, feito a mao por script (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 18; pedido do Matheus em 2026-11-10: "faz tudo em
estilo cartoon pra ver como fica"). Troca o poste em blocos (secao 14): o mesmo lampiao de ferro verde com a hera, agora em formas lisas e
cores chapadas, como o carro e a geladeira.

O pe, a coluna e o colar sao uma superficie de revolucao; a lanterna e um tronco de piramide com os vidros pintados, o chapeu outro, e a
hera e uma faixa pintada em espiral na coluna, com tufos de musgo no pe. A mascara de luz (poste_luz.png) acende os vidros a noite.
Nada vem da Meshy nem de imagem de terceiros. A mesma entrada da sempre o mesmo arquivo.

uso (da raiz): python -I docs/objetos3d/cartoon/poste.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (FAROL, FAROL_ESC, BRILHO, MUSGO, MUSGO_CLARO, MUSGO_ESC, OURO, OURO_ESC, cor, exportar, exportar_luz, por, revolucao, tons,  # noqa: E402
                   triangulos, tronco, tufos)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
ALTO = 2.20
# o perfil do pe, da coluna e do colar (o raio, a altura)
PERFIL = [(0.20, 0.0), (0.20, 0.09), (0.155, 0.13), (0.155, 0.21), (0.095, 0.30), (0.072, 0.36), (0.064, 1.30), (0.092, 1.33), (0.092, 1.39),
          (0.05, 1.43), (0.125, 1.48), (0.125, 1.515), (0, 1.515)]
L0, L1, M0, M1 = 1.515, 1.905, 0.105, 0.165          # a lanterna: de onde ate onde, a meia largura embaixo e em cima
C0, C1, CM0, CM1 = 1.905, 2.075, 0.215, 0.05          # o chapeu
VERDE, VERDE_CLARO, VERDE_ESC = (62, 138, 118), (104, 184, 156), (40, 98, 92)


def pinta_coluna(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    c = tons(N, VERDE, VERDE_CLARO, VERDE_ESC, alto=0.70, baixo=0.05)
    por(c, (y > 0.085) & (y < 0.135), VERDE_ESC)                                   # o friso do pe
    por(c, (y > 1.325) & (y < 1.395), OURO); por(c, (y > 1.325) & (y < 1.345), OURO_ESC)   # o colar dourado
    por(c, (y > 1.47) & (N[:, 1] < 0.5), VERDE_ESC)                               # o prato da lanterna
    # a hera: uma faixa em espiral na coluna, com folhas claras
    a = np.arctan2(x, z)
    volta = np.mod(a / (2 * math.pi) - (y - 0.30) * 1.9, 1.0)
    hera = (y > 0.24) & (y < 1.16) & (np.abs(volta - 0.5) < 0.17 * np.clip((1.20 - y) / 0.5, 0.25, 1))
    por(c, hera, MUSGO)
    por(c, hera & (np.sin(y * 46 + a * 3) > 0.45), MUSGO_CLARO); por(c, hera & (np.sin(y * 46 + a * 3) < -0.6), MUSGO_ESC)
    return c


def vidro(P, N):
    """0..1: o vidro de cada face da lanterna (o que acende), dentro da moldura"""
    y = P[:, 1]
    t = (y - L0) / (L1 - L0)
    m = M0 + (M1 - M0) * t                                         # a meia largura da face nesta altura
    lado = np.where(np.abs(N[:, 0]) > np.abs(N[:, 2]), P[:, 2], P[:, 0])   # a coordenada ao longo da face
    return ((np.abs(lado) < m - 0.030) & (np.abs(lado) > 0.011) & (t > 0.10) & (t < 0.90)).astype(float)


def pinta_lanterna(P, N):
    y = P[:, 1]
    t = (y - L0) / (L1 - L0)
    c = tons(N, VERDE, VERDE_CLARO, VERDE_ESC, alto=0.9, baixo=0.3)        # a moldura e a travessa do meio
    v = vidro(P, N) > 0.5
    por(c, v, FAROL)
    por(c, v & (t < 0.34), FAROL_ESC)
    lado = np.where(np.abs(N[:, 0]) > np.abs(N[:, 2]), P[:, 2], P[:, 0])
    por(c, v & (t > 0.58) & (t < 0.80) & (lado > 0.03) & (lado < 0.075), BRILHO)   # o brilho do vidro
    return c


def pinta_chapeu(P, N):
    y = P[:, 1]
    c = tons(N, VERDE, VERDE_CLARO, VERDE_ESC, alto=0.80, baixo=0.20)
    por(c, y < C0 + 0.028, OURO); por(c, N[:, 1] < -0.5, VERDE_ESC)
    return c


def pinta_pinha(P, N):
    return tons(N, OURO, (255, 228, 130), OURO_ESC, alto=0.75, baixo=0.15)


def pecas():
    ps = [revolucao("coluna", PERFIL, pinta_coluna, n=8),
          tronco("lanterna", (0, 0), L0, M0, L1, M1, pinta_lanterna, tampas=(False, False)),
          tronco("chapeu", (0, 0), C0, CM0, C1, CM1, pinta_chapeu, tampas=(True, True)),
          revolucao("pinha", [(0.035, C1), (0.058, C1 + 0.05), (0.04, C1 + 0.10), (0, ALTO)], pinta_pinha, n=6)]
    return ps + tufos([(0.19, 0.10, 0.10, 0.07), (-0.19, -0.10, 0.10, 0.06), (-0.10, 0.19, 0.10, 0.06), (0.10, -0.19, 0.10, 0.07)])


def main(saida: str) -> None:
    ps = pecas()
    print("POSTE", exportar(ps, saida, "poste", (62, 138, 118), "poste.py (DigiLab)"), "triangulos", triangulos(ps))
    exportar_luz(ps, {"lanterna": vidro}, saida, "poste")


if __name__ == "__main__":
    main(sys.argv[1])
