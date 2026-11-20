"""Publica a barraca refeita no jogo (web/app/public/lugares/barraca/): reduz a textura pintada (textura_barraca.py, 1024 px) ao lado e
as cores que cabem no orcamento de 300 KB dos lugares (web/app/test/lugares3d.test.ts), roda o acabamento do Blender (acabar_barraca.py)
e grava a marca de IA e as tarefas da Meshy no asset.extras do glTF.

  A textura: 512 px, PNG de paleta com 256 cores e pontilhado (Floyd-Steinberg). Nao e o achatamento antigo (3 a 12 cores lisas, uma por
  face): o pontilhado guarda o degrade e as pinceladas. Em 1024 px RGB ela teria ~1,3 MB; em 1024 px com 256 cores, ~345 KB, sozinha
  acima do orcamento (o desvio no docs/registro/2026-11.md).

A ordem completa (da raiz), a partir da malha da Meshy em malha/:
  blender -b --python docs/objetos3d/barraca/faces.py -- docs/objetos3d/barraca/malha/meshy.glb docs/objetos3d/barraca/retrabalho/faces.json
  blender -b --python docs/objetos3d/barraca/interior.py -- docs/objetos3d/barraca/malha/meshy.glb docs/objetos3d/barraca/retrabalho/interior.json
  python -I docs/objetos3d/barraca/publicar_barraca.py <blender.exe>
e depois o validador (docs/itens3d/validar.cjs) para docs/lugares3d/barraca/validacao.json.
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
TRAB = AQUI / "retrabalho"
PUB = RAIZ / "web" / "app" / "public" / "lugares" / "barraca"
LADO, CORES = 512, 256


def main(blender: str) -> None:
    malha = AQUI / "malha"
    # 1. a textura pintada (o escuro de dentro e o chao), 1024 px
    subprocess.run([sys.executable, "-I", str(AQUI / "textura_barraca.py"), str(malha / "textura_base_color.png"), str(TRAB / "faces.json"),
                    str(TRAB / "interior.json"), str(TRAB / "cor_1024.png"), str(TRAB / "chao_uv.json")], check=True)
    # 2. a reducao para o orcamento
    cor = TRAB / "barraca_cor.png"
    Image.open(TRAB / "cor_1024.png").convert("RGB").resize((LADO, LADO), Image.LANCZOS).quantize(
        colors=CORES, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG).save(cor, optimize=True)
    # 3. o acabamento no Blender, exportado direto na pasta publica
    for velho in PUB.glob("barraca*"):
        velho.unlink()
    subprocess.run([blender, "--background", "--factory-startup", "--python", str(AQUI / "acabar_barraca.py"), "--",
                    str(malha / "meshy.glb"), str(cor), str(TRAB / "chao_uv.json"), str(PUB / "barraca.gltf"), "60"], check=True)
    (PUB / "barraca_cor.png").write_bytes(cor.read_bytes())  # a textura reduzida como saiu daqui, sem nova codificacao do Blender
    # 4. a marca de IA e as tarefas da Meshy
    g = json.loads((PUB / "barraca.gltf").read_text(encoding="utf-8"))
    tarefa = lambda p: json.loads((AQUI / p).read_text(encoding="utf-8"))["id"]
    g["asset"]["extras"] = {
        "gerado_por_ia": True, "gerador": "Meshy (meshy.ai), plano Pro, conta do Matheus",
        "tarefas_meshy": {"esboco": tarefa("esbocos/esboco_1_domo_costuras.json"), "vistas": tarefa("vistas/vistas.json"),
                          "malha": tarefa("malha/malha.json")},
        "pipeline": "docs/objetos3d/REFERENCIAS.md (secao 5) e docs/TAREFA_V3_LUGARES_3D.md (secao 14): a malha e a textura pintada "
                    "da Meshy como vieram, sem achatar; o escuro de dentro pintado nas faces vistas pela porta, as cordas tingidas de "
                    "laranja, um chao (2 triangulos) e um forro escuro (8) por dentro (textura_barraca.py, acabar_barraca.py); normais "
                    "suavizadas a 60 graus; textura em 512 px com 256 cores",
        "licenca": "License.txt ao lado"}
    (PUB / "barraca.gltf").write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    nomes = [im["uri"] for im in g.get("images", [])]
    if nomes != ["barraca_cor.png"] or [b["uri"] for b in g["buffers"]] != ["barraca.bin"]:
        raise SystemExit(f"arquivos inesperados no glTF: {nomes} {g['buffers']}")
    print("publicado", sorted(p.name for p in PUB.iterdir()), sum(p.stat().st_size for p in PUB.iterdir() if p.name != "License.txt"), "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
