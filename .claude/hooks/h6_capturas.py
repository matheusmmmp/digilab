"""H6 (PreToolUse, Edit|Write|MultiEdit|NotebookEdit e Bash|PowerShell): as capturas de referência só mudam com a aprovação na hora.

A tarefa é a `docs/TAREFA_V3_UX_TELA_PET.md`, seção 3.3 (etapa A1). O e2e pixel a pixel é o gate da interface, e a referência dele não
pode ser regravada por um agente sem o Matheus ver.

As pastas protegidas são duas:
- qualquer pasta `*-snapshots/` (as referências do Playwright dentro do repositório);
- a pasta das referências do portão, que fica fora do git: `DIGILAB_CAPTURAS`, relativa a `web/app/` como no
  `web/app/playwright.capturas.config.ts`. O padrão é `../../artifacts_v2_front_react/capturas`.

O que o hook faz em cada caso:
- **Ferramenta de edição** com o caminho numa pasta protegida: nega (código 2).
- **Comando de shell que roda o Playwright com `--update-snapshots` ou `-u`** (`npx playwright test -u`, `npm run e2e -- -u`,
  `npm run capturas -- --update-snapshots`): pede a aprovação na hora (a decisão "ask", como o H3). É o único caminho para trocar uma
  referência.
- **Comando de shell que cita uma pasta protegida:** deixa passar se é só leitura (`ls`, `cat`, `git diff`…); nega se escreve (qualquer
  outro comando, ou um redirecionamento `>` para lá).

O hook lê o texto do comando: um script que escreva lá por dentro não passa por aqui. É o mesmo limite do H3.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, ler_evento, perguntar, raiz_do_projeto  # noqa: E402
from h3_main import segmentos  # noqa: E402

FERRAMENTAS_DE_EDICAO = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
FERRAMENTAS_DE_SHELL = {"Bash", "PowerShell"}
CAPTURAS_PADRAO = "../../artifacts_v2_front_react/capturas"
SO_LEITURA = {"ls", "dir", "cat", "type", "head", "tail", "less", "more", "wc", "file", "stat", "du", "find", "grep", "rg", "pwd", "cd",
              "echo", "sha256sum", "md5sum", "get-childitem", "gci", "get-content", "gc", "get-item", "test-path", "get-filehash",
              "select-string", "resolve-path"}
GIT_SO_LEITURA = {"diff", "status", "log", "show", "ls-files", "blame"}
REDIRECIONAMENTO = re.compile(r"(?<![0-9&])>{1,2}\s*(\"[^\"]+\"|'[^']+'|[^\s;|&]+)")


def pasta_das_capturas(raiz: Path) -> Path:
    pasta = Path(os.environ.get("DIGILAB_CAPTURAS") or CAPTURAS_PADRAO)
    if not pasta.is_absolute():
        pasta = raiz / "web" / "app" / pasta
    return Path(os.path.normcase(os.path.abspath(pasta)))


def protegido(alvo: str, raiz: Path, cwd: Path) -> bool:
    """O caminho cai numa pasta `*-snapshots` ou dentro da pasta das referências do portão."""
    texto = alvo.strip().strip("\"'")
    if not texto:
        return False
    caminho = Path(texto)
    if not caminho.is_absolute():
        caminho = cwd / caminho
    absoluto = Path(os.path.normcase(os.path.abspath(caminho)))
    if any(parte.endswith("-snapshots") for parte in absoluto.parts):
        return True
    capturas = pasta_das_capturas(raiz)
    return absoluto == capturas or capturas in absoluto.parents


def roda_playwright(tokens: list[str]) -> bool:
    baixos = [t.lower() for t in tokens]
    if any(t.endswith("playwright") or t.endswith("playwright.cmd") for t in baixos):
        return True
    return "npm" in [Path(t).stem for t in baixos] and "run" in baixos and any(t in ("e2e", "capturas") for t in baixos)


def atualiza_referencia(tokens: list[str]) -> bool:
    return roda_playwright(tokens) and any(t == "-u" or t == "--update-snapshots" or t.startswith("--update-snapshots=") for t in tokens)


def so_leitura(tokens: list[str]) -> bool:
    resto = [t for t in tokens if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t)]   # tira as atribuições VAR=valor da frente
    if not resto:
        return True
    comando = Path(resto[0]).name.lower()
    if comando == "git":
        sub = [t for t in resto[1:] if not t.startswith("-")]
        return bool(sub) and sub[0] in GIT_SO_LEITURA
    return comando in SO_LEITURA


def motivo_no_shell(comando: str, raiz: Path, cwd: Path) -> tuple[str, str] | None:
    """("ask" ou "negar", o motivo) para o primeiro trecho do comando que mexe nas referências; None se nenhum mexe."""
    for alvo in REDIRECIONAMENTO.findall(comando):
        if protegido(alvo, raiz, cwd):
            return "negar", f"H6: o redirecionamento para {alvo.strip(chr(34) + chr(39))} escreveria numa pasta de capturas de referência."
    for tokens in segmentos(comando):
        if atualiza_referencia(tokens):
            return "ask", ("H6: este comando regrava as capturas de referência do Playwright (--update-snapshots/-u). Só com a aprovação "
                           "do Matheus, depois de ver as capturas novas (docs/TAREFA_V3_UX_TELA_PET.md, G-REFERENCIA).")
        if any(protegido(t, raiz, cwd) for t in tokens) and not so_leitura(tokens):
            return "negar", ("H6: este comando mexe numa pasta de capturas de referência (*-snapshots/ ou DIGILAB_CAPTURAS). As referências "
                             "só mudam pelo Playwright com --update-snapshots, com a aprovação do Matheus.")
    return None


def main() -> None:
    evento = ler_evento()
    ferramenta = evento.get("tool_name") or ""
    entrada = evento.get("tool_input") or {}
    raiz = raiz_do_projeto(evento)
    cwd = Path(evento.get("cwd") or raiz)
    if ferramenta in FERRAMENTAS_DE_EDICAO:
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or entrada.get("path")
        if alvo and protegido(alvo, raiz, cwd):
            bloquear(f"H6: {alvo} é uma captura de referência do e2e. As referências só mudam pelo Playwright com --update-snapshots, com "
                     "a aprovação do Matheus (docs/TAREFA_V3_UX_TELA_PET.md, G-REFERENCIA).")
        return
    if ferramenta in FERRAMENTAS_DE_SHELL:
        achado = motivo_no_shell(str(entrada.get("command") or ""), raiz, cwd)
        if achado is None:
            return
        decisao, motivo = achado
        if decisao == "ask":
            perguntar(motivo)
        bloquear(motivo)


if __name__ == "__main__":
    main()
