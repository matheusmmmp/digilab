# TAREFA V2 — TRANSICAO_V3: fechar a V2 e propor o plano da V3 (2026-10-30)

Coordenador: Gerente da transição V2 → V3 (Claude Code, Opus 5.5). Worker: o mesmo. Worktree e branch: `v2-transicao-v3`. Status:
**ENTREGUE (PR aberto, sem merge).** Só papel.

Categoria: arquitetura. Origem: Matheus, 2026-10-30: o prompt do Gerente "aposentar a V2 e começar a V3", com a definição da V3 em três
trilhas (cérebro, layout, batalha).

## 1. Pergunta

Em que estado cada tarefa, marco e frente da V2 fica quando a V2 fecha, e qual é o plano da V3, por trilha?

## 2. Depende de

- A `main` em `b3643bb` (PR #475).
- As decisões V3-D1 a V3-D8 (seção 8). Até o Matheus responder, os dois documentos novos ficam PROPOSTOS.

## 3. Mudança mínima

- **Novo:** `docs/FECHAMENTO_V2.md` (a tabela de toda tarefa, marco e frente da V2, com a marca de cada um) e `docs/PLANO_V3.md` (as
  perguntas, as trilhas C, L e B, as missões propostas, as regras que continuam e o glossário V2 × V3).
- **Alterado:** só o registro (`docs/registro/2026-10.md` e `docs/REGISTRO_DESVIOS.md`).
- **Não muda:** nenhum código, nenhum `TAREFA_V2_*.md`, o `CLAUDE.md`, o `PAINEL_V2.md`. Nada é renomeado nem movido.

## 4. Experimento e gate (se houver run)

Nenhum. Nenhuma vida, nenhuma faixa.

## 5. Entrega

- Um PR (`v2-transicao-v3`), com o relato no corpo e as V3-D1 a V3-D8 listadas.
- `python tools/conferir_saude.py` antes do PR.
- O merge é só do Matheus.

## 6. Fora desta tarefa

- A tag `v2-final`, o clone `v3`, o cabeçalho "congelado" nos documentos da V2, a última linha do `PAINEL_V2.md` e o PR do `CLAUDE.md`:
  dependem das V3-D2, D3, D5 e D7 e vêm depois do merge.
- Abrir qualquer missão da V3: o despacho espera as V3-D1 a V3-D8.
- Mudar as frentes em voo (a M7 do layout e a rodada 2 do combate seguem nas sessões delas).

## 7. Critérios de aceitação

- Toda tarefa `docs/TAREFA_V2_*.md` da `main` em `b3643bb` aparece numa linha do `docs/FECHAMENTO_V2.md`, com uma marca e o documento de
  onde vem.
- Nenhum número no fechamento sem o documento ou o PR de onde ele vem.
- O `docs/PLANO_V3.md` diz, por trilha, a pergunta, o que conta como "terminou", as missões, as dependências e os arquivos tocados.
- `python tools/conferir_saude.py` passa.

## 8. Precisa do Matheus

As V3-D1 a V3-D8, no `docs/PLANO_V3.md`, seção 7, cada uma com a recomendação e o custo de errar.
