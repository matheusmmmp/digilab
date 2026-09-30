# Validação da variante `a_c_e2v_v` do reequilíbrio (V21D)

Status: **APROVADA** (2026-09-30), com o furioso como exceção declarada. As seções 1 a 3 são o registro, escrito e
commitado **antes** de rodar qualquer coisa nas sementes de validação (commit `357ab23`). A seção 4 veio num commit
posterior, depois da run única.

Decisão do Matheus (2026-09-30): fixar o ganho da rodada 2 (`docs/EQUILIBRIO_RODADA2.md`) com o furioso como
**exceção conhecida** (o problema dele é da base do combate; rodada 3, tarefa futura), validar nas sementes de
validação e levar ao jogo nos pets v6.

## 1. A variante (exata)

Regras da validação V21C (`experiments/configs/v21c/validacao.json`) mais estas chaves da `ConfigCombateV21D`
(`experiments/configs/v21d/validacao.json`):

| chave | valor | o que faz |
|---|---|---|
| `preparo_sob_pele_oculto` | **ligada** | A: o preparo do pesado feito sob `pele_dura` não aparece em `oponente_preparando` |
| `muralha_lista_espelho` | **ligada** | C: a muralha luta com a lista do espelho (`bots.GAMBITS_MURALHA_V21D`) |
| `vigia_bate_em_quem_recua` | **ligada** | E2 no vigia: `se(perto, oponente_frequente(recuar)) → golpe_rapido` antes do preparar; sai `oponente_preparando → esquivar` |
| `vigia_recua_do_preparo_sob_pele` | **ligada** | V: `se(oponente_vai_preparar, oponente_frequente(pele_dura)) → recuar` no topo do vigia; sai `guts < 20 → carregar` |
| `investida_erra_contra_recuo` | desligada | D2 |
| `preparo_prende` | desligada | E1 |
| `tita_bate_em_quem_recua` | desligada | E2 no titã |

A base V2C não muda (`dano_parry` 5, sem D1). No Python as chaves continuam **desligadas por padrão**: a V21C, a
pesquisa (V3, E1, confirmatória) e o `engine.py` não mudam.

## 2. Método

`python experiments/validar_v21d.py --conjunto validacao`, uma vez. Os métodos são os da rodada 2
(`experiments/calibrar_equilibrio.py`), com as sementes como parâmetro, e rodam a V21C e a variante nas mesmas sementes:

- **Sementes de validação:** 4101, 4202, 4303, 4404, 4505. Nenhuma delas foi usada na calibração.
- **Matriz:** as 8 formas adultas, os dois lados da mesma espécie, 100 partidas por par por semente e espécie, lados
  trocados na metade, ε dos bots 0,05 e 0,15. Força = média dos pontos contra as outras 7 (média das 4 espécies).
- **Painel B:** pet = bot canônico da forma (ε 0,05, sem treino, condição 1,0) contra os 32 bots do painel (8 formas ×
  4 espécies), 50 partidas por bot por semente, sob as regras e listas da variante.
- **S1:** 12 formas (8 normais + 4 sombrias), 100 partidas por par por semente e espécie.
- **E4 na escala:** adulto sem treino × adolescente da linha sem treino e com +22 (uniforme), como `run_bateria_v21`
  com a escala.
- **Campanha na escala:** o pet do estágio sugerido × cada NPC, sem treino e com o treino típico, 10 partidas por
  semente, fatores de `ConfigEscala.fator_npc` (como `calibrar_escala.py --validar`), regras
  `campanha.REGRAS_CAMPANHA` mais as chaves.
- **E3:** resposta declarada de cada técnica (`RESPOSTAS_V21C`), como a bateria.

Antes da validação, o script foi conferido nas sementes de **calibração**: com `--conjunto calibracao` ele refaz a
rodada 2 byte a byte (matriz, painel e colaterais da `a_c_e2v_v` e da V21C;
`artifacts_combate_v21c/validacao_v21d/conferencia_calibracao.json`). Na validação, a parte V21C é conferida contra os
artefatos de validação já gravados (matriz, E3, E4, campanha); as conferências são registradas e não interrompem a run.

Artefatos: `artifacts_combate_v21c/validacao_v21d/` (`matriz.json`, `painel.json`, `colaterais.json`,
`criterios.json`).

## 3. Critérios (o que conta como passar)

A validação **passa** se todos os itens abaixo passarem, com a variante, nas sementes de validação:

| item | critério |
|---|---|
| **A1** força entre formas | as 7 formas que não são o furioso com força (ε 0,05) em [0,40; 0,60] |
| **A2** força contra o painel B | as 7 formas que não são o furioso com taxa no painel em [0,40; 0,60] |
| **A6** lugar no ciclo | toda forma (as 8) vence (> 0,5) pelo menos 2 das outras 7 (ε 0,05) |
| **S1** | nenhuma sombria vence (> 0,5) as 8 formas normais |
| **E4 na escala** | o adulto sem treino vence o Champion (sem treino e com +22) em ≥ 0,60, nas 8 formas |
| **campanha na escala** | Brutamontes, Carcereiro, Porteiro e Soberano com ≤ 0,30 sem treino e ≥ 0,80 com o treino típico; a Sentinela segue exceção aceita |
| **E3 da pele dura** | a resposta declarada ("ficar longe") reduz a taxa dos usuários da pele dura (redução > 0) |

**Relatados, não reprovam** (exceção declarada):
- o furioso (força, painel, vitórias);
- A3 (suporte do equilíbrio ≥ 6), A4 (no máximo 7 pares fora de [0,1; 0,9] com ε 0,05 e 4 com ε 0,15), A5 (amplitude
  ≤ 0,20 com ε 0,05 e 0,15);
- A1 e A2 com as 8 formas;
- o E3 das outras técnicas (o do contra-golpe já falhava na calibração com A + C);
- a Sentinela na campanha.

**Depois da run não se mexe em número nenhum por causa do resultado.** Se reprovar, a reprovação é relatada, e a
decisão (aceitar outra exceção, rodada 3, voltar) é do Matheus.

Não medidos nesta validação: E2 (espécies), E5, G6b, G8, G9 e as runs de pesquisa com pets reais (a pesquisa não lê as
chaves).

## 4. Resultado (run única, 2026-09-30)

**APROVADA**: os 7 itens passam. Todo número abaixo vem de `artifacts_combate_v21c/validacao_v21d/`
(`criterios.json`, `matriz.json`, `painel.json`, `colaterais.json`); sementes 4101…4505, ~3 min com 8 processos.

**Conferências** (`criterios.json > conferencias_v21c_com_artefatos_de_validacao`): a V21C destas sementes sai igual
aos artefatos de validação já gravados. São eles a matriz (`validacao/matriz_arquetipos.json`), o E3
(`validacao/uso_tecnicas.json`), o E4 (`validacao_escala/gates.json`), a campanha (`configs/escala/validacao.json`) e o
S1 (`bateria_sombria/gates.json`). As cinco conferem.

| item | critério | resultado | |
|---|---|---|---|
| **A1** | 7 formas sem o furioso em [0,40; 0,60] | sentinela 0,562, emboscador 0,544, duelista 0,475, vigia 0,449, muralha 0,423, espelho 0,418, titã 0,407 | passa |
| **A2** | idem, contra o painel B | emboscador 0,549, sentinela 0,543, duelista 0,492, vigia 0,444, titã 0,436, espelho 0,434, muralha 0,432 | passa |
| **A6** | toda forma vence ≥ 2 das outras 7 | mínimo 2 (titã: espelho e muralha); furioso 5, duelista, muralha e sentinela 4, emboscador, espelho e vigia 3 | passa |
| **S1** | nenhuma sombria vence as 8 | devastador 0,374 (vence duelista, titã, vigia), predador 0,326 (2), colosso partido 0,233 (espelho, muralha), bastião rachado 0,152 (0) | passa |
| **E4 na escala** | adulto sem treino ≥ 0,60 contra o Champion | menor 0,8355 (espelho contra o Champion com +22); muralha 0,854 e 0,855; as outras 0,965–1,0 | passa |
| **campanha na escala** | 4 NPCs nas metas (sem ≤ 0,30, com ≥ 0,80) | Brutamontes 0,221 / 0,969; Carcereiro 0,261 / 0,841; Porteiro 0,196 / 0,894; Soberano 0,203 / 0,913 | passa |
| **E3 da pele dura** | a resposta reduz a taxa | 0,435 → 0,101 (titã 0,413 → 0,006; vigia 0,458 → 0,195) | passa |

**Margens estreitas** (o erro padrão entre sementes não foi estimado; diferenças abaixo de ~0,01 não devem ser
lidas):
- o titã passa o A1 por 0,007 (0,407);
- o titã vence exatamente 2 das 7, o mínimo do A6;
- o espelho (0,418) e a muralha (0,423) passam o A1 por menos de 0,025.

**Relatados (exceção declarada; não reprovam):**
- **furioso:** força 0,722, painel 0,675, vence 5 das 7. Faz 1,00 contra a sentinela e o emboscador, 0,923 contra o
  duelista, 0,937 contra o titã e 0,779 contra o vigia.
- **A3:** suporte 4 com ε 0,05 (furioso 0,318, sentinela 0,262, muralha 0,261, espelho 0,155), 3 com ε 0,15. Não passaria
  (≥ 6).
- **A4:** 9 pares extremos com ε 0,05 e 7 com ε 0,15. Não passaria (≤ 7 e ≤ 4). Com ε 0,05, os pares extremos são:
  - 4 do furioso: × sentinela 1,00, × emboscador 1,00, × titã 0,937, × duelista 0,923;
  - sentinela × muralha 1,00 e emboscador × muralha 1,00;
  - espelho × emboscador 0,006;
  - sentinela × titã 0,986 e emboscador × titã 0,985.
- **A5:** amplitude 0,316 com ε 0,05 (furioso − titã) e 0,424 com ε 0,15 (furioso 0,767 − espelho 0,343). Não passaria
  (≤ 0,20).
- **A1 e A2 com as 8 formas:** não passam, só pelo furioso.
- **E3 das outras técnicas:**
  - investida 0,586 → 0,495 e marcar 0,543 → 0,452 (reduzem);
  - contra-golpe 0,431 → 0,496 (**não reduz**). A causa é o espelho, que sobe com a resposta "recuar e atirar" (0,426 →
    0,948), como na calibração;
  - na V21C destas sementes o contra-golpe caía (0,520 → 0,461), mas o espelho já subia (0,624 → 0,919).
- **Sentinela na campanha:** 0,418 sem treino e 0,738 com o treino típico, travado o colosso (0,035 / 0,245). Na V21C
  destas sementes era 0,413 / 0,703.

**Comparação com a V21C nas mesmas sementes** (ε 0,05):

| | V21C | a_c_e2v_v |
|---|---|---|
| formas em [0,40; 0,60] (força; painel) | 2; 2 | 7; 7 |
| força: furioso / titã / vigia | 0,753 / 0,171 / 0,248 | 0,722 / 0,407 / 0,449 |
| menor nº de vitórias | titã 1 | titã 2 |
| pares extremos (ε 0,05 / 0,15) | 17 / 12 | 9 / 7 |
| amplitude (ε 0,05 / 0,15) | 0,582 / 0,590 | 0,316 / 0,424 |
| suporte (ε 0,05) | 4 | 4 |

Confrontos que mudam (V21C → variante):
- vigia × sentinela 0,037 → 0,636 e vigia × emboscador 0,035 → 0,606;
- vigia × titã 0,970 → 0,522;
- titã × espelho 0,036 → 0,885 e titã × muralha 0,616 → 0,893;
- muralha × espelho 0,280 → 0,554;
- furioso × vigia 0,992 → 0,779.

O titã segue perdendo dos caçadores: 0,015 contra a sentinela e contra o emboscador.

Os números repetem os da calibração (`docs/EQUILIBRIO_RODADA2.md`, seção 4): a força difere em no máximo 0,003 por forma
e o painel em no máximo 0,005. Na calibração o furioso tinha 0,725 e o titã 0,406.

**Não medidos:** E2 (espécies), E5, G6b, G8, G9 e as runs de pesquisa com pets reais.

## 5. No jogo web: pets v6

Depois da validação, a variante entrou no jogo web **só nos pets v6** (`web/app/`). Os pets v1–v5 lutam como antes (V21C):
os gabaritos de paridade com o HTML e as assinaturas não mudam, e os testes de antes continuam passando.

- **Regras da luta** (`combate.RegrasLuta`): `null` é a V21C, e `CV21D` (`constantes.ts`) é a variante, com as quatro
  chaves ligadas. `Motor.regras` dá `CV21D` para os pets v6. A regra vale para a luta inteira (os dois lados), como as
  `Regras` do Python, em todas as lutas de um pet v6: arena, campanha, sparring, replay do registro, pet de cenário como
  rival e "Melhor de 10".
- **O que muda na luta:**
  - o preparo feito sob pele não aparece em `oponente_preparando` (estado `prepPele` no lutador);
  - a muralha e o vigia usam as listas variantes (`bots.BOTS_V21D`, `gambitsAdulto`), tanto o pet v6 (a semente dos
    gambits na evolução para adulto) quanto os bots e NPCs com esses estilos que lutam contra ele.
- **O que não muda:**
  - `BOTS_V21` (as listas canônicas);
  - o repertório de candidatas dos gambits híbridos. As duas regras novas do vigia saem só da semente;
    `gambits_pet.regraDe` as encontra fora do repertório, como a regra do devastador.
    Desde 2026-09-30 (medalhas, parte 2) elas também voltam como candidatas de troca para o vigia v6
    (`gambits_pet.candidatasDoVigia`), para uma troca não as tirar para sempre; o repertório não muda.
- **Paridade Python × web:** `experiments/exportar_gabarito_v21d.py` → `web/app/test/gabaritos/combate_v21d_python.json`
  (272 partidas, V21C e variante, mesmas sementes; 56 das 136 partidas mudam com a V21D). `test/paridade_v21d.test.ts`
  refaz cada partida no TS e exige perfil, turnos (sha256) e fim iguais. As decisões por regra, a leitura do vigia e a
  resolução são do TS; só as ações de exploração vêm do gabarito, porque a rng do Python não é a da web. As 272 partidas
  saem iguais.
- **Constantes:** `CV21D` no `mapa_constantes.json`. A lista `chaves_v21d` confere as quatro chaves booleanas contra
  `experiments/configs/v21d/validacao.json` e contra os campos da `ConfigCombateV21D`; `versaoPet` fica em `so_web`.
- **Saves:** os pets v6 criados antes desta mudança mudariam de comportamento no replay. O descarte único do app
  (`src/tamer.ts`, `descartarPetsAntigos`) ganhou um marcador de versão (`…-descarte`, versão 2):
  - na primeira abertura depois da atualização, os pets até v6 (o ativo e os guardados) saem, com o mesmo aviso das
    medalhas;
  - com pet descartado, o Tamer recomeça sem medalhas, porque o aviso diz "um ovo novo e nenhuma medalha";
  - não há v7.

**Relato: NPCs da campanha v5 no motor web com a V21D.** Medido depois da validação; não é critério e nenhum fator mudou.
Fonte: `artifacts_campanha/mega/validacao_v21d.json`, de `node test/calibrar_mega.mjs --validar --v21d` (sementes de
validação, mesmo método de `validacao.json`, que sai igual rodado de novo).

| NPC | V21C (sem / com) | V21D (sem / com) |
|---|---|---|
| Puppetmon | 0,236 / 0,893 | 0,227 / 0,870 |
| Machinedramon | 0,267 / 0,853 | 0,268 / 0,911 |
| Piedmon (Espiral) | 0,155 / 0,941 | 0,196 / 0,941 |
| Myotismon (Cidadela, Ultimate) | 0,171 / 0,921 | 0,212 / 0,921 |

Os quatro seguem nas metas (≤ 0,30 sem treino, ≥ 0,80 com o treino típico), sem forma travada.

**Testes** (chaves desligadas no Python):
- `python -m pytest tests/ -q`: 428 passaram e 1 foi pulado (os 426 da rodada 2 mais 2 novos: o config da validação e o
  gabarito da web reproduzem);
- web: `npm run tipos` limpo, `npm test` com 135 testes em 15 arquivos, `npm run e2e` com 24 testes.
