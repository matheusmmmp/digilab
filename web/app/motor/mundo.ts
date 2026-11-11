/* O mundo fisico minimo em TS (docs/TAREFA_V2_MUNDO_FISICO.md, etapa 5): o porte de digilab/mundo.py, so o motor e a paridade;
   nenhuma tela e nenhuma versao de pet nova. O mundo e um componente: o mapa, as posicoes inteiras, as arvores, a comida que
   amadurece e apodrece, a bola que rola, a percepcao (visao e cheiro), os alvos e a consequencia de andar, comer e brincar. O engine,
   a politica e o dono ficam com quem usa o mundo; aqui entra o estado do pet (fome, energia, humor, sujeira) e sai o estado depois.

   Os sorteios sao os do Python, numero a numero (o G-PAR da secao 10): cada fluxo e um random.Random do Python semeado por
   derivar_semente (sha256 de "rotulo|rotulo...", os 8 primeiros bytes), entao este arquivo traz o sha256 e o Mersenne Twister com a
   semeadura e os sorteios do CPython (random, getrandbits, randrange, randint). Nada disso usa o mulberry32 do jogo (motor/rng.ts).

   Os registros e o `ocorrido` usam os nomes em snake_case do Python de proposito: sao o mesmo dado, conferido campo a campo. */
import { C, CMU, TPD, type ConfigMundo } from "./constantes.ts";
import {
  CONFIG_CONTRATO, bigodes, contratoLigado, controlar, relativo, setorDe, solido, validarContrato, visivel, type Andar,
  type CategoriaSolido, type ConfigContrato, type Solido,
} from "./contrato.ts";

// ================================================================== sha256 e derivar_semente
const K256 = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be,
  0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa,
  0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85,
  0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
  0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f,
  0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]);

function utf8(texto: string): number[] {
  const b: number[] = [];
  for (const ch of texto) {
    const c = ch.codePointAt(0)!;
    if (c < 0x80) b.push(c);
    else if (c < 0x800) b.push(0xc0 | (c >> 6), 0x80 | (c & 63));
    else if (c < 0x10000) b.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
    else b.push(0xf0 | (c >> 18), 0x80 | ((c >> 12) & 63), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
  }
  return b;
}

/** sha256 de um texto (UTF-8), os 32 bytes */
export function sha256(texto: string): number[] {
  const m = utf8(texto);
  const bits = m.length * 8;
  m.push(0x80);
  while (m.length % 64 !== 56) m.push(0);
  for (let i = 7; i >= 0; i--) m.push(Math.floor(bits / 2 ** (8 * i)) & 0xff);
  const h = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
  const w = new Uint32Array(64);
  const rotr = (x: number, n: number) => (x >>> n) | (x << (32 - n));
  for (let o = 0; o < m.length; o += 64) {
    for (let i = 0; i < 16; i++) w[i] = (m[o + 4 * i] << 24) | (m[o + 4 * i + 1] << 16) | (m[o + 4 * i + 2] << 8) | m[o + 4 * i + 3];
    for (let i = 16; i < 64; i++) {
      const s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3);
      const s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10);
      w[i] = (w[i - 16] + s0 + w[i - 7] + s1) >>> 0;
    }
    let [a, b, c, d, e, f, g, hh] = h;
    for (let i = 0; i < 64; i++) {
      const t1 = (hh + (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) + ((e & f) ^ (~e & g)) + K256[i] + w[i]) >>> 0;
      const t2 = ((rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0;
      hh = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
    }
    h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
  }
  const saida: number[] = [];
  for (const x of h) saida.push(x >>> 24, (x >>> 16) & 0xff, (x >>> 8) & 0xff, x & 0xff);
  return saida;
}

/** protocol.derivar_semente: int.from_bytes(sha256("|".join(str(r)))[:8], "big"), como bigint */
export function derivarSemente(...rotulos: (string | number | bigint)[]): bigint {
  const bytes = sha256(rotulos.map(r => String(r)).join("|"));
  let v = 0n;
  for (let i = 0; i < 8; i++) v = (v << 8n) | BigInt(bytes[i]);
  return v;
}

// ================================================================== o random.Random do Python
const N = 624;

/** O Mersenne Twister do CPython (_randommodule.c) com a semeadura de um int (init_by_array sobre as palavras de 32 bits, da menos
    significativa) e os sorteios de random.py: random(), getrandbits(k <= 32), randrange(n), randint(a, b). */
export class RandomPy {
  private mt = new Uint32Array(N);
  private i = N;

  constructor(semente: number | bigint) {
    let n = typeof semente === "bigint" ? semente : BigInt(semente);
    if (n < 0n) n = -n;
    const chave: number[] = [];
    while (n > 0n) { chave.push(Number(n & 0xffffffffn)); n >>= 32n; }
    if (chave.length === 0) chave.push(0);
    this.porArray(chave);
  }

  private initGenrand(s: number): void {
    const mt = this.mt;
    mt[0] = s >>> 0;
    for (let i = 1; i < N; i++) {
      const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (Math.imul(1812433253, p) + i) >>> 0;
    }
    this.i = N;
  }

  private porArray(chave: number[]): void {
    const mt = this.mt;
    this.initGenrand(19650218);
    let i = 1, j = 0;
    for (let k = Math.max(N, chave.length); k > 0; k--) {
      const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(p, 1664525)) + chave[j] + j) >>> 0;
      i++; j++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
      if (j >= chave.length) j = 0;
    }
    for (let k = N - 1; k > 0; k--) {
      const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(p, 1566083941)) - i) >>> 0;
      i++;
      if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
    }
    mt[0] = 0x80000000;
  }

  private uint32(): number {
    const mt = this.mt;
    if (this.i >= N) {
      for (let k = 0; k < N; k++) {
        const y = (mt[k] & 0x80000000) | (mt[(k + 1) % N] & 0x7fffffff);
        mt[k] = mt[(k + 397) % N] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      this.i = 0;
    }
    let y = mt[this.i++];
    y ^= y >>> 11;
    y ^= (y << 7) & 0x9d2c5680;
    y ^= (y << 15) & 0xefc60000;
    y ^= y >>> 18;
    return y >>> 0;
  }

  /** random(): 53 bits, (a * 2^26 + b) / 2^53 */
  random(): number {
    const a = this.uint32() >>> 5, b = this.uint32() >>> 6;
    return (a * 67108864 + b) * (1 / 9007199254740992);
  }

  getrandbits(k: number): number {
    if (k < 0 || k > 32) throw new Error(`getrandbits fora de [0, 32]: ${k}`);
    if (k === 0) return 0;
    return this.uint32() >>> (32 - k);
  }

  /** _randbelow_with_getrandbits: k = n.bit_length(); sorteia k bits ate dar < n */
  private abaixo(n: number): number {
    if (!Number.isInteger(n) || n <= 0 || n > 2 ** 32) throw new Error(`randrange sem faixa valida: ${n}`);
    const k = n.toString(2).length;                               // n.bit_length()
    let r = this.getrandbits(k);
    while (r >= n) r = this.getrandbits(k);
    return r;
  }

  randrange(inicio: number, fim?: number): number {
    if (fim === undefined) return this.abaixo(inicio);
    return inicio + this.abaixo(fim - inicio);
  }

  randint(a: number, b: number): number {
    return a + this.abaixo(b - a + 1);
  }
}

// ================================================================== a conta inteira (a mesma do Python)
/** div_arred: n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0. */
export function divArred(n: number, d: number): number {
  if (d <= 0) throw new Error(`divisor nao positivo: ${d}`);
  const a = Math.abs(n);
  let q = Math.floor(a / d);
  const r = a - q * d;
  if (2 * r >= d) q += 1;
  return n >= 0 || q === 0 ? q : -q;                           // sem o -0 do JS
}

/** math.isqrt(dx^2 + dy^2) */
export function distancia(dx: number, dy: number): number {
  const n = dx * dx + dy * dy;
  let r = Math.floor(Math.sqrt(n));
  while (r * r > n) r--;
  while ((r + 1) * (r + 1) <= n) r++;
  return r;
}

export const ESCALA_DIR = 1024;
/** as 16 direcoes: (arred(1024 cos a), -arred(1024 sen a)), a = i x 22,5 graus; y cresce para o sul */
export const DIR16: readonly (readonly [number, number])[] = [
  [1024, 0], [946, -392], [724, -724], [392, -946], [0, -1024], [-392, -946], [-724, -724], [-946, -392],
  [-1024, 0], [-946, 392], [-724, 724], [-392, 946], [0, 1024], [392, 946], [724, 724], [946, 392]];
export const ID_BOLA = 0;

/** a direcao do golpe na bola (o direcao_do_golpe do Python; pets v15): das 16, a mais alinhada com o vetor de onde o pet vinha ate a bola (o maior produto
    escalar, em inteiros; no empate, a de menor indice). Com o pet em cima da bola nao ha lado: null */
export function direcaoDoGolpe(px: number, py: number, bx: number, by: number): number | null {
  const dx = bx - px, dy = by - py;
  if (dx === 0 && dy === 0) return null;
  let melhor = 0, maior = -Infinity;
  DIR16.forEach(([cx, cy], k) => { const p = dx * cx + dy * cy; if (p > maior) { maior = p; melhor = k; } });
  return melhor;
}

export function noMapa(x: number, y: number, cm: ConfigMundo = CMU): [number, number] {
  return [Math.min(cm.celulas_x * cm.sub - 1, Math.max(0, x)), Math.min(cm.celulas_y * cm.sub - 1, Math.max(0, y))];
}

export function deslocar(x: number, y: number, direcao: number, comprimento: number, cm: ConfigMundo = CMU): [number, number] {
  const [cx, cy] = DIR16[direcao];
  return noMapa(x + divArred(cx * comprimento, ESCALA_DIR), y + divArred(cy * comprimento, ESCALA_DIR), cm);
}

export function passoAte(x: number, y: number, tx: number, ty: number, alcance: number, cm: ConfigMundo = CMU): [number, number] {
  const dx = tx - x, dy = ty - y;
  const d = distancia(dx, dy);
  if (d <= alcance) return [tx, ty];
  return noMapa(x + divArred(dx * alcance, d), y + divArred(dy * alcance, d), cm);
}

export function centroDaCelula(celula: readonly [number, number], cm: ConfigMundo = CMU): [number, number] {
  return [celula[0] * cm.sub + Math.floor(cm.sub / 2), celula[1] * cm.sub + Math.floor(cm.sub / 2)];
}

/** 0 casa, 1 jardim, 2 campo, 3 mata (a ordem de layout.regioes) */
export function regiaoDe(x: number, cm: ConfigMundo = CMU): number {
  const celula = Math.floor(x / cm.sub);
  const i = cm.layout.regioes.findIndex(([, x0, x1]) => x0 <= celula && celula <= x1);
  if (i < 0) throw new Error(`x fora de toda regiao: ${x}`);
  return i;
}

export type FonteCheiro = readonly [number, number, number];

export function cheiroEm(x: number, y: number, fontes: readonly FonteCheiro[], cm: ConfigMundo = CMU): number {
  const raio = cm.raio_cheiro_celulas * cm.sub;
  let total = 0;
  for (const [fx, fy, a] of fontes) {
    const d = distancia(fx - x, fy - y);
    if (d < raio) total += Math.floor((a * (raio - d)) / raio);
  }
  return total;
}

/** (cheiro no centro, direcao 1 a 8 que passa do centro; a maior vence, no empate a ordem fixa; 0 sem gradiente) */
export function direcaoDoCheiro(x: number, y: number, fontes: readonly FonteCheiro[], cm: ConfigMundo = CMU): [number, number] {
  const centro = cheiroEm(x, y, fontes, cm);
  let melhor = centro, direcao = 0;
  for (let k = 0; k < 8; k++) {
    const [cx, cy] = DIR16[2 * k];
    const c = cheiroEm(x + divArred(cx * cm.sub, ESCALA_DIR), y + divArred(cy * cm.sub, ESCALA_DIR), fontes, cm);
    if (c > melhor) { melhor = c; direcao = k + 1; }
  }
  return [centro, direcao];
}

// ================================================================== os eventos do log (events.deixar_comida, deixar_bola)
export const TIPOS_COMIDA_MUNDO = ["racao", "a", "b", "c"] as const;
export type TipoComidaMundo = typeof TIPOS_COMIDA_MUNDO[number];
export interface EventoMundo { tick: number; tipo: "deixar_comida" | "deixar_bola" | "levar_pet"; valor: string }

function posicaoMundo(x: unknown, y: unknown): [number, number] {
  if (typeof x !== "number" || typeof y !== "number" || !Number.isInteger(x) || !Number.isInteger(y))
    throw new Error(`posicao do mundo nao inteira: (${String(x)}, ${String(y)})`);
  if (!(x >= 0 && x < 1024 && y >= 0 && y < 480)) throw new Error(`posicao fora do mapa: (${x}, ${y})`);
  return [x, y];
}

export function eventoDeixarComida(tick: number, tipo: string, x: unknown, y: unknown): EventoMundo {
  if (!(TIPOS_COMIDA_MUNDO as readonly string[]).includes(tipo)) throw new Error(`tipo de comida desconhecido: ${tipo}`);
  const [px, py] = posicaoMundo(x, y);
  return { tick, tipo: "deixar_comida", valor: `${tipo}|${px}|${py}` };
}

export function eventoDeixarBola(tick: number, x: unknown, y: unknown): EventoMundo {
  const [px, py] = posicaoMundo(x, y);
  return { tick, tipo: "deixar_bola", valor: `${px}|${py}` };
}

function inteiroDoLog(texto: string): number {
  if (!/^[0-9]+$/.test(texto)) throw new Error(`inteiro malformado no log: ${texto}`);
  return Number(texto);
}

export function lerDeixarComida(e: EventoMundo): [TipoComidaMundo, number, number] {
  if (e.tipo !== "deixar_comida") throw new Error(`evento nao e deixar_comida: ${e.tipo}`);
  const p = e.valor.split("|");
  if (p.length !== 3 || !(TIPOS_COMIDA_MUNDO as readonly string[]).includes(p[0])) throw new Error(`deixar_comida malformado: ${e.valor}`);
  const [x, y] = posicaoMundo(inteiroDoLog(p[1]), inteiroDoLog(p[2]));
  return [p[0] as TipoComidaMundo, x, y];
}

export function lerDeixarBola(e: EventoMundo): [number, number] {
  if (e.tipo !== "deixar_bola") throw new Error(`evento nao e deixar_bola: ${e.tipo}`);
  const p = e.valor.split("|");
  if (p.length !== 2) throw new Error(`deixar_bola malformado: ${e.valor}`);
  return posicaoMundo(inteiroDoLog(p[0]), inteiroDoLog(p[1]));
}

/** o levar pet (v19; events.levar_pet do Python): o ponto onde o dono soltou o pet, inteiro e com sinal (fora do mapa vale: quem o limita
    e o Mundo.levarPet, PP-4). So inteiros seguros, como o int do Python que cabe no float do TS */
function pontoSolto(x: unknown, y: unknown): [number, number] {
  if (typeof x !== "number" || typeof y !== "number" || !Number.isSafeInteger(x) || !Number.isSafeInteger(y))
    throw new Error(`levar_pet com posicao nao inteira: (${String(x)}, ${String(y)})`);
  return [x === 0 ? 0 : x, y === 0 ? 0 : y];         // o -0 vira 0 (o log grava "0")
}

/** o inteiro com sinal do log, na forma canonica (sem zero a esquerda, sem "+" e sem "-0"): a mesma regra do Python */
function inteiroComSinalDoLog(texto: string): number {
  if (!/^(0|-?[1-9][0-9]*)$/.test(texto)) throw new Error(`inteiro malformado no log: ${texto}`);
  const n = Number(texto);
  if (!Number.isSafeInteger(n)) throw new Error(`inteiro grande demais no log: ${texto}`);
  return n;
}

export function eventoLevarPet(tick: number, x: unknown, y: unknown): EventoMundo {
  const [px, py] = pontoSolto(x, y);
  return { tick, tipo: "levar_pet", valor: `${px}|${py}` };
}

export function lerLevarPet(e: EventoMundo): [number, number] {
  if (e.tipo !== "levar_pet") throw new Error(`evento nao e levar_pet: ${e.tipo}`);
  const p = e.valor.split("|");
  if (p.length !== 2) throw new Error(`levar_pet malformado: ${e.valor}`);
  return pontoSolto(inteiroComSinalDoLog(p[0]), inteiroComSinalDoLog(p[1]));
}

// ================================================================== percepcao, alvos e o mundo
export type Visto = [number, string, number, number, number];
export interface PercepcaoMundo {
  x: number; y: number; regiao: number; vistos: Visto[]; cheiro: number; direcao_cheiro: number; alvo_pendente: string | null;
  /** so com a chave `sensores` do contrato (a PercepcaoContrato do Python): para onde o cone olha; nenhum cerebro a le */
  orientacao?: number;
}
export interface AlvoMundo { tipo: string; x: number; y: number; id: number | null; de: string | null }
export type AcaoComAlvo = "explorar" | "comer" | "brincar";
export interface EstadoNoMundo { fome: number; energia: number; humor: number; sujeira: number }
export type EscolherAlvo = (acao: AcaoComAlvo, candidatos: AlvoMundo[], percepcao: PercepcaoMundo, u: number) => AlvoMundo | null;

export interface Comida { id: number; tipo: string; x: number; y: number; tick_posta: number; origem: string }
export interface Arvore { id: string; x: number; y: number; fruta: string; regiao: string; p: number; recarga_ate: number }
export interface Bola { x0: number; y0: number; x1: number; y1: number; t0: number; d: number }

const ACOES_COM_ALVO: readonly string[] = ["explorar", "comer", "brincar"];
const FRUTAS = ["a", "b", "c"];

export const alvo = (tipo: string, x: number, y: number, id: number | null = null, de: string | null = null): AlvoMundo => ({ tipo, x, y, id, de });
export const alvoPonto = (x: number, y: number): AlvoMundo => alvo("ponto", x, y);
const mesmoAlvo = (a: AlvoMundo, b: AlvoMundo) => a.tipo === b.tipo && a.x === b.x && a.y === b.y && a.id === b.id && a.de === b.de;
const objetoDo = (a: AlvoMundo): string | null => {
  const t = a.tipo === "continuar" ? a.de : a.tipo;
  return t === "comida" || t === "bola" ? t : null;
};
const comparaStr = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);

export interface OpcoesMundo {
  /** a semente do pet (os fluxos `alvo` e `mundo-sujeira`); sem `partilhado`, tambem a do mundo que ele cria (a vida de hoje) */
  semente: number | bigint;
  cfg?: ConfigMundo;
  efeitoFrutas?: Record<string, number>;
  /** os numeros do estado que o mundo usa (Config do Python) */
  estado?: { ganhoAlimentar: number; probSujeiraPosRefeicao: number; sujeiraMaxima: number; intervalo: number };
  /** o contrato sensorio-motor da P4 (motor/contrato.ts); desligado por padrao, e o jogo nao o liga */
  contrato?: ConfigContrato;
  /** a bola sai na direcao do golpe (pets v15; a ConfigBolaNoGolpe do Python), desligada por padrao: a distancia e o sorteio de sempre,
      a direcao e a em que o pet vinha, de onde ele estava antes do passo ate a bola (direcaoDoGolpe); parado em cima dela, a sorteada. Fora da ConfigMundo de proposito, como o N_PONTOS_LONGE_FIXO do Python: um campo
      novo nela mudaria os gabaritos */
  bolaNoGolpe?: boolean;
  /** CO2b (docs/TAREFA_V3_COOPERACAO.md): o mundo de todos (o do grupo), com a semente do grupo. Sem ele, o pet e dono do proprio
      MundoPartilhado, com a semente do pet: o jogo de hoje, byte a byte */
  partilhado?: MundoPartilhado;
  /** o tick do mundo em que o pet entrou (um inicio de dia; so com `partilhado`): o relogio do pet comeca em 0 nele */
  entrada?: number;
}

// ================================================================== os sentidos sobre o outro (dois pets, etapa 3; degrau 1; CO2c)
// docs/futuro/dois_pets.md, secao 5 (DP-4, DP-11): a visao e o toque, so do que e fisico. O grupo (motor/grupo.ts) monta a percepcao.
/** os candidatos do explorar que so existem com o outro (secao 6) */
export const CANDIDATOS_SOCIAIS: readonly string[] = ["seguir", "onde_comeu"];
export const TIPOS_TOQUE = ["disputa_ganhou", "disputa_perdeu", "encostou", "encostaram", "esbarrou"] as const;
export type TipoToque = typeof TIPOS_TOQUE[number];

/** A PercepcaoSocial do Python (secao 5), sem campo de estado interno do outro: `outros` = (id, dx, dy, d, acao visivel) a ate o raio da
    visao, em ordem de d e de id; `onde_comeu` = (id, x, y, idade) do ultimo consumo visto de cada outro; `toque` = (id, tipo, direcao,
    idade) do ultimo contato; `sentidos` (o degrau 1b) fica null: a cooperacao usa so a visao e o toque */
export interface PercepcaoSocial {
  outros: [string, number, number, number, string][]; onde_comeu: [string, number, number, number][];
  toque: [string, string, number, number][]; sentidos: null;
}

/** o que o grupo da a parte de um pet (o `_grupo` do MotorMundo) */
export interface GanchoGrupo {
  perceberSocial(ident: string): PercepcaoSocial | null;
  viuComer(quem: string, x: number, y: number): void;
}

/** o pendente de um pet; `social`: o id do outro, quando o alvo que ficou e social */
export interface Pendente { acao: AcaoComAlvo; alvo: AlvoMundo; social?: string }

/** o que o grupo le no fim do tick (o `_tick_social` do Python): a partida, o alvo, quem o pet seguiu e o que comeu */
export interface TickSocial {
  tick: number; de: [number, number]; alvo: AlvoMundo | null; pendente_antes: Pendente | null; social: string | null;
  comeu: { id: number; tipo: string; x: number; y: number; situacao: string | null } | null;
}

const chaveAlvo = (a: AlvoMundo): string => `${a.tipo}|${a.x}|${a.y}|${a.id}|${a.de}`;

/** o registro do contrato numa decisao com alvo (o _registro_contrato do Python) */
export interface RegistroContrato {
  tick: number; orientacao: number; parou_por: string; contato: [CategoriaSolido, number][]; obstaculos: number[];
  resultado: { parou_por: string; comeu: boolean; empurrou: boolean; bola_afastou: null }; trajetoria: [number, number][] | null;
}

/** O mundo fisico como componente (o `Mundo` de digilab/mundo.py; docs/futuro/dois_pets.md, secao 2, DP-1; CO2b): as arvores, as
    comidas, a bola, os fluxos do mundo (`mundo-arvores`, `mundo-bola`) e os registros do mundo (as quedas, as comidas que sumiram, as
    bolas deixadas e as rolagens). Nao sabe de pet: a posicao, o pendente, a percepcao guardada, os fluxos do pet (`alvo`,
    `mundo-sujeira`) e os registros do pet ficam no `Mundo` de cada pet (o MotorMundo do Python). Tudo aqui usa o relogio do mundo.

    A atualizacao (quedas, apodrecer, sumir) e idempotente por tick: a segunda chamada no mesmo tick nao faz nada, e um tick para tras
    falha alto. Com dois pets, quem decide primeiro no tick a dispara. */
export class MundoPartilhado {
  readonly cm: ConfigMundo;
  readonly semente: number | bigint;
  readonly rngArvores: RandomPy;
  readonly rngBola: RandomPy;
  readonly raioVisao: number;
  readonly ninho: [number, number];
  readonly comedouro: [number, number];
  bola: Bola;
  readonly arvores: Arvore[] = [];
  readonly comidas = new Map<number, Comida>();
  private proxId_ = ID_BOLA + 1;
  private passoMundo_ = 0;
  private tickAtualizado_: number | null = null;
  // os registros do mundo (derivados; o replay reconstroi tudo)
  readonly quedas: { tick: number; arvore: string; sorteadas: number; pontos: [number, number][]; colocadas: number[] }[] = [];
  readonly sumidas: Record<string, unknown>[] = [];
  readonly bolasDeixadas: { tick: number; x: number; y: number }[] = [];
  readonly rolagens: Record<string, unknown>[] = [];

  constructor(cfg: ConfigMundo, semente: number | bigint) {
    const cm = this.cm = cfg;
    if (!cm.ligada) throw new Error("o Mundo so existe com a ConfigMundo ligada");
    this.semente = semente;
    this.rngArvores = new RandomPy(derivarSemente("mundo-arvores", semente));
    this.rngBola = new RandomPy(derivarSemente("mundo-bola", semente));
    this.raioVisao = cm.raio_visao_celulas * cm.sub;
    this.ninho = centroDaCelula(cm.layout.ninho, cm);
    this.comedouro = centroDaCelula(cm.layout.comedouro, cm);
    const [bx, by] = centroDaCelula(cm.layout.bola_inicio, cm);
    this.bola = { x0: bx, y0: by, x1: bx, y1: by, t0: 0, d: 0 };
    for (const [id, x, y, fruta] of cm.layout.arvores) {
      if (!FRUTAS.includes(fruta)) throw new Error(`arvore ${id} com fruta desconhecida: ${fruta}`);
      const [ax, ay] = centroDaCelula([x, y], cm);
      const nome = cm.layout.regioes[regiaoDe(ax, cm)][0];
      let p: number;
      if (nome === "jardim") p = cm.p_queda_jardim * cm.mult_queda;
      else if (nome === "mata") p = cm.p_queda_mata * cm.mult_queda;
      else throw new Error(`arvore ${id} fora do jardim e da mata: ${nome}`);
      this.arvores.push({ id, x: ax, y: ay, fruta, regiao: nome, p, recarga_ate: 0 });
    }
  }

  get proxId(): number { return this.proxId_; }
  get passoMundo(): number { return this.passoMundo_; }
  get tickAtualizado(): number | null { return this.tickAtualizado_; }

  // ------------------------------------------------------------ a comida e a bola no tempo
  prazoMaduro(tipo: string): number {
    return tipo === "racao" ? this.cm.maduro_racao_min : this.cm.maduro_fruta_min;
  }

  situacao(c: { tipo: string; tick_posta: number }, tick: number): "madura" | "podre" | null {
    const idade = tick - c.tick_posta;
    const m = this.prazoMaduro(c.tipo);
    if (idade < m) return "madura";
    if (idade < m + this.cm.prazo_podre_min) return "podre";
    return null;
  }

  bolaEm(tick: number): [number, number] {
    const b = this.bola;
    if (b.d === 0 || tick >= b.t0 + Math.ceil(b.d / this.cm.atrito)) return [b.x1, b.y1];
    const andou = this.cm.atrito * (tick - b.t0);
    return [b.x0 + divArred((b.x1 - b.x0) * andou, b.d), b.y0 + divArred((b.y1 - b.y0) * andou, b.d)];
  }

  novaComida(tipo: string, x: number, y: number, tick: number, origem: string): Comida {
    const c: Comida = { id: this.proxId_++, tipo, x, y, tick_posta: tick, origem };
    this.comidas.set(c.id, c);
    return c;
  }

  private removerSumidas(tick: number): void {
    for (const c of [...this.comidas.values()].filter(c => this.situacao(c, tick) === null)) {
      this.comidas.delete(c.id);
      this.sumidas.push({ ...c, sumiu_em: c.tick_posta + this.prazoMaduro(c.tipo) + this.cm.prazo_podre_min });
    }
  }

  /** os passos do mundo ate o tick: cada arvore fora da recarga sorteia a queda no fluxo `mundo-arvores`. Idempotente por tick (quem
      decide primeiro dispara); um tick para tras falha alto */
  atualizar(tick: number): void {
    if (this.tickAtualizado_ !== null) {
      if (tick < this.tickAtualizado_)
        throw new Error(`o mundo nao volta no tempo: atualizado ate o tick ${this.tickAtualizado_}, pedido o ${tick}`);
      if (tick === this.tickAtualizado_) return;
    }
    const cm = this.cm, rng = this.rngArvores;
    const ate = Math.floor(tick / cm.passo_mundo_ticks);
    while (this.passoMundo_ < ate) {
      this.passoMundo_++;
      const tk = this.passoMundo_ * cm.passo_mundo_ticks;
      for (const arv of this.arvores) {
        if (tk < arv.recarga_ate) continue;
        if (rng.random() >= arv.p) continue;
        const n = rng.randint(cm.frutas_por_queda_min, cm.frutas_por_queda_max);
        const pontos: [number, number][] = [];
        for (let i = 0; i < n; i++) {
          const dir = rng.randrange(16);
          pontos.push(deslocar(arv.x, arv.y, dir, rng.randrange(cm.raio_queda_celulas * cm.sub + 1), cm));
        }
        let noChao = 0;
        for (const c of this.comidas.values()) if (c.origem === arv.id && this.situacao(c, tk) !== null) noChao++;
        const cabem = Math.max(0, cm.max_frutas_por_arvore - noChao);
        const ids = pontos.slice(0, cabem).map(([x, y]) => this.novaComida(arv.fruta, x, y, tk, arv.id).id);
        this.quedas.push({ tick: tk, arvore: arv.id, sorteadas: n, pontos, colocadas: ids });
        arv.recarga_ate = tk + cm.recarga_min;
      }
    }
    this.removerSumidas(tick);
    this.tickAtualizado_ = tick;
  }

  // ------------------------------------------------------------ percepcao
  fontesDeCheiro(tick: number): FonteCheiro[] {
    const f: FonteCheiro[] = [];
    for (const c of this.comidas.values())
      if (this.situacao(c, tick) === "madura") f.push([c.x, c.y, c.tipo === "racao" ? this.cm.cheiro_racao : this.cm.cheiro_fruta]);
    return f;
  }

  /** pura: o que um pet em (x, y) percebe agora; `alvoPendente` e o do pet, `ve` o filtro do cone e da oclusao (o contrato; null: tudo) */
  perceber(x: number, y: number, tick: number, alvoPendente: string | null, ve: ((ox: number, oy: number) => boolean) | null = null)
      : PercepcaoMundo {
    const vistos: Visto[] = [];
    for (const c of this.comidas.values()) {
      const sit = this.situacao(c, tick);
      if (sit === null) continue;
      const dx = c.x - x, dy = c.y - y, d = distancia(dx, dy);
      if (d <= this.raioVisao && (ve === null || ve(c.x, c.y))) vistos.push([c.id, sit === "madura" ? c.tipo : c.tipo + "_podre", dx, dy, d]);
    }
    const [bx, by] = this.bolaEm(tick);
    const db = distancia(bx - x, by - y);
    if (db <= this.raioVisao && (ve === null || ve(bx, by))) vistos.push([ID_BOLA, "bola", bx - x, by - y, db]);
    vistos.sort((a, b) => a[4] - b[4] || comparaStr(a[1], b[1]) || a[0] - b[0]);
    const [cheiro, direcao] = direcaoDoCheiro(x, y, this.fontesDeCheiro(tick), this.cm);
    return { x, y, regiao: regiaoDe(x, this.cm), vistos: vistos.slice(0, this.cm.max_vistos), cheiro, direcao_cheiro: direcao,
             alvo_pendente: alvoPendente };
  }

  /** as comidas maduras a ate `raio` de (x, y), em (distancia, tipo, id), da mais perto (o "achou e comeu" do explorar, MF-1) */
  madurasPerto(x: number, y: number, tick: number, raio: number): [number, string, number][] {
    const perto: [number, string, number][] = [];
    for (const c of this.comidas.values())
      if (this.situacao(c, tick) === "madura") perto.push([distancia(c.x - x, c.y - y), c.tipo, c.id]);
    perto.sort((p, q) => p[0] - q[0] || comparaStr(p[1], q[1]) || p[2] - q[2]);
    return perto.filter(p => p[0] <= raio);
  }

  // ------------------------------------------------------------ o que muda o mundo
  /** a comida sai do chao (alguem a comeu); a que nao esta no chao falha alto */
  retirarComida(ident: number): Comida {
    const c = this.comidas.get(ident);
    if (c === undefined) throw new Error(`comida fora do chao: ${ident}`);
    this.comidas.delete(ident);
    return c;
  }

  /** alguem brincou com a bola: ela rola do ponto em que esta, no fluxo `mundo-bola` (vai mais longe no campo). Com `de` (a posicao de
      quem bateu; a bolaNoGolpe), a direcao e a do golpe; o sorteio dela fica no fluxo, e a distancia sai a mesma */
  rolarBola(tick: number, de: readonly [number, number] | null): void {
    const cm = this.cm;
    const [bx, by] = this.bolaEm(tick);
    const sorteada = this.rngBola.randrange(16);
    const golpe = de === null ? null : direcaoDoGolpe(de[0], de[1], bx, by);
    const direcao = golpe ?? sorteada;
    let celulas = this.rngBola.randint(cm.bola_min_celulas, cm.bola_max_celulas);
    if (cm.layout.regioes[regiaoDe(bx, cm)][0] === "campo") celulas *= cm.mult_bola_campo;
    const [x1, y1] = deslocar(bx, by, direcao, celulas * cm.sub, cm);
    this.bola = { x0: bx, y0: by, x1, y1, t0: tick, d: distancia(x1 - bx, y1 - by) };
    this.rolagens.push({ tick, de: [bx, by], para: [x1, y1], direcao, celulas });
  }

  /** a comida que o dono deixa (origem `dono`); tipo desconhecido ou posicao fora do mapa falha alto (como o log) */
  deixarComida(tipo: string, x: number, y: number, tick: number): Comida {
    lerDeixarComida(eventoDeixarComida(tick, tipo, x, y));
    return this.novaComida(tipo, x, y, tick, "dono");
  }

  /** o dono poe a bola parada em (x, y); fora do mapa falha alto */
  deixarBola(x: number, y: number, tick: number): void {
    lerDeixarBola(eventoDeixarBola(tick, x, y));
    this.bola = { x0: x, y0: y, x1: x, y1: y, t0: tick, d: 0 };
    this.bolasDeixadas.push({ tick, x, y });
  }

  /** o Mundo.resumo do Python, sem as rngs: tudo o que o mundo guarda, sem o que e do pet */
  resumo(): Record<string, unknown> {
    return {
      bola: { ...this.bola }, comidas: [...this.comidas.values()].map(c => ({ ...c })), prox_id: this.proxId_,
      passo_mundo: this.passoMundo_, tick_atualizado: this.tickAtualizado_, arvores: this.arvores.map(a => ({ ...a })),
      quedas: this.quedas, sumidas: this.sumidas, bolas_deixadas: this.bolasDeixadas, rolagens: this.rolagens,
    };
  }
}

/** A parte de um pet no mundo fisico (o MotorMundo ligado de digilab/mundo.py): a posicao, o alvo pendente, a percepcao da decisao, os
    fluxos `alvo` e `mundo-sujeira`, os registros do pet (consumos, decisoes, regioes, visitas, comidas deixadas, levadas) e o contrato
    da P4. O que e do mundo mora no `MundoPartilhado` (`comum`). Sem `partilhado`, o pet e dono do proprio, com a semente dele: o jogo de
    hoje, byte a byte; os atributos de antes (`comidas`, `arvores`, `bola`, `quedas`...) leem de la.

    Os metodos recebem o tick do pet; o mundo e os registros do mundo fisico usam o do mundo (o do pet mais a `entrada`). Com um pet so,
    a entrada e 0 e os dois relogios sao o mesmo. */
export class Mundo {
  readonly cm: ConfigMundo;
  readonly comum: MundoPartilhado;
  readonly entrada: number;
  readonly efeitoFrutas: Record<string, number>;
  private readonly ganhoAlimentar: number;
  private readonly probSujeira: number;
  private readonly sujeiraMaxima: number;
  readonly alcance: number;
  private readonly intervalo: number;
  private readonly raioPegar: number;
  private readonly raioVisao: number;
  private readonly raioMancha: number;
  readonly rngSujeira: RandomPy;
  readonly rngAlvo: RandomPy;
  readonly bolaNoGolpe: boolean;
  pet: [number, number];
  private pendente: Pendente | null = null;
  private fomeAntes = 0;
  private percepcao: PercepcaoMundo | null = null;
  private readonly manchasAbertas = new Map<string, { arvore: string; chegada: number; saida: number | null; decisoes: number }>();
  ultimosCandidatos: AlvoMundo[] | null = null;
  // os registros do pet (derivados; o replay reconstroi tudo)
  readonly consumos: Record<string, unknown>[] = [];
  readonly deixadas: Record<string, unknown>[] = [];
  /** v19: cada vez que o dono levou o pet (o tick, de onde, o ponto pedido e onde ele caiu, ja no mapa) */
  readonly levadas: { tick: number; de: [number, number]; pedido: [number, number]; para: [number, number] }[] = [];
  readonly decisoes: Record<string, unknown>[] = [];
  readonly regioes: { tick: number; de: number; para: number }[] = [];
  readonly visitas: { arvore: string; chegada: number; saida: number | null; decisoes: number }[] = [];
  // o contrato da P4 (desligado: nada disto muda o mundo de hoje)
  readonly cct: ConfigContrato;
  private solidos: readonly Solido[] = [];                     // os que colidem (as paredes, com a chave delas)
  private opacos: readonly Solido[] = [];                      // os que tapam (as paredes e os troncos)
  orientacao = 0;
  readonly contratoDecisoes: RegistroContrato[] = [];
  // dois pets (CO2c): o grupo e o id do pet nele (o Grupo poe na entrada); fora do grupo, nada disto e usado e a vida e a de hoje
  private grupo: GanchoGrupo | null = null;
  ident: string | null = null;
  /** a percepcao social da decisao (null sozinho ou fora do grupo) */
  social: PercepcaoSocial | null = null;
  private readonly candsSociais = new Map<string, string>();   // o candidato social da decisao -> o id do outro
  private pendenteAntes: Pendente | null = null;                // o alvo pendente com que a decisao comecou (a disputa)
  /** o que o grupo le no fim do tick */
  tickSocial: TickSocial | null = null;
  /** a memoria da visao: id -> (x, y, tick do mundo) do ultimo consumo visto de cada outro */
  readonly viuComerDe = new Map<string, [number, number, number]>();
  /** a memoria do toque: id -> (tipo, direcao, tick do mundo) do ultimo contato com cada outro */
  readonly toques = new Map<string, [string, number, number]>();
  // os registros sociais do pet (as medidas; derivados, o replay refaz)
  readonly vistosComer: { tick: number; outro: string; x: number; y: number; d: number }[] = [];
  readonly idasOndeComeu: Record<string, unknown>[] = [];
  readonly aVista: Record<string, number> = {};                 // decisoes com cada outro a vista
  decisoesNoGrupo = 0;                                          // decisoes com outro pet presente

  constructor(op: OpcoesMundo) {
    const dado = op.partilhado;
    const cm = this.cm = op.cfg ?? (dado ? dado.cm : CMU);
    if (!cm.ligada) throw new Error("o Mundo so existe com a ConfigMundo ligada");
    const ef = op.efeitoFrutas ?? { a: 0, b: 0, c: 0 };
    if (Object.keys(ef).sort().join() !== FRUTAS.join()) throw new Error(`efeitoFrutas precisa de a, b e c: ${Object.keys(ef)}`);
    this.efeitoFrutas = { ...ef };
    const es = op.estado ?? { ganhoAlimentar: C.ganhoAlim, probSujeiraPosRefeicao: C.probSujRef, sujeiraMaxima: C.sujMax, intervalo: C.intervalo };
    this.ganhoAlimentar = es.ganhoAlimentar;
    this.probSujeira = es.probSujeiraPosRefeicao;
    this.sujeiraMaxima = es.sujeiraMaxima;
    this.alcance = cm.velocidade * es.intervalo;
    this.intervalo = es.intervalo;
    this.raioPegar = cm.raio_pegar_celulas * cm.sub;
    this.raioVisao = cm.raio_visao_celulas * cm.sub;
    this.raioMancha = cm.raio_mancha_celulas * cm.sub;
    if (dado === undefined) {
      if (op.entrada !== undefined && op.entrada !== 0) throw new Error("entrada so com um MundoPartilhado dado (o do grupo)");
      this.comum = new MundoPartilhado(cm, op.semente);       // com um pet, ele e dono do proprio mundo (a semente do mundo e a do pet)
      this.entrada = 0;
    } else {                                                   // no grupo: o mundo e de todos, e o pet entra num tick dele
      if (!(dado instanceof MundoPartilhado) || JSON.stringify(dado.cm) !== JSON.stringify(cm))
        throw new Error("o MundoPartilhado dado tem de ter a mesma ConfigMundo do pet");
      const e = op.entrada ?? 0;
      if (!Number.isInteger(e) || e < 0 || e % TPD) throw new Error(`entrada tem de ser um inicio de dia do mundo (multiplo de ${TPD}): ${e}`);
      this.comum = dado;
      this.entrada = e;
    }
    this.rngSujeira = new RandomPy(derivarSemente("mundo-sujeira", op.semente));
    this.rngAlvo = new RandomPy(derivarSemente("alvo", op.semente));
    this.bolaNoGolpe = op.bolaNoGolpe ?? false;
    this.pet = [this.comum.ninho[0], this.comum.ninho[1]];
    this.cct = validarContrato({ ...(op.contrato ?? CONFIG_CONTRATO) });
    if (contratoLigado(this.cct)) {
      if (dado !== undefined) throw new Error("o contrato da P4 roda com um pet, fora do grupo");
      this.montarContrato();
    }
  }

  /** o tick do pet no relogio do mundo */
  tm(tick: number): number {
    return tick + this.entrada;
  }

  /** o Grupo poe o pet nele (so com o mundo partilhado dado); uma vez so */
  ligarGrupo(grupo: GanchoGrupo, ident: string): void {
    if (this.grupo !== null) throw new Error(`o pet ${this.ident} ja esta num grupo`);
    if (!ident) throw new Error("o pet do grupo precisa de um id");
    this.grupo = grupo;
    this.ident = ident;
  }

  /** o raio da visao do pet (o grupo: quem ve o outro comer, quem esta a vista) */
  get raioDaVisao(): number { return this.raioVisao; }

  /** o alvo que ficou sem chegar (o grupo: a disputa de quem nao decidiu no tick) */
  get pendenteAtual(): Pendente | null { return this.pendente; }

  // ------------------------------------------------------------ o que e do mundo, lido de la (os atributos de antes)
  get rngArvores(): RandomPy { return this.comum.rngArvores; }
  get rngBola(): RandomPy { return this.comum.rngBola; }
  get comedouro(): [number, number] { return this.comum.comedouro; }
  get bola(): Bola { return this.comum.bola; }
  get arvores(): Arvore[] { return this.comum.arvores; }
  get comidas(): Map<number, Comida> { return this.comum.comidas; }
  get quedas(): MundoPartilhado["quedas"] { return this.comum.quedas; }
  get sumidas(): Record<string, unknown>[] { return this.comum.sumidas; }
  get bolasDeixadas(): { tick: number; x: number; y: number }[] { return this.comum.bolasDeixadas; }
  get rolagens(): Record<string, unknown>[] { return this.comum.rolagens; }

  /** as paredes na borda (so com a chave `paredes`; solidas e opacas) e os quadrados dos troncos (com a chave `sensores`; opacos, sem
      colisao, P4-4), na ordem do Python (o _montar_contrato) */
  private montarContrato(): void {
    const cc = this.cct, cm = this.cm;
    const largura = cm.celulas_x * cm.sub, altura = cm.celulas_y * cm.sub, e = cc.espessura_parede;
    const paredes = cc.paredes
      ? [solido(-e, -e, largura + e, 0, "parede", true, true), solido(-e, altura, largura + e, altura + e, "parede", true, true),
         solido(-e, 0, 0, altura, "parede", true, true), solido(largura, 0, largura + e, altura, "parede", true, true)]
      : [];
    const meio = Math.floor(cc.lado_tronco / 2);
    const troncos = cc.sensores
      ? this.arvores.map(a => solido(a.x - meio, a.y - meio, a.x - meio + cc.lado_tronco, a.y - meio + cc.lado_tronco, "tronco", false, true))
      : [];
    this.solidos = Object.freeze(paredes);
    this.opacos = Object.freeze([...paredes, ...troncos]);
  }

  // ------------------------------------------------------------ a comida e a bola no tempo (o tick do pet)
  situacao(c: { tipo: string; tick_posta: number }, tick: number): "madura" | "podre" | null {
    return this.comum.situacao(c, this.tm(tick));
  }

  bolaEm(tick: number): [number, number] {
    return this.comum.bolaEm(this.tm(tick));
  }

  atualizar(tick: number): void {
    this.comum.atualizar(this.tm(tick));
  }

  // ------------------------------------------------------------ percepcao
  /** pura: o que o pet percebe agora */
  perceber(tick: number): PercepcaoMundo {
    const [x, y] = this.pet;
    /* com a chave `sensores`: so o que passa pelo cone em torno da orientacao e pela oclusao (o Mundo.perceber com o contrato) */
    const sens = this.cct.sensores;
    const ve = sens
      ? (ox: number, oy: number): boolean => visivel(x, y, ox, oy, this.orientacao, this.raioVisao, this.cct.cos_meio_cone, this.opacos)
      : null;
    const p = this.comum.perceber(x, y, this.tm(tick), this.pendente ? this.pendente.alvo.tipo : null, ve);
    if (sens) p.orientacao = this.orientacao;
    return p;
  }

  /** antes de cada decisao: o mundo anda ate o tick e o pet percebe (a fome de antes fica para o MF-2) */
  antesDaDecisao(tick: number, fome: number): PercepcaoMundo {
    this.atualizar(tick);
    this.percepcao = this.perceber(tick);
    this.fomeAntes = fome;
    if (this.grupo !== null) {
      this.social = this.grupo.perceberSocial(this.ident!);
      this.pendenteAntes = this.pendente;
      this.candsSociais.clear();
      if (this.social !== null) {
        this.decisoesNoGrupo++;
        for (const [ident] of this.social.outros) this.aVista[ident] = (this.aVista[ident] ?? 0) + 1;
      }
    }
    return this.percepcao;
  }

  // ------------------------------------------------------------ os alvos
  private alvoCheiro(p: PercepcaoMundo): AlvoMundo {
    const [x, y] = deslocar(p.x, p.y, 2 * (p.direcao_cheiro - 1), this.cm.passo_cheiro_celulas * this.cm.sub, this.cm);
    return alvo("cheiro", x, y);
  }

  private continuar(acao: AcaoComAlvo, tick: number): AlvoMundo | null {
    const pend = this.pendente;
    if (!pend || pend.acao !== acao) return null;
    const velho = pend.alvo;
    if (velho.tipo === "comida") {
      const c = this.comidas.get(velho.id!);
      return c ? alvo("continuar", c.x, c.y, velho.id, "comida") : null;
    }
    if (velho.tipo === "bola") {
      const [bx, by] = this.bolaEm(tick);
      return alvo("continuar", bx, by, ID_BOLA, "bola");
    }
    return alvo("continuar", velho.x, velho.y, null, velho.tipo);
  }

  candidatos(acao: AcaoComAlvo, u: number, tick: number): AlvoMundo[] {
    const p = this.percepcao!, cm = this.cm;
    const cands: AlvoMundo[] = [];
    if (acao === "comer") {
      for (const [i, tipo, dx, dy] of p.vistos) if (tipo !== "bola") cands.push(alvo("comida", p.x + dx, p.y + dy, i));
      if (p.direcao_cheiro) cands.push(this.alvoCheiro(p));
    } else if (acao === "explorar") {
      if (p.direcao_cheiro) cands.push(this.alvoCheiro(p));
      const faixa = cm.vagar_max_celulas - cm.vagar_min_celulas + 1;
      const [vx, vy] = deslocar(p.x, p.y, u % 16, (cm.vagar_min_celulas + (Math.floor(u / 16) % faixa)) * cm.sub, cm);
      cands.push(alvo("vagar", vx, vy));
      cands.push(alvo("casa", this.comedouro[0], this.comedouro[1]));
    } else {
      for (const [i, tipo, dx, dy] of p.vistos) if (tipo === "bola") cands.push(alvo("bola", p.x + dx, p.y + dy, i));
    }
    const cont = this.continuar(acao, tick);
    if (cont) cands.push(cont);
    if (acao === "explorar" && this.social !== null) cands.push(...this.candidatosSociais(p));
    return cands;
  }

  /** dois pets, secao 6: `seguir` cada outro visto (onde ele esta) e `onde_comeu` de cada outro que este pet viu comer, depois dos de
      hoje. O padrao do motor nunca os escolhe; so o cerebro */
  private candidatosSociais(p: PercepcaoMundo): AlvoMundo[] {
    const cands: AlvoMundo[] = [];
    for (const [ident, dx, dy] of this.social!.outros) {
      const a = alvo("seguir", p.x + dx, p.y + dy);
      this.candsSociais.set(chaveAlvo(a), ident);
      cands.push(a);
    }
    for (const [ident, x, y] of this.social!.onde_comeu) {
      const a = alvo("onde_comeu", x, y);
      this.candsSociais.set(chaveAlvo(a), ident);
      cands.push(a);
    }
    return cands;
  }

  /** o id do outro de um alvo social (seguir, onde_comeu, ou o continuar deles), ou null */
  private idSocial(a: AlvoMundo | null): string | null {
    if (a === null) return null;
    if (CANDIDATOS_SOCIAIS.includes(a.tipo)) {
      const id = this.candsSociais.get(chaveAlvo(a));
      if (id === undefined) throw new Error(`alvo social fora dos candidatos: ${JSON.stringify(a)}`);
      return id;
    }
    if (a.tipo === "continuar" && a.de !== null && CANDIDATOS_SOCIAIS.includes(a.de)) {
      const id = this.pendenteAntes?.social;
      if (id === undefined) throw new Error(`continuar social sem o outro no pendente: ${JSON.stringify(a)}`);
      return id;
    }
    return null;
  }

  /** a ida a `onde_comeu` (a confianca da secao 8 sai daqui): chegou, comeu, e quantas comidas boas estavam a vista na chegada */
  private registrarSocial(a: AlvoMundo, chegou: boolean, comeu: Record<string, unknown> | null, x1: number, y1: number, tick: number): void {
    const classe = a.tipo === "continuar" ? a.de : a.tipo;
    if (classe !== "onde_comeu") return;
    const tm = this.tm(tick);
    this.idasOndeComeu.push({
      tick: tm, outro: this.idSocial(a), x: a.x, y: a.y, continuacao: a.tipo === "continuar", chegou,
      comeu: comeu === null ? null : { id: comeu.id, tipo: comeu.tipo, situacao: comeu.situacao, como: comeu.como },
      boas_a_vista: chegou ? this.comum.madurasPerto(x1, y1, tm, this.raioVisao).length : null,
    });
  }

  /** o que o instinto usa; nunca escolhe comida podre */
  alvoPadrao(acao: AcaoComAlvo, cands: AlvoMundo[]): AlvoMundo | null {
    const p = this.percepcao!;
    if (acao === "comer") {
      const podres = new Set(p.vistos.filter(v => v[1].endsWith("_podre")).map(v => v[0]));
      for (const a of cands) if (a.tipo === "comida" && !podres.has(a.id!)) return a;
      return cands.find(a => a.tipo === "cheiro") ?? null;
    }
    if (acao === "explorar") {
      const cont = cands.find(a => a.tipo === "continuar");
      if (cont) return cont;
      if (p.direcao_cheiro && p.cheiro > this.cm.limiar_cheiro_explorar) return cands.find(a => a.tipo === "cheiro")!;
      return cands.find(a => a.tipo === "vagar")!;
    }
    return cands.find(a => a.tipo === "bola") ?? null;
  }

  private validarAlvo(acao: AcaoComAlvo, a: AlvoMundo, cands: AlvoMundo[]): void {
    if (cands.some(c => mesmoAlvo(c, a))) return;
    if (acao === "explorar" && a.tipo === "ponto" && a.id === null && a.de === null) {
      if (Number.isInteger(a.x) && Number.isInteger(a.y)) {
        const [x, y] = noMapa(a.x, a.y, this.cm);
        if (x === a.x && y === a.y) return;
      }
      throw new Error(`ponto fora do mapa ou nao inteiro: (${a.x}, ${a.y})`);
    }
    throw new Error(`alvo fora dos candidatos de ${acao}: ${JSON.stringify(a)}`);
  }

  // ------------------------------------------------------------ a consequencia
  private comer(ident: number, como: string, tick: number, e: EstadoNoMundo): [Record<string, unknown>, EstadoNoMundo] {
    const c = this.comum.retirarComida(ident);
    const tm = this.tm(tick);                                   // o registro do consumo e do mundo: o relogio do mundo
    const sit = this.comum.situacao(c, tm);
    let { fome, humor, sujeira } = e;
    if (sit === "madura" && c.tipo === "racao") {
      fome = Math.min(1, fome + this.ganhoAlimentar);
      if (this.rngSujeira.random() < this.probSujeira) sujeira = Math.min(this.sujeiraMaxima, sujeira + 1);
    } else if (sit === "madura") {
      fome = Math.min(1, fome + this.cm.nutricao_fruta);
      humor = Math.min(1, Math.max(0, humor + this.efeitoFrutas[c.tipo]));
    } else {
      humor = Math.min(1, Math.max(0, humor + this.cm.efeito_podre));
    }
    const reg = { tick: tm, id: c.id, tipo: c.tipo, origem: c.origem, tick_posta: c.tick_posta, situacao: sit, como,
                  fome_antes: e.fome, humor_antes: e.humor, fome_depois: fome, humor_depois: humor };
    this.consumos.push(reg);
    if (this.grupo !== null) {                                  // dois pets: o consumo e visto pelos outros e lido pela disputa
      this.tickSocial!.comeu = { id: c.id, tipo: c.tipo, x: c.x, y: c.y, situacao: sit };
      this.grupo.viuComer(this.ident!, c.x, c.y);
    }
    return [reg, { ...e, fome, humor, sujeira }];
  }

  /** A consequencia de uma decisao (MotorMundo._consequencia): o estado vem depois do efeito de sempre da acao (o engine); sai o
      estado depois de andar, comer e brincar, com o +0,05 do comer desfeito (MF-2). `escolher` e o gancho do cerebro (null: o
      padrao); `regra` vai para o registro. Toda decisao passa aqui (as acoes sem alvo so registram e limpam o pendente). */
  consequencia(tick: number, acao: string, estado: EstadoNoMundo, escolher: EscolherAlvo | null = null, regra: string | null = null)
      : { estado: EstadoNoMundo; ocorrido: Record<string, unknown> | null } {
    const [x0, y0] = this.pet;
    const regiaoAntes = regiaoDe(x0, this.cm);
    let e = { ...estado };
    let a: AlvoMundo | null = null;
    let ocorrido: Record<string, unknown> | null = null;
    this.ultimosCandidatos = null;
    if (ACOES_COM_ALVO.includes(acao)) {
      const ac = acao as AcaoComAlvo;
      const u = this.rngAlvo.randrange(1 << 16);
      const cands = this.candidatos(ac, u, tick);
      this.ultimosCandidatos = cands;
      a = escolher ? escolher(ac, cands.slice(), this.percepcao!, u) : null;
      if (a === null) a = this.alvoPadrao(ac, cands);
      else this.validarAlvo(ac, a, cands);
      let andar: Andar | null = null;
      let x1: number, y1: number;
      if (a !== null && this.cct.controlador) {             // a P4: o controlador do contrato, nos ticks da decisao
        const cm = this.cm;
        andar = controlar(x0, y0, a.x, a.y, this.raioPegar, this.intervalo, cm.velocidade, this.cct.r_pet, this.solidos, cm.celulas_x,
                          cm.celulas_y, cm.sub, this.cct.ticks_bloqueado, this.orientacao);
        [x1, y1] = [andar.x, andar.y];
      } else {
        [x1, y1] = a === null ? [x0, y0] : passoAte(x0, y0, a.x, a.y, this.alcance, this.cm);
      }
      if (this.grupo !== null)
        this.tickSocial = { tick: this.tm(tick), de: [x0, y0], alvo: a, pendente_antes: this.pendenteAntes, social: this.idSocial(a), comeu: null };
      const desloc = andar === null ? distancia(x1 - x0, y1 - y0) : andar.andado;
      this.pet = [x1, y1];
      if (ac === "comer") e.fome = this.fomeAntes;
      const energiaAntes = e.energia;
      if (desloc) e.energia = Math.max(0, e.energia - this.cm.custo_energia_por_subunidade * desloc);
      const chegou = a !== null && distancia(a.x - x1, a.y - y1) <= this.raioPegar;
      let comeu: Record<string, unknown> | null = null;
      let bola = false;
      if (chegou && ac === "comer" && objetoDo(a!) === "comida") {
        [comeu, e] = this.comer(a!.id!, "comer", tick, e);
      } else if (chegou && ac === "explorar" && e.fome < this.cm.fome_max_comer_achado) {
        const alcancaveis = this.comum.madurasPerto(x1, y1, this.tm(tick), this.raioPegar);
        if (alcancaveis.length) [comeu, e] = this.comer(alcancaveis[0][2], "achou", tick, e);
      } else if (chegou && ac === "brincar" && objetoDo(a!) === "bola") {
        e.humor = Math.min(1, e.humor + this.cm.ganho_humor_bola);
        this.comum.rolarBola(this.tm(tick), this.bolaNoGolpe ? [x0, y0] : null);
        bola = true;
      }
      const social = this.grupo !== null ? this.idSocial(a) : null;
      if (social !== null) this.registrarSocial(a!, chegou, comeu, x1, y1, tick);
      if (a !== null && !chegou) {
        const base = a.tipo !== "continuar" ? a : alvo(a.de!, a.x, a.y, a.id);
        this.pendente = social === null ? { acao: ac, alvo: base } : { acao: ac, alvo: base, social };
      } else {
        this.pendente = null;
      }
      ocorrido = { acao, u, alvo: a, de: [x0, y0], para: [x1, y1], deslocamento: desloc, energia_gasta: energiaAntes - e.energia,
                   chegou, comeu, brincou_com_bola: bola };
      if (contratoLigado(this.cct) && a !== null) ocorrido.contrato = this.registroContrato(tick, x0, y0, x1, y1, andar, chegou, comeu);
    } else {
      this.pendente = null;
      if (this.grupo !== null)
        this.tickSocial = { tick: this.tm(tick), de: [x0, y0], alvo: null, pendente_antes: this.pendenteAntes, social: null, comeu: null };
    }
    this.registrarDecisao(this.tm(tick), acao, [x0, y0], regiaoAntes, a, ocorrido, regra);
    return { estado: e, ocorrido };
  }

  /** o que o contrato registra numa decisao com alvo (o _registro_contrato do Python): a orientacao anda com o ultimo deslocamento
      (sem o controlador, o da decisao inteira); parado, fica */
  private registroContrato(tick: number, x0: number, y0: number, x1: number, y1: number, andar: Andar | null, chegou: boolean,
                           comeu: Record<string, unknown> | null): RegistroContrato {
    let parouPor: string, contatos: [CategoriaSolido, number][], trajetoria: [number, number][] | null;
    if (andar !== null) {
      this.orientacao = andar.orientacao;
      parouPor = andar.parou_por;
      contatos = andar.contatos.map(c => [c[0], c[1]]);
      trajetoria = andar.trajetoria.map(q => [q[0], q[1]]);
    } else {
      if (x1 !== x0 || y1 !== y0) this.orientacao = setorDe(x1 - x0, y1 - y0);
      parouPor = chegou ? "chegou" : "hora";
      contatos = [];
      trajetoria = null;
    }
    const contato = contatos.map((c): [CategoriaSolido, number] => [c[0], relativo(c[1], this.orientacao)])
      .sort((p, q) => comparaStr(p[0], q[0]) || p[1] - q[1]);
    const reg: RegistroContrato = {
      tick, orientacao: this.orientacao, parou_por: parouPor, contato,
      obstaculos: bigodes(x1, y1, this.cct.r_pet, this.orientacao, this.solidos, this.cct.raio_bigode),
      resultado: { parou_por: parouPor, comeu: comeu !== null, empurrou: false, bola_afastou: null }, trajetoria,
    };
    this.contratoDecisoes.push(reg);
    return reg;
  }

  /** `tick`: o do mundo (os registros do mundo fisico) */
  private registrarDecisao(tick: number, acao: string, antes: [number, number], regiaoAntes: number, a: AlvoMundo | null,
                           ocorrido: Record<string, unknown> | null, regra: string | null): void {
    const [x1, y1] = this.pet;
    const regiao = regiaoDe(x1, this.cm);
    for (const v of this.manchasAbertas.values()) v.decisoes++;
    const dentro = new Set(this.arvores.filter(t => distancia(t.x - x1, t.y - y1) <= this.raioMancha).map(t => t.id));
    for (const id of [...this.manchasAbertas.keys()].filter(i => !dentro.has(i))) {
      const v = this.manchasAbertas.get(id)!;
      this.manchasAbertas.delete(id);
      v.saida = tick;
      this.visitas.push(v);
    }
    for (const id of [...dentro].filter(i => !this.manchasAbertas.has(i)).sort(comparaStr))
      this.manchasAbertas.set(id, { arvore: id, chegada: tick, saida: null, decisoes: 0 });
    if (regiao !== regiaoAntes) this.regioes.push({ tick, de: regiaoAntes, para: regiao });
    const o = ocorrido as { chegou: boolean; deslocamento: number; energia_gasta: number; comeu: { id: number } | null; brincou_com_bola: boolean } | null;
    this.decisoes.push({
      tick, acao, regra, antes, regiao_antes: regiaoAntes, x: x1, y: y1, regiao, alvo: a ? a.tipo : null,
      chegou: o ? o.chegou : null, deslocamento: o ? o.deslocamento : 0, energia_gasta: o ? o.energia_gasta : 0,
      comeu: o && o.comeu ? o.comeu.id : null, brincou_com_bola: o ? o.brincou_com_bola : false, manchas: [...dentro].sort(comparaStr),
    });
  }

  // ------------------------------------------------------------ o dono
  deixarComida(tick: number, tipo: string, x: number, y: number): void {
    const c = this.comum.deixarComida(tipo, x, y, this.tm(tick));     // valida como o log
    this.deixadas.push({ tick: this.tm(tick), id: c.id, tipo, x, y, pet: [this.pet[0], this.pet[1]] });
  }

  deixarBola(tick: number, x: number, y: number): void {
    this.comum.deixarBola(x, y, this.tm(tick));
  }

  /** v19 (MotorMundo._aplicar_levar_pet do Python): o dono solta o pet em (x, y); fora do mapa, ele cai na borda mais proxima (noMapa,
   *  PP-4). O destino que o pet tinha (o pendente) se perde: na proxima decisao ele escolhe de novo, de onde caiu. So a posicao muda (PP-1):
   *  nada do registro das decisoes, das regioes nem das manchas, que andam so na decisao */
  levarPet(tick: number, x: number, y: number): void {
    const [px, py] = lerLevarPet(eventoLevarPet(tick, x, y));
    const de: [number, number] = [this.pet[0], this.pet[1]];
    this.pet = noMapa(px, py, this.cm);
    this.pendente = null;
    this.levadas.push({ tick: this.tm(tick), de, pedido: [px, py], para: [this.pet[0], this.pet[1]] });
  }

  // ------------------------------------------------------------ leitura
  /** os registros sociais do pet (o resumo_social do Python; so no grupo) */
  resumoSocial(): Record<string, unknown> {
    return {
      viu_comer: Object.fromEntries([...this.viuComerDe].map(([i, v]) => [i, [...v]])),
      toques: Object.fromEntries([...this.toques].map(([i, v]) => [i, [...v]])),
      vistos_comer: this.vistosComer, idas_onde_comeu: this.idasOndeComeu, a_vista: { ...this.aVista },
      decisoes_no_grupo: this.decisoesNoGrupo,
    };
  }

  /** o MotorMundo.resumo_mundo_fisico, sem as rngs (as mesmas chaves de antes da separacao do MundoPartilhado) */
  resumo(): Record<string, unknown> {
    const m = this.comum;
    return {
      pet: [this.pet[0], this.pet[1]], bola: { ...m.bola }, comidas: [...m.comidas.values()].map(c => ({ ...c })),
      prox_id: m.proxId, passo_mundo: m.passoMundo, arvores: m.arvores.map(a => ({ ...a })),
      pendente: this.pendente ? { acao: this.pendente.acao, alvo: { ...this.pendente.alvo } } : null,
      quedas: m.quedas, consumos: this.consumos, sumidas: m.sumidas, deixadas: this.deixadas, bolas_deixadas: m.bolasDeixadas,
      rolagens: m.rolagens, decisoes: this.decisoes, regioes: this.regioes, visitas: this.visitas,
      manchas_abertas: [...this.manchasAbertas.values()].map(v => ({ ...v })),
      ...(contratoLigado(this.cct) ? { orientacao: this.orientacao, contrato_decisoes: this.contratoDecisoes } : {}),
      ...(this.levadas.length > 0 ? { levadas: this.levadas.map(l => ({ ...l, de: [...l.de], pedido: [...l.pedido], para: [...l.para] })) } : {}),   // so com alguma levada: a vida de antes sai byte a byte
    };
  }
}
