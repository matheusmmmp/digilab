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
import time
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
                            ConfigInformacao, ConfigJulgamentoFruta, ConfigLobos, ConfigMundo, ConfigPedido, LIMITE_TETO_PESOS_PLANO)
from digilab.config import ConfigCorpo  # noqa: E402
from digilab.config import CONFIG_TROCA_DIGESTAO, ConfigTrocaDigestao  # noqa: E402
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
from digilab.metrics import REGRAS_TEMPO_LIVRE, efeitos_do_tapa, metabolismo_da_vida, tempo_comer_brincar, vez_no_grupo  # noqa: E402
from digilab.mundo import DonoCarinhoBanheiro  # noqa: E402
from digilab.mundo import alvo_padrao_de  # noqa: E402
from digilab.events import ACOES_MAO, ACOES_TROCA_ARVORES, dar_fruta, fruta_dada, trocar_arvores  # noqa: E402
from digilab.config import CONFIG_PQP_MUNDO_LIGADA, CONFIG_MODELO_MUNDO_LIGADA, ConfigModeloMundo  # noqa: E402
from digilab.modelo_mundo import TIPOS as MODELO_TIPOS, PoliticaComModelo  # noqa: E402
from digilab.metrics import busca_transicao, exposto_transicao, mudanca_de_escolha, oportunidade_revalorizacao  # noqa: E402
from digilab.mundo import (ESTILOS_LUGAR, CanalMundo, DeixarBola, DeixarComida, DonoComLugar, MotorMundo,  # noqa: E402
                           _PoliticaComMundo, centro_da_celula, reproduzir_mundo)
from digilab.obediencia import MotorPersonalidade, _PoliticaObservada  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import desarranjo_n6 as desarranjo_dos_lobos  # noqa: E402
from digilab.policies.lobos import sinal_homeostatico  # noqa: E402
from digilab.policies.lobos import (DRIVES_NOVOS_SINAL, RECEPTOR_DO_INDICE, RECEPTORES_NOVOS, contribuicoes_corpo,  # noqa: E402
                                    sinal_corpo, sinal_corpo_canais)
from digilab.policies.lobos import CANAL_DO_DRIVE, INDICE_HUMOR, arred, sinal_por_canal  # noqa: E402
from digilab.policies.lobos import LOBO_PLANEJAMENTO  # noqa: E402
from digilab.config import CONFIG_REDE_DE_SI_LIGADA, ConfigRedeDeSi  # noqa: E402
from digilab.rede_de_si import ACOES as ACOES_REDE, CONTEXTO as CONTEXTO_REDE, PoliticaComRede, RedeDeSi  # noqa: E402
from digilab.rede_de_si import div_arred  # noqa: E402
from digilab.corpo import todos_receptores_orgaos  # noqa: E402
from digilab.policies.lobos import REGRAS_PEDIDO, sortear  # noqa: E402
from digilab.metrics import (brier_skill, brier_skill_multiclasse, mae_previsao, media_historica,  # noqa: E402
                             previsao_persistencia)
from digilab.motivo import Motivo, fator_do_plano, nome_base  # noqa: E402
from digilab.expressao import expressar  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.temperamento import sortear as sortear_temperamento  # noqa: E402
from digilab.treino import (CanalDeInteracao, MotorComFeedback, OrcamentoExcedido, OrcamentoNaoConsumido,  # noqa: E402
                            reproduzir_com_feedback, simular_vida)

# A bancada em módulos (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md): o código está no pacote experiments/bancada/, um módulo por
# assunto (a tabela em experiments/bancada/__init__.py). Este arquivo ficou como a porta de entrada: a docstring e as importações de
# antes, iguais, e todo nome de topo do pacote, posto aqui pelo `instalar_fachada`. `import bancada_v2 as bv`, `bv.X` e `bv.X = ...`
# valem como antes, e `python experiments/bancada_v2.py ...` também.
if __package__:
    from . import bancada as _pacote  # noqa: E402
else:
    import bancada as _pacote  # noqa: E402
_pacote.instalar_fachada(sys.modules[__name__])


if __name__ == "__main__":
    raise SystemExit(main())
