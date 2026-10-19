/* O e2e do WORLD-POC-02 (docs/TAREFA_V2_WORLD_POC_02.md, etapa E2): o G-DET com o corpo no Chrome. O mesmo hash do estado, com o corpo
   químico ligado, no Chrome e no Node. As medidas vão para artifacts_v2_world_poc/poc02_e2e.json (as do POC-01a não mudam). */
import { expect, test } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { Simulacao } from "../poc/mundo3d/simulacao.ts";

const ARTEFATOS = fileURLToPath(new URL("../../../artifacts_v2_world_poc/", import.meta.url));
declare global { interface Window { __poc: { hashDe(semente: number, ticks: number, corpo?: boolean): string } } }

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
  mkdirSync(ARTEFATOS, { recursive: true });
  writeFileSync(ARTEFATOS + "poc02_e2e.json", JSON.stringify({ G_DET_corpo_chrome_node: res }, null, 1) + "\n");
});
