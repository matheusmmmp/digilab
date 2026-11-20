"""O tools/replicar_run.py (EVIDENCIA A3): num repositório git de brinquedo, com um orquestrador falso que grava o meta e os artefatos, a
réplica pelo SHA sai igual byte a byte (com o .gz versionado descomprimido); um orquestrador que muda a saída diverge; o SHA errado, a
árvore suja e o comando com --saida falham alto; a tabela das runs reais aponta para pastas e metas que existem."""
from __future__ import annotations

import gzip
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import replicar_run as rr  # noqa: E402

ORQ = '''import argparse, json, pathlib, sys
ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int); ap.add_argument("--saida")
a = ap.parse_args()
p = pathlib.Path(a.saida); p.mkdir(parents=True)
(p / "medidas.json").write_text(json.dumps({"x": list(range(a.n))}) + "\\n", encoding="utf-8", newline="\\n")
(p / "resultado.json").write_text(json.dumps({"soma": sum(range(a.n))%s}) + "\\n", encoding="utf-8", newline="\\n")
'''


def _git(r: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True, text=True).stdout.strip()


def _repo(tmp: Path, extra: str = "", limpo: bool = True, comando: str = "python orq.py --n 7") -> tuple[Path, str]:
    r = tmp / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    (r / "orq.py").write_text(ORQ % extra, encoding="utf-8", newline="\n")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "codigo")
    sha = _git(r, "rev-parse", "HEAD")
    pasta = r / "artifacts_x" / "run"
    subprocess.run([sys.executable, "orq.py", "--n", "7", "--saida", str(pasta)], cwd=r, check=True)
    medidas = (pasta / "medidas.json").read_bytes()
    (pasta / "medidas.json.gz").write_bytes(gzip.compress(medidas, mtime=123))
    (pasta / "medidas.json").unlink()
    meta = {"git_head": sha, "git_limpo": limpo, "comando": comando, "python": "3.13.0",
            "artefatos_sha256": {"medidas.json": rr.sha256(medidas), "resultado.json": rr.sha256((pasta / "resultado.json").read_bytes())}}
    (pasta / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "artefatos")
    return r, sha


@pytest.fixture
def brinquedo(monkeypatch):
    monkeypatch.setitem(rr.RUNS, "x", {"descricao": "brinquedo", "pasta": "artifacts_x/run",
                                       "artefatos": {"resultado.json": "resultado.json", "medidas.json": "medidas.json.gz"}})


def test_a_replica_sai_igual_byte_a_byte(tmp_path, brinquedo):
    r, sha = _repo(tmp_path)
    rel = rr.replicar("x", sha[:8], r, trabalho=tmp_path / "w")
    assert rel["byte_a_byte"] and rel["fonte_do_comando"] == "meta.json" and rel["comando"][0] == sys.executable
    c = {x["artefato"]: x for x in rel["comparacoes"]}
    assert c["medidas.json"]["sha256_replica"] == c["medidas.json"]["sha256_no_meta"] != c["medidas.json"]["sha256_versionado"]
    assert not (tmp_path / "w").exists()                                     # a worktree sai apagada
    assert _git(r, "status", "--porcelain") == ""                            # e o repositório fica como estava


def test_a_divergencia_e_reportada(tmp_path, brinquedo):
    r, sha = _repo(tmp_path)
    (r / "orq.py").write_text(ORQ % " + 1", encoding="utf-8", newline="\n")  # o código muda depois da run
    _git(r, "commit", "-q", "-am", "muda")
    rel = rr.replicar("x", sha, r, trabalho=tmp_path / "w")                  # a réplica usa o SHA da run, não a HEAD
    assert rel["byte_a_byte"]
    falso = tmp_path / "falsa"
    falso.mkdir()
    (falso / "resultado.json").write_text("{}\n", encoding="utf-8")
    (falso / "medidas.json").write_bytes(gzip.decompress(_git_blob(r, "artifacts_x/run/medidas.json.gz")))
    rel = rr.replicar("x", sha, r, so_comparar=falso)
    assert not rel["byte_a_byte"] and [x["igual"] for x in rel["comparacoes"]] == [False, True]
    assert rr.principal(["x", sha, "--raiz", str(r), "--so-comparar", str(falso)]) == 1


def _git_blob(r: Path, caminho: str) -> bytes:
    return subprocess.run(["git", "-C", str(r), "show", f"HEAD:{caminho}"], check=True, capture_output=True).stdout


def test_falha_alto(tmp_path, brinquedo):
    r, sha = _repo(tmp_path)
    outro = _git(r, "rev-parse", "HEAD")
    with pytest.raises(RuntimeError, match="git_head"):
        rr.replicar("x", outro, r)
    with pytest.raises(KeyError, match="desconhecida"):
        rr.replicar("nada", sha, r)
    with pytest.raises(RuntimeError, match="ja tem --saida"):
        rr.montar_comando(rr.RUNS["x"], {"comando": "python a.py --saida b"}, tmp_path)
    with pytest.raises(RuntimeError, match="nao comeca por python"):
        rr.montar_comando(rr.RUNS["x"], {"comando": "node a.ts"}, tmp_path)
    (tmp_path / "w").mkdir()
    with pytest.raises(FileExistsError):
        rr.replicar("x", sha, r, trabalho=tmp_path / "w")


def test_a_arvore_suja_falha(tmp_path, brinquedo):
    r, sha = _repo(tmp_path, limpo=False)
    with pytest.raises(RuntimeError, match="arvore limpa"):
        rr.replicar("x", sha, r)


def test_as_runs_reais_apontam_para_metas_versionados():
    for nome, spec in rr.RUNS.items():
        meta = json.loads(rr.blob(RAIZ, "HEAD", f"{spec['pasta']}/meta.json"))
        assert meta["git_head"] and meta["git_limpo"] is True, nome
        assert meta.get("comando") or spec.get("comando"), nome
        for versionado in spec["artefatos"].values():
            assert rr.blob(RAIZ, "HEAD", f"{spec['pasta']}/{versionado}"), (nome, versionado)
    c4 = rr.RUNS["c4"]
    meta = json.loads(rr.blob(RAIZ, "HEAD", f"{c4['pasta']}/meta.json"))
    assert meta["git_head"].startswith("a287ba20")
    gz = rr.blob(RAIZ, "HEAD", f"{c4['pasta']}/medidas.json.gz")
    assert rr.sha256(rr.conteudo("medidas.json.gz", gz)) == meta["artefatos_sha256"]["medidas.json"]
