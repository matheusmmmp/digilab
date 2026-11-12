"""O genoma da visao (GOSTO_VISUAL, P1d; docs/ESPEC_GOSTO_VISUAL_P1.md, secao 5.1; GV-4 e GV-7 pela recomendacao): o gosto inato de cada
pet pelo que passa na tela, no molde do `GenomaPaladar` (digilab/genoma_paladar.py).

Por canal k da tela (CANAIS_TELA, na ordem do evento `sentido_tela`), dois inteiros na escala C da TV (`ConfigOlhar.escala`):
  - o ponto otimo `o_k`, uniforme em [0, C];
  - a largura do pico `l_k`, uniforme em [largura_min, largura_max] (PROPOSTO [C/4, C]).
Sorteados por pet, uniformes e independentes, com a rng propria `visao-ovo`, derivada da semente do ovo; a ordem na rng e, canal a canal,
o otimo e depois a largura. Ela nao toca o temperamento, o `GenomaFrutas` (`frutas-ovo`), o `GenomaPaladar` (`paladar-ovo`) nem nenhuma
outra rng: o sorteio do genoma de hoje nao muda. Fixo na vida, nunca aprendido; o aprendido nunca e herdado (DEFINICOES_FRUTAS_V2, 2.4).
O genoma vazio (`genoma_visao_vazio`: todos os pets com o otimo no meio e a largura do meio) e o controle da run genoma x dono.

O agrado (o pico sobre a distancia ao otimo, em inteiros) e conta do cerebro (o M-SENS, digilab/digibrain/sens.py, `agrado`), que le o
genoma na escala S (`na_escala`). So inteiros.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .config import CANAIS_TELA, CONFIG_OLHAR, ConfigOlhar
from .policies.lobos import div_arred
from .protocol import derivar_semente

FLUXO = "visao-ovo"


@dataclass(frozen=True)
class GenomaVisao:
    otimo: dict                                             # canal -> o_k, inteiro em [0, C]
    largura: dict                                           # canal -> l_k, inteiro em [1, C]

    def __post_init__(self) -> None:
        for nome, d in (("otimo", self.otimo), ("largura", self.largura)):
            if type(d) is not dict or tuple(d) != CANAIS_TELA:
                raise ValueError(f"o genoma da visao tem {nome} por canal, na ordem {CANAIS_TELA}: {d!r}")
            if any(type(v) is not int for v in d.values()):
                raise ValueError(f"o {nome} do genoma da visao e inteiro: {d!r}")
        if any(v < 0 for v in self.otimo.values()) or any(v <= 0 for v in self.largura.values()):
            raise ValueError(f"o genoma da visao: otimo >= 0 e largura > 0: {self.otimo!r}, {self.largura!r}")

    def na_escala(self, S: int, C: int) -> tuple[dict, dict]:
        """(o otimo, a largura) na escala S do cerebro: div_arred(v x S, C); a largura no minimo 1"""
        if any(v > C for v in self.otimo.values()) or any(v > C for v in self.largura.values()):
            raise ValueError(f"o genoma da visao passa da escala C = {C}")
        return ({c: div_arred(v * S, C) for c, v in self.otimo.items()},
                {c: max(1, div_arred(v * S, C)) for c, v in self.largura.items()})

    def para_dict(self) -> dict:
        return {"otimo": dict(self.otimo), "largura": dict(self.largura)}


def genoma_visao(semente: int, co: ConfigOlhar | None = None) -> GenomaVisao:
    """O genoma da visao do ovo de `semente`: rng propria `visao-ovo`, dois randint por canal (o otimo, a largura), na ordem de CANAIS_TELA."""
    co = co or CONFIG_OLHAR
    if type(semente) is not int:
        raise TypeError(f"a semente do ovo e int: {semente!r}")
    rng = random.Random(derivar_semente(FLUXO, semente))
    otimo, largura = {}, {}
    for c in CANAIS_TELA:
        otimo[c] = rng.randint(0, co.escala)
        largura[c] = rng.randint(co.largura_min, co.largura_max)
    return GenomaVisao(otimo, largura)


def genoma_visao_vazio(co: ConfigOlhar | None = None) -> GenomaVisao:
    """O controle (espec, secao 5.1): o mesmo genoma para todos, o otimo no meio da escala e a largura do meio da faixa."""
    co = co or CONFIG_OLHAR
    return GenomaVisao({c: co.escala // 2 for c in CANAIS_TELA}, {c: (co.largura_min + co.largura_max) // 2 for c in CANAIS_TELA})
