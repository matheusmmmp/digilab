"""O inventario da LIMPEZA (docs/TAREFA_V3_LIMPEZA.md): o grafo de imports do Python do repositorio e a classe de cada arquivo.

So le o codigo (AST); nao importa nada do projeto. As classes:
  - SAI:   um dos cerebros que saem (o bandit, o A, o B, o C, a camada unica e as politicas da v1 em cima do bandit), ou um
           arquivo que nenhuma raiz viva alcanca e que alcanca um deles;
  - REFAZ: um arquivo vivo (alcancado por uma raiz viva) que importa direto um arquivo que sai; precisa trocar o import por um
           modulo neutro antes de os cerebros sairem;
  - FICA:  o resto vivo, ou o que nao toca os cerebros;
  - REVER: um arquivo que nenhuma raiz viva alcanca e que nao toca os cerebros (codigo de etapas antigas a decidir caso a caso).

As raizes vivas sao o motor, o DigiBrain modular, a bancada, as runs da V3, as ferramentas e o servidor (RAIZES abaixo). Os testes
seguem a classe do que testam: um teste que importa direto um arquivo que sai e nada vivo e SAI; um que importa os dois e REFAZ.

    python tools/inventario_limpeza.py            # grava docs/limpeza/inventario_python.json e imprime o resumo
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "limpeza" / "inventario_python.json"
PASTAS = ("digilab", "experiments", "tests", "tools", "servidor", "scripts")

# os cerebros que saem (decisao do Matheus, 2026-11-16: o bandit, o A e a v1; tambem o B, o C e a camada unica)
SAEM = (
    "digilab/policies/bandit.py", "digilab/policies/lobos.py", "digilab/policies/cerebro_b.py",
    "digilab/policies/cerebro_c.py", "digilab/policies/camada_unica.py", "digilab/policies/__init__.py",
    "digilab/memoria.py", "digilab/memoria_espacos.py", "digilab/obediencia.py",
)
# o que fica vivo: o motor, o modular, o mundo, o corpo, o grupo, a bancada, as runs da V3, as ferramentas e o servidor
RAIZES_PREFIXO = ("digilab/digibrain/", "experiments/bancada/", "tools/", "servidor/")
RAIZES = (
    "digilab/engine.py", "digilab/mundo.py", "digilab/motor_corpo.py", "digilab/corpo.py", "digilab/grupo.py",
    "digilab/tv.py", "digilab/cooperacao.py", "digilab/frutas.py", "digilab/painel_digibrain.py",
    "experiments/bancada_v2.py", "experiments/run_v2_digibrain_prototipo.py", "experiments/run_v2_digibrain_l2.py",
)
RAIZES_GLOB = ("experiments/run_v3_*.py",)


def _arquivos() -> list[Path]:
    return sorted(p for d in PASTAS if (RAIZ / d).exists() for p in (RAIZ / d).rglob("*.py")
                  if "node_modules" not in p.parts and "__pycache__" not in p.parts)


def _rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def _nomes(arquivos: list[Path]) -> dict[str, str]:
    """nome de modulo -> arquivo: o pacote digilab.* e os modulos soltos de experiments/, tests/ e tools/ (que entram no sys.path)"""
    nomes: dict[str, str] = {}
    for p in arquivos:
        partes = _rel(p)[:-3].split("/")
        if partes[-1] == "__init__":
            partes = partes[:-1]
        nomes[".".join(partes)] = _rel(p)
    for p in arquivos:
        partes = _rel(p)[:-3].split("/")
        if partes[-1] == "__init__":
            partes = partes[:-1]
        if partes[0] in ("experiments", "tests", "tools") and len(partes) > 1:
            nomes.setdefault(".".join(partes[1:]), _rel(p))
    return nomes


def _resolver(nomes: dict[str, str], mod: str) -> str | None:
    while mod:
        if mod in nomes:
            return nomes[mod]
        mod = mod.rpartition(".")[0]
    return None


def grafo() -> dict[str, list[str]]:
    arquivos = _arquivos()
    nomes = _nomes(arquivos)
    arestas: dict[str, list[str]] = {}
    for p in arquivos:
        r = _rel(p)
        arv = ast.parse(p.read_text(encoding="utf-8"), filename=r)   # falha alto num arquivo que nao parseia
        pacote = r[:-3].split("/")[:-1] if not r.endswith("__init__.py") else r.split("/")[:-1]
        alvos: set[str] = set()
        for n in ast.walk(arv):
            if isinstance(n, ast.Import):
                for a in n.names:
                    x = _resolver(nomes, a.name)
                    if x:
                        alvos.add(x)
            elif isinstance(n, ast.ImportFrom):
                if n.level:
                    base = pacote[:len(pacote) - (n.level - 1)]
                    mod = ".".join(base + ([n.module] if n.module else []))
                else:
                    mod = n.module or ""
                for a in n.names:
                    y = _resolver(nomes, f"{mod}.{a.name}")
                    if y:
                        alvos.add(y)
                x = _resolver(nomes, mod)
                if x:
                    alvos.add(x)
        alvos.discard(r)
        arestas[r] = sorted(alvos)
    return arestas


def _fecho(arestas: dict[str, list[str]], inicio: set[str], parar: set[str]) -> set[str]:
    """os arquivos alcancados a partir de `inicio`, sem atravessar os de `parar`"""
    vistos, pilha = set(), list(inicio)
    while pilha:
        r = pilha.pop()
        if r in vistos or r in parar:
            continue
        vistos.add(r)
        pilha.extend(arestas.get(r, []))
    return vistos


def classificar(arestas: dict[str, list[str]]) -> dict[str, dict]:
    saem = set(SAEM)
    faltando = saem - set(arestas)
    if faltando:
        raise RuntimeError(f"arquivos que saem e nao existem: {sorted(faltando)}")
    raizes = {r for r in arestas if r in RAIZES or r.startswith(RAIZES_PREFIXO)
              or any(Path(r).match(g) for g in RAIZES_GLOB)}
    raizes -= saem
    vivos = _fecho(arestas, raizes, saem)
    tocam = {r for r in arestas if _fecho(arestas, {r}, set()) & saem}
    out = {}
    for r, alvos in arestas.items():
        diretos = sorted(set(alvos) & saem)
        if r.startswith("tests/"):
            vivos_importados = [a for a in alvos if a in vivos]
            if r in saem:
                classe = "SAI"
            elif diretos and not vivos_importados:
                classe = "SAI"
            elif diretos:
                classe = "REFAZ"
            elif r in tocam and not vivos_importados:
                classe = "SAI"
            elif not vivos_importados:
                classe = "REVER"
            else:
                classe = "FICA"
        elif r in saem:
            classe = "SAI"
        elif r in vivos:
            classe = "REFAZ" if diretos else "FICA"
        elif r in tocam:
            classe = "SAI"
        else:
            classe = "REVER"
        out[r] = {"classe": classe, "importa_direto_o_que_sai": diretos, "raiz": r in raizes}
    return out


def main() -> None:
    arestas = grafo()
    classes = classificar(arestas)
    resumo: dict[str, dict[str, int]] = {}
    for r, c in classes.items():
        area = r.split("/")[0]
        resumo.setdefault(area, {}).setdefault(c["classe"], 0)
        resumo[area][c["classe"]] += 1
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps({"rotulo": "inventario da LIMPEZA, gerado por tools/inventario_limpeza.py; so le o codigo",
                                 "saem": list(SAEM), "resumo": resumo, "arquivos": classes},
                                indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(resumo, indent=1, ensure_ascii=False, sort_keys=True))
    for r, c in sorted(classes.items()):
        if c["classe"] == "REFAZ" and not r.startswith("tests/"):
            print("REFAZ", r, c["importa_direto_o_que_sai"])


if __name__ == "__main__":
    sys.exit(main())
