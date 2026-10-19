/* A física inteira do WORLD-POC-01a (docs/futuro/mundo_3d.md, seção 3; W-1, o arranjo V): círculos no chão contra retângulos e contra
   outros círculos, em subunidades inteiras. O movimento anda uma subunidade por vez em cada eixo, então nada atravessa uma parede, por
   mais rápido que vá, e o deslize sai sozinho: o eixo bloqueado para, e o outro continua. Sem float, sem transcendental, sem engine. */
import { ATRITO_BOLA, RESTITUICAO } from "./config.ts";
import { divArred, isqrt } from "./inteiros.ts";

/** um retângulo sólido [x0, x1) x [y0, y1) no chão */
export interface Retangulo { x0: number; y0: number; x1: number; y1: number }
/** um sólido com a categoria (o que o contato e os sensores contam) e se tapa a visão */
export interface Solido { ret: Retangulo; categoria: "parede" | "obstaculo"; alto: boolean }
export interface Circulo { x: number; y: number; r: number }

/** o círculo invade o retângulo: o ponto mais perto do retângulo (fechado, [x0, x1] x [y0, y1], a face contínua) fica a menos de r do
 *  centro. Encostado, o centro fica a r da face */
export function circuloNoRetangulo(cx: number, cy: number, r: number, q: Retangulo): boolean {
  const px = Math.min(Math.max(cx, q.x0), q.x1), py = Math.min(Math.max(cy, q.y0), q.y1);
  const dx = cx - px, dy = cy - py;
  return dx * dx + dy * dy < r * r;
}

export function circuloNoCirculo(ax: number, ay: number, ar: number, b: Circulo): boolean {
  const dx = ax - b.x, dy = ay - b.y, s = ar + b.r;
  return dx * dx + dy * dy < s * s;
}

export const pontoNoRetangulo = (x: number, y: number, q: Retangulo): boolean => x >= q.x0 && x < q.x1 && y >= q.y0 && y < q.y1;

/** o que bloqueou um passo: o sólido (pelo índice), ou o outro círculo */
export type Bloqueio = { tipo: "solido"; indice: number } | { tipo: "circulo"; indice: number };

/** o primeiro sólido ou círculo que o círculo (x, y, r) invade, na ordem: sólidos, depois círculos; null se nenhum */
export function bloqueioEm(x: number, y: number, r: number, solidos: readonly Solido[], circulos: readonly Circulo[]): Bloqueio | null {
  for (let i = 0; i < solidos.length; i++) if (circuloNoRetangulo(x, y, r, solidos[i].ret)) return { tipo: "solido", indice: i };
  for (let i = 0; i < circulos.length; i++) if (circuloNoCirculo(x, y, r, circulos[i])) return { tipo: "circulo", indice: i };
  return null;
}

/** o resultado de um movimento: onde parou, quanto andou e o que bloqueou cada eixo */
export interface Movimento {
  x: number; y: number;
  bloqueioX: Bloqueio | null; bloqueioY: Bloqueio | null;
}

/** move o círculo pela velocidade (vx, vy) de um tick: n = max(|vx|, |vy|) passos; em cada um, o ponto alvo é p0 + v i / n
 *  arredondado, e o círculo tenta x e depois y, uma subunidade por vez. Um eixo bloqueado para naquele eixo até o fim do tick (o deslize) */
export function mover(c: Circulo, vx: number, vy: number, solidos: readonly Solido[], circulos: readonly Circulo[]): Movimento {
  const n = Math.max(Math.abs(vx), Math.abs(vy));
  let x = c.x, y = c.y, bloqueioX: Bloqueio | null = null, bloqueioY: Bloqueio | null = null;
  for (let i = 1; i <= n; i++) {
    const ax = c.x + divArred(vx * i, n), ay = c.y + divArred(vy * i, n);
    if (bloqueioX === null && ax !== x) {
      const nx = x + Math.sign(ax - x);
      const b = bloqueioEm(nx, y, c.r, solidos, circulos);
      if (b === null) x = nx; else bloqueioX = b;
    }
    if (bloqueioY === null && ay !== y) {
      const ny = y + Math.sign(ay - y);
      const b = bloqueioEm(x, ny, c.r, solidos, circulos);
      if (b === null) y = ny; else bloqueioY = b;
    }
  }
  return { x, y, bloqueioX, bloqueioY };
}

/** a bola de um tick: move pela velocidade; o eixo bloqueado reflete com a restituição (truncada para zero, então a velocidade nunca
 *  cresce); depois o atrito tira ATRITO_BOLA do módulo, proporcional em cada eixo */
export function passoBola(b: { x: number; y: number; r: number; vx: number; vy: number }, solidos: readonly Solido[],
  circulos: readonly Circulo[]): Movimento {
  const m = mover(b, b.vx, b.vy, solidos, circulos);
  b.x = m.x; b.y = m.y;
  const [num, den] = RESTITUICAO;
  if (m.bloqueioX !== null) b.vx = 0 - Math.trunc((b.vx * num) / den);
  if (m.bloqueioY !== null) b.vy = 0 - Math.trunc((b.vy * num) / den);
  const s = isqrt(b.vx * b.vx + b.vy * b.vy);
  if (s <= ATRITO_BOLA) { b.vx = 0; b.vy = 0; }
  else { b.vx = divArred(b.vx * (s - ATRITO_BOLA), s); b.vy = divArred(b.vy * (s - ATRITO_BOLA), s); }
  return m;
}
