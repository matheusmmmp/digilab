# TAREFA V2 — BANCADA-K4-CANAIS (2026-10-05)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-k4-canais`. Status: ABERTA.
Rodada 10 do `docs/ROADMAP_V2.md`. **É pré-requisito da calibração conjunta (K2, chat B): faça primeiro e entregue rápido.**

## 1. Mudança mínima (só `experiments/` e `digilab/metrics.py`)

- **K4, fora do orçamento** (decisão do Matheus, 2026-10-05):
  - No P3 dos mundos das frutas, o julgamento da fruta (`JulgadorFruta`, #170) entra pela regra do mundo, **fora do orçamento**, como as
    informações do P2.
  - A regra do mundo passa a aceitar o elogio e a bronca do julgador, só eles. Eles são contados à parte, como as broncas do pedido.
  - O atencioso decide com o orçamento inteiro.
  - A receita do A está em `experiments/medir_k4_orcamento.py`.
  - No `run_v2_experimento_maior.py`, `K4_DONO_JULGA_FRUTA = True`.
  - O `sem_ensino` tira os julgamentos.
- **Canais** (#169):
  - a chave `"consequencia": {"canais_ligados": true}` na config;
  - os braços de ablação da K-7 nomeados na bancada (P1 com e sem canais, P1 com e sem memória, no descasado e no mutável), sem mudar
    os braços de antes.
- **Faixas:** 28101…28505 e 29101…29505 (comparação dos cérebros, C-8) entram em `FAIXAS_RESERVADAS`.
- **Não muda:** `engine.py`, `lobos.py`, `frutas.py`, a web.

## 2. Gates (só as sementes dos testes)

- Os braços de antes saem byte a byte (gabarito gravado antes da mudança); o P3 sem o julgamento é o P3 de hoje.
- No P3 com o K4:
  - o orçamento do dono fecha igual ao do P3 de hoje;
  - há um julgamento por consumo, pelo efeito vigente, dos dois lados da troca do mutável;
  - o `sem_ensino` tira os julgamentos e guarda as ofertas.
- G1 de toda vida e de todo acoplado novos.
- Uma fumaça não canônica com o P3+K4 e as ablações, sem artefato.

## 3. Entrega e o próximo passo

Um PR com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e do `REGISTRO_DESVIOS.md`. Merge só pelo Matheus.
**Depois do merge**, abra a tarefa seguinte, `docs/TAREFA_V2_CEREBRO_B.md`, numa worktree nova de `origin/main`.
