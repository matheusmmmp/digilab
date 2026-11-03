/* As contas comuns do DigiBrain modular: o espelho de digilab/digibrain/_comum.py (docs/TAREFA_V3_LAB_MODULAR.md, LM1). Aritmetica inteira na
   escala S (DM-2), sem float: `mul(a, b, S) = divArred(a x b, S)`, com o `divArred` do jogo (meio longe do zero), o mesmo do `div_arred` do A. */
import { divArred } from "../mundo.ts";

export { divArred };

/** a chave de uma unidade (b, o): o comportamento, o tipo do alvo (null nos sem alvo) e a identidade do alvo (o id da comida, 0 da bola,
 *  [x, y] do lugar lembrado; null no cheiro, no vagar e nos sem alvo). Ja na forma de lista do `chave_json` do Python. */
export type ChaveUnidade = readonly [string, string | null, number | readonly [number, number] | null];

/** o produto na escala S: div_arred(a x b, S) */
export function mul(a: number, b: number, S: number): number {
  return divArred(a * b, S);
}

export function clamp(v: number, lo: number, hi: number): number {
  return v < lo ? lo : (v > hi ? hi : v);
}

/** a ativacao: clamp(v, 0, A_max) */
export function phi(v: number, aMax: number): number {
  return clamp(v, 0, aMax);
}

/** o ganho por decisao de uma constante de tempo tau (ticks), com tau >= Delta: div_arred(S x Delta, tau) */
export function ganhoDeTau(tau: number, delta: number, S: number): number {
  if (!Number.isInteger(tau) || tau < delta) throw new Error(`constante de tempo ${tau} abaixo do passo do cerebro (${delta} ticks)`);
  return divArred(S * delta, tau);
}

/** um passo do integrador com vazamento (forma I): y + mul(k, u - y) */
export function integrar(y: number, u: number, k: number, S: number): number {
  return y + mul(k, u - y, S);
}

/** modelo_mundo.raiz_inteira: o piso da raiz quadrada, por Newton em inteiros */
export function raizInteira(n: number): number {
  if (!Number.isInteger(n) || n < 0) throw new Error(`raiz inteira de ${n}`);
  if (n < 2) return n;
  let x = n;
  let y = Math.floor((x + 1) / 2);
  while (y < x) {
    x = y;
    y = Math.floor((x + Math.floor(n / x)) / 2);
  }
  return x;
}

/** chave_unidade */
export function chaveUnidade(acao: string, tipo: string | null = null, ident: number | readonly [number, number] | null = null): ChaveUnidade {
  return [acao, tipo, ident];
}

/** chave_json: a chave em listas (aqui ja e a propria chave); null fica null */
export function chaveJson(chave: ChaveUnidade | null): ChaveUnidade | null {
  if (chave === null) return null;
  const ident = chave[2];
  return [chave[0], chave[1], ident !== null && typeof ident === "object" ? [ident[0], ident[1]] as const : ident];
}

/** o texto da chave, para indexar a persistencia (`{texto: h}`): o JSON da chave_json */
export function textoDaChave(chave: ChaveUnidade): string {
  return JSON.stringify(chaveJson(chave));
}

/** o gancho vazio (M-PERS, M-GEN, M-EXPR no que a etapa 1 nao cobre) */
export function semEquacao(modulo: string, metodo: string): Error {
  return new Error(`${modulo}.${metodo}: gancho vazio no prototipo (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.9)`);
}
