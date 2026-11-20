# TAREFA V2 — CEREBRO-B (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D, depois da BANCADA-K4-CANAIS. Worktree e branch: `v2-cerebro-b`.
Status: ABERTA. Etapa C5 do `docs/ROADMAP_V2.md`; contrato de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md` (C-1 a C-10, decididas).

## 1. O que construir

O cérebro B (CfC + ator-crítico + elegibilidade; ponto flutuante permitido; `docs/research/digibrain/synthesis/brain_comparison.md`) num
arquivo próprio, `digilab/policies/cerebro_b.py` (nome PROPOSTO). Só no Python e só com a biblioteca padrão.

- **O contrato comum** (seção 1 do plano):
  - a interface `Politica` e os ganchos da bancada;
  - as ações de `AcaoPet`, com a fruta como sub-decisão;
  - a mesma `Observacao` dos lobos;
  - o instinto como prior: com o aprendizado desligado, o B é o instinto byte a byte (C-1);
  - a sonda do aprendido: a mesma decisão com a parte aprendida zerada e o mesmo `u`;
  - replay bit a bit no mesmo runtime.
- **Capacidade** entre 0,9× e 1,1× os parâmetros aprendíveis do A (C-3), com a conta no PR.
- **Sinais:** as mesmas fontes da bancada (dono, consequência, informação). Memória e pedido próprios não são obrigatórios (C-2).
- **Na bancada:** o cérebro `cerebro_b` em todos os braços que aprendem.

**Nada de calibração.** O **adendo de calibração** (no máximo 4 parâmetros livres, as grades e a regra de escolha; seção 1.4 do plano,
C-10) vai no PR, para o coordenador conferir antes de qualquer run. Sem sementes reservadas.

## 2. Gates

- G1.
- Aprendizado desligado = instinto byte a byte, e igual ao P0 dos lobos.
- Capacidade dentro da faixa.
- A sonda reproduz a decisão sem o aprendido.
- Um teste em que o B aprende algo simples com a consequência, com a conta ou a tendência conhecida.

Se ele não fechar por um dos cinco motivos da seção 7 do plano, entregue assim mesmo, com o motivo.

## 3. Entrega

Um PR com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e do `REGISTRO_DESVIOS.md`. Merge só pelo Matheus.
