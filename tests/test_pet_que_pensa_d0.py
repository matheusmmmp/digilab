"""O D0 do pet que pensa (docs/TAREFA_V3_PET_QUE_PENSA.md, secao 4): a medida `medidas_d0_plano`, as conferencias e o resumo."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import pre_run  # noqa: E402
import run_v3_pet_que_pensa_d0 as D0  # noqa: E402
import run_v3_pet_vivo_r1 as R  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO  # noqa: E402

LAM = CONFIG_DIGIBRAIN_INATOS.lambda_sono
URG = CONFIG_DIGIBRAIN_INATOS.urgencia_lambda
PISO = LAM // 2
CFG = json.loads((RAIZ / "experiments/configs/v3_pet_que_pensa/d0.json").read_text(encoding="utf-8"))


def _dec(k: int, escolha: str, energia: int, fome: int = 0, reflexo: bool = False, u=0.5, nada: bool = False, **extra) -> dict:
    return {"k": k, "escolha": [escolha, None, None], "reflexo": reflexo, "u": None if reflexo else u, "nada_a_fazer": nada,
            "afeto": {"urgencias": {"fome": fome, "energia": 0}}, "cadeia": {"leitura": {"energia": energia}}, **extra}


def _vida(decisoes: list[dict]) -> list[dict]:
    return decisoes + [{"k": len(decisoes), "escolha": ["ocioso", None, None], "reflexo": False, "u": None}]


@pytest.fixture(scope="module")
def vida_real():
    """uma vida do HOJE nas sementes dos testes (101, comedouro), com o rastro"""
    return R.orq.cerebro_de(R._vida_de_teste(101, True, 4, lugar="comedouro")[1]).motivos


# ------------------------------------------------------------------ a medida, a mao
def test_as_contas_a_mao():
    vida = _vida([
        _dec(0, "dormir", PISO - 1, reflexo=True),               # abaixo do piso: reflexo duro no desenho tambem
        _dec(1, "dormir", PISO, reflexo=True),                   # na faixa, sem a fome urgente
        _dec(2, "dormir", LAM - 1, fome=URG + 1, reflexo=True),  # na faixa, com a fome urgente: o conflito
        _dec(3, "comer", LAM - 1, fome=URG + 1, reflexo=False),  # na faixa, ja aberta hoje (a guarda da fome): conflito, nao soma de novo
        _dec(4, "dormir", LAM + 10, reflexo=True),               # o sono que segura
        _dec(5, "explorar", 600, fome=URG),                      # aberta, a fome no limite nao e urgente
        _dec(6, "dormir", 700, fome=URG + 5, u=None),            # aberta, sem sorteio, com a fome urgente
        _dec(7, "ocioso", 800, u=None, nada=True),               # aberta, nada a fazer
    ])
    d = met.medidas_d0_plano(vida, LAM, PISO, URG)
    assert d["n"] == 8 and d["com_segurada"] is False
    assert d["fora"] == {"REFLEXO": 3, "SEGURA": 1, "SEGURADA": 0}
    assert d["abertas_hoje"] == 4
    assert (d["abertas_hoje_sorteio"], d["abertas_hoje_nada_a_fazer"], d["abertas_hoje_fome_urgente"], d["abertas_hoje_dormir"]) == (2, 1, 2, 1)
    assert (d["faixa"], d["faixa_fora_reflexo"], d["conflito"], d["conflito_reflexo"], d["conflito_dormir"]) == (3, 1, 2, 1, 1)
    assert d["abaixo_piso"] == 1
    assert d["abertas_plan_teto"] == 4 + 2 and d["abertas_plan_piso"] == 4 + 1
    assert d["F_ABERTAS_HOJE"] == 4 / 8 and d["F_CONFLITO"] == 2 / 8 and d["F_CONFLITO_NA_FAIXA"] == 2 / 3
    assert tuple(d["fora"]) == met.FORA_DA_DISPUTA_D0


def test_a_escolha_segurada():
    vida = _vida([_dec(0, "explorar", 600, segurada=True, u=None), _dec(1, "explorar", 600, segurada=False),
                  _dec(2, "dormir", PISO, reflexo=True, segurada=False)])
    d = met.medidas_d0_plano(vida, LAM, PISO, URG)
    assert d["com_segurada"] is True and d["fora"] == {"REFLEXO": 1, "SEGURA": 0, "SEGURADA": 1} and d["abertas_hoje"] == 1


def test_falha_alto():
    with pytest.raises(ValueError, match="rastro"):
        met.medidas_d0_plano(_vida([]), LAM, PISO, URG)
    with pytest.raises(ValueError, match="piso"):
        met.medidas_d0_plano(_vida([_dec(0, "explorar", 600)]), LAM, LAM + 1, URG)
    with pytest.raises(ValueError, match="piso"):
        met.medidas_d0_plano(_vida([_dec(0, "explorar", 600)]), LAM, 0, URG)
    sem_energia = _dec(0, "explorar", 600)
    sem_energia["cadeia"]["leitura"] = {}
    with pytest.raises(ValueError, match="energia"):
        met.medidas_d0_plano(_vida([sem_energia]), LAM, PISO, URG)
    sem_fome = _dec(0, "explorar", 600)
    sem_fome["afeto"]["urgencias"] = {}
    with pytest.raises(ValueError, match="fome"):
        met.medidas_d0_plano(_vida([sem_fome]), LAM, PISO, URG)
    with pytest.raises(ValueError, match="segurada"):
        met.medidas_d0_plano(_vida([_dec(0, "explorar", 600, segurada=False), _dec(1, "explorar", 600)]), LAM, PISO, URG)
    with pytest.raises(ValueError, match="segurada"):
        met.medidas_d0_plano(_vida([_dec(0, "dormir", 100, reflexo=True, segurada=True)]), LAM, PISO, URG)


# ------------------------------------------------------------------ numa vida de teste
def test_c_d0_numa_vida_de_teste(vida_real):
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    cs = met.medidas_caminho_sono(vida_real, LAM, passo)
    d = met.medidas_d0_plano(vida_real, LAM, PISO, URG)
    D0.conferir_d0("teste", d, cs)
    assert d["fora"]["SEGURA"] == 0 and d["com_segurada"] is False        # o HOJE: sem o sono que segura, sem a C3
    assert d["faixa_fora_reflexo"] == 0                                    # sem o sono que segura, o reflexo pega toda a faixa
    assert d["abertas_plan_teto"] == d["abertas_hoje"] + d["faixa"]
    ruim = copy.deepcopy(d)
    ruim["fora"]["REFLEXO"] += 1
    with pytest.raises(D0.D0Divergiu, match="C-D0"):
        D0.conferir_d0("teste", ruim, cs)


def test_a_medida_e_deterministica_e_nao_mexe_nos_motivos(vida_real):
    antes = json.dumps(vida_real, sort_keys=True)
    a = met.medidas_d0_plano(vida_real, LAM, PISO, URG)
    b = met.medidas_d0_plano(vida_real, LAM, PISO, URG)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert json.dumps(vida_real, sort_keys=True) == antes


def test_escalares_e_resumo(vida_real):
    d = json.loads(json.dumps(met.medidas_d0_plano(vida_real, LAM, PISO, URG)))
    regs = [{"grupo": "run", "braco": "HOJE", "lugar": "comedouro", "semente": s, "dono": dono, "d0": d}
            for s in (1, 2) for dono in ("atencioso", "relapso")]
    r = D0.resumo(regs, "run", "HOJE", "comedouro")
    assert r["vidas"] == 4 and r["unidades"] == 2
    assert r["medidas"]["F_ABERTAS_HOJE"]["media"] == d["F_ABERTAS_HOJE"]
    assert set(r["medidas"]["F_CONFLITO"]["por_dono"]) == {"atencioso", "relapso"}
    with pytest.raises(D0.D0Divergiu):
        D0.resumo(regs, "v38", "HOJE", "longe")


# ------------------------------------------------------------------ a config e a trava
def test_config_e_tarefa():
    D0.conferir_config(CFG)
    with pytest.raises(ValueError):
        D0.conferir_config({**CFG, "fase": "d1"})
    with pytest.raises(ValueError):
        D0.conferir_config({**CFG, "extra": 1})
    D0.exigir_aprovada((RAIZ / D0.TAREFA).read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError):
        D0.exigir_aprovada("**Status: PROPOSTO")
    assert D0.piso_de(LAM) == LAM // 2


def test_o_orquestrador_tem_o_nome_que_o_pre_run_reconhece():
    assert pre_run.RUN.search(D0.ORQUESTRADOR)


def test_os_conjuntos_sao_o_hoje_e_o_v38():
    vidas, nomes = D0.vidas_do_d0()
    assert {(v[0], v[1]) for v in vidas} == set(D0.CONJUNTOS)
    assert len(vidas) == len(nomes) == 2400 + 320
