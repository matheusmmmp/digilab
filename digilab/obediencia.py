"""Personalidade no motor: temperamento na politica, vinculo, obediencia e desejo.

docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md, secoes 1-3. Nada aqui altera engine.py:
  - PoliticaBanditPersonalidade: a politica da memoria por espacos com as ESCALAS do
    temperamento (variancia da amostra, peso de elogio e repreensao, decaimento das
    memorias de demora e bronca). Temperamento neutro = configs identicas = mesma politica.
  - MotorPersonalidade: subclasse do MotorComFeedback. Sobrescreve so
    _aplicar_acao_usuario (recusa) e embrulha a politica para ver cada decisao
    (desejo e vinculo). O log e o mesmo: o replay reconstroi tudo.

Obediencia (so para acoes de cuidado; feedback sempre chega):
    p = logistica(b0 + b_vinculo*vinculo - b_teimosia*teimosia - b_conflito*conflito)
sorteada na stream propria `rng_obediencia` (derivada da semente do motor). Na
desobediencia: `recusar` (a acao do dono nao tem efeito) ou `fazer_outra` (o pet
segue a propria acao atual por um tick). Em ambos:
  - a acao consome orcamento igual (o canal ja contou antes de chegar aqui);
  - a funcao de efeito do dono roda sobre um estado DESCARTADO, so para consumir a
    rng de ambiente como uma acao aceita: recusar nao desalinha o clima entre bracos;
  - a tentativa conta como contato (tempo sem cuidado zera), sem efeito nas necessidades;
  - a politica recebe a acao do dono normalmente (recusa nao corta aprendizado).
Com `obediencia_desligada`, p = 1 e a rng_obediencia nunca e usada.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

from .config import (CONFIG_BANDIT, CONFIG_DESEJO, CONFIG_HABITUACAO, CONFIG_MEMORIA_ESPACOS, CONFIG_OBEDIENCIA,
                     CONFIG_TEMPERAMENTO, CONFIG_VINCULO, ConfigObediencia)
from .desejo import Desejo, desejo_de
from .events import AcaoPet, AcaoUsuario
from .memoria_espacos import PoliticaBanditEspacos
from .motivo import Motivo
from .policy import Observacao, efeito_da_acao_do_pet
from .protocol import derivar_semente
from .state import aplicar_acao_usuario
from .temperamento import NEUTRO, Temperamento
from .treino import MotorComFeedback
from .vinculo import Vinculo

# acao do dono -> necessidade que ela atende (as demais nao atendem nenhuma)
ATENDE = {"alimentar": "fome", "limpar": "higiene", "brincar": "humor", "acariciar": "humor"}
_IDX = {"fome": 0, "higiene": 1, "energia": 2, "humor": 3}


class PoliticaBanditPersonalidade(PoliticaBanditEspacos):
    """Memoria por espacos + temperamento. Com o temperamento neutro, os configs
    derivados sao IGUAIS aos padrao e a politica e identica a PoliticaBanditEspacos."""

    def __init__(self, cfg=None, temperamento: Temperamento = NEUTRO, cfg_bandit=None, cfg_memoria=None,
                 cfg_temperamento=None, habituacao_ligada: bool = False, cfg_habituacao=None) -> None:
        ct = cfg_temperamento or CONFIG_TEMPERAMENTO
        cb = cfg_bandit or CONFIG_BANDIT
        self.temperamento = temperamento
        if not temperamento.neutro:
            cb = replace(cb, variancia_amostra=cb.variancia_amostra * temperamento.fator_variancia(ct),
                         recompensa_elogio=cb.recompensa_elogio * temperamento.peso_elogio(ct),
                         recompensa_repreensao=cb.recompensa_repreensao * temperamento.peso_repreensao(ct))
            fator = {c: temperamento.fator_tau_rancor(ct) for c in ct.categorias_rancor}
        else:
            fator = None
        # habituacao (adendo DF 2.3): desligada = memoria e recompensa identicas as de antes
        self.habituacao_ligada = habituacao_ligada
        hab = (cfg_habituacao or CONFIG_HABITUACAO) if habituacao_ligada else None
        super().__init__(cfg, cb, cfg_memoria, fator, hab, temperamento)


def logistica(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def conflito(obs_vetor: tuple, acao: AcaoUsuario, cfg: ConfigObediencia) -> tuple[float, str | None]:
    """(conflito em [0, 1], necessidade em conflito). Necessidade mais urgente abaixo do
    limiar que a acao do dono NAO atende."""
    urg = sorted((obs_vetor[i], n) for n, i in _IDX.items() if obs_vetor[i] < cfg.limiar_conflito)
    if not urg:
        return 0.0, None
    nivel, nome = urg[0]
    if ATENDE.get(acao.value) == nome:
        return 0.0, None
    return (cfg.limiar_conflito - nivel) / cfg.limiar_conflito, nome


def termos_obediencia(vinculo: float, temperamento: Temperamento, conf: float, nec: str | None,
                      cfg: ConfigObediencia, vinculo_neutro: float) -> tuple[float, dict]:
    """(p, contribuicoes). Contribuicao de cada termo relativa ao pet neutro (vinculo no
    valor inicial, temperamento 0, sem conflito): e o que vira fator do motivo."""
    z = cfg.b0 + cfg.b_vinculo * vinculo - cfg.b_teimosia * temperamento.teimosia - cfg.b_conflito * conf
    contrib = {"vinculo_baixo": cfg.b_vinculo * (vinculo - vinculo_neutro),
               "teimosia": -cfg.b_teimosia * temperamento.teimosia}
    if nec is not None:
        contrib[f"necessidade_{nec}"] = -cfg.b_conflito * conf
    return logistica(z), contrib


@dataclass(frozen=True)
class Recusa:
    tick: int
    acao_dono: str
    tipo: str                # "recusar" | "fazer_outra"
    p_obedecer: float
    motivo: Motivo

    def para_dict(self) -> dict:
        return {"tick": self.tick, "acao_dono": self.acao_dono, "tipo": self.tipo, "p_obedecer": self.p_obedecer,
                "motivo": self.motivo.para_dict()}


class _PoliticaObservada:
    """Delega tudo a politica; so avisa o motor depois de cada decisao observada."""

    def __init__(self, politica, motor: "MotorPersonalidade") -> None:
        self._p = politica
        self._motor = motor

    def agir(self, obs, rng):
        return self._p.agir(obs, rng)

    def observar(self, transicao) -> None:
        self._p.observar(transicao)
        self._motor._decisao_observada(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self._p.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self._p.estado_interno()

    def __getattr__(self, nome):
        return getattr(self._p, nome)


class MotorPersonalidade(MotorComFeedback):
    def __init__(self, politica=None, cfg=None, semente: int = 42, temperamento: Temperamento = NEUTRO,
                 obediencia_desligada: bool = False, cfg_obediencia: ConfigObediencia | None = None,
                 cfg_vinculo=None, cfg_desejo=None) -> None:
        super().__init__(politica=politica, cfg=cfg, semente=semente)
        self.politica = _PoliticaObservada(self.politica, self)
        self.temperamento = temperamento
        self.obediencia_desligada = obediencia_desligada
        self.co = cfg_obediencia or CONFIG_OBEDIENCIA
        self.cd = cfg_desejo or CONFIG_DESEJO
        self.vinculo = Vinculo(cfg_vinculo or CONFIG_VINCULO)
        self._rng_obediencia = random.Random(derivar_semente("obediencia", semente))
        self.desejos: list[Desejo] = []
        self.recusas: list[Recusa] = []
        self.pedidos_obediencia = 0
        self._acao_pet_atual: AcaoPet | None = None
        self._n_eventos = 0               # indice do proximo evento de log (vale ao vivo e no replay)

    def _avancar(self, ticks: int):
        self._n_eventos += 1
        return super()._avancar(ticks)

    # ------------------------------------------------------------ decisoes do pet
    def _decisao_observada(self, transicao) -> None:
        tick = self._estado.tick
        obs: Observacao = transicao.observacao
        self._acao_pet_atual = transicao.acao
        d = self._desejo_atual(obs, tick)
        ultimo = self.desejos[-1] if self.desejos else None
        mudou = (d is None) != (ultimo is None) or (d is not None and d.chave() != ultimo.chave())
        if d is not None and mudou:
            self.desejos.append(d)
        elif d is None and ultimo is not None and mudou:
            self.desejos.append(Desejo(tick, ultimo.tipo, ultimo.alvo, 0.0))   # desejo acabou (intensidade 0)
        self.vinculo.decisao(obs, transicao.acao, tick, d if mudou else None)

    def _desejo_atual(self, obs: Observacao, tick: int) -> Desejo | None:
        """Gancho: o MotorTreino poe o pedido de pausa (fadiga) na frente."""
        return desejo_de(obs, self.politica._p, tick, self.cd)

    # ------------------------------------------------------------ acao do dono
    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        tick = self._estado.tick
        ref = self._n_eventos             # indice do evento desta acao no log
        self._n_eventos += 1
        if not self.obediencia_desligada and acao.value in self.co.acoes_sujeitas:
            self.pedidos_obediencia += 1
            vetor = Observacao.de_estado(self._estado).vetor_estado
            conf, nec = conflito(vetor, acao, self.co)
            p, contrib = termos_obediencia(self.vinculo.valor, self.temperamento, conf, nec, self.co,
                                           self.vinculo.cfg.inicial)
            if self._rng_obediencia.random() >= p:
                tipo = "fazer_outra" if self._rng_obediencia.random() < self.co.prob_fazer_outra else "recusar"
                aplicar_acao_usuario(self._estado, acao, self.cfg, self._rng_ambiente)   # efeito descartado
                # a tentativa do dono conta como contato (zera o tempo sem cuidado, como toda acao
                # do dono): sem isso o relogio do bandit (tempo sem cuidado + ultimo cuidado) desalinha
                self._estado = replace(self._estado, tick_ultimo_cuidado=self._estado.tick,
                                       total_cuidados=self._estado.total_cuidados + 1)
                if tipo == "fazer_outra":
                    self._estado = efeito_da_acao_do_pet(self._estado, self._acao_atual, self.cfg, 1)
                self.recusas.append(Recusa(tick, acao.value, tipo, p, self._motivo(tick, tipo, p, contrib)))
                self._depois_do_dono(acao, tick, ref)
                self.politica.receber_acao_dono(acao, tick)                             # recusa nao corta aprendizado
                return
        super()._aplicar_acao_usuario(acao)
        self._depois_do_dono(acao, tick, ref)

    def _depois_do_dono(self, acao: AcaoUsuario, tick: int, ref: int) -> None:
        self.vinculo.acao_dono(acao, tick, self._acao_pet_atual, ref)

    def _motivo(self, tick: int, tipo: str, p: float, contrib: dict) -> Motivo:
        """Honesto: so cita o termo de MAIOR contribuicao negativa, se passar do limiar."""
        negativos = sorted((c, n) for n, c in contrib.items() if c <= -self.co.limiar_motivo)
        fatores, refs = (), ()
        if negativos:
            nome = negativos[0][1]
            fatores = (nome,)
            if nome == "vinculo_baixo" and self.vinculo.ultimo_ref_baixa is not None:
                refs = (self.vinculo.ultimo_ref_baixa,)
        return Motivo("vida", tipo, fatores, refs, min(1.0, max(0.0, 1.0 - p)), False, tick=tick)

    def personalidade(self) -> dict:
        return {"temperamento": self.temperamento.para_dict(), "obediencia_desligada": self.obediencia_desligada,
                "vinculo": self.vinculo.para_dict(), "pedidos_obediencia": self.pedidos_obediencia,
                "recusas": len(self.recusas), "desejos": len(self.desejos)}
