/* Arena em tempo real (docs/TAREFA_V2_UP_ARENA.md): a chave e os dados do jogo. Os dados e a arte do Digimon UP (Bandai; com o credito,
   autorizados pelo Matheus: docs/UI_GUIDELINES.md, secao 5.1) ficam FORA do repositorio, em D:\Trab\digilab\Assets\arena_up, gerados por
   Assets\gerar_arena_up.py. Mesmo caminho relativo do atlas: a pagina em /v1/web/dist/ pede ../../../Assets/arena_up/. Se nao carregar:
   aviso visivel. A arena nao toca no motor do pet, no log nem no save. */
import { conferirDados, type DadosArena, type Recuos } from "../arena/index.ts";

/** Chave da arena em tempo real (D1, Matheus, 2026-10-29), DESLIGADA: desligada, o jogo e o de hoje (nenhuma rota, botao ou pedido novo).
    ?arena_tr=1 liga so naquela aba (conferir e e2e), como o ?clipes_up=1 */
export const ARENA_TEMPO_REAL = false;
export const arenaTrLigada = (): boolean => ARENA_TEMPO_REAL || new URLSearchParams(location.search).get("arena_tr") === "1";

export const ARENA_UP_URL = "../../../Assets/arena_up/";
export const ENDERECO_ARENA_TR = "#/lutar/tempo-real";
export const ehArenaTr = (hash: string): boolean => hash.replace(/^#\/?/, "") === "lutar/tempo-real";

/** as particulas dos golpes (dados/efeitos.json): grade e tempo por camada; so a tela usa */
export interface CamadaEfeito { camada: string; r: [number, number, number, number]; tx: number; ty: number; n: number; ms: number; loop: boolean }
export interface Efeito { nome: string; c: CamadaEfeito[] }
export type EfeitosArena = Record<string, { w: number; h: number; e: Efeito[] }>;

export interface PacoteArena { dados: DadosArena; efeitos: EfeitosArena; recuos: Recuos }
export type EstadoArenaTr = { tipo: "carregando" } | { tipo: "ok"; pacote: PacoteArena } | { tipo: "erro"; erro: string };

async function json(nome: string): Promise<unknown> {
  const r = await fetch(`${ARENA_UP_URL}dados/${nome}.json`, { cache: "no-cache" });
  if (!r.ok) throw new Error(`dados/${nome}.json: HTTP ${r.status}`);
  return r.json();
}

/** os cinco JSON; a conferencia levanta erro se faltar campo, Digimon ou atributo */
export async function carregarArenaTr(): Promise<PacoteArena> {
  const [status, golpes, atributos, atlas, efeitos] = await Promise.all(["status", "golpes", "atributos", "atlas", "efeitos"].map(json));
  const dados = { status, golpes, atributos, atlas } as DadosArena;
  return { dados, efeitos: efeitos as EfeitosArena, recuos: conferirDados(dados) };
}

/** imagens da arena (sprites, folhas de efeito, mapas): uma promessa por arquivo; a falha fica guardada para o aviso */
const imagens = new Map<string, Promise<HTMLImageElement | null>>();
export const falhasImagem = new Set<string>();
export function imagemArena(rel: string): Promise<HTMLImageElement | null> {
  let p = imagens.get(rel);
  if (!p) {
    p = new Promise(ok => {
      const i = new Image();
      i.onload = () => ok(i);
      i.onerror = () => { falhasImagem.add(rel); ok(null); };
      i.src = ARENA_UP_URL + rel.split("/").map(encodeURIComponent).join("/");
    });
    imagens.set(rel, p);
  }
  return p;
}
