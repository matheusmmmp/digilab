"""O G0 da genetica, etapa E1: o registro do genoma (docs/TAREFA_V3_GENOMA_G0.md, secao 3.2).

Ida e volta evento <-> Genoma; as falhas altas; o JSON canonico e o sha256 estavel; nenhum campo do aprendido (EG-5); o `ParametrosInatos` cobre todo
campo dos inatos; a ConfigGenoma desligada; o preflight (so biblioteca padrao, engine.py intacto)."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from dataclasses import FrozenInstanceError, fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab import genoma as gen  # noqa: E402
from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_GENOMA, CONFIG_GENOMA_LIGADO, PARAMETROS_GENOMA,  # noqa: E402
                            ConfigGenoma)
from digilab.digibrain.ganchos import CAMPOS_POR_MODULO, ParametrosInatos  # noqa: E402
from digilab.events import Evento  # noqa: E402
from digilab.genoma import Genoma, GenomaInvalido  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402

CANONICO = ('{"secoes":{"especie":{"forma":"hoje"},"frutas":{"forma":"hoje"},"inatos":{"forma":"hoje"},'
            '"paladar":{"forma":"hoje"},"temperamento":{"forma":"hoje"}},"versao":1}')


def _ev(valor, tick=0, tipo="genoma"):
    return Evento(tick=tick, tipo=tipo, valor=valor)


def _carga(**mudar):
    c = {"versao": 1, "secoes": {s: {"forma": "hoje"} for s in gen.SECOES}}
    c.update(mudar)
    return c


def _ev_carga(c):
    return _ev(json.dumps(c, sort_keys=True, ensure_ascii=True, separators=(",", ":")))


def test_o_genoma_vazio_e_hoje_nas_cinco_secoes():
    g = Genoma()
    assert tuple(g.secoes) == gen.SECOES == ("temperamento", "especie", "frutas", "paladar", "inatos")
    assert set(g.secoes.values()) == {"hoje"}
    with pytest.raises(FrozenInstanceError):
        g.secoes = {}


def test_ida_e_volta_evento_genoma():
    g = Genoma()
    e = g.evento()
    assert (e.tick, e.tipo) == (0, "genoma") and e.valor == CANONICO
    assert Genoma.de_evento(e) == g
    assert Genoma.de_evento(Evento.de_dict(e.para_dict())).evento() == e


def test_o_json_e_canonico_e_o_sha256_e_estavel():
    g = Genoma()
    esperado = json.dumps({"versao": 1, "secoes": {s: {"forma": "hoje"} for s in gen.SECOES}}, sort_keys=True, ensure_ascii=True,
                          separators=(",", ":"))
    assert g.json() == esperado == CANONICO and g.json().isascii()
    assert g.sha256() == hashlib.sha256(CANONICO.encode("ascii")).hexdigest()
    assert g.sha256() == Genoma(dict(reversed(list(g.secoes.items())))).sha256()   # a ordem de entrada nao muda o sha
    assert len(g.sha256()) == 64


def test_o_json_do_evento_tem_de_ser_o_canonico():
    with pytest.raises(GenomaInvalido, match="canonico"):
        Genoma.de_evento(_ev(json.dumps(json.loads(CANONICO), sort_keys=True)))   # com espacos
    with pytest.raises(GenomaInvalido, match="canonico"):
        Genoma.de_evento(_ev(json.dumps({"versao": 1, "secoes": json.loads(CANONICO)["secoes"]}, separators=(",", ":"))))   # fora de ordem


def test_secao_desconhecida_falha_alto():
    c = _carga()
    c["secoes"]["corpo"] = {"forma": "hoje"}
    with pytest.raises(GenomaInvalido, match="desconhecida"):
        Genoma.de_evento(_ev_carga(c))
    with pytest.raises(GenomaInvalido, match="desconhecida"):
        Genoma({**Genoma().secoes, "plasticidade": "hoje"})


def test_secao_faltando_falha_alto():
    c = _carga()
    del c["secoes"]["paladar"]
    with pytest.raises(GenomaInvalido, match="faltando"):
        Genoma.de_evento(_ev_carga(c))
    with pytest.raises(GenomaInvalido, match="faltando"):
        Genoma({})


def test_forma_desconhecida_falha_alto():
    c = _carga()
    c["secoes"]["frutas"] = {"forma": "valores"}   # a forma "valores" e do G1
    with pytest.raises(GenomaInvalido, match="forma desconhecida"):
        Genoma.de_evento(_ev_carga(c))
    with pytest.raises(GenomaInvalido, match="forma desconhecida"):
        Genoma({**Genoma().secoes, "inatos": 3})


def test_campo_a_mais_falha_alto():
    c = _carga()
    c["secoes"]["inatos"] = {"forma": "hoje", "w0": 5}
    with pytest.raises(GenomaInvalido, match="campo"):
        Genoma.de_evento(_ev_carga(c))
    with pytest.raises(GenomaInvalido, match="campos do evento"):
        Genoma.de_evento(_ev_carga(_carga(extra=1)))
    c2 = _carga()
    del c2["secoes"]["inatos"]["forma"]
    with pytest.raises(GenomaInvalido):
        Genoma.de_evento(_ev_carga(c2))


@pytest.mark.parametrize("versao", [1.0, "1", True, None])
def test_valor_nao_inteiro_falha_alto(versao):
    with pytest.raises(GenomaInvalido, match="inteiro"):
        Genoma.de_evento(_ev_carga(_carga(versao=versao)))


def test_versao_desconhecida_e_evento_malformado_falham_alto():
    with pytest.raises(GenomaInvalido, match="versao"):
        Genoma.de_evento(_ev_carga(_carga(versao=2)))
    with pytest.raises(GenomaInvalido):
        Genoma.de_evento(_ev("{nao e json"))
    with pytest.raises(GenomaInvalido):
        Genoma.de_evento(_ev(7))
    with pytest.raises(GenomaInvalido):
        Genoma.de_evento(_ev("[]"))
    with pytest.raises(GenomaInvalido, match="tick 0"):
        Genoma.de_evento(_ev(CANONICO, tick=5))
    with pytest.raises(GenomaInvalido, match="evento"):
        Genoma.de_evento(_ev(CANONICO, tipo="origem"))


def test_nenhum_campo_do_registro_vem_do_aprendido():
    """EG-5: a lista de campos (secoes e a classe) so tem as cinco inatas; nada da politica, da memoria nem do carater"""
    assert {f.name for f in fields(Genoma)} == {"secoes"}
    aprendido = ("politica", "memoria", "carater", "mem", "pers", "plast", "aprendid", "episod", "peso", "habito")
    for nome in gen.SECOES:
        assert not any(a in nome for a in aprendido), nome
    fonte = (RAIZ / "digilab" / "genoma.py").read_text(encoding="utf-8")
    importados = {n.module for n in ast.walk(ast.parse(fonte)) if isinstance(n, ast.ImportFrom)}
    assert importados == {"__future__", "dataclasses", "events"}   # nao importa politica, memoria, motor nem digibrain


def test_o_parametros_inatos_segue_cobrindo_todo_campo_dos_inatos():
    p = ParametrosInatos()   # levanta se um campo ficar fora dos modulos ou repetido
    todos = {f.name for f in fields(CONFIG_DIGIBRAIN_INATOS)}
    assert {c for cs in CAMPOS_POR_MODULO.values() for c in cs} == todos
    assert sum(len(p.do_modulo(m)) for m in CAMPOS_POR_MODULO) == len(todos)
    assert "inatos" in Genoma().secoes   # a secao existe, na forma "hoje" (a config de sempre)


def test_a_config_genoma_e_desligada_com_status_e_fonte():
    assert CONFIG_GENOMA.ligado is False and CONFIG_GENOMA_LIGADO.ligado is True
    with pytest.raises(TypeError):
        ConfigGenoma(ligado=1)
    assert set(PARAMETROS_GENOMA) == {f.name for f in fields(ConfigGenoma)}
    assert all(st in ("PROPOSTO", "DECIDIDO") and fonte for st, fonte in PARAMETROS_GENOMA.values())


def test_o_genoma_nao_toca_o_motor_e_so_usa_a_biblioteca_padrao():
    """o preflight: so a stdlib no pacote (a AST), engine.py intacto, e nenhum arquivo do pacote le a chave ainda"""
    import run_arena
    assert sorted(run_arena._imports_externos(RAIZ / "digilab")) == []
    assert sha256_engine() == ENGINE_SHA256_V0
    for n in ast.walk(ast.parse((RAIZ / "digilab" / "genoma.py").read_text(encoding="utf-8"))):
        if isinstance(n, ast.Import):
            assert all(a.name.split(".")[0] in sys.stdlib_module_names for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.level == 0:
            assert n.module.split(".")[0] in sys.stdlib_module_names
    citam = {p.name for p in (RAIZ / "digilab").rglob("*.py") if "ConfigGenoma" in p.read_text(encoding="utf-8")}
    assert citam == {"config.py"}   # a E2 e a E3 ligam a chave
