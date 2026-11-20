"""Testes do orquestrador da EVIDENCIA A2 (experiments/run_v3_ablacao_aprendizado.py): a config, a trava, a faixa, as frações, a regra de
leitura (seção 5.3 do plano) e a fumaça (as sementes de teste, 1 dia, o harness Node de verdade)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))
import bancada_v2 as bv  # noqa: E402
import run_v3_ablacao_aprendizado as ab  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v3_ablacao_aprendizado"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def test_as_configs_seguem_o_plano():
    assert ab.conferir_config(_cfg("run")) == "run" and ab.conferir_config(_cfg("fumaca")) == "fumaca"
    for mudanca in ({"k": 199}, {"dias": 2}, {"primeira": 101}, {"etapa": "fumaca"}):
        with pytest.raises((ValueError, bv.SementeSemPlano)):
            ab.conferir_config({**_cfg("run"), **mudanca})
    with pytest.raises(ValueError):
        ab.conferir_config({**_cfg("run"), "extra": 1})


def test_a_faixa_esta_reservada_e_nao_colide():
    ab.exigir_faixa_reservada()
    outras = [(lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS if (lo, hi) != ab.FAIXA]
    assert all(hi < ab.FAIXA[0] or lo > ab.FAIXA[1] for lo, hi in outras)


def test_a_trava():
    with pytest.raises(RuntimeError, match="APROVADO"):
        ab.exigir_plano_aprovado("# plano\n\n**Status: PROPOSTO, aguardando o Matheus.**\n")
    ab.exigir_plano_aprovado((RAIZ / ab.PLANO).read_text(encoding="utf-8"))


def _vida(semente, dono, braco, acoes, tipos=None, reflexo=0, nada=0):
    n = sum(acoes.values())
    tipos = tipos or {"comida": 0, "cheiro": 0, "bola": 0, "vagar": 0, "ponto": 0, "sem_objeto": n}
    return {"semente": semente, "dono": dono, "braco": braco, "decisoes": n, "acoes": {a: acoes.get(a, 0) for a in ab.ACOES}, "tipos": tipos,
            "reflexo": reflexo, "nada_a_fazer": nada, "morte": None, "recusas": 0, "escolhida": {"incentivo": 0, "habito": 0, "fora_da_lista": 0},
            "unidades_com_aprendido": 1 if braco == "A" else 0}


def test_as_fracoes_falham_alto():
    v = _vida(1, "atencioso", "A", {"dormir": 10})
    assert ab.fracoes(v)["acao:dormir"] == 1.0 and ab.fracoes(v)["tipo:sem_objeto"] == 1.0
    with pytest.raises(RuntimeError, match="nao fecham"):
        ab.fracoes({**v, "decisoes": 11})
    with pytest.raises(RuntimeError, match="sem decisao"):
        ab.fracoes({**v, "decisoes": 0})
    with pytest.raises(RuntimeError, match="faltam"):
        ab.por_unidade([v])


def _vidas(efeito: dict):
    """30 sementes; o A dorme 'efeito[s]' a mais de 100 decisoes, com um ruido que varia pela semente"""
    out = []
    for s in range(30):
        for d in ab.DONOS:
            ruido = (s * 7 + len(d)) % 5
            out.append(_vida(s, d, "B", {"dormir": 50 + ruido, "comer": 50 - ruido}))
            e = efeito.get(s, 0)
            out.append(_vida(s, d, "A", {"dormir": 50 + ruido + e, "comer": 50 - ruido - e}))
    return out


def test_a_regra_de_leitura():
    assert ab.analisar(_vidas({s: 10 for s in range(30)}))["leitura"]["classe"] == "muda"
    r = ab.analisar(_vidas({s: (1 if s % 2 else -1) for s in range(30)}))
    assert r["leitura"]["classe"] == "nula", r["contrastes"]["acao:dormir"]
    ind = ab.leitura({m: {"ic95": {"ic_inferior": 0.01, "ic_superior": 0.02}} for m in ab.MEDIDAS},
                     {m: {"rejeita": False} for m in ab.MEDIDAS})
    assert ind["classe"] == "indeterminado"


@pytest.mark.skipif(shutil.which("node") is None, reason="sem o Node")
def test_a_fumaca_roda_o_harness_e_grava_uma_vez(tmp_path):
    out = ab.rodar(_cfg("fumaca"), tmp_path / "f", CONFIGS / "fumaca.json")
    r, m = out["resultado"], out["meta"]
    assert r["vidas"] == 2 * len(ab.DONOS) * 2 and r["unidades"] == 2
    assert r["leitura"]["classe"] in ("muda", "nula", "indeterminado")
    assert r["descritivo"]["b_unidades_com_aprendido"] == 0 and r["descritivo"]["a_unidades_com_aprendido"] > 0
    assert set(m["artefatos_sha256"]) == {"medidas.json", "resultado.json"} and m["node"] and m["python"] and set(m["codigo_sha256"]) == set(ab.CODIGO)
    with pytest.raises(FileExistsError):
        ab.rodar(_cfg("fumaca"), tmp_path / "f", CONFIGS / "fumaca.json")
