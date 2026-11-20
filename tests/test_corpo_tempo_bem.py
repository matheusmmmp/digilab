"""O "Tempo bem" (a primaria de bem-estar de 2026-11-20): a metrica em `digilab/metrics.py` e o resumo do replay de conferencia
(`experiments/run_v3_corpo_tempo_bem.py`). So funcoes puras: nenhuma vida e refeita aqui."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_corpo_c3 as c3  # noqa: E402
import run_v3_corpo_tempo_bem as tb  # noqa: E402
from digilab.metrics import (exaustao_nas_decisoes, janela_dias, privacao_nas_decisoes,  # noqa: E402
                             tempo_bem_nas_decisoes)

DIA = janela_dias(1, 1)


def test_tempo_bem_conta_so_a_decisao_sem_privacao_e_sem_exaustao():
    dec = [(0, 0.5, 0.5, 0.5),      # bem
           (15, 0.10, 0.5, 0.5),    # privacao pela fome
           (30, 0.5, 0.10, 0.5),    # privacao pela higiene
           (45, 0.5, 0.5, 0.20),    # exaustao sem privacao (energia entre 0,15 e 0,25)
           (60, 0.5, 0.5, 0.10),    # privacao e exaustao pela energia
           (75, 0.15, 0.15, 0.25)]  # nos limiares: bem (as duas regras sao "abaixo de")
    r = tempo_bem_nas_decisoes(dec, DIA)
    assert r == {"n": 6, "frac": 2 / 6, "frac_privacao": 3 / 6, "frac_exaustao": 2 / 6}


def test_tempo_bem_usa_as_regras_das_duas_medidas_de_hoje():
    dec = [(15 * k, (k * 7 % 11) / 10, (k * 3 % 11) / 10, (k * 5 % 11) / 10) for k in range(96)]
    r = tempo_bem_nas_decisoes(dec, DIA)
    assert r["frac_privacao"] == privacao_nas_decisoes([(t, f, h, e, 0.5) for t, f, h, e in dec], 0.15)["fracao_privacao"]
    assert r["frac_exaustao"] == exaustao_nas_decisoes([(t, e) for t, _, _, e in dec], DIA, 0.25)["frac"]
    # a privacao pela energia esta dentro da exaustao: o complemento do tempo bem e a uniao das duas
    uniao = sum(1 for _, f, h, e in dec if min(f, h, e) < 0.15 or e < 0.25) / len(dec)
    assert r["frac"] == pytest.approx(1 - uniao)


def test_tempo_bem_so_le_a_janela_e_falha_alto_sem_decisao():
    dec = [(0, 0.5, 0.5, 0.5), (1440, 0.0, 0.0, 0.0)]
    assert tempo_bem_nas_decisoes(dec, DIA)["frac"] == 1.0
    assert tempo_bem_nas_decisoes(dec, janela_dias(2, 2))["frac"] == 0.0
    with pytest.raises(ValueError):
        tempo_bem_nas_decisoes(dec, janela_dias(3, 3))
    with pytest.raises(ValueError):
        tempo_bem_nas_decisoes([(0, 1.5, 0.5, 0.5)], DIA)


def test_medidas_da_vida_separa_os_dias_1_a_14_dos_dias_8_a_14():
    passo, dias = 15, 14
    n = dias * 1440 // passo
    # a primeira semana toda em privacao, a segunda toda bem
    estados = [(0.05, 0.5, 0.5, 0.5, 1.0) if k * passo < 7 * 1440 else (0.5, 0.5, 0.5, 0.5, 1.0) for k in range(n)]
    m = tb.medidas_da_vida(estados, passo, dias)
    assert m["decisoes"] == n and m["tempo_bem"] == 0.5 and m["tempo_bem_8_14"] == 1.0
    assert m["privacao_vida"] == 0.5 and m["exaustao_vida"] == 0.0


def test_resumir_da_o_contraste_pareado_por_lugar_nas_12_e_nas_11_celulas():
    linhas = []
    for base in range(1, 5):
        for dono, lugar in c3.CELULAS:
            for braco, v in (("CTRL", 0.50), ("DTB", 0.60 if lugar == "comedouro" else 0.50 + 0.01 * base)):
                linhas.append({"vida": f"{braco}|{dono}|{lugar}|{base}", "braco": braco, "dono": dono, "lugar": lugar, "base": base,
                               "semente": base, "k": 0, "tempo_bem": v, "tempo_bem_8_14": v})
    r = tb.resumir(linhas)
    assert r["vidas"] == len(linhas) == 2 * 12 * 4
    assert r["tempo_bem"]["comedouro"]["media"] == pytest.approx(0.10) and r["tempo_bem"]["comedouro"]["n"] == 4
    assert r["tempo_bem"]["longe_fixo"]["media"] == pytest.approx(0.025)
    assert r["tempo_bem"]["as 12 celulas"]["niveis"]["CTRL"] == pytest.approx(0.50)
    assert set(r["por_celula"]) == {f"{d}|{lugar}" for d, lugar in c3.CELULAS}
    # as 11 distintas tiram uma celula do comedouro: a media por unidade muda
    assert r["tempo_bem"]["as 11 celulas"]["media"] != pytest.approx(r["tempo_bem"]["as 12 celulas"]["media"])
    assert r["vidas_no_piso_ou_teto"] == {"tempo_bem_0": 0, "tempo_bem_1": 0}
