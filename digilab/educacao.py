"""Educacao, lesoes e heranca no motor (educacao-v1).

docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, aprovado em 2026-09-28. Nada aqui altera engine.py nem o Estado v0:
  - MotorEducacao: subclasse do MotorTreino. Guarda a disciplina, a janela de travessura aberta e (depois)
    as lesoes. Sem nenhuma acao nova no log, rejoga igual ao MotorTreino, bit a bit (teste).
  - Acoes novas do dono (events.ACOES_EDUCACAO): so este motor aceita. Nos motores anteriores levantam erro.

Chamados (da crianca em diante), um slot por tipo a cada intervalo do cronograma, contado do inicio do estagio:
  - necessidade pedida abaixo do limiar -> chamado REAL: atende quem faz a acao do tipo (ou petisco, na fome);
  - necessidade em dia -> com chance f vira chamado FALSO:
        f = 0 com disciplina cheia ou depois de `acertos_para_aprender` broncas certas seguidas no estagio;
        senao min(teto, base * (1 - disciplina/max) + reforco * petiscos_cedidos)
    bronca -> disciplina +passo (certo); petisco -> cede e reforca; alimentar -> recusa a refeicao
    (efeito descartado, como a recusa da obediencia); prazo vencido -> disciplina -passo.
  - so com ConfigEducacao.ligada (desligada: nenhuma janela, nenhum sorteio; = MotorTreino);
  - uma janela por vez; dormindo nao chama. O sorteio do slot sai SEMPRE da `rng_travessura` (mesmo quando a
    necessidade e real ou o pet dorme): os bracos veem os mesmos numeros nos mesmos slots.
O dono ve a janela (tipo e pedido), nunca se e falsa: julga pela necessidade, como no Tamagotchi.

Parte 3 (tambem so com a chave ligada):
  - AVISO antes de sujar: os slots de `tipo_slot_aviso` (higiene) abrem um aviso, nunca chamado. levar_ao_banheiro
    no prazo -> sem sujeira (e disciplina +disciplina_por_banheiro, hoje 0); prazo vencido -> sujeira +1.
  - mau humor legitimo = chamado real de carinho: elogio tambem resolve. Bronca num chamado REAL = bronca sem
    motivo: o vinculo cai `vinculo_bronca_sem_motivo`.
  - resolvem sozinhas (sem janela): acordar o pet dormindo (a acao do dono que o acorda custa humor) e
    superalimentacao (comer ja saciado, refeicao aceita ou petisco, custa saude).
"""

from __future__ import annotations

import random
from dataclasses import replace

from .config import (CONFIG_EDUCACAO, CONFIG_EVOLUCAO_PESQUISA, CONFIG_LESOES, ConfigEducacao, ConfigLesoes)
from .events import ACOES_EDUCACAO, AcaoUsuario
from .obediencia import PoliticaBanditPersonalidade
from .protocol import derivar_semente
from .state import aplicar_acao_usuario
from .temperamento import NEUTRO, Temperamento
from .treino_vida import MotorTreino

# necessidade que cada tipo de chamado pede (carinho -> humor)
NECESSIDADE = {"fome": "fome", "higiene": "higiene", "carinho": "humor"}


class AcaoAindaSemEfeito(NotImplementedError):
    """Acao de educacao que existe no enum, mas cuja regra ainda nao foi implementada."""


def atende(pedido: str, acao: AcaoUsuario) -> bool:
    """acao do dono que atende um chamado REAL do tipo `pedido` (carinho = mau humor: elogio tambem resolve)"""
    return (acao.value in CONFIG_EVOLUCAO_PESQUISA.atende[pedido] or (pedido == "fome" and acao is AcaoUsuario.PETISCO)
            or (pedido == "carinho" and acao is AcaoUsuario.ELOGIAR))


class MotorEducacao(MotorTreino):
    def __init__(self, politica=None, cfg=None, semente: int = 42, temperamento: Temperamento = NEUTRO,
                 especie: str = "brasa", obediencia_desligada: bool = False, cfg_treino=None, cfg_sombrio=None,
                 cfg_educacao: ConfigEducacao | None = None, cfg_lesoes: ConfigLesoes | None = None, **kw) -> None:
        super().__init__(politica, cfg, semente, temperamento, especie, obediencia_desligada, cfg_treino,
                         cfg_sombrio, **kw)
        self.ce = cfg_educacao or CONFIG_EDUCACAO
        self.cl = cfg_lesoes or CONFIG_LESOES
        self._rng_travessura = random.Random(derivar_semente("travessura", semente))
        self.disciplina = 0
        self.janela: dict | None = None          # {"tipo", "pedido", "inicio", "prazo", "falso"}
        self.acertos = 0                         # broncas certas seguidas no estagio
        self.petiscos_cedidos = 0
        self._inicio_estagio = 0
        self._proximo: dict[str, int] = {}
        self._agendar(self.treino.estagio, 0)
        self.contagem = {"chamados_reais": 0, "reais_atendidos": 0, "reais_ignorados": 0, "falsos": 0,
                         "falsos_corrigidos": 0, "falsos_cedidos": 0, "falsos_ignorados": 0, "refeicoes_recusadas": 0,
                         "avisos": 0, "avisos_atendidos": 0, "avisos_ignorados": 0, "broncas_sem_motivo": 0,
                         "acordado": 0, "superalimentacao": 0}
        self.historico_janelas: list[dict] = []

    # ------------------------------------------------------------ agenda
    def _agendar(self, estagio: str, inicio: int) -> None:
        self._inicio_estagio = inicio
        iv = self.ce.intervalos_chamado_min.get(estagio, {})
        self._proximo = {tipo: inicio + m for tipo, m in iv.items()}

    def fracao_falso(self) -> float:
        c = self.ce
        if self.disciplina >= c.disciplina_max or self.acertos >= c.acertos_para_aprender:
            return 0.0
        return min(c.teto_falso, c.fracao_falso_base * (1 - self.disciplina / c.disciplina_max)
                   + c.reforco_por_petisco * self.petiscos_cedidos)

    def _evoluiu(self, estagio: str, tick: int) -> None:
        super()._evoluiu(estagio, tick)
        self.disciplina = int(self.disciplina * self.ce.fator_disciplina_ao_evoluir)
        self.acertos = 0
        self._agendar(estagio, tick)

    def _decisao_observada(self, transicao) -> None:
        super()._decisao_observada(transicao)          # checkpoint: pode evoluir e reagendar
        if not self.ce.ligada:
            return
        tick = self._estado.tick
        self._expirar(tick)
        for tipo in sorted(self._proximo):
            while tick >= self._proximo[tipo]:
                self._proximo[tipo] += self.ce.intervalos_chamado_min[self.treino.estagio][tipo]
                self._slot(tipo, tick)

    def _slot(self, tipo: str, tick: int) -> None:
        u = self._rng_travessura.random()               # sempre: numeros comuns entre bracos
        if self.janela is not None or self._estado.dormindo:
            return
        if tipo == self.ce.tipo_slot_aviso:
            self.janela = {"tipo": "aviso", "pedido": "banheiro", "inicio": tick, "prazo": tick + self.ce.janela_min,
                           "falso": False}
            self.contagem["avisos"] += 1
            return
        real = getattr(self._estado, NECESSIDADE[tipo]) < self.ce.limiar_necessidade_real
        if not real and u >= self.fracao_falso():
            return
        self.janela = {"tipo": "chamado", "pedido": tipo, "inicio": tick, "prazo": tick + self.ce.janela_min,
                       "falso": not real}
        self.contagem["falsos" if not real else "chamados_reais"] += 1

    def _fechar(self, desfecho: str, tick: int) -> None:
        self.historico_janelas.append({**self.janela, "desfecho": desfecho, "fim": tick})
        self.janela = None

    def _expirar(self, tick: int) -> None:
        j = self.janela
        if j is None or tick <= j["prazo"]:
            return
        if j["tipo"] == "aviso":
            self._estado = replace(self._estado, sujeira=min(self.cfg.sujeira_maxima, self._estado.sujeira + 1))
            self.contagem["avisos_ignorados"] += 1
        elif j["falso"]:
            self.disciplina = max(0, self.disciplina - self.ce.passo_disciplina)
            self.acertos = 0
            self.contagem["falsos_ignorados"] += 1
        else:
            self.contagem["reais_ignorados"] += 1
        self._fechar("ignorado", tick)

    # ------------------------------------------------------------ dono
    def estado(self) -> dict:
        d = super().estado()
        j = self.janela
        d["educacao"] = {"disciplina": self.disciplina,
                         "janela": None if j is None else {k: j[k] for k in ("tipo", "pedido", "inicio", "prazo")}}
        return d

    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        tick = self._estado.tick
        self._expirar(tick)
        j = self.janela
        if j is not None and j["falso"] and acao is AcaoUsuario.ALIMENTAR:
            self._recusar_refeicao(acao, tick)
            return
        dormia, fome, n_recusas = self._estado.dormindo, self._estado.fome, len(self.recusas)
        if acao is AcaoUsuario.PETISCO:
            self._petisco(acao, tick)
        elif acao is AcaoUsuario.LEVAR_AO_BANHEIRO:
            self._contato(acao, tick)
        elif acao in ACOES_EDUCACAO:
            raise AcaoAindaSemEfeito(f"{acao.value}: regra ainda nao implementada (Fase 2, parte seguinte)")
        else:
            super()._aplicar_acao_usuario(acao)
        if not self.ce.ligada:
            return
        self._sozinhas(acao, dormia, fome, len(self.recusas) > n_recusas)
        if j is None:
            return
        if j["tipo"] == "aviso":
            if acao is AcaoUsuario.LEVAR_AO_BANHEIRO:
                self.disciplina = min(self.ce.disciplina_max, self.disciplina + self.ce.disciplina_por_banheiro)
                self.contagem["avisos_atendidos"] += 1
                self._fechar("atendido", tick)
            return
        if not j["falso"] and acao is AcaoUsuario.REPREENDER:
            self.vinculo.ajustar(tick, "bronca_sem_motivo", self.ce.vinculo_bronca_sem_motivo, self._n_eventos - 1)
            self.contagem["broncas_sem_motivo"] += 1
        if j["falso"]:
            if acao is AcaoUsuario.REPREENDER:
                self.disciplina = min(self.ce.disciplina_max, self.disciplina + self.ce.passo_disciplina)
                self.acertos += 1
                self.contagem["falsos_corrigidos"] += 1
                self._fechar("corrigido", tick)
            elif acao is AcaoUsuario.PETISCO:
                self.petiscos_cedidos += 1
                self.acertos = 0
                self.contagem["falsos_cedidos"] += 1
                self._fechar("cedido", tick)
        elif atende(j["pedido"], acao):
            self.contagem["reais_atendidos"] += 1
            self._fechar("atendido", tick)

    def _sozinhas(self, acao: AcaoUsuario, dormia: bool, fome_antes: float, recusou: bool) -> None:
        """travessuras que se resolvem sozinhas: nao abrem janela, so tem consequencia"""
        if dormia and not self._estado.dormindo:
            self._estado = replace(self._estado, humor=max(0.0, self._estado.humor - self.ce.custo_humor_acordar))
            self.contagem["acordado"] += 1
        comeu = acao is AcaoUsuario.PETISCO or (acao is AcaoUsuario.ALIMENTAR and not recusou)
        if comeu and fome_antes >= self.ce.limiar_superalimentacao:
            self._estado = replace(self._estado,
                                   saude=max(0.0, self._estado.saude - self.ce.custo_saude_superalimentacao))
            self.contagem["superalimentacao"] += 1

    def _contato(self, acao: AcaoUsuario, tick: int) -> None:
        """o que toda acao do dono faz fora o efeito: conta como contato, vinculo e politica recebem"""
        ref = self._n_eventos
        self._n_eventos += 1
        self._estado = replace(self._estado, tick_ultimo_cuidado=self._estado.tick,
                               total_cuidados=self._estado.total_cuidados + 1)
        self._depois_do_dono(acao, tick, ref)
        self.politica.receber_acao_dono(acao, tick)

    def _petisco(self, acao: AcaoUsuario, tick: int) -> None:
        # sem obediencia (o pet sempre aceita petisco) e sem sorteio de sujeira
        ganho = self.cfg.ganho_alimentar * self.ce.fracao_petisco_alimentar
        self._estado = replace(self._estado, fome=min(1.0, self._estado.fome + ganho))
        self._contato(acao, tick)

    def _recusar_refeicao(self, acao: AcaoUsuario, tick: int) -> None:
        # chamado falso: recusa a refeicao. Efeito calculado e descartado (consome a rng de ambiente como uma
        # refeicao aceita, igual a recusa da obediencia); a janela continua aberta
        aplicar_acao_usuario(self._estado, acao, self.cfg, self._rng_ambiente)
        self.contagem["refeicoes_recusadas"] += 1
        self._contato(acao, tick)

    def resumo_educacao(self) -> dict:
        return {"disciplina": self.disciplina, "acertos": self.acertos, "petiscos_cedidos": self.petiscos_cedidos,
                "contagem": dict(self.contagem)}


def fabricas_educacao(semente: int, especie: str, temperamento: Temperamento, obediencia_desligada: bool = False,
                      ct=None, ce: ConfigEducacao | None = None, cl: ConfigLesoes | None = None):
    """(fabrica da politica, fabrica do motor) de uma vida com educacao; reusadas no replay."""
    fp = lambda cfg=None: PoliticaBanditPersonalidade(cfg, temperamento)  # noqa: E731
    fm = (lambda politica, cfg, s: MotorEducacao(politica, cfg, s, temperamento, especie,  # noqa: E731
                                                 obediencia_desligada=obediencia_desligada, cfg_treino=ct,
                                                 cfg_educacao=ce, cfg_lesoes=cl))
    return fp, fm
