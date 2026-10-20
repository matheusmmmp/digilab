# TAREFA V2 — FRONT-REACT (2026-10-19)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-front-react` (etapa 1), `v2-front-tailwind` (etapa 2). Status: etapa 1 mergeada (#368);
ENTREGUE a etapa 2 (PR, espera o merge); etapa 3 depois.

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

## 10. Etapa 2 entregue (2026-10-19): Tailwind, shadcn e lucide, sem mudar o visual

**Dependências**, todas com versão exata:

| pacote | versão | publicada | por quê |
|---|---|---|---|
| `tailwindcss` (dev) | 4.3.3 | 2026-07-16 | a do protótipo (^4.3.3); última da linha 4.3, três meses sem versão nova |
| `@tailwindcss/vite` (dev) | 4.3.3 | 2026-07-16 | o plugin do Tailwind para o Vite (o protótipo usa o do PostCSS, por causa do Next); aceita o Vite ^8 |
| `class-variance-authority` | 0.7.1 | 2024-11-26 | as variantes dos componentes do shadcn (`cva`); a do protótipo |
| `clsx` | 2.1.1 | 2024-04-23 | o `cn()` do shadcn; a do protótipo |
| `tailwind-merge` | 3.7.0 | 2026-09-12 | o `cn()` resolve conflito de classe; a linha 3 é a do Tailwind 4 (o protótipo pede ^3.3.1) |
| `lucide-react` | 1.48.0 | 2026-09-24 | os ícones do protótipo. Sai versão quase todo dia; esta tem mais de três semanas. O protótipo pede ^1.16.0 |

O `@base-ui/react` do protótipo não entra. Na tela Pet, o protótipo só o usa no menu de mover módulo e nos popovers de Inventário e
Mais, que somem com os itens sem dado.

**O que entrou.**
- **`src/estilo/tailwind.css`**, carregado por último no `main.tsx`:
  - só o tema e as utilidades do Tailwind, **sem o preflight** (o reset dele mudaria todas as telas);
  - as utilidades saem só das pastas listadas em `@source`. Por enquanto é só `src/componentes/ui`, e nunca o resto de `src/`: um
    `className` do jogo com nome de utilidade não ganha CSS;
  - o tema traz os tokens `--dl-*` e `--ui-*` como cores (`bg-dl-surface`, `text-ui-text`...), fontes (`font-dl-num`...), cantos
    (`rounded-ui`) e sombra (`shadow-ui`);
  - traz também os nomes semânticos do shadcn (`primary`, `muted-foreground`, `border`...) nos tokens `--ui-*`.
- **shadcn:** o `components.json` (alias `@/` = `src/`, no `vite.config.ts` e no `tsconfig.app.json`), o `cn()` em `src/lib/utils.ts` e
  o `Button` em `src/componentes/ui/button.tsx`. É o do shadcn com duas mudanças:
  - um `<button>` de verdade, sem o primitivo do base-ui;
  - o alvo de toque de 44 px do guia em todos os tamanhos.

  Nenhuma tela usa o Button ainda; ele entra na etapa 3.
- **lucide-react:** instalado. Nenhuma tela usa ainda, e o bundle não muda: o build só leva o ícone importado.
- **`test/ui_shadcn.test.ts`:** confere o `cn()`, o Button (variantes, alvo de 44 px, `className` de fora) e um ícone do lucide, por
  `renderToStaticMarkup`.
- **Capturas:** passam a ter uma nova tentativa (`retries: 1`). O mesmo build, sem mudança nenhuma, variou 7 pixels uma vez em cerca de
  25 rodadas (o Pet v11 de 390); uma diferença de verdade se repete na nova tentativa.

**O gate.** Referência: o build da `main` em `e762425` (React), em `artifacts_v2_front_tailwind/capturas/`.

| conferência | resultado |
|---|---|
| `npm run tipos` | passa |
| `npm test` (Vitest) | 43 arquivos, 507 testes (os 503 de antes e os 4 novos), todos passam |
| `npm run e2e` (o jogo) | 70 de 70 |
| `npm run capturas` (30 telas, zero pixel) | 30 de 30, em 5 rodadas: **o visual não mudou** |
| `npm run poc:build` | passa |
| CSS do app | 180,8 KB (32,3 KB gzip) → 187,2 KB (33,6 KB gzip): +1,3 KB gzip, o tema e as utilidades do Button |
| JS do app | 765,9 KB (237,8 KB gzip), igual ao da etapa 1 |

**Para a etapa 3.**
- Toda tela que passar a Tailwind entra no `@source` do `tailwind.css`.
- As utilidades ficam numa camada (`@layer utilities`), e o CSS do jogo, fora de camada, ganha delas. Uma tela em Tailwind não pode
  depender de uma regra global do jogo que pegue os mesmos elementos (`button`, `h2`...), ou precisa sobrepô-la.
