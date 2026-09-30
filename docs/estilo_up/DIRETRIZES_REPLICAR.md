# Como replicar as pranchas no front (e ficar igual)

Para quem implementa o app (`web/app/`). Complementa `docs/UI_GUIDELINES.md` (regras) e
`docs/ASSETS_UP.md` (imagens). O objetivo aqui é **fidelidade visual**: medidas, fontes e
receitas exatas.

## 1. As três referências, nesta ordem

1. **A prancha renderizada.** Abrir `http://localhost:8765/Assets/Pranchas_UP/index.html` (servidor
   local ligado). Cada prancha é o HTML exato do canvas, com as imagens locais (uso pessoal, fora
   do repositório). Abrir **em 390×844** e comparar com o app no mesmo tamanho.
2. **O código da prancha.** O mesmo arquivo `Assets/Pranchas_UP/<Prancha>.html` tem todos os
   valores em `style="…"`. Quando em dúvida sobre um tamanho, cor ou espaço, **copiar o número da
   prancha**, não estimar pelo olho. (No canvas, a ferramenta Artifact lê
   `project/<Prancha>.dc.html` com o mesmo conteúdo.)
3. **`docs/estilo_up/dl-up.css`.** Os mesmos valores já organizados em classes `dl-*`. Pode
   importar direto ou copiar para `src/estilo/`. Os nomes batem com os que o app já usa quando
   possível.

A prancha `CatFicha` usa uma animação que só roda no canvas; na cópia local o sprite fica vazio.

**Nomes:** use sempre os do app (Digimon, brasões e níveis Digimon, guia seção 12). Os textos das
pranchas (nomes de forma, "criança/adolescente", números) são exemplo de layout.

## 2. Desvios que fazem "não ficar parecido" (vistos no app em 2026-09-28)

Corrigir estes primeiro; são os que mais mudam a aparência.

| # | no app | na prancha | como corrigir |
|---|---|---|---|
| 1 | cada destino dentro de um card com borda, com 16px de padding em volta da página | a tela é **cheia**: sem card por fora, cabeçalho encostado no topo e nas laterais | remover o `.painel` com borda e o padding do `body`; usar `.dl-tela` + `.dl-cab` + `.dl-conteudo` (margem lateral de 14px só no conteúdo) |
| 2 | hexágono desenhado em SVG pequeno (28×48) | hexágono grande da imagem `Common_Create_Bg_Pattern.png` em **180px** de largura (140px dentro do palco), linhas brancas | `background-image` com a imagem real e `background-size:180px auto` |
| 3 | fonte M PLUS sem o peso 500, que as pranchas usam em legendas | pesos 500, 700, 800 e 900 carregados | incluir 500 no link do Google Fonts (ou fontsource) |
| 4 | títulos e números sem o contorno completo | Rubik 900 itálico com contorno de 8 sombras de 2px + sombra de 4px embaixo | classe `.dl-num` (e `--grande` para 44px) |
| 5 | sprite pequeno ou fora de escala inteira | palco 3× (Agumon 44×48 → 132×144), revelação 4×, listas 1× | calcular o tamanho a partir do tamanho nativo × inteiro; `image-rendering:pixelated` |
| 6 | cocô em triângulos, cena antiga | palco em card hexagonal com anel de plataforma e balão de causa | receita da seção 4 |
| 7 | — | as pranchas escrevem "criança", "Brasa Brigão" etc. | **não trocar os nomes do app**: os nomes em Digimon estão certos (níveis In-Training, Rookie, Champion, Ultimate/Mega; formas e NPCs pelo Digimon; espécies pelo brasão). Nas pranchas, nomes e rótulos de estágio são exemplo; copiar só o visual |
| 8 | checkbox técnico "fala por LLM" | faixa de status: ponto + texto | `CfgFala` / `ConvEstados` |
| 9 | — | as barras de navegação das pranchas (celular e desktop) não têm Conversar | **manter o botão Conversar na barra** (decisão do Matheus, 2026-09-28): ícone próprio entre Diário e a engrenagem, abre `#/conversar/chat`; não é desvio a corrigir. As pranchas novas já trazem Conversar e Configurações: no cabeçalho do Pet (celular, dois botões de 44px à direita do relógio) e no pé da barra lateral (desktop) |
| 10 | apertar Lutar rola a página até um palco que já estava desenhado embaixo da aba Arena | a luta é **tela cheia**, com rota própria | ver seção 7 |

## 3. Medidas que se repetem

- **Largura de referência:** 390px (conferir também 360px). Margem lateral do conteúdo: **14px**.
  Espaço entre blocos: **12px**; entre cards de grade: **8–10px**.
- **Topo:** faixa quadriculada de **10px** + borda navy de **3px** (só no Pet) ou cabeçalho de
  **~71px** (padding 12/14, título 26px, borda de 3px).
- **Nav:** círculos de **44px**, rótulo de 12px, padding 8/8/12, borda branca de 3px em cima;
  altura total de ~83px. O conteúdo precisa de `padding-bottom` ≥ 96px para não ficar embaixo dela.
- **Card:** raio 12 (16 no palco), sombra `0 0 0 2px #9FC2EF, 0 3px 0 2px #7FA6DC`.
- **Botão:** 48px de altura, raio 12, borda branca de 3px, anel navy de 2px, sombra interna de 4px.
- **Texto:** 15/14px no corpo (700), 12px de apoio (700, #3A5288), 11px de legenda (800),
  cabeçalho de card 15px (900), título de tela 26px Rubik, revelação 44px Rubik.

## 4. Receitas de tela (coordenadas da prancha, em px)

**Pet (`UpPet`)**
1. Faixa quadriculada de 10px.
2. Linha do cabeçalho (padding 12/14/10): retrato redondo de 52px (sprite 1× dentro), plaquinha
   com o nome (15px), etiqueta de estágio embaixo, relógio `.dl-num` 26px à direita e
   "sincronizado" com ponto verde de 8px.
3. Palco `.dl-palco`, cena de **318px** de altura:
   - título "Meu parceiro" (36px, translúcido);
   - chip de emoção em (10, 46);
   - anel 212×60 em top 226;
   - sprite 3× com os pés sobre o anel (top 104 para um sprite de 48px de altura);
   - balão de causa em (222, 60) com o rabinho;
   - plaquinha do nome embaixo (bottom 14).
4. Necessidades em grade de 4 (barra segmentada de 5).
5. Chamado.
6. Par necessidade × vontade.
7. Nav.

**Luta (`UpLuta`, `BatAcao`)**
1. Palco `.dl-arena` de 420–430px de altura.
2. HUD no topo (top 12, laterais 10): dois `.dl-hud__lado` com retrato de 34–36px, vida (9px) e
   guts segmentado (5px), turno em hexágono de 50px e, abaixo, a distância.
3. Sombras 16px de altura sob os pés.
4. Sprites 3×; o seu virado para a direita (`scaleX(-1)` quando o sprite olha para a esquerda).
5. Intenção do rival em balão com borda `#7A1F3A`.
6. Ação em plaquinha inclinada; dano em `.dl-num--dano` 32–34px.
7. Abaixo do palco: card de intenção, card de regra `.dl-malha.dl-aprendido`, registro.

**Revelação (`UpEvolucao`, `AssetsEvolucao`)**
1. Fundo `.dl-listras` + hexágono a 30%.
2. Etiqueta "criança → adolescente" e título "EVOLUÇÃO!" `.dl-num--grande` 44px.
3. Círculo branco a 18% de 240px com dois halos; anel de Digivice girando (opacidade 0,8) e anel
   de luz por trás.
4. Sprite 4× com `.dl-brilho-pet`.
5. Plaquinha do nome com borda branca.
6. Card "por quê" `.dl-card--forte`.
7. Botão destaque "Continuar".

**Campanha (`CampMapa`)**
1. Mapa de 420px com o oceano de fundo, as ilhas em escala 0,85 (150px), o trilho (linha branca
   tracejada ou amarela contínua), os marcadores e a moldura digital por cima a 55%.
2. O card do lugar sobe 26px sobre o mapa (`margin-top:-26px`).

## 5. Como validar

1. Servidor local ligado; prancha em `/Assets/Pranchas_UP/<Prancha>.html` e app lado a lado, os
   dois em 390×844, mesmo tema.
2. Screenshot dos dois. Comparar nesta ordem: **estrutura** (blocos e ordem), **medidas** (alturas
   dos blocos, margens), **tipografia** (fonte, peso, tamanho, contorno), **cor**, **escala de
   sprite**.
3. Diferença de mais de ~4px numa medida, fonte errada ou cor fora dos tokens: corrigir.
   Conteúdo (números, nomes) é exemplo e não conta.
4. Registrar por tela: igual / parecido / diferente, com o motivo quando ficar diferente (falta de
   dado no motor ou decisão do Matheus).

## 6. Desktop (a partir de 1100px): casca única

Pranchas `*Desktop` (1280×720), todas com a mesma casca:

- **Barra lateral** de 96px, navy `#173A8A`, borda direita branca de 3px:
  - no topo, ovo + "DIGILAB";
  - os 4 destinos (círculos de 50px, ativo com anel ciano e brilho);
  - no pé (`margin-top:auto`), **Conversar** e **Ajustes** (quadrados de 46px, raio 12).
- **Barra do topo** de 76px com quadriculado:
  - título Rubik 30px;
  - abas em pílula;
  - à direita, o **mini-card do pet**: retrato de 44px (abre Meus pets), nome, brasão, estágio, dia e relógio com "salvo".
- **Conteúdo:** padding 20/24, em 2 ou 3 colunas. As colunas vão até o fundo: o último card de cada coluna tem `flex-grow:1`, para não sobrar buraco embaixo.
- A **luta** e a **primeira vez** não usam a casca (ver seção 7).

## 7. Página, aba, tela cheia, modal, folha ou faixa

A prancha `NavMapa` (página "Direção Digimon UP" do canvas) mostra isto em desenho.

| tela | tipo | abre com | fecha / sai | rota |
|---|---|---|---|---|
| Pet | página | menu | — | `#/pet` |
| Crescer · Treinar / Aprendizado / Evolução | aba | menu Crescer | outra aba | `#/crescer/<aba>` |
| Lutar · Arena (escolha do rival + prévia parada) | aba | menu Lutar | outra aba | `#/lutar/arena` |
| Lutar · Campanha (mapa + rivais da ilha) | aba | menu Lutar | outra aba | `#/lutar/campanha` |
| **Luta em andamento** (arena e campanha) | **tela cheia** | botão Lutar / Desafiar | fim da luta → modal Resultado; ou Desistir | `#/lutar/luta` |
| Resultado da luta (pranchas `ResVitoria`, `ResDerrota`, `ResCampanha`, `ResDesktop`, regras em `ResNota`) | modal, sem × | abre sozinho no fim da luta, sobre a luta congelada | Continuar (ou Esc) → aba de origem; Ver replay → Diário | — |
| Revelação de evolução | tela cheia | o motor evolui o pet | Continuar → Crescer · Evolução | `#/evolucao` |
| Diário · Registro / Catálogo / Lab | aba | menu Diário | outra aba | `#/diario/<aba>` |
| Ficha do Digimon; detalhe de um evento; porquê do balão | folha (celular) / painel fixo à direita (desktop) | tocar no item | × ou tocar fora | — |
| Conversar | página | menu / botão no Pet | menu ou Voltar | `#/conversar/chat` |
| Configurações | página | menu (engrenagem) | menu ou Voltar | `#/config` |
| Loja · Chapéus / Rosto / Digivice / Armário (pranchas `Loja*`, página Loja) | página com abas | saldo de bits no cabeçalho do Pet ou no topo do desktop | Voltar → Pet | `#/loja/<aba>` |
| Item da loja + provador | folha (celular) / painel fixo à direita (desktop) | tocar num item | × ou tocar fora | — |
| Confirmar compra | modal | Comprar | Cancelar / Comprar | — |
| Meus pets / trocar / novo ovo | modal | mini-card ou retrato do pet | × ou Esc | — |
| Nova geração · 1 escolher os pais, 2 o que o filho herda (pranchas `Her*`, página Herança e gerações) | página em 2 passos | botão "Nova geração" em Meus pets (só com o pet adulto) | Voltar → Meus pets | `#/heranca` |
| Confirmar a nova geração | modal | Cruzar | Cancelar / Cruzar | — |
| O ovo novo | tela cheia | depois de cruzar | Chocar o ovo → Pet | `#/heranca/ovo` |
| Diário · Gerações | aba | menu Diário | outra aba | `#/diario/geracoes` |
| Confirmar forçar treino, novo ovo, apagar | modal | ação perigosa | Cancelar / Confirmar | — |
| Primeira vez | tela cheia | sem save | Começar → Pet | `#/inicio` |
| Offline / sincronizando / erro de save | faixa | estado do servidor | some sozinha | — |

Regras:

- **Aba** troca só o que está abaixo das abas; cabeçalho e menu ficam.
- **Tela cheia** esconde o menu e as abas e trava a rolagem do fundo. O Voltar do navegador nela pede confirmação (na luta, é Desistir).
- **Luta:** a aba Arena **não desenha o palco da luta** embaixo da lista, só a prévia parada ao lado do rival escolhido. Lutar navega para `#/lutar/luta`. Nada de `scrollIntoView` para "chegar" na luta.
- **Modal** tem fundo `rgba(9,20,52,.62)`, foco preso, Esc fecha e o foco volta ao botão que abriu. Um modal por vez.
- **Folha** no celular sobe de baixo (máx. 85% da altura, alça de arrastar). No desktop não é sobreposta: vira a coluna da direita da própria aba (ex.: ficha em `CatDesktop`).

## 8. O que não fazer

- Não "interpretar" a prancha com outra biblioteca de UI ou outro raio, sombra ou fonte.
- Não usar sombra difusa, degradê decorativo nem emoji do sistema.
- Não redimensionar sprite por fração (0,8×, 1,5×): só inteiro.
- Não colocar um card em volta da tela inteira.
- Não inventar dado para preencher um bloco da prancha: bloco sem dado fica de fora e vira lacuna.
