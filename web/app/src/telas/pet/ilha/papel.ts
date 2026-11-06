/* O pet em papel da ilha (docs/TAREFA_V3_HABITAT_ILHA_3D.md, regras 7 e 8, H3): o personagem do POC (poc/mapa_ac/heroi.ts) adaptado ao
   pet do motor e ao atlas do jogo (src/atlas.ts), desenhado como um recorte de papel em pe no mundo 3D, no jeito do Paper Mario:
     - um plano sempre de frente para a camera (paralelo a imagem dela, tambem com a camera livre girando), com o pixel art em filtro nearest e uma borda
       branca de 1 texel, o "papel" recortado; a sombra semitransparente do export sai (a sombra e a redonda do chao);
     - o tamanho na tela e um numero inteiro de pixels do canvas por texel (a vista o calcula na distancia do foco, regra 8) e o canto do
       papel cai num pixel inteiro;
     - o lado: o atlas do UP desenha os Digimon olhando para a direita (confira pelo rabo, nao pela cabeca); o papel olha para o lado em
       que a posicao desenhada anda em x na tela e, ao trocar, gira em volta do eixo vertical (a escala em x passa por 0, a virada de folha);
     - andando (a posicao do motor mudou nos ultimos ANDANDO_MS), o clipe Run do atlas de clipes (H-4) e um pulinho; parado, o Idle; um
       sprite sem Run usa o Idle com o pulinho;
     - o golpe (docs/TAREFA_V3_HABITAT_OBJETOS.md): o clipe Attack_1 do atlas, desde `golpe.desde`, olhando para `golpe.alvo` (no saco de
       pancada do treino e na bola); um sprite sem Attack_1 fica no Idle. O corte do golpe guarda o centro e o pe do Idle,
       entao o Digimon nao pula ao bater;
     - o comer (docs/TAREFA_V3_SPRITES_ACOES.md, M3): com o clipe Comer no atlas, o laco da acao comer e o "comeu a racao" (uma vez,
       virado para a comida), pelas regras do cenaAcao.ts (escolherComer); o quadro e o Comer com o Comer_objeto por cima, no corte
       alargado (corte.ts), e o gesto de hoje sai. Sem o clipe, fica o gesto;
     - o ovo ao nascer (balanca de lado), a forma sombria, o quadro parado ao dormir (na grade de reserva, o olho fechado);
     - a silhueta clara atras das arvores: onde uma arvore esconde o papel, ela aparece;
     - com movimento reduzido, sem pulinho e sem virada animada (a troca de lado e instantanea);
     - a noite, o papel fica no tom NOITE_PAPEL (o papel nao recebe luz: e o tom da cena noturna).
   Sem o atlas (os e2e e as capturas; ou carregando), a grade de reserva do jogo (fontePet.ts). So desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { OVO, chaveSprite } from "../../../../motor/index.ts";
import { atlasAtual, chaveUp, desenharSprite, dimSprite, quadroAgora, type AtlasOk, type Clipe } from "../../../atlas.ts";
import { balancoOvo, jogoAtual } from "../../../jogo.ts";
import { SONO, alturaSono } from "../sono.ts";
import { SEM_GESTO, escolherComer, esquecerComer, marcarEmburrar, gestoAgora, type EscolhaComer } from "../cenaAcao.ts";
import { flashDesde } from "../../../flash.ts";
import { alargarCorte, unirCaixas, type Corte } from "./corte.ts";
import { velocidadeAtual } from "../../../tempo.ts";
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
  /** a noite do motor: o papel escurece um pouco, como o resto da cena */
  noite: boolean;
  /** o golpe de agora (a coreografia do treino e a batida na bola; so vista): desde quando (o mesmo `agora`) e o ponto do chao em que o
      pet bate (celulas; ele olha para la); null fora dele */
  golpe?: { desde: number; alvo: readonly [number, number] } | null;
  /** a vista move o pet desenhado sem o motor (a ida e a volta do treino): conta como andando */
  andandoVista?: boolean;
}

interface Folha { tex: THREE.CanvasTexture; w: number; h: number }

/** a borda branca do papel em volta do que e opaco; o que nao e opaco (a sombra do export) sai; corta fora do `corte`, entao o centro
    do papel e o centro do que se ve do Digimon (a sombra cai embaixo dele, e a virada de lado nao o faz pular). O corte alargado pode
    passar das bordas do quadro: o que fica fora e transparente */
function recortar(c: HTMLCanvasElement, corte: Corte): HTMLCanvasElement {
  const B = BORDA_PAPEL, cw = corte.x1 - corte.x0 + 1, ch = Math.min(c.height, corte.pe), w = cw + 2 * B, h = ch + 2 * B;
  const s = document.createElement("canvas");
  s.width = w; s.height = h;
  const g = s.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const sx0 = Math.max(0, corte.x0), sx1 = Math.min(c.width - 1, corte.x1);
  if (sx1 >= sx0) g.drawImage(c, sx0, 0, sx1 - sx0 + 1, ch, B + sx0 - corte.x0, B, sx1 - sx0 + 1, ch);
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
/** a caixa do que e opaco (alfa >= 230) num canvas: as colunas x0 a x1 e a ultima linha mais 1; null se nada e opaco */
function caixaOpaca(c: HTMLCanvasElement): Corte | null {
  const g = c.getContext("2d", { willReadFrequently: true });
  if (!g) throw new Error("canvas 2d indisponível");
  const px = g.getImageData(0, 0, c.width, c.height).data;
  let x0 = c.width, x1 = -1, pe = 0;
  for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) if (px[(y * c.width + x) * 4 + 3] >= 230) {
    if (x < x0) x0 = x;
    if (x > x1) x1 = x;
    pe = y + 1;
  }
  return x1 < 0 ? null : { x0, x1, pe };
}
/** o corte inteiro de um canvas (a grade de reserva: ela nao tem sombra nem folga) */
const corteInteiro = (c: HTMLCanvasElement): Corte => ({ x0: 0, x1: c.width - 1, pe: c.height });
/** o tom do papel a noite (multiplica a textura) */
const NOITE_PAPEL = 0xaab6dd;
const textura = (c: HTMLCanvasElement) => {
  const t = new THREE.CanvasTexture(c);
  t.magFilter = t.minFilter = THREE.NearestFilter;
  t.generateMipmaps = false;
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
};

/** o ovo do atlas e uma peca pintada de 72x100, mais que o dobro do bebe (~45 px): no papel ele entra pela metade, do tamanho do bebe
    que vai nascer dele. PROPOSTO, SEM FONTE */
const OVOS = new Set<string>(Object.values(OVO));
/** um quadro do atlas em 1x na caixa do sprite (com 1 px de folga para o contorno da forma sombria); o ovo, pela metade. Um clipe com a
    camada do objeto (`<Tag>_objeto`, o Comer_objeto) a desenha por cima, no mesmo quadro (a comida na frente da boca) */
function quadroAtlas(a: AtlasOk, nome: string, iq: number, sombria: boolean, clipe: Clipe): HTMLCanvasElement {
  const [w, h] = dimSprite(a.dados, nome), c = document.createElement("canvas");
  c.width = w + 2; c.height = h + 2;
  const g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  desenharSprite(g, a, nome, 1, 1, 1, iq, { sombria, clipe });
  const objeto = `${clipe}_objeto` as Clipe;
  if (a.dados.sprites[chaveUp(a.dados, nome)]?.clipes?.[objeto]) desenharSprite(g, a, nome, 1, 1, 1, iq, { sombria, clipe: objeto });
  if (!OVOS.has(nome)) return c;
  const m = document.createElement("canvas");
  m.width = Math.ceil(c.width / 2); m.height = Math.ceil(c.height / 2);
  const gm = m.getContext("2d");
  if (!gm) throw new Error("canvas 2d indisponível");
  gm.imageSmoothingQuality = "high";
  gm.drawImage(c, 0, 0, m.width, m.height);
  return m;
}

export class Papel {
  readonly raiz = new THREE.Group();
  private readonly papel: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  private readonly silhueta: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  private readonly sombra: THREE.Mesh;
  private readonly folhas = new Map<string, Folha>();
  private readonly cortes = new Map<string, Corte>();
  private dono = "";                    // as folhas sao de um sprite so: trocou a forma, saem todas
  private clipe: Clipe = "Idle";
  private t0 = 0;
  private lado = 1;                     // 1 = olhando para a direita na tela; -1 = para a esquerda
  private escalaX = 1;
  private celAntes: [number, number] | null = null;
  private motorAntes = "";
  private mudouEm = -1e9;
  private golpeDesde: number | null = null;
  /** onde estava cada comida no quadro anterior (celulas): a entrada nova em `mundo.consumos` chega com a comida ja tirada do mundo */
  private comidasAntes = new Map<number, readonly [number, number]>();
  /** o que tocou no comer no ultimo quadro (o clipe, o gesto ou nada; cenaAcao.ts, escolherComer): o teste e o e2e leem */
  comer: EscolhaComer["tocou"] = null;
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
  private folhaAgora(quadro: number, andando: boolean, agora: number, golpe: Passo["golpe"], comer: EscolhaComer, emburra: boolean): { folha: Folha; ovo: boolean } {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    if (a.tipo !== "ok") {
      const f = fonteDoPet(quadro);
      return { folha: this.folha(`reserva|${f.chave}`, () => recortar(f.canvas, corteInteiro(f.canvas))), ovo: nascendo > 0 };
    }
    const ovo = nascendo > 0, nome = ovo ? OVO[m.especie] : chaveSprite(m.forma), s = a.dados.sprites[chaveUp(a.dados, nome)];
    const bate = !ovo && !!golpe && !!s?.clipes?.Attack_1, come = !ovo && !bate && comer.tocou === "clipe";
    if (come && !s?.clipes?.Comer) throw new Error("o comer escolheu o clipe Comer num sprite sem ele: " + nome);
    const emb = emburra && !ovo && !bate && !come;
    if (emb && !s?.clipes?.Emburrar) throw new Error("o emburrar escolheu o clipe Emburrar num sprite sem ele: " + nome);
    const clipe: Clipe = bate ? "Attack_1" : come ? "Comer" : emb ? "Emburrar" : !ovo && andando && s?.clipes?.Run ? "Run" : "Idle";
    if (clipe !== this.clipe || (bate && golpe!.desde !== this.golpeDesde)) { this.clipe = clipe; this.t0 = bate ? golpe!.desde : agora; }
    this.golpeDesde = bate ? golpe!.desde : null;
    if (come) this.t0 = comer.desde;
    const iq = ovo ? 0 : quadroAgora(a, nome, m.acao === "dormir" && !bate, clipe, this.t0), sombria = !ovo && m.sombria;
    const corte = bate || come || emb ? this.corteAlargado(a, nome, sombria, clipe) : this.corte(a, nome, sombria);
    return { folha: this.folha(`${nome}|${clipe}|${iq}|${sombria ? 1 : 0}`, () => recortar(quadroAtlas(a, nome, iq, sombria, clipe), corte)), ovo };
  }
  /** a forma de agora tem o clipe Emburrar no atlas? (sem atlas, no ovo ou sem o clipe: fica o tremor de cenaAcao.ts) */
  private temEmburrar(): boolean {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    return a.tipo === "ok" && nascendo <= 0 && !!a.dados.sprites[chaveUp(a.dados, chaveSprite(m.forma))]?.clipes?.Emburrar;
  }
  /** a soma dos ms do clipe Comer do sprite de agora (um ciclo); null sem o atlas, no ovo ou num sprite sem o Comer: fica o gesto de hoje */
  private cicloComer(): number | null {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    if (a.tipo !== "ok" || nascendo > 0) return null;
    const c = a.dados.sprites[chaveUp(a.dados, chaveSprite(m.forma))]?.clipes?.Comer;
    return c ? c.ms.reduce((x, y) => x + y, 0) : null;
  }
  /** o corte do sprite: a caixa do que e opaco em todos os quadros do Idle e do Run (abaixo do pe, so a sombra do export, que sai; dos
      lados, a folga da caixa do atlas, que deixaria o Digimon fora do centro do papel). Um corte so por sprite: o papel nao pula entre quadros */
  private corte(a: AtlasOk, nome: string, sombria: boolean): Corte {
    const ch = `${nome}|${sombria ? 1 : 0}`, pronto = this.cortes.get(ch);
    if (pronto) return pronto;
    const s = a.dados.sprites[chaveUp(a.dados, nome)], clipes: Clipe[] = s?.clipes?.Run ? ["Idle", "Run"] : ["Idle"];
    const caixas: (Corte | null)[] = [];
    for (const c of clipes) {
      const n = s ? (s.clipes?.[c]?.quadros.length ?? s.quadros.length) : 1;
      for (let i = 0; i < n; i++) caixas.push(caixaOpaca(quadroAtlas(a, nome, i, sombria, c)));
    }
    const final = unirCaixas(caixas) ?? corteInteiro(quadroAtlas(a, nome, 0, sombria, "Idle"));
    this.cortes.set(ch, final);
    return final;
  }
  /** o corte de um clipe fora da locomocao (o Attack_1; o Comer, com o Comer_objeto por cima): o do Idle e do Run alargado para caber todos
      os quadros dele, com o mesmo centro e o mesmo pe (corte.ts: o papel cresce para os dois lados, e o Digimon fica onde estava) */
  private corteAlargado(a: AtlasOk, nome: string, sombria: boolean, clipe: Clipe): Corte {
    const ch = `${nome}|${sombria ? 1 : 0}|${clipe}`, pronto = this.cortes.get(ch);
    if (pronto) return pronto;
    const base = this.corte(a, nome, sombria), n = a.dados.sprites[chaveUp(a.dados, nome)]?.clipes?.[clipe]?.quadros.length ?? 0;
    const final = alargarCorte(base, Array.from({ length: n }, (_, i) => caixaOpaca(quadroAtlas(a, nome, i, sombria, clipe))));
    this.cortes.set(ch, final);
    return final;
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
    const golpe = p.golpe ?? null, andaBase = !!p.andandoVista || p.agora - this.mudouEm < ANDANDO_MS;
    /* o comer (cenaAcao.ts, escolherComer): o laco cede ao passo e ao golpe; o "comeu a racao" cede so ao golpe, e o pet para de andar nele */
    const mo0 = jogoAtual(), mu = mo0.motor.mundo, sub = mu?.cm.sub ?? 1, nCons = mu?.consumos.length ?? 0;
    const ultimo = nCons > 0 ? (mu!.consumos[nCons - 1] as { id?: number }).id : undefined;
    const comer = escolherComer({
      chave: String(mo0.motor.semente), acao: mo0.nascendo > 0 ? "" : mo0.motor.acao, consumos: nCons,
      alvo: ultimo !== undefined ? this.comidasAntes.get(ultimo) ?? null : null, ciclo: this.cicloComer(),
      velocidade: velocidadeAtual(), andando: andaBase || !!golpe, pausa: velocidadeAtual() <= 0, donoDesde: flashDesde(),
    }, p.agora);
    this.comidasAntes = new Map([...(mu?.comidas.values() ?? [])].map(c => [c.id, [c.x / sub, c.y / sub] as const]));
    const noClipe = comer.tocou === "clipe" && !golpe;
    this.comer = golpe && comer.tocou === "clipe" ? null : comer.tocou;
    const andando = !golpe && !noClipe && andaBase;
    /* o emburrar: o clipe Emburrar (laco) toca com o pet parado e acordado na acao `emburrar`; o tremor programatico sai (o clipe e o corpo) */
    const emburra = !golpe && !noClipe && !andando && mo0.nascendo <= 0 && mo0.motor.acao === "emburrar" && this.temEmburrar();
    const { folha, ovo } = this.folhaAgora(p.quadro, andando, p.agora, golpe, comer, emburra);
    marcarEmburrar(emburra && !ovo);
    if (this.papel.material.map !== folha.tex) {
      this.papel.material.map = this.silhueta.material.map = folha.tex;
      this.papel.material.needsUpdate = this.silhueta.material.needsUpdate = true;
    }
    /* dormindo (sono.ts): o quadro parado achatado, respirando, num tom apagado */
    const mo = jogoAtual().motor, dorme = !ovo && mo.acao === "dormir";
    /* a cena da acao do motor, o cocô e a reacao ao toque (cenaAcao.ts; so vista): o gesto do corpo sobre o desenho. Parado e acordado ele faz o da acao */
    const gesto = ovo ? SEM_GESTO : gestoAgora({ acao: mo.acao, sujeira: mo.e.sujeira, chave: String(mo.semente) }, p.agora, p.reduzido, !andando && !dorme, velocidadeAtual() <= 0, noClipe, emburra);
    const alt = (dorme ? alturaSono(p.agora, p.reduzido) : 1) * gesto.estica;
    this.papel.material.color.setHex(p.noite ? NOITE_PAPEL : dorme ? SONO.tom : 0xffffff);
    /* o lado ao longo da direita da camera no chao (com a camera livre ela gira; fixa, e o x do mundo): no golpe, o do ponto em que o pet
       bate e o da comida no "comeu a racao" (SA-4); fora deles, o do passo da posicao desenhada */
    const dir = this.v.set(1, 0, 0).applyQuaternion(p.camera.quaternion), h = Math.hypot(dir.x, dir.z) || 1;
    const naDireita = (x: number, z: number) => (x * dir.x + z * dir.z) / h;
    const alvo = golpe?.alvo ?? (noClipe && comer.momento ? comer.alvo : null);
    if (alvo) { const d = naDireita(alvo[0] - p.cel[0], alvo[1] - p.cel[1]); if (Math.abs(d) > LADO_MIN) this.lado = d > 0 ? 1 : -1; }
    else if (this.celAntes !== null) {
      const dx = naDireita(p.cel[0] - this.celAntes[0], p.cel[1] - this.celAntes[1]);
      if (dx > LADO_MIN) this.lado = 1; else if (dx < -LADO_MIN) this.lado = -1;
    }
    this.celAntes = [p.cel[0], p.cel[1]];
    const passo = VIRAR_POR_S * p.dt;
    this.escalaX = p.reduzido || Math.abs(this.lado - this.escalaX) <= passo ? this.lado : this.escalaX + Math.sign(this.lado - this.escalaX) * passo;
    /* o tamanho em pixels inteiros do canvas; o pulinho em texels inteiros; o ovo balanca um texel de lado */
    const n = p.pxPorTexel, wpx = Math.round(folha.w * n * (dorme || gesto.estica !== 1 ? 1 + (1 - alt) / 2 : 1)), hpx = Math.round(folha.h * n * alt), { nascendo } = jogoAtual();
    const pulo = (andando && !p.reduzido && !ovo ? Math.round(Math.abs(Math.sin(p.agora / PULO_MS)) * PULO_TEXELS) * n : 0) + Math.round(gesto.alto) * n;
    const balanco = ovo && !p.reduzido ? balancoOvo(nascendo) * n : 0;
    /* o pe do papel no chao (o foco: sem dobra), projetado; o canto vai ao pixel inteiro mais perto */
    this.v.set(p.cel[0], 0, p.cel[1]).project(p.camera);
    const [W, H] = p.canvas, ax = ((this.v.x + 1) / 2) * W, ay = ((1 - this.v.y) / 2) * H;
    const esquerda = Math.round(ax - wpx / 2) + balanco + Math.round(gesto.frente) * n * this.lado, base = Math.round(ay) - pulo;
    const dx = (esquerda + wpx / 2 - ax) / p.ppu, dy = (ay - base) / p.ppu;
    const cam = p.camera, direita = this.v.set(1, 0, 0).applyQuaternion(cam.quaternion).clone(), cima = new THREE.Vector3(0, 1, 0).applyQuaternion(cam.quaternion);
    this.papel.quaternion.copy(cam.quaternion);
    this.papel.position.set(0, 0, 0).addScaledVector(direita, dx).addScaledVector(cima, dy);
    this.papel.scale.set((Math.abs(this.escalaX) < 0.06 ? 0.06 * Math.sign(this.escalaX || 1) : this.escalaX) * wpx / p.ppu, hpx / p.ppu, 1);
    this.raiz.position.set(p.cel[0], 0, p.cel[1]);
    const larg = wpx / p.ppu;
    this.sombra.scale.set(larg * 0.85, 1, larg * 0.42);
    this.sombra.position.set(0, 0.03, 0);
    return { x: esquerda / p.razao, y: (base - hpx) / p.razao, w: wpx / p.razao, h: hpx / p.razao };
  }

  /** solta as texturas */
  dispose(): void { for (const f of this.folhas.values()) f.tex.dispose(); this.folhas.clear(); esquecerComer(); marcarEmburrar(false); }
}
