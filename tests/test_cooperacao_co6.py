"""A CO6 da cooperacao (docs/ESPEC_V3_COOPERACAO_CO6.md): a reputacao e o peso dos deveres na percepcao, sem mudar a decisao.

- o G2: com a CO6 desligada, as vidas do grupo de hoje (o modular nos dois pets, a cooperacao ligada) saem byte a byte contra o gabarito
  gravado antes da mudanca (experiments/exportar_gabarito_co6.py, tests/gabaritos/co6_vidas_de_hoje.json.gz);
- o G-SEM-DECISAO-CO6 (CO6-5): ligada, as decisoes, os logs, o registro e o estado interno (fora a chave `social`) sao os do gabarito;
- o G-RECEPTOR-SOCIAL: a reputacao vem so dos atos testemunhados, e o `k` so dela e da posicao;
- o `k` em casos feitos a mao: o passo, o decaimento e o teto por estagio;
- o gabarito do G-PAR-CO6 (o do TS) refeito sai igual."""
from __future__ import annotations

import gzip
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402
import exportar_gabarito_co6_par as ep  # noqa: E402

from digilab.config import (CONFIG_COOPERACAO, CONFIG_COOPERACAO_CO6, CONFIG_COOPERACAO_LIGADA, CONFIG_MUNDO_MVP,  # noqa: E402
                            CONFIG_PADRAO, PARAMETROS_COOPERACAO, TICKS_POR_DIA, ConfigCooperacao)
from digilab.cooperacao import Cooperacao, decair  # noqa: E402
from digilab.mundo import PercepcaoSocial  # noqa: E402

GABARITO = json.loads(gzip.decompress(e6.ARQUIVO.read_bytes()).decode())
S = CONFIG_COOPERACAO.escala
PERTO = {"A": (0, 0), "B": (10, 0)}
RAIOS = {"A": 96, "B": 96}
CRIANCAS = {"A": TICKS_POR_DIA, "B": TICKS_POR_DIA}
CONSUMO = {"id": 1, "fome_antes": 0.3, "fome_depois": 0.6, "humor_antes": 0.5, "humor_depois": 0.5}


@pytest.mark.parametrize("i", range(len(e6.VIDAS)))
def test_g2_co6_desligada_vidas_de_hoje(i):
    v = e6.VIDAS[i]
    assert GABARITO["vidas"][i]["semente"] == v[0]
    assert json.loads(json.dumps(e6.vida(v), sort_keys=True)) == GABARITO["vidas"][i]


# ------------------------------------------------------------------ a chave
def test_a_chave_desligada_por_padrao_e_so_com_a_cooperacao():
    assert CONFIG_COOPERACAO.co6 is False and CONFIG_COOPERACAO_LIGADA.co6 is False
    with pytest.raises(ValueError, match="co6 so liga"):
        ConfigCooperacao(co6=True)
    with pytest.raises(ValueError, match="k_teto"):
        ConfigCooperacao(ligada=True, co6=True, k_teto_crianca=600)          # acima do adolescente
    with pytest.raises(ValueError, match="k_passo"):
        ConfigCooperacao(ligada=True, co6=True, k_passo=0)
    assert [CONFIG_COOPERACAO.k_teto_bebe, CONFIG_COOPERACAO.k_teto_crianca, CONFIG_COOPERACAO.k_teto_adolescente,
            CONFIG_COOPERACAO.k_teto_adulto] == [0, S // 4, S // 2, 3 * S // 4]
    for nome in ("co6", "k_passo", "k_teto_bebe", "k_teto_crianca", "k_teto_adolescente", "k_teto_adulto"):
        assert nome in PARAMETROS_COOPERACAO
    with pytest.raises(RuntimeError, match="co6"):
        Cooperacao(CONFIG_COOPERACAO_LIGADA).fim_do_tick_k(0, PERTO, RAIOS, CRIANCAS)
    with pytest.raises(RuntimeError, match="co6"):
        Cooperacao(CONFIG_COOPERACAO_LIGADA).peso_dever("A")


# ------------------------------------------------------------------ o k a mao
def _com_reputacao() -> Cooperacao:
    """B deixa a comida para A, que a come no raio: a reputacao de B vista por A fica positiva (a de A vista por B, 0)"""
    c = Cooperacao(CONFIG_COOPERACAO_CO6)
    c.decisao(5, "B", [1], ["A"], 0.6, None, PERTO, RAIOS)
    c.decisao(6, "A", [1], ["B"], 0.3, CONSUMO, PERTO, RAIOS)
    assert c.reputacao("B", "A", 6) > 0 and c.reputacao("A", "B", 6) == 0
    return c


def test_o_k_o_passo_so_com_quem_retribui():
    c = _com_reputacao()
    for t in range(10, 20):
        c.fim_do_tick_k(t, PERTO, RAIOS, CRIANCAS)
    assert c.peso_dever("A") == 10                 # um passo por tick de encontro
    assert c.peso_dever("B") == 0                  # a reputacao de A vista por B e 0: nao e encontro


def test_o_k_um_tem_de_ver_o_outro():
    c = _com_reputacao()
    for t in range(10, 20):
        c.fim_do_tick_k(t, {"A": (0, 0), "B": (100, 0)}, {"A": 96, "B": 120}, CRIANCAS)    # B ve A, A nao ve B
    assert c.peso_dever("A") == 0


def test_o_k_decai_pela_meia_vida_da_pontuacao():
    c = _com_reputacao()
    for t in range(10, 210):
        c.fim_do_tick_k(t, PERTO, RAIOS, CRIANCAS)
    um = 2 ** 16
    assert c._k["A"] == 200 * um
    longe = {"A": (0, 0), "B": (500, 0)}
    for t in range(210, 210 + TICKS_POR_DIA):
        c.fim_do_tick_k(t, longe, RAIOS, CRIANCAS)
    assert c._k["A"] == decair(200 * um, TICKS_POR_DIA, CONFIG_COOPERACAO.k_meia_vida_pontuacao)
    assert 95 <= c.peso_dever("A") <= 105          # um dia: perto da metade


def test_o_teto_por_estagio():
    c = _com_reputacao()
    for t in range(10, 410):
        c.fim_do_tick_k(t, PERTO, RAIOS, {"A": t, "B": t})                           # bebes: o teto 0
    assert c.peso_dever("A") == 0
    for t in range(410, 1010):
        c.fim_do_tick_k(t, PERTO, RAIOS, {"A": TICKS_POR_DIA + t, "B": t})
    assert c.peso_dever("A") == S // 4             # o teto da crianca
    for t in range(1010, 1210):
        c.fim_do_tick_k(t, PERTO, RAIOS, {"A": 3 * TICKS_POR_DIA + t, "B": t})
    assert c.peso_dever("A") == S // 4 + 200       # adolescente: o teto sobe, e o k anda um passo por tick
    assert [c.teto_k(x) for x in (0, TICKS_POR_DIA - 1, TICKS_POR_DIA, 3 * TICKS_POR_DIA, 7 * TICKS_POR_DIA)] == \
        [0, 0, S // 4, S // 2, 3 * S // 4]


def test_a_reputacao_negativa_nao_e_encontro():
    c = Cooperacao(CONFIG_COOPERACAO_CO6)
    c.decisao(360, "B", [2], ["A"], 0.2, None, PERTO, RAIOS)
    c.decisao(360, "A", [2], ["B"], 0.5, {**CONSUMO, "id": 2, "fome_antes": 0.5, "fome_depois": 0.9}, PERTO, RAIOS)
    c.fim_do_tick(360, [{"vencedor": "A", "perdedor": "B", "comida": 2}], [], {"A": "comer", "B": "emburrar"}, PERTO, RAIOS)
    assert c.reputacao("A", "B", 360) < 0
    for t in range(361, 400):
        c.fim_do_tick_k(t, PERTO, RAIOS, CRIANCAS)
    assert c.peso_dever("B") == 0


def test_a_leitura_da_conta_com_memoria_e_a_de_hoje():
    """o atalho da leitura (a conta lembra o ultimo tick lido) da o mesmo valor que decair do ultimo ato"""
    c = _com_reputacao()
    conta = c._reputacao[("B", "A")]
    for t in (7, 100, 100, 3000, 5000):
        assert conta.em(t) == ep_decair_em(conta, t)


def ep_decair_em(conta, tick: int) -> int:
    from digilab.cooperacao import BITS_FRACAO
    from digilab.mundo import div_arred
    return div_arred(decair(conta.bruto, tick - conta.tick, conta.cfg.k_meia_vida_pontuacao), 2 ** BITS_FRACAO)


# ------------------------------------------------------------------ o G-RECEPTOR-SOCIAL
def test_g_receptor_social_so_os_atos_testemunhados():
    """o ato de B fora da vista de A nao entra na reputacao de B vista por A, e o k de A nao anda, mesmo perto depois"""
    c = Cooperacao(CONFIG_COOPERACAO_CO6)
    longe = {"A": (0, 0), "B": (500, 0)}
    c.decisao(5, "B", [1], ["A"], 0.6, None, longe, RAIOS)
    c.decisao(6, "A", [1], ["B"], 0.3, CONSUMO, longe, RAIOS)
    assert c.pontuacao("B", 6) > 0 and c.reputacao("B", "A", 6) == 0
    for t in range(10, 50):
        c.fim_do_tick_k(t, PERTO, RAIOS, CRIANCAS)
    assert c.peso_dever("A") == 0
    # os campos da percepcao: so a memoria do proprio pet (a reputacao) e o proprio k; nenhum le o corpo ou o cerebro do outro
    assert list(PercepcaoSocial.__dataclass_fields__) == ["outros", "onde_comeu", "toque", "sentidos", "reputacao", "peso_dever"]


# ------------------------------------------------------------------ o G-SEM-DECISAO-CO6 e o M-SENS
@pytest.mark.parametrize("i", range(len(e6.VIDAS)))
def test_g_sem_decisao_co6_ligada_e_as_decisoes_de_hoje(i):
    """CO6-5: com a CO6 ligada, as decisoes, os logs, o registro e o estado interno (fora a chave `social`) sao os do gabarito"""
    semente, donos, entrada_b, lugar = e6.VIDAS[i]
    gv = GABARITO["vidas"][i]
    g = e6.grupo(semente, donos, entrada_b, lugar, CONFIG_COOPERACAO_CO6)
    registro = {"cabecalho": g.registro.cabecalho, "eventos": [e.para_dict() for e in g.registro.eventos]}
    assert json.loads(e6._json(registro)) == gv["registro"]
    for p, m in sorted(g.motores.items()):
        assert json.loads(e6._json(e6.decisoes(m.politica))) == gv["pets"][p]["decisoes"]
        assert e6._sha(m.log.para_jsonl()) == gv["pets"][p]["log_sha256"]
        ei = m.politica.estado_interno()
        social = ei.pop("social")
        assert set(social) == {"reputacao", "peso_dever"} and set(social["reputacao"]) == set(g.motores) - {p}
        assert e6._sha(e6._json(ei)) == gv["pets"][p]["estado_interno_sha256"]
    r = json.loads(e6._json(g.coop.resumo(g.ids_presentes(), g.tick)))
    assert set(r.pop("peso_dever")) == set(g.motores)
    assert r == gv["cooperacao"]


def test_o_msens_le_a_ultima_percepcao_e_falha_alto():
    from digilab.digibrain.sens import Sens
    s = Sens(CONFIG_PADRAO, CONFIG_MUNDO_MVP)
    base = PercepcaoSocial((), (), ())
    s._ler_social(base)
    assert s.social is None                                                    # a CO6 desligada: nada
    s._ler_social(replace(base, reputacao=(("B", 12),), peso_dever=40))
    assert s.social == {"reputacao": {"B": 12}, "peso_dever": 40}
    for ruim in (replace(base, reputacao=(("B", 1),)), replace(base, reputacao=(("B", 1),), peso_dever=S + 1),
                 replace(base, reputacao=(("B", 1.0),), peso_dever=1), replace(base, reputacao=(("B", 1), ("B", 2)), peso_dever=1)):
        with pytest.raises(ValueError, match="M-SENS"):
            s._ler_social(ruim)


def test_o_gabarito_do_g_par_co6_e_o_de_hoje():
    """o gabarito do TS (web/app/test/gabaritos/co6_python.json.gz) refeito sai igual; o exportador falha alto se a CO6 mudar uma vida"""
    gravado = json.loads(gzip.decompress(ep.ARQUIVO.read_bytes()).decode())
    assert json.loads(json.dumps(ep.gerar(), sort_keys=True)) == gravado
