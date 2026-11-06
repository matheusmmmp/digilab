"""Os concepts 2D de um item da ilha pela Meshy (docs/TAREFA_V3_ITENS_3D.md, secao 4.1, etapa 1).

Manda as referencias de estilo recortadas da propria ilha (sem o pet) e um prompt por variante ao Image to Image da Meshy, espera cada
tarefa, baixa a imagem e grava, ao lado, o JSON da tarefa (o prompt, o modelo, os creditos gastos) e o saldo antes e depois.
A chave vem da variavel MESHY_API_KEY (do processo ou, no Windows, das variaveis do usuario); nunca e impressa.

uso (da raiz): python -I docs/itens3d/gerar_concepts.py docs/itens3d/bola/concept/prompts.json
"""
import base64, json, os, sys, time, urllib.request
from pathlib import Path

API = "https://api.meshy.ai/openapi/v1"


def chave() -> str:
    k = os.environ.get("MESHY_API_KEY")
    if not k and sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as r:
            k = winreg.QueryValueEx(r, "MESHY_API_KEY")[0]
    if not k:
        raise SystemExit("MESHY_API_KEY ausente")
    return k


def pedir(metodo: str, caminho: str, corpo: dict | None = None) -> dict:
    req = urllib.request.Request(API + caminho, method=metodo, data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Authorization": "Bearer " + chave(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def main(arq: str) -> None:
    cfg = json.loads(Path(arq).read_text(encoding="utf-8"))
    pasta = Path(arq).parent
    refs = [data_uri(pasta / r) for r in cfg["referencias"]]
    saldo_antes = pedir("GET", "/balance")["balance"]
    print("saldo antes", saldo_antes)
    gasto = 0
    for v in cfg["variantes"]:
        corpo = {"ai_model": cfg["ai_model"], "prompt": cfg["prompt_base"] + " " + v["prompt"], "reference_image_urls": refs,
                 "aspect_ratio": "1:1"}
        tid = pedir("POST", "/image-to-image", corpo)["result"]
        while True:
            t = pedir("GET", f"/image-to-image/{tid}")
            if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"):
                break
            time.sleep(4)
        if t["status"] != "SUCCEEDED":
            raise SystemExit(f"{v['nome']}: {t['status']} {t.get('task_error')}")
        urllib.request.urlretrieve(t["image_urls"][0], pasta / f"{v['nome']}.png")
        gasto += t.get("consumed_credits") or 0
        (pasta / f"{v['nome']}.json").write_text(json.dumps({k: t.get(k) for k in ("id", "ai_model", "prompt", "status", "consumed_credits",
                                                            "created_at", "finished_at")}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(v["nome"], "ok", t.get("consumed_credits"), "creditos")
    saldo_depois = pedir("GET", "/balance")["balance"]
    (pasta / "saldo.json").write_text(json.dumps({"antes": saldo_antes, "depois": saldo_depois, "gasto_tarefas": gasto}, indent=1) + "\n")
    print("saldo depois", saldo_depois, "gasto", saldo_antes - saldo_depois)


if __name__ == "__main__":
    main(sys.argv[1])
