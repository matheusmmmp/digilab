# Como trabalhar em paralelo na V2

Status: **PROPOSTO** (2026-10-01). Regras de organização para várias sessões (chats) trabalhando ao mesmo tempo nas frentes da V2
(`docs/PLANO_V2_PESQUISA.md`). Não muda nenhuma regra de pesquisa do `CLAUDE.md`; só diz quem trabalha onde e como as entregas se juntam.

## 1. Pastas

- `D:\Trab\digilab\v2` é a **referência da `main`**: ninguém troca o branch dela nem trabalha nela. Serve para ler, criar worktrees e rodar
  `git fetch`. A `v1` é a pasta antiga: só leitura.
- **Cada worker trabalha na própria worktree**, criada a partir da `main`, com um branch por frente. Pasta, branch e frente têm o mesmo nome:

```bash
git -C D:/Trab/digilab/v2 fetch origin
git -C D:/Trab/digilab/v2 worktree add D:/Trab/digilab/v2-<frente> -b v2-<frente> origin/main
```

- Exemplos de nome: `v2-f0-inventario`, `v2-l0-lobos`, `v2-l1-decisao`, `v2-a1-comida`.
- Cada worktree precisa do próprio ambiente: `python -m venv .venv` e `pip install pytest anthropic`; em `web/app`, `npm install`.
- Ao fechar a frente (PR mesclado), a worktree pode sair com `git worktree remove`.

## 2. Papéis

| papel | quantos | faz | não faz |
|---|---|---|---|
| **Coordenador** | 1 chat | mantém o plano e a ordem das frentes; escreve as tarefas; reserva sementes; revisa PRs; escreve o marco de cada rodada; leva as decisões ao Matheus | não escreve código de frente; não faz merge |
| **Worker** | 1 chat por frente | lê a tarefa, trabalha só na worktree dela, entrega um PR e para | não mexe em outra frente; não muda plano congelado; não faz merge |
| **Matheus** | — | referenda gates e parâmetros PROPOSTOS; aprova frentes; faz os merges (`gh pr merge`) | — |

## 3. A tarefa fica num arquivo

- O coordenador escreve `docs/TAREFA_V2_<FRENTE>.md` a partir do modelo `docs/modelos/TAREFA_V2_MODELO.md` e faz o commit na `main` (por PR) antes de
  abrir o worker.
- Frente com run: o plano de análise `docs/PLANO_ANALISE_V2_<FRENTE>.md` é commitado **antes** da run, como sempre.
- Mensagem inicial padrão do worker (o chat abre já na pasta da worktree):

> Leia o `CLAUDE.md` inteiro e `docs/TAREFA_V2_<FRENTE>.md`. Trabalhe só nesta worktree (`v2-<frente>`, branch `v2-<frente>`). Siga as regras do
> `CLAUDE.md` e de `docs/V2_TRABALHO_PARALELO.md`. Ao terminar: testes passando, PR contra a `main` com o resumo e os números (cada um com o artefato),
> aviso ao coordenador e pare. Merge só quando o Matheus pedir.

## 4. Ordem e recursos compartilhados

- **Paralelo só o que o plano permite.** Na fase 1: L0 (esqueleto dos lobos, aprendizado desligado) antes de L1, L2 e L3; F0 e A1 podem correr ao lado.
  Duas alavancas novas nunca no mesmo braço antes de cada uma passar sozinha.
- **GPU (uma RTX 2060):** uma frente com Ollama por vez. O coordenador mantém a fila.
- **Sementes:** cada frente recebe do coordenador uma faixa própria, anotada na tarefa; calibração e validação continuam separadas
  (3101…3505 e 4101…4505 para os gates da fase 1, conforme o plano de análise de cada frente).
- **Arquivos que todos editam** (o registro de desvios): cada worker acrescenta a própria seção no fim e não reescreve a dos outros.
  No conflito de merge, mantêm-se todas as seções. Desde a etapa 2 da rodada de saúde (2026-10-13), o registro é dividido por mês: a
  seção vai no fim de `docs/registro/AAAA-MM.md` (o mês da data dela), e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`. Um PR
  que ainda escreveu no formato antigo é absorvido por `python tools/registro_por_mes.py absorver <commit>`. Desde a etapa 1 da rodada de saúde (2026-10-13), o `CLAUDE.md` não recebe seção de
  etapa: o resumo vai no documento da frente, e o `CLAUDE.md` só muda com o ok do Matheus. As pendências estão no `docs/PAINEL_V2.md`,
  que é do coordenador.
- **Versão de pet:** só o coordenador reserva o número da próxima `VERSAO_PET`, para duas frentes não pegarem o mesmo.

## 5. Acompanhamento

- Barra lateral do app: grupo **"V2"** com o coordenador e os workers.
- Fim de cada worker: mensagem ao coordenador com PR, artefato, números e o que ficou aberto.
- Fim de cada rodada: o coordenador escreve `docs/V2_RODADA_<N>.md` (o que passou, o que falhou, decisões pendentes, a próxima divisão de frentes) e
  leva ao Matheus.
- Rodadas fechadas e curtas (avaliação de prompt, revisão de literatura, verificação de achados) podem ser um workflow num chat só em vez de vários
  workers; frentes longas de código ficam em chats separados.

## 6. O que nunca fazer

- Trabalhar ou trocar branch na pasta `v2` (ou na `v1`).
- Usar `git stash` sem etiqueta: a pilha é compartilhada entre worktrees.
- Fazer merge, mesmo com o PR verde: é do Matheus.
- Rodar sem plano de análise commitado, ou ajustar olhando a amostra de validação.

## 7. Agentes de fora do Claude Code (2026-10-18) — PROPOSTO

Desenho em `docs/TAREFA_V2_INFRA_MULTIAGENTE.md` e `docs/infra/GUIA_OPERACIONAL.md`. Não muda nenhuma regra acima; só diz onde o ChatGPT, o
ChatGPT Work e o Codex entram.

- **O ChatGPT e o Work pesquisam, propõem e revisam.** Leem o repositório pelo conector GitHub (só leitura; a leitura neste repositório
  está PENDENTE de teste, `docs/infra/TESTE_CHATGPT_WORK.md`). A porta de entrada deles é o `AGENTS.md`.
- **A tarefa proposta por eles entra como qualquer outra:** o coordenador ou o Matheus roda `tools/nova_tarefa.py`, com `--origem`, e
  commita por PR antes de abrir o worker.
- **O Codex, se for usado, é um worker:** worktree ou branch próprio, PR, sem merge, com as mesmas sementes e a mesma fila da GPU do
  coordenador.
- **O relato de volta é o corpo do PR**, no formato do `.github/pull_request_template.md`. O CI (`verificar-pr`) confere o que dá para
  conferir no repositório. O resto é declarado e passa pela revisão.
- **O que continua só do Matheus:** merge, decisão de número, abrir a validação, ligar serviço pago e dar acesso ao GitHub.
