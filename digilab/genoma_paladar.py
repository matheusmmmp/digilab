"""O genoma do Paladar (docs/futuro/paladar.md, secao 3.3; PL-2 pela recomendacao): o quanto cada pet gosta de cada qualidade do gosto.

Um peso por qualidade, `h_q`, na escala S do cerebro A:
  - as frutas (`doce`, `azedo`, `amargo`): sorteados por pet, uniformes e independentes em [paladar_h_min, paladar_h_max] (PROPOSTO
    [-S/2, S]), com a rng propria `paladar-ovo`, derivada da semente do ovo. Ela nao toca o temperamento, o `GenomaFrutas` do N4
    (`frutas-ovo`) nem nenhuma outra rng;
  - a racao (`salgado`): o mesmo para todos, `paladar_h_salgado` (PROPOSTO S/4), o gosto basico.
Os `h_q` nao sao pesos aprendidos: sao parametros do sinal do cerebro (o canal `gosto`, a etapa 3), como os `pesos_drives_corpo`. O
genoma e do individuo e fixo na vida; o aprendido nunca e herdado (DEFINICOES_FRUTAS_V2, 2.4).

O valor inato de um tipo para um pet e div_arred(Sum_q h_q x perfil_q, C): com as frutas como a mesma forma girada e os h independentes e
de mesma distribuicao, a fruta de maior valor inato e uniforme entre `a`, `b` e `c` sobre os pets. So inteiros.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .config import CONFIG_CORPO, ConfigCorpo
from .corpo import QUALIDADES, div_arred
from .events import FRUTAS
from .protocol import derivar_semente

QUALIDADES_SORTEADAS = ("doce", "azedo", "amargo")        # as das frutas, nesta ordem na rng
FLUXO = "paladar-ovo"


@dataclass(frozen=True)
class GenomaPaladar:
    h: dict                                                 # qualidade -> h_q, inteiro em [-S, S]

    def __post_init__(self) -> None:
        if set(self.h) != set(QUALIDADES):
            raise ValueError(f"o genoma do paladar tem as qualidades {QUALIDADES}, veio {sorted(self.h)}")
        if any(type(v) is not int for v in self.h.values()):
            raise ValueError(f"os h_q do genoma do paladar sao inteiros: {self.h!r}")

    def valor_inato(self, perfil: dict[str, int], escala: int) -> int:
        """div_arred(Sum_q h_q x perfil_q, C): o valor inato do tipo com este perfil (na escala S)."""
        if set(perfil) != set(QUALIDADES):
            raise ValueError(f"o perfil tem as qualidades {QUALIDADES}, veio {sorted(perfil)}")
        return div_arred(sum(self.h[q] * perfil[q] for q in QUALIDADES), escala)

    def favorita(self, perfis: dict[str, dict[str, int]], escala: int) -> list[str]:
        """As frutas de maior valor inato (com o empate, todas, na ordem de FRUTAS: quem desempata e quem usa, PJ-1)."""
        valores = {f: self.valor_inato(perfis[f], escala) for f in FRUTAS}
        maior = max(valores.values())
        return [f for f in FRUTAS if valores[f] == maior]


def genoma_paladar(semente: int, cc: ConfigCorpo | None = None) -> GenomaPaladar:
    """O genoma do paladar do ovo de `semente`: rng propria, um randint por qualidade das frutas, na ordem doce, azedo, amargo."""
    cc = cc or CONFIG_CORPO
    rng = random.Random(derivar_semente(FLUXO, semente))
    h = {q: rng.randint(cc.paladar_h_min, cc.paladar_h_max) for q in QUALIDADES_SORTEADAS}
    h["salgado"] = cc.paladar_h_salgado
    return GenomaPaladar({q: h[q] for q in QUALIDADES})
