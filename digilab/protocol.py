"""Protocolo experimental congelado da arena (Etapa 1).

Tudo que define o experimento mora aqui, em dataclasses frozen, ANTES de
qualquer execucao. Cada campo carrega um status:

  DECIDIDO  - fixado pelo pesquisador (ou imposto pelo enunciado da tarefa)
  PROPOSTO  - valor razoavel escolhido por quem implementou, ainda nao
              referendado. Uma run com qualquer campo PROPOSTO grava aviso
              no artefato de saida.

O hash do protocolo cobre os campos daqui, todos os dataclasses de
config.py e o conteudo de engine.py. Mudou qualquer um deles, mudou o
hash, e o artefato antigo deixa de ser comparavel.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, fields, replace
from enum import Enum
from pathlib import Path
from typing import Any

from . import config as _config


class Status(str, Enum):
    DECIDIDO = "DECIDIDO"
    PROPOSTO = "PROPOSTO"


@dataclass(frozen=True)
class Campo:
    valor: Any
    status: Status
    justificativa: str

    def para_dict(self) -> dict:
        return {
            "valor": _para_json(self.valor),
            "status": self.status.value,
            "justificativa": self.justificativa,
        }


def _para_json(v: Any) -> Any:
    if isinstance(v, tuple):
        return [_para_json(x) for x in v]
    if isinstance(v, Enum):
        return v.value
    return v


# Hash de engine.py na versao v0 recebida. engine.py nao pode mudar: o
# preflight compara. Calculado com finais de linha normalizados para \n.
ENGINE_SHA256_V0 = "48ba51ce6426eb98a726c05e07f3a57992ae0f328f517740ec36f1c3db153630"

BRACOS_VALIDOS = ("atencioso", "relapso", "aleatorio", "incoerente")


@dataclass(frozen=True)
class Protocolo:
    versao: str

    sementes_coorte: Campo
    orcamento_interacoes: Campo
    dias_simulados: Campo
    bracos: Campo
    partidas_por_par: Campo
    semente_torneio: Campo
    definicao_vitoria: Campo
    metricas: Campo
    limiar_divergencia_jsd_bits: Campo
    estados_sonda: Campo
    amostras_por_estado: Campo
    semente_sonda: Campo
    bootstrap_reamostragens: Campo
    bootstrap_semente: Campo
    nivel_confianca: Campo

    # ------------------------------------------------------------ consultas

    def campos(self) -> dict[str, Campo]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "versao"}

    def campos_propostos(self) -> list[str]:
        return [n for n, c in self.campos().items() if c.status is Status.PROPOSTO]

    def v(self, nome: str) -> Any:
        """Atalho para o valor de um campo. Nome inexistente levanta erro."""
        if nome not in self.campos():
            raise KeyError(f"campo de protocolo inexistente: {nome!r}")
        return self.campos()[nome].valor

    # -------------------------------------------------------------- validacao

    def validar(self) -> None:
        sementes = self.v("sementes_coorte")
        if len(sementes) < 5:
            raise ValueError(f"protocolo exige pelo menos 5 sementes, tem {len(sementes)}")
        if len(set(sementes)) != len(sementes):
            raise ValueError(f"sementes repetidas: {sementes}")
        if not all(isinstance(s, int) for s in sementes):
            raise TypeError("sementes precisam ser int")
        orc = self.v("orcamento_interacoes")
        if not isinstance(orc, int) or orc <= 0:
            raise ValueError(f"orcamento_interacoes invalido: {orc!r}")
        dias = self.v("dias_simulados")
        if not isinstance(dias, int) or dias <= 0:
            raise ValueError(f"dias_simulados invalido: {dias!r}")
        passos = dias * _config.TICKS_POR_DIA // _config.CONFIG_DONOS.passo_ticks
        teto = passos * _config.CONFIG_DONOS.max_interacoes_por_passo
        if orc > teto:
            raise ValueError(
                f"orcamento {orc} inalcancavel: teto fisico e {teto} "
                f"({passos} passos x {_config.CONFIG_DONOS.max_interacoes_por_passo})"
            )
        bracos = self.v("bracos")
        for b in bracos:
            if b not in BRACOS_VALIDOS:
                raise ValueError(f"braco desconhecido: {b!r}")
        for obrigatorio in ("atencioso", "aleatorio"):
            if obrigatorio not in bracos:
                raise ValueError(f"braco obrigatorio ausente: {obrigatorio}")
        if self.v("partidas_por_par") <= 0:
            raise ValueError("partidas_por_par precisa ser positivo")
        lim = self.v("limiar_divergencia_jsd_bits")
        if not (0.0 < lim < 1.0):
            raise ValueError(f"limiar de divergencia fora de (0,1) bits: {lim}")
        nivel = self.v("nivel_confianca")
        if not (0.5 < nivel < 1.0):
            raise ValueError(f"nivel_confianca invalido: {nivel}")

    # ------------------------------------------------------------------ hash

    def para_dict(self) -> dict:
        return {"versao": self.versao, **{n: c.para_dict() for n, c in self.campos().items()}}

    def hash(self) -> str:
        return hash_protocolo(self)

    # -------------------------------------------------------------- variacao

    def com_substituicoes(self, substituicoes: dict[str, Any]) -> "Protocolo":
        """Variante nao canonica (ex.: teste de fumaca). Campo trocado vira PROPOSTO."""
        novos: dict[str, Campo] = {}
        for nome, valor in substituicoes.items():
            if nome not in self.campos():
                raise KeyError(f"substituicao para campo inexistente: {nome!r}")
            if isinstance(valor, list):
                valor = tuple(valor)
            novos[nome] = Campo(valor, Status.PROPOSTO, "substituido via --config (nao canonico)")
        p = replace(self, versao=self.versao + "+substituido", **novos)
        p.validar()
        return p


def conteudo_normalizado(caminho: Path) -> bytes:
    return caminho.read_bytes().replace(b"\r\n", b"\n")


def sha256_engine() -> str:
    return hashlib.sha256(conteudo_normalizado(Path(__file__).with_name("engine.py"))).hexdigest()


def configs_congelados() -> dict:
    return {
        "Config": asdict(_config.CONFIG_PADRAO),
        "ConfigBandit": asdict(_config.CONFIG_BANDIT),
        "ConfigDonos": asdict(_config.CONFIG_DONOS),
        "ConfigTracos": asdict(_config.CONFIG_TRACOS),
        "ConfigArena": asdict(_config.CONFIG_ARENA),
        "ConfigMetricas": asdict(_config.CONFIG_METRICAS),
        "TICKS_POR_DIA": _config.TICKS_POR_DIA,
    }


def hash_protocolo(p: Protocolo) -> str:
    carga = {
        "protocolo": p.para_dict(),
        "configs": configs_congelados(),
        "engine_sha256": sha256_engine(),
    }
    texto = json.dumps(carga, sort_keys=True, ensure_ascii=True, default=_para_json)
    return hashlib.sha256(texto.encode("ascii")).hexdigest()


def derivar_semente(*rotulos: Any) -> int:
    """Semente deterministica e independente a partir de rotulos.

    Usa sha256, nao hash() do Python (que e aleatorizado por processo).
    """
    texto = "|".join(str(r) for r in rotulos)
    return int.from_bytes(hashlib.sha256(texto.encode("utf-8")).digest()[:8], "big")


# =====================================================================
# O protocolo canonico. Congelado antes de qualquer run.
# =====================================================================

_P = Status.PROPOSTO
_D = Status.DECIDIDO

PROTOCOLO_ARENA_V1 = Protocolo(
    versao="arena-v1",
    sementes_coorte=Campo(
        (101, 202, 303, 404, 505),
        _D,
        "criterio de pronto exige incerteza sobre pelo menos 5 sementes; "
        "o numero 5 e decidido, os valores sao arbitrarios e fixados aqui",
    ),
    orcamento_interacoes=Campo(
        14 * 16,
        _P,
        "16 interacoes/dia x 14 dias; na demo v0 o dono atencioso gastou ~13,6/dia. "
        "Igual entre bracos por construcao (simulador impoe)",
    ),
    dias_simulados=Campo(14, _P, "mesma janela da demo v0, que ja separa atencioso de relapso"),
    bracos=Campo(
        ("atencioso", "relapso", "aleatorio", "incoerente"),
        _D,
        "definidos no enunciado da tarefa; aleatorio e o controle critico",
    ),
    partidas_por_par=Campo(20, _P, "por par de pets, cada uma com semente de partida propria"),
    semente_torneio=Campo(7001, _P, "raiz das sementes de partida"),
    definicao_vitoria=Campo(
        "KO (hp do oponente chega a 0) ou, apos max_turnos, maior hp restante; "
        "hp igual = empate, conta 0.5 para cada lado",
        _P,
        "regra simples e simetrica; max_turnos em ConfigArena",
    ),
    metricas=Campo(
        (
            "taxa_vitoria_round_robin",
            "rating_bradley_terry_com_erro_padrao",
            "divergencia_jsd_entre_politicas",
            "saude_humor_finais",
        ),
        _D,
        "lista do enunciado; implementadas uma unica vez em digilab/metrics.py",
    ),
    limiar_divergencia_jsd_bits=Campo(
        0.02,
        _P,
        "JSD media entre politicas de bracos diferentes abaixo disto = politicas "
        "praticamente iguais; a run e REPROVADA por falta de profundidade do ambiente",
    ),
    estados_sonda=Campo(64, _P, "estados sorteados uniformemente para condicionar a divergencia"),
    amostras_por_estado=Campo(200, _P, "amostras Monte Carlo de acao por estado, com numeros aleatorios comuns"),
    semente_sonda=Campo(9001, _P, "raiz das sementes da sonda de divergencia"),
    bootstrap_reamostragens=Campo(10000, _P, "bootstrap percentil sobre sementes"),
    bootstrap_semente=Campo(4242, _P, "semente do bootstrap"),
    nivel_confianca=Campo(0.95, _P, "intervalo de 95%"),
)


# =====================================================================
# Ablacao treino x cuidado. PROTOCOLO_ARENA_V1 acima nao muda (nem o hash).
# =====================================================================

POLITICAS_VALIDAS = ("bandit", "instinto")


@dataclass(frozen=True)
class ProtocoloAblacao(Protocolo):
    """Protocolo da arena com um eixo a mais: a politica de comportamento.

    Os bracos passam a ser dono x politica. Com `instinto` o pet recebe o
    mesmo dono e o mesmo orcamento, mas nao aprende nada: o que sobra de
    diferenca entre donos e efeito do cuidado (estado de vida -> tracos).
    """

    politicas: Campo

    def validar(self) -> None:
        super().validar()
        pols = self.v("politicas")
        if not isinstance(pols, tuple) or not pols:
            raise ValueError(f"politicas precisa ser tupla nao vazia: {pols!r}")
        if len(set(pols)) != len(pols):
            raise ValueError(f"politicas repetidas: {pols}")
        for p in pols:
            if p not in POLITICAS_VALIDAS:
                raise ValueError(f"politica desconhecida: {p!r}")
        for obrigatoria in ("bandit", "instinto"):
            if obrigatoria not in pols:
                raise ValueError(f"politica obrigatoria ausente na ablacao: {obrigatoria}")


def bracos_do_protocolo(p: Protocolo) -> list[tuple[str, str, str]]:
    """(rotulo do braco, dono, politica) na ordem de execucao.

    Protocolo sem eixo de politica = todo braco com bandit e rotulo igual ao
    dono, exatamente como a run canonica v1 sempre fez.
    """
    donos = list(p.v("bracos"))
    if isinstance(p, ProtocoloPersonalidade):
        return [(d, d, "bandit_personalidade") for d in donos]
    if isinstance(p, ProtocoloMemoriaEspacos):
        return [(d, d, "bandit_espacos") for d in donos]
    if isinstance(p, ProtocoloMemoria):
        return [(d, d, "bandit_memoria") for d in donos]
    if not isinstance(p, ProtocoloAblacao):
        return [(d, d, "bandit") for d in donos]
    return [(f"{d}-{pol}", d, pol) for d in donos for pol in p.v("politicas")]


def _campos_v1() -> dict[str, Campo]:
    return PROTOCOLO_ARENA_V1.campos()


PROTOCOLO_ARENA_V1_ABLACAO = ProtocoloAblacao(
    versao="arena-v1-ablacao",
    **_campos_v1(),
    politicas=Campo(
        ("bandit", "instinto"),
        _P,
        "ablacao treino x cuidado: bandit aprende com o dono; instinto recebe o mesmo "
        "dono e orcamento sem aprender. Sementes, orcamento, duracao e vitoria herdados de arena-v1",
    ),
)

# =====================================================================
# Memoria de vida (TAREFA_MEMORIA_EXPRESSAO, Parte B). O nome ARENA_V2 fica
# reservado para pets no combate V2.
# =====================================================================


@dataclass(frozen=True)
class ProtocoloMemoria(Protocolo):
    """arena-v1 + features de memoria curta em TODOS os bracos (inclusive o
    aleatorio). O campo `memoria` carrega os nomes das features e a
    ConfigMemoria inteira, para o hash cobrir os parametros da memoria."""

    memoria: Campo

    def validar(self) -> None:
        super().validar()
        from .memoria import FATORES_MEMORIA

        valor = dict(self.v("memoria"))
        if tuple(valor.get("features", ())) != FATORES_MEMORIA:
            raise ValueError(f"features de memoria do protocolo difere do codigo: {valor.get('features')}")
        esperado = tuple(sorted(asdict(_config.CONFIG_MEMORIA).items()))
        if tuple(tuple(x) for x in valor.get("config", ())) != esperado:
            raise ValueError("ConfigMemoria do protocolo difere de config.py")


def _campo_memoria() -> Campo:
    from .memoria import FATORES_MEMORIA

    return Campo(
        (("features", FATORES_MEMORIA), ("config", tuple(sorted(asdict(_config.CONFIG_MEMORIA).items())))),
        _P,
        "features de memoria curta (latencia do dono por necessidade, repreensoes e elogios com decaimento) "
        "acrescentadas ao contexto do bandit em todos os bracos; parametros de ConfigMemoria",
    )


PROTOCOLO_ARENA_V1_MEMORIA = ProtocoloMemoria(versao="arena-v1-memoria", **_campos_v1(), memoria=_campo_memoria())


@dataclass(frozen=True)
class ProtocoloMemoriaEspacos(ProtocoloMemoria):
    """arena-v1 + memoria por espacos (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 1) em todos os bracos.
    arena-v1-memoria (features com decaimento) continua existindo e reproduzivel."""

    def validar(self) -> None:
        Protocolo.validar(self)
        from .memoria_espacos import FATORES_ESPACOS

        valor = dict(self.v("memoria"))
        if tuple(valor.get("features", ())) != FATORES_ESPACOS:
            raise ValueError(f"features de memoria do protocolo difere do codigo: {valor.get('features')}")
        esperado = json.dumps(asdict(_config.CONFIG_MEMORIA_ESPACOS), sort_keys=True, default=list)
        if valor.get("config") != esperado:
            raise ValueError("ConfigMemoriaEspacos do protocolo difere de config.py")


def _campo_memoria_espacos() -> Campo:
    from .memoria_espacos import FATORES_ESPACOS

    return Campo(
        (("features", FATORES_ESPACOS),
         ("config", json.dumps(asdict(_config.CONFIG_MEMORIA_ESPACOS), sort_keys=True, default=list))),
        _P,
        "memoria por espacos (4 curto, 2 longo, uma por categoria, a mais forte vence; relembra a cada 4 h "
        "acordado): uma feature por categoria ativa (demora, bronca, elogio, carinho) em todos os bracos",
    )


PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS = ProtocoloMemoriaEspacos(
    versao="arena-v1-memoria-espacos", **_campos_v1(), memoria=_campo_memoria_espacos())

PROTOCOLOS = {
    PROTOCOLO_ARENA_V1.versao: PROTOCOLO_ARENA_V1,
    PROTOCOLO_ARENA_V1_ABLACAO.versao: PROTOCOLO_ARENA_V1_ABLACAO,
    PROTOCOLO_ARENA_V1_MEMORIA.versao: PROTOCOLO_ARENA_V1_MEMORIA,
    PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS.versao: PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS,
}


# =====================================================================
# Personalidade, obediencia e desejo (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md),
# sobre a memoria por espacos. Tres variantes com os MESMOS ovos.
# =====================================================================


def _json_personalidade() -> str:
    return json.dumps({"temperamento": asdict(_config.CONFIG_TEMPERAMENTO), "vinculo": asdict(_config.CONFIG_VINCULO),
                       "obediencia": asdict(_config.CONFIG_OBEDIENCIA), "desejo": asdict(_config.CONFIG_DESEJO)},
                      sort_keys=True, default=list)


@dataclass(frozen=True)
class ProtocoloPersonalidade(ProtocoloMemoriaEspacos):
    temperamento_neutro: Campo
    obediencia_desligada: Campo
    personalidade: Campo

    def validar(self) -> None:
        super().validar()
        for nome in ("temperamento_neutro", "obediencia_desligada"):
            if not isinstance(self.v(nome), bool):
                raise ValueError(f"{nome} precisa ser booleano")
        if self.v("personalidade") != _json_personalidade():
            raise ValueError("configs de personalidade do protocolo diferem de config.py")


OVOS_PERSONALIDADE = (101, 202, 303, 404, 505, 606, 707, 808, 909, 1010)


def _protocolo_personalidade(versao: str, neutro: bool, desligada: bool) -> ProtocoloPersonalidade:
    campos = _campos_v1()
    campos["sementes_coorte"] = Campo(OVOS_PERSONALIDADE, _P, "10 ovos (sementes do ovo e do ambiente), os mesmos em "
                                      "todos os bracos e nas tres variantes: decomposicao ovo x braco")
    return ProtocoloPersonalidade(
        versao=versao, **campos, memoria=_campo_memoria_espacos(),
        temperamento_neutro=Campo(neutro, _P, "todos os eixos do temperamento em 0 (reproduz a memoria por espacos)"),
        obediencia_desligada=Campo(desligada, _P, "p de obedecer = 1 sempre (rng_obediencia nunca usada)"),
        personalidade=Campo(_json_personalidade(), _P, "ConfigTemperamento, ConfigVinculo, ConfigObediencia, ConfigDesejo"),
    )


PROTOCOLO_ARENA_V1_PERSONALIDADE = _protocolo_personalidade("arena-v1-personalidade", False, False)
PROTOCOLO_ARENA_V1_PERSONALIDADE_NEUTRO = _protocolo_personalidade("arena-v1-personalidade-neutro", True, False)
PROTOCOLO_ARENA_V1_PERSONALIDADE_SEM_OBEDIENCIA = _protocolo_personalidade("arena-v1-personalidade-sem-obediencia",
                                                                         False, True)
for _p in (PROTOCOLO_ARENA_V1_PERSONALIDADE, PROTOCOLO_ARENA_V1_PERSONALIDADE_NEUTRO,
           PROTOCOLO_ARENA_V1_PERSONALIDADE_SEM_OBEDIENCIA):
    PROTOCOLOS[_p.versao] = _p


# =====================================================================
# Emocao, extremos e habituacao (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 2), sobre a
# personalidade completa. Duas variantes com os MESMOS ovos: habituacao ligada e desligada.
# Variantes novas (e nao campos no protocolo da personalidade): mudar aquele protocolo mudaria o
# hash das runs ja gravadas em artifacts_v1_personalidade/.
# =====================================================================


def _json_habituacao() -> str:
    return json.dumps({"habituacao": asdict(_config.CONFIG_HABITUACAO), "emocao": asdict(_config.CONFIG_EMOCAO),
                       "limiar_extremo": _config.CONFIG_EXPRESSAO.limiar_extremo}, sort_keys=True, default=list)


@dataclass(frozen=True)
class ProtocoloHabituacao(ProtocoloPersonalidade):
    habituacao_ligada: Campo
    habituacao: Campo

    def validar(self) -> None:
        super().validar()
        if not isinstance(self.v("habituacao_ligada"), bool):
            raise ValueError("habituacao_ligada precisa ser booleano")
        if self.v("habituacao") != _json_habituacao():
            raise ValueError("configs de emocao/habituacao do protocolo diferem de config.py")


def _protocolo_habituacao(versao: str, ligada: bool) -> ProtocoloHabituacao:
    base = _protocolo_personalidade(versao, False, False)
    return ProtocoloHabituacao(
        **{f.name: getattr(base, f.name) for f in fields(base)},
        habituacao_ligada=Campo(ligada, _P, "habituacao de eventos negativos (memoria e recompensa do bandit)"),
        habituacao=Campo(_json_habituacao(), _P, "ConfigHabituacao, ConfigEmocao e limiar_extremo"),
    )


PROTOCOLO_ARENA_V1_HABITUACAO = _protocolo_habituacao("arena-v1-personalidade-habituacao", True)
PROTOCOLO_ARENA_V1_SEM_HABITUACAO = _protocolo_habituacao("arena-v1-personalidade-sem-habituacao", False)
for _p in (PROTOCOLO_ARENA_V1_HABITUACAO, PROTOCOLO_ARENA_V1_SEM_HABITUACAO):
    PROTOCOLOS[_p.versao] = _p


# =====================================================================
# educacao-v1: parametros de educacao, lesoes, heranca e equilibrio
# docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, aprovado pelo Matheus em 2026-09-28. Os valores moram em
# config.py; aqui ficam o status e a fonte de cada um. "Aprovado" nao troca PROPOSTO por DECIDIDO:
# DECIDIDO so o que veio de regra ja existente ou de decisao explicita; o resto segue PROPOSTO com fonte.
# O protocolo de run (bracos, sementes, painel) entra na Fase 3, em PLANO_ANALISE_V3.
# =====================================================================

_NV = "fonte da comunidade, nao verificada"
_SF = "sem fonte"
_FONTES_EDUCACAO_V1 = {
    "ConfigEducacao.ligada": (_D, "chave desligada por padrao, como ConfigEscala; runs de educacao usam a ligada"),
    "ConfigEducacao.janela_min": (_D, "docs/cronograma_interacoes.json, janelas.chamado_min"),
    "ConfigEducacao.estagio_inicio_chamados": (_D, "Fase 0, item 6 (decisao do Matheus)"),
    "ConfigEducacao.intervalos_chamado_min": (_D, "docs/cronograma_interacoes.json, estagios.*.intervalos_min"),
    "ConfigEducacao.limiar_necessidade_real": (_D, "igual a ConfigDonos.limiar_necessidade_pedido_adequado"),
    "ConfigEducacao.fracao_falso_base": (_P, _SF + "; no Tamagotchi o chamado falso some com disciplina cheia"),
    "ConfigEducacao.reforco_por_petisco": (_P, _SF),
    "ConfigEducacao.teto_falso": (_P, _SF),
    "ConfigEducacao.disciplina_max": (_D, "escala 0-100, igual as outras barras do jogo"),
    "ConfigEducacao.passo_disciplina": (_P, "medidor de 4 barras do Tamagotchi; " + _NV),
    "ConfigEducacao.acertos_para_aprender": (_P, "Digimon Pendulum/4U (3 acertos); " + _NV),
    "ConfigEducacao.fator_disciplina_ao_evoluir": (_P, _SF),
    "ConfigEducacao.fracao_petisco_alimentar": (_P, _SF),
    "ConfigEducacao.disciplina_por_banheiro": (_D, "Matheus delegou (2026-09-28): 0; com +passo o permissivo se "
                                                      "educava so pelo banheiro (Fase 2 parte 3)"),
    "ConfigEducacao.tipo_slot_aviso": (_D, "cronograma_interacoes.json _meta: coco a cada 120 min = intervalo de higiene"),
    "ConfigEducacao.vinculo_bronca_sem_motivo": (_P, _SF + "; mesma magnitude de ConfigTreino.vinculo_forcar"),
    "ConfigEducacao.custo_humor_acordar": (_P, _SF + "; mesma magnitude de Config.custo_repreender"),
    "ConfigEducacao.limiar_superalimentacao": (_P, _SF),
    "ConfigEducacao.custo_saude_superalimentacao": (_P, _SF),
    "ConfigLesoes.ligada": (_D, "chave desligada por padrao, como ConfigEscala"),
    "ConfigLesoes.efeito_qualificacao": (_D, "Matheus delegou (2026-09-28): sem qualificacao o pet fica adolescente "
                                             "(docs/PLANO_ANALISE_V3.md)"),
    "ConfigLesoes.luta_treina": (_D, "Matheus, opcao B (2026-09-28): desligado; na V3b levou 577/640 pets a forma "
                                     "sombria (artifacts_educacao_v3b)"),
    "ConfigLesoes.experiencia_por_vitoria": (_P, _SF + " (mecanica decidida pelo Matheus em 2026-09-29; valor proposto)"),
    "ConfigLesoes.experiencia_max": (_P, _SF + " (= epsilon_base_pet: um pet muito experiente e disciplinado quase nao erra)"),
    "ConfigLesoes.lutas_minimas_taxa": (_D, "Fase 0; igual a ConfigEvolucaoPesquisa.sparring_minimo_adulto"),
    "ConfigLesoes.limiar_taxa_vitoria": (_P, "Digimon V-Pet Color (80%); " + _NV),
    "ConfigLesoes.prob_lesao_derrota": (_P, _SF),
    "ConfigLesoes.lesoes_para_morte": (_P, "Digimon Ver.20th (20 lesoes); " + _NV),
    "ConfigLesoes.horas_sem_tratar_morte": (_P, "Digimon Ver.20th (6 h); " + _NV),
    "ConfigHeranca.sigma_temperamento": (_P, _SF),
    "ConfigHeranca.estagio_minimo_pais": (_P, _SF),
    "ConfigDuracoes.teste": (_D, "Fase 0, item 8: as duracoes de hoje (ConfigEvolucaoPesquisa)"),
    "ConfigDuracoes.canonica": (_D, "Fase 0, item 8; cronograma_interacoes.json _meta (v-pets: 6 h, 24 h, 36 h)"),
    "ConfigEducacao.epsilon_base_pet": (_D, "igual a ConfigCombateV2.epsilon_bots"),
    "ConfigEducacao.delta_epsilon_indisciplina": (_P, _SF + " (PLANO_ANALISE_V3, secao 2.2)"),
    "ConfigSparring.lutas": (_D, "igual a ConfigLesoes.lutas_minimas_taxa"),
    "ConfigSparring.lutas_braco_lutador": (_P, _SF + " (PLANO_ANALISE_V3, secao 2.5)"),
    "ConfigSparring.intervalo_min": (_P, _SF),
    "ConfigSparring.primeira_apos_inicio_min": (_P, _SF),
    "ConfigEquilibrio.taxa_min": (_P, _SF),
    "ConfigEquilibrio.taxa_max": (_P, _SF),
    "ConfigEquilibrio.margem_max": (_P, _SF),
}


def _valor_config(nome: str) -> Any:
    classe, campo = nome.split(".")
    instancias = {"ConfigEducacao": _config.CONFIG_EDUCACAO, "ConfigLesoes": _config.CONFIG_LESOES,
                  "ConfigHeranca": _config.CONFIG_HERANCA, "ConfigEquilibrio": _config.CONFIG_EQUILIBRIO,
                  "ConfigDuracoes": _config.CONFIG_DURACOES, "ConfigSparring": _config.CONFIG_SPARRING}
    return getattr(instancias[classe], campo)


PARAMETROS_EDUCACAO_V1: dict[str, Campo] = {
    n: Campo(_valor_config(n), st, fonte) for n, (st, fonte) in _FONTES_EDUCACAO_V1.items()}


def validar_parametros_educacao(params: dict[str, Campo] | None = None) -> None:
    """Todo campo das 6 dataclasses tem status e fonte, e o valor registrado bate com config.py."""
    params = PARAMETROS_EDUCACAO_V1 if params is None else params
    esperados = {f"{type(c).__name__}.{f.name}" for c in (_config.CONFIG_EDUCACAO, _config.CONFIG_LESOES,
                                                         _config.CONFIG_HERANCA, _config.CONFIG_EQUILIBRIO,
                                                         _config.CONFIG_DURACOES, _config.CONFIG_SPARRING)
                 for f in fields(c)}
    if set(params) != esperados:
        raise ValueError(f"parametros sem registro: {sorted(esperados - set(params))}; "
                         f"registro sem parametro: {sorted(set(params) - esperados)}")
    for n, c in params.items():
        if c.valor != _valor_config(n):
            raise ValueError(f"{n}: protocolo diz {c.valor!r}, config.py diz {_valor_config(n)!r}")


def hash_parametros_educacao(params: dict[str, Campo] | None = None) -> str:
    params = PARAMETROS_EDUCACAO_V1 if params is None else params
    carga = {"versao": "educacao-v1", "parametros": {n: c.para_dict() for n, c in sorted(params.items())},
             "engine_sha256": sha256_engine()}
    texto = json.dumps(carga, sort_keys=True, ensure_ascii=True, default=_para_json)
    return hashlib.sha256(texto.encode("ascii")).hexdigest()
