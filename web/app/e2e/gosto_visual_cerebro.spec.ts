/* A captura ligada ao cérebro no jogo (GOSTO_VISUAL, 2026-11-12; docs/registro/2026-11.md, D-GV-CEREBRO-1 a 10): o pet de um só da v32 (o pet de
   exemplo do primeiro acesso, sem save), a TV do jogo do P0 ligada pelo painel da TV, o pet levado até ela pelo botão "Levar até a TV". O que a
   TV passa entra no registro pelo "st" (só os sete níveis), o cérebro escolhe olhar, e o painel da TV e o do DigiBrain dizem a mesma coisa:
   "olhando a TV" e "olhar". A captura real é bloqueada no navegador do app; a TV do jogo alimenta o cérebro pela mesma via (a fonte "tv").
   As capturas de tela vão para DIGILAB_CAPTURAS (cerebro_*.png), quando a variável existe. */
import { expect, test, type Browser, type Page } from "@playwright/test";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const CAPTURAS = process.env.DIGILAB_CAPTURAS ?? null;

async function abrir(browser: Browser, largura: number, altura: number) {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: altura } });
  const page = await ctx.newPage();
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(chave => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
  }, CHAVE);
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
  return { ctx, page, erros };
}
const estado = (page: Page) => page.evaluate(() => {
  const d = (window as any).__digilab, r = JSON.parse(d.registro());
  return { versao: r.versao as number, st: (r.log as unknown[][]).filter(e => e[1] === "st").map(e => e[2] as string), tv: d.tvCerebro() };
});
/** anda o jogo, levando o pet até a TV quando ela sai da vista dele, até o cérebro escolher olhar; aí pausa o relógio (para a captura) */
const esperarOlhar = (page: Page) => page.evaluate(async () => {
  const d = (window as any).__digilab, t0 = performance.now();
  let levou = 0;
  while (performance.now() - t0 < 150_000) {
    const c = d.tvCerebro();
    if (c && c.olhando) { d.velocidade(0); return true; }
    const b = document.querySelector<HTMLButtonElement>("[data-tv-levar]");
    if (c && !c.noRaio && b && performance.now() - levou > 1500) { b.click(); levou = performance.now(); }
    await new Promise(r => setTimeout(r, 20));
  }
  return false;
});
const capturar = async (page: Page, nome: string) => { if (CAPTURAS) await page.screenshot({ path: join(CAPTURAS, nome) }); };

test("a TV no cérebro, no desktop: o st no registro, o painel da TV diz olhando e o DigiBrain diz olhar", async ({ browser }) => {
  test.setTimeout(240_000);
  const { ctx, page, erros } = await abrir(browser, 1440, 900);
  expect((await estado(page)).versao).toBe(38);   // o ovo novo: a v38 (a v35 com o equilibrio do cuidado; a v35 e a v30 com a TV no jogo)
  await page.locator(".pet-hud [data-painel-pet='tv'] button").click();
  const painel = page.getByTestId("painel-tv");
  await expect(painel.getByTestId("tv-prot")).toContainText("entra no cérebro dele");
  await painel.getByRole("button", { name: "Ligar a TV" }).click();
  await expect(painel.getByTestId("tv-reacao")).toContainText("No cérebro:", { timeout: 15_000 });
  expect(await esperarOlhar(page)).toBe(true);
  await expect(painel.getByTestId("tv-reacao")).toContainText("No cérebro: olhando a TV");
  const e = await estado(page);
  expect(e.st.length).toBeGreaterThan(0);
  expect(e.st.every(v => /^tv(\|([0-9]|1[0-5])){7}$/.test(v))).toBe(true);
  await page.waitForTimeout(1200);                                       // o pet desenhado chega à almofada
  await capturar(page, "cerebro_tv_desktop.png");
  await page.keyboard.press("Escape");
  await page.locator(".pet-hud [data-painel-pet='digibrain'] button").click();
  await expect(page.locator("#pet-painel .scan-estado")).toContainText("olhar");
  await page.waitForTimeout(800);
  await capturar(page, "cerebro_digibrain_desktop.png");
  expect(erros).toEqual([]);
  await ctx.close();
});

test("a TV no cérebro, no celular: a folha da TV diz olhando e o DigiBrain diz olhar", async ({ browser }) => {
  test.setTimeout(240_000);
  const { ctx, page, erros } = await abrir(browser, 390, 844);
  await page.locator(".mm-retrato").click();
  await page.locator("#leque-pet").getByRole("button", { name: "TV", exact: true }).click();
  const painel = page.getByTestId("painel-tv");
  await painel.getByRole("button", { name: "Ligar a TV" }).click();
  await expect(painel.getByTestId("tv-reacao")).toContainText("No cérebro:", { timeout: 15_000 });
  expect(await esperarOlhar(page)).toBe(true);
  await expect(painel.getByTestId("tv-reacao")).toContainText("No cérebro: olhando a TV");
  await page.waitForTimeout(1200);
  await capturar(page, "cerebro_tv_celular.png");
  await page.keyboard.press("Escape");
  await page.locator(".mm-retrato").click();
  await page.locator("#leque-pet").getByRole("button", { name: "DigiBrain", exact: true }).click();
  await expect(page.locator("#pet-painel .scan-estado")).toContainText("olhar");
  await page.waitForTimeout(800);
  await capturar(page, "cerebro_digibrain_celular.png");
  expect(erros).toEqual([]);
  await ctx.close();
});
