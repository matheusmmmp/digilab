"""A figura do mapa proposto da ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12; PROPOSTO, SEM FONTE): 128 x 60 celulas.

So o desenho para o Matheus aprovar antes do codigo: nada daqui e lido pelo motor. Gera, na mesma pasta:
  - mapa_proposto.txt: uma linha de texto por linha de celulas (`~` mar, `r` agua doce, `.` terra, `=` ponte, `T` arvore, `#` marco);
  - mapa_proposto.png: a mesma coisa pintada, com os lugares marcados, e a ilha de hoje (64 x 30) na mesma escala para comparar.

Deterministico: a rng tem semente fixa. Uso: python docs/pranchas/ilha-grande/gerar_figura.py
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[2]))
from digilab.config import AGUA_ILHA  # noqa: E402  (a ilha de hoje, para a comparacao)

W, H = 128, 60
MAR, DOCE, TERRA, PONTE, ARVORE, MARCO = "~", "r", ".", "=", "T", "#"

# os lugares e os marcos (x, y em celulas): PROPOSTO
LUGARES = {"lar": (20, 30), "praça": (64, 30), "saco": (24, 24), "portão": (64, 7), "barraca": (102, 21), "cais": (72, 51)}
MARCOS = {"carro": (30, 21, 3, 2), "lata": (34, 13, 2, 2), "geladeira": (103, 44, 1, 1), "trilho": (110, 31, 2, 3)}   # x, y, largura, altura
PONTES = (17, 33, 47)                 # as linhas de cima de cada ponte (duas linhas cada)
LAGOS = ((87, 8, 6, 3.2), (27, 41, 7, 3.6), (52, 15, 3.2, 2))      # cx, cy, rx, ry
BOSQUES = ((24, 17, 6, 3, 12), (36, 46, 8, 3, 12), (76, 13, 6, 3, 9), (104, 16, 6, 3, 12), (108, 40, 5, 4, 9), (58, 45, 6, 3, 8),
           (94, 47, 5, 2, 6), (16, 33, 3, 4, 7))       # cx, cy, rx, ry, quantas arvores
SOLTAS = 22


def costa(x: int, y: int) -> bool:
    """dentro da ilha: uma elipse com a borda ondulada"""
    dx, dy = (x + 0.5 - W / 2) / (W / 2 - 8), (y + 0.5 - H / 2) / (H / 2 - 5)
    ang = math.atan2(dy, dx)
    borda = 1 + 0.06 * math.sin(3 * ang + 0.7) + 0.045 * math.sin(7 * ang + 2.1) + 0.03 * math.sin(13 * ang)
    return dx * dx + dy * dy < borda * borda


def rio_x(y: int) -> int:
    """a coluna de oeste do rio (duas celulas de largura) em cada linha; reto debaixo de cada ponte"""
    for p in PONTES:
        if p - 1 <= y <= p + 2:
            y = p
    return 86 + round(5 * math.sin(y / 7.0))


def gerar() -> list[str]:
    g = [[TERRA if costa(x, y) else MAR for x in range(W)] for y in range(H)]
    for y in range(10, H):
        for x in (rio_x(y), rio_x(y) + 1):
            if g[y][x] == TERRA:
                g[y][x] = DOCE
        if y > 10 and rio_x(y) != rio_x(y - 1):        # a curva fecha na diagonal: o pet nao passa pelo canto
            for x in range(min(rio_x(y), rio_x(y - 1)), max(rio_x(y), rio_x(y - 1)) + 2):
                if g[y][x] == TERRA:
                    g[y][x] = DOCE
    for cx, cy, rx, ry in LAGOS:
        for y in range(H):
            for x in range(W):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 < 1 and g[y][x] == TERRA:
                    g[y][x] = DOCE
    for p in PONTES:
        for y in (p, p + 1):
            for x in (rio_x(p), rio_x(p) + 1):
                g[y][x] = PONTE
    for x0, y0, w, h in MARCOS.values():
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                assert g[y][x] == TERRA, ("marco fora da terra", x, y)
                g[y][x] = MARCO
    # as arvores: longe da agua (1 celula), dos lugares, dos marcos, das pontes e umas das outras
    r = random.Random(20261111)
    arvores: list[tuple[int, int]] = []

    def livre(x: int, y: int) -> bool:
        if not (1 <= x < W - 1 and 1 <= y < H - 1):
            return False
        if any(g[y + j][x + i] != TERRA for j in (-1, 0, 1) for i in (-1, 0, 1)):
            return False
        if any(math.hypot(x - lx, y - ly) < 6 for lx, ly in LUGARES.values()):
            return False
        if any(abs(y - p) < 4 and abs(x - rio_x(p)) < 7 for p in PONTES):
            return False
        return all(math.hypot(x - ax, y - ay) >= 2.2 for ax, ay in arvores)

    def plantar(sorteio, quantas: int) -> None:
        feitas = tentativas = 0
        while feitas < quantas:
            tentativas += 1
            if tentativas >= 5000:        # o bosque nao coube inteiro (a costa ou a agua por perto): fica com as que couberam
                print(f"bosque incompleto: {feitas} de {quantas}")
                return
            x, y = sorteio()
            if livre(x, y):
                arvores.append((x, y))
                feitas += 1

    for cx, cy, rx, ry, n in BOSQUES:
        plantar(lambda: (round(cx + r.uniform(-rx, rx)), round(cy + r.uniform(-ry, ry))), n)
    plantar(lambda: (r.randrange(W), r.randrange(H)), SOLTAS)
    for x, y in arvores:
        g[y][x] = ARVORE
    return ["".join(l) for l in g]


def secas(linhas) -> int:
    return sum(l.count(TERRA) + l.count(PONTE) for l in linhas)


def ligada(linhas) -> bool:
    """toda a terra e alcancavel a partir do lar, andando em 4 direcoes por terra e ponte"""
    anda = {(x, y) for y, l in enumerate(linhas) for x, c in enumerate(l) if c in (TERRA, PONTE)}
    vistos, fila = {LUGARES["lar"]}, [LUGARES["lar"]]
    assert LUGARES["lar"] in anda
    while fila:
        x, y = fila.pop()
        for v in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if v in anda and v not in vistos:
                vistos.add(v)
                fila.append(v)
    return len(vistos) == len(anda)


CORES = {MAR: (86, 168, 220), DOCE: (132, 206, 236), TERRA: (126, 190, 96), PONTE: (176, 132, 84), ARVORE: (44, 110, 60), MARCO: (150, 150, 160),
         "areia": (232, 216, 160)}


def pintar(d: ImageDraw.ImageDraw, linhas, x0: int, y0: int, px: int) -> None:
    alt, larg = len(linhas), len(linhas[0])
    for y, l in enumerate(linhas):
        for x, c in enumerate(l):
            cor = CORES[c]
            if c == TERRA and any(0 <= y + j < alt and 0 <= x + i < larg and linhas[y + j][x + i] == MAR
                                  for j in (-2, -1, 0, 1, 2) for i in (-2, -1, 0, 1, 2)):
                cor = CORES["areia"]
            d.rectangle([x0 + x * px, y0 + y * px, x0 + (x + 1) * px - 1, y0 + (y + 1) * px - 1], fill=cor)
            if c == ARVORE:
                d.ellipse([x0 + x * px - 2, y0 + y * px - 2, x0 + (x + 1) * px + 1, y0 + (y + 1) * px + 1], fill=cor)


def main() -> None:
    linhas = gerar()
    assert len(linhas) == H and all(len(l) == W for l in linhas)
    assert ligada(linhas), "ha terra que o pet nao alcanca"
    assert set(linhas[0]) == set(linhas[1]) == set(linhas[-1]) == set(linhas[-2]) == {MAR} and all(l[:2] == l[-2:] == MAR * 2 for l in linhas), "a ilha encosta na borda do mapa"
    (AQUI / "mapa_proposto.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    px, margem, topo = 8, 16, 44
    img = Image.new("RGB", (W * px + 2 * margem, topo + H * px + 30 * px + 3 * margem + 40), (24, 30, 40))
    d = ImageDraw.Draw(img)
    hoje = secas(AGUA_ILHA)
    d.text((margem, 10), f"A ilha proposta: {W} x {H} celulas, {secas(linhas)} de terra livre, {sum(l.count(ARVORE) for l in linhas)} arvores, "
           f"{len(PONTES)} pontes (PROPOSTO)", fill=(255, 255, 255))
    d.text((margem, 24), "verde escuro: arvore (o pet contorna)   cinza: marco (o pet contorna)   marrom: ponte   azul claro: rio e lagos", fill=(190, 200, 210))
    pintar(d, linhas, margem, topo, px)
    for nome, (x, y) in LUGARES.items():
        cx, cy = margem + x * px + px // 2, topo + y * px + px // 2
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=(255, 255, 255), width=2)
        d.text((cx + 8, cy - 6), nome, fill=(255, 255, 255))
    for nome, (x, y, w, _h) in MARCOS.items():
        d.text((margem + (x + w) * px + 4, topo + y * px), nome, fill=(40, 40, 50))
    y1 = topo + H * px + margem + 20
    d.text((margem, y1 - 16), f"A ilha de hoje, na mesma escala: 64 x 30 celulas, {hoje} de terra", fill=(255, 255, 255))
    pintar(d, AGUA_ILHA, margem, y1, px)
    img.save(AQUI / "mapa_proposto.png")
    print(f"terra livre: {secas(linhas)} (hoje: {hoje}); arvores: {sum(l.count(ARVORE) for l in linhas)}")


if __name__ == "__main__":
    main()
