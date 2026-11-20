/* Copiado para web/app/e2e_capturas/ so na hora de rodar (playwright.capturas.config.ts) e apagado depois: as capturas do codigo da ilha A (ObjetosDaIlha.tsx) nos estados da prancha, a 1920 e a 390, nas duas peles.
   Saem em D:\Trab\digilab\capturas_ux_ilha_aprovar\codigo_a\. Os saves sao os da prancha (docs/pranchas/ux-ilha-a/fonte/). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync } from "node:fs";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = fileURLToPath(new URL("../../..", import.meta.url));
const PREFIXO = "/" + basename(RAIZ);
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const OUT = "D:/Trab/digilab/capturas_ux_ilha_aprovar/codigo_a";
const ler = (n: string) => JSON.parse(readFileSync(`${RAIZ}/docs/pranchas/ux-ilha-a/fonte/${n}`, "utf8"));
const DIA = ler("save_dia.json"), NOITE = ler("save_noite.json");
const ESTADOS = (process.env.CAP_ESTADOS ?? "nada_tocado,etiqueta_aberta,toque_bola,segurar_pet,indo_tigela").split(",");

async function abrir(page: Page, save: unknown, pele: string): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(save)] as const);
  await page.goto(APP + `?pele=${pele}#/pet/estado`);
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
}
const tela = (page: Page, nome: string) => page.evaluate(n => {
  const d = (window as any).__digilab, m = d.mundo();
  const p = n === "tigela" ? m.comedouro : m.bola;
  const c = document.querySelector(".pet-cena")!.getBoundingClientRect(), r = d.cenaPara(p[0], p[1]);
  return [c.x + r[0], c.y + r[1]] as [number, number];
}, nome);

for (const pele of ["vidro", "xcom"]) for (const larg of [1920, 390]) {
  const nomePele = pele === "xcom" ? "militar" : "vidro";
  test(`codigo ilha A ${pele} ${larg}`, async ({ browser }) => {
    test.setTimeout(240_000);
    mkdirSync(OUT, { recursive: true });
    const novo = async () => {
      const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: larg, height: larg >= 1100 ? 950 : 844 }, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      const erros: string[] = [];
      page.on("pageerror", e => erros.push(e.message));
      return { ctx, page, erros };
    };
    const arq = (e: string) => `${OUT}/ilha_a_${e}_${larg}_${nomePele}.png`;
    if (ESTADOS.some(e => ["nada_tocado", "etiqueta_aberta", "toque_bola"].includes(e))) {
      const { ctx, page, erros } = await novo();
      await abrir(page, DIA, pele);
      await page.waitForTimeout(4000);
      await page.mouse.move(5, larg >= 1100 ? 600 : 600);
      await page.waitForTimeout(300);
      if (ESTADOS.includes("nada_tocado")) await page.screenshot({ path: arq("nada_tocado") });
      if (ESTADOS.includes("etiqueta_aberta")) {
        const [x, y] = await tela(page, "tigela");
        await page.mouse.click(x, y - (larg >= 1100 ? 14 : 6));
        await expect(page.locator("[data-cartao][data-objeto=tigela]")).toBeVisible();
        if (larg >= 1100) { const [bx, by] = await tela(page, "bola"); await page.mouse.move(bx, by - 30); }
        await page.waitForTimeout(400);
        await page.screenshot({ path: arq("etiqueta_aberta") });
        await page.keyboard.press("Escape");
      }
      if (ESTADOS.includes("toque_bola")) {
        const [bx, by] = await tela(page, "bola");
        await page.mouse.click(bx, by - (larg >= 1100 ? 30 : 12));
        await expect(page.locator("[data-cartao][data-objeto=bola]")).toBeVisible();
        await page.mouse.move(5, 600);
        await page.waitForTimeout(400);
        await page.screenshot({ path: arq("toque_bola") });
      }
      expect(erros).toEqual([]);
      await ctx.close();
    }
    if (ESTADOS.includes("segurar_pet")) {
      const { ctx, page, erros } = await novo();
      await abrir(page, DIA, pele);
      await page.waitForTimeout(300);
      const c = await page.evaluate(() => (window as any).__digilab.cena());
      const cena = (await page.locator(".pet-cena").boundingBox())!;
      const px = cena.x + c.ret.x + c.ret.w / 2, py = cena.y + c.ret.y + c.ret.h * 0.6, [dx, dy] = larg >= 1100 ? [230, -150] : [70, -80];
      await page.mouse.move(px, py); await page.mouse.down();
      await page.mouse.move(px + dx, py + dy, { steps: 20 });
      await page.waitForTimeout(500);
      expect(await page.evaluate(() => (window as any).__digilab.petNaMao())).toBe(true);
      await page.screenshot({ path: arq("segurar_pet") });
      await page.mouse.up();
      expect(erros).toEqual([]);
      await ctx.close();
    }
    if (ESTADOS.includes("indo_tigela")) {
      const { ctx, page, erros } = await novo();
      await abrir(page, NOITE, pele);
      await page.mouse.move(5, 600);
      await expect(page.locator("[data-objeto=tigela].obj-etq--alvo")).toBeVisible({ timeout: 60_000 });
      await page.waitForTimeout(250);
      await page.screenshot({ path: arq("indo_tigela") });
      expect(erros).toEqual([]);
      await ctx.close();
    }
  });
}
