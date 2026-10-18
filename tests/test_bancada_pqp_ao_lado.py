"""O J5 com a fruta ao lado da racao (adendo 5 de docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md; o lado do mundo e do dono e o #318 do A): a
bancada, as medidas novas e a calibracao montada, SEM rodar (so as sementes dos testes).

O que se confere:
- a faixa 51101...51505 reservada com a fonte e as unidades dela sem colisao;
- as medidas novas em dados com a resposta conhecida (`metrics.decisao_lado_a_lado` e `metrics.oportunidade_lado_a_lado`);
- a config: a chave `fruta_ao_lado` e as recusas (sem o paladar, fora do comedouro, as bases de cada fase);
- G2: desligada, a vida e as medidas sao as do paladar sem ela;
- a vida com a fruta ao lado: a regra do A em todos os bracos, o G1 (o replay do disco) e as medidas recontadas do motor (as postas, as
  comidas pela origem, as decisoes lado a lado e a oportunidade nova do T1);
- o orquestrador: a config do adendo, a G-APRENDEU a 1/4 no piloto e a fumaca dos quatro passos.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa as cpq  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa_paladar as cpp  # noqa: E402
from digilab.events import FRUTAS  # noqa: E402
from digilab.metrics import decisao_lado_a_lado, oportunidade_lado_a_lado  # noqa: E402
from digilab.mundo import ORIGEM_AO_LADO  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa"
S = 1024
DIA = 1440


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def _fumaca(**kw) -> dict:
    """a fumaca da bancada do J5 com o paladar e a fruta ao lado: as sementes dos testes, 2 dias de fase 1 e 1 de janela"""
    return {**_cfg("fumaca"), "paladar": True, "fruta_ao_lado": True,
            "consequencia": {"ganho": 4, "canais_ligados": True, "ganho_gosto": S}, **kw}


_VIDAS: dict = {}


def _vida(braco="P1", protocolo="T1", semente=101):
    chave = (braco, protocolo, semente)
    if chave not in _VIDAS:
        cfg = _fumaca(bracos=[braco], protocolos=[protocolo], sementes=[semente],
                      **({"g_plano": S} if bv.BRACOS_PQP[braco].planejador else {}))
        bp = bv.bancada_pqp_da_config(cfg)
        v = bp.vida(bv.EspecPQP(braco, protocolo, semente))
        _VIDAS[chave] = (bp, v, bp.medir(v))
    return _VIDAS[chave]


# ------------------------------------------------------------------ 1. a faixa


def test_a_faixa_da_fruta_ao_lado_reservada_com_fonte():
    fonte = {(lo, hi): f for lo, hi, f in bv.FAIXAS_RESERVADAS}[(51101, 51505)]
    assert "PLANO_ANALISE_V2_PET_QUE_PENSA" in fonte and "fruta ao lado" in fonte
    assert bv.BASES_PQP_AO_LADO == tuple(51101 + 101 * i for i in range(5))
    assert all("fruta ao lado" in bv.na_faixa_reservada(b) for b in bv.BASES_PQP_AO_LADO)
    assert not any(q_lo <= 51505 and 51101 <= q_hi for q_lo, q_hi, _ in bv.FAIXAS_QUEIMADAS)
    novas = bv.unidades_derivadas(bv.BASES_PQP_AO_LADO, 40, "pet_que_pensa")
    velhas = [u for fase in (*bv.BASES_PET_QUE_PENSA.values(), bv.BASES_PQP_PALADAR)
              for u in bv.unidades_derivadas(fase, 40, "pet_que_pensa")]
    a = {u["semente"] for u in novas} | {u["genoma"] for u in novas}
    b = {u["semente"] for u in velhas} | {u["genoma"] for u in velhas}
    assert len(a) == 2 * len(novas) and not a & b and not a & bv.SEMENTES_TESTE


# ------------------------------------------------------------------ 2. as medidas novas, em dados


def test_a_decisao_e_a_oportunidade_lado_a_lado():
    vistos = {1: "racao", 7: "a", 8: "b", 9: "a"}            # 7 e 8 sao da regra; a 9 e uma "a" de arvore
    regra = {7, 8}
    assert decisao_lado_a_lado("comer", vistos, regra)
    assert not decisao_lado_a_lado("explorar", vistos, regra)                    # so o comer (A5.3)
    assert not decisao_lado_a_lado("comer", {7: "a", 8: "b"}, regra)              # sem a racao
    assert not decisao_lado_a_lado("comer", {1: "racao", 9: "a"}, regra)          # sem fruta da regra
    assert oportunidade_lado_a_lado("comer", vistos, regra, 7, "a") == (True, True)
    assert oportunidade_lado_a_lado("comer", vistos, regra, 9, "a") == (True, False)   # a x de uma arvore nao e a da regra
    assert oportunidade_lado_a_lado("comer", vistos, regra, 1, "a") == (True, False)   # comeu a racao
    assert oportunidade_lado_a_lado("comer", vistos, regra, None, "a") == (True, False)
    assert oportunidade_lado_a_lado("comer", vistos, regra, 8, "c") == (False, False)  # a x da regra nao esta a vista
    assert oportunidade_lado_a_lado("dormir", vistos, regra, 7, "a") == (False, False)
    assert oportunidade_lado_a_lado("comer", {7: "a"}, regra, 7, "a") == (False, False)  # sem a racao


# ------------------------------------------------------------------ 3. a config


def test_as_recusas_da_config():
    with pytest.raises(ValueError, match="bool"):
        bv.validar_config_pqp(_fumaca(fruta_ao_lado=1))
    sem_paladar = {**_cfg("fumaca"), "fruta_ao_lado": True}
    with pytest.raises(ValueError, match="com o paladar"):
        bv.validar_config_pqp(sem_paladar)
    with pytest.raises(ValueError, match="comedouro"):
        bv.validar_config_pqp(_fumaca(lugar="perto"))
    cal = cpp.config_do_gosto(_cfg("calibracao_ao_lado"), S)
    bv.validar_config_pqp(cal)
    for bases in (bv.BASES_PQP_PALADAR, bv.BASES_PET_QUE_PENSA["calibracao"]):           # as de antes nao voltam (A5.8)
        with pytest.raises(bv.SementeSemPlano, match="A5.8"):
            bv.validar_config_pqp({**cal, "unidades": {**cal["unidades"], "bases": list(bases)}})
    bv.validar_config_pqp({**cal, "unidades": {**cal["unidades"], "bases": list(bv.BASES_PET_QUE_PENSA["validacao"])}})
    with pytest.raises(bv.SementeSemPlano, match="fruta ao lado"):                       # as 51101... so com ela
        bv.validar_config_pqp({k: v for k, v in cal.items() if k != "fruta_ao_lado"})


def test_g2_desligada_a_vida_e_a_do_paladar():
    """sem a chave e com "fruta_ao_lado": false, a mesma vida do paladar byte a byte, e as medidas sem a chave nova"""
    base = {**_fumaca(bracos=["P1"], protocolos=["T1"])}
    del base["fruta_ao_lado"]
    a = bv.bancada_pqp_da_config(base)
    b = bv.bancada_pqp_da_config({**base, "fruta_ao_lado": False})
    va, vb = a.vida(bv.EspecPQP("P1", "T1", 101)), b.vida(bv.EspecPQP("P1", "T1", 101))
    assert va.motor.log.para_jsonl() == vb.motor.log.para_jsonl()
    assert not va.motor.cfal.ligada and not any(e.tipo == "deixar_fruta" for e in va.motor.log)
    ma, mb = a.medir(va), b.medir(vb)
    del ma["custo"], mb["custo"]
    assert "ao_lado" not in ma and ma == mb and all("origem" not in c for c in ma["paladar"]["consumos"])


# ------------------------------------------------------------------ 4. a vida com a fruta ao lado


@pytest.mark.parametrize("braco,protocolo", [("P1", "T1"), ("P1-plan", "T2")])
def test_a_vida_com_a_fruta_ao_lado_e_as_medidas(braco, protocolo):
    bp, v, m = _vida(braco, protocolo)
    motor, al = v.motor, m["ao_lado"]
    assert motor.cfal.ligada and bp.cfg_corpo().paladar
    postas = motor.frutas_ao_lado
    assert postas and sum(r[f] for r in al["postas_por_dia"] for f in FRUTAS) == len(postas)
    assert sum(1 for e in motor.log if e.tipo == "deixar_fruta") == len(postas)
    assert {f["tipo"] for f in postas} == set(FRUTAS) and sorted(al["permutacao"]) == sorted(FRUTAS)
    assert all([f["x"], f["y"]] == al["celulas"][f["tipo"]] for f in postas)                # cada tipo na celula da permutacao
    # as comidas pela origem, contra o motor
    da_regra = [c for c in motor.consumos_mundo if c["origem"] == ORIGEM_AO_LADO and c["situacao"] == "madura"]
    assert sum(r[f] for r in al["comidas_da_regra_por_dia"] for f in FRUTAS) == len(da_regra)
    assert al["frutas_da_regra"]["da_regra"] == len(da_regra) > 0
    # as decisoes lado a lado: comer, com a racao e uma fruta da regra a vista; a fracao e a das que comeram fruta madura
    n = sum(r["decisoes"] for r in al["lado_a_lado_por_dia"])
    assert n > 0 and all(r["fracao"] is None or 0 <= r["fracao"] <= 1 for r in al["lado_a_lado_por_dia"])
    f = bv.fracao_lado_a_lado_dias(m, (0, bp.d_a - 1))
    assert f["decisoes"] == sum(r["decisoes"] for r in al["lado_a_lado_por_dia"][:bp.d_a])
    if protocolo == "T1":
        t1 = m["t1"]
        assert al["t1_alvo_padrao_x"]["oportunidades"] >= t1["n_antes"] and t1["n_antes"] <= 3
        assert 0 <= al["t1_alvo_padrao_x"]["padrao_e_x"] <= al["t1_alvo_padrao_x"]["oportunidades"]
    else:
        assert al["t2_x_da_regra_depois"] >= 0 and "t2" in m


def test_a_oportunidade_do_t1_e_a_nova_recontada():
    """o T1 com a fruta ao lado le so a oportunidade lado a lado (A5.3): recontada das decisoes do replay de medicao"""
    bp, v, m = _vida("P1", "T1")
    regs: list = []

    def fp(cfg=None):
        r = bv._RegistroPQP(bp.politica(v.espec, cfg), bp.bancada.cfg_mundo, bp.cfg_modelo, True, True)
        regs.append(r)
        return r
    bp.rejogar(v.motor.log, v.espec, fp, lambda mt: setattr(regs[-1], "motor", mt))
    linhas = []
    for d in regs[-1].decisoes:
        op, esc = oportunidade_lado_a_lado(d["acao"], d["maduros_id"], d["ids_ao_lado"], None if d["alvo"] is None else d["alvo"]["id"],
                                           v.x)
        if op:
            assert d["acao"] == "comer" and "racao" in d["maduros_id"].values()
        linhas.append({"tick": d["tick"], "depois": d["depois"], "conta": op, "sucesso": esc, "reexperiencia": d["comeu"] == v.x})
    esperado = bv.mudanca_de_escolha(linhas, bv.N_OPORTUNIDADES_PQP, v.tick_mudanca)
    assert {k: m["t1"][k] for k in esperado} == esperado
    assert any(ln["conta"] for ln in linhas), "a fumaca precisa de alguma oportunidade lado a lado"


# ------------------------------------------------------------------ 5. o orquestrador


def test_a_config_da_calibracao_e_a_do_adendo_5():
    c, pal = cpp.validar(_cfg("calibracao_ao_lado")), _cfg("calibracao_paladar")
    assert c["fruta_ao_lado"] is True and c["paladar"] is True and cpp.ao_lado(c)
    assert c["unidades"] == {"bases": list(bv.BASES_PQP_AO_LADO), "k": 4, "prefixo": "pet_que_pensa"}
    assert c["calibracao_ganho_gosto"] == {"grade": [S // 2, S, 2 * S, 4 * S], "dias": [4, 6], "faixa": [0.25, 0.75]}
    assert c["calibracao_g_plano"] == pal["calibracao_g_plano"]
    iguais = set(pal) - {"descricao", "unidades", "calibracao_ganho_gosto"}
    assert {k: c[k] for k in iguais} == {k: pal[k] for k in iguais}
    f = cpp.validar(_cfg("fumaca_calibracao_ao_lado"))
    assert set(f["sementes"]) <= bv.SEMENTES_TESTE and "plano" not in f and cpp.ao_lado(f)
    for chave in ("calibracao_ganho_gosto", "calibracao_g_plano"):
        assert {k: f[chave][k] for k in ("grade", "faixa")} == {k: c[chave][k] for k in ("grade", "faixa")}
    assert bv.LIMIAR_APRENDEU_AO_LADO == 1 / 4 and cpq.LIMIAR_APRENDEU == 1 / 3


def test_a_g_aprendeu_com_o_limiar_dado():
    por = {(b, p): {} for b in bv.BRACOS_PQP for p in ("T1", "T2")}
    for b in bv.BRACOS_PQP:
        for s, fa in enumerate((0.3, 0.3, 0.3, 0.3)):
            por[(b, "T1")][s] = {"t1": {"f_antes": fa, "sem_oportunidade": False}}
            por[(b, "T2")][s] = {"t2": {"sem_oportunidade": False, "sem_exposicao": False}}
    boot = cpq.BOOTSTRAP_PILOTO
    assert all(x["passa"] for x in cpq.premissas(por, boot, 1 / 4)["G-APRENDEU"].values())
    assert not any(x["passa"] for x in cpq.premissas(por, boot)["G-APRENDEU"].values())          # 0,3 nao passa de 1/3


def test_a_fumaca_dos_quatro_passos(tmp_path):
    cfg = _cfg("fumaca_calibracao_ao_lado")
    pasta = tmp_path / "cal"
    r = cpp.rodar_ganho_gosto(cfg, pasta)
    assert r["regra"]["fonte"].startswith("PLANO_ANALISE_V2_PET_QUE_PENSA, adendo 5")
    dias = tuple(cfg["calibracao_ganho_gosto"]["dias"])
    for pt in r["pontos"]:
        medidas = json.loads((pasta / "ganho_gosto" / f"ganho_{pt['ganho_gosto']}" / "medidas.json").read_text(encoding="utf-8"))
        assert pt["media"] == cpp.fracoes_do_ponto(medidas, dias, True)["media"]
        assert all("ao_lado" in m for m in medidas.values())
        with pytest.raises(ValueError, match="sobra"):
            cpp.fracoes_do_ponto(medidas, dias, False)
    assert r["escolha"] == cpp.escolha_ganho(r["pontos"], tuple(cfg["calibracao_ganho_gosto"]["faixa"]))
    cpp.rodar_g_plano(cfg, pasta)
    rv = cpp.rodar_reval(cfg, pasta)
    if not rv["passa"]:
        (pasta / "reval.json").write_text(json.dumps({**rv, "passa": True}), encoding="utf-8")   # so na fumaca: o encanamento do piloto
    pil = cpp.rodar_piloto(cfg, pasta)
    assert pil["regras"]["limiar_aprendeu"] == 1 / 4
    for braco, g in pil["premissas"]["G-APRENDEU"].items():
        assert g["passa"] == (g["ic"] is not None and g["ic"]["ic_inferior"] > 1 / 4)
    medidas = json.loads((pasta / "g_plano" / "piloto" / "P1" / "medidas.json").read_text(encoding="utf-8"))
    assert all("ao_lado" in m and m["paladar"]["g_reval"]["ganho_gosto"] == r["escolha"]["ganho_gosto"] for m in medidas.values())
