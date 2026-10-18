"""Registro de desejo (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md, secao 3).

O que o pet quer agora, CALCULADO (nunca inventado) e sem consumir rng:
  necessidade  do estado de vida: a necessidade mais baixa abaixo de
               `limiar_necessidade` (lado CONDICAO, cuidado)
  vontade      da politica: a acao com maior recompensa esperada pela MEDIA da
               posterior do bandit (theta^ . x, sem amostra, sem prior), emitida
               so se a margem para a segunda passar `limiar_vontade` (lado
               ESTILO, aprendizado). Bandit recem-nascido nao tem vontade.
Necessidade tem prioridade sobre vontade. Somente leitura: nao muda decisao.

Com o cerebro A (os pets v11 do jogo; docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, PW-3, o D-W4 do #201): `desejo_lobos`. A necessidade e a
mesma; a vontade e a acao de maior desvio aprendido sobre o prior na regra do tempo livre (`PoliticaLobos.desvio_aprendido`), com a
mesma margem (`limiar_vontade`) e o mesmo desempate (a primeira de ACOES_PET_HOJE). O A recem-nascido e o instinto: nao tem vontade.
O `desejo_de` de sempre nao muda (o cerebro A nele segue sem vontade, como o instinto).
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import CONFIG_DESEJO, ConfigDesejo
from .events import ACOES_PET_HOJE, AcaoPet
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


def _necessidade(obs: Observacao, tick: int, cfg: ConfigDesejo) -> Desejo | None:
    """a necessidade mais baixa abaixo do limiar (o lado da condicao), ou None"""
    v = obs.vetor_estado
    urgentes = sorted((v[i], nome, alvo) for nome, (i, alvo) in NECESSIDADES.items() if v[i] < cfg.limiar_necessidade)
    if urgentes:
        nivel, _, alvo = urgentes[0]
        return Desejo(tick, "necessidade", alvo, (cfg.limiar_necessidade - nivel) / cfg.limiar_necessidade)
    return None


def _vontade(tick: int, notas: list[tuple[float, AcaoPet]], cfg: ConfigDesejo) -> Desejo | None:
    """a acao de maior nota, se a margem para a segunda passar o limiar (empate: a primeira de ACOES_PET_HOJE)"""
    ordem = sorted(((m, -ACOES_PET_HOJE.index(a), a) for m, a in notas), reverse=True)
    (m1, _, a1), (m2, _, _) = ordem[0], ordem[1]
    margem = m1 - m2
    if margem < cfg.limiar_vontade:
        return None
    return Desejo(tick, "vontade", a1.value, min(1.0, margem))


def desejo_lobos(obs: Observacao, cerebro, tick: int, cfg: ConfigDesejo | None = None) -> Desejo | None:
    """O desejo dos pets v11 (PW-3): a necessidade de sempre e, sem ela, a vontade pelo desvio aprendido do cerebro A na regra do tempo
    livre (`cerebro.desvio_aprendido`). Pura (nao muda o cerebro). `cerebro` e o PoliticaLobos (sem embrulho)."""
    cfg = cfg or CONFIG_DESEJO
    n = _necessidade(obs, tick, cfg)
    if n is not None:
        return n
    desvio = cerebro.desvio_aprendido(obs)
    if len(desvio) < 2:
        raise ValueError(f"vontade com menos de duas acoes no tempo livre: {sorted(a.value for a in desvio)}")
    return _vontade(tick, [(d, a) for a, d in desvio.items()], cfg)


def desejo_de(obs: Observacao, politica, tick: int, cfg: ConfigDesejo | None = None) -> Desejo | None:
    cfg = cfg or CONFIG_DESEJO
    n = _necessidade(obs, tick, cfg)
    if n is not None:
        return n
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

