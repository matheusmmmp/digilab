"""V2, banheiro, etapa 2 (lado do corpo): a vontade e o conforto (docs/TAREFA_V2_BANHEIRO.md, secoes 3, 5b e 8; BN-6).

O G-MEC do corpo, em contas exatas: a vontade sobe +150 por tick acordado e nada dormindo, sobe com 1/3 do que a digestao passa (o
resto da divisao guardado: a soma e exata), cai a 0 no aliviar e, acima de 0,75, sobe o desconforto +150 por tick; a necessidade no chao
da +22500 de desconforto e, na regiao, +100 por tick por necessidade, ate 3; o conforto sobe com o carinho (com o medo da mao) e cai com
meia-vida 60. O grafo com o banheiro passa as quatro checagens. O G-CONS no corpo (com o limpador, o sinal do aliviar e maior; sem ele,
o mesmo no banheiro e fora) e o G-CAR (o sinal do carinho e pelo menos 3 vezes o do limpador nos tres estados de referencia). Sem a
sub-chave, nada disso existe. O motor (o mapa, o objeto, o limpador) e da etapa 3, do A. So as sementes dos testes.
"""
from __future__ import annotations

import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CONFIG_BANHEIRO, CONFIG_CONSEQUENCIA, CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES,  # noqa: E402
                            CONFIG_PADRAO, ConfigBanheiro, ConfigCorpo)
from digilab.corpo import (PARAMETROS_CORPO, Corpo, div_arred, grafo_do_corpo, k_meia_vida, passo_meia_vida,  # noqa: E402
                           quimicos_de, taxas_de)
from digilab.corpo_grafo import Emissor, Grafo, GrafoInvalido, Leitura, Quimico, checar  # noqa: E402
from digilab.events import ACOES_PET_BANHEIRO, ACOES_PET_HOJE, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.instinto_banheiro import PARAMETROS_BANHEIRO  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.policies import lobos as lb  # noqa: E402
from digilab.state import Estado  # noqa: E402

CFG = CONFIG_PADRAO
CC = CONFIG_CORPO_BANHEIRO
C = CC.escala
S = CC.escala_receptor
ACORDADO = Estado(tick=600)                                       # 10h: dia, acordado, sem sujeira
DRIVES = ("fome", "higiene", "energia") + tuple(d for d in lb.DRIVES_NOVOS_SINAL if d in lb.receptores_novos(CC, True))
PD = dict(CONFIG_CONSEQUENCIA.pesos_drives_corpo)


def _corpo(cc=CC, com_mundo=True, **q) -> Corpo:
    c = Corpo.de_estado(Estado(), CFG, cc, com_mundo=com_mundo)
    c.q.update(q)
    return c


def _pc(c: Corpo) -> PercepcaoCorpo:
    return PercepcaoCorpo(**c.receptores())


# ================================================================== a chave e a config
def test_sub_chave_exige_os_gestos_e_os_registros_cobrem_os_campos():
    with pytest.raises(ValueError, match="banheiro exige ConfigCorpo.gestos"):
        ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True, banheiro=True)
    assert CC.banheiro and CC.gestos and not CONFIG_CORPO_DRIVES.banheiro
    assert set(PARAMETROS_CORPO) == {f.name for f in fields(ConfigCorpo)}
    assert set(PARAMETROS_BANHEIRO) == {f.name for f in fields(ConfigBanheiro)}
    assert not CONFIG_BANHEIRO.ligada and not CONFIG_BANHEIRO.limpador
    with pytest.raises(ValueError):
        ConfigBanheiro(limiar_moderada=0.95)
    with pytest.raises(ValueError):
        ConfigBanheiro(w_banheiro_0=0)
    assert CC.k_meia_vida_conforto == k_meia_vida(60)


def test_sem_a_sub_chave_nada_existe():
    """a etapa 6 sem o banheiro: os quimicos, os receptores e as acoes do pet de antes; os estimulos do banheiro falham alto"""
    c = _corpo(CONFIG_CORPO_DRIVES)
    assert c.quimicos == quimicos_de(CONFIG_CORPO_DRIVES, True) and "vontade" not in c.q and "conforto" not in c.q
    assert "vontade" not in c.receptores() and set(taxas_de(CFG, CONFIG_CORPO_DRIVES).pet) == set(ACOES_PET_HOJE)
    assert "resto_vontade" not in c.para_dict()
    for estimulo in (c.estimulo_aliviar, c.estimulo_necessidade):
        with pytest.raises(ValueError, match="sub-chave banheiro"):
            estimulo()
    with pytest.raises(ValueError, match="sem a sub-chave banheiro"):
        c.passo(ACORDADO, necessidades=1)


def test_quimicos_receptores_e_acao_do_pet_com_a_chave():
    c = _corpo()
    assert c.quimicos[-2:] == ("vontade", "conforto") and c.q["vontade"] == c.q["conforto"] == 0
    assert set(taxas_de(CFG, CC).pet) == set(ACOES_PET_HOJE) | set(ACOES_PET_BANHEIRO) and taxas_de(CFG, CC).pet[AcaoPet.ALIVIAR] == {}
    c.q.update(vontade=405000, conforto=45000)
    r = c.receptores()
    assert r["vontade"] == div_arred(405000 * S, C) == 922 and r["conforto"] == div_arred(45000 * S, C) == 102
    # o cerebro le a vontade como falta (a concentracao) e o conforto ao contrario (a falta de conforto)
    pc = _pc(c)
    assert lb.falta_receptor(pc, "vontade", S) == 922 and lb.falta_receptor(pc, "conforto", S) == S - 102


# ================================================================== a vontade (G-MEC)
def test_vontade_sobe_acordado_e_para_dormindo():
    c = _corpo()
    c.passo(ACORDADO)
    assert c.q["vontade"] == CC.vontade_sobe == 150
    c.passo(replace(ACORDADO, dormindo=True))
    assert c.q["vontade"] == 150
    for _ in range(9):
        c.passo(ACORDADO)
    assert c.q["vontade"] == 1500


def test_vontade_sobe_com_um_terco_do_digerido_com_o_resto_guardado():
    """a racao (202500) e o comer (22500) e a fruta passam pela digestao; a vontade ganha floor(total / 3), o resto fica guardado"""
    c = _corpo(fome=C)
    c.acao_dono(AcaoUsuario.ALIMENTAR)
    assert c.digerido_total == 202500 and c.q["vontade"] == 67500 and c.resto_vontade == 0
    c.estimulo_fruta(0.15, 0.0)                     # 67500
    c.acao_pet(AcaoPet.COMER)                       # 22500
    assert c.digerido_total == 292500 and c.q["vontade"] == 97500 and c.resto_vontade == 0
    # quantidades que nao dividem por 3: o resto passa de um consumo ao seguinte
    c = _corpo(fome=C)
    for q in (1, 1, 1, 7):
        c._ingerir(q)
    assert c.digerido_total == 10 and c.q["vontade"] == 3 and c.resto_vontade == 1
    assert c.para_dict()["resto_vontade"] == 1


def test_aliviar_zera_a_vontade_e_a_vontade_alta_sobe_o_desconforto():
    c = _corpo(vontade=400000)
    c.estimulo_aliviar()
    assert c.q["vontade"] == 0
    # acima de 0,75 (337500), +150 de desconforto por tick a mais; no limiar, nada
    abaixo, acima, limiar = _corpo(vontade=300000), _corpo(vontade=337501), _corpo(vontade=337500 - CC.vontade_sobe)
    for c in (abaixo, acima, limiar):
        c.passo(ACORDADO)
    base = abaixo.q["desconforto"]
    assert base == abaixo.t.desconforto_por_tick
    assert acima.q["desconforto"] == base + CC.vontade_desconforto
    assert limiar.q["vontade"] == 337500 and limiar.q["desconforto"] == base   # a fase 2 le a vontade depois da subida: 337500 nao passa


def test_necessidade_no_chao_e_na_regiao():
    c = _corpo()
    c.estimulo_necessidade()
    assert c.q["desconforto"] == CC.necessidade_desconforto == 22500
    base = _corpo()
    base.passo(ACORDADO)
    for n, extra in ((1, 100), (2, 200), (3, 300), (5, 300)):
        c = _corpo()
        c.passo(ACORDADO, necessidades=n)
        assert c.q["desconforto"] == base.q["desconforto"] + extra
    with pytest.raises(ValueError):
        _corpo().passo(ACORDADO, necessidades=-1)


# ================================================================== o conforto (BN-6)
def test_conforto_sobe_com_o_carinho_com_o_medo_da_mao_e_cai_com_meia_vida_60():
    c = _corpo()
    c.acao_dono(AcaoUsuario.ACARICIAR)
    assert c.q["conforto"] == CC.conforto_carinho == 45000
    c = _corpo(susto=225000)                         # o susto na metade corta o carinho na metade
    c.acao_dono(AcaoUsuario.ACARICIAR)
    assert c.q["conforto"] == div_arred(45000 * (C - 225000), C) == 22500
    c = _corpo(conforto=90000)
    for _ in range(60):
        c.passo(replace(ACORDADO, dormindo=True))
    assert abs(c.q["conforto"] - 45000) <= 90                     # a metade no prazo, a menos do arredondamento
    q = 90000
    for _ in range(60):
        q = passo_meia_vida(q, CC.k_meia_vida_conforto)
    assert c.q["conforto"] == q


def test_os_drives_de_hoje_nao_mudam_com_o_banheiro():
    """com a vontade abaixo do limiar (o pet alivia antes), os quimicos da etapa 6 saem iguais com e sem a sub-chave, tick a tick: a
    vontade e o conforto nao mexem em nenhum outro quimico"""
    a, b = _corpo(CONFIG_CORPO_DRIVES), _corpo()
    for t in range(1500):
        e = replace(ACORDADO, tick=600 + t, dormindo=(t % 300) > 250)
        a.passo(e)
        b.passo(e)
        if t % 97 == 0:
            for c in (a, b):
                c.acao_dono(AcaoUsuario.ALIMENTAR if t % 2 else AcaoUsuario.ACARICIAR)
        assert {k: v for k, v in b.q.items() if k not in ("vontade", "conforto")} == a.q
        assert b.q["vontade"] <= CC.vontade_limiar
        if b.q["vontade"] > 300000:
            b.estimulo_aliviar()                     # o aliviar so mexe na vontade


# ================================================================== o grafo (secao 18 da tarefa do corpo)
@pytest.mark.parametrize("com_mundo", [False, True])
def test_grafo_com_o_banheiro_passa_as_quatro_checagens(com_mundo):
    c = _corpo(com_mundo=com_mundo)
    r = c.relato_grafo
    assert r["lacos"] == [] and r["so_pelo_teto"] == []
    assert "emissor:aliviar" in r["sumidouros"]["vontade"] and "reacao:digestao" in r["fontes"]["vontade"]
    assert "emissor:vontade_sobe" in r["fontes"]["vontade"]
    assert "meia_vida" in r["sumidouros"]["conforto"] and r["fontes"]["conforto"] == ["emissor:carinho_conforto"]
    assert ["conforto", "susto"] in r["pares_meia_vida_mesma_ordem"]          # o medo da mao acopla os dois (60 e 30)
    assert "emissor:vontade_desconforto" in r["fontes"]["desconforto"]


def test_gatilho_acima_mal_formado_falha_alto():
    q = (Quimico("a", 10, receptor="a", leitura="falta"), Quimico("b", 10, receptor="b", leitura="falta"))
    ok = Grafo(q, (), (Emissor("e", "acima", 2, (("b", 1),), (Leitura("a", 1, 1),), 5),))
    checar(ok)
    for e in (Emissor("e", "acima", 2, (("b", 1),), (), 5),                                           # sem leitura
              Emissor("e", "acima", 1, (("b", 1),), (Leitura("a", 1, 1),), 5),                        # fora da fase 2
              Emissor("e", "acima", 2, (("b", 1),), (Leitura("a", 1, 1), Leitura("b", 1, 1)), 5)):    # duas leituras
        with pytest.raises(GrafoInvalido, match="acima"):
            checar(Grafo(q, (), (e,)))


def test_grafo_sem_o_aliviar_nao_tem_sumidouro_para_a_vontade():
    """a checagem do sumidouro pega a vontade sem o aliviar (o teto sozinho e so relato, entao tira-se o teto tambem)"""
    g = grafo_do_corpo(CFG, CC, taxas_de(CFG, CC), True)
    quimicos = tuple(replace(q, descarte=False) if q.nome == "vontade" else q for q in g.quimicos)
    emissores = tuple(e for e in g.emissores if e.nome != "aliviar")
    with pytest.raises(GrafoInvalido, match="sem sumidouro"):
        checar(Grafo(quimicos, g.reacoes, emissores))


# ================================================================== G-CONS e G-CAR (secoes 5b e 8)
def _sinal(antes: Corpo, depois: Corpo) -> int:
    return lb.sinal_corpo(_pc(antes), _pc(depois), DRIVES, CONFIG_CONSEQUENCIA.ganho, S, PD)


def _aliviar(necessidade: bool, **q) -> int:
    a = _corpo(**q)
    d = _corpo(**q)
    d.estimulo_aliviar()
    if necessidade:
        d.estimulo_necessidade()
    return _sinal(a, d)


@pytest.mark.parametrize("q", [dict(desconforto=135000, vontade=360000), dict(desconforto=0, vontade=240000),
                               dict(desconforto=300000, vontade=420000, solidao=90000)])
def test_g_cons_o_limpador_aumenta_o_sinal_do_aliviar_no_banheiro(q):
    """com o limpador (no banheiro a necessidade some: so o aliviar) o sinal imediato e maior que fora (o aliviar e a necessidade);
    sem o limpador o banheiro e fora tem os mesmos estimulos, e o mesmo sinal"""
    no_banheiro_com_limpador = _aliviar(False, **q)
    fora = _aliviar(True, **q)
    no_banheiro_sem_limpador = _aliviar(True, **q)
    assert no_banheiro_com_limpador > fora
    assert no_banheiro_sem_limpador == fora


def _carinho(solidao: float, desconforto: float = 0.3, conforto: int = 0, cc=CC) -> int:
    q = dict(desconforto=round(desconforto * C), solidao=round(solidao * C))
    if cc.banheiro:
        q["conforto"] = conforto
    a = _corpo(cc, **q)
    d = _corpo(cc, **q)
    d.acao_dono(AcaoUsuario.ACARICIAR)
    drives = DRIVES if cc.banheiro else tuple(x for x in DRIVES if x not in ("vontade", "conforto"))
    return lb.sinal_corpo(_pc(a), _pc(d), drives, CONFIG_CONSEQUENCIA.ganho, S, PD)


LIMPADOR = 132     # o desconforto em 0,3: evitar +22500 vale div_arred(4 x (358^2 - 307^2), 1024) = 132 (secao 5b)


def test_g_car_o_carinho_vale_pelo_menos_3_vezes_o_limpador():
    assert _aliviar(False, desconforto=135000, vontade=360000) - _aliviar(True, desconforto=135000, vontade=360000) == LIMPADOR
    carinhos = {s: _carinho(s) for s in (0.2, 0.5, 0.8)}
    assert carinhos == {0.2: 940, 0.5: 1759, 0.8: 2739}
    assert all(f >= 3 * LIMPADOR for f in carinhos.values())
    # com o conforto ainda alto do carinho anterior (o pior caso da grade 6.1), ainda passa
    assert all(_carinho(s, conforto=CC.conforto_carinho) >= 3 * LIMPADOR for s in (0.2, 0.5, 0.8))
    # BN-6: sem o conforto (so a solidao e o estresse da tarefa do corpo), a solidao em 0,2 nao passa
    assert _carinho(0.2, cc=CONFIG_CORPO_DRIVES) == 164 < 3 * LIMPADOR
