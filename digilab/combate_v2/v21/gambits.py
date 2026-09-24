"""Gambits V2.1: a evolucao muda a cabeca.

| estagio     | regras | condicoes                                                        |
|-------------|--------|------------------------------------------------------------------|
| crianca     | 3      | sempre, distancia_eh, hp_proprio_abaixo, guts_proprio_abaixo/acima |
| adolescente | 5      | + oponente_preparando, oponente_hp_abaixo, oponente_guts_abaixo  |
| adulto      | 8      | + oponente_repete, oponente_frequente, turno_execucao            |
| vigia       | 8      | + oponente_vai_preparar (passiva)                                |

`turno_execucao(t)`: o turno corrente da partida e >= t (interpretacao: a
especificacao so da o nome; registrado em docs/REGISTRO_DESVIOS.md).
`oponente_vai_preparar`: a regra do oponente que dispararia agora (sem a
exploracao epsilon, sem rng) e preparar_pesado. So o vigia enxerga.

Decisao igual a V2: pesado automatico; epsilon -> acao legal uniforme; senao a
primeira regra cujas condicoes valem E cuja acao e legal.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Union

from ...config import CONFIG_COMBATE_V2, CONFIG_COMBATE_V21
from .regras import ACOES_ESCOLHIVEIS, REGRAS_PADRAO, TECNICAS, Acao, Distancia, EstadoCombate, Regras, \
    acao_obrigatoria, acoes_legais, eh_legal

Motivo = Union[int, str]
EXPLORACAO = "exploracao"
PESADO_AUTOMATICO = "pesado_automatico"

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
    "turno_execucao": ("t",),
    "oponente_vai_preparar": (),
}

CONDICOES_POR_ESTAGIO = {
    "crianca": ("sempre", "distancia_eh", "hp_proprio_abaixo", "guts_proprio_abaixo", "guts_proprio_acima"),
}
CONDICOES_POR_ESTAGIO["adolescente"] = CONDICOES_POR_ESTAGIO["crianca"] + (
    "oponente_preparando", "oponente_hp_abaixo", "oponente_guts_abaixo")
CONDICOES_POR_ESTAGIO["adulto"] = CONDICOES_POR_ESTAGIO["adolescente"] + (
    "oponente_repete", "oponente_frequente", "turno_execucao")
CONDICAO_DO_VIGIA = "oponente_vai_preparar"


def max_regras(estagio: str) -> int:
    v = CONFIG_COMBATE_V21
    return {"crianca": v.max_regras_crianca, "adolescente": v.max_regras_adolescente,
            "adulto": v.max_regras_adulto}[estagio]


class GambitInvalido(ValueError):
    pass


def _dominio(tipo: str) -> tuple:
    b = CONFIG_COMBATE_V2
    return {"d": tuple(Distancia), "f": b.fracoes_hp, "g": b.limiares_guts, "a": tuple(Acao),
            "k": b.k_repete, "t": CONFIG_COMBATE_V21.turnos_execucao}[tipo]


@dataclass(frozen=True)
class Contexto:
    """O que so algumas passivas enxergam. Vazio para quase todos."""

    intencao_oponente: Acao | None = None


CONTEXTO_VAZIO = Contexto()


@dataclass(frozen=True)
class Condicao:
    nome: str
    params: tuple = ()

    def validar(self) -> None:
        if self.nome not in CATALOGO:
            raise GambitInvalido(f"condicao fora do catalogo: {self.nome!r}")
        tipos = CATALOGO[self.nome]
        if len(self.params) != len(tipos):
            raise GambitInvalido(f"{self.nome}: espera {len(tipos)} parametro(s), veio {self.params!r}")
        for tipo, valor in zip(tipos, self.params):
            if valor not in _dominio(tipo):
                raise GambitInvalido(f"{self.nome}: parametro {valor!r} fora de {_dominio(tipo)}")

    def vale(self, estado: EstadoCombate, lado: int, ctx: Contexto) -> bool:
        b = CONFIG_COMBATE_V2
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
        if n == "oponente_hp_abaixo":
            return op.fracao_hp < p[0]
        if n == "oponente_guts_abaixo":
            return op.guts < p[0]
        if n == "oponente_repete":
            acao, k = p
            ult = op.historico[-k:]
            return len(ult) == k and all(a is acao for a in ult)
        if n == "oponente_frequente":
            ult = op.historico[-b.janela_frequente:]
            return sum(a is p[0] for a in ult) / b.janela_frequente >= b.limiar_frequente
        if n == "turno_execucao":
            return estado.turno >= p[0]
        if n == "oponente_vai_preparar":
            return ctx.intencao_oponente is Acao.PREPARAR_PESADO
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

    def validar(self) -> None:
        if not 1 <= len(self.condicoes) <= CONFIG_COMBATE_V2.max_condicoes_por_regra:
            raise GambitInvalido(f"regra com {len(self.condicoes)} condicoes")
        if self.acao not in ACOES_ESCOLHIVEIS:
            raise GambitInvalido(f"acao nao escolhivel numa regra: {self.acao!r}")
        for c in self.condicoes:
            c.validar()

    def para_dict(self) -> dict:
        return {"se": [c.para_dict() for c in self.condicoes], "entao": self.acao.value}


REGRA_FINAL_VALIDA = (Acao.DEFENDER, Acao.CARREGAR)


@dataclass(frozen=True)
class ListaGambits:
    """Lista para um estagio. A tecnica/passiva do lutador e checada em Lutador."""

    regras: tuple[Regra, ...]
    final: Regra
    estagio: str

    def __post_init__(self) -> None:
        if self.estagio not in CONDICOES_POR_ESTAGIO:
            raise GambitInvalido(f"estagio sem gambits: {self.estagio!r} (bebe nao luta)")
        if len(self.regras) > max_regras(self.estagio):
            raise GambitInvalido(f"{len(self.regras)} regras; {self.estagio} aceita ate {max_regras(self.estagio)}")
        for r in self.regras + (self.final,):
            r.validar()
            for c in r.condicoes:
                if c.nome not in CONDICOES_POR_ESTAGIO[self.estagio] and c.nome != CONDICAO_DO_VIGIA:
                    raise GambitInvalido(f"condicao {c.nome!r} nao existe no estagio {self.estagio}")
            if r.acao in TECNICAS.values() and self.estagio == "crianca":
                raise GambitInvalido("crianca nao tem tecnica")
        if self.final.condicoes != (Condicao("sempre"),) or self.final.acao not in REGRA_FINAL_VALIDA:
            raise GambitInvalido("regra final precisa ser 'sempre -> defender' ou 'sempre -> carregar'")

    def usa_condicao(self, nome: str) -> bool:
        return any(c.nome == nome for r in self.regras for c in r.condicoes)

    def acoes(self) -> set:
        return {r.acao for r in self.regras} | {self.final.acao}

    def primeira_regra(self, estado: EstadoCombate, lado: int, ctx: Contexto,
                       r: Regras = REGRAS_PADRAO) -> tuple[Acao, int]:
        for i, rg in enumerate(self.regras):
            if all(c.vale(estado, lado, ctx) for c in rg.condicoes) and eh_legal(estado, lado, rg.acao, r):
                return rg.acao, i
        if eh_legal(estado, lado, self.final.acao, r):
            return self.final.acao, len(self.regras)
        # furioso nao pode defender: a final 'defender' cai para carregar (sempre legal)
        return Acao.CARREGAR, len(self.regras)

    def para_dict(self) -> dict:
        return {"estagio": self.estagio, "regras": [r.para_dict() for r in self.regras],
                "final": self.final.para_dict()}


def se(*condicoes: Condicao) -> tuple[Condicao, ...]:
    return tuple(condicoes)


def regra(condicoes, acao: Acao) -> Regra:
    if isinstance(condicoes, Condicao):
        condicoes = (condicoes,)
    return Regra(tuple(condicoes), acao)


def lista(regras: list[Regra], final: Acao, estagio: str = "adulto") -> ListaGambits:
    return ListaGambits(tuple(regras), Regra((Condicao("sempre"),), final), estagio)


def decidir_gambits(gambits: ListaGambits, epsilon: float, estado: EstadoCombate, lado: int,
                    rng: random.Random, ctx: Contexto = CONTEXTO_VAZIO,
                    r: Regras = REGRAS_PADRAO) -> tuple[Acao, Motivo]:
    obrig = acao_obrigatoria(estado, lado)
    if obrig is not None:
        return obrig, PESADO_AUTOMATICO
    if epsilon > 0.0 and rng.random() < epsilon:
        legais = acoes_legais(estado, lado, r)
        return legais[rng.randrange(len(legais))], EXPLORACAO
    return gambits.primeira_regra(estado, lado, ctx, r)
