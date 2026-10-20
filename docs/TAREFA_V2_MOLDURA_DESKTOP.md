# TAREFA V2 — MOLDURA-DESKTOP (2026-10-20)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-moldura-desktop`. Status: ENTREGUE (PR, espera o ok visual e o merge).

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

## 9. Entregue (2026-10-20)

**O que mudou (só a partir de 1100 px).**
- **`src/componentes/Nav.tsx`:**
  - o bloco do logo (as três barras, "DIGILAB" em Pixelify Sans e a legenda);
  - os ícones de traço do lucide (PawPrint, Sprout, Swords, BookOpen, MessageCircle e Settings) e a seta dos cards do pé.
  - São elementos `desk-so`: abaixo de 1100 px ficam escondidos, e a barra é a de antes.
- **`src/componentes/Topo.tsx`:** o topo numa linha só.
  - À esquerda, as abas da tela (a tela sem abas mostra o título como a aba ativa; um `h1` só para leitor de tela quando há abas) e o
    Voltar.
  - Os botões da tela.
  - À direita, o relógio (sol ou lua, do motor), o "salvo" e o pet: o retrato redondo da prancha, o nome, o nível e o brasão.
  - O logo saiu do topo, e a linha de página (título e abas) subiu para ele.
- **`src/App.tsx`:** o conteúdo de toda tela dentro de `div.moldura`, o painel de cantos cortados. Abaixo de 1100 px o envoltório é
  `display:contents` e não muda nada. O topo não tem mais o `semTitulo`: a tela Pet mostra "Pet" como a aba ativa, como na prancha.
- **`src/estilo/desktop.css`:**
  - a barra lateral escura do topo ao fundo, com a grade de 24 px, os estilhaços e o canto cortado;
  - o topo;
  - o painel (borda e fundo em duas camadas recortadas, o traço azul no canto);
  - o fundo da página com a grade de 48 px e os estilhaços.
  - Tudo pelos tokens `--ui-*`.
- **`src/estilo/tokens.css`:** `--ui-topo` passou de 64 para 84 px e `--ui-lateral` de 208 para 230 px (a prancha). O novo
  `--ui-moldura-v` (54 px) é o que o painel ocupa na vertical; a tela Pet, a Conversa e as telas `.tela.desk` descontam dele a altura.
- **`index.html`:** a fonte Pixelify Sans (só no logo).
- **`e2e_capturas/telas.spec.ts`:**
  - espera a cena 3D da tela Pet subir antes de o relógio andar; antes, o pet saía num quadro ou noutro;
  - `DIGILAB_CAPTURAS_LARGURAS` escolhe as larguras (360 incluída);
  - `DIGILAB_CAPTURAS_RESERVA=1` tira o atlas e a decoração do UP, para as capturas que vão para o repositório.

**Gate.**

| conferência | resultado |
|---|---|
| `npm run tipos` | passa |
| `npm test` (Vitest) | 43 arquivos, 507 testes, todos passam |
| `npm run e2e` | 74 de 74 (inclusive os layouts de 390, 899, 900, 1099, 1100 e 1280 px) |
| `npm run capturas`, 390 px (referência: a `main` em `6099ca3`) | 15 de 15 iguais, pixel a pixel |
| `npm run capturas`, 360 px (`DIGILAB_CAPTURAS_LARGURAS=360`; referência tirada do build da `main`) | 15 de 15 iguais, pixel a pixel |
| `npm run capturas`, 1280 px | as 15 mudam, que é o pedido |

O antes e o depois de cada tela em 1280 estão em `docs/estilo_up/pranchas/capturas/Moldura_<tela>.png`, lado a lado. São 15 imagens,
sem o atlas e sem a decoração do UP.

**O que ficou para depois.**
- O conteúdo ficou mais estreito: a lateral tem 22 px a mais, e o painel tem margem e respiro.
- Na Arena, o bloco "lutas de treino" (que já era apertado) encosta na coluna das regras. O miolo das telas é de outra tarefa; cada tela
  ajusta o dela quando chegar a vez.
