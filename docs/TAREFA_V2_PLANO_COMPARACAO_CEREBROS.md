# TAREFA V2 — PLANO-COMPARACAO-CEREBROS (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat C. Worktree e branch: `v2-plano-comparacao-cerebros`.
Status: ABERTA. Etapa K3/V2 do `docs/ROADMAP_V2.md` (revisão 3). **Só papel: nenhuma run, nenhum código.**

## 1. Pergunta

Como comparar os cérebros A (lobos, C3-like), B (CfC/A2C) e C (Fly-like) de `docs/research/digibrain/synthesis/brain_comparison.md` de
modo justo, antes de qualquer um dos dois novos existir? Cada um calibrado com **o mesmo orçamento** e depois uma validação única.

## 2. Entrega

**`docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`:**
- o contrato comum (a interface `Politica`, o que cada cérebro vê, o mesmo mundo, os mesmos braços P0–P3 e as mesmas condições da
  bancada; o que é "mesma capacidade" e "mesmo orçamento de calibração": vidas, pontos de grade, tempo de máquina);
- o critério de escolha do DigiBrain da web (M6): desempenho na pergunta maior, legibilidade (fração decidida pelo aprendido, motivo
  honesto), custo de porte para o TypeScript, determinismo inteiro; a ordem de prioridade e o que acontece num empate;
- as medidas e os contrastes (sem Holm novo para as predições do experimento maior: a comparação é família própria);
- as sementes (faixas novas, fora de `FAIXAS_RESERVADAS` e das faixas do roadmap, seção 6) e o adendo de tamanho de amostra;
- o que conta como "o cérebro B/C não fecha" (não aprende, não é determinístico, não cabe no orçamento);
- no fim, as decisões do Matheus com recomendação e custo de errar.

## 3. Regras

Referências só VERIFICADAS (a skill de literatura do projeto); Creatures, FlyWire e DF como pista; nenhuma alegação de novidade; números só
com artefato; sem sementes de validação.
