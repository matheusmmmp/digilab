/* O campo visto de lado (poc/lateral.html): o mundo 3D com o Digimon em sprite 2D, na composição de um campo de RPG lateral. Protótipo de
   vista, fora do jogo e do motor; reaproveita o personagem (heroi.ts) e os kits CC0 do mapa_ac, sem a dobra do mundo.
     - a câmera de lado, um pouco de cima, com campo de visão estreito (quase ortográfica) e seguindo o personagem só em x;
     - as camadas em profundidade: céu e nuvens, três faixas de morros que somem na névoa, árvores no meio, o caminho, o capim alto na
       frente (que encobre os pés) e a borda do penhasco;
     - um bloco flutuante que pula quando o personagem bate nele por baixo.
   Todos os números são do desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { FBXLoader } from "three/examples/jsm/loaders/FBXLoader.js";
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
/* desenhadas em alta resolução e lidas com filtro (linear + anisotrópico): o chão em alta definição */
function canvasTex(w: number, h: number, desenhar: (g: CanvasRenderingContext2D) => void, repetir = false): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  desenhar(c.getContext("2d")!);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  if (repetir) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

/* um traço que dá a volta na borda do ladrilho (desenhado de novo deslocado), para o ladrilho repetir sem emenda */
function emTodaVolta(w: number, h: number, x: number, y: number, f: (x: number, y: number) => void): void {
  for (const dx of [-w, 0, w]) for (const dy of [-h, 0, h]) f(x + dx, y + dy);
}

/* a grama do chão: um ladrilho de 256 x 256 com manchas suaves e folhinhas em dois tons */
const TEX_GRAMA = canvasTex(256, 256, g => {
  const r = rng(7);
  g.fillStyle = "#74c455"; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 14; i++) {
    const x = r() * 256, y = r() * 256, raio = 30 + r() * 50, cor = r() < 0.5 ? "rgba(95,174,70,0.35)" : "rgba(143,214,106,0.35)";
    emTodaVolta(256, 256, x, y, (a, b) => { const gr = g.createRadialGradient(a, b, 0, a, b, raio); gr.addColorStop(0, cor); gr.addColorStop(1, "rgba(0,0,0,0)"); g.fillStyle = gr; g.fillRect(a - raio, b - raio, raio * 2, raio * 2); });
  }
  g.lineCap = "round";
  for (let i = 0; i < 260; i++) {
    const x = r() * 256, y = r() * 256, alt = 4 + r() * 7, inc = (r() - 0.5) * 4;
    g.strokeStyle = r() < 0.5 ? "#5aa843" : "#93d96e"; g.lineWidth = 1.4;
    emTodaVolta(256, 256, x, y, (a, b) => { g.beginPath(); g.moveTo(a, b); g.lineTo(a + inc, b - alt); g.stroke(); });
  }
}, true);

/* a face do penhasco: faixas de estrato onduladas em tons de terra, rachaduras e a grama pendendo no alto (512 x 512 por 3 de largura) */
const TEX_PENHASCO = canvasTex(512, 512, g => {
  const r = rng(3);
  const faixas = ["#c9a46a", "#b58b55", "#d4b27a", "#a77d4b", "#bf9660"];
  const fase = r() * 6;
  let y = 30;
  for (let i = 0; y < 512; i++) {
    const h = 40 + r() * 50, amp = 3 + r() * 5;
    g.fillStyle = faixas[i % faixas.length];
    g.beginPath(); g.moveTo(0, y + Math.sin(fase + i) * amp);
    for (let x = 0; x <= 512; x += 8) g.lineTo(x, y + Math.sin(fase + i + (x / 512) * Math.PI * 2) * amp);
    g.lineTo(512, 512); g.lineTo(0, 512); g.fill();
    y += h;
  }
  g.strokeStyle = "rgba(110,75,40,0.45)"; g.lineWidth = 2.5; g.lineCap = "round";
  for (let i = 0; i < 30; i++) {
    const x = r() * 512, yy = 60 + r() * 440, c = 14 + r() * 30;
    emTodaVolta(512, 0, x, yy, (a, b) => { g.beginPath(); g.moveTo(a, b); g.quadraticCurveTo(a + c / 2, b + 3 - r() * 6, a + c, b + 1); g.stroke(); });
  }
  /* a grama que pende do alto, em gotas arredondadas */
  g.fillStyle = "#5fb84a";
  g.fillRect(0, 0, 512, 26);
  for (let x = 0; x < 512; x += 16) {
    const alt = 10 + r() * 22;
    emTodaVolta(512, 0, x + 8, 26, (a, b) => { g.beginPath(); g.ellipse(a, b, 10, alt, 0, 0, Math.PI); g.fill(); });
  }
  g.fillStyle = "rgba(255,255,255,0.18)"; g.fillRect(0, 0, 512, 6);
}, true);

/* o caminho de terra clara, com a borda ondulada e pedrinhas (512 x 128 por 3,4 de largura) */
const TEX_CAMINHO = canvasTex(512, 128, g => {
  const r = rng(5);
  const borda = (base: number, amp: number) => Array.from({ length: 33 }, (_, k) => base + (k === 0 || k === 32 ? 0 : (r() - 0.5) * amp));
  const cima = borda(14, 10), baixo = borda(114, 10);
  g.fillStyle = "#ead293";
  g.beginPath(); g.moveTo(0, cima[0]);
  for (let k = 1; k <= 32; k++) g.quadraticCurveTo((k - 0.5) * 16, (cima[k - 1] + cima[k]) / 2, k * 16, cima[k]);
  g.lineTo(512, baixo[32]);
  for (let k = 31; k >= 0; k--) g.quadraticCurveTo((k + 0.5) * 16, (baixo[k + 1] + baixo[k]) / 2, k * 16, baixo[k]);
  g.fill();
  for (let i = 0; i < 70; i++) {
    const x = r() * 512, y = 26 + r() * 76, raio = 1.5 + r() * 3.5;
    g.fillStyle = r() < 0.6 ? "rgba(196,165,100,0.75)" : "rgba(255,244,205,0.8)";
    emTodaVolta(512, 0, x, y, (a, b) => { g.beginPath(); g.ellipse(a, b, raio * 1.4, raio, 0, 0, Math.PI * 2); g.fill(); });
  }
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
/* o kit da cena: "tff" (RPG Tiny Fantasy Forest, Dungeon Mason, fora do repositório) ou "quaternius" (os CC0 do mapa_ac), pelo ?kit= */
const KIT_CENA = new URLSearchParams(location.search).get("kit") === "quaternius" ? "quaternius" : "tff";
const TFF = "./Assets/kits3d/tiny_fantasy_forest/x/Assets/RPG Tiny Fantasy Forest PBR/";
const MESH = TFF + "Mesh/";
/* o kit inteiro pinta com uma paleta só (o "Base Map": quadrados de cor em que cada face cai), lida sem filtro */
const TEX_TFF = (() => {
  const t = new THREE.TextureLoader().load(TFF + "Texture/Base Map.png");
  t.colorSpace = THREE.SRGBColorSpace;
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  return t;
})();

/* um FBX do kit, normalizado como o carregarVariante do mapa_ac: o pé no chão, centrado em x e z, na altura pedida */
async function carregarFbx(loader: FBXLoader, url: string, altura: number, vento: number): Promise<Variante> {
  const raiz = await loader.loadAsync(url);
  /* o FBXLoader põe -90° em x na raiz (a conversão do z para cima), mas as malhas do kit já vêm com o y para cima: tira a rotação */
  raiz.rotation.set(0, 0, 0);
  raiz.updateMatrixWorld(true);
  const caixa = new THREE.Box3().setFromObject(raiz);
  const tam = caixa.getSize(new THREE.Vector3()), centro = caixa.getCenter(new THREE.Vector3());
  if (!(tam.y > 0)) throw new Error(`modelo sem altura: ${url}`);
  const s = altura / tam.y;
  const norm = new THREE.Matrix4().makeScale(s, s, s).multiply(new THREE.Matrix4().makeTranslation(-centro.x, -caixa.min.y, -centro.z));
  const pecas: Variante["pecas"] = [];
  raiz.traverse(o => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh || /^LOD[1-9]/.test(mesh.name)) return;   // cada FBX traz LOD0 e LOD1 juntos; fica o LOD0
    pecas.push({ geo: mesh.geometry, mat: toon({ map: TEX_TFF }, vento), local: norm.clone().multiply(mesh.matrixWorld) });
  });
  if (!pecas.length) throw new Error(`FBX sem malha: ${url}`);
  return { pecas };
}

type Peca = { url: string; altura: number; vento: number; tinta?: number };
/* os FBX citam um "Albedo.png" que não vem no pacote; a cor é a do Base Map, aplicada depois, então o pedido vai para ele */
const GERENTE_FBX = new THREE.LoadingManager();
GERENTE_FBX.setURLModifier(u => u.endsWith("/Albedo.png") ? TFF + "Texture/Base Map.png" : u);
const LOADERS = { gltf: new GLTFLoader(), fbx: new FBXLoader(GERENTE_FBX) };
async function instanciar(p: Peca, lugares: { x: number; z: number; s: number; giro: number }[]): Promise<THREE.Object3D[]> {
  const modelo: Modelo = { arquivos: [p.url], altura: p.altura, vento: p.vento, sombra: 0 };
  const v: Variante = p.url.toLowerCase().endsWith(".fbx") ? await carregarFbx(LOADERS.fbx, p.url, p.altura, p.vento)
    : await carregarVariante(LOADERS.gltf, p.url, modelo);
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

type Pedido = [Peca, ReturnType<typeof espalhar>, number];   // a peça, onde ela fica e o raio da sombra (0 = sem sombra)

/* o campo com o RPG Tiny Fantasy Forest: a mesma composição, com as árvores, montanhas, pedras, capim e flores do kit */
const PEDIDOS_TFF: Pedido[] = [
  [{ url: MESH + "TreePlants/Tree02.fbx", altura: 6, vento: 0.003 }, [{ x: -5.5, z: -5, s: 1, giro: 0.4 }], 2],
  [{ url: MESH + "TreePlants/Tree02.fbx", altura: 5, vento: 0.003 }, [{ x: 14, z: -6, s: 1, giro: 1 }, { x: -19, z: -7, s: 1.1, giro: 2 }], 1.8],
  [{ url: MESH + "TreePlants/Tree02.fbx", altura: 4.5, vento: 0.003 }, espalhar(21, 18, -14, -9, 0.7, 1.3), 0],
  [{ url: MESH + "Mountains/RockMountain01.fbx", altura: 6, vento: 0 }, [{ x: -26, z: -42, s: 1, giro: 0 }, { x: 30, z: -44, s: 1.2, giro: 2 }], 0],
  [{ url: MESH + "Mountains/RockMountain03.fbx", altura: 5, vento: 0 }, [{ x: 6, z: -40, s: 1, giro: 1 }], 0],
  [{ url: MESH + "BuildingUtilityDeco/TreeStump01.fbx", altura: 0.6, vento: 0 }, [{ x: 8, z: -2.4, s: 1, giro: 0.5 }, { x: -15, z: -3, s: 0.8, giro: 2 }], 0.5],
  [{ url: MESH + "BuildingUtilityDeco/Gate01.fbx", altura: 2.6, vento: 0 }, [{ x: 18, z: -2.6, s: 1, giro: 0 }], 0],
  [{ url: MESH + "Rock/Rock01.fbx", altura: 0.8, vento: 0 }, [{ x: 10, z: -2.2, s: 1, giro: 0 }, { x: -24, z: -2.5, s: 1.2, giro: 1 }], 0.5],
  [{ url: MESH + "Rock/Rock04.fbx", altura: 0.6, vento: 0 }, [{ x: -9, z: 2.3, s: 1, giro: 2 }, { x: 22, z: 2.2, s: 0.9, giro: 0 }], 0.4],
  [{ url: MESH + "Rock/Cobble01.fbx", altura: 0.12, vento: 0 }, espalhar(51, 30, -1.1, 1.3, 0.7, 1.3), 0],
  [{ url: MESH + "Rock/Cobble03.fbx", altura: 0.12, vento: 0 }, espalhar(52, 30, -1.1, 1.3, 0.7, 1.3), 0],
  [{ url: MESH + "TreePlants/Flower01.fbx", altura: 0.3, vento: 0.06 }, espalhar(33, 35, -5, -1.8, 0.8, 1.3), 0],
  [{ url: MESH + "TreePlants/Grass01.fbx", altura: 0.25, vento: 0.08 }, espalhar(35, 110, -8, -1.4, 0.8, 1.4), 0],
  /* o capim alto na frente */
  [{ url: MESH + "TreePlants/Grass01.fbx", altura: 0.6, vento: 0.08 }, espalhar(41, 120, 1.7, 2.9, 0.8, 1.3), 0],
  [{ url: MESH + "TreePlants/Grass01.fbx", altura: 0.55, vento: 0.08, tinta: 0xffe27a }, espalhar(42, 60, 1.8, 2.9, 0.8, 1.3), 0],
];

async function povoar(): Promise<string[]> {
  const faltas: string[] = [];
  const sombras: { x: number; z: number; r: number }[] = [];
  const pedidos: Pedido[] = KIT_CENA === "tff" ? PEDIDOS_TFF : [
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
      cena.add(...await instanciar(p, lugares));
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
const selKit = document.getElementById("kit") as HTMLSelectElement;
selKit.value = KIT_CENA;
selKit.addEventListener("change", () => { location.search = selKit.value === "tff" ? "" : `?kit=${selKit.value}`; });
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
