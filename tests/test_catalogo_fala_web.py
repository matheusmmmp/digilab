"""CN1: o catalogo da fala do servidor_web/ (Node) esta em dia com o Python (digilab/expressao.py, servidor/fala_llm.py).

O CI nao roda o Vitest do servidor_web/; este teste garante ao menos que o catalogo e o gabarito que ele le saem das tabelas de hoje.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))

import gerar_catalogo_fala_web as G  # noqa: E402


def test_catalogo_e_gabarito_em_dia():
    assert G.main(["--conferir"]) == 0, "rode python tools/gerar_catalogo_fala_web.py"


def test_catalogo_so_tem_o_catalogo_fechado():
    c = G.catalogo()
    assert set(c["acoes_vida"]) and set(c["acoes_combate"]) and set(c["fatores"])
    assert set(c["dominios"]) <= set(c["fatores"])
    assert c["modelo_padrao"] in c["precos_usd_por_mtok"]
    assert c["estagios_llm"] == ["adolescente", "adulto"]


def test_gabarito_tem_recusas_e_aceitos():
    g = G.gabarito()
    assert sum(c["erro"] for c in g["motivos"]) > 50
    assert sum(not c["erro"] for c in g["motivos"]) > 500
    assert any(m["ok"] for m in g["molduras"]) and any(not m["ok"] for m in g["molduras"])
