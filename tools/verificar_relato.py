"""Confere o relato de volta de um PR (.github/pull_request_template.md) contra o repositório.

O relato é o corpo do PR. Esta ferramenta separa duas coisas:
- DECLARADA: o que o agente escreveu no corpo (inclusive uma saída de teste colada). Não conta como prova.
- VERIFICADA: o que esta ferramenta conferiu sozinha no repositório (o arquivo existe, o DOI está na tabela verificada, o plano foi
  commitado antes do artefato, o link resolve). Os testes não rodam aqui: quem os roda é o job `testes` do CI, e é o resultado desse job
  que conta.

Cada categoria tem a própria regra de evidência (docs/infra/GUIA_OPERACIONAL.md, seção "O que o CI confere"):
- implementacao: algum arquivo de teste mudou ou é citado, e todo teste citado existe;
- experimento: o plano de análise citado existe e foi commitado antes de todo artefato novo; todo caminho de artefato citado existe;
- literatura: Origem, DOIs, Resultados e Limitações preenchidos; todo DOI está em docs/referencias; nada mudou fora de docs/;
- arquitetura: o relato diz PROPOSTO, as decisões do Matheus estão listadas, nada mudou em digilab/, experiments/ ou web/app/src/;
- documentacao: só mudaram documentos; todo link relativo dos .md mudados resolve.

Uso:
  python tools/verificar_relato.py --arquivo corpo.md [--base origin/main]   # arquivos mudados por git diff base...HEAD
  python tools/verificar_relato.py --pr 123                                  # corpo e arquivos pelo gh (ignora --base)
  python tools/verificar_relato.py --env CORPO_PR --base origin/main          # no CI: o corpo vem por variável de ambiente
  python tools/verificar_relato.py --listar-testes --base origin/main         # os tests/test_*.py mudados, um por linha

Sai com 0 se o relato passa; com 1, e a tabela do que falhou, se não. Com GITHUB_STEP_SUMMARY definido, a tabela vai também para o resumo
do job.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

CATEGORIAS = ("implementacao", "experimento", "literatura", "arquitetura", "documentacao")
CAMPOS = ("Tarefa", "Categoria", "Executor", "Branch")
SECOES = ("O que é", "Arquivos", "Evidências declaradas", "Desvios", "Decisões do Matheus", "Questões abertas", "Próximos passos")
CAMPOS_LITERATURA = ("Origem", "DOIs", "Resultados", "Limitações")
# Um <...> que sobrou do modelo; não pega HTML de verdade, que o relato não usa.
PLACEHOLDER = re.compile(r"<[^<>\n]*[a-zà-ú][^<>\n]*>")
COMENTARIO = re.compile(r"<!--.*?-->", re.S)
DOI = re.compile(r"\b10\.\d{4,9}/[^\s\]\)>,;\"'`|{}]+", re.I)
CAMINHO_ARTEFATO = re.compile(r"\bartifacts[\w-]*/[\w./-]+")
CAMINHO_TESTE = re.compile(r"\btests/[\w/-]+\.py\b")
CAMINHO_PLANO = re.compile(r"\bdocs/PLANO_ANALISE_V2_[\w-]+\.md\b")
LINK_MD = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SUCESSO = re.compile(r"\b(testes?|su[ií]te|ci|pytest)\b[^\n]{0,60}?\b(passa|passam|passaram|passou|passed|verde|ok)\b", re.I)
DOCUMENTO = re.compile(r"(^docs/|\.md$|^\.github/pull_request_template\.md$)")
CODIGO_PROIBIDO_ARQUITETURA = ("digilab/", "experiments/", "web/app/src/")


@dataclass
class Item:
    regra: str
    coluna: str  # "DECLARADA" ou "VERIFICADA"
    ok: bool
    detalhe: str
    alerta: bool = False  # um alerta aparece na tabela, mas não reprova


def limpar(corpo: str) -> str:
    return COMENTARIO.sub("", corpo.replace("\r\n", "\n"))


def campo(corpo: str, nome: str) -> str | None:
    m = re.search(rf"^\s*(?:\*\*)?{re.escape(nome)}(?:\*\*)?\s*:\s*(.*)$", corpo, re.M)
    return m.group(1).strip() if m else None


def secoes(corpo: str) -> dict[str, str]:
    saida: dict[str, str] = {}
    partes = re.split(r"^##\s+(.+?)\s*$", corpo, flags=re.M)
    for i in range(1, len(partes), 2):
        saida[partes[i].strip()] = partes[i + 1].strip()
    return saida


CODIGO = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def vazio(texto: str | None) -> bool:
    """Vazio, ou com um <...> do modelo fora de código (um `--arquivo <corpo.md>` citado num comando não conta; achado da INFRA-POC)."""
    return texto is None or not texto.strip() or bool(PLACEHOLDER.search(CODIGO.sub("", texto)))


def dois_conhecidos(raiz: Path) -> dict[str, tuple[bool, str]]:
    """Cada DOI de docs/referencias com (pode citar?, de onde veio).

    - Numa tabela `*_verificadas.csv`, vale a coluna `verificada`: só "VERIFICADA…" pode citar; "NÃO VERIFICADA", "NÃO LOCALIZADA" e
      "EXISTÊNCIA CONFIRMADA; CONTEÚDO NÃO LIDO" não podem, mesmo que o DOI também apareça noutro arquivo.
    - Fora das tabelas, um DOI num `.bib` (as entradas conferidas depois da revisão, como diz a skill literatura-digilab) ou num
      `*crossref.json` (a existência conferida) pode citar.
    """
    pasta = raiz / "docs" / "referencias"
    saida: dict[str, tuple[bool, str]] = {}
    for arq in sorted([*pasta.glob("*.bib"), *pasta.glob("*crossref.json")]):
        for d in DOI.findall(arq.read_text(encoding="utf-8")):
            saida.setdefault(normalizar_doi(d), (True, arq.name))
    for arq in sorted(pasta.glob("*_verificadas.csv")):
        with arq.open(encoding="utf-8-sig", newline="") as f:
            for linha in csv.DictReader(f):
                status = (linha.get("verificada") or "").strip()
                for d in DOI.findall(linha.get("doi_ou_id") or ""):
                    ok = status.startswith("VERIFICADA")
                    anterior = saida.get(normalizar_doi(d))
                    if anterior is None or anterior[0] or not ok:
                        saida[normalizar_doi(d)] = (ok, f"{arq.name}: {status}")
    return saida


def normalizar_doi(d: str) -> str:
    return d.rstrip(".").lower()


def git(raiz: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falhou: {r.stderr.strip()}")
    return r.stdout


def mudados_por_git(raiz: Path, base: str) -> list[str]:
    return [l for l in git(raiz, "diff", "--name-only", f"{base}...HEAD").splitlines() if l.strip()]


def primeiro_commit(raiz: Path, caminho: str) -> str | None:
    """O commit que acrescentou o arquivo (o mais antigo com --diff-filter=A), ou None se ainda não está commitado."""
    linhas = git(raiz, "log", "--format=%H", "--diff-filter=A", "--", caminho).split()
    return linhas[-1] if linhas else None


def antes(raiz: Path, a: str, b: str) -> bool:
    """O commit a é ancestral do commit b (ou é o mesmo)."""
    r = subprocess.run(["git", "-C", str(raiz), "merge-base", "--is-ancestor", a, b], capture_output=True)
    return r.returncode == 0


def links_quebrados(raiz: Path, caminho_md: str) -> list[str]:
    arq = raiz / caminho_md
    if not arq.exists():  # o PR apagou o arquivo
        return []
    quebrados = []
    for alvo in LINK_MD.findall(arq.read_text(encoding="utf-8")):
        if re.match(r"^[a-z]+:", alvo) or alvo.startswith("#"):
            continue
        alvo = alvo.split("#", 1)[0]
        if alvo and not (arq.parent / alvo).exists():
            quebrados.append(alvo)
    return quebrados


def verificar(corpo_bruto: str, mudados: list[str], raiz: Path) -> list[Item]:
    corpo = limpar(corpo_bruto)
    itens: list[Item] = []
    sec = secoes(corpo)

    # 1. Campos e seções (comum a todas as categorias).
    for nome in CAMPOS:
        valor = campo(corpo, nome)
        itens.append(Item(f"campo {nome}", "DECLARADA", not vazio(valor), valor or "falta"))
    for nome in SECOES:
        itens.append(Item(f"seção {nome}", "DECLARADA", not vazio(sec.get(nome)), "preenchida" if not vazio(sec.get(nome)) else "falta ou vazia"))

    categoria = (campo(corpo, "Categoria") or "").strip("` ").lower()
    if categoria not in CATEGORIAS:
        itens.append(Item("categoria válida", "DECLARADA", False, f"{categoria or 'nenhuma'}; use uma de {', '.join(CATEGORIAS)}"))
        return itens

    tarefa = campo(corpo, "Tarefa") or ""
    m = re.search(r"docs/TAREFA_V2_[\w-]+\.md", tarefa)
    if m:
        itens.append(Item("a tarefa existe", "VERIFICADA", (raiz / m.group(0)).exists(), m.group(0)))
    else:
        itens.append(Item("a tarefa existe", "VERIFICADA", False, "o campo Tarefa não cita docs/TAREFA_V2_*.md"))

    # 2. A frase de sucesso é sempre só declarada.
    for frase in SUCESSO.finditer(corpo):
        itens.append(Item("afirmação de sucesso", "DECLARADA", True,
                          f"\"{frase.group(0)}\": só conta se o job testes do CI passar", alerta=True))

    # 3. A regra da categoria.
    regra = REGRAS[categoria]
    itens.extend(regra(corpo, sec, mudados, raiz))
    return itens


def _implementacao(corpo, sec, mudados, raiz):
    itens = []
    citados = sorted(set(CAMINHO_TESTE.findall(corpo)))
    testes_mudados = [c for c in mudados if c.startswith("tests/") and c.endswith(".py")]
    itens.append(Item("há teste no PR", "VERIFICADA", bool(citados or testes_mudados),
                      f"mudados: {len(testes_mudados)}; citados: {len(citados)}"))
    for c in citados:
        itens.append(Item("o teste citado existe", "VERIFICADA", (raiz / c).exists(), c))
    return itens


def _experimento(corpo, sec, mudados, raiz):
    itens = []
    planos = sorted(set(CAMINHO_PLANO.findall(corpo)))
    itens.append(Item("plano de análise citado", "DECLARADA", bool(planos), ", ".join(planos) or "nenhum"))
    artefatos_citados = sorted(set(a.rstrip(".") for a in CAMINHO_ARTEFATO.findall(corpo)))
    for a in artefatos_citados:
        itens.append(Item("o artefato citado existe", "VERIFICADA", (raiz / a).exists(), a))
    artefatos_novos = [c for c in mudados if c.startswith("artifacts")]
    for p in planos:
        if not (raiz / p).exists():
            itens.append(Item("o plano existe", "VERIFICADA", False, p))
            continue
        cp = primeiro_commit(raiz, p)
        if cp is None:
            itens.append(Item("o plano está commitado", "VERIFICADA", False, p))
            continue
        for a in artefatos_novos:
            ca = primeiro_commit(raiz, a)
            ok = ca is not None and antes(raiz, cp, ca) and cp != ca
            itens.append(Item("plano commitado antes do artefato", "VERIFICADA", ok, f"{p} ({cp[:7]}) antes de {a} ({(ca or 'sem commit')[:7]})"))
    return itens


def _literatura(corpo, sec, mudados, raiz):
    itens = []
    lit = sec.get("Literatura", "")
    for nome in CAMPOS_LITERATURA:
        valor = campo(lit, nome)
        itens.append(Item(f"literatura: {nome}", "DECLARADA", not vazio(valor), valor or "falta"))
    conhecidos = dois_conhecidos(raiz)
    dois = sorted({normalizar_doi(d) for d in DOI.findall(corpo)})
    itens.append(Item("há DOI no relato", "DECLARADA", bool(dois), f"{len(dois)} DOI"))
    for d in dois:
        ok, fonte = conhecidos.get(d, (False, "não está em docs/referencias"))
        itens.append(Item("o DOI está em docs/referencias", "VERIFICADA", ok, f"{d} ({fonte})"))
    fora = [c for c in mudados if not c.startswith("docs/")]
    itens.append(Item("só docs/ mudou", "VERIFICADA", not fora, ", ".join(fora) or "ok"))
    return itens


def _arquitetura(corpo, sec, mudados, raiz):
    itens = [Item("status PROPOSTO", "DECLARADA", "PROPOSTO" in corpo, "o relato diz PROPOSTO" if "PROPOSTO" in corpo else "falta")]
    decisoes = sec.get("Decisões do Matheus", "")
    sem = vazio(decisoes) or re.fullmatch(r"\s*nenhuma\.?\s*", decisoes, re.I) is not None
    itens.append(Item("decisões do Matheus listadas", "DECLARADA", not sem, "listadas" if not sem else "uma arquitetura sempre leva decisão"))
    codigo = [c for c in mudados if c.startswith(CODIGO_PROIBIDO_ARQUITETURA)]
    itens.append(Item("nenhum código mudou", "VERIFICADA", not codigo, ", ".join(codigo) or "ok"))
    return itens


def _documentacao(corpo, sec, mudados, raiz):
    itens = []
    nao_doc = [c for c in mudados if not DOCUMENTO.search(c)]
    itens.append(Item("só documentos mudaram", "VERIFICADA", not nao_doc, ", ".join(nao_doc) or "ok"))
    for c in mudados:
        if c.endswith(".md"):
            q = links_quebrados(raiz, c)
            itens.append(Item("os links resolvem", "VERIFICADA", not q, f"{c}: {', '.join(q) or 'ok'}"))
    return itens


REGRAS = {
    "implementacao": _implementacao,
    "experimento": _experimento,
    "literatura": _literatura,
    "arquitetura": _arquitetura,
    "documentacao": _documentacao,
}


def tabela(itens: list[Item]) -> str:
    linhas = ["| regra | evidência | resultado | detalhe |", "|---|---|---|---|"]
    for i in itens:
        res = "alerta" if i.alerta else ("ok" if i.ok else "**FALHA**")
        det = i.detalhe.replace("|", "\\|")
        linhas.append(f"| {i.regra} | {i.coluna} | {res} | {det} |")
    falhas = sum(1 for i in itens if not i.ok and not i.alerta)
    linhas.append("")
    linhas.append(f"{falhas} falha(s). DECLARADA = escrito pelo agente, não é prova; VERIFICADA = conferido por esta ferramenta no repo. "
                  "A execução dos testes é conferida pelo job `testes`, não por este relatório.")
    return "\n".join(linhas)


def principal(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    fonte = p.add_mutually_exclusive_group()
    fonte.add_argument("--arquivo", type=Path)
    fonte.add_argument("--pr", type=int)
    fonte.add_argument("--env", help="nome da variável de ambiente com o corpo do PR")
    p.add_argument("--base", default="origin/main")
    p.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--listar-testes", action="store_true")
    a = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    raiz = a.raiz.resolve()

    if a.listar_testes:
        for c in mudados_por_git(raiz, a.base):
            if re.fullmatch(r"tests/test_[\w-]+\.py", c) and (raiz / c).exists():
                print(c)
        return 0

    if a.pr is not None:
        r = subprocess.run(["gh", "pr", "view", str(a.pr), "--json", "body,files"], capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            raise RuntimeError(f"gh pr view {a.pr} falhou: {r.stderr.strip()}")
        dados = json.loads(r.stdout)
        corpo, mudados = dados["body"], [f["path"] for f in dados["files"]]
    elif a.env:
        if a.env not in os.environ:
            raise RuntimeError(f"a variável {a.env} não está definida")
        corpo, mudados = os.environ[a.env], mudados_por_git(raiz, a.base)
    elif a.arquivo:
        corpo, mudados = a.arquivo.read_text(encoding="utf-8"), mudados_por_git(raiz, a.base)
    else:
        p.error("diga de onde vem o corpo: --arquivo, --pr ou --env")

    itens = verificar(corpo, mudados, raiz)
    saida = tabela(itens)
    print(saida)
    resumo = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumo:
        with open(resumo, "a", encoding="utf-8") as f:
            f.write("## Relato do PR\n\n" + saida + "\n")
    return 1 if any(not i.ok and not i.alerta for i in itens) else 0


if __name__ == "__main__":
    sys.exit(principal())
