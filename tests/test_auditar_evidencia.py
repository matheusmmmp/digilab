"""Testes da auditoria da evidência (tools/auditar_evidencia.py), num repositório git pequeno feito no teste."""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import auditar_evidencia as ae  # noqa: E402


def _git(raiz: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, check=True, text=True).stdout.strip()


def _commit(raiz: Path, msg: str) -> str:
    _git(raiz, "add", "-A")
    _git(raiz, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)
    return _git(raiz, "rev-parse", "HEAD")


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    raiz = tmp_path / "r"
    raiz.mkdir()
    _git(raiz, "init", "-q")
    _git(raiz, "config", "core.autocrlf", "false")
    (raiz / "docs").mkdir()
    plano = b"# plano\nregra escrita antes\n"
    (raiz / "docs" / "PLANO.md").write_bytes(plano)
    c_plano = _commit(raiz, "plano")
    (raiz / "codigo.py").write_text("x = 1\n")
    c_codigo = _commit(raiz, "codigo")
    run = raiz / "artifacts_t" / "run"
    run.mkdir(parents=True)
    resultado = b'{"r": 1}\n'
    medidas = b'{"m": [1, 2]}\n'
    (run / "resultado.json").write_bytes(resultado)
    (run / "medidas.json.gz").write_bytes(gzip.compress(medidas, mtime=0))
    meta = {
        "git_head": c_codigo, "git_limpo": True, "python": "3.13.0", "inicio": "2026-01-01T00:00:00",
        "plano_sha256": hashlib.sha256(plano.replace(b"\n", b"\r\n")).hexdigest(),   # o disco do Windows: CRLF
        "artefatos_sha256": {"resultado.json": hashlib.sha256(resultado).hexdigest(),
                             "medidas.json": hashlib.sha256(medidas).hexdigest()},
    }
    (run / "meta.json").write_text(json.dumps(meta))
    (raiz / "docs" / "RESULTADO.md").write_text("# resultado\n")
    c_run = _commit(raiz, "run")
    monkeypatch.chdir(raiz)
    return {"plano": c_plano, "codigo": c_codigo, "run": c_run}


EXP = {
    "nome": "T", "pergunta": "p", "meta": "artifacts_t/run/meta.json", "plano": "docs/PLANO.md",
    "plano_meta": "plano_sha256", "resultado_doc": "docs/RESULTADO.md",
    "artefatos": {"resultado.json": "artifacts_t/run/resultado.json",
                  "medidas.json": "artifacts_t/run/medidas.json.gz"},
    "vidas": None,
}


def test_acha_o_plano_pelo_sha_e_confere_a_ordem(repo):
    linha = ae.auditar_experimento(repo["run"], EXP)
    assert linha["codigo"] == repo["codigo"] and linha["codigo_completo"]
    assert linha["plano_commit_com_esse_sha"]["commit"] == repo["plano"]
    assert linha["plano_commit_com_esse_sha"]["codificacao"] == "crlf"
    assert linha["plano_ancestral_do_codigo"] is True
    assert linha["comando_no_meta"] is False
    assert linha["meta_adicionado"]["commit"] == repo["run"]


def test_confere_os_artefatos_contra_o_meta(repo):
    art = ae.auditar_experimento(repo["run"], EXP)["artefatos"]
    assert art["resultado.json"]["confere_meta"] is True
    assert art["medidas.json"]["confere_meta"] is True          # pelo conteúdo descomprimido do .gz
    assert "sha256_descomprimido" in art["medidas.json"]


def test_artefato_que_nao_confere(repo):
    (Path("artifacts_t/run/resultado.json")).write_bytes(b'{"r": 2}\n')
    c = _commit(Path("."), "outro resultado")
    assert ae.auditar_experimento(c, EXP)["artefatos"]["resultado.json"]["confere_meta"] is False


def test_plano_que_nao_existe_com_esse_sha(repo):
    meta = json.loads(Path("artifacts_t/run/meta.json").read_text())
    meta["plano_sha256"] = "0" * 64
    Path("artifacts_t/run/meta.json").write_text(json.dumps(meta))
    c = _commit(Path("."), "plano trocado")
    linha = ae.auditar_experimento(c, EXP)
    assert linha["plano_commit_com_esse_sha"] is None
    assert "plano_ancestral_do_codigo" not in linha


def test_caminho_ausente_falha_alto(repo):
    exp = dict(EXP, meta="artifacts_t/run/nao_existe.json")
    with pytest.raises(SystemExit):
        ae.auditar_experimento(repo["run"], exp)


def test_metas_sem_sha(repo):
    Path("artifacts_t/outra").mkdir()
    Path("artifacts_t/outra/meta.json").write_text(json.dumps({"fontes_sha256": {}}))
    c = _commit(Path("."), "meta sem sha")
    r = ae.metas_sem_sha(c)
    assert r["metas_lidos"] == 2
    assert r["lacunas"] == [{"caminho": "artifacts_t/outra/meta.json", "motivo": "sem SHA do código"}]
