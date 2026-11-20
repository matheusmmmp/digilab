"""V2, N5-CEREBRO (docs/TAREFA_V2_N5_CEREBRO.md; docs/PLANO_ANALISE_V2_N5.md, N5-1 a N5-3): a entrada `info` dos lobos.

A informacao do dono (Observacao.info_frutas: +1 bem, -1 mal, 0 nada) entra so na sub-decisao da fruta, com UM peso compartilhado
entre as frutas, iniciado em ConfigLobos.w0_info.
Gates: G1 replay; w0_info = 0, ou nenhuma informacao no registro, = a vida de hoje byte a byte; com informacao e o aprendizado
desligado a escolha pende para o lado da informacao na medida do w0_info; o peso da informacao muda com o sinal da consequencia e nao
muda com acao do dono (espiao). Sementes so dos testes (11, 22, 33).
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

import bancada_v2 as bv  # noqa: E402
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO, CONFIG_INFORMACAO_LIGADA,  # noqa: E402
                            CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import DonoInformante, OfertasFrutas, fabricas_frutas, reproduzir_frutas, simular_vida_frutas  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import PARAMETROS_LOBOS, PoliticaLobos, validar_parametros_lobos  # noqa: E402
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)
DIAS, ORC = 3, 48
CF, CI = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA
S = CONFIG_LOBOS.escala
GRADE = (S // 4, S // 2, 3 * S // 4)


def _nucleo(m, com_log: bool = True) -> tuple:
    n = (m._estado, tuple(m.acoes_recentes(10**9)), m._rng_politica.getstate(), m._rng_ambiente.getstate(),
         m._rng_fruta.getstate())
    return n + (m.log.para_jsonl(),) if com_log else n


def _consumos(m) -> list:
    return [(c["tick"], c["fruta"]) for c in m.consumos]


def _lobos(w0: int = 0, aprende: bool = False):
    cl = replace(CONFIG_LOBOS_APRENDIZ if aprende else CONFIG_LOBOS, w0_info=w0)
    return lambda cfg=None: PoliticaLobos(cfg, cl, None, CF)  # noqa: E731


def _p(fonte: str, w0: int = 0):
    """O cerebro da bancada com a fonte do braco: P1 (consequencia, com a E2) ou P3 (dono)."""
    cl = replace(CONFIG_LOBOS_APRENDIZ, w0_info=w0)
    braco = bv.braco_de(fonte)
    return lambda cfg=None: bv.PoliticaDoBraco(PoliticaLobos(cfg, cl, None, CF), braco, CONFIG_CONSEQUENCIA)  # noqa: E731


def _vida(dono, s, politica_fabrica, modo: str | None = "certo", ci=CI):
    fp, fm = fabricas_frutas(cfg_frutas=CF, cfg_informacao=ci, politica_fabrica=politica_fabrica)
    inf = DonoInformante.do_genoma(modo, s, CF) if modo else None
    v = simular_vida_frutas(f"{dono}-n5", criar_dono(dono), fp(), s, DIAS, ORC, fm, OfertasFrutas(CF), rotulo_dono=dono,
                            informante=inf)
    return v.motor, fp, fm


def _estado(m) -> dict:
    return m.politica.estado_interno()


# ------------------------------------------------------------------ registro e formas


def test_registro_e_padrao():
    validar_parametros_lobos()
    assert PARAMETROS_LOBOS["w0_info"][0] == "PROPOSTO" and CONFIG_LOBOS.w0_info == 0
    with pytest.raises(ValueError):
        PoliticaLobos(None, replace(CONFIG_LOBOS, w0_info=-1), None, CF)
    with pytest.raises(ValueError):
        PoliticaLobos(None, replace(CONFIG_LOBOS, w0_info=0.5), None, CF)


def test_peso_unico_so_com_frutas_e_w0_positivo():
    sem = PoliticaLobos(None, CONFIG_LOBOS, None, CF).estado_interno()
    com = PoliticaLobos(None, replace(CONFIG_LOBOS, w0_info=S // 2), None, CF).estado_interno()
    assert "peso_info" not in sem and com["peso_info"] == com["peso_info_prior"] == S // 2
    assert com["parametros_aprendidos"] == sem["parametros_aprendidos"] + 1        # um peso so, compartilhado (N5-3)
    assert com["entradas"] == sem["entradas"]                                      # nao entra na escolha de comer (N5-2)
    # sem ver as frutas o w0_info nao cria nada
    assert "peso_info" not in PoliticaLobos(None, replace(CONFIG_LOBOS, w0_info=S // 2)).estado_interno()


# ------------------------------------------------------------------ a vida de hoje


@pytest.mark.parametrize("dono", DONOS)
def test_w0_zero_com_informacao_e_a_vida_de_hoje(dono):
    """w0_info = 0: com o informante no registro, a vida (estado, acoes, rngs, consumos) e os pesos sao os da vida sem ele, para os
    lobos desligados e para o P1 aprendendo (o log so difere pelos eventos de informar)."""
    for fabrica in (_lobos(0), _p("P1", 0)):
        for s in SEMENTES:
            a, _, _ = _vida(dono, s, fabrica, modo=None)
            b, _, _ = _vida(dono, s, fabrica, modo="certo")
            assert b.informacoes and _nucleo(a, False) == _nucleo(b, False) and _consumos(a) == _consumos(b)
            ea, eb = _estado(a), _estado(b)
            assert ea["pesos"] == eb["pesos"] and ea.get("pesos_fruta") == eb.get("pesos_fruta")


@pytest.mark.parametrize("w0", GRADE)
def test_sem_informacao_no_registro_e_a_vida_de_hoje(w0):
    """Com w0_info > 0 e nenhuma informacao (chave desligada ou ligada sem informante): a vida byte a byte (log incluido) e os pesos
    da vida com w0_info = 0; so o estado interno ganha o peso da informacao, parado no prior."""
    for dono in DONOS:
        for s in SEMENTES:
            hoje, _, _ = _vida(dono, s, _p("P1", 0), modo=None, ci=CONFIG_INFORMACAO)
            for ci in (CONFIG_INFORMACAO, CI):
                b, _, _ = _vida(dono, s, _p("P1", w0), modo=None, ci=ci)
                assert _nucleo(hoje) == _nucleo(b) and hoje.resumo_frutas()["consumos"] == b.resumo_frutas()["consumos"]
                eh, eb = _estado(hoje), _estado(b)
                assert eh["pesos"] == eb["pesos"] and eh["pesos_fruta"] == eb["pesos_fruta"]
                assert eb["peso_info"] == w0


# ------------------------------------------------------------------ a escolha pende para a informacao


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _p_escolher(w0: int, info: tuple, inc: dict, aprende: bool = False, n: int = 2000) -> dict:
    """Frequencia de cada fruta na sub-decisao, com u numa grade uniforme, numa decisao de comer com fruta e a informacao `info`."""
    p = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, w0_info=w0), None, CF)
    e = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
    obs = replace(Observacao.de_estado(e), fruta=max(inc.values()), info_frutas=info)
    assert p.agir(obs, _Rng(1.0 - 1e-12)) is AcaoPet.COMER
    presentes = list(inc)
    conta = {f: 0 for f in presentes}
    for k in range(n):
        conta[p.escolher_fruta(presentes, inc, (k + 0.5) / n)] += 1
    return {f: c / n for f, c in conta.items()}


def test_aprendizado_desligado_a_escolha_pende_na_medida_do_w0():
    inc = {"a": 0.5, "b": 0.5}
    # "a faz mal", "b faz bem": quanto maior o w0_info, menos "a"
    pa = [_p_escolher(w0, (-1.0, 1.0, 0.0), inc)["a"] for w0 in (0,) + GRADE]
    assert pa[0] == 0.5 and pa[0] > pa[1] > pa[2] > pa[3]
    # a conta: peso_a = max(0,5 - w0/S, piso), peso_b = 0,5 + w0/S
    piso = CONFIG_LOBOS.piso_peso / S
    for w0, obtido in zip(GRADE, pa[1:]):
        pa_ = max(0.5 - w0 / S, piso)
        assert obtido == pytest.approx(pa_ / (pa_ + 0.5 + w0 / S), abs=1e-3)
    # informacao so sobre uma fruta: so ela muda de peso; "bem" puxa para ela
    assert _p_escolher(S // 2, (1.0, 0.0, 0.0), inc)["a"] == pytest.approx(1.0 / 1.5, abs=1e-3)
    # sem informacao vigente: a escolha de hoje
    assert _p_escolher(S // 2, (0.0, 0.0, 0.0), inc)["a"] == 0.5


def test_aprendizado_desligado_numa_vida_o_errado_come_mais_a_fruta_ruim():
    """Lobos desligados com w0_info 3S/4 no descasado: com o informante errado o pet come a fruta que faz mal mais vezes que com o certo
    (soma sobre donos e sementes dos testes); com w0_info 0 os dois sao a mesma vida."""
    ruim = {}
    for modo in ("certo", "errado"):
        n = 0
        for dono in DONOS:
            for s in SEMENTES:
                m, _, _ = _vida(dono, s, _lobos(GRADE[-1]), modo=modo)
                n += sum(c["efeito_humor"] < 0 for c in m.consumos)
        ruim[modo] = n
    assert ruim["errado"] > ruim["certo"]


# ------------------------------------------------------------------ G1 e o peso da informacao


@pytest.mark.parametrize("modo", ("certo", "errado"))
def test_g1_replay_bit_a_bit(modo):
    for fonte in ("P1", "P3"):
        for s in SEMENTES:
            m, fp, fm = _vida("atencioso", s, _p(fonte, S // 2), modo=modo)
            r = reproduzir_frutas(LogDeEventos.de_jsonl(m.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
            assert _nucleo(r) == _nucleo(m) and r.resumo_frutas() == m.resumo_frutas()
            assert json.dumps(_estado(r), sort_keys=True) == json.dumps(_estado(m), sort_keys=True)


def _espiao(monkeypatch) -> list:
    """Grava cada _aplicar_sinal: (consequencia?, peso_info antes, peso_info depois, tinha informacao no registro?)."""
    chamadas = []
    original = lobos.Aprendiz._aplicar_sinal

    def espiao(self, registro, f_S, consequencia=False):
        antes = self._peso_info
        original(self, registro, f_S, consequencia)
        chamadas.append((consequencia, antes, self._peso_info, "I" in registro.get("fruta", {})))
    monkeypatch.setattr(lobos.Aprendiz, "_aplicar_sinal", espiao)
    return chamadas


def test_o_peso_da_informacao_muda_pela_consequencia(monkeypatch):
    chamadas = _espiao(monkeypatch)
    mudou = 0
    for modo in ("certo", "errado"):
        for s in SEMENTES:
            m, _, _ = _vida("atencioso", s, _p("P1", S // 2), modo=modo)
            e = _estado(m)
            mudou += e["peso_info"] != e["peso_info_prior"]
    assert mudou > 0
    assert any(c and a != d for c, a, d, _ in chamadas)
    assert all(c for c, _, _, _ in chamadas)                    # no P1 todo sinal e da consequencia


def test_o_peso_da_informacao_nao_muda_pelo_dono(monkeypatch):
    chamadas = _espiao(monkeypatch)
    fruta_mudou = False
    for modo in ("certo", "errado"):
        for dono in DONOS:
            for s in SEMENTES:
                m, _, _ = _vida(dono, s, _p("P3", S // 2), modo=modo)
                e = _estado(m)
                assert e["peso_info"] == e["peso_info_prior"] == S // 2
                fruta_mudou |= e["pesos_fruta"] != e["pesos_fruta_prior"]
    com_info = [c for c in chamadas if c[3]]
    assert com_info and all(not c and a == d for c, a, d, _ in com_info)   # sinais do dono em decisoes com informacao
    assert fruta_mudou                                          # o dono ainda mexe nos pesos de cada fruta (como no #141)


def test_elogio_numa_escolha_com_informacao_nao_mexe_no_peso_da_informacao():
    p = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS_APRENDIZ, w0_info=S // 2), None, CF)
    e = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
    obs = replace(Observacao.de_estado(e), fruta=0.5, info_frutas=(1.0, -1.0, 0.0))
    p.agir(obs, _Rng(1.0 - 1e-12))
    p.observar(Transicao(Observacao.de_estado(e), AcaoPet.COMER, Observacao.de_estado(e)))
    assert p.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, 0.1) == "a"
    p.receber_acao_dono(AcaoUsuario.ELOGIAR, 12 * 60 + 1)
    est = p.estado_interno()
    assert est["peso_info"] == S // 2 and est["pesos_fruta"] != est["pesos_fruta_prior"]


def test_consequencia_ruim_numa_fruta_informada_bem_derruba_o_peso_da_informacao():
    """O dono disse "a faz bem"; o pet comeu "a" e o humor caiu: a E2 da sinal negativo, e o peso da informacao desce (o mundo
    desmente o dono). Com "a faz mal" e o mesmo desfecho, o peso sobe (o mundo confirma)."""
    def depois(info_a: float) -> int:
        p = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS_APRENDIZ, w0_info=S // 2), None, CF)
        e = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
        obs = replace(Observacao.de_estado(e), fruta=0.5, info_frutas=(info_a, 0.0, 0.0))
        p.agir(obs, _Rng(1.0 - 1e-12))
        t = Transicao(Observacao.de_estado(e), AcaoPet.COMER, Observacao.de_estado(e))
        p.observar_consequencia(t, 0, CONFIG_CONSEQUENCIA)
        assert p.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, 0.0) == "a"
        p.fruta_comida("a", Observacao.de_estado(replace(e, humor=0.7)))
        return p.estado_interno()["peso_info"]
    assert depois(1.0) < S // 2 < depois(-1.0)
