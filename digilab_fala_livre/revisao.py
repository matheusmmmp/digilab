"""Autocorrecao da fala livre (rodada 3 de artifacts_voz): o pet revisa a propria fala.

A fala continua sendo escrita pela LLM (livre-v4), sem moldura. Depois de gerar, o PROPRIO modelo roda o
verificador (verif-v4) sobre a fala; se houver afirmacao sem fato, trecho de cobranca ou manipulacao, a fala volta
para ele com os trechos apontados e o pedido de reescrever sem eles, no mesmo jeito. No maximo `MAX_REVISOES`
reescritas. Se nenhuma versao passar, fica a que tem menos problemas (empate: a mais recente).

A medida da rodada e feita depois por um juiz INDEPENDENTE (outro modelo): a revisao nao se mede sozinha.

`so_respeito` (livre-v6, decisao do Matheus em 2026-09-30): o pet pode inventar, desde que a invencao seja
identificada. So volta para revisao a manipulacao; cada invencao fica marcada em `invencoes`. Se a fala nao puder ser
verificada (erro do verificador em todas as versoes), ela e CORTADA e o pet diz o texto verdadeiro do assunto.
"""

from __future__ import annotations

import json
from dataclasses import replace

from .corpus import Especie
from .gerar import Resultado, gerar
from .ollama import ClienteOllama
from .prompt import MAX_TOKENS, VERSAO_PROMPT_V4, esquema
from .saida import FALA_GENERICA, SaidaInvalida, ler
from .verificador import VERSAO_VERIFICADOR_V4, VERSAO_VERIFICADOR_V5, Verificacao, verificar

MAX_REVISOES = 2
VERSAO_REVISAO = "revisao-v1"


def _problemas(v: Verificacao, so_respeito: bool = False) -> list[str]:
    """so_respeito (livre-v6): invencao e livre; so volta para revisao a manipulacao e o fato citado que nao existe"""
    ps = [] if so_respeito else [a["trecho"] for a in v.afirmacoes if a["sustentada"] is False]
    ps += v.manipulacao_extraida + [f"(padrão de manipulação: {p})" for p in v.manipulacao_padroes]
    if v.citados_inexistentes:
        ps.append(f"(citou fatos que não existem: {', '.join(v.citados_inexistentes)})")
    return ps


def _pedido_revisao(problemas: list[str], so_respeito: bool = False) -> str:
    lista = "\n".join(f"- {p}" for p in problemas)
    if so_respeito:
        return ("REVISÃO: estes trechos usam culpa, chantagem, ameaça ou apelo para prender o jogador, ou citam um "
                "fato que não existe:\n" + lista + "\nReescreva a fala sem isso, com o mesmo jeito e o mesmo assunto. "
                "Mesmo formato JSON.")
    return ("REVISÃO: na sua fala, estes trechos afirmam algo que não está nos FATOS ou cobram o jogador:\n" + lista +
            "\nReescreva a fala SEM esses trechos, com o mesmo jeito e o mesmo assunto. Diga só o que os FATOS "
            "sustentam. Mesmo formato JSON.")


def gerar_com_revisao(cliente: ClienteOllama, estado: dict, situacao: str = "espontanea", semente: int = 0,
                      versao: str = VERSAO_PROMPT_V4, especie: Especie | None = None, rival: str | None = None,
                      max_revisoes: int = MAX_REVISOES,
                      versao_verificador: str = VERSAO_VERIFICADOR_V4,
                      so_respeito: bool = False) -> tuple[Resultado, list[dict]]:
    """(resultado final, tentativas). Cada tentativa: fala, fatos citados, problemas apontados pelo proprio modelo."""
    from .corpus import bloco_estilo
    from .fatos import fatos_de_estado
    from .prompt import mensagens
    r = gerar(cliente, estado, situacao, semente=semente, versao=versao, especie=especie, rival=rival)
    tentativas = []
    if r.erro is not None:
        return r, tentativas
    msgs = mensagens(fatos_de_estado(estado), situacao, versao=versao,
                     estilo=bloco_estilo(especie, rival) if especie is not None else None)
    atual = r
    for n in range(max_revisoes + 1):
        v = verificar(cliente, atual.fala, atual.fatos_citados, list(atual.fatos), semente=semente + 7919 * (n + 1),
                      versao=versao_verificador)
        probs = _problemas(v, so_respeito) if v.erro is None else []
        tentativas.append({"fala": atual.fala, "fatos_citados": list(atual.fatos_citados), "problemas": probs,
                           "invencoes": [a["trecho"] for a in v.afirmacoes if a["sustentada"] is False],
                           "erro_verificacao": v.erro, "latencia_s": atual.latencia_s})
        if not probs or n == max_revisoes:
            break
        msgs = msgs + [{"role": "assistant", "content": json.dumps({"fala": atual.fala, "fatos_citados":
                                                                     list(atual.fatos_citados)}, ensure_ascii=False)},
                       {"role": "user", "content": _pedido_revisao(probs, so_respeito)}]
        try:
            resp = cliente.conversar(msgs, esquema(atual.estagio), MAX_TOKENS[atual.estagio], semente + 104729 * (n + 1))
            f = ler(resp.texto)
        except (OSError, ValueError, SaidaInvalida) as err:
            tentativas.append({"fala": None, "erro": f"{type(err).__name__}: {err}"})
            break
        atual = replace(atual, fala=f.fala, fatos_citados=f.fatos_citados, latencia_s=resp.latencia_s)
    validas = [(i, t) for i, t in enumerate(tentativas) if t.get("fala") not in (None, FALA_GENERICA)]
    if so_respeito:
        # livre-v6 (decisao do Matheus): inventar pode, desde que a invencao seja IDENTIFICADA. Fala que o
        # verificador nao conseguiu conferir e cortada: no lugar, o texto verdadeiro do assunto
        validas = [(i, t) for i, t in validas if t.get("erro_verificacao") is None]
        if not validas:
            a = next((f for f in r.fatos if f["id"][:1] in "FWHOPL"), None)
            if a is None:
                return replace(r, fala=FALA_GENERICA, fatos_citados=(), erro="cortada: sem verificacao"), tentativas
            texto = a["texto"][0].upper() + a["texto"][1:] + "."
            return replace(r, fala=texto, fatos_citados=(a["id"],), erro="cortada: sem verificacao"), tentativas
    i, melhor = min(validas, key=lambda it: (len(it[1]["problemas"]), -it[0]))
    final = replace(r, fala=melhor["fala"], fatos_citados=tuple(melhor["fatos_citados"]))
    return final, tentativas
