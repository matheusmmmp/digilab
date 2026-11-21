/* As rotas da proteção (CN4, docs/PLANO_V3_CONTA.md seção 6):
     GET  /robots.txt          a da API: ninguém indexa nada (a do jogo é o web/app/public/robots.txt)
     GET  /.well-known/tdmrep.json   o aviso de mineração reservada (PI-6, tdmrep.ts; o do jogo é o web/app/public/.well-known/)
     GET  /assets/estado       {ligado, motivo, validade_s, turnstile: <chave do site> | null}: o que o jogo precisa para pedir as URLs
     POST /assets/visitante    {turnstile}: o visitante sem conta passa pelo Turnstile e leva o cookie dl_visitante (DURACAO_VISITANTE_MS)
     POST /assets/assinar      {caminhos: ["/atlas/x.png", ...]} -> {urls: {caminho: url}, validade_s, expira_em}: com a sessão da conta
                               ou o cookie do visitante; até CAMINHOS_POR_PEDIDO por pedido e ASSINATURAS_POR_HORA por hora
     GET  /assets/*            só no local: serve a pasta DIGILAB_DIR_ASSETS depois de conferir a assinatura (403 sem ela). Fora do
                               local, quem confere é a borda (docs/PLANO_V3_CONTA_BORDA.md)
   As URLs não carregam a sessão (a borda não lê o cookie): o que as liga à conta é só quem as pediu e a vida curta (D-CONTA-213). */
import { createHmac, randomUUID, timingSafeEqual } from "node:crypto";
import { readFile } from "node:fs/promises";
import { extname, resolve, sep } from "node:path";
import type { Context, Hono } from "hono";
import { getCookie, setCookie } from "hono/cookie";
import type { ConfigConta } from "../conta/config.ts";
import type { GuardasConta } from "../conta/rotas.ts";
import { caminhoValido, PARAMETRO, urlAssinada, verificar } from "./assinatura.ts";
import { ASSINATURAS_POR_HORA, CAMINHOS_POR_PEDIDO, DURACAO_VISITANTE_MS } from "./config.ts";
import { robotsDaApi } from "./robots.ts";
import { CAMINHO_TDMREP, tdmrepJson } from "./tdmrep.ts";

export const COOKIE_VISITANTE = "dl_visitante";
const LIMITE_CORPO_ASSETS = 16 * 1024;
const HORA_MS = 3600_000;

const TIPOS: Record<string, string> = {
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".json": "application/json",
  ".bin": "application/octet-stream", ".glb": "model/gltf-binary", ".gltf": "model/gltf+json", ".ogg": "audio/ogg",
  ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4", ".txt": "text/plain; charset=utf-8",
};

/** só as rotas do robots.txt e do tdmrep.json (valem também sem a conta) */
export function montarRobots(app: Hono): void {
  app.get("/robots.txt", c => c.text(robotsDaApi(), 200, { "Cache-Control": "public, max-age=86400" }));
  app.get(CAMINHO_TDMREP, c => c.body(tdmrepJson(), 200, { "Content-Type": "application/json", "Cache-Control": "public, max-age=86400" }));
}

const macVisitante = (segredo: string, expira: number, id: string): string =>
  createHmac("sha256", segredo).update(`visitante|${expira}|${id}`).digest("base64url");

export function montarRotasProtecao(app: Hono, cfg: ConfigConta, guardas: GuardasConta): void {
  const p = cfg.protecao, { agora } = cfg;
  const origemApi = new URL(cfg.urlApi).origin;
  const json = (c: Context, codigo: number, dados: unknown) => c.json(dados, codigo as 200, { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" });
  app.use("/assets/*", guardas.cors);

  const origemValida = (c: Context): boolean => {
    const o = c.req.header("origin");
    return o === undefined || o === cfg.origemJogo || o === origemApi;
  };
  const lerCorpo = async (c: Context): Promise<Record<string, unknown> | Response> => {
    const texto = await c.req.text();
    if (Buffer.byteLength(texto, "utf8") > LIMITE_CORPO_ASSETS) return json(c, 413, { erro: "corpo grande demais" });
    if (texto === "") return {};
    if (!(c.req.header("content-type") ?? "").startsWith("application/json")) return json(c, 415, { erro: "o corpo é JSON" });
    try {
      const d = JSON.parse(texto) as unknown;
      if (typeof d === "object" && d !== null && !Array.isArray(d)) return d as Record<string, unknown>;
    } catch { /* cai no 400 */ }
    return json(c, 400, { erro: "o corpo precisa ser um objeto JSON" });
  };

  /** o visitante do cookie, se o cookie confere e não venceu */
  const visitanteDe = (c: Context): string | null => {
    const v = getCookie(c, COOKIE_VISITANTE);
    if (!v || p.segredoAssets === null) return null;
    const m = /^(\d{1,15})\.([0-9a-f-]{36})\.([A-Za-z0-9_-]{43})$/.exec(v);
    if (!m) return null;
    const expira = Number(m[1]), esperado = Buffer.from(macVisitante(p.segredoAssets, expira, m[2]!)), dado = Buffer.from(m[3]!);
    if (esperado.length !== dado.length || !timingSafeEqual(esperado, dado) || expira <= agora()) return null;
    return m[2]!;
  };

  /* o limite por hora, por conta ou visitante (na memória: reiniciar zera, e está tudo bem; é contra a raspagem em lote) */
  const janelas = new Map<string, { inicio: number; n: number }>();
  const cabeNaHora = (quem: string, n: number): boolean => {
    const t = agora();
    for (const [k, j] of janelas) if (t - j.inicio >= HORA_MS) janelas.delete(k);
    const j = janelas.get(quem) ?? { inicio: t, n: 0 };
    if (j.n + n > ASSINATURAS_POR_HORA) return false;
    j.n += n;
    janelas.set(quem, j);
    return true;
  };

  app.get("/assets/estado", c => json(c, 200, { ligado: p.segredoAssets !== null, motivo: p.motivoAssets, validade_s: p.validadeAssetsS,
    turnstile: p.turnstile?.chaveSite ?? null }));

  app.post("/assets/visitante", async c => {
    if (p.segredoAssets === null) return json(c, 503, { erro: "as URLs assinadas estão desligadas", motivo: p.motivoAssets });
    if (!origemValida(c)) return json(c, 403, { erro: "origem desconhecida" });
    const d = await lerCorpo(c);
    if (d instanceof Response) return d;
    if (p.turnstile !== null) {
      const r = await p.turnstile.conferir(d.turnstile, "visitante");
      if (!r.ok) return json(c, r.motivo === "indisponivel" ? 503 : 403, { erro: "o Turnstile não passou", motivo: r.motivo, codigos: r.codigos });
    }
    const expira = agora() + DURACAO_VISITANTE_MS, id = randomUUID();
    setCookie(c, COOKIE_VISITANTE, `${expira}.${id}.${macVisitante(p.segredoAssets, expira, id)}`,
      { httpOnly: true, secure: cfg.cookieSeguro, sameSite: "Lax", path: "/assets", maxAge: Math.floor(DURACAO_VISITANTE_MS / 1000) });
    return json(c, 200, { visitante: true, expira_em: new Date(expira).toISOString() });
  });

  app.post("/assets/assinar", async c => {
    if (p.segredoAssets === null) return json(c, 503, { erro: "as URLs assinadas estão desligadas", motivo: p.motivoAssets });
    if (!origemValida(c)) return json(c, 403, { erro: "origem desconhecida" });
    const s = guardas.sessaoDe(c);
    const visitante = s ? null : visitanteDe(c);
    if (!s && visitante === null)
      return json(c, 401, { erro: "sem sessão e sem visitante", turnstile: p.turnstile?.chaveSite ?? null });
    const d = await lerCorpo(c);
    if (d instanceof Response) return d;
    const caminhos = d.caminhos;
    if (!Array.isArray(caminhos) || caminhos.length === 0 || caminhos.length > CAMINHOS_POR_PEDIDO)
      return json(c, 400, { erro: `caminhos: uma lista de 1 a ${CAMINHOS_POR_PEDIDO}` });
    const invalido = caminhos.find(x => !caminhoValido(x));
    if (invalido !== undefined) return json(c, 400, { erro: `caminho inválido: ${JSON.stringify(invalido)}` });
    const unicos = [...new Set(caminhos as string[])];
    if (!cabeNaHora(s ? `conta:${s.conta_id}` : `visitante:${visitante}`, unicos.length))
      return json(c, 429, { erro: `passou de ${ASSINATURAS_POR_HORA} caminhos por hora` });
    const horaS = Math.floor(agora() / 1000);
    const urls = Object.fromEntries(unicos.map(x => [x, urlAssinada(p.segredoAssets!, p.urlAssets, x, horaS)]));
    return json(c, 200, { urls, validade_s: p.validadeAssetsS, expira_em: new Date((horaS + p.validadeAssetsS) * 1000).toISOString() });
  });

  /* o servidor dos assets, só no local: a mesma conferência que a borda faz na CN5 */
  if (p.dirAssets !== null) {
    const raiz = resolve(p.dirAssets);
    const prefixo = new URL(p.urlAssets).pathname.replace(/\/+$/, "");
    app.get("/assets/*", async c => {
      if (p.segredoAssets === null) return json(c, 503, { erro: "as URLs assinadas estão desligadas", motivo: p.motivoAssets });
      const caminho = c.req.path;
      if (!caminho.startsWith(prefixo + "/") || !caminhoValido(caminho)) return json(c, 404, { erro: "asset desconhecido" });
      const veredito = verificar(p.segredoAssets, caminho, c.req.query(PARAMETRO), Math.floor(agora() / 1000), p.validadeAssetsS);
      if (veredito !== "ok") return json(c, 403, { erro: "a URL do asset não confere", motivo: veredito });
      const arquivo = resolve(raiz, "." + caminho.slice(prefixo.length));
      if (!arquivo.startsWith(raiz + sep)) return json(c, 404, { erro: "asset desconhecido" });
      let dados: Buffer;
      try { dados = await readFile(arquivo); } catch (err) {
        const codigo = (err as NodeJS.ErrnoException).code;
        if (codigo === "ENOENT" || codigo === "EISDIR" || codigo === "ENOTDIR") return json(c, 404, { erro: "asset desconhecido" });
        throw err;
      }
      return c.body(new Uint8Array(dados), 200, { "Content-Type": TIPOS[extname(arquivo).toLowerCase()] ?? "application/octet-stream",
        "Cache-Control": "private, max-age=" + p.validadeAssetsS, "X-Robots-Tag": "noindex" });
    });
  }
}
