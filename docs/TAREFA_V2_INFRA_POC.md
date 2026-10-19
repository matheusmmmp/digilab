# TAREFA V2 — INFRA_POC (2026-10-18)

Coordenador: a sessão da INFRA-MULTIAGENTE (#326). Worker: uma sessão nova do Claude Code, sem histórico. Worktree e branch: `v2-infra-poc`. Status: ABERTA.

Categoria: documentacao. Origem: Claude Code, 2026-10-18: prova de conceito da infra multiagente: um worker sem histórico executa uma tarefa pequena a partir só do handoff.

## 1. Pergunta

Um worker que só leu o `CLAUDE.md`, o `AGENTS.md` e esta tarefa consegue executar uma mudança pequena e devolver um relato que o CI aceita? É a prova de conceito de `docs/TAREFA_V2_INFRA_MULTIAGENTE.md`; não vem de hipótese de pesquisa.

## 2. Depende de

O branch `v2-infra-multiagente` (PR #326), que ainda **não** está na `main`. Por isso esta worktree saiu dele, e o PR desta tarefa vai **contra o branch `v2-infra-multiagente`, não contra a `main`** (um PR empilhado). Isso substitui o "PR contra a `main`" da seção 5 e da mensagem inicial.

## 3. Mudança mínima

Só `docs/infra/GUIA_OPERACIONAL.md`: acrescentar, no fim da seção 3 ("O que o CI confere"), um parágrafo **"Conferir um relato antes de abrir o PR"** com os dois comandos de `tools/verificar_relato.py` que rodam localmente (`--arquivo <corpo.md> --base <base>` e `--pr <N>`). Antes de escrever, rode os dois neste repositório e escreva só o que de fato rodou. Nada mais muda: nem código, nem testes, nem outro documento.

## 4. Experimento e gate (se houver run)

Não há run; esta seção não se aplica.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V2_*.md` da run ou o `TAREFA_V2_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

Corrigir qualquer outra coisa que você ache no guia ou na infra: anote em "Questões abertas" do PR, não corrija.

## 7. Critérios de aceitação

- O diff do PR só toca `docs/infra/GUIA_OPERACIONAL.md`.
- O corpo do PR segue `.github/pull_request_template.md` com `Categoria: documentacao`, e o job `relato` do CI passa.
- Os dois comandos escritos no guia rodam como estão escritos (o relato diz a saída que você viu, como DECLARADA).

## 8. Precisa do Matheus

Nenhuma. Merge não: o coordenador e o Matheus revisam.
