"""V2, W-BANCADA-BANHEIRO (rodada 25): as faixas dos dois pets (docs/PLANO_ANALISE_V2_DOIS_PETS.md, secao 8, PDP-6) e a bancada do banheiro,
so o que ja da (docs/TAREFA_V2_BANHEIRO.md, etapa 5; docs/PLANO_ANALISE_V2_BANHEIRO.md, secoes 1 a 4 e 8).

O que se confere:
- as quatro faixas dos dois pets em FAIXAS_RESERVADAS com a fonte, sem colidir com as de antes, com as queimadas nem com as configs; o
  prefixo "dois_pets" pela regra E3; as unidades dos oito prefixos sem colisao entre planos e fases;
- os oito bracos do 2 x 2 (P0 e P1 x B00, B0C, BL0, BLC) declarados como o plano pede e falhando alto com o no do banheiro (a etapa 3 do
  A) no braco_de, na config e na vida; a trava e so a tabela: sem ela, o corpo com o banheiro, a chave do banheiro com o limpador do braco
  e o cerebro A (ou o instinto do alivio) se montam, e a vida para na fiacao do motor, que espera a etapa 3;
- as medidas do plano pelas funcoes do #224 (`medidas_banheiro_de`, `tabela_banheiro`), em dados com a resposta conhecida, e o contrato do
  motor conferido na `Bancada.medidas_banheiro`;
- o registro da medicao anota cada carinho no tick certo.
So as sementes dos testes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.instinto_banheiro import PoliticaInstintoBanheiro  # noqa: E402
from digilab.metrics import curva_sobrevivencia  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402

SONDA = {"estados": 5, "amostras": 5, "semente": 101}
T = 1440

# ------------------------------------------------------------------ 1. as faixas dos dois pets

BASES = {
    "experimento-maior": bv.BASES_EXPERIMENTO_MAIOR, "n6": bv.BASES_N6, "n7": bv.BASES_N7, "comparacao-cerebros": bv.BASES_COMPARACAO,
    "mundo": {"calibracao": (31101, 31202, 31303, 31404, 31505), "validacao": (32101, 32202, 32303, 32404, 32505)},
    "corpo": {"calibracao": (33101, 33202, 33303, 33404, 33505), "validacao": (34101, 34202, 34303, 34404, 34505)},
    "banheiro": {"calibracao": (37101, 37202, 37303, 37404, 37505), "validacao": (38101, 38202, 38303, 38404, 38505)},
    "dois_pets": {"calibracao": (39101, 39202, 39303, 39404, 39505), "validacao": (40101, 40202, 40303, 40404, 40505),
                  "degrau_1b": (41101, 41202, 41303, 41404, 41505), "dois_donos": (42101, 42202, 42303, 42404, 42505)},
}
NOVAS = {(39101, 39505): "calibracao", (40101, 40505): "validacao", (41101, 41505): "degrau 1b", (42101, 42505): "dois donos"}
K = 40


def _numeros_das_configs() -> set[int]:
    achados: set[int] = set()

    def andar(o, chave=""):
        marca = "semente" in chave.lower() or "base" in chave.lower()
        if isinstance(o, dict):
            for k, v in o.items():
                andar(v, k)
        elif isinstance(o, list):
            for v in o:
                andar(v, chave)
        elif isinstance(o, int) and not isinstance(o, bool) and marca:
            achados.add(o)

    for p in (RAIZ / "experiments" / "configs").rglob("*.json"):
        andar(json.loads(p.read_text(encoding="utf-8")))
    return achados


def test_faixas_dos_dois_pets_reservadas_com_fonte():
    faixas = {(lo, hi): fonte for lo, hi, fonte in bv.FAIXAS_RESERVADAS}
    for (lo, hi), uso in NOVAS.items():
        assert "PLANO_ANALISE_V2_DOIS_PETS" in faixas[(lo, hi)] and "PDP-6" in faixas[(lo, hi)] and uso in faixas[(lo, hi)]
    for fase, bs in BASES["dois_pets"].items():
        for b in bs:
            assert "dois pets" in bv.na_faixa_reservada(b), (fase, b)


def test_faixas_disjuntas_fora_das_queimadas_e_das_configs():
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))
    numeros = _numeros_das_configs()
    assert numeros
    for lo, hi in NOVAS:
        assert not any(q_lo <= hi and lo <= q_hi for q_lo, q_hi, _ in bv.FAIXAS_QUEIMADAS)
        assert not [n for n in numeros if lo <= n <= hi], (lo, hi)


def test_o_prefixo_dos_dois_pets_segue_a_regra():
    assert "dois_pets" in bv.PREFIXOS_UNIDADES
    u = bv.unidades_derivadas(BASES["dois_pets"]["calibracao"], 4, "dois_pets")[6]
    assert (u["base"], u["k"]) == (39202, 2)
    assert u["semente"] == derivar_semente("dois_pets", 39202, 2) and u["genoma"] == derivar_semente("dois_pets-genoma", 39202, 2)


def test_unidades_sem_colisao_entre_planos_e_fases():
    por = {}
    for prefixo, fases in BASES.items():
        for fase, bases in fases.items():
            us = bv.unidades_derivadas(bases, K, prefixo)
            por[(prefixo, fase)] = [x["semente"] for x in us] + [x["genoma"] for x in us]
    todos = [v for vs in por.values() for v in vs]
    assert len(set(todos)) == len(todos)
    numeros = _numeros_das_configs()
    for (prefixo, _), vs in por.items():
        if prefixo == "dois_pets":
            assert all(bv.na_faixa_reservada(v) is None and v not in numeros and v not in bv.SEMENTES_TESTE for v in vs)


def test_config_com_o_prefixo_dos_dois_pets_pede_plano():
    cfg = {"bracos": ["P0"], "donos": ["atencioso"], "unidades": {"bases": [101], "k": 1, "prefixo": "dois_pets"}, "dias": 1,
           "orcamento": 16, "sonda": SONDA, "bootstrap": {}, "mundos": ["descasado"]}
    bv.validar_config(cfg)
    for b in (39101, 42505):
        with pytest.raises(bv.SementeSemPlano):
            bv.validar_config({**cfg, "unidades": {"bases": [b], "k": 1, "prefixo": "dois_pets"}})
    bv.validar_config({**cfg, "unidades": {"bases": [39101], "k": 1, "prefixo": "dois_pets"},
                       "plano": "docs/PLANO_ANALISE_V2_DOIS_PETS.md"})


# ------------------------------------------------------------------ 2. os bracos do banheiro


BANHEIRO = [f"{c}-{b}" for c in ("P0", "P1") for b in ("B00", "B0C", "BL0", "BLC")]


def _cfg(**troca) -> dict:
    cfg = {"bracos": ["P1-B0C"], "donos": ["atencioso"], "sementes": [101], "dias": 2, "orcamento": 32, "sonda": SONDA,
           "bootstrap": {}, "mundos": ["fisico"], "lugares": ["comedouro"]}
    cfg.update(troca)
    return cfg


def test_os_bracos_do_banheiro_declarados_como_o_plano_pede():
    B = bv.BRACOS
    assert {r: (B[r].fonte, B[r].no, B[r].regime, B[r].gestos, B[r].banheiro) for r in BANHEIRO} == {
        f"{c}-{b}": (f, "banheiro", "corpo", None, b) for c, f in (("P0", "nenhuma"), ("P1", "consequencia"))
        for b in ("B00", "B0C", "BL0", "BLC")}
    assert bv.BRACOS_BANHEIRO == {"B00": (False, False), "B0C": (False, True), "BL0": (True, False), "BLC": (True, True)}


@pytest.mark.parametrize("braco", BANHEIRO)
def test_o_banheiro_falha_alto_com_o_no(braco):
    assert "etapa 3" in bv.NOS_PENDENTES["banheiro"] and "DonoCarinhoBanheiro" in bv.NOS_PENDENTES["banheiro"]
    with pytest.raises(NotImplementedError, match="DonoCarinhoBanheiro"):
        bv.braco_de(braco)
    with pytest.raises(NotImplementedError, match="DonoCarinhoBanheiro"):
        bv.validar_config(_cfg(bracos=[braco]))
    with pytest.raises(NotImplementedError, match="DonoCarinhoBanheiro"):
        bv.Bancada(2, 32).vida(bv.EspecVida("atencioso", braco, 101, None, "fisico", lugar="comedouro"))


def test_a_trava_e_so_a_tabela(monkeypatch):
    """Sem a entrada, os bracos se resolvem e o cerebro se monta; a vida para na fiacao do motor e do dono, que espera a etapa 3."""
    monkeypatch.setattr(bv, "NOS_PENDENTES", {})
    b = bv.Bancada(2, 32)
    for braco in BANHEIRO:
        assert bv.braco_de(braco) is bv.BRACOS[braco]
        bv.validar_config(_cfg(bracos=[braco]))
        e = bv.EspecVida("atencioso", braco, 101, None, "fisico", lugar="comedouro")
        cc = b.cfg_corpo_de(e)
        assert cc.drives_novos and cc.gestos and cc.banheiro
        cb = b.cfg_banheiro_de(e)
        assert cb.ligada and cb.limpador == bv.BRACOS_BANHEIRO[braco[3:]][0]
        pol = b.politica(e)
        assert isinstance(pol.cerebro, PoliticaLobos) and pol.cerebro._banheiro == cb
        assert pol.cerebro._aprende == braco.startswith("P1")
        with pytest.raises(NotImplementedError, match="etapa 3"):
            b.vida(e)
    inst = b.politica(bv.EspecVida("atencioso", "P0-B00", 101, None, "fisico", "instinto", lugar="comedouro"))
    assert isinstance(inst.cerebro, PoliticaInstintoBanheiro)
    with pytest.raises(ValueError, match="mundo fisico"):
        bv.validar_config(_cfg(mundos=["bola"], lugares=None))
    with pytest.raises(ValueError, match="mundo fisico"):
        b.cfg_banheiro_de(bv.EspecVida("atencioso", "P1-BLC", 101, None, "bola"))
    assert b.cfg_banheiro_de(bv.EspecVida("atencioso", "P1-c", 101, None, "bola")) is None
    assert not b.cfg_corpo_de(bv.EspecVida("atencioso", "P1-c", 101, None, "bola")).banheiro      # os bracos do corpo, sem banheiro


def test_o_banheiro_so_no_corpo_e_no_p0_ou_no_p1(monkeypatch):
    for errado in (dict(regime="quimica"), dict(fonte="dono"), dict(gestos="sem_tapa"), dict(banheiro="B11")):
        monkeypatch.setitem(bv.BRACOS, "X", bv.replace(bv.BRACOS["P1-B00"], rotulo="X", **errado))
        with pytest.raises(ValueError, match="banheiro"):
            bv.braco_de("X")


# ------------------------------------------------------------------ 3. as medidas do plano


def test_as_medidas_do_banheiro_em_dados_conhecidos():
    alivios = [(10, False, False), (20, True, False),                     # dia 1: 1 de 2
               (T + 5, True, False),                                      # dia 2: 1 de 1
               (2 * T + 1, True, False), (2 * T + 2, True, True),          # dia 3: 2 de 2, um urgente
               (3 * T + 7, True, False)]                                  # dia 4: 1 de 1; dia 5 sem alivio
    carinhos = [(30, 0.5, 900), (40, 0.3, 300), (T + 6, 0.1, 60)]
    limpador = [(T + 5, 130)]
    pesos = [{"banheiro": 256 + 100 * d, "aqui": 1024} for d in range(5)]
    cuidado = [(0, False, 0.9, 0.5), (15, True, 0.7, 0.2)]
    escolhas = [(10, "banheiro", False, 640), (20, "banheiro", True, 160), (25, "aqui", False, 0)]
    m = bv.medidas_banheiro_de(alivios, 5, carinhos, limpador, pesos, cuidado, escolhas)
    assert [o["fracao"] for o in m["por_dia"]] == [0.5, 1.0, 1.0, 1.0, None]
    assert m["criterio"] == {"dia": 2, "censurado": False, "tau": 4, "t_estrela": 2}       # 2, 3 e 4 acima de 0,80; tau = D - 1
    assert m["alivios_ate_criterio"] == 3 and m["alivios"] == 6
    assert m["acidentes"] == {"n": 1, "fracao": 1 / 6}
    assert m["cuidado"] == {"n": 2, "privacao": 0.5, "saude_media": 0.8, "fome_media": 0.35}
    c1 = m["carinho"]["por_dia"][0]
    assert m["carinho"]["n"] == 3 and c1["n"] == 2 and abs(c1["solidao_media"] - 0.4) < 1e-12 and c1["sinal_medio"] == 600
    assert m["carinho"]["por_dia"][1]["sinal_medio"] == 60 and m["carinho"]["por_dia"][2] == {"dia": 3, "n": 0, "solidao_media": None,
                                                                                               "sinal_medio": None}
    assert m["limpador"]["n"] == 1 and m["limpador"]["por_dia"][1]["sinal_medio"] == 130
    assert [p["banheiro_menos_aqui"] for p in m["peso_alvo_por_dia"]] == [-768, -668, -568, -468, -368]
    assert m["chegou_tarde"] == {"escolhas_banheiro": 2, "fora": 1, "fracao": 0.5, "distancia_media": 400.0}
    # censurado: sem tres dias seguidos acima de 0,80, T* = tau e os alivios sao os da vida toda
    cens = bv.medidas_banheiro_de([(10, True, False), (T + 1, False, False)], 5)
    assert cens["criterio"]["censurado"] and cens["criterio"]["t_estrela"] == 4 and cens["alivios_ate_criterio"] == 2
    assert cens["cuidado"] is None and cens["peso_alvo_por_dia"] is None and cens["chegou_tarde"]["fracao"] is None
    with pytest.raises(ValueError, match="pesos do alvo"):
        bv.medidas_banheiro_de(alivios, 5, pesos_alvo=pesos[:4])
    with pytest.raises(ValueError, match="fora"):
        bv.medidas_banheiro_de(alivios, 5, carinhos=[(5 * T, 0.5, 1)])
    with pytest.raises(ValueError):
        bv.medidas_banheiro_de([(5 * T, True, False)], 5)


def test_a_tabela_do_banheiro_e_a_curva_por_braco():
    def m(braco, dia, origem=None):
        crit = {"dia": dia, "censurado": dia is None, "tau": 4, "t_estrela": 4 if dia is None else dia}
        return {"braco": braco, "origem": origem, "banheiro": {"criterio": crit}}

    medidas = {"a": m("P1-B0C", 2), "b": m("P1-B0C", None), "c": m("P1-B00", None), "d": m("P1-B00", 3),
               "e": m("P1-B00", 1, origem="x"), "f": {"braco": "P1", "origem": None, "banheiro": None}}
    tab = bv.tabela_banheiro(medidas)
    assert set(tab) == {"P1-B00", "P1-B0C"}
    assert tab["P1-B0C"] == curva_sobrevivencia([medidas["a"]["banheiro"]["criterio"], medidas["b"]["banheiro"]["criterio"]])
    assert tab["P1-B00"]["fracao_censurada"] == 0.5 and tab["P1-B00"]["rmst"] == 3.5         # T* 4 e 3: o acoplado fica fora


def test_o_contrato_do_motor_e_conferido():
    b = bv.Bancada(2, 32)
    vida = SimpleNamespace(nome="vida-teste")
    with pytest.raises(NotImplementedError, match="alivios"):
        b.medidas_banheiro(vida, SimpleNamespace(), None)
    with pytest.raises(RuntimeError, match="contrato"):
        b.medidas_banheiro(vida, SimpleNamespace(alivios=[{"tick": 0, "dentro": True}]), None)


# ------------------------------------------------------------------ 4. o registro anota os carinhos


def test_o_registro_anota_cada_carinho_no_tick_certo():
    b = bv.Bancada(3, 48)
    for mundo in ("bola", "padrao"):
        v = b.vida(bv.EspecVida("atencioso", "P1-c", 202, None, mundo))
        regs = []

        def fab(cfg=None):
            reg = bv._Registro(b.politica(v.espec, cfg))
            regs.append(reg)
            return reg

        m = reproduzir_com_feedback(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fab, semente=v.espec.semente,
                                    fabrica_motor=b.fabrica_motor(v.espec))
        assert bv.resumo_motor(m) == bv.resumo_motor(v.motor)
        reg = regs[-1]
        acariciar = [e.tick for e in v.motor.log if e.tipo == "acao_usuario" and str(e.valor) == "acariciar"]
        assert acariciar and [t for t, _, _ in reg.carinhos] == acariciar
        assert all(a.solidao is not None and d.solidao <= a.solidao for _, a, d in reg.carinhos)   # o carinho tira solidao
        # as decisoes depois de um carinho caem no tick certo (o relogio do registro anda com o carinho)
        ticks = [t for t, _, _ in reg.decisoes]
        assert all(b2 - a2 == 15 for a2, b2 in zip(ticks, ticks[1:]))


def test_as_medidas_dos_outros_bracos_tem_o_banheiro_vazio():
    b = bv.Bancada(2, 32)
    m = b.medir(b.vida(bv.EspecVida("atencioso", "P1-c", 101, None, "bola")), SONDA)
    assert m["banheiro"] is None and m["corpo"] is not None
