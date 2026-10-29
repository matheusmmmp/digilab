/* Desenho da arena em tempo real no canvas (porte do bloco "desenho" do arena.html). So apresentacao: le a Luta da simulacao
   (arena/), nunca a altera; os numeros, as particulas e os aneis de troca saem dos eventos e vivem aqui. */
import { CENAS, ELIPSE, ENTRADA, MUNDO, PASSO_MS, ativo, tagDe, vivos, type Evento, type IdCena, type Luta, type Lutador } from "../../../../arena/index.ts";
import type { Efeito, EfeitosArena } from "../../../arenaTempoReal.ts";

const { w: W, h: H, esc: ESC } = MUNDO;
const { cx: CX, cy: CY, rx: RX, ry: RY } = ELIPSE;
/** cores do canvas (as do prototipo) */
const COR = { ceu: "#cfe6f5", chaoA: "#9fcf7a", chaoB: "#8cc068", borda: "#5d8a44", tinta: "#1d2433", apagado: "#6b7280", bom: "#2f9e44", destaque: "#e8a317", azul: "#2c73e0", vermelho: "#d6336c" };

/** a arte de cada arena (os recortes dos mapas do jogo em Assets/arena_up/mapas) */
export const VISUAL_CENA: Record<IdCena, { piso?: string; fundo?: string; fundoCobre?: boolean; fundoAlt?: number; ceu?: [string, string] }> = {
  campo: {},
  coliseu: { piso: "coliseu_piso.jpg", fundo: "coliseu_fundo.jpg", fundoCobre: true },
  floresta: { piso: "floresta_piso.jpg", fundo: "floresta_fundo.png", fundoAlt: 92 },
  praia: { piso: "praia_piso.jpg", ceu: ["#9fd3ef", "#d9f0f7"] },
  deserto: { piso: "deserto_piso.jpg", ceu: ["#f3c27a", "#fbe3b6"] },
  castelo: { piso: "castelo_piso.jpg", fundo: "castelo_fundo.png", fundoAlt: 96, ceu: ["#2a2346", "#4b3b6e"] },
  caverna: { piso: "caverna_piso.jpg", ceu: ["#0d1016", "#1d2430"] },
  ringue: { piso: "ringue_piso.jpg", fundo: "ringue_fundo.jpg", fundoCobre: true },
};
/** os arquivos de mapa que uma arena usa */
export function arquivosCena(id: IdCena): string[] {
  const v = VISUAL_CENA[id];
  return [v.piso, v.fundo, ...(CENAS[id].obst || []).map(o => o[3] + ".png"), id === "caverna" ? "fogo.png" : undefined].filter((x): x is string => !!x);
}

interface EfeitoRef { dono: string; e: Efeito }
export interface Visual {
  numeros: { x: number; y: number; txt: string; cor: string; t: number }[];
  efeitos: { ref: EfeitoRef; x: number; y: number; t: number; fim: number; espelho: boolean }[];
  trocas: { x: number; y: number; t: number; l: "a" | "b" }[];
}
export const visualNovo = (): Visual => ({ numeros: [], efeitos: [], trocas: [] });

/** as imagens ja carregadas (null = nao carregou: a tela desenha um marcador e mostra o aviso) */
export interface Imagens { sprites: Map<string, HTMLImageElement | null>; folhas: Map<string, HTMLImageElement | null>; mapas: Map<string, HTMLImageElement | null> }

export function indexarEfeitos(ef: EfeitosArena): Map<string, EfeitoRef> {
  const m = new Map<string, EfeitoRef>();
  for (const [dono, d] of Object.entries(ef)) for (const e of d.e) m.set(e.nome.toLowerCase(), { dono, e });
  return m;
}
const durEf = (e: Efeito) => Math.max(...e.c.map(c => c.n * c.ms));

/** os eventos de um passo viram numeros, particulas e aneis; depois tudo envelhece PASSO_MS */
export function aplicarEventosVisuais(v: Visual, L: Luta, ev: readonly Evento[], prefabs: Map<string, EfeitoRef>): void {
  const altura = (n: string) => L.dados.atlas.d[n].h;
  for (const e of ev) {
    if (e.tipo === "dano") {
      const ef = e.mult > 1 ? " eficaz!" : e.mult < 1 ? " fraco" : "";
      v.numeros.push({ x: e.x + e.dx, y: e.y - altura(e.alvo.n) * 0.8, txt: (e.crit ? "crítico " : "") + e.valor + ef, cor: e.mult > 1 ? COR.bom : e.mult < 1 ? COR.apagado : e.crit ? COR.destaque : COR.tinta, t: 0 });
      const hits = e.hits.length ? e.hits : [{ prefab: "Fx_Battle_Hit_A_Normal", atraso: 0 }];
      for (const h of hits) { const ref = prefabs.get(h.prefab.toLowerCase()); if (ref) v.efeitos.push({ ref, x: e.x, y: e.y - altura(e.alvo.n) * 0.45, t: -h.atraso * 1000, fim: durEf(ref.e), espelho: e.espelho }); }
    } else if (e.tipo === "esquiva") v.numeros.push({ x: e.x, y: e.y - altura(e.alvo.n) * 0.8, txt: "esquivou", cor: COR.apagado, t: 0 });
    else if (e.tipo === "habilidade") v.numeros.push({ x: e.x, y: e.y - altura(e.u.n) - 4, txt: e.propria ? "habilidade!" : "golpe forte!", cor: e.u.lado === "a" ? COR.azul : COR.vermelho, t: 0 });
    else if (e.tipo === "runa") v.numeros.push({ x: e.x, y: e.y - altura(e.u.n) - 4, txt: "poder da runa!", cor: "#c9a6ff", t: 0 });
    else if (e.tipo === "ambiente" && e.mostrar) v.numeros.push({ x: e.mostrar.x, y: e.mostrar.y - altura(e.u.n) * 0.8, txt: `−${e.mostrar.valor} ${e.motivo}`, cor: "#ff8a4c", t: 0 });
    else if (e.tipo === "troca") v.trocas.push({ x: e.x, y: e.y, t: 0, l: e.lado });
  }
  for (const x of v.efeitos) x.t += PASSO_MS;
  v.efeitos = v.efeitos.filter(x => x.t < x.fim);
  for (const x of v.trocas) x.t += PASSO_MS;
  v.trocas = v.trocas.filter(x => x.t < 400);
  for (const x of v.numeros) x.t += PASSO_MS;
  v.numeros = v.numeros.filter(x => x.t < 900);
}

function desenharEf(ctx: CanvasRenderingContext2D, im: HTMLImageElement | null | undefined, ref: EfeitoRef, t: number, x: number, y: number, espelho: boolean, loop: boolean) {
  if (!im || t < 0) return;
  for (const c of ref.e.c) {
    let i = Math.floor(t / c.ms);
    if (c.loop || loop) i %= c.n; else if (i >= c.n) continue;
    const w = c.r[2] / c.tx, h = c.r[3] / c.ty, sx = c.r[0] + (i % c.tx) * w, sy = c.r[1] + Math.floor(i / c.tx) * h;
    ctx.save(); ctx.translate(Math.round(x), Math.round(y)); if (espelho) ctx.scale(-1, 1);
    ctx.drawImage(im, sx, sy, w, h, -Math.round(w / 2), -Math.round(h / 2), w, h); ctx.restore();
  }
}

function quadroAtual(u: Lutador): [number, number, number] {
  const nomes = { idle: "Idle", run: "Run", attack: u.usandoHab ? u.sk.anim : u.g.anim, stun: "Stun", die: "Die" };
  const tg = tagDe(u.A, nomes[u.estado]);
  const fs = u.A.f.slice(tg[1], tg[2] + 1), total = fs.reduce((s, f) => s + f[2], 0) || 1;
  const loop = u.estado === "idle" || u.estado === "run";
  const t = loop ? u.t % total : Math.min(u.t, total - 1);
  let acc = 0;
  for (const f of fs) { if (t < acc + f[2]) return f; acc += f[2]; }
  return fs[fs.length - 1];
}

function chao(ctx: CanvasRenderingContext2D, id: IdCena, im: Imagens) {
  const c = VISUAL_CENA[id], piso = c.piso ? im.mapas.get(c.piso) : null;
  if (piso) {
    ctx.imageSmoothingEnabled = true;
    if (c.ceu) { const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, c.ceu[0]); g.addColorStop(1, c.ceu[1]); ctx.fillStyle = g; }
    else ctx.fillStyle = COR.ceu;
    ctx.fillRect(0, 0, W, H);
    const f = c.fundo ? im.mapas.get(c.fundo) : null;
    if (f && c.fundoCobre) { const s = Math.max(W / f.width, H / f.height); ctx.drawImage(f, (W - f.width * s) / 2, 0, f.width * s, f.height * s); }
    else if (f && c.fundoAlt) { const alt = c.fundoAlt, larg = f.width * alt / f.height; for (let x = 0; x < W; x += larg) ctx.drawImage(f, x, 6, larg, alt); }
    ctx.beginPath(); ctx.ellipse(CX, CY + 6, RX + 8, RY + 10, 0, 0, 7); ctx.fillStyle = "rgba(0,0,0,0.45)"; ctx.fill();
    ctx.save(); ctx.beginPath(); ctx.ellipse(CX, CY, RX, RY, 0, 0, 7); ctx.clip();
    ctx.drawImage(piso, CX - RX, CY - RY, RX * 2, RY * 2);
    ctx.restore();
    ctx.beginPath(); ctx.ellipse(CX, CY, RX, RY, 0, 0, 7);
    const semCerca = !!CENAS[id].semCerca;
    ctx.strokeStyle = semCerca ? "rgba(255,255,255,0.9)" : "rgba(0,0,0,0.5)"; ctx.lineWidth = semCerca ? 2 : 1.5; ctx.stroke();
    ctx.imageSmoothingEnabled = false;
    return;
  }
  /* campo de treino (ou mapa que nao carregou): o losango xadrez */
  ctx.fillStyle = COR.ceu; ctx.fillRect(0, 0, W, H);
  ctx.save();
  ctx.beginPath(); ctx.ellipse(CX, CY + 10, RX + 14, RY + 14, 0, 0, Math.PI * 2); ctx.fillStyle = COR.borda; ctx.fill();
  ctx.beginPath(); ctx.ellipse(CX, CY, RX, RY, 0, 0, Math.PI * 2); ctx.clip();
  const tw = 32, th = 16;
  for (let j = -2; j < 16; j++) for (let i = -2; i < 18; i++) {
    const x = (i - j) * tw / 2 + CX, y = (i + j) * th / 2 + CY - 140;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + tw / 2, y + th / 2); ctx.lineTo(x, y + th); ctx.lineTo(x - tw / 2, y + th / 2); ctx.closePath();
    ctx.fillStyle = (i + j) % 2 ? COR.chaoA : COR.chaoB; ctx.fill();
  }
  ctx.restore();
  ctx.beginPath(); ctx.ellipse(CX, CY, RX, RY, 0, 0, Math.PI * 2); ctx.strokeStyle = COR.borda; ctx.lineWidth = 2; ctx.stroke();
}

/** o que cada arena desenha embaixo dos lutadores */
function baixo(ctx: CanvasRenderingContext2D, L: Luta) {
  const c = L.cena, t = L.relogio;
  if (c.id === "coliseu" && c.seguro < 1) {
    ctx.save(); ctx.beginPath(); ctx.ellipse(CX, CY, RX, RY, 0, 0, 7); ctx.ellipse(CX, CY, RX * c.seguro, RY * c.seguro, 0, 0, 7, true);
    ctx.fillStyle = "rgba(200,40,30,0.28)"; ctx.fill("evenodd");
    ctx.beginPath(); ctx.ellipse(CX, CY, RX * c.seguro, RY * c.seguro, 0, 0, 7); ctx.strokeStyle = "rgba(255,120,90,0.9)"; ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore();
  } else if (c.id === "praia" && c.linha < CY + RY) {
    ctx.save(); ctx.beginPath(); ctx.ellipse(CX, CY, RX, RY, 0, 0, 7); ctx.clip();
    ctx.fillStyle = "rgba(40,140,200,0.42)"; ctx.fillRect(0, c.linha, W, H);
    ctx.strokeStyle = "rgba(235,250,255,0.85)"; ctx.lineWidth = 1.5; ctx.beginPath();
    for (let x = 0; x <= W; x += 6) ctx.lineTo(x, c.linha + Math.sin(x / 14 + t / 300) * 1.6);
    ctx.stroke(); ctx.restore();
  } else if (c.id === "deserto") {
    const z = c.zonas[0];
    ctx.save(); ctx.beginPath(); ctx.ellipse(z.x, z.y, z.rx, z.ry, 0, 0, 7);
    const g = ctx.createRadialGradient(z.x, z.y, 2, z.x, z.y, z.rx);
    g.addColorStop(0, "rgba(120,80,40,0.75)"); g.addColorStop(1, "rgba(170,120,60,0.15)"); ctx.fillStyle = g; ctx.fill();
    ctx.strokeStyle = "rgba(110,72,36,0.55)"; ctx.lineWidth = 1;
    for (let k = 1; k <= 3; k++) {
      ctx.beginPath();
      for (let a = 0; a < 6.3; a += 0.3) { const r = k / 3 * (1 - a / 14), ang = a + t / 900; ctx.lineTo(z.x + Math.cos(ang + k * 2) * z.rx * r, z.y + Math.sin(ang + k * 2) * z.ry * r); }
      ctx.stroke();
    }
    ctx.restore();
  } else if (c.id === "castelo") {
    const z = c.zonas[0], pronta = c.runaCd <= 0, pulso = 0.5 + 0.5 * Math.sin(t / 250);
    ctx.save(); ctx.beginPath(); ctx.ellipse(z.x, z.y, z.rx, z.ry, 0, 0, 7);
    ctx.fillStyle = pronta ? `rgba(170,120,255,${0.25 + 0.25 * pulso})` : "rgba(90,80,120,0.25)"; ctx.fill();
    ctx.strokeStyle = pronta ? "#d7c2ff" : "rgba(160,150,190,0.6)"; ctx.lineWidth = 1.2; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(z.x, z.y, z.rx * 0.55, z.ry * 0.55, 0, 0, 7); ctx.stroke();
    for (let i = 0; i < 6; i++) { const a = i / 6 * 6.283 + t / 1500; ctx.beginPath(); ctx.moveTo(z.x, z.y); ctx.lineTo(z.x + Math.cos(a) * z.rx, z.y + Math.sin(a) * z.ry); ctx.stroke(); }
    ctx.restore();
  } else if (c.id === "caverna") {
    for (const z of c.zonas) {
      const g = ctx.createRadialGradient(z.x, z.y, 1, z.x, z.y, z.rx);
      g.addColorStop(0, "rgba(255,210,90,0.95)"); g.addColorStop(0.5, "rgba(255,90,20,0.85)"); g.addColorStop(1, "rgba(120,20,10,0)");
      ctx.save(); ctx.beginPath(); ctx.ellipse(z.x, z.y, z.rx, z.ry, 0, 0, 7); ctx.fillStyle = g; ctx.fill(); ctx.restore();
    }
    for (const e of c.erupcoes) if (!e.explodiu) {
      const p = e.t / 1200;
      ctx.beginPath(); ctx.ellipse(e.x, e.y, 28, 17, 0, 0, 7); ctx.strokeStyle = `rgba(255,140,40,${0.4 + 0.5 * p})`; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.beginPath(); ctx.ellipse(e.x, e.y, 28 * p, 17 * p, 0, 0, 7); ctx.fillStyle = "rgba(255,110,30,0.35)"; ctx.fill();
    }
  }
}

/** o que cada arena desenha por cima */
function cima(ctx: CanvasRenderingContext2D, L: Luta, im: Imagens) {
  const c = L.cena;
  if (c.id === "deserto" && c.tempestade) {
    ctx.fillStyle = "rgba(214,170,100,0.30)"; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(255,235,200,0.55)"; ctx.lineWidth = 1;
    for (let i = 0; i < 40; i++) { const x = (i * 53 + L.relogio * 0.35) % (W + 40) - 20, y = (i * 37) % H; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 16, y + 3); ctx.stroke(); }
  } else if (c.id === "caverna") {
    const fogo = im.mapas.get("fogo.png"); if (!fogo) return;
    for (const e of c.erupcoes) if (e.explodiu) {
      const i = Math.min(5, Math.floor((e.t - 1200) / 100)), fw = fogo.width / 3, fh = fogo.height / 2;
      ctx.drawImage(fogo, (i % 3) * fw, Math.floor(i / 3) * fh, fw, fh, e.x - 26, e.y - 58, 52, 62);
    }
  }
}

function barra(ctx: CanvasRenderingContext2D, L: Luta, u: Lutador, x: number, y: number, w: number) {
  ctx.fillStyle = "rgba(0,0,0,0.45)"; ctx.fillRect(x, y, w, 7);
  const p = u.hp / u.st.hp;
  ctx.fillStyle = p > 0.5 ? COR.bom : p > 0.2 ? COR.destaque : COR.vermelho;
  ctx.fillRect(x + 1, y + 1, Math.max(0, (w - 2) * p), 5);
  ctx.fillStyle = COR.tinta; ctx.font = "8px 'IBM Plex Mono', monospace";
  ctx.textAlign = u.lado === "a" ? "left" : "right";
  ctx.fillText(`${u.n}  ${u.hp}/${u.st.hp}  ·  ${vivos(L, u.lado).length}/3 de pé`, u.lado === "a" ? x : x + w, y + 17);
  const pr = Math.max(0, Math.min(1, 1 - u.recSk / (u.st.hcd * 1000))), pronta = u.recSk <= 0;
  ctx.fillStyle = "rgba(0,0,0,0.35)"; ctx.fillRect(x, y + 21, w * 0.6, 4);
  ctx.fillStyle = u.lado === "a" ? COR.azul : COR.vermelho; ctx.fillRect(x + (u.lado === "a" ? 0 : w * 0.4), y + 21, w * 0.6 * pr, 4);
  ctx.fillStyle = COR.apagado; ctx.font = "7px 'IBM Plex Mono', monospace";
  ctx.fillText(pronta ? (u.lado === "a" && L.cfg.jogador ? "habilidade pronta [Q]" : "habilidade pronta") : `habilidade em ${(u.recSk / 1000).toFixed(1)} s`,
    u.lado === "a" ? x + w * 0.62 : x + w * 0.38, y + 26);
}

/** um quadro inteiro */
export function desenhar(ctx: CanvasRenderingContext2D, L: Luta, v: Visual, im: Imagens, prefabs: Map<string, EfeitoRef>): void {
  ctx.setTransform(ESC, 0, 0, ESC, 0, 0);
  ctx.imageSmoothingEnabled = false;
  chao(ctx, L.cena.id, im);
  for (const e of v.trocas) {
    ctx.globalAlpha = 1 - e.t / 400; ctx.strokeStyle = e.l === "a" ? COR.azul : COR.vermelho; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.ellipse(e.x, e.y - 2, 10 + e.t / 12, 4 + e.t / 30, 0, 0, Math.PI * 2); ctx.stroke(); ctx.globalAlpha = 1;
  }
  baixo(ctx, L);
  // lutadores e obstaculos na ordem de profundidade (quem esta mais abaixo fica na frente)
  type Ent = { y: number; u?: Lutador; o?: Luta["cena"]["obst"][number] };
  const ents: Ent[] = [ativo(L, "a"), ativo(L, "b")].filter(u => !u.foraAte).map((u): Ent => ({ y: u.y, u }))
    .concat(L.cena.obst.filter(o => !(o.hp !== undefined && o.hp <= 0)).map((o): Ent => ({ y: o.y, o })))
    .sort((p, q) => p.y - q.y);
  for (const { u, o } of ents) {
    if (o) {
      const img = im.mapas.get(o.img + ".png"); if (!img) continue;
      const w = img.width / ESC, h = img.height / ESC;
      ctx.save(); ctx.imageSmoothingEnabled = true;
      ctx.beginPath(); ctx.ellipse(o.x, o.y, o.r * 1.2, o.r * 0.5, 0, 0, 7); ctx.fillStyle = "rgba(0,0,0,0.3)"; ctx.fill();
      if (o.hp !== undefined && o.max !== undefined && o.hp < o.max) ctx.globalAlpha = 0.55 + 0.45 * o.hp / o.max;
      ctx.drawImage(img, o.x - w / 2, o.y - h + 4, w, h); ctx.restore();
      continue;
    }
    if (!u) continue;
    if (u.buffAte > L.relogio) {
      ctx.beginPath(); ctx.ellipse(u.x, u.y - 2, u.raio * 1.3, u.raio * 0.5, 0, 0, 7);
      ctx.strokeStyle = `rgba(200,160,255,${0.5 + 0.4 * Math.sin(L.relogio / 120)})`; ctx.lineWidth = 2; ctx.stroke();
    }
    ctx.save(); ctx.translate(Math.round(u.x), Math.round(u.y));
    if (u.viraEsq) ctx.scale(-1, 1);
    if ((u.estado === "stun" && Math.floor(u.t / 60) % 2) || u.entrada > 0) ctx.globalAlpha = u.entrada > 0 ? 0.35 + 0.65 * (1 - u.entrada / ENTRADA) : 0.6;
    if (u.escondido) ctx.globalAlpha = 0.55;
    const sp = im.sprites.get(u.n);
    if (sp) { const f = quadroAtual(u); ctx.drawImage(sp, f[0], f[1], u.A.w, u.A.h, -Math.round(u.A.w / 2), -Math.round(u.A.h - 9), u.A.w, u.A.h); }
    else {   /* sprite que nao carregou: um marcador na cor do lado (o aviso esta na tela) */
      ctx.fillStyle = u.lado === "a" ? COR.azul : COR.vermelho; ctx.beginPath(); ctx.ellipse(0, -14, 12, 14, 0, 0, 7); ctx.fill();
    }
    ctx.restore();
  }
  // moitas por cima dos pes
  for (const z of L.cena.zonas) if (z.tipo === "moita") {
    for (let i = 0; i < 9; i++) {
      const a = i / 9 * 6.283, x = z.x + Math.cos(a) * z.rx * 0.7, y = z.y + Math.sin(a) * z.ry * 0.6;
      ctx.beginPath(); ctx.ellipse(x, y - 3, 9, 7, 0, 0, 7); ctx.fillStyle = i % 2 ? "rgba(46,110,58,0.92)" : "rgba(62,138,70,0.92)"; ctx.fill();
    }
    ctx.beginPath(); ctx.ellipse(z.x, z.y - 4, z.rx * 0.75, z.ry * 0.8, 0, 0, 7); ctx.fillStyle = "rgba(54,124,62,0.9)"; ctx.fill();
  }
  for (const p of L.projeteis) {
    const pf = p.dados.proj?.prefab, ref = pf ? prefabs.get(pf.toLowerCase()) : undefined;
    if (ref) desenharEf(ctx, im.folhas.get(ref.dono), ref, p.t, p.x, p.y, p.esq, true);
    else { ctx.fillStyle = p.de.lado === "a" ? COR.azul : COR.vermelho; ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, 7); ctx.fill(); }
  }
  for (const e of v.efeitos) desenharEf(ctx, im.folhas.get(e.ref.dono), e.ref, e.t, e.x, e.y, e.espelho, false);
  cima(ctx, L, im);
  ctx.textAlign = "center"; ctx.font = "bold 9px 'IBM Plex Mono', monospace";
  for (const n of v.numeros) { ctx.globalAlpha = 1 - n.t / 900; ctx.fillStyle = n.cor; ctx.fillText(n.txt, n.x, n.y - n.t / 25); ctx.globalAlpha = 1; }
  barra(ctx, L, ativo(L, "a"), 10, 10, 170); barra(ctx, L, ativo(L, "b"), W - 180, 10, 170);
  if (L.fim) {
    ctx.fillStyle = "rgba(0,0,0,0.5)"; ctx.fillRect(0, H / 2 - 22, W, 36);
    ctx.fillStyle = "#fff"; ctx.textAlign = "center"; ctx.font = "14px Silkscreen, monospace";
    ctx.fillText(L.vencedor ? `Equipe ${L.vencedor === "a" ? "azul" : "vermelha"} venceu` : "Empate", W / 2, H / 2 + 2);
  }
}

