# Equilíbrio do combate em tempo real — relatório por fase

O plano está em `docs/PLANO_EQUILIBRIO_COMBATE_TR.md` (#459), e as decisões DE-1 a DE-7 foram DECIDIDAS pelo Matheus em 2026-10-30, pela
recomendação. Todo número novo é PROPOSTO e vem de um artefato em `web/app/scripts/medicoes/equilibrio_tr/`. As fases de ajuste usam só as
sementes de calibração (68101…68505). A conferência (70101…70505) roda uma vez, na fase 5.

## Fase 1 — o relógio (T-1…T-5)

Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`, 2026-10-30.

### 1.1 O que mudou no código (nenhuma luta do jogo muda)

- **Os números do relógio viajam nas regras da luta.** Os que a rodada pode mudar (`RelogioTR`, em
  `web/app/motor/combate_tr/constantes_tr.ts`) vão em `RegrasV21.relogio` e no estado da luta (`EstadoTR.C`).
  - A v13 usa os de hoje (`RELOGIO_V13`), e as vidas v13 continuam iguais (o gabarito confere).
  - O limite, a morte súbita (D-5), o instante do golpe (D-1) e a geometria do chão ficam em `CTR_TR` e não entram.
- **O relógio candidato da v14 é `RELOGIO_V14`, PROPOSTO, e ainda não pertence a nenhuma versão de pet.** A v14 (DE-1) liga uma vez só,
  no fim da rodada, com os números de todas as fases. Se cada fase ligasse os seus, a fase 2 mudaria as vidas v14 já jogadas (a regra
  "uma versão por mecânica").
- **A bancada:** `web/app/scripts/equilibrio_tr/fase1_relogio.ts`.
  - Os 8 bots canônicos das formas adultas, em perfil neutro e com as regras `CV21E_TR`, jogam todos os pares, com o espelho e os lados
    trocados.
  - São as 5 bases da faixa × 20 sementes = 200 lutas por par, 7 200 lutas no total, e a rodada leva perto de 5 s.
  - A Cidadela (3 lutas contra o líder) entra com cada forma como o pet.
- **O aviso do chip coberto (DE-3):** `regraQueCobre`, em `web/app/motor/gambits_pet.ts`, e o aviso em `TelaItens`. A lista e as lutas não
  mudam.

### 1.2 A grade (só as sementes de calibração; no máximo 4 processos em paralelo)

- **Rodada 1, um número por vez** (`fase1/grade1/`): nenhum número do relógio tira os pares defensivos do limite. O pior par fica em
  100%, menos com o empurrão em 0 (0,775). O médio em 120 leva o T-5 a 0,71.
- **Rodada 2, o empurrão 0 com o médio** (`fase1/grade2/`): `e0m120` tira o total no limite de 0,16 para 0,052.
- **Rodada 3, o recuo e a arrancada** (`fase1/grade3/`): `r06arr8` (o recuo 0,6 e a arrancada 500 px/s) é o melhor total (0,047).
- **Três rodadas é o limite da fase** (plano, seção 5). A fase para com o melhor candidato.

| número (`RelogioTR`) | v13 | candidato v14 (PROPOSTO) | por quê |
|---|---|---|---|
| `empurrao` | 6 px | 0 | o empurrão do golpe corpo a corpo tirava o atacante do contato, e as listas defensivas não voltavam |
| `medio` | 150 px | 120 px | a faixa média mais curta faz as listas saírem do longe mais cedo e reagirem ao preparo |
| `recuo` | 0,8 | 0,6 | quem recua o tempo todo (a sentinela) é alcançado |
| `arrancada` | 420 px/s | 500 px/s | idem |
| os outros (ritmo, atordoamento, andar, projétil, perto, contato) | — | iguais | nenhum melhorou as metas na rodada 1 |

### 1.3 As metas, antes e depois (calibração)

Os arquivos são `fase1/antes_calibracao.json` (o relógio v13) e `fase1/depois_calibracao.json` (o candidato v14).

| # | meta | antes (v13) | depois (candidato v14) | passa? |
|---|---|---|---|---|
| T-1 | média de 40 a 60 s, mediana de 35 a 55 s | 44,5 s / 41,1 s | 41,4 s / 36,3 s | sim (antes e depois) |
| T-2 | no limite, ≤ 5% em cada par | total 0,160; pior par 1,00 | total 0,047; pior par 0,56 | **não fechou** |
| T-3 | a Cidadela no p90 ≤ 3 min | 68,3 s | 64,4 s | sim |
| T-4 | o lado A no espelho, entre 0,45 e 0,55 (só os nocautes) | 0,512 | 0,518 | sim |
| T-5 | "rival preparando" decide ≥ 50% das vezes livres | 0,464 | 0,769 | sim (depois) |

**Os piores pares no limite, depois:** muralha × sentinela 0,56, vigia × vigia 0,40, furioso × emboscador 0,24, furioso × sentinela 0,21.

### 1.4 O que não fechou e o que fica

- **T-2 por par** fica com o resultado como está. Os pares que sobram no limite são de listas defensivas (a muralha, a vigia, a sentinela),
  e nenhum número do relógio os resolve sem piorar o resto. A alavanca é a lista das formas, que é a fase 2.
- **O diagnóstico do T-5:** com o candidato, a regra "rival preparando" decide 77% das vezes em que o pet está livre durante o preparo.
  Mas só 60% dos preparos do rival têm alguma decisão livre do pet. Essa segunda conta é diagnóstico, não meta.
- **A conferência não rodou:** ela roda uma vez, na fase 5, com todos os números congelados.

## Fase 2 — as formas (F-1…F-7)

Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`, 2026-10-30.

### 2.1 O que mudou no código (nenhuma luta do jogo muda)

- **As listas candidatas da v14 são `LISTAS_V14`** (`web/app/motor/bots.ts`), PROPOSTAS. Como o `RELOGIO_V14`, ainda não pertencem a
  nenhuma versão de pet: só a bancada as usa, e a v14 (DE-1) liga tudo no fim da rodada. Os bots e os pets v13 ficam com as listas de hoje
  (o teste `test/listas_v14.test.ts` confere isso, e que cada lista cabe na forma dela).
- **A bancada:** `web/app/scripts/equilibrio_tr/fase2_formas.ts`, em cima do relógio candidato da fase 1. As variantes da grade estão em
  `variantes_fase2.ts`.
  - Os lutadores são os bots canônicos (a forma, o caráter canônico, sem treino, a semente da forma), como na M-A1 da rodada das formas.
  - As linhas do Champion e os ramos do Rookie lutam com a mesma espécie dos dois lados, em rodízio pelas sementes.
  - No limite, a luta fica com a fração de vida (sem desafiado), porque são lutas de força e os lados trocam.
  - São 200 lutas por célula, perto de 25 mil lutas por rodada, em perto de 13 s.
- **A bancada da fase 1 ganhou `--listas v14`,** para conferir que as metas do relógio continuam com as listas novas.
- **As alavancas são só as listas.** As passivas vêm de `CV21` e `CSO`, que são conferidos contra o Python e não mudam (plano, seção 4).

### 2.2 O diagnóstico (antes da grade)

- **As formas de longe quase não vencem** (o emboscador 0,05; de longe × de perto 0,003 no Ultimate e 0,007 no Champion).
- **Com o relógio v13, o resultado é o mesmo** (`fase2/diagnostico_relogio_v13.json`): a causa não é a fase 1.
- **Uma luta do emboscador contra o duelista passa 93% do tempo de perto.** As lutas começam a 130 px, e o rival chega ao contato em
  menos de uma ação (2 s). Preso na cerca, o emboscador continua mandando "recuar". Ele também só marcava e disparava depois de 10 s
  (`turno_execucao 5`).
- **O recuo igual ao andar, ou acima dele, quase não muda nada** (`fase2/diagnostico/`, só diagnóstico e não alavanca): de longe × de
  perto fica perto de 0,05. O que falta às formas de longe não é espaço. Com a base de hoje, o disparo (6 de dano por 20 de Guts) perde
  para o pesado de perto, e a base não muda nesta rodada.

### 2.3 A grade (só as sementes de calibração; no máximo 4 processos em paralelo)

- **Rodada 1, uma troca por vez** (`fase2/grade1/`):
  - "de perto, golpe rápido" no lugar de "de perto, recuar" equilibra as 4 linhas do Champion (de 0,49 a 0,51);
  - "contra o preparo de perto, golpe rápido" (interromper no lugar da esquiva) ajuda a sentinela;
  - o emboscador marcar e disparar desde o começo sobe de 0,05 para 0,25.
- **Rodada 2, as combinações e as sombrias** (`fase2/grade2/`):
  - o predador ganha o disparo, que a lista dele não tinha;
  - o bastião rachado ganha o contra-golpe de perto;
  - a distância (F-2) cai para 0,50, e o ciclo (F-3) passa.
- **Rodada 3, os ajustes finos** (`fase2/grade3/`):
  - o sereno do Rookie avança de qualquer distância, como o arisco, e fica com a regra final de defender;
  - o bastião rachado só devolve o golpe com 40 de Guts;
  - a muralha só devolve o golpe rápido frequente com 40 de Guts.
- **O candidato é a variante `r3a`.** Três rodadas é o limite da fase (plano, seção 5).

| lista (`LISTAS_V14`) | o que muda em relação à de hoje |
|---|---|
| `cacador` (Champion) | de perto, golpe rápido no lugar de recuar |
| `sentinela` | contra o preparo de perto, golpe rápido no lugar da esquiva |
| `emboscador` | contra o preparo de perto, golpe rápido; marca e dispara desde o começo (sai `turno_execucao 5`) |
| `muralha` | o contra-golpe contra o golpe rápido frequente só com 40 de Guts |
| `sereno` (Rookie) | avança de longe e do médio; de perto, golpe rápido com 20 de Guts; a final continua defender |
| `predador` (sombria) | marca de longe e dispara do médio e de longe |
| `bastiao_rachado` (sombria) | de perto, contra-golpe com 40 de Guts |

### 2.4 As metas, antes e depois (calibração)

Os arquivos são `fase2/antes_calibracao.json` (as listas de hoje, com o relógio candidato) e `fase2/depois_calibracao.json` (as
`LISTAS_V14`, igual à `grade3/r3a.json`).

| # | meta | antes | depois | passa? |
|---|---|---|---|---|
| F-1 | as 8 formas entre 0,40 e 0,60 | 5 fora: muralha 0,80, tita 0,73, furioso 0,62, sentinela 0,21, emboscador 0,05 | 5 fora: tita 0,73, muralha 0,71, furioso 0,62, emboscador 0,25, sentinela 0,23 | **não fechou** |
| F-2 | a mais forte − a mais fraca ≤ 0,20 | 0,75 | 0,50 | **não fechou** |
| F-3 | toda forma vence ≥ 2 das outras 7 | o emboscador vence 0 | todas ≥ 2 | sim (depois) |
| F-4 | as linhas entre 0,40 e 0,60 | Champion: o caçador 0,16; Rookie: o sereno × arisco 0,14 | Champion: de 0,49 a 0,51; Rookie: 0,605 | **não fechou** (só o Rookie, a 0,005) |
| F-5 | de longe × de perto entre 0,45 e 0,55 | Champion 0,007; Ultimate 0,003 | Champion 0,345; Ultimate 0,116 | **não fechou** |
| F-6 | nenhuma passiva muda a força em mais de 0,10 | o espelho 0,109 | o espelho 0,19; a sentinela 0,118 | **não fechou** |
| F-7 | cada sombria entre 0,45 e 0,65 | devastador 0,68; bastião 0,23; predador 0,26; colosso partido 0,65 | devastador 0,68; bastião 0,67; predador 0,23; colosso partido 0,65 | **não fechou** |

**As metas do relógio com as listas novas** (`fase2/relogio_com_listas_calibracao.json`): T-1 41,9 s / 38,0 s, T-3 64,3 s no p90, T-4
0,513 e T-5 0,702 continuam passando. O T-2 fica como na fase 1 (total 0,050, pior par 0,56).

### 2.5 O que não fechou e o que fica

- **As formas de longe (F-1, F-5)** sobem, mas não chegam à faixa. A sentinela e o emboscador ficam perto de 0,25 contra as outras 7. A
  causa é a base (o disparo contra o pesado de perto, no tempo real), que não muda nesta rodada; nem as listas nem o recuo fecham isso.
  Uma alavanca possível seria um número só do tempo real para o disparo, mas ela muda a base e pede uma decisão do Matheus. Fica como
  questão aberta, sem número.
- **O tita, a muralha e o furioso (F-1)** seguem acima de 0,60. Na rodada 3, as trocas que os enfraqueciam pioravam outra forma (o tita
  sem a pele contra o preparo foi a 0,87).
- **F-6:** o efeito da passiva do espelho e da sentinela passa de 0,10 depois das listas. A hipótese, não medida, é que as listas
  novas das formas de longe disparam mais, e a passiva do espelho devolve o disparo. As passivas são da base e não mudam.
- **F-7:** o predador fica em 0,23. Sem recuar (a passiva dele), ele cai no mesmo problema das formas de longe. O devastador e o bastião
  ficam um pouco acima de 0,65.
- **F-4, o Rookie:** 0,605, a 0,005 da faixa. Fica como está, porque a fase não tem uma quarta rodada.
- **T-2 por par**, que a fase 1 deixou para as listas, também não fechou: nenhuma variante mexeu nos pares defensivos sem piorar as
  formas.
- **A conferência não rodou:** ela roda uma vez, na fase 5.
