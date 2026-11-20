/* O mundo do WORLD-POC-01a: a sala (o piso, as paredes, um obstáculo alto e um baixo), a bola, a comida e o pet, tudo em subunidades
   inteiras. É a fonte da verdade (docs/futuro/mundo_3d.md, seção 2): o cérebro nunca o lê, só a Observação dos sensores. Sem DOM. */
import {
  ALCANCE, ALTURA, ESCALA, ESPESSURA_PAREDE, FOME_COMER, FOME_POR_TICK, IMPULSO_BOLA, LARGURA, R_BOLA, R_PET, RESPAWN_COMIDA, SUB,
  TEDIO_EMPURRAR, TEDIO_POR_TICK,
} from "./config.ts";
import { type Circulo, type Movimento, type Solido, bloqueioEm, mover, passoBola } from "./fisica.ts";
import { type Rng, comComprimento, distancia, setorDe } from "./inteiros.ts";

export interface Pet { x: number; y: number; r: number; orientacao: number; fome: number; tedio: number }
export interface Bola { x: number; y: number; r: number; vx: number; vy: number }
export interface Comida { id: number; x: number; y: number; ativa: boolean; volta_em: number | null }
/** um contato do tick (a verdade): o que o pet encostou e em que direção do mundo (setor absoluto de 16) */
export interface ContatoMundo { categoria: "parede" | "obstaculo" | "bola"; setor: number }

/** a sala do POC: as quatro paredes e os dois obstáculos (o alto tapa a visão, o baixo não) */
export function solidosDaSala(): Solido[] {
  const e = ESPESSURA_PAREDE;
  return [
    { ret: { x0: -e, y0: -e, x1: LARGURA + e, y1: 0 }, categoria: "parede", alto: true },
    { ret: { x0: -e, y0: ALTURA, x1: LARGURA + e, y1: ALTURA + e }, categoria: "parede", alto: true },
    { ret: { x0: -e, y0: 0, x1: 0, y1: ALTURA }, categoria: "parede", alto: true },
    { ret: { x0: LARGURA, y0: 0, x1: LARGURA + e, y1: ALTURA }, categoria: "parede", alto: true },
    { ret: { x0: 5 * SUB, y0: 3 * SUB, x1: 7 * SUB, y1: 7 * SUB }, categoria: "obstaculo", alto: true },
    { ret: { x0: 10 * SUB, y0: 6 * SUB, x1: 12 * SUB, y1: 8 * SUB }, categoria: "obstaculo", alto: false },
  ];
}

export const centroDaCelula = (cx: number, cy: number): [number, number] => [cx * SUB + SUB / 2, cy * SUB + SUB / 2];

/** o estado inteiro do mundo; `estado()` o devolve em JSON puro, para o hash e para o registro */
export class Mundo {
  readonly solidos: Solido[];
  pet: Pet;
  bola: Bola;
  comidas: Comida[];
  tick = 0;
  /** os contatos do pet desde a última leitura dos sensores */
  contatos: ContatoMundo[] = [];
  /** quantos empurrões e quantas comidas desde a última leitura (a verdade, para o registro) */
  empurroes = 0;
  comeu = 0;
  private proximaComida: number;
  private readonly rngAmbiente: Rng;

  constructor(rngAmbiente: Rng) {
    this.rngAmbiente = rngAmbiente;
    this.solidos = solidosDaSala();
    const [px, py] = centroDaCelula(2, 9), [bx, by] = centroDaCelula(9, 3), [cx, cy] = centroDaCelula(13, 10);
    this.pet = { x: px, y: py, r: R_PET, orientacao: 0, fome: 0, tedio: 0 };
    this.bola = { x: bx, y: by, r: R_BOLA, vx: 0, vy: 0 };
    this.comidas = [{ id: 1, x: cx, y: cy, ativa: true, volta_em: null }];
    this.proximaComida = 2;
  }

  /** o dono deixa uma comida no ponto (x, y): o evento `deixar_comida` do log. Fora da sala ou dentro de um sólido falha alto */
  deixarComida(x: number, y: number): void {
    if (!Number.isInteger(x) || !Number.isInteger(y) || x < 0 || y < 0 || x >= LARGURA || y >= ALTURA) {
      throw new Error(`deixar_comida fora da sala: (${x}, ${y})`);
    }
    if (this.solidos.some(s => x >= s.ret.x0 && x < s.ret.x1 && y >= s.ret.y0 && y < s.ret.y1)) {
      throw new Error(`deixar_comida dentro de um solido: (${x}, ${y})`);
    }
    this.comidas.push({ id: this.proximaComida++, x, y, ativa: true, volta_em: null });
  }

  /** as células em que o círculo do pet cabe no centro, na ordem de y e x */
  celulasLivres(): [number, number][] {
    const livres: [number, number][] = [];
    for (let cy = 0; cy < ALTURA / SUB; cy++) for (let cx = 0; cx < LARGURA / SUB; cx++) {
      const [x, y] = centroDaCelula(cx, cy);
      if (bloqueioEm(x, y, R_PET, this.solidos, []) === null) livres.push([cx, cy]);
    }
    return livres;
  }

  /** um tick: o pet anda com a velocidade que o controlador deu (empurrando a bola se bater nela), a bola rola, o pet come o que
   *  alcança, o corpo de brinquedo anda e a comida comida volta numa célula livre sorteada pela rng do ambiente */
  passo(vx: number, vy: number, podeComer: number | null): Movimento {
    const p = this.pet, b = this.bola;
    if (vx !== 0 || vy !== 0) p.orientacao = setorDe(vx, vy);
    const m = mover(p, vx, vy, this.solidos, [b]);
    p.x = m.x; p.y = m.y;
    for (const bl of [m.bloqueioX, m.bloqueioY]) {
      if (bl === null) continue;
      if (bl.tipo === "circulo") {
        const [ix, iy] = comComprimento(b.x - p.x, b.y - p.y, IMPULSO_BOLA);
        b.vx = ix; b.vy = iy;
        this.empurroes += 1;
        p.tedio = Math.max(0, p.tedio - TEDIO_EMPURRAR);
        this.registrarContato("bola", b.x - p.x, b.y - p.y);
      } else {
        const s = this.solidos[bl.indice];
        const qx = Math.min(Math.max(p.x, s.ret.x0), s.ret.x1), qy = Math.min(Math.max(p.y, s.ret.y0), s.ret.y1);
        this.registrarContato(s.categoria, qx - p.x, qy - p.y);
      }
    }
    const pc: Circulo = { x: p.x, y: p.y, r: p.r };
    passoBola(b, this.solidos, [pc]);
    if (podeComer !== null) {
      const c = this.comidas.find(k => k.id === podeComer && k.ativa);
      if (c && distancia(c.x - p.x, c.y - p.y) <= p.r + ALCANCE) {
        c.ativa = false; c.volta_em = this.tick + RESPAWN_COMIDA;
        p.fome = Math.max(0, p.fome - FOME_COMER);
        this.comeu += 1;
      }
    }
    for (const c of this.comidas) {
      if (!c.ativa && c.volta_em !== null && c.volta_em <= this.tick) {
        const livres = this.celulasLivres();
        const [cx, cy] = livres[this.rngAmbiente.inteiro(livres.length)];
        [c.x, c.y] = centroDaCelula(cx, cy);
        c.ativa = true; c.volta_em = null;
      }
    }
    p.fome = Math.min(ESCALA, p.fome + FOME_POR_TICK);
    p.tedio = Math.min(ESCALA, p.tedio + TEDIO_POR_TICK);
    this.tick += 1;
    return m;
  }

  private registrarContato(categoria: ContatoMundo["categoria"], dx: number, dy: number): void {
    const setor = setorDe(dx, dy);
    if (!this.contatos.some(c => c.categoria === categoria && c.setor === setor)) this.contatos.push({ categoria, setor });
  }

  /** o estado em JSON puro (a verdade), na ordem fixa dos campos */
  estado() {
    return {
      tick: this.tick, pet: { ...this.pet }, bola: { ...this.bola }, comidas: this.comidas.map(c => ({ ...c })),
      rng_ambiente: this.rngAmbiente.estado, proxima_comida: this.proximaComida,
    };
  }
}
