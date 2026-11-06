"""A ponte da luta, PE1 (docs/TAREFA_V3_PONTE_LUTA.md, secoes 3.2, 3.4 e 3.5): o estimulo da luta no corpo (a dor pela vida perdida) e o
evento `pl` do resumo da luta no replay do mundo do Python, atras de `ConfigLutaCorpo.ligada` (a chave `luta_corpo`, desligada).

T-PL-1: um resumo com vida perdida sobe a dor exatamente div_arred(p x C, S), sem rng; um resumo com a chave desligada levanta erro.
G2: desligada, a vida de hoje sai igual (os gabaritos de hoje estao nos testes deles; aqui, a tabela do corpo e o replay).
So as sementes dos testes."""
from __future__ import annotations

import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_LUTA_CORPO, CONFIG_LUTA_CORPO_LIGADA, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_PADRAO, PARAMETROS_LUTA_CORPO, ConfigCorpo, ConfigLutaCorpo)
from digilab.corpo import Corpo, div_arred  # noqa: E402
from digilab.events import Evento, LogDeEventos, LutaSemChave, ler_resumo_luta, resumo_luta  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, reproduzir_mundo  # noqa: E402
from digilab.state import Estado  # noqa: E402

CFG = CONFIG_PADRAO
CM = CONFIG_MUNDO_LIGADA
CC = CONFIG_CORPO_DRIVES
CL = CONFIG_LUTA_CORPO_LIGADA
C, S = CC.escala, CC.escala_receptor
MotorMundoCorpo = com_corpo(MotorMundo)


def _fabrica(cl, cc=CC):
    return lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, cfg_luta_corpo=cl)


def _motor(cl, semente=101):
    return _fabrica(cl)(PoliticaInstintoMundo(CFG), CFG, semente)


def test_a_chave_nasce_desligada_e_tem_status():
    assert ConfigLutaCorpo().ligada is False and CONFIG_LUTA_CORPO.ligada is False
    assert PARAMETROS_LUTA_CORPO["ligada"][0] in ("PROPOSTO", "DECIDIDO")
    assert {f.name for f in fields(ConfigLutaCorpo)} == set(PARAMETROS_LUTA_CORPO)
    assert "luta_corpo" not in {f.name for f in fields(ConfigCorpo)}      # o dump da ConfigCorpo (gabarito de paridade) nao muda


def test_a_chave_exige_os_gestos_e_e_bool():
    with pytest.raises(ValueError, match="gestos"):
        Corpo.de_estado(Estado(), CFG, ConfigCorpo(ligada=True), cfg_luta=CL)
    with pytest.raises(TypeError):
        ConfigLutaCorpo(ligada=1)


@pytest.mark.parametrize("p", [0, 1, 7, 100, 333, 512, 1023, 1024])
def test_t_pl_1_a_dor_sobe_exatamente_div_arred(p):
    corpo = Corpo.de_estado(Estado(), CFG, CC, cfg_luta=CL)
    antes = dict(corpo.q)
    corpo.estimulo_luta(p)
    assert corpo.q["dor"] == antes["dor"] + div_arred(p * C, S)
    assert {k: v for k, v in corpo.q.items() if k != "dor"} == {k: v for k, v in antes.items() if k != "dor"}


def test_t_pl_1_corta_em_s_e_em_c():
    corpo = Corpo.de_estado(Estado(), CFG, CC, cfg_luta=CL)
    corpo.estimulo_luta(5000)                      # acima de S: cortado em S, a dor cheia
    assert corpo.q["dor"] == C
    corpo.estimulo_luta(1024)                      # acima de C: cortado em C
    assert corpo.q["dor"] == C


def test_t_pl_1_falha_alto():
    corpo = Corpo.de_estado(Estado(), CFG, CC, cfg_luta=CL)
    for ruim in (-1, 1.5, "3", True):
        with pytest.raises(ValueError):
            corpo.estimulo_luta(ruim)
    desligado = Corpo.de_estado(Estado(), CFG, CC)
    with pytest.raises(ValueError, match="luta_corpo"):
        desligado.estimulo_luta(10)


def test_o_evento_pl_ida_e_volta_e_falhas():
    e = resumo_luta(5, "muralha", -1, 300)
    assert (e.tipo, e.valor) == ("pl", "muralha|-1|300")
    assert ler_resumo_luta(e) == ("muralha", -1, 300)
    for args in (("", 0, 1), ("a|b", 0, 1), ("a", 2, 1), ("a", 0, -1), ("a", 0, 1.0)):
        with pytest.raises(ValueError):
            resumo_luta(0, *args)
    for valor in ("a|0", "a|0|1|2", "a|7|1", "a|0|-3", "|0|1"):
        with pytest.raises(ValueError):
            ler_resumo_luta(Evento(tick=0, tipo="pl", valor=valor))
    with pytest.raises(ValueError):
        ler_resumo_luta(Evento(tick=0, tipo="luta", valor="x|1"))


def test_no_motor_o_resumo_sobe_a_dor_sem_rng_e_o_replay_fecha():
    m = _motor(CL)
    m.avancar(40)
    m.resumo_luta("muralha", -1, 400)
    antes_rng = m._rng.getstate() if hasattr(m, "_rng") else None
    dor0 = m.corpo.q["dor"]
    m.resumo_luta("sombra", 0, 0)
    assert m.corpo.q["dor"] <= dor0                # vida perdida zero: a dor so decai, nada sobe
    if antes_rng is not None:
        assert m._rng.getstate() == antes_rng
    m.avancar(20)
    assert [e.tipo for e in m.log if e.tipo == "pl"] == ["pl", "pl"]
    r = reproduzir_mundo(m.log, lambda cfg=None: PoliticaInstintoMundo(CFG), CFG, 101, fabrica_motor=_fabrica(CL))
    assert r.corpo.q == m.corpo.q and r.estado() == m.estado()


def test_a_dor_do_evento_e_a_conta_no_corpo_do_motor():
    m = _motor(CL)
    dor0 = m.corpo.q["dor"]
    m.resumo_luta("muralha", -1, 512)
    assert m.corpo.q["dor"] == dor0 + div_arred(512 * C, S)


def test_chave_desligada_o_resumo_levanta_erro_e_nao_grava():
    for cc in (CONFIG_LUTA_CORPO, None):
        m = _motor(cc) if cc else MotorMundo(PoliticaInstintoMundo(CFG), CFG, 101, obediencia_desligada=True, cfg_mundo=CM)
        n = len(m.log)
        with pytest.raises(LutaSemChave):
            m.resumo_luta("muralha", -1, 400)
        assert len(m.log) == n
        log = LogDeEventos([resumo_luta(0, "muralha", -1, 400)])
        fab = _fabrica(cc) if cc else (lambda p, cfg, s: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM))
        with pytest.raises(LutaSemChave):
            reproduzir_mundo(log, lambda cfg=None: PoliticaInstintoMundo(CFG), CFG, 101, fabrica_motor=fab)


def test_desligada_a_vida_com_corpo_sai_igual_com_ou_sem_a_chave_no_config():
    """O campo novo desligado nao muda uma vida de hoje: mesmo corpo, mesma trajetoria."""
    a = _motor(CONFIG_LUTA_CORPO)
    b = _motor(ConfigLutaCorpo(ligada=False))
    a.avancar(300)
    b.avancar(300)
    assert a.corpo.q == b.corpo.q and a.estado() == b.estado()
