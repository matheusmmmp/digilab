"""A reavaliacao por estimativa (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 4, A4.7): o IC pelo t, o t sobre as medias
de base e a assimetria g1 no digilab/metrics.py (com contas a mao); o contraste da reavaliacao (o p do Holm pelo t, o G-MOD-EMB pelas
medias de base, a ressalva do g1 sem mudar o p nem a decisao); o G-MVP sem "passa"; a trava do adendo 4 APROVADO; e as analises das fases
antigas, que se refazem iguais dos artefatos gravados; e o registro da reavaliacao (A4.10): a config registrada, as sementes fora
de 66101 a 66505 recusadas. Nenhuma vida da 66xxx: so as sementes dos testes (a fumaca fica em tests/test_digibrain_conserto.py)."""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import (assimetria_g1, contraste_pareado, holm, ic_t, quantil_t, t_medias_de_grupo,  # noqa: E402
                             t_unilateral)

BOOT = {"reamostragens": 2000, "semente": 4242, "nivel": 0.95}


# ================================================================== digilab/metrics.py, contra contas a mao
def test_quantil_t_confere_com_a_tabela():
    # os quantis 0,975 da t de Student (a tabela): 4, 9, 49 e 2 graus de liberdade
    for gl, tabela in ((4, 2.776445), (9, 2.262157), (49, 2.009575), (2, 4.302653)):
        assert quantil_t(gl) == pytest.approx(tabela, abs=1e-6)
        assert t_unilateral(quantil_t(gl), gl) == pytest.approx(0.025, abs=1e-12)
    assert quantil_t(9, 0.90) < quantil_t(9)
    with pytest.raises(ValueError):
        quantil_t(0)


def test_ic_t_confere_com_a_conta_a_mao():
    # [1, 2, 3, 4, 5]: media 3, dp = raiz(2,5), ep = raiz(2,5) / raiz(5) = raiz(0,5); 3 +- 2,776445 x 0,707107
    r = ic_t([1, 2, 3, 4, 5])
    meia = 2.7764451051977934 * math.sqrt(0.5)
    assert (r["n"], r["gl"], r["media"]) == (5, 4, 3.0) and r["dp"] == pytest.approx(math.sqrt(2.5))
    assert r["ic_inferior"] == pytest.approx(3.0 - meia) and r["ic_superior"] == pytest.approx(3.0 + meia)
    assert r["ic_inferior"] == pytest.approx(1.036757, abs=1e-6) and r["motivo"] is None
    # sem variacao, o IC e o ponto; com menos de 2 valores, nao ha IC e o motivo diz
    assert (ic_t([0.4, 0.4])["ic_inferior"], ic_t([0.4, 0.4])["ic_superior"]) == (0.4, 0.4)
    um = ic_t([0.4])
    assert um["ic_inferior"] is None and um["motivo"] == "menos de 2 valores"


def test_t_sobre_as_medias_de_grupo_confere_com_a_conta_a_mao():
    # as medias dos grupos: 2, 3 e 6; media 11/3, dp = raiz(13/3), t = (11/3) / (raiz(13/3) / raiz(3)), 2 gl
    r = t_medias_de_grupo({"a": [1, 3], "b": [2, 4], "c": [6]})
    t = (11 / 3) / (math.sqrt(13 / 3) / math.sqrt(3))
    assert r["medias_grupo"] == [2.0, 3.0, 6.0] and r["gl"] == 2 and r["t"] == pytest.approx(t)
    assert r["p_unilateral"] == pytest.approx(t_unilateral(t, 2))
    meia = 4.302652729749459 * math.sqrt(13 / 3) / math.sqrt(3)
    assert r["ic"]["ic_inferior"] == pytest.approx(11 / 3 - meia) and r["ic"]["ic_superior"] == pytest.approx(11 / 3 + meia)
    # o grupo pesa um so, qualquer que seja o tamanho dele: e diferente do t sobre os 5 valores
    assert r["p_unilateral"] != pytest.approx(contraste_pareado({"a": [1, 3], "b": [2, 4], "c": [6]}, 100, 1)["t_pareado"]["p_unilateral"])
    assert t_medias_de_grupo({"a": [1.0]})["p_unilateral"] is None
    assert t_medias_de_grupo({"a": [1.0, 3.0], "b": [2.0]})["motivo"] == "sem variacao entre as medias dos grupos"


def test_assimetria_g1_confere_com_a_conta_a_mao():
    # [0, 0, 0, 1]: m2 = 3/16, m3 = 3/32, g1 = (3/32) / (3/16)^1,5 = 2 / raiz(3)
    assert assimetria_g1([0, 0, 0, 1]) == pytest.approx(2 / math.sqrt(3))
    assert assimetria_g1([0, 0, 0, -1]) == pytest.approx(-2 / math.sqrt(3))
    assert assimetria_g1([1, 2, 3]) == 0.0
    assert assimetria_g1([2, 2]) is None and assimetria_g1([2]) is None


def test_o_contraste_pareado_de_hoje_nao_muda():
    # o mesmo do tests/test_experimento_maior.py, aqui so como trava: a conta e o formato de hoje
    r = contraste_pareado({i: [v] for i, v in enumerate([0.3, -0.1, 0.2, 0.05, 0.4, 0.15])}, 2000, 7)
    assert set(r) == {"n", "n_grupos", "media", "ic95", "ic90", "p_unilateral", "t_pareado", "motivo"}
    assert r["t_pareado"]["gl"] == 5


# ================================================================== o contraste da reavaliacao (A4.4.6)
def _difs(por_base: dict) -> dict:
    return {(base, i): v for base, vs in por_base.items() for i, v in enumerate(vs)}


def test_o_contraste_t_usa_o_p_e_o_ic_do_t_e_poe_o_bootstrap_ao_lado():
    difs = _difs({66101: [0.03, 0.05], 66202: [0.01, 0.04], 66303: [0.02, -0.01], 66404: [0.06, 0.02], 66505: [0.00, 0.03]})
    c = orq.contraste_t(difs, BOOT)
    hoje = orq.contraste(difs, BOOT)
    valores = [v for _, v in sorted(difs.items())]
    assert c["teste"].startswith("t sobre as unidades") and c["p_unilateral"] == hoje["t_pareado"]["p_unilateral"]
    assert (c["ic95"]["ic_inferior"], c["ic95"]["ic_superior"]) == (ic_t(valores)["ic_inferior"], ic_t(valores)["ic_superior"])
    assert c["gl"] == 9 and c["media"] == hoje["media"]
    assert c["bootstrap"] == {"rotulo": orq.ROTULO_BOOTSTRAP, "p_unilateral": hoje["p_unilateral"], "ic95": hoje["ic95"],
                              "ic90": hoje["ic90"], "motivo": None}
    assert "anticonservadora com 5 bases" in c["bootstrap"]["rotulo"]
    # o IC pelo t e mais largo que o percentil do bootstrap de 5 bases (A4.4.1)
    assert c["ic95"]["ic_superior"] - c["ic95"]["ic_inferior"] > c["bootstrap"]["ic95"]["ic_superior"] - c["bootstrap"]["ic95"]["ic_inferior"]


def test_o_g_mod_emb_usa_o_t_sobre_as_medias_de_base():
    difs = _difs({66101: [0.03, 0.05], 66202: [0.01, 0.04], 66303: [0.02, -0.01], 66404: [0.06, 0.02], 66505: [0.00, 0.03]})
    c = orq.contraste_t(difs, BOOT, por_base=True)
    t = t_medias_de_grupo({b: [v for (bb, _), v in difs.items() if bb == b] for b in (66101, 66202, 66303, 66404, 66505)})
    assert c["teste"].startswith("t sobre as medias de base") and c["gl"] == 4
    assert c["p_unilateral"] == t["p_unilateral"] and c["ic95"] == t["ic"] and c["medias_base"] == t["medias_grupo"]
    assert c["p_unilateral"] != orq.contraste_t(difs, BOOT)["p_unilateral"]
    assert orq.POR_MEDIAS_DE_BASE == ("G-MOD-EMB",)


def test_a_ressalva_do_g1_sai_com_g1_ate_menos_meio_e_nao_muda_o_p_nem_o_holm():
    # assimetria negativa: uma unidade muito abaixo das outras
    neg = _difs({66101: [0.05, 0.06], 66202: [0.05, 0.07], 66303: [0.06, 0.05], 66404: [0.07, 0.06], 66505: [0.05, -0.08]})
    pos = _difs({b: [-v for v in [x for (bb, _), x in sorted(neg.items()) if bb == b]] for b in (66101, 66202, 66303, 66404, 66505)})
    c = orq.contraste_t(neg, BOOT)
    assert c["g1"] <= orq.LIMIAR_G1 == -0.5 and c["ressalva_assimetria"] == orq.RESSALVA_G1
    assert "1,8 vez" in c["ressalva_assimetria"] and "A4.4.5" in c["ressalva_assimetria"]
    assert c["p_unilateral"] == orq.contraste(neg, BOOT)["t_pareado"]["p_unilateral"]          # o p e o do t, com ou sem ressalva
    assert orq.contraste_t(pos, BOOT)["g1"] > 0 and orq.contraste_t(pos, BOOT)["ressalva_assimetria"] is None
    # o Holm usa so o p: a decisao gravada e a mesma de um Holm sobre os p, sem olhar o g1
    familia = {"x": {**c, "holm": holm({"x": c["p_unilateral"], "y": 0.9}, 0.05)["x"]}}
    assert familia["x"]["holm"]["rejeita"] == (c["p_unilateral"] <= 0.025)
    leitura = orq._leitura_contraste(familia["x"])
    if familia["x"]["holm"]["rejeita"]:
        assert "nao e lida como confirmacao" in leitura


def test_a_posicao_do_ic_nas_tres_frases_de_a4_2():
    assert orq.posicao_do_ic({"ic_inferior": 0.81, "ic_superior": 0.9}, 0.8) == "o IC95 inteiro acima de 0,8"
    assert orq.posicao_do_ic({"ic_inferior": 0.75, "ic_superior": 0.85}, 0.8) == "o IC95 contem 0,8"
    assert orq.posicao_do_ic({"ic_inferior": 0.8, "ic_superior": 0.85}, 0.8) == "o IC95 contem 0,8"           # a borda: contem
    assert orq.posicao_do_ic({"ic_inferior": 0.6, "ic_superior": 0.79}, 0.8) == "o IC95 inteiro abaixo de 0,8"
    assert orq.posicao_do_ic({"ic_inferior": None, "ic_superior": None}, 0.8) is None


def test_o_g_mvp_da_reavaliacao_e_estimativa_sem_passa():
    fracoes = _difs({66101: [0.75, 0.917], 66202: [0.833, 0.75], 66303: [0.75, 0.833], 66404: [0.917, 0.75], 66505: [0.833, 0.833]})
    m = orq.g_mvp_estimativa(fracoes, BOOT, 0.8, "a fracao")
    assert "passa" not in m and "falha" not in m and m["referencia"] == 0.8
    assert m["estimativa"] == pytest.approx(sum(fracoes.values()) / 10)
    assert m["ic95"]["ic_inferior"] == pytest.approx(ic_t(list(fracoes.values()))["ic_inferior"])
    assert m["ic95_percentil"] == orq.contraste(fracoes, BOOT)["ic95"] and "anticonservadora" in m["ic95_percentil_rotulo"]
    assert m["posicao"] == orq.posicao_do_ic(m["ic95"], 0.8)


# ================================================================== a trava (A4.7)
PLANO = (RAIZ / orq.PLANO).read_text(encoding="utf-8")


def test_a_trava_exige_o_adendo_4_aprovado_no_cabecalho():
    orq.exigir_adendo_aprovado(PLANO, 4)                                               # o plano de hoje: APROVADO
    proposto = PLANO.replace("**Status: APROVADO pelo Matheus em 2026-10-27.**", "**Status: PROPOSTO, para o Matheus.**")
    assert proposto != PLANO
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        orq.exigir_adendo_aprovado(proposto, 4)
    sem_status = PLANO.replace("**Status: APROVADO pelo Matheus em 2026-10-27.**\n", "")
    with pytest.raises(RuntimeError, match="sem a linha do status"):
        orq.exigir_adendo_aprovado(sem_status, 4)
    with pytest.raises(RuntimeError, match="nao esta no plano"):
        orq.exigir_adendo_aprovado(PLANO.replace("## Adendo 4:", "## Adendo IV:"), 4)
    # o APROVADO fora do cabecalho (numa subsecao) nao conta
    so_titulo = "## Adendo 4: a reavaliacao\n\nTexto.\n\n### A4.0 O que nao muda\n\n**Status: APROVADO pelo Matheus.**\n"
    with pytest.raises(RuntimeError, match="sem a linha do status"):
        orq.exigir_adendo_aprovado(so_titulo, 4)


def test_a_trava_vale_na_config_da_reavaliacao(tmp_path, monkeypatch):
    """com o adendo 4 so PROPOSTO, o modo da config da reavaliacao falha alto antes de qualquer vida"""
    (tmp_path / "docs").mkdir()
    (tmp_path / orq.PLANO).write_text(PLANO.replace("**Status: APROVADO pelo Matheus em 2026-10-27.**", "**Status: PROPOSTO.**"),
                                      encoding="utf-8")
    destino = tmp_path / orq.SAIDA["piloto_conserto"]
    destino.mkdir(parents=True)
    shutil.copy(RAIZ / orq.SAIDA["piloto_conserto"] / "resultado.json", destino / "resultado.json")
    cfg = {**json.loads((RAIZ / "experiments/configs/v2_digibrain_prototipo/piloto_conserto.json").read_text(encoding="utf-8")),
           "fase": "reavaliacao", "unidades": {"bases": list(orq.BASES["reavaliacao"]), "k": 10, "prefixo": orq.PREFIXO}}
    assert orq.modo_da_config(cfg) == "reavaliacao"                                      # com o plano de hoje, APROVADO
    monkeypatch.setattr(orq, "RAIZ", tmp_path)
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        orq.modo_da_config(cfg)


# ================================================================== o registro da reavaliacao (A4.10), sem vida nenhuma
CONFIG_REAVALIACAO = RAIZ / "experiments/configs/v2_digibrain_prototipo/reavaliacao.json"


def _cfg_reavaliacao() -> dict:
    return json.loads(CONFIG_REAVALIACAO.read_text(encoding="utf-8"))


def test_a_config_registrada_da_reavaliacao_segue_o_plano():
    """a config de A4.10: o plano de hoje passa a trava, o modo e o da reavaliacao, o K e o g_apr do M4-con sao os do piloto do conserto
    (A4.5), as 50 unidades sao as das bases 66101 a 66505, e so a descricao, a fase, as bases e o K mudam em relacao a do piloto"""
    orq.exigir_adendo_aprovado(PLANO, 4)
    cfg = _cfg_reavaliacao()
    assert orq.modo_da_config(cfg) == "reavaliacao"
    assert orq.adendo_do_piloto_conserto() == {"k": 10, "g_apr_m4_con": 1923}
    us = bv.unidades_derivadas(cfg["unidades"]["bases"], cfg["unidades"]["k"], orq.PREFIXO)
    assert len(us) == 50 and {u["base"] for u in us} == set(orq.BASES["reavaliacao"]) == set(range(66101, 66506, 101))
    piloto = json.loads((RAIZ / "experiments/configs/v2_digibrain_prototipo/piloto_conserto.json").read_text(encoding="utf-8"))
    assert {k for k in cfg if cfg[k] != piloto[k]} == {"descricao", "fase", "unidades"}
    assert {k for k in cfg["unidades"] if cfg["unidades"][k] != piloto["unidades"][k]} == {"bases", "k"}
    assert orq.BRACOS_DA_FASE["reavaliacao"] == orq.BRACOS_CONSERTO and len(orq.BRACOS_CONSERTO) == 12


@pytest.mark.parametrize("bases", [
    [65303, 65404, 65505],                          # o piloto do conserto
    [64101, 64202, 64303, 64404, 64505],            # a avaliacao do #420 (queimada)
    [66101, 66202, 66303, 66404],                   # uma base a menos
    [66101, 66202, 66303, 66404, 66505, 67101],     # uma base a mais, fora da faixa
    [66101, 66202, 66303, 66404, 66506],            # uma base trocada, fora da faixa
    [101, 66202, 66303, 66404, 66505],              # uma semente dos testes misturada
])
def test_a_reavaliacao_recusa_sementes_fora_de_66101_a_66505(bases):
    cfg = _cfg_reavaliacao()
    cfg["unidades"] = {**cfg["unidades"], "bases": bases}
    with pytest.raises(bv.SementeSemPlano):
        orq.modo_da_config(cfg)


def test_a_reavaliacao_recusa_outro_k_ou_outros_dias_e_nao_grava_por_cima(tmp_path):
    for campo, valor, msg in (("k", 9, "K 9"), ("dias", 13, "dias 13")):
        cfg = _cfg_reavaliacao()
        if campo == "k":
            cfg["unidades"] = {**cfg["unidades"], "k": valor}
        else:
            cfg[campo] = valor
        with pytest.raises(ValueError, match=msg):
            orq.modo_da_config(cfg)
    with pytest.raises(FileExistsError):                # a pasta de saida ja existe: nenhuma vida roda (secao 6.4)
        orq.rodar(_cfg_reavaliacao(), tmp_path, 1)


# ================================================================== as fases antigas se refazem iguais (A4.7)
def _refazer(pasta: Path) -> str:
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    regs = list(json.loads((pasta / "medidas.json").read_text(encoding="utf-8")).values())
    cfg, fase, modo = meta["config"], meta["fase"], meta["modo"]
    if fase in orq.FASES_CALIBRACAO:
        r = {"modo": modo, "fase": fase, "plano": orq.PLANO, **orq.analisar_calibracao(regs, cfg, fase in orq.FASES_CONSERTO)}
    else:
        r = {"modo": modo, "fase": fase, "plano": orq.PLANO, **orq.analisar(regs, cfg),
             "custo": orq.custo(regs, None, len(cfg["unidades"]["bases"]), len(orq.BRACOS_DA_FASE[fase]))}
    return bv._dump(r)


@pytest.mark.parametrize("pasta", ["avaliacao"] + [f"{c}calibracao/rodada_{n}" for c in ("", "conserto/") for n in (1, 2, 3)])
def test_as_analises_das_fases_antigas_se_refazem_iguais(pasta):
    """a avaliacao do #420 e as calibracoes, refeitas das medidas gravadas com o codigo de hoje, saem byte a byte o resultado.json gravado
    (os pilotos, com a simulacao do poder, sao conferidos no relato do PR, pela mesma conta)"""
    p = RAIZ / "artifacts_v2_digibrain_prototipo" / pasta
    assert _refazer(p) == (p / "resultado.json").read_text(encoding="utf-8")
