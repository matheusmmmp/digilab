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
    for rel in {conferir_saude.COPIA, conferir_saude.MAPA, "CLAUDE.md", *mapa.values()}:
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RAIZ / rel, tmp / rel)


def test_secao_que_some_falha(tmp_path):
    _copia_minima(tmp_path)
    alvo = tmp_path / "docs/historico/claude/combate.md"
    texto = alvo.read_text(encoding="utf-8")
    inicio = texto.index("## Combate V2 (")
    fim = texto.index("## ", inicio + 3)
    alvo.write_text(texto[:inicio] + texto[fim:], encoding="utf-8")
    falhas = conferir_saude.conferir(tmp_path)
    assert any("Combate V2 (" in f for f in falhas)


def test_secao_alterada_falha(tmp_path):
    _copia_minima(tmp_path)
    alvo = tmp_path / "docs/historico/claude/v1_pesquisa.md"
    texto = alvo.read_text(encoding="utf-8")
    alvo.write_text(texto.replace("0,72 pontos", "0,73 pontos", 1), encoding="utf-8")
    assert conferir_saude.conferir(tmp_path)


def test_raiz_grande_falha(tmp_path):
    _copia_minima(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("x\n" * 200, encoding="utf-8")
    assert any("200" in f for f in conferir_saude.conferir(tmp_path))


def test_secao_sem_destino_falha(tmp_path):
    _copia_minima(tmp_path)
    mapa_p = tmp_path / conferir_saude.MAPA
    mapa = json.loads(mapa_p.read_text(encoding="utf-8"))
    mapa.pop(next(iter(mapa)))
    mapa_p.write_text(json.dumps(mapa, ensure_ascii=False), encoding="utf-8")
    assert any("sem destino" in f for f in conferir_saude.conferir(tmp_path))


def test_copia_sem_secao_levanta():
    with pytest.raises(ValueError):
        conferir_saude.secoes("sem cabeçalho nenhum\n")
