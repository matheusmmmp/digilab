"""SOCIAL_PAR M2, a companhia no corpo (docs/ESPEC_SOCIAL_PAR_M2.md, secao 5): a `ConfigCompanhia`.

O G2 (desligada, as vidas de hoje byte a byte contra tests/gabaritos/social_m2_de_hoje.json, gravado num commit proprio antes do codigo), o
G2b (ligada com o pet sozinho), o emissor, o corte, a contagem, a falta da solidao, a entrega, o laco entre os corpos, o replay, o
determinismo e a companhia com o M1 (o corpo da decisao seguinte, D-SP-68)."""
from __future__ import annotations

import ast
import inspect
import json
import sys
import textwrap
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_social_m2 as gab  # noqa: E402
from digilab.config import (CONFIG_COMPANHIA, CONFIG_COMPANHIA_LIGADA, CONFIG_CORPO_DRIVES, CONFIG_CORPO_LIGADA, CONFIG_MUNDO_LIGADA,
                            CONFIG_PADRAO, PARAMETROS_COMPANHIA, ConfigCompanhia)
from digilab.corpo import Corpo
from digilab.grupo import Grupo, reproduzir_grupo, sementes_do_grupo
from digilab.state import Estado

GABARITO = json.loads((RAIZ / "tests" / "gabaritos" / "social_m2_de_hoje.json").read_text(encoding="utf-8"))
COMP = {"cfg_companhia": CONFIG_COMPANHIA_LIGADA}
M1 = {"unidades_sociais": True}


# ================================================================== a config
def test_config_padrao_e_numeros_com_status():
    assert CONFIG_COMPANHIA.ligada is False
    assert (CONFIG_COMPANHIA_LIGADA.raio_celulas, CONFIG_COMPANHIA_LIGADA.alivio_solidao) == (1, 900)
    assert set(PARAMETROS_COMPANHIA) == {"ligada", "raio_celulas", "alivio_solidao"}
    assert all(s in ("PROPOSTO", "DECIDIDO") and f for s, f in PARAMETROS_COMPANHIA.values())


@pytest.mark.parametrize("kw", [{"ligada": 1}, {"raio_celulas": -1}, {"alivio_solidao": 0}])
def test_config_invalida_levanta(kw):
    with pytest.raises((TypeError, ValueError)):
        ConfigCompanhia(**kw)


# ================================================================== o G2 e o G2b
def test_g2_desligada_as_vidas_de_hoje_byte_a_byte():
    assert gab.gerar() == GABARITO


@pytest.mark.parametrize("semente", gab.SEMENTES)
def test_g2b_sozinho_ligada_sai_igual(semente):
    assert gab.impressao_sozinho(semente, None, COMP) == GABARITO[f"sozinho|{semente}"]


# ================================================================== o emissor (3.2)
def _corpo(ccp=CONFIG_COMPANHIA_LIGADA, cc=CONFIG_CORPO_DRIVES):
    return Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=True, cfg_companhia=ccp)


def _solidao_depois(companhia: int, dormindo: bool = False, q0: int = 100000, ccp=CONFIG_COMPANHIA_LIGADA) -> int:
    c = _corpo(ccp)
    c.q["solidao"] = q0
    c.passo(Estado(dormindo=dormindo), companhia=companhia)
    return c.q["solidao"]


def test_emissor_acordado_em_contato_tira_o_alivio_uma_vez():
    hoje = _solidao_depois(0)
    assert _solidao_depois(1) == hoje - CONFIG_COMPANHIA_LIGADA.alivio_solidao
    assert _solidao_depois(2) == _solidao_depois(1)              # M2-4: dois ou mais, o mesmo alivio


def test_emissor_dormindo_nada():
    assert _solidao_depois(1, dormindo=True) == _solidao_depois(0, dormindo=True)


def test_corte_em_zero():
    assert _solidao_depois(1, q0=10) == 0


def test_o_emissor_no_grafo_nao_le_quimico():
    e = _corpo().grafo.emissor("companhia")
    assert (e.gatilho, e.fase, e.le, e.efeitos) == ("companhia", 1, (), (("solidao", -900),))
    assert "companhia" not in {x.nome for x in _corpo(CONFIG_COMPANHIA).grafo.emissores}


def test_desligada_companhia_no_tick_levanta():
    with pytest.raises(ValueError, match="sem a ConfigCompanhia ligada"):
        _solidao_depois(1, ccp=CONFIG_COMPANHIA)


def test_sem_a_solidao_falha_alto():
    with pytest.raises(ValueError, match="solidao"):
        _corpo(cc=CONFIG_CORPO_LIGADA)


def test_motor_sem_os_drives_novos_falha_alto():
    _, fm = gab.fabricas(101, None, COMP)
    from digilab.motor_corpo import com_corpo
    from digilab.mundo import MotorMundo
    from digilab.temperamento import NEUTRO
    with pytest.raises(ValueError, match="ConfigCompanhia.ligada sem o corpo"):
        com_corpo(MotorMundo)(None, CONFIG_PADRAO, 101, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=CONFIG_MUNDO_LIGADA,
                              cfg_corpo=CONFIG_CORPO_LIGADA, cfg_companhia=CONFIG_COMPANHIA_LIGADA)


# ================================================================== a contagem (3.1)
def _grupo_falso(posicoes: dict, ccp=CONFIG_COMPANHIA_LIGADA):
    """um Grupo so com o que a contagem le: o mundo (a geometria) e os motores com a posicao e a config (sem corpo nenhum)"""
    g = Grupo.__new__(Grupo)
    g.mundo = SimpleNamespace(cmf=CONFIG_MUNDO_LIGADA)
    g.motores = {i: SimpleNamespace(pet=p, ccp=ccp, _companhia=None) for i, p in posicoes.items()}
    return g


def _celula(cx, cy):
    s = CONFIG_MUNDO_LIGADA.sub
    return (cx * s + s // 2, cy * s + s // 2)


@pytest.mark.parametrize("b, esperado", [((10, 10), 1), ((11, 11), 1), ((12, 10), 0), ((10, 13), 0)])
def test_contagem_pelo_contato(b, esperado):
    g = _grupo_falso({"A": _celula(10, 10), "B": _celula(*b)})
    g._contar_companhia(["A", "B"])
    assert g.motores["A"]._companhia == g.motores["B"]._companhia == esperado


def test_contagem_nao_depende_da_ordem():
    pos = {"A": _celula(10, 10), "B": _celula(11, 10), "C": _celula(30, 30)}
    a, b = _grupo_falso(pos), _grupo_falso(pos)
    a._contar_companhia(["A", "B", "C"])
    b._contar_companhia(["C", "B", "A"])
    assert {i: m._companhia for i, m in a.motores.items()} == {i: m._companhia for i, m in b.motores.items()} == {"A": 1, "B": 1, "C": 0}


# ================================================================== o laco entre os corpos (4)
def test_laco_o_grupo_so_le_a_posicao_e_a_config():
    """pela AST, a contagem so le `pet` e `ccp` dos motores; o teste de cima ja roda com motores sem corpo nenhum"""
    arvore = ast.parse(textwrap.dedent(inspect.getsource(Grupo._contar_companhia)))
    lidos = {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Subscript)}
    assert lidos <= {"pet", "ccp", "_companhia"}
    nomes = {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute)} | {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    assert "corpo" not in nomes and "q" not in nomes


# ================================================================== a entrega e as vidas
def test_entrega_fora_do_grupo_e_tick_sem_entrega_levantam():
    motor, _ = gab.vida_sozinho(101, None, COMP)
    motor._companhia = 1
    with pytest.raises(RuntimeError, match="fora do grupo"):
        motor._companhia_do_tick()
    motor._companhia, motor._grupo = None, object()
    with pytest.raises(RuntimeError, match="sem a contagem"):
        motor._companhia_do_tick()


def test_pets_do_grupo_com_configs_diferentes_levantam():
    ss = sementes_do_grupo(101, ("A", "B"))
    g = Grupo(gab.a0.CM, 101, cfg_cooperacao=gab.a0.CCO)
    fp, fm = gab.fabricas(ss["A"], None, COMP)
    g.entrar("A", fp(), fm, "digibrain", "atencioso")
    fp, fm = gab.fabricas(ss["B"])
    with pytest.raises(ValueError, match="ConfigCompanhia diferente"):
        g.entrar("B", fp(), fm, "digibrain", "atencioso")


@pytest.fixture(scope="module")
def entrada_comp():
    return gab.vida_entrada(101, None, COMP)


def test_companhia_muda_a_vida_do_grupo_so_depois_do_contato(entrada_comp):
    """o grupo com a companhia: a solidao dos dois difere da de hoje, e o registro difere (a companhia age)"""
    assert gab.impressao_grupo(entrada_comp) != GABARITO["entrada|101"]


def test_replay_do_grupo_com_a_companhia(entrada_comp):
    ss = sementes_do_grupo(101, ("A", "B"))
    fab = {i: gab.fabricas(ss[i], None, COMP) for i in ("A", "B")}
    r = reproduzir_grupo(entrada_comp.registro, fab, gab.a0.CM, cfg_cooperacao=gab.a0.CCO)
    assert r.registro.para_jsonl() == entrada_comp.registro.para_jsonl()
    assert {i: gab._texto(m.estado()) for i, m in r.motores.items()} == {i: gab._texto(m.estado()) for i, m in entrada_comp.motores.items()}


def test_determinismo_com_a_companhia(entrada_comp):
    assert gab.impressao_grupo(gab.vida_entrada(101, None, COMP)) == gab.impressao_grupo(entrada_comp)


# ================================================================== com o M1 (D-SP-68)
def _desfecho_seguir_solidao(motor_extra):
    v = gab.vida_par("B1", 101, M1, motor_extra)
    out = {}
    for i, m in sorted(v.grupo.motores.items()):
        pl = m.politica.m.plast
        out[i] = pl.desfecho["seguir"][pl.receptores.index("solidao")]
    return out


def test_com_o_m1_o_desfecho_do_seguir_na_solidao_cai():
    """o receptor da solidao le a falta: sem a companhia, o intervalo do `seguir` sobe a solidao (o desfecho >= 0); com ela, a solidao cai
    perto do outro, e o desfecho fica negativo nos dois pets (o P1 le o corpo da decisao seguinte, D-SP-68)"""
    sem, com = _desfecho_seguir_solidao(None), _desfecho_seguir_solidao(COMP)
    assert all(v >= 0 for v in sem.values())
    assert all(v < 0 for v in com.values())
