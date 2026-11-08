# A rodada "pet vivo": a crítica às revisões e o plano (2026-11-07)

Estado: **PROPOSTO**, para o Matheus decidir. Escrito pelo Gerente da V3 (Claude Code, Opus 5.5), a pedido dele em 2026-11-07: "leia a outra revisão [...] Analise os levantamentos anteriores e planeje a próxima rodada. E veja se tem alguma crítica ou algum ponto sobre as análises."

O que foi lido:
- **o levantamento:** `docs/futuro/levantamento_cerebro_modular.md`;
- **a busca colada no chat em 2026-11-07:** chegou cortada no eixo 7, com links do ChatGPT;
- **a revisão I:** `docs/referencias/I_REVISAO_PET_VIVO_MODULACAO.md`.

Os pontos sobre o código foram conferidos na `main` (`f866be29`) e citam o arquivo.

## 1. As três análises lado a lado

| | o levantamento | a busca colada | a revisão I |
|---|---|---|---|
| o que é | o inventário do cérebro, das runs e das falhas, e o prompt | uma primeira passada: referências e uma recomendação de método | a busca completa: 9 eixos, cerca de 70 fontes e 5 mecanismos com teste |
| qualidade das fontes | só as já verificadas no projeto | quase tudo só pelo resumo; duas linhas misturadas; termina no eixo 7 | DOIs reconferidos no Crossref; as colunas `lido` e `evid.` (C, S ou D); três correções de citação |
| o ponto mais forte | o corpo entra no cérebro só como entrada e recompensa, nunca como modulador | **auditar a escolha antes de acrescentar qualquer mecanismo**, e três hipóteses para o mesmo sintoma, entre elas **o número desigual de alvos** | os testes com placebo: margem fixa, giros desacoplados, r embaralhado no tempo, alvo ao acaso na mesma distância, alívio em hora aleatória |
| o ponto fraco | não tinha ainda as fontes externas | não serve como fonte enquanto não for verificada | ver a seção 2 |

A revisão I é a melhor das três. A busca colada traz uma ideia que a revisão I não traz: o número de alvos.

## 2. A crítica à revisão I

### 2.1 Dois mecanismos já existem em parte, e a revisão não sabe

- **O M3 (o terceiro fator pela queda do drive convexo):**
  - o `r` do modular já é isto. O `sinal_corpo` (`digilab/policies/lobos.py`, linhas 2745 a 2747 e 2897) é `ganho·(D_antes − D_depois)/S`, com `D` o déficit homeostático, Σ falta²;
  - o hebbiano já usa o `r_n` com sinal (`digilab/digibrain/plast.py`, linhas 17 e 133 a 140): uma piora já enfraquece;
  - **o que o M3 traz de novo** é só (a) subtrair a linha de base, `r − EMA(r)` (Daw, Kakade e Dayan 2002), e (b) o árbitro hábito × modelo de Miller, Shenhav e Ludvig 2019;
  - o teste precisa ser desses dois pedaços. A parte que já existe não entra como braço.
- **O M5 (a ponte de crédito por opção):**
  - o P2 já dá o crédito à decisão que abriu a opção. Em `plast.py`, linha 18, `e_j = z_j` é "a elegibilidade" da decisão que começou a opção, e `r_n` é a soma dos `r_n` das consequências dela;
  - a C2 (#517) já testou o crédito na corrida inteira e deu ≈ 0, mas a corrida média tinha 1,5 decisão (R§14.6);
  - **o que o M5 traz de novo** é uma opção que dura a caminhada inteira, até comer (o "DoUntil"), e o buffer de lugares;
  - a diferença para a C2 tem que estar escrita no plano, senão a run repete a C2.

### 2.2 O M1 repete três coisas já testadas sem citá-las

- **A persistência:** o bônus para a intenção em curso já existe (`h = w_pers·C`, `digilab/digibrain/estado.py`, linha 9). A G-PESA ficou entre 0,0014 e 0,0035 em todas as runs, porque o termo só aparece em cerca de 3 % das decisões (R§6).
- **A L-2:** a busca suspensa no cochilo caiu só 28 % (pedia a metade), e a busca retomada foi cortada de novo em 86 % das vezes pelo sorteio (R§12.5).
- **A C3:** "decidir só quando a ação acaba" é o remédio do Graham 2013 que a revisão cita. Ele é a C3, que saiu indeterminada (+0,0124 [−0,0060; +0,0308]).
- **Onde o M1 se diferencia:**
  - a troca por **razão** (`rival·16 > ativo·G`), e não por soma;
  - o **término explícito** (o DoUntil);
  - a lista Startle por argmax.

  O plano precisa dizer por que isso venceria onde a persistência aditiva, a L-2 e a C3 não venceram.

### 2.3 O M4 parte de um diagnóstico que não vale para este pet

- **O que a revisão supõe:** pelo Foster, Morris e Dayan 2000, "lembra mas não acha" seria um valor de lugar sem vetor.
- **O que o pet já tem:** o modular já guarda a coordenada. A unidade `explorar/ponto lembrado` vai até um ponto (x, y) (`digilab/digibrain/mem.py`).
- **O que a C1 mostra:** 0 das 12 704 visitas acharam ração (R§13.6). O pet chega ao lugar, e a comida é que não está lá.
- **O que serve do M4:** a busca local depois de chegar (Gray, Hill e Bargmann 2005) e o "apagar ao chegar e não achar" (o devlog de Rain World). O vetor, não.
- **Antes do M4:** o plano tem que explicar por que o lugar fica vazio. Se a ração não reaparece ali, nenhum mecanismo de memória resolve, e o problema é do mundo.

### 2.4 O M2 precisa conversar com a L0

- **O que a L0 achou:** a falha do "longe" é de decisão em 99,9 % e de percepção em 5,8 % (R§10). Isso parece contrariar o M2.
- **O que a L0 também achou:** a busca que não fecha anda 0,15 passo líquido, contra 5 necessários. Isso é navegação, e o M2 ataca exatamente isso.
- **O que o pet tem hoje:** o mundo já tem a intensidade do cheiro (`PercepcaoMundo`), e o modular lê só a presença, pela regra G-SEM-DIRECAO.
- **O que o M2 faz com isso:** o `dC/dt` usa a intensidade no tempo e respeita a regra, porque não lê direção. Já o viés lateral `C_esq − C_dir` lê direção, e a G-SEM-DIRECAO teria que ser revista com o Matheus.

### 2.5 O que falta na revisão

- **O número de alvos** (da busca colada): o M-ARB sorteia proporcional a cada unidade (comportamento, alvo).
  - Um comportamento com mais unidades ganha chance só por isso.
  - O explorar tem o vagar, o cheiro e o ponto lembrado, e o comer tem uma unidade por comida vista.
  - Isso pode explicar parte das trocas de meta e do explorar em 29 % do tempo.
  - Nenhuma das três análises mediu.
- **O incômodo do Matheus é a vida, não a eficiência.**
  - Os cinco mecanismos são consertos do forrageio, medidos pelo fechamento dos episódios de fome.
  - O que ele disse foi "não sinto que tem órgãos" e "não sinto que é um pet que está realmente pensando e agindo conforme os estímulos". O que ataca isso ficou na lista dos "fora":
    - a tabela químico → parâmetro do Creatures;
    - os dois estados M_fica e M_sai do Flavell 2013, com controle em verme;
    - o ganho olfativo pela fome do Root 2011.
  - Falta também uma **medida** de "age pelo estado interno". Hoje todo gate é de forrageio, e isso empurra cada mecanismo para a eficiência.
- **O custo da máquina:**
  - os cinco testes somam mais de 20 braços, e o M1 tem doses e o cruzamento 2×2 com o M2;
  - a regra é uma run de pesquisa por vez, com no máximo 4 processos;
  - as doses são calibração, com faixa própria;
  - a validação roda uma vez;
  - "as mesmas sementes da L0" não pode: as sementes da L0 já foram vistas.
- **As medidas novas** (o teste de desvalorização, os giros com o cheiro em queda, as revisitas inúteis) entram no `digilab/metrics.py`, uma vez só, antes da run.

### 2.6 Pontos de forma

- **O arquivo está sem commit** na pasta `D:\Trab\digilab\v3`, que é só a referência da `main`. Este PR leva uma cópia para o git, e o original fica para o Matheus apagar.
- **Os nomes M1 a M5 colidem** com os braços M1, M2 e M3\* do modular e com as etapas M1 a M5 da conversa. Aqui eles viram **PV-1 a PV-5**, na ordem da revisão.
- **As referências entram como pistas:** só passam a VERIFICADA depois da skill `literatura-digilab`, numa tabela `docs/referencias/v3c5_referencias_verificadas.csv`.
- **A divergência do G0** (Grand e Cliff 1998 usado para conteúdo) aparece de novo na revisão: lá a referência está como "metadados", e é isso que vale.

## 3. A rodada proposta

A rodada se chama **PET_VIVO**, numa tarefa própria (`docs/TAREFA_V3_PET_VIVO.md`). Ela tem duas perguntas, e a primeira vem antes de qualquer mecanismo.

### Etapa 0: papel (sem vida nova)

1. **A verificação das referências da revisão I:** a skill `literatura-digilab` confere a existência e o conteúdo, e o resultado vai para o `v3c5`. Os pontos da seção 2 entram como notas.
2. **A auditoria da escolha:** um descritivo com plano registrado, no molde da D-C1-3, sobre vidas já gravadas, sem semente nova. Ele usa os artefatos da C4 (REL) e da AN0 e mede, para cada decisão:
   - quanto cada termo pesa (inato, proximidade, novidade, incentivo, hábito, memória, persistência, lembrança);
   - **quantas unidades cada comportamento tem e quanto da probabilidade vem só desse número**;
   - quanto o reflexo do sono decide;
   - quanto a escolha muda quando cada receptor muda (a sensibilidade da ação ao corpo).

   O que a auditoria responde: qual das três hipóteses da busca colada vale (pesos, número de alvos ou sinal do corpo fraco). A resposta escolhe a etapa 2.
3. **A medida de "age pelo estado":** uma medida no `metrics.py`, com um plano próprio, para servir de gate ao lado do forrageio.
   - Candidatas: a dependência da distribuição das ações em relação a cada receptor; o teste de revalorização do Zhang 2009, que a C4 e o J5 já tocaram; a repetibilidade das sondas da INDIVIDUALIDADE (o I2, com a faixa 85101…85505 proposta).
   - O I2 vira a **linha de base do "antes"** desta rodada.

### Etapa 1: a decisão do Matheus

Com a auditoria na mão, o Matheus escolhe uma ou duas frentes. A recomendação de hoje, que pode mudar com a auditoria:

| ordem | frente | por que | custo |
|---|---|---|---|
| 1 | **PV-2, a quimiotaxia por dC/dt** (sem o viés lateral) | ataca a navegação de 0,15 passo líquido; tem evidência com controle em verme e larva; respeita a G-SEM-DIRECAO; é barata | baixo |
| 2 | **O corpo modula o cérebro**: a tabela de receptores químico → parâmetro, mais os dois estados persistentes de Flavell | é o que o Matheus sente que falta; também ataca a troca de meta (os estados persistentes) | médio; precisa de espec |
| 3 | **PV-1, a histerese por razão com término** | só se a auditoria mostrar que a troca vem da escolha e não do número de alvos; o plano diz por que vence onde a persistência, a L-2 e a C3 não venceram | médio |
| 4 | **PV-3, a linha de base e o árbitro do hábito** | só os dois pedaços novos (2.1) | baixo |
| depois | PV-4 (a busca local e o apagar, depois de explicar o lugar vazio) e PV-5 (a opção até comer, diferente da C2) | dependem da auditoria e do mundo | — |

Se a auditoria mostrar que o número de alvos pesa, o primeiro conserto é normalizar o sorteio por comportamento (o posto do Dill 2015, ou sortear o comportamento antes do alvo). É o mais barato de todos.

### Etapa 2: a frente escolhida

- Cada frente segue o método de sempre: a tarefa, o gabarito em commit próprio, o código atrás de chave desligada, o plano com os placebos da revisão I e a faixa pedida ao Gerente.
- A run roda uma vez, e os gates são de **forrageio e de "age pelo estado"**.
- Depois vem o porte ao jogo, se passar.

## 4. O que fica com o Matheus

- **A rodada:** aprovar a PET_VIVO e a ordem da etapa 0 (verificar, auditar, medir).
- **A G-SEM-DIRECAO:** fica como está (o PV-2 só com dC/dt) ou se revê, e então o viés lateral entra.
- **O arquivo da revisão:** apagar o `docs/referencias/I_REVISAO_PET_VIVO_MODULACAO.md` sem commit da pasta `v3`, depois deste merge.
