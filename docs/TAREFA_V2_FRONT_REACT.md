# TAREFA V2 — FRONT-REACT (2026-10-19)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-front-react`. Status: EM ANDAMENTO (etapa 1).

Categoria: arquitetura. Origem: Matheus, 2026-10-19: para a interface ficar igual ao protótipo da tela Pet, ele decidiu trocar o Preact
por React, com as bibliotecas de visual do protótipo (Tailwind, componentes no estilo shadcn, ícones lucide), mantendo o Vite e sem
Next.js (opção b).

## 1. Pergunta

O jogo web passa do Preact para o React (e depois ganha Tailwind, shadcn e lucide) sem mudar nada do que o jogo faz e, até a etapa 3, sem
mudar nada do que ele mostra? Não vem de uma hipótese da pesquisa: é infraestrutura do jogo (`web/app/`).

## 2. Depende de

- A decisão do Matheus de 2026-10-19 (opção b). Ela substitui, na parte da interface, a de 2026-09-28 (`docs/TAREFA_FRONT_TS.md`: Vite +
  TypeScript + Preact, sem Next.js). O front continua Vite + TypeScript; muda só a biblioteca das telas.
- Para a etapa 3: o ok do Matheus nas pranchas `PetPrototipo*` e `TelasLayoutDesktop` (branch `v2-tela-pet`).

## 3. Mudança mínima, em três etapas (um PR cada, cada um para no merge)

| etapa | o que muda | o gate |
|---|---|---|
| 1. Preact → React | a dependência (`preact`, `@preact/preset-vite` saem; `react`, `react-dom`, `@vitejs/plugin-react`, `@types/react`, `@types/react-dom` entram), o `tsconfig` (`jsxImportSource`), o `vite.config.ts`, o `main.tsx` (`createRoot`) e as telas: `class` → `className`, `for` → `htmlFor`, atributos SVG em camelCase, `onInput` → `onChange` nos campos controlados, os tipos (`ComponentChildren` → `ReactNode`). Nada de visual novo. | **o jogo sai igual** (abaixo) |
| 2. Tailwind + shadcn + lucide | as três bibliotecas configuradas (só os componentes do shadcn que as telas usarem), com os tokens `--dl-*` de hoje mapeados no tema do Tailwind; nenhuma tela muda de visual | o mesmo gate |
| 3. A tela Pet do protótipo | a tela Pet copiada 1:1 do protótipo (o visual dele vence o `UI_GUIDELINES`, desvio anotado no §8.1; os itens sem dado no motor somem; o habitat continua o de hoje, que vai virar o mundo 3D); a coluna da direita se recolhe e o habitat e as ações crescem | as capturas lado a lado com o protótipo e o ok do Matheus antes do merge |

**O que não muda, em nenhuma etapa:** o motor (`web/app/motor/`, sem DOM), o save e a chave dele, o replay, a paridade com o Python e os
gabaritos, as assinaturas, as versões de pet, o POC 3D (`web/app/poc/`) e o servidor local. Nenhum arquivo de `motor/` entra no diff.

**Dependências:** todas com versão exata (sem `^` nem `~`), escolhidas entre as versões estáveis há semanas; cada uma justificada no PR.

## 4. O gate "o jogo sai igual" (etapas 1 e 2)

- `npm run tipos`, `npm test` (Vitest: paridade, motor e telas), `npm run build` e `npm run e2e` (o e2e do jogo) passam como na `main`.
- **Capturas antes/depois, pixel a pixel** (`npm run capturas`, `e2e_capturas/telas.spec.ts`): as 13 abas, as Configurações e o Pet de um
  pet v11, em 390 e 1280 px (30 capturas). A referência sai do build de antes da mudança (`npm run capturas -- --update-snapshots`) e fica
  fora do repositório, em `artifacts_v2_front_react/capturas/`; o build de depois compara com ela, com o relógio da página falso e
  pausado (`page.clock`), para o tempo do jogo não andar entre uma captura e outra.
- Tolerância: 4 pixels por captura, o ruído medido entre duas rodadas do mesmo build (2 pixels no Pet de 390, na borda do balão da fala).
  Qualquer diferença acima disso é listada no PR, com a captura do diff.

## 5. Entrega

- Etapa 1: este documento (primeiro commit) e a migração no mesmo PR; o relato no corpo do PR e na seção 9 deste documento.
- `docs/TAREFA_FRONT_TS.md` (a decisão de 2026-09-28) e `docs/MAPA_REPOSITORIO.md` ganham a nota da troca para React.
- Aviso ao coordenador pelo corpo do PR. Merge só pelo Matheus.

## 6. Fora desta tarefa

O Next.js (descartado de novo). Qualquer mudança de regra de jogo. As outras telas no layout novo (a prancha `TelasLayoutDesktop` é
proposta; vira tarefa própria depois do ok). O celular das outras telas.

## 7. Critérios de aceitação

- Etapa 1: `package.json` sem `preact`; `npm run tipos`, `npm test`, `npm run build`, `npm run e2e` e `npm run capturas` passam; o diff não
  toca `web/app/motor/`.
- Etapa 2: o mesmo, com Tailwind, shadcn e lucide instalados e um componente de exemplo usado sem mudar captura nenhuma.
- Etapa 3: as capturas da tela Pet lado a lado com o protótipo e o ok do Matheus.

## 8. Precisa do Matheus

- Etapa 3: as decisões abertas das pranchas (DigiBrain no desktop, a higiene como quinta barra, a ordem no celular, os subtítulos em japonês
  da prancha-mapa). Recomendações no relato das pranchas.
