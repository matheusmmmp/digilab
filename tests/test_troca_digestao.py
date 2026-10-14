"""A troca da digestao num tick (rede de si, etapa 2b; docs/TAREFA_V2_REDE_DE_SI.md; docs/PLANO_ANALISE_V2_REDE_DE_SI.md, secao 3, RS-3).

- Sem a troca pedida, o MotorCorpo de hoje (os gabaritos do corpo, na suite) e nenhuma chave nova no estado().
- A troca: no comeco do primeiro tick em ou depois do pedido, a taxa_digestao do corpo passa a lenta, o grafo e refeito com ela e
  conferido, e a troca fica registrada; antes do tick a vida e a mesma de sem a troca; depois, a digestao por tick nao passa da lenta.
- G1: o replay pela mesma fabrica refaz a troca. As falhas altas.
- A bancada: o P1-c-lenta roda (sem o no), troca no tick da bancada (o fim do dia dias // 2), e os outros bracos nao trocam.
Sementes: so as dos testes (101, 202).
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_PADRAO, CONFIG_TROCA_DIGESTAO, TICKS_POR_DIA, ConfigTrocaDigestao  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402

LENTA = CONFIG_TROCA_DIGESTAO.taxa_lenta


def _cfg(**kw):
    c = {"dias": 2, "orcamento": 32, "donos": ["atencioso"], "bracos": ["P1-c-lenta", "P1-c"], "mundos": ["bola"], "sementes": [101],
         "sonda": {"estados": 5, "amostras": 5, "semente": 101}, "bootstrap": {"reamostragens": 50, "semente": 1, "nivel": 0.95}}
    c.update(kw)
    return c


def _banc():
    return bv.bancada_da_config(_cfg())


def _motor(banc, braco="P1-c-lenta", s=101, **troca):
    espec = bv.EspecVida(braco=braco, semente=s, dono="atencioso", mundo="bola")
    fm = banc.fabrica_motor(espec)
    return fm(banc.politica(espec, CONFIG_PADRAO), CONFIG_PADRAO, s)


# ------------------------------------------------------------------ o motor
def test_a_config_da_troca():
    assert LENTA == 450000 // 8
    with pytest.raises(ValueError):
        ConfigTrocaDigestao(taxa_lenta=0)


def test_sem_a_troca_nada_novo_no_estado():
    m = _motor(_banc(), "P1-c")
    assert m._troca_pedida is None and m.troca_digestao is None and "troca_digestao" not in m.estado()


def test_a_troca_no_tick_com_o_grafo_refeito():
    banc = _banc()
    m = _motor(banc)
    T = banc.tick_troca_digestao
    assert T == TICKS_POR_DIA and m._troca_pedida == (T, LENTA)
    assert m.estado()["troca_digestao"] is None
    taxa_antes = m.cc.taxa_digestao
    m.avancar(T)
    assert m.troca_digestao is None and m.corpo.cc.taxa_digestao == taxa_antes      # o tick T ainda nao comecou
    m.avancar(1)
    assert m.troca_digestao == {"tick": T, "tick_pedido": T, "de": taxa_antes, "para": LENTA}
    assert m.cc.taxa_digestao == m.corpo.cc.taxa_digestao == LENTA
    reacao = next(r for r in m.corpo.grafo.reacoes if r.nome == "digestao")
    assert reacao.taxa == LENTA and m.corpo.relato_grafo is not None
    assert m.estado()["troca_digestao"]["tick"] == T


def test_depois_da_troca_a_digestao_nao_passa_da_lenta():
    banc = _banc()
    m = _motor(banc)
    m.avancar(banc.tick_troca_digestao + 1)
    vistos = []
    for _ in range(4):
        m.observar(AcaoUsuario.ALIMENTAR)
        for _ in range(30):
            alimento = m.corpo.q["alimento"]
            m.avancar(1)
            vistos.append((alimento, m.corpo.digerido_no_tick))
    assert all(d <= LENTA for _, d in vistos)
    assert any(d == LENTA for _, d in vistos)                       # a lenta morde: sobra comida no estomago de um tick para outro
    assert any(a > LENTA for a, _ in vistos)


def test_antes_da_troca_a_vida_e_a_de_sem_a_troca():
    banc = _banc()
    for s in (101, 202):
        lenta = banc.vida(bv.EspecVida(braco="P1-c-lenta", semente=s, dono="atencioso", mundo="bola"))
        hoje = banc.vida(bv.EspecVida(braco="P1-c", semente=s, dono="atencioso", mundo="bola"))
        T = banc.tick_troca_digestao
        antes = lambda m: [e for e in m.motor.log if e.tick < T]  # noqa: E731
        assert antes(lenta) == antes(hoje)
        assert [a for a in lenta.motor.acoes_recentes(10**9) if a[0] < T] == [a for a in hoje.motor.acoes_recentes(10**9) if a[0] < T]
        assert lenta.motor.troca_digestao["tick"] == T and hoje.motor.troca_digestao is None
        assert lenta.motor.estado()["corpo"] != hoje.motor.estado()["corpo"]      # depois, a vida muda


def test_g1_o_replay_refaz_a_troca():
    banc = _banc()
    for s in (101, 202):
        v = banc.vida(bv.EspecVida(braco="P1-c-lenta", semente=s, dono="atencioso", mundo="bola"))
        assert v.motor.estado()["troca_digestao"]["tick"] == banc.tick_troca_digestao
        banc.conferir_replay(v)                                     # do texto do log, o estado() com a troca incluido, bit a bit


def test_as_falhas_altas():
    banc = _banc()
    espec = bv.EspecVida(braco="P1-c", semente=101, dono="atencioso", mundo="bola")
    pol = banc.politica(espec, CONFIG_PADRAO)
    corpo = banc.cfg_corpo_de(espec)
    from digilab.ambiente import MotorAmbiente
    from digilab.motor_corpo import com_corpo
    from digilab.temperamento import NEUTRO

    def m(**kw):
        return com_corpo(MotorAmbiente)(pol, CONFIG_PADRAO, 101, NEUTRO, "brasa", obediencia_desligada=True, cfg_bola=banc.cfg_bola, **kw)

    with pytest.raises(ValueError, match="digestao"):
        m(cfg_corpo=replace(corpo, digestao=False, vida=False, drives_novos=False, gestos=False, metabolismo=False),
          troca_digestao=(10, LENTA))
    with pytest.raises(ValueError, match="mesma taxa"):
        m(cfg_corpo=corpo, troca_digestao=(10, corpo.taxa_digestao))
    for ruim in ((0, LENTA), (10, 0), (10.0, LENTA)):
        with pytest.raises(ValueError):
            m(cfg_corpo=corpo, troca_digestao=ruim)


# ------------------------------------------------------------------ a bancada
def test_o_p1_c_lenta_roda_na_bancada_e_so_ele_troca():
    banc = _banc()
    assert "digestao_lenta" not in bv.NOS_PENDENTES and bv.braco_de("P1-c-lenta").digestao_lenta
    bv.validar_config(_cfg())
    for braco in ("P1-c-lenta", "P1-c"):
        v = banc.vida(bv.EspecVida(braco=braco, semente=101, dono="atencioso", mundo="bola"))
        esperado = banc.tick_troca_digestao if braco == "P1-c-lenta" else None
        banc.conferir_troca_digestao(v, v.motor, esperado)
    v = banc.vida(bv.EspecVida(braco="P1-c", semente=101, dono="atencioso", mundo="bola"))
    with pytest.raises(RuntimeError, match="nao foi a pedida"):
        banc.conferir_troca_digestao(v, v.motor, banc.tick_troca_digestao)


def test_a_chave_da_config_troca_a_taxa_lenta():
    b = bv.bancada_da_config(_cfg(digestao_lenta={"taxa_lenta": 450000 // 4}))
    assert b.cfg_troca_digestao.taxa_lenta == 450000 // 4
    v = b.vida(bv.EspecVida(braco="P1-c-lenta", semente=101, dono="atencioso", mundo="bola"))
    assert v.motor.troca_digestao["para"] == 450000 // 4
