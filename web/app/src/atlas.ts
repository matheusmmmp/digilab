/* Atlas do Digimon UP (Bandai; com o credito, autorizado pelo Matheus para este projeto: docs/UI_GUIDELINES.md, secao 5.1). Fica FORA do
   repositorio, em D:\Trab\digilab\Assets, gerado por Assets\gerar_atlas_up.py. Mesmo caminho relativo do HTML: a pagina em /v1/web/dist/ pede
   ../../../Assets/ (no modo dev, o vite.config serve so estes dois arquivos). Se nao carregar: aviso visivel. */
import { useEffect, useState } from "react";
import { zoomAtual } from "./escala.ts";

export const ATLAS_URL = "../../../Assets/digilab_atlas_up.json";
/** Chave dos clipes oficiais do UP (TAREFA_V2_UP_ATLAS), LIGADA desde 2026-10-30 (decisao H-4 do Matheus, docs/TAREFA_V3_HABITAT_ILHA_3D.md,
    H1b): o app carrega tambem o atlas de clipes (Assets\gerar_atlas_up_clipes.py), o Idle de cada sprite toca com a duracao real de cada quadro e
    as vistas que andam usam o Run. Sem o atlas de clipes, o aviso de atlas que nao carregou (nunca cai calado no atlas atual). Desligada, o app
    carrega so o atlas acima e desenha como antes. E do app, nao do motor: o log, o replay e a paridade nao mudam. */
export const CLIPES_UP = true;
export const ATLAS_CLIPES_URL = "../../../Assets/digilab_atlas_up_clipes.json";

/** [x, y, largura, altura, deslocamento x, deslocamento y] de cada quadro dentro da caixa do sprite */
export type Quadro = [number, number, number, number, number, number];
export type Clipe = "Idle" | "Run" | "Attack_1" | "Stun" | "Die" | "Evol";
/** um clipe: quadros, a duracao de cada um em ms e se repete; quadro vazio = [0,0,0,0,0,0] */
export interface ClipeUp { quadros: Quadro[]; ms: number[]; loop: boolean }
/** `clipes` so existe com a chave CLIPES_UP ligada; entao `quadros` e o Idle e a imagem e a do atlas de clipes */
export interface SpriteUp { caixa: [number, number]; quadros: Quadro[]; clipes?: Partial<Record<Clipe, ClipeUp>> }
export interface SpriteClipes { digimon: string; caixa: [number, number]; clipes: Partial<Record<Clipe, ClipeUp>> }
export interface AtlasClipes { atlas: string; sprites: Record<string, SpriteClipes> }
export interface AtlasUp {
  atlas: string;
  ms_por_quadro: number;
  sprites: Record<string, SpriteUp>;
  pecas: Record<string, [number, number, number, number]>;
}
export type EstadoAtlas =
  | { tipo: "carregando" }
  | { tipo: "ok"; dados: AtlasUp; img: HTMLImageElement; imgClipes?: HTMLImageElement }
  | { tipo: "erro"; erro: string };

let estado: EstadoAtlas = { tipo: "carregando" };
const ouvintes = new Set<() => void>();
const avisar = (e: EstadoAtlas): void => { estado = e; for (const o of ouvintes) o(); };

/* fundos do UP como variaveis de CSS (docs/estilo_up/dl-up.css): o hexagono (linhas brancas; no tema escuro, na cor
   --dl-hex do escuro) e o anel de plataforma. Sem atlas, fica o hexagono desenhado de reserva do tokens.css. */
function pecaComoUrl(dados: AtlasUp, img: HTMLImageElement, nome: string, cor?: string): string {
  const r = dados.pecas[nome];
  if (!r) throw new Error("peça do atlas ausente: " + nome);
  const c = document.createElement("canvas"); c.width = r[2]; c.height = r[3];
  const g = c.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
  g.drawImage(img, r[0], r[1], r[2], r[3], 0, 0, r[2], r[3]);
  if (cor) { g.globalCompositeOperation = "source-in"; g.fillStyle = cor; g.fillRect(0, 0, r[2], r[3]); }
  return `url(${c.toDataURL()})`;
}
function aplicarFundos(dados: AtlasUp, img: HTMLImageElement): void {
  const st = document.documentElement.style;
  st.setProperty("--dl-img-hex-claro", pecaComoUrl(dados, img, "fundo_hex"));
  st.setProperty("--dl-img-hex-escuro", pecaComoUrl(dados, img, "fundo_hex", "#1F3A78"));
  st.setProperty("--dl-img-anel", pecaComoUrl(dados, img, "anel_plataforma"));
  document.documentElement.dataset.fundos = "up";
}
const carregarImagem = (png: string, rotulo: string): Promise<HTMLImageElement> => new Promise((ok, falha) => {
  const img = new Image();
  img.onload = () => ok(img);
  img.onerror = () => falha(new Error(`imagem do ${rotulo} não carregou: ${png}`));
  img.src = png;
});
/** junta os clipes ao atlas atual: cada sprite do atlas de clipes troca o do atlas atual (caixa e Idle como `quadros`); o resto (ovos, pecas,
    oraculo, guia) fica. Falha alto: sprite sem Idle ou clipe com `ms` que nao casa com os quadros. */
export function juntarClipes(base: AtlasUp, c: AtlasClipes): AtlasUp {
  const sprites = { ...base.sprites };
  for (const [k, s] of Object.entries(c.sprites)) {
    const idle = s.clipes.Idle;
    if (!idle) throw new Error("atlas de clipes: sprite sem Idle: " + k);
    for (const [nome, cl] of Object.entries(s.clipes))
      if (!cl || cl.quadros.length === 0 || cl.quadros.length !== cl.ms.length || cl.ms.some(m => !(m > 0)))
        throw new Error(`atlas de clipes: clipe ${nome} de ${k} sem quadros ou com duracao invalida`);
    sprites[k] = { caixa: s.caixa, quadros: idle.quadros, clipes: s.clipes };
  }
  return { ...base, sprites };
}
export function carregarAtlas(url = ATLAS_URL, clipes = CLIPES_UP, urlClipes = ATLAS_CLIPES_URL): void {
  const abs = (u: string): string => new URL(u, document.baseURI).href;
  fetch(url)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} em ${url}`); return r.json() as Promise<AtlasUp>; })
    .then(async dados => {
      const png = new URL(dados.atlas, abs(url)).href;
      const img = await carregarImagem(png, "atlas");
      aplicarFundos(dados, img);
      if (!clipes) { avisar({ tipo: "ok", dados, img }); return; }
      /* chave ligada: sem o atlas de clipes, aviso visivel; nunca cai calado no atlas atual */
      const r = await fetch(urlClipes);
      if (!r.ok) throw new Error(`atlas de clipes: HTTP ${r.status} em ${urlClipes}`);
      const c = await r.json() as AtlasClipes;
      const imgClipes = await carregarImagem(new URL(c.atlas, abs(urlClipes)).href, "atlas de clipes");
      avisar({ tipo: "ok", dados: juntarClipes(dados, c), img, imgClipes });
    })
    .catch((err: unknown) => {
      console.error("falha ao carregar o atlas", url, err);
      avisar({ tipo: "erro", erro: err instanceof Error ? err.message : String(err) });
    });
}
export function useAtlas(): EstadoAtlas {
  const [, set] = useState(0);
  useEffect(() => { const o = () => set(x => x + 1); ouvintes.add(o); return () => { ouvintes.delete(o); }; }, []);
  return estado;
}

/** chave do UP: o nome antigo traz o quadro no fim (_0.._3); o UP so tem o ciclo idle. Falha alto se nao existe. */
export function chaveUp(a: AtlasUp, nome: string): string {
  if (a.sprites[nome] || a.pecas[nome]) return nome;
  const b = nome.replace(/_\d$/, "");
  if (a.sprites[b]) return b;
  throw new Error("sprite desconhecido: " + nome);
}
/** tamanho em pixels nativos: a caixa comum do idle (sprite) ou o recorte (peca) */
export function dimSprite(a: AtlasUp, nome: string): [number, number] {
  const k = chaveUp(a, nome), s = a.sprites[k];
  return s ? [s.caixa[0], s.caixa[1]] : [a.pecas[k][2], a.pecas[k][3]];
}
export type AtlasOk = Extract<EstadoAtlas, { tipo: "ok" }>;
const movimentoReduzido = (): boolean => matchMedia("(prefers-reduced-motion: reduce)").matches;
/** quadro de um clipe no instante t (ms desde o inicio): pela soma das duracoes; repete se `loop`, senao segura o ultimo */
export function quadroDoClipe(ms: number[], loop: boolean, t: number): number {
  const total = ms.reduce((a, b) => a + b, 0);
  if (!loop && t >= total) return ms.length - 1;
  let r = t % total;
  for (let i = 0; i < ms.length; i++) { if (r < ms[i]) return i; r -= ms[i]; }
  return ms.length - 1;
}
/** quadro do clipe agora (padrao Idle, 120 ms por quadro sem a chave; com ela, a duracao de cada quadro); `t0` = performance.now() do inicio de
    um clipe que nao repete; parado ou com movimento reduzido, o primeiro */
export function quadroAgora(a: AtlasOk, nome: string, parado = false, clipe: Clipe = "Idle", t0 = 0): number {
  const s = a.dados.sprites[chaveUp(a.dados, nome)];
  if (!s) return 0;
  const c = s.clipes?.[clipe];
  if (!c && (clipe !== "Idle" || s.clipes)) throw new Error(`clipe ${clipe} indisponível para ${nome}`);
  if (parado || movimentoReduzido()) return 0;
  return c ? quadroDoClipe(c.ms, c.loop, performance.now() - t0) : Math.floor(performance.now() / a.dados.ms_por_quadro) % s.quadros.length;
}

/* forma sombria: o mesmo quadro com veu roxo (#7B3FB8) e contorno de 1 px (proposta aprovada na Etapa 0); a cena da evolucao
   (src/evolucaoUp.ts) usa o mesmo veu */
const cacheSombrio = new Map<string, HTMLCanvasElement>();
export function quadroSombrio(img: HTMLImageElement, q: Quadro): HTMLCanvasElement {
  const ch = q.join(",") + (img.src);
  const c0 = cacheSombrio.get(ch);
  if (c0) return c0;
  const [sx, sy, w, h] = q;
  const novo = (cw: number, chh: number): [HTMLCanvasElement, CanvasRenderingContext2D] => {
    const c = document.createElement("canvas"); c.width = cw; c.height = chh;
    const g = c.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível"); return [c, g];
  };
  const [base, b] = novo(w, h), [sil, si] = novo(w, h), [c, g] = novo(w + 2, h + 2);
  b.drawImage(img, sx, sy, w, h, 0, 0, w, h);
  b.globalCompositeOperation = "source-atop"; b.fillStyle = "rgba(123,63,184,.5)"; b.fillRect(0, 0, w, h);
  si.drawImage(img, sx, sy, w, h, 0, 0, w, h);
  si.globalCompositeOperation = "source-in"; si.fillStyle = "#7B3FB8"; si.fillRect(0, 0, w, h);
  for (const [dx, dy] of [[0, 1], [2, 1], [1, 0], [1, 2]]) g.drawImage(sil, dx, dy);
  g.drawImage(base, 1, 1);
  cacheSombrio.set(ch, c);
  return c;
}

/** desenha um quadro do idle (ou uma peca) em escala inteira de pixel do aparelho, sem suavizar */
export function desenharSprite(ctx: CanvasRenderingContext2D, e: AtlasOk, nome: string, x: number, y: number, escala: number, iQuadro: number,
  opc: { sombria?: boolean; espelho?: boolean; clipe?: Clipe } = {}): void {
  if (!Number.isInteger(escala) || escala < 1) throw new Error("escala de sprite so inteira: " + escala);
  const k = chaveUp(e.dados, nome), s = e.dados.sprites[k];
  /* no pixel do canvas (ignora a escala do contexto), como o spriteUp do HTML */
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingEnabled = false;
  x = Math.round(x); y = Math.round(y);
  if (!s) { const r = e.dados.pecas[k]; ctx.drawImage(e.img, r[0], r[1], r[2], r[3], x, y, r[2] * escala, r[3] * escala); ctx.restore(); return; }
  /* com a chave ligada o sprite vem do atlas de clipes (outra imagem) */
  const clipe = opc.clipe ?? "Idle", c = s.clipes?.[clipe];
  if (opc.clipe && opc.clipe !== "Idle" && !c) throw new Error(`clipe ${clipe} indisponível para ${nome}`);
  const img = s.clipes ? e.imgClipes : e.img, lista = c ? c.quadros : s.quadros;
  if (!img) throw new Error("atlas de clipes sem imagem: " + nome);
  const q = lista[iQuadro % lista.length];
  if (q[2] === 0) { ctx.restore(); return; }
  /* espelho (so na luta, o rival): em volta da caixa comum do idle */
  if (opc.espelho) { ctx.translate(x + s.caixa[0] * escala, y); ctx.scale(-1, 1); x = 0; y = 0; }
  if (opc.sombria) ctx.drawImage(quadroSombrio(img, q), 0, 0, q[2] + 2, q[3] + 2, x + (q[4] - 1) * escala, y + (q[5] - 1) * escala, (q[2] + 2) * escala, (q[3] + 2) * escala);
  else ctx.drawImage(img, q[0], q[1], q[2], q[3], x + q[4] * escala, y + q[5] * escala, q[2] * escala, q[3] * escala);
  ctx.restore();
}
/** silhueta preta (primeiro quadro) para o que o motor ainda nao decidiu */
const cacheSilhueta = new Map<string, { url: string; w: number; h: number }>();
export function silhuetaAtlas(a: AtlasOk, nome: string): { url: string; w: number; h: number } {
  const pronta = cacheSilhueta.get(nome);
  if (pronta) return pronta;
  const [w, h] = dimSprite(a.dados, nome), c = document.createElement("canvas"); c.width = w; c.height = h;
  const g = c.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
  desenharSprite(g, a, nome, 0, 0, 1, 0);
  g.globalCompositeOperation = "source-in"; g.fillStyle = "#000000"; g.fillRect(0, 0, w, h);
  const r = { url: c.toDataURL(), w, h };
  cacheSilhueta.set(nome, r);
  return r;
}
/** estado do atlas fora de componente (o palco desenha num intervalo proprio) */
export const atlasAtual = (): EstadoAtlas => estado;
/** escala do sprite em pixels do aparelho: 1x em pixels CSS quando o aparelho tem densidade inteira */
/** pixels do aparelho por pixel de CSS, inteiro (com o zoom do desktop, src/escala.ts) */
export const escalaSprite = (): number => Math.max(1, Math.floor((devicePixelRatio || 1) * zoomAtual()));

/** imagem (data URL) de um sprite ou peca em escala inteira, primeiro quadro; cache por nome e escala */
const cacheImagem = new Map<string, string>();
export function imagemAtlas(a: AtlasOk, nome: string, escala = 1, opc: { sombria?: boolean } = {}): { url: string; w: number; h: number } {
  const [w, h] = dimSprite(a.dados, nome), ch = `${nome}@${escala}@${opc.sombria ? 1 : 0}`;
  if (!cacheImagem.has(ch)) {
    const c = document.createElement("canvas"); c.width = w * escala; c.height = h * escala;
    const g = c.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível");
    desenharSprite(g, a, nome, 0, 0, escala, 0, opc);
    cacheImagem.set(ch, c.toDataURL());
  }
  return { url: cacheImagem.get(ch)!, w: w * escala, h: h * escala };
}
