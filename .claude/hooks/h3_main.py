"""H3 (PreToolUse, Bash|PowerShell): o merge e o push na `main` pedem a aprovação do Matheus na hora (a decisão "ask").

Pergunta quando o comando tem:
- `gh pr merge` (qualquer PR);
- um `git push` que manda para a `main`: o refspec `main`, `HEAD:main`, `<x>:main`, `refs/heads/main`, ou `--all`/`--mirror`, ou um
  `git push` sem refspec com o branch atual sendo a `main`.

Não pergunta no `git merge origin/main` num branch de worker (o que os workers fazem para resolver conflito), nem no push de outro branch.
O hook lê o texto do comando: um alias do git ou um script que faça o push por dentro não passa por aqui. A proteção de verdade da `main`
continua sendo do GitHub.
"""
from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import git, ler_evento, perguntar, raiz_do_projeto  # noqa: E402

SEPARADORES = re.compile(r"&&|\|\||;|\||\n")
REFS_MAIN = {"main", "refs/heads/main"}
OPCOES_COM_VALOR = {"-o", "--push-option", "--repo", "--receive-pack", "--exec", "-C", "-c"}


def segmentos(comando: str) -> list[list[str]]:
    saida = []
    for pedaco in SEPARADORES.split(comando):
        pedaco = pedaco.strip()
        if not pedaco:
            continue
        try:
            saida.append(shlex.split(pedaco, posix=True))
        except ValueError:
            saida.append(pedaco.split())
    return saida


def e_merge_de_pr(tokens: list[str]) -> bool:
    return len(tokens) >= 3 and Path(tokens[0]).stem.lower() == "gh" and tokens[1] == "pr" and tokens[2] == "merge"


def argumentos_do_push(tokens: list[str]) -> tuple[list[str], list[str], str | None] | None:
    """(as opções, os argumentos posicionais e o diretório do -C) de um `git ... push ...`; None se não é um push."""
    if not tokens or Path(tokens[0]).stem.lower() != "git":
        return None
    i, diretorio = 1, None
    while i < len(tokens) and tokens[i].startswith("-"):
        if tokens[i] == "-C" and i + 1 < len(tokens):
            diretorio = tokens[i + 1]
            i += 2
        elif tokens[i] == "-c" and i + 1 < len(tokens):
            i += 2
        else:
            i += 1
    if i >= len(tokens) or tokens[i] != "push":
        return None
    opcoes, posicionais = [], []
    j = i + 1
    while j < len(tokens):
        t = tokens[j]
        if t.startswith("-"):
            opcoes.append(t)
            if t in OPCOES_COM_VALOR and j + 1 < len(tokens):
                j += 1
        else:
            posicionais.append(t)
        j += 1
    return opcoes, posicionais, diretorio


def push_para_main(tokens: list[str], raiz: Path) -> bool:
    achado = argumentos_do_push(tokens)
    if achado is None:
        return False
    opcoes, posicionais, diretorio = achado
    if any(o in ("--all", "--mirror") for o in opcoes):
        return True
    refspecs = posicionais[1:]
    for ref in refspecs:
        destino = ref.lstrip("+").split(":")[-1]
        if destino in REFS_MAIN:
            return True
    if not refspecs:
        onde = Path(diretorio) if diretorio else raiz
        try:
            return git(onde if onde.is_absolute() else raiz / onde, "rev-parse", "--abbrev-ref", "HEAD").strip() == "main"
        except RuntimeError:
            return True                       # sem saber o branch, pergunta (falhar para o lado seguro)
    return False


def main() -> None:
    evento = ler_evento()
    comando = (evento.get("tool_input") or {}).get("command") or ""
    raiz = raiz_do_projeto(evento)
    for tokens in segmentos(comando):
        if e_merge_de_pr(tokens):
            perguntar("H3: merge de PR. O merge é só do Matheus (CLAUDE.md, trabalho em paralelo): confirme se é para fazer agora.")
        if push_para_main(tokens, raiz):
            perguntar("H3: push na main. Na main só entra o merge do Matheus: confirme se é para fazer agora.")


if __name__ == "__main__":
    main()
