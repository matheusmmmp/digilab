"""V2, a rede de si, etapas 1 e 2 (docs/TAREFA_V2_REDE_DE_SI.md): a rede e o embrulho somente leitura.

- G-INT: o modulo so faz conta em inteiros (AST: nenhuma constante float, nenhuma divisao `/`, nenhum `math`, `random` ou `float`);
- G-PESOS: as duas cabecas somam menos de mil, e o teto falha alto;
- a conta exata de um passo do LMS, da cabeca do corpo e da autoria; com `passo` 0, a previsao e a persistencia para sempre;
- as estimativas contrafactuais (sem o pedido, ao nascer) e o erro exposto (o recente e a surpresa);
- G-OBS: com a rede observando, as vidas da etapa 0 (`tests/gabaritos/rede_de_si_vidas_de_hoje.json`) saem byte a byte iguais;
- G-RECEPTOR: o modulo so importa `config` e `events`; um quimico sem receptor e o que a observacao traz fora do corpo e do contexto nao
  mudam a rede;
- G1-REDE: o estado da rede e refeito bit a bit pelo replay da vida.
So as sementes dos testes.
"""
from __future__ import annotations

import ast
import json
import random
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_rede_de_si as gr  # noqa: E402
from digilab import rede_de_si as rds  # noqa: E402
from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_PADRAO, CONFIG_REDE_DE_SI,  # noqa: E402
                            CONFIG_REDE_DE_SI_LIGADA, ConfigRedeDeSi)
from digilab.corpo import Corpo  # noqa: E402
from digilab.corpo import div_arred as div_corpo  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.mundo import PercepcaoMundo  # noqa: E402
from digilab.policies.lobos import div_arred as div_lobos  # noqa: E402
from digilab.policy import Observacao  # noqa: E402
from digilab.rede_de_si import ACOES, PoliticaComRede, RedeDeSi, contexto, n_pesos  # noqa: E402
from digilab.state import Estado  # noqa: E402

CR = CONFIG_REDE_DE_SI_LIGADA
S = CR.escala
GABARITO = json.loads(gr.ARQUIVO.read_text(encoding="utf-8"))
CASOS = dict(gr.casos())
COM_CORPO = sorted(k for k in CASOS if "|P1+ped|" not in k)
SEM_CORPO = sorted(k for k in CASOS if "|P1+ped|" in k)
NOVOS = dict(tedio=0, solidao=0, estresse=0, dor=0, susto=0)


def pc(fome=S, higiene=S, energia=S, humor=S, saude=S, **novos) -> PercepcaoCorpo:
    return PercepcaoCorpo(fome=fome, higiene=higiene, energia=energia, humor=humor, saude=saude, **{**NOVOS, **novos})


def obs_de(corpo: PercepcaoCorpo, **kw) -> Observacao:
    return Observacao(vetor_estado=(0.8,) * 6 + (0.0, 0.5), ticks_desde_cuidado=0, total_cuidados=0, corpo=corpo, **kw)


def rede(**kw) -> RedeDeSi:
    return RedeDeSi(replace(CR, **kw))


# ================================================================== a config e os registros
def test_config_e_registro():
    assert set(rds.PARAMETROS_REDE_DE_SI) == {f.name for f in fields(ConfigRedeDeSi)}
    assert not CONFIG_REDE_DE_SI.ligada and CR.horizontes == (1, 4, 16)
    with pytest.raises(ValueError, match="desligada"):
        RedeDeSi(CONFIG_REDE_DE_SI)
    with pytest.raises(ValueError, match="desligada"):
        PoliticaComRede(object(), CONFIG_REDE_DE_SI)
    for errado in (dict(passo=-1), dict(horizontes=(4, 1)), dict(faixas_idade=()), dict(fator_erro=S + 1), dict(teto=0)):
        with pytest.raises(ValueError):
            ConfigRedeDeSi(**errado)
    for n, d in [(7, 2), (-7, 2), (5, 3), (-5, 3), (123456, 1024), (-1, 1024)]:
        assert rds.div_arred(n, d) == div_lobos(n, d) == div_corpo(n, d)


# ================================================================== G-INT e G-RECEPTOR (o modulo)
ARVORE = ast.parse((RAIZ / "digilab" / "rede_de_si.py").read_text(encoding="utf-8"))


def test_g_int_so_inteiros():
    for no in ast.walk(ARVORE):
        assert not (isinstance(no, ast.Constant) and isinstance(no.value, float)), f"constante float na linha {no.lineno}"
        assert not isinstance(no, (ast.Div,)), "divisao `/` no modulo da rede"
        if isinstance(no, ast.Name):
            assert no.id not in ("float", "math", "random", "round"), no.id


def test_g_receptor_so_importa_config_e_events():
    importados = set()
    for no in ast.walk(ARVORE):
        if isinstance(no, ast.ImportFrom):
            importados.add(("." * no.level) + (no.module or ""))
        elif isinstance(no, ast.Import):
            importados |= {a.name for a in no.names}
    assert importados == {"__future__", "dataclasses", ".config", ".events"}


# ================================================================== G-PESOS
def test_g_pesos():
    assert n_pesos(10, CR) == 10 * 3 * 22 + 8 * 18 == 804 < CR.maximo_pesos       # o corpo da bola e das frutas
    assert n_pesos(11, CR) == 11 * 3 * 23 + 8 * 19 == 911 < CR.maximo_pesos       # com a curiosidade (o mundo fisico)
    r = rede()
    r.observar(obs_de(pc()), AcaoPet.OCIOSO)
    assert r.n_pesos() == 804
    assert all(type(w) is int for t in r.pesos_corpo.values() for ws in t.values() for w in ws)
    # o corpo inteiro com o banheiro no mundo fisico (13 receptores) passa de mil: falha alto
    big = rede()
    with pytest.raises(ValueError, match="G-PESOS"):
        big.observar(obs_de(pc(curiosidade=0, vontade=0, conforto=0)), AcaoPet.OCIOSO)


# ================================================================== a conta exata
def test_um_passo_do_lms_da_cabeca_do_corpo():
    r = rede(horizontes=(1,))
    a0 = pc(fome=800, tedio=300)
    r.observar(obs_de(a0), AcaoPet.BRINCAR)
    x0 = list(r.pendentes["1"][0][1])
    p0 = r.pendentes["1"][0][2]
    assert p0 == r.leituras(a0)                         # o prior e a persistencia
    a1 = pc(fome=780, tedio=250, dor=10)
    r.observar(obs_de(a1), AcaoPet.OCIOSO)
    l1 = r.leituras(a1)
    for i, rec in enumerate(r.receptores):
        erro = l1[i] - p0[i]
        esperado = [w + (div_corpo(CR.passo * erro * xj, S * S) if xj and erro else 0)
                    for w, xj in zip(r.prior_corpo["1"][rec], x0)]
        assert r.pesos_corpo["1"][rec] == esperado, rec
    assert r.pesos_corpo["1"]["fome"] != r.prior_corpo["1"]["fome"]
    assert r.pesos_corpo["1"]["saude"] == r.prior_corpo["1"]["saude"]          # erro 0: nada muda


def test_um_passo_do_lms_da_autoria():
    r = rede()
    o = obs_de(pc(fome=600))
    reg = r.observar(o, AcaoPet.COMER)
    assert reg["autoria"] == [div_corpo(S, len(ACOES))] * len(ACOES) == [128] * 8      # o prior e uniforme
    y = r._y_autoria(r.leituras(o.corpo), contexto(o, S), 0)
    for a in ACOES:
        erro = (S if a is AcaoPet.COMER else 0) - 128
        esperado = [w + (div_corpo(CR.passo * erro * yj, S * S) if yj else 0) for w, yj in zip(r.prior_autoria[a.value], y)]
        assert r.pesos_autoria[a.value] == esperado


def test_passo_zero_e_a_persistencia_para_sempre():
    rng = random.Random(11)
    r = rede(passo=0)
    for k in range(200):
        o = obs_de(pc(fome=rng.randint(0, S), energia=rng.randint(0, S), tedio=rng.randint(0, S)))
        reg = r.observar(o, rng.choice(ACOES))
        assert all(p == reg["leituras"] for p in reg["corpo"].values())
        assert reg["autoria"] == [128] * 8
    assert r.pesos_corpo == r.prior_corpo and r.pesos_autoria == r.prior_autoria


def test_contrafactuais_sem_o_pedido_e_ao_nascer():
    r = rede()
    com = obs_de(pc(fome=500), pedido_frutas=(-1.0, 0.0, 0.0), frutas_cenario=(1.0, 0.0, 0.0), fruta=0.5)
    sem = replace(com, pedido_frutas=(0.0, 0.0, 0.0))
    for k in range(300):                                 # o pet deixa de comer com o pedido e come sem ele
        o = com if k % 2 else sem
        r.observar(o, AcaoPet.OCIOSO if k % 2 else AcaoPet.COMER)
    reg = r.observar(com, AcaoPet.OCIOSO)
    ls, ctx = reg["leituras"], reg["contexto"]
    assert ctx == [0, S, S]
    i = ACOES.index(AcaoPet.COMER)
    assert reg["autoria_sem_pedido"][i] > reg["autoria"][i]       # "sem o pedido, eu teria comido?"
    # a contrafactual e a mesma conta com o pedido zerado (antes do aprendizado desta decisao)
    assert reg["faixa"] == r.faixa(reg["k"]) == 2 and reg["autoria_ao_nascer"] != reg["autoria"]
    r2 = rede()
    reg0 = r2.observar(com, AcaoPet.OCIOSO)
    assert reg0["faixa"] == 0 and reg0["autoria_ao_nascer"] == reg0["autoria"]


def test_o_erro_exposto():
    r = rede(horizontes=(1,), passo=0)
    seq = [800, 700, 700, 400]
    regs = [r.observar(obs_de(pc(fome=f)), AcaoPet.OCIOSO) for f in seq]
    rec = 0
    for k in range(1, len(seq)):
        e = abs(seq[k] - seq[k - 1])                  # passo 0: a previsao e a persistencia
        assert regs[k]["surpresa"]["1"][0] == e - rec
        rec += div_corpo((e - rec) * CR.fator_erro, S)
    assert r.erro_recente["1"]["fome"] == rec and regs[0]["surpresa"] == {}


def test_contexto_do_mundo_fisico_e_das_frutas():
    p = PercepcaoMundo(200, 240, 0, ((1, "a", 5, 0, 5), (0, "bola", 10, 0, 10)), 0, 0, None)
    assert contexto(obs_de(pc(), mundo=p), S) == [S, S, 0]
    p = PercepcaoMundo(200, 240, 0, ((1, "a_podre", 5, 0, 5),), 0, 0, None)
    assert contexto(obs_de(pc(), mundo=p), S) == [0, 0, 0]                       # a podre nao conta
    assert contexto(obs_de(pc(), bola=1.0), S) == [S, 0, 0]
    assert contexto(obs_de(pc(), frutas_cenario=(0.0, 1.0, 0.0), pedido_frutas=(0.0, -1.0, 0.0)), S) == [0, S, S]


def test_falhas_altas():
    r = rede()
    with pytest.raises(RuntimeError, match="sem o corpo"):
        r.observar(Observacao((0.8,) * 6 + (0.0, 0.5), 0, 0), AcaoPet.OCIOSO)
    r.observar(obs_de(pc()), AcaoPet.OCIOSO)
    with pytest.raises(ValueError, match="layout"):
        r.observar(obs_de(pc(curiosidade=0)), AcaoPet.OCIOSO)
    with pytest.raises(ValueError, match="fora de inteiros"):
        r.observar(obs_de(pc(fome=S + 1)), AcaoPet.OCIOSO)
    with pytest.raises(TypeError):
        r.observar(obs_de(pc()), "ocioso")


# ================================================================== G-RECEPTOR (a vida)
def test_quimico_sem_receptor_e_o_resto_da_observacao_nao_mudam_a_rede():
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, CONFIG_CORPO_DRIVES)
    antes = PercepcaoCorpo(**c.receptores())
    c.q["alimento"], c.q["vida"] = 300000, 1000                    # quimicos sem receptor
    depois = PercepcaoCorpo(**c.receptores())
    assert antes == depois
    rng = random.Random(33)
    a, b = rede(), rede()
    for _ in range(100):
        corpo = pc(fome=rng.randint(0, S), tedio=rng.randint(0, S))
        acao = rng.choice(ACOES)
        a.observar(obs_de(corpo), acao)
        # o que a rede nao le: o Estado (vetor), o relogio do cuidado, a informacao do dono
        b.observar(Observacao(vetor_estado=tuple(rng.random() for _ in range(8)), ticks_desde_cuidado=rng.randint(0, 900),
                              total_cuidados=rng.randint(0, 50), corpo=corpo, info_frutas=(1.0, -1.0, 0.0)), acao)
    assert json.dumps(a.estado(), sort_keys=True) == json.dumps(b.estado(), sort_keys=True)


# ================================================================== G-OBS e G1-REDE (as vidas)
class BancadaComRede(bv.Bancada):
    """a bancada com a politica de cada vida embrulhada pela rede (so para os testes; a chave da bancada e da etapa 3, do D)"""

    def politica(self, espec, cfg=None):
        p = PoliticaComRede(super().politica(espec, cfg), CR)
        CRIADAS.append(p)
        return p


CRIADAS: list[PoliticaComRede] = []
BANCADAS = gr.bancadas(BancadaComRede)


@pytest.mark.parametrize("chave", COM_CORPO)
def test_g_obs_a_vida_com_a_rede_e_a_de_hoje(chave):
    montagem, espec = CASOS[chave]
    CRIADAS.clear()
    assert gr.vida_de_hoje(BANCADAS[montagem], espec) == GABARITO[chave]
    p = CRIADAS[-1]
    assert p.rede.k > 0 and p.rede.n_pesos() == 804                   # a rede observou a vida inteira


@pytest.mark.parametrize("chave", SEM_CORPO)
def test_sem_corpo_a_rede_falha_alto(chave):
    montagem, espec = CASOS[chave]
    with pytest.raises(RuntimeError, match="sem o corpo"):
        BANCADAS[montagem].vida(espec)


@pytest.mark.parametrize("chave", [c for c in COM_CORPO if c.endswith("|101") and "atencioso" in c])
def test_g1_rede_o_replay_refaz_a_rede(chave):
    montagem, espec = CASOS[chave]
    b = BANCADAS[montagem]
    CRIADAS.clear()
    v = b.vida(espec)
    original = CRIADAS[-1]
    CRIADAS.clear()
    b.rejogar(v.motor.log, espec)
    refeita = CRIADAS[-1]
    assert json.dumps(refeita.rede.estado(), sort_keys=True) == json.dumps(original.rede.estado(), sort_keys=True)
    assert original.rede.pesos_corpo != original.rede.prior_corpo        # aprendeu
    assert len(original.rede.registros) == original.rede.k


def test_o_embrulho_repassa_o_que_o_cerebro_tem():
    from digilab.policies.lobos import PoliticaLobos
    from digilab.config import CONFIG_LOBOS, CONFIG_MUNDO_LIGADA
    cerebro = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CONFIG_MUNDO_LIGADA, cfg_corpo=CONFIG_CORPO_DRIVES)
    p = PoliticaComRede(cerebro, CR)
    for nome in ("observar", "receber_acao_dono", "escolher_alvo", "escolher_fruta", "consequencia_mundo", "consequencia_corpo",
                 "mudanca_no_corpo", "estado_interno", "ultima_regra", "gancho_que_nao_existe"):
        assert hasattr(p, nome) == hasattr(cerebro, nome)
    assert not hasattr(p, "gancho_que_nao_existe")
    assert p.estado_interno() == cerebro.estado_interno()
