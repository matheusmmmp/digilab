"""Etapa 4 - arena."""

import itertools
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab import AcaoPet, PoliticaInstinto  # noqa: E402
from digilab.arena import (  # noqa: E402
    ORDEM_COMBATE,
    Lutador,
    lutar,
    mapa_pet_combate,
    stats_de_tracos,
    vence,
)
from digilab.config import CONFIG_ARENA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.policies import PoliticaBandit  # noqa: E402
from digilab.tracos import tracos_de_acoes  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402


def test_nucleo_ciclico_sem_estrategia_dominante():
    for a in ORDEM_COMBATE:
        vitorias = sum(vence(a, b) for b in ORDEM_COMBATE)
        derrotas = sum(vence(b, a) for b in ORDEM_COMBATE)
        assert vitorias == 2 and derrotas == 2
        assert not vence(a, a)
    for a, b in itertools.permutations(ORDEM_COMBATE, 2):
        assert vence(a, b) != vence(b, a)


def test_mapa_congelado_cobre_tudo():
    mapa = mapa_pet_combate(CONFIG_ARENA)
    assert set(mapa) == set(AcaoPet)
    assert set(mapa.values()) == set(ORDEM_COMBATE)


def test_stats_somam_zero_e_sao_deterministicos():
    t = tracos_de_acoes([AcaoPet.BRINCAR] * 500 + [AcaoPet.DORMIR] * 200)
    s1, s2 = stats_de_tracos(t), stats_de_tracos(t)
    assert s1 == s2
    assert abs(sum(s1.afinidade)) < 1e-12


def test_tracos_sao_lentos():
    t = tracos_de_acoes([AcaoPet.EMBURRAR] * 10)
    assert t[list(AcaoPet).index(AcaoPet.EMBURRAR)] < 0.25


def test_historico_vazio_falha_alto():
    with pytest.raises(ValueError):
        tracos_de_acoes([])


def _lutador(nome, semente):
    vida = simular_vida("atencioso", criar_dono("atencioso"), PoliticaBandit(), semente, 2, 32)
    acoes = [a for _, a in vida.motor.acoes_recentes(10**9)]
    return Lutador(nome, vida.motor.politica, stats_de_tracos(tracos_de_acoes(acoes))), vida


def test_partida_deterministica_e_reproduzivel_do_log():
    la, va = _lutador("A", 101)
    lb, vb = _lutador("B", 202)
    r1 = lutar(la, lb, semente=5)
    r2 = lutar(la, lb, semente=5)
    assert r1 == r2

    # reconstroi os dois pets do log e reproduz a partida bit a bit
    pa = reproduzir_com_feedback(va.motor.log, lambda c: PoliticaBandit(c), semente=101)
    pb = reproduzir_com_feedback(vb.motor.log, lambda c: PoliticaBandit(c), semente=202)
    ra = Lutador("A", pa.politica, la.stats)
    rb = Lutador("B", pb.politica, lb.stats)
    assert lutar(ra, rb, semente=5) == r1


def test_arena_nao_treina_a_politica():
    la, _ = _lutador("A", 101)
    lb, _ = _lutador("B", 202)
    antes = la.politica.estado_interno()
    lutar(la, lb, semente=9)
    assert la.politica.estado_interno() == antes


def test_sementes_diferentes_dao_partidas_diferentes():
    la = Lutador("A", PoliticaInstinto(), stats_de_tracos(tracos_de_acoes([AcaoPet.OCIOSO])))
    lb = Lutador("B", PoliticaInstinto(), stats_de_tracos(tracos_de_acoes([AcaoPet.OCIOSO])))
    assert lutar(la, lb, 1).turnos != lutar(la, lb, 2).turnos


def test_espelho_e_simetrico_em_media():
    """Mesma politica e mesmos stats dos dois lados: nenhum lado leva vantagem sistematica."""
    s = stats_de_tracos(tracos_de_acoes([AcaoPet.OCIOSO] * 50))
    la, lb = Lutador("A", PoliticaInstinto(), s), Lutador("B", PoliticaInstinto(), s)
    pontos = sum(lutar(la, lb, k).pontos_a for k in range(300)) / 300
    assert 0.40 < pontos < 0.60
