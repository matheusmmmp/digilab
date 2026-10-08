"""V2, W-DOMINANCIA (rodada 18): a dominancia de um drive no sinal e o braco P1-cw (PLANO_ANALISE_V2_CORPO_DRIVES, adendo 2, A2.2 a
A2.5; decisao D-4).

O que se confere:
- as funcoes de metrics.py em dados sinteticos com a resposta conhecida (c_d, p_d, lidera, f_d, a leitura "domina");
- na bancada: a medida de toda vida, o sinal recalculado batendo com os canais do cerebro, a sonda nos bracos que nao aprendem pela
  consequencia, a fruta com a tristeza (E2), o dominancia.json por braco x condicao x tipo;
- o P1-cw declarado (o P1-c com a pesos_janela desde a W-BANCADA-CORPO; espera a etapa 6 do corpo).
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
from digilab.config import CONFIG_CONSEQUENCIA  # noqa: E402
from digilab.metrics import (LIMIAR_DOMINA, LIMIAR_LIDERA, contribuicao_drives, dominancia_decisoes,  # noqa: E402
                             leitura_dominancia, parcelas_drives)

SONDA = {"estados": 5, "amostras": 5, "semente": 101}
D8 = 7 * 1440


# ------------------------------------------------------------------ metrics, em dados sinteticos


def test_contribuicao_de_cada_drive():
    c = contribuicao_drives({"fome": 512, "cansaco": 100}, {"fome": 256, "cansaco": 300})
    assert c == {"fome": 512 ** 2 - 256 ** 2, "cansaco": 100 ** 2 - 300 ** 2}            # 196608 e -80000
    assert contribuicao_drives({"fome": 512}, {"fome": 256}, {"fome": 512}) == {"fome": 98304}    # w = 1/2 na escala S
    assert contribuicao_drives({"fome": 3}, {"fome": 3}) == {"fome": 0}
    with pytest.raises(ValueError):
        contribuicao_drives({"fome": 1}, {"cansaco": 1})
    with pytest.raises(ValueError):
        contribuicao_drives({"fome": 2000}, {"fome": 1})
    with pytest.raises(ValueError):
        contribuicao_drives({"fome": 0.5}, {"fome": 1})


def test_parcelas_somam_um_com_valor_absoluto():
    assert parcelas_drives({"tedio": 3, "cansaco": -1}) == {"tedio": 0.75, "cansaco": 0.25}    # brincar: o tedio cai, o cansaco sobe
    assert parcelas_drives({"a": 0, "b": 0}) is None


def test_dominancia_numa_vida():
    dec = [(D8, "tempo_livre", {"a": 90, "b": -10}),          # a lidera (0,9)
           (D8 + 15, "bola_no_cenario", {"a": 50, "b": 50}),   # dividida: sem lider
           (D8 + 30, "tempo_livre", {"a": 80, "b": 20}),       # 0,80 exato: lidera
           (D8 + 45, "tempo_livre", {"a": 5, "b": -5}),        # D_antes = D_depois: sem sinal, fora
           (D8 + 60, "tempo_livre", {"a": 0, "b": 0}),         # fora
           (D8 + 75, "fome_urgente", {"a": 0, "b": 40}),       # o resto: b lidera
           (0, "tempo_livre", {"a": 0, "b": 70})]              # fora da janela
    r = dominancia_decisoes(dec)
    tl, resto = r["tempo_livre"], r["resto"]
    assert (tl["n"], tl["lideradas"], tl["sem_lider"]) == (3, {"a": 2, "b": 0}, 1)
    assert tl["f"] == {"a": pytest.approx(2 / 3), "b": 0.0}
    assert tl["parcela"] == {"a": pytest.approx(220 / 300), "b": pytest.approx(80 / 300)}
    assert tl["contribuicao"] == {"a": 220, "b": 60} and tl["soma_abs"] == {"a": 220, "b": 80}
    assert (resto["n"], resto["f"]) == (1, {"a": 0.0, "b": 1.0})
    assert dominancia_decisoes([], (0, 1440))["tempo_livre"]["n"] == 0
    with pytest.raises(ValueError):
        dominancia_decisoes(dec, limiar=0.5)
    assert (LIMIAR_LIDERA, LIMIAR_DOMINA) == (0.80, 0.50)


def test_leitura_domina_pelo_ic():
    r = leitura_dominancia({"a": [0.9, 0.8, 0.85, 0.95], "b": [0.1, 0.6, None], "c": [0.7, None]})
    assert r["a"]["domina"] is True and r["a"]["ic"]["ic_inferior"] >= 0.8                 # toda reamostragem fica acima de 0,8
    assert r["b"]["domina"] is False and r["b"]["sem_valor"] == 1
    assert r["c"]["domina"] is None and r["c"]["motivo"] and r["c"]["media"] == 0.7
    assert r["a"]["ic"]["n"] == 4


# ------------------------------------------------------------------ na bancada


def _bancada(dias=3, canais=True, montagem="completa"):
    cc = replace(CONFIG_CONSEQUENCIA, canais_ligados=canais)
    return bv.Bancada(dias, 16 * dias, cfg_lobos=bv.cfg_lobos_do_ponto("T3"), cfg_consequencia=cc, montagem=montagem)


@pytest.mark.parametrize("mundo", ["padrao", "bola", "descasado", "mutavel"])
def test_o_sinal_da_medida_bate_com_os_canais_do_cerebro(mundo):
    b = _bancada()
    v = b.vida(bv.EspecVida("atencioso", "P1", 202, None, mundo))
    d = b.medir(v, SONDA)["dominancia"]
    assert d["origem"] == "sinal" and d["conferido_com_canais"]
    tl = d["vida_toda"]["tempo_livre"]
    assert tl["n"] > 0 and sum(tl["lideradas"].values()) + tl["sem_lider"] == tl["n"]
    if mundo in ("descasado", "mutavel"):                     # a fruta com a E2: a tristeza (o humor) entra no sinal
        assert "tristeza" in d["vida_toda"]["resto"]["f"] or "tristeza" in tl["f"]


def test_a_conferencia_com_os_canais_falha_alto(monkeypatch):
    b = _bancada()
    v = b.vida(bv.EspecVida("aleatorio", "P1", 303, None, "bola"))
    monkeypatch.setattr(bv, "sinal_por_canal", lambda *a: {"fome": 1})
    with pytest.raises(RuntimeError, match="divergem"):
        b.medir(v, SONDA)


@pytest.mark.parametrize("braco,cerebro", [("P0", "lobos"), ("P0", "instinto"), ("P3", "lobos")])
def test_a_sonda_nos_bracos_que_nao_aprendem_pela_consequencia(braco, cerebro):
    b = _bancada()
    v = b.vida(bv.EspecVida("relapso", braco, 101, None, "descasado", cerebro))
    d = b.medir(v, SONDA)["dominancia"]                      # o instinto nao tem o gancho da fruta: o registro so anota
    assert d["origem"] == "sonda" and not d["conferido_com_canais"]
    assert d["vida_toda"]["tempo_livre"]["n"] + d["vida_toda"]["resto"]["n"] > 0


def test_sem_canais_a_medida_sai_sem_conferir():
    b = _bancada(canais=False, montagem="simples")              # na completa o P1 liga os canais de qualquer jeito
    v = b.vida(bv.EspecVida("atencioso", "P1", 101, None, "bola"))
    d = b.medir(v, SONDA)["dominancia"]
    assert d["origem"] == "sinal" and not d["conferido_com_canais"]


def test_no_mundo_fisico_tambem():
    b = bv.Bancada(2, 32)
    v = b.vida(bv.EspecVida("atencioso", "P1", 101, None, "fisico", lugar="perto"))
    d = b.medir(v, SONDA)["dominancia"]
    assert d["origem"] == "sinal" and d["janela"] == [0, 2 * 1440]


def _medida(braco, mundo, dono, semente, lideradas, n, origem="sinal"):
    tl = {"n": n, "lideradas": lideradas, "soma_abs": {d: 10 * v for d, v in lideradas.items()},
          "contribuicao": {d: v for d, v in lideradas.items()}, "sem_lider": n - sum(lideradas.values())}
    vazio = {"n": 0, "lideradas": {}, "soma_abs": {}, "contribuicao": {}, "sem_lider": 0}
    return {"vida": f"{dono}-{braco}@{semente}", "braco": braco, "condicao": "casado", "mundo": mundo, "dono": dono,
            "genoma": None, "semente": semente, "dominancia": {"origem": origem, "na_janela": {"tempo_livre": tl, "resto": vazio}}}


def test_tabela_da_dominancia_soma_as_celulas_da_unidade():
    medidas = {}
    for semente, (l1, n1, l2, n2) in {101: (9, 10, 8, 10), 202: (10, 10, 10, 10), 303: (6, 10, 9, 10)}.items():
        medidas[f"x{semente}"] = _medida("P1", "bola", "atencioso", semente, {"tedio": l1, "cansaco": 0}, n1)
        medidas[f"y{semente}"] = _medida("P1", "bola", "relapso", semente, {"tedio": l2, "cansaco": 0}, n2)
    t = bv.tabela_dominancia(medidas)["P1"]["casado/bola"]
    assert t["origem"] == "sinal" and t["unidades"] == 3
    tl = t["tempo_livre"]
    assert tl["f_por_unidade"]["tedio"] == [17 / 20, 20 / 20, 15 / 20]           # os dois donos somados por unidade
    assert tl["leitura"]["tedio"]["domina"] is True and tl["leitura"]["cansaco"]["domina"] is False
    assert tl["decisoes"] == 60 and tl["parcela"] == {"cansaco": 0.0, "tedio": 1.0}
    medidas["z"] = _medida("P1", "bola", "aleatorio", 101, {"tedio": 1}, 1, origem="sonda")
    with pytest.raises(RuntimeError, match="origem"):
        bv.tabela_dominancia(medidas)


def test_rodar_grava_o_dominancia_json(tmp_path):
    cfg = {"bracos": ["P0", "P1"], "donos": ["atencioso"], "sementes": [101, 202], "mundos": ["bola", "descasado"], "dias": 2,
           "orcamento": 32, "ponto": "T3", "montagem": "completa", "consequencia": {"canais_ligados": True},
           "sonda": SONDA, "bootstrap": {"reamostragens": 100, "semente": 101, "nivel": 0.95}}
    bv.rodar(cfg, tmp_path)
    dom = json.loads((tmp_path / "dominancia.json").read_text(encoding="utf-8"))
    assert set(dom) == {"P0", "P1"} and set(dom["P1"]) == {"casado/bola", "descasado/descasado"}
    assert dom["P0"]["casado/bola"]["origem"] == "sonda" and dom["P1"]["casado/bola"]["origem"] == "sinal"
    cel = dom["P1"]["casado/bola"]["tempo_livre"]
    assert {"decisoes", "f_por_unidade", "leitura", "parcela", "contribuicao"} <= set(cel)
    medidas = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    assert all(m["dominancia"]["conferido_com_canais"] == (m["braco"] == "P1") for m in medidas.values())


# ------------------------------------------------------------------ o P1-cw


def test_p1_cw_declarado_como_o_p1_c_com_a_chave():
    """Desde a W-BANCADA-CORPO o P1-cw e o P1-c (o corpo) com a pesos_janela, como o plano pede (A2.4): espera a etapa 6 do corpo
    (NOS_PENDENTES["corpo"]); tests/test_bancada_pesos_janela.py confere o mecanismo num braco de teste sem o no."""
    b = bv.BRACOS["P1-cw"]
    assert (b.fonte, b.no, b.pesos_janela) == ("consequencia", "corpo-A2.4", True)
    assert b == bv.replace(bv.BRACOS["P1-c"], rotulo="P1-cw", no="corpo-A2.4", pesos_janela=True)
    with pytest.raises(NotImplementedError, match="etapa 6"):
        bv.braco_de("P1-cw")
    with pytest.raises(NotImplementedError, match="etapa 6"):
        bv.validar_config({"bracos": ["P1", "P1-cw"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16,
                           "sonda": SONDA, "bootstrap": {}, "mundos": ["bola"]})
