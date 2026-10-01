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

Modo livre gravado (parte 7; excecao ao determinismo no CLAUDE.md): com um `decisor_externo` (LLM ou acaso
real, fora deste pacote), o slot sem necessidade real vira chamado falso se o DECISOR disser, nao a rng. Cada
decisao entra no log como evento `decisao_externa` (ponto, valor, fonte, versao); o replay le do log e nunca
chama o decisor. O sorteio da rng_travessura continua consumido (numeros comuns). `modo_livre` fica True.

Parte 3 (tambem so com a chave ligada):
  - AVISO antes de sujar: os slots de `tipo_slot_aviso` (higiene) abrem um aviso, nunca chamado. levar_ao_banheiro
    no prazo -> sem sujeira (e disciplina +disciplina_por_banheiro, hoje 0); prazo vencido -> sujeira +1.
  - mau humor legitimo = chamado real de carinho: elogio tambem resolve. Bronca num chamado REAL = bronca sem
    motivo: o vinculo cai `vinculo_bronca_sem_motivo`.
  - resolvem sozinhas (sem janela): acordar o pet dormindo (a acao do dono que o acorda custa humor) e
    superalimentacao (comer ja saciado, refeicao aceita ou petisco, custa saude).

Mentira (DESIGN_VOZ_PROPRIA, secao 9; so com ConfigMentira.ligada, que exige a educacao ligada):
  - toda fala espontanea abre uma janela de fala (uma janela por vez, junto das de chamado e aviso). Na pesquisa a
    fala vem de um slot a cada `intervalo_fala_min`, o primeiro `defasagem_fala_min` depois do inicio do estagio
    (da crianca em diante); no jogo, do evento `fala` (gatilho).
  - se ela e mentira sai da `rng_mentira` (derivada da semente): p = chance_mentira() (config.ConfigMentira). Cada
    fala consome SEMPRE dois sorteios (mentira e tema), mesmo sem abrir janela: numeros comuns entre bracos.
  - tema "estado" (a mentira contradiz as barras, o dono atento ve) ou "historia" (nao da para conferir).
  - bronca numa mentira: disciplina +passo e acerto; bronca numa verdade: bronca sem motivo (vinculo);
    petisco ou elogio numa mentira: +impunes_premiada; prazo vencido numa mentira: +1 impune (e zera os acertos).
  - impunes e acertos zeram na evolucao.

Parte 4 (so com ConfigLesoes.ligada): lutas fora da arena de pesquisa.
  - `lutar(rival, semente)` grava o evento `luta` (rival + semente) e joga a partida V21C com as regras da
    campanha; o resultado nao vai para o log: o replay joga de novo. O lutador do pet e o do rival vem de
    fabricas injetadas (as mesmas no replay).
  - derrota -> lesao com prob_lesao_derrota, sorteada numa rng derivada da semente da LUTA (igual entre bracos).
  - morte: lesoes_para_morte no estagio, ou lesao sem tratar por horas_sem_tratar_morte. Depois da morte,
    acao do dono e luta levantam PetMorto (o tempo ainda corre).
  - tratar_lesao limpa a lesao pendente. Contadores de luta e lesao zeram ao evoluir; na passagem para adulto
    grava-se a qualificacao por vitorias (efeito na forma: ConfigLesoes.efeito_qualificacao).

M1 (so com ConfigConfianca.ligada; docs/DESIGN_MVP_M1_CONFIANCA.md): confianca de combate e desgaste por rival
repetido (digilab/confianca.py), recalculados das lutas que ja estao no log (nenhum evento novo). Com a chave
ligada a experiencia de combate (`vitorias_vida`) soma a NOVIDADE da luta em vez de 1, o registro da luta e o
resumo ganham a confianca, e `epsilon_lutador()` soma kappa * max(0, -c). Desligada: nada disso existe e a vida,
o log e o resumo sao byte a byte os de antes (tests/test_confianca.py, gate G1).
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Callable

from .campanha import REGRAS_CAMPANHA, npc
from .combate_v2.v21.bots import lutador_adulto
from .combate_v2.v21.partida import Lutador, jogar
from .confianca import ConfiancaCombate, epsilon_confianca
from .config import (CONFIG_CONFIANCA, CONFIG_EDUCACAO, CONFIG_EVOLUCAO_PESQUISA, CONFIG_LESOES, CONFIG_MENTIRA,
                     ConfigConfianca, ConfigEducacao, ConfigLesoes, ConfigMentira)
from .events import ACOES_EDUCACAO, AcaoUsuario, LogDeEventos, decisao_externa, fala, ler_decisao, ler_luta, luta
from .heranca import HerancaInvalida, Origem, ler_origem
from .obediencia import PoliticaBanditPersonalidade
from .protocol import derivar_semente
from .state import aplicar_acao_usuario
from .temperamento import NEUTRO, Temperamento
from .treino_stats import TreinoPet
from .treino_vida import MotorTreino

# necessidade que cada tipo de chamado pede (carinho -> humor)
NECESSIDADE = {"fome": "fome", "higiene": "higiene", "carinho": "humor"}


class AcaoAindaSemEfeito(NotImplementedError):
    """Acao de educacao que existe no enum, mas cuja regra ainda nao foi implementada."""


class PetMorto(RuntimeError):
    """Acao do dono ou luta depois da morte."""


def rival_padrao(nome: str, escala=None) -> Lutador:
    """'npc:<tier>' (campanha) ou 'bot:<forma>@<especie>' (adulto canonico da bateria)."""
    tipo, _, resto = nome.partition(":")
    if tipo == "npc":
        return npc(resto, escala=escala)
    if tipo == "bot":
        forma, especie = resto.split("@")
        return lutador_adulto(forma, especie, escala=escala, nome=nome)
    raise ValueError(f"rival desconhecido: {nome!r}")


def epsilon_disciplina(disciplina: int, ce: ConfigEducacao | None = None) -> float:
    """epsilon do Lutador do pet: sem educacao ele ignora os proprios gambits mais vezes (PLANO_ANALISE_V3)"""
    ce = ce or CONFIG_EDUCACAO
    return ce.epsilon_base_pet + (1 - disciplina / ce.disciplina_max) * ce.delta_epsilon_indisciplina


def epsilon_pet(disciplina: int, vitorias_vida: float, ce: ConfigEducacao | None = None,
                cl: ConfigLesoes | None = None, confianca: float = 0.0, cc: ConfigConfianca | None = None) -> float:
    """epsilon do Lutador do pet no jogo: disciplina (PLANO_ANALISE_V3) menos a experiencia de combate (estilo
    "lutar"), mais a inseguranca (M1: kappa * max(0, -c), so com ConfigConfianca.ligada; a confianca positiva
    nao reduz alem do que a experiencia ja reduz). As runs V3/V3b usam so epsilon_disciplina (reprodutiveis)."""
    cl = cl or CONFIG_LESOES
    cc = cc or CONFIG_CONFIANCA
    exp = min(cl.experiencia_max, vitorias_vida * cl.experiencia_por_vitoria)
    inseguranca = epsilon_confianca(confianca, cc.kappa_eps) if cc.ligada else 0.0
    return max(0.0, epsilon_disciplina(disciplina, ce) - exp) + inseguranca


def atende(pedido: str, acao: AcaoUsuario) -> bool:
    """acao do dono que atende um chamado REAL do tipo `pedido` (carinho = mau humor: elogio tambem resolve)"""
    return (acao.value in CONFIG_EVOLUCAO_PESQUISA.atende[pedido] or (pedido == "fome" and acao is AcaoUsuario.PETISCO)
            or (pedido == "carinho" and acao is AcaoUsuario.ELOGIAR))


class MotorEducacao(MotorTreino):
    def __init__(self, politica=None, cfg=None, semente: int = 42, temperamento: Temperamento = NEUTRO,
                 especie: str = "brasa", obediencia_desligada: bool = False, cfg_treino=None, cfg_sombrio=None,
                 cfg_educacao: ConfigEducacao | None = None, cfg_lesoes: ConfigLesoes | None = None,
                 lutador_do_pet: Callable[["MotorEducacao"], Lutador] | None = None,
                 rival_por_nome: Callable[[str], Lutador] = rival_padrao, cfg_evo=None,
                 decisor_externo: Callable[[dict], tuple[bool, dict]] | None = None,
                 cfg_mentira: ConfigMentira | None = None, honestidade_especie: float = 1.0,
                 cfg_confianca: ConfigConfianca | None = None, **kw) -> None:
        super().__init__(politica, cfg, semente, temperamento, especie, obediencia_desligada, cfg_treino,
                         cfg_sombrio, **kw)
        if cfg_evo is not None:
            # parte 6: duracao dos estagios (ConfigDuracoes); o TreinoPet ainda esta no tick 0, sem nada feito
            self.treino = TreinoPet(especie, self.ct, cfg_evo)
        self.ce = cfg_educacao or CONFIG_EDUCACAO
        self.cl = cfg_lesoes or CONFIG_LESOES
        self.cc = cfg_confianca or CONFIG_CONFIANCA
        # M1: so existe com a chave ligada (desligada, nenhum calculo e nenhuma chave nova no resumo)
        self.confianca: ConfiancaCombate | None = ConfiancaCombate(self.cc) if self.cc.ligada else None
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
        # parte 4: lutas e lesoes
        self.lutador_do_pet = lutador_do_pet
        self.rival_por_nome = rival_por_nome
        self.lutas = self._lutas_zeradas()
        self.lesionado_desde: int | None = None
        self.historico_lutas: list[dict] = []
        self.vitorias_vida = 0                      # experiencia de combate: nao zera ao evoluir
        self._lutas_que_treinaram = 0
        self.morte: dict | None = None
        self.origem: Origem | None = None        # parte 5: filho de um cruzamento (evento `origem`, o primeiro)
        # parte 7: modo livre gravado
        self.decisor_externo = decisor_externo
        self._decisoes_gravadas: list[dict] | None = None   # no replay: fila lida do log
        self.modo_livre = False
        self._log_replay: LogDeEventos | None = None      # no replay: o log inteiro (o lutador le ate o tick)
        self.adulto_liberado: bool | None = None           # efeito "condicao_adulto" da qualificacao
        # mentira (DESIGN_VOZ_PROPRIA, secao 9)
        self.cm = cfg_mentira or CONFIG_MENTIRA
        if self.cm.ligada and not self.ce.ligada:
            raise ValueError("ConfigMentira ligada exige ConfigEducacao ligada (a fala usa a janela da educacao)")
        if not 0.0 <= honestidade_especie <= 1.0:
            raise ValueError(f"honestidade_especie fora de [0, 1]: {honestidade_especie}")
        self.honestidade_especie = honestidade_especie
        self._rng_mentira = random.Random(derivar_semente("mentira", semente))
        self.mentiras_impunes = 0
        self.acertos_mentira = 0                 # broncas certas seguidas em mentiras no estagio
        self.contagem_mentira = {"falas": 0, "falas_sem_janela": 0, "mentiras": 0, "corrigidas": 0, "premiadas": 0,
                                 "impunes": 0, "broncas_injustas": 0, "verdades_aceitas": 0, "verdades_ignoradas": 0}
        self._proximo_fala: int | None = None
        self._agendar_fala(self.treino.estagio, 0)

    @staticmethod
    def _lutas_zeradas() -> dict:
        return {"lutas": 0, "vitorias": 0, "derrotas": 0, "empates": 0, "lesoes": 0, "tratadas": 0}

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
        adulto_com_lutas = estagio == "adulto" and self.cl.ligada
        if adulto_com_lutas:
            n, v = self.lutas["lutas"], self.lutas["vitorias"]
            taxa = v / n if n else None
            self.qualificacao_vitorias = {"lutas": n, "vitorias": v, "taxa": taxa,
                                          "qualifica": n >= self.cl.lutas_minimas_taxa and taxa >= self.cl.limiar_taxa_vitoria,
                                          "efeito": self.cl.efeito_qualificacao}
        self.lutas = self._lutas_zeradas()
        super()._evoluiu(estagio, tick)
        if adulto_com_lutas:
            self.transicoes["adulto"]["vitorias"] = self.qualificacao_vitorias
            if self.cl.efeito_qualificacao == "condicao_adulto":
                self.adulto_liberado = self.qualificacao_vitorias["qualifica"]
        self.disciplina = int(self.disciplina * self.ce.fator_disciplina_ao_evoluir)
        self.acertos = 0
        self._agendar(estagio, tick)
        if self.cm.ligada:
            self.mentiras_impunes = 0
            self.acertos_mentira = 0
            self._agendar_fala(estagio, tick)

    def _decisao_observada(self, transicao) -> None:
        super()._decisao_observada(transicao)          # checkpoint: pode evoluir e reagendar
        tick = self._estado.tick
        self._conferir_morte(tick)
        if not self.ce.ligada:
            return
        self._expirar(tick)
        for tipo in sorted(self._proximo):
            while tick >= self._proximo[tipo]:
                self._proximo[tipo] += self.ce.intervalos_chamado_min[self.treino.estagio][tipo]
                self._slot(tipo, tick)
        while self._proximo_fala is not None and tick >= self._proximo_fala:
            self._proximo_fala += self.cm.intervalo_fala_min
            self._abrir_fala(tick, "slot")

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
        if not real and not self._falso(tipo, tick, u):
            return
        self.janela = {"tipo": "chamado", "pedido": tipo, "inicio": tick, "prazo": tick + self.ce.janela_min,
                       "falso": not real}
        self.contagem["falsos" if not real else "chamados_reais"] += 1

    def _falso(self, tipo: str, tick: int, u: float) -> bool:
        """o slot sem necessidade real vira chamado falso? rng (padrao) ou decisor externo (gravado no log)"""
        f = self.fracao_falso()
        if self._decisoes_gravadas is not None:              # replay de uma vida em modo livre
            if not self._decisoes_gravadas or self._decisoes_gravadas[0]["tick"] != tick:
                raise ValueError(f"replay pediu decisao externa no tick {tick}, o log nao tem")
            d = self._decisoes_gravadas.pop(0)
            self._n_eventos += 1
            self.modo_livre = True
            return bool(d["valor"])
        if self.decisor_externo is None or f == 0.0:          # disciplina cheia/aprendido: nem pergunta
            return u < f
        ctx = {"ponto": "slot_falso", "tick": tick, "estagio": self.treino.estagio, "pedido": tipo,
               "fracao_falso": f, "disciplina": self.disciplina, "petiscos_cedidos": self.petiscos_cedidos,
               "temperamento": self.temperamento.para_dict(),
               "necessidades": {k: getattr(self._estado, k) for k in ("fome", "higiene", "energia", "humor", "saude")}}
        valor, meta = self.decisor_externo(ctx)
        if not isinstance(valor, bool):
            raise TypeError(f"decisor externo devolveu {valor!r}, precisa ser bool")
        self._log.anexar(decisao_externa(tick, "slot_falso", valor, str(meta.get("fonte", "?")),
                                         str(meta.get("versao", "?"))))
        self._n_eventos += 1
        self.modo_livre = True
        return valor

    def _fechar(self, desfecho: str, tick: int) -> None:
        self.historico_janelas.append({**self.janela, "desfecho": desfecho, "fim": tick})
        self.janela = None

    def _expirar(self, tick: int) -> None:
        j = self.janela
        if j is None or tick <= j["prazo"]:
            return
        if j["tipo"] == "fala":
            if j["falso"]:
                self.mentiras_impunes += 1
                self.acertos_mentira = 0
                self.contagem_mentira["impunes"] += 1
                self._fechar("impune", tick)
            else:
                self.contagem_mentira["verdades_ignoradas"] += 1
                self._fechar("ignorado", tick)
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
        d["educacao"] = {"disciplina": self.disciplina, "lesionado": self.lesionado_desde is not None,
                         "janela": None if j is None else {k: j[k] for k in ("tipo", "pedido", "inicio", "prazo")}}
        if j is not None and j["tipo"] == "fala":
            # o dono ve a fala, nunca se e mentira; so percebe quando ela contradiz as barras
            d["educacao"]["janela"]["contradiz_barras"] = j["contradiz_barras"]
        if self.cm.ligada:
            d["educacao"]["honestidade"] = self.honestidade_mostrada()
        return d

    @property
    def log_ate_agora(self) -> LogDeEventos:
        """o log que vale agora: ao vivo, o do motor; no replay, o inteiro (quem le corta pelo tick)"""
        return self._log_replay if self._log_replay is not None else self._log

    # ------------------------------------------------------------ heranca
    def registrar_origem(self, origem: Origem) -> None:
        """Filho de um cruzamento: grava o evento `origem` como o PRIMEIRO do log."""
        if len(self._log):
            raise HerancaInvalida("a origem precisa ser o primeiro evento do log")
        self._log.anexar(origem.evento())
        self._aplicar_origem(origem)

    def _aplicar_origem(self, origem: Origem) -> None:
        if self.origem is not None or self._n_eventos != 0:
            raise HerancaInvalida("evento origem fora da primeira posicao do log")
        if origem.temperamento != self.temperamento or origem.especie != self.treino.especie:
            raise HerancaInvalida("o motor nao tem o temperamento e a especie que a origem herda")
        self.origem = origem
        self._n_eventos += 1

    # ------------------------------------------------------------ lutas e lesoes
    def _conferir_morte(self, tick: int) -> None:
        if self.morte is not None or not self.cl.ligada:
            return
        if self.lesionado_desde is not None and tick - self.lesionado_desde >= self.cl.horas_sem_tratar_morte * 60:
            self.morte = {"tick": tick, "causa": "lesao_sem_tratar"}

    def _avancar(self, ticks: int):
        # a morte tambem e conferida no fim do avanco: o prazo da lesao cai num tick de passo do dono, antes
        # da proxima decisao do pet (igual ao vivo e no replay: vem do evento avanco)
        r = super()._avancar(ticks)
        self._conferir_morte(self._estado.tick)
        return r

    def _vivo(self) -> None:
        if self.morte is not None:
            raise PetMorto(f"o pet morreu no tick {self.morte['tick']} ({self.morte['causa']})")

    def lutar(self, rival: str, semente: int) -> dict:
        """Luta fora da arena de pesquisa: grava o evento e joga. Devolve o registro da luta."""
        if not self.cl.ligada:
            raise ValueError("luta com ConfigLesoes desligada")
        self._vivo()
        self._log.anexar(luta(self._estado.tick, rival, semente))
        return self._lutar(rival, semente)

    def _lutar(self, rival: str, semente: int) -> dict:
        if not self.cl.ligada:
            raise ValueError("evento luta no log, mas ConfigLesoes desligada")
        tick = self._estado.tick
        self._n_eventos += 1
        self._checkpoint()
        self._conferir_morte(tick)
        self._vivo()
        if self.lutador_do_pet is None:
            raise ValueError("MotorEducacao sem lutador_do_pet: nao da para lutar")
        p = jogar(self.lutador_do_pet(self), self.rival_por_nome(rival), semente, REGRAS_CAMPANHA)
        res = "vitoria" if p.pontos_a == 1.0 else "derrota" if p.pontos_a == 0.0 else "empate"
        self.lutas["lutas"] += 1
        self.lutas[{"vitoria": "vitorias", "derrota": "derrotas", "empate": "empates"}[res]] += 1
        conf = None
        if self.confianca is not None:
            # M1: decai desde a ultima luta, pesa pela novidade do rival; a derrota pesa mais pela sensibilidade
            sinal = {"vitoria": 1, "derrota": -1, "empate": 0}[res]
            conf = self.confianca.registrar(tick, rival, sinal, self.temperamento.sensibilidade)
        if res == "vitoria":
            # experiencia de combate: com a confianca ligada, soma a novidade (repetir o rival rende menos)
            self.vitorias_vida += conf["novidade"] if conf is not None else 1
        lesao = res == "derrota" and random.Random(derivar_semente("lesao", semente)).random() < self.cl.prob_lesao_derrota
        if lesao:
            self.lutas["lesoes"] += 1
            if self.lesionado_desde is None:
                self.lesionado_desde = tick
            if self.lutas["lesoes"] >= self.cl.lesoes_para_morte:
                self.morte = {"tick": tick, "causa": "lesoes"}
        treinou = None
        if self.cl.luta_treina and self.treino.estagio in self.ct.teto_por_estagio and self.treino.pode_tocar(tick):
            exercicios = tuple(self.ct.exercicios)
            treinou = exercicios[self._lutas_que_treinaram % len(exercicios)]
            self.treino.sessao(tick, treinou, True)
            self._lutas_que_treinaram += 1
        reg = {"tick": tick, "rival": rival, "semente": semente, "resultado": res, "turnos": p.turnos,
               "lesao": lesao, "estagio": self.treino.estagio, "treinou": treinou}
        if conf is not None:
            reg["confianca"] = conf
        self.historico_lutas.append(reg)
        return reg

    def epsilon_lutador(self) -> float:
        """epsilon do lutador do pet no jogo, agora: disciplina, experiencia e (M1, so ligada) a inseguranca"""
        c = self.confianca.valor(self._estado.tick) if self.confianca is not None else 0.0
        return epsilon_pet(self.disciplina, self.vitorias_vida, self.ce, self.cl, c, self.cc)

    def _tratar_lesao(self, acao: AcaoUsuario, tick: int) -> None:
        if self.lesionado_desde is not None:
            self.lesionado_desde = None
            self.lutas["tratadas"] += 1
        self._contato(acao, tick)

    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        tick = self._estado.tick
        if self.cl.ligada:
            self._conferir_morte(tick)
            self._vivo()
        self._expirar(tick)
        j = self.janela
        if j is not None and j["tipo"] == "chamado" and j["falso"] and acao is AcaoUsuario.ALIMENTAR:
            self._recusar_refeicao(acao, tick)
            return
        dormia, fome, n_recusas = self._estado.dormindo, self._estado.fome, len(self.recusas)
        if acao is AcaoUsuario.PETISCO:
            self._petisco(acao, tick)
        elif acao is AcaoUsuario.LEVAR_AO_BANHEIRO:
            self._contato(acao, tick)
        elif acao is AcaoUsuario.TRATAR_LESAO:
            self._tratar_lesao(acao, tick)
        elif acao in ACOES_EDUCACAO:
            raise AcaoAindaSemEfeito(f"{acao.value}: regra ainda nao implementada (Fase 2, parte seguinte)")
        else:
            super()._aplicar_acao_usuario(acao)
        if not self.ce.ligada:
            return
        self._sozinhas(acao, dormia, fome, len(self.recusas) > n_recusas)
        if j is None:
            return
        if j["tipo"] == "fala":
            self._julgar_fala(j, acao, tick)
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

    # ------------------------------------------------------------ mentira
    def _agendar_fala(self, estagio: str, inicio: int) -> None:
        self._proximo_fala = (inicio + self.cm.defasagem_fala_min
                              if self.cm.ligada and estagio in self.cm.estagios_fala else None)

    def honestidade(self) -> float:
        """h (0 a 1): sombria e sobrecarga tiram; um pet sem sobrecarga e nao sombrio tem h = 1 e nunca mente"""
        fator = self.cm.fator_sombria if self.sombria else 1.0
        h = fator * (1 - self.cm.peso_sobrecarga * self.treino.sobrecarga / 100.0) * self.honestidade_especie
        return max(0.0, min(1.0, h))

    def chance_mentira(self) -> float:
        cm, h = self.cm, self.honestidade()
        if h >= 1.0 or self.acertos_mentira >= cm.acertos_para_aprender:
            return 0.0
        return min(cm.teto_chance, cm.coef_chance * (1 - h) * (1 - self.disciplina / self.ce.disciplina_max)
                   + cm.reforco_por_impune * self.mentiras_impunes)

    def honestidade_mostrada(self) -> float:
        """a que o jogo mostra: cai com a vista grossa, sobe com a disciplina"""
        return 1.0 - self.chance_mentira() / self.cm.teto_chance

    def falar(self, gatilho: str) -> dict | None:
        """Fala espontanea disparada de fora (o jogo): grava o evento `fala` e abre a janela (ou nao, se ja houver
        uma aberta ou o pet dormir). Devolve a janela aberta (com a verdade: quem chama e a apresentacao)."""
        if not self.cm.ligada:
            raise ValueError("fala espontanea com ConfigMentira desligada")
        self._vivo()
        self._log.anexar(fala(self._estado.tick, gatilho))
        return self._fala_do_log(gatilho)

    def _fala_do_log(self, gatilho: str) -> dict | None:
        if not self.cm.ligada:
            raise ValueError("evento fala no log, mas ConfigMentira desligada")
        tick = self._estado.tick
        self._n_eventos += 1
        self._checkpoint()
        self._expirar(tick)
        return self._abrir_fala(tick, gatilho)

    def _abrir_fala(self, tick: int, gatilho: str) -> dict | None:
        u, u_tema = self._rng_mentira.random(), self._rng_mentira.random()     # sempre: numeros comuns
        self.contagem_mentira["falas"] += 1
        if self.janela is not None or self._estado.dormindo or self.morte is not None:
            self.contagem_mentira["falas_sem_janela"] += 1
            return None
        h, p = self.honestidade(), self.chance_mentira()
        mentira = u < p
        tema = "estado" if u_tema < self.cm.fracao_tema_estado else "historia"
        self.janela = {"tipo": "fala", "pedido": tema, "inicio": tick, "prazo": tick + self.cm.janela_fala_min,
                       "falso": mentira, "contradiz_barras": mentira and tema == "estado", "gatilho": gatilho,
                       "honestidade": h, "chance": p}
        if mentira:
            self.contagem_mentira["mentiras"] += 1
        return dict(self.janela)

    def _julgar_fala(self, j: dict, acao: AcaoUsuario, tick: int) -> None:
        """o dono julga a fala (bronca, petisco ou elogio fecham a janela; o resto nao)"""
        if acao is AcaoUsuario.REPREENDER:
            if j["falso"]:
                self.disciplina = min(self.ce.disciplina_max, self.disciplina + self.ce.passo_disciplina)
                self.acertos_mentira += 1
                self.contagem_mentira["corrigidas"] += 1
                self._fechar("corrigida", tick)
            else:
                self.vinculo.ajustar(tick, "bronca_sem_motivo", self.ce.vinculo_bronca_sem_motivo, self._n_eventos - 1)
                self.contagem_mentira["broncas_injustas"] += 1
                self._fechar("bronca_injusta", tick)
        elif acao in (AcaoUsuario.PETISCO, AcaoUsuario.ELOGIAR):
            if j["falso"]:
                self.mentiras_impunes += self.cm.impunes_premiada
                self.acertos_mentira = 0
                self.contagem_mentira["premiadas"] += 1
                self._fechar("premiada", tick)
            else:
                self.contagem_mentira["verdades_aceitas"] += 1
                self._fechar("aceita", tick)

    @property
    def historico_falas(self) -> list[dict]:
        return [j for j in self.historico_janelas if j["tipo"] == "fala"]

    def resumo_mentira(self) -> dict:
        return {"mentiras_impunes": self.mentiras_impunes, "acertos_mentira": self.acertos_mentira,
                "honestidade": self.honestidade(), "chance": self.chance_mentira(),
                "honestidade_mostrada": self.honestidade_mostrada(), "contagem": dict(self.contagem_mentira)}

    def estado_lutas(self) -> dict:
        return {"lutas": dict(self.lutas), "lesionado_desde": self.lesionado_desde, "morte": self.morte,
                "vitorias_vida": self.vitorias_vida}

    def resumo_educacao(self) -> dict:
        r = {"disciplina": self.disciplina, "acertos": self.acertos, "petiscos_cedidos": self.petiscos_cedidos,
             "contagem": dict(self.contagem), **self.estado_lutas()}
        if self.confianca is not None:          # M1: so com a chave ligada (desligada, o resumo e o de antes)
            r["confianca"] = self.confianca.para_dict()
        return r


def reproduzir_educacao(log: LogDeEventos, politica_fabrica: Callable, cfg=None, semente: int = 42,
                        fabrica_motor: Callable | None = None, ate_tick: int | None = None,
                        pular_lutas: bool = False) -> MotorEducacao:
    """reproduzir_com_feedback + os eventos novos. Evento desconhecido levanta erro.
    ate_tick: para antes do primeiro evento nesse tick (corta o avanco que o atravessa), como politica_no_tick.
    pular_lutas: para medir a politica (carater): luta nao muda politica nem estado, so contadores."""
    from .config import CONFIG_PADRAO
    cfg = cfg or CONFIG_PADRAO
    if fabrica_motor is None:
        raise ValueError("reproduzir_educacao precisa da fabrica do MotorEducacao (lutador do pet, configs)")
    motor = fabrica_motor(politica_fabrica(cfg), cfg, semente)
    if motor.decisor_externo is not None:
        raise ValueError("replay nao chama decisor externo: use a fabrica sem ele (as decisoes vem do log)")
    decisoes = [ler_decisao(e) for e in log if e.tipo == "decisao_externa"]
    if decisoes:
        motor._decisoes_gravadas = decisoes
    motor._log_replay = log
    for evento in log:
        if ate_tick is not None and evento.tick >= ate_tick:
            break
        if evento.tipo == "avanco":
            n = int(evento.valor) if ate_tick is None else min(int(evento.valor), ate_tick - evento.tick)
            motor._avancar(n)
        elif evento.tipo == "luta" and pular_lutas:
            pass
        elif evento.tipo == "acao_usuario":
            motor._aplicar_acao_usuario(AcaoUsuario(evento.valor))
        elif evento.tipo == "luta":
            motor._lutar(*ler_luta(evento))
        elif evento.tipo == "origem":
            motor._aplicar_origem(ler_origem(evento))
        elif evento.tipo == "decisao_externa":
            pass                                     # ja consumida dentro do avanco que a pediu
        elif evento.tipo == "fala":
            motor._fala_do_log(str(evento.valor))
        else:
            raise ValueError(f"tipo de evento desconhecido no log: {evento.tipo!r}")
    if ate_tick is None and motor._decisoes_gravadas:
        raise ValueError(f"{len(motor._decisoes_gravadas)} decisoes externas no log que o replay nao usou")
    motor._log_replay = None
    motor._log = LogDeEventos([e for e in log if ate_tick is None or e.tick < ate_tick])
    return motor


def politica_no_tick_educacao(log: LogDeEventos, politica_fabrica: Callable, semente: int, tick: int,
                              fabrica_motor: Callable):
    """evolucao.politica_no_tick para vidas com educacao (entende os eventos novos; lutas nao mudam a politica)"""
    return reproduzir_educacao(log, politica_fabrica, semente=semente, fabrica_motor=fabrica_motor, ate_tick=tick,
                               pular_lutas=True).politica


def fabricas_filho(origem: Origem, **kw):
    """fabricas_educacao com a especie e o temperamento herdados (a semente do motor vem de quem chama)."""
    return fabricas_educacao(0, origem.especie, origem.temperamento, **kw)


def fabricas_educacao(semente: int, especie: str, temperamento: Temperamento, obediencia_desligada: bool = False,
                      ct=None, ce: ConfigEducacao | None = None, cl: ConfigLesoes | None = None,
                      lutador_do_pet: Callable | None = None, rival_por_nome: Callable = rival_padrao,
                      cfg_evo=None, decisor_externo=None, cm: ConfigMentira | None = None,
                      honestidade_especie: float = 1.0, cc: ConfigConfianca | None = None,
                      politica_fabrica: Callable | None = None):
    """(fabrica da politica, fabrica do motor) de uma vida com educacao; reusadas no replay (sem o decisor).
    politica_fabrica (V2, L1): troca a politica do pet (padrao: o bandit da personalidade, bit a bit como antes)."""
    fp = politica_fabrica or (lambda cfg=None: PoliticaBanditPersonalidade(cfg, temperamento))  # noqa: E731
    fm = (lambda politica, cfg, s: MotorEducacao(politica, cfg, s, temperamento, especie,  # noqa: E731
                                                 obediencia_desligada=obediencia_desligada, cfg_treino=ct,
                                                 cfg_educacao=ce, cfg_lesoes=cl, lutador_do_pet=lutador_do_pet,
                                                 rival_por_nome=rival_por_nome, cfg_evo=cfg_evo,
                                                 decisor_externo=decisor_externo, cfg_mentira=cm,
                                                 honestidade_especie=honestidade_especie, cfg_confianca=cc))
    return fp, fm
