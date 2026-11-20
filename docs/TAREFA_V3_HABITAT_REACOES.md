# TAREFA V3 — HABITAT_REACOES (2026-11-11)

Coordenador e worker: sessão do Gerente da V3 (Claude Code, Opus 5.5). Worktree e branch: `v3-habitat-reacoes`. Status: PLANO APROVADO
(etapa 0, sem código; HR-1 a HR-8 DECIDIDAS em 2026-11-11).

Categoria: documentacao. Origem: Matheus, 2026-11-10: "depois a gente planeja o que a gente faz com o Digimon no habitat, por exemplo.
Quando você dá comida, a reação dele e tal". Liberado em 2026-11-11: "Pode começar no que ficou pendente ali".

## 1. Pergunta

O que o pet mostra e faz ouvir quando o dono cuida dele na ilha? Por exemplo, a comida, o carinho, o banho, o chamado e o sono. Nó do
produto: a experiência básica (`docs/PRODUTO_VISAO.md`, seção 3).

## 2. Depende de

- O SOM_UP na `main` (#781): os barramentos, `somEventos.ts` e o `mapa.json` versão 2.
- As decisões HR-1 a HR-8 do plano (`docs/PLANO_V3_HABITAT_REACOES.md`, seção 6), antes da HR1.

## 3. Mudança mínima

Esta etapa traz só o plano, `docs/PLANO_V3_HABITAT_REACOES.md`, e este arquivo. As etapas HR1 a HR5 mexem só na vista e no som do
`web/app/src`. O motor, o log, o save, o replay e a RNG do motor não mudam.

## 4. Experimento e gate

Não há run.

## 5. Entrega

O plano e o relato no corpo do PR.

## 6. Fora desta tarefa

- O ambiente da ilha (S5).
- Os sons dos Bits e da loja (S6).
- A voz por espécie pelo genoma (S7), que fica como a HR5 e vira frente própria.

## 7. Critérios de aceitação

1. O plano tem uma linha por momento de cuidado, com a cara, o som do gesto e a voz.
2. Cada som citado tem a fonte: o arquivo do UP que está no disco, CC0 a baixar ou síntese.
3. As decisões HR-1 a HR-8 vêm com a recomendação e o custo de errar.

## 8. Precisa do Matheus

Nada: as HR-1 a HR-8 foram aprovadas em 2026-11-11 ("Aprovo as oito"), com a HR-5, baixar de 8 a 10 sons CC0 na HR4.

## 9. HR1 (2026-11-11): as reações que faltavam na vista

Branch `v3-habitat-hr1`. Só vista: um módulo novo, `web/app/src/telas/pet/momentos.ts`.

- **Os clipes que nada disparava:**
  - Feliz: ao nascer, ao atender o chamado, depois de comer bem, depois de tratar, no fim do pulinho do carinho e em laço ao brincar;
  - Sacudir: ao limpar;
  - Chamar: em laço com o chamado aberto;
  - Die: na morte.
- **Os instantes novos:** o acordar (Cansado), o chamado perdido (Triste), a fruta podre (Recusa) e o pet dormindo que vira de lado quando o
  dono tenta pegar.
- **Os ganchos:** `acoes.ts` (limpar, tratar), `ToquePet.tsx` (o carinho que relaxou), `PegarPet.tsx` (o pet dormindo), `reacao.ts`
  (os rostos com duração própria), `ilha/papel.ts` (o clipe no corpo) e `main.tsx` (`__digilab.clipeMomento` e `__digilab.momento`
  para o e2e).
- **Os testes:** `test/momentos.test.ts` (12) e o e2e "momentos: limpar faz o pet sacudir com o clipe do atlas" (`e2e/jogo.spec.ts`),
  que se pula sem o atlas de clipes.
- **Os desvios:** D-HR1-1 a D-HR1-7 (`docs/registro/2026-11.md`).

## 10. HR2 e HR3 (2026-11-11): o som do cuidado, a voz do pet e o bipe do chamado

Branch `v3-habitat-hr2`. Só apresentação.

- **Fora do git:** `Assets/gerar_sons_up.py` ganha 9 efeitos do Digimon UP; o `mapa.json` passa a 26 efeitos.
- **`web/app/src/somVoz.ts` (novo):** o tom da voz (humor × espécie × estágio) e a pausa de 4 s.
- **`web/app/src/som.ts`:**
  - `efeito` com taxa;
  - `voz(taxa)`;
  - `bipe(tipo)`, sintetizado;
  - o mapa sem os efeitos novos avisa e cala.
- **`web/app/src/somEventos.ts`:** os efeitos novos, `emitirVoz` e `emitirBipe`.
- **`web/app/src/somJogo.ts`:** a voz com o tom do pet de agora; o cuidado e a voz calam com o tempo rápido.
- **Os instantes:**
  - `telas/pet/momentos.ts`: o chamado, a casca, o sono, a fruta, a ação do motor, o começo do clipe e os gestos do dono;
  - `telas/pet/reacao.ts`: o tapa e a recusa da comida;
  - `telas/pet/ToquePet.tsx`: o medo da mão;
  - `telas/pet/ilha/papel.ts`: o chamado urgente.
- **Testes:** `test/som_hr2.test.ts` (9) e o e2e "som: limpar pede a agua e a voz do pet" (pulado sem os efeitos da HR2 em `Assets/sons`).
- **Desvios:** D-HR2-1 a 5 e D-HR3-1 (`docs/registro/2026-11.md`).

