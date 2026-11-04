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
    """o preflight: so a stdlib no pacote (a AST), engine.py intacto, e so o config.py e o mundo.py (E2) leem a chave"""
    import run_arena
    assert sorted(run_arena._imports_externos(RAIZ / "digilab")) == []
    assert sha256_engine() == ENGINE_SHA256_V0
    for n in ast.walk(ast.parse((RAIZ / "digilab" / "genoma.py").read_text(encoding="utf-8"))):
        if isinstance(n, ast.Import):
            assert all(a.name.split(".")[0] in sys.stdlib_module_names for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.level == 0:
            assert n.module.split(".")[0] in sys.stdlib_module_names
    citam = {p.name for p in (RAIZ / "digilab").rglob("*.py") if "ConfigGenoma" in p.read_text(encoding="utf-8")}
    assert citam == {"config.py", "mundo.py"}   # a E2 liga a chave no replay do mundo; a E3 liga na bancada


# ============================================================ E2: o replay do mundo (docs/TAREFA_V3_GENOMA_G0.md, secao 3.2; G0-4, G0-5, G0-7)
import gabarito_dois_pets as gdp  # noqa: E402,F401  (tests/ no sys.path abaixo)
import gabarito_genoma_g0 as GAB  # noqa: E402

from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402


@pytest.fixture(scope="module")
def vidas_de_hoje():
    """as 40 vidas da E0, geradas agora com o codigo desta etapa e a chave desligada"""
    return GAB.gerar()


def test_e2_chave_desligada_as_vidas_da_e0_saem_iguais_ao_gabarito_no_log_e_na_trajetoria(vidas_de_hoje):
    gravado = json.loads(GAB.ARQUIVO.read_text(encoding="utf-8"))
    assert set(vidas_de_hoje) == set(gravado) and len(gravado) == 40
    for chave, v in gravado.items():
        assert vidas_de_hoje[chave]["log"] == v["log"], chave
        assert vidas_de_hoje[chave]["trajetoria"] == v["trajetoria"], chave
        assert vidas_de_hoje[chave]["partes"] == v["partes"], chave


@pytest.fixture(scope="module", params=[("padrao", "perto", 101), ("afastado", "longe", 202)], ids=lambda p: f"{p[0]}-{p[1]}-{p[2]}")
def vida_a(request):
    layout, lugar, s = request.param
    fp, fm = gdp.fabricas_diretas(layout, "quimica", "lobos")
    dono = gdp.DonoComBolaPerto(gdp.DonoComLugar(gdp.criar_dono("atencioso"), lugar, s, "atencioso", gdp.LAYOUTS[layout]))
    v = gdp.simular_vida_mundo("atencioso", dono, fp(gdp.CONFIG_PADRAO), s, GAB.DIAS_A, 16 * GAB.DIAS_A, fm, rotulo_dono="atencioso")
    return v.motor, fp, fm, s


def _refazer(motor, fp, fm, s, eventos, **kw):
    return reproduzir_mundo(LogDeEventos(eventos), fp, CONFIG_PADRAO, s, fabrica_motor=fm, **kw)


def _com_genoma(motor):
    return [Genoma().evento()] + list(motor.log)


def test_e2_chave_ligada_genoma_vazio_a_trajetoria_sai_igual_e_o_log_ganha_o_genoma_na_frente(vida_a):
    motor, fp, fm, s = vida_a
    sem = _refazer(motor, fp, fm, s, list(motor.log))
    com = _refazer(motor, fp, fm, s, _com_genoma(motor), cfg_genoma=CONFIG_GENOMA_LIGADO)
    assert GAB.impressao(sem, [])["partes"] == GAB.impressao(com, [])["partes"]
    assert sem.log.para_jsonl() == motor.log.para_jsonl()                   # o replay de hoje refaz o log de hoje
    linhas = com.log.para_jsonl().splitlines()
    assert linhas[1:] == motor.log.para_jsonl().splitlines()                # o log e o de hoje...
    assert linhas[0] == LogDeEventos([Genoma().evento()]).para_jsonl().splitlines()[0]   # ...com o genoma na frente


def test_e2_replay_do_log_com_genoma_refeito_da_a_mesma_vida(vida_a):
    motor, fp, fm, s = vida_a
    com = _refazer(motor, fp, fm, s, _com_genoma(motor), cfg_genoma=CONFIG_GENOMA_LIGADO)
    de_novo = _refazer(motor, fp, fm, s, list(LogDeEventos.de_jsonl(com.log.para_jsonl())), cfg_genoma=CONFIG_GENOMA_LIGADO)
    assert de_novo.log.para_jsonl() == com.log.para_jsonl()
    assert GAB.impressao(de_novo, []) == GAB.impressao(com, [])
    assert repr(de_novo._estado) == repr(motor._estado)


def test_e2_ate_tick_com_genoma_para_antes_do_primeiro_avanco(vida_a):
    motor, fp, fm, s = vida_a
    r = _refazer(motor, fp, fm, s, _com_genoma(motor), cfg_genoma=CONFIG_GENOMA_LIGADO, ate_tick=5)
    base = _refazer(motor, fp, fm, s, list(motor.log), ate_tick=5)
    assert GAB.impressao(r, [])["partes"] == GAB.impressao(base, [])["partes"]


def test_e2_o_genoma_com_a_chave_desligada_falha(vida_a):
    motor, fp, fm, s = vida_a
    with pytest.raises(ValueError, match="genoma"):
        _refazer(motor, fp, fm, s, _com_genoma(motor))
    with pytest.raises(ValueError, match="genoma"):
        _refazer(motor, fp, fm, s, _com_genoma(motor), cfg_genoma=CONFIG_GENOMA)


def test_e2_o_genoma_fora_da_primeira_posicao_falha(vida_a):
    motor, fp, fm, s = vida_a
    ev = list(motor.log)
    with pytest.raises(ValueError, match="primeiro"):
        _refazer(motor, fp, fm, s, [ev[0], Genoma().evento()] + ev[1:], cfg_genoma=CONFIG_GENOMA_LIGADO)
    with pytest.raises(ValueError, match="primeiro"):
        _refazer(motor, fp, fm, s, ev + [Genoma().evento()], cfg_genoma=CONFIG_GENOMA_LIGADO)


def test_e2_dois_genomas_no_mesmo_log_falham(vida_a):
    motor, fp, fm, s = vida_a
    g = Genoma().evento()
    with pytest.raises(ValueError, match="primeiro"):
        _refazer(motor, fp, fm, s, [g, g] + list(motor.log), cfg_genoma=CONFIG_GENOMA_LIGADO)


def test_e2_genoma_malformado_falha_alto_no_replay(vida_vazia=None):
    fp, fm = gdp.fabricas_diretas("padrao", "quimica", "lobos")
    ruim = Evento(tick=0, tipo="genoma", valor='{"versao":1}')
    with pytest.raises(GenomaInvalido):
        reproduzir_mundo(LogDeEventos([ruim]), fp, CONFIG_PADRAO, 101, fabrica_motor=fm, cfg_genoma=CONFIG_GENOMA_LIGADO)


def test_e2_o_genoma_em_outros_replays_falha_g0_7():
    """a educacao, as frutas, o ambiente e o motor base seguem sem o evento (G0-7): nele o genoma falha alto"""
    from digilab import ambiente, educacao, frutas
    from digilab.engine import reproduzir
    log = LogDeEventos([Genoma().evento()])
    fp = lambda cfg=None: gdp.PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    for fn in (educacao.reproduzir_educacao, frutas.reproduzir_frutas, ambiente.reproduzir_ambiente):
        with pytest.raises(ValueError):
            fn(log, fp, CONFIG_PADRAO, 101)
    with pytest.raises(ValueError):
        reproduzir(log, fp, CONFIG_PADRAO, 101)
