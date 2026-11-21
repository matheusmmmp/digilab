/* Os assets por URL assinada no jogo (CN4, docs/PLANO_V3_CONTA.md seção 6; o servidor em servidor_web/src/protecao/rotas.ts).

   A chave: só com VITE_DIGILAB_API e VITE_DIGILAB_PROTECAO=1 no build (protecaoNoBuild). Desligada (o padrão), `buscarAsset` é o `fetch` de
   sempre e `srcDoAsset` devolve o endereço como veio: o gabarito test/gabaritos/cn4_assets_desligados.json confere, byte a byte.

   Ligada: o caminho de cada asset é o que vem depois de "/Assets/" no endereço de hoje (o atlas, os sons, a cena da evolução); o jogo pede
   ao servidor as URLs (`POST /assets/assinar`, juntando os pedidos do mesmo instante, até CAMINHOS_POR_PEDIDO de cada vez) e guarda cada
   uma até perto de vencer. Sem a sessão da conta, o jogo vira visitante (`POST /assets/visitante`), com o Turnstile se o servidor mandar a
   chave do site. O que não der falha alto: quem carrega o asset mostra o aviso dele, como hoje. */
import { apiDoBuild, protecaoNoBuild } from "../conta/apiDoBuild.ts";
import { tokenTurnstile } from "./turnstile.ts";

/** quantos caminhos vão num pedido (o mesmo teto do servidor, servidor_web/src/protecao/config.ts) */
export const CAMINHOS_POR_PEDIDO = 64;
/** quanto antes de vencer a URL guardada deixa de servir, em ms (PROPOSTO, SEM FONTE): a imagem que começa a baixar no fim não pega uma vencida */
export const MARGEM_MS = 60_000;
/** a espera para juntar os pedidos do mesmo instante (a abertura pede o atlas, os sons e o mapa juntos), em ms (PROPOSTO, SEM FONTE) */
export const JANELA_MS = 10;

export interface AmbienteAssets {
  api: string;
  buscar: (url: string, init?: RequestInit) => Promise<Response>;
  /** o endereço da página, para ler os caminhos relativos */
  base: () => string;
  agora: () => number;
  /** o token do Turnstile para a chave do site e a ação (o widget, na página; o falso nos testes) */
  turnstile: (chaveSite: string, acao: string) => Promise<string>;
}

let amb: AmbienteAssets | null = null;
const guardadas = new Map<string, { url: string; ate: number }>();
let fila = new Map<string, { ok: (u: string) => void; falha: (e: unknown) => void }[]>();
let relogio: ReturnType<typeof setTimeout> | null = null;
let visitante: Promise<void> | null = null;

/** liga com um ambiente (os testes); sem ele, o jogo usa o do build quando a chave está ligada */
export function ligarAssets(a: AmbienteAssets | null): void {
  amb = a === null ? null : { ...a, api: a.api.replace(/\/+$/, "") };
  guardadas.clear(); fila = new Map(); visitante = null;
  if (relogio !== null) { clearTimeout(relogio); relogio = null; }
}
const ambiente = (): AmbienteAssets | null => {
  if (amb) return amb;
  if (!protecaoNoBuild()) return null;
  amb = { api: apiDoBuild().replace(/\/+$/, ""), buscar: (u, i) => fetch(u, i), base: () => document.baseURI, agora: Date.now, turnstile: tokenTurnstile };
  return amb;
};
export const assetsAssinados = (): boolean => ambiente() !== null;

/** o caminho do asset no servidor: o que vem depois de "/Assets" no endereço de hoje ("/sons/mapa.json"); fora de /Assets/, erro */
export function caminhoDoAsset(url: string, base: string): string {
  const p = new URL(url, base).pathname, i = p.indexOf("/Assets/");
  if (i < 0) throw new Error(`asset fora da pasta Assets: ${url}`);
  return p.slice(i + "/Assets".length);
}

async function pedirJson(a: AmbienteAssets, caminho: string, corpo: unknown): Promise<{ status: number; dados: Record<string, unknown> }> {
  const r = await a.buscar(a.api + caminho, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
  const texto = await r.text();
  let dados: unknown = {};
  if (texto) { try { dados = JSON.parse(texto); } catch { throw new Error(`o servidor respondeu ${r.status} sem JSON em ${caminho}`); } }
  if (typeof dados !== "object" || dados === null || Array.isArray(dados)) throw new Error(`resposta estranha em ${caminho}: ${texto.slice(0, 80)}`);
  return { status: r.status, dados: dados as Record<string, unknown> };
}

/** vira visitante (uma vez por vez): com o Turnstile, se o servidor mandou a chave do site */
function virarVisitante(a: AmbienteAssets, chaveSite: unknown): Promise<void> {
  visitante ??= (async () => {
    if (chaveSite !== null && typeof chaveSite !== "string") throw new Error("a chave do Turnstile veio estranha");
    const corpo = chaveSite ? { turnstile: await a.turnstile(chaveSite, "visitante") } : {};
    const r = await pedirJson(a, "/assets/visitante", corpo);
    if (r.status !== 200) throw new Error(`o servidor não aceitou o visitante (${r.status}: ${String(r.dados.motivo ?? r.dados.erro ?? "")})`);
  })();
  visitante.catch(() => { visitante = null; });
  return visitante;
}

async function assinarLote(a: AmbienteAssets, caminhos: string[], tentou = false): Promise<Record<string, string>> {
  const r = await pedirJson(a, "/assets/assinar", { caminhos });
  if (r.status === 401 && !tentou) {
    await virarVisitante(a, r.dados.turnstile ?? null);
    return assinarLote(a, caminhos, true);
  }
  if (r.status !== 200) throw new Error(`as URLs dos assets não vieram (${r.status}: ${String(r.dados.erro ?? "")})`);
  const urls = r.dados.urls as Record<string, unknown> | undefined, validade = Number(r.dados.validade_s);
  if (typeof urls !== "object" || urls === null || !(validade > 0)) throw new Error("a resposta das URLs dos assets veio sem as URLs ou a validade");
  const ate = a.agora() + validade * 1000 - MARGEM_MS, fora: Record<string, string> = {};
  for (const c of caminhos) {
    const u = urls[c];
    if (typeof u !== "string") throw new Error(`o servidor não assinou ${c}`);
    guardadas.set(c, { url: u, ate });
    fora[c] = u;
  }
  return fora;
}

function esvaziar(a: AmbienteAssets): void {
  relogio = null;
  const todos = fila;
  fila = new Map();
  const caminhos = [...todos.keys()];
  for (let i = 0; i < caminhos.length; i += CAMINHOS_POR_PEDIDO) {
    const lote = caminhos.slice(i, i + CAMINHOS_POR_PEDIDO);
    assinarLote(a, lote).then(
      urls => { for (const c of lote) for (const e of todos.get(c)!) e.ok(urls[c]!); },
      err => { for (const c of lote) for (const e of todos.get(c)!) e.falha(err); });
  }
}

/** a URL assinada do asset (a guardada, se ainda serve) */
export function assinarAsset(url: string): Promise<string> {
  const a = ambiente();
  if (!a) throw new Error("as URLs assinadas estão desligadas");
  const c = caminhoDoAsset(url, a.base()), g = guardadas.get(c);
  if (g && g.ate > a.agora()) return Promise.resolve(g.url);
  return new Promise((ok, falha) => {
    const lista = fila.get(c) ?? [];
    lista.push({ ok, falha });
    fila.set(c, lista);
    relogio ??= setTimeout(() => esvaziar(a), JANELA_MS);
  });
}

/** o fetch de um asset: desligada a chave, o fetch de sempre (com os mesmos argumentos); ligada, o da URL assinada */
export function buscarAsset(url: string, init?: RequestInit): Promise<Response> {
  if (!assetsAssinados()) return init === undefined ? fetch(url) : fetch(url, init);
  return assinarAsset(url).then(u => (init === undefined ? fetch(u) : fetch(u, init)));
}

/** o endereço de uma imagem: desligada, o mesmo; ligada, o assinado (e a imagem pede o CORS, porque o atlas vai para o canvas) */
export async function srcDoAsset(url: string): Promise<{ src: string; crossOrigin: "anonymous" | null }> {
  if (!assetsAssinados()) return { src: url, crossOrigin: null };
  return { src: await assinarAsset(url), crossOrigin: "anonymous" };
}
