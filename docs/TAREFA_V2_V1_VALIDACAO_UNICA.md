# TAREFA V2 — V1-VALIDACAO-UNICA (2026-10-06)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B. Worktree e branch: `v2-v1-validacao`. Status: ABERTA.
Etapa V1 do `docs/ROADMAP_V2.md`.
- Planos: `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, com o adendo 1 (ablações) e o adendo 2 (opção A: N = 30, K = 6 por base, Δ do
  P3 = 17,5 consumos).
- Ponto do cérebro A: o da K2 (`artifacts_v2_calibracao_conjunta/escolha.json`).

**Sementes de validação: 15101…15505, uma vez.**

## 1. Duas partes

1. **Agora:** a config da validação, com:
   - `"montagem": "completa"` e o K4 ligado;
   - o ponto da K2;
   - as unidades derivadas das bases de validação (K = 6, N = 30);
   - os blocos N6 e N7 e as ablações da K-7;
   - o Δ por primário do adendo 2.

   Confira o orquestrador do experimento maior contra o adendo 2 (o Δ do P3 em consumos e o poder simulado) e corrija o que faltar,
   **sem rodar** nas sementes de validação. Teste com fumaça nas sementes dos testes.
2. **A run, só com o sinal verde do coordenador.** Antes dela entram os adendos de `docs/PREDICOES_V2.md`, ainda em preparação, que
   podem pedir a medida em **pelo menos três durações de vida**. Se pedirem, o desenho das durações entra num adendo 3, com a estimativa
   de tempo dentro das 12 h (K-10), antes de rodar.

## 2. Regras

- Uma run só. Nada se ajusta olhando a validação.
- Toda vida é rejogada do disco bit a bit.
- O resultado, pela regra de decisão do plano, vai em `docs/RESULTADO_V2_VALIDACAO_UNICA.md`. Cada predição sai como confirma, refuta,
  inconclusivo ou inconclusivo por duração. As ablações e os blocos N6 e N7 vêm como secundários; G-MARCA e G-MARCA-E são declarados
  subpotenciados.
- Nenhuma alegação de novidade.

## 3. Entrega

Um PR (config, ajustes, run e resultado) com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e outra no fim do
`REGISTRO_DESVIOS.md`. Merge só pelo Matheus.
