/* O estilo Cassette do habitat (src/habitat.ts): a ilha da grade com as texturas e os objetos do Cassette Beasts, o da demo cassette do
   #480. Os assets sao do jogo do Matheus, extraidos pelas ferramentas locais (D:/Trab/digilab/extrair_cb) para Assets/kits3d/cassette_beasts/:
   nao se redistribuem, ficam fora do repositorio e so o modo dev do Vite os serve (vite.config.ts); sem eles, a cena volta para a ilha.
     - o terreno: a geometria da ilha (degraus), com a textura do jogo por celula: a grama das planicies no tampo, a terra clara no caminho,
       a areia das planicies na areia, a parede media das planicies nos degraus; sem filtro (o pixel do jogo);
     - os objetos: as arvores Tree1 e Tree2 e a pedra da agua da Clareira (json/mapas/Clareira.json: o tronco em malha e as camadas de
       folhagem), e a grama, as flores e os cogumelos como recortes. A folhagem e os recortes ficam em planos de pe virados para o sul:
       as duas cameras do habitat olham sempre para o norte, entao o plano faz o papel do billboard do jogo e cabe num InstancedMesh.
   So vista; todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { curvar, type Variante } from "./cena.ts";
import { rng, type Celula, type Ilha } from "./grade.ts";
import type { Modelo, NomeModelo } from "./modelos.ts";

/** onde o dev serve os assets, relativo a pagina (o mesmo caminho do atlas, src/atlas.ts) */
export const BASE_CASSETTE = "../../../Assets/kits3d/cassette_beasts/";
/** o pixel_size dos sprites do jogo (unidades do jogo por pixel) */
const PIXEL = 0.125;
const PLAINS = "models/world_scenes/world_plains/materials/";
const TEX = {
  grama: [1, 1, 2, 3].map(n => `${PLAINS}world_plains_grass_${n}.webp`),
  /* os dirt_ das planicies sao grama com manchas: o caminho e o path_4 a 6 (a terra clara) */
  caminho: [4, 5, 6].map(n => `${PLAINS}world_plains_path_${n}.webp`),
  areia: [`${PLAINS}world_plains_sand_1.webp`, `${PLAINS}world_plains_sand_2.webp`],
  agua: [`${PLAINS}world_plains_sand_3.webp`],
  parede: [`${PLAINS}world_plains_wall_medium_1.webp`, `${PLAINS}world_plains_wall_medium_2.webp`],
  topoParede: [`${PLAINS}world_plains_wall_top_1.webp`],
} as const;

const ARV = "res://world/objects/static_physics/";
const ENV = "sprites/environment/";
/** o que entra no lugar de cada modelo da grade: obj: um objeto da Clareira; img: um recorte */
const PECAS: Record<NomeModelo, readonly string[]> = {
  arvore_redonda: [`obj:${ARV}tree_1/Tree1.tscn`],
  pinheiro: [`obj:${ARV}tree_1/Tree2.tscn`],
  arbusto: [`img:${ENV}battle/grasslands_grass_3.webp`],
  pedra: [`obj:${ARV}rocks/rock_water_1.tscn`, `obj:${ARV}rocks/rock_water_2.tscn`],
  flor: [`img:${ENV}battle/grasslands_flowers_1.webp`],
  trevo: [`img:${ENV}battle/grasslands_grass_1.webp`],
  grama: [`img:${ENV}battle/grasslands_grass_2.webp`, `img:${ENV}battle/grasslands_grass_1.webp`],
  grama_alta: [`img:${ENV}battle/grasslands_grass_4.webp`],
  samambaia: [`img:${ENV}battle/grasslands_grass_5.webp`],
  cogumelo: [`img:${ENV}world/mushroom_small_1.webp`, `img:${ENV}world/mushroom_small_2.webp`],
};
export const arquivosCassette = (id: NomeModelo): readonly string[] => PECAS[id];

/* ---------- as texturas ---------- */
const cacheTex = new Map<string, Promise<THREE.Texture>>();
/** a textura do jogo, sem filtro e com o v do Godot (para baixo, como a imagem); a promessa resolve com a imagem carregada */
function textura(base: string, p: string): Promise<THREE.Texture> {
  const url = new URL(p, new URL(BASE_CASSETTE, base)).href;
  if (!cacheTex.has(url)) cacheTex.set(url, new THREE.TextureLoader().loadAsync(url).then(t => {
    t.magFilter = t.minFilter = THREE.NearestFilter;
    t.generateMipmaps = false;
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.flipY = false;
    return t;
  }).catch(e => { throw new Error(`cassette: textura nao carregou: ${p} (${(e as Error).message ?? e})`); }));
  return cacheTex.get(url)!;
}
/** o material do jogo: a textura tambem como emissao (a cor sai quase chapada, a luz so soma o relevo), como na demo */
const materialJogo = (map: THREE.Texture | null, lados = THREE.DoubleSide) => curvar(new THREE.MeshLambertMaterial({
  map, emissiveMap: map, emissive: map ? 0xffffff : 0x000000, emissiveIntensity: 0.62, alphaTest: 0.5, side: lados,
}));

/* ---------- o terreno ---------- */
const CANTO: readonly (readonly [number, number])[] = [[0, 0], [1, 0], [1, 1], [0, 1]];
const ARESTAS = [
  { a: 0, b: 1, dx: 0, dz: -1, va: 3, vb: 2 }, { a: 1, b: 2, dx: 1, dz: 0, va: 0, vb: 3 },
  { a: 2, b: 3, dx: 0, dz: 1, va: 1, vb: 0 }, { a: 3, b: 0, dx: -1, dz: 0, va: 2, vb: 1 },
] as const;
class Lote {
  readonly pos: number[] = [];
  readonly uv: number[] = [];
  /** um quadrilatero a-b-c-d com os uv dados; os dois lados desenham (o material e DoubleSide) */
  quad(v: readonly THREE.Vector3[], uv: readonly (readonly [number, number])[]): void {
    for (const k of [0, 1, 2, 0, 2, 3]) { this.pos.push(v[k].x, v[k].y, v[k].z); this.uv.push(uv[k][0], uv[k][1]); }
  }
  geometria(): THREE.BufferGeometry {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(this.pos, 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute(this.uv, 2));
    g.computeVertexNormals();
    return g;
  }
}

/** o terreno da grade com as texturas do jogo: um lote (uma malha) por textura */
export function terrenoCassette(ilha: Ilha, base: string): THREE.Group {
  const lotes = new Map<string, Lote>(), r = rng(29), grupo = new THREE.Group();
  const lote = (p: string) => { if (!lotes.has(p)) lotes.set(p, new Lote()); return lotes.get(p)!; };
  const escolher = (l: readonly string[]) => l[Math.floor(r() * l.length)];
  const UV_TAMPO = [[0, 0], [1, 0], [1, 1], [0, 1]] as const;
  for (let j = 0; j < ilha.prof; j++) for (let i = 0; i < ilha.larg; i++) {
    const x = ilha.x0 + i, z = ilha.z0 + j, c = ilha.cel(x, z)!;
    const p = (k: number, h = c.cantos[k]) => new THREE.Vector3(x + CANTO[k][0], h, z + CANTO[k][1]);
    lote(escolher(TEX[c.tipo])).quad([p(0), p(1), p(2), p(3)], UV_TAMPO);
    for (const e of ARESTAS) parede(ilha, c, x, z, e, lote, escolher);
  }
  for (const [p, l] of lotes) {
    const mat = materialJogo(null);
    void textura(base, p).then(t => { mat.map = mat.emissiveMap = t; mat.emissive.setHex(0xffffff); mat.needsUpdate = true; })
      .catch(err => console.error(err));
    grupo.add(Object.assign(new THREE.Mesh(l.geometria(), mat), { frustumCulled: false }));
  }
  return grupo;
}
/* a parede de uma aresta, em faixas de uma unidade de altura: a de cima com o topo da parede, as outras com a parede media */
function parede(ilha: Ilha, c: Celula, x: number, z: number, e: (typeof ARESTAS)[number], lote: (p: string) => Lote, escolher: (l: readonly string[]) => string): void {
  const viz = ilha.cel(x + e.dx, z + e.dz);
  const ta = c.cantos[e.a], tb = c.cantos[e.b], ba = viz ? viz.cantos[e.va] : -1.6, bb = viz ? viz.cantos[e.vb] : -1.6;
  if (ta - ba < 1e-3 && tb - bb < 1e-3) return;
  const n = Math.max(1, Math.round(Math.max(ta - ba, tb - bb)));
  const [ax, az] = CANTO[e.a], [bx, bz] = CANTO[e.b];
  for (let k = 0; k < n; k++) {
    const f0 = k / n, f1 = (k + 1) / n, y = (t: number, b: number, f: number) => t - (t - b) * f;
    const v = [new THREE.Vector3(x + ax, y(ta, ba, f0), z + az), new THREE.Vector3(x + bx, y(tb, bb, f0), z + bz),
      new THREE.Vector3(x + bx, y(tb, bb, f1), z + bz), new THREE.Vector3(x + ax, y(ta, ba, f1), z + az)];
    lote(escolher(k === 0 && c.tipo !== "agua" ? TEX.topoParede : TEX.parede)).quad(v, [[0, 0], [1, 0], [1, 1], [0, 1]]);
  }
}

/* ---------- os objetos ---------- */
interface Superficie { pos: number[]; nor: number[]; uv: number[]; ind: number[] | null; textura: string | null }
interface ObjetoCB { malhas: { t: number[]; superficies: Superficie[] }[]; sprites: { img: string; t: number[] }[] }
/** uma Transform do Godot (base 3x3 por linhas + origem) como Matrix4 do three */
const matriz = (t: number[]) => new THREE.Matrix4().set(t[0], t[1], t[2], t[9], t[3], t[4], t[5], t[10], t[6], t[7], t[8], t[11], 0, 0, 0, 1);
function geometria(s: Superficie): THREE.BufferGeometry {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(s.pos, 3));
  if (s.nor.length) g.setAttribute("normal", new THREE.Float32BufferAttribute(s.nor, 3));
  if (s.uv.length) g.setAttribute("uv", new THREE.Float32BufferAttribute(s.uv, 2));
  if (s.ind) g.setIndex(s.ind);
  return g;
}
/** um recorte em pe, virado para o sul (+z), com o centro na origem e o tamanho do pixel do jogo; v para baixo (flipY falso) */
function plano(t: THREE.Texture): THREE.BufferGeometry {
  const img = t.image as { width: number; height: number };
  const g = new THREE.PlaneGeometry(img.width * PIXEL, img.height * PIXEL), uv = g.attributes.uv;
  for (let i = 0; i < uv.count; i++) uv.setY(i, 1 - uv.getY(i));
  return g;
}

/** o carregador do estilo: le a Clareira uma vez e monta cada peca (obj: ou img:) na altura do modelo da grade */
export async function carregadorCassette(base: string): Promise<(arquivo: string, id: NomeModelo, modelo: Modelo) => Promise<Variante>> {
  const resp = await fetch(new URL("json/mapas/Clareira.json", new URL(BASE_CASSETTE, base)).href);
  if (!resp.ok) throw new Error(`cassette: sem json/mapas/Clareira.json (HTTP ${resp.status}); ver extrair_cb`);
  const clareira = await resp.json() as { objetos: Record<string, ObjetoCB> };
  return async (arquivo, _id, modelo) => {
    const pecas: { geo: THREE.BufferGeometry; mat: THREE.Material; local: THREE.Matrix4 }[] = [];
    if (arquivo.startsWith("img:")) {
      const t = await textura(base, arquivo.slice(4)), geo = plano(t);
      geo.translate(0, (t.image as { height: number }).height * PIXEL / 2, 0);
      pecas.push({ geo, mat: materialJogo(t), local: new THREE.Matrix4() });
    } else {
      const o = clareira.objetos[arquivo.slice(4)];
      if (!o) throw new Error(`cassette: objeto fora da Clareira: ${arquivo}`);
      for (const mm of o.malhas) for (const s of mm.superficies)
        pecas.push({ geo: geometria(s), mat: materialJogo(s.textura ? await textura(base, s.textura) : null), local: matriz(mm.t) });
      for (const sp of o.sprites) {
        const t = await textura(base, sp.img), m = matriz(sp.t);
        /* so a posicao da transformacao: o recorte fica sempre de pe, virado para a camera */
        pecas.push({ geo: plano(t), mat: materialJogo(t), local: new THREE.Matrix4().makeTranslation(m.elements[12], m.elements[13], m.elements[14] + 0.01 * pecas.length) });
      }
    }
    if (!pecas.length) throw new Error(`cassette: peca vazia: ${arquivo}`);
    /* normaliza a caixa de todas as partes para a altura do modelo, com o pe no chao e o centro em x/z na origem */
    const caixa = new THREE.Box3();
    for (const p of pecas) { p.geo.computeBoundingBox(); caixa.union(p.geo.boundingBox!.clone().applyMatrix4(p.local)); }
    const tam = caixa.getSize(new THREE.Vector3()), centro = caixa.getCenter(new THREE.Vector3());
    if (!(tam.y > 0)) throw new Error(`cassette: peca sem altura: ${arquivo}`);
    const s = modelo.altura / tam.y;
    const norm = new THREE.Matrix4().makeScale(s, s, s).multiply(new THREE.Matrix4().makeTranslation(-centro.x, -caixa.min.y, -centro.z));
    return { pecas: pecas.map(p => ({ ...p, local: norm.clone().multiply(p.local) })) };
  };
}
