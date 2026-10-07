"""A chave `pesos_janela` no cerebro A (docs/PLANO_ANALISE_V2_CORPO_DRIVES.md, adendo 2, A2.4; o braco P1-cw): o peso de cada drive no
sinal pela falta media dele nas ultimas J decisoes, w_d = max(div_arred(S, 4), S - div_arred(3 * m_d, 4)), fixo dentro da decisao (o mesmo
no antes e no depois), com a janela andando depois dela.

G2: desligada, o sinal e a vida de hoje (os gabaritos de sempre, na suite; aqui, o sinal sem pesos e o de sempre e a vida com a chave
desligada e a mesma). Conta exata do peso e do sinal, a janela conferida decisao a decisao numa vida, os caminhos da E2, dos canais e do
mundo fisico com os mesmos pesos, e o G1. So as sementes dos testes.
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA, CONFIG_LOBOS, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigConsequencia  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar, fabricas_mundo, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import (PARAMETROS_CONSEQUENCIA_N3, PoliticaLobos, div_arred, pesos_da_janela, sinal_homeostatico,  # noqa: E402
                                    sinal_homeostatico_canais, sinal_homeostatico_fruta, sinal_por_canal)
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402

S = CONFIG_LOBOS.escala
CL_T3 = bv.cfg_lobos_do_ponto("T3")
CC = CONFIG_CONSEQUENCIA
CC_J = replace(CC, pesos_janela=True)
SEMENTES = (101, 202)                    # so dos testes


def _obs(fome=0.6, higiene=0.8, energia=0.7, humor=0.5) -> Observacao:
    return Observacao.de_estado(Estado(fome=fome, higiene=higiene, energia=energia, humor=humor))


# ------------------------------------------------------------------ a chave e o registro
def test_chave_desligada_por_padrao_e_registrada():
    assert CONFIG_CONSEQUENCIA.pesos_janela is False and CONFIG_CONSEQUENCIA.janela_pesos == 32
    assert {f.name for f in fields(ConfigConsequencia)} == set(PARAMETROS_CONSEQUENCIA_N3)
    assert PARAMETROS_CONSEQUENCIA_N3["pesos_janela"][0] == "PROPOSTO" and PARAMETROS_CONSEQUENCIA_N3["janela_pesos"][0] == "PROPOSTO"
    for ruim in (0, -1, 3.0):
        with pytest.raises(ValueError, match="janela_pesos"):
            ConfigConsequencia(janela_pesos=ruim)


# ------------------------------------------------------------------ o peso e o sinal, conta exata
def test_peso_pela_falta_media_conta_exata():
    drives = (0, 1, 2)
    assert pesos_da_janela([], drives, S) == {0: S, 1: S, 2: S}                       # janela vazia: o peso de hoje
    cheia = [{0: S, 1: 0, 2: S // 2} for _ in range(32)]
    assert pesos_da_janela(cheia, drives, S) == {0: S // 4, 1: S, 2: S - div_arred(3 * (S // 2), 4)}   # 256, 1024, 640
    assert pesos_da_janela([{0: 1, 1: 0, 2: 0}, {0: 2, 1: 0, 2: 0}], drives, S)[0] == S - div_arred(3 * div_arred(3, 2), 4)
    for _ in range(500):                                                               # o piso de um quarto nunca e furado
        rng = random.Random(_)
        w = pesos_da_janela([{0: rng.randrange(S + 1), 1: 0, 2: 0} for _ in range(rng.randrange(1, 40))], drives, S)
        assert S // 4 <= w[0] <= S


def test_sinal_ponderado_conta_exata():
    """fome 0,4 -> 0,7 (o resto igual), ganho 4: falta 614 -> 307, delta 282747. Peso de hoje: 1104. Peso de um quarto: o delta vira
    div_arred(256 x 282747, 1024) = 70687, e o sinal div_arred(4 x 70687, 1024) = 276"""
    t = Transicao(_obs(fome=0.4), lb.AcaoPet.COMER, _obs(fome=0.7))
    assert sinal_homeostatico(t, S, CC) == 1104
    assert sinal_homeostatico(t, S, CC, {0: S, 1: S, 2: S}) == 1104
    assert sinal_homeostatico(t, S, CC, {0: S // 4, 1: S, 2: S}) == div_arred(4 * div_arred(256 * 282747, 1024), 1024) == 276
    assert sinal_homeostatico(t, S, CC, {0: S, 1: S // 4, 2: S // 4}) == 1104      # so a fome mudou


def test_com_peso_de_hoje_a_conta_e_a_de_sempre_e_os_canais_somam_o_escalar():
    rng = random.Random(7)
    for _ in range(2000):
        a, d = _obs(*(rng.random() for _ in range(4))), _obs(*(rng.random() for _ in range(4)))
        t = Transicao(a, lb.AcaoPet.EXPLORAR, d)
        todos_s = {0: S, 1: S, 2: S, 3: S}
        assert sinal_homeostatico(t, S, CC, todos_s) == sinal_homeostatico(t, S, CC)
        assert sinal_homeostatico_fruta(a, d, S, CC, todos_s) == sinal_homeostatico_fruta(a, d, S, CC)
        pesos = {i: rng.randrange(S // 4, S + 1) for i in range(4)}
        assert sum(sinal_homeostatico_canais(t, S, CC, pesos).values()) == sinal_homeostatico(t, S, CC, pesos)
        assert sum(sinal_por_canal(a.vetor_estado, d.vetor_estado, (0, 1, 2, 3), 4, S, pesos).values()) == \
            sinal_homeostatico_fruta(a, d, S, CC, pesos)
    with pytest.raises(ValueError, match="peso"):
        sinal_homeostatico(Transicao(_obs(), lb.AcaoPet.COMER, _obs()), S, CC, {0: S + 1, 1: S, 2: S})


# ------------------------------------------------------------------ numa vida: a janela decisao a decisao
class _Lobos(PoliticaLobos):
    """os lobos com o credito e a transicao espiados"""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.observadas, self.creditos = [], []

    def observar_consequencia(self, transicao, f_S, cfg_consequencia=None) -> None:
        self.observadas.append((transicao, f_S))
        super().observar_consequencia(transicao, f_S, cfg_consequencia)

    def _creditar(self, registro, f_S, anteriores, consequencia=False) -> None:
        self.creditos.append(f_S)
        super()._creditar(registro, f_S, anteriores, consequencia)


def _vida_p1(cc, dono="aleatorio", semente=101, dias=3):
    pols = []

    def fab(cfg=None):
        p = _Lobos(cfg or CONFIG_PADRAO, CL_T3)
        pols.append(p)
        return bv.PoliticaDoBraco(p, bv.braco_de("P1"), cc)

    v = simular_vida(dono, criar_dono(dono), fab(), semente, dias, 16 * dias)
    return v, pols[-1], fab


@pytest.mark.parametrize("dono", ["atencioso", "aleatorio"])
def test_a_janela_e_o_sinal_decisao_a_decisao(dono):
    """refeito por fora: a janela e a das J decisoes anteriores, o peso e o da A2.4, e o credito e o sinal com esses pesos"""
    for semente in SEMENTES:
        _, p, _ = _vida_p1(CC_J, dono, semente)
        janela, creditos_esperados = [], []
        motivos = p.motivos
        assert len(motivos) == len(p.observadas)
        drives = (0, 1, 2, 3)                                   # os do N3 e o humor da E2 (humor_na_fruta)
        for m, (t, f_S) in zip(motivos, p.observadas):
            n = len(janela)
            esperado = {}
            for i in drives:
                media = div_arred(sum(f[i] for f in janela), n) if n else 0
                esperado[i] = max(div_arred(S, 4), S - div_arred(3 * media, 4))
            assert m["pesos_janela"] == {lb.CANAL_DO_DRIVE[i]: w for i, w in esperado.items()}
            total = 0
            for i in (0, 1, 2):
                fa = S - lb.arred(t.observacao.vetor_estado[i] * S)
                fd = S - lb.arred(t.observacao_seguinte.vetor_estado[i] * S)
                delta = fa * fa - fd * fd
                total += delta if esperado[i] == S else div_arred(esperado[i] * delta, S)
            f = div_arred(CC.ganho * total, S)
            if f != 0:
                creditos_esperados.append(f)
            janela.append({i: S - lb.arred(t.observacao.vetor_estado[i] * S) for i in drives})
            del janela[:-CC_J.janela_pesos]
        assert p.creditos == creditos_esperados
        assert any(w < S for m in motivos for w in m["pesos_janela"].values())       # a janela mexeu nos pesos
        assert len(p.estado_interno()["aprendizado"]["janela_pesos"]) == min(len(motivos), 32)


def test_desligada_a_vida_e_a_de_hoje_e_ligada_muda():
    hoje, p_hoje, _ = _vida_p1(CC)
    off, p_off, _ = _vida_p1(replace(CC, pesos_janela=False, janela_pesos=8))      # o J nao importa com a chave desligada
    assert hoje.motor.log.para_jsonl() == off.motor.log.para_jsonl()
    assert json.dumps(p_hoje.estado_interno(), sort_keys=True) == json.dumps(p_off.estado_interno(), sort_keys=True)
    assert "janela_pesos" not in p_hoje.estado_interno()["aprendizado"]
    assert all("pesos_janela" not in m for m in p_hoje.motivos)
    _, p_on, _ = _vida_p1(CC_J)
    assert p_on.creditos != p_hoje.creditos


def test_f_s_que_nao_e_o_da_transicao_falha_alto():
    p = PoliticaLobos(CONFIG_PADRAO, CL_T3)
    o = _obs()
    p.agir(o, random.Random(1))
    t = Transicao(o, lb.AcaoPet(p.motivos[-1]["acao"]), _obs(fome=0.65))
    with pytest.raises(RuntimeError, match="pesos_janela"):
        p.observar_consequencia(t, sinal_homeostatico(t, S, CC) + 1, CC_J)


def test_g1_com_a_janela():
    for semente in SEMENTES:
        v, p, fab = _vida_p1(CC_J, "relapso", semente)
        r = reproduzir_com_feedback(v.motor.log, fab, semente=semente)
        assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(v.motor.politica.estado_interno(), sort_keys=True)


# ------------------------------------------------------------------ a E2, os canais e o mundo fisico com os mesmos pesos
@pytest.mark.parametrize("canais", [False, True])
def test_e2_e_canais_nas_frutas(canais):
    cc = replace(CC_J, canais_ligados=canais)
    b = bv.Bancada(3, 48, cfg_lobos=CL_T3, cfg_consequencia=cc, montagem="completa" if canais else "simples")  # na completa o P1 tem canais
    for mundo in ("descasado", "mutavel"):
        espec = bv.EspecVida("atencioso", "P1", 202, None, mundo)
        v = b.vida(espec)
        ei = v.motor.politica.estado_interno()
        assert ei["aprendizado"]["recompensas"].get("consequencia_fruta", 0) > 0
        assert all("pesos_janela" in m for m in ei["motivos"])
        assert canais == ("canais" in ei)
        r = b.rejogar(v.motor.log, espec)
        assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(ei, sort_keys=True)


def test_no_mundo_fisico_o_gancho_usa_os_pesos_da_decisao():
    cc = CC_J
    pols = []

    def fab(cfg=None):
        p = _Lobos(cfg or CONFIG_PADRAO, CL_T3, cfg_mundo=CONFIG_MUNDO_LIGADA)
        pols.append(p)
        return bv.PoliticaDoBraco(p, bv.braco_de("P1"), cc)

    fp, fm = fabricas_mundo(CONFIG_MUNDO_LIGADA, fab)
    lugar = DonoComLugar(criar_dono("atencioso"), "perto", 101, "atencioso", CONFIG_MUNDO_LIGADA)
    v = simular_vida_mundo("atencioso", lugar, fp(CONFIG_PADRAO), 101, 3, 48, fm, rotulo_dono="atencioso")
    p = pols[-1]
    esperados, mudou = [], 0
    for m, (t, f_s) in zip(p.motivos, p.observadas):
        pesos = {i: m["pesos_janela"][lb.CANAL_DO_DRIVE[i]] for i in (0, 1, 2, 3)}
        f = sinal_homeostatico(t, S, cc, pesos)                     # frutas iguais: a E2 da o mesmo numero do N3
        mudou += f != f_s
        if f != 0:
            esperados.append(f)
    assert p.creditos == esperados and mudou > 0
    r = reproduzir_mundo(v.motor.log, fp, CONFIG_PADRAO, 101, fm)
    assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(v.motor.politica.estado_interno(), sort_keys=True)
