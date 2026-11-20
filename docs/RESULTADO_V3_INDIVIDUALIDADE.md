# RESULTADO V3 — INDIVIDUALIDADE, I2: a linha de base descritiva no modular (2026-11-08, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_INDIVIDUALIDADE.md](PLANO_ANALISE_V3_INDIVIDUALIDADE.md), APROVADO pelo Matheus em 2026-11-07 ("Aprovo
todas"), com o registro da run na seção 12, empurrado antes da primeira vida (`0b3901f`).

**A run:** única, no commit `0b3901f` (árvore limpa), que é a `main` `ad207f7` com o registro por cima.
- **A faixa e o tamanho:** bases 85101…85505, K = 12, 60 sementes × 4 donos × 2 braços (REL e REL+F) = 480 vidas de 14 dias, no
  `comedouro`.
- **A máquina:** 4 processos, das 05:48 às 08:30 (2 h 42 min de parede). Cada vida custou 81 s em média, e não os 40 s da estimativa
  (D-IND-I2b-2).

**Os artefatos** ficam em `artifacts_v3_individualidade/` (fora do git): `meta.json`, `medidas.json`, `tracos.jsonl`, `analise.json`,
`custo.json` e `vidas.tar.gz` (as 480 vidas e as baterias; sha256 `f07fb6ce…`).
- **A origem dos números:** todo número deste documento sai do `analise.json`. O que é conta minha sobre o `tracos.jsonl` está marcado
  como "conta sobre o artefato".
- **A conferência:** os sha256 do `meta.json` batem, e a análise refeita a partir do `medidas.json` saiu igual byte a byte.
- **As conferências por vida:** toda vida passou pelo G1 (o replay do disco), pelo cenário, pelo mecanismo, pela memória do braço e pelo
  G2 da bateria. Toda janela teve decisão acordada: a fração de janelas válidas é 1,0 nos seis traços e nos dois braços, e nenhum dia
  ficou sem sonda.

## 1. A tabela (7.1)

O R e o η² estão com o IC95 do bootstrap, 2 000 reamostras: sobre os pets no R e sobre as sementes no η². A média e o desvio são entre
os 240 pets de cada braço.

**REL** (o pet do jogo)

| traço | R_pet | R_dia | R_rep | η²_dono | média (dp) |
|---|---|---|---|---|---|
| apego | 0,110 [0,090; 0,129] | 0,118 [0,091; 0,145] | 0,589 [0,570; 0,606] | 0,66 [0,59; 0,73] | 0,273 (0,077) |
| tédio | 0,059 [0,046; 0,072] | 0,054 [0,033; 0,075] | 0,505 [0,486; 0,524] | 0,47 [0,40; 0,55] | 0,604 (0,058) |
| neofilia | 0,282 [0,255; 0,307] | 0,359 [0,327; 0,389] | 0,610 [0,587; 0,633] | 0,89 [0,87; 0,91] | 0,446 (0,272) |
| ousadia | 0,113 [0,098; 0,128] | 0,213 [0,183; 0,241] | 0,244 [0,218; 0,269] | 0,78 [0,73; 0,82] | 0,222 (0,152) |
| brincar | 0,047 [0,035; 0,059] | 0,089 [0,064; 0,114] | 0,180 [0,153; 0,207] | 0,28 [0,21; 0,37] | 0,070 (0,031) |
| susto | 0,019 [0,011; 0,027] | 0,000 [0,000; 0,009] | 0,443 [0,393; 0,489] | 0,06 [0,02; 0,14] | −0,024 (0,014) |

**REL+F** (com as facetas)

| traço | R_pet | R_dia | R_rep | η²_dono | média (dp) |
|---|---|---|---|---|---|
| apego | 0,105 [0,084; 0,124] | 0,109 [0,080; 0,136] | 0,593 [0,573; 0,611] | 0,61 [0,54; 0,69] | 0,287 (0,076) |
| tédio | 0,055 [0,043; 0,068] | 0,048 [0,030; 0,068] | 0,499 [0,480; 0,519] | 0,40 [0,31; 0,51] | 0,592 (0,057) |
| neofilia | 0,273 [0,249; 0,295] | 0,365 [0,332; 0,395] | 0,563 [0,540; 0,584] | 0,89 [0,86; 0,91] | 0,479 (0,269) |
| ousadia | 0,105 [0,090; 0,120] | 0,196 [0,168; 0,221] | 0,248 [0,222; 0,274] | 0,79 [0,75; 0,83] | 0,217 (0,147) |
| brincar | 0,045 [0,036; 0,055] | 0,090 [0,069; 0,111] | 0,158 [0,131; 0,184] | 0,24 [0,18; 0,32] | 0,068 (0,030) |
| susto | 0,027 [0,019; 0,034] | 0,007 [0,000; 0,022] | 0,454 [0,409; 0,496] | 0,04 [0,00; 0,11] | −0,023 (0,015) |

**As facetas** (só no REL+F; o Spearman da média do traço com a faceta no fim da vida, 240 pets):

| traço | faceta | esperado | Spearman |
|---|---|---|---|
| apego | `apego_dono` | positivo | **−0,39** [−0,48; −0,28] |
| neofilia | `cautela_comida` | negativo | **+0,19** [+0,10; +0,27] |
| ousadia | `ousadia_longe` | positivo | **−0,29** [−0,41; −0,16] |

## 2. As frases que a leitura pode escrever (7.2)

- **"O traço se repete entre pets"** (o IC95 do R_dia exclui 0): vale para o apego, o tédio, a neofilia, a ousadia e o brincar, nos dois
  braços. **O susto não se distingue de zero nesta run** (REL [0,000; 0,009], REL+F [0,000; 0,022]).
- **"O dono acompanha o traço"** (o IC95 do η²_dono exclui 0): vale para os seis traços, nos dois braços. É forte na neofilia (0,89), na
  ousadia (0,78–0,79) e no apego (0,61–0,66), e fraco no susto (0,04–0,06).
- **"A faceta acompanha o traço"** (o IC95 do Spearman exclui 0): vale para as três. **Mas as três vão no sentido contrário ao esperado:**
  - o apego cai com o `apego_dono`;
  - a neofilia sobe com a `cautela_comida`;
  - a ousadia cai com o `ousadia_longe`.

  A run não diz por quê. A seção 5 traz a pergunta que isso deixa.

## 3. As expectativas E1 a E3 (7.3), relidas sem ajuste

- **E1 (o R_pet é baixo no REL): confirmada.** O R_pet vai de 0,019 (susto) a 0,282 (neofilia). Com o genoma vazio, a maior parte da
  variância de cada traço fica dentro do pet.
- **E2 (no REL+F, o R_pet do apego, da neofilia e da ousadia é maior que no REL): não vista.** Os três saem um pouco menores no REL+F
  (0,105 contra 0,110; 0,273 contra 0,282; 0,105 contra 0,113), com os IC sobrepostos.
- **E3 (uma parte visível da diferença entre pets acompanha o dono, sobretudo pelo relapso): a primeira metade confirmada, a segunda
  não.** Conta sobre o artefato (as médias por dono, no REL):

  | traço | atencioso | incoerente | relapso | aleatório |
  |---|---|---|---|---|
  | apego | 0,223 | 0,223 | 0,274 | **0,375** |
  | neofilia | 0,190 | 0,190 | **0,690** | **0,713** |
  | ousadia | 0,091 | 0,091 | **0,391** | 0,315 |

  O relapso e o aleatório andam juntos, longe do atencioso. No apego, o aleatório fica acima do relapso. O η² alto não vem só do relapso.
  O atencioso e o incoerente saem idênticos (D-IND-I2b-1, seção 4).

## 4. A regra dos traços para o I3 (7.4)

**Os seis traços ficam.** Nenhum cai pela (a), pela (b) ou pela (c), e a bateria do I3 é a do I2 inteira.
- (a) Nenhum traço fica abaixo dos 50 %: a fração de janelas válidas é 1,0 em todos.
- (b) Nos traços binários, a fração de 1 fica dentro de [5 %; 95 %]: neofilia 44,6 % e ousadia 22,2 %, no REL.
- (c) Nenhum IC95 do R_rep fica abaixo de 0,05. O menor é o do brincar, 0,180 [0,153; 0,207].

O susto fica pela regra, mas é o traço com o R_dia indistinguível de zero (seção 2). A regra não olha o R_dia, e nada aqui a ajusta.

**Os desvios desta run** (`docs/registro/2026-11.md`, seção "2026-11-08 — INDIVIDUALIDADE, I2b"):
- **D-IND-I2b-1: no `comedouro`, as vidas do incoerente são byte a byte as do atencioso** (120 de 120 pares, nos dois braços). O
  incoerente só difere do atencioso nos sinais de ensino, e o `CanalSemEnsino` os tira.
  - Isso já estava registrado na C4 e na DC3 (`CELULA_DUPLICADA`), mas o plano do I2 não o previu.
  - Os números seguem o plano como está: o η² conta quatro donos, dois deles idênticos, e 60 dos 240 pets de cada braço repetem outros
    60.
  - Para o I3 e o I4, há duas saídas: tirar o incoerente ou trocá-lo por um dono que difira no cuidado. Fica como questão aberta.
- **D-IND-I2b-2: o custo foi o dobro da estimativa.** A seção 6 do plano previa 40 s por vida e cerca de 80 min. Saíram 81 s por vida e
  2 h 42 min, ainda com 4 processos e uma run por vez. A estimativa vinha da fumaça do I1, sem a bateria completa do G2 por vida.

## 5. Sem leitura (seção 8 do plano e o que a run não diz)

- **A síndrome** (o Spearman entre os traços, nas médias por pet, no REL): neofilia × ousadia +0,82, apego × neofilia +0,74,
  apego × ousadia +0,62, apego × tédio −0,66. O susto não acompanha nenhum (|ρ| ≤ 0,22). Os três traços com η² alto andam juntos, e a
  run não separa se é uma síndrome do pet ou o mesmo eixo do dono.
- **A norma de reação:** a inclinação média por dia fica perto de zero em todos os traços. A maior é a da neofilia, +0,015 por dia no
  REL e +0,023 no REL+F. A variância entre pets é pequena.
- **O descritivo, no REL com o atencioso:**
  - a latência média da ação-chave é 4,3 decisões na bola, 6,2 na comida nova, 9,2 no longe e 5,1 na `nula`;
  - a distância andada fica entre 84 e 116 subunidades por janela (a maior é a do longe);
  - nenhum dia ficou sem sonda.

  O resto, por dono e por braço, está no `analise.json`, em `descritivo`.
- **O que a run não demonstra** (do `analise.json`):
  - que o pet tem personalidade (os traços são nomes de medida);
  - que o modular supera o A;
  - qualquer efeito do genoma (o genoma é vazio nesta run);
  - que o mecanismo é novo.
- **A pergunta que fica, para o I3 e o I4:**
  - **as facetas no sentido contrário.** A correlação junta os quatro donos, e o dono move muito o traço (η² alto) e pode mover a faceta
    também. A run não separa isso. A sonda `sem_faceta` do I4 e uma leitura dentro de cada dono são os caminhos, nenhum deles feito aqui;
  - **o susto:** o tapa só na cópia não separa os pets de dia para dia.

## 6. O que segue

Pela tarefa, o Gate I no modular (IN-4) vem antes do I3. A bateria do I3 são os seis traços (7.4). As questões abertas para o Matheus são o
incoerente duplicado (D-IND-I2b-1) e as facetas no sentido contrário.

## 7. Adendo 1: as facetas dentro do dono (2026-11-09, descritivo, sem run)

Este é o adendo 1 do plano (seção 13), decidido pelo Matheus em 2026-11-09 e commitado antes da conta (`39e4ae7`).
- **O artefato:** `artifacts_v3_individualidade/facetas_por_dono.json`, gravado por
  `experiments/descritivo_individualidade_facetas.py`. Ele lê o `medidas.json` do I2 e grava o sha256 dele.
- **O que entra:** só os pets do REL+F, 60 por dono. O incoerente fica fora (D-IND-I2c-2).

| dono | apego × `apego_dono` | neofilia × `cautela_comida` | ousadia × `ousadia_longe` |
|---|---|---|---|
| atencioso | indefinido (a faceta não varia) | indefinido (a faceta não varia) | +0,15 [−0,16; +0,43] |
| relapso | +0,18 [−0,08; +0,42] | indefinido (a faceta não varia) | −0,13 [−0,41; +0,13] |
| aleatório | −0,00 [−0,27; +0,25] | +0,08 [−0,09; +0,24] | −0,00 [−0,26; +0,24] |

- **A frase que a leitura pode escrever (7.2):** dentro de cada dono, **nenhuma faceta acompanha o traço**. Todos os IC95 contêm 0.
- **A conta sobre o `medidas.json`:** as facetas ficam no teto, `teto_faceta` = S/4 = 192 (`digilab/config.py`):
  - no atencioso, o `apego_dono` é +192 nos 60 pets, e a `cautela_comida` é −192 nos 60;
  - no relapso, a `cautela_comida` também é −192 nos 60;
  - no aleatório, ela é −192 em 53 dos 60.
- **O que isso diz:** a correlação no sentido contrário da seção 2 vem da diferença entre os donos. O relapso e o aleatório deixam o
  `apego_dono` abaixo do teto e põem o apego medido acima do atencioso. Dentro do dono, a faceta quase não se move, porque está no teto.
- **O que não diz:** a run não diz se a faceta causa algo no traço; isso é da sonda `sem_faceta` do I4. O teto é um número DECIDIDO
  (ME-4), e o adendo não o calibra.

## 8. O I5: o hábito como medida (2026-11-10, a análise única, Claude Code, Opus 5.5, branch `v3-individualidade-i5b`)

O plano é o `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I5.md` (APROVADO), com o registro na seção 11, commitado antes da primeira vida
(`977b33c`). A análise rodou uma vez.

- **Os dados:** as 360 vidas do I2 (2 braços × 3 donos × 60 sementes), rejogadas do `vidas.tar.gz`. Todos os logs refeitos saíram iguais
  aos do disco, com 96 decisões por dia. Nenhum dia ficou fora (todos tiveram 16 ou mais decisões acordadas).
- **O artefato:** `artifacts_v3_individualidade_i5/` (`meta.json`, `perfis.jsonl`, `analise.json`, `custo.json`). O `meta.json` grava o
  `git_head` `977b33c`, a árvore limpa e os sha256 do registro.
- **O custo:** 2,0 s por vida rejogada (o máximo foi 2,3 s), e 3 min 53 s ao todo, com 4 processos.

### 8.1 A tabela (os dias 8 a 14; a média sobre 180 pets; o IC95 pelo bootstrap sobre as sementes, 2 000 reamostras)

| braço | perfil | H_dono [IC95] | H_mundo [IC95] | D_si | D_dono | D_mundo | D_braço |
|---|---|---|---|---|---|---|---|
| REL | SEQ | −0,0007 [−0,0064; 0,0052] | 0,0363 [0,0278; 0,0447] | 0,3405 | 0,3398 | 0,3768 | 0,2800 |
| REL | LUGAR | 0,0006 [−0,0036; 0,0052] | 0,0176 [0,0098; 0,0248] | 0,5009 | 0,5015 | 0,5184 | 0,4074 |
| REL | HORA | −0,0011 [−0,0037; 0,0015] | 0,0133 [0,0095; 0,0169] | 0,4280 | 0,4269 | 0,4412 | 0,3475 |
| REL+F | SEQ | −0,0005 [−0,0050; 0,0041] | 0,0335 [0,0272; 0,0397] | 0,3465 | 0,3461 | 0,3800 | 0,2800 |
| REL+F | LUGAR | 0,0014 [−0,0029; 0,0055] | 0,0156 [0,0075; 0,0235] | 0,5041 | 0,5055 | 0,5197 | 0,4074 |
| REL+F | HORA | −0,0008 [−0,0037; 0,0022] | 0,0114 [0,0082; 0,0145] | 0,4301 | 0,4294 | 0,4415 | 0,3475 |

O D_braço é o mesmo nos dois braços porque é o mesmo par visto de cada lado.

### 8.2 As frases (seção 6.2 do plano)

- **H_dono:** nos três perfis e nos dois braços, "não se distingue de zero nesta análise".
- **H_mundo:** nos três perfis e nos dois braços, "o pet tem hábito próprio além do mundo da semente" (o IC95 inteiro acima de 0).

### 8.3 As expectativas, relidas sem ajuste

- **E1** (o lugar tem hábito além do dono): **não se confirma.** O H_dono do LUGAR não se distingue de zero nos dois braços.
- **E2** (o H_mundo do LUGAR é menor que o H_dono): **sai ao contrário.** O H_mundo é maior que o H_dono nos três perfis e nos dois braços.
- **E3** (a sequência quase não tem hábito além do dono): **confirma-se**, mas não separa a SEQ: o H_dono está perto de 0 nos três perfis.

### 8.4 O que a tabela mostra, além das frases (descritivo)

- **O que separa os pets é o dono, não o pet.** Um pet se parece com ele mesmo em outro dia tanto quanto com outro pet do mesmo dono no
  mesmo dia (D_si ≈ D_dono), mesmo vivendo num mundo diferente. Com o mesmo mundo e outro dono, a distância é maior (D_mundo > D_si). O
  H_mundo positivo vem dessa diferença entre donos. A frase do plano é a que a regra permite, mas o hábito que ela descreve é o do dono:
  nesta análise não aparece um hábito do pet além do dono. É a leitura D-IND-I5b-1 do registro.
- **Por dono, o H_mundo muda de sinal.** O do atencioso é negativo na HORA (−0,0155 no REL, −0,0232 no REL+F), e o do relapso é negativo
  no LUGAR (−0,0277 e −0,0427). O H_mundo de um dono compara o pet com os pets dos outros dois donos, então o sinal depende de quais donos
  estão na comparação. Está por dono no `analise.json`, em `por_dono`.
- **Os dias 1 a 7:** o H_dono é negativo nos três perfis (SEQ −0,038, HORA −0,020, LUGAR −0,004 a −0,006). Nos primeiros dias, o pet muda
  mais de um dia para o outro do que difere dos outros pets no mesmo dia. Na janela de 8 a 14, o H_dono sobe para perto de 0.
- **O par dos braços é o mais próximo.** O pet do outro braço, com a mesma semente e o mesmo dono, fica mais perto (D_braço 0,28 na SEQ)
  do que o próprio pet em outro dia (D_si 0,34). As facetas mudam menos o dia do que a passagem de um dia para o outro.
- **REL × REL+F:** os dois braços dão os mesmos sinais e ICs que se sobrepõem em todos os perfis. As facetas não mudam o hábito medido aqui.

### 8.5 O que a análise não demonstra

- que o pet não tem hábito (a medida só não o separa do dono nesta janela e nestes perfis);
- qualquer efeito do genoma (vazio no I2);
- que a medida é nova.

### 8.6 O que isso muda no I7

O I7 mede o afastamento contra o gêmeo (D_G). Esta tabela dá a escala: o pet já varia 0,34 a 0,50 de um dia para o outro, e o par mais
próximo que existe hoje (D_braço) fica em 0,28 a 0,41. O D_G do I7 vai se medir contra esse ruído. É só contexto, não muda o plano do I7.

## 9. O I7: o desenvolvimento contrafactual (2026-11-11, a run única, Claude Code, Opus 5.5, branch `v3-individualidade-i7b`)

O plano é o `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md` (APROVADO, com o adendo 1 DECIDIDO). O registro está na seção 13, commitado e
empurrado antes da primeira vida (`3f7b1fa`). A run rodou uma vez.

- **Os dados:** as 360 pets do I2 (2 braços × 3 donos × 60 sementes). Cada pet tem 17 ramos: o N, o G, cinco A(t), cinco E(t) e cinco
  E°(t), com t = 2, 4, 6, 8 e 10. Nenhum (pet, t) ficou sem ramo.
- **As conferências G-I7-0 a 3** passaram em todos os 6 120 ramos. Cada uma falha alto, e a run terminou sem erro. No `ramos.jsonl`,
  `false` numa conferência quer dizer que ela não se aplica àquele ramo; por exemplo, a G-I7-0 só vale para o N.
  - o N saiu igual ao log do I2, byte a byte;
  - cada ramo, vivido duas vezes, deu o mesmo log (a IR-6);
  - as decisões antes do momento são as do original;
  - o E e o E° têm um tapa a mais, só no momento.
- **O artefato:** `artifacts_v3_individualidade_i7/`.
  - versionados: o `meta.json`, o `analise.json` e o `custo.json`; o `meta.json` grava o `git_head` `3f7b1fa`, a árvore limpa e os sha256;
  - só locais, como o `perfis.jsonl` do I5: o `perfis.jsonl.gz` (2 MB) e o `ramos.jsonl` (10 MB). Os sha256 de ambos estão no
    `meta.json`.
- **O custo:** 2 h 48 min de parede com 4 processos, contra a projeção de 6 h da fumaça. São 27 s por pet (110 s dentro de cada processo),
  e cada ramo, vivido duas vezes, leva cerca de 6 s.

### 9.1 A tabela (os dias t+1 a t+4; as razões contra o gêmeo; o IC95 pelo bootstrap sobre as sementes, 2 000 reamostras)

| braço | perfil | Φ_E (as 5 idades) | γ_E | γ_E cru | β_E | Φ_A(2) | Φ_A(10) | β_A | ΔΦ E − E° |
|---|---|---|---|---|---|---|---|---|---|
| REL | SEQ | 0,255 [0,226; 0,284] | 0,0113 [0,0056; 0,0177] | 3,84 [2,44; 5,32] | −0,0008 [−0,0088; 0,0072] | 1,002 [0,972; 1,032] | 0,995 [0,967; 1,025] | −0,0020 [−0,0071; 0,0031] | 0,0018 [−0,0024; 0,0061] |
| REL | LUGAR | 0,286 [0,257; 0,319] | 0,0136 [0,0083; 0,0187] | 5,38 [3,53; 7,20] | 0,0005 [−0,0079; 0,0091] | 0,981 [0,954; 1,008] | 0,959 [0,936; 0,982] | −0,0027 [−0,0070; 0,0010] | 0,0008 [−0,0026; 0,0038] |
| REL | HORA | 0,262 [0,231; 0,295] | 0,0191 [0,0144; 0,0244] | 6,85 [5,30; 8,54] | −0,0001 [−0,0079; 0,0077] | 1,000 [0,986; 1,014] | 0,995 [0,974; 1,016] | 0,0002 [−0,0027; 0,0028] | 0,0132 [0,0083; 0,0180] |
| REL+F | SEQ | 0,279 [0,258; 0,300] | 0,0152 [0,0089; 0,0218] | 5,11 [3,30; 7,06] | 0,0038 [−0,0040; 0,0115] | 1,001 [0,967; 1,032] | 0,998 [0,972; 1,024] | −0,0010 [−0,0066; 0,0046] | 0,0043 [0,0000; 0,0087] |
| REL+F | LUGAR | 0,312 [0,286; 0,336] | 0,0130 [0,0082; 0,0179] | 5,62 [3,86; 7,37] | 0,0055 [−0,0033; 0,0144] | 0,967 [0,947; 0,990] | 0,970 [0,947; 0,994] | −0,0003 [−0,0042; 0,0034] | 0,0053 [0,0023; 0,0085] |
| REL+F | HORA | 0,285 [0,263; 0,307] | 0,0210 [0,0164; 0,0255] | 7,81 [6,36; 9,31] | 0,0063 [−0,0014; 0,0138] | 0,996 [0,977; 1,014] | 1,001 [0,986; 1,017] | 0,0015 [−0,0012; 0,0041] | 0,0185 [0,0140; 0,0232] |

O γ_E cru é a inclinação de Σ D_E contra k, sem dividir pelo gêmeo (12.2). Em todas as células o IC95 dele fica inteiro acima de 0.

**Por idade (o ponto), o resto do dia t (Φ⁰) e a forma em U (12.3):**

| braço | perfil | Φ_E(2) | Φ_E(4) | Φ_E(6) | Φ_E(8) | Φ_E(10) | Φ⁰_E(2) | Φ⁰_E(10) | U1_E | U2_E |
|---|---|---|---|---|---|---|---|---|---|---|
| REL | SEQ | 0,266 | 0,265 | 0,227 | 0,256 | 0,262 | 0,192 | 0,200 | 0,038 [−0,048; 0,117] | 0,035 [−0,043; 0,109] |
| REL | LUGAR | 0,289 | 0,295 | 0,262 | 0,283 | 0,300 | 0,176 | 0,194 | 0,027 [−0,069; 0,122] | 0,038 [−0,053; 0,129] |
| REL | HORA | 0,261 | 0,281 | 0,236 | 0,261 | 0,270 | 0,151 | 0,168 | 0,025 [−0,063; 0,113] | 0,034 [−0,049; 0,117] |
| REL+F | SEQ | 0,282 | 0,272 | 0,260 | 0,253 | 0,330 | 0,185 | 0,268 | 0,022 [−0,059; 0,101] | 0,070 [−0,000; 0,141] |
| REL+F | LUGAR | 0,303 | 0,311 | 0,284 | 0,294 | 0,367 | 0,172 | 0,238 | 0,019 [−0,073; 0,111] | 0,083 [0,010; 0,159] |
| REL+F | HORA | 0,272 | 0,287 | 0,256 | 0,262 | 0,348 | 0,155 | 0,238 | 0,017 [−0,065; 0,102] | 0,092 [0,027; 0,156] |

### 9.2 As frases (7.2 e adendo 1)

- **A condição do evento:** em todas as células, "o tapa mudou o dia em ao menos uma idade" (o Φ⁰_E fica de 0,15 a 0,27, com o IC95
  acima de 0).
- **γ_E:** nas seis células, "a diferença do evento cresce com os dias". A régua crua passa junto.
- **β_E:** nas seis células, "não se distingue de zero nesta análise".
- **A forma em U:** nenhuma célula tem as duas diferenças do mesmo lado, então não há frase de U nem de ∩.
- **Φ_A(t):** em todas as idades e células, "o ramo vira um gêmeo" (o IC95 inteiro acima de 0,8). No LUGAR também se escreve "a
  história até o dia t sobrevive a outro acaso", em parte das idades: no REL nos dias 6, 8 e 10, e no REL+F nos dias 2, 6, 8 e 10. O
  Φ_A fica de 0,96 a 0,98 nesses casos, logo abaixo de 1.
- **Φ_E(t):** em todas as idades e células, "o ramo fica mais perto do original que um gêmeo".
- **γ_A:** só no REL × LUGAR, "a diferença cresce com os dias" (0,012 [0,004; 0,020]); nas outras células, não se distingue de 0.
  **β_A:** em nenhuma célula se distingue de 0.
- **A hipótese:** nas seis células, **"nenhuma das hipóteses descreve o perfil do braço sozinha"**:
  - a H-AMP pede o γ_E > 0, que passa, e o β_E < 0, que não passa;
  - a H-CAN pede o γ_E < 0;
  - a H-TRANS pede o Φ_A(10) abaixo de 0,8;
  - a H-CAOS pede o Φ_E acima de 0,8.

### 9.3 Os contrastes (seção 4)

- **REL+F − REL** (as mesmas sementes reamostradas juntas): nenhum se distingue de 0.

| perfil | Φ_E (5 idades) | γ_E | β_E |
|---|---|---|---|
| SEQ | 0,0244 [−0,0065; 0,0564] | 0,0039 [−0,0034; 0,0109] | 0,0046 [−0,0041; 0,0131] |
| LUGAR | 0,0258 [−0,0051; 0,0551] | −0,0006 [−0,0072; 0,0062] | 0,0051 [−0,0048; 0,0146] |
| HORA | 0,0233 [−0,0106; 0,0562] | 0,0019 [−0,0035; 0,0072] | 0,0064 [−0,0026; 0,0150] |

- **E − E°** (o dono que reage contra o dono que repete o log; a coluna ΔΦ da 9.1):
  - acima de 0 em quatro células: REL × HORA, 0,013; REL+F × HORA, 0,019; REL+F × LUGAR, 0,005; REL+F × SEQ, 0,004, com o IC95 começando
    em 0,00004;
  - não se distingue de 0 no REL × SEQ e no REL × LUGAR.

  Onde passa, o efeito é pequeno: o E° sozinho dá de 90 % a 99 % do Φ_E.

### 9.4 As expectativas, relidas sem ajuste

- **E-I7** (a H-CAN no LUGAR e na HORA, e nenhuma diferença entre o REL e o REL+F):
  - **a H-CAN não se confirma:** a diferença do tapa cresce com os dias, e outro acaso torna o ramo um gêmeo;
  - **a parte das facetas se confirma:** nenhum contraste REL+F − REL se distingue de 0.
- **E-I7b** (Φ_E > Φ_E°):
  - **confirma-se em quatro das seis células,** com efeito pequeno;
  - não se distingue de 0 no REL × SEQ e no REL × LUGAR.

### 9.5 O que a tabela mostra, além das frases (descritivo do plano, 12.5 e 3.5)

- **Outro acaso apaga a história em poucos dias.** O Φ_A fica de 0,96 a 1,02 nos dias t+1 a t+4. No resto do dia t, ele já está em 0,81
  a 0,93. Trocar a rng de política no dia t faz do pet, em um dia, outro pet tão distante quanto um gêmeo, em qualquer idade.
- **O estado interno guarda mais que o comportamento.** O Φ^est do A fica de 0,56 a 0,77: o cérebro do ramo continua mais perto do
  original que o de um gêmeo, mesmo com o comportamento já do gêmeo. O do E fica de 0,16 a 0,24.
- **O reencontro:** no dia 14, 66 % dos ramos E do REL e 63 % dos do REL+F decidem exatamente como o original.
  - Por idade, a fração não muda: fica entre 59 % e 68 %.
  - Por dono, muda: o relapso reencontra menos (54 % e 51 %) que o atencioso (73 % e 65 %) e o aleatório (72 % nos dois braços).
- **O efeito comum do tapa (C_E)** fica de 0,11 a 0,31. O tapa não empurra todos os pets para o mesmo lado; cada um muda para o seu.
- **Por dono:** o Φ_E do relapso é o maior nos três perfis e nos dois braços (0,34 a 0,39, contra 0,21 a 0,29 dos outros dois).

### 9.6 Exploratório, fora do plano (2026-11-11, depois da análise; nenhuma frase de leitura sai daqui)

Sai das mesmas vidas, lidas de novo do `perfis.jsonl.gz` e do `ramos.jsonl`, mais a releitura de 24 ramos para ver as folhas do estado.
A saída das três peças está em `artifacts_v3_individualidade_i7/exploratorio_9_6.txt` (versionado), com os trechos de código no
`exploratorio_9_6_codigo.txt` ao lado.

- **O tapa é tudo ou nada, pet a pet.** Contando, para cada ramo E(t), os dias t+1 a t+4 com D_E = 0:
  - cerca de 2/3 dos ramos (583 a 605 de 900, por braço e perfil) têm D_E = 0 nos quatro dias: o comportamento volta ao do original
    inteiro, já no dia seguinte;
  - cerca de 1/3 (275 a 300 de 900) tem D_E > 0 nos quatro dias;
  - só 18 a 22 de 900 misturam os dois.
- **Os ramos que se afastam chegam perto de um gêmeo:** o D_E médio deles cresce de 0,23 para 0,26 na SEQ, enquanto o D_G médio é 0,30; de
  0,36 para 0,40 no LUGAR (D_G 0,43); e de 0,26 para 0,32 na HORA (D_G 0,37).
  - O Φ_E médio de 0,26 a 0,31 é a mistura das duas populações, 1/3 com Φ de 0,8 a 0,9 e 2/3 com 0.
  - O γ_E > 0 vem do grupo que se afasta.
- **Nos ramos que voltam, o tapa fica só na memória:**
  - a distância do estado interno no dia t+4 é de 0,005 em média (contra 0,36 nos que se afastam), mas não é zero em 89 % deles;
  - nos dois casos relidos, as folhas que diferem (4 e 5 de 4 855) são todas da memória autobiográfica (`mem.autobio`: a dor guardada
    do episódio do tapa);
  - nos que se afastam, diferem cerca de 2 200 folhas, da memória, do afeto, da plasticidade e do árbitro.
- **O que separa os dois grupos parece ser o fluxo da rng de política.** Em 20 ramos relidos (10 de cada grupo):
  - nos 10 que voltaram, o `arb.sorteios` (a contagem de sorteios do árbitro) e o `arb.reflexos` no fim do dia t são os do original;
  - em 8 dos 10 que se afastaram, os dois já diferem no fim do próprio dia t.

  A leitura PROPOSTA: quando o tapa dispara (ou deixa de disparar) um reflexo, o árbitro sorteia um número diferente de vezes. A rng de
  política fica deslocada, e o resto da vida é outro acaso, o mesmo que o ramo A faz de propósito. Quando não dispara, o modular absorve
  o tapa. São 20 ramos, e os outros 2 afastados não se explicam assim.

### 9.7 O que a análise não demonstra

- que o pet não tem história: o estado interno do A fica mais perto do original que um gêmeo, e o comportamento é que não mostra isso;
- que a idade não importa em outra janela, em outro evento ou num pet que vive mais de 14 dias;
- que o mecanismo da 9.6 vale para todos os ramos: são 20 ramos relidos, fora do plano;
- qualquer efeito do genoma (vazio no I2);
- que a medida é nova.

### 9.8 O que isso muda para a frente

- **PROPOSTO, do exploratório da 9.6: o comportamento do modular, nesta janela, parece dominado pelo fluxo da rng de política.** Trocar a rng apaga a história em um dia, e um
  tapa só muda o pet de modo duradouro quando desloca esse fluxo.
- **A pergunta que fica, PROPOSTA:** o desenvolvimento do pet vem da história ou do sorteio? Um ramo E com a rng ressincronizada depois
  do tapa (o mesmo número de sorteios) separaria as duas coisas. Isso pede um plano novo (um adendo ao I7, ou um I8) e não roda sem ele.

## 10. O adendo 2 do I7: história ou sorteio (2026-11-11, a run única, Claude Code, Opus 5.5, branch `v3-individualidade-i7d`)

**O desenho:** a seção 14 do `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md`, DECIDIDA (AD2-1 a AD2-7), com o registro da seção 15.
- **Os pets:** 360 novos, da faixa 88101…88505: 2 braços × 3 donos × 60 sementes, 14 dias no `comedouro`.
- **Os ramos por pet:** o N, o G, o R° e, nas idades 2, 4, 6, 8 e 10, o E (o tapa), o R (o tapa com o sorteio amarrado) e o S (um sorteio
  jogado fora, sem tapa). São 6 480 ramos, cada um vivido duas vezes, com as conferências G-AD2-0 a 4 passando em todos. Nenhum pet ficou
  sem ramo.
- **O amarrado funcionou:** o R° saiu igual ao N byte a byte em todos os pets. Nos ramos R, 2,2 % (REL) e 2,3 % (REL+F) dos sorteios do
  pet caíram numa chave sem par, e nenhum passo do dono ficou descasado.
- **A run:** de 12:19 a 14:03, 1 h 44 min com 4 processos. A análise caiu no fim (D-IND-I7d-2) e foi refeita a partir dos artefatos, sem
  viver de novo (D-IND-I7d-3).
- **Os artefatos:** `artifacts_v3_individualidade_i7_ad2/`, com o `meta.json` e o `analise.json` versionados. O `vidas.tar.gz`, o
  `perfis.jsonl.gz` e o `ramos.jsonl` ficam locais, com os sha256 no `meta.json`. Não há `custo.json`, porque o custo por ramo se perdeu
  com a queda.

### 10.1 A tabela (os dias t+1 a t+4, as cinco idades juntas; o IC95 pelo bootstrap sobre as sementes, 2 000 reamostras)

ρ = Σ D_R / Σ D_E (14.4). Os Φ são razões contra o gêmeo, e os γ são as inclinações em k (3.3).

| braço | perfil | ρ | Φ_E | Φ_R | Φ_S | γ_R | γ_E |
|---|---|---|---|---|---|---|---|
| REL | SEQ | 0,881 [0,846; 0,913] | 0,260 [0,235; 0,285] | 0,229 [0,205; 0,251] | 0,848 [0,832; 0,865] | 0,0065 [0,0009; 0,0122] | 0,0110 [0,0054; 0,0169] |
| REL | LUGAR | 0,948 [0,918; 0,978] | 0,298 [0,270; 0,327] | 0,282 [0,254; 0,309] | 0,907 [0,890; 0,925] | 0,0067 [0,0020; 0,0117] | 0,0062 [0,0016; 0,0107] |
| REL | HORA | 0,754 [0,728; 0,779] | 0,265 [0,239; 0,291] | 0,200 [0,178; 0,222] | 0,867 [0,851; 0,881] | 0,0085 [0,0037; 0,0137] | 0,0155 [0,0112; 0,0198] |
| REL+F | SEQ | 0,889 [0,857; 0,923] | 0,265 [0,240; 0,290] | 0,235 [0,214; 0,257] | 0,847 [0,830; 0,865] | 0,0043 [−0,0015; 0,0107] | 0,0135 [0,0077; 0,0194] |
| REL+F | LUGAR | 0,959 [0,930; 0,988] | 0,304 [0,275; 0,333] | 0,291 [0,266; 0,317] | 0,916 [0,902; 0,932] | 0,0113 [0,0056; 0,0178] | 0,0171 [0,0120; 0,0228] |
| REL+F | HORA | 0,770 [0,742; 0,799] | 0,269 [0,244; 0,294] | 0,207 [0,187; 0,226] | 0,873 [0,862; 0,885] | 0,0066 [0,0022; 0,0112] | 0,0183 [0,0129; 0,0234] |

Φ_S por idade:

| braço | perfil | t = 2 | t = 4 | t = 6 | t = 8 | t = 10 |
|---|---|---|---|---|---|---|
| REL | SEQ | 0,861 [0,830; 0,894] | 0,851 [0,817; 0,886] | 0,855 [0,822; 0,890] | 0,839 [0,807; 0,869] | 0,838 [0,805; 0,867] |
| REL | LUGAR | 0,922 [0,890; 0,953] | 0,888 [0,853; 0,919] | 0,906 [0,875; 0,936] | 0,918 [0,888; 0,949] | 0,904 [0,876; 0,931] |
| REL | HORA | 0,855 [0,825; 0,886] | 0,853 [0,823; 0,880] | 0,872 [0,842; 0,899] | 0,870 [0,845; 0,894] | 0,882 [0,854; 0,907] |
| REL+F | SEQ | 0,850 [0,814; 0,888] | 0,826 [0,792; 0,856] | 0,836 [0,798; 0,869] | 0,865 [0,833; 0,894] | 0,857 [0,823; 0,890] |
| REL+F | LUGAR | 0,902 [0,872; 0,931] | 0,927 [0,899; 0,956] | 0,924 [0,892; 0,954] | 0,918 [0,884; 0,949] | 0,911 [0,891; 0,930] |
| REL+F | HORA | 0,866 [0,838; 0,893] | 0,868 [0,845; 0,890] | 0,884 [0,860; 0,908] | 0,876 [0,849; 0,902] | 0,874 [0,850; 0,896] |

São seis células sem correção de multiplicidade (14.4).

### 10.2 As frases (14.4)

| braço | perfil | a hipótese | o deslocamento sozinho | o efeito amarrado |
|---|---|---|---|---|
| REL | SEQ | H-HIST | deslocar o fluxo em um sorteio faz do pet um gemeo | o efeito amarrado cresce com os dias |
| REL | LUGAR | H-HIST | deslocar o fluxo em um sorteio faz do pet um gemeo | o efeito amarrado cresce com os dias |
| REL | HORA | os dois pesam | deslocar o fluxo em um sorteio faz do pet um gemeo | o efeito amarrado cresce com os dias |
| REL+F | SEQ | H-HIST | nao se distingue do limiar nesta analise | nao se distingue de zero nesta analise |
| REL+F | LUGAR | H-HIST | deslocar o fluxo em um sorteio faz do pet um gemeo | o efeito amarrado cresce com os dias |
| REL+F | HORA | os dois pesam | deslocar o fluxo em um sorteio faz do pet um gemeo | o efeito amarrado cresce com os dias |

- **A condição do evento** vale nas seis células, para o E e para o R: o Φ⁰ fica acima de 0 em ao menos uma idade.
- **No REL+F SEQ, a régua crua do γ_R não se distingue de zero,** e por isso a frase do γ_R não se escreve ali. Nas outras cinco células,
  a crua passa junto.

**Em palavras:**
- **Amarrar o sorteio quase não muda o efeito do tapa** no SEQ e no LUGAR, nos dois braços (a H-HIST, com ρ de 0,88 a 0,96).
- **No HORA, os dois pesam:** cerca de 3/4 do efeito fica com o sorteio amarrado (ρ de 0,75 e 0,77).
- **O deslocamento sozinho faz um gêmeo:** jogar fora um único sorteio, sem tapa, deixa o pet tão longe do original quanto um gêmeo, em
  todas as idades, em 5 das 6 células. No REL+F SEQ, o IC de t = 4 encosta no limiar (0,792).

### 10.3 A expectativa E-AD2, relida sem ajuste

A E-AD2 previa a H-SORT, ou "os dois pesam" com ρ abaixo de 0,5, e Φ_S acima de 0,8.
- **A parte do ρ não se confirma:** o ρ fica de 0,75 a 0,96, nenhuma célula fica abaixo de 0,5, e quatro dão a H-HIST.
- **A parte do Φ_S se confirma** em 5 das 6 células.

**A leitura proposta no exploratório da 9.6** ("um reflexo desloca a rng de política, e o resto da vida vira outro acaso") **não se sustenta
como explicação do tapa.** O deslocamento sozinho faria um gêmeo, como o S mostra, mas o tapa que dura não depende dele: com o sorteio
amarrado, a mesma fração de pets se afasta.

### 10.4 O que a tabela mostra, além das frases (descritivo, 14.5)

- **O tudo ou nada continua com o sorteio amarrado** (a fração dos ramos por janela de quatro dias, no SEQ; o "D > 0 nos quatro" por dono à
  direita):

| braço | ramo | D = 0 nos quatro | D > 0 nos quatro | os dois | D > 0 nos quatro, por dono |
|---|---|---|---|---|---|
| REL | E | 68 % | 31 % | 2 % | aleatorio 21 %, atencioso 25 %, relapso 46 % |
| REL | R | 69 % | 29 % | 2 % | aleatorio 19 %, atencioso 24 %, relapso 43 % |
| REL+F | E | 67 % | 31 % | 2 % | aleatorio 21 %, atencioso 27 %, relapso 47 % |
| REL+F | R | 68 % | 29 % | 3 % | aleatorio 18 %, atencioso 26 %, relapso 44 % |

  A previsão da 9.6 era que a fração "D > 0 nos quatro" caísse do E para o R. Ela cai pouco, de 31 % para 29 %. Ela é maior com o dono
  relapso (43 % a 47 %) que com o atencioso e o aleatório.
- **A separação pelo M-ARB:**
  - nos ramos E que se afastam (SEQ, REL), 187 de 278 têm a contagem de sorteios do fim do dia t diferente da do original, e nos que voltam,
    0 de 608;
  - nos ramos R que se afastam, 200 de 257 também a têm, com o sorteio amarrado.

  A diferença na contagem acompanha o afastamento, mas não é a causa dele. Os números do REL+F são parecidos (`descritivo.separacao_pelo_arb`
  no `analise.json`).
- **O estado interno contra o gêmeo** (Φ^est, SEQ; o estado não depende do perfil):
  - o E fica de 0,14 a 0,31 e o R de 0,13 a 0,28, os dois maiores na idade 2;
  - o S fica de 0,52 a 0,72, abaixo do gêmeo mesmo com o comportamento igual ao de um gêmeo.
- **A réplica do E**, nos pets novos, ao lado do I7b:
  - o Φ_E fica de 0,26 a 0,30 (no I7b, de 0,26 a 0,31);
  - o γ_E fica de 0,006 a 0,018, com o IC95 acima de 0 nas seis células (no I7b, de 0,011 a 0,021);
  - o reencontro do dia 14 é de 67 % (REL) e 65 % (REL+F) dos ramos E (no I7b, 66 % e 63 %), e de 68 % e 66 % dos ramos R.

  São diferenças pequenas, entre duas amostras, e não têm leitura.
- **O ρ por idade** fica só no descritivo, sem frase:

| braço | perfil | t = 2 | t = 4 | t = 6 | t = 8 | t = 10 |
|---|---|---|---|---|---|---|
| REL | SEQ | 0,854 | 0,945 | 0,873 | 0,798 | 0,911 |
| REL | LUGAR | 0,924 | 1,005 | 0,926 | 0,902 | 0,970 |
| REL | HORA | 0,738 | 0,827 | 0,725 | 0,691 | 0,765 |
| REL+F | SEQ | 0,842 | 0,925 | 0,894 | 0,850 | 0,934 |
| REL+F | LUGAR | 0,938 | 0,999 | 0,979 | 0,858 | 1,007 |
| REL+F | HORA | 0,741 | 0,832 | 0,750 | 0,689 | 0,826 |

### 10.5 O que a análise não demonstra

- **Que o sorteio não pesa no pet:** ele pesa muito, porque um único número a mais faz um gêmeo (o S). O que a análise mostra é que o efeito
  duradouro do tapa não vem do deslocamento do fluxo.
- **Que a história é uma experiência no sentido de um animal.** "História" aqui é o que o motor e o cérebro carregam do tapa (o estado, as
  decisões do dia, o dono reagindo), separado do fluxo da rng.
- **Que o amarrado é perfeito:** 2 % dos sorteios do R caíram numa chave sem par e receberam um número de outra rng. Eles entram no ρ como
  sorteio, então o ρ subestima um pouco a parte da história.
- **O que acontece em outras idades, outros mundos, outros donos ou no cérebro A.** São seis células sem correção de multiplicidade.

### 10.6 O que isso muda para a frente (PROPOSTO)

- **O tapa muda o pet pela história em cerca de 30 % das vezes,** e em 70 % ele volta ao original. A sensibilidade extrema ao sorteio é uma
  propriedade separada: qualquer deslocamento do fluxo (um sorteio a mais) produz um gêmeo.
- **Para as perguntas seguintes (Q1, Q2):** comparar ramos com o sorteio amarrado separa o efeito de uma experiência do acaso. Sem ele, um
  efeito pode vir só de mexer no fluxo. Isso vale como recomendação de método, PROPOSTA.
- **Uma pergunta nova, PROPOSTA:** o que decide se um pet absorve o tapa ou se afasta? O dono relapso pesa (46 % contra 21 % a 25 %), e a
  fração não muda com o sorteio amarrado.

## 11. O adendo 3 do I7: o que separa absorver de se afastar (2026-11-11, Claude Code, Opus 5.5, branch `v3-individualidade-i7e`)

**O desenho:** a seção 16 do plano do I7, DECIDIDA (AD3-1 a AD3-6), com o registro da seção 17.
- **As amostras:** a descoberta são as vidas do adendo 2, nos ramos E e R. A confirmação são as vidas do I7b, nos ramos E.
- **Nenhuma vida nova:** os candidatos saem do replay do original até o momento do tapa.
- **As duas fases:** a fase 1 leu 3 600 momentos em 7 min. Os níveis da descoberta entraram no registro antes da fase 2 (a energia, a fome e o
  humor pela mediana; a ação mais comum, `dormir`).
- **Os artefatos:** `artifacts_v3_individualidade_i7_ad3/`, com o `meta.json`, o `niveis.json` e o `analise.json` versionados. O
  `candidatos.jsonl` fica local, com o sha256 no `meta.json`.
- **Os ramos com grupo:** 1768 na descoberta E (560 se afastam),
  1753 na descoberta R (521) e 1758 na confirmação
  (572).

### 11.1 A tabela (Δ = a fração "se afasta" no primeiro nível menos no segundo; o IC95 pelo bootstrap sobre as sementes, 2 000 reamostras)

| candidato (o primeiro nível) | descoberta, E | descoberta, R | confirmação, E | a frase (16.4) |
|---|---|---|---|---|
| C-ACAO (a ação `dormir`) | −0,005 [−0,064; +0,051] | +0,003 [−0,053; +0,058] | −0,016 [−0,070; +0,037] | nao separa nesta analise |
| C-BRACO (o braço REL+F) | +0,006 [−0,024; +0,034] | +0,009 [−0,022; +0,038] | +0,024 [−0,009; +0,055] | nao separa nesta analise |
| C-DONO (o dono relapso) | +0,232 [+0,184; +0,282] | +0,219 [+0,167; +0,270] | +0,174 [+0,122; +0,223] | separa |
| C-ENERGIA (a energia abaixo da mediana) | −0,068 [−0,111; −0,023] | −0,072 [−0,110; −0,033] | −0,039 [−0,089; +0,015] | so na descoberta: nao se confirma nos pets do I7b |
| C-FOME (a fome acima da mediana) | +0,062 [+0,007; +0,113] | +0,068 [+0,017; +0,117] | +0,034 [−0,013; +0,082] | so na descoberta: nao se confirma nos pets do I7b |
| C-HUMOR (o humor abaixo da mediana) | +0,095 [+0,047; +0,143] | +0,096 [+0,049; +0,143] | +0,066 [+0,019; +0,113] | separa |
| C-IDADE (a idade t ≤ 4) | +0,091 [+0,043; +0,138] | +0,091 [+0,044; +0,136] | +0,004 [−0,051; +0,058] | so na descoberta: nao se confirma nos pets do I7b |

São sete candidatos sem correção de multiplicidade, e a repetição na confirmação faz esse papel (16.4).

### 11.2 As frases

- **Separam nas duas amostras:**
  - **o dono relapso:** de 17 a 23 pontos a mais de pets que se afastam. Ele foi visto na descoberta antes do plano, então vale a
    confirmação, +0,174 [+0,122; +0,223];
  - **o humor baixo no momento do tapa:** de 7 a 10 pontos a mais.
- **Só na descoberta,** sem se confirmar nos pets do I7b: a energia baixa (menos pets se afastam), a fome alta e a idade cedo (t ≤ 4).
- **Não separam nesta análise:** a ação em curso e o braço.

### 11.3 O que a tabela mostra, além das frases (descritivo, 16.5)

- **O dono e o humor juntos** (a fração que se afasta em cada célula):

| conjunto | outros donos, humor alto | outros donos, humor baixo | relapso, humor alto | relapso, humor baixo |
|---|---|---|---|---|
| descoberta|E | 17 % (n = 476) | 29 % (n = 700) | 39 % (n = 418) | 68 % (n = 174) |
| descoberta|R | 15 % (n = 474) | 28 % (n = 692) | 37 % (n = 414) | 62 % (n = 173) |
| confirmacao|E | 21 % (n = 440) | 30 % (n = 728) | 38 % (n = 439) | 63 % (n = 151) |

  Os dois se somam. Com o dono relapso e o humor baixo, perto de 2/3 dos pets se afastam, contra 15 % a 21 % com os outros donos e o humor
  alto.
- **O efeito imediato decide quase tudo:**

| conjunto | o resto do dia t igual ao original: se afastam | o resto do dia t diferente: se afastam |
|---|---|---|
| confirmacao|E | 3 % (n = 1194) | 96 % (n = 564) |
| descoberta|E | 2 % (n = 1212) | 96 % (n = 554) |
| descoberta|R | 2 % (n = 1217) | 92 % (n = 534) |

  Se o tapa não muda o resto do dia em que acontece, o pet quase nunca se afasta depois. Se muda, ele quase sempre se afasta. Isso é parte do
  efeito, e não uma condição anterior a ele, então fica só no descritivo.
- **Os drives em média, por grupo** (a energia, a fome e o humor, na escala de 0 a 1):

| conjunto | grupo | energia | fome | humor |
|---|---|---|---|---|
| confirmacao|E | absorve | 0,390 | 0,554 | 0,612 |
| confirmacao|E | afasta | 0,407 | 0,569 | 0,560 |
| descoberta|E | absorve | 0,380 | 0,540 | 0,617 |
| descoberta|E | afasta | 0,403 | 0,567 | 0,561 |
| descoberta|R | absorve | 0,381 | 0,539 | 0,617 |
| descoberta|R | afasta | 0,403 | 0,572 | 0,559 |

### 11.4 O que a análise não demonstra

- **Causa.** O dono relapso e o humor baixo estão associados ao afastamento nas duas amostras, mas a análise não diz se eles o causam. O humor
  baixo pode ser efeito do dono relapso, e a tabela cruzada mostra que os dois se somam, sem separar um do outro como causa.
- **Que os outros candidatos não importam.** "Só na descoberta" quer dizer que não se repetiram nos pets do I7b, e não que o efeito é zero.
- **O mecanismo:** por que o humor baixo deixa o tapa pegar. A análise não lê o cérebro.

### 11.5 O que isso muda para a frente (PROPOSTO)

- **Uma resposta à pergunta do adendo 3:** um pet com o dono relapso e o humor baixo no momento do tapa se afasta muito mais do original.
  Quando o tapa muda o próprio dia, o efeito dura.
- **Um desenho causal possível depois, PROPOSTO (a AD3-6 deixou para depois):** dar o tapa só nos momentos de humor baixo e só nos de humor
  alto, no mesmo pet e com o sorteio amarrado (o método do adendo 2). Isso testaria se o humor decide, separado do dono. Pede um plano novo.
