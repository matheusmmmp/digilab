"""Conferências da rodada de saúde (docs/TAREFA_V2_SAUDE.md).

Etapa 1 (G-NADA-PERDIDO): toda seção `## ` da cópia de antes do CLAUDE.md
(docs/historico/CLAUDE_pre_saude.md) tem de estar, igual e inteira, no destino
que o mapa (docs/historico/mapa_claude.json) dá a ela. Nenhuma seção pode ficar
sem destino, e o mapa não pode ter seção que a cópia não tem. O CLAUDE.md da
raiz tem de ter menos de 200 linhas.

Uso: python tools/conferir_saude.py [--raiz .]
Sai com 0 se tudo confere; com 1, e a lista do que falhou, se não.
"""
import argparse
import json
import sys
from pathlib import Path

COPIA = "docs/historico/CLAUDE_pre_saude.md"
MAPA = "docs/historico/mapa_claude.json"
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
    n_raiz = len((raiz / "CLAUDE.md").read_text(encoding="utf-8").splitlines())
    if n_raiz >= LIMITE_RAIZ:
        falhas.append(f"o CLAUDE.md da raiz tem {n_raiz} linhas (o limite é menos de {LIMITE_RAIZ})")
    return falhas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", default=".", help="a raiz do repositório")
    args = ap.parse_args()
    raiz = Path(args.raiz)
    falhas = conferir(raiz)
    n = len(secoes((raiz / COPIA).read_text(encoding="utf-8")))
    if falhas:
        print(f"G-NADA-PERDIDO FALHA ({len(falhas)}):")
        for f in falhas:
            print("  -", f)
        return 1
    print(f"G-NADA-PERDIDO passa: {n} seções da cópia, todas inteiras no destino do mapa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
