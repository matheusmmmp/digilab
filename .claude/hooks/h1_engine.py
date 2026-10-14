"""H1 (PreToolUse, Edit|Write|MultiEdit|NotebookEdit): nega a edição de `digilab/engine.py`.

O `engine.py` não muda: o sha256 dele está congelado em `digilab/protocol.py` (`ENGINE_SHA256_V0`), e o teste e o preflight conferem.
Este hook só antecipa o gate: barra a ferramenta de edição antes de ela rodar. Um comando de shell que mexa no arquivo não passa por aqui
(o matcher só vê as ferramentas de edição); quem pega esse caso é o H1b, no fim do turno.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, ler_evento, raiz_do_projeto  # noqa: E402

PROTEGIDO = Path("digilab") / "engine.py"


def caminho_da_ferramenta(evento: dict) -> str | None:
    entrada = evento.get("tool_input") or {}
    return entrada.get("file_path") or entrada.get("notebook_path") or entrada.get("path")


def main() -> None:
    evento = ler_evento()
    alvo = caminho_da_ferramenta(evento)
    if not alvo:
        return
    raiz = raiz_do_projeto(evento)
    caminho = Path(alvo)
    if not caminho.is_absolute():
        caminho = Path(evento.get("cwd") or raiz) / caminho
    try:
        relativo = caminho.resolve().relative_to(raiz)
    except ValueError:
        return
    if str(relativo).lower() == str(PROTEGIDO).lower():
        bloquear("H1: digilab/engine.py não muda (o sha256 está congelado em digilab/protocol.py, ENGINE_SHA256_V0). "
                 "Mecânica nova entra numa subclasse do motor, atrás de chave desligada (CLAUDE.md, regras não negociáveis).")


if __name__ == "__main__":
    main()
