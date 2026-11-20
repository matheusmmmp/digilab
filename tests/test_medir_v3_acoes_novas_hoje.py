"""AN0 da ACOES_NOVAS: o descritivo de hoje sai igual em duas execucoes e bate com o artefato gravado."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("medir_hoje", RAIZ / "experiments" / "medir_v3_acoes_novas_hoje.py")
medir = importlib.util.module_from_spec(spec)
sys.modules["medir_hoje"] = medir
spec.loader.exec_module(medir)


def test_sai_igual_em_duas_execucoes_e_igual_ao_gravado():
    a = medir._texto(medir.gerar())
    b = medir._texto(medir.gerar())
    assert hashlib.sha256(a.encode()).digest() == hashlib.sha256(b.encode()).digest()
    assert a == medir.SAIDA.read_bytes().decode("utf-8")


def test_contas_basicas_do_artefato():
    d = json.loads(medir.SAIDA.read_text(encoding="utf-8"))
    t = d["grupos"]["total"]
    assert t["decisoes_vagar"] <= t["decisoes"]
    assert t["fracao_vagar"] == round(t["decisoes_vagar"] / t["decisoes"], 6)
    assert sum(t["mistura_das_escolhas"].values()) == t["decisoes"]
    assert sum(int(k.rstrip("+")) * v for k, v in t["corridas_de_vagar"]["histograma"].items() if "+" not in k) <= t["decisoes_vagar"]
    assert d["conferencia_3_3"]["fora_do_r"] == ["susto"]


def test_corridas():
    assert medir._corridas([False, True, True, False, True]) == [(1, 2), (4, 1)]
    assert medir._corridas([]) == []
