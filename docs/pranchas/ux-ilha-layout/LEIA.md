# Prancha: o layout da ilha inicial (2026-11-08)

O pedido do Matheus foi uma planta pensada para a ilha do pet: os objetos ficam "um do lado do outro", as árvores ficam longe do pet, não há
nenhuma árvore perto do ninho, e há "vários postes aleatórios, um monte de árvore aleatória". Esta prancha é só desenho e não muda nada no
jogo. A página para comparar as plantas é https://claude.ai/artifact/Tq149bn7Jmaq9btokYVavK.

## Os arquivos

- `planta_hoje.png`: a ilha de hoje, vista de cima. Sai dos dados do jogo (`ilha_mvp.json`, a `ilhaDe(CMU_MVP)` de
  `web/app/src/telas/pet/ilha/grade.ts`, tirada de `cdc9e522`).
- `planta_A.png`, `planta_B.png` e `planta_C.png`: as três propostas. Os pontos estão em `propostas.json`.
- `desenhar.py`: refaz as quatro plantas (`python desenhar.py`, com o matplotlib).
- **Como ler:** o norte fica no alto, a câmera do jogo olha do sul, e o contorno tracejado é a área onde o pet anda (64 × 30 células).

## A ilha de hoje

- A área do pet é um gramado vazio. O `CMU_MVP` não tem árvores no motor, e a vista só põe decoração baixa ali dentro.
- O ninho (4, 15), a tigela (10, 15) e a bola (40, 15) ficam numa linha reta.
- A barraca, o portão, o carro, a geladeira e o trilho ficam enfileirados na faixa norte, e nenhum caminho leva a eles.
- Os 14 postes ficam espalhados pela borda, e as árvores formam uma faixa uniforme na moldura.

## As referências e as regras

O levantamento, com as fontes e o que não foi confirmado, está no Obsidian do Matheus: `20 Temas/Layout da ilha inicial.md`. As 12 regras
que saem dele, em resumo:
1. o lar junto;
2. o bosque atrás do ninho;
3. a praça como nó;
4. uma zona por função;
5. o portão como marco no fim de um caminho reto;
6. todo caminho liga dois nós;
7. a vegetação em bosques e nas bordas;
8. o arbusto e a pedra na base dos bosques;
9. os postes nos caminhos;
10. o ferro-velho num canto;
11. espaço livre onde o pet age;
12. começar enxuto e crescer.

## As propostas

- **A, o lar no bosque e a praça (a recomendada):**
  - o ninho vai para (11, 13), com o bosque e as três frutíferas atrás dele, em (9, 9), (14, 7) e (6, 14);
  - a tigela vai para (16, 15,5) e a bola para (21, 19);
  - a praça fica em (31, 16), com o portão ao norte no fim de um caminho reto, a barraca a leste, o cais ao sul e o saco perto da praça;
  - o ferro-velho fica no canto nordeste, e os postes só na praça e no caminho do cais.
- **B, a vila em roda:** o ninho no centro de uma praça grande, e cada destino numa ponta. O ninho perde o abrigo e muda de região no motor.
- **C, a trilha:** uma trilha de oeste a leste, com um destino por zona. É a que menos muda o motor, mas os destinos ficam longe uns dos
  outros.

Todos os pontos são de desenho: PROPOSTO, SEM FONTE.

## O que muda no jogo, se uma for escolhida

- **No motor:** as árvores dentro da área do pet, o ninho, a tigela e a bola são do `LayoutMundo`. Mudar isso é um mapa novo com uma versão
  nova de pet. O #694 (a árvore que sacode) já cria o `CMU_ILHA` na v20. O layout escolhido deveria entrar nele antes de a v20 fechar, senão a
  troca depois pede uma v21.
- **Só na vista:** os lugares, os postes, o ferro-velho, os bosques da moldura e as pedras.
- **Os pets de hoje** (v12 a v19) continuam no `CMU_MVP`.

## As decisões (IL-1 a IL-4), DECIDIDAS

O Matheus respondeu "A, com IL-2 a IL-4" em 2026-11-08, nesta sessão. As quatro ficam pela recomendação:
- **IL-1:** a planta A, o lar no bosque e a praça.
- **IL-2:** as frutíferas do sacudir vão para o bosque do lar. O `CMU_ILHA` do #694 usa os pontos da A.
- **IL-3:** os postes ficam nos caminhos e na praça, cerca de 6 no lugar de 14.
- **IL-4:** o carro, a geladeira e o trilho ficam juntos no canto nordeste.

Os pontos seguem PROPOSTO, SEM FONTE. A escolha é a da planta, não a de cada número.

## O fim da ilha e guiar o olhar (2026-11-08, pedidos depois da escolha da A)

- **O fim da ilha** (o Matheus: "adicionar um final, né, para a ilha, para ela não acabar no meio do nada"): em volta da moldura, o mar até o
  horizonte, com ilhas e morros ao longe, e a mata em degraus até o morro no norte e no leste. Nenhum canto da câmera mostra o vazio. Isso foi
  para a sessão "Ilha A em 3D".
- **Guiar o olhar sem texto** (o Matheus: "regras de game design para instruir o player a observar o mundo [...] Tem que ser algo mais
  natural"). O levantamento está no Obsidian, em `20 Temas/Ensinar a olhar.md`. As regras, PROPOSTAS:
  - **só vista, para a prancha 3D:**
    - a câmera abre devagar no primeiro dia, do ninho até a árvore e a praça;
    - a luz em hierarquia: os destinos com luz quente, a decoração mais apagada;
    - a ilha limpa, sem contorno nem seta;
    - um sinal só: o que é tocável balança de leve quando o pet passa, e a decoração nunca balança;
    - a barraca tapa parte do cais, que aparece ao contornar;
    - todo toque responde no mundo;
    - pássaros pousam na árvore madura, e também onde não há nada;
  - **pedem o pet ou o motor (uma frente própria, depois):**
    - o pet olha para o alvo antes de ir;
    - o interesse dele se gasta e volta;
    - a primeira fruta rola até ele;
    - o pet ajuda só depois de uns 2 minutos, com uma opção para reduzir;
    - a recompensa incerta ao sacudir, que conflita com a AS-6 (frutas iguais) e fica para quando ela for revista.
