/* A vista da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, H2): o modo mundo dos pets v12 numa ilha 3D no estilo Animal Crossing. So vista:
   le o Motor.mundo (jogoAtual), nunca escreve nele; a camera, a interpolacao, o vento e as animacoes ficam fora do log.
   - a ilha sai da grade (grade.ts) do layout do motor; a cena (cena.ts) a desenha, com o mundo curvo centrado no pet;
   - a camera em perspectiva segue a posicao desenhada do pet (o Seguidor de vistaMundo.ts) a uma distancia fixa (H-3); em retrato ela
     se afasta ate caber LARGURA_MIN celulas de lado a lado (constantes.ts);
   - o contrato CENA (cenaEstado.ts) fica igual: ret (o retangulo do pet em px de CSS, para o PalcoPet), medir (a M3), e mundo.paraMundo,
     paraTela e pet, que passam pela mesma dobra do shader (curva.ts, regra 6);
   - o dia e a noite do motor (eNoite) escurecem o ceu, a nevoa, a luz e a agua.
   Os kits carregam depois do terreno; se um modelo nao carrega, a cena cai na reserva (MundoReserva), com o erro no console. */
import * as THREE from "three";
import { TPD, eNoite, type Mundo } from "../../../../motor/index.ts";
import { jogoAtual } from "../../../jogo.ts";
import { CENA } from "../cenaEstado.ts";
import { fonteDoPet } from "../fontePet.ts";
import { Seguidor, dentroDoMapa, ninhoDe } from "../vistaMundo.ts";
import { AFASTAR_MAX, CAMERA_DESLOC, CAMERA_OLHAR, DOBRA_K, FOV_GRAUS, LARGURA_MIN, LONGE, NEVOA, PERTO, RAZAO_MAX, TEXEL_ALVO } from "./constantes.ts";
import { CURVA, montarCena, objetos, toon, type CenaIlha } from "./cena.ts";
import { paraMundoCel, paraTelaNdc, type CameraLida, type Dobra } from "./curva.ts";
import { ilhaDe, type Ilha } from "./grade.ts";

const movimentoReduzido = (): boolean => matchMedia("(prefers-reduced-motion: reduce)").matches;
type Ret = { x: number; y: number; w: number; h: number };

class VistaIlha {
  readonly renderer: THREE.WebGLRenderer;
  readonly camera = new THREE.PerspectiveCamera(FOV_GRAUS, 1, PERTO, LONGE);
  private readonly ilha: Ilha;
  private readonly cenaIlha: CenaIlha;
  private readonly seguidor = new Seguidor();
  private readonly raio = new THREE.Raycaster();
  private readonly lida: CameraLida;
  private readonly sprite: THREE.Sprite;
  private readonly comidas = new Map<number, THREE.Mesh>();
  private readonly bola: THREE.Mesh;
  private chave = "";
  private texels: [number, number] = [1, 1];
  private larguraCss = 1;
  private alturaCss = 1;
  private afast = 1;
  private noite: boolean | null = null;
  private ultimo = performance.now();
  private petCel: [number, number] = [0, 0];

  readonly canvas: HTMLCanvasElement;
  private readonly mu: Mundo;

  constructor(canvas: HTMLCanvasElement, mu: Mundo) {
    this.canvas = canvas; this.mu = mu;
    THREE.ColorManagement.enabled = true;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.ilha = ilhaDe(mu.cm);
    this.cenaIlha = montarCena(this.ilha);
    const v = new THREE.Vector3();
    this.lida = {
      projetar: (x, y, z) => { v.set(x, y, z).project(this.camera); return [v.x, v.y]; },
      raio: (nx, ny) => {
        this.raio.setFromCamera(new THREE.Vector2(nx, ny), this.camera);
        const { origin: o, direction: d } = this.raio.ray;
        return { o: [o.x, o.y, o.z], d: [d.x, d.y, d.z] };
      },
    };
    /* o ninho e o comedouro do layout; a bola e a racao entram e saem a cada quadro */
    const [nx, ny] = ninhoDe(mu.cm), sub = mu.cm.sub;
    const ninho = new THREE.Mesh(new THREE.CircleGeometry(1.2, 24).rotateX(-Math.PI / 2), toon({ color: 0xb98a55 }));
    ninho.position.set(nx / sub, 0.02, ny / sub);
    const comedouro = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.35, 0.75), toon({ color: 0xeef4fc }));
    comedouro.position.set(mu.comedouro[0] / sub, 0.18, mu.comedouro[1] / sub);
    this.bola = new THREE.Mesh(new THREE.SphereGeometry(0.38, 16, 12), toon({ color: 0x378add }));
    this.sprite = new THREE.Sprite(new THREE.SpriteMaterial({ alphaTest: 0.5, transparent: false }));
    this.sprite.center.set(0.5, 0);
    this.cenaIlha.cena.add(ninho, comedouro, this.bola, this.sprite);
  }

  /** os kits (public/kits3d) entram depois do terreno */
  async carregarObjetos(): Promise<void> {
    const o = await objetos(this.ilha, document.baseURI);
    this.cenaIlha.cena.add(o.grupo);
  }

  /** a dobra de agora: centrada no z desenhado do pet */
  private get dobra(): Dobra { return { k: DOBRA_K, focoZ: this.petCel[1] }; }

  /** ajusta o canvas a caixa (px de CSS): a resolucao, a proporcao e o afastamento da camera em retrato */
  ajustar(larguraCss: number, alturaCss: number): void {
    this.larguraCss = Math.max(1, larguraCss); this.alturaCss = Math.max(1, alturaCss);
    this.renderer.setPixelRatio(Math.min(RAZAO_MAX, devicePixelRatio || 1));
    this.renderer.setSize(this.larguraCss, this.alturaCss, false);
    this.canvas.style.width = `${this.larguraCss}px`; this.canvas.style.height = `${this.alturaCss}px`;
    this.camera.aspect = this.larguraCss / this.alturaCss;
    /* a largura vista na altura do pet, com a camera do POC; em retrato, a camera se afasta ate caber LARGURA_MIN */
    const fundo = this.profundidadeDoPet(1), larg = 2 * fundo * Math.tan(THREE.MathUtils.degToRad(FOV_GRAUS / 2)) * this.camera.aspect;
    this.afast = Math.min(AFASTAR_MAX, Math.max(1, LARGURA_MIN / larg));
    const nevoa = this.cenaIlha.cena.fog as THREE.Fog;
    nevoa.near = NEVOA[0] * this.afast; nevoa.far = NEVOA[1] * this.afast;
    this.camera.updateProjectionMatrix();
    this.chave = "";
  }
  /** a distancia do pet ao plano da camera (ao longo do eixo dela), com o afastamento `a` */
  private profundidadeDoPet(a: number): number {
    const d = new THREE.Vector3(...CAMERA_OLHAR).sub(new THREE.Vector3(...CAMERA_DESLOC)).normalize();
    return new THREE.Vector3(...CAMERA_DESLOC).multiplyScalar(-a).dot(d);
  }

  /** o modo mundo: o ponto do cliente (px) no chao dobrado, em subunidades inteiras do mapa (null fora do mapa ou fora do chao) */
  paraMundo(cx: number, cy: number): [number, number] | null {
    const r = this.canvas.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return null;
    const p = paraMundoCel(this.lida, this.dobra, ((cx - r.left) / r.width) * 2 - 1, 1 - ((cy - r.top) / r.height) * 2);
    if (!p) return null;
    const sub = this.mu.cm.sub, x = Math.round(p[0] * sub), y = Math.round(p[1] * sub);
    return dentroDoMapa(this.mu.cm, x, y) ? [x, y] : null;
  }
  /** o modo mundo: o ponto do mapa (subunidades) no cliente (px), pela mesma dobra */
  paraTela(x: number, y: number): [number, number] {
    const r = this.canvas.getBoundingClientRect(), sub = this.mu.cm.sub, [nx, ny] = paraTelaNdc(this.lida, this.dobra, x / sub, y / sub);
    return [r.left + ((nx + 1) / 2) * r.width, r.top + ((1 - ny) / 2) * r.height];
  }
  /** onde o pet esta desenhado (subunidades) */
  get petDesenhado(): [number, number] | null { return this.seguidor.pos; }

  /** um quadro: o pet onde o motor diz (interpolado), a camera atras dele, a racao e a bola, o dia ou a noite; devolve o retangulo do pet */
  desenhar(agora: number, quadro: number): Ret {
    const { motor: m } = jogoAtual(), mu = m.mundo ?? this.mu, cm = mu.cm, sub = cm.sub;
    const pos = this.seguidor.seguir(mu.pet, agora - this.ultimo, cm);
    this.ultimo = agora;
    this.petCel = [pos[0] / sub, pos[1] / sub];
    const [px, pz] = this.petCel, a = this.afast;
    this.camera.position.set(px + CAMERA_DESLOC[0] * a, CAMERA_DESLOC[1] * a, pz + CAMERA_DESLOC[2] * a);
    this.camera.lookAt(px + CAMERA_OLHAR[0] * a, CAMERA_OLHAR[1] * a, pz + CAMERA_OLHAR[2] * a);
    this.camera.updateMatrixWorld();
    CURVA.uFocoZ.value = pz;
    CURVA.uTempo.value = movimentoReduzido() ? 0 : agora / 1000;
    const noite = eNoite(m.e.tick % TPD);
    if (noite !== this.noite) { this.noite = noite; this.cenaIlha.aplicarNoite(noite); }
    this.sincronizar(mu, m.e.tick);
    const ret = this.desenharPet(quadro, px, pz);
    this.renderer.render(this.cenaIlha.cena, this.camera);
    return ret;
  }

  /** a racao e a bola onde o motor diz: entra a racao nova, sai a comida, muda de cor a podre */
  private sincronizar(mu: Mundo, tick: number): void {
    const vistas = new Set<number>(), sub = mu.cm.sub;
    for (const c of mu.comidas.values()) {
      const sit = mu.situacao(c, tick);
      if (sit === null) continue;
      vistas.add(c.id);
      let g = this.comidas.get(c.id);
      if (!g) {
        g = new THREE.Mesh(new THREE.SphereGeometry(0.3, 12, 8).scale(1, 0.55, 1), toon({ color: 0x9b6a3c }));
        g.position.set(c.x / sub, 0.12, c.y / sub);
        this.cenaIlha.cena.add(g);
        this.comidas.set(c.id, g);
      }
      (g.material as THREE.MeshToonMaterial).color.setHex(sit === "podre" ? 0x6b6b3a : 0x9b6a3c);
    }
    for (const [id, g] of this.comidas) if (!vistas.has(id)) { this.cenaIlha.cena.remove(g); this.comidas.delete(id); }
    const [bx, by] = mu.bolaEm(tick);
    this.bola.position.set(bx / sub, 0.38, by / sub);
  }

  /** o pet como sprite em pe no chao (o papel entra na H3) */
  private desenharPet(quadro: number, px: number, pz: number): Ret {
    const f = fonteDoPet(quadro), mat = this.sprite.material;
    if (f.chave !== this.chave) {
      mat.map?.dispose();
      const t = new THREE.CanvasTexture(f.canvas);
      t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.SRGBColorSpace;
      mat.map = t; mat.needsUpdate = true;
      this.texels = [f.canvas.width, f.canvas.height];
      this.chave = f.chave;
    }
    const w = this.texels[0] * TEXEL_ALVO, h = this.texels[1] * TEXEL_ALVO;
    this.sprite.position.set(px, 0, pz);
    this.sprite.scale.set(w, h, 1);
    /* o retangulo na tela: os cantos do sprite projetados */
    const base = this.paraTela(px * this.mu.cm.sub, pz * this.mu.cm.sub), topo = new THREE.Vector3(px, h, pz).project(this.camera);
    const r = this.canvas.getBoundingClientRect(), yTopo = r.top + ((1 - topo.y) / 2) * r.height, alt = base[1] - yTopo, larg = alt * (w / h);
    return { x: base[0] - r.left - larg / 2, y: yTopo - r.top, w: larg, h: alt };
  }
}

const mediana = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const p95 = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.min(s.length - 1, Math.floor(s.length * 0.95))] : 0; };

/** liga a ilha num canvas; devolve a funcao que desliga. Falha alto (a tela cai na reserva) se o WebGL nao subir ou um modelo faltar */
export function iniciarIlha(canvas: HTMLCanvasElement, mundo: Mundo, aoPerder: () => void): () => void {
  const vista = new VistaIlha(canvas, mundo), caixa = canvas.parentElement;
  if (!caixa) throw new Error("cena 3D sem caixa");
  const perdeu = (ev: Event) => { ev.preventDefault(); aoPerder(); };
  canvas.addEventListener("webglcontextlost", perdeu);
  let vivo = true, quadro = 0, pedido = 0;
  vista.carregarObjetos().catch(err => { if (!vivo) return; console.error("ilha: os modelos dos kits não carregaram; fica a reserva do mundo:", err); aoPerder(); });
  /* medir (a M3): os intervalos entre quadros do navegador */
  let medida: number[] | null = null, ultimoQuadro = performance.now();
  const laco = (agora: number) => {
    if (!vivo) return;
    if (medida) medida.push(agora - ultimoQuadro);
    ultimoQuadro = agora;
    CENA.ret = vista.desenhar(agora, quadro++);
    pedido = requestAnimationFrame(laco);
  };
  const ajustar = () => {
    vista.ajustar(caixa.clientWidth, caixa.clientHeight);
    if (caixa.clientWidth > 0 && caixa.clientHeight > 0) CENA.ret = vista.desenhar(performance.now(), quadro);
  };
  ajustar();
  const obs = new ResizeObserver(ajustar); obs.observe(caixa);
  pedido = requestAnimationFrame(laco);
  CENA.medir = () => new Promise(resolve => {
    medida = [];
    setTimeout(() => {
      const deltas = medida ?? [];
      medida = null;
      const total = deltas.reduce((a, b) => a + b, 0);
      resolve({
        medida: "M3 (tela Pet, ilha)", data: new Date().toISOString(), userAgent: navigator.userAgent, devicePixelRatio,
        tela_css: [innerWidth, innerHeight], canvas_px: [canvas.width, canvas.height],
        duracao_s: +(total / 1000).toFixed(3), quadros: deltas.length, fps_media: +((deltas.length * 1000) / total).toFixed(2),
        quadro_mediana_ms: +mediana(deltas).toFixed(2), quadro_p95_ms: +p95(deltas).toFixed(2),
        draw_calls: vista.renderer.info.render.calls,
      });
    }, 10_000);
  });
  CENA.modo3d = true;
  CENA.mundo = {
    paraMundo: (cx, cy) => vista.paraMundo(cx, cy),
    paraTela: (x, y) => vista.paraTela(x, y),
    get pet() { const p = vista.petDesenhado; if (!p) throw new Error("a cena do mundo ainda nao desenhou o pet"); return p; },
  };
  return () => {
    vivo = false;
    cancelAnimationFrame(pedido); obs.disconnect(); canvas.removeEventListener("webglcontextlost", perdeu);
    CENA.modo3d = false; CENA.ret = null; CENA.medir = null; CENA.mundo = null;
    vista.renderer.dispose();
  };
}
