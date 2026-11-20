"""A viabilidade do corpo, a C5 da V3 (digilab/metrics.py::viabilidade_do_corpo; A6.8, item 4 e AD6-4 do adendo 6): a fracao dos ticks com
alguma das cinco variaveis abaixo do limiar da privacao e a menor necessidade (media e minimo), em vidas pequenas feitas a mao."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.metrics import JANELA_8_14, janela_dias, privacao_nas_decisoes, viabilidade_do_corpo  # noqa: E402

L = CONFIG_PADRAO.limiar_privacao


def _vida() -> list:
    """6 ticks: t0 tudo bem; t1 a saude cai a 0,10 (fora); t2 o humor em 0,15 (no limiar: dentro); t3 a fome a 0,05 (fora);
    t4 tudo em 0,5; t5 a energia a 0,0 (fora)"""
    return [(0, 0.9, 0.8, 0.7, 0.6, 0.5), (1, 0.9, 0.9, 0.9, 0.9, 0.10), (2, 0.9, 0.9, 0.9, 0.15, 0.9),
            (3, 0.05, 0.9, 0.9, 0.9, 0.9), (4, 0.5, 0.5, 0.5, 0.5, 0.5), (5, 0.9, 0.9, 0.0, 0.9, 0.9)]


def test_o_limiar_e_o_da_privacao_e_vale_estritamente_abaixo():
    assert L == 0.15
    r = viabilidade_do_corpo(_vida(), (0, 6), L)
    assert r["n_ticks"] == 6 and r["fracao_fora"] == 3 / 6                       # t1, t3 e t5; o 0,15 do t2 nao conta
    assert r["menor_minimo"] == 0.0
    assert r["menor_media"] == pytest.approx((0.5 + 0.10 + 0.15 + 0.05 + 0.5 + 0.0) / 6)


def test_a_janela_e_inicio_incluso_e_fim_excluso():
    r = viabilidade_do_corpo(_vida(), (1, 4), L)
    assert r["n_ticks"] == 3 and r["fracao_fora"] == 2 / 3 and r["menor_minimo"] == 0.05
    assert r["menor_media"] == pytest.approx((0.10 + 0.15 + 0.05) / 3)


def test_humor_e_saude_contam_e_a_privacao_de_hoje_nao():
    """o que a C5 muda: so a saude baixa (t1) e uma variavel fora aqui; a privacao das decisoes (fome, higiene, energia) nao a ve"""
    t1 = [_vida()[1]]
    assert viabilidade_do_corpo(t1, (0, 6), L)["fracao_fora"] == 1.0
    assert privacao_nas_decisoes([(0, 0.9, 0.9, 0.9, 0.9)], L)["fracao_privacao"] == 0.0


def test_vida_e_dias_8_a_14_sao_janelas_do_mesmo_vetor():
    ticks = [(t, 0.5, 0.5, 0.5, 0.5, 0.5) for t in range(0, 14 * 1440, 60)]
    ticks += [(14 * 1440 - 1, 0.5, 0.5, 0.5, 0.5, 0.05)]
    vida, tarde = viabilidade_do_corpo(ticks, janela_dias(1, 14), L), viabilidade_do_corpo(ticks, JANELA_8_14, L)
    assert vida["n_ticks"] == len(ticks) and tarde["n_ticks"] == sum(1 for t, *_ in ticks if t >= 7 * 1440)
    assert vida["fracao_fora"] == 1 / len(ticks) and tarde["fracao_fora"] == 1 / tarde["n_ticks"]
    assert tarde["menor_minimo"] == 0.05


def test_falha_alto():
    with pytest.raises(ValueError, match="sem tick"):
        viabilidade_do_corpo(_vida(), (100, 200), L)
    with pytest.raises(ValueError, match="5 "):
        viabilidade_do_corpo([(0, 0.5, 0.5, 0.5, 0.5)], (0, 1), L)
    with pytest.raises(ValueError, match="fora de"):
        viabilidade_do_corpo([(0, 0.5, 0.5, 1.2, 0.5, 0.5)], (0, 1), L)
    with pytest.raises(ValueError, match="janela"):
        viabilidade_do_corpo(_vida(), (5, 5), L)
