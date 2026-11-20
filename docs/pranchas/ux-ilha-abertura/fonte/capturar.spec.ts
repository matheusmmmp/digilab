/* Copiado para web/app/e2e_capturas/abertura.spec.ts so na hora de rodar (playwright.capturas.config.ts) e apagado depois: as capturas da
   prancha da camera do primeiro dia (docs/pranchas/ux-ilha-abertura/). Vem do capturar.spec.ts da luz: o mesmo save (o dia), o relogio
   parado, a pele Vidro e o mapa Ilha. Por proposta (CAP_ABERTURA: a, b ou c, ou todas sem a variavel):
   - os quadros: o tempo da abertura parado em seis pontos (window.__abertura.em), de 0 ao fim;
   - o video (so a 1920 x 950): o tempo parado a cada 1/15 s, do 0 ao fim e mais 1 s, um PNG por passo em video_<p>/; o ffmpeg junta
     (o LEIA.md diz como). A gravacao do Playwright nao serviu: o corte no tempo da abertura nao saia no lugar.
   A pasta: D:\Trab\digilab\capturas_ux_ilha_abertura\. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, unknown> = JSON.parse(readFileSync(new URL("./saves_bola.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAIDA = "D:\\Trab\\digilab\\capturas_ux_ilha_abertura";
const PROPOSTAS = (process.env.CAP_ABERTURA ?? "a,b,c").split(",");
const FRACOES = [0, 0.2, 0.4, 0.6, 0.8, 1];

for (const p of PROPOSTAS) for (const [w, h] of [[1920, 950], [390, 844]] as const) {
  test(`abertura ${p} ${w}`, async ({ browser }) => {
    test.setTimeout(600_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1, colorScheme: "light" });
    await ctx.addInitScript(() => {
      const orig = window.setInterval.bind(window);
      (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
    });
    const page: Page = await ctx.newPage();
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(e.message));
    await page.goto("/Assets/digilab_atlas_up.json");
    await page.evaluate(([chave, s]) => {
      localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
      localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
      localStorage.setItem(chave, s);
    }, [CHAVE, JSON.stringify(SAVES.dia)] as const);
    await page.goto(APP + `?abertura=${p}&mapa=ilha&pele=vidro#/pet`);
    await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
    await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
    await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 30_000 });
    await page.mouse.move(2, h - 2);
    const dur: number = await page.evaluate(() => (window as any).__abertura.duracao);
    mkdirSync(SAIDA, { recursive: true });
    await page.waitForTimeout(4000);
    for (const f of FRACOES) {
      await page.evaluate(t => (window as any).__abertura.em(t), Math.round(dur * f));
      await page.waitForTimeout(700);
      await page.screenshot({ path: join(SAIDA, `${p}_${Math.round(f * 100)}_${w}.png`) });
    }
    if (w === 1920) {
      const pasta = join(SAIDA, `video_${p}`);
      mkdirSync(pasta, { recursive: true });
      for (let i = 0, t = 0; t <= dur + 1000; i++, t = Math.round((i * 1000) / 15)) {
        await page.evaluate(x => (window as any).__abertura.em(x), t);
        await page.waitForTimeout(60);
        await page.screenshot({ path: join(pasta, `${String(i).padStart(4, "0")}.png`) });
      }
    }
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
