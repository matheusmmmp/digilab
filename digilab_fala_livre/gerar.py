"""Gera uma fala livre: fatos -> mensagens -> Ollama local -> parser. Nunca decide nada no pet."""

from __future__ import annotations

from dataclasses import dataclass

from .fatos import estagio_de, fatos_de_estado
from .ollama import ClienteOllama
from .prompt import MAX_TOKENS, VERSAO_PROMPT, esquema, mensagens
from .saida import FALA_GENERICA, FalaLivre, SaidaInvalida, ler


@dataclass(frozen=True)
class Resultado:
    fala: str
    fatos_citados: tuple[str, ...]
    fatos: tuple[dict, ...]         # o bloco usado (para o verificador e para o log de apresentacao)
    estagio: str
    modelo: str
    versao_prompt: str
    latencia_s: float | None
    erro: str | None                # SaidaInvalida ou falha de rede: a fala vira a generica


def gerar(cliente: ClienteOllama, estado: dict, situacao: str, fala_jogador: str | None = None,
          historico: list[tuple[str, str]] | None = None, semente: int = 0) -> Resultado:
    fatos = fatos_de_estado(estado)              # FatosInvalidos sobe: sem fatos validos nao ha fala
    est = estagio_de(fatos)
    msgs = mensagens(fatos, situacao, fala_jogador, historico)
    base = dict(fatos=tuple({"id": f.id, "tipo": f.tipo, "texto": f.texto} for f in fatos), estagio=est,
                modelo=cliente.modelo, versao_prompt=VERSAO_PROMPT)
    try:
        r = cliente.conversar(msgs, esquema(est), MAX_TOKENS[est], semente)
    except (OSError, ValueError) as err:          # rede, timeout, resposta que nao e JSON do Ollama
        return Resultado(FALA_GENERICA, (), latencia_s=None, erro=f"chamada: {type(err).__name__}: {err}", **base)
    try:
        f: FalaLivre = ler(r.texto)
    except SaidaInvalida as err:
        return Resultado(FALA_GENERICA, (), latencia_s=r.latencia_s, erro=f"saida: {err}", **base)
    return Resultado(f.fala, f.fatos_citados, latencia_s=r.latencia_s, erro=None, **base)
