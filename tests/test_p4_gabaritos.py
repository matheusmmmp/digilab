"""P4, etapa 0 (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 4): o G2 do lado Python. As vidas de hoje que a P4 vai tocar (o J1 pela bancada e o
J5 com o adendo 8 nos quatro bracos) saem iguais ao gabarito gravado antes de qualquer codigo (tests/gabaritos/p4_vidas_de_hoje.json, por
tests/gabarito_p4.py). O lado TS fica em web/app/test/p4_etapa0.test.ts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_p4 as gp  # noqa: E402

GABARITO = json.loads(gp.ARQUIVO.read_text(encoding="utf-8"))


def test_o_gabarito_tem_o_j1_e_o_j5_nos_quatro_bracos():
    assert set(GABARITO) == {"j1", "j5_adendo8"}
    assert len(GABARITO["j1"]) == 36 and len(GABARITO["j5_adendo8"]) == 16
    bracos = {nome.split("~")[0] for nome in GABARITO["j5_adendo8"]}
    assert bracos == {"P1", "P1-plan", "P1-plan-desfecho", "P1-plan-cong"}


def test_g2_as_vidas_do_j1_sao_as_de_hoje():
    assert gp.vidas_j1() == GABARITO["j1"]


def test_g2_as_vidas_do_j5_com_o_adendo_8_sao_as_de_hoje():
    assert gp.vidas_j5() == GABARITO["j5_adendo8"]
