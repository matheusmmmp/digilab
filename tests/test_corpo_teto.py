"""A ponte com teto (docs/PLANO_ANALISE_V3_CORPO_C3.md, secoes 2 e 7; `ConfigTetoFomeCorpo`). Sem teto, a D de hoje sai byte a byte
(tests/test_gabarito_corpo_acoplamento.py e o gabarito das chaves); aqui, o teto passado explicitamente vazio, o corte da ponte e as
travas."""
from __future__ import annotations

import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import (CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_CORPO_METABOLISMO, CONFIG_PADRAO, CONFIG_TETO_FOME_BAIXO,  # noqa: E402
                            CONFIG_TETO_FOME_CORPO, CONFIG_TETO_FOME_LIMIAR, PARAMETROS_TETO_FOME_CORPO, ConfigTetoFomeCorpo)
from digilab.corpo import Corpo  # noqa: E402
from digilab.state import Estado  # noqa: E402

CC = CONFIG_CORPO_METABOLISMO
D = CONFIG_ACOPLAMENTO_CORPO_LIGADA


def _corpo(ct=None, ca=D):
    return Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, cfg_acoplamento=ca, cfg_teto_fome=ct)


def test_o_status_cobre_os_campos():
    assert {f.name for f in fields(ConfigTetoFomeCorpo)} == set(PARAMETROS_TETO_FOME_CORPO)
    assert CONFIG_TETO_FOME_CORPO.teto is None
    assert CONFIG_TETO_FOME_BAIXO.teto == CC.escala // 2


def test_o_teto_do_dtl_e_o_limiar_da_privacao():
    c = _corpo(CONFIG_TETO_FOME_LIMIAR)
    assert CONFIG_TETO_FOME_LIMIAR.teto == c.t.limiar_privacao
    c.q["fome"] = CONFIG_TETO_FOME_LIMIAR.teto
    assert not c.em_privacao()
    c.q["fome"] += 1
    assert c.em_privacao()


def test_as_travas():
    for ruim in (0, -1, 1.5, "x"):
        with pytest.raises(ValueError):
            ConfigTetoFomeCorpo(teto=ruim)
    with pytest.raises(ValueError, match="exige a D"):
        _corpo(CONFIG_TETO_FOME_LIMIAR, ca=None)
    with pytest.raises(ValueError, match="passa de C"):
        _corpo(ConfigTetoFomeCorpo(teto=CC.escala + 1))
    with pytest.raises(TypeError):
        _corpo(object())


@pytest.mark.parametrize("ct", [CONFIG_TETO_FOME_LIMIAR, CONFIG_TETO_FOME_BAIXO])
def test_a_ponte_para_no_teto(ct):
    """com a falta, a ponte sobe a fome ate o teto e para; a fome basal continua, e o cansaco nao sobe pela falta"""
    teto, sem = _corpo(ct), _corpo()
    for c in (teto, sem):
        c.q["combustivel"] = 0
        c.q["reserva"] = 0
        c.q["fome"] = ct.teto - 2_000
    for _ in range(40):
        for c in (teto, sem):
            c.passo(Estado())
    basal = 40 * 375
    assert sem.q["fome"] > teto.q["fome"]
    assert teto.q["fome"] <= ct.teto + basal                      # passado o teto, so a basal sobe
    assert teto.q["cansaco"] == sem.q["cansaco"]                   # a falta nao vai ao cansaco nos dois
    assert teto.ticks_teto > 0 and sem.ticks_teto == 0


def test_abaixo_do_teto_e_a_d():
    """longe do teto, o corpo com teto e o da D saem iguais"""
    teto, sem = _corpo(CONFIG_TETO_FOME_LIMIAR), _corpo()
    for c in (teto, sem):
        c.q["combustivel"] = 1_000
        c.q["fome"] = 0
    for _ in range(100):
        for c in (teto, sem):
            c.passo(Estado())
    assert teto.q == sem.q and teto.ticks_teto == 0


def test_o_teto_vazio_explicito_e_a_d():
    a, b = _corpo(), _corpo(CONFIG_TETO_FOME_CORPO)
    for c in (a, b):
        c.q["combustivel"] = 0
        c.q["fome"] = 380_000
        for _ in range(200):
            c.passo(Estado())
    assert a.q == b.q


def test_o_gabarito_de_paridade_reproduz():
    import exportar_gabarito_corpo_teto as ex
    assert ex.ARQUIVO.read_text(encoding="utf-8") == ex.texto()
