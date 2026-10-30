# Tarefa V2 — tema dos menus: peles Militar e Holográfico

Gerente: sessão "Gerente do layout habitat" (2026-10-30). Merge só do Matheus. Base: `origin/main` 19668ab9.
Lido sobre a pilha do layout ainda sem merge: M1 `v2-layout-xcom` (#460), M2 `v2-layout-casca` (#464), M3 `v2-layout-pet`
(#469), M4 `v2-layout-telas` (#470), M5 `v2-layout-config` (#467), M6 `v2-layout-auto` (#468). M3–M6 saem todas da M2, em
paralelo; os nomes de arquivo e de classe abaixo são os desses branches e podem mudar até o merge (a T1 confere de novo).

## 1. Referência

- As páginas de referência das duas peles são **privadas** e **nada delas entra no git** (têm sprites embutidos). A
  referência no repo é este texto, como no `docs/TAREFA_V2_LAYOUT_HABITAT.md`.
- A pele Militar é a pele XCOM que a frente do layout montou (§3.1 do `TAREFA_V2_LAYOUT_HABITAT.md`); este documento só
  muda o nome na tela e acrescenta a segunda pele e a escolha. Estrutura, rotas, telas e componentes do layout não mudam.
- Cores semânticas, sprites, textos e acessibilidade continuam no `docs/UI_GUIDELINES.md`.

## 2. Decisões do Matheus (2026-10-30)

| # | pergunta | decisão |
|---|---|---|
| TM1 | qual pele vem por padrão? | **Vidro** (Holográfico). Quem nunca escolheu vê o Holográfico |
| TM2 | nomes na tela | **"Militar"** (id `xcom`) e **"Holográfico"** (id `vidro`). A palavra "XCOM" não aparece na tela (fica só em id, classe e comentário) |
| TM3 | onde a pele vale | **só nos menus** (painéis, trilho/barra, dock, chamado, modais, telas que abrem sozinhas), **sempre escura**. Claro/escuro continua no habitat, balão, retrato e relógio. Pele e tema são **eixos independentes**: as 2 × 3 combinações valem |
| TM4 | onde se escolhe | **Ajustes › Aparência**, dois cartões de prévia no molde de `.cfg-tema` (depois da M5: `.mc-opcao--tema` + `.mc-tema-prev` em `menus_config.css`) |
| TM5 | capturas | **completas nas duas peles**, em 360, 390 e 1280 px |
| TM6 | ordem com o layout | a **M7** do layout roda antes, normal (só na pele Militar); a **T3** do tema captura de novo depois, nas duas |

## 3. Valores das duas peles

### 3.1 Descrição

**Militar** (já no código): painel `rgba(8,12,14,.93)`, borda `rgba(118,170,175,.45)` com linha de topo mais clara,
título Saira Condensed caixa alta com hachura diagonal, escolhido `#BFE5E7` com texto escuro, botão CONTINUE com borda
`#6CC58A`, sem brilho.

**Holográfico:**

- superfície `rgba(24,36,50,.84)` → `rgba(6,11,18,.92)`, `backdrop-filter: blur(10px)`;
- reflexo `linear-gradient(155deg, rgba(255,255,255,.06), rgba(255,255,255,.015) 34%, transparent 35%)`;
- sombra `0 8px 18px rgba(0,0,0,.4)`;
- contorno externo 1 px `rgba(178,192,206,.5)`; contorno interno 1 px `rgba(150,172,194,.2)` recuado 4 px;
- chanfros de 12 px (canto superior direito e inferior esquerdo);
- azul só em destaques: trecho de luz 96×2 px `#3AA8FF` com `box-shadow: 0 0 8px #3AA8FF` no topo esquerdo e marcador
  4×4 px no canto inferior direito;
- selecionado `linear-gradient(180deg, rgba(58,168,255,.28), rgba(58,168,255,.1))`, borda `#3AA8FF`, brilho leve, chanfro
  8 px, barra acesa de 3 px no trilho;
- botão principal `rgba(58,168,255,.2)` com borda `#3AA8FF`;
- títulos 13 px, 700, espaçamento 2 px, caixa alta; rótulos 10–11 px caixa alta `#8A9BAD`; corpo em Barlow;
  números e estados `#5FD4FF` em Rajdhani 700;
- barras de 5 px segmentadas com brilho, mantendo a cor de cada necessidade.

Habitat, pet, retrato, relógio e balão **iguais nas duas peles**.

### 3.2 Tokens `--hx-*`

Hoje (`tokens.css` da M1) os tokens ficam só em `:root` e são lidos por `hud.css`, `casca.css` (trilho, botões do topo),
`painel-hx.css`, `menus_config.css`, `pet_dock.css` e `abertas.css`. A T1 põe o Holográfico em `:root[data-pele="vidro"]`
e deixa o Militar em `:root` (a pele sem atributo é a Militar; o padrão Vidro vem do `pele.ts`, TM1).

"(proposta)" marca valor que a referência não fixa; a T1 propõe e confere o contraste, e o Matheus aprova nas capturas da T3.

| token | papel | Militar (atual) | Holográfico |
|---|---|---|---|
| `--hx-chao` | trilho/barra, fundo da página atrás do painel | `#0B1118` | `rgba(6,11,18,.92)` |
| `--hx-miolo` | fundo do painel (fim do gradiente), linhas | `#0A1316` | `rgba(6,11,18,.92)` |
| `--hx-miolo-2` | fundo do painel (início do gradiente), hover | `#16191E` | `rgba(24,36,50,.84)` |
| `--hx-borda` | borda fina | `rgba(118,170,175,.38)` | `rgba(178,192,206,.5)` (contorno externo) |
| `--hx-borda-topo` | linha de topo, borda de botão | `#5E7C80` | `rgba(178,192,206,.5)` (sem linha de topo; o destaque é o trecho de luz) |
| `--hx-texto` | texto do menu | `#D6E5E6` | `#D6E5E6` (proposta: mantém) |
| `--hx-texto-2` | texto secundário forte, abas | `#BFD6D8` | `#BFD6D8` (proposta: mantém) |
| `--hx-sec` | apoio | `#8EA9AB` | `#8A9BAD` |
| `--hx-rotulo` | rótulo pequeno caixa alta | `#7FE3FF` | `#8A9BAD` |
| `--hx-escolhido` | fundo do item escolhido | `#BFE5E7` | `linear-gradient(180deg, rgba(58,168,255,.28), rgba(58,168,255,.1))` |
| `--hx-escolhido-ink` | texto do escolhido | `#0A1316` | `var(--hx-texto)` (proposta: texto claro sobre o azul translúcido) |
| `--hx-hachura` | faixa do título | `repeating-linear-gradient(-60deg, rgba(150,195,200,.38) 0 4px, transparent 4px 9px)` | `none` |
| `--hx-hachura-verde` | faixa do botão principal | `repeating-linear-gradient(-60deg, rgba(108,197,138,.55) 0 4px, transparent 4px 9px)` | `none` |
| `--hx-btn-bg` | botão principal | `rgba(14,30,22,.92)` | `rgba(58,168,255,.2)` |
| `--hx-btn-ink` | texto do botão principal | `#A6E8BC` | `var(--hx-texto)` (proposta) |
| `--hx-btn-borda` | borda do botão principal | `#6CC58A` | `#3AA8FF` |
| `--hx-medidor` | barra do medidor sem cor própria | `#9FD5D9` | `#5FD4FF` |
| `--hx-medidor-trilho` | trilho do medidor | `rgba(118,170,175,.2)` | `rgba(150,172,194,.2)` (proposta) |
| `--hx-mascara` | segmentos do medidor | `repeating-linear-gradient(90deg,#000 0 7px,transparent 7px 9px)` | igual (proposta; a referência só diz "segmentada") |
| `--hx-alerta`, `--hx-perigo`, `--hx-ok`, `--hx-necessidade`, `--hx-aprendido` | semântica do UI_GUIDELINES §3 | `#FFB020`, `#D46A6A`, `#4BE07E`, `#FF7FC0`, `#6FE3FF` | **iguais** (a cor de cada necessidade não muda) |
| `--hx-foco` | anel de foco | `#7FE3FF` | `#5FD4FF` (proposta: distinto da borda `#3AA8FF` do escolhido) |
| `--hx-f` | fonte dos menus | `"Saira Condensed", "Rajdhani", system-ui, sans-serif` | `"Barlow", system-ui, sans-serif` |

Tokens novos (a T1 cria nas duas peles; no Militar valem "nada muda"):

| token novo | papel | Militar | Holográfico |
|---|---|---|---|
| `--hx-f-num` | números e estados | `var(--hx-f)` | `"Rajdhani", system-ui, sans-serif` (700) |
| `--hx-num` | cor de números e estados | `var(--hx-texto-2)` | `#5FD4FF` |
| `--hx-escolhido-borda` | borda do escolhido (a de hoje usa `--hx-escolhido` como cor; no vidro ele é gradiente) | `#BFE5E7` | `#3AA8FF` |
| `--hx-escolhido-brilho` | brilho leve do escolhido | `none` | `0 0 8px rgba(58,168,255,.35)` (proposta) |
| `--hx-borda-int` | contorno interno recuado 4 px | `transparent` | `rgba(150,172,194,.2)` |
| `--hx-vidro` | `backdrop-filter` | `none` | `blur(10px)` |
| `--hx-reflexo` | camada do reflexo sobre a superfície | `none` | `linear-gradient(155deg, rgba(255,255,255,.06), rgba(255,255,255,.015) 34%, transparent 35%)` |
| `--hx-sombra` | sombra do painel | `none` | `0 8px 18px rgba(0,0,0,.4)` |
| `--hx-chanfro` / `--hx-chanfro-p` | chanfro do painel / do escolhido | `0` / `0` | `12px` / `8px` |
| `--hx-luz` | trecho de luz 96×2 px, marcador 4×4 px, barra de 3 px no trilho | `transparent` | `#3AA8FF` (com `box-shadow: 0 0 8px #3AA8FF`) |
| `--hx-titulo-tam` / `--hx-titulo-esp` | título do painel | `18px` / `.08em` | `13px` / `2px` |
| `--hx-rotulo-tam` | rótulo pequeno | `12px` | `11px` (10 px só onde já é 10–11 hoje) |
| `--hx-medidor-alt` | altura da barra | `12px` | `5px` |
| `--hx-medidor-brilho` | brilho da barra | `none` | `0 0 6px currentColor` (proposta) |

Notas para a T1:

- **Chanfro com `clip-path` corta a borda e a sombra.** A sombra vai num elemento de fora (ou `filter: drop-shadow`) e o
  contorno do chanfro num pseudo-elemento ou numa borda desenhada por gradiente; não mudar o DOM dos componentes por isso.
- **`backdrop-filter` só funciona com fundo translúcido** e custa caro em celular: um vidro por painel, não por linha.
- O `.hx-painel__cab::before` (hachura) vira, no Holográfico, o trecho de luz no topo esquerdo; o marcador 4×4 px vai num
  `::after` do painel.
- A M1 registrou o contraste do Militar contra o pior fundo (`tokens.css`); o Holográfico precisa da mesma tabela, medida
  sobre a parte **mais clara** do habitat atrás do vidro (§6).

### 3.3 Onde a pele é pintada sem passar só pelos tokens

A pele por CSS sobre classes `dl-*` (decisão D7 do layout) remapeia os `--dl-*` para tons escuros fixos. Esses remapeamentos
e as cores literais **não mudam com `data-pele`**; a T1 precisa cobrir cada um em `estilo/pele-vidro.css`:

| arquivo (branch) | o que tem | o que a T1 faz |
|---|---|---|
| `estilo/painel-hx.css` (M4, `v2-layout-telas`) | remapeia ~50 `--dl-*`/`--ui-*` dentro de `.painel-tela__folha` com literais (`#16191E`, `#111B1E`, `#4F6B6F`, `#5E7C80`, `#16282B`, `#6CC58A`…); `rgba(22,46,34,.96)` no hover do `.dl-btn`; `#3A4C4F` no desabilitado | bloco `:root[data-pele="vidro"] .painel-tela .painel-tela__folha { … }` com os mesmos nomes; botão principal e chips com os tokens novos |
| `estilo/abertas.css` (M6, `v2-layout-auto`) | `.ab-hx` remapeia `--dl-*` (via `--hx-*`, já segue a pele) e literais: `rgba(118,170,175,.22)` (`--dl-hex`), véus `rgba(11,17,24,.9)` / `.72`, `rgba(10,19,22,.9)`, brilhos `rgba(127,227,255,.03–.12)` | trocar os literais de pele por tokens ou sobrepor em `pele-vidro.css`; véu escuro sobre o habitat igual nas duas |
| `estilo/menus_config.css` (M5, `v2-layout-config`) | `.mc-*` só com `--hx-*`; literais `#2C73E0`, `#E8F0FB`, `#0B1636` são a **prévia do tema do habitat** (ficam); `rgba(4,8,12,.6)` véu | nada na pele; a T2 acrescenta os cartões da pele aqui |
| `estilo/pet_dock.css` (M3, `v2-layout-pet`) | dock, painéis Estado/Evolução/Últimas ações, chamado; literais `rgba(10,19,22,.96)` (fundo) e `rgba(255,255,255,.9)` | fundo vira token; conferir se o branco é do balão (fica) ou do menu |
| `estilo/casca.css` (M2, `v2-layout-casca`) | trilho `.hx-nav`, `.topo-bt`, `.painel-tela`; literais `#FFFFFF` e `rgba(15,42,102,.35)` são do **topo do habitat** (retrato/relógio, ficam); véus `rgba(4,8,12,.5)` / `.45` | `.hx-nav__bt[aria-current]` ganha a barra acesa de 3 px no Holográfico |
| `estilo/hud.css` (M1) | componentes `hx-*`; literal `rgba(22,46,34,.96)` no hover do `.hx-continuar` | literal vira token (`--hx-btn-bg-hover`) |
| `estilo/decoracao.css` | `.cfg-tema*` (molde antigo; depois da M5 parece sem uso) | nada; a M7 decide se é CSS morto |
| DigiBrain, "Por que ele disse isso" | ganham a pele Militar na M7 (D8) | a T1 confere o que a M7 entregou |

A lista vale sobre os branches de hoje; antes de começar, a T1 refaz a busca por literais (`#…`, `rgba(`) em todo arquivo
que lê `--hx-*` ou `.ab-hx`/`.painel-tela__folha`/`.mc` depois dos merges e da M7.

## 4. A pele é preferência de tela

`web/app/src/pele.ts`, irmão de `tema.ts` e no mesmo molde:

- `export type Pele = "xcom" | "vidro"`; `PELE_PADRAO: Pele = "vidro"` (TM1); `NOME_PELE = { xcom: "Militar", vidro: "Holográfico" }` (TM2);
- chave `CHAVE + "-pele"` no `localStorage` (a chave do save não muda); sem armazenamento → o padrão;
- `data-pele` no `<html>` sempre presente (`xcom` ou `vidro`), para o CSS não depender de ausência de atributo;
- `?pele=xcom|vidro` no endereço sobrepõe **sem gravar** (conferência, e2e e capturas), como `?tema=`;
- `iniciarPele()`, `escolherPele(p)`, `usePele()` com ouvintes, como `useTema()`.

**Fora** do save, do registro e do replay: nenhum evento do motor, nenhum campo novo no save, a assinatura do pet não muda.
**O motor não muda.**

## 5. Missões

Um PR por missão, cada uma numa worktree `D:\Trab\digilab\v2-tema-<missão>` a partir de `origin/main`.

- **T0 · Tarefa (este documento).** Sem código.
- **T1 · Pele Holográfico.** `pele.ts` + teste de unidade (padrão, chave, `?pele=` sem gravar, valor inválido, sem
  armazenamento); `iniciarPele()` no `main.tsx` ao lado de `iniciarTema()`; tokens do Holográfico em
  `:root[data-pele="vidro"]` no `tokens.css` e os tokens novos da §3.2 nas duas peles; o resto em
  `estilo/pele-vidro.css` (importado depois de `hud.css`, `painel-hx.css`, `abertas.css`, `menus_config.css`, `pet_dock.css`),
  **sem mudar a estrutura dos componentes** (`componentes/hx/*` e telas iguais; só classes e CSS); Barlow (400–700) e
  Rajdhani (700) no `<link>` de fontes do `index.html` (hoje só há Saira Condensed nos menus); a tabela de contraste do
  Holográfico no comentário do `tokens.css`. A tela de escolha ainda não existe: confere-se com `?pele=`.
- **T2 · Escolha em Ajustes › Aparência.** Seção "Pele dos menus" acima de "Tema do habitat", dois cartões de prévia
  (Militar, Holográfico) no molde de `.mc-opcao--tema`/`.mc-tema-prev`: `role="radiogroup"` com `aria-labelledby`, cada
  cartão `role="radio"` + `aria-checked`, setas entre os cartões, foco visível, alvo ≥ 44 px, a troca vale **na hora**
  (sem recarregar). A prévia é desenhada em CSS (sem imagem). O resumo de "Aparência" no menu de Ajustes mostra a pele e o
  tema. O texto de apoio explica que a pele vale nos menus e o tema no habitat.
- **T3 · Conferência e capturas.** Todas as telas (Pet com dock e painéis, Crescer, Lutar, Diário, Conversar, Ajustes,
  Meus pets, telas que abrem sozinhas, luta em tela cheia e resultado, DigiBrain, "Por que ele disse isso") nas duas peles
  × claro/escuro, em 360, 390 e 1280 px; correções; e2e de troca de pele (Ajustes › Aparência → `data-pele` muda, a escolha
  sobrevive ao recarregar, `?pele=` não grava); `e2e_capturas` nas duas peles (TM5), regeneradas **depois da aprovação do
  Matheus**.

Ordem: **T1 e T2 só depois dos merges da frente do layout (#458→#460→#464→#467–#470) e da M7** (TM6). T2 depende da T1;
T3 depende de T1 e T2. Arquivos de uma missão por vez: `tokens.css`, `main.tsx`, `index.html`, `TelaConfig.tsx`,
`menus_config.css`.

## 6. Critérios de aceite (no fim da T3)

- **Contraste AA** (4,5:1 texto, 3:1 bordas e ícones) de todo texto do Holográfico sobre o vidro, medido com o vidro
  sobre a parte **mais clara** do habitat (tema claro, cenário mais claro) e registrado no `tokens.css`; o Militar sem regressão.
- **Foco visível** em todo controle nas duas peles, distinto do estado escolhido.
- **`prefers-reduced-motion`:** sem transição nem brilho animado; o trecho de luz fica parado.
- **`prefers-reduced-transparency: reduce`:** o vidro fica **opaco** (`backdrop-filter: none`, superfície sem alfa) e o
  contraste continua AA.
- Pele padrão Holográfico; "XCOM" não aparece na tela; a troca vale na hora e sobrevive ao recarregar.
- Habitat, pet, retrato, relógio e balão iguais nas duas peles; **tema claro/escuro sem regressão** nas 2 × 3 combinações.
- Nomes Digimon na tela; **nenhum caractere japonês ou chinês**; português do Brasil; só o que o motor registra aparece.
- Sprites, atlas, pranchas e páginas de referência **nunca no git**; e2e e capturas com o sprite de reserva.
- Nenhuma mudança no motor; replay e paridade intactos; save sem campo novo; `npm run tipos`, `npm test`, `npm run e2e` e o
  portão de capturas (regenerado nas duas peles) passando.
