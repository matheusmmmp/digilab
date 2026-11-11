# TAREFA V3 — MAPA_DIGITAL (2026-11-06)

Coordenador: o Gerente da frente MAPA_DIGITAL (Claude Code, Opus 5.5, nesta sessão; o mesmo da MUNDO_ENFEITES). Worker: a definir por
etapa. Worktree e branch: `v3-mapa-digital` (na worktree `v3-mundo-enfeites`). Status: ABERTA; a direção B escolhida pelo Matheus
(2026-11-06); D-MD1 a D-MD5 DECIDIDAS pela recomendação (2026-11-06, seção 8); nada foi feito no jogo.

Categoria: arquitetura. Origem: Matheus, 2026-11-06: o chão, as texturas e os objetos da ilha estão genéricos ("bem o que veio do kit");
pediu uma estética "mais na pegada do anime, com as cores mais chapadas" e um mapa mais temático. Mostrou como referência de clima
imagens de animes e jogos de monstros digitais, entre eles o Next Order. Entre as três maquetes (A, fundo de anime; B, mundo digital;
C, cidade engolida), escolheu a **B**.

Lido para esta tarefa: `CLAUDE.md`, `web/app/CLAUDE.md`, `docs/TAREFA_V3_MUNDO_ENFEITES.md` (os enfeites e os traços de nanquim, seção
11), `docs/TAREFA_V3_HABITAT_ILHA_3D.md` (a ilha, a regra 5, H-6), `web/app/src/telas/pet/ilha/cena.ts` (`toon`, o `GRADIENTE`, o
`terreno`, o `ceu`, as `nuvens`, `montarCena`, `aplicarNoite`), `estilos.ts`, `grade.ts`, `modelos.ts`, `web/app/src/habitat.ts` (os mapas
de Ajustes).

## 1. Pergunta

A ilha fica com a cara da maquete B — fundo de anime (céu pintado com nuvens enormes, grama saturada e chapada com florzinhas, barranco
de pedra cinza com musgo, cel shading de dois tons, traços de nanquim) e o toque digital (partículas de dados, uma grade fraca no céu,
fios entre os postes, um objeto humano gigante como marco) — sem tocar o motor, sem mudar onde as coisas ficam e sem perder fps?

**A linha da inspiração:** a referência é o clima (cores, céu, o digital, objetos humanos na natureza). Nada é copiado: nenhum mapa,
modelo, textura, logotipo ou nome desses jogos; as imagens de terceiros não vão para gerador nenhum (só a descrição do estilo).

## 2. Depende de

- A MUNDO_ENFEITES na `main` (a E3 entrou no PR #631): os postes, o carro, a geladeira, o trilho e o `tracar_linhas.py`.
- As decisões D-MD1 a D-MD5 (seção 8), tomadas.

## 3. Mudança mínima

**O que muda (só a vista):**
- um estilo de mapa novo, `digital` (D-MD1), em `estilos.ts`, sobre a **mesma grade** (`grade.ts`): a área andável, a moldura, os objetos e
  os enfeites ficam onde estão;
- `cena.ts`: uma paleta de terreno nova (grama em dois verdes saturados, a pedra cinza com faixas de musgo no barranco, o caminho), uma
  textura de chão com florzinhas, o céu pintado (D-MD2), o `GRADIENTE` do toon em dois tons com a sombra azulada;
- os modelos dos kits (árvores, arbustos, pedras, flores) recoloridos para a paleta chapada e com os traços de nanquim (o pipeline da
  E3: `achatar_cores.py`, `limpar_faces.py`, `arestas_uv.py`, `tracar_linhas.py`), numa pasta própria do estilo; os postes e o carro
  ganham os traços também;
- o digital: as partículas de dados (pontinhos ciano que flutuam, mais fortes à noite), a grade fraca no céu, os fios entre os postes
  (curvas penduradas entre postes vizinhos) e um objeto gigante como marco (D-MD3);
- Ajustes › Mapa: o "Digital" na lista (D-MD1).

**O que NÃO muda:** o motor, o log, o save, a área andável e o caminho do pet; a grade e os objetos de hoje (o gate D-G0, como o E-G0);
os outros estilos (ilha, voxel, floresta, cassette); as versões de pet.

## 4. Etapas e gates

| etapa | o quê | gasto |
|---|---|---|
| D0 | esta tarefa (PR de arquitetura) | 0 |
| D1 | o estilo `digital` na lista, a paleta do chão com as flores, o barranco de pedra, o toon de dois tons e o céu pintado | 0 a 6 créditos (D-MD2) |
| D2 | os kits recoloridos e com traços, e os traços nos postes e no carro | 0 |
| D3 | o digital: as partículas, a grade no céu, os fios dos postes | 0 |
| D4 | o objeto gigante (o marco) | ~66 créditos (D-MD3) |

**Gates (cada etapa, contra a mesma captura da ilha de hoje):**
- D-G0: os objetos e os enfeites da grade não mudam (o gabarito de `test/gabaritos/ilha_objetos.json` e as posições dos enfeites);
- D-G1: os draw calls da M3 (`?medir3d=1`) no máximo 10 % acima do estilo ilha; as partículas num desenho só;
- D-G2: os arquivos novos com os gates G1 a G8 da ITENS_3D (os kits recoloridos com a licença CC0 de origem ao lado);
- D-G3: nada cobre o pet nem o HUD; o pet (o sprite) continua legível sobre o chão novo (contraste);
- D-G4: as capturas lado a lado com a maquete B (`D:\Trab\digilab\capturas_enfeites\maquetes\`), lidas por um revisor que não fez a etapa,
  e aprovadas pelo Matheus;
- D-G5: o fps de verdade, no desktop e num celular, pelo Matheus.

Em cada etapa: `npm run tipos`, `npm test`, `npm run e2e`; o registro em `docs/registro/AAAA-MM.md` com a linha no índice; o resumo numa
seção no fim deste arquivo; as capturas com o pet fora do git (`D:\Trab\digilab\capturas_mapa_digital\`).

## 5. Fora desta tarefa

- O pet interagir com o digital (as partículas, o marco): é cérebro e motor (a ideia de `docs/futuro/enfeites_interacao.md`).
- Mudar a grade, a área andável ou o layout do motor.
- Os outros estilos de mapa.
- A cidade engolida (a maquete C) e mais objetos gigantes além de um.

## 6. Critérios de aceitação

- D-G0 num teste; D-G1 nas M3 citadas no PR; D-G2 num teste como o `ilha_enfeites.test.ts`.
- As capturas de cada etapa ao lado da maquete B, com o parecer do revisor no PR e a aprovação do Matheus.
- O gasto da Meshy nos `saldo.json`, dentro do teto da D-MD4.

## 7. Riscos

- **O sprite do pet sobre a grama saturada:** o pet é um sprite em papel; um chão muito saturado pode apagá-lo. O D-G3 confere e, se
  precisar, a grama perto do pet fica um tom mais clara.
- **Os traços nos kits:** os kits CC0 são facetados como as malhas da Meshy; o limiar da E3 (70°, comprimento mínimo) vale de partida.
- **A maquete é pintura, o jogo é 3D:** o alvo é a direção (cor, céu, chão, o digital), não a imagem igual.

## 8. Precisa do Matheus

**DECIDIDAS em 2026-11-06:** o Matheus aceitou as cinco recomendações abaixo ("Sim, mescle os dois", à pergunta "Aceito as cinco
recomendações e mesclo o #631 e o #632?").

- **D-MD1, o digital como estilo novo ou no lugar da ilha.** Recomendação: um estilo novo, "Digital", em Ajustes › Mapa, e ele vira o
  padrão quando as capturas forem aprovadas; a ilha de hoje fica selecionável. Custo de errar: trocar o padrão sem aprovação muda a cara
  do jogo de todo mundo de uma vez.
- **D-MD2, o céu pintado.** Recomendação: uma panorâmica de céu gerada pela Meshy (Image to Image, 6 créditos, a partir de uma descrição,
  sem imagem de terceiros) e ajustada à mão; a alternativa é desenhar as nuvens no código, como as de hoje, maiores. Custo de errar: 6
  créditos, ou um céu que não fica pintado o bastante.
- **D-MD3, o objeto gigante.** Recomendação: uma lata de refrigerante sem marca (a da maquete), pela Meshy, longe no fundo; outras ideias:
  uma cabine telefônica ou um hidrante gigantes. Custo de errar: ~66 créditos num marco que não combina.
- **D-MD4, o teto de gasto da frente.** Recomendação: R$ 20 (~185 créditos; o saldo do Pro é 602 em 2026-11-06). Custo de errar: gastar
  além do previsto num mês de plano.
- **D-MD5, os números PROPOSTOS** (a paleta, a densidade das partículas, a transparência da grade, a curva dos fios). Recomendação: aceitar
  e ajustar jogando. Custo de errar: só vista.

## 9. D1: o estilo Digital, com o chão, o barranco, o toon e o céu (2026-11-06, Gerente, Claude Code, Opus 5.5, branch `v3-mapa-digital-d1`)

**O que entrou:**
- **O estilo "Digital"** em Ajustes › Mapa (`habitat.ts`, `EscolhaHabitat.tsx`, `estilos.ts`), sobre a mesma grade da ilha. O padrão
  continua a ilha até as capturas serem aprovadas (D-MD1).
- **O céu pintado** (D-MD2): uma imagem da Meshy (Image to Image, 16:9, 6 créditos, saldo 602 → 596), com a maquete A como referência de
  estilo e um pedido só de céu (`docs/mapa_digital/ceu/`). Em `public/mapa_digital/ceu.jpg`, com a saturação a 85 %, depois do
  revisor. Ele cobre a tela sem esticar (`cobrirFundo` em `cena.ts`): corta os lados no celular em pé e mantém o alto do céu. As
  nuvens de sprite da ilha saem nesse estilo. A noite continua o degradê de hoje.
- **O chão** (`PALETA_DIGITAL`): a grama em três verdes por região, sorteados por célula, como um xadrez solto; o caminho de terra quente;
  o barranco de pedra cinza (as faixas de estrato) com a borda de musgo. **As florzinhas** (`flores`): discos brancos, rosa e amarelos,
  ~1,1 por célula de grama, numa malha só.
- **O cel shading de dois tons** (`doisTons`): os materiais toon da cena e dos objetos passam de três tons para dois; a luz de baixo do
  céu de dia fica azulada (`CEU_DIGITAL.chaoHemi`), a sombra do anime.

**Os gates:** D-G0, a mesma grade e os mesmos objetos (o E-G0 passa; o estilo não toca `grade.ts`); D-G1, os draw calls iguais ou menores
que os da ilha (390: 81 → 79 de dia e 103 → 101 à noite, sem as nuvens de sprite; 1280: 88 → 88 e 109 → 109;
`D:\Trab\digilab\capturas_mapa_digital\d1\`); D-G2, o `License.txt` do céu e o tamanho num teste (`test/mapa_digital.test.ts`); D-G3, o pet
legível sobre o chão novo, de dia e de noite (o revisor). D-G4: o revisor (um subagente Sonnet que só viu as capturas e a maquete)
**aprovou com ressalva**: o verde quase neon contra o azul elétrico; o conserto foi o dele (a saturação da grama e do céu ~15 % menor,
três tons por região, as flores maiores e mais numerosas), e as capturas foram refeitas. Comparação: `comparacao_d1.png`.

**Fica para as próximas etapas:** as árvores, os arbustos e as pedras dos kits ainda com as cores e o toon deles (só o toon passa a dois
tons), sem os traços (D2); as partículas, a grade no céu e os fios (D3); a lata (D4). Os itens (a bola, o saco, o kit, o cocô) seguem com
os três tons: eles entram depois da cena.

## 10. D2: os kits recoloridos, a névoa, os itens em dois tons e os traços do poste (2026-11-06, Gerente, Claude Code, Opus 5.5, branch `v3-mapa-digital-d2`)

**O que entrou:**
- **Os kits do Digital** (`docs/mapa_digital/kits_digital.py`): as 9 texturas dos kits CC0 (`public/kits3d/`) recoloridas em poucos tons
  (4; 6 a 8 nos atlas), com o filtro de moda, a saturação ×1,35 e o brilho ×1,08 (×1,3 nos pinheiros), o alfa das folhas intacto, em `public/kits3d_digital/`
  (740 KB), com a licença de cada kit; os glTF copiados apontam para a textura nova e para o `.bin` de sempre (`../../kits3d/`), sem
  duplicar a geometria. O estilo Digital carrega os kits de lá; a ilha não muda.
- **A névoa do estilo** (`CEU_DIGITAL.nevoa`, de 34 a 85 em vez de 26 a 62; a de 42 a 95 deixou os pinheiros pesados, pelo revisor): a vista recalculava a névoa com a órbita a partir de
  `NEVOA`; agora usa a do estilo quando ele tem uma (`cena.userData.nevoa`). As árvores de trás deixaram de sair desbotadas.
- **Os itens em dois tons** (`usarDoisTons`): o estilo diz, antes de montar, o degradê dos materiais toon criados depois (os itens da
  vista, os cocôs, os modelos carregados).
- **Os traços de nanquim no poste** (`tracar_linhas.py` sobre a textura chapada; a máscara da luz refeita): vale nos dois estilos, como
  na geladeira e no trilho.

**O que não entrou, e por quê:**
- **Os traços nas árvores e nos kits:** as texturas são divididas entre vários modelos (a casca e as folhas de todas as árvores), e as
  folhas são cartões transparentes; um traço pelas arestas de um modelo sujaria os outros.
- **Os traços no carro:** a malha da Meshy dele usa só 9 % da largura do mapa de textura (u de 0 a 0,091); um traço sai ~11 vezes mais
  grosso na horizontal e borra o carro. Pede refazer os UVs no Blender, uma tarefa à parte.

**Os gates:** D-G0 (o E-G0 passa); D-G1, os draw calls iguais aos da D1 (79 e 101 em 390, 88 e 109 em 1280;
`D:\Trab\digilab\capturas_mapa_digital\d2\`); D-G2, os kits do Digital num teste (`test/mapa_digital.test.ts`: cada modelo da tabela
com a textura, o `.bin` de sempre e a licença, e a pasta abaixo de 2 MB). D-G4: o revisor (corpo do PR). Comparação:
`comparacao_d2.png` e `zoom_arvores_d1_d2.png`.

## 11. D3: as partículas, a grade no céu, os fios, e a escala nova (2026-11-06, Gerente, Claude Code, Opus 5.5, branch `v3-mapa-digital-d3`)

**O toque digital** (`web/app/src/telas/pet/ilha/digital.ts`, `DIGITAL` em `constantes.ts`, PROPOSTO):
- **as partículas de dados:** 140 cristais ciano (octaedros) sobre a área e 3 células em volta dela, entre 0,6 e 3,2 acima do chão; sobem,
  descem e giram pelo shader (o `uTempo` da curva: paradas com movimento reduzido); aditivas, mais fortes à noite (0,55 de dia, 0,95 à
  noite). Um `InstancedMesh` só; o `curvar` ganhou o trecho `mexer` (o GLSL depois do `begin_vertex`, com o nome na chave do programa);
- **a grade no céu:** meridianos que saem de um ponto de fuga acima da imagem e arcos em volta dele, em ciano (50 %, 3 px; a primeira rodada, a 22 % e
  1,5 px, quase não aparecia, pelo revisor), desenhados por cima do céu pintado quando a imagem chega; só de dia;
- **os fios:** cada poste ligado aos dois vizinhos mais perto até 10 células, um fio pendurado (uma parábola com queda de 6 % do vão) do
  alto de um ao do outro; uma malha de segmentos só.

**A escala (pedido do Matheus no meio da D3, 2026-11-06: os objetos têm que ser muito maiores que o pet, que é uma criança):** em
`modelos.ts`, a árvore redonda de 4,2 para 6, o pinheiro de 5 para 7, o poste de 3 para 4,5, o carro de 1,9 para 3,4, a geladeira de 1,7
para 3 e o trilho de 1 para 2 (para um pet de cerca de 1 célula); vale nos dois estilos. Com os marcos maiores, a grade os afasta: o carro
de 2,4 a 4 células da área, a geladeira de 1,8 a 4, o trilho de 2 a 5, e entre os marcos 5 a 6,5 células (`entreMarcos`, separado da
distância aos postes); a geladeira e o trilho numa faixa de −14 a 16 e de −16 a 18 células do ninho em x. Os do motor: mvp, carro (−1;
−3,7), geladeira (6,2; −2) e trilho (11,6; −4,7); padrão, carro (8; −3,9), geladeira (18,9; −2,7) e trilho (−3; −3,7). Os objetos da grade
(E-G0) não mudam de lugar: só de tamanho.

**Os gates:** D-G0 (o E-G0 passa); E-G10 (as distâncias, com a de marcos) passa; D-G1, dois draw calls a mais (as partículas e os fios):
81 e 103 em 390, 90 e 111 em 1280 (`D:\Trab\digilab\capturas_mapa_digital\d3\`); D-G3, o pet legível, agora pequeno perto dos objetos.
D-G4: o revisor (corpo do PR). Comparação: `comparacao_d3.png`; a ilha com a escala nova: `ilha_d3\`.

**O teste da D3 (2026-11-06, depois do merge do #650):** as contas da D3 ficaram em `digitalConta.ts` (sem DOM) e são testadas em
`test/mapa_digital.test.ts` nos dois layouts: as 140 partículas dentro da área com a margem e entre as alturas, sempre iguais; os pares de
postes sem repetição e dentro do alcance; um segmento por pedaço de fio. O #650 tinha entrado sem teste (o check `relato` reprovou e o
merge não esperou por ele; D-MD-13).


## 12. D4: a lata gigante (2026-11-06, Gerente, Claude Code, Opus 5.5, branch `v3-mapa-digital-d4`)

**O modelo** (`docs/mapa_digital/lata/`, `web/app/public/mapa_digital/lata/`): pela Meshy, como os enfeites. Quatro concepts (cereja, limão,
uva, pêssego), sem marca e sem texto, com duas referências geradas pela própria Meshy para o DigiLab (o recorte da lata na maquete B e o
concept da geladeira); o Matheus escolheu o 1, a cereja. Depois a multivista e a malha (1 978 triângulos, abaixo do teto 2 414 dos marcos).
O conserto: a cor chapada nas nove cores do concept (`paleta.json`) e o corpo repintado sem o alumínio e sem os reflexos brancos
(`faces_corpo.py`, `pintar_corpo.py`); sem o `limpar_faces.py` e sem os traços, que quebravam as faixas onduladas (D-MD-16). glTF-Validator
sem erro nem aviso; `License.txt` com a marca de IA. Gasto: 60 créditos (saldo 596 → 536); a frente soma 84, dentro do teto da D-MD4.

**No jogo** (`digital.ts`, `lata`; a conta em `digitalConta.ts`, `lugarDaLata`; `DIGITAL.lata` em `constantes.ts`, PROPOSTO): a lata fica no
horizonte, a `longe` células ao norte do pet, andando com ele só com a fração 1 − `paralaxe`, de lado por uma fração da meia largura
visível, com a dobra do mundo descontada e sem névoa; a parte de baixo some atrás do penhasco e da mata, como na maquete (D-MD-14). A vista
a reposiciona a cada quadro pelo gancho novo `quadro` dos objetos (D-MD-17). Só vista: a grade e o motor não mudam.

**Os gates:** D-G0 (o E-G0 passa); D-G1, um draw call a mais (82 e 104 em 390, 91 e 112 em 1280); D-G2, os arquivos da lata num teste
(`test/mapa_digital.test.ts`, com o lugar no horizonte nos dois layouts); D-G3, a lata longe do pet e do HUD fixo. D-G4: o revisor
(um subagente Sonnet que só viu as capturas e a maquete) **aprovou com ressalva**: a lata lia como uma faixa pastel, sem a tampa; o conserto
foi o dele (subir e trazer para a esquerda), e as capturas foram refeitas (`D:\Trab\digilab\capturas_mapa_digital\d4\`, `comparacao_d4.png`).
Ficam: à noite ela fica escura e quase ilegível (o revisor sugere um leve brilho; não feito, fica para o Matheus), e o fps de verdade (D-G5).

**Com a D4, as etapas da tarefa estão feitas.** Falta o Matheus aprovar o Digital como padrão (D-MD1) e medir o fps (D-G5).

## 13. D5: o cel shading (2026-11-07, Gerente, Claude Code, Opus 5.5, branch `v3-mapa-digital-d5`)

**Por que:**
- **A recomendação era o chão e o barranco pintados.** Ao vê-la começar, o Matheus disse que o mundo ainda parecia "sem textura" e pediu
  uma pele mais cel shading.
- **A etapa cobriu o estilo Digital inteiro** (D-MD-18).
- **Fica igual:** a grade, o motor e os outros estilos.

**O que entrou:**
- **O traço de nanquim** (`pos.ts`, `Contorno`; `CONTORNO_DIGITAL` em `constantes.ts`; `Estilo.contorno`):
  - um contorno de tela, pela profundidade, que pega as árvores, os kits, os lugares, os itens e o terreno;
  - só o Digital o pede (D-MD-19).
- **O chão pintado** (`cena.ts`, `pintarTerreno`, `aPinta`):
  - a grama sem o xadrez, com manchas e folhinhas desenhadas;
  - o barranco em placas de pedra com juntas e rachaduras (D-MD-20).
- **Os tufos de capim em moitas** (`tufos`):
  - a grama alta da maquete, num desenho só;
  - fora do contorno.
- **As flores:** menos soltas, mais em manchas de uma cor, cada flor numa haste.
- **As nuvens de anime** (`nuvensAnime`): o cúmulo com o contorno e a sombra azulada, todas num desenho só.

**Os gates:**
- **D-G0:** a grade não muda; o E-G0 passa.
- **D-G1:** a M3 das capturas, em draw calls por quadro:

  | tela | Digital | Ilha | diferença |
  |---|---|---|---|
  | 1280, dia | 98 | 92 | +6,5 % |
  | 1280, noite | 119 | 113 | +5,3 % |
  | 390, dia | 89 | 85 | +4,7 % |
  | 390, noite | 111 | 107 | +3,7 % |

  O limite é +10 %. As capturas do Digital estão em `D:\Trab\digilab\capturas_mapa_digital\d5\`, e as da Ilha em `d5\ilha\`.
- **D-G2:** nenhum arquivo novo; o chão e o céu saem do código.
- **D-G3:** o pet e o HUD continuam legíveis de dia e de noite, segundo o revisor.
- **D-G4:** o revisor (um subagente Sonnet que só viu as capturas e a maquete) aprovou com ressalva duas vezes. As correções da primeira
  leitura entraram (D-MD-21).
- **O teste:** `web/app/test/mapa_digital_d5.test.ts` (D5-G1 a D5-G4).
- **A comparação:** `comparacao_d5.png`, a maquete, a D4 e a D5 lado a lado.

**Ficam:**
- as nuvens, que quase não aparecem na câmera do habitat (D-MD-22);
- uma granulação fina no capim à noite, no celular;
- o barranco, que ainda lê um pouco como muro de tijolo;
- o fps de verdade (D-G5) e o Digital como padrão (D-MD1), com o Matheus.

## 12.1. D4 revista: a lata sai do horizonte (2026-11-10, Gerente, Claude Code, Fable 5.2, branch `v3-objeto-lata-mao`)

O Matheus pediu em 2026-11-10 a lata dentro do mapa e refeita ("tá fora do mapa e ainda tá toda errada"). A lata presa ao horizonte da
seção 12 sai do estilo Digital, com o `DIGITAL.lata`, a função `lata` e o `lugarDaLata`. A lata nova é um marco da grade, feita à mão
por script: `docs/TAREFA_V3_MUNDO_ENFEITES.md`, seção 17.
