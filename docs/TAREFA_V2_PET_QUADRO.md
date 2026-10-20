# TAREFA V2 — PET-QUADRO (2026-10-20)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-pet-quadro`, a partir da `main` com o #374. Status: ENTREGUE (PR, espera o ok visual e o merge).

Categoria: implementacao. Origem: Matheus, 2026-10-20, pelo Gerente. Na tela Pet do desktop, a coluna da direita vira o quadro modular
do protótipo: módulos que se arrastam entre as duas colunas e se recolhem; recolhidos, o habitat e as ações crescem.

## 1. Pergunta

A tela Pet do desktop pode ser montada em módulos arrastáveis e recolhíveis, só com o que o motor tem, sem mudar o celular, o motor, o
save nem o replay? Não vem de uma hipótese da pesquisa: é a interface do jogo.

## 2. Depende de

- A tela Pet nova com a cena 3D (#373, mergeada).
- A moldura nova do desktop (#374, mergeada).

## 3. Mudança mínima

**O quadro (`src/componentes/Quadro.tsx`, novo, sem conhecimento do jogo).** Duas colunas, a principal e a lateral. Cada módulo tem a alça
(GripVertical), o traço azul, o ícone e o título; à direita, o que a tela põe, o menu ⋮ (mover para cima, para baixo, para a outra
coluna) e o chevron de recolher. O cabeçalho do módulo se arrasta (drag and drop do HTML5) para outra posição ou para a outra coluna; o
menu é o caminho pelo teclado. A coluna lateral inteira também se recolhe.

**O arranjo é preferência de quem joga, não estado do jogo.**
- Fica no `localStorage`, na chave `digilab-web-v21-sprites-quadro-pet`, lido e gravado dentro de `try/catch`.
- Um arranjo gravado que não tenha exatamente os módulos de hoje volta ao padrão.
- Não entra no save, no log nem no replay; o motor não muda.

**Os módulos, só com dado do motor.**

| módulo | o que mostra | coluna padrão |
|---|---|---|
| Habitat | a cena 3D do #373 (com o cenário em CSS e SVG de reserva), o balão da fala e o da causa; é o maior bloco e cresce | principal |
| Ações | a necessidade prioritária e as ações | principal |
| Estado atual | as necessidades e a confiança; a emoção registrada à direita do título | lateral |
| Desejo | o desejo atual, ou "nenhum desejo agora" | lateral |
| Próxima evolução | a forma atual e o estágio que vem (a forma só quando o motor já a decidiu), o tempo até lá e o atalho para a árvore; sem nível nem XP. Sem próxima evolução, o módulo não aparece | lateral |
| Últimas ações | as últimas linhas do registro; "Ver tudo" leva ao Diário | lateral |
| DigiBrain | o painel do cérebro (só no pet v11) | lateral |
| Por que ele disse isso | o porquê da fala; começa recolhido, e o balão da fala o abre | lateral |

**O que não muda:**
- o celular (sem quadro nem arrastar: a folha "Como ele está" continua);
- as outras telas;
- o motor, o save, o replay e as rotas.

## 4. Gate

- `npm run tipos`, `npm test` e `npm run e2e` passam.
- e2e novo: arrastar um módulo para a outra coluna, mover pelo menu, recolher um módulo e a coluna lateral (o habitat cresce), recarregar
  e o arranjo voltar; o save não ganha chave.
- `npm run capturas`: em 1280 só as telas Pet mudam; as de 390 e as de 360 ficam iguais, pixel a pixel.

## 5. Entrega

- PR com o antes e o depois em 1280 e a prova de que 390 e 360 não mudaram. Depois, parar. Sem merge.
- O relato no corpo do PR e na seção 9 deste documento.

## 6. Fora desta tarefa

- O quadro nas outras telas.
- Arrastar no celular.
- Módulos sem dado no motor (nível, XP, missões e afins).

## 7. Critérios de aceitação

- No desktop, a tela Pet tem os módulos da seção 3, cada um com a alça, o menu, o chevron, o traço azul e o título com ícone.
- O arranjo sobrevive a recarregar e não toca no save.
- O gate da seção 4 passa.

## 8. Precisa do Matheus

O ok visual no antes e depois.

## 9. Entregue (2026-10-20)

**O que mudou (só a partir de 1100 px, só a tela Pet).**
- **`src/componentes/Quadro.tsx` (novo):**
  - o quadro de duas colunas e o `Modulo` (alça, traço azul, ícone, título, o que a tela põe à direita, o menu ⋮ e o chevron);
  - arrastar pelo cabeçalho do módulo (drag and drop do HTML5), com a linha azul de onde ele vai cair e a coluna vazia "Arraste um quadro
    para cá";
  - o menu (mover para cima, para baixo e para a outra coluna; fecha com Esc ou com um clique fora);
  - recolher cada módulo e a coluna lateral inteira;
  - o arranjo no `localStorage` (`digilab-web-v21-sprites-quadro-pet`), em `try/catch`; um arranjo que não tenha exatamente os módulos
    de hoje volta ao padrão.
- **`src/telas/pet/TelaPet.tsx`:**
  - a `TelaPetDesktop` monta os módulos da seção 3, cada um só com o que o motor tem;
  - a Próxima evolução usa a `previsaoEvo` da tela Evolução: o estágio que vem e o tempo até lá; a forma seguinte só quando o motor já a
    decidiu (o Mega); sem próxima evolução, na morte ou no ovo, o módulo não aparece;
  - o DigiBrain e o porquê da fala saíram dos botões da cena: viraram módulos;
  - o celular continua o mesmo (o botão DigiBrain na cena e a folha "Como ele está"). O `AgoraHaPouco` saiu: o registro do desktop é o
    módulo Últimas ações.
- **`src/App.tsx`:** o atalho da Próxima evolução para Crescer › Evolução.
- **`src/telas/pet/cena3d.ts`:** a cena se ajusta ao tamanho da caixa (`ResizeObserver`), e recolher a lateral faz o habitat crescer.
  - Em paisagem, a escala é fracionária e o quarto ocupa mais da caixa; a janela da parede cabe na parede visível.
  - Em retrato (o celular), tudo continua como antes.
  - Ao redimensionar, redesenha o mesmo quadro, sem avançar o contador.
- **`src/estilo/pet_home.css`:** o CSS do quadro e dos módulos, no bloco do desktop.

**Gate.**

| conferência | resultado |
|---|---|
| `npm run tipos` | passa |
| `npm test` (Vitest) | 43 arquivos, 507 testes, todos passam |
| `npm run e2e` | 76 de 76: os 74 de antes (os do Pet e do DigiBrain em 1280 ajustados ao quadro) e os 2 novos: arrastar, menu, recolher e o arranjo salvo; no celular não há quadro |
| `npm run capturas`, 390 px (referência: o build de `v2-moldura-desktop`, a mesma árvore da `main` depois do #374) | 15 de 15 iguais, pixel a pixel |
| `npm run capturas`, 360 px (mesma referência) | 15 de 15 iguais, pixel a pixel |
| `npm run capturas`, 1280 px | 13 de 15 iguais; mudam só `pet-estado` e `pet-v11`, que é o pedido |

Notas do gate:
- A referência de 360 foi tirada de novo do build da base: a antiga dava diferença em `crescer-evolucao` também no próprio build da base.
- `lutar-fronteira` em 1280 falhou uma vez com a máquina carregada e passou sozinha. O mapa do DigiBrain passou 3 vezes seguidas na
  repetição.

O antes e o depois em 1280 estão em `docs/estilo_up/pranchas/capturas/`, sem o atlas e sem a decoração do UP:
- `Quadro_pet-v11.png` e `Quadro_pet-estado.png`: a moldura do #374 e o quadro;
- `Quadro_pet-v11_recolhida.png`: o quadro e a coluna lateral recolhida, com o habitat e as ações maiores.

**O que ficou para depois.**
- Com a lateral aberta, o habitat em 1280 fica menor que no #374 (a coluna lateral leva 370 px). Recolher a lateral devolve a largura.
- Na coluna lateral de 370 px, os módulos de baixo (Últimas ações, DigiBrain) pedem rolagem em 800 px de altura.
