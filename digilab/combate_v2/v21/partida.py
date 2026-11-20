"""Lutador V2.1 (perfil + gambits) e laco de partida, log e replay.

Igual a V2: rng de combate propria por lado, derivada da semente da partida
(rotulo "combate-v21"); a resolucao nao consome rng. Log = cabecalho, turnos
(acoes reveladas + motivos), fim; evento desconhecido levanta erro.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

from ...protocol import derivar_semente
from .catalogo import Perfil
from .gambits import CONDICAO_DO_VIGIA, CONTEXTO_VAZIO, Contexto, GambitInvalido, ListaGambits, decidir_gambits
from .regras import REGRAS_PADRAO, TECNICAS, Acao, EstadoCombate, Regras, estado_inicial, resolver, resultado


class ReplayCombateDivergiu(RuntimeError):
    pass


@dataclass(frozen=True)
class Lutador:
    nome: str
    perfil: Perfil
    gambits: ListaGambits
    epsilon: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.epsilon <= 1.0:
            raise ValueError(f"epsilon fora de [0, 1]: {self.epsilon}")
        if self.gambits.estagio != self.perfil.estagio:
            raise GambitInvalido(f"{self.nome}: gambits de {self.gambits.estagio} num {self.perfil.estagio}")
        propria = TECNICAS.get(self.perfil.tecnica or "")
        for a in self.gambits.acoes():
            if a in TECNICAS.values() and a is not propria:
                raise GambitInvalido(f"{self.nome}: tecnica {a.value} nao e da linha ({self.perfil.tecnica})")
        if self.gambits.usa_condicao(CONDICAO_DO_VIGIA) and self.perfil.passiva != "vigia":
            raise GambitInvalido(f"{self.nome}: {CONDICAO_DO_VIGIA} so existe para o vigia")

    def intencao(self, estado: EstadoCombate, lado: int, r: Regras) -> Acao | None:
        """A regra que dispararia agora, sem exploracao e sem rng (o que o vigia ve)."""
        if estado.proprio(lado).preparando:
            return None
        return self.gambits.primeira_regra(estado, lado, CONTEXTO_VAZIO, r)[0]

    def decidir(self, estado: EstadoCombate, lado: int, rng: random.Random, oponente: "Lutador", r: Regras):
        ctx = CONTEXTO_VAZIO
        if self.perfil.passiva == "vigia":
            ctx = Contexto(intencao_oponente=oponente.intencao(estado, 1 - lado, r))
        return decidir_gambits(self.gambits, self.epsilon, estado, lado, rng, ctx, r)

    def para_dict(self) -> dict:
        return {"nome": self.nome, "perfil": self.perfil.para_dict(), "epsilon": self.epsilon,
                "gambits": self.gambits.para_dict()}

    def hash(self) -> str:
        return hashlib.sha256(json.dumps(self.para_dict(), sort_keys=True).encode("utf-8")).hexdigest()


def sementes_de_rng(semente: int) -> tuple[int, int]:
    return derivar_semente("combate-v21", semente, 0), derivar_semente("combate-v21", semente, 1)


@dataclass(frozen=True)
class Partida:
    semente: int
    nome_a: str
    nome_b: str
    pontos_a: float
    motivo_fim: str
    turnos: int
    estado_final: EstadoCombate
    log: tuple[dict, ...]

    def para_jsonl(self) -> str:
        return "".join(json.dumps(e, sort_keys=True) + "\n" for e in self.log)


def _mj(m):
    return m if isinstance(m, str) else int(m)


def jogar(a: Lutador, b: Lutador, semente: int, r: Regras = REGRAS_PADRAO,
          sementes_rng: tuple[int, int] | None = None) -> Partida:
    sa, sb = sementes_rng if sementes_rng is not None else sementes_de_rng(semente)
    rngs = (random.Random(sa), random.Random(sb))
    lut = (a, b)
    estado = estado_inicial(a.perfil, b.perfil)
    log: list[dict] = [{"tipo": "cabecalho", "versao": "v21", "semente": semente, "sementes_rng": [sa, sb],
                        "a": a.nome, "b": b.nome, "hash_a": a.hash(), "hash_b": b.hash()}]
    while (fim := resultado(estado, r)) is None:
        esc = [lut[i].decidir(estado, i, rngs[i], lut[1 - i], r) for i in (0, 1)]
        estado, _ = resolver(estado, esc[0][0], esc[1][0], r)
        log.append({"tipo": "turno", "t": estado.turno, "a": esc[0][0].value, "ma": _mj(esc[0][1]),
                    "b": esc[1][0].value, "mb": _mj(esc[1][1])})
    pontos, motivo = fim
    log.append({"tipo": "fim", "pontos_a": pontos, "motivo": motivo, "turnos": estado.turno,
                "hp_a": estado.lados[0].hp, "hp_b": estado.lados[1].hp})
    return Partida(semente, a.nome, b.nome, pontos, motivo, estado.turno, estado, tuple(log))


def reproduzir(log: list[dict], a: Lutador, b: Lutador, r: Regras = REGRAS_PADRAO) -> Partida:
    if not log or log[0].get("tipo") != "cabecalho":
        raise ReplayCombateDivergiu("log sem cabecalho")
    for ev in log:
        if ev.get("tipo") not in ("cabecalho", "turno", "fim"):
            raise ValueError(f"evento desconhecido no log de combate: {ev.get('tipo')!r}")
    cab = log[0]
    if (cab["a"], cab["b"], cab["hash_a"], cab["hash_b"]) != (a.nome, b.nome, a.hash(), b.hash()):
        raise ReplayCombateDivergiu("lutadores do replay nao sao os do log")
    p = jogar(a, b, cab["semente"], r, sementes_rng=tuple(cab["sementes_rng"]))
    gravado = [json.loads(json.dumps(e, sort_keys=True)) for e in log]
    refeito = [json.loads(json.dumps(e, sort_keys=True)) for e in p.log]
    if gravado != refeito:
        for i, (x, y) in enumerate(zip(gravado, refeito)):
            if x != y:
                raise ReplayCombateDivergiu(f"evento {i} diverge: gravado {x} x replay {y}")
        raise ReplayCombateDivergiu(f"numero de eventos diverge: {len(gravado)} x {len(refeito)}")
    return p
