"""Campanha contra NPCs no combate V2.1 (docs/TAREFA_TREINO_SOMBRIO.md, secao 5).

Separada da arena: os stats NAO sao normalizados ao orcamento da especie (o NPC tem
total 72, 80 ou 90; um pet do catalogo tem 60). Sem treino por enquanto: os pets
lutam com os stats da forma (a parte "com treino" espera a tarefa de treino).

NPC = stats uniformes (total / 6 em cada stat), adulto, sem tecnica nem passiva,
estilo em gambits:
  tier1_brutamontes  agressivo    (bateria V2)
  tier2_sentinela    contragolpe  (bateria V2)
  tier3_soberano     adaptativo da bateria V2. A tarefa pede corrigi-lo porque, no
                     prototipo (docs/pve.py, com finta/parry/morte subita), o estilo
                     atirador vencia o chefe sem treino (0,67). No combate V2.1 isso
                     NAO se repete (atirador 0,06 contra o chefe original), e a
                     correcao testada (GAMBIT_SOBERANO_RESPOSTA_LONGE) piora: os
                     cacadores passam a vence-lo. Fica o original; a correcao fica
                     registrada em artifacts_campanha/campanha.json, chave "soberano".
Os gambits da V2 sao traduzidos para a linguagem da V2.1 pelo nome (mesmas
condicoes e acoes).
"""

from __future__ import annotations

from .combate_v2.bots import GAMBITS as GAMBITS_V2, GAMBITS_V2C
from .combate_v2.regras import Acao as AcaoV2
from .combate_v2.v21.catalogo import Perfil
from .combate_v2.v21.gambits import CONDICAO_DO_VIGIA, Condicao as C, ListaGambits, Regra, lista, regra, se
from .combate_v2.v21.partida import Lutador
from .combate_v2.v21.bots import ADULTOS, CRIANCAS
from .combate_v2.v21.regras import TECNICAS, Acao, Distancia, Regras
from .config import (CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2C, CONFIG_COMBATE_V21, CONFIG_COMBATE_V21C,
                     STATS_V21, ConfigCampanha)

PERTO, MEDIO, LONGE = Distancia.PERTO, Distancia.MEDIO, Distancia.LONGE

# a campanha luta com o combate corrigido aprovado (V2C + V21C), o mesmo da web
REGRAS_CAMPANHA = Regras(base=CONFIG_COMBATE_V2C, v21=CONFIG_COMBATE_V21C)


def traduzir(gl_v2, estagio: str = "adulto") -> ListaGambits:
    """ListaGambits da V2 -> V2.1 (acao pelo valor; distancia e numeros iguais)."""
    def par(p):
        return Acao(p.value) if isinstance(p, AcaoV2) else p

    regras = tuple(Regra(tuple(C(c.nome, tuple(par(p) for p in c.params)) for c in r.condicoes), Acao(r.acao.value))
                   for r in gl_v2.regras)
    return ListaGambits(regras, Regra((C("sempre"),), Acao(gl_v2.final.acao.value)), estagio)


# adaptativo da V2 com resposta a luta de longe (8 regras): quem foge e atira leva
# perseguicao (avancar quando o oponente insiste em recuar ou disparar) e troca de tiro
# quando esta longe com guts sobrando, em vez de so avancar e levar disparo de graca
GAMBIT_SOBERANO_RESPOSTA_LONGE = lista([
    regra(C("oponente_preparando"), Acao.ESQUIVAR),
    regra(C("oponente_repete", (Acao.DEFENDER, 2)), Acao.PREPARAR_PESADO),
    regra(C("oponente_frequente", (Acao.PREPARAR_PESADO,)), Acao.GOLPE_RAPIDO),
    regra(C("oponente_frequente", (Acao.GOLPE_RAPIDO,)), Acao.DEFENDER),
    regra(se(C("oponente_frequente", (Acao.DISPARO,)), C("guts_proprio_acima", (40,))), Acao.DISPARO),
    regra(C("oponente_frequente", (Acao.RECUAR,)), Acao.AVANCAR),
    regra(se(C("distancia_eh", (PERTO,)), C("guts_proprio_acima", (40,))), Acao.GOLPE_RAPIDO),
    regra(C("guts_proprio_acima", (20,)), Acao.AVANCAR),
], Acao.CARREGAR)


def gambit_npc(estilo: str, estagio: str = "adulto") -> ListaGambits:
    """'<familia>:<nome>': v2 (bateria V2), v2c (bots redesenhados da V2C) ou v21 (gambits canonicos de
    uma forma adulta sem as regras de tecnica e da passiva do vigia, que o NPC nao tem). Sem familia = v2."""
    if estilo == "soberano_resposta_longe":    # correcao testada e NAO adotada
        return GAMBIT_SOBERANO_RESPOSTA_LONGE
    familia, _, nome = estilo.rpartition(":")
    if familia in ("", "v2"):                   # os bots da V2 valem no estagio do NPC (se couberem nele)
        return traduzir(GAMBITS_V2[nome], estagio)
    if familia == "v2c":
        return traduzir(GAMBITS_V2C[nome], estagio)
    if familia == "crianca":                   # sementes das criancas (bots.CRIANCAS)
        return CRIANCAS[nome]
    if familia == "v21":                       # sem tecnica nem passiva: saem as regras que dependem delas
        g = ADULTOS[nome]
        return ListaGambits(tuple(r for r in g.regras if r.acao not in TECNICAS.values()
                                  and all(c.nome != CONDICAO_DO_VIGIA for c in r.condicoes)), g.final, g.estagio)
    raise ValueError(f"familia de estilo desconhecida: {estilo}")


def perfil_de_stats(rotulo: str, stats: dict, estagio: str = "adulto", cfg=None, cat=None) -> Perfil:
    """Mesma conversao stat -> combate de catalogo.perfil, sem forma e sem renormalizar."""
    cfg = cfg or CONFIG_COMBATE_V21
    cat = cat or CONFIG_CATALOGO
    if set(stats) != set(STATS_V21):
        raise ValueError(f"stats incompletos: {sorted(stats)}")
    est = cat.mult_estagio[estagio]
    gmax = (cfg.guts_max_base + cfg.guts_max_por_folego * stats["folego"]) * est
    return Perfil(rotulo=rotulo, estagio=estagio, tecnica=None, passiva=None,
                  hp_max=(cfg.hp_base + cfg.hp_por_vigor * stats["vigor"]) * est,
                  guts_inicial=min(gmax, (cfg.guts_inicial_base + cfg.guts_inicial_por_folego * stats["folego"]) * est),
                  guts_max=gmax, regen=cfg.regen_base + cfg.regen_por_recuperacao * stats["recuperacao"],
                  mult_perto=cfg.mult_base + cfg.mult_por_ponto * stats["forca"],
                  mult_disparo=cfg.mult_base + cfg.mult_por_ponto * stats["mira"],
                  mult_guarda=cfg.guarda_base - cfg.guarda_por_ponto * stats["guarda"], stats=dict(stats))


def npc(tier: str, estilo: str | None = None, cfg: ConfigCampanha | None = None) -> Lutador:
    cfg = cfg or CONFIG_CAMPANHA
    d = cfg.npcs[tier]
    stats = {k: d["total_stats"] / len(STATS_V21) for k in STATS_V21}
    est = estilo or d["estilo"]
    return Lutador(f"npc:{tier}:{est}", perfil_de_stats(tier, stats, d.get("estagio", "adulto"), cfg=REGRAS_CAMPANHA.v21),
                   gambit_npc(est, d.get("estagio", "adulto")), d.get("epsilon", cfg.epsilon_npc))
