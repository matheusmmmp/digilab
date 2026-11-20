"""O R-sono (docs/PLANO_ANALISE_V3_PET_VIVO_SONO.md): a medida do caminho do sono, as conferencias e a regra de leitura."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_pet_vivo_r1 as R  # noqa: E402
import run_v3_pet_vivo_sono as SN  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO  # noqa: E402

LAM = CONFIG_DIGIBRAIN_INATOS.lambda_sono
PASSO = CONFIG_PADRAO.intervalo_decisao_ticks
CFG = json.loads((RAIZ / "experiments/configs/v3_pet_vivo/sono.json").read_text(encoding="utf-8"))


def _un(comportamento: str, w: int, inato: int = 0, habito: int = 0) -> dict:
    return {"chave": [comportamento, None, None], "termos": {"inato": inato, "habito": habito}, "a": max(w, 0), "w": w}


def _dec(k: int, escolha: str, energia: int, reflexo: bool = False, u=0.5, unidades=None) -> dict:
    """uma decisao a mao: a escolha, a leitura da energia, o reflexo, o u do sorteio e as unidades com o peso"""
    if unidades is None:
        unidades = [_un("dormir", 300, inato=250, habito=50), _un("comer", 100), _un("explorar", 400)]
    return {"k": k, "escolha": [escolha, None, None], "reflexo": reflexo, "u": None if reflexo else u, "unidades": unidades,
            "cadeia": {"leitura": {"energia": energia}}}


def _vida(decisoes: list[dict]) -> list[dict]:
    """as decisoes com o rastro e, no fim, a ultima da vida, que nao fecha e nao tem o rastro"""
    return decisoes + [{"k": len(decisoes), "escolha": ["ocioso", None, None], "reflexo": False, "u": None, "unidades": []}]


@pytest.fixture(scope="module")
def vida_real():
    """uma vida do HOJE nas sementes dos testes (101, comedouro), com o rastro"""
    return R.orq.cerebro_de(R._vida_de_teste(101, True, 4, lugar="comedouro")[1]).motivos


# ------------------------------------------------------------------ a medida, a mao
def test_os_quatro_caminhos_e_o_episodio_a_mao():
    so_dormir = [_un("dormir", 200, inato=200), _un("comer", 0)]
    vida = _vida([
        _dec(0, "dormir", LAM - 1, reflexo=True),       # episodio 1 comeca pelo REFLEXO
        _dec(1, "dormir", LAM + 10),                    # ... e segue pelo sorteio: fica no episodio do reflexo
        _dec(2, "dormir", LAM + 50, reflexo=True),      # ... e pelo sono que segura
        _dec(3, "explorar", 600),
        _dec(4, "dormir", 500),                         # episodio 2 comeca pelo SORTEIO
        _dec(5, "dormir", LAM - 5, reflexo=True),       # ... e cai no reflexo: fica no episodio do sorteio
        _dec(6, "comer", 700),
        _dec(7, "dormir", 800, u=None, unidades=so_dormir),   # episodio 3: o candidato UNICO
        _dec(8, "explorar", 900),
    ])
    cs = met.medidas_caminho_sono(vida, LAM, PASSO)
    assert cs["n"] == 9 and cs["dormir"] == 6 and cs["passo"] == PASSO
    assert cs["decisoes"] == {"REFLEXO": 2, "SEGURA": 1, "SORTEIO": 2, "UNICO": 1}
    assert cs["episodios"] == {"REFLEXO": 1, "SEGURA": 0, "SORTEIO": 1, "UNICO": 1}
    assert cs["ticks_decisao"] == {"REFLEXO": 2 * PASSO, "SEGURA": PASSO, "SORTEIO": 2 * PASSO, "UNICO": PASSO}
    assert cs["ticks_episodio"] == {"REFLEXO": 3 * PASSO, "SEGURA": 0, "SORTEIO": 2 * PASSO, "UNICO": PASSO}
    assert cs["F_PESOS"] == 3 / 6 and cs["F_PESOS_DEC"] == 3 / 6
    assert cs["sem_reflexo_exausto"] == 0
    assert tuple(cs["decisoes"]) == met.CAMINHOS_SONO


def test_a_margem_so_no_sorteio_a_mao():
    perde = [_un("dormir", 100, inato=120, habito=-20), _un("explorar", 300), _un("brincar", 0)]
    vida = _vida([
        _dec(0, "dormir", 400),                          # w 300 de 800; folga 300 - 400; o comer e candidato; aprendido 50
        _dec(1, "dormir", 600, unidades=perde),          # w 100 de 400; folga -200; sem comer nem brincar com peso; aprendido -20
        _dec(2, "dormir", LAM - 1, reflexo=True),        # fora da margem
        _dec(3, "explorar", 500),                        # acordado: a chance do dormir 300/800
        _dec(4, "comer", LAM - 1, unidades=[_un("comer", 50)]),   # acordado e exausto sem reflexo: fora do acordado, contado ao lado
    ])
    cs = met.medidas_caminho_sono(vida, LAM, PASSO)
    m = cs["margem"]
    assert m["n"] == 2
    assert m["energia_media"] == 500 and (m["energia_q1"], m["energia_mediana"], m["energia_q3"]) == (400, 400, 600)
    assert m["chance_dormir"] == pytest.approx((300 / 800 + 100 / 400) / 2)
    assert m["folga_media"] == (-100 - 200) / 2 and m["folga_negativa"] == 1.0
    assert m["comer_ou_brincar_candidato"] == 0.5
    assert m["aprendido_medio"] == (50 - 20) / 2
    assert cs["acordado"] == {"n": 1, "chance_dormir": 300 / 800, "dormir_candidato": 1.0}
    assert cs["sem_reflexo_exausto"] == 1


def test_a_vida_sem_dormir_e_a_sem_sorteio():
    cs = met.medidas_caminho_sono(_vida([_dec(0, "explorar", 600), _dec(1, "comer", 700)]), LAM, PASSO)
    assert cs["dormir"] == 0 and cs["F_PESOS"] is None and cs["F_PESOS_DEC"] is None
    assert cs["margem"]["n"] == 0 and cs["margem"]["energia_media"] is None
    cs = met.medidas_caminho_sono(_vida([_dec(0, "dormir", LAM - 1, reflexo=True)]), LAM, PASSO)
    assert cs["F_PESOS"] == 0.0 and cs["margem"]["chance_dormir"] is None and cs["acordado"]["n"] == 0


def test_falha_alto():
    with pytest.raises(ValueError, match="sem nenhuma decisao com o rastro"):
        met.medidas_caminho_sono(_vida([]), LAM, PASSO)
    with pytest.raises(ValueError, match="com o reflexo e a escolha"):
        met.medidas_caminho_sono(_vida([_dec(0, "comer", LAM - 1, reflexo=True)]), LAM, PASSO)
    sem = _dec(0, "dormir", 500)
    sem["cadeia"]["leitura"] = {}
    with pytest.raises(ValueError, match="sem a leitura da energia"):
        met.medidas_caminho_sono(_vida([sem]), LAM, PASSO)
    with pytest.raises(ValueError, match="sem a unidade do dormir"):
        met.medidas_caminho_sono(_vida([_dec(0, "dormir", 500, unidades=[_un("comer", 10), _un("explorar", 5)])]), LAM, PASSO)


# ------------------------------------------------------------------ as conferencias, numa vida das sementes dos testes
def test_c_reflexo_e_c_soma_numa_vida_de_teste(vida_real):
    cs = json.loads(json.dumps(met.medidas_caminho_sono(vida_real, LAM, PASSO)))
    SN.conferir_caminhos("teste", "run", vida_real, cs)
    assert cs["n"] == len(vida_real) - 1                 # a ultima decisao nao fecha e fica de fora
    assert cs["decisoes"]["SEGURA"] == 0 and cs["decisoes"]["REFLEXO"] > 0 and cs["decisoes"]["SORTEIO"] > 0
    assert 0 < cs["F_PESOS"] <= cs["F_PESOS_DEC"] <= 1   # o episodio que o reflexo comeca leva decisoes do sorteio com ele


def test_as_conferencias_falham_alto(vida_real):
    cs = json.loads(json.dumps(met.medidas_caminho_sono(vida_real, LAM, PASSO)))
    segura = copy.deepcopy(cs)
    segura["decisoes"]["SEGURA"] = 1
    with pytest.raises(SN.SonoDivergiu, match="C-REFLEXO"):
        SN.conferir_caminhos("teste", "run", vida_real, segura)
    exausto = {**copy.deepcopy(cs), "sem_reflexo_exausto": 2}
    with pytest.raises(SN.SonoDivergiu, match="C-REFLEXO"):
        SN.conferir_caminhos("teste", "run", vida_real, exausto)
    SN.conferir_caminhos("teste", "v38", vida_real, exausto)      # com o sono que segura, a C-REFLEXO nao le isso
    soma = copy.deepcopy(cs)
    soma["decisoes"]["SORTEIO"] += 1
    with pytest.raises(SN.SonoDivergiu, match="C-SOMA"):
        SN.conferir_caminhos("teste", "v38", vida_real, soma)
    troca = copy.deepcopy(cs)
    troca["decisoes"]["REFLEXO"] -= 1
    troca["decisoes"]["SORTEIO"] += 1
    with pytest.raises(SN.SonoDivergiu, match="C-SOMA"):
        SN.conferir_caminhos("teste", "v38", vida_real, troca)


def test_a_medida_e_deterministica_e_nao_mexe_nos_motivos(vida_real):
    antes = json.dumps(vida_real, sort_keys=True)
    a = met.medidas_caminho_sono(vida_real, LAM, PASSO)
    assert a == met.medidas_caminho_sono(vida_real, LAM, PASSO)
    assert json.dumps(vida_real, sort_keys=True) == antes


# ------------------------------------------------------------------ a regra de leitura e o orquestrador
def _resumos(ics: dict) -> dict:
    """os resumos do HOJE nos 3 lugares: `ics[lugar]` e o (inferior, superior) da F_PESOS; fora dele, (0.5, 0.6)"""
    out = {}
    for lugar in SN.LUGARES:
        a, b = ics.get(lugar, (0.5, 0.6))
        out[f"run|HOJE|{lugar}"] = {"medidas": {"F_PESOS": {"media": None if a is None else (a + b) / 2, "ic_inferior": a,
                                                            "ic_superior": b}}}
    return out


def test_leitura_as_regras_escritas_antes():
    assert SN.leitura(_resumos({}))["L-CAMINHO"]["leitura"] == SN.LEITURA_SORTEIO
    tudo_reflexo = {lugar: (0.02, 0.08) for lugar in SN.LUGARES}
    assert SN.leitura(_resumos(tudo_reflexo))["L-CAMINHO"]["leitura"] == SN.LEITURA_REFLEXO
    # um lugar com o limite de cima em 0,10 ou acima tira o "quase tudo reflexo"
    assert SN.leitura(_resumos({**tudo_reflexo, "longe": (0.05, 0.10)}))["L-CAMINHO"]["leitura"] == SN.LEITURA_MISTO
    # o sorteio pede o limite de baixo acima de 0,25 em 2 lugares
    assert SN.leitura(_resumos({"comedouro": (0.20, 0.40), "longe": (0.25, 0.40)}))["L-CAMINHO"]["leitura"] == SN.LEITURA_MISTO
    assert SN.leitura(_resumos({"comedouro": (0.20, 0.40)}))["L-CAMINHO"]["leitura"] == SN.LEITURA_SORTEIO
    lei = SN.leitura(_resumos({}))
    assert lei["L-CAMINHO"]["cortes"] == {"reflexo": 0.10, "sorteio": 0.25, "lugares_sorteio": 2}
    assert len(lei["nao_demonstra"]) == 5
    with pytest.raises(SN.SonoDivergiu, match="sem o IC"):
        SN.leitura(_resumos({"longe": (None, 0.5)}))


def test_config_e_plano():
    SN.conferir_config(CFG)
    SN.exigir_aprovado((RAIZ / SN.PLANO).read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="APROVADO"):
        SN.exigir_aprovado("**Status: PROPOSTO.**")
    with pytest.raises(ValueError, match="a letra"):
        SN.conferir_config({**CFG, "dias": 7})
    with pytest.raises(ValueError, match="sobram"):
        SN.conferir_config({**CFG, "extra": 1})
    with pytest.raises(ValueError, match="processos"):
        SN.rodar(CFG, RAIZ / "nao_existe", 5, Path("nao_existe.tar.gz"))


def test_o_orquestrador_tem_o_nome_que_o_pre_run_reconhece():
    import re
    assert re.fullmatch(r"experiments/run_v[23]_\w+\.py", SN.ORQUESTRADOR)
    assert (RAIZ / SN.ORQUESTRADOR).is_file()
    assert SN.LAMBDA_SONO == LAM and SN.CORTE_CUSTO_H == 2.0


def test_escalares_e_resumo(vida_real):
    cs = json.loads(json.dumps(met.medidas_caminho_sono(vida_real, LAM, PASSO)))
    e = SN.escalares(cs)
    assert e["F_PESOS"] == cs["F_PESOS"] and e["decisoes:REFLEXO"] == cs["decisoes"]["REFLEXO"]
    assert sum(e[f"fracao_decisoes:{c}"] for c in met.CAMINHOS_SONO) == pytest.approx(1.0)
    assert sum(e[f"fracao_ticks_episodio:{c}"] for c in met.CAMINHOS_PESOS) == pytest.approx(cs["F_PESOS"])
    reg = [{"grupo": "run", "braco": "HOJE", "lugar": "longe", "semente": s, "dono": d, "sono": cs}
           for s in (1, 2, 3) for d in ("atencioso", "relapso")]
    r = SN.resumo(reg, "run", "HOJE", "longe")
    assert r["vidas"] == 6 and r["unidades"] == 3
    m = r["medidas"]["F_PESOS"]
    assert m["n"] == 3 and m["media"] == pytest.approx(cs["F_PESOS"])
    assert set(m["por_dono"]) == {"atencioso", "relapso"}
    with pytest.raises(SN.SonoDivergiu, match="nenhuma vida"):
        SN.resumo(reg, "run", "HOJE", "comedouro")
