# Investigação da Issue #336: autorização, labels e acesso do Claude Code

Status: PROPOSTO. Tarefa: `docs/TAREFA_V2_INVESTIGA_336.md` (categoria arquitetura, operação ENVIAR PARA INVESTIGAÇÃO do
`docs/infra/GUIA_OPERACIONAL.md`). Worker: sessão nova do Claude Code, worktree `v2-investiga-336`, 2026-10-18. Só auditoria, viabilidade e
riscos; nada aqui foi implementado, e nenhuma recomendação vale antes de o Matheus decidir.

## 0. O que o `gh` devolveu da Issue #336

Lido nesta sessão, em 2026-10-18, com `gh issue view 336 --repo matheusmmmp/digilab --comments` e
`gh api repos/matheusmmmp/digilab/issues/336` (mais `.../issues/336/comments`):

| campo | Issue | comentário 6253853412 |
|---|---|---|
| título | "POC: fluxo rastreável de ideia, tarefa V2 e PR" | — |
| autor (`user.login`) | `matheusmmmp` | `matheusmmmp` |
| `author_association` | `OWNER` | — |
| `performed_via_github_app` | `{"name": "ChatGPT Codex Connector", "slug": "chatgpt-codex-connector"}` | `{"name": "ChatGPT Codex Connector", "slug": "chatgpt-codex-connector"}` |
| criado em | 2026-10-18T18:56:31Z | 2026-10-18T18:59:53Z |
| estado, labels | `open`, nenhuma label | — |
| número de comentários | 1 | — |

O comentário único diz que a tarefa de documentação foi formalizada no PR #337 (`v2-chatgpt-claude-poc` → `main`, hoje MERGED). O corpo
da Issue traz o ID `CHATGPT-CLAUDE-POC-2026-10`, estado PROPOSTO, e as três questões pendentes que este relatório responde.

O que isso mostra: a Issue e o comentário aparecem como do `matheusmmmp`, mas a API diz que os dois foram escritos pelo app do ChatGPT. É
o caso que o `tools/conferir_autorizacao.py` existe para separar.

## 1. Como registrar a autorização humana sem duplicar o escopo

**O que existe hoje.**
- O protocolo: `docs/infra/GUIA_OPERACIONAL.md`, "Protocolo por Issue", etapa AUTORIZAR IMPLEMENTAÇÃO. A autorização é um comentário do
  Matheus na Issue com três linhas: o caminho da tarefa, o blob SHA do arquivo aprovado e "Escopo: seção 3 dessa tarefa". O escopo não é
  repetido no comentário: o comentário aponta para o conteúdo exato (o blob) da tarefa, que é a fonte do escopo.
- A conferência: `tools/conferir_autorizacao.py` (no branch `v2-infra-autorizacao`, PR #344, ainda aberto), com teste em
  `tests/test_infra_conferir_autorizacao.py`. Só vale o comentário do dono, tipo User, com `performed_via_github_app` nulo, não editado, e
  com o blob SHA igual ao da tarefa em `--ref`.
- Rodado nesta sessão: `python tools/conferir_autorizacao.py --issue 336 --tarefa docs/TAREFA_V2_INVESTIGA_336.md --ref origin/v2-infra-autorizacao`
  → blob `a632449c445d49dbc0ee2abfb879d372ff4b2710`, "Nenhum comentário de autorização na Issue #336", saída 1. É o esperado: esta tarefa é
  de investigação e ninguém autorizou implementação.
- O limite conhecido, escrito no próprio script e no guia: o `gh` do Claude Code usa o token do Matheus (`gh auth status`: conta
  `matheusmmmp`, keyring), então um comentário escrito por um agente via `gh` sai sem a marca de app e passaria na regra 2. A defesa hoje é
  só a regra do `AGENTS.md` (nenhum agente escreve a frase de autorização); o hook é a decisão IM-8, em aberto.

**Opções.**
- **A. Manter o comentário com blob SHA (o protocolo atual).** Não duplica o escopo (aponta para o blob), é barato, e a ferramenta já
  existe. Fraco contra um agente que use o token do Matheus.
- **B. A + o hook do IM-8.** Um hook do Claude Code que recusa um comando `gh` cujo corpo tenha a frase de autorização. Fecha o buraco do
  Claude Code; não cobre o Codex nem outro agente local com o mesmo token.
- **C. Autorização pelo merge da tarefa de implementação.** O merge na `main` já é só do Matheus; a tarefa de implementação separada (que
  o guia já exige) passaria a ser a autorização, e o comentário viraria só aviso. Não duplica nada e não depende de detectar o autor de um
  comentário. O custo: o merge também é feito pela conta do Matheus, e sem proteção da `main` (`gh api repos/matheusmmmp/digilab/branches/main`
  → `"protected": false`, o IM-7) um app com escrita poderia empurrar direto.
- **D. Review aprovado num PR, ou commit assinado.** Uma assinatura GPG/SSH do Matheus num commit da tarefa é a prova mais forte de
  autoria, mas exige configurar chave e conferir assinatura; o review aprovado sofre do mesmo problema do token.

**Recomendação (PROPOSTO).** Ficar com A, que já está pronta, e decidir o IM-8 (B) antes do primeiro uso real; considerar C como a regra de
fundo ("a tarefa de implementação na `main` é o que vale; o comentário só a liga à Issue"), o que já é quase o que o guia diz. Não adotar D
agora: é custo de configuração sem necessidade demonstrada.

**Risco e custo de errar.** Se A ficar sem B, um agente que desobedeça a regra pode forjar uma autorização indistinguível na API; o
estrago é limitado porque o worker ainda precisa da tarefa de implementação na `main`, e o merge é do Matheus. Se C for adotada sem
proteger a `main`, o merge deixa de ser uma barreira. O erro mais caro é tratar o nome do autor na tela como prova: a própria Issue #336
mostra que o nome engana.

## 2. Quais labels, se alguma, devem classificar ideias e tarefas

**O que existe hoje.** `gh label list --repo matheusmmmp/digilab` devolve só as 10 labels padrão do GitHub: `accessibility`, `bug`,
`documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`. A única Issue do
repositório (`gh issue list --state all`) é a #336, sem label. O guia já diz: "Labels são filtros auxiliares, não aprovação nem fonte de
estado. Neste MVP, use apenas labels existentes". O estado de cada tarefa mora no `Status:` do `TAREFA_V2_*.md` e no `docs/PAINEL_V2.md`.

**Opções.**
- **A. Nenhuma label.** O ID no corpo da Issue e o link para a tarefa bastam com uma Issue só.
- **B. Só as existentes, com um uso fixo:** `enhancement` para ideia nova, `question` para Issue que é só pergunta, `documentation` para
  ideia de documentação. Custo zero, nada novo criado.
- **C. Labels novas por etapa** (`ideia`, `investigacao`, `implementacao`). Mais fácil de filtrar, mas duplicam o estado que já mora na
  tarefa e no painel, e envelhecem quando ninguém as troca.

**Recomendação (PROPOSTO).** B, opcional: rotular só o tipo da Issue com as labels existentes, e nunca a etapa. Reabrir a questão quando
houver mais de umas dez Issues abertas ao mesmo tempo, que é quando filtrar começa a valer.

**Risco e custo de errar.** Baixo. O risco de C é o que a regra do guia evita: uma label de etapa desatualizada que alguém (ou o Work) lê
como estado ou como autorização. O custo de começar com B e mudar depois é rotular de novo poucas Issues.

## 3. Como confirmar o acesso de leitura do Claude Code ao branch e ao PR

**O que existe hoje.** O guia termina a seção do protocolo dizendo que a sessão do Work leu a Issue pelo conector, mas que "isso não
comprova que uma sessão Claude Code consiga lê-lo". Esta sessão é a prova pedida. Rodado aqui, em 2026-10-18:

| o quê | comando | resultado |
|---|---|---|
| autenticação | `gh auth status` | logado em github.com como `matheusmmmp` (keyring), protocolo https |
| a Issue | `gh issue view 336 ... --comments` e `gh api .../issues/336` | lidos o corpo, o comentário e os campos da seção 0 |
| os branches | `git ls-remote origin refs/heads/v2-infra-autorizacao refs/heads/v2-investiga-336` | os dois em `824cf17` |
| o PR de base | `gh pr list --head v2-infra-autorizacao --state all` | PR #344, OPEN, base `main` |
| o PR anterior | `gh pr view 337` | MERGED em 2026-10-18T23:54:01Z, `v2-chatgpt-claude-poc` → `main` |
| permissões | `gh api repos/matheusmmmp/digilab --jq .permissions` | `admin`, `maintain`, `push`, `triage`, `pull` todos `true`; repositório `public` |

O acesso de leitura está confirmado. Mais do que leitura: o Claude Code tem, pelo token do Matheus, permissão de administrador.

**Opções.**
- **A. Confirmar por sessão, como aqui:** o worker roda os comandos acima e os cita no relato. Custo zero; vale só para a máquina e o token
  daquele dia.
- **B. Um passo de conferência no início do worker** (por exemplo, a mensagem inicial do `V2_TRABALHO_PARALELO.md` pedir
  `gh auth status` e `gh pr view <base>`). Falha alto e cedo se o `gh` não estiver logado.
- **C. Um token próprio do Claude Code, só leitura** (fine-grained, `contents: read`, `issues: read`, `pull_requests: read`), com escrita
  só pelo token do Matheus. Resolveria também o limite da questão 1: um comentário do agente sairia com outro autor. Custo: criar e guardar
  o token, e o worker passaria a não conseguir abrir PR nem comentar sem outro passo.

**Recomendação (PROPOSTO).** A agora (esta seção é o registro), e B se o fluxo for repetido. C é a única que separa de fato o agente do
Matheus na API, mas muda o fluxo do worker (que hoje abre o PR); só vale se o Matheus quiser que a autoria na API seja prova.

**Risco e custo de errar.** O risco não é de falta de acesso, é de excesso: o mesmo token que lê também faz merge, muda a proteção da
`main` e escreve comentário como o Matheus. Hoje o que impede isso é só a regra escrita (`AGENTS.md`, `CLAUDE.md`) e a disciplina da
sessão. Errar por ficar em A custa pouco enquanto os agentes obedecem; errar ao adotar C sem ajustar o fluxo trava os workers.

## 4. O que não foi verificado

- Não conferi se outra máquina, ou uma sessão do Claude Code na nuvem, tem o mesmo acesso: tudo acima vale para esta máquina e este token.
- Não li o histórico de nenhuma conversa; o contexto é só o do repositório e o do `gh`.
