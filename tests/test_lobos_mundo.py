"""V2, LOBOS-MUNDO (docs/TAREFA_V2_LOBOS_MUNDO.md): os lobos veem a bola e as frutas e escolhem a fruta; E2 no sinal do P1.

G2: com o aprendizado desligado, os lobos no mundo da bola = PoliticaInstintoBola e no mundo das frutas = PoliticaInstintoFrutas,
    byte a byte (estado, acoes, log, rngs do motor, a escolha da fruta, a rng_fruta e os registros das frutas).
G1: replay bit a bit com o aprendizado ligado (fonte dono e fonte consequencia com a E2).
E2: comer fruta que faz mal ao humor da sinal negativo pelo humor; as outras acoes ignoram o humor.
Sem o mundo ligado, as formas e o estado interno de antes (a L0, a L1, o N3 e a bancada tem os testes deles).
Sementes so dos testes (11, 22, 33): nenhuma faixa reservada.
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.ambiente import DonoComBola, MotorAmbiente, fabricas_ambiente, reproduzir_ambiente  # noqa: E402
from digilab.config import (CONFIG_BOLA, CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_FRUTAS, CONFIG_FRUTAS_LIGADA,  # noqa: E402
                            CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, ConfigConsequencia)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, AcaoPet, LogDeEventos  # noqa: E402
from digilab.frutas import (MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas, fabricas_frutas, reproduzir_frutas,  # noqa: E402
                            simular_vida_frutas)
from digilab.policies.lobos import (ENTRADAS, ENTRADAS_MUNDO, INDICE_HUMOR, PARAMETROS_CONSEQUENCIA_N3, REGRAS,  # noqa: E402
                                    REGRAS_MUNDO, PoliticaLobos, sinal_homeostatico, sinal_homeostatico_fruta,
                                    validar_parametros_consequencia)
from digilab.policy import Observacao, PoliticaInstinto, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)
DIAS, ORC = 3, 48
CB, CF = CONFIG_BOLA_LIGADA, CONFIG_FRUTAS_LIGADA
S = CONFIG_LOBOS.escala


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m.log.para_jsonl(), m._rng_politica.getstate(),
            m._rng_ambiente.getstate())


def _lobos(cl=CONFIG_LOBOS, cb=None, cf=None):
    return lambda cfg=None: PoliticaLobos(cfg, cl, cb, cf)  # noqa: E731


def _vida_bola(dono, s, politica_fabrica=None):
    fp, fm = fabricas_ambiente(cfg_bola=CB)
    fp = politica_fabrica or fp
    v = simular_vida(f"{dono}-bola", DonoComBola(dono, CB), fp(), s, DIAS, ORC, rotulo_dono=dono, fabrica_motor=fm)
    return v.motor, fp, fm


def _vida_frutas(dono, s, politica_fabrica=None, cf=CF, cb=CONFIG_BOLA, dono_obj=None):
    fp, fm = fabricas_frutas(cfg_frutas=cf, cfg_bola=cb, politica_fabrica=politica_fabrica)
    v = simular_vida_frutas(f"{dono}-frutas", dono_obj or criar_dono(dono), fp(), s, DIAS, ORC, fm, OfertasFrutas(cf),
                            rotulo_dono=dono)
    return v.motor, fp, fm


def _regras_usadas(motor) -> set:
    return {m["regra"] for m in motor.politica.estado_interno()["motivos"]}


# ------------------------------------------------------------------ formas


def test_sem_mundo_ligado_as_formas_e_o_estado_de_antes():
    antes = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ).estado_interno()
    for cb, cf in ((None, None), (CONFIG_BOLA, CONFIG_FRUTAS), (CONFIG_BOLA, None)):
        p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cb, cf)
        assert not p.ve_mundo and p.estado_interno() == antes
    assert antes["entradas"] == list(ENTRADAS) and set(antes["pesos"]) == set(REGRAS)
    assert antes["parametros_aprendidos"] == 7 * 7 * 10 and "pesos_fruta" not in antes


def test_com_mundo_entradas_regras_e_prior():
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, CB, CF)
    e = p.estado_interno()
    assert e["entradas"] == list(ENTRADAS + ENTRADAS_MUNDO) and tuple(e["pesos"]) == REGRAS + REGRAS_MUNDO
    assert e["parametros_aprendidos"] == 9 * 7 * 12 + 2 * len(FRUTAS) < CONFIG_LOBOS.maximo_pesos   # + presenca (FRUTA-NO-CENARIO)
    assert e["pesos_fruta"] == {f: S for f in FRUTAS}
    j = {n: i for i, n in enumerate(e["entradas"])}
    livre = e["pesos"]["tempo_livre"]
    for regra in REGRAS_MUNDO:
        w = e["pesos"][regra]
        assert w["brincar"][j["bola"]] == int(CB.w_bola * S)
        for a in ("ocioso", "explorar", "chamar_atencao"):
            assert w[a] == livre[a] and livre[a][-2:] == [0, 0]
    assert e["pesos"]["fruta_no_cenario"]["comer"][j["fruta"]] == int(CF.w_fruta * S)
    assert e["pesos"]["bola_no_cenario"]["comer"] == [0] * 12
    # so a bola: as mesmas formas, sem a sub-decisao da fruta e sem comer na regra das frutas
    so_bola = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, CB, None).estado_interno()
    assert so_bola["parametros_aprendidos"] == 9 * 7 * 12 and "pesos_fruta" not in so_bola
    assert so_bola["pesos"]["fruta_no_cenario"]["comer"] == [0] * 12


def test_coeficiente_do_mundo_fora_da_grade_falha_alto():
    with pytest.raises(ValueError):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, replace(CB, w_bola=0.1), None)
    with pytest.raises(ValueError):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, None, replace(CF, w_fruta=-1.0))


# ------------------------------------------------------------------ G2


@pytest.mark.parametrize("dono", DONOS)
def test_g2_bola_lobos_desligados_iguais_ao_instinto_da_bola(dono):
    usou = set()
    for s in SEMENTES:
        a, _, _ = _vida_bola(dono, s)
        b, _, _ = _vida_bola(dono, s, _lobos(cb=CB))
        assert _nucleo(a) == _nucleo(b) and a.resumo_bola() == b.resumo_bola() and a.estado() == b.estado()
        usou |= _regras_usadas(b)
    if dono != "relapso":
        assert "bola_no_cenario" in usou


@pytest.mark.parametrize("mundo", ("descasado", "iguais"))
@pytest.mark.parametrize("dono", DONOS)
def test_g2_frutas_lobos_desligados_iguais_ao_instinto_das_frutas(dono, mundo):
    cf = replace(CF, mundo=mundo)
    comidas = 0
    for s in SEMENTES:
        a, _, _ = _vida_frutas(dono, s, cf=cf)
        b, _, _ = _vida_frutas(dono, s, _lobos(cf=cf), cf=cf)
        assert _nucleo(a) == _nucleo(b) and a.estado() == b.estado()
        assert a.resumo_frutas() == b.resumo_frutas()                    # escolha, consumos, incentivos e rng_fruta
        assert a._rng_fruta.getstate() == b._rng_fruta.getstate()
        assert "fruta_no_cenario" in _regras_usadas(b)
        comidas += b.contagem_frutas["comidas"]
        assert all("fruta" in m for m in b.politica.motivos if m["acao"] == "comer" and m["percepcao"]["fruta"] > 0)
    assert comidas > 0


@pytest.mark.parametrize("dono", ("atencioso", "aleatorio"))
def test_g2_bola_e_frutas_juntas(dono):
    for s in SEMENTES:
        a, _, _ = _vida_frutas(dono, s, cb=CB, dono_obj=DonoComBola(dono, CB))
        b, _, _ = _vida_frutas(dono, s, _lobos(cb=CB, cf=CF), cb=CB, dono_obj=DonoComBola(dono, CB))
        assert _nucleo(a) == _nucleo(b) and a.resumo_frutas() == b.resumo_frutas() and a.resumo_bola() == b.resumo_bola()


def test_g2_lobos_que_veem_o_mundo_num_mundo_sem_bola_nem_fruta_sao_o_instinto():
    for dono in DONOS:
        a = simular_vida(dono, criar_dono(dono), PoliticaInstinto(), 11, DIAS, ORC, rotulo_dono=dono)
        b = simular_vida(dono, criar_dono(dono), PoliticaLobos(None, None, CB, CF), 11, DIAS, ORC, rotulo_dono=dono)
        assert _nucleo(a.motor) == _nucleo(b.motor)


def test_g2_aprendizado_ligado_sem_sinal_e_o_mesmo_sorteio():
    """P1 com ganho 0 (sinal sempre zero, inclusive o da fruta): o aprendiz ligado decide e escolhe a fruta igual ao instinto."""
    for s in SEMENTES:
        a, _, _ = _vida_frutas("atencioso", s)
        b, _, _ = _vida_frutas("atencioso", s, _p1(ConfigConsequencia(ganho=0)))
        assert _nucleo(a) == _nucleo(b) and a.resumo_frutas() == b.resumo_frutas()
        assert not b.politica.pesos_mudaram() and b.politica.estado_interno()["aprendizado"]["recompensas"]["consequencia_fruta"]


# ------------------------------------------------------------------ G1 e o aprendizado


@pytest.mark.parametrize("dono", ("atencioso", "incoerente"))
def test_g1_replay_bit_a_bit_aprendendo_com_o_dono(dono):
    mudou = False
    for s in SEMENTES:
        m, fp, fm = _vida_frutas(dono, s, _lobos(CONFIG_LOBOS_APRENDIZ, cb=CB, cf=CF), cb=CB, dono_obj=DonoComBola(dono, CB))
        r = reproduzir_frutas(LogDeEventos.de_jsonl(m.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
        assert _nucleo(r) == _nucleo(m) and r.resumo_frutas() == m.resumo_frutas()
        assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(m.politica.estado_interno(), sort_keys=True)
        mudou |= m.politica.pesos_mudaram()
    assert mudou


def _p1(cc=CONFIG_CONSEQUENCIA, cf=CF):
    braco = bv.braco_de("P1")
    return lambda cfg=None: bv.PoliticaDoBraco(PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ, None, cf), braco, cc)  # noqa: E731


def test_g1_p1_com_a_e2_rejoga_bit_a_bit_e_credita_as_frutas():
    total_fruta = 0
    sub_mudou = False
    for s in SEMENTES:
        m, fp, fm = _vida_frutas("atencioso", s, _p1())
        r = reproduzir_frutas(LogDeEventos.de_jsonl(m.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
        assert _nucleo(r) == _nucleo(m) and r.resumo_frutas() == m.resumo_frutas()
        e = m.politica.estado_interno()
        assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(e, sort_keys=True)
        rec = e["aprendizado"]["recompensas"]
        assert rec.get("consequencia_fruta", 0) == m.contagem_frutas["comidas"]
        assert "consequencia_pendente" not in e["aprendizado"]
        total_fruta += rec.get("consequencia_fruta", 0)
        sub_mudou |= e["pesos_fruta"] != e["pesos_fruta_prior"]
    assert total_fruta > 0 and sub_mudou


def test_p1_sem_humor_na_fruta_e_outro_sinal():
    a, _, _ = _vida_frutas("atencioso", 11, _p1())
    b, _, _ = _vida_frutas("atencioso", 11, _p1(replace(CONFIG_CONSEQUENCIA, humor_na_fruta=False)))
    assert a.politica.estado_interno()["pesos_fruta"] != b.politica.estado_interno()["pesos_fruta"]


# ------------------------------------------------------------------ E2: o sinal


def _obs(**kw) -> Observacao:
    return Observacao.de_estado(Estado(**kw))


def test_e2_registro_e_humor_no_vetor():
    validar_parametros_consequencia()
    assert PARAMETROS_CONSEQUENCIA_N3["humor_na_fruta"][0] == "DECIDIDO" and CONFIG_CONSEQUENCIA.humor_na_fruta
    assert ENTRADAS[1 + INDICE_HUMOR] == "humor"


def test_e2_fruta_ruim_da_sinal_negativo_pelo_humor():
    cc = ConfigConsequencia(ganho=16)
    antes = _obs(fome=1.0, higiene=1.0, energia=1.0, humor=0.8)
    ruim = _obs(fome=1.0, higiene=1.0, energia=1.0, humor=0.7)
    assert sinal_homeostatico_fruta(antes, ruim, S, cc) < 0
    assert sinal_homeostatico_fruta(antes, ruim, S, replace(cc, humor_na_fruta=False)) == 0
    neutra = _obs(fome=1.0, higiene=1.0, energia=1.0, humor=0.8)
    assert sinal_homeostatico_fruta(antes, neutra, S, cc) == 0
    # com fome, a nutricao conta; o humor ruim pesa contra
    com_fome = _obs(fome=0.5, higiene=1.0, energia=1.0, humor=0.8)
    nutre = _obs(fome=0.6, higiene=1.0, energia=1.0, humor=0.8)
    nutre_ruim = _obs(fome=0.6, higiene=1.0, energia=1.0, humor=0.7)
    assert sinal_homeostatico_fruta(com_fome, nutre, S, cc) > sinal_homeostatico_fruta(com_fome, nutre_ruim, S, cc)


@pytest.mark.parametrize("acao", list(AcaoPet))
def test_e2_as_outras_acoes_ignoram_o_humor(acao):
    cc = ConfigConsequencia(ganho=16)
    t = Transicao(_obs(fome=0.6, humor=0.8), acao, _obs(fome=0.6, humor=0.3))
    assert sinal_homeostatico(t, S, cc) == 0


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _comer_com_fruta(efeito_humor: float):
    """Uma decisao de comer no tempo livre com fruta, pelo caminho do motor: agir, observar_consequencia, escolher_fruta,
    fruta_comida. Devolve a politica e o peso de comer na entrada da fruta antes."""
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
    e = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
    obs = replace(Observacao.de_estado(e), fruta=0.5)
    assert p.agir(obs, _Rng(1.0 - 1e-12)) is AcaoPet.COMER and p.ultima_regra == "fruta_no_cenario"
    t = Transicao(Observacao.de_estado(e), AcaoPet.COMER, Observacao.de_estado(e))
    p.observar_consequencia(t, sinal_homeostatico(t, S), CONFIG_CONSEQUENCIA)
    assert p.estado_interno()["aprendizado"]["consequencia_pendente"]["acao"] == "comer"
    escolhida = p.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.4}, 0.1)
    assert escolhida == "a"
    p.fruta_comida("a", Observacao.de_estado(replace(e, humor=0.8 + efeito_humor)))
    return p


def test_e2_comer_a_fruta_ruim_desaprende_comer_e_a_fruta():
    j = (ENTRADAS + ENTRADAS_MUNDO).index("fruta")
    p = _comer_com_fruta(-0.1)
    e = p.estado_interno()
    assert e["pesos"]["fruta_no_cenario"]["comer"][j] < e["pesos_prior"]["fruta_no_cenario"]["comer"][j]
    assert e["pesos_fruta"]["a"] < S and e["pesos_fruta"]["b"] > S and e["pesos_fruta"]["c"] == S
    assert e["aprendizado"]["recompensas"]["consequencia_fruta"] == 1
    # fruta que nao faz mal, com o pet saciado: sinal zero, nada muda
    assert not _comer_com_fruta(0.0).pesos_mudaram()


def test_e2_comer_sem_fruta_e_outras_fontes_nao_adiam():
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
    e = Estado(fome=0.4, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
    obs = Observacao.de_estado(e)
    a = p.agir(obs, _Rng(0.0))
    assert a is AcaoPet.COMER and p.ultima_regra == "fome_moderada"
    t = Transicao(obs, a, Observacao.de_estado(replace(e, fome=0.5)))
    p.observar_consequencia(t, sinal_homeostatico(t, S), CONFIG_CONSEQUENCIA)
    assert "consequencia_pendente" not in p.estado_interno()["aprendizado"] and p.pesos_mudaram()
    p.fruta_comida("a", obs)                   # sem pendente (fonte dono, P0): o aviso nao faz nada


def test_e2_comer_com_fruta_sem_o_aviso_falha_alto():
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, None, CF)
    e = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
    obs = replace(Observacao.de_estado(e), fruta=0.5)
    p.agir(obs, _Rng(1.0 - 1e-12))
    t = Transicao(Observacao.de_estado(e), AcaoPet.COMER, Observacao.de_estado(e))
    p.observar_consequencia(t, 0, CONFIG_CONSEQUENCIA)
    with pytest.raises(RuntimeError):
        p.agir(obs, _Rng(0.5))


def test_motor_recusa_fruta_fora_do_cenario():
    class Errada(PoliticaInstintoFrutas):
        def escolher_fruta(self, presentes, incentivos, u):
            return "z"
    fp, fm = fabricas_frutas(cfg_frutas=CF, politica_fabrica=lambda cfg=None: Errada(cfg, CONFIG_BOLA, CF))
    with pytest.raises(RuntimeError):
        for s in SEMENTES:
            simular_vida_frutas("x", criar_dono("atencioso"), fp(), s, DIAS, ORC, fm, OfertasFrutas(CF), rotulo_dono="atencioso")


def test_escolha_no_prior_e_a_do_motor():
    m = MotorFrutas(None, CONFIG_PADRAO, 5, cfg_frutas=CF)
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, None, CF)
    rng = random.Random(3)
    for _ in range(2000):
        n = rng.randint(1, 3)
        presentes = sorted(rng.sample(FRUTAS, n), key=FRUTAS.index)
        inc = {f: rng.choice((0.0, rng.random())) for f in presentes}
        m.incentivo.update(inc)
        u = rng.random()
        assert p.escolher_fruta(presentes, inc, u) == m._escolher(presentes, u)
    assert PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, CB, None).escolher_fruta(["a"], {"a": 1.0}, 0.3) is None
