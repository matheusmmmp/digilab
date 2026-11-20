"""Parte B: memoria curta de vida que muda o comportamento."""

import ast
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.memoria import FATORES_MEMORIA, ORIGEM_ESPERADA, PoliticaBanditMemoria  # noqa: E402
from digilab.motivo import indices_eventos_dono, motivos_de_vida  # noqa: E402
from digilab.policies import PoliticaBandit  # noqa: E402
from digilab.protocol import (  # noqa: E402
    PROTOCOLO_ARENA_V1,
    PROTOCOLO_ARENA_V1_MEMORIA,
    PROTOCOLOS,
    Status,
    bracos_do_protocolo,
)
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402

DIAS, ORC = 3, 48


def _vida(dono="atencioso", semente=202, politica=None):
    return simular_vida(dono, criar_dono(dono), politica or PoliticaBanditMemoria(), semente, DIAS, ORC)


@pytest.fixture(scope="module")
def vidas():
    return {d: _vida(d) for d in ("atencioso", "relapso", "aleatorio", "incoerente")}


def test_replay_bit_a_bit_com_memoria(vidas):
    for dono, v in vidas.items():
        r = reproduzir_com_feedback(v.motor.log, lambda c: PoliticaBanditMemoria(c), semente=202)
        assert r.estado() == v.motor.estado(), dono
        assert r.acoes_recentes(10**9) == v.motor.acoes_recentes(10**9), dono
        assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(
            v.motor.politica.estado_interno(), sort_keys=True), dono


def test_orcamento_identico_entre_bracos(vidas):
    n = {d: sum(1 for e in v.motor.log if e.tipo == "acao_usuario") for d, v in vidas.items()}
    assert set(n.values()) == {ORC}


def test_memoria_muda_comportamento():
    com = _vida()
    sem = _vida(politica=PoliticaBandit())
    assert com.motor.acoes_recentes(10**9) != sem.motor.acoes_recentes(10**9)


def test_refs_da_memoria_apontam_para_acao_do_dono_esperada(vidas):
    for dono, v in vidas.items():
        eventos = list(v.motor.log)
        indices = indices_eventos_dono(v.motor.log)
        mem = v.motor.politica.memoria
        for fator, ordinal in mem.refs().items():
            if ordinal is None:
                continue
            ev = eventos[indices[ordinal - 1]]
            assert ev.tipo == "acao_usuario" and AcaoUsuario(ev.valor) is ORIGEM_ESPERADA[fator], (dono, fator)


def test_evento_ref_dos_motivos_de_memoria(vidas):
    for dono, v in vidas.items():
        _, emb = motivos_de_vida(v.motor.log, lambda c: PoliticaBanditMemoria(c), 202)
        eventos = list(v.motor.log)
        for m in emb.motivos:
            for r in m.evento_ref:
                assert 0 <= r < len(eventos) and eventos[r].tipo == "acao_usuario", (dono, m)
                assert eventos[r].tick <= m.tick
            for f in m.fatores:
                if f in FATORES_MEMORIA and m.evento_ref:
                    valores = {AcaoUsuario(eventos[r].valor) for r in m.evento_ref}
                    assert ORIGEM_ESPERADA[f] in valores, (dono, m)


def test_combate_v2_nao_importa_memoria():
    for arq in (RAIZ / "digilab" / "combate_v2").glob("*.py"):
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            nomes = []
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom):
                nomes = [no.module or ""] + [a.name for a in no.names]
            assert not any("memoria" in n for n in nomes), arq.name
        assert "memoria" not in arq.read_text(encoding="utf-8").lower() or arq.name == "__init__.py", arq.name


def test_protocolo_memoria():
    PROTOCOLO_ARENA_V1_MEMORIA.validar()
    assert PROTOCOLOS["arena-v1-memoria"] is PROTOCOLO_ARENA_V1_MEMORIA
    assert "ARENA_V2" not in " ".join(PROTOCOLOS).upper()
    campos_v1 = PROTOCOLO_ARENA_V1.campos()
    campos = PROTOCOLO_ARENA_V1_MEMORIA.campos()
    assert set(campos) - set(campos_v1) == {"memoria"}
    assert campos["memoria"].status is Status.PROPOSTO
    assert PROTOCOLO_ARENA_V1.hash().startswith("adce99fc3fdc")
    assert {p for _, _, p in bracos_do_protocolo(PROTOCOLO_ARENA_V1_MEMORIA)} == {"bandit_memoria"}
    assert [d for _, d, _ in bracos_do_protocolo(PROTOCOLO_ARENA_V1_MEMORIA)] == list(PROTOCOLO_ARENA_V1.v("bracos"))


def test_run_memoria_reduzida_grava_referencia_sem_memoria(tmp_path):
    import run_arena

    cfg = {"saida": str(tmp_path / "m"), "protocolo": "arena-v1-memoria", "protocolo_substituicoes": {
        "dias_simulados": 1, "orcamento_interacoes": 16, "partidas_por_par": 1, "estados_sonda": 4,
        "amostras_por_estado": 20, "bootstrap_reamostragens": 200}}
    (tmp_path / "c.json").write_text(json.dumps(cfg))
    assert run_arena.main(["--config", str(tmp_path / "c.json")]) in (0, 2)
    m = json.loads((tmp_path / "m" / "metrics.json").read_text())
    assert set(m["interacoes_por_pet"].values()) == {16}
    comp = m["divergencia_com_x_sem_memoria"]
    assert comp["com_memoria"] == m["divergencia_resumo"]["jsd_media_entre_bracos"]
    assert set(comp["sem_memoria"]) == {"artifacts/metrics.json", "artifacts_ablacao/metrics.json"}
    pol = json.loads((tmp_path / "m" / "vidas" / "atencioso@101.politica.json").read_text())
    assert pol["nome"] == "bandit_thompson_memoria" and "memoria" in pol
