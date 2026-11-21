# Tarefa V3: o pet que pensa (o planejador no modular)

**Status: APROVADO pelo Matheus em 2026-11-21** ("Aprovo todas", à pergunta "Aprova as PQ3-1 a PQ3-9 pela recomendação?").
Escrito pelo Gerente da V3 (Claude Code, Opus 5.5) em 2026-11-21. O pedido é do Matheus: "Eu quero já partir para a parte do pet que
pensa", e, à pergunta de quem escreve o desenho, "Você escreve". **As PQ3-1 a PQ3-9 (seção 8) estão DECIDIDAS pela recomendação.** Os
números novos seguem PROPOSTOS e SEM FONTE. Nenhuma vida roda antes do código da P2 na `main` e do ok do Matheus para cada degrau.

**Regras desta tarefa:**
- Os números novos são PROPOSTOS e SEM FONTE, salvo onde citam um artefato.
- **Nenhuma alegação de novidade.** O que se testa aqui é **este** pet, com **este** planejador.
  - **O planejamento** com um modelo aprendido é a linha do Dyna e do MuZero (só o título; `docs/futuro/pet_que_pensa.md`, seção 10).
  - **O mecanismo** (prever o próprio corpo para agir antes da falta) é a alostase e o controle interoceptivo antecipatório. As três estão
    em `docs/referencias/v3c5_referencias_verificadas.csv`:
    - Sterling (2012), `10.1016/j.physbeh.2011.06.004`, resumo;
    - Tschantz et al. (2022), `10.1016/j.biopsycho.2022.108266`, resumo, o precedente mais próximo;
    - Keramati e Gutkin (2014), `10.7554/eLife.04811`: o valor como redução do drive, que é o `valor(·)` da seção 3.1.
  - **Os testes:** Adams e Dickinson (1981, resumo), para a revalorização. Momennejad et al. (2017) só sustenta o T2, que fica para depois.
- **A revisão da coordenadora está incorporada** (vault, `10 Auditoria/Revisão do PR 1063 pet que pensa 2026-11-21.md`, sobre o
  `Levantamento do pet que pensa 2026-11-21.md`).
- A pausa das runs confirmatórias do cérebro vale também aqui: a decisão do Matheus de 2026-11-21 ("Sim, aplicar") põe a triagem antes de
  qualquer confirmação.

## 0. Por que agora

As runs de 2026-11-17 a 2026-11-20 responderam com clareza, por caminhos independentes, que **o aprendizado do modular quase não decide o
comportamento**. O parecer está no vault, em `10 Auditoria/Vale continuar o cérebro 2026-11-21.md`.

| achado | de onde |
|---|---|
| uma regra de quatro linhas vence o modular (−0,083) | A1 |
| o aprendizado em vida muda pouco o comportamento (TV 0,0084) | A2 |
| o elogio imediato sai igual a não elogiar (E-imed = E0) | ELOGIO (#991) |
| a parte aprendida do dormir é **zero**; no v38, só 11–13 % das decisões de dormir passam pelo sorteio | R-sono (#1044) |
| com mais recompensa o pet dorme **mais** (−0,0109, cerca de 16 min/dia) | recompensa (#1061) |
| zerar o aprendizado social não muda a resposta ao parceiro (C-APR ≈ 0) | SOCIAL_PAR MD2 (#1052) |

**O que melhorou o pet veio do corpo e de regras escritas à mão:** o "sono que segura" do v38 e o teto baixo na ponte do corpo. A leitura é
estrutural: o reflexo do sono e o "sono que segura" decidem sem ler nada aprendido, e os termos aprendidos somam a pesos que quase não
chegam à ação. Calibrar o crédito ou a recompensa mexe numa parte que não decide.

**O pet que pensa troca a pergunta.** Em vez de "um peso aprendido move a escolha?", ele pergunta: "o pet escolhe pelo que **prevê** que a
ação vai fazer no próprio corpo?". É o caminho (e) que o Matheus escolheu em 2026-10-07: "pensar, não agir no instinto".

## 1. O que já existe

**O J5 da V2** (`docs/futuro/pet_que_pensa.md`; `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`):
- **as peças:**
  - o modelo do desfecho: o que cada comida faz em cada receptor, aprendido só pela percepção;
  - o mapa da comida: o que o pet viu cair onde;
  - o planejador de um alvo, que soma um termo `g_plano` ao peso dos candidatos.
- **o código:** `digilab/modelo_mundo.py` (os modelos) e o lobo `planejamento` do cérebro A (`digilab/policies/lobos.py`). Os dois estão na
  `main`.
- **o resultado** (`docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md`, 2026-10-19):
  - **o T1, a revalorização, passa:** `q`(P1-plan) − `q`(P1) = 0,197, IC95 [0,075; 0,323]. É o único primário do J5 que passou;
  - **o T2, a busca, ficou inconclusivo por premissa:** o pet quase não via a fruta cair na árvore nova;
  - o rótulo "pensa" não valeu (o `docs/FECHAMENTO_V2.md` registra que só o T1 passou).
- **o que foi levado e o que não foi:**
  - **o modelo do desfecho foi levado, reescrito:** o P1 do M-PLAST é a conta do `ModeloMundo` com o ganho a mais (`plast.py`), e o
    incentivo usa o `valor_previsto` do J5 (`base.py:88`), que revaloriza a comida pelo estado. Os dois estão ligados por padrão
    (`config.py:2888`). O pet de hoje já tem, portanto, uma revalorização da comida de horizonte zero;
  - **o planejador não foi levado:** nenhum termo do modular escolhe pela previsão do corpo de uma ação;
  - os braços do A saíram da bancada na limpeza (LZ0 a LZ2b). O `lobos.py` ainda está na `main` e sai na LZ4; o lobo `planejamento` não
    serve de base para o código novo.

**No modular, onde um termo novo encaixa** (`digilab/digibrain/adapt.py` e `arb.py`):
- a ativação de cada unidade (comportamento × objeto) é a soma dos termos: o inato, o `incentivo`, o `habito`, a `memoria`, a
  `persistencia` e, com as chaves, a `lembranca` e a `faceta`. O M-ARB sorteia proporcional aos pesos;
- cada termo tem uma sonda "quem decidiu" (`sem_<termo>`), que refaz o sorteio com o mesmo u e o termo zerado;
- **fora da disputa:** o reflexo do sono (energia abaixo de `lambda_sono`), o "sono que segura" (v38) e a escolha segurada. O reflexo
  suave (`ConfigConsertoValuation.reflexo_suave`, desligado) já transforma o reflexo em peso.

## 2. O que o planejador tem de resolver aqui

1. **Ter acesso às decisões que importam.** No J5, o planejador só escolhia o alvo da comida. No pet de hoje, quem decide o dia é o sono
   (cerca de 620 das 1 343 decisões de uma vida dormem; R-a) e o reflexo. Se o planejador não puder disputar o dormir e o acordar, ele
   repete o destino do aprendizado.
2. **Prever o próprio corpo, não só a comida.** O valor de dormir, comer, brincar ou explorar está na mudança dos receptores: a energia, a
   fome, o tédio e a higiene. Um modelo por ação e por receptor generaliza o modelo do desfecho do J5.
3. **Não quebrar o que funciona.** O "sono que segura" e o teto baixo melhoraram o pet. O planejador entra somando, com um ganho que em 0
   devolve o pet de hoje (o G2 do J5), e com um piso de segurança no reflexo.
4. **Ser legível.** O motivo só diz "fui dormir porque prevejo recuperar a energia" quando a sonda `sem_plano` mudaria a escolha (a regra de
   honestidade do motivo).

## 3. O desenho proposto

### 3.1 O M-PLAN, um módulo novo

**O modelo do corpo** (a generalização do modelo do desfecho, PQ3-1):
- **estende o P1 do M-PLAST,** no mesmo estado. Não cria um segundo modelo do desfecho ao lado dele;
- **por taxa e duração, não por Δ médio de episódio:** o Δ de um sono depende de onde ele começa (dormir em S/10 rende mais que dormir em
  S/4) e do corte em [0, S], e uma média por episódio mistura esses casos. Por isso:
  - o modelo aprende a taxa por tick de cada receptor em cada modo (acordado, andando, dormindo, comendo por tipo);
  - prevê a duração do episódio (no dormir, pela energia em que o pet costuma acordar);
  - o Δ previsto é a taxa vezes a duração, cortado em [0, S];
- é aprendido só pela percepção, em inteiros, com o passo `passo_corpo`, como o `d_tr` do J5;
- o prior é 0: o pet nasce sem saber.

**O mapa dos lugares** (o mapa da comida do J5, nos lugares da V3):
- para cada lugar (o comedouro, os lugares do longe), a contagem do que o pet viu lá, por tipo, com um esquecimento lento;
- a primeira versão pode deixar o mapa de fora e medir só o modelo do corpo (PQ3-3).

**O valor previsto de uma unidade:**
`V(b, o) = valor(Δ_b,o, receptores de agora) − custo(o)`
- **`valor(·)`** é a conta do sinal pelo corpo que já existe: a falta antes contra a falta prevista depois. A mesma ação vale mais com mais
  falta (dormir vale mais cansado). Por isso o planejador já revaloriza pelo estado;
- **o custo** é o gasto de chegar ao objeto, também previsto pelo modelo (o andar);
- **o horizonte é um episódio da ação** (PQ3-2), e não uma árvore de busca.

### 3.2 Onde entra

- **Um termo novo `plano` na ativação de cada unidade,** com o ganho `g_plano` (0 = o pet de hoje). Ele soma como os outros termos e tem a
  sonda `sem_plano` (com `plano_decidiu`).
- **O reflexo do sono vira disputa, com piso** (PQ3-4):
  - com o `g_plano` > 0, o reflexo duro é trocado pelo reflexo suave, que já existe: o dormir ganha peso abaixo de `lambda_sono`, e o
    planejador disputa;
  - um **piso de segurança** continua duro: com a energia abaixo de `lambda_sono / 2` (S/8, PROPOSTO), o pet dorme sem sorteio, como
    hoje, para o planejador não levar o pet à exaustão;
  - **o "sono que segura" do v38 fica de fora da primeira versão.** É a regra que mais melhorou o pet ("Tempo bem" 0,727 no v38, contra
    0,633 no pet da bancada). O plano age só no adormecer e na faixa do reflexo; acordar continua com a regra de hoje.
- **Os modelos ficam num módulo próprio, com teto próprio** (a PQ-6 do J5): não contam no teto de pesos do cérebro.

### 3.3 O motivo e a tela

- O motivo ganha o campo `plano`: a previsão da ação escolhida (os receptores que ela muda) e se o plano decidiu.
- A frase só nomeia o que o modelo tem, como no J5. Sem o `plano_decidiu`, o motivo de hoje.
- A fala pelo decodificador de conceitos ganha o conceito "prever", que só entra com o `plano_decidiu` (fica para o porte, etapa P5).

## 4. Como saber se funciona: triagem antes de confirmar

Pela decisão de 2026-11-21, cada etapa com vida nova começa por uma triagem barata. Só o que passar ganha plano de análise e run
confirmatória.

| degrau | o que mede | custo | vida nova? |
|---|---|---|---|
| **D0, replay descritivo** | nas vidas já gravadas: em quantas decisões o planejador poderia decidir (as que não são reflexo, "sono que segura" nem escolha segurada), por lugar e por dono; e **quantas têm conflito** (a fome urgente com a energia na faixa do reflexo suave) | minutos | não |
| **D1, triagem** | os quatro braços abaixo, 20 unidades, 12 células: 960 vidas, de 20 a 35 min com 4 processos (estimativa da revisão, sem medida) | minutos | sim, sementes de teste |
| **D2, a revalorização** | dois testes sem reexperiência: (a) **pela comida**, o T1 do J5 (o efeito de uma comida muda e o dono a dá na mão); (b) **pelo corpo**: do dia 8 em diante a ração mata menos fome, o pet fica sabendo pela mão, e o "comer antes de dormir" muda na noite seguinte. Em cada um, o pet com planejador muda a escolha, e o de hoje não | triagem de 20 unidades, depois confirmação | sim |
| **D3, a medida de produto** | o jogador percebe que o pet pensa? Proxy no motor: a fração das decisões em que o plano decidiu **e** o motivo nomeia a previsão. A medida real é no beta (BT), com o jogador | baixo no motor | não |

**Os braços do D1:**

| braço | o que é | o que separa |
|---|---|---|
| HOJE | o pet de hoje (`g_plano` = 0, o reflexo duro) | a referência |
| SUAVE | o reflexo suave com o mesmo piso, `g_plano` = 0 | o efeito de afrouxar o reflexo, que sozinho já mexe muito no pet (o D + C5 quase dobrou a exaustão, de 0,232 para 0,435; `docs/SINTESE_CORPO.md`) |
| PLAN | o reflexo suave, o piso e o planejador (`g_plano` > 0) | o desenho |
| EMBAR | o PLAN, com o modelo do corpo aprendido igual, mas lido com os receptores permutados (uma permutação fixa por vida) | o conteúdo da previsão: qualquer termo novo de magnitude parecida muda o sorteio |

**A leitura do D1:**
- **o primário é o "Tempo bem", PLAN − HOJE;**
- **"o pet planeja" exige também PLAN − SUAVE > 0 e PLAN − EMBAR > 0.** Sem os dois, o ganho é do reflexo afrouxado ou de um termo
  qualquer, não do planejar;
- **as guardas:** a saúde não piora e a exaustão não sobe;
- **descritivos:** a fração `plano_decidiu`, o custo por decisão e **a fração dos sonos que começam com a fome urgente** (o laço "com fome e
  cansado, dorme e acorda pior"). Se essa fração não cair, o próximo passo é o horizonte de duas opções (PQ3-2), não um ganho maior;
- **o braço congelado** (os modelos parados antes da mudança) fica para o D2.

**O D2 e o P1 de hoje:** pela docstring do `plast.py`, só o consumo do `comer` atualiza o desfecho. O desenho precisa decidir se o P1
aprende com a comida dada na mão. Se aprender, o pet de hoje também muda a escolha, e o contraste cai. Se não aprender, o contraste mede
só o gancho da mão, não o planejar. Por isso o D2 tem também o teste (b), pelo corpo, que o P1 de hoje não alcança.

**O corte da triagem para virar confirmação** fica para a PQ3-9: com o δ = 0,032 da C4, 2δ = 0,064, e o teto baixo, o único ganho
replicado, deu +0,062 e **não passaria**.

**O T2, a busca,** fica para depois do D2. Na V2 ele caiu por premissa (o pet não via a mudança), e só faz sentido com o mapa ligado (PQ3-3).

## 5. Riscos

| # | risco | o que o desenho faz |
|---|---|---|
| R-1 | o planejador decide pouco, como o aprendizado | o D0 mede antes, sem vida nova, quantas decisões ficam abertas. Se quase nenhuma, o desenho volta (PQ3-4) |
| R-2 | o planejador domina e o pet vira um otimizador frio | soma por `g_plano`, com o inato e o hábito somando junto; a triagem olha a variedade (a entropia do dia, que já é medida) |
| R-3 | tirar o reflexo duro faz mal ao pet | o piso de segurança duro e as guardas da triagem: o "Tempo bem", a saúde e a exaustão |
| R-4 | uma assinatura falsa: um hábito sofisticado passa na revalorização | os braços de controle do J5 (com os modelos congelados), levados para o D2 |
| R-5 | o modelo do corpo aprende devagar e o planejador decide com um prior vazio | o prior 0 não move nada; a triagem mede em que dia o termo começa a decidir |
| R-6 | o custo por decisão no navegador | os candidatos são poucos, e a conta é em inteiros; o D1 mede o custo |
| R-7 | o rótulo "pensa" sem prova | só com o D2 passando. Antes disso, a tela não diz "pensou" |

## 6. As etapas

| etapa | o quê | quem decide |
|---|---|---|
| **P0** | esta tarefa (papel) | FEITA: aprovada em 2026-11-21 |
| **P1** | o D0: o replay descritivo, sem vida nova | depois da P0 |
| **P2** | o código do M-PLAN atrás de chave (o modelo do corpo, o termo `plano`, a sonda, o piso), no Python, com testes e o G2 (com `g_plano` = 0, o log igual ao de hoje, bit a bit) | o merge |
| **P3** | o D1, a triagem | o ok para rodar |
| **P4** | o plano de análise do D2 e a confirmação, só se o D1 passar do corte | a aprovação do plano |
| **P5** | o porte para a web e o motivo na tela, só se o D2 passar: só o M-PLAN, o piso e a sonda `sem_plano` vão à web, com paridade por gabarito; os braços SUAVE, EMBAR e congelado ficam só no Python | o Matheus |

## 7. A relação com as outras frentes

- **CORPO (a coordenadora):** o modelo do corpo aprende o corpo que estiver ligado. Se o teto baixo entrar (V1-a, V1-b), o planejador
  aprende o corpo novo sem mudar nada. A triagem da V1-a não bloqueia esta tarefa.
- **PET_VIVO / cadeia (a coordenadora):** o R2 e o adendo da recompensa estão pausados. O pet que pensa não usa o crédito do intervalo.
- **VALUATION (a coordenadora):** o reflexo suave da C5 é a peça que a PQ3-4 reusa.
- **SOCIAL_PAR:** pausada. O outro pet pode entrar no modelo depois, como no J5 (fora da primeira versão).

## 8. As decisões do Matheus (DECIDIDAS em 2026-11-21, "Aprovo todas", pela recomendação)

| nº | decisão | recomendação | custo de errar |
|---|---|---|---|
| PQ3-1 | o que o modelo prevê | **o corpo por ação, estendendo o P1 do M-PLAST:** a taxa por tick de cada receptor em cada modo, vezes a duração prevista do episódio | só a comida, como no J5: o planejador não disputa o sono, que é o que decide o dia. Um Δ médio por episódio: enviesa o dormir pelo ponto de partida |
| PQ3-2 | o horizonte | **um episódio da ação** (até ela acabar); se no D1 a fração dos sonos com a fome urgente não cair, o próximo passo é o horizonte de duas opções | H decisões ou uma árvore de busca: multiplica o custo e pede um modelo de transição do mundo inteiro, antes de saber se o simples decide |
| PQ3-3 | o mapa dos lugares | **fora da primeira versão:** só o modelo do corpo; o mapa entra com o T2 | ligar já: duas peças novas de uma vez, e uma triagem que não separa qual decidiu |
| PQ3-4 | o reflexo do sono | **vira disputa (o reflexo suave), com um piso duro em `lambda_sono / 2` (S/8)** quando o `g_plano` > 0; **o "sono que segura" fica de fora** da primeira versão | manter o reflexo duro: o planejador não chega ao dormir (R-1). Tirar sem piso: o pet pode se esgotar (R-3). Pôr o "sono que segura" em disputa já: arrisca a regra que mais melhorou o pet |
| PQ3-5 | onde o termo entra | **um termo `plano` na ativação de cada unidade, com `g_plano` e a sonda `sem_plano`** | um cérebro novo: a comparação deixa de ser "o mesmo pet com e sem pensar" |
| PQ3-6 | o tamanho e o teto | **os modelos num módulo próprio, com teto próprio**; 0 pesos a mais no cérebro | contar no teto de pesos: o planejador esbarra nele |
| PQ3-7 | a ordem e os braços da avaliação | **D0 (replay) → D1 (triagem) → D2 (revalorização) → D3 (produto)**, cada degrau só com o anterior passando. **No D1, os braços HOJE, SUAVE, PLAN e EMBAR, com o "Tempo bem" PLAN − HOJE como primário** e "planeja" exigindo PLAN − SUAVE > 0 e PLAN − EMBAR > 0 | só PLAN contra HOJE: não separa o planejar do reflexo afrouxado nem de um termo qualquer. Ir direto à confirmação: repete o custo das runs de 2026-11-17 a 20 |
| PQ3-9 | o corte da triagem para virar confirmação | **o IC95 de PLAN − HOJE no "Tempo bem" acima de 0 e a média em δ (0,032) ou mais,** com PLAN − SUAVE e PLAN − EMBAR também acima de 0. Não 2δ: 2δ = 0,064 recusaria o teto baixo (+0,062), o único ganho replicado | 2δ: recusa efeitos do tamanho do melhor que o projeto já achou. Sem corte: toda triagem vira confirmação, e o custo volta |
| PQ3-8 | quem executa | **o código numa sessão lateral, com a revisão do Gerente;** a Gerência da V3 fica dona da frente | a coordenadora: mais uma frente na fila dela, que já tem o corpo, a cadeia e a VALUATION |

## 9. O que esta tarefa não afirma

- Nada sobre o pet pensar: só o D2, passando, deixa usar a palavra.
- Nada sobre o planejador ser melhor que o aprendizado no "Tempo bem". É uma pergunta da triagem.
- Nada sobre a web antes da P5.
- Nenhum número de resultado. Os que aparecem são citados de artefatos já na `main`.

## 10. Adendo 1: o portão de "quando pensar" e a entropia da decisão (APROVADO pelo Matheus em 2026-11-21 ("Aprovo todas", à pergunta "Aprova as PQ3-10, PQ3-11 e PE-8 a PE-11 pela recomendação?"))

**De onde vem.** O Matheus pediu a leitura das notas do vault sobre Bennett (2023) e Gleick (2011), em `20 Temas`, e escolheu levar às
tarefas os três pontos que mexiam na etapa atual ("Os três"). Dois são desta tarefa:
- o portão de "quando pensar" (Bennett, salto 3);
- a entropia por decisão (Gleick, parte C).

O terceiro, o crítico, entra na `docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md`. **O Bennett é moldura, não citação:** o adendo se apoia na
fonte primária, já verificada no projeto.

### 10.1 O portão (um braço novo no D1)

- **O problema:** o termo `plano` soma em toda decisão (PQ3-5). A arbitragem por incerteza entre o sistema de hábito e o de modelo, de Daw,
  Niv e Dayan (2005), já verificada no projeto, põe no centro outra pergunta: **quando** simular. O J5 da V2 registrou isso como o risco R-6
  e deixou para depois.
- **O D0 mostrou onde fica o conflito** (`docs/RESULTADO_V3_PET_QUE_PENSA_D0.md`, #1069): a fome urgente com a energia na faixa do reflexo
  suave aparece em 8 % a 21 % das decisões do corpo de hoje, e em 10 % a 16 % no v38.
- **O braço PLAN-PORTÃO:** o PLAN, com o termo `plano` somado só nas decisões em que o portão abre. O portão abre em dois casos (PQ3-10):
  1. a margem entre as duas unidades de maior peso, sem o termo `plano`, fica abaixo de `margem_portao` (PROPOSTO: S/8 da maior);
  2. o inato, o hábito e o incentivo apontam unidades diferentes como a de maior peso.
- **A sonda nova:** `portao_abriu`, por decisão, no motivo. Com o portão fechado, o `plano_decidiu` é falso por construção.
- **O que o braço mede:** se planejar só no conflito dá o mesmo "Tempo bem" que planejar sempre. Na triagem, o PLAN-PORTÃO entra no
  contraste contra HOJE e contra PLAN. Se ele empatar com o PLAN, é o desenho mais barato e o mais legível para o D3: o pet "pensa" só
  quando hesita.
- **O tamanho do D1:** passa de 4 para 5 braços, de 960 para 1 200 vidas.

### 10.2 A entropia da decisão (um descritivo novo no D1)

- **A medida:** a entropia do sorteio `H(w/T)` em bits, em cada decisão (os `w` e o `T` já estão no motivo do M-ARB), e a fração das
  decisões com `H` abaixo de 0,1 bit ("quase reflexo"). Com o reflexo, `H` = 0. Fonte: Shannon (1948).
- **Por que:** mede "quanto da decisão é escolha" de forma mais fina que a F_PESOS do R-sono e as frações abertas do D0. Mostra se o
  planejador concentra a escolha (H cai) ou a espalha.
- **A previsão, escrita antes de calcular (D-RB-13):**
  - no HOJE, `H` ≈ 0 no sono e acima de 1 bit no acordado do `longe`;
  - no PLAN, `H` cai nas decisões com conflito em relação ao HOJE.

  É descritiva, não gate.
- **Também no D0:** a mesma medida pode sair das vidas já gravadas, por replay e sem vida nova, ao lado das frações do #1069 (PQ3-11).

### 10.3 As decisões do adendo (DECIDIDAS em 2026-11-21, pela recomendação)

| nº | decisão | recomendação | custo de errar |
|---|---|---|---|
| PQ3-10 | o braço PLAN-PORTÃO no D1 | **sim, com o portão pela margem (S/8, SEM FONTE) ou pela discordância entre o inato, o hábito e o incentivo** | sem o braço: o D1 não diz se pensar sempre é preciso, e o motivo na tela fica "pensou" em quase toda decisão |
| PQ3-11 | a entropia da decisão como descritivo do D1, e por replay ao lado do D0 | **sim** | sem ela: a pergunta "quanto é escolha" segue medida só por frações grossas |
