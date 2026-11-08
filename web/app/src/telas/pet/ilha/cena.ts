/* A cena da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H2): o three, so desenho, adaptado da vista do POC poc/mapa_ac/cena.ts (uma copia
   adaptada, e nao um import: o G-FRONTEIRA segura que as telas nao importam o POC). Le a grade (grade.ts) e poe na cena:
     - o mundo curvo: todo material passa por curvar(), que dobra o mundo para baixo pelo quadrado da distancia ao foco (o pet) ao longo
       da direcao em que a camera olha (z, sem a camera livre),
       a mesma conta de curva.ts (dobrarY), que a vista usa para passar da tela ao mapa e de volta;
     - o terreno: o tampo de cada celula e as paredes dos degraus, com as faixas de estrato e a borda de grama em cima; a grama com o tom
       da regiao do layout;
     - a agua por celula (o rio, a lagoa e o mar) com a espuma na margem, a cachoeira onde o rio desce do plato e o mar ate o horizonte;
     - os modelos dos kits CC0 (modelos.ts, em public/kits3d/) como InstancedMesh com material toon de 3 tons e vento nas folhagens;
     - as sombras redondas (as "bolhas" do AC), o ceu em degrade, as nuvens e a nevoa da cor do horizonte;
     - o dia e a noite (aplicarNoite): o ceu, a nevoa, a luz e a agua.
   O vento e a agua andam por uTempo; com movimento reduzido, a vista o deixa parado. Todos os numeros sao do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { CEU_SEM_PINTURA, DIA, DOBRA_K, NOITE } from "./constantes.ts";
import { ALTURA_NIVEL, FORA, NIVEL_AGUA, rng, type Celula, type Ilha, type Objeto } from "./grade.ts";
import { MODELOS, type Modelo, type NomeLugar, type NomeModelo } from "./modelos.ts";

/* ---------- o mundo curvo ---------- */
/** os uniforms globais: a dobra, o foco (o pet) e a direcao da dobra no chao (a da camera; z sem a camera livre), o tempo (s), o vento
    (1 = ligado, 0 = a qualidade caiu) e a noite (0 a 1) */
export const CURVA = {
  uCurva: { value: DOBRA_K }, uFocoX: { value: 0 }, uFocoZ: { value: 0 }, uDirX: { value: 0 }, uDirZ: { value: 1 },
  uTempo: { value: 0 }, uVento: { value: 1 }, uNoite: { value: 0 },
};
const GLSL_CURVA_PARS = "uniform float uCurva;\nuniform float uFocoX;\nuniform float uFocoZ;\nuniform float uDirX;\nuniform float uDirZ;\n"
  + "uniform float uTempo;\nuniform float uVento;\nuniform float uNoite;\n";
/* o lugar do project_vertex do three, com a dobra entre o modelo e a vista (curva.ts, dobrarY, faz a mesma conta) */
const GLSL_PROJETAR = `
vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
  mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
  mvPosition = instanceMatrix * mvPosition;
#endif
vec4 pMundo = modelMatrix * mvPosition;
float dzCurva = (pMundo.x - uFocoX) * uDirX + (pMundo.z - uFocoZ) * uDirZ;
pMundo.y -= uCurva * dzCurva * dzCurva;
mvPosition = viewMatrix * pMundo;
gl_Position = projectionMatrix * mvPosition;`;
const glslVento = (amp: number) => `
#ifdef USE_INSTANCING
  vec3 baseVento = instanceMatrix[3].xyz;
#else
  vec3 baseVento = vec3(0.0);
#endif
transformed.x += uVento * sin(uTempo * 1.7 + baseVento.x * 0.9 + baseVento.z * 0.6) * ${amp.toFixed(3)} * max(transformed.y, 0.0);
transformed.z += uVento * cos(uTempo * 1.3 + baseVento.x * 0.5) * ${(amp * 0.5).toFixed(3)} * max(transformed.y, 0.0);`;

/** liga a dobra do mundo (e o vento, se amp > 0) num material do three; devolve o mesmo material. `mexer`: um trecho de GLSL depois do
    begin_vertex (pode mudar `transformed`, com os uniforms da curva; as particulas do estilo digital, digital.ts), com o nome dele na chave */
export function curvar<M extends THREE.Material>(m: M, vento = 0, mexer?: { nome: string; glsl: string }): M {
  m.onBeforeCompile = s => {
    Object.assign(s.uniforms, CURVA);
    s.vertexShader = GLSL_CURVA_PARS + s.vertexShader
      .replace("#include <begin_vertex>", "#include <begin_vertex>" + (vento > 0 ? glslVento(vento) : "") + (mexer?.glsl ?? ""))
      .replace("#include <project_vertex>", GLSL_PROJETAR);
  };
  m.customProgramCacheKey = () => `curva-${vento}-${mexer?.nome ?? ""}`;
  return m;
}

/* o degrade de 3 tons do material toon (o sombreado chapado do AC) */
const GRADIENTE = (() => {
  const t = new THREE.DataTexture(new Uint8Array([110, 110, 110, 255, 185, 185, 185, 255, 255, 255, 255, 255]), 3, 1, THREE.RGBAFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.needsUpdate = true;
  return t;
})();
/** o degrade dos materiais toon criados daqui em diante: o de tres tons, ou o de dois no estilo digital (usarDoisTons, chamado pelo estilo
    antes de montar a cena; os itens e os modelos carregados depois entram ja com ele) */
let gradienteAtual: THREE.Texture = GRADIENTE;
export const toon = (p: THREE.MeshToonMaterialParameters, vento = 0) => curvar(new THREE.MeshToonMaterial({ gradientMap: gradienteAtual, ...p }), vento);
/* o cel shading de dois tons do estilo digital (docs/TAREFA_V3_MAPA_DIGITAL.md, D1): a sombra e a luz, sem o meio-tom */
const GRADIENTE_DOIS = (() => {
  const t = new THREE.DataTexture(new Uint8Array([150, 150, 150, 255, 255, 255, 255, 255]), 2, 1, THREE.RGBAFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.needsUpdate = true;
  return t;
})();
/** os materiais toon novos com dois tons (o estilo digital) ou tres (os outros); vale ate a proxima chamada */
export function usarDoisTons(sim: boolean): void { gradienteAtual = sim ? GRADIENTE_DOIS : GRADIENTE; }
/** passa os materiais toon de tres tons de um objeto (e dos filhos) para os dois tons do estilo digital */
export function doisTons(o: THREE.Object3D): void {
  o.traverse(f => {
    const ms = (f as THREE.Mesh).material;
    for (const m of Array.isArray(ms) ? ms : ms ? [ms] : []) {
      const t = m as THREE.MeshToonMaterial;
      if (t.isMeshToonMaterial && t.gradientMap === GRADIENTE) { t.gradientMap = GRADIENTE_DOIS; t.needsUpdate = true; }
    }
  });
}

/* ---------- o terreno ---------- */
/** a grama por regiao do layout (a casa aparada e clara, o campo mais seco, a mata mais escura) e a da moldura */
export interface PaletaTerreno {
  grama: Readonly<Record<string, readonly number[]>>; caminho: readonly number[]; areia: readonly number[]; fundo: readonly number[];
  borda: number; estrato: readonly number[]; estratoAreia: readonly number[]; margem: readonly number[];
  /** o chao pintado (pintarTerreno; o estilo digital, D5): a grama com manchas e folhas desenhadas, sem o xadrez, e a pedra em placas */
  pintado?: boolean;
}
const GRAMA: Readonly<Record<string, readonly number[]>> = {
  casa: [0x9cdb72, 0x98d76e], jardim: [0x8fd16a, 0x8bcd66, 0x92d46d], campo: [0xa9d870, 0xa4d36b, 0xaedb74],
  mata: [0x74b957, 0x70b553, 0x78bd5b], [FORA]: [0x8fd16a, 0x8bcd66, 0x92d46d],
};
/** a paleta da ilha (o estilo Animal Crossing); os outros estilos do habitat (estilos.ts) trocam so as cores */
export const PALETA_ILHA: PaletaTerreno = {
  grama: GRAMA, caminho: [0xd9c08c, 0xd5bb87], areia: [0xf3e2b0, 0xf0dead], fundo: [0xc9b07a], borda: 0x6fb84e,
  estrato: [0xe9c79a, 0xdcae7c, 0xcf9c6a], estratoAreia: [0xe8d39f, 0xdcc48f], margem: [0xa88a5c, 0x97794e],
};
/** a paleta do estilo digital (docs/TAREFA_V3_MAPA_DIGITAL.md, D1; a maquete B): a grama em verdes saturados de anime (dois por regiao,
    sorteados por celula, como um xadrez solto; o revisor achou a primeira rodada quase neon, e a saturacao caiu ~15 %), o caminho de terra quente, o barranco de pedra cinza (as faixas de estrato) com a borda de
    musgo, a agua e a areia mais vivas. PROPOSTO, SEM FONTE */
export const PALETA_DIGITAL: PaletaTerreno = {
  grama: {
    casa: [0x74c45c, 0x68b952, 0x7dcb63], jardim: [0x6cbf55, 0x60b44b, 0x75c75d], campo: [0x82c862, 0x77be58, 0x8acf69],
    mata: [0x55a347, 0x4c9940, 0x5caa4e], [FORA]: [0x6cbf55, 0x60b44b, 0x75c75d],
  },
  caminho: [0xe2ba74, 0xdab26c], areia: [0xf8e5aa, 0xf2dc9e], fundo: [0x8fc7d8], borda: 0x4cb339,
  /* D5: a pedra numa cor so (as placas e as rachaduras vem da pintura), e o chao pintado */
  estrato: [0x9ea6ad], estratoAreia: [0xe2cf98, 0xd6c08a], margem: [0x8f969c, 0x7e858b], pintado: true,
};
/** as florzinhas do chao do estilo digital: brancas, rosa e amarelas, salpicadas na grama (a maquete B); a densidade por celula de grama e
    o raio (celulas). D5: menos soltas e mais em manchas, uma cor por mancha (o vermelho e o amarelo da maquete), de pe numa haste.
    PROPOSTO, SEM FONTE */
const FLORES = {
  cores: [0xffffff, 0xffffff, 0xff9ec8, 0xffe066], porCelula: 0.45, raio: 0.06,
  mancha: { chance: 0.11, flores: [5, 11], raio: 0.75, cores: [0xe8433a, 0xffd23a, 0xffd23a, 0xffffff, 0xff8fc0], tamanho: 0.075, haste: 0.09 },
} as const;
/** os tufos de grama do estilo digital (D5; a grama alta da maquete B): por celula de grama, quantos tufos, quantas folhas por tufo, a
    altura e a largura da folha (celulas), e as cores da base e da ponta. PROPOSTO, SEM FONTE */
/*  D5, depois do revisor: em moitas (a chance de uma celula ter uma, os tufos por moita e o raio dela), com chao liso entre elas, e mais
    claros (o capim espalhado virava ruido, sobretudo a noite e no celular) */
const TUFOS = { moita: 0.42, porMoita: [2, 4], raioMoita: 0.22, folhas: [4, 7], altura: [0.12, 0.28], largura: 0.05, base: 0x5aa847, ponta: 0xb4ea86 } as const;
const cor = (hex: number) => new THREE.Color(hex);

export class Malha {
  readonly pos: number[] = [];
  readonly nor: number[] = [];
  readonly col: number[] = [];
  /** a pintura de cada vertice (o chao pintado do estilo digital, pintarTerreno): 0 nada, 1 a grama, 2 a pedra */
  readonly pin: number[] = [];
  marca = 0;
  /** um triangulo com a normal da face, virado para `fora` (o lado que tem que ficar de frente) */
  tri(a: THREE.Vector3, b: THREE.Vector3, c: THREE.Vector3, k: THREE.Color, fora: THREE.Vector3): void {
    const n = new THREE.Vector3().subVectors(b, a).cross(new THREE.Vector3().subVectors(c, a)).normalize();
    if (n.dot(fora) < 0) { [b, c] = [c, b]; n.negate(); }
    for (const v of [a, b, c]) { this.pos.push(v.x, v.y, v.z); this.nor.push(n.x, n.y, n.z); this.col.push(k.r, k.g, k.b); this.pin.push(this.marca); }
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
    g.setAttribute("aPinta", new THREE.Float32BufferAttribute(this.pin, 1));
    return g;
  }
}

/* as arestas da celula: [canto a, canto b, vizinho dx, dz, os cantos do vizinho na mesma ordem, a normal para fora] */
const ARESTAS = [
  { a: 0, b: 1, dx: 0, dz: -1, va: 3, vb: 2, n: new THREE.Vector3(0, 0, -1) },
  { a: 1, b: 2, dx: 1, dz: 0, va: 0, vb: 3, n: new THREE.Vector3(1, 0, 0) },
  { a: 2, b: 3, dx: 0, dz: 1, va: 1, vb: 0, n: new THREE.Vector3(0, 0, 1) },
  { a: 3, b: 0, dx: -1, dz: 0, va: 2, vb: 1, n: new THREE.Vector3(-1, 0, 0) },
] as const;
const CANTO_XZ: readonly (readonly [number, number])[] = [[0, 0], [1, 0], [1, 1], [0, 1]];
const FAIXA = 0.28;                       // a altura de uma faixa de estrato
const BORDA_GRAMA = 0.14;                 // a grama que desce pela borda do penhasco

/** o terreno da grade em degraus com faixas de estrato, nas cores da paleta */
export function terreno(ilha: Ilha, COR: PaletaTerreno = PALETA_ILHA): THREE.Mesh {
  const m = new Malha(), r = rng(5), cima = new THREE.Vector3(0, 1, 0);
  for (let j = 0; j < ilha.prof; j++) for (let i = 0; i < ilha.larg; i++) {
    const x = ilha.x0 + i, z = ilha.z0 + j, c = ilha.cel(x, z)!;
    const p = (k: number, h = c.cantos[k]) => new THREE.Vector3(x + CANTO_XZ[k][0], h, z + CANTO_XZ[k][1]);
    const paleta = c.tipo === "agua" ? COR.fundo : c.tipo === "grama" ? COR.grama[c.regiao] : COR[c.tipo];
    if (!paleta) throw new Error("regiao da ilha sem cor de grama: " + c.regiao);
    /* o sorteio sai sempre, para a rng andar igual; no chao pintado a grama fica na primeira cor da regiao (sem o xadrez) */
    const k = paleta[Math.floor(r() * paleta.length)], grama = COR.pintado && c.tipo === "grama";
    m.marca = grama ? 1 : 0;
    m.quad(p(0), p(1), p(2), p(3), cor(grama ? paleta[0] : k), cima);
    for (const e of ARESTAS) parede(m, ilha, c, x, z, e, COR);
  }
  const mat = toon({ vertexColors: true });
  return new THREE.Mesh(m.geometria(), COR.pintado ? pintarTerreno(mat) : mat);
}

/* a pintura do chao (D5; o cel shading do estilo digital, a maquete B): no fragmento, pelas coordenadas do mundo (antes da dobra):
   - a grama (aPinta 1): manchas grandes em tres tons chapados (um ruido de valor em degraus) e folhinhas desenhadas (um traco curto por
     sexto de celula, metade escuro e metade claro), que somem quando ficam menores que um pixel (fwidth);
   - a pedra (aPinta 2): placas em fileiras desencontradas, cada uma num tom, com a junta e algumas rachaduras no nanquim do contorno.
   Os numeros sao do desenho: PROPOSTO, SEM FONTE */
const GLSL_PINTA_VERT = "attribute float aPinta;\nvarying float vPinta;\nvarying vec3 vPPos;\nvarying vec3 vPNor;\n";
const GLSL_PINTA_FRAG = `varying float vPinta;
varying vec3 vPPos;
varying vec3 vPNor;
float pHash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float pValor(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(pHash(i), pHash(i + vec2(1.0, 0.0)), f.x), mix(pHash(i + vec2(0.0, 1.0)), pHash(i + vec2(1.0, 1.0)), f.x), f.y);
}
`;
const GLSL_PINTA = `
if (vPinta > 0.5 && vPinta < 1.5) {
  vec2 p = vPPos.xz;
  float n = pValor(p * 0.42) * 0.65 + pValor(p * 1.3 + 17.0) * 0.35;
  float tom = n > 0.6 ? 1.12 : (n < 0.4 ? 0.86 : 1.0);
  vec2 q = p * 6.0, id = floor(q), f = fract(q) - 0.5;
  float r = pHash(id);
  f += (vec2(pHash(id + 3.1), pHash(id + 7.7)) - 0.5) * 0.5;
  float lam = abs(f.x - f.y * (r - 0.5) * 0.9);
  float folha = (1.0 - smoothstep(0.03, 0.065, lam)) * (1.0 - smoothstep(0.17, 0.25, abs(f.y))) * step(0.3, r);
  folha *= 1.0 - smoothstep(0.18, 0.4, fwidth(q.x));
  diffuseColor.rgb *= tom * mix(1.0, r > 0.68 ? 1.22 : 0.7, folha);
} else if (vPinta > 1.5) {
  vec3 nn = normalize(vPNor);
  float u = abs(nn.x) > abs(nn.z) ? vPPos.z : vPPos.x, v = vPPos.y;
  float H = 0.7, fila = floor(v / H);
  float uu = u + pHash(vec2(fila, 3.0)) * 3.0, W = 1.3 + 0.9 * pHash(vec2(fila, 9.0)), col = floor(uu / W);
  vec2 f = vec2(fract(uu / W) * W, fract(v / H) * H);
  float bd = min(min(f.x, W - f.x), min(f.y, H - f.y));
  float w = max(fwidth(uu), fwidth(v)) * 1.1 + 0.012;
  float junta = 1.0 - smoothstep(w, w * 2.0, bd);
  float k = pHash(vec2(col, fila) + 5.3), rach = 0.0;
  if (k > 0.4) {
    float cx = W * (0.3 + 0.4 * pHash(vec2(col, fila) + 1.7));
    float dd = abs((f.x - cx) - (f.y - H * 0.5) * (k - 0.75) * 3.0);
    rach = (1.0 - smoothstep(w * 0.7, w * 1.5, dd)) * step(abs(f.y - H * 0.5), H * 0.36);
  }
  diffuseColor.rgb *= (0.86 + 0.22 * pHash(vec2(col, fila))) * (1.0 + 0.1 * smoothstep(H * 0.72, H * 0.95, f.y));
  diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.106, 0.165, 0.2), max(junta, rach) * 0.8);
}
`;
/** liga a pintura do chao (GLSL_PINTA) num material toon ja curvado (toon), por cima da dobra */
export function pintarTerreno(m: THREE.MeshToonMaterial): THREE.MeshToonMaterial {
  const antes = m.onBeforeCompile.bind(m), chave = m.customProgramCacheKey.bind(m);
  m.onBeforeCompile = (s, r) => {
    antes(s, r);
    s.vertexShader = GLSL_PINTA_VERT + s.vertexShader.replace("#include <begin_vertex>", "#include <begin_vertex>\nvPinta = aPinta; vPPos = position; vPNor = normal;");
    s.fragmentShader = GLSL_PINTA_FRAG + s.fragmentShader.replace("#include <color_fragment>", "#include <color_fragment>" + GLSL_PINTA);
  };
  m.customProgramCacheKey = () => chave() + "-pinta";
  return m;
}

/** as florzinhas da grama (FLORES): discos de seis triangulos rente ao chao, so nas celulas de grama planas, por uma rng propria (o chao
    sai sempre igual); uma malha so, um desenho so */
export function flores(ilha: Ilha): THREE.Mesh {
  const m = new Malha(), r = rng(31), cima = new THREE.Vector3(0, 1, 0), R = FLORES.raio;
  for (let j = 0; j < ilha.prof; j++) for (let i = 0; i < ilha.larg; i++) {
    const x = ilha.x0 + i, z = ilha.z0 + j, c = ilha.cel(x, z)!;
    if (c.tipo !== "grama") continue;
    for (let n = Math.floor(FLORES.porCelula + r()); n > 0; n--) {
      const fx = x + 0.1 + r() * 0.8, fz = z + 0.1 + r() * 0.8, y = ilha.altura(fx, fz) + 0.012, k = cor(FLORES.cores[Math.floor(r() * FLORES.cores.length)]);
      const centro = new THREE.Vector3(fx, y, fz);
      for (let a = 0; a < 6; a++) {
        const p = (b: number) => new THREE.Vector3(fx + Math.cos((b * Math.PI) / 3) * R, y, fz + Math.sin((b * Math.PI) / 3) * R);
        m.tri(centro, p(a), p(a + 1), k, cima);
      }
    }
  }
  /* as manchas (D5): numa rng propria, para as florzinhas soltas sairem como antes */
  const rm = rng(37), M = FLORES.mancha, haste = cor(TUFOS.base);
  for (let j = 0; j < ilha.prof; j++) for (let i = 0; i < ilha.larg; i++) {
    const x = ilha.x0 + i, z = ilha.z0 + j, c = ilha.cel(x, z)!;
    if (c.tipo !== "grama" || rm() > M.chance) continue;
    const k = cor(M.cores[Math.floor(rm() * M.cores.length)]), n = M.flores[0] + Math.floor(rm() * (M.flores[1] - M.flores[0] + 1));
    for (let f = 0; f < n; f++) {
      const a = rm() * Math.PI * 2, d = Math.sqrt(rm()) * M.raio, fx = x + 0.5 + Math.cos(a) * d, fz = z + 0.5 + Math.sin(a) * d;
      const dono = ilha.cel(Math.floor(fx), Math.floor(fz));
      if (!dono || dono.tipo !== "grama") continue;
      const chao = ilha.altura(fx, fz), h = M.haste * (0.7 + rm() * 0.6), y = chao + h, Rf = M.tamanho * (0.8 + rm() * 0.4);
      /* a haste: um triangulo fino de pe; a flor: o disco de seis triangulos no alto */
      m.tri(new THREE.Vector3(fx - 0.012, chao, fz), new THREE.Vector3(fx + 0.012, chao, fz), new THREE.Vector3(fx, y, fz), haste, new THREE.Vector3(0, 0, 1));
      const centro = new THREE.Vector3(fx, y, fz);
      for (let b = 0; b < 6; b++) {
        const p = (e: number) => new THREE.Vector3(fx + Math.cos((e * Math.PI) / 3) * Rf, y, fz + Math.sin((e * Math.PI) / 3) * Rf);
        m.tri(centro, p(b), p(b + 1), k, cima);
      }
    }
  }
  const malha = new THREE.Mesh(m.geometria(), toon({ vertexColors: true, polygonOffset: true, polygonOffsetFactor: -1, side: THREE.DoubleSide, depthWrite: false }));
  malha.frustumCulled = false;
  return malha;
}

/** os tufos de grama do estilo digital (TUFOS; D5): folhas finas de pe, da base escura a ponta clara, inclinadas ao acaso, nas celulas de
    grama, por uma rng propria (o chao sai sempre igual). A normal e a do chao (a folha acende como a grama embaixo dela). Uma malha so, um
    desenho so */
export function tufos(ilha: Ilha): THREE.Mesh {
  const pos: number[] = [], nor: number[] = [], col: number[] = [], r = rng(41), base = cor(TUFOS.base), ponta = cor(TUFOS.ponta);
  const v = (x: number, y: number, z: number, k: THREE.Color) => { pos.push(x, y, z); nor.push(0, 1, 0); col.push(k.r, k.g, k.b); };
  for (let j = 0; j < ilha.prof; j++) for (let i = 0; i < ilha.larg; i++) {
    const x = ilha.x0 + i, z = ilha.z0 + j, c = ilha.cel(x, z)!;
    if (c.tipo !== "grama") continue;
    if (r() > TUFOS.moita) continue;
    const mx = x + 0.25 + r() * 0.5, mz = z + 0.25 + r() * 0.5;
    for (let t = TUFOS.porMoita[0] + Math.floor(r() * (TUFOS.porMoita[1] - TUFOS.porMoita[0] + 1)); t > 0; t--) {
      const tx = mx + (r() - 0.5) * 2 * TUFOS.raioMoita, tz = mz + (r() - 0.5) * 2 * TUFOS.raioMoita, chao = ilha.altura(tx, tz) - 0.01;
      const n = TUFOS.folhas[0] + Math.floor(r() * (TUFOS.folhas[1] - TUFOS.folhas[0] + 1)), giro = r() * Math.PI;
      for (let f = 0; f < n; f++) {
        const a = giro + (f / n) * Math.PI + (r() - 0.5) * 0.5, ca = Math.cos(a), sa = Math.sin(a), w = TUFOS.largura * (0.7 + r() * 0.6);
        const h = TUFOS.altura[0] + r() * (TUFOS.altura[1] - TUFOS.altura[0]), inc = (r() - 0.5) * 0.7 * h, ox = (r() - 0.5) * 0.08, oz = (r() - 0.5) * 0.08;
        const bx = tx + ox, bz = tz + oz;
        v(bx - ca * w, chao, bz - sa * w, base);
        v(bx + ca * w, chao, bz + sa * w, base);
        v(bx + sa * inc, chao + h, bz - ca * inc, ponta);
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  /* sem escrever a profundidade: o contorno (pos.ts) nao pega cada folha (viravam pontinhos de nanquim), e a folha continua atras do que
     esta na frente dela */
  const malha = new THREE.Mesh(g, toon({ vertexColors: true, side: THREE.DoubleSide, depthWrite: false }));
  malha.frustumCulled = false;
  return malha;
}

/* a parede de uma aresta: do tampo desta celula ate o do vizinho (ou ate o fundo, na borda da grade), em faixas */
function parede(m: Malha, ilha: Ilha, c: Celula, x: number, z: number, e: (typeof ARESTAS)[number], COR: PaletaTerreno): void {
  const viz = ilha.cel(x + e.dx, z + e.dz);
  const ta = c.cantos[e.a], tb = c.cantos[e.b];
  const ba = viz ? viz.cantos[e.va] : -1.6, bb = viz ? viz.cantos[e.vb] : -1.6;
  if (ta - ba < 1e-3 && tb - bb < 1e-3) return;
  const [ax, az] = CANTO_XZ[e.a], [bx, bz] = CANTO_XZ[e.b];
  const ponto = (cx: number, cz: number, h: number) => new THREE.Vector3(x + cx, h, z + cz);
  const alta = Math.max(ta - ba, tb - bb), n = Math.max(1, Math.round(alta / FAIXA));
  const grama = c.tipo === "grama" || c.tipo === "caminho", agua = c.tipo === "agua" || viz?.tipo === "agua";
  const paleta = c.tipo === "areia" ? COR.estratoAreia : agua && alta < 0.8 ? COR.margem : COR.estrato;
  const pedra = COR.pintado && paleta === COR.estrato ? 2 : 0;
  for (let i = 0; i < n; i++) {
    /* as faixas vao de cima para baixo; a de cima e a borda de grama */
    const f0 = i / n, f1 = (i + 1) / n, y = (t: number, f: number, b: number) => t - (t - b) * f;
    let k = cor(paleta[Math.floor(((ta + ba) / 2 - f0 * alta) / FAIXA + 100) % paleta.length]);
    let g0 = f0;
    if (i === 0 && grama && !agua) {
      const fg = Math.min(BORDA_GRAMA / alta, 0.5);
      m.marca = 0;
      m.quad(ponto(ax, az, y(ta, 0, ba)), ponto(bx, bz, y(tb, 0, bb)), ponto(bx, bz, y(tb, fg, bb)), ponto(ax, az, y(ta, fg, ba)), cor(COR.borda), e.n);
      g0 = fg;
      if (g0 >= f1) continue;
    }
    if (agua && alta < 0.8) k = cor(COR.margem[i % 2]);
    m.marca = pedra;
    m.quad(ponto(ax, az, y(ta, g0, ba)), ponto(bx, bz, y(tb, g0, bb)), ponto(bx, bz, y(tb, f1, bb)), ponto(ax, az, y(ta, f1, ba)), k, e.n);
  }
}

/* ---------- a agua ---------- */
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
uniform float uNoite;
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
  c *= mix(vec3(1.0), vec3(${NOITE.agua.toFixed(2)}, ${(NOITE.agua + 0.05).toFixed(2)}, ${(NOITE.agua + 0.2).toFixed(2)}), uNoite);
  gl_FragColor = vec4(c, 1.0);
  #include <colorspace_fragment>
  #include <fog_fragment>
}`;
const CACHOEIRA_FRAG = `
uniform float uTempo;
uniform float uNoite;
varying float vMargem;
varying vec2 vXZ;
#include <fog_pars_fragment>
void main() {
  float faixa = fract(vMargem * 2.5 - uTempo * 1.6 + sin(vXZ.x * 7.0) * 0.15);
  vec3 c = mix(vec3(0.55, 0.88, 0.97), vec3(0.95, 1.0, 1.0), smoothstep(0.55, 0.9, faixa));
  c *= mix(vec3(1.0), vec3(${NOITE.agua.toFixed(2)}, ${(NOITE.agua + 0.05).toFixed(2)}, ${(NOITE.agua + 0.2).toFixed(2)}), uNoite);
  gl_FragColor = vec4(c, 1.0);
  #include <colorspace_fragment>
  #include <fog_fragment>
}`;

function materialAgua(frag: string): THREE.ShaderMaterial {
  const mat = new THREE.ShaderMaterial({
    vertexShader: AGUA_VERT, fragmentShader: frag, fog: true, side: THREE.DoubleSide,
    uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {}]),
  });
  /* os uniforms da curva sao os mesmos objetos de CURVA (atualizar CURVA atualiza a agua) */
  Object.assign(mat.uniforms, CURVA);
  return mat;
}

function agua(ilha: Ilha): THREE.Group {
  const { larg, prof, x0, z0 } = ilha, idx = (x: number, z: number) => (z - z0) * larg + (x - x0);
  /* a distancia (em celulas) de cada celula de agua ate a terra, por busca em largura; vai nos cantos como a margem */
  const dist = new Float32Array(larg * prof).fill(99), fila: number[] = [];
  for (let i = 0; i < larg * prof; i++) if (ilha.celulas[i].tipo !== "agua") { dist[i] = 0; fila.push(i); }
  for (let q = 0; q < fila.length; q++) {
    const i = fila[q], x = i % larg, z = (i - x) / larg;
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx, nz = z + dz;
      if (nx < 0 || nz < 0 || nx >= larg || nz >= prof) continue;
      const j = nz * larg + nx;
      if (dist[j] > dist[i] + 1) { dist[j] = dist[i] + 1; fila.push(j); }
    }
  }
  const margemCanto = (cx: number, cz: number) => {
    let d = 99;
    for (const [dx, dz] of [[-1, -1], [0, -1], [-1, 0], [0, 0]]) {
      const x = cx + dx, z = cz + dz;
      d = Math.min(d, x < x0 || z < z0 || x >= x0 + larg || z >= z0 + prof ? 6 : dist[idx(x, z)]);
    }
    return Math.max(0, d - 0.5) + (d === 0 ? 0 : 0.5);
  };
  const pos: number[] = [], margem: number[] = [], cpos: number[] = [], cmar: number[] = [];
  const nivelAgua = (c: Celula) => Math.max(c.nivel, 0) * ALTURA_NIVEL + NIVEL_AGUA;
  for (let z = z0; z < z0 + prof; z++) for (let x = x0; x < x0 + larg; x++) {
    const c = ilha.cel(x, z)!;
    if (c.tipo !== "agua") continue;
    const y = nivelAgua(c);
    const v = (cx: number, cz: number) => { pos.push(x + cx, y, z + cz); margem.push(margemCanto(x + cx, z + cz)); };
    v(0, 0); v(0, 1); v(1, 1); v(0, 0); v(1, 1); v(1, 0);
    /* a cachoeira: a agua do plato que encontra a agua mais baixa ao sul */
    const sul = ilha.cel(x, z + 1);
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
    grupo.add(Object.assign(new THREE.Mesh(g, materialAgua(frag)), { frustumCulled: false }));
  };
  malha(pos, margem, AGUA_FRAG);
  if (cpos.length) malha(cpos, cmar, CACHOEIRA_FRAG);
  /* o mar continua alem da grade, ate o horizonte do sul */
  const mar = new THREE.PlaneGeometry(larg + 160, 80).rotateX(-Math.PI / 2).translate(x0 + larg / 2, NIVEL_AGUA - 0.01, z0 + prof + 40);
  mar.setAttribute("aMargem", new THREE.Float32BufferAttribute(new Array(mar.attributes.position.count).fill(6), 1));
  grupo.add(Object.assign(new THREE.Mesh(mar, materialAgua(AGUA_FRAG)), { frustumCulled: false }));
  return grupo;
}

/* ---------- as sombras redondas ---------- */
const TEX_SOMBRA = (() => {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const gr = g.createRadialGradient(32, 32, 4, 32, 32, 31);
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
/** as pecas de uma variante; `nome` e o do no do glTF, quando o carregador da (os itens gerados separam as pecas que se mexem pelo nome) */
export interface Variante { pecas: { nome?: string; geo: THREE.BufferGeometry; mat: THREE.Material; local: THREE.Matrix4 }[] }

export async function carregarVariante(loader: GLTFLoader, url: string, modelo: Modelo): Promise<Variante> {
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
    pecas.push({ nome: mesh.name, geo: mesh.geometry, mat, local: norm.clone().multiply(mesh.matrixWorld) });
  });
  return { pecas };
}

/** os objetos da ilha prontos: o grupo e as malhas da grama (a queda de qualidade tira metade delas); `noite`, o que muda a noite
    (os postes acesos, enfeites.ts); `quadro`, o que segue a camera a cada quadro (o foco, a dobra e a direcao dela, a meia largura visivel por unidade de distancia; a lata do estilo
    digital, digital.ts) */
export interface Objetos {
  grupo: THREE.Group; grama: THREE.InstancedMesh[]; noite?: (noite: boolean) => void;
  quadro?: (foco: readonly [number, number], dobra: number, dir: readonly [number, number], meiaLargura: number) => void;
  /** os lugares da ilha (lugaresCena.ts), nos estilos que os tem: a caixa de cada um, para o toque */
  lugares?: Map<NomeLugar, THREE.Box3>;
  /** o grupo do modelo de cada lugar (lugaresCena.ts): a vista apaga o lugar trancado pelo nivel do Tamer (marcadoresLugar.ts, Apagador) e tira o
      marcador provisorio dos que tem modelo */
  lugaresRaiz?: Map<NomeLugar, THREE.Group>;
  /** acende (aberto) ou apaga (trancado) a mascara de luz de um lugar (lugaresCena.ts) */
  abrirLugar?: (nome: NomeLugar, aberto: boolean) => void;
}

/** carrega uma variante de um modelo da grade (o arquivo, o modelo da grade e a linha da tabela MODELOS) */
export type Carregador = (arquivo: string, id: NomeModelo, modelo: Modelo) => Promise<Variante>;

/** carrega os modelos e poe os objetos da grade como instancias; falha alto se um arquivo nao carrega. Sem `carregar`, os kits CC0 da
 *  ilha (public/kits3d, MODELOS); os outros estilos do habitat (estilos.ts) dao o carregador e os arquivos deles */
export async function objetos(ilha: Ilha, base: string, carregar?: Carregador, arquivosDe: (id: NomeModelo) => readonly string[] = id => MODELOS[id].arquivos,
  girar = true): Promise<Objetos> {
  const gltf = new GLTFLoader(), usados = new Set(ilha.objetos.map(o => o.modelo));
  const carregador: Carregador = carregar ?? ((arq, _id, modelo) => carregarVariante(gltf, new URL("kits3d/" + arq, base).href, modelo));
  const variantes = new Map<NomeModelo, Variante[]>();
  await Promise.all([...usados].flatMap(id => arquivosDe(id).map(async (arq, i) => {
    const v = await carregador(arq, id, MODELOS[id]);
    if (!variantes.has(id)) variantes.set(id, []);
    variantes.get(id)![i] = v;
  })));
  /* agrupa os objetos por (modelo, variante) e monta um InstancedMesh por peca */
  const grupos = new Map<string, Objeto[]>();
  ilha.objetos.forEach((o, i) => {
    /* a clareira de um lugar (lugares.ts): o objeto nao entra, e os outros mantem a variante (pelo indice de antes) */
    if (ilha.escondidos.has(i)) return;
    const k = `${o.modelo}|${i % arquivosDe(o.modelo).length}`;
    if (!grupos.has(k)) grupos.set(k, []);
    grupos.get(k)!.push(o);
  });
  const grupo = new THREE.Group(), grama: THREE.InstancedMesh[] = [], sombras: { x: number; z: number; r: number }[] = [];
  for (const [k, lista] of grupos) {
    const [id, j] = k.split("|") as [NomeModelo, string], v = variantes.get(id)![Number(j)];
    const lugar = lista.map(o => new THREE.Matrix4().compose(
      new THREE.Vector3(o.x, ilha.altura(o.x, o.z), o.z),
      /* sem girar: os recortes em pe (o estilo Cassette) ficam virados para a camera */
      new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), girar ? o.giro : 0),
      new THREE.Vector3(o.escala, o.escala, o.escala)));
    for (const p of v.pecas) {
      const im = new THREE.InstancedMesh(p.geo, p.mat, lista.length);
      lugar.forEach((m, i) => im.setMatrixAt(i, m.clone().multiply(p.local)));
      im.frustumCulled = false;     // a dobra muda onde a peca aparece; o volume do three nao sabe disso
      grupo.add(im);
      if (id === "grama" || id === "grama_alta") grama.push(im);
    }
    if (MODELOS[id].sombra > 0) for (const o of lista) sombras.push({ x: o.x, z: o.z, r: MODELOS[id].sombra * o.escala });
  }
  if (sombras.length) {
    const somb = new THREE.InstancedMesh(GEO_SOMBRA, materialSombra(), sombras.length);
    sombras.forEach((s, i) => somb.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(s.x, ilha.altura(s.x, s.z) + 0.02, s.z),
      new THREE.Quaternion(), new THREE.Vector3(s.r * 2, 1, s.r * 2))));
    somb.frustumCulled = false;
    somb.renderOrder = 1;
    grupo.add(somb);
  }
  return { grupo, grama };
}

/* ---------- o ceu ---------- */
export function ceu(cores: readonly string[]): THREE.Texture {
  const c = document.createElement("canvas");
  c.width = 4; c.height = 256;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, cores[0]); gr.addColorStop(0.55, cores[1]); gr.addColorStop(1, cores[2]);
  g.fillStyle = gr;
  g.fillRect(0, 0, 4, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** um ceu pintado (a textura com userData.cobrir) cobrindo a tela sem esticar: corta os lados numa tela mais estreita que a imagem (o
    celular em pe) e a parte de baixo numa mais larga, mantendo o alto do ceu; o degrade (sem cobrir) fica como esta */
export function cobrirFundo(fundo: THREE.Color | THREE.Texture | null, aspecto: number): void {
  const t = fundo as THREE.Texture | null;
  if (!t?.isTexture || !t.userData.cobrir) return;
  const img = t.image as { width?: number; height?: number } | undefined;
  if (!img?.width || !img.height) return;
  const ai = img.width / img.height;
  if (aspecto < ai) { t.repeat.set(aspecto / ai, 1); t.offset.set((1 - aspecto / ai) / 2, 0); }
  else { const r = ai / aspecto; t.repeat.set(1, r); t.offset.set(0, 1 - r); }
}

/* as nuvens: planos brancos e fofos bem longe, ao norte, que nao dobram (ficam no ceu) */
function nuvens(ilha: Ilha): THREE.Group {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 128;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  g.fillStyle = "#ffffff";
  for (const [x, y, r] of [[70, 80, 38], [120, 60, 50], [175, 78, 40], [100, 92, 34], [150, 95, 30]]) { g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill(); }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const grupo = new THREE.Group(), r = rng(9);
  for (let i = 0; i < 12; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, fog: false, depthWrite: false, opacity: DIA.nuvens }));
    const w = 30 + r() * 30;
    s.scale.set(w, w / 2, 1);
    s.position.set(ilha.x0 - 40 + r() * (ilha.larg + 80), 26 + r() * 16, ilha.z0 - 70 - r() * 30);
    grupo.add(s);
  }
  return grupo;
}

/** as nuvens de anime do estilo digital (D5; os cumulos grandes da maquete B): o desenho num canvas (os circulos com o contorno de nanquim
    por fora, a sombra azulada embaixo e o branco em cima) e quantas, de que largura e onde (celulas; atras da mata do norte, sem nevoa).
    PROPOSTO, SEM FONTE */
const NUVENS_ANIME = { n: 6, largura: [32, 50], altura: [19, 28], longe: [24, 40], tinta: "#1b2a33", sombra: "#c9d9ee" } as const;
function nuvensAnime(ilha: Ilha): THREE.Group {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 256;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const bolas: [number, number, number][] = [[140, 170, 62], [215, 125, 82], [300, 108, 70], [370, 150, 60], [255, 182, 58], [90, 196, 40], [420, 192, 42]];
  const pintar = (cor: string, mais: number, dy: number) => {
    g.fillStyle = cor;
    for (const [x, y, r] of bolas) { g.beginPath(); g.arc(x, y + dy, r + mais, 0, Math.PI * 2); g.fill(); }
  };
  pintar(NUVENS_ANIME.tinta, 5, 0);
  pintar(NUVENS_ANIME.sombra, 0, 0);
  g.save(); g.beginPath();
  for (const [x, y, r] of bolas) { g.moveTo(x + r, y); g.arc(x, y, r, 0, Math.PI * 2); }
  g.clip();
  pintar("#ffffff", -4, -14);
  g.restore();
  /* o chao da nuvem reto, como a base de um cumulo */
  g.globalCompositeOperation = "destination-out";
  g.fillRect(0, 232, c.width, c.height - 232);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  /* todas num desenho so (D-G1): uma malha de quadros de pe, virados para o sul (a camera do habitat olha para o norte; nao seguem a
     camera livre, como um painel de fundo). A noite apaga como as outras nuvens (aplicarNoite muda a opacidade do material) */
  const r = rng(13), N = NUVENS_ANIME, pos: number[] = [], uv: number[] = [], idx: number[] = [];
  for (let i = 0; i < N.n; i++) {
    const w = N.largura[0] + r() * (N.largura[1] - N.largura[0]), h = w / 2;
    const x = ilha.x0 + ((i + 0.2 + r() * 0.6) / N.n) * ilha.larg, y = N.altura[0] + r() * (N.altura[1] - N.altura[0]);
    const z = ilha.z0 - N.longe[0] - r() * (N.longe[1] - N.longe[0]), b = i * 4;
    pos.push(x - w / 2, y - h / 2, z, x + w / 2, y - h / 2, z, x + w / 2, y + h / 2, z, x - w / 2, y + h / 2, z);
    uv.push(0, 0, 1, 0, 1, 1, 0, 1);
    idx.push(b, b + 1, b + 2, b, b + 2, b + 3);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  geo.setIndex(idx);
  const malha = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: tex, fog: false, depthWrite: false, transparent: true, opacity: DIA.nuvens }));
  malha.frustumCulled = false;
  return new THREE.Group().add(malha);
}

/** as nuvens em pixel do ceu sem pintura (CEU_SEM_PINTURA, 2026-11-08): cada nuvem e uma grade pequena (px) de bolhas sorteadas, so branco em cima
    e a sombra embaixo, ampliada sem filtro; quadros de pe atras da mata do norte, como as de anime, sem nevoa */
function nuvensPixel(ilha: Ilha): THREE.Group {
  const N = CEU_SEM_PINTURA.nuvens, [pw, ph] = N.px, r = rng(17), grupo = new THREE.Group();
  for (let i = 0; i < N.n; i++) {
    const c = document.createElement("canvas");
    c.width = pw; c.height = ph;
    const g = c.getContext("2d");
    if (!g) throw new Error("canvas 2d indisponível");
    /* as bolhas lado a lado, com a base reta; depois o alfa vira 0 ou 1 (bordas em degrau) */
    const bolhas = 3 + Math.floor(r() * 3);
    g.fillStyle = "#ffffff";
    for (let k = 0; k < bolhas; k++) {
      const x = pw * (0.2 + 0.6 * (k + 0.5) / bolhas) + (r() - 0.5) * 3, raio = ph * (0.32 + r() * 0.22);
      g.beginPath(); g.arc(x, ph - raio * 0.9, raio, 0, Math.PI * 2); g.fill();
    }
    const img = g.getImageData(0, 0, pw, ph), d = img.data, sombra = new THREE.Color(N.sombra);
    for (let y = 0; y < ph; y++) for (let x = 0; x < pw; x++) {
      const k = (y * pw + x) * 4, cheio = d[k + 3] > 110 && y < ph - 1;
      const embaixo = cheio && (y >= ph - 3 || d[((y + 2) * pw + x) * 4 + 3] <= 110);
      d[k] = embaixo ? Math.round(sombra.r * 255) : 255; d[k + 1] = embaixo ? Math.round(sombra.g * 255) : 255;
      d[k + 2] = embaixo ? Math.round(sombra.b * 255) : 255; d[k + 3] = cheio ? 255 : 0;
    }
    g.putImageData(img, 0, 0);
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace; tex.magFilter = THREE.NearestFilter; tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false;
    const w = N.largura[0] + r() * (N.largura[1] - N.largura[0]), h = w * ph / pw;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, fog: false, depthWrite: false, transparent: true, opacity: DIA.nuvens }));
    m.position.set(ilha.x0 + ((i + 0.15 + r() * 0.7) / N.n) * ilha.larg, N.altura[0] + r() * (N.altura[1] - N.altura[0]),
      ilha.z0 - N.longe[0] - r() * (N.longe[1] - N.longe[0]));
    m.frustumCulled = false;
    grupo.add(m);
  }
  return grupo;
}

/** a cena estatica da ilha: o ceu, a nevoa, as luzes, o terreno, a agua e as nuvens (os objetos, o pet e os itens entram depois) */
export interface CenaIlha { cena: THREE.Scene; aplicarNoite(noite: boolean): void }
/** `chao`: o terreno do estilo (o da ilha, se nada vier); `agua`: false tira a agua por celula e o mar (o estilo desenha a dele);
    `ceuDia`, um ceu pintado no lugar do degrade do dia, com a cor do horizonte (a nevoa) dele; `chaoHemi`, a cor de baixo da luz do ceu
    de dia (o estilo digital a puxa para o azul, a sombra azulada do anime); `nevoa`, o comeco e o fim da nevoa (celulas) */
export function montarCena(ilha: Ilha, chao: THREE.Object3D = terreno(ilha),
  opcoes: { agua?: boolean; nuvens?: boolean | "anime" | "pixel"; ceuDia?: THREE.Texture; horizonteDia?: number; chaoHemi?: number; nevoa?: readonly [number, number] } = {}): CenaIlha {
  const cena = new THREE.Scene(), fundo = { dia: opcoes.ceuDia ?? ceu(DIA.ceu), noite: ceu(NOITE.ceu) };
  cena.fog = new THREE.Fog(DIA.horizonte, opcoes.nevoa?.[0] ?? 26, opcoes.nevoa?.[1] ?? 62);
  if (opcoes.nevoa) cena.userData.nevoa = opcoes.nevoa;    /* a vista recalcula a nevoa com a orbita a partir desta (vista.ts) */
  const hemi = new THREE.HemisphereLight(), sol = new THREE.DirectionalLight();
  sol.position.set(-0.6, 1, 0.75);
  const ceuNuvens = opcoes.nuvens === false ? new THREE.Group() : opcoes.nuvens === "anime" ? nuvensAnime(ilha) : opcoes.nuvens === "pixel" ? nuvensPixel(ilha) : nuvens(ilha);
  cena.add(hemi, sol, chao, ceuNuvens);
  if (opcoes.agua !== false) cena.add(agua(ilha));
  const aplicarNoite = (noite: boolean) => {
    const p = noite ? NOITE : DIA;
    cena.background = noite ? fundo.noite : fundo.dia;
    (cena.fog as THREE.Fog).color.setHex(!noite && opcoes.horizonteDia !== undefined ? opcoes.horizonteDia : p.horizonte);
    hemi.color.setHex(p.hemi[0]); hemi.groundColor.setHex(!noite && opcoes.chaoHemi !== undefined ? opcoes.chaoHemi : p.hemi[1]); hemi.intensity = p.hemi[2];
    sol.color.setHex(p.sol[0]); sol.intensity = p.sol[1];
    CURVA.uNoite.value = noite ? 1 : 0;
    for (const s of ceuNuvens.children) ((s as THREE.Sprite | THREE.Mesh).material as THREE.Material).opacity = p.nuvens;
  };
  aplicarNoite(false);
  return { cena, aplicarNoite };
}
