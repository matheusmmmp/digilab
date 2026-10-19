# Relatório da prova de conceito da infra multiagente (2026-10-18)

Tarefa da prova: `docs/TAREFA_V2_INFRA_POC.md`, que está no branch `v2-infra-poc`, PR
[#331](https://github.com/matheusmmmp/digilab/pull/331), empilhado sobre o #326. Tarefa da infra: `docs/TAREFA_V2_INFRA_MULTIAGENTE.md`.

**A tarefa:** um parágrafo novo no `docs/infra/GUIA_OPERACIONAL.md` com os dois comandos locais de `tools/verificar_relato.py`. É pequena,
reversível e só de documentação.

## Resultado em uma linha

**O lado do Claude Code e do GitHub funcionou de ponta a ponta.** O lado do ChatGPT Work foi testado depois, no mesmo dia
(`docs/infra/TESTE_CHATGPT_WORK.md`): a leitura e o gatilho funcionam. A escrita funciona quando o conector tem escrita, o que pede a `main`
protegida (IM-7). A etapa 7 abaixo
ficou com o substituto; o teste do Work feito em seguida é o que conta para ela.

## As etapas

| # | etapa | como | estado | evidência |
|---|---|---|---|---|
| 1 | criar a especificação | o coordenador (esta sessão) escreveu o pedido | **executada** | as seções 1, 3 e 7 da tarefa |
| 2 | gerar o handoff | `python tools/nova_tarefa.py INFRA_POC --categoria documentacao --origem "Claude Code" …`; depois o coordenador preencheu os `<...>` | **executada** | commit `8206cf2` no `v2-infra-poc` |
| 3 | o executor lê o handoff | uma **sessão nova do Claude Code**, sem histórico, aberta na worktree `v2-infra-poc` só com a mensagem padrão do worker | **executada** | o relato do #331 diz o que ela leu (`CLAUDE.md`, `AGENTS.md`, a tarefa) |
| 4 | executar a tarefa | o worker escreveu o parágrafo e rodou os dois comandos antes de escrever | **executada** | o diff do #331 (`docs/infra/GUIA_OPERACIONAL.md`) |
| 5 | gerar evidências | o CI do #331: job `relato` ok, job `testes` ok (os `tests/test_infra_*.py` rodados no Windows) | **executada (VERIFICADA pelo CI)** | `gh pr checks 331` |
| 5b | **teste negativo** | o coordenador tirou `Executor:` do corpo do #331 e trocou o "não rodados" por "todos os testes passam" | **executada** | o job `relato` reprovou: `campo Executor` FALHA, e a frase de sucesso saiu como alerta DECLARADA (run `39149575989`). Com o corpo restaurado, passou de novo (run `39149686082`) |
| 6 | produzir o relato de volta | o corpo do #331, no formato do `.github/pull_request_template.md` | **executada** | o #331 |
| 7 | recuperar o relato no ambiente de revisão | **ChatGPT Work: PENDENTE** (IM-3, `docs/infra/TESTE_CHATGPT_WORK.md`). No lugar dele, um subagente do Claude sem histórico leu só o PR pelo `gh` | **substituto, não é o teste do Work** | o substituto resumiu o PR, separou o declarado do verificado (`relato` e `testes` ok) e listou as questões abertas do relato. Disse que entendeu o trabalho sem o histórico |
| 8 | atualizar o contexto compartilhado | `python tools/gerar_estado_atual.py` no `v2-infra-poc`: o `--conferir` acusou desatualizado, e a regeneração mostrou `TAREFA_V2_INFRA_POC … ABERTA` | **executada localmente, não commitada** | a regeneração no PR mudaria o PR do worker. Pela proposta IM-4, quem regenera é o coordenador, depois do merge |

## O que a prova achou (e o que já foi corrigido)

| achado | quem achou | o que foi feito |
|---|---|---|
| o verificador tomava `<corpo.md>` dentro de código por resto do modelo e marcava a seção como vazia | o worker | **corrigido** no #326: o `<...>` dentro de crase ou bloco de código não conta, com teste novo |
| `--pr` ignora `--base`, e a docstring não dizia | o worker | **corrigido** na docstring |
| no runner Windows, o Python escreve CRLF, e o `\r` entrava no nome do arquivo de teste | o CI do #326 | **corrigido** no workflow (`tr -d '\r'`) |
| a seção 5 do modelo sempre pede o registro e o "PR contra a `main`", o que conflita com uma tarefa só de documento ou com PR empilhado | o worker | **não corrigido**. O worker seguiu as seções mais específicas. Fica como melhoria do modelo, para decidir |
| o critério "o diff só toca o guia" não vale para o PR inteiro, porque o commit do coordenador com a tarefa vai junto | o worker | **registrado**. Quando a tarefa entra na `main` por PR antes do worker, como manda o protocolo, isso some. Aqui ela foi junto por causa do empilhamento |
| o comando do guia com `--base origin/main` não foi rodado como está escrito; foi rodado com `origin/v2-infra-multiagente` | o revisor substituto | **registrado**: é equivalente, mas não idêntico |

## O que não foi provado

- **A ida de uma tarefa do Work para o repositório por PR:** o Work comentou e criou um branch, mas não abriu um PR de tarefa
  (`TESTE_CHATGPT_WORK.md`, passo 6).
- **Uma tarefa de categoria implementacao, experimento, literatura ou arquitetura num PR real.** Essas regras só foram testadas em
  `tests/test_infra_verificar_relato.py`, com repositórios de teste.
- **O check obrigatório na `main`** (IM-1): não foi ligado.
