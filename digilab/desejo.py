"""Registro de desejo (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md, secao 3).

O que o pet quer agora, CALCULADO (nunca inventado) e sem consumir rng:
  necessidade  do estado de vida: a necessidade mais baixa abaixo de
               `limiar_necessidade` (lado CONDICAO, cuidado)
  vontade      da politica: a acao com maior recompensa esperada pela MEDIA da
               posterior do bandit (theta^ . x, sem amostra, sem prior), emitida
               so se a margem para a segunda passar `limiar_vontade` (lado
               ESTILO, aprendizado). Bandit recem-nascido nao tem vontade.
Necessidade tem prioridade sobre vontade. Somente leitura: nao muda decisao.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import CONFIG_DESEJO, ConfigDesejo
from .events import ACOES_PET_HOJE
from .policy import Observacao

TIPOS = ("necessidade", "vontade")
# necessidade -> (indice em Observacao.vetor_estado, alvo)
NECESSIDADES = {"fome": (0, "comer"), "higiene": (1, "limpar"), "energia": (2, "dormir"), "humor": (3, "brincar")}
NECESSIDADE_DO_ALVO = {alvo: nome for nome, (_, alvo) in NECESSIDADES.items()}
# pedido de pausa do treino (TAREFA_TREINO_SOMBRIO): necessidade que vem da fadiga, nao do estado de vida
NECESSIDADE_DO_ALVO["descansar"] = "fadiga_treino"


@dataclass(frozen=True)
class Desejo:
    tick: int
    tipo: str
    alvo: str
    intensidade: float
    origem_ref: tuple[int, ...] = ()     # indice do evento de log que originou (vazio: estado corrente)

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS:
            raise ValueError(f"tipo de desejo desconhecido: {self.tipo!r}")
        if not 0.0 <= self.intensidade <= 1.0:
            raise ValueError(f"intensidade fora de [0, 1]: {self.intensidade}")

    def chave(self) -> tuple[str, str]:
        return self.tipo, self.alvo

    def para_dict(self) -> dict:
        return {"tick": self.tick, "tipo": self.tipo, "alvo": self.alvo, "intensidade": self.intensidade,
                "origem_ref": list(self.origem_ref)}


def desejo_de(obs: Observacao, politica, tick: int, cfg: ConfigDesejo | None = None) -> Desejo | None:
    cfg = cfg or CONFIG_DESEJO
    v = obs.vetor_estado
    urgentes = sorted((v[i], nome, alvo) for nome, (i, alvo) in NECESSIDADES.items() if v[i] < cfg.limiar_necessidade)
    if urgentes:
        nivel, _, alvo = urgentes[0]
        return Desejo(tick, "necessidade", alvo, (cfg.limiar_necessidade - nivel) / cfg.limiar_necessidade)
    bracos = getattr(politica, "_bracos", None)
    if bracos is None:
        return None                               # politica sem posterior (instinto): sem vontade
    x = politica._features(obs)
    medias = sorted(((sum(t * xi for t, xi in zip(bracos[a].theta(), x)), -i, a) for i, a in enumerate(ACOES_PET_HOJE)),
                    reverse=True)
    (m1, _, a1), (m2, _, _) = medias[0], medias[1]
    margem = m1 - m2
    if margem < cfg.limiar_vontade:
        return None
    return Desejo(tick, "vontade", a1.value, min(1.0, margem))

