"""Gera a fala da voz-v1 (CONVERSA_PET, DC2): conceitos -> mensagens -> LLM -> parser. Nunca decide nada no pet.

Como `gerar.py`, mas a entrada e `Conceitos` (conceitos.py) e nao o estado do pet: o pedido nao tem fato de estado, memoria, desejo
nem log. O resultado carrega, em `fatos`, os conceitos ativos (tipo "conceito", com o id [C1]...) e os [J] "o dono me disse",
que sao o que o verificador (verif-v7) e o registro de apresentacao precisam ver.
"""

from __future__ import annotations

from .conceitos import Conceitos
from .corpus import Especie, bloco_estilo, repete_citacao
from .fatos import ESTAGIOS
from .gerar import Resultado
from .ollama import ClienteOllama
from .prompt import (MAX_CHARS, MAX_TOKENS, VERSAO_VOZ_V1, esquema, fatos_do_dono_voz, ids_conceitos, linha_conceito,
                     mensagens_voz)
from .saida import FALA_GENERICA, SaidaInvalida, aparar, ler

TIPO_CONCEITO = "conceito"


def fatos_da_voz(conceitos: Conceitos, historico, estagio: str, situacao: str = "conversa") -> list[dict]:
    """Os `fatos` do verificador: {id, tipo, texto} dos conceitos ativos e dos [J]. O texto do conceito e a linha do prompt."""
    fatos = [{"id": cid, "tipo": TIPO_CONCEITO, "texto": linha_conceito(cid, c).split("] ", 1)[1], **c.para_dict()}
             for cid, c in ids_conceitos(conceitos).items()]
    if situacao == "conversa":
        fatos += [f.para_dict() for f in fatos_do_dono_voz(historico, estagio)]
    return fatos


def gerar_voz(cliente: ClienteOllama, conceitos: Conceitos, estagio: str, situacao: str, fala_jogador: str | None = None,
              historico=None, semente: int = 0, especie: Especie | None = None, comando: bool = False) -> Resultado:
    """Saida invalida, falha de rede ou citacao repetida do corpus viram a fala generica (a fala sempre acontece; a LLM nunca faz
    o pet agir por engano de formato)."""
    if estagio not in ESTAGIOS:
        raise ValueError(f"voz-v1: estagio desconhecido: {estagio!r}")
    estilo = bloco_estilo(especie) if especie is not None else None
    msgs = mensagens_voz(conceitos, estagio, situacao, fala_jogador, historico, estilo=estilo, comando=comando)
    fatos = tuple(fatos_da_voz(conceitos, historico, estagio, situacao))
    base = dict(fatos=fatos, estagio=estagio, modelo=cliente.modelo, versao_prompt=VERSAO_VOZ_V1,
                especie=especie.especie if especie is not None else None)
    try:
        r = cliente.conversar(msgs, esquema(estagio, comando), MAX_TOKENS[estagio], semente)
    except (OSError, ValueError) as err:
        return Resultado(FALA_GENERICA, (), erro=f"chamada: {type(err).__name__}: {err}", latencia_s=None, **base)
    try:
        f = ler(r.texto)
    except SaidaInvalida as err:
        return Resultado(FALA_GENERICA, (), erro=f"saida: {err}", latencia_s=r.latencia_s, **base)
    fala = aparar(f.fala, MAX_CHARS[estagio])
    if especie is not None:
        c = repete_citacao(fala, especie.citacoes)
        if c is not None:
            return Resultado(FALA_GENERICA, (), erro=f"repete_citacao: {c}", latencia_s=r.latencia_s, **base)
    return Resultado(fala, f.fatos_citados, latencia_s=r.latencia_s, erro=None, comando=f.comando if comando else None, **base)
