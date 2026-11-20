"""O teto de pesos por plano (docs/DECISAO_V2_TETO_PESOS.md, TP-1 e TP-2, decididas pelo Matheus pela recomendacao): o padrao do cerebro A
fica 1000; um plano declara o seu teto na config da bancada (`teto_pesos`), ate LIMITE_TETO_PESOS_PLANO (2000); a contagem e a falha alta
continuam.

- o limite na ConfigLobos e a falha alta acima dele;
- a contagem e a falha alta: o cerebro dos dois pets com o corpo (1116) e com o banheiro (1277) falha no padrao e nasce com o teto do plano;
- G2: sem nada declarado, a bancada de hoje (a ConfigLobos e o meta iguais, o meta sem a chave nova); os gabaritos de sempre, na suite;
- a declaracao: so por `teto_pesos`, com o plano, acima do padrao e ate o limite; os pesos declarados conferidos contra o cerebro montado,
  na bancada de vidas e na do grupo.
So as sementes dos testes.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import (CONFIG_BANHEIRO_LIGADA, CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_LOBOS,  # noqa: E402
                            CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, LIMITE_TETO_PESOS_PLANO, ConfigLobos)
from digilab.policies.lobos import PARAMETROS_LOBOS, PoliticaLobos  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_DOIS_PETS.md"
DEGRAU1 = replace(CONFIG_LOBOS_APRENDIZ, alvo_aprendido=True, entradas_sociais=True, modelo_outros=True, presenca_fruta_mundo=True)
BANCADA = {"bracos": ["P0", "P1"], "donos": ["atencioso"], "sementes": [101, 202], "dias": 1, "orcamento": 16,
           "sonda": {"estados": 4, "amostras": 4, "semente": 101}, "bootstrap": {"reamostragens": 10, "semente": 4242, "nivel": 0.95}}


def _cfg_grupo(**kw) -> dict:
    c = json.loads((RAIZ / "experiments" / "configs" / "v2_dois_pets" / "fumaca.json").read_text(encoding="utf-8"))
    return {**c, "bracos": ["B+Ainf"], "sementes": [101], **kw}


# ================================================================== o limite
def test_o_padrao_fica_1000_e_o_limite_e_2000():
    assert CONFIG_LOBOS.maximo_pesos == ConfigLobos().maximo_pesos == 1000
    assert LIMITE_TETO_PESOS_PLANO == 2000
    assert replace(CONFIG_LOBOS, maximo_pesos=2000).maximo_pesos == 2000
    for ruim in (2001, 10 ** 6, 0, -1, 1500.0, True):
        with pytest.raises(ValueError, match="maximo_pesos"):
            replace(CONFIG_LOBOS, maximo_pesos=ruim)
    assert "TP-2" in PARAMETROS_LOBOS["maximo_pesos"][1]


# ================================================================== a contagem e a falha alta continuam
@pytest.mark.parametrize("cfg_corpo,cfg_banheiro,pesos", [(CONFIG_CORPO_DRIVES, None, 1116),
                                                          (CONFIG_CORPO_BANHEIRO, CONFIG_BANHEIRO_LIGADA, 1277)])
def test_o_cerebro_acima_de_1000_falha_no_padrao_e_nasce_com_o_teto_do_plano(cfg_corpo, cfg_banheiro, pesos):
    kw = {"cfg_mundo": CONFIG_MUNDO_LIGADA, "cfg_corpo": cfg_corpo, **({"cfg_banheiro": cfg_banheiro} if cfg_banheiro else {})}
    with pytest.raises(ValueError, match="teto 1000"):
        PoliticaLobos(CONFIG_PADRAO, DEGRAU1, **kw)
    assert PoliticaLobos(CONFIG_PADRAO, replace(DEGRAU1, maximo_pesos=2000), **kw).n_pesos() == pesos
    with pytest.raises(ValueError, match=f"teto {pesos}"):                       # o teto conta: n >= teto falha
        PoliticaLobos(CONFIG_PADRAO, replace(DEGRAU1, maximo_pesos=pesos), **kw)
    assert PoliticaLobos(CONFIG_PADRAO, replace(DEGRAU1, maximo_pesos=pesos + 1), **kw).n_pesos() == pesos


def test_abaixo_de_1000_nada_muda_com_o_teto():
    """o teto nao entra em nenhuma conta da vida: o mesmo cerebro, com o padrao e com 2000, tem o mesmo estado interno"""
    a = PoliticaLobos(CONFIG_PADRAO, DEGRAU1, cfg_mundo=CONFIG_MUNDO_LIGADA)
    b = PoliticaLobos(CONFIG_PADRAO, replace(DEGRAU1, maximo_pesos=2000), cfg_mundo=CONFIG_MUNDO_LIGADA)
    assert a.n_pesos() == b.n_pesos() == 990 and a.estado_interno() == b.estado_interno()


# ================================================================== G2: nada declarado, a bancada de hoje
def test_g2_sem_teto_declarado_a_bancada_de_hoje(tmp_path):
    configs = [p for p in (RAIZ / "experiments" / "configs").rglob("*.json")]
    vistos = 0
    for p in configs:
        c = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(c, dict) or "teto_pesos" in c or not {"dias", "orcamento"} <= set(c):
            continue
        c = {k: c[k] for k in ("dias", "orcamento", "ponto", "lobos") if k in c}   # so o que monta o cerebro A
        b = bv.bancada_da_config(c)
        esperado = bv.cfg_lobos_do_ponto(c.get("ponto", bv.PONTO_PADRAO), c.get("lobos")) if ("lobos" in c or "ponto" in c) \
            else bv.Bancada(int(c["dias"]), int(c["orcamento"])).cfg_lobos
        assert b.cfg_lobos == esperado and b.cfg_lobos.maximo_pesos == 1000, p.name
        vistos += 1
    assert vistos > 10
    r = bv.rodar(BANCADA, tmp_path / "v")
    meta = json.loads((tmp_path / "v" / "meta.json").read_text(encoding="utf-8"))
    assert "teto_pesos" not in meta and meta["cfg_lobos"]["maximo_pesos"] == 1000 and r["vidas"]


# ================================================================== a declaracao
def test_o_teto_so_entra_por_teto_pesos_com_o_plano():
    assert bv.validar_teto_pesos(BANCADA) is None
    assert bv.validar_teto_pesos({**BANCADA, "plano": PLANO, "teto_pesos": {"maximo": 2000, "pesos": 1277}}) == 2000
    with pytest.raises(ValueError, match="teto_pesos"):
        bv.validar_teto_pesos({**BANCADA, "lobos": {"maximo_pesos": 1500}})
    for t in ({"maximo": 2000}, {"maximo": 1000, "pesos": 999}, {"maximo": 2001, "pesos": 1277}, {"maximo": 1500, "pesos": 999},
              {"maximo": 1500, "pesos": 1500}, {"maximo": 1500.0, "pesos": 1200}, {"maximo": 1500, "pesos": 1200, "x": 1}, [1500]):
        with pytest.raises(ValueError):
            bv.validar_teto_pesos({**BANCADA, "plano": PLANO, "teto_pesos": t})
    for sem in ({}, {"plano": "docs/NAO_EXISTE.md"}):
        with pytest.raises(bv.SementeSemPlano):
            bv.validar_teto_pesos({**BANCADA, **sem, "teto_pesos": {"maximo": 1500, "pesos": 1200}})
    with pytest.raises(ValueError, match="teto_pesos"):                          # as duas validacoes de config a chamam
        bv.validar_config({**BANCADA, "lobos": {"maximo_pesos": 1500}})
    with pytest.raises(ValueError, match="teto_pesos"):
        bv.validar_config_grupo(_cfg_grupo(lobos={"maximo_pesos": 1500}))
    bv.validar_config({**BANCADA, "plano": PLANO, "teto_pesos": {"maximo": 1500, "pesos": 1200}})
    bv.validar_config_grupo(_cfg_grupo(plano=PLANO, teto_pesos={"maximo": 1500, "pesos": 1200}))


def test_o_teto_declarado_chega_ao_cerebro_e_so_ele_muda():
    c = {**BANCADA, "ponto": "T3", "lobos": {"w0_info": 256}}
    sem = bv.bancada_da_config(c)
    com = bv.bancada_da_config({**c, "plano": PLANO, "teto_pesos": {"maximo": 1500, "pesos": 1200}})
    assert com.cfg_lobos.maximo_pesos == 1500 and replace(com.cfg_lobos, maximo_pesos=1000) == sem.cfg_lobos
    so_teto = bv.bancada_da_config({**BANCADA, "plano": PLANO, "teto_pesos": {"maximo": 1500, "pesos": 1200}})
    assert so_teto.cfg_lobos == replace(bv.cfg_lobos_do_ponto(bv.PONTO_PADRAO), maximo_pesos=1500)


class _Cerebro:
    def __init__(self, n):
        self.n = n

    def n_pesos(self):
        return self.n


def test_os_pesos_declarados_conferidos_contra_o_maior_cerebro():
    cfg = {**BANCADA, "plano": PLANO, "teto_pesos": {"maximo": 2000, "pesos": 1277}}
    assert bv.conferir_teto_pesos(BANCADA, {"x": _Cerebro(5)}) is None             # sem teto, nada conferido
    grande = PoliticaLobos(CONFIG_PADRAO, replace(DEGRAU1, maximo_pesos=2000), cfg_mundo=CONFIG_MUNDO_LIGADA,
                           cfg_corpo=CONFIG_CORPO_BANHEIRO, cfg_banheiro=CONFIG_BANHEIRO_LIGADA)
    r = bv.conferir_teto_pesos(cfg, {"A": grande, "B": _Cerebro(990), "instinto": object()})
    assert r == {"maximo": 2000, "pesos": 1277, "por_cerebro": {"A": 1277, "B": 990}}
    with pytest.raises(RuntimeError, match="1116"):
        bv.conferir_teto_pesos(cfg, {"A": _Cerebro(1116)})
    with pytest.raises(RuntimeError, match="nenhum cerebro"):
        bv.conferir_teto_pesos(cfg, {"instinto": object()})


def test_a_run_confere_os_pesos_declarados(tmp_path):
    """a bancada de vidas e a do grupo conferem os pesos declarados contra o cerebro montado antes de qualquer vida (aqui, cerebros de
    hoje, abaixo de 1000: a declaracao nao bate e a run falha alto, sem gravar vida)"""
    with pytest.raises(RuntimeError, match="teto_pesos.pesos 1200"):
        bv.rodar({**BANCADA, "plano": PLANO, "teto_pesos": {"maximo": 1500, "pesos": 1200}}, tmp_path / "v")
    assert not (tmp_path / "v" / "vidas").exists()
    with pytest.raises(RuntimeError, match="o maior cerebro dos bracos tem 990"):
        bv.rodar_grupo(_cfg_grupo(plano=PLANO, teto_pesos={"maximo": 1500, "pesos": 1200}), tmp_path / "g")
    assert not (tmp_path / "g" / "grupos").exists()
