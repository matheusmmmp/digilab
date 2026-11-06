"""A2 da UX_TELA_PET (docs/TAREFA_V3_UX_TELA_PET.md, seções 3.2 e 3.4): os seis agentes de .claude/agents/ e o registro local de
componentes do jogo web (web/app/registry.json).

O CI instala só o pytest, então o frontmatter é lido por linha, sem YAML: os campos de uma linha (name, model, tools, disallowedTools) e
os comandos dos hooks.
"""
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
AGENTES = RAIZ / ".claude" / "agents"
APP = RAIZ / "web" / "app"
ESCRITA = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL = {"Bash", "PowerShell"}
ESPERADOS = {"ux-designer": "opus", "ux-implementador": "sonnet", "ux-browser-tester": "sonnet", "rev-replay": "opus",
             "rev-a11y": "sonnet", "rev-cena": "sonnet"}


def frontmatter(nome: str) -> tuple[dict, str, str]:
    """(os campos de uma linha, o frontmatter inteiro, o corpo) do agente."""
    texto = (AGENTES / f"{nome}.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    assert m, f"{nome}: sem frontmatter"
    campos = {}
    for linha in m.group(1).splitlines():
        c = re.match(r"^([A-Za-z]+):\s*(.+)$", linha)
        if c:
            campos[c.group(1)] = c.group(2).strip()
    return campos, m.group(1), m.group(2)


def lista(valor: str | None) -> set[str]:
    return {t.strip() for t in (valor or "").split(",") if t.strip()}


def test_os_seis_agentes_e_nenhum_outro():
    assert sorted(p.stem for p in AGENTES.glob("*.md")) == sorted(ESPERADOS)


@pytest.mark.parametrize("nome", sorted(ESPERADOS))
def test_campos_basicos(nome):
    campos, _, corpo = frontmatter(nome)
    assert campos["name"] == nome
    assert campos["model"] == ESPERADOS[nome]
    assert campos.get("description") and "tools" in campos
    assert "docs/TAREFA_V3_UX_TELA_PET.md" in corpo
    assert not (lista(campos["tools"]) & lista(campos.get("disallowedTools")))


@pytest.mark.parametrize("nome", ["rev-replay", "rev-a11y", "rev-cena"])
def test_revisores_so_leitura(nome):
    campos, _, _ = frontmatter(nome)
    assert lista(campos["tools"]) == {"Read", "Grep", "Glob"}
    assert ESCRITA | SHELL <= lista(campos["disallowedTools"])


def test_testador_sem_escrita_com_playwright_so_nele():
    campos, bruto, _ = frontmatter("ux-browser-tester")
    assert not (lista(campos["tools"]) & ESCRITA)
    assert ESCRITA <= lista(campos["disallowedTools"])
    assert "mcp__playwright__*" in lista(campos["tools"]) and "@playwright/mcp" in bruto
    for outro in ESPERADOS:
        if outro != "ux-browser-tester":
            assert "playwright" not in frontmatter(outro)[1].lower(), outro


def test_designer_sem_shell():
    campos, _, _ = frontmatter("ux-designer")
    assert not (lista(campos["tools"]) & SHELL)
    assert SHELL <= lista(campos["disallowedTools"])


@pytest.mark.parametrize("nome,papel", [("ux-designer", "designer"), ("ux-implementador", "implementador"),
                                        ("ux-browser-tester", "testador")])
def test_hook_h8_com_o_papel_certo(nome, papel):
    _, bruto, _ = frontmatter(nome)
    papeis = re.findall(r"h8_escopo\.py\\?\"?\s+([a-z]+)", bruto)
    assert papeis == [papel]
    for script in re.findall(r"\.claude/hooks/([a-z0-9_]+\.py)", bruto):
        assert (RAIZ / ".claude" / "hooks" / script).exists(), script


def test_implementador_e_testador_com_h6():
    for nome in ("ux-implementador", "ux-browser-tester"):
        assert "h6_capturas.py" in frontmatter(nome)[1], nome


def test_registro_local_cobre_o_kit_hx():
    reg = json.loads((APP / "registry.json").read_text(encoding="utf-8"))
    assert reg["$schema"] == "https://ui.shadcn.com/schema/registry.json"
    arquivos = [f["path"] for item in reg["items"] for f in item["files"]]
    assert all((APP / a).exists() for a in arquivos), [a for a in arquivos if not (APP / a).exists()]
    kit = sorted(f"src/componentes/hx/{p.name}" for p in (APP / "src" / "componentes" / "hx").glob("*.tsx"))
    assert set(kit) <= set(arquivos)
    assert "src/componentes/ui/button.tsx" in arquivos
    pacote = json.loads((APP / "package.json").read_text(encoding="utf-8"))
    deps = {**pacote.get("dependencies", {}), **pacote.get("devDependencies", {})}
    assert all(d in deps for item in reg["items"] for d in item["dependencies"])


def test_components_json_sem_registro_publico_novo():
    """A UX-4 recomenda não usar registro público além do padrão; o components.json segue sem `registries`."""
    assert "registries" not in json.loads((APP / "components.json").read_text(encoding="utf-8"))
