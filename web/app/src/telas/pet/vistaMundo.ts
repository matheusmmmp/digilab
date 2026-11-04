/* A vista do mundo fisico dos pets v12 (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2): o que a cena 3D (cena3d.ts) e a reserva
   (MundoReserva.tsx) fazem igual, sem DOM. A vista so le o Motor.mundo, nunca escreve nele; a camera e a interpolacao ficam fora do log.
   - a janela: a camera mostra 16 x 12 celulas do mapa em volta do pet (o tamanho da sala do arranjo V do POC, a cena do Pet dos v1-v11),
     presa nas bordas do mapa;
   - os lugares nomeados do caminho acessivel (MV-4): o comedouro do mapa, "perto do pet" (perto_max_celulas a leste) e "longe"
     (longe_min_celulas para o lado com mais espaco), com as distancias do motor (CMU) e o deslocar do motor, que prende no mapa;
   - o seguidor: a posicao desenhada vai ate a do motor (so vista; caminha pelo intervalo entre as decisoes e se mexe no lugar, ver Seguidor; salta quando a distancia passa de 8 celulas, ao trocar de
     pet ou recarregar). Os numeros da janela e do seguidor sao da vista, nao do jogo: nao mudam a vida. */
import { centroDaCelula, deslocar, regiaoDe, type ConfigMundo } from "../../../motor/index.ts";

/** a janela da camera, em celulas: a sala do arranjo V do POC */
export const JANELA_CELULAS: readonly [number, number] = [16, 12];
/** o pet fica um pouco abaixo do meio da janela (mais chao a frente dele) */
const FRACAO_PET_Y = 0.55;
/** o seguidor: constante de tempo (ms) e o salto (celulas) */
const TAU_MS = 250, SALTO_CELULAS = 8;

export interface Janela { x0: number; y0: number; w: number; h: number }
/** o que a vista le do mundo do motor (Motor.mundo) */
export interface MundoLido { pet: readonly [number, number]; comedouro: readonly [number, number]; cm: ConfigMundo }

const largura = (cm: ConfigMundo) => cm.celulas_x * cm.sub, profundidade = (cm: ConfigMundo) => cm.celulas_y * cm.sub;
const prender = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));

/** a janela de 16 x 12 celulas em volta de `centro` (subunidades), presa no mapa */
export function janelaEm(cm: ConfigMundo, centro: readonly [number, number]): Janela {
  const w = JANELA_CELULAS[0] * cm.sub, h = JANELA_CELULAS[1] * cm.sub;
  return { x0: prender(centro[0] - w / 2, 0, largura(cm) - w), y0: prender(centro[1] - h * FRACAO_PET_Y, 0, profundidade(cm) - h), w, h };
}
/** o ponto e uma posicao do mapa (subunidades inteiras dentro dele)? E o que o motor aceita no deixarComida */
export function dentroDoMapa(cm: ConfigMundo, x: number, y: number): boolean {
  return Number.isInteger(x) && Number.isInteger(y) && x >= 0 && y >= 0 && x < largura(cm) && y < profundidade(cm);
}
export type Lugar = "comedouro" | "perto" | "longe";
export const NOME_LUGAR: Readonly<Record<Lugar, string>> = { comedouro: "Comedouro", perto: "Perto do pet", longe: "Longe" };
/** os lugares nomeados (MV-4): o comedouro do mapa, perto do pet e longe dele, com as distancias e o deslocar do motor */
export function lugaresNomeados(m: MundoLido): Record<Lugar, [number, number]> {
  const { cm } = m, [px, py] = m.pet, leste = px < largura(cm) / 2;
  return {
    comedouro: [m.comedouro[0], m.comedouro[1]],
    perto: deslocar(px, py, 0, cm.perto_max_celulas * cm.sub, cm),
    longe: deslocar(px, py, leste ? 0 : 8, cm.longe_min_celulas * cm.sub, cm),
  };
}
/** o nome da regiao do mapa em x (casa, jardim, campo, mata: o layout do motor) */
export const regiaoEm = (cm: ConfigMundo, x: number): string => cm.layout.regioes[regiaoDe(x, cm)][0];
const ARTIGO: Readonly<Record<string, string>> = { casa: "na", jardim: "no", campo: "no", mata: "na" };
/** "na casa", "no jardim": a regiao em x com o artigo */
export function naRegiao(cm: ConfigMundo, x: number): string {
  const r = regiaoEm(cm, x), a = ARTIGO[r];
  if (!a) throw new Error("regiao do mapa sem artigo na tela: " + r);
  return `${a} ${r}`;
}
/** o ninho do layout, em subunidades */
export const ninhoDe = (cm: ConfigMundo): [number, number] => centroDaCelula(cm.layout.ninho, cm);

/** o que o seguidor precisa saber do jogo para andar e mexer o pet (so vista; tudo vem de fora, o seguidor nao le o motor) */
export interface Movimento {
  /** a velocidade do jogo, em minutos de jogo por segundo (0 = Pausa) */
  velJogo: number;
  /** a acao do motor agora */
  acao: string;
  /** dormindo (ou ovo): fica como era, sem passo novo */
  dorme: boolean;
  /** prefers-reduced-motion: nada novo se mexe */
  reduzido: boolean;
}
/** o intervalo entre duas decisoes do motor, em minutos de jogo (CMU.intervalo = 15) */
export const INTERVALO_DECISAO_MIN = 15;
/** a caminhada ocupa esta fracao do intervalo real (chega antes da proxima decisao), com piso e teto em ms. O teto vale a 1x, onde o
    intervalo real e de 15 min de relogio: sem ele o pet rastejaria sem se ver mexer. O piso (o tau de antes) vale nas velocidades altas */
const FRACAO_CAMINHADA = 0.9, CAMINHADA_MIN_MS = TAU_MS, CAMINHADA_MAX_MS = 6000;
/** as acoes em que o pet fica no lugar do motor: ele se mexe ali, no raio abaixo (subunidades; 16 = uma celula) */
export const ACOES_NO_LUGAR: readonly string[] = ["ocioso", "brincar", "chamar_atencao"];
export const RAIO_NO_LUGAR = 4;
const TAU_PASSINHO_MS = 200, TROCA_MIN_MS = 500, TROCA_VAR_MS = 700;

/** o tempo (ms) que a caminhada de uma decisao leva na velocidade `velJogo` (min de jogo por s) */
export function duracaoCaminhadaMs(velJogo: number): number {
  const intervaloMs = (INTERVALO_DECISAO_MIN / velJogo) * 1000;
  return Math.min(CAMINHADA_MAX_MS, Math.max(CAMINHADA_MIN_MS, intervaloMs * FRACAO_CAMINHADA));
}
function mulberry32(a: number): () => number {
  return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

/** a posicao desenhada, que vai ate a do motor sem pular (so vista). Sem `mov`, o suave de ~250 ms de antes. Com `mov`:
    - andando (o alvo mudou): caminha em velocidade constante e chega em ate 90% do intervalo real entre as decisoes; em Pausa fica parada;
    - nas acoes de ACOES_NO_LUGAR, acordado e ja no alvo: passinhos curtos num raio de RAIO_NO_LUGAR, sempre voltando ao ponto do motor;
    - dormindo ou com movimento reduzido: o suave de antes, sem passinhos. */
export class Seguidor {
  pos: [number, number] | null = null;
  /** a caminhada em curso (a base ainda nao chegou ao alvo): a vista pode usar o clipe de andar */
  caminhando = false;
  /** onde a caminhada esta (sem o passinho) e o alvo dela */
  private base: [number, number] | null = null;
  private alvoVisto: [number, number] | null = null;
  private vel = 0;
  private off: [number, number] = [0, 0];
  private offAlvo: [number, number] = [0, 0];
  private troca = 0;
  private readonly rng: () => number;
  constructor(semente = 1) { this.rng = mulberry32(semente); }

  seguir(alvo: readonly [number, number], dtMs: number, cm: ConfigMundo, mov?: Movimento): [number, number] {
    const b = this.base;
    if (!b || Math.hypot(alvo[0] - b[0], alvo[1] - b[1]) > SALTO_CELULAS * cm.sub) {
      this.base = [alvo[0], alvo[1]]; this.alvoVisto = [alvo[0], alvo[1]]; this.off = [0, 0]; this.offAlvo = [0, 0];
      return (this.pos = [alvo[0], alvo[1]]);
    }
    if (!(dtMs > 0)) return this.pos!;
    if (!mov || mov.dorme || mov.reduzido) {
      /* o suave de antes (e o de quando a Pausa nao e dada) */
      if (mov && mov.velJogo <= 0) return this.pos!;
      const k = 1 - Math.exp(-dtMs / TAU_MS);
      const q: [number, number] = [b[0] + (alvo[0] - b[0]) * k, b[1] + (alvo[1] - b[1]) * k];
      this.base = Math.hypot(alvo[0] - q[0], alvo[1] - q[1]) < 0.05 ? [alvo[0], alvo[1]] : q;
      this.alvoVisto = [alvo[0], alvo[1]]; this.vel = 0; this.caminhando = false; this.off = [0, 0]; this.offAlvo = [0, 0];
      return (this.pos = [this.base[0], this.base[1]]);
    }
    if (!(mov.velJogo > 0)) return this.pos!;                       /* Pausa: nada se mexe */
    const av = this.alvoVisto;
    if (!av || av[0] !== alvo[0] || av[1] !== alvo[1]) {
      this.alvoVisto = [alvo[0], alvo[1]];
      this.vel = Math.hypot(alvo[0] - b[0], alvo[1] - b[1]) / duracaoCaminhadaMs(mov.velJogo);
    }
    const dx = alvo[0] - b[0], dy = alvo[1] - b[1], d = Math.hypot(dx, dy), passo = this.vel * dtMs;
    const andando = d > 0.05;
    this.base = !andando || passo >= d ? [alvo[0], alvo[1]] : [b[0] + (dx / d) * passo, b[1] + (dy / d) * passo];
    const parado = Math.hypot(alvo[0] - this.base[0], alvo[1] - this.base[1]) < 0.05;
    this.caminhando = !parado;
    if (parado && ACOES_NO_LUGAR.includes(mov.acao)) {
      this.troca -= dtMs;
      if (this.troca <= 0) {
        this.troca = TROCA_MIN_MS + this.rng() * TROCA_VAR_MS;
        if (this.offAlvo[0] !== 0 || this.offAlvo[1] !== 0) this.offAlvo = [0, 0];            /* volta ao ponto do motor */
        else {
          const ang = this.rng() * 2 * Math.PI, r = RAIO_NO_LUGAR * (0.4 + 0.6 * this.rng());
          this.offAlvo = [Math.cos(ang) * r, Math.sin(ang) * r];
        }
      }
    } else this.offAlvo = [0, 0];
    const ko = 1 - Math.exp(-dtMs / TAU_PASSINHO_MS);
    let ox = this.off[0] + (this.offAlvo[0] - this.off[0]) * ko, oy = this.off[1] + (this.offAlvo[1] - this.off[1]) * ko;
    if (this.offAlvo[0] === 0 && this.offAlvo[1] === 0 && Math.hypot(ox, oy) < 0.05) { ox = 0; oy = 0; }
    this.off = [ox, oy];
    return (this.pos = [prender(this.base[0] + ox, 0, largura(cm)), prender(this.base[1] + oy, 0, profundidade(cm))]);
  }
}
