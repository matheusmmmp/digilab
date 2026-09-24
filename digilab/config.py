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
