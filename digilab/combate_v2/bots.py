"""Bots da bateria do combate V2.

Todos os bots FIXOS e o ADAPTATIVO sao ListaGambits: isso prova que a
linguagem e expressiva. O `oraculo` e REFERENCIA FORA DA LINGUAGEM
(fora_da_linguagem=True): melhor resposta de 1 passo contra a distribuicao
empirica das acoes do oponente na partida. Serve de teto, nunca de alvo.

Limitacoes da linguagem encontradas ao escrever os bots (reportadas, o
catalogo NAO foi ampliado):
  - nao existe "ultima acao do oponente foi X" (oponente_repete so aceita
    k em {2, 3}). O `contragolpe` nao consegue punir "logo depois" do pesado
    do oponente; aproxima com "oponente com pouco guts" (quem acabou de
    preparar/esquivar gastou guts).
  - nao existe condicao sobre a PROPRIA acao anterior nem negacao; "manter
    distancia media/longe" do atirador vira "se perto, recua".
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..config import CONFIG_COMBATE_V2, ConfigCombateV2
from .gambits import EXPLORACAO, PESADO_AUTOMATICO, Condicao as C, Motivo, lista, regra, se
from .lutador import CondicaoFisica, Estilo, Lutador
from .regras import Acao, Distancia, EstadoCombate, acao_obrigatoria, acoes_legais, resolver

A = Acao
PERTO, MEDIO, LONGE = Distancia.PERTO, Distancia.MEDIO, Distancia.LONGE


def _dist(d: Distancia) -> C:
    return C("distancia_eh", (d,))


GAMBITS = {
    # ε = 1: so a regra final para a lista ser valida; nunca e usada
    "aleatorio": lista([], A.DEFENDER),

    # avanca e ataca; prefere o pesado quando tem guts
    "agressivo": lista([
        regra(_dist(LONGE), A.AVANCAR),
        regra(_dist(MEDIO), A.AVANCAR),
        regra(C("guts_proprio_acima", (40,)), A.PREPARAR_PESADO),
        regra(C("sempre"), A.GOLPE_RAPIDO),
    ], A.CARREGAR),

    # defende e carrega; ataca so quando o oponente esta sem guts
    "tartaruga": lista([
        regra(C("oponente_guts_abaixo", (20,)), A.PREPARAR_PESADO),
        regra(C("oponente_guts_abaixo", (20,)), A.GOLPE_RAPIDO),
        regra(C("oponente_guts_abaixo", (20,)), A.DISPARO),
        regra(C("oponente_preparando"), A.DEFENDER),
        regra(C("guts_proprio_abaixo", (40,)), A.CARREGAR),
    ], A.DEFENDER),

    # mantem medio/longe e dispara; recua quando o oponente avanca
    "atirador": lista([
        regra(se(C("oponente_preparando"), _dist(PERTO)), A.ESQUIVAR),
        regra(_dist(PERTO), A.RECUAR),
        regra(se(C("oponente_repete", (A.AVANCAR, 2)), _dist(MEDIO)), A.RECUAR),
        regra(C("sempre"), A.DISPARO),
    ], A.CARREGAR),

    # esquiva quando o oponente prepara; pune quando ele fica sem guts
    "contragolpe": lista([
        regra(C("oponente_preparando"), A.ESQUIVAR),
        regra(C("oponente_preparando"), A.DEFENDER),
        regra(C("oponente_guts_abaixo", (20,)), A.PREPARAR_PESADO),
        regra(C("oponente_guts_abaixo", (20,)), A.GOLPE_RAPIDO),
        regra(_dist(LONGE), A.AVANCAR),
        regra(C("guts_proprio_abaixo", (40,)), A.CARREGAR),
        regra(_dist(MEDIO), A.AVANCAR),
    ], A.DEFENDER),

    # responde ao padrao do oponente na partida
    "adaptativo": lista([
        regra(C("oponente_preparando"), A.ESQUIVAR),
        regra(C("oponente_repete", (A.DEFENDER, 2)), A.PREPARAR_PESADO),
        regra(C("oponente_frequente", (A.PREPARAR_PESADO,)), A.GOLPE_RAPIDO),
        regra(C("oponente_frequente", (A.CARREGAR,)), A.GOLPE_RAPIDO),
        regra(C("oponente_frequente", (A.DISPARO,)), A.AVANCAR),
        regra(C("oponente_frequente", (A.GOLPE_RAPIDO,)), A.DEFENDER),
        regra(se(_dist(PERTO), C("guts_proprio_acima", (40,))), A.GOLPE_RAPIDO),
        regra(C("guts_proprio_acima", (20,)), A.AVANCAR),
    ], A.CARREGAR),
}

FIXOS = ("aleatorio", "agressivo", "tartaruga", "atirador", "contragolpe")
ADAPTATIVO = "adaptativo"
ORACULO = "oraculo"
TODOS = FIXOS + (ADAPTATIVO, ORACULO)


@dataclass(frozen=True)
class EstiloOraculo:
    """REFERENCIA FORA DA LINGUAGEM DE GAMBITS. Melhor resposta de 1 passo.

    Distribuicao do oponente = frequencia empirica das acoes dele na partida,
    restrita as legais agora (sem historico ou sem nenhuma legal: uniforme
    sobre as legais). Valor de um estado = diferenca de fracao de hp +
    peso_guts x diferenca de guts + valor do pesado pendente (config).
    Empate entre acoes: a primeira na ordem fixa de ACOES_ESCOLHIVEIS.
    """

    epsilon: float
    fora_da_linguagem: bool = True

    def decidir(self, estado: EstadoCombate, lado: int, rng: random.Random, cfg: ConfigCombateV2) -> tuple[Acao, Motivo]:
        obrig = acao_obrigatoria(estado, lado)
        if obrig is not None:
            return obrig, PESADO_AUTOMATICO
        minhas = acoes_legais(estado, lado, cfg)
        if self.epsilon > 0.0 and rng.random() < self.epsilon:
            return minhas[rng.randrange(len(minhas))], EXPLORACAO
        op = 1 - lado
        forcada = acao_obrigatoria(estado, op)
        if forcada is not None:
            dist = {forcada: 1.0}
        else:
            legais_op = acoes_legais(estado, op, cfg)
            cont = {x: 0 for x in legais_op}
            for x in estado.proprio(op).historico:
                if x in cont:
                    cont[x] += 1
            total = sum(cont.values())
            dist = ({x: c / total for x, c in cont.items() if c} if total
                    else {x: 1.0 / len(legais_op) for x in legais_op})
        melhor, melhor_v = None, None
        for a in minhas:
            v = 0.0
            for b, p in dist.items():
                par = (a, b) if lado == 0 else (b, a)
                novo, _ = resolver(estado, par[0], par[1], cfg)
                v += p * self._valor(novo, lado, cfg)
            if melhor_v is None or v > melhor_v:
                melhor, melhor_v = a, v
        return melhor, "oraculo"

    @staticmethod
    def _valor(estado: EstadoCombate, lado: int, cfg: ConfigCombateV2) -> float:
        eu, op = estado.proprio(lado), estado.oponente(lado)
        v = (eu.fracao_hp - op.fracao_hp) + cfg.peso_guts_oraculo * (eu.guts - op.guts)
        if estado.distancia is Distancia.PERTO:
            pend = cfg.peso_pesado_pendente_oraculo * cfg.dano_pesado
            if eu.preparando:
                v += pend / op.hp_max
            if op.preparando:
                v -= pend / eu.hp_max
        return v

    def para_dict(self) -> dict:
        return {"tipo": "oraculo_1_passo", "fora_da_linguagem": True, "epsilon": self.epsilon}


def estilo(nome: str, cfg: ConfigCombateV2 | None = None) -> Estilo | EstiloOraculo:
    cfg = cfg or CONFIG_COMBATE_V2
    if nome == ORACULO:
        return EstiloOraculo(cfg.epsilon_bots)
    if nome not in GAMBITS:
        raise KeyError(f"bot desconhecido: {nome!r}")
    return Estilo(GAMBITS[nome], 1.0 if nome == "aleatorio" else cfg.epsilon_bots)


def bot(nome: str, condicao: CondicaoFisica | None = None, cfg: ConfigCombateV2 | None = None) -> Lutador:
    cfg = cfg or CONFIG_COMBATE_V2
    return Lutador(nome, condicao or CondicaoFisica.neutra(cfg), estilo(nome, cfg))


def permutar(gambits_nome: str, semente: int, n: int) -> list:
    """n permutacoes distintas da ordem das regras (a final fica no fim)."""
    base = GAMBITS[gambits_nome]
    rng = random.Random(semente)
    vistas, saida = {tuple(range(len(base.regras)))}, []
    tentativas = 0
    while len(saida) < n:
        tentativas += 1
        if tentativas > 10_000:
            raise RuntimeError("nao achei permutacoes distintas suficientes")
        ordem = list(range(len(base.regras)))
        rng.shuffle(ordem)
        if tuple(ordem) in vistas:
            continue
        vistas.add(tuple(ordem))
        saida.append((tuple(ordem), lista([base.regras[i] for i in ordem], base.final.acao)))
    return saida


__all__ = ["GAMBITS", "FIXOS", "ADAPTATIVO", "ORACULO", "TODOS", "EstiloOraculo", "estilo", "bot", "permutar"]
