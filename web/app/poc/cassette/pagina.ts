/* A demo do mapa Plains1 do Cassette Beasts (poc/cassette.html), só para validar o visual: o mapa convertido pelas ferramentas locais
   (D:/Trab/digilab/extrair_cb: o .pck do jogo, as malhas do Godot e o GridMap em JSON) e o pet do atlas do UP andando nele. Os assets
   são do jogo do Matheus e ficam fora do repositório, em Assets/kits3d/cassette_beasts/, servidos só no dev; sem eles, a página avisa.
     - o GridMap: um InstancedMesh por (peça, superfície), na posição da célula com a base ortogonal da orientação (as 24 do Godot);
     - as árvores: o tronco em malha e as camadas de folhagem como sprites voltados para a câmera (o billboard do jogo), 8 px por unidade;
     - a grama e as flores soltas: sprites também;
     - o pós (pos.ts): GBA HD (o pixel do jogo), HD-2D ou neutro.
   Protótipo de vista, fora do jogo e do motor. Todos os números são do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { CURVA } from "../mapa_ac/cena.ts";
import { Heroi } from "../mapa_ac/heroi.ts";
import { Ovo } from "../mapa_ac/ovo.ts";
import { PRESETS, Pos } from "../mapa_ac/pos.ts";

const BASE = "./Assets/kits3d/cassette_beasts/";
const PARAMS = new URLSearchParams(location.search);
/* ?mapa=: Clareira (a do ovo, montada na floresta por extrair_cb/clareira_cb.mjs), EasthamWoods (seis pedaços da floresta do mundo
   aberto) ou Plains1 (o mapa de demonstração do jogo) */
const MAPA = PARAMS.get("mapa") ?? "Clareira";
const INICIO: Record<string, [number, number]> = { Plains1: [30, -58] };
const PIXEL_TAMANHO = 0.125;                            // o pixel_size dos sprites do jogo (unidades por pixel)
const ESCALA_PET = 2.6;                                 // o pet do atlas (34 px por célula do mapa_ac) na escala deste mundo
const VELOCIDADE = 7, CORRIDA = 12;                     // unidades por segundo
const SPRITE_PADRAO = "brasa_crianca_sereno";

interface Superficie { pos: number[]; nor: number[]; uv: number[]; ind: number[] | null; textura: string | null }
interface MapaCB {
  mapa: string; cs: [number, number, number]; celulas: [number, number, number, number, number][];
  itens: Record<string, { nome: string; t: number[]; superficies: Superficie[] }>;
  objetos: Record<string, { malhas: { t: number[]; superficies: Superficie[] }[]; sprites: { img: string; t: number[] }[];
    colisao?: { r?: number; caixa?: [number, number, number]; t: number[] }[] }>;
  postos: { obj: string; t: number[] }[];
  sprites: { img: string; t: number[] }[];
  ovo?: [number, number, number];
  inicio?: [number, number];
  aguas?: { tipo: string; t: number[]; tam: [number, number]; cores: { fundo: number[]; meio: number[]; espuma: number[] } }[];
}

/* ---------- a água ---------- */
/* o jeito do liquid_transparent.shader do jogo, simplificado: a cor do meio com manchas da do fundo, faixas de brilho que andam e
   tudo quantizado no pixel do mundo (pixel_size 0,125). Sem o mapa de profundidade, não há a espuma da margem nem a refração */
const AGUA_VERT = `
varying vec3 vMundo;
void main() {
  vec4 p = modelMatrix * vec4(position, 1.0);
  vMundo = p.xyz;
  gl_Position = projectionMatrix * viewMatrix * p;
}`;
const AGUA_FRAG = `
uniform vec3 uMeio, uFundo, uEspuma;
uniform float uTempo, uAlfa;
varying vec3 vMundo;
float ruido(vec2 p) { return sin(p.x * 1.3 + sin(p.y * 0.9 + uTempo * 0.4)) * sin(p.y * 1.1 + sin(p.x * 0.7 - uTempo * 0.3)); }
void main() {
  vec2 p = floor(vMundo.xz / 0.125) * 0.125;
  float n = ruido(p * 0.35);
  vec3 c = mix(uMeio, uFundo, smoothstep(0.2, 0.8, n));
  float faixa = sin((p.x * 0.5 + p.y * 1.0) * 1.7 - uTempo * 1.2) * sin(p.y * 0.8 + uTempo * 0.5 + n * 2.0);
  c = mix(c, uEspuma, step(0.86, faixa) * 0.85);
  gl_FragColor = vec4(c, uAlfa);
  #include <colorspace_fragment>
}`;
const aguaTempo = { value: 0 };
const cor3 = (c: number[]) => new THREE.Color().setRGB(c[0], c[1], c[2], THREE.SRGBColorSpace);

/* as 24 bases ortogonais do Godot 3 (Basis, por linhas), na ordem do índice de orientação do GridMap */
const BASES = [
  [1, 0, 0, 0, 1, 0, 0, 0, 1], [0, -1, 0, 1, 0, 0, 0, 0, 1], [-1, 0, 0, 0, -1, 0, 0, 0, 1], [0, 1, 0, -1, 0, 0, 0, 0, 1],
  [1, 0, 0, 0, 0, -1, 0, 1, 0], [0, 0, 1, 1, 0, 0, 0, 1, 0], [-1, 0, 0, 0, 0, 1, 0, 1, 0], [0, 0, -1, -1, 0, 0, 0, 1, 0],
  [1, 0, 0, 0, -1, 0, 0, 0, -1], [0, 1, 0, 1, 0, 0, 0, 0, -1], [-1, 0, 0, 0, 1, 0, 0, 0, -1], [0, -1, 0, -1, 0, 0, 0, 0, -1],
  [1, 0, 0, 0, 0, 1, 0, -1, 0], [0, 0, -1, 1, 0, 0, 0, -1, 0], [-1, 0, 0, 0, 0, -1, 0, -1, 0], [0, 0, 1, -1, 0, 0, 0, -1, 0],
  [0, 0, 1, 0, 1, 0, -1, 0, 0], [0, -1, 0, 0, 0, 1, -1, 0, 0], [0, 0, -1, 0, -1, 0, -1, 0, 0], [0, 1, 0, 0, 0, -1, -1, 0, 0],
  [0, 0, 1, 0, -1, 0, 1, 0, 0], [0, 1, 0, 0, 0, 1, 1, 0, 0], [0, 0, -1, 0, 1, 0, 1, 0, 0], [0, -1, 0, 0, 0, -1, 1, 0, 0],
];
/** uma Transform do Godot (base 3x3 por linhas + origem) como Matrix4 do three */
const matriz = (t: number[]) => new THREE.Matrix4().set(t[0], t[1], t[2], t[9], t[3], t[4], t[5], t[10], t[6], t[7], t[8], t[11], 0, 0, 0, 1);

const tela = document.getElementById("tela") as HTMLCanvasElement;
const estado = document.getElementById("estado")!;
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.info.autoReset = false;
const camera = new THREE.PerspectiveCamera(30, 1, 0.5, 400);
const cena = new THREE.Scene();
cena.background = new THREE.Color(0x8fd3ff);
/* a luz do jogo é quase chapada: a textura sai perto da cor dela, com a sombra das árvores por cima */
cena.add(new THREE.HemisphereLight(0xffffff, 0xb8c8b0, 0.7));
const sol = new THREE.DirectionalLight(0xfff6e6, 1.5);
sol.castShadow = true;
sol.shadow.mapSize.set(2048, 2048);
Object.assign(sol.shadow.camera, { left: -40, right: 40, top: 40, bottom: -40, near: 1, far: 160 });
sol.shadow.bias = -0.0008;
cena.add(sol, sol.target);
const pos = new Pos(renderer);
CURVA.uCurva.value = 0;                                 // o Heroi usa o material do mapa_ac; aqui o mundo não dobra

/* ---------- as texturas e as malhas ---------- */
const texturas = new Map<string, THREE.Texture>();
const prontas = new Map<string, Promise<void>>();
const loaderTex = new THREE.TextureLoader();
function textura(p: string): THREE.Texture {
  if (!texturas.has(p)) {
    let ok!: () => void;
    prontas.set(p, new Promise<void>(r => { ok = r; }));
    const t = loaderTex.load(BASE + p, () => ok(), undefined, () => console.error("textura não carregou:", p));
    t.magFilter = t.minFilter = THREE.NearestFilter;
    t.generateMipmaps = false;
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.flipY = false;                                    // o v do Godot cresce para baixo, como a imagem
    texturas.set(p, t);
  }
  return texturas.get(p)!;
}
function geometria(s: Superficie): THREE.BufferGeometry {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(s.pos, 3));
  if (s.nor.length) g.setAttribute("normal", new THREE.Float32BufferAttribute(s.nor, 3));
  if (s.uv.length) g.setAttribute("uv", new THREE.Float32BufferAttribute(s.uv, 2));
  if (s.ind) g.setIndex(s.ind);
  return g;
}
/* a textura também como emissão: a maior parte da cor sai chapada (o jeito do jogo) e a luz do sol só soma o relevo e a sombra */
const material = (s: Superficie) => {
  const map = s.textura ? textura(s.textura) : null;
  return new THREE.MeshLambertMaterial({ map, emissiveMap: map, emissive: map ? 0xffffff : 0x000000, emissiveIntensity: 0.62, alphaTest: 0.5, side: THREE.DoubleSide });
};

/** um sprite voltado para a câmera, com o centro na origem da transformação, 8 px por unidade como no jogo */
function sprite(img: string, m: THREE.Matrix4): THREE.Sprite {
  const t = textura(img);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, alphaTest: 0.5, transparent: false }));
  s.position.setFromMatrixPosition(m);
  void prontas.get(img)!.then(() => s.scale.set(t.image.width * PIXEL_TAMANHO, t.image.height * PIXEL_TAMANHO, 1));
  return s;
}

const terreno = new THREE.Group();
cena.add(terreno);
/* o que bloqueia o andar: cilindros (centro e raio no chão) e caixas (a inversa da transformação e as meias medidas), dos
   CollisionShape das cenas do jogo; e os retângulos de água */
const RAIO_PET = 0.7;
const circulos: { x: number; z: number; r: number }[] = [];
const caixas: { inv: THREE.Matrix4; ext: [number, number, number]; esc: number }[] = [];
const lagos: { inv: THREE.Matrix4; meia: [number, number]; y: number }[] = [];

function montar(m: MapaCB): void {
  const [cx, cy, cz] = m.cs;
  /* o GridMap */
  const porItem = new Map<number, THREE.Matrix4[]>();
  for (const [x, y, z, item, rot] of m.celulas) {
    const b = BASES[rot];
    if (!b) throw new Error(`orientação ${rot} fora das 24`);
    const lugar = new THREE.Matrix4().set(b[0], b[1], b[2], x * cx + cx / 2, b[3], b[4], b[5], y * cy + cy / 2, b[6], b[7], b[8], z * cz + cz / 2, 0, 0, 0, 1);
    if (!porItem.has(item)) porItem.set(item, []);
    porItem.get(item)!.push(lugar.multiply(matriz(m.itens[item].t)));
  }
  for (const [item, lugares] of porItem) for (const s of m.itens[item].superficies) {
    const im = new THREE.InstancedMesh(geometria(s), material(s), lugares.length);
    lugares.forEach((l, i) => im.setMatrixAt(i, l));
    im.receiveShadow = true;                          // o chão só recebe: com as faces dos dois lados, ele se sombreava inteiro
    im.computeBoundingSphere();
    terreno.add(im);
  }
  /* as árvores e os outros objetos */
  for (const p of m.postos) {
    const o = m.objetos[p.obj], base = matriz(p.t);
    for (const c of o.colisao ?? []) {
      const mc = base.clone().multiply(matriz(c.t));
      const esc = new THREE.Vector3().setFromMatrixColumn(mc, 0).length();
      if (c.r !== undefined) circulos.push({ x: mc.elements[12], z: mc.elements[14], r: c.r * esc });
      else if (c.caixa) caixas.push({ inv: mc.clone().invert(), ext: c.caixa, esc });
    }
    for (const mm of o.malhas) for (const s of mm.superficies) {
      const malha = new THREE.Mesh(geometria(s), material(s));
      malha.applyMatrix4(base.clone().multiply(matriz(mm.t)));
      malha.castShadow = malha.receiveShadow = true;
      cena.add(malha);
    }
    for (const sp of o.sprites) cena.add(sprite(sp.img, base.clone().multiply(matriz(sp.t))));
  }
  for (const sp of m.sprites) cena.add(sprite(sp.img, matriz(sp.t)));
  for (const a of m.aguas ?? []) {
    const mat = new THREE.ShaderMaterial({ vertexShader: AGUA_VERT, fragmentShader: AGUA_FRAG, transparent: true, depthWrite: false,
      uniforms: { uMeio: { value: cor3(a.cores.meio) }, uFundo: { value: cor3(a.cores.fundo ?? a.cores.meio) },
        uEspuma: { value: cor3(a.cores.espuma) }, uTempo: aguaTempo, uAlfa: { value: a.cores.meio[3] ?? 0.9 } } });
    const plano = new THREE.Mesh(new THREE.PlaneGeometry(a.tam[0], a.tam[1]).rotateX(-Math.PI / 2), mat);
    const mt = matriz(a.t);
    plano.applyMatrix4(mt);
    plano.renderOrder = 5;
    cena.add(plano);
    lagos.push({ inv: mt.clone().invert(), meia: [a.tam[0] / 2, a.tam[1] / 2], y: mt.elements[13] });
  }
  estado.textContent = `${m.mapa}: ${m.celulas.length} células, ${Object.keys(m.itens).length} peças, ${m.postos.length} árvores`;
}

/* ---------- o pet e o chão ---------- */
const heroi = new Heroi();
heroi.raiz.scale.setScalar(ESCALA_PET);
cena.add(heroi.raiz);
let px = 0, pz = 0, py = 0;
let assentar = false;
let ovo: Ovo | null = null;                                   // pôr o pet no chão no primeiro quadro depois de o mapa montar
const raio = new THREE.Raycaster();
/** se o pet cabe em (x, z) com o chão em h: fora dos cilindros e das caixas dos objetos e fora da água acima do chão */
function livre(x: number, z: number, h: number): boolean {
  if (circulos.some(c => (c.x - x) ** 2 + (c.z - z) ** 2 < (c.r + RAIO_PET) ** 2)) return false;
  const p = new THREE.Vector3();
  for (const b of caixas) {
    p.set(x, h + 0.5, z).applyMatrix4(b.inv);
    const folga = RAIO_PET / b.esc;
    if (Math.abs(p.x) < b.ext[0] + folga && Math.abs(p.z) < b.ext[2] + folga && Math.abs(p.y) < b.ext[1] + 2 / b.esc) return false;
  }
  for (const l of lagos) {
    p.set(x, l.y, z).applyMatrix4(l.inv);
    if (Math.abs(p.x) < l.meia[0] && Math.abs(p.z) < l.meia[1] && h < l.y - 0.05) return false;
  }
  return true;
}

/** a altura do chão em (x, z): o primeiro acerto do terreno descendo de cima */
function chao(x: number, z: number, perto: number): number | null {
  raio.set(new THREE.Vector3(x, perto + 3, z), new THREE.Vector3(0, -1, 0));
  raio.far = 160;                                       // do alto (o assentar começa em 83) até bem abaixo do chão
  const h = raio.intersectObject(terreno, true)[0];
  return h ? h.point.y : null;
}

/* o atlas carrega junto com o mapa (ele é grande); o pet troca de sprite quando ele chegar */
void Heroi.listar().then(fonte => {
  if (fonte) heroi.usarSprite(fonte, fonte.atlas.sprites[SPRITE_PADRAO] ? SPRITE_PADRAO : Object.keys(fonte.atlas.sprites)[0]);
});

(async () => {
  const r = await fetch(BASE + `json/mapas/${MAPA}.json`);
  if (!r.ok) { estado.textContent = "sem os assets do Cassette Beasts nesta máquina (ver extrair_cb)"; return; }
  const m = await r.json() as MapaCB;
  montar(m);
  if (m.ovo) {
    ovo = new Ovo(m.ovo[0], m.ovo[1], m.ovo[2]); ovo.raiz.scale.setScalar(ESCALA_PET); cena.add(ovo.raiz);
    circulos.push({ x: m.ovo[0], z: m.ovo[2], r: 0.36 * ESCALA_PET });   // o RAIO do ovo.ts, na escala do mundo
  }
  /* o início: um ponto escolhido olhando a vista (a trilha do Plains1) ou o centro das árvores; ?x=&z= troca */
  const centro: [number, number] = m.inicio ?? INICIO[MAPA] ?? [m.postos.reduce((a, p) => a + p.t[9], 0) / m.postos.length, m.postos.reduce((a, p) => a + p.t[11], 0) / m.postos.length];
  px = Number(PARAMS.get("x") ?? centro[0]); pz = Number(PARAMS.get("z") ?? centro[1]);
  assentar = true;
})();

/* ---------- o painel ---------- */
const selVisual = document.getElementById("visual") as HTMLSelectElement;
function usarVisual(nome: string): void { pos.ajuste = { ...(PRESETS[nome] ?? PRESETS.neutro) }; selVisual.value = nome; }
usarVisual(PARAMS.get("visual") ?? "gba-hd");
selVisual.addEventListener("change", () => usarVisual(selVisual.value));
(document.getElementById("mapa") as HTMLSelectElement).value = MAPA;
/* para conferir no console: levar o pet a um ponto e, com a página em segundo plano (sem requestAnimationFrame), desenhar quadros à mão */
(window as unknown as { cb: object }).cb = { cena, heroi, pos, livre, colisoes: () => ({ circulos: circulos.length, caixas: caixas.length, lagos: lagos.length }), ir: (x: number, z: number) => { px = x; pz = z; py = chao(x, z, 80) ?? py; },
  passo: (n = 1) => { for (let i = 0; i < n; i++) quadro(antes + 1000 / 30, false); }, orbita: () => ORBITA };

/* ---------- a entrada: WASD/setas, Shift corre; arrastar gira a câmera, a roda aproxima ---------- */
const teclas = new Set<string>();
addEventListener("keydown", e => { teclas.add(e.code); if (e.code.startsWith("Arrow")) e.preventDefault(); });
addEventListener("keyup", e => teclas.delete(e.code));
addEventListener("blur", () => teclas.clear());
const ORBITA = { giro: 0, inclina: 0.72, dist: 34 };
let arrasto: { x: number; y: number } | null = null;
tela.addEventListener("pointerdown", e => { tela.setPointerCapture(e.pointerId); arrasto = { x: e.clientX, y: e.clientY }; });
tela.addEventListener("pointermove", e => {
  if (!arrasto) return;
  ORBITA.giro -= (e.clientX - arrasto.x) * 0.008;
  ORBITA.inclina = Math.min(1.35, Math.max(0.2, ORBITA.inclina + (e.clientY - arrasto.y) * 0.008));
  arrasto = { x: e.clientX, y: e.clientY };
});
tela.addEventListener("pointerup", () => { arrasto = null; });
tela.addEventListener("wheel", e => { e.preventDefault(); ORBITA.dist = Math.min(120, Math.max(8, ORBITA.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });

/* ---------- o laço ---------- */
const alvoCam = new THREE.Vector3();
let antes = performance.now(), quadros = 0, tFps = antes;
const fps = document.getElementById("fps")!;
function quadro(agora: number, seguir = true): void {
  const dt = Math.min(0.05, (agora - antes) / 1000);
  antes = agora;
  let x = 0, z = 0;
  if (teclas.has("KeyA") || teclas.has("ArrowLeft")) x -= 1;
  if (teclas.has("KeyD") || teclas.has("ArrowRight")) x += 1;
  if (teclas.has("KeyW") || teclas.has("ArrowUp")) z -= 1;
  if (teclas.has("KeyS") || teclas.has("ArrowDown")) z += 1;
  const correr = teclas.has("ShiftLeft") || teclas.has("ShiftRight");
  if (assentar) { const h = chao(px, pz, 80); if (h !== null) { py = h; assentar = false; alvoCam.set(px, py, pz); } }
  const n = Math.hypot(x, z), andando = n > 0;
  if (andando) {
    const c = Math.cos(ORBITA.giro), s = Math.sin(ORBITA.giro), v = (correr ? CORRIDA : VELOCIDADE) * dt;
    const dx = ((x * c + z * s) / n) * v, dz = ((-x * s + z * c) / n) * v;
    /* sobe degrau baixo e rampa; parede alta, objeto e água seguram; tenta x e z separados para deslizar na borda */
    const tentar = (ax: number, az: number) => {
      const hh = chao(px + ax, pz + az, py);
      if (hh === null || hh - py >= 1.1 || !livre(px + ax, pz + az, hh)) return false;
      px += ax; pz += az; py = hh;
      return true;
    };
    if (!tentar(dx, dz)) { tentar(dx, 0); tentar(0, dz); }
  }
  heroi.atualizar(px, py, pz, x, andando, agora, dt, correr);
  ovo?.atualizar(agora);
  aguaTempo.value = agora / 1000;
  alvoCam.lerp(new THREE.Vector3(px, py, pz), 1 - Math.exp(-dt * 6));
  const c = Math.cos(ORBITA.giro), s = Math.sin(ORBITA.giro), ch = Math.cos(ORBITA.inclina) * ORBITA.dist;
  camera.position.set(alvoCam.x + s * ch, alvoCam.y + Math.sin(ORBITA.inclina) * ORBITA.dist, alvoCam.z + c * ch);
  camera.lookAt(alvoCam.x, alvoCam.y + 1.5, alvoCam.z);
  sol.position.set(alvoCam.x - 30, alvoCam.y + 60, alvoCam.z + 25);
  sol.target.position.copy(alvoCam);
  const w = tela.clientWidth, h = tela.clientHeight;
  if (tela.width !== Math.round(w * renderer.getPixelRatio()) || tela.height !== Math.round(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  renderer.info.reset();
  pos.desenhar(cena, camera);
  quadros++;
  if (agora - tFps > 1000) { fps.textContent = `${Math.round((quadros * 1000) / (agora - tFps))} fps · ${renderer.info.render.calls} draw calls`; quadros = 0; tFps = agora; }
  if (seguir) requestAnimationFrame(t => quadro(t));
}
requestAnimationFrame(t => quadro(t));
