"""V2, N3 (docs/PLANO_ANALISE_V2_N3.md): a fonte "consequencia" (P1) na bancada.

Gates: G2 (com a fonte desligada, a vida do P1 e a do P0 byte a byte), G1 (replay bit a bit do P1 e do acoplado P1 <- P0), o sinal
(reducao do deficit de fome, higiene e energia pela propria acao, janela imediata, inteiro) e nada do dono chegando ao P1. Sementes:
so as dos testes (101...505)."""

import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, ConfigConsequencia  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import (PARAMETROS_CONSEQUENCIA_N3, deficit_homeostatico, sinal_homeostatico,  # noqa: E402
                                    validar_parametros_consequencia)
from digilab.policy import Observacao, Transicao, efeito_da_acao_do_pet  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (101, 202, 303, 404, 505)
DIAS, ORC = 3, 48
S = CONFIG_LOBOS_APRENDIZ.escala
BANCADA = bv.Bancada(DIAS, ORC)


def _transicao(acao: AcaoPet, **kw) -> Transicao:
    e = Estado(**kw)
    depois = efeito_da_acao_do_pet(e, acao, CONFIG_PADRAO, CONFIG_PADRAO.intervalo_decisao_ticks)
    return Transicao(Observacao.de_estado(e), acao, Observacao.de_estado(depois))


# ------------------------------------------------------------------ o sinal


def test_parametros_e_engine():
    validar_parametros_consequencia()
    assert all(s == "PROPOSTO" for s, _ in PARAMETROS_CONSEQUENCIA_N3.values())
    assert CONFIG_CONSEQUENCIA.drives == (0, 1, 2)
    assert sha256_engine() == ENGINE_SHA256_V0


def test_deficit_e_inteiro_quadratico_e_so_dos_drives():
    assert deficit_homeostatico((1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0), (0, 1, 2), S) == 0
    assert deficit_homeostatico((0.5, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0), (0, 1, 2), S) == (S // 2) ** 2
    # o humor (indice 3) e a saude (4) nao entram
    assert deficit_homeostatico((1.0, 1.0, 1.0, 0.1, 0.2, 0.0, 0.0, 0.0), (0, 1, 2), S) == 0
    with pytest.raises(ValueError):
        deficit_homeostatico((1.5, 1.0, 1.0, 0, 0, 0, 0, 0), (0, 1, 2), S)


def test_sinal_por_acao_janela_imediata():
    cc = ConfigConsequencia(ganho=16)
    comer_fome_alta = sinal_homeostatico(_transicao(AcaoPet.COMER, fome=0.3), S, cc)
    comer_fome_baixa = sinal_homeostatico(_transicao(AcaoPet.COMER, fome=0.9), S, cc)
    assert type(comer_fome_alta) is int and comer_fome_alta > comer_fome_baixa > 0      # reduzir deficit maior vale mais
    assert sinal_homeostatico(_transicao(AcaoPet.BRINCAR, energia=0.7), S, cc) < 0        # energia -0,02; humor fora
    assert sinal_homeostatico(_transicao(AcaoPet.EXPLORAR, energia=0.7), S, cc) < 0
    for a in (AcaoPet.DORMIR, AcaoPet.OCIOSO, AcaoPet.CHAMAR_ATENCAO, AcaoPet.EMBURRAR):
        assert sinal_homeostatico(_transicao(a, fome=0.4, energia=0.5), S, cc) == 0      # sem efeito imediato nos drives
    assert sinal_homeostatico(_transicao(AcaoPet.COMER, fome=0.3), S, ConfigConsequencia(ganho=0)) == 0
    with pytest.raises(ValueError):
        sinal_homeostatico(_transicao(AcaoPet.COMER, fome=0.3), S, ConfigConsequencia(ganho=1.5))


def test_observar_consequencia_usa_a_regra_da_l1_e_nao_o_relogio_nem_os_chamados():
    obs = Observacao(vetor_estado=(0.4, 0.9, 0.7, 0.6, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)
    semente = next(s for s in range(50) if PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ).agir(obs, random.Random(s))
                   is AcaoPet.COMER)
    p = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    acao = p.agir(obs, random.Random(semente))
    t = Transicao(obs, acao, obs)
    p.observar_consequencia(t, S)
    assert p.pesos_mudaram() and p._pendentes == [] and p._tick_ultima_decisao == -1
    assert p._pesos["fome_moderada"][AcaoPet.COMER][0] > p._prior["fome_moderada"][AcaoPet.COMER][0]
    # a mesma regra: o mesmo f_S pela via do dono (elogio = +S) da o mesmo passo
    q = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    q.agir(obs, random.Random(semente))
    q.observar(t)
    q.receber_acao_dono(AcaoUsuario.ELOGIAR, 10)
    assert q._pesos["fome_moderada"] == p._pesos["fome_moderada"]
    # chamar_atencao pela consequencia nao vira chamado pendente
    semente2 = next(s for s in range(50) if PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ).agir(obs, random.Random(s))
                    is AcaoPet.CHAMAR_ATENCAO)
    r = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    r.agir(obs, random.Random(semente2))
    r.observar_consequencia(Transicao(obs, AcaoPet.CHAMAR_ATENCAO, obs), 0)
    assert r._pendentes == [] and not r.pesos_mudaram()


# ------------------------------------------------------------------ G2: fonte desligada = P0


@pytest.mark.parametrize("dono", DONOS)
def test_g2_p1_com_ganho_zero_e_o_p0_byte_a_byte(dono):
    b0 = bv.Bancada(DIAS, ORC, cfg_consequencia=ConfigConsequencia(ganho=0))
    for s in SEMENTES:
        p0 = BANCADA.vida(bv.EspecVida(dono, "P0", s))
        p1 = b0.vida(bv.EspecVida(dono, "P1", s))
        assert bv.resumo_motor(p0.motor) == bv.resumo_motor(p1.motor), (dono, s)
        assert not p1.motor.politica.cerebro.pesos_mudaram()


def test_g2_p1_com_o_aprendizado_desligado_e_o_p0():
    espec = bv.EspecVida("aleatorio", "P1", 303)
    pol = bv.PoliticaDoBraco(PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS_APRENDIZ, aprendizado_ligado=False)),
                             bv.BRACOS["P1"])
    v = simular_vida("aleatorio-P1", criar_dono("aleatorio"), pol, 303, DIAS, ORC, rotulo_dono="aleatorio",
                     fabrica_motor=BANCADA.fabrica_motor(espec))
    p0 = BANCADA.vida(bv.EspecVida("aleatorio", "P0", 303))
    assert bv.resumo_motor(v.motor) == bv.resumo_motor(p0.motor)


# ------------------------------------------------------------------ o P1 aprende, sem o dono; G1


def test_p1_aprende_sem_nada_do_dono_e_rejoga_bit_a_bit():
    for dono in ("atencioso", "aleatorio"):
        v = BANCADA.vida(bv.EspecVida(dono, "P1", 202))          # a bancada ja confere o replay (G1)
        pol = v.motor.politica
        cer = pol.cerebro
        assert pol.consequencias > 0 and cer.pesos_mudaram()
        mem = cer.memoria.para_dict()
        assert mem["elogios"] == mem["broncas"] == mem["cuidados"] == 0      # nada do dono chega ao aprendiz
        rec = cer.estado_interno()["aprendizado"]["recompensas"]
        assert rec["elogio"] == rec["repreensao"] == rec["latencia"] == rec["ignorado"] == 0 and rec["consequencia"] > 0
        assert pol.sinais_entregues == 0
        assert all(type(w) is int for g in cer._pesos.values() for ws in g.values() for w in ws)
        p0 = BANCADA.vida(bv.EspecVida(dono, "P0", 202))
        assert v.motor.acoes_recentes(10**9) != p0.motor.acoes_recentes(10**9)
        assert v.interacoes == ORC


def test_acoplado_p1_no_registro_do_p0_e_o_cuidado_controlado():
    p0 = BANCADA.vida(bv.EspecVida("aleatorio", "P0", 404))
    a = BANCADA.acoplar(p0, "P1", "nenhum")                      # confere o replay
    acoes_dono = lambda m: [(e.tick, str(e.valor)) for e in m.log if e.tipo == "acao_usuario"]  # noqa: E731
    assert acoes_dono(a.motor) == acoes_dono(p0.motor)           # o mesmo cuidado, nos mesmos ticks
    assert a.rotulo_braco == "P1<P0:nenhum" and a.motor.politica.cerebro.pesos_mudaram()


def test_rodar_com_p1_e_ganho_no_config(tmp_path):
    cfg = {"bracos": ["P0", "P1"], "donos": ["aleatorio"], "sementes": [101, 202], "dias": 2, "orcamento": 32,
           "sonda": {"estados": 20, "amostras": 20, "semente": 101},
           "bootstrap": {"reamostragens": 200, "semente": 1, "nivel": 0.95},
           "acoplados": [{"origem": "P0", "destino": "P1", "filtro": "nenhum"}], "consequencia": {"ganho": 8}}
    r = bv.rodar(cfg, tmp_path)
    assert {m["braco"] for m in r["medidas"].values()} == {"P0", "P1", "P1<P0:nenhum"}
    assert all(v.motor.politica.cfg_consequencia.ganho == 8 for v in r["vidas"].values())
    with pytest.raises(TypeError):
        bv.rodar({**cfg, "consequencia": {"ganho_errado": 1}}, tmp_path / "x")
