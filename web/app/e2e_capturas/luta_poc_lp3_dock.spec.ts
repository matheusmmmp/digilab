/* As capturas do dock da luta da POC (LP3; decisao do Matheus de 2026-11-09: os mesmos botoes da tela de antes): a luta montada no nucleo,
   no desktop (1920 x 950) e no celular (390 x 844, 3 px por px de CSS), nas duas peles, com o dock em cada estado: lutando, pausado, x2,
   a confirmacao do Desistir, o resultado com Ver replay, o replay com Sair do replay e o fim do replay com Ver de novo.
   Roda com: npx playwright test -c e2e_capturas/luta_poc_lp3.config.ts luta_poc_lp3_dock, com DIGILAB_CAPTURAS_LP3=<pasta>. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_LP3 ?? "";
const CHAVE = "digilab-web-v21-sprites";
const TELAS = [{ nome: "1920", w: 1920, h: 950, dpr: 1 }, { nome: "390", w: 390, h: 844, dpr: 3 }];
const PELES = (process.env.DIGILAB_LP3_PELES ?? "vidro,militar").split(",");

async function semear(page: Page): Promise<void> {
  await page.goto("/motor/index.ts");
  await page.evaluate((chave) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-descarte", "8");
    localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
  }, CHAVE);
}

for (const t of TELAS) for (const pele of PELES) {
  test(`LP3 dock ${t.nome} ${pele}`, async ({ browser }) => {
    test.skip(!PASTA, "so com DIGILAB_CAPTURAS_LP3");
    const dir = join(PASTA, "dock"); mkdirSync(dir, { recursive: true });
    const ctx = await browser.newContext({ viewport: { width: t.w, height: t.h }, deviceScaleFactor: t.dpr });
    const page = await ctx.newPage();
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(String(e)));
    const foto = (n: string) => page.screenshot({ path: join(dir, `dock_${t.nome}_${pele}_${n}.png`) });
    await semear(page);
    await page.goto(`/?luta_poc=1&pele=${pele}&palco_poc=floresta,cirro_crianca_arisco,brasa_crianca_sereno,101`);
    const dock = page.getByTestId("poc-dock"), dado = (k: string) => page.getByTestId("poc-canvas").evaluate((el, k) => (el as HTMLElement).dataset[k] ?? "", k);
    await expect(dock).toBeVisible();
    /* o atlas carregado (o retrato no HUD), senao a luta aparece com os marcadores: a luta fica pausada enquanto ele carrega */
    await dock.getByRole("button", { name: "Pausar a animação" }).click();
    await expect(page.locator(".hud-ret img").first()).toBeVisible({ timeout: 120_000 });
    await dock.getByRole("button", { name: "Continuar a animação" }).click();
    await expect.poll(async () => +(await dado("passo")) > 150 && +(await dado("projeteisDesenho")) + +(await dado("nossos")) > 0, { timeout: 60_000 }).toBe(true);
    await foto("1_lutando");
    await dock.getByRole("button", { name: "Pausar a animação" }).click();
    await page.waitForTimeout(300); await foto("2_pausado");
    await dock.getByRole("button", { name: "Continuar a animação" }).click();
    await dock.getByRole("button", { name: "Velocidade dobrada" }).click();
    await page.waitForTimeout(600); await foto("3_x2");
    await dock.getByRole("button", { name: "Desistir" }).click();
    await expect(page.getByTestId("poc-desistir-conf")).toBeVisible();
    await page.waitForTimeout(300); await foto("4_desistir");
    await page.getByTestId("poc-desistir-conf").getByRole("button", { name: "Continuar vendo" }).click();
    await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 120_000 });
    await page.waitForTimeout(400); await foto("5_resultado");
    await page.getByTestId("poc-ver-replay").click();
    await expect(dock.getByRole("button", { name: "Sair do replay" })).toBeVisible();
    await expect.poll(async () => +(await dado("passo")) > 200, { timeout: 60_000 }).toBe(true);
    await foto("6_replay");
    await dock.getByRole("button", { name: "Velocidade dobrada" }).click();
    await expect(page.getByTestId("poc-resultado")).toContainText("Fim do replay", { timeout: 120_000 });
    await page.waitForTimeout(400); await foto("7_fim_replay");
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
