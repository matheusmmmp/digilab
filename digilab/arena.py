"""Arena (Etapa 4): combate por turnos com revelacao simultanea.

Nucleo
------
Cinco acoes de combate num torneio ciclico (pedra-papel-tesoura-lagarto-
Spock): cada acao vence exatamente duas e perde para duas. Acao igual =
nada acontece. Nao existe estrategia pura dominante; contra a mistura
uniforme, toda estrategia empata em expectativa.

Stats
-----
Derivados dos tracos por mapeamento deterministico e congelado: a
afinidade de cada acao de combate e a soma dos tracos das acoes de pet que
mapeiam nela, centrada (soma zero). Vencer um turno com a acao c causa

    dano_base * (1 + ganho_afinidade * afinidade[c])

Como as afinidades somam zero, nenhum perfil de tracos e melhor em todas
as acoes: o bonus so paga quando disposicao e tracos coincidem.

Disposicao
----------
Herdada da politica de comportamento, sem politica de combate separada:
a cada turno o lutador monta uma Observacao sintetica (necessidades fixas
de config, energia <- hp proprio, humor <- vantagem de hp) e chama
politica.agir(); a AcaoPet resultante passa pelo mapa congelado. A
politica NUNCA recebe observar() na arena: combate nao treina.

O dono nao participa.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from .config import CONFIG_ARENA, ConfigArena
from .events import AcaoPet
from .policy import Observacao, Politica
from .protocol import derivar_semente
from .tracos import ORDEM_TRACOS


class AcaoCombate(str, Enum):
    GOLPE = "golpe"
    BLOQUEIO = "bloqueio"
    AGARRAO = "agarrao"
    FINTA = "finta"
    CARGA = "carga"


ORDEM_COMBATE = tuple(AcaoCombate)
_IDX = {a: i for i, a in enumerate(ORDEM_COMBATE)}


def vence(a: AcaoCombate, b: AcaoCombate) -> bool:
    """a vence b se b esta 1 ou 3 posicoes a frente no ciclo de 5."""
    return (_IDX[b] - _IDX[a]) % 5 in (1, 3)


def mapa_pet_combate(cfg: ConfigArena) -> dict[AcaoPet, AcaoCombate]:
    mapa = {AcaoPet(p): AcaoCombate(c) for p, c in cfg.mapa_pet_combate}
    faltando = set(AcaoPet) - set(mapa)
    if faltando:
        raise ValueError(f"mapa de combate sem as acoes de pet: {sorted(a.value for a in faltando)}")
    inalcancaveis = set(AcaoCombate) - set(mapa.values())
    if inalcancaveis:
        raise ValueError(f"acoes de combate inalcancaveis: {sorted(a.value for a in inalcancaveis)}")
    if len(cfg.mapa_pet_combate) != len(mapa):
        raise ValueError("mapa de combate com acao de pet duplicada")
    return mapa


@dataclass(frozen=True)
class Stats:
    afinidade: tuple[float, ...]  # na ordem de ORDEM_COMBATE, soma zero

    def multiplicador(self, acao: AcaoCombate, cfg: ConfigArena) -> float:
        m = 1.0 + cfg.ganho_afinidade * self.afinidade[_IDX[acao]]
        if m <= 0.0:
            raise ValueError(f"multiplicador de dano nao positivo: {m}")
        return m


def stats_de_tracos(tracos: tuple[float, ...], cfg: ConfigArena | None = None) -> Stats:
    cfg = cfg or CONFIG_ARENA
    if len(tracos) != len(ORDEM_TRACOS):
        raise ValueError("vetor de tracos com tamanho errado")
    mapa = mapa_pet_combate(cfg)
    bruto = {c: 0.0 for c in ORDEM_COMBATE}
    for acao_pet, t in zip(ORDEM_TRACOS, tracos):
        bruto[mapa[acao_pet]] += t
    media = sum(bruto.values()) / len(ORDEM_COMBATE)
    return Stats(afinidade=tuple(bruto[c] - media for c in ORDEM_COMBATE))


@dataclass
class Lutador:
    nome: str
    politica: Politica
    stats: Stats


@dataclass(frozen=True)
class Turno:
    acao_a: str
    acao_b: str
    hp_a: float
    hp_b: float


@dataclass(frozen=True)
class ResultadoPartida:
    semente: int
    nome_a: str
    nome_b: str
    vencedor: str  # "a" | "b" | "empate"
    turnos: tuple[Turno, ...]

    @property
    def pontos_a(self) -> float:
        return {"a": 1.0, "b": 0.0, "empate": 0.5}[self.vencedor]

    def para_dict(self) -> dict:
        return {
            "semente": self.semente,
            "nome_a": self.nome_a,
            "nome_b": self.nome_b,
            "vencedor": self.vencedor,
            "turnos": [[t.acao_a, t.acao_b, t.hp_a, t.hp_b] for t in self.turnos],
        }


def observacao_de_combate(hp_proprio: float, hp_oponente: float, cfg: ConfigArena) -> Observacao:
    frac = hp_proprio / cfg.hp_inicial
    vantagem = (hp_proprio - hp_oponente) / cfg.hp_inicial
    humor = min(1.0, max(0.0, 0.5 + 0.5 * vantagem))
    return Observacao(
        vetor_estado=(cfg.fome_arena, cfg.higiene_arena, frac, humor, cfg.saude_arena, 0.0, 0.0, cfg.hora_arena),
        ticks_desde_cuidado=0,
        total_cuidados=0,
    )


def lutar(a: Lutador, b: Lutador, semente: int, cfg: ConfigArena | None = None) -> ResultadoPartida:
    """Partida deterministica dada a semente e as duas politicas."""
    cfg = cfg or CONFIG_ARENA
    mapa = mapa_pet_combate(cfg)
    rng_a = random.Random(derivar_semente("arena", semente, "a"))
    rng_b = random.Random(derivar_semente("arena", semente, "b"))
    hp_a = hp_b = cfg.hp_inicial
    turnos: list[Turno] = []

    for _ in range(cfg.max_turnos):
        # revelacao simultanea: as duas escolhas usam so o estado anterior ao turno
        ca = mapa[a.politica.agir(observacao_de_combate(hp_a, hp_b, cfg), rng_a)]
        cb = mapa[b.politica.agir(observacao_de_combate(hp_b, hp_a, cfg), rng_b)]
        if vence(ca, cb):
            hp_b = max(0.0, hp_b - cfg.dano_base * a.stats.multiplicador(ca, cfg))
        elif vence(cb, ca):
            hp_a = max(0.0, hp_a - cfg.dano_base * b.stats.multiplicador(cb, cfg))
        turnos.append(Turno(ca.value, cb.value, hp_a, hp_b))
        if hp_a <= 0.0 or hp_b <= 0.0:
            break

    if hp_a > hp_b:
        vencedor = "a"
    elif hp_b > hp_a:
        vencedor = "b"
    else:
        vencedor = "empate"
    return ResultadoPartida(semente, a.nome, b.nome, vencedor, tuple(turnos))
