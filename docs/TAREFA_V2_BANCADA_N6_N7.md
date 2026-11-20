# TAREFA V2 — BANCADA-N6-N7 (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-n6-n7`. Status: ABERTA.

## 1. Pergunta

Infraestrutura da bancada para a memória (N6) e a arbitragem (N7), para que os dois rodem sem orquestrador novo quando o cérebro estiver
pronto (chat B, depois do N5).

## 2. Mudança mínima (só `experiments/` e `digilab/metrics.py`)

- **Faixas reservadas:** acrescentar 21101…21505 e 22101…22505 (N7).
- **Mundo `iguais_frutas`** (N7-5): as frutas com o mesmo efeito, as ofertas do `CalendarioFrutas`.
- **Braços do N6** (`docs/PLANO_ANALISE_V2_N6.md`): relevante, nenhuma, só recência e embaralhada, com o aprendizado do lobo de decisão
  desligado (N6-2); o embaralhamento por desarranjo com rng própria (N6-6). A memória em si é do chat B: até ela existir, esses braços
  levantam `NotImplementedError` com o nó, como a bancada já faz.
- **Braços do N7** (`docs/PLANO_ANALISE_V2_N7.md`): com e sem pedido, P3+ped, com o dono que pede do chat A (`TAREFA_V2_N7_MUNDO.md`)
  quando estiver na `main`.
- **Medidas** dos dois planos que ainda não existem em `metrics.py` (por exemplo, a deferência por zona do N7, a fração de citações de
  memória do N6 sobre as decisões em que ela pode agir), testadas em dados sintéticos.
- **Não muda:** `engine.py`, `lobos.py`, `frutas.py`, a web.

## 3. Gates

G1 de toda vida nova; `iguais_frutas` com as mesmas ofertas dos outros mundos de frutas; os braços que dependem do cérebro falham alto com
o nó; as medidas recuperam a resposta conhecida em dados sintéticos. Só as sementes dos testes.

## 4. Entrega

Um PR, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Merge só
pelo Matheus.
