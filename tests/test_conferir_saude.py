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


# ---------------------------------------------------------------- etapa 2: o registro por mês (G-CONCAT)
import registro_por_mes as rpm  # noqa: E402

BASE = json.loads((RAIZ / rpm.LOTES).read_text(encoding="utf-8"))["base"]["commit"]


def _registro_minimo(tmp: Path) -> None:
    """O índice, os arquivos do mês, os lotes e a cópia da etapa 0 num diretório à parte."""
    for rel in [rpm.REGISTRO, rpm.LOTES, rpm.COPIA, *[p.relative_to(RAIZ).as_posix() for p in (RAIZ / rpm.PASTA).iterdir()]]:
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RAIZ / rel, tmp / rel)


@pytest.fixture
def git_registro(monkeypatch):
    """O registro antigo de cada commit vem do git do repositório de verdade; `extras` simula commits que não existem."""
    extras: dict[str, str] = {}
    original = rpm.git_show

    def falso(raiz, commit, caminho):
        return extras[commit] if commit in extras else original(RAIZ, commit, caminho)
    monkeypatch.setattr(rpm, "git_show", falso)
    monkeypatch.setattr(conferir_saude, "registro_do_commit", lambda raiz, commit: falso(raiz, commit, rpm.REGISTRO))
    return extras


def test_registro_repositorio_passa():
    falhas, n = conferir_saude.conferir_registro(RAIZ)
    assert falhas == [] and n >= 219


def test_registro_concatenacao_e_a_base_byte_a_byte():
    antigo = rpm.git_show(RAIZ, BASE, rpm.REGISTRO)
    concat = b"".join(p.read_bytes() for p in sorted((RAIZ / rpm.PASTA).iterdir())).decode("utf-8")
    assert concat.startswith(antigo)
    assert concat.startswith((RAIZ / rpm.COPIA).read_bytes().decode("utf-8"))


def test_registro_partir_devolve_o_texto():
    texto = rpm.git_show(RAIZ, BASE, rpm.REGISTRO)
    preambulo, secoes = rpm.partir(texto)
    assert preambulo + "".join(t for _, t in secoes) == texto
    with pytest.raises(ValueError):
        rpm.partir("# x\n\n## sem data\n\ntexto\n")


def test_registro_byte_mudado_falha(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    alvo = tmp_path / rpm.PASTA / "2026-09.md"
    alvo.write_bytes(alvo.read_bytes().replace("REPROVADA".encode(), "REPROVADO".encode(), 1))
    falhas, _ = conferir_saude.conferir_registro(tmp_path)
    assert any("G-CONCAT" in f for f in falhas)


def test_registro_secao_que_some_falha(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    alvo = tmp_path / rpm.PASTA / "2026-09.md"
    preambulo, secoes = rpm.partir(rpm.ler(alvo))
    rpm.escrever(alvo, preambulo + "".join(t for _, t in secoes[:3] + secoes[4:]))
    falhas, _ = conferir_saude.conferir_registro(tmp_path)
    assert any("índice" in f for f in falhas) and any("G-CONCAT" in f for f in falhas)


def test_registro_secao_no_indice_falha(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    alvo = tmp_path / rpm.REGISTRO
    rpm.escrever(alvo, rpm.ler(alvo) + "\n## 2026-10-14 — escrita no lugar errado\n\ntexto\n")
    falhas, _ = conferir_saude.conferir_registro(tmp_path)
    assert any("seção datada no índice" in f for f in falhas)


def test_registro_secao_nova_sem_linha_no_indice_falha(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    alvo = tmp_path / rpm.PASTA / "2026-10.md"
    rpm.escrever(alvo, rpm.ler(alvo) + "\n## 2026-10-14 — NOVA (worker X): sem índice\n\ntexto\n")
    falhas, _ = conferir_saude.conferir_registro(tmp_path)
    assert any("índice" in f for f in falhas)
    rpm.escrever(tmp_path / rpm.REGISTRO, rpm.ler(tmp_path / rpm.REGISTRO) + rpm.linha_indice("2026-10-14 — NOVA (worker X): sem índice"))
    assert conferir_saude.conferir_registro(tmp_path)[0] == []


def test_registro_secao_no_mes_errado_falha(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    alvo = tmp_path / rpm.PASTA / "2026-10.md"
    titulo = "2026-11-01 — NOVA (worker X): no mês errado"
    rpm.escrever(alvo, rpm.ler(alvo) + f"\n## {titulo}\n\ntexto\n")
    rpm.escrever(tmp_path / rpm.REGISTRO, rpm.ler(tmp_path / rpm.REGISTRO) + f"- [{titulo}](registro/2026-10.md)\n")
    falhas, _ = conferir_saude.conferir_registro(tmp_path)
    assert any("outro mês" in f for f in falhas)


def test_registro_absorver_lote_e_conferir(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    antigo = rpm.git_show(RAIZ, BASE, rpm.REGISTRO)
    titulo = "2026-10-14 — LOTE (worker X): escrita no formato antigo"
    git_registro["pr-velho"] = antigo + f"\n## {titulo}\n\n- uma linha\n"
    antes = conferir_saude.conferir_registro(tmp_path)[1]
    assert rpm.absorver(tmp_path, "pr-velho") == [titulo]
    falhas, n = conferir_saude.conferir_registro(tmp_path)
    assert falhas == [] and n == antes + 1
    assert rpm.ler(tmp_path / rpm.PASTA / "2026-10.md").endswith(f"\n\n## {titulo}\n\n- uma linha\n")
    with pytest.raises(ValueError):                       # de novo: nada novo
        rpm.absorver(tmp_path, "pr-velho")
    alvo = tmp_path / rpm.PASTA / "2026-10.md"            # o texto do lote mudado depois falha
    rpm.escrever(alvo, rpm.ler(alvo).replace("- uma linha", "- outra linha"))
    assert any("lote pr-velho" in f for f in conferir_saude.conferir_registro(tmp_path)[0])


def test_registro_absorver_secao_mudada_falha(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    antigo = rpm.git_show(RAIZ, BASE, rpm.REGISTRO)
    git_registro["pr-que-reescreve"] = antigo.replace("Estado em disco no início", "Estado no início", 1) + "\n## 2026-10-14 — X\n\ntexto\n"
    with pytest.raises(ValueError, match="outro texto"):
        rpm.absorver(tmp_path, "pr-que-reescreve")
    git_registro["pr-que-renomeia"] = antigo.replace("REPROVADA", "REPROVADO", 1) + "\n## 2026-10-14 — X\n\ntexto\n"
    with pytest.raises(ValueError, match="no meio"):
        rpm.absorver(tmp_path, "pr-que-renomeia")


def test_registro_absorver_mes_novo(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    antigo = rpm.git_show(RAIZ, BASE, rpm.REGISTRO)
    git_registro["pr-novembro"] = antigo + "\n## 2026-11-02 — NOVEMBRO (worker X): o primeiro do mês\n\ntexto\n"
    rpm.absorver(tmp_path, "pr-novembro")
    assert rpm.ler(tmp_path / rpm.PASTA / "2026-11.md") == "## 2026-11-02 — NOVEMBRO (worker X): o primeiro do mês\n\ntexto\n"
    assert conferir_saude.conferir_registro(tmp_path)[0] == []


def test_registro_arquivo_estranho_na_pasta_falha(tmp_path, git_registro):
    _registro_minimo(tmp_path)
    (tmp_path / rpm.PASTA / "notas.md").write_text("x\n", encoding="utf-8")
    assert conferir_saude.conferir_registro(tmp_path)[0]


