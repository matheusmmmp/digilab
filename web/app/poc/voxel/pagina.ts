/* A ilha em voxel (poc/voxel.html): um mapa gerado por código no jeito do Cube World, sem nenhum asset baixado.
     - o terreno: um campo de alturas com ruído (fbm) e a queda para o mar na borda, em cubos de 0,5 m;
     - a cor por cubo, sem textura: areia na beira d'água, grama em manchas, pedra nas encostas íngremes, neve no alto, terra por baixo,
       e uma variação pequena de brilho por cubo (o "granulado" do Cube World);
     - árvores redondas, pinheiros e cerejeiras, pedras e flores, também em cubos;
     - uma malha só, com as faces escondidas cortadas e a oclusão por vértice (o canto entre dois cubos escurece), que é o que dá o volume;
     - o Digimon em sprite 2D anda por cima e sobe um cubo sozinho.
   A mesma semente dá a mesma ilha (?semente=). Protótipo de vista, fora do jogo e do motor. Todos os números: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
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

const S = 0.5;                                           // o lado do cubo, em metros
const N = 192;                                           // a ilha tem N x N colunas (96 m)
const ALTO = 72;                                         // a altura máxima da grade, em cubos
const AGUA = 7;                                          // o nível do mar, em cubos
const NEVE = 40;                                         // daqui para cima, neve
const VELOCIDADE = 3.6, CORRIDA = 7, PULO = 6.5, GRAVIDADE = 20;
const SPRITE_PADRAO = "brasa_crianca_sereno";
const SEMENTE = Math.max(1, Math.floor(Number(new URLSearchParams(location.search).get("semente")) || 7));

const tela = document.getElementById("tela") as HTMLCanvasElement;
const estado = document.getElementById("estado")!;

/* ---------- o ruído: valor em grade com interpolação suave, somado em oitavas (fbm) ---------- */
function ruido2(semente: number): (x: number, y: number) => number {
  const r = rng(semente), T = 256, tab = Float32Array.from({ length: T * T }, () => r());
  const v = (i: number, j: number) => tab[(((j % T) + T) % T) * T + (((i % T) + T) % T)];
  const suave = (t: number) => t * t * (3 - 2 * t);
  return (x, y) => {
    const i = Math.floor(x), j = Math.floor(y), fx = suave(x - i), fy = suave(y - j);
    const a = v(i, j) + (v(i + 1, j) - v(i, j)) * fx, b = v(i, j + 1) + (v(i + 1, j + 1) - v(i, j + 1)) * fx;
    return a + (b - a) * fy;
  };
}
function fbm(f: (x: number, y: number) => number, x: number, y: number, oitavas: number): number {
  let soma = 0, amp = 1, total = 0, freq = 1;
  for (let o = 0; o < oitavas; o++) { soma += f(x * freq, y * freq) * amp; total += amp; amp *= 0.5; freq *= 2; }
  return soma / total;
}
/* um sorteio fixo por cubo, para a variação de brilho (o mesmo cubo dá sempre o mesmo valor) */
function hash3(x: number, y: number, z: number): number {
  let h = Math.imul(x, 374761393) ^ Math.imul(y, 668265263) ^ Math.imul(z, 2147483647) ^ SEMENTE;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

/* ---------- o terreno: a altura de cada coluna ---------- */
const altura = new Int16Array(N * N);
const ALT = (x: number, z: number) => (x < 0 || z < 0 || x >= N || z >= N ? 0 : altura[z * N + x]);
{
  const base = ruido2(SEMENTE), detalhe = ruido2(SEMENTE + 1), serra = ruido2(SEMENTE + 2);
  for (let z = 0; z < N; z++) for (let x = 0; x < N; x++) {
    const dx = (x - N / 2) / (N / 2), dz = (z - N / 2) / (N / 2);
    /* a máscara da ilha: 1 no centro, 0 na borda, com a costa recortada pelo ruído */
    const d = Math.hypot(dx, dz) + (fbm(detalhe, x / 22, z / 22, 3) - 0.5) * 0.35;
    const mascara = Math.max(0, Math.min(1, (1 - d) / 0.45));
    const colinas = fbm(base, x / 48, z / 48, 4);
    const montanha = Math.pow(Math.max(0, fbm(serra, x / 60, z / 60, 3) - 0.4) * 2.4, 2);
    const h = 3 + mascara * (AGUA + colinas * 16 + montanha * 34);
    altura[z * N + x] = Math.max(0, Math.min(ALTO - 12, Math.floor(h)));
  }
}

/* ---------- os cubos soltos (árvores, pedras, flores): uma tabela por posição ---------- */
const soltos = new Map<number, number>();               // a chave da posição -> a cor (0xRRGGBB)
const chave = (x: number, y: number, z: number) => (y * N + z) * N + x;
const solido = (x: number, y: number, z: number) => y < 0 || (x >= 0 && z >= 0 && x < N && z < N && (y < ALT(x, z) || soltos.has(chave(x, y, z))));
const por = (x: number, y: number, z: number, cor: number) => { if (x >= 0 && z >= 0 && x < N && z < N && y >= ALT(x, z) && y < ALTO) soltos.set(chave(x, y, z), cor); };

const COR = {
  areia: 0xe9d9a1, grama: [0x78cf55, 0x8ad95e, 0x6cc44e, 0x9fe06a], pedra: 0xa3a6ad, neve: 0xf4f7fb, terra: 0x9b7048, terraEscura: 0x7d5a3a,
  tronco: 0x7a5232, folhas: [0x4fae44, 0x5fbf4f, 0x6fca58], pinho: [0x3f9256, 0x4ca062], cereja: [0xf29bc0, 0xf7b5d1, 0xe983ad], outono: [0xe08a2e, 0xeaa23c],
  flores: [0xe94b4b, 0xffd23f, 0xffffff, 0x6b8cff, 0xff8ad8],
};
const declive = (x: number, z: number) => {
  const h = ALT(x, z);
  return Math.max(Math.abs(h - ALT(x + 1, z)), Math.abs(h - ALT(x - 1, z)), Math.abs(h - ALT(x, z + 1)), Math.abs(h - ALT(x, z - 1)));
};
const manchaGrama = ruido2(SEMENTE + 3);
/** a cor de um cubo do terreno, pela altura, pelo declive e pela profundidade abaixo da superfície */
function corTerreno(x: number, y: number, z: number): number {
  const h = ALT(x, z), fundo = h - 1 - y;
  if (h <= AGUA + 1) return fundo > 2 ? COR.terraEscura : COR.areia;
  /* o alto e as encostas íngremes são pedra de cima a baixo (sem a faixa de terra), com neve só no topo da coluna mais alta */
  if (h > NEVE - 6 || declive(x, z) >= 3) return fundo === 0 && y >= NEVE + Math.floor(hash3(x, 0, z) * 3) ? COR.neve : COR.pedra;
  if (fundo === 0) { const m = fbm(manchaGrama, x / 14, z / 14, 2); return COR.grama[Math.min(3, Math.floor(m * 4.4))]; }
  return fundo > 3 ? COR.terraEscura : COR.terra;
}

/* ---------- a vegetação ---------- */
{
  const r = rng(SEMENTE + 10), ocupado: [number, number][] = [];
  const longe = (x: number, z: number, d: number) => ocupado.every(([a, b]) => (a - x) ** 2 + (b - z) ** 2 >= d * d);
  const gramado = (x: number, z: number) => { const h = ALT(x, z); return h > AGUA + 1 && h < NEVE - 8 && declive(x, z) <= 1; };
  const arredondada = (x: number, z: number, y0: number, folhas: number[]) => {
    const tronco = 5 + Math.floor(r() * 3), raio = 2.6 + r() * 1.2;
    for (let y = 0; y < tronco; y++) por(x, y0 + y, z, COR.tronco);
    const cy = y0 + tronco + 1, ri = Math.ceil(raio);
    for (let dy = -ri; dy <= ri; dy++) for (let dz = -ri; dz <= ri; dz++) for (let dx = -ri; dx <= ri; dx++) {
      const d = Math.hypot(dx, dy * 1.25, dz);
      if (d <= raio - hash3(x + dx, cy + dy, z + dz) * 0.9) por(x + dx, cy + dy, z + dz, folhas[Math.floor(hash3(dx, dy, dz + x) * folhas.length)]);
    }
  };
  const pinheiro = (x: number, z: number, y0: number) => {
    const alt = 9 + Math.floor(r() * 5);
    for (let y = 0; y < alt; y++) por(x, y0 + y, z, COR.tronco);
    for (let y = 3; y <= alt + 1; y++) {
      const raio = Math.max(0.6, ((alt + 1 - y) / (alt - 2)) * 3.4) * (y % 2 ? 1 : 0.8), ri = Math.ceil(raio);
      for (let dz = -ri; dz <= ri; dz++) for (let dx = -ri; dx <= ri; dx++)
        if (Math.hypot(dx, dz) <= raio) por(x + dx, y0 + y, z + dz, COR.pinho[(dx + dz + y) & 1]);
    }
  };
  for (let k = 0; k < 9000 && ocupado.length < 150; k++) {
    const x = 4 + Math.floor(r() * (N - 8)), z = 4 + Math.floor(r() * (N - 8));
    if (!gramado(x, z) || !longe(x, z, 11)) continue;
    const y0 = ALT(x, z), alto = y0 > 22, t = r();
    if (alto || t < 0.3) pinheiro(x, z, y0);
    else if (t < 0.4) arredondada(x, z, y0, COR.cereja);
    else if (t < 0.47) arredondada(x, z, y0, COR.outono);
    else arredondada(x, z, y0, COR.folhas);
    ocupado.push([x, z]);
  }
  /* pedras: montinhos de 2 a 6 cubos */
  for (let k = 0; k < 160; k++) {
    const x = 2 + Math.floor(r() * (N - 4)), z = 2 + Math.floor(r() * (N - 4));
    if (ALT(x, z) <= AGUA) continue;
    const n = 2 + Math.floor(r() * 5);
    for (let i = 0; i < n; i++) { const a = x + Math.floor(r() * 3) - 1, b = z + Math.floor(r() * 3) - 1; por(a, ALT(a, b) + (i > 3 ? 1 : 0), b, COR.pedra); }
  }
  /* flores: um cubo colorido em cima da grama, em grupinhos */
  for (let k = 0; k < 120; k++) {
    const x = Math.floor(r() * N), z = Math.floor(r() * N);
    if (!gramado(x, z)) continue;
    const cor = COR.flores[Math.floor(r() * COR.flores.length)];
    for (let i = 0; i < 4; i++) { const a = x + Math.floor(r() * 5) - 2, b = z + Math.floor(r() * 5) - 2; if (gramado(a, b) && !soltos.has(chave(a, ALT(a, b), b))) por(a, ALT(a, b), b, cor); }
  }
}

/* ---------- a malha: só as faces à mostra, com a oclusão por vértice ---------- */
/* as 6 faces: a normal e os 4 cantos (no sentido anti-horário visto de fora) */
const FACES: { n: [number, number, number]; c: [number, number, number][] }[] = [
  { n: [0, 1, 0], c: [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]] },
  { n: [0, -1, 0], c: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]] },
  { n: [1, 0, 0], c: [[1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1]] },
  { n: [-1, 0, 0], c: [[0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]] },
  { n: [0, 0, 1], c: [[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]] },
  { n: [0, 0, -1], c: [[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]] },
];
const BRILHO_AO = [0.5, 0.68, 0.84, 1];                  // 0 = canto fechado por dois cubos, 3 = canto aberto
const pos: number[] = [], nor: number[] = [], cor: number[] = [], idx: number[] = [];
const cTmp = new THREE.Color();
function face(x: number, y: number, z: number, f: (typeof FACES)[number], corHex: number): void {
  const [nx, ny, nz] = f.n;
  /* os dois eixos da face (os que não são a normal) */
  const eixos = [0, 1, 2].filter(e => f.n[e] === 0);
  const ao: number[] = [];
  for (const c of f.c) {
    const d = [0, 0, 0], e = [0, 0, 0];
    d[eixos[0]] = c[eixos[0]] ? 1 : -1;
    e[eixos[1]] = c[eixos[1]] ? 1 : -1;
    const bx = x + nx, by = y + ny, bz = z + nz;
    const s1 = solido(bx + d[0], by + d[1], bz + d[2]) ? 1 : 0, s2 = solido(bx + e[0], by + e[1], bz + e[2]) ? 1 : 0;
    const cc = solido(bx + d[0] + e[0], by + d[1] + e[1], bz + d[2] + e[2]) ? 1 : 0;
    ao.push(s1 && s2 ? 0 : 3 - (s1 + s2 + cc));
  }
  /* o granulado: cada cubo um pouco mais claro ou mais escuro; as faces de cima um tom mais claras que as dos lados */
  const var_ = 0.93 + hash3(x, y, z) * 0.14;
  const base = pos.length / 3;
  f.c.forEach((c, i) => {
    pos.push((x + c[0] - N / 2) * S, (y + c[1]) * S, (z + c[2] - N / 2) * S);
    nor.push(nx, ny, nz);
    cTmp.setHex(corHex).convertSRGBToLinear().multiplyScalar(var_ * BRILHO_AO[ao[i]]);
    cor.push(cTmp.r, cTmp.g, cTmp.b);
  });
  /* a diagonal do quadrado vai pelo par de cantos menos escuros (evita o degradê torto) */
  if (ao[0] + ao[2] >= ao[1] + ao[3]) idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
  else idx.push(base + 1, base + 2, base + 3, base + 1, base + 3, base);
}
const t0 = performance.now();
for (let z = 0; z < N; z++) for (let x = 0; x < N; x++) {
  const h = ALT(x, z);
  if (h <= 0) continue;
  /* o topo da coluna e os lados até a altura do vizinho */
  if (!solido(x, h, z)) face(x, h - 1, z, FACES[0], corTerreno(x, h - 1, z));
  for (const f of FACES.slice(2)) {
    const hv = ALT(x + f.n[0], z + f.n[2]);
    for (let y = Math.max(0, hv); y < h; y++) if (!solido(x + f.n[0], y, z + f.n[2])) face(x, y, z, f, corTerreno(x, y, z));
  }
}
for (const [k, c] of soltos) {
  const x = k % N, z = Math.floor(k / N) % N, y = Math.floor(k / (N * N));
  for (const f of FACES) if (!solido(x + f.n[0], y + f.n[1], z + f.n[2])) face(x, y, z, f, c);
}
const geo = new THREE.BufferGeometry();
geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
geo.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
geo.setAttribute("color", new THREE.Float32BufferAttribute(cor, 3));
geo.setIndex(idx);
geo.computeBoundingSphere();
const malhaMs = performance.now() - t0;

/* ---------- a cena ---------- */
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.05;
const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 600);
const cena = new THREE.Scene();
cena.background = ceu();
cena.fog = new THREE.Fog(COR_HORIZONTE, 110, 300);
cena.add(new THREE.HemisphereLight(0xeaf6ff, 0x7a9a5e, 1.4));
const sol = new THREE.DirectionalLight(0xffeccc, 2.8);
sol.position.set(-45, 70, 35);
sol.castShadow = true;
sol.shadow.mapSize.set(4096, 4096);
Object.assign(sol.shadow.camera, { left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 220 });
sol.shadow.bias = -0.0003;
sol.shadow.normalBias = 0.04;
cena.add(sol);
const ilha = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.92, metalness: 0 }));
ilha.castShadow = ilha.receiveShadow = true;
cena.add(ilha);
/* o mar: um plano largo e o raso em volta da ilha um pouco mais claro */
const mar = new THREE.Mesh(new THREE.CircleGeometry(400, 64).rotateX(-Math.PI / 2),
  new THREE.MeshStandardMaterial({ color: 0x2f93e0, roughness: 0.15, metalness: 0, transparent: true, opacity: 0.88 }));
mar.position.y = (AGUA + 0.6) * S;
mar.receiveShadow = true;
cena.add(mar);
const fundo = new THREE.Mesh(new THREE.CircleGeometry(400, 64).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xd9c98e, roughness: 1 }));
fundo.position.y = 0;
cena.add(fundo);
estado.textContent = "";
console.info(`voxel: semente ${SEMENTE}, ${soltos.size} cubos soltos, ${idx.length / 6} faces, malha em ${malhaMs.toFixed(0)} ms`);

/* ---------- o chão para o personagem ---------- */
/** a altura (em metros) do chão sob (x, z), procurando de baixo do pé para baixo: o que estiver acima da cabeça (a copa) não conta */
function chao(wx: number, wz: number, yPe: number): number {
  const x = Math.floor(wx / S + N / 2), z = Math.floor(wz / S + N / 2);
  for (let y = Math.floor(yPe / S + 0.01) + 1; y >= 0; y--) if (solido(x, y, z)) return (y + 1) * S;
  return 0;
}

/* ---------- o personagem ---------- */
const heroi = new Heroi();
heroi.raiz.scale.setScalar(1.3);
cena.add(heroi.raiz);
/* o começo: a coluna de grama mais perto do centro */
let px = 0, pz = 0;
for (let r = 0; r < N / 2; r++) {
  const x = Math.floor(N / 2 + r), z = Math.floor(N / 2 + r / 2), h = ALT(x, z);
  if (h > AGUA + 1 && !soltos.has(chave(x, h, z))) { px = (x - N / 2 + 0.5) * S; pz = (z - N / 2 + 0.5) * S; break; }
}
let py = ALT(Math.floor(px / S + N / 2), Math.floor(pz / S + N / 2)) * S, vy = 0;   // no chão, não na copa de cima
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

/* ---------- o painel ---------- */
const inSemente = document.getElementById("semente") as HTMLInputElement;
inSemente.value = String(SEMENTE);
document.getElementById("gerar")!.addEventListener("click", () => { location.search = `?semente=${Math.max(1, Math.floor(Number(inSemente.value) || 1))}`; });
const chkRealce = document.getElementById("realce") as HTMLInputElement;
const chkLivre = document.getElementById("livre") as HTMLInputElement;

/* ---------- a câmera ---------- */
const orbita = new OrbitControls(camera, tela);
orbita.enableDamping = true;
orbita.maxPolarAngle = 1.45;
orbita.minDistance = 4;
orbita.maxDistance = 220;
orbita.target.set(px, py + 1, pz);
camera.position.set(px - 4, py + 10, pz + 18);
(window as unknown as { voxel: object }).voxel = { heroi, cena, camera, orbita, chao, ir: (x: number, z: number) => { px = x; pz = z; py = chao(x, z, ALTO * S); } };

/* ---------- a entrada ---------- */
const teclas = new Set<string>();
let pedePulo = false;
addEventListener("keydown", e => {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLSelectElement) return;
  if (e.code === "Space") { pedePulo = true; e.preventDefault(); }
  teclas.add(e.code);
});
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

/* ---------- o pós-processamento (o mesmo da ilha da floresta) ---------- */
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: 4 }));
composer.addPass(new RenderPass(cena, camera));
const ao = new GTAOPass(cena, camera, 1, 1);
ao.updateGtaoMaterial({ radius: 1.0, distanceExponent: 1.5, thickness: 1.2, scale: 1.0, samples: 16 });
ao.blendIntensity = 0.7;
composer.addPass(ao);
composer.addPass(new UnrealBloomPass(new THREE.Vector2(1, 1), 0.2, 0.5, 0.92));
composer.addPass(new OutputPass());

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

const LIMITE = (N / 2 - 2) * S;
let antes = performance.now(), quadros = 0, tFps = antes;
const fps = document.getElementById("fps")!;
function quadro(agora: number): void {
  const dt = Math.min(0.05, (agora - antes) / 1000);
  antes = agora;
  const d = direcao(), vel = d.correr ? CORRIDA : VELOCIDADE;
  const frente = new THREE.Vector3().subVectors(orbita.target, camera.position).setY(0).normalize();
  const direita = new THREE.Vector3(-frente.z, 0, frente.x);
  const andando = d.x !== 0 || d.z !== 0;
  if (andando) {
    const nx = px + (direita.x * d.x + frente.x * d.z) * vel * dt, nz = pz + (direita.z * d.x + frente.z * d.z) * vel * dt;
    /* sobe um cubo sozinho; mais que isso, só pulando */
    if (Math.abs(nx) < LIMITE && Math.abs(nz) < LIMITE && chao(nx, nz, py + S * 1.05) - py <= S * 1.05) { px = nx; pz = nz; }
  }
  if (pedePulo && vy === 0 && chao(px, pz, py) >= py - 0.01) vy = PULO;
  pedePulo = false;
  vy -= GRAVIDADE * dt;
  const piso = chao(px, pz, py + S * 1.05);
  py += vy * dt;
  if (py <= piso) { py = piso > py + S * 1.1 ? py : piso; vy = 0; }
  /* o degrau: quem anda para cima de um cubo sobe suave */
  if (piso > py && piso - py <= S * 1.05) py += Math.min(piso - py, dt * 6);
  heroi.atualizar(px, py, pz, d.x, andando && vy === 0, agora, dt, d.correr);
  heroi.raiz.rotation.y = Math.atan2(camera.position.x - px, camera.position.z - pz);
  if (!chkLivre.checked) {
    const alvo = new THREE.Vector3(px, py + 1, pz), delta = alvo.clone().sub(orbita.target).multiplyScalar(1 - Math.exp(-dt * 6));
    orbita.target.add(delta);
    camera.position.add(delta);
  }
  orbita.update();
  CURVA.uTempo.value = agora / 1000;
  redimensionar();
  if (chkRealce.checked) composer.render();
  else renderer.render(cena, camera);
  quadros++;
  if (agora - tFps > 1000) { fps.textContent = `${Math.round((quadros * 1000) / (agora - tFps))} fps · ${(idx.length / 6 / 1000).toFixed(0)} mil faces`; quadros = 0; tFps = agora; }
  requestAnimationFrame(quadro);
}
requestAnimationFrame(quadro);
