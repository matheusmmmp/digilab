"""V2, CANAIS-REFORCO (docs/TAREFA_V2_CANAIS_REFORCO.md, etapa C4; H-R2; contrato K-6): o sinal da consequencia separado por canal (fome,
higiene, energia e humor), cada canal creditado ao seu grupo de pesos (lobos.ROTA_CANAIS), com o mesmo total do escalar. So testes de
mecanismo, so as sementes dos testes (nenhuma faixa reservada).

- G2: com os canais desligados, as 192 vidas do gabarito gravado ANTES da mudanca saem iguais (P0 a P3, padrao, bola e os tres mundos
  das frutas), estado interno incluido (tests/gabarito_canais_reforco.py).
- Total: a soma dos canais e o escalar, em inteiros, para qualquer par de estados; e decisao a decisao numa vida com os canais ligados.
- Credito: uma fruta que mata a fome e piora o humor credita o comer pelo canal da fome e a escolha da fruta pelo do humor, conta exata.
- G1 com os canais (a bancada rejoga toda vida do log, estado interno incluido); o dono e o P0 nao mudam com os canais ligados.
"""
from __future__ import annotations

import copy
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_canais_reforco as gab  # noqa: E402
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ,  # noqa: E402
                            CONFIG_PADRAO, ConfigConsequencia)
from digilab.events import FRUTAS, AcaoPet  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import (ALVOS_CANAIS, CANAL_DO_DRIVE, INDICE_HUMOR, PARAMETROS_CONSEQUENCIA_N3, ROTA_CANAIS,  # noqa: E402
                                    Aprendiz, PoliticaLobos, div_arred, sinal_homeostatico, sinal_homeostatico_canais,
                                    sinal_homeostatico_fruta, sinal_homeostatico_fruta_canais, sinal_por_canal,
                                    validar_parametros_consequencia)
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = CONFIG_LOBOS.escala
CF = CONFIG_FRUTAS_LIGADA
CC = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)
BANCADA = bv.Bancada(4, 64)
BANCADA_CANAIS = bv.Bancada(4, 64, cfg_consequencia=CC)
BANCADA_CANAIS_T3 = bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", {"w0_info": 512}), cfg_consequencia=CC)
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel")


# ------------------------------------------------------------------ registro e G2


def test_registro():
    validar_parametros_consequencia()
    assert CONFIG_CONSEQUENCIA.canais_ligados is False
    assert PARAMETROS_CONSEQUENCIA_N3["canais_ligados"][0] == "PROPOSTO"
    assert set(ROTA_CANAIS) == set(CANAL_DO_DRIVE.values()) and set(ROTA_CANAIS.values()) == set(ALVOS_CANAIS)
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
    assert all(p._sensibilidade_canal(c) == S for c in ROTA_CANAIS)          # H-R4: o ponto de entrada existe, sem uso
    with pytest.raises(KeyError):
        p._sensibilidade_canal("combate")


def test_g2_canais_desligados_e_a_vida_de_hoje():
    g = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    agora = gab.gerar()
    assert set(agora) == set(g) and len(g) == 192
    assert [k for k in g if agora[k] != g[k]] == []


# ------------------------------------------------------------------ o total: a soma dos canais e o escalar


def _obs_aleatoria(rng: random.Random) -> Observacao:
    return Observacao.de_estado(Estado(fome=rng.random(), higiene=rng.random(), energia=rng.random(), humor=rng.random(),
                                       tick=600, tick_ultimo_cuidado=590))


@pytest.mark.parametrize("ganho", [0, 1, 4, 16, 64])
def test_a_soma_dos_canais_e_o_escalar_em_qualquer_estado(ganho):
    rng = random.Random(11)
    cc = replace(CONFIG_CONSEQUENCIA, ganho=ganho)
    for _ in range(3000):
        oa, od = _obs_aleatoria(rng), _obs_aleatoria(rng)
        a, d = oa.vetor_estado, od.vetor_estado
        t = Transicao(oa, AcaoPet.COMER, od)
        canais = sinal_homeostatico_canais(t, S, cc)
        assert list(canais) == ["fome", "higiene", "energia"]
        assert sum(canais.values()) == sinal_homeostatico(t, S, cc)
        fr = sinal_homeostatico_fruta_canais(oa, od, S, cc)
        assert list(fr) == ["fome", "higiene", "energia", "humor"]
        assert sum(fr.values()) == sinal_homeostatico_fruta(oa, od, S, cc)
        for i, c in CANAL_DO_DRIVE.items():                          # cada canal fica a no maximo 1 da sua conta isolada
            delta = lobos.deficit_homeostatico(a, (i,), S) - lobos.deficit_homeostatico(d, (i,), S)
            assert abs(fr[c] - div_arred(ganho * delta, S)) <= 1


def test_drive_sem_canal_falha_alto():
    with pytest.raises(ValueError):
        sinal_por_canal(_obs_aleatoria(random.Random(1)).vetor_estado, _obs_aleatoria(random.Random(2)).vetor_estado, (0, 5), 4, S)


# ------------------------------------------------------------------ o credito: cada canal no seu grupo, conta exata

ANTES = Estado(fome=0.4, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
DEPOIS = replace(ANTES, fome=0.7, humor=0.7)          # a fruta mata a fome e piora o humor


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _comer_com_duas_frutas() -> PoliticaLobos:
    """Uma politica P1 (aprendiz ligado, vendo as frutas) que acabou de decidir comer com 'a' e 'b' no cenario e escolheu 'a';
    a consequencia ja foi observada (fica pendente ate a fruta comida, E2)."""
    obs = replace(Observacao.de_estado(ANTES), fruta=0.5, frutas_cenario=(1.0, 1.0, 0.0))
    for u in (1.0 - 1e-12, 0.0, 0.5, 0.25, 0.75):
        p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
        if p.agir(obs, _Rng(u)) is AcaoPet.COMER:
            break
    else:                                                             # pragma: no cover
        raise AssertionError("nenhum u levou a comer")
    p.observar_consequencia(Transicao(Observacao.de_estado(ANTES), AcaoPet.COMER, Observacao.de_estado(ANTES)), 0, CC)
    assert p.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.4}, 0.1) == "a"
    return p


def test_fruta_que_mata_a_fome_e_piora_o_humor_conta_exata():
    # a conta a mao (S = 1024, ganho 4): falta = S - arred(h * S)
    #   fome:  antes 1024 - 410 = 614, depois 1024 - 717 = 307: Delta = 614^2 - 307^2 = 282747
    #   humor: antes 1024 - 819 = 205, depois 1024 - 717 = 307: Delta = 205^2 - 307^2 = -52224
    #   escalar = div_arred(4 * 230523, 1024) = 900; fome = div_arred(4 * 282747, 1024) = 1104; humor = 900 - 1104 = -204
    assert CC.ganho == 4 and S == 1024
    canais = sinal_homeostatico_fruta_canais(Observacao.de_estado(ANTES), Observacao.de_estado(DEPOIS), S, CC)
    assert canais == {"fome": 1104, "higiene": 0, "energia": 0, "humor": -204}
    assert sinal_homeostatico_fruta(Observacao.de_estado(ANTES), Observacao.de_estado(DEPOIS), S, CC) == 900

    p = _comer_com_duas_frutas()
    registro = p._consequencia_pendente[0]
    g, sub = registro["regra"], registro["fruta"]
    esperado = copy.deepcopy(p)
    passo, teto = CONFIG_LOBOS_APRENDIZ.passo, CONFIG_LOBOS_APRENDIZ.teto
    lobos.atualizar_pesos(esperado._pesos[g], esperado._prior[g], registro, 1104, passo, teto, S)       # canal da fome: o comer
    lobos.atualizar_fruta(esperado._pesos_fruta, esperado._prior_fruta, sub, -204, passo, teto, S)      # canal do humor: a fruta
    if "presenca" in registro:
        lobos.atualizar_comer_fruta(esperado._pesos_comer_fruta, esperado._prior_comer_fruta, registro, -204, passo, teto, S)

    escalar = copy.deepcopy(p)
    escalar._consequencia_pendente = (registro, *p._consequencia_pendente[1:2], CONFIG_CONSEQUENCIA, [])
    p.fruta_comida("a", Observacao.de_estado(DEPOIS))
    escalar.fruta_comida("a", Observacao.de_estado(DEPOIS))

    e, x, sc = p.estado_interno(), esperado.estado_interno(), escalar.estado_interno()
    for chave in ("pesos", "pesos_fruta", "pesos_comer_fruta"):
        assert e[chave] == x[chave]
    assert e["canais"] == {"creditos": 1, "por_canal": canais, "por_alvo": {"corpo": 1104, "fruta": -204}}
    # a fruta escolhida: pelos canais o peso dela desce (o humor piorou); pelo escalar ele sobe (a fome manda no total), conta exata
    X, P, W = sub["X"]["a"], sub["P"]["a"], sub["W"]["a"]
    assert e["pesos_fruta"]["a"] - S == div_arred(-204 * passo * X * (S - P), S * S * W) < 0
    assert sc["pesos_fruta"]["a"] - S == div_arred(900 * passo * X * (S - P), S * S * W) > 0
    # o comer: pelos canais recebe a fome inteira (1104), pelo escalar so o total (900)
    assert e["pesos"][g]["comer"] != sc["pesos"][g]["comer"] and "canais" not in sc


def test_canais_com_traco_falham_alto():
    p = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS_APRENDIZ, traco_decisoes=2, traco_fator=S // 2), None, CF)
    obs = Observacao.de_estado(ANTES)
    a = p.agir(obs, _Rng(0.5))
    with pytest.raises(ValueError):
        p.observar_consequencia(Transicao(obs, a, obs), 0, CC)


# ------------------------------------------------------------------ na vida: o total decisao a decisao, G1, o dono intocado


def _espiar(monkeypatch) -> list:
    vistos = []
    original = Aprendiz._creditar_canais

    def espiao(self, registro, canais, f_S):
        vistos.append((dict(canais), f_S))
        return original(self, registro, canais, f_S)
    monkeypatch.setattr(Aprendiz, "_creditar_canais", espiao)
    return vistos


@pytest.mark.parametrize("mundo,braco", [("descasado", "P1"), ("mutavel", "P1"), ("casado_frutas", "P2"), ("padrao", "P1")])
def test_total_igual_ao_escalar_decisao_a_decisao(monkeypatch, mundo, braco):
    """Toda decisao do P1 com consequencia passa pelos canais (inclusive as de sinal 0); a soma dos canais e o escalar que a bancada
    calculou (ou o da fruta), decisao a decisao. A bancada rejoga a vida do log e confere o estado interno (G1)."""
    vistos = _espiar(monkeypatch)
    for bancada in (BANCADA_CANAIS, BANCADA_CANAIS_T3):
        n0 = len(vistos)
        m = bancada.vida(bv.EspecVida("atencioso", braco, 101, None, mundo)).motor
        cerebro = bv.do_braco(m.politica).cerebro
        e = cerebro.estado_interno()
        meus = vistos[n0:]
        # a bancada roda a vida e o replay: as duas passadas creditam o mesmo
        assert len(meus) % 2 == 0 and meus[: len(meus) // 2] == meus[len(meus) // 2:]
        meus = meus[: len(meus) // 2]
        assert meus and all(sum(c.values()) == f for c, f in meus)
        assert e["canais"]["creditos"] == len(meus)
        assert sum(e["canais"]["por_canal"].values()) == sum(e["canais"]["por_alvo"].values()) == sum(f for _, f in meus)
        if mundo != "padrao":
            assert any(c.get("humor", 0) != 0 for c, _ in meus)       # comeu fruta com efeito no humor
            assert e["canais"]["por_alvo"]["fruta"] == e["canais"]["por_canal"]["humor"]
        else:
            assert e["canais"]["por_alvo"]["fruta"] == 0


@pytest.mark.parametrize("mundo", MUNDOS_FRUTAS)
def test_canais_mudam_o_p1_e_nao_o_dono_nem_o_p0(mundo):
    for s in (101, 202):
        for braco in ("P0", "P3"):
            a = BANCADA.vida(bv.EspecVida("atencioso", braco, s, None, mundo)).motor
            b = BANCADA_CANAIS.vida(bv.EspecVida("atencioso", braco, s, None, mundo)).motor
            assert bv.resumo_motor(a) == bv.resumo_motor(b)
            assert a.politica.estado_interno() == b.politica.estado_interno()
    a = BANCADA.vida(bv.EspecVida("atencioso", "P1", 101, None, mundo)).motor
    b = BANCADA_CANAIS.vida(bv.EspecVida("atencioso", "P1", 101, None, mundo)).motor
    assert bv.do_braco(a.politica).cerebro.estado_interno()["pesos_fruta"] != \
        bv.do_braco(b.politica).cerebro.estado_interno()["pesos_fruta"]


def test_g1_com_os_canais_pelo_texto_do_log():
    for mundo, braco in (("descasado", "P1"), ("mutavel", "P2e"), ("padrao", "P1")):
        v = BANCADA_CANAIS_T3.vida(bv.EspecVida("aleatorio", braco, 202, None, mundo))
        BANCADA_CANAIS_T3.conferir_replay(v, v.motor.log.para_jsonl())


def test_canais_ligados_na_config_da_bancada():
    b = bv.bancada_da_config({"dias": 4, "orcamento": 64, "consequencia": {"canais_ligados": True}})
    assert b.cfg_consequencia.canais_ligados and b.cfg_consequencia.ganho == CONFIG_CONSEQUENCIA.ganho
    assert isinstance(b.cfg_consequencia, ConfigConsequencia)


def test_indice_do_humor():
    assert CANAL_DO_DRIVE[INDICE_HUMOR] == "humor" and FRUTAS
