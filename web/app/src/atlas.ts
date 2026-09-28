/* Atlas do Digimon UP (Bandai; so uso pessoal e local). Fica FORA do repositorio, em D:\Trab\digilab\Assets,
   gerado por Assets\gerar_atlas_up.py. Mesmo caminho relativo do HTML: a pagina em /v1/web/dist/ pede
   ../../../Assets/ (no modo dev, o vite.config serve so estes dois arquivos). Se nao carregar: aviso visivel. */
import { useEffect, useState } from "preact/hooks";

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

export function carregarAtlas(url = ATLAS_URL): void {
  fetch(url)
    .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} em ${url}`); return r.json() as Promise<AtlasUp>; })
    .then(dados => {
      const png = new URL(dados.atlas, new URL(url, document.baseURI)).href, img = new Image();
      img.onload = () => avisar({ tipo: "ok", dados, img });
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
/** desenha um quadro do idle em escala inteira de pixel do aparelho, sem suavizar */
export function desenharSprite(ctx: CanvasRenderingContext2D, e: Extract<EstadoAtlas, { tipo: "ok" }>, nome: string, x: number, y: number, escala: number, iQuadro: number): void {
  if (!Number.isInteger(escala) || escala < 1) throw new Error("escala de sprite so inteira: " + escala);
  const k = chaveUp(e.dados, nome), s = e.dados.sprites[k];
  ctx.imageSmoothingEnabled = false;
  if (!s) { const r = e.dados.pecas[k]; ctx.drawImage(e.img, r[0], r[1], r[2], r[3], x, y, r[2] * escala, r[3] * escala); return; }
  const q = s.quadros[iQuadro % s.quadros.length];
  ctx.drawImage(e.img, q[0], q[1], q[2], q[3], x + q[4] * escala, y + q[5] * escala, q[2] * escala, q[3] * escala);
}
