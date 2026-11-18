"""A VALUATION V2 (docs/PLANO_ANALISE_V3_VALUATION.md): os bracos da ablacao, as duas chaves de ablacao (`ConfigAblacaoValuation`), a trava
da run e uma fumaca do orquestrador (experiments/run_v3_valuation.py), com as sementes dos testes."""
from __future__ import annotations

import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_valuation as V  # noqa: E402
from digilab.config import (CARACTERISTICAS_DIGIBRAIN, CONFIG_ABLACAO_VALUATION, CONFIG_DIGIBRAIN_INATOS, PARAMETROS_ABLACAO_VALUATION,  # noqa: E402
                            ConfigAblacaoValuation)
from digilab.digibrain.arb import Arbitragem  # noqa: E402
from digilab.digibrain.impulso import Impulso  # noqa: E402


# ------------------------------------------------------------------ a config das chaves
def test_a_config_das_chaves_tem_status_e_desliga_por_padrao():
    assert {f.name for f in fields(ConfigAblacaoValuation)} == set(PARAMETROS_ABLACAO_VALUATION)
    assert all(st == "PROPOSTO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_ABLACAO_VALUATION.values())
    assert not CONFIG_ABLACAO_VALUATION.ligada
    with pytest.raises(ValueError):
        ConfigAblacaoValuation(ve_z=True, maior_peso=True)        # uma ablacao por braco
    with pytest.raises(TypeError):
        ConfigAblacaoValuation(ve_z=1)


def test_nenhuma_linha_de_w0_le_o_v_nem_o_e():
    """a premissa do braco F (o MAPA, 2.6): o V e o E so chegam a uma unidade pelo habito"""
    assert all(c not in ("V", "E") for _, linha in CONFIG_DIGIBRAIN_INATOS.w0 for c, _ in linha)


def _sens_afeto():
    S = CONFIG_DIGIBRAIN_INATOS.escala
    sens = {"contexto": {"noite": 0, "dormindo": 0, "sem_cuidado": S}, "conjuncoes": {"comida_vista": 0, "sem_comida": S, "bola_vista": 0}}
    afeto = {"urgencias": {"fome": S // 2}, "V": -300, "E": 700}
    return sens, afeto


def test_ve_z_zera_so_o_v_e_o_e():
    sens, afeto = _sens_afeto()
    hoje = Impulso().contexto_z(sens, afeto, {"F": 100})
    sem = Impulso(cfg_ablacao=ConfigAblacaoValuation(ve_z=True)).contexto_z(sens, afeto, {"F": 100})
    iv, ie = CARACTERISTICAS_DIGIBRAIN.index("V"), CARACTERISTICAS_DIGIBRAIN.index("E")
    assert (hoje[iv], hoje[ie]) == (-300, 700) and (sem[iv], sem[ie]) == (0, 0)
    assert [x for j, x in enumerate(hoje) if j not in (iv, ie)] == [x for j, x in enumerate(sem) if j not in (iv, ie)]


class _RngProibida:
    def random(self):
        raise AssertionError("a ablacao maior_peso nao chama a rng")


class _RngFixa:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _unidades(ativacoes):
    acoes = ("ocioso", "dormir", "comer", "explorar")
    termos = dict.fromkeys(("inato", "prox", "nov", "incentivo", "habito", "memoria", "persistencia"), 0)
    return [{"chave": (a, None, None), "acao": a, "tipo": None, "a": x, "soma": x, "termos": {**termos, "inato": x}}
            for a, x in zip(acoes, ativacoes)]


def test_maior_peso_escolhe_o_maior_sem_rng_e_o_sorteio_de_hoje_nao_muda():
    S = CONFIG_DIGIBRAIN_INATOS.escala
    sens = {"leitura": {"energia": S}, "contexto": {"dormindo": 0}, "social": None}
    afeto = {"g_exp": S // 2, "urgencias": {"fome": 0}}
    un = _unidades([100, 300, 2000, 900])
    g = Arbitragem(ablacao=ConfigAblacaoValuation(maior_peso=True)).escolher(un, afeto, sens, _RngProibida())
    assert g["unidade"]["acao"] == "comer" and g["u"] is None
    hoje = Arbitragem().escolher(un, afeto, sens, _RngFixa(0.0))      # u = 0: o primeiro candidato, como sempre
    assert hoje["unidade"]["acao"] == "ocioso" and hoje["u"] == 0.0


# ------------------------------------------------------------------ os bracos
def test_cada_braco_muda_uma_coisa_so():
    rel = V.montar("REL")
    for b in V.HIPOTESES:
        m = V.montar(b)
        mudou = [k for k in ("cd", "inatos", "ablacao") if m[k] != rel[k]]
        assert len(mudou) == 1, (b, mudou)
    assert replace(rel["inatos"], epsilon=0) == V.montar("B")["inatos"]
    assert V.montar("C")["cd"].controle_mem == "sem"
    assert dict(dict(V.montar("E")["inatos"].w0)["comer"]) == {"vies": -512, "u_fome": 3 * 1024}
    assert V.montar("F")["ablacao"].ve_z and V.montar("G")["ablacao"].maior_peso
    assert V.montar("R")["inatos"].lambda_sono == 0


def test_o_braco_a_esta_fora_e_falha_alto():
    assert "A" in V.FORA and "A" not in V.BRACOS and V.BRACOS == ("REL", "B", "C", "E", "F", "G", "R")
    with pytest.raises(ValueError, match="fora da run"):
        V.montar("A")


def test_o_rel_da_valuation_e_a_vida_da_c4():
    """o braco REL vive a mesma vida que o REL da C4 e da A1 (o `ma.viver`), byte a byte"""
    a, *_ = V.viver("REL", "relapso", "longe_fixo", 101, 2, 16)
    b, *_ = ma.viver("REL", "relapso", "longe_fixo", 101, 2, 16)
    assert a.log.para_jsonl() == b.log.para_jsonl()
    assert json.dumps(a.politica.estado_interno(), sort_keys=True, default=str) == json.dumps(b.politica.estado_interno(), sort_keys=True,
                                                                                               default=str)


# ------------------------------------------------------------------ a trava
def _cfg(bases, k, dias=14):
    return {"descricao": "x", "plano": V.PLANO, "fase": V.FASE, "unidades": {"bases": list(bases), "k": k, "prefixo": V.PREFIXO},
            "dias": dias, "orcamento_por_dia": 16}


def test_a_trava_le_o_aprovado_e_o_adendo():
    com = "**Status: APROVADO pelo Matheus em 2026-11-16,**\n"
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        V.exigir_aprovado("**Status: PROPOSTO.**\n" + V.STATUS_ADENDO_1 + "\n")
    with pytest.raises(RuntimeError, match="adendo 1"):
        V.exigir_aprovado(com)
    V.exigir_aprovado(com + V.STATUS_ADENDO_1 + " em 2026-11-17.**\n")


def test_a_config_segue_o_plano():
    assert V.modo_da_config(_cfg((101, 202), 2, 3)) == "fumaca"
    with pytest.raises(bv.SementeSemPlano):
        V.modo_da_config(_cfg((77101,), 40))
    with pytest.raises(ValueError):
        V.modo_da_config(_cfg((101,), 2, 15))
    cfg = json.loads((RAIZ / "experiments" / "configs" / "v3_valuation" / "ablacao.json").read_text(encoding="utf-8"))
    assert tuple(cfg["unidades"]["bases"]) == V.BASES and cfg["unidades"]["k"] == V.K_POR_BASE and cfg["dias"] == V.DIAS
    assert any((lo, hi) == V.FAIXA for lo, hi, _ in V.FAIXAS_RESERVADAS)


# ------------------------------------------------------------------ a fumaca
def test_a_fumaca_roda_os_sete_bracos_com_as_conferencias(tmp_path):
    r = V.rodar(_cfg((101,), 1, 2), tmp_path / "fum", 1)
    res, meta = r["resultado"], r["meta"]
    assert res["vidas"] == len(V.BRACOS) * len(V.CELULAS) == 28
    assert set(res["primario"]) == {f"{b} - REL" for b in V.HIPOTESES}
    assert all(c["leitura"] in ("confirmada", "efeito trivial", "refutada", "indeterminada") for c in res["primario"].values())
    assert set(meta["artefatos_sha256"]) == {"medidas.json", "resultado.json", "vidas.tar.gz"}
    for reg in r["registros"]:
        v = reg["valuation"]
        assert set(v) >= {"dormir_no_episodio", "comer_no_episodio", "janela_vencida", "comer_trocado_no_reflexo", "comer_no_topo_perdeu"}
        if reg["braco"] == "R":
            assert reg["reflexos"] == 0
    destino = tmp_path / "de_novo.tar.gz"
    V.tar_deterministico(tmp_path / "fum" / "vidas", destino)
    assert destino.read_bytes() == (tmp_path / "fum" / "vidas.tar.gz").read_bytes()
