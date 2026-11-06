"""Gera o índice de desvios, docs/REGISTRO_DESVIOS.md, a partir dos arquivos do mês (docs/TAREFA_V3_INDICE_DESVIOS.md, D-ID1 a D-ID4).

O índice é função dos arquivos de docs/registro/: o cabeçalho (`CABECALHO_INDICE`) e uma linha por seção `## AAAA-MM-DD — ...`, na ordem
dos meses e, dentro do mês, na ordem do arquivo. O worker não edita o índice; quem faz o merge regenera depois de cada leva (D-ID2). Um
conflito no índice se resolve rodando este gerador, nunca à mão.

Só lê os arquivos do mês; nunca escreve neles.

Uso:
  python tools/gerar_indice_desvios.py             # escreve docs/REGISTRO_DESVIOS.md
  python tools/gerar_indice_desvios.py --conferir  # sai com 1 se o índice do disco não é o gerado (o CI só avisa)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro_por_mes as rpm  # noqa: E402


def entradas(raiz: Path) -> list[tuple[str, str]]:
    """As seções dos arquivos do mês, (título, arquivo relativo à raiz), na ordem do índice. Falha alto sem arquivo do mês."""
    arquivos = rpm.arquivos_do_mes(raiz)
    if not arquivos:
        raise ValueError(f"{rpm.PASTA} não tem arquivo nenhum")
    return [(titulo, c.relative_to(raiz).as_posix()) for c in arquivos for titulo, _ in rpm.partir(rpm.ler(c))[1]]


def gerar(raiz: Path) -> str:
    return rpm.CABECALHO_INDICE + "".join(rpm.linha_indice(t) for t, _ in entradas(raiz))


def atrasadas(raiz: Path) -> list[str]:
    """Os títulos das seções que ainda não têm linha no índice do disco (o atraso que o G-CONCAT aceita no PR, D-ID3)."""
    listados = {t for t, _ in rpm.ler_indice(rpm.ler(raiz / rpm.REGISTRO))}
    return [t for t, _ in entradas(raiz) if t not in listados]


def principal(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", type=Path, default=Path("."), help="a raiz do repositório")
    ap.add_argument("--conferir", action="store_true", help="só confere; sai com 1 se o índice não é o gerado")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    destino = a.raiz / rpm.REGISTRO
    novo = gerar(a.raiz)
    n = novo.count("\n- [")
    if a.conferir:
        if not destino.exists() or rpm.ler(destino) != novo:
            falta = atrasadas(a.raiz) if destino.exists() else []
            print(f"{rpm.REGISTRO} não é o gerado ({len(falta)} seção(ões) sem linha): rode python tools/gerar_indice_desvios.py")
            return 1
        print(f"{rpm.REGISTRO} em dia: {n} seções.")
        return 0
    rpm.escrever(destino, novo)
    print(f"escrito: {rpm.REGISTRO}, {n} seções.")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
