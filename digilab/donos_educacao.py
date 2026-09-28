"""Donos da educacao-v1: o permissivo e a resposta de cada braco a janela de travessura.

docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, secao 2.4. Os donos da v1 e o DonoComTreino nao mudam: o
DonoComEducacao embrulha o DonoComTreino e so acrescenta a resposta a janela aberta.

Resposta a janela (PROPOSTO, sem fonte; o dono julga pela necessidade, nunca sabe se o chamado e falso):
  atencioso, exigente  necessidade baixa -> atende; em dia -> bronca
  permissivo           necessidade baixa -> atende; em dia -> petisco (cede)
  incoerente           necessidade baixa -> atende; em dia -> elogio ou bronca sorteados (prob_elogio_incoerente)
  relapso              como o atencioso, mas so nos passos de visita
  aviso antes de sujar todos menos o aleatorio levam ao banheiro (o relapso, so na visita)
  aleatorio            nada de especial (as acoes sorteadas podem acertar por acaso)
  persona              so nas horas de presenca: responde com prob_atender_janela; manha -> petisco com
                       prob_ceder_petisco, senao bronca (digilab/personas.py)
A resposta sai do mesmo orcamento: o dono de baixo decide como se ela ja tivesse sido gasta, e o passo nunca
passa do teto (a ultima acao de cuidado cede o lugar).
"""

from __future__ import annotations

import random
from dataclasses import replace

from .config import (CONFIG_DONOS, CONFIG_DURACOES, CONFIG_EDUCACAO_LIGADA, CONFIG_PADRAO, CONFIG_TREINO, TICKS_POR_DIA,
                     Config, ConfigDonos, ConfigEducacao)
from .donos import DonoAtencioso, DonoRelapso, Visao, _DonoBase, _feedback, julgar_acao
from .educacao import NECESSIDADE, fabricas_educacao
from .events import ACOES_TREINO, AcaoUsuario
from .personas import Persona
from .protocol import derivar_semente
from .temperamento import Temperamento
from .treino import CanalDeInteracao, Vida
from .treino_vida import BRACOS_TREINO, DonoComTreino, orcamento_treino, plano_de_treino

BRACOS_EDUCACAO = tuple(BRACOS_TREINO) + ("permissivo",)
ATENDE_PRIMEIRA = {"fome": AcaoUsuario.ALIMENTAR, "higiene": AcaoUsuario.LIMPAR, "carinho": AcaoUsuario.ACARICIAR}


class DonoPermissivo(DonoAtencioso):
    """Presenca alta, educacao zero: cuida como o atencioso, elogia o que acha bom e nunca da bronca
    (onde o atencioso repreenderia, faz carinho)."""

    nome = "permissivo"

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        return [AcaoUsuario.ACARICIAR if a is AcaoUsuario.REPREENDER else a for a in super()._desejo(visao, rng)]

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        sinal = julgar_acao(visao.estado, self.cfg)
        return _feedback(sinal) if sinal > 0 else AcaoUsuario.ACARICIAR


def hora_do_passo(passo: int, cfg_donos: ConfigDonos) -> int:
    """hora do dia (0-23) em que o dono age no passo (tick (passo + 1) x passo_ticks)"""
    return ((passo + 1) * cfg_donos.passo_ticks % TICKS_POR_DIA) // 60


class DonoPersonaBase(_DonoBase):
    """Cuidado de uma persona: so nas horas de presenca; cuida abaixo do limiar dela; feedback coerente
    com prob_feedback_coerente, senao sorteado. Fora da presenca nao faz nada (o canal ainda pode exigir o
    minimo no fim da vida: vira carinho)."""

    def __init__(self, persona: Persona, cfg: ConfigDonos | None = None) -> None:
        super().__init__(cfg)
        self.persona = persona
        self.nome = f"persona:{persona.nome}"

    def _desejo(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        p = self.persona
        if not p.presente(hora_do_passo(visao.passo, self.cfg)):
            return []
        e = visao.estado
        acoes = [a for a, k in ((AcaoUsuario.ALIMENTAR, "fome"), (AcaoUsuario.LIMPAR, "higiene"),
                                (AcaoUsuario.BRINCAR, "humor")) if e[k] < p.limiar_cuidado]
        if visao.atrasado:
            if rng.random() < p.prob_feedback_coerente:
                sinal = julgar_acao(e, self.cfg)
                if sinal != 0:
                    acoes.append(_feedback(sinal))
            else:
                acoes.append(AcaoUsuario.ELOGIAR if rng.random() < 0.5 else AcaoUsuario.REPREENDER)
        return acoes

    def _preencher(self, visao: Visao, rng: random.Random) -> AcaoUsuario:
        return AcaoUsuario.ACARICIAR


class DonoComEducacao(DonoComTreino):
    def __init__(self, braco: str, dias: int, cfg_donos: ConfigDonos | None = None, ct=None,
                 ce: ConfigEducacao | None = None, cfg_evo=None, persona: Persona | None = None):
        if persona is not None:
            if braco != f"persona:{persona.nome}":
                raise KeyError(f"braco de persona precisa ser 'persona:{persona.nome}', veio {braco!r}")
        elif braco not in BRACOS_EDUCACAO:
            raise KeyError(f"braco sem dono de educacao: {braco!r}")
        perfil = persona.perfil_treino if persona is not None else braco
        super().__init__("atencioso" if perfil == "permissivo" else perfil, dias, cfg_donos, ct)
        self.persona = persona
        if braco == "permissivo":
            self.nome = braco
            self.base = DonoPermissivo(self.cfg_donos)
        elif persona is not None:
            # o treino segue as regras do atencioso (pausa respeitada); perfil_treino so muda quantas sessoes
            self.nome = braco
            self.base = DonoPersonaBase(persona, self.cfg_donos)
        self.ce = ce or CONFIG_EDUCACAO_LIGADA
        if cfg_evo is not None:                  # slots de treino nos estagios da duracao escolhida
            self.slots = set(plano_de_treino(dias, "exigente" if perfil == "exigente" else "atencioso",
                                             self.cfg_donos, self.ct, cfg_evo))
            self.n_slots = len(self.slots)
        self.respostas = {"atende": 0, "bronca": 0, "petisco": 0, "elogio": 0, "banheiro": 0}

    def _resposta(self, visao: Visao, rng: random.Random) -> tuple[AcaoUsuario, str] | None:
        j = visao.estado.get("educacao", {}).get("janela")
        if j is None or self.nome == "aleatorio":
            return None
        if self.persona is not None:
            return self._resposta_persona(j, visao, rng)
        if isinstance(self.base, DonoRelapso):
            self.base._planejar_dia(visao, rng, TICKS_POR_DIA // self.cfg_donos.passo_ticks)   # idempotente no dia
            if visao.passo not in self.base._visitas:
                return None
        if j["tipo"] == "aviso":
            return AcaoUsuario.LEVAR_AO_BANHEIRO, "banheiro"
        if visao.estado[NECESSIDADE[j["pedido"]]] < self.ce.limiar_necessidade_real:
            return ATENDE_PRIMEIRA[j["pedido"]], "atende"
        if self.nome == "permissivo":
            return AcaoUsuario.PETISCO, "petisco"
        if self.nome == "incoerente" and rng.random() < self.cfg_donos.prob_elogio_incoerente:
            return AcaoUsuario.ELOGIAR, "elogio"
        return AcaoUsuario.REPREENDER, "bronca"

    def _resposta_persona(self, j: dict, visao: Visao, rng: random.Random) -> tuple[AcaoUsuario, str] | None:
        p = self.persona
        if not p.presente(hora_do_passo(visao.passo, self.cfg_donos)) or rng.random() >= p.prob_atender_janela:
            return None
        if j["tipo"] == "aviso":
            return AcaoUsuario.LEVAR_AO_BANHEIRO, "banheiro"
        if visao.estado[NECESSIDADE[j["pedido"]]] < self.ce.limiar_necessidade_real:
            return ATENDE_PRIMEIRA[j["pedido"]], "atende"
        if rng.random() < p.prob_ceder_petisco:
            return AcaoUsuario.PETISCO, "petisco"
        return AcaoUsuario.REPREENDER, "bronca"

    def decidir(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        # a resposta sai do orcamento de CUIDADO: os slots de treino continuam reservados (sem verba de cuidado,
        # a janela fica sem resposta, como a de um dono sem tempo)
        slot = (visao.passo + 1) * self.cfg_donos.passo_ticks in self.slots
        cuidado_restante = (visao.orcamento - self.n_slots) - (visao.gasto - self.slots_usados)
        r = self._resposta(visao, rng) if cuidado_restante > 0 and visao.maximo_permitido > int(slot) else None
        if r is None:
            return super().decidir(visao, rng)
        r, chave = r
        self.respostas[chave] += 1
        acoes = [r] + super().decidir(replace(visao, gasto=visao.gasto + 1), rng)
        if len(acoes) > visao.maximo_permitido:
            cuidado = [i for i, a in enumerate(acoes) if i > 0 and a not in ACOES_TREINO]
            del acoes[cuidado[-1] if cuidado else 0]
        return acoes


def simular_vida_educacao(braco: str, semente: int, dias: int, especie: str, temperamento: Temperamento,
                          cfg: Config | None = None, cfg_donos: ConfigDonos | None = None, ct=None,
                          ce: ConfigEducacao | None = None, duracao: str = "teste", persona: Persona | None = None,
                          decisor_externo=None) -> Vida:
    """simular_vida_treino com o MotorEducacao (travessuras ligadas) e o DonoComEducacao; mesmo orcamento.
    duracao: "teste" (a de hoje, bit a bit igual) ou "canonica" (ConfigDuracoes).
    persona: dono de persona (braco = 'persona:<nome>'). decisor_externo: modo livre gravado (educacao.py)."""
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    ce = ce or CONFIG_EDUCACAO_LIGADA
    passos = dias * TICKS_POR_DIA // cfg_donos.passo_ticks
    cfg_evo = None if duracao == "teste" else CONFIG_DURACOES.cfg_evo(duracao)
    if cfg_evo is None:
        orc, _ = orcamento_treino(dias, cfg_donos, ct)
    else:                                        # mesma conta do orcamento_treino, com os estagios da duracao
        ctt = ct or CONFIG_TREINO
        orc = ctt.cuidado_por_dia * dias + len(plano_de_treino(dias, "atencioso", cfg_donos, ctt, cfg_evo))
    fp, fm = fabricas_educacao(semente, especie, temperamento, ct=ct, ce=ce, cfg_evo=cfg_evo,
                               decisor_externo=decisor_externo)
    motor = fm(fp(cfg), cfg, semente)
    dono = DonoComEducacao(braco, dias, cfg_donos, ct, ce, cfg_evo, persona)
    rng_dono = random.Random(derivar_semente("dono", semente, braco))
    canal = CanalDeInteracao(motor, orc, cfg_donos.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cfg_donos.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orc, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
    canal.fechar()
    v = Vida(braco=braco, semente_coorte=semente, motor=motor, interacoes=canal.gasto)
    v.dono = dono
    return v
