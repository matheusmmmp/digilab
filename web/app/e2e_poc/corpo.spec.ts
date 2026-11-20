/* O e2e do WORLD-POC-02 (docs/TAREFA_V2_WORLD_POC_02.md):
     E2  o G-DET com o corpo no Chrome: o mesmo hash do estado, com o corpo químico ligado, no Chrome e no Node;
     E3  a M-CORPO: o painel dos receptores na página acompanha o corpo, e some com ?corpo=0 (o POC-01a).
   As medidas vão para artifacts_v2_world_poc/poc02_e2e.json e o screenshot para poc02_painel.png (as do POC-01a não mudam). */
import { expect, test } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { Simulacao } from "../poc/mundo3d/simulacao.ts";

const ARTEFATOS = fileURLToPath(new URL("../../../artifacts_v2_world_poc/", import.meta.url));
const medidas: Record<string, unknown> = {};

test.describe.configure({ mode: "serial" });
test.afterAll(() => {
  mkdirSync(ARTEFATOS, { recursive: true });
  writeFileSync(ARTEFATOS + "poc02_e2e.json", JSON.stringify(medidas, null, 1) + "\n");
});
declare global {
  interface Window {
    __poc: {
      hashDe(semente: number, ticks: number, corpo?: boolean): string; pausar(): void; comCorpo: boolean;
      receptores(): Record<string, number> | null; painel(): Record<string, number>;
    };
  }
}

test("G-DET com o corpo: o mesmo hash no Chrome e no Node", async ({ page }) => {
  await page.goto("/mundo3d.html?sprite=reserva");
  await expect(page.locator("#estado")).toHaveText("pronto");
  const casos: [number, number][] = [[101, 3000], [202, 3000], [303, 4500]];
  const res = [];
  for (const [semente, ticks] of casos) {
    const chrome = await page.evaluate(([s, t]) => window.__poc.hashDe(s, t, true), [semente, ticks]);
    const node = new Simulacao(semente, undefined, { corpo: true });
    node.avancar(ticks);
    expect(chrome, `semente ${semente}`).toBe(node.hash());
    res.push({ semente, ticks, corpo: true, hash: chrome });
  }
  medidas.G_DET_corpo_chrome_node = res;
});

test("M-CORPO: o painel dos receptores acompanha o corpo da página", async ({ page }) => {
  await page.goto("/mundo3d.html?sprite=reserva");
  await expect(page.locator("#estado")).toHaveText("pronto");
  await page.waitForTimeout(1500);                            // o pet anda uns ticks
  await page.evaluate(() => window.__poc.pausar());
  await page.waitForTimeout(300);                             // um quadro, pelo menos, depois da pausa
  const r = await page.evaluate(() => ({ comCorpo: window.__poc.comCorpo, receptores: window.__poc.receptores(), painel: window.__poc.painel() }));
  expect(r.comCorpo).toBe(true);
  expect(r.receptores).not.toBeNull();
  expect(Object.keys(r.painel).sort()).toEqual(Object.keys(r.receptores!).sort());
  expect(r.painel).toEqual(r.receptores);
  await expect(page.locator("#corpo")).toBeVisible();
  await page.locator("main").screenshot({ path: ARTEFATOS + "poc02_painel.png" });
  medidas.M_CORPO = { ...r, screenshot: "artifacts_v2_world_poc/poc02_painel.png" };
});

test("com ?corpo=0, a página é a do POC-01a: sem o corpo e sem o painel", async ({ page }) => {
  await page.goto("/mundo3d.html?sprite=reserva&corpo=0");
  await expect(page.locator("#estado")).toHaveText("pronto");
  expect(await page.evaluate(() => [window.__poc.comCorpo, window.__poc.receptores()])).toEqual([false, null]);
  await expect(page.locator("#corpo")).toBeHidden();
});
