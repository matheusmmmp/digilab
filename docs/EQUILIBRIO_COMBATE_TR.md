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

## Fase 3 — o estágio, o treino e o aprendizado (P-1…P-4)

Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`, 2026-10-30.

### 3.1 O que mudou no código (nenhuma luta do jogo muda)

- **Nenhum número novo.** P-1 e P-2 passam com a escala de hoje (`CESC_V9`). P-3 e P-4 não têm alavanca nesta fase (seção 3.4), então
  a fase não rodou grade nem gravou candidato.
- **`GambitsPet.semear` aceita a lista de partida.** O padrão é a semente de hoje, então os pets v13 não mudam.
- **`regraDe` conhece as regras das `LISTAS_V14`,** como já conhecia as da V21E. Nenhum pet de hoje as tem na semente nem nas candidatas.
  O teste `test/listas_v14.test.ts` confere as duas mudanças.
- **A bancada:** `web/app/scripts/equilibrio_tr/fase3_estagio.ts`, em cima do `RELOGIO_V14` e das `LISTAS_V14`.
  - O pet típico é a forma de referência do estágio (Rookie: os 2 ramos; Champion: as 4 linhas; Ultimate e Mega: as 8 formas, o Mega
    com as listas do Ultimate), com o caráter canônico e o treino uniforme do treino típico (`CIT.tipico`) ou nenhum. O treino é
    absoluto e a luta é na escala, como na campanha.
  - O pet da bancada não é uma vida: não tem dono nem cuidado, e o epsilon é o do bot (`CV.eps`), sem a disciplina e a experiência.
  - **P-1** (o método da M-B1 da rodada geral): o de baixo com o treino típico contra o de cima sem treino. São as 4 espécies de cada
    lado, 10 sementes por confronto e os dois lados, e o limite fica com o de cima (o desafiado).
  - **P-2:** no mesmo estágio, a mesma forma e a mesma espécie, o típico contra o sem treino. São 100 sementes por forma, os dois lados,
    e no limite a luta fica com a fração de vida.
  - **P-3 e P-4:**
    - o pet típico do Champion e do Ultimate semeia a lista, luta `CAT.sparring` (10) lutas contra o rival sugerido do estágio e aprende
      com cada uma (`GambitsPet.aprender`);
    - o rival sugerido é o primeiro rival do primeiro lugar do estágio: o Tortomon na Torre de pedra (um desafiante) e o Myotismon na
      Cidadela (o líder, com a regra da arena: 3 lutas, e cada luta da série conta);
    - **P-4** é a fração dos pets com a taxa ≥ 0,8 nessas lutas;
    - **P-3** é a lista aprendida contra a de partida, com o mesmo perfil.
  - O custo é de perto de 25 s nas três partes.

### 3.2 As metas (calibração; `fase3/antes/p1.json`, `p2.json`, `p34.json`)

| # | meta | medido (o mesmo antes e depois: nenhum número mudou) | passa? |
|---|---|---|---|
| P-1 | o de baixo vence o de cima ≤ 0,10 (pontos); dois estágios acima, nenhuma vitória | Rookie × Champion 0,000; Champion × Ultimate 0,070; Ultimate × Mega 0,030; Rookie × Ultimate e Champion × Mega, 0 vitórias | sim |
| P-2 | o típico vence o sem treino ≥ 0,80 no mesmo estágio | a pior forma de cada estágio: Rookie 1,00; Champion 0,995 (colosso); Ultimate 1,00; Mega 1,00 | sim |
| P-3 | a lista aprendida vence a de partida entre 0,55 e 0,70 | Champion 0,49 (caçador 0,16, brigão 0,70); Ultimate 0,30 (duelista 0,02, muralha 0,025, espelho 0,05, furioso 0,87) | **não fechou** |
| P-4 | ≥ 80% dos pets do estágio chegam a 0,8 nas 10 lutas | Champion 0,76 (guardião 0,57, colosso 0,59); Ultimate 0,755 (sentinela 0,00, emboscador 0,04; as outras 6, 1,00) | **não fechou** |

As metas das fases 1 e 2 não mudam: a bancada delas reproduz os artefatos gravados.

### 3.3 O diagnóstico do P-3 (`fase3/diagnostico_ordem_duelista.json`)

- **O pet quase não troca regras** nas 10 lutas (0 trocas no duelista; no máximo 0,8 por pet, na sentinela; `trocas_por_pet` em
  `p34.json`). O que muda é a ordem: a lista é reordenada pela nota de cada regra.
- **A regra genérica sobe para o topo.** No duelista, "de perto → golpe rápido" é a última regra da semente: a de reserva, quando nenhuma
  específica vale. Contra o Myotismon, ela dispara muito e ganha nota alta (0,17). Por isso vai para o primeiro lugar e encobre as
  regras específicas de perto (o preparo, a defesa contra o golpe frequente). Com essa lista, o duelista perde da própria semente 98
  vezes em 100.
- **A alavanca é o aprendizado:** a nota, o passo, o limiar de troca (`GA`) e a ordem pela nota. Os números de `GA` são conferidos
  contra o Python (`constantes.test.mjs`) e ficam fora das alavancas desta rodada (plano, seção 4). Um número ou uma regra própria do
  tempo real para o aprendizado pede uma decisão do Matheus.

### 3.4 O que não fechou e o que fica

- **P-3** não fechou, e esta fase não tem alavanca para ele (seção 3.3). Fica como questão aberta, sem número.
- **P-4** não fechou. Pela DE-4 (DECIDIDA), o 0,8 fica, e quem se ajusta são os rivais (os fatores), na fase 4. A fase 4 começa com:
  - **Champion:** o Tortomon contra o guardião e o colosso (0,57 e 0,59);
  - **Ultimate:** a sentinela e o emboscador contra o Myotismon (0,00 e 0,04). Essa parte dependia da resposta do Matheus sobre as formas
    de longe (fase 2, seção 2.5). Ele decidiu pelo multiplicador do disparo (DE-8), e o passo do disparo, abaixo, mostra que o 6× fecha
    essa parte, mas reprova o T-1.
- **A conferência não rodou:** ela roda uma vez, na fase 5.

## O passo do disparo (depois da fase 3; DE-8)

Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`, 2026-10-30. A decisão do Matheus (2026-10-30, DECIDIDA pela recomendação do
coordenador; o plano a registra como DE-8): **um número próprio do tempo real para o disparo**, um multiplicador do dano dele no candidato
v14, calibrado nesta rodada. A base (o disparo e o pesado de `CV` e do perfil) não muda.

### O que mudou no código

- **`RelogioTR.disparo`** (`web/app/motor/combate_tr/constantes_tr.ts`) multiplica o dano do disparo na luta em tempo real
  (`combate_tr/luta.ts`). Na v13 vale 1, e as vidas v13 conferem iguais.
- **As bancadas das fases 2 e 3 ganharam `--disparo X`;** a da fase 1 já aceitava `--relogio '{"disparo":X}'`.
- **O candidato liga o 6×** (`RELOGIO_V14.disparo = 6`, PROPOSTO), pela DE-9 (seção abaixo). Nenhuma luta do jogo muda: a v14 só liga
  no fim da rodada (DE-1).

### A grade (só as sementes de calibração; no máximo 4 processos em paralelo; `disparo/grade1/` a `grade3/`)

- Cada rodada mede as metas das formas (F-1 a F-7) com as `LISTAS_V14`, para valores de 1,5 a 8 (rodada 1: 1,5 a 3; rodada 2: 4 a 8;
  rodada 3: 4,5 a 7).
- A melhor nota das formas é **6×** (`grade2/d6.json`). A nota é a soma da distância de cada meta F à faixa dela.
- O Ultimate de longe × de perto não chega à faixa com nenhum valor: fica em 0,25 com 8×. O caçador do Champion passa de 0,60 acima de
  3×.

### A conferência das outras metas

- **Todo valor acima de 1 reprova o T-1 da fase 1** (`disparo/relogio/`). A luta média cai para 39,4 s com 1,5×, 36,0 s com 3× e 34,8 s
  com 6×, abaixo dos 40 s da DE-7. Com menos lutas no limite, a média encurta.
- **Pela regra do plano** (seção 5: "um ajuste que reprova uma meta já fechada de uma fase anterior volta atrás"), **o candidato fica em
  1**. F-1 e F-5 ficam como na fase 2.
- **O que o 6× mudaria,** medido em todas as metas (`disparo/conferencia_d6/`). É uma decisão para o Matheus, porque troca o T-1 pelo
  resto:

| meta | com o candidato (disparo 1) | com 6× | |
|---|---|---|---|
| T-1 | 41,9 s / 38,0 s | 34,8 s / 32,9 s | **reprova** (fechada na fase 1) |
| T-2 | total 0,050; pior par 0,56 | total 0,021; pior par 0,40 | melhora; não fecha |
| T-3, T-4, T-5 | passam | passam (62,0 s; 0,512; 0,697) | iguais |
| F-1 | 5 fora | 4 fora: espelho 0,35, emboscador 0,39, muralha 0,63, tita 0,69 | melhora; não fecha |
| F-2 | 0,50 | 0,34 | melhora; não fecha |
| F-3 | passa | passa | igual |
| F-4 | Champion de 0,49 a 0,51; Rookie 0,605 | o caçador 0,68; Rookie 0,605 | piora no Champion |
| F-5 | Champion 0,345; Ultimate 0,116 | Champion 0,533; Ultimate 0,198 | o Champion fecha; o Ultimate, não |
| F-6 | espelho 0,19; sentinela 0,118 | espelho 0,111 | melhora; não fecha |
| F-7 | 3 fora (devastador 0,68; bastião 0,67; predador 0,23) | só o predador fora (0,21) | melhora; não fecha |
| P-1, P-2 | passam | passam | iguais |
| P-3 | Champion 0,49; Ultimate 0,30 | Champion 0,573; Ultimate 0,39 | o Champion fecha |
| P-4 | Champion 0,76; Ultimate 0,755 | Champion 0,75; Ultimate 1,00 | o Ultimate fecha |

- **A recomendação, com o custo de errar:** se o Matheus aceitar uma luta média perto de 35 s (abaixo da DE-7), o 6× fecha F-5 no
  Champion, P-3 no Champion e P-4 no Ultimate, e quase fecha F-6 e F-7. O custo é a luta mais curta: as séries ficam mais rápidas, e as
  regras aprendidas têm menos tempo para pesar (o custo que a DE-7 registrou). Se a DE-7 ficar, o disparo fica em 1, e a fase 4 começa
  com as formas de longe fracas. A decisão é dele, e nenhum número muda até lá.

### A decisão (DE-9)

- **O Matheus seguiu a recomendação** (2026-10-30; o plano a registra como DE-9): o `RELOGIO_V14` liga o disparo a **6×**, PROPOSTO.
- **O T-1 fica reprovado e registrado como está** (34,8 s / 32,9 s; `disparo/conferencia_d6/relogio_calibracao.json`). É uma **exceção
  à DE-7**, aceita pelo Matheus no chat da coordenação: a faixa de 40 a 60 s continua a meta do T-1, e a regra da seção 5 do plano não se
  aplica a este número.
- **As metas do candidato passam a ser as da coluna "com 6×"** da tabela acima, medidas com o mesmo relógio (`disparo/conferencia_d6/`,
  o commit `24bf93a`, o mesmo código de hoje com `--disparo 6`). A fase 4 parte deste candidato.
- **As bancadas** agora leem o 6× do `RELOGIO_V14`; os artefatos das fases 1 a 3 com disparo 1 se reproduzem com `--disparo 1`.

## Fase 4 — a progressão, o fim de jogo e os itens (G-1 a G-6, I-1 a I-5; o P-4 pelos rivais)

Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`, 2026-10-30. Em cima do candidato das fases 1 a 3, com as duas decisões do Matheus
de 2026-10-30 (no chat da coordenação; o plano as registra):
- **a DE-9:** o disparo a 6× no `RELOGIO_V14`, com a exceção à DE-7;
- **a DE-10:** a regra de reserva (a última da lista de partida) fica fixa no fim e não entra na reordenação pela nota
  (`GambitsPet.reservaNoFim`), só no candidato v14. Também na lista sem o dono (o Lago e o Palácio), e os chips de regra entram antes dela.
  Os pets v13 não mudam: o gabarito das vidas v13 confere igual.

### A bancada

- **`web/app/scripts/equilibrio_tr/fase4_progressao.ts`**, uma parte por meta (g1 a g6, i2 a i5; o I-1 sai do g1).
  - **Os pets:** o pet típico de cada forma do estágio, nas 4 espécies, com a lista candidata da forma e a escala da campanha (`CESC_V9`).
  - **Os rivais de forma canônica** (os Megas da Liga, das instalações e da Fábrica, os rivais do Salão) lutam com a lista candidata da
    forma deles. Os líderes e os desafiantes lutam com a lista de hoje.
  - **O limite** fica com o desafiado (o líder, o NPC ou o rival).
- **As sementes:** 100 por confronto (5 bases × 20), só as de calibração.
- **O P-4** segue na bancada da fase 3, com o fator do rival sugerido (`--fator-rival`).
- **Os fatores candidatos** são `FATORES_V14` (`combate_tr/constantes_tr.ts`, PROPOSTOS). As tabelas de hoje não mudam, e o teste
  `listas_v14` confere.

### Os ajustes (só as sementes de calibração; no máximo 3 rodadas e 4 processos)

- **Rodada 1, os líderes, os desafiantes e o Salão** (`fase4/grade1/`): cada alavanca de 0,5 a 4,0, de 0,1 em 0,1.
  - **A regra de escolha:** um fator só muda quando a meta dele não passa hoje e algum valor a faz passar; entre os que passam, o de maior
    folga. Onde nada passa, o fator fica.
  - **O que mudou:**
    - a Torre, 1,5 → 1,8;
    - o Tortomon, 1,53 → 1,4: é também o rival do P-4 do Champion, então a DE-4 entra aqui. A grade do P-4 está em `fase4/grade1/p4/`;
    - o Salão do Rookie, 1,15 → 1,2;
    - o Salão do Champion, 1 → 1,6.
- **Rodadas 1 e 2, a Liga** (`fase4/liga/`, `busca_liga_f4.py`): busca por coordenadas, líder a líder, de 0,1 a 2,5.
  - **A ordem, registrada antes de rodar:** mais formas na faixa; depois a menor falta até a faixa; depois a menor mudança.
  - **O resultado:** a Campina vai de 0,4 a 0,2 e a Torre de 0,3 a 0,8. A segunda passada não muda nada.
- **Rodada 1, a carta de Fôlego** (`fase4/grade1/cartas/`), de 20 a 80 de guts: o efeito satura em 0,025 com os fatores de hoje. Ela
  fica em 20.

### As metas do candidato (calibração; `fase4/depois/`; o antes com os fatores de hoje está em `fase4/antes/`)

| # | meta | antes (fatores de hoje) | depois (`FATORES_V14`) | passa? |
|---|---|---|---|---|
| G-1 | os líderes: sem treino ≤ 0,05; com o típico ≥ 0,80; a pior forma ≥ 0,50 | passa só a Campina | passam a Campina e a Torre (sem 0,04; com 0,885). Ficam fora a Floresta (com 0,535; o guardião 0,06), a Cidadela (com 0,74; a sentinela 0,20), o Lago (a sentinela 0,35) e a Espiral (sem 0,069; a sentinela 0,48) | **não fechou** |
| G-2 | os desafiantes: sem ≤ 0,30; com ≥ 0,80; a pior ≥ 0,50 | o Tortomon com 0,74 | os 4 passam (o Tortomon: sem 0,28, com 0,88) | sim |
| G-3 | a Liga: toda forma com título entre 0,25 e 0,85 | a sentinela 0,11, o emboscador 0,06, o duelista 0,96, o vigia 0,88 | de 0,36 (emboscador) a 0,85 (vigia) | sim |
| G-4 | a Torre e o Palácio: a melhor forma vence a 1ª luta ≥ 0,70, a pior ≥ 0,40 | 1,00 e 0,81 | 1,00 e 0,81 | sim |
| G-5 | a Fábrica: uma série com o melhor alugado em ≥ 0,25 | 0,40 | 0,40 | sim |
| G-6 | o Salão: cada nível entre 0,70 e 0,95 | o Rookie 0,965, o Champion 0,98 | 0,895; 0,8175; 0,8775; 0,8975 | sim |
| I-1 | sem treino, com os melhores itens, cada líder ≤ 0,05 | 0,0825 (a Torre) | 0,069 (a Espiral) | **não fechou** |
| I-2 | P-1 com os melhores itens | passa (Champion × Ultimate 0,055) | passa | sim |
| I-3 | com o melhor item, a força de cada forma ≤ 0,60 | a tita 0,745, o furioso 0,624 | igual (os fatores não entram na matriz) | **não fechou** |
| I-4 | cada carta muda a taxa contra o líder do nível em ≥ 0,03 | o Fôlego 0,023, a Foco 0,008 | o Fôlego 0,032, a Cura 0,064, a Foco 0,013 | **não fechou** (a Foco) |
| I-5 | cada chip de regra dispara em ≥ 1 de 2 lutas, sem estar coberto | de 0,005 a 0,11 | igual | **não fechou** |
| P-4 | ≥ 80% dos pets chegam a 0,8 | Champion 0,64 (com a DE-10); Ultimate 0,94 | Champion 0,875; Ultimate 0,94 | sim |

**A reconferência das metas T, F e P** com a DE-9, a DE-10 e os fatores (`fase4/depois/`):
- **T e F saem iguais aos de `disparo/conferencia_d6/`**: os bots não aprendem e não têm fator. Ficam:
  - **T-1 reprovado** (34,8 s / 32,9 s; a exceção da DE-9), T-2 não fecha (o pior par 0,40), e T-3, T-4 e T-5 passam;
  - **F-1 não fecha** (fora: espelho, muralha, emboscador e tita), nem F-2 (0,34), F-4 (o caçador do Champion 0,68), F-5, F-6 e F-7;
  - F-3 passa.
- **P-1 e P-2 passam** (P-1 sai igual).
- **P-3 não fecha:** Champion 0,485 e Ultimate 0,458.
  - **Com a DE-10 sozinha** (`fase4/conferencia_de10/`), o Ultimate sobe de 0,39 para 0,458. O Champion cai de 0,573 para 0,515, e a
    0,485 com o Tortomon a 1,4.
  - **Na lista aprendida do espelho e da muralha**, a lista quase não muda (nenhuma troca), e a aprendida perde da semente (0,065 e 0,04).
    A causa é a ordem nova pela nota, que tira da frente as regras que ganhavam. Não há alavanca de número para isso nesta fase.
- **P-4 passa.**

### O que não fechou e por quê

- **G-1 (4 líderes) e I-1:** o fator não chega lá. Ele sobe e desce o líder para todas as formas juntas, e o que falta é a forma de longe
  (a sentinela) ou o guardião contra o líder. Descer o fator até a pior forma chegar a 0,5 leva o pet sem treino acima de 0,05. A
  alavanca seria a lista do líder (`GAMBITS_ARENA`), que fica fora das 3 rodadas desta fase.
- **I-3:** a tita já passa de 0,60 sem item (0,74; é o F-1). Os itens somam até 0,03.
- **I-4:** a Foco não tem número para ajustar (o pet não se distrai), e o efeito dela é 0,013.
- **I-5:** o chip de regra entra no fim da lista (antes da reserva, pela DE-10), e a primeira regra que vale decide. Ele quase nunca é a
  primeira. Mudar a ordem é o que a DE-3 recusou, então é uma decisão do Matheus.
- **A conferência única** (a fase 5) roda nas sementes de conferência, depois desta fase.

## Fase 5 — a conferência única

Worker: Claude Code, Opus 5.5, worktree `v2-combate-tr`, 2026-10-30.
- **O candidato v14 inteiro:**
  - o `RELOGIO_V14`, com o disparo a 6× (DE-9);
  - as `LISTAS_V14`;
  - a reserva fixa no fim (DE-10);
  - os `FATORES_V14`.
- **As sementes de conferência:** `70101…70505` (5 bases × 20).
- **Uma vez**, com no máximo 4 processos e as mesmas bancadas e opções das fases 1 a 4. Nenhum número mudou por causa dela.
- **Os artefatos:** `web/app/scripts/medicoes/equilibrio_tr/fase5/`. A calibração ao lado é `fase4/depois/`.
- **A v14 não foi ligada no jogo.** Ligá-la é o passo seguinte, com o ok do Matheus.

| # | calibração | conferência | passa na conferência? |
|---|---|---|---|
| T-1 | média 34,8 s; mediana 32,9 s | 34,8 s; 32,9 s | **não** (a exceção da DE-9) |
| T-2 | no limite 0,021; o pior par 0,40 | 0,024; 0,52 | **não** |
| T-3 | a Cidadela, p90 62,0 s | 60,5 s | sim |
| T-4 | 0,512 | 0,504 | sim |
| T-5 | 0,697 | 0,693 | sim |
| F-1 | 4 fora (espelho, muralha, emboscador, tita) | 5 fora (com o furioso 0,601; tita 0,701) | **não** |
| F-2 | 0,342 | 0,36 | **não** |
| F-3 | passa | passa | sim |
| F-4 | o caçador do Champion 0,679 | 0,671 | **não** |
| F-5 | Champion 0,533; Ultimate 0,198 | 0,523; 0,192 | **não** (o Ultimate) |
| F-6 | o espelho 0,111 | 0,111 | **não** |
| F-7 | o predador 0,208 | 0,218 | **não** |
| P-1 | vizinhos ≤ 0,055; dois estágios, 0 vitórias | ≤ 0,058; 0 | sim |
| P-2 | a pior forma ≥ 0,9925 | ≥ 0,985 | sim |
| P-3 | Champion 0,485; Ultimate 0,458 | 0,529; 0,448 | **não** |
| P-4 | Champion 0,875; Ultimate 0,94 | 0,865; 0,9525 | sim |
| G-1 | passam a Campina e a Torre | passam a Campina e a Torre; fora a Floresta (com 0,52; o guardião 0,03), a Cidadela (com 0,77; a sentinela 0,23), o Lago (sem 0,078) e a Espiral (a sentinela 0,43) | **não** |
| G-2 | os 4 passam | os 4 passam | sim |
| G-3 | de 0,36 a 0,85 | de 0,45 a 0,94 (o vigia fora) | **não** |
| G-4 | 1,00 e 0,81 | 1,00 e 0,67 | sim |
| G-5 | 0,40 | 0,40 | sim |
| G-6 | de 0,8175 a 0,8975 | de 0,83 a 0,925 | sim |
| I-1 | 0,069 | 0,0775 (o Lago) | **não** |
| I-2 | passa | passa | sim |
| I-3 | a tita 0,745 | 0,7675 | **não** |
| I-4 | a Foco 0,013 | a Foco 0,014, o Fôlego 0,029 | **não** |
| I-5 | de 0,005 a 0,11 | de 0 a 0,0975 | **não** |

**O que mudou da calibração para a conferência:**
- **Três metas pioram:**
  - **G-3:** o vigia vai de 0,85, no limite da faixa, a 0,94;
  - **F-1:** o furioso sai por 0,001 (0,601);
  - **I-4:** o Fôlego cai de 0,032 para 0,029.
- **Nenhuma meta que reprovou na calibração passa aqui.**
- **Todas as outras** repetem o resultado da calibração.

### O que fica para uma rodada própria (as questões abertas; nenhuma se resolve nesta rodada)

| questão | recomendação | o custo de errar |
|---|---|---|
| **G-1 e I-1, os líderes da Floresta, da Cidadela, do Lago e da Espiral:** a pior forma (o guardião ou a sentinela) não chega a 0,5, e o fator não basta | uma rodada nas listas dos líderes (`GAMBITS_ARENA`), com as mesmas metas, mexendo só no líder que reprova | sem ela, a sentinela e o emboscador seguem travados nesses líderes; uma lista nova muda as lutas de quem já ganhou a medalha (só na v14, que ainda não está no jogo) |
| **I-5, o chip de regra quase nunca dispara:** ele entra no fim, e a primeira regra que vale decide | decidir se o chip entra antes das regras com a mesma condição (o que a DE-3 recusou) ou se os chips trocam de regra; medir só na v14 | sem mudar, os chips de regra são quase só cosméticos; mudando, todo pet com chip luta diferente |
| **P-3 com a DE-10:** a lista aprendida não chega a 0,55 (Champion 0,53, Ultimate 0,45), e o espelho e a muralha aprendidos perdem da semente | olhar a nota-base da semeadura (`GA.base` e a ordem pela nota) numa regra própria do tempo real, como foi feito com o disparo | o `GA` é conferido contra o Python: mudar o comum mexe na paridade; um número próprio do tempo real é mais um número sem a pesquisa por trás |
| **I-3, a tita acima de 0,60 sem item** (é o F-1) | tratar junto com o F-1: a lista ou a passiva da tita | os itens não são a causa; mexer neles não fecha |
| **I-4, a carta de Foco** (0,014) e o Fôlego no limite (0,029) | dar à Foco um efeito com número (por exemplo, menos distração em vez de nenhuma) e conferir o Fôlego junto | a Foco segue uma carta que não muda a luta |
| **G-3, o vigia a 0,94 na conferência** | olhar o fator da Espiral na Liga (o último líder) junto com o G-1 da Espiral | o vigia ganha a Liga fácil demais; o resto das formas fica na faixa |
| **F-1, F-2 e F-4 a F-7, e T-2** | uma rodada das formas por cima do candidato (as listas), como a fase 2, depois das outras | as formas de longe e a tita seguem fora da faixa |

