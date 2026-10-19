/* O controlador do WORLD-POC-01a (docs/futuro/mundo_3d.md, seção 4.4): executa a Intenção do cérebro, tick a tick, até chegar,
   ficar bloqueado, o alvo sumir ou dar a hora da próxima decisão. O caminho sai de um A* inteiro na grade de células (custo 10 no
   ortogonal e 14 na diagonal, sem cortar canto de sólido, desempate fixo), refeito a cada tick porque a bola anda. Quem anda é o motor;
   o cérebro só escolhe o quê e sobre o quê (mundo_fisico.md, 2.1). */
import { ALCANCE, ALTURA, DIST_INVESTIGAR, LARGURA, PASSO_SETOR, R_PET, SUB, TICKS_BLOQUEADO, VELOCIDADE_PET } from "./config.ts";
import { bloqueioEm } from "./fisica.ts";
import { comComprimento, distancia, noSetor } from "./inteiros.ts";
import { centroDaCelula, type Mundo } from "./mundo.ts";
import type { AlvoMundo } from "./sensores.ts";
import type { Intencao, ParouPor } from "./tipos.ts";

const CX = LARGURA / SUB, CY = ALTURA / SUB;

/** as células em que o círculo do pet cabe no centro (a grade do A*), por índice cy * CX + cx */
export function grade(m: Mundo): boolean[] {
  const g: boolean[] = [];
  for (let cy = 0; cy < CY; cy++) for (let cx = 0; cx < CX; cx++) {
    const [x, y] = centroDaCelula(cx, cy);
    g.push(bloqueioEm(x, y, R_PET, m.solidos, []) === null);
  }
  return g;
}

const celulaDe = (x: number, y: number): [number, number] =>
  [Math.min(CX - 1, Math.max(0, Math.floor(x / SUB))), Math.min(CY - 1, Math.max(0, Math.floor(y / SUB)))];

function octil(ax: number, ay: number, bx: number, by: number): number {
  const dx = Math.abs(ax - bx), dy = Math.abs(ay - by);
  return 10 * (dx + dy) - 6 * Math.min(dx, dy);
}

/** o A*: as células do caminho, da de partida à de chegada, ou null se não há caminho. O aberto escolhe o menor (f, h, índice) */
export function caminho(g: readonly boolean[], de: [number, number], para: [number, number]): [number, number][] | null {
  const ini = de[1] * CX + de[0], fim = para[1] * CX + para[0];
  if (!g[fim]) return null;
  const custo = new Map<number, number>([[ini, 0]]), veio = new Map<number, number>();
  const aberto = new Set<number>([ini]), fechado = new Set<number>();
  const h = (i: number) => octil(i % CX, Math.floor(i / CX), para[0], para[1]);
  while (aberto.size) {
    let atual = -1, fa = Infinity, ha = Infinity;
    for (const i of aberto) {
      const f = custo.get(i)! + h(i), hi = h(i);
      if (f < fa || (f === fa && (hi < ha || (hi === ha && i < atual)))) { atual = i; fa = f; ha = hi; }
    }
    if (atual === fim) {
      const cam: [number, number][] = [];
      for (let i: number | undefined = fim; i !== undefined; i = veio.get(i)) cam.push([i % CX, Math.floor(i / CX)]);
      return cam.reverse();
    }
    aberto.delete(atual); fechado.add(atual);
    const ax = atual % CX, ay = Math.floor(atual / CX);
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      if (dx === 0 && dy === 0) continue;
      const nx = ax + dx, ny = ay + dy;
      if (nx < 0 || ny < 0 || nx >= CX || ny >= CY) continue;
      const n = ny * CX + nx;
      if (!g[n] || fechado.has(n)) continue;
      if (dx !== 0 && dy !== 0 && (!g[ay * CX + nx] || !g[ny * CX + ax])) continue;   // sem cortar o canto
      const c = custo.get(atual)! + (dx !== 0 && dy !== 0 ? 14 : 10);
      if (!custo.has(n) || c < custo.get(n)!) { custo.set(n, c); veio.set(n, atual); aberto.add(n); }
    }
  }
  return null;
}

/** a célula livre mais perto (octil) de uma célula ocupada; no empate, a de menor índice */
function livreMaisPerto(g: readonly boolean[], c: [number, number]): [number, number] {
  let melhor: [number, number] | null = null, dm = Infinity;
  for (let i = 0; i < g.length; i++) {
    if (!g[i]) continue;
    const d = octil(i % CX, Math.floor(i / CX), c[0], c[1]);
    if (d < dm) { dm = d; melhor = [i % CX, Math.floor(i / CX)]; }
  }
  if (melhor === null) throw new Error("a sala nao tem celula livre");
  return melhor;
}

const naSala = (x: number, y: number): [number, number] =>
  [Math.min(LARGURA - R_PET - 1, Math.max(R_PET, x)), Math.min(ALTURA - R_PET - 1, Math.max(R_PET, y))];

/** onde está o objeto do motor por trás de um ref, ou null se ele sumiu (a comida comida) */
export function posicaoDoAlvo(alvo: AlvoMundo, m: Mundo): [number, number] | null {
  if (alvo.tipo === "bola") return [m.bola.x, m.bola.y];
  const c = m.comidas.find(k => k.id === alvo.id && k.ativa);
  return c ? [c.x, c.y] : null;
}

/** o que o controlador manda o mundo fazer neste tick */
export interface Comando { vx: number; vy: number; podeComer: number | null }

export class Controlador {
  status: ParouPor | null = null;
  ticks = 0;
  private parado = 0;
  private ultimo: [number, number];
  private readonly alvo: AlvoMundo | null;
  private readonly ponto: [number, number] | null;

  readonly intencao: Intencao;

  constructor(intencao: Intencao, refs: ReadonlyMap<number, AlvoMundo>, m: Mundo) {
    this.intencao = intencao;
    const p = m.pet, t = intencao.tipo;
    this.ultimo = [p.x, p.y];
    const comRef = ["investigar", "tocar", "empurrar", "consumir"].includes(t) || (intencao.ref !== undefined);
    if (t === "descansar") { this.alvo = null; this.ponto = null; return; }
    if (comRef) {
      if (intencao.ref === undefined || !refs.has(intencao.ref)) throw new Error(`intencao ${t} com ref fora da observacao: ${intencao.ref}`);
      this.alvo = refs.get(intencao.ref)!;
      if (t === "consumir" && this.alvo.tipo !== "comida") throw new Error("consumir so vale para a comida");
      if (t === "empurrar" && this.alvo.tipo !== "bola") throw new Error("empurrar so vale para a bola");
      if (t === "afastar") {
        const pos = posicaoDoAlvo(this.alvo, m);
        if (pos === null) throw new Error("afastar de um alvo que sumiu");
        const [ox, oy] = pos;
        const [ux, uy] = p.x === ox && p.y === oy ? [PASSO_SETOR, 0] : comComprimento(p.x - ox, p.y - oy, PASSO_SETOR);
        this.ponto = naSala(p.x + ux, p.y + uy);
        this.alvo = null;
      } else this.ponto = null;
      return;
    }
    if (intencao.setor === undefined || !(t === "aproximar" || t === "afastar")) throw new Error(`intencao ${t} sem ref e sem setor`);
    const s = (p.orientacao + intencao.setor + (t === "afastar" ? 8 : 0)) % 16;
    this.alvo = null;
    this.ponto = naSala(...noSetor(p.x, p.y, s, PASSO_SETOR));
  }

  /** a posição do alvo agora, ou null se ele sumiu */
  private posicao(m: Mundo): [number, number] | null {
    if (this.ponto !== null) return this.ponto;
    return this.alvo === null ? null : posicaoDoAlvo(this.alvo, m);
  }

  /** o comando do tick; depois do status definido, só zero */
  passo(m: Mundo): Comando {
    const parado: Comando = { vx: 0, vy: 0, podeComer: null };
    if (this.status !== null) return parado;
    this.ticks += 1;
    const t = this.intencao.tipo, p = m.pet;
    if (t === "descansar") { this.status = "descansou"; return parado; }
    if (p.x === this.ultimo[0] && p.y === this.ultimo[1] && this.ticks > 1) this.parado += 1; else this.parado = 0;
    this.ultimo = [p.x, p.y];
    if (this.parado >= TICKS_BLOQUEADO) { this.status = "bloqueado"; return parado; }
    const pos = this.posicao(m);
    if (pos === null) { this.status = "sumiu"; return parado; }
    const d = distancia(pos[0] - p.x, pos[1] - p.y);
    const rAlvo = this.alvo?.tipo === "bola" ? m.bola.r : 0;
    if (t === "consumir" && d <= p.r + ALCANCE) {
      this.status = "chegou";
      return { vx: 0, vy: 0, podeComer: (this.alvo as { id: number }).id };
    }
    const chegou = this.ponto !== null ? d <= 2
      : t === "investigar" ? d <= DIST_INVESTIGAR
      : t === "tocar" ? d <= p.r + rAlvo + 1
      : t === "aproximar" ? d <= p.r + rAlvo + ALCANCE
      : false;                                   // o empurrar segue até a hora (ou até bloquear)
    if (chegou) { this.status = "chegou"; return parado; }
    const g = grade(m);
    let destino = celulaDe(pos[0], pos[1]);
    if (!g[destino[1] * CX + destino[0]]) destino = livreMaisPerto(g, destino);
    const cam = caminho(g, celulaDe(p.x, p.y), destino);
    if (cam === null) { this.status = "bloqueado"; return parado; }
    const [wx, wy] = cam.length > 1 ? centroDaCelula(cam[1][0], cam[1][1]) : pos;
    const dx = wx - p.x, dy = wy - p.y, dw = distancia(dx, dy);
    if (dw === 0) return parado;
    const [vx, vy] = dw <= VELOCIDADE_PET ? [dx, dy] : comComprimento(dx, dy, VELOCIDADE_PET);
    return { vx, vy, podeComer: null };
  }
}
