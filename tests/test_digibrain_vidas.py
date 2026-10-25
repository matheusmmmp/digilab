"""O DigiBrain modular nas vidas do motor, etapa 1a (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.1, 10 e 11; o plano do prototipo,
secoes 5.1 e 10):
  - G1: o replay bit a bit numa vida com a chave ligada, em cada braco do modular (o M4-emb com a serie do doador, o M4-con com o g_apr
    fixo) e no A11; o T-MEM-1 pelo replay (os mesmos episodios);
  - T-CADEIA-1 (o oraculo, D3): o cenario do MVP com os valores de partida, fome alta e a racao a 2 celulas; a fracao das escolhas de
    comer na grade de u e o peso dela sobre a soma, e com a escolha o pet come na mesma decisao;
  - T-PONTO-1: o `Alvo.ponto` so em EXPLORAR e so com o M-MEM tendo recuperado um lugar; fora disso, o alvo fora dos candidatos levanta;
  - T-PONTO-2: o `ponto` fora do mapa ou nao inteiro levanta no motor (o comportamento de hoje, mundo.py:1415-1422);
  - T-PONTO-3: o G2 das 196 vidas e o tests/test_gabarito_digibrain.py (inalterado); aqui, que nada fora do pacote e do orquestrador do
    prototipo monta o DigiBrain;
  - o orquestrador (experiments/run_v2_digibrain_prototipo.py): a config segue o plano, os doadores, a fumaca de ponta a ponta e as
    medidas novas de metrics.py."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.digibrain import Intencao  # noqa: E402
from digilab.digibrain.arb import sortear_inteiro  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.metrics import (cadeia_comida_corpo, centro_temporal, entropia_acoes, falta_ao_comer, influencia_por_modulo,  # noqa: E402
                             intencoes_com_meta, media_absoluta, pesos_no_teto, repeticao_apos_alivio)
from digilab.mundo import Alvo  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_digibrain_prototipo"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / nome).read_text(encoding="utf-8"))


# ================================================================== G1 e T-MEM-1
@pytest.mark.parametrize("braco", ["M0", "M1", "M2", "M3", "M3-sp", "M4", "A11"])
def test_g1_o_replay_bit_a_bit(braco):
    motor, reg, fab = orq.viver(braco, "relapso", "comedouro", 101, 2, 16)
    orq.conferir_replay(motor, fab, 101, motor.log.para_jsonl())
    if braco != "A11":
        orq.conferir_mecanismo(braco, reg, None)
        assert len(orq.cerebro_de(reg).motivos) == 2 * 96


def test_g1_o_m4_emb_e_o_m4_con_e_o_t_mem_1_no_replay():
    motor, reg, _ = orq.viver("M4", "atencioso", "comedouro", 202, 2, 16)
    serie = tuple(orq.cerebro_de(reg).m.afeto.serie_e)
    assert len(serie) == 2 * 96 and any(serie)
    m_emb, r_emb, fab = orq.viver("M4-emb", "atencioso", "comedouro", 101, 2, 16, serie_e=serie)
    orq.conferir_replay(m_emb, fab, 101, m_emb.log.para_jsonl())
    orq.conferir_mecanismo("M4-emb", r_emb, serie)
    m_con, r_con, fab = orq.viver("M4-con", "atencioso", "comedouro", 101, 2, 16, g_apr_con=1300)
    orq.conferir_replay(m_con, fab, 101, m_con.log.para_jsonl())
    assert {m["afeto"]["g_apr"] for m in orq.cerebro_de(r_con).motivos} == {1300}
    with pytest.raises(RuntimeError, match="doadora"):
        orq.viver("M4-emb", "atencioso", "comedouro", 101, 2, 16, serie_e=serie[:10])
    # T-MEM-1: os consumos viram episodios, e o replay os refaz iguais
    motor, reg, fab = orq.viver("M3", "atencioso", "comedouro", 101, 2, 16)
    c = orq.cerebro_de(reg)
    comidas = [m for m in c.motivos if m["consequencia"] is not None and m["consequencia"]["comeu"] is not None]
    assert comidas and c.m.mem.proximo_id == len(comidas)
    fp, fm = fab
    r = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(motor.log.para_jsonl()), fp, semente=101, fabrica_motor=fm)
    assert r.politica.estado_interno()["modulos"]["mem"] == c.m.mem.estado_interno()


# ================================================================== T-CADEIA-1
class _RngFixa:
    def __init__(self, u: float) -> None:
        self.u, self.n = u, 0

    def random(self) -> float:
        self.n += 1
        return self.u


def _faminto():
    """um pet M0 sem comida ate a falta da fome passar de 600 com a energia acima do reflexo; a racao posta a 2 celulas a leste"""
    fp, fm = orq.fabricas("M0", "atencioso", 101, 1, 16)
    reg = fp(CONFIG_PADRAO)
    motor = fm(reg, CONFIG_PADRAO, 101)
    c = orq.cerebro_de(reg)
    while not (c.motivos and c.motivos[-1]["falta_fome"] > 600):
        motor.avancar(15)
    energia = motor.corpo.receptores()["energia"]
    assert energia > c.inatos.lambda_sono
    x, y = motor.pet
    motor.deixar_comida("racao", x + 32, y)
    return motor, reg, c


def test_t_cadeia_1_o_oraculo_no_mvp():
    motor, reg, c = _faminto()
    motor.avancar(15)
    m = c.motivos[-1]
    us = m["unidades"]
    comer = next(i for i, u in enumerate(us) if u["chave"][:2] == ["comer", "comida"])
    w = [u["w"] for u in us]
    assert w[comer] > 0 and sum(1 for x in w if x > 0) >= 2
    grade = [(i + 0.5) / 1000 for i in range(1000)]
    frac = sum(1 for u in grade if sortear_inteiro(w, u) == comer) / len(grade)
    assert abs(frac - w[comer] / sum(w)) <= 1 / 1000 + 1e-12
    assert w[comer] == max(w)                                          # com fome alta e a racao perto, comer e a maior
    # com a escolha (um u no meio do intervalo de comer), o pet come na mesma decisao: o alcance de 60 subunidades cobre 2 celulas
    motor2, reg2, c2 = _faminto()
    u = (sum(w[:comer]) + w[comer] / 2) / sum(w)
    motor2._rng_politica = _RngFixa(u)
    n = len(motor2.consumos_mundo)
    motor2.avancar(15)
    m2 = c2.motivos[-1]
    assert m2["unidades"] == us and m2["acao"] == "comer" and m2["u"] == u
    assert len(motor2.consumos_mundo) == n + 1 and motor2.consumos_mundo[-1]["tipo"] == "racao"
    motor2.avancar(15)
    assert c2.motivos[-2]["consequencia"]["comeu"]["como"] == "comer" and c2.motivos[-2]["consequencia"]["r"] > 0


# ================================================================== T-PONTO
def test_t_ponto_1_o_ponto_so_em_explorar_e_so_com_a_memoria():
    motor, reg, _ = orq.viver("M3", "relapso", "longe", 101, 14, 16)
    c = orq.cerebro_de(reg)
    pontos = [m for m in c.motivos if m.get("alvo", {}).get("tipo") == "ponto"]
    assert pontos, "a vida de teste nao foi ao lugar lembrado nenhuma vez"
    for m in pontos:
        assert m["acao"] == "explorar" and m["alvo"]["do_mem"] and m["memoria"]["recuperado"] is not None
        assert m["escolha"][:2] == ["explorar", "ponto"] and m["escolha"][2] == [m["alvo"]["x"], m["alvo"]["y"]]
    assert all(m.get("alvo", {}).get("do_mem") is False for m in c.motivos if "alvo" in m and m["alvo"]["tipo"] != "ponto")
    sem = [m for m in c.motivos if m["memoria"] is not None and m["memoria"]["recuperado"] is None]
    assert sem and not any(u["chave"][1] == "ponto" for m in sem for u in m["unidades"])   # sem lugar recuperado, sem a unidade
    # sem o M-MEM, nunca um ponto
    _, reg2, _ = orq.viver("M2", "relapso", "longe", 101, 3, 16)
    assert not any(m.get("alvo", {}).get("tipo") == "ponto" for m in orq.cerebro_de(reg2).motivos)
    # o adaptador: fora do explorar, o alvo fora dos candidatos levanta
    c3 = orq.cerebro_de(orq.fabricas("M3", "atencioso", 101, 1, 16)[0](CONFIG_PADRAO))
    for intencao, cands in ((Intencao(AcaoPet.COMER, "comida", 3), [Alvo("comida", 1, 1, 4)]),
                            (Intencao(AcaoPet.BRINCAR, "bola", 0), [Alvo("comida", 1, 1, 4)])):
        c3._pendencia = {"intencao": intencao, "pediu": False}
        c3.motivos.append({})
        with pytest.raises(ValueError, match="nao esta entre os candidatos"):
            c3.escolher_alvo(intencao.acao, cands, None, 0)
    c3._pendencia = {"intencao": Intencao(AcaoPet.EXPLORAR, "ponto", None, (300, 200)), "pediu": False}
    assert c3.escolher_alvo(AcaoPet.EXPLORAR, [Alvo("vagar", 5, 5)], None, 0) == Alvo.ponto(300, 200)


def test_t_ponto_2_o_motor_valida_o_ponto():
    fp, fm = orq.fabricas("M3", "atencioso", 101, 1, 16)
    motor = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    cands = [Alvo("vagar", 5, 5)]
    motor._validar_alvo(AcaoPet.EXPLORAR, Alvo.ponto(300, 200), cands)               # dentro do mapa: aceito
    for x, y in ((-1, 5), (5, 480), (1024, 5), (1.5, 5), (5, 2.0)):
        with pytest.raises(ValueError, match="ponto fora do mapa ou nao inteiro"):
            motor._validar_alvo(AcaoPet.EXPLORAR, Alvo.ponto(x, y), cands)
    for acao in (AcaoPet.COMER, AcaoPet.BRINCAR):
        with pytest.raises(ValueError, match="alvo fora dos candidatos"):
            motor._validar_alvo(acao, Alvo.ponto(300, 200), cands)
    with pytest.raises(ValueError, match="alvo fora dos candidatos"):                # os outros alvos nao relaxam
        motor._validar_alvo(AcaoPet.EXPLORAR, Alvo("vagar", 6, 6), cands)


def test_t_ponto_3_so_o_orquestrador_do_prototipo_monta_o_digibrain():
    """o G2 das 196 vidas e o tests/test_gabarito_digibrain.py, que passa sem mudanca; aqui, o resto: nenhum modulo do motor, da bancada
    nem das ferramentas cita o pacote (e o explorar do motor nao ganha candidato)"""
    nomes = re.compile(r"digilab\.digibrain|from \.digibrain|from \.\.digibrain|import digibrain")
    citam = {p.relative_to(RAIZ).as_posix() for pasta in ("digilab", "experiments", "tools") for p in (RAIZ / pasta).rglob("*.py")
             if nomes.search(p.read_text(encoding="utf-8"))}
    assert {c for c in citam if not c.startswith("digilab/digibrain/")} == {"experiments/run_v2_digibrain_prototipo.py"}
    assert "lembranca" not in (RAIZ / "digilab" / "mundo.py").read_text(encoding="utf-8")


# ================================================================== o orquestrador
def test_a_config_segue_o_plano():
    for nome in ("fumaca_calibracao.json", "fumaca_piloto.json", "fumaca_avaliacao.json"):
        assert orq.modo_da_config(_cfg(nome)) == "fumaca"
    assert orq.modo_da_config(_cfg("calibracao.json")) == "calibracao"
    if "## Adendo 1" not in (RAIZ / orq.PLANO).read_text(encoding="utf-8"):
        with pytest.raises(RuntimeError, match="adendo 1"):
            orq.modo_da_config(_cfg("piloto.json"))
    with pytest.raises(ValueError, match="fora do plano"):
        orq.modo_da_config({**_cfg("calibracao.json"), "poder": {**orq.PODER, "replicas": 20}})
    with pytest.raises(ValueError, match="fora do plano"):
        orq.modo_da_config({**_cfg("calibracao.json"), "rodada": 4})
    with pytest.raises(ValueError, match="dias"):
        orq.modo_da_config({**_cfg("calibracao.json"), "dias": 2})
    with pytest.raises(bv.SementeSemPlano):
        orq.modo_da_config({**_cfg("calibracao.json"), "unidades": {"bases": [64101, 64202], "k": 2, "prefixo": orq.PREFIXO}})
    with pytest.raises(bv.SementeSemPlano):
        orq.modo_da_config({**_cfg("calibracao.json"), "unidades": {"bases": [12345], "k": 2, "prefixo": orq.PREFIXO}})
    if not (RAIZ / orq.SAIDA["piloto"] / "resultado.json").exists():
        with pytest.raises(FileNotFoundError):
            orq.modo_da_config({**{k: v for k, v in _cfg("calibracao.json").items() if k != "rodada"}, "fase": "avaliacao",
                                "unidades": {"bases": list(orq.BASES["avaliacao"]), "k": 4, "prefixo": orq.PREFIXO}})
    assert orq.PREFIXO in bv.PREFIXOS_UNIDADES and orq.BRACOS == ("M0", "M1", "M2", "M3", "M3-sp", "M4", "M4-emb", "M4-con", "A11")
    assert len(orq.CELULAS) == 12


def test_os_doadores_do_m4_emb():
    us = bv.unidades_derivadas([101, 202], 3, orq.PREFIXO)
    d = orq.doadores(us)
    por = {(u["base"], u["k"]): u["semente"] for u in us}
    for b in (101, 202):
        assert [d[por[(b, k)]] for k in range(3)] == [por[(b, 1)], por[(b, 2)], por[(b, 0)]]


def test_a_fumaca_de_ponta_a_ponta(tmp_path):
    """a fumaca da avaliacao (2 unidades x 9 bracos x 12 celulas, 2 dias): as vidas gravadas e rejogadas do disco, as falhas altas, as
    medidas, os gates; e a analise do piloto e da calibracao sobre os mesmos registros"""
    cfg = _cfg("fumaca_avaliacao.json")
    r = orq.rodar(cfg, tmp_path / "avaliacao", processos=2)
    regs = r["registros"]
    assert len(regs) == 2 * len(orq.CELULAS) * len(orq.BRACOS)
    assert len(list((tmp_path / "avaliacao" / "vidas").rglob("*.jsonl"))) == len(regs)
    res = r["resultado"]
    assert set(res["G-ABLA"]) == set(orq.FAMILIA_ABLA) and set(res["G-MOD"]) == set(orq.FAMILIA_MOD)
    assert {"G-MVP", "G-ELEGIVEL", "G-PESA", "comparacao_com_o_a", "D-1", "D-2", "leitura", "custo"} <= set(res)
    assert [res["G-ABLA"][g]["holm"]["limiar"] for g in sorted(res["G-ABLA"], key=lambda g: res["G-ABLA"][g]["holm"]["ordem"])] == \
        [0.05 / 4, 0.05 / 3, 0.05 / 2, 0.05]
    assert r["meta"]["g_apr_m4_con"] > 0
    pil = orq.analisar_piloto([x for x in regs if x["braco"] != "A11"], {**cfg, "poder": {**orq.PODER, "replicas": 10,
                                                                                            "reamostragens_internas": 20, "k_max": 4}})
    assert pil["n"]["k"] == 4 and pil["g_apr_m4"]["m4_con"] > 0
    cal = orq.analisar_calibracao(regs, {**cfg, "rodada": 1})
    assert set(cal["criterios"]) == {"taxa_mediana", "pesos_no_teto", "g_pesa"}
    with pytest.raises(FileExistsError):
        orq.rodar(cfg, tmp_path / "avaliacao", processos=1)


# ================================================================== as medidas novas (metrics.py)
def test_a_cadeia_comida_corpo():
    racoes = [(1, 100, 0.3), (2, 400, 0.3), (3, 700, 0.8), (4, 900, None), (5, 1000, 0.2)]
    consumos = [(1, 150, "racao", 600, 200), (2, 600, "racao", 600, 200), (3, 720, "racao", 100, 50), (5, 1005, "racao", 500, 500)]
    c = cadeia_comida_corpo(racoes, consumos, 2)
    assert c == {"elegiveis": 3, "fechadas": 1, "taxa": 1 / 3, "latencias": [50], "sem_decisao": 1, "refeicoes_por_dia": 2.0}
    assert cadeia_comida_corpo([(1, 0, 0.9)], [], 1)["taxa"] is None
    with pytest.raises(ValueError, match="duas vezes"):
        cadeia_comida_corpo([], [(1, 0, "racao", 1, 0), (1, 15, "racao", 1, 0)], 1)


def test_as_outras_medidas_novas():
    ds = [(0, {"incentivo": True, "habito": False}), (15, {"incentivo": False, "habito": False}), (1440, {"incentivo": True, "habito": True})]
    i = influencia_por_modulo(ds, (0, 2880), ("incentivo", "habito"))
    assert i["frac"] == {"incentivo": 2 / 3, "habito": 1 / 3} and i["por_dia"] == {"incentivo": [0.5, 1.0], "habito": [0.0, 1.0]}
    with pytest.raises(ValueError):
        influencia_por_modulo([(0, {"incentivo": True})], (0, 1440), ("incentivo", "habito"))
    assert falta_ao_comer([(0, True, 0.4), (15, False, 0.9), (30, True, 0.2)], (0, 45)) == {"n": 2, "media": pytest.approx(0.3)}
    assert falta_ao_comer([(0, False, 0.4)], (0, 45))["media"] is None
    rep = repeticao_apos_alivio([(0, "a", "comer", 10), (15, "a", "comer", -5), (30, "a", "dormir", 0), (45, "b", "x", 3),
                                 (60, "a", "dormir", None), (75, "b", "x", 1)], (0, 90))
    assert (rep["n_pos"], rep["n_nao_pos"], rep["p_pos"], rep["p_nao_pos"]) == (2, 2, 1.0, 0.5) and rep["indice"] == 0.5
    assert intencoes_com_meta([(0, True), (15, False), (3000, True)], (0, 1440)) == {"n": 2, "frac": 0.5}
    assert pesos_no_teto([512, -512, 3, 0], 512) == 0.5
    with pytest.raises(ValueError):
        pesos_no_teto([600], 512)
    assert centro_temporal([0.0, 1.0, 1.0]) == 2.5 and centro_temporal([0, 0]) is None
    assert entropia_acoes(["a", "a", "b", "b"]) == 1.0 and entropia_acoes([]) is None
    assert media_absoluta([-2, 4]) == 3.0 and media_absoluta([]) is None
