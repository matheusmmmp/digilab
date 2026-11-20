"""O relato do piloto do DigiBrain modular (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secoes 6.2 e 6.3; o adendo 2): le
os artefatos do piloto (medidas.json, resultado.json, meta.json) e junta, so lendo, o que o adendo 2 guarda:
  - o tamanho de efeito de cada contraste da secao 5.2, com o IC95 percentil (o G-MVP pela mesma funcao do orquestrador; o G-ABLA e o
    G-MOD do resultado.json). Sem leitura de gate: os numeros do piloto nao sao evidencia, e o "passa" e o "rejeita" ficam fora;
  - as premissas G-PESA (a fracao das decisoes, dias 8 a 14, com `<modulo>_decidiu`) e G-ELEGIVEL (as vidas com 3 racoes elegiveis ou
    mais) por braco e por celula;
  - a media do g_apr das vidas M4 (o valor do M4-con), o K pelo poder e o custo, como o orquestrador gravou.
Nenhuma vida roda. Grava relato.json na pasta do piloto.

    python experiments/relato_piloto_digibrain.py artifacts_v2_digibrain_prototipo/piloto
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

FORA = ("passa", "holm")                    # a leitura de gate fica fora do relato do piloto


def _sem_gate(c: dict) -> dict:
    return {k: v for k, v in c.items() if k not in FORA}


def _celula(dono: str, lugar: str) -> str:
    return f"{dono}/{lugar}"


def relatar(pasta: Path) -> dict:
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    if meta["fase"] != "piloto":
        raise ValueError("o relato e so do piloto")
    cfg = meta["config"]
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    registros = list(json.loads((pasta / "medidas.json").read_text(encoding="utf-8")).values())
    bracos = tuple(meta["bracos"])
    esperadas = len(meta["unidades"]) * len(orq.CELULAS) * len(bracos)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas no medidas.json, {esperadas} esperadas")
    boot = cfg["bootstrap"]
    mvp = orq.g_mvp(registros, boot, cfg["g_mvp"])
    contrastes = {"G-MVP": _sem_gate(mvp)}
    for fam in ("G-ABLA", "G-MOD"):
        for nome, c in res["contrastes_so_relato"][fam].items():
            contrastes[nome] = _sem_gate(c)
    premissa_de = {(b, m) for m, b in cfg["g_pesa"]["bracos"].items()}
    pesa = {}
    for b in bracos:
        vs = [r for r in registros if r["braco"] == b]
        pesa[b] = {}
        for mod in orq.MODULOS_SONDA:
            agg = orq.contraste(orq.por_unidade(registros, b, None, lambda x, mod=mod: x["influencia"][mod]), boot)
            pesa[b][mod] = {"premissa": (b, mod) in premissa_de, "media": agg["media"], "ic95": agg["ic95"],
                            "por_celula": {_celula(d, lugar): statistics.fmean(r["influencia"][mod] for r in vs
                                                                                if r["dono"] == d and r["lugar"] == lugar)
                                           for d, lugar in orq.CELULAS}}
    n_rac = cfg["g_elegivel"]["racoes"]
    elegivel = {}
    for b in bracos:
        vs = [r for r in registros if r["braco"] == b]
        elegivel[b] = {"frac_vidas": sum(1 for r in vs if r["cadeia"]["elegiveis"] >= n_rac) / len(vs), "vidas": len(vs),
                       "premissa": b == "M3",
                       "por_celula": {_celula(d, lugar): sum(1 for r in vs if r["dono"] == d and r["lugar"] == lugar
                                                             and r["cadeia"]["elegiveis"] >= n_rac)
                                      / sum(1 for r in vs if r["dono"] == d and r["lugar"] == lugar)
                                      for d, lugar in orq.CELULAS}}
    return {"pasta": orq.rc._relativo(pasta), "git_head_da_run": meta["git_head"], "vidas": len(registros),
            "contrastes": contrastes, "G-PESA": pesa, "G-ELEGIVEL": elegivel,
            "g_apr_m4": res["g_apr_m4"], "g_apr_m4_con_usado": meta["g_apr_m4_con"],
            "n": res["n"], "G-MVP_piloto": res["G-MVP_piloto"], "custo": res["custo"],
            "aviso": "o piloto serve so para o efeito, as premissas, o valor do M4-con, o K e o custo (secao 6.2): nenhum numero e evidencia"}


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    d = relatar(pasta)
    bv._gravar(pasta / "relato.json", bv._dump(d))
    print(json.dumps({k: d[k] for k in ("contrastes", "g_apr_m4", "G-MVP_piloto")}, indent=1, ensure_ascii=False, default=str)[:6000])
