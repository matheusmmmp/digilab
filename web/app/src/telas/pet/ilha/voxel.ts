/* O estilo Voxel do habitat (src/habitat.ts): a mesma ilha da grade (grade.ts) em cubos, no jeito do POC voxel do #480 (Cube World),
   gerada por codigo e sem nenhum asset. So desenho: a area andavel continua plana no nivel 0 e o pet anda onde o motor diz.
     - o terreno: cada celula em 2 x 2 colunas de cubos, a altura da grade arredondada para degraus de DEGRAU; a cor por tipo (grama da
       regiao, terra do caminho, areia, fundo da agua), com o "granulado" (uma variacao pequena de brilho por cubo) e as camadas da parede
       (a grama no topo, a terra e a pedra embaixo);
     - os objetos da grade (as arvores, os pinheiros, os arbustos, as pedras, as flores e a grama) como modelos de cubos feitos aqui, no
       tamanho da tabela MODELOS, instanciados como os kits da ilha; a agua e o ceu sao os da ilha.
   Todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GEO_SOMBRA, Malha, materialSombra, toon, type Objetos } from "./cena.ts";
import { FORA, rng, type Ilha, type Objeto } from "./grade.ts";
import { MODELOS, type NomeModelo } from "./modelos.ts";

/** o lado da coluna (meia celula) e a altura de um degrau de cubo, em celulas */
const LADO = 0.5, DEGRAU = 0.25;
const GRAMA: Readonly<Record<string, readonly number[]>> = {
  casa: [0x7ccf4f, 0x76c94a], jardim: [0x6dc246, 0x67bc41], campo: [0x93cc52, 0x8bc54c], mata: [0x4f9e3a, 0x4a9836], [FORA]: [0x6dc246, 0x67bc41],
};
const COR = { caminho: 0xc89a5c, areia: 0xf0d896, fundo: 0xb99a62, terra: 0x9a6b3e, pedra: 0x8d8f94, neve: 0xf4f7fb } as const;

/** a cor com o granulado: o brilho varia ate +-GRAO, sempre igual para a mesma coluna */
const GRAO = 0.07;
function granular(hex: number, r: () => number): THREE.Color {
  const c = new THREE.Color(hex), f = 1 + (r() * 2 - 1) * GRAO;
  return c.setRGB(Math.min(1, c.r * f), Math.min(1, c.g * f), Math.min(1, c.b * f));
}
const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const FORAS = { cima: V(0, 1, 0), n: V(0, 0, -1), s: V(0, 0, 1), o: V(-1, 0, 0), l: V(1, 0, 0) } as const;

/** o terreno em cubos (uma malha so, com as faces escondidas cortadas) */
export function terrenoVoxel(ilha: Ilha): THREE.Mesh {
  const m = new Malha(), r = rng(17), n = 1 / LADO;
  const cols = ilha.larg * n, lins = ilha.prof * n, alt = new Float32Array(cols * lins), cel: (ReturnType<Ilha["cel"]>)[] = [];
  /* a altura de cada coluna: a do meio dela na grade, em degraus (a agua: o fundo) */
  for (let j = 0; j < lins; j++) for (let i = 0; i < cols; i++) {
    const x = ilha.x0 + (i + 0.5) * LADO, z = ilha.z0 + (j + 0.5) * LADO, c = ilha.cel(Math.floor(x), Math.floor(z));
    if (!c) throw new Error(`voxel: coluna fora da grade (${x}, ${z})`);
    const fx = x - Math.floor(x), fz = z - Math.floor(z);
    /* a media dos cantos pesada pela posicao (bilinear), como o tampo da celula */
    const h = c.cantos[0] * (1 - fx) * (1 - fz) + c.cantos[1] * fx * (1 - fz) + c.cantos[2] * fx * fz + c.cantos[3] * (1 - fx) * fz;
    alt[j * cols + i] = Math.round(h / DEGRAU) * DEGRAU;
    cel.push(c);
  }
  const altura = (i: number, j: number) => i < 0 || j < 0 || i >= cols || j >= lins ? -1.75 : alt[j * cols + i];
  for (let j = 0; j < lins; j++) for (let i = 0; i < cols; i++) {
    const c = cel[j * cols + i]!, h = alt[j * cols + i], x0 = ilha.x0 + i * LADO, z0 = ilha.z0 + j * LADO, x1 = x0 + LADO, z1 = z0 + LADO;
    const topo = c.tipo === "agua" ? COR.fundo : c.tipo === "grama" ? GRAMA[c.regiao][(i + j) % GRAMA[c.regiao].length] : COR[c.tipo];
    if (topo === undefined) throw new Error("voxel: regiao sem cor de grama: " + c.regiao);
    const kTopo = granular(h >= 2.4 && c.tipo === "grama" ? COR.neve : topo, r);
    m.quad(V(x0, h, z0), V(x1, h, z0), V(x1, h, z1), V(x0, h, z1), kTopo, FORAS.cima);
    /* as paredes ate a coluna vizinha, um degrau por vez: o primeiro na cor do topo, depois terra, e pedra abaixo de 3 degraus */
    for (const [di, dj, fora, a, b] of [
      [0, -1, FORAS.n, [x0, z0], [x1, z0]], [0, 1, FORAS.s, [x1, z1], [x0, z1]], [-1, 0, FORAS.o, [x0, z1], [x0, z0]], [1, 0, FORAS.l, [x1, z0], [x1, z1]],
    ] as const) {
      const hv = altura(i + di, j + dj);
      for (let y = h, k = 0; y > hv + 1e-4; y -= DEGRAU, k++) {
        const y0 = Math.max(hv, y - DEGRAU);
        const base = k === 0 && c.tipo !== "agua" ? (c.tipo === "grama" ? topo : COR[c.tipo === "caminho" ? "terra" : c.tipo]) : k < 3 ? COR.terra : COR.pedra;
        const kk = granular(base, r);
        if (k === 0) kk.multiplyScalar(0.92);
        m.quad(V(a[0], y, a[1]), V(b[0], y, b[1]), V(b[0], y0, b[1]), V(a[0], y0, a[1]), kk, fora);
      }
    }
  }
  return new THREE.Mesh(m.geometria(), toon({ vertexColors: true }));
}

/* ---------- os modelos de cubos ---------- */
/** um modelo: a lista de cubos (centro x/z, base y, lado w/h/d, cor), numa grade de 1 unidade; a altura e normalizada depois */
type Cubo = [x: number, y: number, z: number, w: number, h: number, d: number, cor: number];

/** uma bola de cubos de raio r (em unidades) com o centro em (cx, cy, cz) */
function bola(cx: number, cy: number, cz: number, r: number, cores: readonly number[], semente: number, achatar = 1): Cubo[] {
  const s = rng(semente), lista: Cubo[] = [], R = Math.ceil(r);
  for (let y = -R; y <= R; y++) for (let z = -R; z <= R; z++) for (let x = -R; x <= R; x++) {
    const d = Math.hypot(x, y / achatar, z);
    if (d > r + (s() - 0.5) * 0.6) continue;
    lista.push([cx + x, cy + y, cz + z, 1, 1, 1, cores[Math.floor(s() * cores.length)]]);
  }
  return lista;
}
const MODELOS_VOXEL: Record<NomeModelo, () => Cubo[]> = {
  arvore_redonda: () => [[0, 0, 0, 1, 4, 1, 0x7a5132], ...bola(0, 5.5, 0, 2.6, [0x5cb447, 0x52a83f, 0x68c050], 3)],
  pinheiro: () => [[0, 0, 0, 1, 2, 1, 0x6b4428], ...[3, 2.5, 2, 1.5, 1].flatMap((w, k) => [[0, 2 + k * 1.6, 0, w * 2, 1.6, w * 2, k % 2 ? 0x2f7a46 : 0x377f4c] as Cubo])],
  arbusto: () => bola(0, 1.2, 0, 1.6, [0x4f9e3a, 0x5aab43, 0x63b54b], 5, 0.8),
  pedra: () => bola(0, 1, 0, 1.4, [0x9a9ca1, 0x8a8c91, 0xa7a9ad], 7, 0.7),
  flor: () => [[0, 0, 0, 0.4, 2, 0.4, 0x4e9a3a], [0, 2, 0, 1.2, 0.8, 1.2, 0xf27aa8], [0, 2.2, 0, 0.5, 0.5, 0.5, 0xffe066]],
  trevo: () => [[-0.5, 0, 0, 1, 0.5, 1, 0x58b04a], [0.5, 0, 0.3, 1, 0.5, 1, 0x4fa642]],
  grama: () => [[-0.4, 0, 0, 0.4, 1.4, 0.4, 0x6cc04c], [0.3, 0, 0.2, 0.4, 1.8, 0.4, 0x5fb444], [0, 0, -0.4, 0.4, 1.1, 0.4, 0x74c752]],
  grama_alta: () => [[-0.4, 0, 0, 0.4, 2.2, 0.4, 0x8bc54c], [0.3, 0, 0.2, 0.4, 2.8, 0.4, 0x82bd46], [0, 0, -0.4, 0.4, 1.9, 0.4, 0x93cc52]],
  samambaia: () => [[0, 0, 0, 2.2, 0.6, 0.6, 0x3f8f3a], [0, 0, 0, 0.6, 0.6, 2.2, 0x47983f], [0, 0.6, 0, 1.2, 0.5, 1.2, 0x4fa045]],
  cogumelo: () => [[0, 0, 0, 0.8, 1.4, 0.8, 0xf4ead8], [0, 1.4, 0, 2.2, 0.8, 2.2, 0xd8413a], [0.5, 2.2, 0.3, 0.4, 0.1, 0.4, 0xffffff]],
};

/** os cubos de um modelo numa geometria, com a base no chao e a altura da tabela MODELOS */
function geometriaModelo(id: NomeModelo): THREE.BufferGeometry {
  const cubos = MODELOS_VOXEL[id](), m = new Malha();
  const topo = Math.max(...cubos.map(c => c[1] + c[4])), s = MODELOS[id].altura / topo;
  for (const [cx, y, cz, w, h, d, cor] of cubos) {
    const x0 = (cx - w / 2) * s, x1 = (cx + w / 2) * s, y0 = y * s, y1 = (y + h) * s, z0 = (cz - d / 2) * s, z1 = (cz + d / 2) * s, k = new THREE.Color(cor);
    const escura = k.clone().multiplyScalar(0.82);
    m.quad(V(x0, y1, z0), V(x1, y1, z0), V(x1, y1, z1), V(x0, y1, z1), k, FORAS.cima);
    m.quad(V(x0, y1, z0), V(x1, y1, z0), V(x1, y0, z0), V(x0, y0, z0), escura, FORAS.n);
    m.quad(V(x0, y1, z1), V(x1, y1, z1), V(x1, y0, z1), V(x0, y0, z1), escura, FORAS.s);
    m.quad(V(x0, y1, z0), V(x0, y1, z1), V(x0, y0, z1), V(x0, y0, z0), escura, FORAS.o);
    m.quad(V(x1, y1, z0), V(x1, y1, z1), V(x1, y0, z1), V(x1, y0, z0), escura, FORAS.l);
  }
  return m.geometria();
}

/** os objetos da grade como modelos de cubos (sincrono: nada para baixar); a mesma forma de objetos() da ilha */
export function objetosVoxel(ilha: Ilha): Objetos {
  const porModelo = new Map<NomeModelo, Objeto[]>();
  for (const o of ilha.objetos) { if (!porModelo.has(o.modelo)) porModelo.set(o.modelo, []); porModelo.get(o.modelo)!.push(o); }
  const grupo = new THREE.Group(), grama: THREE.InstancedMesh[] = [], sombras: { x: number; z: number; r: number }[] = [];
  for (const [id, lista] of porModelo) {
    const im = new THREE.InstancedMesh(geometriaModelo(id), toon({ vertexColors: true }, MODELOS[id].vento), lista.length);
    lista.forEach((o, i) => im.setMatrixAt(i, new THREE.Matrix4().compose(V(o.x, ilha.altura(o.x, o.z), o.z),
      /* os cubos giram so de 90 em 90 graus: o voxel nao fica torto */
      new THREE.Quaternion().setFromAxisAngle(FORAS.cima, Math.round(o.giro / (Math.PI / 2)) * (Math.PI / 2)), V(o.escala, o.escala, o.escala))));
    im.frustumCulled = false;
    grupo.add(im);
    if (id === "grama" || id === "grama_alta") grama.push(im);
    if (MODELOS[id].sombra > 0) for (const o of lista) sombras.push({ x: o.x, z: o.z, r: MODELOS[id].sombra * o.escala });
  }
  if (sombras.length) {
    const somb = new THREE.InstancedMesh(GEO_SOMBRA, materialSombra(), sombras.length);
    sombras.forEach((s, i) => somb.setMatrixAt(i, new THREE.Matrix4().compose(V(s.x, ilha.altura(s.x, s.z) + 0.02, s.z), new THREE.Quaternion(), V(s.r * 2, 1, s.r * 2))));
    somb.frustumCulled = false;
    somb.renderOrder = 1;
    grupo.add(somb);
  }
  return { grupo, grama };
}
