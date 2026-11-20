# TAREFA V2 — CALIBRACAO-CEREBROS-B-C (2026-10-06)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Rodada 11 do `docs/ROADMAP_V2.md`. Plano `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`:
C-1 a C-10 e o **adendo 1**, que traz as grades, as regras e os totais de vidas de cada cérebro, já conferidos pelo coordenador.

Cada cérebro é calibrado por quem o construiu:

| cérebro | worker | worktree e branch | adendo | artefato |
|---|---|---|---|---|
| B (CfC + ator-crítico) | chat D | `v2-calibracao-cerebro-b` | 1.1 | `artifacts_v2_comparacao_cerebros/calibracao_B/` |
| C (Fly-like) | chat A | `v2-calibracao-cerebro-c` | 1.2 | `artifacts_v2_comparacao_cerebros/calibracao_C/` |

## 1. O que fazer

- Um orquestrador pela bancada, com as grades e as regras **exatamente** como estão no adendo.
  - Sementes **28101…28505, K = 4**, prefixo `comparacao-cerebros`.
  - Atencioso, 14 dias. Nas peças comuns, o ponto do A da K2 (`artifacts_v2_calibracao_conjunta/escolha.json`): o ganho da consequência
    (4) e a montagem.
  - O cérebro entra pela receita do próprio PR: `experiments/cerebro_b_bancada.py` e `experiments/cerebro_c_bancada.py`.
- **Teto de vidas:** 1260, as que o A gastou na K2. Se a grade passar disso, pare e escreva um adendo antes.
- **Teto de tempo:** 4× o da K2 do A.
- **Rode uma vez.** Toda vida é rejogada do disco bit a bit.
- **Piloto no ponto escolhido:** confira o critério "não aprende" da seção 7: deriva nula, ou o aprendido mudando menos de 1% das
  escolhas. Se o cérebro não fechar, registre o motivo; ele sai do M6, e a entrega acontece assim mesmo.
- Resultado em `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_<B|C>.md`, com o ponto escolhido e se fechou.

## 2. Regras

- Nenhuma regra usa contraste entre braços nem entre cérebros, nem a `taxa_fruta_ruim`.
- Não tocar nas sementes de validação da comparação (29101…29505) nem nas do experimento maior.
- Só a bancada e os arquivos do próprio cérebro. `lobos.py` é do chat B.

## 3. Entrega

Um PR por cérebro, com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e outra no fim do `REGISTRO_DESVIOS.md`.
Merge só pelo Matheus.
