# A espec da L-2: a intenção de comer que fica suspensa no cochilo (DigiBrain modular, v13)

**O que é:** a especificação da opção L-2 da `docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md`, escolhida pela regra da etapa L0 (o #435) e
pelo PL-2. Só papel: nenhum código, nenhuma vida, nenhuma semente, nenhuma faixa reservada.

**Quem e quando:** o C (Claude Code, Opus 5.5), em 2026-10-29, a pedido do Gerente (relato do Gerente de 2026-10-29).

**O status:** PROPOSTA. Todo valor novo é PROPOSTO, e SEM FONTE salvo onde a linha diz. **Nada roda antes de o Matheus revisar esta espec.**
**As decisões da seção 9 (LS-1 a LS-7) são DECIDIDAS pelo Matheus em 2026-10-29,** como recomendadas.

**Os rótulos:** [DADO] é número de artefato no git; [CÓDIGO] é leitura do código da `main` (`983930d`); [HIPÓTESE] é o que falta medir.

## 0. Em uma página

- **O que os dados mostram** [DADO]: no longe, a busca pelo cheiro do M3\* é quebrada 25,7 vezes por vida. O reflexo do sono quebra
  80 % dessas buscas, e outra unidade, com ração a menos de R, quebra 20 %.
- **O que o código mostra** [CÓDIGO]: no reflexo, o M-ESTADO trata o dormir como qualquer escolha nova. A busca acaba como "trocou", a
  frustração F sobe, e ao acordar não há intenção nenhuma: a busca, se voltar, recomeça do zero.
- **A mudança, a parte (b) da L-2:** quando o reflexo do sono interrompe uma intenção de comer (a busca pelo cheiro ou a ida a uma comida
  vista), ela fica **suspensa**, e não trocada. Na primeira decisão sem o reflexo, ela volta como intenção em curso, com o compromisso de
  antes, e disputa o sorteio com a persistência de hoje. O sorteio não é forçado.
- **A saída:** a intenção suspensa acaba sem voltar se a fome passou, se o alvo sumiu, se uma comida boa apareceu na visão, ou se passou
  tempo demais suspensa (seção 3). Seis medidas mostram se o pet ficou preso (seção 3.2).
- **A parte (a), a histerese contra outra unidade, fica para depois**, por uma regra escrita aqui (seção 4).
- **Onde entra:** só no pacote `digilab/digibrain/`, atrás de uma subchave nova da `ConfigDigibrain`, desligada. O A, a v12, o
  `engine.py`, o motor e o mundo não mudam.
- **A avaliação** (seção 7): o M3\* contra o M3\* com a suspensão, pareados, numa faixa nova. O critério está fixado aqui, antes de
  qualquer run: o mecanismo age, o longe por episódio, o que não pode piorar no comedouro e no perto, e o pet que não fica preso.
- **O que esta espec não afirma:** que a L-2 conserta o longe, que o modular supera o A, ou que algum cérebro está pronto.

## 1. De onde vem

### 1.1 O que a L0 mediu [DADO]

A fonte é `artifacts_v2_digibrain_prototipo/longe_l0/l0.json` (o bloco `medidas.M3`, somado nos quatro donos, 200 vidas por lugar) e
a seção 10 do `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`. O "M3" do registro é o M3\* da leitura: o M3 com as subchaves
`cheiro_inato` e `intencao_cheiro`.

**As buscas pelo cheiro (`comer/cheiro`) trocadas:**

| | comedouro | perto | longe |
|---|---|---|---|
| buscas trocadas | 513 | 22 | **5 142** |
| por vida | 2,6 | 0,1 | **25,7** |
| quebradas pelo reflexo do sono | 363 | 10 | **4 096 (80 %; 20,5 por vida)** |
| por outra unidade, com ração a menos de R | 150 | 11 | **1 042 (20 %; 5,2 por vida)** |
| para comer (não é quebra) | 0 | 1 | 3 |

**As vencedoras das 1 042 do longe que não são o reflexo:**
- explorar, 477: o cheiro 153, o lugar lembrado 197 e o vagar 127;
- chamar a atenção, 330;
- dormir pelo sorteio, 222;
- outras, 13: emburrar 9, brincar 5, menos as 3 de comer, que não são quebra.

**As intenções de ir a uma comida vista (`comer/comida`) trocadas:** 935 no longe, 706 delas pelo reflexo do sono. No comedouro, 480 e
339; no perto, 104 e 61.

**O andado** (M-L3, os episódios de fome do longe, na janela): o episódio que não fecha anda 0,15 passo líquido em direção ao alvo, na
mediana, contra o n_min de 5 de que precisaria. Ele passa 52 % das decisões da janela acordado.

**A ressalva da L0:** a fração de quebra é alta em todo lugar (100 % no comedouro). O que separa o longe é a contagem.

### 1.2 Como o código produz isso [CÓDIGO]

- **O reflexo** (`digilab/digibrain/arb.py`, `Arbitragem.escolher`): com a leitura da energia abaixo de `lambda_sono` (S/4), a escolha é
  dormir, sem sorteio.
- **A troca** (`digilab/digibrain/estado.py`, `EstadoDinamico.escolhida`): o dormir é uma unidade sem alvo e não abre intenção. A
  intenção em curso acaba em `_acabar("trocou", False)`, e a frustração F sobe (`k_F`).
- **O dormir dura uma decisão** (`digilab/policy.py`, `efeito_da_acao_do_pet`): o pet dorme no intervalo em que escolheu dormir. Na
  decisão seguinte, o reflexo volta a valer se a energia ainda estiver abaixo de S/4.
- **A persistência já está no teto:** com `tau_c` = 15 ticks e o passo de 15 ticks, o ganho `k_C` é S, e o compromisso C vai a S na
  primeira decisão da intenção. A persistência é `h = mul(w_pers, C)` = 4S, que é o `a_max`. A intenção em curso já tem a ativação
  máxima. **A busca perde quase só para o reflexo,** que fica fora do sorteio.
- **Ao acordar, não há intenção.** Se o sorteio escolhe a busca de novo, ela abre outra intenção, com a contagem de decisões do zero e a
  elegibilidade nova.

**[HIPÓTESE] O cochilo em serra.** O reflexo não tem histerese própria: o pet acorda assim que a energia passa de S/4. Andar gasta
energia, e o pet pode voltar ao reflexo uma ou duas decisões depois. Com a busca trocada a cada cochilo, cada volta recomeça. A
contagem alta do longe combina com isso, mas a duração dos cochilos não foi medida. A medida S-4 (seção 3.2) a mede.

## 2. O mecanismo: a parte (b)

### 2.1 O que fica suspenso

- **Os tipos que suspendem** (PROPOSTO, a decisão LS-2):
  - a busca pelo cheiro, `comer/cheiro` (só existe com `intencao_cheiro`);
  - a ida a uma comida vista, `comer/comida`.
- **O que não suspende:** brincar com a bola e explorar o lugar lembrado. Elas continuam acabando em "trocou" no reflexo, como hoje.
- **O que suspende:** só o reflexo do sono. O dormir escolhido pelo sorteio continua sendo uma troca. Ele é escolha do cérebro, e não
  interrupção do corpo, e entra na parte (a), se ela vier.

### 2.2 O estado novo no M-ESTADO

Só com a subchave:
- `suspensa`: a intenção suspensa (o mesmo dicionário da I\*: a chave, o C, o `n_sp`, a distância `d`, o início, a elegibilidade `e`, o r
  somado e o `n`), ou nenhuma;
- `n_susp`: as decisões de reflexo que ela já passou suspensa, **somadas na vida dela** (não zera ao voltar);
- as contagens `suspensas`, `retomadas` e os fins novos, "expirou", "saciou" e "superada".

Há no máximo uma intenção em curso ou uma suspensa, nunca as duas. A suspensa não dá persistência: `h` só existe para a I\*.

### 2.3 A ordem dentro da decisão

A ordem de hoje no `DigiBrain.agir` (`digilab/digibrain/adapt.py`) é: M-SENS, M-AFETO, M-ESTADO (o contexto), M-MEM, M-IMPULSO, M-ARB e
M-ESTADO (a escolhida). A suspensão acrescenta um passo e muda um:

1. **O reflexo, uma conta só.** O teste `energia < lambda_sono` sai do `Arbitragem.escolher` para uma função do M-ARB (`reflexo(sens)`).
   O M-ADAPT a chama uma vez, depois do M-AFETO, e passa o mesmo valor ao M-ESTADO e ao M-ARB. A conta é a de hoje, sem rng.
2. **Novo: o cuidado da suspensa** (`EstadoDinamico.cuidar_suspensa(sens, afeto, reflexo)`), antes do contexto. Com uma intenção
   suspensa, na ordem:
   - **com o reflexo** (o pet segue dormindo): `n_susp += 1`, e confere os fins 1 a 3 da tabela da seção 3.1. Nenhum fim: segue
     suspensa;
   - **sem o reflexo** (o pet acordou): confere os fins 1, 2, 4 e 5. Nenhum fim: **a retomada**. A I\* volta a ser a suspensa, com o C, o
     `n_sp` e a distância de antes (o pet não andou dormindo), e conta uma retomada.
   As intenções que acabam aqui vão ao P2 (o crédito, seção 2.4) e ao registro, como as do `escolhida`.
3. **O contexto, o M-MEM, o M-IMPULSO e o M-ARB,** como hoje. A intenção retomada recebe a persistência `h` no contexto e disputa o
   sorteio como qualquer I\*. **A retomada não força a escolha** (a decisão LS-3): se o sorteio escolher outra unidade, a intenção acaba
   em "trocou", como hoje.
4. **A escolhida, com uma regra a mais:** com o reflexo, uma I\* de um tipo que suspende passa a `suspensa`, com `n_susp = 1`, e não
   acaba. O F não sobe, e nada vai ao P2. Com o reflexo e uma I\* de outro tipo, ou sem o reflexo, é a regra de hoje.
5. **A busca guardada no "achou"** (a opção composta da DX-4) não muda: ela vive uma decisão só, e o reflexo nessa decisão a entrega como
   hoje.

### 2.4 O crédito (o P2)

- **A intenção suspensa é a mesma opção.** Ela é entregue ao P2 uma vez, quando acaba, por qualquer fim, com a elegibilidade `e` da
  decisão que a começou.
- **O r dela** soma só as consequências das decisões dela. As decisões de dormir no meio são opções de uma decisão, com o crédito delas,
  como hoje.
- **Os fins sem crédito novo:** os fins "expirou", "saciou" e "superada" entregam a opção como os fins sem a meta de hoje.

### 2.5 O que o cérebro lê

- **Só o que já lê.** A suspensão lê a energia (o reflexo), a urgência da fome, se há cheiro (`direcao_cheiro != 0`) e os `vistos`.
- **O G-SEM-DIRECAO continua valendo:** o cérebro não lê a direção do cheiro, só se ela existe.
- **Nenhuma rng nova.** O M-ESTADO segue sem rng; a única chamada continua sendo a do sorteio do M-ARB.

## 3. A saída: quando a intenção suspensa acaba

### 3.1 Os fins

O custo de errar é prender o pet a uma meta errada ou velha. Cada fim tem um motivo próprio no registro, para a medida da seção 3.2.

| # | o fim | quando | com o reflexo | ao acordar | o F | o valor (PROPOSTO) |
|---|---|---|---|---|---|---|
| 1 | **saciou** | a urgência da fome abaixo de `lambda_retomar` | sim | sim | não sobe | `lambda_retomar` = S/4, o mesmo valor do `lambda_busca` do M-MEM (a pista da fome) |
| 2 | **sumiu** | a busca: sem cheiro e sem comida boa na visão. A ida: a comida-alvo fora dos `vistos` | sim | sim | sobe, como hoje | nenhum |
| 3 | **expirou** | `n_susp` passa de `n_suspensa_max` | sim | — | não sobe | `n_suspensa_max` = 6 decisões, o mesmo valor do `n_desiste_cheiro` |
| 4 | **achou** (só a busca) | uma comida boa na visão ao acordar | — | sim | não sobe (a decisão de 2026-10-26) | nenhum; é o "achou" da DX-4, com a opção composta |
| 5 | **superada** (só a ida) | outra comida boa na visão, mais perto que a comida-alvo | — | sim | não sobe | nenhum |

**As escolhas atrás da tabela** (PROPOSTAS, SEM FONTE):
- **A fome satisfeita** quase não acontece dormindo, porque a fome sobe no sono. O fim 1 existe para o caso em que o pet acorda saciado
  por outra via; ele usa o limiar da pista do M-MEM, para não criar número novo.
- **O tempo:** a suspensão dura no máximo a paciência da própria busca (`n_desiste_cheiro` = 6), somada na vida da intenção. A soma
  limita o cochilo em serra: uma intenção que volta e cai de novo no reflexo não vive para sempre. A busca já acaba sozinha em "desistiu"
  depois de 6 decisões acordada (`n`), e a suspensão não mexe nessa contagem.
- **O F:** os fins pelo corpo (expirou, saciou) e pela comida que apareceu (achou, superada) não contam como fracasso. O "sumiu" conta,
  como hoje. Isso importa porque o F entra no explorar com peso S/2: um F que sobe a cada cochilo empurra o pet a vagar depois de acordar
  (a decisão LS-5).
- **Os campos novos** ficam na `ConfigDigibrainInatos`, no módulo `estado` do `CAMPOS_POR_MODULO` (`digilab/digibrain/ganchos.py`):
  `n_suspensa_max` e `lambda_retomar`. Os dois têm o valor de um campo que já existe, e a espec propõe não calibrá-los (a decisão LS-4).

### 3.2 A medida que mostraria o pet preso

Todas por vida, por lugar e por braço, a partir do registro da decisão (os motivos), sem medida nova no `metrics.py` além das que o plano
pedir:

| # | a medida | o que mostraria o pet preso |
|---|---|---|
| **S-1** | a duração das suspensões (decisões de reflexo somadas) e a fração que acaba em "expirou" | muitas expirando: o pet guarda metas que o corpo não deixa cumprir |
| **S-2** | o fim das intenções retomadas (meta, achou, sumiu, desistiu, trocou, saciou, superada, expirou) contra o fim das que nunca foram suspensas | as retomadas acabando em meta ou achou bem menos que as outras: a meta retomada é velha |
| **S-3** | o andado líquido das intenções retomadas em direção à ração mais próxima (como o M-L3) | andado ≤ 0: o pet volta a andar para o lugar errado |
| **S-4** | as retomadas seguidas de outro reflexo em até 2 decisões (o cochilo em serra) | muitas: o pet acorda, anda um passo e dorme de novo, sem chegar |
| **S-5** | a exaustão e a privação de fome por vida, as medidas `exaustao` e `privacao` que o orquestrador do protótipo já grava (`LIMIAR_EXAUSTAO` = 0,25, `LIMIAR_PRIVACAO` = 0,15) | sobe: a retomada gasta o corpo que o reflexo protegia |
| **S-6** | nas retomadas, a fração em que a sonda `sem_persistencia` muda a escolha | só leitura: diz quanto a volta depende da persistência, e não do inato |

## 4. A parte (a), a histerese contra outra unidade: depois

**A recomendação:** a (a) não entra junto com a (b). O argumento:

1. **O tamanho:** a (a) atacaria 1 042 das 5 142 buscas trocadas do longe (20 %, 5,2 por vida). A (b) ataca 4 096 (80 %, 20,5 por vida)
   e mais 706 idas a uma comida vista.
2. **Nem toda troca por outra unidade é erro.** As vencedoras do longe são o explorar (477, e 153 delas vão para o cheiro, a mesma
   direção da busca), o chamar a atenção (330), que com fome e sem comida à vista é a outra forma de comer, porque chama o dono, e o
   dormir pelo sorteio (222), com a energia baixa. Uma margem contra todas suprimiria também essas, no comedouro e no perto.
3. **O mecanismo seria maior.** A intenção já está no teto da ativação (seção 1.2). Uma margem precisaria de um termo novo depois do
   `phi`, no M-ARB e nas sondas, e de um número novo, o m, que pediria calibração. A (b) não tem magnitude nova.
4. **A identificação:** com as duas juntas, uma mudança no longe não diz qual parte agiu. A (b) sozinha deixa a S-6 e a contagem por
   motivo atribuírem o efeito.

**A regra para a (a) entrar** (PROPOSTA, SEM FONTE; aplicada na leitura da avaliação da (b), seção 7):
- a (b) passa o C-L2-1 (o mecanismo age) e o C-L2-3 (não piora); **e**
- no longe do braço com a (b), as buscas trocadas por outra unidade, com ração a menos de R, ficam acima do dobro das do comedouro no
  mesmo braço; **e**
- o C-L2-2 não mostra melhora no longe.

Sem as três, a (a) não é proposta. Com as três, a (a) volta ao Matheus como espec própria, com o m e a calibração.

## 5. Onde entra e o que não muda

**Onde entra:**
- **a subchave:** `ConfigDigibrain.intencao_suspensa: bool = False` (PROPOSTO). Só vale com `ligada`. Sem `intencao_cheiro`, só a ida a
  uma comida vista suspende. Sem `persistencia` (o M3-sp), a intenção volta sem o `h`, e a suspensão vale do mesmo jeito;
- **os módulos:** o M-ESTADO (`estado.py`: o estado novo, o `cuidar_suspensa`, a regra do `escolhida`), o M-ARB (`arb.py`: a função
  `reflexo`, a mesma conta) e o M-ADAPT (`adapt.py`: a ordem da seção 2.3, o crédito e o registro dos fins novos);
- **a configuração:** a subchave na `ConfigDigibrain` e os dois campos na `ConfigDigibrainInatos` (`digilab/config.py`), com o status e a
  fonte em cada linha;
- **o registro da decisão:** com a subchave, o motivo ganha `suspensa` (a chave, o `n_susp`) e os fins novos. Desligada, nenhum campo
  novo aparece no estado interno nem no motivo.

**O que não muda:**
- **o cérebro A** (`digilab/policies/lobos.py`) e a v12. O modular só importa o `div_arred` e o `leitura_receptor`, que não mudam;
- **o `digilab/engine.py`** (o sha em `ENGINE_SHA256_V0`), **o motor** (`mundo.MotorMundo`, `motor_corpo`), **o mundo** e o campo do
  cheiro. O PL-5 vale: o M-L1 não deu a evidência que a L-1 pediria;
- **o corpo** (`corpo.py`) e o reflexo do sono: o limiar `lambda_sono` e a conta continuam os mesmos;
- **as medidas por vida que já existem** no orquestrador.

**O byte a byte (o G2 da subchave):**
- **antes do código,** num commit próprio, um gabarito novo das vidas do modular com as subchaves do cheiro ligadas (os braços de
  `SUBCHAVES_CONSERTO`, com as sementes dos testes), gravado com o código da `main`. O gabarito de hoje
  (`tests/gabaritos/digibrain_modular_de_hoje.json`) só cobre os braços com o cheiro desligado, e o M3\* é o braço que a L-2 muda;
- **com `intencao_suspensa` desligada,** os dois gabaritos saem iguais, byte a byte: o log, o estado interno do cérebro e as medidas.

**A web:** o cérebro modular ainda não está no jogo (`web/app/motor/digibrain.ts` é só a leitura do painel do A). A suspensão entra no
TS com o porte da v13, atrás da mesma chave, com o G-PAR. Antes disso, nada muda no jogo.

**O que muda no jogo, quando a v13 chegar:** o pet que sai atrás da comida e cochila no caminho volta a ela ao acordar, se ainda estiver
com fome e a comida ainda estiver lá.

## 6. Os testes de mecanismo (antes de qualquer vida)

| # | o teste | o que confere |
|---|---|---|
| T-L2-1 | o byte a byte | desligada, os dois gabaritos da seção 5 |
| T-L2-2 | a suspensão | um reflexo com uma busca em curso: nenhum "trocou", o F igual, a `suspensa` com a busca e `n_susp` = 1, nada ao P2 |
| T-L2-3 | a retomada | a primeira decisão sem o reflexo: a I\* é a suspensa, com o C, o `n_sp`, o `n` e o início de antes, e o `h` dela no contexto |
| T-L2-4 | os cinco fins | cada fim da seção 3.1 num cenário próprio, com o motivo, o F (sobe só no "sumiu") e a entrega ao P2 uma vez |
| T-L2-5 | a soma do tempo | suspensa, retomada e suspensa de novo: o `n_susp` não zera, e o "expirou" vem na decisão `n_suspensa_max + 1` |
| T-L2-6 | o crédito | a opção entregue tem a elegibilidade da decisão que a começou e o r só das decisões dela, sem os cochilos |
| T-L2-7 | o que não suspende | brincar, explorar o lugar e o dormir pelo sorteio acabam em "trocou", como hoje |
| T-L2-8 | o G-SEM-DIRECAO e a rng | o cérebro só lê `direcao_cheiro != 0`; o M-ESTADO não recebe rng; a única chamada é a do M-ARB |
| T-L2-9 | o reflexo extraído | o `reflexo(sens)` dá o mesmo valor que o teste de hoje em todas as decisões dos gabaritos |

## 7. A avaliação: a medida antes e depois, e o critério

Fixado aqui, antes de qualquer run. **Sem faixa de sementes:** a 64xxx e a 66xxx estão gastas para uso confirmatório. A faixa é pedida
ao coordenador quando o plano existir. O plano é um adendo ao `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, commitado antes da
primeira vida, e repete estes critérios sem mudá-los.

### 7.1 O desenho

- **A pergunta:** a suspensão diminui as buscas quebradas no longe e aumenta o fechamento por episódio no longe, sem piorar o comedouro,
  o perto e o corpo?
- **Os braços:**
  - **o par primário:** o M3\* de hoje (as subchaves do cheiro ligadas, como na reavaliação) e o M3\*+S (o mesmo, com
    `intencao_suspensa`);
  - **o par descritivo** (a decisão LS-6): o M0 e o M0+S, para ver a suspensão sem o aprendizado. Sem critério;
  - **o A11 não entra.** Esta avaliação compara o modular com e sem a mudança, e não o modular com o A.
- **As células:** as 12 de hoje (4 donos × 3 lugares). Nenhuma célula nova (o PL-4).
- **O pareamento:** as duas vidas de cada par têm a mesma semente. A rng do ambiente é separada da de política, e o mundo é o mesmo nas
  duas até o pet agir diferente.
- **O número de unidades:** pelo poder, no plano, com a variância das vidas M3\* do piloto do conserto (a seção 7 do RESULTADO) ou de um
  piloto na faixa nova. A 66xxx não entra nem nessa conta.
- **A calibração:** nenhuma, se o Matheus aceitar os dois valores emprestados (a decisão LS-4).
- **A análise:** a diferença pareada por unidade, com o IC95 pelo t sobre as unidades, como no adendo 4. Estimativa com intervalo; nada
  além dos critérios abaixo.

### 7.2 As medidas

| | a medida | o lugar | o papel |
|---|---|---|---|
| **antes e depois** | as buscas trocadas por vida, com o motivo (o reflexo, outra unidade) | os três | o mecanismo (C-L2-1) |
| | as buscas que acabam em "expirou", por vida | os três | o mecanismo (C-L2-1) e o pet preso (C-L2-4) |
| | a taxa de fechamento **por episódio** (a do G-MVP-EP) | o longe | o efeito (C-L2-2) |
| | a taxa de fechamento **por ração** | o longe | relatada, com o teto de cerca de 0,13 declarado; sem critério (o PL-3) |
| | as taxas por episódio e por ração | o comedouro e o perto | não pode piorar (C-L2-3) |
| | a exaustão e a privação de fome (S-5) | os três | não pode piorar (C-L2-3) |
| | as S-1 a S-4 e a S-6 | os três | o pet preso (C-L2-4) e a leitura |
| | as M-L2 e M-L3 da L0, refeitas | o longe | descritivas |

### 7.3 Os critérios (PROPOSTOS, SEM FONTE)

| # | o critério | passa se |
|---|---|---|
| **C-L2-1** | o mecanismo age | no longe do par primário, as buscas trocadas mais as expiradas, por vida, caem pelo menos à metade da média do M3\*, e o IC95 da diferença pareada fica abaixo de 0 |
| **C-L2-2** | o longe por episódio | o limite inferior do IC95 da diferença pareada (M3\*+S − M3\*) na taxa por episódio do longe fica acima de 0 |
| **C-L2-3** | não piorar | no comedouro e no perto, por episódio e por ração, o limite inferior do IC95 da diferença pareada fica acima de −0,03; e, nos três lugares, o limite superior da diferença na exaustão e na privação (S-5) fica abaixo de +0,02 |
| **C-L2-4** | o pet não fica preso | no M3\*+S, no máximo 25 % das suspensões acabam em "expirou" (S-1), e a fração de retomadas que acaba em meta ou achou não fica mais de 0,10 abaixo da fração das buscas nunca suspensas (S-2) |

**Como se leem juntos:**
- **o C-L2-3 é uma conjunção:** todas as comparações dele têm de passar. Por isso não leva correção de multiplicidade (a regra da
  interseção-união; SEM FONTE verificada no repositório);
- **a suspensão só segue para o jogo** com o C-L2-1, o C-L2-3 e o C-L2-4. O C-L2-2 diz se o longe melhorou; sem ele, a suspensão age mas
  não conserta o longe, e a leitura volta ao Matheus com a regra da seção 4;
- **o C-L2-1 pede a metade** porque o reflexo quebra 80 % das buscas trocadas: com a suspensão perfeita, sobram as 20 % por outra
  unidade e as expiradas. A metade deixa folga para as expiradas, sem aceitar só a troca de nome de "trocou" para "expirou";
- **as margens −0,03 e +0,02** são PROPOSTAS, SEM FONTE. O plano diz o poder para elas.

## 8. O que esta espec não afirma

- **Que a L-2 conserta o longe.** A L0 diz onde a busca quebra, e não quanto o fechamento sobe quando ela não quebra. O pet ainda dorme
  cerca de 45 % da janela no longe, e a suspensão não devolve esse tempo.
- **Que o modular supera o A.** O A11 não está na avaliação.
- **Que algum cérebro está pronto.** A prontidão é a da seção 5.6 do plano, e esta espec não a toca.
- **Que o mecanismo é novo.** A intenção que dura várias decisões já é uma opção no sentido de Sutton, Precup e Singh (1999),
  `10.1016/s0004-3702(99)00052-1` (VERIFICADA por título e metadados, como na seção 4.4 da espec do modular): o formalismo, e não esta
  regra. Para a suspensão no sono e para os valores, SEM FONTE.

## 9. O que precisa do Matheus

Propostas pelo C, com a recomendação primeiro. **O Matheus decidiu as sete em 2026-10-29, como recomendadas** (abaixo da
tabela).

| # | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **LS-1** | a (b) primeiro, sozinha; a (a) só pela regra da seção 4 | **sim** | se a (a) também for necessária, uma rodada a mais; as duas juntas não dizem qual agiu |
| **LS-2** | o que suspende: a busca e a ida a uma comida vista | **as duas** | só a busca deixa as 706 idas quebradas pelo reflexo no longe; as duas mudam também as 339 do comedouro, que o C-L2-3 vigia |
| **LS-3** | a retomada pelo sorteio, com a persistência, e não forçada | **pelo sorteio** | forçada, o pet volta à meta mesmo quando o corpo pede outra coisa, e o risco de prender sobe; pelo sorteio, uma retomada pode perder para o dormir pelo sorteio |
| **LS-4** | `n_suspensa_max` = 6 e `lambda_retomar` = S/4, os valores emprestados, sem calibração | **sim** | curto demais: as expiradas comem o efeito (a S-1 mostra); longo demais: o pet guarda a meta (o C-L2-4 pega); calibrar pede sementes de calibração da faixa nova |
| **LS-5** | o F não sobe nos fins "expirou", "saciou", "achou" e "superada" | **sim** | com o F subindo, cada cochilo empurra o pet a explorar ao acordar; sem ele, o corpo que interrompe não conta como fracasso, e o F do longe fica menor que hoje |
| **LS-6** | o par M0 e M0+S, só descritivo | **sim** | sem ele, uma mudança no M3\*+S pode vir da suspensão ou do aprendizado que ela muda; com ele, o custo das vidas dobra |
| **LS-7** | os critérios C-L2-1 a C-L2-4 e as margens | **como estão** | margens largas deixam passar uma piora no comedouro; estreitas pedem mais unidades |

**As decisões do Matheus (2026-10-29), DECIDIDAS como recomendadas:**
- **LS-1:** a parte (b) primeiro, sozinha; a (a) só pela regra da seção 4;
- **LS-2:** suspendem a busca pelo cheiro e a ida a uma comida vista;
- **LS-3:** a retomada pelo sorteio, com a persistência, e não forçada;
- **LS-4:** `n_suspensa_max` = 6 e `lambda_retomar` = S/4, os valores emprestados, sem calibração;
- **LS-5:** o F não sobe nos fins "expirou", "saciou", "achou" e "superada";
- **LS-6:** o par M0 e M0+S, só descritivo;
- **LS-7:** os critérios C-L2-1 a C-L2-4 e as margens, como estão.

**O que já foi feito** (o worker D, no PR da L-2): o gabarito do conserto, o código atrás da chave com os testes T-L2-1 a T-L2-9 e o
adendo 5 ao plano, com a faixa 67101 a 67505 e o poder. Nenhuma vida rodou.

**Depois da revisão, na ordem:** o gabarito do conserto (um commit), o código atrás da chave com os testes T-L2-1 a T-L2-9 (um PR), o
adendo ao plano com o poder (um PR, antes de qualquer vida), a faixa pedida ao coordenador, a avaliação uma vez e o relato.
