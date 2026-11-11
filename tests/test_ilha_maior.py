"""A ida para a ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12, IG4): o evento `mudar_ilha` para um destino de outro tamanho.

- Os destinos de outro tamanho (`ILHAS_MAIORES`): a ilha grande, a partir do mundo do produto de hoje, sem agua ou com ela.
- No Mundo: tudo o que tem posicao anda o deslocamento do ninho (IG-7); o que cai em celula fechada ou fora do mapa vai para a terra; o
  ninho e o comedouro passam a ser os do layout novo; nenhum fluxo de acaso anda; vale uma vez.
- No motor: vale com o controlador ja ligado (a ilha com agua de antes) e com o pet dormindo; o que nao vale falha alto sem ir ao log.
- O replay refaz a vida, e o log cortado antes da ida e a vida de antes.
- O gabarito do G-PAR do TS (web/app/test/gabaritos/ilha_maior_python.json) esta em dia byte a byte.
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

import exportar_gabarito_ilha_maior as G  # noqa: E402

from digilab.config import (CONFIG_CONTRATO_AGUA, CONFIG_MUNDO_GRANDE, CONFIG_MUNDO_ILHA, CONFIG_MUNDO_MVP,  # noqa: E402
                            CONFIG_MUNDO_MVP_AGUA, CONFIG_PADRAO, CONFIG_SACUDIR_LIGADA, ILHAS_DE_TROCA, ILHAS_MAIORES)
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import Mundo, centro_da_celula, fabricas_mundo, reproduzir_mundo  # noqa: E402

GRANDE = CONFIG_MUNDO_GRANDE
NOME = GRANDE.layout.nome
SUB = GRANDE.sub
DX, DY = ((GRANDE.layout.ninho[i] - CONFIG_MUNDO_MVP.layout.ninho[i]) * SUB for i in (0, 1))


def _fabricas(cm, contrato=None, **extras):
    return fabricas_mundo(cm, politica_fabrica=lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO), cfg_contrato=contrato, **extras)


def _motor(cm=CONFIG_MUNDO_MVP, contrato=None, semente=101, **extras):
    fp, fm = _fabricas(cm, contrato, **extras)
    return fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)


def _ir(mundo: Mundo, tick: int = 0) -> dict:
    mundo.atualizar(tick)
    return mundo.trocar_para_maior(GRANDE.layout, *ILHAS_MAIORES[NOME], tick)


def test_o_destino_e_a_ilha_grande_a_partir_do_mundo_do_produto():
    assert list(ILHAS_MAIORES) == [NOME] and NOME in ILHAS_DE_TROCA
    nx, ny, origens = ILHAS_MAIORES[NOME]
    assert (nx, ny) == (GRANDE.celulas_x, GRANDE.celulas_y) == (128, 60)
    assert origens == (CONFIG_MUNDO_MVP.layout, CONFIG_MUNDO_MVP_AGUA.layout)
    assert ILHAS_DE_TROCA[NOME] == (GRANDE.layout, CONFIG_CONTRATO_AGUA)
    assert (DX, DY) == (16 * SUB, 15 * SUB)


def test_tudo_anda_o_deslocamento_do_ninho_e_o_acaso_nao_anda():
    m = Mundo(CONFIG_MUNDO_MVP, 101)
    livre, no_carro, no_canto = (300, 240), G.SOB_O_CARRO, (1000, 470)       # o canto sudeste cai em terra livre? o teste confere abaixo
    ids = [m.deixar_comida("racao", *p, 0)["id"] for p in (livre, no_carro, no_canto)]
    acaso = (m.rng_arvores.getstate(), m.rng_bola.getstate())
    bola = m.bola_em(0)
    reg = _ir(m)
    assert (m.rng_arvores.getstate(), m.rng_bola.getstate()) == acaso
    assert m.cmf == GRANDE and m.secas is not None and reg is m.troca_maior and m.troca_ilha is None
    assert reg["de"] == "mvp" and reg["para"] == NOME and reg["deslocamento"] == [DX, DY]
    assert m.ninho == centro_da_celula(GRANDE.layout.ninho, GRANDE) and m.comedouro == centro_da_celula(GRANDE.layout.comedouro, GRANDE)
    c = m.comidas
    assert (c[ids[0]]["x"], c[ids[0]]["y"]) == (livre[0] + DX, livre[1] + DY)                    # em terra livre: exatamente la
    assert (c[ids[1]]["x"], c[ids[1]]["y"]) != (no_carro[0] + DX, no_carro[1] + DY)              # em cima do carro: para a terra
    assert all(m.seca(k["x"], k["y"]) for k in c.values())
    assert [k["id"] for k in reg["comidas"]] == ids and all(k["de"] != k["para"] for k in reg["comidas"])
    assert reg["bola"]["de"] == list(bola) and m.seca(*m.bola_em(0)) and m.bola["d"] == 0
    assert "troca_maior" in m.resumo() and "troca_ilha" not in m.resumo()


def test_a_ida_vale_uma_vez_e_so_a_partir_do_mundo_do_produto():
    m = Mundo(CONFIG_MUNDO_MVP, 101)
    _ir(m)
    with pytest.raises(ValueError, match="uma vez"):
        _ir(m)
    with pytest.raises(ValueError, match="nao recebe"):
        _ir(Mundo(CONFIG_MUNDO_ILHA, 101, arvores_na_casa=True))                                # o mundo com arvores
    with pytest.raises(ValueError, match="nao recebe"):
        _ir(Mundo(GRANDE, 101))
    with pytest.raises(RuntimeError, match="atualizado"):
        Mundo(CONFIG_MUNDO_MVP, 101).trocar_para_maior(GRANDE.layout, *ILHAS_MAIORES[NOME], 5)
    # depois da troca para a agua, a ida ainda vale (o pet v21 que ja tinha passado)
    a = Mundo(CONFIG_MUNDO_MVP, 101)
    a.atualizar(0)
    a.trocar_layout(CONFIG_MUNDO_MVP_AGUA.layout, 0)
    _ir(a)
    assert a.troca_ilha is not None and a.troca_maior is not None and a.cmf == GRANDE


@pytest.mark.parametrize("cm, contrato", [(CONFIG_MUNDO_MVP, None), (CONFIG_MUNDO_MVP_AGUA, CONFIG_CONTRATO_AGUA)])
def test_o_motor_vai_para_a_ilha_grande_do_mundo_sem_agua_e_do_mundo_com_agua(cm, contrato):
    m = _motor(cm, contrato)
    m.avancar(600)
    m.deixar_comida("racao", 300, 240)
    assert not m._estado.dormindo
    de, n = m.pet, len(m.log)
    m.mudar_ilha(NOME)
    assert len(m.log) == n + 1 and m.log[n].tipo == "mudar_ilha"
    assert m.cmf == GRANDE == m.mundo.cmf and m.cct == CONFIG_CONTRATO_AGUA and m.contrato_decisoes == [] and m.orientacao == 0
    assert m.mundo.troca_maior["pet"]["de"] == list(de) and m.mundo.seca(*m.pet)
    assert m.mundo.troca_maior["pet"]["para"] == list(m.pet)
    assert abs(m.pet[0] - de[0] - DX) <= 2 * SUB and abs(m.pet[1] - de[1] - DY) <= 2 * SUB      # o lugar dele, a menos do corpo
    # a vida segue na ilha grande: o dono poe a racao alem do mapa de antes, e o pet anda
    m.deixar_comida("racao", 1800, 700)
    m.avancar(600)
    assert m.contrato_decisoes and all(m.mundo.seca(c["x"], c["y"]) for c in m.mundo.comidas.values())
    with pytest.raises(ValueError, match="uma vez"):
        m.mudar_ilha(NOME)


def test_a_ida_vale_com_o_pet_dormindo_e_o_que_nao_vale_falha_alto_sem_ir_ao_log():
    m = _motor()
    m.avancar(1)
    while not m._estado.dormindo:
        m.avancar(30)
    antes = m.pet
    m.mudar_ilha(NOME)
    assert m._estado.dormindo and m.mundo.seca(*m.pet)
    assert abs(m.pet[0] - antes[0] - DX) <= 2 * SUB and abs(m.pet[1] - antes[1] - DY) <= 2 * SUB
    for ruim, extras in ((CONFIG_MUNDO_ILHA, {"cfg_sacudir": CONFIG_SACUDIR_LIGADA}), (GRANDE, {})):
        p = _motor(ruim, CONFIG_CONTRATO_AGUA if ruim is GRANDE else None, **extras)
        p.avancar(10)
        n = len(p.log)
        with pytest.raises(ValueError):
            p.mudar_ilha(NOME)
        assert len(p.log) == n


def test_o_replay_refaz_a_vida_com_a_ida_e_corta_antes_dela():
    fp, fm = _fabricas(CONFIG_MUNDO_MVP)
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 303)
    for i in range(12):
        m.avancar(61)
        m.deixar_comida("racao", 200 + 37 * i, 100 + 23 * i)
    corte = len(m.log)
    antes = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 303)
    for i in range(12):
        antes.avancar(61)
        antes.deixar_comida("racao", 200 + 37 * i, 100 + 23 * i)
    m.mudar_ilha(NOME)
    for i in range(12):
        m.avancar(61)
        m.deixar_comida("racao", 400 + 97 * i, 300 + 41 * i)
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 303, fabrica_motor=fm)
    assert r.pet == m.pet and r.mundo.resumo() == m.mundo.resumo() and r.estado() == m.estado() and r.cmf == GRANDE
    cortado = reproduzir_mundo(list(m.log)[:corte], fp, CONFIG_PADRAO, 303, fabrica_motor=fm)
    assert cortado.mundo.resumo() == antes.mundo.resumo() and cortado.estado() == antes.estado() and cortado.cmf == CONFIG_MUNDO_MVP


def test_o_gabarito_do_ts_esta_em_dia_e_as_vidas_passam_nos_gates():
    gerado = G.gerar()
    texto = json.dumps(gerado, sort_keys=True, separators=(",", ":")) + "\n"
    assert texto == G.ARQUIVO.read_text(encoding="utf-8")
    assert [v["comeco"]["mundo"] for v in gerado["vidas"]] == ["mvp", "mvp_agua", "mvp"]
    assert [len(v["comeco"]["trocas"]) for v in gerado["vidas"]] == [1, 1, 2]
    for v in gerado["vidas"]:
        assert v["ida"]["exatos"] >= 1 and v["ida"]["tirados"] >= 1 and v["conferido"]["cruzou_pela_ponte"] >= 1
        assert sum(e["tipo"] == "mudar_ilha" for e in v["log"]) == len(v["comeco"]["trocas"])
    assert replace(CONFIG_MUNDO_MVP_AGUA.layout, nome="mvp") == CONFIG_MUNDO_MVP.layout
