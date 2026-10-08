"""V2, banheiro, etapa 2 (lado do cerebro): o `AcaoPet.ALIVIAR`, o instinto do alivio e o alvo do banheiro nos cerebros
(docs/TAREFA_V2_BANHEIRO.md, secoes 4 e 8).

- o instinto (`PoliticaInstintoBanheiro`): a regra urgente sem sorteio, o aliviar no tempo livre com peso w_vontade x vontade, nada
  dormindo, o alvo herdado (S/4 contra S, com o u do motor) e `aqui` na urgencia;
- o cerebro A com a chave: o aliviar so nas tabelas onde e candidato, os pesos abaixo do teto, o prior da vontade no termo de impulsos;
  com o aprendizado desligado (e ligado, sem nada aprendido) e o instinto do alivio byte a byte, decisao a decisao e alvo a alvo;
- o aprendizado do alvo, em conta exata: pela consequencia (o corpo, no gancho do mundo) e pelo carinho (o `mudanca_no_corpo`, creditado
  a decisao de aliviar: o lado do cerebro do G-CRED); a urgencia nao tem alvo para aprender;
- as falhas altas. O motor com o banheiro (o mapa, a necessidade, o limpador) e da etapa 3, do A: aqui as chamadas sao as do contrato.
So as sementes dos testes.
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import (CONFIG_BANHEIRO_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES,  # noqa: E402
                            CONFIG_LOBOS, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigBanheiro)
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.instinto_banheiro import (ALVOS_ALIVIO, REGRA_ALIVIO_URGENTE, PoliticaInstintoBanheiro, sortear_alvo,  # noqa: E402
                                       tipos_do_alivio, vontade_de)
from digilab.motivo import PoliticaComMotivo  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.mundo import Alvo, PercepcaoMundo  # noqa: E402
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import PoliticaLobos, _RngSonda, sinal_homeostatico  # noqa: E402
from digilab.policy import Observacao, Transicao  # noqa: E402

CB = CONFIG_BANHEIRO_LIGADA
CC = CONFIG_CORPO_BANHEIRO
CM = CONFIG_MUNDO_LIGADA
S = CONFIG_LOBOS.escala
CL_T3 = bv.cfg_lobos_do_ponto("T3")
NOVOS = lb.receptores_novos(CC, True)
TIPOS_VISTOS = ("racao", "a", "b", "c", "racao_podre", "a_podre", "b_podre", "bola")
CANDS = [Alvo("banheiro", 16, 16), Alvo("aqui", 400, 200)]


class RngQueFalha:
    def __getattr__(self, nome):
        raise AssertionError(f"a rng nao podia ser usada: {nome}")


# ================================================================== ajudas
def perc(vistos=(), cheiro=0, direcao=0) -> PercepcaoMundo:
    vs = tuple(sorted(((i + 1 if t != "bola" else 0), t, 5 * (i + 1), 0, 5 * (i + 1)) for i, t in enumerate(vistos)))
    return PercepcaoMundo(200, 240, 0, tuple(sorted(vs, key=lambda v: (v[4], v[1], v[0]))), cheiro, direcao, None)


def corpo(vontade=0, conforto=0, solidao=0, fome=S, higiene=S, energia=S, humor=S) -> PercepcaoCorpo:
    return PercepcaoCorpo(fome=fome, higiene=higiene, energia=energia, humor=humor, saude=S, tedio=0, curiosidade=0, solidao=solidao,
                          estresse=0, dor=0, susto=0, vontade=vontade, conforto=conforto)


def obs_de(vontade=0.0, fome=0.8, higiene=0.8, energia=0.7, humor=0.5, dormindo=0.0, hora=0.5, ticks=0, mundo=None, **kc):
    pc = corpo(vontade=round(vontade * S), **kc)
    return Observacao(vetor_estado=(fome, higiene, energia, humor, 1.0, 0.0, dormindo, hora), ticks_desde_cuidado=ticks,
                      total_cuidados=0, mundo=mundo, corpo=pc)


def obs_aleatoria(rng: random.Random) -> Observacao:
    v = tuple(rng.random() for _ in range(8))
    v = v[:6] + (float(rng.random() < 0.2),) + v[7:]
    mundo = None
    if rng.random() < 0.7:
        vistos = rng.sample(TIPOS_VISTOS, rng.randint(0, 4))
        cheiro = rng.choice((0, 0, rng.randint(1, 120)))
        mundo = perc(vistos, cheiro, rng.randint(0, 8) if cheiro else 0)
    hoje = {n: round(x * S) for n, x in zip(("fome", "higiene", "energia", "humor"), v[:4])}
    pc = PercepcaoCorpo(**hoje, saude=round(v[4] * S), **{n: rng.randint(0, S) for n in NOVOS})
    return Observacao(vetor_estado=v, ticks_desde_cuidado=rng.choice((0, 30, 200, 500)), total_cuidados=0, mundo=mundo, corpo=pc)


def instinto(cb=CB) -> PoliticaInstintoBanheiro:
    return PoliticaInstintoBanheiro(CONFIG_PADRAO, cb, CC)


def lobos(cl=CONFIG_LOBOS, cb=CB) -> PoliticaLobos:
    return PoliticaLobos(CONFIG_PADRAO, cl, cfg_mundo=CM, cfg_corpo=CC, cfg_banheiro=cb)


# ================================================================== o enum
def test_aliviar_no_fim_do_enum_e_as_sete_de_hoje():
    from digilab.events import ACOES_PET_BANHEIRO, ACOES_PET_HOJE
    assert tuple(AcaoPet)[-1] is AcaoPet.ALIVIAR and AcaoPet("aliviar") is AcaoPet.ALIVIAR
    assert ACOES_PET_HOJE + ACOES_PET_BANHEIRO == tuple(AcaoPet) and len(ACOES_PET_HOJE) == 7
    assert lb.ACOES == ACOES_PET_HOJE                       # o cerebro sem o banheiro: as tabelas de sempre
    assert (REGRA_ALIVIO_URGENTE, ALVOS_ALIVIO) == (lb.REGRA_ALIVIO_URGENTE, lb.ALVOS_ALIVIO)


# ================================================================== o instinto do alivio
def test_regra_urgente_alivia_sem_sorteio():
    p = instinto()
    assert p.agir(obs_de(vontade=0.95), RngQueFalha()) is AcaoPet.ALIVIAR and p.ultima_regra == REGRA_ALIVIO_URGENTE
    assert lb.impulsos(p, obs_de(vontade=0.95)) == (REGRA_ALIVIO_URGENTE, (AcaoPet.ALIVIAR,))
    # antes do pedido de necessidade e do abandono
    assert p.agir(obs_de(vontade=0.95, fome=0.1, ticks=900), RngQueFalha()) is AcaoPet.ALIVIAR
    # no limiar, nao (0,90 nao passa de 0,90)
    o = obs_de(vontade=0.9)
    o = replace(o, corpo=replace(o.corpo, vontade=921))       # 921 / 1024 < 0,90
    assert lb.impulsos(p, o)[0] != REGRA_ALIVIO_URGENTE


@pytest.mark.parametrize("kw", [dict(energia=0.2), dict(dormindo=1.0, energia=0.6), dict(hora=0.05, energia=0.5)])
def test_dormindo_nao_alivia(kw):
    p = instinto()
    assert p.agir(obs_de(vontade=1.0, **kw), RngQueFalha()) is AcaoPet.DORMIR and p.ultima_regra.startswith("sono")


@pytest.mark.parametrize("vistos,regra", [((), "tempo_livre"), (("bola",), "bola_no_cenario"), (("a", "bola"), "fruta_no_cenario")])
def test_aliviar_entra_no_tempo_livre_com_a_vontade_moderada(vistos, regra):
    p = instinto()
    o = obs_de(vontade=0.75, mundo=perc(vistos))
    r, cands = lb.impulsos(p, o)
    assert r == regra and cands[-1] is AcaoPet.ALIVIAR
    sonda = _RngSonda(0.0)
    p.agir(o, sonda)
    pesos = dict(zip(*sonda.escolha))
    assert pesos[AcaoPet.ALIVIAR] == CB.w_vontade * (768 / S) == 3.0
    # com a vontade em 0,5 (nao passa do limiar), os candidatos de hoje
    sem = lb.impulsos(p, obs_de(vontade=0.5, mundo=perc(vistos)))
    assert sem[0] == regra and AcaoPet.ALIVIAR not in sem[1]
    assert sem[1] == lb.impulsos(PoliticaInstintoBanheiro(CONFIG_PADRAO, CB, CC), obs_de(vontade=0.0, mundo=perc(vistos)))[1]


def test_alvo_herdado_do_instinto():
    p = instinto()
    p.agir(obs_de(vontade=0.75), random.Random(11))
    assert p.escolher_alvo(AcaoPet.EXPLORAR, [], None, 0) is None and p.escolher_alvo(AcaoPet.COMER, [], None, 0) is None
    contagem = sum(p.escolher_alvo(AcaoPet.ALIVIAR, CANDS, None, u).tipo == "banheiro" for u in range(1 << 16))
    assert contagem == 13108                            # u / 2^16 x 1,25 < 0,25: S/4 contra S, ~1 em 5
    inv = list(reversed(CANDS))
    assert sum(p.escolher_alvo(AcaoPet.ALIVIAR, inv, None, u).tipo == "banheiro" for u in range(1 << 16)) == 13107
    p.agir(obs_de(vontade=0.99), RngQueFalha())
    assert all(p.escolher_alvo(AcaoPet.ALIVIAR, CANDS, None, u).tipo == "aqui" for u in (0, 1, 13107, 65535))   # o acidente


def test_sortear_alvo_e_a_conta_dos_lobos():
    rng = random.Random(22)
    for _ in range(2000):
        pesos = [rng.random() * 3 for _ in range(rng.randint(1, 4))]
        u = rng.randrange(1 << 16)
        assert sortear_alvo(pesos, u) == lb.sortear(pesos, u / (1 << 16))


def test_falhas_altas_do_instinto():
    with pytest.raises(ValueError, match="ConfigBanheiro ligada"):
        PoliticaInstintoBanheiro(CONFIG_PADRAO, ConfigBanheiro(), CC)
    with pytest.raises(ValueError, match="sub-chave banheiro"):
        PoliticaInstintoBanheiro(CONFIG_PADRAO, CB, CONFIG_CORPO_DRIVES)
    with pytest.raises(RuntimeError, match="receptor da vontade"):
        instinto().agir(Observacao((0.8,) * 6 + (0.0, 0.5), 0, 0), random.Random(1))
    with pytest.raises(ValueError, match="candidatos do alvo"):
        tipos_do_alivio([Alvo("banheiro", 0, 0), Alvo("comida", 1, 1, 3)])
    with pytest.raises(ValueError, match="u do alvo"):
        sortear_alvo([1.0, 1.0], 1 << 16)
    o = obs_de()
    with pytest.raises(ValueError):
        vontade_de(replace(o, corpo=replace(o.corpo, vontade=S + 1)), S)


# ================================================================== o cerebro A com a chave
def test_chaves_do_cerebro_vao_juntas():
    with pytest.raises(ValueError, match="vao juntas"):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM, cfg_corpo=CC)                      # a vontade sem o aliviar
    with pytest.raises(ValueError, match="vao juntas"):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_DRIVES, cfg_banheiro=CB)
    with pytest.raises(ValueError, match="mundo fisico"):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_corpo=CC, cfg_banheiro=CB)
    # a chave desligada no cerebro e o de hoje
    hoje = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_DRIVES, cfg_banheiro=ConfigBanheiro())
    assert all(AcaoPet.ALIVIAR not in t for t in hoje._prior.values()) and not hoje._pesos_alvo


def test_aliviar_so_onde_e_candidato_e_os_pesos_abaixo_do_teto():
    p = lobos()
    com = {r for r, t in p._prior.items() if AcaoPet.ALIVIAR in t}
    assert com == set(lb.REGRAS_ENTRADAS_CORPO) | {REGRA_ALIVIO_URGENTE}
    assert list(p._prior[REGRA_ALIVIO_URGENTE]) == [AcaoPet.ALIVIAR]
    assert all(p._prior[r][AcaoPet.ALIVIAR] == [0] * len(p.entradas) for r in lb.REGRAS_ENTRADAS_CORPO)
    i = NOVOS.index("vontade")
    for r in lb.REGRAS_ENTRADAS_CORPO:
        assert p._prior_corpo[r][AcaoPet.ALIVIAR] == [0] * i + [4 * S] + [0] * (len(NOVOS) - i - 1)
        assert all(sum(v) == 0 for a, v in p._prior_corpo[r].items() if a is not AcaoPet.ALIVIAR)
    # 9 regras x 7 acoes x 12 entradas + o aliviar (4 regras x 12) + as entradas do corpo (3 regras x 8 acoes x 8) + 2 do alvo
    assert NOVOS == ("tedio", "curiosidade", "solidao", "estresse", "dor", "susto", "vontade", "conforto")
    assert p.n_pesos() == 756 + 48 + 192 + 2 == 998 < CONFIG_LOBOS.maximo_pesos
    assert p._prior_alvo == {"banheiro": S // 4, "aqui": S}


@pytest.mark.parametrize("cl", [CONFIG_LOBOS, CL_T3], ids=["desligado", "T3"])
def test_lobos_no_prior_sao_o_instinto_do_alivio_decisao_a_decisao(cl):
    """3000 observacoes: a mesma acao, a mesma regra e a mesma rng; e o mesmo alvo do aliviar para qualquer u"""
    rng_obs, rng_u = random.Random(33), random.Random(44)
    ins, lob = instinto(), lobos(cl)
    r1, r2 = random.Random(55), random.Random(55)
    n_aliviar = n_urgente = 0
    for _ in range(3000):
        o = obs_aleatoria(rng_obs)
        a = ins.agir(o, r1)
        b = lob.agir(o, r2)
        assert a is b and ins.ultima_regra == lob.ultima_regra and r1.getstate() == r2.getstate()
        if a is AcaoPet.ALIVIAR:
            n_aliviar += 1
            n_urgente += ins.ultima_regra == REGRA_ALIVIO_URGENTE
            for _ in range(5):
                u = rng_u.randrange(1 << 16)
                cands = CANDS if rng_u.random() < 0.5 else list(reversed(CANDS))
                assert ins.escolher_alvo(AcaoPet.ALIVIAR, cands, None, u) is lob.escolher_alvo(AcaoPet.ALIVIAR, cands, None, u)
        else:
            assert lob.escolher_alvo(a, [], None, 0) is None
        lob._registro_decisao = None                     # so as decisoes, sem o observar (a sonda nao aprende)
    assert n_aliviar > 150 and 0 < n_urgente < n_aliviar


def test_o_prior_da_vontade_vai_a_impulsos():
    p = lobos()
    o = obs_de(vontade=0.75)
    sonda = _RngSonda(0.0)
    p.agir(o, sonda)
    c = p.motivos[-1]["contribuicoes"]
    assert c["impulsos"]["aliviar"] == 4.0 * (768 / S) and c["decisao"]["aliviar"] == 0.0


# ================================================================== o aprendizado do alvo
def _decidir_aliviar(p: PoliticaLobos, o: Observacao, alvo: str) -> AcaoPet:
    """uma decisao de tempo livre que sai `aliviar` (o u no fim da roleta) com o alvo pedido (o u da roleta do alvo)"""
    class U:
        def random(self):
            return 1.0 - 1e-12
    a = p.agir(o, U())
    assert a is AcaoPet.ALIVIAR and p.ultima_regra == "tempo_livre"
    u = 0 if alvo == "banheiro" else (1 << 16) - 1
    assert p.escolher_alvo(AcaoPet.ALIVIAR, CANDS, None, u).tipo == alvo
    return a


def _ocorrido(alvo: str) -> dict:
    return {"acao": "aliviar", "alvo": {"tipo": alvo}, "chegou": True, "deslocamento": 0, "comeu": None, "brincou_com_bola": False}


@pytest.mark.parametrize("alvo", ["banheiro", "aqui"])
def test_alvo_aprende_pela_consequencia_conta_exata(alvo):
    """o P1: a consequencia do aliviar (a vontade a zero) e creditada no gancho do mundo; o alvo escolhido sobe pela regra da fruta"""
    p = lobos(CL_T3)
    antes = obs_de(vontade=0.75, ticks=30)
    _decidir_aliviar(p, antes, alvo)
    sub = p._registro_decisao["alvo"]
    depois = obs_de(vontade=0.0, ticks=30)
    t = Transicao(antes, AcaoPet.ALIVIAR, depois)
    cc = CONFIG_CONSEQUENCIA
    p.observar_consequencia(t, sinal_homeostatico(t, S, cc), cc)
    assert p._pesos_alvo == p._prior_alvo                 # o credito espera o gancho
    p.consequencia_mundo(AcaoPet.ALIVIAR, _ocorrido(alvo), depois)
    drives = ("fome", "higiene", "energia") + tuple(d for d in lb.DRIVES_NOVOS_SINAL if d in NOVOS)
    f = lb.sinal_corpo(antes.corpo, depois.corpo, drives, cc.ganho, S, dict(cc.pesos_drives_corpo))
    assert f == lb.div_arred(4 * 768 * 768, S) == 2304 and p.motivos[-1]["sinal_corpo"]["f"] == f
    esperado = dict(p._prior_alvo)
    for k in sub["candidatos"]:
        fator = (S if k == alvo else 0) - sub["P"][k]
        esperado[k] += lb.div_arred(f * CL_T3.passo * S * fator, S * S * sub["W"][k])
    assert p._pesos_alvo == esperado and p._pesos_alvo[alvo] > p._prior_alvo[alvo]
    p.consequencia_corpo(AcaoPet.ALIVIAR, {"acao": "aliviar", "estimulos": []}, depois)     # fecha a decisao
    json.dumps(p.estado_interno())
    assert p.estado_interno()["aprendizado"]["ultima"]["alvo"]["acao"] == alvo


def test_carinho_depois_do_aliviar_ensina_o_alvo():
    """o lado do cerebro do G-CRED: o carinho (mudanca_no_corpo) e creditado a ultima decisao, o aliviar no banheiro, e sobe o banheiro"""
    p = lobos(CL_T3)
    antes = obs_de(vontade=0.75, ticks=30)
    _decidir_aliviar(p, antes, "banheiro")
    depois = obs_de(vontade=0.0, ticks=30)
    t = Transicao(antes, AcaoPet.ALIVIAR, depois)
    p.observar_consequencia(t, sinal_homeostatico(t, S, CONFIG_CONSEQUENCIA), CONFIG_CONSEQUENCIA)
    p.consequencia_mundo(AcaoPet.ALIVIAR, _ocorrido("banheiro"), depois)
    p.consequencia_corpo(AcaoPet.ALIVIAR, {"acao": "aliviar", "estimulos": []}, depois)
    w = dict(p._pesos_alvo)
    sub = p._ultima["alvo"]
    # o carinho: o conforto sobe (45000 -> 102) e a solidao cai
    o1 = obs_de(vontade=0.0, ticks=40, solidao=205)
    o2 = obs_de(vontade=0.0, ticks=0, solidao=0, conforto=102)
    p.mudanca_no_corpo(o1, o2)
    drives = ("fome", "higiene", "energia") + tuple(d for d in lb.DRIVES_NOVOS_SINAL if d in NOVOS)
    f = lb.sinal_corpo(o1.corpo, o2.corpo, drives, CONFIG_CONSEQUENCIA.ganho, S, dict(CONFIG_CONSEQUENCIA.pesos_drives_corpo))
    assert f == lb.div_arred(4 * (205 * 205 + S * S - (S - 102) ** 2), S) == 940
    esperado = dict(w)
    for k in sub["candidatos"]:
        fator = (S if k == "banheiro" else 0) - sub["P"][k]
        esperado[k] += lb.div_arred(f * CL_T3.passo * S * fator, S * S * sub["W"][k])
    assert p._pesos_alvo == esperado and p._pesos_alvo["banheiro"] > w["banheiro"] and p._pesos_alvo["aqui"] < w["aqui"]


def test_urgencia_nao_tem_alvo_para_aprender():
    p = lobos(CL_T3)
    o = obs_de(vontade=0.97, ticks=30)
    assert p.agir(o, RngQueFalha()) is AcaoPet.ALIVIAR
    assert p.escolher_alvo(AcaoPet.ALIVIAR, CANDS, None, 0).tipo == "aqui"
    assert "alvo" not in p._registro_decisao and p.motivos[-1]["alvo_alivio"]["urgente"]
    d = obs_de(vontade=0.0, ticks=30)
    t = Transicao(o, AcaoPet.ALIVIAR, d)
    p.observar_consequencia(t, sinal_homeostatico(t, S, CONFIG_CONSEQUENCIA), CONFIG_CONSEQUENCIA)
    p.consequencia_mundo(AcaoPet.ALIVIAR, _ocorrido("aqui"), d)
    assert p._pesos_alvo == p._prior_alvo


def test_falhas_altas_do_cerebro():
    hoje = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_DRIVES)
    with pytest.raises(RuntimeError, match="sem o banheiro"):
        hoje.escolher_alvo(AcaoPet.ALIVIAR, CANDS, None, 0)
    p = lobos(CL_T3)
    p.agir(obs_de(vontade=0.2), random.Random(1))       # uma decisao que nao e aliviar
    with pytest.raises(RuntimeError, match="sem a decisao de aliviar"):
        p.escolher_alvo(AcaoPet.ALIVIAR, CANDS, None, 0)
    # o aliviar, no mundo, espera o gancho do mundo antes do corpo
    p = lobos(CL_T3)
    o = obs_de(vontade=0.75, ticks=30)
    _decidir_aliviar(p, o, "aqui")
    t = Transicao(o, AcaoPet.ALIVIAR, o)
    p.observar_consequencia(t, sinal_homeostatico(t, S, CONFIG_CONSEQUENCIA), CONFIG_CONSEQUENCIA)
    with pytest.raises(RuntimeError, match="sem o consequencia_mundo"):
        p.consequencia_corpo(AcaoPet.ALIVIAR, {"acao": "aliviar", "estimulos": []}, o)
    # o motivo do aliviar nao tem texto: o embrulho falha alto
    emb = PoliticaComMotivo(instinto())
    with pytest.raises(NotImplementedError, match="aliviar"):
        emb.agir(obs_de(vontade=0.95), RngQueFalha())


# ================================================================== G1 do cerebro: as mesmas chamadas, o mesmo estado
def _vida_de_chamadas(semente: int) -> dict:
    """uma sequencia de decisoes com os ganchos do contrato (o alvo do aliviar, a consequencia, o gancho do mundo nas acoes com alvo, o
    do corpo sempre e um carinho de vez em quando), com observacoes sorteadas; devolve o estado interno"""
    rng = random.Random(semente)
    p = lobos(CL_T3)
    cc = CONFIG_CONSEQUENCIA
    tick_cuidado = 0
    for k in range(400):
        o = obs_aleatoria(rng)
        o = replace(o, ticks_desde_cuidado=15 * k - tick_cuidado)
        a = p.agir(o, rng)
        if a is AcaoPet.ALIVIAR:
            p.escolher_alvo(a, CANDS if rng.random() < 0.5 else list(reversed(CANDS)), None, rng.randrange(1 << 16))
        d = replace(obs_aleatoria(rng), ticks_desde_cuidado=o.ticks_desde_cuidado)
        t = Transicao(o, a, d)
        p.observar_consequencia(t, sinal_homeostatico(t, S, cc), cc)
        if a in lb.ACOES_COM_ALVO_MUNDO + (AcaoPet.ALIVIAR,):
            p.consequencia_mundo(a, {"acao": a.value, "alvo": None, "chegou": False, "deslocamento": 0, "comeu": None,
                                     "brincou_com_bola": False}, d)
        p.consequencia_corpo(a, {"acao": a.value, "estimulos": []}, d)
        if rng.random() < 0.1:
            o2 = replace(d, ticks_desde_cuidado=0, corpo=replace(d.corpo, conforto=min(S, d.corpo.conforto + 102)))
            p.mudanca_no_corpo(d, o2)
            tick_cuidado = 15 * k + d.ticks_desde_cuidado
    return p.estado_interno()


def test_mesmas_chamadas_mesmo_estado_interno():
    e1, e2 = _vida_de_chamadas(101), _vida_de_chamadas(101)
    assert json.dumps(e1, sort_keys=True, default=repr) == json.dumps(e2, sort_keys=True, default=repr)
    assert e1["pesos_alvo"] != e1["pesos_alvo_prior"]                  # o alvo aprendeu
    assert any(m["acao"] == "aliviar" for m in e1["motivos"]) and e1["aprendizado"]["recompensas"].get("carinho", 0) > 0
    assert json.dumps(_vida_de_chamadas(202), sort_keys=True, default=repr) != json.dumps(e1, sort_keys=True, default=repr)
