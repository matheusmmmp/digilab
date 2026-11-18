"""A VALUATION V3 (docs/PLANO_ANALISE_V3_VALUATION_CONSERTO.md): a chave do conserto (`ConfigConsertoValuation.guarda_fome_reflexo`), o
reflexo do sono com e sem ela, os bracos, a regra de leitura, a trava da run e uma fumaca do orquestrador
(experiments/run_v3_valuation_conserto.py), com as sementes dos testes."""
from __future__ import annotations

import json
import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_valuation_conserto as K  # noqa: E402
from digilab.config import (CONFIG_CONSERTO_VALUATION, CONFIG_CONSERTO_VALUATION_LIGADO, CONFIG_DIGIBRAIN_INATOS,  # noqa: E402
                            CONFIG_SONO_SEGURA_LIGADA, PARAMETROS_CONSERTO_VALUATION, ConfigConsertoValuation)
from digilab.digibrain.arb import Arbitragem  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
LAM_SONO = CONFIG_DIGIBRAIN_INATOS.lambda_sono
LAM_URG = CONFIG_DIGIBRAIN_INATOS.urgencia_lambda


# ------------------------------------------------------------------ a config
def test_a_config_tem_status_e_desliga_por_padrao():
    assert {f.name for f in fields(ConfigConsertoValuation)} == set(PARAMETROS_CONSERTO_VALUATION)
    assert all(st == "PROPOSTO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_CONSERTO_VALUATION.values())
    assert not CONFIG_CONSERTO_VALUATION.guarda_fome_reflexo and CONFIG_CONSERTO_VALUATION_LIGADO.guarda_fome_reflexo
    with pytest.raises(TypeError):
        ConfigConsertoValuation(guarda_fome_reflexo=1)
    with pytest.raises(TypeError):
        Arbitragem(conserto=CONFIG_SONO_SEGURA_LIGADA)


# ------------------------------------------------------------------ o reflexo
def _sens(energia, dormindo=0):
    return {"leitura": {"energia": energia}, "contexto": {"dormindo": dormindo}}


@pytest.mark.parametrize("energia", [0, LAM_SONO - 1])
def test_com_a_chave_a_fome_urgente_tira_o_reflexo_e_so_ela(energia):
    arb = Arbitragem(conserto=CONFIG_CONSERTO_VALUATION_LIGADO)
    assert arb.le_urgencias
    assert arb.reflexo(_sens(energia), {"fome": LAM_URG}) is True          # no limiar: nao e urgente (a guarda do sono que segura)
    assert arb.reflexo(_sens(energia), {"fome": LAM_URG + 1}) is False
    assert arb.reflexo(_sens(energia), {"fome": 0}) is True
    with pytest.raises(RuntimeError, match="urgencia da fome"):
        arb.reflexo(_sens(energia))


def test_sem_a_chave_o_reflexo_de_hoje():
    arb = Arbitragem()
    assert not arb.le_urgencias
    for fome in (0, LAM_URG + 1, S):
        assert arb.reflexo(_sens(LAM_SONO - 1), {"fome": fome}) is True
    assert arb.reflexo(_sens(LAM_SONO - 1)) is True
    assert arb.reflexo(_sens(LAM_SONO)) is False


def test_acima_de_lambda_sono_a_chave_nao_muda_nada():
    com, sem = Arbitragem(conserto=CONFIG_CONSERTO_VALUATION_LIGADO), Arbitragem()
    for energia in (LAM_SONO, S // 2, S):
        for fome in (0, LAM_URG + 1):
            assert com.reflexo(_sens(energia), {"fome": fome}) is sem.reflexo(_sens(energia), {"fome": fome}) is False


def test_com_o_sono_que_segura_a_parte_dele_nao_muda():
    com = Arbitragem(sono=CONFIG_SONO_SEGURA_LIGADA, conserto=CONFIG_CONSERTO_VALUATION_LIGADO)
    sem = Arbitragem(sono=CONFIG_SONO_SEGURA_LIGADA)
    for energia in (LAM_SONO, S // 2):
        for fome in (0, LAM_URG + 1):
            assert com.reflexo(_sens(energia, 1), {"fome": fome}) is sem.reflexo(_sens(energia, 1), {"fome": fome})


# ------------------------------------------------------------------ os bracos e a vida
def test_o_con_muda_so_a_chave():
    rel, con = K.montar("REL"), K.montar("CON")
    assert rel["cd"] == con["cd"] and rel["inatos"] == con["inatos"]
    assert not rel["conserto"].guarda_fome_reflexo and con["conserto"].guarda_fome_reflexo
    with pytest.raises(ValueError):
        K.montar("R")


def test_o_rel_daqui_e_a_vida_da_c4():
    a, *_ = K.viver("REL", "relapso", "longe_fixo", 101, 2, 16)
    b, *_ = ma.viver("REL", "relapso", "longe_fixo", 101, 2, 16)
    assert a.log.para_jsonl() == b.log.para_jsonl()
    assert json.dumps(a.politica.estado_interno(), sort_keys=True, default=str) == json.dumps(b.politica.estado_interno(), sort_keys=True,
                                                                                               default=str)


def test_a_conferencia_pega_um_reflexo_fora_da_regra():
    _, registro, _, _, baixas = K.viver("REL", "relapso", "longe_fixo", 101, 2, 16)
    with pytest.raises(RuntimeError, match="nao e o do braco"):
        K.conferir_conserto("CON", registro, baixas)
    i = next(j for j, b in enumerate(baixas) if b)
    with pytest.raises(RuntimeError, match="a regra diz"):
        K.conferir_conserto("REL", registro, baixas[:i] + [False] + baixas[i + 1:])
    with pytest.raises(RuntimeError, match="leituras do reflexo"):
        K.conferir_conserto("REL", registro, baixas[:-1])


# ------------------------------------------------------------------ a regra de leitura
def _cr(p_classe="> 0", p_sinal=None, p=0.001, g=("≈ 0", "≈ 0", "≈ 0", "≈ 0"), g3=("≈ 0", "≈ 0")):
    def guarda(c, reprova):
        return {"classe": {"classe": c}, "passa": c != reprova}
    return {"P": {"passa": p_classe == "> 0" and p < 0.025, "efeito_trivial": p_classe == "≈ 0" and p_sinal == "+"},
            "G1": {"longe_fixo": guarda(g[0], "> 0"), "12_celulas": guarda(g[1], "> 0")},
            "G2": {"longe_fixo": guarda(g[2], "> 0"), "12_celulas": guarda(g[3], "> 0")},
            "G3": {"comedouro": guarda(g3[0], "< 0"), "longe": guarda(g3[1], "< 0")}}


def test_a_regra_de_leitura_escrita_antes():
    assert K.veredito(_cr())["leitura"] == "passa"
    assert K.veredito(_cr(p_classe="≈ 0", p_sinal="+"))["leitura"] == "efeito trivial"
    assert K.veredito(_cr(p_classe="indeterminado"))["leitura"] == "falha"
    v = K.veredito(_cr(g=("≈ 0", "≈ 0", "> 0", "≈ 0")))
    assert v["leitura"] == "falha" and v["falhas"] == ["G2 (longe_fixo)"]
    assert K.veredito(_cr(g3=("< 0", "≈ 0")))["falhas"] == ["G3 (comedouro)"]
    assert K.veredito(_cr(g=("> 0", "≈ 0", "≈ 0", "≈ 0"), g3=("> 0", "≈ 0")))["falhas"] == ["G1 (longe_fixo)"]


# ------------------------------------------------------------------ a trava
def _cfg(bases, k, dias=14):
    return {"descricao": "x", "plano": K.PLANO, "fase": K.FASE, "unidades": {"bases": list(bases), "k": k, "prefixo": K.PREFIXO},
            "dias": dias, "orcamento_por_dia": 16}


def test_a_trava_e_a_config():
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        K.exigir_aprovado("**Status: PROPOSTO.**\n")
    K.exigir_aprovado("**Status: APROVADO pelo Matheus em 2026-11-17** (x)\n")
    assert K.modo_da_config(_cfg((101, 202), 2, 3)) == "fumaca"
    with pytest.raises(bv.SementeSemPlano):
        K.modo_da_config(_cfg((99101,), 40))
    cfg = json.loads((RAIZ / "experiments" / "configs" / "v3_valuation" / "conserto.json").read_text(encoding="utf-8"))
    assert K.modo_da_config(cfg) == K.FASE
    assert tuple(cfg["unidades"]["bases"]) == K.BASES and cfg["unidades"]["k"] == K.K_POR_BASE
    assert len(K.CELULAS) == 12


# ------------------------------------------------------------------ a fumaca
def test_a_fumaca_roda_os_dois_bracos_nas_12_celulas(tmp_path):
    r = K.rodar(_cfg((101,), 1, 2), tmp_path / "fum", 1)
    res, meta = r["resultado"], r["meta"]
    assert res["vidas"] == len(K.BRACOS) * 12 == 24
    assert set(res["criterios"]) == {"P", "G1", "G2", "G3"} and res["veredito"]["leitura"] in ("passa", "efeito trivial", "falha")
    assert set(meta["artefatos_sha256"]) == {"medidas.json", "resultado.json", "vidas.tar.gz"}
    for reg in r["registros"]:
        v = reg["valuation"]
        assert {"decisoes_energia_baixa", "energia_baixa_fome_urgente", "fracao_fome_urgente"} <= set(v)
        if reg["braco"] == "REL":
            assert reg["reflexos"] == v["decisoes_energia_baixa"]
        else:
            assert reg["reflexos"] == v["decisoes_energia_baixa"] - v["energia_baixa_fome_urgente"]
