"""H1b (Stop): no fim do turno, confere o sha256 do `digilab/engine.py` contra o `ENGINE_SHA256_V0` e as `FAIXAS_QUEIMADAS`.

Pega o que o H1 e o H9 não veem: o arquivo mudado por um comando de shell. As faixas (INFRA_AGENTES E1, `docs/TAREFA_V3_INFRA_AGENTES.md`,
seção 3.1): a tupla `FAIXAS_QUEIMADAS` do disco tem de começar pela do `origin/main`, na mesma ordem (faixa queimada não volta).
Se um dos dois diverge, devolve o turno ao Claude com o motivo (código 2). Não bloqueia duas vezes seguidas (`stop_hook_active`): na segunda, deixa encerrar, porque o teste do sha continua sendo o gate de verdade.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import FAIXAS, bloquear, git, ler_evento, queimadas_do_texto, raiz_do_projeto, sha_do_engine  # noqa: E402


def main() -> None:
    evento = ler_evento()
    if evento.get("stop_hook_active"):
        return
    raiz = raiz_do_projeto(evento)
    atual, congelado = sha_do_engine(raiz)
    if atual != congelado:
        bloquear(f"H1b: digilab/engine.py mudou (sha256 {atual[:16]}…, o congelado é {congelado[:16]}…). O engine.py não muda: "
                 "volte o arquivo (git checkout -- digilab/engine.py) e ponha a mudança numa subclasse do motor, atrás de chave.")
    motivo = faixas_queimadas_mudaram(raiz)
    if motivo:
        bloquear(motivo)


def faixas_queimadas_mudaram(raiz: Path) -> str | None:
    """O motivo, se alguma faixa queimada do `origin/main` sumiu ou mudou no disco; None se não. Sem o `faixas.py` (outro projeto), nada."""
    if not (raiz / FAIXAS).exists():
        return None
    try:
        git(raiz, "rev-parse", "--verify", "--quiet", "origin/main")
    except RuntimeError:
        return "H1b: não achei o origin/main para conferir as FAIXAS_QUEIMADAS; rode git fetch origin."
    try:
        texto_main = git(raiz, "show", f"origin/main:{FAIXAS.as_posix()}")
    except RuntimeError:
        return None                                # o arquivo não existe na main: nenhuma faixa queimada a perder
    na_main = queimadas_do_texto(texto_main)
    no_disco = queimadas_do_texto((raiz / FAIXAS).read_text(encoding="utf-8"))
    if no_disco[:len(na_main)] != na_main:
        return ("H1b: as FAIXAS_QUEIMADAS de experiments/bancada/faixas.py perderam ou mudaram uma entrada do origin/main. Faixa queimada "
                "não volta (CLAUDE.md, sementes): volte as entradas; uma faixa nova entra só no fim da tupla.")
    return None


if __name__ == "__main__":
    main()
