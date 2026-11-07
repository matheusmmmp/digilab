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
     - a noite, o papel fica no tom NOITE_PAPEL (o papel nao recebe luz: e o tom da cena noturna);
     - na mao do dono (docs/TAREFA_V3_PEGAR_PET.md, P2; `suspenso`, as contas em mao.ts): o papel sobe do chao, pende do alto e balanca com
       um tremor, e a careta usa poses que ja existem (PP-3): o Medo nas formas com as reacoes de rosto (com o emote gota delas), o Stun
       nas outras; nenhuma parte acrescentada, nenhum sprite novo. A sombra fica onde ele vai cair. Logo depois de soltar, a queda e o
       quique; a posicao nova do motor nao conta como andar.
   Sem o atlas (os e2e e as capturas; ou carregando), a grade de reserva do jogo (fontePet.ts). So desenho: PROPOSTO, SEM FONTE. */
import * as THREE from "three";
import { OVO, chaveSprite } from "../../../../motor/index.ts";
import { CLIPES_REACOES, atlasAtual, chaveUp, desenharSprite, dimSprite, quadroAgora, type AtlasOk, type Clipe, type ClipeReacao } from "../../../atlas.ts";
import { balancoOvo, jogoAtual } from "../../../jogo.ts";
import { SONO, alturaSono } from "../sono.ts";
import { SEM_GESTO, escolherComer, esquecerComer, marcarEmburrar, marcarDormir, gestoAgora, type EscolhaComer } from "../cenaAcao.ts";
import { CENA } from "../cenaEstado.ts";
import { bobDaReacao, escolherReacao, marcarReacaoRosto } from "../reacao.ts";
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
  /** a altura do chao dobrado sob o pet desenhado (curva.ts, dobrarY; 0 no foco da dobra; o papel nao passa pela dobra do shader): com o pet na mao,
      com a camera solta (cameraLivre.ts) ou numa viagem a um lugar o foco sai do pet, o chao sob ele desce, e o papel desce junto */
  yPe?: number;
  /** o pet suspenso: na mao do dono, ou caindo logo depois de solto; null no chao */
  suspenso?: Suspenso | null;
}
/** o pet fora do chao (mao.ts): `altura` em texels sobre o chao, `angulo` do pendulo (rad; positivo, o pe vai para a direita na tela),
    `tremor` em texels de lado e `sombra`, onde ele vai cair (celulas, ja no mapa; null: embaixo dele) */
export interface Suspenso { naMao: boolean; altura: number; angulo: number; tremor: number; sombra: readonly [number, number] | null }

interface Folha { tex: THREE.CanvasTexture; w: number; h: number }

/** a borda branca do papel em volta do que e opaco; o que nao e opaco (a sombra do export) sai; corta fora do `corte`, entao o centro
    do papel e o centro do que se ve do Digimon (a sombra cai embaixo dele, e a virada de lado nao o faz pular). O corte alargado pode
    passar das bordas do quadro: o que fica fora e transparente */
function recortar(c: HTMLCanvasElement, corte: Corte): HTMLCanvasElement {
  const B = BORDA_PAPEL, topo = corte.topo ?? 0, cw = corte.x1 - corte.x0 + 1, ch = Math.min(c.height, corte.pe) - topo, w = cw + 2 * B, h = ch + 2 * B;
  const s = document.createElement("canvas");
  s.width = w; s.height = h;
  const g = s.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  const sx0 = Math.max(0, corte.x0), sx1 = Math.min(c.width - 1, corte.x1);
  if (sx1 >= sx0) g.drawImage(c, sx0, topo, sx1 - sx0 + 1, ch, B + sx0 - corte.x0, B, sx1 - sx0 + 1, ch);
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
/** a linha mais alta com pixel opaco (alfa >= 230) e o centro das colunas opacas dela (em meios texels: coluna + 0,5); null se nada e opaco */
function topoOpaco(c: HTMLCanvasElement): { linha: number; cx: number } | null {
  const g = c.getContext("2d", { willReadFrequently: true });
  if (!g) throw new Error("canvas 2d indisponível");
  const px = g.getImageData(0, 0, c.width, c.height).data;
  for (let y = 0; y < c.height; y++) {
    let x0 = -1, x1 = -1;
    for (let x = 0; x < c.width; x++) if (px[(y * c.width + x) * 4 + 3] >= 230) { if (x0 < 0) x0 = x; x1 = x; }
    if (x0 >= 0) return { linha: y, cx: (x0 + x1 + 1) / 2 };
  }
  return null;
}
/** o corte inteiro de um canvas (a grade de reserva: ela nao tem sombra nem folga) */
const corteInteiro = (c: HTMLCanvasElement): Corte => ({ x0: 0, x1: c.width - 1, pe: c.height });
/** o tom do papel a noite (multiplica a textura) */
const NOITE_PAPEL = 0xaab6dd;
/** o eixo do pendulo: o z local do papel (o eixo da camera, ja que o papel copia a orientacao dela) */
const EIXO_Z = new THREE.Vector3(0, 0, 1);
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
  /** a coluna do topo do quadro Dormir (fracao da largura do papel, sem espelhar), por corte; `zzFx` e a de agora (null fora do quadro Dormir) */
  private readonly zzs = new Map<string, number>();
  private zzFx: number | null = null;
  /** o alto da cabeca do quadro de uma reacao de rosto (fracoes da largura e da altura do papel, sem espelhar), por corte; `cabecaF` e o de agora */
  private readonly cabecas = new Map<string, [number, number]>();
  private cabecaF: [number, number] | null = null;
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
  private readonly giro = new THREE.Quaternion();

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
  private folhaAgora(quadro: number, andando: boolean, agora: number, golpe: Passo["golpe"], comer: EscolhaComer, emburra: boolean, dormeQ: boolean, rosto: ClipeReacao | null, stun = false): { folha: Folha; ovo: boolean } {
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
    const dorm = dormeQ && !ovo && !bate && !come && !emb;
    if (dorm && !s?.clipes?.Dormir) throw new Error("o sono escolheu o clipe Dormir num sprite sem ele: " + nome);
    const ros = rosto !== null && !ovo && !bate && !come && !emb && !dorm;
    if (ros && !s?.clipes?.[rosto]) throw new Error(`a reacao escolheu o clipe ${rosto} num sprite sem ele: ` + nome);
    const stu = stun && !ovo && !bate && !come && !emb && !dorm && !ros;
    if (stu && !s?.clipes?.Stun) throw new Error("a careta na mao escolheu o clipe Stun num sprite sem ele: " + nome);
    const clipe: Clipe = bate ? "Attack_1" : come ? "Comer" : emb ? "Emburrar" : dorm ? "Dormir" : ros ? rosto : stu ? "Stun" : !ovo && andando && s?.clipes?.Run ? "Run" : "Idle";
    if (clipe !== this.clipe || (bate && golpe!.desde !== this.golpeDesde)) { this.clipe = clipe; this.t0 = bate ? golpe!.desde : agora; }
    this.golpeDesde = bate ? golpe!.desde : null;
    if (come) this.t0 = comer.desde;
    const iq = ovo ? 0 : quadroAgora(a, nome, m.acao === "dormir" && !bate, clipe, this.t0), sombria = !ovo && m.sombria;
    const corte = dorm ? this.corteDormir(a, nome, sombria) : bate || come || emb || ros || stu ? this.corteAlargado(a, nome, sombria, clipe) : this.corte(a, nome, sombria);
    this.cabecaF = ros ? this.cabecaDe(a, nome, sombria, clipe, corte) : null;
    return { folha: this.folha(`${nome}|${clipe}|${iq}|${sombria ? 1 : 0}`, () => recortar(quadroAtlas(a, nome, iq, sombria, clipe), corte)), ovo };
  }
  /** a forma de agora tem o clipe Emburrar no atlas? (sem atlas, no ovo ou sem o clipe: fica o tremor de cenaAcao.ts) */
  private temEmburrar(): boolean {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    return a.tipo === "ok" && nascendo <= 0 && !!a.dados.sprites[chaveUp(a.dados, chaveSprite(m.forma))]?.clipes?.Emburrar;
  }
  /** a forma de agora tem o clipe Dormir no atlas? (sem atlas, no ovo ou sem o clipe: fica o sono de sono.ts, achatado) */
  private temDormir(): boolean {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    return a.tipo === "ok" && nascendo <= 0 && !!a.dados.sprites[chaveUp(a.dados, chaveSprite(m.forma))]?.clipes?.Dormir;
  }
  /** a forma de agora tem o clipe Stun no atlas? (a careta na mao das formas sem as reacoes de rosto; sem o atlas ou no ovo, nao) */
  private temStun(): boolean {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    return a.tipo === "ok" && nascendo <= 0 && !!a.dados.sprites[chaveUp(a.dados, chaveSprite(m.forma))]?.clipes?.Stun;
  }
  /** a forma de agora tem as reacoes de rosto no atlas? (so os Digimon do estagio crianca; sem o atlas, no ovo ou sem elas: nada muda) */
  private temReacoes(): boolean {
    const { motor: m, nascendo } = jogoAtual(), a = atlasAtual();
    return a.tipo === "ok" && nascendo <= 0 && CLIPES_REACOES.every(r => !!a.dados.sprites[chaveUp(a.dados, chaveSprite(m.forma))]?.clipes?.[r]);
  }
  /** onde fica o alto da cabeca no papel de um clipe de reacao (o quadro 0; so o rosto muda, entao e o da silhueta do Idle): a coluna central da
      primeira linha opaca e essa linha, em fracoes do papel (a borda do papel entra), para o emote sair dali */
  private cabecaDe(a: AtlasOk, nome: string, sombria: boolean, clipe: Clipe, corte: Corte): [number, number] {
    const ch = `${nome}|${sombria ? 1 : 0}|${clipe}`, pronto = this.cabecas.get(ch);
    if (pronto) return pronto;
    const q = quadroAtlas(a, nome, 0, sombria, clipe), t = topoOpaco(q);
    if (!t) throw new Error(`o quadro ${clipe} de ${nome} e todo transparente`);
    const B = BORDA_PAPEL, topo = corte.topo ?? 0, cw = corte.x1 - corte.x0 + 1, h = Math.min(q.height, corte.pe) - topo + 2 * B;
    const f: [number, number] = [(t.cx - corte.x0 + B) / (cw + 2 * B), (t.linha - topo + B) / h];
    this.cabecas.set(ch, f);
    return f;
  }
  /** o corte do quadro Dormir: o alargado (mesmo centro e mesmo pe do Idle) e, em cima, so a partir do topo do que e opaco, para o retangulo
      do pet comecar na cabeca (o "zz" sai dali). Guarda a coluna do topo (fracao da largura do papel, sem espelhar) em `zzFx` */
  private corteDormir(a: AtlasOk, nome: string, sombria: boolean): Corte {
    const ch = `${nome}|${sombria ? 1 : 0}|Dormir`, pronto = this.cortes.get(ch);
    if (pronto) { this.zzFx = this.zzs.get(ch) ?? null; return pronto; }
    const q = quadroAtlas(a, nome, 0, sombria, "Dormir"), caixa = caixaOpaca(q), t = topoOpaco(q);
    if (!caixa || !t) throw new Error("o quadro Dormir de " + nome + " e todo transparente");
    const al = alargarCorte(this.corte(a, nome, sombria), [caixa]), final: Corte = { ...al, topo: t.linha };
    this.cortes.set(ch, final);
    const B = BORDA_PAPEL, fx = (t.cx - al.x0 + B) / (al.x1 - al.x0 + 1 + 2 * B);
    this.zzs.set(ch, fx); this.zzFx = fx;
    return final;
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
    const chaveMotor = `${p.motor[0]},${p.motor[1]}`, sus = p.suspenso ?? null, naMao = !!sus?.naMao;
    /* suspenso (na mao ou caindo), a posicao do motor que muda (o "levar pet") nao e andar */
    if (chaveMotor !== this.motorAntes) { if (this.motorAntes && !sus) this.mudouEm = p.agora; this.motorAntes = chaveMotor; }
    if (sus) this.mudouEm = -1e9;
    const golpe = naMao ? null : p.golpe ?? null, andaBase = !sus && (!!p.andandoVista || p.agora - this.mudouEm < ANDANDO_MS);
    /* o comer (cenaAcao.ts, escolherComer): o laco cede ao passo e ao golpe; o "comeu a racao" cede so ao golpe, e o pet para de andar nele */
    const mo0 = jogoAtual(), mu = mo0.motor.mundo, sub = mu?.cm.sub ?? 1, nCons = mu?.consumos.length ?? 0;
    const ultimo = nCons > 0 ? (mu!.consumos[nCons - 1] as { id?: number }).id : undefined;
    const comer = escolherComer({
      chave: String(mo0.motor.semente), acao: mo0.nascendo > 0 ? "" : mo0.motor.acao, consumos: nCons,
      alvo: ultimo !== undefined ? this.comidasAntes.get(ultimo) ?? null : null, ciclo: this.cicloComer(),
      velocidade: velocidadeAtual(), andando: andaBase || !!golpe, pausa: velocidadeAtual() <= 0, donoDesde: flashDesde(),
    }, p.agora);
    this.comidasAntes = new Map([...(mu?.comidas.values() ?? [])].map(c => [c.id, [c.x / sub, c.y / sub] as const]));
    const noClipe = comer.tocou === "clipe" && !golpe && !naMao;
    this.comer = golpe && comer.tocou === "clipe" ? null : comer.tocou;
    const andando = !golpe && !noClipe && andaBase;
    /* o emburrar: o clipe Emburrar (laco) toca com o pet parado e acordado na acao `emburrar`; o tremor programatico sai (o clipe e o corpo) */
    const emburra = !naMao && !golpe && !noClipe && !andando && mo0.nascendo <= 0 && mo0.motor.acao === "emburrar" && this.temEmburrar();
    /* o dormir: com o quadro Dormir do atlas, o quadro e o corpo (sem achatar, sem escurecer, sem respirar); sem ele, o sono de sono.ts */
    const dormeQ = !naMao && !golpe && !noClipe && mo0.nascendo <= 0 && mo0.motor.acao === "dormir" && this.temDormir();
    /* a reacao de rosto (reacao.ts): parado, acordado e sem outro clipe no corpo, o quadro da reacao no lugar do Idle, com o emote por cima */
    let rosto: ClipeReacao | null = null, stun = false;
    /* na mao, a careta (PP-3): o Medo nas formas com as reacoes de rosto, o Stun nas outras */
    if (naMao && mo0.nascendo <= 0) { if (this.temReacoes()) rosto = "Medo"; else stun = this.temStun(); }
    else if (!golpe && !noClipe && !andando && !emburra && !dormeQ && mo0.nascendo <= 0 && this.temReacoes()) {
      const mt = mo0.motor, r = escolherReacao({ chave: String(mt.semente), humor: mt.e.humor, energia: mt.e.energia, saude: mt.e.saude,
        lesionado: mt.lesionadoDesde !== null, dormindo: mt.acao === "dormir" }, p.agora);
      if (r?.mostrar) rosto = r.reacao;
    }
    this.zzFx = null; this.cabecaF = null;
    const { folha, ovo } = this.folhaAgora(p.quadro, andando, p.agora, golpe, comer, emburra, dormeQ, rosto, stun);
    marcarEmburrar(emburra && !ovo); marcarDormir(dormeQ && !ovo); marcarReacaoRosto(rosto && !ovo ? rosto : null);
    if (this.papel.material.map !== folha.tex) {
      this.papel.material.map = this.silhueta.material.map = folha.tex;
      this.papel.material.needsUpdate = this.silhueta.material.needsUpdate = true;
    }
    /* dormindo (sono.ts): o quadro parado achatado, respirando, num tom apagado */
    const mo = jogoAtual().motor, dorme = !ovo && mo.acao === "dormir";
    /* a cena da acao do motor, o cocô e a reacao ao toque (cenaAcao.ts; so vista): o gesto do corpo sobre o desenho. Parado e acordado ele faz o da acao */
    const gesto0 = ovo || naMao ? SEM_GESTO : gestoAgora({ acao: mo.acao, sujeira: mo.e.sujeira, chave: String(mo.semente) }, p.agora, p.reduzido, !andando && !dorme, velocidadeAtual() <= 0, noClipe, emburra);
    /* a expressao se mexe 1 texel inteiro (reacao.ts, bobDaReacao); sem reacao, o gesto de sempre */
    const gesto = rosto && !ovo && !naMao ? { ...gesto0, alto: gesto0.alto + bobDaReacao(p.agora, p.reduzido) } : gesto0;
    const achata = dorme && !dormeQ, alt = (achata ? alturaSono(p.agora, p.reduzido) : 1) * gesto.estica;
    this.papel.material.color.setHex(p.noite ? NOITE_PAPEL : achata ? SONO.tom : 0xffffff);
    /* o lado ao longo da direita da camera no chao (com a camera livre ela gira; fixa, e o x do mundo): no golpe, o do ponto em que o pet
       bate e o da comida no "comeu a racao" (SA-4); fora deles, o do passo da posicao desenhada */
    const dir = this.v.set(1, 0, 0).applyQuaternion(p.camera.quaternion), h = Math.hypot(dir.x, dir.z) || 1;
    const naDireita = (x: number, z: number) => (x * dir.x + z * dir.z) / h;
    const alvo = golpe?.alvo ?? (noClipe && comer.momento ? comer.alvo : null);
    if (alvo) { const d = naDireita(alvo[0] - p.cel[0], alvo[1] - p.cel[1]); if (Math.abs(d) > LADO_MIN) this.lado = d > 0 ? 1 : -1; }
    /* suspenso (na mao ou caindo), o lado fica o de quando ele foi pego: o arrasto nao vira a folha (ela passaria pela largura 0) */
    else if (this.celAntes !== null && !sus) {
      const dx = naDireita(p.cel[0] - this.celAntes[0], p.cel[1] - this.celAntes[1]);
      if (dx > LADO_MIN) this.lado = 1; else if (dx < -LADO_MIN) this.lado = -1;
    }
    this.celAntes = [p.cel[0], p.cel[1]];
    const passo = VIRAR_POR_S * p.dt;
    this.escalaX = p.reduzido || Math.abs(this.lado - this.escalaX) <= passo ? this.lado : this.escalaX + Math.sign(this.lado - this.escalaX) * passo;
    /* o tamanho em pixels inteiros do canvas; o pulinho em texels inteiros; o ovo balanca um texel de lado */
    const n = p.pxPorTexel, wpx = Math.round(folha.w * n * (achata || gesto.estica !== 1 ? 1 + (1 - alt) / 2 : 1)), hpx = Math.round(folha.h * n * alt), { nascendo } = jogoAtual();
    const pulo = (andando && !p.reduzido && !ovo ? Math.round(Math.abs(Math.sin(p.agora / PULO_MS)) * PULO_TEXELS) * n : 0) + Math.round(gesto.alto) * n
      + (sus ? Math.round(sus.altura) * n : 0);
    const balanco = ovo && !p.reduzido ? balancoOvo(nascendo) * n : 0;
    /* o pe do papel no chao dobrado sob o pet (no foco, sem dobra), projetado; o canto vai ao pixel inteiro mais perto */
    const yPe = p.yPe ?? 0;
    this.v.set(p.cel[0], yPe, p.cel[1]).project(p.camera);
    const [W, H] = p.canvas, ax = ((this.v.x + 1) / 2) * W, ay = ((1 - this.v.y) / 2) * H;
    const esquerda = Math.round(ax - wpx / 2) + balanco + Math.round(gesto.frente) * n * this.lado + (sus ? Math.round(sus.tremor) * n : 0), base = Math.round(ay) - pulo;
    const dx = (esquerda + wpx / 2 - ax) / p.ppu, dy = (ay - base) / p.ppu;
    const cam = p.camera, direita = this.v.set(1, 0, 0).applyQuaternion(cam.quaternion).clone(), cima = new THREE.Vector3(0, 1, 0).applyQuaternion(cam.quaternion);
    this.papel.quaternion.copy(cam.quaternion);
    this.papel.position.set(0, 0, 0).addScaledVector(direita, dx).addScaledVector(cima, dy);
    /* o pendulo: o papel gira no plano da imagem em volta do alto dele (a "nuca" na mao do dono) */
    const ang = sus?.angulo ?? 0;
    if (ang !== 0) {
      const hw = hpx / p.ppu;
      this.papel.quaternion.multiply(this.giro.setFromAxisAngle(EIXO_Z, ang));
      this.papel.position.addScaledVector(direita, hw * Math.sin(ang)).addScaledVector(cima, hw * (1 - Math.cos(ang)));
    }
    this.papel.scale.set((Math.abs(this.escalaX) < 0.06 ? 0.06 * Math.sign(this.escalaX || 1) : this.escalaX) * wpx / p.ppu, hpx / p.ppu, 1);
    this.raiz.position.set(p.cel[0], yPe, p.cel[1]);
    const larg = wpx / p.ppu;
    this.sombra.scale.set(larg * 0.85, 1, larg * 0.42);
    /* a sombra passa pela dobra do shader: a altura dela desconta a do pe; na mao, ela fica onde o pet vai cair */
    const somb = sus?.sombra ?? null;
    this.sombra.position.set(somb ? somb[0] - p.cel[0] : 0, 0.03 - yPe, somb ? somb[1] - p.cel[1] : 0);
    const ret = { x: esquerda / p.razao, y: (base - hpx) / p.razao, w: wpx / p.razao, h: hpx / p.razao };
    /* o "zz" sai do alto da cabeca do quadro Dormir: a coluna do topo do que e opaco (espelhada com o papel), em px de CSS da cena */
    CENA.zzX = this.zzFx === null ? null : ret.x + ret.w * (this.escalaX < 0 ? 1 - this.zzFx : this.zzFx);
    /* o alto da cabeca da reacao de rosto, em px de CSS da cena: o emote sai dali (PalcoPet.desenharIcone) */
    CENA.cabeca = this.cabecaF === null ? null : [ret.x + ret.w * (this.escalaX < 0 ? 1 - this.cabecaF[0] : this.cabecaF[0]), ret.y + ret.h * this.cabecaF[1]];
    return ret;
  }

  /** solta as texturas */
  dispose(): void { for (const f of this.folhas.values()) f.tex.dispose(); this.folhas.clear(); esquecerComer(); marcarEmburrar(false); marcarDormir(false); marcarReacaoRosto(null); CENA.zzX = null; CENA.cabeca = null; }
}
