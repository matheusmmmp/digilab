/* O campo visto de lado (poc/lateral.html): o mundo 3D com o Digimon em sprite 2D, na composição de um campo de RPG lateral. Protótipo de
   vista, fora do jogo e do motor; reaproveita o personagem (heroi.ts) e os kits CC0 do mapa_ac, sem a dobra do mundo.
     - a câmera de lado, um pouco de cima, com campo de visão estreito (quase ortográfica) e seguindo o personagem só em x;
     - as camadas em profundidade: céu e nuvens, três faixas de morros que somem na névoa, árvores no meio, o caminho, o capim alto na
       frente (que encobre os pés) e a borda do penhasco;
     - um bloco flutuante que pula quando o personagem bate nele por baixo.
   Todos os números são do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { CURVA, GEO_SOMBRA, KEN, type Modelo, QUA, type Variante, carregarVariante, ceu, materialSombra, toon } from "../mapa_ac/cena.ts";
import { Heroi } from "../mapa_ac/heroi.ts";
import { rng } from "../mapa_ac/mapa.ts";

CURVA.uCurva.value = 0;                                  // sem o mundo curvo do mapa_ac

const X_MIN = -26, X_MAX = 26;                           // até onde o personagem anda
const Z_FUNDO = -1.0, Z_FRENTE = 1.3;                    // a faixa do caminho em que ele pode ir para a frente e para trás
const BORDA_Z = 3;                                       // onde o chão acaba e começa o penhasco
const VELOCIDADE = 3.4, CORRIDA = 6, PULO = 7.2, GRAVIDADE = 22;
const CAM = { fov: 22, altura: 6.2, dist: 25, olharY: 1.6, olharZ: -1 };
/* o modo pixel: a cena desenhada nesta altura em pixels e ampliada sem suavizar, como o pixel art em 3D */
const ALTURA_PIXEL = 300;
const SPRITE_PADRAO = "brasa_crianca_sereno";
const COR_NEVOA = 0xbfe6fb;

const tela = document.getElementById("tela") as HTMLCanvasElement;
const estado = document.getElementById("estado")!;
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const camera = new THREE.PerspectiveCamera(CAM.fov, 1, 0.1, 300);

const cena = new THREE.Scene();
cena.background = ceu();
cena.fog = new THREE.Fog(COR_NEVOA, 30, 80);
cena.add(new THREE.HemisphereLight(0xe6f4ff, 0x7fb85a, 1.7));
const sol = new THREE.DirectionalLight(0xfff0d0, 2.3);
sol.position.set(-0.5, 1, 0.8);
cena.add(sol);

/* ---------- texturas desenhadas no canvas ---------- */
/* desenhadas em poucos pixels e lidas sem filtro (nearest): o pixel art aplicado no 3D */
function canvasTex(w: number, h: number, desenhar: (g: CanvasRenderingContext2D) => void, repetir = false): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  desenhar(c.getContext("2d")!);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.NearestMipmapNearestFilter;
  if (repetir) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

/* a grama do chão: um ladrilho de 16 x 16 com folhas em dois tons */
const TEX_GRAMA = canvasTex(16, 16, g => {
  const r = rng(7);
  g.fillStyle = "#74c455"; g.fillRect(0, 0, 16, 16);
  for (let i = 0; i < 22; i++) { g.fillStyle = r() < 0.5 ? "#5fae46" : "#8fd66a"; g.fillRect(Math.floor(r() * 16), Math.floor(r() * 16), 1, 1 + Math.floor(r() * 2)); }
}, true);

/* a face do penhasco: faixas de estrato em tons de terra, com a grama pendendo no alto */
const TEX_PENHASCO = canvasTex(32, 32, g => {
  const r = rng(3);
  const faixas = ["#c9a46a", "#b58b55", "#d4b27a", "#a77d4b", "#bf9660"];
  let y = 2;
  for (let i = 0; y < 32; i++) { const h = 3 + Math.floor(r() * 4); g.fillStyle = faixas[i % faixas.length]; g.fillRect(0, y, 32, h); y += h; }
  g.fillStyle = "#8a6238";
  for (let i = 0; i < 14; i++) g.fillRect(Math.floor(r() * 32), 6 + Math.floor(r() * 26), 2 + Math.floor(r() * 3), 1);
  g.fillStyle = "#5fb84a"; g.fillRect(0, 0, 32, 2);
  for (let x = 0; x < 32; x += 2) g.fillRect(x, 2, 2, Math.floor(r() * 3));
}, true);

/* o caminho de terra clara, com a borda irregular */
const TEX_CAMINHO = canvasTex(32, 16, g => {
  const r = rng(5);
  for (let x = 0; x < 32; x++) { const a = 1 + Math.floor(r() * 2), b = 14 - Math.floor(r() * 2); g.fillStyle = "#ead293"; g.fillRect(x, a, 1, b - a); }
  g.fillStyle = "#d3b571";
  for (let i = 0; i < 18; i++) g.fillRect(Math.floor(r() * 32), 3 + Math.floor(r() * 10), 1, 1);
  g.fillStyle = "#fbeab4";
  for (let i = 0; i < 10; i++) g.fillRect(Math.floor(r() * 32), 3 + Math.floor(r() * 10), 1, 1);
}, true);

/* o bloco "?" e o bloco já usado */
const texBloco = (usado: boolean) => canvasTex(64, 64, g => {  // este fica liso: é o destaque da cena
  g.fillStyle = usado ? "#a7794a" : "#f2a33a"; g.fillRect(0, 0, 64, 64);
  g.strokeStyle = usado ? "#6d4a28" : "#b8641e"; g.lineWidth = 6; g.strokeRect(3, 3, 58, 58);
  g.fillStyle = usado ? "#6d4a28" : "#7a3b12";
  for (const [x, y] of [[10, 10], [54, 10], [10, 54], [54, 54]]) { g.beginPath(); g.arc(x, y, 3, 0, Math.PI * 2); g.fill(); }
  if (!usado) { g.fillStyle = "#fff6d8"; g.font = "bold 40px system-ui"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("?", 32, 35); }
});

/* ---------- o chão, o caminho e o penhasco ---------- */
const LARGURA_CENA = 90;
{
  const fundoZ = -40, prof = BORDA_Z - fundoZ;
  const texG = TEX_GRAMA.clone();
  texG.repeat.set(LARGURA_CENA / 1.5, prof / 1.5);
  texG.needsUpdate = true;
  const chao = new THREE.Mesh(new THREE.PlaneGeometry(LARGURA_CENA, prof).rotateX(-Math.PI / 2), toon({ map: texG }));
  chao.position.set(0, 0, fundoZ + prof / 2);
  const tex = TEX_PENHASCO.clone();
  tex.repeat.set(LARGURA_CENA / 3, 1);
  tex.needsUpdate = true;
  const penhasco = new THREE.Mesh(new THREE.PlaneGeometry(LARGURA_CENA, 3.2), toon({ map: tex }));
  penhasco.position.set(0, -1.45, BORDA_Z);
  const texC = TEX_CAMINHO.clone();
  texC.repeat.set(LARGURA_CENA / 3.4, 1);
  texC.needsUpdate = true;
  const caminho = new THREE.Mesh(new THREE.PlaneGeometry(LARGURA_CENA, 3.4).rotateX(-Math.PI / 2),
    toon({ map: texC, transparent: true, depthWrite: false }));
  caminho.position.set(0, 0.01, 0.15);
  caminho.renderOrder = 1;
  cena.add(chao, penhasco, caminho);
}

/* ---------- os morros do fundo: faixas de calombos que esfriam e somem na névoa ---------- */
{
  const geo = new THREE.SphereGeometry(1, 20, 12);
  const camadas = [{ z: -13, cor: 0x63b863, raio: 3.4, alt: 2.2, n: 26 }, { z: -24, cor: 0x4fa59a, raio: 5, alt: 3.6, n: 20 },
    { z: -38, cor: 0x7fb7c8, raio: 7, alt: 5.5, n: 16 }];
  const r = rng(11);
  for (const c of camadas) {
    const im = new THREE.InstancedMesh(geo, toon({ color: c.cor }), c.n);
    for (let i = 0; i < c.n; i++) {
      const x = -LARGURA_CENA / 2 + (i + r() * 0.6) * (LARGURA_CENA / c.n) * 1.3 - 10, rr = c.raio * (0.8 + r() * 0.5);
      im.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(x, -0.4, c.z + r() * 2), new THREE.Quaternion(),
        new THREE.Vector3(rr, c.alt * (0.8 + r() * 0.5), rr * 0.7)));
    }
    cena.add(im);
  }
}

/* ---------- as nuvens: recortes brancos baixos, no céu que a câmera de lado enxerga ---------- */
{
  const tex = canvasTex(256, 128, g => {
    g.fillStyle = "#ffffff";
    for (const [x, y, rr] of [[70, 82, 36], [118, 62, 48], [172, 80, 38], [100, 96, 32], [150, 98, 30]]) { g.beginPath(); g.arc(x, y, rr, 0, Math.PI * 2); g.fill(); }
  });
  const r = rng(9);
  for (let i = 0; i < 8; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, fog: false, depthWrite: false }));
    const w = 14 + r() * 12;
    s.scale.set(w, w / 2, 1);
    s.position.set(-50 + i * 14 + r() * 6, 9 + r() * 5, -55 - r() * 10);
    cena.add(s);
  }
}

/* ---------- o bloco "?" ---------- */
const BLOCO = { x: 3, y: 2.2, z: 0, lado: 0.8 };   // a base (1,8) abaixo do alto do pulo com a cabeça (2,28)
const matBloco = new THREE.MeshToonMaterial({ map: texBloco(false) });
const bloco = new THREE.Mesh(new THREE.BoxGeometry(BLOCO.lado, BLOCO.lado, BLOCO.lado), matBloco);
bloco.position.set(BLOCO.x, BLOCO.y, BLOCO.z);
const sombraBloco = new THREE.Mesh(GEO_SOMBRA, materialSombra());
sombraBloco.position.set(BLOCO.x, 0.02, BLOCO.z);
sombraBloco.scale.set(0.8, 1, 0.5);
sombraBloco.renderOrder = 1;
cena.add(bloco, sombraBloco);
let blocoUsado = false, blocoBate = 0;

/* ---------- os modelos dos kits ---------- */
type Peca = { url: string; altura: number; vento: number; tinta?: number };
async function instanciar(loader: GLTFLoader, p: Peca, lugares: { x: number; z: number; s: number; giro: number }[]): Promise<THREE.Object3D[]> {
  const modelo: Modelo = { arquivos: [p.url], altura: p.altura, vento: p.vento, sombra: 0 };
  const v: Variante = await carregarVariante(loader, p.url, modelo);
  const saida: THREE.Object3D[] = [];
  for (const peca of v.pecas) {
    if (p.tinta !== undefined) (peca.mat as THREE.MeshToonMaterial).color.multiply(new THREE.Color(p.tinta));
    const im = new THREE.InstancedMesh(peca.geo, peca.mat, lugares.length);
    lugares.forEach((l, i) => im.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(l.x, 0, l.z),
      new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), l.giro), new THREE.Vector3(l.s, l.s, l.s)).multiply(peca.local)));
    saida.push(im);
  }
  return saida;
}

/* onde cada coisa fica: uma lista de (x, z) por peça, sorteada com semente fixa */
function espalhar(semente: number, n: number, z0: number, z1: number, s0: number, s1: number) {
  const r = rng(semente);
  return Array.from({ length: n }, () => ({ x: -LARGURA_CENA / 2 + r() * LARGURA_CENA, z: z0 + r() * (z1 - z0), s: s0 + r() * (s1 - s0), giro: r() * Math.PI * 2 }));
}

async function povoar(): Promise<string[]> {
  const loader = new GLTFLoader(), faltas: string[] = [];
  const sombras: { x: number; z: number; r: number }[] = [];
  const pedidos: [Peca, ReturnType<typeof espalhar>, number][] = [
    /* a árvore grande atrás do caminho, e as do meio */
    [{ url: QUA + "CommonTree_3.gltf", altura: 6.5, vento: 0.003 }, [{ x: -4.5, z: -4.2, s: 1, giro: 0.4 }], 2.2],
    [{ url: QUA + "CommonTree_1.gltf", altura: 5, vento: 0.003 }, [{ x: 14, z: -6, s: 1, giro: 1 }, { x: -19, z: -7, s: 1.1, giro: 2 }], 1.8],
    [{ url: QUA + "CommonTree_2.gltf", altura: 4.5, vento: 0.003 }, espalhar(21, 9, -11, -8, 0.8, 1.2), 0],
    [{ url: QUA + "Pine_2.gltf", altura: 5, vento: 0.002 }, espalhar(22, 10, -12, -9, 0.8, 1.2), 0],
    /* arbustos e flores no gramado de trás */
    [{ url: QUA + "Bush_Common_Flowers.gltf", altura: 1.1, vento: 0.02 }, espalhar(31, 14, -5.5, -2, 0.8, 1.2), 0.7],
    [{ url: QUA + "Bush_Common.gltf", altura: 1, vento: 0.02 }, espalhar(32, 10, -6, -2.5, 0.8, 1.2), 0.6],
    [{ url: QUA + "Flower_3_Group.gltf", altura: 0.45, vento: 0.06 }, espalhar(33, 40, -4, -1.6, 0.8, 1.3), 0],
    [{ url: QUA + "Flower_4_Group.gltf", altura: 0.45, vento: 0.06 }, espalhar(34, 40, -4, -1.6, 0.8, 1.3), 0],
    [{ url: QUA + "Grass_Common_Short.gltf", altura: 0.3, vento: 0.08 }, espalhar(35, 120, -8, -1.4, 0.8, 1.4), 0],
    /* uma cerca velha e pedras na beira do caminho */
    [{ url: KEN + "fence_simple.glb", altura: 0.8, vento: 0 }, [-14, -12.6, -11.2, 18, 19.4].map((x, i) => ({ x, z: -1.9, s: 1, giro: i === 1 ? 0.15 : 0 })), 0],
    [{ url: QUA + "Rock_Medium_1.gltf", altura: 0.7, vento: 0 }, [{ x: 9, z: -2, s: 1, giro: 0 }, { x: -9, z: 2.3, s: 0.8, giro: 2 }], 0.5],
    /* o capim alto na frente, dourado e verde, que encobre os pés de quem anda no caminho */
    [{ url: QUA + "Grass_Wispy_Tall.gltf", altura: 1.0, vento: 0.08, tinta: 0xffe27a }, espalhar(41, 150, 1.5, 2.9, 0.8, 1.3), 0],
    [{ url: QUA + "Grass_Common_Tall.gltf", altura: 0.9, vento: 0.08, tinta: 0xffd86a }, espalhar(42, 110, 1.6, 2.9, 0.8, 1.3), 0],
    [{ url: QUA + "Grass_Common_Tall.gltf", altura: 0.8, vento: 0.08 }, espalhar(43, 90, 1.8, 2.95, 0.8, 1.2), 0],
  ];
  await Promise.all(pedidos.map(async ([p, lugares, raioSombra]) => {
    try {
      cena.add(...await instanciar(loader, p, lugares));
      if (raioSombra > 0) for (const l of lugares) sombras.push({ x: l.x, z: l.z, r: raioSombra * l.s });
    } catch (e) { faltas.push(`${p.url}: ${(e as Error).message}`); }
  }));
  const somb = new THREE.InstancedMesh(GEO_SOMBRA, materialSombra(), sombras.length);
  sombras.forEach((s, i) => somb.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(s.x, 0.02, s.z), new THREE.Quaternion(),
    new THREE.Vector3(s.r * 2, 1, s.r * 1.4))));
  somb.renderOrder = 1;
  cena.add(somb);
  return faltas;
}
povoar().then(faltas => {
  if (faltas.length) { console.error("modelos que faltaram:", faltas); estado.textContent = `${faltas.length} modelo(s) não carregaram (ver o console)`; }
  else estado.textContent = "";
});

/* ---------- o personagem ---------- */
const heroi = new Heroi();
cena.add(heroi.raiz);
let px = -2, pz = 0.2, py = 0, vy = 0;
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
(window as unknown as { lateral: object }).lateral = { heroi, cena, camera, ir: (x: number) => { px = x; } };

/* ---------- a entrada: teclado e toque ---------- */
const teclas = new Set<string>();
let pedePulo = false;
addEventListener("keydown", e => {
  if (e.target instanceof HTMLSelectElement) return;
  if (e.code === "Space") { pedePulo = true; e.preventDefault(); }
  teclas.add(e.code);
});
addEventListener("keyup", e => teclas.delete(e.code));
addEventListener("blur", () => teclas.clear());
let toque: { x0: number; y0: number; dx: number; dy: number; t0: number } | null = null;
tela.addEventListener("pointerdown", e => { toque = { x0: e.clientX, y0: e.clientY, dx: 0, dy: 0, t0: performance.now() }; tela.setPointerCapture(e.pointerId); });
tela.addEventListener("pointermove", e => { if (toque) { toque.dx = e.clientX - toque.x0; toque.dy = e.clientY - toque.y0; } });
tela.addEventListener("pointerup", () => {
  if (toque && Math.hypot(toque.dx, toque.dy) < 10 && performance.now() - toque.t0 < 250) pedePulo = true;
  toque = null;
});

function direcao(): { x: number; z: number; correr: boolean } {
  let x = 0, z = 0;
  if (teclas.has("KeyA") || teclas.has("ArrowLeft")) x -= 1;
  if (teclas.has("KeyD") || teclas.has("ArrowRight")) x += 1;
  if (teclas.has("KeyW") || teclas.has("ArrowUp")) z -= 1;
  if (teclas.has("KeyS") || teclas.has("ArrowDown")) z += 1;
  let correr = teclas.has("ShiftLeft") || teclas.has("ShiftRight");
  if (toque && Math.hypot(toque.dx, toque.dy) > 12) { x = toque.dx; z = toque.dy * 0.6; correr = Math.abs(toque.dx) > 110; }
  const n = Math.hypot(x, z);
  return n === 0 ? { x: 0, z: 0, correr: false } : { x: x / n, z: z / n, correr };
}

/* ---------- o laço ---------- */
const chkPixel = document.getElementById("pixel") as HTMLInputElement;
const aplicarPixel = () => { tela.style.imageRendering = chkPixel.checked ? "pixelated" : "auto"; };
chkPixel.addEventListener("change", aplicarPixel);
aplicarPixel();
function redimensionar(): void {
  const w = tela.clientWidth, h = tela.clientHeight;
  const razao = chkPixel.checked ? ALTURA_PIXEL / h : Math.min(devicePixelRatio, 2);
  if (renderer.getPixelRatio() !== razao) renderer.setPixelRatio(razao);
  if (tela.width !== Math.round(w * renderer.getPixelRatio()) || tela.height !== Math.round(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    /* na tela em pé, o campo de visão abre para caber a mesma largura de cena */
    camera.fov = w / h < 1 ? CAM.fov * 1.6 : CAM.fov;
    camera.updateProjectionMatrix();
  }
}

const camX = { v: px };
let antes = performance.now(), quadros = 0, tFps = antes;
const fps = document.getElementById("fps")!;
function quadro(agora: number): void {
  const dt = Math.min(0.05, (agora - antes) / 1000);
  antes = agora;
  const d = direcao(), vel = d.correr ? CORRIDA : VELOCIDADE;
  const andando = d.x !== 0 || d.z !== 0;
  px = Math.max(X_MIN, Math.min(X_MAX, px + d.x * vel * dt));
  pz = Math.max(Z_FUNDO, Math.min(Z_FRENTE, pz + d.z * vel * 0.6 * dt));
  /* o pulo, e a cabeçada no bloco quando sobe embaixo dele */
  if (pedePulo && py === 0) vy = PULO;
  pedePulo = false;
  const yAntes = py;
  vy -= GRAVIDADE * dt;
  py = Math.max(0, py + vy * dt);
  if (py === 0) vy = 0;
  const alturaHeroi = 1.1, baseBloco = BLOCO.y - BLOCO.lado / 2;
  if (vy > 0 && Math.abs(px - BLOCO.x) < 0.65 && Math.abs(pz - BLOCO.z) < 0.9 && yAntes + alturaHeroi <= baseBloco && py + alturaHeroi > baseBloco) {
    py = baseBloco - alturaHeroi; vy = 0; blocoBate = 1;
    if (!blocoUsado) { blocoUsado = true; matBloco.map = texBloco(true); matBloco.needsUpdate = true; }
  }
  blocoBate = Math.max(0, blocoBate - dt * 5);
  bloco.position.y = BLOCO.y + Math.sin(blocoBate * Math.PI) * 0.25 + (blocoUsado ? 0 : Math.sin(agora / 500) * 0.04);
  bloco.rotation.y = blocoUsado ? 0 : Math.sin(agora / 900) * 0.12;

  heroi.atualizar(px, py, pz, d.x, andando && py === 0, agora, dt, d.correr);
  /* a câmera de lado segue o personagem em x, com folga */
  camX.v += (px - camX.v) * (1 - Math.exp(-dt * 4));
  camera.position.set(camX.v, CAM.altura, CAM.dist);
  camera.lookAt(camX.v, CAM.olharY, CAM.olharZ);
  CURVA.uTempo.value = agora / 1000;
  redimensionar();
  renderer.render(cena, camera);
  quadros++;
  if (agora - tFps > 1000) { fps.textContent = `${Math.round((quadros * 1000) / (agora - tFps))} fps · ${renderer.info.render.calls} draw calls`; quadros = 0; tFps = agora; }
  requestAnimationFrame(quadro);
}
requestAnimationFrame(quadro);
