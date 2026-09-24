"""Bots canonicos da bateria V2.1: um por arquetipo adulto (8), em gambits de
ate 8 regras usando a tecnica da linha e a passiva da forma; um adolescente
por linha (5 regras, sem passiva, condicoes de adolescente) para o E4; e a
resposta declarada de cada tecnica (E3), escrita como uma regra de gambit.

Todos: temperamento neutro, ramo de crianca "sereno", carater canonico da
forma (catalogo.carater_canonico), condicao 1.0, epsilon de ConfigCombateV2.
"""

from __future__ import annotations

from ...config import CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, ConfigCatalogo, ConfigCombateV21
from .catalogo import LINHA_DA_FORMA, Forma, carater_canonico, perfil
from .gambits import Condicao as C, ListaGambits, Regra, lista, regra, se
from .partida import Lutador
from .regras import Acao as A, Distancia

PERTO, MEDIO, LONGE = Distancia.PERTO, Distancia.MEDIO, Distancia.LONGE


def _d(d: Distancia) -> C:
    return C("distancia_eh", (d,))


def _ga(g: int) -> C:
    return C("guts_proprio_acima", (g,))


def _gb(g: int) -> C:
    return C("guts_proprio_abaixo", (g,))


PREP = C("oponente_preparando")

ADULTOS: dict[str, ListaGambits] = {
    # brigao: investida na media distancia; pesado quando o oponente fecha a guarda
    "duelista": lista([
        regra(PREP, A.ESQUIVAR),
        regra(_d(MEDIO), A.INVESTIDA),
        regra(_d(LONGE), A.AVANCAR),
        regra(se(_d(PERTO), C("oponente_repete", (A.DEFENDER, 2))), A.PREPARAR_PESADO),
        regra(se(_d(PERTO), C("oponente_frequente", (A.ESQUIVAR,))), A.PREPARAR_PESADO),
        regra(se(_d(PERTO), _ga(40)), A.PREPARAR_PESADO),
        regra(_d(PERTO), A.GOLPE_RAPIDO),
        regra(_gb(20), A.CARREGAR),
    ], A.DEFENDER),
    # nao defende; fica mais perigoso com pouco hp
    "furioso": lista([
        regra(PREP, A.ESQUIVAR),
        regra(_d(MEDIO), A.INVESTIDA),
        regra(_d(LONGE), A.AVANCAR),
        regra(se(_d(PERTO), C("hp_proprio_abaixo", (0.5,))), A.GOLPE_RAPIDO),
        regra(se(_d(PERTO), _ga(40)), A.PREPARAR_PESADO),
        regra(_d(PERTO), A.GOLPE_RAPIDO),
        regra(_d(MEDIO), A.AVANCAR),
        regra(_gb(20), A.CARREGAR),
    ], A.CARREGAR),

    # guardiao: contra_golpe contra quem ataca; espelho tambem contra disparo
    "espelho": lista([
        regra(PREP, A.CONTRA_GOLPE),
        regra(C("oponente_frequente", (A.DISPARO,)), A.CONTRA_GOLPE),
        regra(C("oponente_frequente", (A.GOLPE_RAPIDO,)), A.CONTRA_GOLPE),
        regra(C("oponente_frequente", (A.INVESTIDA,)), A.CONTRA_GOLPE),
        regra(se(_d(PERTO), C("oponente_repete", (A.DEFENDER, 2))), A.PREPARAR_PESADO),
        regra(se(_d(PERTO), _ga(60)), A.GOLPE_RAPIDO),
        regra(_gb(40), A.CARREGAR),
        regra(_d(LONGE), A.AVANCAR),
    ], A.DEFENDER),
    # muralha: parede contra corpo a corpo; pune quando o oponente se fecha
    "muralha": lista([
        regra(PREP, A.CONTRA_GOLPE),
        regra(C("oponente_frequente", (A.GOLPE_RAPIDO,)), A.CONTRA_GOLPE),
        regra(se(_d(MEDIO), C("oponente_frequente", (A.INVESTIDA,))), A.DEFENDER),
        regra(se(_d(PERTO), C("oponente_repete", (A.DEFENDER, 2))), A.PREPARAR_PESADO),
        regra(se(_d(PERTO), C("oponente_guts_abaixo", (20,))), A.PREPARAR_PESADO),
        regra(C("oponente_frequente", (A.DISPARO,)), A.AVANCAR),
        regra(se(_d(MEDIO), _ga(60)), A.DISPARO),
        regra(_d(LONGE), A.AVANCAR),
    ], A.DEFENDER),

    # cacador: marca e dispara de longe; foge de perto
    "sentinela": lista([
        regra(se(PREP, _d(PERTO)), A.ESQUIVAR),
        regra(_d(PERTO), A.RECUAR),
        regra(C("oponente_repete", (A.AVANCAR, 2)), A.RECUAR),
        regra(C("oponente_frequente", (A.INVESTIDA,)), A.RECUAR),
        regra(_ga(40), A.MARCAR),
        regra(_ga(20), A.DISPARO),
        regra(_d(MEDIO), A.RECUAR),
        regra(_gb(20), A.CARREGAR),
    ], A.CARREGAR),
    "emboscador": lista([
        regra(se(PREP, _d(PERTO)), A.ESQUIVAR),
        regra(_d(PERTO), A.RECUAR),
        regra(C("turno_execucao", (5,)), A.MARCAR),
        regra(C("turno_execucao", (5,)), A.DISPARO),
        regra(se(_d(MEDIO), C("oponente_frequente", (A.AVANCAR,))), A.RECUAR),
        regra(_d(MEDIO), A.RECUAR),
        regra(_gb(60), A.CARREGAR),
        regra(_ga(60), A.MARCAR),
    ], A.CARREGAR),

    # colosso: pele_dura protege a preparacao do pesado
    # vigia: ve a preparacao chegando e interrompe com golpe rapido
    "vigia": lista([
        regra(se(C("oponente_vai_preparar"), _d(PERTO)), A.GOLPE_RAPIDO),
        regra(PREP, A.ESQUIVAR),
        regra(se(_d(PERTO), _ga(40)), A.PELE_DURA),
        regra(se(_d(PERTO), C("oponente_frequente", (A.ESQUIVAR,))), A.GOLPE_RAPIDO),
        regra(se(_d(PERTO), _ga(20)), A.PREPARAR_PESADO),
        regra(_d(MEDIO), A.AVANCAR),
        regra(_d(LONGE), A.AVANCAR),
        regra(_gb(20), A.CARREGAR),
    ], A.DEFENDER),
    "tita": lista([
        regra(PREP, A.PELE_DURA),
        regra(PREP, A.ESQUIVAR),
        regra(se(_d(PERTO), _ga(40)), A.PELE_DURA),
        regra(se(_d(PERTO), C("oponente_frequente", (A.ESQUIVAR,))), A.GOLPE_RAPIDO),
        regra(se(_d(PERTO), _ga(20)), A.PREPARAR_PESADO),
        regra(_d(MEDIO), A.AVANCAR),
        regra(_d(LONGE), A.AVANCAR),
        regra(_gb(20), A.CARREGAR),
    ], A.DEFENDER),
}

ADOLESCENTES: dict[str, ListaGambits] = {
    "brigao": lista([
        regra(PREP, A.ESQUIVAR),
        regra(_d(MEDIO), A.INVESTIDA),
        regra(_d(LONGE), A.AVANCAR),
        regra(se(_d(PERTO), _ga(40)), A.PREPARAR_PESADO),
        regra(_d(PERTO), A.GOLPE_RAPIDO),
    ], A.DEFENDER, "adolescente"),
    "guardiao": lista([
        regra(PREP, A.CONTRA_GOLPE),
        regra(se(_d(PERTO), C("oponente_guts_abaixo", (20,))), A.PREPARAR_PESADO),
        regra(se(_d(PERTO), _ga(60)), A.GOLPE_RAPIDO),
        regra(_gb(40), A.CARREGAR),
        regra(_d(LONGE), A.AVANCAR),
    ], A.DEFENDER, "adolescente"),
    "cacador": lista([
        regra(se(PREP, _d(PERTO)), A.ESQUIVAR),
        regra(_d(PERTO), A.RECUAR),
        regra(_ga(40), A.MARCAR),
        regra(_ga(20), A.DISPARO),
        regra(_d(MEDIO), A.RECUAR),
    ], A.CARREGAR, "adolescente"),
    "colosso": lista([
        regra(PREP, A.ESQUIVAR),
        regra(se(_d(PERTO), _ga(40)), A.PELE_DURA),
        regra(se(_d(PERTO), _ga(20)), A.PREPARAR_PESADO),
        regra(_d(MEDIO), A.AVANCAR),
        regra(_d(LONGE), A.AVANCAR),
    ], A.DEFENDER, "adolescente"),
}

# resposta declarada de cada tecnica (arvore_evolucao.json, campo "contra"):
# regras que o OPONENTE poe no topo da propria lista quando sabe que enfrenta
# quem tem a tecnica (as tecnicas sao publicas: a linha aparece na forma)
RESPOSTAS: dict[str, tuple[Regra, ...]] = {
    # "defender (parry)": na media distancia, fica em guarda
    "investida": (regra(_d(MEDIO), A.DEFENDER),),
    # "disparo, carregar e esperar": sai do corpo a corpo e atira
    "contra_golpe": (regra(_d(PERTO), A.RECUAR), regra(_ga(20), A.DISPARO)),
    # "avancar e pressionar de perto"
    "marcar": (regra(_d(LONGE), A.AVANCAR), regra(_d(MEDIO), A.AVANCAR)),
    # "ficar longe" e atirar depois do efeito
    "pele_dura": (regra(_d(PERTO), A.RECUAR), regra(_ga(20), A.DISPARO)),
}

FORMAS = tuple(ADULTOS)


def com_resposta(gl: ListaGambits, tecnica: str) -> ListaGambits:
    """Poe a resposta no topo; se a lista estourar o limite, saem as ultimas regras."""
    regras = RESPOSTAS[tecnica] + gl.regras
    limite = CONFIG_COMBATE_V21.max_regras_adulto
    return ListaGambits(regras[:limite], gl.final, gl.estagio)


def lutador_adulto(forma: str, especie: str, cfg: ConfigCombateV21 | None = None,
                   gambits: ListaGambits | None = None, nome: str | None = None,
                   cat: ConfigCatalogo | None = None) -> Lutador:
    cfg = cfg or CONFIG_COMBATE_V21
    f = Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[forma], forma)
    return Lutador(nome or f"{forma}@{especie}", perfil(f, None, carater_canonico(forma, cfg), 1.0, cfg, cat),
                   gambits or ADULTOS[forma], CONFIG_COMBATE_V2.epsilon_bots)


def lutador_adolescente(linha: str, especie: str, carater: dict, cfg: ConfigCombateV21 | None = None,
                        cat: ConfigCatalogo | None = None) -> Lutador:
    """Adolescente da linha com o MESMO carater do adulto comparado (E4)."""
    cfg = cfg or CONFIG_COMBATE_V21
    f = Forma(especie, "adolescente", "sereno", linha)
    return Lutador(f"adolescente-{linha}@{especie}", perfil(f, None, carater, 1.0, cfg, cat),
                   ADOLESCENTES[linha], CONFIG_COMBATE_V2.epsilon_bots)
