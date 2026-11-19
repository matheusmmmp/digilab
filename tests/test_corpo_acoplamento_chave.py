"""A subchave da CORPO_ACOPLAMENTO, a opcao D (docs/TAREFA_V3_CORPO_ACOPLAMENTO.md, secao 10; D-CA-2 e D-CA-5): ligada, a falta de
combustivel sobe a fome em `falta_fome`, e nao o cansaco. O gabarito da chave desligada esta em tests/test_gabarito_corpo_acoplamento.py."""
from __future__ import annotations

import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import sonda_v3_corpo_acoplamento as SA  # noqa: E402
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_CORPO_DRIVES,  # noqa: E402
                            CONFIG_CORPO_METABOLISMO, CONFIG_PADRAO, PARAMETROS_ACOPLAMENTO_CORPO, ConfigAcoplamentoCorpo)
from digilab.corpo import Corpo  # noqa: E402
from digilab.state import Estado  # noqa: E402

CC = CONFIG_CORPO_METABOLISMO


def _corpo(ca=None, combustivel=None):
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, cfg_acoplamento=ca)
    if combustivel is not None:
        c.q["combustivel"] = combustivel
        c.q["reserva"] = 0
    return c


def test_o_status_cobre_os_campos():
    assert {f.name for f in fields(ConfigAcoplamentoCorpo)} == set(PARAMETROS_ACOPLAMENTO_CORPO)
    assert all(st in ("PROPOSTO", "DECIDIDO") and fonte for st, fonte in PARAMETROS_ACOPLAMENTO_CORPO.values())
    assert CONFIG_ACOPLAMENTO_CORPO.ligada is False and CONFIG_ACOPLAMENTO_CORPO_LIGADA.ligada is True


@pytest.mark.parametrize("kw, erro", [({"ligada": 1}, TypeError), ({"falta_fome": 0}, ValueError), ({"falta_fome": 2.5}, ValueError)])
def test_a_config_falha_alto(kw, erro):
    with pytest.raises(erro):
        ConfigAcoplamentoCorpo(**kw)


def test_ligada_exige_o_metabolismo():
    with pytest.raises(ValueError, match="metabolismo"):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, CONFIG_CORPO_DRIVES, cfg_acoplamento=CONFIG_ACOPLAMENTO_CORPO_LIGADA)
    with pytest.raises(TypeError):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, cfg_acoplamento=object())


def test_a_ponte_troca_de_alvo():
    assert dict(_corpo().grafo.emissor("falta_combustivel").efeitos) == {"cansaco": CC.falta_cansaco}
    ca = replace(CONFIG_ACOPLAMENTO_CORPO_LIGADA, falta_fome=321)
    assert dict(_corpo(ca).grafo.emissor("falta_combustivel").efeitos) == {"fome": 321}


@pytest.mark.parametrize("combustivel", [CC.falta_limiar - 1, CC.falta_limiar, CC.armazenar_limiar])
def test_um_tick_com_e_sem_a_falta(combustivel):
    hoje, d = _corpo(combustivel=combustivel), _corpo(CONFIG_ACOPLAMENTO_CORPO_LIGADA, combustivel)
    hoje.passo(Estado())
    d.passo(Estado())
    falta = combustivel - CC.gasto_basal_acordado < CC.falta_limiar      # a falta le o combustivel depois do basal
    assert d.q["cansaco"] == hoje.q["cansaco"] - (CC.falta_cansaco if falta else 0)
    assert d.q["fome"] == hoje.q["fome"] + (CONFIG_ACOPLAMENTO_CORPO_LIGADA.falta_fome if falta else 0)
    assert {k: v for k, v in d.q.items() if k not in ("fome", "cansaco")} == {k: v for k, v in hoje.q.items() if k not in ("fome", "cansaco")}


def test_a_vida_com_a_chave():
    """ligada, a vida muda, sai igual duas vezes, e a sonda nao ve cansaco pela falta"""
    a = SA.viver("REL", "atencioso", "longe_fixo", 101, 2, instrumentar=False, cfg_acoplamento=CONFIG_ACOPLAMENTO_CORPO_LIGADA)
    b = SA.viver("REL", "atencioso", "longe_fixo", 101, 2, instrumentar=False, cfg_acoplamento=CONFIG_ACOPLAMENTO_CORPO_LIGADA)
    hoje = SA.viver("REL", "atencioso", "longe_fixo", 101, 2, instrumentar=False)
    assert a[0].log.para_jsonl() == b[0].log.para_jsonl()
    assert a[0].serie_corpo != hoje[0].serie_corpo
    v = SA.uma_vida("REL", "atencioso", "longe_fixo", 101, 2, CONFIG_ACOPLAMENTO_CORPO_LIGADA)
    assert v["acum_final"]["falta_combustivel"] == 0 and v["ticks_falta_combustivel"] == 0
    assert v["ticks_combustivel_abaixo_do_limiar"] > 0          # a falta acontece; so nao cansa


def test_o_motor_confere_a_chave():
    from digilab.mundo import MotorMundo
    from digilab.motor_corpo import com_corpo
    from digilab.temperamento import NEUTRO
    with pytest.raises(TypeError, match="cfg_acoplamento_corpo"):
        com_corpo(MotorMundo)(None, CONFIG_PADRAO, 1, NEUTRO, "brasa", cfg_corpo=CC, cfg_acoplamento_corpo="sim")


def test_o_gabarito_da_paridade_reproduz():
    import exportar_gabarito_corpo_acoplamento as gab
    assert gab.ARQUIVO.read_text(encoding="utf-8") == gab.texto()
