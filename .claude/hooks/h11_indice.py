"""H11 (PreToolUse, Edit|Write|MultiEdit|NotebookEdit e Bash|PowerShell): o worker não edita o índice de desvios.

O índice `docs/REGISTRO_DESVIOS.md` é gerado por `tools/gerar_indice_desvios.py`, e quem regenera é quem faz o merge, na `main` ou num
PR só do índice (docs/TAREFA_V3_INDICE_DESVIOS.md, D-ID2). Depois do #638, os workers seguiram regenerando o índice nos próprios PRs,
e os PRs voltaram a conflitar nele. Este hook bloqueia (código 2):
- o Edit, o Write, o MultiEdit e o NotebookEdit no índice, sempre: ele é gerado, nem quem faz o merge o edita à mão;
- no shell, rodar `tools/gerar_indice_desvios.py` ou `tools/registro_por_mes.py` para escrever (sem `--conferir` nem `--help`), fora do
  branch `main` e dos branches `v3-indice-*` (o PR só do índice do coordenador);
- no shell, escrever no índice por redirecionamento, `tee`, `sed -i`, `cp`, `mv`, `Set-Content`, `Out-File` ou `Add-Content`.

Passa: ler o índice (`cat`, `grep`, `git diff`), o gerador com `--conferir`, e trazer o índice da `main` num conflito
(`git checkout origin/main -- docs/REGISTRO_DESVIOS.md`, ou `git restore --source origin/main ...`). Um índice atrasado no PR é aceito
(D-ID3). O hook lê o texto do comando: um script que escreva o arquivo por dentro não passa por aqui.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, git, ler_evento, raiz_do_projeto  # noqa: E402

INDICE = "docs/REGISTRO_DESVIOS.md"
GERADORES = ("gerar_indice_desvios.py", "registro_por_mes.py")
SO_CONFERE = ("--conferir", "--help", "-h")
SEPARADORES = re.compile(r"&&|\|\||;|\n")
ESCRITA_NO_SHELL = re.compile(
    r"(>>?\s*['\"]?[^\s'\"]*REGISTRO_DESVIOS\.md)"
    r"|(\btee\b[^|;&\n]*REGISTRO_DESVIOS\.md)"
    r"|(\b(cp|mv|copy|move|Copy-Item|Move-Item)\b[^|;&\n]*REGISTRO_DESVIOS\.md['\"]?\s*($|[|;&\n]))"
    r"|(\bsed\b[^|]*\s-i[^|]*REGISTRO_DESVIOS\.md)"
    r"|((Set-Content|Out-File|Add-Content)\b[^|]*REGISTRO_DESVIOS\.md)"
    r"|(REGISTRO_DESVIOS\.md['\"]?\s*\|\s*(Set-Content|Out-File|Add-Content))", re.I)

MOTIVO = ("H11: o índice docs/REGISTRO_DESVIOS.md é gerado, e o worker não o edita (CLAUDE.md, \"O desvio\"; D-ID2). Registre o desvio "
          "numa seção no fim de docs/registro/AAAA-MM.md e deixe o índice como está: um índice atrasado no PR é aceito (D-ID3). Num "
          "conflito nele, traga o da main: git checkout origin/main -- docs/REGISTRO_DESVIOS.md. Quem regenera é quem faz o merge, "
          "na main ou num branch v3-indice-*.")


def branch_atual(raiz: Path) -> str:
    try:
        return git(raiz, "rev-parse", "--abbrev-ref", "HEAD").strip()
    except RuntimeError:
        return ""


def pode_regenerar(raiz: Path) -> bool:
    nome = branch_atual(raiz)
    return nome == "main" or nome.startswith("v3-indice-")


def e_o_indice(alvo: str, evento: dict) -> bool:
    raiz = raiz_do_projeto(evento)
    caminho = Path(alvo)
    if not caminho.is_absolute():
        caminho = Path(evento.get("cwd") or raiz) / caminho
    try:
        relativo = caminho.resolve().relative_to(raiz)
    except ValueError:
        return False
    return relativo.as_posix().lower() == INDICE.lower()


def roda_gerador_para_escrever(pedaco: str) -> bool:
    if not any(g in pedaco.replace("\\", "/") for g in GERADORES):
        return False
    return not any(re.search(rf"(^|\s){re.escape(op)}(\s|$)", pedaco) for op in SO_CONFERE)


def main() -> None:
    evento = ler_evento()
    ferramenta = evento.get("tool_name")
    entrada = evento.get("tool_input") or {}
    if ferramenta in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        alvo = entrada.get("file_path") or entrada.get("notebook_path")
        if alvo and e_o_indice(alvo, evento):
            bloquear(MOTIVO)
        return
    if ferramenta not in ("Bash", "PowerShell"):
        return
    comando = entrada.get("command") or ""
    if ESCRITA_NO_SHELL.search(comando):
        bloquear(MOTIVO)
    if any(roda_gerador_para_escrever(p) for p in SEPARADORES.split(comando)):
        if not pode_regenerar(raiz_do_projeto(evento)):
            bloquear(MOTIVO + f" Este branch é {branch_atual(raiz_do_projeto(evento)) or 'desconhecido'}.")


if __name__ == "__main__":
    main()
