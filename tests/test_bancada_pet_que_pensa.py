"""V2, W-BANCADA-PQP: a bancada do pet que pensa (J5; docs/TAREFA_V2_PET_QUE_PENSA.md, etapa 4; docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, secoes 2
a 4, 7 e 8), so com as sementes dos testes.

O que se confere:
- as faixas 45101...45505 e 46101...46505 com a fonte, o prefixo `pet_que_pensa` e as bases das duas fases;
- a fruta x e a y da unidade pelas rngs proprias (uniformes, sem tocar o `random` global) e os efeitos (a x faz bem; no T1, depois, mal);
- os bracos: o P1 roda; os tres com o planejador falham alto com o no (NOS_PENDENTES["planejador"]) e, sem o no, com a fiacao do g_plano;
- a regra da mudanca (o primeiro passo do dono a partir das 8 h do dia D_a com o pet acordado) e o motor da mudanca: no T1 a primeira fruta
  na mao troca o efeito da x e as duas maos entram no log fora do orcamento; no T2 a troca de tipo; na fase 1, nada;
- o G1 de toda vida pelo texto do log; um log mexido falha alto;
- o G-SEM-CREDITO (o cerebro igual antes e depois de cada mao) e a mao no modelo do desfecho;
- o congelamento (PP-8): as partes congeladas iguais do tick da mudanca ao fim, a vida igual com e sem o congelamento (os modelos nao
  decidem com g_plano 0), e o gate falha alto se o modelo congelado mudar;
- as medidas da secao 4 (a oportunidade do T1, a busca e a exposicao do T2, o corte da reexperiencia, q e m) em dados com a resposta
  conhecida;
- a config: as recusas (o plano, as bases, a montagem, o corpo do passo 0, os bracos com o planejador) e a fumaca inteira pelo rodar_pqp.
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
from digilab.config import CONFIG_DONOS, CONFIG_FRUTAS_LIGADA, CONFIG_PADRAO, CONFIG_PQP_MUNDO_LIGADA, TICKS_POR_DIA  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.events import FRUTAS, LogDeEventos  # noqa: E402
from digilab.metrics import busca_transicao, exposto_transicao, mudanca_de_escolha, oportunidade_revalorizacao  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

FUMACA = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "fumaca.json"
CURTA = {"d_a": 2, "janela": 1}                 # as vidas curtas dos testes de mecanismo


def _cfg(**troca) -> dict:
    return {**json.loads(FUMACA.read_text(encoding="utf-8")), **troca}


_CACHE: dict = {}


def _bp(**troca) -> bv.BancadaPQP:
    return bv.bancada_pqp_da_config(_cfg(**{**CURTA, **troca}))


def _vida(braco: str, protocolo: str, semente: int = 101):
    chave = (braco, protocolo, semente)
    if chave not in _CACHE:
        _CACHE[chave] = _bp().vida(bv.EspecPQP(braco, protocolo, semente))
    return _CACHE[chave]


# ------------------------------------------------------------------ 1. as faixas e o prefixo


def test_as_faixas_do_j5_reservadas_com_fonte():
    faixas = {(lo, hi): fonte for lo, hi, fonte in bv.FAIXAS_RESERVADAS}
    for (lo, hi), uso in {(45101, 45505): "calibracao do g_plano e piloto", (46101, 46505): "validacao"}.items():
        assert "PLANO_ANALISE_V2_PET_QUE_PENSA" in faixas[(lo, hi)] and "PP-9" in faixas[(lo, hi)] and uso in faixas[(lo, hi)]
    for fase, bases in bv.BASES_PET_QUE_PENSA.items():
        assert bases == tuple(b + 101 * i for b in ((45101,) if fase == "calibracao" else (46101,)) for i in range(5))
        assert all("pet que pensa" in bv.na_faixa_reservada(b) for b in bases)
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))
    assert not any(q_lo <= 46505 and 45101 <= q_hi for q_lo, q_hi, _ in bv.FAIXAS_QUEIMADAS)


def test_o_prefixo_do_j5_segue_a_regra():
    assert bv.PREFIXO_PQP == "pet_que_pensa" and "pet_que_pensa" in bv.PREFIXOS_UNIDADES
    u = bv.unidades_derivadas(bv.BASES_PET_QUE_PENSA["validacao"], 4, "pet_que_pensa")[5]
    assert (u["base"], u["k"]) == (46202, 1)
    assert u["semente"] == derivar_semente("pet_que_pensa", 46202, 1) and u["genoma"] == derivar_semente("pet_que_pensa-genoma", 46202, 1)


# ------------------------------------------------------------------ 2. a unidade: a x, a y e os efeitos


def test_x_e_y_pelas_rngs_proprias():
    estado = random.getstate()
    xs = [bv.fruta_x_pqp(s) for s in range(600)]
    ys = [bv.fruta_y_pqp(s) for s in range(600)]
    assert random.getstate() == estado                                      # nao toca o random global
    assert all(x != y for x, y in zip(xs, ys))
    for f in FRUTAS:
        assert 150 < xs.count(f) < 250 and 150 < ys.count(f) < 250
    s = 4242
    assert bv.fruta_x_pqp(s) == FRUTAS[random.Random(derivar_semente("pet-que-pensa-x", s)).randrange(3)]
    outras = [f for f in FRUTAS if f != bv.fruta_x_pqp(s)]
    assert bv.fruta_y_pqp(s) == outras[random.Random(derivar_semente("pet-que-pensa-y", s)).randrange(2)]


def test_os_efeitos_da_unidade():
    cf = CONFIG_FRUTAS_LIGADA
    antes, depois = bv.efeitos_pqp("b", cf), bv.efeitos_pqp("b", cf, faz_mal=True)
    assert antes == {"a": cf.efeito_humor_neutro, "b": -cf.efeito_humor_ruim, "c": cf.efeito_humor_neutro} and antes["b"] > 0
    assert depois == {**antes, "b": cf.efeito_humor_ruim} and depois["b"] < 0


# ------------------------------------------------------------------ 3. os bracos


def test_os_bracos_do_plano():
    assert set(bv.BRACOS_PQP) == {"P1", "P1-plan", "P1-plan-desfecho", "P1-plan-cong"}
    assert not bv.BRACOS_PQP["P1"].planejador and bv.BRACOS_PQP["P1"].congela == ()
    assert bv.BRACOS_PQP["P1-plan"].congela == () and bv.BRACOS_PQP["P1-plan-desfecho"].congela == ("mapa",)
    assert set(bv.BRACOS_PQP["P1-plan-cong"].congela) == {"mapa", "desfecho"}
    assert bv.braco_pqp("P1") is bv.BRACOS_PQP["P1"]
    with pytest.raises(KeyError):
        bv.braco_pqp("P2")


@pytest.mark.parametrize("braco", ["P1-plan", "P1-plan-desfecho", "P1-plan-cong"])
def test_os_bracos_com_o_planejador_falham_alto(braco, monkeypatch):
    assert "planejador" in bv.NOS_PENDENTES
    with pytest.raises(NotImplementedError, match="etapa 2"):
        bv.braco_pqp(braco)
    with pytest.raises(NotImplementedError, match="etapa 2"):
        _bp().vida(bv.EspecPQP(braco, "T1", 101))
    with pytest.raises(NotImplementedError, match="etapa 2"):
        bv.validar_config_pqp(_cfg(bracos=["P1", braco]))
    # sem o no, o braco ainda nao vira o P1 em silencio: o g_plano entra com o planejador
    monkeypatch.setattr(bv, "NOS_PENDENTES", {})
    with pytest.raises(NotImplementedError, match="g_plano"):
        _bp().politica(bv.EspecPQP(braco, "T1", 101))


def test_o_cerebro_do_p1():
    p = _bp().politica(bv.EspecPQP("P1", "T1", 101))
    m = p.cerebro
    assert isinstance(m, bv.PoliticaComModeloPQP) and m.congela == ()
    cl = m._interna.cl
    assert cl.alvo_aprendido and cl.presenca_fruta_mundo and cl.alvo_por_arvore and cl.aprendizado_ligado
    assert p.braco.fonte == "consequencia"
    corpo = _bp().cfg_corpo()
    assert corpo.metabolismo and corpo.digestao and corpo.vida and not corpo.drives_novos and not corpo.gestos


# ------------------------------------------------------------------ 4. a mudanca


def test_a_regra_da_mudanca():
    limiar = 2 * TICKS_POR_DIA + bv.HORA_MUDANCA_PQP
    r = bv.RegraMudancaPQP("T1", "b", None, 2, 2)
    assert r.acoes({"tick": limiar - 90, "dormindo": False}) == []
    assert r.acoes({"tick": limiar, "dormindo": True}) == []                  # dormindo: espera o pet acordar
    acoes = r.acoes({"tick": limiar + 90, "dormindo": False})
    assert [a.value for a in acoes] == ["dar_fruta_b", "dar_fruta_b"] and r.tick == limiar + 90
    assert r.acoes({"tick": limiar + 180, "dormindo": False}) == []           # uma vez so
    r2 = bv.RegraMudancaPQP("T2", "c", "a", 2, 2)
    assert [a.value for a in r2.acoes({"tick": limiar, "dormindo": False})] == ["trocar_arvores_a_c"]
    assert bv.RegraMudancaPQP("fase1", "a", None, 2, 2).acoes({"tick": limiar, "dormindo": False}) == []
    with pytest.raises(ValueError):
        bv.RegraMudancaPQP("T2", "a", "a", 2, 2)
    with pytest.raises(ValueError):
        bv.RegraMudancaPQP("T3", "a", None, 2, 2)


def test_o_t1_troca_o_efeito_na_primeira_mao():
    v = _vida("P1", "T1")
    m = v.motor
    limiar = 2 * TICKS_POR_DIA + bv.HORA_MUDANCA_PQP
    assert v.tick_mudanca >= limiar and v.tick_mudanca % CONFIG_DONOS.passo_ticks == 0
    assert m.mudanca == {"tick": v.tick_mudanca, "evento": f"dar_fruta_{v.x}"}
    assert m.revaloracao["tick"] == v.tick_mudanca and m.revaloracao["antes"][v.x] > 0 > m.revaloracao["depois"][v.x]
    assert m.efeito_frutas == bv.efeitos_pqp(v.x, CONFIG_FRUTAS_LIGADA, faz_mal=True)
    maos = [c for c in m.consumos_mundo if c.get("como") == "mao"]
    assert len(maos) == 2 and all(c["tick"] == v.tick_mudanca and c["tipo"] == v.x for c in maos)
    assert all(c["humor_depois"] - c["humor_antes"] <= 0 for c in maos)     # a mao ja vem com o efeito ruim
    assert v.dono + v.retirados == _bp().bancada.orcamento_por_dia() * 3     # a mudanca fica fora do orcamento
    assert m.mundo.trocas_tipo == []


def test_o_t2_troca_o_tipo_das_arvores():
    v = _vida("P1", "T2")
    m = v.motor
    assert v.eventos_mudanca == [f"trocar_arvores_{min(v.x, v.y)}_{max(v.x, v.y)}"]
    assert m.mudanca["tick"] == v.tick_mudanca and m.revaloracao is None
    (t,) = m.mundo.trocas_tipo
    assert t["tick"] == v.tick_mudanca and {t["x"], t["y"]} == {v.x, v.y}
    arvores = bv._arvores_do_layout(_bp().bancada.cfg_mundo)
    assert {i: a["fruta"] for i, a in ((a["id"], a) for a in m.mundo.arvores)} == {
        i: (v.y if f == v.x else v.x if f == v.y else f) for i, (_x, _y, f) in arvores.items()}


def test_a_fase_1_nao_muda_nada():
    v = _vida("P1", "fase1")
    assert v.tick_mudanca is None and v.eventos_mudanca == [] and v.motor.mudanca is None
    assert v.motor.log.para_jsonl().count("dar_fruta") == 0 and v.motor._estado.tick == 2 * TICKS_POR_DIA


def test_o_motor_da_mudanca_recusa():
    bp = _bp()
    espec = bv.EspecPQP("P1", "T1", 101)
    kw = dict(obediencia_desligada=True, cfg_mundo=bp.bancada.cfg_mundo, efeito_frutas=bv.efeitos_pqp("a", CONFIG_FRUTAS_LIGADA),
              cfg_corpo=bp.cfg_corpo())
    classe = bv.com_corpo(bv.MotorMundoMudanca)
    with pytest.raises(ValueError, match="juntos"):
        classe(bp.politica(espec, CONFIG_PADRAO), CONFIG_PADRAO, 101, NEUTRO, "brasa", cfg_pqp=CONFIG_PQP_MUNDO_LIGADA, revaloriza="a", **kw)
    with pytest.raises(ValueError, match="J5"):
        classe(bp.politica(espec, CONFIG_PADRAO), CONFIG_PADRAO, 101, NEUTRO, "brasa", **kw)
    m = _vida("P1", "T1").motor
    with pytest.raises(ValueError, match="T1"):
        m._aplicar_acao_usuario(bv.dar_fruta("a" if m.revaloriza != "a" else "b"))


# ------------------------------------------------------------------ 5. o G1


@pytest.mark.parametrize("protocolo", ["T1", "T2", "fase1"])
def test_g1_pelo_texto_do_log(protocolo):
    v = _vida("P1", protocolo, 202)
    texto = v.motor.log.para_jsonl()
    _bp().conferir_replay(v, texto)
    interno = json.loads(bv._interno(v.motor))
    assert interno["modelo_mundo"]["k"] > 0                                 # os modelos entram no G1
    linhas = texto.splitlines()
    mexido = [ln for ln in linhas if "dar_fruta" not in ln and "trocar_arvores" not in ln]
    if mexido != linhas:
        with pytest.raises(bv.ReplayDivergiu):
            _bp().conferir_replay(v, "\n".join(mexido) + "\n")


# ------------------------------------------------------------------ 6. o G-SEM-CREDITO, a mao no modelo e o congelamento


def test_g_sem_credito_e_a_mao_no_desfecho():
    v = _vida("P1", "T1")
    med = _bp().medir(v)
    assert med["g_sem_credito"] == {"maos": 2, "violacoes": 0} and med["maos_no_modelo"] == 2
    ultimo = med["modelos_por_dia"][-1]
    ih = ultimo["receptores"].index("humor")
    assert ultimo["desfecho"][v.x][ih] < 0                                   # o modelo aprendeu o mal da x pela mao


def _congelado(congela):
    return {**bv.BRACOS_PQP, "P1-teste": bv.BracoPQP("P1-teste", False, congela)}


@pytest.mark.parametrize("congela", [("mapa",), ("mapa", "desfecho")])
def test_o_congelamento_pp8(congela, monkeypatch):
    monkeypatch.setattr(bv, "BRACOS_PQP", _congelado(congela))
    bp = _bp()
    base = _vida("P1", "T1", 303)
    v = bp.vida(bv.EspecPQP("P1-teste", "T1", 303))
    # com g_plano 0 os modelos nao decidem: a vida e a mesma, fora os modelos no estado interno
    assert bv.resumo_motor(v.motor) == bv.resumo_motor(base.motor)
    sem = lambda m: {k: x for k, x in json.loads(bv._interno(m)).items() if k != "modelo_mundo"}  # noqa: E731
    assert sem(v.motor) == sem(base.motor)
    med = bp.medir(v)
    assert med["congelamento"] == {"tick": v.tick_mudanca, "partes": list(congela), "conferido": True}
    assert med["maos_no_modelo"] == (0 if "desfecho" in congela else 2)
    modelo = v.motor.politica._pm.cerebro
    retrato = {k: json.loads(x) for k, x in modelo.retrato_congelamento.items()}
    fim = med["modelos_por_dia"][-1]
    assert fim["mapa"] == retrato["mapa"]["mapa"]                             # o mapa e o do tick da mudanca
    fim_base = bp.medir(base)["modelos_por_dia"][-1]
    if "desfecho" in congela:
        assert fim["desfecho"] == retrato["desfecho"]["desfecho"]             # o desfecho tambem, e a mao nao chegou a ele
    else:
        assert fim["desfecho"] == fim_base["desfecho"]                       # o desfecho aprende como no P1, a mao incluida
    # mexer no modelo congelado depois faz o gate falhar alto
    modelo.modelo.mapa[next(iter(modelo.modelo.mapa))][0] += 1
    with pytest.raises(RuntimeError, match="congelamento"):
        modelo.congelamento_conferido()


def test_o_congelamento_recusa():
    with pytest.raises(ValueError):
        bv.PoliticaComModeloPQP(None, _bp().bancada.cfg_mundo, None, ("mapa", "mapa"))
    with pytest.raises(ValueError):
        bv.PoliticaComModeloPQP(None, _bp().bancada.cfg_mundo, None, ("habito",))


# ------------------------------------------------------------------ 7. as medidas da secao 4, em dados com a resposta conhecida


def test_a_oportunidade_do_t1():
    S2 = 512
    troncos = {"J1": "a", "J2": "b"}
    assert oportunidade_revalorizacao(400, [], troncos, {"tipo": "arvore:J2", "fruta": None, "arvore": "J2"}, "b", S2) == (True, True)
    assert oportunidade_revalorizacao(400, [], troncos, {"tipo": "arvore:J1", "fruta": None, "arvore": "J1"}, "b", S2) == (True, False)
    assert oportunidade_revalorizacao(400, ["b", "racao"], {}, {"tipo": "comida", "fruta": "b", "arvore": None}, "b", S2) == (True, True)
    assert oportunidade_revalorizacao(400, ["b", "racao"], {}, None, "b", S2) == (True, False)          # ocioso: nao escolheu
    assert oportunidade_revalorizacao(600, ["b", "racao"], {}, None, "b", S2) == (False, False)        # sem fome
    assert oportunidade_revalorizacao(400, ["b"], {"J2": "b"}, None, "b", S2) == (False, False)        # sem alternativa
    assert oportunidade_revalorizacao(400, ["racao"], {"J1": "a"}, None, "b", S2) == (False, False)    # sem x disponivel
    assert oportunidade_revalorizacao(512, ["b", "a"], {}, {"tipo": "comida", "fruta": "a", "arvore": None}, "b", S2) == (True, False)


def test_a_busca_e_a_exposicao_do_t2():
    S2, velhas, novas = 512, {"J1", "M1"}, {"J3", "M3"}
    arv = lambda i: {"tipo": f"arvore:{i}", "fruta": None, "arvore": i}  # noqa: E731
    assert busca_transicao(300, [], arv("J3"), "a", velhas, novas, S2) == (True, True)
    assert busca_transicao(300, [], arv("M1"), "a", velhas, novas, S2) == (True, False)
    assert busca_transicao(300, ["a"], arv("J3"), "a", velhas, novas, S2) == (False, False)          # a x a vista
    assert busca_transicao(300, [], arv("J2"), "a", velhas, novas, S2) == (False, False)             # outra arvore
    assert busca_transicao(700, [], arv("J3"), "a", velhas, novas, S2) == (False, False)
    assert busca_transicao(300, [], {"tipo": "vagar", "fruta": None, "arvore": None}, "a", velhas, novas, S2) == (False, False)
    with pytest.raises(ValueError):
        busca_transicao(300, [], arv("J3"), "a", velhas, velhas, S2)
    novas_pos = [(100, 100)]
    assert exposto_transicao(50, 50, [(7, "a", 40, 40, 57)], novas_pos, "a", 32)              # a 14 da nova
    assert not exposto_transicao(50, 50, [(7, "a", 0, 0, 0)], novas_pos, "a", 32)             # longe
    assert not exposto_transicao(50, 50, [(7, "a_podre", 40, 40, 57)], novas_pos, "a", 32)    # podre nao conta
    assert not exposto_transicao(50, 50, [(7, "b", 40, 40, 57)], novas_pos, "a", 32)


def _ln(t, depois, conta, sucesso, reexp=False):
    return {"tick": t, "depois": depois, "conta": conta, "sucesso": sucesso, "reexperiencia": reexp}


def test_a_mudanca_de_escolha_com_o_corte():
    linhas = [_ln(10, False, True, False), _ln(20, False, True, True), _ln(30, False, False, False), _ln(40, False, True, True),
              _ln(50, False, True, True),
              _ln(100, True, False, False), _ln(110, True, True, False), _ln(120, True, True, True, reexp=True),
              _ln(130, True, True, False), _ln(140, True, True, False)]
    r = mudanca_de_escolha(linhas, 3, 90)
    assert r["n_antes"] == 3 and r["f_antes"] == 1.0                         # as 3 ultimas antes: 20, 40, 50
    assert r["n_depois"] == 2 and r["f_depois"] == 0.5                       # 110 e 120 (a do corte conta); 130 e 140 nao
    assert r["queda"] == 0.5 and r["subida"] == -0.5 and r["nivel"] == 0.5 and r["corte_reexperiencia"] == 120
    assert r["latencia"] == 20 and r["oportunidades_depois_ate_corte"] == 2 and not r["sem_oportunidade"]
    # o corte numa decisao que nao conta tambem corta
    r = mudanca_de_escolha([_ln(10, False, True, True), _ln(100, True, False, False, reexp=True), _ln(110, True, True, False)], 3, 90)
    assert r["sem_oportunidade"] and r["n_depois"] == 0 and r["queda"] is None and r["corte_reexperiencia"] == 100
    # mais de n depois: as n primeiras
    r = mudanca_de_escolha([_ln(10, False, True, False)] + [_ln(100 + i, True, True, i < 3) for i in range(6)], 3, 90)
    assert r["n_depois"] == 3 and r["f_depois"] == 1.0 and r["subida"] == 1.0 and r["oportunidades_depois_ate_corte"] == 6
    with pytest.raises(ValueError):
        mudanca_de_escolha([_ln(100, True, True, True), _ln(110, False, True, True)], 3, 90)
    with pytest.raises(ValueError):
        mudanca_de_escolha([_ln(100, False, True, True), _ln(90, False, True, True)], 3, 90)


def test_as_medidas_de_uma_vida():
    v = _vida("P1", "T2")
    med = _bp().medir(v)
    t2 = med["t2"]
    arvores = bv._arvores_do_layout(_bp().bancada.cfg_mundo)
    assert set(t2["velhas"]) == {i for i, a in arvores.items() if a[2] == v.x} and set(t2["novas"]) == {i for i, a in arvores.items()
                                                                                                        if a[2] == v.y}
    assert t2["m"] == t2["subida"] and (t2["exposicao"] is None) == t2["sem_exposicao"]
    assert med["desempenho"]["d_fe_janela"] is not None and med["custo"]["bytes_log_por_dia"] > 0
    assert [r["dia"] for r in med["modelos_por_dia"]] == [1, 2, 3]
    assert "planejador" in med["nao_medidos"]["quanto_o_plano_decide"]
    med1 = _bp().medir(_vida("P1", "T1"))
    assert med1["t1"]["q"] == med1["t1"]["queda"] and "t2" not in med1


# ------------------------------------------------------------------ 8. a config e a fumaca


def test_a_config_recusa():
    bv.validar_config_pqp(_cfg())
    with pytest.raises(bv.SementeSemPlano):
        bv.validar_config_pqp(_cfg(sementes=[45101]))
    plano = {"plano": bv.PLANO_PQP, "montagem": "completa"}
    sem_sementes = {k: v for k, v in _cfg().items() if k != "sementes"}
    with pytest.raises(bv.SementeSemPlano):                                  # bases fora das faixas do plano
        bv.validar_config_pqp({**sem_sementes, **plano, "unidades": {"bases": [31101], "k": 1, "prefixo": "pet_que_pensa"}})
    with pytest.raises(bv.SementeSemPlano):                                  # as duas fases misturadas
        bv.validar_config_pqp({**sem_sementes, **plano, "unidades": {"bases": [45101, 46101], "k": 1, "prefixo": "pet_que_pensa"}})
    with pytest.raises(ValueError, match="prefixo"):
        bv.validar_config_pqp({**sem_sementes, "unidades": {"bases": [101], "k": 1, "prefixo": "mundo"}})
    cal = {**sem_sementes, **plano, "unidades": {"bases": list(bv.BASES_PET_QUE_PENSA["calibracao"]), "k": 4, "prefixo": "pet_que_pensa"}}
    with pytest.raises(ValueError, match="passo 0"):
        bv.validar_config_pqp(cal)
    p0 = "artifacts_v2_corpo/calibracao/passo0/passo0.json"
    corpo = json.loads((RAIZ / p0).read_text(encoding="utf-8"))["escolha"]["corpo"]
    assert bv.validar_config_pqp({**cal, "passo0": p0, "corpo": corpo})
    with pytest.raises(ValueError, match="passo 0"):
        bv.validar_config_pqp({**cal, "passo0": p0, "corpo": {**corpo, "gasto_basal_acordado": 1}})
    with pytest.raises(ValueError, match="completa"):
        bv.validar_config_pqp({**cal, "montagem": "simples", "passo0": p0, "corpo": corpo})
    with pytest.raises(ValueError, match="protocolos"):
        bv.validar_config_pqp(_cfg(protocolos=["T3"]))
    with pytest.raises(ValueError, match="sobram"):
        bv.validar_config_pqp(_cfg(g_plano=256))


def test_a_fumaca_inteira(tmp_path):
    cfg = _cfg(sementes=[101], protocolos=["T1", "T2"], **CURTA)
    r = bv.rodar_pqp(cfg, tmp_path / "j5")
    assert set(r["vidas"]) == {"P1~T1@101", "P1~T2@101"}
    for nome, v in r["vidas"].items():
        texto = (tmp_path / "j5" / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8")
        assert texto == v.motor.log.para_jsonl()
    medidas = json.loads((tmp_path / "j5" / "medidas.json").read_text(encoding="utf-8"))
    assert set(medidas) == set(r["vidas"]) and "t1" in medidas["P1~T1@101"] and "t2" in medidas["P1~T2@101"]
    meta = json.loads((tmp_path / "j5" / "meta.json").read_text(encoding="utf-8"))
    assert meta["plano"] == bv.PLANO_PQP and meta["modelo_mundo_sha256"] and meta["mundo_sha256"] and meta["d_a"] == 2
    assert meta["cfg_corpo"]["metabolismo"] is True
    with pytest.raises(FileExistsError):
        bv.rodar_pqp(cfg, tmp_path / "j5")
    assert bv.main(["--config", str(FUMACA), "--saida", str(tmp_path / "main")]) == 0
    assert len(list((tmp_path / "main" / "vidas").glob("*.jsonl"))) == 6     # P1 x T1, T2, fase 1 x 101, 202


def test_o_log_rejogado_tem_a_mudanca():
    v = _vida("P1", "T1", 202)
    log = LogDeEventos.de_jsonl(v.motor.log.para_jsonl())
    r = _bp().rejogar(log, v.espec)
    assert r.mudanca == v.motor.mudanca and r.revaloracao == v.motor.revaloracao
    assert replace(v.espec, protocolo="T1") == v.espec
