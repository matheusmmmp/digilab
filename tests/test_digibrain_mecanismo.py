"""Os testes de mecanismo do DigiBrain modular, etapa 1a (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 10; o G-MECANISMO do
docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secao 5.2): cada um com a resposta conhecida, calculada a mao a partir dos
parametros de partida (CONFIG_DIGIBRAIN_INATOS, PROPOSTOS). A lista: T-SENS-1 a 3, T-AFETO-1 a 3, T-ESTADO-1 e 2, T-IMPULSO-1 e 2,
T-MEM-1 a 4, T-ARB-1 e 2, T-PLAST-1 a 3, T-ADAPT-1 e 2, T-MOTIVO-1 e T-CADEIA-0 a 2. O T-MEM-1 no replay e o G1 ficam em
tests/test_digibrain_vidas.py, com os T-PONTO."""
from __future__ import annotations

import math
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CARACTERISTICAS_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MODELO_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_MUNDO_LIGADA, CONFIG_PADRAO)
from digilab.digibrain import DigiBrain, Intencao  # noqa: E402
from digilab.digibrain._comum import chave_unidade, ganho_de_tau, integrar, mul  # noqa: E402
from digilab.digibrain.afeto import Afeto, canais_do_sinal  # noqa: E402
from digilab.digibrain.arb import Arbitragem, sortear_inteiro  # noqa: E402
from digilab.digibrain.estado import EstadoDinamico  # noqa: E402
from digilab.digibrain.mem import Memoria  # noqa: E402
from digilab.digibrain.plast import Plasticidade  # noqa: E402
from digilab.digibrain.sens import Sens  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.modelo_mundo import ModeloMundo  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.mundo import Alvo, PercepcaoMundo  # noqa: E402
from digilab.policies.lobos import div_arred, impulsos, sinal_corpo, sinal_corpo_canais, valor_previsto  # noqa: E402
from digilab.policy import Observacao, Politica, PoliticaInstinto, Transicao  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
CM = CONFIG_MUNDO_LIGADA
R = CM.raio_visao_celulas * CM.sub                  # o raio da visao, em subunidades
HOJE = ("fome", "higiene", "energia", "humor", "saude")
NOVOS = ("tedio", "curiosidade", "solidao", "estresse", "dor", "susto")
NOITE = 23 * 60 / 1440                              # 23 h, dentro da noite (22 h a 7 h)
DIA = 12 * 60 / 1440


def pc(**faltas) -> PercepcaoCorpo:
    """a PercepcaoCorpo do v11 com o mundo (os receptores do prototipo) com as faltas dadas (0 nas outras): a leitura e S - falta nos de
    hoje e a propria falta nos novos"""
    d = {r: S - faltas.get(r, 0) for r in HOJE}
    d.update({r: faltas.get(r, 0) for r in NOVOS})
    return PercepcaoCorpo(**d)


def obs(corpo: PercepcaoCorpo | None = None, vistos=(), hora=DIA, dormindo=0.0, ticks=0, x=512, y=240, direcao=0) -> Observacao:
    corpo = corpo or pc()
    ve = (corpo.fome / S, corpo.higiene / S, corpo.energia / S, corpo.humor / S, corpo.saude / S, 0.0, dormindo, hora)
    return Observacao(vetor_estado=ve, ticks_desde_cuidado=ticks, total_cuidados=0, corpo=corpo,
                      mundo=PercepcaoMundo(x=x, y=y, regiao=1, vistos=tuple(vistos), cheiro=0, direcao_cheiro=direcao,
                                           alvo_pendente=None))


def racao(ident=3, d=32, tipo="racao"):
    return (ident, tipo, d, 0, d)


def cerebro(**kw) -> DigiBrain:
    return DigiBrain(CONFIG_PADRAO, replace(CONFIG_DIGIBRAIN_LIGADA, **kw), CM)


def unidades_de(c: DigiBrain, o: Observacao) -> tuple[dict, list, dict, dict]:
    """a decisao ate o M-IMPULSO (sem o M-ARB): {chave: unidade}, z, o afeto e a memoria"""
    m = c.m
    sens = m.sens.codificar(o)
    m.plast.montar(m.sens.receptores)
    afeto = m.afeto.ler(sens)
    ctx = m.estado.contexto()
    mem = m.mem.recuperar(sens, afeto) if c.cd.m_mem else None
    us, z = m.impulso.unidades(sens, afeto, ctx, m.plast, mem, m.afeto.drives(m.sens.receptores))
    return {u["chave"]: u for u in us}, z, afeto, mem


def maior(us: dict) -> tuple:
    return max(us, key=lambda k: us[k]["a"])


class RngContada:
    """uma rng que devolve os u dados e conta as chamadas"""

    def __init__(self, *us: float) -> None:
        self.us, self.n = list(us), 0

    def random(self) -> float:
        self.n += 1
        return self.us.pop(0)


# ================================================================== M-SENS
def test_t_sens_1_a_proximidade_a_classe_e_as_linhas():
    s = Sens(CONFIG_PADRAO, CM)
    vistos = [racao(1, 0), racao(2, R // 2), (3, "racao_podre", R, 0, R), racao(4, R + 30)]
    out = s.codificar(obs(vistos=vistos))
    prox = [o["prox"] for o in out["objetos"]]
    assert prox[0] == S and abs(prox[1] - S // 2) <= 1 and prox[2] == 0 and prox[3] == 0
    assert [o["classe"] for o in out["objetos"]] == ["racao", "racao", "podre", "racao"]
    assert [o["id"] for o in out["objetos"]] == [1, 2, 3, 4]                  # na ordem dos vistos
    assert out["conjuncoes"] == {"comida_vista": S, "sem_comida": 0, "bola_vista": 0}
    with pytest.raises(ValueError, match="vistos"):
        Sens(CONFIG_PADRAO, CM).codificar(obs(vistos=[racao(i, 10) for i in range(CM.max_vistos + 1)]))


def test_t_sens_2_a_habituacao_e_a_novidade():
    s = Sens(CONFIG_PADRAO, CM)
    k = ganho_de_tau(P.tau_hab, CONFIG_PADRAO.intervalo_decisao_ticks, S)
    for n in range(1, 13):
        nov = s.codificar(obs(vistos=[racao(1, 16)]))["objetos"][0]["nov"]
        assert abs(nov - (S - S * (1 - (1 - k / S) ** (n - 1)))) <= n          # a novidade da decisao: a habituacao de antes dela
        assert abs(s.hab["racao"] - S * (1 - (1 - k / S) ** n)) <= n
    h0 = s.hab["racao"]
    for n in range(1, 13):                                                        # ausente: a habituacao volta com a mesma constante
        s.codificar(obs())
        assert abs(s.hab["racao"] - h0 * (1 - k / S) ** n) <= n
    meia = math.ceil(math.log(0.5) / math.log(1 - k / S))
    s2 = Sens(CONFIG_PADRAO, CM)
    for _ in range(meia):
        s2.codificar(obs(vistos=[racao(1, 16)]))
    assert s2.hab["racao"] >= S // 2 - meia and s2.hab["bola"] == 0


def test_t_sens_3_o_que_nao_tem_receptor_nao_muda_a_saida():
    a = obs(corpo=pc(fome=300))
    b = replace(a, vetor_estado=a.vetor_estado[:5] + (0.8,) + a.vetor_estado[6:], total_cuidados=99, bola=1.0, fruta=0.5)
    sa, sb = Sens(CONFIG_PADRAO, CM).codificar(a), Sens(CONFIG_PADRAO, CM).codificar(b)
    assert sa == sb
    with pytest.raises(ValueError, match="fora do prototipo"):           # os orgaos ficam fora do prototipo (secao 6)
        Sens(CONFIG_PADRAO, CM).codificar(obs(corpo=replace(pc(), olfato_comida=10)))


# ================================================================== M-AFETO
def test_t_afeto_1_a_urgencia_linear_por_partes():
    a = Afeto(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA)
    lam = P.urgencia_lambda
    for f in (0, 100, lam):
        assert a.urgencia(f) == div_arred(P.urgencia_a * f, S)
    for f in (lam + 50, lam + 200):
        assert a.urgencia(f) == div_arred(P.urgencia_a * f, S) + div_arred(P.urgencia_b * (f - lam), S)
    assert a.urgencia(S) == S                                              # o corte
    inclina_baixo = a.urgencia(lam) - a.urgencia(lam - 100)
    inclina_alto = a.urgencia(lam + 100) - a.urgencia(lam)
    assert abs(inclina_baixo - div_arred(P.urgencia_a * 100, S)) <= 1
    assert abs(inclina_alto - div_arred((P.urgencia_a + P.urgencia_b) * 100, S)) <= 2


def test_t_afeto_2_o_r_e_o_sinal_corpo_do_a():
    a = Afeto(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA)
    antes, depois = pc(fome=600, energia=200, tedio=300, susto=500), pc(fome=150, energia=210, tedio=280, susto=0)
    recs = HOJE + NOVOS
    drives = tuple(r for r in recs if r != "susto")
    out = a.consequencia(antes, depois, recs)
    assert out["r"] == sinal_corpo(antes, depois, drives, P.ganho_r, S)
    assert sum(out["canais"].values()) == out["r"] and set(out["canais"]) == set(drives)
    sem_saude = tuple(d for d in drives if d != "saude")                       # o sinal_corpo_canais do A nao tem a saude
    assert canais_do_sinal(antes, depois, sem_saude, P.ganho_r, S) == sinal_corpo_canais(antes, depois, sem_saude, P.ganho_r, S)
    assert out["r_n"] == max(-S, min(S, div_arred(out["r"], P.r_norm)))


def test_t_afeto_3_o_g_apr_com_e_sem_a_subchave():
    for e in range(0, S + 1, 64):
        com = Afeto(CONFIG_PADRAO, replace(CONFIG_DIGIBRAIN_LIGADA, modula_g_apr=True))
        com.E = e
        g = com.ler({"falta": {"fome": 0}})["g_apr"]
        assert P.g_min <= g <= P.g_max and g == min(P.g_max, max(P.g_min, P.g0 + div_arred(P.beta_e * e, S)))
        sem = Afeto(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA)
        sem.E = e
        assert sem.ler({"falta": {"fome": 0}})["g_apr"] == P.g0
    doadora = (0, S, S // 2)
    emb = Afeto(CONFIG_PADRAO, replace(CONFIG_DIGIBRAIN_LIGADA, modula_g_apr=True, controle_g_apr="embaralhado"), serie_e_doadora=doadora)
    emb.E = 7
    assert [emb.ler({"falta": {"fome": 0}})["g_apr"] for _ in doadora] == [emb.g_apr_de(e) for e in doadora]
    with pytest.raises(RuntimeError, match="doadora"):
        emb.ler({"falta": {"fome": 0}})
    con = Afeto(CONFIG_PADRAO, replace(CONFIG_DIGIBRAIN_LIGADA, controle_g_apr="constante", g_apr_constante=1300))
    con.E = S
    assert con.ler({"falta": {"fome": 0}})["g_apr"] == 1300


# ================================================================== M-ESTADO
def test_t_estado_1_o_integrador_e_a_meia_vida():
    delta = CONFIG_PADRAO.intervalo_decisao_ticks
    for tau in (P.tau_c, P.tau_v, P.tau_e, P.tau_hab, P.tau_f_desce):
        k = ganho_de_tau(tau, delta, S)
        assert k == div_arred(S * delta, tau)
        y = 0
        for n in range(1, 41):
            y = integrar(y, S, k, S)
            assert abs(y - S * (1 - (1 - k / S) ** n)) <= n
        meia = math.log(0.5) / math.log(1 - k / S)                       # em decisoes
        assert abs(meia - math.log(2) * tau / delta) <= 0.5 * meia + 1     # a meia-vida da tabela de tau (Euler, k pequeno)


def _unidade(chave, d=None):
    return {"chave": chave, "d": d}


def test_t_estado_2_a_intencao_persiste_e_acaba():
    est = EstadoDinamico(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA)
    z = [S] + [0] * (len(CARACTERISTICAS_DIGIBRAIN) - 1)
    comer = chave_unidade("comer", "comida", 3)
    est.contexto()
    assert est.escolhida(_unidade(comer, 100), z, S, 0) == []
    c1 = est.I["C"]
    assert est.consequencia(10, {"comeu": None, "brincou_com_bola": False, "chegou": False}, {"visto": True, "d": 80, "ha_cheiro": False}) == []
    ctx = est.contexto()
    assert ctx["persistencia"] == {comer: mul(P.w_pers, c1, S)}
    est.escolhida(_unidade(comer, 80), z, S, 1)
    assert est.I["C"] > c1                                                # escolheu de novo: o C sobe
    f0 = est.F
    fins = est.consequencia(5, {"comeu": None, "brincou_com_bola": False, "chegou": False}, {"visto": False, "d": None, "ha_cheiro": False})
    assert [f["motivo"] for f in fins] == ["sumiu"] and est.I is None and est.F > f0 and fins[0]["r"] == 15
    # N_desiste decisoes sem progresso
    est.contexto()
    est.escolhida(_unidade(comer, 50), z, S, 2)
    for i in range(P.n_desiste):
        if i:
            est.contexto()
            est.escolhida(_unidade(comer, 50), z, S, 2 + i)
        fins = est.consequencia(0, {"comeu": None, "brincou_com_bola": False, "chegou": False}, {"visto": True, "d": 50, "ha_cheiro": False})
    assert [f["motivo"] for f in fins] == ["desistiu"]
    # com a meta: o C zera e o F nao sobe
    est.contexto()
    est.escolhida(_unidade(comer, 20), z, S, 9)
    f1 = est.F
    fins = est.consequencia(300, {"comeu": {"id": 3}, "brincou_com_bola": False, "chegou": True}, {"visto": False, "d": None,
                                                                                                    "ha_cheiro": False})
    assert [(f["motivo"], f["meta"], f["C"]) for f in fins] == [("meta", True, 0)] and est.F == f1
    # trocou: a intencao acaba sem a meta ao escolher outra coisa; a sem alvo e uma opcao de uma decisao so
    est.contexto()
    est.escolhida(_unidade(comer, 20), z, S, 10)
    est.consequencia(0, {"comeu": None, "brincou_com_bola": False, "chegou": False}, {"visto": True, "d": 10, "ha_cheiro": False})
    est.contexto()
    fins = est.escolhida(_unidade(chave_unidade("dormir")), z, S, 11)
    assert [f["motivo"] for f in fins] == ["trocou"] and est.I is None
    assert [f["motivo"] for f in est.consequencia(0, None, {"visto": True, "d": None, "ha_cheiro": False})] == ["unica"]


# ================================================================== M-IMPULSO
def test_t_impulso_1_o_inato_sozinho():
    racao_2 = [racao(3, 32)]
    us, *_ = unidades_de(cerebro(), obs(corpo=pc(fome=819), vistos=racao_2))                  # (a) fome alta, racao a 2 celulas
    assert maior(us) == chave_unidade("comer", "comida", 3)
    assert us[chave_unidade("chamar_atencao")]["a"] < us[chave_unidade("comer", "comida", 3)]["a"]   # comer vence chamar
    us, *_ = unidades_de(cerebro(), obs(corpo=pc(fome=819)))                                   # (b) fome alta, nada a vista
    assert maior(us) == chave_unidade("chamar_atencao")
    for d in (0, 32):                                                                           # (c) saciado com a racao a vista
        us, *_ = unidades_de(cerebro(), obs(corpo=pc(), vistos=[racao(3, d)]))
        assert us[chave_unidade("comer", "comida", 3)]["a"] == 0
    us, *_ = unidades_de(cerebro(), obs(corpo=pc(energia=717), hora=NOITE))                    # (d) energia baixa de noite
    assert maior(us) == chave_unidade("dormir")
    # todas concorrem: nenhuma regra corta as outras
    us, *_ = unidades_de(cerebro(), obs(corpo=pc(fome=819), vistos=racao_2))
    assert set(k[0] for k in us) == {a.value for a in (AcaoPet.OCIOSO, AcaoPet.DORMIR, AcaoPet.COMER, AcaoPet.BRINCAR,
                                                        AcaoPet.CHAMAR_ATENCAO, AcaoPet.EXPLORAR, AcaoPet.EMBURRAR)}


def test_t_impulso_2_o_incentivo_revaloriza_com_o_estado():
    pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
    recs = HOJE + NOVOS
    pl.montar(recs)
    pl.desfecho["racao"][0] = 300                                         # comer racao sobe a leitura da fome em 300
    drives = tuple(r for r in recs if r != "susto")
    gs = []
    for f in (250, 500):
        corpo = pc(fome=f)
        vp = valor_previsto(corpo, {"fome": 300}, drives, P.ganho_r, S)
        g = pl.incentivo(corpo, "racao", drives)
        assert g == max(0, min(P.g_max_incentivo, div_arred(P.c_g * vp, P.s_v)))
        gs.append((vp, g))
    assert gs[1][0] > gs[0][0] and gs[1][1] > gs[0][1]                    # quadratico na falta: com o dobro da falta, mais incentivo
    assert gs[0][0] == div_arred(P.ganho_r * (250 * 250 - 0), S)          # a falta 250 vai a 0 com +300 (o corte em S)
    assert gs[1][0] == div_arred(P.ganho_r * (500 * 500 - 200 * 200), S)


# ================================================================== M-MEM
def _ep(decisao, ponto, r_n, classe="racao", origem="consumo", r=None):
    return {"decisao": decisao, "ponto": ponto, "regiao": 1, "classe": classe, "delta": {}, "r": r_n * 2 if r is None else r,
            "r_n": r_n, "hora": 0, "fome_antes": 0, "origem": origem}


def test_t_mem_1_o_consumo_vira_episodio():
    c = cerebro()
    o = obs(corpo=pc(fome=700), vistos=[racao(3, 8)])
    rng = random.Random(1)
    while True:
        acao = c.agir(o, rng)
        if acao is AcaoPet.COMER:
            break
        c.consequencia_corpo(acao, {}, o)
        c.observar(Transicao(o, acao, o))
        if acao in (AcaoPet.EXPLORAR, AcaoPet.BRINCAR):
            raise AssertionError("o teste espera comer ou uma acao sem alvo")
    alvo = c.escolher_alvo(AcaoPet.COMER, [Alvo("comida", 520, 240, 3)], None, 0)
    depois = obs(corpo=pc(fome=250), x=520, y=240)
    c.observar(Transicao(o, AcaoPet.COMER, depois))
    c.consequencia_mundo(AcaoPet.COMER, {"comeu": {"id": 3, "tipo": "racao", "situacao": "madura", "como": "comer"}, "chegou": True,
                                         "brincou_com_bola": False}, depois)
    c.consequencia_corpo(AcaoPet.COMER, {}, depois)
    k = c.k - 1
    c.agir(depois, rng)
    eps = c.m.mem.episodios
    assert alvo.id == 3 and len(eps) == 1
    e = eps[0]
    r = sinal_corpo(o.corpo, depois.corpo, tuple(x for x in HOJE + NOVOS if x != "susto"), P.ganho_r, S)
    assert (e["decisao"], e["classe"], e["origem"], e["ponto"], e["lugar"], e["r"], e["fome_antes"]) == \
        (k, "racao", "consumo", [520, 240], [520 // CM.sub, 240 // CM.sub], r, 700)
    assert e["delta"]["fome"] == 450 and r > 0


def test_t_mem_2_a_recuperacao():
    sens_fome = {"pos": (100, 100), "conjuncoes": {"comida_vista": 0}}
    m = Memoria(CM)
    m.codificar(_ep(0, (400, 100), 500))
    rec = m.recuperar(sens_fome, {"urgencias": {"fome": S}})                       # (a) com fome e nada a vista
    dist = 300
    assert rec["recuperado"] == 0 and rec["ponto"] == (400, 100) and rec["M"] == mul(P.w_mem, 500, S) > 0
    assert rec["nota"] == mul(500, S - div_arred(dist * S, P.d_max), S)
    us, *_ = unidades_de(_com_memoria(m), obs(corpo=pc(fome=819), x=100, y=100))
    assert us[chave_unidade("explorar", "ponto", (400, 100))]["termos"]["memoria"] > 0
    assert m.recuperar(sens_fome, {"urgencias": {"fome": 0}})["recuperado"] is None    # (b) saciado
    assert m.recuperar({**sens_fome, "conjuncoes": {"comida_vista": 10}}, {"urgencias": {"fome": S}})["recuperado"] is None
    neg = Memoria(CM)
    neg.codificar(_ep(0, (400, 100), -300))
    assert neg.recuperar(sens_fome, {"urgencias": {"fome": S}})["recuperado"] is None   # (c) o episodio negativo nao atrai


def _com_memoria(m: Memoria) -> DigiBrain:
    c = cerebro()
    c.m.mem = m
    return c


def test_t_mem_3_cheio_sai_o_de_menor_r():
    m = Memoria(CM)
    rs = [400, 30, 200, -30, 500] + [100 + i for i in range(P.n_ep - 5)]
    for i, r in enumerate(rs):
        m.codificar(_ep(i, (16 * i, 16), r, r=r))
    assert len(m.episodios) == P.n_ep
    m.codificar(_ep(99, (900, 16), 250, r=250))
    assert len(m.episodios) == P.n_ep and m.saidas == [{"id": 1, "r": 30}]            # |30| = |-30|: sai o mais antigo
    m.codificar(_ep(100, (900, 32), 260, r=260))
    assert m.saidas[-1] == {"id": 3, "r": -30}


def test_t_mem_4_a_visita_vazia_apaga_o_lugar():
    m = Memoria(CM)
    m.codificar(_ep(0, (400, 100), 500))
    sens = {"pos": (100, 100), "conjuncoes": {"comida_vista": 0}}
    assert m.recuperar(sens, {"urgencias": {"fome": S}})["recuperado"] == 0
    m.codificar(_ep(5, (402, 101), 0, classe="nao_havia", origem="visita", r=0))
    rec = m.recuperar(sens, {"urgencias": {"fome": S}})
    assert rec["recuperado"] is None and rec["M"] == 0                                 # o mais recente do lugar manda


# ================================================================== M-ARB
def _units(*ativs, acoes=None):
    acoes = acoes or ["ocioso"] + ["comer"] * (len(ativs) - 1)
    return [{"chave": (a, "x", i), "acao": a, "a": x, "soma": x, "termos": {"incentivo": 0, "habito": 0, "memoria": 0, "persistencia": 0}}
            for i, (a, x) in enumerate(zip(acoes, ativs))]


def test_t_arb_1_o_sorteio_inteiro():
    arb = Arbitragem()
    us = _units(0, 300, 100, 600)
    g_exp = 0
    w = arb.pesos([u["a"] for u in us], g_exp)
    assert w == [0, 300, 100, 600]
    T = sum(w)
    for u in [i / 50 for i in range(50)] + [0.999999999]:
        alvo = min(int(u * T), T - 1)
        esperado = 1 if alvo < 300 else (2 if alvo < 400 else 3)
        rng = RngContada(u)
        out = arb.escolher(us, {"g_exp": g_exp}, {"leitura": {"energia": S}}, rng)
        assert out["indice"] == esperado == sortear_inteiro(w, u) and rng.n == 1 and out["u"] == u
    rng = RngContada()
    out = arb.escolher(_units(0, 0, 500), {"g_exp": g_exp}, {"leitura": {"energia": S}}, rng)
    assert out["indice"] == 2 and rng.n == 0 and out["u"] is None                     # um candidato so: nenhuma chamada
    out = arb.escolher(_units(0, 0), {"g_exp": g_exp}, {"leitura": {"energia": S}}, rng)
    assert out["indice"] == 0 and out["nada_a_fazer"] and rng.n == 0                  # nenhum: ocioso, registrado
    eps = mul(S, P.epsilon, S)
    assert arb.pesos([0, 10], S) == [0, 10 + eps]                                       # o g_exp achata so as que concorrem


def test_t_arb_2_o_reflexo_do_sono():
    arb = Arbitragem()
    us = _units(0, 5000, 4000, 10, acoes=["ocioso", "comer", "explorar", "dormir"])
    rng = RngContada()
    out = arb.escolher(us, {"g_exp": S}, {"leitura": {"energia": P.lambda_sono - 1}}, rng)
    assert out["unidade"]["acao"] == "dormir" and out["reflexo"] and rng.n == 0 and out["u"] is None
    assert not any(v for k, v in out["sondas"].items() if k.endswith("_decidiu"))
    c = cerebro()
    acao = c.agir(obs(corpo=pc(energia=S - P.lambda_sono + 1, fome=900), vistos=[racao(3, 8)]), RngContada())
    assert acao is AcaoPet.DORMIR and c.motivos[-1]["reflexo"] and c.motivos[-1]["u"] is None


# ================================================================== M-PLAST
def test_t_plast_1_o_desfecho_converge_e_e_o_modelo_mundo():
    delta = [400, 0, -30, 0, 0, 0, 0, 0, 0, 0, 0]
    recs = HOJE + NOVOS
    for g_apr in (S, 3 * S // 2):
        pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
        pl.montar(recs)
        eta = mul(g_apr, P.eta_d, S)
        for n in range(1, 16):
            pl.consumo("racao", delta, g_apr)
            assert abs(pl.desfecho["racao"][0] - 400 * (1 - (1 - eta / S) ** n)) <= n
    # com g_apr = S, a conta do ModeloMundo, consumo a consumo e com o andar
    pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
    pl.montar(recs)
    mm = ModeloMundo(CONFIG_MODELO_MUNDO_LIGADA, CM)
    mm._montar(pc())
    assert mm.receptores == recs
    l0 = [624, S, 700, S, S, 0, 0, 0, 0, 0, 0]
    for i, (dx, ganho) in enumerate(((40, 380), (0, 300), (60, 350))):
        l1 = list(l0)
        l1[0] += ganho
        l1[2] -= dx // 6
        pl.consequencia_p1("comer", "racao", l0, l1, (100, 100), (100 + dx, 100), S)
        mm._decisao = (mm.k, l0, 100, 100)
        mm.k += 1
        pm = PercepcaoMundo(x=100 + dx, y=100, regiao=1, vistos=(), cheiro=0, direcao_cheiro=0, alvo_pendente=None)
        mm.consequencia(AcaoPet.COMER, {"comeu": {"tipo": "racao", "situacao": "madura"}},
                        Observacao(vetor_estado=(0.0,) * 8, ticks_desde_cuidado=0, total_cuidados=0,
                                   corpo=PercepcaoCorpo(**dict(zip(recs, l1))), mundo=pm))
        assert pl.desfecho["racao"] == mm.desfecho["racao"] and pl.andar == mm.andar


def _op(b="comer", r=400, e=None, g_apr=S):
    return {"chave": (b, None, None), "r": r, "e": e or ([S, 0, 300] + [0] * (len(CARACTERISTICAS_DIGIBRAIN) - 3)), "g_apr": g_apr}


def test_t_plast_2_o_habito_de_tres_fatores():
    for r, sinal in ((400, 1), (-400, -1), (0, 0)):
        pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
        pl.creditar(_op(r=r))
        linha = pl.H["comer"]
        passo = mul(S, P.eta_h, S)
        assert linha[0] == sinal * abs(mul(passo, mul(r, S, S), S)) and linha[1] == 0             # o pre a 0 nao muda
        assert linha[2] == mul(passo, mul(r, 300, S), S)
        assert all(v == 0 for b, l in pl.H.items() if b != "comer" for v in l)                      # so a linha da escolhida
    pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
    for _ in range(200):
        pl.creditar(_op(r=S))
    assert pl.H["comer"][0] == P.h_max and pl.no_teto()[0] >= 1                                    # o teto segura
    assert Plasticidade(replace(CONFIG_DIGIBRAIN_LIGADA, p2=False)).creditar(_op()) is None


def test_t_plast_3_o_g_apr_dobrado_dobra_o_passo():
    recs = HOJE + NOVOS
    passos = []
    for g in (S // 2, S):
        pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
        pl.montar(recs)
        pl.consumo("racao", [512] + [0] * 10, g)
        pl.creditar(_op(r=S, g_apr=g))
        passos.append((pl.desfecho["racao"][0], pl.H["comer"][0]))
    assert abs(passos[1][0] - 2 * passos[0][0]) <= 1 and abs(passos[1][1] - 2 * passos[0][1]) <= 1


# ================================================================== M-ADAPT
def test_t_adapt_1_o_protocol_e_as_falhas_altas():
    c = cerebro()
    assert isinstance(c, Politica)
    with pytest.raises(ValueError, match="corpo e o mundo"):
        c.agir(replace(obs(), corpo=None), random.Random(1))
    with pytest.raises(ValueError, match="corpo e o mundo"):
        c.agir(replace(obs(), mundo=None), random.Random(1))
    c._pendencia = {"intencao": Intencao(AcaoPet.COMER, "comida", 3), "pediu": False}
    c.motivos.append({})
    with pytest.raises(ValueError, match="nao esta entre os candidatos"):
        c.escolher_alvo(AcaoPet.COMER, [Alvo("comida", 1, 1, 4)], None, 0)
    c = cerebro()
    o = obs(corpo=pc(fome=819))
    acao = c.agir(o, random.Random(3))
    with pytest.raises(RuntimeError, match="sem o gancho de consequencia"):
        c.agir(o, random.Random(3))
    assert acao is not None


def test_t_adapt_2_o_alvo_e_o_da_unidade():
    """a unidade escolhida (comer, item 3): o escolher_alvo devolve o candidato do item 3, com o u do motor ignorado"""
    o = obs(corpo=pc(fome=900), vistos=[(1, "racao", 200, 0, 200), racao(3, 16), racao(5, 40)])
    us, _, afeto, _ = unidades_de(cerebro(), o)
    i = list(us).index(chave_unidade("comer", "comida", 3))
    c = cerebro()
    w = Arbitragem().pesos([u["a"] for u in us.values()], afeto["g_exp"])
    u = (sum(w[:i]) + w[i] / 2) / sum(w)
    assert c.agir(o, RngContada(u)) is AcaoPet.COMER and c.motivos[-1]["escolha"] == ["comer", "comida", 3]
    cands = [Alvo("comida", 712, 240, 1), Alvo("comida", 528, 240, 3), Alvo("comida", 552, 240, 5), Alvo("cheiro", 0, 0)]
    assert c.escolher_alvo(AcaoPet.COMER, cands, None, 12345) == cands[1]
    assert c.motivos[-1]["alvo"] == {**cands[1].para_dict(), "do_mem": False}


# ================================================================== o motivo
def test_t_motivo_1_os_termos_e_as_sondas():
    m = Memoria(CM)
    m.codificar(_ep(0, (300, 240), S))
    c = _com_memoria(m)
    o = obs(corpo=pc(fome=600, tedio=200), x=512, y=240)
    us, _, afeto, _ = unidades_de(_com_memoria(_copiar(m)), o)
    for u in us.values():
        assert sum(u["termos"].values()) == u["soma"] and u["a"] == max(0, min(P.a_max, u["soma"]))
    ponto = chave_unidade("explorar", "ponto", (300, 240))
    assert us[ponto]["termos"]["memoria"] > 0
    # um u no meio do intervalo do lugar lembrado: a memoria decide
    w = Arbitragem().pesos([u["a"] for u in us.values()], afeto["g_exp"])
    chaves = list(us)
    i = chaves.index(ponto)
    T = sum(w)
    u = (sum(w[:i]) + w[i] / 2) / T
    acao = c.agir(o, RngContada(u))
    mot = c.motivos[-1]
    assert acao is AcaoPet.EXPLORAR and tuple(mot["escolha"][:2]) == ("explorar", "ponto")
    assert mot["sondas"]["memoria_decidiu"] and mot["sondas"]["aprendido_decidiu"]
    assert not mot["sondas"]["incentivo_decidiu"] and not mot["sondas"]["habito_decidiu"]     # termos nulos nao mudam a sonda
    assert mot["memoria"]["recuperado"] == 0


def _copiar(m: Memoria) -> Memoria:
    n = Memoria(CM)
    n.episodios = [dict(e) for e in m.episodios]
    n.proximo_id = m.proximo_id
    return n


# ================================================================== a cadeia
def test_t_cadeia_0_o_a_so_le_com_fome_abaixo_de_um_quarto():
    """o A do v12 (o instinto do v11, so lido; nada no A muda): com a fome abaixo de 0,25 e a racao a 2 celulas, o unico candidato e
    chamar (policy.py:131-134). E o ponto de partida, nao um gate do A."""
    o = obs(corpo=pc(fome=S - 200), vistos=[racao(3, 32)])
    regra, candidatos = impulsos(PoliticaInstinto(CONFIG_PADRAO), o)
    assert o.vetor_estado[0] < 0.25 and regra == "pedido_necessidade" and candidatos == (AcaoPet.CHAMAR_ATENCAO,)


def test_t_cadeia_2_o_p1_baixa_o_limiar_de_comer():
    """antes dos consumos, com fome moderada abaixo do limiar inato, comer a racao tem peso 0; depois de k consumos com o mesmo Delta,
    peso > 0, com o valor da conta"""
    o = obs(corpo=pc(fome=307), vistos=[racao(3, 32)])
    c = cerebro()
    comer3 = chave_unidade("comer", "comida", 3)
    us, *_ = unidades_de(c, o)
    assert us[comer3]["a"] == 0 and us[comer3]["termos"]["incentivo"] == 0
    for _ in range(8):
        c.m.plast.consumo("racao", [460] + [0] * 10, S)
    c2 = cerebro()
    c2.m.plast = c.m.plast
    us2, *_ = unidades_de(c2, o)
    drives = tuple(r for r in HOJE + NOVOS if r != "susto")
    d_racao = c.m.plast.desfecho["racao"][0]
    vp = valor_previsto(o.corpo, {"fome": d_racao}, drives, P.ganho_r, S)
    g = mul(max(0, min(P.g_max_incentivo, div_arred(P.c_g * vp, P.s_v))), us2[comer3]["objeto"]["prox"], S)
    assert us2[comer3]["termos"]["incentivo"] == g > 0
    assert us2[comer3]["a"] == max(0, us[comer3]["soma"] + g) > 0
