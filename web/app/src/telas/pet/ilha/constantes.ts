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
