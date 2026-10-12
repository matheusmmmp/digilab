"""O fator do gasto das atividades sobre o combustivel (o no `gasto_atividades` do #273; ME-3 e ME-7 da docs/TAREFA_V2_METABOLISMO.md):
`ConfigCorpo.gasto_atividades_num/gasto_atividades_den`, padrao 1/1.

- G2: com o fator no padrao, as vidas com o metabolismo ligado (`tests/gabaritos/metabolismo_ligado_vidas_de_hoje.json`, gravado antes) e
  as de antes do metabolismo (o gabarito da etapa 0, no teste dele) saem byte a byte;
- a conta exata: cada atividade tira div_arred(cansaco x num, den) do combustivel, e o cansaco nao muda; o andar arredonda uma vez por
  decisao; um fator que zera o gasto falha alto;
- as checagens do grafo passam com o fator, com o mesmo relato do padrao;
- G-HOJE-M e G-CONS-M com o fator; G1 com o fator.
So as sementes dos testes.
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
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_metabolismo_ligado as gml  # noqa: E402
import test_metabolismo as tm  # noqa: E402
from digilab.config import (CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_PADRAO, ConfigCorpo)
from digilab.corpo import PARAMETROS_CORPO, Corpo, div_arred, gasto_da_atividade, grafo_do_corpo, taxas_de  # noqa: E402
from digilab.corpo_grafo import checar  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402

CFG = CONFIG_PADRAO
CM = CONFIG_MUNDO_LIGADA
MET = CONFIG_CORPO_METABOLISMO
MIN = ConfigCorpo(ligada=True, digestao=True, metabolismo=True)
C = MIN.escala
FATORES = {"metade": (1, 2), "padrao": (1, 1), "dobro": (2, 1)}         # os pontos do passo 0 (A3.2, ME-7)


def _fator(cc: ConfigCorpo, nome: str) -> ConfigCorpo:
    num, den = FATORES[nome]
    return replace(cc, gasto_atividades_num=num, gasto_atividades_den=den)


# ================================================================== a chave e o registro
def test_o_fator_no_padrao_e_os_erros():
    assert (MET.gasto_atividades_num, MET.gasto_atividades_den) == (1, 1)
    assert PARAMETROS_CORPO["gasto_atividades_num"][0] == PARAMETROS_CORPO["gasto_atividades_den"][0] == "PROPOSTO"
    for campo in ("gasto_atividades_num", "gasto_atividades_den"):
        for ruim in (0, -1, 1.5):
            with pytest.raises(ValueError, match=campo):
                replace(MIN, **{campo: ruim})
    with pytest.raises(ValueError, match="zera o gasto"):
        taxas_de(CFG, replace(MIN, gasto_atividades_den=100000))
    with pytest.raises(ValueError, match="sem cansaco"):
        gasto_da_atividade(MIN, 0)


def test_as_taxas_das_atividades_pelo_fator():
    for nome, (num, den) in FATORES.items():
        cc = _fator(MIN, nome)
        t, t1 = taxas_de(CFG, cc), taxas_de(CFG, MIN)
        for efeitos, de_hoje in ((t.pet[AcaoPet.BRINCAR], t1.pet[AcaoPet.BRINCAR]), (t.pet[AcaoPet.EXPLORAR], t1.pet[AcaoPet.EXPLORAR]),
                                 (t.dono[AcaoUsuario.BRINCAR], t1.dono[AcaoUsuario.BRINCAR])):
            assert efeitos["cansaco"] == de_hoje["cansaco"]                       # o cansaco nunca muda
            assert efeitos["combustivel"] == -div_arred(de_hoje["cansaco"] * num, den)
            assert {k: v for k, v in efeitos.items() if k != "combustivel"} == {k: v for k, v in de_hoje.items() if k != "combustivel"}
    assert taxas_de(CFG, _fator(MIN, "metade")).pet[AcaoPet.EXPLORAR]["combustivel"] == -3375
    assert taxas_de(CFG, _fator(MIN, "dobro")).pet[AcaoPet.BRINCAR]["combustivel"] == -18000


# ================================================================== a conta exata
@pytest.mark.parametrize("nome", list(FATORES))
@pytest.mark.parametrize("op", ["pet_brincar", "pet_explorar", "dono_brincar", "andar"])
def test_cada_atividade_tira_o_cansaco_vezes_o_fator(nome, op):
    num, den = FATORES[nome]
    cc = _fator(MIN, nome)
    c = tm._corpo(cc, combustivel=300000, cansaco=1000)
    sem = tm._corpo(replace(MIN, metabolismo=False), cansaco=1000)
    for x in (c, sem):
        {"pet_brincar": lambda x: x.acao_pet(AcaoPet.BRINCAR), "pet_explorar": lambda x: x.acao_pet(AcaoPet.EXPLORAR),
         "dono_brincar": lambda x: x.acao_dono(AcaoUsuario.BRINCAR),
         "andar": lambda x: x.estimulo_andar(37, CM.custo_energia_por_subunidade)}[op](x)
    subiu = c.q["cansaco"] - 1000
    assert subiu > 0 and 300000 - c.q["combustivel"] == div_arred(subiu * num, den) == c.contas_metabolismo["gasto_atividade"]
    assert {k: v for k, v in c.q.items() if k not in ("combustivel", "reserva")} == sem.q        # o cansaco de hoje nao muda


def test_o_andar_arredonda_uma_vez_por_decisao():
    """37 subunidades x 75 = 2775 de cansaco; x 1/2 = 1387,5 -> 1388 (div_arred: a metade longe do zero), nao 37 x arred(37,5)"""
    c = tm._corpo(_fator(MIN, "metade"), combustivel=300000)
    c.estimulo_andar(37, CM.custo_energia_por_subunidade)
    assert 300000 - c.q["combustivel"] == 1388
    c = tm._corpo(_fator(MIN, "metade"), combustivel=300000)
    c.estimulo_andar(0, CM.custo_energia_por_subunidade)
    assert c.q["combustivel"] == 300000 and c.contas_metabolismo["gasto_atividade"] == 0


# ================================================================== o grafo
@pytest.mark.parametrize("nome", ["metade", "dobro"])
@pytest.mark.parametrize("base", ["minimo", "etapa6", "banheiro"])
@pytest.mark.parametrize("com_mundo", [False, True])
def test_as_checagens_do_grafo_com_o_fator(nome, base, com_mundo):
    cc0 = {"minimo": MIN, "etapa6": MET, "banheiro": replace(CONFIG_CORPO_BANHEIRO, metabolismo=True)}[base]
    cc = _fator(cc0, nome)
    rel = checar(grafo_do_corpo(CFG, cc, taxas_de(CFG, cc), com_mundo))
    rel0 = checar(grafo_do_corpo(CFG, cc0, taxas_de(CFG, cc0), com_mundo))
    assert rel == rel0                                       # o fator so muda o tamanho de efeitos que ja eram negativos


# ================================================================== G2
def test_g2_o_fator_no_padrao_e_a_vida_do_metabolismo_de_hoje():
    gravado = json.loads(gml.ARQUIVO.read_text(encoding="utf-8"))
    assert len(gravado) == 104
    assert gml.gerar() == gravado


def test_g2_o_fator_explicito_1_1_e_o_padrao():
    c1 = Corpo.de_estado(Estado(), CFG, MET, com_mundo=True)
    c2 = Corpo.de_estado(Estado(), CFG, replace(MET, gasto_atividades_num=3, gasto_atividades_den=3), com_mundo=True)
    for c in (c1, c2):
        for i in range(500):
            c.passo(Estado(tick=i, dormindo=i % 7 == 0))
            if i % 9 == 0:
                c.acao_pet(AcaoPet.BRINCAR)
                c.estimulo_andar(i % 61, CM.custo_energia_por_subunidade)
    assert c1.para_dict() == c2.para_dict()


# ================================================================== G-HOJE-M e G-CONS-M com o fator
@pytest.mark.parametrize("mundo", ["padrao", "fisico"])
@pytest.mark.parametrize("nome", ["metade", "dobro"])
def test_g_hoje_m_com_o_fator_so_o_combustivel_muda(tm_historia, mundo, nome):
    cc = _fator(tm.CHEIO, nome)
    for dono, s in tm.VIDAS_H:
        com = tm._vida(mundo, "instinto", cc, dono, s, tm.DIAS_H)
        sem = tm._vida(mundo, "instinto", CONFIG_CORPO_DRIVES, dono, s, tm.DIAS_H).motor
        hc, hs = com.motor.corpo._hist, sem.corpo._hist
        if min(q["combustivel"] for q, *_ in hc) < cc.falta_limiar:
            t = next(i for i, (q, *_) in enumerate(hc) if q["combustivel"] < cc.falta_limiar)
        else:
            t = len(hc)
            assert com.motor.log.para_jsonl() == sem.log.para_jsonl()
        assert t > 0 and [tm._velhos(q) for q, *_ in hc[:t]] == [q for q, *_ in hs[:t]]
        tm._fecha(com.motor.corpo, cc)
        assert com.motor.corpo.contas_metabolismo["gasto_atividade"] > 0


@pytest.fixture()
def tm_historia(monkeypatch):
    original = Corpo.passo

    def passo(self, antes, necessidades=0):
        original(self, antes, necessidades)
        self.__dict__.setdefault("_hist", []).append((dict(self.q), self.resto_combustivel,
                                                      dict(self.contas_metabolismo or {}), self.digerido_total))

    monkeypatch.setattr(Corpo, "passo", passo)


def test_o_gasto_das_atividades_segue_o_fator_na_vida():
    """a mesma vida gasta das atividades mais com o fator maior (o gasto contado e o que de fato saiu: com o combustivel no fundo, ou
    depois da falta, as vidas se separam, e a proporcao nao e exata)"""
    gastos = {}
    for nome in FATORES:
        v = tm._vida("fisico", "instinto", _fator(tm.CHEIO, nome), "aleatorio", 202, tm.DIAS_H)
        gastos[nome] = v.motor.corpo.contas_metabolismo["gasto_atividade"]
    assert gastos["metade"] < gastos["padrao"] < gastos["dobro"]


# ================================================================== G1
@pytest.mark.parametrize("mundo,nome", [("padrao", "dobro"), ("fisico", "metade")])
def test_g1_o_replay_com_o_fator(mundo, nome):
    cc = _fator(MET, nome)
    for cerebro in ("instinto", "P1"):
        v = tm._vida(mundo, cerebro, cc, "aleatorio", 202)
        fp = lambda cfg=None, _m=mundo, _c=cerebro: tm._politica(_m, _c, cc)  # noqa: E731
        log = LogDeEventos.de_jsonl(v.motor.log.para_jsonl())
        rep = reproduzir_com_feedback if mundo == "padrao" else reproduzir_mundo
        r = rep(log, fp, CFG, 202, fabrica_motor=tm._fabrica(mundo, cc))
        assert r.corpo.para_dict() == v.motor.corpo.para_dict()
        assert r.corpo.cc.gasto_atividades_num == FATORES[nome][0]
