"""H1b (Stop): no fim do turno, confere o sha256 do `digilab/engine.py` contra o `ENGINE_SHA256_V0`.

Pega o que o H1 não vê: o arquivo mudado por um comando de shell. Se o sha diverge, devolve o turno ao Claude com o motivo (código 2). Não
bloqueia duas vezes seguidas (`stop_hook_active`): na segunda, deixa encerrar, porque o teste do sha continua sendo o gate de verdade.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, ler_evento, raiz_do_projeto, sha_do_engine  # noqa: E402


def main() -> None:
    evento = ler_evento()
    if evento.get("stop_hook_active"):
        return
    raiz = raiz_do_projeto(evento)
    atual, congelado = sha_do_engine(raiz)
    if atual != congelado:
        bloquear(f"H1b: digilab/engine.py mudou (sha256 {atual[:16]}…, o congelado é {congelado[:16]}…). O engine.py não muda: "
                 "volte o arquivo (git checkout -- digilab/engine.py) e ponha a mudança numa subclasse do motor, atrás de chave.")


if __name__ == "__main__":
    main()
