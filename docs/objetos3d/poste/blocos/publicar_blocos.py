"""Publica o poste em blocos no jogo (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 14).

Roda o poste_blocos.py numa pasta temporaria de saida, poe a procedencia no asset.extras (feito a mao por script, sem IA; o esboco 1 da
Meshy so como referencia de desenho), troca os arquivos em web/app/public/enfeites/poste/ (o License.txt e reescrito a parte) e roda o
glTF-Validator pelo docs/itens3d/validar.cjs (docs/enfeites/poste/validacao.json, lido pelo web/app/test/ilha_enfeites.test.ts).

uso (da raiz): python -I docs/objetos3d/poste/blocos/publicar_blocos.py <pasta de saida> <pasta do gltf-validator> [quente|digital]
  (a lib numa pasta fora do repo: npm install --prefix <pasta> gltf-validator@2.0.0-dev.3.10)
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.resolve().parents[3]
sys.path.insert(0, str(AQUI))
from poste_blocos import main as gerar  # noqa: E402

PUB = RAIZ / "web" / "app" / "public" / "enfeites" / "poste"
ESBOCO = json.loads((AQUI.parent / "esbocos" / "esboco_1_ferro_hera.json").read_text(encoding="utf-8"))


def main(saida: str, lib: str, vidro: str = "quente") -> None:
    gerar(saida, vidro)
    s = Path(saida)
    g = json.loads((s / "poste.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": False,
        "gerador": "feito a mao por script: docs/objetos3d/poste/blocos/poste_blocos.py (as caixas e a pintura em pixel art no codigo)",
        "referencia_de_desenho": {"esboco": "docs/objetos3d/poste/esbocos/esboco_1_ferro_hera.png", "tarefa_meshy": ESBOCO["id"]},
        "vidro": vidro,
        "licenca": "License.txt ao lado",
    }
    for a in PUB.glob("*"):
        if a.name != "License.txt":
            a.unlink()
    (PUB / "poste.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for n in ("poste.bin", "poste_cor.png", "poste_luz.png"):
        shutil.copyfile(s / n, PUB / n)
    total = sum(a.stat().st_size for a in PUB.glob("poste*"))
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(PUB.glob("*"))}, "total", total, "bytes")
    sai = RAIZ / "docs" / "enfeites" / "poste" / "validacao.json"
    subprocess.run(["node", str(RAIZ / "docs" / "itens3d" / "validar.cjs"), str(PUB / "poste.gltf"), str(sai)], check=True,
                   env={**os.environ, "NODE_PATH": str(Path(lib) / "node_modules")})


if __name__ == "__main__":
    main(*sys.argv[1:4])
