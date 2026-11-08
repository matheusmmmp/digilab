# Prancha: a planta A na ilha 3D (2026-11-08)

A parte da vista da planta A (IL-1 a IL-4, DECIDIDAS em 2026-11-08; a planta em `docs/pranchas/ux-ilha-layout/`, PR #724) aplicada à cena 3D
da tela Pet, em `web/app/src/telas/pet/ilha/`. A página com o antes e o depois é https://claude.ai/artifact/PUJBByRmETT758SSY7XCWv.

## O que entra

- A praça em (31, 16) e os caminhos de terra praça → lar (até o comedouro do layout), praça → portão, praça → barraca e praça → cais.
- O portão no fim do caminho reto ao norte, com um vão na mata atrás dele; a barraca a leste; o cais ao sul; o saco em (22, 9), perto da praça.
- 6 postes, só na praça e no caminho do cais (IL-3).
- O carro, a geladeira e o trilho espalhados pela moldura, cada um com o seu entorno (a IL-4 revista pelo Matheus em 2026-11-08: "Espalha
  eles também pelo mapa"): o carro meio coberto pelo mato no platô do oeste, a geladeira na areia a leste do cais e o trilho na beira leste
  do rio.
- A moldura em bosques e vãos, no lugar da faixa uniforme.
- O fim da ilha (o Matheus, 2026-11-08: "para ela não acabar no meio do nada"): o mar em volta da grade inteira, a mata a leste do rio
  subindo em dois degraus até o morro, e duas faixas de silhuetas ao longe (ilhas perto, morros longe) que seguem o ponto olhado, com o pé
  no horizonte do mar curvo (`fimDaIlha.ts`).
- O sinal só (a regra 3 de guiar o olhar): a tigela, a bola e o saco dão um pulinho quando o pet chega perto (`itens.ts`, `CHAMADO`).

O lar da planta (o ninho em (11, 13), a tigela, a bola e as frutíferas) é do motor e entra com a v20 (PR #694). As capturas são do pet de hoje
(v19, `CMU_MVP`, ninho em (4, 15)). Todos os números são PROPOSTO, SEM FONTE.

## Como fica no código

- `constantes.ts`: a tabela `PLANTA_ILHA`. O `LUGARES_GRADE` e o `SACO_DESDE_NINHO` saem; o `ENFEITES_GRADE` fica com quantos, a folga e o
  espaço entre os marcos.
- `grade.ts`: os lugares e os enfeites nos pontos da planta (o mais perto que cabe), a praça e os caminhos pintados depois da decoração e a
  moldura em bosques e vãos. A decoração que cai num caminho, num vão ou fora de um bosque só some da vista (`escondidos`): a lista `objetos`
  não muda, e o gabarito E-G0 (`test/gabaritos/ilha_objetos.json`) continua passando. As árvores novas dos bosques e as pedras do ferro-velho
  ficam numa lista própria, `extras`.
- `lugares.ts`: o saco no ponto da planta. `cena.ts`: desenha os `extras` e exporta a água (`materialAgua`); o céu e a grade digital
  ficam com a outra sessão (PR próprio).
- `fimDaIlha.ts` (novo) e `vista.ts`: o mar em volta e as silhuetas, atualizados a cada quadro. `grade.ts`, `porBordas`: os degraus a leste.
- `itens.ts`: o pulinho do que se toca.

## Desvios da planta

1. **Os bosques de dentro da área do pet vão para a moldura.** O `LayoutMundo` só aceita árvore com fruta: o `Mundo` falha alto com outra
   (`web/app/motor/mundo.ts:453`), e a árvore do layout fica no jardim ou na mata. É o caso previsto na tarefa: os bosques ficam só na moldura,
   encostados na área.
2. **Os dois bosques do sul saem:** ao sul da área só há areia e mar.
3. **As pedras de (49, 12) e (11, 22) saem:** a pedra não é decoração baixa (regra 5 da ilha 3D).
4. **O caminho do portão para no pé do penhasco:** o portão fica no platô.
5. **Os marcos nos pontos novos:** o carro em (−6,5, 19,5), a geladeira em (50, 31,2) (em (44, 31) ela tapava o cais) e o trilho em
   (69, 21). O bosque do sudoeste encolheu para dar lugar ao carro.

## Guiar o olhar sem texto (as seis regras da vista)

1. **Luz em hierarquia:** proposta, sem código. Os caminhos no tom da areia, a decoração mais escura e menos saturada e uma luz quente no
   chão do portão e da barraca. Fica para depois do PR do céu e da grade digital (`cena.ts`, `estilos.ts`), para não cruzar.
2. **Ilha limpa:** já vale no estilo Ilha. O nanquim do estilo Digital (D5) foi pedido pelo Matheus e fica.
3. **Um sinal só:** em código (`itens.ts`). Ver a PA-4 sobre o vento.
4. **Esconder e revelar:** proposta. Com a câmera olhando para o norte, a barraca não tapa o cais; o par que funciona é a mata do leste
   tapando o trilho, o que já acontece.
5. **Pássaros:** proposta; não é barato (modelo, animação e a árvore madura do motor).
6. **A câmera do primeiro dia:** proposta descrita na página, sem código.

## As perguntas (PA-1 a PA-3), PROPOSTAS

- **PA-1.** A vista da planta A vira código assim? Recomendação: sim; custo de errar baixo (só vista).
- **PA-2.** A barraca fica dentro da área, como na planta? Recomendação: sim; o pet pode passar por ela, como já passa pelo saco. A
  alternativa é a borda norte, perto do portão.
- **PA-3.** A ida e a volta do treino passam a durar conforme a distância (cerca de 7 células por segundo, 0,9 s no mínimo)? Hoje duram
  0,9 s; com o saco em (22, 9), o pet de hoje cruza ~19 células nesse tempo. Recomendação: sim, só em `vista.ts`.

- **PA-4.** O vento continua mexendo a grama e as flores? Recomendação: sim; o pulinho é uma batida curta e se distingue dele.
- **PA-5.** As silhuetas ficam como estão (duas faixas em tons de névoa, com vãos de mar)? Recomendação: sim.

## Recapturar

`fonte/capturar.spec.ts`: copie para `web/app/e2e_capturas/planta_a.spec.ts`, faça o build (`npx vite build`) e rode
`CAP_ROTULO=depois npx playwright test -c playwright.capturas.config.ts e2e_capturas/planta_a.spec.ts --project gpu`. As capturas (PNG) ficam
fora do git, em `D:\Trab\digilab\capturas_ux_ilha_planta_a\<antes|depois>\`; o antes saiu do build da base do branch, `66ae8a5c`.
`CAP_CENAS` e `CAP_PELES` escolhem as cenas e as peles.
