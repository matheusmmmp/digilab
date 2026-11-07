/* A grade do mapa do POC no estilo Animal Crossing (poc/mapa_ac.html): só dados, sem three e sem DOM. Cada célula tem um tipo (grama,
   caminho, areia, água) e as alturas dos quatro cantos; o platô (nível 1), o morro (nível 2), as rampas, o rio, a lagoa e o mar saem de
   regras fixas mais um ruído com semente, então o mapa é sempre o mesmo. A vista (cena.ts) só desenha o que está aqui, e o andar do
   personagem (pagina.ts) pergunta a altura e se a célula deixa passar. Todos os números são do desenho: PROPOSTO, SEM FONTE. */

export const LARG = 56, PROF = 46;              // células em x (oeste-leste) e em z (norte-sul; z cresce para o sul, para a câmera)
export const ALTURA_NIVEL = 1.25;               // a altura de um degrau de penhasco, em células
export const FUNDO_AGUA = -0.55, NIVEL_AGUA = -0.22;

export type Tipo = "grama" | "caminho" | "areia" | "agua";
/** uma célula: o tipo, o nível (0, 1 ou 2; -1 no mar) e as alturas dos cantos [noroeste, nordeste, sudeste, sudoeste] */
export interface Celula { tipo: Tipo; nivel: number; cantos: [number, number, number, number] }

/** um objeto posto no mapa: o modelo, o centro (em células, contínuo), o giro, a escala e o raio que bloqueia o andar (0 = não bloqueia);
    `y` fixa a altura (o lírio na superfície da água), senão vale a do chão */
export interface Objeto { modelo: string; x: number; z: number; giro: number; escala: number; raio: number; y?: number }

/* um gerador simples com semente (mulberry32): o mapa e os objetos saem sempre iguais */
export function rng(semente: number): () => number {
  let a = semente >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* ruído de valor 1D suave, para as bordas do platô e da praia não saírem retas */
function ruido1(semente: number, n: number): (t: number) => number {
  const r = rng(semente), v = Array.from({ length: n + 2 }, () => r());
  return (t: number) => {
    const i = Math.floor(t), f = t - i, s = f * f * (3 - 2 * f);
    const a = v[((i % n) + n) % n], b = v[(((i + 1) % n) + n) % n];
    return a + (b - a) * s;
  };
}

const dist2Segmento = (px: number, pz: number, ax: number, az: number, bx: number, bz: number) => {
  const dx = bx - ax, dz = bz - az, l = dx * dx + dz * dz;
  const t = l === 0 ? 0 : Math.max(0, Math.min(1, ((px - ax) * dx + (pz - az) * dz) / l));
  const qx = ax + t * dx - px, qz = az + t * dz - pz;
  return qx * qx + qz * qz;
};
const pertoDaLinha = (x: number, z: number, pontos: readonly (readonly [number, number])[], r: number) =>
  pontos.slice(1).some((p, i) => dist2Segmento(x, z, pontos[i][0], pontos[i][1], p[0], p[1]) <= r * r);

/* o rio desce do platô (cachoeira na borda) até o mar; a lagoa fica no platô, a oeste; o caminho de terra liga a rampa à praia */
const RIO: readonly (readonly [number, number])[] = [[44, 4], [43, 9], [41.5, 13.5], [40, 19], [42, 25], [41, 31], [39, 36], [38.5, 46]];
const LAGOA = { x: 13, z: 7, rx: 4.2, rz: 2.8 };
const LAGO_BAIXO = { x: 9.5, z: 27, rx: 3.6, rz: 2.4 };
const CAMINHO: readonly (readonly [number, number])[] = [[24.5, 14], [24.5, 19], [22, 24], [23, 30], [27, 34], [28, 38]];
/* as rampas: a coluna x da primeira e o comprimento em células; descem do platô para o sul */
export const RAMPAS = [{ x: 24, largura: 2 }] as const;

export class Mapa {
  readonly celulas: Celula[] = [];
  readonly objetos: Objeto[] = [];
  readonly inicio: [number, number] = [26.5, 27.5];

  constructor() {
    const bordaPlato = ruido1(11, 13), bordaMorro = ruido1(23, 7), bordaPraia = ruido1(37, 11);
    for (let z = 0; z < PROF; z++) for (let x = 0; x < LARG; x++) {
      const cx = x + 0.5, cz = z + 0.5;
      /* o platô ocupa o norte; o morro, o canto noroeste dele; a praia e o mar, o sul */
      const limitePlato = 13 + bordaPlato(cx / 4.5) * 4;
      const limiteMorro = 5 + bordaMorro(cx / 3.5) * 3;
      const limitePraia = 37.5 + bordaPraia(cx / 5) * 2;
      let nivel = cz < limitePlato ? 1 : 0;
      if (cz < limiteMorro && cx < 22) nivel = 2;
      let tipo: Tipo = "grama";
      if (cz > limitePraia) tipo = "areia";
      if (cz > limitePraia + 3.2) { tipo = "agua"; nivel = -1; }
      const elipse = (e: { x: number; z: number; rx: number; rz: number }) => ((cx - e.x) / e.rx) ** 2 + ((cz - e.z) / e.rz) ** 2 <= 1;
      if (pertoDaLinha(cx, cz, RIO, 1.35) || (nivel === 1 && elipse(LAGOA)) || (nivel === 0 && elipse(LAGO_BAIXO))) tipo = "agua";
      else if (tipo === "grama" && pertoDaLinha(cx, cz, CAMINHO, 0.85)) tipo = "caminho";
      const h = nivel < 0 ? FUNDO_AGUA - 0.5 : tipo === "agua" ? nivel * ALTURA_NIVEL + FUNDO_AGUA : nivel * ALTURA_NIVEL;
      this.celulas.push({ tipo, nivel, cantos: [h, h, h, h] });
    }
    this.cavarRampas();
    this.porObjetos();
  }

  cel(x: number, z: number): Celula | undefined {
    return x < 0 || z < 0 || x >= LARG || z >= PROF ? undefined : this.celulas[z * LARG + x];
  }

  /* cada rampa corta o penhasco do platô: as duas células ao sul da borda viram uma ladeira do nível 1 ao 0 */
  private cavarRampas(): void {
    for (const r of RAMPAS) {
      let borda = -1;
      for (let z = 0; z < PROF - 1; z++) if (this.cel(r.x, z)!.nivel === 1 && this.cel(r.x, z + 1)!.nivel === 0) { borda = z; break; }
      if (borda < 0) throw new Error(`rampa em x=${r.x} sem borda de platô`);
      for (let dx = 0; dx < r.largura; dx++) for (let k = 0; k < 2; k++) {
        const c = this.cel(r.x + dx, borda + 1 + k)!;
        const alto = ALTURA_NIVEL * (1 - k / 2), baixo = ALTURA_NIVEL * (1 - (k + 1) / 2);
        c.tipo = "caminho"; c.nivel = 0;
        c.cantos = [alto, alto, baixo, baixo];
      }
    }
  }

  /** a altura do chão num ponto (em células), pela ladeira da célula; fora do mapa, o fundo do mar */
  altura(x: number, z: number): number {
    const c = this.cel(Math.floor(x), Math.floor(z));
    if (!c) return FUNDO_AGUA - 0.5;
    const fx = x - Math.floor(x), fz = z - Math.floor(z);
    const [no, ne, se, so] = c.cantos;
    return (no * (1 - fx) + ne * fx) * (1 - fz) + (so * (1 - fx) + se * fx) * fz;
  }

  /** se o personagem pode estar neste ponto vindo da altura `de`: não na água, não num degrau, não dentro de um objeto */
  livre(x: number, z: number, de: number, raio = 0.28): boolean {
    for (const [ox, oz] of [[0, 0], [raio, 0], [-raio, 0], [0, raio], [0, -raio]]) {
      const c = this.cel(Math.floor(x + ox), Math.floor(z + oz));
      if (!c || c.tipo === "agua") return false;
      if (Math.abs(this.altura(x + ox, z + oz) - de) > 0.4) return false;
    }
    return !this.objetos.some(o => o.raio > 0 && (o.x - x) ** 2 + (o.z - z) ** 2 < (o.raio + raio) ** 2);
  }

  /* as árvores, os arbustos, as flores, as pedras e os troncos: em grama, longe da água, do caminho e da área do início */
  private porObjetos(): void {
    const r = rng(2026);
    const pode = (x: number, z: number, folga: number) => {
      for (let dz = -folga; dz <= folga; dz++) for (let dx = -folga; dx <= folga; dx++) {
        const c = this.cel(Math.floor(x) + dx, Math.floor(z) + dz);
        if (!c || c.tipo !== "grama" || c.cantos.some(h => h !== c.cantos[0])) return false;
        if (c.nivel !== this.cel(Math.floor(x), Math.floor(z))!.nivel) return false;
      }
      if ((x - this.inicio[0]) ** 2 + (z - this.inicio[1]) ** 2 < 9) return false;
      return true;
    };
    const longe = (x: number, z: number, d: number) => !this.objetos.some(o => o.raio > 0 && (o.x - x) ** 2 + (o.z - z) ** 2 < d * d);
    const por = (modelo: string, n: number, folga: number, dist: number, escala: [number, number], raio: number) => {
      for (let i = 0, tent = 0; i < n && tent < n * 40; tent++) {
        const x = 1 + r() * (LARG - 2), z = 1 + r() * (PROF - 2);
        if (!pode(x, z, folga) || !longe(x, z, dist)) continue;
        this.objetos.push({ modelo, x, z, giro: r() * Math.PI * 2, escala: escala[0] + r() * (escala[1] - escala[0]), raio });
        i++;
      }
    };
    /* as árvores redondas (KayKit), os pinheiros (Quaternius), os arbustos e as pedras (KayKit) */
    por("arvore_redonda", 34, 1, 3.2, [0.9, 1.15], 0.45);
    por("pinheiro", 22, 1, 3.2, [0.9, 1.2], 0.4);
    por("arbusto", 26, 0, 1.6, [0.85, 1.15], 0.4);
    por("pedra", 10, 0, 1.6, [0.7, 1.1], 0.35);
    por("toco", 5, 0, 2, [0.9, 1.1], 0.3);
    /* o que não bloqueia: flores em grupos, trevos, tufos de grama */
    por("flor", 70, 0, 0, [0.8, 1.2], 0);
    por("trevo", 50, 0, 0, [0.8, 1.2], 0);
    por("grama", 220, 0, 0, [0.7, 1.3], 0);
    /* o tronco deitado da imagem de referência, perto do início */
    this.objetos.push({ modelo: "tronco", x: this.inicio[0] + 2.3, z: this.inicio[1] + 1.2, giro: 1.2, escala: 1, raio: 0.45 });
  }
}
