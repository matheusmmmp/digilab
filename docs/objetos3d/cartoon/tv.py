"""A TV de tubo em cartoon, feita a mao por script (pedido do Matheus em 2026-11-11: "TV por script cartoon"; o padrao e o de 2026-11-10,
"Sim, fica cartoon": formas lisas e cores chapadas, como o carro, a geladeira e o poste).

O gabinete e uma superelipse levada de tras para a frente (o fundo estreita, como o tubo); a moldura e a tela sao pecas separadas na
frente, para a tela poder mostrar alguma coisa depois (a funcao vidro ja marca o que acenderia; a mascara de luz fica para a TV-3); dois botoes, o alto-falante pintado, quatro
pes, a antena em V e o musgo no pe. A forma segue a televisionVintage do Kenney Furniture Kit (CC0, Assets/kits3d/kenney_furniture) so
como referencia de desenho: nenhum vertice e nenhum pixel dela esta aqui. Nada vem da Meshy. A mesma entrada da sempre o mesmo arquivo.

uso (da raiz): python -I docs/objetos3d/cartoon/tv.py <pasta de saida>
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import (BRILHO, CINZA_ESC, CROMO, FERRO, FERRO_CLARO, OURO, OURO_CLARO, OURO_ESC, cor, cupula, exportar, por,  # noqa: E402
                   revolucao, tons, triangulos, tronco, tubo, tufos)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
GY, GX, GH = 0.54, 0.52, 0.40                 # o gabinete: a altura do centro, a meia largura e a meia altura
Z0, Z1 = -0.36, 0.36                          # o fundo e a frente
TX, TY, TRX, TRY = -0.105, 0.545, 0.315, 0.265   # a tela: o centro e os raios
PX = 0.375                                    # o x do painel dos botoes
BOTOES = (0.70, 0.555)                        # a altura de cada botao
ANT_Y, ANT_ABRE, ANT_ALTO = GY + GH - 0.012, 0.30, 1.42
# a paleta. PROPOSTO, SEM FONTE
CASCA, CASCA_CLARA, CASCA_ESC = (238, 120, 82), (255, 166, 122), (188, 80, 66)
CREME, CREME_ESC = (250, 232, 200), (222, 190, 150)
MOLDURA, MOLDURA_CLARA = (52, 48, 62), (86, 82, 100)
VIDRO, VIDRO_CLARO, VIDRO_ESC = (46, 84, 98), (78, 128, 138), (32, 58, 74)


def pinta_gabinete(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    c = tons(N, CASCA, CASCA_CLARA, CASCA_ESC, alto=0.70, baixo=0.10)
    frente, fundo = (N[:, 2] > 0.7) & (z > Z1 - 0.08), (N[:, 2] < -0.7) & (z < Z0 + 0.08)
    por(c, frente, CREME)                                                            # a cara creme
    painel = frente & (x > PX - 0.085) & (x < PX + 0.085)
    por(c, painel & (y > 0.27) & (y < 0.44) & (np.mod(y - 0.27, 0.044) < 0.022), CREME_ESC)   # as fendas do alto-falante
    por(c, frente & (y < GY - GH + 0.075), CASCA_ESC)                                 # o rodape
    por(c, fundo, CASCA_ESC)
    por(c, fundo & (np.abs(x) < 0.20) & (np.abs(y - GY) < 0.13) & (np.mod(y - GY, 0.06) < 0.03), MOLDURA)   # as fendas de tras
    por(c, (z > -0.02) & (z < 0.015) & ~frente & ~fundo, CASCA_ESC)                   # a emenda do gabinete
    return c


def pinta_moldura(P, N):
    return por(cor(MOLDURA, len(P)), N[:, 1] > 0.5, MOLDURA_CLARA)


def vidro(P, N):
    """0..1: o vidro da tela (o que acende), a face da frente"""
    return (N[:, 2] > 0.7).astype(float)


def pinta_tela(P, N):
    x, y = P[:, 0] - TX, P[:, 1] - TY
    c = cor(VIDRO, len(P))
    v = vidro(P, N) > 0.5
    por(c, ~v, MOLDURA)
    por(c, v & (y < -0.07 - 0.25 * x), VIDRO_ESC)                                     # a metade de baixo, mais funda
    d = x + y                                                                         # o reflexo: duas faixas na diagonal, no canto de cima
    por(c, v & (y > 0.02) & (x < 0.02) & (d > -0.20) & (d < -0.13), VIDRO_CLARO)
    por(c, v & (y > 0.06) & (x < -0.04) & (d > -0.10) & (d < -0.075), BRILHO)
    return c


def pinta_botao(P, N):
    c = tons(N, OURO, OURO_CLARO, OURO_ESC, alto=0.75, baixo=0.15)
    return por(c, (N[:, 2] > 0.9) & (np.abs(P[:, 0] - PX) < 0.008), OURO_ESC)         # o risco do botao


def pinta_pe(P, N):
    return tons(N, MOLDURA_CLARA, CINZA_ESC, MOLDURA, alto=0.6, baixo=0.2)


def pinta_haste(P, N):
    return tons(N, FERRO_CLARO, CROMO, FERRO, alto=0.6, baixo=0.0)


def pinta_base(P, N):
    return tons(N, MOLDURA_CLARA, CINZA_ESC, MOLDURA, alto=0.8, baixo=0.3)


def pecas():
    zs, es = (Z0, -0.24, -0.06, 0.30, Z1), (0.66, 0.88, 1.0, 1.0, 0.965)
    ps = [tubo("gabinete", [(0, GY, z) for z in zs], (0, 1, 0), GX, GH, pinta_gabinete, n=24, escala=es, quina=5.0),
          tubo("moldura", [(TX, TY, Z1 - 0.01), (TX, TY, Z1 + 0.022)], (0, 1, 0), TRX + 0.04, TRY + 0.04, pinta_moldura, n=20, escala=(1.0, 0.97), quina=4.0),
          tubo("tela", [(TX, TY, Z1 + 0.005), (TX, TY, Z1 + 0.034)], (0, 1, 0), TRX, TRY, pinta_tela, n=20, escala=(1.0, 0.95), quina=4.0)]
    ps += [cupula(f"botao_{i}", (PX, y, Z1 - 0.004), (0, 0, 1), 0.058, 0.045, pinta_botao, n=10) for i, y in enumerate(BOTOES)]
    ps += [tronco(f"pe_{i}", (sx * 0.34, sz * 0.20), 0.0, 0.04, GY - GH + 0.05, 0.075, pinta_pe, tampas=(False, False))
           for i, (sx, sz) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1)))]
    ps.append(cupula("antena_base", (0, ANT_Y, -0.04), (0, 1, 0), 0.11, 0.07, pinta_base, n=10))
    for i, s in enumerate((-1, 1)):
        ponta = np.array((s * ANT_ABRE, ANT_ALTO, -0.04))
        ps.append(tubo(f"haste_{i}", [(s * 0.03, ANT_Y + 0.05, -0.04), ponta], (0, 0, 1), 0.013, 0.013, pinta_haste, n=5))
        ps.append(revolucao(f"bolinha_{i}", [(0.016, ponta[1] - 0.03), (0.034, ponta[1]), (0.02, ponta[1] + 0.03), (0, ponta[1] + 0.04)], pinta_botao,
                            n=6, c=(ponta[0], ponta[2]), fundo=True))
    return ps + tufos([(0.44, 0.24, 0.11, 0.07), (-0.46, 0.20, 0.10, 0.06), (-0.30, -0.30, 0.10, 0.06), (0.20, 0.36, 0.08, 0.05)])


def main(saida: str) -> None:
    ps = pecas()
    print("TV", exportar(ps, saida, "tv", CASCA, "tv.py (DigiLab)"), "triangulos", triangulos(ps))


if __name__ == "__main__":
    main(sys.argv[1])
