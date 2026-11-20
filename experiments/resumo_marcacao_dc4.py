"""O resumo descritivo do que o Matheus marcou na DC4 encerrada (CONVERSA_PET, DC4d; D-DC4D-2).

A DC4 foi encerrada pelo Matheus em 2026-11-10 com a legibilidade (4.2) e os pares (4.5) marcados, e sem a amostra da referencia (4.1) nem a
injecao (4.4). Este script so conta, por braco, o que foi marcado: o acerto da legibilidade, a fracao de "nao pede nada", a matriz pedido da
rede x resposta, e a escolha nos pares. **Nenhum gate:** nada aqui compara com o limiar do plano. O marcador Opus
(`respostas/opus_*.jsonl`) nao e lido.

`python experiments/resumo_marcacao_dc4.py --pasta artifacts_v3_conversa_dc4/validacao/marcacao` grava `resumo_marcacao.json` na pasta.
So biblioteca padrao.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import marcacao_dc4 as mc  # noqa: E402

BRACOS = ("G", "H", "S")


def resumir(pasta: Path) -> dict:
    itens = json.loads((pasta / "itens.json").read_text(encoding="utf-8"))
    chave = json.loads((pasta / "chave.json").read_text(encoding="utf-8"))
    out = {}

    leg = mc.respostas(pasta, "legibilidade")
    ids = {x["id"] for x in itens["legibilidade"]}
    if set(leg) != ids:
        raise SystemExit(f"legibilidade incompleta: {len(leg)} de {len(ids)}")
    por = {b: {"n": 0, "acertos": 0, "nada": 0, "matriz": {}} for b in BRACOS}
    for iid, r in leg.items():
        k = chave[iid]
        p = por[k["braco"]]
        p["n"] += 1
        p["acertos"] += r["resposta"] == k["certa"]
        p["nada"] += r["resposta"] == "nada"
        linha = p["matriz"].setdefault(k["certa"], {o: 0 for o in mc.OPCOES_LEGIBILIDADE})
        linha[r["resposta"]] += 1
    for p in por.values():
        p["acerto"] = p["acertos"] / p["n"]
        p["fracao_nada"] = p["nada"] / p["n"]
    out["legibilidade"] = por

    par = mc.respostas(pasta, "pares")
    ids = {x["id"] for x in itens["pares"]}
    if set(par) != ids:
        raise SystemExit(f"pares incompletos: {len(par)} de {len(ids)}")
    comp = {}
    for iid, r in par.items():
        k = chave[iid]
        c = comp.setdefault(k["comparacao"], {"n": 0, "escolhas": {}})
        c["n"] += 1
        braco = k[r["escolha"]]
        c["escolhas"][braco] = c["escolhas"].get(braco, 0) + 1
        c.setdefault("lado_esquerdo_escolhido", 0)
        c["lado_esquerdo_escolhido"] += r["escolha"] == "esquerda"
    out["pares"] = dict(sorted(comp.items()))

    out["nao_marcado"] = {t: f"{len(mc.respostas(pasta, t))} de {len(itens[t])}" for t in ("referencia", "injecao")}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pasta", type=Path, required=True)
    a = ap.parse_args(argv)
    res = resumir(a.pasta)
    mc._json(a.pasta / "resumo_marcacao.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
