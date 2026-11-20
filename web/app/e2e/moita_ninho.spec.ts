/* A arvore na frente do ninho fica transparente (docs/TAREFA_V3_MOITA_NINHO.md), a 1280x800: do primeiro acesso ao brasao, o ovo choca no
   ninho da ilha grande, atras da arvore e da moita da camera de sempre; logo depois de chocar, pelo menos um objeto da ilha esta
   transparente (a leitura `tapando` do __digilab, ilha/transparente.ts). Sem erro no console. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";

function vigiarErros(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => {
    if (m.type() !== "error") return;
    const url = m.location().url ?? "";
    if (/favicon\.ico$/.test(url) || /\/api\//.test(url) || /502|Bad Gateway/.test(m.text())) return;
    erros.push("console: " + m.text() + (url ? ` (${url})` : ""));
  });
  return erros;
}

test("a arvore na frente do ninho fica transparente", async ({ browser }) => {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage(), erros = vigiarErros(page);
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(c => { localStorage.clear(); localStorage.setItem(c + "-dicas-ligadas", "0"); }, CHAVE);
  await page.goto(APP + "#/inicio");
  await page.getByRole("button", { name: /começar/i }).click();
  const brasao = page.locator("dialog.brasao-tela[open]"), pular = page.getByRole("button", { name: /^pular$/i });
  await expect(brasao.or(pular).first()).toBeVisible({ timeout: 20_000 });
  for (let k = 0; k < 3 && !(await brasao.isVisible()); k++) {
    if (await pular.isVisible()) await pular.click();
    await expect(brasao.or(pular).first()).toBeVisible({ timeout: 20_000 });
  }
  await brasao.locator(".br-card").first().click();
  await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);
  /* os kits na cena (data-objetos), e logo depois a arvore e a moita na frente do ninho ficam transparentes */
  await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 60_000 });
  await expect.poll(async () => page.evaluate(() => (window as unknown as { __digilab: { tapando(): number } }).__digilab.tapando()),
    { timeout: 10_000 }).toBeGreaterThanOrEqual(1);
  expect(erros).toEqual([]);
  await ctx.close();
});
