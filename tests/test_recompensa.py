"""O teste de recompensa (docs/PLANO_ANALISE_V3_PET_VIVO_RECOMPENSA.md): os bracos, as conferencias, as medidas e as regras de leitura."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import pv2  # noqa: E402
import recompensa as rec  # noqa: E402
import run_v3_pet_vivo_recompensa as RR  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
SEMENTE, DIAS = 101, 2
CFG = json.loads((RAIZ / "experiments/configs/v3_pet_vivo/recompensa.json").read_text(encoding="utf-8"))
FUMACA = json.loads((RAIZ / "experiments/configs/v3_pet_vivo/recompensa_fumaca.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def celula():
    """os quatro bracos de uma unidade das sementes dos testes, 2 dias, o atencioso no comedouro"""
    return rec.viver_celula("atencioso", "comedouro", SEMENTE, DIAS)


# ------------------------------------------------------------------ os bracos
def test_a_dose_e_a_do_plano():
    assert (rec.ELOGIO.ligada, rec.ELOGIO.ganho, rec.ELOGIO.janela) == (True, 2 * S, 1)
    assert rec.BRACOS == ("R0", "R-CORPO", "R-CB", "R-SORT") and rec.ALVOS == ("comer", "brincar")


def test_o_r0_e_o_pet_do_v38_de_hoje(celula):
    hoje, _, _ = pv2.viver("HOJE", "atencioso", "comedouro", SEMENTE, DIAS, v38=True)
    assert celula["R0"]["motor"].log.para_jsonl() == hoje.log.para_jsonl()
    assert celula["R0"]["dono"] is None


def test_o_carinho_cai_no_passo_da_decisao_de_comer_ou_brincar(celula):
    for braco in rec.NA_HORA:
        v = celula[braco]
        alvos = [k for k, m in enumerate(v["cerebro"].motivos) if m["escolha"][0] in rec.ALVOS]
        assert len(alvos) >= 5
        assert v["dono"].carinhos == [(k, k) for k in alvos]
        RR.conferir_vida(braco, braco, v)


def test_o_credito_vai_a_decisao_recompensada_so_com_a_chave(celula):
    cb = celula["R-CB"]
    creditos = {cr["decisao"]: cr for e in cb["cerebro"].elogios for cr in e["creditos"]}
    for _, k in cb["dono"].carinhos:
        assert creditos[k]["j"] == 0 and creditos[k]["peso"] == S
        assert creditos[k]["p2"]["b"] == cb["cerebro"].motivos[k]["escolha"][0]
    for braco in ("R0", "R-CORPO"):
        assert celula[braco]["cerebro"].cel is None and not hasattr(celula[braco]["cerebro"], "elogios")
    assert celula["R-CORPO"]["motor"].mudancas == 0 and cb["motor"].mudancas == len(cb["dono"].carinhos)


def test_o_r_sort_tem_o_mesmo_numero_em_passos_sorteados(celula):
    n = len(celula["R-CB"]["dono"].carinhos)
    sort = celula["R-SORT"]["dono"].carinhos
    assert len(sort) == n and all(k is None for _, k in sort)
    passos = rec.passos_da_vida(DIAS)
    assert [p for p, _ in sort] == rec.passos_sorteados(n, passos, SEMENTE)
    assert rec.passos_sorteados(n, passos, SEMENTE) != rec.passos_sorteados(n, passos, SEMENTE + 1)
    assert all(0 <= p < passos for p, _ in sort)


def test_o_replay_refaz_a_vida_com_o_carinho(celula):
    v = celula["R-CB"]
    RR.orq.conferir_replay(v["motor"], v["fabricas"], SEMENTE, v["motor"].log.para_jsonl())


def test_as_falhas_altas_dos_bracos(celula):
    with pytest.raises(ValueError):
        rec.DonoRecompensa("R0")
    with pytest.raises(ValueError):
        rec.DonoRecompensa("R-SORT")
    with pytest.raises(ValueError):
        rec.DonoRecompensa("R-CB", [1, 2])
    with pytest.raises(ValueError):
        rec.fabricas("R-X", "atencioso", SEMENTE, DIAS)
    with pytest.raises(RuntimeError):
        rec.DonoRecompensa("R-CB").acoes({})
    with pytest.raises(ValueError):
        rec.passos_sorteados(-1, 10, SEMENTE)


def test_a_c_hora_falha_alto_com_um_carinho_fora_de_hora(celula):
    v = dict(celula["R-CB"])
    dono = rec.DonoRecompensa("R-CB")
    dono.carinhos = list(celula["R-CB"]["dono"].carinhos[:-1])
    v["dono"] = dono
    with pytest.raises(RR.RecompensaDivergiu, match="C-HORA"):
        RR.conferir_vida("x", "R-CB", v)
    with pytest.raises(RR.RecompensaDivergiu, match="C-CORPO"):
        RR.conferir_vida("x", "R0", celula["R-CB"])


# ------------------------------------------------------------------ as medidas
def test_o_tempo_acordado_a_mao():
    acoes = ["dormir", "comer", "brincar", "dormir", "explorar", "dormir", "dormir", "ocioso"]
    assert met.tempo_acordado(acoes) == {"n": 8, "acordado": 4, "frac": 0.5}
    assert met.tempo_acordado(acoes, 4) == {"n": 4, "acordado": 2, "frac": 0.5}
    assert met.tempo_acordado(acoes, 1, 3)["frac"] == 1.0
    with pytest.raises(ValueError):
        met.tempo_acordado(acoes, 8)
    with pytest.raises(TypeError):
        met.tempo_acordado([["dormir"]])


def test_a_medida_do_carinho_a_mao():
    elogios = [{"k": 0, "creditos": []},
               {"k": 3, "f_n": 100, "creditos": [{"p2": {"abs": 4}}]},
               {"k": 5, "f_n": 0, "creditos": [{"p2": {"abs": 0}}]},
               {"k": 7, "f_n": -3, "creditos": [{"p2": {"abs": 1}}, {"p2": None}]}]
    assert met.medidas_carinho(elogios) == {"n": 4, "sinal_zero": 1, "sinal_negativo": 1, "sem_decisao": 1, "creditos": 4,
                                            "creditos_movem": 2, "fracao_movem": 0.5}
    assert met.medidas_carinho([])["fracao_movem"] is None
    with pytest.raises(ValueError):
        met.medidas_carinho([{"k": 0, "creditos": [{"p2": None}]}])


def test_as_medidas_de_uma_vida(celula):
    m = RR.medir("R-CB", DIAS, celula["R-CB"])
    acoes = [x["escolha"][0] for x in celula["R-CB"]["cerebro"].motivos]
    assert m["t_acordado"] == (len(acoes) - acoes.count("dormir")) / len(acoes)
    assert m["carinhos_a_mais"] == m["decisoes_comer"] + m["decisoes_brincar"] == m["credito"]["n"]
    assert 0 <= m["tempo_bem"] <= 1 and m["credito"]["sinal_negativo"] == 0
    assert RR.medir("R0", DIAS, celula["R0"])["credito"] is None


# ------------------------------------------------------------------ as regras de leitura (secao 7)
def _ic(inf, sup):
    return {"ic_inferior": inf, "ic_superior": sup}


def test_l_acordado_em_ordem():
    assert RR.ler_acordado(_ic(-0.03, -0.001))["leitura"] == RR.L_DORME
    assert RR.ler_acordado(_ic(-0.01, 0.01)) == {"leitura": RR.L_IGUAL, "nota": None}
    assert RR.ler_acordado(_ic(0.002, 0.01)) == {"leitura": RR.L_IGUAL, "nota": "sobe, mas abaixo do relevante"}
    assert RR.ler_acordado(_ic(0.021, 0.05))["leitura"] == RR.L_SIM
    assert RR.ler_acordado(_ic(0.01, 0.03))["leitura"] == RR.L_INCONCLUSIVO
    assert RR.ler_acordado(_ic(-0.03, 0.001))["leitura"] == RR.L_INCONCLUSIVO
    assert RR.ler_acordado(_ic(None, None))["leitura"] == RR.L_INCONCLUSIVO


def test_l_porque():
    pos, nulo = _ic(0.001, 0.01), _ic(-0.01, 0.01)
    assert RR.ler_porque(RR.L_IGUAL, pos, pos, True)["leitura"] is None
    assert RR.ler_porque(RR.L_SIM, pos, pos, True)["leitura"] == RR.P_NA_HORA
    assert RR.ler_porque(RR.L_SIM, nulo, pos, True)["leitura"] == RR.P_CREDITO
    assert RR.ler_porque(RR.L_DORME, nulo, nulo, True)["leitura"] == RR.P_CORPO
    assert RR.ler_porque(RR.L_SIM, pos, nulo, True)["leitura"] == RR.L_INCONCLUSIVO
    assert RR.ler_porque(RR.L_SIM, pos, pos, False)["leitura"] == RR.L_INCONCLUSIVO
    assert RR.ler_porque(RR.L_DORME, nulo, nulo, False)["leitura"] == RR.P_CORPO


def test_l_bem():
    assert RR.ler_bem(_ic(0.001, 0.02))["leitura"] == RR.B_MELHOR
    assert RR.ler_bem(_ic(-0.01, 0.02))["leitura"] == RR.B_NAO_PIORA
    assert RR.ler_bem(_ic(-0.06, -0.04))["leitura"] == RR.B_PIORA
    assert RR.ler_bem(_ic(-0.04, 0.0))["leitura"] == RR.L_INCONCLUSIVO


def _registro(braco, dono, lugar, semente, acordado, carinhos=120, movem=60):
    credito = {"n": carinhos, "sinal_zero": 0, "sinal_negativo": 0, "sem_decisao": 0, "creditos": carinhos, "creditos_movem": movem,
               "fracao_movem": movem / carinhos} if braco in rec.COM_CREDITO else None
    return {"braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "t_acordado": acordado, "t_acordado_8_14": acordado,
            "tempo_bem": 0.9, "saude_media": 0.8, "episodios_fome": {"taxa": None}, "decisoes_comer": 60, "decisoes_brincar": 60,
            "sono": {"F_PESOS_DEC": 0.1}, "habito": {"comer": 0, "brincar": 0},
            "carinhos_a_mais": 0 if braco == "R0" else carinhos, "credito": credito}


def _sinteticos(efeito_cb, carinhos=120, movem=60):
    regs = []
    for i, s in enumerate(range(1, 9)):
        ruido = (i % 3 - 1) * 0.002
        for dono, lugar in RR.CELULAS:
            regs += [_registro("R0", dono, lugar, s, 0.50, 0), _registro("R-CORPO", dono, lugar, s, 0.49 + ruido, carinhos),
                     _registro("R-CB", dono, lugar, s, 0.50 + efeito_cb + ruido, carinhos, movem),
                     _registro("R-SORT", dono, lugar, s, 0.49 - ruido, carinhos, movem)]
    return regs


def test_a_analise_num_caso_sintetico():
    r = RR.analisar(_sinteticos(0.05))
    d1 = r["contrastes"]["t_acordado"]["D1"]
    assert d1["n"] == 8 and abs(d1["media"] - 0.05) < 1e-3
    assert r["leitura"]["L-ACORDADO"]["leitura"] == RR.L_SIM
    assert r["leitura"]["L-PORQUE"]["leitura"] == RR.P_NA_HORA
    assert r["leitura"]["L-BEM"]["leitura"] == RR.B_NAO_PIORA
    assert all(v["cumpre"] for v in r["premissas"].values()) and r["celulas_fora"] == []
    assert r["contrastes"]["taxa_por_episodio"]["D1"]["n"] == 0
    assert RR.analisar(_sinteticos(-0.02))["leitura"]["L-ACORDADO"]["leitura"] == RR.L_DORME


def test_as_premissas_que_falham_ficam_registradas():
    r = RR.analisar(_sinteticos(0.05, movem=10))
    assert not r["premissas"]["P-DOSE"]["cumpre"] and r["leitura"]["L-PORQUE"]["leitura"] == RR.L_INCONCLUSIVO
    regs = _sinteticos(0.05)
    for x in regs:
        if (x["dono"], x["lugar"]) == RR.CELULAS[0] and x["braco"] == "R-CB":
            x["carinhos_a_mais"] = 10
    r = RR.analisar(regs)
    assert not r["premissas"]["P-EVENTO"]["cumpre"] and r["celulas_fora"] == [list(RR.CELULAS[0])]
    assert len(r["celulas_da_leitura"]) == 11
    with pytest.raises(RR.RecompensaDivergiu):
        RR.analisar([x for x in regs if x["braco"] != "R-CB"])


# ------------------------------------------------------------------ a config, a faixa e as recusas
def test_a_config_e_a_faixa_seguem_o_plano():
    assert RR.modo_da_config(FUMACA) == "fumaca"
    assert tuple(CFG["unidades"]["bases"]) == RR.BASES and len(RR.BASES) == 200 and CFG["unidades"]["k"] == 1
    assert any((lo, hi) == RR.FAIXA for lo, hi, _ in FAIXAS_RESERVADAS)
    assert RR.modo_da_config(CFG) == RR.FASE
    assert len(RR.CELULAS) == 12 and len(RR.BASES) * len(RR.BRACOS) * len(RR.CELULAS) == 9600
    assert (RR.DELTA_A, RR.MARGEM_BEM, RR.CORTE_CUSTO_H) == (0.02, 0.032, 4.0)


def test_a_config_fora_do_plano_falha_alto(tmp_path):
    with pytest.raises(bv.SementeSemPlano):
        RR.modo_da_config({**CFG, "unidades": {**CFG["unidades"], "bases": [108001, 108002]}})
    with pytest.raises(ValueError):
        RR.modo_da_config({**CFG, "dias": 7})
    with pytest.raises(ValueError):
        RR.modo_da_config({**CFG, "fase": "outra"})
    with pytest.raises(ValueError):
        RR.modo_da_config({**FUMACA, "dias": 15})
    with pytest.raises(RuntimeError):
        RR.exigir_aprovado("**Status: PROPOSTO.**")
    with pytest.raises(ValueError):
        RR.rodar(FUMACA, tmp_path / "x", 5)
    with pytest.raises(FileExistsError):
        RR.rodar(FUMACA, tmp_path, 1)


def test_a_fumaca_de_um_dia_passa_nas_conferencias(tmp_path):
    cfg = {**FUMACA, "dias": 1}
    r = RR.rodar(cfg, tmp_path / "fumaca", 1)
    assert r["resultado"]["modo"] == "fumaca" and r["resultado"]["vidas"] == 48 and len(r["registros"]) == 48
    assert set(r["resultado"]) == {"modo", "fase", "vidas", "conferencias", "projecao_parede_h_4_processos", "corte_h"}
    assert (tmp_path / "fumaca" / "vidas.tar.gz").exists()
