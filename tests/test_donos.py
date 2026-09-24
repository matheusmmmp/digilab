"""Etapa 2 - donos sinteticos e orcamento imposto pelo simulador."""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab import AcaoUsuario, PoliticaInstinto, reproduzir  # noqa: E402
from digilab.donos import FABRICAS_DONO, criar_dono, julgar_acao  # noqa: E402
from digilab.config import CONFIG_DONOS  # noqa: E402
from digilab.treino import (  # noqa: E402
    OrcamentoExcedido,
    OrcamentoNaoConsumido,
    reproduzir_com_feedback,
    simular_vida,
)

DIAS = 3
ORCAMENTO = 3 * 16


def _n_interacoes(motor) -> int:
    return sum(1 for e in motor.log if e.tipo == "acao_usuario")


@pytest.mark.parametrize("braco", sorted(FABRICAS_DONO))
def test_todo_braco_gasta_exatamente_o_orcamento(braco):
    vida = simular_vida(braco, criar_dono(braco), PoliticaInstinto(), 101, DIAS, ORCAMENTO)
    assert vida.interacoes == ORCAMENTO
    assert _n_interacoes(vida.motor) == ORCAMENTO


class _DonoGuloso:
    nome = "guloso"

    def decidir(self, visao, rng):
        return [AcaoUsuario.ALIMENTAR] * (visao.maximo_permitido + 1)


class _DonoPreguicoso:
    nome = "preguicoso"

    def decidir(self, visao, rng):
        return []


def test_dono_que_excede_levanta_erro():
    with pytest.raises(OrcamentoExcedido):
        simular_vida("guloso", _DonoGuloso(), PoliticaInstinto(), 101, DIAS, ORCAMENTO)


def test_dono_que_nao_gasta_levanta_erro():
    with pytest.raises(OrcamentoNaoConsumido):
        simular_vida("preguicoso", _DonoPreguicoso(), PoliticaInstinto(), 101, DIAS, ORCAMENTO)


def test_vida_e_deterministica_e_reproduzivel():
    a = simular_vida("atencioso", criar_dono("atencioso"), PoliticaInstinto(), 202, DIAS, ORCAMENTO)
    b = simular_vida("atencioso", criar_dono("atencioso"), PoliticaInstinto(), 202, DIAS, ORCAMENTO)
    assert a.motor.estado() == b.motor.estado()
    r = reproduzir_com_feedback(a.motor.log, PoliticaInstinto, semente=202)
    assert r.estado() == a.motor.estado()
    assert r.acoes_recentes(10**9) == a.motor.acoes_recentes(10**9)


def test_replay_com_feedback_coincide_com_replay_do_engine_para_instinto():
    vida = simular_vida("aleatorio", criar_dono("aleatorio"), PoliticaInstinto(), 303, DIAS, ORCAMENTO)
    r1 = reproduzir(vida.motor.log, semente=303)
    r2 = reproduzir_com_feedback(vida.motor.log, PoliticaInstinto, semente=303)
    assert r1.estado() == r2.estado()
    assert r1.acoes_recentes(10**9) == r2.acoes_recentes(10**9)


def test_atencioso_cuida_melhor_que_aleatorio_com_mesmo_orcamento():
    """Sanidade do ambiente: com o mesmo volume, o cuidado guiado vale mais."""
    at = simular_vida("atencioso", criar_dono("atencioso"), PoliticaInstinto(), 404, 7, 7 * 16)
    al = simular_vida("aleatorio", criar_dono("aleatorio"), PoliticaInstinto(), 404, 7, 7 * 16)
    assert at.motor.estado()["saude"] > al.motor.estado()["saude"]


def test_julgamento_repreende_emburrar():
    estado = {"acao_atual": "emburrar", "energia": 0.8, "fome": 0.8, "higiene": 0.8, "tick_do_dia": 600}
    assert julgar_acao(estado, CONFIG_DONOS) == -1
