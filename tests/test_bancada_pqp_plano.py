"""V2, W-BANCADA-PQP-PLANO: os bracos do J5 com o planejador (docs/TAREFA_V2_PET_QUE_PENSA.md, etapa 4; docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md,
secoes 3, 4 e 7), com o planejador do #294 na main. So as sementes dos testes.

O que se confere:
- o cerebro: o g_plano da config so nos tres bracos com o planejador, os modelos sao os do proprio cerebro (o embrulho nao os alimenta de
  novo) e a ConfigConsequencia do plano e a do credito;
- o G1 de toda vida dos tres bracos pelo texto do log, nos dois protocolos;
- antes do tick da mudanca os tres bracos sao a mesma vida (o mesmo g_plano, nada congelado ainda);
- o congelamento (PP-8) pelo `congelar` dos modelos do cerebro: as partes congeladas iguais do tick da mudanca ao fim; a mao chega ao
  desfecho no P1-plan e no P1-plan-desfecho e nao no P1-plan-cong; o gate falha alto se o modelo congelado mudar;
- o G-SEM-CREDITO com o planejador: o cerebro igual antes e depois de cada mao, fora os modelos;
- quanto o plano decide, a legibilidade e o G2 (`plano_da_vida`): em dados com a resposta conhecida, contra os motivos do cerebro numa vida,
  e o G2 que falha alto quando o P1 tem o termo do plano;
- a medida da regra da calibracao (`fracao_plano_dias`) em dados com a resposta conhecida.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.expressao import FATORES  # noqa: E402
from digilab.policies.lobos import LOBO_PLANEJAMENTO  # noqa: E402

FUMACA = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "fumaca.json"
CURTA = {"d_a": 2, "janela": 1}
G = 1024                                         # S: o ponto alto da grade, para o plano agir nas vidas curtas
BRACOS_PLANO = ("P1-plan", "P1-plan-desfecho", "P1-plan-cong")


def _bp() -> bv.BancadaPQP:
    cfg = {**json.loads(FUMACA.read_text(encoding="utf-8")), **CURTA, "bracos": list(BRACOS_PLANO), "g_plano": G}
    return bv.bancada_pqp_da_config(cfg)


_CACHE: dict = {}


def _vida(braco: str, protocolo: str, semente: int = 101):
    chave = (braco, protocolo, semente)
    if chave not in _CACHE:
        _CACHE[chave] = _bp().vida(bv.EspecPQP(braco, protocolo, semente))
    return _CACHE[chave]


def _med(braco: str, protocolo: str, semente: int = 101) -> dict:
    chave = ("med", braco, protocolo, semente)
    if chave not in _CACHE:
        _CACHE[chave] = _bp().medir(_vida(braco, protocolo, semente))
    return _CACHE[chave]


# ------------------------------------------------------------------ 1. o cerebro


@pytest.mark.parametrize("braco", BRACOS_PLANO)
def test_o_cerebro_com_o_planejador(braco):
    bp = _bp()
    p = bp.politica(bv.EspecPQP(braco, "T1", 101))
    m = p.cerebro
    cerebro = m._interna
    assert isinstance(m, bv.PoliticaComModeloPQP) and m.do_cerebro and m.congela == bv.BRACOS_PQP[braco].congela
    assert cerebro.cl.g_plano == G and cerebro.modelo_mundo is m.modelo and m.modelo.cfg == bp.cfg_modelo
    assert cerebro._cc_plano == p.cfg_consequencia                          # o plano e o credito com a mesma ConfigConsequencia
    assert cerebro.cl.alvo_aprendido and cerebro.cl.alvo_por_arvore and cerebro.cl.presenca_fruta_mundo
    # o P1 da mesma bancada: g_plano 0, os modelos so observam no embrulho
    p1 = bp.politica(bv.EspecPQP("P1", "T1", 101)).cerebro
    assert not p1.do_cerebro and p1._interna.cl.g_plano == 0 and p1._interna.modelo_mundo is None


def test_o_embrulho_nao_alimenta_os_modelos_do_cerebro_de_novo():
    """com o planejador, o modelo anda uma decisao por decisao do cerebro (k = decisoes), como o do P1 no embrulho"""
    for braco in ("P1", "P1-plan"):
        v = _vida(braco, "T2")
        modelo = v.motor.politica._pm.cerebro.modelo
        assert modelo.k == len(v.motor.decisoes_mundo)


# ------------------------------------------------------------------ 2. o G1 e a vida antes da mudanca


@pytest.mark.parametrize("braco", BRACOS_PLANO)
@pytest.mark.parametrize("protocolo", ["T1", "T2"])
def test_g1_dos_bracos_com_o_planejador(braco, protocolo):
    v = _vida(braco, protocolo)
    bp = _bp()
    bp.conferir_replay(v, v.motor.log.para_jsonl())
    texto = v.motor.log.para_jsonl().splitlines()
    mexido = "\n".join(texto[:-1]) + "\n"
    with pytest.raises(bv.ReplayDivergiu):
        bp.conferir_replay(v, mexido)


@pytest.mark.parametrize("protocolo", ["T1", "T2"])
def test_antes_da_mudanca_os_tres_bracos_sao_a_mesma_vida(protocolo):
    vs = [_vida(b, protocolo) for b in BRACOS_PLANO]
    tm = vs[0].tick_mudanca
    assert all(v.tick_mudanca == tm for v in vs)
    antes = lambda v: [d for d in v.motor.decisoes_mundo if d["tick"] < tm]  # noqa: E731
    assert antes(vs[0]) and all(antes(v) == antes(vs[0]) for v in vs)
    logs = [v.motor.log.para_jsonl().splitlines() for v in vs]
    corte = next(i for i, linha in enumerate(logs[0]) if "dar_fruta" in linha or "trocar_arvores" in linha)
    assert all(lg[:corte] == logs[0][:corte] for lg in logs)


# ------------------------------------------------------------------ 3. o congelamento e a G-SEM-CREDITO


@pytest.mark.parametrize("braco", BRACOS_PLANO)
def test_o_congelamento_pelos_modelos_do_cerebro(braco):
    v = _vida(braco, "T1", 303)
    med = _bp().medir(v)
    congela = bv.BRACOS_PQP[braco].congela
    emb = v.motor.politica._pm.cerebro
    assert emb._interna.modelo_mundo.congelados == tuple(sorted(congela))
    assert med["congelamento"]["tick"] == v.tick_mudanca and med["congelamento"]["partes"] == sorted(congela)
    assert med["g_sem_credito"] == {"maos": 2, "violacoes": 0}
    assert med["maos_no_modelo"] == (0 if "desfecho" in congela else 2)
    ei = json.loads(bv._interno(v.motor))
    assert ei["plano"]["modelo_mundo"] == {k: x for k, x in ei["modelo_mundo"].items()
                                           if k not in ("do_cerebro", "congela", "tick_congelamento", "maos", "maos_ignoradas")}
    if congela:
        retrato = {k: json.loads(x) for k, x in emb.retrato_congelamento.items()}
        assert med["modelos_por_dia"][-1]["mapa"] == retrato["mapa"]["mapa"]
        emb.modelo.mapa[next(iter(emb.modelo.mapa))][0] += 1                # mexer no congelado depois faz o gate falhar alto
        with pytest.raises(RuntimeError, match="congelamento"):
            emb.congelamento_conferido()
        emb.modelo.mapa[next(iter(emb.modelo.mapa))][0] -= 1
    if "desfecho" not in congela:
        ih = med["modelos_por_dia"][-1]["receptores"].index("humor")
        assert med["modelos_por_dia"][-1]["desfecho"][v.x][ih] < 0          # a mao ensinou o mal da x ao modelo do planejador


def test_g_sem_credito_falha_alto_se_a_mao_mexer_no_cerebro(monkeypatch):
    original = bv.PoliticaLobos.fruta_na_mao

    def com_credito(self, tipo, obs_antes, obs_depois):
        original(self, tipo, obs_antes, obs_depois)
        self.motivos.append({"n": -1})                                       # qualquer coisa fora dos modelos

    monkeypatch.setattr(bv.PoliticaLobos, "fruta_na_mao", com_credito)
    v = _bp().vida(bv.EspecPQP("P1-plan", "T1", 101))                       # a vida e o replay com o mesmo cerebro mexido
    with pytest.raises(RuntimeError, match="G-SEM-CREDITO"):
        _bp().medir(v)


# ------------------------------------------------------------------ 4. quanto o plano decide, a legibilidade e o G2


def test_o_plano_decide_e_e_legivel_numa_vida():
    v = _vida("P1-plan", "T1")
    med = _med("P1-plan", "T1")
    cerebro = v.motor.politica._pm.cerebro._interna
    motivos = cerebro.motivos
    pl = med["plano"]
    assert med["g_plano"] == G and med["g2"] == {"planejador": True, "decisoes_com_termo": pl["com_termo"], "conferido": False}
    assert pl["com_termo"] > 0 and 0 < pl["decidiu"] <= pl["com_alvo"]
    assert len(pl["por_dia"]) == 3 and sum(r["decisoes"] for r in pl["por_dia"]) == len(motivos) == med["decisoes"]
    # contra os motivos do cerebro: o alvo que o plano mudou so existe em decisao com alvo
    assert sum(r["decidiu_alvo"] for r in pl["por_dia"]) == sum(1 for m in motivos if (m.get("alvo_plano") or {}).get("plano_decidiu"))
    assert sum(r["decidiu_acao_todas"] for r in pl["por_dia"]) == sum(1 for m in motivos if (m.get("plano") or {}).get("plano_decidiu"))
    assert sum(r["com_termo"] for r in pl["por_dia"]) == sum(
        1 for m in motivos if any(x != 0 for x in m["contribuicoes"].get(LOBO_PLANEJAMENTO, {}).values())
        or any(x != 0 for x in (m.get("alvo_plano") or {}).get("termos", {}).values()))
    for r in pl["por_dia"]:
        assert r["fracao"] is None or 0 <= r["fracao"] <= 1
    leg = med["legibilidade"]
    assert leg["com_fator"] == sum(leg["fatores"].values()) and 0 < leg["com_fator"] <= len(motivos)
    for fator, texto in leg["textos"].items():
        assert FATORES[fator.split("(")[0]]["marcador"] in texto              # o texto do adulto com o marcador do fator


def _dec(tick, n, alvo=True):
    return {"tick": tick, "n_motivo": n, "alvo": {"tipo": "comida"} if alvo else None, "acao": "comer"}


def _mot(n, termo_acao=0, decidiu_acao=None, termos_alvo=None, decidiu_alvo=None, fator=None):
    m = {"n": n, "acao": "comer", "contribuicoes": {"impulsos": {"comer": 1.0}}}
    if decidiu_acao is not None:
        m["contribuicoes"][LOBO_PLANEJAMENTO] = {"comer": termo_acao}
        m["plano"] = {"plano_decidiu": decidiu_acao, "fator": fator if decidiu_acao else None}
    if decidiu_alvo is not None:
        m["alvo_plano"] = {"termos": termos_alvo or {}, "plano_decidiu": decidiu_alvo, "fator": None}
    return m


def test_plano_da_vida_com_a_resposta_conhecida():
    T = TICKS_POR_DIA
    decisoes = [_dec(0, 0), _dec(15, 1), _dec(30, 2, alvo=False), _dec(T, 3), _dec(T + 15, 4)]
    motivos = [_mot(0, 0.5, True, {"comida": 7}, False, fator=["plano_comida", "b"]),   # a acao mudou: decidiu
               _mot(1, 0.0, False, {"comida": 0}, True),                                 # o alvo mudou (termo no alvo): decidiu
               _mot(2, 0.2, True, None, None),                                           # a acao mudou, sem alvo: fora do denominador
               _mot(3, 0.0, False, {"comida": 0}, False),                                # nada (termo zero)
               _mot(4, 0.1, False, {"comida": 3}, False)]                                # termo, sem mudar nada
    r = bv.plano_da_vida(decisoes, motivos, True, 2)
    d0, d1 = r["plano"]["por_dia"]
    assert (d0["decisoes"], d0["com_alvo"], d0["decidiu"], d0["decidiu_acao"], d0["decidiu_alvo"], d0["decidiu_acao_todas"]) == (3, 2, 2, 1,
                                                                                                                               1, 2)
    assert d0["fracao"] == 1.0 and d0["com_termo"] == 2 and d0["fracao_acao_todas"] == 2 / 3
    assert (d1["com_alvo"], d1["decidiu"], d1["com_termo"], d1["fracao"]) == (2, 0, 1, 0.0)
    assert r["plano"]["decidiu"] == 2 and r["plano"]["com_alvo"] == 4 and r["g2"]["decisoes_com_termo"] == 3
    assert r["legibilidade"]["com_fator"] == 1 and r["legibilidade"]["fatores"] == {"plano_comida": 1}
    assert list(r["legibilidade"]["textos"]) == ["plano_comida(b)"] and "vi ali" in r["legibilidade"]["textos"]["plano_comida(b)"]
    with pytest.raises(RuntimeError, match="motivo"):
        bv.plano_da_vida(decisoes, motivos[:1] + motivos[2:] + motivos[:1], True, 2)
    with pytest.raises(RuntimeError, match="motivos"):
        bv.plano_da_vida(decisoes, motivos[:-1], True, 2)


def test_o_g2_falha_alto_com_o_termo_no_p1():
    T = TICKS_POR_DIA
    sem = [{"n": 0, "acao": "comer", "contribuicoes": {"impulsos": {"comer": 1.0}}}]
    r = bv.plano_da_vida([_dec(0, 0)], sem, False, 1)
    assert r["g2"] == {"planejador": False, "decisoes_com_termo": 0, "conferido": True}
    for mot in (_mot(0, 0.0, False, None, None), _mot(0, 0.0, None, {"comida": 0}, False), _mot(0, 0.3, False, None, None)):
        with pytest.raises(RuntimeError, match="G2"):
            bv.plano_da_vida([_dec(0, 0)], [mot], False, 1)
    assert T > 0


def test_o_g2_numa_vida_do_p1():
    v = _bp().vida(bv.EspecPQP("P1", "T1", 202))
    med = _bp().medir(v)
    assert med["g2"]["conferido"] and med["g2"]["decisoes_com_termo"] == 0 and med["plano"]["decidiu"] == 0
    cerebro = v.motor.politica._pm.cerebro._interna
    assert all(LOBO_PLANEJAMENTO not in m["contribuicoes"] and "plano" not in m and "alvo_plano" not in m for m in cerebro.motivos)


def test_a_fracao_da_regra_com_a_resposta_conhecida():
    linhas = [{"dia": d, "com_alvo": c, "decidiu": k} for d, c, k in ((0, 10, 9), (1, 4, 1), (2, 6, 2), (3, 0, 0))]
    med = {"plano": {"por_dia": linhas}}
    assert bv.fracao_plano_dias(med, (1, 2)) == {"com_alvo": 10, "decidiu": 3, "fracao": 0.3}
    assert bv.fracao_plano_dias(med, (3, 3)) == {"com_alvo": 0, "decidiu": 0, "fracao": None}
    with pytest.raises(ValueError, match="dias"):
        bv.fracao_plano_dias(med, (2, 4))
