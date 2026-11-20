# RESULTADO V3 — PET_VIVO, R-sono: o sono vem do reflexo ou do sorteio? (2026-11-20)

Worker: Claude Code, Fable 5.2, worktree `v3-integracao-r1-plano`. Plano: [PLANO_ANALISE_V3_PET_VIVO_SONO.md](PLANO_ANALISE_V3_PET_VIVO_SONO.md)
(APROVADO em 2026-11-20, SN-1 a SN-5 decididas). Pré-registro: `docs/PREREGISTRO.md`, seção `PR-PET-VIVO-SONO`, escrita antes da run.
Código: `682e7e5c`, a `main` com o #1040 (o plano) e o #1041 (o código), `git_limpo` verdadeiro. O pedido do Matheus (2026-11-20):
"Sim, merge e roda". O `pre_run` respondeu "pode rodar" depois de a conferência do "Tempo bem" da CORPO terminar. O replay rodou uma
vez: `python experiments/run_v3_pet_vivo_sono.py --config experiments/configs/v3_pet_vivo/sono.json --processos 4`, de 11:48 a
12:36, 49 min.

Os artefatos ficam em `artifacts_v3_pet_vivo/sono/run/`: `meta.json` (os sha256 do código, do plano, da config, da fonte e dos
artefatos), `resultado.json` (a leitura e os resumos) e `medidas.json.gz` (as medidas por vida). O `medidas.json` cru (8 MB) fica só
no sha256 do `meta.json`: o `.gz` tem o mesmo conteúdo. Todo número abaixo sai do `resultado.json`.

**Nenhuma vida nova:** são as mesmas 5 120 vidas do R1 e do R-a, rejogadas pelo log com a `ConfigRastro` ligada. Nada é creditado, e
nada muda no cérebro.

## 1. A resposta curta

- **L-CAMINHO: "boa parte passa pelo sorteio: vale um teste de recompensa".** No HOJE, a fração do tempo de sono em episódios que os
  pesos começaram (a F_PESOS) é **0,543** no `comedouro`, **0,376** no `longe` e **0,495** no `longe_fixo`. O limite de baixo do
  IC95 passa de 0,25 nos 3 lugares. É o desfecho esperado, escrito antes.
- **O resto é reflexo:** de 46 % a 62 % do tempo de sono fica em episódios que a exaustão começou, e ali nenhuma recompensa muda a
  decisão.
- **Três achados que mudam o desenho de um teste de recompensa** (a seção 5): a fração depende muito do dono; nas vidas de hoje o
  dormir não tem parte aprendida nenhuma; e no pet do jogo (o v38, com o sono que segura) só o adormecer passa pelo sorteio.

## 2. As vidas e as conferências

- **5 120 replays:** o HOJE da run do PV-2 (2 400), o OLF-0 da mesma run (2 400) e o HOJE da checagem do v38 (320).
- **As conferências que falham alto passaram em todas:** a C-FONTE, a C-G1, a C-FECHO, a C-UMA-VEZ, a C-REFLEXO (na run, o reflexo é
  só a energia abaixo de S/4, e fora dele a energia nunca está abaixo) e a C-SOMA. O replay terminou com saída 0.
- **O custo:** 49 min de parede com 4 processos, contra a projeção de 0,60 h da fumaça e o corte de 2 h. Disco livre: 78 GB.

## 3. A regra de leitura (o HOJE, n 200 por lugar, IC95)

| medida | comedouro | longe | longe_fixo |
|---|---|---|---|
| F_PESOS (a da regra) | 0,543 [0,538; 0,548] | 0,376 [0,369; 0,383] | 0,495 [0,480; 0,510] |
| F_PESOS-DEC (ao lado) | 0,673 [0,669; 0,678] | 0,478 [0,472; 0,485] | 0,600 [0,586; 0,614] |

- **A regra lê a F_PESOS:** os cortes são 0,10 (o limite de cima, para "quase tudo reflexo") e 0,25 (o limite de baixo em 2 lugares,
  para "boa parte passa pelo sorteio"), SEM FONTE (SN-3).
- **A F_PESOS conta o episódio inteiro no caminho que o começou.** O sono que o reflexo começa e segue com a energia já acima de S/4
  conta como reflexo, embora cada decisão de continuar passe pelo sorteio.
- **A F_PESOS-DEC conta decisão por decisão,** sem olhar quem começou. Ela é maior (de 0,48 a 0,67): adormecer por exaustão e
  continuar dormindo pelo sorteio é comum. A recompensa poderia agir nas duas pontas: em não adormecer e em acordar mais cedo.

## 4. Os descritivos

### 4.1 As decisões de dormir por caminho (o HOJE, a média)

| medida | comedouro | longe | longe_fixo |
|---|---|---|---|
| decisões de dormir por vida | 629 | 627 | 619 |
| pelo REFLEXO | 0,327 | 0,522 | 0,400 |
| pelo SORTEIO | 0,664 | 0,468 | 0,584 |
| candidato ÚNICO | 0,009 | 0,010 | 0,016 |
| pelo SEGURA | 0,000 | 0,000 | 0,000 |

O SEGURA é 0 no HOJE: o sono que segura está desligado nessas vidas.

### 4.2 Os episódios de sono (o HOJE, a média)

| medida | comedouro | longe | longe_fixo |
|---|---|---|---|
| episódios que o REFLEXO começou | 163 | 270 | 206 |
| episódios que o SORTEIO começou | 190 | 127 | 161 |
| episódios do candidato ÚNICO | 3,8 | 4,3 | 6,1 |
| ticks em episódios do REFLEXO (fração) | 0,457 | 0,624 | 0,505 |
| ticks em episódios do SORTEIO (fração) | 0,523 | 0,355 | 0,463 |
| ticks em episódios do ÚNICO (fração) | 0,020 | 0,021 | 0,032 |

Os episódios são curtos: cerca de 630 decisões de dormir em 357 a 401 episódios por vida, menos de 2 decisões (30 min) por episódio.

### 4.3 Por dono (o HOJE, a média, sem IC)

A F_PESOS:

| dono | comedouro | longe | longe_fixo |
|---|---|---|---|
| atencioso | 0,67 | 0,54 | 0,66 |
| incoerente | 0,67 | 0,56 | 0,66 |
| relapso | 0,46 | 0,22 | 0,37 |
| aleatorio | 0,36 | 0,18 | 0,29 |

A F_PESOS-DEC:

| dono | comedouro | longe | longe_fixo |
|---|---|---|---|
| atencioso | 0,80 | 0,62 | 0,75 |
| incoerente | 0,80 | 0,64 | 0,74 |
| relapso | 0,58 | 0,34 | 0,49 |
| aleatorio | 0,50 | 0,31 | 0,42 |

- **Com o dono atencioso e com o incoerente, o sono passa mais pelos pesos** (de 0,54 a 0,68 pela F_PESOS). **Com o relapso e com o
  aleatório, mais pelo reflexo** (de 0,18 a 0,46).
- No `comedouro`, o incoerente sai igual ao atencioso (o D-RB-3 do R-a).

### 4.4 A margem, só nas decisões de dormir pelo sorteio (o HOJE, a média)

| medida | comedouro | longe | longe_fixo |
|---|---|---|---|
| decisões de dormir pelo sorteio, por vida | 417 | 287 | 356 |
| a energia: 1º quartil | 307 | 313 | 318 |
| a energia: mediana | 365 | 375 | 382 |
| a energia: 3º quartil | 442 | 465 | 469 |
| a chance do dormir no sorteio | 0,459 | 0,401 | 0,433 |
| o dormir ganhou sem ter o maior peso (fração) | 0,295 | 0,412 | 0,360 |
| a folga média do peso do dormir | 353 | −14 | 121 |
| o comer ou o brincar eram candidatos (fração) | 0,430 | 0,566 | 0,499 |
| a parte aprendida da ativação do dormir | 0,0 | 0,0 | 0,0 |

- **O pet que dorme pelo sorteio já está cansado:** a mediana da energia fica entre 365 e 382, pouco acima do S/4 (256), numa
  escala que vai até 1 024.
- **O dormir não ganha folgado:** a chance dele no sorteio fica entre 0,40 e 0,46, e em 29 % a 41 % das vezes ele ganha sem ter o
  maior peso.
- **O comer ou o brincar eram candidatos em 43 % a 57 % dessas decisões.** Nas outras, nenhum dos dois tinha peso: recompensá-los
  só mudaria algo se os tirasse do zero.
- **A parte aprendida do dormir é 0 em todas.** Nas vidas de hoje, nada do que o pet aprende entra no peso do dormir: ele sai só do
  inato. O que a recompensa pode mover hoje é o peso das outras ações.

### 4.5 As decisões acordadas (o HOJE, a média)

| medida | comedouro | longe | longe_fixo |
|---|---|---|---|
| decisões acordadas com a energia em S/4 ou acima, por vida | 714 | 716 | 724 |
| o dormir era candidato (fração) | 0,962 | 0,957 | 0,957 |
| a chance média do dormir no sorteio | 0,311 | 0,231 | 0,267 |

Com a energia em S/4 ou acima, o dormir é candidato em 96 % das decisões acordadas e tem de 23 % a 31 % de chance em cada uma.

### 4.6 O OLF-0 e a checagem do v38

O OLF-0 (n 200 por lugar):

| medida | comedouro | longe | longe_fixo |
|---|---|---|---|
| F_PESOS | 0,455 [0,447; 0,463] | 0,318 [0,312; 0,324] | 0,279 [0,265; 0,294] |
| F_PESOS-DEC | 0,579 [0,572; 0,586] | 0,437 [0,431; 0,443] | 0,409 [0,395; 0,422] |

O OLF-0 lê igual pela regra (o limite de baixo passa de 0,25 nos 3 lugares), com frações menores que as do HOJE.

A checagem do v38 (n 40, com o sono que segura ligado):

| medida | longe | longe_fixo |
|---|---|---|
| F_PESOS | 0,463 [0,444; 0,482] | 0,577 [0,540; 0,614] |
| F_PESOS-DEC | 0,114 [0,112; 0,117] | 0,128 [0,124; 0,132] |

| medida | longe | longe_fixo |
|---|---|---|
| pelo REFLEXO | 0,351 | 0,238 |
| pelo SEGURA | 0,535 | 0,635 |
| pelo SORTEIO | 0,114 | 0,127 |
| candidato ÚNICO | 0,0006 | 0,0008 |
| a mediana da energia no sorteio | 457 | 470 |
| a chance do dormir no sorteio | 0,256 | 0,273 |

- **No v38 as duas frações se separam:** de 0,46 a 0,58 do tempo de sono fica em episódios que o sorteio começou, mas só 11 % a 13 %
  das decisões de dormir passam pelo sorteio. De 53 % a 63 % são o sono que segura.
- **Ou seja, no pet do jogo só o adormecer é alcançável pela recompensa.** Depois que ele dorme, o reflexo o segura até a energia
  passar do limiar de acordar, salvo a fome urgente ou o dono.
- É descritivo: 2 lugares, 40 unidades.

## 5. A leitura

- **Pela regra escrita antes, vale um teste de recompensa.** Perto de metade do tempo de sono vem de episódios que o pet começou
  pelo sorteio, com a energia acima de S/4.
- **Não é a maior parte em todo lugar.** No `longe`, 62 % do tempo de sono vem de episódios da exaustão. Ali a alavanca maior é o
  corpo.
- **A resposta depende do dono.** Com o dono que cuida (atencioso, incoerente), o pet chega menos à exaustão e dorme mais pelo
  sorteio. Com o relapso e o aleatório, a exaustão manda. Um teste de recompensa precisa separar os donos.
- **Hoje o dormir não aprende.** A parte aprendida do peso do dormir é 0 em todas as decisões de sorteio. A recompensa só mexeria no
  sono por tabela, subindo o peso do comer ou do brincar. E em cerca de metade dessas decisões nenhum dos dois era candidato.
- **No pet do jogo a janela é menor.** Com o sono que segura, só o adormecer passa pelo sorteio (11 % a 13 % das decisões de
  dormir). Um teste feito sem essa chave superestima o que a recompensa alcança no jogo.
- **Para a pergunta do Matheus** ("se o dono recompensar mais o comer e o brincar, o pet fica mais tempo acordado?"): o replay diz
  que há por onde, em cerca de metade do sono, e que a outra metade é do corpo. Ele não diz quanto: isso pede vidas novas.

## 6. O que não muda

Nada no cérebro, no corpo, no motor nem na web. A `ConfigRastro` segue desligada por padrão. O teste de recompensa, se o Matheus
quiser, é outra run, com plano próprio.

## 7. O que este replay não demonstra

- **Nada sobre a recompensa:** o replay diz por onde o pet dorme, e não o que o dono mudaria.
- **Nada sobre o que é melhor para o pet:** ficar mais tempo acordado pode custar energia e saúde. A medida primária ("Tempo bem")
  não entra aqui.
- **Nada sobre o corpo depois da C3 ou da C4,** nem sobre o jogo web, nem fora dos 14 dias e dos lugares da C4. Se o corpo novo
  mudar a exaustão, as frações mudam.
- **O v38 é descritivo:** 2 lugares, 40 unidades.
- **Os cortes (0,10 e 0,25) são SEM FONTE.** A margem é larga no `comedouro` e no `longe_fixo` e menor no `longe` (0,369 contra
  0,25).
- **A última decisão de cada vida fica de fora** (1 de 1 344), por não ter a leitura da energia (D-SN-5).

## 8. As decisões que ficam para o Matheus

- **Fazer ou não o teste de recompensa.** Custo de errar: sem o teste, a pergunta fica com a resposta "há por onde, não se sabe
  quanto"; com o teste, são vidas novas, com faixa e plano próprios.
- **Se fizer, com ou sem o sono que segura.** A recomendação é com ele ligado, como no pet do jogo: sem ele, o teste mede uma janela
  que o jogo não tem.
- Nenhuma delas é decidida neste PR.
