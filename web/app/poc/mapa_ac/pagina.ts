/* A página do mapa no estilo Animal Crossing (poc/mapa_ac.html): monta a cena, carrega os kits e o personagem, e anda. Protótipo de vista,
   fora do jogo e do motor: o andar é contínuo e em ponto flutuante, sem log (não decide nada do pet).
     - teclado: WASD ou setas; Shift corre;
     - ponteiro (mouse ou toque): arrastar a partir de qualquer ponto é o direcional;
     - o painel: o Digimon, a dobra do mundo e o lado do desenho. */
import * as THREE from "three";
import { CURVA, COR_HORIZONTE, montarCena, objetos } from "./cena.ts";
import { Heroi } from "./heroi.ts";
import { ALTURA_NIVEL, LARG, Mapa, PROF } from "./mapa.ts";

const VELOCIDADE = 3.6, CORRIDA = 6.2;                  // células por segundo
const CAMERA = new THREE.Vector3(0, 8.4, 14.5);          // o deslocamento da câmera em relação ao personagem
const OLHAR = new THREE.Vector3(0, 0.6, -3.2);           // para onde ela olha, em relação a ele
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
(window as unknown as { mapaAC: object }).mapaAC = { heroi, cena, mapa, ir: (x: number, z: number) => { px = x; pz = z; py = mapa.altura(x, z); } };
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

(async () => {
  const { grupo, faltas } = await objetos(mapa, (f, t) => { estado.textContent = `carregando os kits ${f}/${t}`; });
  cena.add(grupo);
  estado.textContent = faltas.length ? `faltaram ${faltas.length} modelos (ver o console)` : "";
  for (const f of faltas) console.error("modelo não carregou:", f);
})();

/* ---------- a entrada ---------- */
const teclas = new Set<string>();
addEventListener("keydown", e => { teclas.add(e.code); if (e.code.startsWith("Arrow")) e.preventDefault(); });
addEventListener("keyup", e => teclas.delete(e.code));
addEventListener("blur", () => teclas.clear());
let arrasto: { x0: number; y0: number; dx: number; dy: number } | null = null;
tela.addEventListener("pointerdown", e => { arrasto = { x0: e.clientX, y0: e.clientY, dx: 0, dy: 0 }; tela.setPointerCapture(e.pointerId); });
tela.addEventListener("pointermove", e => { if (arrasto) { arrasto.dx = e.clientX - arrasto.x0; arrasto.dy = e.clientY - arrasto.y0; } });
const soltar = () => { arrasto = null; };
tela.addEventListener("pointerup", soltar);
tela.addEventListener("pointercancel", soltar);

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
  return n > 0 ? { x: x / n, z: z / n, correr } : { x: 0, z: 0, correr: false };
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
  const andando = d.x !== 0 || d.z !== 0;
  if (andando) {
    /* anda em x e em z separado, para deslizar ao longo do penhasco e da água */
    const nx = px + d.x * vel * dt, nz = pz + d.z * vel * dt;
    if (mapa.livre(nx, pz, py)) { px = nx; py = mapa.altura(px, pz); }
    if (mapa.livre(px, nz, py)) { pz = nz; py = mapa.altura(px, pz); }
  }
  heroi.atualizar(px, py, pz, d.x, andando, agora, dt, d.correr);
  camAlvo.lerp(new THREE.Vector3(px, py, pz), 1 - Math.exp(-dt * 6));
  camera.position.copy(camAlvo).add(CAMERA);
  camera.lookAt(camAlvo.clone().add(OLHAR));
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
