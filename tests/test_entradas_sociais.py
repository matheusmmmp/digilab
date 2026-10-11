"""Dois pets, etapa 4, segunda metade (docs/TAREFA_V2_DOIS_PETS.md; docs/futuro/dois_pets.md, secao 8, DP-8): as entradas sociais do
cerebro A nas regras de tempo livre, com prior 0, e o modelo dos outros, so registrado.

- G2: com as chaves e sem o grupo (ou com um pet so nele), a vida de hoje: as entradas sao zero e nada aprende delas;
- no prior, o P0 com lobos e o instinto do mundo byte a byte, tambem com o outro a vista (com o alvo aprendido e as duas chaves);
- G1: o replay do registro do grupo refaz os cerebros bit a bit (os pesos sociais e o modelo dos outros incluidos);
- a conta exata: o termo social no peso efetivo e um passo da regra da L1 nos pesos sociais;
- o modelo dos outros nao muda a decisao (a vida com e sem ele e a mesma), e as contas dele saem certas (em casos montados e numa vida,
  contra o registro do motor);
- os pesos: 951 sem o alvo aprendido e 987 com ele (degrau 1 sem o corpo, PDP-1); com o corpo passa de mil e falha alto.
Sementes: so as dos testes (101, 202, 303).
"""
from __future__ import annotations

import ast
import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_dois_pets as gdp  # noqa: E402
from test_grupo import CM, DIAS, fabricas  # noqa: E402
from test_grupo_social import _pet_com, _texto  # noqa: E402
from digilab.config import CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, TICKS_POR_DIA, ConfigLobos  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.grupo import RegistroGrupo, reproduzir_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motivo import _motivo_lobos_decisao  # noqa: E402
from digilab.mundo import TIPOS_TOQUE, PercepcaoMundo, PercepcaoSocial  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import (ACOES_VISIVEIS, ENTRADAS_SOCIAIS, PARAMETROS_LOBOS, ModeloOutros, PoliticaLobos, div_arred,  # noqa: E402
                                    entradas_sociais)

S = CONFIG_LOBOS.escala
CHAVES = dict(entradas_sociais=True, modelo_outros=True)
CL_P0 = replace(CONFIG_LOBOS, alvo_aprendido=True, **CHAVES)
CL_P1 = replace(CONFIG_LOBOS_APRENDIZ, alvo_aprendido=True, **CHAVES)


def fp(cl):
    return lambda c=None: PoliticaLobos(c or CONFIG_PADRAO, cl, cfg_mundo=CM)  # noqa: E731


def inst(c=None):
    return PoliticaInstintoMundo(c or CONFIG_PADRAO)


def _cerebro(g, i):
    return g.motores[i].politica._pm


def _sem_politica(r: dict) -> dict:
    for i in r["pets"]:
        r["pets"][i].pop("politica")
    return r


# ================================================================== config, registro e contagem
def test_os_parametros_novos_estao_no_registro():
    for nome in ("entradas_sociais", "modelo_outros", "janela_social_ticks", "fator_familiaridade"):
        assert PARAMETROS_LOBOS[nome][0] == "PROPOSTO"
    assert {f.name for f in fields(ConfigLobos)} <= set(PARAMETROS_LOBOS) | {"escala"}
    assert CONFIG_LOBOS.entradas_sociais is False and CONFIG_LOBOS.modelo_outros is False


def test_as_entradas_e_os_tipos_do_toque():
    assert tuple(TIPOS_TOQUE) == lobos.TIPOS_TOQUE_SOCIAL
    assert ACOES_VISIVEIS == tuple(a.value for a in AcaoPet) and len(ACOES_VISIVEIS) == 8
    assert len(ENTRADAS_SOCIAIS) == 2 + 8 + 5 and len(set(ENTRADAS_SOCIAIS)) == len(ENTRADAS_SOCIAIS)


def test_os_pesos_abaixo_de_mil_sem_o_corpo():
    base = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM).n_pesos()
    so_social = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, entradas_sociais=True), cfg_mundo=CM)
    assert base == 756 and so_social.n_pesos() == 951
    linhas = {r: sorted(a.value for a in t) for r, t in so_social._pesos_social.items()}
    assert linhas == {"tempo_livre": ["brincar", "chamar_atencao", "explorar", "ocioso"],
                      "bola_no_cenario": ["brincar", "chamar_atencao", "explorar", "ocioso"],
                      "fruta_no_cenario": ["brincar", "chamar_atencao", "comer", "explorar", "ocioso"]}
    assert PoliticaLobos(CONFIG_PADRAO, CL_P1, cfg_mundo=CM).n_pesos() == 987
    # o modelo dos outros nao tem peso
    assert PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, modelo_outros=True), cfg_mundo=CM).n_pesos() == base


def test_com_o_corpo_passa_de_mil_e_falha_alto():
    cc = gdp.CORPOS["drives"]
    with pytest.raises(ValueError, match="teto"):
        PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, entradas_sociais=True), cfg_mundo=CM, cfg_corpo=cc)


def test_as_chaves_falham_alto():
    for k in ("entradas_sociais", "modelo_outros"):
        with pytest.raises(ValueError, match="mundo fisico"):
            PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, **{k: True}))
        with pytest.raises(TypeError):
            PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, **{k: 1}), cfg_mundo=CM)
    for k, v in (("janela_social_ticks", 0), ("fator_familiaridade", 0), ("fator_familiaridade", S + 1), ("janela_social_ticks", 2.0)):
        with pytest.raises(ValueError):
            PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, **{k: v}), cfg_mundo=CM)


# ================================================================== as entradas
def _x(social, janela=240) -> dict:
    return dict(zip(ENTRADAS_SOCIAIS, entradas_sociais(social, janela)))


def test_sem_o_campo_social_tudo_zero():
    assert set(_x(None).values()) == {0.0}
    assert set(_x(PercepcaoSocial((), (), ())).values()) == {0.0}


def test_a_visao_a_acao_do_mais_perto():
    p = PercepcaoSocial((("B", 3, 4, 5, "comer"), ("C", 10, 0, 10, "brincar")), (), ())
    x = _x(p)
    assert x["outro_a_vista"] == 1.0 and x["acao_comer"] == 1.0
    assert sum(v for k, v in x.items() if k.startswith("acao_")) == 1.0 and x["viu_comer"] == 0.0
    with pytest.raises(ValueError):
        _x(PercepcaoSocial((("B", 0, 0, 0, "voar"),), (), ()))


def test_viu_comer_so_o_recente():
    assert _x(PercepcaoSocial((), (("B", 10, 10, 240),), ()))["viu_comer"] == 1.0
    assert _x(PercepcaoSocial((), (("B", 10, 10, 241),), ()))["viu_comer"] == 0.0
    assert _x(PercepcaoSocial((), (("B", 10, 10, 241),), ()), janela=300)["viu_comer"] == 1.0
    assert _x(PercepcaoSocial((), (("B", 10, 10, 241),), ()))["outro_a_vista"] == 0.0    # a memoria nao e a visao
    with pytest.raises(ValueError):
        _x(PercepcaoSocial((), (("B", 1, 1, -1),), ()))


def test_o_toque_o_mais_recente_na_janela():
    p = PercepcaoSocial((), (), (("B", "esbarrou", 3, 30), ("C", "disputa_perdeu", 0, 15)))
    x = _x(p)
    assert x["toque_disputa_perdeu"] == 1.0 and sum(v for k, v in x.items() if k.startswith("toque_")) == 1.0
    assert set(_x(PercepcaoSocial((), (), (("B", "encostou", 1, 241),))).values()) == {0.0}
    empate = _x(PercepcaoSocial((), (), (("B", "encostaram", 1, 15), ("C", "esbarrou", 2, 15))))
    assert empate["toque_encostaram"] == 1.0                                        # empate de idade: o menor id
    with pytest.raises(ValueError):
        _x(PercepcaoSocial((), (), (("B", "abraco", 1, 0),)))


# ================================================================== G2: sem o outro, a vida de hoje
@pytest.mark.parametrize("cl_com,cl_sem", [(CL_P0, replace(CONFIG_LOBOS, alvo_aprendido=True)),
                                           (CL_P1, replace(CONFIG_LOBOS_APRENDIZ, alvo_aprendido=True)),
                                           (replace(CONFIG_LOBOS_APRENDIZ, **CHAVES), CONFIG_LOBOS_APRENDIZ)])
def test_g2_sem_o_outro_a_vida_de_hoje(cl_com, cl_sem):
    """com as chaves e um pet so no grupo: a mesma vida (log, estado, acoes, rngs, mundo) e os mesmos pesos de sempre; os sociais zero"""
    for s in (101, 202):
        gs = [simular_grupo(CM, s, [_pet_com("A", 0, s, fp(cl), lugar="comedouro")], DIAS) for cl in (cl_com, cl_sem)]
        assert _texto(_sem_politica(gs[0].resumo())) == _texto(_sem_politica(gs[1].resumo()))
        e_com, e_sem = (_cerebro(g, "A").estado_interno() for g in gs)
        for chave in ("pesos", "pesos_alvo_mundo"):
            assert e_com.get(chave) == e_sem.get(chave)
        assert all(w == 0 for t in e_com["pesos_social"].values() for v in t.values() for w in v)
        assert e_com["modelo_outros"]["outros"] == {}
        assert all(set(m["percepcao_social"].values()) == {0.0} for m in e_com["motivos"])


# ================================================================== no prior, o instinto do mundo com o outro a vista
@pytest.mark.parametrize("s", [101, 202])
def test_no_prior_o_p0_com_as_chaves_e_o_instinto_do_mundo_com_o_outro_a_vista(s):
    rs = []
    for f in (fp(CL_P0), inst):
        g = simular_grupo(CM, s, [_pet_com("A", 0, s, f, lugar="comedouro"), _pet_com("B", 0, s, inst)], DIAS)
        rs.append(_texto(_sem_politica(g.resumo())))
    assert rs[0] == rs[1]
    m = _cerebro(simular_grupo(CM, s, [_pet_com("A", 0, s, fp(CL_P0), lugar="comedouro"), _pet_com("B", 0, s, inst)], DIAS), "A")
    assert any(v["percepcao_social"]["outro_a_vista"] == 1.0 for v in m.motivos)        # o outro estava a vista
    assert any(v["percepcao_social"]["viu_comer"] == 1.0 for v in m.motivos)


# ================================================================== G1
@pytest.mark.parametrize("entrada_b", [0, TICKS_POR_DIA])
def test_g1_o_replay_refaz_os_cerebros(entrada_b):
    _, fm = fabricas("instinto")
    pets = [_pet_com("A", 0, 202, fp(CL_P1), lugar="comedouro"), _pet_com("B", entrada_b, 202, fp(CL_P1), lugar="perto")]
    g = simular_grupo(CM, 202, pets, DIAS)
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(g.registro.para_jsonl()), {"A": (fp(CL_P1), fm), "B": (fp(CL_P1), fm)}, CM)
    assert _texto(r.resumo()) == _texto(g.resumo())
    for i in "AB":
        assert _texto(_cerebro(r, i).estado_interno()) == _texto(_cerebro(g, i).estado_interno())
    # no grupo o modelo conhece o outro e, com os dois juntos desde o comeco, os pesos sociais aprendem
    e = _cerebro(g, "A").estado_interno()
    assert set(e["modelo_outros"]["outros"]) == {"B"}
    if entrada_b == 0:
        assert any(w != 0 for t in e["pesos_social"].values() for v in t.values() for w in v)


# ================================================================== a conta exata
def test_o_termo_social_no_peso_efetivo():
    c = PoliticaLobos(CONFIG_PADRAO, CL_P1, cfg_mundo=CM)
    x = [1.0] + [0.0] * 11
    c._x_social = [0.0] * len(ENTRADAS_SOCIAIS)
    _, antes = c._pesos_efetivos("tempo_livre", (AcaoPet.OCIOSO, AcaoPet.EXPLORAR), x)
    j = ENTRADAS_SOCIAIS.index("acao_comer")
    c._pesos_social["tempo_livre"][AcaoPet.EXPLORAR][j] = 512
    c._x_social[j] = 1.0
    contrib, depois = c._pesos_efetivos("tempo_livre", (AcaoPet.OCIOSO, AcaoPet.EXPLORAR), x)
    assert depois[AcaoPet.EXPLORAR] - antes[AcaoPet.EXPLORAR] == 0.5 and depois[AcaoPet.OCIOSO] == antes[AcaoPet.OCIOSO]
    with pytest.raises(RuntimeError, match="sem linha"):
        c._pesos_efetivos("tempo_livre", (AcaoPet.OCIOSO, AcaoPet.DORMIR), x)


def test_um_passo_da_regra_nos_pesos_sociais():
    c = PoliticaLobos(CONFIG_PADRAO, CL_P1, cfg_mundo=CM)
    cand = (AcaoPet.OCIOSO, AcaoPet.EXPLORAR)
    jv, jt = ENTRADAS_SOCIAIS.index("outro_a_vista"), ENTRADAS_SOCIAIS.index("toque_esbarrou")
    xs = [0] * len(ENTRADAS_SOCIAIS)
    xs[jv], xs[jt] = S, S
    reg = {"regra": "tempo_livre", "candidatos": cand, "acao": AcaoPet.EXPLORAR, "X": [S] + [0] * 11,
           "P": {AcaoPet.OCIOSO: 700, AcaoPet.EXPLORAR: 324}, "W": {AcaoPet.OCIOSO: 3000, AcaoPet.EXPLORAR: 1400},
           "social": {"X": xs}}
    f, passo = 1024, c.cl.passo
    c._aplicar_sinal(reg, f)
    t = c._pesos_social["tempo_livre"]
    esperado_e = div_arred(f * passo * S * (S - 324), S * S * 1400)
    esperado_o = div_arred(f * passo * S * (0 - 700), S * S * 3000)
    for j in range(len(ENTRADAS_SOCIAIS)):
        assert t[AcaoPet.EXPLORAR][j] == (esperado_e if j in (jv, jt) else 0)
        assert t[AcaoPet.OCIOSO][j] == (esperado_o if j in (jv, jt) else 0)
    assert esperado_e > 0 > esperado_o
    assert all(w == 0 for a in (AcaoPet.BRINCAR, AcaoPet.CHAMAR_ATENCAO) for w in t[a])


# ================================================================== o modelo dos outros nao muda a decisao
@pytest.mark.parametrize("s", [101, 202, 303])
def test_o_modelo_dos_outros_nao_muda_a_decisao(s):
    sem = replace(CL_P1, modelo_outros=False)
    gs = [simular_grupo(CM, s, [_pet_com("A", 0, s, fp(cl), lugar="comedouro"), _pet_com("B", 0, s, fp(cl))], DIAS)
          for cl in (CL_P1, sem)]
    assert _texto(_sem_politica(gs[0].resumo())) == _texto(_sem_politica(gs[1].resumo()))
    for i in "AB":
        e_com, e_sem = (_cerebro(g, i).estado_interno() for g in gs)
        assert "modelo_outros" in e_com and "modelo_outros" not in e_sem
        e_com.pop("modelo_outros")
        assert _texto(e_com) == _texto(e_sem)


def test_a_decisao_nao_le_o_modelo():
    """pela AST: o modelo so aparece no agir (a atualizacao, antes de decidir), no consequencia_mundo, no __init__ e na serializacao"""
    arvore = ast.parse((RAIZ / "digilab" / "policies" / "lobos.py").read_text(encoding="utf-8"))
    leitores = set()
    for f in ast.walk(arvore):
        if isinstance(f, ast.FunctionDef):
            if any(isinstance(n, ast.Attribute) and n.attr == "_modelo" for n in ast.walk(f)):
                leitores.add(f.name)
    assert leitores == {"__init__", "agir", "consequencia_mundo", "estado_interno"}


# ================================================================== as contas do modelo
def _soc(outros=(), comeu=(), toque=()):
    return PercepcaoSocial(tuple(outros), tuple(comeu), tuple(toque))


def _hora(t):
    return (t % TICKS_POR_DIA) / TICKS_POR_DIA


def test_a_familiaridade_e_a_media_movel_do_tempo_a_vista():
    m = ModeloOutros(S, 16)
    f, t = 0, 0
    for k, visto in enumerate([1, 1, 1, 0, 0, 1] * 50):
        m.decisao(_soc(outros=[("B", 1, 1, 1, "ocioso")] if visto else []) if (visto or k) else None, _hora(t))
        f += div_arred(((S if visto else 0) - f) * 16, S)
        t += 15
        assert m.outros["B"]["familiaridade"] == f
    assert 0 < f < S


def test_a_afinidade_divididas_e_perdidas():
    m = ModeloOutros(S, 16)
    vazio = {"comeu": None, "alvo": None, "chegou": None}
    m.decisao(_soc(comeu=[("B", 5, 5, 3)]), _hora(15))           # viu o B comer, mas o pet nao comeu: nada
    m.consequencia({**vazio, "comeu": {"id": 1}}, None, None)     # o pet comeu
    m.decisao(_soc(comeu=[("B", 5, 5, 18)]), _hora(30))           # o mesmo consumo, visto de novo: nao e novo
    assert m.outros["B"]["afinidade"] == {"divididas": 0, "perdidas": 0}
    m.consequencia({**vazio, "comeu": {"id": 2}}, None, None)
    m.decisao(_soc(comeu=[("B", 7, 7, 4)]), _hora(45))            # comeram os dois no mesmo intervalo: dividida
    assert m.outros["B"]["afinidade"]["divididas"] == 1
    m.consequencia({**vazio, "comeu": {"id": 3}}, None, None)
    m.decisao(_soc(comeu=[("B", 9, 9, 2)], toque=[("B", "disputa_perdeu", 0, 2)]), _hora(60))   # perdeu a comida para ele
    assert m.outros["B"]["afinidade"] == {"divididas": 1, "perdidas": 1}
    m.decisao(_soc(toque=[("B", "disputa_perdeu", 0, 17)]), _hora(75))                         # o mesmo toque: uma vez so
    assert m.para_dict()["outros"]["B"]["afinidade"] == {"divididas": 1, "perdidas": 1, "saldo": 0}


def _mundo_com(*tipos):
    return type("O", (), {"mundo": PercepcaoMundo(0, 0, 0, tuple((k, t, 0, 0, 0) for k, t in enumerate(tipos)), 0, 0, None)})()


def test_a_confianca_as_idas_a_onde_comeu():
    m = ModeloOutros(S, 16)
    soc = _soc(comeu=[("B", 40, 50, 30)])
    ida = {"comeu": None, "chegou": False, "alvo": {"tipo": "onde_comeu", "x": 40, "y": 50, "de": None}}
    cont = {"comeu": None, "chegou": True, "alvo": {"tipo": "continuar", "x": 40, "y": 50, "de": "onde_comeu"}}
    m.consequencia(ida, _mundo_com(), soc)                        # nao chegou ainda: nada conta
    m.consequencia(cont, _mundo_com("a_podre", "bola"), soc)      # chegou, sem comida boa: ida sem acerto
    assert m.outros["B"]["confianca"]["comida"] == {"idas": 1, "acertos": 0}
    m.consequencia({**ida, "chegou": True}, _mundo_com("racao"), soc)                         # chegou e viu comida boa
    m.consequencia({**ida, "chegou": True, "comeu": {"id": 9}}, _mundo_com(), soc)            # chegou e comeu
    assert m.para_dict()["outros"]["B"]["confianca"]["comida"] == {"idas": 3, "acertos": 2, "fracao": div_arred(2 * S, 3)}
    with pytest.raises(RuntimeError, match="sem a ida"):
        m.consequencia(cont, _mundo_com(), soc)                    # a ida ja fechou
    with pytest.raises(RuntimeError, match="um outro so"):
        m.consequencia(ida, _mundo_com(), _soc(comeu=[("B", 1, 1, 0)]))


@pytest.mark.parametrize("s", [101, 202, 303])
def test_o_modelo_numa_vida_bate_com_o_registro_do_motor(s):
    """as idas e os acertos do cerebro sao as idas que chegaram no registro do motor; a familiaridade refeita da percepcao"""
    g = simular_grupo(CM, s, [_pet_com("A", 0, s, fp(CL_P1), lugar="comedouro"), _pet_com("B", 0, s, fp(CL_P1))], DIAS)
    for i, o in (("A", "B"), ("B", "A")):
        c = _cerebro(g, i)
        mo = c.estado_interno()["modelo_outros"]["outros"][o]
        idas = [d for d in g.motores[i].idas_onde_comeu if d["chegou"]]
        assert mo["confianca"]["comida"]["idas"] == len(idas)
        assert mo["confianca"]["comida"]["acertos"] == sum(1 for d in idas if d["comeu"] or d["boas_a_vista"])
        f = 0
        for v in c.motivos:
            f += div_arred(((S if v["percepcao_social"]["outro_a_vista"] else 0) - f) * 16, S)
        assert mo["familiaridade"] == f


# ================================================================== o motivo
def test_o_motivo_falha_alto_com_o_termo_social_aprendido():
    reg = {"acao": "ocioso", "candidatos": ["ocioso", "explorar"], "regra": "tempo_livre", "u": 0.99,
           "contribuicoes": {"impulsos": {"ocioso": 3.0, "explorar": 0.1}},
           "aprendido": {"ocioso": [0.0] * 10, "explorar": [0.0] * 10},
           "aprendido_social": {"ocioso": [0.25] + [0.0] * 14, "explorar": [0.0] * 15},
           "percepcao": dict(zip(lobos.ENTRADAS, [1.0] + [0.5] * 9))}
    with pytest.raises(NotImplementedError, match="sociais"):
        _motivo_lobos_decisao(reg, 0, None)
    reg["aprendido_social"] = {"ocioso": [0.0] * 15, "explorar": [0.0] * 15}
    _motivo_lobos_decisao(reg, 0, None)                            # zerado, o motivo sai como sempre
