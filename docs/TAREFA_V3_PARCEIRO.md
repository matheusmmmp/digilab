# TAREFA V3 — PARCEIRO (2026-11-12)

Coordenador: a sessão do Matheus. Worker: Claude Code (Opus 5.5). Worktree e branch: `v3-parceiro`. Status: J0 ENTREGUE (PR); as fases J1 a J9 abrem cada uma com a sua espec.

Categoria: documentacao. Origem: Matheus, 2026-11-12: o Matheus pediu um parceiro mais detalhado (um Digimon, a jornada numa área viva, o mesmo cérebro) e um GDD com a engenharia e o roadmap (2026-11-12).

## 1. Pergunta

Como dar ao jogo um parceiro só, que vive entre o habitat e uma área viva com o mesmo cérebro e o mesmo registro (PAR-1 a PAR-3)? A J0 é só o desenho; a pergunta de pesquisa (G-VIVO, G-MESMO-CEREBRO) é da J1.

## 2. Depende de

As decisões PAR-1 a PAR-3, PAR-6 e PAR-14 (Matheus, 2026-11-12). Para a J1 falta a PAR-7.

## 3. Mudança mínima

J0: só documentos: [`GDD_V3_PARCEIRO.md`](GDD_V3_PARCEIRO.md), [`ENGENHARIA_V3_PARCEIRO.md`](ENGENHARIA_V3_PARCEIRO.md) e [`PLANO_V3_PARCEIRO.md`](PLANO_V3_PARCEIRO.md). Nada muda no código, no motor, no `engine.py` nem nos pets.

## 4. Experimento e gate (se houver run)

Sem run. A jornada fica só no jogo web (PAR-14): sem plano de análise nem faixa de sementes; os critérios da J1 são de produto, conferidos por testes (o roadmap, seção 2).

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

Todo código; o multijogador e a conta; a venda de qualquer coisa; a pergunta do dono, encerrada.

## 7. Critérios de aceitação

Os três documentos existem e os links relativos resolvem (`tools/verificar_relato.py`, categoria documentacao).

## 8. Precisa do Matheus

As PAR-4 a PAR-15, na seção 11 do GDD, cada uma com a recomendação e o custo de errar.
