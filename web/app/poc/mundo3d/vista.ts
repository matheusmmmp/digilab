/* A vista do WORLD-POC-01a (docs/TAREFA_V2_WORLD_POC_01.md, etapa E3; W-2): o Three.js imperativo, SÓ desenho. Ela lê o estado do
   mundo e nunca escreve nele. É o único arquivo do POC que importa o three (a G-FRONTEIRA confere).
     - a câmera ortográfica inclinada (M-2): acima e à frente do chão, olhando para o fundo da sala com ELEVACAO graus;
     - o chão, as paredes e os obstáculos como caixas; a parede da frente é baixa, para a sala aparecer;
     - o pet como THREE.Sprite (sempre de frente para a câmera), com filtro nearest e um número inteiro de pixels por texel, e o ponto de
       baixo do sprite alinhado ao pixel da tela; a sombra como um disco no chão;
     - a oclusão: o sólido que fica entre a câmera e o pet fica semitransparente (só desenho; a visão do pet é a do motor);
     - sem gestão de cor e sem antialias: a cor do texel chega à tela como está (a M2 confere pixel a pixel).
   A unidade do mundo 3D é a subunidade do motor: X = x, Z = y, Y = a altura. */
import * as THREE from "three";
import { ALTURA, LARGURA } from "./config.ts";
import type { Mundo } from "./mundo.ts";

export const ELEVACAO_GRAUS = 50;            // PROPOSTO, sem fonte: o ângulo da câmera sobre o chão
const ALTURA_PAREDE = 24, ALTURA_FRENTE = 6, ALTURA_ALTO = 24, ALTURA_BAIXO = 8;
const COR_CHAO = 0xd9cfb5, COR_SOMBRA = 0xb4a98f;
/* as cores de cada caixa por face, sem luz (o tampo claro, a frente média, os lados escuros): [tampo, frente, lados] */
const CORES_PAREDE = [0x9c8a74, 0x6e604f, 0x83735f], CORES_ALTO = [0x8fb57a, 0x5f8050, 0x76995f], CORES_BAIXO = [0xc4cf96, 0x96a170, 0xadb983];
const OPACIDADE_OCLUSAO = 0.35;

/** a textura do pet: os pixels (linhas de caracteres) e a paleta, ou um recorte de uma imagem (o atlas) */
export type FonteSprite =
  | { tipo: "pixels"; linhas: readonly string[]; paleta: Readonly<Record<string, string>>; subPorTexel: number }
  | { tipo: "imagem"; imagem: CanvasImageSource; x: number; y: number; w: number; h: number; subPorTexel: number };

/** o retângulo do sprite na tela, em pixels do canvas (y para baixo), e quantos pixels tem cada texel */
export interface RetanguloSprite { x: number; y: number; w: number; h: number; pxPorTexel: number }

/** uma posição do pet para desenhar: a do motor ou a interpolada entre dois ticks */
export interface Pose { pet: [number, number]; bola: [number, number] }

export class Vista {
  readonly renderer: THREE.WebGLRenderer;
  readonly cena = new THREE.Scene();
  readonly camera: THREE.OrthographicCamera;
  private readonly alvo = new THREE.Vector3(LARGURA / 2, 0, ALTURA / 2);
  private readonly frente: THREE.Vector3;      // a direção do olhar
  private readonly direita = new THREE.Vector3(1, 0, 0);
  private readonly cima: THREE.Vector3;        // o "para cima" da tela, no mundo
  private readonly sprite: THREE.Sprite;
  private readonly sombra: THREE.Mesh;
  private readonly bola: THREE.Mesh;
  private readonly comidas = new Map<number, THREE.Mesh>();
  private readonly solidos: THREE.Mesh[] = [];
  private readonly texels: [number, number];
  private readonly origem: HTMLCanvasElement;   // os texels da textura, para a M2
  private readonly subPorTexel: number;
  private larguraPx = 0;
  private alturaPx = 0;
  private pxPorSub = 1;
  private ultimoRetangulo: RetanguloSprite = { x: 0, y: 0, w: 0, h: 0, pxPorTexel: 1 };
  /** quantos sólidos ficaram semitransparentes no último quadro (a oclusão) */
  cobrindo = 0;

  readonly canvas: HTMLCanvasElement;
  readonly mundo: Mundo;

  constructor(canvas: HTMLCanvasElement, mundo: Mundo, fonte: FonteSprite) {
    this.canvas = canvas;
    this.mundo = mundo;
    THREE.ColorManagement.enabled = false;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false });
    this.renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
    this.renderer.setClearColor(0xf4f1ea);
    const e = THREE.MathUtils.degToRad(ELEVACAO_GRAUS);
    this.frente = new THREE.Vector3(0, -Math.sin(e), -Math.cos(e));
    this.cima = new THREE.Vector3(0, Math.cos(e), -Math.sin(e));
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 1, 4000);
    this.camera.position.copy(this.alvo).addScaledVector(this.frente, -1500);
    this.camera.up.copy(this.cima);
    this.camera.lookAt(this.alvo);

    const chao = new THREE.Mesh(new THREE.PlaneGeometry(LARGURA, ALTURA), new THREE.MeshBasicMaterial({ color: COR_CHAO }));
    chao.rotation.x = -Math.PI / 2;
    chao.position.set(LARGURA / 2, 0, ALTURA / 2);
    this.cena.add(chao);

    for (const s of mundo.solidos) {
      const frente = s.categoria === "parede" && s.ret.y0 >= ALTURA;
      const h = s.categoria === "parede" ? (frente ? ALTURA_FRENTE : ALTURA_PAREDE) : s.alto ? ALTURA_ALTO : ALTURA_BAIXO;
      const [tampo, frenteCor, lados] = s.categoria === "parede" ? CORES_PAREDE : s.alto ? CORES_ALTO : CORES_BAIXO;
      const w = s.ret.x1 - s.ret.x0, d = s.ret.y1 - s.ret.y0;
      /* a ordem das faces da BoxGeometry: +x, -x, +y (o tampo), -y, +z (a frente, para a câmera), -z */
      const mats = [lados, lados, tampo, lados, frenteCor, lados].map(color => new THREE.MeshBasicMaterial({ color }));
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mats);
      m.position.set(s.ret.x0 + w / 2, h / 2, s.ret.y0 + d / 2);
      this.cena.add(m);
      this.solidos.push(m);
    }

    this.sombra = new THREE.Mesh(new THREE.CircleGeometry(mundo.pet.r, 24), new THREE.MeshBasicMaterial({ color: COR_SOMBRA }));
    this.sombra.rotation.x = -Math.PI / 2;
    this.cena.add(this.sombra);

    this.bola = new THREE.Mesh(new THREE.SphereGeometry(mundo.bola.r, 16, 12), new THREE.MeshBasicMaterial({ color: 0xd9534f }));
    this.cena.add(this.bola);

    const tex = texturaDe(fonte);
    this.origem = tex.image as HTMLCanvasElement;
    this.texels = [this.origem.width, this.origem.height];
    this.subPorTexel = fonte.subPorTexel;
    this.sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, alphaTest: 0.5, transparent: false }));
    this.cena.add(this.sprite);
  }

  /** ajusta o canvas ao tamanho dado (em pixels de CSS) e escolhe quantos pixels do canvas tem uma subunidade (inteiro) */
  ajustar(larguraCss: number, alturaCss: number, razao: number): void {
    const r = Math.max(1, Math.floor(razao));
    this.larguraPx = 2 * Math.floor((larguraCss * r) / 2);    // par: o centro da tela cai num pixel inteiro
    this.alturaPx = 2 * Math.floor((alturaCss * r) / 2);
    this.renderer.setPixelRatio(1);
    this.renderer.setSize(this.larguraPx, this.alturaPx, false);
    this.canvas.style.width = `${this.larguraPx / r}px`;
    this.canvas.style.height = `${this.alturaPx / r}px`;
    const e = THREE.MathUtils.degToRad(ELEVACAO_GRAUS);
    const altoNaTela = ALTURA * Math.sin(e) + ALTURA_PAREDE * Math.cos(e);
    this.pxPorSub = Math.max(1, Math.floor(Math.min((this.larguraPx * 0.94) / LARGURA, (this.alturaPx * 0.9) / altoNaTela)));
    const meiaL = this.larguraPx / (2 * this.pxPorSub), meiaA = this.alturaPx / (2 * this.pxPorSub);
    Object.assign(this.camera, { left: -meiaL, right: meiaL, top: meiaA, bottom: -meiaA });
    this.camera.updateProjectionMatrix();
  }

  get tamanho(): { largura: number; altura: number; pxPorSub: number } {
    return { largura: this.larguraPx, altura: this.alturaPx, pxPorSub: this.pxPorSub };
  }

  /** desenha uma pose (a interpolação fica com quem chama); devolve o retângulo do sprite na tela */
  desenhar(pose: Pose): RetanguloSprite {
    const m = this.mundo, P = this.pxPorSub;
    const pxPorTexel = Math.max(1, Math.floor(P * this.subPorTexel));
    const w = this.texels[0] * pxPorTexel, h = this.texels[1] * pxPorTexel;
    const ancora = new THREE.Vector3(pose.pet[0], 0, pose.pet[1]);
    const rel = ancora.clone().sub(this.alvo);
    const sx = rel.dot(this.direita) * P, sy = rel.dot(this.cima) * P, prof = rel.dot(this.frente);
    const esquerda = Math.round(sx - w / 2), base = Math.round(sy);        // o canto do sprite num pixel inteiro
    const centro = this.alvo.clone()
      .addScaledVector(this.direita, (esquerda + w / 2) / P)
      .addScaledVector(this.cima, (base + h / 2) / P)
      .addScaledVector(this.frente, prof);
    this.sprite.position.copy(centro);
    this.sprite.scale.set(w / P, h / P, 1);
    this.sombra.position.set(pose.pet[0], 0.2, pose.pet[1]);
    this.bola.position.set(pose.bola[0], m.bola.r, pose.bola[1]);
    this.atualizarComidas();
    this.ocluir(centro, h / P);
    this.renderer.render(this.cena, this.camera);
    this.ultimoRetangulo = {
      x: this.larguraPx / 2 + esquerda, y: this.alturaPx / 2 - (base + h), w, h, pxPorTexel,
    };
    return this.ultimoRetangulo;
  }

  get retangulo(): RetanguloSprite { return this.ultimoRetangulo; }

  private atualizarComidas(): void {
    for (const c of this.mundo.comidas) {
      let malha = this.comidas.get(c.id);
      if (!malha) {
        malha = new THREE.Mesh(new THREE.BoxGeometry(6, 4, 6), new THREE.MeshBasicMaterial({ color: 0x4f9d4a }));
        this.cena.add(malha);
        this.comidas.set(c.id, malha);
      }
      malha.visible = c.ativa;
      malha.position.set(c.x, 2, c.y);
    }
  }

  /** o sólido entre a câmera e o sprite fica semitransparente: três raios na direção do olhar, pelos pés, pelo centro e pelo topo */
  private ocluir(centro: THREE.Vector3, alturaMundo: number): void {
    const materiais = (m: THREE.Mesh) => m.material as THREE.MeshBasicMaterial[];
    /* o material opaco é compilado com o alfa fixo em 1: trocar o `transparent` pede recompilar (needsUpdate), só quando muda */
    const marcar = (mat: THREE.MeshBasicMaterial, coberto: boolean) => {
      if (mat.transparent === coberto) return;
      mat.transparent = coberto; mat.opacity = coberto ? OPACIDADE_OCLUSAO : 1; mat.depthWrite = !coberto; mat.needsUpdate = true;
    };
    const cobertos = new Set<THREE.Object3D>();
    for (const f of [-0.45, 0, 0.45]) {
      const ponto = centro.clone().addScaledVector(this.cima, f * alturaMundo);
      const raio = new THREE.Raycaster(ponto.clone().addScaledVector(this.frente, -2000), this.frente.clone(), 0, 2000 - 0.5);
      for (const hit of raio.intersectObjects(this.solidos, false)) cobertos.add(hit.object);
    }
    for (const s of this.solidos) for (const mat of materiais(s)) marcar(mat, cobertos.has(s));
    this.cobrindo = cobertos.size;
  }

  /** a M2: lê os pixels do retângulo do sprite e confere cada texel opaco (alfa >= 128, o corte do alphaTest) contra a cor dele na
   *  textura, em todos os pixels que ele cobre. Chame logo depois de `desenhar` (o buffer ainda é o do quadro) */
  conferirPixels(): { conferidos: number; divergentes: number; texels_opacos: number } {
    const r = this.ultimoRetangulo, gl = this.renderer.getContext();
    const fonte = this.origem.getContext("2d")!.getImageData(0, 0, this.texels[0], this.texels[1]).data;
    const esperado = (i: number, j: number): [number, number, number] | null => {
      const k = (j * this.texels[0] + i) * 4;
      return fonte[k + 3] >= 128 ? [fonte[k], fonte[k + 1], fonte[k + 2]] : null;
    };
    let opacos = 0;
    const buf = new Uint8Array(r.w * r.h * 4);
    gl.readPixels(r.x, this.alturaPx - (r.y + r.h), r.w, r.h, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    let conferidos = 0, divergentes = 0;
    for (let j = 0; j < this.texels[1]; j++) for (let i = 0; i < this.texels[0]; i++) {
      const cor = esperado(i, j);
      if (cor === null) continue;
      opacos += 1;
      for (let b = 0; b < r.pxPorTexel; b++) for (let a = 0; a < r.pxPorTexel; a++) {
        const px = i * r.pxPorTexel + a, py = j * r.pxPorTexel + b;
        const k = ((r.h - 1 - py) * r.w + px) * 4;        // o readPixels começa embaixo
        conferidos += 1;
        if (buf[k] !== cor[0] || buf[k + 1] !== cor[1] || buf[k + 2] !== cor[2]) divergentes += 1;
      }
    }
    return { conferidos, divergentes, texels_opacos: opacos };
  }
}

/** a textura do pet, sem mipmap, com filtro nearest e sem gestão de cor */
function texturaDe(f: FonteSprite): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  const g = c.getContext("2d", { willReadFrequently: true });
  if (!g) throw new Error("canvas 2d indisponivel");
  if (f.tipo === "pixels") {
    c.width = f.linhas[0].length; c.height = f.linhas.length;
    f.linhas.forEach((l, y) => [...l].forEach((ch, x) => {
      if (ch === ".") return;
      g.fillStyle = f.paleta[ch];
      g.fillRect(x, y, 1, 1);
    }));
  } else {
    c.width = f.w; c.height = f.h;
    g.drawImage(f.imagem, f.x, f.y, f.w, f.h, 0, 0, f.w, f.h);
  }
  const t = new THREE.CanvasTexture(c);
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.colorSpace = THREE.NoColorSpace;
  return t;
}

