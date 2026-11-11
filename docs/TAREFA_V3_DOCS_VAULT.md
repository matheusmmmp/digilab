# TAREFA V3 — DOCS_VAULT (2026-11-05)

Coordenador: o Matheus. Worker: Claude Code (sessão no vault Obsidian da pesquisa). Worktree e branch: `v3-docs-vault`. Status: ENTREGUE.

Categoria: documentacao. Origem: Matheus, 2026-11-05: apontar no CLAUDE.md o vault Obsidian DigiLab Research como o lugar da documentacao fora do repositorio.

## 1. Pergunta

Não há hipótese: é uma tarefa de documentação. A pergunta é onde fica a documentação do projeto que não pertence ao repositório
(auditorias, temas, revisão de escopo, produção e divulgação), para que nenhuma sessão volte a escrevê-la em `D:\Trab\digilab\docs\`.

## 2. Depende de

Nada na `main`. A decisão do Matheus já existe: em 2026-11-05 ele indicou o vault Obsidian `C:\Users\mathe\Documents\DigiLab Research`
como o lugar da documentação do laboratório e pediu que o `CLAUDE.md` o declare.

## 3. Mudança mínima

Uma linha a mais no fim da tabela "Onde está o quê" do `CLAUDE.md`, apontando o vault e dizendo que nada ali é fonte de verdade sobre o
código. Mais este documento de tarefa. Não muda código, teste, protocolo nem nenhum outro documento.

## 4. Experimento e gate (se houver run)

Não há run. Sem plano de análise, sem sementes, sem métrica, sem GPU.

## 5. Entrega

- Testes: nenhum teste novo; o job `testes` do CI roda os testes da infra.
- Registro: sem desvio; nada a registrar em `docs/registro/`.
- PR contra a `main` com o relato no modelo de `.github/pull_request_template.md`. Merge só pelo Matheus.

## 6. Fora desta tarefa

Mover para o repositório qualquer conteúdo do vault; reescrever o restante do `CLAUDE.md`; o pacote do vídeo promo e os levantamentos de
ferramentas, que ficam no vault.

## 7. Critérios de aceitação

- O `CLAUDE.md` da `main` tem, na tabela "Onde está o quê", uma linha que cita `C:\Users\mathe\Documents\DigiLab Research` e
  `00 Início/Índice.md`.
- O job `relato` do CI passa com a categoria documentacao e só arquivos `.md` mudados.

## 8. Precisa do Matheus

Nenhuma, além do merge.
