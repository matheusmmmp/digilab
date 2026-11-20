/* A borda (CN5, D-CONTA-197): no local, o pedido com cabeçalho de túnel leva 403 (a regra de sempre); na borda "cloudflare", só o pedido
   que passou pelo Cloudflare Tunnel entra, e a conta local (com o provedor falso) não sobe. */
import { describe, expect, it } from "vitest";
import { criarApp, type Borda } from "../src/app.ts";
import { abrirBanco } from "../src/conta/banco.ts";
import { configDoAmbiente } from "../src/conta/config.ts";
import { GeradorFala } from "../src/fala.ts";

const gerador = () => new GeradorFala(null, null);
const PELA_BORDA = { "cf-ray": "8f1c2d3e4a5b6c7d-GRU", "cf-connecting-ip": "203.0.113.7", "x-forwarded-for": "203.0.113.7" };

function contaDeFora() {
  return configDoAmbiente({ porta: 8766, banco: abrirBanco(":memory:"), ambiente: {
    DIGILAB_URL_API: "https://api.exemplo.test", DIGILAB_URL_JOGO: "https://exemplo.test/jogo/", DIGILAB_PROVEDOR_FALSO: "0" } });
}

describe("a borda local (o padrão)", () => {
  it("o pedido sem cabeçalho de túnel entra; com qualquer um, 403", async () => {
    const app = criarApp({ gerador: gerador(), motivoInicial: "" });
    expect((await app.request("/saude")).status).toBe(200);
    for (const [h, v] of Object.entries(PELA_BORDA)) expect((await app.request("/saude", { headers: { [h]: v } })).status).toBe(403);
  });
});

describe("a borda cloudflare", () => {
  const app = () => criarApp({ gerador: gerador(), motivoInicial: "", borda: "cloudflare", conta: contaDeFora() });

  it("o pedido que passou pelo túnel entra, na /saude e na conta", async () => {
    const a = app();
    const r = await a.request("/saude", { headers: PELA_BORDA });
    expect(r.status).toBe(200);
    expect(await r.json()).toEqual({ ok: true, servico: "digilab-servidor-web" });
    expect((await a.request("/auth/provedores", { headers: PELA_BORDA })).status).toBe(200);
  });

  it("o pedido que não passou pelo túnel leva 403, mesmo com só um dos dois cabeçalhos", async () => {
    const a = app();
    expect((await a.request("/saude")).status).toBe(403);
    expect((await a.request("/saude", { headers: { "cf-ray": "1" } })).status).toBe(403);
    expect((await a.request("/saude", { headers: { "cf-connecting-ip": "203.0.113.7" } })).status).toBe(403);
    expect((await a.request("/saude", { headers: { "x-forwarded-for": "203.0.113.7" } })).status).toBe(403);
    expect(await (await a.request("/saude")).json()).toEqual({ erro: "so pela borda" });
  });

  it("a página /dev/conta e o provedor falso não existem pela borda", async () => {
    const a = app();
    expect((await a.request("/dev/conta", { headers: PELA_BORDA })).status).toBe(404);
    const provedores = await (await a.request("/auth/provedores", { headers: PELA_BORDA })).json();
    expect(JSON.stringify(provedores)).not.toContain("falso");
  });

  it("a conta local não sobe na borda cloudflare", () => {
    const local = configDoAmbiente({ porta: 9, banco: abrirBanco(":memory:"), ambiente: {} });
    expect(local.local).toBe(true);
    expect(() => criarApp({ gerador: gerador(), motivoInicial: "", borda: "cloudflare", conta: local })).toThrow(/conta de fora/);
  });

  it("sem conta (--sem-conta), a borda cloudflare sobe só com a /saude e a fala", async () => {
    const a = criarApp({ gerador: gerador(), motivoInicial: "", borda: "cloudflare" });
    expect((await a.request("/api/fala/status", { headers: PELA_BORDA })).status).toBe(200);
  });

  it("borda desconhecida levanta", () => {
    expect(() => criarApp({ gerador: gerador(), motivoInicial: "", borda: "aberta" as Borda })).toThrow(/borda desconhecida/);
  });
});
