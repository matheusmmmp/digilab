"""O contrato sensorio-motor no mundo do motor (a P4, docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 3.1; docs/futuro/mundo_3d.md, secao 4).

O porte para o Python das contas do POC (web/app/poc/mundo3d/: inteiros.ts, fisica.ts, sensores.ts e controlador.ts), que e a referencia
(P4-1). Tudo em inteiros (a G-INT confere pela AST: nenhum float, nenhuma divisao de float), sem rng e sem estado: o `digilab/mundo.py`
chama estas funcoes atras das chaves da `ConfigContrato`. A paridade com o TS e a etapa 2 da P4.

O que muda em relacao ao POC, e por que:
- **as 16 direcoes sao as do motor** (o `DIR16` do `mundo.py`, y crescendo para o sul e o setor 1 a nordeste). O POC usa a outra
  orientacao do eixo y; no motor, o setor de um vetor e a orientacao do pet seguem a tabela que o mundo ja usa;
- **o mundo do J5 nao tem solidos de colisao** (P4-4): os troncos so tapam a visao, e as paredes da borda so existem com a chave
  `paredes`. As funcoes recebem a lista de solidos e funcionam com ela vazia;
- **a bola do J5 continua a do mundo de hoje** (a rolagem sorteada no `brincar`); o empurrao fisico (`empurrar` e `passo_bola`) fica
  portado e testado aqui, mas o mundo do J5 nao o usa.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from functools import lru_cache

ESCALA = 1024
# as 16 direcoes do motor (as mesmas do DIR16 de digilab/mundo.py; um teste confere)
DIR16 = ((1024, 0), (946, -392), (724, -724), (392, -946), (0, -1024), (-392, -946), (-724, -724), (-946, -392),
         (-1024, 0), (-946, 392), (-724, 724), (-392, 946), (0, 1024), (392, 946), (724, 724), (946, 392))
# o POC: a bola (empurrao, atrito, restituicao); PROPOSTOS, SEM FONTE, so nas funcoes do empurrao
IMPULSO_BOLA = 10
ATRITO_BOLA = 1
RESTITUICAO = (3, 4)
CATEGORIAS_SOLIDO = ("parede", "obstaculo", "tronco")


def div_arred(n: int, d: int) -> int:
    """n / d arredondado ao mais proximo, meio longe do zero (o div_arred do motor); d > 0"""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def distancia(dx: int, dy: int) -> int:
    return math.isqrt(dx * dx + dy * dy)


def sinal(v: int) -> int:
    return (v > 0) - (v < 0)


def setor_de(dx: int, dy: int) -> int:
    """o setor (0 a 15) do vetor: o de maior produto escalar com o DIR16; no empate, o de menor indice; (0, 0) da 0"""
    melhor, maior = 0, None
    for k, (ox, oy) in enumerate(DIR16):
        p = dx * ox + dy * oy
        if maior is None or p > maior:
            melhor, maior = k, p
    return melhor


def com_comprimento(dx: int, dy: int, c: int) -> tuple[int, int]:
    """o vetor (dx, dy) com o comprimento c, em inteiros; o vetor nulo falha alto"""
    d = distancia(dx, dy)
    if d == 0:
        raise ValueError("direcao de um vetor nulo")
    return div_arred(dx * c, d), div_arred(dy * c, d)


def relativo(setor: int, orientacao: int) -> int:
    """o setor relativo (0 a 15) de um setor absoluto, dada a orientacao"""
    return (setor - orientacao) % 16


# ------------------------------------------------------------------ os solidos
@dataclass(frozen=True)
class Solido:
    """um retangulo [x0, x1) x [y0, y1) no chao; `colide` (o corpo nao entra) e `alto` (tapa a visao) separados: o tronco do J5 tapa e
    nao colide (P4-4)"""

    x0: int
    y0: int
    x1: int
    y1: int
    categoria: str
    colide: bool
    alto: bool

    def __post_init__(self) -> None:
        if self.categoria not in CATEGORIAS_SOLIDO:
            raise ValueError(f"categoria de solido: {self.categoria!r}")
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError(f"solido vazio: {self}")


def ponto_no_retangulo(x: int, y: int, s: Solido) -> bool:
    return s.x0 <= x < s.x1 and s.y0 <= y < s.y1


def circulo_no_retangulo(cx: int, cy: int, r: int, s: Solido) -> bool:
    """o circulo invade o retangulo (fechado): o ponto mais perto fica a menos de r do centro; encostado, a r"""
    px, py = min(max(cx, s.x0), s.x1), min(max(cy, s.y0), s.y1)
    dx, dy = cx - px, cy - py
    return dx * dx + dy * dy < r * r


def circulo_no_circulo(ax: int, ay: int, ar: int, bx: int, by: int, br: int) -> bool:
    dx, dy, soma = ax - bx, ay - by, ar + br
    return dx * dx + dy * dy < soma * soma


def bloqueio_em(x: int, y: int, r: int, solidos: tuple, circulos: tuple = ()) -> tuple | None:
    """o primeiro solido que colide (("solido", indice)) ou circulo (("circulo", indice)) que o circulo (x, y, r) invade; None se nenhum"""
    for i, s in enumerate(solidos):
        if s.colide and circulo_no_retangulo(x, y, r, s):
            return ("solido", i)
    for i, (bx, by, br) in enumerate(circulos):
        if circulo_no_circulo(x, y, r, bx, by, br):
            return ("circulo", i)
    return None


def mover(x0: int, y0: int, r: int, vx: int, vy: int, solidos: tuple, circulos: tuple = ()) -> tuple:
    """um tick: n = max(|vx|, |vy|) passos; em cada um, o alvo e p0 + v i / n arredondado, e o circulo tenta x e depois y, uma subunidade
    por vez. Um eixo bloqueado para naquele eixo ate o fim do tick (o deslize). Devolve (x, y, bloqueio_x, bloqueio_y)"""
    n = max(abs(vx), abs(vy))
    x, y, bx, by = x0, y0, None, None
    for i in range(1, n + 1):
        ax, ay = x0 + div_arred(vx * i, n), y0 + div_arred(vy * i, n)
        if bx is None and ax != x:
            nx = x + sinal(ax - x)
            b = bloqueio_em(nx, y, r, solidos, circulos)
            if b is None:
                x = nx
            else:
                bx = b
        if by is None and ay != y:
            ny = y + sinal(ay - y)
            b = bloqueio_em(x, ny, r, solidos, circulos)
            if b is None:
                y = ny
            else:
                by = b
    return x, y, bx, by


# ------------------------------------------------------------------ a bola do POC (portada e testada; o J5 nao a usa)
def empurrar(px: int, py: int, bx: int, by: int) -> tuple[int, int]:
    """a velocidade que o empurrao passa a bola: IMPULSO_BOLA na direcao do pet para a bola"""
    return com_comprimento(bx - px, by - py, IMPULSO_BOLA)


def passo_bola(x: int, y: int, r: int, vx: int, vy: int, solidos: tuple, circulos: tuple = ()) -> tuple[int, int, int, int]:
    """a bola de um tick: move pela velocidade; o eixo bloqueado reflete com a restituicao (truncada para zero); o atrito tira ATRITO_BOLA
    do modulo, proporcional em cada eixo. Devolve (x, y, vx, vy)"""
    x1, y1, bx, by = mover(x, y, r, vx, vy, solidos, circulos)
    num, den = RESTITUICAO
    if bx is not None:
        vx = -_trunc_div(vx * num, den)
    if by is not None:
        vy = -_trunc_div(vy * num, den)
    s = math.isqrt(vx * vx + vy * vy)
    if s <= ATRITO_BOLA:
        return x1, y1, 0, 0
    return x1, y1, div_arred(vx * (s - ATRITO_BOLA), s), div_arred(vy * (s - ATRITO_BOLA), s)


def _trunc_div(n: int, d: int) -> int:
    """a divisao inteira truncada para zero (o Math.trunc do POC)"""
    q = abs(n) // d
    return q if n >= 0 else -q


# ------------------------------------------------------------------ os sensores
def no_cone(dx: int, dy: int, orientacao: int, cos_meio: int) -> bool:
    """o vetor esta dentro do cone em torno da orientacao (o produto escalar com a direcao >= cos_meio x d, na escala 1024); (0, 0) conta"""
    d = distancia(dx, dy)
    if d == 0:
        return True
    ux, uy = DIR16[orientacao]
    return dx * ux + dy * uy >= cos_meio * d


def tapado(x0: int, y0: int, x1: int, y1: int, opacos: tuple) -> bool:
    """a linha de (x0, y0) a (x1, y1) passa por um solido alto? Os pontos p0 + (p1 - p0) k / n, k = 1 .. n - 1, n = max(|dx|, |dy|)"""
    dx, dy = x1 - x0, y1 - y0
    n = max(abs(dx), abs(dy))
    # so os altos que encostam na caixa do segmento podem conter um ponto dele (o resultado e o mesmo; a conta fica menor)
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    altos = [s for s in opacos if s.alto and s.x0 <= xb and s.x1 >= xa and s.y0 <= yb and s.y1 >= ya]
    if not altos:
        return False
    for k in range(1, n):
        x, y = x0 + div_arred(dx * k, n), y0 + div_arred(dy * k, n)
        if any(ponto_no_retangulo(x, y, s) for s in altos):
            return True
    return False


def visivel(x: int, y: int, ox: int, oy: int, orientacao: int, raio: int, cos_meio: int, opacos: tuple) -> bool:
    """o objeto em (ox, oy) e visto do pet em (x, y): no raio, no cone e sem nada alto no meio"""
    dx, dy = ox - x, oy - y
    return distancia(dx, dy) <= raio and no_cone(dx, dy, orientacao, cos_meio) and not tapado(x, y, ox, oy, opacos)


def bigodes(x: int, y: int, r: int, orientacao: int, solidos: tuple, raio: int) -> list[int]:
    """a distancia livre em 8 setores (de dois em dois, a partir da orientacao), ate o raio: o primeiro t em que o circulo do pet bate num
    solido que colide, menos 1"""
    if not solidos:
        return [raio] * 8                                     # nada que colida: todos livres ate o raio
    out = []
    for k in range(8):
        s = (orientacao + 2 * k) % 16
        ox, oy = DIR16[s]
        livre = raio
        for t in range(1, raio + 1):
            px, py = x + div_arred(ox * t, ESCALA), y + div_arred(oy * t, ESCALA)
            if bloqueio_em(px, py, r, solidos) is not None:
                livre = t - 1
                break
        out.append(livre)
    return out


# ------------------------------------------------------------------ o A* e o controlador
def octil(ax: int, ay: int, bx: int, by: int) -> int:
    dx, dy = abs(ax - bx), abs(ay - by)
    return 10 * (dx + dy) - 6 * min(dx, dy)


@lru_cache(maxsize=8)
def grade(cx_n: int, cy_n: int, sub: int, r: int, solidos: tuple) -> tuple[bool, ...]:
    """as celulas em que o circulo do pet cabe no centro, por indice cy * cx_n + cx. Pura (os solidos sao imutaveis): guardada por argumento"""
    return tuple(bloqueio_em(cx * sub + sub // 2, cy * sub + sub // 2, r, solidos) is None for cy in range(cy_n) for cx in range(cx_n))


def caminho(g: tuple[bool, ...], cx_n: int, cy_n: int, de: tuple[int, int], para: tuple[int, int]) -> list[tuple[int, int]] | None:
    """o A* inteiro (custo 10 no ortogonal e 14 na diagonal, sem cortar canto): as celulas do caminho, da de partida a de chegada, ou None.
    O aberto escolhe o menor (f, h, indice)"""
    ini, fim = de[1] * cx_n + de[0], para[1] * cx_n + para[0]
    if not g[fim]:
        return None
    custo, veio = {ini: 0}, {}
    fechado = set()

    def h(i: int) -> int:
        return octil(i % cx_n, i // cx_n, para[0], para[1])
    # o aberto num heap de (f, h, indice): a entrada velha de uma celula (custo ja baixado, ou fechada) e pulada; o topo valido e o menor
    # (f, h, indice) do aberto, o mesmo que o min sobre o conjunto
    aberto = [(h(ini), h(ini), ini)]
    while aberto:
        f, _h, atual = heapq.heappop(aberto)
        if atual in fechado or f != custo[atual] + _h:
            continue
        if atual == fim:
            cam = []
            i = fim
            while True:
                cam.append((i % cx_n, i // cx_n))
                if i not in veio:
                    break
                i = veio[i]
            return cam[::-1]
        fechado.add(atual)
        ax, ay = atual % cx_n, atual // cx_n
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ax + dx, ay + dy
                if nx < 0 or ny < 0 or nx >= cx_n or ny >= cy_n:
                    continue
                n = ny * cx_n + nx
                if not g[n] or n in fechado:
                    continue
                if dx != 0 and dy != 0 and (not g[ay * cx_n + nx] or not g[ny * cx_n + ax]):
                    continue                                   # sem cortar o canto
                c = custo[atual] + (14 if dx != 0 and dy != 0 else 10)
                if n not in custo or c < custo[n]:
                    custo[n] = c
                    veio[n] = atual
                    hn = h(n)
                    heapq.heappush(aberto, (c + hn, hn, n))
    return None


def livre_mais_perto(g: tuple[bool, ...], cx_n: int, c: tuple[int, int]) -> tuple[int, int]:
    """a celula livre mais perto (octil) de uma celula ocupada; no empate, a de menor indice"""
    melhor, dm = None, None
    for i, livre in enumerate(g):
        if not livre:
            continue
        d = octil(i % cx_n, i // cx_n, c[0], c[1])
        if dm is None or d < dm:
            melhor, dm = (i % cx_n, i // cx_n), d
    if melhor is None:
        raise RuntimeError("o mapa nao tem celula livre")
    return melhor


@dataclass(frozen=True)
class Andar:
    """o que o controlador fez numa decisao: a posicao final, a trajetoria tick a tick (as posicoes depois de cada tick), o comprimento
    andado, por que parou (`chegou`, `bloqueado` ou `hora`), os contatos com os solidos (categoria, setor absoluto) e a orientacao final"""

    x: int
    y: int
    trajetoria: tuple
    andado: int
    parou_por: str
    contatos: tuple
    orientacao: int


def controlar(x0: int, y0: int, tx: int, ty: int, raio_chegar: int, ticks: int, velocidade: int, r: int, solidos: tuple,
              cx_n: int, cy_n: int, sub: int, ticks_bloqueado: int, orientacao: int) -> Andar:
    """O controlador do POC (controlador.ts) para um alvo fixo, nos `ticks` da decisao: a cada tick, o caminho do A* refeito na grade, a
    velocidade ate o centro da celula seguinte (ou ate o alvo, na celula dele) e o movimento com o deslize. Para quando chega (d <=
    raio_chegar), quando fica `ticks_bloqueado` ticks sem sair do lugar ou sem caminho, ou quando acabam os ticks (`hora`). A orientacao
    e o setor do ultimo deslocamento."""
    x, y = x0, y0
    traj, contatos = [], []
    andado, parado, status = 0, 0, "hora"
    g = grade(cx_n, cy_n, sub, r, solidos)

    def celula(px: int, py: int) -> tuple[int, int]:
        return min(cx_n - 1, max(0, px // sub)), min(cy_n - 1, max(0, py // sub))
    for _t in range(ticks):
        if distancia(tx - x, ty - y) <= raio_chegar:
            status = "chegou"
            break
        if parado >= ticks_bloqueado:
            status = "bloqueado"
            break
        destino = celula(tx, ty)
        if not g[destino[1] * cx_n + destino[0]]:
            destino = livre_mais_perto(g, cx_n, destino)
        cam = caminho(g, cx_n, cy_n, celula(x, y), destino)
        if cam is None:
            status = "bloqueado"
            break
        wx, wy = (cam[1][0] * sub + sub // 2, cam[1][1] * sub + sub // 2) if len(cam) > 1 else (tx, ty)
        dx, dy = wx - x, wy - y
        dw = distancia(dx, dy)
        if dw == 0:
            parado += 1
            traj.append((x, y))
            continue
        vx, vy = (dx, dy) if dw <= velocidade else com_comprimento(dx, dy, velocidade)
        nx, ny, bx, by = mover(x, y, r, vx, vy, solidos)
        for b in (bx, by):
            if b is not None and b[0] == "solido":
                s = solidos[b[1]]
                qx, qy = min(max(nx, s.x0), s.x1), min(max(ny, s.y0), s.y1)
                c = (s.categoria, setor_de(qx - nx, qy - ny))
                if c not in contatos:
                    contatos.append(c)
        if (nx, ny) == (x, y):
            parado += 1
        else:
            parado = 0
            orientacao = setor_de(nx - x, ny - y)
            andado += distancia(nx - x, ny - y)
        x, y = nx, ny
        traj.append((x, y))
    else:
        if distancia(tx - x, ty - y) <= raio_chegar:
            status = "chegou"
    return Andar(x, y, tuple(traj), andado, status, tuple(contatos), orientacao)
