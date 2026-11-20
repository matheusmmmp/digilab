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
from .regras import Acao, Distancia, EstadoCombate, acao_obrigatoria, acoes_legais, resolver, resultado

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

# V2C (C1): o agressivo (4 regras) ganha a regra de fintar contra quem costuma esquivar (so vale com
# finta). O adaptativo ja usa as 8 regras do limite: ficaria sem uma delas; fica como esta.
FINTA = regra(se(C("executando_pesado"), C("oponente_frequente", (A.ESQUIVAR,))), A.FINTAR)
GAMBITS_FINTA = {n: lista([FINTA] + list(GAMBITS[n].regras), GAMBITS[n].final.acao) for n in ("agressivo",)}

# V2C, redesenho dos bots (a V2C com os bots antigos reprovou: pares passivos que nunca se atacam, suporte
# sem esquiva, espelho do atirador deterministico). So valem com ConfigCombateV2C.bots_v2c.
_FREQ = lambda a: C("oponente_frequente", (a,))  # noqa: E731
GAMBITS_V2C = {
    "aleatorio": GAMBITS["aleatorio"],
    "agressivo": lista([
        FINTA,
        regra(se(C("hp_proprio_abaixo", (0.5,)), _FREQ(A.GOLPE_RAPIDO)), A.DEFENDER),
        regra(_dist(LONGE), A.AVANCAR),
        regra(_dist(MEDIO), A.AVANCAR),
        regra(C("oponente_preparando"), A.GOLPE_RAPIDO),
        regra(se(_FREQ(A.DEFENDER), C("guts_proprio_acima", (40,))), A.PREPARAR_PESADO),
        regra(C("guts_proprio_acima", (20,)), A.GOLPE_RAPIDO),
    ], A.CARREGAR),
    "tartaruga": lista([
        regra(se(C("oponente_preparando"), _FREQ(A.FINTAR)), A.DEFENDER),
        regra(C("oponente_preparando"), A.ESQUIVAR),
        regra(se(_FREQ(A.PREPARAR_PESADO), _dist(PERTO)), A.GOLPE_RAPIDO),
        regra(C("oponente_guts_abaixo", (20,)), A.PREPARAR_PESADO),
        regra(se(_FREQ(A.DEFENDER), _dist(PERTO)), A.PREPARAR_PESADO),
        regra(_FREQ(A.DEFENDER), A.AVANCAR),
        regra(se(_FREQ(A.CARREGAR), _dist(PERTO)), A.GOLPE_RAPIDO),
        regra(se(C("guts_proprio_abaixo", (40,)), _FREQ(A.DEFENDER)), A.CARREGAR),
    ], A.DEFENDER),
    "atirador": lista([
        regra(se(C("oponente_preparando"), _dist(PERTO)), A.ESQUIVAR),
        regra(se(_dist(PERTO), C("guts_proprio_acima", (40,))), A.GOLPE_RAPIDO),
        regra(_dist(PERTO), A.RECUAR),
        regra(se(C("hp_proprio_abaixo", (0.5,)), _FREQ(A.DISPARO)), A.AVANCAR),
        regra(se(_FREQ(A.DISPARO), C("guts_proprio_acima", (40,))), A.ESQUIVAR),
        regra(C("sempre"), A.DISPARO),
    ], A.CARREGAR),
    "contragolpe": lista([
        regra(C("oponente_preparando"), A.ESQUIVAR),
        regra(C("oponente_guts_abaixo", (20,)), A.PREPARAR_PESADO),
        regra(C("oponente_guts_abaixo", (20,)), A.GOLPE_RAPIDO),
        regra(se(_FREQ(A.DEFENDER), _dist(PERTO)), A.PREPARAR_PESADO),
        regra(_dist(LONGE), A.AVANCAR),
        regra(C("guts_proprio_abaixo", (40,)), A.CARREGAR),
        regra(_dist(MEDIO), A.AVANCAR),
    ], A.DEFENDER),
    "adaptativo": GAMBITS["adaptativo"],
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
        if obrig is not None and not getattr(cfg, "finta", False):
            return obrig, PESADO_AUTOMATICO
        minhas = self._minhas(estado, lado, cfg)
        if self.epsilon > 0.0 and rng.random() < self.epsilon:
            return minhas[rng.randrange(len(minhas))], EXPLORACAO
        return self._busca(estado, lado, cfg, getattr(cfg, "oraculo_passos", 1))[0], "oraculo"

    @staticmethod
    def _minhas(estado: EstadoCombate, lado: int, cfg: ConfigCombateV2) -> tuple:
        obrig = acao_obrigatoria(estado, lado)
        if obrig is None:
            return acoes_legais(estado, lado, cfg)
        return (obrig, Acao.FINTAR) if getattr(cfg, "finta", False) else (obrig,)

    @staticmethod
    def _dist_oponente(estado: EstadoCombate, op: int, cfg: ConfigCombateV2, top: int | None) -> dict:
        forcada = acao_obrigatoria(estado, op)
        if forcada is not None:
            return {forcada: 1.0}
        legais_op = acoes_legais(estado, op, cfg)
        cont = {x: 0 for x in legais_op}
        for x in estado.proprio(op).historico:
            if x in cont:
                cont[x] += 1
        total = sum(cont.values())
        dist = ({x: c / total for x, c in cont.items() if c} if total
                else {x: 1.0 / len(legais_op) for x in legais_op})
        if top is not None and len(dist) > top:
            # as `top` mais frequentes (empate: ordem fixa das acoes), renormalizadas
            ordem = sorted(dist, key=lambda x: (-dist[x], list(Acao).index(x)))[:top]
            s = sum(dist[x] for x in ordem)
            dist = {x: dist[x] / s for x in ordem}
        return dist

    def _busca(self, estado: EstadoCombate, lado: int, cfg: ConfigCombateV2, passos: int):
        """Melhor resposta de N passos (valor esperado sob a distribuicao empirica do oponente)."""
        top = getattr(cfg, "oraculo_top_oponente", 3) if passos > 1 or getattr(cfg, "oraculo_passos", 1) > 1 else None
        dist = self._dist_oponente(estado, 1 - lado, cfg, top)
        melhor, melhor_v = None, None
        for a in self._minhas(estado, lado, cfg):
            v = 0.0
            for b, p in dist.items():
                par = (a, b) if lado == 0 else (b, a)
                novo, _ = resolver(estado, par[0], par[1], cfg)
                if passos > 1 and resultado(novo, cfg) is None:
                    v += p * self._busca(novo, lado, cfg, passos - 1)[1]
                else:
                    v += p * self._valor(novo, lado, cfg)
            if melhor_v is None or v > melhor_v:
                melhor, melhor_v = a, v
        return melhor, melhor_v

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

    # (a profundidade vem da config da partida; o hash do lutador nao muda com ela)


def estilo(nome: str, cfg: ConfigCombateV2 | None = None) -> Estilo | EstiloOraculo:
    cfg = cfg or CONFIG_COMBATE_V2
    if nome == ORACULO:
        return EstiloOraculo(cfg.epsilon_bots)
    if nome not in GAMBITS:
        raise KeyError(f"bot desconhecido: {nome!r}")
    if getattr(cfg, "bots_v2c", False):
        g = GAMBITS_V2C[nome]
    else:
        g = GAMBITS_FINTA[nome] if getattr(cfg, "finta", False) and nome in GAMBITS_FINTA else GAMBITS[nome]
    return Estilo(g, 1.0 if nome == "aleatorio" else cfg.epsilon_bots)


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
