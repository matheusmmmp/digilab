"""A continuacao do alvo `banheiro` (decisao do Matheus, 2026-10-11; pedido do Gerente): o `aliviar` com o alvo `banheiro` que nao chega
ao banheiro segura a vontade e deixa o alvo pendente, como o `continuar`; a regra urgente segue aliviando `aqui`. E o `_tick_social` do
ramo do ALIVIAR no grupo.

Gates: G2 (a chave desligada e a vida de hoje: os gabaritos de sempre rodam na suite; com o banheiro ligado, as vidas do gabarito gravado
antes, tests/gabaritos/banheiro_ligado_antes.json, saem iguais ate a primeira decisao que aliviava no caminho e, nela, o pet no mesmo lugar
com o mesmo alvo, segurando), G-MEC da continuacao, o instinto que segue a ida, e G1 (replay bit a bit com idas que continuam). So as
sementes dos testes.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_banheiro_ligado as gbl  # noqa: E402
import gabarito_mundo as gm  # noqa: E402
import test_banheiro_mundo as tb  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.grupo import Grupo  # noqa: E402
from digilab.instinto_banheiro import REGRA_ALIVIO_URGENTE, PoliticaInstintoBanheiro  # noqa: E402
from digilab.mundo import Alvo, PercepcaoMundo, reproduzir_mundo  # noqa: E402
from digilab.policy import Observacao  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402

CB, CC, C, S = tb.CB, tb.CC, tb.C, tb.S
LONGE = tb.FORA_LONGE                                # (200, 64): 137 do banheiro, tres decisoes (60, 60, 17)
GABARITO = json.loads((RAIZ / "tests" / "gabaritos" / "banheiro_ligado_antes.json").read_text(encoding="utf-8"))


class RoteiroAlvos(tb.Roteiro):
    """o Roteiro com um alvo por decisao de aliviar (a lista acaba: o ultimo fica)"""

    def __init__(self, acoes, alvos) -> None:
        super().__init__(acoes, alvos[0])
        self.alvos = list(alvos)

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        if acao is AcaoPet.ALIVIAR:
            self.alvo = self.alvos.pop(0) if len(self.alvos) > 1 else self.alvos[0]
        return super().escolher_alvo(acao, candidatos, percepcao, u)


def motor(acoes, alvos, pet=LONGE, vontade=300000):
    pol = RoteiroAlvos(acoes, alvos)
    m = tb.fm(CB)(pol, CONFIG_PADRAO, 101)
    m.pet = pet
    m.corpo.q["vontade"] = vontade
    return m, pol


def pendentes(pol) -> list:
    return [o.mundo.alvo_pendente for o in pol.obs]


# ================================================================== G-MEC da continuacao
def test_a_ida_continua_ate_chegar_e_alivia_dentro():
    m, pol = motor([AcaoPet.ALIVIAR] * 3, ["banheiro"])
    for _ in range(3):
        m.avancar(15)
    assert pendentes(pol) == [None, "banheiro", "banheiro"]                 # a percepcao mostra a ida pendente
    assert [(i["de"], i["para"], i["distancia"], i["restante"], i["continuacao"]) for i in m.idas_banheiro] == [
        (LONGE, (140, 64), 137, 77, False), ((140, 64), (80, 64), 77, 17, True)]
    assert m.alivios == [{"tick": 30, "dentro": True, "urgente": False, "alvo": "banheiro", "distancia": 17, "recolhido": False}]
    assert m.pet == (63, 64) and m.resumo_mundo_fisico()["pendente"] is None
    assert [(n["x"], n["y"]) for n in m.mundo.necessidades.values()] == [(63, 64)]
    # segurando: so o andar vai ao corpo; a vontade sobe ate o alivio e cai a zero nele
    for _, oc, _ in pol.corpo[:2]:
        assert not any(e[0] in ("aliviar", "necessidade") for e in oc["estimulos"]) and ("andar", 60) in oc["estimulos"]
    assert ("aliviar", True) in pol.corpo[2][1]["estimulos"]
    v = [o.corpo.vontade for o in pol.obs] + [pol.corpo[2][2].corpo.vontade]
    assert v[0] < v[1] < v[2] and v[3] == 0
    assert [d["alvo"] for d in m.decisoes_mundo] == ["banheiro"] * 3 and [d["chegou"] for d in m.decisoes_mundo] == [False, False, True]


def test_aqui_no_meio_da_ida_alivia_onde_esta():
    m, pol = motor([AcaoPet.ALIVIAR] * 2, ["banheiro", "aqui"])
    m.avancar(15)
    m.avancar(15)
    assert m.alivios == [{"tick": 15, "dentro": False, "urgente": False, "alvo": "aqui", "distancia": 77, "recolhido": False}]
    assert m.pet == (140, 64) and m.resumo_mundo_fisico()["pendente"] is None and len(m.idas_banheiro) == 1


def test_outra_acao_desfaz_a_ida():
    m, pol = motor([AcaoPet.ALIVIAR, AcaoPet.OCIOSO, AcaoPet.ALIVIAR], ["banheiro"])
    for _ in range(3):
        m.avancar(15)
    assert pendentes(pol) == [None, "banheiro", None]
    assert [i["continuacao"] for i in m.idas_banheiro] == [False, False] and m.alivios == []
    assert m.resumo_mundo_fisico()["pendente"]["alvo"]["tipo"] == "banheiro"     # a segunda ida, de novo pendente


def test_a_urgencia_alivia_aqui_mesmo_com_a_ida_pendente():
    m, pol = motor([AcaoPet.ALIVIAR] * 2, ["banheiro", "aqui"])
    m.avancar(15)
    m.corpo.q["vontade"] = int(0.95 * C)
    m.avancar(15)
    assert pendentes(pol) == [None, "banheiro"]
    assert m.alivios == [{"tick": 15, "dentro": False, "urgente": True, "alvo": "aqui", "distancia": 77, "recolhido": False}]
    m2, _ = motor([AcaoPet.ALIVIAR] * 2, ["banheiro"])
    m2.avancar(15)
    m2.corpo.q["vontade"] = int(0.95 * C)
    with pytest.raises(RuntimeError, match="urgente"):                     # o cerebro que insiste no banheiro na urgencia falha alto
        m2.avancar(15)


def test_ao_alcance_nada_muda():
    """o banheiro ao alcance: chega e alivia na mesma decisao, sem ida pendente (o de antes)"""
    m, _ = motor([AcaoPet.ALIVIAR], ["banheiro"], pet=tb.FORA_PERTO)
    m.avancar(15)
    assert m.idas_banheiro == [] and m.alivios[0]["dentro"] and m.resumo_mundo_fisico()["pendente"] is None


# ================================================================== o instinto segue a ida
def _perc(pendente):
    return PercepcaoMundo(200, 64, 0, (), 0, 0, pendente)


def _obs(vontade):
    pc = PercepcaoCorpo(fome=S, higiene=S, energia=S, humor=S, saude=S, tedio=0, curiosidade=0, solidao=0, estresse=0, dor=0, susto=0,
                        vontade=round(vontade * S), conforto=0)
    return Observacao(vetor_estado=(0.8, 0.8, 0.7, 0.5, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=0, total_cuidados=0, mundo=_perc(None),
                      corpo=pc)


def test_o_instinto_segue_a_ida_e_a_urgencia_alivia_aqui():
    p = PoliticaInstintoBanheiro(CONFIG_PADRAO, CB, CC)
    cands = [Alvo("banheiro", 63, 64), Alvo("aqui", 200, 64)]
    p.agir(_obs(0.75), random.Random(3))
    assert p.ultima_regra != REGRA_ALIVIO_URGENTE
    assert all(p.escolher_alvo(AcaoPet.ALIVIAR, cands, _perc("banheiro"), u).tipo == "banheiro" for u in range(0, 1 << 16, 97))
    sem = [p.escolher_alvo(AcaoPet.ALIVIAR, cands, _perc(None), u).tipo for u in range(0, 1 << 16, 97)]
    assert "aqui" in sem and "banheiro" in sem                             # sem a ida pendente, o sorteio herdado de sempre
    assert {p.escolher_alvo(AcaoPet.ALIVIAR, cands, _perc("comida"), u).tipo for u in range(0, 1 << 16, 97)} == set(sem)
    p.agir(_obs(0.95), random.Random(3))
    assert p.ultima_regra == REGRA_ALIVIO_URGENTE
    assert all(p.escolher_alvo(AcaoPet.ALIVIAR, cands, _perc("banheiro"), u).tipo == "aqui" for u in (0, 1, 40000, 65535))


# ================================================================== G2: as vidas do banheiro ligado, gravadas antes
def _motores(tipo, arg):
    if tipo == "direto":
        cerebro, nome, s = arg
        cbh = gbl.CBHS[nome]
        fp = tb.fp_instinto(cbh) if cerebro == "instinto" else tb.fp_lobos(cbh)
        v, _ = tb.vida(fp, cbh, semente=s, dias=gbl.DIAS, carinho=True)
        return {None: (v.motor, v.interacoes)}
    if tipo == "bancada":
        braco, cerebro, s = arg
        with gbl.canto():                               # a area de antes (BN-8): a do gabarito
            v = bv.Bancada(gbl.DIAS, 16 * gbl.DIAS).vida(bv.EspecVida("atencioso", braco, s, None, "fisico", cerebro,
                                                                      lugar="comedouro"))
        return {None: (v.motor, v.interacoes)}
    g = gbl.vida_grupo(arg)
    return {i: (g.motores[i], None) for i in ("A", "B")}


def _sha(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=repr).encode()).hexdigest()


@pytest.mark.parametrize("chave,caso", list(gbl.casos()), ids=[c for c, _ in gbl.casos()])
def test_g2_as_vidas_do_banheiro_ligado_ate_a_primeira_ida_que_nao_chega(chave, caso):
    """Sem nenhum alivio no caminho com o alvo banheiro, a vida de antes byte a byte (o resumo do mundo so ganha `idas_banheiro`, vazio).
    Com um: tudo igual ate a decisao k* (o prefixo das decisoes, os alivios antes); na k*, o pet no mesmo ponto, com o mesmo alvo, e no
    lugar do alivio no caminho, uma ida que segura a vontade."""
    antes = GABARITO[chave]
    for ident, (m, inter) in _motores(*caso).items():
        old = antes if ident is None else antes[ident]
        if old["corte"] is None:
            assert gbl.k_estrela(m) is None and m.idas_banheiro == []
            imp = gm.impressao(m, inter)
            r = m.resumo_mundo_fisico()
            assert r.pop("idas_banheiro") == []
            imp["fisico"] = _sha(r)
            assert imp == old["impressao"] and len(m.alivios) == old["alivios"]
            continue
        t = old["corte"]
        prefixo = [d for d in m.decisoes_mundo if d["tick"] < t]
        assert (len(prefixo), _sha(prefixo)) == (old["n_prefixo"], old["prefixo"])
        assert [a for a in m.alivios if a["tick"] < t] == old["alivios_antes"] and not any(i["tick"] < t for i in m.idas_banheiro)
        if old["k"] is None:                                                # no grupo: o pet sem a k* (o corte e do outro)
            continue
        _, de, x, y, alvo = old["decisao"]
        dk = m.decisoes_mundo[old["k"]]
        assert (dk["tick"], list(dk["antes"]), dk["x"], dk["y"], dk["alvo"], dk["acao"]) == (t, de, x, y, alvo, "aliviar")
        assert not dk["chegou"] and not any(a["tick"] == t for a in m.alivios)    # nao aliviou no caminho
        ida = next(i for i in m.idas_banheiro if i["tick"] == t)
        assert ida["para"] == (x, y) and not ida["continuacao"]


def test_o_gabarito_tem_vidas_dos_dois_lados():
    regs = [v for c, v in GABARITO.items() if not c.startswith("grupo")] + [
        v[i] for c, v in GABARITO.items() if c.startswith("grupo") for i in "AB"]
    assert sum(r["corte"] is None for r in regs) >= 10 and sum(r["k"] is not None for r in regs) >= 10
    assert any(r["corte"] is not None and r["k"] is None for r in regs)          # o grupo: o corte que vem do outro pet


# ================================================================== G1 com idas que continuam
@pytest.mark.parametrize("cerebro,semente,continua", [("instinto", 101, True), ("lobos", 303, False)])
def test_g1_replay_com_a_continuacao(cerebro, semente, continua):
    """o replay refaz as idas (a do instinto na semente 101 continua na decisao seguinte; os lobos aprendendo, P1)"""
    fp = tb.fp_instinto(CB) if cerebro == "instinto" else tb.fp_lobos(CB)
    v, _ = tb.vida(fp, CB, semente=semente, dias=4, carinho=True)
    m = v.motor
    assert m.idas_banheiro and any(i["continuacao"] for i in m.idas_banheiro) is continua
    r = reproduzir_mundo(m.log, fp, semente=semente, fabrica_motor=tb.fm(CB))
    assert tb.texto(r.resumo_mundo_fisico()) == tb.texto(m.resumo_mundo_fisico())
    assert tb.texto(r.estado()) == tb.texto(m.estado()) and tb.texto(r.politica.estado_interno()) == tb.texto(m.politica.estado_interno())


# ================================================================== o _tick_social do ALIVIAR no grupo
def test_no_grupo_todo_pet_que_decidiu_tem_o_tick_social_do_tick(monkeypatch):
    """O ramo do ALIVIAR nao preenchia o `_tick_social` (os outros preenchem): a disputa e o toque do fim do tick liam o de uma decisao
    velha. Agora, em todo tick com decisao, cada pet que decidiu tem o do tick, com o alvo do aliviar."""
    vistos = {"aliviar": 0, "outras": 0}
    original = Grupo._toque_e_disputa

    def espiao(self, presentes, ordem):
        for i in ordem:
            m = self.motores[i]
            ts = self._no_tick(m)
            assert ts is not None, (i, self.tick, m.decisoes_mundo[-1]["acao"])
            assert m.decisoes_mundo[-1]["tick"] == self.tick
            if m.decisoes_mundo[-1]["acao"] == "aliviar":
                assert ts["alvo"].tipo in ("banheiro", "aqui") and ts["comeu"] is None and ts["social"] is None
                vistos["aliviar"] += 1
            else:
                vistos["outras"] += 1
        return original(self, presentes, ordem)

    monkeypatch.setattr(Grupo, "_toque_e_disputa", espiao)
    gbl.vida_grupo(303)
    assert vistos["aliviar"] > 0 and vistos["outras"] > 0
