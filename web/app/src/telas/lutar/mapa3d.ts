/* O mapa 3D da Exploracao (docs/TAREFA_V2_EXPLORACAO.md, decisao do Matheus de 2026-10-21): ilhas de voxels procedurais numa vista
   isometrica, Three.js so como vista, no padrao do cena3d.ts da tela Pet (import dinamico, chunk proprio; o G-FRONTEIRA segura que as
   telas nao importam o POC). Nada aqui decide o jogo: a tela diz onde fica cada ilha na caixa (mapaLayout.ts), o tema dela e se esta
   trancada, e este modulo so desenha. Sem arte de terceiros: tudo sao caixas coloridas por face, sem luz (como a sala do Pet), entao o
   mapa sai igual com ou sem o atlas do UP. O mapa e parado: desenha quando a tela muda de tamanho ou o motor muda. */
import * as THREE from "three";

export type TemaIlha = "campina" | "torre" | "floresta" | "cidadela" | "lago" | "espiral" | "fronteira";
export interface IlhaMapa { tema: TemaIlha; cx: number; cy: number; tranca: boolean }
export interface TrilhoMapa { de: number; ate: number; feito: boolean }
/** o que desenhar: a caixa em px de CSS, a largura de uma ilha na tela (tam), as ilhas (o centro do tampo em px da caixa) e o trilho */
export interface CenaMapa { larg: number; alt: number; tam: number; ilhas: IlhaMapa[]; trilhos: TrilhoMapa[] }

/* uma caixa: o centro da base (x, y0, z), o tamanho (w, h, d) e a cor; o tampo da ilha e o plano y = 1 */
type Bloco = readonly [x: number, y0: number, z: number, w: number, h: number, d: number, cor: number];
/* a camera olha de (1, 1, 1): a face de cima clara, a +x (a direita na tela) media, a +z (a esquerda) mais escura. PROPOSTO */
const SOMBRA = { cima: 1, x: 0.8, z: 0.64, resto: 0.5 };
/* o tampo tem 7 x 7 celulas sem os 4 cantos; embaixo, a terra e a rocha afinando */
const LADO = 7;
const TOPO_ILHA = 1;

function corpo(topo: number, terra: number, rocha: number): Bloco[] {
  const b: Bloco[] = [];
  for (let i = 0; i < LADO; i++) for (let j = 0; j < LADO; j++) {
    const di = Math.abs(i - 3), dj = Math.abs(j - 3), x = i - 3, z = j - 3;
    if (di === 3 && dj === 3) continue;
    b.push([x, 0, z, 1, 1, 1, topo], [x, -1, z, 1, 1, 1, terra]);
    if (Math.max(di, dj) <= 2 && !(di === 2 && dj === 2)) b.push([x, -2, z, 1, 1, 1, terra]);
    if (Math.max(di, dj) <= 1) b.push([x, -3, z, 1, 1, 1, rocha]);
  }
  b.push([0, -4, 0, 1, 1, 1, rocha]);
  return b;
}
const arvore = (x: number, z: number, folha: number, alta = 1): Bloco[] =>
  [[x, TOPO_ILHA, z, 0.45, alta, 0.45, 0x6b4a2b], [x, TOPO_ILHA + alta, z, 1.5, 1.3, 1.5, folha], [x, TOPO_ILHA + alta + 1.3, z, 0.9, 0.6, 0.9, folha]];

/** os blocos de cada tema; as alturas ficam abaixo de 4 voxels acima do tampo (ACIMA de mapaLayout.ts) */
function blocosDoTema(t: TemaIlha): Bloco[] {
  switch (t) {
    case "campina": return [...corpo(0x7ccf53, 0x9b6a3c, 0x7d6a5a), ...arvore(-2, -2, 0x4fae3b),
      [2, TOPO_ILHA, -1, 1.1, 0.7, 1.1, 0x5fb847],
      ...([[-1, 1, 0xffd84a], [1, -2, 0xffffff], [2, 2, 0xffd84a], [-2, 1, 0xff9fc4], [0, 2, 0xffffff]] as const)
        .map(([x, z, c]): Bloco => [x, TOPO_ILHA, z, 0.35, 0.35, 0.35, c])];
    /* a pedra e quente (arenito) e o tampo tem musgo: a torre cinza-azulada se confundia com a ilha trancada */
    case "torre": return [...corpo(0x8fb86a, 0xb59a78, 0x8a7560),
      [-0.5, TOPO_ILHA, -0.5, 2.2, 2.6, 2.2, 0xd8c4a0],
      ...([[-1.3, -1.3], [0.3, -1.3], [-1.3, 0.3], [0.3, 0.3]] as const).map(([x, z]): Bloco => [x, TOPO_ILHA + 2.6, z, 0.6, 0.6, 0.6, 0xd8c4a0]),
      [-0.5, TOPO_ILHA, 0.62, 0.7, 1, 0.08, 0x5b4636], [0.62, TOPO_ILHA + 1.5, -0.5, 0.08, 0.6, 0.5, 0x3d4a5c],
      [2, TOPO_ILHA, 2, 0.9, 0.5, 0.9, 0xa8927a]];
    case "floresta": return [...corpo(0x3e9b4a, 0x7a5232, 0x5f4a3a), ...arvore(-2, -1, 0x2f8a3a, 1.2), ...arvore(1, -2, 0x37964a),
      ...arvore(2, 1, 0x2f8a3a), ...arvore(-1, 2, 0x37964a, 0.8)];
    case "cidadela": return [...corpo(0x5d5876, 0x4a3f55, 0x3e3a48),
      [0, TOPO_ILHA, -2.6, 5.2, 1.3, 0.6, 0x433b5c], [-2.6, TOPO_ILHA, 0, 0.6, 1.3, 5.2, 0x433b5c],
      ...([[-2.6, -2.6], [2.4, -2.6], [-2.6, 2.4]] as const).flatMap(([x, z]): Bloco[] =>
        [[x, TOPO_ILHA, z, 1.2, 2.5, 1.2, 0x524870], [x, TOPO_ILHA + 2.5, z, 1.4, 0.5, 1.4, 0x8b2f4f]]),
      [0.5, TOPO_ILHA, 0.5, 1.6, 1.6, 1.6, 0x524870], [0.5, TOPO_ILHA + 1.6, 0.5, 1, 0.6, 1, 0x8b2f4f]];
    case "lago": {
      const b = corpo(0xe8d8a0, 0x9b7a4a, 0x7d6a5a).filter(([x, y0, z]) => !(y0 === 0 && Math.abs(x) + Math.abs(z) <= 2));
      for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++)
        if (Math.abs(x) + Math.abs(z) <= 2) b.push([x, 0, z, 1, 0.7, 1, (x + z) % 2 === 0 ? 0x58b6f2 : 0x4eaaea]);
      b.push([2.6, TOPO_ILHA - 0.1, 0.6, 1.4, 0.2, 0.6, 0x8a5a33], [-2, TOPO_ILHA, -2, 0.8, 0.4, 0.8, 0x7fbf5a]);
      return b;
    }
    case "espiral": return [...corpo(0x9c8d7a, 0x7b6d5d, 0x62574b),
      [0, TOPO_ILHA, 0, 5, 1, 5, 0x8e8070], [0, TOPO_ILHA + 1, 0, 3.4, 1, 3.4, 0x9d907f], [0, TOPO_ILHA + 2, 0, 2, 1, 2, 0xb3a796],
      [0, TOPO_ILHA + 3, 0, 1, 0.6, 1, 0xffffff],
      [2, TOPO_ILHA + 1, 2, 1, 0.15, 1, 0xd9c9a8], [-1.2, TOPO_ILHA + 2, 1.2, 1, 0.15, 1, 0xd9c9a8], [-0.5, TOPO_ILHA + 3, -0.5, 0.6, 0.15, 0.6, 0xd9c9a8]];
    case "fronteira": {
      const b = corpo(0xdfe8f5, 0x9fb0c8, 0x7f90a8);
      for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++)
        if (Math.max(Math.abs(x), Math.abs(z)) === 2) b.push([x, TOPO_ILHA, z, 1, 0.45, 1, (x + z) % 2 === 0 ? 0x2f7cf6 : 0xf2c14e]);
      b.push([0, TOPO_ILHA, 0, 1.4, 0.2, 1.4, 0xf2c14e], [2.6, TOPO_ILHA, -2.6, 0.2, 3.2, 0.2, 0xffffff], [2.0, TOPO_ILHA + 2.4, -2.6, 1.1, 0.7, 0.1, 0x2f7cf6]);
      return b;
    }
  }
}

/** a cor de uma ilha trancada: cinza claro, puxado para o azul (a referencia) */
function trancada(cor: number): number {
  const r = (cor >> 16) & 255, g = (cor >> 8) & 255, b = cor & 255, l = 0.3 * r + 0.59 * g + 0.11 * b;
  const v = (k: number) => Math.round(Math.min(255, 0.5 * l + 0.5 * k));
  return (v(196) << 16) | (v(204) << 8) | v(218);
}

const FACES: readonly { n: [number, number, number]; sombra: number; q: readonly [number, number, number][] }[] = [
  { n: [1, 0, 0], sombra: SOMBRA.x, q: [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]] },
  { n: [-1, 0, 0], sombra: SOMBRA.resto, q: [[0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]] },
  { n: [0, 1, 0], sombra: SOMBRA.cima, q: [[0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]] },
  { n: [0, -1, 0], sombra: SOMBRA.resto, q: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]] },
  { n: [0, 0, 1], sombra: SOMBRA.z, q: [[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]] },
  { n: [0, 0, -1], sombra: SOMBRA.resto, q: [[1, 0, 0], [0, 0, 0], [0, 1, 0], [1, 1, 0]] },
];
/** os blocos numa geometria so, com a cor (ja com a sombra da face) em cada vertice */
function geometria(blocos: readonly Bloco[]): THREE.BufferGeometry {
  const pos: number[] = [], cor: number[] = [];
  for (const [x, y0, z, w, h, d, c] of blocos) {
    const r = ((c >> 16) & 255) / 255, g = ((c >> 8) & 255) / 255, b = (c & 255) / 255;
    const ox = x - w / 2, oy = y0, oz = z - d / 2;
    for (const f of FACES) {
      const v = f.q.map(([a, bb, cc]) => [ox + a * w, oy + bb * h, oz + cc * d]);
      for (const k of [0, 1, 2, 0, 2, 3]) { pos.push(...v[k]); cor.push(r * f.sombra, g * f.sombra, b * f.sombra); }
    }
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(cor, 3));
  return geo;
}

class VistaMapa {
  readonly renderer: THREE.WebGLRenderer;
  private readonly cena = new THREE.Scene();
  private readonly camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 4000);
  /* as duas faces: a ordem dos vertices das caixas nao importa (a profundidade resolve o que aparece) */
  private readonly material = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide });
  private readonly raio = new THREE.Raycaster();
  private malha: THREE.Mesh | null = null;

  constructor(canvas: HTMLCanvasElement) {
    THREE.ColorManagement.enabled = false;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    this.renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
    this.renderer.setClearColor(0x000000, 0);
    this.camera.position.set(1, 1, 1).multiplyScalar(1000);
    this.camera.up.set(0, 1, 0);
    this.camera.lookAt(0, 0, 0);
  }

  /** o ponto do plano y = 1 (o tampo das ilhas) que cai no px (x, y) da caixa */
  private noTampo(x: number, y: number, larg: number, alt: number): THREE.Vector3 {
    this.raio.setFromCamera(new THREE.Vector2((x / larg) * 2 - 1, 1 - (y / alt) * 2), this.camera);
    const p = this.raio.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 1, 0), -TOPO_ILHA), new THREE.Vector3());
    if (!p) throw new Error("o raio da câmera não cruza o tampo das ilhas");
    return p;
  }

  desenhar(c: CenaMapa, razao: number): void {
    /* o ColorManagement e global e a ilha do habitat o liga: repor o desta vista antes das cores e do desenho */
    THREE.ColorManagement.enabled = false;
    if (!(c.larg > 0 && c.alt > 0 && c.tam > 0)) throw new Error(`mapa sem tamanho: ${c.larg} x ${c.alt}, ilha ${c.tam}`);
    this.renderer.setPixelRatio(Math.min(2, Math.max(1, razao)));
    this.renderer.setSize(c.larg, c.alt, false);
    /* px de CSS por voxel: o tampo de 7 celulas (a diagonal na tela, 7 x raiz de 2) ocupa a largura da ilha */
    const P = c.tam / (LADO * Math.SQRT2);
    Object.assign(this.camera, { left: -c.larg / (2 * P), right: c.larg / (2 * P), top: c.alt / (2 * P), bottom: -c.alt / (2 * P) });
    this.camera.updateProjectionMatrix();
    this.camera.updateMatrixWorld();
    const centros = c.ilhas.map(i => this.noTampo(i.cx, i.cy, c.larg, c.alt));
    const blocos: Bloco[] = [];
    c.ilhas.forEach((ilha, k) => {
      const o = centros[k];
      for (const [x, y0, z, w, h, d, cor] of blocosDoTema(ilha.tema)) blocos.push([x + o.x, y0 + o.y - TOPO_ILHA, z + o.z, w, h, d, ilha.tranca ? trancada(cor) : cor]);
    });
    /* o trilho: tracinhos entre os tampos, um pouco abaixo deles, so no trecho entre as ilhas */
    for (const t of c.trilhos) {
      const a = centros[t.de], b = centros[t.ate], dist = a.distanceTo(b), n = Math.max(2, Math.floor(dist / 1.1));
      for (let k = 1; k < n; k++) {
        const f = k / n;
        if (f < 0.3 || f > 0.7) continue;
        const p = a.clone().lerp(b, f);
        blocos.push([p.x, p.y - 0.7, p.z, 0.45, 0.16, 0.45, t.feito ? 0x2f7cf6 : 0xaebbd0]);
      }
    }
    if (this.malha) { this.cena.remove(this.malha); this.malha.geometry.dispose(); }
    this.malha = new THREE.Mesh(geometria(blocos), this.material);
    this.cena.add(this.malha);
    this.renderer.render(this.cena, this.camera);
  }

  descartar(): void {
    if (this.malha) this.malha.geometry.dispose();
    this.material.dispose();
    this.renderer.dispose();
  }
}

export interface Mapa3D { desenhar: (c: CenaMapa) => void; parar: () => void }
/** liga o mapa num canvas; falha alto (a tela cai na reserva) se o WebGL nao subir. aoPerder: o contexto do WebGL caiu depois */
export function iniciarMapa3D(canvas: HTMLCanvasElement, aoPerder: () => void): Mapa3D {
  const vista = new VistaMapa(canvas);
  const perdeu = (ev: Event) => { ev.preventDefault(); aoPerder(); };
  canvas.addEventListener("webglcontextlost", perdeu);
  return {
    desenhar: c => vista.desenhar(c, devicePixelRatio || 1),
    parar: () => { canvas.removeEventListener("webglcontextlost", perdeu); vista.descartar(); },
  };
}
