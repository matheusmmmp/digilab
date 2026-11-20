"""Controle de capacidade equivalente SEM lobos (V2, L1; D2 de docs/DEFINICOES_V2.md; docs/PLANO_ANALISE_V2_L1.md, 2.1).

Os mesmos 490 pesos inteiros, as mesmas 10 entradas, a mesma regra de atualizacao (`lobos.atualizar_pesos`), o
mesmo piso, teto e janela de credito (base `lobos.Aprendiz`) e as mesmas sementes, numa unica camada de decisao
sobre as 7 acoes, sem impulsos: toda acao e candidata em toda decisao e nenhuma regra do instinto existe.

Para ter 490 pesos sem lobos, a tabela e w[contexto][acao][entrada] com contexto = setimo do dia (7 fatias de
1440/7 ticks pela hora do dia): um indice sem semantica de regra, so para igualar a contagem (a politica com
lobos tem 7 regras x 7 acoes x 10 entradas).

Prior: em todo contexto, os coeficientes do tempo livre do instinto (ocioso 3; explorar 2 + 2 energia;
brincar 1 + 3 humor; chamar 1) e 1.0 para dormir, comer e emburrar (as acoes que o instinto so toma por regra).
O controle nao conhece sono, pedido nem abandono: comeca como um pet que nao dorme por regra. E o preco de nao
ter lobos. A atribuicao do motivo (motivo.motivo_lobos) e por entrada, como nos lobos ("pseudo-lobos"); nao
havendo regra, quando o prior decide nao ha fator.
"""

from __future__ import annotations

import random

from ..config import CONFIG_LOBOS, Config, ConfigLobos
from ..events import AcaoPet
from ..policy import Observacao
from .lobos import ACOES, ENTRADAS, Aprendiz, sortear

N_CONTEXTOS = 7
CONTEXTOS = tuple(f"contexto_{k}" for k in range(N_CONTEXTOS))
# prior em unidades de 1.0 (vira inteiro vezes S), o mesmo em todo contexto
PRIOR_CAMADA_UNICA: dict[AcaoPet, dict[str, int]] = {
    AcaoPet.OCIOSO: {"vies": 3},
    AcaoPet.EXPLORAR: {"vies": 2, "energia": 2},
    AcaoPet.BRINCAR: {"vies": 1, "humor": 3},
    AcaoPet.CHAMAR_ATENCAO: {"vies": 1},
    AcaoPet.DORMIR: {"vies": 1},
    AcaoPet.COMER: {"vies": 1},
    AcaoPet.EMBURRAR: {"vies": 1},
}


def contexto(obs: Observacao) -> str:
    """Setimo do dia pela hora (Estado.vetor[7] = tick do dia / 1440, em [0, 1))."""
    hora = obs.vetor_estado[7]
    k = int(hora * N_CONTEXTOS)
    if k >= N_CONTEXTOS:
        k = N_CONTEXTOS - 1
    if k < 0:
        raise ValueError(f"hora fora de [0, 1): {hora}")
    return CONTEXTOS[k]


class PoliticaCamadaUnica(Aprendiz):
    """Camada unica de decisao sobre as 7 acoes, sem lobos. Mesmo contrato da PoliticaLobos."""

    nome = "camada_unica"

    def __init__(self, cfg: Config | None = None, cfg_lobos: ConfigLobos | None = None) -> None:
        cl = cfg_lobos or CONFIG_LOBOS
        super().__init__(cfg, cl, self._tabela_prior(cl.escala))

    @staticmethod
    def _tabela_prior(escala: int) -> dict[str, dict[AcaoPet, list[int]]]:
        tabela = {}
        for c in CONTEXTOS:
            por_acao = {}
            for a in ACOES:
                coefs = PRIOR_CAMADA_UNICA[a]
                desconhecidas = set(coefs) - set(ENTRADAS)
                if desconhecidas:
                    raise ValueError(f"entrada desconhecida no prior: {desconhecidas}")
                por_acao[a] = [int(coefs.get(e, 0)) * escala for e in ENTRADAS]
            tabela[c] = por_acao
        return tabela

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        x = self.percepcao(obs)
        c = contexto(obs)
        contrib, pesos = self._pesos_efetivos(c, ACOES, x)
        u = rng.random()
        acao = ACOES[sortear([pesos[a] for a in ACOES], u)]
        self._registrar(c, ACOES, acao, x, pesos, contrib, u, extra={"sem_impulsos": True})
        return acao
