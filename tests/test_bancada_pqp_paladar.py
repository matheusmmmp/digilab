"""O Paladar, etapa 4 (a bancada; docs/futuro/paladar.md, secoes 6 e 7; adendo 3 de docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md): o paladar nos
bracos do J5, as medidas descritivas, a faixa nova e a calibracao do ganho_gosto e do g_plano montada, SEM rodar (so as sementes dos
testes).

O que se confere:
- a faixa 49101...49505 reservada com a fonte, disjunta, fora das queimadas, e as unidades dela sem colisao;
- a x com o paladar e a favorita do pet (PJ-1), com o empate pela rng de sempre, uniforme entre os tipos sobre os pets; a y entre as outras;
- a config: a chave `paladar` e as recusas (o ganho_gosto sem o paladar, o paladar pela 'lobos' ou pela 'corpo', as bases de cada fase);
- G2: desligado, a bancada do J5 e a de antes (o gabarito do J5 nos testes dele; aqui, o mesmo log com e sem o campo novo);
- a vida com o paladar: as tres chaves, o genoma da unidade no cerebro, o G1 (o replay do disco) e as medidas recontadas (os consumos
  contra o log do motor, o f_gosto contra a conta do canal sobre a leitura gravada, as racoes das 12 h, os pesos das classes por dia);
- a G-REVAL-POSSIVEL: a conta refeita a mao para uma unidade;
- o orquestrador: as recusas, a regra do ganho_gosto em dados com a resposta conhecida, e a fumaca dos quatro passos.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa as cpq  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa_paladar as cpp  # noqa: E402
from digilab.config import CONFIG_PALADAR_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.corpo import QUALIDADES, Corpo, div_arred  # noqa: E402
from digilab.events import FRUTAS  # noqa: E402
from digilab.genoma_paladar import genoma_paladar  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.policies.lobos import sinal_corpo, sinal_gosto  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.state import Estado  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa"
S = 1024


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def _fumaca(**kw) -> dict:
    """a fumaca da bancada do J5 com o paladar: as sementes dos testes, 2 dias de fase 1 e 1 de janela"""
    return {**_cfg("fumaca"), "paladar": True, "consequencia": {"ganho": 4, "canais_ligados": True, "ganho_gosto": S}, **kw}


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


def test_a_faixa_do_paladar_reservada_com_fonte():
    faixas = {(lo, hi): fonte for lo, hi, fonte in bv.FAIXAS_RESERVADAS}
    fonte = faixas[(49101, 49505)]
    assert "PLANO_ANALISE_V2_PET_QUE_PENSA" in fonte and "A3.5" in fonte and "PJ-5" in fonte and "paladar" in fonte
    assert bv.BASES_PQP_PALADAR == tuple(49101 + 101 * i for i in range(5))
    assert all("paladar" in bv.na_faixa_reservada(b) for b in bv.BASES_PQP_PALADAR)
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))
    assert not any(q_lo <= 49505 and 49101 <= q_hi for q_lo, q_hi, _ in bv.FAIXAS_QUEIMADAS)


def test_as_unidades_do_paladar_sem_colisao():
    novas = bv.unidades_derivadas(bv.BASES_PQP_PALADAR, 40, "pet_que_pensa")
    velhas = [u for fase in bv.BASES_PET_QUE_PENSA.values() for u in bv.unidades_derivadas(fase, 40, "pet_que_pensa")]
    a = {u["semente"] for u in novas} | {u["genoma"] for u in novas}
    b = {u["semente"] for u in velhas} | {u["genoma"] for u in velhas}
    assert len(a) == 2 * len(novas) and not a & b and not a & bv.SEMENTES_TESTE


# ------------------------------------------------------------------ 2. a x e a y


def test_a_x_e_a_favorita_com_o_empate_pela_rng_de_sempre():
    bp = bv.bancada_pqp_da_config(_fumaca(bracos=["P1"], protocolos=["T1"]))
    cc, perfis = bp.cfg_corpo(), CONFIG_PALADAR_LIGADA.perfis
    estado = random.getstate()
    xs = []
    for s in range(600):
        g = genoma_paladar(s, cc)
        x = bp.fruta_x(s)
        assert g.valor_inato(perfis[x], cc.escala) == max(g.valor_inato(perfis[f], cc.escala) for f in FRUTAS)
        y = bp.fruta_y(s)
        assert y != x and y == [f for f in FRUTAS if f != x][random.Random(derivar_semente("pet-que-pensa-y", s)).randrange(2)]
        xs.append(x)
    assert random.getstate() == estado
    assert all(150 < xs.count(f) < 250 for f in FRUTAS)                 # a forma girada: a x continua uniforme entre os tipos
    # o empate: a escolha entre as empatadas pela rng da x sem o paladar
    g = bv.GenomaPaladar({"doce": 100, "azedo": 100, "amargo": 100, "salgado": 256})
    assert g.favorita(perfis, cc.escala) == list(FRUTAS)
    for s in (1, 2, 3, 4242):
        assert bv.fruta_x_paladar_pqp(s, g, perfis, cc.escala) == FRUTAS[random.Random(derivar_semente("pet-que-pensa-x", s)).randrange(3)]
    sem = bv.bancada_pqp_da_config(_cfg("fumaca"))
    assert [sem.fruta_x(s) for s in range(50)] == [bv.fruta_x_pqp(s) for s in range(50)]
    assert [sem.fruta_y(s) for s in range(50)] == [bv.fruta_y_pqp(s) for s in range(50)]


# ------------------------------------------------------------------ 3. a config


def test_as_recusas_da_config():
    with pytest.raises(ValueError, match="bool"):
        bv.validar_config_pqp(_fumaca(paladar=1))
    with pytest.raises(ValueError, match="ganho_gosto"):
        bv.validar_config_pqp({**_cfg("fumaca"), "consequencia": {"ganho": 4, "ganho_gosto": S}})
    with pytest.raises(ValueError, match="nunca da 'lobos'"):
        bv.validar_config_pqp(_fumaca(lobos={"paladar": True}))
    with pytest.raises(ValueError, match="nunca da 'lobos'"):
        bv.validar_config_pqp(_fumaca(corpo={"paladar": True}))
    cal = cpp.config_do_gosto(_cfg("calibracao_paladar"), S)
    bv.validar_config_pqp(cal)
    with pytest.raises(bv.SementeSemPlano, match="45101"):                # as da calibracao sem o paladar nao voltam (A3.5)
        bv.validar_config_pqp({**cal, "unidades": {**cal["unidades"], "bases": list(bv.BASES_PET_QUE_PENSA["calibracao"])}})
    bv.validar_config_pqp({**cal, "unidades": {**cal["unidades"], "bases": list(bv.BASES_PET_QUE_PENSA["validacao"])}})
    sem = {k: v for k, v in cal.items() if k != "paladar"}
    sem["consequencia"] = {k: v for k, v in sem["consequencia"].items() if k != "ganho_gosto"}
    with pytest.raises(bv.SementeSemPlano, match="paladar"):              # as do paladar so com o paladar
        bv.validar_config_pqp(sem)


def test_g2_desligado_a_vida_e_a_de_antes():
    """sem a chave e com "paladar": false, a mesma vida byte a byte; o gabarito do J5 (tests/test_bancada_pet_que_pensa.py) confere a de
    antes da etapa"""
    a = bv.bancada_pqp_da_config({**_cfg("fumaca"), "bracos": ["P1"], "protocolos": ["T1"]})
    b = bv.bancada_pqp_da_config({**_cfg("fumaca"), "bracos": ["P1"], "protocolos": ["T1"], "paladar": False})
    va, vb = a.vida(bv.EspecPQP("P1", "T1", 101)), b.vida(bv.EspecPQP("P1", "T1", 101))
    assert va.motor.log.para_jsonl() == vb.motor.log.para_jsonl()
    assert not a.cfg_corpo().paladar and not a.cfg_lobos(bv.EspecPQP("P1", "T1", 101)).paladar and not va.motor.cpal.ligada
    ma, mb = a.medir(va), b.medir(vb)
    del ma["custo"], mb["custo"]                                           # o tempo de CPU muda de vida para vida
    assert "paladar" not in ma and ma == mb


# ------------------------------------------------------------------ 4. a vida com o paladar


@pytest.mark.parametrize("braco,protocolo", [("P1", "T1"), ("P1-plan", "T2")])
def test_a_vida_com_o_paladar_e_as_medidas(braco, protocolo):
    bp, v, m = _vida(braco, protocolo)
    s = v.espec.semente
    assert bp.cfg_corpo().paladar and bp.cfg_lobos(v.espec).paladar and v.motor.cpal.ligada
    assert v.x == bp.fruta_x(s) and m["x"] == v.x
    p = m["paladar"]
    g = genoma_paladar(s, bp.cfg_corpo())
    assert p["genoma"] == g.h and p["lugar_da_x"] == 1 and p["ordem_inata"][0] == v.x
    # os consumos contra o log do motor: um por consumo no mapa
    comidos = [c for c in p["consumos"]]
    assert sum(r["total"] for r in p["por_dia"]) == len(comidos)
    assert sum(p["contagem"].values()) == sum(1 for c in comidos if c["situacao"] == "madura")
    maduros = [c for c in comidos if c["situacao"] == "madura"]
    assert maduros and any(c["f_gosto"] is not None for c in maduros), "a fumaca precisa de algum consumo com o gosto"
    for c in maduros:
        assert set(c["paladar"]) == set(QUALIDADES) and all(0 <= x <= S for x in c["paladar"].values())
        # o f_gosto do cerebro e a conta do canal sobre a leitura gravada (o comer e o "achou e comeu", com o credito do corpo)
        if c["f_gosto"] is not None:
            assert c["f_gosto"] == div_arred(S * sum(div_arred(g.h[q] * c["paladar"][q], S) for q in QUALIDADES), S)
    racoes = [c for c in maduros if c["tipo"] == "racao"]
    for i, c in enumerate(racoes):
        antes = [o for o in racoes[:i] if c["tick_motor"] - o["tick_motor"] < 720]
        assert c["racoes_12h"] == len(antes) + 1 and 0 < c["saciedade_salgado"] <= bp.cfg_corpo().escala
    assert len(p["classes_por_dia"]) == bp.dias_da_vida(protocolo)
    assert all(set(t) == {f"comida:{x}" for x in ("racao",) + FRUTAS}
               for d in p["classes_por_dia"] for t in d["classes"].values())
    f1 = bv.fracao_fruta(comidos, 0, bp.d_a * 1440)
    assert p["fracao_fruta_fase1"] == f1 and f1["consumos"] == sum(r["total"] for r in p["por_dia"][:bp.d_a])
    assert len(p["gosto_do_modelo"]) == bp.dias_da_vida(protocolo)
    assert p["g_reval"] == bp.g_reval_possivel(s)


def test_g_reval_possivel_a_conta_a_mao():
    bp, v, _m = _vida()
    s = v.espec.semente
    r = bp.g_reval_possivel(s)
    cc, cm, h = bp.cfg_corpo(), bp.bancada.cfg_mundo, genoma_paladar(s, bp.cfg_corpo()).h
    efeito = bv.efeitos_pqp(r["x"], bp.bancada.cfg_frutas, faz_mal=True)
    assert r["x"] == bp.fruta_x(s) and r["efeito_x_depois"] == bp.bancada.cfg_frutas.efeito_humor_ruim
    ref = Corpo.de_estado(Estado(fome=0.5, energia=0.5, humor=0.5), CONFIG_PADRAO, cc, com_mundo=True)
    antes = PercepcaoCorpo(**ref.receptores())
    pol = bp.politica(bv.EspecPQP("P1", "T1", s), CONFIG_PADRAO)
    cq = pol.cfg_consequencia
    for t in ("racao",) + FRUTAS:
        c = Corpo.de_estado(Estado(fome=0.5, energia=0.5, humor=0.5), CONFIG_PADRAO, cc, com_mundo=True)
        c.estimulo_consumo_mundo(t, "madura", cm, efeito_fruta=efeito[t] if t in FRUTAS else 0.0, perfil=CONFIG_PALADAR_LIGADA.perfis[t])
        depois = PercepcaoCorpo(**c.receptores())
        # com a saciedade em zero, o sabor e o perfil: a leitura e div_arred(perfil x S, C)
        assert {q: getattr(depois, f"paladar_{q}") for q in QUALIDADES} == \
            {q: div_arred(CONFIG_PALADAR_LIGADA.perfis[t][q] * S, cc.escala) for q in QUALIDADES}
        drives = pol.cerebro._interna._drives_corpo(cq, t in FRUTAS)
        assert ("humor" in drives) == (t in FRUTAS)                       # a E2 so no comer da fruta
        esperado = sinal_corpo(antes, depois, drives, cq.ganho, S, dict(cq.pesos_drives_corpo)) + sinal_gosto(depois, h, cq.ganho_gosto, S)
        assert r["sinais"][t]["total"] == esperado
    tx = r["sinais"][r["x"]]["total"]
    assert r["passa"] == any(tx < r["sinais"][t]["total"] for t in ("racao",) + FRUTAS if t != r["x"])
    with pytest.raises(ValueError, match="sem o paladar"):
        bv.bancada_pqp_da_config(_cfg("fumaca")).g_reval_possivel(s)


# ------------------------------------------------------------------ 5. o orquestrador


def test_a_config_da_calibracao_com_o_paladar_e_a_do_adendo():
    c, sem = cpp.validar(_cfg("calibracao_paladar")), _cfg("calibracao")
    assert c["paladar"] is True and c["plano"] == bv.PLANO_PQP
    assert c["unidades"] == {"bases": list(bv.BASES_PQP_PALADAR), "k": 4, "prefixo": "pet_que_pensa"}
    assert c["calibracao_ganho_gosto"] == {"grade": [S // 2, S, 2 * S], "dias": [4, 6], "faixa": [0.25, 0.60]}
    assert c["calibracao_g_plano"] == sem["calibracao_g_plano"]
    iguais = set(sem) - {"descricao", "unidades", "bracos", "protocolos", "calibracao_g_plano"}
    assert {k: c[k] for k in iguais} == {k: sem[k] for k in iguais}
    f = cpp.validar(_cfg("fumaca_calibracao_paladar"))
    assert set(f["sementes"]) <= bv.SEMENTES_TESTE and "plano" not in f and "unidades" not in f
    for chave in ("calibracao_ganho_gosto", "calibracao_g_plano"):
        assert {k: f[chave][k] for k in ("grade", "faixa")} == {k: c[chave][k] for k in ("grade", "faixa")}


def test_as_recusas_do_orquestrador(tmp_path):
    c = _cfg("calibracao_paladar")
    with pytest.raises(ValueError, match="'paladar': true"):
        cpp.validar({k: v for k, v in c.items() if k != "paladar"})
    with pytest.raises(ValueError, match="bracos"):
        cpp.validar({**c, "bracos": ["P1"]})
    with pytest.raises(ValueError, match="ganho_gosto"):
        cpp.validar({**c, "consequencia": {**c["consequencia"], "ganho_gosto": S}})
    with pytest.raises(ValueError, match="grade"):
        cpp.validar({**c, "calibracao_ganho_gosto": {**c["calibracao_ganho_gosto"], "grade": [S, S // 2]}})
    with pytest.raises(ValueError, match="fase 1"):
        cpp.validar({**c, "calibracao_ganho_gosto": {**c["calibracao_ganho_gosto"], "dias": [5, 7]}})
    with pytest.raises(bv.SementeSemPlano, match="validacao"):
        cpp.validar({**c, "unidades": {**c["unidades"], "bases": list(bv.BASES_PET_QUE_PENSA["validacao"])}})
    with pytest.raises(FileNotFoundError, match="ganho_gosto"):
        cpp.rodar_g_plano(_cfg("fumaca_calibracao_paladar"), tmp_path / "nada")


def test_a_regra_do_ganho_gosto():
    p = lambda g, m: {"ganho_gosto": g, "media": m}  # noqa: E731
    assert cpp.escolha_ganho([p(512, 0.2), p(1024, 0.3), p(2048, 0.5)], (0.25, 0.6))["ganho_gosto"] == 1024
    e = cpp.escolha_ganho([p(512, 0.05), p(1024, 0.1), p(2048, 0.2)], (0.25, 0.6))
    assert (e["ganho_gosto"], e["fechou"], e["lado"]) == (2048, False, "abaixo") and e["desvio"] == pytest.approx(0.05)
    e = cpp.escolha_ganho([p(512, 0.7), p(1024, 0.7), p(2048, None)], (0.25, 0.6))
    assert (e["ganho_gosto"], e["lado"]) == (512, "acima")
    with pytest.raises(RuntimeError):
        cpp.escolha_ganho([p(512, None)], (0.25, 0.6))


def test_a_fumaca_dos_quatro_passos(tmp_path):
    cfg = _cfg("fumaca_calibracao_paladar")
    pasta = tmp_path / "cal"
    r = cpp.rodar_ganho_gosto(cfg, pasta)
    dias = tuple(cfg["calibracao_ganho_gosto"]["dias"])
    for pt in r["pontos"]:
        medidas = json.loads((pasta / "ganho_gosto" / f"ganho_{pt['ganho_gosto']}" / "medidas.json").read_text(encoding="utf-8"))
        assert pt["media"] == cpp.fracoes_do_ponto(medidas, dias)["media"]
        assert all(m["braco"] == "P1" and m["protocolo"] == "fase1" and "paladar" in m for m in medidas.values())
    assert r["escolha"] == cpp.escolha_ganho(r["pontos"], tuple(cfg["calibracao_ganho_gosto"]["faixa"]))
    with pytest.raises(FileNotFoundError, match="passo 3"):
        cpp.rodar_piloto(cfg, pasta)
    g = cpp.rodar_g_plano(cfg, pasta)
    assert g["escolha"]["g_plano"] in cfg["calibracao_g_plano"]["grade"]
    meta = json.loads((pasta / "g_plano" / "meta.json").read_text(encoding="utf-8"))
    assert meta["config"]["consequencia"]["ganho_gosto"] == r["escolha"]["ganho_gosto"] and meta["config"]["paladar"] is True
    rv = cpp.rodar_reval(cfg, pasta)
    assert rv["ganho_gosto"] == r["escolha"]["ganho_gosto"] and rv["n"] == len(cfg["sementes"])
    with pytest.raises(FileExistsError):
        cpp.rodar_reval(cfg, pasta)
    if not rv["passa"]:
        with pytest.raises(RuntimeError, match="inconclusivo por desenho"):
            cpp.rodar_piloto(cfg, pasta)
        # o encanamento do piloto, com a premissa trocada a mao (so na fumaca)
        (pasta / "reval.json").write_text(json.dumps({**rv, "passa": True}), encoding="utf-8")
    pil = cpp.rodar_piloto(cfg, pasta)
    medidas = {}
    for b in bv.BRACOS_PQP:
        medidas.update(json.loads((pasta / "g_plano" / "piloto" / b / "medidas.json").read_text(encoding="utf-8")))
    assert len(medidas) == len(bv.BRACOS_PQP) * 2 * len(cfg["sementes"])
    assert all(m["paladar"]["g_reval"]["ganho_gosto"] == r["escolha"]["ganho_gosto"] for m in medidas.values())
    assert pil["g_plano"] == g["escolha"]["g_plano"] and cpq.VIDAS_POR_UNIDADE == 8
