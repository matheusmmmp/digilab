# TAREFA V3 — HABITAT_REACOES (2026-11-11)

Coordenador e worker: sessão do Gerente da V3 (Claude Code, Opus 5.5). Worktree e branch: `v3-habitat-reacoes`. Status: PLANO APROVADO
(etapa 0, sem código; HR-1 a HR-8 DECIDIDAS em 2026-11-11).

Categoria: documentacao. Origem: Matheus, 2026-11-10: "depois a gente planeja o que a gente faz com o Digimon no habitat, por exemplo.
Quando você dá comida, a reação dele e tal". Liberado em 2026-11-11: "Pode começar no que ficou pendente ali".

## 1. Pergunta

O que o pet mostra e faz ouvir quando o dono cuida dele na ilha? Por exemplo, a comida, o carinho, o banho, o chamado e o sono. Nó do
produto: a experiência básica (`docs/PRODUTO_VISAO.md`, seção 3).

## 2. Depende de

- O SOM_UP na `main` (#781): os barramentos, `somEventos.ts` e o `mapa.json` versão 2.
- As decisões HR-1 a HR-8 do plano (`docs/PLANO_V3_HABITAT_REACOES.md`, seção 6), antes da HR1.

## 3. Mudança mínima

Esta etapa traz só o plano, `docs/PLANO_V3_HABITAT_REACOES.md`, e este arquivo. As etapas HR1 a HR5 mexem só na vista e no som do
`web/app/src`. O motor, o log, o save, o replay e a RNG do motor não mudam.

## 4. Experimento e gate

Não há run.

## 5. Entrega

O plano e o relato no corpo do PR.

## 6. Fora desta tarefa

- O ambiente da ilha (S5).
- Os sons dos Bits e da loja (S6).
- A voz por espécie pelo genoma (S7), que fica como a HR5 e vira frente própria.

## 7. Critérios de aceitação

1. O plano tem uma linha por momento de cuidado, com a cara, o som do gesto e a voz.
2. Cada som citado tem a fonte: o arquivo do UP que está no disco, CC0 a baixar ou síntese.
3. As decisões HR-1 a HR-8 vêm com a recomendação e o custo de errar.

## 8. Precisa do Matheus

Nada: as HR-1 a HR-8 foram aprovadas em 2026-11-11 ("Aprovo as oito"), com a HR-5, baixar de 8 a 10 sons CC0 na HR4.
