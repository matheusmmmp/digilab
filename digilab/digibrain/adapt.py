"""M-ADAPT, o adaptador cerebro-corpo-motor (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.1): o DigiBrain modular sob o `Protocol`
`Politica` (digilab/policy.py), com os ganchos que o motor procura no cerebro (`escolher_alvo`, `consequencia_mundo`,
`consequencia_corpo`, `receber_acao_dono`).

Etapa 0 do prototipo (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): o adaptador encaminha aos modulos, e os modulos ainda nao tem
equacao (levantam NotImplementedError). Nenhuma conta propria aqui. O que ja vale, como no A (lobos.py:2318-2330), sao as falhas altas:
  - a Observacao chega sem `corpo` ou sem `mundo`;
  - uma decisao fica sem o gancho de consequencia (o corpo e o `observar`) quando chega a seguinte;
  - o alvo da intencao nao esta entre os candidatos do motor, ou o gancho chega para outra acao.

A ordem dos ganchos no motor com o mundo e o corpo e: `agir`, `escolher_alvo` (so nas acoes com alvo), `consequencia_corpo`, `observar`,
`consequencia_mundo` (so com o ocorrido). Por isso a decisao guarda tudo numa pendencia e so a fecha (a consequencia ao M-AFETO, ao
M-PLAST, ao M-MEM e ao M-ESTADO) no comeco da decisao seguinte. O `u` do `escolher_alvo` e ignorado: o alvo ja foi escolhido no `agir`.
A forma da `Intencao` e da pendencia e PROPOSTA (a interface entre o M-ARB e o motor; a espec, secao 4.1)."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..config import CONFIG_DIGIBRAIN, CONFIG_PADRAO, Config, ConfigDigibrain
from ..events import AcaoPet, AcaoUsuario
from ..policy import Observacao, Transicao
from ._comum import sem_equacao
from .afeto import Afeto
from .arb import Arbitragem
from .estado import EstadoDinamico
from .impulso import Impulso
from .mem import Memoria
from .plast import Plasticidade
from .sens import Sens


class DigibrainDesligado(RuntimeError):
    """o DigiBrain modular montado com a ConfigDigibrain desligada"""


@dataclass(frozen=True)
class Intencao:
    """a escolha do M-ARB: a acao e, nas acoes com alvo, o objeto (o tipo do candidato do motor e, quando ha, o id dele)"""

    acao: AcaoPet
    tipo_alvo: str | None = None
    id_alvo: int | None = None


@dataclass
class Modulos:
    """os modulos da DM-3, um por arquivo; os testes trocam por modulos de mentira para conferir o adaptador"""

    sens: Sens = field(default_factory=Sens)
    afeto: Afeto = field(default_factory=Afeto)
    estado: EstadoDinamico = field(default_factory=EstadoDinamico)
    impulso: Impulso = field(default_factory=Impulso)
    mem: Memoria = field(default_factory=Memoria)
    arb: Arbitragem = field(default_factory=Arbitragem)
    plast: Plasticidade = field(default_factory=Plasticidade)

    def itens(self) -> tuple:
        return (("sens", self.sens), ("afeto", self.afeto), ("estado", self.estado), ("impulso", self.impulso), ("mem", self.mem),
                ("arb", self.arb), ("plast", self.plast))


class DigiBrain:
    """o cerebro modular (a v13, DM-5), so com a ConfigDigibrain ligada; na etapa 0 nada no motor nem na bancada o monta"""

    nome = "digibrain"

    def __init__(self, cfg: Config | None = None, cfg_digibrain: ConfigDigibrain | None = None, modulos: Modulos | None = None) -> None:
        self.cd = cfg_digibrain or CONFIG_DIGIBRAIN
        if not self.cd.ligada:
            raise DigibrainDesligado("o DigiBrain modular so existe com a ConfigDigibrain ligada")
        self.cfg = cfg or CONFIG_PADRAO
        self.m = modulos or Modulos()
        self._pendencia: dict | None = None
        self._ultimo_motivo: dict | None = None

    @property
    def ultimo_motivo(self) -> dict | None:
        """o motivo da ultima decisao (a secao 7); sem equacao, nenhum"""
        return self._ultimo_motivo

    # ------------------------------------------------------------ a decisao
    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if obs.corpo is None or obs.mundo is None:
            raise ValueError("o DigiBrain modular decide com o corpo e o mundo na Observacao (obs.corpo e obs.mundo)")
        if self._pendencia is not None:
            self._fechar(self._pendencia)
            self._pendencia = None
        m = self.m
        sens = m.sens.codificar(obs)
        afeto = m.afeto.ler(sens)
        contexto = m.estado.contexto()
        memoria = m.mem.recuperar(sens, afeto) if self.cd.m_mem else None
        incentivo = m.plast.incentivo(sens, afeto)
        unidades = m.impulso.unidades(sens, afeto, contexto, incentivo, memoria)
        intencao = m.arb.escolher(unidades, afeto, sens, rng)            # a rng de politica vai so ao M-ARB
        if not isinstance(intencao, Intencao):
            raise TypeError(f"o M-ARB devolve uma Intencao: {intencao!r}")
        m.estado.escolhida(intencao)
        self._pendencia = {"intencao": intencao, "alvo": None, "corpo": None, "transicao": None, "mundo": None}
        return intencao.acao

    def escolher_alvo(self, acao: AcaoPet, candidatos: list, percepcao, u: int):
        p = self._pendente(acao, "escolher_alvo")
        if p["alvo"] is not None:
            raise RuntimeError(f"escolher_alvo duas vezes na mesma decisao ({acao.value})")
        it = p["intencao"]
        if it.tipo_alvo is None:
            raise ValueError(f"a intencao de {acao.value} chegou sem objeto, e o motor pede um alvo")
        alvo = next((c for c in candidatos if c.tipo == it.tipo_alvo and (it.id_alvo is None or c.id == it.id_alvo)), None)
        if alvo is None:
            raise ValueError(f"o alvo da intencao ({it.tipo_alvo}, {it.id_alvo}) nao esta entre os candidatos do motor: "
                             f"{[(c.tipo, c.id) for c in candidatos]}")
        p["alvo"] = alvo
        return alvo

    # ------------------------------------------------------------ a consequencia (guardada; vai aos modulos na decisao seguinte)
    def consequencia_corpo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        self._pendente(acao, "consequencia_corpo")["corpo"] = (ocorrido, obs_depois)

    def observar(self, transicao: Transicao) -> None:
        self._pendente(transicao.acao, "observar")["transicao"] = transicao

    def consequencia_mundo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        self._pendente(acao, "consequencia_mundo")["mundo"] = (ocorrido, obs_depois)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """os gestos do dono; a espec (secao 4.1) os poe na entrada do M-ADAPT, sem dizer ainda a que modulo vao"""
        raise sem_equacao("M-ADAPT", "receber_acao_dono")

    def estado_interno(self) -> dict:
        return {"pendente": self._pendencia is not None, "modulos": {nome: mod.estado_interno() for nome, mod in self.m.itens()}}

    # ------------------------------------------------------------ a pendencia
    def _pendente(self, acao: AcaoPet, gancho: str) -> dict:
        p = self._pendencia
        if p is None:
            raise RuntimeError(f"{gancho} sem decisao pendente")
        if p["intencao"].acao is not acao:
            raise RuntimeError(f"{gancho} de {acao.value} na decisao de {p['intencao'].acao.value}")
        return p

    def _fechar(self, p: dict) -> None:
        """a consequencia da decisao anterior aos modulos; sem o corpo ou sem o observar, a decisao ficou sem consequencia"""
        if p["corpo"] is None or p["transicao"] is None:
            raise RuntimeError(f"a decisao de {p['intencao'].acao.value} ficou sem o gancho de consequencia (o corpo e o observar)")
        if p["intencao"].tipo_alvo is not None and p["alvo"] is None:
            raise RuntimeError(f"a decisao de {p['intencao'].acao.value} tinha objeto, e o motor nao pediu o alvo")
        m = self.m
        m.afeto.consequencia(p)
        m.plast.aprender(p)
        if self.cd.m_mem:
            m.mem.codificar(p)
        m.estado.consequencia(p)
