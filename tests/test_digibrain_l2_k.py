"""O K da avaliacao da L-2 (a A5.9 do adendo 5: 450 unidades, 150 por base, aprovado pelo Matheus em 2026-10-29) e a trava: a fase
`l2_avaliacao` aceita o 450 so com o "aprovado pelo Matheus" na A5.9, porque o piloto nao deu um K na grade; a config da avaliacao segue a
A5.9; e o k_fixado.json se refaz igual do piloto. Nenhuma vida roda."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import k_fixado_l2_digibrain as kf  # noqa: E402
import run_v2_digibrain_l2 as l2  # noqa: E402

CONFIG = RAIZ / "experiments" / "configs" / "v2_digibrain_prototipo" / "l2_avaliacao.json"


def _cfg() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def test_a_trava_aceita_o_450_com_o_matheus():
    assert json.loads((RAIZ / l2.SAIDA["l2_piloto"] / "resultado.json").read_text(encoding="utf-8"))["regra_do_k"]["k"] is None
    assert l2.k_da_avaliacao() == 450
    assert l2.modo_da_config(_cfg()) == "l2_avaliacao"


def test_a_trava_recusa_o_450_sem_o_matheus(monkeypatch):
    plano = l2._plano()
    secao = plano[plano.index("### A5.9"):]
    monkeypatch.setattr(l2, "_plano", lambda: plano.replace(secao, secao.replace("aprovado pelo Matheus", "proposto")))
    with pytest.raises(RuntimeError, match="aprovado por ele"):
        l2.k_da_avaliacao()


@pytest.mark.parametrize("k_por_base", [149, 151, 99])
def test_a_config_da_avaliacao_so_com_o_k_da_a5_9(k_por_base):
    c = _cfg()
    c["unidades"]["k"] = k_por_base
    with pytest.raises(ValueError, match="K por base"):
        l2.modo_da_config(c)


def test_o_k_fixado_se_refaz_igual_e_e_o_da_a5_9():
    d = kf.calcular()
    assert kf.SAIDA.read_text(encoding="utf-8") == bv._dump(d)
    assert d["k"] == l2.k_da_avaliacao() == 450 and d["k_por_base"] == 150 and d["custo"]["vidas"] == 21600
    assert d["conjuncao"]["k_fixado"] > 0.9 and 0.8 <= d["conjuncao"]["k_da_conta"] < 0.81
    assert d["folga_sigma_d"]["k_fixado"] > 0.8 > d["folga_sigma_d"]["k_da_conta"]
