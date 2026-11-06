"""INFRA_AGENTES E2 (docs/TAREFA_V3_INFRA_AGENTES.md, seção 3.2): os revisores de .claude/agents/ são somente leitura, cada um com a lente
dele. O limite é o do harness (o `tools` e o `disallowedTools` do frontmatter), e este teste confere que ele está escrito.

O frontmatter é lido à mão (só `chave: valor` e listas `- item`), para não depender do PyYAML.
"""
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
AGENTES = RAIZ / ".claude" / "agents"
ESCRITA = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
REVISORES = ("revisor-metodo", "revisor-determinismo", "auditor-numeros")


def ler(nome: str) -> tuple[dict, str]:
    """(o frontmatter, o corpo) de .claude/agents/<nome>.md; levanta se o arquivo não abre com o bloco `---`."""
    texto = (AGENTES / f"{nome}.md").read_text(encoding="utf-8")
    if not texto.startswith("---\n"):
        raise ValueError(f"{nome}.md sem frontmatter")
    bloco, corpo = texto[4:].split("\n---\n", 1)
    campos: dict = {}
    chave = None
    for linha in bloco.splitlines():
        if linha.startswith("  - "):
            campos[chave].append(linha[4:].strip())
        elif ":" in linha:
            chave, _, valor = linha.partition(":")
            chave = chave.strip()
            campos[chave] = valor.strip() if valor.strip() else []
        elif linha.strip():
            raise ValueError(f"{nome}.md: linha do frontmatter que não entendo: {linha!r}")
    return campos, corpo


def lista(valor) -> set[str]:
    return set(valor) if isinstance(valor, list) else {v.strip() for v in valor.split(",") if v.strip()}


@pytest.mark.parametrize("nome", REVISORES)
def test_o_revisor_existe_e_so_le(nome):
    campos, corpo = ler(nome)
    assert campos["name"] == nome
    assert campos["description"]
    assert campos["model"] in {"opus", "sonnet", "haiku"}
    assert not lista(campos["tools"]) & (ESCRITA | {"Bash", "PowerShell"})
    assert ESCRITA <= lista(campos["disallowedTools"])
    assert "Read" in lista(campos["tools"])
    # todo achado aponta onde está: arquivo:linha nos revisores; a linha do documento no auditor
    assert ("a linha do documento" if nome == "auditor-numeros" else "arquivo e a linha") in corpo


def test_o_revisor_de_metodo_carrega_a_literatura():
    campos, corpo = ler("revisor-metodo")
    assert "literatura-digilab" in lista(campos["skills"])
    for termo in ("FAIXAS_RESERVADAS", "FAIXAS_QUEIMADAS", "PLANO_ANALISE_V3_", "SEM FONTE", "PROPOSTO", "novidade"):
        assert termo in corpo, termo


def test_o_revisor_de_determinismo_tem_a_lente_dele():
    _, corpo = ler("revisor-determinismo")
    for termo in ("derivar_semente", "byte a byte", "engine.py", "constantes.test.mjs", "exportar_", "rev-replay"):
        assert termo in corpo, termo


def test_o_testador_e_o_da_ux_com_a_secao_3_4():
    """E4 (seção 3.4): um testador só, o ux-browser-tester da UX_TELA_PET (D-IA-5), sem escrita, com tipos, Vitest e e2e, a porta própria
    e o H8 no frontmatter."""
    assert not (AGENTES / "testador-navegador.md").exists()
    campos, corpo = ler("ux-browser-tester")
    assert not lista(campos["tools"]) & ESCRITA
    assert ESCRITA <= lista(campos["disallowedTools"])
    for termo in ("npm run tipos", "npm test", "npm run e2e", "DIGILAB_PORTA_E2E", "console", "*-diff.png"):
        assert termo in corpo, termo
    texto = (AGENTES / "ux-browser-tester.md").read_text(encoding="utf-8")
    assert "h8_escopo.py\\\" testador" in texto or 'h8_escopo.py\\" testador' in texto


def test_o_auditor_tem_as_tres_classes():
    _, corpo = ler("auditor-numeros")
    for classe in ("VERIFICADO", "DIVERGENTE", "SEM FONTE"):
        assert f"**{classe}:**" in corpo, classe
