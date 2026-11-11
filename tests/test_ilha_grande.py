"""A ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG1): o mundo de 128 x 60 celulas, com as arvores e os marcos como celulas
fechadas.

- O mapa do config e o da figura aprovada (docs/pranchas/ilha-grande/mapa_proposto.txt), tem o tamanho do mundo e o mar em toda a borda.
- As celulas fechadas (a agua, a arvore, o marco) viram solidos, e so elas; o centro de toda celula livre serve ao corpo do pet.
- Toda a terra livre se alcanca a pe a partir do ninho; o ninho, o comedouro e a bola ficam em terra, nas regioes de sempre.
- As regioes sao as quatro de sempre, com as faixas dobradas, e cobrem o mapa.
- A racao, a bola e o pet postos em cima de uma arvore ou de um marco vao para a terra mais perto.
- As posicoes dos eventos valem ate o tamanho do mapa de cada mundo: o ponto alem de 1024 x 480 entra na ilha grande e falha alto no
  mundo de 64 x 30, antes de ir para o log.
- O gabarito do G-PAR do TS (web/app/test/gabaritos/ilha_grande_python.json) esta em dia byte a byte, e o replay refaz a vida.
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

import exportar_gabarito_ilha_grande as G  # noqa: E402

from digilab import contrato as ct  # noqa: E402
from digilab.config import (AGUA_DOCE, AGUA_ILHA_GRANDE, AGUA_MAR, ARVORE_FECHADA, CONFIG_CONTRATO_AGUA, CONFIG_MUNDO_GRANDE,  # noqa: E402
                            CONFIG_MUNDO_MVP, CONFIG_MUNDO_MVP_AGUA, CONFIG_PADRAO, ConfigMundo, MARCO_FECHADO, PONTE, TERRA)
from digilab.events import deixar_comida as evento_deixar_comida  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import (Mundo, celulas_secas, centro_da_celula, fabricas_mundo, regiao_de, reproduzir_mundo, solidos_da_agua,  # noqa: E402
                           tamanho_do_mapa)

CM = CONFIG_MUNDO_GRANDE
NX, NY, SUB = CM.celulas_x, CM.celulas_y, CM.sub
FIGURA = RAIZ / "docs" / "pranchas" / "ilha-grande" / "mapa_proposto.txt"


def _fabricas(cm=CM):
    return fabricas_mundo(cm, politica_fabrica=lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO), cfg_contrato=CONFIG_CONTRATO_AGUA)


def test_o_mapa_e_o_da_figura_tem_o_tamanho_do_mundo_e_o_mar_em_toda_a_borda():
    assert list(AGUA_ILHA_GRANDE) == FIGURA.read_text(encoding="utf-8").split()
    assert (NX, NY, SUB) == (128, 60, 16) and tamanho_do_mapa(CM) == (2048, 960)
    assert len(AGUA_ILHA_GRANDE) == NY and all(len(l) == NX for l in AGUA_ILHA_GRANDE)
    assert {c for l in AGUA_ILHA_GRANDE for c in l} == {AGUA_MAR, AGUA_DOCE, TERRA, PONTE, ARVORE_FECHADA, MARCO_FECHADO}
    assert set(AGUA_ILHA_GRANDE[0]) == set(AGUA_ILHA_GRANDE[-1]) == {AGUA_MAR}
    assert all(l[0] == l[-1] == AGUA_MAR for l in AGUA_ILHA_GRANDE)
    # so os dois tamanhos decididos existem
    for outro in ({"celulas_x": 96, "celulas_y": 48}, {"sub": 32}, {"celulas_x": 128, "celulas_y": 60, "sub": 8}):
        with pytest.raises(ValueError, match="64 x 30"):
            ConfigMundo(ligada=True, **outro)


def test_a_ilha_grande_tem_mais_de_tres_vezes_a_terra_de_hoje_com_arvores_e_marcos():
    livres, hoje = sum(celulas_secas(CM)), sum(celulas_secas(CONFIG_MUNDO_MVP_AGUA))
    assert livres > 3 * hoje
    assert sum(l.count(ARVORE_FECHADA) for l in AGUA_ILHA_GRANDE) >= 60
    assert sum(l.count(MARCO_FECHADO) for l in AGUA_ILHA_GRANDE) == 3 * 2 + 2 * 2 + 1 + 2 * 3 + 1  # o carro, a lata, a geladeira, o trilho e a TV
    assert sum(l.count(PONTE) for l in AGUA_ILHA_GRANDE) == 3 * 4                                # tres pontes de 2 x 2


def test_os_solidos_cobrem_o_que_e_fechado_e_so_isso():
    secas, solidos = celulas_secas(CM), solidos_da_agua(CM)
    assert all(s.categoria == "obstaculo" and s.colide and not s.alto for s in solidos)
    for cy in range(NY):
        for cx in range(NX):
            x, y = centro_da_celula((cx, cy), CM)
            dentro = sum(ct.ponto_no_retangulo(x, y, s) for s in solidos)
            assert dentro == (0 if secas[cy * NX + cx] else 1), (cx, cy)
            assert secas[cy * NX + cx] == (AGUA_ILHA_GRANDE[cy][cx] in (TERRA, PONTE))
    assert ct.grade(NX, NY, SUB, CONFIG_CONTRATO_AGUA.r_pet, solidos) == secas


def test_as_regioes_cobrem_o_mapa_e_o_ninho_o_comedouro_e_a_bola_ficam_onde_ficavam():
    L = CM.layout
    assert [r[0] for r in L.regioes] == [r[0] for r in CONFIG_MUNDO_MVP.layout.regioes]
    assert L.regioes[0][1] == 0 and L.regioes[-1][2] == NX - 1
    assert all(L.regioes[i + 1][1] == L.regioes[i][2] + 1 for i in range(len(L.regioes) - 1))
    assert all((x0, x1 + 1) == (2 * a0, 2 * (a1 + 1)) for (_, x0, x1), (_, a0, a1) in zip(L.regioes, CONFIG_MUNDO_MVP.layout.regioes))
    mvp = CONFIG_MUNDO_MVP
    for nome in ("ninho", "comedouro", "bola_inicio"):
        ponto, de_hoje = getattr(L, nome), getattr(mvp.layout, nome)
        assert AGUA_ILHA_GRANDE[ponto[1]][ponto[0]] == TERRA, nome
        assert regiao_de(ponto[0] * SUB, CM) == regiao_de(de_hoje[0] * mvp.sub, mvp), nome
    assert L.arvores == ()                                            # a arvore fechada nao e a que da fruta


def test_toda_a_terra_livre_se_alcanca_a_pe_e_o_ninho_fechado_falha_alto():
    Mundo(CM, 101)                                                    # o layout de verdade passa (o Mundo confere e falha alto)
    cx, cy = CM.layout.ninho
    linhas = list(AGUA_ILHA_GRANDE)
    linhas[cy] = linhas[cy][:cx] + ARVORE_FECHADA + linhas[cy][cx + 1:]
    ruim = replace(CM, layout=replace(CM.layout, nome="grande_teste"))
    from digilab.config import AGUA_POR_LAYOUT
    AGUA_POR_LAYOUT["grande_teste"] = tuple(linhas)
    try:
        with pytest.raises(ValueError, match="ninho na agua"):
            Mundo(ruim, 101)
    finally:
        del AGUA_POR_LAYOUT["grande_teste"]


def test_o_banheiro_de_sempre_cai_no_mar_da_ilha_grande_e_falha_alto():
    from digilab.config import CONFIG_BANHEIRO_LIGADA
    from digilab.mundo import faixa_do_banheiro
    faixa_do_banheiro(CONFIG_BANHEIRO_LIGADA, CONFIG_MUNDO_MVP_AGUA)             # no mundo de hoje com agua, o banheiro fica em terra
    with pytest.raises(ValueError, match="celula fechada"):
        faixa_do_banheiro(CONFIG_BANHEIRO_LIGADA, CM)


def test_o_que_o_dono_poe_em_cima_da_arvore_ou_do_marco_vai_para_a_terra():
    fp, fm = _fabricas()
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    m.avancar(600)
    for ponto in (G.NA_ARVORE, G.NO_MARCO):
        antes = set(m.mundo.comidas)
        m.deixar_comida("racao", *ponto)
        (novo,) = set(m.mundo.comidas) - antes
        c = m.mundo.comidas[novo]
        assert (c["x"], c["y"]) != ponto and m.mundo.seca(c["x"], c["y"])
        m.deixar_bola(*ponto)
        assert m.mundo.seca(m.mundo.bola["x1"], m.mundo.bola["y1"])
        assert not m._estado.dormindo
        m.levar_pet(*ponto)
        assert m.pet != ponto and m.mundo.seca(*m.pet)


def test_a_posicao_do_evento_vale_ate_o_tamanho_do_mapa_de_cada_mundo():
    longe = (1800, 700)                                               # dentro da ilha grande, fora do mapa de 64 x 30
    fp, fm = _fabricas()
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    m.deixar_comida("racao", *longe)
    assert m.log[len(m.log) - 1].tipo == "deixar_comida"
    with pytest.raises(ValueError, match="fora do mapa"):
        m.deixar_comida("racao", 2048, 10)
    # no mundo de 64 x 30 o mesmo ponto falha alto, e nada vai para o log
    fp, fm = _fabricas(CONFIG_MUNDO_MVP_AGUA)
    p = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    n = len(p.log)
    for chamada in (lambda: p.deixar_comida("racao", *longe), lambda: p.deixar_bola(*longe)):
        with pytest.raises(ValueError, match="fora do mapa"):
            chamada()
    assert len(p.log) == n
    with pytest.raises(ValueError, match="fora do mapa"):
        evento_deixar_comida(0, "racao", *longe)                      # quem nao passa o mapa continua no de 64 x 30


def test_o_gabarito_do_ts_esta_em_dia_e_as_vidas_passam_nos_gates():
    gerado = G.gerar()                                                # o `conferir` de cada vida falha alto se algo ficou onde nao pode
    texto = json.dumps(gerado, sort_keys=True, separators=(",", ":")) + "\n"
    assert texto == G.ARQUIVO.read_text(encoding="utf-8")
    assert gerado["config"]["mundo"]["layout"]["nome"] == "grande" and gerado["config"]["contrato"]["controlador"] is True
    assert (gerado["config"]["mundo"]["celulas_x"], gerado["config"]["mundo"]["celulas_y"]) == (128, 60)
    for v in gerado["vidas"]:
        c = v["conferido"]
        assert c["cruzou_pela_ponte"] >= 1 and all(n >= 1 for n in c["tirados_da_agua"].values())
        assert all(n >= 1 for por_tipo in c["tirados_da_arvore_e_do_marco"].values() for n in por_tipo.values())


def test_o_replay_refaz_a_vida_na_ilha_grande():
    fp, fm = _fabricas()
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 303)
    for i in range(40):
        m.avancar(61)
        m.deixar_comida("racao", *G.PONTOS_COMIDA[i % len(G.PONTOS_COMIDA)])
        m.deixar_bola(*G.PONTOS_COMIDA[(i + 3) % len(G.PONTOS_COMIDA)])
        if not m._estado.dormindo:
            m.levar_pet(*G.PONTOS_LEVAR[i % len(G.PONTOS_LEVAR)])
    assert m.levadas and m.contrato_decisoes
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 303, fabrica_motor=fm)
    assert r.pet == m.pet and r.mundo.resumo() == m.mundo.resumo() and r.contrato_decisoes == m.contrato_decisoes
    assert r.estado() == m.estado()
