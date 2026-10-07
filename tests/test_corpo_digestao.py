"""V2, W-CORPO-DIGESTAO (docs/TAREFA_V2_CORPO_DRIVES.md, etapa 3 da secao 14): o orgao 1, a digestao.

O G-HOJE (a) de novo, com a digestao na taxa C (CD-3): os drives lidos sao os de hoje, em malha aberta, como na etapa 1. A reacao
t = min(alimento, fome, taxa por tick), a composicao de cada comida (secao 5), o descarte quando a fome chega a 0 (o corte de hoje) e o
digerido de cada tick (a vontade do banheiro, docs/TAREFA_V2_BANHEIRO.md, secao 3). So as sementes dos testes.
"""
from __future__ import annotations

import dataclasses
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_corpo_quimica as base  # noqa: E402
from digilab.config import CONFIG_PADRAO, ConfigCorpo  # noqa: E402
from digilab.corpo import PARAMETROS_CORPO, QUIMICOS, Corpo, quimicos_de  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.state import Estado, aplicar_acao_usuario  # noqa: E402

CFG = CONFIG_PADRAO
CC_DIG = ConfigCorpo(ligada=True, digestao=True)
C = CC_DIG.escala
LENTA = 1000                      # uma taxa que morde, so para o mecanismo (a digestao lenta da pesquisa so entra com o plano)


def _corpo(fome: int, alimento: int = 0, taxa: int = C, **outros: int) -> Corpo:
    q = {"fome": fome, "desconforto": 0, "cansaco": 0, "tristeza": 0, "dano": 0, "alimento": alimento, **outros}
    return Corpo(q, CFG, ConfigCorpo(ligada=True, digestao=True, taxa_digestao=taxa))


# ------------------------------------------------------------------ a chave

def test_digestao_e_a_taxa_c_por_padrao():
    assert ConfigCorpo().taxa_digestao == C
    assert PARAMETROS_CORPO["taxa_digestao"][0] == "DECIDIDO"
    assert quimicos_de(CC_DIG) == QUIMICOS + ("alimento",)
    assert quimicos_de(ConfigCorpo(ligada=True)) == QUIMICOS
    with pytest.raises(ValueError, match="positiva"):
        ConfigCorpo(ligada=True, digestao=True, taxa_digestao=0)
    with pytest.raises(ValueError, match="exige"):
        ConfigCorpo(digestao=True)


def test_estomago_comeca_vazio_e_sem_receptor():
    corpo = Corpo.de_estado(Estado(), CFG, CC_DIG)
    assert corpo.q["alimento"] == 0
    assert set(corpo.receptores()) == {"fome", "higiene", "energia", "humor", "saude"}   # o pet sente a fome, nao o estomago
    assert set(corpo.drives()) == {"fome", "higiene", "energia", "humor", "saude"}
    with pytest.raises(ValueError, match="quimicos do corpo"):
        Corpo({n: 0 for n in QUIMICOS}, CFG, CC_DIG)           # com a digestao, falta o alimento


# ------------------------------------------------------------------ G-HOJE (a) com a digestao na taxa C

@pytest.mark.parametrize("dono", base.DONOS)
def test_g_hoje_a_com_a_digestao(dono):
    for semente in base.SEMENTES:
        r = base._malha_aberta(dono, semente, CC_DIG)
        base._confere_g_hoje(r)
        assert r["corpo"].digerido_total > 0


def test_g_hoje_a_digestao_e_a_base_dao_a_mesma_quimica():
    """Na taxa C a digestao e a quimica base sao o mesmo corpo, quimico a quimico, na vida inteira."""
    for dono, semente in (("aleatorio", 101), ("atencioso", 202), ("relapso", 303)):
        com = base._malha_aberta(dono, semente, CC_DIG)["corpo"]
        sem = base._malha_aberta(dono, semente)["corpo"]
        assert {n: com.q[n] for n in QUIMICOS} == sem.q


# ------------------------------------------------------------------ a composicao (secao 5)

def test_composicao_de_cada_comida():
    """Com a fome alta e a taxa lenta, o estomago mostra quanto cada comida pos: racao 202500, comer 22500, fruta 67500 (comer + 0,10)."""
    corpo = _corpo(fome=C, taxa=1)
    corpo.acao_dono(AcaoUsuario.ALIMENTAR)
    assert corpo.digerido_tick == 1 and corpo.q["alimento"] == 202500 - 1
    corpo = _corpo(fome=C, taxa=1)
    corpo.acao_pet(AcaoPet.COMER)
    assert corpo.q["alimento"] == 22500 - 1
    corpo = _corpo(fome=C, taxa=1)
    corpo.acao_pet(AcaoPet.COMER)
    corpo.estimulo_fruta(0.10, -0.10)
    assert corpo.q["alimento"] == 67500 - 1                  # o comer e a nutricao da fruta, so a primeira unidade digerida
    assert corpo.q["tristeza"] == 45000                      # o efeito da fruta ruim vai direto, nao pelo estomago


def test_custo_de_fome_do_brincar_nao_e_comida():
    corpo = _corpo(fome=100000)
    corpo.acao_dono(AcaoUsuario.BRINCAR)
    assert corpo.q["fome"] == 122500 and corpo.q["alimento"] == 0 and corpo.digerido_total == 0


# ------------------------------------------------------------------ a reacao

def test_taxa_c_digere_na_hora_e_descarta_o_excesso():
    """Fome 10000 e racao 202500: digere 10000, a fome vai a 0 e os 192500 que sobram sao descartados (o corte de hoje)."""
    corpo = _corpo(fome=10000)
    corpo.acao_dono(AcaoUsuario.ALIMENTAR)
    assert (corpo.q["fome"], corpo.q["alimento"]) == (0, 0)
    assert (corpo.digerido_total, corpo.descartado_total, corpo.digerido_tick) == (10000, 192500, 10000)
    e = dataclasses.replace(Estado(), fome=(C - 10000) / C)
    assert aplicar_acao_usuario(e, AcaoUsuario.ALIMENTAR, CFG, random.Random(0)).fome == 1.0 == corpo.drives()["fome"]


def test_taxa_lenta_digere_por_tick_e_expoe_o_digerido():
    corpo = _corpo(fome=300000, taxa=LENTA)
    corpo.acao_dono(AcaoUsuario.ALIMENTAR)
    assert (corpo.q["fome"], corpo.q["alimento"], corpo.digerido_tick) == (299000, 201500, LENTA)
    corpo.passo(Estado(tick=600))                              # a taxa do tick ja foi: nada mais passa neste tick
    assert corpo.digerido_no_tick == LENTA and corpo.digerido_tick == 0
    assert corpo.q["alimento"] == 201500
    assert corpo.q["fome"] == 299000 + 375                     # o decaimento de hoje
    corpo.passo(Estado(tick=601))                              # o tick seguinte digere a taxa inteira, antes do decaimento
    assert corpo.digerido_no_tick == LENTA
    assert (corpo.q["alimento"], corpo.q["fome"]) == (200500, 299375 - LENTA + 375)
    assert corpo.digerido_total == 2 * LENTA


def test_taxa_lenta_descarta_quando_a_fome_zera():
    corpo = _corpo(fome=500, taxa=LENTA)
    corpo.acao_pet(AcaoPet.COMER)
    assert (corpo.q["fome"], corpo.q["alimento"]) == (0, 0)
    assert (corpo.digerido_total, corpo.descartado_total) == (500, 22000)


def test_estomago_cortado_em_c():
    corpo = _corpo(fome=C, alimento=C - 100, taxa=1)
    corpo.acao_dono(AcaoUsuario.ALIMENTAR)
    assert corpo.q["alimento"] == C - 1                        # cortado em C, e uma unidade digerida


def test_conservacao_numa_vida_com_taxa_lenta():
    """Com a taxa lenta a fome lida nao e mais a de hoje (de proposito), mas a comida se conserva e o estomago anda."""
    r = base._malha_aberta("atencioso", 101, ConfigCorpo(ligada=True, digestao=True, taxa_digestao=LENTA),
                          conferir=False)
    c = r["corpo"]
    assert c.digerido_total + c.descartado_total + c.q["alimento"] == r["comida"]
    assert c.digerido_total > 0


def test_para_dict_com_a_digestao():
    corpo = _corpo(fome=10000)
    corpo.acao_dono(AcaoUsuario.ALIMENTAR)
    corpo.passo(Estado(tick=0))
    d = corpo.para_dict()
    assert d["q"]["alimento"] == 0
    assert d["digestao"] == {"digerido_no_tick": 10000, "digerido_total": 10000, "descartado_total": 192500}
