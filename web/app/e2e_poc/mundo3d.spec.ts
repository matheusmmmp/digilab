/* O e2e do WORLD-POC-01a (docs/TAREFA_V2_WORLD_POC_01.md, etapas E3 e E4), no Chrome instalado, sobre o build da página:
     M1  a página abre, o WebGL existe e desenha a sala (o screenshot vai para o artefato);
     M2  os pixels do sprite batem com os texels, na escala inteira, nos quatro cantos da sala;
     a oclusão: o pet atrás do obstáculo alto fica coberto pelo obstáculo semitransparente (o screenshot vai para o artefato);
     M3  os quadros por segundo do desktop, em headless (só descritivo; o celular é medido pelo Matheus);
     M5  o mesmo hash do estado no Chrome e no Node (a segunda metade; a primeira está no Vitest).
   As medidas vão para artifacts_v2_world_poc/e2e.json; o sprite é o de reserva (o build não tem o atlas, W-6). */
import { expect, test } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { centroDaCelula } from "../poc/mundo3d/mundo.ts";
import { Simulacao } from "../poc/mundo3d/simulacao.ts";
import { SPRITE_RESERVA } from "../poc/mundo3d/sprite_reserva.ts";

const ARTEFATOS = fileURLToPath(new URL("../../../artifacts_v2_world_poc/", import.meta.url));
const medidas: Record<string, unknown> = {};

type Poc = {
  sprite: string; webgl: boolean;
  colocarPet(x: number, y: number): unknown;
  conferirM2(): { conferidos: number; divergentes: number; texels_opacos: number; retangulo: { pxPorTexel: number }; pxPorSub: number;
    cobrindo: number };
  pixelsDiferentesDoFundo(): { diferentes: number; total: number };
  medirFps(): Promise<Record<string, unknown>>;
  hashDe(semente: number, ticks: number): string;
};
declare global { interface Window { __poc: Poc } }

test.describe.configure({ mode: "serial" });

test.beforeEach(async ({ page }) => {
  await page.goto("/mundo3d.html?sprite=reserva");
  await expect(page.locator("#estado")).toHaveText("pronto");
});

test.afterAll(() => {
  mkdirSync(ARTEFATOS, { recursive: true });
  writeFileSync(ARTEFATOS + "e2e.json", JSON.stringify(medidas, null, 1) + "\n");
});

test("M1: a página abre, o WebGL desenha a sala", async ({ page }) => {
  const r = await page.evaluate(() => ({ webgl: window.__poc.webgl, sprite: window.__poc.sprite, ...window.__poc.pixelsDiferentesDoFundo() }));
  expect(r.webgl).toBe(true);
  expect(r.sprite).toBe("reserva");
  expect(r.diferentes / r.total).toBeGreaterThan(0.2);
  mkdirSync(ARTEFATOS, { recursive: true });
  await page.locator("#tela").screenshot({ path: ARTEFATOS + "m1_sala.png" });
  medidas.M1 = { ...r, fracao_desenhada: +(r.diferentes / r.total).toFixed(4), screenshot: "artifacts_v2_world_poc/m1_sala.png" };
});

test("M2: o sprite bate pixel a pixel com os texels, nos quatro cantos da sala", async ({ page }) => {
  const opacos = SPRITE_RESERVA.join("").replace(/\./g, "").length;
  const cantos: [number, number][] = [[2, 2], [13, 2], [2, 9], [13, 9]];
  const resultados = [];
  for (const c of cantos) {
    const [x, y] = centroDaCelula(...c);
    const r = await page.evaluate(([px, py]) => { window.__poc.colocarPet(px, py); return window.__poc.conferirM2(); }, [x, y]);
    expect(r.texels_opacos).toBe(opacos);
    expect(r.conferidos).toBe(opacos * r.retangulo.pxPorTexel ** 2);
    expect(r.divergentes, `canto ${c}`).toBe(0);
    expect(r.cobrindo).toBe(0);
    resultados.push({ celula: c, ...r });
  }
  medidas.M2 = resultados;
});

test("a oclusão: atrás do obstáculo alto, o pet fica coberto pelo obstáculo semitransparente", async ({ page }) => {
  const [x, y] = centroDaCelula(6, 2);      // logo atrás do obstáculo alto (células 5 e 6, linhas 3 a 6)
  const r = await page.evaluate(([px, py]) => { window.__poc.colocarPet(px, py); return window.__poc.conferirM2(); }, [x, y]);
  expect(r.cobrindo).toBe(1);                // o obstáculo alto, e só ele, fica semitransparente
  expect(r.divergentes).toBeGreaterThan(0);  // a parte coberta do sprite chega misturada com a cor do obstáculo
  expect(r.divergentes).toBeLessThan(r.conferidos);   // e a parte de cima, fora dele, continua igual aos texels
  await page.locator("#tela").screenshot({ path: ARTEFATOS + "oclusao.png" });
  medidas.oclusao = { celula: [6, 2], ...r, screenshot: "artifacts_v2_world_poc/oclusao.png" };
});

test("M3 (desktop, headless): os quadros por segundo, só descritivo", async ({ page }) => {
  const m = await page.evaluate(() => window.__poc.medirFps());
  expect(m.quadros as number).toBeGreaterThan(0);
  medidas.M3_desktop_headless = m;
});

test("M5: o mesmo hash do estado no Chrome e no Node", async ({ page }) => {
  const casos: [number, number][] = [[101, 1500], [202, 1500], [303, 3000]];
  const res = [];
  for (const [semente, ticks] of casos) {
    const chrome = await page.evaluate(([s, t]) => window.__poc.hashDe(s, t), [semente, ticks]);
    const s = new Simulacao(semente);
    s.avancar(ticks);
    expect(chrome, `semente ${semente}`).toBe(s.hash());
    res.push({ semente, ticks, hash: chrome });
  }
  medidas.M5_chrome_node = res;
});
