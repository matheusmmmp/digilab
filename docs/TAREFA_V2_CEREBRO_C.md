# TAREFA V2 — CEREBRO-C (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-cerebro-c`. Status: ABERTA. Etapa C5 do
`docs/ROADMAP_V2.md`; contrato de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md` (C-1 a C-10, decididas).

## 1. O que construir

O cérebro C, no estilo Fly-like (`docs/research/digibrain/synthesis/brain_comparison.md`): circuitos especializados, canais de reforço
paralelos, plasticidade local, competição de comportamentos e memória dependente de estado. Fica num arquivo próprio,
`digilab/policies/cerebro_c.py` (nome PROPOSTO), só no Python e só com a biblioteca padrão. De preferência em inteiros, porque o critério 3
do M6 é o porte para a web.

- **O contrato comum** (seção 1 do plano):
  - a interface `Politica` e os ganchos da bancada;
  - as ações de `AcaoPet`, com a fruta como sub-decisão;
  - a mesma `Observacao` dos lobos;
  - o instinto como prior: com o aprendizado desligado, o C é o instinto byte a byte (C-1);
  - a sonda do aprendido: a mesma decisão com a parte aprendida zerada e o mesmo `u`;
  - replay bit a bit.
- **Capacidade** entre 0,9× e 1,1× os parâmetros aprendíveis do A (C-3), com a conta no PR.
- **Sinais:** as mesmas fontes da bancada (dono, consequência, informação). Memória e arbitragem próprias são permitidas, mas não
  obrigatórias (C-2).
- **Na bancada:** a bancada é do chat D, que estará nela nesta rodada. Entregue a fábrica do cérebro `cerebro_c` e combine a entrada com
  o D; se não der, a ligação fica para ele.

**Nada de calibração.** O **adendo de calibração** (no máximo 4 parâmetros livres, as grades e a regra de escolha; seção 1.4 do plano,
C-10) vai no PR, para o coordenador conferir antes de qualquer run. Sem sementes reservadas. `lobos.py` é do chat B: não mexa nele.

## 2. Gates

- G1.
- Aprendizado desligado = instinto byte a byte.
- Capacidade dentro da faixa.
- A sonda reproduz a decisão sem o aprendido.
- Um teste em que o C aprende algo simples com a consequência, com a conta ou a tendência conhecida.

Se ele não fechar por um dos cinco motivos da seção 7 do plano, entregue assim mesmo, com o motivo.

## 3. Entrega

Um PR com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e do `REGISTRO_DESVIOS.md`. Merge só pelo Matheus.
