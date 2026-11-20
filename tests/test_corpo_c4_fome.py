"""A fome nas decisoes (o descritivo da C4 acrescentado depois da aprovacao): a metrica em `digilab/metrics.py` e o resumo do replay
(`experiments/run_v3_corpo_c4_fome.py`). So funcoes puras: nenhuma vida e refeita aqui."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_corpo_c3 as c3  # noqa: E402
import run_v3_corpo_c4_fome as fo  # noqa: E402
from digilab.metrics import fome_nas_decisoes, janela_dias  # noqa: E402

DIA = janela_dias(1, 1)


def test_fome_e_o_complemento_da_observacao_e_o_corte_e_acima_do_limiar():
    dec = [(0, 1.0), (15, 0.75), (30, 0.5), (45, 0.25), (60, 0.0)]   # a fome: 0; 0,25; 0,5 (no teto, nao acima); 0,75; 1
    r = fome_nas_decisoes(dec, DIA)
    assert r == {"n": 5, "media": 0.5, "frac_acima": 2 / 5}
    assert fome_nas_decisoes(dec, DIA, limiar=0.85)["frac_acima"] == 1 / 5    # o corte da privacao: Observacao abaixo de 0,15


def test_fome_so_le_a_janela_e_falha_alto():
    dec = [(0, 1.0), (1440, 0.0)]
    assert fome_nas_decisoes(dec, DIA) == {"n": 1, "media": 0.0, "frac_acima": 0.0}
    assert fome_nas_decisoes(dec, janela_dias(2, 2)) == {"n": 1, "media": 1.0, "frac_acima": 1.0}
    with pytest.raises(ValueError):
        fome_nas_decisoes(dec, janela_dias(3, 3))
    with pytest.raises(ValueError):
        fome_nas_decisoes([(0, 1.5)], DIA)
    with pytest.raises(ValueError):
        fome_nas_decisoes(dec, DIA, limiar=1.5)


def test_fome_da_vida_le_o_primeiro_campo_do_estado_nos_dias_pedidos():
    passo, dias = 15, 2
    n = dias * 1440 // passo
    estados = [(0.8, 0.1, 0.1, 0.1, 1.0) if k * passo < 1440 else (0.2, 0.9, 0.9, 0.9, 1.0) for k in range(n)]
    m = fo.fome_da_vida(estados, passo, dias)
    assert m["decisoes_fome"] == n and m["fome_media"] == pytest.approx(0.5) and m["fome_acima_do_teto"] == 0.5


def test_resumir_da_os_niveis_e_o_contraste_por_lugar_e_por_celula_sem_classe():
    linhas = []
    for base in range(1, 5):
        for dono, lugar in c3.CELULAS:
            for braco, v in (("CTRL", 0.40), ("DTB", 0.50 if lugar == "comedouro" else 0.40 + 0.01 * base)):
                linhas.append({"vida": f"{braco}|{dono}|{lugar}|{base}", "braco": braco, "dono": dono, "lugar": lugar, "base": base,
                               "semente": base, "k": 1, "fome_media": v, "fome_acima_do_teto": v / 2})
    r = fo.resumir(linhas)
    assert r["vidas"] == len(linhas) == 2 * 12 * 4 and r["limiar_fome"] == 0.5
    lugar = r["fome_media"]["por_lugar"]
    assert set(lugar) == {"comedouro", "longe", "longe_fixo", "as 12 celulas", "as 11 celulas"}
    assert lugar["comedouro"]["DTB - CTRL"]["media"] == pytest.approx(0.10) and lugar["comedouro"]["DTB - CTRL"]["n"] == 4
    assert lugar["longe_fixo"]["DTB - CTRL"]["media"] == pytest.approx(0.025)
    assert lugar["as 12 celulas"]["niveis"]["CTRL"] == pytest.approx(0.40)
    assert "classe" not in lugar["comedouro"]["DTB - CTRL"]
    assert set(r["fome_media"]["por_celula"]) == {f"{d}|{lugar}" for d, lugar in c3.CELULAS}
    assert r["fome_acima_do_teto"]["por_lugar"]["comedouro"]["DTB - CTRL"]["media"] == pytest.approx(0.05)
