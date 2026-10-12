"""BN-8 (decisao do Matheus, 2026-10-11): o banheiro mais perto de onde o pet passa o dia, ao alcance de uma decisao (60) do comedouro,
sem mudar o contrato de decisao nem o teto de pesos. A ida que continua (#270) fica.

Gates: G2 (so a area padrao mudou: as vidas do gabarito gravado antes, tests/gabaritos/banheiro_perto_antes.json, com a area de antes
dada explicitamente, saem iguais byte a byte; a chave desligada e a vida de hoje, pelos gabaritos de sempre, na suite) e a geometria da
area nova. So as sementes dos testes.
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
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_banheiro_perto as gbp  # noqa: E402
from digilab.config import CONFIG_BANHEIRO_LIGADA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigBanheiro  # noqa: E402
from digilab.instinto_banheiro import PARAMETROS_BANHEIRO  # noqa: E402
from digilab.mundo import (ZONA_BANHEIRO, centro_da_celula, distancia, faixa_do_banheiro, no_banheiro, ponto_do_banheiro,  # noqa: E402
                           zona_da_necessidade)

CM = CONFIG_MUNDO_LIGADA
CB = CONFIG_BANHEIRO_LIGADA
GABARITO = json.loads(gbp.ARQUIVO.read_text(encoding="utf-8"))


# ================================================================== a area nova
def test_a_area_padrao_e_a_bn8():
    assert (ConfigBanheiro().celulas_x, ConfigBanheiro().celulas_y) == ((8, 12), (18, 20))
    assert (CB.celulas_x, CB.celulas_y) == ((8, 12), (18, 20))
    assert (gbp.CB_CANTO.celulas_x, gbp.CB_CANTO.celulas_y) == ((0, 3), (0, 5))           # a de antes, so nos testes
    assert all(PARAMETROS_BANHEIRO[k][0] == "PROPOSTO" and "BN-8" in PARAMETROS_BANHEIRO[k][1] for k in ("celulas_x", "celulas_y"))


def test_o_banheiro_novo_ao_alcance_do_comedouro_dentro_da_casa():
    """do comedouro (onde o pet passa o dia) o ponto do banheiro esta a 40 subunidades, abaixo do alcance de uma decisao (60); a area
    fica dentro da casa e nao cobre o comedouro nem o ninho (a necessidade deixada no banheiro nao incomoda quem esta neles)"""
    assert faixa_do_banheiro(CB, CM) == (128, 207, 288, 335)
    casa = CM.layout.regioes[0]
    assert casa[0] == "casa" and casa[1] <= CB.celulas_x[0] <= CB.celulas_x[1] <= casa[2]
    alcance = CM.velocidade * CONFIG_PADRAO.intervalo_decisao_ticks
    assert alcance == 60
    cx, cy = centro_da_celula(CM.layout.comedouro, CM)
    bx, by = ponto_do_banheiro(cx, cy, CB, CM)
    assert (bx, by) == (168, 288) and distancia(bx - cx, by - cy) == 40
    assert distancia(bx - cx, by - cy) <= alcance
    for lugar in (CM.layout.comedouro, CM.layout.ninho):
        x, y = centro_da_celula(lugar, CM)
        assert not no_banheiro(x, y, CB, CM) and zona_da_necessidade(x, y, CB, CM) != ZONA_BANHEIRO
    nx, ny = centro_da_celula(CM.layout.ninho, CM)
    assert distancia(*(a - b for a, b in zip(ponto_do_banheiro(nx, ny, CB, CM), (nx, ny)))) == 68


def test_o_motor_anda_ao_banheiro_do_comedouro_numa_decisao():
    """o pet no comedouro que escolhe o banheiro chega e alivia dentro na mesma decisao (sem ida pendente)"""
    import test_banheiro_mundo as tb
    pol = tb.Roteiro([tb.AcaoPet.ALIVIAR], "banheiro")
    m = tb.fm(CB)(pol, tb.CONFIG_PADRAO, 101)
    m.pet = centro_da_celula(CM.layout.comedouro, CM)
    m.corpo.q["vontade"] = 300000
    m.avancar(15)
    assert m.alivios == [{"tick": 0, "dentro": True, "urgente": False, "alvo": "banheiro", "distancia": 40, "recolhido": False}]
    assert m.pet == (168, 288) and m.idas_banheiro == []


# ================================================================== G2: so a area mudou
@pytest.mark.parametrize("chave,caso", list(gbp.casos()), ids=[c for c, _ in gbp.casos()])
def test_g2_com_a_area_de_antes_as_vidas_de_antes(chave, caso):
    with gbp.canto():
        assert gbp.registro(*caso, cbh=gbp.CB_CANTO) == GABARITO[chave]


def test_o_canto_volta_a_bancada_ao_padrao():
    with gbp.canto():
        assert bv.CONFIG_BANHEIRO_LIGADA == gbp.CB_CANTO
    assert bv.CONFIG_BANHEIRO_LIGADA == CB == replace(gbp.CB_CANTO, celulas_x=(8, 12), celulas_y=(18, 20))
