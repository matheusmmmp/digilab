"""H9 (PreToolUse, Edit|Write|MultiEdit): as faixas queimadas não voltam.

Só olha `experiments/bancada/faixas.py` (INFRA_AGENTES E1, `docs/TAREFA_V3_INFRA_AGENTES.md`, seção 3.1; D-IA-4). Aplica a edição pedida ao
texto do arquivo em memória (o `old_string`/`new_string` do Edit, os pares do MultiEdit, o `content` do Write), lê a tupla
`FAIXAS_QUEIMADAS` antes e depois pela AST e:
- código 2 se alguma entrada de antes sumiu ou mudou, ou se o texto depois não se lê (sem a tupla, ou com erro de sintaxe);
- a decisão `ask` se só entraram entradas novas no fim (queimar uma faixa é legítimo, depois de uma run caída, mas pede o Matheus);
- deixa passar se a tupla não mudou: as `FAIXAS_RESERVADAS` seguem editáveis (o coordenador reserva uma faixa nova).

O shell (`sed -i`, um script) não passa por aqui: quem pega esse caso é o H1b, no fim do turno, contra o `origin/main`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import FAIXAS, bloquear, ler_evento, perguntar, queimadas_do_texto, raiz_do_projeto  # noqa: E402


def aplicar(texto: str, ferramenta: str, entrada: dict) -> str | None:
    """O texto depois da edição; None se a edição não acha o trecho (a própria ferramenta vai falhar, e nada muda)."""
    if ferramenta == "Write":
        return entrada["content"]
    pares = entrada["edits"] if ferramenta == "MultiEdit" else [entrada]
    for par in pares:
        velho, novo = par["old_string"], par["new_string"]
        if velho not in texto:
            return None
        texto = texto.replace(velho, novo) if par.get("replace_all") else texto.replace(velho, novo, 1)
    return texto


def main() -> None:
    evento = ler_evento()
    ferramenta = evento.get("tool_name")
    if ferramenta not in ("Edit", "Write", "MultiEdit"):
        return
    entrada = evento.get("tool_input") or {}
    alvo = entrada.get("file_path")
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
    if relativo.as_posix().lower() != FAIXAS.as_posix().lower():
        return
    antes_texto = (raiz / FAIXAS).read_text(encoding="utf-8")
    antes = queimadas_do_texto(antes_texto)
    depois_texto = aplicar(antes_texto, ferramenta, entrada)
    if depois_texto is None:
        return
    try:
        depois = queimadas_do_texto(depois_texto)
    except (SyntaxError, ValueError) as erro:
        bloquear(f"H9: depois desta edição não consigo ler as FAIXAS_QUEIMADAS de experiments/bancada/faixas.py ({erro}). A tupla fica no "
                 "nível do módulo, como um literal.")
    if depois == antes:
        return
    if depois[:len(antes)] == antes:
        novas = ", ".join(f"{lo}...{hi}" for lo, hi, *_ in depois[len(antes):])
        perguntar(f"H9: esta edição queima faixas novas ({novas}). Faixa queimada não volta: confirme com o Matheus se é para queimar agora.")
    bloquear("H9: esta edição remove ou muda uma entrada de FAIXAS_QUEIMADAS em experiments/bancada/faixas.py. Faixa queimada não volta "
             "(CLAUDE.md, sementes); uma faixa nova entra só no fim da tupla.")


if __name__ == "__main__":
    main()
