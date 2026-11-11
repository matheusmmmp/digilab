/* A grade da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, secao 5 e H2): uma funcao pura do LayoutMundo e da ConfigMundo do motor, sem
   three e sem DOM, adaptada da grade do POC (poc/mapa_ac/mapa.ts). Mesmo layout, mesma ilha: a semente da decoracao sai do nome do
   layout. Uma celula do motor vale uma unidade do mundo 3D; x cresce para o leste e z (o y do motor) para o sul, para a camera.
   - A area andavel e o retangulo do motor (celulas_x por celulas_y), no nivel 0, plana: grama, com um caminho de terra pintado na casa.
     La dentro so entra decoracao baixa (modelos.ts, MODELOS_BAIXOS) e as arvores do layout (regra 5).
   - A moldura, so desenho: ao norte o penhasco sobe ao plato (nivel 1) e ao morro (nivel 2); a oeste, o plato com a lagoa; a leste, o rio
     (com a cachoeira onde ele desce do plato) e a mata densa; ao sul, a areia e o mar. Na borda do mapa do motor fica o pe do penhasco
     (norte e oeste), o rio (leste) ou a areia (sul): o pet para ali porque o motor o prende, e a vista mostra um limite.
   A vista (cena.ts) so desenha o que esta aqui. Todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import { AGUA_DOCE, AGUA_MAR, AGUA_POR_LAYOUT, PONTE, celulasSecas, type ConfigMundo } from "../../../../motor/index.ts";
import { ENFEITES_GRADE, TV_TRES_QUARTOS, FIM_ILHA, ILHA_AGUA, PLANTA_ILHA, PLANTA_ILHA_AGUA, type PlantaIlha } from "./constantes.ts";
import { ENFEITES_MODELOS, MODELOS, MODELO_ARVORE_DO_MOTOR, type NomeEnfeite, type NomeLugar, type NomeModelo } from "./modelos.ts";

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
/** um enfeite do mundo humano na moldura (docs/TAREFA_V3_MUNDO_ENFEITES.md): o modelo, o lugar (celulas) e o giro, que vira a frente
    do modelo (+z do glTF) para a area andavel */
export interface Enfeite { nome: NomeEnfeite; x: number; z: number; giro: number }
/** um lugar da ilha (docs/TAREFA_V3_LUGARES_3D.md): o modelo, o lugar (celulas), o giro (a frente, +z do glTF, para a area) e a altura do
    chao em que ele fica (o cais fica na areia, com metade sobre a agua) */
export interface Lugar { nome: NomeLugar; x: number; z: number; giro: number; y: number }

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
  /** os enfeites (docs/TAREFA_V3_MUNDO_ENFEITES.md): numa lista propria e com a rng propria, para os `objetos` sairem iguais (E-G0) */
  readonly enfeites: Enfeite[] = [];
  /** os lugares (docs/TAREFA_V3_LUGARES_3D.md, secao 12): depois dos enfeites, com a rng propria */
  readonly lugares: Lugar[] = [];
  /** os indices de `objetos` que a vista nao desenha: a decoracao dentro da clareira de um lugar (os objetos em si nao mudam, E-G0) */
  readonly escondidos = new Set<number>();
  /** os objetos da planta que nao sao da decoracao sorteada (as pedras do ferro-velho): numa lista propria, para os `objetos` sairem iguais
      (E-G0); a vista desenha os dois */
  readonly extras: Objeto[] = [];
  /** os caminhos de terra da planta A (PLANTA_ILHA), cada um pelos pontos dele, em celulas (o do lar comeca no comedouro do layout) */
  readonly caminhos: [number, number][][] = [];
  /** a coluna oeste do rio (a leste da area) */
  readonly rioX: number;

  readonly cm: ConfigMundo;
  /** a ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA3): o layout do motor tem agua (AGUA_POR_LAYOUT). A ilha inteira
      fica dentro do mapa do motor, a moldura e so mar, e nao ha penhasco, plato nem mata */
  readonly comAgua: boolean;
  /** a planta que vale: a A (PLANTA_ILHA) ou a da ilha com agua (PLANTA_ILHA_AGUA) */
  readonly planta: PlantaIlha;
  /** as celulas de ponte do layout com agua (ponte.ts as desenha); vazio sem agua */
  readonly pontes: [number, number][] = [];

  constructor(cm: ConfigMundo) {
    this.cm = cm;
    const W = cm.celulas_x, H = cm.celulas_y, L = cm.layout;
    this.area = { w: W, h: H };
    this.comAgua = celulasSecas(cm) !== null;
    this.planta = this.comAgua ? PLANTA_ILHA_AGUA : PLANTA_ILHA;
    const M = this.comAgua ? { oeste: ILHA_AGUA.moldura, leste: ILHA_AGUA.moldura, norte: ILHA_AGUA.moldura, sul: ILHA_AGUA.moldura } : MOLDURA;
    this.x0 = -M.oeste; this.z0 = -M.norte;
    this.larg = W + M.oeste + M.leste; this.prof = H + M.norte + M.sul;
    this.rioX = W + RIO.desde;
    const semente = sementeDoLayout(L.nome);
    if (this.comAgua) {
      this.porAgua();
      const ninhoA: [number, number] = [L.ninho[0] + 0.5, L.ninho[1] + 0.5], comedouroA: [number, number] = [L.comedouro[0] + 0.5, L.comedouro[1] + 0.5];
      this.porObjetos(semente, ninhoA, comedouroA);
      this.porLugares();
      this.porPlanta(semente, comedouroA);
      this.porEnfeites(semente);
      return;
    }
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
    this.porBordas(semente);
    this.porLugares();
    this.porPlanta(semente, comedouro);
    this.porEnfeites(semente);
  }

  /* as celulas da ilha com agua, do mapa do motor (AGUA_POR_LAYOUT): o mar (fora do mapa e onde o mapa diz) no nivel -1, a agua doce
     (o rio e a lagoa) no nivel 0, a ponte como caminho, e a terra em grama, ou em areia a ate `praia` celulas do mar (`praiaSul` no sul) */
  private porAgua(): void {
    const W = this.area.w, H = this.area.h, L = this.cm.layout, linhas = AGUA_POR_LAYOUT[L.nome], A = ILHA_AGUA;
    const mar = (x: number, z: number) => x < 0 || z < 0 || x >= W || z >= H || linhas[z][x] === AGUA_MAR;
    for (let j = 0; j < this.prof; j++) for (let i = 0; i < this.larg; i++) {
      const x = this.x0 + i, z = this.z0 + j;
      let nivel = 0, tipo: Tipo = "grama", regiao: Regiao = FORA;
      if (mar(x, z)) { tipo = "agua"; nivel = -1; }
      else {
        const r = L.regioes.find(([, a, b]) => a <= x && x <= b);
        if (!r) throw new Error(`celula ${x} do mapa fora de toda regiao do layout`);
        regiao = r[0];
        const ch = linhas[z][x];
        if (ch === AGUA_DOCE) tipo = "agua";
        else if (ch === PONTE) { tipo = "caminho"; this.pontes.push([x, z]); }
        else {
          const d = z >= A.sulDesde ? A.praiaSul : A.praia;
          let praia = false;
          for (let dz = -d; dz <= d && !praia; dz++) for (let dx = -d; dx <= d; dx++) if (mar(x + dx, z + dz)) { praia = true; break; }
          if (praia) tipo = "areia";
        }
      }
      const h = nivel < 0 ? FUNDO_AGUA - 0.5 : tipo === "agua" ? FUNDO_AGUA : 0;
      this.celulas.push({ tipo, nivel, cantos: [h, h, h, h], regiao });
    }
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

  /* o chao plano em volta de (x, z): `folga` celulas de cada lado, no mesmo nivel e da mesma altura; `tipos`, os tipos aceitos */
  private plana(x: number, z: number, folga: number, tipos: readonly Tipo[] = ["grama"]): boolean {
    const c0 = this.cel(Math.floor(x), Math.floor(z));
    if (!c0) return false;
    for (let dz = -folga; dz <= folga; dz++) for (let dx = -folga; dx <= folga; dx++) {
      const c = this.cel(Math.floor(x) + dx, Math.floor(z) + dz);
      if (!c || !tipos.includes(c.tipo) || c.nivel !== c0.nivel || c.cantos.some(h => h !== c.cantos[0])) return false;
    }
    return true;
  }
  /* o ponto que cabe mais perto de `alvo`, numa busca na grade de quartos de celula ate `busca` celulas dele, sem sorteio; falha alto */
  private pertoDe(alvo: readonly [number, number], busca: number, cabe: (x: number, z: number) => boolean, oque: string): [number, number] {
    let melhor: [number, number] | null = null, dm = Infinity;
    for (let dz = -busca; dz <= busca; dz += 0.25) for (let dx = -busca; dx <= busca; dx += 0.25) {
      const d = Math.hypot(dx, dz), x = alvo[0] + dx, z = alvo[1] + dz;
      if (d > busca || d >= dm || !cabe(x, z)) continue;
      melhor = [x, z]; dm = d;
    }
    if (!melhor) throw new Error(`sem lugar para ${oque} na ilha ${this.cm.layout.nome}, a ate ${busca} celulas de ${alvo.join(", ")}`);
    return melhor;
  }
  /* a decoracao (nao as arvores do motor) a menos de `raio` de (x, z) some da vista (escondidos; os objetos em si nao mudam, E-G0) */
  private abrir(x: number, z: number, raio: number): void {
    this.objetos.forEach((o, i) => { if (o.doMotor === null && Math.hypot(o.x - x, o.z - z) < raio) this.escondidos.add(i); });
  }

  /* os lugares da planta A (PLANTA_ILHA.lugares): o portao e a barraca no ponto que cabe mais perto do alvo, em grama plana com a folga, longe
     das arvores do motor (a clareira) e um do outro; o cais na beira do mar (a ultima linha de areia), na coluna da planta, `mar` celulas mar adentro e com o pe no fundo do mar (as estacas e o casco do barco entram na agua). A frente (+z do glTF):
     fora da area, para o ponto mais perto dela; dentro (a barraca), para a praca. Cada um abre a clareira dele. Falha alto se faltar lugar */
  private porLugares(): void {
    const P = this.planta, doMotor = this.objetos.filter(o => o.doMotor !== null);
    for (const nome of ["portao", "barraca"] as const) {
      const G = P.lugares[nome];
      const [x, z] = this.pertoDe(G.alvo, G.busca, (x, z) => this.plana(x, z, G.folga)
        && !doMotor.some(o => Math.hypot(o.x - x, o.z - z) < G.clareira)
        && !this.lugares.some(l => Math.hypot(l.x - x, l.z - z) < G.clareira + P.lugares[l.nome].clareira), "o lugar " + nome);
      const dentro = this.naArea(Math.floor(x), Math.floor(z));
      const ax = dentro ? P.praca.x : Math.min(Math.max(x, 0), this.area.w), az = dentro ? P.praca.z : Math.min(Math.max(z, 0), this.area.h);
      this.lugares.push({ nome, x, z, giro: Math.atan2(ax - x, az - z), y: this.altura(x, z) });
      this.abrir(x, z, G.clareira);
    }
    const C = P.lugares.cais, i = Math.floor(C.x);
    let j = this.area.h;
    while (this.cel(i, j + 1)?.tipo === "areia") j++;
    /* na ilha com agua a praia fica dentro do mapa: a ultima linha de terra da coluna, de sul para norte */
    if (this.comAgua) {
      j = this.area.h - 1;
      while (j > 0 && this.cel(i, j)?.tipo === "agua") j--;
      if (this.cel(i, j + 1)?.nivel !== -1) throw new Error(`o cais na coluna ${i} da ilha ${this.cm.layout.nome} nao da para o mar`);
    }
    if (this.cel(i, j)?.tipo !== "areia" || this.cel(i, j + 1)?.tipo !== "agua") throw new Error(`sem beira de mar para o cais na coluna ${i} da ilha ${this.cm.layout.nome}`);
    if (doMotor.some(o => Math.hypot(o.x - C.x, o.z - (j + 1)) < C.clareira)) throw new Error(`uma arvore do motor na clareira do cais na ilha ${this.cm.layout.nome}`);
    this.lugares.push({ nome: "cais", x: C.x, z: j + 1 + C.mar, giro: Math.PI, y: FUNDO_AGUA });
    this.abrir(C.x, j + 1, C.clareira);
  }

  /* a praca e os caminhos de terra da planta A, pintados depois da decoracao (a decoracao que cai neles some, escondidos): so a grama da
     area andavel vira caminho, e cada caminho para antes da base do lugar onde chega. Depois, a moldura em bosques e vaos: a arvore e o
     arbusto da moldura so ficam num bosque (PLANTA_ILHA.bosques) ou na mata a leste do rio, e nunca num vao; e cada bosque ganha as arvores
     e os arbustos dele (extras) */
  private porPlanta(semente: number, comedouro: [number, number]): void {
    const P = this.planta, par = (p: readonly number[]): [number, number] => [p[0], p[1]];
    this.caminhos.push([comedouro, ...P.caminhos.lar.map(par)], ...(["portao", "barraca", "cais"] as const).map(n => P.caminhos[n].map(par)));
    const naBase = (x: number, z: number) => this.lugares.some(l => l.nome !== "cais" && Math.hypot(l.x - x, l.z - z) < P.lugares[l.nome].base + P.folgaLugar);
    for (let z = 0; z < this.area.h; z++) for (let x = 0; x < this.area.w; x++) {
      const c = this.cel(x, z)!, cx = x + 0.5, cz = z + 0.5;
      if (c.tipo !== "grama" || naBase(cx, cz)) continue;
      const naPraca = Math.hypot(cx - P.praca.x, cz - P.praca.z) <= P.praca.raio;
      if (naPraca || this.caminhos.some(l => pertoDaLinha(cx, cz, l, P.raioCaminho))) c.tipo = "caminho";
    }
    this.objetos.forEach((o, i) => {
      if (o.doMotor === null && this.cel(Math.floor(o.x), Math.floor(o.z))?.tipo === "caminho") this.escondidos.add(i);
    });
    const naElipse = (x: number, z: number, e: readonly number[], f = 1) => ((x - e[0]) / (e[2] * f)) ** 2 + ((z - e[1]) / (e[3] * f)) ** 2 <= 1;
    const leste = (x: number) => x >= this.rioX + RIO.largura;
    this.objetos.forEach((o, i) => {
      if (o.doMotor !== null || MODELOS[o.modelo].baixo || o.modelo === "pedra" || this.naArea(Math.floor(o.x), Math.floor(o.z))) return;
      if (P.vaos.some(v => naElipse(o.x, o.z, v))) { this.escondidos.add(i); return; }
      if (leste(o.x)) return;
      /* o arbusto fica na base do bosque (a elipse um pouco maior) */
      if (!P.bosques.some(b => naElipse(o.x, o.z, b, o.modelo === "arbusto" ? 1.3 : 1))) this.escondidos.add(i);
    });
    /* o bosque cheio: as arvores e os arbustos da planta (extras), sorteados com a rng propria dentro de cada bosque, em grama plana, nada
       alto rente a area, fora dos vaos e longe das coisas altas que ficaram */
    const r = rng(semente ^ P.sal), B = P.bosque;
    const altos = (): { x: number; z: number }[] => [
      ...this.objetos.filter((o, i) => !this.escondidos.has(i) && !MODELOS[o.modelo].baixo), ...this.extras];
    for (const b of P.bosques) {
      const n = Math.round(Math.PI * b[2] * b[3] * B.porCelula);
      for (const [modelo, quantos, raio, dist, escala] of [["arvore", n, 1, B.entreArvores, B.escalaArvore], ["arbusto", Math.round(n * B.arbustos), 1.3, B.entreArbustos, B.escalaArbusto]] as const) {
        const ja = altos();
        for (let k = 0, tent = 0; k < quantos && tent < quantos * 40; tent++) {
          const a = r() * Math.PI * 2, d = Math.sqrt(r()) * raio, x = b[0] + Math.cos(a) * b[2] * d, z = b[1] + Math.sin(a) * b[3] * d;
          const m: NomeModelo = modelo === "arbusto" ? "arbusto" : r() < 0.5 ? "pinheiro" : "arvore_redonda";
          if (!this.plana(x, z, modelo === "arbusto" ? 0 : 1) || this.distanciaDaArea(x, z) < 1.5 || P.vaos.some(v => naElipse(x, z, v))) continue;
          if (ja.some(o => Math.hypot(o.x - x, o.z - z) < dist)) continue;
          const o: Objeto = { modelo: m, x, z, giro: r() * Math.PI * 2, escala: escala[0] + r() * (escala[1] - escala[0]), doMotor: null };
          this.extras.push(o); ja.push(o);
          k++;
        }
      }
    }
  }

  /* os enfeites da planta A: os postes nos pontos de PLANTA_ILHA.postes (na grama, no caminho ou na areia), com a lampada para o ponto mais
     perto de um caminho; o carro, a geladeira e o trilho, cada um num canto da moldura, no ponto que cabe mais perto do da planta, no chao
     plano dele, fora dos caminhos e das clareiras dos lugares, com o entorno dele. Cada marco abre a clareira dele. Falha alto se faltar lugar */
  private porEnfeites(semente: number): void {
    const P = this.planta;
    /* sem agua os marcos e o entorno deles ficam na moldura; na ilha com agua, dentro do mapa (a moldura e mar) */
    const noLado = (x: number, z: number) => this.naArea(Math.floor(x), Math.floor(z)) === this.comAgua;
    for (const [x, z] of P.postes) {
      if (!this.plana(x, z, ENFEITES_GRADE.poste.folga, ["grama", "caminho", "areia"])) throw new Error(`o poste em ${x}, ${z} nao fica em chao plano na ilha ${this.cm.layout.nome}`);
      let melhor: [number, number] = [x, z], dm = Infinity;
      for (const l of this.caminhos) for (let k = 1; k < l.length; k++) {
        const [ax, az] = l[k - 1], [bx, bz] = l[k], dx = bx - ax, dz = bz - az, q = dx * dx + dz * dz;
        const t = q === 0 ? 0 : Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / q)), px = ax + t * dx, pz = az + t * dz, d = Math.hypot(px - x, pz - z);
        if (d < dm) { dm = d; melhor = [px, pz]; }
      }
      this.enfeites.push({ nome: "poste", x, z, giro: Math.atan2(melhor[0] - x, melhor[1] - z) });
    }
    /* os marcos espalhados pela moldura (IL-4 revista), cada um com o entorno dele (extras): arbustos e grama alta em grama, pedras em
       qualquer chao plano, ate o raio, longe do marco e uns dos outros; a frente do marco para o ponto mais perto da area */
    const M = P.marcos, r = rng(semente ^ P.sal ^ 0x3a7c05);
    for (const nome of ["carro", "geladeira", "trilho", "lata", "tv"] as const) {
      const G = ENFEITES_GRADE[nome], D = M[nome];
      const [x, z] = this.pertoDe(D.ponto, M.busca, (x, z) => noLado(x, z) && this.plana(x, z, G.folga, this.comAgua ? ["grama", "areia"] : G.chao)
        && !this.caminhos.some(l => pertoDaLinha(x, z, l, P.raioCaminho + G.clareira))
        && !this.lugares.some(l => Math.hypot(l.x - x, l.z - z) < P.lugares[l.nome].clareira + G.clareira), "o enfeite " + nome);
      /* a frente para o ponto mais perto da area; dentro dela (a ilha com agua), para a praca */
      const ax = this.comAgua ? P.praca.x : Math.min(Math.max(x, 0), this.area.w), az = this.comAgua ? P.praca.z : Math.min(Math.max(z, 0), this.area.h);
      /* a TV fica em tres quartos para a camera (a UX-GV-3): a TV_TRES_QUARTOS graus do sul, para o lado desse mesmo ponto */
      const giro = nome === "tv" ? (ax < x ? -1 : 1) * TV_TRES_QUARTOS * Math.PI / 180 : Math.atan2(ax - x, az - z);
      this.enfeites.push({ nome, x, z, giro });
      this.abrir(x, z, G.clareira);
      const E = D.entorno;
      for (const [modelo, quantos, escala] of [["arbusto", E.arbusto, [0.8, 1.15]], ["grama_alta", E.grama_alta, [0.9, 1.3]], ["pedra", E.pedra, [0.6, 0.95]]] as const) {
        /* na ilha com agua o marco fica onde o pet anda: do entorno so entra o que e baixo (a regra 5 da ilha) */
        if (this.comAgua && !MODELOS[modelo].baixo) continue;
        for (let k = 0, tent = 0; k < quantos && tent < quantos * 60; tent++) {
          const a = r() * Math.PI * 2, d = G.clareira * 0.55 + r() * (E.raio - G.clareira * 0.55), ox = x + Math.cos(a) * d, oz = z + Math.sin(a) * d;
          if (!noLado(ox, oz) || !this.plana(ox, oz, 0, modelo === "pedra" ? ["grama", "areia"] : ["grama"])) continue;
          if (this.extras.some(o => Math.hypot(o.x - ox, o.z - oz) < (modelo === "grama_alta" ? 0.5 : 1))) continue;
          this.extras.push({ modelo, x: ox, z: oz, giro: r() * Math.PI * 2, escala: escala[0] + r() * (escala[1] - escala[0]), doMotor: null });
          k++;
        }
      }
    }
  }

  /* o fim da ilha a leste (FIM_ILHA.degraus): depois do rio, a mata sobe em degraus ate o morro, como o norte. So a grama da moldura ao norte
     da areia muda de nivel; a decoracao alta que fica rente a um degrau novo some da vista (escondidos; a lista `objetos` nao muda, E-G0) */
  private porBordas(semente: number): void {
    const F = FIM_ILHA, x0 = this.rioX + RIO.largura, onda = ruido1(semente ^ 0x4d, 6), mudou = new Set<Celula>();
    for (let z = this.z0; z < this.area.h; z++) for (let x = x0; x < this.x0 + this.larg; x++) {
      const c = this.cel(x, z)!;
      if (c.tipo !== "grama" || c.nivel < 0) continue;
      const passo = x - x0 - onda((z + 0.5) / 4) * F.ondula;
      let n = c.nivel;
      F.degraus.forEach((d, k) => { if (passo >= d) n = Math.max(n, k + 1); });
      if (n === c.nivel) continue;
      const h = n * ALTURA_NIVEL;
      c.nivel = n; c.cantos = [h, h, h, h];
      mudou.add(c);
    }
    const todos: readonly Tipo[] = ["grama", "caminho", "areia", "agua"];
    this.objetos.forEach((o, i) => {
      if (o.doMotor !== null || o.x < x0 - 1.5) return;
      const perto: Celula[] = [];
      for (let dz = -1; dz <= 1; dz++) for (let dx = -1; dx <= 1; dx++) { const c = this.cel(Math.floor(o.x) + dx, Math.floor(o.z) + dz); if (c) perto.push(c); }
      if (perto.some(c => mudou.has(c)) && !this.plana(o.x, o.z, MODELOS[o.modelo].baixo ? 0 : 1, todos)) this.escondidos.add(i);
    });
  }

  /** a distancia (em celulas) de um ponto ate o retangulo da area andavel (0 dentro dele) */
  distanciaDaArea(x: number, z: number): number {
    const dx = Math.max(0 - x, 0, x - this.area.w), dz = Math.max(0 - z, 0, z - this.area.h);
    return Math.hypot(dx, dz);
  }
}

/** a ilha de um mundo do motor */
export const ilhaDe = (cm: ConfigMundo): Ilha => new Ilha(cm);
