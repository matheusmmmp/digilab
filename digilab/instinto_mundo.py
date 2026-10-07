"""O instinto do mundo fisico e a regra que liga a percepcao do mundo as entradas do cerebro A (V2; docs/TAREFA_V2_MUNDO_FISICO.md,
secao 9, etapa 3; plano docs/PLANO_ANALISE_V2_MUNDO_FISICO.md, secao 3).

O mundo (digilab/mundo.py, etapa 2) injeta `Observacao.mundo` (a `PercepcaoMundo`) e deixa `bola`, `fruta`, `frutas_cenario`,
`info_frutas` e `pedido_frutas` no padrao: os bonus da A1 e do N4 no instinto de hoje nao disparam no mundo. Este modulo le a percepcao
nova. O mundo nao sabe que o cerebro A existe: a regra que liga uma coisa a outra fica aqui (`entradas_mundo`).

A regra (o que o cerebro A recebe nas duas entradas do mundo, `lobos.ENTRADAS_MUNDO`):
- `bola` = 1,0 com a bola entre os `vistos`; 0,0 sem ela;
- `fruta` = 1,0 com alguma comida boa entre os `vistos` (racao ou fruta madura; a podre e a bola nao contam); 0,0 sem nenhuma.
Sem percepcao (`obs.mundo` None: um motor sem o mundo, ou a sonda de uma medida), as duas sao 0,0. As entradas sao binarias porque o
instinto da tarefa soma `w_fruta x 1` e `w_bola x 1`: com elas, o prior do cerebro A repete o instinto do mundo byte a byte.

O instinto do mundo (`PoliticaInstintoMundo`), igual ao de hoje fora de tres pontos:
- **a fome urgente** (regra `pedido_necessidade`): com a fome abaixo de 0,25 e para onde ir comer (comida boa vista, ou cheiro com
  direcao), o pet escolhe `comer`; o padrao do motor o leva a comida vista mais proxima ou segue o cheiro. Sem para onde ir, chama, como
  hoje. A higiene abaixo de 0,25 continua chamando; com as duas baixas e comida, come (a fome o pet resolve sozinho; a higiene, nao);
- **o tempo livre:** `comer` ganha `w_fruta x fruta` (um candidato novo, no fim, como no N4) e `brincar` ganha `w_bola x bola`, com as
  entradas da regra acima, os mesmos `w` calibrados do N4 e da A1 e a mesma chamada de `rng.choices`. As regras se chamam como no N4 e
  na A1 (`bola_no_cenario`, `fruta_no_cenario`): o cerebro A usa as mesmas linhas do prior;
- **o modo `sem_explorar`** (o braco P0z do plano, controle da premissa, nao um pet do jogo): o peso de `explorar` no tempo livre vai
  para `ocioso`, e `explorar` deixa de ser candidato.
A fome moderada e o sono sao os de hoje (a mesma chamada de rng). O instinto nao tem `escolher_alvo`: usa os alvos padrao do motor.
"""

from __future__ import annotations

import random

from .ambiente import REGRA_BOLA
from .config import CONFIG_BOLA, CONFIG_FRUTAS, Config, ConfigBola, ConfigFrutas
from .events import FRUTAS, AcaoPet, AcaoUsuario
from .frutas import REGRA_FRUTA
from .policy import Observacao, PoliticaInstinto

TIPOS_COMIDA_BOA = ("racao",) + FRUTAS            # os tipos maduros de `vistos` (a podre vem com `_podre`; a bola e `bola`)
REGRA_FOME_URGENTE = "pedido_necessidade"         # a regra de hoje; no mundo, com para onde ir, ela come
LIMIAR_FOME_URGENTE = 0.25                        # o mesmo literal do PoliticaInstinto (fome < 0,25 pede ajuda)


def comida_boa_vista(p) -> bool:
    """alguma racao ou fruta madura entre os `vistos` da PercepcaoMundo"""
    return any(tipo in TIPOS_COMIDA_BOA for _, tipo, *_ in p.vistos)


def bola_vista(p) -> bool:
    return any(tipo == "bola" for _, tipo, *_ in p.vistos)


def para_onde_comer(p) -> bool:
    """O motor tem um alvo padrao de `comer` (mundo.MotorMundo.alvo_padrao): a comida boa vista mais proxima, ou o cheiro com direcao.
    E a "comida boa vista ou cheiro" da tarefa, lida como "para onde ir": com cheiro mas sem direcao (`direcao_cheiro` 0, um plato do
    cheiro inteiro) e nada visto, o padrao nao tem alvo, e o pet ficaria parado sem comer e sem chamar (REGISTRO_DESVIOS)."""
    return comida_boa_vista(p) or (p.cheiro > 0 and p.direcao_cheiro != 0)


def entradas_mundo(p) -> tuple[float, float]:
    """A regra que liga a percepcao do mundo as entradas `bola` e `fruta` do cerebro A (docstring do modulo). `p` = Observacao.mundo
    (PercepcaoMundo) ou None."""
    if p is None:
        return 0.0, 0.0
    return (1.0 if bola_vista(p) else 0.0), (1.0 if comida_boa_vista(p) else 0.0)


class PoliticaInstintoMundo(PoliticaInstinto):
    """O instinto do mundo fisico (docstring do modulo). Sem `obs.mundo` e o PoliticaInstinto byte a byte (nada visto, nada cheirado),
    salvo o `sem_explorar`, que tira o explorar em qualquer caso."""

    nome = "instinto_mundo"

    def __init__(self, cfg: Config | None = None, cfg_bola: ConfigBola | None = None, cfg_frutas: ConfigFrutas | None = None,
                 sem_explorar: bool = False) -> None:
        super().__init__(cfg)
        # so os pesos: as chaves `ligada` destas configs sao do cenario do N4 e da A1, que o mundo substitui (o MotorMundo as exige
        # desligadas); o instinto do mundo ve pela percepcao nova
        self.w_bola = (cfg_bola or CONFIG_BOLA).w_bola
        self.w_fruta = (cfg_frutas or CONFIG_FRUTAS).w_fruta
        if self.w_bola < 0.0 or self.w_fruta < 0.0:
            raise ValueError(f"w_bola e w_fruta precisam ser >= 0: {self.w_bola}, {self.w_fruta}")
        if type(sem_explorar) is not bool:
            raise TypeError(f"sem_explorar precisa ser bool: {sem_explorar!r}")
        self.sem_explorar = sem_explorar

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        acao = super().agir(obs, rng)
        # a fome urgente: o ramo `pedido_necessidade` do instinto nao usa a rng, entao trocar a acao depois nao muda nenhum sorteio
        if (self._ultima_regra == REGRA_FOME_URGENTE and obs.mundo is not None
                and obs.vetor_estado[0] < LIMIAR_FOME_URGENTE and para_onde_comer(obs.mundo)):
            return AcaoPet.COMER
        return acao

    def _pesos_tempo_livre(self, energia: float, humor: float, obs: Observacao) -> dict:
        pesos = super()._pesos_tempo_livre(energia, humor, obs)     # os literais de sempre, na mesma ordem
        if self.sem_explorar:
            # P0z: o peso do explorar vai para o ocioso (mesma ordem dos outros candidatos)
            pesos = {AcaoPet.OCIOSO: pesos[AcaoPet.OCIOSO] + pesos[AcaoPet.EXPLORAR], AcaoPet.BRINCAR: pesos[AcaoPet.BRINCAR],
                     AcaoPet.CHAMAR_ATENCAO: pesos[AcaoPet.CHAMAR_ATENCAO]}
        bola, fruta = entradas_mundo(obs.mundo)
        extra = self.w_bola * bola
        if extra > 0.0:
            pesos[AcaoPet.BRINCAR] = pesos[AcaoPet.BRINCAR] + extra
            self._ultima_regra = REGRA_BOLA
        extra = self.w_fruta * fruta
        if extra > 0.0:
            pesos[AcaoPet.COMER] = extra                 # candidato novo, no fim da lista, como no N4
            self._ultima_regra = REGRA_FRUTA
        return pesos

    def termo_mundo(self, regra: str, obs: Observacao) -> float:
        """O peso que o mundo deu na regra (para o motivo, digilab/motivo.py): w_bola x bola em `bola_no_cenario`, w_fruta x fruta em
        `fruta_no_cenario`, 0 nas outras."""
        bola, fruta = entradas_mundo(obs.mundo)
        if regra == REGRA_BOLA:
            return self.w_bola * bola
        if regra == REGRA_FRUTA:
            return self.w_fruta * fruta
        return 0.0

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """Gancho vazio (como o do instinto da bola): roda no MotorPersonalidade, que repassa o dono. Nada aprende."""
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome, "parametros_aprendidos": 0,
                "mundo": {"w_bola": self.w_bola, "w_fruta": self.w_fruta, "sem_explorar": self.sem_explorar}}
