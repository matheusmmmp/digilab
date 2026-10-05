"""V2, FRUTA-NO-CENARIO, parte B (docs/TAREFA_V2_FRUTA_NO_CENARIO.md, secao 3; decisao R2): a decisao de comer le a fruta presente.

Na regra `fruta_no_cenario`, o peso de comer soma (w_f / S) x presenca_f das frutas no cenario (Observacao.frutas_cenario, parte A), com
um peso por fruta, prior 0, que so aprende pela consequencia (o P1 com a E2). A informacao do dono continua so na escolha de qual fruta.
Gates: G1; G2 (aprendizado desligado = instinto das frutas byte a byte; sem frutas = lobos de hoje); o P1 com a fruta ruim sozinha no
cenario aprende a nao comer. Sementes so dos testes.
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
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ,  # noqa: E402
                            CONFIG_PADRAO)
from digilab.events import FRUTAS, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = CONFIG_LOBOS.escala
CF = CONFIG_FRUTAS_LIGADA
MUNDOS = ("casado_frutas", "descasado", "mutavel")
BANCADA = bv.Bancada(4, 64)
E = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _obs(presenca: tuple, info: tuple = (0.0, 0.0, 0.0), estado: Estado = E) -> Observacao:
    return replace(Observacao.de_estado(estado), fruta=0.5, frutas_cenario=presenca, info_frutas=info)


def _p_comer(p: PoliticaLobos, presenca: tuple, info: tuple = (0.0, 0.0, 0.0)) -> float:
    """p(comer) na regra das frutas, lido dos pesos efetivos que o lobo de decisao usou (motivo da decisao)."""
    assert p.agir(_obs(presenca, info), _Rng(0.0)) is not None and p.ultima_regra == "fruta_no_cenario"
    pesos = p.motivos[-1]["pesos"]
    return pesos["comer"] / sum(pesos.values())


# ------------------------------------------------------------------ formas e G2


def test_formas():
    com = PoliticaLobos(None, CONFIG_LOBOS, None, CF).estado_interno()
    assert com["pesos_comer_fruta"] == com["pesos_comer_fruta_prior"] == {f: 0 for f in FRUTAS}
    assert com["parametros_aprendidos"] == 9 * 7 * 12 + 2 * len(FRUTAS)
    for sem in (PoliticaLobos(), PoliticaLobos(None, CONFIG_LOBOS, bv.CONFIG_BOLA_LIGADA, None)):
        assert "pesos_comer_fruta" not in sem.estado_interno()     # sem frutas: os lobos de hoje


@pytest.mark.parametrize("mundo", MUNDOS)
def test_g2_aprendizado_desligado_e_o_instinto_das_frutas(mundo):
    """P0 com lobos (os pesos de presenca no prior) = P0 com o instinto das frutas, byte a byte, pela bancada."""
    for dono in ("atencioso", "aleatorio"):
        for s in (101, 202):
            a = BANCADA.vida(bv.EspecVida(dono, "P0", s, None, mundo, "lobos")).motor
            b = BANCADA.vida(bv.EspecVida(dono, "P0", s, None, mundo, "instinto")).motor
            assert bv.resumo_motor(a) == bv.resumo_motor(b)


def test_no_prior_a_presenca_nao_muda_o_peso_de_comer():
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, None, CF)
    base = _p_comer(p, (0.0, 0.0, 0.0))
    for pres in ((1.0, 0.0, 0.0), (0.0, 1.0, 1.0), (1.0, 1.0, 1.0)):
        assert _p_comer(p, pres) == base


# ------------------------------------------------------------------ o P1 aprende a nao comer a fruta ruim sozinha


def _comer_so_a(p: PoliticaLobos, delta_humor: float) -> None:
    """Uma decisao de comer com so a fruta 'a' no cenario, pelo caminho do motor (agir, consequencia, escolha, fruta comida)."""
    obs = _obs((1.0, 0.0, 0.0))
    assert p.agir(obs, _Rng(1.0 - 1e-12)) is AcaoPet.COMER
    t = Transicao(Observacao.de_estado(E), AcaoPet.COMER, Observacao.de_estado(E))
    p.observar_consequencia(t, 0, CONFIG_CONSEQUENCIA)
    assert p.escolher_fruta(["a"], {"a": 0.5}, 0.5) == "a"
    p.fruta_comida("a", Observacao.de_estado(replace(E, humor=E.humor + delta_humor)))


def test_p1_com_a_fruta_ruim_sozinha_aprende_a_nao_comer():
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
    antes_a, antes_b = _p_comer(p, (1.0, 0.0, 0.0)), _p_comer(p, (0.0, 1.0, 0.0))
    for _ in range(6):
        _comer_so_a(p, -0.1)
    e = p.estado_interno()
    assert e["pesos_comer_fruta"]["a"] < 0 and e["pesos_comer_fruta"]["b"] == e["pesos_comer_fruta"]["c"] == 0
    assert _p_comer(p, (1.0, 0.0, 0.0)) < antes_a           # com a ruim sozinha, come menos
    # a fruta b sozinha: o termo de b nao mudou (o resto do peso de comer aprendeu junto, pela entrada `fruta`)
    assert _p_comer(p, (0.0, 1.0, 0.0)) > _p_comer(p, (1.0, 0.0, 0.0))
    assert antes_b == antes_a


def test_fruta_boa_sozinha_aprende_a_comer_mais():
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
    for _ in range(6):
        _comer_so_a(p, +0.1)
    assert p.estado_interno()["pesos_comer_fruta"]["a"] > 0


def test_o_dono_nao_mexe_nos_pesos_de_presenca():
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
    obs = _obs((1.0, 1.0, 0.0))
    p.agir(obs, _Rng(1.0 - 1e-12))
    p.observar(Transicao(Observacao.de_estado(E), AcaoPet.COMER, Observacao.de_estado(E)))
    p.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.4}, 0.1)
    p.receber_acao_dono(AcaoUsuario.ELOGIAR, E.tick + 1)
    e = p.estado_interno()
    assert e["pesos_comer_fruta"] == {f: 0 for f in FRUTAS} and e["pesos_fruta"] != e["pesos_fruta_prior"]


def test_a_informacao_nao_entra_na_decisao_de_comer():
    p = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, w0_info=S // 2), None, CF)
    for pres in ((1.0, 0.0, 0.0), (1.0, 1.0, 0.0)):
        assert _p_comer(p, pres, (-1.0, 0.0, 0.0)) == _p_comer(p, pres, (1.0, 0.0, 0.0)) == _p_comer(p, pres)


# ------------------------------------------------------------------ pela bancada: G1, P3 intocado, P1 aprende


def test_bancada_p1_aprende_a_presenca_e_p3_nao():
    """Na vida, comer da sinal positivo pela nutricao, entao os pesos de presenca sobem; o que a E2 ensina e a diferenca: o da fruta
    ruim fica abaixo dos outros (a decisao de comer e relativa)."""
    ruim_abaixo = 0
    for s in (101, 202, 303):
        p1 = bv.do_braco(BANCADA.vida(bv.EspecVida("atencioso", "P1", s, None, "descasado")).motor.politica).cerebro
        p3 = bv.do_braco(BANCADA.vida(bv.EspecVida("atencioso", "P3", s, None, "descasado")).motor.politica).cerebro
        assert p3.estado_interno()["pesos_comer_fruta"] == {f: 0 for f in FRUTAS}
        efeito = BANCADA.efeitos_reais(bv.EspecVida("atencioso", "P1", s, None, "descasado"))["antes"]
        ruim = next(f for f in FRUTAS if efeito[f] < 0)
        w = p1.estado_interno()["pesos_comer_fruta"]
        assert w != {f: 0 for f in FRUTAS}
        ruim_abaixo += all(w[ruim] < w[f] for f in FRUTAS if f != ruim)
    assert ruim_abaixo >= 2          # a bancada ja conferiu o replay (G1) de toda vida, com o estado interno


def test_espiao_so_a_consequencia_mexe_na_presenca(monkeypatch):
    chamadas = []
    original = lobos.atualizar_comer_fruta

    def espiao(*a, **k):
        chamadas.append(True)
        return original(*a, **k)
    monkeypatch.setattr(lobos, "atualizar_comer_fruta", espiao)
    BANCADA.vida(bv.EspecVida("atencioso", "P3", 101, None, "descasado"))
    assert chamadas == []
    BANCADA.vida(bv.EspecVida("atencioso", "P1", 101, None, "descasado"))
    assert chamadas
