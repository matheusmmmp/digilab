# TAREFA V3 — PROMO_TELAS (2026-11-06)

Coordenador: a sessão do promo (Claude Code). Worker: Claude Code (Opus 5.5), sessão lateral. Worktree e branch: `v3-promo-telas`.
Status: ENTREGUE (PR aberto, merge só pelo Matheus).

Categoria: implementacao. Origem: Claude Code, 2026-11-06: três defeitos de tela do jogo web vistos nas capturas do vídeo promocional
(`promo/ENTREGA_PILOTO.md`, fora do repositório, seções 11 e 12).

## 1. Pergunta

Nenhuma de pesquisa. Três defeitos de tela do jogo web, vistos no vídeo promocional, devem ser consertados no jogo, não na montagem.

## 2. Depende de

Nada além da `main` de 2026-11-06 (`f7d70add`).

## 3. Mudança mínima

1. **O balão da fala do Rookie com marcas cruas.** Depois de treinar com o pedido de pausa, o balão `.cena-fala` mostrava
   "[sem pausa] [:treino puxado:]". A ação ficava entre colchetes, e a causa sem emote virava uma etiqueta ou, sem o atlas, o texto cru.
2. **O "à toa ?" no "Por que ele disse isso".** O painel mostrava `NOME_PET[m.acao]`, a ação de agora, e não o que o pet fez no motivo.
   As ações do treino (`treinar_cansado`, `forcar_treino`) não são ações do pet. O "?" vinha de `fadiga_treino` sem ícone.
3. **O balão estreito na conversa.** Em Conversar › Livre, "Comi?" partia em "Com / i?".

Só muda a tela (`web/app/src/`). O motor, o log, o save e os gabaritos não mudam.

## 4. Experimento e gate (se houver run)

Nenhum: não há run.

## 5. Entrega

- Em `web/app`: `npm run tipos`, `npm test` e o e2e dos trechos tocados (Pet, Treinar, Conversar).
- Um teste novo para cada defeito, no Vitest ou no e2e.
- PR contra a `main` com o relato no corpo e as capturas antes e depois. Merge só pelo Matheus.

## 6. Fora desta tarefa

- O texto das tabelas de expressão do motor (`motor/expressao.ts`).
- O rótulo do painel para os motivos de ações do pet, que continua mostrando a ação de agora.
- A montagem do vídeo.

## 7. Critérios de aceitação

- O balão do Rookie não mostra `[`, `]`, `[:` nem `:]`, com o atlas e sem ele: `web/app/e2e/jogo.spec.ts`, testes "fala: …", e
  `web/app/test/fala_marcas.test.ts`.
- O painel diz "treinou sem a pausa que pediu", sem o "?": mesmo e2e e o mesmo Vitest.
- "Comi?" cabe numa linha em 390 e 1280 px: `web/app/e2e/jogo.spec.ts`, testes "conversa: a resposta curta …".

## 8. Precisa do Matheus

Nenhuma decisão. O ícone da causa "treino puxado" é a peça `treino_saco` do atlas, o mesmo selo da aba Treinar. É uma escolha da tela,
que se troca numa linha (`ICONE_FATOR` em `web/app/src/falaMarcas.ts`).

## 9. Resultado (2026-11-06)

- **Marcas:** `src/falaMarcas.ts` (novo) quebra a fala do Rookie em texto, ação e causa (`partesFala`). Na tela:
  - a ação vira uma etiqueta sem colchetes (`.fala-acao`);
  - a causa vira o ícone do fator (`ICONE_FATOR`, agora com `fadiga_treino` → `treino_saco`) ou, sem o atlas ou sem ícone, a etiqueta
    `.fala-marca`.

  Isso vale também para a frase de confiança do Estado, que passava o texto cru.
- **Porquê:** `rotuloAcaoFala` mostra o que o pet fez no motivo do treino ("treinou sem a pausa que pediu", "treinou além do limite").
  Uma ação de motivo sem rótulo falha alto. O painel e o balão usam a mesma tabela de ícones.
- **Conversa:** `.mc-pilha` ocupa a linha (`flex:1; justify-items:start`) e o balão encolhe ao texto. Antes, os 86 % do balão eram
  medidos sobre a pilha já encolhida ao texto. O `overflow-wrap` passa de `anywhere` para `break-word`, então palavra curta não parte.
- **Testes:** `test/fala_marcas.test.ts` (5) e 4 e2e novos em `e2e/jogo.spec.ts`. Os 4 e2e reprovam com as telas da `main` e passam
  com o conserto.
