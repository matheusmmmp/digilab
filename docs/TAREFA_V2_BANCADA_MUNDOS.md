# TAREFA V2 — BANCADA-MUNDOS (2026-10-01)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-mundos`. Status: ABERTA.

## 1. Pergunta

Infraestrutura: o campo **mundo** da bancada (`experiments/bancada_v2.py`, hoje só `padrao`) passa a montar as condições da pergunta
maior, para o experimento maior rodar sem orquestrador novo.

## 2. Depende de

Bancada (#126) e bola (#127) na `main`. Frutas (N4, chat A) para o descasado e o mutável: até elas entrarem, esses mundos falham alto com
o nó, como hoje.

## 3. Mudança mínima

- **Mundo `bola`** pela bancada, usando o `MotorAmbiente` (#127), já com as decisões da bola de 2026-10-01: `por_bola` **fora do sorteio do
  dono aleatório** (B1) e a bola **fora do orçamento** (B2). Os donos da bola da A1 ficam como estão (a A1 reproduz).
- **Contrato das condições** (`casado`, `descasado`, `mutavel`): `casado` = mundo padrão ou bola; `descasado` e `mutavel` declarados com o
  que precisam do N4 (preferência inata × efeito real das frutas; troca do efeito no meio da vida) e `NotImplementedError` até lá.
- **Modo acoplado com o mundo:** reproduzir o registro de uma vida num mundo em outro braço sem perder os eventos do mundo (pôr/tirar a
  bola, ofertas futuras de fruta).
- **Não muda:** `engine.py`, `lobos.py` (chat B), `ambiente.py` além do que o mundo `bola` pede (combinar com o chat A se precisar), a web.

## 4. Gates (sem run de pesquisa; só as sementes dos testes)

G1 replay de toda vida dos mundos novos; mundo `bola` com as regras da A1 reproduz a vida da A1 byte a byte; com B1 e B2 ligados, o dono
aleatório nunca sorteia `por_bola` e a bola não gasta orçamento (teste); acoplado com mundo reproduz.

## 5. Entrega

Um PR. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus.

## 6. Fora desta tarefa

Os sinais P1 (chat B) e P2 (N5), as frutas em si (chat A), qualquer run com faixa reservada.
