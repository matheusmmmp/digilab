# TAREFA V2 — BANCADA-EXPERIMENTO (2026-10-05)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-experimento`. Status: ABERTA.

## 1. Pergunta

Infraestrutura para o experimento maior rodar sem orquestrador improvisado (`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`).

## 2. Mudança mínima (só `experiments/` e `digilab/metrics.py`)

- **Faixas reservadas:** acrescentar 18101…18505 (revisão do aprendiz), 19101…19505 e 20101…20505 (N6) a `FAIXAS_RESERVADAS`.
- **Ponto do aprendiz:** a config da bancada aceita o ponto T3 (teto 16·S, R1) como padrão nomeado para o N5 e o experimento maior, sem
  mudar o padrão das runs antigas.
- **Orquestrador do experimento maior** (`experiments/run_v2_experimento_maior.py`, nome PROPOSTO): monta braços P0, P1, P2, P2e, P3 ×
  `casado_frutas`, `descasado`, `mutavel` pela bancada; calcula as medidas e os seis contrastes primários com Holm e a equivalência da
  predição 5 (seção 6 do plano); grava tabelas e um resumo por predição (confirmar, refutar, inconclusivo, inconclusivo por duração). **Sem
  run com faixa reservada:** só fumaça nas sementes dos testes.
- **Não muda:** `engine.py`, `lobos.py` (chat B), `frutas.py` (chat A), a web.

## 3. Gates

G1 de toda vida da fumaça; os contrastes e o Holm conferidos em dados sintéticos com resposta conhecida; a fumaça recusa sementes de
validação sem plano.

## 4. Entrega

Um PR, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
Merge só pelo Matheus.
