"""Parametros do motor.

Regra do projeto: nenhum numero magico espalhado pelo codigo. Tudo que
governa a dinamica mora aqui e entra no PROTOCOLO.md congelado.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, replace

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
class ConfigCombateV2C(ConfigCombateV2):
    """Base corrigida (docs/TAREFA_CORRECAO_COMBATE.md, Etapa 1). Cada chave liga UMA mudanca; os
    valores padrao reproduzem a V2 original. As etapas C5 (custo_esquivar) e C6 (guts_extra_defender)
    mexem em campos da propria ConfigCombateV2. Todos PROPOSTOS."""

    # C1 finta: no turno de execucao do pesado, executar ou fintar (golpe rapido que acerta quem
    # esquivou e nao quebra guarda); condicao de gambit "executando_pesado"
    finta: bool = False
    # C2 parry: defender contra golpe rapido (ou finta) devolve este dano ao atacante (0 = desligado)
    dano_parry: float = 0.0
    # C3 fuga condicionada: recuar so afasta se o oponente nao avancar; avancar ilegal em perto,
    # recuar ilegal em longe
    fuga_condicionada: bool = False
    # C4 morte subita: a partir deste turno todo dano x mult (0 = desligado)
    turno_morte_subita: int = 0
    mult_morte_subita: float = 1.5
    # Etapa 2: oraculo com busca de N passos (1 = o da V2); com 2+, a distribuicao do oponente em cada
    # no fica nas `oraculo_top_oponente` acoes mais frequentes (custo)
    oraculo_passos: int = 1
    oraculo_top_oponente: int = 3
    # redesenho dos bots (pedido do Matheus apos a V2C reprovar): bots.GAMBITS_V2C no lugar dos da V2
    bots_v2c: bool = False


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


@dataclass(frozen=True)
class ConfigBateriaV2C:
    """Gates novos da TAREFA_CORRECAO_COMBATE (Etapa 2). Todos PROPOSTOS."""

    # G6b espelho: mesmo estilo, condicao no extremo da faixa (+-5% de hp; guts inicial +-2)
    variacao_hp_g6b: float = 0.05
    variacao_guts_g6b: int = 2
    taxa_max_g6b: float = 0.65
    partidas_g6b_por_semente: int = 50
    # G8 robustez: cada parametro numerico do combate +-10%, um por vez; G1 vale em >= 80%
    perturbacao_g8: float = 0.10
    fracao_min_g8: float = 0.80
    partidas_g8_por_semente: int = 20
    # G9 decisividade: com epsilon 0,2, no maximo 50% dos confrontos com taxa < 0,1 ou > 0,9
    epsilon_g9: float = 0.20
    extremo_g9: float = 0.10
    fracao_max_g9: float = 0.50
    partidas_g9_por_semente: int = 40


CONFIG_COMBATE_V2 = ConfigCombateV2()
CONFIG_BATERIA_COMBATE = ConfigBateriaCombate()
CONFIG_BATERIA_V2C = ConfigBateriaV2C()


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


@dataclass(frozen=True)
class ConfigVinculoSituacao:
    """Vinculo B, previsibilidade + desejo (docs/V2_VINCULO_PROPOSTA.md, alternativa B; decisao do Matheus, 2026-10-01;
    plano docs/PLANO_ANALISE_V2_VINCULO.md). A parte da ConfigVinculo de proposito: ela entra no hash dos protocolos da
    personalidade, e as runs gravadas precisam continuar reproduzindo. Tudo PROPOSTO (protocol.PARAMETROS_VINCULO_B).
    Ligada: o pedido nao abre (o atendimento sai do vinculo) e a coerencia agrupa o historico de feedback por (acao do
    pet, situacao do pet); a situacao = (necessidade baixa, cansado, noite) e lida da observacao com que o pet decidiu
    a acao atual. Desejo, ajustes diretos, pausa de treino e teto da sombria nao mudam. Desligada: nada muda."""
    ligada: bool = False
    limiar_necessidade: float = 0.5           # = ConfigMemoriaEspacos.limiar_necessidade_pedido (o criterio do pedido)
    limiar_energia: float = 0.25              # = a regra de exaustao da PoliticaInstinto ("energia < 0,25 -> dormir")
    # noite: ConfigPadrao.e_noite, pela hora do vetor de estado (round(hora * TICKS_POR_DIA))


CONFIG_TEMPERAMENTO = ConfigTemperamento()
CONFIG_VINCULO = ConfigVinculo()
CONFIG_VINCULO_SITUACAO = ConfigVinculoSituacao()
CONFIG_VINCULO_B_LIGADA = ConfigVinculoSituacao(ligada=True)
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


@dataclass(frozen=True)
class ConfigCombateV21C(ConfigCombateV21):
    """V2.1 corrigida (TAREFA_CORRECAO_COMBATE, Etapa 3). Padroes = V2.1 original. As mudancas da base
    (C1-C4) vem da ConfigCombateV2C em Regras.base; a correcao da Ferrugem mexe em hp_base/hp_por_vigor."""

    # marcar: a marca se perde se o cacador receber dano corpo a corpo ou terminar o turno em perto
    marca_fragil: bool = False


@dataclass(frozen=True)
class ConfigCombateV21D(ConfigCombateV21C):
    """Reequilibrio dos arquetipos, rodadas 1 e 2 (docs/EQUILIBRIO_RODADA1.md e EQUILIBRIO_RODADA2.md, a partir de
    docs/DIAGNOSTICO_ARQUETIPOS.md). Chaves DESLIGADAS por padrao: com todas em False a luta e a da V21C. Classe propria (e nao campos novos na
    V21C) para o asdict e o hash das configs V21C gravadas nao mudarem. PROPOSTO, so calibracao."""

    # candidato A: o preparo do pesado feito sob pele_dura nao aparece para o rival em oponente_preparando
    # (a pele esconde o pesado, alem de protege-lo). A condicao do vigia (oponente_vai_preparar) nao muda.
    preparo_sob_pele_oculto: bool = False
    # candidato C: a muralha luta com a lista de gambits derivada da do espelho (bots.GAMBITS_MURALHA_V21D)
    muralha_lista_espelho: bool = False
    # --- rodada 2 (docs/EQUILIBRIO_RODADA2.md), tambem desligadas por padrao ---
    # D2: a investida erra quando o alvo recua a partir da distancia media, e o recuo vale contra ela (excecao a
    # fuga condicionada so para a investida; o avanco comum continua prendendo quem recua)
    investida_erra_contra_recuo: bool = False
    # E1: recuar nao afasta quando o oponente prepara o pesado no mesmo turno (a fuga condicionada estendida ao
    # preparo; vale para qualquer forma que prepara)
    preparo_prende: bool = False
    # E2: lista variante que bate rapido de perto contra quem recua com frequencia, antes de preparar o pesado
    # (bots.gambits_adulto); uma chave para o tita e outra para o vigia, para medir cada uma sozinha
    tita_bate_em_quem_recua: bool = False
    vigia_bate_em_quem_recua: bool = False
    # V: lista variante do vigia que recua do preparo que ele nao consegue interromper (o do rival que usa pele_dura)
    vigia_recua_do_preparo_sob_pele: bool = False


@dataclass(frozen=True)
class ConfigCombateV21E(ConfigCombateV21D):
    """Rodada de equilibrio geral, fase 1: as formas (docs/PLANO_EQUILIBRIO_GERAL.md, docs/EQUILIBRIO_GERAL.md). Parte da
    variante V21D validada (a_c_e2v_v: as quatro chaves dela ligadas) e acrescenta listas variantes das formas. Chaves
    DESLIGADAS por padrao: com todas em False a luta e a da V21D com as mesmas chaves. Classe propria (e nao campos novos
    na V21D) para o asdict e o hash das configs V21D gravadas nao mudarem. PROPOSTO, so calibracao (3101..3505).

    A base (custo do golpe rapido, dano do parry, a fuga condicionada C3) foi medida na calibracao e nao mudou: nenhum
    valor tirou o furioso de ~0,72 (docs/EQUILIBRIO_GERAL.md, fase 1). O que o tira e o parry que ja existe (C2 da V2C):
    as formas que o golpe rapido repetido esmagava passam a se defender dele. Listas em bots.gambits_adulto."""

    # o duelista e o tita defendem de perto quando o oponente usa golpe_rapido com frequencia (a regra entra logo depois
    # das que leem o preparo do oponente; sai "guts abaixo de 20 -> carregar": a final defender tambem recupera guts)
    duelista_defende_do_golpe: bool = False
    tita_defende_do_golpe: bool = False
    # as guardias nao carregam (sai "guts abaixo de 40 -> carregar": carregar recebe dano x1,5, e a final defender
    # recupera guts); a da muralha pede muralha_lista_espelho
    espelho_sem_carregar: bool = False
    muralha_sem_carregar: bool = False
    # a muralha (sem o contra-golpe a distancia) responde com o contra-golpe a quem usa pele_dura com frequencia (o
    # colosso, cujo preparo sob pele ela nao ve); pede muralha_lista_espelho
    muralha_contra_golpe_na_pele: bool = False


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
    # stats uniformes no total, estilo fixo em gambits ("<familia>:<nome>", ver campanha.gambit_npc).
    # Rebalanceado (experiments/calibrar_campanha.py, criterios K1-K4, configs/campanha/): a escada original
    # de docs/pve_treino.json (72 agressivo, 80 contragolpe, 90 adaptativo) tinha o chefe vencido pela
    # muralha sem treino e o tier 1 sem efeito de treino no adolescente.
    return {
        # todo pet treinado vence CADA NPC (decisao do Matheus, 2026-09-26: NPC fixo e imprevisivel; rodadas
        # 12-14 de experiments/calibrar_progressao.py). O epsilon alto destrava todas as linhas; o custo e o pet
        # sem treino vencer com frequencia. "lugar" = parada do mapa; vencer qualquer rival abre o proximo.
        "tier1_brutamontes": {"total_stats": 96, "estilo": "crianca:arisco", "estagio": "crianca", "epsilon": 0.5,
                              "lugar": 1, "estagio_minimo_sugerido": "crianca"},
        "tier2_sentinela": {"total_stats": 72, "estilo": "v2c:tartaruga", "epsilon": 0.4, "lugar": 2,
                            "estagio_minimo_sugerido": "adolescente"},
        "tier2_carcereiro": {"total_stats": 90, "estilo": "v21:espelho", "epsilon": 0.5, "lugar": 2,
                             "estagio_minimo_sugerido": "adolescente"},
        "tier2_porteiro": {"total_stats": 90, "estilo": "v2c:agressivo", "epsilon": 0.5, "lugar": 2,
                           "estagio_minimo_sugerido": "adolescente"},
        "tier3_soberano": {"total_stats": 110, "estilo": "v2c:agressivo", "epsilon": 0.5, "lugar": 3,
                           "estagio_minimo_sugerido": "adulto"},
    }


@dataclass(frozen=True)
class ConfigCampanha:
    """Campanha contra NPCs (TAREFA_TREINO_SOMBRIO, secao 5), com as regras V21C. PROPOSTOS."""

    npcs: dict = field(default_factory=_npcs)
    partidas_por_par: int = 100          # lados trocados na metade
    epsilon_npc: float = 0.05


CONFIG_CAMPANHA = ConfigCampanha()


@dataclass(frozen=True)
class ConfigArenaPesquisa:
    """Arena da pesquisa (TAREFA_ANALISE_PODER). Desligado por padrao: as runs antigas nao mudam."""

    # condicao fisica neutra (1,0) na arena normalizada: o G6b ficou como excecao (espelho com +5% de
    # condicao vence 0,725), entao a condicao do cuidado ainda decide lutas entre pets parecidos
    condicao_neutra: bool = False


CONFIG_ARENA_PESQUISA = ConfigArenaPesquisa()
CONFIG_CATALOGO = ConfigCatalogo()
CONFIG_COMBATE_V21 = ConfigCombateV21()
# combate corrigido aprovado com ressalvas (TAREFA_CORRECAO_COMBATE; experiments/configs/v21c/validacao.json):
# base V2C (C1-C4) + vida por vigor 2,5 + marca fragil. A campanha luta com estas regras.
CONFIG_COMBATE_V2C = ConfigCombateV2C(finta=True, dano_parry=5.0, fuga_condicionada=True, turno_morte_subita=25,
                                      mult_morte_subita=1.5)
CONFIG_COMBATE_V21C = ConfigCombateV21C(hp_por_vigor=2.5, hp_base=75.0, marca_fragil=True)
CONFIG_BATERIA_V21 = ConfigBateriaV21()


# =====================================================================
# Treino, sobrecarga e formas sombrias (docs/TAREFA_TREINO_SOMBRIO.md). Dados de
# docs/pve_treino.json e docs/arvore_evolucao.json > ramos_sombrios. Todos PROPOSTOS.
# =====================================================================


def _formas_sombrias() -> dict:
    # linha -> forma sombria (substitui as 2 formas adultas da linha); modificadores somam zero
    return {
        "brigao": {"nome": "devastador", "stats": {"forca": 4, "folego": 1, "recuperacao": -3, "guarda": -2}},
        "guardiao": {"nome": "bastiao_rachado", "stats": {"guarda": 4, "vigor": 1, "recuperacao": -3, "mira": -2}},
        "cacador": {"nome": "predador", "stats": {"mira": 4, "forca": 1, "vigor": -3, "guarda": -2}},
        "colosso": {"nome": "colosso_partido", "stats": {"vigor": 4, "guarda": 1, "folego": -3, "recuperacao": -2}},
    }


@dataclass(frozen=True)
class ConfigSombrio:
    formas: dict = field(default_factory=_formas_sombrias)
    limiar_aviso: int = 30               # sobrecarga na crianca -> adolescente: marca e fala fria
    limiar_sombrio: int = 60             # sobrecarga no adolescente -> adulto: forma sombria da linha
    epsilon_minimo: float = 0.2          # efeitos permanentes da forma sombria
    teto_vinculo: float = 0.6
    # passivas sombrias (resolucao em combate_v2/v21/regras.py)
    # redesenho para o S2 (experiments/calibrar_sombrias.py, configs/sombrias/ r0-r7): os gambits sombrios nao
    # leem o oponente (bots.SOMBRIOS); colosso partido regen x0,5 -> x0,85
    mult_devastador: float = 1.3         # corpo a corpo x1,3; defender e esquivar ilegais
    fracao_contra_golpe_bastiao: float = 1.0   # contra_golpe devolve 100%
    # "fadiga de guarda dobrada" nao existe no combate: defender nao rende guts extra (desvio registrado)
    mult_predador: float = 1.4           # disparo x1,4; recuar ilegal
    turnos_pele_colosso_partido: int = 3  # pele_dura dura 3 turnos
    mult_regen_colosso_partido: float = 0.85


def _exercicios() -> dict:
    return {"levantar_pedra": ("forca", "vigor"), "corrida": ("folego", "recuperacao"), "alvo": ("mira", "folego"),
            "esquiva": ("guarda", "vigor"), "meditar": ("recuperacao", "guarda"), "resistencia": ("vigor", "forca")}


def _aptidao_especie() -> dict:
    return {
        "brasa": {"forca": 1.2, "guarda": 1.1, "folego": 1.0, "vigor": 0.9, "mira": 0.9, "recuperacao": 0.9},
        "cirro": {"mira": 1.2, "recuperacao": 1.1, "folego": 1.0, "guarda": 0.9, "forca": 0.9, "vigor": 0.9},
        "ferrugem": {"guarda": 1.2, "vigor": 1.1, "forca": 1.0, "folego": 0.9, "recuperacao": 0.9, "mira": 0.9},
        "limo": {"recuperacao": 1.2, "folego": 1.1, "vigor": 1.0, "guarda": 0.9, "mira": 0.9, "forca": 0.9},
        "faisca": {"folego": 1.2, "forca": 1.1, "mira": 1.0, "recuperacao": 0.9, "vigor": 0.9, "guarda": 0.9},
        "seixo": {"vigor": 1.2, "forca": 1.1, "guarda": 1.0, "folego": 0.9, "recuperacao": 0.9, "mira": 0.9},
    }


@dataclass(frozen=True)
class ConfigTreino:
    exercicios: dict = field(default_factory=_exercicios)       # exercicio -> (principal, secundario)
    aptidao_especie: dict = field(default_factory=_aptidao_especie)
    ganho_principal: float = 2.0
    ganho_secundario: float = 1.0
    teto_por_stat: float = 10.0
    teto_por_estagio: dict = field(default_factory=lambda: {"crianca": 10.0, "adolescente": 12.0, "adulto": 14.0})
    teto_vida: float = 36.0
    # quanto cada ponto treinado vale em stat de combate (campanha e arena); 1 = o desenho original
    peso_ponto_combate: float = 3.0       # 1 -> 3 (experiments/calibrar_progressao.py): o treino tem de pesar como a evolucao
    # fadiga: ganho x (1 - fadiga/100); recupera acordado; zera ao dormir
    fadiga_por_sessao: float = 20.0
    recupera_fadiga_por_hora: float = 10.0
    limiar_pausa: float = 40.0            # pet pede descanso (desejo de necessidade)
    limite_forcar: float = 60.0           # a sessao vira forcar_treino
    intervalo_minimo_ticks: int = 10      # toque antes disso e rejeitado (nao consome orcamento)
    # forcar
    mult_forcar: float = 1.5
    sobrecarga_forcar: float = 25.0       # calibrado 15 -> 25 (experiments/calibrar_treino.py, ovos de calibracao)
    estresse_forcar: float = 10.0
    vinculo_forcar: float = -0.05
    # sobrecarga em [0, 100], nao zera na evolucao
    sobrecarga_max: float = 100.0
    decai_sobrecarga_hora_bem_cuidado: float = 2.0
    decai_sobrecarga_sono_completo: float = 10.0
    sono_completo_ticks: int = 360        # PROPOSTO: sono de 6 h ou mais conta como completo
    limiar_bem_cuidado: float = 0.3       # PROPOSTO: fome, higiene e energia acima disto = bem cuidado
    # vinculo e pedido de pausa: atender (a pausa acaba sem treino) = amostra 1; treinar por cima = 0
    peso_pausa_vinculo: float = 1.0
    # cronograma_interacoes.json: sessoes por dia (alvo e teto) por estagio; bebe nao treina
    sessoes_alvo_dia: dict = field(default_factory=lambda: {"crianca": 10, "adolescente": 8, "adulto": 5})
    teto_dia: dict = field(default_factory=lambda: {"crianca": 16, "adolescente": 12, "adulto": 8})
    # vidas com treino: orcamento = cuidado por dia + sessoes-alvo do estagio (decisao do Matheus, 2026-09-25)
    cuidado_por_dia: int = 16
    fracao_forcar_exigente: float = 0.5   # exigente forca em 50% das sessoes possiveis acima do limite


CONFIG_SOMBRIO = ConfigSombrio()
CONFIG_TREINO = ConfigTreino()


# =====================================================================
# Escala de stats (docs/TAREFA_PLANILHA_PROGRESSAO.md, Parte C; desenho aprovado em docs/JORNADA_JOGADOR.md).
# DESLIGADA por padrao: com `ligada=False` nada muda (as runs antigas reproduzem byte a byte).
# Perfil = pontos do catalogo (soma zero, o que a pesquisa compara); escala E = magnitude do lutador:
#   E = vida_por_estagio[estagio] x (1 + beta_treino x pontos treinados)
# No combate cada lutador luta nas proprias unidades (vida sem o multiplicador de estagio; guts como hoje) e o
# dano que A causa em B e multiplicado por E_A / E_B (fracao exata: multiplicar E dos dois lados pelo mesmo
# fator da a mesma luta bit a bit). Vida exibida = E x vida propria / vida neutra. Todos PROPOSTOS.
# =====================================================================


def _vida_por_estagio() -> dict:
    return {"bebe": 50, "crianca": 200, "adolescente": 600, "adulto": 1500}


def _fator_npc() -> dict:
    # E do NPC = vida_por_estagio[estagio_minimo_sugerido] x fator. Calibrado (experiments/calibrar_escala.py, sementes
    # de calibracao, experiments/configs/escala/calibracao.json): metas <= 0,30 sem treino e >= 0,80 com o treino tipico.
    # A Sentinela nao fecha com nenhum fator (0,8-3,0): fica o de menor violacao; excecao aceita pelo Matheus (2026-09-28).
    return {"tier1_brutamontes": 1.1, "tier2_sentinela": 1.6, "tier2_carcereiro": 1.5, "tier2_porteiro": 1.1,
            "tier3_soberano": 1.2}


@dataclass(frozen=True)
class ConfigEscala:
    ligada: bool = False
    vida_por_estagio: dict = field(default_factory=_vida_por_estagio)
    beta_treino: float = 0.03            # por ponto treinado (36 pontos -> x2,08)
    # NPCs da campanha na escala: perfil neutro (stat_neutro em todos), E pelo estagio sugerido x fator, epsilon proprio
    fator_npc: dict = field(default_factory=_fator_npc)
    epsilon_npc: float = 0.2
    # E4 na escala (redefinido pelo Matheus depois da Parte C, 2026-09-28): a evolucao sempre importa. O adulto sem
    # treino vence o adolescente da mesma linha, sem treino e com o treino maximo do estagio, em pelo menos taxa_min_e4;
    # esmagar e aceito de proposito (sem teto). Substitui o E4' e o E4'' da Parte B, que reprovaram.
    treino_e4: float = 22.0
    taxa_min_e4: float = 0.60


CONFIG_ESCALA = ConfigEscala()
CONFIG_ESCALA_LIGADA = ConfigEscala(ligada=True)


# ============================================================ educacao, lesoes e heranca (educacao-v1)
# docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, aprovado pelo Matheus em 2026-09-28. Status e fonte de cada valor:
# protocol.PARAMETROS_EDUCACAO_V1 (o teste confere que os valores la batem com estes).

def _intervalos_chamado() -> dict:
    return {"crianca": {"fome": 90, "higiene": 120, "carinho": 90},
            "adolescente": {"fome": 150, "higiene": 120, "carinho": 120},
            "adulto": {"fome": 180, "higiene": 120, "carinho": 180}}


@dataclass(frozen=True)
class ConfigEducacao:
    """Sistema A: travessuras que abrem janela e so o dono resolve; disciplina 0-100."""

    ligada: bool = False                     # como ConfigEscala: desligada, o MotorEducacao = MotorTreino
    janela_min: int = 15                     # cronograma_interacoes.json, janelas.chamado_min
    estagio_inicio_chamados: str = "crianca"
    # intervalo de cada chamado por estagio (cronograma_interacoes.json, intervalos_min); carinho -> humor
    intervalos_chamado_min: dict = field(default_factory=_intervalos_chamado)
    # chamado real: a necessidade pedida esta abaixo disto (igual a ConfigDonos.limiar_necessidade_pedido_adequado)
    limiar_necessidade_real: float = 0.35
    # slot de chamado sem necessidade real: chance de virar chamado FALSO com disciplina 0
    fracao_falso_base: float = 0.25
    reforco_por_petisco: float = 0.05        # cada petisco cedido a um chamado falso soma a fracao
    teto_falso: float = 0.5
    disciplina_max: int = 100
    passo_disciplina: int = 25               # bronca certa; 4 enchem
    acertos_para_aprender: int = 3           # acertos seguidos para o pet parar de repetir a travessura
    fator_disciplina_ao_evoluir: float = 0.5
    fracao_petisco_alimentar: float = 0.5    # petisco = esta fracao do ganho de alimentar, sem sujeira
    # parte 3: os slots deste tipo viram AVISO antes de sujar (o cronograma ancora higiene no coco dos v-pets)
    tipo_slot_aviso: str = "higiene"
    # o design dizia +passo_disciplina por aviso atendido; zerado na parte 3 porque o permissivo chegava a
    # disciplina 100 so pelo banheiro e o chamado falso sumia (decidido, delegado, em 2026-09-28)
    disciplina_por_banheiro: int = 0
    vinculo_bronca_sem_motivo: float = -0.05  # bronca num chamado real (igual a ConfigTreino.vinculo_forcar)
    custo_humor_acordar: float = 0.12         # acordar o pet dormindo (igual a Config.custo_repreender)
    limiar_superalimentacao: float = 0.9      # comer com fome (saciedade) acima disto faz mal
    custo_saude_superalimentacao: float = 0.05
    # Fase 3 (PLANO_ANALISE_V3): disciplina na luta = so o epsilon do Lutador (a resolucao do combate nao muda)
    epsilon_base_pet: float = 0.05            # = ConfigCombateV2.epsilon_bots
    delta_epsilon_indisciplina: float = 0.10  # epsilon = base + (1 - disciplina/max) * delta


@dataclass(frozen=True)
class ConfigLesoes:
    """Sistema C: vitorias, lesoes e evolucao (camada Color). Nao toca a resolucao do combate."""

    ligada: bool = False                     # como ConfigEducacao: desligada, luta no log levanta erro
    lutas_minimas_taxa: int = 10             # igual a ConfigEvolucaoPesquisa.sparring_minimo_adulto
    limiar_taxa_vitoria: float = 0.8
    prob_lesao_derrota: float = 0.2
    lesoes_para_morte: int = 20
    horas_sem_tratar_morte: int = 6
    # o que a qualificacao por vitorias (>= limiar em >= lutas_minimas no adolescente) faz: "condicao_adulto" =
    # sem ela o pet continua adolescente (como o sparring minimo). Decidido (delegado) em 2026-09-28; o catalogo
    # nao tem "forma de vitoria"
    efeito_qualificacao: str = "condicao_adulto"
    # V3b (adendo do PLANO_ANALISE_V3): cada luta fora da arena de pesquisa conta como uma sessao de treino.
    # DESLIGADO depois da V3b (decisao do Matheus, opcao B, 2026-09-28): levava 90% dos pets a forma sombria
    luta_treina: bool = False
    # estilo "lutar" (decisao do Matheus, 2026-09-29): experiencia de combate. Cada vitoria fora da arena de
    # pesquisa (a vida inteira, nao zera ao evoluir) reduz o epsilon do lutador; teto na reducao, piso 0
    experiencia_por_vitoria: float = 0.002
    experiencia_max: float = 0.05


@dataclass(frozen=True)
class ConfigConfianca:
    """MVP M1 (docs/DESIGN_MVP_M1_CONFIANCA.md, 2026-09-29): confianca de combate e desgaste por rival repetido.
    Estado derivado dos eventos de luta que ja existem (nenhum evento novo; o replay recalcula). Tudo PROPOSTO, sem
    fonte (protocol.PARAMETROS_CONFIANCA_M1). Desligada: nada muda em nenhuma run nem no resumo."""

    ligada: bool = False                     # como ConfigEducacao/ConfigLesoes: desligada, o motor nem calcula
    # 2.1 novidade por rival: m[rival] <- m * exp(-dt/tau_hab) + 1 depois da luta; novidade = exp(-lambda * m antes)
    lambda_novidade: float = 0.7             # quao rapido a repeticao satura (3a luta seguida ~0,25; 5a ~0,06)
    tau_habituacao_min: int = 2880           # 48 h de jogo: quando a novidade volta
    # 2.2 confianca c em [-1, 1]: decai para 0 entre as lutas; empurrada por eta_s * novidade * sinal
    eta_confianca: float = 0.25              # quanto uma luta nova mexe na confianca
    k_sensibilidade: float = 0.5             # na derrota, eta * (1 - k * sensibilidade): como a repreensao no temperamento
    tau_confianca_min: int = 1440            # 24 h de jogo: quanto dura a confianca
    # 2.3 so o epsilon do lutador do pet muda: epsilon += kappa * max(0, -c) (a confianca positiva nao reduz)
    kappa_eps: float = 0.10                  # mesma ordem de delta_epsilon_indisciplina
    # 2.5 frases de estado: limiar de confiante/inseguro, histerese (tempo minimo na faixa nova antes de trocar)
    limiar_frase: float = 0.4
    histerese_frase_min: int = 120
    limiar_tedio: float = 0.3                # novidade das ultimas n_tedio lutas <= limiar -> "entediado do rival"
    n_tedio: int = 3


@dataclass(frozen=True)
class ConfigHeranca:
    """Sistema B: herda temperamento (media + ruido) e especie (sorteada entre as dos pais)."""

    sigma_temperamento: float = 0.1
    estagio_minimo_pais: str = "adulto"


@dataclass(frozen=True)
class ConfigEquilibrio:
    """Gate de equilibrio dos estilos de jogo (cuidar, treinar, lutar) contra o painel."""

    taxa_min: float = 0.40
    taxa_max: float = 0.60
    margem_max: float = 0.15


@dataclass(frozen=True)
class ConfigDuracoes:
    """Sistema D: duracao (min) de bebe, crianca e adolescente. `teste` = ConfigEvolucaoPesquisa de hoje;
    `canonica` = v-pets citados no cronograma (Ver.20th/Color: 6 h, 24 h, 36 h)."""

    teste: tuple = (180, 720, 1080)
    canonica: tuple = (360, 1440, 2160)

    def cfg_evo(self, nome: str) -> "ConfigEvolucaoPesquisa":
        if nome not in ("teste", "canonica"):
            raise KeyError(f"duracao desconhecida: {nome!r}")
        b, c, a = getattr(self, nome)
        return replace(CONFIG_EVOLUCAO_PESQUISA, dur_bebe_min=b, dur_crianca_min=c, dur_adolescente_min=a)


CONFIG_DURACOES = ConfigDuracoes()


@dataclass(frozen=True)
class ConfigSparring:
    """Fase 3 (PLANO_ANALISE_V3): sparring de verdade na vida de pesquisa, no adolescente, horarios iguais para
    todos os bracos; rival = adolescente da mesma linha e especie, carater neutro, sem treino."""

    lutas: int = 10                          # = ConfigLesoes.lutas_minimas_taxa
    lutas_braco_lutador: int = 20
    intervalo_min: int = 30
    primeira_apos_inicio_min: int = 30


@dataclass(frozen=True)
class ConfigMentira:
    """Digimons que mentem (docs/DESIGN_VOZ_PROPRIA.md, secao 9). A mentira e decidida pelo MOTOR (rng_mentira,
    derivada da semente) e registrada; a LLM so escreve a frase. Toda fala espontanea abre uma janela de fala,
    como o chamado falso da travessura; o dono ve a fala, nunca se e mentira. Status e fonte de cada valor:
    protocol.PARAMETROS_MENTIRA_V1 (registro a parte: o hash da educacao-v1 nao muda).

        h = fator_sombria (se a forma for sombria, senao 1) x (1 - peso_sobrecarga x sobrecarga/100) x especie
        p = 0 se h = 1 ou depois de `acertos_para_aprender` broncas certas seguidas em mentiras no estagio
        p = min(teto_chance, coef_chance x (1 - h) x (1 - disciplina/max) + reforco_por_impune x impunes)
    """

    ligada: bool = False                     # desligada: nenhuma fala, nenhum sorteio (V3 e confirmatoria intactas)
    fator_sombria: float = 0.4
    peso_sobrecarga: float = 0.5             # sobrecarga 0-100 do treino forcado (TAREFA_TREINO_SOMBRIO)
    coef_chance: float = 0.5
    reforco_por_impune: float = 0.05
    teto_chance: float = 0.8
    acertos_para_aprender: int = 3           # igual a ConfigEducacao.acertos_para_aprender
    impunes_premiada: int = 2                # petisco ou elogio numa mentira: conta como 2 impunes
    janela_fala_min: int = 30
    # pesquisa: uma fala espontanea (slot) a cada tantos minutos, da crianca em diante (bebe so emote). No jogo o
    # gatilho vem de fora (reencontro, marco...) pelo evento `fala`; o ritmo maximo do design e 1 a cada 2 h
    intervalo_fala_min: int = 120
    # o primeiro slot de fala vem esta defasagem depois do inicio do estagio: sem ela a fala cairia sempre no
    # mesmo tick do aviso de higiene (a cada 120 min), que abre a janela antes e a fala nunca aconteceria
    defasagem_fala_min: int = 60
    estagios_fala: tuple = ("crianca", "adolescente", "adulto")
    # a fala mentirosa distorce um fato de estado (o dono atento ve que contradiz as barras) ou um da historia
    # (habito, marco, gosto: o dono nao tem como conferir pelas barras). Fracao das falas sobre estado:
    fracao_tema_estado: float = 0.5
    honestidade_enganador: float = 0.7       # especie com traco VERIFICADO de enganador (corpus_especies.json)


@dataclass(frozen=True)
class ConfigHistoria:
    """Extrator da historia do pet (digilab/historia.py; DESIGN_VOZ_PROPRIA, secao 2). Limiares dos fatos H
    (habito meu), O (habito do dono), P (gosto) e L (marco). Todos PROPOSTOS (protocol.PARAMETROS_HISTORIA_V1)."""

    # H, sequencia A -> B: P(B em ate janela_seq_min depois de A) >= prob_seq_min, A com >= min_ocorrencias_seq,
    # lift >= lift_min sobre a taxa de B numa janela qualquer
    janela_seq_min: int = 30
    prob_seq_min: float = 0.6
    min_ocorrencias_seq: int = 10
    lift_min: float = 1.5
    # H, periodo do dia: taxa da acao no periodo >= fator_periodo x a media do dia, >= min_ocorrencias_periodo
    fator_periodo: float = 2.0
    min_ocorrencias_periodo: int = 10
    # O
    fracao_periodo_dono: float = 0.4         # periodo com >= esta fracao das acoes do dono
    dias_periodo_dono: int = 3               # ... em >= tantos dias diferentes
    fracao_cuidado_dono: float = 0.35        # acao de cuidado com >= esta fracao das acoes do dono
    fracao_cede_manha: float = 0.6           # petisco / (petisco + bronca) nas manhas
    min_manhas: int = 5
    demora_rapida_min: int = 5               # mediana da demora nos chamados <= isto: "atende rapido"
    demora_lenta_min: int = 12               # >= isto: "demora"
    min_chamados_demora: int = 5
    # P
    limiar_gosto: float = 0.02               # |desvio da politica sobre o bandit recem-nascido| na sonda do carater
    fracao_treino_favorito: float = 0.35
    min_sessoes_treino: int = 6
    # L
    ausencia_min: int = 360                  # >= 6 h de jogo sem o dono agir
    # selecao para uma fala
    max_fatos: int = 12
    max_por_regra: int = 2                   # no maximo tantos fatos da mesma regra (ex.: ausencias)
    falas_recentes: int = 5                  # fato citado nas ultimas tantas falas vai para o fim


CONFIG_SPARRING = ConfigSparring()
CONFIG_HISTORIA = ConfigHistoria()
CONFIG_MENTIRA = ConfigMentira()
CONFIG_MENTIRA_LIGADA = ConfigMentira(ligada=True)
CONFIG_EDUCACAO = ConfigEducacao()
CONFIG_EDUCACAO_LIGADA = ConfigEducacao(ligada=True)
CONFIG_LESOES = ConfigLesoes()
CONFIG_LESOES_LIGADA = ConfigLesoes(ligada=True)
CONFIG_CONFIANCA = ConfigConfianca()
CONFIG_CONFIANCA_LIGADA = ConfigConfianca(ligada=True)
CONFIG_HERANCA = ConfigHeranca()
CONFIG_EQUILIBRIO = ConfigEquilibrio()


# O teto de pesos por plano (docs/DECISAO_V2_TETO_PESOS.md, TP-1 e TP-2, decididas pelo Matheus em 2026-10-12 pela recomendacao): o
# padrao do cerebro A fica 1000 (ConfigLobos.maximo_pesos); um plano que precise de mais declara o seu teto na config da bancada, ate
# este limite. Passar dele pede decisao nova. DECIDIDO (TP-2), SEM FONTE: cabe o maior cerebro contado em 2026-10-12 (1277) com folga
LIMITE_TETO_PESOS_PLANO = 2000

# =====================================================================
# V2, L0 (docs/TAREFA_V2_L0_LOBOS.md, 2026-10-01): politica com lobos nomeados, aprendizado desligado.
# Nao entra em nenhum hash de protocolo da v1. Todo campo e PROPOSTO, sem fonte e nao referendado; o status de
# cada um esta em digilab/policies/lobos.py (PARAMETROS_LOBOS_L0, conferido por teste).
# =====================================================================


@dataclass(frozen=True)
class ConfigLobos:
    """Politica com lobos nomeados (percepcao, memoria e emocao, impulsos, decisao). L0: so o esqueleto.

    aprendizado_ligado          PROPOSTO  False no L0: os pesos nunca mudam. True e o L1, que ainda nao existe
                                          (a politica falha alto na construcao).
    bits_ponto_fixo             PROPOSTO  escala dos pesos S = 2**bits. Potencia de dois de proposito: dividir um
                                          inteiro por S e exato em ponto flutuante, e e isso que da ao prior os
                                          MESMOS floats que o instinto escreve (igualdade byte a byte, gate G2).
    escala_ticks_desde_cuidado  PROPOSTO  entrada da percepcao: min(1, ticks sem cuidado / escala); o mesmo valor
                                          da ConfigBandit. Coeficiente zero no prior.
    maximo_pesos                PROPOSTO  teto do plano da V2 (fase 1b: "abaixo de mil pesos, para o replay"). O padrao fica 1000; um
                                          plano declara o seu ate LIMITE_TETO_PESOS_PLANO (TP-1, TP-2). Acima, falha alto.
    """

    aprendizado_ligado: bool = False
    bits_ponto_fixo: int = 10
    escala_ticks_desde_cuidado: float = 480.0
    maximo_pesos: int = 1000
    # --- L1 (docs/TAREFA_V2_L1_DECISAO.md, docs/PLANO_ANALISE_V2_L1.md): so valem com aprendizado_ligado ---
    # Atualizacao do lobo de decisao, em inteiros: dw = arred(f*S * passo * X_j * (S*1[a=a*] - P_a) / (S*S*W_a)).
    # passo e teto sao PROPOSTOS e CALIBRADOS nas sementes 3101...3505 (grade do plano, secao 5); os outros sao
    # PROPOSTOS, copiados da ConfigBandit (mesma janela de credito da v1) e nao calibrados.
    passo: int = 512                         # PROPOSTO, calibrado em 3101...3505: S/2 (grade {32, 64, 128, 256, 512}; a calibracao
                                             # nao fechou: nenhum ponto passou G6; escolhido pela regra da secao 5 do plano)
    teto: int = 1024                         # PROPOSTO, calibrado: |w - w0| <= teto = 1*S (grade {1024, 2048, 4096})
    piso_peso: int = 64                      # PROPOSTO: S/16; peso efetivo minimo dos candidatos com o aprendizado ligado
    janela_latencia_ticks: int = 120         # PROPOSTO: = ConfigBandit.janela_latencia_ticks (chamado atendido paga 1 - L/janela)
    recompensa_pedido_ignorado: float = -0.5  # PROPOSTO: = ConfigBandit.recompensa_pedido_ignorado
    recompensa_elogio: float = 1.0           # PROPOSTO: = ConfigBandit.recompensa_elogio
    recompensa_repreensao: float = -1.0      # PROPOSTO: = ConfigBandit.recompensa_repreensao
    # --- N5 (docs/TAREFA_V2_N5_CEREBRO.md, docs/PLANO_ANALISE_V2_N5.md, decisoes N5-1 a N5-3) ---
    # Confianca de partida no que o dono informa: o peso inteiro, compartilhado entre as frutas, da entrada `info` (+1 bem, -1 mal,
    # 0 nada) na sub-decisao da fruta. 0 = entrada desligada (sem termo e sem aprendizado: a vida de hoje, byte a byte). A grade
    # {S/4, S/2, 3S/4} e calibrada no N5 (sementes 12101...12505), abaixo do teto, para o peso poder cruzar o zero.
    w0_info: int = 0                         # PROPOSTO: N5-1
    # --- REVISAO-APRENDIZ (docs/TAREFA_V2_REVISAO_APRENDIZ.md, docs/PLANO_ANALISE_V2_REVISAO_APRENDIZ.md): a janela de credito ---
    # Traco de elegibilidade curto, em inteiros: o sinal f_S creditado a uma decisao (consequencia, elogio ou bronca) tambem chega as
    # `traco_decisoes` decisoes anteriores, a k-esima com div_arred(f_S * traco_fator**k, S**k) (traco_fator na escala S, < S). O
    # credito do chamado (latencia, ignorado) fica preso ao chamado. 0 = sem traco: o credito de hoje, byte a byte.
    traco_decisoes: int = 0                  # PROPOSTO: alavanca da revisao (grade no plano)
    traco_fator: int = 0                     # PROPOSTO: lambda x S do traco (so com traco_decisoes > 0)
    # --- N6, memoria de episodios (docs/PLANO_ANALISE_V2_N6.md, N6-1 a N6-10; docs/TAREFA_V2_CEREBRO_N6_N7.md) ---
    # Episodios de consumo de fruta (a fruta e a valencia do humor) nos espacos da v1 (ConfigMemoriaEspacos: 4 + 2, 12 h), sem
    # decaimento e sem relembrar (N6-4). Entram so na escolha de qual fruta (N6-1): m_f = div_arred(ganho x valencia_f, S), com
    # ganho < S. Desligada (o padrao): nada existe (a vida e o estado interno de hoje). Ligada com ganho 0: o M0 do plano (registra
    # e codifica, contribuicao zero).
    memoria_ligada: bool = False             # PROPOSTO: N6, chave
    memoria_ganho: int = 0                   # PROPOSTO: N6-10, grade {S/4, S/2, 3S/4} calibrada no N6 (19101...19505)
    memoria_modo: str = "relevante"          # PROPOSTO: "relevante" (MR), "recencia" (MT) ou "embaralhada" (ME), secao 4.1
    memoria_janela_recencia_ticks: int = 240  # PROPOSTO: N6-5, a janela do braco "recencia"
    memoria_permutacao: tuple = ()           # o desarranjo pi de FRUTAS do braco "embaralhada" (lobos.desarranjo_n6(semente), N6-6)
    # --- N7, arbitragem (docs/PLANO_ANALISE_V2_N7.md, N7-1 a N7-10) ---
    # Confianca de partida no pedido do dono ("deixe a fruta X"): o peso inteiro, compartilhado, da entrada `pedido` na decisao de comer
    # (fome_moderada, fruta_no_cenario) e na escolha da fruta. 0 = entrada desligada (a vida de hoje, byte a byte).
    w0_pedido: int = 0                       # PROPOSTO: N7-4, grade {S/4, S/2, 3S/4} calibrada no N7 (21101...21505)
    # --- corpo, etapa 6 (docs/TAREFA_V2_CORPO_DRIVES.md, secao 8; CD-9, CD-10) ---
    # O sinal direto do tapa, creditado a ultima decisao pela janela da v1, como a bronca, em toda fonte que aprende
    recompensa_tapa: float = -1.0            # PROPOSTO: o valor da recompensa_repreensao (CD-10)
    # --- dois pets, etapa 4 (docs/TAREFA_V2_DOIS_PETS.md; docs/futuro/dois_pets.md, secao 8, DP-8) ---
    # O alvo aprendido no mundo fisico: o cerebro escolhe a CLASSE do candidato (comida, cheiro, vagar, casa, continuar, bola, e
    # seguir e onde_comeu quando o motor os tiver). O peso efetivo de uma classe e 1 se ela e a do padrao do motor, mais w / S; o w de
    # toda classe comeca em w0_alvo (o peso pequeno das outras). Desligado: o padrao do motor (a vida de hoje, byte a byte)
    alvo_aprendido: bool = False             # PROPOSTO: a chave
    w0_alvo: int = 64                        # PROPOSTO, SEM FONTE: S/16, o peso pequeno de partida de cada classe
    # --- dois pets, etapa 4, segunda metade (DP-8): as entradas sociais e o modelo dos outros ---
    # As entradas sociais (outro a vista, viu o outro comer, a acao visivel do outro e o tipo do ultimo toque, lidas de Observacao.social)
    # nas regras de tempo livre, um peso por (regra, acao, entrada), prior 0: no prior, a vida de hoje. O modelo dos outros
    # (familiaridade, confianca na comida, afinidade) e so registrado: nunca entra na decisao (degrau 3). Os dois so no mundo fisico
    entradas_sociais: bool = False           # PROPOSTO: a chave das entradas sociais
    modelo_outros: bool = False              # PROPOSTO: a chave do modelo dos outros (so registrado)
    janela_social_ticks: int = 240           # PROPOSTO, SEM FONTE propria: o "recente" do viu comer e do toque (a janela da informacao)
    fator_familiaridade: int = 16            # PROPOSTO, SEM FONTE: S/64 por decisao, a media movel do tempo a vista (~16 h)
    # --- a rota do canal do humor no mundo fisico (CANAIS-REFORCO; decisao do Matheus, 2026-10-11) ---
    # A decisao de comer le a fruta madura a vista (um peso por fruta, prior 0, a FRUTA-NO-CENARIO parte B no mundo fisico), em toda
    # regra em que comer e candidato. Sao os pesos que leem a identidade da fruta: com os canais, o canal do humor (a E2) vai a eles.
    # Desligada: a vida de hoje (e, com os canais, comer a fruta que mexe no humor falha alto, como antes)
    presenca_fruta_mundo: bool = False       # PROPOSTO: a chave
    # --- o pet que pensa, etapa 2b (docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.4; PP-2) ---
    # As classes de alvo por arvore no alvo aprendido: `arvore:<id>` (as 9 do layout), nas regras em que o explorar e candidato, com os
    # candidatos de arvore lembrada do motor (PP-1, ConfigPetQuePensaMundo). Exige o alvo aprendido. Desligada: a vida de hoje
    alvo_por_arvore: bool = False            # PROPOSTO: a chave
    # --- o pet que pensa, etapa 2 (docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.2; PQ-3, PQ-6, PP-6) ---
    # O lobo `planejamento`: o valor previsto V(k) de cada alvo pelos modelos do mundo (modelo_mundo.ModeloMundo, que o cerebro guarda)
    # vira o termo div_arred(g_plano x V, S), cortado em +-teto_plano, no peso efetivo do alvo e da decisao de comer ou explorar. Com
    # g_plano 0, nada existe (o cerebro de hoje). O planejador nao tem pesos (PQ-6): o n_pesos do A nao muda
    g_plano: int = 0                         # PROPOSTO: o ganho do plano; a calibracao (PP-6) escolhe na grade {S/4, S/2, S}
    teto_plano: int = 2048                   # PROPOSTO, SEM FONTE (PP-6): 2 S, o maior termo do plano, para cima ou para baixo
    # O Paladar (docs/futuro/paladar.md, secao 3.4; PL-1, PL-5 e PL-6 pela recomendacao): o canal `gosto` no sinal (a leitura dos
    # receptores do paladar depois de comer, pesada pelos h_q do genoma do pet, nao homeostatico, sem ler a fome) e as classes do alvo
    # de comer por tipo (`comida:racao`, `comida:a`, `comida:b`, `comida:c` no lugar de `comida`, prior w0_alvo: o querer aprendido, sem
    # atracao inata). Exige o mundo fisico, o corpo com o paladar, o alvo aprendido e os h_q do pet. Desligada, nada existe
    paladar: bool = False                    # PROPOSTO: a chave (o desenho, PL-1 a PL-9, decidido)

    def __post_init__(self) -> None:
        if type(self.maximo_pesos) is not int or not 1 <= self.maximo_pesos <= LIMITE_TETO_PESOS_PLANO:
            raise ValueError(f"maximo_pesos {self.maximo_pesos!r}: inteiro de 1 a {LIMITE_TETO_PESOS_PLANO} (o limite do teto por plano, "
                             f"TP-2; acima pede decisao nova)")

    @property
    def escala(self) -> int:
        """S = 2**bits: a unidade 1.0 dos pesos em ponto fixo."""
        return 1 << self.bits_ponto_fixo


CONFIG_LOBOS = ConfigLobos()
CONFIG_LOBOS_APRENDIZ = ConfigLobos(aprendizado_ligado=True)      # L1: o aprendiz da V2 com o lobo de decisao aprendendo


@dataclass(frozen=True)
class ConfigCerebroC:
    """V2, CEREBRO-C (docs/TAREFA_V2_CEREBRO_C.md; contrato da secao 1 de docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md): o DigiBrain C,
    Fly-like (policies/cerebro_c.py). Registro de status e fonte em cerebro_c.PARAMETROS_CEREBRO_C; tudo PROPOSTO, fora de todo hash.

    Os campos do credito do dono (janela, recompensas) e o ponto fixo sao os mesmos do A (ConfigLobos): a fonte do sinal e comum. Os
    cortes das faixas sao a ESTRUTURA dos circuitos (quantos Kenyon cells existem), nao parametros livres: os de necessidade sao os
    limiares do proprio instinto (0,25 = necessidade urgente; 0,5 = o pedido do dono). Os livres do adendo de calibracao sao passo,
    teto e w0_info (PR do CEREBRO-C)."""

    aprendizado_ligado: bool = False
    bits_ponto_fixo: int = 10                # S = 2**bits, como o A
    escala_ticks_desde_cuidado: float = 480.0   # o mesmo do A (a percepcao do prior e a faixa social)
    maximo_pesos: int = 1000                 # o teto do plano da V2, como o A
    passo: int = 64                          # PROPOSTO, livre (adendo): S/16; o quanto uma sinapse muda por sinal de 1*S
    teto: int = 4096                         # PROPOSTO, livre (adendo): 4*S; o maximo de cada compartimento (0 <= w <= teto)
    piso_peso: int = 64                      # o mesmo do A: S/16, peso efetivo minimo dos candidatos com o aprendizado ligado
    janela_latencia_ticks: int = 120         # o mesmo do A (janela de credito da v1)
    recompensa_pedido_ignorado: float = -0.5   # o mesmo do A
    recompensa_elogio: float = 1.0           # o mesmo do A
    recompensa_repreensao: float = -1.0      # o mesmo do A
    w0_info: int = 0                         # PROPOSTO, livre (adendo): resposta inata ao que o dono informa na escolha da fruta; 0 = so a aprendida
    cortes_necessidade: tuple = (0.25, 0.5)  # faixas de fome, higiene, energia e humor (os limiares do instinto)
    cortes_binarios: tuple = (0.5,)          # faixas de saude e sujeira
    cortes_hora: tuple = (0.25, 0.5, 0.75)   # quatro faixas do dia (madrugada, manha, tarde, noite)
    cortes_sem_cuidado: tuple = (0.25, 0.5)  # faixas de min(1, ticks sem cuidado / escala) (o circuito social)

    @property
    def escala(self) -> int:
        """S = 2**bits: a unidade 1.0 dos pesos em ponto fixo."""
        return 1 << self.bits_ponto_fixo


CONFIG_CEREBRO_C = ConfigCerebroC()
CONFIG_CEREBRO_C_APRENDIZ = ConfigCerebroC(aprendizado_ligado=True)


@dataclass(frozen=True)
class ConfigCerebroB:
    """V2, CEREBRO-B (docs/TAREFA_V2_CEREBRO_B.md; contrato da secao 1 de docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md): o DigiBrain B,
    CfC + ator-critico + elegibilidade (policies/cerebro_b.py), em ponto flutuante. Registro de status e fonte em
    cerebro_b.PARAMETROS_CEREBRO_B; tudo PROPOSTO, fora de todo hash.

    O ponto fixo (so para o prior herdado, o mesmo do A), a percepcao e o credito do dono (janela, recompensas) sao os do A: o herdado e a
    fonte do sinal sao comuns (C-1). n_ocultos, delta_t, semente_pesos, escala_inicial e limite_logit sao a ESTRUTURA da rede (o tamanho
    que da a capacidade do contrato 1.3 e a inicializacao fixa, herdada). Os livres do adendo de calibracao sao taxa_ator, taxa_critico,
    lambda_elegibilidade e w0_info (PR do CEREBRO-B)."""

    aprendizado_ligado: bool = False
    bits_ponto_fixo: int = 10                # S = 2**bits, como o A (o prior do instinto e o sinal da consequencia em inteiros)
    escala_ticks_desde_cuidado: float = 480.0   # o mesmo do A (a percepcao)
    maximo_pesos: int = 1000                 # o teto do plano da V2, como o A
    n_ocultos: int = 9                       # estrutura: neuronios da celula CfC (a capacidade do contrato 1.3, 759 parametros)
    delta_t: float = 1.0                     # estrutura: o tempo da celula entre duas decisoes (as decisoes sao a cada 15 ticks)
    semente_pesos: int = 1                   # estrutura: a rng PROPRIA da inicializacao da celula (herdada, igual em todo pet)
    escala_inicial: float = 1.0              # estrutura: pesos da celula iniciados em U(-r, r), r = escala_inicial / sqrt(entradas + ocultos)
    limite_logit: float = 20.0               # estrutura: os logits aprendidos ficam em [-limite, +limite] (exp sem estouro)
    taxa_ator: float = 0.05                  # PROPOSTO, livre (adendo): o passo do ator (celula, cabeca das acoes, cabeca da fruta)
    taxa_critico: float = 0.05               # PROPOSTO, livre (adendo): o passo do critico
    lambda_elegibilidade: float = 0.8        # PROPOSTO, livre (adendo): o decaimento do traco de elegibilidade por decisao
    w0_info: float = 0.0                     # PROPOSTO, livre (adendo): logit inato do que o dono informa na escolha da fruta (0 = so o aprendido)
    janela_latencia_ticks: int = 120         # o mesmo do A (janela de credito da v1)
    recompensa_pedido_ignorado: float = -0.5   # o mesmo do A
    recompensa_elogio: float = 1.0           # o mesmo do A
    recompensa_repreensao: float = -1.0      # o mesmo do A

    @property
    def escala(self) -> int:
        """S = 2**bits: a unidade 1.0 do prior em ponto fixo e do sinal da consequencia."""
        return 1 << self.bits_ponto_fixo


CONFIG_CEREBRO_B = ConfigCerebroB()
CONFIG_CEREBRO_B_APRENDIZ = ConfigCerebroB(aprendizado_ligado=True)


@dataclass(frozen=True)
class ConfigConsequencia:
    """V2, N3 (docs/PLANO_ANALISE_V2_N3.md, secao 3): o sinal do braco P1, a reducao do deficit homeostatico pela propria
    acao (Keramati e Gutkin, 10.7554/elife.04811). Em inteiros na escala S do aprendiz:
        D(h) = soma_i (S - arred(h_i * S))**2  sobre os drives;  f_S = div_arred(ganho * (D(antes) - D(depois)), S)
    Janela de credito IMEDIATA: antes/depois = observacao -> observacao_seguinte da mesma decisao (engine._avancar mede a
    transicao logo depois do efeito da acao do pet, antes do tempo e do dono). Todos os campos PROPOSTOS (registro em
    lobos.PARAMETROS_CONSEQUENCIA_N3); fora de qualquer hash de protocolo.

    drives  PROPOSTO  indices em Estado.vetor: fome (0), higiene (1), energia (2), ponto de ajuste 1.0. Humor fora (canal da
                      bola e do efeito ruim das frutas, F6); saude fora (nao muda pela acao em si).
    ganho   PROPOSTO  escala do sinal (inteiro); o unico parametro calibrado do N3 (grade {4, 8, 16, 32, 64}, sementes
                      8101...8505).
    humor_na_fruta  DECIDIDO  E2 (Matheus, 2026-10-04; PLANO_ANALISE_V2_EXPERIMENTO_MAIOR, secao 3.1): quando a acao foi
                      comer uma fruta, o humor entra nos drives e o "depois" e o estado logo depois de comer
                      (lobos.sinal_homeostatico_fruta, docs/TAREFA_V2_LOBOS_MUNDO.md). Nas outras acoes, e sem frutas,
                      nada muda: o sinal do N3 de sempre.
    canais_ligados  PROPOSTO  CANAIS-REFORCO (docs/TAREFA_V2_CANAIS_REFORCO.md; H-R2; K-6): o mesmo sinal separado por canal (fome,
                      higiene, energia e humor), cada canal creditado ao seu grupo de pesos (lobos.ROTA_CANAIS). A soma dos canais
                      e o escalar, em inteiros, decisao a decisao. False: o escalar de sempre, byte a byte.
    pesos_janela  PROPOSTO  corpo, adendo 2, A2.4 (docs/PLANO_ANALISE_V2_CORPO_DRIVES.md; o braco P1-cw): o peso de cada drive no sinal
                      depende da falta media dele nas ultimas `janela_pesos` decisoes, m_d, na escala S:
                          w_d = max(div_arred(S, 4), S - div_arred(3 * m_d, 4))
                      (saciado na janela: S, o peso de hoje; em falta total: S/4). O peso fica fixo dentro da decisao (o mesmo no antes
                      e no depois) e a janela anda depois dela. False: o sinal de sempre, byte a byte (lobos.sinal_homeostatico).
    janela_pesos  PROPOSTO  A2.4: J, o tamanho da janela em decisoes (32: 8 h a uma decisao a cada 15 min).
    pesos_drives_corpo  PROPOSTO  corpo, etapa 5 (docs/TAREFA_V2_CORPO_DRIVES.md, secao 9): os pesos inteiros w_d do sinal pelo corpo,
                      D = soma_d w_d * falta_d**2 sobre os receptores (lobos.sinal_corpo), um por drive do sinal, pelo nome do
                      receptor. Todos 1 (o sinal de hoje); o plano do corpo pode calibra-los. So valem com a chave do corpo no cerebro.
    """

    drives: tuple = (0, 1, 2)
    ganho: int = 4                     # calibrado em 8101...8505 (a calibracao NAO fechou: nenhum ganho passou G6; regra de
                                       # reserva da secao 6: menos vidas com peso no teto); artifacts_v2_n3/calibracao/escolha.json
    humor_na_fruta: bool = True        # E2: o humor no sinal do P1 so quando a mudanca vem de comer fruta
    canais_ligados: bool = False       # CANAIS-REFORCO: o mesmo total de sinal, separado por canal (H-R2, K-6)
    pesos_janela: bool = False         # corpo, A2.4 (P1-cw): o peso de cada drive pela falta recente dele
    janela_pesos: int = 32             # A2.4: J decisoes
    # corpo, etapa 5: w_d do sinal pelo corpo, por receptor (os de hoje e os drives novos da secao 9; o susto fica fora do sinal)
    pesos_drives_corpo: tuple = (("fome", 1), ("higiene", 1), ("energia", 1), ("humor", 1), ("tedio", 1), ("curiosidade", 1),
                                 ("solidao", 1), ("estresse", 1), ("dor", 1), ("vontade", 1), ("conforto", 1))
    # o Paladar (docs/futuro/paladar.md, secao 3.4): f_gosto = div_arred(ganho_gosto x soma_q div_arred(h_q x leitura de paladar_q
    # depois, S), S), so nas decisoes em que o pet comeu comida madura e so com ConfigLobos.paladar. O unico numero do paladar que o
    # plano do J5 calibra (PL-8, PJ-3); S = 1 vez a soma
    ganho_gosto: int = 1024

    def __post_init__(self) -> None:
        if type(self.janela_pesos) is not int or self.janela_pesos <= 0:
            raise ValueError(f"ConfigConsequencia.janela_pesos precisa ser inteiro positivo: {self.janela_pesos!r}")
        nomes = [par[0] for par in self.pesos_drives_corpo]
        if len(set(nomes)) != len(nomes):
            raise ValueError(f"ConfigConsequencia.pesos_drives_corpo com drive repetido: {nomes}")
        for nome, w in self.pesos_drives_corpo:
            if type(nome) is not str or type(w) is not int or w < 0:
                raise ValueError(f"ConfigConsequencia.pesos_drives_corpo: (nome, inteiro >= 0), veio {(nome, w)!r}")
        if type(self.ganho_gosto) is not int or self.ganho_gosto < 0:
            raise ValueError(f"ConfigConsequencia.ganho_gosto precisa ser inteiro >= 0: {self.ganho_gosto!r}")


CONFIG_CONSEQUENCIA = ConfigConsequencia()


@dataclass(frozen=True)
class ConfigBola:
    """V2, A1 (docs/V2_A1_BOLA_DESENHO.md, opcao A; plano docs/PLANO_ANALISE_V2_A1.md): a bola, primeiro objeto do mundo com
    consequencia. O dono poe (`por_bola`) e tira (`tirar_bola`); o pet a percebe como a entrada `bola` da Observacao; `brincar`
    com bola no cenario e brincar COM a bola (humor + ganho, a bola some); a bola some sozinha no prazo. Nenhuma rng. Tudo
    PROPOSTO, sem fonte (protocol.PARAMETROS_BOLA_A1); duracao, ganho e w_bola vieram da calibracao (plano, secao 4;
    artifacts_v2_a1/calibracao/resultado.json: a calibracao NAO fechou, o ponto e o de maior limite inferior do Delta p).
    Desligada: o MotorAmbiente e o MotorEducacao byte a byte, e `por_bola` no log levanta erro."""

    ligada: bool = False
    duracao_min: int = 120                   # a bola fica no cenario por tantos minutos, se ninguem a usar ou tirar (calibrado)
    ganho_humor_bola: float = 0.15           # humor a mais ao brincar com a bola, alem do efeito do brincar de sempre (calibrado)
    w_bola: float = 6.0                      # peso a mais de brincar na regra de tempo livre do instinto, com bola (calibrado)
    bolas_por_dia: int = 4                   # dos donos sinteticos coerentes (ambiente.DonoComBola), nao do motor


CONFIG_BOLA = ConfigBola()
CONFIG_BOLA_LIGADA = ConfigBola(ligada=True)


def _rotacao_ofertas() -> tuple:
    """o conjunto de frutas de cada oferta, em rotacao (4 de 7 com pelo menos duas frutas ao mesmo tempo; F3)"""
    return (("a",), ("b", "c"), ("a", "b", "c"), ("c",), ("a", "b"), ("b",), ("a", "c"))


@dataclass(frozen=True)
class ConfigFrutas:
    """V2, N4 (docs/DEFINICOES_FRUTAS_V2.md, F1-F11; plano docs/PLANO_ANALISE_V2_N4.md): frutas no mundo, sem aprendizado de
    politica. O dono oferece (fora do orcamento e fora do sorteio do aleatorio, B1 e B2); o pet escolhe ao `comer`, pelo incentivo;
    dois registros por fruta (incentivo antes, avaliacao depois); a avaliacao cai com o consumo recente DAQUELA fruta, sem a fome;
    neofobia e preferencia inata no genoma (rng propria); efeito no corpo separado do gosto, o ruim no humor. Tudo PROPOSTO, sem
    fonte (protocol.PARAMETROS_FRUTAS_N4); duracao_min, w_fruta e k_saciedade vieram da calibracao (plano, secao 4;
    artifacts_v2_n4/calibracao/resultado.json: a calibracao NAO fechou, o ponto e o de maior limite inferior do G-SEP(i)).
    Desligada: o MotorFrutas e o MotorAmbiente byte a byte, e uma oferta no log levanta erro."""

    ligada: bool = False
    duracao_min: int = 120                   # a fruta fica no cenario por tantos minutos, se nao for comida (calibrado)
    w_fruta: float = 6.0                     # peso de comer no tempo livre com fruta, x o maior incentivo no cenario (calibrado)
    k_saciedade: float = 1.0                 # queda da avaliacao por unidade de consumo recente daquela fruta (calibrado)
    meia_vida_recente: int = 16              # decisoes (16 x 15 min = 4 h) para o consumo recente cair a metade
    taxa_incentivo: float = 0.3              # incentivo += taxa x (avaliacao - incentivo), so no consumo
    nutricao: float = 0.10                   # fome a mais por fruta comida, alem do comer de sempre; igual em todas
    efeito_humor_ruim: float = -0.10         # mundo descasado: a fruta de maior preferencia inata faz mal (no humor, F6)
    efeito_humor_neutro: float = 0.0         # as outras frutas (e todas, no mundo "iguais")
    mundo: str = "descasado"                 # "descasado" | "iguais" (variante de efeito igual, F7)
    neofobia_max: float = 1.0                # genoma: neofobia ~ U[0, neofobia_max]
    pref_min: float = 0.2                    # genoma: preferencia inata ~ U[pref_min, pref_max] por fruta
    pref_max: float = 1.0
    horarios_oferta: tuple = (540, 720, 900, 1080)   # 9h, 12h, 15h e 18h: passos do dono em que ha oferta, com o pet acordado
    rotacao_ofertas: tuple = field(default_factory=_rotacao_ofertas)


CONFIG_FRUTAS = ConfigFrutas()
CONFIG_FRUTAS_LIGADA = ConfigFrutas(ligada=True)


@dataclass(frozen=True)
class ConfigInformacao:
    """V2, N5, lado do mundo (docs/TAREFA_V2_N5_MUNDO.md): o dono informa sobre uma fruta ("faz bem" ou "faz mal"). A informacao nao e
    cuidado nem reforco: nao mexe no estado, nao passa pelo aprendiz como sinal e fica fora do orcamento (o canal das ofertas, B2). Ela so
    fica disponivel para a percepcao (`Observacao.info_frutas`) por uma janela. Exige ConfigFrutas.ligada. Tudo PROPOSTO, sem fonte
    (protocol.PARAMETROS_INFORMACAO_N5); o desenho fino e o plano sao do chat C (docs/TAREFA_V2_N5_PLANO.md).
    Desligada: nada muda (a vida das frutas byte a byte), e uma informacao no log levanta erro."""

    ligada: bool = False
    janela_min: int = 240                    # quanto tempo uma informacao vale para a percepcao, desde o evento (renovar reinicia)


CONFIG_INFORMACAO = ConfigInformacao()
CONFIG_INFORMACAO_LIGADA = ConfigInformacao(ligada=True)


@dataclass(frozen=True)
class ConfigPedido:
    """V2, N7, lado do mundo (docs/TAREFA_V2_N7_MUNDO.md; docs/PLANO_ANALISE_V2_N7.md, secao 2): o dono pede \"deixe a fruta X\". O pedido
    nao e cuidado nem reforco: nao mexe no estado, nao passa pelo aprendiz como sinal e fica fora do orcamento (o canal das ofertas, B2).
    Ele so fica disponivel para a percepcao (`Observacao.pedido_frutas`) por uma janela. Exige ConfigFrutas.ligada. Tudo PROPOSTO
    (protocol.PARAMETROS_PEDIDO_N7). Desligada: nada muda (a vida das frutas byte a byte), e um pedido no log levanta erro."""

    ligada: bool = False
    janela_min: int = 240                    # quanto tempo um pedido vale para a percepcao, desde o evento (pedir de novo renova)
    dias_pedido: int = 10                    # o DonoPedinte so pede nos dias 1..dias_pedido; depois e a extincao (N7-7)


CONFIG_PEDIDO = ConfigPedido()
CONFIG_PEDIDO_LIGADA = ConfigPedido(ligada=True)


@dataclass(frozen=True)
class ConfigJulgamentoFruta:
    """V2, K4 (docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md; contrato K4 e decisao E7 do experimento maior; decisao K-11): o dono do P3 julga
    cada consumo de fruta pelo efeito real vigente (elogia a boa, repreende a ruim, nada com a neutra), no primeiro passo depois do
    consumo. `ligada` faz o MotorFrutas expor os consumos em estado()[\"consumos_frutas\"] (o que o dono ve). `no_orcamento`: o
    julgamento usa elogiar/repreender DENTRO do orcamento, como o resto do feedback do P3 (a escolha registrada); False = fora do
    orcamento, pelo canal do mundo, como as informacoes (a alternativa, atras da opcao, para o Matheus decidir). Tudo PROPOSTO
    (protocol.PARAMETROS_JULGAMENTO_K4). Desligada: nada muda."""

    ligada: bool = False
    no_orcamento: bool = True


CONFIG_JULGAMENTO_FRUTA = ConfigJulgamentoFruta()
CONFIG_JULGAMENTO_FRUTA_LIGADA = ConfigJulgamentoFruta(ligada=True)


@dataclass(frozen=True)
class ConfigCorpo:
    """V2, o corpo do Creatures 3 por baixo dos drives (docs/TAREFA_V2_CORPO_DRIVES.md; CD-1 a CD-10 decididas). A quimica guarda a
    FALTA de cada drive em inteiros de [0, escala]; o drive de hoje e a leitura (escala - q) / escala. Etapa 1 (W-CORPO-QUIMICA): a
    quimica dos drives de hoje, sem orgao (`ligada`). Etapas 3 e 4 (W-CORPO-DIGESTAO): o orgao 1, a digestao (`digestao`), e o orgao 2, a
    Vida (`vida`). Etapa 6 (CORPO-DRIVES): os drives novos (`drives_novos`: tedio pela variedade, DS-4; curiosidade, so com o mundo
    fisico; solidao; estresse) e os gestos (`gestos`: o tapa, a dor, o susto e o medo da mao no carinho). Cada sub-chave exige a
    anterior (E-9, um orgao por vez). Desligada: nada existe (a vida de hoje byte a byte). O grafo do corpo e uma tabela unica,
    validada na carga (digilab/corpo_grafo.py, secao 18). Status em corpo.PARAMETROS_CORPO.

    Os numeros das secoes 7, 8 e 17 sao PROPOSTOS, sem fonte. O plano do corpo calibra as subidas (`m_sobe`: tedio_sobe, solidao_sobe e
    o estresse_divisor) e as reducoes (`m_reduz`: as bases do tedio e o carinho) trocando estes campos."""

    ligada: bool = False
    digestao: bool = False                   # etapa 3, orgao 1 (secao 5)
    vida: bool = False                       # etapa 4, orgao 2 (secao 6)
    drives_novos: bool = False               # etapa 6 (secao 7)
    gestos: bool = False                     # etapa 6 (secao 8)
    banheiro: bool = False                   # o banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 3 e BN-6): a vontade e o conforto; exige gestos
    escala: int = 450000                     # C (CD-1): o mmc dos denominadores das taxas de hoje; todo numero de hoje vira inteiro
    escala_receptor: int = 1024              # S: a escala do cerebro A (2**ConfigLobos.bits_ponto_fixo); receptor = div_arred(q * S, C)
    bits_meia_vida: int = 16                 # k_h = arred(2**bits * (1 - 2**(-1/h))) (secao 3)
    # os efeitos da acao do pet: os literais de policy.efeito_da_acao_do_pet, ja na escala C, com o sinal da FALTA (o brincar do pet no
    # humor vem de Config.humor_por_tick_brincando * intervalo_decisao_ticks, nao daqui)
    pet_brincar_cansaco: int = 9000          # energia -0,02
    pet_explorar_cansaco: int = 6750         # energia -0,015
    pet_explorar_tristeza: int = -4500       # humor +0,01
    pet_comer_fome: int = -22500             # fome +0,05
    pet_emburrar_tristeza: int = 4500        # humor -0,01
    # as constantes das meias-vidas da secao 3, para os quimicos novos (etapa 6): ficam aqui como inteiros; nenhum tick as deriva
    k_meia_vida_susto: int = 1497            # h = 30 (secao 8)
    k_meia_vida_dor: int = 753               # h = 60 (secao 8)
    k_meia_vida_estresse: int = 32           # h = 1440 (secao 7)
    # orgao 1, a digestao (secao 5): quanto `alimento` passa para a fome por tick. C = tudo no mesmo tick (CD-3, a fome de hoje); uma
    # taxa menor e a digestao lenta, PROPOSTA, que so entra com o plano
    taxa_digestao: int = 450000
    # orgao 2, a Vida (secao 6): quanto a Vida cai por tick. C // (28 dias x 1440) = 11: a Vida dura a vida mais longa da pesquisa (os 28
    # dias do bloco de duracoes do adendo 3) e nao muda nada nesta etapa
    vida_decaimento: int = 11
    # etapa 6, os drives novos (secao 7; DS-4, secao 17). Sobem por tick acordado; dormindo, tedio, curiosidade e solidao nao sobem
    tedio_sobe: int = 450                    # cheio em ~17 h
    curiosidade_sobe: int = 300              # cheia em 25 h (so com o mundo fisico, CD-8)
    solidao_sobe: int = 225                  # cheia em ~33 h
    estresse_limiar: int = 337500            # 0,75 de falta: o estresse acumula com os drives acima disto
    estresse_divisor: int = 256              # estresse += div_arred(soma max(0, q_d - limiar), divisor) por tick
    janela_tedio: int = 8                    # DS-4: as ultimas J atividades (fixa em 8 pelo adendo 1, A1.2)
    tedio_bola: int = 135000                 # a base da reducao de cada atividade (DS-4)
    tedio_brincar: int = 45000
    tedio_explorar: int = 90000
    tedio_dono: int = 90000
    curiosidade_novidade: int = 90000        # por novidade achada ao explorar
    curiosidade_max_novidades: int = 2       # ate 2 por decisao
    janela_novidade: int = 1440              # um objeto e novidade se o pet nao o viu nestes ticks (o registro e do motor)
    carinho_solidao: int = 180000            # acariciar (secao 8), com o medo da mao
    carinho_estresse: int = 90000
    # etapa 6, os gestos (secao 8)
    tapa_dor: int = 90000
    tapa_susto: int = 180000
    tapa_estresse: int = 45000
    medo_da_mao: int = 1                     # CD-5: o carinho na solidao e no estresse vezes (C - medo_da_mao * q_susto) / C; 0 = sem medo
    # o banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 3; BN-6), sub-chave `banheiro`. A vontade e uma concentracao (o receptor le a
    # concentracao, como a dor); o conforto tambem (o cerebro le a falta de conforto, S - leitura). PROPOSTOS, sem fonte
    vontade_sobe: int = 150                  # por tick acordado: cheia em 50 h sem comer
    vontade_digestao_num: int = 1            # a digestao poe na vontade num/den do alimento digerido (1/3), com o resto guardado
    vontade_digestao_den: int = 3
    vontade_limiar: int = 337500             # 0,75: acima disto o desconforto sobe vontade_desconforto por tick
    vontade_desconforto: int = 150
    necessidade_desconforto: int = 22500     # a necessidade deixada no chao: o "cheiro" imediato (o motor chama o estimulo)
    necessidade_regiao: int = 100            # por tick, por necessidade na regiao do pet (o motor conta), ate necessidade_max_regiao
    necessidade_max_regiao: int = 3
    conforto_carinho: int = 45000            # BN-6: o carinho sobe o conforto (com o medo da mao); o menor da grade 6.1 do plano
    k_meia_vida_conforto: int = 753          # h = 60 (a menor da grade 6.1 do plano): o conforto cai devagar entre os carinhos
    # o metabolismo energetico (docs/TAREFA_V2_METABOLISMO.md, secao 3; ME-1 a ME-7 pela recomendacao, Matheus, 2026-10-11), sub-chave
    # `metabolismo`, que exige a digestao. O combustivel e a reserva sao concentracoes, sem receptor (ME-2); a unica ponte para o pet e a
    # falta, que sobe o cansaco (ME-1). Numeros PROPOSTOS, sem fonte; o passo 0 da calibracao do corpo escala o gasto (ME-7)
    metabolismo: bool = False
    combustivel_inicial: int = 225000        # C/2 ao nascer
    reserva_inicial: int = 112500            # C/4 ao nascer
    conversao_num: int = 1                   # a digestao poe no combustivel num/den do alimento digerido, com o resto guardado (como a
    conversao_den: int = 1                   # vontade). 1/1: com o gasto basal igual a subida da fome, comer o que a fome pede o mantem
    gasto_basal_acordado: int = 375          # por tick acordado (= a subida da fome)
    gasto_basal_dormindo: int = 187          # por tick dormindo (a metade)
    armazenar_limiar: int = 337500           # 3C/4: acima disto o combustivel vai a reserva...
    armazenar_taxa: int = 375                # ...ate isto por tick
    mobilizar_limiar: int = 225000           # C/2: abaixo disto a reserva volta ao combustivel...
    mobilizar_taxa: int = 375                # ...ate isto por tick
    falta_limiar: int = 112500               # C/4: abaixo disto, a falta de combustivel...
    falta_cansaco: int = 500                 # ...sobe o cansaco isto por tick (o de um tick acordado de dia); a unica ponte (ME-1)
    # o gasto das atividades sobre o combustivel (ME-3 e ME-7; o no `gasto_atividades` do #273): o brincar, o explorar, o andar e o
    # brincar do dono tiram do combustivel div_arred(o que somam ao cansaco x num, den). 1/1 = o mesmo numero (a vida de hoje); o passo 0
    # da calibracao do corpo escala por {1/2, 1, 2}. O cansaco nunca muda
    gasto_atividades_num: int = 1
    gasto_atividades_den: int = 1
    # o Paladar (docs/futuro/paladar.md, secoes 3.2 e 3.3; PL-1 a PL-9 pela recomendacao, 2026-10-13): o orgao do gosto, por qualidade
    # (doce, azedo, amargo, salgado). Ao comer, `sabor_q` recebe max(0, perfil_q - saciedade_q) e `saciedade_q` sobe
    # div_arred(perfil_q x saciedade_num, saciedade_den); o receptor `paladar_q` le o `sabor_q`. Sem quimico de prazer (PL-1). Exige
    # `ligada` e o mundo fisico (o perfil vem do mundo, a ConfigPaladar do A). Os numeros sao PROPOSTOS, SEM FONTE
    paladar: bool = False
    meia_vida_sabor: int = 4                 # o sinal na boca acaba antes da decisao seguinte
    k_meia_vida_sabor: int = 10427           # = k_meia_vida(4)
    meia_vida_saciedade: int = 720           # 12 h (PL-4)
    k_meia_vida_saciedade: int = 63          # = k_meia_vida(720)
    saciedade_num: int = 1                   # k_sac = 1/2
    saciedade_den: int = 2
    # o genoma do paladar (secao 3.3, PL-2; digilab/genoma_paladar.py, rng `paladar-ovo`): h_q das frutas uniformes e independentes em
    # [paladar_h_min, paladar_h_max] (na escala S do cerebro), h_salgado o mesmo para todos
    paladar_h_min: int = -512                # -S/2
    paladar_h_max: int = 1024                # S
    paladar_h_salgado: int = 256             # S/4: o gosto basico da racao

    def __post_init__(self) -> None:
        ordem = (("ligada", self.ligada), ("digestao", self.digestao), ("vida", self.vida),
                 ("drives_novos", self.drives_novos), ("gestos", self.gestos), ("banheiro", self.banheiro))
        for (anterior, ligou_antes), (nome, ligou) in zip(ordem, ordem[1:]):
            if ligou and not ligou_antes:
                raise ValueError(f"ConfigCorpo.{nome} exige ConfigCorpo.{anterior} (E-9: um orgao por vez)")
        if self.taxa_digestao <= 0:
            raise ValueError(f"ConfigCorpo.taxa_digestao tem de ser positiva: {self.taxa_digestao}")
        if self.vida_decaimento <= 0:
            raise ValueError(f"ConfigCorpo.vida_decaimento tem de ser positivo: {self.vida_decaimento}")
        positivos = ("tedio_sobe", "curiosidade_sobe", "solidao_sobe", "estresse_limiar", "estresse_divisor", "janela_tedio",
                     "tedio_bola", "tedio_brincar", "tedio_explorar", "tedio_dono", "curiosidade_novidade", "curiosidade_max_novidades",
                     "janela_novidade", "carinho_solidao", "carinho_estresse", "tapa_dor", "tapa_susto", "tapa_estresse",
                     "vontade_sobe", "vontade_digestao_num", "vontade_digestao_den", "vontade_limiar", "vontade_desconforto",
                     "necessidade_desconforto", "necessidade_regiao", "necessidade_max_regiao", "conforto_carinho", "k_meia_vida_conforto")
        for nome in positivos:
            v = getattr(self, nome)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigCorpo.{nome} tem de ser inteiro positivo: {v!r}")
        if self.medo_da_mao not in (0, 1) or type(self.medo_da_mao) is not int:
            raise ValueError(f"ConfigCorpo.medo_da_mao e 0 (sem medo) ou 1: {self.medo_da_mao!r}")
        if self.vontade_digestao_num > self.vontade_digestao_den:
            raise ValueError("ConfigCorpo.vontade_digestao_num / vontade_digestao_den passa de 1")
        if self.banheiro and self.vontade_limiar >= self.escala:
            raise ValueError(f"ConfigCorpo.vontade_limiar tem de ficar abaixo de C: {self.vontade_limiar}")
        if type(self.metabolismo) is not bool:
            raise TypeError(f"ConfigCorpo.metabolismo e bool: {self.metabolismo!r}")
        if self.metabolismo and not self.digestao:
            raise ValueError("ConfigCorpo.metabolismo exige ConfigCorpo.digestao (E-9: a comida digerida e o que vira combustivel)")
        for nome in ("conversao_num", "conversao_den", "gasto_basal_acordado", "gasto_basal_dormindo", "armazenar_limiar",
                     "armazenar_taxa", "mobilizar_limiar", "mobilizar_taxa", "falta_limiar", "falta_cansaco", "gasto_atividades_num",
                     "gasto_atividades_den"):
            v = getattr(self, nome)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigCorpo.{nome} tem de ser inteiro positivo: {v!r}")
        for nome in ("combustivel_inicial", "reserva_inicial"):
            v = getattr(self, nome)
            if type(v) is not int or (self.metabolismo and not 0 <= v <= self.escala):
                raise ValueError(f"ConfigCorpo.{nome} tem de ser inteiro em [0, C]: {v!r}")
        if self.metabolismo and not self.falta_limiar < self.mobilizar_limiar < self.armazenar_limiar < self.escala:
            raise ValueError("o metabolismo pede falta_limiar < mobilizar_limiar < armazenar_limiar < C: "
                             f"{self.falta_limiar}, {self.mobilizar_limiar}, {self.armazenar_limiar}")
        if type(self.paladar) is not bool:
            raise TypeError(f"ConfigCorpo.paladar e bool: {self.paladar!r}")
        if self.paladar and not self.ligada:
            raise ValueError("ConfigCorpo.paladar exige ConfigCorpo.ligada (o orgao e do corpo)")
        for nome in ("meia_vida_sabor", "k_meia_vida_sabor", "meia_vida_saciedade", "k_meia_vida_saciedade", "saciedade_num",
                     "saciedade_den"):
            v = getattr(self, nome)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigCorpo.{nome} tem de ser inteiro positivo: {v!r}")
        for nome in ("paladar_h_min", "paladar_h_max", "paladar_h_salgado"):
            v = getattr(self, nome)
            if type(v) is not int or not -self.escala_receptor <= v <= self.escala_receptor:
                raise ValueError(f"ConfigCorpo.{nome} tem de ser inteiro em [-S, S]: {v!r}")
        if self.paladar_h_min > self.paladar_h_max:
            raise ValueError(f"ConfigCorpo.paladar_h_min > paladar_h_max: {self.paladar_h_min}, {self.paladar_h_max}")


CONFIG_CORPO = ConfigCorpo()
CONFIG_CORPO_LIGADA = ConfigCorpo(ligada=True)
CONFIG_CORPO_DRIVES = ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True, gestos=True)   # a etapa 6 inteira
CONFIG_CORPO_BANHEIRO = replace(CONFIG_CORPO_DRIVES, banheiro=True)                                        # mais a vontade e o conforto
CONFIG_CORPO_METABOLISMO = replace(CONFIG_CORPO_DRIVES, metabolismo=True)                                  # a etapa 6 com o metabolismo


# =====================================================================
# V2, o mundo fisico minimo (docs/TAREFA_V2_MUNDO_FISICO.md, etapa 2; MF-1 a MF-4 decididas em 2026-10-07). Motor em
# digilab/mundo.py. Desligado por padrao: o MotorFrutas byte a byte. Todos os numeros sao PROPOSTOS, SEM FONTE (tarefa, secao 3);
# os que o plano calibra (`mult_queda`, plano secao 6) saem da calibracao do mundo. Posicoes do layout em CELULAS; o motor usa
# subunidades (celula x `sub`), com o objeto no centro da celula.


@dataclass(frozen=True)
class LayoutMundo:
    """A disposicao fixa do mapa (M-4): as regioes sao faixas de x (celulas, inclusivas), sem parede; as arvores sao
    (id, x, y, fruta), com a fruta fixa por arvore. Iguais em toda vida, no Python e na web."""

    nome: str
    regioes: tuple = (("casa", 0, 15), ("jardim", 16, 33), ("campo", 34, 47), ("mata", 48, 63))
    ninho: tuple = (4, 15)
    comedouro: tuple = (10, 15)
    bola_inicio: tuple = (40, 15)
    # o prototipo docs/futuro/mundo_fisico_vistas.html tem 2 + 4 arvores (10 px por celula); a tarefa pede 3 + 6: as do prototipo
    # ficam onde estao, e entram J3, M5 e M6
    arvores: tuple = (("J1", 22, 6, "a"), ("J2", 29, 20, "b"), ("J3", 19, 14, "c"),
                      ("M1", 53, 4, "a"), ("M2", 60, 15, "b"), ("M3", 50, 23, "c"),
                      ("M4", 62, 26, "a"), ("M5", 56, 10, "b"), ("M6", 55, 19, "c"))


LAYOUT_MUNDO_PADRAO = LayoutMundo("padrao")


def layout_afastado(base: LayoutMundo, altura: int = 30) -> LayoutMundo:
    """O layout do G-DIST (plano, adendo 1, A1.8): cada tronco a duas vezes a distancia do centro da regiao dele, cortado para
    dentro dela. Nada mais muda. Centro da regiao = ((x0 + x1 + 1) // 2, altura // 2), em celulas."""
    arvores = []
    for ident, x, y, fruta in base.arvores:
        _, x0, x1 = next(r for r in base.regioes if r[1] <= x <= r[2])
        cx, cy = (x0 + x1 + 1) // 2, altura // 2
        arvores.append((ident, min(x1, max(x0, cx + 2 * (x - cx))), min(altura - 1, max(0, cy + 2 * (y - cy))), fruta))
    return replace(base, nome="afastado", arvores=tuple(arvores))


LAYOUT_MUNDO_AFASTADO = layout_afastado(LAYOUT_MUNDO_PADRAO)


@dataclass(frozen=True)
class ConfigMundo:
    ligada: bool = False
    layout: LayoutMundo = LAYOUT_MUNDO_PADRAO
    # o mapa (secao 3): 64 x 30 celulas de 16 subunidades; posicoes inteiras em subunidades
    celulas_x: int = 64
    celulas_y: int = 30
    sub: int = 16
    # o deslocamento (secao 5): alcance de uma decisao = velocidade x intervalo_decisao_ticks
    velocidade: int = 4                          # subunidades por tick (60 por decisao: ~3 h da casa ao fundo da mata)
    custo_energia_por_subunidade: float = 1.0 / 6000.0   # 60 subunidades = 0,01 de energia, alem do efeito da acao
    raio_pegar_celulas: int = 1
    # a percepcao (secao 7)
    raio_visao_celulas: int = 6
    max_vistos: int = 8
    cheiro_racao: int = 64                       # A da racao
    cheiro_fruta: int = 32                       # A da fruta
    raio_cheiro_celulas: int = 24                # R
    # os alvos (secao 5)
    limiar_cheiro_explorar: int = 16
    passo_cheiro_celulas: int = 8                # o alvo `cheiro`: 8 celulas na direcao do cheiro
    vagar_min_celulas: int = 4
    vagar_max_celulas: int = 12
    fome_max_comer_achado: float = 0.85          # MF-1
    # as comidas (secao 5)
    nutricao_fruta: float = 0.15                 # os 0,05 do comer mais os 0,10 do N4 (a racao usa Config.ganho_alimentar)
    efeito_podre: float = -0.10                  # igual ao ConfigFrutas.efeito_humor_ruim
    ganho_humor_bola: float = 0.15               # igual ao ConfigBola.ganho_humor_bola (A1)
    # as arvores (secao 6): um passo do mundo a cada `passo_mundo_ticks`
    passo_mundo_ticks: int = 15
    p_queda_jardim: float = 1.0 / 96.0
    p_queda_mata: float = 2.0 / 96.0
    mult_queda: float = 1.0                      # o m da calibracao do mundo (plano, secao 6), em {1/2, 1, 2}
    frutas_por_queda_min: int = 1
    frutas_por_queda_max: int = 3
    raio_queda_celulas: int = 2
    max_frutas_por_arvore: int = 4
    recarga_min: int = 720
    # apodrecer (secao 6)
    maduro_fruta_min: int = 720
    maduro_racao_min: int = 1440
    prazo_podre_min: int = 720
    # a bola rola (secao 6): distancia em celulas (no campo, x mult_bola_campo), `atrito` subunidades por tick ate parar
    bola_min_celulas: int = 3
    bola_max_celulas: int = 10
    mult_bola_campo: int = 2
    atrito: int = 8
    # o DonoComLugar (secao 4)
    perto_max_celulas: int = 2
    longe_min_celulas: int = 20
    longe_max_celulas: int = 30
    # o que o motor registra para as medidas do plano (adendo 1, A1.8): a mancha de uma arvore
    raio_mancha_celulas: int = 3

    def __post_init__(self) -> None:
        if self.celulas_x * self.sub != 1024 or self.celulas_y * self.sub != 480:
            raise ValueError("o mapa da tarefa e 64 x 30 celulas de 16 subunidades (secao 3)")
        if self.velocidade <= 0 or self.atrito <= 0:
            raise ValueError("velocidade e atrito precisam ser positivos")
        if self.mult_queda <= 0.0:
            raise ValueError(f"mult_queda precisa ser positivo: {self.mult_queda}")


CONFIG_MUNDO = ConfigMundo()
CONFIG_MUNDO_LIGADA = ConfigMundo(ligada=True)

# O mundo do produto no MVP (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 1; decisao do Matheus de 2026-10-24, a opcao 1): o layout
# padrao sem arvores, so com a racao do jogador. So o jogo (o pet v12) e o gabarito dele (experiments/exportar_gabarito_mvp_produto.py)
# o usam; a bancada e os cenarios de pesquisa seguem com o LAYOUT_MUNDO_PADRAO (tests/test_gabarito_mvp_produto_web.py confere que
# ele nao vaza). PROPOSTO, SEM FONTE: o motivo e o A v11 sem as chaves do mundo, que nao come a fruta do mundo (registro 2026-10-24).
LAYOUT_MUNDO_MVP = replace(LAYOUT_MUNDO_PADRAO, nome="mvp", arvores=())                  # PROPOSTO, SEM FONTE
CONFIG_MUNDO_MVP = replace(CONFIG_MUNDO_LIGADA, layout=LAYOUT_MUNDO_MVP)                  # PROPOSTO, SEM FONTE


# =====================================================================
# V2, o banheiro (docs/TAREFA_V2_BANHEIRO.md; BN-1 a BN-6 decididas em 2026-10-07). Desligado por padrao: a vida de hoje byte a byte.
# Exige o mundo fisico (ConfigMundo.ligada) e o corpo com a sub-chave `banheiro` (que exige os gestos); quem usa confere e falha alto.
# A quimica (a vontade, o desconforto dela, o conforto do carinho) fica na ConfigCorpo; aqui, a chave, o limpador e o instinto do alivio
# (digilab/instinto_banheiro.py). O banheiro no mapa, o objeto e o limpador no motor sao da etapa 3 (A). Todos PROPOSTOS, sem fonte;
# status em instinto_banheiro.PARAMETROS_BANHEIRO.


@dataclass(frozen=True)
class ConfigBanheiro:
    """ligada            o banheiro (a acao `aliviar`, a vontade no instinto, o alvo `banheiro`/`aqui`)
    limpador           recolhe na hora a necessidade deixada no banheiro (secao 3; o motor, etapa 3)
    w_vontade          no tempo livre, `aliviar` entra com peso w_vontade x vontade (secao 4; o plano calibra, m_w)
    limiar_urgente     vontade acima disto: alivia ja, com o alvo `aqui` (o acidente; a regra urgente, que nao se aprende)
    limiar_moderada    vontade acima disto: `aliviar` entra no tempo livre
    w_banheiro_0       o peso herdado do alvo `banheiro`, inteiro na escala S (S/4: o pet nasce preferindo `aqui` 4 a 1)
    w_aqui_0           o peso herdado do alvo `aqui` (S)
    celulas_x          o banheiro no mapa (secao 3; BN-8, 2026-10-11): as colunas de celulas, inclusivas, dentro da casa (8 a 12)
    celulas_y          as linhas de celulas, inclusivas (18 a 20): ao alcance de uma decisao (40 subunidades) do comedouro (10, 15),
                       onde o pet passa o dia, sem cobrir o comedouro nem o ninho (4, 15). Antes (#265): x 0 a 3, y 0 a 5, no canto"""

    ligada: bool = False
    limpador: bool = False
    w_vontade: float = 4.0
    limiar_urgente: float = 0.90
    limiar_moderada: float = 0.50
    w_banheiro_0: int = 256
    w_aqui_0: int = 1024
    celulas_x: tuple = (8, 12)
    celulas_y: tuple = (18, 20)

    def __post_init__(self) -> None:
        if self.w_vontade < 0.0:
            raise ValueError(f"ConfigBanheiro.w_vontade precisa ser >= 0: {self.w_vontade}")
        if not 0.0 < self.limiar_moderada < self.limiar_urgente < 1.0:
            raise ValueError(f"ConfigBanheiro: 0 < limiar_moderada < limiar_urgente < 1: {self.limiar_moderada}, {self.limiar_urgente}")
        for nome in ("w_banheiro_0", "w_aqui_0"):
            v = getattr(self, nome)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigBanheiro.{nome} tem de ser inteiro positivo: {v!r}")
        for nome in ("celulas_x", "celulas_y"):
            v = getattr(self, nome)
            if (type(v) is not tuple or len(v) != 2 or any(type(c) is not int for c in v) or not 0 <= v[0] <= v[1]):
                raise ValueError(f"ConfigBanheiro.{nome} tem de ser (inicio, fim) inteiros, 0 <= inicio <= fim: {v!r}")


CONFIG_BANHEIRO = ConfigBanheiro()
CONFIG_BANHEIRO_LIGADA = ConfigBanheiro(ligada=True)


# =====================================================================
# V2, dois pets de verdade no mesmo mundo (docs/TAREFA_V2_DOIS_PETS.md, etapa 2; desenho docs/futuro/dois_pets.md, secoes 2 a 4, DP-1 a
# DP-3 e DP-7). O grupo: N motores sobre um Mundo (digilab/grupo.py). Desligado por padrao: sem o grupo nada muda (o MotorMundo de um
# pet e dono do proprio Mundo). Os rotulos das sementes (`mundo-ordem`, `segundo-pet`) sao constantes do grupo.py, como os do mundo.


@dataclass(frozen=True)
class ConfigGrupo:
    """O grupo de pets no mundo fisico. Os pets sao `ids`, na ordem dos identificadores (a vez no tick e sorteada, nunca a ordem do codigo);
    o primeiro usa a semente do grupo (sozinho no mapa, e a vida de hoje dessa semente), o segundo `derivar_semente("segundo-pet", s)`.
    `orcamento_por_dia`: as interacoes do dono por dia vivido, POR PET (DP-7, a validacao inicial com um dono so). Um pet entra num
    inicio de dia do mundo (multiplo de TICKS_POR_DIA), para a hora do dia ser a mesma no relogio dele e no do mundo."""

    ligada: bool = False
    ids: tuple = ("A", "B")                  # DP-1: dois pets; o desenho do grupo aceita N, a pesquisa usa dois
    orcamento_por_dia: int = 16              # DP-7: 16 interacoes por dia para cada pet (o orcamento de hoje)
    raio_toque_celulas: int = 1              # dois pets, secao 5.2: o contato com as celulas a ate 1 em Chebyshev (a mesma ou a vizinha)

    def __post_init__(self) -> None:
        if not self.ids or len(set(self.ids)) != len(self.ids) or any(type(i) is not str or not i for i in self.ids):
            raise ValueError(f"ConfigGrupo.ids precisa de nomes distintos e nao vazios: {self.ids!r}")
        if len(self.ids) > 2:
            raise ValueError("ConfigGrupo.ids: so dois pets nesta etapa (a semente de um terceiro nao esta no desenho)")
        if list(self.ids) != sorted(self.ids):
            raise ValueError(f"ConfigGrupo.ids em ordem (a lista dos pets e ordenada pelo identificador): {self.ids!r}")
        if type(self.orcamento_por_dia) is not int or self.orcamento_por_dia <= 0:
            raise ValueError(f"ConfigGrupo.orcamento_por_dia tem de ser inteiro positivo: {self.orcamento_por_dia!r}")
        if type(self.raio_toque_celulas) is not int or self.raio_toque_celulas < 0:
            raise ValueError(f"ConfigGrupo.raio_toque_celulas tem de ser inteiro nao negativo: {self.raio_toque_celulas!r}")


CONFIG_GRUPO = ConfigGrupo()
CONFIG_GRUPO_LIGADA = ConfigGrupo(ligada=True)


# =====================================================================
# V2, a rede de si (docs/TAREFA_V2_REDE_DE_SI.md, etapas 1 e 2; RS-1 a RS-7 pela recomendacao): o automodelo em observacao. A rede
# (digilab/rede_de_si.py) preve os receptores do corpo a n decisoes e estima a propria escolha, so olhando; nao muda a vida. Desligada por
# padrao. Todos PROPOSTOS, sem fonte; status em rede_de_si.PARAMETROS_REDE_DE_SI.


@dataclass(frozen=True)
class ConfigRedeDeSi:
    """ligada         a rede (o embrulho `PoliticaComRede` exige a chave)
    escala          S: a escala dos receptores e dos pesos (a do cerebro A e do corpo)
    passo           o passo do LMS em inteiros (o plano calibra na grade {S/64, S/16, S/4})
    teto            |w - w0| <= teto, por peso
    horizontes      os n da cabeca do corpo, em decisoes (RS-1: 15 min, 1 h, 4 h)
    faixas_idade    os limites das faixas de idade, em decisoes vividas (1, 3 e 7 dias de 96 decisoes): 4 faixas
    fator_erro      o erro recente e uma media em inteiros: e += div_arred((|erro| - e) x fator, S)
    maximo_pesos    as duas cabecas somam menos que isto"""

    ligada: bool = False
    escala: int = 1024
    passo: int = 64
    teto: int = 4096
    horizontes: tuple = (1, 4, 16)
    faixas_idade: tuple = (96, 288, 672)
    fator_erro: int = 64
    maximo_pesos: int = 1000

    def __post_init__(self) -> None:
        for nome in ("escala", "teto", "fator_erro", "maximo_pesos"):
            v = getattr(self, nome)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigRedeDeSi.{nome} tem de ser inteiro positivo: {v!r}")
        if type(self.passo) is not int or self.passo < 0:
            raise ValueError(f"ConfigRedeDeSi.passo tem de ser inteiro >= 0: {self.passo!r}")
        if self.fator_erro > self.escala:
            raise ValueError("ConfigRedeDeSi.fator_erro passa de S")
        for nome in ("horizontes", "faixas_idade"):
            v = tuple(getattr(self, nome))
            if not v or any(type(x) is not int or x <= 0 for x in v) or list(v) != sorted(set(v)):
                raise ValueError(f"ConfigRedeDeSi.{nome}: inteiros positivos, crescentes e sem repeticao: {v!r}")


CONFIG_REDE_DE_SI = ConfigRedeDeSi()
CONFIG_REDE_DE_SI_LIGADA = ConfigRedeDeSi(ligada=True)


@dataclass(frozen=True)
class ConfigModeloMundo:
    """Os modelos do mundo do pet que pensa (J5, docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.1; digilab/modelo_mundo.py): o modelo do desfecho
    (por tipo de comida e receptor, a mudanca esperada da leitura ao comer, e o custo de andar previsto) e o mapa da comida (por arvore e
    pelo comedouro, a frequencia do tipo visto la). Na etapa 1 so observam (o embrulho `PoliticaComModelo`); o planejador e a etapa 2.
    Registro de status: modelo_mundo.PARAMETROS_MODELO_MUNDO. Todos PROPOSTOS, sem fonte (PP-6), nenhum referendado.

    ligada               a chave: os modelos so existem com ela
    escala               S, a dos receptores do corpo e do cerebro A
    passo_desfecho       o passo do modelo do desfecho e do custo de andar: d += div_arred((obs - d) x passo, S) (S/4)
    passo_mapa           o passo do mapa: m += div_arred((1[tipo] x S - m) x passo, S) (S/8)
    raio_ancora_celulas  a comida vista a ate este raio de um tronco ja visto conta para a arvore (2 celulas)
    teto_modelo          os modelos somam menos inteiros que isto (no regime quimica: 5 tipos x 5 receptores + 1 + 10 lugares x 5 = 76)"""

    ligada: bool = False
    escala: int = 1024
    passo_desfecho: int = 256
    passo_mapa: int = 128
    raio_ancora_celulas: int = 2
    teto_modelo: int = 200

    def __post_init__(self) -> None:
        for nome in ("escala", "raio_ancora_celulas", "teto_modelo"):
            v = getattr(self, nome)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigModeloMundo.{nome} tem de ser inteiro positivo: {v!r}")
        for nome in ("passo_desfecho", "passo_mapa"):
            v = getattr(self, nome)
            if type(v) is not int or not 0 <= v <= self.escala:
                raise ValueError(f"ConfigModeloMundo.{nome} tem de ser inteiro em [0, S]: {v!r}")


CONFIG_MODELO_MUNDO = ConfigModeloMundo()
CONFIG_MODELO_MUNDO_LIGADA = ConfigModeloMundo(ligada=True)


# =====================================================================
# V2, o pet que pensa (J5), o mundo (docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.3, etapa 3; PP-1 e PP-5 do
# docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md). Desligada por padrao: a vida de hoje byte a byte. Exige o mundo fisico (ConfigMundo.ligada);
# quem usa confere e falha alto. Ligada, o MotorMundo:
# - guarda os troncos que o pet ja viu (a ate o raio da visao, na decisao e depois de andar) e os poe na percepcao (`troncos`);
# - oferece no explorar um candidato `arvore:<id>` por tronco ja visto, no pe da arvore, depois dos candidatos de hoje (PP-1). O padrao
#   do motor e o instinto nunca os escolhem;
# - aceita a fruta na mao (`dar_fruta_<f>`) e a troca de tipo entre duas classes de arvore (`trocar_arvores_<x>_<y>`), eventos do registro
#   fora do orcamento. Nao ha numero novo: o raio dos troncos e o da visao.


@dataclass(frozen=True)
class ConfigPetQuePensaMundo:
    ligada: bool = False                     # PROPOSTO: a chave (os troncos vistos, os candidatos de arvore, a mao e a troca)


CONFIG_PQP_MUNDO = ConfigPetQuePensaMundo()
CONFIG_PQP_MUNDO_LIGADA = ConfigPetQuePensaMundo(ligada=True)


# =====================================================================
# V2, os orgaos do Olfato e da Audicao (docs/TAREFA_V2_DOIS_PETS.md, etapa 8b; docs/futuro/dois_pets.md, secoes 5.3, 5.4 e 5.6; DP-13 e
# DP-14 DECIDIDAS em 2026-10-11: duas narinas e dois ouvidos). Desligadas por padrao: a vida de hoje byte a byte (G2). Ligadas, o corpo
# (digilab/corpo.py) tem um receptor por canal e por narina (ou ouvido), com limiar, adaptacao e saturacao, que le so a intensidade no
# ponto da narina (do ouvido), sem direcao (G-SEM-DIRECAO); a adaptacao e um quimico do orgao no grafo do corpo, com a meia-vida. Por
# receptor, em inteiros, com I a intensidade que o mundo entrega e `a` o quimico da adaptacao:
#     a <- a + passo(I - a)            a cada tick: div_arred((I - a) x k_adaptacao, 2**bits_meia_vida), com |passo| >= 1 enquanto a != I
#     e = max(0, I - a - limiar)       o limiar
#     r = div_arred(S x e, e + meia_saturacao)   a saturacao, em [0, S): o que o cerebro le
# Com I = 0, o passo da adaptacao e o da meia-vida do grafo (corpo.passo_meia_vida). Os numeros sao PROPOSTOS, SEM FONTE; o plano (por
# adendo) os fixa. Os do mundo (o afastamento das narinas e dos ouvidos, o rastro, o alcance do som) sao do lado do mundo (A): ficam aqui
# para a config ser uma so. Registros de status: corpo.PARAMETROS_OLFATO e corpo.PARAMETROS_OUVIDO.


def _conferir_orgao(nome: str, c) -> None:
    for campo in ("limiar", "meia_saturacao", "meia_vida_adaptacao", "k_adaptacao", "teto_intensidade"):
        v = getattr(c, campo)
        if type(v) is not int or v < 0 or (v == 0 and campo != "limiar"):
            raise ValueError(f"{nome}.{campo} tem de ser inteiro positivo (o limiar, >= 0): {v!r}")


@dataclass(frozen=True)
class ConfigOlfato:
    """O orgao do Olfato (DP-13). `ligada` sem sub-chave falha alto: as sub-chaves sao separadas (ligar uma nao muda a outra).

    narinas               1 ou 2 (DP-13: 2); com 2, `olfato_<canal>_esq` e `_dir`, a +-afastamento_narinas do lado da direcao do ultimo passo
    comida                o Olfato alimentar: o canal `comida` (o cheiro das comidas boas, a mesma `mundo.cheiro_em`, so no ponto)
    outro_pet             o Olfato social (degrau 1b): o canal `outro` (o cheiro proprio e o rastro do outro pet) e os emissores externos
                          do cheiro proprio e do rastro no grafo de cada corpo
    limiar                e = max(0, I - a - limiar)
    meia_saturacao        K: r = div_arred(S e, e + K)
    meia_vida_adaptacao   h da adaptacao, em ticks (um cheiro constante cai a metade em h ticks)
    k_adaptacao           = corpo.k_meia_vida(h), na escala 2**bits_meia_vida (conferido por teste)
    teto_intensidade      o corte de cima do estimulo I e do quimico da adaptacao (a soma das fontes pode passar; o resto e descartado)
    afastamento_narinas   (mundo) subunidades de cada narina ao centro do pet, de lado
    cheiro_pet            (o emissor externo do cheiro proprio) a intensidade A_pet, constante, na posicao do pet
    cheiro_marca          (o emissor externo do rastro) a intensidade A_marca de cada marca, constante, uma por decisao
    raio_celulas          (mundo) R do cheiro do outro pet, como o da comida
    idade_marca           (mundo) T: a marca perde A_marca x (T - idade) // T e some com a idade T
    max_marcas            (mundo) as marcas por pet; as mais antigas saem"""

    ligada: bool = False
    narinas: int = 2
    comida: bool = False
    outro_pet: bool = False
    limiar: int = 4
    meia_saturacao: int = 32
    meia_vida_adaptacao: int = 60
    k_adaptacao: int = 753
    teto_intensidade: int = 4096
    afastamento_narinas: int = 8
    cheiro_pet: int = 32
    cheiro_marca: int = 16
    raio_celulas: int = 24
    idade_marca: int = 240
    max_marcas: int = 16

    def __post_init__(self) -> None:
        for campo in ("ligada", "comida", "outro_pet"):
            if type(getattr(self, campo)) is not bool:
                raise TypeError(f"ConfigOlfato.{campo} e bool: {getattr(self, campo)!r}")
        if self.ligada and not (self.comida or self.outro_pet):
            raise ValueError("ConfigOlfato.ligada sem sub-chave: ligue `comida` (o Olfato alimentar) e/ou `outro_pet` (o Olfato social)")
        if self.narinas not in (1, 2) or type(self.narinas) is not int:
            raise ValueError(f"ConfigOlfato.narinas e 1 ou 2: {self.narinas!r}")
        _conferir_orgao("ConfigOlfato", self)
        for campo in ("afastamento_narinas", "cheiro_pet", "cheiro_marca", "raio_celulas", "idade_marca", "max_marcas"):
            v = getattr(self, campo)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigOlfato.{campo} tem de ser inteiro positivo: {v!r}")


@dataclass(frozen=True)
class ConfigOuvido:
    """O orgao da Audicao (DP-14): o mesmo desenho do Olfato, um canal por tipo de som (`comendo`, `bola`, `chamado`, `emburrado`; o som
    nao e mensagem, e o barulho de uma acao do outro pet). A adaptacao e a habituacao a um som que se repete; entre os sons, ela decai.

    ouvidos               1 ou 2 (DP-14: 2); com 2, `ouvido_<som>_esq` e `_dir`
    limiar, meia_saturacao, meia_vida_adaptacao, k_adaptacao, teto_intensidade   como no Olfato
    afastamento_ouvidos   (mundo) subunidades de cada ouvido ao centro do pet, de lado
    som                   (mundo) a intensidade A de cada som, na posicao do pet que agiu
    raio_som_celulas      (mundo) R_som, alem das 6 da visao (secao 5.4)"""

    ligada: bool = False
    ouvidos: int = 2
    limiar: int = 4
    meia_saturacao: int = 32
    meia_vida_adaptacao: int = 60
    k_adaptacao: int = 753
    teto_intensidade: int = 4096
    afastamento_ouvidos: int = 8
    som: int = 64
    raio_som_celulas: int = 16

    def __post_init__(self) -> None:
        if type(self.ligada) is not bool:
            raise TypeError(f"ConfigOuvido.ligada e bool: {self.ligada!r}")
        if self.ouvidos not in (1, 2) or type(self.ouvidos) is not int:
            raise ValueError(f"ConfigOuvido.ouvidos e 1 ou 2: {self.ouvidos!r}")
        _conferir_orgao("ConfigOuvido", self)
        for campo in ("afastamento_ouvidos", "som", "raio_som_celulas"):
            v = getattr(self, campo)
            if type(v) is not int or v <= 0:
                raise ValueError(f"ConfigOuvido.{campo} tem de ser inteiro positivo: {v!r}")


CONFIG_OLFATO = ConfigOlfato()
CONFIG_OUVIDO = ConfigOuvido()


# =====================================================================
# V2, rede de si, etapa 2b (docs/TAREFA_V2_REDE_DE_SI.md; docs/PLANO_ANALISE_V2_REDE_DE_SI.md, secao 3, RS-3): a troca da digestao num
# tick, gravada no registro como a troca do mutavel. O tick vem de quem monta a vida (a bancada: o fim do dia 7 numa vida de 14); a taxa
# lenta, daqui. Sem a troca pedida, nada muda (a vida de hoje).


@dataclass(frozen=True)
class ConfigTrocaDigestao:
    taxa_lenta: int = 56250                  # PROPOSTO, SEM FONTE: C // 8 (plano, secao 3); o adendo 1 escolhe da grade {C//2, C//4, C//8}

    def __post_init__(self) -> None:
        if type(self.taxa_lenta) is not int or self.taxa_lenta <= 0:
            raise ValueError(f"ConfigTrocaDigestao.taxa_lenta tem de ser inteiro positivo: {self.taxa_lenta!r}")


CONFIG_TROCA_DIGESTAO = ConfigTrocaDigestao()


# V2, dois pets, etapa 8 (degrau 1b), o lado do mundo (docs/TAREFA_V2_DOIS_PETS.md, etapa 8; docs/futuro/dois_pets.md, secoes 5.3, 5.4 e
# 5.6; DP-11, DP-13 e DP-14 decididas; OA-1 a OA-3 da revisao docs/referencias/H_REVISAO_OLFATO_AUDICAO.md, secao 6). Desligada por
# padrao: o grupo de hoje byte a byte (G2). So no grupo, e so com dois pets presentes: sozinho, nada e guardado (nem rastro, nem som).
# Os numeros do mundo sao os da ConfigOlfato e da ConfigOuvido (acima, "para a config ser uma so"): a ConfigSentidos as carrega, e o
# `ligada` delas e o do orgao do corpo, independente desta chave. Ligada, o mundo:
# - guarda o rastro de cada pet (uma marca por decisao, na posicao da decisao; ate `olfato.max_marcas`, as mais antigas saem; a marca vale
#   `olfato.cheiro_marca` x (T - idade) // T e some na idade T = `olfato.idade_marca`) e soma, por outro pet, o cheiro proprio (na posicao
#   atual, `olfato.cheiro_pet`) e as marcas dele, pela mesma conta inteira do cheiro da comida (A x (R - d) // R com d < R, R =
#   `olfato.raio_celulas`), num canal separado do da comida (OA-1: o campo calculado);
# - emite os sons das acoes (`comendo`, `bola`, `chamado`, `emburrado`) na posicao do pet, em linha reta (OA-3), ouvidos a d < R_som =
#   `ouvido.raio_som_celulas` com a intensidade `ouvido.som` x (R_som - d) // R_som;
# - da a direcao em 8 pronta (OA-2: pre-processamento do mundo) e a intensidade nas duas posicoes de amostra (as narinas e os ouvidos, a
#   +-afastamento de lado pela direcao do ultimo passo), que o orgao do corpo le (DP-13 e DP-14).


@dataclass(frozen=True)
class ConfigSentidos:
    ligada: bool = False                     # PROPOSTO: a chave (o cheiro proprio, o rastro e o som no grupo)
    olfato: ConfigOlfato = CONFIG_OLFATO     # os numeros do mundo do cheiro do outro e do rastro (o `ligada` dela e o do orgao)
    ouvido: ConfigOuvido = CONFIG_OUVIDO     # os numeros do mundo do som (idem)

    def __post_init__(self) -> None:
        if type(self.ligada) is not bool:
            raise TypeError(f"ConfigSentidos.ligada e bool: {self.ligada!r}")
        if not isinstance(self.olfato, ConfigOlfato) or not isinstance(self.ouvido, ConfigOuvido):
            raise TypeError("ConfigSentidos.olfato e .ouvido sao a ConfigOlfato e a ConfigOuvido")


CONFIG_SENTIDOS = ConfigSentidos()
CONFIG_SENTIDOS_LIGADA = ConfigSentidos(ligada=True)


# =====================================================================
# V2, o Paladar, o lado do mundo (docs/futuro/paladar.md, secoes 3.1, 4 e 6, etapa 1; PL-1 a PL-9 pela recomendacao, 2026-10-13).
# Desligado por padrao: a vida de hoje byte a byte (G2). Ligado (so com o mundo fisico), cada tipo de comida do mapa tem um perfil de gosto,
# um inteiro em [0, C] por qualidade (PL-3: doce, azedo, amargo, salgado; nomes do estimulo, nao da sensacao). O mundo nao interpreta o
# perfil: ele so vai, com o consumo, ao registro do consumo e ao `ocorrido["comeu"]` (o `comer` e o "achou e comeu"), e o corpo (o orgao do
# Paladar, etapa 2, do B) o le de la e, na fruta na mao, dos `perfis`. O gosto nao se ve nem se cheira; a podre nao tem perfil. A nutricao,
# o cheiro, as arvores e o efeito de cada fruta no humor nao mudam. As tres frutas sao a mesma forma girada (nenhuma e a melhor no mundo)
# e a racao tem o gosto basico, numa qualidade so dela, fraca. Os numeros sao PROPOSTOS, SEM FONTE.
QUALIDADES_PALADAR = ("doce", "azedo", "amargo", "salgado")


def _perfis_paladar() -> dict:
    c = CONFIG_CORPO.escala
    q1, q3 = c // 4, 3 * c // 4
    return {"a": {"doce": q3, "azedo": q1, "amargo": 0, "salgado": 0},
            "b": {"doce": 0, "azedo": q3, "amargo": q1, "salgado": 0},
            "c": {"doce": q1, "azedo": 0, "amargo": q3, "salgado": 0},
            "racao": {"doce": 0, "azedo": 0, "amargo": 0, "salgado": q1}}


@dataclass(frozen=True)
class ConfigPaladar:
    ligada: bool = False                     # PROPOSTO: a chave (os perfis no consumo)
    perfis: dict = field(default_factory=_perfis_paladar)   # PROPOSTO, SEM FONTE: {tipo: {qualidade: inteiro em [0, C]}}

    def __post_init__(self) -> None:
        if type(self.ligada) is not bool:
            raise TypeError(f"ConfigPaladar.ligada e bool: {self.ligada!r}")
        if not isinstance(self.perfis, dict) or set(self.perfis) != {"racao", "a", "b", "c"}:
            raise ValueError(f"ConfigPaladar.perfis tem um perfil por tipo de comida (racao, a, b, c): {self.perfis!r}")
        c = CONFIG_CORPO.escala
        for tipo, perfil in self.perfis.items():
            if not isinstance(perfil, dict) or set(perfil) != set(QUALIDADES_PALADAR):
                raise ValueError(f"ConfigPaladar.perfis[{tipo!r}] tem as qualidades {QUALIDADES_PALADAR}: {perfil!r}")
            for q, v in perfil.items():
                if type(v) is not int or not 0 <= v <= c:
                    raise ValueError(f"ConfigPaladar.perfis[{tipo!r}][{q!r}] fora de inteiros em [0, C = {c}]: {v!r}")


CONFIG_PALADAR = ConfigPaladar()
CONFIG_PALADAR_LIGADA = ConfigPaladar(ligada=True)


# =====================================================================
# V2, a fruta ao lado da racao (o RP-2 de docs/futuro/paladar.md, decidido pelo Matheus em 2026-10-14; os numeros combinados com o
# adendo 5 do plano do J5, do C). Desligada por padrao: a vida de hoje byte a byte (G2). Ligada (so com o mundo fisico e um pet), o dono
# que deixa a racao no comedouro poe, no mesmo passo e logo depois dela, as frutas maduras ao lado, uma de cada tipo, numa coluna de
# celulas fixa ao lado do comedouro; o tipo de cada celula sai de uma permutacao sorteada uma vez por vida (rng `fruta-ao-lado`), para a
# distancia ao ninho nao se misturar com o gosto. No maximo `teto_por_tipo` de cada tipo ao lado (maduras) no chao: o dono so repoe a que
# foi comida, apodreceu ou sumiu. Fora do orcamento e sem contato: o gesto e o mesmo da racao, entao o cuidado nao muda; so o mundo
# ganha as frutas. Os numeros sao PROPOSTOS, SEM FONTE.
@dataclass(frozen=True)
class ConfigFrutaAoLado:
    ligada: bool = False                     # PROPOSTO: a chave
    tipos: tuple = ("a", "b", "c")           # PROPOSTO: as frutas postas ao lado (as tres)
    coluna: int = 1                          # PROPOSTO: a coluna de celulas, relativa ao comedouro (a de fora da casa, longe do ninho)
    linhas: tuple = (-1, 0, 1)               # PROPOSTO: as linhas, relativas ao comedouro, uma por tipo da permutacao
    teto_por_tipo: int = 1                   # PROPOSTO: as maduras ao lado de cada tipo no chao, no maximo

    def __post_init__(self) -> None:
        if type(self.ligada) is not bool:
            raise TypeError(f"ConfigFrutaAoLado.ligada e bool: {self.ligada!r}")
        if not isinstance(self.tipos, tuple) or not self.tipos or len(set(self.tipos)) != len(self.tipos) \
                or not set(self.tipos) <= {"a", "b", "c"}:
            raise ValueError(f"ConfigFrutaAoLado.tipos: frutas distintas entre a, b e c: {self.tipos!r}")
        if not isinstance(self.linhas, tuple) or len(self.linhas) != len(self.tipos) or len(set(self.linhas)) != len(self.linhas) \
                or any(type(v) is not int for v in self.linhas):
            raise ValueError(f"ConfigFrutaAoLado.linhas: uma linha inteira distinta por tipo: {self.linhas!r}")
        if type(self.coluna) is not int:
            raise ValueError(f"ConfigFrutaAoLado.coluna e inteira: {self.coluna!r}")
        if type(self.teto_por_tipo) is not int or self.teto_por_tipo < 1:
            raise ValueError(f"ConfigFrutaAoLado.teto_por_tipo e inteiro >= 1: {self.teto_por_tipo!r}")


CONFIG_FRUTA_AO_LADO = ConfigFrutaAoLado()
CONFIG_FRUTA_AO_LADO_LIGADA = ConfigFrutaAoLado(ligada=True)


# V3-3/V3-4, a competicao entre as regras urgentes (docs/TAREFA_V2_V3_COMPETICAO.md, secao 3; CR-1 a CR-7 decididas pelo Matheus em
# 2026-10-21). Uma config propria, como a do banheiro, para a ConfigLobos (e o gabarito da web, que a guarda inteira) nao mudar. O status
# de cada campo esta em policies/lobos.PARAMETROS_COMPETICAO.
@dataclass(frozen=True)
class ConfigCompeticao:
    """ligada            as regras urgentes que valem disputam um sorteio comum (o `sono_exaustao` fica forcado; o tempo livre so sem
                       urgente; cada acao vem da regra mais urgente que a propoe, CR-3). Desligada: a decisao de hoje, byte a byte
    kappa_instinto     o prior forte (CR-1): o peso efetivo das propostas da regra do instinto (a primeira que vale) vezes kappa. Com uma
                       regra so, o kappa cancela no sorteio proporcional, e a decisao e a de hoje"""

    ligada: bool = False
    kappa_instinto: int = 16

    def __post_init__(self) -> None:
        if type(self.ligada) is not bool:
            raise TypeError(f"ConfigCompeticao.ligada e bool: {self.ligada!r}")
        if type(self.kappa_instinto) is not int or self.kappa_instinto < 1:
            raise ValueError(f"ConfigCompeticao.kappa_instinto e inteiro >= 1: {self.kappa_instinto!r}")


CONFIG_COMPETICAO = ConfigCompeticao()
CONFIG_COMPETICAO_LIGADA = ConfigCompeticao(ligada=True)


# =====================================================================
# V2, a P4 (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 3.1; P4-1, P4-2 e P4-4 decididas pelo Matheus em 2026-10-21): o contrato
# sensorio-motor do POC (web/app/poc/mundo3d/, docs/futuro/mundo_3d.md, secao 4) no mundo do motor, so com o mundo fisico e um pet.
# Tres chaves, todas desligadas por padrao (desligadas, a vida de hoje byte a byte; o G2 contra tests/gabaritos/p4_vidas_de_hoje.json):
#   - `sensores`: a visao vira um cone em torno da orientacao do pet, com a oclusao pelos troncos (opacos, sem colisao: P4-4); os `vistos`
#     e os `troncos` da PercepcaoMundo de hoje so trazem o que passa (o adaptador da P4-2: o cerebro nao ganha entrada). Os bigodes, o
#     contato e o resultado percebido vao ao `ocorrido` e ao registro da decisao;
#   - `controlador`: o andar de uma decisao sai do controlador (o A* inteiro na grade de celulas, o bloqueio e o deslize), tick a tick, nos
#     ticks da decisao, no lugar do `passo_ate` em linha reta;
#   - `paredes` (W-4): as paredes na borda do mapa, solidas e opacas. Fica desligada no plano da P4.
# Os numeros sao os do POC (web/app/poc/mundo3d/config.ts), todos PROPOSTOS e SEM FONTE; o `lado_tronco` e novo (o POC nao tem arvores).
@dataclass(frozen=True)
class ConfigContrato:
    sensores: bool = False                   # PROPOSTO: a chave dos sensores (o cone, a oclusao, os bigodes, o contato)
    controlador: bool = False                # PROPOSTO: a chave do controlador (o A*, o bloqueio, o deslize)
    paredes: bool = False                    # PROPOSTO (W-4): as paredes na borda do mapa; desligada no plano da P4 (P4-4)
    cos_meio_cone: int = 512                 # PROPOSTO, SEM FONTE (o COS_MEIO_CONE do POC): cos(60 graus) x 1024, o cone de 120 graus
    raio_bigode: int = 32                    # PROPOSTO, SEM FONTE (o RAIO_BIGODE do POC): 2 celulas de 16 subunidades
    r_pet: int = 6                           # PROPOSTO, SEM FONTE (o R_PET do POC): o circulo do pet no chao
    ticks_bloqueado: int = 3                 # PROPOSTO, SEM FONTE (o TICKS_BLOQUEADO do POC): ticks sem sair do lugar ate desistir
    lado_tronco: int = 8                     # PROPOSTO, SEM FONTE: o lado do quadrado opaco do tronco, centrado na arvore (meia celula)
    espessura_parede: int = 8                # PROPOSTO, SEM FONTE (o ESPESSURA_PAREDE do POC)

    @property
    def ligada(self) -> bool:
        return self.sensores or self.controlador or self.paredes

    def __post_init__(self) -> None:
        for nome in ("sensores", "controlador", "paredes"):
            if type(getattr(self, nome)) is not bool:
                raise TypeError(f"ConfigContrato.{nome} e bool: {getattr(self, nome)!r}")
        for nome in ("cos_meio_cone", "raio_bigode", "r_pet", "ticks_bloqueado", "lado_tronco", "espessura_parede"):
            v = getattr(self, nome)
            if type(v) is not int or v < 0:
                raise ValueError(f"ConfigContrato.{nome} e inteiro >= 0: {v!r}")
        if not 0 < self.cos_meio_cone <= 1024:
            raise ValueError(f"ConfigContrato.cos_meio_cone em (0, 1024]: {self.cos_meio_cone!r}")
        if self.r_pet == 0 or self.ticks_bloqueado == 0 or self.lado_tronco == 0:
            raise ValueError("ConfigContrato: r_pet, ticks_bloqueado e lado_tronco positivos")


CONFIG_CONTRATO = ConfigContrato()
CONFIG_CONTRATO_LIGADO = ConfigContrato(sensores=True, controlador=True)


# =====================================================================
# V2, o DigiBrain modular (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 11; docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, etapa 0; a direcao de
# 2026-10-24, as DM-1 a DM-9 e as PE "antes" DECIDIDAS em 2026-10-25). O cerebro modular e o pacote digilab/digibrain/ (na etapa 0, so o
# esqueleto: o M-ADAPT e os modulos sem equacao). Desligada por padrao: na etapa 0 nada no motor, na bancada nem no jogo le esta chave, e a
# vida de hoje sai byte a byte (o G2 contra tests/gabaritos/digibrain_vidas_de_hoje.json, com os candidatos de cada sub-decisao do mundo).
# Ligada, o pet usa o cerebro modular (a v13, DM-5). As subchaves sao as pecas que a avaliacao desliga (a ablacao, secao 11) e so valem com
# a chave ligada:
#   - `modula_g_apr`: a excitacao do M-AFETO modula o ganho da aprendizagem (PE-4); desligada no primeiro braco (g_apr = g0 constante);
#   - `p2`: o habito hebbiano do M-PLAST alem do P1 (PE-2);
#   - `m_mem`: a memoria episodica minima, os episodios de alimentacao (DM-3; a secao 4.6);
#   - `persistencia`: a persistencia da intencao no M-ESTADO (a secao 4.4).
# A etapa 1a (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secao 2) pede mais duas, PROPOSTAS:
#   - `p1`: o modelo do desfecho do M-PLAST (o braco M0, o inato sozinho, o desliga);
#   - `controle_g_apr`: os controles do V3 (docs/futuro/digibrain_v3_e0.md, secao 4.3) para o `g_apr`:
#       "nenhum"       o `g_apr` da excitacao da propria vida, com `modula_g_apr` (o M4); g0 sem ela (M0 a M3);
#       "embaralhado"  a excitacao de outra vida, a serie E da vida doadora decisao a decisao, com `modula_g_apr` (o M4-emb; a serie vem
#                      ao `DigiBrain` como dado, `serie_e_doadora`);
#       "constante"    o `g_apr` fixo em `g_apr_constante`, sem `modula_g_apr` (o M4-con: a media do `g_apr` das vidas M4 do piloto).
# Com uma subchave desligada, o termo do modulo e 0 em toda decisao (o DigiBrain levanta erro se nao for).
CONTROLES_G_APR = ("nenhum", "embaralhado", "constante")


@dataclass(frozen=True)
class ConfigDigibrain:
    ligada: bool = False                     # PROPOSTO: a chave do cerebro modular (a v13, DM-5)
    modula_g_apr: bool = False               # PROPOSTO (PE-4): desligada no primeiro braco, com os controles embaralhado e constante do V3
    p2: bool = True                          # PROPOSTO (PE-2): o P2 atras da subchave, com a ablacao
    m_mem: bool = True                       # PROPOSTO (DM-3): o M-MEM minimo
    persistencia: bool = True                # PROPOSTO (secao 4.4): a persistencia da intencao
    p1: bool = True                          # PROPOSTO (etapa 1a; plano, secao 2): o P1, que o braco M0 desliga
    controle_g_apr: str = "nenhum"           # PROPOSTO (etapa 1a; plano, secao 2): o controle do V3 do g_apr (CONTROLES_G_APR)
    g_apr_constante: int = 0                 # PROPOSTO (plano, secao 2): o g_apr do M4-con, na escala S; so com o controle "constante"

    def __post_init__(self) -> None:
        for nome in ("ligada", "modula_g_apr", "p2", "m_mem", "persistencia", "p1"):
            if type(getattr(self, nome)) is not bool:
                raise TypeError(f"ConfigDigibrain.{nome} e bool: {getattr(self, nome)!r}")
        if self.controle_g_apr not in CONTROLES_G_APR:
            raise ValueError(f"ConfigDigibrain.controle_g_apr: so {CONTROLES_G_APR}, nao {self.controle_g_apr!r}")
        if type(self.g_apr_constante) is not int:
            raise TypeError(f"ConfigDigibrain.g_apr_constante e int: {self.g_apr_constante!r}")
        if self.controle_g_apr == "embaralhado" and not self.modula_g_apr:
            raise ValueError("o controle embaralhado e a excitacao de outra vida modulando o g_apr: exige modula_g_apr")
        if self.controle_g_apr == "constante" and (self.modula_g_apr or self.g_apr_constante <= 0):
            raise ValueError("o controle constante e o g_apr fixo, sem a excitacao: modula_g_apr desligada e g_apr_constante > 0")
        if self.controle_g_apr != "constante" and self.g_apr_constante != 0:
            raise ValueError("g_apr_constante so com o controle constante")


CONFIG_DIGIBRAIN = ConfigDigibrain()
CONFIG_DIGIBRAIN_LIGADA = ConfigDigibrain(ligada=True)


# Os valores de partida do DigiBrain modular (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2 a 7; o registro `ParametrosInatos` do M-GEN,
# secao 4.9): todos postos a mao na etapa 1a, PROPOSTOS e SEM FONTE salvo onde a linha diz; a calibracao (plano, secao 6.1) so muda as
# magnitudes (os sinais da tabela da secao 4.5 ficam). Todo valor e um inteiro na escala S = 1024 (o v inteiro representa v/S), salvo as
# constantes de tempo (em ticks), as distancias (em subunidades do mundo) e as contagens. O genoma futuro escreve este registro; o
# aprendido nunca entra nele (EG-5).
#
# As caracteristicas de contexto z (secao 2.1, ~20; a ordem e a das linhas de W0 e de H): o vies, as urgencias dos onze receptores do
# prototipo (secao 6), o contexto do M-SENS, as conjuncoes, duas conjuncoes com a urgencia (a fome sem comida, para chamar e explorar;
# o tempo sem cuidado com o humor baixo, para emburrar: a tabela da secao 4.5), e o estado (F do M-ESTADO, V e E do M-AFETO).
RECEPTORES_DIGIBRAIN = ("fome", "higiene", "energia", "humor", "saude", "tedio", "curiosidade", "solidao", "estresse", "dor", "susto")
CARACTERISTICAS_DIGIBRAIN = (("vies",) + tuple(f"u_{r}" for r in RECEPTORES_DIGIBRAIN)
                             + ("noite", "dormindo", "sem_cuidado", "comida_vista", "sem_comida", "bola_vista", "fome_sem_comida",
                                "cuidado_humor", "F", "V", "E"))
# os tipos de alvo das unidades (secao 4.5): as classes do objeto visto e os alvos sem objeto (o cheiro, o vagar, o lugar lembrado)
TIPOS_ALVO_DIGIBRAIN = ("racao", "a", "b", "c", "podre", "bola", "cheiro", "vagar", "ponto")
COMPORTAMENTOS_DIGIBRAIN = ("ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar")   # a ordem de ACOES_PET_HOJE
_S = 1024


def _linha(**w: int) -> tuple:
    """uma linha de W0: (caracteristica, peso) so dos pesos nao nulos, na ordem de CARACTERISTICAS_DIGIBRAIN"""
    fora = set(w) - set(CARACTERISTICAS_DIGIBRAIN)
    if fora:
        raise KeyError(f"caracteristicas desconhecidas: {sorted(fora)}")
    return tuple((c, w[c]) for c in CARACTERISTICAS_DIGIBRAIN if c in w)


@dataclass(frozen=True)
class ConfigDigibrainInatos:
    escala: int = _S                          # DECIDIDO (PE-12): S = 1024, o do A (ConfigLobos.bits_ponto_fixo = 10)
    a_max: int = 4 * _S                       # PROPOSTO (secao 1): o teto da ativacao, phi(v) = clamp(v, 0, A_max)
    # as constantes de tempo, em ticks (secao 1: k = div_arred(S x Delta, tau), com tau >= Delta = 15)
    tau_hab: int = 120                        # PROPOSTO, SEM FONTE: a habituacao por classe (M-SENS, PE-11)
    tau_v: int = 240                          # PROPOSTO, SEM FONTE: a valencia (M-AFETO)
    tau_e: int = 120                          # PROPOSTO, SEM FONTE: a excitacao (M-AFETO)
    tau_c: int = 30                           # PROPOSTO, SEM FONTE: o compromisso C (M-ESTADO, PE-6); calibracao, rodada 2: 60 -> 30
    tau_f_sobe: int = 60                      # PROPOSTO, SEM FONTE: a frustracao F sobe no fim sem a meta (M-ESTADO)
    tau_f_desce: int = 480                    # PROPOSTO, SEM FONTE: a frustracao F decai a cada decisao (M-ESTADO)
    # M-SENS
    escala_cuidado: int = 480                 # PROPOSTO: o mesmo corte do A (ConfigLobos.escala_ticks_desde_cuidado = 480)
    # M-AFETO: a urgencia u_r = clamp(mul(a_r, falta) + mul(b_r, max(0, falta - lambda_r)), 0, S), a mesma curva nos onze receptores
    urgencia_a: int = _S // 2                 # PROPOSTO, SEM FONTE
    urgencia_b: int = 3 * _S // 2             # PROPOSTO, SEM FONTE
    urgencia_lambda: int = _S // 2            # PROPOSTO, SEM FONTE
    ganho_r: int = 4                          # PROPOSTO: o ganho do sinal_corpo, o do A (ConfigConsequencia.ganho = 4, o do N3)
    r_norm: int = 2                           # PROPOSTO, SEM FONTE: r_n = clamp(div_arred(r, R_n), -S, S)
    fora_do_r: tuple = ("susto",)             # PROPOSTO: o susto fica fora do r, como no A (lobos.DRIVES_NOVOS_SINAL)
    g0: int = _S                              # PROPOSTO, SEM FONTE: o g_apr sem modulacao (com g_apr = S, o P1 e a conta do ModeloMundo)
    beta_e: int = _S                          # PROPOSTO, SEM FONTE: g_apr = clamp(g0 + mul(beta_E, E), g_min, g_max)
    g_min: int = _S // 2                      # PROPOSTO, SEM FONTE
    g_max: int = 2 * _S                       # PROPOSTO, SEM FONTE
    e0: int = _S // 2                         # PROPOSTO, SEM FONTE: g_exp = clamp(e0 + mul(beta_T, tedio) - mul(beta_U, max u), 0, e_max)
    beta_t: int = _S // 2                     # PROPOSTO, SEM FONTE
    beta_u: int = _S // 2                     # PROPOSTO, SEM FONTE
    e_max: int = _S                           # PROPOSTO, SEM FONTE
    # M-IMPULSO: os pesos inatos (os sinais da tabela da secao 4.5; as magnitudes PROPOSTAS, SEM FONTE), uma linha por comportamento
    w0: tuple = (
        ("ocioso", _linha(vies=_S // 8, u_fome=-_S // 4, u_energia=-_S // 4, u_higiene=-_S // 4, u_tedio=-_S // 4)),
        ("dormir", _linha(vies=-_S // 2, u_energia=3 * _S, noite=_S // 2, dormindo=_S // 2,
                          u_fome=-_S // 2)),                                      # rodada 2: u_energia 2S -> 3S
        ("comer", _linha(vies=-_S, u_fome=2 * _S)),
        ("brincar", _linha(vies=-_S // 4, bola_vista=_S, u_tedio=_S // 2, u_humor=_S // 2, u_fome=-_S // 2, u_energia=-_S // 2)),
        ("chamar_atencao", _linha(vies=-_S // 2, fome_sem_comida=2 * _S, u_higiene=_S, sem_cuidado=_S // 4, comida_vista=-_S,
                                  u_solidao=_S // 2, u_estresse=_S // 4)),
        ("explorar", _linha(vies=_S // 8, u_tedio=_S, u_curiosidade=_S, F=_S // 2, fome_sem_comida=_S // 2,
                            u_energia=-2 * _S)),                                  # rodada 2: u_energia -S -> -2S
        ("emburrar", _linha(vies=-_S // 2, cuidado_humor=2 * _S)),
    )
    w0_prox: tuple = (("comer", _S // 2), ("brincar", _S // 4))       # PROPOSTO, SEM FONTE: aproximar-se do que esta perto
    w0_nov: tuple = (("brincar", _S // 8),)                           # PROPOSTO, SEM FONTE: o novo atrai na bola (pelo sinal)
    # o termo inato do tipo do alvo (secao 4.5: comer + comida boa, - podre), somado como uma constante
    w0_tipo: tuple = (("comer", (("racao", _S // 4), ("a", _S // 4), ("b", _S // 4), ("c", _S // 4), ("podre", -2 * _S))),)
    # M-ARB
    epsilon: int = _S // 8                    # PROPOSTO, SEM FONTE: w = a + mul(g_exp, epsilon), so nas unidades com a > 0
    lambda_sono: int = _S // 4                # PROPOSTO: o reflexo do sono, a leitura da energia abaixo de S/4 (o 0,25 do sono_exaustao)
    # M-PLAST
    eta_d: int = _S // 4                      # PROPOSTO: o passo do P1, o passo_desfecho do ModeloMundo (S/4, PP-6)
    eta_h: int = _S // 128                    # PROPOSTO, SEM FONTE: o passo do P2; calibracao, rodada 2: S/16 -> S/128
    h_max: int = _S // 2                      # PROPOSTO, SEM FONTE: o corte do habito, |H| <= H_max (PE-10: sem decaimento)
    c_g: int = _S                             # PROPOSTO, SEM FONTE: G = clamp(div_arred(c_G x valor_previsto, S_V), 0, G_max) x prox / S
    s_v: int = _S                             # PROPOSTO, SEM FONTE
    g_max_incentivo: int = _S                 # PROPOSTO, SEM FONTE
    # M-ESTADO
    w_pers: int = 2 * _S                      # PROPOSTO, SEM FONTE (PE-6): h = mul(w_pers, C); calibracao, rodada 2: S/2 -> 2S
    n_desiste: int = 3                        # PROPOSTO (PE-6, a regra do alcance): o raio da visao (96) pelo alcance (60), 2 decisoes, mais 1
    # M-MEM
    n_ep: int = 16                            # PROPOSTO, SEM FONTE (PE-16)
    lambda_busca: int = _S // 4               # PROPOSTO, SEM FONTE: a pista, a urgencia da fome acima deste limiar
    d_max: int = 1024                         # PROPOSTO, SEM FONTE: a distancia (subunidades) em que o lugar lembrado deixa de atrair
    w_mem: int = _S                           # PROPOSTO, SEM FONTE: M = mul(w_mem, valor)

    def __post_init__(self) -> None:
        for f in fields(self):
            if f.name in ("w0", "w0_prox", "w0_nov", "w0_tipo", "fora_do_r"):
                continue
            if type(getattr(self, f.name)) is not int:
                raise TypeError(f"ConfigDigibrainInatos.{f.name} e inteiro: {getattr(self, f.name)!r}")
        if self.escala != _S:
            raise ValueError(f"o DigiBrain modular usa S = {_S} (PE-12)")
        if tuple(b for b, _ in self.w0) != COMPORTAMENTOS_DIGIBRAIN:
            raise ValueError(f"W0: uma linha por comportamento, na ordem de ACOES_PET_HOJE: {[b for b, _ in self.w0]}")
        for b, linha in self.w0:
            for c, w in linha:
                if c not in CARACTERISTICAS_DIGIBRAIN or type(w) is not int:
                    raise ValueError(f"W0[{b}]: ({c!r}, {w!r})")
        for tabela in (self.w0_prox, self.w0_nov):
            for b, w in tabela:
                if b not in COMPORTAMENTOS_DIGIBRAIN or type(w) is not int:
                    raise ValueError(f"W0_prox ou W0_nov: ({b!r}, {w!r})")
        for b, tipos in self.w0_tipo:
            if b not in COMPORTAMENTOS_DIGIBRAIN:
                raise ValueError(f"W0_tipo: comportamento {b!r}")
            for t, w in tipos:
                if t not in TIPOS_ALVO_DIGIBRAIN or type(w) is not int:
                    raise ValueError(f"W0_tipo[{b}]: ({t!r}, {w!r})")
        if any(r not in RECEPTORES_DIGIBRAIN for r in self.fora_do_r):
            raise ValueError(f"fora_do_r: {self.fora_do_r}")
        for tau in (self.tau_hab, self.tau_v, self.tau_e, self.tau_c, self.tau_f_sobe, self.tau_f_desce):
            if tau < 15:
                raise ValueError(f"constante de tempo abaixo do passo do cerebro (15 ticks): {tau}")
        if not 0 < self.g_min <= self.g0 <= self.g_max or self.r_norm <= 0 or self.s_v <= 0 or self.n_ep <= 0 or self.n_desiste <= 0 \
                or self.escala_cuidado <= 0 or self.d_max <= 0 or self.h_max <= 0:
            raise ValueError("ConfigDigibrainInatos: g_min <= g0 <= g_max; r_norm, s_v, n_ep, n_desiste, escala_cuidado, d_max e h_max "
                             "positivos")


CONFIG_DIGIBRAIN_INATOS = ConfigDigibrainInatos()
# o status de cada campo (conferido por teste contra os campos da dataclass): tudo PROPOSTO, salvo a escala (PE-12)
PARAMETROS_DIGIBRAIN_INATOS: dict[str, tuple[str, str]] = {
    f.name: (("DECIDIDO", "PE-12 (2026-10-25): S = 1024, o do A") if f.name == "escala" else
             ("PROPOSTO", "docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2 a 7; valor de partida a mao (etapa 1a), SEM FONTE salvo o que o "
                          "comentario do campo cita"))
    for f in fields(ConfigDigibrainInatos)}
# a versao do pet do cerebro modular (DM-5, DECIDIDA em 2026-10-25): a v13, so com a ConfigDigibrain ligada. Os saves v1 a v12, as
# assinaturas e os gabaritos nao mudam; no jogo (web/app/), a v13 entra na etapa 1b
VERSAO_PET_DIGIBRAIN = 13
