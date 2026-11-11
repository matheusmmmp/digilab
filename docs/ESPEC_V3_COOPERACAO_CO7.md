# ESPEC V3 — COOPERACAO, CO7: os deveres como escudo, o teste da universalização e a culpa e a inveja (2026-11-11, PROPOSTA, Claude Code, Opus 5.5)

**Status: PROPOSTA, para o Matheus revisar antes de qualquer código.** Esta espec detalha a CO7 da `docs/TAREFA_V3_COOPERACAO.md`: os
deveres como escudo, por estágio. Ela parte da proposta `docs/futuro/kant_cooperacao.md` (as K-2, K-3 e K-4, DECIDIDAS em 2026-11-11) e da
espec da CO6 (`docs/ESPEC_V3_COOPERACAO_CO6.md`, as CO6-1 a CO6-7 DECIDIDAS). **O código é coordenado pela frente COOPERACAO** (o Gerente da
V3, pela K-1). As decisões CO7-1 a CO7-8 (seção 8) estão PROPOSTAS. Todos os números são PROPOSTOS, SEM FONTE como escolha, e não há
alegação de novidade.

## 0. O que já existe e o que vale

- **A CO3** mede os atos (a disputa, que é "anti" com o outro abaixo do piso de fome; a contenção; o encostar), a pontuação e a reputação,
  como função do log.
- **A CO6** põe no cérebro a reputação de cada outro presente e o peso dos deveres `k`, que cresce com a convivência, com um teto por estágio.
  Ela **não usa** os dois na decisão.
- **A D-MM-1:** a felicidade do corpo escolhe entre as ações permitidas, e os deveres entram como restrição.
- **A D-MM-14:** o "bem maior" é lexicográfico: o piso de cada pet, depois a média, nunca a soma.
- **A D-MM-10:** nenhuma correção mexe no corpo. Por isso a culpa e a inveja ficam no afeto (K-4).
- **O G-RECEPTOR-SOCIAL:** nenhum pet lê o estado interno do outro, só o que é físico e visível.
- **O que esta etapa muda:** é a primeira em que a cooperação muda a decisão (a CO-3 previu isso).

## 1. A pergunta da etapa

Com os deveres como restrição e o teste da universalização como peso, o pet passa a agir de modo pró-social, e mais quanto maior o `k` dele?
E isso sem que nenhuma felicidade compre uma ação proibida, e sem ler o que se passa dentro do outro.

## 2. O escudo: as ações proibidas (K-2)

### 2.1 A regra

- **O que é proibido no estágio com `k` acima do limiar do escudo** (CO7-2): pegar a comida para a qual um outro pet à vista está indo,
  quando esse outro mostra aflição visível.
- **O "indo para" é físico:** o outro está a até `r_escudo` células da mesma comida e a última posição dele se aproximou dela.
- **A "aflição visível" também é física:** a ação visível dele é `emburrar` ou `chamar_atencao`.
- **Por que não a fome do outro:** a CO3 usa a fome real do outro para dar o sinal "anti", porque a CO3 é uma medida do motor. O escudo é uma
  regra que o pet segue, e ele só pode seguir o que vê (o G-RECEPTOR-SOCIAL). Usar a fome real deixaria o pet adivinhar o estado do outro
  pelo próprio escudo (CO7-1).

### 2.2 Onde entra

- **No M-ARB:** as unidades candidatas que levam a esse ato saem das candidatas antes do sorteio. Se nenhuma sobra, fica o ocioso.
- **É o *shielding*:** uma restrição dura, fora da soma dos pesos, como na nota *Moral do pet* (Alshiekh et al. 2018, `10.1609/aaai.v32i1.11797`).
  Nenhuma urgência, mesmo a fome do próprio pet, compra a ação proibida.
- **A exceção do próprio piso** (CO7-3): se o próprio pet está abaixo do piso de fome (a privação), o escudo não vale para ele. O dever
  kantiano não pede que o pet se deixe morrer de fome.

## 3. O teste da universalização (K-3)

### 3.1 A regra

- **O teste:** "e se todos os pets da ilha fizessem isto?" (Levine et al. 2020, `10.1073/pnas.2014505117`), na forma do equilíbrio kantiano
  de Roemer (2010, `10.1111/j.1467-9442.2009.01592.x`).
- **O que ele faz:** para cada ação candidata, o motor estima o efeito na felicidade lexicográfica da ilha (D-MM-14) se todos os pets fizessem
  o mesmo tipo de ato.
- **Neste mundo, o teste se reduz à tabela de sinais da CO3:**
  - todos disputando a comida de quem está aflito baixam o piso, e a ação reprova;
  - todos deixando a única comida para quem está aflito sobem o piso, e a ação aprova;
  - o resto é neutro.

  A espec diz isso às claras: com os atos de hoje, a universalização não traz nada além da tabela. Ela fica como forma, para valer de
  verdade quando houver atos novos, como dividir e levar comida.

### 3.2 Onde entra

- **No M-ARB, como peso:** a ação que reprova perde `mul(k, w_univ)` do peso, e a que aprova ganha o mesmo, antes do sorteio.
- **Um teto:** o ganho nunca passa do peso da urgência mais forte, para o dever não virar compulsão (CO7-4).

## 4. A culpa e a inveja, no afeto (K-4)

- **A aversão à desigualdade** é de Hughes et al. (2018), arXiv 1803.08884, preprint.
- **A culpa:** sobe quando o pet está com o humor alto e vê um outro com aflição visível.
- **A inveja:** sobe quando o pet está com o humor baixo e viu um outro comer há pouco (o `onde_comeu`, com a idade curta).
- **Onde entram:** como dois termos novos no M-AFETO, que somam à valência (o `V`) com o sinal negativo. Os pesos são por personalidade: a
  faceta do M-PERS, quando ligada, ou neutros. Nenhum mexe no corpo químico.
- **O que isso muda:** a culpa empurra o pet para ações que aliviam o outro (o encostar, a contenção) pelo caminho que o afeto já usa. A inveja
  empurra para a disputa, e o escudo segura a parte proibida.

## 5. O que não muda

O corpo químico (D-MM-10), a luta (D-MM-2 e LP-3), o `engine.py`, a fala (a LLM é só voz) e o pet sozinho, que sem `Grupo` não tem nada da
CO7.

## 6. A chave, o gabarito e a paridade

- **A chave:** uma subchave `co7` na `ConfigCooperacao`, desligada por padrão, que exige a `co6` ligada. Sem ela, falha alto.
- **O gabarito, num commit próprio, antes:** as vidas do `Grupo` com a CO6 ligada e a CO7 desligada.
- **Os testes:**
  - o G2: desligada, as vidas e o gabarito saem byte a byte;
  - o G-ESCUDO: com a CO7 ligada, nenhuma decisão faz o ato proibido quando a regra vale (fora da exceção do próprio piso). É contado em todas
    as decisões de vidas do `Grupo`;
  - o G-RECEPTOR-SOCIAL: o escudo, o teste e a culpa e a inveja só leem campos físicos;
  - casos feitos à mão para o escudo, o peso da universalização com o teto, e a culpa e a inveja;
  - o G-PAR-CO7: Python e TS iguais, decisão a decisão, contra um gabarito exportado.
- **O replay:** tudo é função do log e do estado do próprio pet.

## 7. As missões e a pergunta de pesquisa

| missão | o quê |
|---|---|
| **CO7-espec** | este documento e as CO7-1 a CO7-8 |
| **CO7a** | o gabarito, num commit próprio |
| **CO7b** | o Python: o escudo no M-ARB, o peso da universalização, a culpa e a inveja no M-AFETO, e os testes |
| **CO7c** | o TS: o espelho, a paridade e o que se vê, que é o gesto, sem número (D-MM-8) |
| **CO-bancada** | o plano de análise de "a cooperação emerge e cresce com o `k`?", antes de qualquer run |

**A ordem:** depois da CO6 na `main`.

## 8. As decisões (PROPOSTAS, para o Matheus; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **CO7-1** | o que o escudo lê | **só o que o pet vê**: o outro indo para a comida e com aflição visível | pela fome real do outro, o escudo fica exato, mas o pet passa a "saber" o estado do outro pelo que lhe é proibido, contra o G-RECEPTOR-SOCIAL |
| **CO7-2** | quando o escudo liga | **acima de um limiar de `k`**, PROPOSTO: 1/4 de S, o teto da criança | desde o bebê, o escudo vale antes de o pet ter convivência; só no adulto, a CO7 quase não aparece nos primeiros dias |
| **CO7-3** | a exceção do próprio piso | **o escudo não vale com o próprio pet em privação** | sem a exceção, um pet pode passar fome por dever, o que nem Kant pede e o jogo não quer |
| **CO7-4** | o peso da universalização | **`mul(k, w_univ)`, com o teto na urgência mais forte**; `w_univ` PROPOSTO | sem o teto, o dever vira compulsão e apaga a personalidade; peso alto demais iguala todos os pets |
| **CO7-5** | a universalização com os atos de hoje | **entra como forma, dizendo que se reduz à tabela da CO3** | esperar os atos novos deixaria a CO7 sem o teste; fingir que traz mais do que a tabela seria afirmar sem base |
| **CO7-6** | a culpa e a inveja | **no M-AFETO, pela valência, com o peso por faceta** | no corpo, reabre a D-MM-10; sem elas, a CO7 só proíbe e não empurra para o bem |
| **CO7-7** | o que se vê | **o gesto** (o pet que hesita e deixa a comida, o que consola), **sem número** (D-MM-8) | um número convida a otimizar e contraria a D-MM-8 |
| **CO7-8** | a ordem | **depois da CO6 na `main`**, com a CO-bancada antes de qualquer run | junto com a CO6, não dá para separar o efeito do sinal do efeito do uso (a CO6-1) |
