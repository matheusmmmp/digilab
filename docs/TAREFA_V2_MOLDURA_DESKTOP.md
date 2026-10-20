# TAREFA V2 — MOLDURA-DESKTOP (2026-10-20)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-moldura-desktop`. Status: EM ANDAMENTO.

Categoria: implementacao. Origem: Matheus, 2026-10-20, a recomendação aprovada depois da tela Pet (#373). Trocar a casca comum do desktop
pela moldura da prancha `TelasLayoutDesktop` (branch `v2-tela-pet`, já sem japonês e com os nomes do motor).

## 1. Pergunta

A casca do desktop (a barra lateral, o topo e a moldura do conteúdo) passa à da prancha sem mudar o miolo de nenhuma tela nem o celular?
Não vem de uma hipótese da pesquisa: é a interface do jogo.

## 2. Depende de

- A troca do front (React, Tailwind, shadcn e lucide), mergeada em #368 e #372.
- A tela Pet nova, mergeada em #373.
- A decisão do Matheus de manter as abas da tela no topo do desktop (2026-10-19).

## 3. Mudança mínima

**O que muda: só a moldura do desktop, a partir de 1100 px**, em `src/componentes/Nav.tsx`, `src/componentes/Topo.tsx`, `src/App.tsx` (o
envoltório do conteúdo) e `src/estilo/desktop.css`. O desenho é o da prancha:

| peça | como fica |
|---|---|
| barra lateral | escura (`--ui-navy`), com a grade e os estilhaços; no alto, o bloco claro de corte diagonal com o logo (três barras inclinadas, "DIGILAB" e "Digital Life · Data · AI · Evolution"); os destinos com ícone de traço (lucide) e rótulo, o ativo em azul de canto cortado; no pé, Conversar e Ajustes em cards com seta |
| topo | à direita da lateral: as abas da tela (maiúsculas, a ativa sublinhada; uma tela sem abas mostra o título como a aba ativa; Voltar quando a tela tem), os botões da tela, o relógio do jogo (sol ou lua, "dia N" e a hora), o "salvo" e o pet (retrato redondo, nome, nível e brasão), como na prancha |
| conteúdo | dentro de um painel de cantos cortados (o de cima à esquerda e o de baixo à direita, com o traço azul), sobre o fundo com a grade de 48 px e os estilhaços |
| coluna da direita | a das telas que já têm uma continua onde está, dentro do painel |

**O que não muda:**
- o miolo de cada tela, inclusive a tela Pet do #373;
- o celular e a faixa de 900 a 1099 px;
- o motor, o save, o replay e as rotas.

## 4. Gate

- `npm run tipos`, `npm run build`, `npm test` e `npm run e2e` passam.
- `npm run capturas`:
  - as 15 capturas de 1280 mudam (é o pedido), com o antes e o depois de cada uma;
  - as 15 de 390 ficam iguais, pixel a pixel;
  - as de 360 conferidas iguais à parte.

## 5. Entrega

- PR com o antes e o depois de cada tela em 1280, e a prova de que 390 e 360 não mudaram. Depois, parar.
- O relato no corpo do PR e na seção 9 deste documento.

## 6. Fora desta tarefa

- O miolo das telas no layout novo: cada tela tem a vez dela.
- O celular.
- O tema escuro além do que os tokens `--ui-*` já dão.

## 7. Critérios de aceitação

- No desktop, as telas têm a lateral, o topo com as abas e o painel da prancha.
- Nenhuma tela perde rota, aba, botão nem dado.
- O gate da seção 4 passa.

## 8. Precisa do Matheus

O ok visual no antes e depois.
