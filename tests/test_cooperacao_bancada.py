"""A bancada da cooperacao (docs/PLANO_ANALISE_V3_COOPERACAO.md, missao CB1): o orquestrador, as medidas e as travas, nas sementes dos testes.

- os oito braços montam as configuracoes do plano (secao 2.2);
- o B0 (a CO7 no grupo, nenhum cerebro com ela) e a vida da CO6: as mesmas decisoes;
- a oportunidade de quem mede e a mesma conta do escudo: no B1, as comidas que a medida marca sao as que o cerebro marcou como proibidas,
  decisao a decisao;
- a coleta casa uma vista por decisao; as medidas P1 a P6 saem; as travas da secao 5 passam (o D0 sem o k no limiar, o G-ESCUDO);
- a faixa principal so roda com o registro da analise."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_cooperacao_bancada as rb  # noqa: E402

from digilab.config import CONFIG_COOPERACAO_CO6, CONFIG_COOPERACAO_CO7  # noqa: E402

S = CONFIG_COOPERACAO_CO7.escala


def _decisoes(g):
    return {i: [[m["acao"], m["escolha"]] for m in mt.politica.motivos] for i, mt in sorted(g.motores.items())}


def test_os_oito_bracos():
    c7 = CONFIG_COOPERACAO_CO7
    assert rb.BRACOS == ("B0", "B1", "D0", "DM", "B1E", "B1U", "B1A", "RM")
    assert rb.configs("B0") == (c7, None, None)
    assert rb.configs("B1") == (c7, c7, c7)
    assert rb.configs("RM") == (c7, c7, None)
    g0, _, _ = rb.configs("D0")
    assert (g0.k_teto_crianca, g0.k_teto_adolescente, g0.k_teto_adulto) == (0, 0, 0)
    gm, _, _ = rb.configs("DM")
    assert gm.k_teto_adulto == c7.k_teto_adulto // 2 and gm.k_teto_crianca == c7.k_teto_crianca // 2
    _, e, _ = rb.configs("B1E")
    assert (e.w_univ, e.w_culpa, e.w_inveja, e.limiar_escudo) == (0, 0, 0, c7.limiar_escudo)
    _, u, _ = rb.configs("B1U")
    assert u.limiar_escudo == S > c7.k_teto_adulto and (u.w_culpa, u.w_inveja) == (0, 0) and u.w_univ == c7.w_univ
    _, a, _ = rb.configs("B1A")
    assert a.limiar_escudo == S and a.w_univ == 0 and (a.w_culpa, a.w_inveja) == (c7.w_culpa, c7.w_inveja)
    with pytest.raises(ValueError):
        rb.configs("B9")


def test_o_b0_e_a_vida_da_co6():
    """a CO7 no grupo e nenhum cerebro com ela: as decisoes da vida com a CO6 so (o G-SEM-DECISAO, nas vidas da bancada)"""
    g, _ = rb.rodar_vida(101, "B0", dias=2)
    orig = rb.configs
    rb.configs = lambda b: (CONFIG_COOPERACAO_CO6, None, None)
    try:
        g6, _ = rb.rodar_vida(101, "B0", dias=2)
    finally:
        rb.configs = orig
    assert _decisoes(g) == _decisoes(g6)


def test_a_oportunidade_e_a_conta_do_escudo():
    """no B1, as comidas que a medida marca sao as que o cerebro marcou como proibidas, decisao a decisao (a 202 tem oportunidades)"""
    g, c = rb.rodar_vida(202, "B1")
    marcadas = 0
    for i, mt in sorted(g.motores.items()):
        mot = mt.politica.motivos
        assert len(mot) == len(c.antes[i])
        for m, v in zip(mot, c.antes[i]):
            assert sorted({cid for cid, _ in v["proibidas"]}) == sorted(m["dever"]["proibidas"]), (i, m["dever"], v)
            marcadas += bool(v["proibidas"])
    assert marcadas > 0


@pytest.mark.parametrize("braco", ["B1", "D0", "RM"])
def test_a_coleta_as_medidas_e_as_travas(braco):
    g, c = rb.rodar_vida(202, braco)
    rb.conferir(g, c, braco)
    for i in g.motores:
        assert len(c.antes[i]) == len(c.depois[i]) > 0
    m = rb.medidas(g, c)
    assert set(m) == {"P1", "P1_oportunidades", "P1_favoraveis", "P1_por_pet", "P2", "P3", "P4", "P5", "P6"}
    assert m["P1_oportunidades"] == sum(p["oportunidades"] for p in m["P1_por_pet"].values())
    assert m["P1"] is None or 0.0 <= m["P1"] <= 1.0
    assert 0.0 <= m["P2"] <= 1.0 and 0.0 <= m["P6"] <= 2.0
    if braco == "D0":
        assert all(v["no_limiar"] == 0 for v in m["P5"].values())


def test_a_faixa_principal_so_com_o_registro():
    rb.checar_faixa([101, 91101, 91140], None)
    with pytest.raises(SystemExit):
        rb.checar_faixa([91201], None)
    rb.checar_faixa([91201], "abc1234")
