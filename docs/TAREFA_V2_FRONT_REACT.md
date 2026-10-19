# TAREFA V2 — FRONT-REACT (2026-10-19)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-front-react`. Status: ENTREGUE a etapa 1 (PR, espera o merge); etapas 2 e 3 depois.

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
- Tolerância: zero pixel, sem nova tentativa. Antes de capturar, o teste espera as fontes e a decodificação de todas as imagens e refaz
  o layout e a pintura da página inteira; sem isso, o texto de um select e dois ícones pequenos saíam ora de um jeito, ora de outro, com o
  mesmo HTML (até 320 pixels). Qualquer diferença é listada no PR, com a captura do diff.

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

## 9. Etapa 1 entregue (2026-10-19): Preact → React

**O que mudou.**
- **Dependências**, todas com versão exata:
  - saíram `preact` 10.29.8 e `@preact/preset-vite` 2.10.6, e com eles 69 pacotes do Babel;
  - entraram `react` e `react-dom` 19.3.0 (de 2026-09-09; a 19.3.1, de 2026-10-14, tem só 5 dias), `@types/react` e `@types/react-dom`
    19.3.0 (de 2026-09-09) e `@vitejs/plugin-react` 6.1.1 (de 2026-08-28; a 6.1.2 tem duas semanas).
- **As telas** (56 arquivos de `src/`), numa troca mecânica:
  - `class` → `className` (1.399), `for` → `htmlFor` (3), atributos SVG em camelCase (25) e `autocomplete` → `autoComplete`;
  - `onInput` → `onChange` nos três campos de texto e número (no React, o `onChange` é o evento de cada tecla);
  - os imports de `preact/hooks` → `react`, `ComponentChildren` → `ReactNode`, `render` → `createRoot`.
- **À mão:**
  - `src/css-variaveis.d.ts`: as variáveis CSS (`--x`) no `style`, que o React não tipa;
  - `FormEvent` no envio da conversa;
  - o foco ao abrir um modal: o Preact escrevia o atributo `autofocus` e o `showModal()` focava o botão; o React não escreve o atributo.
    Os dois botões passaram a `data-autofocus`, e o `abrirModal` (`src/componentes/modal.ts`) foca o marcado.
- **O que não foi tocado:** nada em `web/app/motor/` (o diff contra a `main` é vazio), o save, o replay, a paridade, o POC 3D (o
  `npm run poc:build` passa) e o servidor.

**O gate.** Rodado no build React e, para comparar, no build Preact do commit anterior à migração (uma worktree separada).

| conferência | Preact (antes) | React (depois) |
|---|---|---|
| `npm run tipos` | passa | passa |
| `npm test` (Vitest) | — | 42 arquivos, 503 testes, todos passam |
| `npm run e2e` (o jogo) | 70 de 70 | 70 de 70 (antes do conserto do foco: 67, as 3 falhas eram o foco do Resultado da luta) |
| `npm run capturas` (30 telas, zero pixel) | 30 de 30, em 3 rodadas | 30 de 30, em 5 rodadas: **o jogo sai igual, pixel a pixel** |
| bundle do app (`web/dist/assets/*.js`) | 532 KB (171 KB gzip) | 766 KB (235 KB gzip): +64 KB gzip, o custo do React DOM |

As referências das capturas ficam fora do repositório, em `artifacts_v2_front_react/capturas/` (30 PNG); `npm run capturas --
--update-snapshots` as refaz a partir do build de antes de qualquer mudança.
