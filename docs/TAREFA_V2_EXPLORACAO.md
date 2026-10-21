# TAREFA V2 — EXPLORACAO (2026-10-21)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-exploracao`, a partir da `main` (59d8e4b). Status: ENTREGUE (PR, espera o ok visual e o merge).

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
- O nome da aba passa a "Exploração" (`NOME_ABA.campanha`). A rota, o id da aba e o save não mudam.
  - Os textos que apontam a aba passam a dizer "Exploração": a ajuda da Arena e a da carta em Crescer › Itens.
  - A palavra "campanha" continua nos textos que falam da sequência de lugares.
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

## 9. Entregue (2026-10-21)

**O que mudou.**
- **`src/telas/lutar/mapaLayout.ts` (novo, puro):** onde fica cada ilha, o cartão dela e o marcador, em px da caixa do mapa.
  - **Celular:** duas colunas em zigue-zague, a ilha com 37% da largura e o cartão do outro lado, centrado na altura dela. A altura do mapa
    sai da largura, e a página rola (7 ilhas em 390 px: 1.084 px).
  - **Desktop:** fileiras que vão e voltam, com o cartão embaixo da ilha. Prova 2, 3 e 4 colunas e fica com a que dá a maior ilha que cabe
    na caixa. Numa janela baixa (como 1280 × 720), a ilha fica com 90 px e a caixa rola, começando no marcador.
- **`src/telas/lutar/mapa3d.ts` (novo, chunk próprio):** a vista isométrica (câmera ortográfica de (1, 1, 1)).
  - Cada ilha tem um tampo de 7 × 7 voxels sem os cantos e embaixo a terra e a rocha afinando. Por cima, o tema do lugar (seção 3).
  - As faces são coloridas sem luz (a de cima clara, as dos lados mais escuras), numa geometria só, com a cor no vértice.
  - As trancadas ficam cinzentas, puxadas para o azul. O trilho é de tracinhos entre os tampos, azul onde o lugar de baixo foi vencido.
  - O centro de cada tampo cai no ponto que o `mapaLayout.ts` deu (o raio da câmera cruzando o plano do tampo), e os cartões HTML ficam
    no lugar certo.
  - O mapa é parado e desenha de novo só quando a caixa ou o motor mudam.
- **`src/telas/lutar/MapaExploracao.tsx` (novo):** a caixa medida, a vista 3D por import dinâmico, os cartões e o marcador.
  - Os lugares saem de `m.lugares`, mais a Fronteira nos pets v6 em diante.
  - **Situação de cada lugar:** vencido (as vitórias), aberto ("sugerido: <nível>") ou trancado ("vença alguém em <anterior>").
  - **Fronteira:** "abre com as 6 medalhas (k de 6)", "a Liga dos Líderes está aberta" ou "campeão da Liga dos Líderes".
  - **Selo:** o da medalha do líder (cheio se o Tamer tem); na Fronteira, o de ouro.
  - **Marcador:** fica no próximo desafio (`campProximoLugar`), ou na Fronteira aberta com a campanha vencida, com o rótulo "próximo
    desafio". Com tudo vencido e sem Fronteira aberta, o rótulo é "campanha vencida".
  - Se a vista 3D não sobe, a tela cai no mapa 2D.
- **`src/telas/lutar/TelaCampanha.tsx`:**
  - Sem WebGL, fica a tela de antes (`CampanhaReserva`).
  - Com WebGL, a `TelaExploracao`: no celular o cartão abre a `Folha` com o `Detalhe` de antes; no desktop o lugar fica na lateral (o
    `DetalheDesk` de antes).
  - O "Como funciona" virou um componente, igual nos dois.
- **O resto:**
  - `src/webgl.ts`: o `temWebGL` da tela Pet, agora usado pelas duas telas.
  - `src/rotas.ts`: "Exploração".
  - `src/decoracao.ts`: sem a faixa `campina_gazimon`.
  - Os textos da Arena e dos Itens que apontam a aba.
  - `src/estilo/lutar.css`: o mapa, os cartões, o marcador e a folha. No desktop, a coluna do lugar tem de 300 a 370 px.
- **A faixa da Campina:** a decoração local `campina_gazimon` tem um pergaminho com glifos orientais e saiu de `FUNDO_NPC`. Com isso a
  Campina fica sem faixa no cartão do lugar e sem fundo ilustrado na luta contra o Gazimon. A lista `decoracao_nomes.json` não mudou:
  `tests/test_servidor_remoto.py` confere esse nome nela.

**Gate.**

| conferência | resultado |
|---|---|
| `npm run tipos` | passa |
| `npm test` (Vitest) | 44 arquivos, 539 testes, todos passam; os 32 novos são de `test/mapa_exploracao.test.ts`, com 3, 4 e 7 ilhas no celular (360 a 899 px) e em 5 caixas de desktop: nenhum cartão sobre outro ou sobre outra ilha, nenhuma ilha sobre outra, tudo dentro da caixa |
| `npm run e2e` | E2E_FINAL |
| `npm run capturas`, 390 e 1280 px (referência: o build da `main` 59d8e4b) | 11 telas iguais, pixel a pixel; mudam `lutar-campanha` (o pedido) e `lutar-arena`, `lutar-fronteira` e `lutar-medalhas`, só no nome da aba |
| `npm run capturas`, 360 px (mesma referência) | o mesmo: 11 iguais, 4 de Lutar mudam |
| captura nova `lutar-exploracao-v6` (390 e 1280) | sem referência da `main` (é nova); gravada no branch e conferida de novo, igual |
| determinismo do branch | gravado e conferido de novo nas 48 capturas (390, 1280 e 360): todas iguais |

Notas do gate:
- O e2e da campanha foi ajustado à tela nova:
  - os 6 testes das seis ilhas (360, 390 e 1280, claro e escuro) conferem o mapa 3D, os cartões, o marcador, os alvos de 44 px e a folha
    no celular;
  - um teste novo confere a reserva sem WebGL;
  - os testes que lutam pela aba abrem a folha no celular.
- **As diferenças das outras abas de Lutar:** estão na faixa das abas, de 66 a 110 px no celular e de 34 a 66 px no desktop. A única
  exceção é `lutar-medalhas` em 390: tem também 4 pixels soltos no padrão do fundo, com 1/255 de diferença num canal. Os dois builds,
  rodados de novo, são estáveis.
- Uma rodada de conferência do branch teve 2 capturas instáveis com a máquina carregada; passaram na nova tentativa, e a rodada seguinte
  deu 32 de 32.

**As capturas** (em `docs/estilo_up/pranchas/capturas/`, sem o atlas e sem a decoração do UP; o pet v6 do e2e das arenas, com o Tamer de 3
medalhas):
- `Exploracao_390.png` e `Exploracao_360.png`: 390 × 844 e 360 × 800, rolados até o marcador;
- `Exploracao_1280.png`: o desktop;
- `Exploracao_390_folha.png`: a folha da Cidadela;
- `Exploracao_390_inteira.png`: a página inteira em 390.

A comparação lado a lado com a quarta tela da referência fica fora do repositório, porque a referência não é versionada.

**Diferenças para a referência.**
- As ilhas são mais simples (caixas de cor, sem textura) e menores, porque são 7 lugares e não 3.
- Os cartões não sobrepõem a ilha, para nunca tapar a vizinha.
- O cadeado é pequeno, na linha da situação.
- Não há nível numérico nem "???": o nível sugerido é o nome do Digimon, e todo lugar tem o nome do motor.

**O que ficou para depois.**
- No celular, o mapa de 7 ilhas é mais alto que a tela, e a página abre no alto (a Fronteira). Rolar até o marcador ao abrir mudaria a
  rolagem da página, e ficou de fora.
- No desktop de 1280 × 800, a ilha tem 100 px de largura (a caixa do mapa tem 546 × 622). O que limita é a altura que o marcador reserva
  entre as fileiras.
