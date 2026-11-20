"""Os testes do passeio (AN2, docs/TAREFA_V3_ACOES_NOVAS.md, secoes 3.1 a 3.4 e 11): o vagar que segura o destino, atras da subchave `passeio`
da ConfigDigibrain (desligada por padrao).

  - G2-py: tests/test_passeio_gabarito.py (as oito vidas) e os gabaritos de hoje (tests/test_gabarito_digibrain_modular*.py, o G0); aqui, que a
    subchave nasce desligada, que desligada nenhum campo novo aparece e que as vidas inteiras saem as de hoje;
  - o M-ESTADO em cenarios feitos a mao: abrir, os fins (`meta`, `trocou`, `desistiu`, `interrompido`), a guarda (persistencia 0 acima do
    limiar, o reflexo antes do `interrompido`, o F que nao sobe) e o credito descartado pelo gesto do dono;
  - as vidas (so as sementes dos testes): determinismo, replay bit a bit, a guarda no motivo e o gesto injetado.
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

import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_PADRAO, ConfigDigibrain  # noqa: E402
from digilab.digibrain import adapt as adapt_mod  # noqa: E402
from digilab.digibrain._comum import mul  # noqa: E402
from digilab.digibrain.estado import EstadoDinamico  # noqa: E402
from digilab.events import AcaoUsuario, LogDeEventos  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
CD = replace(CONFIG_DIGIBRAIN_LIGADA, passeio=True)
VAGAR = {"chave": ("explorar", "vagar", None), "d": None}
DORMIR = {"chave": ("dormir", None, None), "d": None}
PONTO = (500, 700)
PASSEIO = ("explorar", "passeio", PONTO)
CALMO = {"fome": 0, "higiene": 0, "energia": 0, "saude": 0, "tedio": S, "solidao": S}
FOME = {**CALMO, "fome": P.urgencia_lambda + 1}
NO_LIMIAR = {**CALMO, "fome": P.urgencia_lambda}
DEPOIS = {"visto": True, "d": 400, "ha_cheiro": False, "comida_boa_vista": False}
OCORRIDO = {"comeu": None, "brincou_com_bola": False, "chegou": False}


def estado(cd=CD) -> EstadoDinamico:
    return EstadoDinamico(CONFIG_PADRAO, cd, P)


def abrir(e: EstadoDinamico, k: int = 0, urg: dict = CALMO):
    """a decisao k escolhe o vagar e o M-ADAPT entrega o ponto: devolve a chave do passeio (ou None)"""
    e.cuidar_passeio(urg, False, False)
    e.contexto(urg)
    assert e.escolhida(VAGAR, [1, 2, 3], 100, k) == []
    return e.abrir_passeio(PONTO, 600)


def continuar(e: EstadoDinamico, k: int, urg: dict = CALMO, d: int = 600, reflexo: bool = False, gesto: bool = False) -> list[dict]:
    """a decisao k segue o passeio; devolve os fins do cuidado (a decisao so escolhe o passeio se ele ainda existe)"""
    fins = e.cuidar_passeio(urg, reflexo, gesto)
    e.contexto(urg)
    if e.I is not None:
        e.escolhida({"chave": PASSEIO, "d": d}, [1, 2, 3], 100, k)
    return fins


# ------------------------------------------------------------------ a subchave nasce desligada
def test_a_subchave_nasce_desligada_e_desligada_nao_ha_campo_novo():
    assert CONFIG_DIGIBRAIN.passeio is False and CONFIG_DIGIBRAIN_LIGADA.passeio is False
    e = estado(replace(CD, passeio=False))
    assert "passeio" not in e.estado_interno() and "interrompido" not in e.fins
    with pytest.raises(RuntimeError, match="sem a subchave"):
        e.cuidar_passeio(CALMO, False, False)
    with pytest.raises(RuntimeError, match="sem a subchave"):
        e.abrir_passeio(PONTO, 1)
    e.contexto()                                             # desligada, o contexto e o de hoje (sem as urgencias)
    assert e.escolhida(VAGAR, [1], 100, 0) == []
    assert e.I is None                                       # o vagar segue uma opcao de uma decisao


def test_a_subchave_exige_bool_e_nao_se_combina_com_as_do_credito_e_da_suspensao():
    with pytest.raises(TypeError):
        ConfigDigibrain(passeio=1)
    for outra in ("credito_corrida", "intencao_suspensa"):
        with pytest.raises(ValueError, match="passeio"):
            ConfigDigibrain(passeio=True, **{outra: True})


def test_com_a_subchave_o_contexto_pede_as_urgencias():
    with pytest.raises(RuntimeError, match="urgencias"):
        estado().contexto()


# ------------------------------------------------------------------ 3.1: o destino fica
def test_o_vagar_escolhido_abre_o_passeio_com_o_ponto_do_motor():
    e = estado()
    assert abrir(e) == PASSEIO
    assert e.I["chave"] == PASSEIO and e.opcao is e.I and e.I["C"] == mul(e.k_c, S, S) and e.I["d"] == 600 and e.passeios == 1
    assert e.estado_interno()["I"]["chave"] == ["explorar", "passeio", [500, 700]] and e.estado_interno()["passeio"]["abertos"] == 1


def test_o_passeio_segue_com_a_persistencia_e_o_compromisso_que_sobe():
    e = estado()
    abrir(e)
    e.consequencia(10, OCORRIDO, DEPOIS)
    c0 = e.I["C"]
    ctx = e.contexto(CALMO)
    assert ctx["persistencia"] == {PASSEIO: mul(P.w_pers, c0, S)} and ctx["I"] == PASSEIO
    assert e.escolhida({"chave": PASSEIO, "d": 500}, [1, 2, 3], 100, 1) == []
    assert e.I["C"] >= c0 and e.I["n"] == 2 and e.I["chave"] == PASSEIO


# ------------------------------------------------------------------ 3.1: os fins
def test_fim_meta_chegou_ao_ponto_sem_subir_o_f():
    e = estado()
    abrir(e)
    fins = e.consequencia(10, {**OCORRIDO, "chegou": True}, DEPOIS)
    assert [f["motivo"] for f in fins] == ["meta"] and fins[0]["meta"] is True and fins[0]["chave"] == PASSEIO
    assert e.I is None and e.F == 0 and e.fins["meta"] == 1 and "credito" not in fins[0]


def test_fim_trocou_quando_outra_unidade_e_escolhida_e_o_f_sobe():
    e = estado()
    abrir(e)
    e.consequencia(10, OCORRIDO, DEPOIS)
    e.cuidar_passeio(CALMO, False, False)
    e.contexto(CALMO)
    fins = e.escolhida({"chave": ("ocioso", None, None), "d": None}, [0, 0, 0], 100, 1)
    assert [f["motivo"] for f in fins] == ["trocou"] and e.F > 0 and e.fins["trocou"] == 1


def test_fim_desistiu_depois_de_n_desiste_decisoes_sem_chegar_mais_perto():
    e = estado()
    abrir(e)
    fins = []
    for k in range(P.n_desiste):
        fins = e.consequencia(10, OCORRIDO, {**DEPOIS, "d": 700})          # a distancia nao cai (600 -> 700)
        if k < P.n_desiste - 1:
            continuar(e, k + 1, d=700)
    assert [f["motivo"] for f in fins] == ["desistiu"] and e.F > 0 and e.I is None


# ------------------------------------------------------------------ 3.2: a guarda
def test_a_persistencia_do_passeio_e_zero_acima_do_limiar_e_vale_no_limiar():
    e = estado()
    abrir(e)
    e.consequencia(10, OCORRIDO, DEPOIS)
    assert e.contexto(NO_LIMIAR)["persistencia"] != {}                       # a urgencia no limiar nao passa dele
    assert e.contexto(FOME)["persistencia"] == {}                            # acima do limiar: persistencia 0


def test_so_a_persistencia_do_passeio_cai_com_urgencia_a_do_lugar_lembrado_fica():
    e = estado()
    e.contexto(CALMO)
    e.escolhida({"chave": ("explorar", "ponto", PONTO), "d": 300}, [1, 2, 3], 100, 0)
    e.consequencia(10, OCORRIDO, DEPOIS)
    assert e.contexto(FOME)["persistencia"] != {}


@pytest.mark.parametrize("necessidade", ["fome", "higiene", "energia", "saude"])
def test_a_urgencia_acaba_o_passeio_como_interrompido_sem_subir_o_f(necessidade):
    e = estado()
    abrir(e)
    e.consequencia(10, OCORRIDO, DEPOIS)
    fins = e.cuidar_passeio({**CALMO, necessidade: P.urgencia_lambda + 1}, False, False)
    assert [f["motivo"] for f in fins] == ["interrompido"] and fins[0]["meta"] is False and fins[0]["chave"] == PASSEIO
    assert e.I is None and e.F == 0 and e.fins["interrompido"] == 1 and "credito" not in fins[0]


def test_o_tedio_a_curiosidade_a_solidao_e_o_estresse_nao_interrompem():
    e = estado()
    abrir(e)
    e.consequencia(10, OCORRIDO, DEPOIS)
    assert e.cuidar_passeio({**CALMO, "tedio": S, "curiosidade": S, "solidao": S, "estresse": S, "humor": S}, False, False) == []
    assert e.I is not None


def test_o_reflexo_do_sono_acaba_o_passeio_como_trocou_e_nao_como_interrompido():
    e = estado()
    abrir(e)
    e.consequencia(10, OCORRIDO, DEPOIS)
    urg = {**CALMO, "energia": S}
    assert e.cuidar_passeio(urg, True, False) == []
    e.contexto(urg)
    fins = e.escolhida(DORMIR, [0, 0, 0], 100, 1, reflexo=True)
    assert [f["motivo"] for f in fins] == ["trocou"] and e.F > 0 and e.fins["interrompido"] == 0


def test_com_urgencia_o_vagar_nao_abre_passeio_e_fica_uma_opcao_de_uma_decisao():
    e = estado()
    assert abrir(e, urg=FOME) is None
    assert e.I is None and e.passeios == 0
    fins = e.consequencia(10, OCORRIDO, DEPOIS)
    assert [f["motivo"] for f in fins] == ["unica"]


def test_abrir_passeio_fora_da_opcao_do_vagar_falha_alto():
    e = estado()
    e.contexto(CALMO)
    e.escolhida(DORMIR, [0, 0, 0], 100, 0)
    with pytest.raises(RuntimeError, match="fora da opcao do vagar"):
        e.abrir_passeio(PONTO, 1)


# ------------------------------------------------------------------ 3.3: o gesto do dono nao treina o passeio
@pytest.mark.parametrize("gesto_no_fim", ["meta", "trocou", "interrompido"])
def test_o_gesto_no_intervalo_descarta_o_credito_do_passeio(gesto_no_fim):
    e = estado()
    abrir(e)
    e.consequencia(10, OCORRIDO, DEPOIS)
    if gesto_no_fim == "interrompido":
        fins = continuar(e, 1, urg=FOME, gesto=True)
    else:
        assert e.cuidar_passeio(CALMO, False, True) == []
        e.contexto(CALMO)
        if gesto_no_fim == "trocou":
            fins = e.escolhida({"chave": ("ocioso", None, None), "d": None}, [0, 0, 0], 100, 1)
        else:
            e.escolhida({"chave": PASSEIO, "d": 500}, [1, 2, 3], 100, 1)
            fins = e.consequencia(10, {**OCORRIDO, "chegou": True}, DEPOIS)
    assert [f["motivo"] for f in fins] == [gesto_no_fim]
    assert fins[0]["credito"] is False and fins[0]["credito_descartado"] == "gesto" and e.descartados == 1
    assert adapt_mod._creditar(_PlastQueFalha(), fins, CD) == []             # nada vai ao P2
    assert adapt_mod._fim(fins[0])["credito"] == "gesto"                     # e o motivo registra o descarte


def test_sem_gesto_o_fim_do_passeio_vai_ao_p2_e_o_motivo_nao_tem_o_campo_credito():
    e = estado()
    abrir(e)
    fins = e.consequencia(10, {**OCORRIDO, "chegou": True}, DEPOIS)
    assert fins[0].get("credito", True) is True and "credito" not in adapt_mod._fim(fins[0])


def test_o_gesto_de_antes_do_passeio_nao_conta():
    e = estado()
    e.cuidar_passeio(CALMO, False, True)                                     # sem passeio em curso: nada a marcar
    abrir(e)
    fins = e.consequencia(10, {**OCORRIDO, "chegou": True}, DEPOIS)
    assert "credito_descartado" not in fins[0] and e.descartados == 0


class _PlastQueFalha:
    def creditar(self, op):                                                  # o P2 nao pode ser chamado para a opcao descartada
        raise AssertionError("a opcao descartada chegou ao P2")


# ------------------------------------------------------------------ as vidas (sementes dos testes)
@pytest.fixture
def com_passeio(monkeypatch):
    original = orq.config_do_braco
    monkeypatch.setattr(orq, "config_do_braco", lambda b, g=None, c=False: replace(original(b, g, c), passeio=True))


def test_desligada_a_vida_nao_tem_campo_novo():
    _motor, reg, _ = orq.viver("M3", "atencioso", "longe", 101, 2, orq.ORCAMENTO_POR_DIA, conserto=True)
    c = orq.cerebro_de(reg)
    assert not any("do_passeio" in m.get("alvo", {}) for m in c.motivos)
    assert "passeio" not in c.estado_interno()["modulos"]["estado"] and "interrompido" not in c.estado_interno()["modulos"]["estado"]["fins"]


def test_a_vida_com_o_passeio_segura_o_destino_e_o_replay_e_bit_a_bit(com_passeio):
    motor, reg, (fp, fm) = orq.viver("M3", "atencioso", "longe", 101, 4, orq.ORCAMENTO_POR_DIA, conserto=True)
    c = orq.cerebro_de(reg)
    est = c.estado_interno()["modulos"]["estado"]
    assert est["passeio"]["abertos"] > 0 and est["fins"]["meta"] + est["fins"]["trocou"] + est["fins"]["desistiu"] + est["fins"]["interrompido"] > 0
    com = [m for m in c.motivos if m.get("alvo", {}).get("do_passeio")]
    assert com and all(m["acao"] == "explorar" for m in com)
    assert any(m["alvo"]["tipo"] == "ponto" and not m["alvo"]["do_mem"] for m in com)       # os que seguem o destino: Alvo.ponto
    assert all("do_passeio" in m["alvo"] for m in c.motivos if m["acao"] == "explorar" and m.get("alvo"))
    r = orq.reproduzir_mundo(LogDeEventos.de_jsonl(motor.log.para_jsonl()), fp, semente=101, fabrica_motor=fm)
    assert r.log.para_jsonl() == motor.log.para_jsonl()
    assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(c.estado_interno(), sort_keys=True)


def test_na_vida_o_passeio_so_persiste_sem_urgencia_e_o_interrompido_nao_sobe_o_f(com_passeio):
    _motor, reg, _ = orq.viver("M3", "atencioso", "longe", 202, 4, orq.ORCAMENTO_POR_DIA, conserto=True)
    c = orq.cerebro_de(reg)
    for m in c.motivos:
        urg = m["afeto"]["urgencias"]
        urgente = max(urg.get(r, 0) for r in ("fome", "higiene", "energia", "saude")) > P.urgencia_lambda
        passeio_em_curso = m["estado"]["I"] is not None and m["estado"]["I"][1] == "passeio"
        if passeio_em_curso and urgente:                      # so o reflexo do sono segura a decisao com urgencia (e ele acaba o passeio)
            assert m["reflexo"]
            assert all(u["termos"]["persistencia"] == 0 for u in m["unidades"] if u["chave"][1] == "passeio")
    assert c.estado_interno()["modulos"]["estado"]["F"] >= 0


def test_o_gesto_injetado_na_vida_descarta_o_credito_e_o_p2_nao_recebe(com_passeio, monkeypatch):
    original = adapt_mod.DigiBrain.agir

    def agir_com_carinho(self, obs, rng):
        if self.m.estado.I is not None and self.m.estado.I["chave"][1] == "passeio":
            self.receber_acao_dono(AcaoUsuario.ACARICIAR, 0)
        return original(self, obs, rng)

    monkeypatch.setattr(adapt_mod.DigiBrain, "agir", agir_com_carinho)
    _motor, reg, _ = orq.viver("M3", "atencioso", "longe", 101, 4, orq.ORCAMENTO_POR_DIA, conserto=True)
    c = orq.cerebro_de(reg)
    descartados = [f for m in c.motivos for f in m["fins"] if f.get("credito") == "gesto"]
    assert descartados and c.estado_interno()["modulos"]["estado"]["passeio"]["credito_descartado"] == len(descartados)
    assert all(f["chave"][1] == "passeio" for f in descartados)
