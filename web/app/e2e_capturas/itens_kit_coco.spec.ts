/* As capturas do kit medico e do coco na ilha (docs/TAREFA_V3_ITENS_3D.md, secao 13): os procedurais de antes ("referencia") e os
   gerados ("gerada"). So roda com DIGILAB_CAPTURAS_ITENS=1 e grava fora do git (o pet e um sprite do UP), em DIGILAB_CAPTURAS_ITENS_PASTA
   (padrao: D:\Trab\digilab\capturas_itens3d\kit_coco\<rotulo>\, com DIGILAB_CAPTURAS_ITENS_ROTULO).
   Os saves (saves_kit_coco.json, de gerar_saves_kit_coco.mjs): "coco", com 3 cocos no chao, e "kit", com o pet lesionado (o kit ao lado
   do ninho); o relogio do jogo fica parado. Por save, largura (390 e 1280) e cena (claro e escuro): a tela inteira e a M3 do jogo
   (?medir3d=1, 10 s), para os draw calls (G9). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_kit_coco.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const ROTULO = process.env.DIGILAB_CAPTURAS_ITENS_ROTULO ?? "referencia";
const SAIDA = process.env.DIGILAB_CAPTURAS_ITENS_PASTA ?? join("D:\\Trab\\digilab\\capturas_itens3d\\kit_coco", ROTULO);
const TELAS: [number, number][] = [[390, 844], [1280, 800]];
const CENAS: { nome: string; esquema: "light" | "dark" }[] = [{ nome: "claro", esquema: "light" }, { nome: "escuro", esquema: "dark" }];
test.skip(!process.env.DIGILAB_CAPTURAS_ITENS, "so com DIGILAB_CAPTURAS_ITENS=1");

for (const save of ["kit", "coco"]) for (const [w, h] of TELAS) for (const cena of CENAS) {
  test(`captura: o ${save} (${ROTULO}) em ${w} px, ${cena.nome}`, async ({ browser }) => {
    test.setTimeout(90_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1, colorScheme: cena.esquema });
    /* o relogio do jogo parado (src/tempo.ts, o unico setInterval de 100 ms), como na captura da bola */
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
    }, [CHAVE, JSON.stringify(SAVES[save])] as const);
    await page.goto(APP + "?medir3d=1#/pet");
    await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
    await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
    await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 30_000 });
    await page.waitForTimeout(1500);
    mkdirSync(SAIDA, { recursive: true });
    const nome = `${save}_${w}_${cena.nome}`;
    await page.screenshot({ path: join(SAIDA, `${nome}.png`) });
    await page.getByRole("button", { name: /Medir 10 s/ }).evaluate(b => (b as HTMLButtonElement).click());
    const txt = page.getByLabel("Medida M3");
    await expect(txt).toHaveValue(/draw_calls/, { timeout: 30_000 });
    writeFileSync(join(SAIDA, `${nome}_m3.json`), JSON.stringify({ save, esquema: cena.esquema, rotulo: ROTULO, m3: JSON.parse(await txt.inputValue()) }, null, 1) + "\n");
    await ctx.close();
  });
}
