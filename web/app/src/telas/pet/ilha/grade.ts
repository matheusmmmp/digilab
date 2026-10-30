/* A grade da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, secao 5 e H2): uma funcao pura do LayoutMundo e da ConfigMundo do motor, sem
   three e sem DOM, adaptada da grade do POC (poc/mapa_ac/mapa.ts). Mesmo layout, mesma ilha: a semente da decoracao sai do nome do
   layout. Uma celula do motor vale uma unidade do mundo 3D; x cresce para o leste e z (o y do motor) para o sul, para a camera.
   - A area andavel e o retangulo do motor (celulas_x por celulas_y), no nivel 0, plana: grama, com um caminho de terra pintado na casa.
     La dentro so entra decoracao baixa (modelos.ts, MODELOS_BAIXOS) e as arvores do layout (regra 5).
   - A moldura, so desenho: ao norte o penhasco sobe ao plato (nivel 1) e ao morro (nivel 2); a oeste, o plato com a lagoa; a leste, o rio
     (com a cachoeira onde ele desce do plato) e a mata densa; ao sul, a areia e o mar. Na borda do mapa do motor fica o pe do penhasco
     (norte e oeste), o rio (leste) ou a areia (sul): o pet para ali porque o motor o prende, e a vista mostra um limite.
   A vista (cena.ts) so desenha o que esta aqui. Todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import type { ConfigMundo } from "../../../../motor/index.ts";
import { MODELOS, MODELO_ARVORE_DO_MOTOR, type NomeModelo } from "./modelos.ts";

/** a moldura em volta da area andavel, em celulas (pelo menos 8 de cada lado, secao 5) */
export const MOLDURA = { oeste: 10, leste: 14, norte: 12, sul: 10 } as const;
/** a altura de um degrau de penhasco, em celulas; o fundo e o nivel da agua */
export const ALTURA_NIVEL = 1.25, FUNDO_AGUA = -0.55, NIVEL_AGUA = -0.22;
/** a faixa de areia ao sul da area, em celulas, antes do mar */
export const FAIXA_AREIA = 3;
/** o rio da moldura leste: a primeira coluna depois da area e a largura */
export const RIO = { desde: 0, largura: 3 } as const;

export type Tipo = "grama" | "caminho" | "areia" | "agua";
/** a regiao do layout (dentro da area) ou a moldura */
export type Regiao = string;
export const FORA = "moldura";
/** uma celula: o tipo, o nivel (0, 1 ou 2; -1 no mar), as alturas dos cantos [noroeste, nordeste, sudeste, sudoeste] e a regiao */
export interface Celula { tipo: Tipo; nivel: number; cantos: [number, number, number, number]; regiao: Regiao }
/** um objeto posto na ilha: o modelo, o centro (em celulas, continuo), o giro, a escala e, se veio do motor, o id da arvore do layout */
export interface Objeto { modelo: NomeModelo; x: number; z: number; giro: number; escala: number; doMotor: string | null }

/* um gerador simples com semente (mulberry32): a decoracao sai sempre igual */
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
/** a semente da decoracao: o FNV-1a de 32 bits do nome do layout */
export function sementeDoLayout(nome: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < nome.length; i++) h = Math.imul(h ^ nome.charCodeAt(i), 0x01000193) >>> 0;
  return h;
}
/* ruido de valor 1D suave, para as bordas do morro e do mar nao sairem retas */
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

/** a decoracao baixa de cada regiao do layout: [modelo, quantos por 100 celulas] */
const DECORACAO: Readonly<Record<string, readonly (readonly [NomeModelo, number])[]>> = {
  casa: [["trevo", 3], ["grama", 4], ["flor", 1.5]],
  jardim: [["flor", 14], ["trevo", 9], ["grama", 4]],
  campo: [["grama_alta", 10], ["grama", 6]],
  mata: [["samambaia", 8], ["cogumelo", 4], ["grama", 8]],
};
/** o caminho de terra da casa: do ninho ao comedouro e dali um pouco para o jardim (em celulas do motor, sobre os centros) */
const RAIO_CAMINHO = 0.7;

export class Ilha {
  /** a primeira celula (oeste, norte) da grade, em celulas do motor; a grade vai de x0 a x0 + larg - 1 */
  readonly x0: number;
  readonly z0: number;
  readonly larg: number;
  readonly prof: number;
  /** a area andavel: o mapa do motor, em celulas */
  readonly area: { w: number; h: number };
  readonly celulas: Celula[] = [];
  readonly objetos: Objeto[] = [];
  /** a coluna oeste do rio (a leste da area) */
  readonly rioX: number;

  readonly cm: ConfigMundo;

  constructor(cm: ConfigMundo) {
    this.cm = cm;
    const W = cm.celulas_x, H = cm.celulas_y, L = cm.layout;
    this.area = { w: W, h: H };
    this.x0 = -MOLDURA.oeste; this.z0 = -MOLDURA.norte;
    this.larg = W + MOLDURA.oeste + MOLDURA.leste; this.prof = H + MOLDURA.norte + MOLDURA.sul;
    this.rioX = W + RIO.desde;
    const semente = sementeDoLayout(L.nome);
    const bordaMorro = ruido1(semente ^ 0x11, 9), bordaMar = ruido1(semente ^ 0x23, 11), bordaPlato = ruido1(semente ^ 0x37, 7);
    const ninho: [number, number] = [L.ninho[0] + 0.5, L.ninho[1] + 0.5], comedouro: [number, number] = [L.comedouro[0] + 0.5, L.comedouro[1] + 0.5];
    const caminho: [number, number][] = [ninho, comedouro, [comedouro[0] + 3.5, comedouro[1] + 2], [Math.min(W - 1, comedouro[0] + 7), comedouro[1] + 1.5]];
    const lagoa = { x: -5.5, z: H * 0.4, rx: 2.6, rz: 4 };
    for (let j = 0; j < this.prof; j++) for (let i = 0; i < this.larg; i++) {
      const x = this.x0 + i, z = this.z0 + j, cx = x + 0.5, cz = z + 0.5;
      const dentro = x >= 0 && x < W && z >= 0 && z < H;
      let nivel = 0, tipo: Tipo = "grama", regiao: Regiao = FORA;
      if (dentro) {
        const r = L.regioes.find(([, a, b]) => a <= x && x <= b);
        if (!r) throw new Error(`celula ${x} do mapa fora de toda regiao do layout`);
        regiao = r[0];
        if (pertoDaLinha(cx, cz, caminho, RAIO_CAMINHO) && regiao === "casa") tipo = "caminho";
      } else {
        /* o rio da moldura leste, do plato ao mar */
        const noRio = x >= this.rioX && x < this.rioX + RIO.largura;
        /* o plato: ao norte da area (o pe do penhasco na borda) e a oeste dela, e mais ao norte o morro; a leste do rio, a mata baixa */
        const plato = (z < 0 && x < this.rioX + RIO.largura + 4 + bordaPlato(cz / 3) * 3) || (x < 0 && z < H);
        if (plato) nivel = 1;
        if (z < -3 - bordaMorro(cx / 4) * 4 && x < W * 0.7) nivel = 2;
        /* a areia e o mar ao sul: a areia comeca na borda da area; o mar, depois da faixa (com uma borda que ondula fora da area) */
        const limiteMar = H + FAIXA_AREIA + (x >= 0 && x < W ? 0 : bordaMar(cx / 5) * 1.6);
        if (z >= H) { nivel = 0; tipo = "areia"; }
        if (z >= limiteMar) { tipo = "agua"; nivel = -1; }
        const elipse = (e: { x: number; z: number; rx: number; rz: number }) => ((cx - e.x) / e.rx) ** 2 + ((cz - e.z) / e.rz) ** 2 <= 1;
        if (noRio && nivel >= 0) tipo = "agua";
        if (nivel === 1 && x < 0 && elipse(lagoa)) tipo = "agua";
        if (noRio && nivel === 2) nivel = 1;
      }
      const h = nivel < 0 ? FUNDO_AGUA - 0.5 : tipo === "agua" ? nivel * ALTURA_NIVEL + FUNDO_AGUA : nivel * ALTURA_NIVEL;
      this.celulas.push({ tipo, nivel, cantos: [h, h, h, h], regiao });
    }
    this.porObjetos(semente, ninho, comedouro);
  }

  /** a celula (x, z) em celulas do motor, ou undefined fora da grade */
  cel(x: number, z: number): Celula | undefined {
    const i = x - this.x0, j = z - this.z0;
    return i < 0 || j < 0 || i >= this.larg || j >= this.prof ? undefined : this.celulas[j * this.larg + i];
  }
  /** se a celula esta na area andavel (o mapa do motor) */
  naArea(x: number, z: number): boolean { return x >= 0 && z >= 0 && x < this.area.w && z < this.area.h; }

  /** a altura do chao num ponto (em celulas); fora da grade, o fundo do mar */
  altura(x: number, z: number): number {
    const c = this.cel(Math.floor(x), Math.floor(z));
    if (!c) return FUNDO_AGUA - 0.5;
    const fx = x - Math.floor(x), fz = z - Math.floor(z), [no, ne, se, so] = c.cantos;
    return (no * (1 - fx) + ne * fx) * (1 - fz) + (so * (1 - fx) + se * fx) * fz;
  }

  /* as arvores do motor; a decoracao baixa da area por regiao; a moldura com as arvores, os arbustos, as pedras e as flores */
  private porObjetos(semente: number, ninho: [number, number], comedouro: [number, number]): void {
    const r = rng(semente);
    const plana = (x: number, z: number, folga: number) => {
      const c0 = this.cel(Math.floor(x), Math.floor(z));
      if (!c0) return false;
      for (let dz = -folga; dz <= folga; dz++) for (let dx = -folga; dx <= folga; dx++) {
        const c = this.cel(Math.floor(x) + dx, Math.floor(z) + dz);
        if (!c || c.tipo !== "grama" || c.nivel !== c0.nivel || c.cantos.some(h => h !== c.cantos[0])) return false;
      }
      return true;
    };
    const longe = (x: number, z: number, d: number, so: (o: Objeto) => boolean = () => true) =>
      !this.objetos.some(o => so(o) && (o.x - x) ** 2 + (o.z - z) ** 2 < d * d);
    const alto = (o: Objeto) => !MODELOS[o.modelo].baixo;
    const por = (modelo: NomeModelo, x: number, z: number, escala: [number, number]) =>
      this.objetos.push({ modelo, x, z, giro: r() * Math.PI * 2, escala: escala[0] + r() * (escala[1] - escala[0]), doMotor: null });

    /* as arvores do layout do motor, no centro da celula delas (as unicas coisas altas dentro da area) */
    for (const [id, x, y] of this.cm.layout.arvores)
      this.objetos.push({ modelo: MODELO_ARVORE_DO_MOTOR, x: x + 0.5, z: y + 0.5, giro: (sementeDoLayout(id) % 628) / 100, escala: 1, doMotor: id });

    /* a decoracao baixa da area: longe do ninho, do comedouro, do caminho e das arvores do motor */
    for (const [regiao, x0, x1] of this.cm.layout.regioes) {
      const lista = DECORACAO[regiao];
      if (!lista) throw new Error("regiao do mapa sem decoracao na ilha: " + regiao);
      const n = (x1 - x0 + 1) * this.area.h;
      for (const [modelo, por100] of lista) {
        const alvo = Math.round((n * por100) / 100);
        for (let k = 0, tent = 0; k < alvo && tent < alvo * 30; tent++) {
          const x = x0 + r() * (x1 - x0 + 1), z = r() * this.area.h;
          if (!plana(x, z, 0)) continue;
          if (Math.hypot(x - ninho[0], z - ninho[1]) < 1.6 || Math.hypot(x - comedouro[0], z - comedouro[1]) < 1.4) continue;
          if (!longe(x, z, 1.2, alto) || !longe(x, z, 0.35)) continue;
          por(modelo, x, z, [0.8, 1.2]);
          k++;
        }
      }
    }

    /* a moldura: so fora da area, em grama plana; a mata densa a leste do rio e mais cheia */
    const naMoldura = (x: number, z: number) => !this.naArea(Math.floor(x), Math.floor(z));
    const sortear = (modelo: NomeModelo, n: number, folga: number, dist: number, escala: [number, number], onde: (x: number, z: number) => boolean) => {
      for (let k = 0, tent = 0; k < n && tent < n * 40; tent++) {
        const x = this.x0 + 0.5 + r() * (this.larg - 1), z = this.z0 + 0.5 + r() * (this.prof - 1);
        if (!naMoldura(x, z) || !onde(x, z) || !plana(x, z, folga)) continue;
        /* nada alto rente a area: a copa nao cobre o pet na borda */
        if (!MODELOS[modelo].baixo && this.distanciaDaArea(x, z) < 1.5) continue;
        if (!longe(x, z, dist, alto)) continue;
        por(modelo, x, z, escala);
        k++;
      }
    };
    const leste = (x: number) => x >= this.rioX + RIO.largura;
    const emQualquer = () => true;
    sortear("pinheiro", 34, 1, 2.6, [0.9, 1.2], x => leste(x));
    sortear("arvore_redonda", 26, 1, 2.8, [0.9, 1.15], x => leste(x));
    sortear("arvore_redonda", 30, 1, 3.0, [0.9, 1.15], x => !leste(x));
    sortear("pinheiro", 24, 1, 3.0, [0.9, 1.2], x => !leste(x));
    sortear("arbusto", 34, 0, 1.5, [0.85, 1.15], emQualquer);
    sortear("pedra", 14, 0, 1.5, [0.7, 1.1], emQualquer);
    sortear("flor", 50, 0, 0, [0.8, 1.2], emQualquer);
    sortear("grama", 90, 0, 0, [0.7, 1.3], emQualquer);
    /* algumas pedras na areia */
    for (let k = 0, tent = 0; k < 6 && tent < 200; tent++) {
      const x = this.x0 + r() * this.larg, z = this.area.h + r() * FAIXA_AREIA, c = this.cel(Math.floor(x), Math.floor(z));
      if (!c || c.tipo !== "areia" || !longe(x, z, 2, alto) || this.distanciaDaArea(x, z) < 1.5) continue;
      por("pedra", x, z, [0.6, 0.9]);
      k++;
    }
  }

  /** a distancia (em celulas) de um ponto ate o retangulo da area andavel (0 dentro dele) */
  distanciaDaArea(x: number, z: number): number {
    const dx = Math.max(0 - x, 0, x - this.area.w), dz = Math.max(0 - z, 0, z - this.area.h);
    return Math.hypot(dx, dz);
  }
}

/** a ilha de um mundo do motor */
export const ilhaDe = (cm: ConfigMundo): Ilha => new Ilha(cm);
