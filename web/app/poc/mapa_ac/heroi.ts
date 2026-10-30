/* O personagem do mapa_ac: o pet do atlas de clipes do Digimon UP (Idle e Run), desenhado como um recorte de papel em pé no mundo 3D, no
   jeito do Paper Mario:
     - um plano vertical sempre de frente para a câmera (a câmera não gira, então basta ele ficar paralelo a ela);
     - o pixel art com filtro nearest e uma borda branca de 1 texel, o "papel" recortado;
     - ao trocar de lado, o plano gira em volta do eixo vertical (a escala em x passa por 0, o virar de folha do Paper Mario);
     - um pulinho e um leve balanço ao correr, e a sombra redonda no chão.
   Sem o atlas na máquina (ele fica fora do repositório), um boneco de reserva de 16 x 16. Só desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { GEO_SOMBRA, curvar, materialSombra } from "./cena.ts";

type Quadro = [number, number, number, number, number, number];
interface Clipe { quadros: Quadro[]; ms: number[]; loop: boolean }
interface AtlasClipes { atlas: string; sprites: Record<string, { digimon: string; caixa: [number, number]; clipes: Record<string, Clipe> }> }

const TEXEL = 1 / 34;                 // o tamanho de um pixel do sprite no mundo, em células
const BORDA = 1;                      // a borda branca do papel, em texels
const VIRAR_POR_S = 9;                // a velocidade da virada de lado (escala em x por segundo)

interface Animacao { texturas: THREE.CanvasTexture[]; ms: number[] }

/* um quadro do atlas recortado na caixa comum, com a borda branca em volta do que não é transparente; o pé fica na linha de baixo */
function quadroComBorda(img: HTMLImageElement, q: Quadro, caixa: [number, number], pe: number): HTMLCanvasElement {
  const [w, h] = [caixa[0] + 2 * BORDA, pe + 2 * BORDA];
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  const g = c.getContext("2d")!;
  g.drawImage(img, q[0], q[1], q[2], q[3], q[4] + BORDA, q[5] + BORDA, q[2], q[3]);
  const d = g.getImageData(0, 0, w, h), px = d.data;
  /* a sombra do próprio export vem semitransparente sob os pés; a sombra aqui é a redonda do chão, então o que não é opaco sai */
  for (let k = 3; k < px.length; k += 4) if (px[k] < 230) px[k] = 0;
  const alfa = (x: number, y: number) => x >= 0 && y >= 0 && x < w && y < h && px[(y * w + x) * 4 + 3] > 0;
  const borda: number[] = [];
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if (alfa(x, y)) continue;
    for (let dy = -BORDA; dy <= BORDA; dy++) for (let dx = -BORDA; dx <= BORDA; dx++) if (alfa(x + dx, y + dy)) { borda.push(x, y); dy = dx = 99; }
  }
  for (let i = 0; i < borda.length; i += 2) { const k = (borda[i + 1] * w + borda[i]) * 4; px[k] = px[k + 1] = px[k + 2] = 255; px[k + 3] = 255; }
  g.putImageData(d, 0, 0);
  return c;
}

/* quantas linhas do quadro vão até o último pixel opaco */
function linhaOpacaFinal(img: HTMLImageElement, q: Quadro): number {
  const c = document.createElement("canvas");
  c.width = q[2]; c.height = q[3];
  const g = c.getContext("2d", { willReadFrequently: true })!;
  g.drawImage(img, q[0], q[1], q[2], q[3], 0, 0, q[2], q[3]);
  const px = g.getImageData(0, 0, q[2], q[3]).data;
  for (let y = q[3] - 1; y >= 0; y--) for (let x = 0; x < q[2]; x++) if (px[(y * q[2] + x) * 4 + 3] >= 230) return y + 1;
  return q[3];
}

const textura = (c: HTMLCanvasElement) => {
  const t = new THREE.CanvasTexture(c);
  t.magFilter = t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
};

/* o boneco de reserva, sem o atlas */
const RESERVA = ["....kkkkkk....", "...kllllllk...", "..kllllllllk..", ".kllwbllwbllk.", ".kllbbllbbllk.", ".klrllllllrlk.", ".kllllkkllllk.",
  ".kdlllllllldk.", "..kdllllllldk.", "..kddllllddk..", "...kddddddk...", "...kdk..kdk...", "...kk....kk..."];
const CORES_RESERVA: Record<string, string> = { k: "#1b1b2f", l: "#f2a65a", d: "#c8743a", w: "#ffffff", b: "#3a2e5f", r: "#e2556a" };

export class Heroi {
  readonly raiz = new THREE.Group();
  private readonly papel: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  private readonly silhueta: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  private readonly sombra: THREE.Mesh;
  private anims: Record<"Idle" | "Run", Animacao> = { Idle: { texturas: [], ms: [] }, Run: { texturas: [], ms: [] } };
  private clipe: "Idle" | "Run" = "Idle";
  private t0 = 0;
  private lado = 1;                    // 1 = olhando para a direita na tela; -1 = para a esquerda
  private escalaX = 1;
  /** se o desenho original olha para a esquerda (o atlas do UP olha); a virada usa isso */
  private olhaEsquerda = true;
  nome = "reserva";

  constructor() {
    /* o papel vai no passe transparente, depois da silhueta: onde ele aparece, cobre a silhueta; onde uma árvore o esconde, ela fica */
    this.papel = new THREE.Mesh(new THREE.PlaneGeometry(1, 1),
      curvar(new THREE.MeshBasicMaterial({ alphaTest: 0.5, side: THREE.DoubleSide, transparent: true })));
    this.papel.renderOrder = 3;
    this.silhueta = new THREE.Mesh(this.papel.geometry, curvar(new THREE.MeshBasicMaterial({
      color: 0xfff1c8, alphaTest: 0.5, side: THREE.DoubleSide, transparent: true, opacity: 0.55, depthTest: false, depthWrite: false })));
    this.silhueta.renderOrder = 2;
    this.papel.add(this.silhueta);
    this.sombra = new THREE.Mesh(GEO_SOMBRA, materialSombra());
    this.sombra.renderOrder = 1;
    this.raiz.add(this.papel, this.sombra);
    this.usarReserva();
  }

  private usarReserva(): void {
    const c = document.createElement("canvas");
    c.width = 14; c.height = 13;
    const g = c.getContext("2d")!;
    RESERVA.forEach((l, y) => [...l].forEach((ch, x) => { if (ch !== ".") { g.fillStyle = CORES_RESERVA[ch]; g.fillRect(x, y, 1, 1); } }));
    const t = textura(c);
    this.anims = { Idle: { texturas: [t], ms: [1000] }, Run: { texturas: [t], ms: [1000] } };
    this.olhaEsquerda = false;
    this.ajustarPlano(14 * 2.4, 13 * 2.4);
    this.nome = "reserva";
  }

  private ajustarPlano(wTexel: number, hTexel: number): void {
    this.papel.geometry.dispose();
    this.papel.geometry = this.silhueta.geometry = new THREE.PlaneGeometry(wTexel * TEXEL, hTexel * TEXEL).translate(0, (hTexel * TEXEL) / 2, 0);
    this.trocarQuadro(this.anims.Idle.texturas[0]);
  }

  private trocarQuadro(t: THREE.Texture): void {
    this.papel.material.map = this.silhueta.material.map = t;
    this.papel.material.needsUpdate = this.silhueta.material.needsUpdate = true;
  }

  /** os nomes dos sprites do atlas de clipes, ou [] sem o atlas na máquina */
  static async listar(): Promise<{ atlas: AtlasClipes; img: HTMLImageElement } | null> {
    try {
      const r = await fetch("./Assets/digilab_atlas_up_clipes.json");
      if (!r.ok) return null;
      const atlas = await r.json() as AtlasClipes;
      const img = new Image();
      img.src = "./Assets/digilab_atlas_up_clipes.png";
      await img.decode();
      return { atlas, img };
    } catch { return null; }
  }

  /** troca o personagem por um sprite do atlas (Idle e Run); falha alto se o sprite não tem os dois clipes */
  usarSprite(fonte: { atlas: AtlasClipes; img: HTMLImageElement }, nome: string): void {
    const s = fonte.atlas.sprites[nome];
    if (!s?.clipes.Idle || !s.clipes.Run) throw new Error(`sprite ${nome} sem Idle ou Run no atlas de clipes`);
    const vazio = (q: Quadro) => q[2] === 0 || q[3] === 0;
    /* o pé: a linha opaca mais baixa em algum quadro do Idle e do Run (abaixo dela, só a sombra do export, que sai) */
    const pe = Math.max(...[...s.clipes.Idle.quadros, ...s.clipes.Run.quadros].filter(q => !vazio(q)).map(q => q[5] + linhaOpacaFinal(fonte.img, q)));
    for (const a of this.anims.Idle.texturas.concat(this.anims.Run.texturas)) a.dispose();
    const anim = (c: Clipe): Animacao => {
      const ok = c.quadros.map((q, i) => [q, c.ms[i]] as const).filter(([q]) => !vazio(q));
      return { texturas: ok.map(([q]) => textura(quadroComBorda(fonte.img, q, s.caixa, pe))), ms: ok.map(([, m]) => m) };
    };
    this.anims = { Idle: anim(s.clipes.Idle), Run: anim(s.clipes.Run) };
    this.olhaEsquerda = true;
    this.ajustarPlano(s.caixa[0] + 2 * BORDA, pe + 2 * BORDA);
    this.nome = `${s.digimon} (${nome})`;
  }

  set desenhoOlhaEsquerda(v: boolean) { this.olhaEsquerda = v; }
  get desenhoOlhaEsquerda(): boolean { return this.olhaEsquerda; }

  /** um passo de desenho: a posição no chão, para onde anda na tela (dx) e se está andando, o tempo em ms e o intervalo em s */
  atualizar(x: number, y: number, z: number, dx: number, andando: boolean, agora: number, dt: number, correndo: boolean): void {
    const clipe = andando ? "Run" : "Idle";
    if (clipe !== this.clipe) { this.clipe = clipe; this.t0 = agora; }
    if (dx > 0.05) this.lado = 1; else if (dx < -0.05) this.lado = -1;
    /* a virada de papel: a escala em x vai até o lado novo passando por 0 */
    const alvo = this.lado * (this.olhaEsquerda ? -1 : 1);
    const passo = VIRAR_POR_S * dt;
    this.escalaX = Math.abs(alvo - this.escalaX) <= passo ? alvo : this.escalaX + Math.sign(alvo - this.escalaX) * passo;
    const a = this.anims[this.clipe], total = a.ms.reduce((s, m) => s + m, 0) * (correndo ? 0.7 : 1);
    let t = (agora - this.t0) % total, i = 0;
    while (i < a.ms.length - 1 && t >= a.ms[i] * (correndo ? 0.7 : 1)) { t -= a.ms[i] * (correndo ? 0.7 : 1); i++; }
    if (this.papel.material.map !== a.texturas[i]) this.trocarQuadro(a.texturas[i]);
    /* o pulinho e o balanço ao correr; parado, só respira */
    const pulo = andando ? Math.abs(Math.sin(agora / (correndo ? 70 : 95))) * 0.07 : Math.sin(agora / 600) * 0.008;
    this.papel.position.set(0, pulo, 0);
    this.papel.rotation.z = andando ? Math.sin(agora / (correndo ? 70 : 95)) * 0.035 : 0;
    this.papel.scale.set(Math.abs(this.escalaX) < 0.06 ? 0.06 * Math.sign(this.escalaX || 1) : this.escalaX, 1 - pulo * 0.4, 1);
    this.raiz.position.set(x, y, z);
    const larg = this.papel.geometry.parameters.width;
    this.sombra.scale.set(larg * 0.75, 1, larg * 0.4);
    this.sombra.position.set(0, 0.03, 0);
  }
}
