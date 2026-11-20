# TAREFA V2 — N5-ACOPLADO (2026-10-04)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-n5-acoplado`. Status: ABERTA.

## 1. Pergunta

Duas peças pequenas que o N5 e o G4 precisam: o **modo acoplado** do informante (braço P2a) e o **motivo** das regras novas dos lobos.

## 2. Depende de

#140 e #141 na `main`.

## 3. Mudança mínima

- **`DonoInformante` modo `acoplado`** (decisão N5-4): o mesmo multiconjunto (fruta, conteúdo) do P2, com conteúdo **verdadeiro**, em ticks
  sorteados por uma **rng própria** (derivada da semente, separada das outras). Só em `frutas.py`/`ambiente.py` (são seus).
- **Motivo das regras novas** (`digilab/motivo.py`, `digilab/expressao.py`): `motivo_lobos` passa a citar `bola_no_cenario`,
  `fruta_no_cenario` e a escolha da fruta, com a regra de honestidade de hoje (só vira fator o que mudou a escolha); textos com marcador único
  e cobertura verificada na carga, como os de hoje. Sem tocar em `lobos.py` (o motivo lê o `estado_interno`).
- **Não muda:** `engine.py`, `lobos.py`, a bancada (chat D), a web.

## 4. Gates (sem run de pesquisa)

G1; os modos `certo` e `errado` de hoje byte a byte; o acoplado tem o mesmo multiconjunto do P2 com conteúdo verdadeiro e ticks diferentes
(teste); a rng do acoplado não mexe nas outras; a cobertura dos textos de motivo passa na carga.

## 5. Entrega

Um PR, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
Merge só pelo Matheus.
