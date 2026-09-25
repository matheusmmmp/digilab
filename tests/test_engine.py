"""Testes do v0.

O teste que importa e `test_replay_reproduz_estado_identico`. Se ele
quebrar, o log deixou de ser dado de pesquisa e nada a jusante vale nada.
"""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab import (  # noqa: E402
    CONFIG_PADRAO,
    AcaoPet,
    AcaoUsuario,
    Estado,
    LogDeEventos,
    Motor,
    PoliticaInstinto,
    reproduzir,
)
from digilab.events import ACOES_V1  # noqa: E402


def _vida_simulada(motor: Motor, dias: int = 3, semente: int = 7) -> None:
    """Um dono sintetico: cuida em horarios plausiveis, com falhas."""
    rng = random.Random(semente)
    for _ in range(dias):
        for _ in range(24):
            motor.avancar(60)
            if rng.random() < 0.35:
                motor.observar(rng.choice(list(ACOES_V1)))


# --------------------------------------------------------------- determinismo


def test_mesma_semente_produz_vida_identica():
    a, b = Motor(semente=42), Motor(semente=42)
    _vida_simulada(a)
    _vida_simulada(b)
    assert a.estado() == b.estado()
    assert a.acoes_recentes(999) == b.acoes_recentes(999)


def test_sementes_diferentes_divergem():
    a, b = Motor(semente=42), Motor(semente=43)
    _vida_simulada(a)
    _vida_simulada(b)
    assert a.estado() != b.estado()


# -------------------------------------------------------------------- replay


def test_replay_reproduz_estado_identico():
    original = Motor(semente=42)
    _vida_simulada(original, dias=5)

    reproduzido = reproduzir(original.log, semente=42)

    assert reproduzido.estado() == original.estado()
    assert reproduzido.acoes_recentes(999) == original.acoes_recentes(999)


def test_replay_sobrevive_ao_disco():
    original = Motor(semente=99)
    _vida_simulada(original, dias=2, semente=3)

    texto = original.log.para_jsonl()
    recarregado = LogDeEventos.de_jsonl(texto)

    assert reproduzir(recarregado, semente=99).estado() == original.estado()


def test_log_rejeita_evento_desconhecido():
    from digilab.events import Evento

    log = LogDeEventos([Evento(tick=0, tipo="teletransporte", valor=1)])
    with pytest.raises(ValueError, match="desconhecido"):
        reproduzir(log)


# --------------------------------------------------------------- invariantes


def test_necessidades_ficam_no_intervalo():
    motor = Motor(semente=11)
    _vida_simulada(motor, dias=10, semente=11)
    e = motor.estado()
    for campo in ("fome", "higiene", "energia", "humor", "saude"):
        assert 0.0 <= e[campo] <= 1.0, f"{campo} saiu do intervalo: {e[campo]}"
    assert 0 <= e["sujeira"] <= CONFIG_PADRAO.sujeira_maxima


def test_abandono_derruba_a_saude():
    motor = Motor(semente=5)
    motor.avancar(60 * 24 * 4)  # quatro dias sem nenhum cuidado
    assert motor.estado()["saude"] < 0.5


def test_cuidado_regular_preserva_a_saude():
    motor = Motor(semente=5)
    for _ in range(4 * 24):
        motor.avancar(60)
        motor.observar(AcaoUsuario.ALIMENTAR)
        motor.observar(AcaoUsuario.LIMPAR)
    assert motor.estado()["saude"] > 0.9


def test_exaustao_leva_ao_sono():
    motor = Motor(semente=5, estado_inicial=Estado(energia=0.05))
    acoes = motor.avancar(30)
    assert acoes and acoes[0][1] is AcaoPet.DORMIR


def test_avanco_nao_aceita_valor_nao_positivo():
    with pytest.raises(ValueError):
        Motor().avancar(0)


# -------------------------------------------------------------- v0 nao aprende


def test_politica_do_v0_nao_tem_parametros():
    assert PoliticaInstinto().estado_interno()["parametros_aprendidos"] == 0


def test_politica_nao_muda_com_a_experiencia():
    """Controle: vidas diferentes, mesmo comportamento na mesma observacao."""
    novato = Motor(semente=1)
    veterano = Motor(semente=1)
    _vida_simulada(veterano, dias=20, semente=4)

    obs_igual = Observacao_fixa()
    r1, r2 = random.Random(0), random.Random(0)
    assert novato.politica.agir(obs_igual, r1) == veterano.politica.agir(obs_igual, r2)


def Observacao_fixa():
    from digilab import Observacao

    return Observacao(
        vetor_estado=(0.6, 0.8, 0.7, 0.6, 1.0, 0.0, 0.0, 0.5),
        ticks_desde_cuidado=10,
        total_cuidados=3,
    )
