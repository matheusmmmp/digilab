"""V2, mundo fisico, etapa 3 (MUNDO-CEREBROS; docs/TAREFA_V2_MUNDO_FISICO.md, secoes 8 e 9): o instinto do mundo, a regra que liga a
percepcao as entradas do cerebro A, os ganchos `escolher_alvo` e `consequencia_mundo` nos lobos, atras da chave (cfg_mundo), e a
PoliticaComMotivo repassando os ganchos novos. Mais a revisao dos empates do cheiro (experiments/analisar_empates_cheiro.py).

G2 (chave desligada = as vidas de hoje byte a byte): os lobos so mudam com cfg_mundo ligada; os gabaritos de sempre conferem o resto na
suite (tests/test_mundo.py, test_gabaritos_mundo_corpo.py, test_cerebro_n6_n7.py, test_canais_reforco.py, test_bancada_*.py). Aqui: os
lobos com o mundo e o aprendizado desligado sao o instinto do mundo byte a byte; o instinto do mundo sem percepcao e o de hoje. So as
sementes dos testes.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import analisar_empates_cheiro as aec  # noqa: E402
import bancada_v2 as bv  # noqa: E402
from digilab.config import (CONFIG_BOLA, CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_FRUTAS, CONFIG_FRUTAS_LIGADA,  # noqa: E402
                            CONFIG_LOBOS, CONFIG_MUNDO, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, AcaoPet  # noqa: E402
from digilab.expressao import FATORES_VIDA  # noqa: E402
from digilab.instinto_mundo import (PoliticaInstintoMundo, comida_boa_vista, entradas_mundo, para_onde_comer)  # noqa: E402
from digilab.motivo import PoliticaComMotivo  # noqa: E402
from digilab.mundo import (ACOES_COM_ALVO, ESTILOS_LUGAR, DonoComLugar, PercepcaoMundo, direcao_do_cheiro,  # noqa: E402
                           fabricas_mundo, reproduzir_mundo, simular_vida_mundo)
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import (ACOES_COM_ALVO_MUNDO, PoliticaLobos, _RngSonda, sinal_homeostatico,  # noqa: E402
                                    sinal_homeostatico_fruta)
from digilab.policy import Observacao, PoliticaInstinto, Transicao  # noqa: E402

CM = CONFIG_MUNDO_LIGADA
SEMENTES = (101, 202)                     # so dos testes
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
S = CONFIG_LOBOS.escala
CL_T3 = bv.cfg_lobos_do_ponto("T3")
TIPOS_VISTOS = ("racao", "a", "b", "c", "racao_podre", "a_podre", "b_podre", "bola")


# ================================================================== ajudas
def perc(vistos=(), cheiro=0, direcao=0, x=200, y=240) -> PercepcaoMundo:
    vs = tuple(sorted(((i + 1 if t != "bola" else 0), t, 5 * (i + 1), 0, 5 * (i + 1)) for i, t in enumerate(vistos)))
    return PercepcaoMundo(x, y, 0, tuple(sorted(vs, key=lambda v: (v[4], v[1], v[0]))), cheiro, direcao, None)


def obs_de(fome=0.6, higiene=0.8, energia=0.7, humor=0.5, saude=1.0, sujeira=0.0, dormindo=0.0, hora=0.5, ticks=0, mundo=None):
    return Observacao(vetor_estado=(fome, higiene, energia, humor, saude, sujeira, dormindo, hora), ticks_desde_cuidado=ticks,
                      total_cuidados=0, mundo=mundo)


def obs_aleatoria(rng: random.Random, com_mundo: bool = True) -> Observacao:
    v = tuple(rng.random() for _ in range(8))
    v = v[:6] + (float(rng.random() < 0.2),) + v[7:]
    mundo = None
    if com_mundo:
        vistos = rng.sample(TIPOS_VISTOS, rng.randint(0, 4))
        cheiro = rng.choice((0, 0, rng.randint(1, 120)))
        mundo = perc(vistos, cheiro, rng.randint(0, 8) if cheiro else 0)
    return Observacao(vetor_estado=v, ticks_desde_cuidado=rng.choice((0, 30, 200, 500)), total_cuidados=0, mundo=mundo)


def vida(fab, dono="atencioso", estilo="perto", semente=101, dias=3, efeito=None, cm=CM):
    fp, fm = fabricas_mundo(cm, fab, efeito_frutas=efeito)
    dono_lugar = DonoComLugar(criar_dono(dono), estilo, semente, dono, cm)
    return simular_vida_mundo(dono, dono_lugar, fp(CONFIG_PADRAO), semente, dias, 16 * dias, fm, rotulo_dono=dono), fp, fm


def resumo(m, politica: bool = False, sem_regra: bool = False) -> str:
    """sha256 de tudo o que a vida guarda. `sem_regra`: sem o campo `regra` das decisoes do mundo, que o motor le da politica de
    cima e a PoliticaComMotivo nao repassa (sai None; a mesma convencao de experiments/run_revisao_aprendiz.py)"""
    mundo = m.resumo_mundo_fisico()
    if sem_regra:
        mundo = {**mundo, "decisoes": [{k: v for k, v in d.items() if k != "regra"} for d in mundo["decisoes"]]}
    d = {"log": m.log.para_jsonl(), "estado": m.estado(), "estado_bruto": repr(m._estado), "acoes": m.acoes_recentes(10**9),
         "rng_ambiente": m._rng_ambiente.getstate(), "rng_politica": m._rng_politica.getstate(), "mundo": mundo}
    if politica:
        d["politica"] = m.politica.estado_interno()
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=repr).encode()).hexdigest()


def instinto(cfg=None):
    return PoliticaInstintoMundo(cfg or CONFIG_PADRAO)


def lobos_mundo(cl=CONFIG_LOBOS):
    return lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=CM)


def braco(rotulo: str, cl=CL_T3, cc=CONFIG_CONSEQUENCIA):
    return lambda cfg=None: bv.PoliticaDoBraco(PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=CM), bv.braco_de(rotulo), cc)


# ================================================================== a regra que liga a percepcao as entradas do cerebro A
def test_regra_das_entradas_do_cerebro_a():
    assert entradas_mundo(None) == (0.0, 0.0)
    assert entradas_mundo(perc()) == (0.0, 0.0)
    assert entradas_mundo(perc(["bola"])) == (1.0, 0.0)
    for t in ("racao",) + FRUTAS:
        assert entradas_mundo(perc([t])) == (0.0, 1.0)
        assert entradas_mundo(perc([t, "bola", t + "_podre" if t != "racao" else "a_podre"])) == (1.0, 1.0)
    assert entradas_mundo(perc(["racao_podre", "a_podre"])) == (0.0, 0.0)      # a podre nao conta
    assert entradas_mundo(perc([], cheiro=80, direcao=3)) == (0.0, 0.0)          # cheiro nao e comida vista
    assert lb.ENTRADAS_MUNDO == ("bola", "fruta")


def test_acoes_com_alvo_iguais_as_do_motor():
    assert ACOES_COM_ALVO_MUNDO == ACOES_COM_ALVO


# ================================================================== o instinto do mundo
def test_instinto_sem_percepcao_e_o_de_hoje():
    """sem obs.mundo (nada visto, nada cheirado) o instinto do mundo e o PoliticaInstinto, decisao a decisao, com a mesma rng"""
    rng_obs = random.Random(11)
    novo, hoje = PoliticaInstintoMundo(CONFIG_PADRAO), PoliticaInstinto(CONFIG_PADRAO)
    r1, r2 = random.Random(22), random.Random(22)
    for _ in range(3000):
        o = obs_aleatoria(rng_obs, com_mundo=False)
        assert novo.agir(o, r1) is hoje.agir(o, r2)
        assert novo.ultima_regra == hoje.ultima_regra and r1.getstate() == r2.getstate()


@pytest.mark.parametrize("vistos,cheiro,direcao,esperada", [
    (["a"], 0, 0, AcaoPet.COMER), (["racao"], 0, 0, AcaoPet.COMER), (["bola", "b"], 30, 2, AcaoPet.COMER),
    ([], 40, 5, AcaoPet.COMER),                                             # vai ao cheiro
    ([], 40, 0, AcaoPet.CHAMAR_ATENCAO),                                    # cheiro sem direcao e nada visto: chama (desvio registrado)
    (["a_podre", "racao_podre"], 0, 0, AcaoPet.CHAMAR_ATENCAO), (["bola"], 0, 0, AcaoPet.CHAMAR_ATENCAO),
    ([], 0, 0, AcaoPet.CHAMAR_ATENCAO),
])
def test_fome_urgente_vai_a_comida_vista_ou_ao_cheiro(vistos, cheiro, direcao, esperada):
    pol = PoliticaInstintoMundo(CONFIG_PADRAO)
    rng = random.Random(33)
    antes = rng.getstate()
    assert pol.agir(obs_de(fome=0.1, mundo=perc(vistos, cheiro, direcao)), rng) is esperada
    assert pol.ultima_regra == "pedido_necessidade" and rng.getstate() == antes      # deterministica: nenhuma rng


def test_fome_urgente_higiene_e_sono():
    pol, rng = PoliticaInstintoMundo(CONFIG_PADRAO), random.Random(1)
    comida = perc(["a"])
    assert pol.agir(obs_de(fome=0.6, higiene=0.1, mundo=comida), rng) is AcaoPet.CHAMAR_ATENCAO   # a higiene continua chamando
    assert pol.agir(obs_de(fome=0.1, higiene=0.1, mundo=comida), rng) is AcaoPet.COMER            # as duas baixas: come
    assert pol.agir(obs_de(fome=0.1, energia=0.1, mundo=comida), rng) is AcaoPet.DORMIR           # o sono vem antes
    assert pol.ultima_regra == "sono_exaustao"
    assert para_onde_comer(perc([], 1, 7)) and not para_onde_comer(perc(["bola"], 1, 0))
    assert comida_boa_vista(perc(["c"])) and not comida_boa_vista(perc(["c_podre"]))


def _pesos(pol, o) -> tuple[str, list, list]:
    sonda = _RngSonda(0.0)
    pol.agir(o, sonda)
    return pol.ultima_regra, *sonda.escolha


@pytest.mark.parametrize("vistos,regra,brincar_extra,comer", [
    ([], "tempo_livre", 0.0, None), (["bola"], "bola_no_cenario", 6.0, None), (["racao"], "fruta_no_cenario", 0.0, 6.0),
    (["bola", "a"], "fruta_no_cenario", 6.0, 6.0), (["a_podre"], "tempo_livre", 0.0, None),
])
def test_tempo_livre_com_o_que_ve(vistos, regra, brincar_extra, comer):
    """os mesmos w do N4 e da A1 (6 e 6), a mesma chamada de rng.choices, comer no fim da lista"""
    assert CONFIG_BOLA.w_bola == 6.0 and CONFIG_FRUTAS.w_fruta == 6.0
    pol = PoliticaInstintoMundo(CONFIG_PADRAO)
    e, h = 0.7, 0.5
    r, pop, pesos = _pesos(pol, obs_de(energia=e, humor=h, mundo=perc(vistos, 50, 1)))
    assert r == regra
    base = [AcaoPet.OCIOSO, AcaoPet.EXPLORAR, AcaoPet.BRINCAR, AcaoPet.CHAMAR_ATENCAO]
    esperado = [3.0, 2.0 + 2.0 * e, 1.0 + 3.0 * h + brincar_extra if brincar_extra else 1.0 + 3.0 * h, 1.0]
    if comer is not None:
        base, esperado = base + [AcaoPet.COMER], esperado + [comer]
    assert pop == base and pesos == esperado
    assert pol.termo_mundo(regra, obs_de(mundo=perc(vistos))) == {"bola_no_cenario": brincar_extra,
                                                                   "fruta_no_cenario": comer or 0.0}.get(regra, 0.0)


def test_fome_moderada_igual_a_de_hoje():
    pol, hoje = PoliticaInstintoMundo(CONFIG_PADRAO), PoliticaInstinto(CONFIG_PADRAO)
    for u in (0.1, 0.49, 0.5, 0.9):
        o = obs_de(fome=0.3, mundo=perc(["a", "bola"], 60, 3))
        assert pol.agir(o, _RngSonda(u)) is hoje.agir(replace(o, mundo=None), _RngSonda(u))
        assert pol.ultima_regra == "fome_moderada"


def test_sem_explorar_o_peso_do_explorar_vai_para_o_ocioso():
    pol = PoliticaInstintoMundo(CONFIG_PADRAO, sem_explorar=True)
    for vistos in ([], ["bola", "a"]):
        _, pop, pesos = _pesos(pol, obs_de(energia=0.7, humor=0.5, mundo=perc(vistos)))
        assert AcaoPet.EXPLORAR not in pop and pop[0] is AcaoPet.OCIOSO
        assert pesos[0] == 3.0 + (2.0 + 2.0 * 0.7)
    with pytest.raises(TypeError):
        PoliticaInstintoMundo(CONFIG_PADRAO, sem_explorar=1)
    with pytest.raises(ValueError):
        PoliticaInstintoMundo(CONFIG_PADRAO, replace(CONFIG_BOLA, w_bola=-1.0))


def test_p0z_nunca_explora_e_ve_as_mesmas_quedas():
    for dono in ("atencioso", "aleatorio"):
        p0, _, _ = vida(instinto, dono, dias=4)
        p0z, _, _ = vida(lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO, sem_explorar=True), dono, dias=4)
        acoes = [a for _, a in p0z.motor.acoes_recentes(10**9)]
        assert AcaoPet.EXPLORAR not in acoes and AcaoPet.EXPLORAR in [a for _, a in p0.motor.acoes_recentes(10**9)]
        quedas = [(q["tick"], q["arvore"], q["sorteadas"], q["pontos"]) for q in p0.motor.quedas]
        assert quedas == [(q["tick"], q["arvore"], q["sorteadas"], q["pontos"]) for q in p0z.motor.quedas]


@pytest.mark.parametrize("sem_explorar", [False, True])
def test_g1_instinto_do_mundo(sem_explorar):
    fab = (lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO, sem_explorar=sem_explorar))
    for semente in SEMENTES:
        v, fp, fm = vida(fab, "relapso", "longe", semente, dias=4)
        r = reproduzir_mundo(v.motor.log, fp, CONFIG_PADRAO, semente, fm)
        assert resumo(r, True) == resumo(v.motor, True)


def test_a_fome_urgente_come_na_vida():
    """numa vida longe, o pet com fome urgente e para onde ir vai comer; sem para onde ir, chama"""
    v, _, _ = vida(instinto, "atencioso", "longe", 101, dias=3)
    urgentes = [d for d in v.motor.decisoes_mundo if d["regra"] == "pedido_necessidade"]
    assert {d["acao"] for d in urgentes} == {"comer", "chamar_atencao"}
    assert any(d["comeu"] is not None for d in urgentes if d["acao"] == "comer")


# ================================================================== os lobos no mundo (o cerebro A)
@pytest.mark.parametrize("dono", DONOS)
def test_lobos_sem_aprendizado_sao_o_instinto_do_mundo_byte_a_byte(dono):
    """o G2 dos lobos no mundo: o prior repete o instinto do mundo (log, estado, acoes, rngs e tudo o que o mundo guarda)"""
    for estilo in ESTILOS_LUGAR:
        for semente in SEMENTES:
            a, _, _ = vida(instinto, dono, estilo, semente)
            b, _, _ = vida(lobos_mundo(), dono, estilo, semente)
            assert resumo(a.motor) == resumo(b.motor), (dono, estilo, semente)


def test_lobos_decisao_a_decisao_e_a_percepcao():
    rng_obs = random.Random(44)
    ins, lob = PoliticaInstintoMundo(CONFIG_PADRAO), PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM)
    r1, r2 = random.Random(55), random.Random(55)
    regras = set()
    for _ in range(3000):
        o = obs_aleatoria(rng_obs)
        assert lob.agir(o, r2) is ins.agir(o, r1)
        assert r1.getstate() == r2.getstate() and lob.ultima_regra == ins.ultima_regra
        assert tuple(lob.percepcao(o)[-2:]) == entradas_mundo(o.mundo)
        regras.add(lob.ultima_regra)
    assert regras >= {"pedido_necessidade", "fome_moderada", "tempo_livre", "bola_no_cenario", "fruta_no_cenario", "abandono"}


def test_lobos_do_mundo_prior_e_chave():
    lob = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM)
    assert lob.ve_mundo_fisico and lob.ve_mundo and lob.entradas == lb.ENTRADAS + lb.ENTRADAS_MUNDO
    assert lob.n_pesos() == len(lb.REGRAS + lb.REGRAS_MUNDO) * len(AcaoPet) * len(lob.entradas)
    ei = lob.estado_interno()
    assert "pesos_fruta" not in ei and "pesos_comer_fruta" not in ei
    assert ei["pesos_prior"]["pedido_necessidade"]["comer"][0] == S
    assert ei["pesos_prior"]["fruta_no_cenario"]["comer"][lob.entradas.index("fruta")] == 6 * S
    assert ei["pesos_prior"]["bola_no_cenario"]["brincar"][lob.entradas.index("bola")] == 6 * S
    # a chave desligada: os lobos de hoje
    hoje, desligada = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS), PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CONFIG_MUNDO)
    assert json.dumps(hoje.estado_interno()) == json.dumps(desligada.estado_interno()) and not desligada.ve_mundo_fisico
    # o mundo substitui o cenario do N4 e da A1
    with pytest.raises(ValueError, match="substitui"):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_mundo=CM)
    with pytest.raises(ValueError, match="substitui"):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_bola=CONFIG_BOLA_LIGADA, cfg_mundo=CM)
    with pytest.raises(RuntimeError, match="cenario"):
        lob.percepcao(replace(obs_de(mundo=perc()), fruta=1.0))


def test_p1_com_ganho_zero_e_o_p0():
    cc0 = replace(CONFIG_CONSEQUENCIA, ganho=0)
    for dono in ("atencioso", "aleatorio"):
        a, _, _ = vida(instinto, dono, "comedouro")
        b, _, _ = vida(braco("P1", cc=cc0), dono, "comedouro")
        assert resumo(a.motor) == resumo(b.motor)


@pytest.mark.parametrize("rotulo,canais", [("P1", False), ("P1", True), ("P3", False), ("P0", False)])
def test_g1_lobos_do_mundo(rotulo, canais):
    cc = replace(CONFIG_CONSEQUENCIA, canais_ligados=canais)
    cl = CONFIG_LOBOS if rotulo == "P0" else CL_T3          # o P0 da bancada: o aprendiz com o aprendizado desligado
    for semente in SEMENTES:
        v, fp, fm = vida(braco(rotulo, cl, cc), "atencioso", "perto", semente, dias=4)
        r = reproduzir_mundo(v.motor.log, fp, CONFIG_PADRAO, semente, fm)
        assert resumo(r, True) == resumo(v.motor, True)
        ei = v.motor.politica.estado_interno()["aprendizado"]
        assert "consequencia_mundo_pendente" not in ei
        if rotulo == "P1":
            assert ei["n_atualizacoes"] > 0 and ei["recompensas"]["consequencia"] > 0


class _Lobos(PoliticaLobos):
    """os lobos do mundo com o credito espiado"""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.creditos, self.ganchos = [], []

    def _creditar(self, registro, f_S, anteriores, consequencia=False) -> None:
        self.creditos.append((registro["acao"], f_S))
        super()._creditar(registro, f_S, anteriores, consequencia)

    def consequencia_mundo(self, acao, ocorrido, obs_depois) -> None:
        self.ganchos.append((acao, ocorrido))
        super().consequencia_mundo(acao, ocorrido, obs_depois)


def test_o_credito_espera_o_consequencia_mundo_e_a_e2_so_no_comer():
    """na vida do P1 cada decisao com alvo e creditada uma vez, no gancho; comer uma fruta usa o sinal da E2"""
    pols = []

    def fab(cfg=None):
        p = _Lobos(cfg or CONFIG_PADRAO, CL_T3, cfg_mundo=CM)
        pols.append(p)
        return bv.PoliticaDoBraco(p, bv.braco_de("P1"), CONFIG_CONSEQUENCIA)

    v, _, _ = vida(fab, "relapso", "perto", 101, dias=4, efeito={"a": -0.1, "b": 0.0, "c": 0.1})
    p, m = pols[-1], v.motor
    com_alvo = [d for d in m.decisoes_mundo if d["acao"] in ("explorar", "comer", "brincar")]
    assert len(p.ganchos) == len(com_alvo) and [a.value for a, _ in p.ganchos] == [d["acao"] for d in com_alvo]
    frutas_comer = [c for c in m.consumos_mundo if c["como"] == "comer" and c["tipo"] in FRUTAS]
    assert frutas_comer, "a vida do teste precisa comer fruta"
    assert p.estado_interno()["aprendizado"]["recompensas"]["consequencia_fruta"] == len(frutas_comer)
    assert all(f != 0 for _, f in p.creditos)


def _decisao_comer(lob: PoliticaLobos, mundo) -> Observacao:
    """uma decisao de tempo livre com comida vista em que o sorteio cai em comer (o ultimo candidato)"""
    o = obs_de(fome=0.6, humor=0.8, mundo=mundo)
    assert lob.agir(o, _RngSonda(1.0 - 1e-12)) is AcaoPet.COMER and lob.ultima_regra == "fruta_no_cenario"
    return o


def _ocorrido(acao, comeu_tipo=None, como="comer"):
    comeu = None if comeu_tipo is None else {"tipo": comeu_tipo, "como": como, "situacao": "madura"}
    return {"acao": acao.value, "u": 0, "alvo": {"tipo": "comida", "x": 0, "y": 0, "id": 1, "de": None}, "de": (0, 0),
            "para": (0, 0), "deslocamento": 0, "energia_gasta": 0.0, "chegou": comeu is not None, "comeu": comeu,
            "brincou_com_bola": False}


@pytest.mark.parametrize("tipo,e2", [("a", True), ("racao", False), (None, False)])
def test_sinal_no_gancho_conta_exata(tipo, e2):
    """comer fruta: sinal_homeostatico_fruta (o humor que a fruta derrubou entra); racao ou nada: o f_S da transicao"""
    lob = _Lobos(CONFIG_PADRAO, CL_T3, cfg_mundo=CM)
    antes = _decisao_comer(lob, perc(["a", "racao"]))
    depois = replace(antes, vetor_estado=(0.75, *antes.vetor_estado[1:3], 0.7, *antes.vetor_estado[4:]))
    t = Transicao(antes, AcaoPet.COMER, depois)
    f_S = sinal_homeostatico(t, S, CONFIG_CONSEQUENCIA)
    lob.observar_consequencia(t, f_S, CONFIG_CONSEQUENCIA)
    assert lob.creditos == [] and "consequencia_mundo_pendente" in lob.estado_interno()["aprendizado"]
    lob.fruta_comida("a", depois)                         # o aviso da E2 vem antes do gancho e nao credita
    assert lob.creditos == []
    lob.consequencia_mundo(AcaoPet.COMER, _ocorrido(AcaoPet.COMER, tipo), depois)
    esperado = sinal_homeostatico_fruta(antes, depois, S, CONFIG_CONSEQUENCIA) if e2 else f_S
    assert lob.creditos == [(AcaoPet.COMER, esperado)]
    assert (esperado != f_S) is e2                         # o humor caiu 0,8 -> 0,7: so a E2 o ve
    assert lob.motivos[-1]["mundo"]["comeu"] == tipo


def test_o_achou_e_comeu_do_explorar_nao_usa_a_e2():
    lob = _Lobos(CONFIG_PADRAO, CL_T3, cfg_mundo=CM)
    o = obs_de(fome=0.6, humor=0.8, mundo=perc(["a"]))
    sonda = _RngSonda(0.3)                                # explorar: o segundo candidato
    assert lob.agir(o, sonda) is AcaoPet.EXPLORAR
    depois = replace(o, vetor_estado=(0.75, *o.vetor_estado[1:3], 0.6, *o.vetor_estado[4:]))
    t = Transicao(o, AcaoPet.EXPLORAR, depois)
    f_S = sinal_homeostatico(t, S, CONFIG_CONSEQUENCIA)
    lob.observar_consequencia(t, f_S, CONFIG_CONSEQUENCIA)
    lob.consequencia_mundo(AcaoPet.EXPLORAR, _ocorrido(AcaoPet.EXPLORAR, "a", "achou"), depois)
    assert lob.creditos == [(AcaoPet.EXPLORAR, f_S)]


def test_pendente_sem_o_gancho_falha_alto():
    lob = PoliticaLobos(CONFIG_PADRAO, CL_T3, cfg_mundo=CM)
    antes = _decisao_comer(lob, perc(["a"]))
    t = Transicao(antes, AcaoPet.COMER, antes)
    lob.observar_consequencia(t, 0, CONFIG_CONSEQUENCIA)
    with pytest.raises(RuntimeError, match="sem consequencia_mundo"):
        lob.agir(antes, _RngSonda(0.5))
    with pytest.raises(RuntimeError, match="pendente de comer"):
        lob.consequencia_mundo(AcaoPet.EXPLORAR, _ocorrido(AcaoPet.EXPLORAR), antes)
    lob2 = PoliticaLobos(CONFIG_PADRAO, CL_T3, cfg_mundo=CM)
    antes = _decisao_comer(lob2, perc(["a"]))
    lob2.observar_consequencia(Transicao(antes, AcaoPet.COMER, antes), 0, CONFIG_CONSEQUENCIA)
    outra = replace(antes, vetor_estado=(0.9, *antes.vetor_estado[1:]))
    with pytest.raises(RuntimeError, match="obs_depois diferente"):
        lob2.consequencia_mundo(AcaoPet.COMER, _ocorrido(AcaoPet.COMER), outra)


def test_canais_no_mundo():
    """frutas iguais (o mundo do plano, PMF-7): os canais somam o escalar e o humor nao aparece. Fruta com efeito no humor e canais:
    o canal do humor nao tem peso que leia a fruta no cerebro A do mundo, e o credito falha alto (rota por adendo)"""
    cc = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)
    v, _, _ = vida(braco("P1", cc=cc), "atencioso", "perto", 101, dias=4)
    canais = v.motor.politica.estado_interno()["canais"]
    assert canais["creditos"] > 0 and canais["por_canal"]["humor"] == 0
    with pytest.raises(RuntimeError, match="CANAIS-REFORCO"):
        vida(braco("P1", cc=cc), "atencioso", "perto", 101, dias=4, efeito={"a": -0.1, "b": 0.0, "c": 0.1})


def test_escolher_alvo_devolve_o_padrao_e_anota_o_motivo():
    v, _, _ = vida(lobos_mundo(), "atencioso", "perto", 202, dias=2)
    motivos = v.motor.politica.estado_interno()["motivos"]
    com_alvo = [d for d in v.motor.decisoes_mundo if d["acao"] in ("explorar", "comer", "brincar")]
    anotados = [m for m in motivos if "mundo" in m]
    assert len(anotados) == len(com_alvo) > 0
    for m, d in zip(anotados, com_alvo):
        assert m["acao"] == d["acao"] and m["mundo"]["alvo"] == d["alvo"] and m["mundo"]["chegou"] == d["chegou"]
        assert d["alvo"] is None or d["alvo"] in m["mundo"]["candidatos"]
    lob = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS)                 # cego ao mundo: o gancho existe e nao faz nada
    assert lob.escolher_alvo(AcaoPet.COMER, [], perc(), 0) is None
    lob.consequencia_mundo(AcaoPet.COMER, _ocorrido(AcaoPet.COMER), obs_de())


# ================================================================== a PoliticaComMotivo
def test_motivo_repassa_os_ganchos_e_nao_muda_a_vida():
    for fab in (lobos_mundo(), braco("P1"), braco("P3")):
        a, _, _ = vida(fab, "aleatorio", "perto", 101)
        embrulhos = []

        def embrulhada(cfg=None, fab=fab):
            p = PoliticaComMotivo(fab(cfg))
            embrulhos.append(p)
            return p

        b, _, _ = vida(embrulhada, "aleatorio", "perto", 101)
        assert resumo(a.motor, True, sem_regra=True) == resumo(b.motor, True, sem_regra=True)
        emb = embrulhos[-1]
        assert hasattr(emb, "escolher_alvo") and hasattr(emb, "consequencia_mundo")
        assert len(emb.motivos) == len(a.motor.decisoes_mundo)
        assert all(set(m.fatores) <= set(FATORES_VIDA) for m in emb.motivos)


def test_motivo_do_instinto_do_mundo():
    embrulhos = []

    def embrulhada(cfg=None):
        p = PoliticaComMotivo(instinto(cfg))
        embrulhos.append(p)
        return p

    a, _, _ = vida(instinto, "atencioso", "longe", 101)
    b, _, _ = vida(embrulhada, "atencioso", "longe", 101)
    assert resumo(a.motor, sem_regra=True) == resumo(b.motor, sem_regra=True)
    emb = embrulhos[-1]
    assert not hasattr(emb, "escolher_alvo")                        # o instinto usa o padrao do motor
    pares = list(zip([d["regra"] for d in a.motor.decisoes_mundo], emb.motivos))
    urgente_comer = [m for r, m in pares if r == "pedido_necessidade" and m.acao == "comer"]
    assert urgente_comer and all(m.fatores == ("fome",) for m in urgente_comer)
    assert any(r == "fruta_no_cenario" for r, _ in pares)
    with pytest.raises(ValueError, match="sem_explorar"):
        PoliticaComMotivo(PoliticaInstintoMundo(CONFIG_PADRAO, sem_explorar=True))


# ================================================================== os empates do cheiro (experiments/analisar_empates_cheiro.py)
def test_empates_exemplo_do_a_e_a_regra_do_motor():
    ex = aec.exemplo_do_a(CM)
    assert ex["vizinhos"]["N"] == ex["vizinhos"]["NE"] == 25 and ex["ordem"] == "NE" and ex["dois"] == "N" == ex["oraculo"]
    fontes = [(0, 0, CM.cheiro_fruta), (300, -120, CM.cheiro_racao)]
    for y in range(-300, 301, 37):
        for x in range(-300, 301, 41):
            assert aec.direcao(x, y, fontes, CM, "ordem")[:2] == direcao_do_cheiro(x, y, fontes, CM)


def test_empates_analise_em_grade_grossa():
    r = aec.analisar(CM, passo_a=24, passo_bc=32)
    for nome in ("fruta", "racao"):
        d, c = r["direcao"][nome], r["comer"][nome]
        assert d["ordem"]["frac_empate"] == d["dois"]["frac_empate"] > 0
        assert d["oraculo"]["erro_abs_graus"]["media"] <= d["dois"]["erro_abs_graus"]["media"] <= d["ordem"]["erro_abs_graus"]["media"]
        assert c["oraculo"]["decisoes_a_mais"]["media"] <= c["ordem"]["decisoes_a_mais"]["media"]
    assert r["vidas"]["decisoes"] > 0 and r["vidas"]["empate"] <= r["vidas"]["com_direcao"]


def test_o_artefato_dos_empates_existe_com_o_exemplo():
    caminho = RAIZ / "artifacts_v2_mundo_cerebros" / "empates_cheiro.json"
    r = json.loads(caminho.read_text(encoding="utf-8"))
    assert r["exemplo_do_a"] == aec.exemplo_do_a(CM)
    assert r["parametros"]["passo_grade_a"] == 1 and r["vidas"]["sementes"] == list(SEMENTES)
