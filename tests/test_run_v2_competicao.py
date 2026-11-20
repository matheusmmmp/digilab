"""O orquestrador da competicao entre as regras urgentes (experiments/run_v2_competicao.py; docs/PLANO_ANALISE_V2_V3_COMPETICAO.md) e as
medidas novas de metrics.py (secao 5): a config segue o plano a letra, as margens nao leem o R1, a fumaca do piloto roda de ponta a ponta
(as vidas gravadas e rejogadas do disco, os gates de mecanismo) e a analise da validacao sai das mesmas medidas."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_competicao as rcp  # noqa: E402

from digilab.metrics import competicao_nas_decisoes, exaustao_nas_decisoes  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_competicao"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / nome).read_text(encoding="utf-8"))


def test_as_medidas_novas():
    c = {"abertura_decidiu": True, "aprendido_decidiu": False}
    d = competicao_nas_decisoes([(0, 1, None), (15, 2, None), (30, 2, c), (45, 3, {**c, "abertura_decidiu": False}), (60, 1, None)],
                                (0, 60))
    assert d == {"n": 4, "frac_forcadas": 0.25, "abertas": 2, "frac_abertas": 0.5, "frac_abertura_decidiu": 0.5,
                 "frac_aprendido_decidiu": 0.0}
    assert competicao_nas_decisoes([(0, 1, None)], (0, 15))["frac_abertura_decidiu"] is None
    with pytest.raises(ValueError):
        competicao_nas_decisoes([(0, 1, c)], (0, 15))                 # uma aberta com um candidato so
    with pytest.raises(ValueError):
        competicao_nas_decisoes([(30, 1, None)], (0, 15))             # sem decisao na janela
    assert exaustao_nas_decisoes([(0, 0.1), (15, 0.25), (30, 0.9)], (0, 45)) == {"n": 3, "frac": 1 / 3}


def test_a_config_segue_o_plano():
    assert rcp.modo_da_config(_cfg("fumaca.json")) == "fumaca"
    assert rcp.modo_da_config(_cfg("fumaca_validacao.json")) == "fumaca"
    assert rcp.modo_da_config(_cfg("piloto.json")) == "piloto"
    with pytest.raises(ValueError, match="fora do plano"):
        rcp.modo_da_config({**_cfg("piloto.json"), "kappa": 8})
    with pytest.raises(bv.SementeSemPlano):
        rcp.modo_da_config({**_cfg("piloto.json"), "unidades": {"bases": [59101, 59202, 59303, 59404, 59505], "k": 4,
                                                                "prefixo": "competicao"}})
    with pytest.raises(bv.SementeSemPlano):
        rcp.modo_da_config({**_cfg("piloto.json"), "unidades": {"bases": [12345], "k": 4, "prefixo": "competicao"}})
    with pytest.raises(ValueError, match="K"):
        rcp.modo_da_config({**_cfg("piloto.json"), "unidades": {**_cfg("piloto.json")["unidades"], "k": 5}})
    if not (RAIZ / rcp.SAIDA["piloto"] / "resultado.json").exists():
        with pytest.raises(FileNotFoundError):                         # a validacao precisa do piloto e do adendo
            rcp.modo_da_config({**_cfg("piloto.json"), "fase": "validacao",
                                "unidades": {"bases": list(rcp.BASES_VALIDACAO), "k": 4, "prefixo": "competicao"}})


def _reg(braco, dono, s, d_fe, priv=0.1, saude=0.9):
    return {"braco": braco, "dono": dono, "semente": s, "d_fe": d_fe, "privacao": priv, "saude": saude}


def test_as_margens_nao_leem_o_r1():
    regs = [_reg(b, d, s, 0.30 if b == "P0" else 0.20) for b in ("P0", "R0") for d in rcp.DONOS for s in (1, 2)]
    m = rcp.margens(regs)
    assert abs(m["delta_r1"] - 0.05) < 1e-12 and not m["volta_ao_matheus"]
    assert abs(m["delta_priv"] - 0.025) < 1e-12 and abs(m["delta_saude"] - 0.025) < 1e-12
    with pytest.raises(RuntimeError, match="nao leem"):
        rcp.margens(regs + [_reg("R1", rcp.DONOS[0], 1, 0.1)])
    sem = [_reg(b, d, s, 0.2) for b in ("P0", "R0") for d in rcp.DONOS for s in (1, 2)]
    assert rcp.margens(sem)["volta_ao_matheus"]                       # PC-2: sem escala, o plano volta ao Matheus


def test_a_fumaca_de_ponta_a_ponta(tmp_path):
    """o piloto da fumaca (2 unidades x 16 vidas): as vidas gravadas e rejogadas do disco, os gates de mecanismo, as margens, o N e a
    G-ABRE; e a analise da validacao sobre as mesmas medidas"""
    cfg = _cfg("fumaca.json")
    r = rcp.rodar(cfg, tmp_path / "piloto", processos=2)
    regs = r["registros"]
    assert len(regs) == 2 * len(rcp.DONOS) * len(rcp.BRACOS)
    assert len(list((tmp_path / "piloto" / "vidas").rglob("*.jsonl"))) == len(regs)
    for x in regs:
        assert (x["competicao"]["abertas"] > 0) <= x["competicao_ligada"]       # desligada, nenhuma aberta
    res = r["resultado"]
    assert set(res) >= {"margens", "n", "G-ABRE_piloto", "contrastes_so_relato", "custo"}
    v = rcp.analisar(regs, {**cfg, "fase": "validacao"}, rcp.margens([x for x in regs if x["braco"] in ("P0", "R0")]))
    assert set(v["secundarios"]) == set(rcp.HOLM) and v["G-R1"]["categoria"] in rcp.CATEGORIAS.values()
    assert isinstance(v["leitura"], str)
    with pytest.raises(FileExistsError):
        rcp.rodar(cfg, tmp_path / "piloto", processos=1)
