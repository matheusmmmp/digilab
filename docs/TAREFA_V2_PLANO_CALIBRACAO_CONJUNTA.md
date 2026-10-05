# TAREFA V2 — PLANO-CALIBRACAO-CONJUNTA (2026-10-05)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat C. Worktree e branch: `v2-plano-calibracao-conjunta`.
Status: ABERTA. Etapa K1 do `docs/ROADMAP_V2.md` (revisão 3). **Só papel.**

## 1. Pergunta

Como calibrar **uma vez** o cérebro A montado (N5, N6, N7 e canais), nas sementes 14101…14505, para a validação única do experimento
maior com ablações (`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, adendo 1)?

## 2. Entrega

**`docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`:**
- os parâmetros livres (teto já no T3; ganho do P1; `w0_info`; `w0_pedido`; ganho da memória `g`; o que os canais pedirem), as grades
  e a **regra de escolha** registrada antes (sem olhar a validação);
- como evitar a explosão combinatória: ordem de varredura (por exemplo, parâmetros que não interagem varridos separados, e só os que
  disputam a mesma decisão juntos), com a justificativa;
- o **adendo de tamanho de amostra** (o N das unidades derivadas, E3) pela variância da calibração;
- os contrastes de ablação e onde cada um é medido;
- no fim, as decisões do Matheus, com recomendação e custo de errar.

## 3. Regras

Números só com artefato; nenhuma alegação de novidade; não usar sementes de validação.
