"""Extrator da historia do pet (digilab/historia.py; DESIGN_VOZ_PROPRIA, secao 2): uma regra por teste, em
registros montados a mao, e o mesmo registro da os mesmos fatos."""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import CONFIG_HISTORIA, CONFIG_LESOES_LIGADA, TICKS_POR_DIA  # noqa: E402
from digilab.historia import (FatoHistoria, HistoriaInvalida, RegistroVida, extrair, fabrica_com_captura, ids,  # noqa: E402
                              periodo_do_tick, registro_de_motor, selecionar)
from digilab.protocol import validar_parametros_historia  # noqa: E402

D = TICKS_POR_DIA
H = 60


def _regras(fatos, tipo=None):
    return [(f.regra, f.texto) for f in fatos if tipo is None or f.tipo == tipo]


def test_parametros_registrados():
    validar_parametros_historia()


def test_periodo_do_tick():
    assert [periodo_do_tick(h * H) for h in (0, 5, 6, 11, 12, 17, 18, 23)] == [
        "madrugada", "madrugada", "manha", "manha", "tarde", "tarde", "noite", "noite"]
    assert periodo_do_tick(D + 7 * H) == "manha"


# ------------------------------------------------------------ H
def test_sequencia_a_depois_b():
    # 12 vezes: come e dorme 10 min depois; brinca sozinho no meio do dia (base rara de dormir)
    acoes = []
    for k in range(12):
        t = k * 4 * H
        acoes += [(t, "comer"), (t + 10, "dormir"), (t + 2 * H, "brincar"), (t + 3 * H, "ocioso")]
    fatos = extrair(RegistroVida(tick_final=48 * H, acoes_pet=tuple(acoes)))
    assert ("sequencia", "quase sempre durmo depois de comer") in _regras(fatos, "H")


def test_sequencia_precisa_de_ocorrencias_e_de_lift():
    poucas = [(k * 4 * H + d, a) for k in range(9) for d, a in ((0, "comer"), (10, "dormir"))]
    assert not [f for f in extrair(RegistroVida(tick_final=40 * H, acoes_pet=tuple(poucas))) if f.regra == "sequencia"]
    # dormir em toda janela de 30 min (depois de qualquer acao): lift ~1, nao e habito de ninguem
    ciclo = ("comer", "dormir", "brincar", "dormir")
    tudo = [(10 * k, ciclo[k % 4]) for k in range(80)]
    fatos = extrair(RegistroVida(tick_final=900, acoes_pet=tuple(tudo)))
    assert not [f for f in fatos if f.regra == "sequencia" and f.dados["b"] == "dormir"]


def test_acao_repetida_conta_uma_vez():
    acoes = tuple((t, "comer") for t in range(0, 30 * 15, 15))        # 30 decisoes seguidas comendo = 1 episodio
    assert not [f for f in extrair(RegistroVida(tick_final=500, acoes_pet=acoes)) if f.tipo == "H"]


def test_habito_por_periodo():
    # chama atencao a noite (20 h) todo dia, e explora uma vez por periodo
    acoes = []
    for d in range(12):
        acoes += [(d * D + 20 * H, "chamar_atencao"), (d * D + 21 * H, "ocioso")]
        acoes += [(d * D + h * H + m, a) for h in (2, 8, 14) for m, a in ((0, "explorar"), (30, "ocioso"))]
    acoes.sort()
    fatos = extrair(RegistroVida(tick_final=12 * D, acoes_pet=tuple(acoes)))
    assert ("periodo", "à noite eu chamo você mais") in _regras(fatos, "H")
    assert not [f for f in fatos if f.regra == "periodo" and f.dados["acao"] == "explorar"]


# ------------------------------------------------------------ O
def test_dono_periodo_e_cuidado():
    acoes = tuple((d * D + 8 * H + k, "acariciar" if k % 2 else "alimentar") for d in range(4) for k in range(3))
    fatos = extrair(RegistroVida(tick_final=4 * D, acoes_dono=acoes))
    regras = _regras(fatos, "O")
    assert ("periodo_dono", "você costuma aparecer de manhã") in regras
    assert ("cuidado_dono", "o que você mais faz é me dar comida") in regras
    # so 2 dias: o periodo nao conta
    dois = tuple(x for x in acoes if x[0] < 2 * D)
    assert not [f for f in extrair(RegistroVida(tick_final=2 * D, acoes_dono=dois)) if f.regra == "periodo_dono"]


def _janela(tipo, inicio, fim, desfecho, falso=False):
    return {"tipo": tipo, "pedido": "fome", "inicio": inicio, "prazo": inicio + 15, "falso": falso,
            "desfecho": desfecho, "fim": fim}


def test_dono_cede_a_manha_e_demora():
    cede = [_janela("chamado", k * H, k * H + 3, "cedido", True) for k in range(4)]
    bronca = [_janela("chamado", 10 * H, 10 * H + 3, "corrigido", True)]
    fatos = extrair(RegistroVida(tick_final=D, janelas=tuple(cede + bronca)))
    assert ("cede_manha", "quando faço manha, você cede com petisco") in _regras(fatos, "O")
    assert ("demora", "você atende meus chamados rápido") not in _regras(fatos)       # manha nao e chamado real
    rapidos = [_janela("aviso", k * H, k * H + 2, "atendido") for k in range(5)]
    assert ("demora", "você atende meus chamados rápido") in _regras(extrair(RegistroVida(D, janelas=tuple(rapidos))))
    lentos = [_janela("chamado", k * H, k * H + 15, "ignorado") for k in range(5)]
    assert ("demora", "você demora para atender meus chamados") in _regras(extrair(RegistroVida(D, janelas=tuple(lentos))))
    medios = [_janela("aviso", k * H, k * H + 8, "atendido") for k in range(5)]
    assert not [f for f in extrair(RegistroVida(D, janelas=tuple(medios))) if f.regra == "demora"]


# ------------------------------------------------------------ P
def test_gosto_desgosto_treino_e_revanche():
    r = RegistroVida(
        tick_final=D, desvio_por_acao=(("brincar", 0.05), ("emburrar", -0.04), ("ocioso", 0.9), ("comer", 0.0)),
        sessoes_treino=tuple((k, "esquiva" if k < 5 else "corrida") for k in range(8)),
        lutas=({"tick": 10, "rival": "sparring:brigao@brasa", "resultado": "derrota", "lesao": False},
               {"tick": 20, "rival": "sparring:brigao@brasa", "resultado": "vitoria", "lesao": False},
               {"tick": 30, "rival": "npc:tier2_sentinela", "resultado": "derrota", "lesao": False}))
    regras = _regras(extrair(r), "P")
    assert ("gosto", "gosto de brincar") in regras and ("desgosto", "não curto emburrar") in regras
    assert ("treino_favorito", "meu treino favorito é esquiva") in regras
    assert ("revanche", "quero revanche contra o sentinela") in regras
    fraco = replace(r, desvio_por_acao=(("brincar", 0.01), ("emburrar", -0.01)), sessoes_treino=r.sessoes_treino[:5],
                    lutas=r.lutas[:2])
    assert _regras(extrair(fraco), "P") == []


# ------------------------------------------------------------ L
def test_marcos():
    lutas = tuple({"tick": 2 * D + k, "rival": "npc:tier1_brutamontes", "resultado": res, "lesao": les}
                  for k, (res, les) in enumerate((("derrota", True), ("derrota", False), ("derrota", False),
                                                  ("vitoria", False))))
    r = RegistroVida(tick_final=4 * D, evolucoes=((180, "crianca"), (D + 900, "adolescente")),
                     acoes_dono=((10, "alimentar"), (2 * D + 100, "tratar_lesao"), (2 * D + 200, "alimentar")),
                     lutas=lutas, sombria_tick=3 * D, filho_de_cruzamento=True)
    textos = [f.texto for f in extrair(r) if f.tipo == "L"]
    for t in ("virei Rookie no dia 1", "virei Champion no dia 2", "perdi minha primeira luta no dia 3",
              "venci minha primeira luta no dia 3", "perdi para o brutamontes 3 vezes antes de vencer",
              "me machuquei no dia 3 e você me tratou", "virei uma forma sombria",
              "nasci de um cruzamento de dois pets"):
        assert t in textos, t
    ausencias = [f for f in extrair(r) if f.regra == "ausencia"]
    assert [(f.dados["inicio"], f.dados["horas"]) for f in ausencias] == [(10, 49), (2 * D + 200, 44)]


# ------------------------------------------------------------ selecao, ids e determinismo
def test_selecao_ordem_limite_por_regra_e_recentes():
    fatos = [FatoHistoria("O", "demora", "O:demora", "você demora para atender meus chamados", 0),
             FatoHistoria("P", "gosto", "P:gosto:brincar", "gosto de brincar", 0)]
    fatos += [FatoHistoria("L", "ausencia", f"L:ausencia:{k}", f"você sumiu por 7 h no dia {k}", k * D) for k in range(5)]
    fatos += [FatoHistoria("H", "sequencia", "H:seq:comer:dormir", "quase sempre durmo depois de comer", 0)]
    s = selecionar(fatos)
    assert [f.tipo for f in s] == ["L", "L", "H", "P", "O"]
    assert [f.tick for f in s[:2]] == [4 * D, 3 * D]                        # os mais recentes, so 2 da regra
    s2 = selecionar(fatos, citados_recentes=[["H:seq:comer:dormir"]])
    assert s2[-1].chave == "H:seq:comer:dormir"
    velho = [["H:seq:comer:dormir"]] + [[]] * CONFIG_HISTORIA.falas_recentes
    assert selecionar(fatos, citados_recentes=velho) == s                     # citado ha mais de 5 falas: volta
    assert [i for i, _ in ids(s)] == ["L1", "L2", "H1", "P1", "O1"]


def test_texto_fora_do_molde_falha():
    with pytest.raises(HistoriaInvalida):
        FatoHistoria("L", "x", "k", "a" * 81, 0)
    with pytest.raises(HistoriaInvalida):
        FatoHistoria("L", "x", "k", "tem [colchete]", 0)
    with pytest.raises(HistoriaInvalida):
        FatoHistoria("X", "x", "k", "ok", 0)


def test_registro_ate_corta_o_futuro():
    r = RegistroVida(tick_final=4 * D, evolucoes=((180, "crianca"), (D + 900, "adolescente")),
                     acoes_dono=((10, "alimentar"), (3 * D, "alimentar")))
    antes = r.ate(D)
    assert antes.evolucoes == ((180, "crianca"),) and antes.acoes_dono == ((10, "alimentar"),)
    assert "virei Champion no dia 2" not in [f.texto for f in extrair(antes)]


@pytest.fixture(scope="module")
def vida_real():
    from digilab.donos_educacao import simular_vida_educacao
    from digilab.educacao import reproduzir_educacao
    from digilab.evolucao import ovo
    from digilab.temperamento import sortear
    from run_educacao import _fabricas, rival_por_nome, ticks_sparring
    s, b = 69001, "permissivo"
    esp, t_ovo = ovo(s)
    tmp = sortear(s)
    fp, _, _, pet = _fabricas(b, s, esp, tmp, t_ovo)
    v = simular_vida_educacao(b, s, 3, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=ticks_sparring(b),
                              rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome)

    def rejogar(capturar):
        fp2, _, fm2, _ = _fabricas(b, s, esp, tmp, t_ovo)
        acoes = []
        fm = fabrica_com_captura(fm2, acoes) if capturar else fm2
        return reproduzir_educacao(v.motor.log, fp2, semente=s, fabrica_motor=fm), acoes
    return v, rejogar


def test_captura_so_observa_e_mesmo_registro_mesmos_fatos(vida_real):
    v, rejogar = vida_real
    sem, _ = rejogar(False)
    com, acoes = rejogar(True)
    assert com.estado() == sem.estado() == v.motor.estado() and com.historico_janelas == sem.historico_janelas
    assert acoes and all(isinstance(t, int) and isinstance(a, str) for t, a in acoes)
    com2, acoes2 = rejogar(True)
    r1, r2 = registro_de_motor(com, acoes), registro_de_motor(com2, acoes2)
    assert r1 == r2
    f1, f2 = extrair(r1), extrair(r2)
    assert [f.para_dict() for f in f1] == [f.para_dict() for f in f2] and f1
