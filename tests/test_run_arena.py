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


# ------------------------------------------------------------ ablacao (etapa 2)


def _rodar_ablacao(tmp_path, **extra):
    cfg = {
        "saida": str(tmp_path / "ab"),
        "protocolo": "arena-v1-ablacao",
        "protocolo_substituicoes": {**REDUZIDO, **extra},
    }
    caminho = tmp_path / "ab.json"
    caminho.write_text(json.dumps(cfg))
    rc = run_arena.main(["--config", str(caminho)])
    return rc, json.loads((tmp_path / "ab" / "metrics.json").read_text())


def test_ablacao_roda_oito_bracos_com_politica_do_protocolo(tmp_path):
    rc, m = _rodar_ablacao(tmp_path)
    assert rc in (0, 2)
    assert len(m["bracos"]) == 8
    assert m["bracos_dono_politica"]["atencioso-instinto"] == {"dono": "atencioso", "politica": "instinto"}
    assert set(m["interacoes_por_pet"].values()) == {16}
    assert len(m["interacoes_por_pet"]) == 8 * 5
    vidas = tmp_path / "ab" / "vidas"
    for s in PROTOCOLO_ARENA_V1.v("sementes_coorte"):
        inst = json.loads((vidas / f"atencioso-instinto@{s}.politica.json").read_text())
        assert inst == {"nome": "instinto", "parametros_aprendidos": 0}
        band = json.loads((vidas / f"atencioso-bandit@{s}.politica.json").read_text())
        assert band["nome"] != "instinto"
    assert set(m["atencioso_vs_aleatorio_por_politica"]) == {"bandit", "instinto"}
    assert m["resultado_central"] == m["atencioso_vs_aleatorio_por_politica"]["bandit"]
    ef = m["efeito_do_treino"]
    assert ef["efeito"]["n"] == 5
    assert ef["veredito"] in {"TREINO_AUMENTA_A_VANTAGEM", "TREINO_REDUZ_A_VANTAGEM", "INDISTINGUIVEL_DE_ZERO"}
    for s, v in ef["por_semente"].items():
        pb = m["atencioso_vs_aleatorio_por_politica"]["bandit"]["por_semente"][s]
        pi = m["atencioso_vs_aleatorio_por_politica"]["instinto"]["por_semente"][s]
        assert v["efeito"] == pytest.approx((2 * pb - 1) - (2 * pi - 1))


def test_ablacao_mesmo_dono_mesma_rng_nas_duas_politicas():
    """Com instinto nos dois lados, trocar so o rotulo do braco nao muda a vida."""
    from digilab.donos import criar_dono
    from digilab.policy import PoliticaInstinto
    from digilab.treino import simular_vida

    a = simular_vida("atencioso-bandit", criar_dono("atencioso"), PoliticaInstinto(), 101, 1, 16, rotulo_dono="atencioso")
    b = simular_vida("atencioso-instinto", criar_dono("atencioso"), PoliticaInstinto(), 101, 1, 16, rotulo_dono="atencioso")
    assert a.motor.log.para_jsonl() == b.motor.log.para_jsonl()
    assert a.motor.estado() == b.motor.estado()


def test_protocolo_desconhecido_no_config_falha(tmp_path):
    caminho = tmp_path / "cfg.json"
    caminho.write_text(json.dumps({"saida": "x", "protocolo": "arena-v9"}))
    with pytest.raises(KeyError, match="protocolo desconhecido"):
        run_arena.main(["--config", str(caminho)])


# ------------------------------------------------------------ gate da ablacao (etapa 4)


def test_ablacao_registra_divergencia_instinto_exatamente_zero(tmp_path):
    rc, m = _rodar_ablacao(tmp_path)
    div = json.loads((tmp_path / "ab" / "divergence.json").read_text())
    inst = div["jsd_entre_bracos_instinto"]
    assert inst["maximo"] == 0.0 and inst["media"] == 0.0
    assert inst["n_pares"] == 6 * 5 * 5  # C(4,2) pares de donos x 5 x 5 sementes
    regra = next(r for r in m["gate"] if r["regra"] == "divergencia_instinto_zero")
    assert regra["ok"]
    assert m["divergencia_resumo"]["jsd_entre_bracos_instinto"] == inst


def test_ablacao_reprova_se_bandit_converge(tmp_path):
    rc, m = _rodar_ablacao(tmp_path, limiar_divergencia_jsd_bits=0.99)
    assert rc == 2 and m["status_run"] == "REPROVADA"
    regra = next(r for r in m["gate"] if r["regra"] == "divergencia_entre_politicas")
    assert not regra["ok"]
    assert "pets bandit de bracos diferentes" in regra["mensagem"]
    assert "NAO TEM PROFUNDIDADE SUFICIENTE" in regra["mensagem"]


def test_ablacao_divergencia_instinto_nao_nula_e_bug(tmp_path, monkeypatch):
    original = run_arena.divergencia_politicas

    def adulterada(*args, **kwargs):
        div, dists = original(*args, **kwargs)
        chave = next(k for k in div.pares if all("instinto@" in n for n in k) and k[0].split("@")[0] != k[1].split("@")[0])
        div.pares[chave] = 1e-12
        return div, dists

    monkeypatch.setattr(run_arena, "divergencia_politicas", adulterada)
    with pytest.raises(run_arena.DivergenciaInstintoNaoNula, match="BUG"):
        _rodar_ablacao(tmp_path)
