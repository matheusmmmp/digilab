# TAREFA V2 — ROTEAMENTO_MODELOS (2026-10-18)

Coordenador: ChatGPT Work. Worker: ChatGPT Work (documentação pelo conector GitHub). Worktree e branch: `v2-roteamento-modelos`.
Status: ENTREGUE (alteração documental entregue por PR; merge do Matheus).

## 1. Pergunta

Como orientar a escolha econômica de modelo e de contexto sem alongar o `CLAUDE.md` nem confundir instrução textual com configuração?
É uma tarefa de infraestrutura, sem hipótese científica.

## 2. Depende de

Autorização explícita do Matheus em 2026-10-18 para incluir a regra no `CLAUDE.md`, após a análise da organização híbrida.
Não depende dos PRs de infraestrutura ainda abertos.

## 3. Mudança mínima

- Acrescentar ao `CLAUDE.md` uma seção curta sobre modelo e contexto, preservando o restante byte a byte.
- Registrar a autorização e a interpretação em `docs/registro/2026-10.md`, com a linha correspondente no índice
  `docs/REGISTRO_DESVIOS.md`.
- Entregar esta tarefa no formato do modelo V2 existente na `main`.
- A regra expressa preferências por famílias de modelos, com escalada conforme dificuldade e sem reduzir os critérios de aceitação.

## 4. Experimento e gate (se houver run)

Não há run, sementes, parâmetros científicos nem uso de GPU.
Verificar o diff e reler os documentos gravados; a mudança é exclusivamente documental.

## 5. Entrega

PR contra a `main`, com o relato da mudança e as verificações. Merge só pelo Matheus.
Verificar que apenas a seção nova foi inserida no `CLAUDE.md` e que os registros anteriores foram preservados integralmente.
Testes de código não executados: não há alteração executável.

## 6. Fora desta tarefa

Configurar modelos locais, criar subagentes, alterar permissões ou hooks, ativar serviços pagos, modificar código ou mudar gates científicos.

## Resumo da etapa

A seção orienta a escolha pelo risco e pela incerteza, a preferência de modelo por tipo de demanda, o uso de scripts para operações
mecânicas, o contexto mínimo e a escalada com justificativa. Deixa explícito que a configuração da sessão ou do agente é que seleciona
o modelo efetivo. A autorização está no registro do mês; o worker entrega por PR e para.
