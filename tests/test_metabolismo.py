"""O metabolismo energetico no corpo, etapa 1 (docs/TAREFA_V2_METABOLISMO.md, secoes 3 e 6; ME-1 a ME-7 pela recomendacao, Matheus,
2026-10-11): o combustivel e a reserva por baixo do cansaco, sem receptor.

- G2: com a sub-chave desligada, as vidas da etapa 0 (`tests/gabaritos/metabolismo_vidas_de_hoje.json`) byte a byte; os gabaritos do
  corpo de sempre ficam nos testes deles;
- G-GRAFO: as checagens passam com o metabolismo em toda combinacao de sub-chaves, e as tabelas feitas para falhar falham alto;
- G-MEC-M: a conta exata de cada peca;
- G-HOJE-M: com o combustivel acima de C/4, todo quimico de antes e o de sem o metabolismo, tick a tick, nos tres mundos e no fisico; com
  a falta, o cansaco passa a diferir no tick dela;
- G-CONS-M: a contabilidade do combustivel e da reserva fecha a cada tick;
- G-RECEPTOR-M: o cerebro nao le o combustivel nem a reserva, o numero de pesos nao muda e nenhum emissor novo sobe o cansaco fora da
  falta;
- G1: o replay refaz o combustivel, a reserva e as contas.
So as sementes dos testes.
"""
from __future__ import annotations

import ast
import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_metabolismo as gmet  # noqa: E402
from digilab import corpo as corpo_mod  # noqa: E402
from digilab.ambiente import DonoComBola, MotorAmbiente, PoliticaInstintoBola  # noqa: E402
from digilab.config import (CONFIG_BANHEIRO_LIGADA, CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_CORPO_BANHEIRO,  # noqa: E402
                            CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS, CONFIG_MUNDO_LIGADA,
                            CONFIG_PADRAO, ConfigCorpo)
from digilab.corpo import CONTAS_METABOLISMO, PARAMETROS_CORPO, Corpo, grafo_do_corpo, quimicos_de, taxas_de  # noqa: E402
from digilab.corpo_grafo import Emissor, Grafo, GrafoInvalido, Leitura, Reacao, checar  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas, simular_vida_frutas  # noqa: E402
from digilab.gestos import CanalMundoComGestos, DonoComGestos, simular_vida_gestos  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.treino import MotorComFeedback, reproduzir_com_feedback  # noqa: E402

CFG = CONFIG_PADRAO
CM = CONFIG_MUNDO_LIGADA
MET = CONFIG_CORPO_METABOLISMO                     # a etapa 6 com o metabolismo
MIN = ConfigCorpo(ligada=True, digestao=True, metabolismo=True)
C = MIN.escala
F, M, A = MIN.falta_limiar, MIN.mobilizar_limiar, MIN.armazenar_limiar
DIAS, ORC = 3, 48
CL_T3 = bv.cfg_lobos_do_ponto("T3")
VELHOS = corpo_mod.QUIMICOS + ("alimento", "vida") + corpo_mod.NOVOS + corpo_mod.GESTOS


def _corpo(cc: ConfigCorpo, com_mundo: bool = False, **q) -> Corpo:
    c = Corpo.de_estado(Estado(), CFG, cc, com_mundo=com_mundo)
    for nome, v in q.items():
        c.q[nome] = v
    return c


def _passo(c: Corpo, dormindo: bool = False) -> None:
    c.passo(Estado(tick=600, dormindo=dormindo))


def _fecha(c: Corpo, cc: ConfigCorpo) -> None:
    """G-CONS-M: o combustivel e a reserva sao o que entrou menos o que saiu, desde o nascimento"""
    k = c.contas_metabolismo
    assert c.q["combustivel"] == (cc.combustivel_inicial + k["convertido"] - k["descartado_teto"] + k["mobilizado"] - k["gasto_basal"]
                                  - k["gasto_atividade"] - k["armazenado"])
    assert c.q["reserva"] == cc.reserva_inicial + k["armazenado"] - k["mobilizado"]
    assert k["convertido"] * cc.conversao_den + c.resto_combustivel == c.digerido_total * cc.conversao_num
    assert 0 <= c.resto_combustivel < cc.conversao_den and all(v >= 0 for v in k.values())


# ================================================================== a chave e o registro
def test_a_subchave_exige_a_digestao_e_os_numeros_conferidos():
    assert ConfigCorpo().metabolismo is False and MET.metabolismo and MET.digestao
    with pytest.raises(ValueError, match="metabolismo exige ConfigCorpo.digestao"):
        ConfigCorpo(ligada=True, metabolismo=True)
    with pytest.raises(TypeError):
        ConfigCorpo(ligada=True, digestao=True, metabolismo=1)
    with pytest.raises(ValueError, match="falta_limiar < mobilizar_limiar"):
        replace(MIN, falta_limiar=M)
    with pytest.raises(ValueError, match="inteiro positivo"):
        replace(MIN, gasto_basal_dormindo=0)
    with pytest.raises(ValueError, match=r"\[0, C\]"):
        replace(MIN, reserva_inicial=C + 1)
    assert set(PARAMETROS_CORPO) == {f.name for f in fields(ConfigCorpo)}
    assert (MIN.combustivel_inicial, MIN.reserva_inicial, F, M, A) == (C // 2, C // 4, C // 4, C // 2, 3 * C // 4)
    assert MIN.gasto_basal_acordado == taxas_de(CFG, MIN).fome_por_tick == 375 and MIN.gasto_basal_dormindo == 187
    assert MIN.falta_cansaco == taxas_de(CFG, MIN).cansaco_acordado == 500


def test_os_quimicos_novos_sem_receptor_e_o_nascimento():
    for cc, mundo in ((MIN, False), (MET, False), (MET, True), (replace(CONFIG_CORPO_BANHEIRO, metabolismo=True), True)):
        c = Corpo.de_estado(Estado(tick=5000), CFG, cc, com_mundo=mundo)
        assert c.quimicos[-2:] == ("combustivel", "reserva")
        assert c.quimicos[:-2] == quimicos_de(replace(cc, metabolismo=False), mundo)
        assert (c.q["combustivel"], c.q["reserva"]) == (C // 2, C // 4)
        assert c.grafo.quimico("combustivel").receptor is None and c.grafo.quimico("reserva").receptor is None
        assert set(c.receptores()) == set(Corpo.de_estado(Estado(), CFG, replace(cc, metabolismo=False), com_mundo=mundo).receptores())
        assert c.para_dict()["metabolismo"] == {"resto_combustivel": 0, "contas": {k: 0 for k in CONTAS_METABOLISMO}}
    assert "metabolismo" not in Corpo.de_estado(Estado(), CFG, CONFIG_CORPO_DRIVES).para_dict()


# ================================================================== G-GRAFO
COMBINACOES = {
    "minimo": MIN, "vida": replace(MIN, vida=True), "novos": replace(MIN, vida=True, drives_novos=True), "etapa6": MET,
    "sem_medo": replace(MET, medo_da_mao=0), "banheiro": replace(CONFIG_CORPO_BANHEIRO, metabolismo=True),
    "fracao": replace(MET, conversao_num=2, conversao_den=3),
}


@pytest.mark.parametrize("nome", list(COMBINACOES))
@pytest.mark.parametrize("com_mundo", [False, True])
def test_g_grafo_as_checagens_passam_em_toda_combinacao(nome, com_mundo):
    cc = COMBINACOES[nome]
    g = grafo_do_corpo(CFG, cc, taxas_de(CFG, cc), com_mundo)
    rel = checar(g)
    sem = checar(grafo_do_corpo(CFG, replace(cc, metabolismo=False), taxas_de(CFG, replace(cc, metabolismo=False)), com_mundo))
    assert rel["lacos"] == sem["lacos"]                   # as retroalimentacoes do metabolismo sao negativas: nenhum laco novo
    assert rel["so_pelo_teto"] == sem["so_pelo_teto"]
    assert set(rel["sumidouros"]["combustivel"]) == {"reacao:armazenamento", "emissor:gasto_basal_acordado", "emissor:gasto_basal_dormindo",
                                                     "emissor:dono:brincar", "emissor:pet:brincar", "emissor:pet:explorar",
                                                     "emissor:andar", "teto"}
    assert rel["fontes"]["combustivel"] == ["reacao:digestao", "reacao:mobilizacao"]
    assert rel["sumidouros"]["reserva"] == ["reacao:mobilizacao", "teto"] and rel["fontes"]["reserva"] == ["reacao:armazenamento"]
    d = next(r for r in g.reacoes if r.nome == "digestao")
    assert ("combustivel", cc.conversao_num, cc.conversao_den) in d.fracoes and "combustivel" in d.produz
    falta = g.emissor("falta_combustivel")
    assert (falta.gatilho, falta.fase, falta.limiar, falta.efeitos) == ("abaixo", 2, F, (("cansaco", 500),))


def _sem(g: Grafo, emissores=(), reacoes=(), tira_combustivel=False, manter=()) -> Grafo:
    em = []
    for e in g.emissores:
        if e.nome in emissores:
            continue
        if tira_combustivel and e.nome not in manter and any(q == "combustivel" for q, _ in e.efeitos):
            ef = tuple(x for x in e.efeitos if x[0] != "combustivel")
            if not ef:
                continue
            e = replace(e, efeitos=ef)
        em.append(e)
    return Grafo(g.quimicos, tuple(r for r in g.reacoes if r.nome not in reacoes), tuple(em))


def test_g_grafo_as_tabelas_feitas_para_falhar_falham_alto():
    g = grafo_do_corpo(CFG, MET, taxas_de(CFG, MET), True)
    checar(g)
    # o combustivel sem gasto: so sai pela transferencia e pelo teto
    with pytest.raises(GrafoInvalido, match="so saem pelo teto"):
        checar(_sem(g, ("gasto_basal_acordado", "gasto_basal_dormindo"), tira_combustivel=True))
    # a reserva sem armazenamento: a mobilizacao a consome e nada a repoe (o teto nao desculpa)
    with pytest.raises(GrafoInvalido, match="transferencia consome sem fonte"):
        checar(_sem(g, reacoes=("armazenamento",)))
    # so o basal ja basta como gasto de verdade
    checar(_sem(g, tira_combustivel=True, manter=("gasto_basal_acordado", "gasto_basal_dormindo")))


def test_g_grafo_a_forma_das_pecas_novas():
    q = (corpo_mod.Quimico("a", 10), corpo_mod.Quimico("b", 10))
    gasto = Emissor("gasta_a", "tick", 1, (("a", -1),))
    sobe = Emissor("sobe_a", "tick", 1, (("a", 1),))
    ok = Reacao("t", ("a",), ("b",), 5, le="a", lado="acima", limiar=3)
    volta = Reacao("v", ("b",), ("a",), 5, le="a", lado="abaixo", limiar=2)
    checar(Grafo(q, (ok, volta), (gasto, sobe)))
    for ruim in (replace(ok, consome=("a", "b")), replace(ok, lado="dentro"), replace(ok, le=None), replace(ok, produz=("a",)),
                 replace(ok, fracoes=(("b", 1, 2),)), replace(ok, limiar=-1), Reacao("x", ("a",), ("b",), 5, limiar=3)):
        with pytest.raises(GrafoInvalido):
            checar(Grafo(q, (ruim, volta), (gasto, sobe)))
    with pytest.raises(GrafoInvalido, match="fora da tabela"):
        checar(Grafo(q, (replace(ok, le="z"), volta), (gasto, sobe)))
    with pytest.raises(GrafoInvalido, match="fracao"):
        checar(Grafo(q, (Reacao("d", ("a",), ("b",), 5, (("a", 1, 2),)),), (gasto, sobe)))
    abaixo = Emissor("falta", "abaixo", 2, (("b", 1),), (Leitura("a", 1, 1, -1),), 3)
    checar(Grafo(q, (), (gasto, sobe, abaixo, Emissor("gasta_b", "tick", 1, (("b", -1),)))))
    for ruim in (replace(abaixo, le=(Leitura("a", 1, 1),)), replace(abaixo, fase=1), replace(abaixo, divisor=2)):
        with pytest.raises(GrafoInvalido, match="abaixo"):
            checar(Grafo(q, (), (gasto, sobe, ruim, Emissor("gasta_b", "tick", 1, (("b", -1),)))))
    # a transferencia "acima" que alimenta um quimico que volta ao lido por um emissor fecha um laco de ganho 1: falha alto
    laco = Emissor("b_faz_a", "limiar", 2, (("a", 1),), (Leitura("b", 1, 2),), 0, 2)
    checar(Grafo(q, (ok,), (gasto, sobe, laco, Emissor("gasta_b", "tick", 1, (("b", -1),)))))      # ganho 1 x 1/2: passa
    with pytest.raises(GrafoInvalido, match="ganho >= 1"):
        checar(Grafo(q, (ok,), (gasto, sobe, replace(laco, le=(Leitura("b", 1, 1),)), Emissor("gasta_b", "tick", 1, (("b", -1),)))))


# ================================================================== G-MEC-M
def test_g_mec_a_conversao_com_o_resto():
    cc = replace(MIN, conversao_num=2, conversao_den=3)
    c = _corpo(cc, fome=1000, combustivel=300000)
    c.resto_combustivel = 2
    c.acao_dono(AcaoUsuario.ALIMENTAR)                   # digere 1000 (a fome): 2 + 2000 = 2002 -> 667 e resto 1
    assert c.digerido_tick == 1000 and c.q["combustivel"] == 300000 + 667 and c.resto_combustivel == 1
    assert c.contas_metabolismo["convertido"] == 667
    # 1/1, a recomendacao: o combustivel sobe o mesmo que a fome desce
    c = _corpo(MIN, fome=90000, combustivel=300000)
    c.acao_pet(AcaoPet.COMER)
    assert c.q["combustivel"] == 300000 + 22500 and c.q["fome"] == 90000 - 22500
    # o teto: o que passa de C e descartado e contado
    c = _corpo(MIN, fome=C, combustivel=C - 100)
    c.acao_dono(AcaoUsuario.ALIMENTAR)
    assert c.q["combustivel"] == C and c.contas_metabolismo["descartado_teto"] == 202500 - 100


def test_g_mec_o_gasto_basal_acordado_e_dormindo():
    for dormindo, gasto in ((False, 375), (True, 187)):
        c = _corpo(MIN, combustivel=300000, reserva=1000)
        _passo(c, dormindo)
        assert (c.q["combustivel"], c.q["reserva"]) == (300000 - gasto, 1000)
        assert c.contas_metabolismo["gasto_basal"] == gasto
    c = _corpo(MIN, combustivel=100, reserva=0)                  # no fundo: so sai o que havia
    _passo(c)
    assert c.q["combustivel"] == 0 and c.contas_metabolismo["gasto_basal"] == 100


@pytest.mark.parametrize("op", ["pet_brincar", "pet_explorar", "dono_brincar", "andar"])
def test_g_mec_cada_atividade_tira_do_combustivel_o_que_soma_ao_cansaco(op):
    c, sem = _corpo(MIN, combustivel=300000, cansaco=1000), _corpo(replace(MIN, metabolismo=False), cansaco=1000)
    for x in (c, sem):
        {"pet_brincar": lambda x: x.acao_pet(AcaoPet.BRINCAR), "pet_explorar": lambda x: x.acao_pet(AcaoPet.EXPLORAR),
         "dono_brincar": lambda x: x.acao_dono(AcaoUsuario.BRINCAR),
         "andar": lambda x: x.estimulo_andar(37, CM.custo_energia_por_subunidade)}[op](x)
    subiu = c.q["cansaco"] - 1000
    assert subiu > 0 and 300000 - c.q["combustivel"] == subiu == c.contas_metabolismo["gasto_atividade"]
    assert {k: v for k, v in c.q.items() if k not in ("combustivel", "reserva")} == sem.q        # o cansaco de hoje nao muda
    c = _corpo(MIN, combustivel=10)
    c.acao_pet(AcaoPet.BRINCAR)
    assert c.q["combustivel"] == 0 and c.contas_metabolismo["gasto_atividade"] == 10


def test_g_mec_o_armazenamento_e_a_mobilizacao_nos_limiares():
    casos = [  # (combustivel, reserva) antes do tick acordado -> (combustivel, reserva) depois; o basal (375) sai antes
        ((A + 1000, 0), (A + 625 - 375, 375)),        # acima: ate a taxa
        ((A + 500, 0), (A, 125)),                     # acima: so ate o limiar
        ((A + 375, 0), (A, 0)),                       # o basal o leva ao limiar: nada vai
        ((A + 1000, C - 50), (A + 625 - 50, C)),      # a reserva cheia: so o que cabe
        ((M + 375, 1000), (M, 1000)),                 # entre os limiares: nada anda
        ((M + 100, 1000), (M, 725)),                  # abaixo: ate o limiar
        ((M - 100, 1000), (M - 100, 625)),            # abaixo: ate a taxa
        ((M - 100, 50), (M - 425, 0)),                # abaixo: so o que a reserva tem
    ]
    for (comb, res), esperado in casos:
        c = _corpo(MIN, combustivel=comb, reserva=res)
        _passo(c)
        assert (c.q["combustivel"], c.q["reserva"]) == esperado, (comb, res)
    # dormindo, o mesmo pelo gasto de 187
    c = _corpo(MIN, combustivel=M, reserva=1000)
    _passo(c, True)
    assert (c.q["combustivel"], c.q["reserva"]) == (M, 813)


def test_g_mec_a_falta_sobe_o_cansaco_so_abaixo_de_c4():
    base = 1000
    # o basal (375) sai na fase 1; abaixo de C/2 a reserva devolve ate 375 antes da fase 2, em que a falta le o combustivel
    for comb, res, falta in ((F + 375, 0, False), (F + 374, 0, True), (F + 374, 1, False), (F, 375, False), (F - 1, 1000, True),
                             (F - 1000, 375, True), (0, 0, True)):
        c = _corpo(MIN, combustivel=comb, reserva=res, cansaco=base)
        sem = _corpo(replace(MIN, metabolismo=False), cansaco=base)
        _passo(c)
        _passo(sem)
        assert c.q["cansaco"] - sem.q["cansaco"] == (500 if falta else 0), (comb, res)
        assert {k: v for k, v in c.q.items() if k not in ("cansaco", "combustivel", "reserva")} == \
            {k: v for k, v in sem.q.items() if k != "cansaco"}
    c = _corpo(MIN, combustivel=0, reserva=0, cansaco=C - 100)       # o teto do cansaco
    _passo(c)
    assert c.q["cansaco"] == C


# ================================================================== G-HOJE-M e G-CONS-M, nas vidas
@pytest.fixture()
def historia(monkeypatch):
    """guarda q, o resto e as contas depois de cada tick de cada corpo"""
    original = Corpo.passo

    def passo(self, antes, necessidades=0):
        original(self, antes, necessidades)
        self.__dict__.setdefault("_hist", []).append((dict(self.q), self.resto_combustivel,
                                                      dict(self.contas_metabolismo or {}), self.digerido_total))

    monkeypatch.setattr(Corpo, "passo", passo)


def _politica(mundo: str, cerebro: str, cc: ConfigCorpo):
    if cerebro == "instinto":
        return {"padrao": lambda: PoliticaInstinto(CFG), "bola": lambda: PoliticaInstintoBola(CFG, CONFIG_BOLA_LIGADA),
                "frutas": lambda: PoliticaInstintoFrutas(CFG, None, CONFIG_FRUTAS_LIGADA),
                "fisico": lambda: PoliticaInstintoMundo(CFG)}[mundo]()
    kw = {"padrao": {}, "bola": {"cfg_bola": CONFIG_BOLA_LIGADA}, "frutas": {"cfg_frutas": CONFIG_FRUTAS_LIGADA},
          "fisico": {"cfg_mundo": CM}}[mundo]
    return bv.PoliticaDoBraco(PoliticaLobos(CFG, CL_T3, cfg_corpo=cc, **kw), bv.braco_de(cerebro), CONFIG_CONSEQUENCIA)


def _fabrica(mundo: str, cc: ConfigCorpo):
    return {"padrao": lambda p, cfg, s: com_corpo(MotorComFeedback)(p, cfg, s, cfg_corpo=cc),
            "bola": lambda p, cfg, s: com_corpo(MotorAmbiente)(p, cfg, s, obediencia_desligada=True, cfg_bola=CONFIG_BOLA_LIGADA,
                                                               cfg_corpo=cc),
            "frutas": lambda p, cfg, s: com_corpo(MotorFrutas)(p, cfg, s, obediencia_desligada=True, cfg_frutas=CONFIG_FRUTAS_LIGADA,
                                                               cfg_corpo=cc),
            "fisico": lambda p, cfg, s: com_corpo(MotorMundo)(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc)}[mundo]


def _vida(mundo: str, cerebro: str, cc: ConfigCorpo, dono: str = "atencioso", s: int = 101, dias: int = DIAS):
    p, fm = _politica(mundo, cerebro, cc), _fabrica(mundo, cc)
    DIAS, ORC = dias, 16 * dias  # noqa: N806
    if mundo == "padrao":
        return simular_vida_gestos(dono, DonoComGestos(criar_dono(dono), "tapa"), p, s, DIAS, ORC, fabrica_motor=fm, rotulo_dono=dono)
    if mundo == "bola":
        return simular_vida_gestos(dono, DonoComGestos(DonoComBola(dono, CONFIG_BOLA_LIGADA), "tapa"), p, s, DIAS, ORC,
                                   fabrica_motor=fm, rotulo_dono=dono)
    if mundo == "frutas":
        return simular_vida_frutas(dono, DonoComGestos(criar_dono(dono), "tapa"), p, s, DIAS, ORC, fm, OfertasFrutas(CONFIG_FRUTAS_LIGADA),
                                   rotulo_dono=dono)
    d = DonoComGestos(DonoComLugar(criar_dono(dono), "perto", s, dono, CM), "tapa")
    return simular_vida_mundo(dono, d, p, s, DIAS, ORC, fm, rotulo_dono=dono, canal_classe=CanalMundoComGestos)


def _velhos(q: dict) -> dict:
    return {k: v for k, v in q.items() if k not in ("combustivel", "reserva")}


MUNDOS = ("padrao", "bola", "frutas", "fisico")
# o combustivel acima de C/4: o corpo nasce cheio, em vidas de 2 dias (com os numeros PROPOSTOS, as atividades gastam ~240 por tick e
# ate o corpo cheio fica em falta no dia 3; o gate confere a condicao em cada vida)
CHEIO = replace(MET, combustivel_inicial=C, reserva_inicial=C)
DIAS_H = 2
VIDAS_H = (("aleatorio", 202), ("relapso", 303))


@pytest.mark.parametrize("mundo", MUNDOS)
@pytest.mark.parametrize("cerebro", ["instinto", "P1"])
def test_g_hoje_m_acima_de_c4_os_quimicos_de_antes_sao_os_de_sem_metabolismo(historia, mundo, cerebro):
    for dono, s in VIDAS_H:
        com, sem = _vida(mundo, cerebro, CHEIO, dono, s, DIAS_H), _vida(mundo, cerebro, CONFIG_CORPO_DRIVES, dono, s, DIAS_H).motor
        hc, hs = com.motor.corpo._hist, sem.corpo._hist
        assert len(hc) == len(hs) == DIAS_H * 1440
        assert min(q["combustivel"] for q, *_ in hc) >= F                  # a condicao do gate: a falta nunca disparou
        assert [_velhos(q) for q, *_ in hc] == [q for q, *_ in hs]           # tick a tick
        assert com.motor.log.para_jsonl() == sem.log.para_jsonl() and com.motor.acoes_recentes(10**9) == sem.acoes_recentes(10**9)
        k = com.motor.corpo.contas_metabolismo
        assert k["gasto_basal"] > 0 and k["gasto_atividade"] > 0 and k["convertido"] > 0 and k["mobilizado"] > 0
        for q, resto, contas, digerido in hc:                               # G-CONS-M a cada tick
            assert q["combustivel"] == (C + contas["convertido"] - contas["descartado_teto"] + contas["mobilizado"]
                                        - contas["gasto_basal"] - contas["gasto_atividade"] - contas["armazenado"])
            assert q["reserva"] == C + contas["armazenado"] - contas["mobilizado"]
            assert contas["convertido"] * CHEIO.conversao_den + resto == digerido * CHEIO.conversao_num
        _fecha(com.motor.corpo, CHEIO)


@pytest.mark.parametrize("mundo", MUNDOS)
def test_g_hoje_m_com_a_falta_o_cansaco_difere_a_partir_do_tick_dela(historia, mundo):
    """com os numeros PROPOSTOS a falta dispara nas vidas curtas: ate o tick dela, tudo igual; no tick dela, so o cansaco, +500"""
    com, sem = _vida(mundo, "instinto", MET).motor, _vida(mundo, "instinto", CONFIG_CORPO_DRIVES).motor
    hc, hs = com.corpo._hist, sem.corpo._hist
    t = next(i for i, (q, *_) in enumerate(hc) if q["combustivel"] < F)
    assert [_velhos(q) for q, *_ in hc[:t]] == [q for q, *_ in hs[:t]]
    antes, depois = _velhos(hc[t][0]), hs[t][0]
    assert antes["cansaco"] == min(C, depois["cansaco"] + MET.falta_cansaco) != depois["cansaco"]
    assert {k: v for k, v in antes.items() if k != "cansaco"} == {k: v for k, v in depois.items() if k != "cansaco"}
    for q, resto, contas, digerido in hc:
        assert q["reserva"] == MET.reserva_inicial + contas["armazenado"] - contas["mobilizado"]
    _fecha(com.corpo, MET)


def test_g_cons_m_numa_sequencia_longa_com_a_conversao_fracionada():
    """o gabarito da paridade guarda uma sequencia longa; aqui, a contabilidade a cada operacao, com a conversao 2/3 e o teto mordendo"""
    import random
    rng = random.Random(11)
    cc = replace(MET, conversao_num=2, conversao_den=3, combustivel_inicial=C - 5000)
    c = Corpo.de_estado(Estado(), CFG, cc, com_mundo=True)
    for tick in range(6000):
        r = rng.random()
        if r < 0.75:
            c.passo(Estado(tick=tick, dormindo=rng.random() < 0.3, sujeira=rng.randrange(3)))
        elif r < 0.85:
            c.acao_dono(AcaoUsuario.ALIMENTAR)
        elif r < 0.9:
            c.acao_pet(rng.choice((AcaoPet.BRINCAR, AcaoPet.EXPLORAR, AcaoPet.COMER)))
        elif r < 0.95:
            c.estimulo_andar(rng.randrange(200), CM.custo_energia_por_subunidade)
        else:
            c.acao_dono(AcaoUsuario.BRINCAR)
        _fecha(c, cc)
    k = c.contas_metabolismo
    assert all(k[x] > 0 for x in CONTAS_METABOLISMO), k


# ================================================================== G-RECEPTOR-M
def test_g_receptor_m_o_cerebro_nao_le_o_combustivel_nem_a_reserva():
    assert not {"combustivel", "reserva"} & {f.name for f in fields(PercepcaoCorpo)}
    for arq in ("policies/lobos.py", "policies/cerebro_b.py", "policies/cerebro_c.py", "rede_de_si.py", "instinto_mundo.py",
                "instinto_banheiro.py", "motivo.py", "motor_corpo.py", "mundo.py"):
        arvore = ast.parse((RAIZ / "digilab" / arq).read_text(encoding="utf-8"))
        nomes = {n.value for n in ast.walk(arvore) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        nomes |= {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
        nomes |= {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)}
        assert not nomes & {"combustivel", "reserva", "contas_metabolismo", "resto_combustivel"}, arq
    # o numero de pesos e o de sem o metabolismo (998 com o banheiro, no mundo fisico)
    cb = replace(CONFIG_CORPO_BANHEIRO, metabolismo=True)
    assert PoliticaLobos(CFG, CONFIG_LOBOS, cfg_mundo=CM, cfg_corpo=cb, cfg_banheiro=CONFIG_BANHEIRO_LIGADA).n_pesos() == 998
    for kw in ({"cfg_frutas": CONFIG_FRUTAS_LIGADA}, {"cfg_mundo": CM}, {}):
        assert (PoliticaLobos(CFG, CONFIG_LOBOS, cfg_corpo=MET, **kw).n_pesos()
                == PoliticaLobos(CFG, CONFIG_LOBOS, cfg_corpo=CONFIG_CORPO_DRIVES, **kw).n_pesos())


def test_g_receptor_m_o_cerebro_recebe_a_mesma_percepcao(historia):
    """espiao: as PercepcaoCorpo que o cerebro recebe nas vidas com e sem o metabolismo (acima de C/4) sao as mesmas, decisao a
    decisao, e nenhuma traz o combustivel"""
    vistos = {}
    for chave, cc in (("com", CHEIO), ("sem", CONFIG_CORPO_DRIVES)):
        p = PoliticaInstintoMundo(CFG)
        lista = vistos.setdefault(chave, [])
        original = p.agir

        def agir(obs, rng, _o=original, _l=lista):
            _l.append(obs.corpo)
            return _o(obs, rng)

        p.agir = agir
        d = DonoComGestos(DonoComLugar(criar_dono("aleatorio"), "perto", 202, "aleatorio", CM), "tapa")
        simular_vida_mundo("aleatorio", d, p, 202, DIAS_H, 16 * DIAS_H, _fabrica("fisico", cc), rotulo_dono="aleatorio",
                           canal_classe=CanalMundoComGestos)
    assert vistos["com"] == vistos["sem"] and len(vistos["com"]) == DIAS_H * 1440 // 15
    assert all(isinstance(x, PercepcaoCorpo) for x in vistos["com"])


def test_g_receptor_m_nenhum_emissor_novo_sobe_o_cansaco_fora_da_falta():
    for cc in COMBINACOES.values():
        for mundo in (False, True):
            def sobem(c):
                g = grafo_do_corpo(CFG, c, taxas_de(CFG, c), mundo)
                return {e.nome: e.efeitos for e in g.emissores if any(q == "cansaco" and d > 0 for q, d in e.efeitos)}
            com, sem = sobem(cc), sobem(replace(cc, metabolismo=False))
            assert set(com) - set(sem) == {"falta_combustivel"}
            assert all(dict(com[n])["cansaco"] == dict(sem[n])["cansaco"] for n in sem)


# ================================================================== G1
@pytest.mark.parametrize("mundo", ["padrao", "fisico"])
def test_g1_o_replay_refaz_o_combustivel_a_reserva_e_as_contas(mundo):
    for cerebro in ("instinto", "P1"):
        v = _vida(mundo, cerebro, MET, "aleatorio", 202)
        fp = lambda cfg=None, _m=mundo, _c=cerebro: _politica(_m, _c, MET)  # noqa: E731
        log = LogDeEventos.de_jsonl(v.motor.log.para_jsonl())
        if mundo == "padrao":
            r = reproduzir_com_feedback(log, fp, CFG, 202, fabrica_motor=_fabrica(mundo, MET))
        else:
            r = reproduzir_mundo(log, fp, CFG, 202, fabrica_motor=_fabrica(mundo, MET))
        assert r.corpo.para_dict() == v.motor.corpo.para_dict()
        assert json.dumps(r.estado(), sort_keys=True, default=repr) == json.dumps(v.motor.estado(), sort_keys=True, default=repr)
        assert v.motor.corpo.contas_metabolismo["mobilizado"] > 0


# ================================================================== G2
def test_g2_a_subchave_desligada_e_a_vida_de_hoje_byte_a_byte():
    gravado = json.loads(gmet.ARQUIVO.read_text(encoding="utf-8"))
    assert len(gravado) == 176
    assert gmet.gerar() == gravado
