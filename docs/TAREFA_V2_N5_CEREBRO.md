# TAREFA V2 — N5-CEREBRO (2026-10-04)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B (dono de `lobos.py`). Worktree e branch: `v2-n5-cerebro`.
Status: ABERTA.

## 1. Pergunta

O lobo de decisão passa a **perceber a informação do dono** sobre as frutas, como o plano do N5 define (`docs/PLANO_ANALISE_V2_N5.md`,
decisões N5-1 a N5-8, aprovadas em 2026-10-04).

## 2. Depende de

#140 (`Observacao.info_frutas`) e #141 (lobos que veem as frutas) na `main`.

## 3. Mudança mínima (só `lobos.py` e `config.py`)

- **Entrada `info`** no lobo de percepção, lida de `Observacao.info_frutas` (+1 bem, −1 mal, 0 sem informação vigente).
- **Só na sub-decisão de qual fruta comer** (N5-2), com **um peso compartilhado** entre as frutas (N5-3).
- **Confiança de partida `w0_info`** em `ConfigLobos` (N5-1): 0 reproduz o P1 de hoje byte a byte; a grade {S/4, S/2, 3S/4} é calibrada no N5
  (rodada 7), abaixo do teto.
- **O peso da informação só muda pela consequência** (o sinal do P1 com a E2), nunca pelo dono.
- **Não muda:** `engine.py`, `AcaoPet`, o bandit, a L0, a L1, o N3, os lobos sem informação (byte a byte), a web.

## 4. Gates (sem run de pesquisa; só as sementes dos testes)

G1 replay; `w0_info = 0` ou sem informação no registro = vida de hoje byte a byte; com informação e aprendizado desligado, a escolha da fruta
pende para o lado da informação na medida do `w0_info` (teste); o peso da informação muda com o sinal da consequência e não muda com ação
do dono (espião).

## 5. Entrega e depois

Um PR, com o relato no corpo. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
Merge só pelo Matheus. **Depois, na mesma rodada:** `docs/TAREFA_V2_REVISAO_APRENDIZ.md`, assim que a BANCADA-N5 (chat D) estiver na
`main`.
