"""O K da avaliacao da L-2 que o Matheus fixou (2026-10-29: 450 unidades, 150 por base, fora da grade da A5.8), com o porque e o custo: so
le os tres .json do piloto da L-2 (artifacts_v2_digibrain_prototipo/l2/piloto/), nenhuma vida. A conta e a da A5.8 (a funcao `poder` de
experiments/poder_l2_digibrain.py, o produto das 10 comparacoes do C-L2-3, com os sigma_d do piloto):
  - a conjuncao com K = 450 e com o K = 297 (o menor multiplo de 3 com 0,8);
  - a folga: a mesma conta com o sigma_d da privacao no longe 20 % maior (ele vem de 10 unidades);
  - o custo: as vidas (48 por unidade) e as horas de parede com 4 processos, pelo tempo de parede por vida do piloto.

    python experiments/k_fixado_l2_digibrain.py
grava artifacts_v2_digibrain_prototipo/l2/k_fixado.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import poder_l2_digibrain as pw  # noqa: E402
import run_v2_digibrain_l2 as l2  # noqa: E402

PILOTO = RAIZ / l2.SAIDA["l2_piloto"]
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "l2" / "k_fixado.json"
K_FIXADO = 450                                 # o Matheus, 2026-10-29 (A5.9)
K_DA_CONTA = 297                               # o menor multiplo de 3 com a conjuncao a 0,8 (custo_k.json)
FOLGA = 1.2                                    # o sigma_d da privacao no longe 20 % maior
DOMINA = "privacao|longe"


def conjuncao(comps: dict, k: int, fator: dict | None = None) -> float:
    fator = fator or {}
    out = 1.0
    for nome, c in comps.items():
        sd = c["sigma_d"] * fator.get(nome, 1.0)
        out *= 1.0 if sd == 0 else pw.poder(abs(c["margem"]) / sd, k)
    return out


def calcular() -> dict:
    res = json.loads((PILOTO / "resultado.json").read_text(encoding="utf-8"))
    meta = json.loads((PILOTO / "meta.json").read_text(encoding="utf-8"))
    med = json.loads((PILOTO / "medidas.json").read_text(encoding="utf-8"))
    comps = res["comparacoes"]
    if K_FIXADO % len(l2.BASES["l2_avaliacao"]):
        raise RuntimeError("o K fixado nao se divide pelas bases da avaliacao")
    for k in l2.GRADE_K:
        if not math.isclose(conjuncao(comps, k), res["regra_do_k"]["conjuncao"][str(k)], rel_tol=1e-12):
            raise RuntimeError(f"a conjuncao refeita em K = {k} nao e a do piloto")
    parede = meta["vidas_parede_s"] / len(med)
    vidas = K_FIXADO * len(l2.BRACOS) * len(l2.orq.CELULAS)
    folga = {DOMINA: FOLGA}
    return {"rotulo": "o K da avaliacao da L-2 fixado pelo Matheus (A5.9), com o porque e o custo; so leitura do piloto",
            "fontes": {l2.orq.rc._relativo(PILOTO / n): bv._sha(PILOTO / n) for n in ("resultado.json", "meta.json", "medidas.json")},
            "script": {"arquivo": l2.orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "k": K_FIXADO, "k_por_base": K_FIXADO // len(l2.BASES["l2_avaliacao"]), "aprovado": "pelo Matheus em 2026-10-29",
            "conjuncao": {"k_fixado": conjuncao(comps, K_FIXADO), "k_da_conta": conjuncao(comps, K_DA_CONTA)},
            "folga_sigma_d": {"comparacao": DOMINA, "fator": FOLGA, "k_fixado": conjuncao(comps, K_FIXADO, folga),
                              "k_da_conta": conjuncao(comps, K_DA_CONTA, folga)},
            "custo": {"vidas": vidas, "parede_por_vida_s_4_processos": parede, "parede_h_4_processos": vidas * parede / 3600}}


if __name__ == "__main__":
    d = calcular()
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {l2.orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)}): {json.dumps(d['conjuncao'])} {json.dumps(d['folga_sigma_d'])}")
