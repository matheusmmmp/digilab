/* O e2e da página de entrada (POC, docs/pranchas/ux-pagina-inicial/POC.md): o build da POC (npm run poc:build) servido pelo
   vite preview do playwright.poc.config.ts, no Chrome instalado. Sem o atlas (fica fora do git), os pets aparecem como caixas marcadas,
   e isso não é erro de console.

     npm run poc:build && npx playwright test -c playwright.poc.config.ts home */
import { expect, test, type Page } from "@playwright/test";

const HOME = "/home/";

function guardarErros(pg: Page): string[] {
  const erros: string[] = [];
  pg.on("console", m => { if (m.type() === "error") erros.push(m.text()); });
  pg.on("pageerror", e => erros.push(String(e)));
  return erros;
}

for (const [w, h] of [[390, 844], [1440, 900]] as const) {
  test(`${w} x ${h}: abre sem erro, "Começar agora" na primeira dobra leva a #/pet`, async ({ page }) => {
    const erros = guardarErros(page);
    await page.setViewportSize({ width: w, height: h });
    /* o jogo não está no build da POC: a rota do jogo responde uma página vazia */
    await page.route("**/jogo/**", r => r.fulfill({ contentType: "text/html", body: "<!doctype html><title>jogo</title>" }));
    await page.goto(HOME);
    const bt = page.locator(".heroi").getByRole("link", { name: "Começar agora" });
    await expect(bt).toBeVisible();
    const caixa = await bt.boundingBox();
    if (!caixa) throw new Error("botão sem caixa");
    expect(caixa.y + caixa.height).toBeLessThanOrEqual(h);
    expect(caixa.height).toBeGreaterThanOrEqual(44);
    expect(await bt.getAttribute("href")).toMatch(/#\/pet$/);
    await bt.click();
    await page.waitForURL(/#\/pet$/);
    expect(erros).toEqual([]);
  });
}

test("360: sem rolagem horizontal", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 780 });
  await page.goto(HOME);
  /* desce a página inteira (as imagens lazy e as seções que entram) e mede de novo no fim */
  for (const y of [0, 1500, 3000, 4500, 99999]) {
    await page.evaluate(v => window.scrollTo({ top: v, behavior: "instant" }), y);
    const [sw, iw] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    expect(sw, `scrollWidth em y=${y}`).toBeLessThanOrEqual(iw);
  }
});

test("390: a barra fixa aparece só quando os dois botões grandes saem da tela", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(HOME);
  const fixo = page.locator(".fixo");
  await expect(fixo).not.toHaveClass(/mostra/);
  await page.evaluate(() => window.scrollTo({ top: 1600, behavior: "instant" }));
  await expect(fixo).toHaveClass(/mostra/);
  await page.locator(".fecho .jogar").scrollIntoViewIfNeeded();
  await expect(fixo).not.toHaveClass(/mostra/);
});
