"""Politica com lobos nomeados (V2: L0 docs/TAREFA_V2_L0_LOBOS.md; L1 docs/TAREFA_V2_L1_DECISAO.md, 2026-10-01).

O aprendiz da V2. Quatro lobos, que sao ESTAGIOS internos com nome, nao interfaces plugaveis
(docs/digibrain 07, secao 2):

  PERCEPCAO        Observacao -> entradas x = (1, Estado.vetor, min(1, ticks sem cuidado / escala)).
                   Os mesmos floats que o instinto e o bandit leem hoje.
  MEMORIA/EMOCAO   presente como lobo nomeado: conta o que o dono fez (elogios, broncas, cuidados) e
                   as decisoes. Contribuicao zero em toda decisao (L0 e L1). L2 enche.
  IMPULSOS         as regras do PoliticaInstinto (policy.py), executadas pelo PROPRIO codigo do
                   instinto com uma rng-sonda (nao consome a rng do motor): devolvem a regra que
                   disparou e os CANDIDATOS, na ordem do instinto (uma acao nas regras deterministas;
                   comer/chamar na fome moderada; ocioso/explorar/brincar/chamar no tempo livre).
  DECISAO          pesos INTEIROS w[regra][acao][entrada], em ponto fixo com escala S = 2**bits,
                   iniciados no prior do instinto (os coeficientes das regras, vezes S). Peso efetivo
                   de cada candidato = ativacao linear sum_j (w_j / S) * x_j, somada da esquerda para a
                   direita. A acao sai por sorteio proporcional com UMA chamada de rng.random(),
                   exatamente a conta de random.choices(k=1) que o instinto faz. Unico lobo que
                   aprende (L1).

L0 (aprendizado desligado): os pesos nunca mudam e a vida sai byte a byte igual a do instinto
(restricao de desenho da tarefa L0, secao 3):
  - regra determinista = um candidato so: nenhuma chamada de rng, como no instinto;
  - S e potencia de dois, entao w_j / S e exato e devolve os MESMOS floats que o instinto escreve
    (3.0; 2.0 + 2.0 * energia; 1.0 + 3.0 * humor; 1.0), somados na mesma ordem e sem somatorio
    compensado (laco explicito, nao sum());
  - o sorteio replica random.choices: cumulativa por itertools.accumulate, total = ultima + 0.0,
    bisect_right(cumulativa, random() * total, 0, n - 1). Na fome moderada os pesos [1.0, 1.0] dao
    "comer se 2 * u < 1.0", que e "comer se u < 0.5", a conta literal do instinto.

L1 (aprendizado ligado, docs/PLANO_ANALISE_V2_L1.md, secao 2): o feedback do dono como VANTAGEM, nao
recompensa fixa (MacGlashan et al., COACH, arXiv:1701.06049). A cada sinal f creditado a uma decisao
(regra r, entradas X, probabilidades P da politica NO MOMENTO da decisao, acao escolhida a*):

    dw[r][a][j] = arred( f_S * passo * X_j * (S*1[a = a*] - P_a) / (S * S * W_a) )

tudo inteiro (f_S = f*S; X_j = arred(x_j*S); P_a = arred(p(a)*S); W_a = max(1, arred(w_eff(a)*S));
arred = inteiro mais proximo, meio longe do zero). Em unidades de 1.0: dw ~ f * passo * x_j *
(1[a = a*] - p(a)) / w_eff(a), a direcao do gradiente de log p(a*) da politica proporcional com o
sinal do dono no lugar da vantagem. A dependencia da politica atual esta em (1 - p(a*)): elogio a
acao ja provavel mexe pouco. Um sinal escalar; janela de credito igual a da v1 (elogio/bronca
creditam a ultima decisao; cada chamar_atencao fica pendente e o primeiro cuidado dentro da janela
paga 1 - L/janela; pendente expirado paga recompensa_pedido_ignorado). Teto |w - w0| <= teto por
peso; piso no peso efetivo dos candidatos (so com o aprendizado ligado). Regras com um candidato nao
tem o que aprender (1[a = a*] - p(a) = 0).

A regra de atualizacao e o credito moram na base `Aprendiz`, compartilhada com o controle de
capacidade equivalente sem lobos (policies/camada_unica.py, D2 de docs/DEFINICOES_V2.md): a mesma
funcao `atualizar_pesos`, o mesmo piso, teto e janela.

Motivo (base do gate G4 da fase 1): a cada decisao, a contribuicao de cada lobo por candidato. Peso
efetivo = impulsos (prior) + decisao (pesos menos prior) + memoria e emocao (zero) + piso (zero fora
do L1). O sorteio e feito SOBRE essa soma, entao a soma fecha com a decisao por construcao;
`estado_interno()["motivos"]` guarda todas (a sonda de divergencia tambem chama agir e acrescenta
motivos: gravar o estado interno antes de sondar).

LOBOS-MUNDO (docs/TAREFA_V2_LOBOS_MUNDO.md, 2026-10-04): com `cfg_bola` e/ou `cfg_frutas` LIGADAS os lobos veem o mundo.
  - percepcao: mais duas entradas no fim, `bola` e `fruta` (o que o MotorAmbiente/MotorFrutas injetam na Observacao);
  - impulsos: o codigo do PoliticaInstintoFrutas (que e o da bola com as frutas) roda na sonda, entao `bola_no_cenario` e
    `fruta_no_cenario` viram regras dos lobos; o prior delas e o do tempo livre mais w_bola na entrada `bola` de brincar e,
    em `fruta_no_cenario`, comer com w_fruta na entrada `fruta` (candidato no fim, como no instinto);
  - decisao: um peso inteiro por fruta para a SUB-DECISAO (qual fruta comer), prior S: peso da fruta = (w/S) x incentivo, e o
    sorteio replica MotorFrutas._escolher com o mesmo u da rng_fruta. O motor pergunta por `escolher_fruta` (gancho em
    frutas.py); com o aprendizado desligado a escolha sai a de hoje, byte a byte (gate G2). A sub-decisao entra no registro da
    decisao de comer e aprende com o mesmo sinal, pela mesma regra (a entrada da fruta e o incentivo dela);
  - E2: na fonte "consequencia", comer com fruta no cenario adia o credito ate o motor avisar `fruta_comida`; o sinal entao e
    `sinal_homeostatico_fruta` (drives + humor, depois = logo depois de comer). As outras acoes seguem com o sinal do N3.
Sem `cfg_bola`/`cfg_frutas` ligadas (o padrao), nada disso existe: as formas, as vidas e o estado interno de antes, byte a byte.
FRUTA-NO-CENARIO, parte B (docs/TAREFA_V2_FRUTA_NO_CENARIO.md; decisao R2): na regra `fruta_no_cenario`, o peso de COMER soma
(w_f / S) x presenca_f das frutas no cenario (Observacao.frutas_cenario), um peso por fruta, prior 0 (o instinto das frutas byte a byte
com o aprendizado desligado). Esses pesos so aprendem pela consequencia (atualizar_comer_fruta, a regra da L1); o dono nao mexe neles.
A informacao do dono continua so na escolha de qual fruta.

CORPO, etapa 5 (docs/TAREFA_V2_CORPO_DRIVES.md, secoes 9 a 11): com `cfg_corpo` LIGADA o cerebro A le os receptores do corpo
(Observacao.corpo, a PercepcaoCorpo do motor, pelo nome dos campos; o cerebro nunca importa o corpo, G-RECEPTOR):
  - o sinal: `sinal_corpo`, D = soma_d w_d * falta_d**2 sobre os receptores (falta = S - leitura nos drives de hoje; a propria leitura
    nos drives novos), no lugar do `sinal_homeostatico`. Os drives: os do N3, o humor so no comer de fruta (E2) e os drives novos que o
    corpo tiver (tedio, curiosidade, solidao, estresse, dor; o susto fica fora). Com os drives de hoje e w_d = 1 o numero e o do N3;
  - o gancho: na fonte consequencia o credito espera `consequencia_corpo` (sem o mundo fisico) ou `consequencia_mundo` (com ele), uma
    chamada por decisao, com o `obs_depois` que ja tem os estimulos da acao (a Transicao do engine nao os tem). O `f_S` que chega em
    `observar_consequencia` tem de ser o do N3 da transicao (conferido) e nao e creditado;
  - as entradas novas: as leituras dos receptores novos (na escala S, divididas por S) entram so nas regras de tempo livre
    (REGRAS_ENTRADAS_CORPO), num peso por (regra, acao, receptor), prior 0: no prior a vida e a de hoje. Aprendem pela regra da L1, com o
    canal do corpo;
  - os canais novos: um por drive novo, com a mesma soma telescopica (o total e o escalar, conferido em toda decisao), todos ao corpo
    (ROTA_CANAIS_CORPO); o humor da fruta continua indo a fruta.
Sem `cfg_corpo` (ou desligada) nada disso existe, e o gancho `consequencia_corpo` nao faz nada: o cerebro vive como hoje, inclusive
num motor com o corpo.

Sem funcoes transcendentais (nada de math): paridade com a web quando o L1 for portado.
"""

from __future__ import annotations

import random
from bisect import bisect_right
from dataclasses import fields, replace
from itertools import accumulate

from ..config import (CONFIG_BOLA, CONFIG_CONSEQUENCIA, CONFIG_FRUTAS, CONFIG_LOBOS, CONFIG_MEMORIA_ESPACOS, CONFIG_PADRAO,
                      TICKS_POR_DIA, Config, ConfigBanheiro, ConfigBola, ConfigConsequencia, ConfigCorpo, ConfigFrutas, ConfigLobos,
                      ConfigMundo)
from ..events import ACOES_PET_HOJE, FRUTAS, AcaoPet, AcaoUsuario
from ..policy import Observacao, PoliticaInstinto, Transicao

ACOES = ACOES_PET_HOJE                   # as sete de sempre; o ALIVIAR (banheiro) so nas tabelas do cerebro com a chave
LOBOS = ("percepcao", "memoria_emocao", "impulsos", "decisao")
# as regras do instinto, na ordem em que ele as testa (policy.py: ultima_regra)
REGRAS = ("sono_exaustao", "sono_continuar", "sono_noite", "pedido_necessidade", "abandono",
          "fome_moderada", "tempo_livre")
# entradas da percepcao: vies + Estado.vetor (ordem congelada em state.py) + tempo sem cuidado
ENTRADAS = ("vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora",
            "ticks_sem_cuidado")
N_ENTRADAS = len(ENTRADAS)
# LOBOS-MUNDO: as regras do instinto do mundo (ambiente.REGRA_BOLA, frutas.REGRA_FRUTA) e as entradas que o motor injeta
REGRAS_MUNDO = ("bola_no_cenario", "fruta_no_cenario")
ENTRADAS_MUNDO = ("bola", "fruta")
# MUNDO-CEREBROS (docs/TAREFA_V2_MUNDO_FISICO.md, secao 9): as acoes com alvo do MotorMundo (mundo.ACOES_COM_ALVO, conferido por teste);
# no mundo fisico a consequencia delas chega pelo gancho `consequencia_mundo`
ACOES_COM_ALVO_MUNDO = (AcaoPet.EXPLORAR, AcaoPet.COMER, AcaoPet.BRINCAR)
INDICE_HUMOR = 3                  # humor em Estado.vetor (ordem congelada em state.py); E2

# Status de cada parametro da ConfigLobos (config.py). Todos PROPOSTOS, sem fonte, nenhum referendado.
PARAMETROS_LOBOS_L0: dict[str, tuple[str, str]] = {
    "aprendizado_ligado": ("PROPOSTO", "L0 desligado (TAREFA_V2_L0_LOBOS, secao 3); o L1 liga"),
    "bits_ponto_fixo": ("PROPOSTO", "sem fonte; potencia de dois para a divisao exata (secao 3, restricao de desenho)"),
    "escala_ticks_desde_cuidado": ("PROPOSTO", "mesmo valor de ConfigBandit.escala_ticks_desde_cuidado"),
    "maximo_pesos": ("PROPOSTO", "PLANO_V2_PESQUISA, fase 1b: abaixo de mil pesos, para o replay"),
}
PARAMETROS_LOBOS_L1: dict[str, tuple[str, str]] = {
    "passo": ("PROPOSTO", "sem fonte; calibrado nas sementes 3101...3505 (PLANO_ANALISE_V2_L1, secao 5)"),
    "teto": ("PROPOSTO", "sem fonte; calibrado nas sementes 3101...3505 (PLANO_ANALISE_V2_L1, secao 5)"),
    "piso_peso": ("PROPOSTO", "sem fonte; S/16, da ordem do piso_prior do bandit (0,05)"),
    "janela_latencia_ticks": ("PROPOSTO", "= ConfigBandit.janela_latencia_ticks (janela de credito da v1)"),
    "recompensa_pedido_ignorado": ("PROPOSTO", "= ConfigBandit.recompensa_pedido_ignorado"),
    "recompensa_elogio": ("PROPOSTO", "= ConfigBandit.recompensa_elogio"),
    "recompensa_repreensao": ("PROPOSTO", "= ConfigBandit.recompensa_repreensao"),
}
PARAMETROS_LOBOS_N5: dict[str, tuple[str, str]] = {
    "w0_info": ("PROPOSTO", "N5-1 (PLANO_ANALISE_V2_N5, secao 3): 0 desliga; grade {S/4, S/2, 3S/4} calibrada no N5"),
}
PARAMETROS_LOBOS_REVISAO: dict[str, tuple[str, str]] = {
    "traco_decisoes": ("PROPOSTO", "REVISAO-APRENDIZ: a janela de credito (0 = a de hoje); grade em PLANO_ANALISE_V2_REVISAO_APRENDIZ"),
    "traco_fator": ("PROPOSTO", "REVISAO-APRENDIZ: lambda do traco na escala S; grade em PLANO_ANALISE_V2_REVISAO_APRENDIZ"),
}
PARAMETROS_LOBOS_N6_N7: dict[str, tuple[str, str]] = {
    "memoria_ligada": ("PROPOSTO", "N6 (PLANO_ANALISE_V2_N6, secao 2): chave da memoria de episodios"),
    "memoria_ganho": ("PROPOSTO", "N6-10: grade {S/4, S/2, 3S/4} calibrada no N6; 0 = contribuicao zero (o M0)"),
    "memoria_modo": ("PROPOSTO", "N6, secao 4.1: relevante (MR), recencia (MT), embaralhada (ME)"),
    "memoria_janela_recencia_ticks": ("PROPOSTO", "N6-5: 240 min, a janela da informacao do N5"),
    "memoria_permutacao": ("PROPOSTO", "N6-6: desarranjo de FRUTAS por vida, rng propria (desarranjo_n6)"),
    "w0_pedido": ("PROPOSTO", "N7-4 (PLANO_ANALISE_V2_N7, secao 3): 0 desliga; grade {S/4, S/2, 3S/4} calibrada no N7"),
}
PARAMETROS_LOBOS_CORPO: dict[str, tuple[str, str]] = {
    "recompensa_tapa": ("PROPOSTO", "CD-10 (TAREFA_V2_CORPO_DRIVES, secao 16): o valor da recompensa_repreensao, em toda fonte que "
                                    "aprende"),
}
PARAMETROS_LOBOS_DOIS_PETS: dict[str, tuple[str, str]] = {
    "alvo_aprendido": ("PROPOSTO", "TAREFA_V2_DOIS_PETS, etapa 4 (DP-8): a chave do alvo aprendido por classe de candidato"),
    "w0_alvo": ("PROPOSTO", "dois_pets.md, secao 8: o peso pequeno das classes que o padrao nao usa (S/16), SEM FONTE"),
    "entradas_sociais": ("PROPOSTO", "TAREFA_V2_DOIS_PETS, etapa 4 (DP-8): a chave das entradas sociais nas regras de tempo livre"),
    "modelo_outros": ("PROPOSTO", "dois_pets.md, secao 8: o modelo dos outros, so registrado ate o degrau 3"),
    "janela_social_ticks": ("PROPOSTO", "o 'recente' do viu comer e do toque: 240, a janela da informacao do N5, SEM FONTE propria"),
    "fator_familiaridade": ("PROPOSTO", "dois_pets.md, secao 8: a familiaridade com decaimento, S/64 por decisao, SEM FONTE"),
}
PARAMETROS_LOBOS = {**PARAMETROS_LOBOS_L0, **PARAMETROS_LOBOS_L1, **PARAMETROS_LOBOS_N5, **PARAMETROS_LOBOS_REVISAO,
                    **PARAMETROS_LOBOS_N6_N7, **PARAMETROS_LOBOS_CORPO, **PARAMETROS_LOBOS_DOIS_PETS}
MODOS_MEMORIA = ("relevante", "recencia", "embaralhada")
REGRAS_PEDIDO = ("fome_moderada", "fruta_no_cenario")   # N7-2 e N7-3: so onde comer e candidato e a necessidade nao e urgente
# V2, N3: o sinal da consequencia (ConfigConsequencia, config.py). Todos PROPOSTOS, nenhum referendado.
PARAMETROS_CONSEQUENCIA_N3: dict[str, tuple[str, str]] = {
    "drives": ("PROPOSTO", "fome, higiene e energia (PLANO_ANALISE_V2_N3, secao 3); humor fora pela F6"),
    "ganho": ("PROPOSTO", "sem fonte; calibrado nas sementes 8101...8505 (PLANO_ANALISE_V2_N3, secao 6)"),
    "humor_na_fruta": ("DECIDIDO", "E2, Matheus, 2026-10-04 (PLANO_ANALISE_V2_EXPERIMENTO_MAIOR, secao 3.1)"),
    "canais_ligados": ("PROPOSTO", "CANAIS-REFORCO (H-R2; K-6 de PLANO_CALIBRACAO_CONJUNTA_V2): o mesmo total de sinal, por canal"),
    "pesos_janela": ("PROPOSTO", "PLANO_ANALISE_V2_CORPO_DRIVES, adendo 2, A2.4 (o braco P1-cw; PCD-8): o peso pela falta recente"),
    "janela_pesos": ("PROPOSTO", "A2.4: J = 32 decisoes (8 h), sem fonte"),
    "pesos_drives_corpo": ("PROPOSTO", "TAREFA_V2_CORPO_DRIVES, secao 9: w_d inteiros, todos 1, sem fonte; o plano do corpo calibra"),
}
# CANAIS-REFORCO (H-R2): o nome de cada canal pelo indice do drive em Estado.vetor, e o grupo de pesos que cada canal credita.
#   corpo: a tabela do lobo de decisao (a regra; as entradas sao o estado do corpo)
#   fruta: os pesos que leem a identidade da fruta (a escolha da fruta, a informacao do N5, o pedido do N7, a presenca da FRUTA-NO-
#          CENARIO). A nutricao e igual em todas as frutas (F6), entao o que distingue uma fruta da outra chega pelo humor.
# Uma rota so por canal: nenhum canal e creditado duas vezes, e o total creditado na decisao e o escalar (contrato K-6). Trocar a
# rota e desenho novo (adendo 2 do plano da calibracao), nao parametro.
CANAL_DO_DRIVE = {0: "fome", 1: "higiene", 2: "energia", INDICE_HUMOR: "humor"}
ROTA_CANAIS = {"fome": "corpo", "higiene": "corpo", "energia": "corpo", "humor": "fruta"}
ALVOS_CANAIS = ("corpo", "fruta")
# CORPO, etapa 5: os receptores pelo nome dos campos da PercepcaoCorpo (motor_corpo.py; o cerebro nao importa o motor nem o corpo).
RECEPTORES_HOJE = ("fome", "higiene", "energia", "humor", "saude")          # leitura = S - falta, na ordem de Estado.vetor
RECEPTOR_DO_INDICE = dict(enumerate(RECEPTORES_HOJE))
RECEPTORES_NOVOS = ("tedio", "curiosidade", "solidao", "estresse", "dor", "susto",   # leitura = a falta (dor e susto: a concentracao)
                    "vontade", "conforto")                                         # banheiro: a concentracao (a vontade, o conforto)
DRIVES_NOVOS_SINAL = ("tedio", "curiosidade", "solidao", "estresse", "dor",         # secao 9: o susto fica fora do sinal
                      "vontade", "conforto")                                       # banheiro (secao 3 e BN-6)
# BN-6: o receptor do conforto le a concentracao; a falta do drive e a falta de conforto, S - leitura (o carinho a reduz)
RECEPTORES_FALTA_INVERTIDA = ("conforto",)
REGRAS_ENTRADAS_CORPO = ("tempo_livre", "bola_no_cenario", "fruta_no_cenario")     # secao 11: so nas regras de tempo livre
# os canais novos (secao 9): um por drive novo, todos ao corpo (a tabela do lobo de decisao); o humor da fruta continua na fruta
ROTA_CANAIS_CORPO = {d: "corpo" for d in DRIVES_NOVOS_SINAL}
VALOR_TAPA = "tapa"                 # AcaoUsuario.TAPA (o enum e do A, etapa 6): o cerebro o le pelo valor
# o banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 4): a regra urgente do instinto do alivio (instinto_banheiro.REGRA_ALIVIO_URGENTE,
# conferido na carga) e os alvos do `aliviar`. O ALIVIAR so entra nas tabelas das regras em que ele e candidato: as de tempo livre e a
# urgente (so ele); nas outras regras, as sete acoes de sempre
REGRA_ALIVIO_URGENTE = "alivio_urgente"
ALVOS_ALIVIO = ("banheiro", "aqui")
# dois pets, etapa 4 (docs/TAREFA_V2_DOIS_PETS.md; docs/futuro/dois_pets.md, secao 8, DP-8): o alvo aprendido no mundo fisico, por
# CLASSE de candidato. As classes de cada acao com alvo, na ordem da tabela de pesos: as do MotorMundo de hoje (a comida separada em
# boa e podre pela percepcao) e o lugar de `seguir` e `onde_comeu`, que o motor oferece no explorar a partir da etapa 3 do A
CLASSES_ALVO = {AcaoPet.COMER: ("comida", "comida_podre", "cheiro", "continuar"),
                AcaoPet.EXPLORAR: ("cheiro", "vagar", "casa", "continuar", "seguir", "onde_comeu"),
                AcaoPet.BRINCAR: ("bola", "continuar")}
# as regras em que cada acao com alvo e candidata no cerebro do mundo fisico (o prior do instinto do mundo): um peso por (regra, acao,
# classe)
REGRAS_ALVO = {"pedido_necessidade": (AcaoPet.COMER,), "fome_moderada": (AcaoPet.COMER,),
               "tempo_livre": (AcaoPet.EXPLORAR, AcaoPet.BRINCAR), "bola_no_cenario": (AcaoPet.EXPLORAR, AcaoPet.BRINCAR),
               "fruta_no_cenario": (AcaoPet.EXPLORAR, AcaoPet.BRINCAR, AcaoPet.COMER)}
ESCALA_U_ALVO = 1 << 16                # o u do alvo do MotorMundo: inteiro em [0, 2^16)
# dois pets, etapa 4, segunda metade (DP-8): as entradas sociais, lidas de Observacao.social (mundo.PercepcaoSocial; o cerebro nao importa
# o mundo: os tipos do toque sao conferidos contra mundo.TIPOS_TOQUE na carga). Todas 0 ou 1:
#   outro_a_vista   algum outro no raio da visao
#   viu_comer       viu algum outro comer ha no maximo `janela_social_ticks`
#   acao_<a>        a acao visivel do outro mais perto (uma por acao do AcaoPet; com um outro a vista, exatamente uma vale 1)
#   toque_<tipo>    o tipo do ultimo contato, se ha no maximo `janela_social_ticks` (o mais recente; empate pelo id)
TIPOS_TOQUE_SOCIAL = ("disputa_ganhou", "disputa_perdeu", "encostou", "encostaram", "esbarrou")
ACOES_VISIVEIS = tuple(a.value for a in AcaoPet)
ENTRADAS_SOCIAIS = (("outro_a_vista", "viu_comer") + tuple(f"acao_{a}" for a in ACOES_VISIVEIS)
                    + tuple(f"toque_{t}" for t in TIPOS_TOQUE_SOCIAL))
TIPOS_COMIDA_BOA = ("racao",) + FRUTAS   # os tipos da percepcao do mundo que sao comida boa (sem `_podre`, sem a bola)

# Prior do instinto em unidades de 1.0 (vira inteiro vezes S): regra -> acao -> entrada -> coeficiente.
# So os candidatos de cada regra tem coeficiente; o resto da tabela e zero. Os numeros sao os literais de
# PoliticaInstinto.agir: pesos do tempo livre {ocioso 3, explorar 2 + 2 energia, brincar 1 + 3 humor,
# chamar 1}; na fome moderada "comer se u < 0.5" = pesos iguais; nas deterministas o unico candidato.
# A igualdade com o codigo do instinto e conferida por teste (tests/test_lobos.py) e pelo gate G2.
PRIOR_INSTINTO: dict[str, dict[AcaoPet, dict[str, int]]] = {
    "sono_exaustao": {AcaoPet.DORMIR: {"vies": 1}},
    "sono_continuar": {AcaoPet.DORMIR: {"vies": 1}},
    "sono_noite": {AcaoPet.DORMIR: {"vies": 1}},
    "pedido_necessidade": {AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
    "abandono": {AcaoPet.EMBURRAR: {"vies": 1}, AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
    "fome_moderada": {AcaoPet.COMER: {"vies": 1}, AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
    "tempo_livre": {AcaoPet.OCIOSO: {"vies": 3}, AcaoPet.EXPLORAR: {"vies": 2, "energia": 2},
                    AcaoPet.BRINCAR: {"vies": 1, "humor": 3}, AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
}

CUIDADOS = frozenset({AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR,
                      AcaoUsuario.PETISCO, AcaoUsuario.LEVAR_AO_BANHEIRO, AcaoUsuario.TRATAR_LESAO})
FEEDBACK = frozenset({AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER})


# ------------------------------------------------------------------ impulsos: sonda do instinto


class _RngSonda:
    """Substituto de random.Random que registra como o instinto usa a rng, sem consumir a rng do motor.

    Devolve sempre o mesmo u em random(); em choices() guarda populacao e pesos e devolve o primeiro.
    Qualquer outro uso levanta erro (falhar alto)."""

    def __init__(self, u: float) -> None:
        self.u = u
        self.chamadas_random = 0
        self.escolha: tuple[list, list] | None = None

    def random(self) -> float:
        self.chamadas_random += 1
        return self.u

    def choices(self, populacao, weights=None, k=1):
        if self.escolha is not None or k != 1 or weights is None:
            raise NotImplementedError("sonda so suporta um unico choices(k=1) ponderado")
        self.escolha = (list(populacao), list(weights))
        return [populacao[0]]

    def __getattr__(self, nome):
        raise NotImplementedError(f"sonda nao suporta rng.{nome}")


def impulsos(instinto: PoliticaInstinto, obs: Observacao) -> tuple[str, tuple[AcaoPet, ...]]:
    """Lobo de impulsos: a regra do instinto que dispara nesta observacao e os candidatos, na ordem dele.

    Executa o codigo do proprio PoliticaInstinto com uma rng-sonda. Regra determinista: um candidato.
    Um `random() < t` (fome moderada): os dois lados, com u = 0 e u -> 1. Um choices(): a populacao."""
    sonda = _RngSonda(0.0)
    a0 = instinto.agir(obs, sonda)
    regra = instinto.ultima_regra
    if regra is None:
        raise RuntimeError("instinto nao registrou a regra")
    if sonda.escolha is not None:
        if sonda.chamadas_random:
            raise NotImplementedError("instinto usou random() e choices() na mesma decisao")
        return regra, tuple(sonda.escolha[0])
    if sonda.chamadas_random == 0:
        return regra, (a0,)
    if sonda.chamadas_random > 1:
        raise NotImplementedError("instinto chamou random() mais de uma vez")
    a1 = instinto.agir(obs, _RngSonda(1.0 - 1e-15))
    if a1 is a0:
        raise NotImplementedError("instinto chamou random() sem que o resultado dependesse dele")
    return regra, (a0, a1)


# ------------------------------------------------------------------ percepcao, ativacao, sorteio, inteiros


def percepcao(obs: Observacao, escala_ticks_desde_cuidado: float) -> list[float]:
    """Lobo de percepcao: (1, Estado.vetor, min(1, ticks sem cuidado / escala)), N_ENTRADAS floats."""
    x = [1.0, *obs.vetor_estado, min(1.0, obs.ticks_desde_cuidado / escala_ticks_desde_cuidado)]
    if len(x) != N_ENTRADAS:
        raise ValueError(f"percepcao com {len(x)} entradas, esperadas {N_ENTRADAS}")
    return x


def ativacao(pesos: list[int], x: list[float], escala: int) -> float:
    """sum_j (w_j / S) * x_j, da esquerda para a direita, sem somatorio compensado (laco, nao sum()).

    w_j / S e exato porque S e potencia de dois; com os pesos no prior, cada termo e o mesmo float que o
    instinto escreve e a soma segue a mesma ordem."""
    if len(pesos) != len(x):
        raise ValueError(f"{len(pesos)} pesos para {len(x)} entradas")
    acumulado = 0.0
    for w, xj in zip(pesos, x):
        acumulado = acumulado + (w / escala) * xj
    return acumulado


def termos(pesos: list[int], x: list[float], escala: int) -> list[float]:
    """Os termos (w_j / S) * x_j da ativacao, um por entrada (a contribuicao de cada entrada)."""
    if len(pesos) != len(x):
        raise ValueError(f"{len(pesos)} pesos para {len(x)} entradas")
    return [(w / escala) * xj for w, xj in zip(pesos, x)]


def sortear(pesos: list[float], u: float) -> int:
    """Indice sorteado com os pesos, dado u = rng.random(): a conta de random.choices(k=1), passo a passo."""
    cumulativa = list(accumulate(pesos))
    total = cumulativa[-1] + 0.0
    if total <= 0.0:
        raise ValueError(f"soma dos pesos nao positiva: {pesos}")
    return bisect_right(cumulativa, u * total, 0, len(cumulativa) - 1)


def arred(x: float) -> int:
    """Inteiro mais proximo, meio longe do zero (simetrico; round() do Python e meio-para-par)."""
    if x >= 0.0:
        return int(x + 0.5)
    return -int(-x + 0.5)


def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def atualizar_pesos(pesos: dict, prior: dict, registro: dict, f_S: int, passo: int, teto: int, S: int) -> int:
    """A regra de atualizacao do L1, em inteiros, aplicada a tabela `pesos[acao] -> list[int]` de uma regra
    (ou contexto): dw[a][j] = arred(f_S * passo * X_j * (S*1[a=a*] - P_a) / (S*S*W_a)), cortado em prior +- teto.
    `registro` = {"candidatos", "acao", "X", "P", "W"} da decisao creditada. Devolve quantos cortes no teto."""
    cortes = 0
    escolhida = registro["acao"]
    for a in registro["candidatos"]:
        fator = (S if a is escolhida else 0) - registro["P"][a]
        if fator == 0:
            continue
        w, w0 = pesos[a], prior[a]
        denominador = S * S * registro["W"][a]
        for j, X in enumerate(registro["X"]):
            if X == 0:
                continue
            delta = div_arred(f_S * passo * X * fator, denominador)
            if delta == 0:
                continue
            novo = w[j] + delta
            if novo > w0[j] + teto:
                novo = w0[j] + teto
                cortes += 1
            elif novo < w0[j] - teto:
                novo = w0[j] - teto
                cortes += 1
            w[j] = novo
    return cortes


def atualizar_fruta(pesos: dict, prior: dict, sub: dict, f_S: int, passo: int, teto: int, S: int) -> int:
    """A mesma regra do L1 na sub-decisao da fruta (LOBOS-MUNDO): cada fruta tem UM peso w_f e a sua propria entrada, o incentivo
    (X_f = arred(incentivo_f * S)); peso efetivo (w_f / S) * incentivo_f. dw_f = arred(f_S * passo * X_f * (S*1[f=f*] - P_f) /
    (S*S*W_f)), cortado em prior +- teto: e o gradiente de log p(f*) da escolha proporcional, como no lobo de decisao.
    `sub` = {"candidatos", "acao", "X", "P", "W"} por fruta. Devolve quantos cortes no teto."""
    cortes = 0
    for f in sub["candidatos"]:
        fator = (S if f == sub["acao"] else 0) - sub["P"][f]
        X = sub["X"][f]
        if fator == 0 or X == 0:
            continue
        delta = div_arred(f_S * passo * X * fator, S * S * sub["W"][f])
        if delta == 0:
            continue
        novo = pesos[f] + delta
        if novo > prior[f] + teto:
            novo = prior[f] + teto
            cortes += 1
        elif novo < prior[f] - teto:
            novo = prior[f] - teto
            cortes += 1
        pesos[f] = novo
    return cortes


# ------------------------------------------------------------------ memoria e emocao (L0: so contadores)


class MemoriaEmocao:
    """Lobo nomeado, sem efeito na decisao no L0 e no L1. So registra o que passou por ele."""

    def __init__(self) -> None:
        self.elogios = 0
        self.broncas = 0
        self.cuidados = 0
        self.outras_acoes_dono = 0
        self.decisoes = 0
        self.tick_ultima_acao_dono: int | None = None

    def acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        if acao is AcaoUsuario.ELOGIAR:
            self.elogios += 1
        elif acao is AcaoUsuario.REPREENDER:
            self.broncas += 1
        elif acao in CUIDADOS:
            self.cuidados += 1
        else:
            self.outras_acoes_dono += 1
        self.tick_ultima_acao_dono = tick

    def decisao(self) -> None:
        self.decisoes += 1

    def contribuicao(self, candidatos: tuple[AcaoPet, ...]) -> dict[AcaoPet, float]:
        return {a: 0.0 for a in candidatos}

    def para_dict(self) -> dict:
        return {"elogios": self.elogios, "broncas": self.broncas, "cuidados": self.cuidados,
                "outras_acoes_dono": self.outras_acoes_dono, "decisoes": self.decisoes,
                "tick_ultima_acao_dono": self.tick_ultima_acao_dono}


# ------------------------------------------------------------------ N6: memoria de episodios das frutas


def desarranjo_n6(semente: int) -> tuple:
    """N6-6: o desarranjo pi de FRUTAS (nenhuma fruta em si mesma) do braco embaralhado, sorteado uma vez por vida pela rng propria
    derivar_semente("n6-embaralha", semente). Com tres frutas ha dois, um por sentido do ciclo. Devolve pi na ordem de FRUTAS."""
    from ..protocol import derivar_semente          # importacao tardia, como as do mundo
    if len(FRUTAS) != 3:
        raise ValueError("o desarranjo do N6 supoe tres frutas")
    rng = random.Random(derivar_semente("n6-embaralha", semente))
    a, b, c = FRUTAS
    return ((b, c, a), (c, a, b))[rng.randrange(2)]


def _inserir_episodio(espacos: list[dict], novo: dict, n: int) -> tuple[list[dict], str]:
    """A regra dos espacos da v1 (memoria_espacos.inserir), com a categoria = a fruta e a intensidade = |valencia| (inteiros): a mesma
    fruta e substituida pela nova se ela for mais forte ou igual; fruta ausente com espacos cheios substitui a mais fraca (em empate, a
    mais antiga) se for mais forte ou igual; senao a nova e descartada."""
    mesma = [e for e in espacos if e["fruta"] == novo["fruta"]]
    if mesma:
        velha = mesma[0]
        if novo["intensidade"] >= velha["intensidade"]:
            return [novo if e is velha else e for e in espacos], "substituiu"
        return list(espacos), "descartada"
    if len(espacos) < n:
        return list(espacos) + [novo], "entrou"
    fraca = min(espacos, key=lambda e: (e["intensidade"], e["tick"]))
    if novo["intensidade"] >= fraca["intensidade"]:
        return [novo if e is fraca else e for e in espacos], "substituiu"
    return list(espacos), "descartada"


class MemoriaEpisodios:
    """N6 (docs/PLANO_ANALISE_V2_N6.md, secoes 2.1 e 2.2): os episodios de consumo de fruta no lobo `memoria_emocao`. Um episodio =
    {tick, fruta, valencia, intensidade}; curto prazo (n_curto espacos, por d_curto ticks) e longo prazo (n_longo, permanente ate ser
    substituido), com a regra de desempate da v1. Sem decaimento continuo e sem relembrar (N6-4): o esquecimento vem so dos espacos.
    `episodios` guarda todos os codificados (o marco 2), na ordem."""

    def __init__(self, n_curto: int, n_longo: int, d_curto_ticks: int) -> None:
        if n_curto < 1 or n_longo < 1 or d_curto_ticks < 1:
            raise ValueError("espacos e prazo do curto precisam ser positivos")
        self.n_curto, self.n_longo, self.d_curto = n_curto, n_longo, d_curto_ticks
        self.curto: list[dict] = []
        self.longo: list[dict] = []
        self.episodios: list[dict] = []
        self.contagem = {"entrou": 0, "substituiu": 0, "descartada": 0, "promovida": 0, "esquecida": 0}
        self.sondas = {"subdecisoes_2mais": 0, "com_recuperacao": 0, "mudou": 0}

    def promover(self, tick: int) -> None:
        """O que passou do prazo do curto tenta o longo (pela regra dos espacos), na ordem de criacao, como a v1."""
        vencidos = sorted((e for e in self.curto if e["tick"] + self.d_curto <= tick), key=lambda e: (e["tick"], e["fruta"]))
        for e in vencidos:
            self.curto = [x for x in self.curto if x is not e]
            self.longo, r = _inserir_episodio(self.longo, e, self.n_longo)
            self.contagem["promovida" if r != "descartada" else "esquecida"] += 1

    def codificar(self, tick: int, fruta: str, valencia: int) -> dict:
        self.promover(tick)
        ep = {"tick": tick, "fruta": fruta, "valencia": valencia, "intensidade": abs(valencia)}
        self.episodios.append(ep)
        self.curto, r = _inserir_episodio(self.curto, ep, self.n_curto)
        self.contagem[r] += 1
        return ep

    def recuperar(self, pista: str, tick: int, modo: str, janela: int, permutacao: dict) -> dict | None:
        """O episodio da fruta da pista (no embaralhado, de pi(pista)) mais forte entre os dois prazos (empate: o mais recente); no braco
        de recencia, so os de idade <= janela. Nada: None."""
        alvo = permutacao[pista] if modo == "embaralhada" else pista
        cands = [e for e in self.curto + self.longo if e["fruta"] == alvo]
        if modo == "recencia":
            cands = [e for e in cands if tick - e["tick"] <= janela]
        return max(cands, key=lambda e: (e["intensidade"], e["tick"])) if cands else None

    def para_dict(self) -> dict:
        return {"curto": [dict(e) for e in self.curto], "longo": [dict(e) for e in self.longo],
                "episodios": [dict(e) for e in self.episodios], "contagem": dict(self.contagem), "sondas": dict(self.sondas)}


def _sortear_frutas(presentes: list[str], pesos: list[float], u: float) -> str:
    """O sorteio de MotorFrutas._escolher, passo a passo (o mesmo de sempre da sub-decisao)."""
    total = 0.0
    for p in pesos:
        total += p
    if total <= 0.0:
        return presentes[min(int(u * len(presentes)), len(presentes) - 1)]
    alvo = u * total
    acc = 0.0
    for f, p in zip(presentes, pesos):
        acc += p
        if alvo < acc:
            return f
    return presentes[-1]


# ------------------------------------------------------------------ a base: pesos inteiros + credito do L1


def entradas_sociais(social, janela: int) -> list[float]:
    """Dois pets, etapa 4 (DP-8): as entradas sociais (ENTRADAS_SOCIAIS), 0.0 ou 1.0, so do que `Observacao.social` traz (o que e fisico:
    a posicao e a acao visivel, o consumo visto, o contato). Sem o campo (sozinho ou fora do grupo), todas 0.0."""
    x = [0.0] * len(ENTRADAS_SOCIAIS)
    if social is None:
        return x
    base_acao, base_toque = 2, 2 + len(ACOES_VISIVEIS)
    if social.outros:
        x[0] = 1.0
        acao = social.outros[0][4]                     # o outro mais perto (os outros vem em ordem de d e de id)
        if acao not in ACOES_VISIVEIS:
            raise ValueError(f"acao visivel desconhecida: {acao!r}")
        x[base_acao + ACOES_VISIVEIS.index(acao)] = 1.0
    for _, _, _, idade in social.onde_comeu:
        if idade < 0:
            raise ValueError(f"consumo visto com idade negativa: {idade}")
        if idade <= janela:
            x[1] = 1.0
    recentes = []
    for ident, tipo, _, idade in social.toque:
        if idade < 0 or tipo not in TIPOS_TOQUE_SOCIAL:
            raise ValueError(f"toque invalido: {tipo!r}, idade {idade}")
        if idade <= janela:
            recentes.append((idade, ident, tipo))
    if recentes:
        x[base_toque + TIPOS_TOQUE_SOCIAL.index(min(recentes)[2])] = 1.0
    return x


class ModeloOutros:
    """Dois pets, etapa 4 (docs/futuro/dois_pets.md, secao 8; cognicao_social.md, secao 3): o modelo dos outros, SO REGISTRADO. Nada daqui
    entra na decisao (degrau 3, por adendo). Por pet conhecido, tres variaveis separadas, sem rotulo e sem soma entre elas:
    - familiaridade: a media movel do outro a vista, em inteiros na escala S, a cada decisao: f += div_arred((S [visto] - f) x fator, S);
    - confianca, por atividade (so `comida` no degrau 1): as idas a `onde_comeu` dele que chegaram (`idas`) e, delas, as que acharam
      comida boa (`acertos`: o pet comeu, ou havia comida boa a vista na chegada);
    - afinidade: `divididas` (o pet comeu e viu o outro comer no mesmo intervalo entre duas decisoes, sem disputa nele) contra `perdidas`
      (cada toque novo de `disputa_perdeu`); o saldo e divididas - perdidas.
    Os eventos (o consumo visto, o toque) sao identificados pelo tick deles no relogio do pet (a hora do dia, como o relogio do N6) menos
    a idade: o mesmo evento visto em duas decisoes conta uma vez."""

    def __init__(self, escala: int, fator: int) -> None:
        self.S, self.fator = escala, fator
        self.outros: dict[str, dict] = {}
        self._dia, self._tdd_anterior = 0, -1
        self._ultimo_comer: dict[str, tuple] = {}
        self._ultimo_toque: dict[str, tuple] = {}
        self._comeu_desde = False               # o pet comeu na consequencia da decisao anterior
        self._ida: str | None = None            # a ida a `onde_comeu` em curso (o id do outro), ate chegar ou mudar de alvo

    def _do(self, ident: str) -> dict:
        if ident not in self.outros:
            self.outros[ident] = {"familiaridade": 0, "confianca": {"comida": {"idas": 0, "acertos": 0}},
                                  "afinidade": {"divididas": 0, "perdidas": 0}}
        return self.outros[ident]

    def _relogio(self, hora: float) -> int:
        tdd = int(round(hora * TICKS_POR_DIA))
        if tdd < self._tdd_anterior:
            self._dia += 1
        self._tdd_anterior = tdd
        return self._dia * TICKS_POR_DIA + tdd

    def decisao(self, social, hora: float) -> None:
        """A cada decisao, antes de decidir (so le o `obs`): a familiaridade de todo outro conhecido e os eventos novos desde a anterior."""
        t = self._relogio(hora)
        vistos, novos_comer, novos_toque = set(), set(), {}
        if social is not None:
            vistos = {o[0] for o in social.outros}
            for ident, x, y, idade in social.onde_comeu:
                ev = (x, y, t - idade)
                if self._ultimo_comer.get(ident) != ev:
                    self._ultimo_comer[ident] = ev
                    novos_comer.add(ident)
            for ident, tipo, direcao, idade in social.toque:
                ev = (tipo, direcao, t - idade)
                if self._ultimo_toque.get(ident) != ev:
                    self._ultimo_toque[ident] = ev
                    novos_toque[ident] = tipo
        for ident in sorted(set(self.outros) | vistos | novos_comer | set(novos_toque)):
            o = self._do(ident)
            o["familiaridade"] += div_arred(((self.S if ident in vistos else 0) - o["familiaridade"]) * self.fator, self.S)
            toque = novos_toque.get(ident, "")
            if toque == "disputa_perdeu":
                o["afinidade"]["perdidas"] += 1
            if self._comeu_desde and ident in novos_comer and not toque.startswith("disputa"):
                o["afinidade"]["divididas"] += 1
        self._comeu_desde = False

    def consequencia(self, ocorrido: dict, obs_depois: Observacao, social) -> None:
        """Do `consequencia_mundo` (explorar, comer, brincar, aliviar): o que o pet comeu e as idas a `onde_comeu`. `social` e a percepcao
        social da decisao (o id do outro sai do ponto do alvo)."""
        if ocorrido["comeu"] is not None:
            self._comeu_desde = True
        alvo = ocorrido["alvo"]
        classe = None if alvo is None else (alvo["de"] if alvo["tipo"] == "continuar" else alvo["tipo"])
        if classe != "onde_comeu":
            self._ida = None
            return
        if alvo["tipo"] == "onde_comeu":
            ids = [] if social is None else [i for i, x, y, _ in social.onde_comeu if (x, y) == (alvo["x"], alvo["y"])]
            if len(ids) != 1:
                raise RuntimeError(f"ida a onde_comeu em ({alvo['x']}, {alvo['y']}) sem um outro so naquele ponto: {ids}")
            self._ida = ids[0]
        elif self._ida is None:
            raise RuntimeError("continuar de uma ida a onde_comeu sem a ida")
        if ocorrido["chegou"]:
            c = self._do(self._ida)["confianca"]["comida"]
            c["idas"] += 1
            if ocorrido["comeu"] is not None or any(tipo in TIPOS_COMIDA_BOA for _, tipo, *_ in obs_depois.mundo.vistos):
                c["acertos"] += 1
            self._ida = None

    def para_dict(self) -> dict:
        outros = {}
        for ident, o in sorted(self.outros.items()):
            c, a = o["confianca"]["comida"], o["afinidade"]
            outros[ident] = {"familiaridade": o["familiaridade"],
                             "confianca": {"comida": {**c, "fracao": div_arred(c["acertos"] * self.S, c["idas"]) if c["idas"] else None}},
                             "afinidade": {**a, "saldo": a["divididas"] - a["perdidas"]}}
        return {"outros": outros, "relogio": [self._dia, self._tdd_anterior], "ida": self._ida, "comeu_desde": self._comeu_desde,
                "ultimo_comer": {i: list(v) for i, v in sorted(self._ultimo_comer.items())},
                "ultimo_toque": {i: list(v) for i, v in sorted(self._ultimo_toque.items())}}


class Aprendiz:
    """Base dos aprendizes da V2: tabela de pesos inteiros `_pesos[grupo][acao][entrada]` iniciada no prior
    `_prior`, e o credito do feedback do L1 (janela da v1). Quem herda define `agir` (que deixa em
    `_registro_decisao` o registro da decisao: grupo, candidatos, acao, X, P, W) e `estado_interno`."""

    nome = "aprendiz"
    entradas: tuple = ENTRADAS          # nomes das entradas da percepcao (LOBOS-MUNDO: mais bola e fruta, por instancia)

    def __init__(self, cfg: Config | None, cfg_lobos: ConfigLobos | None, prior: dict,
                 prior_fruta: dict | None = None, prior_comer_fruta: dict | None = None) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cl = cfg_lobos or CONFIG_LOBOS
        if self.cl.bits_ponto_fixo < 1:
            raise ValueError("bits_ponto_fixo precisa ser >= 1")
        self._escala = self.cl.escala
        self._prior = prior
        self._pesos = {g: {a: list(v) for a, v in acoes.items()} for g, acoes in prior.items()}
        # LOBOS-MUNDO: sub-decisao da fruta, um peso por fruta (vazio fora do mundo das frutas: nada muda)
        self._prior_fruta = dict(prior_fruta or {})
        self._pesos_fruta = dict(self._prior_fruta)
        self._fruta_na_decisao = False                # a ultima decisao viu fruta no cenario (obs.fruta > 0)
        self._consequencia_pendente: tuple | None = None  # E2: (registro, transicao, cfg) do comer com fruta, ate fruta_comida
        self._ve_mundo_fisico = False                 # MUNDO-CEREBROS: so a PoliticaLobos com ConfigMundo ligada
        self._consequencia_mundo_pendente: tuple | None = None   # (registro, transicao, cfg, anteriores, f_S, pesos), ate consequencia_mundo
        self._janela_faltas: list[dict] = []          # A2.4 (pesos_janela): as faltas das ultimas J decisoes, na escala S
        self._pesos_da_e2: dict | None = None         # A2.4: os pesos da decisao com o comer de fruta pendente (E2)
        # N5: o peso compartilhado da entrada `info` na sub-decisao da fruta (None = entrada desligada: w0_info 0 ou sem frutas)
        self._prior_info: int | None = None
        self._peso_info: int | None = None
        self._info_na_decisao: tuple = ()             # Observacao.info_frutas da ultima decisao (na ordem de FRUTAS)
        # FRUTA-NO-CENARIO (parte B): um peso por fruta presente na decisao de COMER da regra fruta_no_cenario (prior 0; vazio fora
        # do mundo das frutas: nada muda)
        self._prior_comer_fruta = dict(prior_comer_fruta or {})
        self._pesos_comer_fruta = dict(self._prior_comer_fruta)
        self._presenca_na_decisao: tuple = ()         # Observacao.frutas_cenario da ultima decisao (na ordem de FRUTAS)
        # N6: a memoria de episodios (None = desligada) e o relogio dela; N7: o peso compartilhado do pedido (None = desligado)
        self._memoria: MemoriaEpisodios | None = None
        self._tick_na_decisao = 0
        self._humor_na_decisao = 0.0
        self._dia_relogio, self._tick_do_dia_anterior = 0, -1
        self._prior_pedido: int | None = None
        self._peso_pedido: int | None = None
        self._pedido_na_decisao: tuple = ()           # Observacao.pedido_frutas da ultima decisao (N7; -1 = pedido vigente)
        # CORPO (etapa 5): so a PoliticaLobos com ConfigCorpo ligada. As entradas novas sao uma tabela a parte, so nas regras de tempo
        # livre: regra -> acao -> um peso por receptor novo (prior 0; vazia sem drives novos: nada muda)
        self._corpo: ConfigCorpo | None = None
        self._receptores_novos: tuple = ()
        self._canais_novos: tuple = ()                # os drives novos do sinal que o corpo tem (canais e drives do sinal)
        self._prior_corpo: dict = {}
        self._pesos_corpo: dict = {}
        self._x_corpo: list[float] = []               # as leituras dos receptores novos na ultima decisao, divididas por S
        self._acao_sem_gancho: AcaoPet | None = None  # a decisao observada que ainda espera o gancho do corpo (uma chamada por decisao)
        self._corpo_pendente: dict | None = None      # o credito pela consequencia, ate o gancho do corpo (ou do mundo)
        self._mundo_creditou: AcaoPet | None = None   # com o mundo fisico: o consequencia_mundo ja creditou esta decisao
        self._cc_corpo: ConfigConsequencia | None = None  # a ConfigConsequencia da ultima decisao creditada pelo corpo (o ganho do carinho)
        # o banheiro (TAREFA_V2_BANHEIRO, secao 4): o prior da vontade no `aliviar` (nas entradas do corpo, termo de impulsos) e os pesos
        # do alvo do `aliviar` (um por alvo, `banheiro` e `aqui`); vazios sem a chave: nada muda
        self._banheiro: ConfigBanheiro | None = None
        # as acoes com alvo no mundo fisico, cuja consequencia chega pelo consequencia_mundo (com o banheiro, mais o aliviar)
        self._acoes_com_alvo: tuple = ACOES_COM_ALVO_MUNDO
        # dois pets, etapa 4: o alvo aprendido por classe (chave "regra:acao" -> classe -> peso); vazio sem a chave: nada muda
        self._cfg_mundo: ConfigMundo | None = None
        self._prior_alvo_mundo: dict = {}
        self._pesos_alvo_mundo: dict = {}
        self._prior_alvo: dict = {}
        self._pesos_alvo: dict = {}
        # dois pets, etapa 4, segunda metade: as entradas sociais (regra -> acao -> um peso por entrada social, prior 0; vazia sem a chave:
        # nada muda) e o modelo dos outros (None sem a chave; so registrado)
        self._prior_social: dict = {}
        self._pesos_social: dict = {}
        self._x_social: list[float] = []
        self._modelo: ModeloOutros | None = None
        self._social_na_decisao = None
        n = self.n_pesos()
        if n >= self.cl.maximo_pesos:
            raise ValueError(f"{n} pesos, teto {self.cl.maximo_pesos}")
        self.memoria = MemoriaEmocao()
        self.motivos: list[dict] = []
        self._aprende = bool(self.cl.aprendizado_ligado)
        if self._aprende:
            if self.cl.passo <= 0 or self.cl.teto <= 0 or self.cl.piso_peso <= 0 or self.cl.janela_latencia_ticks <= 0:
                raise ValueError("passo, teto, piso_peso e janela_latencia_ticks precisam ser positivos")
            for nome in ("passo", "teto", "piso_peso", "janela_latencia_ticks", "traco_decisoes", "traco_fator"):
                if type(getattr(self.cl, nome)) is not int:
                    raise TypeError(f"ConfigLobos.{nome} precisa ser inteiro")
            if self.cl.traco_decisoes < 0 or (self.cl.traco_decisoes > 0 and not 0 < self.cl.traco_fator < self._escala):
                raise ValueError("traco_decisoes >= 0 e, com traco, 0 < traco_fator < S")
        self._piso = self.cl.piso_peso / self._escala
        self._tick_ultimo_cuidado = 0
        self._tick_ultima_decisao = -1
        self._registro_decisao: dict | None = None
        self._ultima: dict | None = None              # registro da ultima decisao (para elogio/bronca)
        self._traco: list[dict] = []                  # REVISAO: as ultimas decisoes observadas (so com traco_decisoes > 0)
        self._pendentes: list[tuple[int, dict]] = []  # chamados pendentes: (tick, registro)
        self._n_recompensas = {"elogio": 0, "repreensao": 0, "latencia": 0, "ignorado": 0}
        self._n_atualizacoes = 0
        self._cortes_teto = 0
        self._canais: dict | None = None              # CANAIS-REFORCO: totais por canal e por alvo (so depois do 1o credito por canal)

    # ------------------------------------------------------------- leitura

    @property
    def ultimo_motivo(self) -> dict | None:
        return self.motivos[-1] if self.motivos else None

    @property
    def aprende(self) -> bool:
        return self._aprende

    def n_pesos(self) -> int:
        return (sum(len(v) for acoes in self._pesos.values() for v in acoes.values()) + len(self._pesos_fruta)
                + (self._peso_info is not None) + len(self._pesos_comer_fruta) + (self._peso_pedido is not None)
                + sum(len(v) for acoes in self._pesos_corpo.values() for v in acoes.values()) + len(self._pesos_alvo)
                + sum(len(t) for t in self._pesos_alvo_mundo.values())
                + sum(len(v) for acoes in self._pesos_social.values() for v in acoes.values()))

    def pesos_mudaram(self) -> bool:
        return (self._pesos != self._prior or self._pesos_fruta != self._prior_fruta or self._peso_info != self._prior_info
                or self._pesos_comer_fruta != self._prior_comer_fruta or self._peso_pedido != self._prior_pedido
                or self._pesos_corpo != self._prior_corpo or self._pesos_alvo != self._prior_alvo
                or self._pesos_alvo_mundo != self._prior_alvo_mundo or self._pesos_social != self._prior_social)

    def _desvios(self):
        """|w - w0| de cada peso: a tabela da decisao e, no mundo das frutas, a sub-decisao da fruta."""
        for g in self._pesos:
            for a in self._pesos[g]:
                for w, w0 in zip(self._pesos[g][a], self._prior[g][a]):
                    yield abs(w - w0)
        for f, w in self._pesos_fruta.items():
            yield abs(w - self._prior_fruta[f])
        if self._peso_info is not None:
            yield abs(self._peso_info - self._prior_info)
        for f, w in self._pesos_comer_fruta.items():
            yield abs(w - self._prior_comer_fruta[f])
        if self._peso_pedido is not None:
            yield abs(self._peso_pedido - self._prior_pedido)
        for g in self._pesos_corpo:
            for a in self._pesos_corpo[g]:
                for w, w0 in zip(self._pesos_corpo[g][a], self._prior_corpo[g][a]):
                    yield abs(w - w0)
        for t, w in self._pesos_alvo.items():
            yield abs(w - self._prior_alvo[t])
        for k, tabela in self._pesos_alvo_mundo.items():
            for c, w in tabela.items():
                yield abs(w - self._prior_alvo_mundo[k][c])
        for g in self._pesos_social:
            for a in self._pesos_social[g]:
                for w, w0 in zip(self._pesos_social[g][a], self._prior_social[g][a]):
                    yield abs(w - w0)

    def desvio_maximo(self) -> int:
        """max |w - w0| sobre todos os pesos (o quanto o aprendizado se afastou do prior)."""
        return max(self._desvios())

    def pesos_no_teto(self) -> int:
        """Quantos pesos estao exatamente no teto (|w - w0| == teto)."""
        return sum(d == self.cl.teto for d in self._desvios())

    def percepcao(self, obs: Observacao) -> list[float]:
        return percepcao(obs, self.cl.escala_ticks_desde_cuidado)

    # ------------------------------------------------------------- decisao: pedacos comuns

    def _p_pedido(self) -> float:
        """N7: -1 quando toda fruta no cenario tem pedido vigente ("deixe X"; com uma fruta so, e a propria X); 0 nos outros casos (sem
        fruta, ou com uma fruta sem pedido, o pet pode comer outra coisa e o conflito com a necessidade nao existe)."""
        pres = self._presenca_na_decisao or (0.0,) * len(FRUTAS)
        ped = self._pedido_na_decisao or (0.0,) * len(FRUTAS)
        presentes = [i for i, v in enumerate(pres) if v > 0.0]
        return -1.0 if presentes and all(ped[i] < 0.0 for i in presentes) else 0.0

    def _pesos_efetivos(self, grupo: str, candidatos: tuple[AcaoPet, ...], x: list[float],
                        sem_pedido: bool = False) -> tuple[dict, dict]:
        """(contribuicoes por termo, peso efetivo por candidato). Termos: impulsos (prior), decisao (pesos menos
        prior), memoria_emocao (zero), piso (so com o aprendizado ligado)."""
        prior, pesos = self._prior[grupo], self._pesos[grupo]
        c = {
            "impulsos": {a: ativacao(prior[a], x, self._escala) for a in candidatos},
            "decisao": {a: ativacao([w - w0 for w, w0 in zip(pesos[a], prior[a])], x, self._escala) for a in candidatos},
            "memoria_emocao": self.memoria.contribuicao(candidatos),
        }
        if grupo == REGRAS_MUNDO[1] and self._pesos_comer_fruta and AcaoPet.COMER in candidatos:
            # FRUTA-NO-CENARIO: comer na regra das frutas soma (w_f / S) x presenca_f das frutas no cenario; no prior (w_f = 0) o termo
            # e 0.0 exato e o peso efetivo e o do instinto, byte a byte
            termo = 0.0
            for f, presente in zip(FRUTAS, self._presenca_na_decisao or (0.0,) * len(FRUTAS)):
                termo = termo + (self._pesos_comer_fruta[f] / self._escala) * presente
            c["decisao"][AcaoPet.COMER] = c["decisao"][AcaoPet.COMER] + termo
        if grupo in self._pesos_corpo:
            # CORPO: as entradas novas (receptores novos / S) nas regras de tempo livre, um peso por (regra, acao, receptor), prior 0
            tabela = self._pesos_corpo[grupo]
            if self._banheiro is None:
                for a in candidatos:
                    c["decisao"][a] = c["decisao"][a] + ativacao(tabela[a], self._x_corpo, self._escala)
            else:
                # banheiro: o prior das entradas do corpo deixa de ser zero (w_vontade na vontade do `aliviar`, o termo do instinto do
                # alivio): o prior vai a impulsos e o aprendido (w - w0) a decisao. Nas outras acoes o prior e 0 e o termo de impulsos e
                # 0.0 exato
                prior_c = self._prior_corpo[grupo]
                for a in candidatos:
                    c["impulsos"][a] = c["impulsos"][a] + ativacao(prior_c[a], self._x_corpo, self._escala)
                    c["decisao"][a] = c["decisao"][a] + ativacao([w - w0 for w, w0 in zip(tabela[a], prior_c[a])], self._x_corpo,
                                                                 self._escala)
        if grupo in self._pesos_social:
            # dois pets, etapa 4: as entradas sociais nas regras de tempo livre, um peso por (regra, acao, entrada), prior 0 (todo o termo e
            # aprendido); no prior o termo e 0.0 exato e o peso efetivo e o do instinto, byte a byte
            tabela = self._pesos_social[grupo]
            for a in candidatos:
                if a not in tabela:
                    raise RuntimeError(f"entradas sociais: {a.value} candidato na regra {grupo!r} sem linha na tabela")
                c["decisao"][a] = c["decisao"][a] + ativacao(tabela[a], self._x_social, self._escala)
        com_pedido = False
        if (self._peso_pedido is not None and not sem_pedido and grupo in REGRAS_PEDIDO and AcaoPet.COMER in candidatos):
            # N7: comer ganha (w_pedido / S) x p, com p = -1 quando toda fruta no cenario tem pedido vigente. As regras urgentes
            # (sono, pedido de necessidade, abandono) nao leem o pedido (N7-3): a necessidade forte toma a frente por construcao
            p = self._p_pedido()
            if p != 0.0:
                c["decisao"][AcaoPet.COMER] = c["decisao"][AcaoPet.COMER] + (self._peso_pedido / self._escala) * p
                com_pedido = True
        soma = {a: c["impulsos"][a] + c["decisao"][a] + c["memoria_emocao"][a] for a in candidatos}
        if self._aprende:
            c["piso"] = {a: (self._piso - soma[a] if soma[a] < self._piso else 0.0) for a in candidatos}
        else:
            c["piso"] = {a: 0.0 for a in candidatos}
            if com_pedido and soma[AcaoPet.COMER] < self._piso:
                c["piso"][AcaoPet.COMER] = self._piso - soma[AcaoPet.COMER]   # o pedido pode levar comer abaixo de zero
        efetivos = {a: c["impulsos"][a] + c["decisao"][a] + c["memoria_emocao"][a] + c["piso"][a] for a in candidatos}
        return c, efetivos

    def _registrar(self, grupo: str, candidatos: tuple[AcaoPet, ...], acao: AcaoPet, x: list[float], pesos: dict,
                   contrib: dict, u: float | None, extra: dict | None = None) -> None:
        """Guarda o registro da decisao (para o credito) e o motivo (para o G4)."""
        aprendido = None
        registro = None
        if self._aprende:
            S = self._escala
            prior, tabela = self._prior[grupo], self._pesos[grupo]
            aprendido = {a.value: termos([w - w0 for w, w0 in zip(tabela[a], prior[a])], x, S) for a in candidatos}
            total = 0.0
            for a in candidatos:
                total = total + pesos[a]
            registro = {
                "regra": grupo, "candidatos": candidatos, "acao": acao,
                "X": [arred(xj * S) for xj in x],
                "P": {a: arred(pesos[a] / total * S) for a in candidatos},
                "W": {a: max(1, arred(pesos[a] * S)) for a in candidatos},
            }
        self._registro_decisao = registro
        maior = max(LOBOS[1:], key=lambda lobo: (contrib[lobo][acao], -LOBOS.index(lobo)))
        self.motivos.append({
            "n": len(self.motivos), "regra": grupo, "candidatos": [a.value for a in candidatos],
            "percepcao": dict(zip(self.entradas, x)),
            "contribuicoes": {lobo: {a.value: v for a, v in por_acao.items()} for lobo, por_acao in contrib.items()},
            "pesos": {a.value: v for a, v in pesos.items()},
            "u": u, "acao": acao.value, "lobo_decisivo": maior, "aprendido": aprendido, **(extra or {}),
        })

    # ------------------------------------------------------------- credito (janela da v1)

    def _esperar_gancho_corpo(self, transicao: Transicao) -> None:
        """CORPO: cada decisao observada espera UM gancho do corpo (consequencia_corpo, ou consequencia_mundo no mundo fisico) antes da
        proxima. Sem o corpo, nada."""
        if self._corpo is None:
            return
        if self._acao_sem_gancho is not None:
            raise RuntimeError(f"corpo: a decisao anterior ({self._acao_sem_gancho.value}) ficou sem o gancho de consequencia")
        if transicao.observacao.corpo is None or transicao.observacao_seguinte.corpo is None:
            raise RuntimeError("corpo: transicao sem Observacao.corpo (o cerebro com a chave do corpo precisa do MotorCorpo)")
        self._acao_sem_gancho = transicao.acao

    def observar(self, transicao: Transicao) -> None:
        self.memoria.decisao()
        self._esperar_gancho_corpo(transicao)
        if not self._aprende:
            return
        obs = transicao.observacao
        tick = obs.ticks_desde_cuidado + self._tick_ultimo_cuidado
        if obs.ticks_desde_cuidado < 0 or tick <= self._tick_ultima_decisao:
            raise RuntimeError(f"relogio inconsistente: decisao em {tick}, anterior {self._tick_ultima_decisao}")
        self._tick_ultima_decisao = tick
        self._expirar(tick)
        registro = self._registro_decisao
        if registro is None or registro["acao"] is not transicao.acao:
            raise RuntimeError("registro da decisao nao corresponde a acao observada")
        self._ultima = registro
        self._guardar_no_traco(registro)
        if transicao.acao is AcaoPet.CHAMAR_ATENCAO:
            self._pendentes.append((tick, registro))

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """Gancho do MotorComFeedback. L0: o feedback so passa pela memoria. L1: credita a decisao (janela da v1)."""
        self.memoria.acao_dono(acao, tick)
        if not self._aprende:
            return
        if tick < self._tick_ultimo_cuidado:
            raise RuntimeError(f"acao do dono no passado: {tick} < {self._tick_ultimo_cuidado}")
        self._tick_ultimo_cuidado = tick
        self._expirar(tick)
        S = self._escala
        if acao in FEEDBACK:
            if self._ultima is None:
                return                                   # feedback antes da primeira decisao nao tem a quem creditar
            if acao is AcaoUsuario.ELOGIAR:
                self._creditar(self._ultima, arred(self.cl.recompensa_elogio * S), self._anteriores(self._ultima))
                self._n_recompensas["elogio"] += 1
            else:
                self._creditar(self._ultima, arred(self.cl.recompensa_repreensao * S), self._anteriores(self._ultima))
                self._n_recompensas["repreensao"] += 1
        elif acao.value == VALOR_TAPA:
            # corpo, etapa 6 (secao 8; CD-9, CD-10): o tapa manda o sinal direto, o valor da bronca, a ultima decisao, pela janela da v1;
            # escalar (os canais nao o dividem). A dor, o susto e o estresse que ele causa ficam no corpo e nao sao creditados aqui
            if self._ultima is None:
                return
            self._creditar(self._ultima, arred(self.cl.recompensa_tapa * S), self._anteriores(self._ultima))
            self._n_recompensas["tapa"] = self._n_recompensas.get("tapa", 0) + 1
        elif acao in CUIDADOS:
            self._pagar_chamados(tick)
        # outras acoes do dono (treino etc.) nao creditam nada: so a memoria as conta

    def _pagar_chamados(self, tick: int) -> None:
        """O primeiro cuidado dentro da janela paga os chamados pendentes: S - div_arred(L S, janela), L a latencia."""
        S = self._escala
        janela = self.cl.janela_latencia_ticks
        for tick_pedido, registro in self._pendentes:
            self._aplicar_sinal(registro, S - div_arred((tick - tick_pedido) * S, janela))
            self._n_recompensas["latencia"] += 1
        self._pendentes = []

    def mudanca_no_corpo(self, obs_antes: Observacao, obs_depois: Observacao) -> None:
        """Gancho do MotorCorpo com `gestos` (secao 8; CD-4): o carinho chega ao cerebro so pelo corpo, sem dizer que gesto foi. O cerebro
        calcula o `sinal_corpo` dos receptores antes e depois do carinho (os drives do sinal: os do N3 e os novos; o humor nao, como fora
        da fruta) e o credita a ultima decisao pela janela da v1, escalar, como o elogio. O carinho e cuidado: acerta o relogio do cuidado
        (o carinho zera o `ticks_desde_cuidado`; o instante dele e o `ticks_desde_cuidado` do `obs_antes`) e paga os chamados pendentes,
        como hoje. Com o aprendizado desligado, so a memoria o conta. Um cerebro que aprende sem a chave do corpo falha alto: sem os
        receptores nao ha sinal."""
        tick = self._tick_ultimo_cuidado + obs_antes.ticks_desde_cuidado
        self.memoria.acao_dono(AcaoUsuario.ACARICIAR, tick)
        if not self._aprende:
            return
        if self._corpo is None:
            raise RuntimeError("mudanca_no_corpo num cerebro que aprende sem a chave do corpo (cfg_corpo)")
        if obs_antes.corpo is None or obs_depois.corpo is None:
            raise RuntimeError("mudanca_no_corpo sem Observacao.corpo")
        if obs_depois.ticks_desde_cuidado != 0:
            raise RuntimeError("mudanca_no_corpo: o carinho e contato e zera o ticks_desde_cuidado")
        self._tick_ultimo_cuidado = tick
        self._expirar(tick)
        self._pagar_chamados(tick)
        if self._ultima is None:
            return
        cc = self._cc_corpo or CONFIG_CONSEQUENCIA
        S = self._escala
        f = sinal_corpo(obs_antes.corpo, obs_depois.corpo, self._drives_corpo(cc, False), cc.ganho, S, dict(cc.pesos_drives_corpo))
        self._n_recompensas["carinho"] = self._n_recompensas.get("carinho", 0) + 1
        if f != 0:
            self._creditar(self._ultima, f, self._anteriores(self._ultima))

    def _expirar(self, tick: int) -> None:
        janela = self.cl.janela_latencia_ticks
        vivos = []
        for tick_pedido, registro in self._pendentes:
            if tick - tick_pedido > janela:
                self._aplicar_sinal(registro, arred(self.cl.recompensa_pedido_ignorado * self._escala))
                self._n_recompensas["ignorado"] += 1
            else:
                vivos.append((tick_pedido, registro))
        self._pendentes = vivos

    def observar_consequencia(self, transicao: Transicao, f_S: int, cfg_consequencia: ConfigConsequencia | None = None) -> None:
        """V2, N3: credita `f_S` (a consequencia da propria acao, calculada fora: `sinal_homeostatico`) a decisao observada,
        pela mesma regra de atualizacao da L1. Fonte sem dono: nao passa pelo relogio de cuidado nem pelos chamados pendentes
        (o credito do chamado depende do dono). Com o aprendizado desligado so conta a decisao (a vida e a do P0).

        E2 (LOBOS-MUNDO): comer com fruta no cenario NAO credita aqui. O motor come a fruta depois desta chamada
        (MotorFrutas._decisao_observada), entao o credito fica pendente ate `fruta_comida`, que calcula o sinal da fruta com
        `cfg_consequencia` (o mesmo ganho de `f_S`). Sem fruta na decisao (e sem frutas no mundo), o N3 de sempre.

        A2.4 (`ConfigConsequencia.pesos_janela`, o braco P1-cw): o sinal passa a ser calculado aqui, com o peso de cada drive pela falta
        media dele nas ultimas J decisoes (`pesos_da_janela`). O `f_S` recebido tem de ser o `sinal_homeostatico` da transicao (confere e
        falha alto); os mesmos pesos valem no antes e no depois, na E2 e no mundo, e a janela anda depois da decisao. Os pesos ficam no
        motivo da decisao (`pesos_janela`, por canal).

        CORPO (etapa 5): com a chave do corpo o credito espera o gancho (consequencia_corpo, ou consequencia_mundo no mundo fisico), que
        calcula `sinal_corpo` sobre os receptores, antes = esta decisao, depois = o `obs_depois` do gancho. O `f_S` que chega aqui e o do
        N3 sobre a transicao do engine (sem os estimulos dos motores filhos): conferido, e nao creditado. Com `pesos_janela`, as faltas da
        janela vem dos receptores."""
        self.memoria.decisao()
        self._esperar_gancho_corpo(transicao)
        if not self._aprende:
            return
        if self._consequencia_pendente is not None:
            raise RuntimeError("E2: o comer com fruta da decisao anterior ficou sem fruta_comida")
        registro = self._registro_decisao
        if registro is None or registro["acao"] is not transicao.acao:
            raise RuntimeError("registro da decisao nao corresponde a acao observada")
        self._ultima = registro
        self._guardar_no_traco(registro)
        anteriores = self._anteriores(registro)
        self._n_recompensas["consequencia"] = self._n_recompensas.get("consequencia", 0) + 1
        cc = cfg_consequencia or CONFIG_CONSEQUENCIA
        if cc.canais_ligados and self.cl.traco_decisoes:
            raise ValueError("CANAIS-REFORCO: os canais nao andam com o traco (traco_decisoes > 0); o T3 nao tem traco (R1)")
        if self._corpo is not None:
            self._pendurar_no_corpo(registro, transicao, f_S, cc, anteriores)
            return
        pesos = None
        if cc.pesos_janela:
            S = self._escala
            if f_S != sinal_homeostatico(transicao, S, cc):
                raise RuntimeError("pesos_janela: o f_S recebido nao e o sinal_homeostatico da transicao")
            drives = _drives_fruta(cc)                # os do N3 e, com a E2, o humor
            pesos = pesos_da_janela(self._janela_faltas, drives, S)
            f_S = sinal_homeostatico(transicao, S, cc, pesos)
            self._janela_faltas.append(faltas_da_observacao(transicao.observacao, drives, S))   # a janela anda depois da decisao
            del self._janela_faltas[:-cc.janela_pesos]
            if self.motivos:
                self.motivos[-1]["pesos_janela"] = {CANAL_DO_DRIVE[i]: w for i, w in pesos.items()}
        if self._ve_mundo_fisico and transicao.acao in self._acoes_com_alvo:
            # MUNDO-CEREBROS: no mundo fisico comer pode so andar, e o que comeu so o motor sabe; o credito espera o consequencia_mundo
            self._consequencia_mundo_pendente = (registro, transicao, cc, anteriores, f_S, pesos)
            return
        if self._fruta_na_decisao and transicao.acao is AcaoPet.COMER:
            self._consequencia_pendente = (registro, transicao, cc, anteriores)
            self._pesos_da_e2 = pesos
            return
        if cc.canais_ligados:
            canais = sinal_homeostatico_canais(transicao, self._escala, cc, pesos)
            self._creditar_canais(registro, canais, f_S)
        elif f_S != 0:
            self._creditar(registro, f_S, anteriores, consequencia=True)

    def fruta_comida(self, fruta: str, obs_depois: Observacao) -> None:
        """Gancho do MotorFrutas, logo depois de o pet comer `fruta` (`obs_depois` = o estado depois de comer). So credita na
        fonte "consequencia" (E2): o comer pendente recebe `sinal_homeostatico_fruta`. Nas outras fontes, ou com o aprendizado
        desligado, nao ha pendente e o aviso nao faz nada (a fruta escolhida ja esta no registro da decisao).

        N6: com a memoria ligada, em toda fonte, o consumo vira um episodio: valencia = arred(dhumor / |efeito_humor_ruim| x S),
        cortada em [-S, S], com dhumor = humor logo depois de comer - humor na decisao (os mesmos antes e depois da E2)."""
        if self._memoria is not None:
            S = self._escala
            dh = obs_depois.vetor_estado[INDICE_HUMOR] - self._humor_na_decisao
            v = arred(dh / self._efeito_humor_ruim * S)
            self._memoria.codificar(self._tick_na_decisao, fruta, max(-S, min(S, v)))
        if self._corpo is not None:
            # CORPO: o credito e no gancho do corpo; aqui so se anota a fruta comida (o humor entra no sinal dela, E2). No mundo fisico a
            # fruta vem do `ocorrido` do consequencia_mundo
            p = self._corpo_pendente
            if p is not None and not self._ve_mundo_fisico:
                sub = p["registro"].get("fruta")
                if p["fruta"] is not None or sub is None or sub["acao"] != fruta:
                    raise RuntimeError(f"corpo: fruta comida {fruta!r} nao e a da sub-decisao registrada (ou veio duas vezes)")
                p["fruta"] = fruta
            return
        pendente, self._consequencia_pendente = self._consequencia_pendente, None
        if pendente is None:
            return
        registro, transicao, cc, anteriores = pendente
        pesos, self._pesos_da_e2 = self._pesos_da_e2, None
        sub = registro.get("fruta")
        if sub is None or sub["acao"] != fruta:
            raise RuntimeError(f"E2: fruta comida {fruta!r} nao e a da sub-decisao registrada")
        self._n_recompensas["consequencia_fruta"] = self._n_recompensas.get("consequencia_fruta", 0) + 1
        f_S = sinal_homeostatico_fruta(transicao.observacao, obs_depois, self._escala, cc, pesos)
        if cc.canais_ligados:
            canais = sinal_homeostatico_fruta_canais(transicao.observacao, obs_depois, self._escala, cc, pesos)
            self._creditar_canais(registro, canais, f_S)
        elif f_S != 0:
            self._creditar(registro, f_S, anteriores, consequencia=True)

    def consequencia_mundo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        """Gancho do MotorMundo (docs/TAREFA_V2_MUNDO_FISICO.md, secao 8), uma vez por decisao de explorar, comer ou brincar, depois do
        `observar` e do `fruta_comida`, com tudo aplicado (andou, comeu, brincou). Sem o mundo (a chave do cerebro, `cfg_mundo`), nada.

        Anota o que aconteceu no motivo da decisao (o alvo, se chegou, o que comeu). Na fonte consequencia, credita o sinal que o
        `observar_consequencia` deixou pendente, pela mesma regra de sempre (escalar ou canais):
        - comer que comeu uma fruta: a E2, `sinal_homeostatico_fruta` (o humor entra nos drives), antes = a observacao da decisao,
          depois = `obs_depois`;
        - o resto (andar, brincar, comer racao, comer sem comida, o "achou e comeu" do explorar): o `f_S` que veio com a transicao
          (o `sinal_homeostatico` do N3, sem o humor). A E2 fica so no comer, como no N4: o explorar tem +0,01 de humor proprio, que o
          sinal do P1 nao ve (F6).
        Nas outras fontes (dono, nenhuma) nao ha pendente e nada e creditado."""
        if not self._ve_mundo_fisico:
            return
        if self.motivos:
            alvo = ocorrido["alvo"]
            comeu = ocorrido["comeu"]
            self.motivos[-1].setdefault("mundo", {}).update({
                "alvo": None if alvo is None else alvo["tipo"], "chegou": ocorrido["chegou"],
                "deslocamento": ocorrido["deslocamento"], "comeu": None if comeu is None else comeu["tipo"],
                "como": None if comeu is None else comeu["como"], "brincou_com_bola": ocorrido["brincou_com_bola"]})
        if self._modelo is not None:
            self._modelo.consequencia(ocorrido, obs_depois, self._social_na_decisao)
        if self._corpo is not None:
            # CORPO com o mundo fisico (secao 9; o arranjo do MotorCorpo do #238): o corpo ja aplicou os estimulos do `ocorrido`, e o sinal e
            # o do corpo, sobre o obs_depois. A E2 so no comer que comeu fruta, como sem o corpo. Este gancho credita, e o
            # `consequencia_corpo` que vem logo depois, na mesma decisao, so fecha a decisao
            if self._acao_sem_gancho is not acao or ocorrido["acao"] != acao.value:
                raise RuntimeError(f"corpo: consequencia_mundo de {acao.value} sem a decisao observada de {acao.value}")
            if self._mundo_creditou is not None:
                raise RuntimeError("corpo: segunda consequencia_mundo na mesma decisao")
            self._mundo_creditou = acao
            comeu = ocorrido["comeu"]
            fruta = comeu["tipo"] if acao is AcaoPet.COMER and comeu is not None and comeu["tipo"] in FRUTAS else None
            self._creditar_corpo(fruta, obs_depois)
            return
        pendente, self._consequencia_mundo_pendente = self._consequencia_mundo_pendente, None
        if pendente is None:
            return
        registro, transicao, cc, anteriores, f_S, pesos = pendente
        if transicao.acao is not acao or ocorrido["acao"] != acao.value:
            raise RuntimeError(f"consequencia_mundo de {acao.value} para a decisao pendente de {transicao.acao.value}")
        if transicao.observacao_seguinte.vetor_estado != obs_depois.vetor_estado:
            raise RuntimeError("consequencia_mundo com um obs_depois diferente da observacao seguinte da transicao")
        comeu = ocorrido["comeu"]
        S = self._escala
        if acao is AcaoPet.COMER and comeu is not None and comeu["tipo"] in FRUTAS:
            self._n_recompensas["consequencia_fruta"] = self._n_recompensas.get("consequencia_fruta", 0) + 1
            f = sinal_homeostatico_fruta(transicao.observacao, obs_depois, S, cc, pesos)
            canais = sinal_homeostatico_fruta_canais(transicao.observacao, obs_depois, S, cc, pesos) if cc.canais_ligados else None
        else:
            f = f_S
            canais = sinal_homeostatico_canais(transicao, S, cc, pesos) if cc.canais_ligados else None
        if canais is not None:
            self._creditar_canais(registro, canais, f)
        elif f != 0:
            self._creditar(registro, f, anteriores, consequencia=True)

    # ------------------------------------------------------------- CORPO (etapa 5): o sinal pelos receptores, no gancho do corpo

    def consequencia_corpo(self, acao: AcaoPet, ocorrido: dict, obs_depois: Observacao) -> None:
        """Gancho do MotorCorpo sem o mundo fisico (docs/TAREFA_V2_CORPO_DRIVES.md, secao 9): uma vez por decisao, logo depois dos
        estimulos da propria acao (o pet, a bola, a fruta) e antes do tempo e do dono; `obs_depois.corpo` ja os tem. Sem a chave do corpo
        no cerebro, nada (o cerebro vive como hoje, com o sinal do N3 da transicao). Com ela, credita o `sinal_corpo` pendente (so na
        fonte consequencia) e confere que e a decisao observada (uma chamada por decisao, falha alto).

        Com o mundo fisico (o arranjo do MotorCorpo, #238): explorar, comer e brincar sao creditados no `consequencia_mundo`, que vem antes
        na mesma decisao (o `ocorrido` dele diz o que o pet comeu); este gancho vem sempre, uma vez por decisao, e nessas tres acoes so
        fecha a decisao (sem o `consequencia_mundo` antes, falha alto). Nas outras acoes, credita aqui. Com o banheiro, o aliviar (que
        tem alvo) vai com as tres."""
        if self._corpo is None:
            return
        mundo, self._mundo_creditou = self._mundo_creditou, None
        if self._ve_mundo_fisico and acao in self._acoes_com_alvo:
            if mundo is not acao:
                raise RuntimeError(f"corpo com o mundo fisico: {acao.value} sem o consequencia_mundo antes do consequencia_corpo")
            self._gancho_recebido(acao, ocorrido["acao"])
            return
        if mundo is not None:
            raise RuntimeError(f"corpo: consequencia_mundo numa decisao de {acao.value}")
        self._gancho_recebido(acao, ocorrido["acao"])
        frutas = [e[1] for e in ocorrido["estimulos"] if e[0] == "fruta"]
        if len(frutas) > 1:
            raise RuntimeError(f"corpo: duas frutas numa decisao {frutas}")
        fruta = frutas[0] if frutas else None
        p = self._corpo_pendente
        if p is not None and p["fruta"] != fruta:
            raise RuntimeError(f"corpo: o estimulo da fruta ({fruta!r}) nao e a fruta_comida da decisao ({p['fruta']!r})")
        self._creditar_corpo(fruta, obs_depois)

    def _gancho_recebido(self, acao: AcaoPet, valor: str) -> None:
        esperada, self._acao_sem_gancho = self._acao_sem_gancho, None
        if esperada is None:
            raise RuntimeError("corpo: gancho de consequencia sem decisao observada (ou a segunda chamada na mesma decisao)")
        if esperada is not acao or valor != acao.value:
            raise RuntimeError(f"corpo: gancho de {acao.value} ({valor}) para a decisao observada de {esperada.value}")

    def _drives_corpo(self, cc: ConfigConsequencia, com_humor: bool) -> tuple:
        """Os drives do sinal pelo corpo, pelo nome do receptor: os do N3 (cc.drives), o humor so com `com_humor` e a E2, e os drives
        novos que o corpo tem (secao 9; o susto fica fora)."""
        drives = tuple(RECEPTOR_DO_INDICE[i] for i in cc.drives)
        if com_humor and cc.humor_na_fruta and "humor" not in drives:
            drives = drives + ("humor",)
        return drives + self._canais_novos

    def _pendurar_no_corpo(self, registro: dict, transicao: Transicao, f_S: int, cc: ConfigConsequencia, anteriores: list) -> None:
        """observar_consequencia com a chave do corpo: confere o f_S do N3, faz os pesos da janela (A2.4, sobre os receptores) e deixa o
        credito para o gancho."""
        S = self._escala
        if f_S != sinal_homeostatico(transicao, S, cc):
            raise RuntimeError("corpo: o f_S recebido nao e o sinal_homeostatico da transicao")
        self._cc_corpo = cc
        pesos = None
        if cc.pesos_janela:
            drives = self._drives_corpo(cc, True)          # os do N3, o humor (E2) e os novos
            pesos = pesos_da_janela(self._janela_faltas, drives, S)
            self._janela_faltas.append(faltas_corpo(transicao.observacao.corpo, drives, S))   # a janela anda depois da decisao
            del self._janela_faltas[:-cc.janela_pesos]
            if self.motivos:
                self.motivos[-1]["pesos_janela"] = dict(pesos)
        self._corpo_pendente = {"registro": registro, "transicao": transicao, "cc": cc, "anteriores": anteriores, "pesos": pesos,
                                "fruta": None}

    def _creditar_corpo(self, fruta: str | None, obs_depois: Observacao) -> None:
        """O credito da decisao pendente pelo corpo: antes = a percepcao da decisao, depois = `obs_depois.corpo`; a E2 (o humor) so com a
        fruta comida. Escalar ou canais, como sempre; a conta fica no motivo da decisao (`sinal_corpo`). Sem pendente (o P0, o P3), nada."""
        p, self._corpo_pendente = self._corpo_pendente, None
        if p is None:
            return
        if obs_depois.corpo is None:
            raise RuntimeError("corpo: obs_depois sem Observacao.corpo")
        S = self._escala
        registro, transicao, cc, anteriores, pesos = p["registro"], p["transicao"], p["cc"], p["anteriores"], p["pesos"]
        drives = self._drives_corpo(cc, fruta is not None)
        pd = dict(cc.pesos_drives_corpo)
        antes, depois = transicao.observacao.corpo, obs_depois.corpo
        contrib = contribuicoes_corpo(antes, depois, drives, S, pd, pesos)
        f = sinal_corpo(antes, depois, drives, cc.ganho, S, pd, pesos)
        if fruta is not None:
            self._n_recompensas["consequencia_fruta"] = self._n_recompensas.get("consequencia_fruta", 0) + 1
        if self.motivos:
            self.motivos[-1]["sinal_corpo"] = {"f": f, "drives": dict(contrib)}
        if cc.canais_ligados:
            self._creditar_canais(registro, sinal_corpo_canais(antes, depois, drives, cc.ganho, S, pd, pesos), f)
        elif f != 0:
            self._creditar(registro, f, anteriores, consequencia=True)

    # ------------------------------------------------------------- CANAIS-REFORCO: o mesmo sinal, separado por canal (H-R2)

    def _sensibilidade_canal(self, canal: str) -> int:
        """Ponto de entrada da H-R4 (o genoma modulando a sensibilidade a cada canal), SEM USO: devolve S (sensibilidade 1) para
        todo canal. Uma sensibilidade diferente de S mudaria o total de sinal e quebraria o contrato K-6; entra so com o desenho da
        H-R4 (docs/research/digibrain/mechanisms/reinforcement.md)."""
        if canal not in ROTA_CANAIS and canal not in self._canais_novos:
            raise KeyError(f"canal desconhecido: {canal!r}")
        return self._escala

    def _creditar_canais(self, registro: dict, canais: dict, f_S: int) -> None:
        """Contrato K-6: a soma dos canais e o escalar `f_S` da mesma decisao (falha alto se nao for). Cada canal vai ao seu grupo
        de pesos (ROTA_CANAIS); o que chega a cada grupo e a soma dos canais dele, aplicada pela regra da L1 (_aplicar_sinal)."""
        S = self._escala
        total = 0
        alvos = {a: 0 for a in ALVOS_CANAIS}
        for canal, f in canais.items():
            sens = self._sensibilidade_canal(canal)
            if sens != S:                                 # pragma: no cover - a H-R4 ainda nao existe
                raise NotImplementedError("H-R4: sensibilidade por canal")
            total += f
            alvos[ROTA_CANAIS[canal] if canal in ROTA_CANAIS else ROTA_CANAIS_CORPO[canal]] += f
        if total != f_S:
            raise RuntimeError(f"CANAIS-REFORCO: soma dos canais {total} != escalar {f_S} (contrato K-6)")
        if alvos["fruta"] != 0 and not ("fruta" in registro or "presenca" in registro or "pedido" in registro):
            raise RuntimeError("CANAIS-REFORCO: canal da fruta sem peso que leia a fruta nesta decisao")
        if self._canais is None:
            self._canais = {"creditos": 0, "por_canal": {c: 0 for c in tuple(ROTA_CANAIS) + self._canais_novos},
                            "por_alvo": {a: 0 for a in ALVOS_CANAIS}}
        self._canais["creditos"] += 1
        for canal, f in canais.items():
            self._canais["por_canal"][canal] += f
        for a, f in alvos.items():
            self._canais["por_alvo"][a] += f
        if any(alvos.values()):
            self._aplicar_sinal(registro, f_S, consequencia=True, alvos=alvos)

    # ------------------------------------------------------------- REVISAO: o traco de elegibilidade (janela de credito)

    def _guardar_no_traco(self, registro: dict) -> None:
        K = self.cl.traco_decisoes
        if K:
            self._traco.append(registro)
            del self._traco[:-(K + 1)]

    def _anteriores(self, registro: dict) -> list[dict]:
        """As decisoes observadas antes de `registro`, da mais recente para a mais antiga, ate traco_decisoes (vazio sem traco)."""
        K = self.cl.traco_decisoes
        if not K:
            return []
        for i in range(len(self._traco) - 1, -1, -1):
            if self._traco[i] is registro:
                return self._traco[max(0, i - K):i][::-1]
        raise RuntimeError("registro fora do traco")

    def _creditar(self, registro: dict, f_S: int, anteriores: list[dict], consequencia: bool = False) -> None:
        """f_S na decisao e, pelo traco, div_arred(f_S * lambda**k, S**k) na k-esima anterior. Sem traco: _aplicar_sinal, so."""
        self._aplicar_sinal(registro, f_S, consequencia)
        S, lam = self._escala, self.cl.traco_fator
        for k, r in enumerate(anteriores, 1):
            g = div_arred(f_S * lam ** k, S ** k)
            if g == 0:
                break                                     # |f_S| lambda^k / S^k so diminui com k
            self._aplicar_sinal(r, g, consequencia)
            self._n_recompensas["traco"] = self._n_recompensas.get("traco", 0) + 1

    def _aplicar_sinal(self, registro: dict, f_S: int, consequencia: bool = False, alvos: dict | None = None) -> None:
        """Aplica f_S ao registro pela regra da L1. N5: o peso da informacao so muda pela consequencia (`consequencia`), nunca
        pelo dono (elogio, bronca, latencia ou chamado ignorado).

        CANAIS-REFORCO: com `alvos` ({"corpo": f, "fruta": f}, a soma dos canais de cada grupo, ROTA_CANAIS), a tabela da regra
        recebe o do corpo e os pesos que leem a fruta (escolha, informacao, pedido, presenca) o da fruta. Sem `alvos`, o escalar
        f_S em todos, como sempre."""
        f_corpo = f_S if alvos is None else alvos["corpo"]
        f_fruta = f_S if alvos is None else alvos["fruta"]
        g = registro["regra"]
        self._cortes_teto += atualizar_pesos(self._pesos[g], self._prior[g], registro, f_corpo, self.cl.passo, self.cl.teto,
                                             self._escala)
        if "corpo" in registro:
            # CORPO: as entradas novas da regra (as leituras dos receptores novos, X = a leitura) pela mesma regra, com o canal do corpo
            self._cortes_teto += atualizar_pesos(self._pesos_corpo[g], self._prior_corpo[g], {**registro, "X": registro["corpo"]["X"]},
                                                 f_corpo, self.cl.passo, self.cl.teto, self._escala)
        if "social" in registro:
            # dois pets, etapa 4: as entradas sociais da regra (X = a entrada x S) pela mesma regra, com o canal do corpo, de toda fonte
            # que ensina a tabela da regra (o outro pet nao manda sinal nenhum: o sinal e o da propria acao ou do dono)
            self._cortes_teto += atualizar_pesos(self._pesos_social[g], self._prior_social[g], {**registro, "X": registro["social"]["X"]},
                                                 f_corpo, self.cl.passo, self.cl.teto, self._escala)
        if consequencia and "alvo_mundo" in registro:
            # dois pets, etapa 4: a classe do alvo pela regra da sub-decisao da fruta (um peso por classe, X = S), so pela consequencia
            # (o credito do consequencia_mundo, ou do corpo no mundo fisico), com o sinal inteiro da decisao (todos os canais)
            sub = registro["alvo_mundo"]
            self._cortes_teto += atualizar_fruta(self._pesos_alvo_mundo[sub["chave"]], self._prior_alvo_mundo[sub["chave"]], sub, f_S,
                                                 self.cl.passo, self.cl.teto, self._escala)
        if "alvo" in registro:
            # banheiro: o alvo do `aliviar` pela regra da sub-decisao da fruta (um peso por alvo, X = S), com o canal do corpo
            self._cortes_teto += atualizar_fruta(self._pesos_alvo, self._prior_alvo, registro["alvo"], f_corpo, self.cl.passo,
                                                 self.cl.teto, self._escala)
        sub = registro.get("fruta")
        if sub is not None:
            self._cortes_teto += atualizar_fruta(self._pesos_fruta, self._prior_fruta, sub, f_fruta, self.cl.passo, self.cl.teto,
                                                 self._escala)
            if consequencia and "I" in sub:
                novo, corte = atualizar_info(self._peso_info, self._prior_info, sub, f_fruta, self.cl.passo, self.cl.teto,
                                             self._escala)
                self._peso_info = novo
                self._cortes_teto += corte
        if self._peso_pedido is not None and ("pedido" in registro or (sub is not None and "Pd" in sub)):
            # N7: o peso do pedido aprende com qualquer fonte que o braco tenha (P1: a consequencia; P3: o dono); P0 nao aprende
            novo, corte = atualizar_pedido(self._peso_pedido, self._prior_pedido, registro, f_fruta, self.cl.passo, self.cl.teto,
                                           self._escala)
            self._peso_pedido = novo
            self._cortes_teto += corte
        if consequencia and "presenca" in registro:
            self._cortes_teto += atualizar_comer_fruta(self._pesos_comer_fruta, self._prior_comer_fruta, registro, f_fruta,
                                                       self.cl.passo, self.cl.teto, self._escala)
        self._n_atualizacoes += 1

    # ------------------------------------------------------------- serializacao

    def _estado_aprendizado(self) -> dict:
        def registro_dict(r):
            if r is None:
                return None
            d = {"regra": r["regra"], "candidatos": [a.value for a in r["candidatos"]], "acao": r["acao"].value,
                 "X": list(r["X"]), "P": {a.value: v for a, v in r["P"].items()}, "W": {a.value: v for a, v in r["W"].items()}}
            if "fruta" in r:
                s = r["fruta"]
                d["fruta"] = {"candidatos": list(s["candidatos"]), "acao": s["acao"], "X": dict(s["X"]), "P": dict(s["P"]),
                              "W": dict(s["W"])}
                if "I" in s:
                    d["fruta"]["I"] = dict(s["I"])
            if "presenca" in r:
                d["presenca"] = dict(r["presenca"])
            if "pedido" in r:
                d["pedido"] = dict(r["pedido"])
            if "fruta" in r and "Pd" in r["fruta"]:
                d["fruta"]["Pd"] = dict(r["fruta"]["Pd"])
            if "corpo" in r:
                d["corpo"] = {"X": list(r["corpo"]["X"])}
            if "social" in r:
                d["social"] = {"X": list(r["social"]["X"])}
            if "alvo" in r:
                s = r["alvo"]
                d["alvo"] = {"candidatos": list(s["candidatos"]), "acao": s["acao"], "X": dict(s["X"]), "P": dict(s["P"]),
                             "W": dict(s["W"])}
            if "alvo_mundo" in r:
                s = r["alvo_mundo"]
                d["alvo_mundo"] = {"chave": s["chave"], "candidatos": list(s["candidatos"]), "acao": s["acao"], "X": dict(s["X"]),
                                   "P": dict(s["P"]), "W": dict(s["W"])}
            return d
        d = {
            "passo": self.cl.passo, "teto": self.cl.teto, "piso_peso": self.cl.piso_peso,
            "n_atualizacoes": self._n_atualizacoes, "cortes_teto": self._cortes_teto,
            "recompensas": dict(self._n_recompensas),
            "desvio_maximo": self.desvio_maximo(), "pesos_no_teto": self.pesos_no_teto(),
            "tick_ultimo_cuidado": self._tick_ultimo_cuidado, "tick_ultima_decisao": self._tick_ultima_decisao,
            "pendentes": [[t, registro_dict(r)] for t, r in self._pendentes],
            "ultima": registro_dict(self._ultima),
        }
        if self._consequencia_pendente is not None:     # E2: so entre observar_consequencia e fruta_comida
            d["consequencia_pendente"] = registro_dict(self._consequencia_pendente[0])
        if self._consequencia_mundo_pendente is not None:   # MUNDO-CEREBROS: so entre observar_consequencia e consequencia_mundo
            d["consequencia_mundo_pendente"] = registro_dict(self._consequencia_mundo_pendente[0])
        if self._janela_faltas:                         # A2.4, so com pesos_janela (com o corpo, ja pelo nome do receptor)
            d["janela_pesos"] = [{(i if isinstance(i, str) else CANAL_DO_DRIVE[i]): v for i, v in f.items()}
                                 for f in self._janela_faltas]
        if self._corpo_pendente is not None:            # CORPO: so entre observar_consequencia e o gancho
            d["corpo_pendente"] = registro_dict(self._corpo_pendente["registro"])
        return d

    def estado_interno(self) -> dict:
        d = {
            "nome": self.nome,
            "parametros_aprendidos": self.n_pesos(),
            "aprendizado_ligado": self._aprende,
            "escala": self._escala,
            "entradas": list(self.entradas),
            "pesos": {g: {a.value: list(v) for a, v in acoes.items()} for g, acoes in self._pesos.items()},
            "pesos_prior": {g: {a.value: list(v) for a, v in acoes.items()} for g, acoes in self._prior.items()},
            "memoria_emocao": self.memoria.para_dict(),
            "n_decisoes": len(self.motivos),
            "motivos": [dict(m) for m in self.motivos],
            "aprendizado": self._estado_aprendizado(),
        }
        if self._prior_fruta:                     # LOBOS-MUNDO, so no mundo das frutas: a sub-decisao da fruta
            d["pesos_fruta"] = dict(self._pesos_fruta)
            d["pesos_fruta_prior"] = dict(self._prior_fruta)
        if self._peso_info is not None:           # N5, so com w0_info != 0: o peso compartilhado da informacao
            d["peso_info"] = self._peso_info
            d["peso_info_prior"] = self._prior_info
        if self._prior_comer_fruta:               # FRUTA-NO-CENARIO, so no mundo das frutas: comer le a fruta presente
            d["pesos_comer_fruta"] = dict(self._pesos_comer_fruta)
            d["pesos_comer_fruta_prior"] = dict(self._prior_comer_fruta)
        if self._memoria is not None:             # N6, so com a memoria ligada
            d["memoria"] = {"ganho": self.cl.memoria_ganho, "modo": self.cl.memoria_modo, **self._memoria.para_dict()}
        if self._peso_pedido is not None:         # N7, so com w0_pedido != 0
            d["peso_pedido"] = self._peso_pedido
            d["peso_pedido_prior"] = self._prior_pedido
        if self._corpo is not None:               # CORPO, so com a chave do corpo no cerebro
            d["corpo"] = {"receptores_novos": list(self._receptores_novos), "canais_novos": list(self._canais_novos)}
            if self._pesos_corpo:
                d["pesos_corpo"] = {g: {a.value: list(v) for a, v in acoes.items()} for g, acoes in self._pesos_corpo.items()}
            if self._banheiro is not None:          # banheiro: o prior das entradas do corpo e os pesos do alvo
                d["pesos_corpo_prior"] = {g: {a.value: list(v) for a, v in acoes.items()} for g, acoes in self._prior_corpo.items()}
                d["pesos_alvo"] = dict(self._pesos_alvo)
                d["pesos_alvo_prior"] = dict(self._prior_alvo)
        if self._prior_alvo_mundo:                # dois pets, etapa 4, so com a chave do alvo aprendido
            d["pesos_alvo_mundo"] = {k: dict(t) for k, t in self._pesos_alvo_mundo.items()}
            d["pesos_alvo_mundo_prior"] = {k: dict(t) for k, t in self._prior_alvo_mundo.items()}
        if self._prior_social:                    # dois pets, etapa 4, so com a chave das entradas sociais (o prior e 0)
            d["entradas_sociais"] = list(ENTRADAS_SOCIAIS)
            d["pesos_social"] = {g: {a.value: list(v) for a, v in acoes.items()} for g, acoes in self._pesos_social.items()}
        if self._modelo is not None:              # dois pets, etapa 4, so com a chave do modelo dos outros (so registrado)
            d["modelo_outros"] = self._modelo.para_dict()
        if self._canais is not None:              # CANAIS-REFORCO, so depois do 1o credito por canal
            d["canais"] = {"creditos": self._canais["creditos"], "por_canal": dict(self._canais["por_canal"]),
                           "por_alvo": dict(self._canais["por_alvo"])}
        return d


# ------------------------------------------------------------------ a politica com lobos


class PoliticaLobos(Aprendiz):
    """Politica com lobos nomeados sob o Protocol Politica (agir, observar, estado_interno) e o gancho
    receber_acao_dono do MotorComFeedback. Nao altera engine.py. L0: aprendizado desligado (padrao);
    L1: ConfigLobos(aprendizado_ligado=True), so o lobo de decisao aprende."""

    nome = "lobos"

    def __init__(self, cfg: Config | None = None, cfg_lobos: ConfigLobos | None = None,
                 cfg_bola: ConfigBola | None = None, cfg_frutas: ConfigFrutas | None = None,
                 cfg_mundo: ConfigMundo | None = None, cfg_corpo: ConfigCorpo | None = None,
                 cfg_banheiro: ConfigBanheiro | None = None) -> None:
        cl = cfg_lobos or CONFIG_LOBOS
        # o banheiro (TAREFA_V2_BANHEIRO, secoes 2 e 4): exige o mundo fisico e o corpo com a sub-chave banheiro; o corpo com a vontade
        # exige a chave do banheiro no cerebro (sem ela o pet teria a vontade e nenhuma acao para alivia-la)
        banheiro = cfg_banheiro is not None and cfg_banheiro.ligada
        corpo_banheiro = cfg_corpo is not None and cfg_corpo.ligada and cfg_corpo.banheiro
        if banheiro != corpo_banheiro:
            raise ValueError("banheiro: a ConfigBanheiro ligada no cerebro e a sub-chave banheiro do corpo vao juntas")
        if banheiro and not (cfg_mundo is not None and cfg_mundo.ligada):
            raise ValueError("banheiro sem o mundo fisico (ConfigMundo ligada)")
        # LOBOS-MUNDO: so ve o mundo com a chave dele ligada (como o instinto); sem nenhuma, as formas de antes
        self._ve_bola = cfg_bola is not None and cfg_bola.ligada
        self._ve_frutas = cfg_frutas is not None and cfg_frutas.ligada
        self._ve_mundo = self._ve_bola or self._ve_frutas
        # MUNDO-CEREBROS: com a ConfigMundo ligada, o cerebro A ve o mundo fisico pela percepcao nova (Observacao.mundo), pela regra
        # de instinto_mundo.entradas_mundo; o instinto da sonda e o PoliticaInstintoMundo. O mundo substitui o cenario do N4 e da A1:
        # cfg_bola e cfg_frutas so dao os pesos (w_bola, w_fruta) e precisam estar desligadas, como no MotorMundo
        fisico = cfg_mundo is not None and cfg_mundo.ligada
        if fisico:
            if self._ve_mundo:
                raise ValueError("o mundo fisico substitui o cenario do N4 e da A1: cfg_bola e cfg_frutas desligadas com cfg_mundo ligada")
            from ..instinto_mundo import PoliticaInstintoMundo, REGRA_FOME_URGENTE
            from ..ambiente import REGRA_BOLA
            from ..frutas import REGRA_FRUTA
            if (REGRA_BOLA, REGRA_FRUTA) != REGRAS_MUNDO:
                raise RuntimeError(f"regras do mundo mudaram: {(REGRA_BOLA, REGRA_FRUTA)}")
            self.entradas = ENTRADAS + ENTRADAS_MUNDO
            cb = replace(cfg_bola or CONFIG_BOLA, ligada=True)        # so para o prior ter os termos do mundo (os pesos)
            cf = replace(cfg_frutas or CONFIG_FRUTAS, ligada=True)
            extra = self._prior_mundo(cb, cf)
            # a fome urgente com para onde ir come (instinto_mundo): o unico candidato da regra pode ser comer
            extra[REGRA_FOME_URGENTE] = {**PRIOR_INSTINTO[REGRA_FOME_URGENTE], AcaoPet.COMER: {"vies": 1}}
            if banheiro:
                # o banheiro: a regra urgente (so o aliviar) e o aliviar nas regras de tempo livre, com a linha das entradas de hoje
                # em zero (o termo dele vem da vontade, nas entradas do corpo)
                from ..instinto_banheiro import REGRA_ALIVIO_URGENTE as REGRA_URG, ALVOS_ALIVIO as ALVOS
                if (REGRA_URG, ALVOS) != (REGRA_ALIVIO_URGENTE, ALVOS_ALIVIO):
                    raise RuntimeError(f"regra ou alvos do banheiro mudaram: {REGRA_URG}, {ALVOS}")
                extra[REGRA_ALIVIO_URGENTE] = {AcaoPet.ALIVIAR: {"vies": 1}}
                acoes_por_regra = {r: ACOES + (AcaoPet.ALIVIAR,) for r in REGRAS_ENTRADAS_CORPO}
                acoes_por_regra[REGRA_ALIVIO_URGENTE] = (AcaoPet.ALIVIAR,)
                prior = self._tabela_prior(cl.escala, REGRAS + REGRAS_MUNDO + (REGRA_ALIVIO_URGENTE,), self.entradas, extra,
                                           acoes_por_regra)
            else:
                prior = self._tabela_prior(cl.escala, REGRAS + REGRAS_MUNDO, self.entradas, extra)
            prior_fruta = prior_comer = None              # sem a sub-decisao da fruta: o mundo nao chama o escolher_fruta
        elif self._ve_mundo:
            from ..frutas import PoliticaInstintoFrutas, REGRA_FRUTA   # importacao tardia: frutas importa o motor inteiro
            from ..ambiente import REGRA_BOLA
            if (REGRA_BOLA, REGRA_FRUTA) != REGRAS_MUNDO:
                raise RuntimeError(f"regras do mundo mudaram: {(REGRA_BOLA, REGRA_FRUTA)}")
            self.entradas = ENTRADAS + ENTRADAS_MUNDO
            cb = cfg_bola if self._ve_bola else replace(cfg_bola or CONFIG_BOLA, ligada=False)
            cf = cfg_frutas if self._ve_frutas else replace(cfg_frutas or CONFIG_FRUTAS, ligada=False)
            prior = self._tabela_prior(cl.escala, REGRAS + REGRAS_MUNDO, self.entradas, self._prior_mundo(cb, cf))
            prior_fruta = {f: cl.escala for f in FRUTAS} if self._ve_frutas else None
            prior_comer = {f: 0 for f in FRUTAS} if self._ve_frutas else None
        else:
            prior, prior_fruta, prior_comer = self._tabela_prior(cl.escala), None, None
        super().__init__(cfg, cl, prior, prior_fruta, prior_comer)
        if fisico:
            from ..instinto_mundo import entradas_mundo
            self._ve_mundo = self._ve_mundo_fisico = True
            self._entradas_mundo = entradas_mundo
            if banheiro:
                from ..instinto_banheiro import PoliticaInstintoBanheiro
                self._instinto = PoliticaInstintoBanheiro(self.cfg, cfg_banheiro, cfg_corpo, cfg_bola, cfg_frutas)
            else:
                self._instinto = PoliticaInstintoMundo(self.cfg, cfg_bola, cfg_frutas)
        else:
            self._instinto = PoliticaInstintoFrutas(self.cfg, cb, cf) if self._ve_mundo else PoliticaInstinto(self.cfg)
        self._ultima_regra: str | None = None
        # N5 (N5-1 a N5-3): a entrada `info` da sub-decisao da fruta, com um peso so; w0_info 0 = desligada (a vida de hoje)
        w0 = cl.w0_info
        if type(w0) is not int or w0 < 0:
            raise ValueError(f"ConfigLobos.w0_info precisa ser inteiro >= 0: {w0!r}")
        if self._ve_frutas and w0 != 0:
            self._prior_info = self._peso_info = w0
            if self.n_pesos() >= cl.maximo_pesos:
                raise ValueError(f"{self.n_pesos()} pesos, teto {cl.maximo_pesos}")
        # N6: a memoria de episodios (so nos lobos que veem as frutas; desligada, nada existe)
        if cl.memoria_modo not in MODOS_MEMORIA:
            raise ValueError(f"ConfigLobos.memoria_modo {cl.memoria_modo!r}: so {MODOS_MEMORIA}")
        if type(cl.memoria_ganho) is not int or not 0 <= cl.memoria_ganho < cl.escala:
            raise ValueError(f"ConfigLobos.memoria_ganho precisa ser inteiro em [0, S): {cl.memoria_ganho!r}")
        if type(cl.memoria_janela_recencia_ticks) is not int or cl.memoria_janela_recencia_ticks <= 0:
            raise ValueError("ConfigLobos.memoria_janela_recencia_ticks precisa ser inteiro positivo")
        self._permutacao = {}
        if cl.memoria_modo == "embaralhada":
            perm = tuple(cl.memoria_permutacao)
            if sorted(perm) != sorted(FRUTAS) or any(p == f for p, f in zip(perm, FRUTAS)):
                raise ValueError(f"memoria embaralhada pede um desarranjo de {FRUTAS} (desarranjo_n6): {perm!r}")
            self._permutacao = dict(zip(FRUTAS, perm))
        elif cl.memoria_permutacao:
            raise ValueError("memoria_permutacao so vale no modo embaralhada")
        if cl.memoria_ligada and self._ve_frutas:
            if cf.efeito_humor_ruim == 0.0:
                raise ValueError("a valencia do episodio e medida em |efeito_humor_ruim|, que e zero")
            self._efeito_humor_ruim = abs(cf.efeito_humor_ruim)
            m = CONFIG_MEMORIA_ESPACOS
            self._memoria = MemoriaEpisodios(m.n_curto, m.n_longo, m.d_curto_ticks)
        # N7: o peso compartilhado do pedido (so nos lobos que veem as frutas; 0 = desligado)
        if type(cl.w0_pedido) is not int or cl.w0_pedido < 0:
            raise ValueError(f"ConfigLobos.w0_pedido precisa ser inteiro >= 0: {cl.w0_pedido!r}")
        if self._ve_frutas and cl.w0_pedido != 0:
            self._prior_pedido = self._peso_pedido = cl.w0_pedido
            if self.n_pesos() >= cl.maximo_pesos:
                raise ValueError(f"{self.n_pesos()} pesos, teto {cl.maximo_pesos}")
        # CORPO (etapa 5): com a chave do corpo, o sinal pelos receptores, as entradas novas e os canais novos
        if cfg_corpo is not None and cfg_corpo.ligada:
            if cfg_corpo.escala_receptor != cl.escala:
                raise ValueError(f"receptores na escala {cfg_corpo.escala_receptor}, cerebro na escala {cl.escala}: tem de ser a mesma S")
            self._corpo = cfg_corpo
            self._receptores_novos = receptores_novos(cfg_corpo, fisico)
            self._canais_novos = tuple(d for d in DRIVES_NOVOS_SINAL if d in self._receptores_novos)
            if self._receptores_novos:
                n = len(self._receptores_novos)
                self._prior_corpo = {r: {a: [0] * n for a in self._prior[r]} for r in REGRAS_ENTRADAS_CORPO if r in self._prior}
                if banheiro:
                    # o termo do instinto do alivio, w_vontade x vontade, e o prior do aliviar na entrada da vontade
                    i = self._receptores_novos.index("vontade")
                    for acoes in self._prior_corpo.values():
                        acoes[AcaoPet.ALIVIAR][i] = _inteiro_exato(cfg_banheiro.w_vontade, cl.escala)
                    self._banheiro = cfg_banheiro
                    self._acoes_com_alvo = ACOES_COM_ALVO_MUNDO + (AcaoPet.ALIVIAR,)
                    self._prior_alvo = {"banheiro": cfg_banheiro.w_banheiro_0, "aqui": cfg_banheiro.w_aqui_0}
                    self._pesos_alvo = dict(self._prior_alvo)
                self._pesos_corpo = {r: {a: list(v) for a, v in acoes.items()} for r, acoes in self._prior_corpo.items()}
                if self.n_pesos() >= cl.maximo_pesos:
                    raise ValueError(f"{self.n_pesos()} pesos, teto {cl.maximo_pesos}")
        # dois pets, etapa 4 (DP-8): o alvo aprendido por classe, so no mundo fisico; um peso por (regra, acao, classe), todos em w0_alvo
        if type(cl.alvo_aprendido) is not bool:
            raise TypeError(f"ConfigLobos.alvo_aprendido precisa ser bool: {cl.alvo_aprendido!r}")
        if type(cl.w0_alvo) is not int or cl.w0_alvo < 0:
            raise ValueError(f"ConfigLobos.w0_alvo precisa ser inteiro >= 0: {cl.w0_alvo!r}")
        if cl.alvo_aprendido:
            if not fisico:
                raise ValueError("ConfigLobos.alvo_aprendido sem o mundo fisico (cfg_mundo ligada)")
            self._cfg_mundo = cfg_mundo
            self._prior_alvo_mundo = {f"{r}:{a.value}": {c: cl.w0_alvo for c in CLASSES_ALVO[a]}
                                      for r, acoes in REGRAS_ALVO.items() if r in self._prior for a in acoes}
            self._pesos_alvo_mundo = {k: dict(t) for k, t in self._prior_alvo_mundo.items()}
            if self.n_pesos() >= cl.maximo_pesos:
                raise ValueError(f"{self.n_pesos()} pesos com o alvo aprendido, teto {cl.maximo_pesos}")
        # dois pets, etapa 4, segunda metade (DP-8): as entradas sociais e o modelo dos outros, so no mundo fisico
        if type(cl.entradas_sociais) is not bool or type(cl.modelo_outros) is not bool:
            raise TypeError("ConfigLobos.entradas_sociais e modelo_outros precisam ser bool")
        if type(cl.janela_social_ticks) is not int or cl.janela_social_ticks <= 0:
            raise ValueError(f"ConfigLobos.janela_social_ticks precisa ser inteiro positivo: {cl.janela_social_ticks!r}")
        if type(cl.fator_familiaridade) is not int or not 0 < cl.fator_familiaridade <= cl.escala:
            raise ValueError(f"ConfigLobos.fator_familiaridade precisa ser inteiro em (0, S]: {cl.fator_familiaridade!r}")
        if cl.entradas_sociais or cl.modelo_outros:
            if not fisico:
                raise ValueError("ConfigLobos.entradas_sociais e modelo_outros sem o mundo fisico (cfg_mundo ligada)")
            from ..mundo import TIPOS_TOQUE
            if tuple(TIPOS_TOQUE) != TIPOS_TOQUE_SOCIAL:
                raise RuntimeError(f"os tipos do toque mudaram: {TIPOS_TOQUE}")
        if cl.entradas_sociais:
            # as linhas: as acoes que o instinto pode propor em cada regra de tempo livre (as de prior nao nulo; com o banheiro, mais o
            # aliviar). Um candidato fora delas falha alto na decisao
            n = len(ENTRADAS_SOCIAIS)
            self._prior_social = {r: {a: [0] * n for a, v in self._prior[r].items() if any(v) or a is AcaoPet.ALIVIAR}
                                  for r in REGRAS_ENTRADAS_CORPO if r in self._prior}
            self._pesos_social = {r: {a: list(v) for a, v in acoes.items()} for r, acoes in self._prior_social.items()}
            if self.n_pesos() >= cl.maximo_pesos:
                raise ValueError(f"{self.n_pesos()} pesos com as entradas sociais, teto {cl.maximo_pesos}")
        if cl.modelo_outros:
            self._modelo = ModeloOutros(cl.escala, cl.fator_familiaridade)

    @property
    def tem_corpo(self) -> bool:
        """O cerebro le o corpo (a chave do corpo ligada)."""
        return self._corpo is not None

    @staticmethod
    def _prior_mundo(cb: ConfigBola, cf: ConfigFrutas) -> dict[str, dict[AcaoPet, dict[str, float]]]:
        """O prior das duas regras do mundo: o do tempo livre (as duas so disparam no lugar dele), brincar com w_bola na entrada
        `bola` e, na das frutas, comer com w_fruta na entrada `fruta`. Mesmos literais do PoliticaInstintoBola/Frutas."""
        if cb.w_bola < 0.0 or cf.w_fruta < 0.0:
            raise ValueError("w_bola e w_fruta negativos: o instinto ignora o termo e o prior nao teria como repetir")
        livre = PRIOR_INSTINTO["tempo_livre"]
        bola = {a: dict(c) for a, c in livre.items()}
        if cb.ligada:
            bola[AcaoPet.BRINCAR]["bola"] = cb.w_bola
        fruta = {a: dict(c) for a, c in bola.items()}
        if cf.ligada:
            fruta[AcaoPet.COMER] = {"fruta": cf.w_fruta}
        return {"bola_no_cenario": bola, "fruta_no_cenario": fruta}

    @staticmethod
    def _tabela_prior(escala: int, regras: tuple = REGRAS, entradas: tuple = ENTRADAS,
                      extra: dict | None = None, acoes_por_regra: dict | None = None) -> dict[str, dict[AcaoPet, list[int]]]:
        """A tabela do prior, regra -> acao -> um inteiro por entrada. Cada regra tem as sete acoes de sempre (ACOES), salvo as de
        `acoes_por_regra` (o banheiro: o aliviar so onde e candidato)."""
        fonte = {**PRIOR_INSTINTO, **(extra or {})}
        tabela = {}
        for regra in regras:
            por_acao = {}
            for a in (acoes_por_regra or {}).get(regra, ACOES):
                coefs = fonte[regra].get(a, {})
                desconhecidas = set(coefs) - set(entradas)
                if desconhecidas:
                    raise ValueError(f"entrada desconhecida no prior: {desconhecidas}")
                por_acao[a] = [_inteiro_exato(coefs.get(e, 0), escala) for e in entradas]
            tabela[regra] = por_acao
        return tabela

    @property
    def ultima_regra(self) -> str | None:
        """Regra do instinto (lobo de impulsos) que decidiu a ultima chamada de agir(). Somente leitura."""
        return self._ultima_regra

    def contribuicoes(self, regra: str, candidatos: tuple[AcaoPet, ...], x: list[float]) -> dict[str, dict[AcaoPet, float]]:
        """Contribuicao de cada lobo ao peso efetivo de cada candidato (o motivo). `piso` so entra no L1."""
        return self._pesos_efetivos(regra, candidatos, x)[0]

    @property
    def ve_mundo(self) -> bool:
        return self._ve_mundo

    @property
    def ve_mundo_fisico(self) -> bool:
        return self._ve_mundo_fisico

    def escolher_alvo(self, acao: AcaoPet, candidatos: list, percepcao, u: int):
        """Gancho do MotorMundo (docs/TAREFA_V2_MUNDO_FISICO.md, secao 5): o alvo de explorar, comer ou brincar. Devolve None, o padrao
        do motor: o cerebro A aprende QUANDO explorar, comer e brincar, nao PARA ONDE (plano do mundo, secao 3; um alvo aprendido entra
        so por adendo, com desenho proprio). Com o mundo, anota os candidatos e o u no motivo da decisao (o `consequencia_mundo` anota
        o alvo que o motor escolheu). So le: nao mexe em peso nem em rng.

        O banheiro (TAREFA_V2_BANHEIRO, secao 4): no `aliviar` o alvo e aprendido. Os candidatos sao um `banheiro` e um `aqui`; o peso
        efetivo de cada um e w / S (com o piso, se aprende), sorteado com u / 2^16 (a conta do instinto do alivio: no prior, o mesmo alvo).
        Na regra urgente, `aqui` (o acidente), sem registro. Com o aprendizado ligado, a escolha entra no registro da decisao e aprende
        pela regra da sub-decisao da fruta, com o sinal da decisao (a consequencia e o carinho, pelo corpo)."""
        if acao is AcaoPet.ALIVIAR:
            return self._alvo_do_alivio(candidatos, u)
        if self._ve_mundo_fisico and self.motivos:
            self.motivos[-1]["mundo"] = {"candidatos": [a.tipo for a in candidatos], "u": u}
        if self._prior_alvo_mundo and self._aprende:
            return self._alvo_aprendido(acao, candidatos, percepcao, u)
        return None

    def _alvo_aprendido(self, acao: AcaoPet, candidatos: list, percepcao, u: int):
        """Dois pets, etapa 4 (docs/futuro/dois_pets.md, secao 8, DP-8): a classe do alvo, aprendida. Cada classe presente tem um
        representante (o primeiro candidato dela, na ordem do motor: a comida boa mais proxima, o primeiro cheiro...). O peso efetivo
        de uma classe e max(0, w) / S, mais 1 se ela e a classe do alvo padrao do motor (`mundo.alvo_padrao_de`, o herdado); o sorteio
        e o de sempre, com u / 2^16. Sem alvo padrao (nada para onde ir), None, como hoje. A escolha entra no registro da decisao e
        aprende so pela consequencia (o credito do consequencia_mundo), pela regra da sub-decisao da fruta. So com o aprendizado
        ligado: o P0 usa o padrao do motor (o instinto do mundo, byte a byte)."""
        from ..mundo import alvo_padrao_de
        if type(u) is not int or not 0 <= u < ESCALA_U_ALVO:
            raise ValueError(f"u do alvo fora de inteiros em [0, 2^16): {u!r}")
        chave = f"{self._ultima_regra}:{acao.value}"
        if chave not in self._pesos_alvo_mundo:
            raise RuntimeError(f"alvo aprendido: {acao.value} na regra {self._ultima_regra!r}, sem tabela de classes")
        if self._registro_decisao is None or self._registro_decisao["acao"] is not acao:
            raise RuntimeError("alvo aprendido sem a decisao registrada")
        padrao = alvo_padrao_de(acao, candidatos, percepcao, self._cfg_mundo)
        if padrao is None:
            if self.motivos:
                self.motivos[-1]["alvo_aprendido"] = {"classes": [], "padrao": None, "alvo": None}
            return None
        podres = {i for i, tipo, *_ in percepcao.vistos if tipo.endswith("_podre")}
        classes, reps = [], []
        for a in candidatos:
            c = ("comida_podre" if a.id in podres else "comida") if a.tipo == "comida" else a.tipo
            if c not in CLASSES_ALVO[acao]:
                raise ValueError(f"alvo aprendido: classe {c!r} fora das de {acao.value} {CLASSES_ALVO[acao]}")
            if c not in classes:
                classes.append(c)
                reps.append(a)
        c_padrao = classes[reps.index(padrao)] if padrao in reps else None
        if c_padrao is None:
            raise RuntimeError(f"alvo aprendido: o padrao {padrao} nao e o representante da classe dele")
        S = self._escala
        tabela = self._pesos_alvo_mundo[chave]
        pesos = [max(0, tabela[c]) / S + (1.0 if c == c_padrao else 0.0) for c in classes]
        k = sortear(pesos, u / ESCALA_U_ALVO)
        total = 0.0
        for p in pesos:
            total = total + p
        self._registro_decisao["alvo_mundo"] = {
            "chave": chave, "candidatos": tuple(classes), "acao": classes[k], "X": {c: S for c in classes},
            "P": {c: arred(p / total * S) for c, p in zip(classes, pesos)},
            "W": {c: max(1, arred(p * S)) for c, p in zip(classes, pesos)}}
        if self.motivos:
            self.motivos[-1]["alvo_aprendido"] = {"classes": list(classes), "padrao": c_padrao, "alvo": classes[k],
                                                  "pesos": dict(zip(classes, pesos))}
        return reps[k]

    def _alvo_do_alivio(self, candidatos: list, u: int):
        if self._banheiro is None:
            raise RuntimeError("alvo do aliviar num cerebro sem o banheiro")
        from ..instinto_banheiro import sortear_alvo, tipos_do_alivio
        tipos = tipos_do_alivio(candidatos)
        if self._ultima_regra == REGRA_ALIVIO_URGENTE:
            k = tipos.index("aqui")
            if self.motivos:
                self.motivos[-1]["alvo_alivio"] = {"candidatos": tipos, "u": u, "alvo": "aqui", "urgente": True}
            return candidatos[k]
        S = self._escala
        if self._aprende:
            pesos = [max(self._pesos_alvo[t], self.cl.piso_peso) / S for t in tipos]
        else:
            pesos = [self._pesos_alvo[t] / S for t in tipos]
        k = sortear_alvo(pesos, u)
        if self.motivos:
            self.motivos[-1]["alvo_alivio"] = {"candidatos": tipos, "u": u, "alvo": tipos[k], "pesos": dict(zip(tipos, pesos)),
                                               "urgente": False}
        if self._aprende:
            if self._registro_decisao is None or self._registro_decisao["acao"] is not AcaoPet.ALIVIAR:
                raise RuntimeError("alvo do aliviar sem a decisao de aliviar registrada")
            total = 0.0
            for p in pesos:
                total = total + p
            self._registro_decisao["alvo"] = {
                "candidatos": tipos, "acao": tipos[k], "X": {t: S for t in tipos},
                "P": {t: arred(p / total * S) for t, p in zip(tipos, pesos)},
                "W": {t: max(1, arred(p * S)) for t, p in zip(tipos, pesos)}}
        return candidatos[k]

    def percepcao(self, obs: Observacao) -> list[float]:
        x = super().percepcao(obs)
        if self._ve_mundo_fisico:
            # MUNDO-CEREBROS: as entradas `bola` e `fruta` vem da percepcao do mundo fisico, pela regra de instinto_mundo.entradas_mundo;
            # os campos de hoje ficam no padrao no mundo (o MotorMundo nao os injeta)
            if obs.bola != 0.0 or obs.fruta != 0.0:
                raise RuntimeError("observacao com a bola ou a fruta do cenario do N4/A1 num cerebro do mundo fisico")
            x.extend(self._entradas_mundo(obs.mundo))
        elif self._ve_mundo:
            x.extend((obs.bola, obs.fruta))
        return x

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        if self._consequencia_pendente is not None:
            raise RuntimeError("E2: o comer com fruta da decisao anterior ficou sem fruta_comida")
        if self._consequencia_mundo_pendente is not None:
            raise RuntimeError("mundo fisico: a decisao anterior ficou sem consequencia_mundo")
        if self._corpo is not None:
            if self._acao_sem_gancho is not None or self._corpo_pendente is not None:
                raise RuntimeError("corpo: a decisao anterior ficou sem o gancho de consequencia")
            if obs.corpo is None:
                raise RuntimeError("corpo: Observacao sem o campo corpo (o cerebro com a chave do corpo precisa do MotorCorpo)")
            S = self._escala
            self._x_corpo = [leitura_receptor(obs.corpo, r, S) / S for r in self._receptores_novos]
        if self._prior_social:
            self._x_social = entradas_sociais(obs.social, self.cl.janela_social_ticks)
        if self._modelo is not None:
            # o modelo dos outros: so le o obs e so registra (nao consome rng, nao entra em peso nenhum)
            self._social_na_decisao = obs.social
            self._modelo.decisao(obs.social, obs.vetor_estado[7])
        x = self.percepcao(obs)
        regra, candidatos = impulsos(self._instinto, obs)
        self._presenca_na_decisao = obs.frutas_cenario
        if self._peso_pedido is not None:
            # N7: o pedido vigente (campo do mundo, chat A); sem o campo na Observacao, nenhum pedido
            self._pedido_na_decisao = tuple(getattr(obs, "pedido_frutas", ()) or ())
        if self._memoria is not None:
            # N6: o relogio do episodio, da hora do dia na percepcao (decisoes a cada 15 ticks: a virada do dia e a hora que volta)
            tdd = int(round(obs.vetor_estado[7] * TICKS_POR_DIA))
            if tdd < self._tick_do_dia_anterior:
                self._dia_relogio += 1
            self._tick_do_dia_anterior = tdd
            self._tick_na_decisao = self._dia_relogio * TICKS_POR_DIA + tdd
            self._humor_na_decisao = obs.vetor_estado[INDICE_HUMOR]
            self._memoria.promover(self._tick_na_decisao)
        contrib, pesos = self._pesos_efetivos(regra, candidatos, x)
        if len(candidatos) == 1:
            u, acao = None, candidatos[0]
        else:
            u = rng.random()
            acao = candidatos[sortear([pesos[a] for a in candidatos], u)]
        self._ultima_regra = regra
        self._fruta_na_decisao = self._ve_frutas and obs.fruta > 0.0
        self._info_na_decisao = obs.info_frutas
        self._registrar(regra, candidatos, acao, x, pesos, contrib, u)
        if self._pesos_corpo:
            S = self._escala
            self.motivos[-1]["percepcao_corpo"] = dict(zip(self._receptores_novos, self._x_corpo))
            if regra in self._pesos_corpo:
                tabela = self._pesos_corpo[regra]
                if self._aprende:
                    if self._banheiro is None:
                        self.motivos[-1]["aprendido_corpo"] = {a.value: termos(tabela[a], self._x_corpo, S) for a in candidatos}
                    else:
                        prior_c = self._prior_corpo[regra]
                        self.motivos[-1]["aprendido_corpo"] = {
                            a.value: termos([w - w0 for w, w0 in zip(tabela[a], prior_c[a])], self._x_corpo, S) for a in candidatos}
                    self._registro_decisao["corpo"] = {"X": [arred(v * S) for v in self._x_corpo]}
        if self._prior_social:
            S = self._escala
            self.motivos[-1]["percepcao_social"] = dict(zip(ENTRADAS_SOCIAIS, self._x_social))
            if regra in self._pesos_social and self._aprende:
                tabela = self._pesos_social[regra]
                self.motivos[-1]["aprendido_social"] = {a.value: termos(tabela[a], self._x_social, S) for a in candidatos}
                self._registro_decisao["social"] = {"X": [arred(v * S) for v in self._x_social]}
        if self._peso_pedido is not None and regra in REGRAS_PEDIDO and AcaoPet.COMER in candidatos:
            p = self._p_pedido()
            if p != 0.0:
                # N7, a sonda de "quem decidiu" (secao 6): a mesma decisao, com o mesmo u e sem o termo do pedido; so le
                _, sem = self._pesos_efetivos(regra, candidatos, x, sem_pedido=True)
                alt = candidatos[sortear([sem[a] for a in candidatos], u)] if u is not None else candidatos[0]
                self.motivos[-1]["pedido"] = {"p": p, "w_pedido": self._peso_pedido, "acao_sem_pedido": alt.value,
                                              "pedido_decidiu": alt is not acao}
                if self._aprende:
                    self._registro_decisao["pedido"] = {"Pd": arred(p * self._escala)}
        if (self._aprende and self._pesos_comer_fruta and regra == REGRAS_MUNDO[1] and AcaoPet.COMER in candidatos):
            # FRUTA-NO-CENARIO: a entrada de cada fruta (presenca x S) para o credito da decisao de comer (so pela consequencia)
            self._registro_decisao["presenca"] = {f: arred(p * self._escala) for f, p in zip(FRUTAS, obs.frutas_cenario)}
        return acao

    def _pesos_das_frutas(self, presentes: list[str], incentivos: dict, memoria: dict | None,
                          sem_info: bool = False) -> tuple[list, dict | None, dict | None]:
        """Os pesos da sub-decisao: ((w_f + m_f) / S) x incentivo_f (m_f = a contribuicao da memoria, N6; o piso no coeficiente so com o
        aprendizado ligado), mais o termo da informacao (N5) e o do pedido (N7), cada um com o piso na fruta em que vale. `sem_info`: o
        termo da informacao zerado (a sonda da K2, `escolha_sem_info`)."""
        S = self._escala
        coef = {}
        for f in presentes:
            w = self._pesos_fruta[f]
            if memoria is not None and memoria[f]["m"] != 0:
                w = w + memoria[f]["m"]
            c = w / S
            if self._aprende and c < self._piso:
                c = self._piso
            coef[f] = c
        pesos = [coef[f] * incentivos[f] for f in presentes]
        info = None
        if self._peso_info is not None and not sem_info:
            # N5: + (w_info / S) x info_f, so nas frutas com informacao vigente (sem ela o peso e o de hoje, byte a byte); a
            # informacao pode levar o peso abaixo de zero, entao a fruta informada tem o piso (com o aprendizado ligado ou nao)
            info = {f: self._info_na_decisao[FRUTAS.index(f)] for f in presentes}
            c_info = self._peso_info / S
            for i, f in enumerate(presentes):
                if info[f] != 0.0:
                    p = pesos[i] + c_info * info[f]
                    pesos[i] = p if p >= self._piso else self._piso
        pedido = None
        if self._peso_pedido is not None and self._pedido_na_decisao:
            # N7: + (w_pedido / S) x pedido_f (pedido_f = -1 na fruta com pedido vigente), na forma da informacao, com o piso
            pedido = {f: self._pedido_na_decisao[FRUTAS.index(f)] for f in presentes}
            c_ped = self._peso_pedido / S
            for i, f in enumerate(presentes):
                if pedido[f] != 0.0:
                    p = pesos[i] + c_ped * pedido[f]
                    pesos[i] = p if p >= self._piso else self._piso
        return pesos, info, pedido

    def _memoria_das_frutas(self, presentes: list[str]) -> dict | None:
        """N6: o episodio recuperado de cada fruta presente (a pista) e a contribuicao m_f = div_arred(ganho x valencia, S); None sem a
        memoria. So le (recuperar nao muda os espacos)."""
        if self._memoria is None:
            return None
        S = self._escala
        memoria = {}
        for f in presentes:
            ep = self._memoria.recuperar(f, self._tick_na_decisao, self.cl.memoria_modo,
                                         self.cl.memoria_janela_recencia_ticks, self._permutacao)
            m = div_arred(self.cl.memoria_ganho * ep["valencia"], S) if ep is not None else 0
            memoria[f] = {"episodio": dict(ep) if ep is not None else None, "m": m}
        return memoria

    def escolha_sem_info(self, presentes: list[str], incentivos: dict, u: float) -> tuple[str | None, bool]:
        """Sonda da K2 (docs/PLANO_CALIBRACAO_CONJUNTA_V2.md, secao 3.4): a escolha da fruta que `escolher_fruta` faria com o mesmo u e o
        termo da informacao zerado, e se alguma fruta presente tem informacao vigente. Chame ANTES de `escolher_fruta` da mesma
        sub-decisao. So le: nao mexe em peso, motivo, registro nem contagem (a vida e o estado interno nao mudam). Sem ver as frutas, ou
        sem o peso da informacao (w0_info 0), (None, False)."""
        if not self._ve_frutas or self._peso_info is None:
            return None, False
        vigente = any(self._info_na_decisao[FRUTAS.index(f)] != 0.0 for f in presentes)
        pesos = self._pesos_das_frutas(presentes, incentivos, self._memoria_das_frutas(presentes), sem_info=True)[0]
        return _sortear_frutas(presentes, pesos, u), vigente

    def escolher_fruta(self, presentes: list[str], incentivos: dict, u: float) -> str | None:
        """Gancho do MotorFrutas: a sub-decisao de comer (qual fruta), pelo lobo de decisao. Peso de cada fruta = (w_f / S) x
        incentivo_f (com o piso no coeficiente, so com o aprendizado ligado), e o sorteio de MotorFrutas._escolher passo a passo,
        com o mesmo u da rng_fruta: no prior (w_f = S) sai a escolha de hoje, byte a byte. Sem ver as frutas devolve None (o
        motor escolhe como sempre). Com o aprendizado ligado a sub-decisao entra no registro da decisao de comer.

        N6: com a memoria ligada, cada fruta presente e uma pista; o episodio recuperado da m_f = div_arred(ganho x valencia, S) no
        coeficiente. A sonda contrafactual (com duas frutas ou mais) refaz a escolha com m_f = 0, os mesmos pesos e o mesmo u, e
        registra se a memoria mudou a fruta; so le."""
        if not self._ve_frutas:
            return None
        S = self._escala
        memoria = self._memoria_das_frutas(presentes)
        pesos, info, pedido = self._pesos_das_frutas(presentes, incentivos, memoria)
        escolhida = _sortear_frutas(presentes, pesos, u)
        sonda = None
        if memoria is not None and len(presentes) >= 2:
            sem = self._pesos_das_frutas(presentes, incentivos, None)[0]
            escolha_sem = _sortear_frutas(presentes, sem, u)
            recuperou = any(v["episodio"] is not None for v in memoria.values())
            sonda = {"escolha_sem_memoria": escolha_sem, "mudou": escolha_sem != escolhida, "recuperou": recuperou}
            self._memoria.sondas["subdecisoes_2mais"] += 1
            self._memoria.sondas["com_recuperacao"] += recuperou
            self._memoria.sondas["mudou"] += escolha_sem != escolhida
        if self.motivos:
            self.motivos[-1]["fruta"] = {"presentes": list(presentes), "pesos": dict(zip(presentes, pesos)), "u": u,
                                         "escolhida": escolhida}
            if info is not None:
                self.motivos[-1]["fruta"]["info"] = dict(info)
            if pedido is not None:
                self.motivos[-1]["fruta"]["pedido"] = dict(pedido)
            if memoria is not None:
                self.motivos[-1]["fruta"]["memoria_emocao"] = {f: dict(v) for f, v in memoria.items()}
                if sonda is not None:
                    self.motivos[-1]["fruta"]["sonda_memoria"] = sonda
        if self._aprende:
            registro = self._registro_decisao
            if registro is None or registro["acao"] is not AcaoPet.COMER or "fruta" in registro:
                raise RuntimeError("sub-decisao da fruta sem uma decisao de comer registrada")
            n = len(presentes)
            total = 0.0
            for p in pesos:
                total += p
            registro["fruta"] = {
                "candidatos": tuple(presentes), "acao": escolhida,
                "X": {f: arred(incentivos[f] * S) for f in presentes},
                "P": {f: (arred(p / total * S) if total > 0.0 else div_arred(S, n)) for f, p in zip(presentes, pesos)},
                "W": {f: max(1, arred(p * S)) for f, p in zip(presentes, pesos)},
            }
            if info is not None:
                registro["fruta"]["I"] = {f: arred(info[f] * S) for f in presentes}
            if pedido is not None and any(v != 0.0 for v in pedido.values()):
                registro["fruta"]["Pd"] = {f: arred(pedido[f] * S) for f in presentes}
        return escolhida


def atualizar_pedido(w: int, w0: int, registro: dict, f_S: int, passo: int, teto: int, S: int) -> tuple[int, int]:
    """N7: a regra da L1 no peso compartilhado do pedido, na decisao de comer (o termo (w/S) x p em comer, Pd = arred(p x S)) e na
    escolha da fruta (a forma de atualizar_info, com Pd_f), somadas e cortadas em w0 +- teto. Devolve (peso novo, cortes)."""
    delta = 0
    ped = registro.get("pedido")
    if ped is not None and AcaoPet.COMER in registro["candidatos"]:
        fator = (S if registro["acao"] is AcaoPet.COMER else 0) - registro["P"][AcaoPet.COMER]
        if fator != 0 and ped["Pd"] != 0:
            delta += div_arred(f_S * passo * ped["Pd"] * fator, S * S * registro["W"][AcaoPet.COMER])
    sub = registro.get("fruta")
    if sub is not None and "Pd" in sub:
        for f in sub["candidatos"]:
            fator = (S if f == sub["acao"] else 0) - sub["P"][f]
            Pd = sub["Pd"][f]
            if fator != 0 and Pd != 0:
                delta += div_arred(f_S * passo * Pd * fator, S * S * sub["W"][f])
    novo = w + delta
    if novo > w0 + teto:
        return w0 + teto, 1
    if novo < w0 - teto:
        return w0 - teto, 1
    return novo, 0


def atualizar_comer_fruta(pesos: dict, prior: dict, registro: dict, f_S: int, passo: int, teto: int, S: int) -> int:
    """FRUTA-NO-CENARIO: a regra da L1 nos pesos de presenca da decisao de COMER (regra fruta_no_cenario). O peso efetivo de comer tem
    o termo (w_f / S) x presenca_f, entao dw_f = arred(f_S * passo * X_f * (S*1[a*=comer] - P_comer) / (S*S*W_comer)), com
    X_f = arred(presenca_f * S), cortado em prior +- teto. Comer uma fruta ruim sozinha (sinal negativo) baixa o peso dela; deixar de
    comer nao mexe (o sinal de nao comer nao fala da fruta). Devolve quantos cortes no teto."""
    fator = (S if registro["acao"] is AcaoPet.COMER else 0) - registro["P"][AcaoPet.COMER]
    cortes = 0
    if fator == 0:
        return 0
    for f, X in registro["presenca"].items():
        if X == 0:
            continue
        delta = div_arred(f_S * passo * X * fator, S * S * registro["W"][AcaoPet.COMER])
        if delta == 0:
            continue
        novo = pesos[f] + delta
        if novo > prior[f] + teto:
            novo, cortes = prior[f] + teto, cortes + 1
        elif novo < prior[f] - teto:
            novo, cortes = prior[f] - teto, cortes + 1
        pesos[f] = novo
    return cortes


def atualizar_info(w: int, w0: int, sub: dict, f_S: int, passo: int, teto: int, S: int) -> tuple[int, int]:
    """N5: a regra da L1 no peso compartilhado da entrada `info` (I_f = arred(info_f * S): +S bem, -S mal, 0 nada). O peso efetivo
    da fruta f tem o termo (w / S) x info_f, entao o gradiente de log p(f*) e a soma, sobre as frutas, de I_f (S*1[f=f*] - P_f) / W_f:
    dw = soma_f arred(f_S * passo * I_f * (S*1[f=f*] - P_f) / (S*S*W_f)), cortado em w0 +- teto. Devolve (peso novo, cortes)."""
    delta = 0
    for f in sub["candidatos"]:
        fator = (S if f == sub["acao"] else 0) - sub["P"][f]
        I = sub["I"][f]
        if fator == 0 or I == 0:
            continue
        delta += div_arred(f_S * passo * I * fator, S * S * sub["W"][f])
    novo = w + delta
    if novo > w0 + teto:
        return w0 + teto, 1
    if novo < w0 - teto:
        return w0 - teto, 1
    return novo, 0


def _inteiro_exato(coef: float, escala: int) -> int:
    """coef * S como inteiro, e so se for exato (o prior tem de devolver o mesmo float que o instinto escreve)."""
    v = coef * escala
    if v != int(v):
        raise ValueError(f"coeficiente {coef!r} nao e multiplo de 1/{escala}: o prior nao repetiria o instinto")
    return int(v)


def deficit_homeostatico(vetor_estado: tuple, drives: tuple, S: int) -> int:
    """D(h) = soma_i (S - arred(h_i * S))**2 sobre os drives (indices em Estado.vetor), ponto de ajuste 1.0. Inteiro."""
    d = 0
    for i in drives:
        h = vetor_estado[i]
        if not 0.0 <= h <= 1.0:
            raise ValueError(f"drive {i} fora de [0, 1]: {h!r}")
        falta = S - arred(h * S)
        d += falta * falta
    return d


def delta_ponderado(antes: tuple, depois: tuple, i: int, S: int, pesos: dict | None) -> int:
    """falta_i(antes)**2 - falta_i(depois)**2 do drive i, com o peso dele na escala S (A2.4): div_arred(w_i * delta, S). Sem `pesos`, ou
    com w_i = S (o peso de hoje), o delta inteiro, sem divisao."""
    delta = deficit_homeostatico(antes, (i,), S) - deficit_homeostatico(depois, (i,), S)
    if pesos is None:
        return delta
    w = pesos[i]
    if type(w) is not int or not 0 <= w <= S:
        raise ValueError(f"peso do drive {i} fora de inteiros em [0, {S}]: {w!r}")
    return delta if w == S else div_arred(w * delta, S)


def _sinal_ponderado(antes: tuple, depois: tuple, drives: tuple, ganho: int, S: int, pesos: dict) -> int:
    """div_arred(ganho * soma_i delta_ponderado_i, S). Com todo peso S, a conta sem pesos (a soma de inteiros e exata)."""
    total = 0
    for i in drives:
        total += delta_ponderado(antes, depois, i, S, pesos)
    return div_arred(ganho * total, S)


def pesos_da_janela(faltas: list[dict], drives: tuple, S: int) -> dict[int, int]:
    """A2.4 (o braco P1-cw): o peso de cada drive pela falta media dele na janela (as faltas das ultimas J decisoes, na escala S, uma
    entrada por decisao): m_d = div_arred(soma, n) (0 com a janela vazia) e w_d = max(div_arred(S, 4), S - div_arred(3 * m_d, 4)). O
    w_d fixo dos drives de hoje e S (peso 1), entao div_arred(S * w_d,janela, S) = w_d,janela."""
    n = len(faltas)
    pesos = {}
    for i in drives:
        m = div_arred(sum(f[i] for f in faltas), n) if n else 0
        pesos[i] = max(div_arred(S, 4), S - div_arred(3 * m, 4))
    return pesos


def faltas_da_observacao(obs: Observacao, drives: tuple, S: int) -> dict[int, int]:
    """A falta de cada drive na escala S, a mesma conta do sinal: S - arred(h * S)."""
    out = {}
    for i in drives:
        h = obs.vetor_estado[i]
        if not 0.0 <= h <= 1.0:
            raise ValueError(f"drive {i} fora de [0, 1]: {h!r}")
        out[i] = S - arred(h * S)
    return out


def sinal_homeostatico(transicao: Transicao, S: int, cfg: ConfigConsequencia | None = None, pesos: dict | None = None) -> int:
    """V2, N3: f_S = div_arred(ganho * (D(antes) - D(depois)), S), com antes/depois = observacao -> observacao_seguinte da
    mesma decisao (janela imediata). Positivo quando a propria acao reduziu o deficit (Keramati e Gutkin,
    10.7554/elife.04811). Inteiro; nada do dono entra. Com `pesos` (A2.4, drive -> w na escala S), cada drive entra com o seu peso
    (delta_ponderado); sem eles, a conta de sempre."""
    cfg = cfg or CONFIG_CONSEQUENCIA
    if type(cfg.ganho) is not int or cfg.ganho < 0:
        raise ValueError(f"ganho precisa ser inteiro >= 0: {cfg.ganho!r}")
    if pesos is not None:
        return _sinal_ponderado(transicao.observacao.vetor_estado, transicao.observacao_seguinte.vetor_estado, tuple(cfg.drives),
                                cfg.ganho, S, pesos)
    antes = deficit_homeostatico(transicao.observacao.vetor_estado, cfg.drives, S)
    depois = deficit_homeostatico(transicao.observacao_seguinte.vetor_estado, cfg.drives, S)
    return div_arred(cfg.ganho * (antes - depois), S)


def sinal_homeostatico_fruta(antes: Observacao, depois: Observacao, S: int, cfg: ConfigConsequencia | None = None,
                             pesos: dict | None = None) -> int:
    """E2 (LOBOS-MUNDO), a variante documentada de `sinal_homeostatico` para quando a acao foi comer uma fruta: antes = a
    observacao da decisao; depois = o estado logo depois de comer (nutricao e efeito no humor ja aplicados); com
    `humor_na_fruta`, o humor (INDICE_HUMOR) entra nos drives. Fruta que faz mal ao humor da sinal negativo por ele. Sem
    `humor_na_fruta`, os drives do N3 (a fruta ainda conta pela fome). Nas outras acoes o sinal e `sinal_homeostatico`."""
    cfg = cfg or CONFIG_CONSEQUENCIA
    if type(cfg.ganho) is not int or cfg.ganho < 0:
        raise ValueError(f"ganho precisa ser inteiro >= 0: {cfg.ganho!r}")
    drives = _drives_fruta(cfg)
    if pesos is not None:
        return _sinal_ponderado(antes.vetor_estado, depois.vetor_estado, drives, cfg.ganho, S, pesos)
    d_antes = deficit_homeostatico(antes.vetor_estado, drives, S)
    d_depois = deficit_homeostatico(depois.vetor_estado, drives, S)
    return div_arred(cfg.ganho * (d_antes - d_depois), S)


def _drives_fruta(cfg: ConfigConsequencia) -> tuple:
    """Os drives da E2: os do N3 e, com `humor_na_fruta`, o humor no fim."""
    drives = tuple(cfg.drives)
    if cfg.humor_na_fruta and INDICE_HUMOR not in drives:
        drives = drives + (INDICE_HUMOR,)
    return drives


def sinal_por_canal(antes: tuple, depois: tuple, drives: tuple, ganho: int, S: int, pesos: dict | None = None) -> dict[str, int]:
    """CANAIS-REFORCO (H-R2, contrato K-6): o escalar div_arred(ganho * (D(antes) - D(depois)), S) separado por canal, um por drive,
    na ordem de `drives`. Delta_i = falta_i(antes)**2 - falta_i(depois)**2 (D e a soma deles). A parte de cada canal sai por
    arredondamento telescopico sobre as somas parciais:
        f_i = div_arred(ganho * (Delta_1 + ... + Delta_i), S) - div_arred(ganho * (Delta_1 + ... + Delta_(i-1)), S)
    entao a soma dos f_i e exatamente div_arred(ganho * soma Delta, S), o escalar, em inteiros (a soma telescopa). Cada f_i difere de
    div_arred(ganho * Delta_i, S) em no maximo 1 (o resto vai ao canal em que a soma parcial cruza o meio). Com `pesos` (A2.4), Delta_i e
    o delta ponderado, e a soma e o escalar ponderado."""
    if type(ganho) is not int or ganho < 0:
        raise ValueError(f"ganho precisa ser inteiro >= 0: {ganho!r}")
    canais: dict[str, int] = {}
    acumulado, anterior = 0, 0
    for i in drives:
        if i not in CANAL_DO_DRIVE:
            raise ValueError(f"drive {i} sem canal (CANAL_DO_DRIVE)")
        acumulado += delta_ponderado(antes, depois, i, S, pesos)
        parcial = div_arred(ganho * acumulado, S)
        canais[CANAL_DO_DRIVE[i]] = parcial - anterior
        anterior = parcial
    return canais


def sinal_homeostatico_canais(transicao: Transicao, S: int, cfg: ConfigConsequencia | None = None,
                              pesos: dict | None = None) -> dict[str, int]:
    """`sinal_homeostatico` separado por canal (sinal_por_canal): a soma dos canais e o escalar."""
    cfg = cfg or CONFIG_CONSEQUENCIA
    return sinal_por_canal(transicao.observacao.vetor_estado, transicao.observacao_seguinte.vetor_estado, tuple(cfg.drives),
                           cfg.ganho, S, pesos)


def sinal_homeostatico_fruta_canais(antes: Observacao, depois: Observacao, S: int,
                                    cfg: ConfigConsequencia | None = None, pesos: dict | None = None) -> dict[str, int]:
    """`sinal_homeostatico_fruta` separado por canal (sinal_por_canal, os drives da E2): a soma dos canais e o escalar."""
    cfg = cfg or CONFIG_CONSEQUENCIA
    return sinal_por_canal(antes.vetor_estado, depois.vetor_estado, _drives_fruta(cfg), cfg.ganho, S, pesos)


# ------------------------------------------------------------------ CORPO (etapa 5): o sinal pelos receptores


def receptores_novos(cc: ConfigCorpo, mundo_fisico: bool) -> tuple[str, ...]:
    """Os receptores novos que o corpo tem com estas chaves (secao 10), na ordem de RECEPTORES_NOVOS: tedio, solidao e estresse com
    `drives_novos`, a curiosidade so com o mundo fisico tambem (CD-8), dor e susto com `gestos`, a vontade e o conforto com o
    `banheiro`. Sem eles, nenhum."""
    tem = set()
    if cc.drives_novos:
        tem |= {"tedio", "solidao", "estresse"} | ({"curiosidade"} if mundo_fisico else set())
    if cc.gestos:
        tem |= {"dor", "susto"}
    if cc.banheiro:
        tem |= {"vontade", "conforto"}
    return tuple(r for r in RECEPTORES_NOVOS if r in tem)


def leitura_receptor(pc, nome: str, S: int) -> int:
    """A leitura do receptor `nome` da PercepcaoCorpo (inteiro em [0, S]); um receptor que nao existe (None) ou fora da escala falha
    alto."""
    v = getattr(pc, nome)
    if v is None:
        raise RuntimeError(f"corpo: o receptor {nome!r} nao existe nesta Observacao.corpo")
    if type(v) is not int or not 0 <= v <= S:
        raise ValueError(f"corpo: receptor {nome!r} fora de inteiros em [0, {S}]: {v!r}")
    return v


def falta_receptor(pc, nome: str, S: int) -> int:
    """A falta na escala S: S - leitura nos drives de hoje (o receptor le o drive), a propria leitura nos novos (o receptor le a falta,
    ou a concentracao na dor, no susto e na vontade), e S - leitura no conforto (BN-6: o receptor le o conforto; a falta e a de
    conforto)."""
    v = leitura_receptor(pc, nome, S)
    if nome in RECEPTORES_HOJE or nome in RECEPTORES_FALTA_INVERTIDA:
        return S - v
    if nome in RECEPTORES_NOVOS:
        return v
    raise KeyError(f"receptor desconhecido: {nome!r}")


def faltas_corpo(pc, drives: tuple, S: int) -> dict[str, int]:
    """A falta de cada drive (pelo nome do receptor), na escala S: a janela da A2.4 com o corpo."""
    return {d: falta_receptor(pc, d, S) for d in drives}


def contribuicoes_corpo(antes, depois, drives: tuple, S: int, pesos_drives: dict | None = None,
                        pesos_janela: dict | None = None) -> dict[str, int]:
    """c_d = w_d * delta_d por drive, delta_d = falta_d(antes)**2 - falta_d(depois)**2 sobre os receptores (secao 9). Com `pesos_janela`
    (A2.4, na escala S), delta_d e ponderado como em `delta_ponderado`: div_arred(w * delta, S) quando w != S. `pesos_drives` sao os
    inteiros w_d (ConfigConsequencia.pesos_drives_corpo); sem eles, todos 1. Um drive sem peso falha alto."""
    c = {}
    for d in drives:
        fa, fd = falta_receptor(antes, d, S), falta_receptor(depois, d, S)
        delta = fa * fa - fd * fd
        if pesos_janela is not None:
            w = pesos_janela[d]
            if type(w) is not int or not 0 <= w <= S:
                raise ValueError(f"peso da janela do drive {d!r} fora de inteiros em [0, {S}]: {w!r}")
            if w != S:
                delta = div_arred(w * delta, S)
        wd = 1 if pesos_drives is None else pesos_drives[d]
        if type(wd) is not int or wd < 0:
            raise ValueError(f"w_d do drive {d!r} precisa ser inteiro >= 0: {wd!r}")
        c[d] = wd * delta
    return c


def sinal_corpo(antes, depois, drives: tuple, ganho: int, S: int, pesos_drives: dict | None = None,
                pesos_janela: dict | None = None) -> int:
    """V2, corpo (secao 9): f_S = div_arred(ganho * (D(antes) - D(depois)), S), com D = soma_d w_d * falta_d**2 sobre os receptores
    (`antes` e `depois` sao PercepcaoCorpo). Com os drives de hoje e w_d = 1, o numero do N3 (`sinal_homeostatico`) sobre o mesmo
    estado: o receptor e S - div_arred(q * S, C), e S - arred(h * S) do drive lido da o mesmo inteiro. Inteiro."""
    if type(ganho) is not int or ganho < 0:
        raise ValueError(f"ganho precisa ser inteiro >= 0: {ganho!r}")
    total = 0
    for c in contribuicoes_corpo(antes, depois, drives, S, pesos_drives, pesos_janela).values():
        total += c
    return div_arred(ganho * total, S)


def sinal_corpo_canais(antes, depois, drives: tuple, ganho: int, S: int, pesos_drives: dict | None = None,
                       pesos_janela: dict | None = None) -> dict[str, int]:
    """`sinal_corpo` separado por canal, um por drive, na ordem de `drives`, com a soma telescopica de `sinal_por_canal`: a soma dos
    canais e exatamente o escalar (contrato K-6)."""
    if type(ganho) is not int or ganho < 0:
        raise ValueError(f"ganho precisa ser inteiro >= 0: {ganho!r}")
    canais: dict[str, int] = {}
    acumulado, anterior = 0, 0
    for d, c in contribuicoes_corpo(antes, depois, drives, S, pesos_drives, pesos_janela).items():
        if d not in ROTA_CANAIS and d not in ROTA_CANAIS_CORPO:
            raise ValueError(f"drive {d!r} sem canal")
        acumulado += c
        parcial = div_arred(ganho * acumulado, S)
        canais[d] = parcial - anterior
        anterior = parcial
    return canais


def validar_parametros_consequencia(cfg: ConfigConsequencia | None = None) -> None:
    campos = {f.name for f in fields(cfg or CONFIG_CONSEQUENCIA)}
    if campos != set(PARAMETROS_CONSEQUENCIA_N3):
        raise ValueError(f"sem registro: {sorted(campos - set(PARAMETROS_CONSEQUENCIA_N3))}; "
                         f"registro sem campo: {sorted(set(PARAMETROS_CONSEQUENCIA_N3) - campos)}")


def validar_parametros_lobos(cfg: ConfigLobos | None = None) -> None:
    """Todo campo da ConfigLobos tem status registrado; nenhum campo registrado sem existir."""
    campos = {f.name for f in fields(cfg or CONFIG_LOBOS)}
    if campos != set(PARAMETROS_LOBOS):
        raise ValueError(f"sem registro: {sorted(campos - set(PARAMETROS_LOBOS))}; "
                         f"registro sem campo: {sorted(set(PARAMETROS_LOBOS) - campos)}")
    for nome, (status, fonte) in PARAMETROS_LOBOS.items():
        if status not in ("PROPOSTO", "DECIDIDO") or not fonte:
            raise ValueError(f"{nome}: status {status!r} ou fonte vazia")
