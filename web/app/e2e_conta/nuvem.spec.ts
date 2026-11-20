/* O save na nuvem (CN3) no navegador: o build com a chave da nuvem (web/dist_nuvem/, montar.ts) e o SERVIDOR DE VERDADE (servidor_web, a
   conta e as rotas /nuvem), no processo do teste: o `route` de cada contexto passa os pedidos de CAMINHO_API ao app do Hono, com os
   cookies do navegador. Dois contextos são dois aparelhos (o PC e o celular, pelo User-Agent), na mesma conta. Os quatro casos do portão
   F3 (docs/ROADMAP_V3_CONTA.md): o mesmo pet nos dois, com o "só ver" e o "Jogar aqui"; jogar offline e voltar; a divergência com a
   escolha (e o "Decidir depois"); e restaurar uma cópia. Nenhum evento pode se perder: cada caso confere o registro no banco.

     npm run e2e:conta    # monta web/dist_conta/ e web/dist_nuvem/ e roda os specs de e2e_conta/ */
import { expect, test, type Browser, type BrowserContext, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { criarApp } from "../../../servidor_web/src/app.ts";
import { abrirBanco, type Banco } from "../../../servidor_web/src/conta/banco.ts";
import { configDoAmbiente, VERSAO_PRIVACIDADE, VERSAO_TERMOS } from "../../../servidor_web/src/conta/config.ts";
import { conferirAqui } from "../../../servidor_web/src/envio/conferidor.ts";
import { GeradorFala } from "../../../servidor_web/src/fala.ts";
import { ehComeco } from "../src/nuvem/protocolo.ts";
import { APP_NUVEM, CAMINHO_API, PORTA } from "./comum.ts";

const CHAVE = "digilab-web-v21-sprites";
const CHAMPION = (JSON.parse(readFileSync(new URL("../e2e/saves.json", import.meta.url), "utf8")) as Record<string, object>).champion;
const ORIGEM = `http://127.0.0.1:${PORTA}`;
const UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36";
const UA_CEL = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Mobile Safari/537.36";
type App = ReturnType<typeof criarApp>;
interface Servidor { app: App; banco: Banco; desvio: { ms: number } }

function servidor(): Servidor {
  const banco = abrirBanco(":memory:"), desvio = { ms: 0 };
  const cfg = configDoAmbiente({ porta: PORTA, banco, agora: () => Date.now() + desvio.ms, ambiente: {
    DIGILAB_URL_API: ORIGEM + CAMINHO_API, DIGILAB_URL_JOGO: ORIGEM + APP_NUVEM, DIGILAB_CONVIDADOS: "falso:ana" } });
  return { app: criarApp({ gerador: new GeradorFala(null, null), motivoInicial: "", conta: cfg, conferidor: conferirAqui }), banco, desvio };
}
/** o login pelo provedor falso, direto no app (sem o navegador): devolve o token da sessão de um aparelho novo */
async function entrar(app: App, ua: string, primeiro: boolean): Promise<string> {
  const jar = new Map<string, string>();
  const pedir = async (caminho: string, init: RequestInit & { headers?: Record<string, string> } = {}) => {
    const headers: Record<string, string> = { "User-Agent": ua, ...(init.headers ?? {}) };
    if (jar.size) headers.Cookie = [...jar].map(([k, v]) => `${k}=${v}`).join("; ");
    const r = await app.request(caminho, { ...init, headers });
    for (const sc of r.headers.getSetCookie()) { const [par] = sc.split(";"), i = par!.indexOf("="); jar.set(par!.slice(0, i), par!.slice(i + 1)); }
    return r;
  };
  const so = (u: string) => { const x = new URL(u); return x.pathname.replace(CAMINHO_API, "") + x.search; };
  const ida = new URL((await pedir("/auth/falso?volta=%23%2Fconfig%2Fconta")).headers.get("location")!);
  const form = new URLSearchParams({ state: ida.searchParams.get("state")!, code_challenge: ida.searchParams.get("code_challenge")!, redirect_uri: ida.searchParams.get("redirect_uri")!, usuario: "ana" });
  const dado = await pedir("/auth/falso/autorizar", { method: "POST", body: form.toString(), headers: { "Content-Type": "application/x-www-form-urlencoded" } });
  await pedir(so(dado.headers.get("location")!));
  if (primeiro) {
    const p = await (await pedir("/conta/primeiro-acesso")).json() as { csrf: string };
    const r = await pedir("/conta/primeiro-acesso", { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": p.csrf },
      body: JSON.stringify({ idade: "18_ou_mais", aceite: { termos: VERSAO_TERMOS, privacidade: VERSAO_PRIVACIDADE } }) });
    expect(r.status).toBe(201);
  }
  return jar.get("dl_sessao")!;
}

interface Aparelho { ctx: BrowserContext; page: Page; rede: { fora: boolean } }
/** um aparelho: um contexto com o cookie da sessão, a rede até o servidor no processo (que cai e volta) e o save semeado */
async function aparelho(browser: Browser, s: Servidor, ua: string, primeiro: boolean, save: object | null): Promise<Aparelho> {
  const token = await entrar(s.app, ua, primeiro);
  const ctx = await browser.newContext({ userAgent: ua, viewport: { width: 1440, height: 900 } }), rede = { fora: false };
  await ctx.addCookies([{ name: "dl_sessao", value: token, url: ORIGEM }]);
  await ctx.route(u => u.pathname.startsWith(CAMINHO_API + "/"), async route => {
    if (rede.fora) { await route.abort("connectionrefused"); return; }
    const req = route.request(), url = new URL(req.url()), headers = await req.allHeaders();
    delete headers.host;
    const corpo = req.postDataBuffer();
    const r = await s.app.request(url.pathname.slice(CAMINHO_API.length) + url.search, { method: req.method(), headers, body: corpo && req.method() !== "GET" ? new Uint8Array(corpo) : undefined });
    await route.fulfill({ status: r.status, headers: Object.fromEntries(r.headers), body: Buffer.from(await r.arrayBuffer()) });
  });
  const page = await ctx.newPage();
  page.on("pageerror", e => { throw e; });
  page.on("console", m => { if (m.type() === "error") console.log(`[${ua === UA_CEL ? "celular" : "pc"}] ${m.text()}`); });
  /* semeia por uma página da mesma origem que não é o app (o app gravaria o pet dele ao fechar) */
  await page.goto("/Assets/digilab_atlas_up_pecas.json");
  await page.evaluate(([chave, txt]) => {
    localStorage.clear();
    localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0");
    localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 10, log: [] }));
    if (txt) localStorage.setItem(chave, txt);
  }, [CHAVE, save ? JSON.stringify(save) : ""] as const);
  await page.goto(APP_NUVEM);
  await expect(page.locator(".pet-tela")).toBeVisible();
  return { ctx, page, rede };
}
const chip = (p: Page) => p.getByTestId("nv-chip").first();
const sincronizarJa = (p: Page) => p.evaluate(() => dispatchEvent(new Event("digilab-nuvem-sincronizar")));
const logLocal = (p: Page) => p.evaluate(k => (JSON.parse(localStorage.getItem(k) ?? "null") as { log: unknown[][] } | null)?.log ?? [], CHAVE);
const daNuvem = (s: Servidor): unknown[][] => JSON.parse((s.banco.prepare("SELECT log FROM nuvem_pets").get() as { log: string }).log);
const contar = (s: Servidor, t: string): number => (s.banco.prepare(`SELECT count(*) AS n FROM ${t}`).get() as { n: number }).n;

/** o PC leva o pet; o celular entra e fica com os da nuvem */
async function doisAparelhos(browser: Browser, s: Servidor): Promise<[Aparelho, Aparelho]> {
  const pc = await aparelho(browser, s, UA_PC, true, CHAMPION);
  await expect(pc.page.getByTestId("nv-levar")).toBeVisible();
  await pc.page.getByTestId("nv-levar-sim").click();
  await expect(chip(pc.page)).toHaveAttribute("data-estado", "ok");
  const cel = await aparelho(browser, s, UA_CEL, false, null);
  await expect(cel.page.getByTestId("nv-escolher")).toBeVisible();
  await cel.page.getByTestId("nv-op-nuvem").click();
  await cel.page.getByTestId("nv-continuar").click();
  return [pc, cel];
}

test.describe("o save na nuvem (CN3), dois aparelhos e o servidor de verdade", () => {
  test.describe.configure({ mode: "serial" });

  test("1. o mesmo pet no PC e no celular; o celular fica só para ver até 'Jogar aqui'", async ({ browser }) => {
    const s = servidor(), [pc, cel] = await doisAparelhos(browser, s);
    /* o celular abre o pet do PC, só para ver */
    await expect(cel.page.getByTestId("nv-outro")).toBeVisible();
    await expect(cel.page.getByTestId("nv-outro")).toContainText("Chrome no Windows");
    await cel.page.getByTestId("nv-so-ver").click();
    await expect(chip(cel.page)).toHaveAttribute("data-estado", "outro");
    await expect(cel.page.locator("html")).toHaveClass(/nv-so-ver/);
    expect(await cel.page.locator(".acoes-pet").evaluate(e => getComputedStyle(e).pointerEvents)).toBe("none");
    const antes = await logLocal(cel.page);
    expect(ehComeco(antes, daNuvem(s))).toBe(true);
    /* o tempo não anda e nenhuma ação entra no registro do celular: o toque força o clique nas ações apagadas */
    await cel.page.locator(".acoes-pet button").first().click({ force: true });
    await cel.page.waitForTimeout(2500);
    expect(await logLocal(cel.page)).toEqual(antes);
    /* o PC joga; o celular recebe */
    await pc.page.locator(".acoes-pet button", { hasText: "Limpar" }).click();
    await sincronizarJa(pc.page);
    await expect.poll(() => daNuvem(s).some(e => e[1] === "d" && e[2] === "limpar")).toBe(true);
    await sincronizarJa(cel.page);
    await expect.poll(async () => ehComeco(await logLocal(cel.page), daNuvem(s)) && (await logLocal(cel.page)).length >= antes.length + 1).toBe(true);
    /* "Jogar aqui" pelo chip: o celular destrava; o PC, ao sincronizar, fica só para ver */
    await chip(cel.page).getByRole("button").click();
    await cel.page.getByTestId("nv-jogar-aqui").click();
    await expect(chip(cel.page)).toHaveAttribute("data-estado", "ok");
    await expect(cel.page.locator("html")).not.toHaveClass(/nv-so-ver/);
    await sincronizarJa(pc.page);
    await expect(pc.page.getByTestId("nv-outro")).toContainText("Chrome no Android");
    await expect(pc.page.locator("html")).toHaveClass(/nv-so-ver/);
    expect(contar(s, "nuvem_divergencias")).toBe(0);
    await pc.ctx.close(); await cel.ctx.close();
  });

  test("2 e 3. jogar offline e voltar; a divergência mostra a escolha, e nenhum evento se perde", async ({ browser }) => {
    const s = servidor(), [pc, cel] = await doisAparelhos(browser, s);
    await cel.page.getByTestId("nv-so-ver").click();
    /* o PC sem rede: o aviso aparece uma vez (UX-NV-6), e o jogo segue */
    pc.rede.fora = true;
    await pc.page.locator(".acoes-pet button", { hasText: "Brincar" }).click();
    await sincronizarJa(pc.page);
    await expect(pc.page.getByTestId("nv-fora")).toBeVisible();
    await pc.page.getByTestId("nv-fora").getByRole("button", { name: "Continuar jogando" }).click();
    await expect(chip(pc.page)).toHaveAttribute("data-estado", "offline");
    await pc.page.locator(".acoes-pet button", { hasText: "Limpar" }).click();
    const historiaPc = await logLocal(pc.page);
    expect(historiaPc.filter(e => e[1] === "d").length).toBeGreaterThan(0);
    /* a vez do PC expira; o celular joga */
    s.desvio.ms += 11 * 60_000;
    await sincronizarJa(cel.page);
    await expect(chip(cel.page)).toHaveAttribute("data-estado", "ok");
    const acoes = () => daNuvem(s).filter(e => e[1] === "d").length, antesCel = acoes();
    await cel.page.locator(".acoes-pet button", { hasText: "Elogiar" }).click();
    await sincronizarJa(cel.page);
    await expect.poll(acoes).toBeGreaterThan(antesCel);
    /* o PC volta: duas histórias, nos dois aparelhos */
    pc.rede.fora = false;
    await sincronizarJa(pc.page);
    await expect(pc.page.getByTestId("nv-divergiu")).toBeVisible();
    await expect(pc.page.getByTestId("nv-ficar")).toBeDisabled();
    await sincronizarJa(cel.page);
    await expect(cel.page.getByTestId("nv-divergiu")).toBeVisible();
    await cel.page.getByTestId("nv-depois").click();
    await expect(chip(cel.page)).toHaveAttribute("data-estado", "divergiu");
    await expect(cel.page.locator("html")).toHaveClass(/nv-so-ver/);
    const historiaCel = daNuvem(s);
    /* o PC fica com a dele */
    await pc.page.getByTestId("nv-historia-outra").click();
    await pc.page.getByTestId("nv-ficar").click();
    await expect(chip(pc.page)).toHaveAttribute("data-estado", "ok");
    expect(ehComeco(historiaPc, daNuvem(s))).toBe(true);
    await sincronizarJa(cel.page);
    await expect.poll(async () => ehComeco(historiaPc, await logLocal(cel.page))).toBe(true);
    /* a do celular foi para Gerações (só para ver), inteira */
    const h = s.banco.prepare("SELECT save FROM nuvem_historias").all() as { save: string }[];
    expect(h).toHaveLength(1);
    expect((JSON.parse(h[0]!.save) as { log: unknown[][] }).log).toEqual(historiaCel);
    await pc.page.goto(APP_NUVEM + "#/diario/geracoes");
    await expect(pc.page.getByTestId("ger-historias")).toContainText("Chrome no Android");
    await pc.ctx.close(); await cel.ctx.close();
  });

  test("4. restaurar uma cópia: a de agora vira uma cópia, e vale para os dois aparelhos", async ({ browser }) => {
    const s = servidor(), [pc, cel] = await doisAparelhos(browser, s);
    await cel.page.getByTestId("nv-so-ver").click();
    const diaria = daNuvem(s);
    await pc.page.locator(".acoes-pet button", { hasText: "Limpar" }).click();
    await sincronizarJa(pc.page);
    await expect.poll(() => daNuvem(s).length).toBeGreaterThan(diaria.length);
    await pc.page.goto(APP_NUVEM + "#/config/conta");
    /* as cópias ficam em "Aparelhos, dados e a conta" (fechado com o cais no build) */
    await pc.page.getByTestId("ct-mais").locator("summary").click();
    await expect(pc.page.getByTestId("nv-copias")).toBeVisible();
    const diarias = s.banco.prepare("SELECT id, save FROM nuvem_copias WHERE motivo = 'diaria'").all() as { id: string; save: string }[];
    expect(diarias).toHaveLength(1);
    await pc.page.getByTestId("nv-restaurar").last().click();
    await pc.page.getByTestId("nv-restaurar-sim").click();
    await expect.poll(() => s.banco.prepare("SELECT count(*) AS n FROM nuvem_copias WHERE motivo = 'antes_de_restaurar'").get()).toEqual({ n: 1 });
    expect(daNuvem(s)).toEqual((JSON.parse(diarias[0]!.save) as { log: unknown[][] }).log);
    await sincronizarJa(cel.page);
    await expect.poll(async () => ehComeco(await logLocal(cel.page), daNuvem(s))).toBe(true);
    await pc.ctx.close(); await cel.ctx.close();
  });
});
