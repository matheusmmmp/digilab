"""Conferências da rodada de saúde (docs/TAREFA_V2_SAUDE.md).

Etapa 1 (G-NADA-PERDIDO): toda seção `## ` da cópia de antes do CLAUDE.md
(docs/historico/CLAUDE_pre_saude.md) tem de estar, igual e inteira, no destino
que o mapa (docs/historico/mapa_claude.json) dá a ela. Nenhuma seção pode ficar
sem destino, e o mapa não pode ter seção que a cópia não tem. O CLAUDE.md da
raiz tem de ter menos de 200 linhas.

As seções que entraram no CLAUDE.md antigo depois da cópia (PRs que já estavam
abertos) ficam em lotes (docs/historico/mapa_claude_posteriores.json): para cada
lote, o CLAUDE.md do commit dele (`git show <commit>:CLAUDE.md`) só pode ter as
seções da cópia, iguais, e as seções do lote, cada uma inteira no destino.

Etapa 2 (G-CONCAT): o registro de desvios por mês (tools/registro_por_mes.py).
Os arquivos de docs/registro/, concatenados na ordem dos meses, começam pelo
REGISTRO_DESVIOS.md antigo do commit de base (docs/historico/registro_lotes.json),
byte a byte, e pela cópia da etapa 0. O índice (docs/REGISTRO_DESVIOS.md) tem uma
linha por seção, na ordem, e nenhuma seção datada. Cada seção está no arquivo do
mês da data dela. As seções que vieram depois pelo formato antigo (os lotes) são
iguais às do REGISTRO_DESVIOS.md do commit do lote.

Uso: python tools/conferir_saude.py [--raiz .]
Sai com 0 se tudo confere; com 1, e a lista do que falhou, se não.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro_por_mes as rpm  # noqa: E402

COPIA = "docs/historico/CLAUDE_pre_saude.md"
MAPA = "docs/historico/mapa_claude.json"
POSTERIORES = "docs/historico/mapa_claude_posteriores.json"
LIMITE_RAIZ = 200


def secoes(texto: str) -> list[tuple[str, str]]:
    """Parte o texto em (cabeçalho, corpo): o preâmbulo antes da primeira
    seção `## ` e cada seção até a seguinte. O corpo vai sem as linhas em
    branco do fim."""
    linhas = texto.split("\n")
    cab = [i for i, l in enumerate(linhas) if l.startswith("## ")]
    if not cab:
        raise ValueError("o texto não tem nenhuma seção '## '")
    partes = [("preambulo", 0, cab[0])]
    partes += [(linhas[c], c, cab[k + 1] if k + 1 < len(cab) else len(linhas)) for k, c in enumerate(cab)]
    saida = []
    for nome, a, b in partes:
        corpo = "\n".join(linhas[a:b]).rstrip()
        if not corpo:
            raise ValueError(f"seção vazia: {nome}")
        saida.append((nome, corpo))
    nomes = [n for n, _ in saida]
    if len(set(nomes)) != len(nomes):
        raise ValueError("há dois cabeçalhos iguais na cópia; o mapa não saberia qual é qual")
    return saida


def claude_do_commit(raiz: Path, commit: str) -> str:
    """O CLAUDE.md de um commit, pelo git. Falha alto se o git não achar."""
    saida = subprocess.run(["git", "-C", str(raiz), "show", f"{commit}:CLAUDE.md"], capture_output=True)
    if saida.returncode != 0:
        raise RuntimeError(f"não consegui ler o CLAUDE.md do commit {commit}: {saida.stderr.decode('utf-8', 'replace').strip()}")
    return saida.stdout.decode("utf-8")


def conferir(raiz: Path) -> list[str]:
    falhas = []
    copia = (raiz / COPIA).read_text(encoding="utf-8")
    mapa = json.loads((raiz / MAPA).read_text(encoding="utf-8"))
    partes = secoes(copia)
    nomes = {n for n, _ in partes}
    for extra in sorted(set(mapa) - nomes):
        falhas.append(f"o mapa tem uma seção que a cópia não tem: {extra[:80]}")
    cache: dict[str, str] = {}
    for nome, corpo in partes:
        destino = mapa.get(nome)
        if destino is None:
            falhas.append(f"seção sem destino no mapa: {nome[:80]}")
            continue
        if destino not in cache:
            caminho = raiz / destino
            if not caminho.exists():
                falhas.append(f"destino não existe: {destino}")
                cache[destino] = ""
                continue
            cache[destino] = caminho.read_text(encoding="utf-8")
        if corpo not in cache[destino]:
            falhas.append(f"seção não está inteira em {destino}: {nome[:80]}")
    antigas = dict(partes)
    caminho_post = raiz / POSTERIORES
    if caminho_post.exists():
        lotes = json.loads(caminho_post.read_text(encoding="utf-8"))["lotes"]
        for lote in lotes:
            commit, mapa_lote = lote["commit"], lote["secoes"]
            try:
                do_commit = secoes(claude_do_commit(raiz, commit))
            except RuntimeError as erro:
                falhas.append(str(erro))
                continue
            nomes_commit = {n for n, _ in do_commit}
            for extra in sorted(set(mapa_lote) - nomes_commit):
                falhas.append(f"lote {commit}: o mapa tem uma seção que o commit não tem: {extra[:80]}")
            for nome, corpo in do_commit:
                if nome in antigas:
                    if antigas[nome] != corpo:
                        falhas.append(f"lote {commit}: seção da cópia mudou no commit: {nome[:80]}")
                    continue
                destino = mapa_lote.get(nome)
                if destino is None:
                    falhas.append(f"lote {commit}: seção nova sem destino: {nome[:80]}")
                    continue
                texto = (raiz / destino).read_text(encoding="utf-8") if (raiz / destino).exists() else ""
                if corpo not in texto:
                    falhas.append(f"lote {commit}: seção não está inteira em {destino}: {nome[:80]}")
    n_raiz = len((raiz / "CLAUDE.md").read_text(encoding="utf-8").splitlines())
    if n_raiz >= LIMITE_RAIZ:
        falhas.append(f"o CLAUDE.md da raiz tem {n_raiz} linhas (o limite é menos de {LIMITE_RAIZ})")
    return falhas


def registro_do_commit(raiz: Path, commit: str) -> str:
    """O REGISTRO_DESVIOS.md de um commit, pelo git (os testes trocam esta função)."""
    return rpm.git_show(raiz, commit, rpm.REGISTRO)


def conferir_registro(raiz: Path) -> tuple[list[str], int]:
    """G-CONCAT. Devolve as falhas e o número de seções nos arquivos do mês."""
    falhas: list[str] = []
    try:
        indice = rpm.ler_indice(rpm.ler(raiz / rpm.REGISTRO))
        arquivos = rpm.arquivos_do_mes(raiz)
    except ValueError as erro:
        return [str(erro)], 0
    if not arquivos:
        return [f"{rpm.PASTA} não tem arquivo nenhum"], 0
    textos = {c: rpm.ler(c) for c in arquivos}
    achadas: list[tuple[str, str]] = []
    secoes: dict[str, str] = {}
    for k, (caminho, texto) in enumerate(textos.items()):
        rel = caminho.relative_to(raiz).as_posix()
        try:
            preambulo, ss = rpm.partir(texto)
        except ValueError as erro:
            falhas.append(f"{rel}: {erro}")
            continue
        if k > 0 and preambulo:
            falhas.append(f"{rel}: texto antes da primeira seção (só o primeiro mês tem o preâmbulo)")
        for titulo, trecho in ss:
            if rpm.mes(titulo) != caminho.stem:
                falhas.append(f"{rel}: seção de outro mês: {titulo[:80]}")
            if titulo in secoes:
                falhas.append(f"seção repetida: {titulo[:80]}")
            secoes[titulo] = trecho.rstrip()
            achadas.append((titulo, rel))
    if achadas != indice:
        falta = [t for t, _ in achadas if t not in {i for i, _ in indice}]
        sobra = [t for t, _ in indice if t not in secoes]
        falhas.append(f"o índice não lista as seções dos arquivos do mês, na ordem (sem linha: {len(falta)}"
                      + (f", a primeira: {falta[0][:60]}" if falta else "") + f"; linha sem seção: {len(sobra)}"
                      + (f", a primeira: {sobra[0][:60]}" if sobra else "") + ")")
    concat = "".join(textos.values())
    copia = raiz / rpm.COPIA
    if copia.exists() and not concat.startswith(rpm.ler(copia)):
        falhas.append(f"a concatenação dos meses não começa pela cópia da etapa 0 ({rpm.COPIA})")
    lotes = json.loads(rpm.ler(raiz / rpm.LOTES))
    base = lotes["base"]
    try:
        antigo = registro_do_commit(raiz, base["commit"])
    except RuntimeError as erro:
        falhas.append(str(erro))
    else:
        if rpm.sha256(antigo) != base["sha256"]:
            falhas.append(f"o registro do commit de base não tem o sha256 gravado: {base['commit']}")
        if not concat.startswith(antigo):
            falhas.append(f"G-CONCAT: a concatenação dos meses não começa pelo registro do commit de base {base['commit'][:12]}")
    for lote in lotes["lotes"]:
        commit, nomes = lote["commit"], lote["secoes"]
        try:
            _, do_commit = rpm.partir(registro_do_commit(raiz, commit))
        except (RuntimeError, ValueError) as erro:
            falhas.append(f"lote {commit}: {erro}")
            continue
        titulos = {t for t, _ in do_commit}
        for nome in nomes:
            if nome not in titulos:
                falhas.append(f"lote {commit}: o commit não tem a seção: {nome[:80]}")
        for titulo, trecho in do_commit:
            if titulo not in secoes:
                falhas.append(f"lote {commit}: seção do commit fora dos arquivos do mês: {titulo[:80]}")
            elif secoes[titulo] != trecho.rstrip():
                falhas.append(f"lote {commit}: seção diferente da do commit: {titulo[:80]}")
    return falhas, len(achadas)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", default=".", help="a raiz do repositório")
    args = ap.parse_args()
    raiz = Path(args.raiz)
    falhas = conferir(raiz)
    n = len(secoes((raiz / COPIA).read_text(encoding="utf-8")))
    caminho_post = raiz / POSTERIORES
    if caminho_post.exists():
        n += sum(len(l["secoes"]) for l in json.loads(caminho_post.read_text(encoding="utf-8"))["lotes"])
    rc = 0
    if falhas:
        print(f"G-NADA-PERDIDO FALHA ({len(falhas)}):")
        for f in falhas:
            print("  -", f)
        rc = 1
    else:
        print(f"G-NADA-PERDIDO passa: {n} seções (a cópia e os lotes posteriores), todas inteiras no destino do mapa.")
    falhas_reg, n_reg = conferir_registro(raiz)
    if falhas_reg:
        print(f"G-CONCAT FALHA ({len(falhas_reg)}):")
        for f in falhas_reg:
            print("  -", f)
        return 1
    lotes = json.loads(rpm.ler(raiz / rpm.LOTES))
    print(f"G-CONCAT passa: {n_reg} seções nos arquivos do mês, o índice na ordem; a concatenação começa pelo registro do commit "
          f"{lotes['base']['commit'][:12]} (sha256 {lotes['base']['sha256'][:16]}…) e pela cópia da etapa 0; "
          f"{sum(len(l['secoes']) for l in lotes['lotes'])} seções de lotes conferidas.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
