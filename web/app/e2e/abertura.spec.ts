/* A camera do primeiro dia (docs/pranchas/ux-ilha-abertura/, AB-1 a AB-5 APROVADAS pelo Matheus em 2026-11-10): com o pedido do ovo que
   chocou na chave da pagina, a ilha abre com a abertura B (data-abertura="tocando"), que acaba sozinha e nao volta ao recarregar; uma tecla a
   interrompe e a camera volta ao pet ("saindo", depois nada); com "reduzir movimento" ela e pulada; sem o pedido, nada. Nada entra no registro.
   O pedido nascendo do ovo de verdade fica no "mundo: o ovo novo choca na cena 3D" (jogo.spec.ts). O save e o do camera_livre.spec. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = { semente: 4242, versao: 21, log: [[480, "t", 120], [600, "d", "acariciar"], [600, "t", 120], [720, "d", "tapa"], [720, "t", 120],
  [840, "dc", { tipo: "racao", x: 168, y: 248 }], [840, "t", 60]] };
const ABERTURA = CHAVE + "-abertura";

async function abrir(browser: Browser, pedido: { semente: number; tocada: boolean } | null, reducedMotion: "reduce" | "no-preference" = "no-preference") {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1920, height: 950 }, reducedMotion });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, p]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
    if (p) localStorage.setItem(chave + "-abertura", p);
  }, [CHAVE, JSON.stringify(SAVE), pedido ? JSON.stringify(pedido) : ""] as const);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
  return { ctx, page, erros };
}
const pedido = (page: Page) => page.evaluate(k => JSON.parse(localStorage.getItem(k) ?? "null"), ABERTURA);
const registro = (page: Page) => page.evaluate(() => JSON.stringify(JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] !== "t")));
/** a abertura nao aparece por `ms` (olhando a cada 250 ms) */
async function nuncaToca(page: Page, ms: number): Promise<void> {
  for (let t = 0; t < ms; t += 250) { expect(await page.locator("[data-abertura]").count()).toBe(0); await page.waitForTimeout(250); }
}

test("abertura: o pedido do ovo toca a B uma vez, acaba sozinha e não volta ao recarregar; nada entra no registro", async ({ browser }) => {
  test.setTimeout(120_000);
  const { ctx, page, erros } = await abrir(browser, { semente: SAVE.semente, tocada: false });
  const antes = await registro(page);
  await expect(page.locator("[data-abertura='tocando']")).toHaveCount(1);
  /* a B dura 5,2 s; a folga cobre a maquina ocupada */
  await expect(page.locator("[data-abertura]")).toHaveCount(0, { timeout: 15_000 });
  expect(await pedido(page)).toEqual({ semente: SAVE.semente, tocada: true });
  expect(await registro(page)).toBe(antes);
  await page.reload();
  await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
  await nuncaToca(page, 3000);
  expect(erros).toEqual([]);
  await ctx.close();
});

test("abertura: uma tecla interrompe, a câmera volta ao pet e a abertura fica marcada", async ({ browser }) => {
  test.setTimeout(120_000);
  const { ctx, page, erros } = await abrir(browser, { semente: SAVE.semente, tocada: false });
  await expect(page.locator("[data-abertura='tocando']")).toHaveCount(1);
  await page.waitForTimeout(800);
  await page.keyboard.press("Shift");
  /* a volta dura 0,4 s (TRANSICAO_MS): bem antes do fim dos 5,2 s ela ja saiu */
  await expect(page.locator("[data-abertura]")).toHaveCount(0, { timeout: 2_000 });
  expect(await pedido(page)).toEqual({ semente: SAVE.semente, tocada: true });
  expect(erros).toEqual([]);
  await ctx.close();
});

test("abertura: com 'reduzir movimento' ela é pulada e marcada; sem pedido, ou com o pedido de outro pet, nada", async ({ browser }) => {
  test.setTimeout(120_000);
  const r = await abrir(browser, { semente: SAVE.semente, tocada: false }, "reduce");
  await nuncaToca(r.page, 3000);
  expect(await pedido(r.page)).toEqual({ semente: SAVE.semente, tocada: true });
  expect(r.erros).toEqual([]);
  await r.ctx.close();
  for (const p of [null, { semente: SAVE.semente + 1, tocada: false }]) {
    const s = await abrir(browser, p);
    await nuncaToca(s.page, 3000);
    expect(await pedido(s.page)).toEqual(p);
    expect(s.erros).toEqual([]);
    await s.ctx.close();
  }
});
