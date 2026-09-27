"""Parser da saida da LLM: falha alto (SaidaInvalida) com qualquer coisa fora do formato.

Quem chama registra o erro e usa FALA_GENERICA, que nao afirma nada (nunca inventa conteudo).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

FALA_GENERICA = "…"
MAX_FALA = 320


class SaidaInvalida(ValueError):
    """A LLM devolveu algo que nao e {"fala": str, "fatos_citados": [str]}."""


@dataclass(frozen=True)
class FalaLivre:
    fala: str
    fatos_citados: tuple[str, ...]


def ler(texto: str) -> FalaLivre:
    if not isinstance(texto, str) or not texto.strip():
        raise SaidaInvalida("saida vazia")
    try:
        d = json.loads(texto)
    except json.JSONDecodeError as err:
        raise SaidaInvalida(f"nao e JSON: {err.msg}") from err
    if not isinstance(d, dict) or set(d) != {"fala", "fatos_citados"}:
        raise SaidaInvalida(f"chaves erradas: {sorted(d) if isinstance(d, dict) else type(d).__name__}")
    fala, cit = d["fala"], d["fatos_citados"]
    if not isinstance(fala, str) or not fala.strip():
        raise SaidaInvalida("fala vazia ou nao e texto")
    if len(fala) > MAX_FALA:
        raise SaidaInvalida(f"fala longa demais ({len(fala)} caracteres)")
    if not isinstance(cit, list) or not all(isinstance(c, str) for c in cit):
        raise SaidaInvalida("fatos_citados precisa ser lista de textos")
    # surrogate UTF-16 solto (o qwen as vezes devolve) quebra a gravacao: trata como saida invalida
    try:
        fala.encode("utf-8")
    except UnicodeEncodeError as err:
        raise SaidaInvalida("texto com caractere invalido") from err
    return FalaLivre(fala.strip(), tuple(c.strip().strip("[]") for c in cit))
