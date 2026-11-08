"""Publica o cais retrabalhado no jogo (docs/TAREFA_V3_LUGARES_3D.md, secao 16).

Pega a saida do acabar_cais.py (o glTF e o .bin) e do textura_cais.py (a cor), poe a marca de IA e as tarefas da Meshy no asset.extras (os
termos da Meshy, secao 2.4), troca os arquivos de web/app/public/lugares/cais/ (a mascara cais_luz.png sai: o barco do esboco 1 nao tem
parte que acende) e roda o glTF-Validator (docs/itens3d/validar.cjs) para docs/lugares3d/cais/validacao.json, lido pelo
test/lugares3d.test.ts.

uso (da raiz): python -I docs/objetos3d/cais/publicar_cais.py <pasta com cais.gltf e cais.bin> <cais_cor.png> <pasta node_modules com o gltf-validator>
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).parent
PUB = RAIZ / "web" / "app" / "public" / "lugares" / "cais"


def main(gl: str, cor: str, node_modules: str) -> None:
    tarefas = {
        "esboco": json.loads((AQUI / "esbocos" / "esboco_1_pier_barco.json").read_text(encoding="utf-8"))["id"],
        "vistas": json.loads((AQUI / "vistas" / "vistas.json").read_text(encoding="utf-8"))["id"],
        "malha": json.loads((AQUI / "malha" / "malha.json").read_text(encoding="utf-8"))["id"],
    }
    g = json.loads((Path(gl) / "cais.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": True,
        "gerador": "Meshy (meshy.ai), plano Pro, conta do Matheus",
        "tarefas_meshy": tarefas,
        "pipeline": ("docs/TAREFA_V3_LUGARES_3D.md, secao 16; docs/objetos3d/REFERENCIAS.md, secao 5: a malha da Meshy como veio, os vertices "
                     "repetidos soldados e as normais ponderadas (acabar_cais.py); a textura pintada da Meshy sem achatar, um realce leve do "
                     "azul, do amarelo e do musgo, 512 px em paleta de 192 cores com pontilhado (textura_cais.py)"),
        "licenca": "License.txt ao lado",
    }
    if [i["uri"] for i in g.get("images", [])] != ["cais_cor.png"]:
        raise SystemExit("o glTF devia usar so cais_cor.png: " + str(g.get("images")))
    for a in PUB.glob("*"):
        if a.name != "License.txt":
            a.unlink()
    (PUB / "cais.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(Path(gl) / "cais.bin", PUB / "cais.bin")
    shutil.copyfile(cor, PUB / "cais_cor.png")
    total = sum(a.stat().st_size for a in PUB.glob("cais*"))
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(PUB.glob("*"))}, "total", total, "bytes")
    sai = RAIZ / "docs" / "lugares3d" / "cais" / "validacao.json"
    subprocess.run(["node", str(RAIZ / "docs" / "itens3d" / "validar.cjs"), str(PUB / "cais.gltf"), str(sai)], check=True,
                   env={**os.environ, "NODE_PATH": node_modules})


if __name__ == "__main__":
    main(*sys.argv[1:4])
