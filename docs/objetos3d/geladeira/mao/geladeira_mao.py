"""A geladeira abandonada, feita a mao por script (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 16; pedido do Matheus em 2026-11-09, depois
do carro da secao 15: "agora arrume essa geladeira tambem").

O desenho segue o esboco 1 (esbocos/esboco_1_retro_duas_portas.png: a geladeira retro verde-menta de duas portas, os puxadores cromados,
a hera subindo pelo lado e o vaso em cima), mas nada vem da Meshy nem de imagem de terceiros: o corpo e as portas sao secoes de cantos
redondos, as pecas (puxadores, dobradicas, vaso, broto, folhas da hera, musgo) sao solidos simples, e a pintura e uma funcao da posicao
no espaco. Os solidos, o atlas e a escrita do glTF sao os do carro (docs/objetos3d/carro/mao/carro_mao.py). A mesma entrada da sempre o
mesmo arquivo.

uso (da raiz): python -I docs/objetos3d/geladeira/mao/geladeira_mao.py <pasta de saida>
"""
import math, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "carro" / "mao"))
from carro_mao import (Peca, caixa, cor, cupula, exportar, folha, mancha, por, ruido, tubo,  # noqa: E402
                       CAIXA_RODA, CINZA, CINZA_ESC, CROMO, FERRUGEM, FERRUGEM_ESC, MUSGO, MUSGO_CLARO, MUSGO_ESC, TERRA, TRACO)

# ---------------------------------------------------------------- as medidas (unidades do modelo; a vista normaliza a altura). PROPOSTO, SEM FONTE
LX, LZ, ZC, ALTO, QUINA = 0.42, 0.34, -0.04, 1.56, 5.0   # o corpo: as meias larguras em x e em z, o centro em z, a altura, o canto
ZP0, ZP1 = 0.28, 0.40                                    # as portas: de onde saem do corpo ate a face da frente
PORTAS = ((0.075, 0.905), (0.935, 1.515))                # a de baixo e a de cima: o y de baixo e o de cima
PX = 0.395                                               # a meia largura das portas
VASO = (0.13, -0.06)                                     # o x e o z do vaso, em cima
INCLINA = 3.5                                            # graus: a geladeira tombada de leve para o lado, meio afundada na areia

MENTA, MENTA_CLARO, MENTA_ESC = (132, 224, 184), (186, 244, 214), (88, 184, 150)
BARRO, BARRO_CLARO, BARRO_ESC = (206, 112, 68), (232, 146, 94), (160, 78, 46)
LASCA = (204, 212, 206)

# a hera: cada ramo e uma linha no plano da face (a lateral em (z, y), a porta em (x, y)). PROPOSTO, SEM FONTE: desenhada olhando o esboco 1
RAMOS_LADO = {1: [[(-0.24, 0.0), (-0.13, 0.24), (-0.21, 0.50), (-0.06, 0.74), (-0.13, 0.98), (0.02, 1.20)],
                  [(0.10, 0.0), (0.19, 0.20), (0.07, 0.42), (0.17, 0.66)]],
              -1: [[(0.02, 0.0), (-0.10, 0.28), (0.04, 0.54), (-0.07, 0.80)],
                   [(-0.22, 0.0), (-0.26, 0.22), (-0.17, 0.40)]]}
RAMOS_TRAS = [[(-0.30, 0.0), (-0.22, 0.30), (-0.32, 0.58), (-0.20, 0.86), (-0.27, 1.12), (-0.12, 1.34)], [(0.28, 0.0), (0.34, 0.26), (0.24, 0.50), (0.33, 0.78), (0.22, 1.02)]]
RAMOS_PORTA = [[(0.35, 0.075), (0.26, 0.22), (0.31, 0.38), (0.19, 0.52)], [(0.20, 0.075), (0.10, 0.18), (0.13, 0.30)]]
# as lascas da tinta: o centro e o raio (a ferrugem na borda, o fundo claro no meio)
LASCAS = [((0.20, 1.36, ZP1), 0.035), ((-0.26, 1.10, ZP1), 0.028), ((0.30, 1.06, ZP1), 0.022), ((-0.22, 0.70, ZP1), 0.04), ((0.05, 0.36, ZP1), 0.03),
          ((-0.30, 0.22, ZP1), 0.035), ((LX, 1.30, 0.10), 0.035), ((LX, 0.86, -0.22), 0.03), ((-LX, 1.24, -0.10), 0.04), ((-LX, 0.50, 0.14), 0.03),
          ((0.10, 1.10, ZC - LZ), 0.04), ((-0.24, ALTO, -0.14), 0.035)]


def xlado(z):
    """a meia largura do corpo em z (a secao de cantos redondos)"""
    return LX * (1 - min(abs(z - ZC) / LZ, 0.999) ** QUINA) ** (1 / QUINA)


def dist_linha(a, b, pts):
    """a distancia de cada ponto (a, b) do plano a uma linha quebrada"""
    d = np.full(a.shape, 1e9)
    for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
        ea, eb = a1 - a0, b1 - b0
        t = np.clip(((a - a0) * ea + (b - b0) * eb) / (ea * ea + eb * eb), 0, 1)
        d = np.minimum(d, np.hypot(a - a0 - t * ea, b - b0 - t * eb))
    return d


def lascas(c, P, N):
    for centro, r in LASCAS:
        fase = centro[1] * 7.0 + centro[0] * 3.0
        d = mancha(P, centro, r * 1.25, fase)
        nucleo = (centro[0] + 0.25 * r, centro[1] + 0.2 * r, centro[2] + 0.2 * r)
        por(c, d < 1, FERRUGEM); por(c, (d < 1) & (mancha(P, nucleo, 0.7 * r, fase + 1.9) < 1), LASCA)
        por(c, (np.abs(N[:, 1]) < 0.5) & (np.hypot(P[:, 0] - centro[0], P[:, 2] - centro[2]) < 0.2 * r) & (P[:, 1] < centro[1]) & (P[:, 1] > centro[1] - 2.6 * r), FERRUGEM)
    return c


def pinta_corpo(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    c = cor(MENTA, len(P))
    lado, tras, cima = np.abs(N[:, 0]) > 0.6, N[:, 2] < -0.6, N[:, 1] > 0.6
    por(c, N[:, 1] > 0.8, MENTA_CLARO)
    por(c, (y < 0.16) & ~cima, MENTA_ESC)                                   # o rodape mais escuro
    por(c, lado & (np.abs(z - ZC + 0.02 - 0.20 * (y - 0.8)) < 0.035) & (y > 0.3) & (y < 1.42), MENTA_CLARO)   # o reflexo chapado na lateral
    onda = 0.07 + 0.03 * np.sin(8 * (x + z) + 1.0) + 0.02 * np.sin(23 * (x - z))
    por(c, (y < onda) & ~cima, FERRUGEM); por(c, (y < onda - 0.045) & ~cima, FERRUGEM_ESC)   # a ferrugem do pe
    lascas(c, P, N)
    # a grade do motor, atras
    g = tras & (np.abs(x) < 0.17) & (y > 0.24) & (y < 0.92)
    por(c, tras & (np.abs(x) < 0.19) & (y > 0.22) & (y < 0.94), TRACO); por(c, g, CINZA_ESC); por(c, g & (((y - 0.24) / 0.07) % 1 < 0.3), CAIXA_RODA)
    for ramo in RAMOS_TRAS:
        por(c, tras & (dist_linha(x, y, ramo) < 0.011), MUSGO_ESC)
    # o anel de ferrugem embaixo do vaso
    rv = np.hypot(x - VASO[0], z - VASO[1])
    por(c, cima & (rv < 0.135 * (1 + 0.12 * np.sin(5 * np.arctan2(z - VASO[1], x - VASO[0])))) & (y > 1.4), FERRUGEM)
    # os ramos da hera na lateral
    for s, ramos in RAMOS_LADO.items():
        for ramo in ramos:
            por(c, lado & (x * s > 0) & (dist_linha(z, y, ramo) < 0.011), MUSGO_ESC)
    return c


def pinta_porta(y0, y1):
    def f(P, N):
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        c = cor(MENTA, len(P))
        frente = N[:, 2] > 0.6
        por(c, ~frente & (N[:, 1] > 0.5), MENTA_CLARO); por(c, ~frente & (N[:, 1] < -0.3), MENTA_ESC)
        u = x - 0.42 * (y - (y0 + y1) / 2)                                  # o reflexo chapado: duas faixas na diagonal
        por(c, frente & (((u > -0.20) & (u < -0.10)) | ((u > -0.06) & (u < -0.035))) & (y > y0 + 0.07) & (y < y1 - 0.07), MENTA_CLARO)
        por(c, frente & (y < y0 + 0.05 + 0.02 * np.sin(x * 19)) & (y0 < 0.5), MENTA_ESC)
        lascas(c, P, N)
        if y1 > 1.4:                                                        # o emblema na porta de cima
            e = np.hypot((x + 0.20) / 0.075, (y - 1.40) / 0.032)
            por(c, frente & (e < 1.25), TRACO); por(c, frente & (e < 1), CROMO)
        else:
            for ramo in RAMOS_PORTA:
                por(c, frente & (dist_linha(x, y, ramo) < 0.011), MUSGO_ESC)
        return c
    return f


def pinta_cromo(P, N):
    c = cor(CINZA, len(P))
    por(c, N[:, 1] > 0.35, CROMO); por(c, N[:, 1] < -0.45, CINZA_ESC)
    return c


def pinta_vaso(P, N):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    r = np.hypot(x - VASO[0], z - VASO[1])
    c = cor(BARRO, len(P))
    por(c, (N[:, 0] - N[:, 2]) < -0.55, BARRO_ESC); por(c, (N[:, 0] + 0.3 * N[:, 2]) > 0.80, BARRO_CLARO)   # a sombra e a luz chapadas
    por(c, (y > ALTO + 0.165) & (N[:, 1] < 0.6), BARRO_CLARO)                 # a borda
    por(c, (N[:, 1] > 0.6) & (r < 0.118), BARRO_ESC); por(c, (N[:, 1] > 0.6) & (r < 0.098), TERRA)
    return c


def pinta_folha_hera(P, N, c0, raio):
    d = np.linalg.norm(P - c0, axis=1) / raio
    c = cor(MUSGO, len(P))
    por(c, d < 0.42, MUSGO_CLARO); por(c, ruido(P, 31, c0[1] * 9) > 0.45, MUSGO_ESC)
    return c


def pinta_musgo(P, N):
    c = cor(MUSGO, len(P))
    por(c, N[:, 1] > 0.93, MUSGO_CLARO); por(c, N[:, 1] < 0.55, MUSGO_ESC)
    return c


def pinta_broto(P, N):
    c = cor(MUSGO, len(P))
    por(c, P[:, 1] > ALTO + 0.31, MUSGO_CLARO); por(c, P[:, 1] < ALTO + 0.23, MUSGO_ESC)
    return c


# ---------------------------------------------------------------- as pecas
def hera(nome, c, n, t, raio) -> Peca:
    """uma folha da hera encostada na face: o centro, a normal da face, a direcao da ponta e o tamanho"""
    c, n, t = (np.asarray(v, float) for v in (c, n, t))
    t = t / np.linalg.norm(t); w = np.cross(n, t)
    V = [c + n * 0.022, c + t * raio, c + w * raio * 0.72 + t * raio * 0.1, c - t * raio * 0.62, c - w * raio * 0.72 + t * raio * 0.1]
    F = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1)]
    return Peca(nome, V, F, lambda P, N, c0=c: pinta_folha_hera(P, N, c0, raio), centro=c - n)


def folhas_do_ramo(ramo, passo=0.085):
    """os pontos ao longo do ramo onde nasce uma folha: a posicao no plano, a direcao da ponta (para um lado e para o outro) e a ordem"""
    out, sobra, k = [], passo * 0.6, 0
    for (a0, b0), (a1, b1) in zip(ramo, ramo[1:]):
        L = math.hypot(a1 - a0, b1 - b0)
        ta, tb = (a1 - a0) / L, (b1 - b0) / L
        while sobra < L:
            lado = 1 if k % 2 == 0 else -1
            ang = lado * math.radians(58)
            da, db = ta * math.cos(ang) - tb * math.sin(ang), ta * math.sin(ang) + tb * math.cos(ang)
            out.append((a0 + ta * sobra + da * 0.035, b0 + tb * sobra + db * 0.035, da, db, k)); sobra += passo; k += 1
        sobra -= L
    return out


def pecas() -> list[Peca]:
    ys = [0.0, 0.03, 0.10, 0.60, 1.20, 1.46, 1.52, 1.548, ALTO]
    esc = [0.93, 0.985, 1.0, 1.0, 1.0, 1.0, 0.975, 0.93, 0.84]
    ps = [tubo("corpo", [(0, y, ZC) for y in ys], (0, 0, 1), LX, LZ, pinta_corpo, n=32, escala=esc, quina=QUINA)]
    for i, (y0, y1) in enumerate(PORTAS):
        ym, h = (y0 + y1) / 2, (y1 - y0) / 2
        ps.append(tubo(f"porta_{i}", [(0, ym, z) for z in (ZP0, ZP1 - 0.035, ZP1 - 0.008, ZP1)], (0, 1, 0), PX, h, pinta_porta(y0, y1), n=32,
                       escala=[1.0, 1.0, 0.975, 0.92], quina=7.0))
    for i, y in enumerate((0.80, 1.035)):   # os puxadores: a barra com os dois pes
        ps.append(tubo(f"puxador_{i}", [(-0.03, y, ZP1 - 0.01), (-0.03, y, ZP1 + 0.05), (0.03, y, ZP1 + 0.062), (0.24, y, ZP1 + 0.062), (0.30, y, ZP1 + 0.05),
                                        (0.30, y, ZP1 - 0.01)], (0, 1, 0), 0.024, 0.030, pinta_cromo, n=6, quina=2.6))
    for i, y in enumerate((0.26, 0.76, 1.08, 1.38)):   # as dobradicas, no canto esquerdo
        ps.append(caixa(f"dobradica_{i}", (-PX - 0.012, y, ZP0 + 0.035), (0.04, 0.10, 0.05), pinta_cromo))
    # o vaso de barro e o broto
    vx, vz = VASO
    perfil = [(0.0, 0.086), (0.04, 0.094), (0.13, 0.112), (0.135, 0.128), (0.175, 0.132), (0.18, 0.122)]
    ps.append(tubo("vaso", [(vx, ALTO - 0.006 + y, vz) for y, _ in perfil], (0, 0, 1), 1.0, 1.0, pinta_vaso, n=12, escala=[r for _, r in perfil]))
    yb = ALTO + 0.165
    for i, (a, h, inc, larg) in enumerate([(0.4, 0.20, 0.07, 0.034), (2.6, 0.17, 0.09, 0.034), (4.6, 0.13, 0.08, 0.030), (1.5, 0.10, 0.07, 0.026)]):
        b = (vx + 0.012 * math.cos(a), yb, vz + 0.012 * math.sin(a))
        ps.append(folha(f"broto_{i}", b, (b[0] + inc * math.cos(a), yb + h, b[2] + inc * math.sin(a)), larg, pinta_broto))
    # a hera em relevo: as folhas ao longo dos ramos da lateral e da porta de baixo
    k = 0
    for s, ramos in RAMOS_LADO.items():
        for ramo in ramos:
            for z, y, dz, dy, i in folhas_do_ramo(ramo):
                ps.append(hera(f"hera_{k}", (s * (xlado(z) + 0.004), max(y, 0.04), z), (s, 0, 0), (0, dy, dz), 0.058 + 0.012 * ((i * 7) % 3))); k += 1
    for ramo in RAMOS_PORTA:
        for x, y, dx, dy, i in folhas_do_ramo(ramo):
            ps.append(hera(f"hera_{k}", (x, max(y, 0.10), ZP1 + 0.004), (0, 0, 1), (dx, dy, 0), 0.056 + 0.012 * ((i * 5) % 3))); k += 1
    for ramo in RAMOS_TRAS:   # atras: e o lado que o jogador ve, porque a frente da geladeira olha para a area
        for x, y, dx, dy, i in folhas_do_ramo(ramo):
            ps.append(hera(f"hera_{k}", (x, max(y, 0.04), ZC - LZ * (1 - min(abs(x) / LX, 0.999) ** QUINA) ** (1 / QUINA) - 0.004), (0, 0, -1), (dx, dy, 0),
                           0.058 + 0.012 * ((i * 3) % 3))); k += 1
    # o musgo no pe
    for i, (x, z, r, h, fase) in enumerate([(0.34, 0.34, 0.15, 0.13, 0.5), (-0.38, 0.22, 0.13, 0.11, 1.6), (0.42, -0.16, 0.14, 0.12, 2.7),
                                            (-0.30, -0.32, 0.14, 0.11, 3.8), (0.08, 0.42, 0.11, 0.09, 4.9)]):
        ps.append(cupula(f"musgo_{i}", (x, 0.02, z), (0, 1, 0), r, h, pinta_musgo, n=8, ondas=0.16, fase=fase))
    return ps


def inclinar(ps: list[Peca], graus: float) -> list[Peca]:
    """gira tudo em volta do eixo z (a geladeira tombada para o lado); o musgo do pe fica no chao"""
    a = math.radians(graus)
    R = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    for p in ps:
        if not p.nome.startswith("musgo"):
            p.V, p.N = p.V @ R.T, p.N @ R.T
            p.pinta = lambda P, N, f=p.pinta: f(P @ R, N @ R)   # a pintura enxerga a geladeira em pe
    return ps


def main(saida: str) -> None:
    print("GELADEIRA", exportar(inclinar(pecas(), INCLINA), saida, "geladeira", MENTA, "geladeira_mao.py (DigiLab)"))


if __name__ == "__main__":
    main(sys.argv[1])
