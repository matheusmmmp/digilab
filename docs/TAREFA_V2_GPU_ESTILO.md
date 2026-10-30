# TAREFA V2 — GPU-ESTILO (2026-10-01)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: o mesmo da F0-CORPUS (chat D). Worktree e branch: `v2-gpu-estilo`.
Status: ABERTA (começa só com o PR #107, corpus em português, na `main`). **Fila da GPU: posição 1** (única frente com Ollama nesta rodada).

## 1. Pergunta

Com o corpus reescrito em português (PR #107), o estilo da espécie volta a funcionar no gemma2:9b sem japonês e sem saída rejeitada, e o comando pelo chat
continua no gate com o estilo ligado? Fecha os itens da fase 0 "corpus" e "rodada do comando com o estilo".

## 2. Depende de

PR #107 na `main`. Ollama local com `gemma2:9b` e nenhum outro modelo carregado (RTX 2060, um modelo por vez).

## 3. Mudança mínima

- **Medida do estilo:** `experiments/medir_estilo_latino.py` de novo, sobre o corpus novo, gravando numa pasta **nova** (`artifacts_voz/estilo_portugues/`);
  `artifacts_voz/estilo_latino/` não é refeito (mede o corpus de antes).
- **Comando com estilo:** rodada 4 em `digilab_fala_livre/avaliacao.py` (`RODADAS_COMANDO[4]`): prompt `livre-v8`, **com** o estilo da espécie, as mesmas 60
  mensagens, **sementes novas** reservadas pelo coordenador: **20261501, 20261601, 20261701** (nenhuma semente + i cruza as rodadas 1–3; teste). As
  rodadas 1–3 não mudam.
- Nenhuma mudança no prompt, no verificador, no corpus ou no servidor.

## 4. Experimento e gate

- Plano curto `docs/PLANO_ANALISE_V2_GPU_ESTILO.md` commitado antes da run.
- Métricas: saídas rejeitadas pelo parser (com o estilo); letras não latinas na fala; no comando, o gate PROPOSTO de sempre (falsos positivos ≤ 5% nas
  negativas; imperativos ≥ 80%), comparado com a rodada 3 (sem estilo).
- Nenhum número sem artefato; nada de ajustar olhando a mesma amostra.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`.
- Registro: seção no fim do `CLAUDE.md` (fala livre) e do `docs/REGISTRO_DESVIOS.md`.
- PR contra a `main` com os números e os artefatos. Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Mudar prompt ou corpus para passar no gate; avaliação cega (é do Matheus); outras espécies.
