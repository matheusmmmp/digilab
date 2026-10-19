"""O adendo 8 do J5 (docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, A8.3 a A8.9; PJ8-1 a PJ8-6): o evento do mundo que para as arvores de um tipo,
a bancada (a x sai das arvores no T1 em T_m; no T2, a busca pelas arvores, sem o corte), o piloto e a validacao apontando as faixas novas,
SEM rodar (so as sementes dos testes).

O que se confere:
- G2: sem a chave `adendo_8`, as vidas do adendo 7 e as do adendo 5 saem iguais aos gabaritos gravados antes (commits proprios);
- o mundo: `parar_arvores` para as arvores do tipo, retira as frutas caidas delas (e so elas: a fruta da regra fica), as quedas seguintes
  nao poem nada e o fluxo `mundo-arvores` anda igual; o evento no log, o replay e as recusas;
- a busca nova em dados com a resposta conhecida;
- a config: a chave e as recusas (sem o adendo 7, as bases de cada fase, a 53101 nao volta);
- a vida com o adendo 8: no T1, as arvores da x param em T_m, nenhuma x de arvore e comida depois e o G1; no T2, as buscas e o m
  recontados do replay, sem o corte;
- o piloto e a validacao do adendo 8: as configs, as recusas e as fumacas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_pqp_adendo7 as gab7  # noqa: E402
import gabarito_pqp_ao_lado as gab5  # noqa: E402
from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_piloto_pet_que_pensa_adendo7 as pa  # noqa: E402
from experiments import run_v2_validacao_pet_que_pensa as vp  # noqa: E402
from digilab.config import CONFIG_MUNDO_LIGADA  # noqa: E402
from digilab.events import ACOES_PARAR_ARVORES, AcaoUsuario, parar_arvores, tipo_parado  # noqa: E402
from digilab.metrics import busca_arvores  # noqa: E402
from digilab.mundo import Mundo, PetQuePensaSemChave  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


_VIDAS: dict = {}


def _vida(braco="P1", protocolo="T1", semente=101):
    chave = (braco, protocolo, semente)
    if chave not in _VIDAS:
        cfg = {**gab7.config(), "adendo_8": True, "bracos": [braco], "protocolos": [protocolo], "sementes": [semente]}
        if not bv.BRACOS_PQP[braco].planejador:
            del cfg["g_plano"]
        bp = bv.bancada_pqp_da_config(cfg)
        v = bp.vida(bv.EspecPQP(braco, protocolo, semente))
        _VIDAS[chave] = (bp, v, bp.medir(v))
    return _VIDAS[chave]


# ------------------------------------------------------------------ 1. G2


def test_g2_sem_o_adendo_8_as_vidas_sao_as_dos_gabaritos():
    g7 = json.loads((RAIZ / "tests" / "gabaritos" / "pqp_adendo7_vidas.json").read_text(encoding="utf-8"))
    g5 = json.loads((RAIZ / "tests" / "gabaritos" / "pqp_ao_lado_vidas.json").read_text(encoding="utf-8"))
    assert gab7.vidas() == g7 and gab7.vidas({**gab7.config(), "adendo_8": False}) == g7
    assert gab5.vidas() == g5


# ------------------------------------------------------------------ 2. o mundo


def _mundo_ate(tick: int) -> Mundo:
    m = Mundo(CONFIG_MUNDO_LIGADA, 7)
    m.ligar_trocas()
    m.atualizar(tick)
    return m


def test_o_enum_e_as_funcoes_do_evento():
    assert [tipo_parado(a) for a in ACOES_PARAR_ARVORES] == ["a", "b", "c"]
    assert parar_arvores("b") is AcaoUsuario.PARAR_ARVORES_B
    with pytest.raises(ValueError):
        parar_arvores("d")
    with pytest.raises(ValueError):
        tipo_parado(AcaoUsuario.TAPA)


def test_parar_arvores_retira_as_caidas_e_as_quedas_seguintes_nao_poem_nada():
    tick = 6 * 60 * 24
    m = _mundo_ate(tick)
    arv_a = {a["id"] for a in m.arvores if a["fruta"] == "a"}
    regra = m.nova_comida("a", 10, 10, tick, "dono_ao_lado")                  # a fruta da regra nunca sai
    caidas = {c["id"] for c in m.comidas.values() if c["origem"] in arv_a}
    assert caidas, "o teste precisa de uma fruta caida de uma arvore do tipo"
    reg = m.parar_arvores("a", tick)
    assert reg["arvores"] == sorted(arv_a) and set(reg["retiradas"]) == caidas
    assert regra["id"] in m.comidas and not any(c["origem"] in arv_a for c in m.comidas.values())
    # o fluxo das quedas anda igual ao de um mundo sem a parada; so nada cai das arvores paradas
    gemeo = _mundo_ate(tick)
    m.atualizar(tick + 3 * 1440)
    gemeo.atualizar(tick + 3 * 1440)
    assert m.rng_arvores.getstate() == gemeo.rng_arvores.getstate()
    depois = [q for q in m.quedas if q["tick"] > tick]
    assert depois and all(q["colocadas"] == [] for q in depois if q["arvore"] in arv_a)
    assert any(q["colocadas"] for q in depois if q["arvore"] not in arv_a)
    assert m.resumo()["paradas_arvores"] == [reg] and "paradas_arvores" not in gemeo.resumo()


def test_parar_arvores_falha_alto():
    m = Mundo(CONFIG_MUNDO_LIGADA, 7)
    m.atualizar(100)
    with pytest.raises(PetQuePensaSemChave):
        m.parar_arvores("a", 100)
    m.ligar_trocas()
    with pytest.raises(ValueError):
        m.parar_arvores("d", 100)
    with pytest.raises(RuntimeError):
        m.parar_arvores("a", 99)


# ------------------------------------------------------------------ 3. a busca nova, em dados


def test_a_busca_pelas_arvores():
    velhas, novas = {"J1", "M1"}, {"J2"}
    arv = lambda i: {"tipo": f"arvore:{i}", "fruta": None, "arvore": i}  # noqa: E731
    fruta = lambda f: {"tipo": "comida", "fruta": f, "arvore": None}  # noqa: E731
    assert busca_arvores([], arv("J2"), None, "a", velhas, novas) == (True, True, False)
    assert busca_arvores(["a"], arv("J1"), None, "a", velhas, novas) == (True, False, True)            # com a x a vista conta
    assert busca_arvores(["a"], fruta("a"), "J2", "a", velhas, novas) == (True, True, True)            # a x caida de uma nova
    assert busca_arvores(["a"], fruta("a"), "dono_ao_lado", "a", velhas, novas) == (False, False, False)   # a da regra nao
    assert busca_arvores(["b"], fruta("b"), "J2", "a", velhas, novas) == (False, False, False)         # outra fruta nao
    assert busca_arvores([], arv("J3"), None, "a", velhas, novas) == (False, False, False)
    assert busca_arvores([], None, None, "a", velhas, novas) == (False, False, False)
    with pytest.raises(ValueError):
        busca_arvores([], arv("J1"), None, "a", velhas, velhas)


# ------------------------------------------------------------------ 4. a config


def test_as_recusas_da_config():
    base = {**gab7.config(), "bracos": ["P1"], "protocolos": ["T1"]}
    del base["g_plano"]
    with pytest.raises(ValueError, match="bool"):
        bv.validar_config_pqp({**base, "adendo_8": 1})
    with pytest.raises(ValueError, match="adendo 7"):
        bv.validar_config_pqp({**base, "adendo_7": False, "adendo_8": True})
    pil = pa.config_do_piloto(_cfg("piloto_adendo8"))
    bv.validar_config_pqp(pil)
    bv.validar_config_pqp({**pil, "unidades": {**pil["unidades"], "bases": list(bv.BASES_PQP_ADENDO8["validacao"])}})
    for bases in (bv.BASES_PQP_ADENDO7["piloto"], bv.BASES_PQP_ADENDO7["validacao"], bv.BASES_PQP_AO_LADO):
        with pytest.raises(bv.SementeSemPlano, match="A8.9"):
            bv.validar_config_pqp({**pil, "unidades": {**pil["unidades"], "bases": list(bases)}})
    with pytest.raises(bv.SementeSemPlano):
        bv.validar_config_pqp({k: v for k, v in pil.items() if k != "adendo_8"})
    with pytest.raises(ValueError, match="so no T1"):
        bv.RegraMudancaPQP("T2", "a", "b", 7, 2, True)


# ------------------------------------------------------------------ 5. a vida com o adendo 8


@pytest.mark.parametrize("braco", ["P1", "P1-plan"])
def test_no_t1_as_arvores_da_x_param_em_t_m(braco):
    _bp, v, m = _vida(braco, "T1")
    p = v.motor.mundo.paradas_arvores
    assert len(p) == 1 and p[0]["tick"] == v.tick_mudanca and p[0]["tipo"] == v.x
    assert m["adendo_8"]["parada"]["retiradas"] == len(p[0]["retiradas"])
    arv_x = set(p[0]["arvores"])
    assert not any(c["tipo"] == v.x and c["origem"] in arv_x and c["tick"] > v.tick_mudanca for c in v.motor.consumos_mundo)
    assert not any(q["colocadas"] for q in v.motor.mundo.quedas if q["arvore"] in arv_x and q["tick"] > v.tick_mudanca)
    assert any(f["tick"] > v.tick_mudanca for f in v.motor.frutas_ao_lado)               # a regra continua no T1
    assert m["adendo_7"]["sem_oportunidade"]["origem_do_corte"] != "arvore"


def test_no_t2_nada_para_e_a_busca_e_recontada_sem_o_corte():
    bp, v, m = _vida("P1", "T2", 404)
    assert v.motor.mundo.paradas_arvores is None
    regs: list = []

    def fp(cfg=None):
        r = bv._RegistroPQP(bp.politica(v.espec, cfg), bp.bancada.cfg_mundo, bp.cfg_modelo, True, True, True, True)
        regs.append(r)
        return r
    bp.rejogar(v.motor.log, v.espec, fp, lambda mt: setattr(regs[-1], "motor", mt))
    arv = bv._arvores_do_layout(bp.bancada.cfg_mundo)
    velhas = {i for i, (_a, _b, f) in arv.items() if f == v.x}
    novas = {i for i, (_a, _b, f) in arv.items() if f == v.y}
    exposicao = m["t2"]["exposicao"]
    contagem = {"antes_com_x": 0, "antes_sem_x": 0, "depois_com_x": 0, "depois_sem_x": 0}
    for d in regs[-1].decisoes:
        if d["tick"] == exposicao:
            continue
        busca, _nova, com_x = busca_arvores(d["maduros"], d["alvo"], d["alvo"]["origem"] if d["alvo"] else None, v.x, velhas, novas)
        if busca and (not d["depois"] or exposicao is not None):
            contagem[("depois" if d["depois"] else "antes") + ("_com_x" if com_x else "_sem_x")] += 1
    assert m["t2"]["buscas"] == contagem and sum(contagem.values()) > 0
    assert m["t2"]["corte_reexperiencia"] is None                                      # PJ8-3: sem o corte
    assert m["adendo_8"]["x_de_arvore_nova_comidas"] >= 0


# ------------------------------------------------------------------ 6. o piloto e a validacao


def test_a_config_do_piloto_do_adendo_8():
    c = pa.validar(_cfg("piloto_adendo8"))
    p7 = _cfg("piloto_adendo7")
    assert c["unidades"] == {"bases": list(bv.BASES_PQP_ADENDO8["piloto"]), "k": 4, "prefixo": "pet_que_pensa"}
    assert c["adendo_8"] is True and pa.chave(c) == "piloto_adendo8" and c["piloto_adendo8"] == p7["piloto_adendo7"]
    iguais = set(p7) - {"descricao", "unidades", "piloto_adendo7"}
    assert {k: c[k] for k in iguais} == {k: p7[k] for k in iguais}
    with pytest.raises(ValueError, match="e so ela"):
        pa.validar({**c, "piloto_adendo7": c["piloto_adendo8"]})
    with pytest.raises(bv.SementeSemPlano, match="A8.9"):
        pa.validar({**c, "unidades": {**c["unidades"], "bases": list(bv.BASES_PQP_ADENDO7["piloto"])}})


def test_a_fumaca_do_piloto_do_adendo_8(tmp_path):
    cfg = _cfg("fumaca_piloto_adendo8")
    rv = pa.rodar_reval(cfg, tmp_path / "p")
    if not rv["passa"]:
        (tmp_path / "p" / "reval.json").write_text(json.dumps({**rv, "passa": True}), encoding="utf-8")   # so na fumaca
    r = pa.rodar_piloto(cfg, tmp_path / "p")
    assert r["regras"]["limiar_aprendeu"] == bv.LIMIAR_ACASO_MEDIO
    medidas = json.loads((tmp_path / "p" / "piloto" / "P1" / "medidas.json").read_text(encoding="utf-8"))
    assert all("adendo_8" in m for m in medidas.values())


def test_a_validacao_do_adendo_8(tmp_path):
    f = vp.validar(_cfg("fumaca_validacao_adendo8"))
    assert f["adendo_8"] and f["validacao"]["limiar_aprendeu"] == bv.LIMIAR_ACASO_MEDIO
    r = vp.rodar(f, tmp_path / "v")
    assert set(r["primarios"]) == {"G-T1", "G-T2"}
