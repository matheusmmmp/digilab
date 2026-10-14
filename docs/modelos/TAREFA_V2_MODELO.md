# TAREFA V2 — <FRENTE> (<data>)

Coordenador: <chat>. Worker: <chat>. Worktree e branch: `v2-<frente>`. Status: <ABERTA | EM ANDAMENTO | ENTREGUE>.

## 1. Pergunta

<Uma frase. De qual hipótese do `docs/PLANO_V2_PESQUISA.md` ela vem (H1, H0…) e qual nó da fase.>

## 2. Depende de

<Frentes que precisam estar na `main` antes; decisões do Matheus que precisam existir.>

## 3. Mudança mínima

<O que muda, em quais arquivos. O que NÃO muda (fronteiras: `engine.py`, runs da v1, versões de pet antigas).>

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V2_<FRENTE>.md`, commitado antes da run.
- Sementes reservadas: calibração <faixa>; validação <faixa>.
- Métrica e gate: <números PROPOSTOS>.
- GPU: <sim/não> (se sim, posição na fila).

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do `docs/REGISTRO_DESVIOS.md`. O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V2_*.md` da run ou o `TAREFA_V2_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

<O que fica de fora, de propósito.>
