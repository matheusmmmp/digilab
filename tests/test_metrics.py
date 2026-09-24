"""Etapa 5 - metricas compartilhadas."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab import PoliticaInstinto  # noqa: E402
from digilab.arena import ResultadoPartida  # noqa: E402
from digilab.metrics import (  # noqa: E402
    bootstrap_ic,
    bradley_terry,
    divergencia_politicas,
    estados_sonda,
    jsd_bits,
    taxa_vitoria,
)
from digilab.policies import PoliticaBandit  # noqa: E402


def _p(a, b, v):
    return ResultadoPartida(0, a, b, v, ())


def test_taxa_vitoria_conta_empate_como_meio():
    t = taxa_vitoria([_p("x", "y", "a"), _p("x", "y", "empate")])
    assert t["x"]["taxa"] == 0.75 and t["y"]["taxa"] == 0.25


def test_bradley_terry_ordena_e_da_erro_padrao():
    partidas = [_p("forte", "fraco", "a")] * 15 + [_p("forte", "fraco", "b")] * 5
    bt = bradley_terry(partidas)
    assert bt["forte"]["forca_log"] > bt["fraco"]["forca_log"]
    assert bt["forte"]["erro_padrao"] > 0
    # razao de chances ~ 3 -> diferenca de forca ~ log 3
    diff = bt["forte"]["forca_log"] - bt["fraco"]["forca_log"]
    assert abs(diff - 1.0986) < 0.05
    # erro padrao do contraste com 20 jogos: ordem de 1/sqrt(20 * 0.75 * 0.25) / 2, nao a translacao livre
    assert bt["forte"]["erro_padrao"] < 0.5


def test_jsd_limites():
    p = {"a": 1.0, "b": 0.0}
    q = {"a": 0.0, "b": 1.0}
    assert jsd_bits(p, p) == 0.0
    assert abs(jsd_bits(p, q) - 1.0) < 1e-12


def test_politicas_identicas_divergem_zero_com_numeros_comuns():
    estados = estados_sonda(8, 1)
    div, _ = divergencia_politicas({"i1": PoliticaInstinto(), "i2": PoliticaInstinto()}, estados, 50, 3)
    assert div.pares[("i1", "i2")] == 0.0


def test_bandit_recem_nascido_proximo_do_instinto():
    estados = estados_sonda(16, 1)
    div, _ = divergencia_politicas({"b": PoliticaBandit(), "i": PoliticaInstinto()}, estados, 200, 3)
    assert div.pares[("b", "i")] < 0.15


def test_bootstrap_ic_contem_media_e_falha_com_uma_unidade():
    ic = bootstrap_ic([0.4, 0.5, 0.6, 0.55, 0.45], 2000, 1, 0.95)
    assert ic["ic_inferior"] <= ic["media"] <= ic["ic_superior"]
    with pytest.raises(ValueError):
        bootstrap_ic([0.5], 100, 1, 0.95)
