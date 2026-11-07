/* As capturas do conserto dos Cenarios do Lab (2026-11-07), em 390 e 1280 px: a aba com o cenario "Controle da pesquisa" montado (a
   mensagem e a tabela lado a lado), as 100 lutas A x B e a luta em tempo real contra o rival fixo na Arena. Confere no caminho que o pet A
   e da versao de hoje e que a luta abre. Roda com: npx playwright test -c e2e_capturas/lab_cenarios.config.ts, com
   DIGILAB_CAPTURAS_LAB=<pasta>. */
import { expect, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_LAB ?? "";
const CHAVE = "digilab-web-v21-sprites";
const VERSAO_PET = 19;

test.describe("capturas dos Cenarios", () => {
  test.skip(!PASTA, "so com DIGILAB_CAPTURAS_LAB");
  for (const [w, h] of [[390, 844], [1280, 800]] as const) test(`cenarios ${w}`, async ({ page }) => {
    mkdirSync(PASTA, { recursive: true });
    await page.setViewportSize({ width: w, height: h });
    /* o save e semeado por uma pagina da mesma origem que nao e o app (o app gravaria o pet dele por cima ao fechar) */
    await page.goto("/motor/index.ts");
    await page.evaluate(([chave, v]) => {
      localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-descarte", "6");
      localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
      localStorage.setItem(chave, JSON.stringify({ semente: 101, versao: v, log: [[480, "u", { n: 1 }], [480, "t", 210]] }));
    }, [CHAVE, VERSAO_PET] as const);
    await page.goto("/#/diario/cenarios");
    await page.locator("details.dl-apoio > summary").click();
    await page.locator("button.cen", { hasText: "Controle da pesquisa" }).click();
    await expect(page.locator("p.resultado").first()).toHaveText(/Controle da pesquisa · semente 1\. O pet A agora é o seu\./);
    await expect(page.locator("table.comp")).toBeVisible();
    const versao = await page.evaluate((c) => JSON.parse(localStorage.getItem(c)!).versao, CHAVE);
    expect(versao).toBe(VERSAO_PET);
    await page.locator("p.resultado").first().scrollIntoViewIfNeeded();
    await page.screenshot({ path: join(PASTA, `cenarios_montado_${w}.png`) });
    await page.getByRole("button", { name: "Rodar 100 lutas A × B" }).click();
    const res = page.locator("p.resultado", { hasText: "100 lutas" });
    await expect(res).toBeVisible();
    await res.scrollIntoViewIfNeeded();
    await page.screenshot({ path: join(PASTA, `cenarios_100lutas_${w}.png`) });
    /* a luta em tempo real contra o rival fixo, pela Arena (sem recarregar: o rival fixo fica so na memoria) */
    await page.evaluate(() => { location.hash = "#/lutar/arena"; });
    await page.locator(".lutar-grande").click();
    await expect(page).toHaveURL(/#\/lutar\/luta$/);
    await expect(page.getByText("Arena · Cenário", { exact: false })).toBeVisible();
    await page.waitForTimeout(2500);
    await page.screenshot({ path: join(PASTA, `cenarios_luta_${w}.png`) });
  });
});
