/* A proteção (CN4): o robots.txt, as URLs assinadas dos assets, o visitante pelo Turnstile, o Turnstile na criação da conta e a cota da
   fala por conta. O Turnstile usa as chaves de teste oficiais da Cloudflare com o fetch falso (siteverifyDeTeste); a LLM, o cliente falso:
   nenhuma chamada sai da máquina. */
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { criarApp } from "../src/app.ts";
import { abrirBanco } from "../src/conta/banco.ts";
import { configDoAmbiente, VERSAO_PRIVACIDADE, VERSAO_TERMOS } from "../src/conta/config.ts";
import { conferirAqui } from "../src/envio/conferidor.ts";
import { GeradorFala, ProvedorClaude, type ClienteClaude } from "../src/fala.ts";
import { ControleGasto } from "../src/gasto.ts";
import { assinarCaminho, caminhoValido, macDe, urlAssinada, verificar } from "../src/protecao/assinatura.ts";
import { ASSINATURAS_POR_HORA, CAMINHOS_POR_PEDIDO, COTA_FALA_DIA, protecaoDoAmbiente, VALIDADE_ASSETS_S } from "../src/protecao/config.ts";
import { ROBOS_DE_IA, robotsDaApi, robotsDoJogo } from "../src/protecao/robots.ts";
import { COOKIE_VISITANTE } from "../src/protecao/rotas.ts";
import { CHAVES_DE_TESTE, siteverifyDeTeste, TurnstileCloudflare, type Buscar } from "../src/protecao/turnstile.ts";
import { API, contar, criarConta, Navegador, ORIGEM_JOGO, JOGO } from "./navegador.ts";

const SEGREDO = "segredo-de-teste-dos-assets-com-32+";
const corpo = (r: Response): Promise<any> => r.json();

function clienteFalso() {
  const pedidos: Record<string, unknown>[] = [];
  const criar = async (p: Record<string, unknown>) => {
    pedidos.push(p);
    return { content: [{ type: "text", text: '{"abertura": "Eba!", "fecho": "^_^"}' }], stop_reason: "end_turn", model: p.model,
      usage: { input_tokens: 400, output_tokens: 20 } };
  };
  const cliente: ClienteClaude = { messages: { create: criar }, beta: { messages: { create: criar } } };
  return { cliente, pedidos };
}

interface Opcoes { ambiente?: Record<string, string>; buscarTurnstile?: Buscar; comLlm?: boolean }

function montarProtecao({ ambiente = {}, buscarTurnstile, comLlm = false }: Opcoes = {}) {
  const relogio = { t: Date.UTC(2026, 10, 16, 12) };
  const banco = abrirBanco(":memory:");
  const cfg = configDoAmbiente({ porta: 8766, banco, agora: () => relogio.t, buscarTurnstile,
    ambiente: { DIGILAB_URL_API: API, DIGILAB_URL_JOGO: JOGO, DIGILAB_CONVIDADOS: "falso:ana falso:caio", ...ambiente } });
  const falso = clienteFalso();
  const dirGasto = mkdtempSync(join(tmpdir(), "digilab-gasto-"));
  const gerador = comLlm
    ? new GeradorFala(new ProvedorClaude(falso.cliente), new ControleGasto(2, join(dirGasto, "gasto.json")), 1000, () => relogio.t)
    : new GeradorFala(null, null);
  return { app: criarApp({ gerador, motivoInicial: "", conta: cfg, conferidor: conferirAqui }), cfg, banco, relogio, pedidos: falso.pedidos };
}

const postarJson = (nav: Navegador, caminho: string, dados: unknown, extra: Record<string, string> = {}) => nav.json("POST", caminho, dados, undefined, extra);

describe("o robots.txt", () => {
  it("o do jogo é o gerado da lista (node scripts/gerar_robots.ts) e recusa cada robô de IA", () => {
    const arquivo = fileURLToPath(new URL("../../web/app/public/robots.txt", import.meta.url));
    /* o checkout do Windows pode trazer CRLF */
    const texto = readFileSync(arquivo, "utf8").replaceAll("\r\n", "\n");
    expect(texto, "rode node scripts/gerar_robots.ts").toBe(robotsDoJogo());
    for (const r of ROBOS_DE_IA) expect(texto).toContain(`User-agent: ${r}\n`);
    expect(texto).toMatch(/User-agent: DuckAssistBot\nDisallow: \/\n/);
    expect(new Set(ROBOS_DE_IA).size).toBe(ROBOS_DE_IA.length);
  });
  it("a API serve o dela: ninguém indexa nada, com e sem a conta", async () => {
    const { app } = montarProtecao();
    const r = await app.request("/robots.txt");
    expect(r.status).toBe(200);
    expect(await r.text()).toBe(robotsDaApi());
    const sem = criarApp({ gerador: new GeradorFala(null, null), motivoInicial: "" });
    expect(await (await sem.request("/robots.txt")).text()).toMatch(/User-agent: \*\nDisallow: \/\n/);
  });
});

describe("a assinatura", () => {
  it("o formato do token da Cloudflare: hora-mac, o mac é o base64 do HMAC-SHA256 do caminho mais a hora (conferido pelo WebCrypto)", async () => {
    const hora = 1_763_300_000, caminho = "/assets/atlas/pecas.png";
    const chave = await crypto.subtle.importKey("raw", new TextEncoder().encode(SEGREDO), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
    const mac = new Uint8Array(await crypto.subtle.sign("HMAC", chave, new TextEncoder().encode(caminho + hora)));
    const esperado = btoa(String.fromCharCode(...mac));
    expect(macDe(SEGREDO, caminho, hora)).toBe(esperado);
    expect(assinarCaminho(SEGREDO, caminho, hora)).toBe(`${hora}-${esperado}`);
    const u = new URL(urlAssinada(SEGREDO, "https://assets.exemplo.test/", "/atlas/pecas.png", hora));
    expect(u.pathname).toBe("/atlas/pecas.png");
    expect(u.searchParams.get("verify")).toBe(`${hora}-${macDe(SEGREDO, "/atlas/pecas.png", hora)}`);
    expect(u.search).not.toContain("+");
  });
  it("confere a hora, o caminho e o segredo", () => {
    const hora = 1_763_300_000, c = "/assets/a.png", v = assinarCaminho(SEGREDO, c, hora);
    expect(verificar(SEGREDO, c, v, hora, 600)).toBe("ok");
    expect(verificar(SEGREDO, c, v, hora + 600, 600)).toBe("ok");
    expect(verificar(SEGREDO, c, v, hora + 601, 600)).toBe("vencida");
    expect(verificar(SEGREDO, c, v, hora - 61, 600)).toBe("do_futuro");
    expect(verificar(SEGREDO, "/assets/b.png", v, hora, 600)).toBe("nao_confere");
    expect(verificar(SEGREDO + "x", c, v, hora, 600)).toBe("nao_confere");
    expect(verificar(SEGREDO, c, `${hora + 1}${v.slice(String(hora).length)}`, hora, 600)).toBe("nao_confere");
    expect(verificar(SEGREDO, c, undefined, hora, 600)).toBe("sem_assinatura");
    expect(verificar(SEGREDO, c, "abc", hora, 600)).toBe("malformada");
  });
  it("só caminhos simples", () => {
    for (const ok of ["/a.png", "/atlas/x_1-2.json", "/sons/a/b.ogg"]) expect(caminhoValido(ok)).toBe(true);
    for (const ruim of ["a.png", "/", "/../x", "/a//b", "/a?b", "/a b", "/%2e%2e/x", 5, "/" + "a".repeat(201)]) expect(caminhoValido(ruim)).toBe(false);
  });
});

describe("a configuração", () => {
  it("o segredo curto, a base sem https e o Turnstile pela metade não sobem; fora do local, o Turnstile é obrigatório", () => {
    expect(() => protecaoDoAmbiente({ DIGILAB_SEGREDO_ASSETS: "curto" }, true, API)).toThrow(/32/);
    expect(() => protecaoDoAmbiente({ DIGILAB_TURNSTILE: "0", DIGILAB_URL_ASSETS: "http://assets.exemplo.test" }, false, "https://api.exemplo.test")).toThrow(/https/);
    expect(() => protecaoDoAmbiente({ DIGILAB_TURNSTILE: "0", DIGILAB_SEGREDO_ASSETS: SEGREDO }, false, "https://api.exemplo.test")).toThrow(/DIGILAB_URL_ASSETS/);
    expect(() => protecaoDoAmbiente({ DIGILAB_TURNSTILE: "1" }, true, API)).toThrow(/TURNSTILE_SECRET_KEY/);
    expect(() => protecaoDoAmbiente({ TURNSTILE_SECRET_KEY: CHAVES_DE_TESTE.segredoPassa }, true, API)).toThrow(/TURNSTILE_SITE_KEY/);
    expect(() => protecaoDoAmbiente({}, false, "https://api.exemplo.test")).toThrow(/DIGILAB_TURNSTILE=0/);
    expect(() => protecaoDoAmbiente({ DIGILAB_TURNSTILE: "talvez" }, true, API)).toThrow(/"0" ou "1"/);
    expect(() => protecaoDoAmbiente({ DIGILAB_TURNSTILE: "0", DIGILAB_DIR_ASSETS: "x" }, false, "https://api.exemplo.test")).toThrow(/só do local/);
  });
  it("os padrões: no local, tudo desligado e a fala sem conta como na CN1; fora, a fala só com conta", () => {
    const local = protecaoDoAmbiente({}, true, API);
    expect(local).toMatchObject({ segredoAssets: null, turnstile: null, cotaFalaDia: COTA_FALA_DIA, falaSoComConta: false,
      validadeAssetsS: VALIDADE_ASSETS_S, urlAssets: `${API}/assets` });
    const fora = protecaoDoAmbiente({ DIGILAB_TURNSTILE: "0" }, false, "https://api.exemplo.test");
    expect(fora).toMatchObject({ falaSoComConta: true, dirAssets: null, turnstile: null });
    const ts = protecaoDoAmbiente({ TURNSTILE_SECRET_KEY: CHAVES_DE_TESTE.segredoPassa, TURNSTILE_SITE_KEY: CHAVES_DE_TESTE.sitePassa }, false, "https://api.exemplo.test");
    expect(ts.turnstile?.chaveSite).toBe(CHAVES_DE_TESTE.sitePassa);
  });
});

describe("o Turnstile com as chaves de teste oficiais", () => {
  it("passa, falha, o token usado, sem token, o token grande e a Cloudflare fora do ar", async () => {
    const chamadas: { segredo: string; token: string }[] = [];
    const passa = new TurnstileCloudflare(CHAVES_DE_TESTE.segredoPassa, CHAVES_DE_TESTE.sitePassa, siteverifyDeTeste(chamadas));
    expect(await passa.conferir(CHAVES_DE_TESTE.tokenFalso, "cadastro")).toEqual({ ok: true });
    expect(chamadas).toEqual([{ segredo: CHAVES_DE_TESTE.segredoPassa, token: CHAVES_DE_TESTE.tokenFalso }]);
    expect(await passa.conferir("", "cadastro")).toMatchObject({ ok: false, motivo: "sem_token" });
    expect(await passa.conferir(42, "cadastro")).toMatchObject({ ok: false, motivo: "token_invalido" });
    expect(await passa.conferir("x".repeat(2049), "cadastro")).toMatchObject({ ok: false, motivo: "token_invalido" });
    expect(chamadas).toHaveLength(1);
    const falha = new TurnstileCloudflare(CHAVES_DE_TESTE.segredoFalha, CHAVES_DE_TESTE.siteBloqueia, siteverifyDeTeste());
    expect(await falha.conferir(CHAVES_DE_TESTE.tokenFalso, "cadastro")).toEqual({ ok: false, motivo: "nao_passou", codigos: ["invalid-input-response"] });
    const usado = new TurnstileCloudflare(CHAVES_DE_TESTE.segredoUsado, CHAVES_DE_TESTE.sitePassa, siteverifyDeTeste());
    expect(await usado.conferir(CHAVES_DE_TESTE.tokenFalso, "cadastro")).toEqual({ ok: false, motivo: "nao_passou", codigos: ["timeout-or-duplicate"] });
    const fora = new TurnstileCloudflare(CHAVES_DE_TESTE.segredoPassa, CHAVES_DE_TESTE.sitePassa, async () => { throw new TypeError("fetch failed"); });
    expect(await fora.conferir(CHAVES_DE_TESTE.tokenFalso, "cadastro")).toEqual({ ok: false, motivo: "indisponivel", codigos: ["TypeError"] });
    const outraAcao = new TurnstileCloudflare("s", "k", async () => new Response(JSON.stringify({ success: true, action: "visitante" })));
    expect(await outraAcao.conferir("t", "cadastro")).toMatchObject({ ok: false, codigos: ["action_diferente"] });
  });

  it("na criação da conta: sem token, 403 e o acesso pendente fica; com o token, a conta nasce", async () => {
    const chamadas: { segredo: string; token: string }[] = [];
    const { app, banco } = montarProtecao({ buscarTurnstile: siteverifyDeTeste(chamadas),
      ambiente: { TURNSTILE_SECRET_KEY: CHAVES_DE_TESTE.segredoPassa, TURNSTILE_SITE_KEY: CHAVES_DE_TESTE.sitePassa } });
    const nav = new Navegador(app);
    await expect(criarConta(nav)).rejects.toThrow();
    expect(contar(banco, "contas")).toBe(0);
    const p = await corpo(await nav.pedir("/conta/primeiro-acesso"));
    expect(p.turnstile).toBe(CHAVES_DE_TESTE.sitePassa);
    const r = await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: { termos: VERSAO_TERMOS, privacidade: VERSAO_PRIVACIDADE },
      turnstile: CHAVES_DE_TESTE.tokenFalso }, p.csrf);
    expect(r.status).toBe(201);
    expect(contar(banco, "contas")).toBe(1);
    expect(chamadas.at(-1)).toEqual({ segredo: CHAVES_DE_TESTE.segredoPassa, token: CHAVES_DE_TESTE.tokenFalso });
  });

  it("o segredo que sempre falha segura a conta; desligado, a conta nasce sem token", async () => {
    const { app, banco } = montarProtecao({ buscarTurnstile: siteverifyDeTeste(),
      ambiente: { TURNSTILE_SECRET_KEY: CHAVES_DE_TESTE.segredoFalha, TURNSTILE_SITE_KEY: CHAVES_DE_TESTE.siteBloqueia } });
    const nav = new Navegador(app);
    await expect(criarConta(nav, "ana", CHAVES_DE_TESTE.tokenFalso)).rejects.toThrow();
    const p = await corpo(await nav.pedir("/conta/primeiro-acesso"));
    const r = await nav.json("POST", "/conta/primeiro-acesso", { idade: "18_ou_mais", aceite: { termos: VERSAO_TERMOS, privacidade: VERSAO_PRIVACIDADE },
      turnstile: CHAVES_DE_TESTE.tokenFalso }, p.csrf);
    expect(r.status).toBe(403);
    expect(await corpo(r)).toMatchObject({ estado: "turnstile", motivo: "nao_passou", codigos: ["invalid-input-response"] });
    expect(contar(banco, "contas")).toBe(0);
    const desligado = montarProtecao();
    const nav2 = new Navegador(desligado.app);
    expect((await corpo(await (async () => { await criarConta(nav2); return nav2.pedir("/conta"); })())).conta.apelido).toBeTruthy();
  });
});

describe("as URLs assinadas dos assets", () => {
  const pasta = (): string => {
    const d = mkdtempSync(join(tmpdir(), "digilab-assets-"));
    mkdirSync(join(d, "atlas"));
    writeFileSync(join(d, "atlas", "pecas.png"), Buffer.from([0x89, 0x50, 0x4e, 0x47, 1, 2, 3]));
    writeFileSync(join(d, "segredo.txt"), "fora");
    return d;
  };

  it("desligadas sem o segredo: o estado diz por quê, e assinar responde 503", async () => {
    const { app } = montarProtecao();
    expect(await corpo(await app.request("/assets/estado"))).toEqual({ ligado: false, motivo: "sem DIGILAB_SEGREDO_ASSETS no ambiente",
      validade_s: VALIDADE_ASSETS_S, turnstile: null });
    const nav = new Navegador(app);
    await criarConta(nav);
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/atlas/pecas.png"] })).status).toBe(503);
  });

  it("com a sessão: assina, a URL serve o arquivo no local, e vence com o relógio", async () => {
    const dir = pasta();
    const { app, relogio } = montarProtecao({ ambiente: { DIGILAB_SEGREDO_ASSETS: SEGREDO, DIGILAB_DIR_ASSETS: dir } });
    const nav = new Navegador(app);
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/atlas/pecas.png"] })).status).toBe(401);
    await criarConta(nav);
    const r = await postarJson(nav, "/assets/assinar", { caminhos: ["/atlas/pecas.png", "/atlas/pecas.png"] }, { Origin: ORIGEM_JOGO });
    expect(r.status).toBe(200);
    expect(r.headers.get("access-control-allow-origin")).toBe(ORIGEM_JOGO);
    const d = await corpo(r);
    expect(Object.keys(d.urls)).toEqual(["/atlas/pecas.png"]);
    expect(d.validade_s).toBe(VALIDADE_ASSETS_S);
    const u = new URL(d.urls["/atlas/pecas.png"]);
    expect(u.origin + u.pathname).toBe(`${API}/assets/atlas/pecas.png`);
    const arquivo = await app.request(u.pathname + u.search);
    expect(arquivo.status).toBe(200);
    expect(arquivo.headers.get("content-type")).toBe("image/png");
    expect(arquivo.headers.get("x-robots-tag")).toBe("noindex");
    expect(new Uint8Array(await arquivo.arrayBuffer())).toEqual(new Uint8Array([0x89, 0x50, 0x4e, 0x47, 1, 2, 3]));
    /* sem a assinatura, com a de outro arquivo, e depois da validade */
    expect(await corpo(await app.request(u.pathname))).toMatchObject({ motivo: "sem_assinatura" });
    expect((await app.request("/assets/segredo.txt" + u.search)).status).toBe(403);
    relogio.t += (VALIDADE_ASSETS_S + 1) * 1000;
    expect(await corpo(await app.request(u.pathname + u.search))).toMatchObject({ motivo: "vencida" });
    /* um arquivo que não existe, assinado, é 404 */
    const outra = await corpo(await postarJson(nav, "/assets/assinar", { caminhos: ["/atlas/nao_tem.png"] }));
    const v = new URL(outra.urls["/atlas/nao_tem.png"]);
    expect((await app.request(v.pathname + v.search)).status).toBe(404);
  });

  it("os limites: caminho inválido, lista grande, outra origem e o teto por hora", async () => {
    const { app, relogio } = montarProtecao({ ambiente: { DIGILAB_SEGREDO_ASSETS: SEGREDO } });
    const nav = new Navegador(app);
    await criarConta(nav);
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/../conta.sqlite"] })).status).toBe(400);
    expect((await postarJson(nav, "/assets/assinar", { caminhos: [] })).status).toBe(400);
    const muitos = Array.from({ length: CAMINHOS_POR_PEDIDO + 1 }, (_, i) => `/a/${i}.png`);
    expect((await postarJson(nav, "/assets/assinar", { caminhos: muitos })).status).toBe(400);
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/a.png"] }, { Origin: "https://outro.exemplo" })).status).toBe(403);
    let feitos = 0, codigo = 200;
    while (codigo === 200) {
      const lote = Array.from({ length: CAMINHOS_POR_PEDIDO }, (_, i) => `/l/${feitos + i}.png`);
      codigo = (await postarJson(nav, "/assets/assinar", { caminhos: lote })).status;
      if (codigo === 200) feitos += lote.length;
    }
    expect(codigo).toBe(429);
    expect(feitos).toBe(Math.floor(ASSINATURAS_POR_HORA / CAMINHOS_POR_PEDIDO) * CAMINHOS_POR_PEDIDO);
    relogio.t += 3600_000;
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/a.png"] })).status).toBe(200);
  });

  it("o visitante sem conta: passa pelo Turnstile, leva o cookie e assina; o cookie mexido ou vencido não serve", async () => {
    const { app, relogio } = montarProtecao({ buscarTurnstile: siteverifyDeTeste(),
      ambiente: { DIGILAB_SEGREDO_ASSETS: SEGREDO, TURNSTILE_SECRET_KEY: CHAVES_DE_TESTE.segredoPassa, TURNSTILE_SITE_KEY: CHAVES_DE_TESTE.sitePassa } });
    expect((await corpo(await app.request("/assets/estado"))).turnstile).toBe(CHAVES_DE_TESTE.sitePassa);
    const nav = new Navegador(app);
    const semVisitante = await postarJson(nav, "/assets/assinar", { caminhos: ["/a.png"] });
    expect(semVisitante.status).toBe(401);
    expect((await corpo(semVisitante)).turnstile).toBe(CHAVES_DE_TESTE.sitePassa);
    expect((await postarJson(nav, "/assets/visitante", {})).status).toBe(403);
    expect((await postarJson(nav, "/assets/visitante", { turnstile: CHAVES_DE_TESTE.tokenFalso })).status).toBe(200);
    expect(nav.cookies.get(COOKIE_VISITANTE)).toMatch(/^\d+\.[0-9a-f-]{36}\.[A-Za-z0-9_-]{43}$/);
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/a.png"] })).status).toBe(200);
    const bom = nav.cookies.get(COOKIE_VISITANTE)!;
    nav.cookies.set(COOKIE_VISITANTE, bom.replace(/^\d+/, String(Date.UTC(2030, 0, 1))));
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/a.png"] })).status).toBe(401);
    nav.cookies.set(COOKIE_VISITANTE, bom);
    relogio.t += 25 * 3600_000;
    expect((await postarJson(nav, "/assets/assinar", { caminhos: ["/a.png"] })).status).toBe(401);
  });

  it("o visitante com o Turnstile fora do ar: 503, e nada de cookie", async () => {
    const { app } = montarProtecao({ buscarTurnstile: async () => { throw new TypeError("fetch failed"); },
      ambiente: { DIGILAB_SEGREDO_ASSETS: SEGREDO, TURNSTILE_SECRET_KEY: CHAVES_DE_TESTE.segredoPassa, TURNSTILE_SITE_KEY: CHAVES_DE_TESTE.sitePassa } });
    const nav = new Navegador(app);
    expect((await postarJson(nav, "/assets/visitante", { turnstile: CHAVES_DE_TESTE.tokenFalso })).status).toBe(503);
    expect(nav.cookies.has(COOKIE_VISITANTE)).toBe(false);
  });
});

describe("a cota da fala", () => {
  const fala = (nav: Navegador, tick: number, extra: Record<string, string> = {}) => {
    const texto = JSON.stringify({ motivo: { origem: "vida", acao: "comer", fatores: ["fome"], evento_ref: [3], intensidade: 0.7, exploracao: false, tick },
      estagio: "adulto", humor: 0.5 });
    return nav.pedir("/api/fala", { method: "POST", body: texto,
      headers: { "Content-Type": "application/json", "Content-Length": String(Buffer.byteLength(texto)), ...extra } });
  };

  it("com a sessão: a LLM até a cota, depois o template; o dia seguinte zera; o cache não gasta", async () => {
    const { app, relogio, pedidos, banco } = montarProtecao({ comLlm: true, ambiente: { DIGILAB_COTA_FALA_DIA: "3" } });
    const nav = new Navegador(app);
    await criarConta(nav);
    for (let i = 0; i < 3; i++) {
      const d = await corpo(await fala(nav, 100 + i));
      expect(d.fonte).toBe("llm");
      expect(d.cota).toMatchObject({ limite: 3, usadas: i + 1, restam: 2 - i, dia: "2026-11-16" });
    }
    const cheia = await corpo(await fala(nav, 200));
    expect(cheia).toMatchObject({ fonte: "template", detalhe: "a cota do dia acabou (3 falas pela LLM por conta)", cota: { restam: 0 } });
    expect(pedidos).toHaveLength(3);
    /* o mesmo motivo de antes vem do cache, sem gastar */
    expect((await corpo(await fala(nav, 100))).fonte).toBe("llm");
    expect(pedidos).toHaveLength(3);
    const status = await corpo(await nav.pedir("/api/fala/status"));
    expect(status.cota).toMatchObject({ usadas: 3, restam: 0 });
    expect(status.so_com_conta).toBe(false);
    /* a virada do dia de Brasília (03:00 UTC) */
    relogio.t = Date.UTC(2026, 10, 17, 3);
    const nova = await corpo(await fala(nav, 300));
    expect(nova).toMatchObject({ fonte: "llm", cota: { usadas: 1, dia: "2026-11-17" } });
    expect((await corpo(await nav.pedir("/conta/dados"))).cota_fala).toEqual([{ dia: "2026-11-16", usadas: 3 }, { dia: "2026-11-17", usadas: 1 }]);
    /* apagar a conta leva a cota */
    const csrf = (await corpo(await nav.pedir("/conta"))).csrf;
    expect((await nav.json("DELETE", "/conta", { confirmar: "apagar" }, csrf)).status).toBe(200);
    expect(contar(banco, "cota_fala")).toBe(0);
  });

  it("sem a sessão: no local, segue o teto total (CN1); com DIGILAB_FALA_SO_COM_CONTA=1, só o template", async () => {
    const local = montarProtecao({ comLlm: true });
    const d = await corpo(await fala(new Navegador(local.app), 1));
    expect(d).toMatchObject({ fonte: "llm", cota: null });
    const so = montarProtecao({ comLlm: true, ambiente: { DIGILAB_FALA_SO_COM_CONTA: "1" } });
    const t = await corpo(await fala(new Navegador(so.app), 1));
    expect(t).toMatchObject({ fonte: "template", detalhe: "sem conta: só o template", cota: null });
    expect(so.pedidos).toHaveLength(0);
    expect((await corpo(await so.app.request("/api/fala/status"))).so_com_conta).toBe(true);
  });

  it("outra origem leva 403; a do jogo recebe o CORS com credenciais", async () => {
    const { app } = montarProtecao({ comLlm: true });
    const nav = new Navegador(app);
    expect((await fala(nav, 1, { Origin: "https://outro.exemplo" })).status).toBe(403);
    const r = await fala(nav, 1, { Origin: ORIGEM_JOGO });
    expect(r.status).toBe(200);
    expect(r.headers.get("access-control-allow-origin")).toBe(ORIGEM_JOGO);
    expect(r.headers.get("access-control-allow-credentials")).toBe("true");
  });

  it("sem a conta (--sem-conta), a fala é a da CN1: sem o campo cota", async () => {
    const app = criarApp({ gerador: new GeradorFala(null, null), motivoInicial: "" });
    const texto = JSON.stringify({ motivo: { origem: "vida", acao: "comer", fatores: ["fome"], evento_ref: [3], intensidade: 0.7, exploracao: false, tick: 1 }, estagio: "adulto", humor: 0.5 });
    const d = await corpo(await app.request("/api/fala", { method: "POST", body: texto, headers: { "Content-Type": "application/json", "Content-Length": String(texto.length) } }));
    expect("cota" in d).toBe(false);
  });
});
