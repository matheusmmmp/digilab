/* Os numeros da vista da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, regra 12), num so lugar. Sao do desenho, nao do jogo: nao mudam a
   vida, o log nem o replay. Todos PROPOSTO, SEM FONTE; os da camera e da dobra sao os do POC poc/mapa_ac (H-3), aprovados pelas capturas
   da H5. As distancias sao em celulas do motor (uma celula = uma unidade do mundo 3D). */

/** a dobra do mundo curvo, por celula (o POC: 0,011) */
export const DOBRA_K = 0.011;
/** a camera em relacao ao pet (o POC: 8,4 acima e 14,5 atras) e para onde ela olha em relacao a ele */
export const CAMERA_DESLOC: readonly [number, number, number] = [0, 8.4, 14.5];
export const CAMERA_OLHAR: readonly [number, number, number] = [0, 0.6, -3.2];
/** o campo de visao vertical (o POC: 32 graus) e o de longe/perto */
export const FOV_GRAUS = 32, PERTO = 0.1, LONGE = 200;
/** as cameras do habitat (src/habitat.ts): atras (a de cima, H-3) e lateral (a do POC do campo lateral, #480: de lado, baixa e com o
    campo de visao estreito, quase ortografica). desloc e olhar sao em relacao ao pet; fov em graus */
export interface CameraHabitat { desloc: readonly [number, number, number]; olhar: readonly [number, number, number]; fov: number }
export const CAMERAS: Readonly<Record<"atras" | "lateral", CameraHabitat>> = {
  atras: { desloc: CAMERA_DESLOC, olhar: CAMERA_OLHAR, fov: FOV_GRAUS },
  lateral: { desloc: [0, 3.6, 26], olhar: [0, 0.9, -1], fov: 20 },
};
/** em retrato (o celular), a camera se afasta ate mostrar LARGURA_MIN celulas de lado a lado na altura do pet, no maximo AFASTAR_MAX vezes */
export const LARGURA_MIN = 11, AFASTAR_MAX = 2.4;
/** a nevoa da cor do horizonte: comeca e termina a estas distancias da camera (o POC: 26 e 62), vezes o afastamento */
export const NEVOA = [26, 62] as const;

/** o pet em papel: o tamanho alvo de um texel do sprite no mundo (o POC: 1/34 de celula) e a borda branca, em texels */
export const TEXEL_ALVO = 1 / 34, BORDA_PAPEL = 1;
/** a virada de lado (escala em x por segundo), o pulinho ao andar (px de canvas por texel de altura) e o periodo dele (ms) */
export const VIRAR_POR_S = 9, PULO_TEXELS = 2, PULO_MS = 95;
/** "andando": a posicao do motor mudou nos ultimos ANDANDO_MS; o lado so troca com um passo em x maior que LADO_MIN (celulas por quadro) */
export const ANDANDO_MS = 450, LADO_MIN = 0.004;

/** o tamanho maximo do pixel do canvas por pixel de CSS (o celular de densidade 3 desenha em 2) */
export const RAZAO_MAX = 2;
/** coberta por um painel ou modal (o veu), a ilha desenha no maximo um quadro a cada COBERTO_MS */
export const COBERTO_MS = 100;
/** a ilha que abre coberta (uma rota de painel aberta direto) adia os kits ate ficar a vista, no maximo KITS_COBERTO_MS: o painel responde
    primeiro, e o carregamento e a montagem dos modelos (centenas de ms de tarefas longas) vem depois */
export const KITS_COBERTO_MS = 5000;
/** a queda de qualidade (regra 10): abaixo de FPS_MIN de media por QUEDA_MS, sem vento, metade da grama e pixelRatio 1 */
export const FPS_MIN = 30, QUEDA_MS = 3000;

/** o dia e a noite: o ceu (topo, meio, horizonte), a luz do hemisferio (ceu, chao, intensidade) e a do sol (cor, intensidade) */
export const DIA = {
  ceu: ["#3d8de8", "#7fc0f5", "#cfeefc"], horizonte: 0xcfeefc,
  hemi: [0xdff1ff, 0x86b85c, 1.6], sol: [0xfff1d6, 2.2], agua: 1, nuvens: 0.92,
} as const;
export const NOITE = {
  ceu: ["#0b1638", "#1d2f63", "#3b4f86"], horizonte: 0x3b4f86,
  hemi: [0x6c7fc4, 0x2a3a3a, 0.9], sol: [0x9fb4ff, 0.7], agua: 0.45, nuvens: 0.35,
} as const;
/** a luz fraca do ninho a noite: o raio (celulas) e a cor */
export const LUZ_NINHO = { raio: 2.2, cor: "255,214,140" } as const;

/* os objetos do cuidado e a coreografia (docs/TAREFA_V3_HABITAT_OBJETOS.md): so vista, como o resto deste arquivo */
/** o kit medico da lesao, ao lado do ninho, em celulas a partir do ninho do layout (o saco de pancada, desde a planta A, fica perto da
    praca: PLANTA_ILHA.lugares.saco) */
export const KIT_DESDE_NINHO: readonly [number, number] = [1.3, -1];
/** o treino na ilha: a ida ate o saco, os golpes e a volta (ms); um golpe a cada GOLPE_MS; o pet para a GOLPE_DIST celulas do saco */
export const TREINO_MS = { ida: 900, golpes: 2400, volta: 900 } as const, GOLPE_MS = 600, GOLPE_DIST = 1.35;
/** a velocidade da ida e da volta do treino (celulas por segundo; lugares.ts, idaDoTreino): a ida e a volta duram a distancia sobre ela, com
    TREINO_MS.ida no minimo (a PA-3 da prancha da planta A, aprovada em 2026-11-08). PROPOSTO, SEM FONTE */
export const TREINO_VEL = 7;
/** a ida do pet ate o lugar aberto (e a volta), separada da camera: ele anda na velocidade dele (celulas por ms) e a camera e o painel chegam antes
    (o Matheus, 2026-11-08: "ele não teleporta até lá, ele vai correndo na velocidade dele mesmo"); a caminhada nunca passa de PET_VIAGEM_MAX_MS.
    PROPOSTO, SEM FONTE (numero de interface, nao de jogo) */
export const PET_VIAGEM_CEL_MS = 3.5 / 1000, PET_VIAGEM_MAX_MS = 6000;
/** quanto a ida do pet ao lugar dura (ms) para `dist` celulas: a velocidade dele, com o teto; "reduzir movimento" chega na hora */
export const duracaoPetViagem = (dist: number, reduzido: boolean): number => (reduzido ? 0 : Math.min(PET_VIAGEM_MAX_MS, dist / PET_VIAGEM_CEL_MS));
/** a batida na bola: quanto dura o golpe (ms) */
export const BATER_BOLA_MS = 450;
/** a bola desenhada vai ate a do motor com esta constante de tempo (ms); salta quando a distancia passa de BOLA_SALTO celulas */
export const BOLA_TAU_MS = 140, BOLA_SALTO = 12;
/** o balanco do saco a cada golpe: a amplitude (radianos) e a constante de tempo do amortecimento (ms) */
export const SACO_BALANCO = { amplitude: 0.32, tau: 650, periodo: 520 } as const;
/** o saco gerado (docs/TAREFA_V3_ITENS_3D.md) reage ao golpe tambem com um giro na corrente (radianos; o sentido vem do lado de quem
    bateu) e com o amassado na direcao do golpe (a fracao que o saco achata nela, maxima no instante do golpe, e volta oscilando, como
    lona cheia); a constante de tempo e o periodo em ms. PROPOSTO, SEM FONTE */
export const SACO_GIRO = { amplitude: 0.22, tau: 900, periodo: 1500 } as const;
export const SACO_AMASSO = { amplitude: 0.14, tau: 150, periodo: 300 } as const;
/** o maior angulo do balanco na direcao do poste (radianos): no saco gerado, o vao entre o saco e o poste e de ~0,29 celula e o fundo do
    saco fica ~1,84 celula abaixo do pivo, entao o saco toca o poste perto de asin(0,29 / 1,84) = 0,16; com folga, 0,14. PROPOSTO */
export const SACO_FOLGA_POSTE = 0.14;
/** o coco no chao (cocos.ts): o raio do anel em volta do pet onde ele cai e o passo entre aneis (celulas), quanto dura o pulinho ao
    surgir (ms); o desenho e o item gerado (itens.ts, public/itens/coco/); PROPOSTO, SEM FONTE */
export const COCO = { raio: 0.85, passo: 0.25, surgirMs: 380 } as const;

/** os enfeites do mundo humano (docs/TAREFA_V3_MUNDO_ENFEITES.md; grade.ts, porEnfeites), desde a planta A (PLANTA_ILHA) em pontos fixos:
    por enfeite, quantos por mapa e a folga de chao plano em volta (celulas); dos marcos (o carro, a geladeira e o trilho), o chao em que
    cada um pode ficar e a clareira que ele abre na decoracao. PROPOSTO, SEM FONTE */
export const ENFEITES_GRADE = {
  poste: { quantos: 6, folga: 0 },
  carro: { quantos: 1, folga: 1, chao: ["grama"], clareira: 2.2 },
  geladeira: { quantos: 1, folga: 1, chao: ["areia"], clareira: 1.4 },
  trilho: { quantos: 1, folga: 1, chao: ["grama"], clareira: 2.2 },
} as const;
/** a planta A da ilha inicial (docs/pranchas/ux-ilha-layout/, IL-1 a IL-4 DECIDIDAS em 2026-11-08; a vista em docs/pranchas/ux-ilha-planta-a/):
    so a parte da vista, em celulas do mundo (x leste, z sul), a mesma em todo mapa de 64 x 30. O ninho, a tigela, a bola e as frutiferas sao
    do motor (o LayoutMundo) e nao entram aqui.
    - a praca, o no: um disco de terra (`praca`, o centro e o raio);
    - os caminhos de terra (`raioCaminho`) da praca ao lar (ate o comedouro do layout), ao portao, a barraca e ao cais, pelos pontos de
      `caminhos`; cada um para antes da base do lugar (`folgaLugar` alem do raio dele) e so pinta grama da area andavel;
    - os lugares: o `alvo` de cada um (a grade poe no ponto que cabe mais perto dele, em `busca` celulas, com a `folga` de chao plano), a
      `clareira` que ele abre na decoracao e o raio da `base` onde o caminho para; o cais na coluna `x`; o saco perto da praca;
    - os postes (IL-3), cerca de 6, so na praca e no caminho do cais, em grama ou areia; a lampada para o ponto mais perto do caminho;
    - os marcos (a IL-4 de 2026-11-08, revista: "espalha eles tambem pelo mapa"), cada um num canto da moldura, no ponto que cabe mais perto
      do da planta (`busca` celulas), com o entorno dele (extras, a rng propria): o carro meio coberto pelo mato no oeste, a geladeira na
      areia perto do cais e o trilho saindo da mata do leste; `entorno`: quantos arbustos, tufos de grama alta e pedras, ate `raio` celulas;
    - a moldura em bosques e vaos (regras 7 e 8 do levantamento): a arvore e o arbusto da moldura so ficam dentro de um bosque (elipses
      `bosques`: x, z, raio x, raio z) ou na mata a leste do rio; nos `vaos` (o de tras do portao) nada alto fica. Cada bosque ganha as
      arvores e os arbustos dele, com a rng propria (`sal`): `porCelula` arvores por celula da elipse, a distancia minima entre as coisas
      altas, a escala e os arbustos (fracao das arvores) na base, na elipse 1,3 vez maior. Os bosques que a planta
      punha dentro da area do pet ficaram na moldura, encostados nela: o LayoutMundo so aceita arvore com fruta (o desvio da prancha).
    PROPOSTO, SEM FONTE */
export const PLANTA_ILHA = {
  praca: { x: 31, z: 16, raio: 4.2 },
  raioCaminho: 0.8, folgaLugar: 0.6,
  caminhos: {
    lar: [[22, 16], [31, 16]],
    portao: [[31, 16], [31, -1]],
    barraca: [[31, 16], [40, 13], [47, 10]],
    cais: [[31, 16], [36, 24], [38, 31]],
  },
  lugares: {
    portao: { alvo: [31, -2.5], busca: 3, folga: 1, clareira: 3, base: 1.6 },
    barraca: { alvo: [48.5, 8.5], busca: 3, folga: 1, clareira: 3.4, base: 2.4 },
    cais: { x: 38, clareira: 4.5 },
    saco: [22, 9],
  },
  postes: [[27.5, 13], [34.5, 13], [27.5, 19.5], [34.5, 19.5], [33.5, 26], [37, 30]],
  marcos: {
    busca: 2.5,
    carro: { ponto: [-6.5, 19.5], entorno: { arbusto: 6, grama_alta: 8, pedra: 1, raio: 2.8 } },
    geladeira: { ponto: [50, 31.2], entorno: { arbusto: 0, grama_alta: 0, pedra: 3, raio: 2 } },
    trilho: { ponto: [69, 21], entorno: { arbusto: 4, grama_alta: 6, pedra: 2, raio: 2.8 } },
  },
  bosques: [[8, -6, 8, 4.2], [-6, 4, 3.4, 4.6], [-6, 25.6, 3.2, 2.6], [19, -8, 4, 3.4], [44, -6, 6, 3.6], [-5, -6, 4, 3.4], [56, -6, 6, 3.6]],
  vaos: [[31, -6, 5, 5]],
  sal: 0xb05c0e5, bosque: { porCelula: 0.16, entreArvores: 2.2, escalaArvore: [0.9, 1.2], arbustos: 0.5, entreArbustos: 1.2, escalaArbusto: [0.85, 1.15] },
} as const;
/** o fim da ilha (o Matheus, 2026-11-08: "adicionar um final [...] para ela nao acabar no meio do nada"; fimDaIlha.ts e grade.ts, porBordas):
    - a leste do rio, a mata sobe em `degraus` ate o morro: a coluna (a partir da margem leste do rio) onde comeca cada nivel, com a borda
      ondulando ate `ondula` celulas; a decoracao rente a um degrau novo some (a lista `objetos` nao muda, E-G0);
    - o mar em volta da grade inteira, ate o horizonte (`mar`, o lado do quadrado, em celulas);
    - as silhuetas ao longe: duas faixas em volta do ponto olhado (as ilhas perto e os morros longe), a `raio` celulas dele, com a cor da
      nevoa puxada para a sombra (`sombra`, a fracao) e o pe `fundo` celulas abaixo da linha do horizonte do mar curvo, para o mar o cobrir;
      `altura` e a altura da faixa e `alto`, a fracao dela que a silhueta mais alta ocupa; `ilhas` e `morros`, quantos picos por volta.
    PROPOSTO, SEM FONTE */
export const FIM_ILHA = {
  degraus: [4, 7], ondula: 2,
  mar: 1200,
  silhuetas: {
    sal: 0xf1a17e, fundo: -5, altura: 18,
    longe: { raio: 60, sombra: 0.3, alto: 0.72, morros: 7 },
    perto: { raio: 52, sombra: 0.55, alto: 0.42, ilhas: 9 },
  },
} as const;
/** o sinal so (a regra 3 de "guiar o olhar sem texto"): o que se toca (a tigela, a bola e o saco) da um pulinho quando o pet chega a `raio`
    celulas dele; de novo so depois que o pet sair de `sai` celulas. O pulinho: achata e estica `amplitude`, com o periodo e o amortecimento
    em ms. A decoracao nao pula. PROPOSTO, SEM FONTE */
export const CHAMADO = { raio: 1.9, sai: 3, amplitude: 0.12, periodo: 260, tau: 260 } as const;
/** a luz de um lugar aberto (lugaresCena.ts): a cor da mascara de cada lugar (o ciano do portal e dos cristais, tirado da textura) e a
    forca (emissiveIntensity). PROPOSTO, SEM FONTE */
export const LUGAR_LUZ = { cor: { portao: "110,240,230", barraca: "110,240,230", cais: "131,228,218" }, forca: 0.55 } as const;
/** a luz dos enfeites a noite (enfeites.ts): o halo na lanterna, na fracao `altura` da altura do modelo, com `tamanho` celulas de
    diametro, em cascas (as fracoes do tamanho) de opacidade `forca` cada (aditiva), e o quanto os vidros brilham (emissiveIntensity).
    PROPOSTO, SEM FONTE. Com o poste em blocos (2026-11-08, docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 14): a altura 0,86 -> 0,77, o meio
    dos vidros da lanterna nova (33,5 de 43,2 blocos; o 0,86 era o do lampiao antigo); a forca 0,08 -> 0,06 (o revisor leu o halo como um
    anel no Digital, na primeira tentativa do retrabalho) */
export const ENFEITE_HALO = { altura: 0.77, tamanho: 1.1, cascas: [0.55, 0.78, 1], forca: 0.06, vidro: 1.6 } as const;
/** o ceu do estilo digital (estilos.ts; docs/TAREFA_V3_MAPA_DIGITAL.md, D1): a cor do horizonte do ceu pintado (a media da faixa de baixo
    da imagem), para a nevoa, a cor de baixo da luz do ceu de dia, azulada (a sombra do anime), e a nevoa mais longe que a da ilha (o fundo
    de anime tem as arvores de tras nitidas; a de 26 a 62 desbotava tudo, e a de 42 a 95 as deixava pesadas; D2). PROPOSTO, SEM FONTE */
export const CEU_DIGITAL = { horizonte: 0xabe9fe, chaoHemi: 0x6f8fc8, nevoa: [34, 85] } as const;
/** o ceu do estilo digital sem a pintura de anime (o Matheus, 2026-11-08: "Não precisa ser um céu tão cartunesco assim. Ele tá destoando muito
    da arte do jogo. Se for alguma coisa mais pixelada"): `modo` "pixel" (o degrade em `faixas` de cor chapada e as nuvens em pixel, do tamanho
    `px` da grade de cada uma, ampliada sem filtro), "suave" (o degrade liso e as nuvens fofas da ilha) ou "pintado" (o ceu.jpg e as nuvens de
    anime de antes); `?ceu=` no endereco troca so na pagina, para comparar. As cores em tons medios, menos saturadas que as de antes, com o
    horizonte mais claro (o levantamento do ceu, no Obsidian: 20 Temas/Ceu do jogo), e a nevoa da cor do horizonte. PROPOSTO, SEM FONTE */
export const CEU_SEM_PINTURA = {
  /* o Matheus voltou para o pintado no mesmo dia ("A arte anterior estava um pouco melhor. Só que não deixa ela tão forte [...] Diminui um pouco a
     tonalidade do azul dela. Um pouco, não tanto"): o padrao e o pintado, com o azul suavizado por `pintura` (a saturacao que fica e quanto puxa
     para o branco); o pixel e o suave ficam no ?ceu= */
  modo: "pintado" as "pixel" | "suave" | "pintado", pintura: { saturacao: 0.8, clarear: 0.05 }, cores: ["#5f9fd6", "#9ec8e9", "#e3f1f6"], horizonte: 0xe3f1f6, faixas: 11, tela: [480, 270],
  nuvens: { n: 12, px: [40, 16], largura: [16, 28], altura: [11, 19], longe: [22, 40], sombra: "#cfe0ee" },
} as const;
/** as nuvens da pintura no mundo (o Matheus, 2026-11-08: "não tá tendo duas nuvens, uma em cima da outra, né? [...] as nuvens não sejam uma arte
    fixa. Ela tem que acompanhar [...] naquele estilo que tava no desenho"): o ceu.jpg vira o degrade do ceu sem nuvens (a cor do ceu de cada linha)
    e as nuvens recortadas dele, em `pedacos` (x, y, largura e altura em px da imagem); elas ficam num anel em volta da ilha (`raio` e `altura` em
    celulas, `escala` celulas por px), viradas para o centro, e o anel gira devagar (`volta`, segundos por volta; parado com "reduzir movimento").
    `esfumar`: a fracao de cada lado do recorte em que a borda some. `nuvem` e `borda`: a saturacao abaixo da qual (em fracao da do ceu da linha) o pixel e nuvem inteira, e a faixa da borda. PROPOSTO, SEM FONTE */
export const NUVENS_PINTADAS = {
  pedacos: [[0, 250, 760, 360], [540, 15, 836, 515], [680, 560, 340, 92]] as const,
  n: 9, raio: [58, 72], altura: [14, 26], escala: 0.05, volta: 1500, nuvem: 0.35, borda: 0.45, esfumar: 0.18,
  /* o desenho das nuvens do anel (o Matheus, 2026-11-08: o recorte "parece uma nuvem gerada por inteligência artificial [...] pegar uma referência
     de nuvem em jogos"): "recorte" (os pedacos da pintura), "3d" (bolhas de pouco poligono com a base reta e dois tons, como as de jogos de ilha)
     ou "chapada" (o desenho limpo de bolhas, com a faixa de sombra embaixo); o Matheus escolheu o "3d" ("3D de polígonos", 2026-11-08); `?nuvens=` troca so na pagina. `bolhas` quantas por nuvem, `tam` a
     largura de uma nuvem (celulas), `baixa` quanto as desenhadas ficam abaixo da `altura` (sao menores que os recortes), `sombra` a cor de baixo e
     `faixa` a fracao da altura em sombra */
  desenho: "3d" as "recorte" | "3d" | "chapada", bolhas: [4, 7], tam: [22, 38], baixa: 8, sombra: "#c4d6ec", faixa: 0.32,
} as const;
/** o traco de nanquim do estilo digital (pos.ts, Contorno; D5, o cel shading que o Matheus pediu): um azul-petroleo quase preto, a
    largura de ~3 px (o revisor pediu o traco mais grosso), e some entre 34 e 76 celulas da camera (perto do fim da nevoa). PROPOSTO, SEM FONTE */
export const CONTORNO_DIGITAL = { tinta: 0x15222a, forca: 1, largura: 3, limiar: 0.012, some: [34, 76] as const };

/** o toque digital do estilo Digital (digital.ts; docs/TAREFA_V3_MAPA_DIGITAL.md, D3): as particulas (quantas, o sal da rng, a margem
    alem da area, a altura acima do chao, o tamanho, a cor, a opacidade de dia e de noite, o sobe e desce, a velocidade e o giro), a
    grade no ceu (a cor, a opacidade, a espessura, os meridianos de cada lado, os paralelos e o ponto de fuga acima da imagem, em alturas
    dela) e os fios (o alto do poste onde prendem, a fracao da altura; o alcance; quantos por poste; a queda por celula de vao; os
    segmentos; a cor). PROPOSTO, SEM FONTE */
export const DIGITAL = {
  particulas: { quantas: 140, sal: 0xd161a1, margem: 3, altura: [0.6, 3.2], tamanho: 0.06, cor: 0x7ff3ff, opacidade: [0.55, 0.95],
    sobe: 0.25, vel: 0.8, giro: 0.9 },
  /* a grade mais discreta (2026-11-08: "tá muito saturada [...] Deixa ela um pouco mais opaca"): o ciano dessaturado, fraca e so na faixa de baixo do
     ceu, sumindo para cima a partir de `desde` (a fracao da altura da imagem) */
  /* e de novo no mesmo dia: "cadê aquelas linhas no céu? Eu quero aquelas linhas no céu, só que não tão forte": no ceu todo outra vez, mais fracas
     no alto (`topo`, a fracao da forca la em cima) */
  grade: { cor: "#b0e8f0", alfa: 0.3, espessura: 2.5, meridianos: 9, paralelos: 8, fuga: 0.25, topo: 0.55 },
  fios: { alto: 0.93, alcance: 10, porPoste: 2, queda: 0.06, segmentos: 12, cor: 0x2b2a33 },
  /* a lata gigante (D4, o marco), no horizonte como na maquete B: a grade tem 64 celulas de largura e a camera segue o pet, entao um
     marco parado num ponto so apareceria perto dele, e o mundo curvo o afundaria. Ela fica a `longe` celulas ao norte do pet e anda com
     ele so com a fracao 1 - `paralaxe` (o que esta longe quase nao corre na tela); `lado` e a fracao da meia largura visivel a direita
     do meio da tela (a mesma no celular e no desktop, longe do aviso do meio e do painel da direita); o pe fica a `base` do chao do pet,
     com a dobra do mundo descontada (ela nao afunda), e a parte de baixo some atras do penhasco e da mata. A altura passa o dobro de
     um pinheiro; o giro vira a frente (as cerejas, +z do glTF) um pouco para o lado, em tres quartos. Ajustados nas capturas da D4
     (1280 e 390 px): PROPOSTO, SEM FONTE */
  lata: { arquivo: "mapa_digital/lata/lata.gltf", longe: 46, lado: 0.22, paralaxe: 0.12, base: -12, altura: 9, giro: -0.35 },
} as const;
