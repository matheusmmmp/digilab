"""O enfeite da temporada (MMO7, docs/PLANO_V3_MMO.md secao 7; MMO-12): a taca dourada no pedestal de pedra, para quem ficou entre os 10
primeiros de uma tabela da semana. Nao se vende na loja: o jogo so a poe na ilha, ao lado do cais, quando o servidor diz que a conta a
ganhou. Segue o padrao de 2026-11-10 ("Sim, fica cartoon"): formas lisas e cores chapadas, como o poste e a TV.

O pedestal e um tronco de piramide de pedra com a faixa turquesa (a cor do cais) e a estrela pintada na frente; a taca, o pe e a borda
sao uma superficie de revolucao em ouro; as duas alcas sao tubos em arco; o musgo no pe. Nada vem da Meshy nem de imagem de terceiros. A
mesma entrada da sempre o mesmo arquivo. Um desenho so para todas as temporadas, por enquanto (D-CONTA-157): o desenho de cada temporada
fica com o Matheus.

uso (da raiz): python -I docs/objetos3d/cartoon/trofeu.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (OURO, OURO_CLARO, OURO_ESC, PEDRA, PEDRA_CLARA, PEDRA_ESC, PEDRA_FUNDA, exportar, por, revolucao, tons,  # noqa: E402
                   triangulos, tronco, tubo, tufos)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
P0, P1, PM0, PM1 = 0.0, 0.62, 0.36, 0.28      # o pedestal: de onde ate onde, a meia largura embaixo e em cima
TAMPA = 0.06                                   # a laje do topo do pedestal
# o perfil da taca (o raio, a altura), do pe ate a borda
TACA = [(0.20, P1 + TAMPA), (0.20, P1 + TAMPA + 0.05), (0.12, P1 + TAMPA + 0.09), (0.05, P1 + TAMPA + 0.14), (0.045, P1 + TAMPA + 0.30),
        (0.10, P1 + TAMPA + 0.36), (0.20, P1 + TAMPA + 0.46), (0.25, P1 + TAMPA + 0.62), (0.27, P1 + TAMPA + 0.78), (0.29, P1 + TAMPA + 0.80),
        (0.24, P1 + TAMPA + 0.80), (0, P1 + TAMPA + 0.70)]
ALCA_Y, ALCA_R = P1 + TAMPA + 0.60, 0.14       # a altura do meio das alcas e o raio do arco
# a paleta. PROPOSTO, SEM FONTE
FAIXA, FAIXA_CLARA, FAIXA_ESC = (64, 196, 196), (120, 226, 222), (36, 140, 150)


def pinta_pedestal(P, N):
    y, z = P[:, 1], P[:, 2]
    c = tons(N, PEDRA, PEDRA_CLARA, PEDRA_ESC, alto=0.70, baixo=0.10)
    por(c, y < 0.05, PEDRA_FUNDA)                                                 # o rodape
    faixa = (y > 0.40) & (y < 0.50)
    por(c, faixa, FAIXA); por(c, faixa & (N[:, 1] > 0.3), FAIXA_CLARA); por(c, (y > 0.40) & (y < 0.415), FAIXA_ESC)
    # a estrela de cinco pontas na frente (+z), pintada pelo angulo
    x, yy = P[:, 0], y - 0.24
    r, a = np.hypot(x, yy), np.arctan2(yy, x)
    raio = 0.085 * (0.55 + 0.45 * np.cos(5 * (a - math.pi / 2)) ** 8)
    por(c, (N[:, 2] > 0.6) & (z > 0) & (r < raio), OURO)
    return c


def pinta_tampa(P, N):
    return tons(N, PEDRA_CLARA, (244, 246, 250), PEDRA, alto=0.80, baixo=0.20)


def pinta_ouro(P, N):
    y = P[:, 1]
    c = tons(N, OURO, OURO_CLARO, OURO_ESC, alto=0.62, baixo=0.12)
    por(c, (y > P1 + TAMPA + 0.76) & (N[:, 1] > 0.2), OURO_CLARO)                 # a borda
    por(c, (y > P1 + TAMPA + 0.52) & (y < P1 + TAMPA + 0.56), OURO_ESC)           # o friso da taca
    return c


def alca(lado: int):
    """um arco de meia volta preso na taca, do lado +x (lado 1) ou -x (lado -1)"""
    pts = []
    for i in range(9):
        a = -math.pi / 2 + math.pi * i / 8
        pts.append((lado * (0.22 + ALCA_R * math.cos(a)), ALCA_Y + ALCA_R * math.sin(a), 0.0))
    return tubo(f"alca_{'d' if lado > 0 else 'e'}", pts, (0, 0, 1), 0.03, 0.03, pinta_ouro, n=6)


def pecas():
    ps = [tronco("pedestal", (0, 0), P0, PM0, P1, PM1, pinta_pedestal, tampas=(False, True)),
          tronco("tampa", (0, 0), P1, PM1 + 0.04, P1 + TAMPA, PM1 + 0.04, pinta_tampa, tampas=(True, True)),
          revolucao("taca", TACA, pinta_ouro, n=14), alca(1), alca(-1)]
    return ps + tufos([(0.34, 0.20, 0.10, 0.07), (-0.33, -0.22, 0.09, 0.06), (-0.22, 0.34, 0.10, 0.06), (0.25, -0.33, 0.09, 0.07)])


def main(saida: str) -> None:
    ps = pecas()
    print("TROFEU", exportar(ps, saida, "trofeu", PEDRA, "trofeu.py (DigiLab)"), "triangulos", triangulos(ps))


if __name__ == "__main__":
    main(sys.argv[1])
