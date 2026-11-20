"""H4 (PreToolUse, Bash|PowerShell): nenhum agente escreve a autorização de implementação no GitHub (IM-8, docs/TAREFA_V2_INFRA_MULTIAGENTE.md).

A autorização é um comentário do Matheus com "AUTORIZO IMPLEMENTAÇÃO" (docs/infra/GUIA_OPERACIONAL.md). O `tools/conferir_autorizacao.py`
recusa a que vem de um app (o ChatGPT Work), mas não consegue recusar a do Claude Code: o `gh` dele usa o token do Matheus, e o comentário
sai igual a um do Matheus (confirmado no comentário 6258009495 da Issue #336). Este hook fecha esse lado.

Bloqueia (código 2) o comando de shell que:
- tem a frase no próprio texto (por exemplo `gh issue comment 336 --body "AUTORIZO IMPLEMENTAÇÃO: ..."` ou `gh api ... -f body=...`); ou
- chama o `gh` com um arquivo de corpo (`--body-file`, `-F`, `--input`) cujo conteúdo tem a frase.

Não bloqueia escrever a frase num documento pelo Edit ou pelo Write: o guia cita o modelo do comentário, e um documento não é autorização.
O Matheus autoriza pelo navegador ou pelo celular, fora do Claude Code.
"""
from __future__ import annotations

import re
import shlex
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, ler_evento, raiz_do_projeto  # noqa: E402

OPCOES_DE_ARQUIVO = {"--body-file", "-F", "--input"}


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


FRASE = re.compile(r"autorizo\s+implementacao", re.I)


def tem_frase(texto: str) -> bool:
    return FRASE.search(sem_acento(texto)) is not None


def arquivos_de_corpo(comando: str) -> list[str]:
    """Os arquivos passados ao `gh` como corpo. `-F campo=@arquivo` (o gh api) também conta."""
    try:
        tokens = shlex.split(comando, posix=True)
    except ValueError:
        tokens = comando.split()
    if not any(Path(t).stem.lower() == "gh" for t in tokens):
        return []
    saida = []
    for i, t in enumerate(tokens):
        nome, _, valor = t.partition("=")
        if nome in OPCOES_DE_ARQUIVO:
            alvo = valor if valor else (tokens[i + 1] if i + 1 < len(tokens) else "")
            if "=@" in alvo:
                alvo = alvo.split("=@", 1)[1]
            saida.append(alvo.lstrip("@"))
    return [s for s in saida if s and s != "-"]


def main() -> None:
    evento = ler_evento()
    comando = (evento.get("tool_input") or {}).get("command") or ""
    raiz = raiz_do_projeto(evento)
    if tem_frase(comando):
        bloquear("H4: o comando escreve \"AUTORIZO IMPLEMENTAÇÃO\". A autorização é só do Matheus, pelo navegador ou pelo celular; nenhum "
                 "agente a escreve (AGENTS.md, IM-8).")
    for arquivo in arquivos_de_corpo(comando):
        caminho = Path(arquivo)
        caminho = caminho if caminho.is_absolute() else raiz / caminho
        if caminho.is_file() and tem_frase(caminho.read_text(encoding="utf-8", errors="replace")):
            bloquear(f"H4: o arquivo de corpo {arquivo} tem \"AUTORIZO IMPLEMENTAÇÃO\". A autorização é só do Matheus; nenhum agente a "
                     "escreve (AGENTS.md, IM-8).")


if __name__ == "__main__":
    main()
