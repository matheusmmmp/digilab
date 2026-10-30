/* A vista do mapa no estilo Animal Crossing (poc/mapa_ac.html): o three, só desenho. Lê a grade de mapa.ts e põe na cena:
     - o "mundo curvo": todo material passa por curvar(), que dobra o mundo para baixo pelo quadrado da distância em z ao foco (o
       personagem), como um tronco rolando; o horizonte cai e o fim do mapa some no céu;
     - o terreno gerado da grade: o tampo de cada célula e as paredes dos degraus, com as faixas de estrato dos penhascos do AC e a borda
       de grama em cima;
     - a água por célula (rio, lagoas e mar) com espuma na margem, e a cachoeira onde o rio desce do platô;
     - os modelos dos kits CC0 (KayKit, Quaternius, Kenney), servidos no dev de Assets/kits3d/, como InstancedMesh com material toon;
     - as sombras redondas no chão (as "bolhas" do AC) sob as árvores e o personagem.
   Todos os números são do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ALTURA_NIVEL, LARG, NIVEL_AGUA, PROF, type Celula, type Mapa, type Objeto, rng } from "./mapa.ts";

/* ---------- o mundo curvo ---------- */
export const CURVA = { uCurva: { value: 0.011 }, uFocoZ: { value: 0 }, uTempo: { value: 0 } };
const GLSL_CURVA_PARS = "uniform float uCurva;\nuniform float uFocoZ;\nuniform float uTempo;\n";
/* o lugar do project_vertex do three, com a dobra entre o modelo e a vista */
const GLSL_PROJETAR = `
vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
  mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
  mvPosition = instanceMatrix * mvPosition;
#endif
vec4 pMundo = modelMatrix * mvPosition;
float dzCurva = pMundo.z - uFocoZ;
pMundo.y -= uCurva * dzCurva * dzCurva;
mvPosition = viewMatrix * pMundo;
gl_Position = projectionMatrix * mvPosition;`;
const glslVento = (amp: number) => `
#ifdef USE_INSTANCING
  vec3 baseVento = instanceMatrix[3].xyz;
#else
  vec3 baseVento = vec3(0.0);
#endif
transformed.x += sin(uTempo * 1.7 + baseVento.x * 0.9 + baseVento.z * 0.6) * ${amp.toFixed(3)} * max(transformed.y, 0.0);
transformed.z += cos(uTempo * 1.3 + baseVento.x * 0.5) * ${(amp * 0.5).toFixed(3)} * max(transformed.y, 0.0);`;

/** liga a dobra do mundo (e o vento, se amp > 0) num material do three; devolve o mesmo material */
export function curvar<M extends THREE.Material>(m: M, vento = 0): M {
  m.onBeforeCompile = s => {
    Object.assign(s.uniforms, CURVA);
    s.vertexShader = GLSL_CURVA_PARS + s.vertexShader
      .replace("#include <begin_vertex>", "#include <begin_vertex>" + (vento > 0 ? glslVento(vento) : ""))
      .replace("#include <project_vertex>", GLSL_PROJETAR);
  };
  m.customProgramCacheKey = () => `curva-${vento}`;
  return m;
}

/* o degradê de 3 tons do material toon (o sombreado chapado do AC) */
const GRADIENTE = (() => {
  const t = new THREE.DataTexture(new Uint8Array([110, 110, 110, 255, 185, 185, 185, 255, 255, 255, 255, 255]), 3, 1, THREE.RGBAFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.needsUpdate = true;
  return t;
})();
export const toon = (p: THREE.MeshToonMaterialParameters, vento = 0) => curvar(new THREE.MeshToonMaterial({ gradientMap: GRADIENTE, ...p }), vento);

/* ---------- o terreno ---------- */
const COR = {
  grama: [0x8fd16a, 0x8bcd66, 0x92d46d], caminho: [0xd9c08c, 0xd5bb87], areia: [0xf3e2b0, 0xf0dead],
  fundo: [0xc9b07a], borda: 0x6fb84e,
  estrato: [0xe9c79a, 0xdcae7c, 0xcf9c6a], estratoAreia: [0xe8d39f, 0xdcc48f], margem: [0xa88a5c, 0x97794e],
};
const cor = (hex: number) => new THREE.Color(hex);

class Malha {
  readonly pos: number[] = [];
  readonly nor: number[] = [];
  readonly col: number[] = [];
  /** um triângulo com a normal da face, virado para `fora` (o lado que tem que ficar de frente) */
  tri(a: THREE.Vector3, b: THREE.Vector3, c: THREE.Vector3, k: THREE.Color, fora: THREE.Vector3): void {
    const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).normalize();
    if (n.dot(fora) < 0) { [b, c] = [c, b]; n.negate(); }
    for (const v of [a, b, c]) { this.pos.push(v.x, v.y, v.z); this.nor.push(n.x, n.y, n.z); this.col.push(k.r, k.g, k.b); }
  }
  quad(a: THREE.Vector3, b: THREE.Vector3, c: THREE.Vector3, d: THREE.Vector3, k: THREE.Color, fora: THREE.Vector3): void {
    this.tri(a, b, c, k, fora);
    this.tri(a, c, d, k, fora);
  }
  geometria(): THREE.BufferGeometry {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(this.pos, 3));
    g.setAttribute("normal", new THREE.Float32BufferAttribute(this.nor, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(this.col, 3));
    return g;
  }
}

/* as arestas da célula: [canto a, canto b, vizinho dx, dz, os cantos do vizinho na mesma ordem, a normal para fora] */
const ARESTAS = [
  { a: 0, b: 1, dx: 0, dz: -1, va: 3, vb: 2, n: new THREE.Vector3(0, 0, -1) },
  { a: 1, b: 2, dx: 1, dz: 0, va: 0, vb: 3, n: new THREE.Vector3(1, 0, 0) },
  { a: 2, b: 3, dx: 0, dz: 1, va: 1, vb: 0, n: new THREE.Vector3(0, 0, 1) },
  { a: 3, b: 0, dx: -1, dz: 0, va: 2, vb: 1, n: new THREE.Vector3(-1, 0, 0) },
] as const;
const CANTO_XZ: readonly (readonly [number, number])[] = [[0, 0], [1, 0], [1, 1], [0, 1]];
const FAIXA = 0.28;                       // a altura de uma faixa de estrato
const BORDA_GRAMA = 0.14;                 // a grama que desce pela borda do penhasco

function terreno(mapa: Mapa): THREE.Mesh {
  const m = new Malha(), r = rng(5);
  const cima = new THREE.Vector3(0, 1, 0);
  for (let z = 0; z < PROF; z++) for (let x = 0; x < LARG; x++) {
    const c = mapa.cel(x, z)!;
    const p = (i: number, h = c.cantos[i]) => new THREE.Vector3(x + CANTO_XZ[i][0], h, z + CANTO_XZ[i][1]);
    const paleta = c.tipo === "agua" ? COR.fundo : COR[c.tipo];
    const k = cor(paleta[Math.floor(r() * paleta.length)]);
    m.quad(p(0), p(1), p(2), p(3), k, cima);
    for (const e of ARESTAS) parede(m, mapa, c, x, z, e);
  }
  const g = m.geometria();
  return new THREE.Mesh(g, toon({ vertexColors: true }));
}

/* a parede de uma aresta: do tampo desta célula até o do vizinho (ou até o fundo, na borda do mapa), em faixas */
function parede(m: Malha, mapa: Mapa, c: Celula, x: number, z: number, e: (typeof ARESTAS)[number]): void {
  const viz = mapa.cel(x + e.dx, z + e.dz);
  const ta = c.cantos[e.a], tb = c.cantos[e.b];
  const ba = viz ? viz.cantos[e.va] : -1.6, bb = viz ? viz.cantos[e.vb] : -1.6;
  if (ta - ba < 1e-3 && tb - bb < 1e-3) return;
  const [ax, az] = CANTO_XZ[e.a], [bx, bz] = CANTO_XZ[e.b];
  const ponto = (cx: number, cz: number, h: number) => new THREE.Vector3(x + cx, h, z + cz);
  const alta = Math.max(ta - ba, tb - bb);
  const n = Math.max(1, Math.round(alta / FAIXA));
  const grama = c.tipo === "grama" || c.tipo === "caminho";
  const agua = c.tipo === "agua" || viz?.tipo === "agua";
  const paleta = c.tipo === "areia" ? COR.estratoAreia : agua && alta < 0.8 ? COR.margem : COR.estrato;
  for (let i = 0; i < n; i++) {
    /* as faixas vão de cima para baixo; a de cima é a borda de grama */
    const f0 = i / n, f1 = (i + 1) / n;
    const y = (t: number, f: number, b: number) => t - (t - b) * f;
    let k = cor(paleta[Math.floor(((ta + ba) / 2 - f0 * alta) / FAIXA + 100) % paleta.length]);
    let g0 = f0, g1 = f1;
    if (i === 0 && grama && !agua) {
      const fg = Math.min(BORDA_GRAMA / alta, 0.5);
      m.quad(ponto(ax, az, y(ta, 0, ba)), ponto(bx, bz, y(tb, 0, bb)), ponto(bx, bz, y(tb, fg, bb)), ponto(ax, az, y(ta, fg, ba)), cor(COR.borda), e.n);
      g0 = fg;
      if (g0 >= g1) continue;
    }
    if (agua && alta < 0.8) k = cor(COR.margem[i % 2]);
    m.quad(ponto(ax, az, y(ta, g0, ba)), ponto(bx, bz, y(tb, g0, bb)), ponto(bx, bz, y(tb, g1, bb)), ponto(ax, az, y(ta, g1, ba)), k, e.n);
  }
}

/* ---------- a água ---------- */
const AGUA_VERT = `
${GLSL_CURVA_PARS}
attribute float aMargem;
varying float vMargem;
varying vec2 vXZ;
#include <fog_pars_vertex>
void main() {
  vMargem = aMargem;
  vec3 transformed = position;
  vXZ = position.xz;
  transformed.y += sin(uTempo * 1.4 + position.x * 0.8 + position.z * 0.6) * 0.02;
  ${GLSL_PROJETAR}
  #include <fog_vertex>
}`;
const AGUA_FRAG = `
uniform float uTempo;
varying float vMargem;
varying vec2 vXZ;
#include <fog_pars_fragment>
float ruido(vec2 p) { return sin(p.x * 1.7 + sin(p.y * 2.3)) * sin(p.y * 1.9 + sin(p.x * 1.3)); }
void main() {
  vec3 raso = vec3(0.47, 0.85, 0.93), fundo = vec3(0.20, 0.62, 0.86);
  vec3 c = mix(raso, fundo, smoothstep(0.2, 2.2, vMargem));
  float onda = ruido(vXZ * 1.3 + vec2(uTempo * 0.35, uTempo * 0.2));
  c += vec3(0.06) * smoothstep(0.55, 0.95, onda);
  float espuma = 1.0 - smoothstep(0.18 + 0.08 * sin(uTempo * 2.0 + vXZ.x * 3.0 + vXZ.y * 2.0), 0.34, vMargem);
  c = mix(c, vec3(0.97, 1.0, 1.0), espuma * 0.9);
  gl_FragColor = vec4(c, 1.0);
  #include <colorspace_fragment>
  #include <fog_fragment>
}`;
const CACHOEIRA_FRAG = `
uniform float uTempo;
varying float vMargem;
varying vec2 vXZ;
#include <fog_pars_fragment>
void main() {
  float faixa = fract(vMargem * 2.5 - uTempo * 1.6 + sin(vXZ.x * 7.0) * 0.15);
  vec3 c = mix(vec3(0.55, 0.88, 0.97), vec3(0.95, 1.0, 1.0), smoothstep(0.55, 0.9, faixa));
  gl_FragColor = vec4(c, 1.0);
  #include <colorspace_fragment>
  #include <fog_fragment>
}`;

function materialAgua(frag: string): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    vertexShader: AGUA_VERT, fragmentShader: frag, fog: true,
    uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {}]),
    // os uniforms da curva são os mesmos objetos de CURVA (atualizar CURVA atualiza a água)
  });
}

function agua(mapa: Mapa): THREE.Group {
  /* a distância (em células) de cada célula de água até a terra, por busca em largura; vai nos cantos como a média */
  const dist = new Float32Array(LARG * PROF).fill(99);
  const fila: number[] = [];
  for (let i = 0; i < LARG * PROF; i++) if (mapa.celulas[i].tipo !== "agua") { dist[i] = 0; fila.push(i); }
  for (let q = 0; q < fila.length; q++) {
    const i = fila[q], x = i % LARG, z = (i - x) / LARG;
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx, nz = z + dz;
      if (nx < 0 || nz < 0 || nx >= LARG || nz >= PROF) continue;
      const j = nz * LARG + nx;
      if (dist[j] > dist[i] + 1) { dist[j] = dist[i] + 1; fila.push(j); }
    }
  }
  /* a margem num canto: a menor distância das 4 células em volta (terra = 0), menos meia célula */
  const margemCanto = (cx: number, cz: number) => {
    let d = 99;
    for (const [dx, dz] of [[-1, -1], [0, -1], [-1, 0], [0, 0]]) {
      const x = cx + dx, z = cz + dz;
      d = Math.min(d, x < 0 || z < 0 || x >= LARG || z >= PROF ? 6 : dist[z * LARG + x]);
    }
    return Math.max(0, d - 0.5) + (d === 0 ? 0 : 0.5);
  };
  const pos: number[] = [], margem: number[] = [], cpos: number[] = [], cmar: number[] = [];
  const nivelAgua = (c: Celula) => Math.max(c.nivel, 0) * ALTURA_NIVEL + NIVEL_AGUA;
  for (let z = 0; z < PROF; z++) for (let x = 0; x < LARG; x++) {
    const c = mapa.cel(x, z)!;
    if (c.tipo !== "agua") continue;
    const y = nivelAgua(c);
    const v = (cx: number, cz: number) => { pos.push(x + cx, y, z + cz); margem.push(margemCanto(x + cx, z + cz)); };
    v(0, 0); v(0, 1); v(1, 1); v(0, 0); v(1, 1); v(1, 0);
    /* a cachoeira: a água do platô que encontra a água mais baixa ao sul */
    const sul = mapa.cel(x, z + 1);
    if (sul && sul.tipo === "agua" && nivelAgua(sul) < y - 0.3) {
      const yb = nivelAgua(sul), zf = z + 1 + 0.06;
      const w = (cx: number, cy: number, t: number) => { cpos.push(x + cx, cy, zf); cmar.push(t); };
      w(0, y, 0); w(0, yb, 1); w(1, yb, 1); w(0, y, 0); w(1, yb, 1); w(1, y, 0);
    }
  }
  const grupo = new THREE.Group();
  const malha = (p: number[], mg: number[], frag: string) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(p, 3));
    g.setAttribute("aMargem", new THREE.Float32BufferAttribute(mg, 1));
    const mat = materialAgua(frag);
    Object.assign(mat.uniforms, CURVA);
    mat.side = THREE.DoubleSide;
    grupo.add(new THREE.Mesh(g, mat));
  };
  malha(pos, margem, AGUA_FRAG);
  if (cpos.length) malha(cpos, cmar, CACHOEIRA_FRAG);
  /* o mar continua além do mapa, até o horizonte do sul */
  const mar = new THREE.PlaneGeometry(LARG + 120, 60).rotateX(-Math.PI / 2).translate(LARG / 2, NIVEL_AGUA - 0.01, PROF + 30);
  mar.setAttribute("aMargem", new THREE.Float32BufferAttribute(new Array(mar.attributes.position.count).fill(6), 1));
  const matMar = materialAgua(AGUA_FRAG);
  Object.assign(matMar.uniforms, CURVA);
  grupo.add(new THREE.Mesh(mar, matMar));
  return grupo;
}

/* ---------- as sombras redondas ---------- */
const TEX_SOMBRA = (() => {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d")!, gr = g.createRadialGradient(32, 32, 4, 32, 32, 31);
  gr.addColorStop(0, "rgba(40,70,30,0.42)");
  gr.addColorStop(0.65, "rgba(40,70,30,0.28)");
  gr.addColorStop(1, "rgba(40,70,30,0)");
  g.fillStyle = gr;
  g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
})();
export function materialSombra(): THREE.MeshBasicMaterial {
  return curvar(new THREE.MeshBasicMaterial({ map: TEX_SOMBRA, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }));
}
export const GEO_SOMBRA = new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2);

/* ---------- os modelos dos kits ---------- */
const KIT = "./Assets/kits3d/";
const KAY = KIT + "kaykit_forest/x/KayKit_Forest_Nature_Pack_1.0_FREE/Assets/gltf/";
const QUA = KIT + "quaternius_nature/x/glTF/";
const KEN = KIT + "kenney_nature/x/Models/GLTF format/";
/** cada modelo do mapa: as variantes (arquivos), a altura alvo em células, se balança ao vento e o raio da sombra (0 = sem sombra) */
interface Modelo { arquivos: string[]; altura: number; vento: number; sombra: number }
const MODELOS: Record<string, Modelo> = {
  arvore_redonda: { arquivos: ["CommonTree_1", "CommonTree_2", "CommonTree_3", "CommonTree_4", "CommonTree_5"].map(n => QUA + n + ".gltf"), altura: 4.2, vento: 0.004, sombra: 1.5 },
  pinheiro: { arquivos: ["Pine_1", "Pine_2", "Pine_3", "Pine_5"].map(n => QUA + n + ".gltf"), altura: 5.0, vento: 0.003, sombra: 1.3 },
  arbusto: { arquivos: ["Bush_Common", "Bush_Common_Flowers"].map(n => QUA + n + ".gltf").concat(KAY + "Bush_1_A_Color1.gltf", KAY + "Bush_2_A_Color1.gltf"), altura: 1.0, vento: 0.02, sombra: 0.7 },
  pedra: { arquivos: ["Rock_1_A_Color1", "Rock_2_A_Color1", "Rock_3_A_Color1"].map(n => KAY + n + ".gltf"), altura: 0.6, vento: 0, sombra: 0.5 },
  toco: { arquivos: [KEN + "stump_round.glb", KEN + "stump_oldTall.glb"], altura: 0.35, vento: 0, sombra: 0.35 },
  tronco: { arquivos: [KEN + "log_large.glb"], altura: 0.42, vento: 0, sombra: 0.6 },
  flor: { arquivos: ["Flower_3_Group", "Flower_4_Group", "Flower_3_Single", "Flower_4_Single"].map(n => QUA + n + ".gltf"), altura: 0.45, vento: 0.06, sombra: 0 },
  trevo: { arquivos: ["Clover_1", "Clover_2"].map(n => QUA + n + ".gltf"), altura: 0.2, vento: 0.05, sombra: 0 },
  grama: { arquivos: ["Grass_Common_Short", "Grass_Wispy_Short", "Grass_Common_Tall"].map(n => QUA + n + ".gltf"), altura: 0.35, vento: 0.08, sombra: 0 },
};

interface Variante { pecas: { geo: THREE.BufferGeometry; mat: THREE.Material; local: THREE.Matrix4 }[] }

async function carregarVariante(loader: GLTFLoader, url: string, modelo: Modelo): Promise<Variante> {
  const gltf = await loader.loadAsync(url);
  const raiz = gltf.scene;
  raiz.updateMatrixWorld(true);
  const caixa = new THREE.Box3().setFromObject(raiz);
  const tam = caixa.getSize(new THREE.Vector3()), centro = caixa.getCenter(new THREE.Vector3());
  if (!(tam.y > 0)) throw new Error(`modelo sem altura: ${url}`);
  const s = modelo.altura / tam.y;
  const norm = new THREE.Matrix4().makeScale(s, s, s).multiply(new THREE.Matrix4().makeTranslation(-centro.x, -caixa.min.y, -centro.z));
  const pecas: Variante["pecas"] = [];
  raiz.traverse(o => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    if (mats.length !== 1) throw new Error(`modelo com vários materiais por malha: ${url}`);
    const orig = mats[0] as THREE.MeshStandardMaterial;
    const mat = toon({
      map: orig.map, color: orig.color, vertexColors: !!mesh.geometry.attributes.color && orig.vertexColors,
      alphaTest: orig.alphaTest > 0 ? Math.max(orig.alphaTest, 0.4) : 0, side: orig.side, transparent: false,
    }, modelo.vento);
    pecas.push({ geo: mesh.geometry, mat, local: norm.clone().multiply(mesh.matrixWorld) });
  });
  return { pecas };
}

/** carrega os modelos e põe os objetos do mapa como instâncias; devolve o grupo e quantos arquivos faltaram */
export async function objetos(mapa: Mapa, aoProgresso: (feito: number, total: number) => void): Promise<{ grupo: THREE.Group; faltas: string[] }> {
  const loader = new GLTFLoader(), grupo = new THREE.Group(), faltas: string[] = [];
  const usados = new Set(mapa.objetos.map(o => o.modelo));
  const variantes = new Map<string, (Variante | null)[]>();
  const tarefas = [...usados].flatMap(id => MODELOS[id].arquivos.map((url, i) => ({ id, url, i })));
  let feito = 0;
  await Promise.all(tarefas.map(async t => {
    let v: Variante | null = null;
    try { v = await carregarVariante(loader, t.url, MODELOS[t.id]); } catch (e) { faltas.push(`${t.url}: ${(e as Error).message}`); }
    if (!variantes.has(t.id)) variantes.set(t.id, []);
    variantes.get(t.id)![t.i] = v;
    aoProgresso(++feito, tarefas.length);
  }));
  /* agrupa os objetos por (modelo, variante) e monta um InstancedMesh por peça */
  const grupos = new Map<string, Objeto[]>();
  mapa.objetos.forEach((o, i) => {
    const vs = variantes.get(o.modelo)!, j = i % vs.length;
    if (!vs[j]) return;
    const k = `${o.modelo}|${j}`;
    if (!grupos.has(k)) grupos.set(k, []);
    grupos.get(k)!.push(o);
  });
  const sombras: { x: number; z: number; r: number }[] = [];
  for (const [k, lista] of grupos) {
    const [id, j] = k.split("|");
    const v = variantes.get(id)![Number(j)]!;
    const lugar = lista.map(o => new THREE.Matrix4().compose(
      new THREE.Vector3(o.x, mapa.altura(o.x, o.z), o.z),
      new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), o.giro),
      new THREE.Vector3(o.escala, o.escala, o.escala)));
    for (const p of v.pecas) {
      const im = new THREE.InstancedMesh(p.geo, p.mat, lista.length);
      lugar.forEach((m, i) => im.setMatrixAt(i, m.clone().multiply(p.local)));
      im.frustumCulled = false;     // a dobra muda onde a peça aparece; o volume do three não sabe disso
      grupo.add(im);
    }
    if (MODELOS[id].sombra > 0) for (const o of lista) sombras.push({ x: o.x, z: o.z, r: MODELOS[id].sombra * o.escala });
  }
  const somb = new THREE.InstancedMesh(GEO_SOMBRA, materialSombra(), sombras.length);
  sombras.forEach((s, i) => somb.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(s.x, mapa.altura(s.x, s.z) + 0.02, s.z),
    new THREE.Quaternion(), new THREE.Vector3(s.r * 2, 1, s.r * 2))));
  somb.frustumCulled = false;
  somb.renderOrder = 1;
  grupo.add(somb);
  return { grupo, faltas };
}

/* ---------- o céu ---------- */
export const COR_HORIZONTE = 0xcfeefc;
function ceu(): THREE.Texture {
  const c = document.createElement("canvas");
  c.width = 4; c.height = 256;
  const g = c.getContext("2d")!, gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, "#3d8de8");
  gr.addColorStop(0.55, "#7fc0f5");
  gr.addColorStop(1, "#cfeefc");
  g.fillStyle = gr;
  g.fillRect(0, 0, 4, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* as nuvens: planos brancos e fofos bem longe, que não dobram (ficam no céu) */
function nuvens(): THREE.Group {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 128;
  const g = c.getContext("2d")!;
  g.fillStyle = "#ffffff";
  for (const [x, y, r] of [[70, 80, 38], [120, 60, 50], [175, 78, 40], [100, 92, 34], [150, 95, 30]]) { g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const grupo = new THREE.Group(), r = rng(9);
  for (let i = 0; i < 9; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, fog: false, depthWrite: false, opacity: 0.92 }));
    const w = 30 + r() * 30;
    s.scale.set(w, w / 2, 1);
    s.position.set(-40 + r() * (LARG + 80), 26 + r() * 16, -70 - r() * 30);
    grupo.add(s);
  }
  return grupo;
}

/** monta a cena estática: céu, névoa, luz, terreno, água e nuvens (os objetos e o personagem entram depois) */
export function montarCena(mapa: Mapa): THREE.Scene {
  const cena = new THREE.Scene();
  cena.background = ceu();
  cena.fog = new THREE.Fog(COR_HORIZONTE, 26, 62);
  cena.add(new THREE.HemisphereLight(0xdff1ff, 0x86b85c, 1.6));
  const sol = new THREE.DirectionalLight(0xfff1d6, 2.2);
  sol.position.set(-0.6, 1, 0.75);
  cena.add(sol);
  cena.add(terreno(mapa), agua(mapa), nuvens());
  return cena;
}
