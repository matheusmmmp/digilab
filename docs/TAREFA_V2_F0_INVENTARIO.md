# TAREFA V2 — F0-INVENTARIO (2026-10-01)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: a abrir. Worktree e branch: `v2-f0-inventario`.
Status: ABERTA.

## 1. Pergunta

O que o jogo e a pesquisa têm hoje, o que está validado e o que é provisório, e **qual interação mínima com consequência** a fase 1a deve usar?
Fase 0, item 2 do `docs/PLANO_V2_PESQUISA.md` ("o primeiro passo concreto"); passo 1 do `docs/TODO_INTERACAO_CORPO.md`.

## 2. Depende de

Nada além da `main`. Leitura obrigatória: `CLAUDE.md`, `docs/PLANO_V2_PESQUISA.md` (PR #102, se ainda não estiver na `main`: `git show origin/plano-v2-pesquisa:docs/PLANO_V2_PESQUISA.md`),
`docs/TODO_INTERACAO_CORPO.md`, `docs/LEITURA_CONSOLIDADA_DONO.md`, `docs/futuro/dwarf_fortress.md`.
Insumo fora do repositório (auditoria da Fase 1, aprovada pelo Matheus): `D:\Trab\digilab\docs\digibrain\integration\01_CURRENT_STATE.md`. Use como ponto de partida,
mas confira cada item no código: ela foi escrita sobre o commit `3fe6d76` e a `main` andou depois.

## 3. Mudança mínima

Só documento: `docs/V2_INVENTARIO_JOGO.md`. **Nenhum código muda.**

Conteúdo:
1. Tabela de mecânicas (Python e web): nome, onde está (arquivo e símbolo), rótulo `EXECUTADO / ESPECIFICADO / IDEIA`, validada por gate com artefato ou
   provisória, usada pela pesquisa (sim/não), versão de pet em que entrou.
2. As decisões do pet hoje: em que momentos o pet escolhe uma ação, quantas escolhas por dia, e em quais o dono muda o resultado (é o que a V2 quer aumentar).
3. Candidatas à interação mínima da 1a (comida posta no cenário, bola, obstáculo, equipamento; outras que o inventário mostrar): para cada uma, o que o pet
   percebe, o que decide, a consequência, o que mudaria no motor, e o risco de virar outro canal de cuidado (o confundidor da `LEITURA_CONSOLIDADA_DONO.md`).
4. Recomendação em até 3 frases, terminando com a pergunta ao Matheus sobre qual interação ele aprova.

## 4. Experimento e gate

Sem run, sem sementes, sem GPU.

## 5. Entrega

- Testes: `python -m pytest tests/ -q` (só para confirmar que nada mudou).
- Registro: seção própria no fim do `docs/REGISTRO_DESVIOS.md` só se encontrar divergência entre documento e código.
- PR contra a `main` com o resumo. Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Desenhar ou implementar a interação; mexer no vínculo (frente `v2-f0-vinculo`); qualquer mudança de jogo.
