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
