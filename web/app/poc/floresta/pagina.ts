/* A ilha da floresta (poc/floresta.html): um mapa 3D montado só com as peças do kit RPG Tiny Fantasy Forest PBR (Dungeon Mason, Unity
   Asset Store EULA, fora do repositório em Assets/kits3d/tiny_fantasy_forest/), na ordem do manual do kit: a massa de terra, os platôs,
   as manchas do chão, a estrada e o rio, as pedras e montanhas, as construções e, por fim, árvores, capim e flores. O Digimon em sprite 2D
   anda por cima, com a altura tirada do chão por um raio. Protótipo de vista, fora do jogo e do motor.
   O kit está em centímetros; aqui, 1 unidade = 1 metro. Todos os números de posição são do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { FBXLoader } from "three/examples/jsm/loaders/FBXLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { COR_HORIZONTE, CURVA, ceu } from "../mapa_ac/cena.ts";
import { Heroi } from "../mapa_ac/heroi.ts";
import { rng } from "../mapa_ac/mapa.ts";

CURVA.uCurva.value = 0;                                  // o personagem do mapa_ac sem a dobra do mundo

const TFF = "./Assets/kits3d/tiny_fantasy_forest/x/Assets/RPG Tiny Fantasy Forest PBR/";
const CM = 0.01;                                         // o kit em centímetros, a cena em metros
const VELOCIDADE = 3.4, CORRIDA = 7;                     // metros por segundo
const RAIO_ILHA = 46;                                    // até onde o personagem anda
const SPRITE_PADRAO = "brasa_crianca_sereno";

const tela = document.getElementById("tela") as HTMLCanvasElement;
const estado = document.getElementById("estado")!;
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 600);
camera.position.set(0, 38, 62);

const cena = new THREE.Scene();
cena.background = ceu();
cena.fog = new THREE.Fog(COR_HORIZONTE, 120, 320);
cena.add(new THREE.HemisphereLight(0xeaf6ff, 0x6f9a4e, 1.3));
const sol = new THREE.DirectionalLight(0xffe9c8, 3.0);
sol.position.set(-40, 70, 30);
sol.castShadow = true;
sol.shadow.mapSize.set(4096, 4096);
Object.assign(sol.shadow.camera, { left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 200 });
sol.shadow.bias = -0.0004;
sol.shadow.normalBias = 0.03;
cena.add(sol);

/* ---------- os materiais ---------- */
/* o kit pinta tudo com uma paleta só (o "Base Map", quadrados de cor), com o brilho e a emissão em mapas do mesmo desenho; a água dos rios
   e da cachoeira é o segundo material, sem textura. As texturas são lidas sem filtro: filtrar misturaria os quadrados vizinhos. */
function texKit(arquivo: string, cor: boolean): THREE.Texture {
  const t = new THREE.TextureLoader().load(TFF + "Texture/" + arquivo);
  if (cor) t.colorSpace = THREE.SRGBColorSpace;
  t.magFilter = t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  return t;
}
const BASE = texKit("Base Map.png", true);
const EMISSAO = texKit("Emission Map.png", true);
/* o "Metallic Map" do Unity guarda o metal no R e a lisura no alfa; o three lê a rugosidade no G e o metal no B: refaz o mapa num canvas
   (até carregar, rugosidade 0,85 e metal 0, o material de antes) */
const BRILHO = (() => {
  const c = document.createElement("canvas");
  c.width = c.height = 512;
  const g = c.getContext("2d")!;
  g.fillStyle = "rgb(0,217,0)"; g.fillRect(0, 0, 512, 512);
  const t = new THREE.CanvasTexture(c);
  t.magFilter = t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  const img = new Image();
  img.onload = () => {
    const tmp = document.createElement("canvas");
    tmp.width = tmp.height = 512;
    const gt = tmp.getContext("2d", { willReadFrequently: true })!;
    gt.drawImage(img, 0, 0, 512, 512);
    const src = gt.getImageData(0, 0, 512, 512).data, dst = g.createImageData(512, 512);
    for (let k = 0; k < src.length; k += 4) { dst.data[k] = 0; dst.data[k + 1] = 255 - src[k + 3]; dst.data[k + 2] = src[k]; dst.data[k + 3] = 255; }
    g.putImageData(dst, 0, 0);
    t.needsUpdate = true;
  };
  img.src = TFF + "Texture/Metallic Map.png";
  return t;
})();
const MAT_AGUA = new THREE.MeshStandardMaterial({ color: 0x3aa0e8, roughness: 0.1, metalness: 0, transparent: true, opacity: 0.85 });

/* os estilos do kit: "kit" é a peça parada; "arvore" e "grama" ganham o degradê de baixo para cima (a base na sombra da própria copa, o
   que o Unity do kit tira da oclusão e da luz do céu) e o vento no topo */
type Estilo = "kit" | "arvore" | "grama";
const TEMPO = { value: 0 };
const ESTILOS: Record<Estilo, { altura: number; baixo: number; vento: number } | null> = {
  kit: null,
  arvore: { altura: 335, baixo: 0.55, vento: 0.00002 },     // a Tree02 tem 335 cm
  grama: { altura: 46, baixo: 0.5, vento: 0.0012 },         // o Grass01 tem 46 cm
};
const materiais = new Map<Estilo, THREE.MeshStandardMaterial>();
function materialKit(estilo: Estilo): THREE.MeshStandardMaterial {
  if (materiais.has(estilo)) return materiais.get(estilo)!;
  const m = new THREE.MeshStandardMaterial({ map: BASE, roughnessMap: BRILHO, metalnessMap: BRILHO, roughness: 1, metalness: 1,
    emissiveMap: EMISSAO, emissive: 0xffffff, emissiveIntensity: 1.2 });
  const e = ESTILOS[estilo];
  if (e) {
    m.onBeforeCompile = s => {
      s.uniforms.uTempo = TEMPO;
      s.vertexShader = "uniform float uTempo;\nvarying float vAlturaKit;\n" + s.vertexShader.replace("#include <begin_vertex>", `#include <begin_vertex>
  vAlturaKit = clamp(position.y / ${e.altura.toFixed(1)}, 0.0, 1.0);
  #ifdef USE_INSTANCING
    vec3 baseV = instanceMatrix[3].xyz;
  #else
    vec3 baseV = vec3(0.0);
  #endif
  float alto = max(transformed.y, 0.0);
  transformed.x += sin(uTempo * 1.8 + baseV.x * 0.4 + baseV.z * 0.3) * ${e.vento.toFixed(6)} * alto * alto;
  transformed.z += cos(uTempo * 1.4 + baseV.x * 0.3) * ${(e.vento * 0.7).toFixed(6)} * alto * alto;`);
      s.fragmentShader = "varying float vAlturaKit;\n" + s.fragmentShader.replace("#include <map_fragment>",
        `#include <map_fragment>\n  diffuseColor.rgb *= mix(${e.baixo.toFixed(2)}, 1.06, smoothstep(0.0, 1.0, vAlturaKit));`);
    };
    m.customProgramCacheKey = () => `kit-${estilo}`;
  }
  materiais.set(estilo, m);
  return m;
}

/* ---------- o carregamento das peças ---------- */
/* os FBX citam um "Albedo.png" que não vem no pacote; a cor é a do Base Map, então o pedido vai para ele */
const gerente = new THREE.LoadingManager();
gerente.setURLModifier(u => u.endsWith("/Albedo.png") ? TFF + "Texture/Base Map.png" : u);
const loader = new FBXLoader(gerente);
interface Peca { geo: THREE.BufferGeometry; mats: THREE.Material[]; local: THREE.Matrix4 }
const cache = new Map<string, Promise<Peca[]>>();
const faltas: string[] = [];

/** as malhas visíveis de um FBX do kit (o LOD0; sem o LOD1 nem os colisores), com a escala em metros */
function pecas(nome: string, estilo: Estilo = "kit"): Promise<Peca[]> {
  const chave = nome + "|" + estilo;
  if (!cache.has(chave)) cache.set(chave, (async () => {
    const raiz = await loader.loadAsync(TFF + "Mesh/" + nome + ".fbx");
    raiz.rotation.set(0, 0, 0);                            // o FBXLoader põe -90° em x; as malhas do kit já vêm com o y para cima
    raiz.scale.setScalar(CM);
    raiz.updateMatrixWorld(true);
    const lista: Peca[] = [];
    raiz.traverse(o => {
      const m = o as THREE.Mesh;
      if (!m.isMesh || m.name !== "LOD0") return;
      const orig = Array.isArray(m.material) ? m.material : [m.material];
      const mats = orig.map(x => (x as THREE.MeshLambertMaterial).map ? materialKit(estilo) : MAT_AGUA);
      lista.push({ geo: m.geometry, mats, local: m.matrixWorld.clone() });
    });
    if (!lista.length) throw new Error(`FBX sem LOD0: ${nome}`);
    return lista;
  })());
  return cache.get(chave)!;
}

interface Lugar { x: number; y: number; z: number; giro: number; s: number }
const terreno = new THREE.Group();                         // o que o personagem pisa (e onde as plantas nascem)
const evitar = new THREE.Group();                          // onde as plantas não nascem: estrada, rio e construções
const resto = new THREE.Group();
cena.add(terreno, evitar, resto);

/** uma peça solta no mapa (um Mesh por malha), para o raio do chão achar */
async function por(nome: string, l: Partial<Lugar>, grupo: THREE.Group, sombra = true): Promise<void> {
  try {
    const g = new THREE.Group();
    for (const p of await pecas(nome)) {
      const m = new THREE.Mesh(p.geo, p.mats.length === 1 ? p.mats[0] : p.mats);
      m.applyMatrix4(p.local);
      m.castShadow = sombra && !p.mats.includes(MAT_AGUA);
      m.receiveShadow = true;
      g.add(m);
    }
    g.position.set(l.x ?? 0, l.y ?? 0, l.z ?? 0);
    g.rotation.y = l.giro ?? 0;
    g.scale.setScalar(l.s ?? 1);
    grupo.add(g);
    g.updateMatrixWorld(true);                             // o raio do chão usa a matriz de mundo antes do primeiro quadro
  } catch (e) { faltas.push(`${nome}: ${(e as Error).message}`); }
}

/** muitas cópias de uma peça (árvores, capim, flores), como InstancedMesh */
async function espalhar(nome: string, lugares: Lugar[], estilo: Estilo = "kit", sombra = true): Promise<void> {
  if (!lugares.length) return;
  try {
    for (const p of await pecas(nome, estilo)) {
      const im = new THREE.InstancedMesh(p.geo, p.mats.length === 1 ? p.mats[0] : p.mats, lugares.length);
      lugares.forEach((l, i) => im.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(l.x, l.y, l.z),
        new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), l.giro), new THREE.Vector3(l.s, l.s, l.s)).multiply(p.local)));
      im.castShadow = sombra;
      im.receiveShadow = true;
      im.computeBoundingSphere();
      resto.add(im);
    }
  } catch (e) { faltas.push(`${nome}: ${(e as Error).message}`); }
}

/* ---------- o chão por raio ---------- */
const raio = new THREE.Raycaster();
const BAIXO = new THREE.Vector3(0, -1, 0);
/** a altura do chão em (x, z) e se ali é estrada, rio ou construção; null fora da ilha */
function chao(x: number, z: number): { y: number; evitar: boolean } | null {
  raio.set(new THREE.Vector3(x, 60, z), BAIXO);
  const hit = raio.intersectObjects([terreno, evitar], true)[0];
  if (!hit) return null;
  let o: THREE.Object3D | null = hit.object, ev = false;
  while (o) { if (o === evitar) ev = true; o = o.parent; }
  return { y: hit.point.y, evitar: ev };
}

/** sorteia n lugares no gramado (fora da estrada, do rio e das construções), entre os raios r0 e r1 do centro c */
function sortear(semente: number, n: number, c: [number, number], r0: number, r1: number, s0: number, s1: number, altMin = -1): Lugar[] {
  const r = rng(semente), saida: Lugar[] = [];
  for (let k = 0; k < n * 6 && saida.length < n; k++) {
    const a = r() * Math.PI * 2, d = r0 + Math.sqrt(r()) * (r1 - r0);
    const x = c[0] + Math.cos(a) * d, z = c[1] + Math.sin(a) * d, h = chao(x, z);
    if (!h || h.evitar || h.y < altMin) continue;
    saida.push({ x, y: h.y, z, giro: r() * Math.PI * 2, s: s0 + r() * (s1 - s0) });
  }
  return saida;
}

/* ---------- o mar ---------- */
{
  const mar = new THREE.Mesh(new THREE.CircleGeometry(400, 64).rotateX(-Math.PI / 2),
    new THREE.MeshStandardMaterial({ color: 0x2d8fe0, roughness: 0.2, metalness: 0 }));
  mar.position.y = -0.9;
  mar.receiveShadow = true;
  cena.add(mar);
}

/* ---------- a montagem, na ordem do manual do kit ---------- */
async function montar(): Promise<void> {
  /* 1. a massa de terra: a ilha de 100 m, a praia em volta e dois platôs (40 m e 20 m) a noroeste */
  await Promise.all([
    por("LandMass/LM100RND", {}, terreno),
    por("LandMass/Shore01", {}, terreno),
    por("LandMass/LM40RND", { x: -18, y: 2.5, z: -16 }, terreno),
    por("LandMass/LM20", { x: -22, y: 5, z: -22 }, terreno),
    por("LandMass/LM20", { x: 24, y: 2.5, z: -24, giro: 0.5 }, terreno),
  ]);
  /* 2. as manchas de cor no chão */
  const r = rng(61);
  const manchas: Promise<void>[] = [];
  for (let i = 0; i < 22; i++) {
    const a = r() * Math.PI * 2, d = 6 + r() * 34, x = Math.cos(a) * d, z = Math.sin(a) * d, h = chao(x, z);
    if (h) manchas.push(por(`GroundPadding/GroundPadding06_${1 + (i % 4)}`, { x, y: h.y + 0.01, z, giro: r() * Math.PI * 2, s: 0.7 + r() * 0.6 }, resto, false));
  }
  await Promise.all(manchas);
  /* 3. a estrada (do sul até o platô) e o rio (a leste, com a ponte) */
  await Promise.all([
    por("RiverRoadLakeFall/RoadA01", { x: -2, y: 0.02, z: 26 }, evitar, false),
    por("RiverRoadLakeFall/RoadA02", { x: -2, y: 0.02, z: 12 }, evitar, false),
    por("RiverRoadLakeFall/RoadE01", { x: -2, y: 0.02, z: 12 }, evitar, false),
    por("RiverRoadLakeFall/RoadA01", { x: -4.7, y: 0.02, z: -1.4 }, evitar, false),
    por("RiverRoadLakeFall/RoadC01", { x: -2, y: 0.02, z: 12, giro: Math.PI }, evitar, false),
    por("RiverRoadLakeFall/RiverE02", { x: 30, y: 0, z: 8, giro: -0.3 }, evitar),
    por("RiverRoadLakeFall/Waterfall01", { x: 26, y: 2.5, z: -16 }, evitar),
  ]);
  await por("BuildingUtilityDeco/Bridge06", { x: 15, y: 0, z: 6, giro: Math.PI / 2 - 0.3 }, terreno);
  /* 4. pedras e montanhas */
  await Promise.all([
    por("Mountains/RockMountain01", { x: -36, y: 0, z: 18, giro: 0.4 }, evitar),
    por("Mountains/RockMountain03", { x: 34, y: 0, z: 28, giro: 1.2 }, evitar),
    por("Rock/RockCliff05", { x: -38, y: 0, z: -4, giro: 1.6 }, evitar),
    por("Rock/RockCliff06", { x: 4, y: 0, z: -40, giro: 0.2 }, evitar),
    ...[[8, 18], [-14, 30], [20, -6], [-30, 4], [12, -30]].map(([x, z], i) => por(`Rock/${["Rock01", "Rock03_1", "Rock04", "Rock06_1", "Rock01"][i]}`,
      { x, y: chao(x, z)?.y ?? 0, z, giro: i * 1.3, s: 0.8 + (i % 3) * 0.2 }, evitar)),
  ]);
  /* 5. construções e decoração: o portão na estrada, o portal no platô, a rampa e a escada para subir */
  await Promise.all([
    por("BuildingUtilityDeco/Gate01", { x: -2.5, y: 0.02, z: 36 }, evitar),
    por("BuildingUtilityDeco/Portal01", { x: -22, y: 5, z: -24 }, evitar),
    por("BuildingUtilityDeco/Ramp01", { x: -8, y: 0, z: 5.6, giro: 0 }, terreno),
    por("BuildingUtilityDeco/Stair01", { x: -14, y: 2.5, z: -10.3, giro: 0 }, terreno),
    por("BuildingUtilityDeco/TreeStump01", { x: 6, y: 0, z: 10 }, evitar),
  ]);
  /* 6. árvores, depois capim, depois flores (a ordem do manual) */
  await espalhar("TreePlants/Tree02", sortear(71, 140, [0, 0], 8, 45, 0.8, 1.4), "arvore");
  await espalhar("TreePlants/Tree02", sortear(72, 22, [-18, -16], 3, 18, 0.8, 1.3, 2), "arvore");
  await espalhar("TreePlants/Grass01", sortear(73, 700, [0, 0], 2, 46, 0.8, 1.6), "grama", false);
  await espalhar("TreePlants/Flower01", sortear(74, 260, [0, 0], 2, 46, 0.8, 1.4), "grama", false);
  await espalhar("Rock/Cobble01", sortear(75, 60, [0, 0], 4, 44, 0.8, 1.6), "kit", false);
}
montar().then(() => {
  if (faltas.length) { console.error("peças que faltaram:", faltas); estado.textContent = `${faltas.length} peça(s) não carregaram (ver o console)`; }
  else estado.textContent = "";
});

/* ---------- o personagem ---------- */
const heroi = new Heroi();
heroi.raiz.scale.setScalar(1.4);
cena.add(heroi.raiz);
let px = -2, pz = 30, py = 0;
const selSprite = document.getElementById("sprite") as HTMLSelectElement;
(async () => {
  const fonte = await Heroi.listar();
  if (!fonte) { selSprite.innerHTML = "<option>reserva (sem o atlas)</option>"; selSprite.disabled = true; return; }
  const nomes = Object.entries(fonte.atlas.sprites).filter(([, s]) => s.clipes?.Idle && s.clipes?.Run).map(([n, s]) => [n, s.digimon] as const);
  selSprite.innerHTML = nomes.map(([n, d]) => `<option value="${n}">${d} · ${n}</option>`).join("");
  selSprite.value = nomes.some(([n]) => n === SPRITE_PADRAO) ? SPRITE_PADRAO : nomes[0][0];
  heroi.usarSprite(fonte, selSprite.value);
  selSprite.addEventListener("change", () => heroi.usarSprite(fonte, selSprite.value));
})();

/* ---------- a câmera: órbita em volta do personagem ---------- */
const orbita = new OrbitControls(camera, tela);
orbita.enableDamping = true;
orbita.maxPolarAngle = 1.45;
orbita.minDistance = 4;
orbita.maxDistance = 220;
orbita.target.set(px, 1, pz);
camera.position.set(px, 14, pz + 22);
const chkLivre = document.getElementById("livre") as HTMLInputElement;
(window as unknown as { floresta: object }).floresta = { heroi, cena, camera, orbita, chao, pos: () => ({ ao, bloom }), ir: (x: number, z: number) => { px = x; pz = z; } };

/* ---------- a entrada ---------- */
const teclas = new Set<string>();
addEventListener("keydown", e => { if (!(e.target instanceof HTMLSelectElement)) teclas.add(e.code); });
addEventListener("keyup", e => teclas.delete(e.code));
addEventListener("blur", () => teclas.clear());
function direcao(): { x: number; z: number; correr: boolean } {
  let f = 0, l = 0;
  if (teclas.has("KeyW") || teclas.has("ArrowUp")) f += 1;
  if (teclas.has("KeyS") || teclas.has("ArrowDown")) f -= 1;
  if (teclas.has("KeyA") || teclas.has("ArrowLeft")) l -= 1;
  if (teclas.has("KeyD") || teclas.has("ArrowRight")) l += 1;
  const n = Math.hypot(f, l);
  return n === 0 ? { x: 0, z: 0, correr: false } : { x: l / n, z: f / n, correr: teclas.has("ShiftLeft") || teclas.has("ShiftRight") };
}

/* ---------- o pós-processamento: o que o Unity do kit faz e o modelo sozinho não tem ----------
     - a oclusão de ambiente (GTAO): escurece onde as coisas se encostam (a base das árvores, as pedras no chão, os cantos dos platôs);
     - o bloom: as partes emissivas (o portal) e o céu claro vazam um pouco de luz;
     - o tom de cor Neutral (Khronos PBR Neutral): segura os brancos estourados sem desbotar as cores, nem as do sprite. */
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.05;
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: 4 }));
composer.addPass(new RenderPass(cena, camera));
const ao = new GTAOPass(cena, camera, 1, 1);
ao.updateGtaoMaterial({ radius: 1.2, distanceExponent: 1.5, thickness: 1.5, scale: 1.2, samples: 16 });
ao.blendIntensity = 0.9;
composer.addPass(ao);
const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.22, 0.5, 0.92);
composer.addPass(bloom);
composer.addPass(new OutputPass());
const chkRealce = document.getElementById("realce") as HTMLInputElement;

/* ---------- o laço ---------- */
function redimensionar(): void {
  const w = tela.clientWidth, h = tela.clientHeight;
  if (tela.width !== Math.round(w * renderer.getPixelRatio()) || tela.height !== Math.round(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    composer.setPixelRatio(renderer.getPixelRatio());
    composer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}

let antes = performance.now(), quadros = 0, tFps = antes;
const fps = document.getElementById("fps")!;
function quadro(agora: number): void {
  const dt = Math.min(0.05, (agora - antes) / 1000);
  antes = agora;
  /* o andar relativo à câmera: para a frente é para onde ela olha, no chão */
  const d = direcao(), vel = d.correr ? CORRIDA : VELOCIDADE;
  const frente = new THREE.Vector3().subVectors(orbita.target, camera.position).setY(0).normalize();
  const direita = new THREE.Vector3(-frente.z, 0, frente.x);
  const andando = d.x !== 0 || d.z !== 0;
  if (andando) {
    const nx = px + (direita.x * d.x + frente.x * d.z) * vel * dt, nz = pz + (direita.z * d.x + frente.z * d.z) * vel * dt;
    const h = Math.hypot(nx, nz) < RAIO_ILHA ? chao(nx, nz) : null;
    /* não sobe degrau maior que 0,6 m (o platô só pela rampa e pela escada) */
    if (h && h.y - py < 0.6) { px = nx; pz = nz; py = h.y; }
  } else {
    const h = chao(px, pz);
    if (h) py = h.y;
  }
  heroi.atualizar(px, py, pz, d.x, andando, agora, dt, d.correr);
  /* o papel de frente para a câmera */
  heroi.raiz.rotation.y = Math.atan2(camera.position.x - px, camera.position.z - pz);
  if (!chkLivre.checked) {
    const alvo = new THREE.Vector3(px, py + 1, pz), delta = alvo.clone().sub(orbita.target).multiplyScalar(1 - Math.exp(-dt * 6));
    orbita.target.add(delta);
    camera.position.add(delta);
  }
  orbita.update();
  TEMPO.value = agora / 1000;
  CURVA.uTempo.value = agora / 1000;
  redimensionar();
  if (chkRealce.checked) composer.render();
  else renderer.render(cena, camera);
  quadros++;
  if (agora - tFps > 1000) { fps.textContent = `${Math.round((quadros * 1000) / (agora - tFps))} fps · ${renderer.info.render.calls} draw calls`; quadros = 0; tFps = agora; }
  requestAnimationFrame(quadro);
}
requestAnimationFrame(quadro);
