# TAREFA V2 — BANCADA-FRUTAS (2026-10-04)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-frutas`. Status: ABERTA.

## 1. Pergunta

Infraestrutura: os mundos das frutas na bancada, para cumprir o contrato das condições do `#137` e o plano do experimento maior
(`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`).

## 2. Depende de

Frutas (#132) e bancada de mundos (#137) na `main`.

## 3. Mudança mínima (só em `experiments/bancada_v2.py` e `digilab/metrics.py`, se precisar de medida)

- **Mundos das frutas** pelo `MotorFrutas`, com as ofertas fora do orçamento (B2) e fora do sorteio do dono aleatório (B1):
  - **`casado`** = casado com frutas (E1): a fruta de maior preferência inata do pet tem o efeito bom; o mundo padrão continua como
    referência;
  - **`descasado`**: o efeito real contraria a preferência inata, com o efeito ruim no humor (F6);
  - **`mutavel`**: o efeito troca num tick, gravado no registro.
- **Unidades derivadas** (E3): as 5 sementes reservadas × k, com a regra de derivação escrita e testada.
- **Medidas da predição:** `taxa_fruta_ruim` por janela (início, final, depois da troca), na `metrics.py`.
- **Não muda:** `engine.py`, `lobos.py` (chat B), `ambiente.py` e `frutas.py` (chat A), a web.

## 4. Gates (sem run de pesquisa; só as sementes dos testes)

G1 replay de toda vida dos mundos novos; casado × descasado com as mesmas ofertas, diferindo só no sinal do efeito (teste); no mutável, a
troca aparece no registro e o replay a refaz; as unidades derivadas não colidem com nenhuma faixa reservada ou já usada.

## 5. Entrega

Um PR. `python -m pytest tests/ -q` inteiro. Seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`. Relato no corpo do PR.
Merge só pelo Matheus.

## 6. Fora desta tarefa

Os sinais P1/P2 (chat B), o evento de informação (chat A), a calibração do experimento maior.
