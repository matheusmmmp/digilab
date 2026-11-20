/* A captura de referencia da bola na ilha (docs/TAREFA_V3_ITENS_3D.md, secao 7): a bola procedural de hoje, para o par lado a lado com a
   bola gerada. So roda com DIGILAB_CAPTURAS_ITENS=1 e grava fora do git (o pet e um sprite do UP), em DIGILAB_CAPTURAS_ITENS_PASTA (padrao:
   D:\Trab\digilab\capturas_itens3d\bola\<rotulo>\, com DIGILAB_CAPTURAS_ITENS_ROTULO = "referencia" ou "gerada").
   Os saves (saves_bola.json, de gerar_saves_bola.mjs) tem a bola 2 celulas a leste do pet; o relogio do jogo fica parado, entao o pet e a
   bola nao andam. Por largura (390 e 1280) e por cena (claro, escuro e noite): a tela inteira, um recorte em volta da bola e a M3 do jogo
   (?medir3d=1, 10 s) num JSON. O draw_calls da M3 vale (G9); o fps do Chrome sem janela nao e o do jogo e fica so registrado. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_bola.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const ROTULO = process.env.DIGILAB_CAPTURAS_ITENS_ROTULO ?? "referencia";
const SAIDA = process.env.DIGILAB_CAPTURAS_ITENS_PASTA ?? join("D:\\Trab\\digilab\\capturas_itens3d\\bola", ROTULO);
const TELAS: [number, number][] = [[390, 844], [1280, 800]];
const CENAS: { nome: string; save: string; esquema: "light" | "dark" }[] = [
  { nome: "claro", save: "dia", esquema: "light" }, { nome: "escuro", save: "dia", esquema: "dark" }, { nome: "noite", save: "noite", esquema: "light" },
];
test.skip(!process.env.DIGILAB_CAPTURAS_ITENS, "so com DIGILAB_CAPTURAS_ITENS=1");

for (const [w, h] of TELAS) {
  for (const cena of CENAS) {
    test(`captura: a bola (${ROTULO}) em ${w} px, ${cena.nome}`, async ({ browser }) => {
      test.setTimeout(90_000);
      const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1, colorScheme: cena.esquema });
      /* o relogio do jogo parado (src/tempo.ts, o unico setInterval de 100 ms), como em sprites_comer.spec.ts */
      await ctx.addInitScript(() => {
        const orig = window.setInterval.bind(window);
        (window as any).setInterval = ((fn: TimerHandler, ms?: number, ...r: unknown[]) => ms === 100 ? 0 : orig(fn, ms, ...r)) as typeof setInterval;
      });
      const page: Page = await ctx.newPage();
      await page.goto("/Assets/digilab_atlas_up.json");
      await page.evaluate(([chave, s]) => {
        localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", JSON.stringify({ versao: 1, log: [] }));
        localStorage.setItem(chave + "-descarte", "8"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
        localStorage.setItem(chave, s);
      }, [CHAVE, JSON.stringify(SAVES[cena.save])] as const);
      await page.goto(APP + "?medir3d=1#/pet");
      await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
      await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
      await expect.poll(() => page.evaluate(() => (window as any).__digilab.cena()?.bola ?? null), { timeout: 30_000, message: "a bola desenhada" }).not.toBeNull();
      /* os kits e os itens carregados (vista.ts, data-objetos); a referencia de 2026-11-05 foi tirada antes deste marco, com a bola
         procedural, que nao dependia de carga */
      if (ROTULO !== "referencia") await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 30_000 });
      await page.waitForTimeout(1500);
      mkdirSync(SAIDA, { recursive: true });
      const nome = `bola_${w}_${cena.nome}`;
      await page.screenshot({ path: join(SAIDA, `${nome}.png`) });
      /* o recorte em volta da bola: a bola na tela (cenaPara, subunidades) com 120 px de folga */
      const b = await page.evaluate(() => { const d = (window as any).__digilab, c = d.cena(); return c?.bola ? d.cenaPara(c.bola[0], c.bola[1]) : null; }) as [number, number] | null;
      if (!b) throw new Error("a bola nao tem lugar na tela");
      const caixa = (await page.locator(".pet-cena").boundingBox())!, F = 120;
      const x = Math.max(0, caixa.x + b[0] - F), y = Math.max(0, caixa.y + b[1] - F);
      await page.screenshot({ path: join(SAIDA, `${nome}_recorte.png`), clip: { x, y, width: Math.min(2 * F, w - x), height: Math.min(2 * F, h - y) } });
      /* a M3 do jogo (CenarioPet.tsx, MedirCena): o botao mede 10 s e mostra o JSON */
      /* o botao fica sob a barra de acoes do pet: o clique vai pelo DOM, sem mexer na tela da captura */
      await page.getByRole("button", { name: /Medir 10 s/ }).evaluate(b => (b as HTMLButtonElement).click());
      const txt = page.getByLabel("Medida M3");
      await expect(txt).toHaveValue(/draw_calls/, { timeout: 30_000 });
      const m3 = JSON.parse(await txt.inputValue());
      writeFileSync(join(SAIDA, `${nome}_m3.json`), JSON.stringify({ save: cena.save, esquema: cena.esquema, rotulo: ROTULO, bola_tela: b, m3 }, null, 1) + "\n");
      await ctx.close();
    });
  }
}
