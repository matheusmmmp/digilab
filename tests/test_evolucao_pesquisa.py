"""Evolucao do pet de pesquisa ate a forma adulta (ESPEC_EVOLUCAO_COMBATE.md, secao Pesquisa)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_CATALOGO, CONFIG_EVOLUCAO_PESQUISA as CFG  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario as U, Evento, LogDeEventos, acao_usuario, avanco  # noqa: E402
from digilab.evolucao import carater, evoluir, fracao_cuidado_bebe, ovo, politica_no_tick  # noqa: E402
from digilab.policies.bandit import PoliticaBandit  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402


def test_ovo_pareado_depende_so_da_semente():
    assert ovo(101) == ovo(101)
    esp, temp = ovo(202)
    assert esp in CONFIG_CATALOGO.especies_ativas
    assert set(temp) == set(CONFIG_CATALOGO.temperamento) and all(-1 <= v <= 1 for v in temp.values())
    assert {ovo(s) [0] for s in range(50)} == set(CONFIG_CATALOGO.especies_ativas)


def test_cuidado_conta_chamados_na_janela_sem_reusar_acao():
    ev = [avanco(0, 30), acao_usuario(30, U.ALIMENTAR),            # chamado de fome aos 30: atendido
          avanco(30, 15), acao_usuario(45, U.ACARICIAR),            # carinho aos 45: atendido
          avanco(45, 20), acao_usuario(65, U.LIMPAR),               # higiene aos 60: atendido (65 <= 75)
          avanco(65, 200)]
    frac, atend, tot = fracao_cuidado_bebe(LogDeEventos(ev))
    chamados = sum(len(range(iv, CFG.dur_bebe_min, iv)) for iv in CFG.chamados_bebe_min.values())
    assert (atend, tot) == (3, chamados) and frac == pytest.approx(3 / chamados)
    # acao fora da janela nao conta
    frac2, atend2, _ = fracao_cuidado_bebe(LogDeEventos([avanco(0, 50), acao_usuario(50, U.ALIMENTAR), avanco(50, 200)]))
    assert atend2 == 0


def test_politica_no_tick_corta_o_log_no_meio_de_um_avanco():
    v = simular_vida("atencioso", criar_dono("atencioso"), PoliticaBandit(), 202, 1, 16)
    log = v.motor.log
    p1 = politica_no_tick(log, lambda c: PoliticaBandit(c), 202, 900)
    p2 = politica_no_tick(log, lambda c: PoliticaBandit(c), 202, 900)
    assert p1.estado_interno() == p2.estado_interno()
    tudo = politica_no_tick(log, lambda c: PoliticaBandit(c), 202, 10**9)
    assert tudo.estado_interno() == v.motor.politica.estado_interno()


def test_carater_de_politica_sem_aprendizado_e_zero():
    car, bruto = carater(PoliticaInstinto(), PoliticaInstinto(), 8, 20, 9001)
    assert all(x == 0.0 for x in car.values()) and all(x == 0.0 for x in bruto.values())
    car2, _ = carater(PoliticaBandit(), PoliticaBandit(), 8, 20, 9001)     # bandit novo x bandit novo
    assert all(x == 0.0 for x in car2.values())


def test_evoluir_e_deterministico_e_instinto_cai_no_desempate():
    v = simular_vida("relapso", criar_dono("relapso"), PoliticaBandit(), 303, 2, 32)
    a = evoluir(v.motor.log, lambda c: PoliticaBandit(c), 303, 8, 20, 9001, 0.5)
    b = evoluir(v.motor.log, lambda c: PoliticaBandit(c), 303, 8, 20, 9001, 0.5)
    assert a == b and a.forma.estagio == "adulto" and a.especie == ovo(303)[0]
    assert CONFIG_CATALOGO.condicao_mult_min <= a.condicao <= CONFIG_CATALOGO.condicao_mult_max
    vi = simular_vida("relapso", criar_dono("relapso"), PoliticaInstinto(), 303, 2, 32)
    ei = evoluir(vi.motor.log, lambda c: PoliticaInstinto(c), 303, 8, 20, 9001, 0.5)
    assert (ei.forma.linha, ei.forma.adulta) == ("brigao", "duelista")   # carater zero: desempate fixo
