# TAREFA V2 — W-PLANO-PORTE: o plano do porte do cérebro A para a web, pets v11 (2026-10-07)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-w-plano-porte`. Status: ABERTA. **Só
papel: nenhum código.** Etapa W do `docs/ROADMAP_V2.md`.

**A decisão de partida (M6, 2026-10-07):** o DigiBrain da web é o **cérebro A**, os lobos. Pela regra registrada a escolha seria o C. O A
foi escolhido por evidência descritiva posterior (`docs/DESCRITIVO_V2_PLATO.md`): ele aprende qual fruta evitar e resiste à informação
errada, e o C não; no braço do dono, o do produto, o C falha. Detalhe no `REGISTRO_DESVIOS`.

## 1. A pergunta

Como levar o cérebro A para o jogo web (`web/app/motor/`, hoje com o bandit da v1 em `bandit.ts`) sem quebrar nenhum pet existente?

O jogo web não tem o mundo das frutas nem a bola da pesquisa. O cérebro A montado na validação usa:
- a sub-decisão da fruta;
- a memória de episódios (N6);
- o pedido (N7);
- a informação (N5);
- o K4.

## 2. Entrega: `docs/PLANO_PORTE_V2_WEB.md`

1. **O que entra nos pets v11 agora:**
   - o núcleo dos lobos (L0), o aprendizado da L1 pelo dono e a consequência homeostática (P1);
   - tudo em inteiros, no ponto da K2 (teto 16·S, ganho 4).
   Diga para cada peça se ela tem sentido no mundo do jogo de hoje.
2. **O que espera** e de que depende: as frutas, a bola, a memória, o pedido, a informação e os canais (que na validação não mudaram nada).
   Isso inclui decidir se o mundo das frutas vai para o jogo (decisão do Matheus, com o custo).
3. **Paridade Python ↔ TypeScript:**
   - os gabaritos gerados pelo Python, que já é a referência;
   - os gates, no estilo do vínculo B e do V21E: decisões e pesos iguais, e o replay bit a bit no mesmo runtime;
   - o cuidado com `Math` × inteiros.
4. **Versão do pet:** **v11 = v10 + o DigiBrain A.**
   - Os pets v1 a v10 e as assinaturas deles não mudam.
   - Diga como a tela mostra o motivo, a partir do `motivo_lobos`, com a regra de honestidade.
5. **A fala e a voz:** o que muda no motivo que a LLM lê.
6. **A ordem das tarefas de código, com o dono de cada uma:**
   - o motor (chat A);
   - os gabaritos Python (chat B);
   - a tela (chat A ou D).
   Para cada tarefa, os gates.
7. **Riscos** e, no fim, as **decisões do Matheus**, com recomendação e custo de errar.

## 3. Regras

- **Leia antes:**
  - `CLAUDE.md`, as seções da web, do vínculo B (pets v10) e da V2;
  - `docs/TAREFA_FRONT_TS.md`;
  - `docs/RESULTADO_V2_VALIDACAO_UNICA.md`;
  - `docs/DESCRITIVO_V2_PLATO.md`.
- A memória "sempre aplicar na web" vale: o que for para o produto tem paridade.
- **Gargalo conhecido, que não se resolve aqui:** a decisão de comer não aprende o efeito de uma fruta quando ela está sozinha
  (`docs/DESCRITIVO_V2_PLATO.md`). Registre como limite.
- Merge só pelo Matheus.
