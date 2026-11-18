# TAREFA V3 — CORPO (2026-11-18)

Coordenador: a sessão "Auditoria de projeto com LLM". Worker: Claude Code (Opus 5.5, a sessão lateral da CORPO_ACOPLAMENTO). Worktree e
branch: `v3-corpo-mapa` para a C0 (o `v3-corpo` fica para as fases seguintes). Status: ABERTA; a C0 entregue, esperando o CHECKPOINT C1.

Categoria: documentacao. Origem: Matheus, 2026-11-18: o programa C0-C5 do corpo, colado pelo Matheus na sessao lateral da CORPO_ACOPLAMENTO em 2026-11-18.

## 1. Pergunta

O corpo de hoje deixa o pet comer e descansar sem que uma necessidade anule a outra? Se não, qual redesenho, atrás de chave, reduz a tensão
entre a fome e a energia sem piorar o bem-estar e cria substrato para o social? Vem da A1, da VALUATION (V2 e V3) e da CORPO_ACOPLAMENTO.

## 2. Depende de

- A CORPO_ACOPLAMENTO até o plano (#994, #995 e #996, na `main`).
- A run da opção D (`docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md`), rodando em 2026-11-18: o resultado dela entra na prioridade da C1.
- O "aprovado" do Matheus em cada CHECKPOINT (C1, C2, C2.5, C3, C4 e C5).

## 3. Mudança mínima

As fases, em ordem, cada uma num PR:
- **C0:** o `docs/MAPA_CORPO.md`, só papel.
- **C1:** o `docs/PLANO_ANALISE_V3_CORPO.md`, só papel.
- **C2:** a run de ablação, uma vez.
- **C3:** o conserto atrás de chave, no Python e no TS.
- **C4:** a validação, uma vez.
- **C5:** a síntese e a especificação.

O que não muda: o `engine.py`, os saves de hoje (toda mudança atrás de chave desligada), a métrica da A1 e a da V2, e nenhum mecanismo
social (M1–M4, SP-3, CO6/CO7).

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V3_CORPO.md`, commitado antes da run.
- Sementes reservadas: a pedir ao coordenador na C1 (a ablação) e na C4 (a validação).
- Métrica e gate: o forrageio (a taxa por episódio da A1), a privação e a exaustão (a V2), lidos juntos; a regra na C1, PROPOSTA.
- GPU: não.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- O mecanismo social, a limpeza da complexidade acidental e as decisões de produto (o que é JOGO, o que é LAB).

## 7. Critérios de aceitação

- **C0:** o `docs/MAPA_CORPO.md` cobre as ações e as taxas do corpo v11, com arquivo e linha; cada opção tem uma predição e um custo; a
  prioridade é explícita.
- **As fases seguintes:** os critérios do programa, fase a fase, com o plano commitado antes da primeira vida.

## 8. Precisa do Matheus

- **CHECKPOINT C1:** aprovar o mapa e a prioridade (a recomendação e o custo de errar estão na seção 8 do mapa).
- **Antes da C1, três pontos em que o programa bate com as regras do projeto:**
  - o harness da ablação em TS, contra a pesquisa no Python;
  - o K = 200 sementes independentes, contra a derivação das runs anteriores;
  - o worker regenerar o índice de desvios, contra o CLAUDE.md.

  A recomendação para os três é ficar com a regra do projeto.
