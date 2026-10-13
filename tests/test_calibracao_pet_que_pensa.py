"""V2, W-BANCADA-PQP-PLANO: a config e o orquestrador da calibracao do g_plano do J5 (docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, secoes 5, 8 e
11; PP-6), SEM rodar: so a fumaca nas sementes dos testes.

O que se confere:
- a config da calibracao e a do plano: as bases 45101...45505 (K_u = 4), so o P1-plan na fase 1 de 7 dias, a grade {S/4, S/2, S}, os dias
  4 a 6, a faixa [0,10; 0,40], o cerebro no ponto da K2, o mundo da calibracao do mundo e o corpo do passo 0 fino (adendo 5);
- a fumaca e a mesma config nas sementes dos testes;
- as recusas (as bases da validacao, o g_plano na config, outro braco ou protocolo, os dias fora da fase 1, a grade, a pasta que existe);
- a regra em dados com a resposta conhecida (o menor na faixa; senao o mais perto, empate no menor; sem nada, falha alto);
- a fumaca inteira: os tres pontos pela bancada, a medida recontada das medidas gravadas e a escolha pela regra.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa as cp  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa"


def _cfg(nome: str = "calibracao") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def test_a_config_da_calibracao_e_a_do_plano():
    c = cp.validar(_cfg())
    assert c["plano"] == bv.PLANO_PQP and (RAIZ / c["plano"]).is_file()
    assert c["unidades"] == {"bases": list(bv.BASES_PET_QUE_PENSA["calibracao"]), "k": 4, "prefixo": "pet_que_pensa"}
    assert (c["bracos"], c["protocolos"], c["d_a"], c["janela"], c["n_mao"]) == (["P1-plan"], ["fase1"], 7, 3, 2)
    S = 1024
    assert c["calibracao_g_plano"] == {"grade": [S // 4, S // 2, S], "dias": [4, 6], "faixa": [0.10, 0.40]}
    assert (c["dono"], c["lugar"], c["orcamento_por_dia"], c["ponto"], c["montagem"]) == ("atencioso", "comedouro", 16, "T3", "completa")
    k2 = json.loads((RAIZ / "artifacts_v2_calibracao_conjunta" / "escolha.json").read_text(encoding="utf-8"))["ponto"]
    assert c["lobos"] == {"memoria_ganho": k2["g"], "w0_pedido": k2["w0_pedido"], "w0_info": k2["w0_info"]}
    assert c["consequencia"] == {"ganho": k2["ganho"], "canais_ligados": True}
    mundo = json.loads((RAIZ / "artifacts_v2_mundo" / "calibracao" / "resultado.json").read_text(encoding="utf-8"))
    assert c["mundo"] == {"mult_queda": mundo["m_escolhido"]}
    p0 = json.loads((RAIZ / c["passo0"]).read_text(encoding="utf-8"))["escolha"]
    assert "adendo5" in c["passo0"] and p0["ponto"] == [4, 5] and p0["fechou"] and c["corpo"] == p0["corpo"]
    bp = bv.bancada_pqp_da_config(cp.config_do_ponto(c, 256))
    assert bp.g_plano == 256 and bp.cfg_corpo().metabolismo and bp.bancada.cfg_corpo.gasto_basal_acordado == 300


def test_a_fumaca_e_a_mesma_config_nas_sementes_dos_testes():
    c, f = _cfg(), _cfg("fumaca_calibracao")
    cp.validar(f)
    assert set(f["sementes"]) <= bv.SEMENTES_TESTE and "plano" not in f and "unidades" not in f
    assert f["calibracao_g_plano"]["grade"] == c["calibracao_g_plano"]["grade"]
    assert f["calibracao_g_plano"]["faixa"] == c["calibracao_g_plano"]["faixa"]
    iguais = set(c) - {"descricao", "plano", "unidades", "corpo", "passo0", "d_a", "janela", "calibracao_g_plano"}
    assert {k: f[k] for k in iguais} == {k: c[k] for k in iguais}


def test_as_recusas():
    c = _cfg()
    with pytest.raises(bv.SementeSemPlano, match="validacao"):
        cp.validar({**c, "unidades": {**c["unidades"], "bases": list(bv.BASES_PET_QUE_PENSA["validacao"])}})
    with pytest.raises(ValueError, match="g_plano"):
        cp.validar({**c, "g_plano": 256})
    with pytest.raises(ValueError, match="P1-plan"):
        cp.validar({**c, "bracos": ["P1-plan", "P1-plan-cong"]})
    with pytest.raises(ValueError, match="fase1"):
        cp.validar({**c, "protocolos": ["T1"]})
    for dias in ([4, 7], [-1, 2], [5, 4]):
        with pytest.raises(ValueError, match="dias"):
            cp.validar({**c, "calibracao_g_plano": {**c["calibracao_g_plano"], "dias": dias}})
    for grade in ([], [512, 256], [256, 256], [0, 256], [256.0]):
        with pytest.raises(ValueError, match="grade"):
            cp.validar({**c, "calibracao_g_plano": {**c["calibracao_g_plano"], "grade": grade}})
    with pytest.raises(ValueError, match="faixa"):
        cp.validar({**c, "calibracao_g_plano": {**c["calibracao_g_plano"], "faixa": [0.4, 0.1]}})
    with pytest.raises(ValueError, match="calibracao_g_plano"):
        cp.validar({k: v for k, v in c.items() if k != "calibracao_g_plano"})


def _ponto(g, media):
    return {"g_plano": g, "media": media}


def test_a_regra_com_a_resposta_conhecida():
    f = (0.10, 0.40)
    assert cp.escolha([_ponto(256, 0.05), _ponto(512, 0.12), _ponto(1024, 0.30)], f) == {"g_plano": 512, "media": 0.12, "fechou": True,
                                                                                          "desvio": 0.0}
    assert cp.escolha([_ponto(256, 0.10), _ponto(512, 0.2)], f)["g_plano"] == 256                    # a borda conta
    e = cp.escolha([_ponto(256, 0.02), _ponto(512, 0.04), _ponto(1024, 0.45)], f)
    assert (e["g_plano"], e["fechou"], e["lado"]) == (1024, False, "acima") and abs(e["desvio"] - 0.05) < 1e-12
    f2 = (0.125, 0.375)                                                                             # contas exatas em binario
    e = cp.escolha([_ponto(256, 0.4375), _ponto(512, 0.0625), _ponto(1024, None)], f2)              # empate em 0,0625: o menor
    assert (e["g_plano"], e["fechou"], e["lado"], e["desvio"]) == (256, False, "acima", 0.0625)
    with pytest.raises(RuntimeError, match="nenhum ponto"):
        cp.escolha([_ponto(256, None)], f)


def test_a_fumaca_inteira(tmp_path):
    f = _cfg("fumaca_calibracao")
    f = {**f, "sementes": [101]}
    r = cp.rodar(f, tmp_path / "cal", processos=1)
    g = json.loads((tmp_path / "cal" / "g_plano.json").read_text(encoding="utf-8"))
    assert [p["g_plano"] for p in g["pontos"]] == [256, 512, 1024] and g["escolha"] == r["escolha"]
    dias = tuple(f["calibracao_g_plano"]["dias"])
    for p in g["pontos"]:
        pasta = tmp_path / "cal" / f"g_plano_{p['g_plano']}"
        medidas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
        assert set(medidas) == {"P1-plan~fase1@101"} and json.loads((pasta / "meta.json").read_text(encoding="utf-8"))["g_plano"] == p["g_plano"]
        m = medidas["P1-plan~fase1@101"]
        assert m["g_plano"] == p["g_plano"] and "t1" not in m and "t2" not in m and m["tick_mudanca"] is None
        assert p["por_unidade"][0]["fracao"] == bv.fracao_plano_dias(m, dias)["fracao"] == p["media"]
        assert len(list((pasta / "vidas").glob("*.jsonl"))) == 1
    assert r["escolha"] == cp.escolha(g["pontos"], tuple(f["calibracao_g_plano"]["faixa"]))
    meta = json.loads((tmp_path / "cal" / "meta.json").read_text(encoding="utf-8"))
    assert meta["modelo_mundo_sha256"] and meta["lobos_sha256"] and meta["orquestrador_sha256"]
    with pytest.raises(FileExistsError):
        cp.rodar(f, tmp_path / "cal")
    assert cp.main(["--config", str(CONFIGS / "fumaca_calibracao.json"), "--saida", str(tmp_path / "main"), "--processos", "2"]) == 0
    assert (tmp_path / "main" / "g_plano.json").is_file()


# ------------------------------------------------------------------ o piloto (secao 6), em dados com a resposta conhecida


def _m(braco, prot, s, base, f_antes=None, valor=None, sem_exp=False):
    t = {"f_antes": f_antes, "sem_oportunidade": valor is None, "q": valor, "m": valor, "sem_exposicao": sem_exp}
    return {"braco": braco, "protocolo": prot, "semente": s, "unidade": {"base": base, "k": 0}, "t1" if prot == "T1" else "t2": t}


def _por(valores):
    """valores[(braco, prot)] = [(f_antes, valor), ...] por unidade (sementes 1..n, bases alternadas)"""
    med = {}
    for (b, p), vs in valores.items():
        for i, (fa, v) in enumerate(vs, 1):
            med[f"{b}~{p}@{i}"] = _m(b, p, i, 10 + i % 2, fa, v)
    return cp._por_unidade(med)


def test_as_margens_e_os_contrastes_do_piloto():
    um = [(0.5, 0.5), (1.0, 0.25), (None, None), (0.5, 0.0)]
    vals = {(b, p): um for b in bv.BRACOS_PQP for p in ("T1", "T2")}
    vals[("P1", "T1")] = [(0.5, 0.0), (1.0, 0.0), (0.5, 0.25), (0.5, 0.0)]
    por = _por(vals)
    mg = cp.margens(por)
    assert mg["delta_t1"] == 0.5 * (0.5 + 1.0 + 0.5) / 3 and mg["n_t1"] == 3
    assert mg["delta_t2"] == 0.5 * ((1 - 0.5) + 0 + (1 - 0.5)) / 3 and mg["com_espaco"] == {"T1": True, "T2": True}
    d = cp._difs(por, "t1", "q", "P1-plan", "P1")
    assert {s: v for s, (_b, v) in d.items()} == {1: 0.5, 2: 0.25, 4: 0.0}          # a unidade 3 sem oportunidade sai
    assert cp._agrupado(d) == {11: [0.5], 10: [0.25, 0.0]}
    pr = cp.premissas(por, cp.BOOTSTRAP_PILOTO)
    assert pr["G-OPORTUNIDADE"]["P1-plan/T1"] == {"sem": 1, "n": 4, "fracao": 0.25, "passa": True}
    assert pr["G-APRENDEU"]["P1-plan"]["n"] == 3 and pr["G-APRENDEU"]["P1-plan"]["passa"] is True    # todos >= 0,5 > 1/3


def test_o_n_efetivo_e_o_k_dos_dois_primarios():
    assert cp.n_efetivo(20, 15, 20) == 15 and cp.n_efetivo(25, 3, 4) == 18 and cp.n_efetivo(5, 0, 4) == 0
    forte = {s: (s % 5, 0.4 + 0.01 * (s % 3)) for s in range(20)}            # efeito grande e pouca variancia: chega no K_u minimo
    fraco = {s: (s % 5, (-1) ** s * 0.6) for s in range(20)}                 # media 0 e muita variancia
    poder = {**cp.PODER_PILOTO, "replicas": 200}
    r = cp.escolher_k_dois({"G-T1": forte, "G-T2": forte}, {"G-T1": 0.4, "G-T2": 0.4}, 20, 5, poder, 4242)
    assert r["chega_ao_alvo"] and r["k"] == 4 and r["n"] == 20 and r["escolhido"]["G-T1"]["n_efetivo"] == 20
    r = cp.escolher_k_dois({"G-T1": forte, "G-T2": fraco}, {"G-T1": 0.4, "G-T2": 0.05}, 20, 5, poder, 4242)
    assert not r["chega_ao_alvo"] and r["k"] == 10 and len(r["tabela"]) == 7    # sem chegar, K_u = 10 com o poder declarado


def test_o_piloto_recusa_a_pasta_que_existe(tmp_path):
    f = {**_cfg("fumaca_calibracao"), "sementes": [101]}
    cp.rodar(f, tmp_path / "cal", processos=1)
    r = cp.rodar_piloto(f, tmp_path / "cal", processos=1)
    assert r["g_plano"] == json.loads((tmp_path / "cal" / "g_plano.json").read_text(encoding="utf-8"))["escolha"]["g_plano"]
    assert set((tmp_path / "cal" / "piloto").iterdir()) >= {tmp_path / "cal" / "piloto" / b for b in bv.BRACOS_PQP}
    med = json.loads((tmp_path / "cal" / "piloto" / "P1" / "medidas.json").read_text(encoding="utf-8"))
    assert {m["g_plano"] for m in med.values()} == {0} and {m["protocolo"] for m in med.values()} == {"T1", "T2"}
    assert r["custo"]["vidas_por_unidade"] == 8 and (tmp_path / "cal" / "piloto" / "piloto.json").is_file()
    with pytest.raises(FileExistsError):
        cp.rodar_piloto(f, tmp_path / "cal")
