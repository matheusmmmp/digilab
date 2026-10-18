"""Gera docs/TAREFA_V2_<FRENTE>.md a partir de docs/modelos/TAREFA_V2_MODELO.md.

Preenche o nome da frente, a data, o branch, a categoria e a origem; o resto do modelo fica com os <...> para o coordenador escrever.
Não sobrescreve uma tarefa que já existe. No fim imprime, sem executar, o comando da worktree e a mensagem inicial do worker, tirada de
docs/V2_TRABALHO_PARALELO.md (seção 3), para não haver uma segunda cópia dela.

Uso:
  python tools/nova_tarefa.py INFRA_POC --categoria documentacao --origem "Claude Code" --resumo "conferir os links da infra"
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

CATEGORIAS = ("implementacao", "experimento", "literatura", "arquitetura", "documentacao")
ORIGENS = ("Matheus", "ChatGPT", "ChatGPT Work", "Claude Code", "Claude Research", "Claude Science")
MODELO = Path("docs/modelos/TAREFA_V2_MODELO.md")
PARALELO = Path("docs/V2_TRABALHO_PARALELO.md")
NOME = re.compile(r"[A-Z0-9]+(?:_[A-Z0-9]+)*")


def nome_branch(frente: str) -> str:
    return "v2-" + frente.lower().replace("_", "-")


def gerar(raiz: Path, frente: str, categoria: str, origem: str, resumo: str, data: str) -> Path:
    if not NOME.fullmatch(frente):
        raise ValueError(f"nome de frente inválido: {frente!r}; use maiúsculas, dígitos e _ (ex.: INFRA_POC)")
    if categoria not in CATEGORIAS:
        raise ValueError(f"categoria inválida: {categoria!r}; use uma de {', '.join(CATEGORIAS)}")
    if origem not in ORIGENS:
        raise ValueError(f"origem inválida: {origem!r}; use uma de {', '.join(ORIGENS)}")
    if not resumo.strip():
        raise ValueError("o resumo da origem não pode ser vazio")
    destino = raiz / "docs" / f"TAREFA_V2_{frente}.md"
    if destino.exists():
        raise FileExistsError(f"{destino.relative_to(raiz)} já existe; esta ferramenta não sobrescreve")

    texto = (raiz / MODELO).read_text(encoding="utf-8")
    trocas = [
        ("# TAREFA V2 — <FRENTE> (<data>)", f"# TAREFA V2 — {frente} ({data})"),
        ("`v2-<frente>`", f"`{nome_branch(frente)}`"),
        ("Status: <ABERTA | EM ANDAMENTO | ENTREGUE>.", "Status: ABERTA."),
        ("Categoria: <implementacao | experimento | literatura | arquitetura | documentacao>.", f"Categoria: {categoria}."),
    ]
    for antigo, novo in trocas:
        if antigo not in texto:
            raise ValueError(f"o modelo mudou: não achei {antigo!r} em {MODELO}")
        texto = texto.replace(antigo, novo, 1)
    origem_modelo = re.search(r"Origem: <Matheus \|.*?privada>\.", texto, re.S)
    if origem_modelo is None:
        raise ValueError(f"o modelo mudou: não achei o campo Origem em {MODELO}")
    texto = texto.replace(origem_modelo.group(0), f"Origem: {origem}, {data}: {resumo.strip().rstrip('.')}.", 1)
    texto = texto.replace("`docs/PLANO_ANALISE_V2_<FRENTE>.md`", f"`docs/PLANO_ANALISE_V2_{frente}.md`")
    destino.write_text(texto, encoding="utf-8", newline="\n")
    return destino


def mensagem_worker(raiz: Path, frente: str) -> str:
    """A mensagem inicial padrão, com <FRENTE> e <frente> trocados."""
    texto = (raiz / PARALELO).read_text(encoding="utf-8")
    m = re.search(r"Mensagem inicial padrão do worker.*?\n\n((?:> .*\n?)+)", texto)
    if m is None:
        raise ValueError(f"não achei a mensagem inicial do worker em {PARALELO}")
    msg = "\n".join(l[2:] for l in m.group(1).splitlines())
    return msg.replace("<FRENTE>", frente).replace("v2-<frente>", nome_branch(frente)).replace("<frente>", nome_branch(frente)[3:])


def principal(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("frente")
    p.add_argument("--categoria", required=True, choices=CATEGORIAS)
    p.add_argument("--origem", required=True, choices=ORIGENS)
    p.add_argument("--resumo", required=True, help="de onde veio a tarefa, em uma frase")
    p.add_argument("--data", default=dt.date.today().isoformat())
    p.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    a = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    raiz = a.raiz.resolve()
    destino = gerar(raiz, a.frente, a.categoria, a.origem, a.resumo, a.data)
    branch = nome_branch(a.frente)
    print(f"Criado: {destino.relative_to(raiz).as_posix()} (preencha os <...> e faça o commit por PR antes de abrir o worker)")
    print()
    print("Worktree (não executado):")
    print("  git -C D:/Trab/digilab/v2 fetch origin")
    print(f"  git -C D:/Trab/digilab/v2 worktree add D:/Trab/digilab/{branch} -b {branch} origin/main")
    print()
    print("Mensagem inicial do worker:")
    print(mensagem_worker(raiz, a.frente))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
