"""Publica o carro retrabalhado no jogo (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12). Adaptado do publicar_portao.py.

Pega a saida do acabar_carro.py (o glTF e o .bin) e do estilizar_carro.py seguido do textura_carro.py (a cor), poe a marca de IA e as tarefas da Meshy no asset.extras
(os termos da Meshy, secao 2.4), troca os arquivos em web/app/public/enfeites/carro/ (o License.txt fica, reescrito a parte) e roda o
glTF-Validator pelo docs/itens3d/validar.cjs (docs/enfeites/carro/validacao.json, lido pelo web/app/test/ilha_enfeites.test.ts).

uso (da raiz): python -I docs/objetos3d/carro/publicar_carro.py <pasta com carro.gltf e carro.bin> <carro_cor.png> <pasta do gltf-validator>
  (a lib numa pasta fora do repo: npm install --prefix <pasta> gltf-validator@2.0.0-dev.3.10)
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PUB = RAIZ / "web" / "app" / "public" / "enfeites" / "carro"
AQUI = Path(__file__).parent
SALDO = json.loads((AQUI / "saldo.json").read_text(encoding="utf-8"))
ESBOCO = json.loads((AQUI / "esbocos" / "esboco_1_hatch_retro.json").read_text(encoding="utf-8"))


def main(gl: str, cor: str, lib: str) -> None:
    g = json.loads((Path(gl) / "carro.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": True,
        "gerador": "Meshy (meshy.ai), plano Pro, conta do Matheus",
        "tarefas_meshy": {"esboco": ESBOCO["id"], "vistas": SALDO["vistas"]["tarefa"], "malha": SALDO["malha"]["tarefa"]},
        "pipeline": ("docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12; docs/objetos3d/REFERENCIAS.md, secao 5: a malha da Meshy girada com a "
                     "frente em +z, os vertices repetidos soldados e as normais ponderadas (acabar_carro.py); a textura da Meshy redesenhada em "
                     "cartoon limpo por regiao (estilizar_carro.py: mean shift, classes pelo matiz com a paleta fixa, o vidro chapado na "
                     "mascara das janelas, a oclusao assada do oclusao_carro.py e as flores rosa do teto; rodada 3, secao 13) e 512 px em "
                     "paleta de 256 cores com difusao (textura_carro.py)"),
        "licenca": "License.txt ao lado",
    }
    if [i["uri"] for i in g.get("images", [])] != ["carro_cor.png"]:
        raise SystemExit("o glTF devia usar so carro_cor.png: " + str(g.get("images")))
    for a in PUB.glob("*"):
        if a.name != "License.txt":
            a.unlink()
    (PUB / "carro.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(Path(gl) / "carro.bin", PUB / "carro.bin")
    shutil.copyfile(cor, PUB / "carro_cor.png")
    total = sum(a.stat().st_size for a in PUB.glob("carro*"))
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(PUB.glob("*"))}, "total", total, "bytes")
    sai = RAIZ / "docs" / "enfeites" / "carro" / "validacao.json"
    subprocess.run(["node", str(RAIZ / "docs" / "itens3d" / "validar.cjs"), str(PUB / "carro.gltf"), str(sai)], check=True,
                   env={**os.environ, "NODE_PATH": str(Path(lib) / "node_modules")})


if __name__ == "__main__":
    main(*sys.argv[1:4])
