/* As capturas da troca das palavras (docs/TAREFA_V3_ELOGIAR_REPREENDER.md): o dock com "Elogiar" e "Repreender" no desktop (1920x950) e no
   celular (390x844, com o Mais aberto). So roda com DIGILAB_CAPTURAS_ER=1 e grava em docs/capturas_elogiar_repreender/ (nao compara com
   referencia). O pet e o primeiro save de saves_cena.json (um pet v13 nascido), sem o relogio do jogo, para a foto nao andar. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_cena.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), APP = `/${basename(REPO)}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAIDA = fileURLToPath(new URL("../../../docs/capturas_elogiar_repreender/", import.meta.url));
test.skip(!process.env.DIGILAB_CAPTURAS_ER, "so com DIGILAB_CAPTURAS_ER=1");

async function abrir(page: Page, save: object): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(save)] as const);
  await page.goto(APP + "#/pet/estado");
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect.poll(() => page.evaluate(() => (window as any).__digilab.cena()?.ret?.w ?? 0), { timeout: 30_000 }).toBeGreaterThan(0);
}
const semRelogio = (ctx: import("@playwright/test").BrowserContext) => ctx.addInitScript(() => {
  const orig = window.setInterval.bind(window);
  (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
});

for (const [w, h, nome] of [[1920, 950, "desktop"], [1280, 800, "desktop"], [390, 844, "celular"]] as const) {
  test(`captura: o dock com Elogiar e Repreender, ${nome} ${w}`, async ({ browser }) => {
    test.setTimeout(120_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await semRelogio(ctx);
    const page = await ctx.newPage();
    await abrir(page, Object.values(SAVES)[0]);
    if (nome === "celular") await page.getByRole("button", { name: "Mais", exact: true }).click();
    await expect(page.getByRole("button", { name: "Elogiar", exact: true }).first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Repreender", exact: true }).first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Carinho", exact: true })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Tapa", exact: true })).toHaveCount(0);
    if (nome === "desktop") {   /* o rotulo inteiro, sem as reticencias */
      const corte = await page.locator(".pet-dock .dock .dock-bt span").evaluateAll(es => es.filter(e => e.scrollWidth > e.clientWidth).map(e => e.textContent));
      expect(corte).toEqual([]);
    }
    await page.waitForTimeout(800);
    await page.screenshot({ path: `${SAIDA}dock_${nome}_${w}x${h}.png` });
    await ctx.close();
  });
}
