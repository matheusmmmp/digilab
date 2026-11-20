# A ilha da prancha L1 vista de cima: uma celula vale P px, nas cores que a propria cena pinta (cena.ts: PALETA_ILHA, a grama por regiao,
# o caminho e a areia; a agua e a cor de base do shader, vec3(0.55, 0.88, 0.97), cena.ts:206). O planalto e o morro ficam 7 % mais
# escuros por nivel, para ler o relevo; as arvores de enfeite (sem doMotor) sao pontos da grama da mata escurecida. Nenhuma cor nova.
# Uso: python docs/pranchas/ux-lugares/ilha_png.py ilha.json ilha_cima.png 6   (o ilha.json sai de ilha_json.mts)
import json
import sys

from PIL import Image, ImageDraw

d = json.load(open(sys.argv[1], encoding="utf-8"))
P = int(sys.argv[3])
GRAMA = {"casa": 0x9CDB72, "jardim": 0x8FD16A, "campo": 0xA9D870, "mata": 0x74B957, "moldura": 0x8FD16A}
CAMINHO, AREIA, AGUA = 0xD9C08C, 0xF3E2B0, (140, 224, 247)


def rgb(h: int) -> tuple:
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255)


im = Image.new("RGB", (d["larg"] * P, d["prof"] * P))
dr = ImageDraw.Draw(im)
for i, (tipo, nivel, regiao) in enumerate(d["celulas"]):
    x, z = i % d["larg"], i // d["larg"]
    c = {"agua": AGUA, "areia": rgb(AREIA), "caminho": rgb(CAMINHO)}.get(tipo) or rgb(GRAMA.get(regiao, GRAMA["moldura"]))
    f = 1 - 0.07 * max(0, nivel)
    dr.rectangle([x * P, z * P, x * P + P - 1, z * P + P - 1], fill=tuple(int(v * f) for v in c))
for modelo, ox, oz, motor in d["objetos"]:
    if modelo in ("pinheiro", "arvore_redonda", "arbusto") and not motor:
        X, Z, r = (ox - d["x0"]) * P, (oz - d["z0"]) * P, P * (0.9 if modelo != "arbusto" else 0.6)
        dr.ellipse([X - r, Z - r, X + r, Z + r], fill=tuple(int(v * 0.72) for v in rgb(GRAMA["mata"])))
im.save(sys.argv[2])
