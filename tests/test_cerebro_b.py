"""V2, CEREBRO-B (docs/TAREFA_V2_CEREBRO_B.md; contrato da secao 1 de docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md): o DigiBrain B,
CfC + ator-critico + elegibilidade (digilab/policies/cerebro_b.py).

Gates da tarefa: G1; aprendizado desligado = instinto byte a byte, e igual ao P0 dos lobos; capacidade em [0,9; 1,1] x A; a sonda
reproduz a decisao sem o aprendido; o B aprende algo simples com a consequencia, com a conta conhecida. Mais o contrato da secao 1.1
(ganchos, a entrada da informacao, a escolha da fruta). So as sementes dos testes.
"""
from __future__ import annotations

import copy
import math
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import cerebro_b_bancada as cbb  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_CEREBRO_B, CONFIG_CEREBRO_B_APRENDIZ, CONFIG_CONSEQUENCIA,  # noqa: E402
                            CONFIG_FRUTAS_LIGADA, CONFIG_PADRAO)
from digilab.events import FRUTAS, AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import PoliticaInstintoFrutas  # noqa: E402
from digilab.policies import cerebro_b  # noqa: E402
from digilab.policies.cerebro_b import N_ENTRADAS_B, PoliticaCerebroB, fabrica_cerebro_b  # noqa: E402
from digilab.policies.lobos import ACOES, PoliticaLobos, sinal_homeostatico_fruta  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = CONFIG_CEREBRO_B.escala
CF, CB = CONFIG_FRUTAS_LIGADA, CONFIG_BOLA_LIGADA
CBA = CONFIG_CEREBRO_B_APRENDIZ
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel", "iguais_frutas")
BANCADA = cbb.BancadaComB(4, 64)
E = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)
QUASE_UM = 1.0 - 1e-12        # u que escolhe o ultimo candidato (comer, na regra fruta_no_cenario)


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _obs(presenca: tuple, info: tuple = (0.0, 0.0, 0.0), estado: Estado = E) -> Observacao:
    return replace(Observacao.de_estado(estado), fruta=0.5, frutas_cenario=presenca, info_frutas=info)


def _vida(dono, braco, s, mundo, cerebro="cerebro_b", bancada=BANCADA):
    return bancada.vida(bv.EspecVida(dono, braco, s, None, mundo, cerebro))


def _cerebro(vida):
    return bv.do_braco(vida.motor.politica).cerebro


def _p(motivo: dict, acao: str) -> float:
    """p(acao) da decisao, somando os pesos na ordem dos candidatos (a mesma conta do cerebro)."""
    total = 0.0
    for a in motivo["candidatos"]:
        total += motivo["pesos"][a]
    return motivo["pesos"][acao] / total


def _comer_so(c: PoliticaCerebroB, fruta: str, d_humor: float, presenca: tuple | None = None) -> dict:
    """Uma decisao de comer com `fruta` sozinha no cenario e a E2: a fruta muda o humor em d_humor. Devolve o motivo."""
    pres = presenca or tuple(1.0 if f == fruta else 0.0 for f in FRUTAS)
    assert c.agir(_obs(pres), _Rng(QUASE_UM)) is AcaoPet.COMER
    m = c.motivos[-1]
    t = Transicao(Observacao.de_estado(E), AcaoPet.COMER, Observacao.de_estado(E))
    c.observar_consequencia(t, 0, CONFIG_CONSEQUENCIA)
    assert c.escolher_fruta([fruta], {fruta: 0.5}, 0.0) == fruta
    c.fruta_comida(fruta, Observacao.de_estado(replace(E, humor=E.humor + d_humor)))
    return m


# ------------------------------------------------------------------ parametros e capacidade (contrato 1.3)


def test_parametros_registrados():
    cerebro_b.validar_parametros_cerebro_b()
    assert CONFIG_CEREBRO_B.aprendizado_ligado is False and CBA.aprendizado_ligado is True


def test_capacidade_dentro_da_faixa_do_a():
    """Os parametros aprendiveis do B (a celula CfC, a cabeca das acoes, a cabeca da fruta com o peso da informacao e o critico) ficam em
    [0,9; 1,1] x os do A no ponto da K2 (T3 com o w0_info: 763)."""
    b = PoliticaCerebroB(None, CBA, None, CF)
    a = PoliticaLobos(None, replace(bv.cfg_lobos_do_ponto("T3"), w0_info=S // 2), None, CF)
    H, D = CBA.n_ocultos, N_ENTRADAS_B
    conta = 3 * (H * (D + H) + H) + len(ACOES) * (H + 1) + len(FRUTAS) * (H + 1) + 1 + (H + 1)
    assert a.n_pesos() == 763
    assert b.n_pesos() == b.estado_interno()["parametros_aprendidos"] == conta == 648 + 70 + 31 + 10 == 759
    assert 0.9 <= b.n_pesos() / a.n_pesos() <= 1.1
    # a contagem nao depende do mundo nem da chave (a estrutura e herdada)
    assert PoliticaCerebroB().n_pesos() == PoliticaCerebroB(None, CBA, CB, None).n_pesos() == 759


# ------------------------------------------------------------------ G2: aprendizado desligado = instinto byte a byte


@pytest.mark.parametrize("mundo", MUNDOS_FRUTAS + ("bola",))
def test_aprendizado_desligado_e_o_instinto_pela_bancada(mundo):
    """O P0 do B (aprendizado desligado) e o P0 do instinto que ve o mundo, byte a byte (log, estado, acoes, rngs, frutas), e o P0 dos
    lobos."""
    for dono in DONOS:
        for s in (101, 202):
            b = _vida(dono, "P0", s, mundo).motor
            assert bv.resumo_motor(b) == bv.resumo_motor(_vida(dono, "P0", s, mundo, "instinto").motor)
            assert bv.resumo_motor(b) == bv.resumo_motor(_vida(dono, "P0", s, mundo, "lobos").motor)


def test_aprendizado_desligado_no_padrao_e_nos_bracos_que_aprendem():
    """No mundo padrao, o P0 do B e o dos lobos (que e o instinto, gate da L0). Com o aprendizado desligado o B e o instinto em
    qualquer braco: o P1 e o P3 do B desligado vivem a vida do P0 do instinto."""
    for dono in DONOS:
        assert bv.resumo_motor(_vida(dono, "P0", 101, "padrao").motor) == bv.resumo_motor(_vida(dono, "P0", 101, "padrao", "lobos").motor)
    desligado = cbb.BancadaComB(4, 64, cfg_cerebro_b=CONFIG_CEREBRO_B)
    for braco in ("P1", "P3"):
        for mundo in ("descasado", "padrao"):
            ref = "instinto" if mundo != "padrao" else "lobos"
            b = _vida("atencioso", braco, 202, mundo, bancada=desligado).motor
            assert bv.resumo_motor(b) == bv.resumo_motor(_vida("atencioso", "P0", 202, mundo, ref).motor)


@pytest.mark.parametrize("com_mundo", (False, True))
def test_aprendizado_desligado_decisao_a_decisao(com_mundo):
    """3000 observacoes aleatorias (todas as regras): a mesma acao e o mesmo estado da rng do instinto."""
    gen = random.Random(7)
    b = PoliticaCerebroB(None, CONFIG_CEREBRO_B, CB if com_mundo else None, CF if com_mundo else None)
    i = PoliticaInstintoFrutas(None, CB, CF) if com_mundo else PoliticaInstinto()
    r1, r2 = random.Random(11), random.Random(11)
    regras = set()
    for _ in range(3000):
        v = tuple(gen.random() for _ in range(6)) + (float(gen.random() < 0.3), gen.random())
        obs = Observacao(vetor_estado=v, ticks_desde_cuidado=gen.randrange(0, 1200), total_cuidados=0)
        if com_mundo:
            pres = tuple(float(gen.random() < 0.4) for _ in FRUTAS)
            obs = replace(obs, bola=float(gen.random() < 0.3), fruta=gen.random() if any(pres) else 0.0, frutas_cenario=pres)
        assert b.agir(obs, r1) is i.agir(obs, r2)
        assert r1.getstate() == r2.getstate()
        regras.add(b.ultima_regra)
    assert len(regras) >= (9 if com_mundo else 7)


def test_aprendiz_novo_decide_como_o_instinto():
    """Com o aprendizado LIGADO e nada aprendido (as cabecas em zero), o B ainda decide como o instinto: exp(0) = 1 exato."""
    gen = random.Random(3)
    b = PoliticaCerebroB(None, CBA, CB, CF)
    i = PoliticaInstintoFrutas(None, CB, CF)
    r1, r2 = random.Random(5), random.Random(5)
    for _ in range(500):
        v = tuple(gen.random() for _ in range(6)) + (0.0, gen.random())
        pres = tuple(float(gen.random() < 0.4) for _ in FRUTAS)
        obs = replace(Observacao(vetor_estado=v, ticks_desde_cuidado=gen.randrange(0, 900), total_cuidados=0),
                      fruta=0.5 if any(pres) else 0.0, frutas_cenario=pres)
        assert b.agir(obs, r1) is i.agir(obs, r2)
        b._registro_decisao = None                 # sem sinal: nada a creditar (so a decisao)
    assert r1.getstate() == r2.getstate()


# ------------------------------------------------------------------ G1


@pytest.mark.parametrize("mundo", ("descasado", "mutavel", "padrao"))
def test_g1_replay_bit_a_bit(mundo):
    """Toda vida do B (P0 a P3; P2, P2e e P2a so nas frutas) e o acoplado so cuidado, rejogados do texto do log: tudo igual, estado
    interno incluido (pesos, oculto, traco e motivos)."""
    bracos = ("P0", "P1", "P3") + (("P2", "P2e", "P2a") if mundo != "padrao" else ())
    for dono in ("atencioso", "aleatorio"):
        for braco in bracos:
            v = _vida(dono, braco, 303, mundo)
            BANCADA.conferir_replay(v, v.motor.log.para_jsonl())
            assert bv._interno(BANCADA.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)) == bv._interno(v.motor)
    if mundo != "padrao":
        origem = _vida("atencioso", "P3", 303, mundo)
        for destino in ("P1", "P3"):
            BANCADA.conferir_replay(BANCADA.acoplar(origem, destino, "sem_ensino"))


def test_os_blocos_n6_e_n7_ficam_fora():
    for braco in ("MR", "P1+ped"):
        with pytest.raises(ValueError):
            _vida("atencioso", braco, 101, "descasado")


# ------------------------------------------------------------------ a sonda do aprendido (contrato 1.1)


def _treinado(s: int = 202):
    """Um B treinado de verdade: o cerebro de uma vida P3 do descasado (o dono ensina o ator)."""
    return _cerebro(_vida("atencioso", "P3", s, "descasado"))


def _zerar_aprendido(c: PoliticaCerebroB) -> PoliticaCerebroB:
    """O gemeo com a parte aprendida zerada: as cabecas das acoes e da fruta em zero e o peso da informacao no inato (a celula fica:
    ela so age pelas cabecas)."""
    z = copy.deepcopy(c)
    L = z._L
    for i in range(L.A, L.info):
        z._theta[i] = 0.0
    z._theta[L.info] = z._theta0[L.info]
    return z


def test_sonda_reproduz_a_decisao_sem_o_aprendido():
    """Para observacoes aleatorias, a acao da sonda (`acao_sem_aprendido`) e a que o gemeo com a parte aprendida zerada toma com o mesmo
    u, e o gemeo e o instinto. O aprendido decide em parte das decisoes (nao e sempre o prior)."""
    c = _treinado()
    assert c.pesos_mudaram()
    zero = _zerar_aprendido(c)
    gen = random.Random(5)
    decidiu = 0
    for _ in range(1500):
        v = (gen.random(), gen.random(), gen.random(), gen.random(), gen.random(), gen.random(), 0.0, gen.random())
        pres = tuple(float(gen.random() < 0.5) for _ in FRUTAS)
        obs = replace(Observacao(vetor_estado=v, ticks_desde_cuidado=gen.randrange(0, 900), total_cuidados=0),
                      fruta=0.5 if any(pres) else 0.0, frutas_cenario=pres,
                      info_frutas=tuple(gen.choice((-1.0, 0.0, 1.0)) for _ in FRUTAS))
        u = gen.random()
        c.agir(obs, _Rng(u))
        zero.agir(obs, _Rng(u))
        m, mz = c.motivos[-1], zero.motivos[-1]
        assert m["sonda"]["acao_sem_aprendido"] == mz["acao"] and mz["sonda"]["aprendido_decidiu"] is False
        assert all(z == 0.0 for z in mz["aprendido"].values())
        decidiu += m["sonda"]["aprendido_decidiu"]
        c._registro_decisao = zero._registro_decisao = None
    assert 0 < decidiu < 1500


def test_sonda_da_fruta_reproduz_a_escolha_sem_o_aprendido():
    """A escolha da fruta sem o aprendido e a do gemeo zerado com o mesmo u; a sem a informacao, a do gemeo com theta_info 0."""
    c = PoliticaCerebroB(CONFIG_PADRAO, replace(CBA, w0_info=0.5), None, CF)
    L = c._L
    c._theta[L.bF + FRUTAS.index("a")] = -1.5            # o treino da escolha precisa de duas frutas; aqui, direto
    c._theta[L.Fr + FRUTAS.index("b") * L.H + 2] = 2.0
    c._theta[L.info] = 1.25
    zero = _zerar_aprendido(c)
    sem_info = copy.deepcopy(c)
    sem_info._theta[L.info] = 0.0
    gen = random.Random(9)
    decidiu = 0
    for _ in range(400):
        presentes = [f for f in FRUTAS if gen.random() < 0.7] or ["b"]
        pres = tuple(1.0 if f in presentes else 0.0 for f in FRUTAS)
        info = tuple(gen.choice((-1.0, 0.0, 1.0)) for _ in FRUTAS)
        inc = {f: 0.2 + gen.random() for f in presentes}
        u = gen.random()
        escolhas = []
        for cer in (c, zero, sem_info):
            assert cer.agir(_obs(pres, info), _Rng(QUASE_UM)) is AcaoPet.COMER
            escolhas.append(cer.escolher_fruta(presentes, inc, u))
            cer._registro_decisao = None
        sonda = c.motivos[-1]["fruta"]["sonda"]
        assert sonda["escolha_sem_aprendido"] == escolhas[1] and sonda["escolha_sem_info"] == escolhas[2]
        decidiu += sonda["aprendido_decidiu"]
    assert decidiu > 0


# ------------------------------------------------------------------ o B aprende com a consequencia (conta e tendencia)


def test_aprende_com_a_consequencia_a_conta_do_primeiro_passo():
    """A fruta 'a' sozinha derruba o humor 0,8 -> 0,7. A E2 da r = -204 / 1024 (ganho 4: falta 205 -> 307). O critico comeca em zero,
    entao delta = r. O traco da primeira decisao e o proprio gradiente: na cabeca das acoes, d log p(comer) / d b_comer = 1 - p(comer) e
    d / d b_a = -p(a) nos outros candidatos. Logo b_comer = taxa_ator x delta x (1 - p), b_a = taxa_ator x delta x (-p_a), o vies do
    critico = taxa_critico x delta; as acoes fora dos candidatos e a cabeca da fruta (uma fruta so) nao mudam."""
    c = PoliticaCerebroB(CONFIG_PADRAO, CBA, None, CF)
    L = c._L
    m = _comer_so(c, "a", -0.1)
    r = sinal_homeostatico_fruta(Observacao.de_estado(E), Observacao.de_estado(replace(E, humor=E.humor - 0.1)), S,
                                 CONFIG_CONSEQUENCIA) / S
    assert r == -204 / 1024
    passo = CBA.taxa_ator * r
    for k, a in enumerate(ACOES):
        if a.value in m["candidatos"]:
            esperado = passo * ((1.0 if a is AcaoPet.COMER else 0.0) - _p(m, a.value))
        else:
            esperado = 0.0
        assert c._theta[L.bA + k] == esperado, a
    assert c._critico[-1] == CBA.taxa_critico * r
    assert all(w == 0.0 for w in c._theta[L.Fr:L.info]) and c._theta[L.info] == 0.0
    assert c._theta[L.bA + ACOES.index(AcaoPet.COMER)] < 0.0


@pytest.mark.parametrize("d_humor, sentido", ((-0.1, -1), (+0.1, +1)))
def test_tendencia_a_fruta_ruim_afasta_e_a_boa_atrai(d_humor, sentido):
    """Tendencia: a cada consumo de 'a' sozinha, p(comer | so 'a') cai se ela faz mal e sobe se faz bem (o logit aprendido de comer
    acompanha). O critico aprende o valor esperado (delta encolhe em modulo)."""
    c = PoliticaCerebroB(CONFIG_PADRAO, CBA, None, CF)
    ps, zs = [], []
    for _ in range(12):
        m = _comer_so(c, "a", d_humor)
        ps.append(_p(m, "comer"))
        zs.append(m["aprendido"]["comer"])
    assert zs[0] == 0.0 and sentido * zs[-1] > 0.0
    assert sentido * (ps[-1] - ps[0]) > 0.0
    assert sum(1 for x, y in zip(ps, ps[1:]) if sentido * (y - x) > 0.0) >= 9


def test_a_informacao_entra_na_escolha_da_fruta():
    """Contrato 1.1: a entrada da informacao. Inata (w0_info, com o aprendizado desligado): o peso da fruta informada 'mal' e o
    incentivo x exp(-w0_info), 'bem' x exp(+w0_info), sem informacao o incentivo. Aprendida: depois de escolher, entre duas frutas, a
    informada 'mal' e ela fazer mal, theta_info sobe na direcao de evitar o 'mal' (cresce)."""
    inata = PoliticaCerebroB(CONFIG_PADRAO, replace(CONFIG_CEREBRO_B, w0_info=1.0), None, CF)
    inata.agir(_obs((1.0, 1.0, 1.0), (-1.0, 1.0, 0.0)), _Rng(QUASE_UM))
    inata.escolher_fruta(["a", "b", "c"], {"a": 0.8, "b": 0.6, "c": 0.4}, 0.5)
    assert inata.motivos[-1]["fruta"]["pesos"] == {"a": 0.8 * math.exp(-1.0), "b": 0.6 * math.exp(1.0), "c": 0.4}
    c = PoliticaCerebroB(CONFIG_PADRAO, CBA, None, CF)
    L = c._L
    assert c.agir(_obs((1.0, 1.0, 0.0), (-1.0, 0.0, 0.0)), _Rng(QUASE_UM)) is AcaoPet.COMER
    c.observar_consequencia(Transicao(Observacao.de_estado(E), AcaoPet.COMER, Observacao.de_estado(E)), 0, CONFIG_CONSEQUENCIA)
    assert c.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, 0.0) == "a"
    c.fruta_comida("a", Observacao.de_estado(replace(E, humor=E.humor - 0.1)))
    # d log p(a) / d theta_info = (1 - P_a) x info_a + (0 - P_b) x info_b = 0,5 x (-1); delta = r < 0: theta_info sobe
    r = -204 / 1024
    assert c._theta[L.info] == CBA.taxa_ator * r * (0.5 * -1.0 + -0.5 * 0.0)
    assert c._theta[L.info] > 0.0
    # e a sonda separa a informacao: com theta_info > 0, 'mal' pesa menos que sem ela
    c.agir(_obs((1.0, 1.0, 0.0), (-1.0, 0.0, 0.0)), _Rng(QUASE_UM))
    c.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, 0.5)
    q = c.motivos[-1]["fruta"]["q"]
    assert q["a"] < q["b"]


# ------------------------------------------------------------------ o dono, o chamado, a memoria recorrente


def test_o_dono_chega_pelo_traco_e_decisao_de_um_candidato_nao_aprende():
    """Canal do dono: o elogio depois de uma decisao com escolha anda o ator pelo traco (b da acao = taxa x 1 x (1 - p)); depois de uma
    decisao de um candidato so (dormir por exaustao, traco zero), o ator nao muda e so o critico aprende."""
    c = PoliticaCerebroB(CONFIG_PADRAO, CBA, CB, CF)
    L = c._L
    acao = c.agir(replace(_obs((1.0, 0.0, 0.0)), bola=1.0), _Rng(0.3))
    m = c.motivos[-1]
    c.observar(Transicao(Observacao.de_estado(E), acao, Observacao.de_estado(E)))
    c.receber_acao_dono(AcaoUsuario.ELOGIAR, E.tick + 1)
    assert c._theta[L.bA + ACOES.index(acao)] == CBA.taxa_ator * 1.0 * (1.0 - _p(m, acao.value))
    assert c.estado_interno()["aprendizado"]["recompensas"]["elogio"] == 1
    d = PoliticaCerebroB(CONFIG_PADRAO, CBA, None, None)
    dormindo = replace(E, energia=0.1)
    assert d.agir(Observacao.de_estado(dormindo), _Rng(0.5)) is AcaoPet.DORMIR
    d.observar(Transicao(Observacao.de_estado(dormindo), AcaoPet.DORMIR, Observacao.de_estado(dormindo)))
    d.receber_acao_dono(AcaoUsuario.REPREENDER, dormindo.tick + 1)
    assert d._theta == d._theta0 and d._critico[-1] == CBA.taxa_critico * -1.0


def test_o_chamado_paga_pela_latencia_na_decisao_dele():
    """O chamado atendido paga 1 - L / janela na decisao do chamado, pelo gradiente dela (o traco ja andou); o expirado paga
    recompensa_pedido_ignorado."""
    c = PoliticaCerebroB(CONFIG_PADRAO, CBA, None, None)
    sozinho = replace(E, tick_ultimo_cuidado=E.tick - 400)           # abandono: chamar atencao entre os candidatos
    for u in (0.0, 0.2, 0.4, 0.6, 0.8, QUASE_UM):
        acao = c.agir(Observacao.de_estado(sozinho), _Rng(u))
        if acao is AcaoPet.CHAMAR_ATENCAO:
            break
        c._registro_decisao = None
    assert acao is AcaoPet.CHAMAR_ATENCAO
    grad = list(c._registro_decisao["grad"])
    c.observar(Transicao(Observacao.de_estado(sozinho), acao, Observacao.de_estado(sozinho)))
    tick = c._tick_ultima_decisao
    c.receber_acao_dono(AcaoUsuario.ALIMENTAR, tick + 30)
    r = 1.0 - 30 / CBA.janela_latencia_ticks
    assert c._theta == [t + CBA.taxa_ator * r * g for t, g in zip(c._theta0, grad)]
    assert c.estado_interno()["aprendizado"]["recompensas"]["latencia"] == 1


def test_o_estado_oculto_e_memoria_recorrente():
    """A celula guarda o passado: dois B com a mesma observacao agora e observacoes diferentes antes ficam com estados ocultos diferentes;
    com o mesmo passado, iguais."""
    a, b, c = (PoliticaCerebroB(CONFIG_PADRAO, CBA, None, CF) for _ in range(3))
    a.agir(_obs((1.0, 0.0, 0.0)), _Rng(0.5))
    b.agir(_obs((0.0, 1.0, 0.0), estado=replace(E, fome=0.3)), _Rng(0.5))
    c.agir(_obs((1.0, 0.0, 0.0)), _Rng(0.5))
    for x in (a, b, c):
        x._registro_decisao = None
        x.agir(_obs((0.0, 0.0, 1.0)), _Rng(0.5))
    assert a._h == c._h and a._h != b._h


# ------------------------------------------------------------------ pela bancada: o B aprende nas vidas


def test_bancada_o_b_aprende_e_o_p0_nao():
    """Nas vidas de 4 dias: o P0 nunca muda um parametro; o P1, o P2 e o P3 mudam e o aprendido decide parte das decisoes; o P1 nao
    recebe nada do dono e o P3 nada da consequencia."""
    for s in (101, 202):
        p0 = _cerebro(_vida("atencioso", "P0", s, "descasado"))
        assert not p0.pesos_mudaram() and not any(m["sonda"]["aprendido_decidiu"] for m in p0.motivos)
        for braco in ("P1", "P2", "P3"):
            c = _cerebro(_vida("atencioso", braco, s, "descasado"))
            rec = c.estado_interno()["aprendizado"]["recompensas"]
            assert c.pesos_mudaram() and any(m["sonda"]["aprendido_decidiu"] for m in c.motivos)
            assert (rec["elogio"] + rec["repreensao"] > 0) == (braco == "P3")
            assert ("consequencia" in rec) == (braco != "P3")


def test_fabrica_ganchos_e_erros():
    p = fabrica_cerebro_b(CBA, None, CF)(CONFIG_PADRAO)
    for gancho in ("agir", "observar", "estado_interno", "receber_acao_dono", "observar_consequencia", "escolher_fruta",
                   "fruta_comida"):
        assert callable(getattr(p, gancho))
    assert p.cl.escala == S and p.nome == "cerebro_b" and p.ve_mundo
    assert PoliticaCerebroB().escolher_fruta(["a"], {"a": 1.0}, 0.5) is None      # sem ver as frutas, o motor escolhe
    for errado, erro in ((replace(CBA, taxa_ator=1), TypeError), (replace(CBA, n_ocultos=0), ValueError),
                         (replace(CBA, lambda_elegibilidade=1.5), ValueError)):
        with pytest.raises(erro):
            PoliticaCerebroB(None, errado)
    c = PoliticaCerebroB(CONFIG_PADRAO, CBA, None, None)
    acao = c.agir(Observacao.de_estado(replace(E, fome=0.3)), _Rng(0.5))
    with pytest.raises(RuntimeError):                       # o sinal da bancada tem de ser o da transicao
        c.observar_consequencia(Transicao(Observacao.de_estado(E), acao, Observacao.de_estado(E)), 7, CONFIG_CONSEQUENCIA)
