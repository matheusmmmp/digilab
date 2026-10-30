"""Copia os modelos dos kits 3D CC0 que a ilha usa para web/app/public/kits3d/ (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H1; decisao H-1).

Os kits ficam fora do git em D:/Trab/digilab/Assets/kits3d/ (secao 3.2 da tarefa). Este script copia so os modelos da lista MODELOS
(o mesmo conjunto de src/telas/pet/ilha/modelos.ts; o teste test/ilha_modelos.test.ts confere os dois), com a licenca de cada kit
ao lado, e:
  - tira dos materiais as texturas que o material toon da ilha nao usa (normal, oclusao, metalico/rugosidade), e com elas as imagens
    que ficam sem uso;
  - reduz as texturas com lado maior que LADO_MAX (o filtro e o de area; os modelos sao vistos de longe);
  - falha se o total passar de ORCAMENTO_BYTES (8 MB, a H-1).
Uso, de web/app/:  python scripts/kits3d_copiar.py [--kits D:/Trab/digilab/Assets/kits3d]
O Kenney (H-6) nao entra. Os numeros (LADO_MAX) sao do desenho: PROPOSTO, SEM FONTE. """
import argparse
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

APP = Path(__file__).resolve().parent.parent
DESTINO = APP / "public" / "kits3d"
ORCAMENTO_BYTES = 8 * 1024 * 1024
LADO_MAX = 1024

# o kit: a pasta dos .gltf dentro de Assets/kits3d e a licenca, e os modelos usados (sem a extensao)
KITS = {
    "quaternius": {
        "pasta": "quaternius_nature/x/glTF",
        "licenca": "quaternius_nature/x/License_Standard.txt",
        "modelos": [
            "CommonTree_1", "CommonTree_2", "CommonTree_3", "CommonTree_4", "CommonTree_5",
            "Pine_1", "Pine_2", "Pine_3", "Pine_5",
            "Bush_Common", "Bush_Common_Flowers",
            "Flower_3_Group", "Flower_4_Group", "Flower_3_Single", "Flower_4_Single",
            "Clover_1", "Clover_2",
            "Grass_Common_Short", "Grass_Wispy_Short", "Grass_Common_Tall",
            "Fern_1", "Mushroom_Common", "Mushroom_Laetiporus",
        ],
    },
    "kaykit": {
        "pasta": "kaykit_forest/x/KayKit_Forest_Nature_Pack_1.0_FREE/Assets/gltf",
        "licenca": "kaykit_forest/x/KayKit_Forest_Nature_Pack_1.0_FREE/License.txt",
        "modelos": ["Bush_1_A_Color1", "Bush_2_A_Color1", "Rock_1_A_Color1", "Rock_2_A_Color1", "Rock_3_A_Color1"],
    },
}
# as texturas que o material toon (ilha/cena.ts) nao le
SEM_USO = ("normalTexture", "occlusionTexture", "metallicRoughnessTexture", "emissiveTexture")


def limpar_gltf(g: dict) -> dict:
    """tira as texturas sem uso dos materiais e refaz as listas de texturas e imagens so com as usadas (os indices sao remapeados)"""
    for m in g.get("materials", []):
        for k in SEM_USO:
            m.pop(k, None)
        pbr = m.get("pbrMetallicRoughness", {})
        pbr.pop("metallicRoughnessTexture", None)
    usadas = sorted({m["pbrMetallicRoughness"]["baseColorTexture"]["index"] for m in g.get("materials", [])
                     if "baseColorTexture" in m.get("pbrMetallicRoughness", {})})
    nova_tex = {v: i for i, v in enumerate(usadas)}
    texturas = [g["textures"][i] for i in usadas]
    imgs = sorted({t["source"] for t in texturas})
    nova_img = {v: i for i, v in enumerate(imgs)}
    for t in texturas:
        t["source"] = nova_img[t["source"]]
    for m in g.get("materials", []):
        b = m.get("pbrMetallicRoughness", {}).get("baseColorTexture")
        if b is not None:
            b["index"] = nova_tex[b["index"]]
    g["textures"] = texturas
    g["images"] = [g["images"][i] for i in imgs]
    if not g["textures"]:
        g.pop("textures"); g.pop("images")
    return g


def copiar_imagem(origem: Path, destino: Path) -> None:
    im = Image.open(origem)
    lado = max(im.size)
    if lado > LADO_MAX:
        f = LADO_MAX / lado
        im = im.resize((round(im.size[0] * f), round(im.size[1] * f)), Image.Resampling.BOX)
    im.save(destino, optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kits", default=str(APP.parent.parent.parent / "Assets" / "kits3d"))
    kits = Path(ap.parse_args().kits)
    if not kits.is_dir():
        raise SystemExit(f"os kits nao estao em {kits}")
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    for nome, kit in KITS.items():
        pasta, saida = kits / kit["pasta"], DESTINO / nome
        saida.mkdir(parents=True)
        shutil.copyfile(kits / kit["licenca"], saida / Path(kit["licenca"]).name)
        imagens: set[str] = set()
        for mod in kit["modelos"]:
            g = limpar_gltf(json.loads((pasta / f"{mod}.gltf").read_text(encoding="utf-8")))
            for b in g["buffers"]:
                if b["uri"].startswith("data:"):
                    raise SystemExit(f"{mod}: buffer embutido; a lista espera o .bin ao lado")
                shutil.copyfile(pasta / b["uri"], saida / b["uri"])
            imagens.update(i["uri"] for i in g.get("images", []))
            (saida / f"{mod}.gltf").write_text(json.dumps(g, separators=(",", ":")), encoding="utf-8")
        for uri in sorted(imagens):
            copiar_imagem(pasta / uri, saida / uri)
    total = sum(p.stat().st_size for p in DESTINO.rglob("*") if p.is_file())
    print(f"kits3d: {sum(len(k['modelos']) for k in KITS.values())} modelos, {total / 1048576:.2f} MB em {DESTINO}")
    if total > ORCAMENTO_BYTES:
        print(f"passou do orcamento de {ORCAMENTO_BYTES / 1048576:.0f} MB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
