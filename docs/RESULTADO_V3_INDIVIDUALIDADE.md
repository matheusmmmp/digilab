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
