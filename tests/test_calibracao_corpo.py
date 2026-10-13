"""V2, CORPO-CALIBRACAO: o orquestrador da calibracao do corpo (experiments/run_v2_calibracao_corpo.py; PLANO_ANALISE_V2_CORPO_DRIVES,
secoes 6 e 7 e adendos 1 a 3), so com as sementes dos testes.

O que se confere:
- os numeros de cada ponto da grade (6.1): as subidas x m_sobe (o divisor do estresse / m_sobe), as reducoes x m_reduz, o gasto do
  passo 0 fixo; a config recusa as bases da validacao e um corpo que nao seja o do passo 0;
- a regra da grade (6.2) em dados com a resposta conhecida: a faixa com os dois mundos juntos, o mais perto de (1, 1), o empate no menor
  m_sobe, o "nao fechou" pelo centro; o w_novos pela mediana da parcela;
- as margens da secao 7 e o poder (os efeitos, a nao inferioridade e a equivalencia) em dados com a resposta conhecida;
- a medida dos efeitos do tapa (5.4) em dados conhecidos;
- a fumaca inteira (a grade, o piloto com todos os blocos, as sensibilidades, o N), com o replay do disco de toda vida.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_corpo as cc  # noqa: E402
from digilab.metrics import efeitos_do_tapa  # noqa: E402

FUMACA = RAIZ / "experiments" / "configs" / "v2_corpo" / "fumaca_calibracao.json"


def _fumaca() -> dict:
    return json.loads(FUMACA.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ 1. a grade e a config


def test_os_numeros_de_cada_ponto():
    cfg = _fumaca()
    meio = cc.corpo_do_ponto(cfg, 0.5, 0.5)
    assert (meio["tedio_sobe"], meio["solidao_sobe"], meio["estresse_divisor"]) == (225, 113, 512)     # 225/2 = 112,5 -> 113
    assert (meio["tedio_bola"], meio["tedio_brincar"], meio["tedio_explorar"], meio["tedio_dono"]) == (67500, 22500, 45000, 45000)
    assert (meio["carinho_solidao"], meio["carinho_estresse"]) == (90000, 45000)
    um = cc.corpo_do_ponto(cfg, 1.0, 1.0)
    assert (um["tedio_sobe"], um["solidao_sobe"], um["estresse_divisor"], um["tedio_bola"], um["carinho_solidao"]) == \
        (450, 225, 256, 135000, 180000)
    dois = cc.corpo_do_ponto(cfg, 2.0, 2.0)
    assert (dois["tedio_sobe"], dois["solidao_sobe"], dois["estresse_divisor"], dois["tedio_bola"], dois["carinho_estresse"]) == \
        (900, 450, 128, 270000, 180000)
    for p in (meio, um, dois):                           # o gasto do passo 0 fica fixo, e a config de cada ponto valida
        assert {k: p[k] for k in cc.CAMPOS_PASSO0} == cfg["corpo"]
        cc.config_bancada(cfg, p, ["P0-c"], ["bola", "padrao"])
    assert cc.nome_ponto(0.5, 2.0) == "sobe_0.5_reduz_2"


def test_a_config_recusa_o_que_nao_e_do_plano(tmp_path):
    cfg = _fumaca()
    assert cc.modo_da_config(cfg) == "fumaca"
    with pytest.raises(bv.SementeSemPlano):
        cc.modo_da_config({**cfg, "unidades": {"bases": [34101], "k": 1, "prefixo": "corpo"}})
    with pytest.raises(bv.SementeSemPlano):
        cc.modo_da_config({**cfg, "unidades": {"bases": [31101], "k": 1, "prefixo": "corpo"}})
    with pytest.raises(ValueError, match="prefixo"):
        cc.modo_da_config({**cfg, "unidades": {"bases": [101], "k": 1, "prefixo": "mundo"}})
    with pytest.raises(ValueError, match="corpo"):
        cc.modo_da_config({**cfg, "corpo": {**cfg["corpo"], "tedio_sobe": 1}})
    # a calibracao: o plano a letra, com o corpo do passo 0
    passo0 = tmp_path / "passo0.json"
    passo0.write_text(json.dumps({"escolha": {"corpo": {"gasto_basal_acordado": 188, "gasto_basal_dormindo": 94,
                                                         "gasto_atividades_num": 1, "gasto_atividades_den": 2}}}), encoding="utf-8")
    cal = {**cfg, "plano": cc.PLANO, "donos": list(cc.DONOS_V1), "unidades": {"bases": list(cc.BASES_CALIBRACAO), "k": 4, "prefixo": "corpo"},
           "dias": 14, "orcamento": 224, "bootstrap": {"reamostragens": 10000, "semente": 4242, "nivel": 0.95},
           "poder": {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8}, "passo0": str(passo0.relative_to(RAIZ))
           if passo0.is_relative_to(RAIZ) else str(passo0)}
    with pytest.raises(ValueError, match="passo 0"):
        cc.modo_da_config({**cal, "corpo": {"gasto_basal_acordado": 375, "gasto_basal_dormindo": 187, "gasto_atividades_num": 1,
                                              "gasto_atividades_den": 1}})
    assert cc.modo_da_config({**cal, "corpo": {"gasto_basal_acordado": 188, "gasto_basal_dormindo": 94,
                                                "gasto_atividades_num": 1, "gasto_atividades_den": 2}}) == "calibracao"
    with pytest.raises(ValueError, match="grade"):
        cc.modo_da_config({**cal, "corpo": {"gasto_basal_acordado": 188, "gasto_basal_dormindo": 94, "gasto_atividades_num": 1,
                                              "gasto_atividades_den": 2}, "grade": {**cal["grade"], "w_novos": [1, 2]}})


# ------------------------------------------------------------------ 2. a regra da grade (6.2)


def _reg(tedio, solidao, estresse, n=100, mundo="bola", braco="P0-c", pares=None):
    return {"braco": braco, "origem": None, "mundo": mundo, "novos_livres": pares,
            "drives": {"n_acordado": n, "tedio": {"media": 0.5, "acima": round(tedio * n)},
                       "solidao": {"media": 0.4, "acima": round(solidao * n)}, "estresse": {"media": 0.1, "acima": round(estresse * n)}}}


def test_a_faixa_junta_os_dois_mundos():
    f = cc.faixa_da_grade([_reg(0.05, 0.2, 0.0, mundo="bola"), _reg(0.25, 0.2, 0.0, mundo="padrao"), _reg(0.9, 0.9, 0.9, braco="P1-c")])
    assert f["tedio"] == pytest.approx(0.15) and f["solidao"] == pytest.approx(0.2) and f["passa"] and f["vidas"] == 2
    assert not cc.faixa_da_grade([_reg(0.2, 0.2, 0.25)])["passa"]          # o estresse acima de 0,20
    assert not cc.faixa_da_grade([_reg(0.6, 0.2, 0.0)])["passa"]           # o tedio acima de 0,50
    with pytest.raises(ValueError):
        cc.faixa_da_grade([{**_reg(0.2, 0.2, 0.0), "drives": None}])


def _f(t, s, e, passa):
    return {"tedio": t, "solidao": s, "estresse": e, "passa": passa}


def test_a_escolha_da_grade():
    todos = {(a, b): _f(0.9, 0.9, 0.9, False) for a in cc.GRADE_M for b in cc.GRADE_M}
    assert cc.escolha_da_grade({**todos, (1.0, 1.0): _f(0.3, 0.3, 0.0, True), (2.0, 2.0): _f(0.3, 0.3, 0.0, True)})["ponto"] == [1.0, 1.0]
    # empate de distancia (1/2, 1) e (2, 1): o menor m_sobe; (1, 2) tambem empata e perde para o (1/2, 1) pelo m_sobe
    e = cc.escolha_da_grade({**todos, (0.5, 1.0): _f(0.3, 0.3, 0.0, True), (2.0, 1.0): _f(0.3, 0.3, 0.0, True),
                             (1.0, 2.0): _f(0.3, 0.3, 0.0, True)})
    assert e["ponto"] == [0.5, 1.0] and e["fechou"]
    # nenhum passa: o mais perto do centro (0,30; 0,30; 0,10)
    perto = {**todos, (2.0, 0.5): _f(0.32, 0.29, 0.11, False)}
    e = cc.escolha_da_grade(perto)
    assert e["ponto"] == [2.0, 0.5] and not e["fechou"] and e["registro"] == "nao fechou"


def test_o_w_novos_pela_mediana_da_parcela():
    # A = novos, B = outros: com w = 1 a parcela 0,1; com w = 2, 2/11; com w = 4, 4/13 (passa)
    regs = [_reg(0.2, 0.2, 0.0, pares=[[1, 9]] * 5)]
    w = cc.escolha_w(regs)
    assert w["w_novos"] == 4 and w["fechou"] and w["medianas"]["4"] == pytest.approx(4 / 13)
    assert cc.escolha_w([_reg(0.2, 0.2, 0.0, pares=[[1, 1]] * 3)])["w_novos"] == 1                  # 0,5 ja no 1
    nao = cc.escolha_w([_reg(0.2, 0.2, 0.0, pares=[[1, 999]] * 3)])                                  # nunca chega a 0,25
    assert not nao["fechou"] and nao["w_novos"] == 4
    with pytest.raises(ValueError):
        cc.escolha_w([_reg(0.2, 0.2, 0.0, pares=[])])


# ------------------------------------------------------------------ 3. as margens e o poder (secao 7)


def _pil(s, dono, mundo, braco, be, priv=0.1, saude=0.8, ted=0.4):
    return {"ponto": "piloto", "semente": s, "dono": dono, "mundo": mundo, "braco": braco, "be": be, "privacao": priv, "saude": saude,
            "drives": {"tedio": {"media": ted}}}


def test_as_margens_pela_regra_registrada():
    regs = []
    for s in (1, 2):
        regs += [_pil(s, "a", "bola", "P0-q", 0.6, priv=0.2, saude=0.9), _pil(s, "a", "bola", "P1-q", 0.2),
                 _pil(s, "a", "bola", "P0-c", 0.6, ted=0.5), _pil(s, "a", "padrao", "P0-q", 0.0, priv=0.9, saude=0.0)]
    mg = cc.margens(regs)
    assert mg["delta_be"] == pytest.approx(0.2) and mg["delta_priv"] == pytest.approx(0.05)
    assert mg["delta_saude"] == pytest.approx(0.025) and mg["delta_ted"] == pytest.approx(0.25)
    assert mg["g_hoje"] == pytest.approx({"be": 0.1, "privacao": 0.025, "saude": 0.0125})


def test_o_poder_da_nao_inferioridade_e_da_equivalencia():
    col = [0.01 * ((-1) ** i) * (i % 3) for i in range(20)]
    larga = cc.poder_conjunto([col, col], 20, 200, 1, "t", cc.nao_inferior([1.0, 1.0]))
    estreita = cc.poder_conjunto([col, col], 20, 200, 1, "t", cc.nao_inferior([1e-6, 1e-6]))
    assert larga == 1.0 and estreita < 0.6
    assert cc.poder_conjunto([col], 20, 200, 1, "t", cc.equivalente([1.0])) == 1.0
    assert cc.poder_conjunto([col], 5, 200, 1, "t", cc.equivalente([1e-6])) < 0.5
    assert cc.poder_conjunto([[0.1]], 5, 10, 1, "t", cc.equivalente([1.0])) is None
    t = cc.tabela_k(lambda n: n / 50, {"k_min": 4, "k_max": 10, "alvo": 0.8}, 5)
    assert t["k"] == 8 and t["chega_ao_alvo"]
    t = cc.tabela_k(lambda n: 0.1, {"k_min": 4, "k_max": 10, "alvo": 0.8}, 5)
    assert t["k"] == 10 and not t["chega_ao_alvo"]


def test_os_efeitos_do_tapa():
    r = efeitos_do_tapa(tapas=[100, 1000], carinhos=[(50, 0.4, 10), (200, 0.1, -5), (700, 0.3, 4)],
                        decisoes=[(90, "ocioso"), (150, "chamar_atencao"), (300, "brincar"), (800, "chamar_atencao")],
                        estresse=[(90, 0.1), (150, 0.8), (300, 0.9), (1500, 0.2)], janela=(0, 2880), horas_depois=360)
    assert r["tapas"] == 2 and r["medo_da_mao"]["depois_tapa"] == {"n": 1, "reducao_solidao": 0.1}
    assert r["medo_da_mao"]["sem_tapa"]["n"] == 2 and r["medo_da_mao"]["sem_tapa"]["reducao_solidao"] == pytest.approx(0.35)
    assert r["chamar_atencao"]["depois_tapa"] == {"n": 2, "fracao": 0.5} and r["chamar_atencao"]["sem_tapa"]["fracao"] == 0.5
    assert r["carinho_sinal"] == {"depois_tapa": -5, "sem_tapa": 7}
    assert r["estresse_fim_do_dia"] == [{"dia": 1, "estresse": 0.9}, {"dia": 2, "estresse": 0.2}]
    assert r["estresse_acima"] == {"n": 4, "fracao": 0.5} and "nao disponivel" in r["vinculo"]
    with pytest.raises(ValueError):
        efeitos_do_tapa([], [(5, 0.1, 1), (1, 0.1, 1)], [], [], (0, 100))


# ------------------------------------------------------------------ 4. a fumaca inteira


def test_a_fumaca_inteira(tmp_path):
    saida = tmp_path / "cal"
    r = cc.rodar(_fumaca(), saida, 1, FUMACA)
    res = r["resultado"]
    assert set(res["faixas"]) == {cc.nome_ponto(a, b) for a in cc.GRADE_M for b in cc.GRADE_M}
    assert res["escolha"]["nome"] in res["faixas"] and res["w_novos"]["w_novos"] in cc.GRADE_W
    assert res["g_p0c"]["passa"]
    grade = r["medidas"]["grade"]
    assert sum(len(g) for g in grade.values()) == 9 * 2 * 2                  # 9 pontos x 2 unidades x 2 celulas, so o P0-c
    assert {x["braco"] for g in grade.values() for x in g.values()} == {"P0-c"}
    piloto = r["medidas"]["piloto"]
    bracos = {x["braco"] for x in piloto.values() if x["ponto"] == "piloto"}
    assert set(cc.BLOCO_G_HOJE) | set(cc.BLOCO_CORPO) | set(cc.BLOCO_TAPA) | set(cc.BLOCO_G) | set(cc.BLOCO_CW) | set(cc.ROT_AC.values()) == bracos
    por_unidade_piloto = sum(1 for x in piloto.values() if x["ponto"] == "piloto") / 2
    assert por_unidade_piloto == 6 * 2 + 6 * 2 + 2 + 2 + 2                   # um dono: G-HOJE, corpo com os acoplados, tapa, G, P1-cw
    assert {x["ponto"] for x in piloto.values()} == {"piloto", "tapa_-0.5", "tapa_-2", "janela_4", "janela_16"}
    sens = [x for x in piloto.values() if x["ponto"] != "piloto"]
    assert len(sens) == 2 * (2 + 2 * 2)                                       # por unidade: 2 tapas x 1 dono, 2 janelas x 2 mundos
    assert all(k.startswith(x["ponto"] + "|") for k, x in piloto.items() if x["ponto"] != "piloto")
    assert set(res["n"]["gates"]) == {"G-PARADO (PR-1)", "G-SEP (PR-3)", "G-PADRAO (PR-4)", "G-TED (PR-5)", "G-CUIDADO (PR-2)", "G-HOJE (b)"}
    assert res["n"]["k"] in (4, 5) and res["custo"]["validacao_estimada"]["vidas"] == res["n"]["n"] * 120
    assert set(res["sensibilidades"]["recompensa_tapa"]) == {"-0.5", "-1", "-2"}
    # toda vida gravada foi rejogada do disco (Bancada.conferir_replay) e tem o log no disco
    vidas = list(saida.rglob("vidas/*.jsonl"))
    assert len(vidas) == len(grade[res["escolha"]["nome"]]) * 9 + len(piloto)
    meta = json.loads((saida / "meta.json").read_text(encoding="utf-8"))
    assert meta["sha256"]["corpo.py"] and meta["modo"] == "fumaca" and math.isfinite(meta["duracao_s"])
    with pytest.raises(FileExistsError):
        cc.rodar(_fumaca(), saida, 1, FUMACA)
