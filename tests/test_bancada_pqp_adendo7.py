"""O adendo 7 do J5 (docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, A7.2 a A7.8; PJ7-1 a PJ7-6): a bancada, as medidas novas, o orquestrador do
piloto e a validacao apontando as faixas novas, SEM rodar (so as sementes dos testes).

O que se confere:
- G2: sem a chave `adendo_7`, as vidas e as medidas da fruta ao lado (o adendo 5) saem iguais ao gabarito gravado antes
  (tests/gabaritos/pqp_ao_lado_vidas.json, commit proprio);
- as medidas novas em dados com a resposta conhecida (a oportunidade com qualquer alternativa ao lado, os alvos para o acaso 1/k e a
  busca sem a fome);
- a config: a chave e as recusas (sem a fruta ao lado, as bases de cada fase, a janela de 5 dias nas sementes do plano);
- a vida com o adendo 7: a fruta ao lado para em T_m no T2 e continua no T1, o G1, e o T1, o acaso e o T2 recontados do replay;
- a G-APRENDEU pelo acaso medio do braco;
- o orquestrador do piloto (os numeros do adendo 6, as recusas, a fumaca dos dois passos) e a validacao do adendo 7 (as bases, o piloto
  refeito, o limiar e a fumaca).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_pqp_ao_lado as gab  # noqa: E402
from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa as cpq  # noqa: E402
from experiments import run_v2_piloto_pet_que_pensa_adendo7 as pa  # noqa: E402
from experiments import run_v2_validacao_pet_que_pensa as vp  # noqa: E402
from digilab.metrics import alvos_ao_lado, busca_transicao, oportunidade_ao_lado  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa"
DIA = 1440


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


_VIDAS: dict = {}


def _vida(braco="P1", protocolo="T1", semente=101):
    chave = (braco, protocolo, semente)
    if chave not in _VIDAS:
        cfg = {**gab.config(), "adendo_7": True, "janela": 3, "bracos": [braco], "protocolos": [protocolo], "sementes": [semente]}
        if not bv.BRACOS_PQP[braco].planejador:
            del cfg["g_plano"]
        bp = bv.bancada_pqp_da_config(cfg)
        v = bp.vida(bv.EspecPQP(braco, protocolo, semente))
        _VIDAS[chave] = (bp, v, bp.medir(v))
    return _VIDAS[chave]


# ------------------------------------------------------------------ 1. G2


def test_g2_sem_o_adendo_7_as_vidas_sao_as_do_gabarito():
    gravado = json.loads((RAIZ / "tests" / "gabaritos" / "pqp_ao_lado_vidas.json").read_text(encoding="utf-8"))
    assert gab.vidas() == gravado
    assert gab.vidas({**gab.config(), "adendo_7": False}) == gravado


# ------------------------------------------------------------------ 2. as medidas novas, em dados


def test_a_oportunidade_com_qualquer_alternativa_ao_lado():
    regra = {7, 8, 9}                                   # a, b e c postas pela regra; o 5 e uma "a" de arvore
    assert oportunidade_ao_lado("comer", {1: "racao", 7: "a"}, regra, 7, "a") == (True, True)
    assert oportunidade_ao_lado("comer", {7: "a", 8: "b"}, regra, 7, "a") == (True, True)          # sem a racao, outra fruta ao lado
    assert oportunidade_ao_lado("comer", {7: "a", 8: "b"}, regra, 8, "a") == (True, False)
    assert oportunidade_ao_lado("comer", {7: "a", 5: "a"}, regra, 7, "a") == (False, False)       # a outra "a" nao e alternativa ao lado
    assert oportunidade_ao_lado("comer", {7: "a", 5: "b"}, regra, 7, "a") == (False, False)       # uma "b" de arvore tambem nao
    assert oportunidade_ao_lado("comer", {1: "racao", 5: "a"}, regra, 5, "a") == (False, False)   # a x de arvore nao e a da regra
    assert oportunidade_ao_lado("explorar", {1: "racao", 7: "a"}, regra, 7, "a") == (False, False)
    assert alvos_ao_lado({1: "racao", 2: "racao", 7: "a", 8: "b", 9: "c"}, regra) == 4             # as racoes sao um alvo
    assert alvos_ao_lado({7: "a", 8: "b", 5: "c"}, regra) == 2                                     # a "c" de arvore nao conta
    assert alvos_ao_lado({1: "racao", 9: "c"}, regra) == 2


def test_a_busca_sem_a_fome():
    velhas, novas = {"J1"}, {"J2"}
    arv = {"tipo": "arvore:J2", "fruta": None, "arvore": "J2"}
    assert busca_transicao(900, [], arv, "a", velhas, novas, 512) == (False, False)                 # com o limite, a fome alta nao busca
    assert busca_transicao(900, [], arv, "a", velhas, novas, None) == (True, True)                  # sem ele, busca
    assert busca_transicao(900, ["a"], arv, "a", velhas, novas, None) == (False, False)             # a x a vista continua fora


# ------------------------------------------------------------------ 3. a config


def test_as_recusas_da_config():
    base = {**gab.config(), "bracos": ["P1"], "protocolos": ["T1"]}
    del base["g_plano"]
    with pytest.raises(ValueError, match="bool"):
        bv.validar_config_pqp({**base, "adendo_7": 1})
    with pytest.raises(ValueError, match="fruta ao lado"):
        bv.validar_config_pqp({**base, "fruta_ao_lado": False, "adendo_7": True})
    pil = pa.config_do_piloto(_cfg("piloto_adendo7"))
    bv.validar_config_pqp(pil)
    bv.validar_config_pqp({**pil, "unidades": {**pil["unidades"], "bases": list(bv.BASES_PQP_ADENDO7["validacao"])}})
    for bases in (bv.BASES_PET_QUE_PENSA["validacao"], bv.BASES_PQP_AO_LADO, bv.BASES_PQP_PALADAR):     # nenhuma faixa velha volta
        with pytest.raises(bv.SementeSemPlano, match="A7.8"):
            bv.validar_config_pqp({**pil, "unidades": {**pil["unidades"], "bases": list(bases)}})
    with pytest.raises(bv.SementeSemPlano):                                                       # as novas so com o adendo 7
        bv.validar_config_pqp({k: v for k, v in pil.items() if k != "adendo_7"})
    with pytest.raises(ValueError, match="janela de 5"):
        bv.validar_config_pqp({**pil, "janela": 3})


# ------------------------------------------------------------------ 4. a vida com o adendo 7


def test_a_fruta_ao_lado_para_em_t_m_no_t2_e_continua_no_t1():
    _bp, v2, _m2 = _vida("P1", "T2")
    assert v2.tick_mudanca is not None and v2.motor.frutas_ao_lado
    assert all(f["tick"] < v2.tick_mudanca for f in v2.motor.frutas_ao_lado)
    _bp, v1, _m1 = _vida("P1", "T1")
    assert any(f["tick"] > v1.tick_mudanca for f in v1.motor.frutas_ao_lado)
    with pytest.raises(ValueError, match="so do T2"):
        bv.FrutaAoLadoAteMudanca(None, bv.RegraMudancaPQP("T1", "a", None, 7, 2))


def test_a_regra_da_mudanca_dispara_igual_ao_acoes():
    r = bv.RegraMudancaPQP("T2", "a", "b", 1, 2)
    cedo = {"tick": DIA + 8 * 60 - 15, "dormindo": False}
    dormindo = {"tick": DIA + 8 * 60, "dormindo": True}
    hora = {"tick": DIA + 8 * 60, "dormindo": False}
    assert not r.dispara(cedo) and r.acoes(cedo) == []
    assert not r.dispara(dormindo) and r.acoes(dormindo) == []
    assert r.dispara(hora) and r.acoes(hora) and r.tick == hora["tick"]
    assert not r.dispara({"tick": hora["tick"] + 15, "dormindo": False})                           # uma vez so


def _registro(bp, v):
    regs: list = []

    def fp(cfg=None):
        r = bv._RegistroPQP(bp.politica(v.espec, cfg), bp.bancada.cfg_mundo, bp.cfg_modelo, True, True, True)
        regs.append(r)
        return r
    bp.rejogar(v.motor.log, v.espec, fp, lambda mt: setattr(regs[-1], "motor", mt))
    return regs[-1]


def test_o_t1_e_o_acaso_recontados_do_replay():
    bp, v, m = _vida("P1-plan", "T1", 202)
    reg = _registro(bp, v)
    linhas, ks = [], []
    for d in reg.decisoes:
        op, esc = oportunidade_ao_lado(d["acao"], d["maduros_id"], d["ids_ao_lado"], None if d["alvo"] is None else d["alvo"]["id"], v.x)
        linhas.append({"tick": d["tick"], "depois": d["depois"], "conta": op, "sucesso": esc, "reexperiencia": d["comeu"] == v.x})
        if op and not d["depois"]:
            ks.append(alvos_ao_lado(d["maduros_id"], d["ids_ao_lado"]))
    esperado = bv.mudanca_de_escolha(linhas, bv.N_OPORTUNIDADES_PQP, v.tick_mudanca)
    assert {k: m["t1"][k] for k in esperado} == esperado
    assert m["t1"]["acaso_antes"] == [1 / k for k in ks[-bv.N_OPORTUNIDADES_PQP:]] and ks
    a7 = m["adendo_7"]
    assert a7["acaso_medio_antes"] == sum(m["t1"]["acaso_antes"]) / len(m["t1"]["acaso_antes"])
    assert a7["sem_oportunidade"]["motivo"] in (None, "sem antes", "corte", "janela")
    if a7["corte"]["tick"] is not None:
        assert a7["corte"]["origem"] in ("regra", "arvore", "achou e comeu")
        assert a7["corte"]["latencia_corte"] == a7["corte"]["tick"] - v.tick_mudanca


def test_o_t2_recontado_do_replay_sem_a_fome():
    bp, v, m = _vida("P1", "T2", 202)
    reg = _registro(bp, v)
    arv = bv._arvores_do_layout(bp.bancada.cfg_mundo)
    velhas = {i for i, (_a, _b, f) in arv.items() if f == v.x}
    novas = {i for i, (_a, _b, f) in arv.items() if f == v.y}
    buscas = [busca_transicao(d["fome"], d["maduros"], d["alvo"], v.x, velhas, novas, None)[0] for d in reg.decisoes]
    com_fome = [busca_transicao(d["fome"], d["maduros"], d["alvo"], v.x, velhas, novas, bp.cfg_modelo.escala // 2)[0]
                for d in reg.decisoes]
    assert sum(buscas) >= sum(com_fome)
    pd = m["adendo_7"]["t2_depois_por_dia"]
    assert len(pd) == bp.dias_da_vida("T2")
    assert sum(r["velhas"] + r["novas"] for r in pd) == sum(1 for d in reg.decisoes if d["depois"] and d["alvo"] is not None
                                                          and d["alvo"]["arvore"] in velhas | novas)


# ------------------------------------------------------------------ 5. a G-APRENDEU pelo acaso medio


def test_a_g_aprendeu_pelo_acaso_medio():
    por = {(b, p): {} for b in bv.BRACOS_PQP for p in ("T1", "T2")}
    for b in bv.BRACOS_PQP:
        acaso = [1 / 4, 1 / 4, 1 / 4] if b == "P1" else [1 / 2, 1 / 2, 1 / 2]
        for s in range(4):
            por[(b, "T1")][s] = {"t1": {"f_antes": 0.4, "sem_oportunidade": False, "acaso_antes": acaso}}
            por[(b, "T2")][s] = {"t2": {"sem_oportunidade": False, "sem_exposicao": False}}
    assert cpq.acaso_medio(por, "P1") == 0.25 and cpq.acaso_medio(por, "P1-plan") == 0.5
    pr = cpq.premissas(por, cpq.BOOTSTRAP_PILOTO, bv.LIMIAR_ACASO_MEDIO)["G-APRENDEU"]
    assert pr["P1"]["passa"] and pr["P1"]["limiar"] == 0.25                                        # 0,4 passa de 1/4
    assert not pr["P1-plan"]["passa"] and pr["P1-plan"]["limiar"] == 0.5                           # e nao de 1/2


# ------------------------------------------------------------------ 6. o orquestrador do piloto e a validacao


def test_a_config_do_piloto_e_a_do_adendo():
    c = pa.validar(_cfg("piloto_adendo7"))
    cal = _cfg("calibracao_ao_lado")
    assert c["unidades"] == {"bases": list(bv.BASES_PQP_ADENDO7["piloto"]), "k": 4, "prefixo": "pet_que_pensa"}
    assert (c["d_a"], c["janela"], c["adendo_7"], c["consequencia"]["ganho_gosto"], c["g_plano"]) == (7, 5, True, 512, 1024)
    assert pa.conferir_adendo6(c) == {"ganho_gosto": 512, "g_plano": 1024}
    iguais = set(cal) - {"descricao", "unidades", "calibracao_ganho_gosto", "calibracao_g_plano", "janela", "consequencia"}
    assert {k: c[k] for k in iguais} == {k: cal[k] for k in iguais}
    with pytest.raises(ValueError, match="adendo 6"):
        pa.validar({**c, "g_plano": 512})
    with pytest.raises(bv.SementeSemPlano):
        pa.validar({**c, "unidades": {**c["unidades"], "bases": list(bv.BASES_PQP_ADENDO7["validacao"])}})
    with pytest.raises(ValueError, match="bracos"):
        pa.validar({**c, "bracos": ["P1"]})


def test_a_fumaca_do_piloto(tmp_path):
    cfg = _cfg("fumaca_piloto_adendo7")
    with pytest.raises(FileNotFoundError, match="reval"):
        pa.rodar_piloto(cfg, tmp_path / "p")
    rv = pa.rodar_reval(cfg, tmp_path / "p")
    if not rv["passa"]:
        (tmp_path / "p" / "reval.json").write_text(json.dumps({**rv, "passa": True}), encoding="utf-8")   # so na fumaca
    r = pa.rodar_piloto(cfg, tmp_path / "p")
    assert r["regras"]["limiar_aprendeu"] == bv.LIMIAR_ACASO_MEDIO and r["g_plano"] == cfg["g_plano"]
    for b, g in r["premissas"]["G-APRENDEU"].items():
        assert "limiar" in g and g["passa"] == (g["ic"] is not None and g["limiar"] is not None and g["ic"]["ic_inferior"] > g["limiar"])
    medidas = json.loads((tmp_path / "p" / "piloto" / "P1" / "medidas.json").read_text(encoding="utf-8"))
    assert all("adendo_7" in m for m in medidas.values())
    with pytest.raises(FileExistsError):
        pa.rodar_piloto(cfg, tmp_path / "p")


def test_a_validacao_do_adendo_7():
    f = vp.validar(_cfg("fumaca_validacao_adendo7"))
    assert f["adendo_7"] and f["validacao"]["limiar_aprendeu"] == bv.LIMIAR_ACASO_MEDIO
    with pytest.raises(ValueError, match="acaso medio"):
        vp.validar({**f, "validacao": {**f["validacao"], "limiar_aprendeu": 0.25}})
    cal = _cfg("validacao_ao_lado")                         # a do adendo 5 continua valida e nao aceita o 'piloto'
    vp.validar(cal)
    with pytest.raises(ValueError, match="piloto"):
        vp.validar({**cal, "validacao": {**cal["validacao"], "piloto": "x"}})
    a7 = {**cal, "adendo_7": True, "janela": 5, "validacao": {**cal["validacao"], "limiar_aprendeu": bv.LIMIAR_ACASO_MEDIO}}
    with pytest.raises(ValueError, match="piloto"):                                                # sem o piloto refeito
        vp.validar(a7)


def test_a_fumaca_da_validacao_do_adendo_7(tmp_path):
    cfg = _cfg("fumaca_validacao_adendo7")
    r = vp.rodar(cfg, tmp_path / "v")
    assert set(r["primarios"]) == {"G-T1", "G-T2"}
    assert all("limiar" in g for g in r["premissas"]["G-APRENDEU"].values())
