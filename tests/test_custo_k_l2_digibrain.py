"""O custo do K da L-2 (experiments/custo_k_l2_digibrain.py): o artefato se refaz igual dos tres .json do piloto no git, a conjuncao e a
do resultado.json do piloto em cada K da grade (o script falha alto se nao), e o K fora da grade e o menor multiplo de 3 com a conjuncao
a 0,8. Nenhuma vida roda."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import custo_k_l2_digibrain as ck  # noqa: E402


def test_o_custo_do_k_se_refaz_igual():
    d = ck.calcular()
    assert ck.SAIDA.read_text(encoding="utf-8") == bv._dump(d)
    assert d["regra_do_k"]["k"] is None and d["regra_do_k"]["volta_ao_matheus"]
    k = d["fora_da_grade"]["k"]
    assert k % 3 == 0 and d["fora_da_grade"]["conjuncao"] >= 0.8 and d["grade"]["201"]["conjuncao"] < 0.8
    assert d["grade"]["51"]["vidas"] == 51 * 48 and d["comparacao_que_domina"] == "privacao|longe"
