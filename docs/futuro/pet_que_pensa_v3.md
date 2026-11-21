# O pet que pensa na V3: um modelo do próprio corpo no tempo, para quebrar o laço da fome e do sono

Status (2026-11-21): **PROPOSTO.** É só desenho: nenhum código, nenhuma vida e nenhuma triagem. A triagem só roda depois que o Matheus
aprovar este desenho, e uma run de 200 só depois da triagem, de um plano de análise na `main` e da seção `PR-<id>` no
`docs/PREREGISTRO.md`. As decisões abertas estão na seção 9, PQV-1 a PQV-12.

**A origem:** o Matheus decidiu em 2026-11-21: "vamos partir para o 'pet que pensa'". É a opção D3 do parecer da Gerência (vault,
`10 Auditoria/Vale continuar o cérebro 2026-11-21.md`). O pedido dele vem de 2026-10-07: o pet que prevê as consequências ("se eu fizer
X, acontece Y") e planeja, e não instinto com reforço por cima.

**O levantamento que sustenta este desenho** está no vault: `10 Auditoria/Levantamento do pet que pensa 2026-11-21.md`. Ele cobre o
que a V2 fez (o J5), onde o modular decide hoje e por que os resultados da V3 dizem que o corpo decide.

**Regras deste documento:**
- os números novos são PROPOSTOS e SEM FONTE, salvo onde a fonte está ao lado;
- as referências vêm só das tabelas verificadas (`docs/referencias/*_verificadas.csv`), com o grau de leitura registrado lá;
- **nenhuma alegação de novidade** (seção 8).

## 0. Em uma tabela

| | o J5 da V2 | este desenho |
|---|---|---|
| o cérebro | o A (o lobo `planejamento`), que saiu | o modular: um módulo novo, o M-PLANO |
| o que o pet prevê | o que uma fruta faz no corpo, e o que cai em cada árvore | **o próprio corpo no tempo:** cada receptor, por um horizonte que cobre um sono |
| a escolha que ele muda | a árvore aonde ir | **dormir agora ou comer antes,** e o resto do que o pet faz acordado |
| o horizonte | até chegar ao alvo | um plano de até 2 opções, até 8 h (32 decisões) |
| a medida | a revalorização (T1) e a busca (T2) | o "Tempo bem", mais as sondas e os controles do mecanismo (seção 5) |

## 1. O ponto de partida

O levantamento resume três fatos (todos FATO VERIFICADO nos documentos de resultado citados lá):

1. **O planejador do J5 funcionou no que mediu, e morreu com o cérebro A.**
   - O G-T1 passou com 0,197 [0,075; 0,323] (#370), e o G-T2 saiu inconclusivo por premissa
     (`v2-final:docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md`).
   - O modular herdou só a parte de horizonte zero: o P1 do M-PLAST (o desfecho por classe de comida) e o incentivo pelo
     `valor_previsto` (`digilab/digibrain/plast.py`, `base.py:88`). Esse incentivo entra só no comer e no brincar com objeto.
2. **Quem decide é o corpo, antes do sorteio.**
   - O reflexo do sono escolhe dormir sem sorteio, com a energia abaixo de `lambda_sono` (`arb.py`).
   - De 46 % a 62 % do tempo de sono está em episódios que o reflexo começou, e a parte aprendida do dormir é zero
     (`docs/RESULTADO_V3_PET_VIVO_SONO.md`).
   - Fora do sono, as ações acordadas quase não se distinguem (η² ≤ 0,037, `docs/RESULTADO_V3_PET_VIVO_RA.md`).
3. **O "Tempo bem" se perde num laço míope** (`docs/SINTESE_CORPO.md`, seção 1):
   1. o jejum sobe a fome e, pela ponte, o cansaço;
   2. o reflexo põe o pet com fome para dormir;
   3. dormindo ele não come, e acorda pior.
   - **O que já se tentou:** o DTB, um conserto no corpo, subiu o "Tempo bem" em +0,062. Tirar o reflexo sem nada no lugar (o D + C5)
     quase dobrou a exaustão (0,232 → 0,435).

**A hipótese deste desenho (HIPÓTESE, não testada):**
- dormir com fome é a escolha certa para o próximo quarto de hora e a errada para as próximas oito;
- um pet que prevê o próprio corpo por um horizonte que cubra um sono pode preferir "comer, depois dormir";
- nenhuma calibração do crédito alcança essa escolha, porque o reflexo a faz antes do sorteio.

## 2. O que o pet preveria, e por qual horizonte

### 2.1 O modelo do corpo no tempo (o MC)

O pet aprende, só do que percebe (os receptores da `PercepcaoCorpo` e a própria posição, como no J5; sem o químico, o `Estado`, as
constantes do `corpo.py` nem o registro):

| peça | o que é | tamanho | de onde vem |
|---|---|---|---|
| **as taxas por modo** τ[m, r] | quanto o receptor r muda por tick no modo m: `acordado` (parado ou com uma ação sem andar), `andando`, `dormindo` | 3 modos × R receptores | **nova:** a média móvel inteira da mudança entre duas decisões seguidas no mesmo modo, dividida pelos ticks |
| **o desfecho por classe** d[c, r] | quanto o receptor muda ao consumir a classe c | já existe | **o P1 do M-PLAST,** sem mudança |
| **o custo de andar** | o andar previsto por subunidade | já existe | o P1 (o `andar`) |
| **o fim do sono** E_acordar | a leitura da energia em que o pet costuma acordar | 1 inteiro | **nova:** a média móvel da energia percebida na primeira decisão acordada depois de um sono |

- **O tamanho:** com R = 13 receptores, são 3 × 13 + 1 = 40 inteiros novos, ao lado dos do P1. Ficam num estado próprio, fora dos pesos
  da decisão, como os modelos do J5 (a PQ-6 da V2).
- **O passo:** S/8 nas taxas e S/16 no E_acordar (PROPOSTO, SEM FONTE). O prior é 0 (o pet nasce sem saber), como no J5.
- **Por que taxas, e não um modelo de transição completo:** o corpo de hoje é quase linear por modo entre os eventos (a fome sobe pelo
  relógio dela, a energia cai acordado e sobe dormindo). Isso é leitura do `corpo.py`, não medida. Taxas por modo cabem em inteiros, são
  legíveis ("quando eu durmo, a fome sobe x por hora") e custam pouco (seção 6). Um modelo de estado inteiro (Dyna) fica como
  alternativa na PQV-2.

**A conferência que o MC precisa passar antes de valer** (o G-PREV, seção 5.3): no fim de cada opção, a leitura prevista da fome e da
energia tem de errar menos do que a previsão "nada muda".

### 2.2 Os planos e o horizonte

Em cada decisão, fora do reflexo duro (seção 3.2), o M-PLANO monta poucos planos curtos, de até duas opções:

| plano | opção 1 | opção 2 (a continuação) |
|---|---|---|
| **dormir agora** | dormir até E_acordar | o que fica: acordado parado até o fim do horizonte |
| **comer k, depois dormir** | andar até k e comer (d[c] da classe de k) | dormir até E_acordar |
| **comer k, depois seguir** | andar até k e comer | acordado parado |
| **seguir** (a linha de base) | acordado parado | — |

- **Os k** são as comidas vistas e o comedouro lembrado (os alvos que o M-IMPULSO já monta). No máximo `k_max` = 4 alvos, os mais perto
  (PROPOSTO).
- **A trajetória prevista:**
  1. em cada opção, a leitura de cada receptor anda pela taxa do modo vezes os ticks;
  2. o consumo soma o d[c] de uma vez, cortado em [0, S];
  3. a duração do andar sai da distância pelo custo de andar, e a do sono, da energia até o E_acordar pela taxa de dormir.
- **O horizonte:** H = 480 ticks (8 h, 32 decisões), cortado onde acabar. Cobre um sono e a refeição de depois (PROPOSTO, SEM FONTE). A
  duração média de um sono no v38 não está medida neste documento; a fumaça a mede antes da triagem e confere se as 8 h cobrem o sono
  típico.
- **Nada de busca em árvore:** o número de planos é fixo, no máximo 2 + 2 × `k_max` = 10.

### 2.3 O valor de um plano

`J(plano) = − Σ_{c = 1..8} D(leitura prevista no checkpoint c)`, com os 8 checkpoints a cada 60 ticks e `D = Σ_d w_d · falta_d²`, a mesma
falta do `sinal_corpo` (`base.py:100`).
- É o drive homeostático de Keramati e Gutkin (2014), integrado no tempo (seção 8).
- O pet não conhece os limiares da privação nem da exaustão. Eles são do corpo, e o "Tempo bem" os usa para medir, não para decidir
  (PQV-4).
- Uma falta grande pesa mais que a soma de duas pequenas, pelo quadrado. É o que faz "acordar faminto" custar mais que "ficar cansado mais
  um pouco".

## 3. Como a previsão entra na decisão

### 3.1 O termo do plano

Para cada unidade u do M-IMPULSO que começa algum plano (dormir, comer k, ocioso):

`plano[u] = clamp(div_arred(g_plano · (J(melhor plano que começa por u) − J(seguir)), S_J), −P_max, P_max)`

- **Ele entra na ativação como mais um termo,** guardado à parte como os outros (inato, incentivo, hábito, memória...). As unidades sem
  plano (brincar, chamar, emburrar, explorar) ficam com 0.
- **`g_plano` = 0 é o cérebro de hoje, bit a bit** (o G2, como no J5). Esse é o primeiro teste do código.
- **S_J** (a escala do J) e **P_max** (o teto do termo) são PROPOSTOS e saem da fumaça, sem olhar o "Tempo bem": a regra é o termo
  ficar na mesma ordem do inato do dormir nas decisões com conflito.
- **A sonda nova `sem_plano`:** o mesmo u, sem o termo. Se a escolha muda, o plano decidiu (o `plano_decidiu`). Mesma rng, nenhuma
  chamada nova.

### 3.2 O reflexo do sono: o ponto que decide se o desenho serve

Com o reflexo duro de hoje, o termo do plano nunca chega à decisão em que o laço se fecha: com a energia abaixo de `lambda_sono`, o pet
dorme sem sorteio. Três opções (PQV-5):

| opção | o reflexo | o que o plano alcança | o risco |
|---|---|---|---|
| **R-a, como hoje** | duro abaixo de `lambda_sono` | só o adormecer pelo sorteio | o plano quase não decide nada (a lição do R-sono) |
| **R-b, uma faixa do plano** (recomendada) | duro só abaixo de um piso menor, `lambda_colapso` = S/8; entre ele e o `lambda_sono`, o dormir ganha o peso do reflexo suave (C5) e o plano compete | a decisão de dormir com fome, na faixa onde o laço se fecha | o D + C5 quase dobrou a exaustão; o piso e o controle SUAVE (seção 5) existem por isso |
| **R-c, sem reflexo** | nenhum | tudo | o pet pode morrer de exaustão por um modelo errado; nenhum piso do corpo |

- **O "sono que segura" (v38) não muda:** o pet que dorme continua até `lambda_acordar`, salvo a fome urgente. O plano age no adormecer
  e na faixa.
- **O piso fica no cérebro, não no corpo:** é o mesmo reflexo, só com o limiar mais baixo. O corpo não muda (seção 4).

### 3.3 O motivo e a fala

- **O motivo ganha o fator `plano`** quando a sonda `sem_plano` muda a escolha, com o plano vencedor e as duas leituras previstas
  ("comi antes de dormir: previ acordar com a fome x").
- **O texto só nomeia o que o modelo tem,** como no J5.
- **O rótulo "pensa" na tela só vale depois da confirmatória** (a R-7 da V2, herdada; PQV-11).

## 4. O que fica no corpo

**Tudo.** Nenhuma linha do `digilab/corpo.py` nem do `web/app/motor/corpo.ts` muda:
- o metabolismo, a ponte da falta de combustível (com ou sem o DTB, PQV-6) e a digestão;
- o dano da privação e os limiares dela;
- os receptores e a escala S.

O pet não lê nada disso: aprende as taxas pela leitura dos receptores. Os testes do código conferem isso (o G-SEM-ACESSO): o M-PLANO
importa só a `config`, os `events`, o `_comum` e o `base` do pacote, como os modelos do J5.

O piso do reflexo e o termo do plano ficam no cérebro. É essa separação que deixa medir "o pet aprendeu a cuidar de si" contra "o corpo
foi consertado" (o DTB).

## 5. Como medir se o pet planeja, e não só segue o reflexo

### 5.1 Os braços

Todos no mesmo pet base (PQV-6), com os mesmos donos, lugares e sementes. Muda só o cérebro:

| braço | o reflexo | o termo do plano | o que separa |
|---|---|---|---|
| **HOJE** | duro (R-a) | 0 | o pet do jogo de hoje |
| **SUAVE** | a faixa (R-b), sem plano | 0 | **o controle que importa:** só afrouxar o reflexo. Separa "planeja" de "dorme menos porque o reflexo afrouxou" |
| **PLAN** | a faixa (R-b) | `g_plano` > 0 | o pet que pensa |
| **PLAN-EMBAR** | a faixa (R-b) | `g_plano` > 0, com o MC embaralhado | separa "a previsão certa decide" de "um termo a mais muda o sorteio" |

- **No PLAN-EMBAR,** o MC aprende igual, mas o plano lê as taxas com os receptores permutados (uma permutação fixa por vida, da semente).
  A magnitude do termo é a mesma, e o conteúdo, errado.
- **Na confirmatória, um quinto braço, o PLAN-CONG:** o MC congelado no fim do dia 1. Separa "aprender o modelo" de "ter um modelo". Fica
  fora da triagem pelo custo.

### 5.2 A medida primária e o que conta como "planeja"

- **A primária:** o "Tempo bem" (dias 1 a 14), a fração das decisões sem privação e sem exaustão (`docs/PLANO_ANALISE_V3_CORPO_C4.md`).
- **O pet "planeja" só se as três coisas saírem juntas:**
  1. **PLAN − HOJE > 0:** o pet fica melhor;
  2. **PLAN − SUAVE > 0:** o ganho não é só o reflexo afrouxado;
  3. **PLAN − PLAN-EMBAR > 0:** o ganho vem da previsão certa.
- Se só a 1 sair, o resultado é "o reflexo suave ajudou", não "o pet pensa".

### 5.3 O mecanismo (descritivo na triagem; gate na confirmatória)

| medida | o que é | o que o PLAN deveria mostrar |
|---|---|---|
| `plano_decidiu` | a fração das decisões em que a sonda `sem_plano` muda a escolha | longe de 0 (no R-sono, a parte aprendida do dormir era 0) |
| a antecipação | P(comer \| fome acima da metade e energia na faixa) | sobe contra o HOJE e o SUAVE |
| o sono com fome | a fração dos episódios de sono que começam com a fome urgente | cai |
| o G-PREV | o erro absoluto da fome e da energia previstas no fim de cada opção, contra a previsão "nada muda" | menor, a partir do dia 2 |
| as guardas | a saúde, a exaustão e o forrageio, como na C4 | nenhuma piora além do δ da C4 |

### 5.4 O teste sem reexperiência (só na confirmatória, PQV-9)

A DS-1 da V2 pede uma mudança no mundo que o pet aprenda sem reexperimentar a consequência na escolha. A versão pelo corpo:
- **do dia 8 em diante,** a ração do comedouro passa a matar menos fome;
- **o dono dá uma ração na mão, fora do comedouro** (como o T1 da V2);
- **o teste:** o pet com o MC muda o "comer antes de dormir" na primeira noite seguinte; o hábito não muda.

Fica fora da triagem: ela pede mudança no motor e premissas de oportunidade, que derrubaram a primeira validação do J5.

### 5.5 A triagem (só depois da aprovação deste desenho)

- **As vidas:** 20 unidades × 12 células (4 donos × 3 lugares) × 4 braços = 960 vidas de 14 dias, sem pré-registro (a regra da triagem
  de 2026-11-21).
- **O corte proposto (ainda não decidido, PQV-8):** |PLAN − HOJE| > 2δ no "Tempo bem", com δ = 0,032 da C4, isto é, 0,064. Além disso,
  PLAN − SUAVE e PLAN − PLAN-EMBAR com o sinal certo.
  - **Um aviso sobre o corte:** o DTB, o único ganho replicado do projeto, deu +0,062. Ele não passaria por 2δ.
- **As sementes:** uma faixa nova, pedida à coordenadora depois da aprovação. As 106xxx a 109xxx estão tomadas.
- **A fumaça antes da triagem:** 2 vidas por braço, para conferir o G2, o custo por vida e a duração do sono, e para fixar S_J e P_max
  sem olhar o "Tempo bem".

## 6. Custo de máquina

**A referência:** a run da recompensa levou 2 h 45 para 9 600 vidas de 14 dias com 4 processos
(`docs/RESULTADO_V3_PET_VIVO_RECOMPENSA.md`, seção 2). Dá perto de 4 s de processo por vida (a conta é nossa).

**O M-PLANO por decisão (estimativa, SEM MEDIDA):**
- até 10 planos × 8 checkpoints × 13 receptores, perto de 1 000 operações inteiras, mais as 10 somas do D;
- nenhuma simulação tick a tick: a trajetória é a taxa vezes os ticks;
- são 1 344 decisões por vida.
- **HIPÓTESE:** de +25 % a +100 % por vida em Python. A fumaça mede.

| etapa | vidas | parede, com 4 processos (estimativa) |
|---|---|---|
| fumaça | 8 | minutos |
| **triagem** | 960 | **de 20 a 35 min** |
| confirmatória, 5 braços × 12 células × 200 | 12 000 | de 4 a 7 h: **grande demais; o plano dela deveria cortar braços ou células** |

- **A regra da máquina vale:** no máximo 4 processos, uma run de pesquisa por vez, e o `tools/pre_run.py` como porta.
- **Na web,** 1 000 operações inteiras por decisão, a cada 15 ticks, custam microssegundos. O custo de lá é o porte e a paridade, não a CPU.

## 7. O que é Python e o que um dia iria para a web

| | Python (onde a pesquisa acontece) | web (só depois da confirmatória) |
|---|---|---|
| o M-PLANO | `digilab/digibrain/plano.py`, desligado por padrão, com a subchave `plano` na `ConfigDigibrain` | `web/app/motor/digibrain/plano.ts`, com a paridade por gabarito (`tests/gabaritos/*_python.json`) |
| o piso do reflexo (R-b) | na `Arbitragem`, ao lado do reflexo suave que já existe | idem, no `arb.ts` |
| as sondas e os braços | o `sem_plano`, o SUAVE, o EMBAR e o CONG, só de pesquisa | só o `sem_plano`, para o motivo |
| o motivo e a fala | o fator `plano` no registro | a frase no balão, sem o rótulo "pensa" até a R-7 |
| o pet do jogo | nenhum ovo muda | uma versão nova do pet, só para os ovos novos, como a V1 do corpo |

**As etapas propostas,** cada uma um PR e cada uma esperando a anterior:

| etapa | o quê | roda vida? |
|---|---|---|
| **PQV-0** | este desenho | não |
| **PQV-1c** | o código Python, desligado: o MC, os planos, o termo, a sonda, o piso; testes do G2 (`g_plano` = 0 igual a hoje bit a bit), do G-INT, do G-SEM-ACESSO e do replay | só os testes |
| **PQV-2t** | a fumaça e a triagem (seção 5.5) | 968 vidas, depois do ok do Matheus |
| **PQV-3** | se a triagem passar: o plano de análise, a seção `PR-<id>` e a run de 200 | sim, com plano na `main` |
| **PQV-4w** | se confirmar: o porte à web e a versão nova do pet | não |

Os orquestradores do J5 (`pet_que_pensa*`, `pqp_*`) e o lobo `planejamento` saem na limpeza (LZ2 e LZ4). Este desenho não os reaproveita:
parte do P1 do modular, que fica.

## 8. A literatura, e o que não é novo

Só referências das tabelas verificadas, no grau de leitura registrado lá:
- **Keramati e Gutkin (2014),** eLife, `10.7554/eLife.04811`, resumo e texto completo (`docs/referencias/v3c5_referencias_verificadas.csv`):
  a recompensa como redução do drive homeostático, a equivalência entre buscar recompensa e buscar estabilidade, e a resposta
  antecipatória. É a forma do J (seção 2.3).
- **Sterling (2012),** Physiol. Behav., `10.1016/j.physbeh.2011.06.004`, resumo: a regulação eficiente antecipa as necessidades (a
  alostase).
- **Tschantz et al. (2022),** Biol. Psychol., `10.1016/j.biopsycho.2022.108266`, resumo: o controle interoceptivo homeostático, o alostático
  e o dirigido a meta como modelos generativos distintos. **É o precedente mais próximo:** prever o próprio corpo para agir antes da
  falta.
- **Daw, Niv e Dayan (2005),** Nat. Neurosci., `10.1038/nn1560`, resumo: o controle com modelo e o hábito, arbitrados pela incerteza. Fica
  como passo seguinte; aqui o termo do plano só soma.
- **Adams e Dickinson (1981),** `10.1080/14640748108400816`, resumo: a forma do teste sem reexperiência (seção 5.4).
- **Akam, Costa e Dayan (2015),** PLoS Comput Biol, `10.1371/journal.pcbi.1004648`, resumo: por que não a tarefa de dois passos.
- **Sutton (1990), Dyna,** `10.1016/b978-1-55860-141-3.50030-4`, e **Schrittwieser et al. (2020), MuZero,** `10.1038/s41586-020-03051-4`,
  só o título: planejar com um modelo aprendido já existe.

**Nenhuma alegação de novidade.**
- O mecanismo é a alostase com um modelo aprendido, que a literatura acima já descreve.
- O que este desenho pode ter de próprio é a medida com os controles no mesmo pet: o SUAVE, o EMBAR e o CONG.
- **Não foi feita busca nova** de pets virtuais ou agentes de jogo que planejam pelo corpo. A falta de um precedente direto não foi
  conferida.

## 9. As decisões abertas

| # | a decisão | a recomendação | as outras opções | o custo de errar |
|---|---|---|---|---|
| **PQV-1** | o que o planejador mira | **o laço da fome e do sono, pelo modelo do próprio corpo** | (b) a busca da comida, o T2 da V2 (o mapa); (c) as duas | errar para (b) repete uma pergunta que não mexe no "Tempo bem", pois o corpo decide fora dela; errar para (a) custa só adiar o T2, que já está adiado |
| **PQV-2** | a forma do modelo | **as taxas por modo + o P1 + o E_acordar (40 inteiros novos)** | (b) um modelo de transição do estado inteiro, à Dyna; (c) uma rede pequena | (b) e (c) custam muito mais em inteiros, na paridade e na legibilidade; se o corpo não for quase linear por modo, o G-PREV falha na fumaça e se troca, com o custo de uma fumaça |
| **PQV-3** | o horizonte | **até 2 opções e 8 h (32 decisões)** | (b) 1 opção, como o J5; (c) 3 opções ou 16 h | (b) não vê o despertar com fome, e o desenho perde o sentido; (c) multiplica os planos e o custo por pouco a mais. A fumaça confere se as 8 h cobrem o sono típico |
| **PQV-4** | o valor de um plano | **a soma do D (Σ falta²) prevista em 8 checkpoints** | (b) o "Tempo bem" previsto, com os limiares | (b) põe no cérebro os limiares que o corpo usa para medir: o pet otimizaria a métrica, não o bem-estar, e o pet não percebe esses limiares |
| **PQV-5** | o reflexo do sono | **R-b, a faixa do plano, com o piso `lambda_colapso` = S/8** | (a) o reflexo duro de hoje; (c) sem reflexo | com (a), o plano não alcança o laço, e o resultado já é previsível pelo R-sono; com (c), um modelo errado mata o pet de exaustão; o custo de (b) é o D + C5, e o braço SUAVE o mede |
| **PQV-6** | o pet base | **o v38 do jogo, sem o DTB** | (b) o v38 com o DTB; (c) o pet da bancada | com (b), o DTB já quebra parte do laço e o plano tem menos o que mostrar, e o DTB ainda não está no jogo (V1-a pendente); com (c), a resposta não vale para o pet do jogo, o erro da C4 |
| **PQV-7** | os braços da triagem | **HOJE, SUAVE, PLAN e PLAN-EMBAR** | (b) só HOJE e PLAN; (c) os cinco, com o CONG | com (b), um ganho não diz se é o plano ou o reflexo afrouxado, e a triagem teria de se repetir; com (c), mais 240 vidas por uma pergunta (aprender contra ter) que só vale se houver ganho |
| **PQV-8** | o corte da triagem | **|PLAN − HOJE| > 2δ = 0,064 no "Tempo bem", e PLAN − SUAVE e PLAN − EMBAR com o sinal certo** | (b) só o 2δ; (c) 1δ = 0,032 | o 2δ ainda não foi decidido (a regra de 2026-11-21). Ele recusaria o DTB (+0,062): pode descartar um ganho real; o 1δ leva à confirmatória mais coisas que não confirmam |
| **PQV-9** | o teste sem reexperiência (seção 5.4) | **só na confirmatória, se a triagem passar** | (b) já na triagem; (c) nunca | (b) pede mudança no motor antes de saber se vale; (c) deixa o "pensa" sem a medida da DS-1, e a R-7 não se cumpre |
| **PQV-10** | o mapa da comida (o T2 da V2) | **fora desta versão** | (b) junto, como no J5 | (b) traz de volta as premissas que derrubaram o T2 duas vezes, sem relação com o laço |
| **PQV-11** | o "pensa" na tela | **o motivo mostra o fator `plano` desde o código; o rótulo "pensa" só depois da confirmatória** | (b) o rótulo junto com o código | (b) promete ao jogador o que a medida ainda não mostrou |
| **PQV-12** | a faixa de sementes da triagem | **pedir à coordenadora depois da aprovação deste desenho** | — | nenhum, desde que a triagem não use uma faixa tomada (106xxx a 109xxx) |

**Os números PROPOSTOS e SEM FONTE deste desenho:** os passos S/8 e S/16, o `k_max` 4, o H de 480 ticks, os 8 checkpoints de 60
ticks, o `lambda_colapso` S/8, e o S_J e o P_max (da fumaça).
