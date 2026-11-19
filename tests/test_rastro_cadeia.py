"""O rastro da cadeia, o R1 (docs/PLANO_ANALISE_V3_PET_VIVO_R1.md, secao 7): a `ConfigRastro`, o `motivo["cadeia"]` do M-ADAPT, a
`Afeto.r_intervalo`, o texto (digilab/digibrain/rastro.py), as medidas (`metrics.medidas_rastro`) e o orquestrador do replay
(experiments/run_v3_pet_vivo_r1.py). So as sementes dos testes: nenhuma vida da run do PV-2."""
from __future__ import annotations

import copy
import json
import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_pet_vivo_r1 as R  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_PADRAO, CONFIG_RASTRO, CONFIG_RASTRO_LIGADA, PARAMETROS_RASTRO, ConfigRastro  # noqa: E402
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.digibrain.rastro import texto_cadeia, texto_da_vida  # noqa: E402

DIAS = 4
CFG = json.loads((RAIZ / "experiments/configs/v3_pet_vivo/r1.json").read_text(encoding="utf-8"))
UNIDADE = {"base": 101, "k": 0, "semente": 101, "genoma": 0}


@pytest.fixture(scope="module")
def vidas():
    """a mesma vida do HOJE (101, comedouro), sem e com o rastro"""
    return {r: R._vida_de_teste(101, r, DIAS, lugar="comedouro") for r in (False, True)}


def _motivos(vidas, rastro):
    return orq.cerebro_de(vidas[rastro][1]).motivos


# ------------------------------------------------------------------ a chave
def test_a_config_do_rastro():
    assert set(PARAMETROS_RASTRO) == {f.name for f in fields(ConfigRastro)}
    assert all(st in ("PROPOSTO", "DECIDIDO") for st, _ in PARAMETROS_RASTRO.values())
    assert CONFIG_RASTRO.ligada is False and CONFIG_RASTRO_LIGADA.ligada is True
    with pytest.raises(TypeError):
        ConfigRastro(ligada=1)
    with pytest.raises(TypeError):
        DigiBrain(CONFIG_PADRAO, orq.config_do_braco("REL", None, True), orq.CM, semente=101, cfg_rastro=True)


def test_desligada_nenhum_campo_novo(vidas):
    assert not any("cadeia" in m for m in _motivos(vidas, False))
    fp, _ = R.pv2.fabricas("HOJE", "atencioso", 101, DIAS, R.ORCAMENTO_POR_DIA, extra_cerebro={"cfg_rastro": CONFIG_RASTRO})
    assert orq.cerebro_de(fp(CONFIG_PADRAO)).rastro is False


def test_ligada_a_vida_e_a_mesma_decisao_a_decisao(vidas):
    (m0, r0, _, _), (m1, r1, _, _) = vidas[False], vidas[True]
    assert bv.resumo_motor(m0) == bv.resumo_motor(m1)
    c0, c1 = orq.cerebro_de(r0), orq.cerebro_de(r1)
    sem_rastro = [{k: v for k, v in m.items() if k != "cadeia"} for m in c1.motivos]
    assert json.dumps(sem_rastro, sort_keys=True) == json.dumps(c0.motivos, sort_keys=True)
    e0, e1 = c0.estado_interno(), c1.estado_interno()
    e0.pop("motivos"), e1.pop("motivos")
    assert json.dumps(e0, sort_keys=True) == json.dumps(e1, sort_keys=True)


def test_ligada_a_vida_do_v38_e_a_mesma():
    def vida(rastro):
        fab = R.pv2.fabricas("HOJE", "relapso", 202, 2, R.ORCAMENTO_POR_DIA, v38=True, extra_cerebro=R.RASTRO if rastro else None)
        from bancada.regras_mundo import simular_vida_fisico
        from digilab.donos import criar_dono
        from digilab.mundo import DonoComLugar
        reg = fab[0](CONFIG_PADRAO)
        motor, _ = simular_vida_fisico(DonoComLugar(criar_dono("relapso"), "longe", 202, "relapso", orq.CM), reg, 202, 2,
                                       R.ORCAMENTO_POR_DIA * 2, "relapso", fab[1])
        return motor, orq.cerebro_de(reg)
    (m0, c0), (m1, c1) = vida(False), vida(True)
    assert bv.resumo_motor(m0) == bv.resumo_motor(m1)
    assert [m["escolha"] for m in c0.motivos] == [m["escolha"] for m in c1.motivos]
    R.conferir_rastro(c1.motivos, CONFIG_PADRAO.intervalo_decisao_ticks)


def test_o_g1_do_replay_com_o_rastro(vidas):
    motor, _, fab, _ = vidas[True]
    orq.conferir_replay(motor, fab, 101, motor.log.para_jsonl())


# ------------------------------------------------------------------ o registro
def test_o_registro_de_cada_decisao(vidas):
    motivos = _motivos(vidas, True)
    assert "cadeia" not in motivos[-1] and all("cadeia" in m for m in motivos[:-1])
    R.conferir_rastro(motivos, CONFIG_PADRAO.intervalo_decisao_ticks)
    for m in motivos[:-1]:
        c, con = m["cadeia"], m["consequencia"]
        assert (c["mesmo_tick"]["r"], c["mesmo_tick"]["r_n"], c["mesmo_tick"]["canais"]) == (con["r"], con["r_n"], con["canais"])
        assert c["atualizacoes"] == {"p1": con["p1"], "p2": con["creditos"], "episodio": con["episodio"], "autobio": con["autobio"]}
        assert set(c["intervalo"]["canais"]) == set(c["mesmo_tick"]["canais"])
        assert c["intervalo"]["ja_contado"] is False
        assert all(c["intervalo"]["tick_de"] <= t <= c["intervalo"]["tick_ate"] for _, t in c["gestos"])
    # o sono: o r do mesmo tick e 0 (o DORMIR nao tem estimulo), e a energia volta no intervalo
    dormir = [m["cadeia"] for m in motivos[:-1] if m["acao"] == "dormir"]
    assert dormir and all(c["mesmo_tick"]["r"] == 0 for c in dormir)
    assert any(c["intervalo"]["delta"]["energia"] > 0 for c in dormir)
    # houve consumo, com o P1, e algum gesto do dono caiu num intervalo
    assert any(m["cadeia"]["atualizacoes"]["p1"] is not None for m in motivos[:-1])
    assert any(m["cadeia"]["gestos"] for m in motivos[:-1])


def test_a_conferencia_falha_alto(vidas):
    motivos = _motivos(vidas, True)
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    ruim = copy.deepcopy(motivos)
    ruim[3]["cadeia"]["intervalo"]["delta"]["energia"] += 1
    with pytest.raises(R.RastroDivergiu, match="C-FECHO"):
        R.conferir_rastro(ruim, passo)
    ruim = copy.deepcopy(motivos)
    ruim[5]["cadeia"]["intervalo"]["ate"] = 5
    with pytest.raises(R.RastroDivergiu, match="C-UMA-VEZ"):
        R.conferir_rastro(ruim, passo)
    ruim = copy.deepcopy(motivos)
    ruim[5]["cadeia"]["intervalo"]["tick_ate"] += passo
    with pytest.raises(R.RastroDivergiu, match="C-UMA-VEZ"):
        R.conferir_rastro(ruim, passo)
    ruim = copy.deepcopy(motivos)
    del ruim[7]["cadeia"]
    with pytest.raises(R.RastroDivergiu, match="sem o rastro"):
        R.conferir_rastro(ruim, passo)
    with pytest.raises(R.RastroDivergiu):
        R.conferir_rastro(_motivos(vidas, False), passo)


# ------------------------------------------------------------------ o texto
def _cadeia(k, acao, dt, di, r=0, r_int=0, gestos=(), p1=None, p2=(), episodio=None, termos=None, reflexo=False):
    return {"id": k, "tick": 15 * k, "acao": acao, "reflexo": reflexo, "leitura": {},
            "mesmo_tick": {"r": r, "r_n": r // 2, "canais": {"fome": r, "energia": 0}, "delta": dt},
            "intervalo": {"r": r_int, "r_n": r_int // 2, "canais": {"fome": 0, "energia": r_int}, "delta": di, "de": k, "ate": k + 1,
                          "tick_de": 15 * k, "tick_ate": 15 * k + 15, "ja_contado": False},
            "gestos": [list(g) for g in gestos],
            "atualizacoes": {"p1": p1, "p2": list(p2), "episodio": episodio, "autobio": None},
            "pesou": {"termos": termos or {"inato": 10}, "sondas": None, "memoria": None, "lembranca": None}}


CONSUMO = _cadeia(0, "comer", {"fome": 400, "energia": -8}, {"fome": -12, "energia": -20}, r=100, r_int=-40, gestos=[("alimentar", 15)],
                  p1={"regra": "P1", "classe": "racao"}, p2=[{"regra": "P2", "b": "comer", "r_n": 50}], episodio=3,
                  termos={"inato": 400, "prox": 200})
SONO = _cadeia(1, "dormir", {"fome": 0, "energia": 0}, {"fome": -12, "energia": 60}, r=0, r_int=80, reflexo=True)
TROCA = _cadeia(2, "explorar", {"fome": 0, "energia": -10}, {"fome": -12, "energia": -20}, r=-4, r_int=-40)


def test_o_texto_de_tres_decisoes():
    assert texto_cadeia(CONSUMO) == ("decisao 0: comer (pesou o inato, a proximidade); no mesmo tick: fome +400, energia -8 "
                                     "(r 100); ate a decisao seguinte: energia -20, fome -12 (r -40); o dono: alimentar; aprendeu: o P1 da "
                                     "classe racao, o P2 do comer (r_n 50), o episodio 3")
    assert texto_cadeia(SONO) == ("decisao 1: dormir (pelo reflexo); no mesmo tick: nada (r 0); ate a decisao seguinte: energia +60, "
                                  "fome -12 (r 80); nenhum gesto do dono; nenhum aprendizado")
    assert texto_cadeia(TROCA).startswith("decisao 2: explorar (pesou o inato); no mesmo tick: energia -10 (r -4)")
    with pytest.raises(ValueError, match="sem o campo"):
        texto_cadeia({k: v for k, v in SONO.items() if k != "intervalo"})
    with pytest.raises(ValueError, match="termo sem nome"):
        texto_cadeia({**TROCA, "pesou": {"termos": {"outro": 5}}})


def test_o_texto_da_vida(vidas):
    motivos = _motivos(vidas, True)
    linhas = texto_da_vida(motivos)
    assert len(linhas) == len(motivos) - 1
    assert any("aprendeu: o P1 da classe racao" in x for x in linhas)
    assert any(": dormir (" in x and "no mesmo tick: nada (r 0)" in x and "energia +" in x for x in linhas)
    assert texto_da_vida(_motivos(vidas, False)) == []


# ------------------------------------------------------------------ as medidas
def _motivo(k, comportamento, cadeia=None, reflexo=False, fins=()):
    m = {"k": k, "escolha": [comportamento, None, None], "reflexo": reflexo, "fins": list(fins)}
    if cadeia is not None:
        m["cadeia"] = cadeia
    return m


def test_as_medidas_num_caso_feito_a_mao():
    motivos = [_motivo(0, "comer", CONSUMO), _motivo(1, "dormir", SONO, reflexo=True, fins=[{"motivo": "meta"}]),
               _motivo(2, "explorar", TROCA), _motivo(3, "explorar")]
    r = met.medidas_rastro(motivos)
    assert r["n"] == 3
    # M-FORA: a fome 400 no tick e 36 no intervalo; a energia 18 no tick e 100 no intervalo
    assert r["fora"]["receptores"]["fome"] == {"tick": 400, "intervalo": 36, "F": 36 / 436}
    assert r["fora"]["receptores"]["energia"] == {"tick": 18, "intervalo": 100, "F": 100 / 118}
    # no sinal: |100| + |0| + |-4| no tick (o canal fome) e |-40| + |80| + |-40| no intervalo (o canal energia)
    assert (r["fora"]["sinal_tick"], r["fora"]["sinal_intervalo"], r["fora"]["F_sinal"]) == (104, 160, 160 / 264)
    assert (r["fora"]["soma_r"], r["fora"]["soma_r_int"]) == (96, 0)
    # M-ACAO: os r_n do intervalo sao -20 (comer), 40 (dormir) e -20 (explorar); a media 0; acordado -20, dormindo 40
    a = r["acao"]
    assert a["media_r_int_n"] == 0 and a["media_contexto"] == {"acordado": -20.0, "dormindo": 40.0}
    assert a["por_comportamento"]["dormir"] == {"n": 1, "r_int_n": 40.0, "resto_global": 40.0, "resto_contexto": 0.0}
    assert a["por_comportamento"]["comer"]["resto_global"] == -20.0 and a["por_comportamento"]["comer"]["resto_contexto"] == 0.0
    assert a["eta2_global"] == 1.0          # cada comportamento tem uma decisao: toda a variancia fica entre eles
    assert a["eta2_contexto"] is None       # tirada a media do contexto, nada sobra
    assert a["dormir_r_tick_nao_zero"] == 0.0
    # M-DONO: um intervalo em tres com gesto
    assert r["dono"] == {"fracao_com_gesto": 1 / 3, "r_int_n_com": -20.0, "r_int_n_sem": 10.0,
                         "por_gesto": {"alimentar": {"n": 1, "r_int_n": -20.0}}}
    # M-TROCA: comer, dormir, explorar, explorar: 3 intencoes em 4 decisoes, 2 trocas, uma delas no reflexo
    t = r["troca"]
    assert (t["decisoes"], t["intencoes"], t["duracao_media"], t["fracao_trocas"], t["trocas_pelo_reflexo"]) == (4, 3, 4 / 3, 2 / 3, 0.5)
    assert t["duracao"] == {"1": 2 / 3, "2": 1 / 3, "3": 0.0, "4+": 0.0} and t["fins"] == {"meta": 1}
    # M-MUDA: a fome muda no tick em 1 de 3 decisoes e no intervalo em todas
    assert r["muda"]["fome"] == {"tick": 1 / 3, "intervalo": 1.0}
    with pytest.raises(ValueError, match="sem nenhuma decisao com o rastro"):
        met.medidas_rastro([_motivo(0, "comer")])


def test_o_eta2_separa_o_sono_do_resto():
    # dois comportamentos acordados com o mesmo intervalo, e o sono diferente: o eta2 global e 1 e o por contexto nao existe
    def c(k, acao, r_int):
        return _cadeia(k, acao, {"fome": 0}, {"fome": 0}, r_int=r_int)
    motivos = [_motivo(k, b, c(k, b, v)) for k, (b, v) in enumerate([("comer", -20), ("explorar", -20), ("dormir", 60), ("dormir", 60)])]
    a = met.medidas_rastro(motivos + [_motivo(4, "ocioso")])["acao"]
    assert a["eta2_global"] == 1.0 and a["eta2_contexto"] is None
    # agora os acordados diferem entre si: o eta2 por contexto aparece
    motivos = [_motivo(k, b, c(k, b, v)) for k, (b, v) in enumerate([("comer", -40), ("comer", -40), ("explorar", 0), ("explorar", 0),
                                                                       ("dormir", 60), ("dormir", 20)])]
    a = met.medidas_rastro(motivos + [_motivo(6, "ocioso")])["acao"]
    # os restos por contexto: comer -10, -10; explorar +10, +10; dormir +10, -10 -> entre 400 de 600
    assert a["eta2_contexto"] == pytest.approx(400 / 600)


def test_as_medidas_de_uma_vida(vidas):
    r = met.medidas_rastro(_motivos(vidas, True))
    assert r["n"] == DIAS * 96 - 1 and r["troca"]["decisoes"] == DIAS * 96
    assert 0 < r["fora"]["F_sinal"] < 1 and r["acao"]["dormir_r_tick_nao_zero"] == 0.0
    assert abs(sum(r["troca"]["duracao"].values()) - 1) < 1e-12
    assert json.loads(json.dumps(r)) == r


# ------------------------------------------------------------------ o replay
def _gravada(vidas):
    motor, registro, _, _ = vidas[False]
    c = orq.cerebro_de(registro)
    return json.loads(json.dumps({**orq.medidas(motor, registro, "REL", DIAS, True),
                                  "pv2": met.medidas_pv2(c.motivos, motor.consumos_mundo, False, c.S), "custo": {"x": 1}}))


def test_o_replay_de_uma_vida_confere_e_sai_igual(vidas):
    texto = vidas[False][0].log.para_jsonl()
    gravada = _gravada(vidas)
    a = R.rejogar(DIAS, R.ORCAMENTO_POR_DIA, "run", "HOJE", "atencioso", "comedouro", UNIDADE, texto, gravada)
    b = R.rejogar(DIAS, R.ORCAMENTO_POR_DIA, "run", "HOJE", "atencioso", "comedouro", UNIDADE, texto, gravada)
    a.pop("custo"), b.pop("custo")
    assert bv._dump(a) == bv._dump(b)                                    # C-IGUAL
    assert a["rastro"] == met.medidas_rastro(_motivos(vidas, True))      # o replay da as medidas da vida vivida com o rastro
    so = R.rejogar(DIAS, R.ORCAMENTO_POR_DIA, "run", "HOJE", "atencioso", "comedouro", UNIDADE, texto, gravada, so_g1=True)
    assert "rastro" not in so


def test_o_replay_falha_alto(vidas):
    texto = vidas[False][0].log.para_jsonl()
    gravada = _gravada(vidas)
    with pytest.raises(R.RastroDivergiu, match="C-G1"):
        R.rejogar(DIAS, R.ORCAMENTO_POR_DIA, "run", "HOJE", "atencioso", "comedouro", UNIDADE, texto, {**gravada, "reflexos": -1})
    with pytest.raises(R.RastroDivergiu, match="C-G1"):                  # a vida de outra semente nao e a do log
        R.rejogar(DIAS, R.ORCAMENTO_POR_DIA, "run", "HOJE", "atencioso", "comedouro", {**UNIDADE, "semente": 202}, texto, gravada)


def test_a_fonte_falha_alto(tmp_path):
    falso = tmp_path / "vidas.tar.gz"
    with pytest.raises(FileNotFoundError, match="C-FONTE"):
        R.conferir_fonte(falso)
    falso.write_bytes(b"outra coisa")
    with pytest.raises(R.RastroDivergiu, match="C-FONTE"):
        R.conferir_fonte(falso)


# ------------------------------------------------------------------ a trava e a analise
def test_a_config_e_a_do_plano():
    R.conferir_config(CFG)
    assert CFG["plano"] == R.PLANO and tuple(CFG["unidades"]["bases"]) == R.BASES
    for mudar in ({"dias": 13}, {"fase": "outra"}, {"orcamento_por_dia": 8}, {"plano": "docs/outro.md"},
                  {"unidades": {**CFG["unidades"], "bases": [101]}}, {"unidades": {**CFG["unidades"], "k": 8}}):
        with pytest.raises(ValueError):
            R.conferir_config({**CFG, **mudar})
    with pytest.raises(ValueError, match="sobram"):
        R.conferir_config({**CFG, "outra": 1})


def test_a_trava(tmp_path):
    R.exigir_aprovado((RAIZ / R.PLANO).read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="APROVADO"):
        R.exigir_aprovado("**Status: PROPOSTO, aguardando o Matheus.**\n")
    with pytest.raises(ValueError, match="processos"):
        R.rodar(CFG, tmp_path / "x", 5, tmp_path / "vidas.tar.gz")
    (tmp_path / "existe").mkdir()
    with pytest.raises(FileExistsError):
        R.rodar(CFG, tmp_path / "existe", 1, tmp_path / "vidas.tar.gz")


def test_o_numero_de_vidas():
    unidades = bv.unidades_derivadas(list(R.BASES), R.K_POR_BASE, R.PREFIXO)
    vidas = R.vidas_esperadas(unidades)
    # 200 unidades x 12 celulas no HOJE e no OLF-0, mais 40 unidades x 8 celulas do HOJE do v38
    assert len(vidas) == 2400 + 2400 + 320 == 5120
    assert len({R.nome_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}) == 5120
    assert all(R.NOME_VIDA.match(R.membro_da_vida(g, b, d, lugar, u["semente"])) for g, b, d, lugar, u in vidas[:50])


def _resumos(f, g, c):
    """os resumos do HOJE nos 3 lugares, com o IC (inferior, superior) de cada medida da regra"""
    def med(par):
        return {"ic_inferior": par[0], "ic_superior": par[1]}
    return {f"run|HOJE|{lugar}": {"medidas": {"F_sinal": med(f), "eta2_global": med(g), "eta2_contexto": med(c)}} for lugar in R.LUGARES}


def test_a_regra_de_leitura():
    def lei(f, g, c):
        x = R.leitura(_resumos(f, g, c))
        return x["L-FORA"]["leitura"], x["L-ACAO"]["leitura"]
    assert lei((0.6, 0.7), (0.3, 0.4), (0.1, 0.2)) == ("a maior parte do sinal esta fora do r",
                                                        "o intervalo distingue a acao mesmo acordado")
    assert lei((0.1, 0.2), (0.3, 0.4), (0.01, 0.04)) == ("o intervalo e pequeno",
                                                          "o sinal do intervalo e o sono, e a linha de base por contexto o apaga")
    assert lei((0.3, 0.6), (0.0, 0.04), (0.0, 0.04)) == ("parte do sinal esta fora", "o intervalo e decaimento igual para toda acao")
    assert lei((0.3, 0.6), (0.3, 0.4), (0.04, 0.06))[1] == "indeterminado"
    with pytest.raises(R.RastroDivergiu, match="sem o IC"):
        R.leitura(_resumos((None, None), (0.3, 0.4), (0.1, 0.2)))


def test_o_resumo_por_unidade(vidas):
    rastro = met.medidas_rastro(_motivos(vidas, True))
    registros = [{"grupo": "run", "braco": "HOJE", "lugar": "comedouro", "dono": d, "semente": s, "rastro": rastro}
                 for s in (101, 202, 303) for d in ("atencioso", "relapso")]
    r = R.resumo(registros, "run", "HOJE", "comedouro")
    assert (r["vidas"], r["unidades"]) == (6, 3)
    f = r["medidas"]["F_sinal"]
    assert f["n"] == 3 and f["media"] == pytest.approx(rastro["fora"]["F_sinal"]) and set(f["por_dono"]) == {"atencioso", "relapso"}
    with pytest.raises(R.RastroDivergiu, match="nenhuma vida"):         # a analise falha alto sem um conjunto ou um lugar
        R.analisar(registros)
    todos = [{**x, "grupo": g, "braco": b, "lugar": lugar} for x in registros for g, b in R.CONJUNTOS for lugar in R.lugares_do(g)]
    a = R.analisar(todos)
    assert len(a["resumos"]) == 3 + 3 + 2 and set(a["leitura"]) == {"L-FORA", "L-ACAO", "nao_demonstra"}
