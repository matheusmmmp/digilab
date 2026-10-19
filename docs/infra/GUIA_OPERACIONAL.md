# Guia operacional: ChatGPT, ChatGPT Work e Claude Code no Digilab

Status: PROPOSTO (`docs/TAREFA_V2_INFRA_MULTIAGENTE.md`). Este guia não muda as regras do `CLAUDE.md` nem do
`docs/V2_TRABALHO_PARALELO.md`: só diz como os três ambientes entram nelas.

**O princípio:** a conversa é onde se pensa; o repositório é o que vale. Nada que está só numa conversa (do ChatGPT ou do Claude) conta
como decidido, implementado ou resultado.

## 1. O ciclo de um dia

```
ChatGPT / Work                    repositório (GitHub)                    Claude Code
───────────────                   ────────────────────                    ───────────
pesquisa, hipótese, desenho  ──►  Matheus/coordenador: nova_tarefa.py
                                  → docs/TAREFA_V2_<FRENTE>.md (PR)  ──►  worker na worktree v2-<frente>
                                                                          implementa, testa, registra desvio
                                  PR com o relato  ◄────────────────────  abre o PR e para
                                  CI: verificar-pr (relato + testes)
Work lê o PR pelo conector   ◄──  (testado em 2026-10-18; gatilho opcional)
revisão, inconsistências  ──────► Matheus decide e faz o merge
                                  coordenador: PAINEL_V2 + gerar_estado_atual.py
```

**O que é automático hoje:**
- o CI no PR;
- se o Matheus mantiver a tarefa agendada no Work, o aviso e o resumo de PR alterado, uns 5 min depois.

O Work lê o branch, o PR e o log do CI, mas não vê o que mudou no corpo de um PR. Ele só escreve no GitHub se o conector tiver escrita, e aí escreve em nome do Matheus. Tudo testado em
2026-10-18 (`docs/infra/TESTE_CHATGPT_WORK.md`). Todo o resto é uma pessoa ou uma sessão fazendo um passo.

## 2. Como fazer cada coisa

**Começar uma pesquisa no ChatGPT.** Abra pelo contexto do repositório, não pela memória da conversa:
> Leia o AGENTS.md, o docs/INDICE.md e o docs/PAINEL_V2.md de matheusmmmp/digilab. Quero pesquisar <tema>. Separe o que o repositório já
> decidiu do que é proposta sua.

Se o conector não estiver ligado, cole o `AGENTS.md` e o painel.

**Transformar a discussão em tarefa.** Peça ao ChatGPT um texto com as seções do modelo `docs/modelos/TAREFA_V2_MODELO.md`. Depois, no
repositório:
```bash
python tools/nova_tarefa.py <FRENTE> --categoria <implementacao|experimento|literatura|arquitetura|documentacao> --origem "ChatGPT" --resumo "<de onde veio>"
```
Cole o texto nos `<...>`, revise e faça o commit por PR. A tarefa só vale quando está na `main`.

**Passar a tarefa ao Claude Code.**
1. Crie a worktree com o comando que o `nova_tarefa.py` imprime.
2. Abra uma sessão nela.
3. Mande a mensagem inicial que ele também imprime, tirada do `V2_TRABALHO_PARALELO.md`.

**Recuperar o resultado.** O resultado está no PR: o corpo (o relato), o diff e o resumo do job `verificar-pr`. No Work: "leia o PR #N de matheusmmmp/digilab, o corpo e o resultado do check verificar-pr". Ele lê o log do CI. Sem o conector: copie o link ou o corpo.

**Continuar uma pesquisa anterior.** Não dependa do histórico do chat. Comece pela tarefa da frente e pelos documentos que ela cita.
- Literatura: `docs/referencias/` e as sínteses `*_SINTESE_*.md`.
- Resultados: `docs/RESULTADO_V2_*.md`.

**Consultar decisões antigas.**
- `docs/PAINEL_V2.md`, seção 3;
- as "decisões que valem" do `CLAUDE.md`;
- a seção de decisões de cada tarefa;
- `docs/REGISTRO_DESVIOS.md`, com o detalhe no mês em `docs/registro/`.

**Saber o estado atual.**
1. Rode `git fetch` (a pasta `v2` local pode estar velha).
2. Leia `docs/PAINEL_V2.md`.
3. Para as tarefas, `docs/ESTADO_ATUAL.md`: lembre que o status ali é o declarado no arquivo.

**Delegar tarefas independentes.** Uma frente, uma worktree, um worker, um PR. O que pode correr em paralelo, e com quais sementes, o
coordenador decide (`V2_TRABALHO_PARALELO.md`, seção 4). Workflows de vários agentes só para rodadas curtas e fechadas.

**Revisar uma implementação.**
1. Leia o relato.
2. Confira no resumo do CI o que é VERIFICADA e o que é só DECLARADA.
3. Leia o diff.
4. Peça uma segunda leitura ao Work ou a uma sessão nova do Claude, sem histórico.

**Recuperar depois de uma interrupção.**
- `git -C D:/Trab/digilab/v2 worktree list` mostra as frentes;
- `gh pr list --state open` mostra os PRs abertos;
- a tarefa de cada frente diz o que falta.

Commit de trabalho em andamento só no branch da frente. Nunca `git stash` sem nome.


### Protocolo por Issue: ideia, investigação e implementação

Use o Issue como registro curto da ideia e das perguntas. Não cole o histórico inteiro da conversa e não inclua conteúdo que não possa ficar visível no GitHub. **Este repositório está público no momento**; a visibilidade deve ser conferida antes de registrar qualquer dado sensível.

A fonte de verdade muda por etapa:

| etapa | fonte de verdade | uso dos outros artefatos |
|---|---|---|
| **REGISTRAR IDEIA** | Issue com ID, origem/contexto, hipótese ou objetivo, motivação, referências, estado PROPOSTO, dependências e questões abertas | comentários registram discussão; não iniciam worker |
| **ENVIAR PARA INVESTIGAÇÃO** | `docs/TAREFA_V2_<FRENTE>.md`, criado com `tools/nova_tarefa.py` e aprovado/mesclado pelo Matheus antes de abrir o worker | Issue guarda o link e o andamento, sem duplicar o escopo |
| **RELATAR RESULTADO** | PR: corpo no formato `.github/pull_request_template.md`, diff e resumo do CI | o Issue recebe um comentário curto com o link para o PR |
| **AUTORIZAR IMPLEMENTAÇÃO** | comentário explícito do Matheus no Issue, ligado ao blob SHA exato da tarefa e à seção 3 | o coordenador cria uma tarefa de implementação separada; o worker só começa depois de ela estar na `main` |

**REGISTRAR IDEIA.** Peça: “Registre essa ideia no Issue do DigiLab.” Resuma a conversa nos campos acima; mantenha o status **PROPOSTO**. A proposta não é decisão nem autorização.

**ENVIAR PARA INVESTIGAÇÃO.** Peça: “Envie a ideia #336 para investigação, sem implementar.” O coordenador preenche uma tarefa a partir de `docs/modelos/TAREFA_V2_MODELO.md`, referencia o Issue e delimita a mudança mínima como auditoria/investigação. Declare que arquitetura e funcionalidade ficam intocadas. Abra PR para a tarefa. **Só após o arquivo de tarefa estar na `main`** o coordenador cria a worktree e abre manualmente uma sessão Claude Code usando a mensagem da seção 3 de `docs/V2_TRABALHO_PARALELO.md`. Criar Issue ou PR não inicia Claude Code automaticamente.

**AUTORIZAR IMPLEMENTAÇÃO.** Depois de revisar o relatório, o Matheus pode comentar no Issue, por exemplo:
```
AUTORIZO IMPLEMENTAÇÃO: docs/TAREFA_V2_FRENTE.md
blob SHA: <SHA do conteúdo aprovado>
Escopo: seção 3 dessa tarefa
```
A aprovação só vale para aquele conteúdo e escopo. Se o blob SHA mudar, é necessária nova autorização. O coordenador abre uma tarefa de implementação separada; a investigação sozinha nunca autoriza código ou mudança de arquitetura. Labels são filtros auxiliares, não aprovação nem fonte de estado. Neste MVP, use apenas labels existentes; não crie um fluxo dependente de labels.

**Conferir a autorização antes de começar a implementação.** O ChatGPT Work, com escrita no conector, comenta **como matheusmmmp**: na tela,
o comentário dele e o seu parecem iguais (`docs/infra/TESTE_CHATGPT_WORK.md`, passo 6). Por isso o coordenador não confia no nome e roda:

```bash
python tools/conferir_autorizacao.py --issue <N> --tarefa docs/TAREFA_V2_<FRENTE>.md
```

O comentário só vale se:
- o autor é `matheusmmmp`, do tipo User;
- **`performed_via_github_app` é nulo**, ou seja, não foi escrito pelo app "ChatGPT Codex Connector";
- não foi editado depois de criado;
- o blob SHA é o da tarefa hoje na `origin/main`.

Saída 0 quer dizer autorizado; com saída 1, a tabela diz por quê. O blob SHA do conteúdo aprovado sai de
`git rev-parse origin/main:docs/TAREFA_V2_<FRENTE>.md`.

**Limite:** o `gh` do Claude Code usa o seu token (um app OAuth, não um GitHub App), então um comentário escrito pelo Claude Code com `gh` não
tem a marca do app. A defesa, nesse caso, é a regra do `AGENTS.md` e do worker: **nenhum agente escreve "AUTORIZO"**. Um hook que bloqueie
isso é a decisão IM-8.

**ENTREGA E RECUPERAÇÃO.** O worker abre um PR e para; não faz merge. O PR é a fonte do relato e das evidências. No Issue, registre apenas o link e o estado curto. Para retomar depois de uma interrupção, use o ID/link do Issue, o caminho da tarefa e o branch/PR; não dependa do histórico do chat. No Work, peça: “Leia o último PR ligado ao Issue #336, confira corpo, diff e check verificar-pr; separe o que foi declarado do que o CI verificou.” Esta sessão criou e leu o Issue #336 pelo conector GitHub; isso não comprova que uma sessão Claude Code consiga lê-lo.

GitHub Actions: use o `verificar-pr` que já existe; esta POC não adiciona Actions, secrets, serviços pagos nem execução automática de agentes.

## 3. O que o CI confere (`.github/workflows/verificar-pr.yml`)

**Job `relato`** (`tools/verificar_relato.py`). Confere os campos `Tarefa`, `Categoria`, `Executor` e `Branch` e as seções do template. Um
`<...>` que sobrou do modelo conta como vazio. Depois aplica a regra da categoria:

| categoria | o que é VERIFICADA (o repositório confere) |
|---|---|
| implementacao | algum `tests/` mudou ou é citado, e todo teste citado existe. Quem roda os testes é o job `testes` |
| experimento | o `PLANO_ANALISE_V2_*` citado existe e o primeiro commit dele vem antes do primeiro commit de todo artefato novo; todo `artifacts*/…` citado existe. A run não é refeita |
| literatura | Origem, DOIs, Resultados e Limitações estão preenchidos; todo DOI está em `docs/referencias/` e não está marcado como não verificado na tabela; nada mudou fora de `docs/` |
| arquitetura | o relato diz PROPOSTO; as decisões do Matheus estão listadas; nada mudou em `digilab/`, `experiments/` ou `web/app/src/` |
| documentacao | só mudaram documentos, e todo link relativo dos `.md` mudados resolve |

Uma frase como "os testes passam" no corpo vira **alerta DECLARADA**: só conta se o job `testes` passar.

**Job `testes`** (Windows, a plataforma do projeto):
1. roda os `tests/test_*.py` que o PR mudou e os `tests/test_infra_*.py`;
2. roda `tools/conferir_saude.py`;
3. roda `tools/gerar_estado_atual.py --conferir`, que só avisa.

A suíte inteira (~36 min) roda só manualmente: Actions > verificar-pr > Run workflow > `suite_inteira`.

**O que o CI não confere:**
- se a run de um experimento reproduz;
- se o número do relato bate com o artefato;
- se a literatura sustenta o que a síntese diz.

Isso continua com a revisão e com as skills de auditoria.

**Custo:** zero enquanto o repositório for público e o workflow usar runner padrão (`docs/infra/MATRIZ_CAPACIDADES.md`). Se o repositório
virar privado, os minutos passam a contar na cota da conta.

**Conferir um relato antes de abrir o PR.** O job `relato` roda também na máquina, com os mesmos critérios. Antes de abrir o PR, com o
corpo num arquivo e o branch-base do PR (`origin/main`, ou o branch de baixo num PR empilhado):

```bash
python tools/verificar_relato.py --arquivo <corpo.md> --base origin/main
```

Com o PR já aberto, o corpo e os arquivos mudados vêm pelo `gh`:

```bash
python tools/verificar_relato.py --pr <N>
```

Os dois imprimem a tabela da conferência e saem com 0 se o relato passa, com 1 se não. O `--arquivo` compara `git diff <base>...HEAD`;
rode `git fetch origin` antes, para a base estar atualizada.

## 4. Instalação no Windows (uma vez)

| passo | comando | depende de |
|---|---|---|
| Git e GitHub CLI | `winget install Git.Git GitHub.cli` | winget |
| login no GitHub | `gh auth login` | conta GitHub (interativo) |
| Python 3.10+ | `winget install Python.Python.3.12` | — |
| a referência da `main` | `git clone https://github.com/matheusmmmp/digilab.git D:/Trab/digilab/v2` | — |
| uma frente | `git -C D:/Trab/digilab/v2 fetch origin` e depois `git -C D:/Trab/digilab/v2 worktree add D:/Trab/digilab/v2-<frente> -b v2-<frente> origin/main` | — |
| o ambiente da frente | `python -m venv .venv`, depois `.venv\Scripts\python -m pip install pytest anthropic` | rede |
| conferir a infra | `.venv\Scripts\python -m pytest tests/test_infra_*.py -q` e `python tools/conferir_saude.py` | — |
| o Claude Code | o app desktop ou `npm install -g @anthropic-ai/claude-code` | assinatura Claude |
| o conector do ChatGPT | Settings > Plugins > GitHub (`docs/infra/TESTE_CHATGPT_WORK.md`) | plano pago do ChatGPT; testado em 2026-10-18. Com escrita, proteger a `main` antes (IM-7) |
| check obrigatório | GitHub > Settings > Branches > regra da `main` > exigir `verificar-pr` | decisão IM-1 do Matheus |

## 5. O que fica com o Matheus, sempre

- merge;
- decisão de número PROPOSTO;
- abrir a validação;
- configurar serviço pago (`claude-code-action`, Codex com chave de API);
- ligar o check obrigatório;
- dar ao app do ChatGPT ou do Claude acesso ao GitHub.

Nenhum agente faz isso, e nenhuma automação desta infraestrutura tenta fazer.
