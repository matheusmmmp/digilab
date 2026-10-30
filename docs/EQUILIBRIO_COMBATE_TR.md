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
- **O candidato fica em 1** (seção abaixo): o `RELOGIO_V14` não muda.

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
