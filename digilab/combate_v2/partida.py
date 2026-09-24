"""Laco de uma partida V2, log e replay.

Cada lado tem rng de combate propria, derivada da semente da partida e da
posicao (0/1); nao compartilha estado com rng de ambiente nem de politica de
vida. A resolucao nao consome rng: so as decisoes (epsilon) consomem.

Log = lista de eventos JSON: "cabecalho", um "turno" por turno (escolhas
reveladas + motivos) e "fim". Evento desconhecido no replay levanta erro.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass

from ..config import CONFIG_COMBATE_V2, ConfigCombateV2
from ..protocol import derivar_semente
from .lutador import Lutador
from .regras import Acao, EstadoCombate, estado_inicial, resolver, resultado


class ReplayCombateDivergiu(RuntimeError):
    pass


def sementes_de_rng(semente: int) -> tuple[int, int]:
    return derivar_semente("combate-v2", semente, 0), derivar_semente("combate-v2", semente, 1)


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


def _motivo_json(m):
    return m if isinstance(m, str) else int(m)


def jogar(
    a: Lutador, b: Lutador, semente: int, cfg: ConfigCombateV2 | None = None,
    sementes_rng: tuple[int, int] | None = None,
) -> Partida:
    cfg = cfg or CONFIG_COMBATE_V2
    sa, sb = sementes_rng if sementes_rng is not None else sementes_de_rng(semente)
    rngs = (random.Random(sa), random.Random(sb))
    lutadores = (a, b)
    estado = estado_inicial(
        (a.condicao.hp_max, b.condicao.hp_max),
        (a.condicao.guts_inicial, b.condicao.guts_inicial),
        (a.condicao.regen_guts, b.condicao.regen_guts),
    )
    log: list[dict] = [{
        "tipo": "cabecalho", "semente": semente, "sementes_rng": [sa, sb],
        "a": a.nome, "b": b.nome, "hash_a": a.hash(), "hash_b": b.hash(),
    }]
    while (fim := resultado(estado, cfg)) is None:
        escolhas = [lutadores[i].estilo.decidir(estado, i, rngs[i], cfg) for i in (0, 1)]
        estado, _ = resolver(estado, escolhas[0][0], escolhas[1][0], cfg)
        log.append({
            "tipo": "turno", "t": estado.turno,
            "a": escolhas[0][0].value, "ma": _motivo_json(escolhas[0][1]),
            "b": escolhas[1][0].value, "mb": _motivo_json(escolhas[1][1]),
        })
    pontos, motivo = fim
    log.append({
        "tipo": "fim", "pontos_a": pontos, "motivo": motivo, "turnos": estado.turno,
        "hp_a": estado.lados[0].hp, "hp_b": estado.lados[1].hp,
    })
    return Partida(semente, a.nome, b.nome, pontos, motivo, estado.turno, estado, tuple(log))


def reproduzir(log: list[dict], a: Lutador, b: Lutador, cfg: ConfigCombateV2 | None = None) -> Partida:
    """Rejoga a partida do log (decisoes E resolucao) e confere cada turno bit a bit."""
    cfg = cfg or CONFIG_COMBATE_V2
    if not log or log[0].get("tipo") != "cabecalho":
        raise ReplayCombateDivergiu("log sem cabecalho")
    for ev in log:
        if ev.get("tipo") not in ("cabecalho", "turno", "fim"):
            raise ValueError(f"evento desconhecido no log de combate: {ev.get('tipo')!r}")
    cab = log[0]
    if (cab["a"], cab["b"], cab["hash_a"], cab["hash_b"]) != (a.nome, b.nome, a.hash(), b.hash()):
        raise ReplayCombateDivergiu("lutadores do replay nao sao os do log")
    p = jogar(a, b, cab["semente"], cfg, sementes_rng=tuple(cab["sementes_rng"]))
    gravado = [json.loads(json.dumps(e, sort_keys=True)) for e in log]
    refeito = [json.loads(json.dumps(e, sort_keys=True)) for e in p.log]
    if gravado != refeito:
        for i, (x, y) in enumerate(zip(gravado, refeito)):
            if x != y:
                raise ReplayCombateDivergiu(f"evento {i} diverge: gravado {x} x replay {y}")
        raise ReplayCombateDivergiu(f"numero de eventos diverge: {len(gravado)} x {len(refeito)}")
    return p


def reproduzir_acoes(log: list[dict], cfg: ConfigCombateV2 | None = None, condicoes=None) -> EstadoCombate:
    """Replay so da resolucao, a partir das acoes reveladas (sem decisores).

    `condicoes` = (CondicaoFisica_a, CondicaoFisica_b); padrao = neutra.
    """
    from .lutador import CondicaoFisica

    cfg = cfg or CONFIG_COMBATE_V2
    ca, cb = condicoes or (CondicaoFisica.neutra(cfg), CondicaoFisica.neutra(cfg))
    estado = estado_inicial((ca.hp_max, cb.hp_max), (ca.guts_inicial, cb.guts_inicial), (ca.regen_guts, cb.regen_guts))
    for ev in log:
        tipo = ev.get("tipo")
        if tipo == "turno":
            estado, _ = resolver(estado, Acao(ev["a"]), Acao(ev["b"]), cfg)
        elif tipo not in ("cabecalho", "fim"):
            raise ValueError(f"evento desconhecido no log de combate: {tipo!r}")
    return estado
