/* As constantes do WORLD-POC-01a (docs/TAREFA_V2_WORLD_POC_01.md). Todas PROPOSTAS e SEM FONTE: o POC é um protótipo técnico, não
   pesquisa, e nenhum destes números entra no motor da pesquisa nem no jogo. Unidade de comprimento: a subunidade do mapa de hoje
   (16 por célula, `ConfigMundo.sub`); unidade de tempo: o tick do POC. */

export const SUB = 16;                       // subunidades por célula
export const CELULAS_X = 16;                 // a sala: 16 x 12 células
export const CELULAS_Y = 12;
export const LARGURA = CELULAS_X * SUB;      // 256 subunidades
export const ALTURA = CELULAS_Y * SUB;       // 192 subunidades
export const ESPESSURA_PAREDE = 8;

export const ESCALA = 1024;                  // a escala inteira das direções e dos receptores de brinquedo
export const R_PET = 6;                      // o círculo do pet no chão
export const VELOCIDADE_PET = 4;             // subunidades por tick (a do mapa de hoje, `ConfigMundo.velocidade`)
export const R_BOLA = 4;
export const IMPULSO_BOLA = 10;              // a velocidade que o empurrão passa à bola, em subunidades por tick
export const ATRITO_BOLA = 1;                // quanto a bola perde de velocidade por tick
export const RESTITUICAO = [3, 4] as const;  // a fração da velocidade normal que a bola mantém na reflexão
export const ALCANCE = 8;                    // o alcance de interação, a partir da borda do círculo
export const DIST_INVESTIGAR = 2 * SUB;      // o investigar para a esta distância do alvo

export const INTERVALO_DECISAO = 15;         // ticks entre duas decisões (o `intervalo_decisao_ticks` de hoje)
export const TICKS_BLOQUEADO = 3;            // ticks sem sair do lugar até o controlador desistir
export const PASSO_SETOR = 4 * SUB;          // o "aproximar(setor)" e o "afastar" andam esta distância

export const RAIO_VISAO = 6 * SUB;           // o raio da visão de hoje (`raio_visao_celulas` 6)
export const COS_MEIO_CONE = 512;            // cos(60 graus) x 1024: o cone da visão tem 120 graus
export const MAX_VISTOS = 8;
export const RAIO_BIGODE = 2 * SUB;          // o alcance dos 8 bigodes

/* o corpo de brinquedo (sem os receptores do corpo químico): fome e tédio em [0, ESCALA] */
export const FOME_POR_TICK = 1;
export const TEDIO_POR_TICK = 1;
export const FOME_COMER = 600;               // quanto o comer tira da fome
export const TEDIO_EMPURRAR = 300;           // quanto um empurrão na bola tira do tédio
export const LIMIAR_FOME = 500;              // o cérebro de teste procura comida acima disto
export const LIMIAR_TEDIO = 400;             // e a bola acima disto
export const RESPAWN_COMIDA = 60;            // ticks até uma comida comida reaparecer noutra célula livre
