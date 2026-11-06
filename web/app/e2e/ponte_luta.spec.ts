/* PE0 da ponte da luta (docs/TAREFA_V3_PONTE_LUTA.md, 3.5): o pet de teste v16 e o v17 (modular e A) lutam no app: uma luta na Arena contra
   um bot e a Liga dos Lideres (a serie), e o replay do registro no app sai igual (a assinatura depois de recarregar). Os saves vem de
   e2e/gerar_save_ponte_luta.mjs. Nada da ponte (PE1 em diante) existe ainda: e a vida de hoje. */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAVES = JSON.parse(readFileSync(new URL("./save_ponte_luta.json", import.meta.url), "utf8")) as Record<string, { semente: number; versao: number; log: unknown[][] }>;
const TAMER_6 = { versao: 2, log: ["campina", "torre", "floresta", "cidadela", "lago", "espiral"].map((id, i) =>
  ["medalha", { id, n: i + 1, quando: 1 + i, pet: 1, forma: "Agumon", tick: 900 + i }]) };

async function semear(page: Page, chave: string): Promise<void> {
  const lab = chave === "v16";
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([k, s, t, lab]) => {
    localStorage.clear(); localStorage.setItem(k + "-boas-vindas", "1"); localStorage.setItem(k + "-tamer", t);
    localStorage.setItem(k + "-descarte", "6"); localStorage.setItem(k + "-dicas-ligadas", "0"); localStorage.setItem(k + "-guardados", "[]");
    localStorage.setItem(k + (lab ? "-lab" : ""), s);
    if (lab) localStorage.setItem(k + "-lab-ligado", "1");
  }, [CHAVE, JSON.stringify(SAVES[chave]), JSON.stringify(TAMER_6), lab] as const);
}
/** abre o pet: o ativo (v17) ou o de teste pelo laboratorio (v16) */
async function abrir(page: Page, chave: string, hash: string): Promise<void> {
  if (chave === "v16") {
    await page.goto(APP + "#/config/laboratorio");
    await page.getByRole("button", { name: "Abrir", exact: true }).click();
    await expect(page.locator(".topo-lab .lab-selo")).toBeVisible();
    await page.evaluate(h => { location.hash = h; }, hash);
  } else await page.goto(APP + hash);
}
const numLog = (page: Page, tipo: string) => page.evaluate(([t]) => JSON.parse((window as any).__digilab.registro()).log.filter((e: unknown[]) => e[1] === t).length, [tipo] as const);
const registro = (page: Page) => page.evaluate(() => (window as any).__digilab.registro() as string);

for (const chave of Object.keys(SAVES)) {
  test(`${chave}: luta na Arena e a Liga (a serie), e o replay do app sai igual`, async ({ page }) => {
    test.setTimeout(400_000);
    const erros: string[] = [];
    page.on("pageerror", e => erros.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$/.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
    await semear(page, chave);
    await abrir(page, chave, "#/lutar/arena");
    const versao = JSON.parse(await registro(page)).versao;
    expect(versao).toBe(SAVES[chave].versao);
    const l0 = await numLog(page, "l");
    /* a luta contra um bot, na Arena */
    await page.locator(".lutar-grande").click();
    await expect(page).toHaveURL(/#\/lutar\/luta$/);
    await expect(page.getByTestId("luta-relogio")).toHaveText(/^0:0[1-9]$/, { timeout: 15_000 });
    await page.getByRole("button", { name: "Velocidade dobrada" }).click();
    await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 150_000 });
    await page.keyboard.press("Escape");
    await expect(page).toHaveURL(/#\/lutar\/arena$/);
    expect(await numLog(page, "l")).toBe(l0 + 1);
    /* a serie: a Liga dos Lideres (a tentativa e um evento so, com as lutas dela) */
    await page.evaluate(() => { location.hash = "#/lutar/fronteira"; });
    const lutar = page.locator(".fr-lutar:not([disabled])");
    await expect(lutar).toContainText("Desafiar a Liga");
    await lutar.click();
    await expect(page.locator(".luta-liga")).toContainText("Liga dos Líderes · luta 1 de 6");
    await page.locator(".luta-ctl--x2").click();
    await expect(page.locator("dialog.modal-res[open]")).toBeVisible({ timeout: 250_000 });
    await page.locator(".res-continuar").click();
    expect(await numLog(page, "l")).toBe(l0 + 2);
    const reg = JSON.parse(await registro(page));
    const lutas = reg.log.filter((e: unknown[]) => e[1] === "l");
    expect(lutas[lutas.length - 1][2]).toEqual({ r: "liga", s: expect.any(Number) });
    /* o replay: o app recarrega o save e refaz as lutas (um registro que nao fecha o app recusa); o tempo segue andando, entao o registro de
       antes e o comeco do de agora, com as mesmas lutas (a assinatura bit a bit e do teste do motor, test/ponte_luta_pe0.test.ts) */
    const regAntes = reg.log as unknown[][];
    await page.waitForTimeout(500);                      // o app grava o save
    await abrir(page, chave, "#/pet/estado");
    const depois = JSON.parse(await registro(page)).log as unknown[][];
    expect(depois.slice(0, regAntes.length)).toEqual(regAntes);
    expect(depois.filter(e => e[1] === "l")).toEqual(regAntes.filter(e => e[1] === "l"));
    expect(await page.evaluate(() => (window as any).__digilab.assinatura() as string)).toContain(chave === "v16" ? '"lab"' : '"cb"');
    expect(erros).toEqual([]);
  });
}
