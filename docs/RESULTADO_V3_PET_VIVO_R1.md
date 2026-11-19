# RESULTADO V3 — PET_VIVO, R1: o rastro da cadeia, só leitura (2026-11-19)

Worker: Claude Code, Fable 5.2, worktree `v3-integracao-r1-plano`. Plano: [PLANO_ANALISE_V3_PET_VIVO_R1.md](PLANO_ANALISE_V3_PET_VIVO_R1.md)
(APROVADO em 2026-11-19, RA-1 a RA-6 decididas). Código: `3c4b72a6`, com a árvore igual à da `main` em `60fcfdc2` (o merge do #1025),
`git_limpo` verdadeiro. O pedido do Matheus (2026-11-19): "Sim, merge e roda". O `pre_run` respondeu "pode rodar", e nenhuma outra run
de pesquisa estava em curso. O replay rodou uma vez:
`python experiments/run_v3_pet_vivo_r1.py --config experiments/configs/v3_pet_vivo/r1.json --processos 4`, de 17:34 a 18:12, 38 min.

Os artefatos ficam em `artifacts_v3_pet_vivo/r1/run/`: `meta.json` (os sha256 do código, do plano, da config, da fonte e dos
artefatos), `resultado.json` (a leitura e os resumos) e `medidas.json.gz` (as medidas por vida). O `medidas.json` cru (36 MB) fica só
na máquina, com o sha256 no `meta.json`. Todo número abaixo sai do `resultado.json`.

**Nenhuma vida nova:** são as vidas já gravadas da run do PV-2, rejogadas pelo log com a `ConfigRastro` ligada. Nada é creditado, e
nada muda no cérebro.

## 1. A resposta curta

- **L-FORA: "a maior parte do sinal está fora do r".** No HOJE, a fração do sinal que cai no intervalo entre as decisões (a `F_sinal`)
  é **0,780** no `comedouro`, **0,777** no `longe` e **0,776** no `longe_fixo`. O limite de baixo do IC95 passa de 1/2 nos 3 lugares.
- **L-AÇÃO: "o sinal do intervalo é o sono, e a linha de base por contexto o apaga"** (a H-CTX). O η² global fica entre 0,46 e 0,50;
  o η² por contexto fica entre 0,011 e 0,019, com o limite de cima abaixo de 0,05 nos 3 lugares.
- **O que o plano do R2 recebe** (a seção 5 do plano): propor outra linha de base, ou outro contexto, antes do código.

As três hipóteses escritas antes (H-FORA, H-SONO e H-CTX) saem como previsto.

## 2. As vidas e as conferências

- **5 120 replays:** o HOJE da run do PV-2 (2 400), o OLF-0 da mesma run (2 400) e o HOJE da checagem do v38 (320).
- **As conferências que falham alto passaram em todas:** a C-FONTE (o sha256 da fonte), a C-G1 (o log e as medidas de cada vida
  rejogada iguais aos gravados), a C-FECHO e a C-UMA-VEZ. O replay terminou com saída 0.
- **A checagem do v38 só tem dois lugares** (`longe` e `longe_fixo`, 40 unidades cada), como na run do PV-2.
- **O custo:** 38 min de parede com 4 processos, contra a projeção de 0,92 h e o corte de 4 h (RA-6).

## 3. A regra de leitura (o HOJE, n 200 por lugar, IC95)

| medida | comedouro | longe | longe_fixo | o corte |
|---|---|---|---|---|
| `F_sinal` | 0,780 [0,779; 0,781] | 0,777 [0,776; 0,777] | 0,776 [0,774; 0,777] | o limite de baixo ≥ 1/2 |
| η² global | 0,460 [0,458; 0,462] | 0,498 [0,495; 0,501] | 0,490 [0,485; 0,495] | o limite de baixo > 0,05 |
| η² por contexto | 0,019 [0,018; 0,021] | 0,011 [0,010; 0,011] | 0,016 [0,015; 0,017] | o limite de cima < 0,05 |

Os cortes são os da RA-5, SEM FONTE.

## 4. Os descritivos

### 4.1 O intervalo por ação (M-AÇÃO, o HOJE)

A média do `r_int_n` (o r do intervalo, normalizado) por comportamento:

| comportamento | comedouro | longe | longe_fixo |
|---|---|---|---|
| dormir | **+107,9** | **+102,3** | **+103,1** |
| ocioso | −79,9 | −77,6 | −80,2 |
| comer | −162,2 | −194,7 | −174,4 |
| brincar | −189,2 | −195,5 | −177,4 |
| chamar atenção | −190,8 | −198,8 | −196,1 |
| explorar | −191,6 | −200,2 | −190,3 |
| emburrar | −63,6 | −171,2 | −112,5 |

- **O dormir é o único com o intervalo positivo,** e o r do mesmo tick dele é 0 em todas as decisões de dormir
  (`dormir_r_tick_nao_zero` = 0,000 nos 8 conjuntos): a H-SONO.
- **A média por contexto:** acordado, −185,8, −197,5 e −188,3; dormindo, +107,9, +102,3 e +103,1.
- **O resto do dormir:** +156,1, +159,4 e +156,5 pela linha de base global; **0 pela de contexto.** O 0 sai por construção: o contexto
  "dormindo" só tem o dormir, então a média do contexto é a do próprio dormir.
- **Acordado, o que sobra pela linha de base por contexto:** o ocioso fica acima (+105,9, +119,8, +108,0) e o comer um pouco acima
  (+23,6, +2,7, +14,1); o explorar e o brincar ficam perto de 0.
- **As somas com sinal** (`soma_r` e `soma_r_int`): o r do mesmo tick soma positivo (84 643, 100 280, 98 062) e o do intervalo soma
  negativo (−101 963, −125 735, −117 635). O que a ação ganha no tick, o intervalo desfaz com sobra.

### 4.2 A fração fora do r por canal (M-FORA, o HOJE)

| canal | comedouro | longe | longe_fixo |
|---|---|---|---|
| fome | 0,505 | 0,520 | 0,520 |
| curiosidade | 0,573 | 0,559 | 0,543 |
| tédio | 0,689 | 0,660 | 0,660 |
| humor | 0,777 | 0,740 | 0,745 |
| energia | 0,838 | 0,862 | 0,858 |
| higiene, saúde, solidão, estresse | 1,000 | 1,000 | 1,000 |

A dor não tem valor (nenhuma variação nas vidas, n 0). Por dono, a `F_sinal` vai de 0,73 a 0,75 (atencioso e incoerente) a 0,81 a
0,82 (aleatório e relapso).

### 4.3 O dono (M-DONO, sem IC como regra)

- **A fração dos intervalos com gesto do dono:** 0,093, 0,104 e 0,100. Por dono: 0,13 a 0,15 no atencioso e no incoerente, 0,08 no
  aleatório e 0,03 no relapso.
- **A média do `r_int_n`:** com gesto, +334,5, +289,0 e +284,6; sem gesto, −72,3, −76,2 e −72,6.
- **Por gesto:** brincar +635,0, +645,5 e +598,3; limpar +375,4, +382,2 e +376,6; alimentar +189,8, +178,3 e +167,7.
- É coincidência no tempo, não causa. Vai ao plano do R2 (a INT-5).

### 4.4 As intenções (M-TROCA)

- **A fração das decisões que trocam de intenção:** 0,691, 0,746 e 0,715. A duração média é de 1,45, 1,34 e 1,40 decisões; 71 % a
  76 % das intenções duram 1 decisão.
- **A fração das trocas que vêm do reflexo do sono:** 0,174, 0,267 e 0,209.
- Vai ao plano do R3 (a INT-6).

### 4.5 O que muda (M-MUDA, a resposta ao D-PV0R-6)

A fração das decisões em que o receptor muda:

| receptor | no mesmo tick | no intervalo |
|---|---|---|
| energia | 0,378, 0,344, 0,341 | 0,999 nos 3 |
| humor | 0,343, 0,291, 0,297 | 0,995, 0,932, 0,956 |
| tédio | 0,242, 0,208, 0,218 | 0,512, 0,484, 0,506 |
| fome | 0,042, 0,025, 0,032 | 0,936, 0,708, 0,795 |
| higiene | 0,000 nos 3 | 0,956, 0,834, 0,881 |

### 4.6 O OLF-0 e o v38, ao lado, sem leitura

| medida | OLF-0 comedouro | OLF-0 longe | OLF-0 longe_fixo | v38 longe | v38 longe_fixo |
|---|---|---|---|---|---|
| `F_sinal` | 0,773 | 0,796 | 0,806 | 0,776 | 0,763 |
| η² global | 0,492 | 0,498 | 0,521 | 0,404 | 0,376 |
| η² por contexto | 0,011 | 0,011 | 0,013 | 0,017 | 0,017 |
| `r_int_n` do dormir | +105,9 | +103,6 | +106,6 | +67,7 | +60,3 |

O desenho é o mesmo nos três conjuntos. No v38, o dormir vale menos no intervalo, e o brincar sobra positivo pela linha de base por
contexto (+41,2 e +30,4).

## 5. A leitura

- **Há o que creditar.** Perto de 78 % do que muda no sinal do corpo acontece entre as decisões, fora do r de hoje. Na energia, na
  higiene, na saúde, na solidão e no estresse, quase tudo.
- **O que o intervalo distingue é dormir de estar acordado.** Pela linha de base global, metade da variância do resto fica entre os
  comportamentos. Pela linha de base por contexto, sobra menos de 2 %.
- **Por isso a linha de base por contexto (acordado e dormindo), como está, apaga o sinal do sono.** O resto do dormir fica em 0 por
  construção. Um R2 com essa linha de base não ensinaria nada sobre dormir, que é o caso que motivou a etapa.
- **Acordado, o que o intervalo mais separa é o ocioso das outras ações.** O plano do R2 precisa dizer se isso é efeito da ação ou só
  o gasto menor de quem fica parado.

## 6. O que não muda

Nada no cérebro, no corpo, no motor nem na web. A `ConfigRastro` segue desligada por padrão. O TS do rastro fica para depois da LZ3
(RA-3). O R2 é da tarefa CREDITO_INTERVALO.

## 7. O que este replay não demonstra

- **Nada sobre o crédito:** medir que o sinal existe não mostra que creditá-lo ajuda, nem que não piora o forrageio.
- **Nada sobre o efeito do dono:** a M-DONO é coincidência no tempo.
- **Nada sobre o jogo web** nem sobre o v38 além da checagem descritiva (2 lugares, 40 unidades cada).
- **Nada fora dos 14 dias, do mundo do MVP e dos lugares da C4.**
- **Os cortes (1/2, 1/4 e 0,05) são SEM FONTE.** As margens aqui são largas (0,78 contra 0,5; 0,02 contra 0,05), mas o corte não tem
  fonte.
- **O contexto é só acordado e dormindo, pela média da vida** (RA-4). Outra linha de base (a média móvel, a hora do dia, o estado do
  corpo) não foi medida.

## 8. As decisões que ficam para o Matheus

Nenhuma neste PR. A escolha da linha de base e do contexto é do plano do R2 (a tarefa CREDITO_INTERVALO), que recebe esta leitura.
