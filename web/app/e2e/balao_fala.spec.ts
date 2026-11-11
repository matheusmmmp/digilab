/* O caminho do balao da fala ate o painel "Por que ele disse isso" (docs/PAINEL_V3.md, secao 2.1; o balao e do PR #559). O save do teste
   (e2e/save_balao.json, gerado por e2e/gerar_save_balao.mjs) termina com um motivo registrado (treino com cansaco), entao o balao existe:
   tocar nele abre o painel "fala", e la a causa aparece (os icones, ou "?" quando o fator nao tem icone). So le a tela; nao muda a vida. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVE = JSON.parse(readFileSync(fileURLToPath(new URL("./save_balao.json", import.meta.url)), "utf8"));

async function semear(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE)] as const);
}

for (const largura of [390, 1280]) {
  test(`o balão da fala abre o "Por que ele disse isso" com a causa, em ${largura} px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: largura >= 1100 ? 800 : 844 });
    await semear(page);
    const erros: string[] = [];
    page.on("pageerror", e => erros.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
    await page.goto(APP + "#/pet/estado");
    const balao = page.locator(".cena-fala");
    await expect(balao).toBeVisible();
    await expect(balao).toContainText("toque para ver o porquê");
    await expect(page.locator("#pet-painel[data-painel-pet='fala']")).toHaveCount(0);
    await balao.click();
    const painel = page.locator("#pet-painel[data-painel-pet='fala']");
    await expect(painel).toBeVisible();
    await expect(painel.getByText("Por que ele disse isso").first()).toBeVisible();
    /* a causa: os icones, ou o "?" (o fator do treino cansado nao tem icone); em todo caso o rotulo acessivel diz qual */
    const causa = painel.locator(".causa-icones");
    await expect(causa).toBeVisible();
    await expect(causa).toHaveAttribute("aria-label", /^causa: .+/);
    await expect(causa.locator(".causa-ic, .balao-q").first()).toBeVisible();
    await expect(painel.locator(".fala-status")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator("#pet-painel")).toHaveCount(0);
    expect(erros).toEqual([]);
  });
}
