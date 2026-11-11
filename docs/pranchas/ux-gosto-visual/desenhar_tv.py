"""Desenha a TV de tubo do #814 (docs/objetos3d/cartoon/tv.py) para a prancha, vista pela camera da ilha (do sul, de cima): de lado
(o giro de hoje), em tres quartos (a UX-GV-3, 40 graus) e com a tela acesa. Amostra cada triangulo, pinta pela funcao da peca e desenha
com z-buffer, o dobro do tamanho, e reduz. So desenho da prancha: nada do jogo. Os angulos sao PROPOSTO, SEM FONTE.
uso (da raiz): python docs/pranchas/ux-gosto-visual/desenhar_tv.py"""
import math, sys
from pathlib import Path
import numpy as np
from PIL import Image

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parents[1] / "objetos3d" / "cartoon"))
import tv  # noqa: E402

ELEV, L, S = 38, 300, 3   # a inclinacao da camera, o lado da imagem e a superamostragem


def programa(P, N):
    """a tela acesa: um desenho de faixas (o "desenho colorido e agitado" da TV do jogo), so na face da frente"""
    c = tv.pinta_tela(P, N)
    v = N[:, 2] > 0.7
    x, y = P[:, 0] - tv.TX, P[:, 1] - tv.TY
    ceu, sol, morro, chao = (120, 200, 255), (255, 228, 130), (104, 184, 156), (238, 120, 82)
    c[v] = ceu
    c[v & (y < -0.02 + 0.10 * np.sin(x * 9))] = morro
    c[v & (y < -0.14)] = chao
    c[v & ((x - 0.12) ** 2 + (y - 0.10) ** 2 < 0.006)] = sol
    return c


def pontos(ligada: bool):
    ps = tv.pecas()
    P, C, NN = [], [], []
    for p in ps:
        pinta = programa if (ligada and p.nome == "tela") else p.pinta
        V, N, F = p.V, p.N, p.F
        a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
        for i in range(len(F)):
            k = int(max(40, area[i] * 900000))
            r = np.random.default_rng(i).random((k, 2))
            m = r.sum(axis=1) > 1
            r[m] = 1 - r[m]
            w = np.column_stack([1 - r.sum(axis=1), r])
            pp, nn = w @ V[F[i]], w @ N[F[i]]
            nn /= np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-9)
            P.append(pp); C.append(pinta(pp, nn)); NN.append(nn)
    return np.vstack(P), np.vstack(C), np.vstack(NN)


def desenhar(giro: float, ligada: bool, saida: str) -> None:
    """giro: 0 = a tela para a camera (o sul); 90 = a tela para o oeste (a esquerda da imagem)"""
    P, C, NN = pontos(ligada)
    a, e, G = math.radians(giro), math.radians(ELEV), L * S
    Ry = np.array([[math.cos(a), 0, -math.sin(a)], [0, 1, 0], [math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
    Q, n2 = (P - (0, 0.70, 0)) @ Ry.T @ Rx.T, NN @ Ry.T @ Rx.T
    o = np.argsort(Q[:, 2]); o = o[n2[o, 2] > 0.0]
    s = G / 1.9
    xi, yi = (Q[o, 0] * s + G / 2).astype(int), (G / 2 - Q[o, 1] * s).astype(int)
    img = np.zeros((G, G, 4), np.uint8)
    for dx in (0, 1, 2):
        for dy in (0, 1, 2):
            xx, yy = np.clip(xi + dx, 0, G - 1), np.clip(yi + dy, 0, G - 1)
            img[yy, xx, :3] = C[o]; img[yy, xx, 3] = 255
    Image.fromarray(img, "RGBA").resize((L, L), Image.LANCZOS).save(AQUI / "img" / saida, optimize=True)
    print(saida)


if __name__ == "__main__":
    desenhar(90, False, "tv_lado.png")          # hoje: a tela para o oeste, de lado para a camera
    desenhar(90, True, "tv_lado_ligada.png")
    desenhar(50, False, "tv_34.png")            # a UX-GV-3: 40 graus para o sul
    desenhar(50, True, "tv_34_ligada.png")
    desenhar(0, True, "tv_frente_ligada.png")   # a saida (a) do plano, para comparar
