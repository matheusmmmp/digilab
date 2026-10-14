"""V2, W-BANCADA-REDE: a etapa 3 da rede de si na bancada (docs/TAREFA_V2_REDE_DE_SI.md, etapa 3; docs/PLANO_ANALISE_V2_REDE_DE_SI.md,
secoes 3 e 4), com a rede (etapas 1 e 2, #264) na main.

O que se confere:
- a chave `rede_de_si` da config: a ConfigRedeDeSi ligada (com campos por cima), recusada desligada e em braco sem corpo;
- G-OBS pela bancada: a vida com a rede e a vida sem ela, byte a byte (o resumo do motor e o estado interno do cerebro);
- G1-REDE: o replay refaz o estado da rede bit a bit, e uma rede mexida falha alto;
- a rede refeita das leituras (o replay da bancada): as mesmas previsoes e os mesmos pesos; congelada no tick 0 e a persistencia; o
  oraculo com entradas nulas e a propria rede (o mesmo LMS);
- as linhas de base e o Brier skill em dados com a resposta conhecida;
- as sondas do cerebro (o pedido e o "ao nascer") lidas do motivo e nunca entregues a rede; os quimicos so no oraculo;
- o P1+ped-c monta (o corpo e o pedido juntos); o P1-c-lenta falha alto com o no da troca da digestao;
- a adaptacao numa troca forcada; o `rodar` com a chave (as medidas e o meta).
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

import bancada_v2 as bv  # noqa: E402
from digilab import metrics  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA, CONFIG_REDE_DE_SI_LIGADA  # noqa: E402
from digilab.policies.lobos import REGRAS_PEDIDO  # noqa: E402
from digilab.rede_de_si import CONTEXTO, PoliticaComRede  # noqa: E402

SONDA = {"estados": 5, "amostras": 5, "semente": 101}
CC_CANAIS = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)


def _bancada(rede=True, dias=2, **kw):
    lobos = bv.cfg_lobos_do_ponto("T3", {"memoria_ganho": 512, "w0_info": 256, "w0_pedido": 256})
    return bv.Bancada(dias, 16 * dias, cfg_lobos=lobos, montagem="completa", cfg_consequencia=CC_CANAIS,
                      cfg_rede=CONFIG_REDE_DE_SI_LIGADA if rede else None, **kw)


def _vida(banc, braco="P1-c", mundo="bola", semente=101, dono="atencioso"):
    return banc.vida(bv.EspecVida(dono=dono, braco=braco, semente=semente, mundo=mundo))


def _medir(banc, v):
    """o replay de medicao com as pecas da rede a mao (o medir inteiro mede tambem o resto)"""
    return banc.medir(v, SONDA)["rede_de_si"]


_CACHE: dict = {}


def _vida_medida(braco, mundo, semente=101):
    chave = (braco, mundo, semente)
    if chave not in _CACHE:
        banc = _bancada()
        v = _vida(banc, braco, mundo, semente)
        _CACHE[chave] = (banc, v, _medir(banc, v))
    return _CACHE[chave]


# ------------------------------------------------------------------ 1. a chave da config


def _cfg(**kw):
    c = {"dias": 2, "orcamento": 32, "donos": ["atencioso"], "bracos": ["P1-c"], "mundos": ["bola"], "sementes": [101],
         "sonda": SONDA, "bootstrap": {"reamostragens": 50, "semente": 1, "nivel": 0.95}, "rede_de_si": {}}
    c.update(kw)
    return c


def test_a_chave_liga_a_rede_com_os_campos_por_cima():
    assert bv.bancada_da_config(_cfg()).cfg_rede == CONFIG_REDE_DE_SI_LIGADA
    b = bv.bancada_da_config(_cfg(rede_de_si={"passo": 16, "horizontes": [1, 4]}))
    assert b.cfg_rede == replace(CONFIG_REDE_DE_SI_LIGADA, passo=16, horizontes=(1, 4))
    sem = _cfg()
    del sem["rede_de_si"]
    assert bv.bancada_da_config(sem).cfg_rede is None
    assert "rede_de_si" in bv.CHAVES_CONFIG


@pytest.mark.parametrize("valor", [{"ligada": False}, [], None, {"passo": -1}])
def test_a_chave_recusa_desligar_e_campo_ruim(valor):
    with pytest.raises((ValueError, TypeError)):
        bv.validar_config(_cfg(rede_de_si=valor))


@pytest.mark.parametrize("braco", ["P1", "P0-hoje", "P3"])
def test_a_rede_le_o_corpo_braco_sem_corpo_falha_alto(braco):
    with pytest.raises(ValueError, match="receptores do corpo"):
        bv.validar_config(_cfg(bracos=["P1-c", braco]))


def test_sem_a_chave_a_politica_nao_ganha_a_rede():
    esp = bv.EspecVida(dono="atencioso", braco="P1-c", semente=101, mundo="bola")
    assert not isinstance(_bancada(rede=False).politica(esp), PoliticaComRede)
    p = _bancada().politica(esp)
    assert isinstance(p, PoliticaComRede) and bv.do_braco(p) is p._interna


# ------------------------------------------------------------------ 2. G-OBS e G1-REDE pela bancada


@pytest.mark.parametrize("braco,mundo", [("P1-c", "bola"), ("P0-c", "bola"), ("P1-c-tapa", "bola"), ("P1+ped-c", "iguais_frutas")])
def test_g_obs_a_vida_com_a_rede_e_a_vida_sem_ela(braco, mundo):
    com = _vida(_bancada(), braco, mundo)
    sem = _vida(_bancada(rede=False), braco, mundo)
    assert bv.resumo_motor(com.motor) == bv.resumo_motor(sem.motor)
    assert bv._interno(com.motor) == bv._interno(sem.motor)
    assert bv.rede_de(com.motor.politica).rede.k == len(bv.do_braco(com.motor.politica).cerebro.motivos) > 0


def test_g1_rede_o_replay_refaz_a_rede_e_a_mexida_falha_alto():
    banc = _bancada()
    v = _vida(banc)
    banc.conferir_replay(v)                                          # do texto do log, com a rede (G1-REDE)
    rede = bv.rede_de(v.motor.politica).rede
    rede.pesos_corpo["4"][rede.receptores[0]][0] += 1
    with pytest.raises(bv.ReplayDivergiu, match="G1-REDE"):
        banc.conferir_replay(v)


# ------------------------------------------------------------------ 3. a rede refeita, a congelada e o oraculo


def test_a_rede_refeita_das_leituras_e_a_rede():
    banc = _bancada()
    v = _vida(banc)
    rede = bv.rede_de(v.motor.politica).rede
    ref = bv.rede_offline(rede.cfg, rede.registros, list(rede.receptores))
    for n in rede.horizontes:
        assert ref["corpo"][str(n)] == [r["corpo"][str(n)] for r in rede.registros]
    assert ref["autoria"] == [r["autoria"] for r in rede.registros]
    assert ref["pesos_corpo"] == rede.pesos_corpo and ref["pesos_autoria"] == rede.pesos_autoria
    # congelada no tick 0, a rede e o prior: a persistencia, exata
    cong = bv.rede_offline(rede.cfg, rede.registros, list(rede.receptores), congelar_k=0)
    for n in rede.horizontes:
        assert cong["corpo"][str(n)] == [r["leituras"] for r in rede.registros]
    # congelada no meio: igual ate a primeira atualizacao que ela pula (k + n), diferente depois
    k = len(rede.registros) // 2
    meio = bv.rede_offline(rede.cfg, rede.registros, list(rede.receptores), congelar_k=k)
    assert meio["corpo"]["1"][:k] == ref["corpo"]["1"][:k] and meio["corpo"]["1"][k:] != ref["corpo"]["1"][k:]
    # o oraculo com entradas nulas e a propria rede: o mesmo LMS (a entrada 0 nao pesa nem aprende)
    nulo = bv.rede_offline(rede.cfg, rede.registros, list(rede.receptores), extra=[[0, 0, 0]] * len(rede.registros), autoria=False)
    assert all(nulo["corpo"][str(n)] == ref["corpo"][str(n)] for n in rede.horizontes)


def test_o_gate_da_reproducao_falha_alto_com_um_registro_mexido():
    banc, v, _ = _vida_medida("P1-c", "bola")
    rede = bv.rede_de(v.motor.politica).rede
    regs = json.loads(json.dumps(rede.registros))
    regs[10]["corpo"]["4"][0] += 1
    falsa = type("R", (), {})()
    falsa.__dict__.update(rede.__dict__)
    falsa.registros = regs
    falsa.n_pesos = rede.n_pesos
    with pytest.raises(bv.ReplayDivergiu, match="n = 4"):
        bv.Bancada.medidas_rede(banc, falsa, [[0]] * len(regs), _cerebro_motivos(v), v.motor.log)


def _cerebro_motivos(v):
    return bv.do_braco(v.motor.politica).cerebro.motivos


def test_os_quimicos_vao_so_ao_oraculo():
    banc, v, med = _vida_medida("P1-c", "bola")
    rede = bv.rede_de(v.motor.politica).rede
    assert med["quimicos_do_oraculo"] == len(v.motor.corpo.quimicos) > len(rede.receptores)
    assert all(set(r) == {"k", "acao", "leituras", "contexto", "faixa", "corpo", "autoria", "autoria_sem_pedido", "autoria_ao_nascer",
                          "surpresa"} for r in rede.registros)
    assert med["mae"]["4"]["oraculo"]["n"] == med["mae"]["4"]["rede"]["n"] > 0


# ------------------------------------------------------------------ 4. as linhas de base e o Brier, com a resposta conhecida


def test_media_historica_so_com_o_passado():
    assert metrics.media_historica([[1, 10], [2, 10], [4, 11], [1, 10]]) == [[1, 10], [2, 10], [2, 10], [2, 10]]
    assert metrics.media_historica([]) == []
    with pytest.raises(ValueError):
        metrics.media_historica([[1, 2], [3]])


def test_mae_previsao_conta_a_mao():
    leituras = [[0, 100, 0], [10, 100, 0], [20, 90, 0], [30, 80, 5]]
    rec = ["fome", "higiene", "susto"]
    pers = metrics.previsao_persistencia(leituras)
    # n = 1, k em {0, 1, 2}: erros fome 10, 10, 10; higiene 0, 10, 10; susto 0, 0, 5
    r = metrics.mae_previsao(leituras, pers, 1, range(4), rec)
    assert r["n"] == 3 and r["mae"] == (30 + 20) / 6
    assert r["por_receptor"] == {"fome": 10.0, "higiene": 20 / 3, "susto": 5 / 3}
    assert metrics.mae_previsao(leituras, pers, 1, range(4), rec, so=("fome",))["mae"] == 10.0
    # n = 2: so k em {0, 1}
    assert metrics.mae_previsao(leituras, pers, 2, range(4), rec)["n"] == 2
    assert metrics.mae_previsao(leituras, pers, 5, range(4), rec) == {"mae": None, "n": 0,
                                                                         "por_receptor": {"fome": None, "higiene": None, "susto": None}}
    perfeita = [leituras[k + 1] for k in range(3)] + [[0, 0, 0]]
    assert metrics.mae_previsao(leituras, perfeita, 1, range(4), rec)["mae"] == 0.0


def test_brier_skill_com_a_resposta_conhecida():
    ev = [1, 0] * 15
    assert metrics.brier_skill([float(e) for e in ev], ev)["bss"] == 1.0                 # perfeita
    assert metrics.brier_skill([0.5] * 30, ev)["bss"] == 0.0                              # a taxa-base
    r = metrics.brier_skill([1.0 - e for e in ev], ev)
    assert r["bss"] == pytest.approx(-3.0) and r["brier_base"] == 0.25                    # o contrario: Brier 1
    assert metrics.brier_skill([0.5] * 19, [1, 0] * 9 + [1])["fora"] == "menos de 20 decisoes"
    assert metrics.brier_skill([0.3] * 25, [1] * 25)["bss"] is None                       # a base sem variancia


def test_brier_skill_multiclasse_com_a_resposta_conhecida():
    cands = ["a", "b"]
    dec = [(cands, {"a": 3.0, "b": 0.0}, "a")] * 10 + [(cands, {"a": 0.0, "b": 5.0}, "b")] * 10
    r = metrics.brier_skill_multiclasse(dec)
    assert r["bss"] == 1.0 and r["frequencias"] == {"a": 0.5, "b": 0.5} and r["brier_base"] == 0.5
    # a previsao igual a base (uniforme): skill 0; a base restrita aos candidatos de cada decisao
    assert metrics.brier_skill_multiclasse([(cands, {"a": 1, "b": 1}, c) for _, _, c in dec])["bss"] == 0.0
    tres = [(["a", "b", "c"], {"a": 1, "b": 1, "c": 1}, "a")] * 10 + [(["a"], {"a": 1}, "a")] * 10
    assert metrics.brier_skill_multiclasse(tres)["bss"] is None                            # so a classe a: sem variancia
    with pytest.raises(ValueError):
        metrics.brier_skill_multiclasse([(cands, {}, "c")] * 20)


# ------------------------------------------------------------------ 5. a autoria: as sondas do cerebro, lidas do motivo


def test_a_autoria_do_pedido_e_ao_nascer_pelas_sondas_do_cerebro():
    banc, v, med = _vida_medida("P1+ped-c", "iguais_frutas")
    rede = bv.rede_de(v.motor.politica).rede
    motivos = _cerebro_motivos(v)
    S = rede.S
    k0, k1 = med["janela_k"]
    esperadas = [k for k in range(k0, k1) if rede.registros[k]["contexto"][CONTEXTO.index("pedido")] == S
                 and motivos[k]["regra"] in REGRAS_PEDIDO and "comer" in motivos[k]["candidatos"]]
    assert esperadas and med["autoria"]["bss_ped"]["n"] == len(esperadas)
    eventos = sum((motivos[k]["pedido"]["acao_sem_pedido"] if "pedido" in motivos[k] else motivos[k]["acao"]) == "comer"
                  for k in esperadas)
    assert med["autoria"]["bss_ped"]["eventos"] == eventos
    assert sum(z["n"] for z in med["autoria"]["bss_ped_por_zona"].values()) == len(esperadas)
    assert med["autoria"]["bss_nasc"]["n"] == k1 - k0
    # a sonda "ao nascer" e a escolha pelo prior com o mesmo u (e, sem escolha, a propria acao)
    for m in motivos:
        s = bv.sonda_ao_nascer(m)
        assert s in m["candidatos"] and (m["u"] is not None or s == m["acao"])


def test_medir_nao_entrega_nada_a_rede():
    banc = _bancada()
    v = _vida(banc)
    antes = bv._estado_rede(v.motor)
    _medir(banc, v)
    assert bv._estado_rede(v.motor) == antes


# ------------------------------------------------------------------ 6. os bracos novos


def test_o_p1_ped_c_monta_o_corpo_e_o_pedido_juntos():
    banc, v, _ = _vida_medida("P1+ped-c", "iguais_frutas")
    b = bv.braco_de("P1+ped-c")
    assert (b.fonte, b.pedido, b.regime, b.gestos, b.metabolismo) == ("consequencia", True, "corpo", "sem_tapa", True)
    assert v.motor.corpo is not None and v.motor.cp.ligada and v.pedidos > 0 and v.motor.decisoes_com_pedido > 0
    cerebro = bv.do_braco(v.motor.politica).cerebro
    assert cerebro.estado_interno().get("peso_pedido") is not None
    banc.conferir_replay(v)


def test_o_p1_c_lenta_roda_com_a_troca_da_digestao():
    # a etapa 2b (o A) tirou o no: a troca da digestao no MotorCorpo (tests/test_troca_digestao.py confere o mecanismo)
    b = bv.BRACOS["P1-c-lenta"]
    assert b.digestao_lenta and b.regime == "corpo" and "digestao_lenta" not in bv.NOS_PENDENTES
    assert bv.braco_de("P1-c-lenta") is b
    bv.validar_config(_cfg(bracos=["P1-c-lenta"]))
    banc, v, med = _vida_medida("P1-c-lenta", "bola")
    assert v.motor.troca_digestao["tick"] == banc.tick_troca_digestao
    a = med["adaptacao"]
    assert a is not None and a["k_troca"] == banc.tick_troca_digestao // 15


def test_a_digestao_lenta_so_no_corpo(monkeypatch):
    monkeypatch.setattr(bv, "NOS_PENDENTES", {})
    monkeypatch.setitem(bv.BRACOS, "X", replace(bv.BRACOS["P1-c-lenta"], rotulo="X", regime="quimica"))
    with pytest.raises(ValueError, match="digestao lenta"):
        bv.braco_de("X")
    assert bv.braco_de("P1-c-lenta").digestao_lenta                 # sem o no, o braco existe


def test_a_adaptacao_numa_troca_forcada():
    banc, v, _ = _vida_medida("P1-c", "bola")
    rede = bv.rede_de(v.motor.politica).rede
    q = [[0] * 3] * len(rede.registros)
    # congelada no tick 0: a congelada e a persistencia, so na fome, nos ultimos quatro dias (aqui a vida inteira)
    a = banc.medidas_rede(rede, q, _cerebro_motivos(v), v.motor.log, tick_troca=0)["adaptacao"]
    leituras = [r["leituras"] for r in rede.registros]
    pers = metrics.mae_previsao(leituras, metrics.previsao_persistencia(leituras), 4, range(len(leituras)), list(rede.receptores),
                                so=("fome",))
    assert a["k_troca"] == 0 and a["congelada"] == pers["mae"] and a["d_adapta"] == a["congelada"] - a["rede"]
    assert len(a["curva_fome"]) == banc.dias
    b = banc.medidas_rede(rede, q, _cerebro_motivos(v), v.motor.log, tick_troca=bv.TICKS_POR_DIA)["adaptacao"]
    assert b["k_troca"] == bv.TICKS_POR_DIA // 15
    assert banc.tick_troca_digestao == banc.tick_troca


# ------------------------------------------------------------------ 7. as medidas e o rodar


def test_as_medidas_da_secao_4():
    _, v, med = _vida_medida("P1-c", "bola")
    rede = bv.rede_de(v.motor.politica).rede
    assert med["receptores"] == list(rede.receptores) and med["horizontes"] == [1, 4, 16] and med["horizonte_primario"] == 4
    assert med["decisoes"] == 2 * 96 and med["janela_k"] == [0, 192]       # vida de 2 dias: os ultimos 7 dias sao a vida inteira
    l4 = med["mae"]["4"]
    assert med["d_si"] == l4["persistencia"]["mae"] - l4["rede"]["mae"]
    assert med["d_media"] == l4["media"]["mae"] - l4["rede"]["mae"]
    assert "susto" in l4["rede"]["por_receptor"] and set(l4["rede_menos_persistencia_por_receptor"]) == set(rede.receptores)
    assert [c["dia"] for c in med["curva"]] == [1, 2] and len(med["pesos_por_dia"]) == 2
    assert med["n_pesos"] == 804 and med["adaptacao"] is None
    assert len(med["surpresa"]["por_hora"]) == 2 * 24


def test_rodar_com_a_chave(tmp_path):
    cfg = _cfg(bracos=["P1-c", "P0-c"], ponto="T3", montagem="completa", unidades={"bases": [101, 202], "k": 1, "prefixo": "rede_de_si"})
    del cfg["sementes"]
    bv.rodar(cfg, tmp_path / "s")
    medidas = json.loads((tmp_path / "s" / "medidas.json").read_text(encoding="utf-8"))
    vidas = list(medidas.values())
    assert len(vidas) == 4 and all(m["rede_de_si"]["decisoes"] == 192 for m in vidas)
    meta = json.loads((tmp_path / "s" / "meta.json").read_text(encoding="utf-8"))
    assert meta["cfg_rede"]["ligada"] and len(meta["rede_de_si_sha256"]) == 64


def test_sem_a_chave_nada_muda_nas_medidas_e_no_meta():
    banc = _bancada(rede=False)
    v = _vida(banc)
    assert banc.medir(v, SONDA)["rede_de_si"] is None
    sem = _cfg()
    del sem["rede_de_si"]
    m = bv.meta(sem)
    assert "cfg_rede" not in m and "rede_de_si_sha256" not in m


def test_as_fumacas_validam():
    for nome in ("fumaca.json", "fumaca_autoria.json"):
        cfg = json.loads((RAIZ / "experiments" / "configs" / "v2_rede_de_si" / nome).read_text(encoding="utf-8"))
        bv.validar_config(cfg)
        assert cfg["rede_de_si"] == {} and "P1-c-lenta" not in cfg["bracos"]


def test_com_os_orgaos_ligados_a_rede_falha_alto():
    # #299: com o Olfato e a Audicao, a rede le um receptor por narina e ouvido e passa do teto; a bancada do Digicorpo roda sem eles
    from digilab.corpo import todos_receptores_orgaos
    banc = _bancada()
    v = _vida(banc)
    assert not any(r.startswith(("olfato", "ouvido")) for r in bv.rede_de(v.motor.politica).rede.receptores)
    pol = banc.politica(bv.EspecVida(dono="atencioso", braco="P1-c", semente=101, mundo="bola"))
    assert isinstance(pol, bv.PoliticaComRedeSemOrgaos)

    class Corpo:
        pass
    pc = Corpo()
    for r in todos_receptores_orgaos():
        setattr(pc, r, None)
    pc.olfato_comida_esq = 10
    falsa = type("O", (), {"corpo": pc})()
    with pytest.raises(RuntimeError, match="orgaos ligados"):
        pol.agir(falsa, None)
    assert pol.rede.k == 0                                            # a rede nao viu a observacao
