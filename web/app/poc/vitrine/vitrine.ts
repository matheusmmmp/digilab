/* A vitrine dos objetos do mapa (o planejamento da melhora dos objetos, pedido do Matheus em 2026-11-07): cada modelo sozinho, no estilo
   Digital (o toon de dois tons e o traco de nanquim do pos.ts), de tres quartos pela frente e de lado, num fundo neutro. So ferramenta de
   olhar: nada do jogo muda. Quando acaba, poe data-pronto="1" no body (a captura do Playwright espera por ele). */
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { CURVA, carregarVariante, usarDoisTons } from "../../src/telas/pet/ilha/cena.ts";
import { CONTORNO_DIGITAL, DIGITAL } from "../../src/telas/pet/ilha/constantes.ts";
import { ENFEITES_MODELOS, ITENS_MODELOS, LUGARES_MODELOS, MODELOS, type Modelo } from "../../src/telas/pet/ilha/modelos.ts";
import { Pos, PRESETS } from "../../src/telas/pet/ilha/pos.ts";

interface Item { grupo: string; nome: string; url: string; modelo: Modelo }
const base = document.baseURI.replace(/poc\/.*$/, "");
const itens: Item[] = [];
for (const [n, m] of Object.entries(LUGARES_MODELOS)) itens.push({ grupo: "Lugares", nome: n, url: "lugares/" + m.arquivos[0], modelo: m });
for (const [n, m] of Object.entries(ENFEITES_MODELOS)) itens.push({ grupo: "Enfeites", nome: n, url: "enfeites/" + m.arquivos[0], modelo: m });
itens.push({ grupo: "Enfeites", nome: "lata", url: DIGITAL.lata.arquivo, modelo: { arquivos: [DIGITAL.lata.arquivo], altura: 4, vento: 0, sombra: 0, baixo: false } });
for (const [n, m] of Object.entries(ITENS_MODELOS)) itens.push({ grupo: "Itens", nome: n, url: "itens/" + m.arquivos[0], modelo: m });
for (const [n, m] of Object.entries(MODELOS)) for (const a of m.arquivos) itens.push({ grupo: "Kits da natureza (Digital)", nome: `${n} · ${a.split("/").pop()!.replace(/\.gl(tf|b)$/, "")}`, url: "kits3d_digital/" + a, modelo: m });

const L = 600;
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(L, L, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const pos = new Pos(renderer);
usarDoisTons(true);
CURVA.uCurva.value = 0;
const cena = new THREE.Scene();
cena.background = new THREE.Color(0xdfe7ee);
const hemi = new THREE.HemisphereLight(0xffffff, 0x6f8fc8, 1.6), sol = new THREE.DirectionalLight(0xffffff, 2.2);
sol.position.set(-0.6, 1, 0.75);
cena.add(hemi, sol);
const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 200);
const gltf = new GLTFLoader(), raiz = document.getElementById("vitrine")!;

/** desenha o grupo de dois angulos (tres quartos pela frente e de lado) e devolve as duas imagens */
function fotos(g: THREE.Object3D): string[] {
  const caixa = new THREE.Box3().setFromObject(g), c = caixa.getCenter(new THREE.Vector3()), r = caixa.getBoundingSphere(new THREE.Sphere()).radius;
  const d = r / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.05;
  const out: string[] = [];
  for (const ang of [Math.PI * 0.18, Math.PI * 0.5]) {
    camera.position.set(c.x + Math.sin(ang) * d * 0.94, c.y + d * 0.34, c.z + Math.cos(ang) * d * 0.94);
    camera.lookAt(c);
    camera.near = d / 50; camera.far = d * 4; camera.updateProjectionMatrix();
    pos.desenhar(cena, camera, PRESETS.normal, 0.5, { ...CONTORNO_DIGITAL, some: [d * 3, d * 4] });
    out.push(renderer.domElement.toDataURL("image/png"));
  }
  return out;
}

let grupoAtual = "", grade: HTMLElement | null = null;
for (const it of itens) {
  if (it.grupo !== grupoAtual) {
    grupoAtual = it.grupo;
    const h = document.createElement("h2"); h.textContent = it.grupo; raiz.append(h);
    grade = document.createElement("div"); grade.className = "grade"; raiz.append(grade);
  }
  const fig = document.createElement("figure"), leg = document.createElement("figcaption");
  try {
    const { pecas } = await carregarVariante(gltf, new URL(it.url, base).href, it.modelo);
    const g = new THREE.Group();
    for (const p of pecas) { const m = new THREE.Mesh(p.geo, p.mat); m.matrixAutoUpdate = false; m.matrix.copy(p.local); g.add(m); }
    g.updateMatrixWorld(true);
    cena.add(g);
    for (const src of fotos(g)) { const img = document.createElement("img"); img.src = src; fig.append(img); }
    cena.remove(g);
    const tri = pecas.reduce((s, p) => s + (p.geo.index ? p.geo.index.count : p.geo.getAttribute("position").count) / 3, 0);
    leg.textContent = `${it.nome} — ${Math.round(tri)} triângulos`;
  } catch (e) {
    leg.textContent = `${it.nome} — não carregou: ${(e as Error).message}`;
  }
  fig.append(leg);
  grade!.append(fig);
}
document.body.setAttribute("data-pronto", "1");
