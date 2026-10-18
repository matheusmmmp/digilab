"""O gabarito do cerebro A para o jogo web (web/app/test/gabaritos/lobos_python.json, etapa 1 do W-PORTE) esta em dia com o Python.
Se mudar digilab/policies/lobos.py, o corpo, a consequencia ou o ponto do v11, rode `python experiments/exportar_gabarito_lobos.py`; o
teste do TS (etapas 2 e 3) confere a paridade."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_lobos as G  # noqa: E402


def test_gabarito_dos_lobos_em_dia():
    atual = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    assert atual == json.loads(json.dumps(G.gerar(), sort_keys=True))


def test_gabarito_e_o_v11():
    """o v11 da PW-1: sem elogio e sem bronca, com carinho, tapa e a consequencia no corpo, e o cerebro aprendendo"""
    g = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    assert len(g["l0"]) >= 2 and len(g["v11"]) >= 4
    for v in g["v11"]:
        valores = {e["valor"] for e in v["log"] if e["tipo"] == "acao_usuario"}
        assert not valores & {"elogiar", "repreender"}
        rec = v["aprendizado"]["recompensas"]
        assert rec["elogio"] == rec["repreensao"] == 0 and rec["carinho"] > 0 and rec["consequencia"] > 0
        assert v["aprendizado"]["n_atualizacoes"] > 0 and v["pesos_corpo"]
        assert all("sinal_corpo" in m for m in v["motivos"] if m["regra"] == "tempo_livre")
    assert any(v["aprendizado"]["recompensas"]["tapa"] > 0 for v in g["v11"])
    for v in g["l0"]:
        assert all(m["aprendido"] is None for m in v["motivos"])


def test_traco_do_v11_e_o_da_vida():
    """etapa 3 (G-PAR-L1): o traco das chamadas ao cerebro tem uma decisao (agir, consequencia, gancho do corpo) por motivo, e do dono so
    chegam o tapa e o carinho, tantos quantos o aprendizado contou; o interno e o estado do cerebro sem os motivos"""
    g = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    for v in g["v11"]:
        tipos = [t["t"] for t in v["traco"]]
        decisoes = [t for t in tipos if t in ("agir", "consequencia", "corpo")]
        assert decisoes == ["agir", "consequencia", "corpo"] * len(v["motivos"])
        assert set(tipos) == {"agir", "consequencia", "corpo", "dono", "carinho"}
        assert {t["acao"] for t in v["traco"] if t["t"] == "dono"} == {"tapa"}
        rec = v["aprendizado"]["recompensas"]
        assert tipos.count("dono") == rec["tapa"] and tipos.count("carinho") == rec["carinho"]
        assert v["interno"]["aprendizado"] == v["aprendizado"] and v["interno"]["pesos_corpo"] == v["pesos_corpo"]
        assert "motivos" not in v["interno"] and v["interno"]["n_decisoes"] == len(v["motivos"])
