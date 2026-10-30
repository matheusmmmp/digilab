# TAREFA V3 — COMBATE_V14: ligar a v14 no jogo, a B2 (2026-10-30)

Coordenador: Gerente da V3 (Claude Code). Worker: a definir (Sonnet). Worktree e branch: `v3-combate-v14`. Status: ABERTA.

Categoria: implementacao. Origem: Matheus, 2026-10-30, depois da conferência única da rodada 2 (#502): "Ligar a v14 já". A
recomendação do Gerente e do worker do combate era esperar uma rodada da alavanca de estrutura; o Matheus escolheu ligar agora, com
as 13 metas que passam (a B2 do `docs/PLANO_V3.md`, seção 4; a DE-1 do `docs/PLANO_EQUILIBRIO_COMBATE_TR.md`).

## 1. Pergunta

Sem hipótese de pesquisa: é uma tarefa de produto. **O jogo passa a nascer pets v14, com o combate em tempo real do candidato que a
conferência da rodada 2 mediu, sem mudar nenhuma vida v13 já jogada?**

## 2. Depende de

- A conferência R2-5 na `main` (#502): o candidato v14 é exatamente o que ela mediu (`docs/EQUILIBRIO_COMBATE_TR.md`, R2-5).
- A DE-1 (DECIDIDA): os números novos entram numa versão nova de pet, a v14, e a v13 não muda.
- A decisão CV14-1 (seção 8).

## 3. Mudança mínima

- **`VERSAO_PET` = 14** (`web/app/motor/constantes.ts`), uma versão por mecânica (`web/app/CLAUDE.md`).
- **O pet v14 usa o candidato inteiro, do jeito que a conferência mediu,** e nada além disso:
  - `RELOGIO_V14`, `FATORES_V14`, `APRENDIZADO_V14` e `LISTAS_LIDER_V14` (`web/app/motor/combate_tr/constantes_tr.ts`);
  - `LISTAS_V14` (`web/app/motor/bots.ts`);
  - a reserva fixa no fim (DE-10, `GambitsPet.reservaNoFim`) e o chip antes da regra que o cobre (DR2-1, `CHIP_ANTES_V14`);
  - as `CARTAS_V14` vazias (as cartas de hoje).
  A fonte da verdade é a configuração da conferência (`web/app/scripts/equilibrio_tr/` e o `r2_5/completo.tar.gz`). **Nenhum número
  novo.** Se o pet v14 no jogo não puder ser exatamente o candidato medido, pare e avise.
- **Os comentários** "ainda não é de nenhuma versão de pet" passam a dizer que é a v14.
- **Os testes:**
  - o gabarito das vidas v13 continua igual, byte a byte (nenhum gabarito v13 é regravado);
  - um teste novo confere que uma luta v14 do jogo dá o mesmo resultado que a bancada da conferência com a mesma semente e o mesmo par;
  - o replay de um pet v14 é bit a bit;
  - a paridade com o Python (`constantes.test.mjs`) passa sem mudança: o `GA` comum não muda (DR2-5).
- **A tela:** só o que o motor registra; os nomes Digimon; nenhum id interno. Se alguma tela mostrar a versão, ela mostra a v14.

**O que NÃO muda:** `digilab/engine.py` e todo o Python; as vidas, assinaturas e gabaritos v1 a v13; o combate por turnos; as telas da
luta (a B3 é outra missão); `App.tsx`, `tokens.css`, `pet.css` e `Nav.tsx` (arquivos disputados com a trilha L).

## 4. Experimento e gate

Não há run de pesquisa. A conferência já rodou uma vez (R2-5); nada se mede de novo para ajustar.

## 5. Entrega

- Testes: em `web/app`, `npm test`, `npm run tipos` e `npm run e2e` (no máximo 4 processos); `python -m pytest
  tests/test_gabarito_mvp_produto_web.py tests/test_gabarito_mundo_web.py -q` para conferir que os gabaritos do web não mudaram.
- As capturas (`e2e_capturas`) não são regeneradas aqui. Se a v14 mudar alguma captura, liste quais no PR: a regeneração fica com a
  T3, no fim da trilha L.
- O registro: uma seção no fim de `docs/registro/2026-10.md` e uma linha no fim de `docs/REGISTRO_DESVIOS.md`, com o mesmo título e LF.
- O resumo numa seção "Resultado" no fim deste documento e no corpo do PR. O Gerente põe a linha no `docs/PAINEL_V3.md`.
- Um PR contra a `main`, no modelo `.github/pull_request_template.md`, conferido com `python tools/verificar_relato.py`. O merge é só do
  Matheus.

## 6. Fora desta tarefa

- A rodada 3 (a alavanca de estrutura das formas de longe e do tita, a troca pelo resultado, a Cidadela, o Lago e a Espiral, o I-4, o
  chip no topo). Se ela vier, entra numa versão nova (v15), pela mesma regra.
- A B3 (a luta na pele dos menus).
- Descartar ou converter pets v13 (só com a CV14-1 dizendo isso).

## 7. Critérios de aceitação

- `VERSAO_PET` = 14, e um ovo novo nasce v14.
- O gabarito v13 passa sem regravar, e `git diff origin/main -- web/app/test/gabaritos/` não mostra nenhum gabarito v1 a v13 mudado.
- O teste "luta v14 do jogo = bancada da conferência" passa.
- `npm test`, `npm run tipos` e `npm run e2e` passam, com as contagens no PR.
- O registro e a seção "Resultado" estão no PR.

## 8. Decisões do Matheus

| # | decisão | estado |
|---|---|---|
| **B2** | ligar a v14 agora ou esperar a rodada 3 | **DECIDIDA, 2026-10-30: ligar já** ("Ligar a v14 já", no chat do Gerente da V3). A recomendação era esperar; o custo aceito é que as formas de longe e o tita fiquem fracos no jogo e que três líderes sigam desequilibrados (as 14 metas que falham na R2-5) |
| **CV14-1** | os pets v13 que já existem | **a recomendação, que vale até o Matheus dizer outra coisa: a v13 continua viva, com o ramo por versão no motor;** só os ovos novos nascem v14, e nenhum save é apagado. Custo de errar: o ramo por versão volta ao motor (o D-9 o tinha tirado); descartar a v13 apagaria pets do jogador, o que só vale com aviso na tela e decisão explícita |

## 9. Resultado (2026-10-30, worker Sonnet 5.5)

- **Feito:** `VERSAO_PET` = 14 e as regras `CV21E_TR14`. O ovo novo nasce v14; a v13 abre e joga como antes (CV14-1); a v12 ou mais antiga segue
  recusada. O pet v14 usa o candidato inteiro, sem número novo: `RELOGIO_V14` (pela versão, `relogioDe`), `FATORES_V14` (líderes, desafiantes,
  Liga, instalações, Salão, Fábrica), `LISTAS_V14` (pets e rivais de forma canônica), `LISTAS_LIDER_V14`, `APRENDIZADO_V14`, a reserva fixa no
  fim, o chip antes da regra que o cobre e as `CARTAS_V14` vazias. A Fábrica ganha as regras v14 (`v: 14`); as tentativas `v: 13` se refazem iguais.
- **Os testes:** `test/pet_v14.test.ts` confere que a luta v14 do jogo dá o mesmo resultado que a bancada da conferência (mesma semente, mesmo
  par) nos líderes, desafiantes, Liga, instalações, Salão e Fábrica, e que o replay do pet v14 é bit a bit. Os testes de vidas v13 passaram a
  pedir o 13 explicitamente (`new Motor(x, 13)`); nenhum gabarito foi regravado.
- **Fora do escopo, intocado:** o Python, `App.tsx`, `tokens.css`, `pet.css`, `Nav.tsx`, as telas da luta e as capturas (a regeneração fica com a T3).
- **Contagens:** no corpo do PR.
