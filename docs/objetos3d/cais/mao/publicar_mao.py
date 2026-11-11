"""Publica o cais feito a mao no jogo (docs/TAREFA_V3_LUGARES_3D.md, secao 18).

Roda o cais_mao.py numa pasta temporaria de saida, poe a procedencia no asset.extras (feito a mao por script, sem IA; o esboco 1 da Meshy
so como referencia de desenho), troca os arquivos em web/app/public/lugares/cais/ (o License.txt e reescrito a parte) e roda o
glTF-Validator pelo docs/itens3d/validar.cjs (docs/lugares3d/cais/validacao.json, lido pelo web/app/test/lugares3d.test.ts).

uso (da raiz): python -I docs/objetos3d/cais/mao/publicar_mao.py <pasta de saida> <pasta do gltf-validator>
  (a lib numa pasta fora do repo: npm install --prefix <pasta> gltf-validator@2.0.0-dev.3.10)
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.resolve().parents[3]
sys.path.insert(0, str(AQUI))
from cais_mao import main as gerar  # noqa: E402

PUB = RAIZ / "web" / "app" / "public" / "lugares" / "cais"
ESBOCO = json.loads((AQUI.parent / "esbocos" / "esboco_1_pier_barco.json").read_text(encoding="utf-8"))


def main(saida: str, lib: str) -> None:
    gerar(saida)
    s = Path(saida)
    g = json.loads((s / "cais.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": False,
        "gerador": "feito a mao por script: docs/objetos3d/cais/mao/cais_mao.py (as tabuas, as estacas e o barco por solidos simples, a pintura no codigo)",
        "referencia_de_desenho": {"esboco": "docs/objetos3d/cais/esbocos/esboco_1_pier_barco.png", "tarefa_meshy": ESBOCO["id"]},
        "licenca": "License.txt ao lado",
    }
    for a in PUB.glob("*"):   # so o que sobra: o Vite deixa de servir um arquivo apagado e recriado (D-OBJ-CARRO-12)
        if a.name not in ("License.txt", "cais.gltf", "cais.bin", "cais_cor.png"):
            a.unlink()
    (PUB / "cais.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for n in ("cais.bin", "cais_cor.png"):
        shutil.copyfile(s / n, PUB / n)
    total = sum(a.stat().st_size for a in PUB.glob("cais*"))
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(PUB.glob("*"))}, "total", total, "bytes")
    sai = RAIZ / "docs" / "lugares3d" / "cais" / "validacao.json"
    subprocess.run(["node", str(RAIZ / "docs" / "itens3d" / "validar.cjs"), str(PUB / "cais.gltf"), str(sai)], check=True,
                   env={**os.environ, "NODE_PATH": str(Path(lib) / "node_modules")})


if __name__ == "__main__":
    main(*sys.argv[1:3])
