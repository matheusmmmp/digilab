"""TAREFA_CORRECAO_COMBATE: regras da base corrigida (V2C), uma mudanca por teste.

Cada mudanca e ligada sozinha sobre a V2 original (ConfigCombateV2C com os padroes = V2), e a
tabela de interacao confere o efeito exato. A V2 original continua igual (test_base_v2_intacta e
a bateria rejogada em test_motivo_expressao).
"""

from __future__ import annotations

import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.bots import GAMBITS, GAMBITS_FINTA, bot  # noqa: E402
from digilab.combate_v2.gambits import Condicao, GambitInvalido, decidir_gambits, regra  # noqa: E402
from digilab.combate_v2.partida import jogar, reproduzir  # noqa: E402
from digilab.combate_v2.regras import (ACOES_ESCOLHIVEIS, Acao as A, AcaoIlegal, Distancia as D,  # noqa: E402
                                       eh_legal, estado_inicial, resolver)
from digilab.config import CONFIG_COMBATE_V2, ConfigCombateV2C  # noqa: E402

V2 = CONFIG_COMBATE_V2


def cfg(**kw) -> ConfigCombateV2C:
    return ConfigCombateV2C(**{**asdict(V2), **kw})


def est(dist=D.PERTO, preparando=(False, False), guts=(50, 50), turno=0):
    e = estado_inicial((70.0, 70.0), guts, (8, 8))
    lados = tuple(replace(l, preparando=p) for l, p in zip(e.lados, preparando))
    return replace(e, distancia=dist, lados=lados, turno=turno)


def test_padroes_da_v2c_reproduzem_a_v2():
    c = cfg()
    a, b = bot("adaptativo"), bot("agressivo")
    assert jogar(a, b, 7).log == jogar(bot("adaptativo", cfg=c), bot("agressivo", cfg=c), 7, c).log
    assert A.FINTAR not in ACOES_ESCOLHIVEIS


# ------------------------------------------------------------------ C1 finta
def test_fintar_so_e_legal_no_turno_de_execucao_e_com_a_chave():
    c = cfg(finta=True)
    assert not eh_legal(est(preparando=(True, False)), 0, A.FINTAR, V2)
    assert eh_legal(est(preparando=(True, False)), 0, A.FINTAR, c)
    assert not eh_legal(est(), 0, A.FINTAR, c)                     # nao esta executando
    with pytest.raises(AcaoIlegal):
        resolver(est(), A.FINTAR, A.DEFENDER, c)


@pytest.mark.parametrize("reacao,dano_executor_causa", [
    (A.ESQUIVAR, 8.0),                  # acerta quem esquivou
    (A.DEFENDER, 8.0 * 0.3),            # nao quebra guarda: redutor normal do defender
    (A.CARREGAR, 8.0 * 1.5),
    (A.AVANCAR, 8.0),
])
def test_tabela_da_finta(reacao, dano_executor_causa):
    c = cfg(finta=True)
    e, r = resolver(est(preparando=(True, False)), A.FINTAR, reacao, c)
    assert r.dano_recebido[1] == pytest.approx(dano_executor_causa)
    assert not e.lados[0].preparando


def test_finta_longe_nao_acerta_e_pesado_ainda_disponivel():
    c = cfg(finta=True)
    _, r = resolver(est(D.MEDIO, preparando=(True, False)), A.FINTAR, A.ESQUIVAR, c)
    assert r.dano_recebido[1] == 0.0
    _, r = resolver(est(preparando=(True, False)), A.PESADO, A.ESQUIVAR, c)
    assert r.dano_recebido[1] == 0.0                                 # o pesado continua esquivavel


def test_regra_de_fintar_exige_a_condicao_e_decide_no_turno_de_execucao():
    with pytest.raises(GambitInvalido):
        regra(Condicao("sempre"), A.FINTAR).validar(V2)
    c = cfg(finta=True)
    g = GAMBITS_FINTA["agressivo"]
    e = est(preparando=(True, False))
    e = replace(e, lados=(e.lados[0], replace(e.lados[1], historico=(A.ESQUIVAR, A.ESQUIVAR, A.DEFENDER))))
    import random
    assert decidir_gambits(g, 0.0, e, 0, random.Random(1), c)[0] is A.FINTAR
    assert decidir_gambits(g, 0.0, e, 0, random.Random(1), V2)[0] is A.PESADO    # sem a chave: automatico
    assert decidir_gambits(GAMBITS["agressivo"], 0.0, e, 0, random.Random(1), c)[0] is A.PESADO


# ------------------------------------------------------------------ C2 parry
@pytest.mark.parametrize("ataque,reacao,devolvido", [
    (A.GOLPE_RAPIDO, A.DEFENDER, 5.0),
    (A.GOLPE_RAPIDO, A.ESQUIVAR, 0.0),
    (A.GOLPE_RAPIDO, A.CARREGAR, 0.0),
    (A.DEFENDER, A.DEFENDER, 0.0),
])
def test_tabela_do_parry(ataque, reacao, devolvido):
    c = cfg(dano_parry=5.0)
    _, r = resolver(est(), ataque, reacao, c)
    assert r.dano_recebido[0] == pytest.approx(devolvido)
    _, r0 = resolver(est(), ataque, reacao, V2)
    assert r0.dano_recebido[0] == 0.0


def test_parry_so_com_golpe_que_acertou_de_perto():
    c = cfg(dano_parry=5.0, finta=True)
    _, r = resolver(est(preparando=(True, False)), A.FINTAR, A.DEFENDER, c)
    assert r.dano_recebido[0] == pytest.approx(5.0)                  # a finta e golpe rapido
    _, r = resolver(est(preparando=(True, False)), A.PESADO, A.DEFENDER, c)
    assert r.dano_recebido[0] == 0.0                                 # pesado nao sofre parry


# ------------------------------------------------------------------ C3 fuga condicionada
@pytest.mark.parametrize("dist,a,b,fim_v2,fim_c3", [
    (D.MEDIO, A.RECUAR, A.AVANCAR, D.MEDIO, D.PERTO),               # quem avanca alcanca
    (D.MEDIO, A.AVANCAR, A.RECUAR, D.MEDIO, D.PERTO),
    (D.MEDIO, A.RECUAR, A.DEFENDER, D.LONGE, D.LONGE),
    (D.MEDIO, A.RECUAR, A.RECUAR, D.LONGE, D.LONGE),
    (D.LONGE, A.AVANCAR, A.AVANCAR, D.PERTO, D.PERTO),
])
def test_tabela_da_fuga(dist, a, b, fim_v2, fim_c3):
    assert resolver(est(dist), a, b, V2)[0].distancia is fim_v2
    assert resolver(est(dist), a, b, cfg(fuga_condicionada=True))[0].distancia is fim_c3


def test_fuga_ilegalidades():
    c = cfg(fuga_condicionada=True)
    assert eh_legal(est(D.PERTO), 0, A.AVANCAR, V2) and not eh_legal(est(D.PERTO), 0, A.AVANCAR, c)
    assert eh_legal(est(D.LONGE), 0, A.RECUAR, V2) and not eh_legal(est(D.LONGE), 0, A.RECUAR, c)
    assert eh_legal(est(D.MEDIO), 0, A.AVANCAR, c) and eh_legal(est(D.MEDIO), 0, A.RECUAR, c)


# ------------------------------------------------------------------ C4 morte subita
def test_morte_subita_a_partir_do_turno():
    c = cfg(turno_morte_subita=25, mult_morte_subita=1.5)
    _, r = resolver(est(turno=23), A.GOLPE_RAPIDO, A.AVANCAR, c)     # resolve o turno 24
    assert r.dano_recebido[1] == pytest.approx(8.0)
    _, r = resolver(est(turno=24), A.GOLPE_RAPIDO, A.AVANCAR, c)     # resolve o turno 25
    assert r.dano_recebido[1] == pytest.approx(12.0)
    _, r = resolver(est(turno=30), A.GOLPE_RAPIDO, A.DEFENDER, cfg(turno_morte_subita=25, dano_parry=5.0))
    assert r.dano_recebido == pytest.approx((7.5, 8.0 * 0.3 * 1.5))  # parry tambem


# ------------------------------------------------------------------ C5 e C6 (campos da base)
def test_c5_custo_da_esquiva_e_c6_sem_bonus_de_defender():
    c5 = cfg(custo_esquivar=15)
    e = est(guts=(15, 50))
    assert not eh_legal(e, 0, A.ESQUIVAR, V2) and eh_legal(e, 0, A.ESQUIVAR, c5)
    c6 = cfg(guts_extra_defender=0)
    assert resolver(est(), A.DEFENDER, A.DEFENDER, V2)[0].lados[0].guts == 50 + 8 + 5
    assert resolver(est(), A.DEFENDER, A.DEFENDER, c6)[0].lados[0].guts == 50 + 8


def test_replay_bit_a_bit_na_v2c():
    c = cfg(finta=True, dano_parry=5.0, fuga_condicionada=True, turno_morte_subita=25)
    a, b = bot("agressivo", cfg=c), bot("contragolpe", cfg=c)
    p = jogar(a, b, 11, c)
    assert reproduzir(list(p.log), a, b, c).log == p.log
