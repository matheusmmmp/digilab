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
Work lê o PR pelo conector   ◄──  (PENDENTE: IM-3)
revisão, inconsistências  ──────► Matheus decide e faz o merge
                                  coordenador: PAINEL_V2 + gerar_estado_atual.py
```

**O que é automático hoje:** só o CI no PR. Todo o resto é uma pessoa ou uma sessão fazendo um passo. O Work lendo o PR e o gatilho de PR
estão **PENDENTES** até o teste (`docs/infra/TESTE_CHATGPT_WORK.md`).

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

**Recuperar o resultado.** O resultado está no PR: o corpo (o relato), o diff e o resumo do job `verificar-pr`. No Work (depois do IM-3):
"leia o PR #N". Sem o conector: copie o link ou o corpo.

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
| o conector do ChatGPT | Settings > Plugins > GitHub (`docs/infra/TESTE_CHATGPT_WORK.md`) | plano pago do ChatGPT; PENDENTE |
| check obrigatório | GitHub > Settings > Branches > regra da `main` > exigir `verificar-pr` | decisão IM-1 do Matheus |

## 5. O que fica com o Matheus, sempre

- merge;
- decisão de número PROPOSTO;
- abrir a validação;
- configurar serviço pago (`claude-code-action`, Codex com chave de API);
- ligar o check obrigatório;
- dar ao app do ChatGPT ou do Claude acesso ao GitHub.

Nenhum agente faz isso, e nenhuma automação desta infraestrutura tenta fazer.
