/* O contrato sensorio-motor no mundo do motor (a P4, docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 3.1, etapa 2): o espelho, funcao a
   funcao, de digilab/contrato.py, com a mesma conta inteira, a mesma ordem dos vizinhos e os mesmos empates (a G-PAR-CONTRATO,
   test/contrato.test.ts, contra o gabarito de experiments/exportar_gabarito_contrato.py). Sem rng e sem estado: o motor/mundo.ts chama
   estas funcoes atras das chaves da ConfigContrato, desligada por padrao (o jogo nao muda).

   Como no Python: as 16 direcoes sao as do motor (y cresce para o sul); os troncos so tapam a visao; as paredes so existem com a chave
   delas; o empurrao da bola esta portado e conferido, mas o mundo nao o usa. As ajudas inteiras (div_arred, isqrt) ficam aqui, privadas,
   para o modulo nao depender do mundo.ts (que depende dele). */

export const ESCALA_CONTRATO = 1024;
const DIR16_C: readonly (readonly [number, number])[] = [
  [1024, 0], [946, -392], [724, -724], [392, -946], [0, -1024], [-392, -946], [-724, -724], [-946, -392],
  [-1024, 0], [-946, 392], [-724, 724], [-392, 946], [0, 1024], [392, 946], [724, 724], [946, 392]];
export const IMPULSO_BOLA = 10;
export const ATRITO_BOLA = 1;
export const RESTITUICAO: readonly [number, number] = [3, 4];
export const CATEGORIAS_SOLIDO = ["parede", "obstaculo", "tronco"] as const;
export type CategoriaSolido = typeof CATEGORIAS_SOLIDO[number];

// ================================================================== a config (digilab/config.py, ConfigContrato)
export interface ConfigContrato {
  sensores: boolean; controlador: boolean; paredes: boolean; cos_meio_cone: number; raio_bigode: number; r_pet: number;
  ticks_bloqueado: number; lado_tronco: number; espessura_parede: number;
}
/** desligada: o mundo de hoje, byte a byte; os numeros sao os do POC, PROPOSTOS e SEM FONTE (o lado_tronco e novo) */
export const CONFIG_CONTRATO: Readonly<ConfigContrato> = Object.freeze({
  sensores: false, controlador: false, paredes: false, cos_meio_cone: 512, raio_bigode: 32, r_pet: 6, ticks_bloqueado: 3,
  lado_tronco: 8, espessura_parede: 8,
});
export const CONFIG_CONTRATO_LIGADO: Readonly<ConfigContrato> = Object.freeze({ ...CONFIG_CONTRATO, sensores: true, controlador: true });

export const contratoLigado = (c: ConfigContrato): boolean => c.sensores || c.controlador || c.paredes;

/** as mesmas falhas altas do __post_init__ do Python */
export function validarContrato(c: ConfigContrato): ConfigContrato {
  for (const k of ["sensores", "controlador", "paredes"] as const)
    if (typeof c[k] !== "boolean") throw new TypeError(`ConfigContrato.${k} e bool: ${c[k]}`);
  for (const k of ["cos_meio_cone", "raio_bigode", "r_pet", "ticks_bloqueado", "lado_tronco", "espessura_parede"] as const)
    if (!Number.isInteger(c[k]) || c[k] < 0) throw new Error(`ConfigContrato.${k} e inteiro >= 0: ${c[k]}`);
  if (!(c.cos_meio_cone > 0 && c.cos_meio_cone <= 1024)) throw new Error(`ConfigContrato.cos_meio_cone em (0, 1024]: ${c.cos_meio_cone}`);
  if (c.r_pet === 0 || c.ticks_bloqueado === 0 || c.lado_tronco === 0)
    throw new Error("ConfigContrato: r_pet, ticks_bloqueado e lado_tronco positivos");
  return c;
}

// ================================================================== a conta inteira (privada; a mesma do mundo.ts)
function divArredC(n: number, d: number): number {
  if (d <= 0) throw new Error(`divisor nao positivo: ${d}`);
  const a = Math.abs(n);
  let q = Math.floor(a / d);
  const r = a - q * d;
  if (2 * r >= d) q += 1;
  return n >= 0 || q === 0 ? q : -q;
}

function isqrtC(n: number): number {
  let r = Math.floor(Math.sqrt(n));
  while (r * r > n) r--;
  while ((r + 1) * (r + 1) <= n) r++;
  return r;
}

const dist = (dx: number, dy: number): number => isqrtC(dx * dx + dy * dy);
const sinal = (v: number): number => (v > 0 ? 1 : v < 0 ? -1 : 0);
/** a divisao truncada para zero (o _trunc_div do Python), sem o -0 */
const truncDiv = (n: number, d: number): number => { const q = Math.floor(Math.abs(n) / d); return n >= 0 || q === 0 ? q : -q; };

/** o setor (0 a 15) do vetor: o de maior produto escalar com o DIR16; no empate, o de menor indice; (0, 0) da 0 */
export function setorDe(dx: number, dy: number): number {
  let melhor = 0, maior: number | null = null;
  for (let k = 0; k < 16; k++) {
    const p = dx * DIR16_C[k][0] + dy * DIR16_C[k][1];
    if (maior === null || p > maior) { melhor = k; maior = p; }
  }
  return melhor;
}

/** o vetor (dx, dy) com o comprimento c; o vetor nulo falha alto */
export function comComprimento(dx: number, dy: number, c: number): [number, number] {
  const d = dist(dx, dy);
  if (d === 0) throw new Error("direcao de um vetor nulo");
  return [divArredC(dx * c, d), divArredC(dy * c, d)];
}

/** o setor relativo (0 a 15) de um setor absoluto, dada a orientacao */
export const relativo = (setor: number, orientacao: number): number => (((setor - orientacao) % 16) + 16) % 16;

// ================================================================== os solidos
/** um retangulo [x0, x1) x [y0, y1); `colide` e `alto` separados (o tronco tapa e nao colide, P4-4) */
export interface Solido { x0: number; y0: number; x1: number; y1: number; categoria: CategoriaSolido; colide: boolean; alto: boolean }

export function solido(x0: number, y0: number, x1: number, y1: number, categoria: CategoriaSolido, colide: boolean, alto: boolean): Solido {
  if (!CATEGORIAS_SOLIDO.includes(categoria)) throw new Error(`categoria de solido: ${categoria}`);
  if (x1 <= x0 || y1 <= y0) throw new Error(`solido vazio: ${x0},${y0},${x1},${y1}`);
  return Object.freeze({ x0, y0, x1, y1, categoria, colide, alto });
}

export const pontoNoRetangulo = (x: number, y: number, s: Solido): boolean => s.x0 <= x && x < s.x1 && s.y0 <= y && y < s.y1;

/** o circulo invade o retangulo: o ponto mais perto fica a menos de r do centro; encostado, a r */
export function circuloNoRetangulo(cx: number, cy: number, r: number, s: Solido): boolean {
  const px = Math.min(Math.max(cx, s.x0), s.x1), py = Math.min(Math.max(cy, s.y0), s.y1);
  const dx = cx - px, dy = cy - py;
  return dx * dx + dy * dy < r * r;
}

export function circuloNoCirculo(ax: number, ay: number, ar: number, bx: number, by: number, br: number): boolean {
  const dx = ax - bx, dy = ay - by, soma = ar + br;
  return dx * dx + dy * dy < soma * soma;
}

export type Bloqueio = ["solido" | "circulo", number] | null;
export type Circulo = readonly [number, number, number];

/** o primeiro solido que colide ou circulo que o circulo (x, y, r) invade; null se nenhum */
export function bloqueioEm(x: number, y: number, r: number, solidos: readonly Solido[], circulos: readonly Circulo[] = []): Bloqueio {
  for (let i = 0; i < solidos.length; i++) if (solidos[i].colide && circuloNoRetangulo(x, y, r, solidos[i])) return ["solido", i];
  for (let i = 0; i < circulos.length; i++) {
    const [bx, by, br] = circulos[i];
    if (circuloNoCirculo(x, y, r, bx, by, br)) return ["circulo", i];
  }
  return null;
}

/** um tick com o deslize: n = max(|vx|, |vy|) passos de uma subunidade, x antes de y; o eixo bloqueado para ate o fim do tick */
export function mover(x0: number, y0: number, r: number, vx: number, vy: number, solidos: readonly Solido[], circulos: readonly Circulo[] = [])
    : [number, number, Bloqueio, Bloqueio] {
  const n = Math.max(Math.abs(vx), Math.abs(vy));
  let x = x0, y = y0, bx: Bloqueio = null, by: Bloqueio = null;
  for (let i = 1; i <= n; i++) {
    const ax = x0 + divArredC(vx * i, n), ay = y0 + divArredC(vy * i, n);
    if (bx === null && ax !== x) {
      const nx = x + sinal(ax - x);
      const b = bloqueioEm(nx, y, r, solidos, circulos);
      if (b === null) x = nx; else bx = b;
    }
    if (by === null && ay !== y) {
      const ny = y + sinal(ay - y);
      const b = bloqueioEm(x, ny, r, solidos, circulos);
      if (b === null) y = ny; else by = b;
    }
  }
  return [x, y, bx, by];
}

// ================================================================== a bola do POC (portada e conferida; o mundo nao a usa)
export const empurrar = (px: number, py: number, bx: number, by: number): [number, number] => comComprimento(bx - px, by - py, IMPULSO_BOLA);

export function passoBola(x: number, y: number, r: number, vx: number, vy: number, solidos: readonly Solido[], circulos: readonly Circulo[] = [])
    : [number, number, number, number] {
  const [x1, y1, bx, by] = mover(x, y, r, vx, vy, solidos, circulos);
  const [num, den] = RESTITUICAO;
  if (bx !== null) vx = -truncDiv(vx * num, den);
  if (by !== null) vy = -truncDiv(vy * num, den);
  vx += 0; vy += 0;                                            // sem o -0 do JS
  const s = isqrtC(vx * vx + vy * vy);
  if (s <= ATRITO_BOLA) return [x1, y1, 0, 0];
  return [x1, y1, divArredC(vx * (s - ATRITO_BOLA), s), divArredC(vy * (s - ATRITO_BOLA), s)];
}

// ================================================================== os sensores
/** dentro do cone em torno da orientacao (o produto escalar >= cos_meio x d, na escala 1024); (0, 0) conta */
export function noCone(dx: number, dy: number, orientacao: number, cosMeio: number): boolean {
  const d = dist(dx, dy);
  if (d === 0) return true;
  const [ux, uy] = DIR16_C[orientacao];
  return dx * ux + dy * uy >= cosMeio * d;
}

/** a linha de p0 a p1 passa por um solido alto? Os pontos p0 + (p1 - p0) k / n, k = 1 .. n - 1, n = max(|dx|, |dy|) */
export function tapado(x0: number, y0: number, x1: number, y1: number, opacos: readonly Solido[]): boolean {
  const dx = x1 - x0, dy = y1 - y0;
  const n = Math.max(Math.abs(dx), Math.abs(dy));
  const xa = Math.min(x0, x1), xb = Math.max(x0, x1), ya = Math.min(y0, y1), yb = Math.max(y0, y1);
  const altos = opacos.filter(s => s.alto && s.x0 <= xb && s.x1 >= xa && s.y0 <= yb && s.y1 >= ya);
  if (!altos.length) return false;
  for (let k = 1; k < n; k++) {
    const x = x0 + divArredC(dx * k, n), y = y0 + divArredC(dy * k, n);
    if (altos.some(s => pontoNoRetangulo(x, y, s))) return true;
  }
  return false;
}

/** o objeto em (ox, oy) e visto do pet em (x, y): no raio, no cone e sem nada alto no meio */
export function visivel(x: number, y: number, ox: number, oy: number, orientacao: number, raio: number, cosMeio: number,
                        opacos: readonly Solido[]): boolean {
  const dx = ox - x, dy = oy - y;
  return dist(dx, dy) <= raio && noCone(dx, dy, orientacao, cosMeio) && !tapado(x, y, ox, oy, opacos);
}

/** a distancia livre em 8 setores (de dois em dois, a partir da orientacao), ate o raio */
export function bigodes(x: number, y: number, r: number, orientacao: number, solidos: readonly Solido[], raio: number): number[] {
  if (!solidos.length) return Array(8).fill(raio);
  const out: number[] = [];
  for (let k = 0; k < 8; k++) {
    const [ox, oy] = DIR16_C[(orientacao + 2 * k) % 16];
    let livre = raio;
    for (let t = 1; t <= raio; t++) {
      const px = x + divArredC(ox * t, ESCALA_CONTRATO), py = y + divArredC(oy * t, ESCALA_CONTRATO);
      if (bloqueioEm(px, py, r, solidos) !== null) { livre = t - 1; break; }
    }
    out.push(livre);
  }
  return out;
}

// ================================================================== o A* e o controlador
export function octil(ax: number, ay: number, bx: number, by: number): number {
  const dx = Math.abs(ax - bx), dy = Math.abs(ay - by);
  return 10 * (dx + dy) - 6 * Math.min(dx, dy);
}

const cacheGrade = new WeakMap<readonly Solido[], Map<string, readonly boolean[]>>();

/** as celulas em que o circulo do pet cabe no centro, por indice cy * cx_n + cx; guardada por argumento (os solidos sao imutaveis) */
export function grade(cxN: number, cyN: number, sub: number, r: number, solidos: readonly Solido[]): readonly boolean[] {
  let porArgs = cacheGrade.get(solidos);
  if (!porArgs) { porArgs = new Map(); cacheGrade.set(solidos, porArgs); }
  const chave = `${cxN},${cyN},${sub},${r}`;
  const pronta = porArgs.get(chave);
  if (pronta) return pronta;
  const g: boolean[] = [];
  for (let cy = 0; cy < cyN; cy++)
    for (let cx = 0; cx < cxN; cx++) g.push(bloqueioEm(cx * sub + Math.floor(sub / 2), cy * sub + Math.floor(sub / 2), r, solidos) === null);
  Object.freeze(g);
  porArgs.set(chave, g);
  return g;
}

type Entrada = [number, number, number];                        // (f, h, indice)
const menor = (a: Entrada, b: Entrada): boolean => a[0] < b[0] || (a[0] === b[0] && (a[1] < b[1] || (a[1] === b[1] && a[2] < b[2])));

/** o heap de (f, h, indice), como o heapq do Python */
class Heap {
  private readonly a: Entrada[] = [];
  get tamanho(): number { return this.a.length; }
  push(e: Entrada): void {
    const a = this.a;
    a.push(e);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (!menor(a[i], a[p])) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }
  pop(): Entrada {
    const a = this.a, topo = a[0], ult = a.pop()!;
    if (a.length) {
      a[0] = ult;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < a.length && menor(a[l], a[m])) m = l;
        if (r < a.length && menor(a[r], a[m])) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]];
        i = m;
      }
    }
    return topo;
  }
}

/** o A* inteiro (10 no ortogonal, 14 na diagonal, sem cortar canto): as celulas do caminho ou null. O aberto escolhe o menor (f, h, indice) */
export function caminho(g: readonly boolean[], cxN: number, cyN: number, de: readonly [number, number], para: readonly [number, number])
    : [number, number][] | null {
  const ini = de[1] * cxN + de[0], fim = para[1] * cxN + para[0];
  if (!g[fim]) return null;
  const custo = new Map<number, number>([[ini, 0]]), veio = new Map<number, number>(), fechado = new Set<number>();
  const h = (i: number): number => octil(i % cxN, Math.floor(i / cxN), para[0], para[1]);
  const aberto = new Heap();
  aberto.push([h(ini), h(ini), ini]);
  while (aberto.tamanho) {
    const [f, hh, atual] = aberto.pop();
    if (fechado.has(atual) || f !== custo.get(atual)! + hh) continue;
    if (atual === fim) {
      const cam: [number, number][] = [];
      let i = fim;
      for (;;) {
        cam.push([i % cxN, Math.floor(i / cxN)]);
        if (!veio.has(i)) break;
        i = veio.get(i)!;
      }
      return cam.reverse();
    }
    fechado.add(atual);
    const ax = atual % cxN, ay = Math.floor(atual / cxN);
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        if (dx === 0 && dy === 0) continue;
        const nx = ax + dx, ny = ay + dy;
        if (nx < 0 || ny < 0 || nx >= cxN || ny >= cyN) continue;
        const n = ny * cxN + nx;
        if (!g[n] || fechado.has(n)) continue;
        if (dx !== 0 && dy !== 0 && (!g[ay * cxN + nx] || !g[ny * cxN + ax])) continue;
        const c = custo.get(atual)! + (dx !== 0 && dy !== 0 ? 14 : 10);
        if (!custo.has(n) || c < custo.get(n)!) {
          custo.set(n, c);
          veio.set(n, atual);
          const hn = h(n);
          aberto.push([c + hn, hn, n]);
        }
      }
    }
  }
  return null;
}

/** a celula livre mais perto (octil) de uma celula ocupada; no empate, a de menor indice */
export function livreMaisPerto(g: readonly boolean[], cxN: number, c: readonly [number, number]): [number, number] {
  let melhor: [number, number] | null = null, dm: number | null = null;
  for (let i = 0; i < g.length; i++) {
    if (!g[i]) continue;
    const d = octil(i % cxN, Math.floor(i / cxN), c[0], c[1]);
    if (dm === null || d < dm) { melhor = [i % cxN, Math.floor(i / cxN)]; dm = d; }
  }
  if (melhor === null) throw new Error("o mapa nao tem celula livre");
  return melhor;
}

/** o que o controlador fez numa decisao (o Andar do Python) */
export interface Andar {
  x: number; y: number; trajetoria: [number, number][]; andado: number; parou_por: "chegou" | "bloqueado" | "hora";
  contatos: [CategoriaSolido, number][]; orientacao: number;
}

/** o controlador do POC para um alvo fixo, nos `ticks` da decisao (o controlar do Python) */
export function controlar(x0: number, y0: number, tx: number, ty: number, raioChegar: number, ticks: number, velocidade: number, r: number,
                          solidos: readonly Solido[], cxN: number, cyN: number, sub: number, ticksBloqueado: number, orientacao: number): Andar {
  let x = x0, y = y0, andado = 0, parado = 0, status: Andar["parou_por"] = "hora", acabou = false;
  const traj: [number, number][] = [], contatos: [CategoriaSolido, number][] = [];
  const g = grade(cxN, cyN, sub, r, solidos);
  const celula = (px: number, py: number): [number, number] =>
    [Math.min(cxN - 1, Math.max(0, Math.floor(px / sub))), Math.min(cyN - 1, Math.max(0, Math.floor(py / sub)))];
  for (let t = 0; t < ticks; t++) {
    if (dist(tx - x, ty - y) <= raioChegar) { status = "chegou"; acabou = true; break; }
    if (parado >= ticksBloqueado) { status = "bloqueado"; acabou = true; break; }
    let destino = celula(tx, ty);
    if (!g[destino[1] * cxN + destino[0]]) destino = livreMaisPerto(g, cxN, destino);
    const cam = caminho(g, cxN, cyN, celula(x, y), destino);
    if (cam === null) { status = "bloqueado"; acabou = true; break; }
    const [wx, wy] = cam.length > 1 ? [cam[1][0] * sub + Math.floor(sub / 2), cam[1][1] * sub + Math.floor(sub / 2)] : [tx, ty];
    const dx = wx - x, dy = wy - y, dw = dist(dx, dy);
    if (dw === 0) { parado++; traj.push([x, y]); continue; }
    const [vx, vy] = dw <= velocidade ? [dx, dy] : comComprimento(dx, dy, velocidade);
    const [nx, ny, bx, by] = mover(x, y, r, vx, vy, solidos);
    for (const b of [bx, by]) {
      if (b !== null && b[0] === "solido") {
        const s = solidos[b[1]];
        const qx = Math.min(Math.max(nx, s.x0), s.x1), qy = Math.min(Math.max(ny, s.y0), s.y1);
        const c: [CategoriaSolido, number] = [s.categoria, setorDe(qx - nx, qy - ny)];
        if (!contatos.some(k => k[0] === c[0] && k[1] === c[1])) contatos.push(c);
      }
    }
    if (nx === x && ny === y) parado++;
    else { parado = 0; orientacao = setorDe(nx - x, ny - y); andado += dist(nx - x, ny - y); }
    x = nx; y = ny;
    traj.push([x, y]);
  }
  if (!acabou && dist(tx - x, ty - y) <= raioChegar) status = "chegou";
  return { x, y, trajetoria: traj, andado, parou_por: status, contatos, orientacao };
}
