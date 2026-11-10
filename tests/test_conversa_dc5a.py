"""DC5a da CONVERSA_PET (docs/PLANO_ANALISE_V3_CONVERSA_DC5.md, secao 10): a voz-v4, a selecao, as medidas, as entradas, o orquestrador e a
marcacao, todos com clientes falsos. Nenhuma chamada a modelo de verdade e nenhuma vida das faixas de pesquisa (so as sementes dos testes)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_voz_jogo_dc5 as gvj  # noqa: E402

GABARITO_VOZ_JOGO = RAIZ / "experiments/configs/v3_conversa_dc5/gabarito_voz_jogo.json"


# ================================================================== 0. a voz do jogo nao muda (o gabarito gravado antes da mudanca)
def test_a_voz_do_jogo_e_a_do_gabarito_byte_a_byte():
    """o gabarito foi gravado com o codigo da `main` antes da voz-v4 (commit proprio); a voz-v2, a voz-v3 e o servico do jogo dao o mesmo"""
    gravado = json.loads(GABARITO_VOZ_JOGO.read_text(encoding="utf-8"))
    assert gvj.gabarito() == gravado
    assert {v["versao_prompt"] for v in gravado["servico"].values()} == {"voz-v2", "voz-v3"}
