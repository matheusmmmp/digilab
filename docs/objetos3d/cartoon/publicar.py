"""Publica no jogo um objeto em cartoon feito a mao por script (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 18, e
docs/TAREFA_V3_LUGARES_3D.md, secao 19): o poste, o trilho, a barraca ou o portao.

Roda o script do objeto numa pasta de saida, poe a procedencia no asset.extras (feito a mao por script, sem IA), troca os arquivos na
pasta publica (o glTF, o .bin, a textura e, se houver, a mascara de luz), reescreve o License.txt e roda o glTF-Validator pelo
docs/itens3d/validar.cjs (o validacao.json que os testes leem).

uso (da raiz): python -I docs/objetos3d/cartoon/publicar.py <nome> <pasta de saida> <pasta do gltf-validator>
  (a lib numa pasta fora do repo: npm install --prefix <pasta> gltf-validator@2.0.0-dev.3.10)
"""
import importlib, json, os, shutil, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.resolve().parents[2]
sys.path.insert(0, str(AQUI))

# o nome -> a pasta publica, a pasta da validacao, o que e, as pecas, a referencia de desenho e o que saiu
OBJETOS = {
    "poste": ("enfeites", "docs/enfeites", "o poste de luz da praca e do caminho do cais", "o pe, a coluna, a lanterna, o chapeu, a hera, o musgo",
              None, "O poste de antes (os blocos, feito por script em 2026-11-08) saiu do jogo; o historico esta em docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 14."),
    "trilho": ("enfeites", "docs/enfeites", "o trilho com o vagao, um marco da ilha", "os dormentes, os trilhos, as rodas, o chassi, a caixa, as escotilhas, o teto de lona",
               "docs/objetos3d/trem/esbocos/esboco_1_vagao_madeira.png",
               "O vagao de antes (a malha e a textura da Meshy) saiu do jogo; o historico esta em docs/TAREFA_V3_MUNDO_ENFEITES.md e em docs/objetos3d/trem/."),
    "barraca": ("lugares", "docs/lugares3d", "a barraca do Tamer, o lugar do Diario", "o domo, o rolo da porta, a antena, os estais, as estacas, o banquinho, os livros",
                "docs/objetos3d/barraca/esbocos/esboco_1_domo_costuras.png",
                "A barraca de antes (a malha e a textura da Meshy) saiu do jogo; o historico esta em docs/TAREFA_V3_LUGARES_3D.md e em docs/objetos3d/barraca/."),
    "portao": ("lugares", "docs/lugares3d", "o portao da arena, o lugar do Lutar", "os pilares, as pedras do arco, o portal, as flamulas, o musgo",
               "docs/objetos3d/portao/esbocos/esboco_1_pedra_blocos.png",
               "O portao de antes (a malha e a textura da Meshy) saiu do jogo; o historico esta em docs/TAREFA_V3_LUGARES_3D.md e em docs/objetos3d/portao/."),
}


def main(nome: str, saida: str, lib: str) -> None:
    pasta, docs, oque, partes, esboco, antes = OBJETOS[nome]
    importlib.import_module(nome).main(saida)
    s, pub = Path(saida), RAIZ / "web" / "app" / "public" / pasta / nome
    g = json.loads((s / f"{nome}.gltf").read_text(encoding="utf-8"))
    g["asset"]["extras"] = {
        "gerado_por_ia": False,
        "gerador": f"feito a mao por script: docs/objetos3d/cartoon/{nome}.py (solidos simples, a pintura no codigo)",
        "licenca": "License.txt ao lado",
    }
    if esboco:
        g["asset"]["extras"]["referencia_de_desenho"] = {"esboco": esboco}
    nomes = [f"{nome}.gltf", f"{nome}.bin", f"{nome}_cor.png"] + ([f"{nome}_luz.png"] if (s / f"{nome}_luz.png").exists() else [])
    for a in pub.glob("*"):   # so o que sobra: o Vite deixa de servir um arquivo apagado e recriado (D-OBJ-CARRO-12)
        if a.name not in ("License.txt", *nomes):
            a.unlink()
    (pub / f"{nome}.gltf").write_text(json.dumps(g, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for n in nomes[1:]:
        shutil.copyfile(s / n, pub / n)
    ref = (f"O desenho segue o esboco do objeto ({esboco}), gerado pela Meshy para o DigiLab e usado so como referencia de desenho:\n"
           "nenhum pixel e nenhum vertice dele esta nestes arquivos. " if esboco else "")
    (pub / "License.txt").write_text(
        f"DigiLab: {oque} ({', '.join(nomes)})\n\n"
        f"Procedencia: feito a mao por script, sem IA, em 2026-11-10 (docs/objetos3d/cartoon/{nome}.py no repositorio do DigiLab).\n"
        f"A malha ({partes}) e a textura (pintada pelo codigo, pela posicao no espaco)\n"
        "saem do script; a mesma entrada da sempre o mesmo arquivo. Nada vem de modelo gerado nem de imagem de terceiros.\n\n"
        f"{ref}{antes}\n\n"
        "Uso: no jogo DigiLab, publicado. Autor: o projeto DigiLab (Matheus).\n"
        "Aprovacao: as capturas ficam no PR dos objetos em cartoon.\n", encoding="utf-8", newline="\n")
    print("PUBLICAR", {a.name: a.stat().st_size for a in sorted(pub.glob("*"))}, "total", sum(a.stat().st_size for a in pub.glob(f"{nome}*")), "bytes")
    sai = RAIZ / docs / nome / "validacao.json"
    subprocess.run(["node", str(RAIZ / "docs" / "itens3d" / "validar.cjs"), str(pub / f"{nome}.gltf"), str(sai)], check=True,
                   env={**os.environ, "NODE_PATH": str(Path(lib) / "node_modules")})


if __name__ == "__main__":
    main(*sys.argv[1:4])
