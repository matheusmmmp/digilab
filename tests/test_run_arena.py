"""Etapa 6 - orquestrador, gate e deteccao de convergencia (config reduzido)."""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_arena  # noqa: E402
from digilab.protocol import PROTOCOLO_ARENA_V1  # noqa: E402

REDUZIDO = {
    "dias_simulados": 1,
    "orcamento_interacoes": 16,
    "partidas_por_par": 1,
    "estados_sonda": 4,
    "amostras_por_estado": 20,
    "bootstrap_reamostragens": 200,
}


def _rodar(tmp_path, **extra):
    cfg = {"saida": str(tmp_path / "out"), "protocolo_substituicoes": {**REDUZIDO, **extra}}
    caminho = tmp_path / "cfg.json"
    caminho.write_text(json.dumps(cfg))
    rc = run_arena.main(["--config", str(caminho)])
    return rc, json.loads((tmp_path / "out" / "metrics.json").read_text())


def test_run_grava_artefatos_com_sementes_e_hash(tmp_path):
    rc, m = _rodar(tmp_path)
    assert rc in (0, 2)
    out = tmp_path / "out"
    for arq in ("metrics.json", "divergence.json", "matches.csv", "partidas.jsonl", "preflight.json"):
        assert (out / arq).exists(), arq
    assert m["sementes_coorte"] == list(PROTOCOLO_ARENA_V1.v("sementes_coorte"))
    assert len(m["protocolo_hash"]) == 64
    assert m["protocolo_hash"] != m["protocolo_canonico_hash"]
    assert set(m["interacoes_por_pet"].values()) == {16}
    assert any("NAO CANONICO" in a for a in m["avisos"])
    assert any("PROPOSTO" in a for a in m["avisos"])
    rc_central = m["resultado_central"]
    assert rc_central["n"] == 5 and rc_central["ic_inferior"] <= rc_central["media"] <= rc_central["ic_superior"]


def test_convergencia_reprova_a_run_com_mensagem_explicita(tmp_path):
    rc, m = _rodar(tmp_path, limiar_divergencia_jsd_bits=0.99)
    assert rc == 2
    assert m["status_run"] == "REPROVADA"
    regra = next(r for r in m["gate"] if r["regra"] == "divergencia_entre_politicas")
    assert not regra["ok"]
    assert "NAO TEM PROFUNDIDADE SUFICIENTE" in regra["mensagem"]


def test_config_com_chave_desconhecida_falha(tmp_path):
    caminho = tmp_path / "cfg.json"
    caminho.write_text(json.dumps({"saida": "x", "turbo": True}))
    with pytest.raises(KeyError):
        run_arena.main(["--config", str(caminho)])
