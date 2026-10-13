"""V2, MUNDO-ALVO: o braco P1-alvo na bancada, o G-USO e o orquestrador do piloto e da validacao (docs/PLANO_ANALISE_V2_MUNDO_ALVO.md).
So as sementes dos testes."""
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
import run_v2_mundo_alvo as ra  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.metrics import classes_por_dia, uso_do_alvo  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402

CFG = json.loads((RAIZ / "experiments/configs/v2_mundo_alvo/fumaca_validacao.json").read_text(encoding="utf-8"))
CFG_PILOTO = json.loads((RAIZ / "experiments/configs/v2_mundo_alvo/fumaca_piloto.json").read_text(encoding="utf-8"))


def _pequena(cfg, **kw):
    c = json.loads(json.dumps(cfg))
    c.update({"donos": ["atencioso"], "lugares": ["comedouro"], "dias": 3, "orcamento": 48})
    c["unidades"]["bases"] = [101]
    c.update(kw)
    return c


@pytest.fixture(scope="module")
def bancada():
    return bv.bancada_da_config(ra.config_bancada(_pequena(CFG)))


@pytest.fixture(scope="module")
def vida_alvo(bancada):
    return bancada.vida(bv.EspecVida("atencioso", "P1-alvo", 101, None, "fisico", lugar="comedouro"))


# ------------------------------------------------------------------ o braco P1-alvo
def test_p1_alvo_e_o_p1_com_so_a_chave_do_alvo(bancada):
    e = bv.EspecVida("atencioso", "P1-alvo", 101, None, "fisico", lugar="comedouro")
    alvo = bv.do_braco(bancada.politica(e)).cerebro
    p1 = bv.do_braco(bancada.politica(replace(e, braco="P1"))).cerebro
    assert alvo.cl.alvo_aprendido and not p1.cl.alvo_aprendido
    assert alvo.cl == replace(p1.cl, alvo_aprendido=True)
    assert alvo.cl.w0_alvo == ra.W0_ALVO_PLANO == alvo.cl.escala // 16
    assert alvo.n_pesos() == 792 and p1.n_pesos() == 756          # o plano, secao 2 (abaixo do teto de 1000)
    assert bv.braco_de("P1-alvo").fonte == "consequencia"


def test_p1_alvo_so_no_mundo_fisico():
    b = bv.bancada_da_config({"bracos": ["P1-alvo"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16,
                              "sonda": {"estados": 4, "amostras": 4, "semente": 101}, "bootstrap": {}, "mundos": ["bola"]})
    with pytest.raises(ValueError, match="mundo fisico"):
        b.politica(bv.EspecVida("atencioso", "P1-alvo", 101, None, "bola"))


def test_p1_alvo_g1_e_usa_o_alvo(bancada, vida_alvo):
    bancada.conferir_replay(vida_alvo)                               # G1, estado interno incluido
    ds = ra.decisoes_com_alvo(vida_alvo)
    assert ds and any(d["alvo"] != d["padrao"] for d in ds)
    acoplado = bancada.acoplar(bancada.vida(bv.EspecVida("atencioso", "P0z", 101, None, "fisico", lugar="comedouro")), "P1-alvo",
                               "nenhum")
    assert acoplado.rotulo_braco == ra.ROT_P1AAC


def test_os_outros_bracos_nao_mudam_com_o_p1_alvo_na_tabela(bancada):
    # o P1 e o P0 de hoje: sem o alvo (os gabaritos do mundo, na suite, cobrem as vidas de antes byte a byte)
    for braco in ("P0", "P1"):
        e = bv.EspecVida("atencioso", braco, 101, None, "fisico", lugar="comedouro")
        assert not bv.do_braco(bancada.politica(e)).cerebro.cl.alvo_aprendido
    assert bv.BRACOS["P1"] == bv.Braco("P1", "consequencia", "N3")      # o P1 de sempre, sem o campo novo


# ------------------------------------------------------------------ o G-USO
def test_prior_com_o_mesmo_u_e_a_escolha_quando_os_pesos_sao_os_do_prior(vida_alvo):
    cer = bv.do_braco(vida_alvo.motor.politica).cerebro
    S, w0 = cer.cl.escala, cer.cl.w0_alvo
    iguais = 0
    ds = iter(ra.decisoes_com_alvo(vida_alvo))
    for mot in cer.motivos:
        al = mot.get("alvo_aprendido")
        if al is None or al["alvo"] is None:
            continue
        d = next(ds)
        prior = [max(0, w0) / S + (1.0 if c == al["padrao"] else 0.0) for c in al["classes"]]
        if [al["pesos"][c] for c in al["classes"]] == prior:
            assert d["prior"] == d["alvo"]
            iguais += 1
    assert iguais > 0


def test_uso_do_alvo_conta_exata():
    ds = [(10, "comida", "comida"), (20, "cheiro", "comida"), (30, "vagar", "vagar"), (40, "casa", "vagar")]
    assert uso_do_alvo(ds, (0, 100)) == {"decisoes": 4, "difere": 2, "fracao": 0.5}
    assert uso_do_alvo(ds, (15, 35)) == {"decisoes": 2, "difere": 1, "fracao": 0.5}
    assert uso_do_alvo(ds, (50, 60))["fracao"] is None
    with pytest.raises(ValueError):
        uso_do_alvo(list(reversed(ds)), (0, 100))


def test_classes_por_dia():
    T = TICKS_POR_DIA
    c = classes_por_dia([(0, "comer", "comida"), (10, "comer", "cheiro"), (20, "comer", "comida"), (T + 5, "explorar", "vagar")])
    assert c["comer"]["1"] == {"n": 3, "fracao": {"cheiro": 1 / 3, "comida": 2 / 3}}
    assert c["explorar"]["2"] == {"n": 1, "fracao": {"vagar": 1.0}}


def test_g_uso_por_unidade_e_limiar():
    regs = [{"braco": "P1-alvo", "semente": s, "alvo": {"g_uso": {"fracao": f, "decisoes": 10}}}
            for s, fs in ((1, (0.1, 0.3)), (2, (0.2, None)), (3, (0.25, 0.25))) for f in fs]
    r = ra.g_uso(regs, {"reamostragens": 2000, "semente": 4242}, 0.05)
    assert r["media"] == pytest.approx((0.2 + 0.2 + 0.25) / 3)
    assert r["celulas_sem_decisao"] == 1 and r["passa"]
    assert not ra.g_uso(regs, {"reamostragens": 2000, "semente": 4242}, 0.5)["passa"]


# ------------------------------------------------------------------ a tabela do alvo no fim de cada dia
def test_tabela_por_dia_e_a_do_cerebro_no_fim_do_dia(bancada, vida_alvo):
    serie = ra.tabela_alvo_por_dia(bancada, vida_alvo, 3)
    assert len(serie) == 3
    fab, fm = bancada.fabrica_politica(vida_alvo.espec), bancada.fabrica_motor(vida_alvo.espec)
    for d in (1, 2):
        r = reproduzir_mundo(vida_alvo.motor.log, fab, semente=101, fabrica_motor=fm, ate_tick=d * TICKS_POR_DIA)
        assert serie[d - 1] == bv.do_braco(r.politica).cerebro._pesos_alvo_mundo
    assert serie[2] == bv.do_braco(vida_alvo.motor.politica).cerebro._pesos_alvo_mundo
    assert serie[0] != serie[2]                                     # aprendeu ao longo da vida


# ------------------------------------------------------------------ as categorias e a leitura
def _r(inf95, sup95, inf90, sup90):
    return {"ic95": {"ic_inferior": inf95, "ic_superior": sup95}, "ic90": {"ic_inferior": inf90, "ic_superior": sup90}}


def test_categorias_do_g_alvo():
    d = 0.01
    assert ra.categoria_g_alvo(_r(0.02, 0.05, 0.025, 0.04), d)["categoria"] == "o alvo ajuda"
    assert ra.categoria_g_alvo(_r(0.001, 0.009, 0.002, 0.008), d)["categoria"] == "o alvo ajuda, abaixo de Delta"
    assert ra.categoria_g_alvo(_r(-0.05, -0.01, -0.04, -0.02), d)["categoria"] == "o alvo atrapalha"
    assert ra.categoria_g_alvo(_r(-0.012, 0.009, -0.008, 0.008), d)["categoria"] == "equivalente"
    assert ra.categoria_g_alvo(_r(-0.02, 0.03, -0.015, 0.02), d)["categoria"] == "inconclusivo"


def test_leitura_da_secao_9():
    passa, falha = {"passa": True}, {"passa": False}
    assert "premissa" in ra.leitura(falha, passa, {"categoria": "o alvo ajuda"}, True)
    assert "e do pet" in ra.leitura(passa, passa, {"categoria": "o alvo ajuda"}, True)
    assert "dono reagindo" in ra.leitura(passa, passa, {"categoria": "o alvo ajuda"}, False)
    assert "usou o alvo e nao procurou melhor" in ra.leitura(passa, passa, {"categoria": "equivalente"}, False)
    assert "o alvo nao foi usado" in ra.leitura(passa, falha, {"categoria": "inconclusivo"}, False)
    assert "atrapalha" in ra.leitura(passa, falha, {"categoria": "o alvo atrapalha"}, False)


# ------------------------------------------------------------------ a config
def test_modos_da_config():
    assert ra.modo_da_config(CFG) == "fumaca" and ra.modo_da_config(CFG_PILOTO) == "fumaca"
    piloto = json.loads((RAIZ / "experiments/configs/v2_mundo_alvo/piloto.json").read_text(encoding="utf-8"))
    assert ra.modo_da_config(piloto) == "piloto"
    assert piloto["unidades"]["bases"] == list(ra.BASES_PILOTO) and piloto["unidades"]["k"] == ra.K_PILOTO
    for bases in ([31101], [32505], [32101, 32202]):                 # as do plano do mundo, nunca
        with pytest.raises(bv.SementeSemPlano):
            ra.modo_da_config({**CFG, "unidades": {**CFG["unidades"], "bases": bases}})
    with pytest.raises(bv.SementeSemPlano):                          # o piloto recusa as da validacao
        ra.modo_da_config({**piloto, "unidades": {**piloto["unidades"], "bases": list(ra.BASES_VALIDACAO)}})
    with pytest.raises(bv.SementeSemPlano):
        ra.modo_da_config({**piloto, "unidades": {**piloto["unidades"], "bases": [47101, 47202]}})
    for k, v in (("delta_mf", 0.01), ("m", 2.0), ("lobos", {}), ("g_uso", {"limiar": 0.1}), ("bracos_afastado", []),
                 ("acoplados", ra.ACOPLADOS[:1])):
        with pytest.raises(ValueError):
            ra.modo_da_config({**CFG, k: v})
    with pytest.raises(ValueError):
        ra.modo_da_config({**piloto, "dias": 7})


def test_faixas_do_plano_reservadas():
    for b in ra.BASES_PILOTO + ra.BASES_VALIDACAO:
        assert "MUNDO_ALVO" in (bv.na_faixa_reservada(b) or "")
    us = bv.unidades_derivadas(ra.BASES_PILOTO, 10, ra.PREFIXO) + bv.unidades_derivadas(ra.BASES_VALIDACAO, 10, ra.PREFIXO)
    vals = [u["semente"] for u in us] + [u["genoma"] for u in us]
    assert len(set(vals)) == len(vals)
    assert all(bv.na_faixa_reservada(v) is None and v not in bv.SEMENTES_TESTE for v in vals)


# ------------------------------------------------------------------ as fumacas inteiras (pequenas)
def test_fumaca_da_validacao(tmp_path):
    cfg = _pequena(CFG, donos=["atencioso", "aleatorio"])
    cfg["unidades"]["bases"] = [101, 202]
    r = ra.rodar(cfg, tmp_path / "v", 1)
    res = r["resultado"]
    assert len(r["medidas"]) == 2 * 2 * 8                           # 2 unidades x 2 celulas x (4 + 2 acoplados + 2 afastados)
    assert {m["braco"] for m in r["medidas"].values()} == {"P0", "P0z", "P1", "P1-alvo", ra.ROT_P1AC, ra.ROT_P1AAC,
                                                           "P1@afastado", "P1-alvo@afastado"}
    assert set(res["secundarios"]) == set(ra.HOLM) and res["nao_rodados"] == []
    assert res["G-USO"]["n"] == 2 and res["G-ALVO"]["categoria"] in set(ra.CATEGORIAS.values())
    assert res["descritivos"]["alvo"]["vidas_com_tabela"] == 4
    meta = json.loads((tmp_path / "v" / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["sha256"]) == {"mundo.py", "config.py", "lobos.py", "engine.py", "plano", "config"}
    assert meta["cerebros_conferidos"]["P1-alvo"]["pesos"] == 792
    assert len(list((tmp_path / "v" / "vidas").glob("*.jsonl"))) == 32
    with pytest.raises(FileExistsError):
        ra.rodar(cfg, tmp_path / "v", 1)


def test_fumaca_do_piloto(tmp_path):
    cfg = _pequena(CFG_PILOTO)
    cfg["unidades"]["bases"] = [101, 202, 303]
    r = ra.rodar(cfg, tmp_path / "p", 1)
    res = r["resultado"]
    assert len(r["medidas"]) == 3 * 6
    assert res["fase"] == "piloto" and ra.PODER["k_min"] <= res["n"]["k"] <= ra.PODER["k_max"]
    assert res["n"]["n"] == 3 * res["n"]["k"]
    assert set(res["poder_secundarios"]) == {"PA-2 (G-ALVO-AC)", "PA-3 (G-INSTINTO)"}
    assert res["custo"]["validacao_estimada"]["vidas"] == res["n"]["n"] * 1 * 8


# ------------------------------------------------------------------ o canal do humor da comida podre no P1-alvo (saida 1)
def test_p1_alvo_com_canais_come_podre_e_roda():
    """O caso achado na fumaca do piloto (base 101, relapso, perto; o acoplado P1-alvo^ac ao P0z): o P1-alvo escolhe a classe
    comida_podre e come a fruta podre (humor -0,1), com os canais do J1 e a presenca_fruta_mundo desligada. Antes o cerebro falhava alto
    (CANAIS-REFORCO); pela saida 1 (decisao do Matheus, 2026-10-13) o alvo aprendido conta como leitor da comida, e a vida roda (o G1 e
    conferido no acoplar). O canal do humor fica negativo, e o alvo recebe o sinal inteiro da decisao: o peso da comida_podre desce."""
    cfg = json.loads(json.dumps(CFG_PILOTO))
    cfg.update({"donos": ["relapso"], "lugares": ["perto"]})
    b = bv.bancada_da_config(ra.config_bancada(cfg))
    u = bv.unidades_derivadas([101], 1, ra.PREFIXO)[0]
    z = b.vida(bv.EspecVida("relapso", "P0z", u["semente"], u["genoma"], "fisico", lugar="perto"))
    v = b.acoplar(z, "P1-alvo", "nenhum")
    cer = bv.do_braco(v.motor.politica).cerebro
    podres = [m for m in cer.motivos if (m.get("alvo_aprendido") or {}).get("alvo") == "comida_podre"
              and m.get("mundo", {}).get("comeu") is not None]
    assert podres
    ei = cer.estado_interno()
    assert ei["canais"]["por_canal"]["humor"] < 0
    assert any(t["comida_podre"] < cer.cl.w0_alvo for t in ei["pesos_alvo_mundo"].values() if "comida_podre" in t)
    b.acoplar(z, "P1", "nenhum")                                   # o P1 do J1, no mesmo registro, roda como antes


def test_sem_leitor_da_comida_o_canal_do_humor_segue_falhando_alto():
    """A guarda do CANAIS-REFORCO fica: o P1 com canais, sem o alvo e sem a presenca, comendo a fruta que mexe no humor, falha alto."""
    import digilab.policies.lobos as lb
    lob = object.__new__(lb.PoliticaLobos)                      # so o que a guarda le: a escala e os canais novos (nenhum)
    lob._escala, lob._canais_novos = 1024, ()
    with pytest.raises(RuntimeError, match="canal da fruta sem peso que leia a fruta"):
        lob._creditar_canais({"acao": None}, {"humor": -113}, -113)
