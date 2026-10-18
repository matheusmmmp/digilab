"""A geração da tarefa (tools/nova_tarefa.py) a partir do modelo do repositório."""
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import nova_tarefa as nt  # noqa: E402


@pytest.fixture
def raiz(tmp_path):
    for rel in (nt.MODELO, nt.PARALELO):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RAIZ / rel, tmp_path / rel)
    return tmp_path


def test_gera_a_partir_do_modelo(raiz):
    destino = nt.gerar(raiz, "INFRA_POC", "documentacao", "Claude Code", "conferir os links", "2026-10-18")
    texto = destino.read_text(encoding="utf-8")
    assert destino.name == "TAREFA_V2_INFRA_POC.md"
    assert texto.startswith("# TAREFA V2 — INFRA_POC (2026-10-18)")
    assert "`v2-infra-poc`" in texto and "Status: ABERTA." in texto
    assert "Categoria: documentacao." in texto
    assert "Origem: Claude Code, 2026-10-18: conferir os links." in texto
    assert "`docs/PLANO_ANALISE_V2_INFRA_POC.md`" in texto
    # o resto do modelo fica para o coordenador, com os campos novos
    assert "## 7. Critérios de aceitação" in texto and "## 8. Precisa do Matheus" in texto
    assert "<Uma frase." in texto


def test_nao_sobrescreve(raiz):
    nt.gerar(raiz, "X", "documentacao", "Matheus", "a", "2026-10-18")
    with pytest.raises(FileExistsError):
        nt.gerar(raiz, "X", "documentacao", "Matheus", "a", "2026-10-18")


@pytest.mark.parametrize("frente, categoria, origem, resumo", [
    ("infra-poc", "documentacao", "Matheus", "a"),
    ("X", "outra", "Matheus", "a"),
    ("X", "documentacao", "Gemini", "a"),
    ("X", "documentacao", "Matheus", "  "),
])
def test_entrada_invalida_levanta(raiz, frente, categoria, origem, resumo):
    with pytest.raises(ValueError):
        nt.gerar(raiz, frente, categoria, origem, resumo, "2026-10-18")


def test_mensagem_do_worker_vem_do_documento_do_paralelo(raiz):
    msg = nt.mensagem_worker(raiz, "INFRA_POC")
    assert "docs/TAREFA_V2_INFRA_POC.md" in msg and "v2-infra-poc" in msg
    assert "<" not in msg and "Merge só quando o Matheus pedir" in msg


def test_modelo_mudado_falha_alto(raiz):
    (raiz / nt.MODELO).write_text("# outro modelo\n", encoding="utf-8")
    with pytest.raises(ValueError, match="o modelo mudou"):
        nt.gerar(raiz, "X", "documentacao", "Matheus", "a", "2026-10-18")
