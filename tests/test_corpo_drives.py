"""V2, corpo, etapa 6 (lado da quimica): os drives novos e os gestos (docs/TAREFA_V2_CORPO_DRIVES.md, secoes 7, 8 e 17).

O G-MEC do corpo, em contas exatas: as subidas por tick acordado (e nada dormindo), o estresse pelos drives acima do limiar, as
meias-vidas no prazo, o tedio pela variedade recente (DS-4: a bola reduz mais que o brincar sem bola; a mesma atividade repetida reduz
menos), a novidade na curiosidade (so com o mundo fisico, CD-8), o carinho na solidao e no estresse com o medo da mao (CD-5), o tapa na
dor, no susto e no estresse, e os receptores novos. E que a etapa 6 nao mexe nos drives de hoje. O motor (o tapa no log, o
`atividade` por decisao, os `vistos_novos`) e do A. So as sementes dos testes.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_CORPO_DRIVES, CONFIG_PADRAO, ConfigCorpo  # noqa: E402
from digilab.corpo import Corpo, div_arred, passo_meia_vida  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.state import Estado  # noqa: E402

CFG = CONFIG_PADRAO
CC = CONFIG_CORPO_DRIVES                                         # a etapa 6 inteira (com a quimica, a digestao e a Vida)
C = CC.escala
S = CC.escala_receptor
SEM_GESTOS = ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True)
SEM_NOVOS = ConfigCorpo(ligada=True, digestao=True, vida=True)
ACORDADO = Estado(tick=600)                                       # 10h: dia, acordado, sem sujeira


class TapaDeTeste:
    """o AcaoUsuario.TAPA do A (etapa 6, events.py): o corpo o le pelo valor"""
    value = "tapa"


def _corpo(cc=CC, com_mundo=False, **q) -> Corpo:
    c = Corpo.de_estado(Estado(), CFG, cc, com_mundo=com_mundo)
    c.q.update(q)
    return c


# ================================================================== os quimicos e os receptores
def test_quimicos_e_receptores_novos():
    c = _corpo(com_mundo=True)
    assert c.quimicos == ("fome", "desconforto", "cansaco", "tristeza", "dano", "alimento", "vida", "tedio", "curiosidade", "solidao",
                          "estresse", "dor", "susto")
    assert all(c.q[n] == 0 for n in ("tedio", "curiosidade", "solidao", "estresse", "dor", "susto"))
    c.q.update(tedio=337500, dor=90000)
    r = c.receptores()
    assert r["tedio"] == div_arred(337500 * S, C) == 768 and r["dor"] == div_arred(90000 * S, C) == 205
    assert set(r) == {"fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto"}
    assert "curiosidade" not in _corpo(com_mundo=False).q                              # CD-8: so com o mundo fisico
    assert set(_corpo(SEM_GESTOS).receptores()) == {"fome", "higiene", "energia", "humor", "saude", "tedio", "solidao", "estresse"}


def test_drives_novos_sobem_acordado_e_param_dormindo():
    c = _corpo(com_mundo=True)
    c.passo(ACORDADO)
    assert (c.q["tedio"], c.q["curiosidade"], c.q["solidao"]) == (CC.tedio_sobe, CC.curiosidade_sobe, CC.solidao_sobe) == (450, 300, 225)
    c.passo(replace(ACORDADO, dormindo=True))
    assert (c.q["tedio"], c.q["curiosidade"], c.q["solidao"]) == (450, 300, 225)
    assert c.q["estresse"] == 0                                                      # nenhum drive acima de 0,75


def test_estresse_pelos_drives_acima_do_limiar_conta_exata():
    """depois da fase 1 do tick: estresse += div_arred(soma max(0, q_d - 337500), 256), e entao a meia-vida"""
    c = _corpo(fome=400000, tedio=340000)
    c.passo(ACORDADO)
    fome = 400000 + c.t.fome_por_tick
    tedio = 340000 + CC.tedio_sobe
    v = div_arred((fome - 337500) + (tedio - 337500), 256)
    assert c.q["fome"] == fome and c.q["tedio"] == tedio
    assert c.q["estresse"] == passo_meia_vida(v, CC.k_meia_vida_estresse)


@pytest.mark.parametrize("quimico,q0,h", [("dor", 90000, 60), ("susto", 180000, 30)])
def test_meia_vida_chega_a_metade_no_prazo(quimico, q0, h):
    c = _corpo(**{quimico: q0})
    n = 0
    while c.q[quimico] > q0 // 2:
        c.passo(replace(ACORDADO, dormindo=True))
        n += 1
    assert abs(n - h) <= 1, n


def test_meia_vida_do_estresse_e_a_da_secao_3():
    """k = 32: a meia-vida efetiva da tabela da secao 3 e 1419 (+-2 pelo minimo de 1 no decremento)"""
    q, n = 45000, 0
    while q > 22500:
        q = passo_meia_vida(q, CC.k_meia_vida_estresse)
        n += 1
    assert abs(n - 1419) <= 2


# ================================================================== o tedio pela variedade (DS-4)
def test_tedio_bola_reduz_mais_que_brincar_sem_bola():
    a, b = _corpo(tedio=337500), _corpo(tedio=337500)
    a.atividade("bola")
    b.atividade("brincar")
    assert a.q["tedio"] == 337500 - 135000 and b.q["tedio"] == 337500 - 45000


def test_tedio_repetir_reduz_menos_que_alternar():
    """com a janela vazia a primeira reducao e a base; a bola de novo vale (J - 1)/J; a bola e depois explorar devolve a base"""
    rep, alt = _corpo(tedio=C), _corpo(tedio=C)
    rep.atividade("bola")
    alt.atividade("bola")
    antes_rep, antes_alt = rep.q["tedio"], alt.q["tedio"]
    rep.atividade("bola")
    alt.atividade("explorar")
    assert antes_rep - rep.q["tedio"] == div_arred(135000 * 7, 8) == 118125
    assert antes_alt - alt.q["tedio"] == 90000
    assert rep.janela_tedio == ["bola", "bola"]


def test_tedio_janela_de_8_e_repetir_8_vezes_zera():
    c = _corpo(tedio=C)
    reducoes = []
    for _ in range(9):
        antes = c.q["tedio"]
        c.atividade("brincar")
        reducoes.append(antes - c.q["tedio"])
    assert reducoes == [div_arred(45000 * (8 - r), 8) for r in range(8)] + [0]
    assert len(c.janela_tedio) == 8


def test_tedio_dono_brinca_vem_do_acao_dono():
    c = _corpo(tedio=337500)
    c.acao_dono(AcaoUsuario.BRINCAR)
    assert c.q["tedio"] == 337500 - 90000 and c.janela_tedio == ["dono_brinca"]
    c.acao_pet(AcaoPet.BRINCAR)                                       # o brincar do pet nao reduz o tedio sozinho: so o `atividade`
    assert c.q["tedio"] == 337500 - 90000
    with pytest.raises(ValueError, match="desconhecida"):
        c.atividade("dormir")
    with pytest.raises(ValueError, match="drives_novos"):
        _corpo(SEM_NOVOS).atividade("bola")


# ================================================================== a curiosidade (CD-8)
def test_novidade_reduz_a_curiosidade_ate_2():
    c = _corpo(com_mundo=True, curiosidade=C)
    c.estimulo_novidade(0)
    assert c.q["curiosidade"] == C                                    # explorar sem novidade nao reduz
    c.estimulo_novidade(1)
    assert c.q["curiosidade"] == C - 90000
    c.estimulo_novidade(5)
    assert c.q["curiosidade"] == C - 90000 - 180000
    with pytest.raises(ValueError, match="CD-8"):
        _corpo(com_mundo=False).estimulo_novidade(1)
    with pytest.raises(ValueError, match="inteiro"):
        c.estimulo_novidade(-1)


# ================================================================== o carinho e o tapa (secao 8)
def test_carinho_reduz_solidao_e_estresse():
    c = _corpo(solidao=300000, estresse=200000)
    tristeza = c.q["tristeza"]
    c.acao_dono(AcaoUsuario.ACARICIAR)
    assert c.q["solidao"] == 120000 and c.q["estresse"] == 110000
    assert c.q["tristeza"] == max(0, tristeza - 27000)                # o 0,06 de hoje


def test_o_susto_corta_o_carinho_na_medida():
    """CD-5: o carinho vezes (C - q_susto) / C; com o susto na metade, metade do alivio; com o medo em 0, o alivio inteiro"""
    c = _corpo(solidao=300000, estresse=200000, susto=C // 2)
    c.acao_dono(AcaoUsuario.ACARICIAR)
    assert c.q["solidao"] == 300000 - 90000 and c.q["estresse"] == 200000 - 45000
    s = _corpo(replace(CC, medo_da_mao=0), solidao=300000, estresse=200000, susto=C // 2)
    s.acao_dono(AcaoUsuario.ACARICIAR)
    assert s.q["solidao"] == 120000 and s.q["estresse"] == 110000
    sem = _corpo(SEM_GESTOS, solidao=300000, estresse=200000)          # sem gestos nao ha susto: o fator e 1
    sem.acao_dono(AcaoUsuario.ACARICIAR)
    assert sem.q["solidao"] == 120000


def test_tapa_sobe_dor_susto_e_estresse_e_nao_mexe_nos_drives_de_hoje():
    c = _corpo()
    hoje = c.drives()
    c.acao_dono(TapaDeTeste())
    assert (c.q["dor"], c.q["susto"], c.q["estresse"]) == (90000, 180000, 45000)
    assert c.drives() == hoje
    with pytest.raises(ValueError, match="gestos"):
        _corpo(SEM_GESTOS).acao_dono(TapaDeTeste())


# ================================================================== a etapa 6 nao mexe nos drives de hoje
def test_os_drives_de_hoje_nao_mudam_com_a_etapa_6():
    """a mesma sequencia de ticks e estimulos de hoje: a quimica dos drives de hoje e a digestao e a Vida saem iguais com e sem os
    drives novos e os gestos (eles so leem os drives de hoje)"""
    novo, hoje = _corpo(com_mundo=True), _corpo(SEM_NOVOS)
    estado = ACORDADO
    for k in range(3000):
        e = replace(estado, tick=600 + k, dormindo=(k // 500) % 2 == 1, sujeira=k % 3)
        for c in (novo, hoje):
            c.passo(e)
            if k % 97 == 0:
                c.acao_dono(AcaoUsuario.ACARICIAR)
            if k % 61 == 0:
                c.acao_pet(AcaoPet.BRINCAR)
            if k % 131 == 0:
                c.acao_dono(AcaoUsuario.ALIMENTAR)
        if k % 89 == 0:
            novo.acao_dono(TapaDeTeste())
            novo.atividade("explorar")
    assert {n: novo.q[n] for n in hoje.q} == hoje.q
    assert novo.q["estresse"] > 0 and novo.q["tedio"] > 0
