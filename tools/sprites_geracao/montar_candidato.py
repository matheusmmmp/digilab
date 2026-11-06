"""SPRITES_GERACAO, etapa G1, E6 (docs/TAREFA_V3_SPRITES_GERACAO.md, secao 3.4): monta o diretorio do atlas candidato.

Copia os 60 Digimon do catalogo (Assets/catalogo_sprites_up.json) de remaster/acoes/export so com a tag Comer (sem o lote 1: Feliz,
Sacudir, Chamar, Emburrar) e o <Nome>_objeto, e troca o Digimon da prova pelo gerado (remaster/geracao/<Nome>/export). Grava em
remaster/geracao/candidato/export, que o `Assets/gerar_atlas_up_clipes.py --acoes ... --saida remaster/geracao/candidato/atlas` le.
NUNCA escreve em remaster/acoes nem em Assets. Sem `--gerado`, o candidato e so o derivado (teste de fumaca da montagem).
Falha alto: Digimon do catalogo sem export, tag Comer ausente, gerado de outro Digimon, saida dentro de remaster/acoes ou de Assets.

Uso: python tools/sprites_geracao/montar_candidato.py [--nome Agumon --gerado DIR] [--remaster DIR] [--assets DIR] [--saida DIR]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import converter as C  # noqa: E402
import ficha as F  # noqa: E402

ASSETS = F.AQUI.parents[2] / "Assets"


def digimons_do_catalogo(assets: Path) -> list[str]:
    cat = json.loads((assets / "catalogo_sprites_up.json").read_text(encoding="utf-8"))
    return sorted({e["digimon"] for e in cat["formas"].values()})


def so_comer(origem: Path, nome: str, destino: Path) -> None:
    """Regrava <nome> so com a tag Comer, renumerada de 0 (descarta as outras tags do lote 1)."""
    c = F.ler_export(origem / nome, "Comer")
    C.gravar(destino, nome, c.quadros, c.ms)


def proibido(saida: Path) -> None:
    partes = {p.name for p in [saida.resolve(), *saida.resolve().parents]}
    if "acoes" in partes or "Assets" in partes:
        raise SystemExit(f"a saida {saida} cai em remaster/acoes ou Assets: use remaster/geracao/candidato/export")


def montar(remaster: Path, assets: Path, saida: Path, nome: str | None = None, gerado: Path | None = None) -> int:
    proibido(saida)
    if (nome is None) != (gerado is None):
        raise ValueError("--nome e --gerado vao juntos")
    lista = digimons_do_catalogo(assets)
    if nome is not None and nome not in lista:
        raise ValueError(f"{nome} nao esta no catalogo")
    if saida.exists():
        shutil.rmtree(saida)
    for d in lista:
        origem = gerado if d == nome else remaster / "acoes" / "export"
        for n in (d, d + "_objeto"):
            so_comer(origem, n, saida)
    # confere: 60 Digimon, dois arquivos cada, e o Digimon da prova veio do gerado
    arquivos = sorted(p.stem for p in saida.glob("*.json"))
    if len(arquivos) != 2 * len(lista):
        raise AssertionError(f"candidato com {len(arquivos)} exports, esperava {2 * len(lista)}")
    return len(lista)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E6: monta o candidato (60 Digimon, so o Comer)")
    ap.add_argument("--nome", default=None)
    ap.add_argument("--gerado", type=Path, default=None, help="pasta export do gerado (remaster/geracao/<Nome>/export)")
    ap.add_argument("--remaster", type=Path, default=F.REMASTER)
    ap.add_argument("--assets", type=Path, default=ASSETS)
    ap.add_argument("--saida", type=Path, default=None, help="padrao: <remaster>/geracao/candidato/export")
    a = ap.parse_args(argv)
    saida = a.saida or a.remaster / "geracao" / "candidato" / "export"
    n = montar(a.remaster, a.assets, saida, a.nome, a.gerado)
    print(f"{saida}: {n} Digimon so com o Comer" + (f", {a.nome} do gerado" if a.nome else " (todos derivados)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
