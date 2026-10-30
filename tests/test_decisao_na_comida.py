"""A decisao na comida (docs/TAREFA_V2_PRODUTO_FOME.md, o conserto (b); a chave do produto `decidirNaComida` do jogo web): com a
`ConfigDecisaoNaComida` ligada, a comida que o dono deixa no chao faz o pet decidir ja no proximo passo do laco. Desligada (o padrao, a
pesquisa), a vida de hoje.

- A chave nasce desligada, e ligada exige o mundo fisico.
- Desligada, a vida e a de hoje (os gabaritos do MVP, tests/test_gabarito_mvp_produto_web.py e tests/test_gabarito_mvp_mundo_web.py,
  seguem byte a byte; aqui, a mesma vida com a ConfigDecisaoNaComida desligada explicita).
- Ligada, a racao no meio do intervalo traz a decisao no mesmo tick, e a seguinte vem um intervalo depois; o cerebro e o mesmo.
- O gabarito do G-PAR do TS (web/app/test/gabaritos/decisao_na_comida_python.json) esta em dia byte a byte.
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_decisao_na_comida as G  # noqa: E402

from digilab.config import (CONFIG_DECISAO_NA_COMIDA, CONFIG_DECISAO_NA_COMIDA_LIGADA, CONFIG_MUNDO_MVP, CONFIG_PADRAO,  # noqa: E402
                            ConfigDecisaoNaComida)
from digilab.mundo import MotorMundo  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")
GRAVADO = json.loads(TEXTO)


def test_a_chave_nasce_desligada_e_exige_o_mundo():
    assert CONFIG_DECISAO_NA_COMIDA.ligada is False and CONFIG_DECISAO_NA_COMIDA_LIGADA.ligada is True
    with pytest.raises(TypeError):
        ConfigDecisaoNaComida(ligada=1)
    m = MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CONFIG_MUNDO_MVP)
    assert m.cdc is CONFIG_DECISAO_NA_COMIDA
    with pytest.raises(ValueError, match="mundo fisico"):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_decisao_comida=CONFIG_DECISAO_NA_COMIDA_LIGADA)
    with pytest.raises(TypeError):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CONFIG_MUNDO_MVP, cfg_decisao_comida=True)


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, separators=(",", ":")) + "\n"
    assert all(v["semente"] in bv.SEMENTES_TESTE for v in GRAVADO["vidas"])


def _decisoes(v: dict) -> list[int]:
    return [o["tick"] for o in v["traco"] if o["op"] == "decisao"]


def _racoes(v: dict) -> list[int]:
    return [o["tick"] for o in v["traco"] if o["op"] == "deixar_comida"]


def test_ligada_a_racao_traz_a_decisao_no_mesmo_tick_desligada_espera_o_intervalo():
    intervalo = CONFIG_PADRAO.intervalo_decisao_ticks
    vidas = GRAVADO["vidas"]
    assert [(v["semente"], v["decisao_na_comida"]) for v in vidas] == [(101, True), (101, False), (202, True), (202, False)]
    for lig, des in ((vidas[0], vidas[1]), (vidas[2], vidas[3])):
        dl, dd, racoes = _decisoes(lig), _decisoes(des), _racoes(lig)
        assert racoes == _racoes(des) and racoes
        for t in racoes:
            assert t in dl
            i = dl.index(t)
            if i + 1 < len(dl) and not any(t < r < dl[i + 1] for r in racoes):
                assert dl[i + 1] - t == intervalo
        assert sum(1 for t in racoes if t not in dd) > 5
        assert all(b - a == intervalo for a, b in zip(dd, dd[1:]))
        assert lig["decisoes"] > des["decisoes"]


def test_desligada_explicita_e_a_vida_de_hoje():
    """a vida desligada do gabarito e a mesma com a ConfigDecisaoNaComida padrao (sem o argumento): o motor nao muda nada sem a chave"""
    vidas = GRAVADO["vidas"]
    for v in (vidas[1], vidas[3]):
        assert v == G._vida(v["nome"], v["semente"], False)
