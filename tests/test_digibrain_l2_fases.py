"""As fases da L-2 (experiments/run_v2_digibrain_l2.py; o adendo 5 do plano, A5.2, A5.4, A5.5, A5.8 e A5.9): a config e as travas (o
adendo 5 APROVADO, as sementes da avaliacao recusadas no piloto, a avaliacao sem o K fixado recusada), a regra do K e os criterios em dados
feitos a mao, o credito por opcao com a intencao suspensa, e as duas fases de ponta a ponta na fumaca (as sementes dos testes). Nenhuma
vida da faixa 67xxx roda aqui."""
from __future__ import annotations

import copy
import json
import statistics
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import poder_l2_digibrain as pw  # noqa: E402
import run_v2_digibrain_l2 as l2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_digibrain_prototipo"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def _avaliacao(k_por_base: int = 10) -> dict:
    c = _cfg("l2_piloto")
    c["fase"], c["unidades"] = "l2_avaliacao", {"bases": [67303, 67404, 67505], "k": k_por_base, "prefixo": "digibrain_prototipo"}
    return c


# ------------------------------------------------------------------ a config e as travas
def test_a_config_do_piloto_segue_o_adendo_5():
    assert l2.modo_da_config(_cfg("l2_piloto")) == "l2_piloto"
    assert l2.modo_da_config(_cfg("fumaca_l2_piloto")) == "fumaca" and l2.modo_da_config(_cfg("fumaca_l2_avaliacao")) == "fumaca"


@pytest.mark.parametrize("bases", [[67303, 67404], [67101, 67303], [66101, 66202], [64101, 67202], [67101], [67101, 67202, 67404]])
def test_o_piloto_recusa_as_sementes_da_avaliacao_e_as_de_outras_fases(bases):
    c = _cfg("l2_piloto")
    c["unidades"]["bases"] = bases
    with pytest.raises(bv.SementeSemPlano):
        l2.modo_da_config(c)


@pytest.mark.parametrize("mudar", [("k", 4), ("dias", 13), ("orcamento_por_dia", 15), ("plano", "outro.md")])
def test_o_piloto_segue_o_plano_a_letra(mudar):
    c = _cfg("l2_piloto")
    if mudar[0] == "k":
        c["unidades"]["k"] = mudar[1]
    else:
        c[mudar[0]] = mudar[1]
    with pytest.raises(ValueError):
        l2.modo_da_config(c)


def test_a_config_recusa_chave_a_mais_e_fase_desconhecida():
    c = _cfg("l2_piloto")
    with pytest.raises(ValueError, match="sobram"):
        l2.modo_da_config({**c, "inatos": {}})
    with pytest.raises(ValueError, match="fase"):
        l2.modo_da_config({**c, "fase": "reavaliacao"})


def test_a_trava_exige_o_adendo_5_aprovado(monkeypatch):
    plano = l2._plano()
    monkeypatch.setattr(l2, "_plano", lambda: plano.replace("**Status: APROVADO pelo Matheus em 2026-10-29,** com o piloto",
                                                            "**Status: PROPOSTO,** com o piloto"))
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        l2.modo_da_config(_cfg("l2_piloto"))


# ------------------------------------------------------------------ o K fixado (A5.9)
def _piloto(tmp_path, k, monkeypatch, a59: str | None):
    pasta = tmp_path / "piloto"
    pasta.mkdir()
    (pasta / "resultado.json").write_text(json.dumps({"regra_do_k": {"k": k}}), encoding="utf-8")
    monkeypatch.setitem(l2.SAIDA, "l2_piloto", str(pasta))
    plano = l2._plano()
    if "### A5.9" in plano:                    # o plano de hoje ja tem a A5.9 (o K = 450): os cenarios a trocam pela deles
        plano = plano[:plano.index("### A5.9")]
    texto = plano if a59 is None else plano + "\n### A5.9 O K da avaliacao\n\n" + a59 + "\n"
    monkeypatch.setattr(l2, "_plano", lambda: texto)


def test_a_avaliacao_recusa_sem_o_piloto(tmp_path, monkeypatch):
    monkeypatch.setitem(l2.SAIDA, "l2_piloto", str(tmp_path / "nao_existe"))
    with pytest.raises(FileNotFoundError, match="piloto"):
        l2.modo_da_config(_avaliacao())


def test_a_avaliacao_recusa_sem_a_a5_9(tmp_path, monkeypatch):
    _piloto(tmp_path, 30, monkeypatch, None)
    with pytest.raises(RuntimeError, match="A5.9"):
        l2.modo_da_config(_avaliacao())


def test_a_avaliacao_com_o_k_fixado(tmp_path, monkeypatch):
    _piloto(tmp_path, 30, monkeypatch, "**K fixado: 30 unidades** (10 por base)")
    assert l2.k_da_avaliacao() == 30 and l2.modo_da_config(_avaliacao(10)) == "l2_avaliacao"
    with pytest.raises(ValueError, match="K por base"):
        l2.modo_da_config(_avaliacao(7))


def test_a_avaliacao_recusa_um_k_diferente_do_piloto(tmp_path, monkeypatch):
    _piloto(tmp_path, 30, monkeypatch, "**K fixado: 21 unidades**")
    with pytest.raises(RuntimeError, match="nao e o da regra"):
        l2.k_da_avaliacao()


def test_o_k_acima_de_100_sem_o_matheus_e_recusado(tmp_path, monkeypatch):
    _piloto(tmp_path, 102, monkeypatch, "**K fixado: 102 unidades**")
    with pytest.raises(RuntimeError, match="aprovado por ele"):
        l2.k_da_avaliacao()


def test_o_k_acima_de_100_com_o_matheus(tmp_path, monkeypatch):
    _piloto(tmp_path, 102, monkeypatch, "**K fixado: 102 unidades**, aprovado pelo Matheus em (a data)")
    assert l2.k_da_avaliacao() == 102


def test_o_k_sem_regra_so_com_o_matheus_e_divisivel_pelas_bases(tmp_path, monkeypatch):
    _piloto(tmp_path, None, monkeypatch, "**K fixado: 20 unidades**, aprovado pelo Matheus")
    with pytest.raises(RuntimeError, match="nao se divide"):
        l2.k_da_avaliacao()


# ------------------------------------------------------------------ a regra do K e os criterios, em dados feitos a mao
def _registros(m3: dict, m3s: dict, n: int = 10) -> list[dict]:
    """vidas sinteticas: para cada medida (medida, lugar), o valor da unidade i em cada braco e m3[(m, lu)](i); o mesmo nas 4 celulas"""
    regs = []
    for i in range(n):
        for dono in orq.DONOS:
            for lu in orq.LUGARES:
                for braco, fonte in (("M3", m3), ("M3+S", m3s)):
                    v = {m: fonte.get((m, lu), lambda i: 0.5)(i) for m in ("episodio", "racao", "exaustao", "privacao", "c_l2_1")}
                    regs.append({"semente": 1000 + i, "base": 1, "dono": dono, "lugar": lu, "braco": braco,
                                 "episodios_fome": {"taxa": v["episodio"]}, "cadeia": {"taxa": v["racao"]},
                                 "exaustao": v["exaustao"], "privacao": v["privacao"],
                                 "l2": {"c_l2_1": v["c_l2_1"], "fins": {"busca": {}},
                                        "trocas": {"busca": {"reflexo": 0, "outra_com_racao_em_R": 0, "outra_sem_racao_em_R": 0}},
                                        "s1": {"suspensas": 4, "expiradas": 1}, "s4": {"retomadas": 3},
                                        "s2": {"buscas_suspensas": 10, "buscas_suspensas_meta_ou_achou": 6, "buscas_nunca_suspensas": 10,
                                               "buscas_nunca_suspensas_meta_ou_achou": 6}}})
    return regs


def test_a_comparacao_do_piloto_e_o_sigma_d_das_diferencas():
    a = lambda i: 0.4 + 0.01 * i                    # noqa: E731
    b = lambda i: 0.4 + 0.01 * i + 0.003 * (i % 3)  # noqa: E731
    regs = _registros({("privacao", "longe"): a}, {("privacao", "longe"): b})
    c = l2.comparacao_do_piloto(regs, "privacao", "longe")
    difs = [b(i) - a(i) for i in range(10)]
    assert c["unidades"] == 10 and c["sigma_d"] == pytest.approx(statistics.stdev(difs))
    assert c["poder"]["30"] == pytest.approx(pw.poder(0.02 / c["sigma_d"], 30)) and 0 < c["rho"] <= 1
    assert c["sigma_M3"] == pytest.approx(statistics.stdev([a(i) for i in range(10)]))


def test_a_regra_do_k_e_o_menor_da_grade_com_a_conjuncao_a_0_8():
    def comps(poder_por_k):
        return {f"{m}|{lu}": {"poder": {str(k): poder_por_k[k] for k in l2.GRADE_K}} for m, lu in l2.COMPARACOES_C3}
    p = {12: 0.5, 21: 0.9, 30: 0.99, 51: 1.0, 102: 1.0, 201: 1.0}
    r = l2.regra_do_k(comps(p))
    assert r["conjuncao"]["21"] == pytest.approx(0.9 ** 10) and r["k"] == 30 and r["k_por_base"] == 10 and not r["volta_ao_matheus"]
    r = l2.regra_do_k(comps({12: 0.1, 21: 0.2, 30: 0.3, 51: 0.5, 102: 0.99, 201: 1.0}))
    assert r["k"] == 102 and r["volta_ao_matheus"]
    r = l2.regra_do_k(comps({k: 0.5 for k in l2.GRADE_K}))
    assert r["k"] is None and r["volta_ao_matheus"] and r["custo"]["201"]["vidas"] == 201 * 48


def test_os_criterios_como_estao():
    um = lambda v: (lambda i: v + 0.001 * i)        # noqa: E731
    base = {(m, lu): um(0.5) for m in ("episodio", "racao", "exaustao", "privacao") for lu in orq.LUGARES}
    m3 = {**base, ("c_l2_1", "longe"): um(20.0)}
    m3s = {**base, ("c_l2_1", "longe"): um(8.0), ("episodio", "longe"): lambda i: 0.55 + 0.001 * i + 0.002 * (i % 2)}
    c = l2.criterios(_registros(m3, m3s))
    assert c["C-L2-1"]["passa"] and c["C-L2-2"]["passa"] and c["C-L2-3"]["passa"] and c["C-L2-4"]["passa"]
    assert c["leitura"]["segue_para_o_jogo"] and c["limiares"]["status"].startswith("PROPOSTOS")
    pior = {**m3s, ("privacao", "longe"): lambda i: 0.53 + 0.001 * i}            # +0,03 na privacao do longe
    assert not l2.criterios(_registros(m3, pior))["C-L2-3"]["passa"]
    metade = {**m3s, ("c_l2_1", "longe"): um(11.0)}                               # nao chega a metade
    assert not l2.criterios(_registros(m3, metade))["C-L2-1"]["passa"]


# ------------------------------------------------------------------ o credito com a intencao suspensa
def test_o_credito_aceita_o_cochilo_suspenso_e_recusa_outro_buraco():
    _motor, reg, _ = orq.viver("M3+S", "atencioso", "longe", 101, 4, orq.ORCAMENTO_POR_DIA, conserto=True)
    c = orq.cerebro_de(reg)
    orq.conferir_mecanismo("M3+S", reg, None)
    assert any("n_susp" in f for m in c.motivos for f in m["fins"])
    k = next(k for k, m in enumerate(c.motivos) if m["reflexo"] and m.get("suspensa") is not None
             and any(any("n_susp" in f and f["inicio"] < k for f in mm["fins"]) for mm in c.motivos[k:]))
    falso = copy.deepcopy(c.motivos)
    falso[k]["suspensa"] = None

    class C:
        S, motivos, m = c.S, falso, c.m
    with pytest.raises(RuntimeError, match="nao e da unidade"):
        orq.conferir_credito("M3+S", C)


def test_os_bracos_da_l2_sao_o_m3_e_o_m0_do_conserto_com_a_suspensao():
    assert orq.config_do_braco("M3+S", conserto=True) == orq.replace(orq.config_do_braco("M3", conserto=True), intencao_suspensa=True)
    assert orq.config_do_braco("M0+S", conserto=True) == orq.replace(orq.config_do_braco("M0", conserto=True), intencao_suspensa=True)
    with pytest.raises(ValueError):
        orq.config_do_braco("M3+S")                                              # fora do conserto, nao existe


# ------------------------------------------------------------------ as duas fases na fumaca
@pytest.mark.parametrize("nome", ["fumaca_l2_piloto", "fumaca_l2_avaliacao"])
def test_a_fumaca_de_ponta_a_ponta(tmp_path, nome):
    with pytest.raises(ValueError, match="4 processos"):
        l2.rodar(_cfg(nome), tmp_path / "x", 5)
    r = l2.rodar(_cfg(nome), tmp_path / "saida", 1)
    assert {p.name for p in (tmp_path / "saida").iterdir()} >= {"meta.json", "medidas.json", "resultado.json", "vidas"}
    regs = r["registros"]
    assert len(regs) == 2 * len(l2.BRACOS) * len(orq.CELULAS) and r["meta"]["modo"] == "fumaca"
    for x in regs:
        if x["braco"].endswith("+S"):
            assert x["l2"]["trocas"]["busca"]["reflexo"] == 0 and x["l2"]["trocas"]["ida"]["reflexo"] == 0
    assert sum(x["l2"]["s4"]["retomadas"] for x in regs if x["braco"] == "M3+S") > 0
    assert all(x["l2"]["s4"]["retomadas"] == 0 for x in regs if not x["braco"].endswith("+S"))
    res = r["resultado"]
    assert ("regra_do_k" in res) == (nome == "fumaca_l2_piloto") and ("criterios" in res) == (nome == "fumaca_l2_avaliacao")
    with pytest.raises(FileExistsError):
        l2.rodar(_cfg(nome), tmp_path / "saida", 1)
