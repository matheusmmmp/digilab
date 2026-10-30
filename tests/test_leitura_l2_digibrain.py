"""A leitura da avaliacao da L-2 (adendo 5): o resultado.json se refaz igual das 12 partes relidas, o avaliacao_leitura.json se refaz igual,
e a run foi a liberada (a main limpa, 4 processos, 21 600 vidas, K = 450). Nenhuma vida roda."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import leitura_l2_digibrain as lt  # noqa: E402


def test_a_run_e_a_liberada():
    meta = json.loads((lt.AVALIACAO / "meta.json").read_text(encoding="utf-8"))
    assert meta["fase"] == "l2_avaliacao" and meta["git_limpo"] is True and meta["processos"] == 4
    assert meta["git_head"].startswith("0a27d97") and meta["k_fixado"] == 450
    assert meta["medidas_indice_sha256"] == bv._sha(lt.AVALIACAO / lt.l2.INDICE)


def test_a_leitura_se_refaz_igual_das_partes():
    d = lt.calcular()
    assert d["resultado_refeito_das_partes"] is True and d["vidas"] == 21600
    assert lt.SAIDA.read_text(encoding="utf-8") == bv._dump(d)
    p = d["por_braco_e_lugar"]
    assert len(p) == 12 and all(v["vidas"] == 1800 for v in p.values())
    assert all(p[f"{b}|{lu}"]["s1"]["suspensas"] == 0 for b in ("M3", "M0") for lu in lt.l2.orq.LUGARES)
