/* DC3d da CONVERSA_PET: a "Fala com conteudo (teste)" no laboratorio. Desligada por padrao; ligada, o ovo de teste chocado ganha a marca "fu" no
   registro (o modular com a `fala_unidades`) e a tela diz isso. Desligada, o ovo de teste e o de hoje. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(chave => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave + "-lab-ligado", "1");
  }, CHAVE);
}
const guardado = (page: Page, chave: string) => page.evaluate(k => localStorage.getItem(k), chave);
const marcas = async (page: Page) => (JSON.parse((await guardado(page, CHAVE + "-lab"))!).log as [number, string][]).filter(e => e[1] === "fu").length;

test("a fala com conteudo: desligada por padrao; ligada, o ovo de teste nasce com a marca \"fu\" e a tela diz isso", async ({ page }) => {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
  await semear(page);
  await page.goto(APP + "#/config/laboratorio");
  const chave = page.getByRole("switch", { name: /Fala com conteúdo/ });
  await expect(page.getByText("Fala com conteúdo (teste) · desligada")).toBeVisible();
  await expect(chave).not.toBeChecked();
  await page.getByRole("button", { name: "Chocar o ovo de teste" }).click();
  await expect(page.getByText("cérebro modular · versão 16", { exact: true })).toBeVisible();
  expect(await marcas(page)).toBe(0);

  /* descartar e chocar outro com a chave ligada */
  await page.getByRole("button", { name: "Descartar", exact: true }).click();
  await page.getByRole("alertdialog").getByRole("button", { name: "Descartar" }).click();
  await chave.check();
  await expect(page.getByText("Fala com conteúdo (teste) · ligada")).toBeVisible();
  expect(await guardado(page, CHAVE + "-lab-fala")).toBe("1");
  await page.screenshot({ path: test.info().outputPath("lab_fala_ligada.png"), fullPage: false });
  await page.getByRole("button", { name: "Chocar o ovo de teste" }).click();
  await expect(page.getByText("cérebro modular · versão 16 · fala com conteúdo")).toBeVisible();
  expect(await marcas(page)).toBe(1);
  await page.screenshot({ path: test.info().outputPath("lab_fala_pet.png"), fullPage: false });
  expect(erros).toEqual([]);
});
