/* A conta inteira do POC: a divisão arredondada, a raiz inteira, as 16 direções em tabela (nenhuma função transcendental), a rng e o
   hash. Tudo determinístico, e o mesmo em qualquer máquina. */
import { ESCALA } from "./config.ts";

/** n / d arredondado ao mais próximo, meio longe do zero, sem o -0 do JS (o div_arred do Python); d > 0 */
export function divArred(n: number, d: number): number {
  if (d <= 0) throw new Error(`divisor nao positivo: ${d}`);
  const a = Math.abs(n);
  let q = Math.floor(a / d);
  if (2 * (a - q * d) >= d) q += 1;
  return n >= 0 || q === 0 ? q : -q;
}

/** a raiz quadrada inteira (math.isqrt) */
export function isqrt(n: number): number {
  if (!Number.isSafeInteger(n) || n < 0) throw new Error(`isqrt de ${n}`);
  let r = Math.floor(Math.sqrt(n));
  while (r * r > n) r--;
  while ((r + 1) * (r + 1) <= n) r++;
  return r;
}

export const distancia = (dx: number, dy: number): number => isqrt(dx * dx + dy * dy);

/** as 16 direções, (cos, sen) x 1024 de k x 22,5 graus, arredondadas e escritas à mão (o eixo y cresce para o fundo da sala) */
export const DIRECOES_16: readonly (readonly [number, number])[] = [
  [1024, 0], [946, 392], [724, 724], [392, 946], [0, 1024], [-392, 946], [-724, 724], [-946, 392],
  [-1024, 0], [-946, -392], [-724, -724], [-392, -946], [0, -1024], [392, -946], [724, -724], [946, -392],
];

/** o setor (0 a 15) do vetor (dx, dy): o de maior produto escalar com a tabela; no empate, o de menor índice. (0, 0) dá 0 */
export function setorDe(dx: number, dy: number): number {
  let melhor = 0, maior = -Infinity;
  for (let k = 0; k < 16; k++) {
    const [ox, oy] = DIRECOES_16[k];
    const p = dx * ox + dy * oy;
    if (p > maior) { maior = p; melhor = k; }
  }
  return melhor;
}

/** o vetor (dx, dy) com o comprimento `c`, em inteiros; o vetor nulo falha alto */
export function comComprimento(dx: number, dy: number, c: number): [number, number] {
  const d = distancia(dx, dy);
  if (d === 0) throw new Error("direcao de um vetor nulo");
  return [divArred(dx * c, d), divArred(dy * c, d)];
}

/** o ponto a `t` subunidades de (x, y) no setor `s` */
export function noSetor(x: number, y: number, s: number, t: number): [number, number] {
  const [ox, oy] = DIRECOES_16[((s % 16) + 16) % 16];
  return [x + divArred(ox * t, ESCALA), y + divArred(oy * t, ESCALA)];
}

/** o xorshift32: uma rng inteira pequena e igual em todo lugar; a semente 0 falha alto */
export class Rng {
  private s: number;
  constructor(semente: number) {
    if (!Number.isInteger(semente) || (semente >>> 0) === 0) throw new Error(`semente invalida: ${semente}`);
    this.s = semente >>> 0;
  }
  proximo(): number {
    let x = this.s;
    x ^= x << 13; x >>>= 0;
    x ^= x >>> 17;
    x ^= x << 5; x >>>= 0;
    this.s = x;
    return x;
  }
  /** um inteiro em [0, n) */
  inteiro(n: number): number {
    if (!Number.isInteger(n) || n <= 0) throw new Error(`inteiro(${n})`);
    return this.proximo() % n;
  }
  get estado(): number { return this.s; }
}

/** o FNV-1a de 32 bits do texto, em hexadecimal: o hash do estado (não é criptográfico; serve para comparar vidas) */
export function fnv1a(texto: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < texto.length; i++) {
    h ^= texto.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, "0");
}

/** a semente de um fluxo (as rng separadas do ambiente e da política), derivada da semente da vida e do rótulo */
export function derivarSemente(semente: number, rotulo: string): number {
  const h = parseInt(fnv1a(`${semente}|${rotulo}`), 16);
  return h === 0 ? 1 : h;
}
