"""V2, W-CORPO-DIGESTAO (docs/TAREFA_V2_CORPO_DRIVES.md, etapa 4 da secao 14): o orgao 2, a Vida.

O quimico `vida` decai `vida_decaimento` por tick desde C; os receptores de estagio nos limiares C - v x tick_do_estagio dao o estagio de
hoje, tick a tick (treino_stats.estagio_no_tick, com as duracoes de cada motor), e nos motores com estagio a troca cai no mesmo tick. A
Vida nao mata e nao tem receptor para o cerebro. O G-HOJE (a) segue valendo com os dois orgaos ligados. So as sementes dos testes.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_corpo_quimica as base  # noqa: E402
from digilab.config import (CONFIG_DURACOES, CONFIG_EVOLUCAO_PESQUISA, CONFIG_PADRAO, TICKS_POR_DIA,  # noqa: E402
                            ConfigCorpo)
from digilab.corpo import ESTAGIOS, QUIMICOS, Corpo, limiares_estagio, quimicos_de, ticks_de_estagio  # noqa: E402
from digilab.donos_educacao import simular_vida_educacao  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.treino_stats import estagio_no_tick  # noqa: E402
from digilab.treino_vida import simular_vida_treino  # noqa: E402

CFG = CONFIG_PADRAO
CC_VIDA = ConfigCorpo(ligada=True, digestao=True, vida=True)
C = CC_VIDA.escala
V = CC_VIDA.vida_decaimento
DURACOES = {"pesquisa": CONFIG_EVOLUCAO_PESQUISA, "teste": CONFIG_DURACOES.cfg_evo("teste"),
            "canonica": CONFIG_DURACOES.cfg_evo("canonica")}


# ------------------------------------------------------------------ a chave e o decaimento

def test_vida_dura_a_vida_mais_longa_da_pesquisa():
    assert V == C // (28 * TICKS_POR_DIA) == 11
    assert V * 28 * TICKS_POR_DIA < C                          # nos 28 dias do adendo 3 a Vida nao chega a 0
    assert quimicos_de(CC_VIDA) == QUIMICOS + ("alimento", "vida")


def test_subchaves_da_vida():
    with pytest.raises(ValueError, match="exige"):
        ConfigCorpo(ligada=True, vida=True)                    # a Vida e o orgao 2: exige o 1
    with pytest.raises(NotImplementedError):
        ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True)
    with pytest.raises(ValueError, match="positivo"):
        ConfigCorpo(ligada=True, digestao=True, vida=True, vida_decaimento=0)
    corpo = Corpo.de_estado(Estado(), CFG, ConfigCorpo(ligada=True, digestao=True))
    with pytest.raises(ValueError, match="sem o orgao 2"):
        corpo.estagio()


def test_limiares_e_vida_curta_demais_falha_alto():
    assert ticks_de_estagio(CONFIG_EVOLUCAO_PESQUISA) == (180, 900, 1980)
    assert limiares_estagio(CC_VIDA, CONFIG_EVOLUCAO_PESQUISA) == (C - V * 180, C - V * 900, C - V * 1980)
    with pytest.raises(ValueError, match="acaba antes"):
        limiares_estagio(ConfigCorpo(ligada=True, digestao=True, vida=True, vida_decaimento=C // 1980 + 1), CONFIG_EVOLUCAO_PESQUISA)


def test_vida_comeca_em_c_e_vem_do_tick_do_estado():
    assert Corpo.de_estado(Estado(), CFG, CC_VIDA).q["vida"] == C
    meio = Corpo.de_estado(Estado(tick=1000), CFG, CC_VIDA)
    assert meio.q["vida"] == C - V * 1000 and meio.estagio() == estagio_no_tick(1000)
    assert Corpo.de_estado(Estado(tick=10 ** 6), CFG, CC_VIDA).q["vida"] == 0


def test_vida_sem_receptor_para_o_cerebro():
    corpo = Corpo.de_estado(Estado(), CFG, CC_VIDA)
    assert set(corpo.receptores()) == {"fome", "higiene", "energia", "humor", "saude"}
    assert "vida" not in corpo.drives()


# ------------------------------------------------------------------ o estagio pela Vida e o de hoje, tick a tick

@pytest.mark.parametrize("nome", sorted(DURACOES))
def test_estagio_pela_vida_e_o_de_hoje_tick_a_tick(nome):
    """Em todo tick, do nascimento ao fim da Vida e alem: a Vida e C - v x tick (cortada em 0) e o estagio e o de estagio_no_tick."""
    cfg_evo = DURACOES[nome]
    corpo = Corpo.de_estado(Estado(), CFG, CC_VIDA, cfg_evo)
    for tick in range(C // V + 3 * TICKS_POR_DIA):
        assert corpo.q["vida"] == max(0, C - V * tick)
        assert corpo.estagio() == estagio_no_tick(tick, cfg_evo), (nome, tick)
        corpo.passo(Estado(tick=tick))
    assert corpo.q["vida"] == 0 and corpo.estagio() == "adulto"   # nao mata: em 0, fica em 0


def _cruzamentos(cfg_evo, ate: int) -> dict[str, int]:
    corpo = Corpo.de_estado(Estado(), CFG, CC_VIDA, cfg_evo)
    vistos = {}
    for tick in range(ate):
        e = corpo.estagio()
        if e != "bebe" and e not in vistos:
            vistos[e] = tick
        corpo.passo(Estado(tick=tick))
    return vistos


@pytest.mark.parametrize("duracao", ["teste", "canonica"])
def test_estagio_pela_vida_cai_no_tick_da_evolucao_do_motor_com_educacao(duracao):
    """O MotorEducacao (MotorTreino por baixo) troca de estagio no checkpoint; os ticks sao os mesmos dos receptores da Vida."""
    for semente in (101, 202):
        motor = simular_vida_educacao("atencioso", semente, 3, "brasa", NEUTRO, duracao=duracao).motor
        do_motor = {e: d["tick"] for e, d in motor.transicoes.items()}
        assert do_motor == _cruzamentos(DURACOES[duracao], 3 * TICKS_POR_DIA)
        assert set(do_motor) == set(ESTAGIOS[1:])


def test_estagio_pela_vida_cai_no_tick_da_evolucao_do_motor_com_treino():
    for semente in (303, 404):
        motor = simular_vida_treino("atencioso", semente, 2, "brasa", NEUTRO).motor
        do_motor = {e: d["tick"] for e, d in motor.transicoes.items()}
        assert do_motor == _cruzamentos(CONFIG_EVOLUCAO_PESQUISA, 2 * TICKS_POR_DIA)


# ------------------------------------------------------------------ G-HOJE (a) com os dois orgaos

@pytest.mark.parametrize("dono", base.DONOS)
def test_g_hoje_a_com_a_digestao_e_a_vida(dono):
    for semente in base.SEMENTES:
        r = base._malha_aberta(dono, semente, CC_VIDA)
        base._confere_g_hoje(r)
        corpo = r["corpo"]
        fim = base.DIAS * TICKS_POR_DIA
        assert corpo.q["vida"] == C - V * fim and corpo.estagio() == estagio_no_tick(fim)


def test_vida_nao_mexe_na_quimica_dos_drives():
    for dono, semente in (("aleatorio", 101), ("relapso", 303)):
        com = base._malha_aberta(dono, semente, CC_VIDA)["corpo"]
        sem = base._malha_aberta(dono, semente)["corpo"]
        assert {n: com.q[n] for n in QUIMICOS} == sem.q
