"""As contas da PET_VIVO no `digilab/metrics.py` (docs/PLANO_ANALISE_V3_PET_VIVO.md, secoes 4 e 7; secao 9: cada uma contra um caso feito a
mao). Sem vida: so numeros."""
from __future__ import annotations

import math

import pytest

from digilab import metrics as m

# tres comportamentos com 1, 2 e 3 unidades (o caso da secao 9): b0 = (10), b1 = (10, 10), b2 = (10, 10, 10)
UNIDADES = [(0, 10), (1, 10), (1, 10), (2, 10), (2, 10), (2, 10)]


def test_p_p1_tv_e_inflacao_no_caso_de_tres_comportamentos():
    W = m.pesos_por_comportamento(UNIDADES, 3)
    W1 = m.maximo_por_comportamento(UNIDADES, 3)
    assert W == [10, 20, 30] and W1 == [10, 10, 10]
    assert m.distribuicao(W) == [1 / 6, 2 / 6, 3 / 6]
    # TV = (|1/6 - 1/3| + |2/6 - 1/3| + |3/6 - 1/3|) / 2 = (1/6 + 0 + 1/6) / 2 = 1/6
    assert m.distancia_tv(W, W1) == 1 / 6
    assert m.inflacao([1 / 6, 2 / 6, 3 / 6], [1 / 3, 1 / 3, 1 / 3]) == pytest.approx([0.5, 1.0, 1.5])
    assert m.inflacao([0.2, 0.0], [0.4, 0.0]) == [0.5, None]
    assert m.unidades_ativas_por_comportamento(UNIDADES + [(0, 0)], 3) == [1, 2, 3]


def test_media_inteira_por_comportamento_e_proporcional_a_media():
    # medias 10, 15 e 20: o vetor inteiro W_b x (L / n_b), com L = 6
    W = m.media_inteira_por_comportamento([(0, 10), (1, 10), (1, 20), (2, 10), (2, 20), (2, 30), (2, 0)], 3)
    assert W == [60, 90, 120]
    assert m.distribuicao(W) == pytest.approx([10 / 45, 15 / 45, 20 / 45])


def test_a_tv_e_a_diferenca_sao_feitas_em_inteiros():
    p, q = [1, 2], [2, 1]
    assert m.distancia_tv(p, q) == 1 / 3
    assert m.diferenca_de_distribuicao(p, q) == [-1 / 3, 1 / 3]
    assert m.distancia_tv([3, 0], [7, 0]) == 0.0
    assert m.diferenca_de_distribuicao([2, 2], [5, 5]) == [0.0, 0.0]


def test_entropia_e_partes():
    assert m.entropia_bits([5, 5]) == 1.0
    assert m.entropia_bits([0, 7]) == 0.0
    assert m.partes_absolutas({"inato": 300, "habito": -100, "nov": 0}) == {"inato": 0.75, "habito": 0.25, "nov": 0.0}
    assert m.partes_absolutas({"inato": 0}) == {"inato": 0.0}


def test_os_pesos_fora_do_contrato_falham_alto():
    with pytest.raises(ValueError):
        m.distribuicao([0, 0])
    with pytest.raises(ValueError):
        m.distancia_tv([1, -1], [1, 1])
    with pytest.raises(ValueError):
        m.distancia_tv([1, 1], [1, 1, 1])
    with pytest.raises(ValueError):
        m.distribuicao([1.5, 1])


def test_mediana_e_quantis():
    assert m.mediana([3, 1, 2]) == 2
    assert m.mediana([4, 1, 2, 3]) == 2.5
    assert m.mediana([]) is None
    assert m.quantis([5, 1, 4, 2, 3], (0.1, 0.5, 0.9)) == [1, 3, 5]
    with pytest.raises(ValueError):
        m.quantis([], (0.5,))


def test_tabela_do_alivio_pede_media_e_limite_de_baixo_positivos():
    tab = m.tabela_do_alivio({("comer", "fome"): [10.0, 12.0, 11.0], ("comer", "tedio"): [-1.0, 2.0, -0.5],
                              ("dormir", "energia"): [5.0]})
    assert tab[("comer", "fome")]["alivia"] is True
    assert tab[("comer", "tedio")]["alivia"] is False
    assert tab[("dormir", "energia")]["alivia"] is False            # uma vida so: sem IC, nao alivia
    assert tab[("comer", "fome")]["media"] == 11.0


def test_coerencia_sensibilidade_coerente_e_se_c_no_caso_feito_a_mao():
    # 4 decisoes; a massa movida para o comer soma 0,8 e para o explorar 0,2; a TV soma 1,0
    movido = {"comer": 0.8, "explorar": 0.2, "dormir": 0.0}
    assert m.coerencia(movido, ["comer"], 1.0) == 0.8
    assert m.sensibilidade_coerente(movido, ["comer"], 4) == 0.2
    assert m.coerencia(movido, [], 1.0) is None
    assert m.coerencia(movido, ["comer"], 0.0) is None
    assert m.sensibilidade_coerente(movido, ["comer"], 0) is None
    assert m.se_c({"fome": 0.2, "energia": 0.4, "tedio": None}) == pytest.approx(0.3)
    assert m.se_c({"fome": None}) is None


def test_um_cerebro_sem_coluna_de_corpo_tem_se_c_zero():
    # sem coluna de corpo, a falta nao muda os pesos: P com falta + Delta = P com falta - Delta em toda decisao
    W = [3, 5, 0, 2]
    movido = {"a": 0.0, "b": 0.0}
    tv = 0.0
    for _ in range(10):
        d = m.diferenca_de_distribuicao(W, W)
        tv += m.distancia_tv(W, W)
        movido["a"] += max(0.0, d[0])
        movido["b"] += max(0.0, d[1])
    assert tv == 0.0
    assert m.sensibilidade_coerente(movido, ["a"], 10) == 0.0
    assert m.se_c({"fome": m.sensibilidade_coerente(movido, ["a"], 10)}) == 0.0
    assert m.coerencia(movido, ["a"], tv) is None


def test_revalorizacao_e_um_delta_p_do_comer():
    # a RV de uma decisao: P(comer | fome + Delta) - P(comer | fome - Delta)
    com_fome, sem_fome = [1, 3, 0], [2, 2, 0]                       # comer e o indice 1
    assert m.diferenca_de_distribuicao(com_fome, sem_fome)[1] == 0.25
    assert not math.isnan(m.entropia_bits(com_fome))
