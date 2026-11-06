"""H8 (PreToolUse, no frontmatter de cada agente): o escopo de cada papel da frente UX_TELA_PET. Uso: `h8_escopo.py <papel>`.

A tarefa é a `docs/TAREFA_V3_UX_TELA_PET.md`, seções 3.2 e 3.3 (etapa A1). O hook não entra no `settings.json`: cada agente
(`.claude/agents/*.md`, etapa A2) o declara no próprio frontmatter, com o papel como argumento. Assim o limite vem do harness, não de um
pedido no prompt.

Os papéis:
- **designer:** escreve só em `docs/pranchas/ux-pet/` e no `docs/PROPOSTAS_V3_UX_TELA_PET.md`; nenhum comando de shell.
- **implementador:** escreve no projeto, menos estes lugares:
  - o motor, os gabaritos, o save, as rotas e o hash do jogo (`web/app/motor/`, `web/app/test/gabaritos/`, `web/app/src/save.ts`,
    `web/app/src/rotas.ts`);
  - a pesquisa e o servidor (`digilab/`, `experiments/`, `servidor/`);
  - as capturas de referência (as pastas do H6).

  O shell dele não passa por aqui: quem o cobre é o H6.
- **testador:** nenhuma escrita. No shell, só estes comandos:
  - `npm run build`, `npm run e2e`, `npm run capturas` e `npx playwright test`, sempre sem `--update-snapshots`/`-u`;
  - leitura (`ls`, `cat`, `git diff`…);
  - nenhum redirecionamento `>`.

Um papel desconhecido bloqueia: um agente com o hook mal configurado não ganha escopo livre.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, ler_evento, raiz_do_projeto  # noqa: E402
from h3_main import segmentos  # noqa: E402
from h6_capturas import (FERRAMENTAS_DE_EDICAO, FERRAMENTAS_DE_SHELL, atualiza_referencia, protegido,  # noqa: E402
                         so_leitura)

PAPEIS = ("designer", "implementador", "testador")
DESIGNER_PASTAS = ("docs/pranchas/ux-pet/",)
DESIGNER_ARQUIVOS = ("docs/PROPOSTAS_V3_UX_TELA_PET.md",)
IMPLEMENTADOR_NEGADOS = ("web/app/motor/", "web/app/test/gabaritos/", "web/app/src/save.ts", "web/app/src/rotas.ts", "digilab/",
                         "experiments/", "servidor/")
TESTADOR_NPM = {"build", "e2e", "capturas"}
REDIRECIONAMENTO = re.compile(r"(?<![0-9&])>{1,2}(?!&)")


def relativo(alvo: str, raiz: Path, cwd: Path) -> str | None:
    """O caminho relativo à raiz, com `/` e na caixa original; None se cai fora do projeto."""
    caminho = Path(alvo)
    if not caminho.is_absolute():
        caminho = cwd / caminho
    absoluto = Path(os.path.abspath(caminho))
    try:
        rel = Path(os.path.relpath(absoluto, raiz)).as_posix()
    except ValueError:                         # outro disco no Windows
        return None
    return None if rel == ".." or rel.startswith("../") else rel


def casa(rel: str, prefixos: tuple[str, ...]) -> bool:
    baixo = rel.lower()
    return any(baixo == p.lower().rstrip("/") or baixo.startswith(p.lower()) for p in prefixos)


def checar_edicao(papel: str, alvo: str, raiz: Path, cwd: Path) -> str | None:
    if papel == "testador":
        return "H8: o testador não escreve arquivos; devolve as falhas e os diffs ao Gerente."
    rel = relativo(alvo, raiz, cwd)
    if rel is None:
        return f"H8: o {papel} só escreve dentro do projeto ({alvo} está fora)."
    if papel == "designer":
        if casa(rel, DESIGNER_PASTAS) or rel.lower() in (a.lower() for a in DESIGNER_ARQUIVOS):
            return None
        return f"H8: o designer só escreve em docs/pranchas/ux-pet/ e em docs/PROPOSTAS_V3_UX_TELA_PET.md, não em {rel}."
    if casa(rel, IMPLEMENTADOR_NEGADOS):
        return (f"H8: o implementador não mexe em {rel} (o motor, os gabaritos, o save, as rotas e o hash do jogo, a pesquisa e o servidor "
                "ficam fora da interface; docs/TAREFA_V3_UX_TELA_PET.md, seção 3.2).")
    if protegido(alvo, raiz, cwd):
        return f"H8: {rel} é uma captura de referência; só muda com a aprovação do Matheus (H6)."
    return None


def comando_do_testador(tokens: list[str]) -> bool:
    resto = [t for t in tokens if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t)]   # VAR=valor na frente
    if not resto:
        return True
    if re.match(r"^\$env:[A-Za-z_][A-Za-z0-9_]*$", resto[0], re.I) and len(resto) >= 2 and resto[1].startswith("="):
        return True                            # $env:X = "y" no PowerShell
    if re.match(r"^\$env:[A-Za-z_][A-Za-z0-9_]*=", resto[0], re.I):
        return True
    if atualiza_referencia(resto):
        return False
    nome = Path(resto[0]).stem.lower()
    if nome == "npm":
        return len(resto) >= 3 and resto[1] == "run" and resto[2] in TESTADOR_NPM
    if nome == "npx":
        return len(resto) >= 3 and resto[1] == "playwright" and resto[2] == "test"
    return so_leitura(resto) and nome not in ("find",)   # o find tem -delete e -exec


def checar_shell(papel: str, comando: str) -> str | None:
    if papel == "designer":
        return "H8: o designer não roda comandos; escreve o plano e a prancha."
    if papel == "implementador":
        return None                            # o shell do implementador é coberto pelo H6 (e pelo H1/H3 da sessão)
    if REDIRECIONAMENTO.search(comando):
        return "H8: o testador não redireciona saída para arquivo."
    for tokens in segmentos(comando):
        if not comando_do_testador(tokens):
            return ("H8: o testador só roda npm run build/e2e/capturas, npx playwright test (sem --update-snapshots/-u) e leitura; "
                    f"não: {' '.join(tokens)}")
    return None


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in PAPEIS:
        bloquear(f"H8: papel desconhecido {sys.argv[1:]!r}; o frontmatter do agente deve chamar h8_escopo.py com um de {PAPEIS}.")
    papel = sys.argv[1]
    evento = ler_evento()
    ferramenta = evento.get("tool_name") or ""
    entrada = evento.get("tool_input") or {}
    raiz = raiz_do_projeto(evento)
    cwd = Path(evento.get("cwd") or raiz)
    motivo = None
    if ferramenta in FERRAMENTAS_DE_EDICAO:
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or entrada.get("path")
        motivo = checar_edicao(papel, alvo, raiz, cwd) if alvo else f"H8: {ferramenta} sem caminho."
    elif ferramenta in FERRAMENTAS_DE_SHELL:
        motivo = checar_shell(papel, str(entrada.get("command") or ""))
    if motivo:
        bloquear(motivo)


if __name__ == "__main__":
    main()
