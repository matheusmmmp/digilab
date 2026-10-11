"""O banheiro no mundo fisico, etapa 3 (docs/TAREFA_V2_BANHEIRO.md, secoes 2 a 5 e 8; BN-1 a BN-6 decididas em 2026-10-07).

Gates: G2 (a chave desligada e a vida de hoje: os gabaritos de sempre rodam na suite; aqui, a chave explicita desligada), G-MEC (a
vontade sobe e cai; o limpador recolhe so no banheiro; o objeto da o desconforto da zona; o limpar recolhe; o urgente alivia aqui; o
alvo banheiro leva o pet ate la ou segura a vontade; a continuacao em tests/test_banheiro_continuar.py), G-CRED (o carinho do DonoCarinhoBanheiro e creditado a decisao de aliviar), G-CONS
(com limpador, o sinal do aliviar no banheiro e maior que fora; sem limpador, igual), G1 (replay bit a bit, com e sem o limpador, com o
carinho, com o instinto e os lobos aprendendo, e no grupo) e o contrato da bancada (`motor.alivios`). So as sementes dos testes.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import (CONFIG_BANHEIRO, CONFIG_BANHEIRO_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_CORPO_BANHEIRO,  # noqa: E402
                            CONFIG_CORPO_DRIVES, CONFIG_GRUPO_LIGADA, CONFIG_MUNDO, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,
                            LAYOUT_MUNDO_AFASTADO, TICKS_POR_DIA, ConfigBanheiro)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.grupo import PetDoGrupo, reproduzir_grupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_banheiro import PoliticaInstintoBanheiro  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import (ZONA_BANHEIRO, BanheiroSemMundo, DonoCarinhoBanheiro, DonoComLugar, MotorMundo,  # noqa: E402
                           faixa_do_banheiro, no_banheiro, ponto_do_banheiro, regiao_de, reproduzir_mundo, simular_vida_mundo,
                           zona_da_necessidade)
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

CM = CONFIG_MUNDO_LIGADA
CC = CONFIG_CORPO_BANHEIRO
CB = CONFIG_BANHEIRO_LIGADA
CBL = replace(CB, limpador=True)
# um banheiro em volta do comedouro (10, 15), so para os testes: o pet passa muito tempo nele e o carinho acontece
CB_PERTO = replace(CB, celulas_x=(8, 12), celulas_y=(12, 18))
S = CC.escala_receptor
C = CC.escala
M = com_corpo(MotorMundo)
CL_T3 = bv.cfg_lobos_do_ponto("T3")
NOVOS = lb.receptores_novos(CC, True)
DRIVES_SINAL = ("fome", "higiene", "energia") + tuple(d for d in lb.DRIVES_NOVOS_SINAL if d in NOVOS)
CHAVES_ALIVIO = {"tick", "dentro", "urgente", "alvo", "distancia", "recolhido"}
DIAS = 3


def fm(cbh=CB, cm=CM, cc=CC):
    return lambda p, cfg, s, **kw: M(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc, cfg_banheiro=cbh, **kw)


def fp_instinto(cbh=CB):
    return lambda cfg=None: PoliticaInstintoBanheiro(cfg or CONFIG_PADRAO, cbh, CC)


class LobosEspiao(PoliticaLobos):
    """os lobos do P1, anotando a decisao que cada carinho credita (o G-CRED)"""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.creditos: list = []

    def mudanca_no_corpo(self, obs_antes, obs_depois) -> None:
        self.creditos.append(None if self._ultima is None else self._ultima["acao"])
        super().mudanca_no_corpo(obs_antes, obs_depois)


def fp_lobos(cbh=CB, cm=CM, espiao=False):
    classe = LobosEspiao if espiao else PoliticaLobos
    return lambda cfg=None: bv.PoliticaDoBraco(classe(cfg or CONFIG_PADRAO, CL_T3, cfg_mundo=cm, cfg_corpo=CC, cfg_banheiro=cbh),
                                               bv.BRACOS["P1"], CONFIG_CONSEQUENCIA)


def vida(fp, cbh=CB, semente=101, dias=DIAS, dono="atencioso", lugar="comedouro", carinho=False, cm=CM):
    car = DonoCarinhoBanheiro() if carinho else None
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, cm)
    v = simular_vida_mundo("t", d, fp(), semente, dias, 16 * dias, fm(cbh, cm), rotulo_dono=dono, carinho=car)
    return v, car


def texto(x) -> str:
    return json.dumps(x, sort_keys=True, default=str)


class Roteiro:
    """um cerebro de teste: as acoes de uma lista (depois, ocioso) e o alvo do aliviar pedido; anota as observacoes e o gancho do corpo"""

    nome = "roteiro"

    def __init__(self, acoes, alvo="aqui") -> None:
        self.acoes = list(acoes)
        self.alvo = alvo
        self.obs: list = []
        self.corpo: list = []

    def agir(self, obs, rng):
        self.obs.append(obs)
        return self.acoes.pop(0) if self.acoes else AcaoPet.OCIOSO

    def observar(self, transicao) -> None:
        pass

    def receber_acao_dono(self, acao, tick) -> None:
        pass

    def estado_interno(self) -> dict:
        return {}

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        if acao is AcaoPet.ALIVIAR:
            return next(c for c in candidatos if c.tipo == self.alvo)
        return None

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        self.corpo.append((acao, ocorrido, obs_depois))


def motor_roteiro(acoes, alvo="aqui", cbh=CB, pet=None, vontade=None, semente=101):
    pol = Roteiro(acoes, alvo)
    m = fm(cbh)(pol, CONFIG_PADRAO, semente)
    if pet is not None:
        m.pet = pet
    if vontade is not None:
        m.corpo.q["vontade"] = vontade
    return m, pol


DENTRO = (32, 48)                             # dentro do banheiro padrao (celulas 0 a 3, 0 a 5: x 0 a 63, y 0 a 95)
FORA_PERTO = (104, 48)                        # 41 subunidades a leste do banheiro: ao alcance de uma decisao (60)
FORA_LONGE = (200, 64)                        # na casa (celula 12), longe do banheiro


# ================================================================== G2 e as chaves
def test_g2_chave_desligada_explicita_e_a_vida_de_hoje():
    """com a ConfigBanheiro desligada dada explicitamente, a vida do mundo com o corpo de hoje, byte a byte: nem chave em estado(),
    nem registro, nem necessidade no Mundo (os gabaritos de sempre, banheiro_vidas_de_hoje, dois_pets, corpo_mundo e mundo, rodam na
    suite com o codigo novo)"""
    cc = CONFIG_CORPO_DRIVES
    fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    vs = []
    for kw in ({}, {"cfg_banheiro": CONFIG_BANHEIRO}):
        fab = lambda p, cfg, s, kw=kw: M(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, **kw)  # noqa: E731
        d = DonoComLugar(criar_dono("atencioso"), "perto", 101, "atencioso", CM)
        vs.append(simular_vida_mundo("t", d, fp(), 101, 2, 32, fab, rotulo_dono="atencioso").motor)
    a, b = vs
    assert texto(a.resumo_mundo_fisico()) == texto(b.resumo_mundo_fisico()) and texto(a.estado()) == texto(b.estado())
    assert "banheiro" not in b.estado() and "alivios" not in b.resumo_mundo_fisico() and "necessidades" not in b.mundo.resumo()
    assert b.mundo.necessidades is None and not hasattr(b, "alivios")


def test_as_chaves_vao_juntas_e_falham_alto():
    pol = Roteiro([])
    with pytest.raises(BanheiroSemMundo, match="mundo fisico"):           # sem o mundo
        M(pol, CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CONFIG_MUNDO, cfg_corpo=CC, cfg_banheiro=CB)
    with pytest.raises(BanheiroSemMundo, match="corpo na frente"):        # sem o corpo
        MotorMundo(pol, CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_banheiro=CB)
    with pytest.raises(ValueError, match="vao juntos"):                    # o corpo sem a vontade
        M(pol, CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_DRIVES, cfg_banheiro=CB)
    with pytest.raises(ValueError, match="vao juntos"):                    # a vontade sem o banheiro no mapa
        M(pol, CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC)
    with pytest.raises(ValueError, match="dentro da casa"):
        fm(replace(CB, celulas_x=(14, 17)))(pol, CONFIG_PADRAO, 101)
    with pytest.raises(ValueError, match="fora do mapa"):
        fm(replace(CB, celulas_y=(28, 30)))(pol, CONFIG_PADRAO, 101)
    for ruim in ((3, 1), (-1, 2), (0,), (0.0, 3)):
        with pytest.raises(ValueError):
            ConfigBanheiro(celulas_x=ruim)
    with pytest.raises(BanheiroSemMundo):
        DonoCarinhoBanheiro().acoes({"tick": 0})


def test_aliviar_sem_banheiro_falha_alto():
    """um cerebro que alivia num mundo sem o banheiro: a acao so existe com a chave"""
    pol = Roteiro([AcaoPet.ALIVIAR])
    m = MotorMundo(pol, CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM)
    with pytest.raises(ValueError, match="acao sem alvo|banheiro"):
        m.avancar(15)


# ================================================================== a geometria
def test_o_retangulo_o_ponto_mais_perto_e_a_zona():
    assert faixa_do_banheiro(CB, CM) == (0, 63, 0, 95)
    assert no_banheiro(0, 0, CB, CM) and no_banheiro(63, 95, CB, CM) and not no_banheiro(64, 0, CB, CM) and not no_banheiro(0, 96, CB, CM)
    assert ponto_do_banheiro(*DENTRO, CB, CM) == DENTRO
    assert ponto_do_banheiro(300, 248, CB, CM) == (63, 95) and ponto_do_banheiro(30, 400, CB, CM) == (30, 95)
    assert zona_da_necessidade(*DENTRO, CB, CM) == ZONA_BANHEIRO
    assert zona_da_necessidade(*FORA_LONGE, CB, CM) == regiao_de(FORA_LONGE[0], CM) == 0          # a casa, fora do banheiro
    assert zona_da_necessidade(600, 64, CB, CM) == regiao_de(600, CM) != 0


# ================================================================== G-MEC
def test_g_mec_aliviar_zera_a_vontade_e_a_necessidade_fica_com_o_cheiro():
    """aqui, fora do banheiro, sem o limpador: a vontade cai a 0 e o desconforto sobe +22500 na hora (o objeto fica no chao)"""
    m, pol = motor_roteiro([AcaoPet.ALIVIAR], "aqui", pet=FORA_LONGE, vontade=300000)
    desc = m.corpo.q["desconforto"]
    m.avancar(15)
    acao, oc, depois = pol.corpo[0]
    assert acao is AcaoPet.ALIVIAR and ("aliviar", False) in oc["estimulos"] and ("necessidade",) in oc["estimulos"]
    assert depois.corpo.vontade == 0
    assert oc["estimulos"][:2] == [("pet", "aliviar"), ("andar", 0)]
    assert m.alivios == [{"tick": 0, "dentro": False, "urgente": False, "alvo": "aqui", "distancia": 200 - 63, "recolhido": False}]
    assert [(n["x"], n["y"], n["tick"]) for n in m.mundo.necessidades.values()] == [(*FORA_LONGE, 0)]
    # o cheiro na hora (antes de qualquer tick): a leitura do obs_depois e a do desconforto + 22500
    assert C - depois.corpo.higiene * C // S >= 0
    assert m.corpo.q["vontade"] == 15 * CC.vontade_sobe                     # e volta a subir a cada tick acordado
    assert m.corpo.q["desconforto"] > desc + CC.necessidade_desconforto


@pytest.mark.parametrize("limpador", [False, True])
@pytest.mark.parametrize("onde", ["dentro", "fora"])
def test_g_mec_o_limpador_recolhe_so_no_banheiro(limpador, onde):
    pet = DENTRO if onde == "dentro" else FORA_LONGE
    m, pol = motor_roteiro([AcaoPet.ALIVIAR], "aqui", cbh=CBL if limpador else CB, pet=pet, vontade=300000)
    m.avancar(15)
    recolhe = limpador and onde == "dentro"
    a = m.alivios[0]
    assert a["dentro"] is (onde == "dentro") and a["recolhido"] is recolhe
    assert len(m.mundo.necessidades) == (0 if recolhe else 1)
    assert (("necessidade",) in pol.corpo[0][1]["estimulos"]) is (not recolhe)


def test_g_mec_o_objeto_da_o_desconforto_da_zona():
    """o corpo recebe, a cada tick, quantas necessidades estao na zona do pet (o banheiro e uma zona propria, dentro da casa)"""
    m, pol = motor_roteiro([AcaoPet.ALIVIAR] * 2, "aqui", pet=FORA_LONGE, vontade=300000)
    recebidas = []
    passo = m.corpo.passo
    m.corpo.passo = lambda antes, necessidades=0: (recebidas.append(necessidades), passo(antes, necessidades=necessidades))[1]
    m.avancar(15)
    assert recebidas == [1] * 15                                  # a necessidade de agora, na casa (a zona do pet)
    m.pet = DENTRO                                                # no banheiro: outra zona, a da casa nao conta
    recebidas.clear()
    m.avancar(15)                                                 # alivia dentro do banheiro (sem o limpador, o objeto fica)
    assert recebidas == [1] * 15 and m.necessidades_na_zona() == 1
    m.pet = FORA_LONGE
    assert m.necessidades_na_zona() == 1 and len(m.mundo.necessidades) == 2
    # a conta do corpo: +100 por tick por necessidade, ate 3 (a soma inteira da fase 1)
    a = M(Roteiro([]), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC, cfg_banheiro=CB)
    b = M(Roteiro([]), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC, cfg_banheiro=CB)
    for x in range(5):
        b.mundo.deixar_necessidade(a.pet[0] + x, a.pet[1], 0)
    a.avancar(15)
    b.avancar(15)
    assert b.corpo.q["desconforto"] - a.corpo.q["desconforto"] == 15 * CC.necessidade_regiao * CC.necessidade_max_regiao


def test_g_mec_o_limpar_recolhe_a_zona_do_pet():
    m, pol = motor_roteiro([AcaoPet.ALIVIAR] * 2, "aqui", pet=FORA_LONGE, vontade=300000)
    m.avancar(15)
    m.pet = DENTRO
    m.avancar(15)
    m.pet = FORA_LONGE
    m.observar(AcaoUsuario.LIMPAR)                       # recolhe a da casa, nao a do banheiro
    assert [(n["x"], n["y"]) for n in m.mundo.necessidades.values()] == [DENTRO]
    assert m.recolhas == [{"tick": 30, "zona": 0, "ids": [1]}] and m.mundo.recolhidas[0]["como"] == "limpar"
    m.observar(AcaoUsuario.LIMPAR)                       # nada mais na zona
    assert m.recolhas[-1]["ids"] == [] and len(m.mundo.necessidades) == 1
    m.pet = DENTRO
    m.observar(AcaoUsuario.LIMPAR)
    assert m.mundo.necessidades == {} and m.estado()["banheiro"]["necessidades"] == 0


def test_g_mec_o_urgente_alivia_aqui():
    """com a vontade acima de 0,90 o instinto alivia ja, aqui (o acidente); um cerebro que pedisse o banheiro falha alto"""
    vontade = int(0.95 * C)
    m = fm()(PoliticaInstintoBanheiro(CONFIG_PADRAO, CB, CC), CONFIG_PADRAO, 101)
    m.pet = FORA_LONGE
    m.corpo.q["vontade"] = vontade
    m.avancar(15)
    assert m.alivios[0]["urgente"] and m.alivios[0]["alvo"] == "aqui" and not m.alivios[0]["dentro"]
    m2, _ = motor_roteiro([AcaoPet.ALIVIAR], "banheiro", pet=FORA_LONGE, vontade=vontade)
    with pytest.raises(RuntimeError, match="urgente"):
        m2.avancar(15)


def test_g_mec_o_alvo_banheiro_leva_ate_la_ou_segura_a_vontade():
    """ao alcance, alivia dentro; alem do alcance de uma decisao, anda o alcance e segura a vontade (a continuacao, 2026-10-11: antes
    aliviava no caminho, em (140, 64))"""
    perto, _ = motor_roteiro([AcaoPet.ALIVIAR], "banheiro", pet=FORA_PERTO, vontade=300000)
    perto.avancar(15)
    a = perto.alivios[0]
    assert perto.pet == (63, 48) and a["dentro"] and a["distancia"] == 41 and perto.decisoes_mundo[0]["chegou"]
    longe, pol = motor_roteiro([AcaoPet.ALIVIAR], "banheiro", pet=FORA_LONGE, vontade=300000)
    e0 = longe.corpo.q["cansaco"]
    longe.avancar(15)
    assert longe.pet == (200 - 60, 64) and longe.alivios == []                            # andou o alcance (60) e nao aliviou
    assert not longe.decisoes_mundo[0]["chegou"] and longe.decisoes_mundo[0]["alvo"] == "banheiro"
    assert ("andar", 60) in pol.corpo[0][1]["estimulos"] and longe.corpo.q["cansaco"] > e0
    assert not any(e[0] in ("aliviar", "necessidade") for e in pol.corpo[0][1]["estimulos"]) and longe.mundo.necessidades == {}
    assert longe.idas_banheiro == [{"tick": 0, "de": FORA_LONGE, "para": (140, 64), "distancia": 137, "restante": 77,
                                    "continuacao": False}]
    # o alvo do banheiro fica pendente, como o `continuar`
    assert longe.resumo_mundo_fisico()["pendente"] == {"acao": "aliviar", "alvo": {"tipo": "banheiro", "x": 63, "y": 64, "id": None,
                                                                                   "de": None}}


def test_g_mec_sem_gancho_o_padrao_e_aqui():
    class SemGancho(Roteiro):
        escolher_alvo = None
    pol = SemGancho([AcaoPet.ALIVIAR])
    m = fm()(pol, CONFIG_PADRAO, 101)
    m.pet = FORA_LONGE
    m.avancar(15)
    assert m.alivios[0]["alvo"] == "aqui" and m.pet == FORA_LONGE


# ================================================================== G-CONS
def _sinal(pol: Roteiro) -> int:
    antes, (_, _, depois) = pol.obs[0], pol.corpo[0]
    cc = CONFIG_CONSEQUENCIA
    return lb.sinal_corpo(antes.corpo, depois.corpo, DRIVES_SINAL, cc.ganho, S, dict(cc.pesos_drives_corpo))


@pytest.mark.parametrize("vontade", [240000, 360000])
def test_g_cons_o_limpador_faz_o_banheiro_melhor_na_hora(vontade):
    """o sinal imediato do aliviar (o do corpo, sobre os receptores): com o limpador, maior dentro do banheiro que fora; sem ele, igual"""
    sinais = {}
    for limp in (False, True):
        for onde, pet in (("dentro", DENTRO), ("fora", FORA_LONGE)):
            m, pol = motor_roteiro([AcaoPet.ALIVIAR], "aqui", cbh=CBL if limp else CB, pet=pet, vontade=vontade)
            m.avancar(15)
            sinais[limp, onde] = _sinal(pol)
    assert sinais[True, "dentro"] > sinais[True, "fora"]
    assert sinais[False, "dentro"] == sinais[False, "fora"] == sinais[True, "fora"]


# ================================================================== o dono que acaricia e o G-CRED
def test_g_cred_o_carinho_vai_a_decisao_de_aliviar_e_fica_fora_do_orcamento():
    v, car = vida(fp_lobos(CB_PERTO, espiao=True), CB_PERTO, dias=4, carinho=True)
    m = v.motor
    dentro = [a for a in m.alivios if a["dentro"]]
    assert dentro and car.feitos == len(dentro) == m.alivios_dentro
    # um carinho no primeiro passo do dono depois de cada alivio dentro (o passo do dono e o intervalo: 15)
    assert car.ticks == [a["tick"] + 15 for a in dentro]
    cerebro = m.politica._pm.cerebro
    assert cerebro.creditos == [AcaoPet.ALIVIAR] * car.feitos          # cada carinho creditado a decisao de aliviar
    dec = {d["tick"]: d for d in m.decisoes_mundo}
    assert all(max(t for t in dec if t < tc) == tc - 15 and dec[tc - 15]["acao"] == "aliviar" for tc in car.ticks)
    # fora do orcamento (BN-2): o dono gastou o orcamento inteiro; os carinhos vieram a mais, no log
    assert v.interacoes == 16 * 4
    gestos = sum(1 for e in m.log if e.tipo in ("acao_usuario", "deixar_comida", "deixar_bola"))
    assert gestos == v.interacoes + car.feitos
    assert sum(1 for e in m.log if e.tipo == "acao_usuario" and e.valor == "acariciar") >= car.feitos


def test_sem_alivio_dentro_o_dono_nao_acaricia():
    v, car = vida(fp_instinto(), CB, dias=2, carinho=True)
    assert all(not a["dentro"] for a in v.motor.alivios) and car.feitos == 0


# ================================================================== G1
@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
@pytest.mark.parametrize("cbh", [CB, CBL, CB_PERTO, replace(CB_PERTO, limpador=True)], ids=["B", "BL", "perto", "perto_L"])
def test_g1_replay_bit_a_bit(cerebro, cbh):
    fp = fp_instinto(cbh) if cerebro == "instinto" else fp_lobos(cbh)
    v, car = vida(fp, cbh, carinho=True)
    m = v.motor
    assert m.alivios
    r = reproduzir_mundo(m.log, fp, semente=101, fabrica_motor=fm(cbh))
    assert texto(r.resumo_mundo_fisico()) == texto(m.resumo_mundo_fisico())
    assert texto(r.estado()) == texto(m.estado()) and texto(r.mundo.resumo()) == texto(m.mundo.resumo())
    assert texto(r.politica.estado_interno()) == texto(m.politica.estado_interno())


def test_g1_no_layout_afastado_com_o_relapso():
    cm = replace(CM, layout=LAYOUT_MUNDO_AFASTADO)
    fp = fp_lobos(CB_PERTO, cm)
    v, _ = vida(fp, CB_PERTO, semente=202, dono="relapso", lugar="longe", carinho=True, cm=cm)
    r = reproduzir_mundo(v.motor.log, fp, semente=202, fabrica_motor=fm(CB_PERTO, cm))
    assert texto(r.resumo_mundo_fisico()) == texto(v.motor.resumo_mundo_fisico())


def test_as_quedas_nao_dependem_do_banheiro():
    """o mundo (as arvores) sorteia o mesmo com e sem o banheiro: as necessidades tem contador proprio e nao mexem no fluxo do mundo"""
    com, _ = vida(fp_instinto(), CB, dias=2)
    d = DonoComLugar(criar_dono("atencioso"), "comedouro", 101, "atencioso", CM)
    fab = lambda p, cfg, s: com_corpo(MotorMundo)(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                   cfg_corpo=CONFIG_CORPO_DRIVES)
    sem = simular_vida_mundo("t", d, PoliticaInstintoMundo(CONFIG_PADRAO), 101, 2, 32, fab, rotulo_dono="atencioso").motor
    chave = lambda q: (q["tick"], q["arvore"], q["sorteadas"], q["pontos"])  # noqa: E731
    assert [chave(q) for q in com.motor.quedas] == [chave(q) for q in sem.quedas]


def test_g1_grupo_com_o_banheiro():
    """dois pets no mesmo mundo, os dois com o banheiro: as necessidades sao do Mundo (a de um incomoda o outro na mesma zona), e o
    replay do grupo refaz tudo"""
    fabricas = {i: (fp_instinto(CB_PERTO), fm(CB_PERTO)) for i in ("A", "B")}
    sementes = sementes_do_grupo(303, CONFIG_GRUPO_LIGADA.ids)
    pets = [PetDoGrupo(i, 0, fp, f, DonoComLugar(criar_dono("atencioso"), "perto", sementes[i], "atencioso", CM), "atencioso",
                       "instinto") for i, (fp, f) in fabricas.items()]
    g = simular_grupo(CM, 303, pets, 2)
    assert all(g.motores[i].alivios for i in ("A", "B")) and g.motores["A"].mundo.necessidades is g.motores["B"].mundo.necessidades
    r = reproduzir_grupo(g.registro, fabricas, CM)
    assert texto(r.resumo()) == texto(g.resumo())
    assert all(texto(r.motores[i].resumo_mundo_fisico()) == texto(g.motores[i].resumo_mundo_fisico()) for i in ("A", "B"))


# ================================================================== o contrato da bancada
def test_os_alivios_seguem_o_contrato_da_bancada():
    v, car = vida(fp_lobos(CB_PERTO), CB_PERTO, dias=4, carinho=True)
    al = v.motor.alivios
    assert al and all(set(a) == CHAVES_ALIVIO for a in al)
    assert all(type(a["tick"]) is int and a["tick"] % 15 == 0 and a["alvo"] in ("banheiro", "aqui") for a in al)
    assert all(not a["recolhido"] for a in al)                              # sem o limpador
    med = bv.medidas_banheiro_de([(a["tick"], a["dentro"], a["urgente"]) for a in al], 4)
    assert med["alivios"] == len(al) and len(med["por_dia"]) == 4
    assert v.motor.estado()["banheiro"] == {"alivios": len(al), "alivios_dentro": sum(a["dentro"] for a in al),
                                            "necessidades": len(v.motor.mundo.necessidades),
                                            "na_zona": v.motor.necessidades_na_zona()}
    assert TICKS_POR_DIA % 15 == 0
