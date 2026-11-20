/* Os efeitos do jogo na luta da POC (LUTA_POC, LP3): os prefabs dos golpes, dos projeteis e dos acertos do Digimon UP (Bandai; com o credito,
   autorizados pelo Matheus: docs/UI_GUIDELINES.md, secao 5.1), recortados por Assets/gerar_arena_up.py em D:\Trab\digilab\Assets\arena_up
   (fora do repositorio): dados/efeitos.json (a grade e o tempo de cada camada) e efeitos/<Digimon>.png (a folha). O caminho relativo e o do
   atlas: a pagina em /v1/web/dist/ pede ../../../Assets/arena_up/; no dev, o vite.config.ts serve so estes arquivos.
   Se nao carregar: o palco desenha so o efeito do elemento (E2) e mostra o aviso (falhar alto, nunca calado). */

export const ARENA_UP_URL = "../../../Assets/arena_up/";

/** uma camada de um efeito: o retangulo na folha, a grade (tx x ty quadros), quantos quadros, o tempo de cada um e se repete */
export interface CamadaEfeito { camada: string; r: [number, number, number, number]; tx: number; ty: number; n: number; ms: number; loop: boolean }
export interface Efeito { nome: string; c: CamadaEfeito[] }
export type EfeitosArena = Record<string, { w: number; h: number; e: Efeito[] }>;
/** um efeito achado pelo nome do prefab: a folha (o dono) e as camadas */
export interface EfeitoRef { dono: string; e: Efeito; dur: number }

export type EstadoEfeitos = { tipo: "carregando" } | { tipo: "ok"; prefabs: Map<string, EfeitoRef> } | { tipo: "erro"; erro: string };
let estado: EstadoEfeitos = { tipo: "carregando" };
let pedido: Promise<void> | null = null;
const ouvintes = new Set<() => void>();
const avisar = () => { for (const o of ouvintes) o(); };
export function ouvirEfeitos(f: () => void): () => void { ouvintes.add(f); return () => { ouvintes.delete(f); }; }
export const efeitosAtuais = (): EstadoEfeitos => estado;

/** o indice dos prefabs pelo nome (sem caixa) */
export function indexarEfeitos(ef: EfeitosArena): Map<string, EfeitoRef> {
  const m = new Map<string, EfeitoRef>();
  for (const [dono, d] of Object.entries(ef)) for (const e of d.e) {
    if (!e.c.length) throw new Error(`efeito ${e.nome} sem camada (efeitos.json)`);
    m.set(e.nome.toLowerCase(), { dono, e, dur: Math.max(...e.c.map(c => c.n * c.ms)) });
  }
  return m;
}

/** pede o efeitos.json uma vez (as folhas vem sob demanda, em folhaEfeito) */
export function carregarEfeitos(): Promise<void> {
  return pedido ??= fetch(`${ARENA_UP_URL}dados/efeitos.json`, { cache: "no-cache" })
    .then(r => { if (!r.ok) throw new Error(`dados/efeitos.json: HTTP ${r.status}`); return r.json() as Promise<EfeitosArena>; })
    .then(j => { estado = { tipo: "ok", prefabs: indexarEfeitos(j) }; avisar(); },
      (err: unknown) => { estado = { tipo: "erro", erro: err instanceof Error ? err.message : String(err) }; avisar(); });
}

/** as folhas: uma imagem por Digimon (null: nao carregou; a falha fica para o aviso) */
const folhas = new Map<string, HTMLImageElement | null>();
export const falhasEfeito = new Set<string>();
export function folhaEfeito(dono: string): HTMLImageElement | null {
  if (folhas.has(dono)) return folhas.get(dono)!;
  folhas.set(dono, null);
  const i = new Image();
  i.onload = () => { folhas.set(dono, i); avisar(); };
  i.onerror = () => { falhasEfeito.add(`efeitos/${dono}.png`); avisar(); };
  i.src = `${ARENA_UP_URL}efeitos/${encodeURIComponent(dono)}.png`;
  return null;
}
