/* Atlas do Digimon UP (Bandai; so uso pessoal e local). Fica FORA do repositorio, em D:\Trab\digilab\Assets,
   gerado por Assets\gerar_atlas_up.py. Mesmo caminho relativo do HTML: a pagina em /v1/web/dist/ pede
   ../../../Assets/ (no modo dev, o vite.config serve so estes dois arquivos). Se nao carregar: aviso visivel. */
import { useEffect, useState } from "react";
import { zoomAtual } from "./escala.ts";

export const ATLAS_URL = "../../../Assets/digilab_atlas_up.json";

/** [x, y, largura, altura, deslocamento x, deslocamento y] de cada quadro dentro da caixa do sprite */
export type Quadro = [number, number, number, number, number, number];
export interface SpriteUp { caixa: [number, number]; quadros: Quadro[] }
export interface AtlasUp {
  atlas: string;
  ms_por_quadro: number;
  sprites: Record<string, SpriteUp>;
  pecas: Record<string, [number, number, number, number]>;
}
export type EstadoAtlas =
  | { tipo: "carregando" }
  | { tipo: "ok"; dados: AtlasUp; img: HTMLImageElement }
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
export function carregarAtlas(url = ATLAS_URL): void {
  fetch(url)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} em ${url}`); return r.json() as Promise<AtlasUp>; })
    .then(dados => {
      const png = new URL(dados.atlas, new URL(url, document.baseURI)).href, img = new Image();
      img.onload = () => { aplicarFundos(dados, img); avisar({ tipo: "ok", dados, img }); };
      img.onerror = () => avisar({ tipo: "erro", erro: "imagem do atlas não carregou: " + png });
      img.src = png;
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
/** quadro do idle agora (120 ms por quadro); parado ou com movimento reduzido, o primeiro */
export function quadroAgora(a: AtlasOk, nome: string, parado = false): number {
  const s = a.dados.sprites[chaveUp(a.dados, nome)];
  return !s || parado || movimentoReduzido() ? 0 : Math.floor(performance.now() / a.dados.ms_por_quadro) % s.quadros.length;
}

/* forma sombria: o mesmo quadro com veu roxo (#7B3FB8) e contorno de 1 px (proposta aprovada na Etapa 0) */
const cacheSombrio = new Map<string, HTMLCanvasElement>();
function quadroSombrio(a: AtlasOk, q: Quadro): HTMLCanvasElement {
  const ch = q.join(",");
  const c0 = cacheSombrio.get(ch);
  if (c0) return c0;
  const [sx, sy, w, h] = q;
  const novo = (cw: number, chh: number): [HTMLCanvasElement, CanvasRenderingContext2D] => {
    const c = document.createElement("canvas"); c.width = cw; c.height = chh;
    const g = c.getContext("2d"); if (!g) throw new Error("canvas 2d indisponível"); return [c, g];
  };
  const [base, b] = novo(w, h), [sil, si] = novo(w, h), [c, g] = novo(w + 2, h + 2);
  b.drawImage(a.img, sx, sy, w, h, 0, 0, w, h);
  b.globalCompositeOperation = "source-atop"; b.fillStyle = "rgba(123,63,184,.5)"; b.fillRect(0, 0, w, h);
  si.drawImage(a.img, sx, sy, w, h, 0, 0, w, h);
  si.globalCompositeOperation = "source-in"; si.fillStyle = "#7B3FB8"; si.fillRect(0, 0, w, h);
  for (const [dx, dy] of [[0, 1], [2, 1], [1, 0], [1, 2]]) g.drawImage(sil, dx, dy);
  g.drawImage(base, 1, 1);
  cacheSombrio.set(ch, c);
  return c;
}

/** desenha um quadro do idle (ou uma peca) em escala inteira de pixel do aparelho, sem suavizar */
export function desenharSprite(ctx: CanvasRenderingContext2D, e: AtlasOk, nome: string, x: number, y: number, escala: number, iQuadro: number,
  opc: { sombria?: boolean; espelho?: boolean } = {}): void {
  if (!Number.isInteger(escala) || escala < 1) throw new Error("escala de sprite so inteira: " + escala);
  const k = chaveUp(e.dados, nome), s = e.dados.sprites[k];
  /* no pixel do canvas (ignora a escala do contexto), como o spriteUp do HTML */
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingEnabled = false;
  x = Math.round(x); y = Math.round(y);
  if (!s) { const r = e.dados.pecas[k]; ctx.drawImage(e.img, r[0], r[1], r[2], r[3], x, y, r[2] * escala, r[3] * escala); ctx.restore(); return; }
  const q = s.quadros[iQuadro % s.quadros.length];
  /* espelho (so na luta, o rival): em volta da caixa comum do idle */
  if (opc.espelho) { ctx.translate(x + s.caixa[0] * escala, y); ctx.scale(-1, 1); x = 0; y = 0; }
  if (opc.sombria) ctx.drawImage(quadroSombrio(e, q), 0, 0, q[2] + 2, q[3] + 2, x + (q[4] - 1) * escala, y + (q[5] - 1) * escala, (q[2] + 2) * escala, (q[3] + 2) * escala);
  else ctx.drawImage(e.img, q[0], q[1], q[2], q[3], x + q[4] * escala, y + q[5] * escala, q[2] * escala, q[3] * escala);
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
