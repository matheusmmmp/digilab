"""Linguagem de gambits (FF XII): lista priorizada de regras condicao -> acao.

Catalogo FECHADO de condicoes, com parametros em conjuntos discretos (o
aprendizado futuro precisa de espaco finito). Parametro fora do conjunto ou
condicao desconhecida levanta erro na construcao.

Decisao:
  1. quem esta preparando nao escolhe: executa o pesado (motivo
     "pesado_automatico", nao consome rng);
  2. com probabilidade epsilon, acao legal uniforme (motivo "exploracao");
  3. senao, a primeira regra cujas condicoes valem E cuja acao e legal
     (motivo = indice da regra; a regra final e a de indice len(regras)).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Union

from ..config import CONFIG_COMBATE_V2, ConfigCombateV2
from .regras import ACOES_ESCOLHIVEIS, Acao, Distancia, EstadoCombate, acao_obrigatoria, acoes_legais, eh_legal

Motivo = Union[int, str]
EXPLORACAO = "exploracao"
PESADO_AUTOMATICO = "pesado_automatico"

# nome -> tipos dos parametros ("d" distancia, "f" fracao de hp, "g" guts,
# "a" acao, "k" repeticoes)
CATALOGO: dict[str, tuple[str, ...]] = {
    "sempre": (),
    "distancia_eh": ("d",),
    "hp_proprio_abaixo": ("f",),
    "guts_proprio_abaixo": ("g",),
    "guts_proprio_acima": ("g",),
    "oponente_preparando": (),
    "oponente_hp_abaixo": ("f",),
    "oponente_guts_abaixo": ("g",),
    "oponente_repete": ("a", "k"),
    "oponente_frequente": ("a",),
    # V2C (C1): o proprio lado esta no turno de execucao do pesado (escolhe executar ou fintar).
    # "turno_execucao" ja existe na V2.1 com outro sentido (turno da luta >= N): nome diferente.
    "executando_pesado": (),
}

# acoes que podem aparecer no historico (inclui o pesado executado)
ACOES_OBSERVAVEIS = tuple(Acao)


class GambitInvalido(ValueError):
    pass


def _dominio(tipo: str, cfg: ConfigCombateV2) -> tuple:
    return {
        "d": tuple(Distancia),
        "f": cfg.fracoes_hp,
        "g": cfg.limiares_guts,
        "a": ACOES_OBSERVAVEIS,
        "k": cfg.k_repete,
    }[tipo]


@dataclass(frozen=True)
class Condicao:
    nome: str
    params: tuple = ()

    def validar(self, cfg: ConfigCombateV2) -> None:
        if self.nome not in CATALOGO:
            raise GambitInvalido(f"condicao fora do catalogo: {self.nome!r}")
        tipos = CATALOGO[self.nome]
        if len(self.params) != len(tipos):
            raise GambitInvalido(f"{self.nome}: espera {len(tipos)} parametro(s), veio {self.params!r}")
        for tipo, valor in zip(tipos, self.params):
            if valor not in _dominio(tipo, cfg):
                raise GambitInvalido(f"{self.nome}: parametro {valor!r} fora de {_dominio(tipo, cfg)}")

    def vale(self, estado: EstadoCombate, lado: int, cfg: ConfigCombateV2) -> bool:
        eu, op = estado.proprio(lado), estado.oponente(lado)
        n, p = self.nome, self.params
        if n == "sempre":
            return True
        if n == "distancia_eh":
            return estado.distancia is p[0]
        if n == "hp_proprio_abaixo":
            return eu.fracao_hp < p[0]
        if n == "guts_proprio_abaixo":
            return eu.guts < p[0]
        if n == "guts_proprio_acima":
            return eu.guts >= p[0]
        if n == "oponente_preparando":
            return op.preparando
        if n == "executando_pesado":
            return eu.preparando
        if n == "oponente_hp_abaixo":
            return op.fracao_hp < p[0]
        if n == "oponente_guts_abaixo":
            return op.guts < p[0]
        if n == "oponente_repete":
            acao, k = p
            ult = op.historico[-k:]
            return len(ult) == k and all(a is acao for a in ult)
        if n == "oponente_frequente":
            # fracao sobre uma janela FIXA de 5: acoes que ainda nao existem
            # contam como "nao e essa acao"
            ult = op.historico[-cfg.janela_frequente:]
            return sum(a is p[0] for a in ult) / cfg.janela_frequente >= cfg.limiar_frequente
        raise GambitInvalido(f"condicao sem avaliador: {n!r}")

    def para_dict(self) -> dict:
        def serial(x):
            if isinstance(x, Distancia):
                return x.rotulo
            if isinstance(x, Acao):
                return x.value
            return x

        return {"nome": self.nome, "params": [serial(x) for x in self.params]}


@dataclass(frozen=True)
class Regra:
    condicoes: tuple[Condicao, ...]
    acao: Acao

    def validar(self, cfg: ConfigCombateV2) -> None:
        if not 1 <= len(self.condicoes) <= cfg.max_condicoes_por_regra:
            raise GambitInvalido(f"regra com {len(self.condicoes)} condicoes (1..{cfg.max_condicoes_por_regra})")
        if self.acao is Acao.FINTAR:
            if Condicao("executando_pesado") not in self.condicoes:
                raise GambitInvalido("regra de fintar precisa da condicao executando_pesado")
        elif self.acao not in ACOES_ESCOLHIVEIS:
            raise GambitInvalido(f"acao nao escolhivel numa regra: {self.acao!r}")
        for c in self.condicoes:
            c.validar(cfg)

    def dispara(self, estado: EstadoCombate, lado: int, cfg: ConfigCombateV2) -> bool:
        return all(c.vale(estado, lado, cfg) for c in self.condicoes) and eh_legal(estado, lado, self.acao, cfg)

    def para_dict(self) -> dict:
        return {"se": [c.para_dict() for c in self.condicoes], "entao": self.acao.value}


REGRA_FINAL_VALIDA = (Acao.DEFENDER, Acao.CARREGAR)


@dataclass(frozen=True)
class ListaGambits:
    regras: tuple[Regra, ...]
    final: Regra

    def __post_init__(self) -> None:
        self.validar(CONFIG_COMBATE_V2)

    def validar(self, cfg: ConfigCombateV2) -> None:
        if len(self.regras) > cfg.max_regras:
            raise GambitInvalido(f"{len(self.regras)} regras; maximo {cfg.max_regras} + a final")
        for r in self.regras:
            r.validar(cfg)
        if not isinstance(self.final, Regra):
            raise GambitInvalido("lista sem regra final")
        if self.final.condicoes != (Condicao("sempre"),) or self.final.acao not in REGRA_FINAL_VALIDA:
            raise GambitInvalido("regra final precisa ser 'sempre -> defender' ou 'sempre -> carregar'")

    def primeira_regra(self, estado: EstadoCombate, lado: int, cfg: ConfigCombateV2) -> tuple[Acao, int]:
        for i, r in enumerate(self.regras):
            if r.dispara(estado, lado, cfg):
                return r.acao, i
        if not eh_legal(estado, lado, self.final.acao, cfg):
            raise GambitInvalido("regra final ilegal (nao deveria acontecer)")
        return self.final.acao, len(self.regras)

    def para_dict(self) -> dict:
        return {"regras": [r.para_dict() for r in self.regras], "final": self.final.para_dict()}


def se(*condicoes: Condicao) -> tuple[Condicao, ...]:
    return tuple(condicoes)


def regra(condicoes: tuple[Condicao, ...] | Condicao, acao: Acao) -> Regra:
    if isinstance(condicoes, Condicao):
        condicoes = (condicoes,)
    return Regra(tuple(condicoes), acao)


def lista(regras: list[Regra], final: Acao) -> ListaGambits:
    return ListaGambits(tuple(regras), Regra((Condicao("sempre"),), final))


def decidir_gambits(
    gambits: ListaGambits, epsilon: float, estado: EstadoCombate, lado: int, rng: random.Random,
    cfg: ConfigCombateV2 | None = None,
) -> tuple[Acao, Motivo]:
    cfg = cfg or CONFIG_COMBATE_V2
    obrig = acao_obrigatoria(estado, lado)
    if obrig is not None:
        # C1: com finta, a primeira regra de fintar que vale troca o pesado (sem exploracao)
        if eh_legal(estado, lado, Acao.FINTAR, cfg):
            for i, r in enumerate(gambits.regras):
                if r.acao is Acao.FINTAR and r.dispara(estado, lado, cfg):
                    return Acao.FINTAR, i
        return obrig, PESADO_AUTOMATICO
    if epsilon > 0.0 and rng.random() < epsilon:
        legais = acoes_legais(estado, lado, cfg)
        return legais[rng.randrange(len(legais))], EXPLORACAO
    return gambits.primeira_regra(estado, lado, cfg)
