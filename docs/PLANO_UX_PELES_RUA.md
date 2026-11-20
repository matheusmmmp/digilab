# Plano de UX das peles de rua: três modelos base (2026-11-20)

**PR-1 DECIDIDA pelo Matheus em 2026-11-20** ("Zine e Estêncil", em resposta a "Qual modelo de pele segue adiante?"): o **Zine** é o principal e o **Estêncil** é a opção escura. O Arcade não segue e fica na pasta só como registro. **PR-2 a PR-6 DECIDIDAS pelo Matheus em 2026-11-20, pela recomendação** ("Sim, aprovo", em resposta a "Aprova as PR-2 a PR-6 pela recomendação para eu começar o código pelo Estêncil?"). O código segue as etapas PE1 a PE4 (seção 8), começando pelo Estêncil. A prancha está em `docs/pranchas/ux-peles-rua/`. As cores, as fontes e os
tamanhos são **PROPOSTO, SEM FONTE**. Autor: Gerente da UX_TELA_PET (Claude Code, Fable 5.2), branch `v3-ux-peles-rua`.

**O pedido do Matheus (2026-11-20), com 15 imagens de referência:** "Eu quero que você olhe as [pranchas] que temos referente aos novos
modelos de layout, que é o vidro e o militar, né? E daí projete uma nova UI pensando numa estética mais com esse traço de desenho, com
retas, cores fortes, colagem e street art, algo moderno e daí você tenta ver o que consegue fazer para se basear." E: "Gere 3 modelos
bases diferentes".

## 1. O que foi olhado

- **As duas peles de hoje** (`docs/TAREFA_V2_TEMA_MENUS.md`; `web/app/src/estilo/tokens.css`, `pele-vidro.css` e `pele-xcom.css`):
  - **Militar** (id `xcom`): grafite fosco, caqui pálido, linha de topo e cantos em L, sem brilho;
  - **Vidro** (id `vidro`, o padrão): azul-marinho translúcido, borda ciano fina, chanfro de 12 px, brilho por dentro.
- **Como uma pele é feita:** um bloco de tokens `--hx-*` e `--hud-*` por pele e um arquivo de forma por pele (56 linhas no Militar, 188 no
  Vidro). A estrutura das telas não muda. A prancha segue esse mesmo corte.
- **O que as duas têm em comum:** são escuras, finas e discretas. Linhas de 1 px, letra condensada pequena, quase nenhuma cor.
- **As 15 referências,** agrupadas pelo que cada uma traz:
  - o traço grosso, a sombra dura e as caixas tortas (as telas de jogo em preto, amarelo e rosa; o manual do mordomo);
  - as retas e os cortes em diagonal (a página do Valorant e os cartazes dele);
  - a colagem, o adesivo com borda e a retícula (a folha de logotipos em adesivo, o cartaz do Digimon, os rótulos de lanchonete);
  - o azul com contorno marinho e o pixel (a primeira tela, a árvore de habilidades, a marca de lanches em pixel);
  - a letra desenhada como logotipo (os dois passo a passo de logotipo, o cartaz azul e vermelho).

## 2. Os três modelos

Os três usam as mesmas peças de hoje, nos mesmos lugares. Só a pele muda.

| | 1 · Estêncil | 2 · Zine | 3 · Arcade |
|---|---|---|---|
| **a ideia** | cartaz de rua | colagem de papel | adesivo de fliperama |
| **a base** | tinta quase preta, osso e vermelhão | papel creme, traço preto, amarelo e anil | azul-cobalto, marinho, lima e branco |
| **a forma** | cantos cortados em 45°, botões em paralelogramo | caixas retas giradas até 1,2°, traço meio tremido | cantos em degrau de pixel |
| **a sombra** | dura, preta, 5 px | dura, preta, 5 px | dura, marinho, 5 px |
| **a letra dos títulos** | Saira Stencil One (vazada) | Rubik 900 itálico | Bungee |
| **o enfeite** | riscas de sinalização, índice vermelho | fita amarela, retícula, tiras pretas | retícula de pontos, borda branca de adesivo |
| **de quem descende** | do Militar | de nenhuma das duas: é a única clara | do Vidro |
| **o que muda mais** | a letra e os cortes | tudo: claro no lugar de escuro | a cor chapada no lugar do vidro |

**O que não muda em nenhum:** o habitat e o pet (a pele não os toca), os nomes do Digimon, a posição das peças e o sentido das cores do
guia (seção 3): a necessidade é rosa, o aprendido é ciano, o alerta é âmbar, o perigo é vermelho e o ok é verde.

## 3. As telas da prancha

Para cada modelo: a tela do pet a 1920 × 950, um lugar aberto (Crescer › Treinar, o painel mais cheio do jogo), o celular (a tela do pet e
a folha, a 390 × 844) e a folha do modelo (a paleta, as letras, os botões, as etiquetas, os medidores). E uma prancha com as duas peles de
hoje e os três modelos lado a lado.

## 4. O que cada modelo pede de novo

Uma pele nova é um bloco novo de valores para os tokens que já existem. Fora isso:

| | 1 · Estêncil | 2 · Zine | 3 · Arcade |
|---|---|---|---|
| **tokens novos** | `--hx-f-tit` (a letra dos títulos), `--hx-sombra-cor` | os mesmos dois | os mesmos dois |
| **fonte nova** (fora da seção 4.2 do guia) | Saira Stencil One | nenhuma | Bungee |
| **quebra a regra "sempre escura"** (TM3) | não | **sim** | não |
| **as cores de sentido** | as do Militar, sem mudança | mais fortes, e sempre como fundo com texto preto | mais claras, e como fundo de adesivo com texto marinho |
| **o que pesa no código** | o corte dos cantos em duas camadas | a pele clara: todo lugar que supõe fundo escuro; o giro; o filtro do traço tremido | os degraus dos cantos; a borda branca do adesivo |
| **o custo, pela leitura do código** | baixo a médio | alto | médio |

O custo é uma estimativa pela leitura do `pele-vidro.css` e do `pele-xcom.css`, não uma medida.

## 5. O contraste

Calculado pelos valores dos tokens (WCAG 2.x), não medido na tela. O mínimo do guia é 4,5 para 1.

| o par | Estêncil | Zine | Arcade |
|---|---|---|---|
| o texto na caixa | 14,6 | 16,3 | 6,5 |
| o texto secundário na caixa | 7,9 | 6,6 | 4,8 |
| o texto na tecla | 12,1 | 14,4 | 8,8 |
| o botão de ação | 5,3 | 13,2 | 14,3 |
| o escolhido | 14,6 | 5,7 | 18,1 |
| a necessidade (texto sobre o rosa) | 7,6 | 7,2 | 9,3 |

- **O Arcade é o mais apertado:** o secundário dá 4,8. Como letra sobre o cobalto, o alerta dá 4,2, o perigo 3,2 e o rosa 3,3; por isso,
  nele, essas cores só aparecem como fundo de etiqueta, com texto marinho (9,0 ou mais).
- **No Zine,** o pior par é o texto preto sobre o vermelho do perigo: 5,0.
- **Não calculado:** o texto sobre a cena (o que fica fora de caixa) e os estados de foco e de passar o mouse.

## 6. Decisões para o Matheus

**Todas DECIDIDAS em 2026-11-20:** a PR-1 pela escolha ("Zine e Estêncil") e as PR-2 a PR-6 pela recomendação ("Sim, aprovo").

- **PR-1. Qual modelo segue: DECIDIDA (2026-11-20), o Zine e o Estêncil.** A recomendação era: **o Zine como o principal e o Estêncil como a opção escura.** O Zine é o que mais responde ao
  pedido (traço de desenho, colagem, cor forte) e o que mais se separa do verde e do azul da ilha. O Estêncil é o mais barato e mantém
  uma pele escura para quem prefere. O Arcade é o que eu deixaria por último: o cobalto se mistura com o céu e o contraste é o mais
  apertado. É gosto, e a escolha é sua. Custo de errar: baixo; é desenho.
- **PR-2. Uma pele clara:** o Zine quebra a decisão TM3 ("a pele é sempre escura"). Recomendo **aceitar a exceção para esta pele.** Custo
  de errar: médio. Todo trecho do jogo que supõe menu escuro precisa ser revisto; é o que torna o Zine o mais caro.
- **PR-3. As fontes novas:** Saira Stencil One (Estêncil) e Bungee (Arcade) não estão no guia. Recomendo **aceitar só a do modelo
  escolhido.** O Zine não pede fonte nova. Custo de errar: baixo; é uma fonte a mais para carregar.
- **PR-4. As cores:** os valores dos tokens de cada modelo são novos e PROPOSTOS; no Zine e no Arcade as cores de sentido mudam de tom
  para funcionar como fundo. Recomendo **aceitar como ponto de partida** e medir o contraste na tela, no código. Custo de errar: baixo.
- **PR-5. A pele nova ao lado das de hoje:** recomendo que ela **entre como mais uma opção em Ajustes › Visual,** com o Vidro continuando
  o padrão até você decidir trocar. A outra opção é substituir uma das duas. Custo de errar: baixo.

- **PR-6. O desenho do DigiBrain na pele clara** (da rodada 2): recomendo que **o desenho da rede fique escuro nas duas peles,** como
  conteúdo (igual ao habitat), numa moldura da pele. No Zine ele vira uma foto escura colada no papel. A outra opção é redesenhar a rede
  em tinta sobre papel. Custo de errar: médio; redesenhar a rede é trabalho no scan, não na pele.

## 7. A rodada 2: as outras telas nos dois modelos escolhidos (2026-11-20)

Depois da escolha ("Zine e Estêncil"), mais cinco telas em cada um dos dois, para o código ter de onde partir. O conteúdo vem de
capturas do jogo de 2026-11-20.

| a tela | o que testa |
|---|---|
| **Ajustes** e a parte **Exibir** | a linha com seta, a linha com chave, a marca de novo, o volume |
| **Lutar › Arena** | duas escolhas de uma só (o rival, o mapa), a aba trancada, um botão principal |
| **Diário › Registro** | a leitura de texto corrido: linhas finas com hora, ícone e seta; os filtros |
| **o DigiBrain aberto e um chamado** | o conteúdo escuro dentro da pele; o cartão mais urgente da tela |
| **os estados** | cada peça parada: normal, com o mouse, pressionada, com o foco, desligada, escolhida, trancada |

**O que a rodada fixou no desenho:**
- **O escolhido nunca depende só da cor.** No Zine ele vira anil, entorta e ganha o adesivo do visto; no Estêncil vira osso e ganha a
  barra vermelha.
- **A linha de quem fez:** no Registro, a linha do que o dono fez tem um fundo e uma marca; as do pet não.
- **A marca de novo:** tracejada no Zine (como hoje); uma barra âmbar no Estêncil.
- **Os estados:**
  - no Zine, com o mouse o recorte sobe 2 px e a sombra cresce; pressionado, encosta no papel e a sombra some;
  - no Estêncil, com o mouse o fundo clareia e entra um traço de osso; pressionado, o botão afunda 2 px;
  - nada pisca nem gira; a troca leva 80 ms (o tempo do guia) e vira corte com o movimento reduzido.
- **O foco:** um contorno de 3 px, anil no Zine e branco no Estêncil.

**Um achado para o código (Estêncil):** as peças de canto cortado ou inclinadas são recortadas, e o recorte come o contorno de foco do
navegador. No desenho o foco vai por dentro nas peças de canto cortado, e vira duas barras (em cima e embaixo) na aba. No código isso
pede uma regra de foco por tipo de peça, e não uma só para tudo.

## 8. As etapas de código (PROPOSTAS; liberadas com as PR-2 a PR-6, em 2026-11-20)

Um PR por etapa. O custo é a leitura dos arquivos de pele de hoje, não uma medida.

| etapa | o que entrega | custo |
|---|---|---|
| **PE1** | a porta: os dois ids novos em `pele.ts`, os blocos de tokens e os cartões de escolha em Ajustes › Visual. O Vidro segue o padrão | baixo |
| **PE2** | o Estêncil inteiro (o arquivo de forma), com as capturas das telas e os estados | médio |
| **PE3** | o Zine, parte 1: a pele clara. Os tokens e a revisão de todo trecho que supõe menu escuro | alto |
| **PE4** | o Zine, parte 2: a forma (o traço, o giro, a fita, a retícula) e os estados | médio |

O Estêncil vem primeiro porque é escuro como as peles de hoje e exercita a porta sem o risco da pele clara.

## 9. O que não foi feito

- Sete telas por modelo escolhido. Conversar, as outras abas dos lugares, as telas que abrem sozinhas (a evolução, o ovo, a luta) e a
  conta não foram desenhados.
- Os estados estão desenhados parados; o movimento entre eles não.
- As telas da rodada 2 só a 1920; no celular, só a tela do pet e a folha de um lugar.
- O celular foi desenhado a 390; a 360 não foi conferido.
- Nenhum revisor viu a prancha, e o contraste foi calculado, não medido.
- O custo do filtro do traço tremido do Zine no jogo, com a ilha 3D rodando.
- O fundo da tela do lugar é o mesmo da tela do pet; no jogo a câmera vai ao saco de pancada.

---

## 10. A Estêncil no jogo, com a forma do desenho (2026-11-20, Gerente da UX_TELA_PET, Claude Code, Fable 5.2, branch `v3-ux-peles-pe1`)

**De onde vem:** a primeira versão no jogo trazia só as cores da pele. O Matheus viu e pediu (2026-11-20): "eu quero que você analise o
desenho que você fez e tente replicar o mesmo desenho que você fez de layout no jogo, porque tem diferenças bem graves entre o que você
considerou que os itens estavam no jogo e o que realmente está. Quero que seja bem similar." Depois da segunda tentativa, disse que
parecia "literalmente os layouts que já tinha antes, só que com uma outra tonalidade", e pediu: "eu quero que você gere uma sessão
revisora, e daí quando finalizar de desenhar, pede para a sessão revisora analisar se está igual à prancha." Perguntado se o incômodo
era o jogo ou a prancha, respondeu: "O jogo não bate".

Esta seção é a resposta: a forma do desenho escrita sobre a estrutura real do jogo, conferida por uma sessão revisora em rodadas. As
etapas PE1 e PE2 da seção 8 saem juntas, num PR só.

**O lado a lado** (o desenho em cima, o jogo embaixo) está em `docs/pranchas/ux-peles-rua/capturas_codigo/`: `lado_a_lado_*.jpg` (a
tela do pet, um lugar, Lutar, Diário, Ajustes e o DigiBrain). As capturas do jogo estão na mesma pasta (`estencil_*.jpg`).

### 10.1 O que entrou

- **A porta:** o terceiro id de pele, `estencil` (`web/app/src/pele.ts`). Vale pelo endereço (`?pele=estencil`) e pelo terceiro cartão de
  Ajustes › Visual, com a etiqueta "prévia". **O padrão continua sendo o Vidro.**
- **Os tokens** (`estilo/tokens.css`, o bloco `:root[data-pele="estencil"]`): a tinta, o osso e o vermelhão; a letra vazada dos títulos
  (`--hx-f-tit`, a Saira Stencil One, carregada no `index.html` junto das outras); a cor da sombra dura; os segmentos das barras; as
  duas cores do mapa do minimapa; e as cores da rede do DigiBrain.
- **A forma** (`estilo/pele-estencil.css`), peça por peça:
  - **a caixa:** contorno de osso de 2 px, canto de cima à direita e de baixo à esquerda cortados, sombra dura. Vale no topo, no
    trilho, nas janelas, no aviso, nas ações, no minimapa, no painel dos lugares, no DigiBrain e na placa do lugar;
  - **o topo:** o nome do pet na letra vazada; o "agora" com o rótulo num bloco de vermelhão; a marca numa placa com a sombra de
    vermelhão entre duas riscas, fixa no centro da tela; o dia pequeno em cima da hora grande;
  - **as janelas:** o índice em vermelhão (01, 02…, a ordem delas na pilha), o título na letra vazada, as barras em segmentos;
  - **o aviso do meio:** do tamanho do texto, com o ícone em traço e o "Estado" num paralelogramo. Quando o pet pede algo, a caixa vira
    a cor da necessidade. O chamado é o cartão rosa com o botão de tinta;
  - **as ações de baixo e os exercícios:** ícones em traço, na cor do texto;
  - **o minimapa:** oito lados, com o mapa em esquema (a água some no fundo, a terra em tinta clara, a costa em osso);
  - **os painéis:** o ícone num ladrilho de vermelhão, o título grande, as abas e os botões em paralelogramo, o botão principal com o
    contorno de osso, os cartões de canto cortado (o escolhido em osso com a barra de vermelhão), a chave em retângulo, o volume com o
    losango, a linha do dono no Registro com fundo e marca, o botão de perigo riscado;
  - **os estados:** com o mouse o botão sobe e ganha a sombra, e a opção clareia e ganha um traço; pressionado, afunda e escurece; o
    foco tem 3 px, por dentro nas peças de canto cortado e em duas barras na aba;
  - **o celular:** o retrato, o relógio, os destinos e as ações na caixa pequena (corte de 9 px, sombra de 4 px), com as ações em
    tinta; a folha de um lugar em duas colunas.

### 10.2 O que mudou fora do CSS

A regra das peles é não mudar a estrutura (o DOM). Entraram ganchos que não mudam nada nas outras peles:
- `data-pede` e `data-acao` no aviso do meio; `data-acao` em cada ação de baixo; `data-ex` em cada cartão de exercício;
- `data-tipo` em cada linha do Registro (a linha do dono depende dele);
- o "%" do medidor num `span` próprio (`hx-medidor__pct`), que esta pele esconde nas necessidades.

E dois trechos de tela que leem a pele:
- **o Minimapa** pinta o mapa em esquema quando a pele define `--hx-mapa-terra` (só a Estêncil define). A conta é pura
  (`esquemaDoMapa`, em `telas/pet/minimapaGeo.ts`, com teste); a vista publica a cor da água junto do mapa;
- **o retrato da Arena** entrega o sprite recortado nesta pele, para encher o quadro; nas outras, o quadro inteiro, como antes.

O motor, o save, as rotas e os gabaritos não mudaram.

### 10.3 A revisão independente

A sessão revisora ("Revisão da pele Estêncil contra a prancha") montou a lista de conferência **só pela prancha, antes de ver o jogo**
(73 itens), e depois comparou as capturas do jogo com as da prancha, peça por peça, com recortes lado a lado e medidas de pixel. Ela
não mexeu no repositório; eu corrigi o que ela apontou e pedi nova rodada.

| | rodada 1 | rodada 2 | rodada 3 | rodada 4 | rodada 5 | rodada 6 |
|---|---|---|---|---|---|---|
| igual | 22 | 52 | 60 | 59 | 62 | 63 |
| parecido, a consertar | 23 | 11 | 5 (margens) | 4 (medidas) | 1 | 0 |
| parecido, só por decisão do Matheus | 8 | 9 | 8 | 10 | 10 | 10 |
| diferente | 11 | 1 | 0 | 0 | 0 | 0 |
| não conferido | 9 | 0 | 0 | 0 | 0 | 0 |

- **A rodada 1** confirmou o que o Matheus viu: no celular e nas telas sem prancha era "o layout de antes com outra tonalidade"; no
  computador, nas telas com prancha, já era a prancha, com diferenças de medida e de acabamento.
- **A rodada 3:** "nas telas que a prancha desenhou, o jogo agora bate com a prancha na forma de todas as peças". Sobraram cinco
  margens, de 6 a 22 px.
- **A rodada 4:** as cinco margens e o foco do fechar ficaram iguais. Ao medir a caixa de todas as peças, ela achou quatro sobras que
  não tinham sido medidas (o DigiBrain 8 px à direita das janelas, a altura do chamado, as ações do celular e a largura dos Bits).
- **A rodada 5:** as quatro sobras ficaram iguais: 62 de 73 itens iguais, 10 por decisão do Matheus e 1 a consertar (o espaçamento de dentro do DigiBrain). Esse último e o topo dos painéis alinhado com o trilho (uma recomendação dela) foram acertados depois da rodada.
- **A rodada 6:** "os três pontos estão resolvidos, e não sobra nenhum conserto na lista": 63 de 73 itens iguais e 10 por decisão do Matheus.
- **Os relatórios** (a lista, as seis rodadas e os recortes) estão fora do git, em `D:\Trab\digilab\capturas_ux_peles_rua\revisao\`,
  com um resumo no vault (`10 Auditoria/Revisão da pele Estêncil contra a prancha 2026-11-20`).
- **O limite dela:** foi medida por pixel a caixa de fora de cada peça fixa da HUD; o espaçamento de dentro dos painéis foi julgado
  pela forma, pela letra, pela cor e pela ordem das peças, não por pixel.

### 10.4 As decisões que ficam com o Matheus

A revisora separou dez itens que só não estão "iguais" porque o jogo tem uma peça ou um dado que a prancha não desenhou. Em todos
ficou o que o jogo tem; ela recomenda manter os dez:
- os ícones do jogo (trilho, janelas, Bits, abas) no lugar dos do kit da prancha;
- o brasão no cartão do pet; o "Detalhes" na janela do Estado; a seta das janelas fechadas na ponta direita; o "Reserva" em Alimentar;
- o "N" e os ícones dos lugares no minimapa;
- a posição e a largura dos painéis dos lugares (à direita, o layout do jogo);
- a Arena sem a etiqueta do nível ao lado do pet (o jogo não mostra o nível ali);
- no celular, os Bits junto do relógio, e a necessidade como etiqueta em cima do pet (o jogo não tem o aviso do meio no celular).

**Trocas que só valem nesta pele, feitas para seguir o desenho** (cada uma é uma regra; voltam com a retirada dela): os ícones em
traço no lugar das figuras das ações, dos exercícios, do aviso e do chamado; o sol do relógio escondido e um quadrado no lugar da
nuvem do "salvo"; o nome de todas as abas à vista no computador; o "%" das necessidades escondido; o rótulo "Arena" repetido fora da
vista; e o rótulo "Treino" acima do estado, em Crescer.

### 10.5 Como foi conferido

- **Capturas do jogo a 1920 × 950** e no celular (390 × 844), e os estados (com o mouse, pressionado, com o foco) recortados em volta
  de cada peça. As mesmas telas foram capturadas no Militar, do mesmo build, para a revisora separar o que é do jogo do que é da pele.
- **Testes:** `npm run tipos` limpo; `npm test` com 212 arquivos, 2173 passam e 3 pulam; `npm run e2e` (porta 8811, 2 workers) na árvore com a `main` juntada: 145 passam e 2 falham, os dois antigos e sem relação com a pele (`jogo.spec.ts:339` e `:378` esperam a versão 9 do registro do Tamer e recebem a 11). Depois dele entraram só acertos de CSS da pele (as rodadas 4 e 5); no build final rodaram de novo os testes da pele (`e2e/pele_estencil.spec.ts`), que passam.

### 10.6 O que não foi feito

- **As telas que a prancha não desenhou** (Crescer › Aprendizado e Evolução, Conversar, o painel do porquê, Ajustes › Visual) têm a
  moldura da pele, mas o miolo é o de antes nas cores novas. Para ficarem Estêncil precisam de desenho.
- **Não olhadas com esta pele:** as outras abas (Itens, Exploração, Fronteira, Medalhas, Catálogo, Gerações, Cenários), as telas que
  abrem sozinhas (as boas-vindas, o ovo, a evolução, a luta e o resultado), a conta e o "Meus pets".
- O celular a 360 px. O Zine (PE3 e PE4).
- O custo da sombra (um `drop-shadow` por caixa) não foi medido, nem no celular.
- O portão das capturas de referência (`npm run capturas`) não foi rodado.
- A etiqueta "prévia" do cartão continua: sai quando o Matheus disser que a pele está pronta.

---

## 11. O Zine no jogo (PE3 e PE4), e a conferência do Vidro e do Militar (2026-11-20, Gerente da UX_TELA_PET, Claude Code, Fable 5.2, branch `v3-ux-peles-pe3`)

**De onde vem:** com a Estêncil no PR #1054, o Matheus pediu (2026-11-20): "Agora eu quero que você revise tanto as pranchas que eram
do vidro quanto as que eram do militar [...] e veja se está alinhado com o que está no jogo, o que estava proposto nas pranchas. E
também já aplique um novo template também chamado Zine, aquele lá em cima das pranchas, né? Desenvolva as pranchas para ele também e
passe pelo revisor para bater frente a frente com as pranchas."

**O lado a lado** (o desenho em cima, o jogo embaixo) está em `docs/pranchas/ux-peles-rua/capturas_codigo/`:
`lado_a_lado_zine_*.jpg` (a tela do pet, um lugar, Lutar, Diário e Ajustes), com as capturas do jogo (`zine_*.jpg`).

### 11.1 O que entrou

- **A porta:** o quarto id de pele, `zine` (`web/app/src/pele.ts`), por `?pele=zine` e pelo quarto cartão de Ajustes › Visual, com a
  etiqueta "prévia". Os cartões de pele passam a duas colunas. **O padrão continua sendo o Vidro.**
- **Os tokens** (`estilo/tokens.css`, o bloco `:root[data-pele="zine"]`): o papel creme, a tinta no traço e no texto, o anil no
  escolhido e nos medidores, o amarelo-fita na ação; as cores de sentido próprias da pele; Barlow no texto e Rubik nos títulos e nos
  números (a Rubik reta 800 e 900 passa a ser carregada junto da itálica).
- **A forma** (`estilo/pele-zine.css`):
  - **o recorte:** o papel, o traço de tinta de 3 px e a sombra dura são o `::after` de cada peça, pelo filtro do corte à mão (o
    `<filter id="rabisco">`, que entrou no `index.html`); cada peça gira um pouco, com o giro da prancha;
  - **a fita amarela** no cartão do pet, na primeira janela, no minimapa, nos painéis e no DigiBrain;
  - **o topo, o trilho e as janelas:** a marca numa tira de tinta com a sombra amarela; o destino atual num adesivo anil; as janelas
    com a tira preta do título e o índice num quadradinho amarelo torto; as barras com traço e o miolo anil riscado;
  - **os painéis:** a tira preta do cabeçalho, as abas de fichário (a escolhida amarela e mais alta), o destaque amarelo com
    retícula, os cartões como recortes tortos, os botões retos com sombra, a opção escolhida em anil com o adesivo do visto;
  - **o minimapa** quadrado, com o mapa em esquema (a água anil, a ilha de papel, a costa de tinta);
  - **o DigiBrain:** a moldura de papel, com a rede escura por dentro, como uma foto colada (PR-6);
  - **o celular:** o retrato e as ações em amarelo, os destinos como recortes tortos, o atual em anil.
- **A regra da pele clara:** a cor de sentido (necessidade, aprendido, alerta, perigo, ok) é sempre um fundo com texto de tinta, nunca
  a cor da letra. O teste confere o contraste da tinta sobre cada uma.

### 11.2 O que mudou fora do CSS

- o filtro `rabisco`, um `<svg>` sem tamanho no `index.html` (só o Zine o usa);
- o Minimapa lê mais um token, `--hx-mapa-agua` (a cor do fundo do mapa em esquema);
- o retrato da Arena recortado vale também para o Zine;
- o volume de Ajustes passa a porcentagem num atributo de estilo (`--vol`), para a pele pintar o trilho até o cursor;
- em Ajustes › Visual, a frase "Os menus são sempre escuros" vira "Os menus seguem a pele" quando a pele é o Zine.

### 11.3 A revisão independente do Zine

A mesma sessão revisora, do zero: 75 itens tirados só da prancha (os 73 da Estêncil mais o giro e o traço, e a leitura na pele
clara), antes de ver o jogo.

| | rodada 1 | rodada 2 | rodada 3 |
|---|---|---|---|
| igual | 52 | 65 | 66 |
| parecido, a consertar | 16 | 2 (leves) | 0 |
| parecido, só por decisão do Matheus | 7 | 8 | 9 |
| diferente | 0 | 0 | 0 |

- **A rodada 1:** "o jogo é a prancha, mas ainda não está igual". O mais grave: o traço e a sombra do minimapa em anil, as abas de
  Lutar saindo do painel, e, no celular, a etiqueta da causa fora do balão. Os estados passaram todos, e ela não achou texto claro
  sobre o papel nem cor de sentido usada como letra, fora uma frase errada ("Os menus são sempre escuros").
- **A rodada 2:** os 16 consertos resolvidos; os 17 giros medidos batem com a prancha. Sobraram dois acertos leves (a moldura do
  minimapa 7 px maior e um contorno nos botões do DigiBrain).
- **A rodada 3:** "não sobra nenhum conserto na lista do Zine": 66 de 75 itens iguais e 9 por decisão do Matheus. Os botões do
  DigiBrain passaram a igual; no minimapa a caixa bate, e dele sobra só a decisão sobre o desenho do mapa.
- **As nove decisões do Matheus,** as mesmas da Estêncil (seção 10.4): os ícones do jogo, o brasão, o "Detalhes", o "Reserva", o mapa
  com o "N" e os ícones dos lugares, a posição e a largura dos painéis, a etiqueta do nível na Arena, os Bits junto do relógio no
  celular e o celular sem o aviso do meio. Em todas ficou o que o jogo tem.
- **Os relatórios** estão fora do git, em `D:\Trab\digilab\capturas_ux_peles_rua\revisao_zine\`, com um resumo no vault
  (`10 Auditoria/Revisão da pele Zine contra a prancha 2026-11-20`).

### 11.4 A conferência do Vidro e do Militar contra as pranchas

As pranchas das duas peles antigas estão fora do git, num canvas privado do Matheus (a série D; `docs/TAREFA_V2_LAYOUT_HABITAT.md`,
seção 1). A revisora leu o canvas, montou uma lista por pele e comparou com capturas do jogo a 1536 × 1024.

| | Vidro | Militar |
|---|---|---|
| igual | 6 | 3 |
| parecido | 15 | 18 |
| diferente | 22 | 22 |
| não conferido | 13 | 13 |
| itens em que a diferença é mudança de propósito, com decisão registrada | 28 | 32 |
| itens com algum desalinhamento | 9 | 8 |

- **A pele das duas bate com a prancha;** a cor mudou na refeitura das peles, aprovada em 2026-10-31.
- **A estrutura das telas é outra, de propósito:** o HUD da tela Pet, os menus como lugares da ilha, o celular mínimo e a luta em
  tempo real vieram depois da série D. A referência de hoje para as telas são as pranchas novas do repositório.
- **Os desalinhamentos** (sem decisão achada), do mais grave ao menos: Conversar (os modos no corpo, sem a coluna de apoio); a cor das
  barras e dos ícones das necessidades (por estado, e não por necessidade; os dois documentos do repositório se contradizem); as cinco
  ações de Gerações fora da aba; o botão principal (Vidro) e o fechar (Militar); a chave dos Ajustes como caixa de marcar; e o filtro
  "falas" do Registro, que a prancha propôs e o jogo não tem.
- **Nada disso foi corrigido neste PR:** é uma decisão do Matheus. Os de pele (as necessidades, o botão e o fechar, a chave) cabem num
  PR pequeno por pele; os de tela (Conversar, Gerações, o filtro) mexem no que o jogo mostra.
- **O limite:** o jogo não foi conferido contra as pranchas novas do repositório; 13 itens por pele ficaram sem conferir (o menu Mais,
  Itens e Fronteira trancados no save, dois modos do Conversar e as nove telas que abrem sozinhas).
- **Os relatórios** estão fora do git, em `D:\Trab\digilab\capturas_ux_peles_rua\pranchas_d\`, com um resumo no vault
  (`10 Auditoria/Conferência do Vidro e do Militar contra as pranchas D 2026-11-20`).

### 11.5 Como foi conferido

- **Capturas do jogo** a 1920 × 950 e a 390 × 844, e os estados recortados em volta de cada peça.
- **Testes:** `npm run tipos` limpo; `npm test` com 212 arquivos, 2178 passam e 3 pulam; o e2e inteiro no build final (porta 8811, 2 workers): 147 passam e 2 falham, os dois antigos e sem relação com a pele (`jogo.spec.ts:339` e `:378` esperam a versão 9 do registro do Tamer e recebem a 11).

### 11.6 O que não foi feito

- **As pranchas do Zine são as nove que já existiam** (o pet, um lugar, o celular, a folha, Ajustes, Lutar, Diário, o DigiBrain e os
  estados). Nenhuma prancha nova foi desenhada: as telas sem prancha (Crescer › Aprendizado e Evolução, Conversar, o painel do porquê,
  Ajustes › Visual) pegaram o papel, a tira do cabeçalho e as cores, e leem bem, mas o miolo é o de antes.
- **Não olhadas com esta pele:** as outras abas (Itens, Exploração, Fronteira, Medalhas, Catálogo, Gerações, Cenários), as telas que
  abrem sozinhas, a conta e o "Meus pets". Numa pele clara, é onde pode haver texto claro sobre papel.
- O custo do filtro do corte à mão com a ilha 3D rodando não foi medido. O celular a 360 px.
- O portão das capturas de referência (`npm run capturas`) não foi rodado.
- As etiquetas "prévia" das duas peles continuam.
