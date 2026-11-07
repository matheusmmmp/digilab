"""Os lugares no estilo da Ilha (docs/TAREFA_V3_LUGARES_3D.md, secao 12): troca cada cor chapada da textura de um lugar pela versao da
Ilha, mais escura e mais saturada, perto dos kits CC0 da cena (o marrom dos troncos, o verde da grama, o cinza-azulado das pedras). Vista
na cena com o toon, a paleta da Meshy saia em pastel (a luz do toon clareia). A troca e exata, cor a cor: a textura ja tem uma cor por face
(o conserto de cada lugar), e uma cor fora da tabela falha alto. A saida e um PNG de paleta (sem perda: so ha essas cores).

Uso: python docs/lugares3d/estilo_ilha.py <portao|barraca|cais> <textura de entrada> <textura de saida>
As cores novas ficam na `paleta_ilha` do paleta.json de cada lugar. PROPOSTO, SEM FONTE."""
import json
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    lugar, entrada, saida = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    pal = json.loads((AQUI / lugar / "paleta.json").read_text(encoding="utf-8"))
    troca = {tuple(a): tuple(b) for a, b in zip(pal["paleta"], pal["paleta_ilha"], strict=True)}
    im = Image.open(entrada).convert("RGB")
    usadas = {c for _, c in im.getcolors(1 << 24)}
    fora = usadas - troca.keys()
    if fora:
        raise SystemExit(f"cores fora da paleta de {lugar}: {sorted(fora)}")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            px[x, y] = troca[px[x, y]]
    # poucas cores: o PNG de paleta e sem perda e mais leve; confere que voltou igual
    pal_im = im.convert("P", palette=Image.ADAPTIVE, colors=len(usadas))
    if list(pal_im.convert("RGB").getdata()) != list(im.getdata()):
        raise SystemExit(f"{lugar}: a paleta do PNG mudou alguma cor")
    pal_im.save(saida, optimize=True)
    print(f"{lugar}: {len(usadas)} cores trocadas -> {saida}")


if __name__ == "__main__":
    main()
