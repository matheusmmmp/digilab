"""A linha de base do intervalo, o R-a (docs/PLANO_ANALISE_V3_PET_VIVO_RA.md, secao 7): `metrics.medidas_linha_base` e o orquestrador
do replay (experiments/run_v3_pet_vivo_ra.py). So as sementes dos testes e vidas montadas a mao: nenhuma vida da run do PV-2."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_pet_vivo_ra as RA  # noqa: E402
import run_v3_pet_vivo_r1 as R  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402

S = 1024
CFG = json.loads((RAIZ / "experiments/configs/v3_pet_vivo/ra.json").read_text(encoding="utf-8"))


def _noite(tick_do_dia: int) -> bool:
    return CONFIG_PADRAO.e_noite(tick_do_dia)


def _vida(decisoes: list[tuple]) -> list[dict]:
    """uma vida montada a mao: cada decisao e (comportamento, r_n do intervalo, tick, a fome lida na decisao); so o que a medida le"""
    motivos = []
    for k, (comp, rn, tick, fome) in enumerate(decisoes):
        motivos.append({"escolha": (comp, None), "cadeia": {
            "id": k, "leitura": {"fome": fome, "tedio": 0}, "mesmo_tick": {"delta": {"fome": 0, "tedio": 0}},
            "intervalo": {"r_n": rn, "tick_de": tick, "ja_contado": False}}})
    return motivos


@pytest.fixture(scope="module")
def vida_real():
    """uma vida do HOJE nas sementes dos testes (101, comedouro), com o rastro"""
    return R.orq.cerebro_de(R._vida_de_teste(101, True, 4, lugar="comedouro")[1]).motivos


# ------------------------------------------------------------------ a medida, a mao
def test_global_e_ctx_a_mao():
    m = _vida([("dormir", 100, 0, S), ("dormir", 60, 15, S), ("comer", -40, 30, S), ("explorar", -120, 45, S)])
    lb = met.medidas_linha_base(m, S, _noite, piso=1)["linhas"]
    assert lb["GLOBAL"]["resto"] == {"comer": -40.0, "dormir": 80.0, "explorar": -120.0}       # a media da vida e 0
    assert lb["GLOBAL"]["resto_dormir"] == 80.0
    assert lb["CTX"]["resto_dormir"] == 0.0                                                    # por construcao (D-RA-18)
    assert lb["CTX"]["resto"] == {"comer": 40.0, "dormir": 0.0, "explorar": -40.0}


def test_fase_a_mao():
    # o tick 0 e noite e o 600 (10 h) e dia: a linha de base e a media de cada fase
    m = _vida([("dormir", 100, 0, S), ("comer", 20, 15, S), ("dormir", 50, 600, S), ("explorar", -70, 615, S)])
    r = met.medidas_linha_base(m, S, _noite, piso=1)
    assert r["fase"] == {"dia": 2, "noite": 2}
    assert r["linhas"]["FASE"]["resto"] == {"comer": -40.0, "dormir": 50.0, "explorar": -60.0}
    assert r["linhas"]["FASE"]["resto_dormir"] == 50.0


def test_estado_a_mao():
    # a carga e (S - fome)^2: as 4 decisoes caem uma em cada quartil, entao o resto de todas e 0
    m = _vida([("dormir", 100, 0, 1000), ("comer", 20, 15, 800), ("dormir", 50, 30, 600), ("explorar", -70, 45, 400)])
    lb = met.medidas_linha_base(m, S, _noite, piso=1)["linhas"]["ESTADO"]
    assert lb["resto"] == {"comer": 0.0, "dormir": 0.0, "explorar": 0.0}
    # com 8 decisoes, duas por quartil, pela ordem da carga
    m = _vida([("dormir", 10, 0, 1000), ("comer", 30, 15, 990), ("dormir", 50, 30, 800), ("comer", 70, 45, 790),
               ("dormir", 1, 60, 600), ("comer", 3, 75, 590), ("dormir", 5, 90, 400), ("comer", 7, 105, 390)])
    lb = met.medidas_linha_base(m, S, _noite, piso=1)["linhas"]["ESTADO"]
    assert lb["resto"] == {"comer": 5.5, "dormir": -5.5}                                       # (10+10+1+1)/4 e o oposto


def test_movel_a_mao():
    m = _vida([("dormir", 8, 0, S), ("dormir", 8, 15, S), ("comer", 0, 30, S)])
    lb = met.medidas_linha_base(m, S, _noite, ks=(2,), piso=1)["linhas"]["MOVEL-2"]
    # b: 0 -> 4 -> 6; os restos: 8 - 0, 8 - 4, 0 - 6 (a linha de base nunca usa a decisao atual)
    assert lb["resto"] == {"comer": -6.0, "dormir": 6.0}


def test_o_piso_tira_o_comportamento_raro_do_eta2_do_acordado():
    dec = [("dormir", 50, 15 * k, S) for k in range(6)] + [("comer", -10 - k, 90 + 15 * k, S) for k in range(6)]
    dec += [("explorar", -30 - k, 180 + 15 * k, S) for k in range(6)] + [("ocioso", 500, 270, S)]
    r = met.medidas_linha_base(_vida(dec), S, _noite)
    assert r["piso"] == 5 and r["contagem"]["ocioso"] == 1
    assert r["acordados_no_eta2"] == ["comer", "explorar"]
    sem = met.medidas_linha_base(_vida(dec[:-1]), S, _noite)
    # o ocioso fora do eta2 do acordado: ele so muda a media global, e o eta2 entre o comer e o explorar nao muda
    assert r["linhas"]["GLOBAL"]["eta2_acordado"] == sem["linhas"]["GLOBAL"]["eta2_acordado"]
    assert r["linhas"]["GLOBAL"]["eta2_todas"] != sem["linhas"]["GLOBAL"]["eta2_todas"]


def test_falha_alto():
    with pytest.raises(ValueError, match="rastro"):
        met.medidas_linha_base([{"escolha": ("dormir", None)}], S, _noite)
    m = _vida([("dormir", 1, 0, S), ("comer", 2, 15, S)])
    m[1]["cadeia"]["intervalo"]["tick_de"] = None
    with pytest.raises(ValueError, match="tick"):
        met.medidas_linha_base(m, S, _noite)
    m = _vida([("dormir", 1, 0, S)])
    m[0]["cadeia"]["leitura"]["inventado"] = 3
    m[0]["cadeia"]["mesmo_tick"]["delta"]["inventado"] = 0
    with pytest.raises(KeyError, match="inventado"):
        met.medidas_linha_base(m, S, _noite)


# ------------------------------------------------------------------ numa vida das sementes dos testes
def test_c_igual_r1_numa_vida_de_teste(vida_real):
    acao = json.loads(json.dumps(met.medidas_rastro(vida_real)["acao"]))
    lb = json.loads(json.dumps(met.medidas_linha_base(vida_real, S, _noite)))
    RA.conferir_igual_r1("teste", lb["linhas"], acao)
    assert set(lb["linhas"]) == set(RA.LINHAS)
    torto = copy.deepcopy(acao)
    torto["eta2_global"] = (torto["eta2_global"] or 0) + 0.25
    with pytest.raises(RA.LinhaBaseDivergiu, match="eta2 da GLOBAL"):
        RA.conferir_igual_r1("teste", lb["linhas"], torto)
    torto = copy.deepcopy(acao)
    torto["por_comportamento"]["dormir"]["resto_contexto"] = 1.0
    with pytest.raises(RA.LinhaBaseDivergiu, match="resto por comportamento da CTX"):
        RA.conferir_igual_r1("teste", lb["linhas"], torto)


def test_o_tick_do_rastro_e_o_da_decisao(vida_real):
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    cadeias = [m["cadeia"] for m in vida_real if "cadeia" in m]
    assert [c["intervalo"]["tick_de"] for c in cadeias] == [passo * c["id"] for c in cadeias]


def test_a_medida_e_deterministica_e_nao_mexe_nos_motivos(vida_real):
    antes = copy.deepcopy(vida_real)
    a = met.medidas_linha_base(vida_real, S, _noite)
    assert vida_real == antes
    assert a == met.medidas_linha_base(vida_real, S, _noite)


# ------------------------------------------------------------------ a regra de leitura e as recusas do orquestrador
def _resumos(resto: dict, eta: dict) -> dict:
    """os resumos do HOJE nos 3 lugares, com o mesmo IC em todos: `resto[linha]` e `eta[linha]` sao (inferior, superior)"""
    medidas = {}
    for nome in RA.LINHAS:
        a, b = resto.get(nome, (10.0, 20.0))
        medidas[f"resto_dormir|{nome}"] = {"ic_inferior": a, "ic_superior": b}
        a, b = eta.get(nome, (0.01, 0.02))
        medidas[f"eta2_acordado|{nome}"] = {"ic_inferior": a, "ic_superior": b}
    return {f"run|HOJE|{lugar}": {"medidas": copy.deepcopy(medidas)} for lugar in RA.LUGARES}


def test_leitura_as_regras_escritas_antes():
    lei = RA.leitura(_resumos({}, {}))
    assert {v["leitura"] for v in lei["L-SONO"].values()} == {"preserva o sono"}
    assert set(lei["L-SONO"]) == {"FASE", "ESTADO", "MOVEL-4", "MOVEL-16", "MOVEL-96"}
    assert lei["L-ALEM"]["leitura"] == "so o sono"
    lei = RA.leitura(_resumos({"MOVEL-4": (-5.0, -1.0), "FASE": (-1.0, 3.0)}, {"ESTADO": (0.06, 0.09)}))
    assert lei["L-SONO"]["MOVEL-4"]["leitura"] == "apaga o sono"
    assert lei["L-SONO"]["FASE"]["leitura"] == "indeterminado"
    assert lei["L-ALEM"]["leitura"] == "ha o que creditar alem do sono"
    assert RA.leitura(_resumos({}, {"MOVEL-96": (0.03, 0.06)}))["L-ALEM"]["leitura"] == "indeterminado"
    # a CTX nao entra no ramo "so o sono"
    assert RA.leitura(_resumos({}, {"CTX": (0.03, 0.9)}))["L-ALEM"]["leitura"] == "so o sono"
    sem = _resumos({}, {})
    sem["run|HOJE|longe"]["medidas"]["eta2_acordado|ESTADO"]["ic_inferior"] = None
    with pytest.raises(RA.LinhaBaseDivergiu, match="sem o IC"):
        RA.leitura(sem)


def test_leitura_em_dois_lugares():
    r = _resumos({}, {})
    for lugar in ("comedouro", "longe"):
        r[f"run|HOJE|{lugar}"]["medidas"]["eta2_acordado|ESTADO"] = {"ic_inferior": 0.06, "ic_superior": 0.08}
    assert RA.leitura(r)["L-ALEM"]["leitura"] == "ha o que creditar alem do sono"


def test_config_e_plano():
    RA.conferir_config(CFG)
    RA.exigir_aprovado((RAIZ / RA.PLANO).read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="APROVADO"):
        RA.exigir_aprovado("**Status: PROPOSTO, a espera do Matheus.**")
    with pytest.raises(ValueError, match="a letra"):
        RA.conferir_config({**CFG, "dias": 7})
    with pytest.raises(ValueError, match="sobram"):
        RA.conferir_config({**CFG, "extra": 1})
    with pytest.raises(ValueError, match="processos"):
        RA.rodar(CFG, RAIZ / "nao_existe", 5, Path("nao_existe.tar.gz"))


def test_o_orquestrador_tem_o_nome_que_o_pre_run_reconhece():
    import re
    assert re.fullmatch(r"experiments/run_v[23]_\w+\.py", RA.ORQUESTRADOR)
    assert (RAIZ / RA.ORQUESTRADOR).is_file()


def test_escalares_e_resumo():
    dec = [("dormir", 50 + k, 15 * k, S) for k in range(6)] + [("comer", -10 - k, 90 + 15 * k, 500) for k in range(6)]
    lb = json.loads(json.dumps(met.medidas_linha_base(_vida(dec), S, _noite)))
    reg = [{"grupo": "run", "braco": "HOJE", "lugar": "longe", "semente": s, "dono": d, "linha_base": lb}
           for s in (1, 2, 3) for d in ("atencioso", "relapso")]
    r = RA.resumo(reg, "run", "HOJE", "longe")
    assert r["vidas"] == 6 and r["unidades"] == 3
    m = r["medidas"]["resto_dormir|GLOBAL"]
    assert m["n"] == 3 and m["media"] == lb["linhas"]["GLOBAL"]["resto_dormir"]
    assert r["medidas"]["n:dormir"]["media"] == 6
    with pytest.raises(RA.LinhaBaseDivergiu, match="nenhuma vida"):
        RA.resumo(reg, "run", "HOJE", "comedouro")
