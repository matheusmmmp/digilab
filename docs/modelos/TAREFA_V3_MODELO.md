# TAREFA V3 — <FRENTE> (<data>)

Coordenador: <chat>. Worker: <chat>. Worktree e branch: `v3-<frente>`. Status: <ABERTA | EM ANDAMENTO | ENTREGUE>.

Categoria: <implementacao | experimento | literatura | arquitetura | documentacao>. Origem: <Matheus | ChatGPT | ChatGPT Work | Claude Code |
Claude Research/Science>, <data>: <de onde veio a tarefa, em uma frase; nunca link de conversa privada>.

## 1. Pergunta

<Uma frase. De qual hipótese do `docs/PLANO_V2_PESQUISA.md` ela vem (H1, H0…) e qual nó da fase.>

## 2. Depende de

<Frentes que precisam estar na `main` antes; decisões do Matheus que precisam existir.>

## 3. Mudança mínima

<O que muda, em quais arquivos. O que NÃO muda (fronteiras: `engine.py`, runs da v1, versões de pet antigas).>

## 4. Experimento e gate (se houver run)

- Plano de análise: `docs/PLANO_ANALISE_V3_<FRENTE>.md`, commitado antes da run.
- Sementes reservadas: calibração <faixa>; validação <faixa>.
- Métrica e gate: <números PROPOSTOS>.
- GPU: <sim/não> (se sim, posição na fila).

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

<O que fica de fora, de propósito.>

## 7. Critérios de aceitação

<Cada um verificável por quem não estava na sessão: um teste, um arquivo que existe, um link que resolve, um número com artefato.>

## 8. Precisa do Matheus

<As decisões que o worker não toma, cada uma com a recomendação e o custo de errar. "Nenhuma" se não houver.>
