"""Publica o portao retrabalhado no jogo (docs/TAREFA_V3_LUGARES_3D.md, secao 14).

Pega a saida do acabar_portao.py (o glTF e o .bin) e do textura_portao.py (a cor e a mascara), poe a marca de IA e as tarefas da Meshy no
asset.extras (os termos da Meshy, secao 2.4), copia tudo para web/app/public/lugares/portao/ e roda o glTF-Validator (validar_gltf.cjs)
(docs/lugares3d/portao/validacao.json, lido pelo test/lugares3d.test.ts).

uso (da raiz): python -I docs/objetos3d/portao/publicar_portao.py <pasta com portao.gltf e portao.bin> <portao_cor.png> <portao_luz.png> <pasta com o gltf-validator instalado>
"""
import json, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PUB = RAIZ / "web" / "app" / "public" / "lugares" / "portao"
SALDO = json.loads((Path(__file__).parent / "saldo.json").read_text(encoding="utf-8"))


def main(gl: str, cor: str, luz: str, validador: str) -> None:
    g = json.loads((Path(gl) / "portao.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": True,
        "gerador": "Meshy (meshy.ai), plano Pro, conta do Matheus",
        "tarefas_meshy": SALDO["tarefas"],
        "pipeline": ("docs/TAREFA_V3_LUGARES_3D.md, secao 14; docs/objetos3d/REFERENCIAS.md, secao 5: a malha da Meshy 1,5 vez mais funda, "
                     "os vertices repetidos soldados, a folha do portal plana com ilha unica de UV e as normais ponderadas (acabar_portao.py); "
                     "a textura pintada da Meshy sem achatar, o portal da vista de frente da multivista, 512 px em paleta de 240 cores "
                     "(textura_portao.py); a mascara do portal ao lado "
                     "(portao_luz.png)"),
        "licenca": "License.txt ao lado",
    }
    if [i["uri"] for i in g.get("images", [])] != ["portao_cor.png"]:
        raise SystemExit("o glTF devia usar so portao_cor.png: " + str(g.get("images")))
    for a in PUB.glob("*"):
        if a.name != "License.txt":
            a.unlink()
    (PUB / "portao.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(Path(gl) / "portao.bin", PUB / "portao.bin")
    shutil.copyfile(cor, PUB / "portao_cor.png")
    shutil.copyfile(luz, PUB / "portao_luz.png")
    total = sum(a.stat().st_size for a in PUB.glob("portao*"))
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(PUB.glob("*"))}, "total", total, "bytes")
    sai = RAIZ / "docs" / "lugares3d" / "portao" / "validacao.json"
    subprocess.run(["node", str(Path(__file__).parent / "validar_gltf.cjs"), validador, str(PUB / "portao.gltf"), str(sai)], check=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])
