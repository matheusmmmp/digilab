# TAREFA V3 — MOEDA (2026-11-10)

Coordenador: Matheus. Worker: Claude Code (Gerente da V3, Opus 5.5). Worktree e branch: `v3-moeda-plano` (o plano); as etapas MO1 a MO5 em `v3-moeda`. Status: ABERTA (o plano PROPOSTO espera as decisões M-1 a M-10).

Categoria: documentacao. Origem: Matheus, 2026-11-10: o Matheus pediu em 2026-11-10 uma rodada de planejamento da moeda do jogo (os Bits) e das melhorias da ilha, para aprovar.

## 1. Pergunta

Não é pesquisa: é o produto. Como pôr no jogo web uma moeda (os Bits) que se ganha pelo feito, e não pelo clique, e que se gasta em melhorias dos lugares da ilha, numa loja e em enfeites, sem comprar força nem mexer no pet? O desenho está em `docs/PLANO_V3_MOEDA.md`.

## 2. Depende de

- As decisões M-1 a M-10 do `docs/PLANO_V3_MOEDA.md` (seção 9).
- Na `main` já estão o Tamer (`web/app/src/tamer.ts`), o nível do Tamer (`docs/PLANO_V3_PROGRESSAO_TUTORIAL.md`), a campanha v6 e os chips de stat com os tetos.

## 3. Mudança mínima

- Este PR: só o plano, `docs/PLANO_V3_MOEDA.md`, e esta tarefa.
- As etapas (seção 7 do plano): o registro do Tamer 9 com os eventos `"bits"` e `"compra"`, a trava do portão, a loja, as melhorias e os enfeites. Só em `web/app/`.
- **Não muda:** o motor do pet e as versões de pet, o Python, o `engine.py`, a pesquisa.

## 4. Experimento e gate (se houver run)

Não há run. A conta do equilíbrio (o 1º pet junta o ★★ do portão antes de ficar pronto para o Champion) é feita numa vida gravada, na rodada de equilíbrio.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

Moeda por dinheiro real, gacha, uma segunda moeda da Fronteira, a troca de Bits entre jogadores, o equilíbrio dos preços (fica para a rodada de equilíbrio do fim).

## 7. Critérios de aceitação

- Do plano: `docs/PLANO_V3_MOEDA.md` existe, com as decisões M-1 a M-10 marcadas DECIDIDAS pelo Matheus.
- De cada etapa: os testes do Vitest do saldo derivado (saldo negativo falha alto), da novidade e do teto do cuidado; o e2e do portão trancado; as capturas no desktop e no celular.

## 8. Precisa do Matheus

As M-1 a M-10 do `docs/PLANO_V3_MOEDA.md`, seção 9, cada uma com a recomendação e o custo de errar.
