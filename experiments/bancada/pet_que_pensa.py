"""A bancada da V2, módulo `pet_que_pensa`.

O pet que pensa (J5): a bancada.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA, ConfigFrutas, ConfigLobos, ConfigMundo
from digilab.config import ConfigCorpo
from digilab.motor_corpo import com_corpo
from digilab.donos import criar_dono
from digilab.events import FRUTAS, AcaoUsuario, LogDeEventos
from digilab.metrics import deficit_fome_energia
from digilab.mundo import alvo_padrao_de
from digilab.events import ACOES_MAO, ACOES_TROCA_ARVORES, dar_fruta, fruta_dada, trocar_arvores
from digilab.config import CONFIG_PQP_MUNDO_LIGADA, CONFIG_MODELO_MUNDO_LIGADA, ConfigModeloMundo
from digilab.modelo_mundo import TIPOS as MODELO_TIPOS, PoliticaComModelo
from digilab.metrics import busca_transicao, exposto_transicao, mudanca_de_escolha, oportunidade_revalorizacao
from digilab.mundo import ESTILOS_LUGAR, DonoComLugar, MotorMundo, reproduzir_mundo
from digilab.policies import PoliticaLobos
from digilab.policies.lobos import arred
from digilab.policies.lobos import LOBO_PLANEJAMENTO
from digilab.motivo import Motivo, fator_do_plano, nome_base
from digilab.expressao import expressar
from digilab.protocol import derivar_semente
from digilab.temperamento import NEUTRO

from . import RAIZ


# ================================================================== o pet que pensa (J5): a bancada (TAREFA_V2_PET_QUE_PENSA, etapa 4)
# docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, secoes 2 a 4 e 8 (PP-1 a PP-9). A vida de uma unidade: o mundo fisico do layout padrao (a x faz
# bem, as outras duas neutras), o corpo do regime quimica com o metabolismo (PP-3), o dono atencioso so com o cuidado no comedouro (PMF-3,
# PMF-4) e o cerebro A do P1 (a consequencia com a E2, no ponto e na montagem da config) com o alvo aprendido (#255), a presenca da fruta
# no mundo (#269) e as classes por arvore (#291, PP-2). O mundo do J5 (#291: os troncos vistos, os candidatos de arvore, a fruta na mao e a
# troca de tipo) liga em toda vida. Os modelos do mundo ficam em todo braco, pelo embrulho `PoliticaComModeloPQP`, que os congela no tick
# da mudanca (PP-8) pelo `congelar` deles: no P1 (g_plano 0) sao modelos que so observam (#289); nos tres bracos com o planejador (#294,
# o `g_plano` da config) sao os do proprio cerebro, que os le no lobo `planejamento`.
#
# Os protocolos (secao 3): a fase 1 sao os `D_a` dias de aprendizado, iguais nos dois testes; no tick da mudanca (T_m, o primeiro passo do
# dono a partir das 8 h do dia D_a com o pet acordado, PP-5), o T1 troca o efeito da x para "faz mal" e da a x na mao `n_mao` vezes; o T2
# troca o tipo das arvores da x e da y. Os eventos da mudanca vem pela regra do mundo (`RegraMudancaPQP`), fora do orcamento, e ficam no
# log; o replay os refaz. A troca do efeito do T1 fica presa a primeira fruta na mao (`MotorMundoMudanca`): T_m depende da vida (o pet
# acordado), entao o motor nao a sabe ao nascer, e a primeira mao e o evento do log que a marca.
#
# As medidas (secao 4) saem do replay de medicao (conferido bit a bit contra a vida), so da percepcao do pet e do que o motor registra,
# pelas funcoes de digilab/metrics.py: as oportunidades do T1, as buscas e a exposicao do T2, o corte da reexperiencia e as primarias q e
# m. Os modelos nunca sao lidos pela medida das oportunidades. Do motivo do cerebro saem quanto o plano decide (a sonda "quem decidiu",
# por dia), a legibilidade (o fator do plano e os textos dele) e o G2 do plano (no P1, o termo do plano e zero em toda decisao).

PLANO_PQP = "docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md"
PREFIXO_PQP = "pet_que_pensa"
BASES_PET_QUE_PENSA = {"calibracao": (45101, 45202, 45303, 45404, 45505), "validacao": (46101, 46202, 46303, 46404, 46505)}
ROTULO_X_PQP = "pet-que-pensa-x"            # a fruta x da unidade (plano, secao 2)
ROTULO_Y_PQP = "pet-que-pensa-y"            # a fruta y do T2, entre as outras duas
D_A_PQP = 7                                 # PP-4: os dias de aprendizado
JANELA_PQP = 3                              # PP-4: os dias da janela do teste
N_MAO_PQP = 2                               # PP-5: as frutas na mao
HORA_MUDANCA_PQP = 8 * 60                   # PP-5: T_m e o primeiro passo do dono a partir das 8 h do dia D_a com o pet acordado
N_OPORTUNIDADES_PQP = 3                     # PP-4 e PP-7: as 3 ultimas antes e as 3 primeiras depois
PROTOCOLOS_PQP = ("T1", "T2", "fase1")      # "fase1": so os D_a dias, sem mudanca (a calibracao do g_plano, secao 5)
CONGELA_PQP = ("mapa", "desfecho")


@dataclass(frozen=True)
class BracoPQP:
    """Um braco do plano do J5 (secao 3): o mesmo cerebro A e o mesmo habito; muda o planejador e o que congela no tick da mudanca."""

    rotulo: str
    planejador: bool                 # o g_plano da config (o da calibracao); com False, g_plano 0: os modelos so observam
    congela: tuple = ()              # o que para de aprender no tick da mudanca: "mapa", "desfecho"


BRACOS_PQP = {
    "P1": BracoPQP("P1", False),
    "P1-plan": BracoPQP("P1-plan", True),
    "P1-plan-desfecho": BracoPQP("P1-plan-desfecho", True, ("mapa",)),            # PP-8: o mapa congelado na mudanca
    "P1-plan-cong": BracoPQP("P1-plan-cong", True, ("mapa", "desfecho")),
}


def braco_pqp(rotulo: str) -> BracoPQP:
    if rotulo not in BRACOS_PQP:
        raise KeyError(f"braco do J5 {rotulo!r}: so {sorted(BRACOS_PQP)}")
    return BRACOS_PQP[rotulo]


def fruta_x_pqp(semente: int) -> str:
    """A fruta x da unidade: uniforme entre a, b e c, pela rng propria (plano, secao 2). Um sorteio; nao toca outra rng."""
    return FRUTAS[random.Random(derivar_semente(ROTULO_X_PQP, semente)).randrange(len(FRUTAS))]


def fruta_y_pqp(semente: int) -> str:
    """A fruta y do T2: uniforme entre as outras duas, pela rng propria (plano, secao 2)."""
    outras = [f for f in FRUTAS if f != fruta_x_pqp(semente)]
    return outras[random.Random(derivar_semente(ROTULO_Y_PQP, semente)).randrange(len(outras))]


def efeitos_pqp(x: str, cf: ConfigFrutas, faz_mal: bool = False) -> dict:
    """O efeito de cada fruta no humor: antes da mudanca a x faz bem (-efeito_humor_ruim, o "bem" do casado) e as outras sao neutras; com
    `faz_mal`, a x passa ao efeito ruim (o T1 depois da mudanca)."""
    return {f: (cf.efeito_humor_ruim if faz_mal else -cf.efeito_humor_ruim) if f == x else cf.efeito_humor_neutro for f in FRUTAS}


class MotorMundoMudanca(MotorMundo):
    """O MotorMundo do J5: avisa o cerebro da mudanca do teste e, no T1, troca o efeito da x. A primeira acao da mudanca no log (a fruta na
    mao no T1, a troca de tipo no T2) marca o tick (`mudanca`) e chama o gancho opcional `mudanca_no_mundo(tick)` do cerebro antes de
    aplicar a acao (o congelamento dos modelos, PP-8). Com `revaloriza` (o T1), a primeira fruta na mao troca antes o efeito da x para
    `efeito_depois` (`revaloracao`); uma fruta na mao de outro tipo falha alto. O replay refaz tudo pelo log e pela mesma fabrica."""

    def __init__(self, *a, revaloriza: str | None = None, efeito_depois: dict | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        if not (self.cmf.ligada and self.cpq.ligada):
            raise ValueError("o MotorMundoMudanca e do J5: o mundo fisico e a ConfigPetQuePensaMundo ligados")
        if (revaloriza is None) != (efeito_depois is None):
            raise ValueError("revaloriza e efeito_depois vao juntos (o T1)")
        if revaloriza is not None and (revaloriza not in FRUTAS or set(efeito_depois) != set(FRUTAS)):
            raise ValueError(f"revaloracao invalida: {revaloriza!r}, {efeito_depois!r}")
        self.revaloriza = revaloriza
        self.efeito_depois = None if efeito_depois is None else dict(efeito_depois)
        self.mudanca: dict | None = None          # {"tick": do mundo, "evento": o primeiro evento da mudanca}
        self.revaloracao: dict | None = None      # {"tick", "antes", "depois"} (so no T1)

    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if acao in ACOES_MAO or acao in ACOES_TROCA_ARVORES:
            tm = self._tm(self._estado.tick)
            if self.mudanca is None:
                self.mudanca = {"tick": tm, "evento": acao.value}
                gancho = getattr(self._pm_cerebro(), "mudanca_no_mundo", None)
                if gancho is not None:
                    gancho(tm)
            if acao in ACOES_MAO and self.revaloriza is not None:
                if fruta_dada(acao) != self.revaloriza:
                    raise ValueError(f"fruta na mao {fruta_dada(acao)!r} no T1 da x {self.revaloriza!r}")
                if self.revaloracao is None:
                    self.revaloracao = {"tick": tm, "antes": dict(self.efeito_frutas), "depois": dict(self.efeito_depois)}
                    self.efeito_frutas = dict(self.efeito_depois)
        super()._aplicar_acao_usuario(acao)

    def resumo_mundo_fisico(self) -> dict:
        return {**super().resumo_mundo_fisico(), "mudanca": self.mudanca, "revaloracao": self.revaloracao}


class PoliticaComModeloPQP(PoliticaComModelo):
    """Os modelos do mundo em todo braco do J5, com o congelamento da PP-8 pelo `congelar` dos proprios modelos (#294).

    Sem o planejador (o P1, g_plano 0), o embrulho guarda modelos que so observam (#289): a decisao, a consequencia e a fruta na mao chegam
    a eles, e a vida nao muda. Com o planejador, os modelos sao os do cerebro (`PoliticaLobos.modelo_mundo`), que os alimenta sozinho (na
    decisao, na consequencia e na mao) e os le no lobo `planejamento`; o embrulho so os le e os congela, sem passo a mais.

    No tick da mudanca (o gancho `mudanca_no_mundo` do MotorMundoMudanca, antes de a acao da mudanca ser aplicada), as partes de `congela`
    param de aprender ("mapa": o mapa e os lugares vistos; "desfecho": o desfecho e o custo de andar) e o retrato delas fica para o gate
    (`congelamento_conferido`). A fruta na mao nunca chega ao credito (G-SEM-CREDITO: o A so a passa aos modelos). O estado interno ganha
    os modelos (`modelo_mundo`), para o G1 os conferir."""

    def __init__(self, interna, cfg_mundo: ConfigMundo, cfg=None, congela: tuple = ()) -> None:
        if set(congela) - set(CONGELA_PQP) or len(set(congela)) != len(congela):
            raise ValueError(f"congela {congela!r}: so {CONGELA_PQP}, sem repetir")
        proprio = getattr(interna, "modelo_mundo", None)
        if proprio is None:
            super().__init__(interna, cfg_mundo, cfg)
        else:
            if cfg is not None and proprio.cfg != cfg:
                raise ValueError("os modelos do cerebro com o planejador nao tem a ConfigModeloMundo da bancada")
            self._interna = interna
            self.modelo = proprio
        self.do_cerebro = proprio is not None
        self.congela = tuple(congela)
        self.tick_congelamento: int | None = None
        self.retrato_congelamento: dict | None = None
        self.maos = 0
        self.maos_ignoradas = 0

    @property
    def congelado(self) -> tuple:
        return tuple(self.modelo.congelados)

    def _partes(self) -> dict:
        m = self.modelo
        return {"mapa": json.dumps({"mapa": m.mapa, "lugares_vistos": m.lugares_vistos}, sort_keys=True),
                "desfecho": json.dumps({"desfecho": m.desfecho, "andar": m.andar}, sort_keys=True)}

    def mudanca_no_mundo(self, tick: int) -> None:
        if self.tick_congelamento is None:
            self.tick_congelamento = tick
            if self.congela:
                self.modelo.congelar(*self.congela)
            self.retrato_congelamento = self._partes()
        gancho = getattr(self._interna, "mudanca_no_mundo", None)
        if gancho is not None:
            gancho(tick)

    def agir(self, obs, rng):
        if self.do_cerebro:
            return self._interna.agir(obs, rng)       # o cerebro passa a decisao aos modelos dele
        return super().agir(obs, rng)

    def consequencia_mundo(self, acao, ocorrido: dict, obs_depois) -> None:
        if self.do_cerebro:
            self._interna.consequencia_mundo(acao, ocorrido, obs_depois)
            return
        super().consequencia_mundo(acao, ocorrido, obs_depois)

    def fruta_na_mao(self, tipo: str, obs_antes, obs_depois) -> None:
        self.maos += 1
        if "desfecho" in self.modelo.congelados:
            self.maos_ignoradas += 1
        if self.do_cerebro:
            self._interna.fruta_na_mao(tipo, obs_antes, obs_depois)
            return
        super().fruta_na_mao(tipo, obs_antes, obs_depois)

    def congelamento_conferido(self) -> dict:
        """O gate de mecanismo (secao 7): as partes congeladas sao, no fim da vida, as do tick da mudanca. Falha alto se nao forem."""
        if self.tick_congelamento is None:
            return {"tick": None, "partes": [], "conferido": not self.congela}
        if self.congelado != tuple(sorted(self.congela)):
            raise RuntimeError(f"congelamento: os modelos tem {self.congelado}, o braco congela {self.congela} (PP-8)")
        agora = self._partes()
        mudaram = [p for p in self.congelado if agora[p] != self.retrato_congelamento[p]]
        if mudaram:
            raise RuntimeError(f"congelamento: {mudaram} mudaram depois da mudanca (tick {self.tick_congelamento}; PP-8)")
        return {"tick": self.tick_congelamento, "partes": list(self.congelado), "conferido": True,
                "ignoradas": dict(self.modelo.ignoradas)}

    def estado_interno(self) -> dict:
        return {**self._interna.estado_interno(),
                "modelo_mundo": {**self.modelo.para_dict(), "do_cerebro": self.do_cerebro, "congela": list(self.congela),
                                 "tick_congelamento": self.tick_congelamento, "maos": self.maos, "maos_ignoradas": self.maos_ignoradas}}


class RegraMudancaPQP:
    """A regra do mundo do J5 (secao 3): no primeiro passo do dono a partir das 8 h do dia `d_a` com o pet acordado (T_m), o T1 da a x na
    mao `n_mao` vezes (o MotorMundoMudanca troca o efeito na primeira) e o T2 troca o tipo das arvores da x e da y. A fase 1 nao muda nada.
    Fora do orcamento (simular_vida_fisico, `mudanca`)."""

    def __init__(self, protocolo: str, x: str, y: str | None, d_a: int, n_mao: int) -> None:
        if protocolo not in PROTOCOLOS_PQP:
            raise ValueError(f"protocolo {protocolo!r}: so {PROTOCOLOS_PQP}")
        if protocolo == "T2" and (y is None or y == x):
            raise ValueError("o T2 precisa de uma fruta y diferente da x")
        self.protocolo, self.x, self.y, self.d_a, self.n_mao = protocolo, x, y, d_a, n_mao
        self.tick: int | None = None
        self.eventos: list[str] = []

    def acoes(self, estado: dict) -> list:
        if self.protocolo == "fase1" or self.tick is not None:
            return []
        if estado["tick"] < self.d_a * TICKS_POR_DIA + HORA_MUDANCA_PQP or estado["dormindo"]:
            return []
        self.tick = estado["tick"]
        acoes = [dar_fruta(self.x)] * self.n_mao if self.protocolo == "T1" else [trocar_arvores(self.x, self.y)]
        self.eventos = [a.value for a in acoes]
        return acoes


@dataclass(frozen=True)
class EspecPQP:
    braco: str
    protocolo: str
    semente: int

    @property
    def nome(self) -> str:
        return f"{self.braco}~{self.protocolo}@{self.semente}"


@dataclass
class VidaPQP:
    espec: EspecPQP
    motor: MotorMundo
    x: str
    y: str | None
    tick_mudanca: int | None
    eventos_mudanca: list
    dono: int                        # as acoes do dono no orcamento
    retirados: int                   # os sinais que o filtro sem_ensino nao deixou chegar (PMF-3)
    cpu_s: float

    @property
    def nome(self) -> str:
        return self.espec.nome


def _arvores_do_layout(cm: ConfigMundo) -> dict:
    """id -> (x, y em subunidades, no centro da celula, a fruta no layout): a arvore como o motor a poe (as velhas e as novas do T2)."""
    return {ident: (x * cm.sub + cm.sub // 2, y * cm.sub + cm.sub // 2, fruta) for ident, x, y, fruta in cm.layout.arvores}


@dataclass(frozen=True)
class BancadaPQP:
    """A bancada do J5 sobre a Bancada da config (o ponto, a montagem, os lobos, a consequencia, o mundo e o corpo dela). `dias` e
    `orcamento` da Bancada sao os da vida inteira dos testes (D_a + a janela); a fase 1 usa os D_a dias com o mesmo orcamento por dia."""

    bancada: Bancada
    d_a: int = D_A_PQP
    janela: int = JANELA_PQP
    n_mao: int = N_MAO_PQP
    dono: str = "atencioso"
    lugar: str = "comedouro"
    cfg_modelo: ConfigModeloMundo = CONFIG_MODELO_MUNDO_LIGADA
    g_plano: int = 0                 # o ganho do plano dos bracos com o planejador (a calibracao, PP-6); o P1 tem sempre 0

    def __post_init__(self) -> None:
        if self.d_a < 1 or self.janela < 1 or self.n_mao < 1:
            raise ValueError("d_a, janela e n_mao precisam ser positivos")
        if type(self.g_plano) is not int or self.g_plano < 0:
            raise ValueError(f"g_plano do J5 precisa ser inteiro >= 0: {self.g_plano!r}")
        if self.bancada.cfg_lobos.g_plano != 0:
            raise ValueError("o g_plano do J5 e da BancadaPQP (so nos bracos com o planejador), nunca da chave 'lobos' (o P1 o teria)")
        if self.bancada.dias != self.d_a + self.janela:
            raise ValueError(f"a Bancada vive {self.bancada.dias} dias; o J5 vive d_a + janela = {self.d_a + self.janela}")
        if self.lugar not in ESTILOS_LUGAR:
            raise ValueError(f"lugar {self.lugar!r}: so {ESTILOS_LUGAR}")
        criar_dono(self.dono)

    def dias_da_vida(self, protocolo: str) -> int:
        return self.d_a if protocolo == "fase1" else self.d_a + self.janela

    def cfg_corpo(self) -> ConfigCorpo:
        """PP-3: o regime quimica com o metabolismo (os numeros do passo 0 vem da chave "corpo" da config)."""
        return replace(self.bancada.cfg_corpo, drives_novos=False, gestos=False, metabolismo=True)

    def cfg_lobos(self, espec: EspecPQP) -> ConfigLobos:
        """O cerebro A do P1 (secao 2) com o habito do plano: o alvo aprendido, a presenca da fruta no mundo e as classes por arvore. Nos
        bracos com o planejador, o `g_plano` da bancada (sem ele, falha alto); no P1, 0."""
        b = braco_pqp(espec.braco)
        if b.planejador and self.g_plano == 0:
            raise ValueError(f"braco {espec.braco}: o planejador precisa do g_plano (a chave 'g_plano' da config)")
        cl = replace(self.bancada.cfg_lobos, alvo_aprendido=True, presenca_fruta_mundo=True, alvo_por_arvore=True,
                     g_plano=self.g_plano if b.planejador else 0)
        return cfg_lobos_do_braco(cl, self.braco_montado(), espec.semente, self.bancada.montagem)

    def braco_montado(self) -> Braco:
        return braco_montado(braco_de("P1"), self.bancada.montagem, False)

    def politica(self, espec: EspecPQP, cfg=None) -> PoliticaDoBraco:
        """O cerebro A do braco na fonte consequencia. Com o planejador, o lobo `planejamento` (#294) com o `g_plano` da bancada, os
        modelos da `cfg_modelo` e a ConfigConsequencia do credito (a mesma: o cerebro a confere em toda decisao)."""
        bp = braco_pqp(espec.braco)
        b = self.braco_montado()
        bc = self.bancada
        cb, cf = bc.pesos_do_mundo()
        cc = bc.cfg_consequencia if b.canais is None else replace(bc.cfg_consequencia, canais_ligados=b.canais)
        plano = {"cfg_modelo": self.cfg_modelo, "cfg_consequencia": cc} if bp.planejador else {}
        cerebro = PoliticaLobos(cfg, self.cfg_lobos(espec), cfg_bola=cb, cfg_frutas=cf, cfg_mundo=bc.cfg_mundo, cfg_corpo=self.cfg_corpo(),
                                **plano)
        if bp.planejador and cerebro.modelo_mundo is None:
            raise RuntimeError(f"braco {espec.braco}: o cerebro nao tem o planejador")
        return PoliticaDoBraco(PoliticaComModeloPQP(cerebro, bc.cfg_mundo, self.cfg_modelo, bp.congela), b, cc)

    def fabrica_motor(self, espec: EspecPQP):
        x = fruta_x_pqp(espec.semente)
        cf = self.bancada.cfg_frutas
        kw = {"revaloriza": x, "efeito_depois": efeitos_pqp(x, cf, faz_mal=True)} if espec.protocolo == "T1" else {}
        cm, corpo, efeito = self.bancada.cfg_mundo, self.cfg_corpo(), efeitos_pqp(x, cf)
        return lambda politica, cfg, semente: com_corpo(MotorMundoMudanca)(
            politica, cfg, semente, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=cm, efeito_frutas=efeito,
            cfg_corpo=corpo, cfg_pqp=CONFIG_PQP_MUNDO_LIGADA, **kw)

    def vida(self, espec: EspecPQP) -> VidaPQP:
        if espec.protocolo not in PROTOCOLOS_PQP:
            raise ValueError(f"protocolo {espec.protocolo!r}: so {PROTOCOLOS_PQP}")
        dias = self.dias_da_vida(espec.protocolo)
        orcamento = self.bancada.orcamento_por_dia() * dias
        x = fruta_x_pqp(espec.semente)
        y = fruta_y_pqp(espec.semente) if espec.protocolo == "T2" else None
        regra = RegraMudancaPQP(espec.protocolo, x, y, self.d_a, self.n_mao)
        dono = DonoComLugar(criar_dono(self.dono), self.lugar, espec.semente, self.dono, self.bancada.cfg_mundo)
        cpu = time.process_time()
        motor, retirados = simular_vida_fisico(dono, self.politica(espec, CONFIG_PADRAO), espec.semente, dias, orcamento, self.dono,
                                               self.fabrica_motor(espec), mudanca=regra)
        cpu = time.process_time() - cpu
        if espec.protocolo != "fase1" and regra.tick is None:
            raise RuntimeError(f"{espec.nome}: a mudanca nao aconteceu (o pet nunca acordado a partir das 8 h do dia {self.d_a})")
        n_mudanca = sum(1 for e in motor.log if e.tipo == "acao_usuario"
                        and (AcaoUsuario(e.valor) in ACOES_MAO or AcaoUsuario(e.valor) in ACOES_TROCA_ARVORES))
        if n_mudanca != len(regra.eventos):
            raise RuntimeError(f"{espec.nome}: {n_mudanca} eventos da mudanca no log, a regra deu {len(regra.eventos)}")
        dono_n = contar_acoes(motor.log)[0] + contar_gestos_mundo(motor.log) - n_mudanca
        if dono_n + retirados != orcamento:
            raise RuntimeError(f"{espec.nome}: {dono_n + retirados} interacoes no orcamento, orcamento {orcamento}")
        if regra.tick is not None and (motor.mudanca is None or motor.mudanca["tick"] != regra.tick):
            raise RuntimeError(f"{espec.nome}: a mudanca do motor ({motor.mudanca}) nao e a da regra (tick {regra.tick})")
        vida = VidaPQP(espec, motor, x, y, regra.tick, list(regra.eventos), dono_n, retirados, cpu)
        self.conferir_replay(vida)
        return vida

    def rejogar(self, log: LogDeEventos, espec: EspecPQP, fabrica_politica=None, envolver_motor=None):
        fp = fabrica_politica or (lambda cfg=None: self.politica(espec, cfg))
        fm = self.fabrica_motor(espec)
        if envolver_motor is not None:
            fm0 = fm

            def fm(*a, **kw):
                m = fm0(*a, **kw)
                envolver_motor(m)
                return m
        return reproduzir_mundo(log, fp, semente=espec.semente, fabrica_motor=fm)

    def conferir_replay(self, vida: VidaPQP, texto_log: str | None = None) -> None:
        """G1: rejoga a vida do log (do disco, se vier o texto) e compara tudo bit a bit, os modelos do mundo incluidos."""
        texto = vida.motor.log.para_jsonl() if texto_log is None else texto_log
        if texto != vida.motor.log.para_jsonl():
            raise ReplayDivergiu(f"{vida.nome}: o log do disco nao e o da vida")
        r = self.rejogar(LogDeEventos.de_jsonl(texto), vida.espec)
        if resumo_motor(r) != resumo_motor(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: log, estado, acoes, rngs ou o mundo divergem no replay")
        if _interno(r) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: estado interno da politica (cerebro e modelos) diverge no replay")

    # ------------------------------------------------------------- medidas
    def medir(self, vida: VidaPQP) -> dict:
        """As medidas da secao 4, do replay de medicao (conferido contra a vida): as oportunidades do T1 ou as buscas do T2, com o corte da
        reexperiencia, as primarias q e m, e os descritivos (os modelos por dia, o desempenho, o custo, as oportunidades). Os gates de
        mecanismo (secao 7) falham alto: o G-SEM-CREDITO (o cerebro inteiro igual antes e depois de cada fruta na mao) e o congelamento."""
        espec, cm = vida.espec, self.bancada.cfg_mundo
        regs: list = []

        def fp(cfg=None):
            r = _RegistroPQP(self.politica(espec, cfg), cm, self.cfg_modelo)
            regs.append(r)
            return r
        motor = self.rejogar(vida.motor.log, espec, fp, lambda m: setattr(regs[-1], "motor", m))
        if resumo_motor(motor) != resumo_motor(vida.motor) or _interno(motor) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao diverge da vida")
        reg = regs[-1]
        reg._retratar_dias(self.dias_da_vida(espec.protocolo) * TICKS_POR_DIA)    # o retrato do fim do ultimo dia
        modelo = reg.modelo_pqp()
        congelamento = modelo.congelamento_conferido()
        if reg.violacoes_sem_credito:
            raise RuntimeError(f"{vida.nome}: G-SEM-CREDITO, o cerebro mudou numa fruta na mao ({reg.violacoes_sem_credito})")
        x, y = vida.x, vida.y
        arvores = _arvores_do_layout(cm)
        S, fome_max = self.cfg_modelo.escala, self.cfg_modelo.escala // 2
        planejador = braco_pqp(espec.braco).planejador
        out = {"braco": espec.braco, "protocolo": espec.protocolo, "semente": espec.semente, "x": x, "y": y,
               "g_plano": reg.cerebro_a().cl.g_plano, "tick_mudanca": vida.tick_mudanca, "eventos_mudanca": vida.eventos_mudanca,
               "decisoes": len(reg.decisoes), "congelamento": congelamento, "g_sem_credito": {"maos": reg.maos, "violacoes": 0},
               "maos_no_modelo": modelo.maos - modelo.maos_ignoradas}
        out.update(plano_da_vida(reg.decisoes, reg.cerebro_a().motivos, planejador, self.dias_da_vida(espec.protocolo)))
        if espec.protocolo == "T1":
            linhas = []
            for d in reg.decisoes:
                op, esc = oportunidade_revalorizacao(d["fome"], d["maduros"], d["troncos"], d["alvo"], x, fome_max)
                linhas.append({"tick": d["tick"], "depois": d["depois"], "conta": op, "sucesso": esc, "reexperiencia": d["comeu"] == x})
            out["t1"] = mudanca_de_escolha(linhas, N_OPORTUNIDADES_PQP, vida.tick_mudanca)
            out["t1"]["q"] = out["t1"]["queda"]
        elif espec.protocolo == "T2":
            velhas = {i for i, (_ax, _ay, f) in arvores.items() if f == x}
            novas = {i for i, (_ax, _ay, f) in arvores.items() if f == y}
            pos_novas = [(ax, ay) for i, (ax, ay, _f) in arvores.items() if i in novas]
            raio = self.cfg_modelo.raio_ancora_celulas * cm.sub
            exposicao, linhas = None, []
            for d in reg.decisoes:
                if d["depois"] and exposicao is None and exposto_transicao(d["x"], d["y"], d["vistos"], pos_novas, x, raio):
                    exposicao = d["tick"]
                    linhas.append({"tick": d["tick"], "depois": True, "conta": False, "sucesso": False, "reexperiencia": d["comeu"] == x})
                    continue
                busca, nova = busca_transicao(d["fome"], d["maduros"], d["alvo"], x, velhas, novas, fome_max)
                conta = busca and (not d["depois"] or exposicao is not None)
                linhas.append({"tick": d["tick"], "depois": d["depois"], "conta": conta, "sucesso": nova, "reexperiencia": d["comeu"] == x})
            out["t2"] = {**mudanca_de_escolha(linhas, N_OPORTUNIDADES_PQP, vida.tick_mudanca), "exposicao": exposicao,
                         "sem_exposicao": exposicao is None, "velhas": sorted(velhas), "novas": sorted(novas)}
            out["t2"]["m"] = out["t2"]["subida"]
        fase1_fim = self.d_a * TICKS_POR_DIA
        fim = self.dias_da_vida(espec.protocolo) * TICKS_POR_DIA
        fe = [(d["tick"], d["fome01"], d["energia01"]) for d in reg.decisoes]
        out["desempenho"] = {"d_fe_fase1": deficit_fome_energia(fe, (0, fase1_fim))["d_fe"],
                             "d_fe_janela": None if fim == fase1_fim else deficit_fome_energia(fe, (fase1_fim, fim))["d_fe"],
                             "humor_janela": None if fim == fase1_fim else _media([d["humor01"] for d in reg.decisoes
                                                                                   if fase1_fim <= d["tick"] < fim])}
        out["modelos_por_dia"] = reg.modelos_por_dia
        out["modelos_contra_o_real"] = modelos_contra_o_real(reg.modelos_por_dia, vida.motor, x, S)
        out["custo"] = {"cpu_s": vida.cpu_s, "us_por_decisao": 1e6 * vida.cpu_s / max(1, len(reg.decisoes)),
                        "bytes_log_por_dia": len(vida.motor.log.para_jsonl().encode("utf-8")) / self.dias_da_vida(espec.protocolo)}
        out["nao_medidos"] = {"deriva": "nao medida nesta etapa (a JSD ao prior do A com o embrulho dos modelos fica para o orquestrador)"}
        return out


def _media(xs: list) -> float | None:
    return None if not xs else sum(xs) / len(xs)


class _RegistroPQP:
    """O replay de medicao do J5: embrulha a politica do braco, so le e repassa. Por decisao: o tick, a fome (o receptor, em S; e em 0-1
    para o D_FE), as comidas maduras a vista (pelos `vistos`), os troncos ja vistos com o tipo que dao agora (pelo motor), a posicao, o
    alvo escolhido (o do cerebro, ou o padrao do motor pela mesma funcao pura), se veio depois da mudanca e o que comeu. Confere o
    G-SEM-CREDITO em cada fruta na mao e retrata os modelos no fim de cada dia."""

    def __init__(self, interna: PoliticaDoBraco, cm: ConfigMundo, cfg_modelo: ConfigModeloMundo) -> None:
        self.interna, self.cm, self.cfg_modelo = interna, cm, cfg_modelo
        self.nome = interna.nome
        self.motor = None
        self.decisoes: list[dict] = []
        self.depois = False
        self.maos = 0
        self.violacoes_sem_credito: list = []
        self.modelos_por_dia: list = []
        self._dia = 0

    def modelo_pqp(self) -> PoliticaComModeloPQP:
        m = self.interna.cerebro
        if not isinstance(m, PoliticaComModeloPQP):
            raise TypeError("o cerebro do J5 e o PoliticaComModeloPQP")
        return m

    def cerebro_a(self) -> PoliticaLobos:
        c = self.modelo_pqp()._interna
        if not isinstance(c, PoliticaLobos):
            raise TypeError("o cerebro do J5 e o A (PoliticaLobos)")
        return c

    def _retratar_dias(self, tick: int) -> None:
        while tick >= (self._dia + 1) * TICKS_POR_DIA:
            self._dia += 1
            m = self.modelo_pqp().modelo
            self.modelos_por_dia.append({"dia": self._dia, "desfecho": json.loads(json.dumps(m.desfecho)), "andar": m.andar,
                                         "mapa": json.loads(json.dumps(m.mapa)), "receptores": None if m.receptores is None
                                         else list(m.receptores)})

    def agir(self, obs, rng):
        tick = self.motor._estado.tick
        self._retratar_dias(tick)
        pm, pc = obs.mundo, obs.corpo
        tipos_arv = {a["id"]: a["fruta"] for a in self.motor.mundo.arvores}
        v = obs.vetor_estado
        self.decisoes.append({"tick": tick, "depois": self.depois, "fome": pc.fome, "fome01": v[0], "energia01": v[2], "humor01": v[3],
                              "x": pm.x, "y": pm.y, "vistos": [tuple(t) for t in pm.vistos],
                              "maduros": [t for _i, t, *_ in pm.vistos if t in FRUTAS or t == "racao"],
                              "troncos": {i: tipos_arv[i] for i in sorted(self.motor.troncos_vistos)}, "acao": None, "alvo": None,
                              "comeu": None})
        a = self.interna.agir(obs, rng)
        self.decisoes[-1]["acao"] = a.value
        self.decisoes[-1]["n_motivo"] = len(self.cerebro_a().motivos) - 1     # o motivo desta decisao (o plano, a sonda, o fator)
        return a

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        r = self.interna.escolher_alvo(acao, candidatos, percepcao, u)
        alvo = alvo_padrao_de(acao, list(candidatos), percepcao, self.cm) if r is None else r
        fruta = None
        if alvo is not None and alvo.tipo == "comida":
            fruta = next((t for i, t, *_ in percepcao.vistos if i == alvo.id), None)
        self.decisoes[-1]["alvo"] = None if alvo is None else {"tipo": alvo.tipo, "fruta": fruta,
                                                               "arvore": alvo.tipo[len("arvore:"):] if alvo.tipo.startswith("arvore:")
                                                               else None}
        return r

    def consequencia_mundo(self, acao, ocorrido: dict, obs_depois) -> None:
        c = ocorrido.get("comeu")
        if c is not None and c["situacao"] == "madura":
            self.decisoes[-1]["comeu"] = c["tipo"]
        self.interna.consequencia_mundo(acao, ocorrido, obs_depois)

    def mudanca_no_mundo(self, tick: int) -> None:
        self.depois = True
        gancho = getattr(self.interna, "mudanca_no_mundo", None)
        if gancho is not None:
            gancho(tick)

    def fruta_na_mao(self, tipo: str, obs_antes, obs_depois) -> None:
        self.maos += 1
        antes = json.dumps(_sem_modelos(self.interna.estado_interno()), sort_keys=True)
        gancho = getattr(self.interna, "fruta_na_mao", None)
        if gancho is not None:
            gancho(tipo, obs_antes, obs_depois)
        depois = json.dumps(_sem_modelos(self.interna.estado_interno()), sort_keys=True)
        if antes != depois:
            self.violacoes_sem_credito.append(self.motor._estado.tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _sem_modelos(ei: dict) -> dict:
    """O estado interno do cerebro sem os modelos do mundo (os do embrulho e os do planejador), para a G-SEM-CREDITO: a fruta na mao so
    pode mudar os modelos."""
    out = {k: v for k, v in ei.items() if k != "modelo_mundo"}
    if "plano" in out:
        out["plano"] = {k: v for k, v in out["plano"].items() if k != "modelo_mundo"}
    return out


def plano_da_vida(decisoes: list, motivos: list, planejador: bool, dias: int) -> dict:
    """As medidas do plano numa vida do J5, do motivo de cada decisao (secao 4 e o G2 da secao 7). So le.

    - **Quanto o plano decide**, por dia: entre as decisoes com alvo (o motor pediu o alvo e havia para onde ir), as em que a sonda "quem
      decidiu" muda a escolha: a da decisao (`plano`: a acao com o mesmo u e sem o termo) ou a do alvo (`alvo_plano`: o alvo com o mesmo u
      e sem o termo). As duas partes saem tambem em separado, e a da acao sobre todas as decisoes.
    - **A legibilidade:** a fracao das decisoes com o fator do plano no motivo (`motivo.fator_do_plano`), a contagem por fator e o texto do
      adulto de cada fator diferente (`expressao.expressar`).
    - **O G2** (gate de mecanismo): sem o planejador (o P1, g_plano 0), o termo do plano e zero em toda decisao e nenhum motivo tem a sonda;
      falha alto se nao for. Com o planejador, sai a contagem das decisoes com termo diferente de zero."""
    if len(motivos) != len(decisoes):
        raise RuntimeError(f"plano: {len(motivos)} motivos para {len(decisoes)} decisoes")
    por_dia = [{"dia": d, "decisoes": 0, "com_alvo": 0, "decidiu": 0, "decidiu_acao": 0, "decidiu_alvo": 0, "decidiu_acao_todas": 0,
                "com_termo": 0, "com_fator": 0} for d in range(dias)]
    fatores: dict = {}
    textos: dict = {}
    for d, m in zip(decisoes, motivos):
        if m["n"] != d["n_motivo"]:
            raise RuntimeError(f"plano: a decisao do tick {d['tick']} aponta o motivo {d['n_motivo']}, nao o {m['n']}")
        r = por_dia[d["tick"] // TICKS_POR_DIA]
        p, ap = m.get("plano"), m.get("alvo_plano")
        termo = (any(v != 0 for v in m["contribuicoes"].get(LOBO_PLANEJAMENTO, {}).values())
                 or (ap is not None and any(v != 0 for v in ap["termos"].values())))
        if not planejador and (termo or p is not None or ap is not None or LOBO_PLANEJAMENTO in m["contribuicoes"]):
            raise RuntimeError(f"G2: o P1 (g_plano 0) com o termo do plano na decisao do tick {d['tick']}")
        dec_acao, dec_alvo = bool(p and p["plano_decidiu"]), bool(ap and ap["plano_decidiu"])
        r["decisoes"] += 1
        r["com_termo"] += termo
        r["decidiu_acao_todas"] += dec_acao
        if d["alvo"] is not None:
            r["com_alvo"] += 1
            r["decidiu_acao"] += dec_acao
            r["decidiu_alvo"] += dec_alvo
            r["decidiu"] += dec_acao or dec_alvo
        fp = fator_do_plano(m)
        if fp is not None:
            r["com_fator"] += 1
            fatores[nome_base(fp)] = fatores.get(nome_base(fp), 0) + 1
            if fp not in textos:
                textos[fp] = expressar(Motivo("vida", m["acao"], (fp,), (), 1.0, False, tick=d["tick"]), "adulto").conteudo
    for r in por_dia:
        r["fracao"] = None if not r["com_alvo"] else r["decidiu"] / r["com_alvo"]
        r["fracao_acao_todas"] = None if not r["decisoes"] else r["decidiu_acao_todas"] / r["decisoes"]
    n = len(decisoes)
    com_fator = sum(r["com_fator"] for r in por_dia)
    com_termo = sum(r["com_termo"] for r in por_dia)
    return {"plano": {"planejador": planejador, "por_dia": por_dia, "com_alvo": sum(r["com_alvo"] for r in por_dia),
                      "decidiu": sum(r["decidiu"] for r in por_dia), "com_termo": com_termo},
            "legibilidade": {"decisoes": n, "com_fator": com_fator, "fracao": None if not n else com_fator / n,
                             "fatores": dict(sorted(fatores.items())), "textos": dict(sorted(textos.items()))},
            "g2": {"planejador": planejador, "decisoes_com_termo": com_termo, "conferido": not planejador}}


def fracao_plano_dias(medida: dict, dias: tuple) -> dict:
    """A medida da regra da calibracao do g_plano (secao 5), numa vida: a fracao das decisoes com alvo em que o plano muda a escolha, nos
    dias `dias` (inclusive, contados de 0), pela soma dos dias. Sem decisao com alvo na janela, None."""
    ini, fim = dias
    linhas = [r for r in medida["plano"]["por_dia"] if ini <= r["dia"] <= fim]
    if len(linhas) != fim - ini + 1:
        raise ValueError(f"a vida nao tem os dias {ini} a {fim} (tem {len(medida['plano']['por_dia'])})")
    com_alvo, decidiu = sum(r["com_alvo"] for r in linhas), sum(r["decidiu"] for r in linhas)
    return {"com_alvo": com_alvo, "decidiu": decidiu, "fracao": None if not com_alvo else decidiu / com_alvo}


def modelos_contra_o_real(retratos: list, motor: MotorMundo, x: str, S: int) -> list:
    """O descritivo dos modelos (secao 4), por dia: o desfecho da x no humor contra o efeito real dela no fim do dia (em S), e a fracao
    das arvores do layout em que o tipo de maior frequencia no mapa e o tipo que a arvore da (o real, com a troca do T2), entre as que o
    mapa ja viu dar alguma fruta. Le o motor so como o experimentador (o real), nunca para a vida."""
    reais = {a["id"]: a["fruta"] for a in motor.mundo.arvores}
    trocas = motor.mundo.trocas_tipo or []
    rev = getattr(motor, "revaloracao", None)
    out = []
    for r in retratos:
        fim = r["dia"] * TICKS_POR_DIA
        arv = dict(reais)
        for t in reversed(trocas):               # o tipo de cada arvore no fim do dia: desfaz as trocas que vieram depois
            if t["tick"] >= fim:
                for i in t["arvores"]:
                    arv[i] = t["y"] if arv[i] == t["x"] else t["x"]
        if rev is None:
            efeito = motor.efeito_frutas[x]                  # sem revaloracao (o T2 e a fase 1), o efeito nunca mudou
        else:
            efeito = (rev["depois"] if rev["tick"] < fim else rev["antes"])[x]
        ih = None if r["receptores"] is None or "humor" not in r["receptores"] else r["receptores"].index("humor")
        certas = vistas = 0
        for i, f in arv.items():
            m = r["mapa"].get(i)
            if m is None or max(m) == 0:
                continue
            vistas += 1
            certas += max(range(len(m)), key=lambda j: (m[j], -j)) == list(MODELO_TIPOS).index(f)
        out.append({"dia": r["dia"], "desfecho_x_humor": None if ih is None else r["desfecho"][x][ih],
                    "efeito_real_x": arred(efeito * S), "mapa_arvores_vistas": vistas,
                    "mapa_acerto": None if not vistas else certas / vistas})
    return out


CHAVES_CONFIG_PQP = {"descricao", "plano", "tipo", "bracos", "protocolos", "sementes", "unidades", "d_a", "janela", "n_mao",
                     "orcamento_por_dia", "dono", "lugar", "ponto", "lobos", "montagem", "consequencia", "mundo", "corpo", "passo0",
                     "g_plano"}


def validar_config_pqp(cfg: dict) -> dict:
    """A config da bancada do J5 (`"tipo": "pet_que_pensa"`). As unidades usam o prefixo `pet_que_pensa`. Fora das sementes dos testes, a
    run e do plano: pede o `plano` do J5, as bases das faixas dele, a montagem completa (o cerebro da secao 2) e o corpo do passo 0
    (`passo0`: o passo0.json cuja escolha da o gasto, PP-3)."""
    faltam = {"tipo", "bracos", "protocolos", "orcamento_por_dia"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG_PQP
    if faltam or sobram:
        raise ValueError(f"config do J5: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["tipo"] != "pet_que_pensa":
        raise ValueError(f"config do J5 com tipo {cfg['tipo']!r}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config do J5: ou 'sementes' ou 'unidades' (bases x K derivadas), um dos dois")
    bracos, protocolos = list(cfg["bracos"]), list(cfg["protocolos"])
    if not bracos or len(set(bracos)) != len(bracos) or any(b not in BRACOS_PQP for b in bracos):
        raise ValueError(f"bracos do J5 {bracos}: so {sorted(BRACOS_PQP)}, sem repetir")
    if not protocolos or len(set(protocolos)) != len(protocolos) or any(p not in PROTOCOLOS_PQP for p in protocolos):
        raise ValueError(f"protocolos do J5 {protocolos}: so {PROTOCOLOS_PQP}, sem repetir")
    com_plano = any(braco_pqp(b).planejador for b in bracos)
    g = cfg.get("g_plano")
    if com_plano and (type(g) is not int or g <= 0):
        raise ValueError(f"bracos com o planejador pedem 'g_plano' inteiro > 0 (a calibracao, PP-6): {g!r}")
    if not com_plano and g is not None:
        raise ValueError("'g_plano' sem braco com o planejador")
    if set(cfg.get("lobos", {})) & {"g_plano", "teto_plano"}:
        raise ValueError("o g_plano do J5 vem da chave 'g_plano' (so nos bracos com o planejador), nunca da 'lobos'")
    if "ponto" in cfg and cfg["ponto"] not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {cfg['ponto']!r}: so {sorted(PONTOS_APRENDIZ)}")
    if "montagem" in cfg and cfg["montagem"] not in MONTAGENS:
        raise ValueError(f"montagem {cfg['montagem']!r}: so {MONTAGENS}")
    if "mundo" in cfg:
        replace(CONFIG_MUNDO_LIGADA, **cfg["mundo"])
    if cfg.get("lugar", "comedouro") not in ESTILOS_LUGAR:
        raise ValueError(f"lugar {cfg.get('lugar')!r}: so {ESTILOS_LUGAR}")
    criar_dono(cfg.get("dono", "atencioso"))
    validar_teto_pesos(cfg)
    if "unidades" in cfg:
        u = cfg["unidades"]
        if set(u) != {"bases", "k", "prefixo"} or u["prefixo"] != PREFIXO_PQP:
            raise ValueError(f"unidades do J5: {{'bases', 'k', 'prefixo': {PREFIXO_PQP!r}}}, nao {u}")
        unidades_derivadas(u["bases"], int(u["k"]), u["prefixo"])
        usadas = set(u["bases"])
    else:
        usadas = set(cfg["sementes"])
    for ini, fim, motivo in FAIXAS_QUEIMADAS:
        queimadas = sorted(x for x in usadas if ini <= x <= fim)
        if queimadas:
            raise SementeSemPlano(f"sementes/bases {queimadas} na faixa queimada {ini}...{fim} ({motivo}): nao usar para nada")
    fora = sorted(usadas - SEMENTES_TESTE)
    if fora:
        if cfg.get("plano") != PLANO_PQP or not (RAIZ / PLANO_PQP).is_file():
            raise SementeSemPlano(f"sementes/bases {fora} fora das dos testes: precisa do plano do J5 ({PLANO_PQP}, campo 'plano')")
        faixa = set(BASES_PET_QUE_PENSA["calibracao"]) | set(BASES_PET_QUE_PENSA["validacao"])
        if "unidades" not in cfg or not usadas <= faixa or not (usadas <= set(BASES_PET_QUE_PENSA["calibracao"])
                                                               or usadas <= set(BASES_PET_QUE_PENSA["validacao"])):
            raise SementeSemPlano(f"as bases do plano do J5 sao as de uma fase so: {BASES_PET_QUE_PENSA} (secao 8), em 'unidades'")
        if cfg.get("montagem") != "completa":
            raise ValueError("a run do plano do J5 usa o cerebro do plano (secao 2): a montagem completa")
        if "passo0" not in cfg or "corpo" not in cfg:
            raise ValueError("a run do plano do J5 usa o corpo do passo 0 (PP-3): as chaves 'passo0' e 'corpo'")
        p0 = json.loads((RAIZ / cfg["passo0"]).read_text(encoding="utf-8"))
        if p0["escolha"]["corpo"] != cfg["corpo"]:
            raise ValueError(f"o corpo da config nao e o do passo 0 ({cfg['passo0']}): {cfg['corpo']} contra {p0['escolha']['corpo']}")
    return cfg


def bancada_pqp_da_config(cfg: dict) -> BancadaPQP:
    validar_config_pqp(cfg)
    d_a, janela = int(cfg.get("d_a", D_A_PQP)), int(cfg.get("janela", JANELA_PQP))
    chaves = {k: v for k, v in cfg.items() if k in ("consequencia", "lobos", "ponto", "montagem", "mundo", "corpo", "teto_pesos", "plano")}
    bancada = bancada_da_config({**chaves, "dias": d_a + janela, "orcamento": int(cfg["orcamento_por_dia"]) * (d_a + janela)})
    return BancadaPQP(bancada, d_a, janela, int(cfg.get("n_mao", N_MAO_PQP)), cfg.get("dono", "atencioso"), cfg.get("lugar", "comedouro"),
                      g_plano=int(cfg.get("g_plano", 0)))


def rodar_pqp(cfg: dict, pasta: Path) -> dict:
    """As vidas de todos os bracos x protocolos x unidades, gravadas e rejogadas do disco; as medidas por vida (secao 4). Recusa a pasta que
    ja existe (secao 11)."""
    if pasta.exists():
        raise FileExistsError(f"{pasta}: a pasta de saida do J5 ja existe")
    bp = bancada_pqp_da_config(cfg)
    if "unidades" in cfg:
        unidades = unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), cfg["unidades"]["prefixo"])
        sementes = [(u["semente"], {"base": u["base"], "k": u["k"]}) for u in unidades]
    else:
        sementes = [(int(s), None) for s in cfg["sementes"]]
    vidas, medidas = {}, {}
    for (s, unidade), braco, protocolo in product(sementes, cfg["bracos"], cfg["protocolos"]):
        v = bp.vida(EspecPQP(braco, protocolo, s))
        caminho = pasta / "vidas" / f"{v.nome}.jsonl"
        _gravar(caminho, v.motor.log.para_jsonl())
        bp.conferir_replay(v, caminho.read_text(encoding="utf-8"))
        vidas[v.nome] = v
        medidas[v.nome] = {**bp.medir(v), "unidade": unidade}
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "meta.json", _dump({**meta({**cfg, "dias": bp.bancada.dias}), "plano": PLANO_PQP,
                                        "modelo_mundo_sha256": _sha(RAIZ / "digilab" / "modelo_mundo.py"),
                                        "d_a": bp.d_a, "janela": bp.janela, "n_mao": bp.n_mao, "g_plano": bp.g_plano,
                                        "cfg_corpo": bp.cfg_corpo().__dict__, "cfg_modelo": bp.cfg_modelo.__dict__}))
    return {"vidas": vidas, "medidas": medidas}


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .faixas import FAIXAS_QUEIMADAS, SEMENTES_TESTE, SementeSemPlano, unidades_derivadas  # noqa: E402
from .bracos import Braco, braco_de, braco_montado, cfg_lobos_do_braco, MONTAGENS, PoliticaDoBraco, PONTOS_APRENDIZ  # noqa: E402
from .vida import contar_acoes, contar_gestos_mundo, _interno, ReplayDivergiu, resumo_motor  # noqa: E402
from .regras_mundo import simular_vida_fisico  # noqa: E402
from .nucleo import Bancada  # noqa: E402
from .config import bancada_da_config, validar_teto_pesos  # noqa: E402
from .rodar import _dump, _gravar, meta, _sha  # noqa: E402
