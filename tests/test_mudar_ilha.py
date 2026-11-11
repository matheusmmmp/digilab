"""A troca de ilha (docs/TAREFA_V3_ILHA_AGUA.md, IA4; a IA-4 do Matheus: os pets vivos passam para a ilha nova): o evento `mudar_ilha`
leva o mundo do pet, no meio da vida, do layout de hoje (sem agua) para o mesmo layout com agua.

- o formato do evento no log (o nome do layout: minusculas, digitos e sublinhado);
- a troca no Mundo: a comida e a bola na agua vao para a terra mais perto, nenhum fluxo de acaso anda, vale uma vez so;
- a troca no motor: o contrato passa a ser o do destino, o pet na agua cai em terra, o destino pendente se perde; nao e contato;
- sem o evento nada muda (os gabaritos de antes sao conferidos pelos testes deles);
- o replay refaz a vida com a troca, e o gabarito do G-PAR do TS (web/app/test/gabaritos/mudar_ilha_python.json) esta em dia.
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

import exportar_gabarito_ilha_agua as ga  # noqa: E402
import exportar_gabarito_mudar_ilha as G  # noqa: E402

from digilab import contrato as ct  # noqa: E402
from digilab.config import (CONFIG_CONTRATO, CONFIG_CONTRATO_AGUA, CONFIG_MUNDO_ILHA, CONFIG_MUNDO_ILHA_AGUA, CONFIG_MUNDO_MVP,  # noqa: E402
                            CONFIG_MUNDO_MVP_AGUA, CONFIG_PADRAO, ILHAS_DE_TROCA, LAYOUT_MUNDO_MVP_AGUA)
from digilab.events import Evento, ler_mudar_ilha, mudar_ilha  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import Mundo, MotorMundo, fabricas_mundo, reproduzir_mundo, solidos_da_agua  # noqa: E402

ANTES, DEPOIS = CONFIG_MUNDO_MVP, CONFIG_MUNDO_MVP_AGUA


def _motor(semente: int = 101, cm=ANTES, **kw) -> MotorMundo:
    return MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, semente, cfg_mundo=cm, **kw)


# ------------------------------------------------------------------ o formato do log
def test_o_evento_guarda_o_nome_do_layout_e_so_aceita_a_forma_canonica():
    e = mudar_ilha(9, "mvp_agua")
    assert (e.tick, e.tipo, e.valor) == (9, "mudar_ilha", "mvp_agua") and ler_mudar_ilha(e) == "mvp_agua"
    for ruim in ("", "Mvp_agua", "mvp agua", "mvp-agua", "a" * 33, "água", 5, None, "mvp|agua"):
        with pytest.raises(ValueError, match="mudar_ilha"):
            mudar_ilha(9, ruim)
        with pytest.raises(ValueError):
            ler_mudar_ilha(Evento(tick=9, tipo="mudar_ilha", valor=ruim))
    with pytest.raises(ValueError, match="nao e mudar_ilha"):
        ler_mudar_ilha(Evento(tick=9, tipo="levar_pet", valor="mvp_agua"))


def test_os_destinos_sao_o_layout_de_antes_com_a_agua_e_o_controlador():
    assert set(ILHAS_DE_TROCA) == {"mvp_agua", "ilha_agua"}
    for antes, depois in ((CONFIG_MUNDO_MVP, CONFIG_MUNDO_MVP_AGUA), (CONFIG_MUNDO_ILHA, CONFIG_MUNDO_ILHA_AGUA)):
        layout, contrato = ILHAS_DE_TROCA[depois.layout.nome]
        assert layout == depois.layout and replace(layout, nome=antes.layout.nome) == antes.layout
        assert contrato == CONFIG_CONTRATO_AGUA and contrato.controlador


# ------------------------------------------------------------------ a troca no Mundo
def test_a_troca_tira_a_comida_e_a_bola_da_agua_e_nao_mexe_no_acaso():
    com, sem = Mundo(ANTES, 202), Mundo(ANTES, 202)
    for w in (com, sem):
        w.atualizar(60)
        w.deixar_comida("racao", 670, 250, 60)                         # sera o rio
        w.deixar_comida("racao", 300, 240, 60)                         # terra
        w.deixar_bola(5, 5, 60)                                        # sera o mar
    assert com.resumo() == sem.resumo()
    reg = com.trocar_layout(LAYOUT_MUNDO_MVP_AGUA, 60)
    assert com.cmf == DEPOIS and com.secas is not None and com.troca_ilha is reg
    a, b = list(com.comidas.values())
    assert (a["x"], a["y"]) == Mundo(DEPOIS, 1).em_terra(670, 250) != (670, 250) and (b["x"], b["y"]) == (300, 240)
    assert reg == {"tick": 60, "de": "mvp", "para": "mvp_agua", "comidas": [{"id": a["id"], "de": [670, 250], "para": [a["x"], a["y"]]}],
                   "bola": {"de": [5, 5], "para": list(com.em_terra(5, 5))}}
    assert com.bola == {"x0": reg["bola"]["para"][0], "y0": reg["bola"]["para"][1], "x1": reg["bola"]["para"][0],
                        "y1": reg["bola"]["para"][1], "t0": 60, "d": 0} and com.seca(*com.bola_em(60))
    # nenhum fluxo de acaso andou, e so o resumo com a troca difere
    assert com.resumo()["rngs"] == sem.resumo()["rngs"] and "troca_ilha" in com.resumo() and "troca_ilha" not in sem.resumo()


def test_a_bola_que_rolava_para_onde_esta_na_troca():
    w = Mundo(ANTES, 303)
    w.atualizar(60)
    w.deixar_bola(300, 240, 60)
    r = w.rolar_bola(60)
    meio = w.bola_em(62)
    assert meio != tuple(r["para"]) and meio != (300, 240)
    w.atualizar(62)                                                    # (o motor atualiza o mundo ate o tick antes da troca)
    reg = w.trocar_layout(LAYOUT_MUNDO_MVP_AGUA, 62)
    assert reg["bola"] == {"de": list(meio), "para": list(w.em_terra(*meio))} and w.bola_em(999) == w.em_terra(*meio)


def test_a_troca_vale_uma_vez_e_so_para_o_mesmo_layout_com_agua():
    w = Mundo(ANTES, 101)
    w.atualizar(10)
    with pytest.raises(RuntimeError, match="atualizado"):
        w.trocar_layout(LAYOUT_MUNDO_MVP_AGUA, 11)
    with pytest.raises(ValueError, match="so muda a agua"):
        w.trocar_layout(CONFIG_MUNDO_ILHA_AGUA.layout, 10)             # outro layout (as arvores, o ninho noutro lugar)
    with pytest.raises(ValueError, match="nao tem agua"):
        w.trocar_layout(replace(ANTES.layout, nome="outro_sem_agua"), 10)
    w.trocar_layout(LAYOUT_MUNDO_MVP_AGUA, 10)
    with pytest.raises(ValueError, match="ja tem agua"):
        w.trocar_layout(LAYOUT_MUNDO_MVP_AGUA, 10)
    ja = Mundo(DEPOIS, 101)                                            # o mundo que ja nasceu com agua
    ja.atualizar(10)
    with pytest.raises(ValueError, match="ja tem agua"):
        ja.trocar_layout(LAYOUT_MUNDO_MVP_AGUA, 10)


# ------------------------------------------------------------------ a troca no motor
def test_o_motor_passa_para_a_agua_com_o_controlador_e_o_pet_cai_em_terra():
    m = _motor()
    m.avancar(120)
    while m._estado.dormindo:
        m.avancar(7)
    m.levar_pet(670, 250)                                              # sera o rio
    assert m.cct == CONFIG_CONTRATO and m.mundo.secas is None and m.pet == (670, 250)
    n, tick = m._n_eventos, m._estado.tick
    estado = m.estado()
    m.mudar_ilha("mvp_agua")
    assert m.cmf == DEPOIS and m.mundo.cmf == DEPOIS and m.cct == CONFIG_CONTRATO_AGUA and m._solidos == solidos_da_agua(DEPOIS)
    assert ct.bloqueio_em(*m.pet, m.cct.r_pet, m._solidos) is None and m.pet != (670, 250) and m._pendente is None
    assert m.mundo.troca_ilha["pet"] == {"de": [670, 250], "para": list(m.pet)}
    assert list(m.log)[-1] == mudar_ilha(tick, "mvp_agua") and m._n_eventos == n + 1
    sem_mundo = lambda e: {k: v for k, v in e.items() if k != "mundo"}  # noqa: E731
    assert sem_mundo(m.estado()) == sem_mundo(estado) and m._estado.tick == tick      # nao e contato nem cuidado: so o mundo muda
    assert m.estado()["mundo"] == {**estado["mundo"], "pet": m.pet}
    # dali em diante o pet anda pelo controlador e nunca entra na agua
    m.deixar_comida("racao", 760, 190)
    m.avancar(600)
    assert m.contrato_decisoes
    for d in m.contrato_decisoes:
        for x, y in d["trajetoria"] or ():
            assert ct.bloqueio_em(x, y, m.cct.r_pet, m._solidos) is None


def test_a_troca_vale_com_o_pet_dormindo_e_o_que_nao_vale_falha_alto_sem_ir_ao_log():
    m = _motor(202)
    while not m._estado.dormindo:
        m.avancar(7)
    n = len(m.log)
    for ruim, erro in (("ilha_que_nao_existe", "desconhecida"), ("ilha_agua", "so muda a agua"), ("Mvp", "invalido")):
        with pytest.raises(ValueError, match=erro):
            m.mudar_ilha(ruim)
    assert len(m.log) == n and m.mundo.secas is None and m.cct == CONFIG_CONTRATO
    m.mudar_ilha("mvp_agua")
    assert m._estado.dormindo and m.mundo.secas is not None
    with pytest.raises(ValueError):
        m.mudar_ilha("mvp_agua")                                       # a segunda troca
    assert len(m.log) == n + 1
    # com o contrato ja ligado, ou ja na agua, a troca nao vale
    with pytest.raises(ValueError, match="sem o contrato ligado"):
        _motor(101, cfg_contrato=replace(CONFIG_CONTRATO, sensores=True)).mudar_ilha("mvp_agua")
    with pytest.raises(ValueError, match="sem o contrato ligado"):
        _motor(101, DEPOIS, cfg_contrato=CONFIG_CONTRATO_AGUA).mudar_ilha("mvp_agua")


# ------------------------------------------------------------------ o replay e o gabarito
def test_o_replay_refaz_a_vida_com_a_troca_e_corta_antes_dela():
    fp, fm = fabricas_mundo(ANTES, politica_fabrica=lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO))
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 303)
    for i in range(40):
        m.avancar(61)
        m.deixar_comida("racao", *ga.PONTOS_COMIDA[i % len(ga.PONTOS_COMIDA)])
        if not m._estado.dormindo:
            m.levar_pet(*ga.PONTOS_LEVAR[i % len(ga.PONTOS_LEVAR)])
        if i == 11:
            m.mudar_ilha("mvp_agua")
    troca = m.mundo.troca_ilha
    assert troca is not None and m.contrato_decisoes
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 303, fabrica_motor=fm)
    assert r.pet == m.pet and r.mundo.resumo() == m.mundo.resumo() and r.contrato_decisoes == m.contrato_decisoes
    assert r.estado() == m.estado() and r.cmf == DEPOIS and r.cct == CONFIG_CONTRATO_AGUA
    # o replay cortado antes da troca e a vida de antes: sem agua e sem o contrato
    antes = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 303, fabrica_motor=fm, ate_tick=troca["tick"])
    assert antes.cmf == ANTES and antes.mundo.secas is None and antes.cct == CONFIG_CONTRATO and antes.mundo.troca_ilha is None


def test_o_gabarito_do_ts_esta_em_dia_e_as_vidas_passam_nos_gates():
    gerado = G.gerar()                                                 # o `conferir` de cada vida falha alto se algo ficou na agua
    texto = json.dumps(gerado, sort_keys=True, separators=(",", ":")) + "\n"
    assert texto == G.ARQUIVO.read_text(encoding="utf-8")
    assert [v["troca"]["dormindo"] for v in gerado["vidas"]] == [False, True]
    for v in gerado["vidas"]:
        assert v["conferido"]["cruzou_pela_ponte"] >= 1 and [e["tipo"] for e in v["log"]].count("mudar_ilha") == 1
        assert v["resumo"]["troca_ilha"]["para"] == "mvp_agua"
