# Matriz de capacidades: ChatGPT, ChatGPT Work, Claude Code e GitHub (2026-10-18)

Tarefa: `docs/TAREFA_V2_INFRA_MULTIAGENTE.md`.

**Como as linhas foram conferidas.** A documentação oficial foi lida em 2026-10-18 por um subagente desta sessão. O WebFetch levou 403 em
help.openai.com, e essas páginas foram baixadas com curl. As páginas do Codex em developers.openai.com redirecionam para learn.chatgpt.com.

**O que cada status quer dizer:**
- `DOC`: lido na página oficial citada. Não foi testado aqui.
- `TESTADO`: rodado neste repositório, com a evidência ao lado.
- `NÃO CONFIRMADO`: a página não diz, ou só uma fonte secundária diz.

**Nenhuma linha do ChatGPT Work está `TESTADO`:** o teste depende do Matheus (`docs/infra/TESTE_CHATGPT_WORK.md`).

**Os tipos:** nativa · configuração (depende de configurar) · paga (paga ou por API) · externa (infraestrutura de fora) · não suportada.

## OpenAI

| capacidade | o que a doc diz | tipo | custo | fonte | status |
|---|---|---|---|---|---|
| **ChatGPT Work** | Agente para tarefas longas de vários passos: pesquisa, apps conectados, entregáveis. Lançado em 2026-07-09 nos planos pagos (não no Free nem no Go). Na web e no celular roda na nuvem. | nativa | a cota e os créditos do Codex | [Work e Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex), [release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) | DOC |
| Work lê o repositório e os PRs | Pelo conector GitHub, que busca sob demanda o que foi autorizado. Não indexa nem sincroniza o repositório. | configuração | no plano | [conector GitHub](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt) | DOC; **issues: **TESTADO** nesta POC (Issue #336 criado e lido pelo conector em 2026-10-18; sem validação de Claude Code)** |
| Work reage a evento de PR | Tarefa disparada por webhook (nota de 2026-08-25): PR aberto, pronto para revisão, fechado, revisão, comentário, commit, merge. Planos Plus, Pro, Business, Enterprise e Edu. Ação que pede aprovação fica parada até a revisão. | configuração | no plano | as três acima | DOC; **neste repo: NÃO CONFIRMADO** |
| Work escreve no GitHub | O app GitHub do ChatGPT **só lê**. Para editar código e fazer push, a doc manda usar o Codex. | não suportada | — | [conector GitHub](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt) | DOC |
| Conector GitHub | Settings > Plugins > GitHub, instalar o app no GitHub e escolher os repositórios. Disponível no chat, no deep research ou no agente, conforme o plano. Um repositório novo leva cerca de 5 min para aparecer. | configuração | no plano | idem | DOC |
| ChatGPT Projects | Juntam chats, arquivos e instruções, com memória padrão ou só do projeto; limite de arquivos por plano (Plus 25, Pro 40). O Work não funciona em projeto com memória só do projeto. A doc não fala em sincronizar com repositório. | nativa | no plano | [Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt) | DOC |
| Codex lê o `AGENTS.md` | Sim, em camadas: o global, depois da raiz do git até a pasta atual, e o mais próximo vale. Limite padrão de 32 KiB. | nativa | — | [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | DOC |
| Codex abre PR | O Codex Cloud roda cada tarefa isolada, com o computador dormindo, e pode fazer commit e abrir PR (a partir do Plus). A CLI roda local. Com login do ChatGPT usa a cota do plano; com chave própria, preço de API. | nativa / paga | cota do plano ou API | [cloud](https://learn.chatgpt.com/docs/cloud), [Codex no plano](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan) | DOC |
| MCP personalizado no ChatGPT | Servidor MCP remoto em Plugins. Escrita só no Business, Enterprise e Edu; no Pro, só leitura. | configuração | no plano | [developer mode](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt-beta) | DOC; **Plus: NÃO CONFIRMADO** |
| Ler conversas do ChatGPT a partir do Claude, ou o contrário | Nenhuma doc oferece. As duas ferramentas não compartilham conversa nem estado. | não suportada | — | — | DOC (nenhuma das páginas oferece) |

## Anthropic (Claude Code)

| capacidade | o que a doc diz | tipo | custo | fonte | status |
|---|---|---|---|---|---|
| `CLAUDE.md` | Instruções persistentes por projeto, usuário e organização; as de subpastas carregam sob demanda. São contexto, não regra imposta. | nativa | — | [memory](https://code.claude.com/docs/en/memory) | DOC; **TESTADO** (este repo usa) |
| `AGENTS.md` no Claude Code | Lido só quando **não há** `CLAUDE.md` na pasta ou acima, a não ser que o `CLAUDE.md` importe `@AGENTS.md`. Aqui há `CLAUDE.md`, então o Claude Code não lê o `AGENTS.md`, e é por isso que o `AGENTS.md` não repete regra. | nativa, com condição | — | idem | DOC |
| Hooks | Comandos em eventos (`PreToolUse`, `Stop`…), configurados em `settings.json`; podem bloquear. | nativa | — | [hooks](https://code.claude.com/docs/en/hooks) | DOC; **TESTADO** (H1, H1b, H3 em `.claude/`) |
| Skills | Pasta com `SKILL.md`; carregam quando a tarefa pede, ou por `/nome`. | nativa | — | [skills](https://code.claude.com/docs/en/skills) | DOC; TESTADO (`literatura-digilab`) |
| Subagentes | `.claude/agents/*.md`, com contexto próprio; `isolation: worktree` dá uma worktree temporária. | nativa | — | [sub-agents](https://code.claude.com/docs/en/sub-agents) | DOC |
| `claude -p` (sem interface) | Roda sem interação, com saída JSON. `--bare` exige `ANTHROPIC_API_KEY`; sem ele, usa o login atual. Sem `--bare`, roda hooks e o `.mcp.json` do projeto sem pedir confiança. | nativa | assinatura ou API | [headless](https://code.claude.com/docs/en/headless) | DOC (o uso da assinatura sem `--bare` é dedução) |
| `claude-code-action` (GitHub Actions) | Aceita `ANTHROPIC_API_KEY` ou `CLAUDE_CODE_OAUTH_TOKEN` (assinatura). Gasta minutos do Actions. Exige o app do Claude no GitHub com escrita e só dispara para quem tem escrita. | configuração / paga | minutos + tokens ou assinatura | [github-actions](https://code.claude.com/docs/en/github-actions) | DOC; **não configurado** (decisão: sem execução paga) |
| MCP no Claude Code | `claude mcp add` (HTTP, stdio), com escopo local, de projeto (`.mcp.json`) ou de usuário. | nativa | — | [mcp](https://code.claude.com/docs/en/mcp) | DOC |
| Sessões paralelas e worktrees | O app abre uma sessão por worktree. As regras de coordenador e worker são do projeto. | nativa | — | `docs/V2_TRABALHO_PARALELO.md` | TESTADO (as rodadas da V2) |

## GitHub

| capacidade | o que a doc diz | tipo | custo | fonte | status |
|---|---|---|---|---|---|
| Actions, repositório **público** | Runner padrão grátis em repositório público, Windows incluído (a página não o separa). Runner maior é sempre cobrado. | nativa | **grátis** (só runner padrão) | [billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) | DOC; o repo é público (`gh repo view`: `PUBLIC`, 2026-10-18) |
| Actions, se o repo voltar a ser **privado** | Cota de 2.000 min/mês no Free e 3.000 no Pro. Além da cota, por minuto: Linux US$ 0,006, Windows US$ 0,010, macOS US$ 0,062. O preço é por minuto, sem multiplicador. | paga | ver ao lado | idem | DOC |
| Taxa de plataforma para self-hosted | Anunciada em 2025-12-16 (US$ 0,002/min a partir de 2026-03-01) e adiada sem data. Hoje o self-hosted é grátis. Não é usado aqui. | — | hoje grátis | [changelog](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/) | DOC |
| `pull_request` × `pull_request_target` | O `_target` roda com escrita e secrets: não fazer checkout de código de fora nele. O `verificar-pr.yml` usa `pull_request` e `permissions: contents: read`. | nativa | — | [hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) | DOC |
| Injeção pelo corpo do PR | Não interpolar `${{ }}` dentro de `run:`; passar por `env:`. O workflow faz assim. | — | — | idem | DOC |
| Template de PR | `.github/pull_request_template.md`. Precisa estar no branch padrão para aparecer: só vale depois do merge. | nativa | — | [PR template](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository) | DOC |
| Check obrigatório (branch protection) | Em repositório público, inclusive no Free. Quem configura é o admin, ou seja, o Matheus (IM-1). | configuração | — | [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) | DOC; não configurado |
| Git worktree | `git worktree add [-b <branch>] <path> [<commit>]`; um branch só pode estar numa worktree por vez. | nativa | — | [git-worktree](https://git-scm.com/docs/git-worktree) | DOC; TESTADO (esta tarefa) |

## Recomendações

1. **O canal entre os dois lados é o GitHub.** O Claude Code escreve: branch, PR e o relato no corpo do PR. O ChatGPT e o Work leem pelo
   conector, que só lê. Não há sincronização de conversa nos dois sentidos, e nenhuma doc promete isso.
2. **A volta é semiautomática:** o Work pode ser disparado por evento de PR (DOC), mas isso precisa ser configurado e testado pelo Matheus.
   A ida (Work → repositório) passa por uma pessoa, porque o conector não escreve: o Matheus, ou o coordenador, commita a tarefa proposta.
3. **CI gratuito e sem secrets** para o que o repositório consegue conferir sozinho. Executar o Claude no CI (`claude-code-action`) fica
   fora até decisão, porque gasta tokens ou a assinatura.
4. **O Codex é a única ferramenta da OpenAI que escreve no repositório.** Se for usado, ele lê o `AGENTS.md` e segue as mesmas regras
   (worktree ou branch próprio, PR, sem merge).

## Limites de permissão, persistência e execução em segundo plano

- **O Work** roda na nuvem com o computador desligado. Uma ação que pede aprovação para até o Matheus revisar.
- **O `claude -p` sem `--bare`** roda os hooks e o MCP do projeto sem pedir confiança. Só usar em worktree conhecida.
- **Um commit feito com o `GITHUB_TOKEN` padrão não dispara outro workflow.** Um cron em repositório público é desligado depois de 60 dias
  sem atividade.
- **O app do Claude no GitHub** instala com escrita em Actions, Contents, Pull requests e Workflows, sem permissão parcial. Isso é motivo
  extra para não instalar sem decisão.

## Não confirmado

- Se o Work lê issues.
- MCP personalizado no Plus.
- O preço dos runners maiores.
- A nova data da taxa de self-hosted.
- O preço exato do Codex por plano.
- **Tudo o que o Work faz neste repositório**, até o teste com o Matheus.
