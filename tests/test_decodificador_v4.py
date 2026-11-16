"""O decodificador `dec-v4` (a fala do assistir, docs/futuro/fala_do_assistir.md, FA-2 a FA-6, DECIDIDAS pelo Matheus em 2026-11-12): a
config calibrada, o formato, as regras dos quatro conceitos, a falha alta, que so le, que o conceito se refaz do log do pet pelo replay
(FA-6), que a calibracao e a do disco e que o gabarito da web esta em dia. O dec-v1 e o dec-v2 seguem no test_decodificador.py."""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import sys
from dataclasses import asdict, fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_decodificador_v4 as ex  # noqa: E402
import exportar_gabarito_digibrain_modular as lm  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_gosto_visual as G  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402

from digilab.config import CONFIG_FALA_ASSISTIR, PARAMETROS_FALA_ASSISTIR, ConfigFalaAssistir  # noqa: E402
from digilab.digibrain.decodificador import (CATALOGO, CATALOGO_ASSISTIR, VERSAO_V4, conceitos_assistir, decodificar,  # noqa: E402
                                             decodificar_v4)
from digilab.events import LogDeEventos  # noqa: E402
from digilab.genoma_visao import genoma_visao  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402

S = 1024
PASTA_LIMIARES = RAIZ / "artifacts_v3_gosto_visual" / "fala_limiares"


def _viver(semente: int, dono: str, dias: int = 2):
    unidade = {"semente": semente, "genoma": semente}
    motor, fab, _ = G.viver("proprio", dono, unidade, dias, enjoo=True)
    return motor, fab


@pytest.fixture(scope="module")
def vida():
    motor, fab = _viver(101, "agitado")
    return motor, fab, [json.loads(json.dumps(m)) for m in sd.cerebro_da_copia(motor).motivos]


@pytest.fixture(scope="module")
def olhando(vida):
    ms = vida[2]
    pares = [(ms[k - 1], m) for k, m in enumerate(ms) if k and m["olhar"]["olhava"] is not None]
    assert pares
    return pares


def test_a_config_tem_status_e_fonte_e_e_a_calibrada():
    assert set(PARAMETROS_FALA_ASSISTIR) == {f.name for f in fields(ConfigFalaAssistir)}
    assert all(st == "PROPOSTO" and fonte for st, fonte in PARAMETROS_FALA_ASSISTIR.values())
    lim = json.loads((PASTA_LIMIARES / "limiares.json").read_text(encoding="utf-8"))
    assert lim["config_em_digilab_igual"] and lim["config_fala_assistir"] == asdict(CONFIG_FALA_ASSISTIR)
    assert all(getattr(CONFIG_FALA_ASSISTIR, n) == v for n, v in lim["limiares"].items())
    assert lim["entrada_sha256"] == hashlib.sha256((PASTA_LIMIARES / "sinais.json.gz").read_bytes()).hexdigest()
    for ruim in ({"gostei_agrado": 0}, {"chato_tedio": S}, {"intervalo_susto_s": 301}, {"intervalo_susto_s": 0}, {"limiar_ativo": -1}):
        with pytest.raises(ValueError):
            ConfigFalaAssistir(**ruim)


def test_a_calibracao_sai_do_disco_igual(tmp_path, monkeypatch):
    """o calibrar.py, rodado de novo sobre o sinais.json.gz do disco, da o limiares.json do disco (byte a byte)"""
    sys.path.insert(0, str(PASTA_LIMIARES))
    import calibrar
    monkeypatch.setattr(calibrar, "SAIDA", tmp_path / "limiares.json")
    calibrar.main()
    assert (tmp_path / "limiares.json").read_bytes() == (PASTA_LIMIARES / "limiares.json").read_bytes()


def test_o_formato_e_o_assistir_so_enquanto_olha(vida):
    ms = vida[2]
    n_olha = 0
    for k, m in enumerate(ms):
        r = decodificar_v4(m, ms[k - 1] if k else None)
        assert set(r) == {"versao", "k", "intencao", "conceitos", "assistir"} and r["versao"] == VERSAO_V4 == "dec-v4"
        assert [c["nome"] for c in r["conceitos"]] == list(CATALOGO)
        a = r["assistir"]
        if m["olhar"]["olhava"] is None:
            assert a is None
            continue
        n_olha += 1
        assert a["olhava"] == m["olhar"]["olhava"] and [c["nome"] for c in a["conceitos"]] == list(CATALOGO_ASSISTIR)
        for c in a["conceitos"]:
            assert type(c["valor"]) is int and 0 <= c["valor"] <= S and type(c["confianca"]) is int and 0 <= c["confianca"] <= S
        ativos = [c for c in a["conceitos"] if c["valor"] >= CONFIG_FALA_ASSISTIR.limiar_ativo]
        assert (a["intencao"] is None) == (not ativos)
        if a["intencao"] is not None:
            assert a["intencao"] in [c["nome"] for c in ativos]
    assert n_olha > 0


def test_os_12_conceitos_sao_os_do_dec_v1_quando_nao_ha_unidade_de_olhar(vida):
    """o olhar no catalogo nao muda conta nenhuma: sem unidade de olhar no motivo, os 12 conceitos sao os do dec-v1"""
    ms, n = vida[2], 0
    for k, m in enumerate(ms):
        if any(u["chave"][0] == "olhar" for u in m["unidades"]):
            with pytest.raises(ValueError, match="comportamento desconhecido"):
                decodificar(m)
            continue
        n += 1
        v1, v4 = decodificar(m), decodificar_v4(m, ms[k - 1] if k else None)
        assert v4["conceitos"] == v1["conceitos"] and v4["intencao"] == v1["intencao"]
    assert n > 0


def _troca(m, ant, **s):
    m, ant = copy.deepcopy(m), copy.deepcopy(ant)
    o, u = m["olhar"], m["afeto"]["urgencias"]
    for c in ("agrado", "agrado_efetivo", "enjoo"):
        if c in s:
            o[c] = s[c]
    for c in ("tedio", "susto"):
        if c in s:
            u[c] = s[c]
    if "susto_anterior" in s:
        ant["afeto"]["urgencias"]["susto"] = s["susto_anterior"]
    m["gestos"] = [["tapa", 0]] if s.get("tapa") else []
    return m, ant


def _ca(m, ant, cfg, **s):
    return conceitos_assistir(*_troca(m, ant, **s), cfg)


def _valor(a, nome):
    return next(c["valor"] for c in a["conceitos"] if c["nome"] == nome)


def test_as_regras_dos_quatro_conceitos(olhando):
    ant, m = olhando[0]
    cfg, h = CONFIG_FALA_ASSISTIR, CONFIG_FALA_ASSISTIR.limiar_ativo
    neutro = dict(agrado=512, agrado_efetivo=512, enjoo=cfg.o_que_e_enjoo + 1, tedio=0, susto=0, susto_anterior=0)
    assert _ca(m, ant, CONFIG_FALA_ASSISTIR, **neutro)["intencao"] is None
    # gostei: o agrado efetivo no limiar e ativo; um abaixo, nao
    a = _ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "agrado_efetivo": cfg.gostei_agrado})
    assert _valor(a, "gostei") == h and a["intencao"] == "gostei"
    assert _valor(_ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "agrado_efetivo": cfg.gostei_agrado - 1}), "gostei") < h
    # susto: a subida desde a decisao anterior; o tapa zera; o susto vence os outros
    a = _ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "susto": 100 + cfg.susto_subida, "susto_anterior": 100, "agrado_efetivo": S})
    assert a["intencao"] == "susto" and _valor(a, "gostei") == S
    assert _valor(_ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "susto": 900, "susto_anterior": 0, "tapa": True}), "susto") == 0
    assert _valor(_ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "susto": 50, "susto_anterior": 900}), "susto") == 0
    # chato: o enjoo E o tedio
    assert _ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "enjoo": cfg.chato_enjoo, "tedio": cfg.chato_tedio})["intencao"] == "chato"
    assert _valor(_ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "enjoo": S, "tedio": cfg.chato_tedio - 1}), "chato") < h
    # o_que_e: o agrado sem o enjoo baixo E o enjoo baixo (o agrado efetivo nao entra)
    a = _ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "agrado": cfg.o_que_e_agrado, "enjoo": cfg.o_que_e_enjoo})
    assert a["intencao"] == "o_que_e"
    assert _valor(_ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "agrado": 0, "enjoo": cfg.o_que_e_enjoo + 1}), "o_que_e") < h
    # a confianca: 0 no limiar, S nas pontas
    a = _ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "agrado_efetivo": cfg.gostei_agrado})
    assert next(c["confianca"] for c in a["conceitos"] if c["nome"] == "gostei") == 0
    a = _ca(m, ant, CONFIG_FALA_ASSISTIR, **{**neutro, "agrado_efetivo": S})
    assert next(c["confianca"] for c in a["conceitos"] if c["nome"] == "gostei") == S
    # a config muda o limiar
    a = _ca(m, ant, replace(cfg, gostei_agrado=600), **{**neutro, "agrado_efetivo": 600})
    assert a["intencao"] == "gostei"


def test_falha_alto(vida, olhando):
    ant, m = olhando[0]
    with pytest.raises(ValueError, match="pede o motivo com o olhar"):
        decodificar_v4({k: v for k, v in m.items() if k != "olhar"}, ant)
    sem = copy.deepcopy(m); del sem["olhar"]["enjoo"]
    with pytest.raises(ValueError, match="olhar com o enjoo"):
        decodificar_v4(sem, ant)
    nulo = copy.deepcopy(m); nulo["olhar"]["agrado_efetivo"] = None
    with pytest.raises(ValueError, match="agrado efetivo"):
        decodificar_v4(nulo, ant)
    with pytest.raises(ValueError, match="pede o motivo anterior"):
        decodificar_v4(m, None)
    with pytest.raises(ValueError, match="motivo anterior e o da decisao"):
        decodificar_v4(m, vida[2][0] if m["k"] != 1 else vida[2][2])
    with gzip.open(lm.PASTA / f"{lm.PREFIXO}{lm.LUGARES[0]}.json.gz", "rt", encoding="utf-8") as f:
        m_lm0 = json.load(f)["vidas"][0]["decisoes"][0]["motivo"]
    with pytest.raises(ValueError, match="pede o motivo com o olhar"):
        decodificar_v4(m_lm0, None)


def test_so_le(vida):
    ms = vida[2]
    for k, m in enumerate(ms[:300]):
        antes = copy.deepcopy(m)
        r = decodificar_v4(m, ms[k - 1] if k else None)
        assert m == antes
        assert decodificar_v4({x: y for x, y in m.items() if x != "consequencia"}, ms[k - 1] if k else None) == r


def test_o_conceito_se_refaz_do_log_do_pet_pelo_replay(vida):
    """FA-6: as linhas do log de apresentacao (o conceito, a confianca, o tick e as versoes de cada decisao com intencao do assistir) saem
    iguais do replay do log do pet gravado em disco; o texto da fala nunca entra no registro do pet"""
    motor, fab, ms = vida
    linhas = []
    for k, m in enumerate(ms):
        a = decodificar_v4(m, ms[k - 1] if k else None)["assistir"]
        if a is not None and a["intencao"] is not None:
            c = next(x for x in a["conceitos"] if x["nome"] == a["intencao"])
            linhas.append({"k": k, "conceito": c["nome"], "valor": c["valor"], "confianca": c["confianca"], "versao_dec": VERSAO_V4})
    texto = motor.log.para_jsonl()
    r = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fab[0], semente=101, fabrica_motor=fab[1])
    ms2 = [json.loads(json.dumps(m)) for m in sd.cerebro_da_copia(r).motivos]
    assert ms2 == ms
    for l in linhas:
        a = decodificar_v4(ms2[l["k"]], ms2[l["k"] - 1] if l["k"] else None)["assistir"]
        c = next(x for x in a["conceitos"] if x["nome"] == l["conceito"])
        assert a["intencao"] == l["conceito"] and (c["valor"], c["confianca"]) == (l["valor"], l["confianca"])
    assert "fala" not in texto and "assistir" not in texto


def test_o_gabarito_da_web_esta_em_dia():
    em_disco = gzip.decompress(ex.ARQUIVO.read_bytes())
    assert hashlib.sha256(em_disco).hexdigest() == hashlib.sha256(gzip.decompress(ex.bytes_do_arquivo())).hexdigest()


def test_nenhum_modulo_da_vida_chama_o_dec_v4():
    citam = {p.name for p in (RAIZ / "digilab").rglob("*.py") if "decodificar_v4" in p.read_text(encoding="utf-8")
             or "conceitos_assistir" in p.read_text(encoding="utf-8")}
    assert citam == {"decodificador.py"}
    assert orq is not None and genoma_visao is not None
