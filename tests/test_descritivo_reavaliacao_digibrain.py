"""O descritivo da reavaliacao do DigiBrain modular (experiments/descritivo_reavaliacao_digibrain.py): o artefato se refaz igual dos
medidas.json do git, as duas fracoes do G-MVP batem com o resultado.json, a identidade da secao 1 fecha, e as contas pequenas (a faixa do
d0 e os pares das acoes sem r) dao o esperado em casos feitos a mao. Nenhuma vida roda."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import descritivo_reavaliacao_digibrain as dr  # noqa: E402


@pytest.fixture(scope="module")
def descritivo() -> dict:
    return dr.descrever(dr._ler(dr.ENTRADA), dr._ler(dr.RESULTADO), dr._ler(dr.PILOTO), dr._ler(dr.AVALIACAO))


def test_o_artefato_se_refaz_igual(descritivo):
    assert dr.SAIDA.read_text(encoding="utf-8") == bv._dump(descritivo)


def test_as_fracoes_do_g_mvp_sao_as_do_resultado(descritivo):
    res = dr._ler(dr.RESULTADO)
    c = descritivo["conferencia_com_o_resultado"]
    assert c["G-MVP"] == pytest.approx(res["G-MVP"]["estimativa"], rel=1e-12)
    assert c["G-MVP-EP"] == pytest.approx(res["G-MVP-EP"]["estimativa"], rel=1e-12)
    todas = descritivo["1_episodio_contra_racao_M3"]["todas"]
    # cada unidade tem uma vida por celula: a fracao das vidas e a media das unidades
    assert todas["frac_vidas_com_cadeia"]["racao"] == pytest.approx(c["G-MVP"], rel=1e-12)
    assert todas["frac_vidas_com_cadeia"]["episodio"] == pytest.approx(c["G-MVP-EP"], rel=1e-12)


def test_a_identidade_fecha_em_todo_bloco(descritivo):
    for nome in ("1_episodio_contra_racao_M3", "3_A11_ao_lado"):
        s = descritivo[nome]
        blocos = [s["todas"], *s["por_dono"].values(), *s["por_lugar"].values(), *s["por_celula"].values()]
        for b in blocos:
            i = b["identidade"]
            assert math.isclose(i["fechadas_por_episodio_fechado"] * i["taxa_episodio"] * i["episodios_por_racao_elegivel"],
                                i["taxa_racao"], rel_tol=1e-12)
            assert sum(b["tabela_2x2"].values()) == b["vidas"]
            r = b["refeicoes_de_racao"]
            assert r["fecharam_um_episodio"] + r["fora_de_episodio"] + r["no_episodio_sem_fechar"] == r["total"]


def test_a_faixa_do_d0():
    g = {"raio_visao": 96, "corte_d0": 384}
    assert [dr._faixa_d0(d, g) for d in (0, 96, 97, 384, 385)] == ["na_visao", "na_visao", "no_cheiro", "no_cheiro", "alem_do_cheiro"]


def test_os_pares_sem_r_a_mao():
    # 10 pares r > 0 (4 ficam), 30 pares r <= 0 no total (12 ficam); deles, 10 de acoes com r possivel (3 ficam): os 20 sem r, 9 ficam
    v = {"vida": "x", "repeticao": {"n_pos": 10, "n_nao_pos": 30, "p_pos": 0.4, "p_nao_pos": 0.4, "indice": 0.0},
         "repeticao_r_possivel": {"total": {"n_pos": 10, "n_nao_pos": 10, "indice": 0.4 - 0.3}}}
    s = dr._sem_r(v)
    assert s["pares"] == 20 and s["fica"] == pytest.approx(9 / 20) and s["frac_dos_pares"] == pytest.approx(20 / 40)
    # sem pares r <= 0 nas acoes com r possivel: os sem r sao todo o lado r <= 0
    v["repeticao_r_possivel"]["total"] = {"n_pos": 10, "n_nao_pos": 0, "indice": None}
    assert dr._sem_r(v)["fica"] == pytest.approx(0.4)
    # o lado r > 0 tem de ser o mesmo
    v["repeticao_r_possivel"]["total"]["n_pos"] = 9
    with pytest.raises(RuntimeError):
        dr._sem_r(v)


def test_o_descritivo_le_so_os_artefatos_e_tem_o_rotulo(descritivo):
    assert "exploratorio" in descritivo["rotulo"] and "sem gate" in descritivo["rotulo"]
    for caminho, sha in descritivo["fontes"].items():
        assert bv._sha(RAIZ / caminho) == sha
    assert descritivo["vidas"] == 7200
    assert json.loads(dr.SAIDA.read_text(encoding="utf-8"))["script"]["sha256"] == bv._sha(Path(dr.__file__))
