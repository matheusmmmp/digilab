"""A ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA1): a agua no layout, os solidos dela e as regras para nada cair
nela.

- G-AG-1: o layout sem agua nao muda nada (o Mundo sem `secas`, os solidos vazios); os gabaritos de antes sao conferidos pelos testes
  deles (tests/test_gabarito_*.py).
- G-AG-2: em vidas inteiras do roteiro do gabarito, nenhuma comida, nenhuma bola e nenhuma posicao do pet fica na agua (o `conferir` do
  gerador falha alto).
- G-AG-3: toda celula de terra do layout se alcanca a pe a partir do ninho; o layout que nao cumpre falha alto.
- G-AG-5: o controlador leva o pet de um lado ao outro do rio, pela ponte.
- O gabarito do G-PAR do TS (web/app/test/gabaritos/ilha_agua_python.json, no mundo do produto com a agua) esta em dia byte a byte, e
  o replay refaz a vida. A ilha com arvores (a bola posta pelo dono, as arvores sacudidas) roda o mesmo roteiro so aqui.
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_ilha_agua as G  # noqa: E402

from digilab import contrato as ct  # noqa: E402
from digilab.config import (AGUA_DOCE, AGUA_ILHA, AGUA_MAR, AGUA_POR_LAYOUT, CONFIG_CONTRATO, CONFIG_CONTRATO_AGUA, CONFIG_MUNDO_ILHA,  # noqa: E402
                            CONFIG_MUNDO_ILHA_AGUA, CONFIG_MUNDO_MVP, CONFIG_MUNDO_MVP_AGUA, CONFIG_PADRAO, CONFIG_SACUDIR_LIGADA, PONTE, TERRA)
from digilab.mundo import (Mundo, MotorMundo, celulas_secas, centro_da_celula, deslocar, fabricas_mundo, reproduzir_mundo,  # noqa: E402
                           solidos_da_agua)
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402

CM = CONFIG_MUNDO_ILHA_AGUA
NX, NY, SUB = CM.celulas_x, CM.celulas_y, CM.sub


def _mundo(cm=CM) -> Mundo:
    return Mundo(cm, 101, arvores_na_casa=True)


def _com_agua(linhas) -> object:
    """o mundo da ilha com outro mapa de agua (um layout de teste na tabela, pelo nome)"""
    AGUA_POR_LAYOUT["teste_agua"] = tuple(linhas)
    return replace(CM, layout=replace(CM.layout, nome="teste_agua"))


@pytest.fixture(autouse=True)
def _tabela_limpa():
    yield
    AGUA_POR_LAYOUT.pop("teste_agua", None)


# ------------------------------------------------------------------ G-AG-1: sem agua, nada muda
def test_o_layout_sem_agua_nao_tem_solido_nem_celulas():
    assert set(AGUA_POR_LAYOUT) == {"ilha_agua", "mvp_agua"} and CONFIG_MUNDO_ILHA.layout.nome == "ilha"
    # a agua vai pelo nome do layout: os dois mundos com agua a tem, e os de antes (o mesmo layout com o nome de antes) nao
    for com, sem in ((CONFIG_MUNDO_ILHA_AGUA, CONFIG_MUNDO_ILHA), (CONFIG_MUNDO_MVP_AGUA, CONFIG_MUNDO_MVP)):
        assert celulas_secas(com) is not None and celulas_secas(sem) is None
        assert replace(com.layout, nome=sem.layout.nome) == sem.layout
    assert _mundo(CONFIG_MUNDO_MVP_AGUA).secas == _mundo().secas
    assert celulas_secas(CONFIG_MUNDO_ILHA) is None and solidos_da_agua(CONFIG_MUNDO_ILHA) == ()
    m = _mundo(CONFIG_MUNDO_ILHA)
    assert m.secas is None and m.seca(5, 5) and m.em_terra(5, 5) == (5, 5) and m.ate_a_margem(0, 0, 900, 400) == (900, 400)
    assert m.rolagem_seca(0, 0, 900, 400) == (900, 400)


# ------------------------------------------------------------------ o mapa
def test_o_mapa_tem_o_tamanho_do_mundo_e_o_mar_em_toda_a_borda():
    assert len(AGUA_ILHA) == NY and all(len(l) == NX for l in AGUA_ILHA)
    assert set("".join(AGUA_ILHA)) == {AGUA_MAR, AGUA_DOCE, TERRA, PONTE}
    borda = AGUA_ILHA[0] + AGUA_ILHA[-1] + "".join(l[0] + l[-1] for l in AGUA_ILHA)
    assert set(borda) == {AGUA_MAR}                                  # o que limita o pet e a agua, nao a borda do mapa


def test_o_mapa_errado_falha_alto():
    with pytest.raises(ValueError, match="linhas"):
        celulas_secas(_com_agua(AGUA_ILHA[:-1]))
    with pytest.raises(ValueError, match="linhas"):
        celulas_secas(_com_agua((AGUA_ILHA[0][:-1],) + AGUA_ILHA[1:]))
    with pytest.raises(ValueError, match="desconhecido"):
        celulas_secas(_com_agua(("#" + AGUA_ILHA[0][1:],) + AGUA_ILHA[1:]))


def test_os_solidos_cobrem_a_agua_e_so_a_agua():
    secas, solidos = celulas_secas(CM), solidos_da_agua(CM)
    assert all(s.categoria == "obstaculo" and s.colide and not s.alto for s in solidos)
    assert [(s.y0, s.x0) for s in solidos] == sorted((s.y0, s.x0) for s in solidos)
    for cy in range(NY):
        for cx in range(NX):
            x, y = centro_da_celula((cx, cy), CM)
            dentro = sum(ct.ponto_no_retangulo(x, y, s) for s in solidos)
            assert dentro == (0 if secas[cy * NX + cx] else 1), (cx, cy)
    assert sum((s.x1 - s.x0) * (s.y1 - s.y0) for s in solidos) == (NX * NY - sum(secas)) * SUB * SUB
    # o centro de toda celula de terra e livre para o corpo do pet (a grade do contrato e as celulas secas)
    assert ct.grade(NX, NY, SUB, CONFIG_CONTRATO_AGUA.r_pet, solidos) == secas


# ------------------------------------------------------------------ G-AG-3: a terra e uma so
def test_toda_a_terra_se_alcanca_a_pe_e_o_layout_ilhado_falha_alto():
    _mundo()                                                          # o layout de verdade passa
    linhas = list(AGUA_ILHA)
    for y in (11, 12, 21, 22):                                        # sem as pontes e sem a volta pelo norte da nascente,
        linhas[y] = linhas[y].replace(PONTE, AGUA_DOCE)               # a margem leste fica ilhada
    for y in (1, 2):
        linhas[y] = linhas[y][:43] + AGUA_DOCE + linhas[y][44:]
    with pytest.raises(ValueError, match="nao alcanca"):
        _mundo(_com_agua(linhas))
    cx, cy = CM.layout.ninho
    linhas = list(AGUA_ILHA)
    linhas[cy] = linhas[cy][:cx] + AGUA_DOCE + linhas[cy][cx + 1:]
    with pytest.raises(ValueError, match="ninho na agua"):
        _mundo(_com_agua(linhas))


# ------------------------------------------------------------------ nada cai na agua
def test_o_ponto_na_agua_vale_a_terra_mais_perto():
    m = _mundo()
    assert not m.seca(5, 5) and m.seca(*m.em_terra(5, 5))
    assert m.em_terra(300, 240) == (300, 240)                         # em terra, o ponto fica
    assert AGUA_ILHA[250 // SUB][670 // SUB] == AGUA_DOCE
    x, y = m.em_terra(670, 250)                                       # no rio: o centro de uma celula da margem
    assert m.seca(x, y) and (x % SUB, y % SUB) == (SUB // 2, SUB // 2) and abs(x - 670) <= 2 * SUB and abs(y - 250) <= SUB


def test_a_comida_e_a_bola_postas_na_agua_vao_para_a_terra():
    m = _mundo()
    c = m.deixar_comida("racao", 670, 250, 10)
    assert m.seca(c["x"], c["y"]) and (c["x"], c["y"]) == m.em_terra(670, 250) != (670, 250)
    m.deixar_bola(205, 368, 20)
    assert m.seca(m.bola["x1"], m.bola["y1"]) and m.bolas_deixadas[-1] == {"tick": 20, "x": m.bola["x1"], "y": m.bola["y1"]}
    with pytest.raises(ValueError):
        m.deixar_comida("racao", -1, 5, 30)                           # fora do mapa continua falhando alto


def test_a_bola_para_na_margem():
    m = _mundo()
    assert m.ate_a_margem(560, 250, 600, 250) == (600, 250)           # sem agua no caminho, chega
    x, y = m.ate_a_margem(560, 250, 900, 250)                         # o rio no caminho: para antes dele
    assert m.seca(x, y) and x == 41 * SUB - 1 and y == 250 and not m.seca(x + 1, y)
    for semente in (101, 202, 303):                                   # as rolagens de verdade ficam em terra, tick a tick
        w = Mundo(CM, semente, arvores_na_casa=True)
        w.deixar_bola(640, 250, 0)
        for t in range(1, 60):
            r = w.rolar_bola(t * 100)
            assert w.seca(*r["para"]) and w.seca(*r["de"])
            assert all(w.seca(*w.bola_em(t * 100 + k)) for k in range(100))
            assert [w.bola_em(t * 100 + k) for k in range(len(G.pontos_da_rolagem(r, CM.atrito)))][:-1] == G.pontos_da_rolagem(r, CM.atrito)[:-1]


def test_a_bola_nao_entra_na_agua_no_meio_da_rolagem():
    """a conta do `bola_em` arredonda pela distancia e sai ate 1 subunidade da linha que o `ate_a_margem` conferiu: a `rolagem_seca`
    encurta a rolagem ate todo ponto do caminho ficar em terra (os casos abaixo entravam na agua so com o `ate_a_margem`)"""
    m = _mundo()
    for x, y in ((601, 76), (867, 114), (86, 136), (291, 50), (662, 153)):
        achou = 0
        for d in range(16):
            for c in range(1, 25):
                alvo = deslocar(x, y, d, c * SUB, CM)
                x1, y1 = m.rolagem_seca(x, y, *alvo)
                pontos = G.pontos_da_rolagem({"de": (x, y), "para": (x1, y1)}, CM.atrito)
                assert all(m.seca(*q) for q in pontos), (x, y, d, c)
                margem = m.ate_a_margem(x, y, *alvo)
                achou += (x1, y1) != margem
                if (x1, y1) != margem:                                # so encurta: fica antes da margem, na mesma rolagem
                    assert not all(m.seca(*q) for q in G.pontos_da_rolagem({"de": (x, y), "para": margem}, CM.atrito))
        assert achou, (x, y)


# ------------------------------------------------------------------ a fruta que cairia na agua
def test_a_fruta_que_cairia_na_agua_cai_na_terra_mais_perto():
    """um mapa de teste com agua ao lado das arvores (no mapa de verdade nenhuma fruta chega a agua): a fruta da queda natural e a da
    sacudida ficam em terra, no ponto que o `em_terra` da para o ponto sorteado; o gemeo sem agua, com a mesma semente, sorteia o mesmo"""
    linhas = list(AGUA_ILHA)
    for y in (8, 10, 6, 13):                                          # faixas de agua doce acima e abaixo das arvores (9, 9), (14, 7), (6, 14)
        linhas[y] = linhas[y][:8] + AGUA_DOCE * 3 + linhas[y][11:]
    for y in (15,):
        linhas[y] = linhas[y][:5] + AGUA_DOCE * 3 + linhas[y][8:]
    cm = _com_agua(linhas)
    com, sem = Mundo(cm, 202, arvores_na_casa=True), Mundo(CONFIG_MUNDO_ILHA, 202, arvores_na_casa=True)
    for w in (com, sem):
        w.ligar_sacudir(CONFIG_SACUDIR_LIGADA)
    movidas = 0
    for t in range(60, 6000, 60):
        for w in (com, sem):
            w.atualizar(t)
        for arv in ("J1", "J2", "J3"):
            a, b = com.sacudir(arv, t), sem.sacudir(arv, t)
            assert a["motivo"] == b["motivo"]
            if a["caiu"] is not None:
                assert (a["x"], a["y"]) == com.em_terra(b["x"], b["y"]) and com.seca(a["x"], a["y"])
                c = com.comidas[a["caiu"]]
                assert (c["x"], c["y"]) == (a["x"], a["y"])            # o registro guarda onde a fruta ficou
                movidas += (a["x"], a["y"]) != (b["x"], b["y"])
    assert movidas >= 3 and len(com.sacudidas) == len(sem.sacudidas)
    assert [q["pontos"] for q in com.quedas] == [q["pontos"] for q in sem.quedas]
    assert all(com.seca(c["x"], c["y"]) for c in list(com.comidas.values()) + com.sumidas)


# ------------------------------------------------------------------ o motor
def test_a_agua_exige_o_controlador():
    with pytest.raises(ValueError, match="controlador"):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CM, cfg_sacudir=G.CS)
    with pytest.raises(ValueError, match="controlador"):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CM, cfg_sacudir=G.CS,
                   cfg_contrato=replace(CONFIG_CONTRATO, sensores=True))
    m = MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CM, cfg_sacudir=G.CS, cfg_contrato=CONFIG_CONTRATO_AGUA)
    assert m._solidos == solidos_da_agua(CM) and m.pet == m.mundo.ninho


def test_o_pet_solto_na_agua_cai_em_terra_sem_invadir_a_margem():
    m = MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CM, cfg_sacudir=G.CS, cfg_contrato=CONFIG_CONTRATO_AGUA)
    m.avancar(120)
    while m._estado.dormindo:
        m.avancar(7)
    r = CONFIG_CONTRATO_AGUA.r_pet
    for x, y in ((690, 300), (5, 5), (-40, 120), (1500, 50), (210, 372), (670, 250), (300, 200)):
        m.levar_pet(x, y)
        assert ct.bloqueio_em(*m.pet, r, m._solidos) is None, (x, y, m.pet)
    assert m.pet == (300, 200)                                        # em terra e longe da margem, fica onde foi solto
    assert m.mundo.seca(653, 250) and not m.mundo.seca(656, 250)
    m.levar_pet(653, 250)                                             # em terra, mas com o corpo sobre o rio: o centro da celula
    assert m.pet == centro_da_celula((653 // SUB, 250 // SUB), CM)


# ------------------------------------------------------------------ G-AG-5: o pet atravessa pela ponte
def test_o_controlador_atravessa_o_rio_pela_ponte():
    solidos, cc = solidos_da_agua(CM), CONFIG_CONTRATO_AGUA
    x, y = centro_da_celula((36, 16), CM)                             # a oeste do rio, longe das duas pontes
    tx, ty = centro_da_celula((48, 16), CM)                           # a leste, na mesma linha
    orientacao, pisou, chegou = 0, set(), False
    for _ in range(40):
        a = ct.controlar(x, y, tx, ty, SUB, CONFIG_PADRAO.intervalo_decisao_ticks, CM.velocidade, cc.r_pet, solidos, NX, NY, SUB,
                         cc.ticks_bloqueado, orientacao)
        for px, py in a.trajetoria:
            assert ct.bloqueio_em(px, py, cc.r_pet, solidos) is None
            pisou.add(AGUA_ILHA[py // SUB][px // SUB])
        x, y, orientacao = a.x, a.y, a.orientacao
        if a.parou_por == "chegou":
            chegou = True
            break
    assert chegou and x > 44 * SUB and pisou == {TERRA, PONTE}


# ------------------------------------------------------------------ G-AG-2 e o gabarito
def test_o_gabarito_do_ts_esta_em_dia_e_as_vidas_passam_nos_gates():
    gerado = G.gerar()                                                # o `conferir` de cada vida falha alto se algo ficou na agua
    texto = json.dumps(gerado, sort_keys=True, separators=(",", ":")) + "\n"
    assert texto == G.ARQUIVO.read_text(encoding="utf-8")
    assert gerado["config"]["mundo"]["layout"]["nome"] == "mvp_agua" and gerado["config"]["contrato"]["controlador"] is True
    for v in gerado["vidas"]:
        c = v["conferido"]
        assert c["cruzou_pela_ponte"] >= 1 and all(n >= 1 for n in c["tirados_da_agua"].values())
        assert c["rolagens_paradas_na_margem"] >= 1 and not any(e["tipo"] in ("deixar_bola", "sacudir_arvore") for e in v["log"])


def test_a_ilha_com_arvores_passa_nos_gates_com_a_bola_e_a_sacudida():
    """o mesmo roteiro na ilha com arvores (o que o TS de hoje nao roda): a bola posta pelo dono na agua e as arvores sacudidas"""
    m, pedidos = G.viver(202, CM, com_arvores=True)
    c = G.conferir(m, pedidos)
    assert c["cruzou_pela_ponte"] >= 1
    assert sum(p["pedido"] != p["ficou"] for p in pedidos["bola"]) >= 1
    assert sum(s["caiu"] is not None for s in m.mundo.sacudidas) >= 3


def test_o_replay_refaz_a_vida_com_agua():
    """o instinto no layout com agua, com a comida, a bola e o pet postos na agua pelo dono: o replay do log da a mesma vida"""
    fp, fm = fabricas_mundo(CM, politica_fabrica=lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO), cfg_sacudir=G.CS,
                            cfg_contrato=CONFIG_CONTRATO_AGUA)
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 303)
    for i in range(40):
        m.avancar(61)
        m.deixar_comida("racao", *G.PONTOS_COMIDA[i % len(G.PONTOS_COMIDA)])
        m.deixar_bola(*G.PONTOS_BOLA[i % len(G.PONTOS_BOLA)])
        if not m._estado.dormindo:
            m.levar_pet(*G.PONTOS_LEVAR[i % len(G.PONTOS_LEVAR)])
    assert m.levadas and m.contrato_decisoes
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 303, fabrica_motor=fm)
    assert r.pet == m.pet and r.mundo.resumo() == m.mundo.resumo() and r.contrato_decisoes == m.contrato_decisoes
    assert r.estado() == m.estado()
