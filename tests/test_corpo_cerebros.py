"""V2, corpo, etapa 5: o cerebro A no corpo (docs/TAREFA_V2_CORPO_DRIVES.md, secoes 9 a 11; secao 14, linha 5).

O `sinal_corpo` sobre os receptores (a conta de exemplo da secao 9, a igualdade com o N3 nos drives de hoje, os pesos w_d e a janela da
A2.4), os canais novos (a soma telescopica e as rotas), as entradas novas (prior 0: a decisao de hoje; a regra da L1 com o canal do
corpo, conta exata), o gancho (o credito espera o consequencia_corpo ou o consequencia_mundo, uma chamada por decisao), o embrulho
(PoliticaComMotivo repassa os ganchos do corpo) e o G-HOJE (a) do sinal: em malha aberta, o sinal pelo corpo contra o sinal do N3 do
motor de hoje, decisao a decisao; e, em malha fechada, o P1 com a chave do corpo e o P1 de hoje no mesmo motor com o corpo sao a mesma
vida. So as sementes dos testes.

As sub-chaves da etapa 6 (`drives_novos`, `gestos`) ainda falham alto na ConfigCorpo; os testes das entradas novas fabricam a chave
(`_cc_futura`) para exercitar o lado do cerebro, com percepcoes montadas a mao. Nenhum motor produz essas percepcoes ainda.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.ambiente import DonoComBola, MotorAmbiente, PoliticaInstintoBola  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS,  # noqa: E402
                            CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigConsequencia, ConfigCorpo)
from digilab.corpo import Corpo, div_arred  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.educacao import reproduzir_educacao  # noqa: E402
from digilab.events import ACOES_PET_HOJE, FRUTAS, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.frutas import MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas, simular_vida_frutas  # noqa: E402
from digilab.motivo import PoliticaComMotivo  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, fabricas_mundo, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import PoliticaLobos, _RngSonda  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto, Transicao  # noqa: E402
from digilab.treino import MotorComFeedback, reproduzir_com_feedback, simular_vida  # noqa: E402

CFG = CONFIG_PADRAO
S = CONFIG_LOBOS.escala
C = ConfigCorpo().escala
SO_QUIMICA = ConfigCorpo(ligada=True)
COM_ORGAOS = ConfigCorpo(ligada=True, digestao=True, vida=True)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (101, 202, 303)                     # so dos testes
CL_T3 = bv.cfg_lobos_do_ponto("T3")            # o aprendiz da validacao unica (aprendizado ligado, teto 16 S)
CC = CONFIG_CONSEQUENCIA
CC_CANAIS = replace(CC, canais_ligados=True)
CC_JANELA = replace(CC, pesos_janela=True)
CM = CONFIG_MUNDO_LIGADA
HOJE = ("fome", "higiene", "energia")          # os drives do N3 (cc.drives = (0, 1, 2)), pelo nome do receptor


# ================================================================== ajudas
def _cc_futura(**kw) -> ConfigCorpo:
    """A ConfigCorpo com as sub-chaves da etapa 6 (drives_novos, gestos), que o __post_init__ ainda recusa: fabricada campo a campo, so
    para exercitar o lado do cerebro. Nenhum motor a aceita."""
    cc = object.__new__(ConfigCorpo)
    for f in fields(ConfigCorpo):
        object.__setattr__(cc, f.name, kw.get(f.name, f.default))
    return cc


TODOS_NOVOS = _cc_futura(ligada=True, drives_novos=True, gestos=True)


def pc(fome=S, higiene=S, energia=S, humor=S, saude=S, **novos) -> PercepcaoCorpo:
    return PercepcaoCorpo(fome=fome, higiene=higiene, energia=energia, humor=humor, saude=saude, **novos)


def obs_de(fome=0.9, higiene=0.9, energia=0.8, humor=0.5, saude=1.0, sujeira=0.0, dormindo=0.0, hora=0.5, ticks=0, corpo=None,
           **kw) -> Observacao:
    return Observacao(vetor_estado=(fome, higiene, energia, humor, saude, sujeira, dormindo, hora), ticks_desde_cuidado=ticks,
                      total_cuidados=0, corpo=corpo, **kw)


def corpo_da_obs(o: Observacao, **novos) -> Observacao:
    """a percepcao do corpo que o motor daria a este estado: receptor = arred(h * S) nos drives de hoje (= S - div_arred(q S, C))"""
    return replace(o, corpo=pc(**{d: lb.arred(o.vetor_estado[i] * S) for i, d in enumerate(lb.RECEPTORES_HOJE)}, **novos))


def _fabrica(mundo: str, cc: ConfigCorpo | None):
    if mundo == "padrao":
        cls, kw = MotorComFeedback, {}
    elif mundo == "bola":
        cls, kw = MotorAmbiente, dict(obediencia_desligada=True, cfg_bola=CONFIG_BOLA_LIGADA)
    else:
        cls, kw = MotorFrutas, dict(obediencia_desligada=True, cfg_frutas=CONFIG_FRUTAS_LIGADA)
    if cc is None:
        return lambda p, cfg, s: cls(p, cfg, s, **kw)
    k = com_corpo(cls)
    return lambda p, cfg, s: k(p, cfg, s, cfg_corpo=cc, **kw)


def _vida(mundo: str, dono: str, semente: int, cc_motor: ConfigCorpo | None, fp, dias: int = 3):
    fm = _fabrica(mundo, cc_motor)
    if mundo == "frutas":
        return simular_vida_frutas(dono, criar_dono(dono), fp(CFG), semente, dias, 16 * dias, fm, OfertasFrutas(CONFIG_FRUTAS_LIGADA)).motor
    d = DonoComBola(dono, CONFIG_BOLA_LIGADA) if mundo == "bola" else criar_dono(dono)
    return simular_vida(dono, d, fp(CFG), semente, dias, 16 * dias, fabrica_motor=fm, rotulo_dono=dono).motor


def _cerebro(mundo: str, cc_corpo: ConfigCorpo | None, cl=CL_T3) -> PoliticaLobos:
    kw = {"padrao": {}, "bola": {"cfg_bola": CONFIG_BOLA_LIGADA}, "frutas": {"cfg_frutas": CONFIG_FRUTAS_LIGADA}}[mundo]
    return PoliticaLobos(CFG, cl, cfg_corpo=cc_corpo, **kw)


def _fabrica_p1(mundo: str, cc_corpo: ConfigCorpo | None, ccons: ConfigConsequencia, pols: list):
    def fp(cfg=None):
        c = _cerebro(mundo, cc_corpo)
        pols.append(c)
        return bv.PoliticaDoBraco(c, bv.braco_de("P1"), ccons)
    return fp


def _sem_chaves_do_corpo(d: dict) -> dict:
    """o estado interno sem o que so a chave do corpo acrescenta (a conta do sinal no motivo e o bloco `corpo`)"""
    d = {k: v for k, v in d.items() if k != "corpo"}
    d["motivos"] = [{k: v for k, v in m.items() if k != "sinal_corpo"} for m in d["motivos"]]
    return d


def _resumo(m, politica: dict) -> str:
    d = {"log": m.log.para_jsonl(), "estado": m.estado(), "bruto": repr(m._estado), "acoes": m.acoes_recentes(10**9),
         "rng": [m._rng_ambiente.getstate(), m._rng_politica.getstate()], "politica": politica}
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=repr).encode()).hexdigest()


# ================================================================== o sinal pelo corpo
def test_sinal_corpo_a_conta_de_exemplo_da_secao_9():
    """brincar com a bola com o tedio em 0,75 e o cansaco em 0,20 (ganho 4): +1440; o N3 de hoje so ve o cansaco: -34"""
    q = {"tedio": (337500, 202500), "cansaco": (90000, 99000)}
    leit = {n: tuple(div_arred(v * S, C) for v in par) for n, par in q.items()}
    assert leit == {"tedio": (768, 461), "cansaco": (205, 225)}
    antes = pc(energia=S - 205, tedio=768, solidao=0, estresse=0)
    depois = pc(energia=S - 225, tedio=461, solidao=0, estresse=0)
    drives = HOJE + ("tedio", "solidao", "estresse")
    c = lb.contribuicoes_corpo(antes, depois, drives, S)
    assert c == {"fome": 0, "higiene": 0, "energia": 205 ** 2 - 225 ** 2, "tedio": 768 ** 2 - 461 ** 2, "solidao": 0, "estresse": 0}
    assert sum(c.values()) == 368703
    assert lb.sinal_corpo(antes, depois, drives, 4, S) == 1440
    assert lb.sinal_corpo(antes, depois, HOJE, 4, S) == -34
    canais = lb.sinal_corpo_canais(antes, depois, drives, 4, S)
    assert canais == {"fome": 0, "higiene": 0, "energia": -34, "tedio": 1474, "solidao": 0, "estresse": 0}
    assert sum(canais.values()) == 1440


def _estado_aleatorio(rng: random.Random, cc: ConfigCorpo) -> tuple[Observacao, Corpo]:
    q = {n: rng.choice((0, C, rng.randrange(C + 1), rng.randrange(C + 1))) for n in ("fome", "desconforto", "cansaco", "tristeza", "dano")}
    corpo = Corpo(q, CFG, cc)
    h = corpo.drives()
    o = Observacao(vetor_estado=(h["fome"], h["higiene"], h["energia"], h["humor"], h["saude"], 0.0, 0.0, 0.5), ticks_desde_cuidado=0,
                   total_cuidados=0, corpo=PercepcaoCorpo(**corpo.receptores()))
    return o, corpo


@pytest.mark.parametrize("ganho", [0, 1, 4, 16, 64])
def test_sinal_corpo_nos_drives_de_hoje_e_o_numero_do_n3(ganho):
    """os receptores de um corpo qualquer e o Estado que ele le dao o mesmo sinal (N3 e E2): o receptor e S - div_arred(q S, C), e
    S - arred(h S) do drive lido da o mesmo inteiro (q x 64 / 28125 nunca cai a menos de 1/56250 de um meio)"""
    rng = random.Random(11)
    cc = replace(CC, ganho=ganho)
    for _ in range(3000):
        a, _ = _estado_aleatorio(rng, SO_QUIMICA)
        d, _ = _estado_aleatorio(rng, SO_QUIMICA)
        t = Transicao(a, AcaoPet.COMER, d)
        assert lb.sinal_corpo(a.corpo, d.corpo, HOJE, ganho, S) == lb.sinal_homeostatico(t, S, cc)
        assert lb.sinal_corpo(a.corpo, d.corpo, HOJE + ("humor",), ganho, S) == lb.sinal_homeostatico_fruta(a, d, S, cc)
        assert lb.faltas_corpo(a.corpo, HOJE + ("humor",), S) == {
            lb.CANAL_DO_DRIVE[i]: v for i, v in lb.faltas_da_observacao(a, (0, 1, 2, 3), S).items()}


def test_pesos_w_d_e_a_janela_da_a24():
    rng = random.Random(22)
    pj = {"fome": S, "higiene": S // 4, "energia": 700, "humor": 300}
    pj_idx = {0: S, 1: S // 4, 2: 700, 3: 300}
    for _ in range(500):
        a, _ = _estado_aleatorio(rng, SO_QUIMICA)
        d, _ = _estado_aleatorio(rng, SO_QUIMICA)
        t = Transicao(a, AcaoPet.COMER, d)
        # w_d = 1 e a janela: o sinal ponderado de hoje (delta_ponderado)
        assert lb.sinal_corpo(a.corpo, d.corpo, HOJE, 4, S, None, pj) == lb.sinal_homeostatico(t, S, CC, pj_idx)
        # w_d inteiro multiplica a parcela do drive
        c1 = lb.contribuicoes_corpo(a.corpo, d.corpo, HOJE, S, None, pj)
        c3 = lb.contribuicoes_corpo(a.corpo, d.corpo, HOJE, S, {"fome": 1, "higiene": 3, "energia": 0}, pj)
        assert c3 == {"fome": c1["fome"], "higiene": 3 * c1["higiene"], "energia": 0}
        assert lb.sinal_corpo(a.corpo, d.corpo, HOJE, 4, S, {"fome": 1, "higiene": 3, "energia": 0}, pj) == div_arred(4 * sum(c3.values()), S)
    # os pesos de hoje na config: todos 1, nos drives de hoje (sem a saude) e nos drives novos do sinal (sem o susto)
    assert dict(CC.pesos_drives_corpo) == {d: 1 for d in ("fome", "higiene", "energia", "humor") + lb.DRIVES_NOVOS_SINAL}
    lb.validar_parametros_consequencia(CC)


def test_falhas_altas_do_sinal():
    antes, depois = pc(), pc()
    with pytest.raises(RuntimeError, match="nao existe"):
        lb.sinal_corpo(antes, depois, HOJE + ("tedio",), 4, S)                        # o receptor do tedio ainda nao existe
    with pytest.raises(ValueError, match="fora de inteiros"):
        lb.sinal_corpo(pc(fome=S + 1), depois, HOJE, 4, S)
    with pytest.raises(ValueError, match="fora de inteiros"):
        lb.sinal_corpo(pc(fome=1.0), depois, HOJE, 4, S)
    with pytest.raises(KeyError):
        lb.sinal_corpo(antes, depois, HOJE, 4, S, {"fome": 1})                       # drive sem w_d
    with pytest.raises(ValueError, match="ganho"):
        lb.sinal_corpo(antes, depois, HOJE, -1, S)
    with pytest.raises(ValueError, match="repetido"):
        ConfigConsequencia(pesos_drives_corpo=(("fome", 1), ("fome", 2)))
    with pytest.raises(ValueError, match="inteiro"):
        ConfigConsequencia(pesos_drives_corpo=(("fome", -1),))
    with pytest.raises(ValueError, match="inteiro"):
        ConfigConsequencia(pesos_drives_corpo=(("fome", 1.0),))


# ================================================================== os canais novos
def test_canais_novos_somam_o_escalar_e_vao_ao_corpo():
    rng = random.Random(33)
    drives = HOJE + ("humor",) + lb.DRIVES_NOVOS_SINAL
    assert set(lb.ROTA_CANAIS_CORPO) == set(lb.DRIVES_NOVOS_SINAL) and set(lb.ROTA_CANAIS_CORPO.values()) == {"corpo"}
    assert lb.ROTA_CANAIS["humor"] == "fruta"                                       # o humor da fruta continua na fruta
    for _ in range(3000):
        def p():
            return pc(*(rng.randrange(S + 1) for _ in range(5)), **{r: rng.randrange(S + 1) for r in lb.RECEPTORES_NOVOS})
        a, d = p(), p()
        for ganho in (1, 4, 64):
            canais = lb.sinal_corpo_canais(a, d, drives, ganho, S)
            assert list(canais) == list(drives)
            assert sum(canais.values()) == lb.sinal_corpo(a, d, drives, ganho, S)
            c = lb.contribuicoes_corpo(a, d, drives, S)
            assert all(abs(canais[k] - div_arred(ganho * c[k], S)) <= 1 for k in drives)


# ================================================================== as entradas novas
def test_receptores_novos_pelas_chaves():
    assert lb.receptores_novos(SO_QUIMICA, False) == lb.receptores_novos(COM_ORGAOS, True) == ()
    assert lb.receptores_novos(_cc_futura(ligada=True, drives_novos=True), False) == ("tedio", "solidao", "estresse")
    assert lb.receptores_novos(_cc_futura(ligada=True, drives_novos=True), True) == ("tedio", "curiosidade", "solidao", "estresse")
    assert lb.receptores_novos(_cc_futura(ligada=True, gestos=True), True) == ("dor", "susto")
    assert lb.receptores_novos(TODOS_NOVOS, True) == lb.RECEPTORES_NOVOS[:6]
    # o banheiro (TAREFA_V2_BANHEIRO): a vontade e o conforto no fim
    assert lb.receptores_novos(_cc_futura(ligada=True, drives_novos=True, gestos=True, banheiro=True), True) == lb.RECEPTORES_NOVOS


def test_pesos_novos_so_nas_regras_de_tempo_livre():
    """3 regras x 7 acoes x 6 entradas = 126 com o mundo fisico (curiosidade); sem ele, 5 entradas; no padrao so o tempo_livre"""
    casos = [
        ({}, ("tempo_livre",), 5),
        ({"cfg_bola": CONFIG_BOLA_LIGADA, "cfg_frutas": CONFIG_FRUTAS_LIGADA}, lb.REGRAS_ENTRADAS_CORPO, 5),
        ({"cfg_mundo": CM}, lb.REGRAS_ENTRADAS_CORPO, 6),
    ]
    k2 = replace(CL_T3, w0_info=256)
    for kw, regras, n in casos:
        sem = PoliticaLobos(CFG, k2, **kw)
        com = PoliticaLobos(CFG, k2, cfg_corpo=TODOS_NOVOS, **kw)
        ei = com.estado_interno()
        assert set(ei["pesos_corpo"]) == set(regras)
        assert com.n_pesos() - sem.n_pesos() == len(regras) * len(ACOES_PET_HOJE) * n
        assert all(w == 0 for g in ei["pesos_corpo"].values() for v in g.values() for w in v)
        assert com.n_pesos() < k2.maximo_pesos
    frutas = PoliticaLobos(CFG, k2, cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_corpo=TODOS_NOVOS)
    assert PoliticaLobos(CFG, k2, cfg_frutas=CONFIG_FRUTAS_LIGADA).n_pesos() == 763 and frutas.n_pesos() == 868
    mundo = PoliticaLobos(CFG, k2, cfg_mundo=CM, cfg_corpo=TODOS_NOVOS)
    assert mundo.n_pesos() - PoliticaLobos(CFG, k2, cfg_mundo=CM).n_pesos() == 126
    # sem drives novos (a etapa 5 de hoje): nenhum peso a mais e o estado interno so ganha o bloco `corpo`
    so = PoliticaLobos(CFG, k2, cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_corpo=COM_ORGAOS)
    assert so.n_pesos() == 763 and "pesos_corpo" not in so.estado_interno()
    assert so.estado_interno()["corpo"] == {"receptores_novos": [], "canais_novos": []}


def _obs_aleatoria(rng: random.Random, receptores: tuple) -> Observacao:
    v = tuple(rng.random() for _ in range(8))
    v = v[:6] + (float(rng.random() < 0.2),) + v[7:]
    pres = tuple(float(rng.random() < 0.4) for _ in FRUTAS)
    o = Observacao(vetor_estado=v, ticks_desde_cuidado=rng.choice((0, 30, 200, 500)), total_cuidados=0,
                   bola=float(rng.random() < 0.3), fruta=rng.random() if any(pres) else 0.0, frutas_cenario=pres)
    return corpo_da_obs(o, **{r: rng.randrange(S + 1) for r in receptores})


@pytest.mark.parametrize("aprende", [False, True])
def test_no_prior_as_entradas_novas_nao_mudam_a_decisao(aprende):
    """3000 observacoes (todas as regras): o cerebro com as entradas novas no prior decide como o de hoje, com a mesma rng"""
    cl = CL_T3 if aprende else CONFIG_LOBOS
    kw = {"cfg_bola": CONFIG_BOLA_LIGADA, "cfg_frutas": CONFIG_FRUTAS_LIGADA}
    novo = PoliticaLobos(CFG, cl, cfg_corpo=TODOS_NOVOS, **kw)
    hoje = PoliticaLobos(CFG, cl, **kw)
    rng = random.Random(44)
    r1, r2 = random.Random(55), random.Random(55)
    regras = set()
    for _ in range(3000):
        o = _obs_aleatoria(rng, novo._receptores_novos)
        assert novo.agir(o, r1) is hoje.agir(replace(o, corpo=None), r2)
        assert r1.getstate() == r2.getstate()
        assert novo.motivos[-1]["pesos"] == hoje.motivos[-1]["pesos"]
        regras.add(novo.ultima_regra)
    assert regras >= set(lb.REGRAS_ENTRADAS_CORPO) | {"sono_noite", "pedido_necessidade", "fome_moderada"}


def _decisao_brincar(lob: PoliticaLobos, **novos) -> Observacao:
    """uma decisao de tempo livre (fome, higiene e energia altas) em que o sorteio cai em brincar"""
    o = corpo_da_obs(obs_de(), **novos)
    assert lob.agir(o, _RngSonda(0.8)) is AcaoPet.BRINCAR and lob.ultima_regra == "tempo_livre"
    return o


@pytest.mark.parametrize("ccons", [CC, CC_CANAIS], ids=["escalar", "canais"])
def test_entradas_novas_aprendem_pelo_sinal_do_corpo_conta_exata(ccons):
    """a conta da secao 9 numa decisao: brincar baixa o tedio de 768 a 461 e o cansaco sobe de 205 a 225, f = +1440, creditado no
    gancho do corpo; as entradas novas da regra mudam pela regra da L1 (dw = div_arred(f passo X_j (S 1[a=a*] - P_a), S S W_a))"""
    lob = PoliticaLobos(CFG, CL_T3, cfg_corpo=TODOS_NOVOS)
    novos = {"tedio": 768, "solidao": 300, "estresse": 100, "dor": 0, "susto": 40}
    antes = _decisao_brincar(lob, **novos)
    assert antes.corpo.energia == S - 205
    depois = corpo_da_obs(obs_de(energia=0.78, humor=0.6), **{**novos, "tedio": 461})
    assert depois.corpo.energia == S - 225
    t = Transicao(antes, AcaoPet.BRINCAR, depois)
    f_n3 = lb.sinal_homeostatico(t, S, ccons)
    assert f_n3 == -34
    lob.observar_consequencia(t, f_n3, ccons)
    assert not lob.pesos_mudaram()                                                   # o credito espera o gancho
    registro = lob.estado_interno()["aprendizado"]["corpo_pendente"]
    assert registro["corpo"]["X"] == [768, 300, 100, 0, 40]                          # a leitura de cada receptor novo
    lob.consequencia_corpo(AcaoPet.BRINCAR, {"acao": "brincar", "estimulos": [("pet", "brincar")]}, depois)
    sc = lob.motivos[-1]["sinal_corpo"]
    assert sc["f"] == 1440
    assert sc["drives"] == {"fome": 0, "higiene": 0, "energia": -8600, "tedio": 377303, "solidao": 0, "estresse": 0, "dor": 0}
    ei = lob.estado_interno()
    passo, X = CL_T3.passo, registro["corpo"]["X"]
    for a in registro["candidatos"]:
        fator = (S if a == registro["acao"] else 0) - registro["P"][a]
        esperado = [div_arred(1440 * passo * x * fator, S * S * registro["W"][a]) for x in X]
        assert ei["pesos_corpo"]["tempo_livre"][a] == esperado, a
    assert any(w != 0 for w in ei["pesos_corpo"]["tempo_livre"]["brincar"])
    if ccons.canais_ligados:
        canais = ei["canais"]
        assert canais["por_canal"] == {"fome": 0, "higiene": 0, "energia": -34, "humor": 0, "tedio": 1474, "solidao": 0,
                                       "estresse": 0, "dor": 0}
        assert canais["por_alvo"] == {"corpo": 1440, "fruta": 0}
    # o mesmo sinal pelo dono (o elogio na decisao seguinte) tambem chega as entradas novas: sao entradas da tabela da regra
    lob2 = PoliticaLobos(CFG, CL_T3, cfg_corpo=TODOS_NOVOS)
    _decisao_brincar(lob2, **novos)
    lob2.observar(Transicao(antes, AcaoPet.BRINCAR, depois))
    lob2.consequencia_corpo(AcaoPet.BRINCAR, {"acao": "brincar", "estimulos": [("pet", "brincar")]}, depois)
    lob2.receber_acao_dono(AcaoUsuario.ELOGIAR, 1)
    assert lob2.estado_interno()["pesos_corpo"]["tempo_livre"]["brincar"] != [0] * 5


def test_entradas_novas_aprendidas_pesam_na_decisao():
    """um peso aprendido na entrada do tedio soma (w / S) x leitura / S ao peso de brincar no tempo livre, e muda a decisao com o mesmo
    u; fora das regras de tempo livre, nada"""
    lob = PoliticaLobos(CFG, CL_T3, cfg_corpo=TODOS_NOVOS)
    lob._pesos_corpo["tempo_livre"][AcaoPet.BRINCAR] = [8 * S, 0, 0, 0, 0]          # como se tivesse aprendido: o tedio puxa brincar
    hoje = PoliticaLobos(CFG, CL_T3)
    o = corpo_da_obs(obs_de(), tedio=768, solidao=0, estresse=0, dor=0, susto=0)
    assert hoje.agir(replace(o, corpo=None), _RngSonda(0.5)) is AcaoPet.EXPLORAR
    assert lob.agir(o, _RngSonda(0.5)) is AcaoPet.BRINCAR
    ph, pc_ = hoje.motivos[-1]["pesos"], lob.motivos[-1]["pesos"]
    assert pc_["brincar"] == ph["brincar"] + 8.0 * (768 / S)
    assert all(pc_[a] == ph[a] for a in ph if a != "brincar")
    assert lob.motivos[-1]["aprendido_corpo"]["brincar"] == [8.0 * (768 / S), 0.0, 0.0, 0.0, 0.0]
    noite = corpo_da_obs(obs_de(hora=0.95, energia=0.5), tedio=768, solidao=0, estresse=0, dor=0, susto=0)
    lob._acao_sem_gancho = None
    lob.agir(noite, _RngSonda(0.5))
    assert lob.ultima_regra not in lb.REGRAS_ENTRADAS_CORPO and "aprendido_corpo" not in lob.motivos[-1]


def test_entradas_novas_cortadas_no_teto():
    lob = PoliticaLobos(CFG, replace(CL_T3, teto=3, passo=4096), cfg_corpo=TODOS_NOVOS)
    novos = {"tedio": 768, "solidao": 300, "estresse": 100, "dor": 0, "susto": 40}
    antes = _decisao_brincar(lob, **novos)
    depois = corpo_da_obs(obs_de(energia=0.78), **{**novos, "tedio": 0})
    t = Transicao(antes, AcaoPet.BRINCAR, depois)
    lob.observar_consequencia(t, lb.sinal_homeostatico(t, S, CC), CC)
    lob.consequencia_corpo(AcaoPet.BRINCAR, {"acao": "brincar", "estimulos": [("pet", "brincar")]}, depois)
    pesos = lob.estado_interno()["pesos_corpo"]["tempo_livre"]
    assert max(abs(w) for v in pesos.values() for w in v) == 3 and lob.pesos_no_teto() > 0


def test_motivo_cita_so_o_que_tem_fator():
    """as entradas novas aprendidas nao tem fator na expressao: o motivo falha alto em vez de esconder a causa (etapa 6)"""
    from digilab.motivo import motivo_lobos
    lob = PoliticaLobos(CFG, CL_T3, cfg_corpo=TODOS_NOVOS)
    novos = {"tedio": 768, "solidao": 300, "estresse": 100, "dor": 0, "susto": 40}
    reg = lob.motivos
    _decisao_brincar(lob, **novos)
    assert reg[-1]["percepcao_corpo"] == {k: v / S for k, v in novos.items()}
    assert all(v == 0.0 for termos in reg[-1]["aprendido_corpo"].values() for v in termos)
    registro = dict(reg[-1])
    motivo_lobos(registro, 0, None)                                                  # sem nada aprendido no corpo, como hoje
    registro["aprendido_corpo"] = {"brincar": [0.5, 0, 0, 0, 0], "ocioso": [0.0] * 5, "explorar": [0.0] * 5, "chamar_atencao": [0.0] * 5}
    registro["contribuicoes"] = {**registro["contribuicoes"], "impulsos": {"ocioso": 10.0, "explorar": 0.0, "brincar": 0.0,
                                                                            "chamar_atencao": 0.0}}
    with pytest.raises(NotImplementedError, match="entradas novas"):
        motivo_lobos(registro, 0, None)


# ================================================================== o gancho
def _novo_e_decidido(cl=CL_T3, cc_corpo=SO_QUIMICA):
    lob = PoliticaLobos(CFG, cl, cfg_corpo=cc_corpo)
    antes = _decisao_brincar(lob)
    depois = corpo_da_obs(obs_de(energia=0.78))
    return lob, Transicao(antes, AcaoPet.BRINCAR, depois), depois


OCORRIDO = {"acao": "brincar", "estimulos": [("pet", "brincar")]}


def test_gancho_uma_chamada_por_decisao():
    lob, t, depois = _novo_e_decidido()
    lob.observar_consequencia(t, lb.sinal_homeostatico(t, S, CC), CC)
    with pytest.raises(RuntimeError, match="ficou sem o gancho"):
        lob.agir(t.observacao, _RngSonda(0.8))                                       # a proxima decisao sem o gancho
    with pytest.raises(RuntimeError, match="gancho de dormir"):
        lob.consequencia_corpo(AcaoPet.DORMIR, {"acao": "dormir", "estimulos": []}, depois)
    lob, t, depois = _novo_e_decidido()
    lob.observar_consequencia(t, lb.sinal_homeostatico(t, S, CC), CC)
    lob.consequencia_corpo(AcaoPet.BRINCAR, OCORRIDO, depois)
    with pytest.raises(RuntimeError, match="segunda chamada"):
        lob.consequencia_corpo(AcaoPet.BRINCAR, OCORRIDO, depois)
    lob, t, depois = _novo_e_decidido(CONFIG_LOBOS)                                  # sem aprender (P0): o gancho e conferido igual
    lob.observar(t)
    with pytest.raises(RuntimeError, match="ficou sem o gancho"):
        lob.observar(t)


def test_gancho_falhas_altas():
    lob, t, depois = _novo_e_decidido()
    with pytest.raises(RuntimeError, match="f_S recebido"):
        lob.observar_consequencia(t, lb.sinal_homeostatico(t, S, CC) + 1, CC)
    lob, t, depois = _novo_e_decidido()
    with pytest.raises(RuntimeError, match="sem Observacao.corpo"):
        lob.observar_consequencia(replace(t, observacao_seguinte=replace(depois, corpo=None)), -34, CC)
    lob = PoliticaLobos(CFG, CL_T3, cfg_corpo=SO_QUIMICA)
    with pytest.raises(RuntimeError, match="sem o campo corpo"):
        lob.agir(obs_de(), _RngSonda(0.8))
    with pytest.raises(RuntimeError, match="sem decisao observada"):
        lob.consequencia_corpo(AcaoPet.BRINCAR, OCORRIDO, depois)
    with pytest.raises(ValueError, match="mesma S"):
        PoliticaLobos(CFG, CL_T3, cfg_corpo=_cc_futura(ligada=True, escala_receptor=512))
    with pytest.raises(RuntimeError, match="nao existe"):                          # chave com tedio, percepcao sem ele
        PoliticaLobos(CFG, CL_T3, cfg_corpo=TODOS_NOVOS).agir(corpo_da_obs(obs_de()), _RngSonda(0.8))
    # sem a chave do corpo o gancho nao faz nada (o cerebro de hoje num motor com o corpo)
    hoje = PoliticaLobos(CFG, CL_T3)
    hoje.consequencia_corpo(AcaoPet.BRINCAR, OCORRIDO, depois)
    assert not hoje.tem_corpo and not hoje.pesos_mudaram()
    # a chave do corpo desligada e o cerebro de hoje
    assert not PoliticaLobos(CFG, CL_T3, cfg_corpo=ConfigCorpo()).tem_corpo


def test_fruta_do_gancho_e_a_fruta_comida():
    """no mundo das frutas a E2 entra no sinal pelo corpo com a fruta que o motor avisou; um estimulo de fruta diferente falha alto"""
    lob = PoliticaLobos(CFG, CL_T3, cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_corpo=SO_QUIMICA)
    o = corpo_da_obs(obs_de(fome=0.6, humor=0.8, fruta=1.0, frutas_cenario=(1.0, 0.0, 0.0)))
    assert lob.agir(o, _RngSonda(1.0 - 1e-12)) is AcaoPet.COMER and lob.ultima_regra == "fruta_no_cenario"
    assert lob.escolher_fruta(["a"], {"a": 1.0}, 0.3) == "a"
    depois = corpo_da_obs(obs_de(fome=0.7, humor=0.7))
    t = Transicao(o, AcaoPet.COMER, corpo_da_obs(obs_de(fome=0.6, humor=0.8)))
    lob.observar_consequencia(t, lb.sinal_homeostatico(t, S, CC), CC)
    lob.fruta_comida("a", replace(depois, corpo=None))                              # o MotorFrutas manda o Estado, sem o corpo
    with pytest.raises(RuntimeError, match="nao e a fruta_comida"):
        lob.consequencia_corpo(AcaoPet.COMER, {"acao": "comer", "estimulos": [("pet", "comer")]}, depois)
    lob = PoliticaLobos(CFG, CL_T3, cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_corpo=SO_QUIMICA)
    assert lob.agir(o, _RngSonda(1.0 - 1e-12)) is AcaoPet.COMER
    lob.escolher_fruta(["a"], {"a": 1.0}, 0.3)
    lob.observar_consequencia(t, lb.sinal_homeostatico(t, S, CC), CC)
    lob.fruta_comida("a", replace(depois, corpo=None))
    lob.consequencia_corpo(AcaoPet.COMER, {"acao": "comer", "estimulos": [("pet", "comer"), ("fruta", "a")]}, depois)
    assert lob.motivos[-1]["sinal_corpo"]["f"] == lb.sinal_homeostatico_fruta(o, depois, S, CC)
    assert set(lob.motivos[-1]["sinal_corpo"]["drives"]) == {"fome", "higiene", "energia", "humor"}


# ================================================================== G-HOJE (a) do sinal, malha aberta
class Forcada:
    """o pet de teste: as acoes de uma vida de hoje, na ordem; guarda as transicoes, a fruta comida e o gancho do corpo"""

    nome = "forcada"

    def __init__(self, acoes) -> None:
        self._acoes = list(acoes)
        self.transicoes, self.frutas, self.ganchos = [], {}, []

    def agir(self, obs, rng):
        return self._acoes.pop(0)

    def observar(self, t) -> None:
        self.transicoes.append(t)

    def fruta_comida(self, fruta, obs) -> None:
        self.frutas[len(self.transicoes) - 1] = (fruta, obs)

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        self.ganchos.append((acao, ocorrido, obs_depois))

    def receber_acao_dono(self, acao, tick) -> None:
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome}


def _sinais_malha_aberta(mundo: str, dono: str, semente: int, cc: ConfigCorpo) -> list[tuple[int, int]]:
    """a vida de hoje rejogada com as acoes do pet forcadas no motor de hoje e no mesmo motor com o corpo; por decisao, (o sinal do N3
    de hoje, com a E2 no comer de fruta; o sinal pelo corpo no gancho)"""
    fp = {"padrao": lambda cfg=None: PoliticaInstinto(cfg or CFG),
          "bola": lambda cfg=None: PoliticaInstintoBola(cfg or CFG, CONFIG_BOLA_LIGADA),
          "frutas": lambda cfg=None: PoliticaInstintoFrutas(cfg or CFG, None, CONFIG_FRUTAS_LIGADA)}[mundo]
    hoje = _vida(mundo, dono, semente, None, fp)
    acoes = [a for _, a in hoje.acoes_recentes(10**9)]
    fa, fb = Forcada(acoes), Forcada(acoes)
    a = _fabrica(mundo, None)(fa, CFG, semente)
    b = _fabrica(mundo, cc)(fb, CFG, semente)
    for ev in hoje.log:
        if ev.tipo == "avanco":
            a._avancar(int(ev.valor))
            b._avancar(int(ev.valor))
        elif ev.tipo == "acao_usuario":
            a._aplicar_acao_usuario(AcaoUsuario(ev.valor))
            b._aplicar_acao_usuario(AcaoUsuario(ev.valor))
        else:
            raise ValueError(ev.tipo)
    assert a._estado == hoje._estado
    assert len(fb.ganchos) == len(fb.transicoes) == len(fa.transicoes) == len(acoes)
    assert {k: f for k, (f, _) in fa.frutas.items()} == {k: f for k, (f, _) in fb.frutas.items()}
    sinais = []
    for k, (ta, tb, (acao, oc, depois)) in enumerate(zip(fa.transicoes, fb.transicoes, fb.ganchos)):
        assert acao is ta.acao is tb.acao
        fruta = [e[1] for e in oc["estimulos"] if e[0] == "fruta"]
        assert fruta == ([fa.frutas[k][0]] if k in fa.frutas else [])
        if fruta:
            x = lb.sinal_homeostatico_fruta(ta.observacao, fa.frutas[k][1], S, CC)
            y = lb.sinal_corpo(tb.observacao.corpo, depois.corpo, HOJE + ("humor",), CC.ganho, S)
        else:
            x = lb.sinal_homeostatico(ta, S, CC)
            y = lb.sinal_corpo(tb.observacao.corpo, depois.corpo, HOJE, CC.ganho, S)
        sinais.append((x, y))
    return sinais


@pytest.mark.parametrize("cc", [SO_QUIMICA, COM_ORGAOS], ids=["quimica", "orgaos"])
@pytest.mark.parametrize("mundo", ["padrao", "bola", "frutas"])
def test_g_hoje_a_do_sinal_malha_aberta(mundo, cc):
    """secao 12: o sinal igual em >= 99% das decisoes; nas outras, a diferenca <= 3 div_arred(ganho (2S + 1), S)"""
    folga = 3 * div_arred(CC.ganho * (2 * S + 1), S)
    total = iguais = 0
    for dono in DONOS:
        for semente in SEMENTES:
            for x, y in _sinais_malha_aberta(mundo, dono, semente, cc):
                assert abs(x - y) <= folga, (mundo, dono, semente, x, y)
                total += 1
                iguais += x == y
    assert total and iguais / total >= 0.99, (iguais, total)


# ================================================================== malha fechada: o P1 com o corpo e o P1 de hoje no mesmo motor
@pytest.mark.parametrize("ccons", [CC, CC_CANAIS, CC_JANELA], ids=["escalar", "canais", "janela"])
@pytest.mark.parametrize("mundo", ["padrao", "bola", "frutas"])
def test_p1_com_o_corpo_e_o_p1_de_hoje_no_mesmo_motor(mundo, ccons):
    """sem drives novos e com w_d = 1 o sinal pelo corpo e o numero do N3: o cerebro com a chave do corpo, creditado no gancho, vive a
    mesma vida do cerebro de hoje, creditado na transicao (e na fruta_comida), no mesmo motor com o corpo; o estado interno so ganha a
    conta do sinal no motivo e o bloco `corpo`"""
    for dono in ("atencioso", "aleatorio"):
        p_hoje, p_corpo = [], []
        m_hoje = _vida(mundo, dono, 101, COM_ORGAOS, _fabrica_p1(mundo, None, ccons, p_hoje))
        m_corpo = _vida(mundo, dono, 101, COM_ORGAOS, _fabrica_p1(mundo, COM_ORGAOS, ccons, p_corpo))
        ei_hoje, ei_corpo = p_hoje[-1].estado_interno(), p_corpo[-1].estado_interno()
        assert p_corpo[-1].pesos_mudaram() and ei_corpo["aprendizado"]["n_atualizacoes"] > 0
        assert _resumo(m_hoje, ei_hoje) == _resumo(m_corpo, _sem_chaves_do_corpo(ei_corpo)), (mundo, dono)
        creditadas = [m for m in ei_corpo["motivos"] if "sinal_corpo" in m]
        assert len(creditadas) == len(ei_corpo["motivos"]) == m_corpo.consequencias
        if mundo == "frutas":
            assert ei_corpo["aprendizado"]["recompensas"].get("consequencia_fruta", 0) == len(m_corpo.consumos) > 0


@pytest.mark.parametrize("mundo", ["padrao", "bola", "frutas"])
def test_g1_replay_bit_a_bit_com_o_cerebro_no_corpo(mundo):
    for rotulo in ("P1", "P3"):
        def fp(cfg=None, rotulo=rotulo):
            return bv.PoliticaDoBraco(_cerebro(mundo, COM_ORGAOS), bv.braco_de(rotulo), CC_CANAIS)
        m = _vida(mundo, "atencioso", 202, COM_ORGAOS, fp)
        fm = _fabrica(mundo, COM_ORGAOS)
        if mundo == "padrao":
            r = reproduzir_com_feedback(m.log, fp, CFG, 202, fabrica_motor=fm)
        else:
            r = reproduzir_educacao(m.log, fp, CFG, 202, fabrica_motor=fm)
        assert _resumo(m, m.politica.estado_interno()) == _resumo(r, r.politica.estado_interno()), (mundo, rotulo)


# ================================================================== o mundo fisico com o corpo (mecanismo)
class Gravador:
    """o P1 do mundo fisico de hoje, gravando as chamadas do motor ao cerebro, na ordem"""

    nome = "lobos"

    def __init__(self, cerebro, ccons) -> None:
        self.c, self.cc, self.chamadas = cerebro, ccons, []

    def agir(self, obs, rng):
        estado = rng.getstate()
        a = self.c.agir(obs, rng)
        self.chamadas.append(("agir", obs, estado, a))
        return a

    def observar(self, t) -> None:
        f = lb.sinal_homeostatico(t, S, self.cc)
        self.chamadas.append(("consequencia", t, f))
        self.c.observar_consequencia(t, f, self.cc)

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        self.chamadas.append(("alvo", acao, candidatos, percepcao, u))
        return self.c.escolher_alvo(acao, candidatos, percepcao, u)

    def fruta_comida(self, fruta, obs) -> None:
        self.chamadas.append(("fruta", fruta, obs))
        self.c.fruta_comida(fruta, obs)

    def consequencia_mundo(self, acao, ocorrido, obs_depois) -> None:
        self.chamadas.append(("mundo", acao, ocorrido, obs_depois))
        self.c.consequencia_mundo(acao, ocorrido, obs_depois)

    def receber_acao_dono(self, acao, tick) -> None:
        return None

    def estado_interno(self) -> dict:
        return self.c.estado_interno()


@pytest.mark.parametrize("ccons", [CC, CC_JANELA], ids=["escalar", "janela"])
def test_mundo_fisico_com_o_corpo_credita_no_gancho_do_mundo(ccons):
    """as chamadas de uma vida do P1 no mundo fisico, rejogadas num cerebro com a chave do corpo (a percepcao do corpo montada do
    Estado), no arranjo do MotorCorpo com o mundo (#238): o consequencia_mundo antes, nas decisoes de explorar, comer e brincar, e o
    consequencia_corpo sempre, uma vez por decisao. As mesmas decisoes e os mesmos pesos; explorar, comer e brincar creditados no
    consequencia_mundo, o resto no consequencia_corpo"""
    gravadores = []

    def fab(cfg=None):
        g = Gravador(PoliticaLobos(cfg or CFG, CL_T3, cfg_mundo=CM), ccons)
        gravadores.append(g)
        return g

    fp, fm = fabricas_mundo(CM, fab, efeito_frutas={"a": -0.1, "b": 0.0, "c": 0.1})
    simular_vida_mundo("relapso", DonoComLugar(criar_dono("relapso"), "perto", 101, "relapso", CM), fp(CFG), 101, 4, 64, fm,
                       rotulo_dono="relapso")
    g = gravadores[-1]
    novo = PoliticaLobos(CFG, CL_T3, cfg_mundo=CM, cfg_corpo=SO_QUIMICA)
    ganchos = {"mundo": 0, "corpo": 0}
    frutas = 0
    for ch in g.chamadas:
        if ch[0] == "agir":
            _, obs, estado, acao = ch
            rng = random.Random()
            rng.setstate(estado)
            assert novo.agir(corpo_da_obs(obs), rng) is acao
        elif ch[0] == "consequencia":
            _, t, f = ch
            t2 = replace(t, observacao=corpo_da_obs(t.observacao), observacao_seguinte=corpo_da_obs(t.observacao_seguinte))
            novo.observar_consequencia(t2, f, ccons)
            if t.acao not in lb.ACOES_COM_ALVO_MUNDO:
                novo.consequencia_corpo(t.acao, {"acao": t.acao.value, "estimulos": [("pet", t.acao.value)]}, t2.observacao_seguinte)
                ganchos["corpo"] += 1
        elif ch[0] == "alvo":
            novo.escolher_alvo(*ch[1:])
        elif ch[0] == "fruta":
            novo.fruta_comida(ch[1], ch[2])
        else:
            _, acao, oc, depois = ch
            novo.consequencia_mundo(acao, oc, corpo_da_obs(depois))
            novo.consequencia_corpo(acao, {"acao": acao.value, "estimulos": [("pet", acao.value)]}, corpo_da_obs(depois))
            ganchos["mundo"] += 1
            ganchos["corpo"] += 1
            frutas += acao is AcaoPet.COMER and oc["comeu"] is not None and oc["comeu"]["tipo"] in FRUTAS
    ei_hoje, ei = g.c.estado_interno(), novo.estado_interno()
    assert frutas > 0 and ganchos["mundo"] > 0 and ganchos["corpo"] > 0
    assert ganchos["corpo"] == len(ei["motivos"]) > ganchos["mundo"]
    assert ei["pesos"] == ei_hoje["pesos"] and g.c.pesos_mudaram()
    assert ei["aprendizado"]["recompensas"] == ei_hoje["aprendizado"]["recompensas"]
    assert all("sinal_corpo" in m for m in ei["motivos"])
    # no mundo, explorar, comer e brincar sem o consequencia_mundo antes do consequencia_corpo falham alto
    lob = PoliticaLobos(CFG, CL_T3, cfg_mundo=CM, cfg_corpo=SO_QUIMICA)
    with pytest.raises(RuntimeError, match="consequencia_mundo"):
        lob.consequencia_corpo(AcaoPet.COMER, {"acao": "comer", "estimulos": []}, corpo_da_obs(obs_de()))


# ================================================================== o cerebro A com o corpo no MotorCorpo com o mundo fisico (#238 + #239)
MotorMundoCorpo = com_corpo(MotorMundo)
EFEITO_FRUTAS = {"a": -0.1, "b": 0.0, "c": 0.1}


def _fabrica_mundo_corpo(cc_motor: ConfigCorpo, efeito=EFEITO_FRUTAS):
    return lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc_motor, efeito_frutas=efeito)


def _fp_mundo(rotulo: str, ccons: ConfigConsequencia, cc_corpo: ConfigCorpo | None, pols: list | None = None):
    def fp(cfg=None):
        c = PoliticaLobos(cfg or CFG, CL_T3, cfg_mundo=CM, cfg_corpo=cc_corpo)
        if pols is not None:
            pols.append(c)
        return bv.PoliticaDoBraco(c, bv.braco_de(rotulo), ccons)
    return fp


def _vida_mundo_corpo(fp, dono: str, lugar: str, semente: int, cc_motor: ConfigCorpo, dias: int = 3, efeito=EFEITO_FRUTAS):
    fm = _fabrica_mundo_corpo(cc_motor, efeito)
    v = simular_vida_mundo(dono, DonoComLugar(criar_dono(dono), lugar, semente, dono, CM), fp(CFG), semente, dias, 16 * dias, fm,
                           rotulo_dono=dono)
    return v.motor, fm


def _resumo_mundo(m) -> str:
    return json.dumps({"estado": m.estado(), "q": m.corpo.q, "bruto": repr(m._estado), "mundo": m.resumo_mundo_fisico(),
                       "politica": m.politica.estado_interno(), "rng": [m._rng_ambiente.getstate(), m._rng_politica.getstate()],
                       "acoes": m.acoes_recentes(10**9), "log": m.log.para_jsonl()}, sort_keys=True, default=repr)


@pytest.mark.parametrize("cc", [SO_QUIMICA, COM_ORGAOS], ids=["quimica", "orgaos"])
def test_g1_cerebro_com_o_corpo_no_motor_corpo_com_o_mundo(cc):
    """o G1 que faltava (#238 e #239 entraram juntos): o cerebro A com `cfg_corpo` dentro do MotorCorpo com o mundo fisico ligado, P1
    (escalar e canais) e P3, rejogado do log bit a bit, estado interno e registro do mundo incluidos. Com os canais, as frutas iguais (o
    mundo `fisico` da bancada, PMF-7): uma fruta que mexe no humor nao tem rota de canal no mundo e falha alto, como sem o corpo"""
    for rotulo, ccons, efeito in (("P1", CC, EFEITO_FRUTAS), ("P1", CC_CANAIS, None), ("P3", CC, EFEITO_FRUTAS)):
        for dono, lugar in (("atencioso", "perto"), ("relapso", "longe"), ("aleatorio", "comedouro")):
            fp = _fp_mundo(rotulo, ccons, cc)
            m, fm = _vida_mundo_corpo(fp, dono, lugar, 202, cc, efeito=efeito)
            assert m.consequencias == len(m.acoes_recentes(10**9)) > 0
            r = reproduzir_mundo(m.log, fp, CFG, 202, fabrica_motor=fm)
            assert _resumo_mundo(m) == _resumo_mundo(r), (rotulo, ccons.canais_ligados, dono, lugar)


@pytest.mark.parametrize("ccons", [CC, CC_JANELA], ids=["escalar", "janela"])
def test_p1_com_o_corpo_e_o_p1_de_hoje_no_motor_corpo_com_o_mundo(ccons):
    """no MotorCorpo com o mundo fisico, sem drives novos e com w_d = 1: o P1 com a chave do corpo (creditado no consequencia_mundo e no
    consequencia_corpo) vive a mesma vida do P1 de hoje (creditado no consequencia_mundo e na transicao); o estado interno so ganha a
    conta do sinal no motivo e o bloco `corpo`"""
    for dono, lugar in (("atencioso", "perto"), ("relapso", "longe")):
        p_hoje, p_corpo = [], []
        m_hoje, _ = _vida_mundo_corpo(_fp_mundo("P1", ccons, None, p_hoje), dono, lugar, 101, COM_ORGAOS, dias=4)
        m_corpo, _ = _vida_mundo_corpo(_fp_mundo("P1", ccons, COM_ORGAOS, p_corpo), dono, lugar, 101, COM_ORGAOS, dias=4)
        ei_hoje, ei_corpo = p_hoje[-1].estado_interno(), p_corpo[-1].estado_interno()
        assert p_corpo[-1].pesos_mudaram()
        assert _resumo(m_hoje, ei_hoje) == _resumo(m_corpo, _sem_chaves_do_corpo(ei_corpo)), (dono, lugar)
        assert m_hoje.resumo_mundo_fisico() == m_corpo.resumo_mundo_fisico()
        assert all("sinal_corpo" in m for m in ei_corpo["motivos"])
        frutas = [c for c in m_corpo.consumos_mundo if c["como"] == "comer" and c["tipo"] in FRUTAS]
        assert ei_corpo["aprendizado"]["recompensas"].get("consequencia_fruta", 0) == len(frutas)


# ================================================================== o embrulho
def test_embrulho_repassa_os_ganchos_do_corpo_e_nao_muda_a_vida():
    for mundo in ("padrao", "frutas"):
        nu = _vida(mundo, "atencioso", 101, SO_QUIMICA, lambda cfg=None: _cerebro(mundo, SO_QUIMICA))
        emb = _vida(mundo, "atencioso", 101, SO_QUIMICA, lambda cfg=None: PoliticaComMotivo(_cerebro(mundo, SO_QUIMICA)))
        assert _resumo(nu, nu.politica.estado_interno()) == _resumo(emb, emb.politica.estado_interno()), mundo

    class SemGancho:
        """um embrulho que nao repassa o gancho do corpo: com a chave do corpo, o cerebro falha alto (a licao do N5-ACOPLADO)"""

        nome = "lobos"

        def __init__(self, p) -> None:
            self.p = p

        def agir(self, obs, rng):
            return self.p.agir(obs, rng)

        def observar(self, t) -> None:
            self.p.observar(t)

        def receber_acao_dono(self, acao, tick) -> None:
            self.p.receber_acao_dono(acao, tick)

        def estado_interno(self) -> dict:
            return self.p.estado_interno()

    with pytest.raises(RuntimeError, match="ficou sem o gancho"):
        _vida("padrao", "atencioso", 101, SO_QUIMICA, lambda cfg=None: SemGancho(_cerebro("padrao", SO_QUIMICA)))

    class ComCarinho(PoliticaInstinto):
        def __init__(self, *a) -> None:
            super().__init__(*a)
            self.mudancas, self.ganchos = [], []

        def mudanca_no_corpo(self, antes, depois) -> None:
            self.mudancas.append((antes, depois))

        def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
            self.ganchos.append(acao)

    p = ComCarinho(CFG)
    e = PoliticaComMotivo(p)
    antes, depois = obs_de(ticks=40), obs_de(ticks=0)
    e.mudanca_no_corpo(antes, depois)
    e.consequencia_corpo(AcaoPet.OCIOSO, {}, None)
    assert p.mudancas == [(antes, depois)] and p.ganchos == [AcaoPet.OCIOSO]
    assert e._tick_ultimo_cuidado == 40 and e._n_dono == 1          # o carinho e acao do dono no log: o relogio e o indice andam
    assert not hasattr(PoliticaComMotivo(PoliticaInstinto(CFG)), "consequencia_corpo")
    assert not hasattr(PoliticaComMotivo(PoliticaInstinto(CFG)), "mudanca_no_corpo")
