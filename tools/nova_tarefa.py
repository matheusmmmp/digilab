"""Gera docs/TAREFA_<FASE>_<FRENTE>.md a partir de docs/modelos/TAREFA_<FASE>_MODELO.md (FASE = V2, o padrão, ou V3).

Preenche o nome da frente, a data, o branch, a categoria e a origem; o resto do modelo fica com os <...> para o coordenador escrever.
Não sobrescreve uma tarefa que já existe. No fim imprime, sem executar, o comando da worktree e a mensagem inicial do worker, tirada de
docs/V2_TRABALHO_PARALELO.md (seção 3), para não haver uma segunda cópia dela.

Uso:
  python tools/nova_tarefa.py INFRA_POC --categoria documentacao --origem "Claude Code" --resumo "conferir os links da infra"
  python tools/nova_tarefa.py LITERATURA_C0 --fase V3 --categoria literatura --origem Matheus --resumo "V3-D1"
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

CATEGORIAS = ("implementacao", "experimento", "literatura", "arquitetura", "documentacao")
ORIGENS = ("Matheus", "ChatGPT", "ChatGPT Work", "Claude Code", "Claude Research", "Claude Science")
FASES = ("V2", "V3")
MODELO = Path("docs/modelos/TAREFA_V2_MODELO.md")  # o da V2; o da fase é modelo_da_fase(fase)
PARALELO = Path("docs/V2_TRABALHO_PARALELO.md")
NOME = re.compile(r"[A-Z0-9]+(?:_[A-Z0-9]+)*")


def modelo_da_fase(fase: str) -> Path:
    return Path(f"docs/modelos/TAREFA_{fase}_MODELO.md")


def nome_branch(frente: str, fase: str = "V2") -> str:
    return fase.lower() + "-" + frente.lower().replace("_", "-")


def gerar(raiz: Path, frente: str, categoria: str, origem: str, resumo: str, data: str, fase: str = "V2") -> Path:
    if fase not in FASES:
        raise ValueError(f"fase inválida: {fase!r}; use uma de {', '.join(FASES)}")
    modelo = modelo_da_fase(fase)
    if not NOME.fullmatch(frente):
        raise ValueError(f"nome de frente inválido: {frente!r}; use maiúsculas, dígitos e _ (ex.: INFRA_POC)")
    if categoria not in CATEGORIAS:
        raise ValueError(f"categoria inválida: {categoria!r}; use uma de {', '.join(CATEGORIAS)}")
    if origem not in ORIGENS:
        raise ValueError(f"origem inválida: {origem!r}; use uma de {', '.join(ORIGENS)}")
    if not resumo.strip():
        raise ValueError("o resumo da origem não pode ser vazio")
    destino = raiz / "docs" / f"TAREFA_{fase}_{frente}.md"
    if destino.exists():
        raise FileExistsError(f"{destino.relative_to(raiz)} já existe; esta ferramenta não sobrescreve")

    texto = (raiz / modelo).read_text(encoding="utf-8")
    trocas = [
        (f"# TAREFA {fase} — <FRENTE> (<data>)", f"# TAREFA {fase} — {frente} ({data})"),
        (f"`{fase.lower()}-<frente>`", f"`{nome_branch(frente, fase)}`"),
        ("Status: <ABERTA | EM ANDAMENTO | ENTREGUE>.", "Status: ABERTA."),
        ("Categoria: <implementacao | experimento | literatura | arquitetura | documentacao>.", f"Categoria: {categoria}."),
    ]
    for antigo, novo in trocas:
        if antigo not in texto:
            raise ValueError(f"o modelo mudou: não achei {antigo!r} em {modelo}")
        texto = texto.replace(antigo, novo, 1)
    origem_modelo = re.search(r"Origem: <Matheus \|.*?privada>\.", texto, re.S)
    if origem_modelo is None:
        raise ValueError(f"o modelo mudou: não achei o campo Origem em {modelo}")
    texto = texto.replace(origem_modelo.group(0), f"Origem: {origem}, {data}: {resumo.strip().rstrip('.')}.", 1)
    texto = texto.replace(f"`docs/PLANO_ANALISE_{fase}_<FRENTE>.md`", f"`docs/PLANO_ANALISE_{fase}_{frente}.md`")
    destino.write_text(texto, encoding="utf-8", newline="\n")
    return destino


def mensagem_worker(raiz: Path, frente: str, fase: str = "V2") -> str:
    """A mensagem inicial padrão, com <FRENTE> e <frente> trocados."""
    texto = (raiz / PARALELO).read_text(encoding="utf-8")
    m = re.search(r"Mensagem inicial padrão do worker.*?\n\n((?:> .*\n?)+)", texto)
    if m is None:
        raise ValueError(f"não achei a mensagem inicial do worker em {PARALELO}")
    msg = "\n".join(l[2:] for l in m.group(1).splitlines())
    msg = msg.replace("TAREFA_V2_<FRENTE>", f"TAREFA_{fase}_<FRENTE>")
    return msg.replace("<FRENTE>", frente).replace("v2-<frente>", nome_branch(frente, fase)).replace("<frente>", nome_branch(frente, fase)[3:])


def principal(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("frente")
    p.add_argument("--categoria", required=True, choices=CATEGORIAS)
    p.add_argument("--origem", required=True, choices=ORIGENS)
    p.add_argument("--resumo", required=True, help="de onde veio a tarefa, em uma frase")
    p.add_argument("--fase", choices=FASES, default="V2")
    p.add_argument("--data", default=dt.date.today().isoformat())
    p.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    a = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    raiz = a.raiz.resolve()
    destino = gerar(raiz, a.frente, a.categoria, a.origem, a.resumo, a.data, a.fase)
    branch = nome_branch(a.frente, a.fase)
    print(f"Criado: {destino.relative_to(raiz).as_posix()} (preencha os <...> e faça o commit por PR antes de abrir o worker)")
    print()
    print("Worktree (não executado):")
    print("  git -C D:/Trab/digilab/v2 fetch origin")
    print(f"  git -C D:/Trab/digilab/v2 worktree add D:/Trab/digilab/{branch} -b {branch} origin/main")
    print()
    print("Mensagem inicial do worker:")
    print(mensagem_worker(raiz, a.frente, a.fase))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
