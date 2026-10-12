"""V2, BANCADA (docs/TAREFA_V2_BANCADA.md): um orquestrador unico para os bracos da pergunta maior.

    python experiments/bancada_v2.py --config experiments/configs/bancada/fumaca.json --saida <pasta>   # fumaca, NAO canonica

A pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6) compara fontes de plasticidade no MESMO aprendiz (validacao
V1 do docs/ROADMAP_V2.md: a L1 separa de onde vem o sinal da regra de atualizacao). A bancada fixa isso em codigo:

  vida = (genoma, mundo, dono, braco, semente)
    genoma   None = sem genoma (temperamento neutro); um inteiro g = temperamento sorteado de g (a semente do genoma separada
             da do ambiente, como no E1 da linhagem). No mundo padrao: MotorComFeedback sem genoma (como a L1) e
             MotorPersonalidade com genoma; nos mundos da bola, sempre o MotorAmbiente da A1 (obediencia desligada).
    mundo    padrao   o motor de sempre, sem objeto nenhum.
             bola     a bola da A1 (MotorAmbiente, ConfigBola ligada) com as decisoes B1 e B2 de 2026-10-01: os donos sao os
                      da v1 (o aleatorio NAO sorteia por_bola) e a bola entra por uma regra do mundo FORA do orcamento
                      (RegraBola: a regra dos coerentes do DonoComBola sem o limite do passo; o relapso so nas visitas, B3).
             bola_a1  a bola exatamente como a A1 rodou (DonoComBola: o aleatorio sorteia por_bola e a bola gasta orcamento);
                      so para reproduzir a A1 (gate), nao para runs novas.
             casado_frutas, descasado, mutavel   os mundos das frutas (N4, MotorFrutas; docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md,
                      secao 2, E1): as mesmas ofertas nos tres, por um calendario que sai da semente (CalendarioFrutas: horarios
                      fixos, a rotacao do N4 com o inicio derivado da semente, sem olhar o estado do pet nem o braco), fora do
                      orcamento e fora do sorteio do dono aleatorio (B1, B2). Muda so o efeito no humor (F6), pelo genoma das frutas:
                      no casado a fruta de maior preferencia inata faz bem e a de menor faz mal; no descasado, o contrario; a do
                      meio e neutra nos dois (efeitos_da_condicao: o descasado e o casado com o sinal trocado). O mutavel comeca
                      casado e troca para o descasado na metade da vida (tick_troca); a troca fica no registro derivado do motor
                      (MotorFrutasMundo.troca) e o replay a refaz.
             Cada mundo realiza uma CONDICAO da pergunta maior (CONDICOES): casado (padrao, bola, bola_a1, casado_frutas),
             descasado e mutavel.
    dono     um dono sintetico; a rng do dono deriva de (semente, nome do dono), igual em todos os bracos e mundos.
    braco    P0..P3: o MESMO cerebro (PoliticaLobos, mesmo prior, mesma ConfigLobos); so a FONTE do sinal muda.
    semente  a do motor: rng de ambiente = semente, rng de politica = semente + 1_000_003 (engine.py, intocado).

  fontes (o campo `fonte` do braco):
    nenhuma       P0   so a predisposicao herdada: o aprendiz com o aprendizado DESLIGADO (o prior fixo). Nada do dono chega
                       a ele. Entregar "sinal nenhum" a um aprendiz ligado nao e P0: o credito do chamado expira por dentro
                       (Aprendiz._expirar) e vira sinal negativo do dono ausente.
    consequencia  P1   (N3, docs/PLANO_ANALISE_V2_N3.md) a consequencia da propria acao: em `observar`, o sinal
                       `lobos.sinal_homeostatico` da transicao (reducao do deficit de fome, higiene e energia, janela
                       imediata) entra na mesma regra de atualizacao da L1 (`Aprendiz.observar_consequencia`). Nada do
                       dono chega ao aprendiz (nem o credito do chamado).
    informacao    P2   (certa), P2e (errada) e P2a (acoplada): o aprendiz do P1 (a consequencia da propria acao, com a E2, e o
                       UNICO reforco) num mundo das frutas em que um informante diz se cada fruta faz bem ou mal
                       (docs/PLANO_ANALISE_V2_N5.md). A informacao entra pela percepcao (o MotorFrutas injeta `info_frutas`), nunca
                       pelo `receber_acao_dono`: nada do dono chega ao aprendiz. P2 = DonoInformante `certo` logo depois de cada
                       oferta do CalendarioFrutas; P2e = `errado`, nos mesmos ticks; P2a = o mesmo multiconjunto (fruta, conteudo
                       verdadeiro) do P2 em ticks sorteados pela rng derivar_semente("informacao-acoplada", semente) (plano,
                       secao 4.2; InformanteAcoplado). Informar e evento do log fora do orcamento, pelo canal do mundo.
    dono          P3   o feedback explicito (COACH): toda acao do dono chega ao aprendiz pelo gancho receber_acao_dono,
                       exatamente como na L1 (a vida e byte a byte a da L1: teste).

  modo acoplado (malha aberta; generaliza log_so_cuidado/vidas_acopladas de run_v2_l1.py): o registro de eventos de uma vida,
  com um filtro (nenhum, sem_sinais, sem_sinais_sem_carinho), e rejogado com o cerebro de outro braco, no MESMO mundo. O motor
  acoplado guarda o log filtrado: o registro dele e o da origem com os eventos retirados, evento a evento. Os eventos do mundo
  (por/tirar a bola; as ofertas de fruta do N4) nunca saem: nenhum filtro pode retira-los (o "so cuidado" da A1, que tirava a
  bola, e outra coisa e fica em run_v2_a1.py).

  cerebros: lobos (o aprendiz, todos os bracos) e instinto (a referencia herdada, so no P0: PoliticaInstintoBola na bola,
  PoliticaInstintoFrutas nas frutas). Desde a BANCADA-N5 os lobos veem o mundo (LOBOS-MUNDO, #141): a bancada passa cfg_bola nos
  mundos da bola e cfg_frutas nos das frutas, e o P0 com lobos e o instinto que ve a bola e as frutas, byte a byte. No mundo padrao,
  nada muda.

  medidas (todas de digilab/metrics.py; nenhuma conta aqui): desempenho no proprio ambiente (tempo fora de privacao e saude
  media, amostrados em cada decisao; humor medio, `privacao_nas_decisoes`; acerto na tarefa do dono, `acerto_na_tarefa`), custo
  da plasticidade (deriva ao prior por dia e tempo ate a metade do caminho, `custo_da_plasticidade`), nos mundos das frutas a
  `taxa_fruta_ruim` por janela (inicio, final, antes e depois da troca, e por dia) e a tabela braco x condicao.

  unidades derivadas (E3 do plano do experimento maior, secao 8.1): de cada semente reservada (base b) saem K unidades,
  semente = derivar_semente("experimento-maior", b, k) e genoma = derivar_semente("experimento-maior-genoma", b, k)
  (unidades_derivadas; o campo "unidades" da config). FAIXAS_RESERVADAS lista as faixas reservadas ou usadas; o teste confere
  que nenhuma unidade cai nelas.

  N6 e N7 (BANCADA-N6-N7; docs/PLANO_ANALISE_V2_N6.md e docs/PLANO_ANALISE_V2_N7.md): o mundo iguais_frutas (condicao "iguais": as
  tres frutas com o efeito neutro, N7-5), os bracos de memoria M0, MR, MT, ME (N6) e os do pedido P0+ped, P1+ped, P3+ped (N7), o
  desarranjo do ME por rng propria (desarranjo_n6, N6-6) e as unidades derivadas com prefixo ("n6", "n7"; o padrao continua
  "experimento-maior"). Desde a BANCADA-LIGA-N6-N7 os bracos rodam: a memoria e o pedido do cerebro (CEREBRO-N6-N7) por cima do ponto,
  o DonoPedinte (N7-MUNDO) pelo canal do mundo, os pedidos e as broncas do pedido fora do orcamento, o "so cuidado" sem eles, e as
  medidas dos dois planos lidas das sondas que o cerebro grava no motivo.

  K4 e canais (BANCADA-K4-CANAIS; decisao do Matheus de 2026-10-05 e K-7 do plano da calibracao conjunta): com "julgamento_fruta" na
  config, o dono dos bracos com fonte dono (o P3) julga cada consumo de fruta pelo efeito real vigente (JulgadorFruta, #170), pela
  regra do mundo, FORA do orcamento (o atencioso decide com o orcamento inteiro); os julgamentos sao elogiar/repreender contados a parte
  (VidaBancada.julgamentos) e saem com o sem_ensino. Os canais (#169) seguem a chave "consequencia" da config, e um braco pode fixa-los
  (Braco.canais): as ablacoes da K-7 sao o P1c (P1 completo: memoria e canais), o P1c-mem (sem memoria, g = 0) e o P1c-can (escalar).

  montagem (BANCADA-MONTAGEM; decisao do Matheus de 2026-10-05, opcao 1; PLANO_CALIBRACAO_CONJUNTA_V2, secao 1): a chave "montagem" da
  config. "simples" (o padrao, e sem a chave) e a bancada de antes, byte a byte. "completa" monta o cerebro A da secao 1 em cada braco,
  pela fonte (MONTAGEM_COMPLETA): o P0 sem nada; P1, P2, P2e, P2a e P3 com a memoria relevante (ganho g da config, so nos mundos das
  frutas); canais ligados nos que aprendem pela consequencia (P1, P2*) e desligados no P3; w0_info da config so nos P2*; w0_pedido da
  config so nos bracos com pedido. O que o braco fixa (a memoria do N6 e das ablacoes, os canais das ablacoes) vence a montagem, entao o
  P1c e o P1 completo e o P1c-mem e o P1c-can sao o P1 completo menos uma peca.

  P2d e P3i (P2D-P3I, parte D; adendo 3, secao 3.3, do plano do experimento maior): o P2d e o P2 com a informacao depois do consumo (o
  JulgadorFruta da parte A com saida="informacao", no primeiro passo do dono depois de cada consumo, no lugar do informante da oferta);
  o P3i e o P3 com o julgamento do K4 saindo como informacao (a mesma saida), e na montagem completa com o w0_info da config. O
  conhecimento e o mesmo do P2 e do K4 (os efeitos reais da bancada, com a troca do mutavel); as informacoes ficam fora do orcamento,
  contam em `informacoes` e saem no sem_ensino; o multiconjunto (fruta, conteudo) vai por vida nas medidas.

  mundo fisico (W-BANCADA-MUNDO, rodada 17; docs/TAREFA_V2_MUNDO_FISICO.md, secao 9, etapa 4; PLANO_ANALISE_V2_MUNDO_FISICO): os mundos
  `fisico` e `fisico_afastado` (o layout afastado da A1.8), no MotorMundo da main, condicao "iguais" (PMF-7: as tres frutas com o efeito
  neutro). O lugar onde o dono solta a racao (comedouro, perto, longe; PMF-4) e um fator da vida (EspecVida.lugar, a chave "lugares" da
  config): a celula e dono x lugar. O dono e o DonoComLugar (o alimentar vira deixar_comida no lugar) e fica so com o cuidado (PMF-3): o
  filtro sem_ensino aplicado ao vivo (CanalSemEnsino: o elogio e a bronca gastam o orcamento do dono como sempre, mas nao chegam ao motor;
  contados em VidaBancada.retirados). O replay e o reproduzir_mundo; as medidas do plano saem de `metrics` (D_FE, privacao, visitas e as
  inclinacoes da A1.8, taxa no abandono, permanencia media). Desde a W-LIGA-MUNDO (a etapa 3 do B na main, #232): o cerebro "instinto"
  no mundo fisico e a PoliticaInstintoMundo; o P0z (o P0 sem explorar, controle da premissa e fonte dos acoplados P0^ac e P1^ac) e o
  instinto do mundo no modo `sem_explorar`, em qualquer cerebro da config (os lobos nao tem o modo); os lobos veem o mundo pela chave dele
  (`PoliticaLobos(..., cfg_mundo=)`, com os pesos w_bola e w_fruta da bancada), e o P0 com lobos e o instinto do mundo byte a byte.

  dominancia de um drive no sinal (W-DOMINANCIA, rodada 18; PLANO_ANALISE_V2_CORPO_DRIVES, adendo 2, A2.2 a A2.5): em cada decisao, a
  contribuicao de cada drive do sinal, c_d = falta_d,antes^2 - falta_d,depois^2 (w_d = 1, D-4), e a parcela p_d = |c_d| / soma|c|
  (metrics.contribuicao_drives e dominancia_decisoes), lidas do replay de medicao (_Registro: a transicao e, na fruta, o estado logo
  depois de comer, como a E2). Nos bracos que aprendem pela consequencia e o sinal deles ("sinal"; com os canais ligados, conferido
  contra os totais por canal do cerebro); nos outros, a mesma conta como sonda ("sonda", o P0 do plano). Por vida no medidas.json
  (`dominancia`) e por braco x condicao x tipo de decisao no dominancia.json, com a leitura da A2.3 (lidera com p_d >= 0,80; domina
  com o IC95 inferior de f_d acima de 0,50), fora do Holm. O braco P1-cw (o peso pela janela recente, A2.4) e o P1 com a chave
  `pesos_janela` da ConfigConsequencia ligada (#236, W-LIGA-PESOS-JANELA); nele o w_d da medida e o peso da janela que o cerebro usou
  na decisao (o motivo `pesos_janela`), e a conferencia com os canais recalcula o sinal com os mesmos pesos.

  corpo (W-BANCADA-CORPO, etapa 8 da TAREFA_V2_CORPO_DRIVES; PLANO_ANALISE_V2_CORPO_DRIVES, secoes 2 a 5 e adendos 1 e 2): o regime do
  corpo e um campo do braco (`Braco.regime`): "hoje" (a chave do corpo desligada), "quimica" (a `ConfigCorpo` da bancada: a quimica dos
  drives de hoje, com a digestao na taxa C e a Vida, sem os drives novos) e "corpo" (a quimica mais `drives_novos` e `gestos`). Com o
  regime, o motor e o `com_corpo(...)` do mundo e o cerebro A recebe `cfg_corpo` (o sinal pelos receptores, `sinal_corpo`). A chave
  "corpo" da config troca os numeros da `ConfigCorpo` (nao as sub-chaves: elas sao do regime). Desde a W-LIGA-GESTOS (a etapa 6 na
  main: o motor e o `DonoComGestos` do A, #245; a quimica e o cerebro do B, #247) rodam todos os bracos do plano: o bloco G-HOJE, o do
  corpo (P0-q, P1-q, P0-c, P1-c), o do tapa, o G (P1-c-tapaX, P1-c-frutas) e o P1-cw (o P1-c com `pesos_janela`). O dono dos bracos com
  gestos e o `DonoComGestos` (o elogio vira carinho; a bronca vira tapa, ou nada no modo sem tapa) e, no P1-c-tapaX, ainda o
  `DonoTapaFruta` (o tapa na fruta X, dentro do orcamento). A bronca do modo sem tapa (o `SemGesto`) gasta o orcamento sem ir ao motor nem
  ao log (os canais com gestos), contada em `VidaBancada.retirados`. O tapa passa pela PoliticaDoBraco em toda fonte que aprende (CD-10)
  e o carinho pelo corpo (`mudanca_no_corpo`, CD-4) nas mesmas fontes; no P0, nada. Os gestos ficam fora do mundo fisico e do `bola_a1`
  (o plano do corpo nao os usa la). O filtro `sem_gestos` do acoplado tira o tapa e o carinho. Nos bracos
  com corpo saem as medidas do plano (secao 5: `BE`/`OC`, o cuidado preservado e, quando houver receptores novos, os drives novos) e a
  dominancia pelos receptores (a conta do cerebro: `lobos.contribuicoes_corpo`, conferida contra o motivo e os canais).

  ponto do aprendiz (BANCADA-EXPERIMENTO; decisao R1 de 2026-10-05, docs/RESULTADO_V2_REVISAO_APRENDIZ.md): o campo "ponto" da config
  escolhe um ponto nomeado de PONTOS_APRENDIZ, e a chave "lobos" troca campos por cima dele. Sem "ponto", o "L1" (o
  CONFIG_LOBOS_APRENDIZ: passo 512, teto 1024), entao as runs antigas nao mudam. O "T3" (teto 16*S = 16384, o resto igual: sem traco)
  e o ponto de partida do N5 e do experimento maior (PONTO_N5_EXPERIMENTO).

Toda vida e rejogada do disco e comparada bit a bit (G1): divergencia levanta erro e para tudo. engine.py e lobos.py nao
mudam. Sementes: so as dos testes (101...505) sem plano; qualquer outra exige o plano de analise registrado (campo "plano").
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import sys
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.ambiente import (DonoComBola, MotorAmbiente, PoliticaInstintoBola, _PoliticaComBola,  # noqa: E402
                              reproduzir_ambiente)
from digilab.config import (CONFIG_BOLA, CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_DONOS, CONFIG_FRUTAS_LIGADA,  # noqa: E402
                            CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,
                            CONFIG_PEDIDO_LIGADA, LAYOUT_MUNDO_AFASTADO, TICKS_POR_DIA, ConfigBola, ConfigConsequencia, ConfigFrutas,
                            ConfigInformacao, ConfigJulgamentoFruta, ConfigLobos, ConfigMundo, ConfigPedido)
from digilab.config import ConfigCorpo  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA, ConfigGrupo  # noqa: E402
from digilab.grupo import Grupo, PetDoGrupo, RegistroGrupo, reproduzir_grupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.corpo import Corpo, div_arred as div_arred_corpo  # noqa: E402
from digilab.gestos import CanalComGestos, DonoComGestos, simular_vida_gestos  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.donos import Visao, criar_dono, cuidados_necessarios, julgar_acao  # noqa: E402
from digilab.events import (ACOES_BOLA, ACOES_FRUTAS, ACOES_PET_HOJE, ACOES_INFORMACAO, ACOES_PEDIDO, FRUTAS, AcaoPet, AcaoUsuario,  # noqa: E402
                            LogDeEventos, fruta_de, informar, oferta_de)
from digilab.evolucao import politica_no_tick  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.instinto_banheiro import PoliticaInstintoBanheiro  # noqa: E402
from digilab.config import CONFIG_BANHEIRO_LIGADA, ConfigBanheiro  # noqa: E402
from digilab.frutas import (DonoInformante, DonoPedinte, JulgadorFruta, MotorFrutas, PoliticaInstintoFrutas,  # noqa: E402
                            _PoliticaComFrutas, genoma_frutas)
from digilab.metrics import (acerto_na_tarefa, custo_da_plasticidade, desempenho_no_ambiente,  # noqa: E402
                             consumos_ate_metade, distribuicoes_de_acao, estados_sonda, jsd_media, multiconjunto_informacoes, privacao_nas_decisoes,
                             resposta_a_bola, tabela_braco_condicao, tabela_braco_condicao_parcial, taxa_fruta_ruim,
                             ZONAS_CONFLITO, deferencia_ao_pedido, dia_cruza_zero, fracao_da_fruta, memoria_nas_subdecisoes,
                             ocupacao_espacos_frutas)
from digilab.metrics import (cuidado_preservado, deficit_fome_energia, inclinacao_permanencia, janela_dias,  # noqa: E402
                             permanencia_media, taxa_no_abandono, visitas_manchas)
from digilab.metrics import contribuicao_drives, dominancia_decisoes, leitura_dominancia  # noqa: E402
from digilab.metrics import drives_novos as medir_drives_novos, tempo_livre_be  # noqa: E402
from digilab.metrics import alivios_ate_criterio, alivios_por_dia, curva_sobrevivencia, dia_do_criterio  # noqa: E402
from digilab.metrics import metabolismo_da_vida, tempo_comer_brincar, vez_no_grupo  # noqa: E402
from digilab.mundo import DonoCarinhoBanheiro  # noqa: E402
from digilab.mundo import (ESTILOS_LUGAR, CanalMundo, DeixarBola, DeixarComida, DonoComLugar, MotorMundo,  # noqa: E402
                           _PoliticaComMundo, centro_da_celula, reproduzir_mundo)
from digilab.obediencia import MotorPersonalidade, _PoliticaObservada  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import desarranjo_n6 as desarranjo_dos_lobos  # noqa: E402
from digilab.policies.lobos import sinal_homeostatico  # noqa: E402
from digilab.policies.lobos import (DRIVES_NOVOS_SINAL, RECEPTOR_DO_INDICE, RECEPTORES_NOVOS, contribuicoes_corpo,  # noqa: E402
                                    sinal_corpo, sinal_corpo_canais)
from digilab.policies.lobos import CANAL_DO_DRIVE, INDICE_HUMOR, arred, sinal_por_canal  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.temperamento import sortear as sortear_temperamento  # noqa: E402
from digilab.treino import (CanalDeInteracao, MotorComFeedback, OrcamentoExcedido, OrcamentoNaoConsumido,  # noqa: E402
                            reproduzir_com_feedback, simular_vida)

ACOES = tuple(a.value for a in ACOES_PET_HOJE)
SINAIS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})
SEMENTES_TESTE = frozenset({101, 202, 303, 404, 505})
# pontos nomeados do aprendiz: campos trocados sobre o CONFIG_LOBOS_APRENDIZ (decisao R1, 2026-10-05). Um ponto novo entra aqui, com a
# fonte; os de antes nao mudam.
PONTOS_APRENDIZ = {
    "L1": {},                                   # passo 512, teto 1024 = 1*S: o ponto calibrado da L1 (o padrao de sempre)
    "T3": {"teto": 16 * 2 ** CONFIG_LOBOS_APRENDIZ.bits_ponto_fixo},   # R1: teto 16*S, sem traco (REVISAO_APRENDIZ, secao 3)
}
PONTO_PADRAO = "L1"                             # sem o campo "ponto": as runs antigas, byte a byte
PONTO_N5_EXPERIMENTO = "T3"                     # o ponto de partida do N5 e do experimento maior (R1)
CEREBROS = ("lobos", "instinto")
INFORMACOES = frozenset(a.value for a in ACOES_INFORMACAO)
PEDIDOS = frozenset(a.value for a in ACOES_PEDIDO)        # N7: "deixe a fruta X" (o pedido do dono, N7-MUNDO)
# corpo (etapa 6): os gestos do dono no registro, o tapa e o carinho (o que o DonoComGestos poe no lugar da bronca e do elogio)
GESTOS = frozenset({AcaoUsuario.TAPA.value, AcaoUsuario.ACARICIAR.value})
SINAIS_DO_DONO = SINAIS | {AcaoUsuario.TAPA.value}       # o que o dono manda direto ao aprendiz: o elogio, a bronca e o tapa
FILTROS = {"nenhum": frozenset(), "sem_sinais": SINAIS,
           "sem_sinais_sem_carinho": SINAIS | {AcaoUsuario.ACARICIAR.value},
           # N5 (plano, secao 4): o "so cuidado" do P2 tira os sinais de ensino E a informacao; as ofertas ficam. N7 (plano, secao 4.2):
           # o "so cuidado" do P3+ped tira tambem os pedidos; as broncas do pedido sao `repreender` e saem com os sinais
           "sem_informacao": INFORMACOES, "sem_ensino": SINAIS | INFORMACOES | PEDIDOS,
           "sem_ensino_sem_carinho": SINAIS | INFORMACOES | PEDIDOS | {AcaoUsuario.ACARICIAR.value},
           # N7: o controle do P0+ped (o P0 no registro dele sem os pedidos; os sinais do dono ficam) e o nome do plano para o so cuidado
           "sem_pedido": PEDIDOS, "sem_ensino_sem_pedido": SINAIS | INFORMACOES | PEDIDOS,
           # corpo (TAREFA_V2_CORPO_DRIVES, secao 14, etapa 8): o acoplado sem os gestos do dono, o tapa e o carinho; o resto fica
           "sem_gestos": GESTOS}
# os eventos do MUNDO no log: acoes do dono que poem coisas no cenario. O acoplado nunca os tira (as ofertas de fruta do N4 entram
# aqui quando existirem). Os filtros so tiram o que o dono ENSINA ou o carinho.
EVENTOS_DO_MUNDO = frozenset(a.value for a in ACOES_BOLA + ACOES_FRUTAS)
# o que entra pelo canal do mundo, fora do orcamento do dono: os eventos do mundo e a informacao do dono (B2; plano do N5, secao 2).
# A informacao NAO e evento do mundo: o "so cuidado" a tira (FILTROS); o mundo (bola, ofertas) nunca sai.
FORA_DO_ORCAMENTO = EVENTOS_DO_MUNDO | INFORMACOES | PEDIDOS     # N7: os pedidos tambem (B2); as broncas do pedido, pela regra
assert not any(f & EVENTOS_DO_MUNDO for f in FILTROS.values()), "um filtro nao pode tirar eventos do mundo"


@dataclass(frozen=True)
class Condicao:
    """Uma condicao da pergunta maior (docs/ARQUITETURA_V2_VALIDACAO.md, secao 6, item 2): a relacao entre o mundo e a
    predisposicao herdada. `precisa` = o que falta (e de qual no) para a condicao existir; vazio quando ja existe."""

    nome: str
    descricao: str
    precisa: str = ""
    no: str = ""


CONDICOES = {
    "casado": Condicao("casado", "o mundo e aquele para o qual o prior foi feito: nada nele contradiz a predisposicao herdada"),
    "descasado": Condicao(
        "descasado", "o mundo contradiz o prior: a fruta preferida de nascenca faz mal (e a menos preferida faz bem)"),
    "mutavel": Condicao(
        "mutavel", "o mundo muda no meio da vida: comeca casado e o efeito das frutas troca na metade (a boa vira ruim e "
        "vice-versa); a troca fica no registro derivado e o replay a refaz"),
    # N7-5 (docs/PLANO_ANALISE_V2_N7.md, secao 4.3): fora da pergunta maior, o mundo da arbitragem
    "iguais": Condicao(
        "iguais", "as tres frutas com o mesmo efeito (neutro no humor) e a mesma nutricao: escolher uma fruta nao tem consequencia "
        "propria, so a da fome (o mundo \"iguais\" do N4 na bancada)"),
}


@dataclass(frozen=True)
class Mundo:
    nome: str
    condicao: str                    # a condicao da pergunta maior que este mundo realiza
    bola: str | None = None          # None: sem bola; "b1b2": a bola das decisoes B1/B2; "a1": a bola como a A1 rodou
    frutas: bool = False             # os mundos das frutas (MotorFrutasMundo); o efeito sai da condicao
    fisico: str | None = None        # o mundo fisico (MotorMundo): o layout, "padrao" ou "afastado" (A1.8)

    @property
    def ambiente(self) -> bool:
        """roda no MotorAmbiente (bola) ou numa subclasse dele (frutas, mundo fisico)"""
        return self.bola is not None or self.frutas or self.fisico is not None


MUNDOS = {
    "padrao": Mundo("padrao", "casado"),
    "bola": Mundo("bola", "casado", "b1b2"),
    "bola_a1": Mundo("bola_a1", "casado", "a1"),
    "casado_frutas": Mundo("casado_frutas", "casado", frutas=True),
    "descasado": Mundo("descasado", "descasado", frutas=True),
    "mutavel": Mundo("mutavel", "mutavel", frutas=True),
    "iguais_frutas": Mundo("iguais_frutas", "iguais", frutas=True),
    # o mundo fisico (PLANO_ANALISE_V2_MUNDO_FISICO, secao 2; PMF-7: o mundo "iguais") e o layout afastado do G-DIST (A1.8)
    "fisico": Mundo("fisico", "iguais", fisico="padrao"),
    "fisico_afastado": Mundo("fisico_afastado", "iguais", fisico="afastado"),
}
LAYOUTS_FISICO = {"padrao": None, "afastado": LAYOUT_MUNDO_AFASTADO}     # None: o layout da ConfigMundo da bancada


def mundo_de(nome: str) -> Mundo:
    if nome in CONDICOES and CONDICOES[nome].precisa:
        c = CONDICOES[nome]
        raise NotImplementedError(f"condicao {nome!r} ({c.descricao}): precisa {c.precisa}")
    if nome not in MUNDOS:
        raise NotImplementedError(f"mundo {nome!r}: so {sorted(MUNDOS)}")
    m = MUNDOS[nome]
    if CONDICOES[m.condicao].precisa:          # pragma: no cover - um mundo registrado so realiza condicao que ja existe
        raise NotImplementedError(m.condicao)
    return m
MEDIDAS_TABELA = ("fracao_fora_de_privacao", "saude_media", "humor_medio", "acerto_total", "deriva_final")
CHAVES_CONFIG = {"descricao", "plano", "bracos", "donos", "sementes", "unidades", "genomas", "mundos", "dias", "orcamento",
                 "sonda", "bootstrap", "acoplados", "consequencia", "lobos", "frutas", "ponto", "julgamento_fruta", "montagem",
                 "lugares", "mundo", "corpo"}
# corpo (W-BANCADA-CORPO): a quimica da pergunta do plano (secao 1: "a quimica de hoje", CD-3): o corpo com a digestao na taxa C e a
# Vida, sem os drives novos. O regime "corpo" liga por cima os drives novos e os gestos (etapa 6). A chave "corpo" da config troca os
# numeros, nunca as sub-chaves
CONFIG_CORPO_QUIMICA = ConfigCorpo(ligada=True, digestao=True, vida=True)
REGIMES_CORPO = ("hoje", "quimica", "corpo")
SUBCHAVES_CORPO = ("ligada", "digestao", "vida", "drives_novos", "gestos", "metabolismo")
GESTOS_DONO = ("sem_tapa", "tapa", "tapa_fruta")
# K4 fora do orcamento (decisao do Matheus, 2026-10-05): a chave liga o motor e a regra do mundo; o julgamento usa elogiar/repreender
CONFIG_JULGAMENTO_FORA = ConfigJulgamentoFruta(ligada=True, no_orcamento=False)
JULGAMENTOS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})


# ------------------------------------------------------------------ as frutas na bancada


def efeitos_da_condicao(genoma, cf: ConfigFrutas, condicao: str) -> dict:
    """O efeito no humor de cada fruta (F6: o ruim no humor, fora de em_privacao). Casado: a de maior preferencia inata faz bem
    (-efeito_humor_ruim) e a de menor faz mal (efeito_humor_ruim); descasado: o mesmo com o sinal trocado; a do meio fica com o
    efeito neutro nos dois. Assim casado e descasado diferem SO no sinal, e os dois tem uma fruta boa e uma ruim."""
    if condicao == "iguais":                       # N7-5: todas com o efeito neutro, como o mundo "iguais" do N4
        return {f: cf.efeito_humor_neutro for f in FRUTAS}
    if cf.efeito_humor_ruim >= 0.0:
        raise ValueError("efeito_humor_ruim precisa ser negativo")
    pref = genoma.preferencia_inata
    maior = genoma.fruta_preferida()
    menor = min(FRUTAS, key=lambda f: (pref[f], FRUTAS.index(f)))
    if maior == menor:
        raise ValueError("preferencias inatas iguais: sem fruta preferida nem rejeitada")
    ruim, bom = cf.efeito_humor_ruim, -cf.efeito_humor_ruim
    if condicao == "casado":
        alto, baixo = bom, ruim
    elif condicao == "descasado":
        alto, baixo = ruim, bom
    else:
        raise ValueError(f"efeitos so de casado, descasado ou iguais, nao {condicao!r}")
    return {f: (alto if f == maior else baixo if f == menor else cf.efeito_humor_neutro) for f in FRUTAS}


class MotorFrutasMundo(MotorFrutas):
    """O MotorFrutas (digilab/frutas.py, que nao muda) com o efeito de cada fruta dado pela CONDICAO do mundo da bancada, no
    lugar do `ConfigFrutas.mundo` do N4. No mutavel o efeito comeca casado e troca para o descasado na primeira decisao em ou
    depois de `tick_troca` (as decisoes caem a cada 15 ticks, entao com tick_troca multiplo de 15 a troca e no tick exato); a
    troca fica em `self.troca` (registro derivado: tick e os efeitos antes e depois) e em cada consumo (o efeito aplicado).
    Nenhuma rng a mais; o replay pelo log refaz tudo."""

    def __init__(self, *a, condicao: str, tick_troca: int | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        if not self.cf.ligada:
            raise ValueError("os mundos das frutas pedem ConfigFrutas.ligada")
        if condicao == "mutavel":
            if tick_troca is None or tick_troca <= 0:
                raise ValueError("o mutavel precisa de tick_troca > 0")
            inicial = "casado"
        elif condicao in ("casado", "descasado", "iguais"):
            if tick_troca is not None:
                raise ValueError(f"so o mutavel troca, nao {condicao!r}")
            inicial = condicao
        else:
            raise ValueError(f"condicao das frutas desconhecida: {condicao!r}")
        self.condicao = condicao
        self.tick_troca = tick_troca
        conds = ("iguais",) if condicao == "iguais" else ("casado", "descasado")
        self._efeitos = {c: efeitos_da_condicao(self.genoma, self.cf, c) for c in conds}
        self.efeito_vigente = inicial
        self.efeito_humor = dict(self._efeitos[inicial])
        self.troca: dict | None = None

    def _frutas_na_proxima_decisao(self) -> float:
        t = self._estado.tick
        if self.condicao == "mutavel" and self.troca is None and t >= self.tick_troca:
            antes = dict(self.efeito_humor)
            self.efeito_vigente = "descasado"
            self.efeito_humor = dict(self._efeitos["descasado"])
            self.troca = {"tick": t, "tick_troca": self.tick_troca, "de": "casado", "para": "descasado",
                          "efeito_antes": antes, "efeito_depois": dict(self.efeito_humor)}
        return super()._frutas_na_proxima_decisao()

    def resumo_mundo(self) -> dict:
        return {"condicao": self.condicao, "tick_troca": self.tick_troca, "efeito_vigente": self.efeito_vigente,
                "efeitos": {c: dict(e) for c, e in self._efeitos.items()}, "troca": self.troca}


class CalendarioFrutas:
    """As ofertas de fruta do experimento maior (plano, secao 2; K5): saem da SEMENTE, nao do estado do pet nem do braco, entao o
    mesmo pet ve as mesmas frutas nos mesmos ticks em qualquer braco e condicao. Nos horarios fixos do N4
    (`ConfigFrutas.horarios_oferta`), todo dia, o proximo conjunto da `rotacao_ofertas`, comecando no indice
    derivar_semente("calendario-frutas", semente) % len(rotacao). Diferente do OfertasFrutas do N4, oferece com o pet dormindo
    tambem (a fruta fica no cenario ate o prazo): olhar o sono faria a oferta depender do estado. Regra do mundo da bancada:
    fora do orcamento e fora do sorteio do dono aleatorio (B1, B2), igual para todo dono."""

    def __init__(self, semente: int, cf: ConfigFrutas) -> None:
        self.cf = cf
        self.k = derivar_semente("calendario-frutas", semente) % len(cf.rotacao_ofertas)

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        if visao.estado["tick"] % TICKS_POR_DIA not in self.cf.horarios_oferta:
            return []
        conjunto = self.cf.rotacao_ofertas[self.k % len(self.cf.rotacao_ofertas)]
        self.k += 1
        return [oferta_de(f) for f in conjunto]


# ------------------------------------------------------------------ unidades derivadas (E3)

BASES_EXPERIMENTO_MAIOR = {"calibracao": (14101, 14202, 14303, 14404, 14505),
                           "validacao": (30101, 30202, 30303, 30404, 30505)}   # adendo 4.1: a 15101...15505 ficou queimada
BASES_N6 = {"calibracao": (19101, 19202, 19303, 19404, 19505), "validacao": (20101, 20202, 20303, 20404, 20505)}
BASES_N7 = {"calibracao": (21101, 21202, 21303, 21404, 21505), "validacao": (22101, 22202, 22303, 22404, 22505)}
BASES_COMPARACAO = {"calibracao": (28101, 28202, 28303, 28404, 28505), "validacao": (29101, 29202, 29303, 29404, 29505)}
# o prefixo das unidades derivadas de cada plano (regra E3): semente derivar_semente(prefixo, b, k), genoma
# derivar_semente(prefixo + "-genoma", b, k) (plano do N6, secao 12.2; plano do N7, secao 12.2; o da comparacao dos cerebros,
# PLANO_ANALISE_V2_COMPARACAO_CEREBROS, secao 6.2; o do mundo fisico, PLANO_ANALISE_V2_MUNDO_FISICO, secao 4; o do corpo,
# PLANO_ANALISE_V2_CORPO_DRIVES, secao 4; o do banheiro, PLANO_ANALISE_V2_BANHEIRO, secao 3; o dos dois pets, PLANO_ANALISE_V2_DOIS_PETS,
# secao 8; o da rede de si, PLANO_ANALISE_V2_REDE_DE_SI, secao 8)
PREFIXOS_UNIDADES = ("experimento-maior", "n6", "n7", "comparacao-cerebros", "mundo", "corpo", "banheiro", "dois_pets", "rede_de_si")
# faixas queimadas: continuam reservadas e nao podem ser usadas para nada (adendo 4.1 do PLANO_ANALISE_V2_EXPERIMENTO_MAIOR)
FAIXAS_QUEIMADAS = ((15101, 15505, "a validacao antiga do experimento maior: run indevida parada em 2026-10-06 (PR #183)"),)
# faixas reservadas ou ja usadas no repositorio (fonte ao lado); o teste tambem varre experiments/configs/. Intervalos fechados.
FAIXAS_RESERVADAS = (
    (101, 1010, "testes (101...505) e ovos da personalidade (101...1010)"),
    (1101, 1505, "baterias do combate V2 (configs bateria_*)"),
    (2101, 2505, "validacao do combate V2"),
    (3101, 3505, "calibracao: V2.1, L1, vinculo B"),
    (4101, 4505, "validacao: V2.1, V21D, equilibrio, L1"),
    (5101, 5505, "validacao do vinculo B"),
    (6101, 6505, "A1, calibracao"), (7101, 7505, "A1, validacao"),
    (8101, 8505, "N3, calibracao"), (9101, 9505, "N3, validacao"),
    (10101, 10505, "N4, calibracao"), (11101, 11505, "N4, validacao"),
    (12101, 12505, "N5, calibracao (reservada)"), (13101, 13505, "N5, validacao (reservada)"),
    (14101, 14505, "experimento maior, bases da calibracao"),
    (15101, 15505, "QUEIMADA: experimento maior, a validacao antiga (adendo 4.1; run indevida parada em 2026-10-06, PR #183); nao usar"),
    (16101, 16505, "N11 cerebros, calibracao (ROADMAP_V2, secao 6; substituida pela C-8, nao usar)"),
    (17101, 17505, "N11 cerebros, validacao (ROADMAP_V2, secao 6; substituida pela C-8, nao usar)"),
    (18101, 18505, "revisao do aprendiz, so calibracao (V2_RODADA_5)"),
    (19101, 19505, "N6, calibracao (PLANO_ANALISE_V2_N6, N6-9)"), (20101, 20505, "N6, validacao (PLANO_ANALISE_V2_N6, N6-9)"),
    (21101, 21505, "N7, calibracao (PLANO_ANALISE_V2_N7, secao 12.1)"), (22101, 22505, "N7, validacao (PLANO_ANALISE_V2_N7, secao 12.1)"),
    (28101, 28505, "comparacao dos cerebros: calibracao de B e C e piloto (PLANO_ANALISE_V2_COMPARACAO_CEREBROS, C-8)"),
    (29101, 29505, "comparacao dos cerebros: validacao de A, B e C (PLANO_ANALISE_V2_COMPARACAO_CEREBROS, C-8)"),
    (30101, 30505, "experimento maior, bases da validacao (adendo 4.1 do PLANO_ANALISE_V2_EXPERIMENTO_MAIOR)"),
    (31101, 31505, "mundo fisico, calibracao e piloto do N (PLANO_ANALISE_V2_MUNDO_FISICO, secao 11, PMF-6)"),
    (32101, 32505, "mundo fisico, validacao (PLANO_ANALISE_V2_MUNDO_FISICO, secao 11, PMF-6)"),
    (33101, 33505, "corpo e drives, calibracao e piloto (PLANO_ANALISE_V2_CORPO_DRIVES, secao 10, PCD-7)"),
    (34101, 34505, "corpo e drives, validacao (PLANO_ANALISE_V2_CORPO_DRIVES, secao 10, PCD-7)"),
    (37101, 37505, "banheiro, calibracao e piloto (PLANO_ANALISE_V2_BANHEIRO, secao 10)"),
    (38101, 38505, "banheiro, validacao (PLANO_ANALISE_V2_BANHEIRO, secao 10)"),
    (39101, 39505, "dois pets, calibracao do K e piloto (PLANO_ANALISE_V2_DOIS_PETS, secao 8, PDP-6)"),
    (40101, 40505, "dois pets, validacao (PLANO_ANALISE_V2_DOIS_PETS, secao 8, PDP-6)"),
    (41101, 41505, "dois pets, adendo do degrau 1b, prevista (PLANO_ANALISE_V2_DOIS_PETS, secoes 8 e 10, PDP-6)"),
    (42101, 42505, "dois pets, adendo dos dois donos, prevista (PLANO_ANALISE_V2_DOIS_PETS, secoes 8 e 10, PDP-6)"),
    (43101, 43505, "rede de si, calibracao e piloto (PLANO_ANALISE_V2_REDE_DE_SI, secao 8, RS-6)"),
    (44101, 44505, "rede de si, validacao (PLANO_ANALISE_V2_REDE_DE_SI, secao 8, RS-6)"),
    (50001, 50020, "analise de poder, piloto"), (60001, 60160, "confirmatoria"), (69001, 69001, "M1, gate G1"),
    (80001, 82004, "linhagem E1 (piloto, genomas e ambientes)"),
    (20260900, 20261800, "fala, voz, comando e bootstraps (sementes de 2026-09/10 e semente + i)"),
)


def unidades_derivadas(bases, k_por_base: int, prefixo: str = "experimento-maior") -> list[dict]:
    """E3 (plano do experimento maior, secao 8.1): a unidade k da base b tem semente derivar_semente(prefixo, b, k) e genoma
    derivar_semente(prefixo + "-genoma", b, k), k = 0..K-1; o prefixo e o do plano (PREFIXOS_UNIDADES: "experimento-maior", o
    padrao; "n6"; "n7"; "comparacao-cerebros"; "mundo"; "corpo"; "banheiro"; "dois_pets"; "rede_de_si"). Falha alto com K < 1, base repetida, prefixo desconhecido ou colisao."""
    if prefixo not in PREFIXOS_UNIDADES:
        raise ValueError(f"prefixo das unidades {prefixo!r}: so {PREFIXOS_UNIDADES}")
    if k_por_base < 1:
        raise ValueError("K precisa ser >= 1")
    bases = list(bases)
    if len(set(bases)) != len(bases):
        raise ValueError(f"base repetida: {bases}")
    out = [{"base": b, "k": k, "semente": derivar_semente(prefixo, b, k),
            "genoma": derivar_semente(f"{prefixo}-genoma", b, k)} for b in bases for k in range(k_por_base)]
    valores = [u["semente"] for u in out] + [u["genoma"] for u in out]
    if len(set(valores)) != len(valores):
        raise ValueError("colisao entre sementes e genomas derivados")
    return out


def na_faixa_reservada(valor: int) -> str | None:
    for lo, hi, fonte in FAIXAS_RESERVADAS:
        if lo <= valor <= hi:
            return fonte
    return None


class ReplayDivergiu(RuntimeError):
    pass


class SementeSemPlano(RuntimeError):
    pass


# ------------------------------------------------------------------ bracos e fonte do sinal


@dataclass(frozen=True)
class Braco:
    rotulo: str
    fonte: str                       # nenhuma | consequencia | informacao | dono
    no: str                          # o no do roadmap que liga a fonte
    informacao: str | None = None    # P2: "certa"; P2e: "errada"
    memoria: str | None = None       # N6: nenhuma | relevante | recencia | embaralhada (o lobo memoria_emocao, chat B)
    pedido: bool = False             # N7: o dono pede "deixe a fruta X" (o mundo do chat A e a entrada `pedido` do chat B)
    canais: bool | None = None       # canais da consequencia (#169): None segue a config; True/False fixa (as ablacoes da K-7)
    julgamento: str | None = None    # P3i: "informacao" = o julgamento do K4 sai como informacao (JulgadorFruta saida="informacao")
    instinto_mundo: str | None = None   # P0z: o instinto do mundo num modo (PoliticaInstintoMundo, etapa 3 do B: "sem_explorar")
    pesos_janela: bool = False       # P1-cw: o peso de cada drive pela falta recente (adendo 2 do plano do corpo, A2.4; chave do B)
    regime: str | None = None        # corpo: None = "hoje" (sem corpo), "quimica" ou "corpo" (PLANO_ANALISE_V2_CORPO_DRIVES, secao 1)
    gestos: str | None = None        # corpo: o DonoComGestos (etapa 6 do A): "sem_tapa", "tapa" ou "tapa_fruta" (o tapa na fruta X, A1.1)
    banheiro: str | None = None      # banheiro: o braco do 2 x 2 (limpador x carinho depois do banheiro): "B00", "B0C", "BL0" ou "BLC"
    metabolismo: bool = False        # corpo, adendo 3 (A3.1, ME-6): o combustivel e a reserva no bloco do corpo, do tapa e nos acoplados


BRACOS = {
    "P0": Braco("P0", "nenhuma", "N0"),
    "P1": Braco("P1", "consequencia", "N3"),
    "P2": Braco("P2", "informacao", "N5", "certa"),
    "P2e": Braco("P2e", "informacao", "N5", "errada"),
    "P2a": Braco("P2a", "informacao", "N5", "acoplada"),
    "P3": Braco("P3", "dono", "N1"),
    # N6 (docs/PLANO_ANALISE_V2_N6.md, secao 4.1): o aprendizado do lobo de decisao desligado (N6-2), a memoria e a unica plasticidade
    "M0": Braco("M0", "nenhuma", "N6", memoria="nenhuma"),
    "MR": Braco("MR", "nenhuma", "N6", memoria="relevante"),
    "MT": Braco("MT", "nenhuma", "N6", memoria="recencia"),
    "ME": Braco("ME", "nenhuma", "N6", memoria="embaralhada"),
    # N7 (docs/PLANO_ANALISE_V2_N7.md, secao 4.1): o pedido "deixe X"; o P3+ped com a bronca da desobediencia (N7-8)
    "P0+ped": Braco("P0+ped", "nenhuma", "N7", pedido=True),
    "P1+ped": Braco("P1+ped", "consequencia", "N7", pedido=True),
    "P3+ped": Braco("P3+ped", "dono", "N7", pedido=True),
    # K-7 (PLANO_CALIBRACAO_CONJUNTA_V2, secoes 1 e 4.1): o P1 completo (memoria com o ganho da config e canais) e as duas ablacoes
    "P1c": Braco("P1c", "consequencia", "K-7", memoria="relevante", canais=True),
    "P1c-mem": Braco("P1c-mem", "consequencia", "K-7", memoria="nenhuma", canais=True),     # sem memoria: g = 0
    "P1c-can": Braco("P1c-can", "consequencia", "K-7", memoria="relevante", canais=False),  # escalar: sem canais
    # adendo 3, secao 3.3, do plano do experimento maior (P2D-P3I): o momento (P2 x P2d) e a interpretacao (P3 x P3i)
    "P2d": Braco("P2d", "informacao", "adendo-3", "depois"),          # a informacao depois do consumo, no lugar da da oferta
    "P3i": Braco("P3i", "dono", "adendo-3", julgamento="informacao"),  # o julgamento do K4 como informacao
    # mundo fisico (PLANO_ANALISE_V2_MUNDO_FISICO, secao 3 e adendo 1): o controle da premissa e a fonte dos acoplados P0^ac e P1^ac
    "P0z": Braco("P0z", "nenhuma", "mundo-fisico", instinto_mundo="sem_explorar"),
    # corpo (PLANO_ANALISE_V2_CORPO_DRIVES, secao 3): o bloco G-HOJE (a quimica contra hoje, malha fechada, os donos de sempre)
    "P0-hoje": Braco("P0-hoje", "nenhuma", "corpo-3.1", regime="hoje"),
    "P1-hoje": Braco("P1-hoje", "consequencia", "corpo-3.1", regime="hoje"),
    "P3-hoje": Braco("P3-hoje", "dono", "corpo-3.1", regime="hoje"),
    "P0-quimica": Braco("P0-quimica", "nenhuma", "corpo-3.1", regime="quimica"),
    "P1-quimica": Braco("P1-quimica", "consequencia", "corpo-3.1", regime="quimica"),
    "P3-quimica": Braco("P3-quimica", "dono", "corpo-3.1", regime="quimica"),
    # o bloco do corpo (3.2), com o DonoComGestos sem tapa; os acoplados P1-q^ac e P1-c^ac saem do registro do P0-q (a config os pede).
    # Desde o adendo 3 (A3.1, ME-6), o bloco do corpo, o do tapa e o G ganham o metabolismo em todos os bracos; o G-HOJE (3.1) fica sem
    "P0-q": Braco("P0-q", "nenhuma", "corpo-3.2", regime="quimica", gestos="sem_tapa", metabolismo=True),
    "P1-q": Braco("P1-q", "consequencia", "corpo-3.2", regime="quimica", gestos="sem_tapa", metabolismo=True),
    "P0-c": Braco("P0-c", "nenhuma", "corpo-3.2", regime="corpo", gestos="sem_tapa", metabolismo=True),
    "P1-c": Braco("P1-c", "consequencia", "corpo-3.2", regime="corpo", gestos="sem_tapa", metabolismo=True),
    # o bloco do tapa (3.3, so no mundo bola)
    "P0-c-tapa": Braco("P0-c-tapa", "nenhuma", "corpo-3.3", regime="corpo", gestos="tapa", metabolismo=True),
    "P1-c-tapa": Braco("P1-c-tapa", "consequencia", "corpo-3.3", regime="corpo", gestos="tapa", metabolismo=True),
    # o bloco G, a generalizacao do tapa (adendo 1, A1.1, no iguais_frutas)
    "P1-c-tapaX": Braco("P1-c-tapaX", "consequencia", "corpo-A1.1", regime="corpo", gestos="tapa_fruta", metabolismo=True),
    "P1-c-frutas": Braco("P1-c-frutas", "consequencia", "corpo-A1.1", regime="corpo", gestos="sem_tapa", metabolismo=True),
    # corpo, adendo 2 (PLANO_ANALISE_V2_CORPO_DRIVES, A2.4 e A2.5): o P1-c com o peso de cada drive pela janela recente
    "P1-cw": Braco("P1-cw", "consequencia", "corpo-A2.4", pesos_janela=True, regime="corpo", gestos="sem_tapa", metabolismo=True),
    # banheiro (PLANO_ANALISE_V2_BANHEIRO, secoes 1 a 3): os quatro bracos do 2 x 2 (limpador x carinho depois do banheiro), com o cerebro A
    # no P1 (o aprendiz, fonte consequencia) e no P0 (o instinto, a referencia), no corpo com os gestos e o banheiro; o mundo fisico
    **{f"{c}-{b}": Braco(f"{c}-{b}", fonte, "banheiro", regime="corpo", banheiro=b)
       for c, fonte in (("P0", "nenhuma"), ("P1", "consequencia")) for b in ("B00", "B0C", "BL0", "BLC")},
}
# o 2 x 2 do banheiro: o braco -> (limpador, carinho depois do banheiro)
BRACOS_BANHEIRO = {"B00": (False, False), "B0C": (False, True), "BL0": (True, False), "BLC": (True, True)}
FONTES_IMPLEMENTADAS = ("nenhuma", "dono", "consequencia", "informacao")
# o que os bracos do N6 e do N7 esperam de outros chats; um braco que depende de uma peca daqui falha alto com o no. A entrada sai
# daqui quando a peca estiver na main (e os testes de tests/test_bancada_n6_n7.py dizem o que conferir entao).
# Vazio desde a BANCADA-LIGA-N6-N7: a memoria (CEREBRO-N6-N7, #167) e o pedido (N7-MUNDO, #166) estao na main. Fica a tabela para a
# proxima peca de outro chat (o K4 e os canais, rodada 10).
NOS_PENDENTES: dict = {
    # o "instinto_mundo" (W-BANCADA-MUNDO) saiu na W-LIGA-MUNDO: a PoliticaInstintoMundo e os ganchos dos cerebros estao na main (#232)
    # o "pesos_janela" (W-DOMINANCIA) saiu na W-LIGA-PESOS-JANELA: a chave da ConfigConsequencia esta na main (#236)
    # o "corpo", o "dono_gestos" e o "tapa" (W-BANCADA-CORPO) sairam na W-LIGA-GESTOS: a etapa 6 do corpo esta na main (o motor e o
    # DonoComGestos do A, #245; a quimica dos drives novos e dos gestos e o cerebro do B, #247). O "corpo_mundo" saiu junto: o #247 passou
    # o cerebro ao arranjo do MotorCorpo no mundo fisico (o consequencia_mundo credita, o consequencia_corpo fecha a decisao), com o G1
    # o "banheiro" (W-BANCADA-BANHEIRO) saiu na W-BANCADA-DOIS-PETS: a etapa 3 do banheiro esta na main (#265: o banheiro no MotorMundo,
    # a necessidade, o limpador, o limpar, o aliviar com alvo e o DonoCarinhoBanheiro)
    # dois pets (TAREFA_V2_DOIS_PETS, etapa 5, do D): o "sentidos_grupo" saiu com o #263 (a visao, o toque e a disputa) e o
    # "cerebro_social" com o #266 (as entradas sociais e o modelo dos outros no cerebro A, ligados nos bracos do grupo)
    # o "canais_fruta_mundo" (W-BANCADA-DOIS-PETS) saiu na W-BANCADA-METABOLISMO: a rota do canal do humor no mundo fisico entrou (#269,
    # ConfigLobos.presenca_fruta_mundo), ligada no cerebro do grupo
    # metabolismo (TAREFA_V2_METABOLISMO, ME-7; PLANO_ANALISE_V2_CORPO_DRIVES, A3.2): o passo 0 da calibracao do corpo escala "o gasto
    # (basal e das atividades sobre o combustivel)". O basal tem campo na ConfigCorpo; as atividades tiram do combustivel o mesmo numero
    # que somam ao cansaco (ME-3), sem fator. Trava o passo 0 (`pontos_passo0`)
    "gasto_atividades": "o fator do gasto das atividades sobre o combustivel na ConfigCorpo (ME-7 e A3.2: o passo 0 escala o basal e as "
                        "atividades; o corpo de hoje tira das atividades o mesmo numero que somam ao cansaco, ME-3, sem fator; do B, "
                        "digilab/corpo.py)",
}
# filtros do acoplado que dependem de eventos que ainda nao existem: o no do NOS_PENDENTES de cada um. O "sem_gestos" saiu na
# W-LIGA-GESTOS (o tapa na main)
FILTROS_PENDENTES: dict = {}
# a memoria de cada braco do N6 no cerebro: o M0 guarda e nao age (ganho 0, N6-2/N6-3); o ME com o desarranjo da vida (N6-6)
MODO_MEMORIA = {"nenhuma": "relevante", "relevante": "relevante", "recencia": "recencia", "embaralhada": "embaralhada"}
CONFIG_LOBOS_PADRAO = ConfigLobos()
# os drives do sinal pelos nomes do corpo (PLANO_ANALISE_V2_CORPO_DRIVES, A2.2), pelos indices de Estado.vetor (os canais de
# lobos.CANAL_DO_DRIVE: fome, higiene, energia, humor)
NOMES_DRIVES = {0: "fome", 1: "desconforto", 2: "cansaco", INDICE_HUMOR: "tristeza"}
APRENDE_PELA_CONSEQUENCIA = ("consequencia", "informacao")   # o P2 e o P1 com a informacao na percepcao (plano do N5, secao 3)


def braco_de(rotulo: str) -> Braco:
    if rotulo not in BRACOS:
        raise KeyError(f"braco desconhecido {rotulo!r}: {sorted(BRACOS)}")
    b = BRACOS[rotulo]
    if b.fonte not in FONTES_IMPLEMENTADAS:
        raise NotImplementedError(f"braco {b.rotulo}: a fonte {b.fonte!r} chega no {b.no} (docs/ROADMAP_V2.md)")
    if b.regime is not None and b.regime not in REGIMES_CORPO:
        raise ValueError(f"braco {b.rotulo}: regime {b.regime!r}, so {REGIMES_CORPO}")
    if b.gestos is not None and (b.gestos not in GESTOS_DONO or b.regime in (None, "hoje")):
        raise ValueError(f"braco {b.rotulo}: gestos {b.gestos!r} (so {GESTOS_DONO}, e so com o corpo)")
    if b.banheiro is not None and (b.banheiro not in BRACOS_BANHEIRO or b.regime != "corpo" or b.gestos is not None
                                   or b.fonte not in ("nenhuma", "consequencia")):
        raise ValueError(f"braco {b.rotulo}: banheiro {b.banheiro!r} (so {sorted(BRACOS_BANHEIRO)}, no corpo, sem os gestos de dono e "
                         "so no P0 ou no P1)")
    if b.metabolismo and b.regime not in ("quimica", "corpo"):
        raise ValueError(f"braco {b.rotulo}: o metabolismo so existe com o corpo (regime quimica ou corpo), nao {b.regime!r}")
    if b.gestos in ("tapa", "tapa_fruta") and b.regime != "corpo":
        raise ValueError(f"braco {b.rotulo}: o tapa so existe com `gestos` no corpo (regime \"corpo\"), nao {b.regime!r}")
    for peca, presente in (("memoria", b.memoria is not None), ("pedido", b.pedido), ("instinto_mundo", b.instinto_mundo is not None),
                           ("pesos_janela", b.pesos_janela), ("corpo", b.regime == "corpo"),
                           ("dono_gestos", b.gestos is not None), ("tapa", b.gestos in ("tapa", "tapa_fruta")),
                           ("banheiro", b.banheiro is not None)):
        if presente and peca in NOS_PENDENTES:
            raise NotImplementedError(f"braco {b.rotulo}: {NOS_PENDENTES[peca]}")
    return b


def filtro_de(nome: str) -> frozenset:
    """O conjunto de acoes que o filtro do acoplado tira; um filtro que depende de evento que ainda nao existe falha alto com o no."""
    if nome in FILTROS_PENDENTES and FILTROS_PENDENTES[nome] in NOS_PENDENTES:
        raise NotImplementedError(f"filtro {nome!r}: {NOS_PENDENTES[FILTROS_PENDENTES[nome]]}")
    if nome not in FILTROS:
        raise KeyError(f"filtro desconhecido {nome!r}: {sorted(FILTROS)}")
    return FILTROS[nome]


def desarranjo_n6(semente: int) -> dict:
    """N6-6 (plano do N6, secao 4.1): a permutacao pi do ME, um desarranjo de FRUTAS (nenhuma fruta em si mesma), sorteado uma vez por
    vida pela rng propria derivar_semente("n6-embaralha", semente). Com tres frutas ha dois, um por sentido do ciclo. Nao toca outra rng."""
    rng = random.Random(derivar_semente("n6-embaralha", semente))
    passo = 1 + rng.randrange(len(FRUTAS) - 1) if len(FRUTAS) == 3 else None
    if passo is None:                       # pragma: no cover - o mundo das frutas tem tres frutas (FRUTAS)
        raise ValueError("desarranjo_n6 escrito para tres frutas")
    pi = {f: FRUTAS[(i + passo) % len(FRUTAS)] for i, f in enumerate(FRUTAS)}
    if tuple(pi[f] for f in FRUTAS) != desarranjo_dos_lobos(semente):     # o mesmo pi que os lobos usam (CEREBRO-N6-N7)
        raise RuntimeError("desarranjo_n6 da bancada difere do dos lobos")
    return pi


# BANCADA-MONTAGEM: as pecas do cerebro A montado que cada fonte liga (PLANO_CALIBRACAO_CONJUNTA_V2, secao 1). memoria: o modo
# (com o ganho g da config); canais: os da consequencia; info: o w0_info da config. O pedido segue o braco (so onde ha pedido).
MONTAGENS = ("simples", "completa")
MONTAGEM_PADRAO = "simples"
MONTAGEM_COMPLETA = {
    "nenhuma": {"memoria": None, "canais": False, "info": False},           # P0 (K-1): o instinto, nada ligado
    "consequencia": {"memoria": "relevante", "canais": True, "info": False},  # P1
    "informacao": {"memoria": "relevante", "canais": True, "info": True},     # P2, P2e, P2a
    "dono": {"memoria": "relevante", "canais": False, "info": False},         # P3: o sinal e o dono, sem canais
}


def recebe_informacao(b: Braco) -> bool:
    """O braco recebe informacao do dono? Os de fonte informacao (P2, P2e, P2a, P2d) e o P3i (o julgamento como informacao): na
    montagem completa so eles ficam com o w0_info da config."""
    return MONTAGEM_COMPLETA[b.fonte]["info"] or b.julgamento == "informacao"


def braco_montado(b: Braco, montagem: str, frutas: bool) -> Braco:
    """O braco com as pecas da montagem. "simples": o proprio braco. "completa": a memoria e os canais da fonte (MONTAGEM_COMPLETA)
    onde o braco nao os fixa; a memoria so nos mundos das frutas (fora deles o cerebro nao a tem). O que o braco fixa vence: o N6 (M0 a
    ME) e as ablacoes da K-7 (P1c-mem sem memoria, P1c-can sem canais) ficam o que sao, por cima da montagem."""
    if montagem not in MONTAGENS:
        raise ValueError(f"montagem {montagem!r}: so {MONTAGENS}")
    if montagem == "simples":
        return b
    pecas = MONTAGEM_COMPLETA[b.fonte]
    memoria = b.memoria if b.memoria is not None else (pecas["memoria"] if frutas else None)
    canais = b.canais if b.canais is not None else pecas["canais"]
    return replace(b, memoria=memoria, canais=canais)


def cfg_lobos_do_braco(cl: ConfigLobos, b: Braco, semente: int, montagem: str = MONTAGEM_PADRAO) -> ConfigLobos:
    """As chaves do N6 e do N7 que o braco liga por cima do aprendiz do ponto (CEREBRO-N6-N7): memoria so nos bracos de memoria (o M0
    com ganho 0; o MT na recencia; o ME com o desarranjo da vida), o pedido so nos bracos com pedido (w0_pedido da config). Nos outros
    bracos as chaves voltam ao padrao (desligadas): a vida de hoje, byte a byte, seja qual for a config. Na montagem completa o braco
    chega ja montado (braco_montado) e o w0_info da config fica so nos bracos com fonte informacao (os P2)."""
    if montagem not in MONTAGENS:
        raise ValueError(f"montagem {montagem!r}: so {MONTAGENS}")
    if montagem == "completa" and not recebe_informacao(b):
        cl = replace(cl, w0_info=0)
    if b.memoria is None:
        cl = replace(cl, memoria_ligada=False, memoria_ganho=0, memoria_modo=CONFIG_LOBOS_PADRAO.memoria_modo, memoria_permutacao=())
    else:
        modo = MODO_MEMORIA[b.memoria]
        cl = replace(cl, memoria_ligada=True, memoria_modo=modo, memoria_ganho=0 if b.memoria == "nenhuma" else cl.memoria_ganho,
                     memoria_permutacao=desarranjo_dos_lobos(semente) if modo == "embaralhada" else ())
    if not b.pedido:
        cl = replace(cl, w0_pedido=0)
    return cl


class PoliticaDoBraco:
    """O cerebro do braco com a fonte do sinal na frente dele. Decide, observa e serializa pelo cerebro; o que muda entre os
    bracos e so de onde vem o sinal: na fonte "dono" tudo o que passa por `receber_acao_dono`, na "nenhuma" nada, na
    "consequencia" so o sinal da propria acao, calculado em `observar` (o dono nao chega). Nao consome rng nem muda a ordem de
    nada: a vida do P3 e byte a byte a da L1 e a do P0 a do instinto (testes).

    Os gestos do corpo (etapa 6; TAREFA_V2_CORPO_DRIVES, secao 8): o tapa e o sinal direto (CD-10) e chega ao cerebro em toda fonte que
    aprende (dono, consequencia, informacao); o carinho chega so pelo corpo, no `mudanca_no_corpo` (CD-4), nas mesmas fontes. No P0
    (fonte "nenhuma", o aprendizado desligado) nenhum dos dois chega, como nada do dono."""

    def __init__(self, cerebro, braco: Braco, cfg_consequencia: ConfigConsequencia | None = None) -> None:
        self.cerebro = cerebro
        self.braco = braco
        self.nome = cerebro.nome
        self.cfg_consequencia = cfg_consequencia or CONFIG_CONSEQUENCIA
        self.sinais_entregues = 0        # elogios e broncas que chegaram ao aprendiz (a eficiencia amostral conta estes)
        self.consequencias = 0           # P1: decisoes com sinal de consequencia != 0

    def agir(self, obs, rng):
        return self.cerebro.agir(obs, rng)

    def observar(self, transicao) -> None:
        if self.braco.fonte in APRENDE_PELA_CONSEQUENCIA:
            f_S = sinal_homeostatico(transicao, self.cerebro.cl.escala, self.cfg_consequencia)
            self.consequencias += f_S != 0
            self.cerebro.observar_consequencia(transicao, f_S, self.cfg_consequencia)   # o mesmo ganho no sinal da fruta (E2)
        else:
            self.cerebro.observar(transicao)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        if self.braco.fonte == "dono":
            self.sinais_entregues += acao.value in SINAIS_DO_DONO
            self.cerebro.receber_acao_dono(acao, tick)
        elif acao is AcaoUsuario.TAPA and self.braco.fonte in APRENDE_PELA_CONSEQUENCIA:
            # o tapa e o sinal direto em toda fonte que aprende (CD-10): o cerebro o credita a ultima decisao; o resto do dono nao chega
            self.sinais_entregues += 1
            self.cerebro.receber_acao_dono(acao, tick)
        elif self.braco.fonte not in ("nenhuma",) + APRENDE_PELA_CONSEQUENCIA:   # pragma: no cover - braco_de ja barra
            raise NotImplementedError(self.braco.fonte)
        # informacao: nada do dono chega ao aprendiz por aqui (o MotorFrutas nem chama o gancho para informar; plano do N5, secao 3)

    def mudanca_no_corpo(self, obs_antes, obs_depois) -> None:
        """O carinho pelo corpo (CD-4; o MotorCorpo com `gestos` chama este gancho, sem dizer que gesto foi): chega ao cerebro nas fontes
        que aprendem, como o tapa; no P0, nada. Explicito, para o __getattr__ nao o repassar ao P0."""
        if self.braco.fonte == "nenhuma":
            return
        self.cerebro.mudanca_no_corpo(obs_antes, obs_depois)

    def consequencia_mundo(self, acao, ocorrido: dict, obs_depois) -> None:
        """O gancho do MotorMundo (explorar, comer e brincar, com tudo aplicado), repassado ao cerebro EM TODA FONTE: o cerebro anota o
        que aconteceu no motivo, o modelo dos outros (`modelo_outros`, dois pets, #266) conta as idas a `onde_comeu` e o que o pet comeu,
        e so na fonte consequencia ha sinal pendente para creditar (o cerebro decide; no P0, nada e creditado). Explicito, para nao
        depender do __getattr__; o cerebro sem o gancho (o instinto) nao recebe nada, como antes."""
        gancho = getattr(self.cerebro, "consequencia_mundo", None)
        if gancho is not None:
            gancho(acao, ocorrido, obs_depois)

    def estado_interno(self) -> dict:
        return {**self.cerebro.estado_interno(), "bancada": {"braco": self.braco.rotulo, "fonte": self.braco.fonte}}

    def __getattr__(self, nome):
        cerebro = self.__dict__.get("cerebro")
        if cerebro is None:
            raise AttributeError(nome)
        return getattr(cerebro, nome)


# ------------------------------------------------------------------ a vida


@dataclass(frozen=True)
class EspecVida:
    dono: str
    braco: str
    semente: int
    genoma: int | None = None
    mundo: str = "padrao"
    cerebro: str = "lobos"
    lugar: str | None = None         # mundo fisico: onde o dono solta a racao (DonoComLugar; PMF-4); so nele, e obrigatorio nele

    @property
    def nome(self) -> str:
        m = "" if self.mundo == "padrao" else f"~{self.mundo}"
        g = "" if self.genoma is None else f"~g{self.genoma}"
        c = "" if self.cerebro == "lobos" else f"~{self.cerebro}"
        lg = "" if self.lugar is None else f"~{self.lugar}"
        return f"{self.dono}-{self.braco}{c}{m}{lg}{g}@{self.semente}"

    @property
    def celula(self) -> tuple:
        """O que define o par de vidas que se comparam entre bracos: tudo menos o braco (no mundo fisico, o lugar tambem)."""
        base = (self.dono, self.semente, self.genoma, self.mundo, self.cerebro)
        return base if self.lugar is None else base + (self.lugar,)

    @property
    def condicao(self) -> str:
        return mundo_de(self.mundo).condicao


@dataclass
class VidaBancada:
    espec: EspecVida
    motor: MotorComFeedback
    interacoes: int                  # acoes do dono no log, fora os eventos do mundo
    origem: str | None = None        # so no modo acoplado: o nome da vida de origem, o braco dela e o filtro
    origem_braco: str | None = None
    filtro: str | None = None
    broncas: int = 0                 # N7: as broncas do pedido no registro (repreender pelo canal do mundo, fora do orcamento)
    julgamentos: int = 0             # K4: os julgamentos da fruta no registro (elogiar/repreender pelo canal do mundo)
    retirados: int = 0               # mundo fisico: os sinais do dono que o filtro sem_ensino ao vivo nao deixou chegar (PMF-3); com os
    #                                  gestos: as broncas do modo sem tapa (SemGesto), que gastam o orcamento e nao chegam ao log
    carinhos: int = 0                # banheiro: os carinhos do DonoCarinhoBanheiro (acariciar pelo canal do mundo, fora do orcamento)
    gestos: dict | None = None       # corpo: o que o DonoComGestos trocou (acariciar, tapa, sem_gesto) e, no P1-c-tapaX, os tapas na fruta X

    @property
    def rotulo_braco(self) -> str:
        """O braco na tabela: "P3", ou "P0<P3:sem_sinais" para o P0 acoplado ao registro do P3 sem os sinais."""
        b = self.espec.braco if self.espec.cerebro == "lobos" else f"{self.espec.braco}~{self.espec.cerebro}"
        if self.origem is None:
            return b
        return f"{b}<{self.origem_braco}:{self.filtro}"

    @property
    def eventos_mundo(self) -> int:
        return contar_acoes(self.motor.log)[1]

    @property
    def informacoes(self) -> int:
        return contar_informacoes(self.motor.log)

    @property
    def pedidos(self) -> int:
        return contar_pedidos(self.motor.log)

    @property
    def nome(self) -> str:
        if self.origem is None:
            return self.espec.nome
        e = self.espec
        return replace(e, braco=f"{e.braco}~de-{self.origem_braco}-{self.filtro}").nome


def filtrar_log(log: LogDeEventos, retirar: frozenset) -> LogDeEventos:
    """O mesmo log sem as acoes do dono em `retirar` (valores de AcaoUsuario); avancos, eventos do mundo e as outras acoes nos
    mesmos ticks. Tirar um evento do mundo falha alto: o acoplado reproduz o mundo da origem."""
    if retirar & EVENTOS_DO_MUNDO:
        raise ValueError(f"o filtro tiraria eventos do mundo: {sorted(retirar & EVENTOS_DO_MUNDO)}")
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in retirar)])


def contar_acoes(log: LogDeEventos) -> tuple[int, int]:
    """(acoes do dono no orcamento, eventos do mundo). As informacoes (fora do orcamento, sem ser mundo) nao entram em nenhuma das
    duas: contar_informacoes."""
    dono = mundo = 0
    for e in log:
        if e.tipo == "acao_usuario":
            if str(e.valor) in EVENTOS_DO_MUNDO:
                mundo += 1
            elif str(e.valor) not in INFORMACOES and str(e.valor) not in PEDIDOS:
                dono += 1
    return dono, mundo


def contar_gestos_mundo(log: LogDeEventos) -> int:
    """Os gestos do dono no mundo fisico (deixar_comida, deixar_bola): eventos proprios do log, no orcamento do dono (CanalMundo)."""
    return sum(1 for e in log if e.tipo in ("deixar_comida", "deixar_bola"))


def contar_pedidos(log: LogDeEventos) -> int:
    return sum(1 for e in log if e.tipo == "acao_usuario" and str(e.valor) in PEDIDOS)


def contar_informacoes(log: LogDeEventos) -> int:
    return sum(1 for e in log if e.tipo == "acao_usuario" and str(e.valor) in INFORMACOES)


def resumo_motor(motor) -> tuple:
    """Tudo que uma vida produz: log, estado final, acoes do pet, as rngs e, no motor de personalidade, obediencia, recusas,
    desejos e vinculo."""
    extra = ()
    if isinstance(motor, MotorPersonalidade):
        extra = (motor._rng_obediencia.getstate(), [r.para_dict() for r in motor.recusas],
                 [d.para_dict() for d in motor.desejos], motor.vinculo.para_dict())
    if isinstance(motor, MotorAmbiente):
        bola = motor.resumo_bola() if motor.cb.ligada else {"ligada": False, "contagem": dict(motor.contagem_bola)}
        extra = extra + (bola, dict(motor.contagem), motor.morte)
    if isinstance(motor, MotorFrutas):
        extra = extra + (motor.resumo_frutas(),)
    if isinstance(motor, MotorFrutasMundo):
        extra = extra + (motor.resumo_mundo(),)
    if isinstance(motor, MotorMundo) and motor.cmf.ligada:
        extra = extra + (motor.resumo_mundo_fisico(),)
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9), motor._rng_politica.getstate(),
            motor._rng_ambiente.getstate(), *extra)


def _interno(motor) -> str:
    return json.dumps(motor.politica.estado_interno(), sort_keys=True)


@dataclass(frozen=True)
class Bancada:
    dias: int
    orcamento: int
    cfg_lobos: ConfigLobos = CONFIG_LOBOS_APRENDIZ    # o aprendiz de todos os bracos (o P0 o usa com o aprendizado desligado)
    cfg_bola: ConfigBola = CONFIG_BOLA_LIGADA          # a bola dos mundos da bola (padroes calibrados na A1)
    cfg_consequencia: ConfigConsequencia = CONFIG_CONSEQUENCIA    # o sinal do P1 (N3)
    cfg_frutas: ConfigFrutas = CONFIG_FRUTAS_LIGADA    # as frutas dos mundos das frutas (padroes calibrados no N4)
    cfg_informacao: ConfigInformacao = CONFIG_INFORMACAO_LIGADA   # o canal da informacao, ligado em todo mundo das frutas (N5)
    cfg_pedido: ConfigPedido = CONFIG_PEDIDO_LIGADA      # N7: o pedido, ligado so no motor dos bracos com pedido
    julgamento_fruta: bool = False                       # K4: o dono dos bracos com fonte dono julga a fruta, fora do orcamento
    montagem: str = MONTAGEM_PADRAO                      # BANCADA-MONTAGEM: "simples" (a de antes) ou "completa" (o cerebro A da secao 1)
    cfg_mundo: ConfigMundo = CONFIG_MUNDO_LIGADA         # W-BANCADA-MUNDO: o mundo fisico (o layout afastado vem do mundo)
    cfg_corpo: ConfigCorpo = CONFIG_CORPO_QUIMICA        # W-BANCADA-CORPO: o corpo do regime "quimica" (o "corpo" liga por cima)
    metabolismo: bool = True                             # adendo 3 (A3.1): False tira o metabolismo dos bracos do corpo, so para
                                                         # refazer as vidas de antes dele (os gabaritos do G2); fora da config

    def __post_init__(self) -> None:
        if self.dias <= 0 or self.orcamento <= 0:
            raise ValueError("dias e orcamento precisam ser positivos")
        if not self.cfg_lobos.aprendizado_ligado:
            raise ValueError("cfg_lobos e a do aprendiz (aprendizado ligado); o P0 desliga por conta propria")
        if not self.cfg_bola.ligada:
            raise ValueError("cfg_bola e a dos mundos da bola: ligada (o mundo padrao nao usa bola)")
        if not self.cfg_frutas.ligada:
            raise ValueError("cfg_frutas e a dos mundos das frutas: ligada")
        if not (self.cfg_corpo.ligada and self.cfg_corpo.digestao and self.cfg_corpo.vida) or self.cfg_corpo.drives_novos \
                or self.cfg_corpo.gestos or self.cfg_corpo.metabolismo:
            raise ValueError("cfg_corpo e a da quimica (ligada, digestao e Vida, sem drives novos, gestos nem metabolismo); o regime e o "
                             "braco ligam o resto")
        if not self.cfg_informacao.ligada:
            raise ValueError("cfg_informacao e a dos mundos das frutas: ligada (sem informante, nada muda na vida)")
        if not self.cfg_pedido.ligada:
            raise ValueError("cfg_pedido e a dos bracos com pedido: ligada")
        if self.montagem not in MONTAGENS:
            raise ValueError(f"montagem {self.montagem!r}: so {MONTAGENS}")
        if not self.cfg_mundo.ligada:
            raise ValueError("cfg_mundo e a do mundo fisico: ligada")

    def cfg_mundo_de(self, mundo: Mundo) -> ConfigMundo:
        """A ConfigMundo de um mundo fisico: a da bancada, com o layout afastado no `fisico_afastado` (A1.8; nada mais muda)."""
        if mundo.fisico is None:
            raise ValueError(f"mundo {mundo.nome!r} nao e o fisico")
        layout = LAYOUTS_FISICO[mundo.fisico]
        return self.cfg_mundo if layout is None else replace(self.cfg_mundo, layout=layout)

    def braco(self, espec: EspecVida) -> Braco:
        """O braco da vida com as pecas da montagem da bancada (braco_montado)."""
        return braco_montado(braco_de(espec.braco), self.montagem, mundo_de(espec.mundo).frutas)

    @property
    def tick_troca(self) -> int:
        """o mutavel troca na metade da vida (no fim do dia dias // 2: dia 7 numa vida de 14; plano, secao 4.3)"""
        if self.dias < 2:
            raise ValueError("o mutavel precisa de pelo menos 2 dias")
        return (self.dias // 2) * TICKS_POR_DIA

    def janelas_frutas(self, condicao: str) -> dict:
        """as janelas da taxa_fruta_ruim (plano, secao 4.3): inicio e final (as duas metades da vida), antes e depois da troca no
        mutavel, e uma por dia (a curva)"""
        metade, fim = (self.dias // 2) * TICKS_POR_DIA, self.dias * TICKS_POR_DIA
        j = {"total": (0, fim), "inicio": (0, metade), "final": (metade, fim)}
        if condicao == "mutavel":
            j["antes_da_troca"] = (0, self.tick_troca)
            j["depois_da_troca"] = (self.tick_troca, fim)
        for d in range(self.dias):
            j[f"dia_{d + 1}"] = (d * TICKS_POR_DIA, (d + 1) * TICKS_POR_DIA)
        return j

    # ------------------------------------------------------------- fabricas

    def politica(self, espec: EspecVida, cfg=None) -> PoliticaDoBraco:
        if espec.cerebro not in CEREBROS:
            raise KeyError(f"cerebro {espec.cerebro!r}: so {CEREBROS} (outros cerebros sao a comparacao do N11)")
        b = braco_de(espec.braco)
        mundo = mundo_de(espec.mundo)
        if b.fonte == "informacao" and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a informacao e sobre as frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        if (b.memoria is not None or b.pedido) and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a memoria e o pedido sao das frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        if b.instinto_mundo is not None and mundo.fisico is None:
            raise ValueError(f"braco {b.rotulo}: o instinto do mundo e do mundo fisico, nao {espec.mundo!r}")
        if mundo.fisico is not None and (espec.cerebro == "instinto" or b.instinto_mundo is not None):
            # o instinto que ve o mundo (instinto_mundo, #232), com os pesos w_bola e w_fruta da bancada (as chaves de hoje desligadas: o
            # mundo substitui o cenario do N4 e da A1). O P0z e ele no modo sem_explorar, em qualquer cerebro: os lobos nao tem o modo
            if b.fonte != "nenhuma" or b.memoria is not None or b.pedido:
                raise ValueError(f"o instinto do mundo so no P0 e no P0z (nao aprende, nao lembra, nao le o pedido): braco {b.rotulo}")
            if b.instinto_mundo not in (None, "sem_explorar"):
                raise ValueError(f"braco {b.rotulo}: modo do instinto do mundo {b.instinto_mundo!r}")
            cb, cf = self.pesos_do_mundo()
            if b.banheiro is not None:          # banheiro: o instinto do alivio, sobre o do mundo (o P0 do 2 x 2 com o cerebro instinto)
                return PoliticaDoBraco(PoliticaInstintoBanheiro(cfg, self.cfg_banheiro_de(espec), self.cfg_corpo_de(espec), cb, cf), b)
            return PoliticaDoBraco(PoliticaInstintoMundo(cfg, cb, cf, sem_explorar=b.instinto_mundo == "sem_explorar"), b)
        if espec.cerebro == "instinto":
            if b.fonte != "nenhuma" or b.memoria is not None or b.pedido:
                raise ValueError(f"cerebro instinto so no P0 (nao aprende, nao lembra, nao le o pedido): braco {b.rotulo}")
            if mundo.frutas:
                return PoliticaDoBraco(PoliticaInstintoFrutas(cfg, CONFIG_BOLA, self.cfg_frutas), b)
            if mundo.bola is not None:
                return PoliticaDoBraco(PoliticaInstintoBola(cfg, self.cfg_bola), b)
            return PoliticaDoBraco(PoliticaInstinto(cfg), b)
        b = self.braco(espec)       # a montagem (BANCADA-MONTAGEM); na simples, o proprio braco
        cl = self.cfg_lobos if b.fonte != "nenhuma" else replace(self.cfg_lobos, aprendizado_ligado=False)
        cl = cfg_lobos_do_braco(cl, b, espec.semente, self.montagem)
        # LOBOS-MUNDO (#141): os lobos veem o mundo em que vivem; no padrao, nenhuma chave (as formas de antes). No mundo fisico, a
        # chave dele (MUNDO-CEREBROS, #232), com os pesos da bancada nas chaves de hoje desligadas
        cb = self.cfg_bola if mundo.bola is not None else None
        cf = self.cfg_frutas if mundo.frutas else None
        cm = None
        if mundo.fisico is not None:
            (cb, cf), cm = self.pesos_do_mundo(), self.cfg_mundo_de(mundo)
        # canais (#169): o braco que os fixa (as ablacoes da K-7) manda; os outros seguem a config
        cc = self.cfg_consequencia if b.canais is None else replace(self.cfg_consequencia, canais_ligados=b.canais)
        if b.pesos_janela:                  # P1-cw (A2.4, #236): o peso de cada drive pela falta recente; o resto do P1 igual
            cc = replace(cc, pesos_janela=True)
        return PoliticaDoBraco(PoliticaLobos(cfg, cl, cfg_bola=cb, cfg_frutas=cf, cfg_mundo=cm, cfg_corpo=self.cfg_corpo_de(espec),
                                             cfg_banheiro=self.cfg_banheiro_de(espec)), b, cc)

    def cfg_corpo_de(self, espec: EspecVida) -> ConfigCorpo | None:
        """A ConfigCorpo da vida pelo regime do braco: None em "hoje" (e nos bracos sem regime: a vida de antes); a da bancada em
        "quimica"; a da bancada com `drives_novos` e `gestos` em "corpo" (a etapa 6). Vale tambem no mundo fisico (o arranjo do #247)."""
        regime = braco_de(espec.braco).regime
        if regime in (None, "hoje"):
            return None
        if regime == "quimica":
            return replace(self.cfg_corpo, drives_novos=False, gestos=False, metabolismo=self.metabolismo_de(espec))
        # banheiro: o corpo com os gestos e a sub-chave banheiro (a vontade e o conforto, TAREFA_V2_BANHEIRO, secao 3 e BN-6)
        return replace(self.cfg_corpo, drives_novos=True, gestos=True, banheiro=braco_de(espec.braco).banheiro is not None,
                       metabolismo=self.metabolismo_de(espec))

    def metabolismo_de(self, espec: EspecVida) -> bool:
        """o metabolismo da vida: o do braco (A3.1), salvo na bancada com `metabolismo=False` (as vidas de antes, so para o G2)"""
        return self.metabolismo and braco_de(espec.braco).metabolismo

    def cfg_banheiro_de(self, espec: EspecVida) -> ConfigBanheiro | None:
        """A ConfigBanheiro da vida: None fora dos bracos do banheiro; nos quatro do 2 x 2, a ligada, com o limpador do braco (BL0 e BLC).
        O carinho depois do banheiro e do dono (o DonoCarinhoBanheiro), nao da chave."""
        b = braco_de(espec.braco)
        if b.banheiro is None:
            return None
        if mundo_de(espec.mundo).fisico is None:
            raise ValueError(f"braco {b.rotulo}: o banheiro e do mundo fisico, nao {espec.mundo!r}")
        return replace(CONFIG_BANHEIRO_LIGADA, limpador=BRACOS_BANHEIRO[b.banheiro][0])

    def pesos_do_mundo(self) -> tuple[ConfigBola, ConfigFrutas]:
        """A ConfigBola e a ConfigFrutas da bancada com a chave desligada: no mundo fisico elas so dao os pesos w_bola e w_fruta ao instinto
        do mundo e ao prior dos lobos (o MotorMundo exige as duas desligadas)."""
        return replace(self.cfg_bola, ligada=False), replace(self.cfg_frutas, ligada=False)

    def fabrica_politica(self, espec: EspecVida):
        return lambda cfg=None: self.politica(espec, cfg)

    def fabrica_motor(self, espec: EspecVida):
        mundo = mundo_de(espec.mundo)
        # corpo (W-BANCADA-CORPO): o com_corpo(...) do motor do mundo, com a ConfigCorpo do regime; sem regime, o motor de antes
        corpo = self.cfg_corpo_de(espec)
        classe = (lambda base: base) if corpo is None else com_corpo  # noqa: E731
        kc = {} if corpo is None else {"cfg_corpo": corpo}
        banheiro = self.cfg_banheiro_de(espec)       # o banheiro (#265): a chave no MotorMundo, com o corpo com a sub-chave na frente
        if banheiro is not None:
            kc["cfg_banheiro"] = banheiro
        if mundo.fisico is not None:
            # o desenho do plano do mundo (secao 2): MotorMundo, obediencia, educacao, lesoes, frutas e bola de hoje desligadas, especie
            # brasa; o mundo "iguais" (PMF-7): as tres frutas com o efeito neutro no humor
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cm = self.cfg_mundo_de(mundo)
            efeito = efeitos_da_condicao(None, self.cfg_frutas, mundo.condicao)
            return lambda politica, cfg, semente: classe(MotorMundo)(politica, cfg, semente, temperamento, "brasa",
                                                                     obediencia_desligada=True, semente_genoma=espec.genoma,
                                                                     cfg_mundo=cm, efeito_frutas=efeito, **kc)
        if mundo.frutas:
            # o desenho do N4 (plano, secao 3): MotorFrutas, obediencia, educacao, lesoes e bola desligadas, especie brasa; o genoma
            # das frutas (preferencia inata, neofobia) sai do genoma da vida, ou da semente sem genoma (o padrao do MotorFrutas)
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cf, ci, condicao = self.cfg_frutas, self.cfg_informacao, mundo.condicao
            troca = self.tick_troca if condicao == "mutavel" else None
            # N7: a chave do pedido so no motor dos bracos com pedido (com ela o estado() ganha pedido e desobediencias; nos outros, o
            # motor de hoje, e um pedido no registro falha alto)
            cp = self.cfg_pedido if braco_de(espec.braco).pedido else None
            # K4: com o julgamento, o motor dos bracos com fonte dono expoe os consumos (estado()["consumos_frutas"]) para o julgador
            cj = CONFIG_JULGAMENTO_FORA if self.julga_fruta(espec) else None
            # P1-c-tapaX (A1.1): o DonoTapaFruta le os consumos pelo mesmo estado()["consumos_frutas"] (a chave so os expoe)
            if braco_de(espec.braco).gestos == "tapa_fruta":
                cj = CONFIG_JULGAMENTO_FORA
            return lambda politica, cfg, semente: classe(MotorFrutasMundo)(
                politica, cfg, semente, temperamento, "brasa", obediencia_desligada=True, cfg_bola=CONFIG_BOLA, cfg_frutas=cf,
                semente_genoma=espec.genoma, condicao=condicao, tick_troca=troca, cfg_informacao=ci, cfg_pedido=cp,
                cfg_julgamento=cj, **kc)
        if mundo.bola is not None:
            # o desenho da A1 (plano, secao 3): MotorAmbiente, obediencia, educacao e lesoes desligadas, especie brasa
            temperamento = NEUTRO if espec.genoma is None else sortear_temperamento(espec.genoma)
            cb = self.cfg_bola
            return lambda politica, cfg, semente: classe(MotorAmbiente)(politica, cfg, semente, temperamento, "brasa",
                                                                        obediencia_desligada=True, cfg_bola=cb, **kc)
        if espec.genoma is None:
            return lambda politica, cfg, semente: classe(MotorComFeedback)(politica=politica, cfg=cfg, semente=semente, **kc)
        temperamento = sortear_temperamento(espec.genoma)
        if braco_de(espec.braco).regime is not None:
            # corpo (W-BANCADA-CORPO): nos bracos do plano do corpo, hoje e quimica, a obediencia fica desligada no padrao com genoma,
            # como nos mundos da bola e das frutas (o corpo a exige, secao 2): o par G-HOJE difere so na quimica
            return lambda politica, cfg, semente: classe(MotorPersonalidade)(politica, cfg, semente, temperamento,
                                                                             obediencia_desligada=True, **kc)
        return lambda politica, cfg, semente: MotorPersonalidade(politica, cfg, semente, temperamento)

    # ------------------------------------------------------------- vidas

    def vida(self, espec: EspecVida) -> VidaBancada:
        mundo = mundo_de(espec.mundo)
        if (espec.lugar is not None) != (mundo.fisico is not None):
            raise ValueError(f"{espec.nome}: o lugar do dono existe so no mundo fisico, e la e obrigatorio")
        b = braco_de(espec.braco)
        if b.gestos is not None and (mundo.fisico is not None or mundo.bola == "a1"):
            raise ValueError(f"{espec.nome}: os gestos do dono (DonoComGestos) ficam fora do mundo fisico e do bola_a1 (o plano do corpo "
                             "nao os usa la; o mundo fisico tem o dono so com o cuidado, PMF-3)")
        if b.gestos == "tapa_fruta" and not mundo.frutas:
            raise ValueError(f"{espec.nome}: o tapa na fruta X precisa de um mundo das frutas")
        fm = self.fabrica_motor(espec)
        rotulo = f"{espec.dono}-{espec.braco}"
        dono_ = self.dono(espec)
        canal = CanalComGestos if b.gestos is not None else CanalDeInteracao   # o SemGesto gasta o orcamento sem ir ao motor
        broncas = 0                              # N7: as broncas do pedido (so no P3+ped), que vem pelo canal do mundo
        julgamentos = 0                          # K4: os julgamentos da fruta, tambem pelo canal do mundo
        retirados = 0                            # mundo fisico: os sinais que o filtro sem_ensino ao vivo nao deixou chegar (PMF-3)
        carinhos = 0                             # banheiro: os carinhos depois do banheiro, pelo canal do mundo (fora do orcamento)
        if mundo.fisico is not None:
            if espec.lugar not in ESTILOS_LUGAR:
                raise ValueError(f"lugar {espec.lugar!r}: so {ESTILOS_LUGAR}")
            # o dono da v1 com o alimentar no lugar do estilo (a rng dono-lugar sem o braco) e so com o cuidado
            dono = DonoComLugar(criar_dono(espec.dono), espec.lugar, espec.semente, espec.dono, self.cfg_mundo_de(mundo))
            # banheiro (#265): nos bracos com carinho (B0C, BLC), o DonoCarinhoBanheiro, fora do orcamento (BN-2)
            carinho = DonoCarinhoBanheiro() if b.banheiro is not None and BRACOS_BANHEIRO[b.banheiro][1] else None
            motor, retirados = simular_vida_fisico(dono, self.politica(espec, CONFIG_PADRAO), espec.semente, self.dias,
                                                   self.orcamento, espec.dono, fm, carinho=carinho)
            carinhos = 0 if carinho is None else carinho.feitos
        elif mundo.bola == "a1":
            # como a A1 rodou: o dono embrulhado poe a bola DENTRO do orcamento; o aleatorio sorteia por_bola
            v = simular_vida(rotulo, DonoComBola(espec.dono, self.cfg_bola), self.politica(espec, CONFIG_PADRAO),
                             espec.semente, self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm)
            motor = v.motor
        elif mundo.bola == "b1b2":
            motor = simular_vida_mundo(dono_, RegraBola(espec.dono, self.cfg_bola),
                                       self.politica(espec, CONFIG_PADRAO), espec.semente, self.dias, self.orcamento,
                                       espec.dono, fm, canal_classe=canal)
        elif mundo.frutas:
            regra = CalendarioFrutas(espec.semente, self.cfg_frutas)
            julga = RegraFrutasComJulgador(regra, self.julgador(espec)) if self.julga_fruta(espec) else None
            regra = julga or regra
            if b.fonte == "informacao" and b.informacao != "depois":     # o P2d nao tem o informante da oferta: o julgador e o dele
                regra = RegraFrutasComInformante(regra, self.informante(espec))
            if b.pedido:
                regra = RegraFrutasComPedinte(regra, self.pedinte(espec))
            motor = simular_vida_mundo(dono_, regra, self.politica(espec, CONFIG_PADRAO), espec.semente,
                                       self.dias, self.orcamento, espec.dono, fm, canal_classe=canal)
            broncas = len(regra.pedinte.broncas) if b.pedido else 0
            # so o julgamento como feedback (elogiar/repreender) e julgamento; como informacao, conta em `informacoes` (o log)
            julgamentos = julga.feitos if julga is not None and julga.julgador.saida == "feedback" else 0
        else:
            # com os gestos, o treino.simular_vida com o CanalComGestos (a mesma rng do dono)
            simular = simular_vida_gestos if b.gestos is not None else simular_vida
            motor = simular(rotulo, dono_, self.politica(espec, CONFIG_PADRAO), espec.semente,
                            self.dias, self.orcamento, rotulo_dono=espec.dono, fabrica_motor=fm).motor
        gestos = None
        if b.gestos is not None:
            gestos = dict(dono_.trocas)
            retirados = gestos["sem_gesto"]      # a bronca do modo sem tapa gasta o orcamento e nao chega ao log
            if isinstance(dono_, DonoTapaFruta):
                gestos.update({"fruta_x": dono_.fruta, "tapas_fruta": len(dono_.tapas), "descartados": len(dono_.descartados)})
        dono, eventos_mundo = contar_acoes(motor.log)
        dono += contar_gestos_mundo(motor.log)   # o deixar_comida e o deixar_bola do mundo fisico gastam o orcamento (0 nos outros)
        dono -= broncas + julgamentos + carinhos    # a bronca do pedido, o julgamento e o carinho do banheiro estao no log, mas vieram
        #                                           pelo mundo
        orcamento_gasto = dono + (eventos_mundo if mundo.bola == "a1" else 0) + retirados
        if orcamento_gasto != self.orcamento:
            raise RuntimeError(f"{espec.nome}: {orcamento_gasto} interacoes no orcamento, orcamento {self.orcamento}")
        vida = VidaBancada(espec, motor, dono, broncas=broncas, julgamentos=julgamentos, retirados=retirados, gestos=gestos,
                           carinhos=carinhos)
        self.conferir_replay(vida)
        return vida

    def dono(self, espec: EspecVida):
        """O dono da vida: o da v1 (criar_dono); nos bracos com gestos, dentro do DonoComGestos (o modo "tapa" no bloco do tapa; o "sem
        tapa" nos outros) e, no P1-c-tapaX, ainda dentro do DonoTapaFruta. A rng e a de sempre: o mesmo dono nos dois modos."""
        base = criar_dono(espec.dono)
        g = braco_de(espec.braco).gestos
        if g is None:
            return base
        base = DonoComGestos(base, "tapa" if g == "tapa" else "sem_tapa")
        return DonoTapaFruta(base, fruta_tapa(espec.semente)) if g == "tapa_fruta" else base

    def efeitos_reais(self, espec: EspecVida) -> dict:
        """o efeito real de cada fruta no mundo da vida (E7: o que o dono informante sabe): {"antes": ..., "depois": ...}; "depois"
        so no mutavel (o descasado, a partir de tick_troca)"""
        mundo = mundo_de(espec.mundo)
        if not mundo.frutas:
            raise ValueError(f"sem frutas no mundo {espec.mundo!r}")
        g = genoma_frutas(espec.semente if espec.genoma is None else espec.genoma, self.cfg_frutas)
        if mundo.condicao == "mutavel":
            return {"antes": efeitos_da_condicao(g, self.cfg_frutas, "casado"),
                    "depois": efeitos_da_condicao(g, self.cfg_frutas, "descasado")}
        return {"antes": efeitos_da_condicao(g, self.cfg_frutas, mundo.condicao), "depois": None}

    def informante(self, espec: EspecVida):
        """o informante do braco: P2 `certo`, P2e `errado` (DonoInformante de frutas.py, com o efeito real do mundo da bancada) e P2a
        acoplado (InformanteAcoplado: o multiconjunto do P2 em ticks sorteados)"""
        b = braco_de(espec.braco)
        if b.fonte != "informacao":
            raise ValueError(f"braco {b.rotulo} nao tem informante")
        ef = self.efeitos_reais(espec)
        troca = self.tick_troca if ef["depois"] is not None else None
        if b.informacao == "acoplada":
            return InformanteAcoplado(espec.semente, self.dias, self.cfg_frutas, ef, troca)
        if b.informacao == "depois":
            raise ValueError(f"braco {b.rotulo}: a informacao dele e o julgador com saida informacao (Bancada.julgador), nao um informante")
        modo = {"certa": "certo", "errada": "errado"}[b.informacao]
        return InformanteDoMundo(modo, ef, troca)

    def julga_fruta(self, espec: EspecVida) -> bool:
        """K4: o dono desta vida julga a fruta? Nos mundos das frutas: os bracos com fonte dono (o P3, o P3i, o P3+ped) com a chave
        julgamento_fruta; o P2d sempre (o julgador com saida "informacao" e o informante dele, P2D-P3I)."""
        if not mundo_de(espec.mundo).frutas:
            return False
        b = braco_de(espec.braco)
        return b.informacao == "depois" or (self.julgamento_fruta and b.fonte == "dono")

    def saida_julgamento(self, espec: EspecVida) -> str:
        """A saida do JulgadorFruta da vida: "informacao" no P2d e no P3i (P2D-P3I, parte A), "feedback" (o K4) nos outros."""
        b = braco_de(espec.braco)
        return "informacao" if (b.informacao == "depois" or b.julgamento == "informacao") else "feedback"

    def julgador(self, espec: EspecVida) -> JulgadorFruta:
        """K4 (contrato K4, E7): o conhecimento do dono do P3 sao os efeitos reais da bancada, os mesmos que o informante do P2 recebe
        (e a troca do mutavel); o julgamento sai fora do orcamento (CONFIG_JULGAMENTO_FORA)."""
        if not self.julga_fruta(espec):
            raise ValueError(f"{espec.nome}: sem julgamento da fruta (chave julgamento_fruta, mundo das frutas, braco com fonte dono "
                             "ou o P2d)")
        ef = self.efeitos_reais(espec)
        troca = self.tick_troca if ef["depois"] is not None else None
        return JulgadorFruta(ef["antes"], ef["depois"], troca, CONFIG_JULGAMENTO_FORA, saida=self.saida_julgamento(espec))

    def pedinte(self, espec: EspecVida) -> DonoPedinte:
        """N7: o dono que pede da unidade (a fruta X pela semente, N7-6), com a bronca da desobediencia so no P3+ped (fonte dono, N7-8)."""
        b = braco_de(espec.braco)
        if not b.pedido:
            raise ValueError(f"braco {b.rotulo} nao tem pedido")
        return DonoPedinte.da_semente(espec.semente, self.cfg_pedido, bronca=b.fonte == "dono")

    def rejogar(self, log: LogDeEventos, espec: EspecVida):
        fp, fm = self.fabrica_politica(espec), self.fabrica_motor(espec)
        if mundo_de(espec.mundo).fisico is not None:
            return reproduzir_mundo(log, fp, semente=espec.semente, fabrica_motor=fm)
        if mundo_de(espec.mundo).ambiente:
            return reproduzir_ambiente(log, fp, semente=espec.semente, fabrica_motor=fm)
        return reproduzir_com_feedback(log, fp, semente=espec.semente, fabrica_motor=fm)

    def acoplar(self, origem: VidaBancada, braco: str, filtro: str) -> VidaBancada:
        """Modo acoplado (malha aberta): o registro da vida de origem, sem as acoes do filtro, rejogado com o cerebro de outro
        braco (ou do mesmo). Os eventos sao os da origem nos mesmos ticks; so o cerebro (e o que ele faz deles) muda."""
        retirar = filtro_de(filtro)
        if origem.origem is not None:
            raise ValueError("acoplar uma vida ja acoplada nao e suportado: acople a partir da vida de origem")
        log = filtrar_log(origem.motor.log, retirar)
        espec = replace(origem.espec, braco=braco)
        m = self.rejogar(log, espec)
        # as broncas do pedido e os julgamentos da fruta (feedback pelo canal do mundo) ficam no registro so se o filtro nao tira os
        # sinais; um filtro que tirasse so um dos dois deixaria a conta sem como separar o que veio do dono
        if (origem.broncas or origem.julgamentos) and len(JULGAMENTOS & retirar) == 1:
            raise ValueError(f"filtro {filtro!r} tira so parte dos sinais: as broncas e os julgamentos da origem nao se separam")
        fica = not (JULGAMENTOS & retirar)
        broncas, julgamentos = (origem.broncas, origem.julgamentos) if fica else (0, 0)
        vida = VidaBancada(espec, m, contar_acoes(log)[0] + contar_gestos_mundo(log) - broncas - julgamentos, origem=origem.nome,
                           origem_braco=origem.rotulo_braco, filtro=filtro, broncas=broncas, julgamentos=julgamentos)
        self.conferir_replay(vida)
        return vida

    def conferir_replay(self, vida: VidaBancada, texto_log: str | None = None) -> None:
        """G1: rejoga a vida a partir do log serializado (do disco, se vier o texto) e compara tudo bit a bit."""
        texto = vida.motor.log.para_jsonl() if texto_log is None else texto_log
        if texto != vida.motor.log.para_jsonl():
            raise ReplayDivergiu(f"{vida.nome}: o log do disco nao e o da vida")
        r = self.rejogar(LogDeEventos.de_jsonl(texto), vida.espec)
        if resumo_motor(r) != resumo_motor(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: log, estado, acoes ou rngs divergem no replay")
        if _interno(r) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: estado interno da politica diverge no replay")

    # ------------------------------------------------------------- medidas

    def medir(self, vida: VidaBancada, sonda: dict, piso: float | None = None, taxa_p0: float | None = None) -> dict:
        """Desempenho no ambiente, acerto na tarefa e custo da plasticidade de uma vida. `piso` = acerto total do P0 na mesma
        celula (o prior herdado); sem ele, o da propria vida. O replay de medicao e conferido bit a bit contra a vida."""
        regs = []

        def fab(cfg=None):
            reg = _Registro(self.politica(vida.espec, cfg))
            regs.append(reg)
            return reg

        fisico = mundo_de(vida.espec.mundo).fisico is not None
        repro = reproduzir_mundo if fisico else reproduzir_com_feedback     # o mundo fisico tem eventos proprios no log
        fm_base = self.fabrica_motor(vida.espec)
        sonda_metab: list = []

        def fm(*a, **kw):
            """o motor de sempre; com o metabolismo, uma sonda so de leitura no passo do corpo (a medida descritiva, A3.3)"""
            motor = fm_base(*a, **kw)
            corpo = getattr(motor, "corpo", None)
            if corpo is not None and corpo.cc.metabolismo:
                sondar_metabolismo(corpo, sonda_metab)
            return motor

        m = repro(LogDeEventos.de_jsonl(vida.motor.log.para_jsonl()), fab, semente=vida.espec.semente, fabrica_motor=fm)
        if resumo_motor(m) != resumo_motor(vida.motor) or _interno(m) != _interno(vida.motor):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao mudou a vida")
        reg = regs[0]
        reg.metabolismo = sonda_metab
        bola = None
        if isinstance(m, MotorAmbiente) and not fisico:
            tick = CONFIG_PADRAO.intervalo_decisao_ticks
            bola = {"resposta": resposta_a_bola([(k * tick, b, r, a) for k, (b, r, a) in enumerate(reg.bola)]),
                    "contagem": dict(m.contagem_bola)}
        frutas = None
        if isinstance(m, MotorFrutasMundo):
            consumos = [(c["tick"], c["efeito_humor"]) for c in m.consumos]
            taxas = taxa_fruta_ruim(consumos, self.janelas_frutas(m.condicao))
            dias = [taxas[f"dia_{d + 1}"] for d in range(self.dias)]
            if taxa_p0 is None and vida.espec.braco == "P0" and vida.origem is None:
                taxa_p0 = taxas["total"]["taxa"]                    # o P0 e a propria referencia
            if m.condicao == "iguais":
                taxa_p0 = None                                      # sem fruta ruim, sem caminho ate a metade (sem_referencia)
            frutas = {"taxa_fruta_ruim": taxas, "consumos": len(consumos), "contagem": dict(m.contagem_frutas),
                      "mundo": m.resumo_mundo(), "genoma": m.genoma.para_dict(),
                      "consumos_ate_metade": consumos_ate_metade([x["taxa"] for x in dias], [x["n"] for x in dias], taxa_p0),
                      "informacoes": [dict(i) for i in m.informacoes],
                      "multiconjunto_informacoes": multiconjunto_informacoes(m.informacoes),
                      "decisoes_com_informacao": m.decisoes_com_informacao}
        n6 = self.medidas_n6(vida, m, reg) if isinstance(m, MotorFrutasMundo) else None
        n7 = self.medidas_n7(vida, m, reg) if isinstance(m, MotorFrutasMundo) else None
        extra_mundo = ({"lugar": vida.espec.lugar, "retirados": vida.retirados, "mundo_fisico": self.medidas_mundo(vida, m, reg)}
                       if fisico else {})
        dominancia = self.medidas_dominancia(vida, reg)
        corpo = self.medidas_corpo(vida, m, reg)
        if corpo is not None and m.cc.metabolismo:
            corpo["metabolismo"] = self.medidas_metabolismo(vida, m, reg)
        banheiro = self.medidas_banheiro(vida, m, reg) if braco_de(vida.espec.braco).banheiro is not None else None
        desempenho = desempenho_no_ambiente(reg.amostras)
        humor = privacao_nas_decisoes(reg.vetores, CONFIG_PADRAO.limiar_privacao)["humor_medio"]
        tarefa = acerto_na_tarefa(reg.decisoes, _julgar, ACOES, TICKS_POR_DIA)
        sinais = []
        for d in tarefa["dias"]:
            ate = [s for (t, _, _), s in zip(reg.decisoes, reg.sinais_na_decisao) if t < (d + 1) * TICKS_POR_DIA]
            sinais.append(ate[-1] if ate else 0)
        deriva = self.deriva(vida, sonda)
        custo = custo_da_plasticidade(deriva, tarefa["acerto"], sinais,
                                      tarefa["acerto_total"] if piso is None else piso)
        return {"vida": vida.nome, "braco": vida.rotulo_braco, "fonte": braco_de(vida.espec.braco).fonte,
                "cerebro": vida.espec.cerebro, "dono": vida.espec.dono, "semente": vida.espec.semente,
                "genoma": vida.espec.genoma, "mundo": vida.espec.mundo, "condicao": vida.espec.condicao,
                "origem": vida.origem, "filtro": vida.filtro, "interacoes": vida.interacoes,
                "eventos_mundo": vida.eventos_mundo, "informacoes": vida.informacoes, "bola": bola, "frutas": frutas,
                "pedidos": vida.pedidos, "broncas": vida.broncas, "julgamentos": vida.julgamentos, "n6": n6, "n7": n7,
                "humor_medio": humor,
                **desempenho, "acerto_total": tarefa["acerto_total"], "acerto_por_dia": tarefa["acerto"],
                "teto_total": tarefa["teto_total"], "sinais_total": reg.sinais, "sinais_do_dono": reg.sinais_do_dono,
                "sinais_acumulados": sinais,
                "deriva_final": custo["deriva_final"], "custo_da_plasticidade": custo, "dominancia": dominancia, "corpo": corpo, "banheiro": banheiro,
                **extra_mundo}

    def medidas_corpo(self, vida: VidaBancada, motor, reg: "_Registro") -> dict | None:
        """As medidas do PLANO_ANALISE_V2_CORPO_DRIVES (secao 5), todas de metrics.py, nas vidas com o corpo ligado (None nas outras). A
        janela e a dos ultimos sete dias (os dias 8 a 14 numa vida de 14), e a vida toda sai ao lado na `BE`:
          - `BE` e `OC` (5.1): (tick, regra do instinto, acao) de cada decisao do replay de medicao;
          - o cuidado preservado (5.2): (tick, em privacao, saude, fome) de cada decisao, a privacao pela Estado.em_privacao;
          - os drives novos (5.3): a falta lida pelo receptor, na escala 0-1, de cada decisao, quando o corpo tem receptores novos;
            sem eles (o regime "quimica"), sai indisponivel, com o no."""
        cc = getattr(motor, "cc", None)
        if cc is None or not cc.ligada:
            return None
        if len(reg.corpo) != len(reg.decisoes) or any(pc is None for pc in reg.corpo):
            raise RuntimeError(f"{vida.nome}: o corpo ligado e decisao sem os receptores (Observacao.corpo)")
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        fim = self.dias * TICKS_POR_DIA
        ticks = [t for t, _, _ in reg.decisoes]
        decs = [(t, regra, a) for (t, _, a), (_, regra, _) in zip(reg.decisoes, reg.bola)]
        cuidado = [(t, p, sau, v[1]) for t, (p, sau), v in zip(ticks, reg.amostras, reg.vetores)]
        S = self.cfg_lobos.escala
        novos = [r for r in RECEPTORES_NOVOS if r in DRIVES_NOVOS_SINAL and getattr(reg.corpo[0], r) is not None]
        if novos:
            amostras = [(t, a, {r: getattr(pc, r) / S for r in novos}) for t, a, pc in zip(ticks, reg.acordado, reg.corpo)]
            drives = {"disponivel": True, "janela": medir_drives_novos(amostras, janela),
                      "vida_toda": medir_drives_novos(amostras, (0, fim))}
        else:
            drives = {"disponivel": False, "motivo": "o corpo sem receptores novos (o regime quimica, sem drives_novos)"}
        return {"regime": braco_de(vida.espec.braco).regime, "janela": list(janela), "gestos": vida.gestos,
                "be": tempo_livre_be(decs, janela), "be_vida": tempo_livre_be(decs, (0, fim)),
                "cuidado": cuidado_preservado(cuidado, janela), "drives_novos": drives,
                "corpo_final": motor.corpo.para_dict()}

    def medidas_metabolismo(self, vida: VidaBancada, motor, reg: "_Registro") -> dict:
        """A medida descritiva do metabolismo (PLANO_ANALISE_V2_CORPO_DRIVES, A3.3; TAREFA_V2_METABOLISMO, secao 6), por vida, so relato:
          - a fracao do tempo acordado com a falta de combustivel (abaixo de `falta_limiar`, C/4) e as vezes que a falta disparou, tick a
            tick, pela sonda do passo do corpo no replay de medicao (`sondar_metabolismo`);
          - o combustivel e a reserva no fim de cada dia;
          - o tempo entre comer e brincar (as decisoes do replay; o plano o pede no P1-c, e sai em toda vida com o metabolismo).
        A conta do corpo no fim (`contas_metabolismo`) sai ao lado; a sonda tem de ter um tick por tick vivido (falha alto)."""
        sonda = getattr(reg, "metabolismo", None)
        fim = self.dias * TICKS_POR_DIA
        if not sonda or len(sonda) != motor._estado.tick or [t for t, *_ in sonda] != list(range(motor._estado.tick)):
            raise RuntimeError(f"{vida.nome}: a sonda do metabolismo nao cobre a vida tick a tick")
        decs = [(t, a) for t, _, a in reg.decisoes]
        return {**metabolismo_da_vida(sonda, motor.cc.falta_limiar, TICKS_POR_DIA), "tempo_comer_brincar": tempo_comer_brincar(decs),
                "contas": dict(motor.corpo.contas_metabolismo), "fim": fim}

    def medidas_dominancia(self, vida: VidaBancada, reg: "_Registro") -> dict:
        """Adendo 2 do plano do corpo (A2.2), numa vida: por decisao observada, c_d = falta_d,antes^2 - falta_d,depois^2 por drive do
        sinal (os de ConfigConsequencia.drives; na decisao que comeu fruta, mais o humor com a E2, e o depois e o estado logo depois de
        comer), com as faltas na escala S do sinal (S - arred(h * S)) e w_d = 1 (D-4). Nos bracos que aprendem pela consequencia, e o
        sinal deles ("sinal"); nos outros, a mesma conta como sonda ("sonda"). Com os canais ligados e o aprendizado ligado, a soma por
        canal dos sinais recalculados daqui (lobos.sinal_por_canal, a mesma ordem dos drives) tem de ser o total que o cerebro guardou:
        se nao for, falha alto. A janela e a dos ultimos sete dias (os dias 8 a 14 numa vida de 14), e a vida toda sai ao lado."""
        b = self.braco(vida.espec)
        cerebro = reg.interna.cerebro
        cc = getattr(reg.interna, "cfg_consequencia", self.cfg_consequencia)
        S = self.cfg_lobos.escala
        if reg.passos_sinal and reg.passos_sinal[0]["antes_corpo"] is not None:
            return self._dominancia_pelo_corpo(vida, reg, b, cerebro, cc, S)
        acao_drives = tuple(cc.drives)
        fruta_drives = acao_drives + ((INDICE_HUMOR,) if cc.humor_na_fruta and INDICE_HUMOR not in acao_drives else ())
        falta = lambda v, ds: {NOMES_DRIVES[i]: S - arred(v[i] * S) for i in ds}  # noqa: E731
        janela = cc.pesos_janela and getattr(cerebro, "_aprende", False)
        indice_do_canal = {c: i for i, c in CANAL_DO_DRIVE.items()}
        decisoes, por_canal = [], {}
        for p in reg.passos_sinal:
            ds = fruta_drives if comeu_fruta_e2(p) else acao_drives
            pesos = None
            if janela:                  # P1-cw (A2.4): os pesos que o cerebro usou nesta decisao, o mesmo no antes e no depois
                anotados = cerebro.motivos[p["k"]].get("pesos_janela")
                if anotados is None:
                    raise RuntimeError(f"{vida.nome}: decisao {p['k']} sem os pesos da janela no motivo")
                pesos = {indice_do_canal[c]: w for c, w in anotados.items()}
                if not set(ds) <= set(pesos):      # o cerebro pesa os drives da E2 em toda decisao; a acao so usa os do N3
                    raise RuntimeError(f"{vida.nome}: os pesos da janela {sorted(pesos)} nao cobrem os drives do sinal {sorted(ds)}")
                pesos = {i: pesos[i] for i in ds}
            w_d = None if pesos is None else {NOMES_DRIVES[i]: w for i, w in pesos.items()}
            decisoes.append((p["tick"], p["regra"],
                             contribuicao_drives(falta(p["antes"], ds), falta(p["depois"], ds), w_d, escala=S)))
            for canal, f in sinal_por_canal(p["antes"], p["depois"], ds, cc.ganho, S, pesos).items():
                por_canal[canal] = por_canal.get(canal, 0) + f
        canais = getattr(cerebro, "_canais", None)
        conferido = False
        if b.fonte in APRENDE_PELA_CONSEQUENCIA and cc.canais_ligados and getattr(cerebro, "_aprende", False):
            if canais is None or canais["creditos"] != len(reg.passos_sinal):
                raise RuntimeError(f"{vida.nome}: o cerebro creditou {None if canais is None else canais['creditos']} decisoes, "
                                   f"a medida viu {len(reg.passos_sinal)}")
            if any(canais["por_canal"].get(c, 0) != v for c, v in por_canal.items()):
                raise RuntimeError(f"{vida.nome}: o sinal por drive da medida e o dos canais do cerebro divergem")
            conferido = True
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        return {"origem": "sinal" if b.fonte in APRENDE_PELA_CONSEQUENCIA else "sonda", "conferido_com_canais": conferido,
                "janela": list(janela), "na_janela": dominancia_decisoes(decisoes, janela),
                "vida_toda": dominancia_decisoes(decisoes, (0, self.dias * TICKS_POR_DIA))}

    def _dominancia_pelo_corpo(self, vida: VidaBancada, reg: "_Registro", b: Braco, cerebro, cc: ConfigConsequencia, S: int) -> dict:
        """A dominancia (A2.2) com o corpo ligado: a conta do sinal pelo corpo (`lobos.contribuicoes_corpo`, secao 9 da tarefa), sobre
        os receptores da decisao e os de depois dos estimulos da propria acao (o gancho `consequencia_corpo`), com os w_d inteiros da
        `ConfigConsequencia.pesos_drives_corpo` e, com a `pesos_janela`, o peso da janela do motivo. Os drives: os do N3, o humor so no
        comer de fruta (E2) e os novos que o corpo tiver (o susto fora), pelos nomes do corpo. Nos bracos que aprendem pela consequencia,
        a contribuicao de cada decisao tem de ser a que o cerebro gravou no motivo (`sinal_corpo`) e, com os canais, a soma por canal a dos
        canais dele: se nao for, falha alto."""
        nomes = {"fome": "fome", "higiene": "desconforto", "energia": "cansaco", "humor": "tristeza"}
        pd = dict(cc.pesos_drives_corpo)
        aprende = (b.fonte in APRENDE_PELA_CONSEQUENCIA and getattr(cerebro, "_aprende", False)
                   and getattr(cerebro, "_corpo", None) is not None)
        decisoes, por_canal = [], {}
        for p in reg.passos_sinal:
            antes, depois = p["antes_corpo"], p["depois_corpo"]
            if antes is None or depois is None:
                raise RuntimeError(f"{vida.nome}: decisao {p['k']} sem os receptores de antes ou de depois (o gancho do corpo)")
            drives = tuple(RECEPTOR_DO_INDICE[i] for i in cc.drives)
            if comeu_fruta_e2(p) and cc.humor_na_fruta and "humor" not in drives:
                drives = drives + ("humor",)
            drives = drives + tuple(r for r in RECEPTORES_NOVOS if r in DRIVES_NOVOS_SINAL and getattr(antes, r) is not None)
            pesos = None
            motivo = cerebro.motivos[p["k"]] if aprende else None
            if aprende and cc.pesos_janela:
                anotados = motivo.get("pesos_janela")
                if anotados is None or not set(drives) <= set(anotados):
                    raise RuntimeError(f"{vida.nome}: decisao {p['k']} sem os pesos da janela dos drives {drives} no motivo")
                pesos = {d: anotados[d] for d in drives}
            c = contribuicoes_corpo(antes, depois, drives, S, pd, pesos)
            if aprende and motivo.get("sinal_corpo", {}).get("drives") != c:
                raise RuntimeError(f"{vida.nome}: decisao {p['k']}: a contribuicao da medida e a do cerebro divergem")
            decisoes.append((p["tick"], p["regra"], {nomes.get(d, d): v for d, v in c.items()}))
            for canal, f in sinal_corpo_canais(antes, depois, drives, cc.ganho, S, pd, pesos).items():
                por_canal[canal] = por_canal.get(canal, 0) + f
        canais = getattr(cerebro, "_canais", None)
        conferido = False
        if aprende and cc.canais_ligados:
            if canais is None or canais["creditos"] != len(reg.passos_sinal):
                raise RuntimeError(f"{vida.nome}: o cerebro creditou {None if canais is None else canais['creditos']} decisoes, "
                                   f"a medida viu {len(reg.passos_sinal)}")
            if any(canais["por_canal"].get(c, 0) != v for c, v in por_canal.items()):
                raise RuntimeError(f"{vida.nome}: o sinal por drive da medida e o dos canais do cerebro divergem")
            conferido = True
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        return {"origem": "sinal" if b.fonte in APRENDE_PELA_CONSEQUENCIA else "sonda", "conferido_com_canais": conferido,
                "conferido_com_motivo": bool(aprende), "pelo_corpo": True, "janela": list(janela),
                "na_janela": dominancia_decisoes(decisoes, janela),
                "vida_toda": dominancia_decisoes(decisoes, (0, self.dias * TICKS_POR_DIA))}

    def medidas_banheiro(self, vida: VidaBancada, motor, reg: "_Registro") -> dict:
        """As medidas do PLANO_ANALISE_V2_BANHEIRO (secoes 4 e 8) numa vida do 2 x 2, pela `medidas_banheiro_de`. Le:
          - do motor (o contrato da etapa 3 do A, conferido aqui): `motor.alivios`, um dict por `aliviar`, com `tick` (o da decisao),
            `dentro` (terminou dentro do banheiro), `urgente` (a regra urgente, o acidente), `alvo` ("banheiro" ou "aqui"),
            `distancia` (do pet ao banheiro na decisao, em subunidades) e `recolhido` (o limpador recolheu a necessidade);
          - do replay de medicao (_Registro): os carinhos (`mudanca_no_corpo`: o tick, a solidao antes e o sinal pelo corpo, a conta do
            cerebro) e a transicao de cada decisao (o sinal do alivio recolhido pelo limpador, a mesma conta) e o cuidado de cada decisao;
          - do cerebro no fim de cada dia (o replay do mundo cortado no dia): os pesos do alvo `banheiro` e `aqui`."""
        alivios = getattr(motor, "alivios", None)
        if alivios is None:
            raise NotImplementedError(f"{vida.nome}: o motor sem os alivios ({NOS_PENDENTES.get('banheiro', 'a etapa 3 do banheiro')})")
        chaves = {"tick", "dentro", "urgente", "alvo", "distancia", "recolhido"}
        if any(set(a) != chaves for a in alivios):
            raise RuntimeError(f"{vida.nome}: alivio fora do contrato {sorted(chaves)}")
        cc = getattr(reg.interna, "cfg_consequencia", self.cfg_consequencia)
        S = self.cfg_lobos.escala
        pd = dict(cc.pesos_drives_corpo)
        # os drives do sinal pelo corpo, como na dominancia: os do N3 e os novos que o corpo tem (o susto fora); a conta do cerebro
        drives = lambda r: tuple(RECEPTOR_DO_INDICE[i] for i in cc.drives) + tuple(  # noqa: E731
            x for x in RECEPTORES_NOVOS if x in DRIVES_NOVOS_SINAL and getattr(r, x) is not None)
        sinal = lambda antes, depois: sinal_corpo(antes, depois, drives(antes), cc.ganho, S, pd)  # noqa: E731
        carinhos = [(t, antes.solidao / S, sinal(antes, depois)) for t, antes, depois in reg.carinhos]
        por_tick = {p["tick"]: p for p in reg.passos_sinal}
        limpador = []
        for a in alivios:
            if a["recolhido"]:
                p = por_tick.get(a["tick"])
                if p is None or p["antes_corpo"] is None or p["depois_corpo"] is None:
                    raise RuntimeError(f"{vida.nome}: alivio recolhido no tick {a['tick']} sem a decisao e os receptores dela")
                limpador.append((a["tick"], sinal(p["antes_corpo"], p["depois_corpo"])))
        ticks = [t for t, _, _ in reg.decisoes]
        cuidado = [(t, p, sau, v[1]) for t, (p, sau), v in zip(ticks, reg.amostras, reg.vetores)]
        fab, fm, T = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec), TICKS_POR_DIA
        pesos = None                             # o instinto do alivio nao aprende o alvo (o herdado, sem pesos)
        if vida.espec.cerebro == "lobos":
            pesos = [do_braco(reproduzir_mundo(vida.motor.log, fab, semente=vida.espec.semente, fabrica_motor=fm, ate_tick=d * T)
                              .politica).cerebro.estado_interno()["pesos_alvo"] for d in range(1, self.dias + 1)]
        return medidas_banheiro_de([(a["tick"], a["dentro"], a["urgente"]) for a in alivios], self.dias, carinhos, limpador, pesos,
                                   cuidado, [(a["tick"], a["alvo"], a["dentro"], a["distancia"]) for a in alivios if not a["urgente"]])

    def medidas_mundo(self, vida: VidaBancada, motor: MotorMundo, reg: "_Registro") -> dict:
        """As medidas do PLANO_ANALISE_V2_MUNDO_FISICO (secao 5 e adendo 1, A1.8), todas de digilab/metrics.py, numa vida do mundo fisico.
        A janela e a dos ultimos sete dias (os dias 8 a 14 numa vida de 14; a vida toda se ela for mais curta), e a vida toda sai ao lado
        no D_FE. Do motor (os registros do MotorMundo): a posicao depois de cada decisao (`decisoes_mundo`, a trajetoria), os troncos, as
        quedas (o fluxo mundo-arvores: as `sorteadas`, que nao dependem do pet) e os consumos (a fome ganha); do replay de medicao
        (_Registro): o estado em cada decisao e se o pet estava acordado. As visitas recontadas pela metrica sao conferidas contra as que
        o motor registrou (`visitas`): uma diferenca falha alto."""
        fim = self.dias * TICKS_POR_DIA
        janela = janela_dias(max(1, self.dias - 6), self.dias)
        decs = motor.decisoes_mundo
        if len(decs) != len(reg.vetores):
            raise RuntimeError(f"{vida.nome}: {len(decs)} decisoes no mundo e {len(reg.vetores)} no replay de medicao")
        ticks = [d["tick"] for d in decs]
        fe = [(t, v[1], v[3]) for t, v in zip(ticks, reg.vetores)]                    # (tick, fome, energia) da decisao
        cuidado = [(t, p, s, v[1]) for t, (p, s), v in zip(ticks, reg.amostras, reg.vetores)]
        traj = [(d["tick"], d["x"], d["y"]) for d in decs]
        if not traj or traj[0][0] > 0:                                                # o nascimento, no ninho
            traj = [(0, *centro_da_celula(motor.cmf.layout.ninho, motor.cmf))] + traj
        arvores = {a["id"]: (a["x"], a["y"]) for a in motor.arvores}
        quedas = [q["tick"] for q in motor.quedas for _ in range(q["sorteadas"])]
        todas = visitas_manchas(traj, arvores, fim, (0, fim), quedas=quedas, raio_celulas=motor.cmf.raio_mancha_celulas)
        recontadas = sorted((v["arvore"], v["inicio"], v["fim"], v["decisoes_dentro"]) for v in todas if not v["censurada"])
        if recontadas != sorted((v["arvore"], v["chegada"], v["saida"], v["decisoes"]) for v in motor.visitas):
            raise RuntimeError(f"{vida.nome}: as visitas da metrica e as do motor divergem")
        visitas = [v for v in todas if janela[0] <= v["inicio"] < janela[1]]
        ganhos = [(c["tick"], c["fome_depois"] - c["fome_antes"]) for c in motor.consumos_mundo]
        horas = sum(reg.acordado) * CONFIG_PADRAO.intervalo_decisao_ticks / 60.0
        return {"janela": list(janela), "d_fe": deficit_fome_energia(fe, janela), "d_fe_vida": deficit_fome_energia(fe, (0, fim)),
                "cuidado": cuidado_preservado(cuidado, janela), "visitas": visitas,
                "permanencia_custo": inclinacao_permanencia(visitas, "custo_viagem"),
                "permanencia_taxa": inclinacao_permanencia(visitas, "taxa_recente"),
                "taxa_no_abandono": taxa_no_abandono(visitas, ganhos, horas), "permanencia_media": permanencia_media(visitas),
                "horas_acordado": horas, "deixadas": len(motor.deixadas), "consumos": len(motor.consumos_mundo),
                "quedas": len(motor.quedas)}

    def medidas_n6(self, vida: VidaBancada, motor, reg: "_Registro") -> dict | None:
        """N6 (plano, secoes 6 e 7), nos bracos de memoria: as sub-decisoes da fruta com a sonda contrafactual que o cerebro grava no
        motivo (`fruta.sonda_memoria`: a escolha com m = 0 e o mesmo u), a fracao decidida pela memoria (G-CITA), a cobertura, a
        ocupacao dos espacos por decisao e as verificacoes exatas dos marcos 1 e 2 (todo consumo virou um episodio da mesma fruta, na
        mesma ordem). Fora dos bracos de memoria, None."""
        if self.braco(vida.espec).memoria is None:      # na montagem completa, tambem P1 a P3 nos mundos das frutas
            return None
        cerebro = reg.interna.cerebro
        interno = cerebro.estado_interno()
        subs = []
        for mot in cerebro.motivos:
            fr = mot.get("fruta")
            if fr is None:
                continue
            mem = fr.get("memoria_emocao")
            if mem is None:
                raise RuntimeError(f"{vida.nome}: sub-decisao sem o registro da memoria com a memoria ligada")
            sonda = fr.get("sonda_memoria")
            if (sonda is None) != (len(fr["presentes"]) < 2):
                raise RuntimeError(f"{vida.nome}: a sonda da memoria tem de existir so com duas frutas ou mais")
            recuperados = sum(1 for v in mem.values() if v["episodio"] is not None)
            subs.append((len(fr["presentes"]), fr["escolhida"], sonda["escolha_sem_memoria"] if sonda else fr["escolhida"],
                         recuperados))
        r = memoria_nas_subdecisoes(subs, len(cerebro.motivos))
        contagem = interno["memoria"]["sondas"]
        if (r["subdecisoes_2_mais"], r["mudou"]) != (contagem["subdecisoes_2mais"], contagem["mudou"]):
            raise RuntimeError(f"{vida.nome}: as sondas do motivo e as contagens do cerebro divergem")
        episodios = interno["memoria"]["episodios"]
        consumos = motor.consumos
        return {**r, "modo": interno["memoria"]["modo"], "ganho": interno["memoria"]["ganho"],
                "ocupacao": ocupacao_espacos_frutas(reg.espacos, FRUTAS),
                "marcos": {"consumos": len(consumos), "episodios": len(episodios),
                           "episodio_por_consumo": [e["fruta"] for e in episodios] == [c["fruta"] for c in consumos],
                           "contagem": dict(interno["memoria"]["contagem"])}}

    def medidas_n7(self, vida: VidaBancada, motor, reg: "_Registro") -> dict | None:
        """N7 (plano, secao 6), nos bracos com pedido e nos acoplados a um deles: a fruta X da unidade, as decisoes de conflito com a sonda
        "quem decidiu" que o cerebro grava no motivo (`pedido.acao_sem_pedido`: a acao com o mesmo u e sem o termo), a deferencia por zona
        e janela (dias 1..metade e metade..dias_pedido do pedido; a extincao depois), as violacoes das regras urgentes (G-URG), a fracao
        de X nas ofertas com X e outra fruta, as desobediencias, e a trajetoria diaria de w_pedido com o dia em que cruza o zero. A decisao
        k cai no tick k x intervalo_decisao_ticks. Fora disso, None."""
        de_pedido = braco_de(vida.espec.braco).pedido or (vida.origem_braco is not None and
                                                          BRACOS.get(vida.origem_braco.split("<")[0], BRACOS["P0"]).pedido)
        if not de_pedido:
            return None
        cerebro = reg.interna.cerebro
        passo = CONFIG_PADRAO.intervalo_decisao_ticks
        T, cp = TICKS_POR_DIA, self.cfg_pedido
        fim, fim_pedidos = self.dias * T, min(cp.dias_pedido, self.dias) * T
        metade = min(cp.dias_pedido // 2, self.dias) * T
        janelas = {"inicial": (0, metade), "final": (metade, fim_pedidos), "extincao": (fim_pedidos, fim)}
        decisoes, consumos = [], []
        for k, mot in enumerate(cerebro.motivos):
            ped = mot.get("pedido")
            if ped is not None:
                decisoes.append((k * passo, mot["regra"], mot["regra"] in ZONAS_CONFLITO and ped["p"] == -1.0,
                                 mot["acao"] == AcaoPet.COMER.value, ped["acao_sem_pedido"] == AcaoPet.COMER.value))
            fr = mot.get("fruta")
            if fr is not None:
                consumos.append((k * passo, fr["escolhida"], fr["presentes"]))
        x = DonoPedinte.sortear_fruta(vida.espec.semente)
        estado = motor.estado()
        serie = None
        interno = cerebro.estado_interno()
        if "peso_pedido" in interno:
            if interno["aprendizado_ligado"]:
                fab, fm = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec)
                serie = [do_braco(politica_no_tick(vida.motor.log, fab, vida.espec.semente, d * T, fm)).cerebro
                         .estado_interno()["peso_pedido"] for d in range(1, self.dias + 1)]
            else:
                serie = [interno["peso_pedido"]] * self.dias
        return {"fruta_x": x, "janelas": janelas, "deferencia": deferencia_ao_pedido(decisoes, janelas),
                "fracao_x": fracao_da_fruta(consumos, x, janelas), "desobediencias": estado.get("desobediencias"),
                "pedidos": vida.pedidos, "broncas": vida.broncas, "w_pedido_por_dia": serie,
                "dia_w_pedido_cruza_zero": dia_cruza_zero(serie) if serie else None}

    def deriva(self, vida: VidaBancada, sonda: dict) -> list[float]:
        """JSD (bits) entre a politica no fim de cada dia e a do prior herdado (o P0 da mesma vida), nas mesmas sondas."""
        estados = estados_sonda(sonda["estados"], sonda["semente"])
        # corpo: o prior e o P0 do mesmo regime, e as sondas ganham os receptores do proprio estado (o cerebro com o corpo os exige)
        regime = braco_de(vida.espec.braco).regime
        p0 = {"quimica": "P0-quimica", "corpo": "P0-c"}.get(regime, "P0")
        corpo = self.cfg_corpo_de(vida.espec)
        if corpo is not None:
            # os receptores novos de cada estado sorteados pela rng propria da sonda (sonda-corpo), na ordem dos estados
            rng = random.Random(derivar_semente("sonda-corpo", sonda["semente"]))
            com_mundo = mundo_de(vida.espec.mundo).fisico is not None
            estados = [replace(o, corpo=percepcao_da_sonda(o, corpo, rng, com_mundo)) for o in estados]
        prior = self.politica(replace(vida.espec, braco=p0), CONFIG_PADRAO)
        d_prior = distribuicoes_de_acao(prior, estados, sonda["amostras"], sonda["semente"])
        fab, fm = self.fabrica_politica(vida.espec), self.fabrica_motor(vida.espec)
        log = vida.motor.log
        serie = []
        fisico = mundo_de(vida.espec.mundo).fisico is not None
        for d in range(1, self.dias + 1):
            # a sonda le o cerebro do braco direto: o embrulho da bola mexeria no motor e poria a bola nos estados da sonda. O mundo
            # fisico tem eventos proprios no log: o replay dele, com o mesmo corte no tick
            if fisico:
                pol = do_braco(reproduzir_mundo(log, fab, semente=vida.espec.semente, fabrica_motor=fm,
                                                ate_tick=d * TICKS_POR_DIA).politica)
            else:
                pol = do_braco(politica_no_tick(log, fab, vida.espec.semente, d * TICKS_POR_DIA, fm))
            serie.append(jsd_media(distribuicoes_de_acao(pol, estados, sonda["amostras"], sonda["semente"]), d_prior))
        return serie

    # ------------------------------------------------------------- dois pets: o grupo (TAREFA_V2_DOIS_PETS, etapa 5)


    def bancada_grupo(self) -> "Bancada":
        """O cerebro A do plano (secao 2): o do ponto e da montagem da bancada, com o que a etapa 4 acrescenta: o alvo aprendido (#255; o
        P0 com o aprendizado desligado fica no alvo padrao do motor), as entradas sociais (prior 0) e o modelo dos outros (so registrado;
        #266). No prior, o P0 e o instinto do mundo byte a byte, tambem com o outro a vista (o gate do #266). E a rota do canal do humor no
        mundo fisico (#269, `presenca_fruta_mundo`: a decisao de comer le a fruta madura a vista, prior 0), sem a qual os canais da montagem
        completa falham alto ao comer a fruta que mexe no humor."""
        return replace(self, cfg_lobos=replace(self.cfg_lobos, alvo_aprendido=True, entradas_sociais=True, modelo_outros=True,
                                               presenca_fruta_mundo=True))

    def canais_no_pet(self, espec: EspecVida) -> bool:
        """Os canais da consequencia chegam ao cerebro deste pet? So nas fontes que aprendem pela consequencia, com os canais do braco
        montado (a montagem completa os liga no P1) ou, sem eles fixos, os da config."""
        b = self.braco(espec)
        if b.fonte not in APRENDE_PELA_CONSEQUENCIA:
            return False
        return self.cfg_consequencia.canais_ligados if b.canais is None else b.canais

    def orcamento_por_dia(self) -> int:
        if self.orcamento % self.dias:
            raise ValueError(f"o grupo tem orcamento por dia vivido: {self.orcamento} interacoes em {self.dias} dias nao divide")
        return self.orcamento // self.dias


    def dias_do_grupo(self, eg: EspecGrupo) -> int:
        """O grupo vive K + `dias` (o B vive os `dias` da bancada depois do dia K); o "A-so", os `dias`."""
        return eg.k + self.dias if BRACOS_GRUPO[eg.braco].b else self.dias


    def espec_do_pet(self, eg: EspecGrupo, ident: str) -> EspecVida:
        braco = dict((i, b) for i, b, _ in _entradas(eg))[ident]
        semente = sementes_do_grupo(eg.semente, CONFIG_GRUPO_LIGADA.ids)[ident]
        return EspecVida(eg.dono, braco, semente, None, eg.mundo, lugar=eg.lugar)


    def efeitos_do_grupo(self, eg: EspecGrupo) -> dict:
        """O efeito verdadeiro (o tipo ruim da unidade) e, no A embaralhado, o desarranjado dos K dias."""
        ruim = tipo_ruim(eg.semente)
        out = {"ruim": ruim, "verdadeiro": efeito_dois_pets(ruim, self.cfg_frutas)}
        if BRACOS_GRUPO[eg.braco].companheiro == "embaralhado":
            pi = desarranjo_dois_pets(eg.semente)
            out.update({"pi": pi, "ruim_embaralhado": pi[ruim], "embaralhado": efeito_dois_pets(pi[ruim], self.cfg_frutas)})
        return out


    def fabrica_motor_do_grupo(self, eg: EspecGrupo, ident: str):
        """A fabrica do motor de um pet do grupo, no formato do Grupo.entrar (`mundo=`, `entrada_mundo=`): o MotorMundo do plano do mundo
        (obediencia, educacao, lesoes, frutas e bola de hoje desligadas, especie brasa, temperamento neutro), com o efeito das frutas da unidade;
        o A embaralhado, o MotorMundoTroca. Sem `mundo`, o MotorMundo dono do proprio Mundo (a vida de hoje, para o gate do pet sozinho)."""
        cm = self.cfg_mundo_de(mundo_de(eg.mundo))
        ef = self.efeitos_do_grupo(eg)
        embaralha = ident == "A" and BRACOS_GRUPO[eg.braco].companheiro == "embaralhado"
        tick_troca = eg.k * TICKS_POR_DIA

        def fabrica(politica, cfg, semente, mundo=None, entrada_mundo=0):
            kw = dict(obediencia_desligada=True, semente_genoma=None, cfg_mundo=cm, mundo=mundo, entrada_mundo=entrada_mundo)
            if embaralha:
                return MotorMundoTroca(politica, cfg, semente, NEUTRO, "brasa", efeito_frutas=ef["embaralhado"], tick_troca=tick_troca,
                                       efeito_depois=ef["verdadeiro"], **kw)
            return MotorMundo(politica, cfg, semente, NEUTRO, "brasa", efeito_frutas=ef["verdadeiro"], **kw)
        return fabrica


    def pets_do_grupo(self, eg: EspecGrupo, envolver=None) -> list[PetDoGrupo]:
        """Os PetDoGrupo do `simular_grupo`: a politica do braco de cada pet pela bancada (o cerebro A com o alvo aprendido), a fabrica do
        motor e o dono, um por pet (o DonoComLugar sobre o dono da v1, com a semente do pet: as rngs `dono` e `dono-lugar` sao dele).
        `envolver(ident, politica)` embrulha a politica (o _RegistroGrupo do replay de medicao)."""
        _validar_espec_grupo(eg)
        bg_ = self.bancada_grupo()
        cm = self.cfg_mundo_de(mundo_de(eg.mundo))
        pets = []
        for ident, braco, entrada in _entradas(eg):
            espec = self.espec_do_pet(eg, ident)

            def fp(cfg=None, e=espec, i=ident):
                p = bg_.politica(e, cfg)
                return p if envolver is None else envolver(i, p)
            dono = DonoComLugar(criar_dono(eg.dono), eg.lugar, espec.semente, eg.dono, cm)
            pets.append(PetDoGrupo(ident, entrada, fp, self.fabrica_motor_do_grupo(eg, ident), dono, eg.dono,
                                   cerebro=f"{espec.cerebro}/{braco}"))
        return pets


    def cfg_grupo(self) -> ConfigGrupo:
        return replace(CONFIG_GRUPO_LIGADA, orcamento_por_dia=self.orcamento_por_dia())


    def grupo(self, eg: EspecGrupo) -> VidaGrupo:
        """O grupo da celula (DP-7, a validacao inicial), pelo `simular_grupo`: um dono para todos, decidindo por pet, com o orcamento por dia
        vivido de cada um e so com o cuidado (o CanalSemEnsino ao vivo, PMF-3). O G1 do grupo e conferido antes de devolver."""
        _validar_espec_grupo(eg)
        canais: list = []

        class _Canal(CanalSemEnsino):
            def __init__(s, *a, **kw) -> None:
                super().__init__(*a, **kw)
                canais.append(s)

        g = simular_grupo(self.cfg_mundo_de(mundo_de(eg.mundo)), eg.semente, self.pets_do_grupo(eg), self.dias_do_grupo(eg),
                          cfg_grupo=self.cfg_grupo(), cfg=CONFIG_PADRAO, canal_classe=_Canal)
        retirados = {c.motor.ident: c.retirados for c in canais}
        if set(retirados) != set(g.motores):
            raise RuntimeError(f"{eg.nome}: canais {sorted(retirados)} para os pets {sorted(g.motores)}")
        vida = VidaGrupo(eg, g, dict(g.interacoes), retirados)
        self.conferir_replay_grupo(vida)
        return vida


    def rejogar_grupo(self, registro: RegistroGrupo, eg: EspecGrupo, envolver=None) -> Grupo:
        fabricas = {p.ident: (p.politica_fabrica, p.fabrica_motor) for p in self.pets_do_grupo(eg, envolver)}
        return reproduzir_grupo(registro, fabricas, self.cfg_mundo_de(mundo_de(eg.mundo)), self.cfg_grupo(), CONFIG_PADRAO)


    def conferir_replay_grupo(self, vida: VidaGrupo, texto: str | None = None) -> None:
        """G1 do grupo: rejoga o registro do grupo a partir do texto (do disco, se vier) e compara tudo bit a bit (o mundo, as vezes
        sorteadas, a rng da ordem e cada pet: log, estado, acoes, rngs, registros do mundo fisico, estado interno da politica)."""
        proprio = vida.grupo.registro.para_jsonl()
        texto = proprio if texto is None else texto
        if texto != proprio:
            raise ReplayDivergiu(f"{vida.nome}: o registro do disco nao e o do grupo")
        r = self.rejogar_grupo(RegistroGrupo.de_jsonl(texto), vida.espec)
        if _resumo_grupo(r) != _resumo_grupo(vida.grupo):
            raise ReplayDivergiu(f"{vida.nome}: o grupo diverge no replay")


    def chao_na_entrada(self, vida: VidaGrupo, ident: str = "B") -> dict:
        """O chao do mundo quando o pet `ident` entra (R-3, so descritivo; o B no dia K): o registro do grupo rejogado ate logo antes da entrada
        dele, com o mundo atualizado ate o tick (a atualizacao e idempotente e so le o tick e o fluxo das arvores). Conta as comidas por tipo e
        situacao."""
        reg = vida.grupo.registro
        idx = [k for k, e in enumerate(reg.eventos) if e.tipo == "entrada" and e.valor == ident]
        if len(idx) != 1:
            raise ValueError(f"{vida.nome}: o pet {ident!r} nao entrou uma vez no registro")
        antes = reg.eventos[:idx[0]]
        entrados = [e.valor for e in antes if e.tipo == "entrada"]
        cab = {**reg.cabecalho, "pets": {i: dict(reg.cabecalho["pets"][i]) for i in entrados}}
        fabricas = {p.ident: (p.politica_fabrica, p.fabrica_motor) for p in self.pets_do_grupo(vida.espec) if p.ident in entrados}
        g = reproduzir_grupo(RegistroGrupo(cab, list(antes)), fabricas, self.cfg_mundo_de(mundo_de(vida.espec.mundo)), self.cfg_grupo(),
                             CONFIG_PADRAO)
        g.mundo.atualizar(g.tick)
        contagem: dict = {}
        for c in g.mundo.comidas.values():
            chave = f"{c['tipo']}/{g.mundo.situacao(c, g.tick)}"
            contagem[chave] = contagem.get(chave, 0) + 1
        return {"tick": g.tick, "comidas": dict(sorted(contagem.items()))}


    def medidas_sociais(self, vida: VidaGrupo) -> dict:
        """Os descritivos da secao 4 que vem dos sentidos (etapa 3 do A, #263), por pet, dos registros do grupo e de cada motor:
          - o uso dos candidatos sociais: por dia vivido, as decisoes de explorar e quantas foram ao `seguir` e ao `onde_comeu` (o alvo de
            `decisoes_mundo`; a fracao None sem explorar no dia);
          - o que o pet viu: os consumos do outro que ele viu (`vistos_comer`), por tipo e situacao (o consumo do outro no mesmo tick; um
            consumo visto sem consumo do outro falha alto), e quantos do tipo ruim maduros;
          - a disputa (`Grupo.disputas`): quantas, quantas o pet ganhou e, em cada uma, a distancia dele e a do outro a comida;
          - o toque (`Grupo.contatos`): os contatos por tipo (disputa, encostar, esbarrar), por dia vivido;
          - o tempo a vista (`a_vista`), as idas a `onde_comeu` (chegou, comeu) e as decisoes no grupo.
        O modelo dos outros sai em `modelo_dos_outros`."""
        g = vida.grupo
        ruim = self.efeitos_do_grupo(vida.espec)["ruim"]
        fim = g.tick
        out = {}
        for ident, m in g.motores.items():
            entrada = m.entrada_mundo
            dias = (fim - entrada) // TICKS_POR_DIA
            dia = lambda t, e=entrada: (t - e) // TICKS_POR_DIA  # noqa: E731
            uso = [{"dia": d + 1, "explorar": 0, "seguir": 0, "onde_comeu": 0} for d in range(dias)]
            for dec in m.decisoes_mundo:
                if dec["acao"] == "explorar":
                    u = uso[dia(dec["tick"])]
                    u["explorar"] += 1
                    if dec["alvo"] in ("seguir", "onde_comeu"):
                        u[dec["alvo"]] += 1
            for u in uso:
                for c in ("seguir", "onde_comeu"):
                    u[f"fracao_{c}"] = u[c] / u["explorar"] if u["explorar"] else None
            vistos: dict = {}
            vistos_ruins = 0
            for vc in m.vistos_comer:
                comidos = [c for c in g.motores[vc["outro"]].consumos_mundo if c["tick"] == vc["tick"]]
                if len(comidos) != 1:
                    raise RuntimeError(f"{vida.nome}/{ident}: consumo visto no tick {vc['tick']} sem um consumo do {vc['outro']}")
                c = comidos[0]
                chave = f"{c['tipo']}/{c['situacao']}"
                vistos[chave] = vistos.get(chave, 0) + 1
                vistos_ruins += c["tipo"] == ruim and c["situacao"] == "madura"
            disputas = []
            for d in g.disputas:
                if ident in (d["vencedor"], d["perdedor"]):
                    ganhou = d["vencedor"] == ident
                    primeiro = None if d["vencedor_primeiro"] is None else d["vencedor_primeiro"] == ganhou
                    disputas.append({"tick": d["tick"], "tipo": d["tipo"], "ganhou": ganhou, "veio_primeiro": primeiro,
                                     "d_eu": d["d_vencedor" if ganhou else "d_perdedor"],
                                     "d_outro": d["d_perdedor" if ganhou else "d_vencedor"], "contato": d["contato"]})
            toque = [{"dia": d + 1} for d in range(dias)]
            for c in g.contatos:
                if ident in c["pets"]:
                    t = toque[dia(c["tick"])]
                    t[c["tipos"][ident]] = t.get(c["tipos"][ident], 0) + 1
            rs = m.resumo_social()
            idas = rs["idas_onde_comeu"]
            out[ident] = {"uso_candidatos": uso,
                          "vistos_comer": {"n": len(m.vistos_comer), "por_tipo": dict(sorted(vistos.items())), "ruins_maduros": vistos_ruins},
                          "disputas": {"n": len(disputas), "ganhou": sum(x["ganhou"] for x in disputas), "lista": disputas},
                          "toque_por_dia": toque, "a_vista": dict(rs["a_vista"]), "decisoes_no_grupo": rs["decisoes_no_grupo"],
                          "idas_onde_comeu": {"n": len(idas), "chegou": sum(1 for i in idas if i["chegou"]),
                                              "comeu": sum(1 for i in idas if i["comeu"] is not None)}}
        return out

    def modelo_dos_outros(self, vida: VidaGrupo) -> dict:
        """O modelo dos outros no fim da vida (plano, secao 4: a familiaridade, a confianca por atividade e a afinidade de cada pet sobre o
        outro; so registradas, DP-8), por pet, como o cerebro o serializa (`estado_interno()["modelo_outros"]["outros"]`). O cerebro do
        grupo sempre o tem (`bancada_grupo`): um cerebro sem ele falha alto. O por dia sai do replay de medicao (`medir_grupo`)."""
        out = {}
        for ident, m in vida.grupo.motores.items():
            interno = m.politica.estado_interno()
            if "modelo_outros" not in interno:
                raise RuntimeError(f"{vida.nome}/{ident}: o cerebro sem o modelo dos outros (a chave modelo_outros)")
            out[ident] = interno["modelo_outros"]["outros"]
        return out

    def medir_grupo(self, vida: VidaGrupo) -> dict:
        """As medidas da secao 4 que ja tem dado no registro do grupo, do replay de medicao (conferido bit a bit contra o grupo):
          - a R de cada pet (`metrics.taxa_fruta_ruim` sobre os consumos de fruta madura, com o efeito vigente do tipo no tick): no B, os 7
            primeiros dias (a primaria, PDP-2), a vida toda e um por dia; no A, um por dia, ate o dia K e depois (o A embaralhado pelo efeito
            de cada lado da troca);
          - o custo de ter companhia: o D_FE e a privacao (`deficit_fome_energia`, `cuidado_preservado`) nos 7 primeiros dias e na vida toda;
          - o alvo aprendido: os pesos por classe no fim de cada dia (o "o que o B aprendeu", com as classes `seguir` e `onde_comeu`);
          - a sorte da ordem (R-5, `vez_no_grupo`) e o chao no dia K (R-3);
          - os consumos por tipo, situacao e como (achou ou foi comer), o gasto do dono e os sinais retirados (PMF-3).
        As medidas sociais (`medidas_sociais`, da etapa 3) e o modelo dos outros (`modelo_dos_outros`, no fim, e por dia em cada pet) saem
    ao lado."""
        eg = vida.espec
        regs: dict = {}

        def envolver(ident, politica):
            regs[ident] = _RegistroGrupo(politica)
            return regs[ident]

        r = self.rejogar_grupo(vida.grupo.registro, eg, envolver)
        if _resumo_grupo(r) != _resumo_grupo(vida.grupo):
            raise ReplayDivergiu(f"{vida.nome}: o replay de medicao mudou o grupo")
        ef = self.efeitos_do_grupo(eg)
        fim_grupo = self.dias_do_grupo(eg) * TICKS_POR_DIA
        dia_k = eg.k * TICKS_POR_DIA
        pets = {}
        for ident, m in r.motores.items():
            reg = regs[ident]
            reg.fim()
            decs = m.decisoes_mundo
            if len(decs) != len(reg.vetores):
                raise RuntimeError(f"{vida.nome}/{ident}: {len(decs)} decisoes no mundo e {len(reg.vetores)} no replay de medicao")
            intervalo = CONFIG_PADRAO.intervalo_decisao_ticks
            ticks = [d["tick"] for d in decs]
            if ticks != [m.entrada_mundo + k * intervalo for k in range(len(ticks))]:
                raise RuntimeError(f"{vida.nome}/{ident}: decisoes fora da grade do pet")
            entrada = m.entrada_mundo
            dias_vividos = (fim_grupo - entrada) // TICKS_POR_DIA
            efeito_no_tick = m.efeito_no_tick if isinstance(m, MotorMundoTroca) else (lambda t: ef["verdadeiro"])  # noqa: E731
            frutas = [(c["tick"], efeito_no_tick(c["tick"])[c["tipo"]]) for c in m.consumos_mundo
                      if c["tipo"] in FRUTAS and c["situacao"] == "madura"]
            vida_j = (entrada, fim_grupo)
            primeiros = (entrada, entrada + min(JANELA_PRIMARIA_DIAS, dias_vividos) * TICKS_POR_DIA)
            janelas = {"vida": vida_j, "primeiros_7": primeiros}
            if entrada < dia_k:                                   # o A que vive os K dias antes do B
                janelas.update({"ate_k": (entrada, dia_k), "depois_k": (dia_k, fim_grupo)})
            for d in range(dias_vividos):
                janelas[f"dia_{d + 1}"] = (entrada + d * TICKS_POR_DIA, entrada + (d + 1) * TICKS_POR_DIA)
            fe = [(t, v[1], v[3]) for t, v in zip(ticks, reg.vetores)]
            cuidado = [(t, p, s, v[1]) for t, (p, s), v in zip(ticks, reg.amostras, reg.vetores)]
            consumos: dict = {}
            for c in m.consumos_mundo:
                chave = f"{c['tipo']}/{c['situacao']}/{c['como']}"
                consumos[chave] = consumos.get(chave, 0) + 1
            pets[ident] = {"braco": dict((i, b) for i, b, _ in _entradas(eg))[ident], "semente": m.semente, "entrada": entrada,
                           "dias_vividos": dias_vividos, "taxa_fruta_ruim": taxa_fruta_ruim(frutas, janelas),
                           "d_fe": {"primeiros_7": deficit_fome_energia(fe, primeiros), "vida": deficit_fome_energia(fe, vida_j)},
                           "cuidado": {"primeiros_7": cuidado_preservado(cuidado, primeiros), "vida": cuidado_preservado(cuidado, vida_j)},
                           "pesos_alvo_por_dia": reg.pesos_alvo_dia, "modelo_outros_por_dia": reg.modelo_dia,
                       "vez": vez_no_grupo(r.ordens, ident),
                           "consumos": dict(sorted(consumos.items())), "consumos_fruta_madura": len(frutas),
                           "interacoes": vida.interacoes.get(ident), "retirados": vida.retirados.get(ident),
                           "troca": getattr(m, "troca", None)}
        b = BRACOS_GRUPO[eg.braco]
        return {"grupo": vida.nome, "braco": eg.braco, "companheiro": b.companheiro, "semente": eg.semente, "k": eg.k, "dono": eg.dono,
                "lugar": eg.lugar, "mundo": eg.mundo, "ruim": ef["ruim"], "ruim_embaralhado": ef.get("ruim_embaralhado"),
                "ordens": len(r.ordens), "pets": pets, "chao_no_dia_k": self.chao_na_entrada(vida) if b.b else None,
                "sociais": self.medidas_sociais(vida), "modelo_dos_outros": self.modelo_dos_outros(vida)}


def receptores_novos_de(cc: ConfigCorpo, com_mundo: bool = False) -> tuple[str, ...]:
    """Os receptores novos que o corpo desta ConfigCorpo tem (os da tabela do grafo, `Corpo.receptores`), na ordem de RECEPTORES_NOVOS:
    nenhum na quimica; tedio, solidao e estresse com `drives_novos`; dor e susto com `gestos`; a curiosidade so com o mundo fisico (CD-8)."""
    nomes = set(Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo).receptores())
    return tuple(r for r in RECEPTORES_NOVOS if r in nomes)


def medidas_banheiro_de(alivios, dias: int, carinhos=(), limpador=(), pesos_alvo=None, cuidado=(), escolhas=()) -> dict:
    """As medidas do PLANO_ANALISE_V2_BANHEIRO numa vida, das funcoes do #224 (`metrics`). As entradas, sem o motor:
      - `alivios`: (tick, dentro do banheiro, urgente) por `aliviar`;
      - `carinhos`: (tick, solidao antes na escala 0-1, sinal pelo corpo) por carinho depois do banheiro;
      - `limpador`: (tick, sinal pelo corpo) por alivio recolhido pelo limpador;
      - `pesos_alvo`: os pesos do alvo no fim de cada dia, {"banheiro": w, "aqui": w} (um por dia, ou None);
      - `cuidado`: (tick, em privacao, saude, fome) por decisao;
      - `escolhas`: (tick, alvo, terminou dentro, distancia) por `aliviar` decidido (sem o urgente), para o "chegou tarde" (R-2).
    Sai: a fracao diaria e os acidentes (`alivios_por_dia`); o dia do criterio com a censura e T* (`dia_do_criterio`, BN-4: 0,80 em tres
    dias seguidos); os alivios ate o criterio; os acidentes na vida; o cuidado preservado na vida (`cuidado_preservado`); o carinho e o
    limpador por dia (quantos, a solidao media no carinho, o sinal medio: R-3); o peso do alvo por dia (banheiro - aqui); o chegou tarde
    (a fracao das escolhas de `banheiro` que terminam fora, e a distancia media delas)."""
    T = TICKS_POR_DIA
    por_dia = alivios_por_dia(alivios, dias)
    criterio = dia_do_criterio([o["fracao"] for o in por_dia])
    n = sum(o["n"] for o in por_dia)
    urgentes = sum(o["urgentes"] for o in por_dia)

    def diario(itens, campos):
        out = [{"dia": d + 1, "n": 0, **{c: None for c in campos}} for d in range(dias)]
        soma = [[0.0] * len(campos) for _ in range(dias)]
        for item in itens:
            d = item[0] // T
            if not 0 <= d < dias:
                raise ValueError(f"tick {item[0]} fora dos {dias} dias")
            out[d]["n"] += 1
            for i, v in enumerate(item[1:]):
                soma[d][i] += v
        for o, s in zip(out, soma):
            if o["n"]:
                o.update({c: v / o["n"] for c, v in zip(campos, s)})
        return out

    if pesos_alvo is not None and len(pesos_alvo) != dias:
        raise ValueError(f"pesos do alvo: {len(pesos_alvo)} dias, a vida tem {dias}")
    banheiro_escolhido = [(t, dentro, dist) for t, alvo, dentro, dist in escolhas if alvo == "banheiro"]
    tarde = [x for x in banheiro_escolhido if not x[1]]
    return {"por_dia": por_dia, "criterio": criterio, "alivios_ate_criterio": alivios_ate_criterio(por_dia, criterio["dia"]),
            "alivios": n, "acidentes": {"n": urgentes, "fracao": urgentes / n if n else None},
            "cuidado": cuidado_preservado(cuidado, (0, dias * T)) if cuidado else None,
            "carinho": {"n": len(carinhos), "por_dia": diario(carinhos, ("solidao_media", "sinal_medio"))},
            "limpador": {"n": len(limpador), "por_dia": diario(limpador, ("sinal_medio",))},
            "peso_alvo_por_dia": None if pesos_alvo is None else [
                {"banheiro": p["banheiro"], "aqui": p["aqui"], "banheiro_menos_aqui": p["banheiro"] - p["aqui"]} for p in pesos_alvo],
            "chegou_tarde": {"escolhas_banheiro": len(banheiro_escolhido), "fora": len(tarde),
                             "fracao": len(tarde) / len(banheiro_escolhido) if banheiro_escolhido else None,
                             "distancia_media": (sum(d for _, _, d in banheiro_escolhido) / len(banheiro_escolhido)
                                                 if banheiro_escolhido else None)}}


def tabela_banheiro(medidas: dict) -> dict:
    """Por braco do 2 x 2 (o rotulo, P0 ou P1), o descritivo da secao 4: a curva de Kaplan-Meier do dia do criterio (`curva_sobrevivencia`:
    a mediana quando existe, a fracao censurada e a RMST, a media de T*), sobre as vidas daquele braco. Os contrastes pareados (G-CARINHO,
    G-LIMPADOR) sao do orquestrador do plano."""
    por_braco: dict = {}
    for m in medidas.values():
        if m.get("banheiro") is not None and m["origem"] is None:
            por_braco.setdefault(m["braco"], []).append(m["banheiro"]["criterio"])
    return {b: curva_sobrevivencia(cs) for b, cs in sorted(por_braco.items())}


def percepcao_da_sonda(obs, cc: ConfigCorpo, rng: random.Random | None = None, com_mundo: bool = False) -> PercepcaoCorpo:
    """Os receptores de um estado sintetico da sonda (a deriva), com a conta do corpo: cada drive h vira o quimico q = arred((1 - h) C),
    o ponto da grade de C mais perto, e o receptor e S - div_arred(q S, C), como o `Corpo.receptores`. Os receptores novos (a leitura e a
    falta, ou a concentracao na dor e no susto) nao tem drive no vetor da sonda: cada um sai uniforme na grade [0, S] da `rng` (a da sonda,
    derivar_semente("sonda-corpo", semente), um sorteio por receptor na ordem de RECEPTORES_NOVOS), como as outras entradas da sonda saem
    uniformes. Sem `rng`, so a quimica (sem receptores novos); com eles e sem `rng`, falha alto."""
    C, S = cc.escala, cc.escala_receptor
    v = obs.vetor_estado
    leituras = {}
    for i, nome in enumerate(("fome", "higiene", "energia", "humor", "saude")):
        q = arred((1.0 - v[i]) * C)
        leituras[nome] = S - div_arred_corpo(q * S, C)
    novos = receptores_novos_de(cc, com_mundo)
    if novos and rng is None:
        raise ValueError(f"a sonda do corpo com os receptores novos {novos} precisa da rng da sonda")
    for r in novos:
        leituras[r] = rng.randrange(S + 1)
    return PercepcaoCorpo(**leituras)


def do_braco(politica) -> PoliticaDoBraco:
    """A PoliticaDoBraco dentro dos embrulhos dos motores (bola, personalidade)."""
    p = politica
    while not isinstance(p, PoliticaDoBraco):
        if isinstance(p, _Espiao):
            p = p.interna
        elif isinstance(p, _PoliticaComMundo):
            p = p._pm
        elif isinstance(p, _PoliticaComFrutas):
            p = p._pf
        elif isinstance(p, _PoliticaComBola):
            p = p._pb
        elif isinstance(p, _PoliticaObservada):
            p = p._p
        else:
            raise TypeError(f"politica sem PoliticaDoBraco dentro: {type(p).__name__}")
    return p


# ------------------------------------------------------------------ o tapa na fruta X (corpo, adendo 1, A1.1)


def fruta_tapa(semente: int) -> str:
    """A fruta X do P1-c-tapaX (A1.1): sorteada uma vez por vida por derivar_semente("tapa-fruta", semente), uniforme entre as tres, sem
    olhar a preferencia inata. E a regra do N7-6 (DonoPedinte.sortear_fruta) com outra rng; nao toca outra."""
    rng = random.Random(derivar_semente("tapa-fruta", semente))
    return FRUTAS[rng.randrange(len(FRUTAS))]


class DonoTapaFruta:
    """O dono do P1-c-tapaX (adendo 1 do plano do corpo, A1.1): o DonoComGestos sem tapa (`base`) mais o tapa na fruta X. Em cada passo,
    um `tapa` por consumo novo de X (lidos em estado()["consumos_frutas"], que o motor expoe com a ConfigJulgamentoFruta ligada) vem
    PRIMEIRO, ate o maximo do passo: e o primeiro passo do dono depois do consumo, dentro do orcamento e como contato (CD-6). O dono
    embrulhado decide com a `Visao` do que sobra (gasto + n, minimo e maximo - n; a regra do DonoJulgaFruta), entao o canal fecha o mesmo
    orcamento. O que nao coube no passo fica em `descartados` (o tick do consumo; nao volta depois). `tapas` guarda (tick do consumo, tick
    do tapa)."""

    def __init__(self, base, fruta: str) -> None:
        if fruta not in FRUTAS:
            raise ValueError(f"fruta {fruta!r}: so {FRUTAS}")
        if not isinstance(base, DonoComGestos) or base.modo != "sem_tapa":
            raise ValueError("o tapa na fruta X vai por cima do DonoComGestos sem tapa (A1.1)")
        self.base = base
        self.fruta = fruta
        self.nome = base.nome
        self.tapas: list[tuple[int, int]] = []
        self.descartados: list[int] = []
        self._vistos = 0

    @property
    def trocas(self) -> dict:
        return self.base.trocas

    def decidir(self, visao: Visao, rng: random.Random) -> list:
        consumos = visao.estado["consumos_frutas"]
        if len(consumos) < self._vistos:
            raise RuntimeError(f"consumos voltaram atras: {self._vistos} -> {len(consumos)}")
        novos, self._vistos = consumos[self._vistos:], len(consumos)
        de_x = [t for t, f in novos if f == self.fruta]
        n = min(len(de_x), visao.maximo_permitido)
        self.descartados.extend(de_x[n:])
        self.tapas.extend((t, visao.estado["tick"]) for t in de_x[:n])
        resto = replace(visao, gasto=visao.gasto + n, minimo_obrigatorio=max(0, visao.minimo_obrigatorio - n),
                        maximo_permitido=visao.maximo_permitido - n)
        return [AcaoUsuario.TAPA] * n + self.base.decidir(resto, rng)


# ------------------------------------------------------------------ o mundo da bola com B1 e B2


class RegraBola:
    """Decisoes B1 e B2 (2026-10-01, docs/RESULTADO_V2_A1.md): quem poe a bola e uma regra do MUNDO, fora do orcamento do dono.
    A regra dos coerentes da A1 (DonoComBola), sem a condicao do limite do passo (a bola nao gasta orcamento): atencioso e
    incoerente poem com o pet acordado, fora da noite, sem cuidado pendente, sem bola no cenario e no maximo `bolas_por_dia`
    por dia; o relapso so nos passos em que ele mesmo agiu (as visitas; B3: aceito como e). O aleatorio NAO poe bola (B1: o
    `por_bola` sai do sorteio dele, e ele nao tem outra regra). Le a visao de ANTES das acoes do dono do passo, como a A1."""

    def __init__(self, dono: str, cfg_bola: ConfigBola, cfg_donos=None, cfg=None) -> None:
        self.dono = dono
        self.cb = cfg_bola
        self.cd = cfg_donos or CONFIG_DONOS
        self.cfg = cfg or CONFIG_PADRAO
        self._dia = -1
        self._bolas_hoje = 0

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        if self.dono == "aleatorio":
            return []
        e = visao.estado
        dia = e["tick"] // TICKS_POR_DIA
        if dia != self._dia:
            self._dia, self._bolas_hoje = dia, 0
        if self.dono == "relapso" and not acoes_do_dono:
            return []
        if (self._bolas_hoje < self.cb.bolas_por_dia and not e["dormindo"] and not self.cfg.e_noite(e["tick_do_dia"])
                and e.get("bola") is None and not cuidados_necessarios(e, self.cd)):
            self._bolas_hoje += 1
            return [AcaoUsuario.POR_BOLA]
        return []


class InformanteDoMundo:
    """O DonoInformante (frutas.py, que nao muda) com o efeito REAL do mundo da bancada (E7; `efeitos_da_condicao`), sobre cada fruta
    oferecida, logo depois da oferta. No mutavel o efeito real troca em `tick_troca`: antes, o dono sabe o do casado; dali em diante,
    o do descasado (dois DonoInformante, escolhidos pelo tick)."""

    def __init__(self, modo: str, efeitos: dict, tick_troca: int | None) -> None:
        self.modo = modo
        self.antes = DonoInformante(modo, efeitos["antes"])
        self.depois = DonoInformante(modo, efeitos["depois"]) if efeitos["depois"] is not None else None
        if (self.depois is None) != (tick_troca is None):
            raise ValueError("so o mutavel troca o efeito, e ele precisa do tick_troca")
        self.tick_troca = tick_troca

    def acoes(self, tick: int, ofertadas: list[str]) -> list[AcaoUsuario]:
        d = self.depois if self.depois is not None and tick >= self.tick_troca else self.antes
        return d.acoes(tick, ofertadas)

    @property
    def feitas(self) -> list[tuple[int, str, str]]:
        return sorted(self.antes.feitas + (self.depois.feitas if self.depois else []))


class InformanteAcoplado:
    """P2a (plano do N5, secao 4.2; decisao N5-4): o MESMO multiconjunto de (fruta, conteudo verdadeiro) que o P2 da unidade recebe,
    em ticks sorteados uniformemente ao longo da vida, pela rng derivar_semente("informacao-acoplada", semente). O multiconjunto sai do
    CalendarioFrutas (que nao depende do pet), passo a passo, com o conteudo do `certo` no tick original; cada item ganha um passo do
    dono sorteado (rng.randrange sobre os passos, na ordem do calendario) e vai ao motor nesse passo, pela ordem original. Fora de
    hora: a informacao muitas vezes fala de uma fruta que nao esta no cenario. No mutavel o conteudo e o verdadeiro NO TICK ORIGINAL
    (e o mesmo multiconjunto do P2), entao um item levado para o outro lado da troca deixa de ser verdadeiro. O modo `acoplado` do
    DonoInformante (docs/TAREFA_V2_N5_ACOPLADO.md, chat A) tem de dar os mesmos eventos; ate ele entrar, a bancada usa este."""

    def __init__(self, semente: int, dias: int, cf: ConfigFrutas, efeitos: dict, tick_troca: int | None) -> None:
        cd = CONFIG_DONOS
        passos = dias * TICKS_POR_DIA // cd.passo_ticks
        verdade = InformanteDoMundo("certo", efeitos, tick_troca)
        calendario = CalendarioFrutas(semente, cf)
        itens: list[tuple[int, str, str]] = []                       # (tick original, fruta, conteudo)
        for passo in range(passos):
            tick = (passo + 1) * cd.passo_ticks                       # o tick da visao do dono em simular_vida_mundo
            ofertas = calendario.decidir(Visao(estado={"tick": tick}, passo=passo, passos_totais=passos, orcamento=0, gasto=0,
                                                minimo_obrigatorio=0, maximo_permitido=0), [])
            for a in verdade.acoes(tick, [fruta_de(o) for o in ofertas]):
                f, c = a.value.split("_")[2:]
                itens.append((tick, f, c))
        rng = random.Random(derivar_semente("informacao-acoplada", semente))
        self.agenda: dict[int, list[tuple[str, str]]] = {}
        self.itens = itens
        for _, f, c in itens:
            tick = (rng.randrange(passos) + 1) * cd.passo_ticks
            self.agenda.setdefault(tick, []).append((f, c))
        self.feitas: list[tuple[int, str, str]] = []

    def acoes(self, tick: int, ofertadas: list[str]) -> list[AcaoUsuario]:
        out = []
        for f, c in self.agenda.get(tick, []):
            self.feitas.append((tick, f, c))
            out.append(informar(f, c))
        return out


class RegraFrutasComJulgador:
    """K4 fora do orcamento (decisao do Matheus, 2026-10-05): o julgamento da fruta (JulgadorFruta, #170) primeiro, como no
    simular_vida_frutas (logo depois das acoes do dono do passo, com o estado do passo), e depois o que a regra de dentro poe (as
    ofertas). Os julgamentos sao elogiar/repreender, os unicos extras que esta regra poe fora do orcamento; `feitos` os conta."""

    def __init__(self, regra, julgador: JulgadorFruta) -> None:
        if julgador.cj.no_orcamento:
            raise ValueError("a regra do mundo so leva o julgamento fora do orcamento")
        self.regra = regra
        self.julgador = julgador
        self.feitos = 0
        # o feedback (elogiar/repreender) so entra fora do orcamento por esta regra; a informacao ja e FORA_DO_ORCAMENTO (P2d, P3i)
        proprios = JULGAMENTOS if julgador.saida == "feedback" else frozenset()
        self.extras_fora_do_orcamento = proprios | getattr(regra, "extras_fora_do_orcamento", frozenset())

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        julg = self.julgador.acoes(visao.estado)
        self.feitos += len(julg)
        return julg + self.regra.decidir(visao, acoes_do_dono)


class RegraFrutasComInformante:
    """O canal do mundo das frutas com um informante: as ofertas do calendario e, logo depois, o que o informante diz (fora do
    orcamento, B2). O informante recebe as frutas oferecidas no passo (o acoplado as ignora)."""

    def __init__(self, calendario: CalendarioFrutas, informante) -> None:
        self.calendario = calendario
        self.informante = informante
        self.extras_fora_do_orcamento = getattr(calendario, "extras_fora_do_orcamento", frozenset())

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        ofertas = self.calendario.decidir(visao, acoes_do_dono)
        return ofertas + self.informante.acoes(visao.estado["tick"], [fruta_de(o) for o in ofertas])


class RegraFrutasComPedinte:
    """N7: o canal do mundo das frutas com o dono que pede (DonoPedinte, N7-MUNDO): o que a regra de dentro poe (as ofertas e, no P2, a
    informacao) e, logo depois, as acoes do pedinte com o estado do passo e as frutas oferecidas: a bronca da desobediencia (so no P3+ped)
    e o pedido "deixe X". Tudo fora do orcamento (B2), como no simular_vida_frutas."""

    def __init__(self, regra, pedinte: DonoPedinte) -> None:
        self.regra = regra
        self.pedinte = pedinte
        proprios = frozenset({AcaoUsuario.REPREENDER.value}) if pedinte.bronca else frozenset()
        self.extras_fora_do_orcamento = proprios | getattr(regra, "extras_fora_do_orcamento", frozenset())

    def decidir(self, visao: Visao, acoes_do_dono: list) -> list[AcaoUsuario]:
        eventos = self.regra.decidir(visao, acoes_do_dono)
        ofertadas = [fruta_de(e) for e in eventos if e in ACOES_FRUTAS]
        return eventos + self.pedinte.acoes(visao.estado, ofertadas)


class _Espiao:
    """So nos testes: embrulha a politica do braco e anota tudo o que chega por `receber_acao_dono` (o gate "a informacao nunca chega
    ao aprendiz como sinal")."""

    def __init__(self, interna) -> None:
        self.interna = interna
        self.nome = interna.nome
        self.recebidas: list[tuple[str, int]] = []

    def agir(self, obs, rng):
        return self.interna.agir(obs, rng)

    def observar(self, transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self.recebidas.append((acao.value, tick))
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def simular_vida_mundo(dono, regra_mundo, politica, semente: int, dias: int, orcamento: int, rotulo_dono: str,
                       fabrica_motor, canal_classe=CanalDeInteracao):
    """treino.simular_vida com um canal do MUNDO fora do orcamento (B2): a cada passo o dono age pelo CanalDeInteracao (o
    orcamento exato de sempre) e depois a regra do mundo poe o que pos, direto no motor (entra no log, nao no canal). O dono
    nao ve os eventos do mundo no gasto do orcamento. Mesma rng do dono que simular_vida (derivada de semente e rotulo_dono).
    `canal_classe`: o CanalComGestos nos bracos com os gestos do corpo (o SemGesto gasta o orcamento sem ir ao motor)."""
    cfg, cd = CONFIG_PADRAO, CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cd.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cd.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono))
    canal = canal_classe(motor, orcamento, cd.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cd.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        acoes = dono.decidir(visao, rng_dono)
        canal.aplicar(acoes, passo, passos)
        permitidos = FORA_DO_ORCAMENTO | getattr(regra_mundo, "extras_fora_do_orcamento", frozenset())
        for evento in regra_mundo.decidir(visao, acoes):
            if evento.value not in permitidos:
                raise ValueError(f"a regra do mundo so poe eventos do mundo, informacao ou pedido, nao {evento.value!r}")
            motor.observar(evento)
    canal.fechar()
    return motor


class CanalSemEnsino(CanalMundo):
    """PMF-3 (PLANO_ANALISE_V2_MUNDO_FISICO, secao 2): os donos so com o cuidado, pelo filtro sem_ensino de hoje aplicado AO VIVO. O dono
    decide como sempre (o mesmo dono sintetico, no mesmo ritmo do orcamento); o elogio e a bronca contam no orcamento dele, mas nao chegam
    ao motor nem ao log (`retirados`). O resto vai como no CanalMundo (o deixar_comida e o deixar_bola gastam o orcamento)."""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.retirados = 0

    def aplicar(self, acoes: list, passo: int, passos_totais: int) -> None:
        minimo, maximo = self.limites(passo, passos_totais)
        if len(acoes) > maximo:
            raise OrcamentoExcedido(f"passo {passo}: dono pediu {len(acoes)} interacoes, maximo {maximo}")
        if len(acoes) < minimo:
            raise OrcamentoNaoConsumido(f"passo {passo}: dono fez {len(acoes)} interacoes, minimo {minimo}")
        for acao in acoes:
            if isinstance(acao, AcaoUsuario) and acao.value in SINAIS:
                self.retirados += 1                        # o sem_ensino: gasta o orcamento do dono, nao chega ao pet
            elif isinstance(acao, DeixarComida):
                self.motor.deixar_comida(acao.tipo, acao.x, acao.y)
            elif isinstance(acao, DeixarBola):
                self.motor.deixar_bola(acao.x, acao.y)
            elif isinstance(acao, AcaoUsuario):
                aceita = getattr(self.motor, "aceita", None)
                if aceita is not None and not aceita(acao):
                    self.rejeitados += 1
                    continue
                self.motor.observar(acao)
            else:
                raise TypeError(f"acao invalida vinda do dono: {acao!r}")
            self.gasto += 1


def simular_vida_fisico(dono, politica, semente: int, dias: int, orcamento: int, rotulo_dono: str, fabrica_motor, carinho=None):
    """O mundo.simular_vida_mundo com o CanalSemEnsino (PMF-3): o dono (embrulhado pelo DonoComLugar) cuida pelos gestos do mundo, que
    gastam o orcamento, e o elogio e a bronca dele ficam fora. A rng do dono e a de sempre (`dono`, semente, rotulo do dono: igual em todo
    braco). Devolve (motor, sinais retirados)."""
    cfg, cd = CONFIG_PADRAO, CONFIG_DONOS
    total_ticks = dias * TICKS_POR_DIA
    if total_ticks % cd.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total_ticks // cd.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    if not isinstance(motor, MotorMundo) or not motor.cmf.ligada:
        raise ValueError("simular_vida_fisico precisa do MotorMundo com o mundo ligado")
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono))
    canal = CanalSemEnsino(motor, orcamento, cd.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cd.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
        if carinho is not None:                  # banheiro (#265): o carinho depois das acoes do dono do passo, fora do orcamento
            for acao in carinho.acoes(motor.estado()):
                motor.observar(acao)
    canal.fechar()
    return motor, canal.retirados


def sondar_metabolismo(corpo, destino: list) -> None:
    """A sonda do metabolismo no replay de medicao, so de leitura: embrulha o `passo` do corpo e anota, a cada tick, (tick do pet no
    comeco do tick, dormindo, combustivel e reserva no fim do tick). Nao muda nada do corpo (o replay de medicao e conferido bit a bit)."""
    original = corpo.passo

    def passo(antes, *a, **kw):
        r = original(antes, *a, **kw)
        destino.append((antes.tick, bool(antes.dormindo), corpo.q["combustivel"], corpo.q["reserva"]))
        return r
    corpo.passo = passo


def comeu_fruta_e2(passo: dict) -> bool:
    """A decisao tem o sinal da E2 (o humor nos drives): a fruta comida e a acao foi COMER, a regra do cerebro (lobos.consequencia_mundo
    e o _creditar_corpo). No mundo fisico o motor avisa `fruta_comida` tambem no "achou e comeu" do explorar, e o cerebro credita esse
    explorar com o sinal do N3, sem o humor (MUNDO-CALIBRACAO, 2026-10-12); fora do mundo fisico, so o comer come fruta."""
    return passo["fruta"] is not None and passo["acao"] == AcaoPet.COMER.value


class _Registro:
    """Embrulha a politica do braco no replay de medicao: anota cada decisao (tick, estado como o dono o julga, acao), a
    amostra de estado (em privacao, saude), os sinais do dono que chegaram ao aprendiz ate ali e os que o dono deu. So le;
    repassa tudo."""

    def __init__(self, interna: PoliticaDoBraco) -> None:
        self.interna = interna
        self.nome = interna.nome
        self._tick_ultimo_cuidado = 0
        self.decisoes: list[tuple[int, dict, str]] = []
        self.amostras: list[tuple[bool, float]] = []
        self.sinais_na_decisao: list[int] = []
        self.sinais_do_dono = 0
        self.bola: list[tuple[bool, str, str]] = []      # (bola no cenario, regra do instinto/impulso, acao), por decisao
        self.vetores: list[tuple] = []                     # (indice, fome, higiene, energia, humor), por decisao
        self.espacos: list[tuple] = []                     # N6: (frutas no curto, frutas no longo prazo) depois de cada decisao
        self.acordado: list[bool] = []                     # mundo fisico: o pet acordado na decisao (as horas acordado da taxa media)
        # adendo 2 do corpo: por decisao observada, o tick, a regra e o estado antes e depois da propria acao (na fruta, o depois e o
        # estado logo depois de comer, o mesmo da E2)
        self.passos_sinal: list[dict] = []
        self.corpo: list = []                              # corpo: a PercepcaoCorpo de cada decisao (None sem o corpo)
        self.carinhos: list = []                           # gestos: (tick, PercepcaoCorpo antes, depois) de cada carinho pelo corpo
        self._decisao: tuple | None = None

    @property
    def sinais(self) -> int:
        return self.interna.sinais_entregues

    def agir(self, obs, rng):
        acao = self.interna.agir(obs, rng)
        v = obs.vetor_estado
        estado = {"fome": v[0], "higiene": v[1], "energia": v[2], "tick_do_dia": int(round(v[7] * TICKS_POR_DIA))}
        self.decisoes.append((obs.ticks_desde_cuidado + self._tick_ultimo_cuidado, estado, acao.value))
        self.amostras.append((Estado(fome=v[0], higiene=v[1], energia=v[2]).em_privacao(CONFIG_PADRAO), v[4]))
        self.sinais_na_decisao.append(self.interna.sinais_entregues)
        self.bola.append((obs.bola > 0.0, self.interna.ultima_regra, acao.value))
        self.vetores.append((len(self.vetores), v[0], v[1], v[2], v[3]))
        self.acordado.append(v[6] == 0.0)
        self.corpo.append(obs.corpo)                       # corpo: os receptores da decisao (None sem o corpo)
        self._decisao = (self.decisoes[-1][0], self.interna.ultima_regra)
        mem = getattr(self.interna.cerebro, "_memoria", None)   # N6, so le: a memoria dos lobos depois de promover (o que a decisao viu)
        if mem is not None:
            self.espacos.append((tuple(e["fruta"] for e in mem.curto), tuple(e["fruta"] for e in mem.longo)))
        return acao

    def observar(self, transicao) -> None:
        tick, regra = self._decisao
        self.passos_sinal.append({"tick": tick, "regra": regra, "k": len(self.decisoes) - 1, "acao": transicao.acao.value,
                                  "antes": transicao.observacao.vetor_estado,
                                  "depois": transicao.observacao_seguinte.vetor_estado, "fruta": None,
                                  "antes_corpo": transicao.observacao.corpo, "depois_corpo": None})
        self.interna.observar(transicao)

    def consequencia_corpo(self, acao, ocorrido: dict, obs_depois) -> None:
        """O gancho do MotorCorpo (uma chamada por decisao, logo depois dos estimulos da propria acao): so anota os receptores de
        depois na decisao observada e repassa (o cerebro sem o gancho, como o instinto, nao recebe nada)."""
        if not self.passos_sinal or self.passos_sinal[-1]["depois_corpo"] is not None:
            raise RuntimeError("corpo: gancho de consequencia sem decisao observada (ou o segundo na mesma decisao)")
        self.passos_sinal[-1]["depois_corpo"] = obs_depois.corpo
        gancho = getattr(self.interna, "consequencia_corpo", None)
        if gancho is not None:
            gancho(acao, ocorrido, obs_depois)

    def fruta_comida(self, fruta: str, obs_depois) -> None:
        """O gancho da E2: a decisao de comer a fruta tem o sinal do estado logo depois de comer. So anota e repassa (o cerebro sem o
        gancho, como o instinto, nao recebe nada, como antes)."""
        ultimo = self.passos_sinal[-1]
        if ultimo["fruta"] is not None:
            raise RuntimeError("duas frutas comidas na mesma decisao")
        ultimo["depois"], ultimo["fruta"] = obs_depois.vetor_estado, fruta
        aviso = getattr(self.interna, "fruta_comida", None)
        if aviso is not None:
            aviso(fruta, obs_depois)

    def receber_acao_dono(self, acao, tick) -> None:
        self._tick_ultimo_cuidado = tick          # toda acao do dono zera o relogio de cuidado (state.aplicar_acao_usuario)
        self.sinais_do_dono += acao.value in SINAIS_DO_DONO
        self.interna.receber_acao_dono(acao, tick)

    def mudanca_no_corpo(self, obs_antes, obs_depois) -> None:
        """O carinho com `gestos` (o MotorCorpo nao o passa por `receber_acao_dono`): e contato e zera o relogio de cuidado no instante
        dele, o `ticks_desde_cuidado` do `obs_antes` (a conta do cerebro). So acerta o relogio, anota os receptores (as medidas do carinho
        do banheiro) e repassa."""
        self._tick_ultimo_cuidado += obs_antes.ticks_desde_cuidado
        self.carinhos.append((self._tick_ultimo_cuidado, obs_antes.corpo, obs_depois.corpo))
        self.interna.mudanca_no_corpo(obs_antes, obs_depois)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _julgar(estado: dict, acao: str) -> int:
    return julgar_acao({**estado, "acao_atual": acao}, CONFIG_DONOS)


# ------------------------------------------------------------------ orquestrador


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def validar_config(cfg: dict) -> dict:
    faltam = {"bracos", "donos", "dias", "orcamento", "sonda", "bootstrap"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config: ou 'sementes' (x 'genomas') ou 'unidades' (bases x K derivadas), um dos dois")
    if "unidades" in cfg:
        u = cfg["unidades"]
        if not {"bases", "k"} <= set(u) <= {"bases", "k", "prefixo"} or "genomas" in cfg:
            raise ValueError(f"unidades fora do formato {{'bases': [...], 'k': K, 'prefixo'?}} (sem 'genomas'): {u}")
        unidades_derivadas(u["bases"], int(u["k"]), u.get("prefixo", "experimento-maior"))
        fora = sorted(set(u["bases"]) - SEMENTES_TESTE)
        if fora:
            plano = cfg.get("plano")
            if not plano or not (RAIZ / plano).is_file():
                raise SementeSemPlano(f"bases {fora} fora das dos testes: precisa do plano de analise registrado (campo 'plano')")
    if "ponto" in cfg and cfg["ponto"] not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {cfg['ponto']!r}: so {sorted(PONTOS_APRENDIZ)}")
    if "montagem" in cfg and cfg["montagem"] not in MONTAGENS:
        raise ValueError(f"montagem {cfg['montagem']!r}: so {MONTAGENS}")
    for b in cfg["bracos"]:
        braco_de(b)
    for m in cfg.get("mundos", ["padrao"]):
        mundo_de(m)
    fisicos = [m for m in cfg.get("mundos", ["padrao"]) if mundo_de(m).fisico is not None]
    com_corpo_ = [b for b in cfg["bracos"] if BRACOS[b].regime in ("quimica", "corpo")]     # os bracos ja passaram pelo braco_de
    com_gestos = [b for b in cfg["bracos"] if BRACOS[b].gestos is not None]
    sem_gestos_ = [m for m in cfg.get("mundos", ["padrao"]) if mundo_de(m).fisico is not None or mundo_de(m).bola == "a1"]
    if com_gestos and sem_gestos_:
        raise ValueError(f"bracos com os gestos do dono {com_gestos} nos mundos {sem_gestos_}: os gestos ficam fora do mundo fisico e do "
                         "bola_a1")
    banheiro = [b for b in cfg["bracos"] if BRACOS[b].banheiro is not None]
    if banheiro and any(mundo_de(m).fisico is None for m in cfg.get("mundos", ["padrao"])):
        raise ValueError(f"bracos {banheiro}: o banheiro so no mundo fisico")
    tapa_x = [b for b in cfg["bracos"] if BRACOS[b].gestos == "tapa_fruta"]
    if tapa_x and any(not mundo_de(m).frutas for m in cfg.get("mundos", ["padrao"])):
        raise ValueError(f"bracos {tapa_x}: o tapa na fruta X so nos mundos das frutas")
    if "corpo" in cfg:
        if set(cfg["corpo"]) & set(SUBCHAVES_CORPO):
            raise ValueError(f"'corpo' troca os numeros da ConfigCorpo, nao as sub-chaves {SUBCHAVES_CORPO}: o regime e do braco")
        if not com_corpo_:
            raise ValueError("'corpo' sem braco com corpo (regime quimica ou corpo)")
    if fisicos:
        lugares = cfg.get("lugares")
        if not lugares or len(set(lugares)) != len(lugares) or any(lg not in ESTILOS_LUGAR for lg in lugares):
            raise ValueError(f"o mundo fisico pede 'lugares', sem repetir, de {ESTILOS_LUGAR}: {lugares}")
    elif "lugares" in cfg:
        raise ValueError("'lugares' so existe com o mundo fisico")
    if "mundo" in cfg:
        if not fisicos:
            raise ValueError("'mundo' (a ConfigMundo) so existe com o mundo fisico")
        replace(CONFIG_MUNDO_LIGADA, **cfg["mundo"])
    for a in cfg.get("acoplados", []):
        if set(a) != {"origem", "destino", "filtro"}:
            raise ValueError(f"acoplado fora do formato: {a}")
        try:
            filtro_de(a["filtro"])
        except KeyError as e:
            raise ValueError(f"acoplado fora do formato: {a}") from e
        braco_de(a["destino"])
        if a["origem"] not in cfg["bracos"]:
            raise ValueError(f"acoplado de um braco que nao roda: {a['origem']}")
    genomas = [g for g in cfg.get("genomas", [None]) if g is not None]
    usadas = set(cfg.get("sementes", [])) | set(genomas) | set(cfg.get("unidades", {}).get("bases", []))
    for ini, fim, motivo in FAIXAS_QUEIMADAS:
        queimadas = sorted(x for x in usadas if ini <= x <= fim)
        if queimadas:
            raise SementeSemPlano(f"sementes/bases {queimadas} na faixa queimada {ini}...{fim} ({motivo}): nao usar para nada")
    fora = sorted((set(cfg.get("sementes", [])) | set(genomas)) - SEMENTES_TESTE)
    if fora:
        plano = cfg.get("plano")
        if not plano or not (RAIZ / plano).is_file():
            raise SementeSemPlano(f"sementes {fora} fora das dos testes {sorted(SEMENTES_TESTE)}: precisa do plano de analise "
                                  "registrado (campo 'plano', arquivo no repositorio)")
    return cfg


def cfg_lobos_do_ponto(ponto: str = PONTO_PADRAO, troca: dict | None = None) -> ConfigLobos:
    """O aprendiz de um ponto nomeado (PONTOS_APRENDIZ), com os campos de `troca` por cima. Ponto desconhecido falha alto."""
    if ponto not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {ponto!r}: so {sorted(PONTOS_APRENDIZ)}")
    base = replace(CONFIG_LOBOS_APRENDIZ, **PONTOS_APRENDIZ[ponto])
    return replace(base, **troca) if troca else base


def bancada_da_config(cfg: dict) -> Bancada:
    """A Bancada da config: os padroes, e o que as chaves "consequencia", "ponto" e "lobos" (o ponto nomeado, e por cima dele os campos
    da chave "lobos"; sem "ponto", o L1 = CONFIG_LOBOS_APRENDIZ) e "frutas" (sobre o CONFIG_FRUTAS_LIGADA; listas do JSON viram tuplas)
    trocam. Sem essas chaves, a bancada de sempre (REVISAO-APRENDIZ)."""
    cc = CONFIG_CONSEQUENCIA if "consequencia" not in cfg else replace(CONFIG_CONSEQUENCIA, **cfg["consequencia"])
    kw = {"cfg_consequencia": cc}
    if "lobos" in cfg or "ponto" in cfg:
        kw["cfg_lobos"] = cfg_lobos_do_ponto(cfg.get("ponto", PONTO_PADRAO), cfg.get("lobos"))
    if cfg.get("julgamento_fruta"):
        kw["julgamento_fruta"] = True
    if "montagem" in cfg:
        kw["montagem"] = cfg["montagem"]
    tupla = lambda v: tuple(tupla(x) for x in v) if isinstance(v, list) else v  # noqa: E731
    if "frutas" in cfg:
        kw["cfg_frutas"] = replace(CONFIG_FRUTAS_LIGADA, **{k: tupla(v) for k, v in cfg["frutas"].items()})
    if "mundo" in cfg:
        kw["cfg_mundo"] = replace(CONFIG_MUNDO_LIGADA, **{k: tupla(v) for k, v in cfg["mundo"].items()})
    if "corpo" in cfg:
        kw["cfg_corpo"] = replace(CONFIG_CORPO_QUIMICA, **{k: tupla(v) for k, v in cfg["corpo"].items()})
    return Bancada(int(cfg["dias"]), int(cfg["orcamento"]), **kw)


def rodar(cfg: dict, pasta: Path) -> dict:
    """Vidas de todos os bracos x donos x sementes (x genomas x mundos), gravadas e rejogadas do disco; os acoplados; as
    medidas por vida e as tabelas braco x condicao por dono e medida."""
    validar_config(cfg)
    bancada = bancada_da_config(cfg)
    dir_vidas = pasta / "vidas"
    vidas: dict[str, VidaBancada] = {}

    def guardar(v: VidaBancada) -> None:
        _gravar(dir_vidas / f"{v.nome}.jsonl", v.motor.log.para_jsonl())
        _gravar(dir_vidas / f"{v.nome}.politica.json", _interno(v.motor))
        bancada.conferir_replay(v, (dir_vidas / f"{v.nome}.jsonl").read_text(encoding="utf-8"))
        vidas[v.nome] = v

    if "unidades" in cfg:
        unidades = unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]),
                                      cfg["unidades"].get("prefixo", "experimento-maior"))
        pares = [(u["genoma"], u["semente"]) for u in unidades]
    else:
        unidades = []
        pares = [(g, int(s)) for g in cfg.get("genomas", [None]) for s in cfg["sementes"]]
    da_unidade = {(u["genoma"], u["semente"]): {"base": u["base"], "k": u["k"]} for u in unidades}
    for (g, s), mundo, dono, braco in product(pares, cfg.get("mundos", ["padrao"]), cfg["donos"], cfg["bracos"]):
        for lugar in (cfg["lugares"] if mundo_de(mundo).fisico is not None else [None]):   # mundo fisico: a celula e dono x lugar
            guardar(bancada.vida(EspecVida(dono, braco, s, g, mundo, lugar=lugar)))
    origens = list(vidas.values())
    for a in cfg.get("acoplados", []):
        for v in origens:
            if v.espec.braco == a["origem"]:
                guardar(bancada.acoplar(v, a["destino"], a["filtro"]))
    # o piso do tempo ate aprender e o acerto do P0 na mesma celula (o prior herdado); sem P0 na config, o da propria vida
    medidas, piso, taxa_p0 = {}, {}, {}
    for nome, v in sorted(vidas.items()):
        if v.espec.braco == "P0" and v.origem is None:
            medidas[nome] = bancada.medir(v, cfg["sonda"])
            piso[v.espec.celula] = medidas[nome]["acerto_total"]
            if medidas[nome]["frutas"] is not None:
                taxa_p0[v.espec.celula] = medidas[nome]["frutas"]["taxa_fruta_ruim"]["total"]["taxa"]
    for nome, v in sorted(vidas.items()):
        if nome not in medidas:
            medidas[nome] = bancada.medir(v, cfg["sonda"], piso.get(v.espec.celula), taxa_p0.get(v.espec.celula))
    for nome, v in vidas.items():
        medidas[nome]["unidade"] = da_unidade.get((v.espec.genoma, v.espec.semente))
    tabelas = tabelas_braco_condicao(medidas, cfg["bootstrap"])
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "tabelas.json", _dump(tabelas))
    _gravar(pasta / "dominancia.json", _dump(tabela_dominancia(medidas)))
    if any(m.get("banheiro") is not None for m in medidas.values()):
        _gravar(pasta / "banheiro.json", _dump(tabela_banheiro(medidas)))
    _gravar(pasta / "meta.json", _dump(meta(cfg)))
    return {"vidas": vidas, "medidas": medidas, "tabelas": tabelas}


def tabelas_braco_condicao(medidas: dict, boot: dict) -> dict:
    """Por dono e medida: tabela braco x condicao, unidade = vida (semente x genoma). A coluna e "condicao/mundo"
    ("casado/padrao", "casado/casado_frutas", "descasado/descasado", "mutavel/mutavel"...): dois mundos da mesma condicao nunca se
    misturam numa celula. Nos mundos das frutas, tambem as medidas do N5 (MEDIDAS_FRUTAS: a taxa da fruta ruim no inicio e no final
    e os consumos ate a metade do caminho), pela tabela parcial, que conta as vidas sem valor em vez de sumir com elas."""
    out = {}
    for dono in sorted({m["dono"] for m in medidas.values()}):
        out[dono] = {}
        for medida in MEDIDAS_TABELA:
            valores: dict[tuple[str, str], list[float]] = {}
            for m in medidas.values():
                if m["dono"] == dono:
                    valores.setdefault((m["braco"], _coluna(m)), []).append(m[medida])
            out[dono][medida] = tabela_braco_condicao(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
        # as medidas do N5 (plano, secao 5), so nos mundos das frutas: podem faltar numa vida (janela sem consumo, P0 sem consumo)
        frutas = [m for m in medidas.values() if m["dono"] == dono and m["frutas"] is not None]
        if frutas:
            for medida, f in MEDIDAS_FRUTAS.items():
                valores = {}
                for m in frutas:
                    valores.setdefault((m["braco"], _coluna(m)), []).append(f(m["frutas"]))
                out[dono][medida] = tabela_braco_condicao_parcial(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
        # as medidas do mundo fisico (PLANO_ANALISE_V2_MUNDO_FISICO, secao 5), com a coluna por lugar
        fisicas = [m for m in medidas.values() if m["dono"] == dono and m.get("mundo_fisico") is not None]
        if fisicas:
            for medida, f in MEDIDAS_MUNDO.items():
                valores = {}
                for m in fisicas:
                    valores.setdefault((m["braco"], _coluna(m)), []).append(f(m["mundo_fisico"]))
                out[dono][medida] = tabela_braco_condicao_parcial(valores, boot["reamostragens"], boot["semente"], boot["nivel"])
    return out


def tabela_dominancia(medidas: dict) -> dict:
    """Adendo 2 do plano do corpo (A2.2, A2.3, A2.6), na janela: por braco x condicao/mundo x tipo de decisao (tempo livre e o resto),
    f_d por unidade (as celulas da unidade somadas: os donos e, no mundo fisico, os lugares; f_d = lideradas / decisoes com sinal), a
    leitura (metrics.leitura_dominancia: o IC95 de f_d por bootstrap sobre as unidades, 10.000 reamostragens, semente 4242; "domina"
    com o limite inferior acima de 0,50), a parcela agregada soma|c_d| / soma soma|c| e a contribuicao com sinal. Regra de leitura,
    fora do Holm. `origem`: "sinal" nos bracos que aprendem pela consequencia, "sonda" nos outros (o P0)."""
    grupos: dict = {}
    for m in medidas.values():
        dom = m.get("dominancia")
        if dom is None:
            continue
        g = grupos.setdefault((m["braco"], f"{m['condicao']}/{m['mundo']}"), {"origem": dom["origem"], "unidades": {}})
        if g["origem"] != dom["origem"]:
            raise RuntimeError(f"{m['vida']}: origem da dominancia diferente no mesmo braco")
        u = g["unidades"].setdefault((m["genoma"], m["semente"]), {})
        for tipo, r in dom["na_janela"].items():
            t = u.setdefault(tipo, {"n": 0, "lideradas": {}, "soma_abs": {}, "contribuicao": {}})
            t["n"] += r["n"]
            for chave in ("lideradas", "soma_abs", "contribuicao"):
                for d, v in r[chave].items():
                    t[chave][d] = t[chave].get(d, 0) + v
    out: dict = {}
    for (braco, coluna), g in sorted(grupos.items()):
        cel = out.setdefault(braco, {}).setdefault(coluna, {"origem": g["origem"], "unidades": len(g["unidades"])})
        for tipo in ("tempo_livre", "resto"):
            us = [u[tipo] for _, u in sorted(g["unidades"].items(), key=lambda x: (str(x[0][0]), x[0][1])) if tipo in u]
            drives = sorted({d for u in us for d in u["lideradas"]})
            f = {d: [(u["lideradas"].get(d, 0) / u["n"]) if u["n"] else None for u in us] for d in drives}
            soma = {d: sum(u["soma_abs"].get(d, 0) for u in us) for d in drives}
            total = sum(soma.values())
            cel[tipo] = {"decisoes": sum(u["n"] for u in us), "f_por_unidade": f, "leitura": leitura_dominancia(f),
                         "parcela": {d: (soma[d] / total) if total else None for d in drives},
                         "contribuicao": {d: sum(u["contribuicao"].get(d, 0) for u in us) for d in drives}}
    return out


def _coluna(m: dict) -> str:
    """A coluna da tabela: "condicao/mundo", e no mundo fisico "condicao/mundo/lugar" (o lugar e parte da celula, PMF-4)."""
    base = f"{m['condicao']}/{m['mundo']}"
    return base if m.get("lugar") is None else f"{base}/{m['lugar']}"


MEDIDAS_FRUTAS = {
    "taxa_fruta_ruim_inicio": lambda f: f["taxa_fruta_ruim"]["inicio"]["taxa"],
    "taxa_fruta_ruim_final": lambda f: f["taxa_fruta_ruim"]["final"]["taxa"],
    "consumos_ate_metade": lambda f: f["consumos_ate_metade"]["consumos"],
}
MEDIDAS_MUNDO = {
    "d_fe": lambda f: f["d_fe"]["d_fe"],
    "privacao_janela": lambda f: f["cuidado"]["privacao"],
    "permanencia_media": lambda f: f["permanencia_media"],
}


def meta(cfg: dict) -> dict:
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    return {"config": cfg, "ponto": cfg.get("ponto", PONTO_PADRAO),
            "cfg_lobos": cfg_lobos_do_ponto(cfg.get("ponto", PONTO_PADRAO), cfg.get("lobos")).__dict__,
            "python": platform.python_version(), "plataforma": platform.platform(),
            "engine_sha256": sha256_engine(), "lobos_sha256": _sha(RAIZ / "digilab" / "policies" / "lobos.py"),
            "config_sha256": _sha(RAIZ / "digilab" / "config.py"), "bancada_sha256": _sha(Path(__file__)),
            "metrics_sha256": _sha(RAIZ / "digilab" / "metrics.py"), "mundo_sha256": _sha(RAIZ / "digilab" / "mundo.py")}


# ================================================================== dois pets: a bancada do grupo (TAREFA_V2_DOIS_PETS, etapa 5)
# PLANO_ANALISE_V2_DOIS_PETS, secoes 2 a 4: o grupo como celula, com um dono (o atencioso, so com o cuidado, PMF-3) e o orcamento por pet
# (DP-7, a validacao inicial), pelo `simular_grupo` do #257. O cerebro e o A do ponto e da montagem da bancada, com o alvo aprendido (#255).
# A visao, o toque e a disputa entre os pets (etapa 3, do A, #263) e as entradas sociais e o modelo dos outros no cerebro (etapa 4, a
# segunda metade, do B, #266) estao na main: o cerebro do grupo os liga, e as medidas sociais e as do modelo saem dos registros. Com os
# canais da montagem completa, a rota do humor no mundo fisico (#269, `presenca_fruta_mundo`) tambem fica ligada.

ROTULO_RUIM = "dois-pets-ruim"               # o tipo que faz mal na unidade (plano, secao 2)
ROTULO_EMBARALHA = "dois-pets-embaralha"     # o desarranjo do A embaralhado (plano, secao 3)
DECISOES_POR_DIA = TICKS_POR_DIA // CONFIG_PADRAO.intervalo_decisao_ticks
if DECISOES_POR_DIA * CONFIG_PADRAO.intervalo_decisao_ticks != TICKS_POR_DIA:   # pragma: no cover - 1440 / 15
    raise RuntimeError("o dia nao e multiplo do intervalo de decisao")
BRACO_DO_B = "P1"                            # todo B e P1 (plano, secao 3)
JANELA_PRIMARIA_DIAS = 7                     # a R_B nos 7 primeiros dias do B (PDP-2)


def tipo_ruim(semente: int) -> str:
    """O tipo de fruta que faz mal na unidade (plano, secao 2): uniforme entre as tres, pela rng propria derivar_semente("dois-pets-ruim",
    s), um sorteio. Nao toca outra rng."""
    return FRUTAS[random.Random(derivar_semente(ROTULO_RUIM, semente)).randrange(len(FRUTAS))]


def desarranjo_dois_pets(semente: int) -> dict:
    """O desarranjo pi do A embaralhado (plano, secao 3), como o desarranjo_n6: um dos dois ciclos de {a, b, c}, pela rng propria
    derivar_semente("dois-pets-embaralha", s). Nenhuma fruta em si mesma."""
    if len(FRUTAS) != 3:                     # pragma: no cover - o mundo tem tres tipos de fruta
        raise ValueError("desarranjo_dois_pets escrito para tres frutas")
    passo = 1 + random.Random(derivar_semente(ROTULO_EMBARALHA, semente)).randrange(len(FRUTAS) - 1)
    return {f: FRUTAS[(i + passo) % len(FRUTAS)] for i, f in enumerate(FRUTAS)}


def efeito_dois_pets(ruim: str, cf: ConfigFrutas) -> dict:
    """O efeito de cada tipo de fruta (plano, secao 2): o ruim com o `efeito_humor_ruim`, os outros dois neutros (`efeito_humor_neutro`).
    Cada tipo tem arvores no jardim e na mata (LAYOUT_MUNDO_PADRAO)."""
    if ruim not in FRUTAS:
        raise ValueError(f"tipo ruim {ruim!r}: so {FRUTAS}")
    return {f: (cf.efeito_humor_ruim if f == ruim else cf.efeito_humor_neutro) for f in FRUTAS}


class MotorMundoTroca(MotorMundo):
    """O MotorMundo do A embaralhado (plano, secao 3): nos K dias o efeito das frutas e o desarranjado (o tipo pi(ruim) faz mal) e, no dia
    K, o mundo passa ao efeito verdadeiro. So no grupo: a troca vem no fim do avanco que chega ao tick do mundo `tick_troca` (o grupo avanca
    em passos do dono, e o dia e multiplo do passo), entao nenhum tick do mundo >= tick_troca roda com o efeito de antes; um avanco que
    passasse do tick falha alto. Na entrada do B (o mesmo tick) os dois ja tem o efeito verdadeiro, como o Grupo confere. A troca fica no
    registro derivado (`troca`) e o replay a refaz pela mesma fabrica."""

    def __init__(self, *a, tick_troca: int, efeito_depois: dict, **kw) -> None:
        super().__init__(*a, **kw)
        if not self.cmf.ligada or self.mundo is None or kw.get("mundo") is None:
            raise ValueError("o A embaralhado so existe no grupo (o MotorMundo ligado sobre o Mundo do grupo)")
        if type(tick_troca) is not int or tick_troca <= self.entrada_mundo or tick_troca % TICKS_POR_DIA:
            raise ValueError(f"a troca e num inicio de dia do mundo depois da entrada do pet: {tick_troca!r}")
        if set(efeito_depois) != set(FRUTAS):
            raise ValueError(f"efeito_depois precisa de {FRUTAS}: {sorted(efeito_depois)}")
        self.tick_troca = tick_troca
        self.efeito_antes = dict(self.efeito_frutas)
        self.efeito_depois = dict(efeito_depois)
        self.troca: dict | None = None

    def efeito_no_tick(self, tick_mundo: int) -> dict:
        return self.efeito_antes if tick_mundo < self.tick_troca else self.efeito_depois

    def _fechar_avanco(self) -> None:
        super()._fechar_avanco()
        agora = self.entrada_mundo + self._estado.tick
        if self.troca is None and agora >= self.tick_troca:
            if agora != self.tick_troca:
                raise RuntimeError(f"o avanco passou da troca do efeito (tick {self.tick_troca}, agora {agora})")
            self.efeito_frutas = dict(self.efeito_depois)
            self.troca = {"tick": agora, "antes": dict(self.efeito_antes), "depois": dict(self.efeito_depois)}


@dataclass(frozen=True)
class BracoGrupo:
    """Um braco do plano dos dois pets (secao 3): o companheiro do B e quando ele entra. O B (P1) entra no dia K e vive os `dias` da
    bancada; o A entra no tick 0 (informativo, embaralhado) ou junto com o B (ingenuo). O "A-so" e o da calibracao do K (secao 5): o A
    informativo sozinho, sem B, os `dias` da bancada."""

    rotulo: str
    companheiro: str | None          # None (sem A), "informativo", "embaralhado" ou "ingenuo"
    a: str | None                    # o braco do A na bancada: "P1" ou "P0"; None sem A
    a_entra: str | None              # "inicio" (tick 0) ou "dia_k" (com o B); None sem A
    b: bool = True                   # o B entra no dia K


BRACOS_GRUPO = {
    "B-so": BracoGrupo("B-so", None, None, None),
    "B+Ainf": BracoGrupo("B+Ainf", "informativo", "P1", "inicio"),
    "B+Aemb": BracoGrupo("B+Aemb", "embaralhado", "P1", "inicio"),
    "B+Aing": BracoGrupo("B+Aing", "ingenuo", "P0", "dia_k"),
    "A-so": BracoGrupo("A-so", "informativo", "P1", "inicio", b=False),
}


@dataclass(frozen=True)
class EspecGrupo:
    """Um grupo da bancada: o braco, a semente do grupo s (o mundo e o A; o B pela derivacao do segundo pet, `sementes_do_grupo`), o K, o
    dono e o lugar dele (plano, secao 2: o atencioso, no comedouro). Sem genoma: o temperamento neutro, como o mundo fisico sem genoma."""

    braco: str
    semente: int
    k: int
    dono: str = "atencioso"
    lugar: str = "comedouro"
    mundo: str = "fisico"

    @property
    def nome(self) -> str:
        m = "" if self.mundo == "fisico" else f"~{self.mundo}"
        return f"{self.dono}-{self.braco}{m}~{self.lugar}~K{self.k}@{self.semente}"


@dataclass
class VidaGrupo:
    espec: EspecGrupo
    grupo: Grupo
    interacoes: dict                 # por pet: o gasto do dono (o orcamento inteiro, conferido pelo canal)
    retirados: dict                  # por pet: os sinais do dono que o filtro sem_ensino ao vivo nao deixou chegar (PMF-3)

    @property
    def nome(self) -> str:
        return self.espec.nome


class _RegistroGrupo(_Registro):
    """O _Registro do replay de medicao do grupo, mais os pesos do alvo aprendido no fim de cada dia do pet (antes da primeira decisao do
    dia seguinte; o do ultimo dia, `fim`). So le."""

    def __init__(self, interna: PoliticaDoBraco) -> None:
        super().__init__(interna)
        self.pesos_alvo_dia: list = []
        self.modelo_dia: list = []

    def pesos_alvo(self):
        w = getattr(self.interna.cerebro, "_pesos_alvo_mundo", None)
        return {k: dict(t) for k, t in w.items()} if w else None

    def modelo(self):
        """o modelo dos outros (so registrado, #266) como o cerebro o serializa: por outro, a familiaridade, a confianca e a afinidade"""
        m = getattr(self.interna.cerebro, "_modelo", None)
        return None if m is None else m.para_dict()["outros"]

    def agir(self, obs, rng):
        k = len(self.decisoes)
        if k and k % DECISOES_POR_DIA == 0:
            self.pesos_alvo_dia.append(self.pesos_alvo())
            self.modelo_dia.append(self.modelo())
        return super().agir(obs, rng)

    def fim(self) -> None:
        self.pesos_alvo_dia.append(self.pesos_alvo())
        self.modelo_dia.append(self.modelo())


def _validar_espec_grupo(eg: EspecGrupo) -> BracoGrupo:
    if eg.braco not in BRACOS_GRUPO:
        raise KeyError(f"braco do grupo desconhecido {eg.braco!r}: {sorted(BRACOS_GRUPO)}")
    bg = BRACOS_GRUPO[eg.braco]
    if mundo_de(eg.mundo).fisico is None:
        raise ValueError(f"{eg.nome}: o grupo vive no mundo fisico, nao {eg.mundo!r}")
    if eg.lugar not in ESTILOS_LUGAR:
        raise ValueError(f"lugar {eg.lugar!r}: so {ESTILOS_LUGAR}")
    if type(eg.k) is not int or eg.k < 0:
        raise ValueError(f"K tem de ser inteiro >= 0: {eg.k!r}")
    if not bg.b and eg.k != 0:
        raise ValueError(f"{eg.braco}: sem B nao ha dia K (K = 0)")
    if bg.a_entra == "inicio" and bg.b and eg.k < 1:
        raise ValueError(f"{eg.braco}: o A vive K >= 1 dias sozinho antes do B")
    return bg


def _entradas(eg: EspecGrupo) -> list[tuple[str, str, int]]:
    """(id, braco na bancada, tick do mundo da entrada) de cada pet do grupo, na ordem dos ids."""
    bg = BRACOS_GRUPO[eg.braco]
    dia_k = eg.k * TICKS_POR_DIA
    out = []
    if bg.a is not None:
        out.append(("A", bg.a, 0 if bg.a_entra == "inicio" else dia_k))
    if bg.b:
        out.append(("B", BRACO_DO_B, dia_k))
    return out


def _resumo_grupo(g: Grupo) -> tuple:
    """O resumo do Grupo, a troca do A embaralhado e a projecao de cada pet (o log de hoje do pet, igual ao do motor)."""
    for i, m in g.motores.items():
        if g.registro.projecao(i).para_jsonl() != m.log.para_jsonl():
            raise ReplayDivergiu(f"a projecao do registro do grupo para {i} nao e o log do motor")
    return (g.registro.para_jsonl(), g.resumo(), {i: getattr(m, "troca", None) for i, m in g.motores.items()})


# o passo 0 da calibracao do corpo (PLANO_ANALISE_V2_CORPO_DRIVES, adendo 3, A3.2; ME-7): so o P0-q, com o metabolismo, nas 20 unidades da
# calibracao (bases 33101...33505, K = 4) e nas 8 celulas; o gasto (basal e das atividades sobre o combustivel) x {1/2, 1, 2}, partindo dos
# PROPOSTOS (375 acordado, 187 dormindo); fica o ponto mais perto de 1 (|log2|) com a fracao do tempo acordado com a falta em [0,05; 0,30],
# nas 8 celulas juntas; sem nenhum, o de fracao mais perto do centro da faixa, "nao fechou". A faixa e PROPOSTA, SEM FONTE.
PASSO0_MULTIPLICADORES = ((1, 2), (1, 1), (2, 1))           # (num, den): 1/2, 1, 2
PASSO0_FAIXA = (0.05, 0.30)
PASSO0_BRACO = "P0-q"


def _escalar(v: int, num: int, den: int) -> int:
    """v x num/den, arredondado (metade para cima): 375/2 = 188 e 187/2 = 94 (o 1/2 da grade nao e inteiro; registro)"""
    return (v * num + den // 2) // den


def pontos_passo0(cfg: dict) -> list[tuple[str, dict]]:
    """As tres configs do passo 0 a partir da `cfg` (a da calibracao do corpo com o P0-q): o basal (`gasto_basal_acordado`,
    `gasto_basal_dormindo`) x num/den pela chave "corpo". O gasto das atividades sobre o combustivel nao tem fator na ConfigCorpo: falha
    alto com o no `gasto_atividades` (e, sem a entrada, na segunda trava: a fiacao do fator entra com o campo do B)."""
    if cfg.get("bracos") != [PASSO0_BRACO]:
        raise ValueError(f"o passo 0 roda so o {PASSO0_BRACO}: {cfg.get('bracos')}")
    base = ConfigCorpo()
    pontos = []
    for num, den in PASSO0_MULTIPLICADORES:
        corpo = {**cfg.get("corpo", {}), "gasto_basal_acordado": _escalar(base.gasto_basal_acordado, num, den),
                 "gasto_basal_dormindo": _escalar(base.gasto_basal_dormindo, num, den)}
        pontos.append((f"gasto_{num}_{den}", {**cfg, "corpo": corpo}))
    if "gasto_atividades" in NOS_PENDENTES:
        raise NotImplementedError(f"o passo 0 da calibracao do corpo (no gasto_atividades): {NOS_PENDENTES['gasto_atividades']}")
    raise NotImplementedError("o passo 0: a fiacao do fator do gasto das atividades entra com o campo da ConfigCorpo (do B)")


def fracao_falta_passo0(medidas: dict) -> dict:
    """A fracao do tempo acordado com a falta nas 8 celulas juntas (A3.2): a soma dos ticks acordados com falta sobre a soma dos ticks
    acordados, nas vidas do P0-q (sem acoplados) com o metabolismo. Uma vida sem a medida falha alto."""
    falta = acordado = vidas = 0
    for m in medidas.values():
        if m.get("origem") is not None or m["braco"] != PASSO0_BRACO:
            continue
        met = (m.get("corpo") or {}).get("metabolismo")
        if met is None:
            raise ValueError(f"{m['vida']}: sem a medida do metabolismo")
        falta += met["acordado_com_falta"]
        acordado += met["acordado"]
        vidas += 1
    if not acordado:
        raise ValueError("o passo 0 sem tick acordado")
    return {"vidas": vidas, "acordado": acordado, "acordado_com_falta": falta, "fracao": falta / acordado}


def escolha_passo0(fracoes: dict) -> dict:
    """A regra do passo 0 (A3.2, escrita antes): `fracoes` = {(num, den): fracao do tempo acordado com a falta}. Fica o ponto mais perto de
    1 pela |log2(num/den)| com a fracao em PASSO0_FAIXA; no empate (1/2 e 2), o menor gasto (como o "menor m_sobe" da 6.2). Sem nenhum, o
    de fracao mais perto do centro da faixa, com "nao fechou". Ponto fora da grade falha alto."""
    if set(fracoes) != set(PASSO0_MULTIPLICADORES):
        raise ValueError(f"o passo 0 pede os tres pontos {PASSO0_MULTIPLICADORES}: {sorted(fracoes)}")
    lo, hi = PASSO0_FAIXA
    distancia = lambda p: abs(math.log2(p[0] / p[1]))  # noqa: E731
    passam = [p for p in PASSO0_MULTIPLICADORES if lo <= fracoes[p] <= hi]
    if passam:
        p = min(passam, key=lambda q: (distancia(q), q[0] / q[1]))
        return {"ponto": list(p), "fechou": True, "fracao": fracoes[p], "passam": [list(q) for q in passam]}
    centro = (lo + hi) / 2
    p = min(PASSO0_MULTIPLICADORES, key=lambda q: (abs(fracoes[q] - centro), distancia(q), q[0] / q[1]))
    return {"ponto": list(p), "fechou": False, "fracao": fracoes[p], "passam": [], "registro": "nao fechou"}


CHAVES_CONFIG_GRUPO = {"descricao", "plano", "tipo", "bracos", "sementes", "unidades", "k_dias", "dias", "orcamento_por_dia", "dono",
                       "lugar", "ponto", "lobos", "montagem", "consequencia", "mundo"}


def validar_config_grupo(cfg: dict) -> dict:
    """A config da bancada do grupo (`"tipo": "grupo"`). As unidades usam o prefixo `dois_pets`. Fora das sementes dos testes, a run e do
    plano: pede o `plano` e a montagem completa (o cerebro do plano, secao 2, com os canais e a rota do humor do #269)."""
    faltam = {"tipo", "bracos", "k_dias", "dias", "orcamento_por_dia"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG_GRUPO
    if faltam or sobram:
        raise ValueError(f"config do grupo: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["tipo"] != "grupo":
        raise ValueError(f"config do grupo com tipo {cfg['tipo']!r}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config do grupo: ou 'sementes' ou 'unidades' (bases x K derivadas), um dos dois")
    bracos = list(cfg["bracos"])
    if not bracos or len(set(bracos)) != len(bracos) or any(b not in BRACOS_GRUPO for b in bracos):
        raise ValueError(f"bracos do grupo {bracos}: so {sorted(BRACOS_GRUPO)}, sem repetir")
    if "ponto" in cfg and cfg["ponto"] not in PONTOS_APRENDIZ:
        raise ValueError(f"ponto do aprendiz {cfg['ponto']!r}: so {sorted(PONTOS_APRENDIZ)}")
    if "montagem" in cfg and cfg["montagem"] not in MONTAGENS:
        raise ValueError(f"montagem {cfg['montagem']!r}: so {MONTAGENS}")
    if "mundo" in cfg:
        replace(CONFIG_MUNDO_LIGADA, **cfg["mundo"])
    for b in bracos:                             # o K, o dono e o lugar de cada braco
        _validar_espec_grupo(EspecGrupo(b, 101, 0 if not BRACOS_GRUPO[b].b else int(cfg["k_dias"]), cfg.get("dono", "atencioso"),
                                        cfg.get("lugar", "comedouro")))
    criar_dono(cfg.get("dono", "atencioso"))
    if "unidades" in cfg:
        u = cfg["unidades"]
        if set(u) != {"bases", "k", "prefixo"} or u["prefixo"] != "dois_pets":
            raise ValueError(f"unidades do grupo: {{'bases', 'k', 'prefixo': 'dois_pets'}}, nao {u}")
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
        plano = cfg.get("plano")
        if not plano or not (RAIZ / plano).is_file():
            raise SementeSemPlano(f"sementes/bases {fora} fora das dos testes: precisa do plano de analise registrado (campo 'plano')")
        if cfg.get("montagem") != "completa":
            raise ValueError("a run do plano dos dois pets usa o cerebro do plano (secao 2): a montagem completa")
    return cfg


def rodar_grupo(cfg: dict, pasta: Path) -> dict:
    """Os grupos de todos os bracos x unidades, gravados (o registro do grupo em JSONL) e rejogados do disco; as medidas por grupo."""
    validar_config_grupo(cfg)
    bancada = bancada_da_config({**cfg, "orcamento": int(cfg["orcamento_por_dia"]) * int(cfg["dias"])})
    if "unidades" in cfg:
        unidades = unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), cfg["unidades"]["prefixo"])
        sementes = [(u["semente"], {"base": u["base"], "k": u["k"]}) for u in unidades]
    else:
        sementes = [(int(s), None) for s in cfg["sementes"]]
    grupos, medidas = {}, {}
    for (s, unidade), braco in product(sementes, cfg["bracos"]):
        k = int(cfg["k_dias"]) if BRACOS_GRUPO[braco].b else 0
        v = bancada.grupo(EspecGrupo(braco, s, k, cfg.get("dono", "atencioso"), cfg.get("lugar", "comedouro")))
        caminho = pasta / "grupos" / f"{v.nome}.jsonl"
        _gravar(caminho, v.grupo.registro.para_jsonl())
        bancada.conferir_replay_grupo(v, caminho.read_text(encoding="utf-8"))
        grupos[v.nome] = v
        medidas[v.nome] = {**bancada.medir_grupo(v), "unidade": unidade}
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "meta.json", _dump({**meta(cfg), "grupo_sha256": _sha(RAIZ / "digilab" / "grupo.py")}))
    return {"grupos": grupos, "medidas": medidas}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="bancada da V2: bracos P0-P3 sobre o mesmo aprendiz (docs/TAREFA_V2_BANCADA.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True, help="pasta de saida (vidas/, medidas.json, tabelas.json, meta.json)")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if cfg.get("tipo") == "grupo":                # dois pets (TAREFA_V2_DOIS_PETS, etapa 5)
        r = rodar_grupo(cfg, Path(a.saida))
        print(f"{len(r['grupos'])} grupos rejogados do disco bit a bit; medidas em {a.saida}")
        return 0
    r = rodar(cfg, Path(a.saida))
    print(f"{len(r['vidas'])} vidas rejogadas do disco bit a bit; medidas e tabelas em {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
