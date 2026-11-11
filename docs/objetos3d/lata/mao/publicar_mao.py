"""Publica a lata gigante feita a mao no jogo (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 17).

Roda o lata_mao.py numa pasta temporaria de saida, poe a procedencia no asset.extras (feito a mao por script, sem IA; o concept 1 da Meshy
so como referencia de desenho), troca os arquivos em web/app/public/enfeites/lata/ (o License.txt e reescrito a parte) e roda o
glTF-Validator pelo docs/itens3d/validar.cjs (docs/enfeites/lata/validacao.json, lido pelo web/app/test/ilha_enfeites.test.ts).

uso (da raiz): python -I docs/objetos3d/lata/mao/publicar_mao.py <pasta de saida> <pasta do gltf-validator>
  (a lib numa pasta fora do repo: npm install --prefix <pasta> gltf-validator@2.0.0-dev.3.10)
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.resolve().parents[3]
sys.path.insert(0, str(AQUI))
from lata_mao import main as gerar  # noqa: E402

PUB = RAIZ / "web" / "app" / "public" / "enfeites" / "lata"
ESBOCO = json.loads((RAIZ / "docs" / "mapa_digital" / "lata" / "concept" / "concept_1_cereja.json").read_text(encoding="utf-8"))


def main(saida: str, lib: str) -> None:
    gerar(saida)
    s = Path(saida)
    g = json.loads((s / "lata.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": False,
        "gerador": "feito a mao por script: docs/objetos3d/lata/mao/lata_mao.py (o corpo por revolucao, as faixas e as cerejas pintadas no codigo)",
        "referencia_de_desenho": {"esboco": "docs/mapa_digital/lata/concept/concept_1_cereja.png", "tarefa_meshy": ESBOCO["id"]},
        "licenca": "License.txt ao lado",
    }
    PUB.mkdir(parents=True, exist_ok=True)
    for a in PUB.glob("*"):   # so o que sobra: o Vite deixa de servir um arquivo apagado e recriado (D-OBJ-CARRO-12)
        if a.name not in ("License.txt", "lata.gltf", "lata.bin", "lata_cor.png"):
            a.unlink()
    (PUB / "lata.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for n in ("lata.bin", "lata_cor.png"):
        shutil.copyfile(s / n, PUB / n)
    total = sum(a.stat().st_size for a in PUB.glob("lata*"))
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(PUB.glob("*"))}, "total", total, "bytes")
    sai = RAIZ / "docs" / "enfeites" / "lata" / "validacao.json"
    sai.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", str(RAIZ / "docs" / "itens3d" / "validar.cjs"), str(PUB / "lata.gltf"), str(sai)], check=True,
                   env={**os.environ, "NODE_PATH": str(Path(lib) / "node_modules")})


if __name__ == "__main__":
    main(*sys.argv[1:3])
