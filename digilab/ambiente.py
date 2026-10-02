"""A bola no cenario: o primeiro objeto do mundo com consequencia (V2, A1).

docs/V2_A1_BOLA_DESENHO.md (aprovado, opcao A) e docs/PLANO_ANALISE_V2_A1.md (registrado antes da run). No L0/L1 nada daqui
e lido: a bola entra pelo INSTINTO, com a chave ConfigBola.ligada; a regra `bola_no_cenario` dos lobos e do chat B (A1 + L1).

  PoliticaInstintoBola   o PoliticaInstinto com a bola: com a chave e bola no cenario, na regra de tempo livre `brincar` ganha
                         `+ w_bola x bola` (a mesma chamada de rng.choices; nenhuma rng a mais) e a regra se chama
                         `bola_no_cenario`. Sem chave, ou sem bola, ou com w_bola = 0: os pesos e a regra de sempre.
  MotorAmbiente          subclasse do MotorEducacao (engine.py intocado). A bola vive fora do Estado: {tick_posta, prazo}.
                         - `por_bola`: poe (ou renova o prazo, se ja ha bola); `tirar_bola`: tira (sem bola: erro). As duas NAO sao
                           contato: nao zeram o tempo sem cuidado, nao passam pela politica, pelo vinculo nem pela janela da educacao;
                           consomem 1 interacao do orcamento como qualquer acao do dono. Sem a chave, levantam erro.
                         - percepcao: antes de cada `agir` o motor injeta `obs.bola` (1.0 com bola no cenario, 0.0 sem); a bola que
                           passou do prazo expira nesse momento.
                         - consequencia: a politica escolheu `brincar` com bola no cenario = brincou COM a bola: humor
                           + ganho_humor_bola (cortado em 1,0), alem do efeito do brincar de sempre, e a bola some. Qualquer outra
                           acao = ignorou por esta decisao (a bola fica ate o prazo).
                         - nenhuma rng: por, usar e expirar sao deterministicos; o replay reconstroi tudo do log.
                         - desligada (padrao): nenhuma bola, nenhum campo novo no comportamento: MotorEducacao byte a byte (teste).
  reproduzir_ambiente    reproduzir_educacao com a fabrica do MotorAmbiente (os eventos da bola sao `acao_usuario` de sempre).
  DonoComBola            os donos sinteticos da v1 embrulhados: poem a bola pela regra do plano (secao 1); nenhum usa `tirar_bola`.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Callable

from .config import CONFIG_BOLA, CONFIG_DONOS, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigBola, ConfigDonos
from .donos import DonoAleatorio, Visao, criar_dono, cuidados_necessarios
from .educacao import MotorEducacao, reproduzir_educacao
from .events import ACOES_BOLA, ACOES_V1, AcaoPet, AcaoUsuario, LogDeEventos
from .policy import Observacao, PoliticaInstinto
from .temperamento import NEUTRO, Temperamento

REGRA_BOLA = "bola_no_cenario"


class BolaSemChave(RuntimeError):
    """Acao da bola num motor com ConfigBola.ligada = False (ou num motor que nao e o MotorAmbiente)."""


class PoliticaInstintoBola(PoliticaInstinto):
    """O instinto que ve a bola, atras da chave. Fora da regra de tempo livre nada muda (as necessidades vem antes)."""

    nome = "instinto_bola"

    def __init__(self, cfg: Config | None = None, cfg_bola: ConfigBola | None = None) -> None:
        super().__init__(cfg)
        self.cb = cfg_bola or CONFIG_BOLA

    def _pesos_tempo_livre(self, energia: float, humor: float, obs: Observacao) -> dict:
        pesos = super()._pesos_tempo_livre(energia, humor, obs)
        if self.cb.ligada and obs.bola > 0.0:
            extra = self.cb.w_bola * obs.bola
            if extra > 0.0:
                pesos[AcaoPet.BRINCAR] = pesos[AcaoPet.BRINCAR] + extra
                self._ultima_regra = REGRA_BOLA
        return pesos

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """Gancho vazio: deixa o instinto rodar no MotorPersonalidade (o embrulho repassa o feedback). Nada aprende."""
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome, "parametros_aprendidos": 0,
                "bola": {"ligada": self.cb.ligada, "w_bola": self.cb.w_bola}}


class _PoliticaComBola:
    """Embrulho do MotorAmbiente: injeta `obs.bola` antes de cada decisao e delega todo o resto."""

    def __init__(self, politica, motor: "MotorAmbiente") -> None:
        self._pb = politica
        self._motor = motor

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if not self._motor.cb.ligada:
            return self._pb.agir(obs, rng)
        presente = self._motor._bola_na_proxima_decisao()
        return self._pb.agir(replace(obs, bola=1.0 if presente else 0.0), rng)

    def observar(self, transicao) -> None:
        self._pb.observar(transicao)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self._pb.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self._pb.estado_interno()

    def __getattr__(self, nome: str):
        return getattr(self._pb, nome)


class MotorAmbiente(MotorEducacao):
    def __init__(self, politica=None, cfg=None, semente: int = 42, temperamento: Temperamento = NEUTRO,
                 especie: str = "brasa", obediencia_desligada: bool = False, cfg_bola: ConfigBola | None = None,
                 **kw) -> None:
        super().__init__(politica, cfg, semente, temperamento, especie, obediencia_desligada, **kw)
        self.cb = cfg_bola or CONFIG_BOLA
        self.bola: dict | None = None
        self._bola_na_decisao = False
        self.contagem_bola = {"postas": 0, "renovadas": 0, "tiradas": 0, "usadas": 0, "expiradas": 0,
                              "decisoes_com_bola": 0, "ignoradas": 0}
        self.historico_bola: list[dict] = []
        self.politica = _PoliticaComBola(self.politica, self)

    # ------------------------------------------------------------ a bola
    def bola_presente(self) -> bool:
        return self.bola is not None and self._estado.tick < self.bola["prazo"]

    def _fechar_bola(self, desfecho: str, tick: int) -> None:
        self.historico_bola.append({**self.bola, "desfecho": desfecho, "fim": tick})
        self.bola = None

    def _expirar_bola(self, tick: int) -> None:
        if self.bola is not None and tick >= self.bola["prazo"]:
            self.contagem_bola["expiradas"] += 1
            self._fechar_bola("expirada", tick)

    def _bola_na_proxima_decisao(self) -> bool:
        """Chamado pelo embrulho logo antes de `agir`: expira a bola vencida e fixa o que a politica ve nesta decisao."""
        self._expirar_bola(self._estado.tick)
        self._bola_na_decisao = self.bola is not None
        return self._bola_na_decisao

    def _decisao_observada(self, transicao) -> None:
        super()._decisao_observada(transicao)
        if not self._bola_na_decisao:
            return
        self._bola_na_decisao = False
        self.contagem_bola["decisoes_com_bola"] += 1
        if transicao.acao is AcaoPet.BRINCAR:
            # brincou COM a bola: a consequencia alem do brincar de sempre (que o engine ja aplicou); a bola some
            self._estado = replace(self._estado, humor=min(1.0, self._estado.humor + self.cb.ganho_humor_bola))
            self.contagem_bola["usadas"] += 1
            self._fechar_bola("usada", self._estado.tick)
        else:
            self.contagem_bola["ignoradas"] += 1

    # ------------------------------------------------------------ acao do dono
    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if acao not in ACOES_BOLA:
            super()._aplicar_acao_usuario(acao)
            return
        if not self.cb.ligada:
            raise BolaSemChave(f"{acao.value} com ConfigBola.ligada = False")
        tick = self._estado.tick
        if self.cl.ligada:
            self._conferir_morte(tick)
            self._vivo()
        self._n_eventos += 1                      # e um evento do log (indice dos refs), mas NAO e contato
        if acao is AcaoUsuario.POR_BOLA:
            if self.bola_presente():
                self.bola = {**self.bola, "prazo": tick + self.cb.duracao_min, "renovada_em": tick}
                self.contagem_bola["renovadas"] += 1
            else:
                self._expirar_bola(tick)
                self.bola = {"tick_posta": tick, "prazo": tick + self.cb.duracao_min}
                self.contagem_bola["postas"] += 1
            return
        if not self.bola_presente():
            raise ValueError(f"tirar_bola no tick {tick} sem bola no cenario")
        self.contagem_bola["tiradas"] += 1
        self._fechar_bola("tirada", tick)

    def estado(self) -> dict:
        d = super().estado()
        if not self.cb.ligada:
            return d                              # desligada: o estado() do MotorEducacao, sem chave nova
        if self.bola_presente():
            d["bola"] = {"tick_posta": self.bola["tick_posta"], "prazo": self.bola["prazo"],
                         "restante": self.bola["prazo"] - self._estado.tick}
        else:
            d["bola"] = None
        return d

    def resumo_bola(self) -> dict:
        return {"ligada": self.cb.ligada, "contagem": dict(self.contagem_bola), "historico": list(self.historico_bola),
                "no_cenario": self.estado()["bola"]}


def reproduzir_ambiente(log: LogDeEventos, politica_fabrica: Callable, cfg=None, semente: int = 42,
                        fabrica_motor: Callable | None = None, **kw) -> MotorAmbiente:
    """reproduzir_educacao com a fabrica do MotorAmbiente. Evento desconhecido levanta erro; a fabrica errada tambem."""
    if fabrica_motor is None:
        raise ValueError("reproduzir_ambiente precisa da fabrica do MotorAmbiente")
    motor = reproduzir_educacao(log, politica_fabrica, cfg, semente, fabrica_motor=fabrica_motor, **kw)
    if not isinstance(motor, MotorAmbiente):
        raise TypeError(f"a fabrica devolveu {type(motor).__name__}, nao MotorAmbiente")
    return motor


def fabricas_ambiente(especie: str = "brasa", temperamento: Temperamento = NEUTRO, cfg_bola: ConfigBola | None = None,
                      obediencia_desligada: bool = True, politica_fabrica: Callable | None = None, **kw):
    """(fabrica da politica, fabrica do motor) de uma vida com a bola, no desenho do plano (secao 3): instinto com a bola,
    obediencia desligada, educacao e lesoes desligadas (padrao dos configs), temperamento neutro. Reusadas no replay."""
    cb = cfg_bola or CONFIG_BOLA
    fp = politica_fabrica or (lambda cfg=None: PoliticaInstintoBola(cfg, cb))  # noqa: E731
    fm = (lambda politica, cfg, s: MotorAmbiente(politica, cfg, s, temperamento, especie,  # noqa: E731
                                                 obediencia_desligada=obediencia_desligada, cfg_bola=cb, **kw))
    return fp, fm


# ================================================================== donos com a bola
class DonoAleatorioBola(DonoAleatorio):
    """O aleatorio da v1 com `por_bola` no sorteio uniforme (as 6 acoes da v1 + a bola)."""

    nome = "aleatorio"
    POOL = ACOES_V1 + (AcaoUsuario.POR_BOLA,)

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        if self._plano is None:
            self._plano = self._planejar(visao, rng)
        acoes = list(self.POOL)
        return [rng.choice(acoes) for _ in range(self._plano[visao.passo])]

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        return rng.choice(list(self.POOL))


class DonoComBola:
    """Embrulha o dono da v1 (plano, secao 1). Atencioso e incoerente poem a bola com o pet acordado, fora da noite, sem
    cuidado pendente, sem bola no cenario, no maximo `bolas_por_dia` por dia e dentro do maximo do passo; o relapso so nos
    passos em que ele mesmo agiu (as visitas); o aleatorio sorteia `por_bola` entre as acoes. Ninguem usa `tirar_bola`.
    A bola consome 1 interacao do orcamento, como qualquer acao: por a bola e trocar um cuidado por uma oportunidade."""

    def __init__(self, braco: str, cfg_bola: ConfigBola | None = None, cfg_donos: ConfigDonos | None = None,
                 cfg: Config | None = None) -> None:
        self.nome = braco
        self.cb = cfg_bola or CONFIG_BOLA
        self.cd = cfg_donos or CONFIG_DONOS
        self.cfg = cfg or CONFIG_PADRAO
        self.base = DonoAleatorioBola(self.cd) if braco == "aleatorio" else criar_dono(braco)
        self._dia = -1
        self._bolas_hoje = 0
        self.contagem = {"bolas": 0, "passos_com_bola": 0}

    def decidir(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        acoes = self.base.decidir(visao, rng)
        if self.nome == "aleatorio":
            n = sum(a is AcaoUsuario.POR_BOLA for a in acoes)
            self.contagem["bolas"] += n
            self.contagem["passos_com_bola"] += n > 0
            return acoes
        e = visao.estado
        dia = e["tick"] // TICKS_POR_DIA
        if dia != self._dia:
            self._dia, self._bolas_hoje = dia, 0
        if self.nome == "relapso" and not acoes:
            return acoes
        if (self._bolas_hoje < self.cb.bolas_por_dia and len(acoes) < visao.maximo_permitido and not e["dormindo"]
                and not self.cfg.e_noite(e["tick_do_dia"]) and e.get("bola") is None
                and not cuidados_necessarios(e, self.cd)):
            acoes.append(AcaoUsuario.POR_BOLA)
            self._bolas_hoje += 1
            self.contagem["bolas"] += 1
            self.contagem["passos_com_bola"] += 1
        return acoes
