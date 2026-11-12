# PLANO DE ANÁLISE V3 — COOPERACAO, a bancada: a cooperação emerge e cresce com o peso dos deveres? (2026-11-12, CB-1 a CB-9 DECIDIDAS, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-12 ("Aprovo todas").** As decisões CB-1 a CB-9 (seção 11) estão DECIDIDAS, todas pela
recomendação. Os números continuam PROPOSTOS.
**Rodado em 2026-11-12 (CB4):** H-EMERGE e H-DOSE NÃO CONFIRMAM, H-REP INCONCLUSIVO POR PREMISSA, H-CUSTO CONFIRMA; o
descritivo está em `docs/futuro/cooperacao_bancada_resultado.md` (D-CB-15). **Nenhuma vida deste plano roda antes de cinco coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus" (feito);
2. a CO6 e a CO7 na `main` (`docs/ESPEC_V3_COOPERACAO_CO6.md` e `docs/ESPEC_V3_COOPERACAO_CO7.md`), com os testes G-ESCUDO,
   G-RECEPTOR-SOCIAL e G-PAR-CO7 verdes;
3. o código da CB1 na `main` (seção 9): o orquestrador, as medidas e as travas;
4. a fumaça e o piloto (CB2), com o custo medido e o N fixado pela regra da seção 6;
5. o registro da análise (seção 10), num commit empurrado antes da primeira vida principal.

**De onde vem:** o Matheus, em 2026-11-12, depois de ler o roteiro da cooperação: "Tá, então efetua o estudo da bancada enquanto roda
as outras especificações." A CO-bancada é a missão que a espec da CO7 (seção 7) e a proposta `docs/futuro/kant_cooperacao.md` (seção 6)
deixam para "antes de qualquer run". O código da CO6 e da CO7 corre em paralelo, na sessão "COOPERACAO: código da CO6 e depois da CO7".

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- **Nenhuma alegação de novidade.** As fontes são as da espec da CO7 e da proposta Kant (Alger e Weibull 2013, `10.3982/ecta10637`;
  Levine et al. 2020, `10.1073/pnas.2014505117`; Roemer 2010, `10.1111/j.1467-9442.2009.01592.x`; Alshiekh et al. 2018,
  `10.1609/aaai.v32i1.11797`; Hughes et al. 2018, arXiv 1803.08884, preprint), com o status que a busca do vault deu a cada uma.
- **Nenhum mecanismo novo.** O estudo só liga, desliga e escala o que a CO6 e a CO7 trazem. Uma regra que falte vira adendo, com o ok do
  Matheus, antes das vidas.

## 0. O que existe (os fatos que o desenho usa)

- **A CO3** (`digilab/cooperacao.py`, espelho `web/app/motor/cooperacao.ts`) é função do log e só mede: os atos (a disputa, "anti" com o
  outro abaixo do piso de fome; a contenção; o encostar, que vale 0 pela D-CO3-3), a pontuação e a reputação de *i* vista por *k*.
- **A CO6** põe na percepção a reputação de cada outro presente e o peso dos deveres `k`, que sobe a cada tick de encontro com quem tem
  reputação positiva, decai pela meia-vida da pontuação e tem teto por estágio (0, 1/4, 1/2 e 3/4 de S, do bebê ao adulto). Não muda a
  decisão (CO6-1).
- **A CO7** usa os sinais: o escudo (a ação proibida sai das candidatas acima do limiar de `k`, 1/4 de S, salvo na privação do próprio
  pet), o peso da universalização (`mul(k, w_univ)`, com teto na urgência mais forte) e a culpa e a inveja no M-AFETO.
- **A CO7-5 diz às claras:** com os atos de hoje, a universalização se reduz à tabela de sinais da CO3. **Por isso a medida primária
  deste plano não é a contagem de atos da CO3** (seção 3.1): medir a cooperação pela mesma tabela que o peso otimiza seria provar por
  construção.
- **O estágio** ainda vem da idade (`ConfigExpressao`): bebê até o dia 1, criança até o 3, adolescente até o 7. O `k` só existe a partir
  da criança.
- **Os atos são raros no mundo de hoje.** Na CO1 houve 2 disputas em 5 vidas (D-CO1-1), mesmo com o comedouro comum em três delas. O
  piloto (seção 6) mede as oportunidades antes de fixar o N.
- **O grupo do Python** roda hoje com o cérebro A (`lobos`) e o `instinto` (`experiments/exportar_gabarito_grupo.py`); o jogo usa o
  modular. Qual cérebro o estudo usa é a CB-2.

## 1. A pergunta e as hipóteses rivais, escritas antes

**A pergunta:** com o escudo, o teste da universalização e a culpa e a inveja ligados (a CO7), o pet passa a agir de modo pró-social com
o irmão, mais quanto maior o peso dos deveres `k`, e esse peso sobe mais com um irmão que retribui? Sem morrer de fome por dever e sem
ler o que se passa dentro do outro.

| hipótese | o que diz | o que a separa |
|---|---|---|
| **H-EMERGE** | a CO7 aumenta a parte das oportunidades em que o irmão aflito acaba comendo (a medida primária P1) | o braço CO7 contra o CO6 só, pareado por vida |
| **H-DOSE** | o efeito cresce com o `k`: k zero < k pela metade < k da espec | os três braços de dose, pareados |
| **H-REP** | o `k` sobe mais, e a P1 também, com um irmão que retribui do que com um que não retribui | o irmão com a CO7 contra o irmão sem ela |
| **H-CUSTO** | cooperar não leva o próprio pet à privação mais vezes (não inferioridade) | as horas abaixo do piso de fome, CO7 contra CO6 |
| **rival R-ESCUDO** | o "efeito" é só mecânico: o escudo tira a disputa, e nada de ativo aparece | as ablações: só o escudo, só a universalização, só o afeto |
| **rival R-IDADE** | o que cresce com o `k` é a idade (o teto sobe com o estágio), não o dever | a dose é por braço, na mesma idade, e não pela correlação com o dia |
| **rival R-NADA** | as oportunidades são tão raras que nenhuma leitura sai | a regra do N (seção 6); sem oportunidades, a leitura é INCONCLUSIVO POR PREMISSA |

## 2. O desenho

### 2.1 As vidas

- **Uma vida** é um grupo de dois pets do mesmo dono, nascidos juntos, por **8 dias** simulados (bebê, criança, adolescente e o começo
  do adulto), no mundo da CB-3.
- **O dono:** o atencioso, o mesmo para os dois (CB-4), com o cuidado só. O dono não ensina a cooperação: nenhum reforço sai do outro pet
  (a regra dos dois pets, CO-3).
- **O pareamento:** cada semente roda em todos os braços. O motor é determinístico: o mesmo mundo, o mesmo dono e o mesmo par até a
  primeira decisão que a chave muda. A diferença entre braços é por semente.

### 2.2 Os braços (por semente)

| braço | o que liga | para quê |
|---|---|---|
| **B0** | a cooperação medida e a CO6 (o sinal chega, ninguém usa) | a linha de base; pelo G-SEM-DECISAO-CO6, é a vida de hoje |
| **B1** | a CO7 inteira, nos dois pets | H-EMERGE |
| **D0** | B1 com o teto de `k` multiplicado por 0 | H-DOSE (o `k` nunca passa do limiar: o escudo e o peso nunca agem; só a culpa e a inveja) |
| **D½** | B1 com o teto multiplicado por 1/2 | H-DOSE |
| **B1-E** | só o escudo | R-ESCUDO |
| **B1-U** | só o peso da universalização | R-ESCUDO |
| **B1-A** | só a culpa e a inveja | R-ESCUDO |
| **R-** | B1 no pet A; o pet B no B0 (não retribui pela CO7) | H-REP, comparado ao B1 pelo lado do pet A |

O multiplicador do teto e as três subchaves das ablações são parâmetros da `ConfigCooperacao` de pesquisa, desligados no jogo. Se a CO7
não os tiver, a CB1 os pede como adendo de código à frente COOPERACAO, sem mudar o comportamento com o multiplicador 1 (o G2).

## 3. As medidas

Todas saem do log e do traço, depois da vida, sem mudar nada dentro dela.

### 3.1 A primária: o irmão aflito come (P1)

- **A oportunidade:** um tick de decisão em que os dois pets estão a até `r_escudo` da mesma comida madura, o outro mostra aflição visível
  (`emburrar` ou `chamar_atencao`) e o próprio pet não está em privação. É a mesma situação física em que o escudo vale, lida por quem
  mede, nos dois braços.
- **O desfecho:** dentro de `janela_p1` ticks (PROPOSTO: 4 decisões), **quem comeu aquela comida** foi o pet aflito.
- **P1 por vida** = desfechos a favor do aflito / oportunidades, a partir do dia 1 (a criança). Uma vida sem oportunidade não entra na P1
  e é contada à parte (R-NADA).
- **Por que esta:** é um resultado no mundo (quem comeu), e não o rótulo de um ato. O peso da universalização não lê "quem comeu depois";
  a P1 não é a tabela que ele otimiza.

### 3.2 As secundárias

- **P2, o bem da ilha:** o piso diário da felicidade lexicográfica do par (D-MM-14: o menor dos dois primeiro), média nos dias 1 a 8.
- **P3, o custo:** a fração dos ticks do próprio pet abaixo do piso de fome, dias 1 a 8 (H-CUSTO).
- **P4, os atos da CO3:** contenções, disputas "anti" e encostos por oportunidade. **Descritiva**, pela razão da seção 0.
- **P5, o `k`:** o `k` médio de cada pet por estágio e a fração do tempo acima do limiar do escudo (H-REP, H-DOSE).
- **P6, a personalidade preservada:** a distância entre os perfis de hábito dos dois pets (`digilab/metrics.py`, os do I5a), B1 contra
  B0. Descritiva: a CO7-4 teme que o dever iguale os pets.

### 3.3 Os ICs

IC de 95 % por bootstrap pareado por semente (10 000 reamostras, a semente do bootstrap fixa no registro), sobre a diferença por vida.

## 4. A regra de decisão, escrita antes

| hipótese | passa se | δ (PROPOSTO) |
|---|---|---|
| H-EMERGE | IC da diferença B1 − B0 na P1 todo acima de δ | 0,10 |
| H-DOSE | a inclinação da P1 em D0, D½, B1 (0, 1/2, 1), pareada, com IC todo acima de 0, e D0 ≤ D½ ≤ B1 nas médias | — |
| H-REP | IC de B1 − R- no `k` do pet A (P5) e na P1 do pet A todo acima de 0 | — |
| H-CUSTO | IC de B1 − B0 na P3 todo abaixo de ε | ε = 0,02 |

- **As leituras possíveis por hipótese:** CONFIRMA, NÃO CONFIRMA (o IC cruza o limiar) ou INCONCLUSIVO POR PREMISSA (menos de `n_min`
  vidas com oportunidade, seção 6).
- **R-ESCUDO** é lida pelas ablações, sem gate: se B1-E sozinho dá quase todo o efeito de B1 na P1 e B1-U e B1-A dão perto de zero, a frase
  é "o efeito vem do escudo, que é uma proibição, e não de um empurrão ativo".
- **Correções:** quatro hipóteses, cada uma com o seu gate e a leitura escrita como tal; nenhuma é escolhida depois.

## 5. As conferências (falham alto)

- O B0 sai byte a byte igual à vida sem a CO6 (o G-SEM-DECISAO-CO6, de novo, nas sementes do estudo).
- O G-ESCUDO conta zero atos proibidos fora da exceção do próprio piso, em toda decisão de B1 e B1-E.
- O D0 nunca tem `k` acima do limiar do escudo.
- O replay de 1 vida por braço refaz a assinatura.
- As medidas só leem o log e o traço (nenhuma lê o estado do motor durante a vida).

## 6. O piloto, o N e o custo

- **A fumaça:** as sementes dos testes (101…505) em todos os braços, para medir o custo por vida e conferir a seção 5.
- **O piloto:** 40 sementes da faixa **91101–91140**, só B0 e B1, para medir as oportunidades por vida e o desvio da diferença na P1. As
  vidas do piloto não entram na análise principal.
- **A regra do N** (fixada agora): o N é o menor de {80, 160, 320} sementes em que a meia largura esperada do IC de B1 − B0 na P1 fica ≤
  δ/2, com o desvio do piloto. Se nem 320 chega, o N fica 320 e a leitura avisa. **`n_min`:** 30 vidas com ao menos uma oportunidade em
  cada braço comparado.
- **Se o piloto der menos de 1 oportunidade por vida em média:** o estudo para antes das vidas principais, e a CB-3 (o mundo) volta ao
  Matheus com a recomendação de um mundo com mais escassez. Não se muda o mundo sem esse ok.
- **As sementes principais:** a partir de **91201**, na ordem, sem pular. A faixa 91xxx não aparece no registro nem nos planos até
  2026-11-12.
- **O custo:** medido na fumaça. Com até 4 processos (a máquina, 2026-10-30), 8 braços e o N do piloto. A CB2 grava o custo e, se a conta
  passar de 12 h, a CB-6 volta ao Matheus antes das vidas.

## 7. A leitura

- **A tabela:** uma linha por hipótese, com a média por braço, a diferença, o IC e a leitura.
- **As frases que a leitura pode escrever:** só as que a tabela sustenta, por exemplo "com os deveres ligados, o irmão aflito come a comida
  disputada em X % das vezes a mais (IC ...)". Frases de "o pet é kantiano" ou de "moral emergente" não entram.
- **A expectativa E-CB (escrita antes, sem valer como gate):** H-EMERGE e H-CUSTO passam; H-DOSE passa fraca, porque D0 ainda tem a culpa e
  a inveja; H-REP é a mais incerta, porque no mundo de hoje os encontros com reputação positiva dependem de atos raros; e o R-ESCUDO
  explica a maior parte do efeito, porque a universalização se reduz à tabela (CO7-5).

## 8. O que a análise grava

Em `experiments/runs/cooperacao_bancada/` (fora do git, como as runs de antes): o registro de cada vida, as medidas por vida
(`medidas.parquet`), o resumo (`resultado.json`) e o manifesto (o commit, os braços, as sementes, o custo). No repositório, só o
`resultado.json` e o descritivo `docs/futuro/cooperacao_bancada_resultado.md`.

## 9. As missões (cada uma num PR)

| missão | o quê | depende de |
|---|---|---|
| **CB0** | este plano | — |
| **CB1** | o orquestrador `experiments/run_v3_cooperacao_bancada.py`, as medidas P1 a P6 em `digilab/metrics.py` (ou num módulo próprio), os braços e as travas da seção 5, com testes nas sementes dos testes | a CO7 na `main` e a CB-2 |
| **CB2** | a fumaça e o piloto; o N pela regra da seção 6; o custo | CB1 |
| **CB3** | o registro da análise (seção 10), num commit antes da primeira vida principal | CB2 |
| **CB4** | as vidas principais e a análise; o resultado e o descritivo | CB3 |

## 10. O registro da análise

Antes da primeira vida principal, um commit grava em `docs/registro/` (a seção do mês): o commit do código, o N do piloto, as sementes, os
δ e ε, a semente do bootstrap, o mundo e o cérebro escolhidos. Depois desse commit, nada da seção 4 muda; uma mudança vira adendo com o ok
do Matheus, e as vidas já rodadas ficam registradas.

## 11. As decisões (DECIDIDAS pelo Matheus em 2026-11-12, todas pela recomendação; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **CB-1** | a medida primária | **P1, o irmão aflito come**, um desfecho no mundo; os atos da CO3 só descritivos | pelos atos da CO3, a H-EMERGE passa por construção (a universalização otimiza a mesma tabela, CO7-5) |
| **CB-2** | o cérebro | **o do jogo (o modular), se a CO7 o tiver no `Grupo` do Python; senão, o A (`lobos`)**, que é o do grupo hoje, e a leitura diz que é o A | o modular sem porte no grupo atrasa o estudo; o A sozinho responde por um cérebro que não é o do jogo |
| **CB-3** | o mundo | **o comedouro comum** (o lugar `comedouro` da CO1), que dá a disputa pela mesma comida; mais escassez só se o piloto der menos de 1 oportunidade por vida | o mundo aberto quase não tem oportunidade (D-CO1-1); escassez demais mede fome, não dever |
| **CB-4** | o dono | **o atencioso, o mesmo para os dois** | um dono relapso põe os dois em privação, onde o escudo não vale (CO7-3); donos diferentes misturam o efeito do dono |
| **CB-5** | a duração | **8 dias**, até o começo do adulto | menos não chega ao teto do adolescente; mais encarece sem estágio novo (o Mega não existe) |
| **CB-6** | os braços | **os oito da seção 2.2** | sem as ablações não se lê o R-ESCUDO; sem o R- não se testa a reputação |
| **CB-7** | os limiares | **δ = 0,10 na P1, ε = 0,02 na P3**, PROPOSTOS, SEM FONTE | δ pequeno pede N grande e acha efeitos sem importância; grande perde um efeito real |
| **CB-8** | o piloto e a regra do N | **40 sementes, B0 e B1, N em {80, 160, 320}** | sem piloto, o N é chute, e os atos raros podem deixar tudo inconclusivo |
| **CB-9** | o encostar | **segue valendo 0** (D-CO3-3, ainda aberta), e por isso fica fora da P1 e só no descritivo P4 | se a D-CO3-3 mudar depois, só o P4 muda; a P1 não depende dele |
