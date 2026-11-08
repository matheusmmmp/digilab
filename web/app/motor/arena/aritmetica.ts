/* A aritmetica da luta (a D-7; docs/TAREFA_V3_LUTA_POC.md, secao 3.2, mudanca 1). O replay refaz a luta em qualquer navegador, e
   Math.hypot e Math.sin podem dar resultados diferentes entre motores de JavaScript. Aqui so entram + - * / e as funcoes de Math que o
   IEEE 754 fixa ou que sao exatas: sqrt, min, max, floor, ceil, round e abs (o teste arena_aritmetica confere pela fonte). */

/** o comprimento de (dx, dy): o Math.hypot da POC, trocado por Math.sqrt(dx*dx + dy*dy) */
export function dist(dx: number, dy: number): number {
  return Math.sqrt(dx * dx + dy * dy);
}

/** pi e 2 pi, como literais (o mesmo double de Math.PI) */
export const PI = 3.141592653589793;
export const DOIS_PI = 6.283185307179586;
/* 2 pi em tres partes (Cody e Waite): a primeira tem os 28 bits baixos zerados, para k * DOIS_PI_A sair exato com |k| < 2^28; as
   outras duas sao o resto de 2 pi (calculado com 60 digitos) */
const DOIS_PI_A = 6.283185243606567;
const DOIS_PI_B = 6.357301909411278e-08;
const DOIS_PI_C = 2.54732686540438e-24;
const MEIO_PI = 1.5707963267948966;

/* os coeficientes de Taylor do seno ate x^19 (1/n! com sinal): em |x| <= pi/2 o erro de truncamento e menor que 2e-18 */
const C3 = -1 / 6, C5 = 1 / 120, C7 = -1 / 5040, C9 = 1 / 362880, C11 = -1 / 39916800, C13 = 1 / 6227020800,
  C15 = -1 / 1307674368000, C17 = 1 / 355687428096000, C19 = -1 / 121645100408832000;

/** o seno por um polinomio fixo: reduz x para [-pi, pi] por 2 pi, rebate para [-pi/2, pi/2] e avalia o polinomio de Taylor de grau 19
    por Horner. Difere do Math.sin do V8 no maximo em poucos ulp; o mesmo em todo navegador */
export function seno(x: number): number {
  const k = Math.round(x / DOIS_PI);
  let r = ((x - k * DOIS_PI_A) - k * DOIS_PI_B) - k * DOIS_PI_C;
  if (r > MEIO_PI) r = PI - r;
  else if (r < -MEIO_PI) r = -PI - r;
  const r2 = r * r;
  return r + r * r2 * (C3 + r2 * (C5 + r2 * (C7 + r2 * (C9 + r2 * (C11 + r2 * (C13 + r2 * (C15 + r2 * (C17 + r2 * C19))))))));
}
