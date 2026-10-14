"""O registro de desvios por mês (rodada de saúde, etapa 2; docs/TAREFA_V2_SAUDE.md).

O `docs/REGISTRO_DESVIOS.md` antigo era um arquivo só, com uma seção `## AAAA-MM-DD — ...` por desvio. Desde a etapa 2 cada seção
fica, inteira e na ordem, em `docs/registro/AAAA-MM.md` (o mês da data dela), e o `docs/REGISTRO_DESVIOS.md` vira o índice: uma linha
por seção, `- [<título>](registro/AAAA-MM.md)`, na ordem em que as seções entraram.

Dois comandos, os dois sem perder nem reescrever um byte das seções:

  python tools/registro_por_mes.py dividir --base <commit>
      parte o REGISTRO_DESVIOS.md antigo (o do disco) nos arquivos do mês e escreve o índice; grava o commit de base e o sha256 do
      arquivo antigo em docs/historico/registro_lotes.json (a base da conferência G-CONCAT).

  python tools/registro_por_mes.py absorver <commit>
      para um PR que ainda escreveu no formato antigo (a seção no fim do REGISTRO_DESVIOS.md): lê o REGISTRO_DESVIOS.md do commit pelo
      git, põe cada seção nova no fim do arquivo do mês dela, acrescenta a linha no índice e registra o lote. Uma seção que já existe
      com outro texto falha alto.

A conferência fica em tools/conferir_saude.py (G-CONCAT).
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REGISTRO = "docs/REGISTRO_DESVIOS.md"
PASTA = "docs/registro"
LOTES = "docs/historico/registro_lotes.json"
COPIA = "docs/historico/REGISTRO_DESVIOS_pre_saude.md"
CABECALHO_DATADO = re.compile(r"^## (\d{4})-(\d{2})-(\d{2}) ")
LINHA_INDICE = re.compile(r"^- \[(?P<titulo>.+)\]\((?P<arquivo>registro/\d{4}-\d{2}\.md)\)$")
MARCA_INDICE = "## Índice"

CABECALHO_INDICE = """# Registro de desvios de pré-condição e de interpretação

Desde 2026-10-13 (rodada de saúde, etapa 2; `docs/TAREFA_V2_SAUDE.md`) o registro fica **dividido por mês**, em
`docs/registro/AAAA-MM.md`. Este arquivo é só o **índice**: uma linha por seção, na ordem em que as seções entraram.

**Onde o worker escreve o desvio novo:**
1. **a seção,** `## AAAA-MM-DD — <FRENTE> (worker X): ...`, no **fim do arquivo do mês da data dela**, `docs/registro/AAAA-MM.md` (no
   primeiro desvio de um mês, o arquivo é criado);
2. **uma linha no fim deste índice,** com o título igual ao da seção: `- [AAAA-MM-DD — ...](registro/AAAA-MM.md)`.

Nunca escreva a seção aqui. Um PR que ainda escreveu no formato antigo é absorvido por `python tools/registro_por_mes.py absorver
<commit>`, e `python tools/conferir_saude.py` confere tudo (G-CONCAT).

O registro inteiro de antes da divisão, num arquivo só: `docs/historico/REGISTRO_DESVIOS_pre_saude.md` (a cópia da etapa 0) e o commit
de base em `docs/historico/registro_lotes.json`.

""" + MARCA_INDICE + "\n\n"


def ler(caminho: Path) -> str:
    """O texto exato, sem tradução de fim de linha."""
    return caminho.read_bytes().decode("utf-8")


def escrever(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto.encode("utf-8"))


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def partir(texto: str) -> tuple[str, list[tuple[str, str]]]:
    """O registro no formato antigo em (preâmbulo, [(título, trecho)]). O trecho vai do `## ` até o começo da seção seguinte, com as
    linhas em branco do fim: preâmbulo + os trechos, na ordem, dá o texto byte a byte. Toda seção tem de ser datada."""
    linhas = texto.splitlines(keepends=True)
    inicios = [i for i, l in enumerate(linhas) if l.startswith("## ")]
    if not inicios:
        raise ValueError("o registro não tem nenhuma seção '## '")
    preambulo = "".join(linhas[:inicios[0]])
    secoes = []
    for k, i in enumerate(inicios):
        fim = inicios[k + 1] if k + 1 < len(inicios) else len(linhas)
        titulo = linhas[i].rstrip("\r\n")[3:]
        if not CABECALHO_DATADO.match(linhas[i]):
            raise ValueError(f"seção sem data no formato AAAA-MM-DD: {titulo[:80]}")
        secoes.append((titulo, "".join(linhas[i:fim])))
    if preambulo + "".join(t for _, t in secoes) != texto:  # pragma: no cover - conferência da própria partição
        raise AssertionError("a partição não devolve o texto")
    return preambulo, secoes


def mes(titulo: str) -> str:
    m = CABECALHO_DATADO.match("## " + titulo)
    if m is None:
        raise ValueError(f"título sem data: {titulo[:80]}")
    return f"{m.group(1)}-{m.group(2)}"


def linha_indice(titulo: str) -> str:
    if "](" in titulo or "\n" in titulo:
        raise ValueError(f"título que o índice não consegue guardar: {titulo[:80]}")
    return f"- [{titulo}](registro/{mes(titulo)}.md)\n"


def ler_indice(texto: str) -> list[tuple[str, str]]:
    """As linhas do índice, (título, arquivo), na ordem. Falha alto com uma seção datada no índice ou com uma linha estranha depois da
    marca."""
    if MARCA_INDICE + "\n" not in texto:
        raise ValueError(f"o índice não tem a marca '{MARCA_INDICE}'")
    cabeca, corpo = texto.split(MARCA_INDICE + "\n", 1)
    for linha in cabeca.splitlines():
        if CABECALHO_DATADO.match(linha):
            raise ValueError(f"seção datada no índice (vai no arquivo do mês): {linha[:80]}")
    entradas = []
    for linha in corpo.splitlines():
        if not linha.strip():
            continue
        if CABECALHO_DATADO.match(linha):
            raise ValueError(f"seção datada no índice (vai no arquivo do mês): {linha[:80]}")
        m = LINHA_INDICE.match(linha)
        if m is None:
            raise ValueError(f"linha do índice fora do formato: {linha[:80]}")
        entradas.append((m.group("titulo"), "docs/" + m.group("arquivo")))
    return entradas


def arquivos_do_mes(raiz: Path) -> list[Path]:
    pasta = raiz / PASTA
    if not pasta.is_dir():
        return []
    estranhos = [p.name for p in pasta.iterdir() if not re.fullmatch(r"\d{4}-\d{2}\.md", p.name)]
    if estranhos:
        raise ValueError(f"arquivos fora do padrão AAAA-MM.md em {PASTA}: {sorted(estranhos)}")
    return sorted(pasta.iterdir())


def git_show(raiz: Path, commit: str, caminho: str) -> str:
    saida = subprocess.run(["git", "-C", str(raiz), "show", f"{commit}:{caminho}"], capture_output=True)
    if saida.returncode != 0:
        raise RuntimeError(f"não consegui ler {caminho} do commit {commit}: {saida.stderr.decode('utf-8', 'replace').strip()}")
    return saida.stdout.decode("utf-8")


def dividir(raiz: Path, base: str) -> dict:
    """Parte o REGISTRO_DESVIOS.md antigo do disco. O texto tem de ser o do commit de base (conferido pelo git)."""
    antigo = ler(raiz / REGISTRO)
    if git_show(raiz, base, REGISTRO) != antigo:
        raise ValueError(f"o {REGISTRO} do disco não é o do commit {base}")
    if arquivos_do_mes(raiz):
        raise ValueError(f"{PASTA} já tem arquivos: a divisão só roda uma vez")
    preambulo, secoes = partir(antigo)
    meses: dict[str, str] = {}
    for k, (titulo, trecho) in enumerate(secoes):
        m = mes(titulo)
        if meses and m not in meses and m < max(meses):
            raise ValueError(f"o mês {m} volta depois de {max(meses)}: a concatenação por mês não daria o original")
        meses[m] = meses.get(m, preambulo if k == 0 else "") + trecho
    for m, texto in meses.items():
        escrever(raiz / PASTA / f"{m}.md", texto)
    escrever(raiz / REGISTRO, CABECALHO_INDICE + "".join(linha_indice(t) for t, _ in secoes))
    lotes = {"base": {"commit": base, "arquivo": REGISTRO, "sha256": sha256(antigo), "secoes": len(secoes)}, "lotes": []}
    escrever(raiz / LOTES, json.dumps(lotes, ensure_ascii=False, indent=2) + "\n")
    return lotes


def absorver(raiz: Path, commit: str) -> list[str]:
    """As seções novas do REGISTRO_DESVIOS.md antigo de um commit, no fim do arquivo do mês, no índice e num lote. Devolve os títulos."""
    antigo = git_show(raiz, commit, REGISTRO)
    _, secoes = partir(antigo)
    conhecidas: dict[str, str] = {}
    for caminho in arquivos_do_mes(raiz):
        for titulo, trecho in partir(ler(caminho))[1]:
            conhecidas[titulo] = trecho.rstrip()
    ultima = max((k for k, (t, _) in enumerate(secoes) if t in conhecidas), default=-1)
    meio = [t for t, _ in secoes[:ultima] if t not in conhecidas]
    if meio:
        raise ValueError(f"seção desconhecida no meio do registro do commit (título mudado?): {meio[0][:80]}")
    novas = []
    for titulo, trecho in secoes:
        if titulo in conhecidas:
            if conhecidas[titulo] != trecho.rstrip():
                raise ValueError(f"a seção existe com outro texto: {titulo[:80]}")
            continue
        novas.append((titulo, trecho.rstrip()))
    if not novas:
        raise ValueError(f"o commit {commit} não tem seção nova no registro")
    indice = ler(raiz / REGISTRO)
    for titulo, corpo in novas:
        caminho = raiz / PASTA / f"{mes(titulo)}.md"
        atual = ler(caminho) if caminho.exists() else ""
        escrever(caminho, (atual + "\n" if atual else "") + corpo + "\n")
        indice += linha_indice(titulo)
    escrever(raiz / REGISTRO, indice)
    lotes = json.loads(ler(raiz / LOTES))
    lotes["lotes"].append({"commit": commit, "secoes": [t for t, _ in novas]})
    escrever(raiz / LOTES, json.dumps(lotes, ensure_ascii=False, indent=2) + "\n")
    return [t for t, _ in novas]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", default=".", help="a raiz do repositório")
    sub = ap.add_subparsers(dest="comando", required=True)
    d = sub.add_parser("dividir", help="parte o registro antigo do disco")
    d.add_argument("--base", required=True, help="o commit cujo REGISTRO_DESVIOS.md está no disco")
    a = sub.add_parser("absorver", help="traz as seções novas do registro antigo de um commit")
    a.add_argument("commit")
    args = ap.parse_args()
    raiz = Path(args.raiz)
    if args.comando == "dividir":
        lotes = dividir(raiz, args.base)
        print(f"dividido: {lotes['base']['secoes']} seções; base {args.base}, sha256 {lotes['base']['sha256']}")
    else:
        for titulo in absorver(raiz, args.commit):
            print("absorvida:", titulo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
