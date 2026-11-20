"""A leitura do painel DigiBrain (digilab/painel_digibrain.py, etapa 5 do W-PORTE): o gabarito da web em dia, as contas e as falhas
altas. Se mudar a leitura ou o gabarito dos lobos, rode `python experiments/exportar_gabarito_painel_digibrain.py`."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_lobos as GL  # noqa: E402
import exportar_gabarito_painel_digibrain as G  # noqa: E402

from digilab.painel_digibrain import LOBOS_BARRAS, leitura_aprendido, leitura_decisao, mapa_decisao, mapa_pesos  # noqa: E402
from digilab.policies.lobos import sortear  # noqa: E402


def test_gabarito_do_painel_em_dia():
    atual = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    assert atual == json.loads(json.dumps(G.gerar(), sort_keys=True))


def test_gabarito_do_mapa_em_dia():
    atual = json.loads(G.ARQUIVO_MAPA.read_text(encoding="utf-8"))
    assert atual == json.loads(json.dumps(G.gerar_mapa(), sort_keys=True))


def test_mapa_das_vidas():
    """as arestas: espessura e aprendido pelas contas, o corpo presente; as acesas: o termo da percepcao, forca maxima 1"""
    g = json.loads(G.ARQUIVO_MAPA.read_text(encoding="utf-8"))
    lobos = json.loads(GL.ARQUIVO.read_text(encoding="utf-8"))
    S, teto = g["S"], g["teto"]
    assert all(a["aprendido"] == 0.0 and a["w"] == a["w0"] for a in g["l0"])
    for vida, mapa, acesas in zip(lobos["v11"], g["pesos"], g["v11"]):
        for a in mapa["arestas"]:
            assert a["w"] != 0 or a["w0"] != 0
            assert a["espessura"] == (abs(a["w"]) / S) ** 0.5 and -1.0 <= a["aprendido"] <= 1.0
        assert any(a["entrada"] in g["receptores"] for a in mapa["arestas"])
        for m, d in zip(vida["motivos"], acesas["decisoes"]):
            linha = vida["pesos_prior"][m["regra"]][m["acao"]]
            termo = {x["entrada"]: x["termo"] for x in d["arestas"]}
            for p in leitura_decisao(m, linha, S, g["receptores"])["percepcao"]:
                assert termo[p["entrada"]] == p["termo"]
            assert max(x["forca"] for x in d["arestas"]) == 1.0 and d["lobo_decisivo"] == m["lobo_decisivo"]


def test_mapa_falha_alto():
    lobos = json.loads(GL.ARQUIVO.read_text(encoding="utf-8"))
    v = lobos["v11"][0]
    p0 = v["pesos_prior"]
    with pytest.raises(ValueError):                                          # regra que o mapa nao desenha
        mapa_pesos({**p0, "bola_no_cenario": p0["tempo_livre"]}, {**p0, "bola_no_cenario": p0["tempo_livre"]}, {}, {}, 1024, 16384, [])
    alem = json.loads(json.dumps(p0))
    alem["tempo_livre"]["brincar"][1] = 16385
    with pytest.raises(ValueError):                                          # alem do teto
        mapa_pesos(p0, alem, {}, {}, 1024, 16384, [])
    with pytest.raises(ValueError):
        mapa_decisao(v["motivos"][0], [1], 1024, [])


def test_leitura_das_vidas():
    """as barras somam o peso efetivo, as chances somam 1, a sonda e a do instinto e o aprendido aparece em alguma decisao"""
    g = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    lobos = json.loads(GL.ARQUIVO.read_text(encoding="utf-8"))
    mudou = 0
    for secao in ("l0", "v11"):
        for vida, leituras in zip(lobos[secao], g[secao]):
            for m, d in zip(vida["motivos"], leituras["decisoes"]):
                assert d["n"] == m["n"] and d["acao"] == m["acao"]
                assert set(d["barras"]) == set(LOBOS_BARRAS)
                assert sum(d["barras"].values()) == pytest.approx(1.0, abs=1e-12)
                assert sum(c["chance"] for c in d["chances"]) == pytest.approx(1.0, abs=1e-12)
                assert [c["acao"] for c in d["chances"]] == m["candidatos"]
                assert len(d["percepcao"]) <= 3 and all(p["entrada"] != "vies" and p["termo"] != 0.0 for p in d["percepcao"])
                assert [abs(p["termo"]) for p in d["percepcao"]] == sorted((abs(p["termo"]) for p in d["percepcao"]), reverse=True)
                q = d["quem_decidiu"]
                if m["u"] is None:
                    assert q == {"escolha": False, "acao_instinto": m["acao"], "mudou": False}
                else:
                    cand = m["candidatos"]
                    assert q["acao_instinto"] == cand[sortear([m["contribuicoes"]["impulsos"][a] for a in cand], m["u"])]
                    mudou += q["mudou"]
                if secao == "l0":
                    assert d["barras"]["decisao"] == d["barras"]["corpo"] == 0.0 and not q["mudou"]
    assert mudou > 0


def test_aprendido_ordena_e_corta():
    assert leitura_aprendido({"ocioso": 0.1, "explorar": -0.3, "brincar": 0.0, "chamar_atencao": 0.1}) == [
        {"acao": "explorar", "desvio": -0.3}, {"acao": "ocioso", "desvio": 0.1}, {"acao": "chamar_atencao", "desvio": 0.1}]
    assert leitura_aprendido({"ocioso": 0.0}) == []
    with pytest.raises(ValueError):
        leitura_aprendido({"voar": 1.0})


def _motivo() -> dict:
    lobos = json.loads(GL.ARQUIVO.read_text(encoding="utf-8"))
    return next(m for m in lobos["v11"][0]["motivos"] if m["u"] is not None and m["regra"] == "tempo_livre")


def test_falha_alto():
    lobos = json.loads(GL.ARQUIVO.read_text(encoding="utf-8"))
    prior = lobos["v11"][0]["pesos_prior"]
    rec = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))["receptores"]
    m = _motivo()
    linha = prior[m["regra"]][m["acao"]]
    leitura_decisao(m, linha, 1024, rec)
    errado = json.loads(json.dumps(m))
    errado["contribuicoes"]["decisao"][m["acao"]] += 1e-9          # a decisao do motivo nao e o aprendido mais o corpo
    with pytest.raises(ValueError):
        leitura_decisao(errado, linha, 1024, rec)
    with pytest.raises(ValueError):
        leitura_decisao(m, linha[:-1], 1024, rec)
    with pytest.raises(ValueError):
        leitura_decisao(m, linha, 1024, rec[:-1])
    fora = {**m, "acao": "dormir"}
    with pytest.raises(ValueError):
        leitura_decisao(fora, linha, 1024, rec)
