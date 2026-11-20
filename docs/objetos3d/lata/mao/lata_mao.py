"""A lata gigante, feita a mao por script (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 17; pedido do Matheus em 2026-11-10: a lata "esta fora
do mapa e ainda esta toda errada", ver a malha e a textura dela e por dentro do mapa).

O desenho segue o concept 1 (docs/mapa_digital/lata/concept/concept_1_cereja.png: a lata de refrigerante em faixas pastel, com o adesivo
das cerejas), mas nada vem da Meshy nem de imagem de terceiros: o corpo e uma superficie de revolucao (PERFIL), o anel de abrir e as
plantas do pe sao solidos simples, e a pintura e uma funcao da posicao no espaco (as faixas em onda pelo angulo e pela altura, as cerejas
no plano desenrolado da frente). Sem marca, sem texto. Os solidos, o atlas e a escrita do glTF sao os do carro
(docs/objetos3d/carro/mao/carro_mao.py). A mesma entrada da sempre o mesmo arquivo.

A lata fica limpa, como no concept (nada de ferrugem nem amassado), tombada de leve e com o pe no chao, entre tufos de musgo e capim. A frente (as cerejas) em +z.

uso (da raiz): python -I docs/objetos3d/lata/mao/lata_mao.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "carro" / "mao"))
from carro_mao import Peca, cor, cupula, exportar, folha, por, tubo, CINZA, CINZA_ESC, CROMO, MUSGO, MUSGO_CLARO, MUSGO_ESC  # noqa: E402

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
R, ALTO, LADOS = 0.52, 2.0, 32
# o perfil (o raio, a altura), de baixo para cima: o fundo, o corpo, o ombro, o gargalo, a borda e a tampa rebaixada
PERFIL = [(0.30, 0.035), (0.40, 0.0), (0.455, 0.022), (R, 0.13), (R, 1.69), (0.50, 1.79), (0.435, 1.925), (0.415, 1.955), (0.432, ALTO), (0.402, ALTO),
          (0.385, 1.955), (0.0, 1.955)]
OMBRO, TAMPA = 1.69, 1.955
INCLINA, AFUNDA = 5.0, 0.07                  # graus para o lado e quanto do pe fica dentro do chao

VERDE, LILAS, AMARELO, ROSA = (172, 234, 200), (204, 178, 238), (254, 232, 134), (252, 168, 190)
CEREJA, CEREJA_ESC, CEREJA_CLARA, BRANCO = (228, 58, 70), (178, 36, 58), (252, 150, 150), (252, 252, 248)
CABO = (96, 168, 74)
FAIXAS = (VERDE, ROSA, AMARELO, LILAS, VERDE, ROSA)
# o adesivo, no plano desenrolado da frente (u = o arco em volta, w = a altura): as duas cerejas (o centro e o raio), o no dos cabos e a folha
CEREJAS = (((-0.150, 0.80), 0.150), ((0.130, 0.72), 0.142))
NO, FOLHA = (0.20, 1.24), ((0.02, 1.27), 0.17, 0.065, 0.22)   # a folha: o centro, o meio comprimento, a meia largura e o giro


def revolucao(nome, perfil, pinta, n=LADOS) -> Peca:
    V, F = [], []
    for r, y in perfil[:-1]:
        for j in range(n):
            a = 2 * math.pi * j / n
            V.append((r * math.sin(a), y, r * math.cos(a)))
    k = len(perfil) - 1
    for i in range(k - 1):
        for j in range(n):
            a, b, c, d = i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            F += [(a, b, c), (a, c, d)]
    topo = len(V); V.append((0.0, perfil[-1][1], 0.0))
    F += [((k - 1) * n + j, (k - 1) * n + (j + 1) % n, topo) for j in range(n)]
    fundo = len(V); V.append((0.0, perfil[0][1] + 0.02, 0.0))
    F += [(fundo, (j + 1) % n, j) for j in range(n)]
    return Peca(nome, V, F, pinta, centro=(0, ALTO / 2, 0))


# ---------------------------------------------------------------- a pintura (P e N por texel; devolve RGB 0..255)
def dist_seg(u, w, a, b):
    eu, ew = b[0] - a[0], b[1] - a[1]
    t = np.clip(((u - a[0]) * eu + (w - a[1]) * ew) / (eu * eu + ew * ew), 0, 1)
    return np.hypot(u - a[0] - t * eu, w - a[1] - t * ew)


def pinta_lata(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    a = np.arctan2(x, z)                                   # 0 na frente (+z)
    raio = np.hypot(x, z)
    # as faixas pastel em onda: a altura mais uma onda pelo angulo (so multiplos inteiros: a emenda de tras fecha)
    v = y / ALTO * 3.1 + 0.62 * np.sin(a + 0.9) + 0.20 * np.sin(2 * a + 0.3) + 1.05
    c = cor(FAIXAS[0], len(P))
    for k in range(1, len(FAIXAS)):
        por(c, v > k, FAIXAS[k])
    # o adesivo das cerejas, na frente
    u, w = a * R, y
    frente = np.abs(a) < 1.25
    d = np.full(len(P), 1e9)
    for (cu, cw), r in CEREJAS:
        d = np.minimum(d, np.hypot(u - cu, w - cw) - r)
    cabos = np.minimum(dist_seg(u, w, (CEREJAS[0][0][0] + 0.03, CEREJAS[0][0][1] + CEREJAS[0][1] - 0.02), NO),
                       dist_seg(u, w, (CEREJAS[1][0][0] + 0.01, CEREJAS[1][0][1] + CEREJAS[1][1] - 0.02), NO)) - 0.020
    (fu, fw), fl, fh, fg = FOLHA
    lu, lw = (u - fu) * math.cos(fg) + (w - fw) * math.sin(fg), -(u - fu) * math.sin(fg) + (w - fw) * math.cos(fg)
    folha_d = (np.hypot(lu / fl, lw / fh) - 1) * fh
    tudo = np.minimum(np.minimum(d, cabos), folha_d)
    por(c, frente & (tudo < 0.042), BRANCO)                 # a borda branca do adesivo
    por(c, frente & (folha_d < 0), MUSGO); por(c, frente & (folha_d < 0) & (np.abs(lw) < 0.008), MUSGO_ESC)
    por(c, frente & (cabos < 0), CABO)
    por(c, frente & (d < 0), CEREJA)
    for (cu, cw), r in CEREJAS:
        dentro = np.hypot(u - cu, w - cw) < r
        por(c, frente & dentro & (np.hypot(u - cu + 0.25 * r, w - cw - 0.22 * r) > 0.98 * r), CEREJA_ESC)      # a sombra em meia-lua, embaixo
        por(c, frente & (np.hypot((u - cu + 0.38 * r) / 0.26, (w - cw - 0.40 * r) / 0.17) < r), CEREJA_CLARA)   # o brilho
    # o metal: o fundo, o gargalo, a borda e a tampa
    metal = (y < 0.075) | (y > OMBRO + 0.115)
    por(c, metal, CINZA)
    por(c, (y > OMBRO + 0.115) & (y < OMBRO + 0.14), CINZA_ESC)
    por(c, (y > TAMPA - 0.01) & (N[:, 1] > 0.5), CROMO)                                         # a borda de cima
    tampa = (N[:, 1] > 0.8) & (raio < 0.39) & (y < TAMPA + 0.01) & (y > 1.0)
    por(c, tampa, CINZA)
    por(c, tampa & (np.abs(raio - 0.33) < 0.012), CINZA_ESC)                                    # o friso da tampa
    por(c, tampa & (np.hypot((x + 0.02) / 0.115, (z - 0.19) / 0.085) < 1.12), CINZA_ESC)        # o furo de beber: a borda e o escuro
    por(c, tampa & (np.hypot((x + 0.02) / 0.115, (z - 0.19) / 0.085) < 1), (40, 44, 58))
    por(c, y < 0.03, CINZA_ESC)
    return c


def pinta_anel(P, N):
    c = cor(CROMO, len(P))
    por(c, N[:, 1] < 0.5, CINZA_ESC)
    por(c, (N[:, 1] >= 0.5) & (np.hypot(P[:, 0] + 0.02, (P[:, 2] + 0.10) / 1.3) < 0.055), CINZA_ESC)    # o furo do anel
    por(c, (N[:, 1] >= 0.5) & (np.hypot(P[:, 0] + 0.02, P[:, 2] - 0.03) < 0.022), CINZA)                # o rebite
    return c


def pinta_musgo(P, N):
    c = cor(MUSGO, len(P))
    por(c, N[:, 1] > 0.80, MUSGO_CLARO); por(c, N[:, 1] < 0.36, MUSGO_ESC)
    return c


def pinta_folha(y0, y1):
    return lambda P, N: por(por(cor(MUSGO, len(P)), (P[:, 1] - y0) / (y1 - y0) < 0.38, MUSGO_ESC), (P[:, 1] - y0) / (y1 - y0) > 0.72, MUSGO_CLARO)


# ---------------------------------------------------------------- as pecas
def inclinar(ps: list[Peca], graus: float, afunda: float) -> None:
    """tomba a lata para o lado (em volta de z) e desce o pe; a pintura continua vendo a lata em pe"""
    a = math.radians(graus)
    Rm = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    for p in ps:
        em_pe = p.pinta
        p.V = p.V @ Rm.T - (0, afunda, 0)
        p.N = p.N @ Rm.T
        p.pinta = lambda P, N, f=em_pe: f((P + (0, afunda, 0)) @ Rm, N @ Rm)


def pecas() -> list[Peca]:
    lata = [revolucao("lata", PERFIL, pinta_lata),
            tubo("anel", [(-0.02, TAMPA + 0.012, -0.20), (-0.02, TAMPA + 0.020, 0.07)], (0, 1, 0), 0.095, 0.012, pinta_anel, n=8, quina=3)]
    inclinar(lata, INCLINA, AFUNDA)
    # o corte do chao: o que fica abaixo de y = 0 some (o pe afundado); os verdes nascem no chao, em volta
    for p in lata:
        p.V[:, 1] = np.maximum(p.V[:, 1], 0.0)
    cx = 0.0
    verdes = []
    for i, (a, r, h) in enumerate(((0.9, 0.17, 0.10), (2.3, 0.21, 0.12), (3.6, 0.16, 0.09), (4.6, 0.20, 0.11), (5.6, 0.14, 0.08))):
        d = R + 0.04
        verdes.append(cupula(f"musgo_{i}", (cx + d * math.sin(a), -0.01, d * math.cos(a)), (0, 1, 0), r, h, pinta_musgo, n=8, ondas=0.16, fase=i * 1.3))
    for i, (a, h, g) in enumerate(((0.5, 0.34, 0.3), (0.7, 0.24, 1.2), (1.6, 0.30, 2.0), (2.9, 0.38, 3.1), (3.1, 0.26, 4.0), (4.1, 0.32, 5.0), (5.2, 0.28, 0.8), (5.9, 0.36, 2.6))):
        d = R + 0.13 + 0.05 * math.sin(i * 2.1)
        x, z = cx + d * math.sin(a), d * math.cos(a)
        verdes.append(folha(f"capim_{i}", (x, 0.0, z), (x + 0.10 * math.cos(g), h, z + 0.10 * math.sin(g)), 0.035, pinta_folha(0.0, h)))
    return lata + verdes


def main(saida: str) -> None:
    print("LATA", exportar(pecas(), saida, "lata", ROSA, "lata_mao.py (DigiLab)"))


if __name__ == "__main__":
    main(sys.argv[1])
