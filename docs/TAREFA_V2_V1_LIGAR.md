# TAREFA V2 — V1-LIGAR: faixa nova, P2d e P3i ligados, e a run (2026-10-06)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B. Worktree e branch: `v2-v1-ligar`. Status: ABERTA. Continua o
#189. Adendo 4 de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`.

## 1. Agora

- **Faixa nova de validação: bases 30101, 30202, 30303, 30404 e 30505** (adendo 4.1).
  - Troque `BASES_EXPERIMENTO_MAIOR["validacao"]`, a config `experiments/configs/v2_experimento_maior/validacao.json` e os testes.
  - Em `FAIXAS_RESERVADAS`, a faixa 15101…15505 fica reservada como **queimada**, com a fonte, e a 30101…30505 entra.
  - Combine com o chat D se ele estiver mexendo na bancada ao mesmo tempo: o conflito é de poucas linhas.
- **A leitura do adendo 4.2 no `resumo.json`:**
  - o limiar como forma possível na leitura das durações, sem mudar a regra;
  - a trajetória do `w_info` do P2e;
  - valor e eficiência separados no mutável.
- **Testes:** só fumaça nas sementes dos testes.

## 2. Depois do PR da bancada do P2d e do P3i (chat D)

Atualize com a `main` e ligue os dois braços (`"p2d_p3i": true`). Confira na fumaça que o orquestrador não falha mais antes de gerar as
vidas.

## 3. A run

**Só com o sinal verde do coordenador**, que vem depois do merge deste PR. Uma vez, nas bases 30101…30505, numa worktree própria (cerca de
6,1 h pelo `artifacts_v2_v1_adendo3/custo.json`). Toda vida é rejogada do disco. O resultado vai em `docs/RESULTADO_V2_VALIDACAO_UNICA.md`.

## 4. Entrega

Um PR com a preparação; a run vai num PR seguinte, com o relato no corpo. A suíte inteira roda, e há uma seção no fim do `CLAUDE.md` e
outra no fim do `REGISTRO_DESVIOS.md`. Merge só pelo Matheus.
