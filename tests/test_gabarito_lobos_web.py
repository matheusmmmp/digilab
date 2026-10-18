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
    # os ganchos do G-PAR-L1 (etapa 3): uma decisao, uma transicao e um gancho do corpo por motivo; o carinho so pelo corpo
    assert g["config_v11"]["receptores"] == list(G.RECEPTORES_V11)
    assert g["config_v11"]["corpo"]["drives_novos"] and g["config_v11"]["corpo"]["gestos"]
    for v in g["v11"]:
        tipos = [h[0] for h in v["ganchos"]]
        assert set(tipos) <= {"agir", "observar", "consequencia_corpo", "dono", "carinho"}
        assert tipos.count("agir") == tipos.count("observar") == tipos.count("consequencia_corpo") == len(v["motivos"])
        assert tipos.count("carinho") >= v["aprendizado"]["recompensas"]["carinho"] > 0
        assert "acariciar" not in {h[1] for h in v["ganchos"] if h[0] == "dono"}
    for v in g["l0"]:
        assert all(m["aprendido"] is None for m in v["motivos"])
