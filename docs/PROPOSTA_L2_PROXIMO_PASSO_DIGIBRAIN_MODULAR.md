# Proposta — o próximo passo do longe depois da avaliação da L-2 (2026-10-29)

Autor: o C (Claude Code, Opus 5.5), a pedido do Gerente (relato do Gerente, 2026-10-29), com a aprovação do Matheus para uma leitura
curta. **Status: PROPOSTA, só papel.** Nenhuma vida, nenhuma semente, nenhuma faixa, nenhuma mudança no cérebro, no motor, no corpo ou no
mundo. As decisões da seção 5 são do Matheus.

**As regras deste documento:**
- **Todo número sai de um artefato,** com o caminho ao lado:
  - **[aval]**: `artifacts_v2_digibrain_prototipo/l2/avaliacao/resultado.json` e a seção 12 do
    `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`;
  - **[leit]**: `artifacts_v2_digibrain_prototipo/l2/avaliacao_leitura.json` (as S-1 a S-6 e as trocas por vencedora);
  - **[prox]**: `artifacts_v2_digibrain_prototipo/l2/proximo_passo_leitura.json`, deste PR. O `experiments/leitura_l2_proximo_passo.py`
    só relê as 12 partes da avaliação pelo índice (o sha256 conferido) e faz a diferença pareada por unidade (base, semente), com o IC
    do t (`metrics.ic_t`, o do adendo 4). Nenhuma vida roda.
- **Os três artefatos acima vêm do PR #454,** que ainda não está na `main`: este PR entra depois dele.
- **[DADO]** é o que os artefatos mostram; **[CÓDIGO]** é leitura de código, sem execução; **[HIPÓTESE]** é aposta, a medir.
- **Todo valor novo é PROPOSTO e SEM FONTE.** Nenhuma afirmação de superioridade do modular nem de prontidão. A leitura é pós hoc e não
  muda nenhum critério da A5.4: o C-L2-1 e o C-L2-4 continuam não passando.

## 0. Em uma página

- **Por que a busca retomada perde para o chamar e o explorar** (seção 1): **em boa parte, ela não perde mais do que antes; a medida
  passou a contar a perda.**
  - No longe, o pet do M3\*+S chama a atenção e explora quase o mesmo número de vezes que o do M3\*: +1,5 e −1,3 por vida, em cerca de
    220 e 350 [prox].
  - As trocas da busca por essas unidades sobem bem mais: +3,7 pelo chamar e +6,6 pelo explorar, por vida [prox]. São, em grande parte,
    as mesmas escolhas do despertar. No M3\*, elas vinham depois de o reflexo já ter acabado a busca. No M3\*+S, a busca suspensa voltou e
    está em curso no despertar, e a escolha conta como troca.
  - O que muda de fato no comportamento: o pet faz 2,2 ações de comer a mais por vida [prox], e o dormir pelo sorteio troca 2,8 buscas
    a mais por vida [prox].
  - Pelo código, a busca retomada já está no teto da ativação, e a fome alta soma peso no chamar e no explorar [CÓDIGO].
- **Quanto da distância de 0,69 no C-L2-4 vem da seleção** (seção 2): **com os artefatos de hoje, não dá para separar** o efeito da
  seleção do efeito do mecanismo dentro das buscas suspensas. O que dá para dizer:
  - as buscas nunca suspensas do M3\*+S têm a mesma taxa das buscas do M3\* que o reflexo não cortou (0,733 e 0,734 no longe, e o mesmo
    nas outras quatro células com busca bastante);
  - logo, a comparação do C-L2-4 é entre dois grupos que o próprio reflexo define. Para separar, falta uma tabela por busca, que só um
    replay instrumentado das vidas daria.
- **Três opções** (seção 3): **P-1,** parar a L-2 e registrá-la como negativa; **P-2,** um replay descritivo, como o da L0, para a tabela
  por busca; **P-3,** uma espec nova contra o cochilo em serra.
- **A recomendação** (seção 4): **a P-1.** A chave `intencao_suspensa` fica no código, desligada. Os dois achados de medida ficam no
  registro, para a próxima espec. A P-2 fica guardada, sem custo de sementes.

## 1. Por que a busca retomada perde para o chamar e o explorar

### 1.1 O que os artefatos mostram [DADO]

Longe, o par primário (M3\* → M3\*+S), por vida (a média das 4 vidas da unidade), 450 unidades, a diferença com o IC95 do t [prox]:

| a medida | M3\* | M3\*+S | a diferença [IC95] |
|---|---|---|---|
| buscas trocadas pelo reflexo | 20,55 | 0 | −20,55 [−20,84; −20,26] |
| buscas trocadas por outra unidade (inclui o dormir pelo sorteio) | 5,14 | 18,41 | +13,27 [+13,03; +13,51] |
| buscas trocadas pelo dormir sorteado | 1,04 | 3,84 | +2,80 [+2,71; +2,90] |
| ações de chamar a atenção | 219,89 | 221,40 | +1,51 [+0,40; +2,63] |
| ações de explorar | 350,25 | 348,94 | −1,31 [−2,30; −0,33] |
| ações de comer | 85,75 | 87,92 | +2,17 [+1,59; +2,75] |
| ações de dormir | 631,75 | 629,76 | −1,99 [−2,71; −1,27] |
| reflexos do sono | 335,65 | 329,62 | −6,03 [−8,98; −3,09] |
| buscas começadas | 45,24 | 39,32 | −5,92 [−6,36; −5,48] |
| buscas em meta ou achou | 18,14 | 19,04 | +0,90 [+0,63; +1,18] |

**As trocas da busca por vencedora, por vida** [prox]:

| a vencedora | M3\* | M3\*+S |
|---|---|---|
| chamar a atenção | 1,54 | 5,24 |
| explorar um ponto lembrado | 1,07 | 3,93 |
| explorar vagando | 0,69 | 2,60 |
| explorar pelo cheiro | 0,71 | 2,57 |
| dormir (o reflexo e o sorteio, juntos) | 21,59 | 3,84 |

**O par descritivo (M0 → M0+S), no longe,** tem a mesma forma, sem a memória [prox]:
- as ações de chamar a atenção: −0,07 [−1,14; +1,01] por vida;
- as trocas da busca pelo chamar: de 2,16 a 6,00 por vida.

O M0 não tem a unidade do ponto lembrado. Logo, o padrão não depende dela.

### 1.2 A leitura

1. **A maior parte da subida é recontagem.** As trocas pelo chamar sobem 3,7 por vida, e as ações de chamar sobem 1,5 [prox]. Então
   cerca de 2,2 das 3,7 já aconteciam no M3\*, fora da busca (pelo menos 1,1, pelo limite superior do IC). No
   explorar, as trocas sobem 6,6 por vida, e as ações descem 1,3: tudo vem de escolhas que já aconteciam.
   - **O mecanismo da recontagem** [CÓDIGO, `digilab/digibrain/estado.py`]: no M3\*, o reflexo acaba a busca em "trocou" (`escolhida`),
     e no despertar não há intenção em curso. A escolha do despertar não é troca de nada.
   - No M3\*+S, a `cuidar_suspensa` devolve a busca à I\* antes do sorteio do despertar. Se o sorteio escolhe outra unidade, a busca acaba
     em "trocou" com essa vencedora.
   - **A medida do C-L2-1 conta as trocas.** Por isso ela passou a contar no despertar o que antes contava no reflexo. A espec
     (`docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md`, seção 7.3, escrita pelo C no #436) não previu isso.
2. **Por que a busca retomada perde o sorteio do despertar** [CÓDIGO, `digilab/digibrain/impulso.py`, `arb.py` e `config.py`]:
   - **a persistência já está no teto.** Com `tau_c` = Δ = 15, o C vai a S na primeira escolha. Então h = mul(`w_pers` = 4S, S) = 4S =
     `a_max`. Com a fome acima de cerca de 0,27 S, o inato da busca já é positivo (−17S/16 + 3 u_fome + S/4, sem o hábito), e a ativação
     fica no teto. O peso da busca retomada não passa de `a_max` + mul(g_exp, ε);
   - **a fome alta soma peso nos concorrentes.** Ela entra no chamar (2S × u_fome sem comida à vista) e no explorar (S/2 × u_fome sem
     comida). Na busca, já no teto, ela não soma mais. O sorteio é proporcional (`sortear_inteiro`): cada concorrente com peso tira uma
     fatia;
   - **o despertar acontece com a energia logo acima do limiar do reflexo** (`lambda_sono` = S/4). O dormir pelo sorteio tem o termo
     3S × u_energia, e o explorar tem −2S × u_energia. Por isso, logo depois do reflexo, o dormir sorteado vence parte das retomadas
     [HIPÓTESE, coerente com o DADO: +2,8 trocas pelo dormir sorteado por vida, e a S-4: em 86 % das retomadas, outro reflexo vem em
     até 2 decisões [leit]];
   - **o dormir pelo sorteio não suspende** (a espec, seção 2.1). Ele acaba a busca em "trocou", e o F sobe. A espec deixou esse caso de
     fora de propósito. Aqui o comportamento muda de fato: o dormir pelo sorteio (as ações de dormir menos os reflexos) sobe cerca
     de 4,0 por vida (−1,99 menos −6,03 [prox]).
3. **O que muda de fato:** o pet do M3\*+S faz 2,2 ações de comer a mais por vida no longe, começa 5,9 buscas a menos e fecha
   0,9 busca a mais em meta ou achou [prox]. Isso é coerente com o C-L2-2 (+0,0103 por episódio [aval]), sem dizer quanto dele vem
   da suspensão e quanto do aprendizado que ela muda.

**O que esta leitura não diz:** o peso de cada unidade em cada despertar, porque as urgências e os pesos de cada decisão não ficam nas
partes gravadas. Os números do item 2 são as constantes do `config.py`, e não valores medidos.

## 2. Quanto da distância de 0,69 no C-L2-4 vem da seleção

**A distância** [aval]: as buscas suspensas acabam em meta ou achou em 0,155, e as nunca suspensas em 0,840, somando os três lugares. No
longe, são 0,139 e 0,733 [leit].

### 2.1 O que dá para dizer com o que está gravado [DADO]

**As buscas nunca suspensas são as que o reflexo não alcançou, com ou sem a suspensão.** No braço sem a suspensão, as buscas que o reflexo
não cortou têm quase a mesma taxa das nunca suspensas do braço com ela [prox] [leit]:

| | sem a suspensão: as não cortadas pelo reflexo | com a suspensão: as nunca suspensas |
|---|---|---|
| M3\*, longe | 0,734 (44 443) | 0,733 (41 125) |
| M3\*, comedouro | 0,951 (22 641) | 0,948 (21 851) |
| M3\*, perto | 0,995 (13 377) | 0,995 (13 360) |
| M0, longe | 0,759 (52 707) | 0,757 (49 071) |
| M0, comedouro | 0,942 (28 540) | 0,941 (27 151) |

**O que isso mostra:**
- **o grupo de comparação do C-L2-4 é o mesmo nos dois braços:** a suspensão não o muda. A distância de 0,69 compara as buscas que o
  reflexo alcança com as que ele não alcança, e essa divisão já existe no M3\*;
- **no M3\*, as buscas alcançadas acabam todas no reflexo, sem meta,** porque a busca cortada termina ali. No M3\*+S, 14 % delas acabam
  em meta ou achou no longe [leit]. Mas a comparação com o M3\* também não é limpa: lá, o pet que acorda começa uma busca nova, que
  conta como outra busca;
- **pela unidade que não depende de como se conta a busca,** o pet do M3\*+S fecha 0,9 busca a mais por vida em meta ou achou, com 5,9
  buscas a menos [prox]. O C-L2-2, por episódio, é a medida que não sofre com isso, e ele passa [aval].

### 2.2 O que não dá para separar, e o que faltaria

**Não dá para separar,** dentro das buscas suspensas, quanto dos 86 % sem meta vem de elas serem as mais longas, as mais longe e as de
mais privação (a seleção), e quanto vem de a retomada perder o sorteio (o mecanismo). As 12 partes guardam só contagens por vida. As
vidas em disco (`vidas/*.jsonl`, fora do git) guardam o log do dono, e não as decisões.

**O que faltaria: uma tabela por busca,** saída de um replay instrumentado das vidas já gravadas (nenhuma semente nova), com, para cada
busca:
- o início, a idade (as decisões desde o começo) em cada corte, e o fim, com o motivo;
- a distância do pet à ração mais perto (do mundo, só para a leitura) no começo, em cada corte e no fim;
- a u_fome e a u_energia em cada reflexo e em cada despertar;
- em cada retomada: os pesos de todas as unidades no sorteio, a vencedora e se a persistência decidiu.

**A conta que ela permitiria:** a comparação por idade. Entre as buscas vivas na idade a, comparar as cortadas em a (suspensas) com as
não cortadas, por faixa de distância e de u_fome. E, depois da retomada, a chance de troca por decisão contra a das buscas nunca
suspensas na mesma idade. Sem critério: só leitura.

## 3. As opções

### P-1: parar a L-2 aqui e registrá-la como negativa

- **O que é:** o resultado da avaliação fica como está registrado: a suspensão não segue para o jogo (o C-L2-1 e o C-L2-4 não passam), e
  a parte (a) não entra (a A5.5).
- **No código:** a chave `intencao_suspensa` fica no código, desligada, sem mudança. A `main` já a tem, e com a chave desligada a vida
  sai byte a byte.
- **No registro:** o RESULTADO, o painel e o registro dizem "L-2 (b): negativa pelos critérios; o C-L2-2 passou, +0,0103 por episódio".
  Os dois achados de medida desta proposta (seções 1.2 e 2.1) ficam como lição para a próxima espec.
- **O longe** fica onde está: por episódio, cerca de 0,43 no M3\* [aval]; por ração, com o teto perto de 0,13. A frente segue para o
  hábito, pela ordem do Matheus ("longe primeiro, hábito depois").
- **O custo:** nenhum.
- **O custo de errar:** se a suspensão ajuda de fato e as falhas são sobretudo da medida (a recontagem e o grupo de comparação), um
  mecanismo que subiu a taxa por episódio fica desligado. O erro é reversível: o código e a avaliação ficam guardados.

### P-2: um replay descritivo, como o da L0, para a tabela por busca

- **O que é:** rejogar só as vidas M3\* e M3\*+S do longe da avaliação (3 600 vidas) com um leitor instrumentado. Ele grava a tabela da
  seção 2.2 e os pesos de cada despertar.
- **O que não muda:** o cérebro, o motor, o mundo e o corpo. O leitor é código novo só em `experiments/`.
- **O plano:** uma seção nova do plano de análise, antes do replay. Ela diria que a leitura é descritiva, sem critério, e que nada se
  ajusta por ela.
- **As sementes:** nenhuma nova. A faixa da avaliação (67303, 67404 e 67505) é tocada pelo replay, e não reusada, como a 66xxx na L0
  (PL-1 do #434).
- **O custo:** o código do leitor e, pela parede da avaliação (0,88 s por vida [aval]), cerca de 53 min de vida num processo, ou cerca de
  13 min com 4, mais o custo do registro.
- **O que ela resolve:** responde à pergunta 1 no nível da decisão e à pergunta 2.
- **O custo de errar:** se a decisão depois dela for a P-1 de qualquer jeito, é um dia gasto. Há também o risco de ler a avaliação como
  calibração. A regra o proíbe: qualquer variante pensada a partir desta tabela vai para uma faixa nova.

### P-3: uma espec nova, a L-2 (b2), contra o cochilo em serra

- **O que é:** duas mudanças possíveis, atrás de uma subchave nova e desligada:
  - **a retomada espera a energia sair da faixa do reflexo:** a suspensa só volta com a leitura da energia em `lambda_sono` + m, com m =
    S/8 (PROPOSTO, SEM FONTE). Antes disso, ela segue suspensa, e o `n_susp` não conta;
  - **o dormir pelo sorteio também suspende,** quando há uma intenção de comer em curso ou recém-retomada.
- **As medidas, refeitas antes de qualquer run:** o C-L2-1 contaria as trocas por decisão em que a busca está em curso, e não por busca.
  O C-L2-4 compararia as suspensas com as não cortadas da mesma idade (a tabela da P-2, que viria antes).
- **O caminho:** o gabarito, o código, o adendo do plano, a faixa nova e uma avaliação inteira. A última custou cerca de 5 h 17 min
  [aval].
- **O custo de errar:** mais uma rodada inteira numa célula limitada pelo sono: na L0, o pet do longe fica acordado em 52 % das decisões
  da janela (a seção 10 do RESULTADO). O ganho do
  C-L2-2 foi de 0,0103 por episódio. Há também o risco de prender o pet perto do sono com uma meta guardada.
- **A origem:** as duas mudanças nasceram de ler esta avaliação. Ficam declaradas como pós hoc na origem; por isso, a faixa precisa ser
  nova.

### A comparação

| | muda o cérebro | vidas | sementes novas | o que responde | o custo de errar |
|---|---|---|---|---|---|
| **P-1** | não | nenhuma | não | nada novo; fecha a L-2 | um mecanismo útil desligado (reversível) |
| **P-2** | não (leitor em `experiments/`) | replay de 3 600 | não | as perguntas 1 e 2, por decisão | um dia, se a decisão não mudar |
| **P-3** | sim (subchave nova, desligada) | uma avaliação inteira | sim | se a (b2) move o longe | uma rodada inteira numa célula limitada pelo sono |

## 4. A recomendação

**A P-1:** parar a L-2 aqui, registrá-la como negativa pelos critérios e seguir para o hábito.
- **Os critérios foram fixados antes, e dois falharam.** A leitura desta proposta explica em parte as falhas, mas não as desfaz, e nada
  aqui muda a A5.4.
- **O ganho que passou é pequeno** (+0,0103 por episódio) **e num lugar limitado pelo sono e pelo cenário.** A P-3 gastaria uma rodada
  inteira para mover uma célula cujo teto não é a decisão.
- **Os dois achados de medida têm valor fora da L-2:**
  - contar as trocas por intenção muda quando a intenção pode voltar;
  - comparar com as "nunca interrompidas" seleciona pelo próprio evento.
  Eles vão para o registro como lição para qualquer espec futura de intenção.
- **A P-2 fica guardada,** sem custo de sementes, para quando o longe voltar.

**Se o Matheus quiser saber o porquê antes de fechar,** a P-2 é barata e não toca o cérebro.

## 5. O que precisa do Matheus

| # | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **LP-1** | o próximo passo do longe: P-1, P-2 ou P-3 | **P-1** | P-1 errada: um mecanismo útil desligado, reversível. P-2 à toa: um dia. P-3 errada: uma avaliação inteira e uma faixa nova numa célula limitada pelo sono |
| **LP-2** | registrar os dois achados de medida (a recontagem das trocas e o grupo de comparação selecionado pelo reflexo) como lição para as próximas especs de intenção | **sim** | sem o registro, a próxima espec de intenção pode repetir as duas medidas |
| **LP-3** | a chave `intencao_suspensa` fica no código, desligada, sem mudança | **sim** | tirá-la é uma mudança de código sem ganho; deixá-la custa só a leitura |

## 6. O que esta proposta não afirma

- **Não afirma** que a suspensão melhora o longe, nem que não melhora: o C-L2-2 passou, e o C-L2-1 e o C-L2-4 não passaram.
- **Não afirma** que o modular supera o A (o A11 não está na avaliação), nem que algum cérebro está pronto.
- **Não reabre** nenhum critério da A5.4. A leitura das seções 1 e 2 é pós hoc e descritiva.
