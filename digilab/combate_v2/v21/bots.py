"""Bots canonicos da bateria V2.1: um por arquetipo adulto (8), em gambits de
ate 8 regras usando a tecnica da linha e a passiva da forma; um adolescente
por linha (5 regras, sem passiva, condicoes de adolescente) para o E4; e a
resposta declarada de cada tecnica (E3), escrita como uma regra de gambit.

Todos: temperamento neutro, ramo de crianca "sereno", carater canonico da
forma (catalogo.carater_canonico), condicao 1.0, epsilon de ConfigCombateV2.
"""

from __future__ import annotations

from ...config import CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, CONFIG_SOMBRIO, ConfigCatalogo, ConfigCombateV21
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

# criancas (espelho de CRIANCA_V21 da web, que semeia o pet crianca): sem tecnica, 3 regras
CRIANCAS: dict[str, ListaGambits] = {
    "sereno": lista([
        regra(_gb(40), A.CARREGAR),
        regra(_d(LONGE), A.AVANCAR),
        regra(se(_d(PERTO), _ga(40)), A.GOLPE_RAPIDO),
    ], A.DEFENDER, "crianca"),
    "arisco": lista([
        regra(_d(LONGE), A.AVANCAR),
        regra(_d(MEDIO), A.AVANCAR),
        regra(se(_d(PERTO), _ga(20)), A.GOLPE_RAPIDO),
    ], A.CARREGAR, "crianca"),
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

# V21C: resposta ao marcar redesenhada (TAREFA_CORRECAO_COMBATE, Etapa 3). A de cima avanca sempre e
# empurra para fora do limite de 8 as ultimas regras do oponente, que passa a jogar pior; esta so reage
# quando o oponente de fato usa marcar: avanca do medio e golpeia de perto (a marca fragil se perde).
RESPOSTAS_V21C = {**RESPOSTAS, "marcar": (
    regra(se(_d(MEDIO), C("oponente_frequente", (A.MARCAR,))), A.AVANCAR),
    regra(se(_d(PERTO), C("oponente_frequente", (A.MARCAR,))), A.GOLPE_RAPIDO))}

FORMAS = tuple(ADULTOS)

# V21D, candidato C (docs/EQUILIBRIO_RODADA1.md; chave muralha_lista_espelho, desligada por padrao): a muralha luta
# com a lista do espelho, como a alavanca (d) "gambits da irma" medida no diagnostico dos arquetipos. As regras de
# contra_golpe fora de perto ficam na lista mas nunca disparam na muralha (sem a passiva do espelho o contra_golpe
# so e legal de perto; a lista cai na regra seguinte). ADULTOS["muralha"] (a canonica) nao muda.
GAMBITS_MURALHA_V21D = ListaGambits(ADULTOS["espelho"].regras, ADULTOS["espelho"].final, "adulto")


# V21D, rodada 2 (docs/EQUILIBRIO_RODADA2.md; chaves desligadas por padrao). Listas variantes do colosso, montadas a
# partir das canonicas (ADULTOS["tita"] e ADULTOS["vigia"] nao mudam):
# - E2 (tita_bate_em_quem_recua, vigia_bate_em_quem_recua): "de perto, contra quem recua com frequencia, golpe
#   rapido" entra logo antes do preparar; sai "oponente preparando -> esquivar" (com o candidato A o preparo sob pele
#   ja nao aparece, e o tita responde ao preparo com a pele antes).
# - V (vigia_recua_do_preparo_sob_pele): "o oponente vai preparar e usa pele com frequencia -> recuar" entra no topo
#   do vigia: o preparo sob pele nao se interrompe, entao ele sai de perto e o pesado erra por distancia. Sai
#   "guts abaixo de 20 -> carregar" (a final defender tambem recupera guts).
REGRA_BATE_EM_QUEM_RECUA = regra(se(_d(PERTO), C("oponente_frequente", (A.RECUAR,))), A.GOLPE_RAPIDO)
REGRA_RECUA_DO_PREPARO_SOB_PELE = regra(se(C("oponente_vai_preparar"), C("oponente_frequente", (A.PELE_DURA,))),
                                        A.RECUAR)


def _lista_colosso_v21d(forma: str, bate: bool, recua: bool) -> ListaGambits:
    regras = list(ADULTOS[forma].regras)
    if bate:
        regras.remove(regra(PREP, A.ESQUIVAR))
        regras.insert(regras.index(regra(se(_d(PERTO), _ga(20)), A.PREPARAR_PESADO)), REGRA_BATE_EM_QUEM_RECUA)
    if recua:
        regras.remove(regra(_gb(20), A.CARREGAR))
        regras.insert(0, REGRA_RECUA_DO_PREPARO_SOB_PELE)
    return ListaGambits(tuple(regras), ADULTOS[forma].final, "adulto")


GAMBITS_TITA_V21D = _lista_colosso_v21d("tita", bate=True, recua=False)
GAMBITS_VIGIA_V21D = {(b, r): _lista_colosso_v21d("vigia", b, r) for b, r in ((True, False), (False, True), (True, True))}


# V21E, rodada de equilibrio geral, fase 1 (docs/EQUILIBRIO_GERAL.md; chaves da ConfigCombateV21E, desligadas por
# padrao). Edicoes sobre a lista que a forma teria sem elas (a canonica ou a variante da V21D):
# - duelista_defende_do_golpe, tita_defende_do_golpe: "de perto, contra quem usa golpe rapido com frequencia, defender"
#   entra logo depois das regras que leem o preparo do oponente (o parry da base V2C devolve dano a cada golpe
#   defendido); sai "guts abaixo de 20 -> carregar" (a final defender tambem recupera guts).
# - espelho_sem_carregar, muralha_sem_carregar: sai "guts abaixo de 40 -> carregar" (carregar recebe dano x1,5).
# - muralha_contra_golpe_na_pele: "o oponente usa pele_dura com frequencia -> contra_golpe" entra logo depois da
#   primeira regra (a do preparo): o preparo sob pele nao aparece (candidato A) e a muralha nao tem o contra-golpe a
#   distancia do espelho.
REGRA_DEFENDE_DO_GOLPE = regra(se(_d(PERTO), C("oponente_frequente", (A.GOLPE_RAPIDO,))), A.DEFENDER)
REGRA_CONTRA_GOLPE_NA_PELE = regra(C("oponente_frequente", (A.PELE_DURA,)), A.CONTRA_GOLPE)
_CARREGAR_20 = regra(_gb(20), A.CARREGAR)
_CARREGAR_40 = regra(_gb(40), A.CARREGAR)


def _depois_das_leituras_do_preparo(regras: list) -> int:
    """Indice logo depois da ultima regra do topo que le o preparo do oponente (oponente_preparando)."""
    i = 0
    while i < len(regras) and PREP in regras[i].condicoes:
        i += 1
    return i


def _lista_v21e(forma: str, gl: ListaGambits, cfg) -> ListaGambits:
    """Aplica as edicoes das chaves da ConfigCombateV21E ligadas para `forma` sobre `gl`. Regra a remover que nao esta na
    lista falha alto (ValueError de list.remove)."""
    k = lambda nome: getattr(cfg, nome, False)  # noqa: E731
    regras = list(gl.regras)
    if forma in ("duelista", "tita") and k(f"{forma}_defende_do_golpe"):
        regras.remove(_CARREGAR_20)
        regras.insert(_depois_das_leituras_do_preparo(regras), REGRA_DEFENDE_DO_GOLPE)
    elif forma in ("espelho", "muralha") and k(f"{forma}_sem_carregar"):
        regras.remove(_CARREGAR_40)
    if forma == "muralha" and k("muralha_contra_golpe_na_pele"):
        regras.insert(1, REGRA_CONTRA_GOLPE_NA_PELE)
    if forma == "muralha" and (k("muralha_sem_carregar") or k("muralha_contra_golpe_na_pele")) and not k(
            "muralha_lista_espelho"):
        raise ValueError("as chaves da muralha na V21E pedem muralha_lista_espelho")
    if regras == list(gl.regras):
        return gl
    return ListaGambits(tuple(regras), gl.final, "adulto")


CHAVES_LISTAS_V21E = ("duelista_defende_do_golpe", "tita_defende_do_golpe", "espelho_sem_carregar",
                      "muralha_sem_carregar", "muralha_contra_golpe_na_pele")


def gambits_adulto(forma: str, cfg: ConfigCombateV21 | None = None) -> ListaGambits:
    """Lista canonica da forma adulta (normal ou sombria) sob as regras `cfg`: a de ADULTOS/SOMBRIOS, salvo as listas
    variantes das chaves da ConfigCombateV21D ligadas (muralha: muralha_lista_espelho; tita: tita_bate_em_quem_recua;
    vigia: vigia_bate_em_quem_recua e vigia_recua_do_preparo_sob_pele) e, por cima delas, as edicoes das chaves da
    ConfigCombateV21E (_lista_v21e). As sombrias nao mudam."""
    cfg = cfg or CONFIG_COMBATE_V21
    gl = _gambits_adulto_v21d(forma, cfg)
    if forma in FORMAS and any(getattr(cfg, c, False) for c in CHAVES_LISTAS_V21E):
        return _lista_v21e(forma, gl, cfg)
    return gl


def _gambits_adulto_v21d(forma: str, cfg) -> ListaGambits:
    if forma == "muralha" and getattr(cfg, "muralha_lista_espelho", False):
        return GAMBITS_MURALHA_V21D
    if forma == "tita" and getattr(cfg, "tita_bate_em_quem_recua", False):
        return GAMBITS_TITA_V21D
    if forma == "vigia":
        chave = (getattr(cfg, "vigia_bate_em_quem_recua", False), getattr(cfg, "vigia_recua_do_preparo_sob_pele", False))
        if any(chave):
            return GAMBITS_VIGIA_V21D[chave]
    if forma in ADULTOS:
        return ADULTOS[forma]
    if forma in SOMBRIOS:
        return SOMBRIOS[forma]
    raise KeyError(f"forma adulta desconhecida: {forma!r}")

# formas sombrias (TAREFA_TREINO_SOMBRIO): "a sombra corrompe o que o pet e, nao apaga" -> cada uma
# luta com os gambits da forma normal da linha de estilo mais proximo; regras com acao que a passiva
# sombria proibe simplesmente nunca disparam (eh_legal). PROPOSTO.
GAMBIT_BASE_SOMBRIA = {"devastador": "furioso", "bastiao_rachado": "espelho", "predador": "emboscador",
                       "colosso_partido": "tita"}
# redesenho para o S2 (atalho com custo: vence a prova de stats, perde a de estilo). A sombra tira a
# leitura do oponente: o devastador fecha e bate rapido, e so solta o pesado com guts sobrando; o bastiao
# fica com os gambits do espelho SEM as regras que leem o oponente; o predador (nao pode recuar) fecha e
# bate rapido. O colosso partido fica com os do tita.
SOMBRIOS: dict[str, ListaGambits] = {s: ADULTOS[b] for s, b in GAMBIT_BASE_SOMBRIA.items()}
SOMBRIOS["devastador"] = lista([
    regra(_d(LONGE), A.AVANCAR),
    regra(_d(MEDIO), A.AVANCAR),
    regra(se(_d(PERTO), _ga(60)), A.PREPARAR_PESADO),
    regra(_d(PERTO), A.GOLPE_RAPIDO),
], A.CARREGAR)
SOMBRIOS["predador"] = lista([
    regra(_d(LONGE), A.AVANCAR),
    regra(_d(MEDIO), A.AVANCAR),
    regra(_d(PERTO), A.GOLPE_RAPIDO),
], A.CARREGAR)
SOMBRIOS["bastiao_rachado"] = ListaGambits(
    tuple(r for r in ADULTOS["espelho"].regras if not any(c.nome.startswith("oponente_") for c in r.condicoes)),
    ADULTOS["espelho"].final, "adulto")


def com_resposta(gl: ListaGambits, tecnica: str, respostas: dict | None = None) -> ListaGambits:
    """Poe a resposta no topo; se a lista estourar o limite, saem as ultimas regras."""
    regras = (respostas or RESPOSTAS)[tecnica] + gl.regras
    limite = CONFIG_COMBATE_V21.max_regras_adulto
    return ListaGambits(regras[:limite], gl.final, gl.estagio)


def lutador_adulto(forma: str, especie: str, cfg: ConfigCombateV21 | None = None,
                   gambits: ListaGambits | None = None, nome: str | None = None,
                   cat: ConfigCatalogo | None = None, escala=None) -> Lutador:
    """escala: ConfigEscala ligada (Parte C da TAREFA_PLANILHA_PROGRESSAO) ou None (o de sempre)."""
    cfg = cfg or CONFIG_COMBATE_V21
    f = Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[forma], forma)
    eps = CONFIG_COMBATE_V2.epsilon_bots
    if f.sombria:
        eps = max(eps, CONFIG_SOMBRIO.epsilon_minimo)          # instavel: ignora os gambits as vezes
    return Lutador(nome or f"{forma}@{especie}", perfil(f, None, carater_canonico(forma, cfg), 1.0, cfg, cat, escala=escala),
                   gambits or gambits_adulto(forma, cfg), eps)


def lutador_adolescente(linha: str, especie: str, carater: dict, cfg: ConfigCombateV21 | None = None,
                        cat: ConfigCatalogo | None = None, escala=None, treino: dict | None = None) -> Lutador:
    """Adolescente da linha com o MESMO carater do adulto comparado (E4). `treino` (so com a escala: E4')."""
    cfg = cfg or CONFIG_COMBATE_V21
    f = Forma(especie, "adolescente", "sereno", linha)
    sufixo = f"+{sum(treino.values()):g}" if treino else ""
    return Lutador(f"adolescente-{linha}{sufixo}@{especie}", perfil(f, None, carater, 1.0, cfg, cat, treino=treino, escala=escala),
                   ADOLESCENTES[linha], CONFIG_COMBATE_V2.epsilon_bots)
