"""A multivista e a malha de um item da ilha pela Meshy (docs/TAREFA_V3_ITENS_3D.md, secao 4.1, etapas 2 e 3).

  vistas: o Image to Image com generate_multi_view a partir da tarefa do concept escolhido; baixa as vistas (vista_1.png ...).
  malha:  o Multi-Image to 3D a partir da tarefa das vistas, com remesh em triangulos para o alvo, so a cor (sem PBR) e o GLB;
          baixa o GLB, a textura de cor e as miniaturas.
Cada etapa grava o JSON da tarefa e o saldo antes e depois. A chave vem da MESHY_API_KEY (gerar_concepts.chave) e nunca e impressa.

uso (da raiz):
  python -I docs/itens3d/gerar_malha.py vistas <pasta> <id da tarefa do concept> <prompt>
  python -I docs/itens3d/gerar_malha.py malha  <pasta> <id da tarefa das vistas> <alvo de poligonos>
"""
import json, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gerar_concepts import pedir  # noqa: E402


def esperar(caminho: str) -> dict:
    while True:
        t = pedir("GET", caminho)
        if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"):
            if t["status"] != "SUCCEEDED":
                raise SystemExit(f"{caminho}: {t['status']} {t.get('task_error')}")
            return t
        time.sleep(5)


def gravar(pasta: Path, nome: str, t: dict, antes: int) -> None:
    depois = pedir("GET", "/balance")["balance"]
    guardar = {k: t.get(k) for k in ("id", "type", "ai_model", "prompt", "status", "consumed_credits", "created_at", "finished_at")}
    guardar["saldo"] = {"antes": antes, "depois": depois}
    (pasta / f"{nome}.json").write_text(json.dumps(guardar, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(nome, "ok;", t.get("consumed_credits"), "creditos; saldo", antes, "->", depois)


def vistas(pasta: Path, concept: str, prompt: str) -> None:
    antes = pedir("GET", "/balance")["balance"]
    tid = pedir("POST", "/image-to-image", {"ai_model": "nano-banana-2", "prompt": prompt, "input_task_id": concept,
                                            "generate_multi_view": True, "remove_background": True})["result"]
    t = esperar(f"/image-to-image/{tid}")
    for i, u in enumerate(t["image_urls"], 1):
        urllib.request.urlretrieve(u, pasta / f"vista_{i}.png")
    gravar(pasta, "vistas", t, antes)


def malha(pasta: Path, vistas_id: str, alvo: int) -> None:
    antes = pedir("GET", "/balance")["balance"]
    corpo = {"input_task_id": vistas_id, "ai_model": "latest", "should_texture": True, "enable_pbr": False, "texture_resolution": "2k",
             "should_remesh": True, "topology": "triangle", "target_polycount": alvo, "save_pre_remeshed_model": False,
             "target_formats": ["glb"], "multi_view_thumbnails": True}
    (pasta / "malha_pedido.json").write_text(json.dumps(corpo, indent=1) + "\n", encoding="utf-8")
    tid = pedir("POST", "/multi-image-to-3d", corpo)["result"]
    (pasta / "malha_tarefa.txt").write_text(tid + "\n", encoding="utf-8")
    baixar(pasta, tid, antes)


def baixar(pasta: Path, tid: str, antes: int) -> None:
    """baixa o GLB, a textura de cor e as miniaturas (front, right, back, left) de uma tarefa pronta"""
    t = esperar(f"/multi-image-to-3d/{tid}")
    urllib.request.urlretrieve(t["model_urls"]["glb"], pasta / "meshy.glb")
    for k, u in (t.get("texture_urls") or [{}])[0].items():
        if u:
            urllib.request.urlretrieve(u, pasta / f"textura_{k}.png")
    mini = t.get("thumbnail_urls") or {}
    for k, u in (mini.items() if isinstance(mini, dict) else enumerate(mini, 1)):
        urllib.request.urlretrieve(u, pasta / f"miniatura_{k}.png")
    gravar(pasta, "malha", t, antes)


if __name__ == "__main__":
    etapa, p = sys.argv[1], Path(sys.argv[2])
    p.mkdir(parents=True, exist_ok=True)
    if etapa == "vistas":
        vistas(p, sys.argv[3], sys.argv[4])
    elif etapa == "malha":
        malha(p, sys.argv[3], int(sys.argv[4]))
    elif etapa == "baixar":  # uma tarefa da malha ja paga: <pasta> <id> <saldo antes>
        baixar(p, sys.argv[3], int(sys.argv[4]))
    else:
        raise SystemExit("etapa desconhecida: " + etapa)
