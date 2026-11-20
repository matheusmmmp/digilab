"""O custo do K da avaliacao da L-2, para o Matheus (o adendo 5, A5.8: um K acima de 100, ou nenhum K da grade, volta a ele com o custo).
So le o resultado.json, o medidas.json e o meta.json do piloto da L-2 (artifacts_v2_digibrain_prototipo/l2/piloto/), nenhuma vida:
  - o custo de cada K da grade, em vidas (48 por unidade) e em horas de parede com 4 processos, pelo tempo de parede por vida do piloto;
  - fora da regra, so como informacao: o menor K (multiplo de 3) com a conjuncao do C-L2-3 >= 0,8, pela mesma conta da A5.8 e com os
    sigma_d do piloto. A regra nao muda: a grade e o alvo sao os da A5.8.

    python experiments/custo_k_l2_digibrain.py
grava artifacts_v2_digibrain_prototipo/l2/custo_k.json
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import poder_l2_digibrain as pw  # noqa: E402
import run_v2_digibrain_l2 as l2  # noqa: E402

PILOTO = RAIZ / l2.SAIDA["l2_piloto"]
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "l2" / "custo_k.json"
K_MAX_BUSCA = 3000


def calcular() -> dict:
    res = json.loads((PILOTO / "resultado.json").read_text(encoding="utf-8"))
    med = json.loads((PILOTO / "medidas.json").read_text(encoding="utf-8"))
    meta = json.loads((PILOTO / "meta.json").read_text(encoding="utf-8"))
    comps = res["comparacoes"]
    if any(c["sigma_d"] is None for c in comps.values()):
        raise RuntimeError("o piloto sem o sigma_d de alguma comparacao")

    def conj(k: int) -> float:
        return math.prod(1.0 if c["sigma_d"] == 0 else pw.poder(abs(c["margem"]) / c["sigma_d"], k) for c in comps.values())

    for k in l2.GRADE_K:                          # a mesma conta do piloto
        if not math.isclose(conj(k), res["regra_do_k"]["conjuncao"][str(k)], rel_tol=1e-12):
            raise RuntimeError(f"a conjuncao refeita em K = {k} nao e a do resultado.json do piloto")
    parede = meta["vidas_parede_s"] / len(med)
    vidas_por_unidade = len(l2.BRACOS) * len(l2.orq.CELULAS)
    k_alem = next((k for k in range(3, K_MAX_BUSCA + 1, 3) if conj(k) >= l2.ALVO_PODER), None)

    def custo(k: int) -> dict:
        return {"vidas": k * vidas_por_unidade, "parede_h_4_processos": k * vidas_por_unidade * parede / 3600, "conjuncao": conj(k)}

    return {"rotulo": "o custo do K da avaliacao da L-2, para o Matheus (A5.8); o K fora da grade e so informacao, a regra nao muda",
            "fontes": {l2.orq.rc._relativo(PILOTO / n): bv._sha(PILOTO / n) for n in ("resultado.json", "medidas.json", "meta.json")},
            "script": {"arquivo": l2.orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "regra_do_k": {k: v for k, v in res["regra_do_k"].items() if k != "custo"},
            "parede_por_vida_s_4_processos": parede, "cpu_por_vida_s": statistics.fmean(v["custo"]["vida_cpu"] for v in med.values()),
            "vidas_por_unidade": vidas_por_unidade,
            "grade": {str(k): custo(k) for k in l2.GRADE_K},
            "fora_da_grade": None if k_alem is None else {"k": k_alem, **custo(k_alem)},
            "comparacao_que_domina": min(comps, key=lambda c: comps[c]["poder"]["201"])}


if __name__ == "__main__":
    d = calcular()
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {l2.orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)}); fora da grade: {d['fora_da_grade']}")
