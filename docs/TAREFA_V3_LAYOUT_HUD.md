# TAREFA V3 — LAYOUT_HUD (2026-10-30)

Coordenador: sessão que passou a prancha (Claude Code). Worker: Claude Code, Opus 5.5. Worktree e branch: `v3-layout-hud`. Status: ENTREGUE.

Categoria: implementacao. Origem: Matheus, 2026-10-30: a prancha visual da tela Pet (trilho, plaquinha, HUD à direita, chamado e barra
de ações), passada por outra sessão.

## 1. Pergunta

O menu e o HUD da tela Pet do jogo web chegam perto da prancha do Matheus sem mexer na cena, no motor nem no comportamento das ações? É
trilha L (layout) da V3; não vem de hipótese de pesquisa.

## 2. Depende de

- O PR #498 (os balões soltos sobre a cena), ainda aberto: este branch sai dele (decisão do Matheus, abaixo) e o PR tem base nele.
- A `main` com a T1 do tema (#486, a pele Holográfica), já mesclada aqui.

## 3. Mudança mínima

Só componentes e estilos do layout e do HUD:

- `web/app/src/telas/pet/TelaPet.tsx`: a pilha da direita (Estado, Evolução, Últimas ações), o cartão do chamado no alto ao centro, a
  etiqueta do DigiBrain e as necessidades em %;
- `web/app/src/componentes/Topo.tsx`: a marca e o ícone de salvo;
- `web/app/src/componentes/hx/MedidorHx.tsx`: a opção `porcento`;
- `web/app/src/estilo/pet_hud.css` (novo), `casca.css` (topo, trilho, avisos) e `pet_dock.css` (a barra de ações).

Não muda: o motor (`web/app/motor/`), a cena (`cena3d.ts`, `ilha/`, `CenarioPet.tsx`, `PalcoPet.tsx`), o pet, as animações, as ações e
o que elas fazem, as rotas e o hash, o save.

## 4. Experimento e gate (se houver run)

Não há run.

## 5. Entrega

- Em `web/app`: `npm run tipos`, `npm test` e `npm run e2e`.
- O desvio na seção do dia em `docs/registro/2026-10.md`, com a linha no índice `docs/REGISTRO_DESVIOS.md`.
- PR com base no `v3-layout-baloes` (#498), relato no modelo `.github/pull_request_template.md`. Merge só pelo Matheus.

## 6. Fora desta tarefa

- A idade do pet na plaquinha (a prancha mostra "3 dias"): o motor não guarda idade; o dia do jogo já está no relógio.
- O cenário de academia da prancha (é ilustração); a cena 3D fica como está.
- As outras telas (Crescer, Lutar, Diário, Conversar, Ajustes), que já têm a pele dos menus.
- As capturas de referência do portão (`e2e_capturas`): só depois da aprovação do Matheus.

## 7. Critérios de aceitação

- A partir de 900 px: Estado, Evolução e Últimas ações empilhados à direita, o Estado aberto por padrão, cada um recolhível, a escolha
  guardada no navegador (e2e "Pet (Home) … 1280 px").
- As cinco necessidades em % do motor (`Math.round(valor × 100)`), barras curtas, alerta abaixo de 50 % (e2e e `hx_pele.test.ts`).
- O chamado e o resumo num cartão escuro no alto ao centro, sem o nome do pet; nada cobre o centro do habitat a 1920×950 (e2e "monitor").
- O DigiBrain como etiqueta no canto inferior direito (desktop); no celular, os botões da borda continuam.
- `npm run tipos`, `npm test` e `npm run e2e` passando.

## 8. Precisa do Matheus

Decididas em 2026-10-30, todas pela recomendação:

| # | pergunta | decisão | custo de errar |
|---|---|---|---|
| HUD-1 | base do PR | empilhar sobre o #498 | rebase se o #498 mudar |
| HUD-2 | Estado, Evolução e Últimas ações no desktop | empilhados e visíveis à direita, cada um recolhível (muda a regra 3 da `TAREFA_V2_LAYOUT_HABITAT`) | a pilha cobre ~300 px da direita da cena em 1280 |
| HUD-3 | valores das necessidades | % do motor | mais fino que os 5 blocos de antes |
| HUD-4 | a faixa "nome · comida baixa · Detalhes" | cartão no alto ao centro, sem o nome | no celular disputa o topo (vai logo abaixo) |

Capturas aprovadas pelo Matheus em 2026-10-30 (16 imagens em `D:\Trab\digilab\capturas_hud_aprovar\`, fora do git); com elas, o `web/app/CLAUDE.md` passa a dizer que a plaquinha e o relógio estão no sistema dos menus.

## Entregue (2026-10-30)

- **Desktop (≥ 900 px):** trilho de 76 px com ícones de 20 px, rótulos curtos e o destino aberto chanfrado na cor do escolhido da pele,
  risca diagonal no alto e linha tracejada na borda; plaquinha e relógio em caixas escuras chanfradas; a marca com o risco duplo;
  pilha de 288 px (300 px a partir de 1600) à direita; cartão do chamado sob a marca; etiqueta do DigiBrain no canto inferior direito; a
  barra de ações com botões de 72 × 52 px, só a largura deles. O painel do DigiBrain e o do porquê abrem no lugar da pilha (não cobrem o
  pet).
- **Celular (< 900 px):** o cartão do chamado sob o topo, à esquerda dos botões da borda; os botões da borda (Estado, Evolução, Últimas
  ações, DigiBrain) abrem um painel por vez, como antes; a barra de ações com 4 + Mais.
- **Estado:** as cinco necessidades com ícone, barra curta e %; "Detalhes" abre a emoção, o mundo (v12), o desejo e a confiança de
  combate (antes sempre visíveis no painel).
- **Avisos fixos:** caixas escuras com a borda de perigo.
- **Desvio:** o retrato e o relógio deixam os tokens `--dl-*` e o tema claro/escuro (regra 7 e D3 da `TAREFA_V2_LAYOUT_HABITAT`) e passam
  ao sistema dos menus, como pede a prancha. O balão continua no `--dl-*`.

## Segunda rodada (2026-10-30)

Pedido do Matheus (pela sessão que coordena): três pontos, sem redesenhar a página.

- **Trilho:** deixa de ocupar a altura toda. Vira um bloco compacto de 76 px, flutuando 12 px da esquerda, logo abaixo da plaquinha e com
  a altura dos quatro destinos. Conversar e Ajustes ficam num segundo bloco logo abaixo. Os dois têm cantos chanfrados e a risca
  diagonal. Com isso `--casca-trilho` vale 0 também no desktop: o habitat, a tela Pet e o topo começam na borda esquerda, e o trilho
  flutua sobre a cena. A faixa do "Pôr ração" desvia do trilho.
- **Plaquinha do pet:** fica no canto superior esquerdo, a 12 px do topo e da esquerda, sem o recuo da largura do trilho.
- **Paleta (HUD-5, decisão do Matheus, pela recomendação):** carvão `#10191B`, contorno `#29474B`, ciano `#49D5E2` e ativo `#B9EFF0`.
  Ela vale no trilho, no topo e em toda a tela Pet, nas duas peles; as telas abertas (Crescer, Lutar…) seguem a pele escolhida. O custo
  de errar: na pele Holográfica, a tela Pet fica turquesa e as outras azuis. Os três painéis ganham o mesmo traço ciano no topo
  esquerdo e o marcador no canto inferior direito.
- **Balão da fala (pedido do Matheus, depois das capturas):** sai do branco com borda azul-marinho (`--dl-*`) e entra no padrão do HUD:
  caixa escura translúcida chanfrada, contorno e traço ciano, texto claro e "toque para ver o porquê" no secundário. A fala fria ou
  sombria troca o ciano pelo lilás. O toque continua abrindo o porquê.
- Capturas em `D:\Trab\digilab\capturas_hud_aprovar_r2\` (16, fora do git), aguardando a aprovação.
