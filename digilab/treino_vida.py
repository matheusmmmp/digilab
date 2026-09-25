"""Vida com treino (docs/TAREFA_TREINO_SOMBRIO.md): motor, plano de sessoes e donos.

MotorTreino (subclasse do MotorPersonalidade; engine.py intacto):
  - acoes TREINAR_* vao para o TreinoPet (treino_stats.py), NUNCA para o Estado do motor nem
    para a politica (barreira 2); acoes de cuidado seguem o caminho da personalidade;
  - obediencia na sessao: mesma logistica e mesma rng_obediencia; contra = o pet "enrola"
    (sem ganho, consome orcamento; se era forcada, os custos entram);
  - forcar (fadiga >= limite): vinculo -0,05 direto e motivo "forcar_treino";
  - pedido de pausa: fadiga >= 40 vira o Desejo (necessidade, alvo "descansar"); treinar com a
    pausa ativa = vinculo amostra 0 e motivo "treinar_cansado"; a pausa acabar sem treino =
    amostra 1 (pausa atendida);
  - evolucao: sobrecarga no inicio do adolescente >= 30 marca "fala fria"; no inicio do adulto
    >= 60 a forma adulta sera a sombria da linha e o vinculo fica com teto 0,6 dali em diante.
  - aceita(acao): o canal pergunta antes de aplicar; toque de treino dentro do intervalo minimo
    e rejeitado sem consumir orcamento e sem entrar no log.

Plano e donos (decisao do Matheus, 2026-09-25): orcamento = cuidado_por_dia x dias + sessoes-alvo
do estagio; todos os bracos com o MESMO orcamento. As sessoes do plano (slots) ficam num bloco
diario a partir de `hora_treino`, um por passo do dono. Em cada slot:
  atencioso, relapso, incoerente  treinam (exercicios em rodizio); com pedido de pausa fazem
                                  carinho no lugar (respeitam a pausa)
  aleatorio                       exercicio sorteado; com pedido de pausa, respeita com prob 0,5
  exigente                        treina no teto do dia (o extra sai do carinho: o orcamento de
                                  cuidado dele e menor na mesma medida); ignora a pausa; com
                                  fadiga >= limite forca em 1 de cada 2 sessoes possiveis
                                  (alternado, sem rng), na outra faz carinho
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace

from .config import (CONFIG_DONOS, CONFIG_EVOLUCAO_PESQUISA, CONFIG_PADRAO, CONFIG_SOMBRIO, CONFIG_TREINO,
                     TICKS_POR_DIA, Config, ConfigDonos, ConfigTreino)
from .desejo import Desejo
from .donos import Visao, criar_dono
from .events import ACOES_TREINO, AcaoUsuario, exercicio_de
from .motivo import Motivo
from .obediencia import MotorPersonalidade, PoliticaBanditPersonalidade, conflito, termos_obediencia
from .policy import Observacao
from .protocol import derivar_semente
from .temperamento import NEUTRO, Temperamento
from .treino import CanalDeInteracao, Vida
from .treino_stats import ToqueRejeitado, TreinoPet

EXERCICIOS = tuple(CONFIG_TREINO.exercicios)
ACAO_DO_EXERCICIO = {exercicio_de(a): a for a in ACOES_TREINO}
HORA_TREINO = 10 * 60          # PROPOSTO: bloco diario de treino a partir das 10:00
BRACOS_TREINO = ("atencioso", "relapso", "aleatorio", "incoerente", "exigente")


class MotorTreino(MotorPersonalidade):
    def __init__(self, politica=None, cfg=None, semente: int = 42, temperamento: Temperamento = NEUTRO,
                 especie: str = "brasa", obediencia_desligada: bool = False, cfg_treino: ConfigTreino | None = None,
                 cfg_sombrio=None, **kw) -> None:
        super().__init__(politica, cfg, semente, temperamento, obediencia_desligada, **kw)
        self.ct = cfg_treino or CONFIG_TREINO
        self.cs = cfg_sombrio or CONFIG_SOMBRIO
        self.treino = TreinoPet(especie, self.ct)
        self.transicoes: dict[str, dict] = {}
        self.fala_fria: bool | None = None       # decidido no inicio do adolescente
        self.sombria: bool | None = None          # decidido no inicio do adulto
        self.pausa: dict | None = None
        self.pausas = {"atendidas": 0, "ignoradas": 0}
        self.enroladas = 0
        self.motivos_treino: list[Motivo] = []

    # ------------------------------------------------------------ tempo
    def _checkpoint(self) -> None:
        e = self._estado
        bem = min(e.fome, e.higiene, e.energia) >= self.ct.limiar_bem_cuidado
        antes = self.treino.estagio
        self.treino.avancar(e.tick, e.dormindo, bem)
        if self.treino.estagio != antes:
            self._evoluiu(self.treino.estagio, e.tick)
        if self.treino.pede_pausa and self.pausa is None:
            self.pausa = {"inicio": e.tick, "treinou": False}
        elif not self.treino.pede_pausa and self.pausa is not None:
            if not self.pausa["treinou"]:
                self.vinculo._amostra(e.tick, "pausa", 1.0, self.ct.peso_pausa_vinculo, None)
                self.pausas["atendidas"] += 1
            self.pausa = None

    def _evoluiu(self, estagio: str, tick: int) -> None:
        s = self.treino.sobrecarga
        self.transicoes[estagio] = {"tick": tick, "sobrecarga": s}
        if estagio == "adolescente":
            self.fala_fria = s >= self.cs.limiar_aviso
        elif estagio == "adulto":
            self.sombria = s >= self.cs.limiar_sombrio
            if self.sombria:
                self.vinculo.limitar(tick, self.cs.teto_vinculo, "sombria")

    def _decisao_observada(self, transicao) -> None:
        self._checkpoint()
        super()._decisao_observada(transicao)

    def _desejo_atual(self, obs: Observacao, tick: int) -> Desejo | None:
        if self.treino.pede_pausa:
            return Desejo(tick, "necessidade", "descansar", min(1.0, self.treino.fadiga / 100.0))
        return super()._desejo_atual(obs, tick)

    # ------------------------------------------------------------ dono
    def aceita(self, acao: AcaoUsuario) -> bool:
        return acao not in ACOES_TREINO or self.treino.pode_tocar(self._estado.tick)

    def estado(self) -> dict:
        d = super().estado()
        t = self.treino
        d["treino"] = {"fadiga": t.fadiga, "pede_pausa": t.pede_pausa, "forcaria": t.forcaria,
                       "sobrecarga": t.sobrecarga, "estagio": t.estagio}
        return d

    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if acao not in ACOES_TREINO:
            super()._aplicar_acao_usuario(acao)
            return
        tick = self._estado.tick
        ref = self._n_eventos
        self._n_eventos += 1
        self._checkpoint()
        if not self.treino.pode_tocar(tick):
            raise ToqueRejeitado(f"treino no tick {tick} dentro do intervalo minimo (o canal devia rejeitar)")
        obedece, p, contrib = True, 1.0, {}
        if not self.obediencia_desligada:
            vetor = Observacao.de_estado(self._estado).vetor_estado
            conf, nec = conflito(vetor, acao, self.co)
            p, contrib = termos_obediencia(self.vinculo.valor, self.temperamento, conf, nec, self.co,
                                           self.vinculo.cfg.inicial)
            obedece = self._rng_obediencia.random() < p
        s = self.treino.sessao(tick, exercicio_de(acao), obedece)
        if s.forcada:
            self.vinculo.ajustar(tick, "forcar", self.ct.vinculo_forcar, ref)
            self.motivos_treino.append(Motivo("vida", "forcar_treino", ("fadiga_treino",), (), min(1.0, s.fadiga_antes / 100.0),
                                              False, tick=tick))
        if self.pausa is not None:
            if not self.pausa["treinou"]:
                self.pausas["ignoradas"] += 1
            self.pausa["treinou"] = True
            self.vinculo._amostra(tick, "pausa", 0.0, self.ct.peso_pausa_vinculo, ref)
            self.motivos_treino.append(Motivo("vida", "treinar_cansado", ("fadiga_treino",), (),
                                              min(1.0, s.fadiga_antes / 100.0), False, tick=tick))
        if not obedece:
            self.enroladas += 1
            self.motivos_treino.append(self._motivo(tick, "enrolar", p, contrib))

    def resumo_treino(self) -> dict:
        return {**self.treino.para_dict(), "transicoes": self.transicoes, "fala_fria": self.fala_fria,
                "sombria": self.sombria, "pausas": dict(self.pausas), "enroladas": self.enroladas,
                "vinculo_teto": self.vinculo.teto}


# ================================================================== plano e donos
def _sessoes_do_estagio(estagio: str, perfil: str, ct: ConfigTreino) -> int:
    return (ct.teto_dia if perfil == "exigente" else ct.sessoes_alvo_dia)[estagio]


def plano_de_treino(dias: int, perfil: str, cfg_donos: ConfigDonos | None = None, ct: ConfigTreino | None = None,
                    cfg_evo=None) -> list[int]:
    """Ticks das sessoes (slots). Cada estagio que treina recebe sessoes_por_dia x duracao em dias
    (arredondado para baixo); por dia, um bloco consecutivo de passos do dono a partir de HORA_TREINO
    (ou do inicio do estagio, se depois), ate a cota do dia ou o fim do estagio."""
    cfg_donos = cfg_donos or CONFIG_DONOS
    ct = ct or CONFIG_TREINO
    cfg_evo = cfg_evo or CONFIG_EVOLUCAO_PESQUISA
    fim_vida = dias * TICKS_POR_DIA
    passo = cfg_donos.passo_ticks
    inicios = {"crianca": cfg_evo.dur_bebe_min, "adolescente": cfg_evo.dur_bebe_min + cfg_evo.dur_crianca_min,
               "adulto": cfg_evo.dur_bebe_min + cfg_evo.dur_crianca_min + cfg_evo.dur_adolescente_min}
    fins = {"crianca": inicios["adolescente"], "adolescente": inicios["adulto"], "adulto": fim_vida}
    slots: list[int] = []
    for est in ("crianca", "adolescente", "adulto"):
        ini, fim = inicios[est], min(fins[est], fim_vida)
        if fim <= ini:
            continue
        por_dia = _sessoes_do_estagio(est, perfil, ct)
        total = int(por_dia * (fim - ini) / TICKS_POR_DIA)
        feitas = 0
        dia = ini // TICKS_POR_DIA
        while feitas < total and dia * TICKS_POR_DIA < fim:
            t = max(dia * TICKS_POR_DIA + HORA_TREINO, ini)
            t = -(-t // passo) * passo                      # primeiro tick de decisao do dono
            cota = 0
            while feitas < total and cota < por_dia and t < fim and t < (dia + 1) * TICKS_POR_DIA:
                if t > 0:
                    slots.append(t)
                    feitas += 1
                    cota += 1
                t += passo
            dia += 1
        if feitas < total:
            raise ValueError(f"plano de treino: {est} so coube {feitas}/{total} sessoes")
    return slots


def orcamento_treino(dias: int, cfg_donos=None, ct: ConfigTreino | None = None) -> tuple[int, int]:
    """(orcamento total, slots-alvo): igual para todos os bracos."""
    ct = ct or CONFIG_TREINO
    alvo = len(plano_de_treino(dias, "atencioso", cfg_donos, ct))
    return ct.cuidado_por_dia * dias + alvo, alvo


class DonoComTreino:
    """Embrulha o dono de cuidado da v1: ele cuida com o orcamento de cuidado; os slots do plano
    sao do treino (ou do carinho que o substitui). Um passo por slot fica reservado."""

    def __init__(self, braco: str, dias: int, cfg_donos: ConfigDonos | None = None, ct: ConfigTreino | None = None):
        if braco not in BRACOS_TREINO:
            raise KeyError(f"braco sem dono de treino: {braco!r}")
        self.nome = braco
        self.cfg_donos = cfg_donos or CONFIG_DONOS
        self.ct = ct or CONFIG_TREINO
        self.base = criar_dono("atencioso" if braco == "exigente" else braco)
        self.slots = set(plano_de_treino(dias, braco, self.cfg_donos, self.ct))
        self.n_slots = len(self.slots)
        self.slots_usados = 0
        self.rodizio = 0
        self.possiveis_forcar = 0
        self.contagem = {"treino": 0, "carinho_no_slot": 0}

    def decidir(self, visao: Visao, rng: random.Random) -> list[AcaoUsuario]:
        tick = (visao.passo + 1) * self.cfg_donos.passo_ticks
        slot = tick in self.slots
        max_b = self.cfg_donos.max_interacoes_por_passo - 1
        orc_b = visao.orcamento - self.n_slots
        gasto_b = visao.gasto - self.slots_usados
        restante_b = orc_b - gasto_b
        depois = visao.passos_totais - visao.passo - 1
        vb = replace(visao, orcamento=orc_b, gasto=gasto_b,
                     minimo_obrigatorio=max(0, restante_b - depois * max_b), maximo_permitido=min(restante_b, max_b))
        acoes = self.base.decidir(vb, rng)
        if slot:
            acoes.append(self._slot(visao.estado["treino"], rng))
            self.slots_usados += 1
        return acoes

    def _slot(self, info: dict, rng: random.Random) -> AcaoUsuario:
        if self.nome == "aleatorio":
            ex = EXERCICIOS[rng.randrange(len(EXERCICIOS))]
            if info["pede_pausa"] and rng.random() < 0.5:
                return self._carinho()
        else:
            ex = EXERCICIOS[self.rodizio % len(EXERCICIOS)]
            if self.nome == "exigente":
                if info["forcaria"]:
                    self.possiveis_forcar += 1
                    # 50% das sessoes possiveis acima do limite, alternado
                    if (self.possiveis_forcar - 1) % round(1 / self.ct.fracao_forcar_exigente) != 0:
                        return self._carinho()
            elif info["pede_pausa"]:
                return self._carinho()
        self.rodizio += 1
        self.contagem["treino"] += 1
        return ACAO_DO_EXERCICIO[ex]

    def _carinho(self) -> AcaoUsuario:
        self.contagem["carinho_no_slot"] += 1
        return AcaoUsuario.ACARICIAR


def fabricas_treino(semente: int, especie: str, temperamento: Temperamento, obediencia_desligada: bool = False,
                    ct: ConfigTreino | None = None):
    """(fabrica da politica, fabrica do motor) de uma vida com treino; reusadas no replay."""
    fp = lambda cfg=None: PoliticaBanditPersonalidade(cfg, temperamento)  # noqa: E731
    fm = (lambda politica, cfg, s: MotorTreino(politica, cfg, s, temperamento, especie,  # noqa: E731
                                               obediencia_desligada=obediencia_desligada, cfg_treino=ct))
    return fp, fm


def simular_vida_treino(braco: str, semente: int, dias: int, especie: str, temperamento: Temperamento,
                        cfg: Config | None = None, cfg_donos: ConfigDonos | None = None,
                        ct: ConfigTreino | None = None) -> Vida:
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    ct = ct or CONFIG_TREINO
    total = dias * TICKS_POR_DIA
    passos = total // cfg_donos.passo_ticks
    orc, _ = orcamento_treino(dias, cfg_donos, ct)
    fp, fm = fabricas_treino(semente, especie, temperamento, ct=ct)
    motor = fm(fp(cfg), cfg, semente)
    dono = DonoComTreino(braco, dias, cfg_donos, ct)
    # rng do dono: propria de cada braco (derivada da semente e do braco), como na v1
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
    v.dono = dono          # contagens do dono (treino x carinho no slot), para o relatorio
    return v
