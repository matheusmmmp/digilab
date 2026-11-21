/* O Worker na frente do bucket PRIVADO dos assets (CN5, D-CONTA-199 revista em 2026-11-21: os assets só saem pela URL assinada da CN4;
   docs/PLANO_V3_CONTA_BORDA.md, seção 6, "se o W1 não estiver no plano"). Fica na rota assets.<domínio>/*, lê o R2 pelo binding ASSETS
   (o bucket não tem domínio público nem o r2.dev) e só entrega o arquivo cuja URL o servidor assinou:

     GET|HEAD /<caminho>?verify=<hora>-<mac>     a mesma conta do `verificar` de servidor_web/src/protecao/assinatura.ts, em WebCrypto
                                                 (o test/worker_assets.test.ts confere com URLs feitas pelo `urlAssinada` do servidor)
     OPTIONS                                     o CORS, só da origem do jogo

   A chave do objeto é o caminho sem a "/" do começo (a mesma do web/app/scripts/publicar_assets.ts). O cache da borda guarda o arquivo pelo
   caminho, sem o `verify`, depois de conferir a assinatura: o R2 é lido uma vez por arquivo, não uma vez por jogador.
   As variáveis (wrangler.toml e `wrangler secret put`): DIGILAB_SEGREDO_ASSETS (o mesmo do servidor), DIGILAB_ORIGEM_JOGO (https://<domínio>),
   DIGILAB_VALIDADE_ASSETS_S (o mesmo do servidor; padrão 600). NÃO CONFERIDO na Cloudflare de verdade. */

/** o pedaço do binding do R2 que o Worker usa */
export interface ObjetoR2 { body: ReadableStream | null; httpEtag: string; size: number; httpMetadata?: { contentType?: string } }
export interface BucketR2 { get(chave: string): Promise<ObjetoR2 | null> }
export interface CacheBorda { match(r: Request): Promise<Response | undefined>; put(r: Request, resp: Response): Promise<void> }
export interface Ambiente {
  ASSETS: BucketR2;
  DIGILAB_SEGREDO_ASSETS: string;
  DIGILAB_ORIGEM_JOGO: string;
  DIGILAB_VALIDADE_ASSETS_S?: string;
}
export interface Contexto { waitUntil(p: Promise<unknown>): void }

/* as mesmas regras do servidor (assinatura.ts e config.ts); o teste confere que não se separaram */
export const PARAMETRO = "verify";
export const FOLGA_RELOGIO_S = 60;
export const VALIDADE_PADRAO_S = 600;
/** PROPOSTO, SEM FONTE (o da seção 6 do plano da borda): o navegador e a borda guardam o arquivo um dia */
export const CACHE_ARQUIVO = "public, max-age=86400";
export const TAMANHO_MINIMO_SEGREDO = 32;

export function caminhoValido(caminho: string): boolean {
  return /^\/[A-Za-z0-9._/-]{1,200}$/.test(caminho) && !caminho.includes("..") && !caminho.includes("//");
}

async function macDe(segredo: string, caminho: string, horaS: number): Promise<string> {
  const chave = await crypto.subtle.importKey("raw", new TextEncoder().encode(segredo), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = new Uint8Array(await crypto.subtle.sign("HMAC", chave, new TextEncoder().encode(caminho + String(horaS))));
  let bin = "";
  for (const b of mac) bin += String.fromCharCode(b);
  return btoa(bin);
}

/** o mesmo veredito do `verificar` do servidor */
export async function verificarWeb(segredo: string, caminho: string, verify: string | null, agoraS: number, validadeS: number): Promise<string> {
  if (verify === null || verify === "") return "sem_assinatura";
  const m = /^(\d{1,12})-([A-Za-z0-9+/]{43}=)$/.exec(verify);
  if (!m) return "malformada";
  const hora = Number(m[1]);
  const esperado = await macDe(segredo, caminho, hora), dado = m[2]!;
  let dif = esperado.length ^ dado.length;
  for (let i = 0; i < Math.min(esperado.length, dado.length); i++) dif |= esperado.charCodeAt(i) ^ dado.charCodeAt(i);
  if (dif !== 0) return "nao_confere";
  if (hora > agoraS + FOLGA_RELOGIO_S) return "do_futuro";
  if (agoraS - hora > validadeS) return "vencida";
  return "ok";
}

const cors = (env: Ambiente): Record<string, string> => ({ "Access-Control-Allow-Origin": env.DIGILAB_ORIGEM_JOGO, Vary: "Origin" });
const erro = (env: Ambiente, status: number, motivo: string): Response =>
  new Response(JSON.stringify({ erro: motivo }), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...cors(env) } });

/** o Worker; `agora` e `cache` só para os testes (na Cloudflare: Date.now e caches.default) */
export async function atender(req: Request, env: Ambiente, ctx: Contexto, agora: () => number = Date.now,
  cache: CacheBorda | null = (globalThis as { caches?: { default: CacheBorda } }).caches?.default ?? null): Promise<Response> {
  if (!env.DIGILAB_SEGREDO_ASSETS || env.DIGILAB_SEGREDO_ASSETS.length < TAMANHO_MINIMO_SEGREDO) return erro(env, 503, "sem o segredo dos assets");
  if (!/^https:\/\/[^/]+$/.test(env.DIGILAB_ORIGEM_JOGO ?? "")) return erro(env, 503, "sem a origem do jogo");
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: { ...cors(env), "Access-Control-Allow-Methods": "GET, HEAD", "Access-Control-Max-Age": "3600" } });
  }
  if (req.method !== "GET" && req.method !== "HEAD") return erro(env, 405, "só GET e HEAD");
  const url = new URL(req.url), caminho = url.pathname;
  if (!caminhoValido(caminho)) return erro(env, 404, "caminho inválido");
  const validade = Number(env.DIGILAB_VALIDADE_ASSETS_S ?? VALIDADE_PADRAO_S);
  if (!Number.isInteger(validade) || validade <= 0) return erro(env, 503, "DIGILAB_VALIDADE_ASSETS_S inválida");
  const v = await verificarWeb(env.DIGILAB_SEGREDO_ASSETS, caminho, url.searchParams.get(PARAMETRO), Math.floor(agora() / 1000), validade);
  if (v !== "ok") return erro(env, 403, v);

  const chaveCache = new Request(url.origin + caminho);
  const guardada = cache ? await cache.match(chaveCache) : undefined;
  const responder = (r: Response): Response => {
    const h = new Headers(r.headers);
    for (const [k, x] of Object.entries(cors(env))) h.set(k, x);
    return new Response(req.method === "HEAD" ? null : r.body, { status: r.status, headers: h });
  };
  if (guardada) return responder(guardada);

  const obj = await env.ASSETS.get(caminho.slice(1));
  if (obj === null) return erro(env, 404, "não existe");
  const resp = new Response(obj.body, { status: 200, headers: {
    "Content-Type": obj.httpMetadata?.contentType ?? "application/octet-stream",
    "Content-Length": String(obj.size),
    ETag: obj.httpEtag,
    "Cache-Control": CACHE_ARQUIVO,
    "X-Robots-Tag": "noindex",
  } });
  if (cache) {
    ctx.waitUntil(cache.put(chaveCache, resp.clone()));
  }
  return responder(resp);
}

export default { fetch: (req: Request, env: Ambiente, ctx: Contexto): Promise<Response> => atender(req, env, ctx) };
