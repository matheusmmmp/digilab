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
/** o saco de pancada do treino, em celulas a partir do ninho do layout (no MVP: o ninho em (4, 15), o saco em (7, 11), ao norte entre
    o ninho e o comedouro), e o kit medico da lesao, ao lado do ninho */
export const SACO_DESDE_NINHO: readonly [number, number] = [3, -4], KIT_DESDE_NINHO: readonly [number, number] = [1.3, -1];
/** o treino na ilha: a ida ate o saco, os golpes e a volta (ms); um golpe a cada GOLPE_MS; o pet para a GOLPE_DIST celulas do saco */
export const TREINO_MS = { ida: 900, golpes: 2400, volta: 900 } as const, GOLPE_MS = 600, GOLPE_DIST = 1.35;
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

/** os enfeites do mundo humano na moldura (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 4.3; grade.ts, porEnfeites): o sal da rng propria
    (os objetos de hoje nao mudam, E-G0) e as tentativas por enfeite antes de falhar alto; e, por enfeite, quantos por mapa, a faixa de
    distancia da area andavel (nada alto rente a ela, como as arvores; perto o bastante para a camera ver), a distancia minima dos enfeites ja
    postos (os postes vem antes, e a distancia e a de quem chega) e das coisas altas de hoje, a folga de chao plano em volta (celulas) e se fica so ao norte da area (o lado que a camera da tela
    Pet ve, atras do pet), e entao a ate `casa` celulas do ninho em x. Os repetidos (o poste) e os marcos (o carro). PROPOSTO, SEM FONTE */
export const ENFEITES_GRADE = {
  sal: 0x5e7e17e5, tentativas: 4000,
  poste: { quantos: 14, perto: 1.5, longe: 4, entreSi: 4, deAlto: 2, folga: 0, norte: false, casa: 0 },
  carro: { quantos: 1, perto: 2.4, longe: 4, entreSi: 2.5, entreMarcos: 6.5, deAlto: 2, folga: 1, norte: true, casa: 12 },
  /* a geladeira e o trilho numa faixa de x a partir do ninho que a camera ve sem o painel Estado na frente (o revisor achou o trilho
     atras dele, em x = 20 no mvp) */
  geladeira: { quantos: 1, perto: 1.8, longe: 4, entreSi: 2.5, entreMarcos: 5, deAlto: 1.4, folga: 1, norte: true, casa: 0, faixa: [-14, 16] },
  trilho: { quantos: 1, perto: 2, longe: 5, entreSi: 2.5, entreMarcos: 6, deAlto: 1.2, folga: 1, norte: true, casa: 0, faixa: [-16, 18] },
} as const;
/** onde ficam os lugares da ilha (lugares.ts; docs/TAREFA_V3_LUGARES_3D.md, secao 12): depois dos enfeites, com a rng propria (os
    objetos e os enfeites de hoje nao mudam). O portao e a barraca ao norte da area, no ponto que cabe mais perto do `alvo` (o deslocamento
    a partir do ninho em x; z ao norte da area), onde a camera da tela Pet mais fica: em grama plana com a folga do modelo, longe dos
    enfeites e um do outro, com a frente para a area. O cais na beira do mar, ao sul: na ultima linha de areia antes da agua, numa faixa de x da area (fracao da largura), com o
    comprido ao longo da beira. Cada lugar abre uma `clareira`: a vista nao desenha os objetos da decoracao (nao os do motor) a menos
    disso do centro (Ilha.escondidos). PROPOSTO, SEM FONTE */
export const LUGARES_GRADE = {
  sal: 0x1a6a2e5, tentativas: 4000,
  barraca: { perto: 2, longe: 3.6, folga: 1, deEnfeite: 3.5, clareira: 3.4, alvo: [-1.4, -2.6] },
  portao: { perto: 1.8, longe: 3.6, folga: 1, deEnfeite: 3.2, clareira: 3, alvo: [8, -2.4] },
  cais: { faixa: [0.15, 0.4], clareira: 4.5 },
} as const;
/** a luz de um lugar aberto (lugaresCena.ts): a cor da mascara de cada lugar (o ciano do portal e dos cristais, tirado da textura) e a
    forca (emissiveIntensity). PROPOSTO, SEM FONTE */
export const LUGAR_LUZ = { cor: { portao: "110,240,230", barraca: "110,240,230", cais: "131,228,218" }, forca: 0.55 } as const;
/** a luz dos enfeites a noite (enfeites.ts): o halo na lanterna, na fracao `altura` da altura do modelo, com `tamanho` celulas de
    diametro, em cascas (as fracoes do tamanho) de opacidade `forca` cada (aditiva), e o quanto os vidros brilham (emissiveIntensity).
    PROPOSTO, SEM FONTE */
export const ENFEITE_HALO = { altura: 0.86, tamanho: 1.1, cascas: [0.55, 0.78, 1], forca: 0.08, vidro: 1.6 } as const;
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
