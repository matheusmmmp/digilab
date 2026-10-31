/* A página do mapa no estilo Animal Crossing (poc/mapa_ac.html): monta a cena, carrega os kits e o personagem, e anda. Protótipo de vista,
   fora do jogo e do motor: o andar é contínuo e em ponto flutuante, sem log (não decide nada do pet).
     - teclado: WASD ou setas, relativos à câmera; Shift corre; F golpeia (com o pet 3D);
     - mouse: arrastar gira a câmera em volta do personagem (360° de lado, inclinação limitada), a roda aproxima e afasta;
     - toque: arrastar a partir de qualquer ponto é o direcional;
     - o painel: o Digimon, a dobra do mundo, o lado do desenho, o pet 3D, os clipes e o golpe. */
import * as THREE from "three";
import { CURVA, COR_HORIZONTE, montarCena, objetos } from "./cena.ts";
import { Heroi } from "./heroi.ts";
import { Pet3D } from "./pet3d.ts";
import { Projeteis } from "./projetil.ts";
import { ALTURA_NIVEL, LARG, Mapa, PROF } from "./mapa.ts";

const VELOCIDADE = 3.6, CORRIDA = 6.2;                  // células por segundo
/* a câmera em órbita: o giro (0 = atrás, olhando para o norte), a inclinação e a distância ao ponto que ela olha; o começo é a vista
   de antes (deslocamento (0; 8,4; 14,5) e olhar (0; 0,6; -3,2) em relação ao personagem) */
const ORBITA = { giro: 0, inclina: Math.atan2(7.8, 17.7), dist: Math.hypot(7.8, 17.7) };
const DIST0 = ORBITA.dist;
const INCLINA_MIN = 0.12, INCLINA_MAX = 1.35, DIST_MIN = 2.5, DIST_MAX = 40;
const GIRO_POR_PX = 0.008;                              // radianos por pixel de arrasto
const OLHAR_ALTO = 0.6, OLHAR_FRENTE = 3.2;             // o ponto olhado: um pouco acima e à frente do personagem (escala com a distância)
const SPRITE_PADRAO = "brasa_crianca_sereno";

const tela = document.getElementById("tela") as HTMLCanvasElement;
const estado = document.getElementById("estado")!;
const mapa = new Mapa();
const cena = montarCena(mapa);
const renderer = new THREE.WebGLRenderer({ canvas: tela, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(COR_HORIZONTE);
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 200);

const heroi = new Heroi();
cena.add(heroi.raiz);
let px = mapa.inicio[0], pz = mapa.inicio[1], py = mapa.altura(px, pz);
/* para conferir no console: levar o personagem a um ponto (em células) */
const projeteis = new Projeteis(mapa);
cena.add(projeteis.raiz);
(window as unknown as { mapaAC: object }).mapaAC = { heroi, cena, mapa, pet3d: () => pet3d, ORBITA, projeteis, ir: (x: number, z: number) => { px = x; pz = z; py = mapa.altura(x, z); } };
const camAlvo = new THREE.Vector3(px, py, pz);

/* ---------- o painel ---------- */
const selSprite = document.getElementById("sprite") as HTMLSelectElement;
const curva = document.getElementById("curva") as HTMLInputElement;
const lado = document.getElementById("lado") as HTMLInputElement;
curva.value = String(CURVA.uCurva.value * 1000);
curva.addEventListener("input", () => { CURVA.uCurva.value = Number(curva.value) / 1000; });
lado.addEventListener("change", () => { heroi.desenhoOlhaEsquerda = lado.checked; });

(async () => {
  const fonte = await Heroi.listar();
  if (!fonte) { selSprite.innerHTML = "<option>reserva (sem o atlas)</option>"; selSprite.disabled = true; return; }
  const nomes = Object.entries(fonte.atlas.sprites).filter(([, s]) => s.clipes?.Idle && s.clipes?.Run).map(([n, s]) => [n, s.digimon] as const);
  selSprite.innerHTML = nomes.map(([n, d]) => `<option value="${n}">${d} · ${n}</option>`).join("");
  const usar = (n: string) => { heroi.usarSprite(fonte, n); lado.checked = heroi.desenhoOlhaEsquerda; };
  selSprite.value = nomes.some(([n]) => n === SPRITE_PADRAO) ? SPRITE_PADRAO : nomes[0][0];
  usar(selSprite.value);
  selSprite.addEventListener("change", () => usar(selSprite.value));
})();

/* o pet como modelo 3D (fora do repositório, em Assets/kits3d/); "papel" volta ao recorte do atlas */
const MODELOS_3D: Record<string, string> = {
  "Agumon (DSTS, dsts-extractor)": "./Assets/kits3d/dsts/agumon.glb",
  "Mushnub (Quaternius, CC0)": "./Assets/kits3d/quaternius_monstros/Mushnub.glb",
};
const selModelo = document.getElementById("modelo3d") as HTMLSelectElement;
const selParado = document.getElementById("clipeParado") as HTMLSelectElement;
const selAndando = document.getElementById("clipeAndando") as HTMLSelectElement;
selModelo.innerHTML += Object.keys(MODELOS_3D).map(n => `<option>${n}</option>`).join("");
let pet3d: Pet3D | null = null;
selModelo.addEventListener("change", async () => {
  if (pet3d) cena.remove(pet3d.raiz);
  pet3d = null;
  heroi.raiz.visible = !selModelo.value;
  for (const s of [selParado, selAndando, selGolpe]) { s.innerHTML = ""; s.disabled = true; }
  btnGolpe.disabled = true;
  if (!selModelo.value) return;
  const novo = new Pet3D(), url = MODELOS_3D[selModelo.value];
  let clipes: string[];
  try { clipes = await novo.carregar(url); } catch (e) { console.error("modelo 3D não carregou:", url, e); estado.textContent = "o modelo 3D não carregou (ver o console)"; return; }
  for (const s of [selParado, selAndando]) { s.innerHTML = clipes.map(c => `<option>${c}</option>`).join(""); s.disabled = false; }
  /* o parado e o andar pelo nome do clipe: Idle e Walk nos pacotes do Quaternius; no DSTS, bn01 (parado) e br01 (correr; o Agumon não
     tem andar de campo, fw01_01), pela tabela de nomes do dsts-viewer (data/animation_names.json) */
  const achar = (re: RegExp) => clipes.find(c => re.test(c)) ?? clipes[0];
  novo.clipeParado = selParado.value = achar(/idle|_bn01$/i);
  novo.clipeAndando = selAndando.value = achar(/walk|_fw01_01$|_br01$/i);
  const golpes = novo.golpesDisponiveis();
  selGolpe.innerHTML = golpes.map(g => `<option value="${g.codigo}">${g.nome} (${g.codigo})</option>`).join("");
  selGolpe.disabled = btnGolpe.disabled = golpes.length === 0;
  novo.aoDisparar = (boca, frente) => projeteis.disparar(boca, frente);
  pet3d = novo;
  cena.add(novo.raiz);
});
selParado.addEventListener("change", () => { if (pet3d) pet3d.clipeParado = selParado.value; });
selAndando.addEventListener("change", () => { if (pet3d) pet3d.clipeAndando = selAndando.value; });
/* o golpe: o botão e o F tocam o escolhido; cada golpe dado passa a escolha para o próximo da lista */
const selGolpe = document.getElementById("golpeSel") as HTMLSelectElement;
const btnGolpe = document.getElementById("golpe") as HTMLButtonElement;
function golpear(): void {
  if (!pet3d || !selGolpe.value || !pet3d.golpear(selGolpe.value)) return;
  selGolpe.selectedIndex = (selGolpe.selectedIndex + 1) % selGolpe.options.length;
}
btnGolpe.addEventListener("click", () => { golpear(); btnGolpe.blur(); });

(async () => {
  const { grupo, faltas } = await objetos(mapa, (f, t) => { estado.textContent = `carregando os kits ${f}/${t}`; });
  cena.add(grupo);
  estado.textContent = faltas.length ? `faltaram ${faltas.length} modelos (ver o console)` : "";
  for (const f of faltas) console.error("modelo não carregou:", f);
})();

/* ---------- a entrada ---------- */
const teclas = new Set<string>();
addEventListener("keydown", e => {
  teclas.add(e.code);
  if (e.code.startsWith("Arrow")) e.preventDefault();
  if (e.code === "KeyF" && !e.repeat && !(e.target instanceof HTMLSelectElement)) golpear();
});
addEventListener("keyup", e => teclas.delete(e.code));
addEventListener("blur", () => teclas.clear());
/* o toque é o direcional; o mouse gira a câmera */
let arrasto: { x0: number; y0: number; dx: number; dy: number } | null = null;
let giroMouse: { x: number; y: number } | null = null;
tela.addEventListener("pointerdown", e => {
  tela.setPointerCapture(e.pointerId);
  if (e.pointerType === "mouse") giroMouse = { x: e.clientX, y: e.clientY };
  else arrasto = { x0: e.clientX, y0: e.clientY, dx: 0, dy: 0 };
});
tela.addEventListener("pointermove", e => {
  if (giroMouse) {
    ORBITA.giro -= (e.clientX - giroMouse.x) * GIRO_POR_PX;
    ORBITA.inclina = Math.min(INCLINA_MAX, Math.max(INCLINA_MIN, ORBITA.inclina + (e.clientY - giroMouse.y) * GIRO_POR_PX));
    giroMouse = { x: e.clientX, y: e.clientY };
  }
  if (arrasto) { arrasto.dx = e.clientX - arrasto.x0; arrasto.dy = e.clientY - arrasto.y0; }
});
const soltar = () => { arrasto = null; giroMouse = null; };
tela.addEventListener("pointerup", soltar);
tela.addEventListener("pointercancel", soltar);
tela.addEventListener("wheel", e => {
  e.preventDefault();
  ORBITA.dist = Math.min(DIST_MAX, Math.max(DIST_MIN, ORBITA.dist * Math.exp(e.deltaY * 0.001)));
}, { passive: false });

/** a direção de andar no mundo: a entrada (x à direita, z para trás na tela) girada pelo giro da câmera */
function direcao(): { x: number; z: number; correr: boolean } {
  let x = 0, z = 0;
  if (teclas.has("KeyA") || teclas.has("ArrowLeft")) x -= 1;
  if (teclas.has("KeyD") || teclas.has("ArrowRight")) x += 1;
  if (teclas.has("KeyW") || teclas.has("ArrowUp")) z -= 1;
  if (teclas.has("KeyS") || teclas.has("ArrowDown")) z += 1;
  let correr = teclas.has("ShiftLeft") || teclas.has("ShiftRight");
  if (arrasto && Math.hypot(arrasto.dx, arrasto.dy) > 12) {
    x = arrasto.dx; z = arrasto.dy;
    correr = Math.hypot(arrasto.dx, arrasto.dy) > 110;
  }
  const n = Math.hypot(x, z);
  if (n === 0) return { x: 0, z: 0, correr: false };
  const c = Math.cos(ORBITA.giro), s = Math.sin(ORBITA.giro);
  return { x: (x * c + z * s) / n, z: (-x * s + z * c) / n, correr };
}

/* ---------- o minimapa ---------- */
const mini = document.getElementById("mini") as HTMLCanvasElement;
const ESC_MINI = 3;
mini.width = LARG * ESC_MINI; mini.height = PROF * ESC_MINI;
const fundoMini = (() => {
  const c = document.createElement("canvas");
  c.width = mini.width; c.height = mini.height;
  const g = c.getContext("2d")!;
  for (let z = 0; z < PROF; z++) for (let x = 0; x < LARG; x++) {
    const k = mapa.cel(x, z)!;
    g.fillStyle = k.tipo === "agua" ? "#6cc6e8" : k.tipo === "areia" ? "#f1e2b2" : k.tipo === "caminho" ? "#d8c08e"
      : ["#86c86a", "#6fb05a", "#5c9a4c"][Math.max(0, Math.min(2, Math.round(k.cantos[0] / ALTURA_NIVEL)))];
    g.fillRect(x * ESC_MINI, z * ESC_MINI, ESC_MINI, ESC_MINI);
  }
  g.fillStyle = "rgba(40,90,40,0.55)";
  for (const o of mapa.objetos) if (o.modelo === "arvore_redonda" || o.modelo === "pinheiro") g.fillRect(o.x * ESC_MINI - 1, o.z * ESC_MINI - 1, 3, 3);
  return c;
})();
function desenharMini(): void {
  const g = mini.getContext("2d")!;
  g.drawImage(fundoMini, 0, 0);
  g.fillStyle = "#f07a2a"; g.strokeStyle = "#fff"; g.lineWidth = 1.5;
  g.beginPath(); g.arc(px * ESC_MINI, pz * ESC_MINI, 4, 0, Math.PI * 2); g.fill(); g.stroke();
}

/* ---------- o relógio ---------- */
const hora = document.getElementById("hora")!, dia = document.getElementById("dia")!;
function relogio(): void {
  const d = new Date();
  hora.textContent = d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  dia.textContent = d.toLocaleDateString("pt-BR", { weekday: "short", day: "numeric", month: "short" });
}
relogio();
setInterval(relogio, 10_000);

/* ---------- o laço ---------- */
function redimensionar(): void {
  const w = tela.clientWidth, h = tela.clientHeight;
  if (tela.width !== Math.round(w * renderer.getPixelRatio()) || tela.height !== Math.round(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}

let antes = performance.now(), quadros = 0, tFps = antes;
const fps = document.getElementById("fps")!;
function quadro(agora: number): void {
  const dt = Math.min(0.05, (agora - antes) / 1000);
  antes = agora;
  const d = direcao(), vel = d.correr ? CORRIDA : VELOCIDADE;
  const andando = (d.x !== 0 || d.z !== 0) && !pet3d?.golpeando;   // parado enquanto golpeia
  if (andando) {
    /* anda em x e em z separado, para deslizar ao longo do penhasco e da água */
    const nx = px + d.x * vel * dt, nz = pz + d.z * vel * dt;
    if (mapa.livre(nx, pz, py)) { px = nx; py = mapa.altura(px, pz); }
    if (mapa.livre(px, nz, py)) { pz = nz; py = mapa.altura(px, pz); }
  }
  heroi.atualizar(px, py, pz, d.x, andando, agora, dt, d.correr);
  pet3d?.atualizar(px, py, pz, d.x, d.z, andando, dt, d.correr);
  projeteis.atualizar(dt);
  camAlvo.lerp(new THREE.Vector3(px, py, pz), 1 - Math.exp(-dt * 6));
  /* o ponto olhado (acima e à frente, na direção do giro) e a câmera em volta dele */
  const c = Math.cos(ORBITA.giro), s = Math.sin(ORBITA.giro), frente = OLHAR_FRENTE * ORBITA.dist / DIST0;
  const olhar = camAlvo.clone().add(new THREE.Vector3(-s * frente, OLHAR_ALTO, -c * frente));
  const ch = Math.cos(ORBITA.inclina) * ORBITA.dist;
  camera.position.copy(olhar).add(new THREE.Vector3(s * ch, Math.sin(ORBITA.inclina) * ORBITA.dist, c * ch));
  camera.lookAt(olhar);
  CURVA.uFocoZ.value = camAlvo.z;
  CURVA.uTempo.value = agora / 1000;
  redimensionar();
  renderer.render(cena, camera);
  desenharMini();
  quadros++;
  if (agora - tFps > 1000) { fps.textContent = `${Math.round((quadros * 1000) / (agora - tFps))} fps · ${renderer.info.render.calls} draw calls`; quadros = 0; tFps = agora; }
  requestAnimationFrame(quadro);
}
requestAnimationFrame(quadro);
