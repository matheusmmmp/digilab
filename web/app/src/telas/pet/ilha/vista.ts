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
import { Seguidor, dentroDoMapa } from "../vistaMundo.ts";
import { AFASTAR_MAX, COBERTO_MS, KITS_COBERTO_MS, CAMERA_DESLOC, CAMERA_OLHAR, DOBRA_K, FOV_GRAUS, FPS_MIN, LARGURA_MIN, LONGE, NEVOA, PERTO, QUEDA_MS, RAZAO_MAX, TEXEL_ALVO } from "./constantes.ts";
import { CURVA, montarCena, objetos, type CenaIlha, type Objetos } from "./cena.ts";
import { paraMundoCel, paraTelaNdc, type CameraLida, type Dobra } from "./curva.ts";
import { ilhaDe, type Ilha } from "./grade.ts";
import { Itens } from "./itens.ts";
import { Papel, type Ret } from "./papel.ts";

const movimentoReduzido = (): boolean => matchMedia("(prefers-reduced-motion: reduce)").matches;

class VistaIlha {
  readonly renderer: THREE.WebGLRenderer;
  readonly camera = new THREE.PerspectiveCamera(FOV_GRAUS, 1, PERTO, LONGE);
  private readonly ilha: Ilha;
  private readonly cenaIlha: CenaIlha;
  private readonly seguidor = new Seguidor();
  private readonly raio = new THREE.Raycaster();
  private readonly lida: CameraLida;
  private readonly papel = new Papel();
  private readonly itens: Itens;
  private objetos: Objetos | null = null;
  /** a qualidade caiu (regra 10): sem vento, metade da grama e pixelRatio 1 */
  private baixa = false;
  private ppu = 1;              // pixels do canvas por unidade do mundo na distancia do pet
  private pxPorTexel = 1;       // pixels do canvas por texel do sprite (inteiro, regra 8)
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
    /* o ninho, o comedouro, a racao, a fruta e a bola (itens.ts) e o pet em papel */
    this.itens = new Itens(mu);
    this.cenaIlha.cena.add(this.itens.raiz, this.papel.raiz);
    CURVA.uVento.value = 1;
  }

  /** os kits (public/kits3d) entram depois do terreno */
  async carregarObjetos(): Promise<void> {
    THREE.ColorManagement.enabled = true;
    const o = await objetos(this.ilha, document.baseURI);
    this.objetos = o;
    this.cenaIlha.cena.add(o.grupo);
    if (this.baixa) this.menosGrama();
  }

  /** a dobra de agora: centrada no z desenhado do pet */
  private get dobra(): Dobra { return { k: DOBRA_K, focoZ: this.petCel[1] }; }

  /** ajusta o canvas a caixa (px de CSS): a resolucao, a proporcao e o afastamento da camera em retrato */
  ajustar(larguraCss: number, alturaCss: number): void {
    this.larguraCss = Math.max(1, larguraCss); this.alturaCss = Math.max(1, alturaCss);
    this.renderer.setPixelRatio(this.baixa ? 1 : Math.min(RAZAO_MAX, devicePixelRatio || 1));
    this.renderer.setSize(this.larguraCss, this.alturaCss, false);
    this.canvas.style.width = `${this.larguraCss}px`; this.canvas.style.height = `${this.alturaCss}px`;
    this.camera.aspect = this.larguraCss / this.alturaCss;
    /* a largura vista na altura do pet, com a camera do POC; em retrato, a camera se afasta ate caber LARGURA_MIN */
    const fundo = this.profundidadeDoPet(1), larg = 2 * fundo * Math.tan(THREE.MathUtils.degToRad(FOV_GRAUS / 2)) * this.camera.aspect;
    this.afast = Math.min(AFASTAR_MAX, Math.max(1, LARGURA_MIN / larg));
    const nevoa = this.cenaIlha.cena.fog as THREE.Fog;
    nevoa.near = NEVOA[0] * this.afast; nevoa.far = NEVOA[1] * this.afast;
    this.camera.updateProjectionMatrix();
    /* o pet em papel: na distancia do foco, um texel do sprite vale um numero inteiro de pixels do canvas (regra 8) */
    this.ppu = this.renderer.domElement.height / 2 / (this.profundidadeDoPet(this.afast) * Math.tan(THREE.MathUtils.degToRad(FOV_GRAUS / 2)));
    this.pxPorTexel = Math.max(1, Math.round(TEXEL_ALVO * this.ppu));
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
    /* fora da cena nada e chao: o raio de um ponto abaixo do canvas ainda tocaria a ilha perto da camera */
    if (cx < r.left || cx > r.right || cy < r.top || cy > r.bottom) return null;
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
    /* o ColorManagement do three e um global que as outras vistas (a sala e o mapa da Exploracao) desligam: sem repor aqui, a cor da nevoa
       e das luzes dependia de qual import dinamico subia por ultimo */
    THREE.ColorManagement.enabled = true;
    const { motor: m } = jogoAtual(), mu = m.mundo ?? this.mu, cm = mu.cm, sub = cm.sub;
    const dtMs = agora - this.ultimo, pos = this.seguidor.seguir(mu.pet, dtMs, cm);
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
    this.itens.sincronizar(mu, m.e.tick, noite);
    const ret = this.papel.atualizar({
      agora, dt: Math.min(0.05, dtMs / 1000), quadro, cel: this.petCel, motor: mu.pet, camera: this.camera,
      ppu: this.ppu, pxPorTexel: this.pxPorTexel, canvas: [this.renderer.domElement.width, this.renderer.domElement.height],
      razao: this.renderer.getPixelRatio(), reduzido: movimentoReduzido(), noite,
    });
    this.renderer.render(this.cenaIlha.cena, this.camera);
    return ret;
  }

  dispose(): void { this.papel.dispose(); this.renderer.dispose(); }

  /** a queda de qualidade (regra 10, PROPOSTO): sem vento, metade da grama e pixelRatio 1; so uma vez */
  baixarQualidade(): void {
    if (this.baixa) return;
    this.baixa = true;
    CURVA.uVento.value = 0;
    this.menosGrama();
    console.info("ilha: a média ficou abaixo de", FPS_MIN, "fps; a qualidade caiu (sem vento, menos grama, pixelRatio 1)");
  }
  get qualidadeBaixa(): boolean { return this.baixa; }
  private menosGrama(): void { for (const g of this.objetos?.grama ?? []) g.count = Math.floor(g.count / 2); }
}

const mediana = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const p95 = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.min(s.length - 1, Math.floor(s.length * 0.95))] : 0; };

/** liga a ilha num canvas; devolve a funcao que desliga. Falha alto (a tela cai na reserva) se o WebGL nao subir ou um modelo faltar */
export function iniciarIlha(canvas: HTMLCanvasElement, mundo: Mundo, aoPerder: () => void): () => void {
  /* antes da vista: os campos dela (o papel) ja criam cores */
  THREE.ColorManagement.enabled = true;
  const vista = new VistaIlha(canvas, mundo), caixa = canvas.parentElement;
  if (!caixa) throw new Error("cena 3D sem caixa");
  const perdeu = (ev: Event) => { ev.preventDefault(); aoPerder(); };
  canvas.addEventListener("webglcontextlost", perdeu);
  let vivo = true, quadro = 0, pedido = 0;
  /* os kits: na hora, ou, se a ilha abriu coberta pelo veu, quando ela ficar a vista (no maximo KITS_COBERTO_MS) */
  let kitsPedidos = false;
  const carregarKits = () => {
    if (kitsPedidos) return;
    kitsPedidos = true;
    vista.carregarObjetos().catch(err => { if (!vivo) return; console.error("ilha: os modelos dos kits não carregaram; fica a reserva do mundo:", err); aoPerder(); });
  };
  const esperaKits = CENA.coberto ? setTimeout(carregarKits, KITS_COBERTO_MS) : null;
  if (!esperaKits) carregarKits();
  /* medir (a M3): os intervalos entre quadros do navegador */
  let medida: number[] | null = null, ultimoQuadro = performance.now();
  /* a queda de qualidade: a media de quadros em janelas de QUEDA_MS (a pagina escondida nao conta: o navegador para o laco) */
  let janela = { inicio: performance.now(), quadros: 0 };
  const laco = (agora: number) => {
    if (!vivo) return;
    /* coberta pelo veu: um quadro a cada COBERTO_MS, sem contar para a queda de qualidade */
    if (CENA.coberto && !medida) {
      if (agora - ultimoQuadro >= COBERTO_MS) { ultimoQuadro = agora; CENA.ret = vista.desenhar(agora, quadro++); }
      janela = { inicio: agora, quadros: 0 };
      pedido = requestAnimationFrame(laco);
      return;
    }
    carregarKits();
    if (medida) medida.push(agora - ultimoQuadro);
    if (agora - ultimoQuadro > 500) janela = { inicio: agora, quadros: 0 };
    ultimoQuadro = agora;
    janela.quadros++;
    if (agora - janela.inicio >= QUEDA_MS) {
      if (!vista.qualidadeBaixa && (janela.quadros * 1000) / (agora - janela.inicio) < FPS_MIN) { vista.baixarQualidade(); ajustar(); }
      janela = { inicio: agora, quadros: 0 };
    }
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
        draw_calls: vista.renderer.info.render.calls, qualidade_baixa: vista.qualidadeBaixa,
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
    cancelAnimationFrame(pedido); obs.disconnect(); if (esperaKits) clearTimeout(esperaKits); canvas.removeEventListener("webglcontextlost", perdeu);
    CENA.modo3d = false; CENA.ret = null; CENA.medir = null; CENA.mundo = null;
    vista.dispose();
  };
}
