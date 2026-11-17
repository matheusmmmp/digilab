"""O credito do carinho no DigiBrain modular (docs/TAREFA_V3_ELOGIO.md, etapa 2): a `ConfigElogio`, o gancho `mudanca_no_corpo` so com a
chave, o sinal na janela de decisoes, as duas rotas (o P2 e o desfecho do P1), o P0 e os donos dos bracos (experiments/elogio.py). O byte
a byte com a chave desligada esta no tests/test_gabarito_elogio.py."""
from __future__ import annotations

import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import elogio as el  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_ELOGIO, CONFIG_ELOGIO_LIGADA, CONFIG_PADRAO, PARAMETROS_ELOGIO,  # noqa: E402
                            ConfigElogio)
from digilab.digibrain import DigiBrain  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
DIAS = 6


@pytest.fixture(scope="module")
def vida_imed():
    return el.viver("E-imed", 101, DIAS, ConfigElogio(ligada=True, janela=4))


def test_a_config_padrao_desligada_e_o_status_de_cada_campo():
    assert CONFIG_ELOGIO.ligada is False and CONFIG_ELOGIO_LIGADA.ligada is True
    assert set(PARAMETROS_ELOGIO) == {f.name for f in fields(ConfigElogio)}
    assert all(st in ("PROPOSTO", "DECIDIDO") for st, _ in PARAMETROS_ELOGIO.values())
    with pytest.raises(TypeError):
        ConfigElogio(ligada=1)
    with pytest.raises(ValueError):
        ConfigElogio(ganho=-1)
    with pytest.raises(ValueError):
        ConfigElogio(janela=0)
    with pytest.raises(TypeError):
        DigiBrain(CONFIG_PADRAO, orq.config_do_braco("REL", None, True), el.CM, semente=101, cfg_elogio={"ligada": True})


def test_desligada_o_cerebro_nao_tem_o_gancho():
    """sem o gancho, o motor nao chama nada no carinho (MotorCorpo._gesto: getattr(..., None)), e a vida e a de hoje"""
    cd = orq.config_do_braco("REL", None, True)
    for cfg in (None, CONFIG_ELOGIO):
        c = DigiBrain(CONFIG_PADRAO, cd, el.CM, semente=101, cfg_elogio=cfg)
        assert not hasattr(c, "mudanca_no_corpo")
        assert "elogio" not in c.estado_interno()
    reg = orq.Registro(DigiBrain(CONFIG_PADRAO, cd, el.CM, semente=101), S)
    assert getattr(reg, "mudanca_no_corpo", None) is None
    ligado = DigiBrain(CONFIG_PADRAO, cd, el.CM, semente=101, cfg_elogio=CONFIG_ELOGIO_LIGADA)
    assert callable(ligado.mudanca_no_corpo)


def test_p0_o_modular_le_a_solidao_e_o_carinho_da_sinal(vida_imed):
    motor, c, dono, _ = vida_imed
    assert {"solidao", "estresse"} <= set(c.m.sens.receptores)
    assert len(c.elogios) == len(dono.carinhos) == motor.mudancas > 0
    assert all(e["sinal"] != 0 for e in c.elogios)
    assert all(e["delta"]["solidao"] <= 0 for e in c.elogios)


def test_o_credito_vai_a_janela_com_o_peso_linear(vida_imed):
    _, c, _, _ = vida_imed
    W = c.cel.janela
    for e in c.elogios:
        js = [x["j"] for x in e["creditos"]]
        assert js == list(range(len(js))) and len(js) <= W
        for x in e["creditos"]:
            assert x["peso"] == S - _div(x["j"] * S, W)
            assert x["r"] == _div(e["f_n"] * x["peso"], S)
            assert x["decisao"] == e["k"] - 1 - x["j"]          # j = 0 e a ultima decisao antes do carinho
            assert x["p2"] is not None and x["p2"]["b"] == c.motivos[x["decisao"]]["escolha"][0]


def test_o_carinho_imediato_cai_na_decisao_que_comeu_x_e_soma_ao_desfecho(vida_imed):
    _, c, dono, _ = vida_imed
    j0 = [x for e in c.elogios for x in e["creditos"] if x["j"] == 0]
    assert j0 and all(x["classe"] == dono.fruta for x in j0)
    for e in c.elogios:
        x = e["creditos"][0]
        p1 = x["p1"]
        assert p1["regra"] == "P1-elogio" and p1["classe"] == dono.fruta
        i = c.m.sens.receptores.index("solidao")
        assert p1["depois"][i] <= p1["antes"][i]                # o pet passa a esperar de X menos solidao


def test_sem_o_ganho_o_credito_e_zero():
    _, c, dono, _ = el.viver("E-imed", 101, DIAS, ConfigElogio(ligada=True, ganho=0))
    assert c.elogios and all(x["r"] == 0 and x["p1"]["abs"] == 0 for e in c.elogios for x in e["creditos"])


def test_o_sorteado_nao_olha_o_consumo():
    passos = el.passos_sorteados(7, el.passos_da_vida(DIAS) // 2, 101)
    assert passos == el.passos_sorteados(7, el.passos_da_vida(DIAS) // 2, 101) and len(passos) == 7
    for s in (101, 202):
        _, _, dono, _ = el.viver("E-sorteado", s, DIAS, CONFIG_ELOGIO_LIGADA, passos)
        assert [p for p, _ in dono.carinhos] == passos and {x for _, x in dono.carinhos} == {"sorteado"}


def test_o_par_tem_o_mesmo_numero_de_carinhos():
    imed, sorteado = el.viver_par(101, DIAS, CONFIG_ELOGIO_LIGADA)
    assert len(imed[2].carinhos) == len(sorteado[2].carinhos) > 0
    assert len(imed[1].elogios) == len(sorteado[1].elogios)


def test_o_contingente_so_na_primeira_metade_e_o_atraso_so_dos_tres():
    metade = el.passos_da_vida(DIAS) // 2
    for braco in ("E-imed", "E-atraso", "E-incons"):
        for s in (101, 202):
            _, _, dono, _ = el.viver(braco, s, DIAS, CONFIG_ELOGIO_LIGADA)
            assert all(p < metade for p, _ in dono.carinhos)
            assert {x for _, x in dono.carinhos} <= {"E-imed": {"imed"}, "E-atraso": {"atraso"}, "E-incons": {"imed", "outra", "antes"}}[braco]
    d = el.DonoElogioFruta("E-atraso", "a", 101, metade)
    assert {el.ATRASOS[d.rng_atraso.randrange(3)] for _ in range(60)} == set(el.ATRASOS)


def test_a_fruta_x_e_os_donos_falham_alto():
    assert {el.fruta_elogio(s) for s in range(101, 140)} == {"a", "b", "c"}
    with pytest.raises(ValueError):
        el.DonoElogioFruta("E-x", "a", 101, 10)
    with pytest.raises(ValueError):
        el.DonoElogioFruta("E-imed", "a", 101, 10, [1])
    with pytest.raises(ValueError):
        el.DonoElogioFruta("E-sorteado", "a", 101, 10)
    with pytest.raises(RuntimeError):
        el.DonoElogioFruta("E-imed", "a", 101, 10).acoes({})


def test_o_replay_da_vida_com_a_chave_ligada(vida_imed):
    motor, _, _, fab = vida_imed
    orq.conferir_replay(motor, fab, 101, motor.log.para_jsonl())


def _div(n: int, d: int) -> int:
    from digilab.digibrain.base import div_arred
    return div_arred(n, d)
