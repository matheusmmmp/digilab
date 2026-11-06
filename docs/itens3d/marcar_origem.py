"""A marca de origem no glTF de um item (docs/TAREFA_V3_ITENS_3D.md, G8 e secao 10: os termos da Meshy proibem tirar a marca de IA).

Da o nome final a imagem (<item>_cor.png), e escreve no asset.extras de onde o item veio: o gerador, as tarefas da Meshy (concept,
vistas, malha), que ele e gerado por IA e o que o pipeline fez depois. O asset.generator do exportador fica como esta.

uso (da raiz): python -I docs/itens3d/marcar_origem.py <item.gltf> <pasta do item em docs/itens3d> <nome do concept escolhido> [o que o pipeline fez]
"""
import json, sys
from pathlib import Path


BOLA = "a cor da malha da Meshy passada a uma esfera limpa e chapada na paleta do concept"


def main(gltf: str, docs: str, concept: str, feito: str = BOLA) -> None:
    g, d = Path(gltf), Path(docs)
    j = json.loads(g.read_text(encoding="utf-8"))
    item = g.stem
    if len(j.get("images", [])) != 1:
        raise SystemExit("o item deve ter uma imagem so: " + str(len(j.get("images", []))))
    velho = g.parent / j["images"][0]["uri"]
    novo = g.parent / f"{item}_cor.png"
    if velho != novo:
        velho.replace(novo)
    j["images"][0]["uri"] = novo.name
    j["images"][0]["name"] = novo.stem
    tarefa = lambda p: json.loads((d / p).read_text(encoding="utf-8"))["id"]
    j["asset"]["extras"] = {
        "gerado_por_ia": True,
        "gerador": "Meshy (meshy.ai), plano Pro, conta do Matheus",
        "tarefas_meshy": {"concept": tarefa(f"concept/{concept}.json"), "vistas": tarefa("vistas/vistas.json"),
                          "malha": tarefa("malha/malha.json")},
        "pipeline": "docs/TAREFA_V3_ITENS_3D.md; " + feito,
        "licenca": "License.txt ao lado",
    }
    g.write_text(json.dumps(j, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ORIGEM", g, "->", novo.name)


if __name__ == "__main__":
    main(*sys.argv[1:5])
