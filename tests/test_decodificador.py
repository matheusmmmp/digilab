"""O decodificador de conceitos `dec-v1` (DC1, docs/research/ESPEC_DECODIFICADOR_FALA.md): a config, o formato fixo, a fidelidade minima as sondas,
que so le (a vida de hoje sai byte a byte) e que o gabarito de paridade da web esta em dia."""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_decodificador as ex  # noqa: E402
import exportar_gabarito_digibrain_modular as lm  # noqa: E402

from digilab.config import CONFIG_DECODIFICADOR, PARAMETROS_DECODIFICADOR, ConfigDecodificador  # noqa: E402
from digilab.digibrain.decodificador import CATALOGO, decodificar  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402

S = 1024


@pytest.fixture(scope="module")
def motivos() -> list[dict]:
    """os motivos das oito vidas curtas do braco REL (gabarito da LM0, sementes dos testes)"""
    out = []
    for lugar in lm.LUGARES:
        with gzip.open(lm.PASTA / f"{lm.PREFIXO}{lugar}.json.gz", "rt", encoding="utf-8") as f:
            for v in json.load(f)["vidas"]:
                out += [d["motivo"] for d in v["decisoes"]]
    return out


def test_a_config_tem_status_e_fonte_em_cada_campo():
    assert set(PARAMETROS_DECODIFICADOR) == {f.name for f in fields(ConfigDecodificador)}
    assert all(st in ("PROPOSTO", "DECIDIDO") and fonte for st, fonte in PARAMETROS_DECODIFICADOR.values())
    assert CONFIG_DECODIFICADOR.piso_sonda > CONFIG_DECODIFICADOR.limiar_valor
    with pytest.raises(ValueError):
        ConfigDecodificador(piso_sonda=100)
    with pytest.raises(ValueError):
        ConfigDecodificador(ganho_v=-1)


def test_o_formato_fixo_da_espec(motivos):
    assert len(motivos) > 3000
    for m in motivos:
        r = decodificar(m)
        assert set(r) == {"versao", "k", "intencao", "conceitos"} and r["versao"] == "dec-v1" and r["k"] == m["k"]
        assert [c["nome"] for c in r["conceitos"]] == list(CATALOGO) and r["intencao"] in CATALOGO
        for c in r["conceitos"]:
            assert set(c) <= {"nome", "valor", "confianca", "alvo"}
            assert type(c["valor"]) is int and 0 <= c["valor"] <= S and type(c["confianca"]) is int and 0 <= c["confianca"] <= S
            assert isinstance(c.get("alvo", ""), str)


def test_a_lembranca_so_e_a_intencao_quando_a_sonda_decidiu(motivos):
    decidiu = 0
    for m in motivos:
        r = decodificar(m)
        l = next(c for c in r["conceitos"] if c["nome"] == "lembranca")
        if m["sondas"]["lembranca_decidiu"]:
            decidiu += 1
            assert r["intencao"] == "lembranca" and l["valor"] >= CONFIG_DECODIFICADOR.limiar_valor
        else:
            assert r["intencao"] != "lembranca"
    assert decidiu > 0


def test_a_determinacao_acompanha_a_sonda_da_persistencia(motivos):
    decidiu = sem_i = 0
    com, sem = [], []
    for m in motivos:
        d = next(c for c in decodificar(m)["conceitos"] if c["nome"] == "determinacao")["valor"]
        if m["sondas"]["persistencia_decidiu"]:
            decidiu += 1
            assert d >= CONFIG_DECODIFICADOR.limiar_valor
            com.append(d)
        elif m["estado"]["I"] is None:
            sem_i += 1
            assert d == 0
        else:
            sem.append(d)
    assert decidiu > 0 and sem_i > 0 and sem
    assert sum(com) / len(com) > sum(sem) / len(sem)


def test_so_le_e_nao_depende_do_consequencia(motivos):
    for m in motivos[:600]:
        antes = copy.deepcopy(m)
        r = decodificar(m)
        assert m == antes
        sem = {k: v for k, v in m.items() if k != "consequencia"}
        assert decodificar(sem) == r


def test_falha_alto_em_receptor_comportamento_e_sonda_desconhecidos(motivos):
    base = motivos[40]
    a = copy.deepcopy(base); a["afeto"]["urgencias"]["ciume"] = 1
    with pytest.raises(ValueError, match="receptor desconhecido"):
        decodificar(a)
    b = copy.deepcopy(base); b["unidades"][0]["chave"][0] = "voar"
    with pytest.raises(ValueError, match="comportamento desconhecido"):
        decodificar(b)
    c = copy.deepcopy(base); c["sondas"]["magia_decidiu"] = True
    with pytest.raises(ValueError, match="sonda desconhecida"):
        decodificar(c)
    d = copy.deepcopy(base); del d["sondas"]["habito_decidiu"]
    with pytest.raises(ValueError, match="nao tem a sonda"):
        decodificar(d)


def test_o_gabarito_da_web_esta_em_dia():
    """o arquivo no disco e o que o exportador gera hoje (o texto, sem o gzip)"""
    em_disco = gzip.decompress(ex.ARQUIVO.read_bytes())
    assert hashlib.sha256(em_disco).hexdigest() == hashlib.sha256(gzip.decompress(ex.bytes_do_arquivo())).hexdigest()


def test_o_decodificador_nao_toca_o_motor_e_so_usa_a_biblioteca_padrao():
    """o preflight: so a stdlib no pacote (a AST) e engine.py intacto; os gabaritos das vidas de hoje nao mudam (conferidos pelos testes do modular)"""
    import ast
    import run_arena
    assert sorted(run_arena._imports_externos(RAIZ / "digilab")) == []
    assert sha256_engine() == ENGINE_SHA256_V0
    for n in ast.walk(ast.parse((RAIZ / "digilab" / "digibrain" / "decodificador.py").read_text(encoding="utf-8"))):
        if isinstance(n, ast.Import):
            assert all(a.name.split(".")[0] in sys.stdlib_module_names for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.level == 0:
            assert n.module.split(".")[0] in sys.stdlib_module_names
    citam = {p.name for p in (RAIZ / "digilab").rglob("*.py") if "decodificar" in p.read_text(encoding="utf-8")}
    assert citam == {"decodificador.py"}   # nenhum modulo da vida chama o decodificador
