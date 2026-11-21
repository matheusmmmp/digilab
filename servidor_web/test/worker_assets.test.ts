/* O Worker dos assets (CN5, D-CONTA-199 revista): só entrega do bucket privado a URL que o servidor assinou (servidor_web/src/protecao),
   com a mesma conta, o mesmo prazo e as mesmas regras do caminho. */
import { describe, expect, it } from "vitest";
import { FOLGA_RELOGIO_S as FOLGA_SERVIDOR, PARAMETRO as PARAMETRO_SERVIDOR, caminhoValido as caminhoServidor, urlAssinada }
  from "../src/protecao/assinatura.ts";
import { TAMANHO_MINIMO_SEGREDO as MINIMO_SERVIDOR, VALIDADE_ASSETS_S } from "../src/protecao/config.ts";
import { atender, caminhoValido, FOLGA_RELOGIO_S, PARAMETRO, TAMANHO_MINIMO_SEGREDO, VALIDADE_PADRAO_S, type Ambiente, type CacheBorda,
  type ObjetoR2 } from "../deploy/worker_assets/worker.ts";

const SEGREDO = "s".repeat(40);
const BASE = "https://assets.exemplo.test";
const AGORA_S = 1_790_000_000;
const ctx = { esperas: [] as Promise<unknown>[], waitUntil(p: Promise<unknown>) { this.esperas.push(p); } };

function bucket(arquivos: Record<string, string>) {
  const lidos: string[] = [];
  return {
    lidos,
    async get(chave: string): Promise<ObjetoR2 | null> {
      lidos.push(chave);
      const t = arquivos[chave];
      if (t === undefined) return null;
      const bytes = new TextEncoder().encode(t);
      return { body: new Blob([bytes]).stream(), size: bytes.length, httpEtag: '"e1"', httpMetadata: { contentType: "application/json" } };
    },
  };
}
function cacheFalso(): CacheBorda & { guardados: Map<string, Response> } {
  const guardados = new Map<string, Response>();
  return { guardados, async match(r) { return guardados.get(r.url)?.clone(); }, async put(r, resp) { guardados.set(r.url, resp); } };
}
const amb = (b: ReturnType<typeof bucket>, extra: Partial<Ambiente> = {}): Ambiente =>
  ({ ASSETS: b, DIGILAB_SEGREDO_ASSETS: SEGREDO, DIGILAB_ORIGEM_JOGO: "https://exemplo.test", ...extra });
const pedir = (b: ReturnType<typeof bucket>, url: string, o: { metodo?: string; agoraS?: number; cache?: CacheBorda | null; extra?: Partial<Ambiente> } = {}) =>
  atender(new Request(url, { method: o.metodo ?? "GET" }), amb(b, o.extra), ctx, () => (o.agoraS ?? AGORA_S) * 1000, o.cache ?? null);

describe("o Worker dos assets", () => {
  it("as regras são as do servidor", () => {
    expect([PARAMETRO, FOLGA_RELOGIO_S, VALIDADE_PADRAO_S, TAMANHO_MINIMO_SEGREDO]).toEqual([PARAMETRO_SERVIDOR, FOLGA_SERVIDOR, VALIDADE_ASSETS_S, MINIMO_SERVIDOR]);
    for (const c of ["/sons/mapa.json", "/a/../b", "//x", "/x y", "/decoracao_up/brasao-1.png", "/" + "a".repeat(201), "sem_barra"])
      expect(caminhoValido(c)).toBe(caminhoServidor(c));
  });

  it("entrega a URL que o servidor assinou, com o tipo, o CORS da origem do jogo e o noindex", async () => {
    const b = bucket({ "sons/mapa.json": '{"ok":1}' });
    const r = await pedir(b, urlAssinada(SEGREDO, BASE, "/sons/mapa.json", AGORA_S - 30));
    expect(r.status).toBe(200);
    expect(await r.text()).toBe('{"ok":1}');
    expect(r.headers.get("content-type")).toBe("application/json");
    expect(r.headers.get("access-control-allow-origin")).toBe("https://exemplo.test");
    expect(r.headers.get("x-robots-tag")).toBe("noindex");
    expect(b.lidos).toEqual(["sons/mapa.json"]);
  });

  it("recusa sem assinatura, com outra assinatura, de outro caminho, vencida e do futuro", async () => {
    const b = bucket({ "sons/mapa.json": "{}", "sons/outro.mp3": "x" });
    const certa = urlAssinada(SEGREDO, BASE, "/sons/mapa.json", AGORA_S);
    const casos: [string, number, string][] = [
      [`${BASE}/sons/mapa.json`, AGORA_S, "sem_assinatura"],
      [urlAssinada("t".repeat(40), BASE, "/sons/mapa.json", AGORA_S), AGORA_S, "nao_confere"],
      [certa.replace("/sons/mapa.json", "/sons/outro.mp3"), AGORA_S, "nao_confere"],
      [certa, AGORA_S + VALIDADE_ASSETS_S + 1, "vencida"],
      [urlAssinada(SEGREDO, BASE, "/sons/mapa.json", AGORA_S + FOLGA_RELOGIO_S + 5), AGORA_S, "do_futuro"],
      [`${BASE}/sons/mapa.json?verify=123-abc`, AGORA_S, "malformada"],
    ];
    for (const [url, agoraS, motivo] of casos) {
      const r = await pedir(b, url, { agoraS });
      expect(r.status, url).toBe(403);
      expect(await r.json()).toEqual({ erro: motivo });
    }
    expect(b.lidos).toEqual([]);
    expect((await pedir(b, certa, { agoraS: AGORA_S + VALIDADE_ASSETS_S })).status).toBe(200);
  });

  it("caminho inválido, objeto que não existe, método errado e o preflight", async () => {
    const b = bucket({});
    expect((await pedir(b, `${BASE}/x%20y.png`)).status).toBe(404);
    expect((await pedir(b, urlAssinada(SEGREDO, BASE, "/nao/existe.png", AGORA_S))).status).toBe(404);
    expect((await pedir(b, urlAssinada(SEGREDO, BASE, "/x.png", AGORA_S), { metodo: "POST" })).status).toBe(405);
    const pre = await pedir(b, `${BASE}/x.png`, { metodo: "OPTIONS" });
    expect(pre.status).toBe(204);
    expect(pre.headers.get("access-control-allow-methods")).toBe("GET, HEAD");
  });

  it("o cache guarda pelo caminho, sem o verify: o segundo jogador não lê o R2", async () => {
    const b = bucket({ "atlas.png": "png" }), cache = cacheFalso();
    expect((await pedir(b, urlAssinada(SEGREDO, BASE, "/atlas.png", AGORA_S), { cache })).status).toBe(200);
    await Promise.all(ctx.esperas);
    expect([...cache.guardados.keys()]).toEqual([`${BASE}/atlas.png`]);
    const r = await pedir(b, urlAssinada(SEGREDO, BASE, "/atlas.png", AGORA_S + 100), { cache, agoraS: AGORA_S + 100 });
    expect(await r.text()).toBe("png");
    expect(b.lidos).toEqual(["atlas.png"]);
    /* o cache não pula a assinatura */
    expect((await pedir(b, `${BASE}/atlas.png`, { cache })).status).toBe(403);
  });

  it("sem o segredo ou sem a origem do jogo, 503", async () => {
    const b = bucket({});
    expect((await pedir(b, `${BASE}/x.png`, { extra: { DIGILAB_SEGREDO_ASSETS: "curto" } })).status).toBe(503);
    expect((await pedir(b, `${BASE}/x.png`, { extra: { DIGILAB_ORIGEM_JOGO: "" } })).status).toBe(503);
  });
});
