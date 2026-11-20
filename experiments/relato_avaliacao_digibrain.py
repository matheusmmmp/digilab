"""O relato da avaliacao do DigiBrain modular (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secoes 7 e 8): le os artefatos da
avaliacao (medidas.json, meta.json) e junta, so lendo, os descritivos que o plano pede e o resultado.json nao grava por inteiro:
  - o D-2: as curvas por dia da fracao das decisoes em que a memoria e o habito decidiram, no M3, no total e por lugar;
  - a cadeia comida -> corpo por celula: a taxa de fechamento media e a fracao das vidas com a cadeia, por braco (inclusive o A11);
  - as PE do prototipo (secao 8): o fim das intencoes por motivo, os episodios que saem (e com r > 0) e o H no teto, por braco;
  - as refeicoes por dia do A11, ao lado da referencia do diagnostico do MVP (secao 7).
Nenhuma medida nova, nenhum gate; nada se ajusta. Grava relato.json na pasta da avaliacao.

    python experiments/relato_avaliacao_digibrain.py artifacts_v2_digibrain_prototipo/avaliacao
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


def _media_por_dia(rs: list[dict], mod: str, dias: int) -> list:
    out = []
    for d in range(dias):
        vs = [r["influencia_por_dia"][mod][d] for r in rs if r["influencia_por_dia"][mod][d] is not None]
        out.append(statistics.fmean(vs) if vs else None)
    return out


def relatar(pasta: Path) -> dict:
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    if meta["fase"] != "avaliacao":
        raise ValueError("o relato e so da avaliacao")
    dias = meta["config"]["dias"]
    registros = list(json.loads((pasta / "medidas.json").read_text(encoding="utf-8")).values())
    esperadas = len(meta["unidades"]) * len(orq.CELULAS) * len(meta["bracos"])
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas no medidas.json, {esperadas} esperadas")
    m3 = [r for r in registros if r["braco"] == "M3"]
    d2 = {"total": {mod: _media_por_dia(m3, mod, dias) for mod in ("memoria", "habito")},
          "por_lugar": {lugar: {mod: _media_por_dia([r for r in m3 if r["lugar"] == lugar], mod, dias) for mod in ("memoria", "habito")}
                        for lugar in orq.LUGARES}}
    cadeia = {}
    for b in meta["bracos"]:
        rs = [r for r in registros if r["braco"] == b]
        cadeia[b] = {}
        for dono, lugar in orq.CELULAS:
            cs = [r for r in rs if r["dono"] == dono and r["lugar"] == lugar]
            taxas = [r["cadeia"]["taxa"] for r in cs if r["cadeia"]["taxa"] is not None]
            com = [r["com_cadeia"] for r in cs if r["com_cadeia"] is not None]
            cadeia[b][f"{dono}/{lugar}"] = {"taxa_media": statistics.fmean(taxas) if taxas else None,
                                            "frac_com_cadeia": sum(com) / len(com) if com else None, "vidas": len(cs)}
    pe = {}
    for b in meta["bracos"]:
        if b == "A11":
            continue
        rs = [r for r in registros if r["braco"] == b]
        fins: dict = {}
        for r in rs:
            for k, v in r["fins"].items():
                fins[k] = fins.get(k, 0) + v
        pe[b] = {"fins_por_motivo": dict(sorted(fins.items())),
                 "episodios_sairam_por_vida": statistics.fmean(r["episodios"]["sairam"] for r in rs),
                 "episodios_sairam_r_pos_por_vida": statistics.fmean(r["episodios"]["sairam_r_pos"] for r in rs),
                 "vidas_com_h_no_teto": sum(1 for r in rs if r["pesos_no_teto"] > 0), "vidas": len(rs)}
    a11 = [r for r in registros if r["braco"] == "A11"]
    return {"pasta": orq.rc._relativo(pasta), "git_head_da_run": meta["git_head"], "vidas": len(registros), "D-2_curvas": d2,
            "cadeia_por_celula": cadeia, "PE": pe,
            "A11_refeicoes_por_dia": statistics.fmean(r["cadeia"]["refeicoes_por_dia"] for r in a11) if a11 else None,
            "aviso": "so descritivo (secoes 7 e 8): nenhuma medida nova, nenhum gate"}


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    d = relatar(pasta)
    bv._gravar(pasta / "relato.json", bv._dump(d))
    print(json.dumps({k: d[k] for k in ("D-2_curvas", "PE", "A11_refeicoes_por_dia")}, indent=1, ensure_ascii=False, default=str)[:8000])
