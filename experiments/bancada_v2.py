"""V2, BANCADA (docs/TAREFA_V2_BANCADA.md): um orquestrador unico para os bracos da pergunta maior.

    python experiments/bancada_v2.py --config experiments/configs/bancada/fumaca.json --saida <pasta>   # fumaca, NAO canonica

A pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6) compara fontes de plasticidade no MESMO aprendiz (validacao
V1 do docs/ROADMAP_V2.md: a L1 separa de onde vem o sinal da regra de atualizacao). A bancada fixa isso em codigo:

  vida = (genoma, mundo, dono, braco, semente)
    genoma   None = sem genoma (temperamento neutro); um inteiro g = temperamento sorteado de g (a semente do genoma separada
             da do ambiente, como no E1 da linhagem). No mundo padrao: MotorComFeedback sem genoma (como a L1) e
             MotorPersonalidade com genoma; nos mundos da bola, sempre o MotorAmbiente da A1 (obediencia desligada).
    mundo    padrao   o motor de sempre, sem objeto nenhum.
             bola     a bola da A1 (MotorAmbiente, ConfigBola ligada) com as decisoes B1 e B2 de 2026-10-01: os donos sao os
                      da v1 (o aleatorio NAO sorteia por_bola) e a bola entra por uma regra do mundo FORA do orcamento
                      (RegraBola: a regra dos coerentes do DonoComBola sem o limite do passo; o relapso so nas visitas, B3).
             bola_a1  a bola exatamente como a A1 rodou (DonoComBola: o aleatorio sorteia por_bola e a bola gasta orcamento);
                      so para reproduzir a A1 (gate), nao para runs novas.
             Cada mundo realiza uma CONDICAO da pergunta maior (CONDICOES): hoje todos sao "casado"; "descasado" e "mutavel"
             levantam NotImplementedError com o que precisam do N4 (frutas).
    dono     um dono sintetico; a rng do dono deriva de (semente, nome do dono), igual em todos os bracos e mundos.
    braco    P0..P3: o MESMO cerebro (PoliticaLobos, mesmo prior, mesma ConfigLobos); so a FONTE do sinal muda.
    semente  a do motor: rng de ambiente = semente, rng de politica = semente + 1_000_003 (engine.py, intocado).

  fontes (o campo `fonte` do braco):
    nenhuma       P0   so a predisposicao herdada: o aprendiz com o aprendizado DESLIGADO (o prior fixo). Nada do dono chega
                       a ele. Entregar "sinal nenhum" a um aprendiz ligado nao e P0: o credito do chamado expira por dentro
                       (Aprendiz._expirar) e vira sinal negativo do dono ausente.
    consequencia  P1   chega no N3 (NotImplementedError ate la).
    informacao    P2   (certa) e P2e (errada): chegam no N5 (NotImplementedError ate la).
    dono          P3   o feedback explicito (COACH): toda acao do dono chega ao aprendiz pelo gancho receber_acao_dono,
                       exatamente como na L1 (a vida e byte a byte a da L1: teste).

  modo acoplado (malha aberta; generaliza log_so_cuidado/vidas_acopladas de run_v2_l1.py): o registro de eventos de uma vida,
  com um filtro (nenhum, sem_sinais, sem_sinais_sem_carinho), e rejogado com o cerebro de outro braco, no MESMO mundo. O motor
  acoplado guarda o log filtrado: o registro dele e o da origem com os eventos retirados, evento a evento. Os eventos do mundo
  (por/tirar a bola; as ofertas de fruta do N4) nunca saem: nenhum filtro pode retira-los (o "so cuidado" da A1, que tirava a
  bola, e outra coisa e fica em run_v2_a1.py).

  cerebros: lobos (o aprendiz, todos os bracos) e instinto (a referencia herdada, so no P0: no mundo da bola e o instinto que ve
  a bola, PoliticaInstintoBola, porque os lobos ainda nao veem a bola: a regra bola_no_cenario deles e do chat B).

  medidas (todas de digilab/metrics.py; nenhuma conta aqui): desempenho no proprio ambiente (tempo fora de privacao e saude
  media, amostrados em cada decisao; acerto na tarefa do dono, `acerto_na_tarefa`), custo da plasticidade (deriva ao prior
  por dia e tempo ate a metade do caminho, `custo_da_plasticidade`) e a tabela braco x condicao (`tabela_braco_condicao`).

Toda vida e rejogada do disco e comparada bit a bit (G1): divergencia levanta erro e para tudo. engine.py e lobos.py nao
mudam. Sementes: so as dos testes (101...505) sem plano; qualquer outra exige o plano de analise registrado (campo "plano").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.ambiente import (DonoComBola, MotorAmbiente, PoliticaInstintoBola, _PoliticaComBola,  # noqa: E402
                              reproduzir_ambiente)
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_DONOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, TICKS_POR_DIA,  # noqa: E402
                            ConfigBola, ConfigLobos)
from digilab.donos import Visao, criar_dono, cuidados_necessarios, julgar_acao  # noqa: E402
from digilab.events import ACOES_BOLA, AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.evolucao import politica_no_tick  # noqa: E402
from digilab.metrics import (acerto_na_tarefa, custo_da_plasticidade, desempenho_no_ambiente,  # noqa: E402
                             distribuicoes_de_acao, estados_sonda, jsd_media, resposta_a_bola, tabela_braco_condicao)
from digilab.obediencia import MotorPersonalidade, _PoliticaObservada  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.temperamento import sortear as sortear_temperamento  # noqa: E402
from digilab.treino import CanalDeInteracao, MotorComFeedback, reproduzir_com_feedback, simular_vida  # noqa: E402

ACOES = tuple(a.value for a in AcaoPet)
SINAIS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})
SEMENTES_TESTE = frozenset({101, 202, 303, 404, 505})
CEREBROS = ("lobos", "instinto")
FILTROS = {"nenhum": frozenset(), "sem_sinais": SINAIS,
           "sem_sinais_sem_carinho": SINAIS | {AcaoUsuario.ACARICIAR.value}}
# os eventos do MUNDO no log: acoes do dono que poem coisas no cenario. O acoplado nunca os tira (as ofertas de fruta do N4 entram
# aqui quando existirem). Os filtros so tiram o que o dono ENSINA ou o carinho.
EVENTOS_DO_MUNDO = frozenset(a.value for a in ACOES_BOLA)
assert not any(f & EVENTOS_DO_MUNDO for f in FILTROS.values()), "um filtro nao pode tirar eventos do mundo"


@dataclass(frozen=True)
class Condicao:
    """Uma condicao da pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6, item 2): a relacao entre o mundo e a
    predisposicao herdada. `precisa` = o que falta (e de qual no) para a condicao existir; vazio quando ja existe."""

    nome: str
    descricao: str
    precisa: str = ""
    no: str = ""


CONDICOES = {
    "casado": Condicao("casado", "o mundo e aquele para o qual o prior foi feito: nada nele contradiz a predisposicao herdada"),
    "descasado": Condicao(
        "descasado", "o mundo contradiz o prior: a fruta preferida de nascenca faz mal",
        "do N4 (docs/DEFINICOES_FRUTAS_V2.md): a preferencia inata por fruta no genoma (F5, gene proprio com rng propria), o "
        "efeito real de cada fruta no corpo separado do gosto, com efeito ruim no humor e fora de em_privacao (F6), e as frutas "
        "do mundo com o efeito CONTRARIO a preferencia inata; as ofertas sao eventos do mundo (EVENTOS_DO_MUNDO)", "N4"),
    "mutavel": Condicao(
        "mutavel", "o mundo muda no meio da vida",
        "do N4: o mesmo que o descasado e mais a TROCA do efeito das frutas num tick da vida; a troca tem de estar no registro "
        "(como evento do mundo ou como parametro gravado da vida), para o replay e o acoplado reproduzirem", "N4"),
}


@dataclass(frozen=True)
class Mundo:
    nome: str
    condicao: str                    # a condicao da pergunta maior que este mundo realiza
    bola: str | None = None          # None: sem bola; "b1b2": a bola das decisoes B1/B2; "a1": a bola como a A1 rodou


MUNDOS = {
    "padrao": Mundo("padrao", "casado"),
    "bola": Mundo("bola", "casado", "b1b2"),
    "bola_a1": Mundo("bola_a1", "casado", "a1"),
}


def mundo_de(nome: str) -> Mundo:
    if nome in CONDICOES and CONDICOES[nome].precisa:
        c = CONDICOES[nome]
        raise NotImplementedError(f"condicao {nome!r} ({c.descricao}): precisa {c.precisa}")
    if nome not in MUNDOS:
        raise NotImplementedError(f"mundo {nome!r}: so {sorted(MUNDOS)}; descasado e mutavel chegam com o N4 (frutas)")
    m = MUNDOS[nome]
    if CONDICOES[m.condicao].precisa:          # pragma: no cover - um mundo registrado so realiza condicao que ja existe
        raise NotImplementedError(m.condicao)
    return m
MEDIDAS_TABELA = ("fracao_fora_de_privacao", "saude_media", "acerto_total", "deriva_final")
CHAVES_CONFIG = {"descricao", "plano", "bracos", "donos", "sementes", "genomas", "mundos", "dias", "orcamento", "sonda",
                 "bootstrap", "acoplados"}


class ReplayDivergiu(RuntimeError):
    pass


class SementeSemPlano(RuntimeError):
    pass


# ------------------------------------------------------------------ bracos e fonte do sinal


@dataclass(frozen=True)
class Braco:
    rotulo: str
    fonte: str                       # nenhuma | consequencia | informacao | dono
    no: str                          # o no do roadmap que liga a fonte
    informacao: str | None = None    # P2: "certa"; P2e: "errada"


BRACOS = {
    "P0": Braco("P0", "nenhuma", "N0"),
    "P1": Braco("P1", "consequencia", "N3"),
    "P2": Braco("P2", "informacao", "N5", "certa"),
    "P2e": Braco("P2e", "informacao", "N5", "errada"),
    "P3": Braco("P3", "dono", "N1"),
}
FONTES_IMPLEMENTADAS = ("nenhuma", "dono")


def braco_de(rotulo: str) -> Braco:
    if rotulo not in BRACOS:
        raise KeyError(f"braco desconhecido {rotulo!r}: {sorted(BRACOS)}")
    b = BRACOS[rotulo]
    if b.fonte not in FONTES_IMPLEMENTADAS:
        raise NotImplementedError(f"braco {b.rotulo}: a fonte {b.fonte!r} chega no {b.no} (docs/ROADMAP_V2.md)")
    return b


class PoliticaDoBraco:
    """O cerebro do braco com a fonte do sinal na frente dele. Decide, observa e serializa pelo cerebro; o que muda entre os
    bracos e so o que passa por `receber_acao_dono`: na fonte "dono" tudo, na "nenhuma" nada. Nao consome rng nem muda a
    ordem de nada: a vida do P3 e byte a byte a da L1 e a do P0 a do instinto (testes)."""

    def __init__(self, cerebro, braco: Braco) -> None:
        self.cerebro = cerebro
        self.braco = braco
        self.nome = cerebro.nome
        self.sinais_entregues = 0        # elogios e broncas que chegaram ao aprendiz (a eficiencia amostral conta estes)

    def agir(self, obs, rng):
        return self.cerebro.agir(obs, rng)

    def observar(self, transicao) -> None:
        self.cerebro.observar(transicao)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        if self.braco.fonte == "dono":
            self.sinais_entregues += acao.value in SINAIS
            self.cerebro.receber_acao_dono(acao, tick)
        elif self.braco.fonte != "nenhuma":          # pragma: no cover - braco_de ja barra
            raise NotImplementedError(self.braco.fonte)

    def estado_interno(self) -> dict:
        return {**self.cerebro.estado_interno(), "bancada": {"braco": self.braco.rotulo, "fonte": self.braco.fonte}}

    def __getattr__(self, nome):
        cerebro = self.__dict__.get("cerebro")
        if cerebro is None:
            raise AttributeError(nome)
        return getattr(cerebro, nome)


# ------------------------------------------------------------------ a vida


@dataclass(frozen=True)
class EspecVida:
    dono: str
    braco: str
    semente: int
    genoma: int | None = None
    mundo: str = "padrao"
    cerebro: str = "lobos"

    @property
    def nome(self) -> str:
        m = "" if self.mundo == "padrao" else f"~{self.mundo}"
        g = "" if self.genoma is None else f"~g{self.genoma}"
        c = "" if self.cerebro == "lobos" else f"~{self.cerebro}"
        return f"{self.dono}-{self.braco}{c}{m}{g}@{self.semente}"

    @property
    def celula(self) -> tuple:
        """O que define o par de vidas que se comparam entre bracos: tudo menos o braco."""
        return (self.dono, self.semente, self.genoma, self.mundo, self.cerebro)

    @property
    def condicao(self) -> str:
        return mundo_de(self.mundo).condicao


@dataclass
class VidaBancada:
    espec: EspecVida
    motor: MotorComFeedback
    interacoes: int                  # acoes do dono no log, fora os eventos do mundo
    origem: str | None = None        # so no modo acoplado: o nome da vida de origem, o braco dela e o filtro
    origem_braco: str | None = None
    filtro: str | None = None

    @property
    def rotulo_braco(self) -> str:
        """O braco na tabela: "P3", ou "P0<P3:sem_sinais" para o P0 acoplado ao registro do P3 sem os sinais."""
        b = self.espec.braco if self.espec.cerebro == "lobos" else f"{self.espec.braco}~{self.espec.cerebro}"
        if self.origem is None:
            return b
        return f"{b}<{self.origem_braco}:{self.filtro}"

    @property
    def eventos_mundo(self) -> int:
        return contar_acoes(self.motor.log)[1]

    @property
    def nome(self) -> str:
        if self.origem is None:
            return self.espec.nome
        e = self.espec
        return replace(e, braco=f"{e.braco}~de-{self.origem_braco}-{self.filtro}").nome


def filtrar_log(log: LogDeEventos, retirar: frozenset) -> LogDeEventos:
    """O mesmo log sem as acoes do dono em `retirar` (valores de AcaoUsuario); avancos, eventos do mundo e as outras acoes nos
    mesmos ticks. Tirar um evento do mundo falha alto: o acoplado reproduz o mundo da origem."""
    if retirar & EVENTOS_DO_MUNDO:
        raise ValueError(f"o filtro tiraria eventos do mundo: {sorted(retirar & EVENTOS_DO_MUNDO)}")
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in retirar)])


def contar_acoes(log: LogDeEventos) -> tuple[int, int]:
    """(acoes do dono fora os eventos do mundo, eventos do mundo)."""
    dono = mundo = 0
    for e in log:
        if e.tipo == "acao_usuario":
            if str(e.valor) in EVENTOS_DO_MUNDO:
                mundo += 1
            else:
                dono += 1
    return dono, mundo


def resumo_motor(motor) -> tuple:
    """Tudo que uma vida produz: log, estado final, acoes do pet, as rngs e, no motor de personalidade, obediencia, recusas,
    desejos e vinculo."""
    extra = ()
    if isinstance(motor, MotorPersonalidade):
        extra = (motor._rng_obediencia.getstate(), [r.para_dict() for r in motor.recusas],
                 [d.para_dict() for d in motor.desejos], motor.vinculo.para_dict())
    if isinstance(motor, MotorAmbiente):
        extra = extra + (motor.resumo_bola(), dict(motor.contagem), motor.morte)
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9), motor._rng_politica.getstate(),
            motor._rng_ambiente.getstate(), *extra)


def _interno(motor) -> str:
    return json.dumps(motor.politica.estado_interno(), sort_keys=True)


@dataclass(frozen=True)
class Bancada:
    dias: int
    orcamento: int
    cfg_lobos: ConfigLobos = CONFIG_LOBOS_APRENDIZ    # o aprendiz de todos os bracos (o P0 o usa com o aprendizado desligado)
    cfg_bola: ConfigBola = CONFIG_BOLA_LIGADA          # a bola dos mundos da bola (padroes calibrados na A1)

    def __post_init__(self) -> None:
        if self.dias <= 0 or self.orcamento <= 0:
            raise ValueError("dias e orcamento precisam ser positivos")
        if not self.cfg_lobos.aprendizado_ligado:
            raise ValueError("cfg_lobos e a do aprendiz (aprendizado ligado); o P0 desliga por conta propria")
        if not self.cfg_bola.ligada:
            raise ValueError("cfg_bola e a dos mundos da bola: ligada (o mundo padrao nao usa bola)")

    # ------------------------------------------------------------- fabricas

    def politica(self, espec: EspecVida, cfg=None) -> PoliticaDoBraco:
        if espec.cerebro not in CEREBROS:
            raise KeyError(f"cerebro {espec.cerebro!r}: so {CEREBROS} (outros cerebros sao a comparacao do N11)")
        b = braco_de(espec.braco)
        mundo = mundo_de(espec.mundo)
        if espec.cerebro == "instinto":
            if b.fonte != "nenhuma":
                raise ValueError(f"cerebro instinto so no P0 (nao aprende): braco {b.rotulo}")
            if mundo.bola is not None:
                return PoliticaDoBraco(PoliticaInstintoBola(cfg, self.cfg_bola), b)
            return PoliticaDoBraco(PoliticaInstinto(cfg), b)
        cl = self.cfg_lobos if b.fonte != "nenhuma" else replace(self.cfg_lobos, aprendizado_ligado=False)
        return PoliticaDoBraco(PoliticaLobos(cfg, cl), b)

    def fabrica_politica(self, espec: EspecVida):
        return lambda cfg=None: self.politica(espec, cfg)

    def fabrica_motor(self, espec: EspecVida):
        mundo = mundo_de(espec.mundo)
        if mundo.bola is not None:
            # o desenho da A1 (plano, secao 3): MotorAmbiente, obediencia, educacao e lesoes desligadas, especie brasa
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cb = self.cfg_bola
            return lambda politica, cfg, semente: MotorAmbiente(politica, cfg, semente, temperamento, "brasa",
                                                                obediencia_desligada=True, cfg_bola=cb)
        if espec.genoma is None:
            return lambda politica, cfg, semente: MotorComFeedback(politica=politica, cfg=cfg, semente=semente)
        temperamento = sortear_temperamento(espec.genoma)
        return lambda politica, cfg, semente: MotorPersonalidade(politica, cfg, semente, temperamento)

    # ------------------------------------------------------------- vidas

    def vida(self, espec: EspecVida) -> VidaBancada:
        mundo = mundo_de(espec.mundo)
        fm = self.fabrica_motor(espec)
        rotulo = f"{espec.dono}-{espec.braco}"
        if mundo.bola == "a1":
            # como a A1 rodou: o dono embrulhado poe a bola DENTRO do orcamento; o aleatorio sorteia por_bola
            v = simular_vida(rotulo, DonoComBola(espec.dono, self.cfg_bola), self.politica(espec, CONFIG_PADRAO),
                             espec.semente, self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm)
            motor = v.motor
        elif mundo.bola == "b1b2":
            motor = simular_vida_mundo(criar_dono(espec.dono), RegraBola(espec.dono, self.cfg_bola),
                                       self.politica(espec, CONFIG_PADRAO), espec.semente, self.dias, self.orcamento,
                                       espec.dono, fm)
        else:
            motor = simular_vida(rotulo, criar_dono(espec.dono), self.politica(espec, CONFIG_PADRAO), espec.semente,
                                 self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm).motor
        dono, eventos_mundo = contar_acoes(motor.log)
        orcamento_gasto = dono + (eventos_mundo if mundo.bola == "a1" else 0)
        if orcamento_gasto != self.orcamento:
            raise RuntimeError(f"{espec.nome}: {orcamento_gasto} interacoes no orcamento, orcamento {self.orcamento}")
        vida = VidaBancada(espec, motor, dono)
        self.conferir_replay(vida)
        return vida

    def rejogar(self, log: LogDeEventos, espec: EspecVida):
        fp, fm = self.fabrica_politica(espec), self.fabrica_motor(espec)
        if mundo_de(espec.mundo).bola is not None:
            return reproduzir_ambiente(log, fp, semente=espec.semente, fabrica_motor=fm)
        return reproduzir_com_feedback(log, fp, semente=espec.semente, fabrica_motor=fm)

    def acoplar(self, origem: VidaBancada, braco: str, filtro: str) -> VidaBancada:
        """Modo acoplado (malha aberta): o registro da vida de origem, sem as acoes do filtro, rejogado com o cerebro de outro
        braco (ou do mesmo). Os eventos sao os da origem nos mesmos ticks; so o cerebro (e o que ele faz deles) muda."""
        if filtro not in FILTROS:
            raise KeyError(f"filtro desconhecido {filtro!r}: {sorted(FILTROS)}")
        if origem.origem is not None:
            raise ValueError("acoplar uma vida ja acoplada nao e suportado: acople a partir da vida de origem")
        log = filtrar_log(origem.motor.log, FILTROS[filtro])
        espec = replace(origem.espec, braco=braco)
        m = self.rejogar(log, espec)
        vida = VidaBancada(espec, m, contar_acoes(log)[0], origem=origem.nome, origem_braco=origem.rotulo_braco,
                           filtro=filtro)
        self.conferir_replay(vida)
        return vida

    def conferir_replay(self, vida: VidaBancada, texto_log: str | None = None) -> None:
        """G1: rejoga a vida a partir do log serializado (do disco, se vier o texto) e compara tudo bit a bit."""
        texto = vida.motor.log.para_jsonl() if texto_log is None else texto_log
        if texto != vida.motor.log.para_jsonl():
            raise ReplayDivergiu(f"{vida.nome}: o log do disco nao e o da vida")
        r = self.rejogar(LogDeEventos.de_jsonl(texto), vida.espec)
        if resumo_motor(r) != resumo_motor(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: log, estado, acoes ou rngs divergem no replay")
        if _interno(r) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: estado interno da politica diverge no replay")

    # ------------------------------------------------------------- medidas

    def medir(self, vida: VidaBancada, sonda: dict, piso: float | None = None) -> dict:
        """Desempenho no ambiente, acerto na tarefa e custo da plasticidade de uma vida. `piso` = acerto total do P0 na mesma
        celula (o prior herdado); sem ele, o da propria vida. O replay de medicao e conferido bit a bit contra a vida."""
        regs = []

        def fab(cfg=None):
            reg = _Registro(self.politica(vida.espec, cfg))
            regs.append(reg)
            return reg

        m = reproduzir_com_feedback(LogDeEventos.de_jsonl(vida.motor.log.para_jsonl()), fab, semente=vida.espec.semente,
                                    fabrica_motor=self.fabrica_motor(vida.espec))
        if resumo_motor(m) != resumo_motor(vida.motor) or _interno(m) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao mudou a vida")
        reg = regs[0]
        bola = None
        if isinstance(m, MotorAmbiente):
            tick = CONFIG_PADRAO.intervalo_decisao_ticks
            bola = {"resposta": resposta_a_bola([(k * tick, b, r, a) for k, (b, r, a) in enumerate(reg.bola)]),
                    "contagem": dict(m.contagem_bola)}
        desempenho = desempenho_no_ambiente(reg.amostras)
        tarefa = acerto_na_tarefa(reg.decisoes, _julgar, ACOES, TICKS_POR_DIA)
        sinais = []
        for d in tarefa["dias"]:
            ate = [s for (t, _, _), s in zip(reg.decisoes, reg.sinais_na_decisao) if t < (d + 1) * TICKS_POR_DIA]
            sinais.append(ate[-1] if ate else 0)
        deriva = self.deriva(vida, sonda)
        custo = custo_da_plasticidade(deriva, tarefa["acerto"], sinais,
                                      tarefa["acerto_total"] if piso is None else piso)
        return {"vida": vida.nome, "braco": vida.rotulo_braco, "fonte": braco_de(vida.espec.braco).fonte,
                "cerebro": vida.espec.cerebro, "dono": vida.espec.dono, "semente": vida.espec.semente,
                "genoma": vida.espec.genoma, "mundo": vida.espec.mundo, "condicao": vida.espec.condicao,
                "origem": vida.origem, "filtro": vida.filtro, "interacoes": vida.interacoes,
                "eventos_mundo": vida.eventos_mundo, "bola": bola,
                **desempenho, "acerto_total": tarefa["acerto_total"], "acerto_por_dia": tarefa["acerto"],
                "teto_total": tarefa["teto_total"], "sinais_total": reg.sinais, "sinais_do_dono": reg.sinais_do_dono,
                "sinais_acumulados": sinais,
                "deriva_final": custo["deriva_final"], "custo_da_plasticidade": custo}

    def deriva(self, vida: VidaBancada, sonda: dict) -> list[float]:
        """JSD (bits) entre a politica no fim de cada dia e a do prior herdado (o P0 da mesma vida), nas mesmas sondas."""
        estados = estados_sonda(sonda["estados"], sonda["semente"])
        prior = self.politica(replace(vida.espec, braco="P0"), CONFIG_PADRAO)
        d_prior = distribuicoes_de_acao(prior, estados, sonda["amostras"], sonda["semente"])
        fab, fm = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec)
        log = vida.motor.log
        serie = []
        for d in range(1, self.dias + 1):
            # a sonda le o cerebro do braco direto: o embrulho da bola mexeria no motor e poria a bola nos estados da sonda
            pol = do_braco(politica_no_tick(log, fab, vida.espec.semente, d * TICKS_POR_DIA, fm))
            serie.append(jsd_media(distribuicoes_de_acao(pol, estados, sonda["amostras"], sonda["semente"]), d_prior))
        return serie


def do_braco(politica) -> PoliticaDoBraco:
    """A PoliticaDoBraco dentro dos embrulhos dos motores (bola, personalidade)."""
    p = politica
    while not isinstance(p, PoliticaDoBraco):
        if isinstance(p, _PoliticaComBola):
            p = p._pb
        elif isinstance(p, _PoliticaObservada):
            p = p._p
        else:
            raise TypeError(f"politica sem PoliticaDoBraco dentro: {type(p).__name__}")
    return p


# ------------------------------------------------------------------ o mundo da bola com B1 e B2


class RegraBola:
    """Decisoes B1 e B2 (2026-10-01, docs/RESULTADO_V2_A1.md): quem poe a bola e uma regra do MUNDO, fora do orcamento do dono.
    A regra dos coerentes da A1 (DonoComBola), sem a condicao do limite do passo (a bola nao gasta orcamento): atencioso e
    incoerente poem com o pet acordado, fora da noite, sem cuidado pendente, sem bola no cenario e no maximo `bolas_por_dia`
    por dia; o relapso so nos passos em que ele mesmo agiu (as visitas; B3: aceito como e). O aleatorio NAO poe bola (B1: o
    `por_bola` sai do sorteio dele, e ele nao tem outra regra). Le a visao de ANTES das acoes do dono do passo, como a A1."""

    def __init__(self, dono: str, cfg_bola: ConfigBola, cfg_donos=None, cfg=None) -> None:
        self.dono = dono
        self.cb = cfg_bola
        self.cd = cfg_donos or CONFIG_DONOS
        self.cfg = cfg or CONFIG_PADRAO
        self._dia = -1
        self._bolas_hoje = 0

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        if self.dono == "aleatorio":
            return []
        e = visao.estado
        dia = e["tick"] // TICKS_POR_DIA
        if dia != self._dia:
            self._dia, self._bolas_hoje = dia, 0
        if self.dono == "relapso" and not acoes_do_dono:
            return []
        if (self._bolas_hoje < self.cb.bolas_por_dia and not e["dormindo"] and not self.cfg.e_noite(e["tick_do_dia"])
                and e.get("bola") is None and not cuidados_necessarios(e, self.cd)):
            self._bolas_hoje += 1
            return [AcaoUsuario.POR_BOLA]
        return []


def simular_vida_mundo(dono, regra_mundo, politica, semente: int, dias: int, orcamento: int, rotulo_dono: str,
                       fabrica_motor):
    """treino.simular_vida com um canal do MUNDO fora do orcamento (B2): a cada passo o dono age pelo CanalDeInteracao (o
    orcamento exato de sempre) e depois a regra do mundo poe o que pos, direto no motor (entra no log, nao no canal). O dono
    nao ve os eventos do mundo no gasto do orcamento. Mesma rng do dono que simular_vida (derivada de semente e rotulo_dono)."""
    cfg, cd = CONFIG_PADRAO, CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cd.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cd.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono))
    canal = CanalDeInteracao(motor, orcamento, cd.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cd.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        acoes = dono.decidir(visao, rng_dono)
        canal.aplicar(acoes, passo, passos)
        for evento in regra_mundo.decidir(visao, acoes):
            if evento.value not in EVENTOS_DO_MUNDO:
                raise ValueError(f"a regra do mundo so poe eventos do mundo, nao {evento.value!r}")
            motor.observar(evento)
    canal.fechar()
    return motor


class _Registro:
    """Embrulha a politica do braco no replay de medicao: anota cada decisao (tick, estado como o dono o julga, acao), a
    amostra de estado (em privacao, saude), os sinais do dono que chegaram ao aprendiz ate ali e os que o dono deu. So le;
    repassa tudo."""

    def __init__(self, interna: PoliticaDoBraco) -> None:
        self.interna = interna
        self.nome = interna.nome
        self._tick_ultimo_cuidado = 0
        self.decisoes: list[tuple[int, dict, str]] = []
        self.amostras: list[tuple[bool, float]] = []
        self.sinais_na_decisao: list[int] = []
        self.sinais_do_dono = 0
        self.bola: list[tuple[bool, str, str]] = []      # (bola no cenario, regra do instinto/impulso, acao), por decisao

    @property
    def sinais(self) -> int:
        return self.interna.sinais_entregues

    def agir(self, obs, rng):
        acao = self.interna.agir(obs, rng)
        v = obs.vetor_estado
        estado = {"fome": v[0], "higiene": v[1], "energia": v[2], "tick_do_dia": int(round(v[7] * TICKS_POR_DIA))}
        self.decisoes.append((obs.ticks_desde_cuidado + self._tick_ultimo_cuidado, estado, acao.value))
        self.amostras.append((Estado(fome=v[0], higiene=v[1], energia=v[2]).em_privacao(CONFIG_PADRAO), v[4]))
        self.sinais_na_decisao.append(self.interna.sinais_entregues)
        self.bola.append((obs.bola > 0.0, self.interna.ultima_regra, acao.value))
        return acao

    def observar(self, transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self._tick_ultimo_cuidado = tick          # toda acao do dono zera o relogio de cuidado (state.aplicar_acao_usuario)
        self.sinais_do_dono += acao.value in SINAIS
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _julgar(estado: dict, acao: str) -> int:
    return julgar_acao({**estado, "acao_atual": acao}, CONFIG_DONOS)


# ------------------------------------------------------------------ orquestrador


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def validar_config(cfg: dict) -> dict:
    faltam = {"bracos", "donos", "sementes", "dias", "orcamento", "sonda", "bootstrap"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    for b in cfg["bracos"]:
        braco_de(b)
    for m in cfg.get("mundos", ["padrao"]):
        mundo_de(m)
    for a in cfg.get("acoplados", []):
        if set(a) != {"origem", "destino", "filtro"} or a["filtro"] not in FILTROS:
            raise ValueError(f"acoplado fora do formato: {a}")
        braco_de(a["destino"])
        if a["origem"] not in cfg["bracos"]:
            raise ValueError(f"acoplado de um braco que nao roda: {a['origem']}")
    genomas = [g for g in cfg.get("genomas", [None]) if g is not None]
    fora = sorted((set(cfg["sementes"]) | set(genomas)) - SEMENTES_TESTE)
    if fora:
        plano = cfg.get("plano")
        if not plano or not (RAIZ / plano).is_file():
            raise SementeSemPlano(f"sementes {fora} fora das dos testes {sorted(SEMENTES_TESTE)}: precisa do plano de analise "
                                  "registrado (campo 'plano', arquivo no repositorio)")
    return cfg


def rodar(cfg: dict, pasta: Path) -> dict:
    """Vidas de todos os bracos x donos x sementes (x genomas x mundos), gravadas e rejogadas do disco; os acoplados; as
    medidas por vida e as tabelas braco x condicao por dono e medida."""
    validar_config(cfg)
    bancada = Bancada(int(cfg["dias"]), int(cfg["orcamento"]))
    dir_vidas = pasta / "vidas"
    vidas: dict[str, VidaBancada] = {}

    def guardar(v: VidaBancada) -> None:
        _gravar(dir_vidas / f"{v.nome}.jsonl", v.motor.log.para_jsonl())
        _gravar(dir_vidas / f"{v.nome}.politica.json", _interno(v.motor))
        bancada.conferir_replay(v, (dir_vidas / f"{v.nome}.jsonl").read_text(encoding="utf-8"))
        vidas[v.nome] = v

    for g, mundo, dono, braco, s in product(cfg.get("genomas", [None]), cfg.get("mundos", ["padrao"]), cfg["donos"],
                                            cfg["bracos"], cfg["sementes"]):
        guardar(bancada.vida(EspecVida(dono, braco, int(s), g, mundo)))
    origens = list(vidas.values())
    for a in cfg.get("acoplados", []):
        for v in origens:
            if v.espec.braco == a["origem"]:
                guardar(bancada.acoplar(v, a["destino"], a["filtro"]))
    # o piso do tempo ate aprender e o acerto do P0 na mesma celula (o prior herdado); sem P0 na config, o da propria vida
    medidas, piso = {}, {}
    for nome, v in sorted(vidas.items()):
        if v.espec.braco == "P0" and v.origem is None:
            medidas[nome] = bancada.medir(v, cfg["sonda"])
            piso[v.espec.celula] = medidas[nome]["acerto_total"]
    for nome, v in sorted(vidas.items()):
        if nome not in medidas:
            medidas[nome] = bancada.medir(v, cfg["sonda"], piso.get(v.espec.celula))
    tabelas = tabelas_braco_condicao(medidas, cfg["bootstrap"])
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "tabelas.json", _dump(tabelas))
    _gravar(pasta / "meta.json", _dump(meta(cfg)))
    return {"vidas": vidas, "medidas": medidas, "tabelas": tabelas}


def tabelas_braco_condicao(medidas: dict, boot: dict) -> dict:
    """Por dono e medida: tabela braco x condicao, unidade = vida (semente x genoma). A coluna e "condicao/mundo" (hoje
    "casado/padrao" e "casado/bola"): dois mundos da mesma condicao nunca se misturam numa celula."""
    out = {}
    for dono in sorted({m["dono"] for m in medidas.values()}):
        out[dono] = {}
        for medida in MEDIDAS_TABELA:
            valores: dict[tuple[str, str], list[float]] = {}
            for m in medidas.values():
                if m["dono"] == dono:
                    valores.setdefault((m["braco"], f"{m['condicao']}/{m['mundo']}"), []).append(m[medida])
            out[dono][medida] = tabela_braco_condicao(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
    return out


def meta(cfg: dict) -> dict:
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    return {"config": cfg, "python": platform.python_version(), "plataforma": platform.platform(),
            "engine_sha256": sha256_engine(), "lobos_sha256": _sha(RAIZ / "digilab" / "policies" / "lobos.py"),
            "config_sha256": _sha(RAIZ / "digilab" / "config.py"), "bancada_sha256": _sha(Path(__file__)),
            "metrics_sha256": _sha(RAIZ / "digilab" / "metrics.py")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="bancada da V2: bracos P0-P3 sobre o mesmo aprendiz (docs/TAREFA_V2_BANCADA.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True, help="pasta de saida (vidas/, medidas.json, tabelas.json, meta.json)")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, Path(a.saida))
    print(f"{len(r['vidas'])} vidas rejogadas do disco bit a bit; medidas e tabelas em {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
