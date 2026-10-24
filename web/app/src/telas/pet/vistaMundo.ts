/* A vista do mundo fisico dos pets v12 (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, etapa 2): o que a cena 3D (cena3d.ts) e a reserva
   (MundoReserva.tsx) fazem igual, sem DOM. A vista so le o Motor.mundo, nunca escreve nele; a camera e a interpolacao ficam fora do log.
   - a janela: a camera mostra 16 x 12 celulas do mapa em volta do pet (o tamanho da sala do arranjo V do POC, a cena do Pet dos v1-v11),
     presa nas bordas do mapa;
   - os lugares nomeados do caminho acessivel (MV-4): o comedouro do mapa, "perto do pet" (perto_max_celulas a leste) e "longe"
     (longe_min_celulas para o lado com mais espaco), com as distancias do motor (CMU) e o deslocar do motor, que prende no mapa;
   - o seguidor: a posicao desenhada vai ate a do motor em ~250 ms (so vista; salta quando a distancia passa de 8 celulas, ao trocar de
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

/** a posicao desenhada, que vai ate a do motor sem pular (so vista) */
export class Seguidor {
  pos: [number, number] | null = null;
  seguir(alvo: readonly [number, number], dtMs: number, cm: ConfigMundo): [number, number] {
    const p = this.pos;
    if (!p || Math.hypot(alvo[0] - p[0], alvo[1] - p[1]) > SALTO_CELULAS * cm.sub) return (this.pos = [alvo[0], alvo[1]]);
    if (!(dtMs > 0)) return p;
    const k = 1 - Math.exp(-dtMs / TAU_MS), q: [number, number] = [p[0] + (alvo[0] - p[0]) * k, p[1] + (alvo[1] - p[1]) * k];
    return (this.pos = Math.hypot(alvo[0] - q[0], alvo[1] - q[1]) < 0.05 ? [alvo[0], alvo[1]] : q);
  }
}
