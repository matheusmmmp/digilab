/* O pet em papel da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, regras 7 e 8, H3): o personagem do POC (poc/mapa_ac/heroi.ts) adaptado ao
   pet do motor e ao atlas do jogo (src/atlas.ts), desenhado como um recorte de papel em pe no mundo 3D, no jeito do Paper Mario:
     - um plano sempre de frente para a camera (paralelo a imagem dela; a camera nao gira), com o pixel art em filtro nearest e uma borda
       branca de 1 texel, o "papel" recortado; a sombra semitransparente do export sai (a sombra e a redonda do chao);
     - o tamanho na tela e um numero inteiro de pixels do canvas por texel (a vista o calcula na distancia do foco, regra 8) e o canto do
       papel cai num pixel inteiro;
     - o lado: o atlas do UP desenha os Digimon olhando para a direita (confira pelo rabo, nao pela cabeca); o papel olha para o lado em
       que a posicao desenhada anda em x na tela e, ao trocar, gira em volta do eixo vertical (a escala em x passa por 0, a virada de folha);
     - andando (a posicao do motor mudou nos ultimos ANDANDO_MS), o clipe Run do atlas de clipes (H-4) e um pulinho; parado, o Idle; um
       sprite sem Run usa o Idle com o pulinho;
     - o ovo ao nascer (balanca de lado), a forma sombria, o quadro parado ao dormir (na grade de reserva, o olho fechado);
     - a silhueta clara atras das arvores: onde uma arvore esconde o papel, ela aparece;
     - com movimento reduzido, sem pulinho e sem virada animada (a troca de lado e instantanea).
   Sem o atlas (os e2e e as capturas; ou carregando), a grade de reserva do jogo (fontePet.ts). So desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { OVO, chaveSprite } from "../../../../motor/index.ts";
import { atlasAtual, chaveUp, desenharSprite, dimSprite, quadroAgora, type AtlasOk, type Clipe } from "../../../atlas.ts";
import { jogoAtual } from "../../../jogo.ts";
import { fonteDoPet } from "../fontePet.ts";
import { ANDANDO_MS, BORDA_PAPEL, LADO_MIN, PULO_MS, PULO_TEXELS, VIRAR_POR_S } from "./constantes.ts";
import { GEO_SOMBRA, materialSombra } from "./cena.ts";

/** o retangulo do papel na tela, em px de CSS relativos ao canvas (para o PalcoPet) */
export interface Ret { x: number; y: number; w: number; h: number }
/** o que a vista passa ao papel a cada quadro */
export interface Passo {
  agora: number; dt: number; quadro: number;
  /** onde o pet esta desenhado (celulas) e onde o motor diz (subunidades) */
  cel: readonly [number, number]; motor: readonly [number, number];
  camera: THREE.PerspectiveCamera;
  /** pixels do canvas por unidade do mundo na distancia do pet, pixels do canvas por texel (inteiro), o tamanho do canvas e px por px de CSS */
  ppu: number; pxPorTexel: number; canvas: [number, number]; razao: number;
  reduzido: boolean;
}

interface Folha { tex: THREE.CanvasTexture; w: number; h: number }

/** a borda branca do papel em volta do que e opaco; o que nao e opaco (a sombra do export) sai; corta as linhas abaixo de `pe` */
function recortar(c: HTMLCanvasElement, pe: number): HTMLCanvasElement {
  const B = BORDA_PAPEL, w = c.width + 2 * B, h = Math.min(c.height, pe) + 2 * B;
  const s = document.createElement("canvas");
  s.width = w; s.height = h;
  const g = s.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  g.drawImage(c, 0, 0, c.width, Math.min(c.height, pe), B, B, c.width, Math.min(c.height, pe));
  const d = g.getImageData(0, 0, w, h), px = d.data;
  for (let k = 3; k < px.length; k += 4) if (px[k] < 230) px[k] = 0;
  const opaco = (x: number, y: number) => x >= 0 && y >= 0 && x < w && y < h && px[(y * w + x) * 4 + 3] > 0;
  const borda: number[] = [];
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if (opaco(x, y)) continue;
    perto: for (let dy = -B; dy <= B; dy++) for (let dx = -B; dx <= B; dx++) if (opaco(x + dx, y + dy)) { borda.push(x, y); break perto; }
  }
  for (let i = 0; i < borda.length; i += 2) { const k = (borda[i + 1] * w + borda[i]) * 4; px[k] = px[k + 1] = px[k + 2] = 255; px[k + 3] = 255; }
  g.putImageData(d, 0, 0);
  return s;
}
/** a ultima linha com pixel opaco (alfa >= 230) de um canvas, mais 1 */
function linhaOpacaFinal(c: HTMLCanvasElement): number {
  const g = c.getContext("2d", { willReadFrequently: true });
  if (!g) throw new Error("canvas 2d indisponível");
  const px = g.getImageData(0, 0, c.width, c.height).data;
  for (let y = c.height - 1; y >= 0; y--) for (let x = 0; x < c.width; x++) if (px[(y * c.width + x) * 4 + 3] >= 230) return y + 1;
  return c.height;
}
const textura = (c: HTMLCanvasElement) => {
  const t = new THREE.CanvasTexture(c);
  t.magFilter = t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
};

/** um quadro do atlas em 1x na caixa do sprite (com 1 px de folga para o contorno da forma sombria) */
function quadroAtlas(a: AtlasOk, nome: string, iq: number, sombria: boolean, clipe: Clipe): HTMLCanvasElement {
  const [w, h] = dimSprite(a.dados, nome), c = document.createElement("canvas");
  c.width = w + 2; c.height = h + 2;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  desenharSprite(g, a, nome, 1, 1, 1, iq, { sombria, clipe });
  return c;
}

export class Papel {
  readonly raiz = new THREE.Group();
  private readonly papel: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  private readonly silhueta: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  private readonly sombra: THREE.Mesh;
  private readonly folhas = new Map<string, Folha>();
  private readonly pes = new Map<string, number>();
  private dono = "";                    // as folhas sao de um sprite so: trocou a forma, saem todas
  private clipe: Clipe = "Idle";
  private t0 = 0;
  private lado = 1;                     // 1 = olhando para a direita na tela; -1 = para a esquerda
  private escalaX = 1;
  private xAntes: number | null = null;
  private motorAntes = "";
  private mudouEm = -1e9;
  private readonly v = new THREE.Vector3();

  constructor() {
    /* o papel vai no passe transparente, depois da silhueta: onde ele aparece, cobre a silhueta; onde uma arvore o esconde, ela fica */
    const geo = new THREE.PlaneGeometry(1, 1).translate(0, 0.5, 0);
    this.papel = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ alphaTest: 0.5, side: THREE.DoubleSide, transparent: true }));
    this.papel.renderOrder = 3;
    this.silhueta = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
      color: 0xfff1c8, alphaTest: 0.5, side: THREE.DoubleSide, transparent: true, opacity: 0.55, depthTest: false, depthWrite: false }));
    this.silhueta.renderOrder = 2;
    this.papel.add(this.silhueta);
    this.sombra = new THREE.Mesh(GEO_SOMBRA, materialSombra());
    this.sombra.renderOrder = 1;
    this.raiz.add(this.papel, this.sombra);
  }

  /** a folha (textura com a borda) do quadro de agora: do atlas, ou da grade de reserva */
  private folhaAgora(quadro: number, andando: boolean, agora: number): { folha: Folha; ovo: boolean } {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    if (a.tipo !== "ok") {
      const f = fonteDoPet(quadro);
      return { folha: this.folha(`reserva|${f.chave}`, () => recortar(f.canvas, f.canvas.height)), ovo: nascendo > 0 };
    }
    const ovo = nascendo > 0, nome = ovo ? OVO[m.especie] : chaveSprite(m.forma), s = a.dados.sprites[chaveUp(a.dados, nome)];
    const clipe: Clipe = !ovo && andando && s?.clipes?.Run ? "Run" : "Idle";
    if (clipe !== this.clipe) { this.clipe = clipe; this.t0 = agora; }
    const iq = ovo ? 0 : quadroAgora(a, nome, m.acao === "dormir", clipe, this.t0), sombria = !ovo && m.sombria;
    const pe = this.pe(a, nome, sombria);
    return { folha: this.folha(`${nome}|${clipe}|${iq}|${sombria ? 1 : 0}`, () => recortar(quadroAtlas(a, nome, iq, sombria, clipe), pe)), ovo };
  }
  /** o pe do sprite: a linha opaca mais baixa nos quadros do Idle e do Run (abaixo dela, so a sombra do export, que sai) */
  private pe(a: AtlasOk, nome: string, sombria: boolean): number {
    const ch = `${nome}|${sombria ? 1 : 0}`, pronto = this.pes.get(ch);
    if (pronto !== undefined) return pronto;
    const s = a.dados.sprites[chaveUp(a.dados, nome)], clipes: Clipe[] = s?.clipes?.Run ? ["Idle", "Run"] : ["Idle"];
    let pe = 0;
    for (const c of clipes) {
      const n = s ? (s.clipes?.[c]?.quadros.length ?? s.quadros.length) : 1;
      for (let i = 0; i < n; i++) pe = Math.max(pe, linhaOpacaFinal(quadroAtlas(a, nome, i, sombria, c)));
    }
    this.pes.set(ch, pe);
    return pe;
  }
  private folha(chave: string, fazer: () => HTMLCanvasElement): Folha {
    const dono = chave.split("|")[0];
    if (dono !== this.dono) { for (const f of this.folhas.values()) f.tex.dispose(); this.folhas.clear(); this.dono = dono; }
    let f = this.folhas.get(chave);
    if (!f) { const c = fazer(); f = { tex: textura(c), w: c.width, h: c.height }; this.folhas.set(chave, f); }
    return f;
  }

  /** um passo de desenho: escolhe a folha, vira para o lado em que anda, poe o papel em pixel inteiro; devolve o retangulo em px de CSS */
  atualizar(p: Passo): Ret {
    /* andando: a posicao do motor mudou nos ultimos ANDANDO_MS */
    const chaveMotor = `${p.motor[0]},${p.motor[1]}`;
    if (chaveMotor !== this.motorAntes) { if (this.motorAntes) this.mudouEm = p.agora; this.motorAntes = chaveMotor; }
    const andando = p.agora - this.mudouEm < ANDANDO_MS;
    const { folha, ovo } = this.folhaAgora(p.quadro, andando, p.agora);
    if (this.papel.material.map !== folha.tex) {
      this.papel.material.map = this.silhueta.material.map = folha.tex;
      this.papel.material.needsUpdate = this.silhueta.material.needsUpdate = true;
    }
    /* o lado: a posicao desenhada anda em x na tela (a camera nao gira: x do mundo e x da tela) */
    if (this.xAntes !== null) {
      const dx = p.cel[0] - this.xAntes;
      if (dx > LADO_MIN) this.lado = 1; else if (dx < -LADO_MIN) this.lado = -1;
    }
    this.xAntes = p.cel[0];
    const passo = VIRAR_POR_S * p.dt;
    this.escalaX = p.reduzido || Math.abs(this.lado - this.escalaX) <= passo ? this.lado : this.escalaX + Math.sign(this.lado - this.escalaX) * passo;
    /* o tamanho em pixels inteiros do canvas; o pulinho em texels inteiros; o ovo balanca um texel de lado */
    const n = p.pxPorTexel, wpx = folha.w * n, hpx = folha.h * n, { nascendo } = jogoAtual();
    const pulo = andando && !p.reduzido && !ovo ? Math.round(Math.abs(Math.sin(p.agora / PULO_MS)) * PULO_TEXELS) * n : 0;
    const balanco = ovo ? (nascendo % 2 ? n : -n) : 0;
    /* o pe do papel no chao (o foco: sem dobra), projetado; o canto vai ao pixel inteiro mais perto */
    this.v.set(p.cel[0], 0, p.cel[1]).project(p.camera);
    const [W, H] = p.canvas, ax = ((this.v.x + 1) / 2) * W, ay = ((1 - this.v.y) / 2) * H;
    const esquerda = Math.round(ax - wpx / 2) + balanco, base = Math.round(ay) - pulo;
    const dx = (esquerda + wpx / 2 - ax) / p.ppu, dy = (ay - base) / p.ppu;
    const cam = p.camera, direita = this.v.set(1, 0, 0).applyQuaternion(cam.quaternion).clone(), cima = new THREE.Vector3(0, 1, 0).applyQuaternion(cam.quaternion);
    this.papel.quaternion.copy(cam.quaternion);
    this.papel.position.set(0, 0, 0).addScaledVector(direita, dx).addScaledVector(cima, dy);
    this.papel.scale.set((Math.abs(this.escalaX) < 0.06 ? 0.06 * Math.sign(this.escalaX || 1) : this.escalaX) * wpx / p.ppu, hpx / p.ppu, 1);
    this.raiz.position.set(p.cel[0], 0, p.cel[1]);
    const larg = wpx / p.ppu;
    this.sombra.scale.set(larg * 0.75, 1, larg * 0.4);
    this.sombra.position.set(0, 0.03, 0);
    return { x: esquerda / p.razao, y: (base - hpx) / p.razao, w: wpx / p.razao, h: hpx / p.razao };
  }

  /** solta as texturas */
  dispose(): void { for (const f of this.folhas.values()) f.tex.dispose(); this.folhas.clear(); }
}
