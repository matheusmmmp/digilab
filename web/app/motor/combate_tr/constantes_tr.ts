/* Os numeros da luta em tempo real (docs/ESPEC_COMBATE_TR.md; COMBATE-TR, etapa R1). Os do combate de hoje (o dano, o Guts, as tecnicas,
   as passivas) vem de constantes.ts (CV, CV21, CSO) e nao se repetem aqui; aqui ficam so os do relogio e do espaco. Todo tempo e um
   numero inteiro de passos de 16 ms. Status e fonte de cada um:
   - DECIDIDO (D-5, Matheus, 2026-10-29): o tempo de turno T_TR, o limite e a morte subita;
   - PROPOSTO, com a fonte: "PROTOTIPO" = arena/constantes.ts (o arena.html, sem medicao); "turnos x T_TR" = o numero por turnos de hoje
     convertido pelo T_TR; SEM FONTE onde nao ha. Nenhum foi calibrado: o equilibrio fica para a rodada do fim. */
import { CV } from "../constantes.ts";

/** o passo fixo (ms). PROPOSTO, o da arena (arena/constantes.ts, PASSO_MS) */
export const PASSO_TR_MS = 16;
/** o tempo de turno T_TR em passos: 125 x 16 ms = 2 s. DECIDIDO (D-5); fonte: o ciclo de ataque padrao do prototipo (STATS_PADRAO.cad,
    2 000 ms) igualado a 1 turno */
export const T_TR = 125;

export const CTR_TR = {
  /** o limite da luta: 40 T_TR = 80 s. DECIDIDO (D-5; turnos x T_TR, CV.tMax) */
  limite: CV.tMax * T_TR,
  /** a morte subita: a partir de 25 T_TR = 50 s. DECIDIDO (D-5; turnos x T_TR, CV.turnoMS) */
  morteSubita: CV.turnoMS * T_TR,
  /** o ritmo das decisoes: o lutador livre decide no primeiro passo multiplo disto (16 passos = 256 ms). PROPOSTO; fonte: a reacao da
      CPU "normal" do prototipo (DIFIC.normal.reacao = 260 ms) */
  ritmo: 16,
  /** o instante do golpe dentro da acao (25 passos = 400 ms), igual para todos (D-1). PROPOSTO; fonte: o golpe generico do prototipo
      (arena/dados.ts, GOLPE_GENERICO.t = 0,4 s). A tela estica o clipe do UP para o quadro do golpe cair aqui */
  instante: 25,
  /** o atordoamento de quem tem o preparo interrompido (31 passos ~ 500 ms). PROPOSTO, SEM FONTE */
  atordoaInterrupcao: 31,
  /** px por passo: andar a 70 px/s (STATS_PADRAO.vel, PROTOTIPO); o recuo a 80% do andar (D-8; SEM FONTE); a arrancada da investida a
      420 px/s (ACAO.investidaJogador, PROTOTIPO); o projetil a 300 px/s (SEM FONTE). Todos x 16 / 1000 */
  andar: 70 * PASSO_TR_MS / 1000,
  recuo: .8,
  arrancada: 420 * PASSO_TR_MS / 1000,
  projetil: 300 * PASSO_TR_MS / 1000,
  /** as faixas de distancia (px entre os centros): perto ate 62 (EQ.alcanceCorpo 44 + EQ.raio 18, PROTOTIPO), medio ate 150
      (ACAO.alcanceDist, PROTOTIPO), longe acima. PROPOSTO */
  perto: 62, medio: 150,
  /** o avanco para quando a distancia chega a isto (EQ.alcanceCorpo, PROTOTIPO); os corpos nao chegam mais perto que isto
      ((EQ.raio + EQ.raio) x 0,9, como no passo() da arena, PROTOTIPO). PROPOSTO */
  contato: 44, minimo: 32.4,
  /** o raio do corpo: o projetil acerta ao chegar a isto do centro do alvo (EQ.raio, PROTOTIPO). PROPOSTO */
  raio: 18,
  /** o empurrao de um golpe corpo a corpo que acerta (px; ACAO.empurrao, PROTOTIPO). PROPOSTO, SEM FONTE para manter (espec 1.7) */
  empurrao: 6,
  /** o chao: uma linha no meio da elipse da arena (cx 240, rx 210, cerca a 20 px da borda: nucleo.prender, PROTOTIPO); cada lado entra
      a 65 px do centro (130 px entre os dois: o medio de hoje, estadoV2; SEM FONTE para o valor exato). PROPOSTO */
  centro: 240, meiaLargura: 190, entrada: 65,
} as const;
