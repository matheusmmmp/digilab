"""O adendo 2 da GV3b do GOSTO_VISUAL (docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md): a regra para as duas TVs sem lugar.

- o caso da falha (D-GV-GV3B-12): o pet na celula (25, 478) do mapa da ilha da GV3b (o mundo do produto, com o enjoo ligado), as TVs a 3
  celulas. Com a regra antiga ("falha", o padrao) o `DuasTVsSemLugar` sobe, um RuntimeError com a mensagem de antes; com a regra
  "sem_sonda" a replica volta so com o registro do caso, e a copia fica sem as duas TVs;
- as replicas que cabem saem iguais nas duas regras, e a sonda com "falha" grava o artefato de antes (sem a chave `sem_lugar`);
- as fases antigas ficam com a regra "falha"; as configs novas (`piloto_enjoo2.json` e `gosto_visual_enjoo2.json`) seguem o adendo 2;
  a trava confere o adendo 2, o adendo 1 e o plano da GV3, todos APROVADOS;
- a faixa 91101...91505 reservada, confirmada pelo coordenador em 2026-11-12, sem cruzar outra nem uma queimada, com unidades novas;
- a contagem das replicas sem lugar contra o teto, e o piloto que passa do teto segura a run;
- a run do adendo 2 recusa rodar sem a pasta do piloto no git, antes de criar a pasta;
- a fumaca da fase nova (a semente 101, 2 dias).
Sementes: as dos testes (101) e as derivadas delas. Nenhuma vida da faixa roda aqui.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_gosto_visual as R  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402
from digilab.config import CONFIG_DUAS_TVS_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.genoma_visao import genoma_visao  # noqa: E402
from digilab.tv import DuasTVsSemLugar  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v3_gosto_visual"
PET_DA_FALHA = (25, 478)                                     # D-GV-GV3B-12: "pet em (25, 478)"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / nome).read_text(encoding="utf-8"))


def _adendo2(status: str = "**Status: APROVADO pelo Matheus em 2026-11-12.**", registro: bool = True) -> str:
    return "\n".join(["# adendo 2", "", status, "", "## 1. algo"] + ([R.TITULO_REGISTRO_ENJOO2] if registro else []) + [""])


@pytest.fixture(scope="module")
def pet_gv3b():
    """um pet da GV3b (o enjoo ligado, o mundo do produto) andado 30 ticks, para ter o cerebro com o olhar"""
    u = R.unidades([101], 1)[0]
    fp, fm = R.fabricas(u["semente"], genoma_visao(u["genoma"]), True)
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, u["semente"])
    m.avancar(30)
    return m


def _no_lugar_da_falha(pet_gv3b):
    m = copy.deepcopy(pet_gv3b)
    m.pet = PET_DA_FALHA
    assert m.mundo.seca(*PET_DA_FALHA)
    return m


# ================================================================== o caso da falha
def test_o_caso_da_falha_levanta_o_erro_com_a_regra_antiga(pet_gv3b):
    assert R.orq.CM.sub * CONFIG_DUAS_TVS_LIGADA.distancia_celulas == 3 * R.orq.CM.sub    # as TVs a 3 celulas
    m = _no_lugar_da_falha(pet_gv3b)
    with pytest.raises(DuasTVsSemLugar, match=r"nao coube em 16 direcoes .*\(pet em \(25, 478\)\)") as e:
        m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 0)
    assert isinstance(e.value, RuntimeError) and e.value.pet == PET_DA_FALHA            # quem nao trata, falha alto como antes
    assert m.mundo.duas_tvs is None
    for r in range(3):                                       # o padrao da sonda e a regra antiga: o erro sobe
        with pytest.raises(DuasTVsSemLugar):
            sd.ler_replica(_no_lugar_da_falha(pet_gv3b), r)
        with pytest.raises(DuasTVsSemLugar):
            sd.ler_replica(_no_lugar_da_falha(pet_gv3b), r, "falha")


def test_o_caso_da_falha_fica_sem_sonda_com_a_regra_nova(pet_gv3b):
    m = _no_lugar_da_falha(pet_gv3b)
    tick = m.estado()["tick"]
    r = sd.ler_replica(m, 1, "sem_sonda")
    assert set(r) == {"replica", "sem_lugar"} and r["replica"] == 1
    assert r["sem_lugar"]["pet"] == list(PET_DA_FALHA) and 0 <= r["sem_lugar"]["direcao_sorteada"] < 16
    assert m.mundo.duas_tvs is None and m.estado()["tick"] == tick                       # a copia nao anda
    with pytest.raises(ValueError, match="regra"):
        sd.ler_replica(_no_lugar_da_falha(pet_gv3b), 0, "mover")


def test_a_replica_que_cabe_sai_igual_nas_duas_regras(pet_gv3b):
    a = sd.ler_replica(copy.deepcopy(pet_gv3b), 0, "falha")
    b = sd.ler_replica(copy.deepcopy(pet_gv3b), 0, "sem_sonda")
    assert "sem_lugar" not in a and json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_as_fases_antigas_ficam_com_a_regra_antiga_e_a_nova_com_sem_sonda():
    assert R.FASES[R.FASE]["sem_lugar"] == R.FASES[R.FASE_ENJOO]["sem_lugar"] == "falha"
    assert R.FASES[R.FASE_ENJOO2]["sem_lugar"] == "sem_sonda" and R.FASES[R.FASE_ENJOO2]["enjoo"]
    assert sd.REGRAS_SEM_LUGAR == ("falha", "sem_sonda")
    with pytest.raises(ValueError, match="regra"):
        sd.sonda(None, (), 101, (1,), 1, "mover")


# ================================================================== as configs e a trava
def test_as_configs_do_adendo_2_seguem_o_adendo():
    for nome, bases, k, modo in (("piloto_enjoo2.json", R.BASES_PILOTO_ENJOO2, R.K_PILOTO, "piloto_enjoo2"),
                                 ("gosto_visual_enjoo2.json", R.BASES_RUN_ENJOO2, R.K_RUN, "gosto_visual_enjoo2")):
        cfg = _cfg(nome)
        assert cfg["fase"] == R.FASE_ENJOO2 and cfg["plano"] == R.PLANO_ENJOO2 and cfg["dias"] == R.DIAS
        assert tuple(cfg["unidades"]["bases"]) == bases and cfg["unidades"]["k"] == k
        assert R.modo_da_config(cfg, _adendo2()) == modo
        assert R.modo_da_config(cfg) == modo                 # o adendo 2 de verdade: APROVADO, com o registro
    assert R.FASES[R.FASE_ENJOO2]["modos"] == ("piloto_enjoo2", "gosto_visual_enjoo2")


def test_a_trava_do_adendo_2(monkeypatch):
    cfg = _cfg("piloto_enjoo2.json")
    with pytest.raises(RuntimeError, match="APROVADO"):
        R.modo_da_config(cfg, _adendo2("**Status: PROPOSTO, a espera do Matheus.**"))
    with pytest.raises(RuntimeError, match="registro"):
        R.modo_da_config(cfg, _adendo2(registro=False))
    with pytest.raises(ValueError):
        R.modo_da_config({**cfg, "plano": R.PLANO_ENJOO}, _adendo2())
    with pytest.raises(bv.SementeSemPlano):                  # as bases queimadas da GV3b na fase nova
        R.modo_da_config({**cfg, "unidades": {"bases": list(R.BASES_PILOTO_ENJOO), "k": 2}}, _adendo2())
    with pytest.raises(bv.SementeSemPlano):                  # as bases novas na fase velha
        R.modo_da_config({**_cfg("piloto_enjoo.json"), "unidades": {"bases": list(R.BASES_PILOTO_ENJOO2), "k": 2}})
    real = R._plano
    for por_baixo in (R.PLANO, R.PLANO_ENJOO):               # o adendo 2 vale sobre o adendo 1 e o plano: os dois aprovados
        sem_marca = real(por_baixo).replace(R.MARCA_APROVADO, "**Status: PROPOSTO")
        monkeypatch.setattr(R, "_plano", lambda plano=R.PLANO, pb=por_baixo, t=sem_marca: t if plano == pb else real(plano))
        with pytest.raises(RuntimeError, match="APROVADO"):
            R.modo_da_config(cfg, _adendo2())
    monkeypatch.setattr(R, "_plano", real)


def test_a_faixa_do_adendo_2_esta_reservada_confirmada_e_nao_cruza_outra_nem_uma_queimada():
    faixas = [f for lo, hi, f in bv.FAIXAS_RESERVADAS if (lo, hi) == R.FAIXA_ENJOO2]
    assert len(faixas) == 1 and "confirmada pelo coordenador, 2026-11-12" in faixas[0]
    assert "PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2" in faixas[0]
    lo, hi = R.FAIXA_ENJOO2
    for a, b, _ in bv.FAIXAS_RESERVADAS:
        if (a, b) != R.FAIXA_ENJOO2:
            assert b < lo or a > hi, f"a faixa cruza {a}...{b}"
    for a, b, _ in bv.FAIXAS_QUEIMADAS:
        assert b < lo or a > hi
    assert all(lo <= b <= 91202 for b in R.BASES_PILOTO_ENJOO2) and all(91303 <= b <= hi for b in R.BASES_RUN_ENJOO2)
    us = R.unidades(R.BASES_PILOTO_ENJOO2, R.K_PILOTO) + R.unidades(R.BASES_RUN_ENJOO2, R.K_RUN)
    velhas = [u for bs in ((R.BASES_PILOTO, R.BASES_RUN), (R.BASES_PILOTO_ENJOO, R.BASES_RUN_ENJOO))
              for b, k in zip(bs, (R.K_PILOTO, R.K_RUN)) for u in R.unidades(b, k)]
    valores = {u["semente"] for u in us} | {u["genoma"] for u in us}
    assert len(valores) == 2 * len(us) == 80
    assert not valores & ({u["semente"] for u in velhas} | {u["genoma"] for u in velhas})


# ================================================================== a contagem, o teto e o piloto no git
def _reg(g: str, d: str, medidas: int, sem: int) -> dict:
    return {"genoma_tipo": g, "dono": d, "medidas": [{}] * medidas, "replicas_sem_lugar": [{}] * sem}


def test_a_contagem_das_replicas_sem_lugar_e_o_teto():
    assert R.TETO_SEM_LUGAR == 0.05
    regs = [_reg(g, d, 100, 0) for g in R.GENOMAS for d in R.DONOS]
    c = R.contar_sem_lugar(regs)
    assert c["total"] == {"tentadas": 600, "sem_lugar": 0, "fracao": 0.0} and not c["passou_do_teto"]
    regs[0] = _reg("proprio", "nenhum", 95, 5)               # 5 em 100 numa celula: no teto, nao passa
    assert not R.contar_sem_lugar(regs)["passou_do_teto"]
    regs[0] = _reg("proprio", "nenhum", 94, 6)               # 6 em 100: a celula passa, o total (6 em 600) nao
    c = R.contar_sem_lugar(regs)
    assert c["celulas_acima_do_teto"] == ["proprio|nenhum"] and c["total"]["fracao"] == 0.01 and c["passou_do_teto"]


def test_a_run_do_adendo_2_recusa_sem_o_piloto_no_git(tmp_path, monkeypatch):
    cfg = _cfg("gosto_visual_enjoo2.json")
    assert R.modo_da_config(cfg) == "gosto_visual_enjoo2"
    with pytest.raises(RuntimeError, match="piloto fora do git"):
        R.rodar(cfg, tmp_path / "run", 1)
    assert not (tmp_path / "run").exists()                   # antes de qualquer pasta e de qualquer vida
    respostas = {"ls-files": None, "status": " M algo.py"}   # o piloto no git, mas o git sujo
    monkeypatch.setattr(R.orq.rc, "_git", lambda *a: a[1] if a[0] == "ls-files" else respostas[a[0]])
    with pytest.raises(RuntimeError, match="git nao esta limpo"):
        R.exigir_piloto_no_git(R.FASES[R.FASE_ENJOO2])


# ================================================================== a fumaca
def test_a_fumaca_do_adendo_2(tmp_path):
    cfg = {"fase": R.FASE_ENJOO2, "plano": R.PLANO_ENJOO2, "unidades": {"bases": [101], "k": 1}, "dias": 2}
    assert R.modo_da_config(cfg) == "fumaca"
    out = R.rodar(cfg, tmp_path / "fumaca", 1, boot=20)
    r, meta = out["resultado"], out["meta"]
    assert r["fase"] == R.FASE_ENJOO2 and r["vidas"] == 6 and meta["enjoo_tela"]["ligada"] is True
    assert meta["sem_lugar"] == {"regra": "sem_sonda", "teto": R.TETO_SEM_LUGAR} and meta["plano_adendo1"] == R.PLANO_ENJOO
    assert set(r["sem_lugar"]) == {"teto", "total", "celulas", "celulas_acima_do_teto", "passou_do_teto"}
    assert r["sem_lugar"]["total"]["tentadas"] == 6 * sd.REPLICAS
    assert "sem_lugar_passou_do_teto" in r["conferencia"]
    assert all("replicas_sem_lugar" in x for x in out["registros"])
    sondas = list((tmp_path / "fumaca" / "vidas").glob("*_sonda.json"))
    assert len(sondas) == 6 and all(json.loads(p.read_text(encoding="utf-8"))["sem_lugar"] == "sem_sonda" for p in sondas)
