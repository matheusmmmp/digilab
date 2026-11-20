"""V2, CEREBRO-C (docs/TAREFA_V2_CEREBRO_C.md; contrato da secao 1 de docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md): o DigiBrain C,
Fly-like (digilab/policies/cerebro_c.py).

Gates da tarefa: G1; aprendizado desligado = instinto byte a byte; capacidade em [0,9; 1,1] x A; a sonda reproduz a decisao sem o
aprendido; o C aprende algo simples com a consequencia, com a conta conhecida. Mais o contrato da secao 1.1 (ganchos, a entrada da
informacao, a escolha da fruta, os canais). So as sementes dos testes.
"""
from __future__ import annotations

import copy
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import cerebro_c_bancada as cbc  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_CEREBRO_C, CONFIG_CEREBRO_C_APRENDIZ, CONFIG_CONSEQUENCIA,  # noqa: E402
                            CONFIG_FRUTAS_LIGADA, CONFIG_PADRAO)
from digilab.events import FRUTAS, AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import PoliticaInstintoFrutas  # noqa: E402
from digilab.policies import cerebro_c  # noqa: E402
from digilab.policies.cerebro_c import CELULAS_FRUTA, PoliticaCerebroC, fabrica_cerebro_c  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = CONFIG_CEREBRO_C.escala
CF, CB = CONFIG_FRUTAS_LIGADA, CONFIG_BOLA_LIGADA
CC = CONFIG_CEREBRO_C_APRENDIZ
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel", "iguais_frutas")
BANCADA = cbc.BancadaComC(4, 64)
E = Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _obs(presenca: tuple, info: tuple = (0.0, 0.0, 0.0), estado: Estado = E) -> Observacao:
    return replace(Observacao.de_estado(estado), fruta=0.5, frutas_cenario=presenca, info_frutas=info)


def _vida(dono, braco, s, mundo, cerebro="cerebro_c", bancada=BANCADA):
    return bancada.vida(bv.EspecVida(dono, braco, s, None, mundo, cerebro))


def _cerebro(vida):
    return bv.do_braco(vida.motor.politica).cerebro


# ------------------------------------------------------------------ parametros e capacidade (contrato 1.3)


def test_parametros_registrados():
    cerebro_c.validar_parametros_cerebro_c()
    assert CONFIG_CEREBRO_C.aprendizado_ligado is False and CC.aprendizado_ligado is True


def test_capacidade_dentro_da_faixa_do_a():
    """Os parametros aprendiveis do C (todas as sinapses de saida, os dois compartimentos, todas as acoes, mais a escolha da fruta)
    ficam em [0,9; 1,1] x os do A no ponto da K2 (T3 com o w0_info, que o A tem no experimento maior: 763)."""
    c = PoliticaCerebroC(None, CC, None, CF)
    a = PoliticaLobos(None, replace(bv.cfg_lobos_do_ponto("T3"), w0_info=S // 2), None, CF)
    assert a.n_pesos() == 763
    assert c.n_pesos() == c.estado_interno()["parametros_aprendidos"] == (22 + 15 + 16) * 7 * 2 + 5 * 2 == 752
    assert 0.9 <= c.n_pesos() / a.n_pesos() <= 1.1
    # a contagem nao depende do mundo nem da chave (a estrutura e herdada)
    assert PoliticaCerebroC().n_pesos() == PoliticaCerebroC(None, CC, CB, None).n_pesos() == 752


# ------------------------------------------------------------------ G2: aprendizado desligado = instinto byte a byte


@pytest.mark.parametrize("mundo", MUNDOS_FRUTAS + ("bola",))
def test_aprendizado_desligado_e_o_instinto_pela_bancada(mundo):
    """O P0 do C (aprendizado desligado) e o P0 do instinto que ve o mundo, byte a byte (log, estado, acoes, rngs, frutas)."""
    for dono in DONOS:
        for s in (101, 202):
            c = _vida(dono, "P0", s, mundo).motor
            i = _vida(dono, "P0", s, mundo, "instinto").motor
            assert bv.resumo_motor(c) == bv.resumo_motor(i)


def test_aprendizado_desligado_no_padrao_e_nos_bracos_que_aprendem():
    """No mundo padrao, o P0 do C e o dos lobos (que e o instinto, gate da L0). Com o aprendizado desligado o C e o instinto em
    qualquer braco: o P1 e o P3 do C desligado vivem a vida do P0 do instinto."""
    for dono in DONOS:
        assert bv.resumo_motor(_vida(dono, "P0", 101, "padrao").motor) == bv.resumo_motor(_vida(dono, "P0", 101, "padrao", "lobos").motor)
    desligado = cbc.BancadaComC(4, 64, cfg_cerebro_c=CONFIG_CEREBRO_C)
    for braco in ("P1", "P3"):
        for mundo in ("descasado", "padrao"):
            ref = "instinto" if mundo != "padrao" else "lobos"
            c = _vida("atencioso", braco, 202, mundo, bancada=desligado).motor
            i = _vida("atencioso", "P0", 202, mundo, ref).motor
            assert bv.resumo_motor(c) == bv.resumo_motor(i)


@pytest.mark.parametrize("com_mundo", (False, True))
def test_aprendizado_desligado_decisao_a_decisao(com_mundo):
    """3000 observacoes aleatorias (todas as regras): a mesma acao e o mesmo estado da rng do instinto."""
    gen = random.Random(7)
    c = PoliticaCerebroC(None, CONFIG_CEREBRO_C, CB if com_mundo else None, CF if com_mundo else None)
    i = PoliticaInstintoFrutas(None, CB, CF) if com_mundo else PoliticaInstinto()
    r1, r2 = random.Random(11), random.Random(11)
    regras = set()
    for _ in range(3000):
        v = tuple(gen.random() for _ in range(6)) + (float(gen.random() < 0.3), gen.random())
        obs = Observacao(vetor_estado=v, ticks_desde_cuidado=gen.randrange(0, 1200), total_cuidados=0)
        if com_mundo:
            pres = tuple(float(gen.random() < 0.4) for _ in FRUTAS)
            obs = replace(obs, bola=float(gen.random() < 0.3), fruta=gen.random() if any(pres) else 0.0, frutas_cenario=pres)
        assert c.agir(obs, r1) is i.agir(obs, r2)
        assert r1.getstate() == r2.getstate()
        regras.add(c.ultima_regra)
    assert len(regras) >= (9 if com_mundo else 7)


# ------------------------------------------------------------------ G1


@pytest.mark.parametrize("mundo", ("descasado", "mutavel", "padrao"))
def test_g1_replay_bit_a_bit(mundo):
    """Toda vida do C (P0 a P3; P2, P2e e P2a so nas frutas) e o acoplado so cuidado, rejogados do texto do log: tudo igual, estado
    interno incluido (a BancadaComC confere o replay em toda vida; aqui de novo, do texto)."""
    bracos = ("P0", "P1", "P3") + (("P2", "P2e", "P2a") if mundo != "padrao" else ())
    for dono in ("atencioso", "aleatorio"):
        for braco in bracos:
            v = _vida(dono, braco, 303, mundo)
            BANCADA.conferir_replay(v, v.motor.log.para_jsonl())
            assert bv._interno(BANCADA.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)) == bv._interno(v.motor)
    if mundo != "padrao":
        origem = _vida("atencioso", "P3", 303, mundo)
        a = BANCADA.acoplar(origem, "P1", "sem_ensino")
        BANCADA.conferir_replay(a)


def test_os_blocos_n6_e_n7_ficam_fora():
    for braco in ("MR", "P1+ped"):
        with pytest.raises(ValueError):
            _vida("atencioso", braco, 101, "descasado")


# ------------------------------------------------------------------ a sonda do aprendido (contrato 1.1)


def _treinado(s: int = 202):
    """Um C treinado de verdade: o cerebro de uma vida P3 do descasado (o dono ensina todos os circuitos)."""
    return _cerebro(_vida("atencioso", "P3", s, "descasado"))


def test_sonda_reproduz_a_decisao_sem_o_aprendido():
    """Para observacoes aleatorias, a acao da sonda (`acao_sem_aprendido`) e a que um gemeo com as sinapses zeradas toma com o mesmo u;
    e a escolha da fruta sem o aprendido e a do gemeo zerado. O aprendido decide em parte das decisoes (nao e sempre o prior)."""
    c = _treinado()
    assert c.pesos_mudaram()
    zero = copy.deepcopy(c)
    for circ in zero._sinapses.values():
        for comp in circ.values():
            for w in comp.values():
                w[:] = [0] * len(w)
    for comp in zero._sinapses_fruta.values():
        comp[:] = [0] * len(comp)
    assert not zero.pesos_mudaram()
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
        decidiu += m["sonda"]["aprendido_decidiu"]
    assert 0 < decidiu < 1500


def test_sonda_da_fruta_reproduz_a_escolha_sem_o_aprendido():
    """A escolha da fruta sem o aprendido (e sem a informacao) e a de um gemeo zerado (e sem informacao) com o mesmo u."""
    c = _treinado()
    c._sinapses_fruta["aversivo"][CELULAS_FRUTA.index("id_a")] = 300      # o treino da escolha precisa de duas frutas; aqui, direto
    c._sinapses_fruta["apetitivo"][CELULAS_FRUTA.index("info_bem")] = 200
    gen = random.Random(9)
    for _ in range(400):
        presentes = [f for f in FRUTAS if gen.random() < 0.7] or ["b"]
        info = tuple(gen.choice((-1.0, 0.0, 1.0)) for _ in FRUTAS)
        inc = {f: 0.05 + gen.random() for f in presentes}
        uf = gen.random()
        c._info_na_decisao = info
        c._registro_decisao = {"acao": AcaoPet.COMER, "candidatos": (AcaoPet.COMER,), "regra": "fruta_no_cenario",
                               "ativas": {k: [] for k in cerebro_c.CIRCUITOS}}
        c.motivos.append({"acao": "comer"})
        esc = c.escolher_fruta(presentes, inc, uf)
        sonda = c.motivos[-1]["fruta"]["sonda"]
        zero = PoliticaCerebroC(None, CC, None, CF)
        zero._info_na_decisao = info
        zero._registro_decisao = {"acao": AcaoPet.COMER, "candidatos": (AcaoPet.COMER,), "regra": "fruta_no_cenario",
                                  "ativas": {k: [] for k in cerebro_c.CIRCUITOS}}
        assert sonda["escolha_sem_aprendido"] == zero.escolher_fruta(presentes, inc, uf)
        sem_info = PoliticaCerebroC(None, CC, None, CF)
        sem_info._sinapses_fruta = copy.deepcopy(c._sinapses_fruta)
        sem_info._sinapses_fruta["apetitivo"][CELULAS_FRUTA.index("info_bem")] = 0
        sem_info._info_na_decisao = (0.0, 0.0, 0.0)
        sem_info._registro_decisao = dict(zero._registro_decisao)
        sem_info._registro_decisao.pop("fruta", None)
        assert sonda["escolha_sem_info"] == sem_info.escolher_fruta(presentes, inc, uf)
        assert sonda["aprendido_decidiu"] == (sonda["escolha_sem_aprendido"] != esc)


# ------------------------------------------------------------------ o C aprende com a consequencia (a conta conhecida)


def _comer_so(c: PoliticaCerebroC, fruta: str, delta_humor: float) -> None:
    """Uma decisao de comer com so `fruta` no cenario, pelo caminho do motor (agir, consequencia, escolha, fruta comida)."""
    pres = tuple(1.0 if f == fruta else 0.0 for f in FRUTAS)
    assert c.agir(_obs(pres), _Rng(1.0 - 1e-12)) is AcaoPet.COMER and c.ultima_regra == "fruta_no_cenario"
    t = Transicao(Observacao.de_estado(E), AcaoPet.COMER, Observacao.de_estado(E))
    c.observar_consequencia(t, 0, CONFIG_CONSEQUENCIA)
    assert c.escolher_fruta([fruta], {fruta: 0.5}, 0.5) == fruta
    c.fruta_comida(fruta, Observacao.de_estado(replace(E, humor=E.humor + delta_humor)))


def _peso_comer(c: PoliticaCerebroC, pres: tuple) -> dict:
    c.agir(_obs(pres), _Rng(0.0))
    return c.motivos[-1]["pesos"]


def test_aprende_a_nao_comer_a_fruta_ruim_sozinha_com_a_conta():
    """A fruta 'a' derruba o humor 0,8 -> 0,7. A E2 da o canal humor -204 (ganho 4: falta 205 -> 307, (205^2 - 307^2) x 4 / 1024) e os
    outros canais zero (fome ja cheia). O humor vai ao circuito objeto: as duas celulas ativas (fruta_a e fome:2*fruta_a) ganham, no
    compartimento aversivo de COMER, div_arred(64 x 204, 1024) = 13 cada. O peso de comer com so 'a' cai exatamente 26/1024; com so
    'b', nada muda; o corpo, o social e a escolha da fruta (uma fruta so) nao aprendem."""
    c = PoliticaCerebroC(CONFIG_PADRAO, CC, None, CF)
    antes_a, antes_b = _peso_comer(c, (1.0, 0.0, 0.0)), _peso_comer(c, (0.0, 1.0, 0.0))
    assert antes_a == antes_b and antes_a["comer"] == 3.0
    _comer_so(c, "a", -0.1)
    ix = c._indice["objeto"]
    av = c._sinapses["objeto"]["aversivo"][AcaoPet.COMER]
    assert av[ix["fruta_a"]] == av[ix["fome:2*fruta_a"]] == 13 and sum(av) == 26
    assert c.estado_interno()["aprendizado"]["canais"]["por_canal"] == {"fome": 0, "higiene": 0, "energia": 0, "humor": -204}
    for circ in ("corpo", "social"):
        assert not any(w for comp in c._sinapses[circ].values() for ws in comp.values() for w in ws)
    assert not any(c._sinapses_fruta["aversivo"]) and not any(c._sinapses_fruta["apetitivo"])
    depois_a, depois_b = _peso_comer(c, (1.0, 0.0, 0.0)), _peso_comer(c, (0.0, 1.0, 0.0))
    assert depois_a["comer"] == 3.0 - 26 / 1024 and depois_b == antes_b
    assert {k: v for k, v in depois_a.items() if k != "comer"} == {k: v for k, v in antes_a.items() if k != "comer"}
    for _ in range(5):                                       # tendencia: cada consumo ruim tira mais 26/1024
        _comer_so(c, "a", -0.1)
    assert _peso_comer(c, (1.0, 0.0, 0.0))["comer"] == 3.0 - 6 * 26 / 1024


def test_fruta_boa_vai_ao_apetitivo_e_a_memoria_de_comer_depende_da_fome():
    """A fruta boa (humor +0,1) potencia o apetitivo de COMER; esse apetitivo so se expressa na medida da fome (gate = S - arred(fome
    x S)): com o pet saciado (fome 1,0) o peso nao muda; com fome 0,5 ele sobe a metade."""
    c = PoliticaCerebroC(CONFIG_PADRAO, CC, None, CF)
    for _ in range(4):
        _comer_so(c, "a", +0.1)
    ix = c._indice["objeto"]
    app = c._sinapses["objeto"]["apetitivo"][AcaoPet.COMER]
    assert app[ix["fruta_a"]] > 0 and app[ix["fome:2*fruta_a"]] == app[ix["fruta_a"]]
    assert _peso_comer(c, (1.0, 0.0, 0.0))["comer"] == 3.0          # saciado: a memoria apetitiva nao se expressa
    meio = replace(E, fome=0.5)
    c.agir(_obs((1.0, 0.0, 0.0), estado=meio), _Rng(0.0))
    # fome 0,5 na faixa 2 (as celulas treinadas); gate = 512: L = div_arred(2 x app x 512, 1024) = app
    assert c.motivos[-1]["circuitos"]["objeto"]["comer"] == app[ix["fruta_a"]] / 1024


def test_a_informacao_entra_na_escolha_da_fruta():
    """Contrato 1.1: a entrada da informacao. A fruta informada 'mal' que faz mal ensina a celula info_mal (aversivo); depois, numa
    escolha entre duas frutas, a fruta com 'mal' perde peso, mesmo outra fruta. Sem informacao (w0_info 0, celulas zeradas), a escolha
    e a de sempre."""
    c = PoliticaCerebroC(CONFIG_PADRAO, CC, None, CF)
    info = (-1.0, 0.0, 0.0)
    for _ in range(3):
        assert c.agir(_obs((1.0, 1.0, 0.0), info), _Rng(1.0 - 1e-12)) is AcaoPet.COMER
        t = Transicao(Observacao.de_estado(E), AcaoPet.COMER, Observacao.de_estado(E))
        c.observar_consequencia(t, 0, CONFIG_CONSEQUENCIA)
        assert c.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, 0.0) == "a"
        c.fruta_comida("a", Observacao.de_estado(replace(E, humor=E.humor - 0.1)))
    av = c._sinapses_fruta["aversivo"]
    assert av[CELULAS_FRUTA.index("id_a")] == av[CELULAS_FRUTA.index("info_mal")] == 3 * 13
    c.agir(_obs((1.0, 1.0, 0.0), (0.0, -1.0, 0.0)), _Rng(1.0 - 1e-12))
    c.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, 0.5)
    pesos = c.motivos[-1]["fruta"]["pesos"]
    assert pesos["b"] == (1024 - 39) / 1024 * 0.5 and pesos["a"] == (1024 - 39) / 1024 * 0.5
    # a resposta inata (w0_info) tambem existe: com w0_info = S/2 e sem aprendizado, 'mal' tira 0,5 do peso da fruta
    inata = PoliticaCerebroC(CONFIG_PADRAO, replace(CONFIG_CEREBRO_C, w0_info=S // 2), None, CF)
    inata.agir(_obs((1.0, 1.0, 0.0), (-1.0, 0.0, 0.0)), _Rng(1.0 - 1e-12))
    inata.escolher_fruta(["a", "b"], {"a": 0.8, "b": 0.8}, 0.5)
    assert inata.motivos[-1]["fruta"]["pesos"] == {"a": 0.8 - 0.5, "b": 0.8}


def test_o_dono_chega_a_todos_os_circuitos_da_decisao():
    """Canal do dono: o elogio depois de uma decisao com escolha potencia, para a acao executada, todas as celulas ativas dos tres
    circuitos (div_arred(64 x 1024, 1024) = 64 cada); a bronca, o aversivo. Decisao com um candidato so nao aprende."""
    c = PoliticaCerebroC(CONFIG_PADRAO, CC, CB, CF)
    obs = replace(_obs((1.0, 0.0, 0.0)), bola=1.0)
    acao = c.agir(obs, _Rng(0.3))
    ativas = c.ativas(obs)
    c.observar(Transicao(Observacao.de_estado(E), acao, Observacao.de_estado(E)))
    c.receber_acao_dono(AcaoUsuario.ELOGIAR, E.tick + 1)
    for circ in cerebro_c.CIRCUITOS:
        app = c._sinapses[circ]["apetitivo"][acao]
        assert [app[k] for k in ativas[circ]] == [64] * len(ativas[circ]) and sum(app) == 64 * len(ativas[circ])
    assert len(ativas["objeto"]) == 4                         # bola, energia*bola, fruta_a, fome*fruta_a
    dormindo = replace(E, energia=0.1)                        # sono por exaustao: um candidato so
    d = PoliticaCerebroC(CONFIG_PADRAO, CC, None, None)
    assert d.agir(Observacao.de_estado(dormindo), _Rng(0.5)) is AcaoPet.DORMIR
    d.observar(Transicao(Observacao.de_estado(dormindo), AcaoPet.DORMIR, Observacao.de_estado(dormindo)))
    d.receber_acao_dono(AcaoUsuario.REPREENDER, dormindo.tick + 1)
    assert not d.pesos_mudaram()


def test_os_canais_somam_o_escalar_e_falham_alto():
    """A soma dos canais de uma decisao e o f_S escalar que a bancada entrega; se nao for, falha alto."""
    c = PoliticaCerebroC(CONFIG_PADRAO, CC, None, None)
    antes, depois = replace(E, fome=0.3, energia=0.6), replace(E, fome=0.6, energia=0.55)
    acao = c.agir(Observacao.de_estado(antes), _Rng(0.99))
    t = Transicao(Observacao.de_estado(antes), acao, Observacao.de_estado(depois))
    from digilab.policies.lobos import sinal_homeostatico
    f = sinal_homeostatico(t, S, CONFIG_CONSEQUENCIA)
    with pytest.raises(RuntimeError):
        copy.deepcopy(c).observar_consequencia(t, f + 1, CONFIG_CONSEQUENCIA)
    c.observar_consequencia(t, f, CONFIG_CONSEQUENCIA)
    assert sum(c.estado_interno()["aprendizado"]["canais"]["por_canal"].values()) == f


# ------------------------------------------------------------------ pela bancada: o C aprende nas vidas


def test_bancada_o_c_aprende_e_o_p0_nao():
    """Nas vidas de 4 dias: o P0 nunca muda uma sinapse; o P1, o P2 e o P3 mudam e o aprendido decide parte das decisoes; o P1 nao
    recebe nada do dono (o canal dono fica vazio) e o P3 nada da consequencia."""
    for s in (101, 202):
        p0 = _cerebro(_vida("atencioso", "P0", s, "descasado"))
        assert not p0.pesos_mudaram() and not any(m["sonda"]["aprendido_decidiu"] for m in p0.motivos)
        for braco in ("P1", "P2", "P3"):
            c = _cerebro(_vida("atencioso", braco, s, "descasado"))
            canais = c.estado_interno()["aprendizado"]["canais"]["por_canal"]
            assert c.pesos_mudaram() and any(m["sonda"]["aprendido_decidiu"] for m in c.motivos)
            assert ("dono" in canais) == (braco == "P3")
            assert ("humor" in canais) == (braco != "P3")


def test_fabrica_e_ganchos():
    p = fabrica_cerebro_c(CC, None, CF)(CONFIG_PADRAO)
    for gancho in ("agir", "observar", "estado_interno", "receber_acao_dono", "observar_consequencia", "escolher_fruta",
                   "fruta_comida"):
        assert callable(getattr(p, gancho))
    assert p.cl.escala == S and p.nome == "cerebro_c" and p.ve_mundo
    assert PoliticaCerebroC().escolher_fruta(["a"], {"a": 1.0}, 0.5) is None      # sem ver as frutas, o motor escolhe
    with pytest.raises(ValueError):
        PoliticaCerebroC(None, replace(CC, passo=0))
    with pytest.raises(TypeError):
        PoliticaCerebroC(None, replace(CC, teto=4.0))
