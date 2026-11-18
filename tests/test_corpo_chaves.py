"""As chaves dos bracos da ablacao do corpo (docs/PLANO_ANALISE_V3_CORPO.md, secoes 2 e 7): a opcao E (`ConfigDigestaoCorpo.inteira`, a
comida que sobra com a fome em 0 vira combustivel) e a opcao C5 (`ConfigConsertoValuation.reflexo_suave`, o reflexo do sono vira peso).
Desligadas, a vida de hoje sai byte a byte: tests/test_gabarito_corpo_acoplamento.py (o gabarito das vidas de hoje, gravado antes de
qualquer chave do corpo) e tests/test_gabarito_valuation_conserto.py; aqui, cada uma tambem passada explicitamente desligada."""
from __future__ import annotations

import json
import random
import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import (CONFIG_CONSERTO_VALUATION, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO, CONFIG_DIGESTAO_CORPO,  # noqa: E402
                            CONFIG_DIGESTAO_CORPO_INTEIRA, CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO, CONFIG_REFLEXO_SUAVE,
                            PARAMETROS_DIGESTAO_CORPO, ConfigConsertoValuation, ConfigDigestaoCorpo)
from digilab.corpo import Corpo  # noqa: E402
from digilab.digibrain.arb import Arbitragem  # noqa: E402
from digilab.state import Estado  # noqa: E402

CC = CONFIG_CORPO_METABOLISMO
S = CONFIG_DIGIBRAIN_INATOS.escala
LAM_SONO = CONFIG_DIGIBRAIN_INATOS.lambda_sono


# ------------------------------------------------------------------ a opcao E
def _corpo(cd=None):
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, cfg_digestao=cd)
    c.q["combustivel"] = CC.falta_limiar           # longe do teto: o excedente cabe inteiro
    return c


def test_o_status_da_e_cobre_os_campos():
    assert {f.name for f in fields(ConfigDigestaoCorpo)} == set(PARAMETROS_DIGESTAO_CORPO)
    assert CONFIG_DIGESTAO_CORPO.inteira is False and CONFIG_DIGESTAO_CORPO_INTEIRA.inteira is True
    with pytest.raises(TypeError):
        ConfigDigestaoCorpo(inteira=1)


def test_a_e_exige_a_digestao_e_o_metabolismo():
    with pytest.raises(ValueError, match="metabolismo"):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, CONFIG_CORPO_DRIVES, cfg_digestao=CONFIG_DIGESTAO_CORPO_INTEIRA)
    with pytest.raises(TypeError):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, cfg_digestao=object())


@pytest.mark.parametrize("fome", [0, 10_000, CC.taxa_digestao // 3])
def test_comer_mais_que_a_fome(fome):
    """com a fome menor que a comida: a fome cai igual nas duas; hoje o resto e descartado, com a E ele vira combustivel"""
    comida = 202_500
    hoje, e = _corpo(), _corpo(CONFIG_DIGESTAO_CORPO_INTEIRA)
    for c in (hoje, e):
        c.q["fome"] = fome
        c._ingerir(comida)
    assert hoje.q["fome"] == e.q["fome"] == 0
    assert hoje.q["alimento"] == e.q["alimento"] == 0
    assert hoje.descartado_total - e.descartado_total == comida - fome
    assert e.q["combustivel"] - hoje.q["combustivel"] == comida - fome      # a conversao 1/1 do v11
    assert e.contas_metabolismo["convertido"] - hoje.contas_metabolismo["convertido"] == comida - fome


def test_comer_com_fome_nao_muda():
    """com a fome maior que a comida nada sobra: as duas saem iguais"""
    hoje, e = _corpo(), _corpo(CONFIG_DIGESTAO_CORPO_INTEIRA)
    for c in (hoje, e):
        c.q["fome"] = 300_000
        c._ingerir(100_000)
    assert hoje.q == e.q and hoje.descartado_total == e.descartado_total == 0


def test_o_excedente_respeita_o_teto():
    e = _corpo(CONFIG_DIGESTAO_CORPO_INTEIRA)
    e.q["combustivel"] = CC.escala - 1_000
    e.q["fome"] = 0
    e._ingerir(50_000)
    assert e.q["combustivel"] == CC.escala
    assert e.contas_metabolismo["descartado_teto"] == 49_000


def test_a_e_desligada_explicita_e_a_de_hoje():
    hoje, explicita = _corpo(), _corpo(CONFIG_DIGESTAO_CORPO)
    for c in (hoje, explicita):
        c.q["fome"] = 5_000
        c._ingerir(202_500)
        for _ in range(50):
            c.passo(Estado())
    assert hoje.q == explicita.q and hoje.descartado_total == explicita.descartado_total


# ------------------------------------------------------------------ a opcao C5
def _sens(energia):
    return {"leitura": {"energia": energia}, "contexto": {"dormindo": 0}, "social": None}


UNIDADES = [{"acao": "comer", "a": 600, "chave": ("comer", 1)}, {"acao": "dormir", "a": 100, "chave": ("dormir",)},
            {"acao": "explorar", "a": 0, "chave": ("explorar",)}]
AFETO = {"g_exp": 0, "urgencias": {"fome": S}}


def _arb(conserto=None):
    a = Arbitragem(conserto=conserto)
    a.sondas = {}                                    # as sondas pedem as somas e os termos do M-IMPULSO; aqui so os pesos
    return a


def test_a_c5_falha_alto():
    with pytest.raises(TypeError):
        ConfigConsertoValuation(reflexo_suave=1)
    with pytest.raises(ValueError):
        ConfigConsertoValuation(peso_reflexo_suave=0)
    with pytest.raises(ValueError, match="bracos diferentes"):
        ConfigConsertoValuation(reflexo_suave=True, guarda_fome_reflexo=True)
    with pytest.raises(RuntimeError, match="unidade dormir"):
        _arb(CONFIG_REFLEXO_SUAVE).escolher([UNIDADES[0]], AFETO, _sens(0), random.Random(1))


@pytest.mark.parametrize("energia", [0, LAM_SONO - 1])
def test_com_a_c5_o_reflexo_vira_peso(energia):
    arb = _arb(CONFIG_REFLEXO_SUAVE)
    assert arb.reflexo(_sens(energia)) is False
    out = arb.escolher(UNIDADES, AFETO, _sens(energia), random.Random(1))
    hoje = _arb().pesos([x["a"] for x in UNIDADES], 0)
    assert out["pesos"] == [hoje[0], hoje[1] + CONFIG_REFLEXO_SUAVE.peso_reflexo_suave, hoje[2]]
    assert out["reflexo"] is False and out["u"] is not None
    assert arb.reflexos == 0 and arb.suaves == 1 and arb.sorteios == 1


def test_com_a_c5_acima_de_lambda_sono_nada_muda():
    com, sem = _arb(CONFIG_REFLEXO_SUAVE), _arb()
    a = com.escolher(UNIDADES, AFETO, _sens(LAM_SONO), random.Random(7))
    b = sem.escolher(UNIDADES, AFETO, _sens(LAM_SONO), random.Random(7))
    assert json.dumps(a, default=str) == json.dumps(b, default=str)
    assert com.suaves == 0


def test_com_a_c5_o_comer_ainda_pode_ganhar():
    """o dormir concorre: em muitas sementes o sorteio escolhe as duas"""
    arb = _arb(CONFIG_REFLEXO_SUAVE)
    acoes = {arb.escolher(UNIDADES, AFETO, _sens(0), random.Random(s))["unidade"]["acao"] for s in range(40)}
    assert acoes == {"comer", "dormir"}


def test_sem_a_c5_o_reflexo_de_hoje():
    for arb in (_arb(), _arb(CONFIG_CONSERTO_VALUATION)):
        assert arb.reflexo(_sens(LAM_SONO - 1)) is True
        out = arb.escolher(UNIDADES, AFETO, _sens(LAM_SONO - 1), random.Random(1))
        assert out["unidade"]["acao"] == "dormir" and out["reflexo"] is True and out["u"] is None
        assert arb.reflexos == 1 and arb.suaves == 0


# ------------------------------------------------------------------ o gabarito de paridade
def test_o_gabarito_de_paridade_reproduz():
    import exportar_gabarito_corpo_chaves as ex
    assert ex.ARQUIVO.read_text(encoding="utf-8") == ex.texto()
