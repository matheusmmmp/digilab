"""Parser da saida da LLM: falha alto (SaidaInvalida) com qualquer coisa fora do formato.

Quem chama registra o erro e usa FALA_GENERICA, que nao afirma nada (nunca inventa conteudo).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass

FALA_GENERICA = "…"
ID_NA_FALA = re.compile(r"\[([A-Z]\d{1,2})\]")
MAX_FALA = 320
# TAREFA_COMANDO_CHAT: catalogo FECHADO do comando pelo chat = AcaoDono do jogo web (web/app/motor/tipos.ts). A LLM so
# propoe um destes (ou null); o app valida de novo e o motor executa como acao do dono. Treino, luta e itens ficam fora.
CATALOGO_COMANDOS = ("alimentar", "limpar", "brincar", "acariciar", "elogiar", "repreender",
                     "petisco", "levar_ao_banheiro", "tratar_lesao")


class SaidaInvalida(ValueError):
    """A LLM devolveu algo que nao e {"fala": str, "fatos_citados": [str]} (com "comando" opcional no catalogo)."""


@dataclass(frozen=True)
class FalaLivre:
    fala: str
    fatos_citados: tuple[str, ...]
    comando: str | None = None      # livre-v7, so na conversa: uma acao do CATALOGO_COMANDOS ou None


FIM_DE_FRASE = ".!?…"


def aparar(fala: str, limite: int) -> str:
    """A fala que bateu no limite de caracteres do esquema veio cortada no meio da palavra (o Ollama para a geracao na
    gramatica: "Vou co-c"). Fica so o que e inteiro: ate o ultimo fim de frase; sem fim de frase, ate o ultimo espaco, com
    reticencias. Abaixo do limite a fala nao muda (as rodadas gravadas nao mudam)."""
    if len(fala) < limite:
        return fala
    corte = max(fala.rfind(c) for c in FIM_DE_FRASE)
    if corte > 0:
        return fala[:corte + 1].strip()
    espaco = fala.rfind(" ")
    if espaco > 0:
        return fala[:espaco].rstrip(",;:-") + "…"
    return fala


def ler(texto: str) -> FalaLivre:
    if not isinstance(texto, str) or not texto.strip():
        raise SaidaInvalida("saida vazia")
    try:
        d = json.loads(texto)
    except json.JSONDecodeError as err:
        raise SaidaInvalida(f"nao e JSON: {err.msg}") from err
    if not isinstance(d, dict) or set(d) - {"comando"} != {"fala", "fatos_citados"}:
        raise SaidaInvalida(f"chaves erradas: {sorted(d) if isinstance(d, dict) else type(d).__name__}")
    fala, cit = d["fala"], d["fatos_citados"]
    # "comando" ausente (fala espontanea) = nenhum; presente, so null ou uma acao do catalogo: fora dele falha alto
    comando = d.get("comando")
    if comando is not None and comando not in CATALOGO_COMANDOS:
        raise SaidaInvalida(f"comando fora do catalogo: {comando!r}")
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
    fora = sorted({c for c in fala if c.isalpha() and not unicodedata.name(c, "").startswith("LATIN")})
    if fora:            # a rodada 4 teve uma fala com caracteres chineses no meio do portugues
        raise SaidaInvalida(f"letras fora do alfabeto latino: {''.join(fora)!r}")
    # identificador escrito dentro da fala ("...no [W1]"): sai do texto e entra na lista de citados
    ids = ID_NA_FALA.findall(fala)
    fala = " ".join(ID_NA_FALA.sub("", fala).split())
    fala = re.sub(r"\s+([,.!?;:])", lambda m: m.group(1), fala)
    if not fala:
        raise SaidaInvalida("fala so com identificadores")
    citados = tuple(dict.fromkeys([c.strip().strip("[]") for c in cit] + ids))
    return FalaLivre(fala.strip(), citados, comando)
