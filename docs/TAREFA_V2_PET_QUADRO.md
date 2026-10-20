# TAREFA V2 — PET-QUADRO (2026-10-20)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-pet-quadro`, empilhado sobre `v2-moldura-desktop` (#374). Status: EM ANDAMENTO.

Categoria: implementacao. Origem: Matheus, 2026-10-20, pelo Gerente. Na tela Pet do desktop, a coluna da direita vira o quadro modular
do protótipo: módulos que se arrastam entre as duas colunas e se recolhem; recolhidos, o habitat e as ações crescem.

## 1. Pergunta

A tela Pet do desktop pode ser montada em módulos arrastáveis e recolhíveis, só com o que o motor tem, sem mudar o celular, o motor, o
save nem o replay? Não vem de uma hipótese da pesquisa: é a interface do jogo.

## 2. Depende de

- A tela Pet nova com a cena 3D (#373, mergeada).
- A moldura nova do desktop (#374, aberto): este PR vai empilhado nele.

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

O ok visual no antes e depois, e o merge do #374 antes deste.
