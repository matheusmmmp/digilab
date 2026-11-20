# Plano de UX das peles de rua: três modelos base (2026-11-20)

**Status: PROPOSTO.** Sem código. A prancha está em `docs/pranchas/ux-peles-rua/` e espera a escolha do Matheus. As cores, as fontes e os
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

- **PR-1. Qual modelo segue:** recomendo **o Zine como o principal e o Estêncil como a opção escura.** O Zine é o que mais responde ao
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

## 7. O que não foi feito

- Só duas telas por modelo. Lutar, o Diário, os Ajustes, as telas que abrem sozinhas (a evolução, o ovo, a luta) e a conta não foram
  desenhados.
- Os estados de foco, de passar o mouse e de pressionar.
- O celular foi desenhado a 390; a 360 não foi conferido.
- Nenhum revisor viu a prancha, e o contraste foi calculado, não medido.
- O custo do filtro do traço tremido do Zine no jogo, com a ilha 3D rodando.
- O fundo da tela do lugar é o mesmo da tela do pet; no jogo a câmera vai ao saco de pancada.
