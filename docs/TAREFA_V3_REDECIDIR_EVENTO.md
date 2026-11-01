# TAREFA V3 — REDECIDIR_EVENTO: a escolha só é refeita quando o corpo ou o mundo muda, contra o sorteio a cada decisão (2026-10-31)

Coordenador: Gerente da V3 (Claude Code). Worker da etapa 1: Claude Code, Opus 5.5 (método), worktree `v3-redecidir-papel`. Worktree e
branch: `v3-redecidir-papel` (as etapas seguintes, um sufixo por etapa, como `v3-redecidir-evento-espec`). Status: **ABERTA; etapa 1 (só
papel) ENTREGUE; as RD-1 a RD-9 (seção 8) DECIDIDAS pelo Matheus em 2026-10-31, pela recomendação.** Nenhum código, nenhuma faixa e nenhuma vida.

Categoria: arquitetura (depois, implementacao e experimento). Origem: Matheus, 2026-10-31: a D-C2-4: depois da C2 (#517), a C3, redecidir
por evento, em separado, com hipótese e plano próprios; nenhuma combinação C2+C3.

## 0. Os cinco pontos

1. **A pergunta:** no longe, o modular quebra as idas e as buscas a cada poucas decisões. Isso acontece, em parte, porque o M-ARB refaz o
   sorteio a cada decisão, mesmo quando nada mudou no corpo nem no mundo?
2. **O que se testa:** um braço em que a escolha da decisão anterior **fica** (sem sorteio) enquanto não houver um evento: um receptor que
   muda de faixa, o reflexo do sono, um evento sensorial novo, o fim da opção, ou um teto de decisões. Contra o mesmo cérebro com o
   sorteio a cada decisão, que é o de hoje.
3. **O cenário:** o da C1 e da C2: o `longe_fixo` (o primário) e o comedouro (a guarda), com o longe sorteado só descritivo.
4. **A fonte:** só Gadanho e Hallam (2001), verificada na C0 e lida pela tese de 1999 (seção 1.2). Ela dá a direção, não o tamanho. O
   resto é SEM FONTE. **Nenhuma alegação de novidade.**
5. **Esta etapa é só papel.** A espec, o código, o plano e a run vêm depois, cada um com o sim do Matheus (seção 5).

## 1. Pergunta

**Decidir de novo a cada passo é parte da falha do modular no longe?** O teste é um braço com a subchave `redecidir_evento` (PROPOSTA),
em que o M-ARB só sorteia quando há um evento, contra o braço de hoje, que sorteia a cada decisão. É a R3 da triagem
(`docs/referencias/V3C0_SINTESE_TRIAGEM_2026-10-30.md`, seção 4; a lacuna L3 da seção 3) e a linha da C3 do `docs/PLANO_V3.md` (seção 2).
Vem da pergunta da trilha C do plano: os mecanismos que a triagem aponta explicam ou corrigem as falhas do modular no longe e no hábito,
quando cada um é testado com controle?

**Uma interpretação, registrada (seção 5.1):** o plano diz "a intenção só é refeita". No código, a "intenção" (a I\*) só existe nas
unidades com alvo fixo e na busca pelo cheiro (`digilab/digibrain/estado.py`, `TIPOS_INTENCAO` e `BUSCA`). Esta tarefa lê "a intenção"
como **a escolha da decisão**, e a RD-2 pergunta ao Matheus se a regra vale para todas as unidades ou só para as intenções do código.

### 1.1 O que o projeto já sabe (os dados)

- **A decisão de hoje** [CÓDIGO, `digilab/digibrain/adapt.py`, `DigiBrain.agir`, e `arb.py`, `Arbitragem.escolher`]: a cada decisão
  (15 ticks, `intervalo_decisao_ticks`), o M-IMPULSO refaz as ativações de todas as unidades e o M-ARB sorteia entre as positivas,
  proporcional ao peso (`sortear_inteiro`), salvo o reflexo do sono, que escolhe dormir sem sorteio. A intenção em curso entra no sorteio
  com a persistência `h`, mas não é garantida.
- **A persistência já está no teto** (`docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md`, 1.2; `docs/PROPOSTA_L2_PROXIMO_PASSO_DIGIBRAIN_MODULAR.md`,
  1.2): com `tau_c` = 15, o C vai a S na primeira decisão, e h = 4S = `a_max`. Aumentar a persistência não muda a disputa; a intenção
  perde fatias do sorteio para cada concorrente com peso (o chamar e o explorar sobem com a fome).
- **As quebras no longe** [DADO]:
  - **o longe sorteado, a L0** (a espec da L-2, 1.1): das 5 142 buscas pelo cheiro trocadas do M3\*, 4 096 (80 %) pelo reflexo do sono e
    1 042 (20 %) por outra unidade, com ração a menos de R; destas, 477 pelo explorar, 330 pelo chamar a atenção, 222 pelo dormir
    sorteado;
  - **o `longe_fixo`, a C1** (`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, 13.4, item 3): a ida ao lugar lembrado do M3\* termina
    12 704 vezes em `meta` e 17 603 em `trocou`: pelo reflexo 14 023, pelo dormir sorteado 1 026, por outra unidade 2 554. As trocas de
    meta por vida: M2 18,3, M3\* 46,1;
  - **o que isso diz da C3:** o reflexo continua sendo evento (seção 3.1), então ele continua quebrando. **O espaço do mecanismo é a parte
    que não é o reflexo:** cerca de 20 % das quebras da busca no sorteado e cerca de 20 % das quebras da ida no `longe_fixo` (3 580 de
    17 603), mais as escolhas de uma decisão (o explorar pelo vagar e pelo cheiro, o chamar) que hoje trocam a cada sorteio. Um nulo é
    plausível e fica escrito antes.
- **O que a L-2 e a C2 deixaram:**
  - **a L-2** (fechada como negativa pela P-1, LP-2 e LP-3; #454, #455) segurou a intenção **através** do reflexo; o C-L2-2 por episódio
    passou (+0,0103), o C-L2-1 e o C-L2-4 falharam, em boa parte pela medida (a LP-2, seção 1.4 abaixo);
  - **a C2** (#517; o RESULTADO, 14) alargou o crédito para a corrida do comportamento e saiu "≈ 0" (+0,0028 [−0,0003; +0,0060]). A
    corrida durou 1,50 decisão em média (14.5, item 3). A interpretação do worker (14.6, não testada) é que a corrida ficou perto do passo e
    que uma unidade mais longa, "a que o gatilho da C3 daria", é a hipótese da C3, não um resultado da C2.
- **A C1 deixa o cenário:** o `longe_fixo`, com o código, o gabarito e o orquestrador na `main`; o M3\* − M2 por episódio "> 0" ali
  (+0,0489 [+0,0355; +0,0624], 13.1); a taxa por episódio do M3\* 0,559 no `longe_fixo` e 0,440 no sorteado (13.4, item 5).

### 1.2 O que a literatura sugere (só a C0 verificada)

- **Gadanho e Hallam (2001), *Adaptive Behavior* 9(1), `10.1177/105971230200900102`,** VERIFICADA na C0
  (`docs/referencias/v3c0_referencias_verificadas.csv`, a linha marca as trilhas C2 e C3). O que a linha sustenta:
  - o resumo do Crossref: um robô simulado numa tarefa de energia, com um modelo de emoção em três papéis dentro de um aprendizado por
    reforço, um deles **decidir quando reavaliar a decisão;**
  - pela triagem, lido pela tese de 1999 (a versão-irmã, não o artigo): ablação de um papel por vez, com IC95 %; **o gatilho de
    reavaliação explica a maior parte do ganho;** o agente continua abaixo do controlador feito à mão.
- **O que isso autoriza:** a direção da hipótese da C3. Refazer a escolha só quando o estado interno muda pode ajudar um agente que
  aprende num corpo com energia. **Não autoriza:**
  - o tamanho do efeito (os números são da tese; para citar um, ler o artigo: a ressalva da C0);
  - que os eventos desta tarefa sejam os da fonte: lá o gatilho vem do modelo de emoção; aqui, das urgências, do reflexo e do mundo
    (seção 3.1), uma escolha SEM FONTE;
  - que o efeito apareça sem a outra metade da fonte, o crédito por comportamento, que a C2 testou sozinha e deu "≈ 0". A D-C2-4 não deixa
    combinar as duas aqui (seção 6).
- **O que não serve de fonte aqui:** Cañamero (1997, em `docs/referencias/dm_referencias_verificadas.csv`) sustenta as motivações e as
  emoções que mudam a intensidade do comportamento, não o momento de redecidir. Blumberg et al. (2002) e Yoon et al. (2000), na mesma
  tabela da C0, tratam de aprender com o adestramento. Nenhuma das três é citada para o gatilho.
- **Fora disso, SEM FONTE:** a lista de eventos, as faixas das urgências, o teto, as variantes da RD-2, as premissas e todos os números
  novos.
- **Nenhuma alegação de novidade** (a regra 9 de `docs/referencias/REGRAS_CITACAO_DIGILAB.md`). Redecidir por evento num agente com corpo
  já está na fonte acima; o que o projeto faz é o teste com braço de controle, num pet persistente, com replay determinístico.

### 1.3 Em que a C3 é diferente da L-2 e da C2

| | o que muda | onde age | o reflexo do sono |
|---|---|---|---|
| **a L-2** (negativa) | a intenção de comer fica suspensa no reflexo e volta ao acordar, disputando o sorteio | só nas quebras pelo reflexo (80 % no sorteado) | segura a intenção através dele |
| **a C2** (≈ 0) | o crédito ao P2 por corrida do comportamento; a decisão igual | só no P2 | fecha a corrida |
| **a C3** | a escolha fica sem sorteio enquanto não há evento | nas quebras que não são o reflexo, e nas escolhas de uma decisão | **é um evento:** quebra como hoje |

- **A C3 não suspende nem retoma nada.** Ao acordar (a energia volta de faixa, um evento), o sorteio roda como hoje, e a busca pode ou
  não voltar a ganhar. A `intencao_suspensa` fica desligada (a LP-3), e a C3 não a combina.
- **A C3 não toca o crédito.** O P2 recebe as opções como hoje (o PE-3); a `credito_corrida` fica desligada. Uma escolha segurada de uma
  unidade sem alvo fixo continua sendo uma opção de uma decisão por decisão.
- **O que fica igual nas três:** o motor, o mundo, o corpo, o A e a v12.

### 1.4 A lição LP-2, aplicada antes

A LP-2 (o Matheus, #455; `docs/PROPOSTA_L2_PROXIMO_PASSO_DIGIBRAIN_MODULAR.md`, seções 1.2, 2 e 5) registrou dois achados de medida da L-2.
Os dois valem aqui, e a medida já nasce com eles:
1. **A recontagem.** Contar as trocas por intenção muda quando o mecanismo muda quantas intenções há e quanto elas duram. Na L-2, o C-L2-1
   passou a contar no despertar o que antes contava no reflexo. **Aqui:**
   - **as trocas não são o primário** (RD-6). O primário é por episódio de fome, que não depende de como se conta a intenção;
   - **as trocas, no descritivo, são por decisão, não por intenção:** uma troca é uma decisão sem o reflexo cuja unidade escolhida difere
     da última unidade escolhida sem o reflexo. **A retomada de uma busca não conta como troca:** a sequência busca, reflexo, reflexo,
     a mesma busca dá zero trocas, nos dois braços, embora o código de hoje conte duas intenções;
   - as contagens de hoje (os fins `trocou` por intenção) saem ao lado, rotuladas como dependentes do braço.
2. **O grupo selecionado pelo próprio evento.** Na L-2, comparar as buscas suspensas com as "nunca suspensas" separava as que o reflexo
   alcança das que ele não alcança. **Aqui:** nenhum grupo que o mecanismo cria vira contraste: nem as decisões seguradas contra as
   sorteadas, nem as intenções que acabaram por evento contra as que acabaram em meta, nem as escolhas que bateram no teto. Esses grupos
   saem só por braço, como descritivo.

### 1.5 O que cada resultado diria (escrito antes; a forma final vai no plano)

O primário é o P-R (seção 4.3): a taxa de fechamento por episódio de fome, M3\*R − M3\*, nas 4 células do `longe_fixo`. A guarda é o
mesmo contraste no comedouro. O S1 é o M2R − M2 no `longe_fixo`. A classe de cada um ("> 0", "≈ 0", "< 0", "indeterminado") segue a regra
da A6.6: o IC95 contra 0 e a margem δ do plano.

| P-R (`longe_fixo`) | guarda (comedouro) | o que diria | o que se faz |
|---|---|---|---|
| > 0 | não "< 0" | nestas condições, sortear a cada decisão explica parte da falha no longe, sem custo perto da ração. O S1 diz se o efeito precisa da memória ("> 0": não; "≈ 0": passa pelo M-MEM) | o `redecidir_evento` vira candidato; volta ao Matheus. Não vai ao jogo sem a L3 |
| > 0 | "< 0" | ajuda longe da ração e atrapalha perto dela | registrado; volta ao Matheus; não vira candidato |
| ≈ 0 | qualquer | nestas condições, a decisão a cada passo não é a causa: o que o gatilho alcança (as quebras fora do reflexo) não move o episódio | registrado; a C4 segue como planejada; nenhum mecanismo novo de decisão sem plano próprio |
| < 0 | qualquer | segurar a escolha piora o pet | registrado como está; a subchave fica desligada |
| indeterminado | qualquer | nada se decide | registrado como indeterminado |
| qualquer, com a P-SEGURA ou a P-EVENTO falhando | — | inconclusivo por premissa: o mecanismo não segurou, ou segurou por tempo e não por evento | registrado; nada se decide |

- **A previsão de sinal (PROPOSTA): P-R > 0.** A direção vem da fonte; o tamanho, de nada. Com o espaço do mecanismo em cerca de 20 % das
  quebras (1.1), um "≈ 0" não contradiz a fonte, e a tarefa registra isso antes.
- **A previsão não se afrouxa até passar.** Se sair ≈ 0 ou < 0, fica registrado assim.
- **O S1 e o longe sorteado saem sem previsão de sinal:** o M2 não tem o lugar lembrado, e no sorteado a C1 saiu "indeterminado".

## 2. Depende de

- **Na `main`:** a C1 inteira (#495, #497, #503, #506, #507, #508, #510) e a C2 (#512, #513, #515, #517), em `39c87f6`. A C3 usa o
  `longe_fixo`, o orquestrador do adendo 6 e as medidas da C5; da C2, só a convenção do adendo e da run.
- **Decisões que precisam existir:**
  - a D-C2-4 (o Matheus, 2026-10-31): a C2 registrada como negativa, a C3 em separado, nenhuma combinação C2+C3;
  - as RD-1 a RD-9 desta tarefa (seção 8), antes da etapa 2.
- **Do Gerente:** a faixa de sementes (RD-7), conferida e posta na `FAIXAS_RESERVADAS` num commit próprio, na etapa 3.
- **A fila de `digilab/digibrain/`** (`docs/PLANO_V3.md`, seção 5): a C2 terminou; a C4 só papel. A etapa 2 da C3 pega o pacote sozinha.

## 3. Mudança mínima (etapa 2, espec e código; nada nesta etapa)

A espec no formato da L-2 (`docs/ESPEC_REDECIDIR_EVENTO_DIGIBRAIN_MODULAR.md`, PROPOSTO o nome) vem na etapa 2, com os rótulos [DADO],
[CÓDIGO] e [HIPÓTESE]. O que segue é o que ela tem de fixar.

### 3.1 O que muda

- **Uma subchave nova, `redecidir_evento`,** em `ConfigDigibrain` (`digilab/config.py`), `False` por padrão, PROPOSTA, SEM FONTE como
  valor (a direção vem de Gadanho e Hallam). Erro alto se ligada com a `intencao_suspensa` ou a `credito_corrida` (a D-C2-4).
- **A regra, no M-ARB e no M-ESTADO,** PROPOSTA:
  - **a escolha segurada:** sem evento desde a decisão anterior, e com a unidade escolhida antes ainda na lista de unidades (a mesma
    `chave`), o M-ARB escolhe essa unidade **sem sorteio** e sem gastar a rng de política. O M-SENS, o M-AFETO, o M-ESTADO (o contexto), o
    M-MEM e o M-IMPULSO rodam como hoje: o z, as ativações e o registro saem iguais em forma;
  - **com evento, ou na primeira decisão da vida:** o sorteio de hoje, sem mudança;
  - **o M-ESTADO recebe a escolha segurada como uma escolha:** a I\* de novo sobe o C e o `n`, como hoje; uma unidade sem alvo fixo abre
    uma opção de uma decisão, como hoje.
- **Os eventos (RD-3), PROPOSTOS e SEM FONTE,** conferidos no começo da decisão, sem rng:
  - **E-REFLEXO:** o reflexo do sono vale (a `Arbitragem.reflexo`). Ele continua escolhendo dormir sem sorteio;
  - **E-RECEPTOR:** alguma urgência (o `afeto["urgencias"]`) muda de faixa, com as faixas em quartos de S (os limites S/4, S/2 e 3S/4);
  - **E-MUNDO:** uma comida boa entra ou sai dos `vistos`; o cheiro aparece ou some (`ha_cheiro`); o alvo da unidade segurada sai dos
    `vistos`; o dono agiu desde a decisão anterior (o `receber_acao_dono`);
  - **E-FIM:** a opção da decisão anterior acabou na consequência (meta, sumiu, desistiu, achou) ou a unidade não está na lista;
  - **E-TETO (RD-4):** a escolha já foi segurada `n_seg_max` decisões seguidas (PROPOSTO: 6, o valor do `n_desiste_cheiro` e do
    `n_suspensa_max`, sem calibração).
- **O registro da decisão** ganha, só com a subchave, o campo `segurada` (verdadeiro ou falso) e o `evento` (a lista dos que valeram).
- **As sondas** (o G-PESA, `SONDAS` do M-ARB): numa decisão segurada, como no reflexo, nenhum módulo "decidiu". A espec fixa isso por teste,
  e o plano diz como o G-PESA lê as decisões seguradas.
- **O que não muda no cérebro:** o P1, o P2 e o crédito (o PE-3), a persistência, o M-MEM, os inatos do #428 (RD-9).
- **Os braços** (RD-1): `M3*R` e `M2R` são o M3\* e o M2 do conserto (as subchaves do cheiro) com `redecidir_evento` ligada, ao lado do
  `SUBCHAVES_CONSERTO` (`experiments/run_v2_digibrain_prototipo.py`).

### 3.2 Os testes, antes de qualquer vida (com as sementes 101…505)

| teste | o que confere |
|---|---|
| **o gabarito antes** | um commit próprio, antes da mudança, grava as vidas de hoje do M2 e do M3\* no `longe_fixo` e no comedouro, se faltar alguma célula nos gabaritos já commitados (o do protótipo, o do MVP, o da C1 e o da C2) |
| **G2** | com a `redecidir_evento` desligada, as vidas dos gabaritos saem byte a byte |
| **G2-SEPARADO** | a subchave ligada muda só as vidas do braço que a liga; fora do pacote `digibrain` e do orquestrador, nada a lê |
| **G1** | o replay refaz cada vida com a subchave ligada |
| **T-RD-1** | sem nenhum evento, a escolha fica por até `n_seg_max` decisões e a rng de política não é chamada; na seguinte, o E-TETO devolve o sorteio |
| **T-RD-2** | cada evento (E-REFLEXO, E-RECEPTOR, E-MUNDO, E-FIM) devolve o sorteio na decisão em que aparece, um por um, com sequências sintéticas |
| **T-RD-3** | a busca, o reflexo, o reflexo e a mesma busca: zero trocas na contagem da seção 1.4, nos dois braços |
| **T-RD-4** | a escolha segurada de uma I\* sobe o C e o `n` como a mesma escolha sorteada; os fins, o F e o crédito são os de sem a subchave |
| **as conferências do orquestrador** | a do crédito, a dos fins de intenção e a da LP-2 (nenhum `retomou` nem `n_susp`) seguem falhando alto em toda vida; mais uma: toda decisão segurada tem a mesma `chave` da anterior e nenhum evento |
| **G-MECANISMO, G-INT, G-SEM-DIRECAO, G-RECEPTOR** | os de hoje passam com a subchave ligada |

### 3.3 O que NÃO muda

- **O motor:** o `engine.py`, o mundo, o corpo, o cheiro, o `longe_fixo`, o A, a v12 e o jogo web.
- **Os resultados anteriores:** o #420, a reavaliação, a L-2, a C1 e a C2 ficam como estão. Nenhuma faixa gasta (64xxx, 66xxx, 67xxx,
  71xxx, 75xxx) volta.

## 4. Experimento e gate (etapas 3 e 4; PROPOSTO, tudo com o Matheus)

### 4.1 O plano e as sementes

- **O plano de análise:** um adendo 8 ao `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` (RD-8), commitado e APROVADO antes da
  primeira vida.
- **As sementes:** uma faixa nova pedida ao Gerente (RD-7). Sem calibração e sem piloto: a variância vem das vidas já gravadas (4.5).
- **GPU:** não.

### 4.2 O desenho

- **O cenário:** o da C1 (A6.2), sem mudança: o `CONFIG_MUNDO_MVP`, o corpo do v11, o pet sozinho, os quatro donos sem ensino, 14 dias,
  o orçamento de 16 por dia, a morte desligada.
- **Os lugares (RD-5):** o `longe_fixo` (o primário), o comedouro (a guarda) e o longe sorteado (só descritivo).
- **As células:** 4 donos × 3 lugares = 12 por unidade.
- **Os braços (RD-1):** M3\*, M3\*R, M2 e M2R. São 48 vidas por unidade.
- **O pareamento:** por unidade e célula. A mesma semente, o mesmo genoma, o mesmo dono e o mesmo lugar nos quatro; só as subchaves mudam.

### 4.3 O primário, a guarda e as secundárias

- **O primário P-R (RD-5, RD-6):** a taxa de fechamento por episódio de fome (a medida de A6.4), M3\*R − M3\*, a média das 4 células do
  `longe_fixo` por unidade, com o IC95 do t sobre as unidades e a previsão > 0.
- **A guarda G-COMEDOURO:** o mesmo contraste nas 4 células do comedouro, lida pela tabela de 1.5 ("< 0" ou não), sem previsão de sinal
  além de "não < 0".
- **A margem δ e o "≈ 0":** pela regra da A6.6, com o δ tirado do poder (4.5).
- **As premissas, PROPOSTAS e SEM FONTE:**
  - **P-SEGURA:** no M3\*R do `longe_fixo`, a fração das decisões sem o reflexo que foram seguradas é ≥ 0,10. Se não for, quase toda
    decisão tem evento, o braço não difere do de hoje, e o primário é inconclusivo por premissa;
  - **P-EVENTO:** das sequências seguradas, no máximo 0,25 acabam pelo E-TETO (o limiar do C-L2-4). Se passar disso, o braço testa um
    relógio, não o evento, e o primário é inconclusivo por premissa.
- **As secundárias** (pré-registradas, com o IC, sem gate):
  - **S1:** M2R − M2 no `longe_fixo`: o efeito sem o lugar lembrado; sem previsão de sinal;
  - **S2:** M3\*R − M3\* no longe sorteado; sem previsão de sinal.

### 4.4 Os descritivos (sem gate; nenhum muda a leitura de 1.5)

- **As quebras, pela LP-2 (1.4):** as trocas por vida contadas por decisão, com o motivo (o reflexo, o dormir sorteado, outra unidade);
  os fins de intenção de hoje ao lado, rotulados; a ida ao lugar lembrado e a busca pelo cheiro, por fim, somadas por braço.
- **O mecanismo, só por braço:** a fração de decisões seguradas, o comprimento das sequências seguradas, a fração de cada evento que
  devolveu o sorteio, as sequências que acabaram no teto.
- **O corpo:** as medidas da C5 (a fração do tempo com algum estado abaixo de 0,15 e a menor necessidade), a exaustão e a privação de
  hoje, para ver se segurar a escolha prende o pet.
- **Os outros:** a taxa por episódio por faixa de d₀ (com a ressalva da LP-2 da C1: a faixa depende de onde o pet está); a G-PESA por
  módulo, com a leitura das decisões seguradas que o plano fixar; os episódios por vida.

### 4.5 O tamanho (PROPOSTO; a conta vai no plano)

- **O ponto de partida:** 150 unidades, como a C1 e a C2. Com 48 vidas por unidade, dá 7 200 vidas.
- **A conta do poder:** num script só de leitura, como o `experiments/adendo7_poder_habito_intencao.py`, sobre o `medidas.json` da C1
  (71xxx), com o dp da taxa por episódio do M3\* no `longe_fixo`. O δ e o K finais saem dele. Nenhum número de poder é escrito aqui sem
  esse artefato.
- **A máquina (V3-D8):** 4 processos e uma run por vez. Pela taxa da C2 (5 400 vidas em 58 min com 4 processos; o RESULTADO, 14), 7 200
  vidas levariam cerca de 1 h 20 min (PROPOSTO, uma estimativa).

## 5. Entrega

### 5.1 Esta etapa (a etapa 1, só papel)

- **Esta tarefa,** preenchida.
- **O registro das interpretações:** "a intenção" do plano lida como a escolha da decisão (seção 1) e o M-MEM nos braços, ao contrário da
  C2 (RD-1), numa seção no fim de `docs/registro/2026-10.md`, com uma linha no fim de `docs/REGISTRO_DESVIOS.md`.
- **O `docs/PAINEL_V3.md`:** a linha da C2 (rodou, ≈ 0, linha 4, D-C2-4 decidida) e a C3 em papel.
- **O PR contra a `main`,** no modelo `.github/pull_request_template.md`.
- **A conferência:** `python tools/conferir_saude.py` e o `tools/verificar_relato.py`.
- **Nenhum código, nenhuma faixa e nenhuma vida.**

### 5.2 As etapas seguintes, cada uma num PR e com o sim do Matheus

| etapa | o quê | categoria |
|---|---|---|
| **2** | a espec no formato da L-2, o gabarito antes, a subchave e os testes da seção 3.2 | arquitetura, depois implementacao |
| **3** | o adendo 8, com o script do poder, a faixa na `FAIXAS_RESERVADAS` e o orquestrador | implementacao |
| **4** | a run, uma vez, e a leitura pela tabela de 1.5 | experimento |

- **Os testes:** `python -m pytest tests/ -q` em cada etapa de código, com a contagem no PR.
- **O resumo de cada etapa:** no corpo do PR e numa seção no fim desta tarefa (a run, numa seção nova do
  `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, conforme a RD-8). Nunca no `CLAUDE.md`.

## 6. Fora desta tarefa

- **Os outros mecanismos:**
  - a corrida do comportamento (a C2) e qualquer combinação com ela (a D-C2-4);
  - a `intencao_suspensa` (a L-2, fechada; a LP-3);
  - a L-3 (fora pela C1-E2) e a C4 (a memória que decide);
  - a D-C1-3 (as visitas ao lugar lembrado que não acham ração).
- **O que não se mexe:** o reflexo do sono e o `lambda_sono`; a persistência e o `w_pers`; a medida do hábito (a D-C2-4).
- **Fora de escopo:** o A11 e qualquer leitura de superioridade sobre o A; o jogo web (a L3 só depois do sim do Matheus).

## 7. Critérios de aceitação

**Da etapa 1:**
- este arquivo existe na `main` depois do merge, sem nenhum marcador do modelo por preencher;
- as RD-1 a RD-9 têm recomendação e custo de errar;
- o registro e a linha do índice existem, com o mesmo título;
- o `docs/PAINEL_V3.md` tem a C2 rodada e a C3 em papel;
- `python tools/conferir_saude.py` sai com 0;
- o corpo do PR passa no `tools/verificar_relato.py --base origin/main`.

**Das seguintes:**
- a espec revista pelo Matheus antes do código;
- o G2 byte a byte com a subchave desligada;
- os T-RD-1 a 4 passando;
- o adendo 8 APROVADO antes da primeira vida;
- toda vida rejogada bit a bit;
- cada número do resultado com o artefato.

## 8. Decisões do Matheus

**Todas DECIDIDAS pelo Matheus em 2026-10-31, pela recomendação.** Os números novos são PROPOSTOS e SEM FONTE. A direção da hipótese vem de Gadanho e Hallam, pela tese.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **RD-1** | os braços(DECIDIDA) | **M3\*, M3\*R, M2 e M2R.** O M3\* (o modular inteiro do longe, o da C1) é o controle do primário; o par M2 diz se o efeito passa pela memória. O M-MEM entra, ao contrário da C2, porque a ida ao lugar lembrado é a maior fonte de quebras do `longe_fixo` (17 603 trocas, 1.1) e a C1 é o cenário em que o M3\* ganha | só o par M3\*: se der > 0, não se sabe se é a ida ao lugar lembrado que segura; só o par M2: o gatilho fica longe do cérebro que a C1 deixou; com o M1 ou o M0: mais vidas sem pergunta. Os 4 braços custam 2 400 vidas a mais que dois (cerca de 25 min) |
| **RD-2** | o que se segura(DECIDIDA) | **toda unidade escolhida** (o explorar pelo vagar e pelo cheiro, o chamar, o dormir sorteado, as intenções), salvo o reflexo, que é evento. É a leitura de "por comportamento" da fonte. A alternativa (b): só as intenções do código (a I\*) | a (b) mexe quase só nas quebras da I\* por outra unidade, onde a persistência já está no teto: um teste fraco, como a corrida curta da C2 (14.6); com toda unidade, o pet pode ficar mais tempo no chamar ou no dormir sorteado sem evento, e por isso o E-TETO e as medidas do corpo saem ao lado |
| **RD-3** | os eventos(DECIDIDA) | **E-REFLEXO, E-RECEPTOR (a urgência muda de quarto de S), E-MUNDO (comida boa entra ou sai da vista, o cheiro aparece ou some, o alvo some, o dono agiu) e E-FIM** (3.1). A alternativa: qualquer objeto que entra ou sai dos `vistos` | qualquer objeto: andando, os `vistos` mudam quase toda decisão, e a P-SEGURA cai; faixas mais largas (metades de S): o corpo muda pouco antes de o pet redecidir, e a P-EVENTO cai pelo teto; sem o E-MUNDO: o pet segura a ida com uma comida melhor à vista |
| **RD-4** | o teto(DECIDIDA) | **`n_seg_max` = 6 decisões seguidas** (90 minutos simulados), o valor do `n_desiste_cheiro` e do `n_suspensa_max`, sem calibração. Sem teto, um pet sem evento fica preso | um teto curto (2 ou 3) faz do braço um relógio, e a P-EVENTO pega isso; um teto longo deixa o pet preso num chamar sem resposta, e as medidas do corpo pegam isso. Calibrar o teto antes da run gasta um piloto sem pergunta |
| **RD-5** | o lugar do primário(DECIDIDA) | **o `longe_fixo` (4 células) no primário; o comedouro como guarda ("não < 0"); o sorteado só descritivo (S2).** A falha está longe da ração, e no `longe_fixo` a C1 deixa o M3\* com efeito e a maior parte das quebras | as 8 células no primário (como a C2): o comedouro, com a viagem curta e o episódio que já fecha, dilui o efeito e come o poder; sem o comedouro: não se vê se segurar atrapalha perto da ração; o sorteado no primário: a C1 saiu "indeterminado" ali, e um nulo não distingue nada |
| **RD-6** | a medida do primário(DECIDIDA) | **a taxa de fechamento por episódio de fome (A6.4),** a que a LP-2 deixa de pé: não depende de como se contam as trocas nem as intenções. As trocas por decisão (1.4) saem como descritivo | as trocas como primário: a recontagem da L-2 de novo, porque o mecanismo muda o que é uma intenção; a taxa por ração: no longe ela não informa (a PL-3) |
| **RD-7** | a faixa de sementes, a pedir ao Gerente(DECIDIDA) | **76101…76505,** com as bases 76101, 76202, 76303, 76404 e 76505. Na busca de 2026-10-31, nem as bases nem "76xxx" aparecem no `experiments/bancada/faixas.py`, nas `experiments/configs/`, nos `docs/` nem nos `web/app/scripts/` da `origin/main` e dos branches remotos. A 73xxx também está livre, mas fica entre as duas faixas da B1 (72xxx e 74xxx) | uma faixa já usada (a 71xxx, a 75xxx) faz a validação deixar de ser única; uma faixa que outra frente pegue no mesmo dia dá colisão, que a `unidades_derivadas` pega alto, mas que custa refazer |
| **RD-8** | onde fica o plano(DECIDIDA) | **um adendo 8 ao `PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`;** o resultado numa seção nova do `RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, como a C1 e a C2 | um `PLANO_ANALISE_V3_REDECIDIR_EVENTO.md` novo repete os braços, o episódio, a A6.6 e o orquestrador, e pode divergir deles; o custo do adendo é só o tamanho do plano |
| **RD-9** | calibrar algo para o braço R(DECIDIDA) | **não:** os inatos do #428 em todos os braços; a persistência, o `lambda_sono` e o teto como estão. A calibração fica para o fim (a decisão de 2026-10-13) | calibrar só o braço R dá a ele um ajuste que o controle não teve, e o contraste deixa de ser só o gatilho; não calibrar pode dar um nulo por faixas mal postas, e por isso a P-SEGURA e a P-EVENTO protegem a leitura |

## Resultado da etapa 1 (só papel; 2026-10-31, worker Claude Code, Opus 5.5, worktree `v3-redecidir-papel`)

- **Esta tarefa,** com:
  - a pergunta, os dados da L0, da C1 e da C2, o espaço do mecanismo (as quebras fora do reflexo) e a diferença para a L-2 e a C2;
  - a LP-2 aplicada antes (1.4): o primário por episódio, as trocas por decisão, a retomada que não conta, nenhum grupo do mecanismo como
    contraste;
  - os braços, a medida, as premissas e a tabela de leitura escritos antes, e as RD-1 a RD-9.
- **A fonte:** só Gadanho e Hallam (2001), da C0, pela tese; o resto SEM FONTE.
- **A faixa 76101…76505 decidida (RD-7),** ainda não reservada: o Gerente a põe na `FAIXAS_RESERVADAS` num commit próprio, na etapa 3.
- **Nenhum código, nenhuma faixa e nenhuma vida.**
- **O registro:** as duas interpretações em `docs/registro/2026-10.md`.

## Resultado da etapa 2 (espec e código; 2026-10-31, worker Claude Code, Opus 5.5, worktree `v3-redecidir-evento-espec`)

- **A espec:** `docs/ESPEC_REDECIDIR_EVENTO_DIGIBRAIN_MODULAR.md`, no formato da L-2, com as leituras RE-1 a RE-4 (o que as RD não fixam)
  para o Matheus, com a recomendação e o custo de errar.
- **O gabarito antes,** num commit próprio: o M3\* no `longe_fixo` e no comedouro, os quatro donos, as sementes 101 a 505
  (`tests/gabaritos/redecidir_evento_de_hoje.json`); o M2 nas mesmas células já estava no gabarito do #513.
- **O código:** `ConfigDigibrain.redecidir_evento` (PROPOSTA, desligada; ValueError com a `credito_corrida`, a `intencao_suspensa` ou sem as
  duas subchaves do cheiro), `ConfigDigibrainInatos.n_seg_max` = 6, os eventos e o registro no M-ESTADO, o `segurar` no M-ARB, a ordem no
  M-ADAPT; no orquestrador, só o `conferir_redecidir` e a contagem `trocas_por_decisao`. O `engine.py` e a web não mudam.
- **Os testes:** `tests/test_redecidir_evento.py` (T-RD-1 a T-RD-4, G1, G2-SEPARADO, as conferências e o G-MECANISMO ligado) e
  `tests/test_gabarito_redecidir_evento.py` (o byte a byte desligado).
- **Nenhuma vida de pesquisa, nenhuma faixa, nenhum adendo.**

## Resultado da etapa 3 (o plano; 2026-11-01, worker Claude Code, Opus 5.5, worktree `v3-redecidir-evento-plano`)

- **A faixa:** 76101…76505 na `FAIXAS_RESERVADAS`, no commit próprio do Gerente (`1a37e58`).
- **O adendo 8, PROPOSTO** (`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, A8.0 a A8.12): os braços, os lugares, o P-R, a guarda,
  as premissas (P-SEGURA, P-EVENTO e a G-ELEGIVEL-EP de A6.4), as secundárias, a tabela de leitura de 1.5, o descritivo da LP-2, a regra de
  parada e o registro da run para a etapa 4; as AD8-1 a AD8-5 para o Matheus. A trava recusa a run até a marca de aprovação.
- **O poder:** `experiments/adendo8_poder_redecidir_evento.py` lê o `medidas.json` da C1 (e o da C2 e os `meta.json`, só ao lado) e grava
  `artifacts_v2_digibrain_prototipo/redecidir_evento/adendo8_poder.json`: σ de planejamento 0,1094, K = 150 → δ = 0,025 (PROPOSTOS), 7 200
  vidas, de 1 h 18 min a 2 h 8 min com 4 processos.
- **O orquestrador:** `experiments/run_v2_redecidir_evento.py`, com as configs em `experiments/configs/v2_redecidir_evento/` (a da run e a
  fumaça), e os braços `M3R` e `M2R` (`SUBCHAVES_C3`) no orquestrador do protótipo.
- **Os testes:** `tests/test_redecidir_evento_run.py`.
- **A varredura dos fins** (A8.10; as sementes 101 a 505, K = 1, os 4 braços, as 12 células, 14 dias: 240 vidas, 337 s com 4 processos,
  fora do git): nenhum fim desconhecido (só `achou`, `desistiu`, `meta`, `sumiu` e `trocou`), e o replay, o crédito e o `conferir_redecidir`
  passaram em toda vida. Nos braços R, cerca de 0,34 a 0,39 das decisões sem o reflexo saíram seguradas e cerca de 0,05 das sequências
  acabaram no teto: as duas premissas têm o que medir; não é dado da C3.
- **Nenhuma vida da faixa 76xxx.**
