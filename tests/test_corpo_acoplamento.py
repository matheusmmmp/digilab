"""CORPO_ACOPLAMENTO, etapa 1: a sonda descritiva (experiments/sonda_v3_corpo_acoplamento.py; docs/TAREFA_V3_CORPO_ACOPLAMENTO.md).

Confere que a instrumentacao so le (a vida sai byte a byte a de sempre), que a contabilidade do cansaco fecha, que o corte faz o que a
docstring diz numa sequencia feita a mao e os dois fatos do corpo em que o diagnostico se apoia."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import sonda_v3_corpo_acoplamento as SA  # noqa: E402
from digilab.config import CONFIG_PADRAO, CONFIG_CORPO_METABOLISMO  # noqa: E402
from digilab.corpo import Corpo, div_arred, grafo_do_corpo, taxas_de  # noqa: E402

DIAS = 2


@pytest.fixture(scope="module")
def vidas():
    com = SA.viver("REL", "atencioso", "longe_fixo", 101, DIAS)
    sem = SA.viver("REL", "atencioso", "longe_fixo", 101, DIAS, instrumentar=False)
    return com, sem


def test_a_instrumentacao_so_le(vidas):
    (m1, r1, b1), (m0, r0, b0) = vidas
    assert isinstance(m1, SA.MotorSonda) and not isinstance(m0, SA.MotorSonda)
    assert m1.log.para_jsonl() == m0.log.para_jsonl()
    assert b1 == b0
    assert SA.VC.orq.cerebro_de(r1).motivos == SA.VC.orq.cerebro_de(r0).motivos
    assert m1.serie_corpo == m0.serie_corpo


def test_a_contabilidade_fecha(vidas):
    (m, r, b), _ = vidas
    dec = SA.decisoes_da_vida(m, r, b)                  # confere a soma das fontes e a energia baixa, decisao a decisao
    assert len(dec) == DIAS * 96
    assert dec[-1]["acum"]["sono"] < 0 < dec[-1]["acum"]["basal_dia"]
    # a vida da VALUATION usa o corpo do v11 (o gasto 4/5 do adendo 5: o basal 300/150 e as atividades x 4/5), nao o 375/187 da config
    cc = m.corpo.cc
    assert (cc.metabolismo, cc.gasto_basal_acordado, cc.gasto_basal_dormindo, cc.gasto_atividades_num, cc.gasto_atividades_den) == (
        True, 300, 150, 4, 5)


def test_cansaco_sem_fonte_falha_alto(vidas):
    (m, _, _), _ = vidas
    with pytest.raises(RuntimeError, match="sem fonte"):
        m.corpo._somar({"cansaco": 7})


def test_limiar_do_cansaco():
    C, S, lam = 450000, 1024, 256
    q = SA.limiar_cansaco(C, S, lam)
    assert S - div_arred(q * S, C) < lam <= S - div_arred((q - 1) * S, C)


def _linha(k, cansaco, urgente, acum, dormindo=False, acao="ocioso", vista=False, comb=0, fome=0, ingerido=0, lim=100):
    base = {f: 0 for f in SA.FONTES}
    base.update(acum)
    return {"k": k, "baixa": cansaco >= lim, "urgente": urgente, "dormindo": dormindo, "acao": acao, "comida_vista": vista,
            "cansaco": cansaco, "fome": fome, "combustivel": comb, "acum": base, "ingerido": ingerido}


def test_o_corte_a_mao():
    C, lim, falta = 200, 150, 50
    dec = [
        _linha(0, 90, False, {}, lim=lim),                                                  # descansado (<= C/2)
        _linha(1, 120, True, {"basal_dia": 20, "atividades": 10}, vista=True, comb=60, lim=lim),   # fome urgente, viu e nao comeu
        _linha(2, 160, True, {"basal_dia": 30, "atividades": 10, "falta_combustivel": 30}, comb=10, lim=lim),   # as duas
        _linha(3, 155, False, {"basal_dia": 30, "atividades": 10, "falta_combustivel": 30, "sono": -5}, dormindo=True, comb=60,
               lim=lim),
        _linha(4, 151, True, {"basal_dia": 45, "atividades": 10, "falta_combustivel": 30, "sono": -24}, dormindo=True, comb=10,
               ingerido=5, lim=lim),
    ]
    r = SA.cortar(dec, lim, C, falta)
    assert (r["energia_baixa"], r["ambas"], r["fome_urgente"]) == (3, 2, 3)
    # na decisao 2: entraram 30 do basal, 30 da falta e 10 das atividades desde a decisao 0 (o empate vai a primeira classe); na 4, 45
    # do basal
    assert r["classes"] == {"falta_combustivel": 1, "atividades": 0, "andar": 0, "tempo_acordado": 1}
    assert r["cruzado"]["falta_combustivel"] == {"fome_antes": 1, "fome_depois": 0}
    assert r["cruzado"]["tempo_acordado"] == {"fome_antes": 0, "fome_depois": 1}   # a 4: a fome voltou dentro do trecho
    assert r["lados"]["adiou"] == 1 and r["lados"]["dormindo"] == 1 and r["lados"]["combustivel_em_falta"] == 2
    assert r["lados"]["falta_combustivel_necessaria"] == 2 and r["lados"]["andar_necessario"] == 0
    assert r["baixa_sem_fome_combustivel_em_falta"] == 0
    assert r["decisoes_desde_comer"] == [0] and r["ambas_sem_ter_comido"] == 1
    assert r["parte_somada"]["falta_combustivel"] == pytest.approx(30 / 70 + 30 / 85)


def test_somar_sem_vidas_falha():
    with pytest.raises(ValueError):
        SA.somar([])


def test_os_fatos_do_corpo():
    """a fome que o cerebro le sobe a cada tick, dormindo ou nao; so o gasto basal do combustivel cai a metade dormindo; a digestao
    poe no combustivel so o que tira da fome; e a falta de combustivel sobe o cansaco"""
    cc = CONFIG_CORPO_METABOLISMO
    g = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc))
    assert g.emissor("fome_tick").gatilho == "tick"
    assert g.emissor("gasto_basal_dormindo").gatilho == "dormindo"
    assert 2 * cc.gasto_basal_dormindo in (cc.gasto_basal_acordado, cc.gasto_basal_acordado - 1)
    assert dict(g.emissor("falta_combustivel").efeitos) == {"cansaco": cc.falta_cansaco}
    assert Corpo._digerir.__doc__ and "min(alimento, fome" in Corpo._digerir.__doc__
