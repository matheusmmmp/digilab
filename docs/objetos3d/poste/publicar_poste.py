"""Publica o poste retrabalhado no jogo (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 13). Adaptado do publicar_carro.py.

Pega a saida do acabar_poste.py (o glTF e o .bin) e do textura_poste.py (a cor e a mascara da luz), poe a marca de IA e as tarefas da Meshy
no asset.extras (os termos da Meshy, secao 2.4), troca os arquivos em web/app/public/enfeites/poste/ (o License.txt e reescrito a parte) e
roda o glTF-Validator pelo docs/itens3d/validar.cjs (docs/enfeites/poste/validacao.json, lido pelo web/app/test/ilha_enfeites.test.ts).

uso (da raiz): python -I docs/objetos3d/poste/publicar_poste.py <pasta com poste.gltf e poste.bin> <poste_cor.png> <poste_luz.png> <pasta do gltf-validator>
  (a lib numa pasta fora do repo: npm install --prefix <pasta> gltf-validator@2.0.0-dev.3.10)
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PUB = RAIZ / "web" / "app" / "public" / "enfeites" / "poste"
AQUI = Path(__file__).parent
SALDO = json.loads((AQUI / "saldo.json").read_text(encoding="utf-8"))
ESBOCO = json.loads((AQUI / "esbocos" / "esboco_1_ferro_hera.json").read_text(encoding="utf-8"))


def main(gl: str, cor: str, luz: str, lib: str) -> None:
    g = json.loads((Path(gl) / "poste.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": True,
        "gerador": "Meshy (meshy.ai), plano Pro, conta do Matheus",
        "tarefas_meshy": {"esboco": ESBOCO["id"], "vistas": SALDO["vistas"]["tarefa"], "malha": SALDO["malha"]["tarefa"]},
        "pipeline": ("docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 13; docs/objetos3d/REFERENCIAS.md, secao 5: a malha da Meshy com os vertices "
                     "repetidos soldados e as normais ponderadas (acabar_poste.py); a textura pintada da Meshy sem achatar, com os vidros no "
                     "amarelo quente do esboco, a hera pintada em espiral no poste e as abas soltas da hera em verde de folha, e 512 px em "
                     "paleta de 256 cores com difusao (textura_poste.py); poste_luz.png e a mascara dos vidros"),
        "licenca": "License.txt ao lado",
    }
    if [i["uri"] for i in g.get("images", [])] != ["poste_cor.png"]:
        raise SystemExit("o glTF devia usar so poste_cor.png: " + str(g.get("images")))
    for a in PUB.glob("*"):
        if a.name != "License.txt":
            a.unlink()
    (PUB / "poste.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(Path(gl) / "poste.bin", PUB / "poste.bin")
    shutil.copyfile(cor, PUB / "poste_cor.png")
    shutil.copyfile(luz, PUB / "poste_luz.png")
    total = sum(a.stat().st_size for a in PUB.glob("poste*"))
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(PUB.glob("*"))}, "total", total, "bytes")
    sai = RAIZ / "docs" / "enfeites" / "poste" / "validacao.json"
    subprocess.run(["node", str(RAIZ / "docs" / "itens3d" / "validar.cjs"), str(PUB / "poste.gltf"), str(sai)], check=True,
                   env={**os.environ, "NODE_PATH": str(Path(lib) / "node_modules")})


if __name__ == "__main__":
    main(*sys.argv[1:5])
