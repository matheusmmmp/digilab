/* As capturas do Emburrar na ilha com o atlas de clipes de verdade (docs/TAREFA_V3_SPRITES_ACOES.md, M3, Emburrar), para o Matheus aprovar. So roda com
   DIGILAB_CAPTURAS_EMBURRAR=1 e grava fora do git (sao quadros do UP), em DIGILAB_CAPTURAS_EMBURRAR_PASTA (padrao: D:\Trab\digilab\remaster\acoes\capturas\emburrar\).
   O pet e o do save "emburrar" (saves_cena.json), com o relogio do jogo parado: o motor fica na acao "emburrar" e a ilha toca o clipe em laco.
   Para ver o clipe de outro Digimon no mesmo pet, a rota troca, so nesta captura, o sprite de todas as formas do atlas de clipes pelo dele
   (o atlas no disco nao muda). Por Digimon e largura: a tela inteira e uma sequencia de recortes em volta do pet, um a cada ~110 ms. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_cena.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const SAIDA = process.env.DIGILAB_CAPTURAS_EMBURRAR_PASTA ?? "D:\\Trab\\digilab\\remaster\\acoes\\capturas\\emburrar";
const ATLAS_CLIPES = join(REPO, "..", "Assets", "digilab_atlas_up_clipes.json");
const TELAS: [number, number][] = [[390, 844], [1280, 800]];
/* o Gabumon (a forma do pet do save: a troca nao muda nada), o Agumon (a prova da M1) e dois da lista dos duvidosos da M1. Com a troca, a
   plaquinha do topo tambem mostra o Digimon trocado (ela le o mesmo atlas), com o nome do pet de verdade */
const DIGIMON = ["Agumon"];
const RECORTES = 8;
test.skip(!process.env.DIGILAB_CAPTURAS_EMBURRAR, "so com DIGILAB_CAPTURAS_EMBURRAR=1");

type SpriteClipes = { digimon: string; clipes: Record<string, unknown> };
const ehForma = (k: string) => !k.startsWith("npc_") && !k.startsWith("bot_");

for (const [w, h] of TELAS) {
  for (const digimon of DIGIMON) {
    test(`captura: o Emburrar do ${digimon} em ${w} px`, async ({ browser }) => {
      test.setTimeout(120_000);
      const real = JSON.parse(readFileSync(ATLAS_CLIPES, "utf8")) as { sprites: Record<string, SpriteClipes> };
      const alvo = Object.values(real.sprites).find(s => s.digimon === digimon);
      if (!alvo) throw new Error("Digimon fora do atlas de clipes: " + digimon);
      if (!alvo.clipes.Emburrar) throw new Error("o atlas de clipes nao tem o Emburrar do " + digimon);
      const trocado = { ...real, sprites: Object.fromEntries(Object.entries(real.sprites).map(([k, s]) => [k, ehForma(k) ? alvo : s])) };
      const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1 });
      await ctx.route(/\/Assets\/digilab_atlas_up_clipes\.json/, r => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(trocado) }));
      /* o relogio do jogo parado (src/tempo.ts, o unico setInterval de 100 ms): o motor fica na acao "emburrar" */
      await ctx.addInitScript(() => {
        const orig = window.setInterval.bind(window);
        (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
      });
      const page: Page = await ctx.newPage();
      await page.goto("/Assets/digilab_atlas_up.json");
      await page.evaluate(([chave, s]) => {
        localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
        localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
        localStorage.setItem(chave, s);
      }, [CHAVE, JSON.stringify(SAVES.emburrar)] as const);
      await page.goto(APP + "#/pet/estado");
      await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
      await expect.poll(() => page.evaluate(() => (window as any).__digilab.emburrar()), { timeout: 30_000, message: "o clipe Emburrar no corpo" }).toBe(true);
      await page.waitForTimeout(600);
      mkdirSync(SAIDA, { recursive: true });
      const nome = `${digimon}_${w}`;
      await page.screenshot({ path: join(SAIDA, `${nome}.png`) });
      /* os recortes em volta do pet: o retangulo que a vista informa, com folga para a comida e para o corte alargado */
      const ret = await page.evaluate(() => (window as any).__digilab.cena().ret as { x: number; y: number; w: number; h: number });
      const cena = (await page.locator(".pet-cena").boundingBox())!, folga = Math.max(ret.w, ret.h) * 0.6;
      const clip = { x: Math.max(0, cena.x + ret.x - folga), y: Math.max(0, cena.y + ret.y - folga), width: ret.w + 2 * folga, height: ret.h + 2 * folga };
      for (let i = 0; i < RECORTES; i++) {
        expect(await page.evaluate(() => (window as any).__digilab.emburrar())).toBe(true);
        await page.screenshot({ path: join(SAIDA, `${nome}_recorte_${i + 1}.png`), clip, scale: "css" });
        await page.waitForTimeout(110);
      }
      writeFileSync(join(SAIDA, `${nome}.txt`), `o pet do save "emburrar" (saves_cena.json) com o clipe Emburrar do ${digimon} em todas as formas; ${w} x ${h} px; relogio parado\n`);
      await ctx.close();
    });
  }
}
