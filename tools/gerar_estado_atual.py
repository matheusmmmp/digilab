"""Gera docs/ESTADO_ATUAL.md, um índice derivado do estado do projeto.

Não é fonte de verdade: cada linha copia o que um arquivo do repositório declara e aponta para ele. O estado curado continua em
docs/PAINEL_V2.md (mantido pelo coordenador); este índice só junta, num lugar, o que se acha espalhado:
- a data do painel;
- a linha `Status:` de cada docs/TAREFA_V2_*.md, como está escrita (muitas ficaram ABERTA depois da entrega);
- quais docs/RESULTADO_V2_*.md citam a tarefa ou o plano pelo nome do arquivo (a citação que o próprio resultado faz; a falta dela não quer
  dizer que a run não rodou);
- as últimas linhas do índice de desvios.

O conteúdo depende só dos arquivos, não do commit nem da hora: regenerar sem mudança nas fontes dá o mesmo arquivo.

Uso:
  python tools/gerar_estado_atual.py            # escreve docs/ESTADO_ATUAL.md
  python tools/gerar_estado_atual.py --conferir # sai com 1 se o arquivo está desatualizado (o CI só avisa)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DESTINO = Path("docs/ESTADO_ATUAL.md")
ULTIMOS_REGISTROS = 10
LARGURA_STATUS = 90


def titulo(texto: str) -> str:
    for linha in texto.splitlines():
        if linha.startswith("# "):
            return linha[2:].strip()
    return "(sem título)"


def status_declarado(texto: str) -> str:
    """O trecho depois do primeiro `Status:` até o fim da frase, sem negrito, cortado."""
    m = re.search(r"Status(?: \([^)]*\))?:\s*(.+)", texto)
    if m is None:
        return "sem status declarado"
    s = m.group(1).replace("**", "").strip()
    s = re.split(r"(?<=[A-ZÀ-Ú])\.(?:\s|$)|\. ", s, maxsplit=1)[0].strip().rstrip(".")
    return s if len(s) <= LARGURA_STATUS else s[: LARGURA_STATUS - 1] + "…"


def celula(s: str) -> str:
    return s.replace("|", "\\|")


def gerar(raiz: Path) -> str:
    docs = raiz / "docs"
    resultados = {p.name: p.read_text(encoding="utf-8") for p in sorted(docs.glob("RESULTADO_V2_*.md"))}

    def citam(nome_arquivo: str) -> str:
        quem = [r for r, texto in resultados.items() if nome_arquivo in texto]
        return ", ".join(f"[{Path(r).stem}]({r})" for r in quem) or "nenhum"
    painel = (docs / "PAINEL_V2.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Atualizado em ([^*]+)\*\*(.*)", painel)
    painel_quando = (m.group(1) + m.group(2)).strip().rstrip(".") if m else "sem data declarada"

    l = [
        "# Estado atual — índice derivado (não editar à mão)",
        "",
        "Gerado por `tools/gerar_estado_atual.py`. **Não é fonte de verdade:** cada linha copia o que o arquivo citado declara. Quem quer",
        "saber o estado lê a fonte; quem acha um erro corrige a fonte e regenera este arquivo.",
        "",
        f"- **Estado curado da V2:** [PAINEL_V2.md](PAINEL_V2.md), atualizado em {painel_quando}. É o coordenador quem o mantém.",
        "- **Onde cada tipo de informação mora** (implementado, decidido, hipótese, proposta, resultado, problema, próximo passo):",
        "  [INDICE.md](INDICE.md).",
        "",
        "## 1. Tarefas (`docs/TAREFA_V2_*.md`)",
        "",
        "O status é o da linha `Status:` do arquivo, como está escrito. Muitas tarefas ficaram ABERTA depois da entrega; a última coluna",
        "lista os `RESULTADO_V2_*.md` que citam a tarefa pelo nome do arquivo.",
        "",
        "| tarefa | título | status declarado | resultados que a citam |",
        "|---|---|---|---|",
    ]
    for p in sorted(docs.glob("TAREFA_V2_*.md")):
        texto = p.read_text(encoding="utf-8")
        l.append(f"| [{p.stem}]({p.name}) | {celula(titulo(texto))} | {celula(status_declarado(texto))} | {citam(p.name)} |")

    l += [
        "",
        "## 2. Planos de análise (`docs/PLANO_ANALISE_V2_*.md`)",
        "",
        "\"nenhum\" quer dizer só que nenhum `RESULTADO_V2_*.md` cita o plano: o resultado pode estar num adendo do próprio plano.",
        "",
        "| plano | título | resultados que o citam |",
        "|---|---|---|",
    ]
    for p in sorted(docs.glob("PLANO_ANALISE_V2_*.md")):
        l.append(f"| [{p.stem}]({p.name}) | {celula(titulo(p.read_text(encoding='utf-8')))} | {citam(p.name)} |")

    indice = (docs / "REGISTRO_DESVIOS.md").read_text(encoding="utf-8")
    entradas = [x.strip() for x in indice.splitlines() if x.strip().startswith("- [")]
    l += [
        "",
        f"## 3. Os últimos {ULTIMOS_REGISTROS} desvios registrados",
        "",
        f"Do índice [REGISTRO_DESVIOS.md](REGISTRO_DESVIOS.md) ({len(entradas)} entradas), na ordem em que entraram.",
        "",
        *entradas[-ULTIMOS_REGISTROS:],
        "",
    ]
    return "\n".join(l)


def principal(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--conferir", action="store_true")
    a = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    raiz = a.raiz.resolve()
    novo = gerar(raiz)
    destino = raiz / DESTINO
    if a.conferir:
        atual = destino.read_text(encoding="utf-8") if destino.exists() else ""
        if atual != novo:
            print(f"{DESTINO.as_posix()} está desatualizado: rode python tools/gerar_estado_atual.py")
            return 1
        print(f"{DESTINO.as_posix()} está em dia")
        return 0
    destino.write_text(novo, encoding="utf-8", newline="\n")
    print(f"escrito: {DESTINO.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
