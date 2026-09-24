"""Camada 1: estado e necessidades.

Determinista e escrita a mao de proposito. Esta camada e o AMBIENTE, nao
o agente. Nada aqui aprende. Se um dia aprender, o controle experimental
vai embora junto.

Toda necessidade vive em 0..1, onde 1 = plenamente satisfeita.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace

from .config import TICKS_POR_DIA, Config
from .events import AcaoUsuario


def _limitar(x: float, minimo: float = 0.0, maximo: float = 1.0) -> float:
    return max(minimo, min(maximo, x))


@dataclass(frozen=True)
class Estado:
    tick: int = 0
    fome: float = 0.80        # 1 = saciado
    higiene: float = 1.00
    energia: float = 0.90
    humor: float = 0.70
    saude: float = 1.00
    sujeira: int = 0
    dormindo: bool = False

    # contadores de cuidado, usados pela politica como memoria curta
    tick_ultimo_cuidado: int = 0
    total_cuidados: int = 0

    @property
    def tick_do_dia(self) -> int:
        return self.tick % TICKS_POR_DIA

    @property
    def em_privacao(self) -> bool:
        return min(self.fome, self.higiene, self.energia) < 0.15

    def vetor(self) -> tuple[float, ...]:
        """Representacao numerica para a politica. Ordem congelada."""
        return (
            self.fome,
            self.higiene,
            self.energia,
            self.humor,
            self.saude,
            self.sujeira / 5.0,
            1.0 if self.dormindo else 0.0,
            self.tick_do_dia / TICKS_POR_DIA,
        )


def avancar_um_tick(estado: Estado, cfg: Config, rng: random.Random) -> Estado:
    """Um minuto simulado. Funcao pura: mesmo estado + mesma rng = mesmo resultado."""
    noite = cfg.e_noite(estado.tick_do_dia)
    mult = cfg.multiplicador_noturno if noite else 1.0

    fome = estado.fome - cfg.decaimento_fome
    higiene = estado.higiene - cfg.decaimento_higiene * (
        1.0 + cfg.penalidade_higiene_por_sujeira * estado.sujeira
    )
    humor = estado.humor - cfg.decaimento_humor

    if estado.dormindo:
        energia = estado.energia + cfg.energia_por_tick_dormindo
    else:
        energia = estado.energia - cfg.decaimento_energia * mult

    sujeira = estado.sujeira
    if not estado.dormindo and rng.random() < cfg.prob_sujeira_por_tick:
        sujeira = min(cfg.sujeira_maxima, sujeira + 1)

    provisorio = replace(
        estado,
        fome=_limitar(fome),
        higiene=_limitar(higiene),
        energia=_limitar(energia),
        humor=_limitar(humor),
        sujeira=sujeira,
    )

    if provisorio.em_privacao:
        saude = estado.saude - cfg.dano_saude_por_tick
    else:
        saude = estado.saude + cfg.cura_saude_por_tick

    return replace(provisorio, tick=estado.tick + 1, saude=_limitar(saude))


def aplicar_acao_usuario(
    estado: Estado, acao: AcaoUsuario, cfg: Config, rng: random.Random
) -> Estado:
    """Efeito imediato de uma acao do dono sobre o estado."""
    novo = estado

    if acao is AcaoUsuario.ALIMENTAR:
        novo = replace(novo, fome=_limitar(novo.fome + cfg.ganho_alimentar))
        if rng.random() < cfg.prob_sujeira_pos_refeicao:
            novo = replace(novo, sujeira=min(cfg.sujeira_maxima, novo.sujeira + 1))

    elif acao is AcaoUsuario.LIMPAR:
        novo = replace(
            novo,
            higiene=_limitar(novo.higiene + cfg.ganho_limpar),
            sujeira=max(0, novo.sujeira - 1),
        )

    elif acao is AcaoUsuario.BRINCAR:
        novo = replace(
            novo,
            humor=_limitar(novo.humor + cfg.ganho_brincar_humor),
            energia=_limitar(novo.energia - cfg.custo_brincar_energia),
            fome=_limitar(novo.fome - cfg.custo_brincar_fome),
            dormindo=False,
        )

    elif acao is AcaoUsuario.ACARICIAR:
        novo = replace(novo, humor=_limitar(novo.humor + cfg.ganho_elogiar * 0.6))

    elif acao is AcaoUsuario.ELOGIAR:
        novo = replace(novo, humor=_limitar(novo.humor + cfg.ganho_elogiar))

    elif acao is AcaoUsuario.REPREENDER:
        novo = replace(novo, humor=_limitar(novo.humor - cfg.custo_repreender))

    else:  # pragma: no cover - enum fechado
        raise ValueError(f"acao de usuario desconhecida: {acao}")

    return replace(
        novo,
        tick_ultimo_cuidado=novo.tick,
        total_cuidados=novo.total_cuidados + 1,
    )
