"""TAREFA_CORRECAO_COMBATE, Etapa 3: regras da V2.1 corrigida (V21C), uma mudanca por teste."""

from __future__ import annotations

import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.v21.bots import lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.partida import jogar, reproduzir  # noqa: E402
from digilab.combate_v2.v21.regras import (Acao as A, AcaoIlegal, Distancia as D, Regras, eh_legal,  # noqa: E402
                                           estado_inicial, resolver)
from digilab.config import CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, ConfigCombateV2C, ConfigCombateV21C  # noqa: E402

V21 = Regras()


def regras(base=None, v21=None) -> Regras:
    return Regras(base=ConfigCombateV2C(**{**asdict(CONFIG_COMBATE_V2), **(base or {})}),
                  v21=ConfigCombateV21C(**{**asdict(CONFIG_COMBATE_V21), **(v21 or {})}))


def est(fa="duelista", fb="duelista", dist=D.PERTO, prep=(False, False), marca=(0, 0), turno=0):
    a, b = lutador_adulto(fa, "brasa"), lutador_adulto(fb, "brasa")
    e = estado_inicial(a.perfil, b.perfil)
    lados = tuple(replace(l, preparando=p, marca=m) for l, p, m in zip(e.lados, prep, marca))
    return replace(e, distancia=dist, lados=lados, turno=turno)


def test_padroes_reproduzem_a_v21():
    a, b = lutador_adulto("espelho", "ferrugem"), lutador_adulto("emboscador", "cirro")
    assert jogar(a, b, 9).log == jogar(a, b, 9, regras()).log


def test_fintar_so_no_turno_de_execucao():
    r = regras({"finta": True})
    assert eh_legal(est(prep=(True, False)), 0, A.FINTAR, r)
    assert not eh_legal(est(prep=(True, False)), 0, A.FINTAR, V21)
    assert not eh_legal(est(), 0, A.FINTAR, r)
    with pytest.raises(AcaoIlegal):
        resolver(est(), A.FINTAR, A.DEFENDER, r)
    _, res = resolver(est(prep=(True, False)), A.FINTAR, A.ESQUIVAR, r)
    assert res.dano_recebido[1] > 0.0                         # acerta quem esquivou


def test_parry_na_v21():
    r = regras({"dano_parry": 5.0})
    _, res = resolver(est(), A.GOLPE_RAPIDO, A.DEFENDER, r)
    assert res.dano_recebido[0] == pytest.approx(5.0)
    _, res0 = resolver(est(), A.GOLPE_RAPIDO, A.DEFENDER, V21)
    assert res0.dano_recebido[0] == 0.0


def test_fuga_condicionada_e_a_sentinela():
    r = regras({"fuga_condicionada": True})
    assert resolver(est(dist=D.MEDIO), A.RECUAR, A.AVANCAR, V21)[0].distancia is D.MEDIO
    assert resolver(est(dist=D.MEDIO), A.RECUAR, A.AVANCAR, r)[0].distancia is D.PERTO
    assert resolver(est(dist=D.MEDIO), A.RECUAR, A.INVESTIDA, r)[0].distancia is D.PERTO
    # a sentinela, com a passiva pronta, continua recuando (e a passiva dela)
    e = est("sentinela", "duelista", dist=D.MEDIO)
    assert resolver(e, A.RECUAR, A.AVANCAR, r)[0].distancia is D.LONGE
    assert not eh_legal(est(dist=D.PERTO), 0, A.AVANCAR, r) and not eh_legal(est(dist=D.LONGE), 0, A.RECUAR, r)


def test_morte_subita_na_v21():
    r = regras({"turno_morte_subita": 25, "mult_morte_subita": 1.5})
    _, r24 = resolver(est(turno=23), A.GOLPE_RAPIDO, A.CARREGAR, r)
    _, r25 = resolver(est(turno=24), A.GOLPE_RAPIDO, A.CARREGAR, r)
    assert r25.dano_recebido[1] == pytest.approx(r24.dano_recebido[1] * 1.5)


@pytest.mark.parametrize("acao_op,dist_fim_perto,perde", [
    (A.GOLPE_RAPIDO, True, True),       # dano corpo a corpo recebido
    (A.CARREGAR, True, True),           # terminou em perto
    (A.CARREGAR, False, False),
])
def test_marca_fragil(acao_op, dist_fim_perto, perde):
    r = regras(v21={"marca_fragil": True})
    dist = D.PERTO if dist_fim_perto else D.MEDIO
    e = est("emboscador", "duelista", dist=dist, marca=(3, 0))
    acao_cac = A.DEFENDER if dist is D.PERTO else A.CARREGAR
    novo, _ = resolver(e, acao_cac, acao_op if dist is D.PERTO else A.CARREGAR, r)
    assert (novo.lados[0].marca == 0) is perde
    antigo, _ = resolver(e, acao_cac, acao_op if dist is D.PERTO else A.CARREGAR, V21)
    assert antigo.lados[0].marca == 2


def test_formula_de_vida_calibravel():
    r = regras(v21={"hp_por_vigor": 2.0, "hp_base": 80.0})
    a = lutador_adulto("muralha", "ferrugem", r.v21)
    s = a.perfil.stats["vigor"]
    assert a.perfil.hp_max == pytest.approx((80.0 + 2.0 * s) * 1.0)


def test_replay_v21c():
    r = regras({"finta": True, "dano_parry": 5.0, "fuga_condicionada": True, "turno_morte_subita": 25},
               {"marca_fragil": True})
    a, b = lutador_adulto("emboscador", "cirro", r.v21), lutador_adulto("furioso", "ferrugem", r.v21)
    p = jogar(a, b, 21, r)
    assert reproduzir(list(p.log), a, b, r).log == p.log
