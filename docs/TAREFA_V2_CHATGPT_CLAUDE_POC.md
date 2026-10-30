# TAREFA V2 — CHATGPT_CLAUDE_POC (2026-10-18)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: ChatGPT Work. Worker: ChatGPT Work (documentação). Worktree e branch: `v2-chatgpt-claude-poc`. Status: ENTREGUE (PR aberto, sem merge; execução Claude Code pendente).

Categoria: documentacao. Origem: ChatGPT Work, 2026-10-18: pedido do Matheus para criar uma POC de fluxo rastreável entre ideia em Issue, tarefa V2, worker Claude Code e revisão via PR (Issue #336).

## 1. Pergunta

Como registrar uma ideia curta no GitHub, convertê-la numa tarefa V2 e recuperar um relato por PR sem copiar o histórico da conversa nem duplicar fontes de verdade? É infraestrutura, não vem de hipótese científica.

## 2. Depende de

- A documentação da infraestrutura em `v2-infra-multiagente` e a inclusão do comando de conferência do relato em `v2-infra-poc` (PR #326 e PR #331, ainda abertos durante esta tarefa).
- A tarefa só pode iniciar um worker Claude Code depois que estiver na `main`, conforme `docs/V2_TRABALHO_PARALELO.md`.
- Não há dependência de código, runs, credenciais, serviços pagos ou labels novos.

## 3. Mudança mínima

- Acrescentar a `docs/infra/GUIA_OPERACIONAL.md` o protocolo REGISTRAR IDEIA → ENVIAR PARA INVESTIGAÇÃO → AUTORIZAR IMPLEMENTAÇÃO, identificando Issue, tarefa, comentário de aprovação e PR como fontes por etapa.
- Atualizar `docs/infra/MATRIZ_CAPACIDADES.md` com o teste de criação e leitura do Issue #336 pelo conector GitHub.
- Manter `docs/TAREFA_V2_CHATGPT_CLAUDE_POC.md` como registro do escopo desta tarefa.
- Não mudar código, arquitetura, workflow, regras do `CLAUDE.md`, `PAINEL_V2.md` nem configuração de permissões. Não iniciar Claude Code nem alegar teste de leitura pelo executor.

## 4. Experimento e gate (se houver run)

- Plano de análise: não há run.
- Sementes reservadas: não se aplica.
- Métrica e gate: não se aplica.
- GPU: não.

## 5. Entrega

- Testes locais: não executados; este ambiente usa o conector GitHub e não tem a worktree Windows do projeto.
- Verificação: o CI `verificar-pr` deve conferir os campos do relato e links relativos dos documentos; os resultados serão reportados como VERIFICADOS apenas após a execução do CI.
- Registro: nenhum desvio científico; o relato e as questões abertas ficam no corpo do PR e neste documento.
- PR empilhado sobre `v2-infra-poc`, pois a infraestrutura base (#326) e o ajuste do guia (#331) ainda não estão na `main`. Merge só pelo Matheus.

## 6. Fora desta tarefa

- Executar ou integrar Claude Code automaticamente.
- Criar GitHub Actions, secrets, agentes permanentes, API paga ou dependência de labels.
- Implementar funcionalidade do DigiBrain ou alterar arquitetura.
- Tornar o repositório público ou alterar sua visibilidade.

## 7. Critérios de aceitação

- O Issue #336 existe e registra a ideia em estado PROPOSTO.
- O guia diferencia as fontes de verdade por etapa e inclui exemplos das três operações solicitadas.
- A autorização de implementação é explícita, humana e ligada ao conteúdo exato da tarefa.
- O guia esclarece que Issue/PR não inicia uma sessão Claude Code e que a investigação não autoriza implementação.
- O PR segue `.github/pull_request_template.md`; o CI verifica relato e links.
- A entrega separa teste real do conector, CI e etapa Claude Code ainda pendente.

## 8. Precisa do Matheus

- Fazer o merge, em ordem, dos PRs empilhados #326, #331 e desta tarefa, se aprovar os diffs. Nenhum agente faz merge.
- Antes de manter escrita recorrente pelo conector, resolver IM-7: proteger `main` contra push direto ou restringir o conector a leitura. Este PR não altera permissões.
- Após a tarefa de investigação e o relatório do Claude Code, aprovar ou rejeitar a implementação por comentário explícito no Issue, vinculado ao blob SHA da tarefa. A POC documental não toma essa decisão.
