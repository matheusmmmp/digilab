# TAREFA V2 — BANCADA-MONTAGEM (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-bancada-montagem`. Status: ABERTA.
**Vem antes do cérebro B e é pré-requisito da run da calibração conjunta (K2, chat B): entregue rápido.**

## 1. Pergunta

O D levantou no #175 que a seção 1 do `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` liga peças diferentes em cada braço:
- memória nos braços P1 a P3;
- canais nos braços P1 e P2.

Mas na bancada as chaves pertencem ao braço, e só o `P1c` monta o P1 completo. **Decisão do Matheus (2026-10-05): opção 1.** A
config da bancada ganha `"montagem": "completa"`, que liga em cada braço o que a tabela da seção 1 manda. Os braços continuam se
chamando P0 a P3, com os mesmos nomes das predições.

## 2. Mudança mínima (só `experiments/`)

- `montagem` na config da bancada.
  - `"simples"` é o padrão e mantém o comportamento de hoje.
  - `"completa"` liga, por braço, as peças da tabela:

    | braço | memória | canais | `w0_info` | `w0_pedido` (só onde há pedido) |
    |---|---|---|---|---|
    | P0 | nada | nada | — | — |
    | P1 | `g` | ligados | — | sim |
    | P2, P2e, P2a | `g` | ligados | `w0_info` | sim |
    | P3 | `g` | desligados | — | sim |

  - Os valores (`g`, `w0_info`, `w0_pedido`) vêm da config, que é o que a K2 varre.
- **Ablações da K-7.** No modo completo, `P1c-mem` e `P1c-can` são o P1 completo menos uma peça, então ficam coerentes com a montagem.
  Escreva no PR como isso foi garantido.
- O orquestrador do experimento maior e o da calibração conjunta (B) usam `"montagem": "completa"` nas configs da K2 e da validação.
  - O B está com o orquestrador dele em `v2-k2-calibracao-conjunta`.
  - Diga no PR o nome exato da chave para ele.
- **Não muda:** `engine.py`, `lobos.py`, `frutas.py`, `cerebro_c.py` e a web.

## 3. Gates (só as sementes dos testes)

- Com `"montagem": "simples"` (ou sem a chave), as vidas saem as de hoje byte a byte, contra um gabarito gravado antes da mudança.
- No modo completo:
  - o P0 é o instinto byte a byte;
  - cada braço tem exatamente as chaves da tabela (conferido no estado interno);
  - o P3 não tem canais;
  - o `w0_info` só aparece nos braços P2.
- G1 de toda vida e de todo acoplado no modo completo.

## 4. Entrega

- Um PR com o relato no corpo e a suíte inteira.
- Uma seção no fim do `CLAUDE.md` e outra no fim do `REGISTRO_DESVIOS.md`.
- Merge só pelo Matheus.

Depois do merge, faça o `docs/TAREFA_V2_CEREBRO_B.md` numa worktree nova de `origin/main`.
