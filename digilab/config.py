"""Parametros do motor.

Regra do projeto: nenhum numero magico espalhado pelo codigo. Tudo que
governa a dinamica mora aqui e entra no PROTOCOLO.md congelado.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TICKS_POR_DIA = 1440  # 1 tick = 1 minuto simulado


@dataclass(frozen=True)
class Config:
    # --- decaimento por tick, em unidades de necessidade (escala 0..1) ---
    # Calibrado para que o cuidado atento fique pouco acima do equilibrio e
    # o relapso fique pouco abaixo. Se as duas condicoes sobrevivem ou as
    # duas morrem, o braco de controle nao tem variancia para medir.
    decaimento_fome: float = 1.0 / 1200.0
    decaimento_higiene: float = 1.0 / 1500.0
    decaimento_energia: float = 1.0 / 900.0
    decaimento_humor: float = 1.0 / 1200.0

    # --- recuperacao ---
    energia_por_tick_dormindo: float = 1.0 / 240.0
    humor_por_tick_brincando: float = 1.0 / 120.0

    # --- efeito das acoes do usuario ---
    ganho_alimentar: float = 0.45
    ganho_limpar: float = 0.60
    ganho_brincar_humor: float = 0.25
    custo_brincar_energia: float = 0.08
    custo_brincar_fome: float = 0.05
    ganho_elogiar: float = 0.10
    custo_repreender: float = 0.12

    # --- sujeira ---
    prob_sujeira_por_tick: float = 1.0 / 400.0
    prob_sujeira_pos_refeicao: float = 0.35
    sujeira_maxima: int = 5
    penalidade_higiene_por_sujeira: float = 0.12

    # --- saude: integra o tempo passado em privacao ---
    limiar_privacao: float = 0.15
    dano_saude_por_tick: float = 1.0 / 2000.0
    cura_saude_por_tick: float = 1.0 / 3000.0

    # --- ciclo circadiano: energia decai mais rapido de madrugada ---
    inicio_noite_tick: int = 22 * 60
    fim_noite_tick: int = 7 * 60
    multiplicador_noturno: float = 1.8

    # --- decisao ---
    intervalo_decisao_ticks: int = 15
    janela_atencao_ticks: int = 240  # memoria curta de cuidado recebido

    # --- limites ---
    saciedade_maxima: float = 1.0
    saciedade_minima: float = 0.0

    def e_noite(self, tick_do_dia: int) -> bool:
        if self.inicio_noite_tick > self.fim_noite_tick:
            return tick_do_dia >= self.inicio_noite_tick or tick_do_dia < self.fim_noite_tick
        return self.inicio_noite_tick <= tick_do_dia < self.fim_noite_tick


CONFIG_PADRAO = Config()


# =====================================================================
# v1 - arena com bracos de controle. Tudo abaixo entra no hash do
# protocolo (digilab/protocol.py). Valores sao PROPOSTOS ate que o
# pesquisador os marque como DECIDIDOS no protocolo.
# =====================================================================


@dataclass(frozen=True)
class ConfigBandit:
    """Bandit contextual linear com Thompson sampling (camada 2)."""

    # regressao bayesiana por acao: A = lambda*I + sum x x^T
    lambda_regularizacao: float = 1.0
    # escala da amostra de Thompson: theta~ = theta^ + sqrt(v2) * chol(A^-1) z
    variancia_amostra: float = 0.25
    # mistura do prior da PoliticaInstinto com uniforme, para nenhuma acao
    # ficar com probabilidade zero e o aprendizado poder desbloquea-la
    piso_prior: float = 0.05
    # recompensa explicita
    recompensa_elogio: float = 1.0
    recompensa_repreensao: float = -1.0
    # recompensa implicita: pedido (chamar_atencao) atendido com latencia L
    # vale 1 - L / janela; nao atendido dentro da janela vale o valor abaixo
    janela_latencia_ticks: int = 120
    recompensa_pedido_ignorado: float = -0.5
    # normalizacao da feature "ticks desde o ultimo cuidado"
    escala_ticks_desde_cuidado: float = 480.0
    # bisseccao para recuperar o limiar de rng.random() no prior
    iteracoes_bisseccao_prior: int = 40


@dataclass(frozen=True)
class ConfigDonos:
    """Donos sinteticos. O orcamento em si mora no protocolo."""

    passo_ticks: int = 15                  # o dono olha o pet a cada passo
    max_interacoes_por_passo: int = 6      # teto fisico por passo, igual para todos
    # DonoAtencioso / DonoIncoerente: gatilhos de cuidado
    limiar_alimentar: float = 0.50
    limiar_limpar: float = 0.50
    sujeira_para_limpar: int = 2
    limiar_humor_brincar: float = 0.40
    # regra de coerencia do feedback (o que e comportamento "adequado")
    limiar_energia_sono_adequado: float = 0.40
    limiar_necessidade_pedido_adequado: float = 0.35
    # DonoRelapso: quantas vezes por dia aparece
    visitas_por_dia_relapso: int = 3   # 16/dia em 3 visitas cabe no teto de 6 por passo
    # DonoIncoerente: probabilidade de elogiar (senao repreende)
    prob_elogio_incoerente: float = 0.5


@dataclass(frozen=True)
class ConfigTracos:
    """Camada 3: tracos = media movel exponencial lenta da distribuicao de acoes."""

    alfa_ema: float = 1.0 / 288.0  # ~3 dias de decisoes (96 por dia)


@dataclass(frozen=True)
class ConfigArena:
    """Combate por turnos com revelacao simultanea, nucleo pedra-papel-tesoura de 5."""

    hp_inicial: float = 100.0
    dano_base: float = 10.0
    ganho_afinidade: float = 0.5
    max_turnos: int = 40
    # observacao sintetica de combate: necessidades fixas, o que varia e o
    # hp (entra no lugar da energia) e a vantagem (entra no lugar do humor)
    fome_arena: float = 0.70
    higiene_arena: float = 0.70
    saude_arena: float = 1.00
    hora_arena: float = 0.50
    # mapeamento congelado acao do pet -> acao de combate (heranca da disposicao)
    mapa_pet_combate: tuple = (
        ("ocioso", "bloqueio"),
        ("dormir", "bloqueio"),
        ("comer", "agarrao"),
        ("brincar", "golpe"),
        ("chamar_atencao", "carga"),
        ("explorar", "finta"),
        ("emburrar", "agarrao"),
    )


@dataclass(frozen=True)
class ConfigMetricas:
    ridge_bradley_terry: float = 0.01
    tolerancia_bradley_terry: float = 1e-10
    max_iter_bradley_terry: int = 200


CONFIG_BANDIT = ConfigBandit()
CONFIG_DONOS = ConfigDonos()
CONFIG_TRACOS = ConfigTracos()
CONFIG_ARENA = ConfigArena()
CONFIG_METRICAS = ConfigMetricas()


# =====================================================================
# Combate V2 (bateria de bots). NAO entra no hash do protocolo arena-v1
# (configs_congelados lista as dataclasses da v1 explicitamente); a bateria
# tem hash proprio. Todos os valores sao PROPOSTOS; so mudam pelo
# procedimento de calibracao (sementes de calibracao, nunca as de validacao).
# =====================================================================


@dataclass(frozen=True)
class ConfigCombateV2:
    # condicao fisica neutra (usada por todos os bots na bateria)
    # calibrado 100 -> 70 (sementes de calibracao): mediana de turnos 34 -> 25 (G4)
    hp_neutro: float = 70.0
    guts_inicial_neutro: int = 50
    regen_guts_neutro: int = 8
    guts_max: int = 100
    t_max: int = 40
    # custos de guts
    custo_golpe_rapido: int = 10
    custo_preparar_pesado: int = 15
    # calibrado 15 -> 20 (sementes de calibracao): com 15 o disparo se paga com a
    # regeneracao e o atirador domina todos os fixos (G1)
    custo_disparo: int = 20
    custo_esquivar: int = 20
    # dano
    dano_golpe_rapido: float = 8.0
    dano_pesado: float = 25.0
    dano_disparo: float = 6.0
    # multiplicadores de dano recebido
    mult_defender: float = 0.3
    mult_defender_contra_pesado: float = 0.6   # pesado quebra guarda
    mult_carregar: float = 1.5
    # ganhos de guts
    guts_extra_defender: int = 5
    guts_carregar: int = 25
    # gambits
    max_regras: int = 8
    max_condicoes_por_regra: int = 2
    fracoes_hp: tuple = (0.25, 0.5, 0.75)
    limiares_guts: tuple = (20, 40, 60)
    k_repete: tuple = (2, 3)
    janela_frequente: int = 5
    limiar_frequente: float = 0.4
    epsilon_bots: float = 0.05
    # oraculo (referencia fora da linguagem): valor de 1 passo = diferenca de
    # fracao de hp + peso_guts * diferenca de guts
    peso_guts_oraculo: float = 0.002
    # pesado preparado e ainda nao executado vale este peso x dano_pesado / hp_max
    # do alvo, se a distancia for perto (sem isso o valor de 1 passo nunca prepara)
    peso_pesado_pendente_oraculo: float = 0.5


@dataclass(frozen=True)
class ConfigBateriaCombate:
    """Limiares dos gates G1-G7 da bateria (todos PROPOSTOS)."""

    peso_minimo_suporte: float = 0.05        # estrategia no suporte do equilibrio
    iteracoes_fictitious_play: int = 20000
    suporte_minimo: int = 3                  # G1
    taxa_min_adaptativo_vs_aleatorio: float = 0.70   # G2
    tolerancia_espelho: float = 0.03         # G3
    partidas_replay_amostra: int = 200       # G3
    mediana_turnos_min: float = 8.0          # G4
    mediana_turnos_max: float = 30.0         # G4
    fracao_max_limite_turnos: float = 0.20   # G4
    fracao_min_acao: float = 0.03            # G5
    variacao_hp: float = 0.10                # G6: hp_max * (1 +- isto)
    variacao_guts_inicial: int = 10          # G6
    partidas_g6_por_semente: int = 50        # G6 (por par)
    permutacoes_g7: int = 5                  # G7
    semente_permutacoes_g7: int = 7007       # G7
    partidas_g7_por_semente: int = 100       # G7 (por permutacao)
    taxa_min_g7: float = 0.60                # G7


CONFIG_COMBATE_V2 = ConfigCombateV2()
CONFIG_BATERIA_COMBATE = ConfigBateriaCombate()


# =====================================================================
# Motivo e expressao (Parte A da TAREFA_MEMORIA_EXPRESSAO). Somente leitura:
# nao muda decisao nenhuma. NAO entra no hash de arena-v1 (configs_congelados
# lista a v1 explicitamente) nem no da bateria do combate V2 (que cobre so
# ConfigCombateV2, ConfigBateriaCombate e os fontes de combate_v2/).
# =====================================================================


@dataclass(frozen=True)
class ConfigExpressao:
    # PROVISORIO: estagio por idade em dias simulados. Quando a evolucao existir
    # no motor, o estagio vem dela. Limite superior (exclusivo) de cada estagio.
    dias_fim_bebe: float = 1.0
    dias_fim_crianca: float = 3.0
    dias_fim_adolescente: float = 7.0
    # vida: fator so e citado se |contribuicao| >= isto (LIMIAR_MOTIVO)
    limiar_motivo: float = 0.05
    # bebe: faixas de humor para o emote
    humor_alegre: float = 0.66
    humor_neutro: float = 0.33
    # adendo DF 2.2: um eixo de temperamento ou de carater so e descrito se |valor| >= isto (PROPOSTO);
    # na faixa central nao ha texto (o Dwarf Fortress nao descreve tracos medianos)
    limiar_extremo: float = 0.2


CONFIG_EXPRESSAO = ConfigExpressao()


# =====================================================================
# Memoria de vida (Parte B). Entra no hash de PROTOCOLO_ARENA_V1_MEMORIA
# (campo `memoria`), nao no de arena-v1. Todos os valores PROPOSTOS.
# =====================================================================


@dataclass(frozen=True)
class ConfigMemoria:
    # pedido (chamar_atencao) conta para a necessidade mais baixa entre fome e
    # higiene, se ela estiver abaixo disto; senao e pedido generico (ignorado)
    limiar_necessidade_pedido: float = 0.5
    # latencia normalizada = min(1, latencia / janela); pedido nao atendido
    # dentro da janela vale 1 (sem evento de origem)
    janela_latencia_ticks: int = 240
    # repreensoes e elogios recentes: soma de exp(-dt / tau), normalizada por escala
    tau_feedback_ticks: float = 360.0
    escala_feedback: float = 3.0


CONFIG_MEMORIA = ConfigMemoria()


# =====================================================================
# Memoria por espacos (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 1; inspirada no
# Dwarf Fortress). Classe separada de ConfigMemoria de proposito: o protocolo
# arena-v1-memoria (features com decaimento) continua reproduzivel. Entra no
# hash de PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS. Todos os valores PROPOSTOS.
# =====================================================================


def _intensidades_categoria() -> dict:
    # None = intensidade vem do evento (demora: latencia normalizada pela janela)
    return {"demora": None, "bronca": 1.0, "elogio": 1.0, "carinho": 0.5, "sujeira": 0.5, "treino_forcado": 1.0}


@dataclass(frozen=True)
class ConfigMemoriaEspacos:
    n_curto: int = 4
    n_longo: int = 2
    d_curto_ticks: int = 12 * 60             # 12 h simuladas no curto prazo
    relembrar_ticks_acordado: int = 4 * 60   # relembra a cada 4 h ACORDADO (cronograma, sem sorteio)
    # decaimento da ativacao entre relembrancas (o adendo nao fixa: mesma constante da memoria B1)
    tau_ativacao_ticks: float = 360.0
    categorias: dict = field(default_factory=_intensidades_categoria)
    # sujeira: TAREFA_CUIDADO_CORPORAL; treino_forcado: TAREFA_TREINO_SOMBRIO
    ativas: tuple = ("demora", "bronca", "elogio", "carinho")
    # demora: pedido (chamar_atencao) conta para a necessidade mais baixa entre fome e higiene
    limiar_necessidade_pedido: float = 0.5
    janela_latencia_ticks: int = 240


CONFIG_MEMORIA_ESPACOS = ConfigMemoriaEspacos()


# =====================================================================
# Personalidade, obediencia e desejo (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md),
# sobre a memoria por espacos. Entram no hash de PROTOCOLO_ARENA_V1_PERSONALIDADE.
# Todos PROPOSTOS. Todo fator de temperamento vale EXATAMENTE 1.0 com o eixo em 0
# (exp(0) = 1, 1 - k*0 = 1): temperamento neutro reproduz a memoria por espacos.
# =====================================================================


@dataclass(frozen=True)
class ConfigTemperamento:
    amplitude: float = 1.0                                  # sorteio uniforme em [-a, a] por eixo
    k_curiosidade: float = 0.6931471805599453               # variancia da amostra x 2^curiosidade
    k_teimosia: float = 0.5                                 # peso da repreensao x (1 - 0,5 teimosia)
    k_sensibilidade: float = 0.5                            # elogio x (1 + 0,5 s); repreensao x (1 - 0,5 s)
    k_rancor: float = 0.6931471805599453                    # tau de demora e bronca x 2^rancor
    categorias_rancor: tuple = ("demora", "bronca")


@dataclass(frozen=True)
class ConfigVinculo:
    inicial: float = 0.5
    alfa: float = 0.1                                       # media movel: v += alfa * peso * (amostra - v)
    peso_atendimento: float = 1.0                           # pedido atendido: 1 - latencia/janela; perdido: 0
    peso_coerencia: float = 1.0                             # feedback com o mesmo sinal dos anteriores na janela
    peso_desejo: float = 0.5                                # vontade respeitada pelo dono na janela
    janela_latencia_ticks: int = 240
    janela_coerencia_ticks: int = 1440
    janela_desejo_ticks: int = 60


@dataclass(frozen=True)
class ConfigObediencia:
    # p = logistica(b0 + b_vinculo*vinculo - b_teimosia*teimosia - b_conflito*conflito)
    b0: float = 1.0
    b_vinculo: float = 2.0
    b_teimosia: float = 1.0
    b_conflito: float = 2.0
    # conflito: a necessidade mais urgente (abaixo do limiar) e a acao do dono nao a atende;
    # conflito = (limiar - nivel) / limiar
    limiar_conflito: float = 0.3
    prob_fazer_outra: float = 0.5                           # desobediencia: fazer_outra, senao recusar
    # so acoes de cuidado podem ser recusadas; feedback (elogiar/repreender) sempre chega
    acoes_sujeitas: tuple = ("alimentar", "limpar", "brincar", "acariciar")
    limiar_motivo: float = 0.05                             # contribuicao negativa minima para virar fator


@dataclass(frozen=True)
class ConfigDesejo:
    limiar_necessidade: float = 0.3                         # nivel abaixo disto vira desejo de necessidade
    limiar_vontade: float = 0.1                             # margem da media da posterior (1a - 2a acao)
    k_cumprimento_ticks: int = 60


@dataclass(frozen=True)
class ConfigEmocao:
    # adendo DF 2.1: eixo do temperamento escolhe a emocao se |valor| passar disto (o de maior modulo vence)
    limiar_eixo: float = 0.2
    # "a valencia multiplica a intensidade da memoria": muda a memoria e, com ela, o aprendizado; o
    # adendo pede emocao somente leitura (2.4/2.5), entao fica desligado (desvio registrado)
    modula_memoria: bool = False


@dataclass(frozen=True)
class ConfigHabituacao:
    # adendo DF 2.3: intensidade_efetiva = intensidade * H ** repeticoes_recentes (eventos negativos da
    # mesma categoria nas ultimas `janela_ticks`, antes deste). Tudo PROPOSTO.
    h: float = 0.8
    janela_ticks: int = 12 * 60
    categorias: tuple = ("demora", "bronca")                 # negativas
    # teimosia acelera a habituacao a broncas: H_bronca = h * (1 - k * max(0, teimosia))
    k_teimosia_bronca: float = 0.2


CONFIG_TEMPERAMENTO = ConfigTemperamento()
CONFIG_VINCULO = ConfigVinculo()
CONFIG_OBEDIENCIA = ConfigObediencia()
CONFIG_DESEJO = ConfigDesejo()
CONFIG_EMOCAO = ConfigEmocao()
CONFIG_HABITUACAO = ConfigHabituacao()


# =====================================================================
# Combate V2.1: arvore de evolucao integrada ao combate (tecnicas por linha,
# passivas por forma adulta, stats por especie/temperamento/carater/arquetipo).
# Transcricao de docs/catalogo_pets.json e docs/arvore_evolucao.json (um teste
# confere que nao divergem). NAO entra no hash de arena-v1 nem no da bateria
# V2 base: a base continua reproduzivel. Todos os numeros PROPOSTOS.
# =====================================================================

STATS_V21 = ("vigor", "folego", "recuperacao", "forca", "mira", "guarda")
ESTAGIOS_V21 = ("bebe", "crianca", "adolescente", "adulto")


def _catalogo_especies() -> dict:
    return {
        "brasa": {"vigor": 9, "folego": 10, "recuperacao": 7, "forca": 14, "mira": 8, "guarda": 12},
        "cirro": {"vigor": 7, "folego": 11, "recuperacao": 11, "forca": 7, "mira": 15, "guarda": 9},
        "ferrugem": {"vigor": 13, "folego": 8, "recuperacao": 8, "forca": 9, "mira": 7, "guarda": 15},
        "limo": {"vigor": 11, "folego": 12, "recuperacao": 15, "forca": 6, "mira": 7, "guarda": 9},
        "faisca": {"vigor": 8, "folego": 13, "recuperacao": 9, "forca": 11, "mira": 11, "guarda": 8},
        "seixo": {"vigor": 15, "folego": 7, "recuperacao": 7, "forca": 12, "mira": 7, "guarda": 12},
    }


def _catalogo_temperamento() -> dict:
    return {
        "curiosidade": {"mira": 2, "folego": 1, "guarda": -2, "vigor": -1},
        "teimosia": {"guarda": 2, "vigor": 1, "recuperacao": -2, "mira": -1},
        "sensibilidade": {"recuperacao": 2, "folego": 1, "forca": -2, "guarda": -1},
        "rancor": {"forca": 2, "mira": 1, "recuperacao": -2, "folego": -1},
    }


def _catalogo_carater() -> dict:
    return {
        "impetuoso": {"forca": 3, "folego": 1, "guarda": -3, "recuperacao": -1},
        "paciente": {"guarda": 3, "recuperacao": 1, "forca": -3, "folego": -1},
        "atento": {"mira": 3, "recuperacao": 1, "vigor": -3, "forca": -1},
        "resistente": {"vigor": 3, "guarda": 1, "mira": -3, "folego": -1},
    }


def _arquetipos_crianca() -> dict:
    return {
        "sereno": {"recuperacao": 2, "guarda": 1, "forca": -2, "mira": -1},
        "arisco": {"forca": 2, "mira": 1, "recuperacao": -2, "guarda": -1},
    }


def _arquetipos_adolescente() -> dict:
    # linha -> eixo de carater, tecnica, modificadores
    return {
        "brigao": {"eixo": "impetuoso", "tecnica": "investida",
                   "stats": {"forca": 3, "folego": 1, "guarda": -2, "mira": -2}},
        "guardiao": {"eixo": "paciente", "tecnica": "contra_golpe",
                     "stats": {"guarda": 3, "recuperacao": 1, "forca": -2, "folego": -2}},
        "cacador": {"eixo": "atento", "tecnica": "marcar",
                    "stats": {"mira": 3, "folego": 1, "vigor": -2, "guarda": -2}},
        "colosso": {"eixo": "resistente", "tecnica": "pele_dura",
                    "stats": {"vigor": 3, "guarda": 1, "mira": -2, "recuperacao": -2}},
    }


def _arquetipos_adulto() -> dict:
    # linha -> eixo complementar e as duas formas (sinal do eixo, modificadores)
    return {
        "brigao": {"eixo_complementar": "paciente", "formas": {
            "duelista": {"sinal": ">=0", "stats": {"mira": 1, "guarda": 1, "vigor": -1, "folego": -1}},
            "furioso": {"sinal": "<0", "stats": {"forca": 2, "guarda": -2}}}},
        "guardiao": {"eixo_complementar": "impetuoso", "formas": {
            "espelho": {"sinal": ">=0", "stats": {"forca": 1, "mira": 1, "vigor": -1, "recuperacao": -1}},
            "muralha": {"sinal": "<0", "stats": {"vigor": 2, "forca": -2}}}},
        "cacador": {"eixo_complementar": "resistente", "formas": {
            "sentinela": {"sinal": ">=0", "stats": {"vigor": 1, "guarda": 1, "mira": -1, "forca": -1}},
            "emboscador": {"sinal": "<0", "stats": {"mira": 2, "vigor": -2}}}},
        "colosso": {"eixo_complementar": "atento", "formas": {
            "vigia": {"sinal": ">=0", "stats": {"mira": 1, "recuperacao": 1, "forca": -1, "folego": -1}},
            "tita": {"sinal": "<0", "stats": {"forca": 2, "recuperacao": -2}}}},
    }


@dataclass(frozen=True)
class ConfigCatalogo:
    stat_neutro: int = 10
    stat_min: int = 3
    stat_max: int = 20
    orcamento_especie: int = 60
    especies: dict = field(default_factory=_catalogo_especies)
    # decisao do Matheus (2026-09-24): 4 especies no jogo, cada forma com sprite
    # proprio (a folha tem ~60 Digimon = 4 x 15 formas). As 6 continuam no
    # catalogo; so estas entram no jogo e na bateria V2.1.
    especies_ativas: tuple = ("brasa", "cirro", "ferrugem", "limo")
    temperamento: dict = field(default_factory=_catalogo_temperamento)
    carater: dict = field(default_factory=_catalogo_carater)
    arquetipos_crianca: dict = field(default_factory=_arquetipos_crianca)
    arquetipos_adolescente: dict = field(default_factory=_arquetipos_adolescente)
    arquetipos_adulto: dict = field(default_factory=_arquetipos_adulto)
    mult_estagio: dict = field(default_factory=lambda: {"bebe": 0.4, "crianca": 0.6, "adolescente": 0.8, "adulto": 1.0})
    condicao_mult_min: float = 0.95
    condicao_mult_max: float = 1.05
    # transicoes (arvore_evolucao.json)
    limiar_cuidado_sereno: float = 0.8
    sparring_minimo_adulto: int = 10


@dataclass(frozen=True)
class ConfigCombateV21:
    # conversao stat -> combate (catalogo_pets.json). Com stat neutro 10:
    # hp 100, guts 50/100, regen 8, multiplicadores 1.0.
    hp_base: float = 70.0
    hp_por_vigor: float = 3.0
    guts_inicial_base: float = 30.0
    guts_inicial_por_folego: float = 2.0
    guts_max_base: float = 80.0
    guts_max_por_folego: float = 2.0
    regen_base: float = 4.0
    regen_por_recuperacao: float = 0.4
    mult_base: float = 0.7              # forca e mira: 0.7 + 0.03 * stat
    mult_por_ponto: float = 0.03
    guarda_base: float = 1.3            # defender: mult * (1.3 - 0.03 * guarda)
    guarda_por_ponto: float = 0.03
    # tecnicas (adolescente e adulto)
    custo_investida: int = 20
    dano_investida: float = 8.0
    mult_parry_investida: float = 0.0   # defender contra investida (parry)
    custo_contra_golpe: int = 15
    fracao_contra_golpe: float = 0.5    # do dano BRUTO corpo a corpo, devolvido
    custo_marcar: int = 10
    turnos_marcar: int = 3
    mult_marcar: float = 2.0
    custo_pele_dura: int = 20
    turnos_pele_dura: int = 2           # este turno e o proximo
    mult_pele_dura: float = 0.5
    # passivas (adulto)
    dano_extra_duelista: float = 4.0
    limiar_hp_furioso: float = 0.5
    mult_furioso: float = 1.25
    # calibrado 0.5 -> 1.0 (sementes de calibracao): com 0.5 o espelho perde a
    # troca contra o disparo marcado e a passiva nao vale nada contra o cacador
    fracao_espelho_disparo: float = 1.0
    guts_extra_muralha: int = 3
    recarga_sentinela: int = 4
    mult_emboscador: float = 2.0
    mult_tita: float = 1.3
    # gambits por estagio
    max_regras_crianca: int = 3
    max_regras_adolescente: int = 5
    max_regras_adulto: int = 8
    turnos_execucao: tuple = (5, 10, 20)
    # carater canonico dos bots: eixo da linha e eixo complementar
    carater_bot_linha: float = 0.5
    carater_bot_complementar: float = 0.25


# numeros de tecnica/passiva perturbados no gate E5 (+-10%)
CAMPOS_TECNICA_PASSIVA_V21 = (
    "custo_investida", "dano_investida", "custo_contra_golpe", "fracao_contra_golpe",
    "custo_marcar", "turnos_marcar", "mult_marcar", "custo_pele_dura", "turnos_pele_dura", "mult_pele_dura",
    "dano_extra_duelista", "limiar_hp_furioso", "mult_furioso", "fracao_espelho_disparo",
    "guts_extra_muralha", "recarga_sentinela", "mult_emboscador", "mult_tita",
)


@dataclass(frozen=True)
class ConfigBateriaV21:
    """Limiares dos gates E1-E5 (PROPOSTOS, docs/ESPEC_COMBATE_V21.md)."""

    peso_minimo_suporte: float = 0.05
    iteracoes_fictitious_play: int = 20000
    suporte_minimo_e1: int = 4
    fracao_min_tecnica: float = 0.05       # E3
    taxa_min_e4: float = 0.60
    taxa_max_e4: float = 0.85
    perturbacao_e5: float = 0.10
    partidas_e3_por_semente: int = 40      # por par
    partidas_e4_por_semente: int = 100     # por par
    partidas_e5_por_semente: int = 20      # por par, no E1 perturbado


def _chamados_bebe() -> dict:
    return {"fome": 30, "higiene": 60, "carinho": 45}


def _eixo_traco() -> dict:
    # caráter: cada eixo junta os tracos de combate (ConfigArena.mapa_pet_combate) que se parecem com ele
    return {"impetuoso": ("golpe", "carga"), "paciente": ("bloqueio",), "atento": ("finta",),
            "resistente": ("agarrao",)}


@dataclass(frozen=True)
class ConfigEvolucaoPesquisa:
    """Evolucao do pet de pesquisa (ESPEC_EVOLUCAO_COMBATE.md, secao Pesquisa). Todos PROPOSTOS.

    Duracoes e chamados do bebe: docs/cronograma_interacoes.json ("a pesquisa usa os valores acima").
    """

    dur_bebe_min: int = 180
    dur_crianca_min: int = 720
    dur_adolescente_min: int = 1080
    chamados_bebe_min: dict = field(default_factory=_chamados_bebe)   # intervalo de cada chamado no bebe
    janela_chamado_min: int = 15
    # acoes do dono que atendem cada chamado
    atende: dict = field(default_factory=lambda: {"fome": ("alimentar",), "higiene": ("limpar",),
                                                   "carinho": ("acariciar", "brincar")})
    # carater = desvio medio de probabilidade (politica - instinto) nas sondas / escala, cortado em [-1, 1]
    escala_carater: float = 0.05
    eixo_traco: dict = field(default_factory=_eixo_traco)
    # temperamento do ovo: cada eixo uniforme em [-amplitude, amplitude]
    amplitude_temperamento: float = 1.0
    # condicao fisica (do cuidado) = min + (max - min) * saude no fim da vida
    # sparring minimo: dado como cumprido na simulacao (o sparring nao treina a politica nem gasta orcamento)
    sparring_simulado: int = 10


CONFIG_EVOLUCAO_PESQUISA = ConfigEvolucaoPesquisa()


def _npcs() -> dict:
    # docs/pve_treino.json > npcs: stats uniformes no total, estilo fixo em gambits (bots da bateria V2)
    return {
        "tier1_brutamontes": {"total_stats": 72, "estilo": "agressivo", "estagio_minimo_sugerido": "crianca"},
        "tier2_sentinela": {"total_stats": 80, "estilo": "contragolpe", "estagio_minimo_sugerido": "adolescente"},
        "tier3_soberano": {"total_stats": 90, "estilo": "adaptativo", "estagio_minimo_sugerido": "adulto"},
    }


@dataclass(frozen=True)
class ConfigCampanha:
    """Campanha contra NPCs (TAREFA_TREINO_SOMBRIO, secao 5), SEM treino ainda. PROPOSTOS."""

    npcs: dict = field(default_factory=_npcs)
    partidas_por_par: int = 100          # lados trocados na metade
    epsilon_npc: float = 0.05


CONFIG_CAMPANHA = ConfigCampanha()
CONFIG_CATALOGO = ConfigCatalogo()
CONFIG_COMBATE_V21 = ConfigCombateV21()
CONFIG_BATERIA_V21 = ConfigBateriaV21()
