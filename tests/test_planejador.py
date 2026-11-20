"""J5, etapa 2 (docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.2 e a tabela das etapas): o planejador de um alvo e o lobo `planejamento`.

- G2: com `g_plano` 0, as vidas do gabarito da etapa (`tests/gabaritos/pet_que_pensa_plano_vidas_de_hoje.json`, gravado antes) saem
  byte a byte, com os motivos e as falas;
- G-PESOS-A: o `n_pesos` do A e o mesmo com e sem o planejador (PQ-6);
- a conta exata de V(k) (o valor de cada tipo pelo `sinal_corpo` da leitura prevista, o custo de andar na mesma conta) e do termo (com o
  corte em +-teto_plano), e o termo no peso efetivo da decisao e do alvo;
- a sonda "quem decidiu" reproduz a escolha sem o termo, com o mesmo u;
- o fator do motivo (so quando a sonda muda a escolha, so o que os modelos tem) e os textos da expressao;
- G1: o replay refaz o planejador (os modelos, o plano de cada decisao, os motivos) bit a bit;
- os modelos no cerebro: os troncos da percepcao (#290), a fruta na mao (G-SEM-CREDITO: so o desfecho aprende) e o congelamento (PP-8).
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

import gabarito_pet_que_pensa_plano as gp  # noqa: E402
from digilab import modelo_mundo as mm  # noqa: E402
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_LOBOS, CONFIG_MODELO_MUNDO_LIGADA, CONFIG_PADRAO, ConfigLobos)  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.expressao import expressar, validar_tabelas  # noqa: E402
from digilab.motivo import FATORES_VIDA, Motivo, PoliticaComMotivo, fator_do_plano, motivo_lobos, nome_base  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.mundo import Alvo, MotorMundo, PercepcaoMundo, reproduzir_mundo  # noqa: E402
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import (FATORES_PLANO, LOBO_PLANEJAMENTO, PoliticaLobos, div_arred, sinal_corpo,  # noqa: E402
                                    sortear, valor_previsto)
from digilab.policy import Observacao  # noqa: E402

S = CONFIG_LOBOS.escala
CM = gp.LAYOUTS["padrao"]
CQ = gp.CORPOS["quimica"]
GABARITO = json.loads(gp.ARQUIVO.read_text(encoding="utf-8"))
CASOS = dict(gp.casos())


def plano(g=S // 2, **kw) -> ConfigLobos:
    return replace(gp.P1_PLANO, g_plano=g, **kw)


def cerebro(g=S // 2, cfg_corpo=CQ, **kw) -> PoliticaLobos:
    return PoliticaLobos(CONFIG_PADRAO, plano(g), cfg_mundo=CM, cfg_corpo=cfg_corpo, cfg_consequencia=gp.gq.CC_CANAIS, **kw)


def pc(fome=S, higiene=S, energia=S, humor=S, saude=S) -> PercepcaoCorpo:
    return PercepcaoCorpo(fome=fome, higiene=higiene, energia=energia, humor=humor, saude=saude)


def pm(x: int, y: int, vistos=(), troncos=()) -> PercepcaoMundo:
    return PercepcaoMundo(x=x, y=y, regiao=0, vistos=tuple(vistos), cheiro=0, direcao_cheiro=0, alvo_pendente=None, troncos=tuple(troncos))


def obs_de(corpo, mundo) -> Observacao:
    return Observacao(vetor_estado=(0.8,) * 6 + (0.0, 0.5), ticks_desde_cuidado=0, total_cuidados=0, corpo=corpo, mundo=mundo)


def lugar(nome: str) -> tuple[int, int]:
    return next((x, y) for n, x, y in mm.lugares_do_layout(CM) if n == nome)


# ================================================================== a config, os registros e as falhas altas
def test_config_registro_e_falhas_altas():
    assert CONFIG_LOBOS.g_plano == 0 and CONFIG_LOBOS.teto_plano == 2 * S
    lb.validar_parametros_lobos()
    assert {lb.PARAMETROS_LOBOS[k][0] for k in ("g_plano", "teto_plano")} == {"PROPOSTO"}
    assert set(FATORES_PLANO) <= set(FATORES_VIDA)
    validar_tabelas()
    for ruim in ({"g_plano": -1}, {"g_plano": 1.0}, {"teto_plano": 0}):
        with pytest.raises(ValueError):
            PoliticaLobos(CONFIG_PADRAO, replace(plano(), **ruim), cfg_mundo=CM, cfg_corpo=CQ)
    with pytest.raises(ValueError, match="exige"):                                    # sem o corpo
        PoliticaLobos(CONFIG_PADRAO, plano(), cfg_mundo=CM)
    with pytest.raises(ValueError, match="exige"):                                    # sem o alvo aprendido
        PoliticaLobos(CONFIG_PADRAO, plano(alvo_aprendido=False, alvo_por_arvore=False), cfg_mundo=CM, cfg_corpo=CQ)
    with pytest.raises(ValueError, match="exige"):                                    # sem o aprendizado
        PoliticaLobos(CONFIG_PADRAO, plano(aprendizado_ligado=False), cfg_mundo=CM, cfg_corpo=CQ)
    with pytest.raises(ValueError, match="so com"):                                   # os cfg do plano sem o plano
        PoliticaLobos(CONFIG_PADRAO, gp.P1_PLANO, cfg_mundo=CM, cfg_corpo=CQ, cfg_modelo=CONFIG_MODELO_MUNDO_LIGADA)
    c = cerebro()
    with pytest.raises(RuntimeError, match="ConfigConsequencia"):                     # o cc do credito diferente do do plano
        c._conferir_cc_do_plano(replace(gp.gq.CC_CANAIS, ganho=8))
    c._conferir_cc_do_plano(gp.gq.CC_CANAIS)


# ================================================================== G-PESOS-A
def test_g_pesos_a_o_planejador_nao_tem_pesos():
    sem = PoliticaLobos(CONFIG_PADRAO, gp.P1_PLANO, cfg_mundo=CM, cfg_corpo=CQ)
    for g in (S // 4, S // 2, S):
        com = cerebro(g)
        assert com.n_pesos() == sem.n_pesos() == 822
        assert com.modelo_mundo is not None and sem.modelo_mundo is None
        assert com.modelo_mundo.cfg.teto_modelo == CONFIG_MODELO_MUNDO_LIGADA.teto_modelo


# ================================================================== G2: g_plano 0 e a vida de hoje
@pytest.mark.parametrize("chave", sorted(CASOS))
def test_g2_g_plano_zero_e_a_vida_de_hoje(chave):
    assert gp.impressao_de(CASOS[chave]) == GABARITO[chave]


def test_g2_sem_plano_nada_novo_no_estado_nem_no_motivo():
    m, p, _ = gp.vida("padrao", "quimica", "P1-plano", "comedouro", 101)
    est = p.cerebro.estado_interno()
    assert "plano" not in est
    assert all(LOBO_PLANEJAMENTO not in x["contribuicoes"] and "plano" not in x and "alvo_plano" not in x for x in est["motivos"])


# ================================================================== a conta exata de V(k) e do termo
def _cerebro_com_modelos():
    c = cerebro(S // 2)
    m = c.modelo_mundo
    jx, jy = lugar("J1")
    m.decisao(obs_de(pc(), pm(jx, jy)))                                   # o pet ve o J1 (e o que estiver no raio)
    m.desfecho["b"] = [300, 0, 0, -40, 0]                                # b: fome +300, humor -40
    m.desfecho["racao"] = [250, 0, 0, 0, 0]
    m.andar = -170                                                       # -170/S de energia por subunidade
    m.mapa["J1"] = [0, 0, 512, 0, 0]                                     # no J1 se viu b, metade da escala
    return c, m, (jx, jy)


def test_conta_exata_do_valor_do_andar_e_de_v():
    c, m, (jx, jy) = _cerebro_com_modelos()
    agora = pc(fome=500, energia=800, humor=900)
    drives = c._drives_plano
    assert drives == ("fome", "higiene", "energia", "humor")
    cc = gp.gq.CC_CANAIS
    pd = dict(cc.pesos_drives_corpo)
    valores = c._valores_do_plano(agora)
    esperado_b = sinal_corpo(agora, replace(agora, fome=800, humor=860), drives, cc.ganho, S, pd)
    assert valores["b"] == esperado_b == valor_previsto(agora, {"fome": 300, "humor": -40}, drives, cc.ganho, S, pd)
    assert valores["racao"] == sinal_corpo(agora, replace(agora, fome=750), drives, cc.ganho, S, pd)
    assert valores["a"] == valores["c"] == valores["podre"] == 0                  # o prior: nada previsto
    assert valor_previsto(pc(fome=1000), {"fome": 300}, drives, cc.ganho, S, pd) == \
        sinal_corpo(pc(fome=1000), pc(fome=S), drives, cc.ganho, S, pd)            # o corte em S
    # o pet a 100 subunidades do J1: V = div_arred(512 x valor_b, S) + o valor do andar 100
    x0, y0 = jx - 100, jy
    andar = sinal_corpo(agora, replace(agora, energia=800 + div_arred(-170 * 100, S)), drives, cc.ganho, S, pd)
    assert c._valor_do_andar(agora, 100) == andar < 0
    prev, rotulo = c._previsao_do_alvo("arvore:J1", jx, jy, None, None, {})
    assert prev == {"b": 512} and rotulo == ("lugar", "J1")
    v = c._valor_do_alvo(prev, jx, jy, pm(x0, y0), agora, valores)
    assert v == div_arred(512 * valores["b"], S) + andar
    assert c._termo_do_plano(v) == div_arred((S // 2) * v, S)
    assert c._termo_do_plano(10 ** 9) == 2 * S and c._termo_do_plano(-10 ** 9) == -2 * S       # o corte em +-teto_plano
    # a comida vista e certa; a podre e "podre"; o cheiro perto do J1 usa a linha do J1; longe de tudo, nada
    assert c._previsao_do_alvo("comida", 0, 0, 7, None, {7: "b"}) == ({"b": S}, ("comida", "b"))
    assert c._previsao_do_alvo("comida", 0, 0, 7, None, {7: "a_podre"}) == ({"podre": S}, ("comida", "podre"))
    assert c._previsao_do_alvo("cheiro", jx + 10, jy, None, None, {}) == ({"b": 512}, ("lugar", "J1"))
    assert c._previsao_do_alvo("vagar", 0, 470, None, None, {}) == ({}, ("lugar", None))


def test_o_termo_entra_no_peso_efetivo_da_decisao():
    """numa vida com o plano, em toda decisao: a contribuicao do lobo planejamento e o termo / S (so em comer e explorar), o peso efetivo
    e a soma das contribuicoes, e a sonda (o mesmo u, sem o termo) da a acao_sem_plano"""
    m, p, _ = gp.vida("padrao", "quimica", "P1-plano", "comedouro", 101, cfg_lobos=plano(S))
    motivos = p.cerebro.motivos
    vistos_termo = 0
    for x in motivos:
        pl = x["plano"]
        contrib = x["contribuicoes"]
        cands = x["candidatos"]
        for a in cands:
            t = pl["termos"][a]
            assert contrib[LOBO_PLANEJAMENTO][a] == t / S
            assert t == 0 or a in ("comer", "explorar")
            vistos_termo += t != 0
            soma = contrib["impulsos"][a] + contrib["decisao"][a] + contrib["memoria_emocao"][a] + contrib["piso"][a]
            assert x["pesos"][a] == soma + contrib[LOBO_PLANEJAMENTO][a]
        if x["u"] is None:
            assert pl["acao_sem_plano"] == x["acao"] and not pl["plano_decidiu"]
            continue
        piso = p.cerebro._piso
        sem = []
        for a in cands:
            s = contrib["impulsos"][a] + contrib["decisao"][a] + contrib["memoria_emocao"][a]
            sem.append(contrib["impulsos"][a] + contrib["decisao"][a] + contrib["memoria_emocao"][a] + (piso - s if s < piso else 0.0))
        alt = cands[sortear(sem, x["u"])] if any(pl["termos"][a] for a in cands) else x["acao"]
        assert alt == pl["acao_sem_plano"] and pl["plano_decidiu"] == (alt != x["acao"])
    assert vistos_termo > 0


def test_o_termo_no_alvo_e_a_sonda_do_alvo():
    """o alvo aprendido com o plano: o representante de cada classe e o de maior V, o peso da classe ganha o termo / S (com o piso), e a
    sonda e o alvo de hoje com o mesmo u. Montado com candidatos dados, a conta exata."""
    c, m, (jx, jy) = _cerebro_com_modelos()
    agora = pc(fome=500, energia=800, humor=900)
    perc = pm(jx - 30, jy, vistos=[(7, "b", 30, 0, 30), (8, "a", -20, 0, 20)])
    c._pc_na_decisao = agora
    c._plano_na_decisao = c._plano_da_decisao(agora, perc)
    c._ultima_regra = "fruta_no_cenario"
    c._registro_decisao = {"acao": AcaoPet.COMER}
    c.motivos.append({})
    cands = [Alvo("comida", jx - 50, jy, 8), Alvo("comida", jx, jy, 7), Alvo("cheiro", jx + 5, jy)]
    u = 40000
    escolhido = c._alvo_aprendido(AcaoPet.COMER, cands, perc, u)
    ap = c.motivos[-1]["alvo_plano"]
    valores = c._plano_na_decisao["_valores"]
    v_b = div_arred(S * valores["b"], S) + c._valor_do_andar(agora, 30)
    v_a = c._valor_do_andar(agora, 20)                                   # a ainda nao tem desfecho: so o andar
    assert ap["V"]["comida"] == max(v_a, v_b) == v_b                     # o representante da comida e a b
    assert ap["termos"]["comida"] == c._termo_do_plano(v_b)
    pesos = c.motivos[-1]["alvo_aprendido"]["pesos"]
    tabela = c._pesos_alvo_mundo["fruta_no_cenario:comer"]
    assert pesos["comida"] == max(c._piso, max(0, tabela["comida"]) / S + 1.0 + ap["termos"]["comida"] / S)
    assert pesos["cheiro"] == max(c._piso, max(0, tabela["cheiro"]) / S + ap["termos"]["cheiro"] / S)
    # a sonda: as classes de hoje (o primeiro de cada), sem o termo, com o mesmo u
    sem = [max(0, tabela["comida"]) / S + 1.0, max(0, tabela["cheiro"]) / S]
    alt = [cands[0], cands[2]][sortear(sem, u / lb.ESCALA_U_ALVO)]
    assert ap["plano_decidiu"] == (escolhido != alt)
    assert escolhido in (cands[1], cands[2])


# ================================================================== o fator e os textos
def test_o_fator_so_nomeia_o_que_os_modelos_tem():
    c, m, _ = _cerebro_com_modelos()
    valores = {"racao": 500, "a": -300, "b": 400, "c": 0, "podre": -100}
    base = {"valores": valores}
    # o escolhido ganhou pelo termo e vale: o tipo que mais pesa nele
    assert c._fator_do_plano({**base, "termo": [200, 10], "prev": [{"b": 512, "a": 100}, {}],
                              "rotulo": [("lugar", "J2"), None]}, 0, 1) == ["plano_arvore", "J2", "b"]
    assert c._fator_do_plano({**base, "termo": [300, 0], "prev": [{"racao": S}, {}], "rotulo": [("comida", "racao"), None]},
                             0, 1) == ["plano_comida", "racao"]
    # o que seria escolhido sem o plano perdeu por um termo negativo: o tipo que pesou contra
    assert c._fator_do_plano({**base, "termo": [0, -150], "prev": [{}, {"a": S}], "rotulo": [None, ("comida", "a")]},
                             0, 1) == ["plano_evita", "a"]
    # o plano decidiu so pelo andar (nenhum tipo a nomear) ou sem lugar: nenhum fator
    assert c._fator_do_plano({**base, "termo": [50, -10], "prev": [{}, {}], "rotulo": [("lugar", None), ("lugar", None)]}, 0, 1) is None
    assert c._fator_do_plano({**base, "termo": [50, 0], "prev": [{"b": 512}, {}], "rotulo": [("lugar", None), None]}, 0, 1) is None


def test_o_motivo_poe_o_fator_do_plano_e_a_expressao_o_diz():
    reg = {"plano": {"plano_decidiu": True, "fator": ["plano_arvore", "J2", "b"]}}
    assert fator_do_plano(reg) == "plano_arvore(J2,b)"
    assert fator_do_plano({"plano": {"plano_decidiu": False, "fator": ["plano_comida", "b"]}}) is None
    assert fator_do_plano({"plano": {"plano_decidiu": True, "fator": None},
                           "alvo_plano": {"plano_decidiu": True, "fator": ["plano_evita", "a"]}}) == "plano_evita(a)"
    with pytest.raises(ValueError):
        fator_do_plano({"plano": {"plano_decidiu": True, "fator": ["outro", "a"]}})
    textos = {"plano_arvore(J2,b)": "porque no J2 lá cai b, que me faz bem", "plano_comida(racao)": "porque vi ali racao, que me faz bem",
              "plano_evita(a)": "porque a me faz mal"}
    for f, texto in textos.items():
        assert nome_base(f) in FATORES_PLANO
        assert texto in expressar(Motivo("vida", "explorar", (f,), (), 0.5, False, tick=1), "adulto").conteudo


def test_numa_vida_o_fator_aparece_so_quando_o_plano_decidiu():
    """com o PoliticaComMotivo: todo motivo com fator do plano vem de uma decisao (ou alvo) em que a sonda mudou a escolha, com o fator
    que o cerebro achou; nenhum fator do plano sem isso"""
    achados = 0
    for g in (S, 2 * S):
        m, p, _ = gp.vida("padrao", "quimica", "P1-plano-motivo", "comedouro", 101, cfg_lobos=plano(g, teto_plano=4 * S))
        regs = p.interna.cerebro.motivos
        assert len(regs) == len(p.motivos)
        for reg, mot in zip(regs, p.motivos):
            fp = fator_do_plano(reg)
            planos = [f for f in mot.fatores if nome_base(f) in FATORES_PLANO]
            assert planos == ([fp] if fp else [])
            achados += fp is not None
            for f in mot.fatores:
                assert nome_base(f) in FATORES_VIDA
            expressar(mot, "adulto", 0.5)
    assert achados > 0


# ================================================================== G1
def test_g1_o_replay_refaz_o_planejador():
    caso = ("padrao", "quimica", "P1-plano-motivo", "longe", 202)
    cl = plano(S)
    m, p, _ = gp.vida(*caso, cfg_lobos=cl)
    texto = m.log.para_jsonl()
    from digilab.events import LogDeEventos
    refeito = []

    def fab_p(cfg):
        q = gp.politica("P1-plano-motivo", "padrao", "quimica", cfg_lobos=cl)
        refeito.append(q)
        return q
    x, _ = gp.xy_do_caso("longe", 202)
    fm = lambda q, cfg, s: gp.MotorMundoCorpo(q, cfg, s, obediencia_desligada=True, cfg_mundo=CM, efeito_frutas=gp.gq.efeito_do_plano(x),  # noqa: E731
                                              cfg_corpo=CQ, cfg_pqp=gp.CONFIG_PQP_MUNDO_LIGADA)
    m2 = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fab_p, CONFIG_PADRAO, 202, fm)
    a = json.dumps(p.estado_interno(), sort_keys=True, default=repr)
    b = json.dumps(refeito[0].estado_interno(), sort_keys=True, default=repr)
    assert a == b and "plano" in p.estado_interno()
    assert [repr(x) for x in refeito[0].motivos] == [repr(x) for x in p.motivos]
    assert m2.resumo_mundo_fisico() == m.resumo_mundo_fisico()


# ================================================================== os modelos no cerebro
def test_os_troncos_da_percepcao_batem_com_os_lugares_vistos():
    """com o mundo do J5 ligado, as arvores que os modelos do cerebro viram sao as `troncos_vistos` do motor (a conta e a mesma, na
    decisao e depois de andar); a conferencia falha alto se a percepcao trouxer um tronco que a conta nao ve"""
    for caso in (("padrao", "quimica", "P1-plano", "comedouro", 101), ("afastado", "metabolismo", "P1-plano", "comedouro", 202)):
        m, p, _ = gp.vida(*caso, cfg_lobos=plano())
        modelo = p.cerebro.modelo_mundo
        assert set(modelo.arvores_vistas()) == set(m.troncos_vistos) and modelo.arvores_vistas()
    modelo = cerebro().modelo_mundo
    jx, jy = lugar("J1")
    modelo.decisao(obs_de(pc(), pm(jx, jy, troncos=[("J1", 0, 0, 0)] + [(n, x - jx, y - jy, 0) for n, x, y in mm.lugares_do_layout(CM)
                                                                          if n not in ("J1", mm.COMEDOURO)
                                                                          and mm.dentro(x - jx, y - jy, modelo.raio_visao)])))
    with pytest.raises(RuntimeError, match="troncos"):
        modelo.decisao(obs_de(pc(), pm(0, 0, troncos=[("J1", jx, jy, 0)])))
    with pytest.raises(RuntimeError, match="layout"):
        modelo.decisao(obs_de(pc(), pm(jx, jy, troncos=[("J1", 1, 0, 1)])))


def test_g_sem_credito_a_fruta_na_mao_so_ensina_o_desfecho():
    c = cerebro()
    c.modelo_mundo.decisao(obs_de(pc(), pm(0, 0)))
    antes = json.loads(json.dumps(c.estado_interno(), sort_keys=True, default=repr))
    c.fruta_na_mao("b", obs_de(pc(fome=500, humor=900), pm(0, 0)), obs_de(pc(fome=567, humor=950), pm(0, 0)))
    depois = json.loads(json.dumps(c.estado_interno(), sort_keys=True, default=repr))
    pa, pd_ = antes.pop("plano"), depois.pop("plano")
    assert antes == depois                                                      # nenhum peso, motivo ou aprendizado do A
    dm = pd_["modelo_mundo"]
    assert dm["consumos_mao"]["b"] == 1 and dm["consumos"]["b"] == 0
    passo = CONFIG_MODELO_MUNDO_LIGADA.passo_desfecho
    assert dm["desfecho"]["b"] == [div_arred(67 * passo, S), 0, 0, div_arred(50 * passo, S), 0] != pa["modelo_mundo"]["desfecho"]["b"]
    sem = PoliticaLobos(CONFIG_PADRAO, gp.P1_PLANO, cfg_mundo=CM, cfg_corpo=CQ)                  # sem o plano: nada
    e0 = json.dumps(sem.estado_interno(), sort_keys=True, default=repr)
    sem.fruta_na_mao("b", obs_de(pc(fome=500), pm(0, 0)), obs_de(pc(fome=567), pm(0, 0)))
    assert json.dumps(sem.estado_interno(), sort_keys=True, default=repr) == e0


def test_na_vida_a_mao_chega_aos_modelos_e_nao_aos_pesos():
    m, p, mudanca = gp.vida("padrao", "quimica", "P1-plano-motivo", "comedouro", 101, cfg_lobos=plano())
    x, _ = gp.xy_do_caso("comedouro", 101)
    modelo = p.interna.cerebro.modelo_mundo
    assert modelo.consumos_mao[x] == gp.N_MAO and sum(modelo.consumos_mao.values()) == gp.N_MAO


def test_o_congelamento_pp8():
    """o mapa congelado (P1-plan-desfecho) e os dois modelos congelados (P1-plan-cong): depois do congelar, nada daquela parte muda"""
    for partes in (("mapa",), ("desfecho", "mapa")):
        c = cerebro()
        modelo = c.modelo_mundo
        jx, jy = lugar("J1")
        modelo.decisao(obs_de(pc(), pm(jx, jy)))
        modelo.congelar(*partes)
        foto = json.loads(json.dumps(modelo.para_dict()))
        c2x, c2y = lugar("M6")
        modelo.decisao(obs_de(pc(fome=500), pm(c2x, c2y, vistos=[(1, "c", 0, 0, 0)])))
        modelo.consequencia(AcaoPet.COMER, {"comeu": {"tipo": "c", "situacao": "madura"}}, obs_de(pc(fome=600, energia=990), pm(c2x + 60, c2y)))
        modelo.na_mao("a", obs_de(pc(fome=500), pm(0, 0)), obs_de(pc(fome=567), pm(0, 0)))
        agora = modelo.para_dict()
        assert agora["mapa"] == foto["mapa"] and agora["lugares_vistos"] == foto["lugares_vistos"]
        if "desfecho" in partes:
            assert agora["desfecho"] == foto["desfecho"] and agora["andar"] == foto["andar"] and agora["ignoradas"]["desfecho"] == 3
        else:
            assert agora["desfecho"] != foto["desfecho"] and agora["andar"] != foto["andar"]
        assert agora["ignoradas"]["mapa"] >= 2
    with pytest.raises(ValueError):
        cerebro().modelo_mundo.congelar("planejador")
