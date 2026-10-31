# Tarefa V2 — tema dos menus: peles Militar e Holográfico

Gerente: sessão "Gerente do tema dos menus" (2026-10-30). Merge só do Matheus. Base: `origin/main` 19668ab9.
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
| TM2 | nomes na tela | **"Militar"** (id `xcom`) e **"Holográfico"** (id `vidro`; **"Sci-fi"** desde 2026-10-31, pedido do Matheus na refeitura das peles). A palavra "XCOM" não aparece na tela (fica só em id, classe e comentário) |
| TM3 | onde a pele vale | **só nos menus** (painéis, trilho/barra, dock, chamado, modais, telas que abrem sozinhas), **sempre escura**. Claro/escuro continua no habitat, balão, retrato e relógio. Pele e tema são **eixos independentes**: as 2 × 3 combinações valem |
| TM4 | onde se escolhe | **Ajustes › Aparência**, dois cartões de prévia no molde de `.cfg-tema` (depois da M5: `.mc-opcao--tema` + `.mc-tema-prev` em `menus_config.css`) |
| TM5 | capturas | **completas nas duas peles, em 1920×950** (D10 do Matheus, 2026-10-30: só o desktop, o monitor dele a 100 %; celular e outras larguras ficam sem polimento, só não podem quebrar o e2e). Antes da D10: 360, 390 e 1280 px |
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

**Refeitos em 2026-10-31 (voltam a PROPOSTOS):** a tabela abaixo é a da T1/T3; os valores de hoje, das duas peles, estão em
`web/app/src/estilo/tokens.css` e na seção "Resultado da refeitura das peles", no fim. Ficam PROPOSTOS até a aprovação das capturas novas.

**DECIDIDOS (2026-10-31, antes da refeitura).** Fonte: o Matheus aprovou as capturas da T3 (PR #505, "Continue com o recomendado"). Valem como DECIDIDOS
todos os "(proposta)" das duas tabelas abaixo, com os quatro ajustes de contraste da T1 (início do gradiente .92, contorno externo .62,
rótulo/secundário `#A3B2C3`, perigo `#F09A9A`), o brilho do escolhido por dentro (`inset`) e o texto escuro da etiqueta "você" no
Holográfico (T3). Os valores de verdade são os de `web/app/src/estilo/tokens.css` e `pele-vidro.css`.

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

**Refeita pela T1 sobre a `main` d5599452 (depois da M7):** os mesmos sete arquivos leem `--hx-*`; a M7 não acrescentou literal
de pele (o DigiBrain e o "Por que ele disse isso" leem os `--dl-*` remapeados do `painel-hx.css`, cobertos no mesmo bloco do vidro;
`.db-emo` roxo e `.db-contra` rosa são cor de estado e ficam). O resultado da busca e o que a T1 fez com cada literal estão na seção
"Resultado da T1", no fim.

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
  × claro/escuro, em 1920×950 (D10); correções; e2e de troca de pele (Ajustes › Aparência → `data-pele` muda, a escolha
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

## Resultado da T1 (2026-10-30, worker Claude Code, Opus 5.5, worktree `v2-tema-t1`)

- **`web/app/src/pele.ts`** no molde do `tema.ts`: `Pele = "xcom" | "vidro"`, padrão `vidro`, chave `CHAVE + "-pele"`, `data-pele`
  sempre no `<html>`, `?pele=` sobrepõe sem gravar (valor inválido cai no gravado e depois no padrão), `escolherPele()`, `usePele()`,
  `peleAtual()`, `NOME_PELE`. Fora do save, do registro e do replay. `iniciarPele()` no `main.tsx` logo depois de `iniciarTema()`.
  Teste: `test/pele.test.ts`.
- **Tokens:** o Militar continua em `:root` como estava e ganha os tokens novos da §3.2 com valor neutro, mais dois para literais que
  viraram token (`--hx-btn-bg-hover`, `--hx-painel-fim`). O Holográfico fica em `:root[data-pele="vidro"]`, com a tabela de contraste
  no comentário do `tokens.css` e conferida em `test/hx_pele.test.ts`. As bordas do escolhido passam a ler `--hx-escolhido-borda`
  (no vidro o `--hx-escolhido` é gradiente e não serve de cor).
- **`estilo/pele-vidro.css`**, importado por último no `main.tsx`, toda regra sob `:root[data-pele="vidro"]` (vence também os CSS
  importados pelas telas): vidro com chanfro, contorno externo e interno, reflexo, trecho de luz e marcador; o escolhido com
  gradiente, borda azul, brilho por dentro e chanfro de 8 px; barra acesa de 3 px no trilho; botão principal azul; medidores de 5 px
  segmentados com brilho na cor de cada necessidade; números em Rajdhani; os literais da §3.3 remapeados.
- **Literais da §3.3 na main de hoje:** `painel-hx.css` (os `--dl-*`/`--ui-*` da folha, o `#3A4C4F` do desabilitado, o fundo radial da
  Evolução) → bloco do vidro; `rgba(22,46,34,.96)` (hover do botão principal, `hud.css` e `painel-hx.css`) → `--hx-btn-bg-hover`;
  `pet_dock.css` `rgba(10,19,22,.96)` → `--hx-painel-fim`, `rgba(255,255,255,.9)` é a dica da ração sobre a cena (fica);
  `abertas.css` `--dl-hex` e os brilhos ciano da Boas-vindas/Como jogar → azul do vidro, os véus escuros e o palco da luta ficam
  iguais, `#0E1E16`/`#1E1214` (faixa de vitória/derrota) ficam; `casca.css` e `menus_config.css` sem literal de pele (topo do
  habitat, prévia do tema e véus ficam).
- **Contraste:** medido no pior caso, branco puro atrás do vidro (o tema claro mais claro; o desfoque só tira a média), com o reflexo
  por cima. Para passar AA, quatro valores saem da referência (desvio registrado em `docs/registro/2026-10.md`): opacidade do início
  do gradiente .84 → .92; contorno externo .5 → .62; rótulo/secundário `#8A9BAD` → `#A3B2C3`; perigo `#D46A6A` → `#F09A9A`. Dos
  "(proposta)": `--hx-escolhido-brilho` vai por dentro (`inset`), porque o chanfro corta a sombra de fora.
- **Limites conhecidos:** o chanfro (`clip-path`) corta a sombra do painel; ela vai no invólucro onde há um (painel lateral, painéis
  da tela Pet). Atrás do painel lateral não há habitat (a casca encolhe o habitat), então o vidro ali desfoca o fundo escuro.
- **Conferência:** o portão `e2e_capturas` ganhou `DIGILAB_CAPTURAS_PELE` (padrão `xcom`, o das referências da M7; `vidro` grava com
  `_vidro` no nome). Com `?pele=xcom`, as 21 telas batem pixel a pixel com as referências da M7.

## Resultado da T2 (2026-10-30, worker Claude Code, Opus 5.5, worktree `recursing-dirac-023802`)

- **`web/app/src/telas/config/EscolhaPele.tsx`:** a seção "Pele dos menus", que o `TelaConfig.tsx` põe no alto de Aparência, acima de
  "Tema do habitat". Dois cartões no molde de `.mc-opcao--tema`: `role="radiogroup"` com `aria-labelledby`, cada cartão `role="radio"` +
  `aria-checked`; setas, Home e End movem e escolhem (`indiceAbaPorTecla` das abas hx), e só o escolhido entra na ordem de Tab. O clique e as
  setas chamam `escolherPele()`: o `data-pele` muda na hora e a escolha fica gravada. Na tela, só "Holográfico" e "Militar" (TM2).
- **Ordem dos cartões:** o Holográfico primeiro, por ser o padrão (TM1). O texto de apoio diz que a pele vale nos menus e o tema no habitat.
- **Resumo de Aparência** no menu de Ajustes: `pele <nome> · tema <tema>` (`resumoAparencia`).
- **Prévia em CSS** (`.mc-pele-prev` em `menus_config.css`): um painel em miniatura com a faixa do título, o item escolhido e o botão
  principal, nas cores fixas de cada pele (§3.1), para mostrar a outra pele mesmo com esta ligada. Sem imagem.
- **Testes:** `test/escolha_pele.test.ts` (o radiogroup, o `tabindex`, os nomes sem XCOM, o resumo, a prévia só em CSS, a ordem das
  seções) e o e2e "pele dos menus" em `e2e/jogo.spec.ts`, em 1920×950: o padrão Holográfico, a seção acima do Tema, os alvos ≥ 44 px, a troca
  pelo clique e pelas setas sem recarregar, a escolha gravada e mantida ao recarregar, o resumo. Parte do e2e de troca de pele previsto na
  T3 já entra aqui; o `?pele=` sem gravar continua conferido pelo teste de unidade da T1.
- **Fora:** o radiogroup do tema do habitat continua sem setas, como estava; `tokens.css` e `pet_dock.css` não mudaram.

## Resultado da T3 (2026-10-30, worker Claude Code, Opus 5.5, worktree `agitated-rubin-b2128e`)

Conferência das duas peles e capturas para a aprovação do Matheus. **Aprovadas em 2026-10-31:** os valores da §3.2 viraram DECIDIDOS,
e as referências do `e2e_capturas` foram regeneradas nas duas peles (o fim desta seção).

- **Capturas, fora do git, em `D:\Trab\digilab\capturas_tema_t3\`** (sprite de reserva; o `LEIA.txt` da pasta lista o que é cada uma):
  - `portao\`: as 21 telas do portão nas duas peles, em 1920×950 (D10), 1280 e 390 px, no tema claro: 126 PNG (`<tela>-<largura>.png`
    é o Militar; `<tela>-vidro-<largura>.png`, o Holográfico). Gravadas com `DIGILAB_CAPTURAS_PELE=vidro|xcom`,
    `DIGILAB_CAPTURAS_RESERVA=1` e `DIGILAB_CAPTURAS_LARGURAS=1920,1280,390`;
  - `conferencia\`: as telas que o portão não alcança, nas duas peles × claro/escuro, em 1920×950: a tela Pet com a pilha da HUD, os
    três painéis abertos, o DigiBrain, o "Por que ele disse isso", o menu Mais do dock, Meus pets, Ajustes › Aparência, as
    Boas-vindas, o Como jogar, a luta em tela cheia e o Resultado (44 PNG), e o anel de foco sobre o cartão escolhido e sobre o outro (8
    PNG). Gravadas por `e2e_capturas/conferencia_pele.spec.ts` com `DIGILAB_CONFERENCIA_PELE=<pasta>`; sem a variável, o spec fica de
    fora do portão.
- **Contraste AA, medido no render** (o mesmo spec: o texto fica transparente, a página é fotografada e, no retângulo de cada texto, o
  percentil 10 do fundo dá a razão WCAG; o pior pixel vai ao lado, em `contraste_*.json`). Tema claro, 24 telas (as 18 rotas do portão
  e das Ajustes, a pilha da HUD aberta, o DigiBrain, o porquê, Meus pets, Boas-vindas e Como jogar), só texto visível inteiro:
  - **Holográfico:** 1170 textos, mediana 11,9:1. Abaixo de AA: os nós trancados da árvore de evolução (`.evo-sub`, 9 px, 2,10:1) e
    três textos do laboratório de Cenários (`.lab-nota` 2,97; a legenda do pet B 3,31; "FERRAMENTA DE PESQUISA" 3,56). **Todos falham
    igual no Militar** (1,98; 2,95; 3,21; 3,41): vêm de cores do jogo, não da pele. Ficam como estão (fora do escopo).
  - **A etiqueta "você" do Registro** (o `#FFFFFF` literal do `diario.css` sobre `--dl-action`) dava 2,55:1 no Holográfico; com o texto
    escuro `--dl-action-ink` passou a 7,5:1 (correção de pele, desvio no registro). No Militar ela segue em 2,1:1, como antes.
  - Os textos sobre o habitat de dia (pet v11 às 15:10): o pior no DigiBrain 5,74, no porquê e na pilha 7,5, em Meus pets 6,83.
  - Duas linhas do Registro aparecem como 1,0 e 4,03 no JSON: são a última linha da lista, cortada pela rolagem interna (a foto do fundo
    em `conferencia\fundos\` mostra só a borda da etiqueta); não é texto legível.
  - **Militar sem regressão:** 1097 textos, as mesmas falhas de antes, nenhuma nova.
- **`prefers-reduced-transparency: reduce`** (emulado pelo CDP): o painel lateral vai de `backdrop-filter: blur(10px)` a `none`, e a
  superfície de `#182432eb`/`#060b12eb` a `#18242f`/`#060b12` (sem alfa). O contraste fica igual ou sobe (as mesmas 12 medidas abaixo
  de AA, sem nova).
- **Foco visível:** 80 toques de Tab por pele (Treinar, Aparência, Pet), nenhum controle sem indicação. No Holográfico o anel é 2 px
  `#5FD4FF` recuado 5 px por dentro da borda 1 px `#3AA8FF` do escolhido (uma segunda linha, não a mesma); no Militar, 2 px `#7FE3FF`
  em volta do escolhido de fundo `#BFE5E7`. O trilho, o topo e a HUD usam `#49D5E2` nas duas peles (paleta da HUD). O interruptor nativo
  de Aparência mantém o anel padrão do Chrome, nas duas.
- **Padrão, nome e troca:** sem nada gravado a pele é a Holográfica; "XCOM" não aparece em nenhum dos 2267 textos medidos; a troca vale na
  hora e sobrevive ao recarregar, e `?pele=` sobrepõe sem gravar: o e2e "pele dos menus" ganhou esse caso, e o "foco visível pelo
  teclado" roda agora nas duas peles.
- **Tela Pet:** o trilho, o topo, a pilha, o dock e o balão usam a paleta turquesa da HUD nas duas peles (decisão do Matheus de
  2026-10-30, `pet_hud.css`); ali a pele só muda a fonte, as barras de 5 px e os números. As telas abertas seguem a pele escolhida.
- **Portão de capturas:** com `DIGILAB_CAPTURAS_RESERVA=1` o portão escondia `.app > .aviso`, que saiu na M7; os avisos de "não
  carregou" entravam nas capturas. Agora esconde também `.avisos > .aviso`.
- **Achados fora do escopo (para depois):** no desktop, o painel do DigiBrain cobre a ponta do balão da fala ("toque para ver o por…");
  "lutas de treino0 de 10" sem espaço na Arena, nas duas peles; abrir `#/config` pelo endereço com Meus pets aberto deixa Meus pets na tela.
- **Depois da aprovação (2026-10-31):** os valores da §3.2 viraram DECIDIDOS (a nota no alto da §3.2 e no `tokens.css`). As referências
  do portão foram regeneradas em 1920×950 nas duas peles, com o sprite de reserva (`DIGILAB_CAPTURAS_RESERVA=1`), na pasta padrão
  do checkout de referência, `D:\Trab\digilab\v3\artifacts_v2_front_react\capturas\`: 42 PNG (21 do Militar, 21 do Holográfico com
  `-vidro`). Ficam **fora do git**, como sempre (`artifacts_*/` no `.gitignore`; o `playwright.capturas.config.ts` lê de
  `DIGILAB_CAPTURAS`). Conferido contra elas: 19 de 21 telas batem pixel a pixel nas duas peles em todas as rodadas; **as duas da
  Exploração (`lutar-campanha`, `lutar-exploracao-v6`) variam nas duas peles** (uma faixa da ilha 3D atrás do mapa, de 4 a 110 mil
  pixels entre uma tentativa e outra): é do habitat, não da pele, e fica para a frente da ilha.

## Resultado da refeitura das peles (2026-10-31, worker Claude Code, Opus 5.5, worktree `v3-tema-peles`)

Pedido do Matheus: as duas peles ficavam praticamente iguais na ilha (cartões pretos opacos, as mesmas bordas e cores). Referência
visual: as duas páginas privadas originais (HUD Vidro e XCOM), lidas de novo; nada delas entrou no git. Mesmo DOM, mesmas rotas, mesmos
dados e interações; o cenário 3D, o pet e o motor não mudam.

- **A causa:** a HUD da tela Pet redefinia os `--hx-*` com uma paleta turquesa única nas duas peles (`pet_hud.css`, decisão de 2026-10-30),
  e o vidro da T1 era quase opaco (.92) para passar AA contra branco puro. Agora a HUD segue a pele (desvio no registro).
- **Militar (`xcom`):** grafite fosco quase opaco e sem desfoque (painel `#1C1F22`, caixas da HUD `rgba(30,33,36,.97)`), cantos retos, linha de
  topo `#6E7872` de 2 px, marcadores táticos discretos (cantos em L no tom do rótulo, hachura caixa-cinza nos títulos), escolhido caqui
  `#C5CFB0` com texto escuro, verde de sinalização só no botão de ação (CONTINUAR e o principal das telas), sem brilho; os literais teal
  das telas viram grafite (`estilo/pele-xcom.css`, novo).
- **Sci-fi (`vidro`):** azul-marinho translúcido `rgba(10,26,52,.78)` → `rgba(5,14,30,.86)` com desfoque de 12 px (o cenário passa por trás),
  borda fina `rgba(110,200,255,.72)`, chanfros, reflexo, contorno interno, brilho suave por dentro, trecho de luz e marcador `#5FD4FF`,
  escolhido em gradiente azul com borda ciano e brilho; as linhas, teclas e cartões dentro de um painel ganham só um realce azul leve
  (`--hx-tecla`), sem outro fundo escuro. Nome na tela: **Sci-fi**.
- **Tokens novos:** `--hx-tecla`, `--hx-tecla-hover`, `--hud-fundo-1`, `--hud-fundo-2`, `--hud-desfoque`, `--hud-ch`, `--hud-ch-p`, `--hud-brilho`,
  `--hud-risca` (antes literais em `pet_hud.css`, `casca.css` e `pet_dock.css`).
- **Contraste:** o pior caso do vidro passa a ser a grama da ilha de dia (o pixel mais claro do habitat nas capturas da H5), não branco puro
  (`test/hx_pele.test.ts`); no render (`conferencia_pele.spec.ts`, tema claro, 24 telas) o Sci-fi tem 1170 textos, mediana 12,5:1, e só as
  falhas que já existiam no Militar (os nós trancados da árvore, o laboratório de Cenários) mais a linha do Registro cortada pela rolagem;
  o opaco (`prefers-reduced-transparency`) tem as mesmas, mediana 13,3; o Militar, 1097 textos, mediana 11,1, as mesmas de antes.
- **Capturas** (fora do git, `D:\Trab\digilab\capturas_tema_peles\r3\`): a ilha e o Crescer › Treinar nas duas peles em 1280 e 390 px
  (`lado_*.png`, Militar à esquerda), e as telas extras da T3 nas duas peles × claro/escuro em 1920 × 950. O teste novo "ilha nas duas peles"
  do `conferencia_pele.spec.ts` grava a ilha e o Crescer.
- **Portão `e2e_capturas`:** as referências são as da T3; elas só são regeneradas depois da aprovação do Matheus (TM5).
