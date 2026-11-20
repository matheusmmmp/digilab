/* As capturas da "Vida do pet", passo 2 (docs/registro/2026-11.md, a seção "VIDA DO PET, a cena e o toque"): uma por acao do pet e uma do toque, em 390, 1280 e 1920 px. So roda com
   DIGILAB_CAPTURAS_VIDA=1 e grava em docs/capturas_vida_pet_cena/ (nao compara com referencia). saves_cena.json: para cada acao, a semente e o
   registro de um pet v13 que a faz no fim dele (gerado pelo motor, que avanca de 15 em 15 min ate a acao sair; o comer, com uma racao perto);
   a captura confere que o motor ainda esta nessa acao quando tira a foto, senao repete. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_cena.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), APP = `/${basename(REPO)}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAIDA = fileURLToPath(new URL("../../../docs/capturas_vida_pet_cena/", import.meta.url));
const TELAS: [number, number][] = [[390, 844], [1280, 800], [1920, 950]];
test.skip(!process.env.DIGILAB_CAPTURAS_VIDA, "so com DIGILAB_CAPTURAS_VIDA=1");

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
/** o relogio do jogo (src/tempo.ts) e o unico setInterval de 100 ms: sem ele o tempo nao anda e o pet fica na acao que o registro termina (so a foto) */
const sem_relogio = (ctx: import("@playwright/test").BrowserContext) => ctx.addInitScript(() => {
  const orig = window.setInterval.bind(window);
  (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
});
const acaoDoMotor = (page: Page) => page.evaluate(() => (window as any).__digilab.mundo().acao as string);

for (const [w, h] of TELAS) {
  for (const acao of Object.keys(SAVES)) {
    test(`captura: ${acao} em ${w} px`, async ({ browser }) => {
      test.setTimeout(180_000);
      const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1 });
      await sem_relogio(ctx);
      const page = await ctx.newPage();
      let ok = false;
      for (let tentativa = 0; tentativa < 3 && !ok; tentativa++) {
        await abrir(page, SAVES[acao]);
        await page.waitForTimeout(400);            /* o pet chega ao ponto e a cena entra no gesto */
        if (await acaoDoMotor(page) !== acao) continue;
        await page.screenshot({ path: `${SAIDA}${acao}_${w}.png` });
        ok = await acaoDoMotor(page) === acao;
      }
      expect(ok, `o motor ficou em ${acao} durante a foto`).toBe(true);
      await ctx.close();
    });
  }
  test(`captura: o toque no pet em ${w} px`, async ({ browser }) => {
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await sem_relogio(ctx);
    const page = await ctx.newPage();
    await abrir(page, SAVES.ocioso);
    await page.waitForTimeout(1800);                 /* o pet termina de chegar ao ponto e de virar de lado */
    const c = (await page.evaluate(() => (window as any).__digilab.cena()))!.ret as { x: number; y: number; w: number; h: number }, cena = (await page.locator(".pet-cena").boundingBox())!;
    await page.mouse.click(cena.x + c.x + c.w / 2, cena.y + c.y + c.h / 2);
    await page.waitForTimeout(350);
    expect(await page.evaluate(() => (window as any).__digilab.reacao())).not.toBeNull();
    await page.screenshot({ path: `${SAIDA}toque_${w}.png` });
    await ctx.close();
  });
}
