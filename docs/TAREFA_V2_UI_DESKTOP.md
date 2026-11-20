# TAREFA V2 — UI-DESKTOP (2026-10-18)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: Matheus (pedido direto). Worker: chat "Digilab interface design". Worktree e branch: `v2-ui-desktop`. Status: ENTREGUE (PR desta etapa).

## 1. Pergunta

Frente de produto, sem hipótese de pesquisa: redesenhar o desktop do jogo web (≥ 1100 px) para a referência visual do Matheus de
2026-10-18. O visual fica claro, com pouco ornamento e com o habitat do pet no centro. Nenhuma regra de jogo, do motor ou do DigiBrain muda.

## 2. Depende de

- Decisões do Matheus de 2026-10-18:
  - o habitat continua o card hexagonal, só maior; nenhum asset novo;
  - o menu mantém os nomes atuais (Pet, Crescer, Lutar, Diário, Conversar, Ajustes), sem rotas inventadas;
  - escopo deste PR: a casca e a tela do Pet; o miolo das outras telas fica para um segundo PR.
- Nenhuma frente de código precisa estar na `main`. O porte do cérebro A (W-PORTE) mexe em `web/app/motor/` e `web/app/test/`, não nas telas.

## 3. Mudança mínima

- **Muda (só a partir de 1100 px):**
  - `web/app/src/estilo/tokens.css`: tokens `--ui-*` novos, com o tema escuro;
  - um CSS novo da casca desktop;
  - `componentes/Topo.tsx`: cabeçalho claro com marca, relógio do jogo, "salvo" e o Tamer;
  - `componentes/Nav.tsx`: barra lateral azul-marinho, ícone e rótulo em linha;
  - `telas/pet/TelaPet.tsx`: o habitat grande, a barra de ações embaixo, Estado atual e Atividades recentes à direita;
  - `telas/pet/PalcoPet.tsx`: só a geometria do palco grande.
- **Não muda:**
  - `web/app/motor/` e os gabaritos;
  - o save e as rotas;
  - o layout abaixo de 1100 px (celular e 900–1099 px);
  - os assets;
  - o miolo de Crescer, Lutar, Diário, Conversar e Ajustes;
  - `digilab/` e o Python.
- **`web/app/CLAUDE.md`** diz que a tela larga segue as pranchas `*Desktop`. A troca dessa regra vai **proposta** no corpo do PR, para o
  ok do Matheus. Este PR não edita o arquivo.

## 4. Experimento e gate (se houver run)

Não há run.

## 5. Entrega

- Testes em `web/app`: `npm run tipos`, `npm test`, `npm run e2e`. Capturas em 1920×1080, 1440×900 e 1366×768.
- Registro: seção no fim de `docs/registro/2026-10.md` e uma linha no índice `docs/REGISTRO_DESVIOS.md`.
- PR contra a `main` com o resumo. Merge só pelo Matheus.

## 6. Fora desta tarefa

- O miolo das outras telas (segundo PR).
- Explorar, Comunidade e Loja, que não existem no app.
- Notificações e perfil de usuário, que o app não tem.
- Um cenário de quarto.
- A versão mobile.

## 7. Resumo da etapa (2026-10-18)

**O que mudou (só a partir de 1100 px):**
- **Tokens:** `--ui-*` em `estilo/tokens.css`, nos dois temas.
  - O `#128CFF` do prompt passa só 3,4:1 com branco. Fica nas barras, bordas e no foco; onde há texto entra o `--ui-primary-forte`
    `#0968CB` (5,5:1).
  - O texto secundário é `#4F6488` (6,0:1).
- **Casca** (`estilo/desktop.css`, `componentes/Topo.tsx`):
  - o cabeçalho fixo de 64 px tem a marca, o relógio do jogo com o dia e o "salvo", e o mini-card do pet, que abre Meus pets;
  - a barra lateral azul-marinho de 208 px tem ícone e rótulo em linha, o ativo em azul e Conversar e Ajustes no pé;
  - o título e as abas viram uma linha no começo da página.
- **Tela do Pet** (`TelaPet.tsx`, `PalcoPet.tsx`, `estilo/desktop.css`):
  - o habitat é o maior bloco, com "agora: <o que ele faz>" por cima;
  - a barra das ações fica embaixo dele, com todas as ações de hoje;
  - a coluna da direita tem Estado atual (as barras reais) e Atividades recentes (as 5 últimas linhas do registro). Ela rola sozinha antes
    de o habitat encolher.
  - **Geometria do palco:** com um habitat de 400 px ou mais, os pés do pet ficam a 76 px do fundo. Num habitat de 468 px isso é a
    geometria da prancha.
- **Marcação:** as mudanças são neutras abaixo de 1100 px. O invólucro `lado-cards` vira `display:contents` e os itens novos são
  `desk-so`.

**O que não mudou:**
- o motor, o save, as rotas e os assets;
- o miolo de Crescer, Lutar, Diário, Conversar e Ajustes (só ganharam a casca);
- os nomes das classes que o e2e usa (`.dl-nav`, `.nav-quad`, `.topo-retrato`, `.topo-pet`, `.acoes-pet`, `.dl-tag--estagio`).

**Conferências:**
- `npm run tipos`;
- `npm test`: 32 arquivos, 357 testes;
- `npm run e2e`: o resultado está no corpo do PR;
- capturas em 1920×1080, 1440×900 e 1366×768 (fora do repositório: têm o atlas);
- **o celular (390 px) e a faixa de 1000 px saíram idênticos pixel a pixel aos da `main`.**

**Fica para depois:**
- o miolo das outras telas no visual novo (segundo PR);
- o DigiBrain e o connectome na interface: `docs/futuro/digibrain_connectome_na_interface.md`, com as decisões DC-1 a DC-5;
- a troca da regra de layout do `web/app/CLAUDE.md`, que fica proposta no PR.
