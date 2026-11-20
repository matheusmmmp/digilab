# TAREFA V2 — INVESTIGA_336 (2026-10-19)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: a sessão da INFRA-MULTIAGENTE. Worker: uma sessão nova do Claude Code, sem histórico. Worktree e branch: `v2-investiga-336`. Status: ABERTA.

Categoria: arquitetura. Origem: ChatGPT Work, 2026-10-19: Issue #336 (POC do fluxo rastreável), aberta pelo Work; o Matheus pediu para enviar para investigação, sem implementar.

## 1. Pergunta

As três questões pendentes da Issue [#336](https://github.com/matheusmmmp/digilab/issues/336), lidas pelo worker na própria Issue:
1. como registrar a autorização humana para implementação sem duplicar o escopo;
2. quais labels, se alguma, devem classificar ideias e tarefas;
3. como confirmar o acesso de leitura do Claude Code ao branch e ao PR.

É a operação ENVIAR PARA INVESTIGAÇÃO do `docs/infra/GUIA_OPERACIONAL.md`: só auditoria, viabilidade e riscos. Não vem de hipótese de
pesquisa.

## 2. Depende de

O branch `v2-infra-autorizacao` (o PR que traz `tools/conferir_autorizacao.py` e esta tarefa). Como da INFRA-POC, a worktree do worker sai
desse branch, e o PR do worker vai **contra `v2-infra-autorizacao`**, não contra a `main` (PR empilhado). Isso substitui o "PR contra a
`main`" da seção 5.

## 3. Mudança mínima

**Muda só um arquivo novo:** `docs/infra/INVESTIGACAO_336.md`, o relatório. Para cada questão:
- o que existe hoje, com o caminho do arquivo, o comando ou o número da Issue ou do PR;
- as opções;
- a recomendação, marcada PROPOSTO;
- o risco e o custo de errar.

**Evidência obrigatória da questão 3:** o worker lê a Issue #336 com `gh` (`gh issue view 336 --repo matheusmmmp/digilab --comments` e
`gh api repos/matheusmmmp/digilab/issues/336`) e escreve no relatório o que leu, inclusive o campo `performed_via_github_app` da Issue
e dos comentários.

Depois de abrir o PR, o worker deixa **um comentário curto na Issue #336**, só com o link do PR e o estado ("investigação entregue no PR
#N, PROPOSTO"), como manda o protocolo.

**Não muda:** código, testes, workflow, labels, configuração do repositório, `CLAUDE.md`, `PAINEL_V2.md` ou qualquer outro documento.

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

- Implementar qualquer recomendação.
- Criar label.
- Mudar a proteção da `main` ou as permissões dos apps.
- **Escrever "AUTORIZO" em qualquer lugar.** A autorização é só do Matheus.

## 7. Critérios de aceitação

- O PR só acrescenta `docs/infra/INVESTIGACAO_336.md` (fora o commit do coordenador com esta tarefa).
- O corpo do PR segue `.github/pull_request_template.md` com `Categoria: arquitetura`, diz PROPOSTO e lista as decisões do Matheus. O
  job `relato` passa.
- O relatório cita o que o `gh` devolveu da Issue #336 (título, autor, `performed_via_github_app`, número de comentários).
- A Issue #336 tem um comentário novo com o link do PR, e só isso.

## 8. Precisa do Matheus

As três recomendações do relatório, que ficam PROPOSTO até o Matheus decidir. O worker lista cada uma no corpo do PR.
