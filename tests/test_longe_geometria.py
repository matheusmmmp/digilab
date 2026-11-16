"""O orquestrador da LONGE_GEOMETRIA (experiments/run_v3_longe_geometria.py; docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, secoes 3 a 7) e o
script de poder (experiments/poder_longe_geometria.py; secao 6): o desenho, a config e a trava (o plano APROVADO, a faixa 96101...96505,
as bases, o K, os dias, no maximo 4 processos, nada por cima de uma pasta existente), os lugares (o `longe_um` com 1 ponto), a interacao, a
regra de leitura da secao 7 e a fumaca de ponta a ponta. Vidas so com as sementes dos testes (101...505): nenhuma da faixa 93xxx roda aqui."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import poder_longe_geometria as pg  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_longe_geometria as lg  # noqa: E402
from bancada.faixas import na_faixa_reservada  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v3_longe_geometria"


def _cfg(nome: str = "longe_geometria") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ o que o plano fixa
def test_o_desenho_e_o_do_plano():
    assert lg.BASES == (96101, 96202, 96303, 96404, 96505) and lg.K_POR_BASE == 40 and lg.DIAS == 14 and lg.ORCAMENTO_POR_DIA == 16
    assert lg.LUGARES == ("longe_um", "longe_fixo", "longe_ancora", "longe") and len(lg.CELULAS) == 16
    assert lg.BRACOS == ("PAD", "M3", "M2", "M0") and lg.BRACO_DO_ORQ["PAD"] == "REL" and lg.CONTROLE == "M2"
    assert lg.PREFIXO == "digibrain_prototipo" and lg.MARGEM == 0.034 and lg.MAX_PROCESSOS == 4 and lg.ALFA_FAMILIA == 0.025
    us = bv.unidades_derivadas(lg.BASES, lg.K_POR_BASE, lg.PREFIXO)
    assert len(us) == 200 and len(us) * len(lg.BRACOS) * len(lg.CELULAS) == 12800 == 200 * pg.VIDAS_POR_UNIDADE


def test_os_bracos_sao_os_do_conserto_e_o_pad_e_o_rel_da_c4():
    for b in lg.BRACOS:
        cd = orq.config_do_braco(lg.BRACO_DO_ORQ[b], conserto=True)
        assert not cd.intencao_suspensa and cd.cheiro_inato and cd.intencao_cheiro
    pad = orq.config_do_braco("REL", conserto=True)
    assert pad.memoria_autobio and pad.controle_mem == "rel" and not pad.facetas_mem and pad.m_mem
    assert not orq.config_do_braco("M2", conserto=True).m_mem and orq.config_do_braco("M3", conserto=True).m_mem


def test_a_faixa_esta_reservada():
    """a faixa 96101...96505 (LG-6), reservada pelo Matheus em 2026-11-16 num commit proprio"""
    assert na_faixa_reservada(96101) and na_faixa_reservada(96505) and not na_faixa_reservada(96506)
    lg.exigir_faixa_reservada()


# ------------------------------------------------------------------ a config e a trava
def test_a_fumaca_passa_sem_faixa_e_sem_aprovacao():
    assert lg.modo_da_config(_cfg("fumaca")) == "fumaca"


def test_a_run_segue_o_plano_aprovado_e_a_faixa_reservada():
    assert lg.modo_da_config(_cfg()) == "longe_geometria"             # o plano APROVADO em 2026-11-16 e a faixa na tabela


def test_a_run_e_recusada_sem_a_faixa_ou_sem_a_aprovacao(monkeypatch):
    todas = lg.FAIXAS_RESERVADAS
    monkeypatch.setattr(lg, "FAIXAS_RESERVADAS", tuple(f for f in todas if f[0] != 96101))
    with pytest.raises(bv.SementeSemPlano, match="FAIXAS_RESERVADAS"):
        lg.modo_da_config(_cfg())
    monkeypatch.setattr(lg, "FAIXAS_RESERVADAS", todas)
    plano = lg._plano()
    assert plano.count("**Status: APROVADO pelo Matheus em 2026-11-16,**") == 1
    monkeypatch.setattr(lg, "_plano", lambda: plano.replace("**Status: APROVADO pelo Matheus em 2026-11-16,**", "**Status: PROPOSTO,**", 1))
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        lg.modo_da_config(_cfg())
    lg.modo_da_config(_cfg("fumaca"))                                 # a fumaca nao precisa da aprovacao


@pytest.mark.parametrize("bases", [[96101, 96202, 96303, 96404], [96101, 96202, 96303, 96404, 96506], [71101, 71202, 71303, 71404, 71505],
                                   [101, 96101]])
def test_recusa_outra_base_e_sementes_fora_da_faixa(bases):
    c = _cfg()
    c["unidades"]["bases"] = bases
    with pytest.raises(bv.SementeSemPlano):
        lg.modo_da_config(c)


def test_recusa_outro_k_outros_dias_outro_orcamento_e_outro_plano():
    for chave, valor in (("k", 30), ("dias", 13), ("orcamento_por_dia", 15), ("plano", "outro.md")):
        c = _cfg()
        if chave == "k":
            c["unidades"]["k"] = valor
        else:
            c[chave] = valor
        with pytest.raises(ValueError):
            lg.modo_da_config(c)
    with pytest.raises(ValueError, match="sobram"):
        lg.modo_da_config({**_cfg(), "inatos": {}})
    with pytest.raises(ValueError, match="fase"):
        lg.modo_da_config({**_cfg(), "fase": "longe_regular"})


def test_recusa_mais_de_4_processos_e_pasta_existente(tmp_path):
    with pytest.raises(ValueError, match="4 processos"):
        lg.rodar(_cfg("fumaca"), tmp_path / "x", 5)
    with pytest.raises(FileExistsError):
        lg.rodar(_cfg("fumaca"), tmp_path, 1)


# ------------------------------------------------------------------ os lugares
def test_o_longe_um_e_o_longe_fixo_com_um_ponto_e_o_ancora_tem_as_direcoes_do_fixo():
    um, fixo, anc = (lg.dono_do_lugar("atencioso", lu, 101) for lu in ("longe_um", "longe_fixo", "longe_ancora"))
    assert um.estilo == fixo.estilo == "longe_fixo" and len(um.pontos_fixos) == 1 and len(fixo.pontos_fixos) == 3
    assert anc.estilo == "longe_ancora" and anc._viaveis_ancora == tuple(fixo._direcoes_viaveis())
    assert lg.dono_do_lugar("atencioso", "longe", 101).estilo == "longe"


def test_os_lugares_da_vida_contam_as_racoes():
    d = lg.dono_do_lugar("atencioso", "longe_ancora", 202)
    est = {"tick": 0, "mundo": {"pet": (500, 240)}}
    for t in range(30):
        x, y = d.lugar(est)
        d.lugares.append({"tick": t, "x": x, "y": y, "pet": (500, 240)})
    lv = lg.lugares_da_vida(d)
    assert lv["racoes"] == 30 == sum(lv["por_direcao"].values()) == sum(lv["distancia_celulas"].values())
    assert {int(k) for k in lv["por_direcao"]} <= set(d._viaveis_ancora)
    assert all(19 <= int(k) <= 30 for k in lv["distancia_celulas"])


# ------------------------------------------------------------------ a interacao e a leitura (secoes 5 e 7)
def _registros(valores: dict) -> list[dict]:
    """registros minimos: valores[(braco, lugar)] = taxa por episodio, a mesma nos 4 donos, em 3 unidades com um desvio por unidade"""
    out = []
    for k, desvio in enumerate((0.0, 0.01, -0.01)):
        for (b, lu), v in valores.items():
            for d in lg.DONOS:
                out.append({"braco": b, "lugar": lu, "dono": d, "base": 101, "k": k, "semente": 1000 + k,
                            "episodios_fome": {"taxa": v + (desvio if b == "M3" else 0.0)}})
    return out


def test_a_interacao_e_o_ganho_no_fixo_menos_o_ganho_no_ancora():
    regs = _registros({("M3", "longe_fixo"): 0.50, ("M2", "longe_fixo"): 0.40, ("M3", "longe_ancora"): 0.42, ("M2", "longe_ancora"): 0.40})
    i = lg.interacao(regs, "M3", "M2", "longe_fixo", "longe_ancora")
    assert len(i) == 3 and all(abs(x - 0.08) < 1e-12 for x in i.values())     # (0,10 + d) - (0,02 + d)


def _p(passa, classe):
    return {"passa": passa, "classe": {"classe": classe}}


def _m(classe):
    return {"classe": {"classe": classe}}


@pytest.mark.parametrize("passa,ci,cm,trecho", [
    (True, "> 0", "≈ 0", "a regularidade explica o ganho"),
    (True, "> 0", "< 0", "a regularidade explica o ganho"),
    (True, "> 0", "> 0", "mesmo sem repeticao"),
    (False, "≈ 0", "> 0", "a geometria explica o ganho"),
    (False, "≈ 0", "≈ 0", "nao ganha em nenhum dos dois"),
    (False, "< 0", "> 0", "a regularidade atrapalha"),
    (False, "indeterminado", "> 0", "indeterminado"),
    (False, "> 0", "≈ 0", "indeterminado"),           # a classe "> 0" sem o Holm rejeitar nao vale como "> 0"
])
def test_a_regra_de_leitura_da_secao_7(passa, ci, cm, trecho):
    assert trecho in lg.leitura_de(_p(passa, ci), True, _m(cm))["linha"]


def test_sem_premissa_a_leitura_e_inconclusiva():
    assert "inconclusivo por premissa" in lg.leitura_de(_p(True, "> 0"), False, _m("≈ 0"))["linha"]


def test_a_trava_do_plano_le_so_a_primeira_linha_de_status():
    with pytest.raises(RuntimeError):
        lg.exigir_plano_aprovado("# t\n\n**Status: PROPOSTO** (x)\n\n**Status: APROVADO pelo Matheus**\n")
    lg.exigir_plano_aprovado("# t\n\n**Status: APROVADO pelo Matheus em 2026-11-16.**\n")


# ------------------------------------------------------------------ o poder (secao 6)
def test_o_poder_e_a_margem_seguem_a_a6_5():
    assert pg.poder_normal(0.0, 0.1, 100) < 0.05
    m = pg.margem_do_poder(0.157, 200)
    assert abs(pg.poder_normal(m, 0.157, 200) - 0.8) < 1e-6 and pg.margem_do_poder(0.157, 200, 0.0125) > m
    poder = json.loads((RAIZ / "artifacts_v3_longe_geometria" / "poder.json").read_text(encoding="utf-8"))
    assert abs(poder["por_k"]["K=200"]["margem_holm_primeiro"] - lg.MARGEM) < 0.0005       # a delta proposta e a do script


# ------------------------------------------------------------------ a fumaca
def test_a_fumaca_roda_de_ponta_a_ponta(tmp_path):
    cfg = {**_cfg("fumaca"), "dias": 1}
    cfg["unidades"] = {**cfg["unidades"], "bases": [101], "k": 1}
    r = lg.rodar(cfg, tmp_path / "f", 1)
    assert r["meta"]["modo"] == "fumaca" and r["resultado"]["vidas"] == 64 and r["meta"]["bracos"]["PAD"]["orquestrador"] == "REL"
    res = r["resultado"]
    assert set(res["primarios"]) == {"I-M3", "I-PAD"} and set(res["leitura"]) >= {"I-M3", "I-PAD", "concordam"}
    cc = res["descritivo"]["conferencia_da_construcao"]
    assert set(cc) == set(lg.LUGARES) and all(v["vidas"] == 4 for v in cc.values())
    assert (tmp_path / "f" / "medidas.json").exists() and (tmp_path / "f" / "resultado.json").exists()
