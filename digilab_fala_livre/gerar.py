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
from .prompt import MAX_CHARS, MAX_TOKENS, VERSAO_PROMPT, VERSOES_VOZ, esquema, mensagens
from .saida import FALA_GENERICA, FalaLivre, SaidaInvalida, aparar, ler


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
    comando: str | None = None      # livre-v7, conversa: a acao do dono que o pet entendeu (catalogo) ou None


def _queda(bloco_fatos, erro: str, **base) -> Resultado:
    """sem fala da LLM: a mentira ordenada pelo motor sai pelo molde; o resto vira a fala generica"""
    f = next((x for x in bloco_fatos if x.tipo == TIPO_MENTIRA), None)
    if f is None:
        return Resultado(FALA_GENERICA, (), erro=erro, **base)
    return Resultado(f.texto[0].upper() + f.texto[1:] + ".", (f.id,), erro=erro, **base)


def gerar(cliente: ClienteOllama, estado: dict, situacao: str, fala_jogador: str | None = None,
          historico: list[tuple[str, str]] | None = None, semente: int = 0, versao: str = VERSAO_PROMPT,
          especie: Especie | None = None, rival: str | None = None, comando: bool = False) -> Resultado:
    """comando (livre-v7, so na conversa): pede e le o campo "comando". Saida invalida (inclusive comando fora do
    catalogo) vira a fala generica com comando None: a LLM nunca faz o pet agir por engano de formato."""
    if especie is not None and versao not in VERSOES_VOZ:
        raise ValueError("o estilo da especie so existe nos prompts da voz propria (v3, v4)")
    fatos = fatos_de_estado(estado)              # FatosInvalidos sobe: sem fatos validos nao ha fala
    est = estagio_de(fatos)
    estilo = bloco_estilo(especie, rival) if especie is not None else None
    msgs = mensagens(fatos, situacao, fala_jogador, historico, versao=versao, estilo=estilo, comando=comando)
    base = dict(fatos=tuple(f.para_dict() for f in fatos), estagio=est, modelo=cliente.modelo, versao_prompt=versao,
                especie=especie.especie if especie is not None else None)
    try:
        r = cliente.conversar(msgs, esquema(est, comando), MAX_TOKENS[est], semente)
    except (OSError, ValueError) as err:          # rede, timeout, resposta que nao e JSON do Ollama
        return _queda(fatos, f"chamada: {type(err).__name__}: {err}", latencia_s=None, **base)
    try:
        f: FalaLivre = ler(r.texto)
    except SaidaInvalida as err:
        return _queda(fatos, f"saida: {err}", latencia_s=r.latencia_s, **base)
    fala = aparar(f.fala, MAX_CHARS[est])        # bateu no limite do esquema: fica so a parte inteira
    if especie is not None:
        c = repete_citacao(fala, especie.citacoes)
        if c is not None:
            return _queda(fatos, f"repete_citacao: {c}", latencia_s=r.latencia_s, **base)
    return Resultado(fala, f.fatos_citados, latencia_s=r.latencia_s, erro=None, comando=f.comando if comando else None,
                     **base)
