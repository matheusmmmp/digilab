"""P4, etapa 3 (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secoes 3.2 e 4): o cerebro A com o planejador nas vidas do J5, com o contrato ligado
pela chave `contrato` da bancada do J5 (os sensores e o controlador; as paredes desligadas, P4-4).

- A config: a chave e bool; com ela, so as sementes dos testes (a run da P4 e do plano dela, com as faixas da P4-8).
- G2: com `"contrato": false`, as vidas do J5 do gabarito da etapa 0 (tests/gabaritos/p4_vidas_de_hoje.json) saem iguais.
- A fumaca dos quatro bracos (P4-5), so o T1 (o protocolo do plano da P4), nas sementes 101 e 202, pelo `rodar_pqp`: as vidas rodam ate o
  fim, sao rejogadas do disco (G1, os modelos do mundo incluidos) e medidas (o G-SEM-CREDITO e o congelamento falham alto na medida).
- P4-2, o cerebro sem entrada nova: trocar por lixo o registro do contrato no `ocorrido` e a `orientacao` da percepcao nao muda nada da
  vida (o log, o estado, o mundo, o cerebro e os modelos).
- Nenhum numero se recalibra (P4-6): o `g_plano` e o `ganho_gosto` da config sao os do adendo 9, os mesmos com e sem o contrato.
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_p4 as g4  # noqa: E402
from bancada import pet_que_pensa as pqp  # noqa: E402

from digilab.config import CONFIG_CONTRATO_LIGADO  # noqa: E402

GRAVADO = json.loads(g4.ARQUIVO.read_text(encoding="utf-8"))
BRACOS = ("P1", "P1-plan", "P1-plan-desfecho", "P1-plan-cong")


def _cfg(**troca) -> dict:
    return {**g4.config_j5(), **troca}


# ================================================================== a config
def test_a_chave_da_bancada():
    assert bv.bancada_pqp_da_config(_cfg()).contrato is False                     # o padrao: desligada
    assert bv.bancada_pqp_da_config(_cfg(contrato=True)).contrato is True
    with pytest.raises(ValueError, match="contrato"):
        bv.bancada_pqp_da_config(_cfg(contrato=1))
    with pytest.raises(TypeError, match="contrato"):
        replace(bv.bancada_pqp_da_config(_cfg()), contrato="sim")
    with pytest.raises(bv.SementeSemPlano, match="P4"):
        bv.bancada_pqp_da_config(_cfg(contrato=True, sementes=[101, 61101]))


def test_nenhum_numero_se_recalibra():
    a, b = bv.bancada_pqp_da_config(_cfg()), bv.bancada_pqp_da_config(_cfg(contrato=True))
    assert a.g_plano == b.g_plano and a.bancada.cfg_consequencia == b.bancada.cfg_consequencia
    assert a.bancada.cfg_lobos == b.bancada.cfg_lobos and a.cfg_modelo == b.cfg_modelo and a.cfg_corpo() == b.cfg_corpo()


# ================================================================== G2
def test_g2_com_a_chave_explicita_desligada():
    assert g4.vidas_j5(_cfg(contrato=False)) == GRAVADO["j5_adendo8"]


# ================================================================== a fumaca dos quatro bracos
@pytest.fixture(scope="module")
def fumaca(tmp_path_factory):
    cfg = _cfg(contrato=True, bracos=list(BRACOS), protocolos=["T1"], sementes=[101, 202])
    return bv.rodar_pqp(cfg, tmp_path_factory.mktemp("p4") / "fumaca"), cfg


def test_a_fumaca_dos_quatro_bracos_roda_ate_o_fim(fumaca):
    r, _cfg_f = fumaca
    assert set(r["vidas"]) == {f"{b}~T1@{s}" for b in BRACOS for s in (101, 202)}
    for nome, v in r["vidas"].items():
        assert v.motor.cct == CONFIG_CONTRATO_LIGADO and v.motor.contrato_decisoes, nome
        assert v.motor.politica is not None
        med = r["medidas"][nome]
        assert med["g_sem_credito"]["violacoes"] == 0 and "t1" in med, nome
        braco = bv.braco_pqp(v.espec.braco)
        assert med["congelamento"]["partes"] == sorted(braco.congela), nome
        if braco.congela:
            assert med["congelamento"]["conferido"] is True, nome
        if braco.planejador:
            assert v.motor.politica._pm.cerebro.modelo is not None, nome


def test_a_fumaca_grava_a_chave_no_meta(fumaca, tmp_path_factory):
    r, cfg = fumaca
    # o meta da pasta da fumaca (o rodar_pqp grava junto das vidas)
    assert cfg["contrato"] is True
    pasta = next(p for p in tmp_path_factory.getbasetemp().rglob("fumaca") if (p / "meta.json").is_file())
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert meta["contrato"] is True and meta["cfg_contrato"] == CONFIG_CONTRATO_LIGADO.__dict__


def test_o_contrato_muda_o_andar_e_nao_os_numeros(fumaca):
    r, _ = fumaca
    hoje = bv.bancada_pqp_da_config(_cfg())
    v_hoje = hoje.vida(bv.EspecPQP("P1-plan", "T1", 101))
    v_com = r["vidas"]["P1-plan~T1@101"]
    assert "contrato_decisoes" not in v_hoje.motor.resumo_mundo_fisico()
    com_alvo = [d for d in v_com.motor.resumo_mundo_fisico()["decisoes"] if d["alvo"] is not None]
    assert len(com_alvo) == len(v_com.motor.contrato_decisoes)
    assert bv.resumo_motor(v_hoje.motor) != bv.resumo_motor(v_com.motor)       # o andar e a visao mudaram a vida


# ================================================================== P4-2: o cerebro sem entrada nova
def test_p4_2_o_cerebro_nao_le_o_registro_nem_a_orientacao(monkeypatch):
    bp = bv.bancada_pqp_da_config(_cfg(contrato=True))
    espec = bv.EspecPQP("P1-plan", "T1", 202)
    base = bp.vida(espec)

    class Lixo(pqp.MotorMundoMudanca):
        def _registro_contrato(self, *a, **kw):
            reg = super()._registro_contrato(*a, **kw)              # o registro de verdade fica no resumo
            return {"lixo": [7, 7, 7], "orientacao": (reg["orientacao"] + 5) % 16, "parou_por": "lixo"}

        def _perceber(self, tick):
            p = super()._perceber(tick)
            return replace(p, orientacao=(p.orientacao + 7) % 16)    # a visao foi a do cone; so o campo muda

    monkeypatch.setattr(pqp, "MotorMundoMudanca", Lixo)
    v = bp.vida(espec)
    assert isinstance(v.motor, Lixo)
    assert v.motor.log.para_jsonl() == base.motor.log.para_jsonl()
    assert bv.resumo_motor(v.motor) == bv.resumo_motor(base.motor)
    assert bv._interno(v.motor) == bv._interno(base.motor)
