# TAREFA V2 — FRUTA-NO-CENARIO (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Decisão R2 de `docs/RESULTADO_V2_REVISAO_APRENDIZ.md` (aprovada em 2026-10-05).
Duas partes, uma por dono de arquivo: **A primeiro** (o mundo), **B depois** (o cérebro).

## 1. Pergunta

A decisão de **comer ou não** passa a saber **qual** fruta está no cenário. Hoje a percepção recebe um número só (`Observacao.fruta`, o
maior incentivo entre as frutas presentes), e o pet aprende qual fruta evitar, mas come a ruim quando ela está sozinha (55% dos consumos do
P1 no descasado). Sem isso, G-EF, G-PIORA e G-REC do N5 ficam fracos por construção.

## 2. Parte A — o mundo (chat A; branch `v2-fruta-no-cenario-mundo`; só `frutas.py`, `policy.py` no campo novo)

- Campo novo `Observacao.frutas_cenario`: a presença de cada fruta (na ordem de `events.FRUTAS`), com padrão vazio/zero, injetado só pelo
  `MotorFrutas`, como `fruta` e `info_frutas`.
- `Observacao.fruta` continua igual (o instinto e os lobos de hoje leem esse).
- Gates: G1; G2 (o campo novo não muda nenhuma vida de hoje, byte a byte); teste da presença certa a cada decisão.

## 3. Parte B — o cérebro (chat B; branch `v2-comer-ve-fruta`; só `lobos.py`, `config.py`)

- A regra `fruta_no_cenario` passa a ter uma entrada por fruta presente na decisão de **comer**, com pesos iniciados de modo que o
  aprendizado desligado dê o instinto das frutas byte a byte.
- Esses pesos aprendem só pela consequência (o P1 com a E2), como a escolha da fruta.
- **A informação do dono continua só na escolha de qual fruta** (N5-2): ela não entra na decisão de comer.
- Gates: G1; G2 (aprendizado desligado = instinto das frutas, byte a byte; sem frutas = lobos de hoje); um teste em que o P1, com uma fruta ruim
  sozinha no cenário, aprende a não comer.
- **Depois, na mesma rodada:** a calibração e a validação do N5 (`docs/PLANO_ANALISE_V2_N5.md`, 12101…12505 / 13101…13505), no ponto **T3
  (teto 16·S)** da revisão (R1). Plano do N5 como está, com um adendo antes da calibração dizendo o ponto e a mudança da R2.

## 4. Entrega

Um PR por parte, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
Merge só pelo Matheus.
