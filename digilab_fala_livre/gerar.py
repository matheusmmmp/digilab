"""Gera uma fala livre: fatos -> mensagens -> Ollama local -> parser. Nunca decide nada no pet.

livre-v3 (DESIGN_VOZ_PROPRIA): `especie` (corpus.Especie) poe o bloco de ESTILO no pedido e liga o filtro contra
repetir citacao (a fala que copia 6+ palavras seguidas de uma citacao do corpus e reprovada e vira a generica).
Se a LLM falhar numa fala com mentira [F1], o pet diz o molde fixo da mentira: a fala sempre acontece e o motor
nao depende da LLM.
"""

from __future__ import annotations

from dataclasses import dataclass

from .corpus import Especie, bloco_estilo, repete_citacao
from .fatos import TIPO_MENTIRA, estagio_de, fatos_de_estado
from .ollama import ClienteOllama
from .prompt import MAX_TOKENS, VERSAO_PROMPT, VERSAO_PROMPT_V3, esquema, mensagens
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
    erro: str | None                # SaidaInvalida, falha de rede ou citacao repetida: a fala vira a generica
    especie: str | None = None      # livre-v3: especie do bloco de estilo (corpus)


def _queda(bloco_fatos, erro: str, **base) -> Resultado:
    """sem fala da LLM: a mentira ordenada pelo motor sai pelo molde; o resto vira a fala generica"""
    f = next((x for x in bloco_fatos if x.tipo == TIPO_MENTIRA), None)
    if f is None:
        return Resultado(FALA_GENERICA, (), erro=erro, **base)
    return Resultado(f.texto[0].upper() + f.texto[1:] + ".", (f.id,), erro=erro, **base)


def gerar(cliente: ClienteOllama, estado: dict, situacao: str, fala_jogador: str | None = None,
          historico: list[tuple[str, str]] | None = None, semente: int = 0, versao: str = VERSAO_PROMPT,
          especie: Especie | None = None, rival: str | None = None) -> Resultado:
    if especie is not None and versao != VERSAO_PROMPT_V3:
        raise ValueError("o estilo da especie so existe no prompt livre-v3")
    fatos = fatos_de_estado(estado)              # FatosInvalidos sobe: sem fatos validos nao ha fala
    est = estagio_de(fatos)
    estilo = bloco_estilo(especie, rival) if especie is not None else None
    msgs = mensagens(fatos, situacao, fala_jogador, historico, versao=versao, estilo=estilo)
    base = dict(fatos=tuple(f.para_dict() for f in fatos), estagio=est, modelo=cliente.modelo, versao_prompt=versao,
                especie=especie.especie if especie is not None else None)
    try:
        r = cliente.conversar(msgs, esquema(est), MAX_TOKENS[est], semente)
    except (OSError, ValueError) as err:          # rede, timeout, resposta que nao e JSON do Ollama
        return _queda(fatos, f"chamada: {type(err).__name__}: {err}", latencia_s=None, **base)
    try:
        f: FalaLivre = ler(r.texto)
    except SaidaInvalida as err:
        return _queda(fatos, f"saida: {err}", latencia_s=r.latencia_s, **base)
    if especie is not None:
        c = repete_citacao(f.fala, especie.citacoes)
        if c is not None:
            return _queda(fatos, f"repete_citacao: {c}", latencia_s=r.latencia_s, **base)
    return Resultado(f.fala, f.fatos_citados, latencia_s=r.latencia_s, erro=None, **base)
