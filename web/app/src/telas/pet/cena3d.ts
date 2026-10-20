/* O cenario 3D da tela Pet (docs/TAREFA_V2_TELA_PET.md, decisao do Matheus de 2026-10-19, opcao b): a vista ortografica inclinada do
   WORLD-POC (web/app/poc/mundo3d/vista.ts, arranjo V), so como vista. E uma copia adaptada, e nao um import, porque o G-FRONTEIRA
   (test/poc_mundo3d.test.ts) segura que as telas do jogo nao importam o POC; quando o mundo 3D entrar no jogo (P4), as duas se juntam.
   O que vem do POC: a camera ortografica inclinada (ELEVACAO_GRAUS), a sala de 16 x 12 celulas com as paredes e os dois obstaculos (um
   alto e um baixo), as caixas coloridas por face sem luz, o pet como THREE.Sprite com filtro nearest num numero inteiro de pixels por
   texel e o canto alinhado ao pixel da tela, e a sombra no chao.
   O que muda para o Pet: as cores claras, a parede do fundo mais alta e com uma janela, uma plataforma sob o pet, sem a bola, sem a
   comida e sem a oclusao; o pet fica parado no meio da sala (so balanca quando brinca ou explora). Nada aqui decide o jogo: so desenha o
   que o motor ja diz (a forma, o que ele faz, o ovo). Este modulo e o unico do app que importa o three, e entra por import dinamico. */
import * as THREE from "three";
import { OVO, chaveSprite, corDominante } from "../../../motor/index.ts";
import { atlasAtual, desenharSprite, dimSprite, quadroAgora } from "../../atlas.ts";
import { S, gradeDe, paleta } from "../../grades.ts";
import { jogoAtual } from "../../jogo.ts";
import { CENA } from "./cenaEstado.ts";

/* a sala do arranjo V (poc/mundo3d/config.ts e mundo.ts): 16 x 12 celulas de 16 subunidades, paredes de 8, dois obstaculos */
const SUB = 16, LARGURA = 16 * SUB, ALTURA = 12 * SUB, ESPESSURA = 8;
const ELEVACAO_GRAUS = 50;                    // o da vista do POC
/* as paredes do fundo e dos lados sobem alem do topo da tela (a sala nunca mostra o vazio acima); a do fundo tem a janela */
const ALTURA_PAREDE = 640, ALTURA_FRENTE = 6, ALTURA_ALTO = 28, ALTURA_BAIXO = 10;
/* o chao ocupa no maximo 68% da altura da tela em retrato (o celular) e 78% em paisagem (o modulo do desktop): o resto e a parede do
   fundo, com a janela, que em paisagem desce e fica mais baixa para caber */
const FRACAO_CHAO = { retrato: 0.68, paisagem: 0.78 }, JANELA_Y = { retrato: 92, paisagem: 56 }, JANELA_ESCALA = { retrato: 1, paisagem: 60 / 76 };
/* PROPOSTO, sem fonte: o pet perto da frente, no meio; a plataforma e a sombra sob ele */
const PET: [number, number] = [LARGURA / 2, ALTURA * 0.68], R_PLATAFORMA = 34, R_SOMBRA = 14;
/* as cores claras (as do cenario de reserva, CenarioPet): [tampo, frente, lados] */
const COR_FUNDO = 0xeef4fc, COR_CHAO = 0xd6e3f4, COR_SOMBRA = 0xa9c1e2, COR_PLATAFORMA = 0x8fbcef, COR_JANELA = 0x9fd0ff, COR_CAIXILHO = 0xffffff;
const CORES_PAREDE = [0xffffff, 0xeef4fc, 0xc9d9ef], CORES_ALTO = [0xffffff, 0x8fb2e0, 0x7ca2d6], CORES_BAIXO = [0xf0f6ff, 0xa9c4e8, 0x95b5e0];

interface Solido { x0: number; y0: number; x1: number; y1: number; tipo: "parede" | "alto" | "baixo" }
const SOLIDOS: Solido[] = [
  { x0: -ESPESSURA, y0: -ESPESSURA, x1: LARGURA + ESPESSURA, y1: 0, tipo: "parede" },
  { x0: -ESPESSURA, y0: ALTURA, x1: LARGURA + ESPESSURA, y1: ALTURA + ESPESSURA, tipo: "parede" },
  { x0: -ESPESSURA, y0: 0, x1: 0, y1: ALTURA, tipo: "parede" },
  { x0: LARGURA, y0: 0, x1: LARGURA + ESPESSURA, y1: ALTURA, tipo: "parede" },
  { x0: 5 * SUB, y0: 3 * SUB, x1: 7 * SUB, y1: 7 * SUB, tipo: "alto" },
  { x0: 10 * SUB, y0: 6 * SUB, x1: 12 * SUB, y1: 8 * SUB, tipo: "baixo" },
];

/** a textura do pet de agora: o quadro do atlas (local) ou a grade de reserva; a chave diz quando trocar */
function fonteDoPet(quadro: number): { chave: string; canvas: HTMLCanvasElement } {
  const { motor: m, nascendo } = jogoAtual(), a = atlasAtual(), c = document.createElement("canvas"), g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  if (a.tipo === "ok") {
    const nome = nascendo > 0 ? OVO[m.especie] : chaveSprite(m.forma), [w, h] = dimSprite(a.dados, nome);
    const iq = nascendo > 0 ? 0 : quadroAgora(a, nome, m.acao === "dormir");
    /* o quadro do atlas na caixa fixa do idle, em 1x, com 1 px de folga para o contorno da forma sombria */
    c.width = w + 2; c.height = h + 2;
    desenharSprite(g, a, nome, 1, 1, 1, iq, { sombria: m.sombria });
    return { chave: `${nome}:${iq}:${m.sombria ? 1 : 0}`, canvas: c };
  }
  const grade = nascendo > 0 ? S.ovo : S[gradeDe(m.estagioAtual)], pal = paleta(corDominante(m.tracos));
  const fechado = m.acao === "dormir" || quadro % 17 === 0;
  c.width = Math.max(...grade.map(l => l.length)); c.height = grade.length;
  grade.forEach((l, y) => [...l].forEach((ch, x) => {
    if (ch === ".") return;
    g.fillStyle = pal[fechado && ch === "w" ? "b" : ch] || "#FF00FF"; g.fillRect(x, y, 1, 1);
  }));
  return { chave: `reserva:${nascendo > 0 ? "ovo" : m.estagioAtual}:${fechado ? 1 : 0}`, canvas: c };
}

class VistaPet {
  readonly renderer: THREE.WebGLRenderer;
  private readonly cena = new THREE.Scene();
  private readonly camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 1, 4000);
  private readonly alvo = new THREE.Vector3(LARGURA / 2, 0, ALTURA / 2);
  private readonly frente: THREE.Vector3;
  private readonly direita = new THREE.Vector3(1, 0, 0);
  private readonly cima: THREE.Vector3;
  private readonly sprite: THREE.Sprite;
  private readonly sombra: THREE.Mesh;
  private readonly janela: THREE.Group;
  private chave = "";
  private texels: [number, number] = [1, 1];
  private larguraPx = 0;
  private alturaPx = 0;
  private P = 1;               // pixels do canvas por subunidade (inteiro em retrato)
  private pxPorTexel = 1;      // pixels do canvas por texel do sprite (inteiro)
  private desloc = 0;          // quanto a janela da camera desce, em subunidades (multiplo de 1/P)

  readonly canvas: HTMLCanvasElement;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    THREE.ColorManagement.enabled = false;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false });
    this.renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
    this.renderer.setClearColor(COR_FUNDO);
    const e = THREE.MathUtils.degToRad(ELEVACAO_GRAUS);
    this.frente = new THREE.Vector3(0, -Math.sin(e), -Math.cos(e));
    this.cima = new THREE.Vector3(0, Math.cos(e), -Math.sin(e));
    this.camera.position.copy(this.alvo).addScaledVector(this.frente, -1500);
    this.camera.up.copy(this.cima);
    this.camera.lookAt(this.alvo);

    const chao = new THREE.Mesh(new THREE.PlaneGeometry(LARGURA, ALTURA), new THREE.MeshBasicMaterial({ color: COR_CHAO }));
    chao.rotation.x = -Math.PI / 2; chao.position.set(LARGURA / 2, 0, ALTURA / 2);
    this.cena.add(chao);
    for (const s of SOLIDOS) {
      const frente = s.tipo === "parede" && s.y0 >= ALTURA;
      const h = s.tipo === "parede" ? (frente ? ALTURA_FRENTE : ALTURA_PAREDE) : s.tipo === "alto" ? ALTURA_ALTO : ALTURA_BAIXO;
      const [tampo, frenteCor, lados] = s.tipo === "parede" ? CORES_PAREDE : s.tipo === "alto" ? CORES_ALTO : CORES_BAIXO;
      const w = s.x1 - s.x0, d = s.y1 - s.y0;
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [lados, lados, tampo, lados, frenteCor, lados].map(color => new THREE.MeshBasicMaterial({ color })));
      m.position.set(s.x0 + w / 2, h / 2, s.y0 + d / 2);
      this.cena.add(m);
    }
    /* a janela na parede do fundo: o vidro e o caixilho em cruz, rentes a parede */
    const janela = new THREE.Group();
    const vidro = new THREE.Mesh(new THREE.PlaneGeometry(120, 76), new THREE.MeshBasicMaterial({ color: COR_JANELA }));
    janela.add(vidro);
    for (const [w, h] of [[3, 76], [120, 3]] as const) janela.add(Object.assign(new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: COR_CAIXILHO })), { renderOrder: 1 }));
    janela.children[1].position.z = janela.children[2].position.z = 0.1;
    janela.position.set(LARGURA / 2, JANELA_Y.retrato, 0.3);
    this.cena.add(janela);
    this.janela = janela;
    /* a plataforma e a sombra no chao, sob o pet */
    const plataforma = new THREE.Mesh(new THREE.RingGeometry(R_PLATAFORMA - 7, R_PLATAFORMA, 40), new THREE.MeshBasicMaterial({ color: COR_PLATAFORMA }));
    plataforma.rotation.x = -Math.PI / 2; plataforma.position.set(PET[0], 0.15, PET[1]);
    this.cena.add(plataforma);
    this.sombra = new THREE.Mesh(new THREE.CircleGeometry(R_SOMBRA, 24), new THREE.MeshBasicMaterial({ color: COR_SOMBRA }));
    this.sombra.rotation.x = -Math.PI / 2;
    this.cena.add(this.sombra);
    /* o pet por cima de tudo: o sprite fica de frente para a camera, e a parte de cima dele entraria no obstaculo de tras */
    this.sprite = new THREE.Sprite(new THREE.SpriteMaterial({ alphaTest: 0.5, transparent: false, depthTest: false, depthWrite: false }));
    this.sprite.renderOrder = 10;
    this.cena.add(this.sprite);
  }

  /** ajusta o canvas a caixa (px de CSS): a sala ate um pouco mais larga que a tela (as paredes dos lados cortam), o chao em ate 68% (retrato) ou 78% (paisagem) da
   *  altura e encostado embaixo, a parede do fundo no resto; o pet na maior escala inteira que cabe em 42% da altura e 60% da largura */
  ajustar(larguraCss: number, alturaCss: number, razao: number): void {
    const r = Math.max(1, Math.floor(razao));
    this.larguraPx = 2 * Math.floor((larguraCss * r) / 2); this.alturaPx = 2 * Math.floor((alturaCss * r) / 2);
    this.renderer.setPixelRatio(1);
    this.renderer.setSize(this.larguraPx, this.alturaPx, false);
    this.canvas.style.width = `${this.larguraPx / r}px`; this.canvas.style.height = `${this.alturaPx / r}px`;
    const e = THREE.MathUtils.degToRad(ELEVACAO_GRAUS), forma = this.larguraPx > this.alturaPx ? "paisagem" : "retrato";
    /* pixels do canvas por subunidade: inteiro em retrato (o celular, como no POC); em paisagem (o modulo do desktop), fracionario, para a
       sala encher a caixa mesmo com 1 pixel do aparelho por pixel de CSS. O pet continua nitido: o tamanho e o canto dele sao contados
       em pixels inteiros do canvas (desenhar) */
    const P = Math.min((this.larguraPx * 1.1) / LARGURA, (this.alturaPx * FRACAO_CHAO[forma]) / (ALTURA * Math.sin(e)));
    this.P = forma === "retrato" ? Math.max(1, Math.floor(P)) : Math.max(1, P);
    this.janela.position.y = JANELA_Y[forma]; this.janela.scale.y = JANELA_ESCALA[forma];
    if (forma === "paisagem") {
      /* a parede que aparece acima do chao, em subunidades: a janela fica no meio dela e ocupa no maximo 60% da altura */
      const parede = (this.alturaPx * 0.98 - ALTURA * Math.sin(e) * this.P) / (this.P * Math.cos(e));
      this.janela.scale.y = Math.min(JANELA_ESCALA.paisagem, (parede * 0.6) / 76);
      this.janela.position.y = Math.min(JANELA_Y.paisagem, parede * 0.55);
    }
    const meiaL = this.larguraPx / (2 * this.P), meiaA = this.alturaPx / (2 * this.P);
    /* a frente da sala a 2% do fundo do canvas: a janela da camera desce o que sobra (em pixels inteiros) */
    const frenteNaTela = -(ALTURA / 2) * Math.sin(e);
    this.desloc = Math.round((frenteNaTela + meiaA - this.alturaPx * 0.02 / this.P) * this.P) / this.P;
    Object.assign(this.camera, { left: -meiaL, right: meiaL, top: meiaA + this.desloc, bottom: -meiaA + this.desloc });
    this.camera.updateProjectionMatrix();
    this.chave = "";
  }

  /** desenha um quadro: troca a textura se o pet mudou e devolve o retangulo do sprite em px de CSS (para os extras do PalcoPet) */
  desenhar(quadro: number, razao: number): { x: number; y: number; w: number; h: number } {
    const { motor: m, nascendo } = jogoAtual(), f = fonteDoPet(quadro);
    if (f.chave !== this.chave) {
      const mat = this.sprite.material as THREE.SpriteMaterial;
      mat.map?.dispose();
      const t = new THREE.CanvasTexture(f.canvas);
      t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.NoColorSpace;
      mat.map = t; mat.needsUpdate = true;
      this.texels = [f.canvas.width, f.canvas.height];
      this.pxPorTexel = Math.max(1, Math.min(12, Math.floor(Math.min(this.alturaPx * 0.42 / this.texels[1], this.larguraPx * 0.6 / this.texels[0]))));
      this.chave = f.chave;
    }
    const P = this.P, w = this.texels[0] * this.pxPorTexel, h = this.texels[1] * this.pxPorTexel;
    /* so balanca: o lugar do pet na sala e fixo (a cena nao tem fisica que decida nada) */
    let px = PET[0];
    if (nascendo > 0) px += nascendo % 2 ? 1 : -1;
    else if (m.acao === "explorar") px += Math.sin(quadro / 3) * 28;
    else if (m.acao === "brincar") px += Math.sin(quadro / 2) * 10;
    const ancora = new THREE.Vector3(px, 0, PET[1]), rel = ancora.clone().sub(this.alvo);
    const sx = rel.dot(this.direita) * P, sy = rel.dot(this.cima) * P - this.desloc * P, prof = rel.dot(this.frente);
    const esquerda = Math.round(sx - w / 2), base = Math.round(sy);
    const centro = this.alvo.clone()
      .addScaledVector(this.direita, (esquerda + w / 2) / P)
      .addScaledVector(this.cima, (base + h / 2) / P + this.desloc)
      .addScaledVector(this.frente, prof);
    this.sprite.position.copy(centro);
    this.sprite.scale.set(w / P, h / P, 1);
    this.sombra.position.set(px, 0.2, PET[1]);
    this.renderer.render(this.cena, this.camera);
    const k = Math.max(1, Math.floor(razao));
    return { x: (this.larguraPx / 2 + esquerda) / k, y: (this.alturaPx / 2 - (base + h)) / k, w: w / k, h: h / k };
  }
}

const mediana = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const p95 = (v: number[]): number => { const s = [...v].sort((a, b) => a - b); return s.length ? s[Math.min(s.length - 1, Math.floor(s.length * 0.95))] : 0; };

/** liga a cena num canvas; devolve a funcao que desliga. Falha alto (a tela cai no cenario de reserva) se o WebGL nao subir */
export function iniciarCena3D(canvas: HTMLCanvasElement, aoPerder: () => void): () => void {
  const vista = new VistaPet(canvas), caixa = canvas.parentElement;
  if (!caixa) throw new Error("cena 3D sem caixa");
  const razao = () => (devicePixelRatio || 1);
  const perdeu = (ev: Event) => { ev.preventDefault(); aoPerder(); };
  canvas.addEventListener("webglcontextlost", perdeu);
  let quadro = 0;
  const desenha = () => { CENA.ret = vista.desenhar(quadro, razao()); quadro++; };
  /* a caixa mudou de tamanho (um modulo do quadro cresceu ou recolheu): reenquadra e redesenha na hora o mesmo quadro, sem esperar o
     proximo e sem avancar o contador (o balanco do pet segue o mesmo ritmo) */
  const ajustar = () => {
    vista.ajustar(caixa.clientWidth, caixa.clientHeight, razao());
    if (caixa.clientWidth > 0 && caixa.clientHeight > 0) CENA.ret = vista.desenhar(Math.max(0, quadro - 1), razao());
  };
  ajustar();
  const obs = new ResizeObserver(ajustar); obs.observe(caixa);
  /* um quadro a cada 120 ms, como o PalcoPet (o idle do atlas e de 120 ms por quadro): a sala e parada */
  const t = setInterval(desenha, 120);
  /* a M3 pela pagina do jogo (docs/TAREFA_V2_TELA_PET.md): 10 s desenhando a cada quadro do navegador, a mesma medida do POC */
  CENA.medir = () => new Promise(resolve => {
    const deltas: number[] = [];
    let ultimo = performance.now();
    const inicio = ultimo;
    const laco = (agora: number) => {
      deltas.push(agora - ultimo); ultimo = agora; desenha();
      if (agora - inicio < 10_000) { requestAnimationFrame(laco); return; }
      const total = deltas.reduce((a, b) => a + b, 0);
      resolve({
        medida: "M3 (tela Pet)", data: new Date().toISOString(), userAgent: navigator.userAgent, devicePixelRatio,
        tela_css: [innerWidth, innerHeight], canvas_px: [canvas.width, canvas.height],
        duracao_s: +(total / 1000).toFixed(3), quadros: deltas.length, fps_media: +((deltas.length * 1000) / total).toFixed(2),
        quadro_mediana_ms: +mediana(deltas).toFixed(2), quadro_p95_ms: +p95(deltas).toFixed(2),
      });
    };
    requestAnimationFrame(laco);
  });
  CENA.modo3d = true;
  return () => {
    clearInterval(t); obs.disconnect(); canvas.removeEventListener("webglcontextlost", perdeu);
    CENA.modo3d = false; CENA.ret = null; CENA.medir = null;
    vista.renderer.dispose();
  };
}
