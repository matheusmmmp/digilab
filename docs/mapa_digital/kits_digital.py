"""Os kits da ilha no estilo Digital (docs/TAREFA_V3_MAPA_DIGITAL.md, etapa D2): uma copia das texturas dos kits CC0 de
web/app/public/kits3d/, recoloridas em poucos tons chapados e mais saturados (o fundo de anime da maquete B), em
web/app/public/kits3d_digital/, e uma copia de cada glTF que aponta para a textura nova e para o .bin de sempre (../../kits3d/<kit>/),
para nao duplicar a geometria. A ilha (o estilo de hoje) nao muda: ela segue lendo public/kits3d/.

A recoloracao de cada textura: o RGB e reduzido a TONS cores pela mediana (sem pontilhado), um filtro de moda limpa os pontinhos, e a
saturacao sobe SATURACAO vezes e o brilho BRILHO vezes; o canal alfa (as folhas sao cartoes recortados) fica como estava. Os numeros sao PROPOSTOS, SEM FONTE.

Os tracos de nanquim (tracar_linhas.py) nao entram aqui: as texturas dos kits sao divididas entre varios modelos (a casca e as folhas de
todas as arvores) e as folhas sao cartoes transparentes; um traco desenhado pelas arestas de um modelo sujaria os outros.

uso (da raiz): python -I docs/mapa_digital/kits_digital.py
"""
import json, shutil
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

ORIGEM, DESTINO = Path("web/app/public/kits3d"), Path("web/app/public/kits3d_digital")
TONS = {"Flowers.png": 6, "Mushrooms.png": 6, "forest_texture.png": 8}   # as texturas de atlas tem mais cores; o resto, TONS_PADRAO
TONS_PADRAO, SATURACAO, BRILHO, MODA = 4, 1.35, 1.08, 5
# os pinheiros mais claros (o revisor achou os de tras escuros e pesados contra o ceu)
BRILHO_TEXTURA = {"Leaf_Pine_C.png": 1.3}


def recolorir(ent: Path, sai: Path) -> None:
    im = Image.open(ent).convert("RGBA")
    alfa = im.getchannel("A")
    q = im.convert("RGB").quantize(TONS.get(ent.name, TONS_PADRAO), method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    rgb = q.filter(ImageFilter.ModeFilter(MODA)).convert("RGB")
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(rgb).enhance(SATURACAO)).enhance(BRILHO_TEXTURA.get(ent.name, BRILHO))
    rgb.putalpha(alfa)
    rgb.save(sai, optimize=True)
    print("KIT", ent.name, ent.stat().st_size, "->", sai.stat().st_size, "bytes")


def main() -> None:
    for kit in sorted(p for p in ORIGEM.iterdir() if p.is_dir()):
        dest = DESTINO / kit.name
        dest.mkdir(parents=True, exist_ok=True)
        for lic in kit.glob("License*.txt"):
            shutil.copy(lic, dest / lic.name)
        for png in sorted(kit.glob("*.png")):
            recolorir(png, dest / png.name)
        for g in sorted(kit.glob("*.gltf")):
            j = json.loads(g.read_text(encoding="utf-8"))
            for b in j["buffers"]:
                b["uri"] = f"../../kits3d/{kit.name}/{b['uri']}"
            (dest / g.name).write_text(json.dumps(j, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
