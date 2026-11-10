/* O desenho da luta da POC no canvas (LUTA_POC, LP3; docs/TAREFA_V3_LUTA_POC.md, secoes 3.3 e 3.3a). So apresentacao: le a Luta da simulacao
   (motor/arena/, refeita passo a passo da mesma entrada) e o estado visual (visualPoc.ts), nunca os altera.
   - O chao e o da POC: a elipse 2D vista de lado, com o mapa do UP de cada uma das 8 arenas e a regra dela a vista (a area que fecha, a mare,
     a areia e a tempestade, a runa e os pilares, a lava e as erupcoes, as arvores e as moitas, o ringue sem cerca). A base e o desenho do
     #446/#448 (web/app/src/telas/lutar/arena_tr/desenho.ts no efb2ded), no mundo de 480 x 280 da simulacao.
   - Os lutadores sao os sprites do atlas do jogo (src/atlas.ts) em escala inteira de pixel, com os clipes Idle, Run, Attack_1, Stun e Die
     seguindo o estado da simulacao; o tempo do clipe e o da luta (os passos de 16 ms). Nada se acrescenta as poses.
   - Os projeteis voam com o desenho do jogo (os prefabs de Assets/arena_up/efeitos, efeitosJogo.ts), por cima do rastro e do brilho do
     elemento (E2); o projetil nosso (LP-8) do mesmo jeito.
   - Os efeitos da LUTA_EFEITOS (E1 a E5) vem dos geradores de pixel do palco de antes (portados para efeitos.ts, projeteis.ts, chao.ts,
     posturas.ts, elementos.ts e nocaute.ts na LP4: a mesma grade, as mesmas cores, os mesmos numeros). */
import { CENAS, ELIPSE_POC, EQ_POC, MUNDO_POC, PASSO_POC_MS, type IdCena, type LutadorPoc } from "../../../../motor/index.ts";
import { chaveUp, desenharSprite, dimSprite, quadroDoClipe, type AtlasOk, type Clipe } from "../../../atlas.ts";
import { zoomAtual } from "../../../escala.ts";
import { imagemMapa, prontas } from "./imagensMapa.ts";
import { ELEMENTO, elementoDoSprite, type ElementoTR } from "./elementos.ts";
import { COR_FORTE, COR_TINTA, MOVIMENTO, faiscaDoPasso, pixelsDoTexto, poeiraDoPasso } from "./efeitos.ts";
import { VOO, pixelsDaCabeca, pixelsDoEstouro, pixelsDoRastro, type PixelTR } from "./projeteis.ts";
import { CHAO, alfaDaMarca, pixelsDaCratera, pixelsDaOnda, pixelsDaTelegrafia, pixelsDoArrasto, poeiraDaNuvem } from "./chao.ts";
import { POSTURA, pixelsDaAura } from "./posturas.ts";
import { efeitosAtuais, folhaEfeito, type EfeitoRef } from "./efeitosJogo.ts";
import {
  TELA_POC, claraoPoc, escuroDoPasso, koDoPasso, lutadorN, nivelDoQuadro, passoDe, pixelsDoKO, preparoDaHabilidade, puloDoEmpurrao, tremidaPoc,
  type LadoN, type VisualPoc,
} from "./visualPoc.ts";
import type { LutaPoc, DadosFormaPoc } from "../../../../motor/index.ts";

const { w: MW, h: MH } = MUNDO_POC;
const { cx: CX, cy: CY, rx: RX, ry: RY } = ELIPSE_POC;
/** cores do chao liso (o Campo de treino, e o recuo quando o mapa nao carrega); as do prototipo */
const COR = { ceu: "#cfe6f5", chaoA: "#9fcf7a", chaoB: "#8cc068", borda: "#5d8a44", azul: "#2c73e0", vermelho: "#d6336c", fundo: "#141a24" };

/** a arte de cada arena (os recortes dos mapas do jogo em Assets/arena_up/mapas): a mesma tabela do #446 */
export const VISUAL_POC: Record<IdCena, { piso?: string; fundo?: string; fundoCobre?: boolean; fundoAlt?: number; ceu?: [string, string] }> = {
  campo: {},
  coliseu: { piso: "coliseu_piso.jpg", fundo: "coliseu_fundo.jpg", fundoCobre: true },
  floresta: { piso: "floresta_piso.jpg", fundo: "floresta_fundo.png", fundoAlt: 92 },
  praia: { piso: "praia_piso.jpg", ceu: ["#9fd3ef", "#d9f0f7"] },
  deserto: { piso: "deserto_piso.jpg", ceu: ["#f3c27a", "#fbe3b6"] },
  castelo: { piso: "castelo_piso.jpg", fundo: "castelo_fundo.png", fundoAlt: 96, ceu: ["#2a2346", "#4b3b6e"] },
  caverna: { piso: "caverna_piso.jpg", ceu: ["#0d1016", "#1d2430"] },
  ringue: { piso: "ringue_piso.jpg", fundo: "ringue_fundo.jpg", fundoCobre: true },
};
/** os arquivos de mapa que uma arena usa (pede o carregamento) */
export function arquivosPoc(id: IdCena): string[] {
  const v = VISUAL_POC[id];
  const arqs = [v.piso, v.fundo, ...(CENAS[id].obst || []).map(o => o[3] + ".png"), id === "caverna" ? "fogo.png" : undefined].filter((x): x is string => !!x);
  for (const a of [...new Set(arqs)]) void imagemMapa(a);
  return [...new Set(arqs)];
}
const img = (arq: string): HTMLImageElement | null => prontas.get(arq) ?? null;

/** Os tamanhos desta tela. PROPOSTOS, SEM FONTE: ajustar nas capturas.
    - efeito: quantos pixels do mundo vale um pixel da folha de efeito do jogo (as folhas sao de alta resolucao);
    - pes: quantos pixels do mundo o sprite desce abaixo do y do lutador (os pes na elipse);
    - margem: a folga (mundo) em volta dos dois lutadores que a camera deixa na tela no zoom */
export const DESENHO_POC = { efeito: .22, pes: 9, margem: [70, 90] } as const;

/** o usuario pediu menos movimento: sem tremida, clarao, poeira nem camera lenta (os numeros, o "K.O." e a barra ficam) */
export const movimentoReduzido = (): boolean => typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/** um lado no palco: a chave da tabela da arena (a forma do jogo ou o NPC: o elemento sai dela), o sprite do atlas (o NPC usa o de outro
    Digimon: NPC.sprite), o nome na tela e os dados da forma */
export interface LadoDesenhoPoc { chave: string; sprite: string; nomeTela: string; forma: DadosFormaPoc }
export interface CenaPocDesenho { L: LutaPoc; v: VisualPoc; A: LadoDesenhoPoc; B: LadoDesenhoPoc }

/** o elemento de um lado (E2, D-LE-1): o da chave da tabela; o NPC que usa o sprite de outro Digimon (o Piedmon, com o do Soberano) e sem
    elemento proprio cai no do sprite, que falha alto se tambem nao tiver */
export function elementoDoLado(f: LadoDesenhoPoc): ElementoTR {
  try { return elementoDoSprite(f.chave); } catch { return elementoDoSprite(f.sprite); }
}
/** o clipe de um lutador e o tempo dentro dele (ms da luta): o estado da simulacao vira o clipe do atlas */
export function clipeDoLutador(u: LutadorPoc, extraMs: number): { clipe: Clipe; t: number } {
  if (u.morto || u.estado === "die") return { clipe: "Die", t: u.t + extraMs };
  const c: Record<LutadorPoc["estado"], Clipe> = { idle: "Idle", run: "Run", attack: "Attack_1", stun: "Stun", die: "Die" };
  return { clipe: c[u.estado], t: u.t };
}

/** a geometria do quadro: px do canvas por pixel do mundo (e, fracionario), a escala inteira dos sprites (es), o centro da camera (no mundo) e
    a altura da tela onde ele fica (oy, fracao: no celular em pe o chao desce, para o HUD e os cartoes caberem em cima) */
export interface GeoPoc { K: number; W: number; H: number; Wp: number; Hp: number; e: number; es: number; e0: number; cx: number; cy: number; oy: number }
export const xDe = (g: GeoPoc, x: number): number => g.Wp / 2 + (x - g.cx) * g.e;
export const yDe = (g: GeoPoc, y: number): number => g.Hp * g.oy + (y - g.cy) * g.e;

/** a camera do quadro: a escala de base cabe o mundo inteiro (480 x 280); o zoom a sobe em niveis de um terco (E5: 1, 1,33 e 1,67), sem
    tirar nenhum dos dois da tela; o centro fica dentro do mundo. Os sprites ficam sempre em escala inteira de pixel (es) */
export function geometriaPoc(Wp: number, Hp: number, K: number, W: number, H: number, v: VisualPoc, L: LutaPoc, passo: number, reduzido: boolean): GeoPoc {
  /* o mundo inteiro cabe em efit; no celular em pe a base aproxima um quarto (a camera acompanha os dois, e o mundo inteiro volta quando
     eles se afastam) */
  const efit = Math.min(Wp / MW, Hp / MH), e0 = H > W ? efit * 1.25 : efit, vivos = [L.a, L.b].filter(u => !u.foraAte);
  const xs = vivos.map(u => u.x), ys = vivos.map(u => u.y);
  const dx = xs.length ? Math.max(...xs) - Math.min(...xs) : 0, dy = ys.length ? Math.max(...ys) - Math.min(...ys) : 0;
  const cabe = Math.min(Wp / (dx + 2 * DESENHO_POC.margem[0]), Hp / (dy + 2 * DESENHO_POC.margem[1]));
  const e = Math.max(efit, Math.min(cabe, e0 * (1 + nivelDoQuadro(v.cam, passo, reduzido) / 3)));
  const prender = (c: number, meia: number, max: number) => (meia * 2 >= max ? max / 2 : Math.max(meia, Math.min(max - meia, c)));
  const cam = v.cam ?? { cx: CX, cy: CY - 30 };
  const oy = H > W ? .62 : .52;
  const cx = prender(cam.cx, Wp / 2 / e, MW), cy = prender(cam.cy, Hp / 2 / e, MH);
  return { K, W, H, Wp, Hp, e, es: Math.max(1, Math.round(e)), e0, cx, cy, oy };
}

function ajustar(cv: HTMLCanvasElement): { K: number; W: number; H: number } {
  const pai = cv.parentElement, W = pai && pai.clientWidth > 0 ? pai.clientWidth : 390, H = pai && pai.clientHeight > 0 ? pai.clientHeight : 300;
  const K = (devicePixelRatio || 1) * zoomAtual(), bw = Math.round(W * K), bh = Math.round(H * K);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; cv.style.width = W + "px"; cv.style.height = H + "px"; }
  return { K, W, H };
}

/** pinta pixels de efeito (os geradores portados do palco de antes) em volta de (X, Y), px do canvas, com u px do canvas por pixel de efeito; dir -1 espelha */
function pintar(cx: CanvasRenderingContext2D, px: readonly PixelTR[], X: number, Y: number, u: number, dir: number): void {
  const x0 = Math.round(X), y0 = Math.round(Y);
  for (const luz of [true, false]) {
    cx.globalCompositeOperation = luz ? "lighter" : "source-over";
    for (const p of px) if (p.luz === luz) {
      const t = p.tam * u; cx.globalAlpha = p.alfa; cx.fillStyle = p.cor;
      cx.fillRect(x0 + dir * p.dx * u - (dir < 0 ? t - u : 0), y0 + p.dy * u, t, t);
    }
  }
  cx.globalCompositeOperation = "source-over"; cx.globalAlpha = 1;
}

/** um quadro de um efeito do jogo (o prefab) no instante t (ms), centrado em (x, y) do mundo; loop repete as camadas que nao repetem */
function desenharEfeito(cx: CanvasRenderingContext2D, ref: EfeitoRef, t: number, x: number, y: number, espelho: boolean, loop: boolean, escala: number): boolean {
  const folha = folhaEfeito(ref.dono); if (!folha || t < 0) return false;
  let desenhou = false;
  for (const c of ref.e.c) {
    let i = Math.floor(t / c.ms);
    if (c.loop || loop) i %= c.n; else if (i >= c.n) continue;
    const w = c.r[2] / c.tx, h = c.r[3] / c.ty, sx = c.r[0] + (i % c.tx) * w, sy = c.r[1] + Math.floor(i / c.tx) * h;
    cx.save(); cx.translate(Math.round(x), Math.round(y)); if (espelho) cx.scale(-1, 1);
    cx.imageSmoothingEnabled = true;
    cx.drawImage(folha, sx, sy, w, h, -w * escala / 2, -h * escala / 2, w * escala, h * escala); cx.restore();
    desenhou = true;
  }
  return desenhou;
}

/* ---------------------------------------------------------------- o chao e as regras (no mundo; o contexto ja na escala da camera) */
function chao(cx: CanvasRenderingContext2D, id: IdCena): boolean {
  const c = VISUAL_POC[id], piso = c.piso ? img(c.piso) : null;
  const faltou = (!!c.piso && prontas.get(c.piso) === null) || (!!c.fundo && prontas.get(c.fundo) === null);
  if (piso) {
    cx.imageSmoothingEnabled = true;
    if (c.ceu) { const g = cx.createLinearGradient(0, 0, 0, MH); g.addColorStop(0, c.ceu[0]); g.addColorStop(1, c.ceu[1]); cx.fillStyle = g; }
    else cx.fillStyle = COR.ceu;
    cx.fillRect(-MW, -MH, MW * 3, MH * 3);
    const f = c.fundo ? img(c.fundo) : null;
    if (f && c.fundoCobre) { const s = Math.max(MW / f.width, MH / f.height); cx.drawImage(f, (MW - f.width * s) / 2, 0, f.width * s, f.height * s); }
    else if (f && c.fundoAlt) { const alt = c.fundoAlt, larg = f.width * alt / f.height; for (let x = -larg; x < MW + larg; x += larg) cx.drawImage(f, x, 6, larg, alt); }
    cx.beginPath(); cx.ellipse(CX, CY + 6, RX + 8, RY + 10, 0, 0, 7); cx.fillStyle = "rgba(0,0,0,0.45)"; cx.fill();
    cx.save(); cx.beginPath(); cx.ellipse(CX, CY, RX, RY, 0, 0, 7); cx.clip();
    cx.drawImage(piso, CX - RX, CY - RY, RX * 2, RY * 2);
    cx.restore();
    cx.beginPath(); cx.ellipse(CX, CY, RX, RY, 0, 0, 7);
    const semCerca = !!CENAS[id].semCerca;
    cx.strokeStyle = semCerca ? "rgba(255,255,255,0.9)" : "rgba(0,0,0,0.5)"; cx.lineWidth = semCerca ? 2 : 1.5;
    if (semCerca) cx.setLineDash([6, 4]);
    cx.stroke(); cx.setLineDash([]);
    return faltou;
  }
  /* o Campo de treino (ou o mapa que nao carregou): o losango xadrez da POC */
  cx.fillStyle = COR.ceu; cx.fillRect(-MW, -MH, MW * 3, MH * 3);
  cx.save();
  cx.beginPath(); cx.ellipse(CX, CY + 10, RX + 14, RY + 14, 0, 0, Math.PI * 2); cx.fillStyle = COR.borda; cx.fill();
  cx.beginPath(); cx.ellipse(CX, CY, RX, RY, 0, 0, Math.PI * 2); cx.clip();
  const tw = 32, th = 16;
  for (let j = -2; j < 16; j++) for (let i = -2; i < 18; i++) {
    const x = (i - j) * tw / 2 + CX, y = (i + j) * th / 2 + CY - 140;
    cx.beginPath(); cx.moveTo(x, y); cx.lineTo(x + tw / 2, y + th / 2); cx.lineTo(x, y + th); cx.lineTo(x - tw / 2, y + th / 2); cx.closePath();
    cx.fillStyle = (i + j) % 2 ? COR.chaoA : COR.chaoB; cx.fill();
  }
  cx.restore();
  cx.beginPath(); cx.ellipse(CX, CY, RX, RY, 0, 0, Math.PI * 2); cx.strokeStyle = COR.borda; cx.lineWidth = 2; cx.stroke();
  return faltou;
}

/** o que cada arena desenha embaixo dos lutadores: a regra a vista. O tempo das animacoes do chao e o da luta (relogio), nao o do navegador */
function baixo(cx: CanvasRenderingContext2D, L: LutaPoc, reduzido: boolean) {
  const c = L.cena, t = reduzido ? 0 : L.relogio;
  if (c.id === "coliseu" && c.seguro < 1) {
    cx.save(); cx.beginPath(); cx.ellipse(CX, CY, RX, RY, 0, 0, 7); cx.ellipse(CX, CY, RX * c.seguro, RY * c.seguro, 0, 0, 7, true);
    cx.fillStyle = "rgba(200,40,30,0.32)"; cx.fill("evenodd");
    cx.beginPath(); cx.ellipse(CX, CY, RX * c.seguro, RY * c.seguro, 0, 0, 7); cx.strokeStyle = "rgba(255,120,90,0.95)"; cx.lineWidth = 1.5; cx.stroke(); cx.restore();
  } else if (c.id === "praia" && c.linha < CY + RY) {
    cx.save(); cx.beginPath(); cx.ellipse(CX, CY, RX, RY, 0, 0, 7); cx.clip();
    cx.fillStyle = "rgba(40,140,200,0.45)"; cx.fillRect(0, c.linha, MW, MH);
    cx.strokeStyle = "rgba(235,250,255,0.85)"; cx.lineWidth = 1.5; cx.beginPath();
    for (let x = 0; x <= MW; x += 6) cx.lineTo(x, c.linha + Math.sin(x / 14 + t / 300) * 1.6);
    cx.stroke(); cx.restore();
  } else if (c.id === "deserto") {
    const z = c.zonas[0];
    cx.save(); cx.beginPath(); cx.ellipse(z.x, z.y, z.rx, z.ry, 0, 0, 7);
    const g = cx.createRadialGradient(z.x, z.y, 2, z.x, z.y, z.rx);
    g.addColorStop(0, "rgba(120,80,40,0.75)"); g.addColorStop(1, "rgba(170,120,60,0.15)"); cx.fillStyle = g; cx.fill();
    cx.strokeStyle = "rgba(110,72,36,0.55)"; cx.lineWidth = 1;
    for (let k = 1; k <= 3; k++) {
      cx.beginPath();
      for (let a = 0; a < 6.3; a += 0.3) { const r = k / 3 * (1 - a / 14), ang = a + t / 900; cx.lineTo(z.x + Math.cos(ang + k * 2) * z.rx * r, z.y + Math.sin(ang + k * 2) * z.ry * r); }
      cx.stroke();
    }
    cx.restore();
  } else if (c.id === "castelo") {
    const z = c.zonas[0], pronta = c.runaCd <= 0, pulso = 0.5 + 0.5 * Math.sin(t / 250);
    cx.save(); cx.beginPath(); cx.ellipse(z.x, z.y, z.rx, z.ry, 0, 0, 7);
    cx.fillStyle = pronta ? `rgba(170,120,255,${0.25 + 0.25 * pulso})` : "rgba(90,80,120,0.25)"; cx.fill();
    cx.strokeStyle = pronta ? "#d7c2ff" : "rgba(160,150,190,0.6)"; cx.lineWidth = 1.2; cx.stroke();
    cx.beginPath(); cx.ellipse(z.x, z.y, z.rx * 0.55, z.ry * 0.55, 0, 0, 7); cx.stroke();
    for (let i = 0; i < 6; i++) { const a = i / 6 * 6.283 + t / 1500; cx.beginPath(); cx.moveTo(z.x, z.y); cx.lineTo(z.x + Math.cos(a) * z.rx, z.y + Math.sin(a) * z.ry); cx.stroke(); }
    cx.restore();
  } else if (c.id === "caverna") {
    for (const z of c.zonas) {
      const g = cx.createRadialGradient(z.x, z.y, 1, z.x, z.y, z.rx);
      g.addColorStop(0, "rgba(255,210,90,0.95)"); g.addColorStop(0.5, "rgba(255,90,20,0.85)"); g.addColorStop(1, "rgba(120,20,10,0)");
      cx.save(); cx.beginPath(); cx.ellipse(z.x, z.y, z.rx, z.ry, 0, 0, 7); cx.fillStyle = g; cx.fill(); cx.restore();
    }
    for (const e of c.erupcoes) if (!e.explodiu) {
      const p = e.t / 1200;
      cx.beginPath(); cx.ellipse(e.x, e.y, 28, 17, 0, 0, 7); cx.strokeStyle = `rgba(255,140,40,${0.4 + 0.5 * p})`; cx.lineWidth = 1.5; cx.stroke();
      cx.beginPath(); cx.ellipse(e.x, e.y, 28 * p, 17 * p, 0, 0, 7); cx.fillStyle = "rgba(255,110,30,0.35)"; cx.fill();
    }
  }
}

/** o que cada arena desenha por cima: a tempestade do Deserto e o fogo das erupcoes da Caverna */
function cima(cx: CanvasRenderingContext2D, L: LutaPoc, reduzido: boolean) {
  const c = L.cena;
  if (c.id === "deserto" && c.tempestade) {
    cx.fillStyle = "rgba(214,170,100,0.30)"; cx.fillRect(-MW, -MH, MW * 3, MH * 3);
    cx.strokeStyle = "rgba(255,235,200,0.55)"; cx.lineWidth = 1;
    const t = reduzido ? 0 : L.relogio;
    for (let i = 0; i < 40; i++) { const x = (i * 53 + t * 0.35) % (MW + 40) - 20, y = (i * 37) % MH; cx.beginPath(); cx.moveTo(x, y); cx.lineTo(x + 16, y + 3); cx.stroke(); }
  } else if (c.id === "caverna") {
    const fogo = img("fogo.png"); if (!fogo) return;
    for (const e of c.erupcoes) if (e.explodiu) {
      const i = Math.min(5, Math.floor((e.t - 1200) / 100)), fw = fogo.width / 3, fh = fogo.height / 2;
      cx.drawImage(fogo, (i % 3) * fw, Math.floor(i / 3) * fh, fw, fh, e.x - 26, e.y - 58, 52, 62);
    }
  }
}

/* ---------------------------------------------------------------- o quadro */
/** o que o ultimo quadro desenhou (para os testes, as capturas e o e2e: o canvas tambem leva isto em data-*) */
export interface ContagemPoc { [k: string]: number | string }

/** desenha um quadro inteiro da luta; devolve se faltou alguma imagem do mapa (o palco avisa) */
export function desenharLutaPoc(cv: HTMLCanvasElement, c: CenaPocDesenho, a: AtlasOk | null): boolean {
  const ctx = cv.getContext("2d"); if (!ctx) throw new Error("canvas 2d indisponível");
  const { K, W, H } = ajustar(cv), Wp = cv.width, Hp = cv.height, L = c.L, v = c.v;
  const reduzido = movimentoReduzido(), passoL = passoDe(L), passo = passoL + v.extra;
  const g = geometriaPoc(Wp, Hp, K, W, H, v, L, passoL, reduzido), e = g.e, es = g.es;
  const n: ContagemPoc = {};
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, Wp, Hp);
  ctx.fillStyle = COR.fundo; ctx.fillRect(0, 0, Wp, Hp);
  /* o mundo na escala da camera */
  const mundo = () => ctx.setTransform(e, 0, 0, e, Wp / 2 - g.cx * e, Hp * g.oy - g.cy * e);
  mundo();
  const faltou = chao(ctx, L.cena.id);
  /* o nocaute (E5): o cenario escurece; os lutadores e os efeitos vem por cima */
  const koVal = v.koEm.filter((k): k is number => k !== null), koEm = koVal.length ? Math.min(...koVal) : null;
  baixo(ctx, L, reduzido);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const escuro = koEm !== null && L.fim ? escuroDoPasso(passo - koEm) : 0;
  if (escuro > 0) { ctx.fillStyle = `rgba(4,8,20,${escuro.toFixed(3)})`; ctx.fillRect(0, 0, Wp, Hp); }
  n.escuro = escuro.toFixed(2);
  ctx.imageSmoothingEnabled = false;
  const formas = [c.A, c.B], els: ElementoTR[] = formas.map(elementoDoLado);
  const dims: [number, number][] = formas.map(f => (a ? dimSprite(a.dados, f.sprite) : [28, 40]));
  /* o pixel de efeito (E2): VOO.pixel pixels do sprite, entre VOO.pixelMinCss e 1,5 vez isso em px de CSS (o sprite grande no zoom deixava o
     efeito em blocos) */
  const ue = (_i: number) => Math.round(Math.max(VOO.pixelMinCss * K, Math.min(VOO.pixelMinCss * 1.5 * K, es * VOO.pixel)));
  const uChao = es * CHAO.pixel, meiaChao = (i: number) => Math.max(3, Math.round(dims[i][0] * es / 2 / uChao));
  /* as marcas no piso (E3): a cratera da habilidade e o arrasto do empurrao grande, presas ao chao */
  let marcas = 0, ondas = 0;
  for (const m of v.marcas) {
    if (alfaDaMarca(m.m, passo) <= 0) continue;
    marcas++;
    if (m.m.tipo === "cratera") pintar(ctx, pixelsDaCratera(m.m, els[1 - m.m.lado], meiaChao(m.m.lado), passo), xDe(g, m.x), yDe(g, m.y), uChao, 1);
    else {
      const a0 = xDe(g, m.x), b0 = xDe(g, m.x1), comp = Math.round(Math.abs(b0 - a0) / uChao);
      pintar(ctx, pixelsDoArrasto(m.m, comp, passo), a0, yDe(g, m.y), uChao, b0 >= a0 ? 1 : -1);
    }
  }
  for (const m of v.marcas) if (m.m.tipo === "cratera") {
    const px = pixelsDaOnda(els[1 - m.m.lado], passo - m.m.t0, meiaChao(m.m.lado), reduzido);
    if (px.length) { ondas++; pintar(ctx, px, xDe(g, m.x), yDe(g, m.y), uChao, 1); }
  }
  n.marcas = marcas; n.ondas = ondas;
  /* a elipse da preparacao da habilidade (E3): fecha do inicio do ataque ao instante do golpe; pronta, pisca */
  let telegrafias = 0, telegrafiasMeio = 0;
  ([0, 1] as const).forEach(i => {
    const u = lutadorN(L, i), p = preparoDaHabilidade(u); if (!p) return;
    telegrafias++; if (p.f >= .35 && p.f <= .65) telegrafiasMeio++;
    pintar(ctx, pixelsDaTelegrafia({ tipo: "pesado", f: p.f, pronto: p.pronto }, els[i], meiaChao(i), passo, reduzido), xDe(g, u.x), yDe(g, u.y), uChao, 1);
  });
  n.telegrafias = telegrafias; n.telegrafiasMeio = telegrafiasMeio;
  /* a sombra vem no proprio sprite do atlas (nenhuma a mais aqui) */
  /* lutadores e obstaculos na ordem de profundidade (quem esta mais abaixo fica na frente) */
  type Ent = { y: number; i?: LadoN; o?: LutaPoc["cena"]["obst"][number] };
  const ents: Ent[] = ([0, 1] as const).filter(i => !lutadorN(L, i).foraAte).map((i): Ent => ({ y: lutadorN(L, i).y, i }))
    .concat(L.cena.obst.filter(o => !(o.hp !== undefined && o.hp <= 0)).map((o): Ent => ({ y: o.y, o })))
    .sort((p, q) => p.y - q.y);
  const topo: number[] = [yDe(g, L.a.y - 40), yDe(g, L.b.y - 40)];
  let fantasmas = 0, rastros = 0, auras = 0, claroes = 0;
  for (const { i, o } of ents) {
    if (o) {
      const im = img(o.img + ".png"); if (!im) continue;
      const w = im.width / MUNDO_POC.esc, h = im.height / MUNDO_POC.esc;
      mundo(); ctx.save(); ctx.imageSmoothingEnabled = true;
      ctx.beginPath(); ctx.ellipse(o.x, o.y, o.r * 1.2, o.r * 0.5, 0, 0, 7); ctx.fillStyle = "rgba(0,0,0,0.3)"; ctx.fill();
      if (o.hp !== undefined && o.max !== undefined && o.hp < o.max) ctx.globalAlpha = 0.55 + 0.45 * o.hp / o.max;
      ctx.drawImage(im, o.x - w / 2, o.y - h + 4, w, h); ctx.restore();
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingEnabled = false;
      continue;
    }
    if (i === undefined) continue;
    const u = lutadorN(L, i), f = formas[i], X = xDe(g, u.x), [w, h] = dims[i];
    const pulo = reduzido ? 0 : puloDoEmpurrao(v, i, passoL) * e;
    const Yb = yDe(g, u.y + DESENHO_POC.pes) - pulo, x0 = X - w * es / 2, y0 = Yb - h * es;
    topo[i] = y0;
    /* a aura (E4): com a habilidade pronta, faiscas na cor do elemento; na runa do Castelo, o anel roxo da POC */
    if (u.buffAte > L.relogio && !u.morto) {
      ctx.beginPath(); ctx.ellipse(X, yDe(g, u.y), u.raio * 1.3 * e, u.raio * .5 * e, 0, 0, 7);
      ctx.strokeStyle = `rgba(200,160,255,${reduzido ? .8 : 0.5 + 0.4 * Math.sin(L.relogio / 120)})`; ctx.lineWidth = 2 * es; ctx.stroke(); auras++;
    }
    if (!a) { ctx.fillStyle = i ? COR.vermelho : COR.azul; ctx.fillRect(X - 12 * e, Yb - 34 * e, 24 * e, 34 * e); continue; }
    const s = a.dados.sprites[chaveUp(a.dados, f.sprite)], { clipe, t } = clipeDoLutador(u, v.extra * PASSO_POC_MS);
    let iq = 0;
    if (s?.clipes) { const cl = s.clipes[clipe]; if (!cl) throw new Error(`clipe ${clipe} indisponível para ${f.sprite}`); iq = quadroDoClipe(cl.ms, cl.loop, t); }
    else if (s) iq = u.morto ? 0 : Math.floor(t / a.dados.ms_por_quadro) % s.quadros.length;
    const opc = { espelho: u.viraEsq, ...(s?.clipes ? { clipe } : {}) };
    /* a imagem fantasma do desvio (E4: o dash da POC): copias apagadas nas posicoes de antes, na cor do elemento */
    if (u.dash > 0 && !u.morto) {
      fantasmas++;
      const fc = document.createElement("canvas"), m = 2 * es; fc.width = w * es + 2 * m; fc.height = h * es + 2 * m;
      const fx = fc.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
      desenharSprite(fx, a, f.sprite, m, m, es, iq, opc);
      fx.globalCompositeOperation = "source-atop"; fx.globalAlpha = POSTURA.fantasmaTinta; fx.fillStyle = ELEMENTO[els[i]].meio; fx.fillRect(0, 0, fc.width, fc.height);
      POSTURA.fantasmas.forEach((alfa, k) => {
        const p = v.hist[i][(k + 1) * (reduzido ? 2 : 3)]; if (!p) return;
        ctx.globalAlpha = alfa; ctx.drawImage(fc, Math.round(xDe(g, p.x) - w * es / 2) - m, Math.round(yDe(g, p.y + DESENHO_POC.pes) - h * es) - m); ctx.globalAlpha = 1;
      });
    }
    /* o rastro da investida (a v18 e a POC: o golpe corpo a corpo avanca na direcao do alvo): copias mais apagadas no caminho ja feito */
    const g0 = u.usandoHab ? u.sk : u.g, h3 = v.hist[i][MOVIMENTO.rastroPassos];
    if (!reduzido && u.estado === "attack" && !g0.proj && !u.golpeDado && h3 && Math.abs(h3.x - u.x) >= TELA_POC.dashMin * MOVIMENTO.rastroPassos) {
      rastros++;
      MOVIMENTO.rastroAlfa.forEach((alfa, k) => {
        const p = v.hist[i][(k + 1) * MOVIMENTO.rastroPassos]; if (!p) return;
        ctx.globalAlpha = alfa; desenharSprite(ctx, a, f.sprite, xDe(g, p.x) - w * es / 2, yDe(g, p.y + DESENHO_POC.pes) - h * es, es, iq, opc); ctx.globalAlpha = 1;
      });
    }
    const branco = !reduzido && claraoPoc(v, passo, i);
    if (u.escondido) ctx.globalAlpha = .55;
    if (branco) {
      claroes++;
      const fc = document.createElement("canvas"), m = 2 * es; fc.width = w * es + 2 * m; fc.height = h * es + 2 * m;
      const fx = fc.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
      desenharSprite(fx, a, f.sprite, m, m, es, iq, opc);
      fx.globalCompositeOperation = "source-atop"; fx.fillStyle = "#fff"; fx.fillRect(0, 0, fc.width, fc.height);
      ctx.drawImage(fc, Math.round(x0) - m, Math.round(y0) - m);
    } else desenharSprite(ctx, a, f.sprite, x0, y0, es, iq, opc);
    ctx.globalAlpha = 1;
    /* a aura da habilidade pronta (E4, a "carregar" de antes): faiscas que sobem dos lados do corpo */
    if (u.recSk <= 0 && !u.morto && u.estado !== "attack") {
      auras++;
      const kp = Math.max(1, Math.ceil(POSTURA.pixelMinCss * K / es)), up = es * kp;
      pintar(ctx, pixelsDaAura(els[i], Math.round(w * POSTURA.auraMeia / kp), Math.round(h * .8 / kp), passoL, reduzido), X, Yb, up, 1);
    }
  }
  n.fantasmas = fantasmas; n.rastros = rastros; n.auras = auras; n.claroes = claroes;
  /* as moitas da Floresta por cima dos pes (quem esta dentro fica escondido) */
  mundo();
  for (const z of L.cena.zonas) if (z.tipo === "moita") {
    for (let k = 0; k < 9; k++) {
      const an = k / 9 * 6.283, x = z.x + Math.cos(an) * z.rx * 0.7, y = z.y + Math.sin(an) * z.ry * 0.6;
      ctx.beginPath(); ctx.ellipse(x, y - 3, 9, 7, 0, 0, 7); ctx.fillStyle = k % 2 ? "rgba(46,110,58,0.92)" : "rgba(62,138,70,0.92)"; ctx.fill();
    }
    ctx.beginPath(); ctx.ellipse(z.x, z.y - 4, z.rx * 0.75, z.ry * 0.8, 0, 0, 7); ctx.fillStyle = "rgba(54,124,62,0.9)"; ctx.fill();
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingEnabled = false;
  /* a poeira nos pes: na corrida (atras de quem corre) e no empurrao (na frente de quem foi empurrado); na habilidade que acerta, a nuvem */
  let poeiras = 0;
  if (!reduzido) {
    const ps = Math.max(1, Math.round(2 * es / 2));
    ctx.fillStyle = "rgba(214,196,160,.8)";
    ([0, 1] as const).forEach(i => {
      const u = lutadorN(L, i); if (u.foraAte || u.morto) return;
      const X = xDe(g, u.x), Y = yDe(g, u.y), atras = u.viraEsq ? 1 : -1;
      const de = v.correndoDe[i];
      if (de !== null) { poeiras++; for (const p of poeiraDoPasso(passoL - de).slice(0, 2)) ctx.fillRect(Math.round(X + atras * (14 + p.dx * 2) * es / 2), Math.round(Y - (2 + p.dy * 2) * es / 2), ps * p.tam, ps * p.tam); }
      const idade = passoL - v.empurradoEm[i];
      if (idade >= 0 && idade < TELA_POC.durDeslize) { poeiras++; for (const p of poeiraDoPasso(idade)) ctx.fillRect(Math.round(X - atras * (10 + p.dx * 2) * es / 2), Math.round(Y - (2 + p.dy * 2) * es / 2), ps * p.tam, ps * p.tam); }
    });
    for (const m of v.marcas) if (m.m.tipo === "cratera" && passoL - m.m.t0 < CHAO.durPouso) {
      poeiras++;
      for (const p of poeiraDaNuvem(passoL - m.m.t0, true)) ctx.fillRect(Math.round(xDe(g, m.x) + (Math.sign(p.dx) * 10 + p.dx * 2) * es / 2), Math.round(yDe(g, m.y) - (2 + p.dy * 2) * es / 2), ps * p.tam, ps * p.tam);
    }
  }
  n.poeiras = poeiras;
  /* os projeteis em voo (E2 e LP-8): o rastro e o brilho do elemento por baixo e o desenho do jogo por cima; sem o desenho, a cabeca do elemento */
  const ef = efeitosAtuais(), prefabs = ef.tipo === "ok" ? ef.prefabs : null;
  let cabecas = 0, nossos = 0, comDesenho = 0, meio = 0;
  for (const o of v.voos) {
    const dir = o.esq ? -1 : 1, k = reduzido ? VOO.rastroReduzido : VOO.rastro, u = ue(o.de), ult = o.pts.length - 1;
    if (ult < 0) continue;
    const cab = o.pts[ult];
    if (o.tFim === null || passo < o.tFim + VOO.rastroFica) for (let j = k; j >= 1; j--) {
      const pt = o.pts[ult - j]; if (!pt) continue;
      pintar(ctx, pixelsDoRastro(els[o.de], j, k, passo, reduzido), xDe(g, pt.x), yDe(g, pt.y), u, dir);
    }
    if (o.tFim !== null && passo >= o.tFim) continue;
    cabecas++; if (o.nosso) nossos++;
    if (o.pts.length >= 3) meio++;
    const ref = o.prefab && prefabs ? prefabs.get(o.prefab.toLowerCase()) : undefined;
    const X = xDe(g, cab.x), Y = yDe(g, cab.y);
    pintar(ctx, pixelsDaCabeca(els[o.de], passo, reduzido).filter(p => p.luz || !ref), X, Y, u, dir);
    if (ref && desenharEfeito(ctx, ref, (passo - o.t0) * PASSO_POC_MS, X, Y, o.esq, true, DESENHO_POC.efeito * e)) comDesenho++;
  }
  n.projeteis = cabecas; n.nossos = nossos; n.projeteisDesenho = comDesenho; n.projeteisMeio = meio;
  /* o acerto: o efeito do jogo (o prefab do hits), a faisca da E1 e o estouro na cor do elemento de quem bateu (E2) */
  let efeitosJogo = 0;
  for (const x of v.efeitos) {
    const ref = prefabs?.get(x.prefab.toLowerCase()); if (!ref) continue;
    const tt = (passo - x.t0) * PASSO_POC_MS; if (tt < 0 || tt >= ref.dur) continue;
    if (desenharEfeito(ctx, ref, tt, xDe(g, x.x), yDe(g, x.y - dims[x.lado][1] * .45), x.espelho, false, DESENHO_POC.efeito * e)) efeitosJogo++;
  }
  n.efeitosJogo = efeitosJogo;
  let impactos = 0;
  for (const im of v.impactos) {
    const idade = passo - im.t0; if (idade < 0) continue;
    const ps = Math.max(1, Math.round(1.5 * K * e / g.e0)), X = Math.round(xDe(g, im.x) - im.dir * 10 * e), Y = Math.round(yDe(g, im.y - dims[im.lado][1] * .45));
    const fa = faiscaDoPasso({ lado: im.lado, t0: im.t0, frac: im.frac, forte: im.forte }, passo);
    if (fa.length) impactos++;
    for (const p of fa) { ctx.fillStyle = p.cor; ctx.fillRect(X + p.dx * ps * 2, Y + p.dy * ps * 2, ps * (im.forte ? 2 : 1), ps * (im.forte ? 2 : 1)); }
    pintar(ctx, pixelsDoEstouro(els[im.de], idade, im.forte, reduzido), X, Y, ue(im.de), -im.dir);
  }
  n.impactos = impactos;
  /* os numeros que sobem: o dano em fonte de pixel com contorno (o critico e a habilidade, maiores e amarelos); o resto em texto */
  ctx.font = `bold ${Math.round(12 * K)}px system-ui, sans-serif`; ctx.textAlign = "center";
  let numeros = 0;
  for (const nu of v.numeros) {
    const idade = passo - nu.t0, base = Math.min(topo[nu.lado], yDe(g, nu.y - 30)), y = base - (10 + idade * .6) * K;
    ctx.globalAlpha = Math.max(0, 1 - idade / TELA_POC.vidaNumero); numeros++;
    if (nu.pixel) {
      const { px, w: tw, h: th } = pixelsDoTexto(nu.txt), p = Math.max(1, Math.round(K * (nu.forte ? 6 : 4)));
      const x0 = Math.round(xDe(g, nu.x) - tw * p / 2), y0 = Math.round(y - th * p);
      ctx.fillStyle = COR_TINTA;
      for (const [ox, oy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]) for (const [gx, gy] of px) ctx.fillRect(x0 + gx * p + ox * Math.max(1, p >> 1), y0 + gy * p + oy * Math.max(1, p >> 1), p, p);
      ctx.fillStyle = nu.forte ? COR_FORTE : nu.cor; for (const [gx, gy] of px) ctx.fillRect(x0 + gx * p, y0 + gy * p, p, p);
    } else {
      ctx.lineWidth = Math.max(2, Math.round(3 * K)); ctx.strokeStyle = "rgba(10,14,22,.85)"; ctx.strokeText(nu.txt, xDe(g, nu.x), y);
      ctx.fillStyle = nu.cor === COR_TINTA ? "#ffffff" : nu.cor; ctx.fillText(nu.txt, xDe(g, nu.x), y);
    }
  }
  ctx.globalAlpha = 1; n.numeros = numeros;
  /* o que cada arena desenha por cima: a tempestade e o fogo das erupcoes */
  mundo(); cima(ctx, L, reduzido); ctx.setTransform(1, 0, 0, 1, 0, 0);
  /* a tremida do palco (E1): a imagem inteira deslocada em px inteiros; sem ela com o movimento reduzido */
  const tr = reduzido ? { x: 0, y: 0 } : tremidaPoc(v, passo);
  n.tremida = `${tr.x},${tr.y}`;
  cv.dataset.tremidaMax = String(Math.max(Number(cv.dataset.tremidaMax ?? 0), Math.abs(tr.x), Math.abs(tr.y)));
  if (tr.x || tr.y) {
    const fc = document.createElement("canvas"); fc.width = Wp; fc.height = Hp;
    const fx = fc.getContext("2d"); if (!fx) throw new Error("canvas 2d indisponível");
    fx.drawImage(cv, 0, 0); ctx.clearRect(0, 0, Wp, Hp); ctx.fillStyle = COR.fundo; ctx.fillRect(0, 0, Wp, Hp); ctx.drawImage(fc, Math.round(tr.x * K), Math.round(tr.y * K));
  }
  /* o "K.O." (E5): grande no meio do palco, em fonte de pixel com contorno e sombra, depois da tremida (ele nao treme) */
  const ko = koEm !== null && L.fim ? koDoPasso(passo - koEm, Wp, Hp, reduzido) : null;
  n.ko = ko ? String(ko.p) : ""; n.koPronto = ko?.pronto ? "1" : "0";
  if (ko) {
    const { px, w: kw, h: kh } = pixelsDoKO(), p = ko.p, x0 = ko.cx - Math.round(kw * p / 2), y0 = ko.cy - Math.round(kh * p / 2), o = Math.max(1, Math.round(p / 3));
    ctx.fillStyle = "#8a1c2b"; for (const [gx, gy] of px) ctx.fillRect(x0 + gx * p + o, y0 + gy * p + 2 * o, p, p);
    ctx.fillStyle = COR_TINTA;
    for (const [ox, oy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]) for (const [gx, gy] of px) ctx.fillRect(x0 + gx * p + ox * o, y0 + gy * p + oy * o, p, p);
    ctx.fillStyle = COR_FORTE; for (const [gx, gy] of px) ctx.fillRect(x0 + gx * p, y0 + gy * p, p, p);
    ctx.fillStyle = "#fff6c2"; for (const [gx, gy] of px) if (!px.some(([q, r]) => q === gx && r === gy - 1)) ctx.fillRect(x0 + gx * p, y0 + gy * p, p, o);
  }
  n.esc = es; n.zoom = (e / g.e0).toFixed(3); n.cena = L.cena.id; n.passo = passoL;
  for (const [k, x] of Object.entries(n)) cv.dataset[k] = String(x);
  return faltou;
}
