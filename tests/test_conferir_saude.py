"""O G-NADA-PERDIDO da rodada de saúde (tools/conferir_saude.py): passa no repositório e falha quando uma seção some ou muda."""
import json
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import conferir_saude  # noqa: E402


def test_repositorio_passa():
    assert conferir_saude.conferir(RAIZ) == []


def test_toda_secao_da_copia_esta_no_mapa():
    copia = (RAIZ / conferir_saude.COPIA).read_text(encoding="utf-8")
    mapa = json.loads((RAIZ / conferir_saude.MAPA).read_text(encoding="utf-8"))
    nomes = [n for n, _ in conferir_saude.secoes(copia)]
    assert sorted(nomes) == sorted(mapa)


def _copia_minima(tmp: Path) -> None:
    """A cópia, o mapa, os destinos e o CLAUDE.md da raiz num diretório à parte."""
    mapa = json.loads((RAIZ / conferir_saude.MAPA).read_text(encoding="utf-8"))
    lotes = json.loads((RAIZ / conferir_saude.POSTERIORES).read_text(encoding="utf-8"))["lotes"]
    destinos_lotes = {d for l in lotes for d in l["secoes"].values()}
    for rel in {conferir_saude.COPIA, conferir_saude.MAPA, conferir_saude.POSTERIORES, "CLAUDE.md", *mapa.values(), *destinos_lotes}:
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RAIZ / rel, tmp / rel)


@pytest.fixture
def git_do_repositorio(monkeypatch):
    """O diretório temporário não é um repositório: o CLAUDE.md de cada commit vem do git do repositório de verdade."""
    original = conferir_saude.claude_do_commit
    monkeypatch.setattr(conferir_saude, "claude_do_commit", lambda raiz, commit: original(RAIZ, commit))


def test_lote_posterior_coberto():
    lotes = json.loads((RAIZ / conferir_saude.POSTERIORES).read_text(encoding="utf-8"))["lotes"]
    assert lotes and all(l["secoes"] for l in lotes)


def test_secao_de_lote_que_some_falha(tmp_path, git_do_repositorio):
    _copia_minima(tmp_path)
    lote = json.loads((tmp_path / conferir_saude.POSTERIORES).read_text(encoding="utf-8"))["lotes"][0]
    nome, destino = next(iter(lote["secoes"].items()))
    alvo = tmp_path / destino
    texto = alvo.read_text(encoding="utf-8")
    inicio = texto.index(nome)
    fim = texto.find("\n## ", inicio + 3)
    alvo.write_text(texto[:inicio] + (texto[fim + 1:] if fim >= 0 else ""), encoding="utf-8")
    assert any("lote" in f and nome[:40] in f for f in conferir_saude.conferir(tmp_path))


def test_commit_inexistente_falha(tmp_path):
    _copia_minima(tmp_path)
    p = tmp_path / conferir_saude.POSTERIORES
    p.write_text(json.dumps({"lotes": [{"commit": "0000000", "secoes": {}}]}), encoding="utf-8")
    assert any("0000000" in f for f in conferir_saude.conferir(tmp_path))


def test_secao_que_some_falha(tmp_path, git_do_repositorio):
    _copia_minima(tmp_path)
    alvo = tmp_path / "docs/historico/claude/combate.md"
    texto = alvo.read_text(encoding="utf-8")
    inicio = texto.index("## Combate V2 (")
    fim = texto.index("## ", inicio + 3)
    alvo.write_text(texto[:inicio] + texto[fim:], encoding="utf-8")
    falhas = conferir_saude.conferir(tmp_path)
    assert any("Combate V2 (" in f for f in falhas)


def test_secao_alterada_falha(tmp_path, git_do_repositorio):
    _copia_minima(tmp_path)
    alvo = tmp_path / "docs/historico/claude/v1_pesquisa.md"
    texto = alvo.read_text(encoding="utf-8")
    alvo.write_text(texto.replace("0,72 pontos", "0,73 pontos", 1), encoding="utf-8")
    assert conferir_saude.conferir(tmp_path)


def test_raiz_grande_falha(tmp_path, git_do_repositorio):
    _copia_minima(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("x\n" * 200, encoding="utf-8")
    assert any("200" in f for f in conferir_saude.conferir(tmp_path))


def test_secao_sem_destino_falha(tmp_path, git_do_repositorio):
    _copia_minima(tmp_path)
    mapa_p = tmp_path / conferir_saude.MAPA
    mapa = json.loads(mapa_p.read_text(encoding="utf-8"))
    mapa.pop(next(iter(mapa)))
    mapa_p.write_text(json.dumps(mapa, ensure_ascii=False), encoding="utf-8")
    assert any("sem destino" in f for f in conferir_saude.conferir(tmp_path))


def test_copia_sem_secao_levanta():
    with pytest.raises(ValueError):
        conferir_saude.secoes("sem cabeçalho nenhum\n")
