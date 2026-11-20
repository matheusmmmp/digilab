# RESULTADO V3 — PET_VIVO, R-a: a linha de base do intervalo, só leitura (2026-11-19)

Worker: Claude Code, Fable 5.2, worktree `v3-integracao-r1-plano`. Plano: [PLANO_ANALISE_V3_PET_VIVO_RA.md](PLANO_ANALISE_V3_PET_VIVO_RA.md)
(APROVADO em 2026-11-19, RB-1 a RB-5 decididas). Código: `1688bca9`, a `main` com o #1030 (o plano) e o #1032 (o código), `git_limpo`
verdadeiro. O pedido do Matheus (2026-11-19): "Sim, merge e roda". O `pre_run` respondeu "pode rodar" depois de a run da C3 da CORPO
terminar. O replay rodou uma vez:
`python experiments/run_v3_pet_vivo_ra.py --config experiments/configs/v3_pet_vivo/ra.json --processos 4`, de 21:18 a 21:52, 33 min.

Os artefatos ficam em `artifacts_v3_pet_vivo/ra/run/`: `meta.json` (os sha256 do código, do plano, da config, da fonte e dos
artefatos), `resultado.json` (a leitura e os resumos) e `medidas.json.gz` (as medidas por vida). O `medidas.json` cru (22 MB) fica só
no sha256 do `meta.json`: o `.gz` tem o mesmo conteúdo. Todo número abaixo sai do `resultado.json`.

**Nenhuma vida nova:** são as mesmas 5 120 vidas do R1, rejogadas pelo log com a `ConfigRastro` ligada. Nada é creditado, e nada muda
no cérebro.

## 1. A resposta curta

- **L-SONO: as cinco linhas de base candidatas "preservam o sono".** Na FASE, na ESTADO e nas MÓVEL com k 4, 16 e 96, o resto do
  dormir fica entre +154 e +165 no HOJE, com o limite de baixo do IC95 acima de 0 nos 3 lugares. Só a linha de base por contexto (a
  do R1) o deixa em 0.
- **L-ALÉM: "só o sono".** Tirado o dormir, o η² entre as ações acordadas fica entre 0,014 e 0,034. O limite de cima fica abaixo de
  0,05 nos 3 lugares, na GLOBAL, na FASE, na ESTADO e nas três MÓVEL (o maior é 0,037).
- **O que o plano do R2 recebe** (a seção 6 do plano): o R2 se reduz a ensinar o valor de dormir; o resto do intervalo é decaimento
  quase igual para toda ação acordada.

O desfecho esperado, escrito antes, era "só o sono", e saiu. Das três hipóteses, a H-ALÉM e a H-ESTADO saem como previsto, e a
**H-MÓVEL não se confirma**: a média móvel curta não apaga o sono (a seção 5).

## 2. As vidas e as conferências

- **5 120 replays:** o HOJE da run do PV-2 (2 400), o OLF-0 da mesma run (2 400) e o HOJE da checagem do v38 (320).
- **As conferências que falham alto passaram em todas:** a C-FONTE, a C-G1, a C-FECHO, a C-UMA-VEZ e a C-IGUAL-R1 (a GLOBAL e a CTX,
  refeitas por decisão, dão as medidas gravadas do R1, vida a vida). O replay terminou com saída 0.
- **O custo:** 33 min de parede com 4 processos, contra a projeção de 0,57 h da fumaça e o corte de 2 h. Disco livre: 88 GB.

## 3. A regra de leitura (o HOJE, n 200 por lugar, IC95)

### 3.1 O resto do dormir (L-SONO)

| linha de base | comedouro | longe | longe_fixo |
|---|---|---|---|
| GLOBAL | 156,1 [155,5; 156,7] | 159,4 [158,9; 159,8] | 156,5 [155,8; 157,1] |
| CTX | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| FASE | 155,9 [155,3; 156,5] | 159,2 [158,7; 159,6] | 156,2 [155,5; 156,8] |
| ESTADO | 153,9 [153,3; 154,4] | 158,1 [157,6; 158,5] | 154,5 [153,8; 155,2] |
| MÓVEL-4 | 158,1 [157,4; 158,7] | 165,5 [165,0; 166,0] | 160,0 [159,1; 161,0] |
| MÓVEL-16 | 157,5 [156,9; 158,1] | 161,5 [161,1; 162,0] | 158,3 [157,5; 159,0] |
| MÓVEL-96 | 153,7 [153,1; 154,2] | 157,1 [156,7; 157,6] | 153,9 [153,3; 154,6] |

O corte é 0: "preserva" com o limite de baixo acima de 0 nos 3 lugares. A CTX dá 0 por construção (D-RA-18) e não entra na L-SONO.

### 3.2 O η² entre as ações acordadas (L-ALÉM)

| linha de base | comedouro | longe | longe_fixo |
|---|---|---|---|
| GLOBAL | 0,031 [0,029; 0,034] | 0,017 [0,016; 0,017] | 0,023 [0,022; 0,024] |
| CTX | 0,031 [0,029; 0,034] | 0,017 [0,016; 0,017] | 0,023 [0,022; 0,024] |
| FASE | 0,031 [0,029; 0,034] | 0,016 [0,016; 0,017] | 0,023 [0,021; 0,024] |
| ESTADO | 0,032 [0,030; 0,034] | 0,017 [0,016; 0,017] | 0,023 [0,022; 0,024] |
| MÓVEL-4 | 0,032 [0,030; 0,034] | 0,019 [0,018; 0,019] | 0,024 [0,023; 0,026] |
| MÓVEL-16 | 0,034 [0,032; 0,037] | 0,018 [0,017; 0,019] | 0,026 [0,024; 0,027] |
| MÓVEL-96 | 0,030 [0,027; 0,032] | 0,014 [0,013; 0,015] | 0,022 [0,021; 0,023] |

O corte é 0,05 (RB-4, SEM FONTE). A GLOBAL e a CTX dão o mesmo número: sem o dormir, as duas tiram a mesma média.

## 4. Os descritivos

### 4.1 O η² entre todos os comportamentos (o HOJE)

| linha de base | comedouro | longe | longe_fixo |
|---|---|---|---|
| GLOBAL | 0,460 [0,458; 0,462] | 0,498 [0,495; 0,501] | 0,490 [0,485; 0,495] |
| CTX | 0,019 [0,018; 0,021] | 0,011 [0,010; 0,011] | 0,016 [0,015; 0,017] |
| FASE | 0,459 [0,457; 0,461] | 0,497 [0,495; 0,500] | 0,488 [0,484; 0,493] |
| ESTADO | 0,450 [0,449; 0,452] | 0,494 [0,492; 0,497] | 0,482 [0,478; 0,486] |
| MÓVEL-4 | 0,411 [0,409; 0,413] | 0,465 [0,462; 0,468] | 0,449 [0,443; 0,455] |
| MÓVEL-16 | 0,456 [0,454; 0,458] | 0,501 [0,498; 0,503] | 0,492 [0,486; 0,497] |
| MÓVEL-96 | 0,462 [0,460; 0,463] | 0,504 [0,501; 0,506] | 0,494 [0,489; 0,499] |

Toda linha de base que não olha o contexto deixa perto de metade da variância do resto entre os comportamentos, como a GLOBAL do R1.
A MÓVEL-4 é a que mais tira (de 0,41 a 0,46).

### 4.2 O resto por comportamento na ESTADO (o HOJE, a média)

| comportamento | comedouro | longe | longe_fixo |
|---|---|---|---|
| dormir | 153,9 | 158,1 | 154,5 |
| ocioso | −18,5 | −12,7 | −22,7 |
| emburrar | −32,6 | −124,9 | −66,2 |
| comer | −109,5 | −135,3 | −118,3 |
| brincar | −133,7 | −131,3 | −117,3 |
| chamar atencao | −144,1 | −141,0 | −141,3 |
| explorar | −140,7 | −141,8 | −135,2 |

- **O ocioso** fica entre −13 e −23 na ESTADO, contra +106 a +120 na CTX e −21 a −32 na GLOBAL.
- **O emburrar** varia muito entre os lugares, com poucas decisões por vida; fica só como descritivo.

### 4.3 As decisões por vida e o piso (o HOJE)

A média de decisões por vida e, entre parênteses, a fração das vidas em que o comportamento passa do piso de 5 e entra no η² do
acordado:

| comportamento | comedouro | longe | longe_fixo |
|---|---|---|---|
| dormir | 629 | 627 | 619 |
| explorar | 435 (1,00) | 350 (1,00) | 361 (1,00) |
| chamar atencao | 172 (1,00) | 222 (1,00) | 231 (1,00) |
| comer | 69 (1,00) | 86 (1,00) | 78 (1,00) |
| brincar | 22 (0,89) | 29 (0,90) | 31 (0,96) |
| emburrar | 7 (0,59) | 21 (0,92) | 15 (0,74) |
| ocioso | 10 (0,84) | 8 (0,75) | 9 (0,75) |

A fração das decisões com o intervalo começando à noite é 0,37 nos 3 lugares.

### 4.4 O OLF-0 e a checagem do v38

- **O OLF-0 (n 200 por lugar) lê igual:** o resto do dormir de +153 a +166 nas cinco candidatas, e o η² do acordado de 0,014 a 0,026.
- **A checagem do v38 (n 40, `longe` e `longe_fixo`) lê igual, com o resto do dormir menor:** de +101 a +114 na FASE, na ESTADO, na
  MÓVEL-16 e na MÓVEL-96, e de +84 a +96 na MÓVEL-4. O η² do acordado fica entre 0,023 e 0,032. É descritivo: 2 lugares, 40 unidades.

O resto do dormir no OLF-0:

| linha de base | comedouro | longe | longe_fixo |
|---|---|---|---|
| GLOBAL | 162,8 [162,2; 163,3] | 158,1 [157,6; 158,6] | 158,0 [157,4; 158,5] |
| CTX | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| FASE | 162,5 [162,0; 163,1] | 157,9 [157,4; 158,4] | 157,7 [157,1; 158,2] |
| ESTADO | 161,6 [161,0; 162,1] | 156,0 [155,5; 156,5] | 153,4 [152,3; 154,5] |
| MÓVEL-4 | 166,4 [165,7; 167,0] | 163,7 [163,1; 164,2] | 164,4 [163,7; 165,2] |
| MÓVEL-16 | 164,6 [164,0; 165,2] | 159,9 [159,4; 160,4] | 159,9 [159,3; 160,4] |
| MÓVEL-96 | 160,2 [159,6; 160,8] | 156,1 [155,6; 156,6] | 155,8 [155,2; 156,3] |

O resto do dormir na checagem do v38:

| linha de base | longe | longe_fixo |
|---|---|---|
| GLOBAL | 113,6 [111,9; 115,4] | 104,1 [101,1; 107,1] |
| CTX | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| FASE | 113,5 [111,8; 115,3] | 103,9 [100,9; 106,8] |
| ESTADO | 112,7 [111,2; 114,2] | 101,4 [99,7; 103,1] |
| MÓVEL-4 | 96,1 [93,8; 98,4] | 83,5 [79,2; 87,9] |
| MÓVEL-16 | 111,8 [110,1; 113,6] | 101,8 [98,6; 104,9] |
| MÓVEL-96 | 111,9 [109,9; 113,8] | 101,8 [98,6; 104,9] |

## 5. A leitura

- **Qualquer linha de base que não separe acordado de dormindo preserva o sono.** A FASE, a ESTADO e as MÓVEL dão quase o mesmo
  resto do dormir que a GLOBAL (de +154 a +165 contra +156 a +159). O que apagava o sono no R1 era só o corte por contexto.
- **A fase do dia não acrescenta nada à GLOBAL:** as duas diferem em menos de 0,4 no resto do dormir e em menos de 0,002 nos η².
- **A H-MÓVEL não se confirma.** A previsão era que a média móvel curta apagaria o sono, porque o pet dorme em blocos. No HOJE, a
  MÓVEL-4 dá o maior resto do dormir das candidatas (de +158 a +165). Só na checagem do v38 ela é a menor (de +84 a +96), ainda
  longe de 0.
- **A H-ESTADO sai como previsto, com uma ressalva.** O resto do ocioso cai de +106 a +120 (CTX) para −13 a −23 (ESTADO). Mas a
  maior parte da queda vem de largar o corte por contexto: a GLOBAL já o deixa em −21 a −32.
- **A H-ALÉM sai como previsto.** Entre as ações acordadas, nenhuma linha de base deixa mais de 3,7 % da variância do resto entre os
  comportamentos (o maior limite de cima, a MÓVEL-16 no `comedouro`).
- **Para o R2:** o que há para ensinar com o intervalo é o valor de dormir. Entre as cinco candidatas, o R-a não separa uma melhor:
  todas preservam o sono, e nenhuma mostra sinal além dele.

## 6. O que não muda

Nada no cérebro, no corpo, no motor nem na web. A `ConfigRastro` segue desligada por padrão. O R2 é da tarefa CREDITO_INTERVALO; a
seção 4 do plano dele (a linha de base) fecha com esta leitura.

## 7. O que este replay não demonstra

- **Nada sobre o crédito:** uma linha de base que preserva o sono não mostra que ensinar o sono ajuda.
- **Nada sobre o corpo depois da C3,** nem sobre o jogo web, nem fora dos 14 dias e dos lugares da C4.
- **A medida primária de bem-estar segue em aberto.**
- **A FASE e a ESTADO são leituras com a vida inteira,** e não mecanismos que o cérebro teria ao vivo. Só as MÓVEL são causais.
- **O ocioso e o emburrar têm poucas decisões por vida** e ficam só como descritivo.
- **O corte de 0,05 é SEM FONTE.** A margem é de 0,037 contra 0,05 no pior caso.
- **O resto mede diferença de média, não causa:** o replay não diz que escolher dormir mais melhoraria a vida do pet.

## 8. As decisões que ficam para o Matheus

Nenhuma neste PR. A escolha da linha de base e do k é do plano do R2 (a tarefa CREDITO_INTERVALO), que recebe esta leitura. O R-a já
leu o `vidas.tar.gz` da run do PV-2 (RB-5 cumprida); se o R2 vai rejogar essas vidas, é o plano dele que diz.
