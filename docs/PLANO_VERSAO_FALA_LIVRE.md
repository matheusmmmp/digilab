# Plano — versão experimental "fala livre" (isolada e removível)

Este plano define **como** a `docs/TAREFA_FALA_LIVRE.md` é implementada:
numa versão separada, que pode ser aprovada ou apagada sem deixar resto na
`main`. Onde este plano e a tarefa divergirem, **vale este plano**.

## 1. Versões

- Antes de começar: tag `v1-antes-fala-livre` no commit atual da `main`.
- Branch de longa duração `exp/fala-livre`, criada a partir dessa tag.
  **Não há merge na `main` até a decisão da seção 6.**
- A versão experimental se identifica como **Digilab `exp-fala-livre`**
  (na tela da web e nos artefatos), para nunca ser confundida com a
  principal.
- A cada merge novo na `main` (ex.: análise de poder), fazer rebase da
  branch experimental e rodar os testes.

## 2. Rodar as duas versões lado a lado

- Criar uma cópia de trabalho separada:
  `git worktree add D:\Trab\digilab\v1-fala-livre exp/fala-livre`.
- Principal no servidor atual (porta 8766); experimental na porta
  **8767**, com o mesmo `servidor_local.py` da branch.
- Pasta de saves da experimental separada da principal. Um save da
  principal pode ser **copiado** para a experimental para testar o mesmo
  pet; nunca o caminho inverso.

## 3. Isolamento no código

Tudo que é novo fica em lugares próprios, para a remoção ser apagar
pastas.

| parte | onde fica |
|---|---|
| Python: prompt, chamada, verificador, avaliação | `digilab_fala_livre/` (pacote **fora** de `digilab/`) e `experiments/avaliar_fala.py` |
| Servidor | `servidor/fala_livre.py`, registrado no `servidor_local.py` por **um** ponto de entrada |
| Web | `web/modulos/fala_livre.js`, carregado pela página por **uma** linha |
| Artefatos | `artifacts_fala_livre/` |
| Falas e conversas | **log de apresentação separado** por pet (`<save>.fala.jsonl`) |

Regras:

- **O log principal do pet não ganha tipos de evento novos.** Falas e
  mensagens vão no log de apresentação separado. Assim a versão do save
  não muda (continua v3) e os saves continuam válidos se a experiência for
  removida. (Isto substitui o trecho da tarefa que gravava as falas no
  log principal.)
- O replay das falas lê o log de apresentação; o replay do pet não sabe
  que ele existe.
- Nenhum arquivo de `digilab/` importa `digilab_fala_livre` (teste por
  AST). O inverso é permitido: a fala lê o estado do pet.
- Na web, os pontos de contato com o arquivo principal são **no máximo
  três ganchos**, cada um marcado com o comentário
  `// GANCHO fala-livre`:
  1. carregar o módulo;
  2. entregar os fatos do pet quando há um gatilho de fala;
  3. montar o campo de conversa na aba Estado.
- Sem o módulo carregado, a página funciona exatamente como a principal.

## 4. Etapas (um commit por etapa, na branch experimental)

1. Tag, branch, worktree, porta 8767 e identificação da versão.
2. Pacote `digilab_fala_livre/`: bloco de fatos com identificadores,
   prompt de sistema, chamada **só ao Ollama local**, parser que falha
   alto. Levantar a memória da máquina e propor até dois modelos locais
   maiores que o `qwen2.5:3b`, para o Matheus aprovar antes de baixar.
3. Verificador (afirmações causais e manipulação) e log de apresentação.
4. Servidor: rota da fala livre.
5. Web: módulo, três ganchos, campo de conversa, ícone do verificador.
6. Avaliação offline: 200 situações + 30 perguntas, moldura × livre,
   `avaliacao_cega.csv`.
7. Relatório (seção "O que reportar" da tarefa) + checklist de remoção
   conferido.

Antes da etapa 2, mostrar ao Matheus o prompt de sistema.

## 5. Critérios de decisão (fixados antes de rodar)

Todos medidos nos artefatos da avaliação offline e na avaliação cega.

| critério | aprovar | reprovar |
|---|---|---|
| afirmações causais não suportadas, no melhor modelo local | ≤ 5% | > 15% |
| manipulação detectada | 0 | qualquer caso confirmado à mão |
| pegadinhas da conversa (inventar o que não aconteceu) | ≤ 3 de 30 | > 8 de 30 |
| avaliação cega, "interessante" (média) | livre ≥ moldura + 0,5 | livre ≤ moldura |
| avaliação cega, "soa como este pet" | livre ≥ moldura | livre < moldura − 0,5 |
| latência p90 por fala, no modelo escolhido | ≤ 3 s | > 8 s |

Entre os limites de aprovar e reprovar: **zona de ajuste**, com uma
rodada de mudança no prompt e nova avaliação, no máximo.

Se o livre só passar num modelo local maior, a decisão pode ser "aprovar
só com esse modelo", mantendo a moldura para os menores. **Nenhuma API
paga (Claude ou outra) entra neste experimento.**

## 6. Decisão (do Matheus)

- **Aprovar:** merge de `exp/fala-livre` na `main` com `modo_fala`
  ainda desligado por padrão; ligar depois, se quiser. Registrar em
  `docs/REGISTRO_DESVIOS.md`.
- **Reprovar:** seguir a seção 7. Os artefatos e o relatório ficam
  arquivados na tag `exp-fala-livre-arquivada` (para a revisão de
  literatura e o registro de desvios), mas nada entra na `main`.

## 7. Checklist de remoção

1. `git tag exp-fala-livre-arquivada exp/fala-livre` (guardar a história).
2. `git worktree remove D:\Trab\digilab\v1-fala-livre`.
3. `git branch -D exp/fala-livre` (local e remoto).
4. Parar o servidor da porta 8767.
5. Conferir que a `main` não tem `digilab_fala_livre`,
   `servidor/fala_livre.py`, `web/modulos/fala_livre.js` nem o texto
   `GANCHO fala-livre`.
6. Os saves da principal nunca foram tocados; os arquivos `.fala.jsonl`
   da pasta experimental podem ser apagados.

Como nada foi mergeado, a remoção não exige mudança na `main`. O passo 5
é só a confirmação.
