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
    assert set(m) == {"P1", "P1_oportunidades", "P1_favoraveis", "P1_por_pet", "P2", "P3", "P4", "P5", "P6", "culpa_inveja"}
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


def _med(p1, op=4, k=(100.0,), p3=0.03, pa=None):
    pa = pa if pa is not None else p1
    fav = None if p1 is None else round(p1 * op)
    return {"P1": p1, "P1_oportunidades": 0 if p1 is None else op, "P1_favoraveis": fav or 0,
            "P1_por_pet": {"A": {"oportunidades": 0 if pa is None else op, "favoraveis": 0 if pa is None else round(pa * op)},
                           "B": {"oportunidades": 0, "favoraveis": 0}},
            "P2": 0.5, "P3": {"A": p3, "B": p3}, "P4": {"contencao": 1, "encostar": 0, "disputa_anti": 0},
            "P5": {"A": {"k_medio": {"crianca": k[0]}, "no_limiar": 0.0}, "B": {"k_medio": {}, "no_limiar": 0.0}}, "P6": 0.1}


def test_a_analise_aplica_a_regra_escrita_antes():
    """dados feitos a mao: o B1 com +0,5 na P1, a dose em escada, o A com k e P1 maiores no B1 que no RM, o custo igual"""
    import analisar_v3_cooperacao_bancada as an
    por = {}
    for s in range(40):
        por[s] = {"B0": _med(0.0), "B1": _med(0.5, k=(300.0,)), "D0": _med(0.0), "DM": _med(0.25), "RM": _med(0.25, k=(100.0,)),
                  "B1E": _med(0.5), "B1U": _med(0.0), "B1A": _med(0.0)}
    r = an.analisar(por)
    assert r["H-EMERGE"]["leitura"] == "CONFIRMA" and abs(r["H-EMERGE"]["diferenca"] - 0.5) < 1e-9
    assert r["H-DOSE"]["leitura"] == "CONFIRMA" and r["H-DOSE"]["ordem"]
    assert r["H-REP"]["leitura"] == "CONFIRMA"
    assert r["H-CUSTO"]["leitura"] == "CONFIRMA"
    assert r["R-ESCUDO"]["B1E"]["diferenca_P1_contra_B0"] == 0.5 and r["R-ESCUDO"]["B1U"]["diferenca_P1_contra_B0"] == 0.0
    poucos = {s: por[s] for s in range(10)}
    assert an.analisar(poucos)["H-EMERGE"]["leitura"] == "INCONCLUSIVO POR PREMISSA"
    iguais = {s: {**por[s], "B1": _med(0.0)} for s in range(40)}
    assert an.analisar(iguais)["H-EMERGE"]["leitura"] == "NAO CONFIRMA"


# ------------------------------------------------------------------ o adendo 1 (secao 12 do plano): o irmao aleatorio
def test_o_adendo_1_o_irmao_aleatorio_e_a_co7_so_no_a():
    g, c = rb.rodar_vida(202, "B1", mundo="irmao_aleatorio")
    assert sorted(c.antes) == ["A"] and sorted(c.depois) == ["A", "B"]
    assert g.registro.cabecalho["pets"]["B"]["cerebro"] == "aleatorio" and not hasattr(g.motores["B"].politica, "motivos")
    rb.conferir(g, c, "B1")
    m = rb.medidas(g, c)
    assert set(m["P1_por_pet"]) == {"A"} and "proprio_comeu" in m["P1_por_pet"]["A"]
    assert m["P1_por_pet"]["A"]["oportunidades"] > 0                      # a situacao acontece (12.1)
    assert m["culpa_inveja"]["A"]["decisoes"] > 0 and 0.0 <= m["culpa_inveja"]["A"]["culpa"] <= 1.0
    g0, c0 = rb.rodar_vida(202, "B0", mundo="irmao_aleatorio")
    assert rb.medidas(g0, c0)["culpa_inveja"]["A"] is None               # sem a CO7 no cerebro, nada a contar
    with pytest.raises(ValueError):
        rb.rodar_vida(202, "RM", mundo="irmao_aleatorio")
    with pytest.raises(ValueError):
        rb.rodar_vida(202, "B0", mundo="outro")


def test_o_adendo_1_a_faixa_e_a_analise_do_pet_a():
    import analisar_v3_cooperacao_bancada as an
    rb.checar_faixa([92101, 92140], None)
    with pytest.raises(SystemExit):
        rb.checar_faixa([92201], None)
    por = {}
    for s in range(40):
        b0 = _med(0.0, pa=0.0)
        b1 = _med(0.0, pa=0.5)                                            # so a P1 do A sobe
        por[s] = {"B0": b0, "B1": b1, "D0": _med(0.0, pa=0.0), "DM": _med(0.0, pa=0.25),
                  "B1E": _med(0.0, pa=0.5), "B1U": _med(0.0, pa=0.0), "B1A": _med(0.0, pa=0.0)}
    r = an.analisar(por, pet="A")
    assert r["H-EMERGE"]["leitura"] == "CONFIRMA" and r["H-REP"]["leitura"] == "FORA (sem o RM)"
    assert r["H-DOSE"]["leitura"] == "CONFIRMA" and r["H-CUSTO"]["leitura"] == "CONFIRMA"
    assert an.analisar(por)["H-EMERGE"]["leitura"] == "NAO CONFIRMA"      # sem o pet, a P1 do par (0) nao sobe
