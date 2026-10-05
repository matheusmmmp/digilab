"""As frutas no mundo (V2, N4): nutricao e valor hedonico separados, sem aprendizado de politica.

docs/DEFINICOES_FRUTAS_V2.md (F1-F11) e docs/PLANO_ANALISE_V2_N4.md (registrado antes da run). Estende o MotorAmbiente da bola
(digilab/ambiente.py, que nao muda) por subclasse. A regra das frutas nos lobos e do chat B; aqui a fruta entra pelo instinto.

  genoma_frutas          o genoma das frutas, com rng propria (`frutas-ovo`), fora do Temperamento (F4, F5): neofobia e a preferencia
                         inata de cada fruta. Fixo na vida.
  PoliticaInstintoFrutas o instinto (com a bola) que ve as frutas: com a chave e fruta no cenario, na regra de tempo livre `comer` entra
                         como candidato com peso `w_fruta x fruta` (o maior incentivo no cenario); a regra se chama `fruta_no_cenario`.
                         A mesma chamada de rng.choices; as regras de necessidade vem antes, como sempre.
  MotorFrutas            subclasse do MotorAmbiente. Frutas no cenario {fruta: prazo} fora do Estado; oferecer poe (ou renova) e NAO e
                         contato. Antes de cada decisao o consumo recente decai, as frutas vencidas saem e o motor injeta `obs.fruta`
                         e `obs.frutas_cenario` (a presenca de cada fruta, na ordem de FRUTAS; FRUTA-NO-CENARIO, parte A).
                         Se a politica escolheu `comer`: um sorteio na `rng_fruta` (sempre, haja fruta ou nao: numeros comuns); com
                         fruta, o pet escolhe uma com probabilidade proporcional ao incentivo e come (sub-decisao de comer, F3):
                           avaliacao = max(0, preferencia_inata - k_saciedade x consumo_recente_antes)   (a fome nao entra)
                           incentivo += taxa_incentivo x (avaliacao - incentivo)                           (o efeito nao entra: N3)
                           fome + nutricao; humor + efeito_humor[fruta]                                     (o ruim no humor, F6)
                         Registros derivados (F1): incentivo, avaliacao, consumo_recente, primeiro_contato e as linhas `oferta` e
                         `consumo`; o replay reconstroi tudo. Nomes so de comportamento ou medida (F2).
                         Desligada (padrao): nenhuma rng, nenhum registro, nenhuma chave nova no estado(): o MotorAmbiente byte a byte.
                         Ganchos dos lobos (LOBOS-MUNDO, docs/TAREFA_V2_LOBOS_MUNDO.md): se a politica tem `escolher_fruta`, a
                         sub-decisao passa por ela (mesmo u; None = a de sempre); depois de comer, `fruta_comida` (o sinal E2 do P1).
                         O instinto nao tem nenhum dos dois: a vida dele nao muda.
  OfertasFrutas          o cronograma das ofertas (B1, B2): nos horarios fixos, com o pet acordado, o proximo conjunto da rotacao.
  simular_vida_frutas    simular_vida com as ofertas FORA do orcamento: o canal conta as acoes do dono de sempre; as ofertas vao direto.

V2, N5, lado do mundo (docs/TAREFA_V2_N5_MUNDO.md; com ConfigInformacao.ligada, que exige as frutas):
  informar               o dono diz "faz bem" ou "faz mal" sobre uma fruta (`informar_fruta_<f>_<bem|mal>`, no fim de AcaoUsuario). NAO e
                         cuidado nem reforco: nao mexe no estado, nao conta como contato, nao passa por `receber_acao_dono` (o aprendiz
                         nao recebe como sinal) e fica fora do orcamento, pelo canal das ofertas (B2). Fica vigente por
                         `janela_min` para a PERCEPCAO: antes de cada decisao o motor injeta `obs.info_frutas` (+1 bem, -1 mal, 0 sem
                         informacao vigente, na ordem de FRUTAS). Informar de novo renova; o conteudo contrario troca o valor.
                         Registro derivado `informacoes` (tick, fruta, conteudo, prazo). Desligada: nada disso existe.
  DonoInformante         o dono sintetico que informa logo depois de cada oferta, sobre cada fruta oferecida, com o efeito real (E7):
                         modo `certo` (P2) diz o efeito real, modo `errado` (P2e) o contrario, nos mesmos ticks e na mesma frequencia;
                         modo `acoplado` (P2a, N5-4): o mesmo multiconjunto de frutas do P2 da unidade, com o conteudo verdadeiro, em
                         ticks sorteados uniformemente na vida pela rng propria `informacao-acoplada` (nao toca nenhuma outra rng).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import Callable

from .ambiente import MotorAmbiente, PoliticaInstintoBola, reproduzir_ambiente
from .config import (CONFIG_BOLA, CONFIG_DONOS, CONFIG_FRUTAS, CONFIG_INFORMACAO, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigBola,
                     ConfigDonos, ConfigFrutas, ConfigInformacao)
from .donos import Visao
from .events import (ACOES_FRUTAS, ACOES_INFORMACAO, FRUTAS, AcaoPet, AcaoUsuario, LogDeEventos, fruta_de, informacao_de, informar,
                     oferta_de)
from .policy import Observacao
from .protocol import derivar_semente
from .temperamento import NEUTRO, Temperamento
from .treino import CanalDeInteracao, Vida

REGRA_FRUTA = "fruta_no_cenario"


class FrutasSemChave(RuntimeError):
    """Oferta de fruta num motor com ConfigFrutas.ligada = False."""


class InformacaoSemChave(RuntimeError):
    """Informacao do dono num motor com ConfigInformacao.ligada = False."""


@dataclass(frozen=True)
class GenomaFrutas:
    neofobia: float
    preferencia_inata: dict

    def fruta_preferida(self) -> str:
        """a de maior preferencia inata (empate: a primeira de FRUTAS)"""
        return max(FRUTAS, key=lambda f: (self.preferencia_inata[f], -FRUTAS.index(f)))

    def para_dict(self) -> dict:
        return {"neofobia": self.neofobia, "preferencia_inata": dict(self.preferencia_inata),
                "fruta_preferida": self.fruta_preferida()}


def genoma_frutas(semente: int, cf: ConfigFrutas | None = None) -> GenomaFrutas:
    """rng propria, derivada da semente do ovo: nao toca ambiente, politica, temperamento nem combate. Ordem fixa: neofobia, a, b, c."""
    cf = cf or CONFIG_FRUTAS
    rng = random.Random(derivar_semente("frutas-ovo", semente))
    neofobia = rng.random() * cf.neofobia_max
    pref = {f: cf.pref_min + (cf.pref_max - cf.pref_min) * rng.random() for f in FRUTAS}
    return GenomaFrutas(neofobia, pref)


def efeitos_humor(genoma: GenomaFrutas, cf: ConfigFrutas) -> dict:
    """o efeito no humor de cada fruta: no mundo descasado a preferida de nascenca faz mal; em "iguais", todas iguais"""
    if cf.mundo == "iguais":
        return {f: cf.efeito_humor_neutro for f in FRUTAS}
    if cf.mundo == "descasado":
        ruim = genoma.fruta_preferida()
        return {f: (cf.efeito_humor_ruim if f == ruim else cf.efeito_humor_neutro) for f in FRUTAS}
    raise ValueError(f"mundo das frutas desconhecido: {cf.mundo!r}")


class PoliticaInstintoFrutas(PoliticaInstintoBola):
    """O instinto que ve a bola e as frutas, atras das chaves. Sem fruta (ou sem chave) e o instinto da bola."""

    nome = "instinto_frutas"

    def __init__(self, cfg: Config | None = None, cfg_bola: ConfigBola | None = None,
                 cfg_frutas: ConfigFrutas | None = None) -> None:
        super().__init__(cfg, cfg_bola)
        self.cf = cfg_frutas or CONFIG_FRUTAS

    def _pesos_tempo_livre(self, energia: float, humor: float, obs: Observacao) -> dict:
        pesos = super()._pesos_tempo_livre(energia, humor, obs)
        if self.cf.ligada and obs.fruta > 0.0:
            extra = self.cf.w_fruta * obs.fruta
            if extra > 0.0:
                pesos[AcaoPet.COMER] = extra             # candidato novo, no fim da lista: sem fruta ele nem existe
                self._ultima_regra = REGRA_FRUTA
        return pesos

    def estado_interno(self) -> dict:
        d = super().estado_interno()
        d["nome"] = self.nome
        d["frutas"] = {"ligada": self.cf.ligada, "w_fruta": self.cf.w_fruta}
        return d


class _PoliticaComFrutas:
    """Embrulho do MotorFrutas: antes de cada decisao prepara as frutas e injeta `obs.fruta` e `obs.frutas_cenario`; delega o resto."""

    def __init__(self, politica, motor: "MotorFrutas") -> None:
        self._pf = politica
        self._motor = motor

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if not self._motor.cf.ligada:
            return self._pf.agir(obs, rng)
        obs = replace(obs, fruta=self._motor._frutas_na_proxima_decisao(), frutas_cenario=self._motor._presenca_na_decisao())
        if self._motor.ci.ligada:
            obs = replace(obs, info_frutas=self._motor._informacao_na_proxima_decisao())
        return self._pf.agir(obs, rng)

    def observar(self, transicao) -> None:
        self._pf.observar(transicao)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self._pf.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self._pf.estado_interno()

    def __getattr__(self, nome: str):
        return getattr(self._pf, nome)


class MotorFrutas(MotorAmbiente):
    def __init__(self, politica=None, cfg=None, semente: int = 42, temperamento: Temperamento = NEUTRO,
                 especie: str = "brasa", obediencia_desligada: bool = False, cfg_bola: ConfigBola | None = None,
                 cfg_frutas: ConfigFrutas | None = None, semente_genoma: int | None = None,
                 cfg_informacao: ConfigInformacao | None = None, **kw) -> None:
        super().__init__(politica, cfg, semente, temperamento, especie, obediencia_desligada, cfg_bola, **kw)
        self.cf = cfg_frutas or CONFIG_FRUTAS
        self.ci = cfg_informacao or CONFIG_INFORMACAO
        if self.ci.ligada and not self.cf.ligada:
            raise ValueError("ConfigInformacao ligada exige ConfigFrutas ligada (a informacao e sobre as frutas)")
        if self.ci.ligada:
            self.informacao: dict[str, tuple[float, int]] = {}      # fruta -> (valor, prazo)
            self.informacoes: list[dict] = []
            self.decisoes_com_informacao = 0
        self.cenario: dict[str, int] = {}                       # fruta -> prazo
        self._na_decisao: list[str] = []
        self._visto_na_decisao = 0.0
        if self.cf.ligada:
            self.genoma = genoma_frutas(semente if semente_genoma is None else semente_genoma, self.cf)
            self.efeito_humor = efeitos_humor(self.genoma, self.cf)
            self._rng_fruta = random.Random(derivar_semente("fruta", semente))
            self._fator_recente = 2.0 ** (-1.0 / self.cf.meia_vida_recente)
            g = self.genoma
            self.incentivo = {f: g.preferencia_inata[f] * (1.0 - g.neofobia) for f in FRUTAS}
            self.avaliacao = {f: g.preferencia_inata[f] for f in FRUTAS}
            self.consumo_recente = {f: 0.0 for f in FRUTAS}
            self.primeiro_contato: dict[str, int | None] = {f: None for f in FRUTAS}
            self.ofertas: list[dict] = []
            self.consumos: list[dict] = []
            self.contagem_frutas = {"oferecidas": 0, "renovadas": 0, "comidas": 0, "expiradas": 0, "decisoes_com_fruta": 0,
                                    "ignoradas": 0, "comer_sem_fruta": 0}
        self.politica = _PoliticaComFrutas(self.politica, self)

    # ------------------------------------------------------------ o cenario
    def frutas_no_cenario(self) -> list[str]:
        t = self._estado.tick
        return [f for f in FRUTAS if f in self.cenario and t < self.cenario[f]]

    def _expirar_frutas(self, tick: int) -> None:
        for f in [f for f in FRUTAS if f in self.cenario and tick >= self.cenario[f]]:
            del self.cenario[f]
            self.contagem_frutas["expiradas"] += 1

    def _frutas_na_proxima_decisao(self) -> float:
        """Chamado pelo embrulho logo antes de `agir`: o consumo recente decai, as frutas vencidas saem, e o pet ve o maior incentivo
        entre as que ficaram (0.0 sem fruta)."""
        for f in FRUTAS:
            self.consumo_recente[f] *= self._fator_recente
        self._expirar_frutas(self._estado.tick)
        self._na_decisao = self.frutas_no_cenario()
        self._visto_na_decisao = max((self.incentivo[f] for f in self._na_decisao), default=0.0)
        return self._visto_na_decisao

    def _presenca_na_decisao(self) -> tuple[float, ...]:
        """FRUTA-NO-CENARIO: 1.0 para cada fruta que a decisao ve (as de `_na_decisao`, ja sem as vencidas), na ordem de FRUTAS"""
        return tuple(1.0 if f in self._na_decisao else 0.0 for f in FRUTAS)

    def informacao_vigente(self) -> tuple[float, ...]:
        """(+1 bem, -1 mal, 0 nenhuma) por fruta, na ordem de FRUTAS, no tick atual"""
        t = self._estado.tick
        return tuple(self.informacao[f][0] if f in self.informacao and t < self.informacao[f][1] else 0.0 for f in FRUTAS)

    def _informacao_na_proxima_decisao(self) -> tuple[float, ...]:
        """Chamado pelo embrulho logo antes de `agir`: a informacao vencida sai e o pet ve a vigente."""
        t = self._estado.tick
        for f in [f for f in FRUTAS if f in self.informacao and t >= self.informacao[f][1]]:
            del self.informacao[f]
        v = self.informacao_vigente()
        if any(x != 0.0 for x in v):
            self.decisoes_com_informacao += 1
        return v

    def _decisao_observada(self, transicao) -> None:
        super()._decisao_observada(transicao)
        if not self.cf.ligada:
            return
        presentes, self._na_decisao = self._na_decisao, []
        tick = self._estado.tick
        acao = transicao.acao
        escolhida = None
        incentivos = {f: self.incentivo[f] for f in presentes}
        if acao is AcaoPet.COMER:
            u = self._rng_fruta.random()                       # sempre: numeros comuns entre bracos
            if presentes:
                # LOBOS-MUNDO: a politica que tem a sub-decisao (lobos) escolhe com o mesmo u; senao (ou None), a de sempre
                escolher = getattr(self.politica, "escolher_fruta", None)
                escolhida = escolher(list(presentes), dict(incentivos), u) if escolher is not None else None
                if escolhida is None:
                    escolhida = self._escolher(presentes, u)
                elif escolhida not in presentes:
                    raise RuntimeError(f"a politica escolheu {escolhida!r}, fora do cenario {presentes}")
                self._comer(escolhida, tick)
                aviso = getattr(self.politica, "fruta_comida", None)   # E2: o sinal do P1 ve o estado depois de comer
                if aviso is not None:
                    aviso(escolhida, Observacao.de_estado(self._estado))
            else:
                self.contagem_frutas["comer_sem_fruta"] += 1
        if presentes:
            self.contagem_frutas["decisoes_com_fruta"] += 1
            if escolhida is None:
                self.contagem_frutas["ignoradas"] += 1
            self.ofertas.append({"tick": tick, "presentes": list(presentes), "incentivos": incentivos, "visto": self._visto_na_decisao,
                                 "escolhida": escolhida, "acao": acao.value, "fome": transicao.observacao.vetor_estado[0],
                                 "regra": getattr(self.politica, "ultima_regra", None)})

    def _escolher(self, presentes: list[str], u: float) -> str:
        """proporcional ao incentivo (a ordem e a de FRUTAS); todos zero: uniforme"""
        pesos = [self.incentivo[f] for f in presentes]
        total = 0.0
        for p in pesos:
            total += p
        if total <= 0.0:
            return presentes[min(int(u * len(presentes)), len(presentes) - 1)]
        alvo = u * total
        acc = 0.0
        for f, p in zip(presentes, pesos):
            acc += p
            if alvo < acc:
                return f
        return presentes[-1]

    def _comer(self, f: str, tick: int) -> None:
        g, cf = self.genoma, self.cf
        e = self._estado
        recente_antes = self.consumo_recente[f]
        inc_antes, aval_antes = self.incentivo[f], self.avaliacao[f]
        aval = max(0.0, g.preferencia_inata[f] - cf.k_saciedade * recente_antes)
        self.avaliacao[f] = aval
        self.incentivo[f] = inc_antes + cf.taxa_incentivo * (aval - inc_antes)
        self.consumo_recente[f] = recente_antes + 1.0
        if self.primeiro_contato[f] is None:
            self.primeiro_contato[f] = tick
        efeito = self.efeito_humor[f]
        self._estado = replace(e, fome=min(1.0, e.fome + cf.nutricao), humor=min(1.0, max(0.0, e.humor + efeito)))
        del self.cenario[f]
        self.contagem_frutas["comidas"] += 1
        self.consumos.append({"tick": tick, "fruta": f, "fome_antes": e.fome, "humor_antes": e.humor,
                              "incentivo_antes": inc_antes, "incentivo_depois": self.incentivo[f],
                              "avaliacao_antes": aval_antes, "avaliacao": aval, "consumo_recente_antes": recente_antes,
                              "nutricao": cf.nutricao, "efeito_humor": efeito})

    # ------------------------------------------------------------ acao do dono
    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if acao in ACOES_INFORMACAO:
            self._informar(acao)
            return
        if acao not in ACOES_FRUTAS:
            super()._aplicar_acao_usuario(acao)
            return
        if not self.cf.ligada:
            raise FrutasSemChave(f"{acao.value} com ConfigFrutas.ligada = False")
        tick = self._estado.tick
        if self.cl.ligada:
            self._conferir_morte(tick)
            self._vivo()
        self._n_eventos += 1                      # e um evento do log, mas NAO e contato
        f = fruta_de(acao)
        if f in self.frutas_no_cenario():
            self.contagem_frutas["renovadas"] += 1
        else:
            self.contagem_frutas["oferecidas"] += 1
        self.cenario[f] = tick + self.cf.duracao_min

    def _informar(self, acao: AcaoUsuario) -> None:
        """N5: so registra a informacao para a percepcao. Nao mexe no estado, nao e contato, nao chega ao aprendiz como sinal."""
        if not self.ci.ligada:
            raise InformacaoSemChave(f"{acao.value} com ConfigInformacao.ligada = False")
        tick = self._estado.tick
        if self.cl.ligada:
            self._conferir_morte(tick)
            self._vivo()
        self._n_eventos += 1                      # e um evento do log, mas NAO e contato nem reforco
        fruta, conteudo = informacao_de(acao)
        prazo = tick + self.ci.janela_min
        self.informacao[fruta] = (1.0 if conteudo == "bem" else -1.0, prazo)
        self.informacoes.append({"tick": tick, "fruta": fruta, "conteudo": conteudo, "prazo": prazo})

    def estado(self) -> dict:
        d = super().estado()
        if not self.cf.ligada:
            return d                              # desligada: o estado() do MotorAmbiente, sem chave nova
        d["frutas"] = {f: self.cenario[f] - self._estado.tick for f in self.frutas_no_cenario()}
        if self.ci.ligada:
            d["informacao"] = dict(zip(FRUTAS, self.informacao_vigente()))
        return d

    def resumo_frutas(self) -> dict:
        if not self.cf.ligada:
            return {"ligada": False}
        return {"ligada": True, "genoma": self.genoma.para_dict(), "efeito_humor": dict(self.efeito_humor),
                "incentivo": dict(self.incentivo), "avaliacao": dict(self.avaliacao), "consumo_recente": dict(self.consumo_recente),
                "primeiro_contato": dict(self.primeiro_contato), "contagem": dict(self.contagem_frutas),
                "ofertas": [dict(o) for o in self.ofertas], "consumos": [dict(c) for c in self.consumos],
                "rng_fruta": self._rng_fruta.getstate()[1][-1],
                **({"informacoes": [dict(i) for i in self.informacoes], "decisoes_com_informacao": self.decisoes_com_informacao}
                   if self.ci.ligada else {})}


def reproduzir_frutas(log: LogDeEventos, politica_fabrica: Callable, cfg=None, semente: int = 42,
                      fabrica_motor: Callable | None = None, **kw) -> MotorFrutas:
    """reproduzir_ambiente com a fabrica do MotorFrutas. Evento desconhecido levanta erro; a fabrica errada tambem."""
    motor = reproduzir_ambiente(log, politica_fabrica, cfg, semente, fabrica_motor=fabrica_motor, **kw)
    if not isinstance(motor, MotorFrutas):
        raise TypeError(f"a fabrica devolveu {type(motor).__name__}, nao MotorFrutas")
    return motor


def fabricas_frutas(especie: str = "brasa", temperamento: Temperamento = NEUTRO, cfg_frutas: ConfigFrutas | None = None,
                    cfg_bola: ConfigBola | None = None, obediencia_desligada: bool = True,
                    politica_fabrica: Callable | None = None, cfg_informacao: ConfigInformacao | None = None, **kw):
    """(fabrica da politica, fabrica do motor) de uma vida com frutas, no desenho do plano (secao 3): instinto que ve as frutas,
    obediencia, educacao, lesoes e bola desligadas, temperamento neutro. Reusadas no replay."""
    cf = cfg_frutas or CONFIG_FRUTAS
    cb = cfg_bola or CONFIG_BOLA
    fp = politica_fabrica or (lambda cfg=None: PoliticaInstintoFrutas(cfg, cb, cf))  # noqa: E731
    fm = (lambda politica, cfg, s: MotorFrutas(politica, cfg, s, temperamento, especie,  # noqa: E731
                                               obediencia_desligada=obediencia_desligada, cfg_bola=cb, cfg_frutas=cf,
                                               cfg_informacao=cfg_informacao, **kw))
    return fp, fm


# ================================================================== as ofertas e a vida
class OfertasFrutas:
    """O cronograma das ofertas, igual para todos os donos (B1: fora do sorteio do aleatorio; B2: fora do orcamento). Nos passos do
    dono em `horarios_oferta`, com o pet acordado, o proximo conjunto de `rotacao_ofertas`; dormindo, a oferta nao acontece e a rotacao
    nao anda."""

    def __init__(self, cf: ConfigFrutas | None = None) -> None:
        self.cf = cf or CONFIG_FRUTAS
        self.k = 0
        self.feitas: list[tuple[int, tuple]] = []

    def acoes(self, estado: dict) -> list[AcaoUsuario]:
        if estado["tick"] % TICKS_POR_DIA not in self.cf.horarios_oferta or estado["dormindo"]:
            return []
        conjunto = self.cf.rotacao_ofertas[self.k % len(self.cf.rotacao_ofertas)]
        self.k += 1
        self.feitas.append((estado["tick"], tuple(conjunto)))
        return [oferta_de(f) for f in conjunto]


class DonoInformante:
    """N5: o dono que informa sobre cada fruta oferecida, logo depois da oferta (os mesmos ticks em todos os modos: o calendario de
    ofertas nao depende do braco). Ele conhece o efeito real de cada fruta no humor (E7). Conteudo binario: "mal" se o efeito real e
    negativo, "bem" caso contrario (fruta neutra = "bem"). Modo `certo` (P2) diz o efeito real; `errado` (P2e), o contrario.
    Nomes definidos no docs/PLANO_ANALISE_V2_N5.md (PR #142).

    Modo `acoplado` (P2a; plano do N5, secao 4.2; decisao N5-4): o mesmo multiconjunto de (fruta, conteudo) que o modo certo da
    unidade produziu, com o conteudo VERDADEIRO, em ticks sorteados uniformemente ao longo da vida (um passo do dono, sem reposicao
    de ordem: cada item sorteia o seu) pela rng propria derivar_semente("informacao-acoplada", semente), toda consumida na
    construcao, antes da vida: nao toca a rng de ambiente, de politica, da fruta nem a do dono. A ordem em que as frutas chegam nao
    importa (o multiconjunto e ordenado antes do sorteio). So a contingencia com a oferta some. Fora do orcamento, como os outros.
    A vida chama `acoes_do_passo(tick, ofertadas)` em todo passo do dono: certo e errado respondem as ofertas do passo; o acoplado
    devolve o que a agenda marcou para aquele tick."""

    MODOS = ("certo", "errado", "acoplado")

    def __init__(self, modo: str, efeito_humor: dict) -> None:
        if modo not in self.MODOS:
            raise ValueError(f"modo do informante desconhecido: {modo!r}")
        if set(efeito_humor) != set(FRUTAS):
            raise ValueError(f"o informante precisa do efeito de todas as frutas: {sorted(efeito_humor)}")
        self.modo = modo
        self.efeito_humor = dict(efeito_humor)
        self.feitas: list[tuple[int, str, str]] = []
        self.agenda: dict[int, list[str]] = {}         # so o acoplado: tick -> frutas a informar
        if modo == "acoplado":
            self._construido = False                   # so pelo construtor `acoplado`, com o multiconjunto e a rng

    @classmethod
    def acoplado(cls, efeito_humor: dict, frutas_do_p2: list[str], semente: int, dias: int,
                 passo_ticks: int | None = None) -> "DonoInformante":
        """O P2a da unidade: `frutas_do_p2` e o multiconjunto das frutas sobre as quais o P2 (modo certo) da MESMA unidade informou;
        `semente` e a da unidade (a rng e derivar_semente("informacao-acoplada", semente)); `dias` e a duracao da vida."""
        passo = passo_ticks or CONFIG_DONOS.passo_ticks
        total = dias * TICKS_POR_DIA
        if total % passo != 0 or total <= 0:
            raise ValueError(f"duracao {dias} dias nao e multipla do passo do dono {passo}")
        fora = [f for f in frutas_do_p2 if f not in FRUTAS]
        if fora:
            raise ValueError(f"frutas desconhecidas no multiconjunto do P2: {fora}")
        d = cls("acoplado", efeito_humor)
        rng = random.Random(derivar_semente("informacao-acoplada", semente))
        passos = total // passo
        for f in sorted(frutas_do_p2, key=FRUTAS.index):
            tick = (rng.randrange(passos) + 1) * passo        # o tick em que o dono age depois do passo sorteado
            d.agenda.setdefault(tick, []).append(f)
        d._construido = True
        return d

    @classmethod
    def acoplado_de(cls, p2: "DonoInformante", semente: int, dias: int, passo_ticks: int | None = None) -> "DonoInformante":
        """O P2a a partir do informante certo de uma vida P2 ja jogada (o multiconjunto sai das informacoes que ele fez)."""
        if p2.modo != "certo":
            raise ValueError(f"o acoplado copia o P2 (modo certo), nao o modo {p2.modo!r}")
        return cls.acoplado(p2.efeito_humor, [f for _, f, _ in p2.feitas], semente, dias, passo_ticks)

    def pendentes(self) -> int:
        """quantas informacoes da agenda do acoplado ainda nao sairam (0 no fim de uma vida inteira)"""
        return sum(len(v) for v in self.agenda.values())

    @classmethod
    def do_genoma(cls, modo: str, semente_genoma: int, cf: ConfigFrutas) -> "DonoInformante":
        """o conhecimento do dono: o efeito real das frutas no mundo deste genoma (o mesmo que o MotorFrutas aplica)"""
        return cls(modo, efeitos_humor(genoma_frutas(semente_genoma, cf), cf))

    def conteudo(self, fruta: str) -> str:
        real = "mal" if self.efeito_humor[fruta] < 0.0 else "bem"
        if self.modo in ("certo", "acoplado"):                # o acoplado diz a verdade (N5-4)
            return real
        return "bem" if real == "mal" else "mal"

    def acoes(self, tick: int, ofertadas: list[str]) -> list[AcaoUsuario]:
        """certo e errado: uma informacao por fruta oferecida neste passo"""
        if self.modo == "acoplado":
            raise ValueError("o acoplado nao responde a ofertas: use acoes_do_passo")
        out = []
        for f in ofertadas:
            c = self.conteudo(f)
            self.feitas.append((tick, f, c))
            out.append(informar(f, c))
        return out

    def acoes_do_passo(self, tick: int, ofertadas: list[str]) -> list[AcaoUsuario]:
        """o que o dono informa neste passo: certo e errado, sobre as ofertas do passo; acoplado, o que a agenda marcou"""
        if self.modo != "acoplado":
            return self.acoes(tick, ofertadas)
        if not self._construido:
            raise ValueError("informante acoplado sem agenda: construa com DonoInformante.acoplado")
        out = []
        for f in self.agenda.pop(tick, []):
            c = self.conteudo(f)
            self.feitas.append((tick, f, c))
            out.append(informar(f, c))
        return out


def simular_vida_frutas(braco: str, dono, politica, semente: int, dias: int, orcamento: int, fabrica_motor: Callable,
                        ofertas: OfertasFrutas | None, cfg: Config | None = None, cfg_donos: ConfigDonos | None = None,
                        rotulo_dono: str | None = None, informante: DonoInformante | None = None) -> Vida:
    """treino.simular_vida com as ofertas de fruta FORA do orcamento: o canal impoe as acoes do dono de sempre; depois delas, as
    ofertas do cronograma vao direto ao motor (entram no log como acao_usuario, sem contar no canal). A rng do dono e a de sempre."""
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    total = dias * TICKS_POR_DIA
    if total % cfg_donos.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total // cfg_donos.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono or braco))
    canal = CanalDeInteracao(motor, orcamento, cfg_donos.max_interacoes_por_passo)
    n_ofertas = 0
    n_informacoes = 0
    for passo in range(passos):
        motor.avancar(cfg_donos.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
        feitas = ofertas.acoes(motor.estado()) if ofertas is not None else []
        for a in feitas:
            motor.observar(a)
            n_ofertas += 1
        if informante is not None:
            # N5: fora do orcamento, pelo canal das ofertas (B2); certo/errado respondem as ofertas, o acoplado segue a agenda
            for a in informante.acoes_do_passo(motor._estado.tick, [fruta_de(x) for x in feitas]):
                motor.observar(a)
                n_informacoes += 1
    canal.fechar()
    v = Vida(braco=braco, semente_coorte=semente, motor=motor, interacoes=canal.gasto)
    v.ofertas = n_ofertas
    v.informacoes = n_informacoes
    return v
