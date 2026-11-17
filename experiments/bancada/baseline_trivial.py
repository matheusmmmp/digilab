"""A bancada da V3, módulo `baseline_trivial`: a política trivial da EVIDENCIA A1 (docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md, seção 3).

Quatro regras, na ordem, e nada mais: come se a fome < X; dorme se a energia < Y; brinca se o tédio > Z; senão explora. Não aprende, não
lembra, não escolhe o alvo (o motor do mundo usa o alvo padrão, `mundo.alvo_padrao_de`) e não lê a rng. A fome e a energia são as do
`vetor_estado` (0 a 1, 1 = satisfeito, como na `PoliticaInstinto`); o tédio é o receptor do corpo (`PercepcaoCorpo.tedio`, 0 a S, S =
entediado), lido como fração de S. X, Y e Z saem da calibração (seção 4 do plano), nunca da validação.
"""
from __future__ import annotations

from dataclasses import dataclass

from digilab.events import AcaoPet


@dataclass(frozen=True)
class LimiaresTriviais:
    """X, Y e Z do plano (seção 3): `fome` e `energia` no 0 a 1 do vetor_estado; `tedio` em fração de S"""
    fome: float
    energia: float
    tedio: float

    def __post_init__(self) -> None:
        for nome in ("fome", "energia", "tedio"):
            v = getattr(self, nome)
            if type(v) is not float or not 0.0 <= v <= 1.0:
                raise ValueError(f"limiar {nome} = {v!r}: um float de 0 a 1")


class BaselineTrivial:
    """A política trivial. Cumpre o Protocol `Politica` e os ganchos que o motor do mundo e o `Registro` chamam, todos sem efeito."""

    nome = "baseline_trivial"

    def __init__(self, limiares: LimiaresTriviais, S: int) -> None:
        if type(S) is not int or S <= 0:
            raise ValueError(f"S = {S!r}: um inteiro > 0")
        self.limiares, self.S = limiares, S

    def agir(self, obs, rng) -> AcaoPet:
        if obs.corpo is None or obs.corpo.tedio is None:
            raise RuntimeError("a baseline trivial precisa do corpo com o receptor do tedio (o corpo do v11)")
        fome, energia = obs.vetor_estado[0], obs.vetor_estado[2]
        if fome < self.limiares.fome:
            return AcaoPet.COMER
        if energia < self.limiares.energia:
            return AcaoPet.DORMIR
        if obs.corpo.tedio > self.limiares.tedio * self.S:
            return AcaoPet.BRINCAR
        return AcaoPet.EXPLORAR

    def observar(self, transicao) -> None:
        pass

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        pass

    def receber_acao_dono(self, acao, tick: int) -> None:
        pass

    def estado_interno(self) -> dict:
        return {"limiares": {"fome": self.limiares.fome, "energia": self.limiares.energia, "tedio": self.limiares.tedio}}
