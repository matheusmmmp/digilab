"""Camada 2: politica de comportamento.

O contrato `Politica` e o ponto onde bandit, Q tabular e planejador vao
entrar como IMPLEMENTACOES ALTERNATIVAS, nao como reescrita. Trocar de
algoritmo tem que ser trocar de classe. Enquanto o protocolo nao estiver
congelado, nenhum deles e a escolha oficial.

O v0 traz so `PoliticaInstinto`: regras escritas a mao, zero aprendizado.
Ela nao e um rascunho do modelo aprendido -- ela e o BRACO DE CONTROLE do
experimento. Se um pet treinado por gente nao vencer este aqui, a
hipotese morre.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .config import Config
from .events import AcaoPet
from .state import Estado


@dataclass(frozen=True)
class Observacao:
    """O que a politica enxerga. Congelado: virou entrada de modelo."""

    vetor_estado: tuple[float, ...]
    ticks_desde_cuidado: int
    total_cuidados: int
    # V2, A1: ha bola no cenario (1.0) ou nao (0.0). Campo com padrao: `de_estado` (o motor da v1) nunca o preenche; so o
    # MotorAmbiente (digilab/ambiente.py) o injeta antes de `agir`. O bandit e as sondas nao o leem.
    bola: float = 0.0
    # V2, N4: o maior incentivo entre as frutas no cenario (0.0 sem fruta). Mesmo regime da `bola`: so o MotorFrutas
    # (digilab/frutas.py) injeta; `de_estado`, o bandit e as sondas nao o leem.
    fruta: float = 0.0
    # V2, N5: a informacao do dono vigente sobre cada fruta, na ordem de events.FRUTAS: +1 "faz bem", -1 "faz mal", 0 nenhuma. So o
    # MotorFrutas com ConfigInformacao.ligada injeta; o instinto, o bandit e as sondas nao leem (os lobos, rodada 6).
    info_frutas: tuple = (0.0, 0.0, 0.0)
    # V2, FRUTA-NO-CENARIO (parte A, decisao R2): a presenca de cada fruta no cenario, na ordem de events.FRUTAS (1.0 presente, 0.0
    # ausente): as mesmas frutas que a sub-decisao de comer considera. So o MotorFrutas com as frutas ligadas injeta; ninguem le ainda
    # (a decisao de comer dos lobos que le e a parte B). `fruta` continua o maior incentivo entre elas.
    frutas_cenario: tuple = (0.0, 0.0, 0.0)
    # V2, N7: o pedido do dono vigente, na ordem de events.FRUTAS: -1 na fruta que o dono pediu para deixar, 0 nas outras. So o MotorFrutas
    # com ConfigPedido.ligada injeta; ninguem le ainda (a entrada `pedido` dos lobos e do chat B).
    pedido_frutas: tuple = (0.0, 0.0, 0.0)
    # V2, mundo fisico (docs/TAREFA_V2_MUNDO_FISICO.md, secao 7): a `PercepcaoMundo` (digilab/mundo.py) da decisao: a propria posicao, a
    # regiao, os objetos vistos, o cheiro e a direcao dele, o alvo pendente. So o MotorMundo com ConfigMundo.ligada injeta; `de_estado`,
    # o bandit e as sondas nao o leem. Com o mundo, `bola`, `fruta`, `frutas_cenario`, `info_frutas` e `pedido_frutas` ficam no padrao.
    mundo: "PercepcaoMundo | None" = None  # noqa: F821

    @staticmethod
    def de_estado(estado: Estado) -> "Observacao":
        return Observacao(
            vetor_estado=estado.vetor(),
            ticks_desde_cuidado=estado.tick - estado.tick_ultimo_cuidado,
            total_cuidados=estado.total_cuidados,
        )


@dataclass(frozen=True)
class Transicao:
    """Entregue a politica depois de cada acao. No v0 ninguem usa."""

    observacao: Observacao
    acao: AcaoPet
    observacao_seguinte: Observacao
    recompensa: float | None = None


@runtime_checkable
class Politica(Protocol):
    nome: str

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        """Escolhe a proxima acao do pet."""

    def observar(self, transicao: Transicao) -> None:
        """Recebe o resultado. Politicas sem aprendizado ignoram."""

    def estado_interno(self) -> dict:
        """Parametros aprendidos, para inspecao e serializacao."""


class PoliticaInstinto:
    """Regras de prioridade escritas a mao. Determinista dada a rng.

    Nao aprende nada. Serve para tres coisas:
      1. o pet recem-nascido nao se comportar de forma aleatoria (cold start);
      2. ser a condicao de controle "sem aprendizado" da ablacao;
      3. ser o prior de onde as politicas aprendizes partem.
    """

    nome = "instinto"

    def __init__(self, cfg: Config | None = None) -> None:
        from .config import CONFIG_PADRAO

        self.cfg = cfg or CONFIG_PADRAO
        self._ultima_regra: str | None = None

    @property
    def ultima_regra(self) -> str | None:
        """Regra que decidiu a ultima chamada de agir(). Somente leitura; nao
        entra em estado_interno() nem muda decisao (usada por digilab.motivo)."""
        return self._ultima_regra

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        fome, higiene, energia, humor, saude, sujeira, dormindo, hora = obs.vetor_estado

        # Sono tem precedencia: exaustao ou madrugada.
        if energia < 0.25:
            self._ultima_regra = "sono_exaustao"
            return AcaoPet.DORMIR
        if dormindo > 0.5 and energia < 0.85:
            self._ultima_regra = "sono_continuar"
            return AcaoPet.DORMIR
        if self.cfg.e_noite(int(hora * 1440)) and energia < 0.55:
            self._ultima_regra = "sono_noite"
            return AcaoPet.DORMIR

        # Necessidades que o pet nao resolve sozinho: pede ajuda.
        if fome < 0.25 or higiene < 0.25:
            self._ultima_regra = "pedido_necessidade"
            return AcaoPet.CHAMAR_ATENCAO

        # Abandono recente pesa no humor.
        if obs.ticks_desde_cuidado > self.cfg.janela_atencao_ticks:
            self._ultima_regra = "abandono"
            return AcaoPet.EMBURRAR if humor < 0.35 else AcaoPet.CHAMAR_ATENCAO

        if fome < 0.45:
            self._ultima_regra = "fome_moderada"
            return AcaoPet.COMER if rng.random() < 0.5 else AcaoPet.CHAMAR_ATENCAO

        # Tempo livre: mistura ponderada, nunca uniforme.
        self._ultima_regra = "tempo_livre"
        pesos = self._pesos_tempo_livre(energia, humor, obs)
        acoes = list(pesos)
        return rng.choices(acoes, weights=[pesos[a] for a in acoes], k=1)[0]

    def _pesos_tempo_livre(self, energia: float, humor: float, obs: Observacao) -> dict:
        """Pesos da mistura do tempo livre: os literais de sempre, na mesma ordem (a canonica nao muda). Gancho da V2, A1:
        a subclasse com a bola (ambiente.PoliticaInstintoBola) soma o termo dela em brincar; aqui `obs` nao e lido."""
        return {
            AcaoPet.OCIOSO: 3.0,
            AcaoPet.EXPLORAR: 2.0 + 2.0 * energia,
            AcaoPet.BRINCAR: 1.0 + 3.0 * humor,
            AcaoPet.CHAMAR_ATENCAO: 1.0,
        }

    def observar(self, transicao: Transicao) -> None:
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome, "parametros_aprendidos": 0}


def efeito_da_acao_do_pet(
    estado: Estado, acao: AcaoPet, cfg: Config, intervalo: int
) -> Estado:
    """Como a acao escolhida realimenta o estado no intervalo seguinte."""
    from dataclasses import replace

    from .state import _limitar

    if acao is AcaoPet.DORMIR:
        return replace(estado, dormindo=True)

    novo = replace(estado, dormindo=False)

    if acao is AcaoPet.BRINCAR:
        return replace(
            novo,
            humor=_limitar(novo.humor + cfg.humor_por_tick_brincando * intervalo),
            energia=_limitar(novo.energia - 0.02),
        )
    if acao is AcaoPet.EXPLORAR:
        return replace(
            novo,
            energia=_limitar(novo.energia - 0.015),
            humor=_limitar(novo.humor + 0.01),
        )
    if acao is AcaoPet.COMER:
        return replace(novo, fome=_limitar(novo.fome + 0.05))
    if acao is AcaoPet.EMBURRAR:
        return replace(novo, humor=_limitar(novo.humor - 0.01))

    return novo
