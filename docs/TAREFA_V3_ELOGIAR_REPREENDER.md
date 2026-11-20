# TAREFA V3 — ELOGIAR_REPREENDER (2026-11-12)

Coordenador: a sessão do Matheus. Worker: Claude Code (Opus 5.5). Worktree e branch: `v3-elogiar-repreender`. Status: ENTREGUE (PR).

Categoria: implementacao. Origem: Matheus, 2026-11-12: o Matheus pediu elogiar no lugar de carinho e repreender no lugar de tapa, na tela e na fala do jogo web (2026-11-12).

## 1. Pergunta

Não é pesquisa: é a troca de nome de dois gestos do dono na tela e na fala do jogo web (o carinho passa a "Elogiar", o tapa a "Repreender").

## 2. Depende de

A decisão do Matheus de 2026-11-12 ("Sim, as duas"), com o escopo recomendado: só a tela e a fala; ids, log, save e corpo ficam.

## 3. Mudança mínima

- Muda: os rótulos e os textos em `web/app/src/` (o dock, os atalhos do Conversar, o histórico, a janela e o painel da TV, o chamado,
  a dica, a Jornada, a Evolução, as memórias) e o `NOME_CHAMADO` de `web/app/motor/nomes.ts`; a validação do comando do chat
  (`web/app/src/acoes.ts`) troca `elogiar` por `acariciar` e `repreender` por `tapa`.
- Muda também: o mínimo de 84 px por botão do dock a partir de 1280 px (`web/app/src/estilo/pet_dock.css`), para "Repreender" caber.
- Não muda: os ids, os eventos, o save, a `VERSAO_PET`, os gabaritos, o corpo, o cérebro, o Python, os prompts da LLM, o `engine.py`.

## 4. Experimento e gate (se houver run)

Sem run.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

Os documentos fechados (o I7 do tapa e afins), os textos da memória antiga em `motor/expressao.ts` (gêmeo em `digilab/expressao.py`), o nome do clipe `Carinho` do atlas e qualquer mudança de mecânica.

## 7. Critérios de aceitação

- `npm run tipos` e `npx vitest run` passam; `test/comando_chat.test.ts` confere a troca do comando.
- O e2e passa com os rótulos novos.
- As capturas em `docs/capturas_elogiar_repreender/` (1920×950 e 390×844) mostram "Elogiar" e "Repreender" no dock.

## 8. Precisa do Matheus

Nenhuma.
