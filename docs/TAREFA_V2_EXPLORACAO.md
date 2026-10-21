# TAREFA V2 — EXPLORACAO (2026-10-21)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-exploracao`, a partir da `main` (59d8e4b). Status: EM ANDAMENTO.

Categoria: implementacao. Origem: Matheus, 2026-10-21, pelo Gerente. A referência é a quarta tela de
`D:\Trab\digilab\_ref\referencia_mobile_2026-10-19.png` (local, não versionada): o mapa isométrico de blocos 3D, o marcador, os cartões
das áreas e as áreas trancadas.

## 1. Pergunta

A aba Lutar › Campanha pode virar a tela Exploração da referência, com o mapa de ilhas em 3D, só com o que o motor registra e sem mudar
o motor, o save, o replay nem a rota? Não vem de uma hipótese da pesquisa: é a interface do jogo.

## 2. Depende de

- A moldura nova do desktop (#374) e a cena 3D da tela Pet (#373), mergeadas.
- O mapeamento enviado ao Gerente em 2026-10-21 e as decisões do Matheus no mesmo dia:
  1. recompor Lutar › Campanha na mesma rota `#/lutar/campanha`, sem mudar a barra;
  2. a aba passa a se chamar "Exploração";
  3. a vista é um mapa isométrico de ilhas de voxels procedurais, Three.js só como vista.

## 3. Mudança mínima

**O mapa (vista 3D, `src/telas/lutar/mapa3d.ts`, novo).**
- Three.js só como vista, no padrão do `cena3d.ts`: em chunk próprio, por import dinâmico, sem importar o `poc`.
- Uma ilha de voxels procedural por lugar, com o tema dele:
  - Campina: grama e flores;
  - Torre de pedra: a torre de pedra;
  - Floresta: as árvores;
  - Cidadela: a muralha escura;
  - Lago: a água;
  - Montanha Espiral: a montanha em degraus;
  - Fronteira: no alto, a plataforma da Liga.
- O trilho entre as ilhas; as trancadas ficam cinzentas.
- Nenhuma arte do UP no mapa: ele aparece também sem o atlas, e pode ir para as capturas do repositório.

**Por cima do mapa (HTML).**
- O marcador "próximo desafio" com o retrato do pet: o motor não tem a posição do pet, e o marcador é o primeiro lugar não vencido, ou a
  Fronteira quando ela está aberta e a campanha vencida.
- Um cartão ao lado de cada ilha, só com dado do motor:
  - o nome real;
  - aberto: "sugerido: <nível>";
  - trancado: o cadeado e "vença alguém em <lugar anterior>";
  - vencido: as vitórias;
  - nos pets v6 em diante, o selo da medalha do líder.
- Sem "Nv. 1-10", sem "???", sem tranca que o motor não tenha.

**Celular e desktop.**
- **Celular (abaixo de 1100 px):** o mapa ocupa a tela, e o cartão abre a folha do lugar, com o detalhe de hoje (rivais, arena,
  "Desafiar").
- **Desktop:** o mapa grande na coluna principal, e o lugar escolhido na lateral, como hoje.
- **Sem WebGL:** fica a tela de hoje inteira, com o mapa 2D e o detalhe.
- **Lugares por versão:** 3 (pets v1–v4), 4 (v5) e 6 mais a Fronteira (v6 em diante), com a Fronteira trancada ou aberta. O In-Training
  vê o mapa; o detalhe diz que ele ainda não luta.

**O resto.**
- O nome da aba passa a "Exploração" (`NOME_ABA.campanha`). A rota, o id da aba e o save não mudam. A palavra "campanha" continua nos
  textos que falam da sequência de lugares.
- A faixa da Campina (`campina_gazimon`, decoração local do UP) tem um pergaminho com glifos orientais e sai de `FUNDO_NPC`. O lugar fica
  sem faixa, como os outros sem faixa própria.

**O que não muda:** o motor, o save, o replay, a rota, as outras abas, fora o nome "Exploração" nas abas de Lutar.

## 4. Gate

- `npm run tipos`, `npm test` e `npm run e2e` passam. O e2e da campanha é ajustado à tela nova e soma:
  - o mapa 3D;
  - os cartões, que abrem a folha no celular;
  - a reserva sem WebGL.
- `npm run capturas`:
  - `lutar-campanha` muda (é o pedido);
  - as outras abas de Lutar mudam só no nome da aba;
  - o resto fica igual em 390, 360 e 1280;
  - entra a captura nova de um pet v6 com 6 lugares e a Fronteira.
- Capturas individuais em 390×844, 360 e 1280, lado a lado com a referência.

## 5. Entrega

- PR com as capturas e o relato no corpo. Depois, parar. Sem merge.
- O relato também na seção 9 deste documento.

## 6. Fora desta tarefa

- O mundo físico do motor (`motor/mundo.ts`): nenhum pet do jogo vive nele.
- Mudar a barra de navegação.
- As outras abas de Lutar, fora o nome da aba.

## 7. Critérios de aceitação

- Em `#/lutar/campanha`, a aba "Exploração" mostra o mapa 3D de ilhas com os cartões e o marcador.
- No celular, o cartão abre a folha do lugar; no desktop, o lugar fica na lateral.
- Sem WebGL, fica a tela de hoje.
- Nada na tela que o motor não tenha; nenhum caractere japonês.
- O gate da seção 4 passa.

## 8. Precisa do Matheus

O ok visual nas capturas.
