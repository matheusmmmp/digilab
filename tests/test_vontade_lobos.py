"""A vontade com o cerebro A (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, PW-3; o D-W4 do #201): `PoliticaLobos.desvio_aprendido` e
`desejo.desejo_lobos`.

- a definicao: a acao de maior desvio aprendido sobre o prior na regra do tempo livre, com a margem de hoje (`limiar_vontade`) e o
  desempate do bandit; a necessidade vem antes, igual ao `desejo_de`;
- a conta exata com pesos postos a mao (a tabela da regra e as entradas do corpo);
- pura: o cerebro sai igual (estado interno, motivos, registro) e a decisao seguinte nao muda;
- o recem-nascido e o cerebro sem aprender nao tem vontade;
- o `desejo_de` de sempre nao muda (o bandit e o instinto como antes; o cerebro A nele sem vontade);
- fora do v11, falha alto;
- o gabarito da web: a secao `vontade` refeita pela funcao, e o resto do gabarito igual.
"""
from __future__ import annotations

import copy
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
import exportar_gabarito_lobos as eg  # noqa: E402

from digilab.config import CONFIG_DESEJO, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, ConfigLobos  # noqa: E402
from digilab.desejo import desejo_de, desejo_lobos  # noqa: E402
from digilab.events import ACOES_PET_HOJE, AcaoPet  # noqa: E402
from digilab.metrics import estados_sonda  # noqa: E402
from digilab.policies.bandit import PoliticaBandit  # noqa: E402
from digilab.policies.lobos import REGRA_VONTADE, PoliticaLobos, ativacao  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto  # noqa: E402

S = 1024
LIVRE = Observacao(vetor_estado=(0.9, 0.9, 0.9, 0.9, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)
TEMPO_LIVRE = (AcaoPet.OCIOSO, AcaoPet.BRINCAR, AcaoPet.CHAMAR_ATENCAO, AcaoPet.EXPLORAR)
_V11: dict = {}


def v11(dono: str = "atencioso", semente: int = 101):
    if (dono, semente) not in _V11:
        b = eg.bancada_v11()
        _V11[(dono, semente)] = (b, b.vida(bv.EspecVida(dono, eg.BRACO_V11, semente)))
    return _V11[(dono, semente)]


# ================================================================== a definicao e a conta exata
def test_o_recem_nascido_e_o_cerebro_sem_aprender_nao_tem_vontade():
    for cl in (ConfigLobos(), CONFIG_LOBOS_APRENDIZ):
        c = PoliticaLobos(CONFIG_PADRAO, cl)
        d = c.desvio_aprendido(LIVRE)
        assert tuple(d) == TEMPO_LIVRE and set(d.values()) == {0.0}
        assert desejo_lobos(LIVRE, c, 7) is None
    assert REGRA_VONTADE == "tempo_livre"


def test_a_conta_exata_com_pesos_postos_a_mao():
    c = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ)
    x = c.percepcao(LIVRE)
    w = c._pesos[REGRA_VONTADE]
    w[AcaoPet.EXPLORAR][0] += 300                    # o vies: +300 / S no explorar
    w[AcaoPet.BRINCAR][4] -= 512                     # o humor 0,9: -512 x 0,9 / S no brincar
    d = c.desvio_aprendido(LIVRE)
    assert d[AcaoPet.EXPLORAR] == ativacao([300] + [0] * (len(x) - 1), x, S) == 300 / S
    assert d[AcaoPet.BRINCAR] == -512 * x[4] / S
    assert d[AcaoPet.OCIOSO] == d[AcaoPet.CHAMAR_ATENCAO] == 0.0
    v = desejo_lobos(LIVRE, c, 42)
    assert (v.tipo, v.alvo, v.tick) == ("vontade", "explorar", 42) and v.intensidade == 300 / S - 0.0
    # abaixo da margem, nada
    w[AcaoPet.EXPLORAR][0] = c._prior[REGRA_VONTADE][AcaoPet.EXPLORAR][0] + 100      # 100 / S < 0,1
    assert desejo_lobos(LIVRE, c, 0) is None
    # o desempate do bandit: com o mesmo desvio, a primeira de ACOES_PET_HOJE; e a intensidade e cortada em 1
    w[AcaoPet.EXPLORAR][0] = c._prior[REGRA_VONTADE][AcaoPet.EXPLORAR][0] + 3000
    w[AcaoPet.OCIOSO][0] = c._prior[REGRA_VONTADE][AcaoPet.OCIOSO][0] + 3000
    assert desejo_lobos(LIVRE, c, 0) is None                                           # margem 0 entre os dois
    w[AcaoPet.OCIOSO][0] = c._prior[REGRA_VONTADE][AcaoPet.OCIOSO][0]
    v = desejo_lobos(LIVRE, c, 0)
    assert v.alvo == "explorar" and v.intensidade == 1.0
    assert ACOES_PET_HOJE.index(AcaoPet.OCIOSO) < ACOES_PET_HOJE.index(AcaoPet.EXPLORAR)


def test_a_necessidade_vem_antes_e_e_a_de_hoje():
    c = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ)
    c._pesos[REGRA_VONTADE][AcaoPet.EXPLORAR][0] += 3000
    rng = random.Random(5)
    for _ in range(300):
        v = tuple(rng.random() for _ in range(5)) + (0.0, 0.0, rng.random())
        obs = Observacao(vetor_estado=v, ticks_desde_cuidado=rng.randrange(480), total_cuidados=0)
        hoje = desejo_de(obs, PoliticaInstinto(CONFIG_PADRAO), 3)
        novo = desejo_lobos(obs, c, 3)
        if hoje is not None:                                                            # o instinto so tem necessidade
            assert novo == hoje
        else:
            assert novo.tipo == "vontade" and novo.alvo == "explorar"


def test_com_o_corpo_entram_as_entradas_novas():
    b, v = v11()
    c = v.motor.politica.cerebro
    obs = v.motor._observacao()
    d = c.desvio_aprendido(obs)
    S_ = c._escala
    x, xc = c.percepcao(obs), [getattr(obs.corpo, r) / S_ for r in c._receptores_novos]
    for a in d:
        base = ativacao([w - w0 for w, w0 in zip(c._pesos[REGRA_VONTADE][a], c._prior[REGRA_VONTADE][a])], x, S_)
        corpo = ativacao([w - w0 for w, w0 in zip(c._pesos_corpo[REGRA_VONTADE][a], c._prior_corpo[REGRA_VONTADE][a])], xc, S_)
        assert d[a] == base + corpo
    assert any(d.values())                                                              # aprendeu de verdade


# ================================================================== pura
def test_a_vontade_e_pura():
    b, v = v11("relapso", 202)
    c = v.motor.politica.cerebro
    antes = copy.deepcopy(c.estado_interno())
    registro = copy.deepcopy(c._registro_decisao)
    for o in estados_sonda(40, 3):
        obs = replace(o, corpo=bv.percepcao_da_sonda(o, b.cfg_corpo_de(bv.EspecVida("relapso", eg.BRACO_V11, 202)), random.Random(1)))
        desejo_lobos(obs, c, 0)
        c.desvio_aprendido(obs)
    assert c.estado_interno() == antes and c._registro_decisao == registro


def test_o_espiao_do_gabarito_nao_muda_a_vida():
    """a vida rejogada com o espiao que calcula a vontade antes de cada decisao e a vida de sempre (o estado interno inteiro)"""
    b, v = v11("aleatorio", 303)
    vida = eg.vida_v11(b, "aleatorio", 303)
    assert eg.vontade_v11(b, vida)["decisoes"]                                           # o replay confere o sha e falha se diferir


# ================================================================== o desejo de hoje e o escopo
def test_o_desejo_de_hoje_nao_muda():
    """o bandit, o instinto e o cerebro A no `desejo_de` como antes: o A sem vontade (a vontade dele e so pelo desejo_lobos)"""
    rng = random.Random(9)
    bandit = PoliticaBandit(CONFIG_PADRAO)
    lobos = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ)
    lobos._pesos[REGRA_VONTADE][AcaoPet.EXPLORAR][0] += 3000
    for _ in range(200):
        v = tuple(rng.random() for _ in range(5)) + (0.0, 0.0, rng.random())
        obs = Observacao(vetor_estado=v, ticks_desde_cuidado=rng.randrange(480), total_cuidados=0)
        d = desejo_de(obs, lobos, 0)
        assert d is None or d.tipo == "necessidade"
        assert desejo_de(obs, PoliticaInstinto(CONFIG_PADRAO), 0) == d
        desejo_de(obs, bandit, 0)                                                       # o bandit roda como sempre
    assert CONFIG_DESEJO.limiar_vontade == 0.1


def test_fora_do_v11_falha_alto():
    c = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_frutas=CONFIG_FRUTAS_LIGADA)
    with pytest.raises(NotImplementedError, match="v11"):
        c.desvio_aprendido(LIVRE)
    with pytest.raises(KeyError):
        PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ).desvio_aprendido(LIVRE, "regra_que_nao_existe")


# ================================================================== o gabarito da web
def test_o_gabarito_da_web_tem_a_vontade_refeita_pela_funcao():
    g = json.loads(eg.ARQUIVO.read_text(encoding="utf-8"))
    sec = g["vontade"]
    assert sec["regra"] == "tempo_livre" and sec["limiar_vontade"] == CONFIG_DESEJO.limiar_vontade
    assert [(v["dono"], v["semente"]) for v in sec["vidas"]] == [(v["dono"], v["semente"]) for v in g["v11"]]
    for v in sec["vidas"]:
        assert len(v["decisoes"]) == len(next(x for x in g["v11"] if x["dono"] == v["dono"])["motivos"])
        tipos = [d["desejo"]["tipo"] if d["desejo"] else None for d in v["decisoes"]]
        assert tipos[0] is None or tipos[0] == "necessidade"                           # o recem-nascido nao tem vontade
        assert "vontade" in tipos and len(v["grade"]) == sec["grade"]["estados"]
        for d in v["decisoes"]:
            if d["desejo"] and d["desejo"]["tipo"] == "vontade":
                ordem = sorted(d["desvio"].items(), key=lambda kv: (-kv[1], ACOES_PET_HOJE.index(AcaoPet(kv[0]))))
                assert d["desejo"]["alvo"] == ordem[0][0]
                assert d["desejo"]["intensidade"] == min(1.0, ordem[0][1] - ordem[1][1])
    # a grade refeita pela funcao, contra o cerebro do fim de uma vida
    b, vida = v11()
    c = vida.motor.politica.cerebro
    from digilab.motor_corpo import PercepcaoCorpo
    for item in sec["vidas"][0]["grade"]:
        obs = Observacao(vetor_estado=tuple(item["vetor"]), ticks_desde_cuidado=item["ticks_desde_cuidado"], total_cuidados=0,
                         corpo=PercepcaoCorpo(**item["corpo"]))
        assert {a.value: x for a, x in c.desvio_aprendido(obs).items()} == item["desvio"]
        d = desejo_lobos(obs, c, 0)
        assert (None if d is None else {"tipo": d.tipo, "alvo": d.alvo, "intensidade": d.intensidade}) == item["desejo"]
