/* As capturas dos enfeites na ilha (docs/TAREFA_V3_MUNDO_ENFEITES.md, E-G9 e E-G11): a ilha sem os enfeites ("referencia") e com eles
   ("enfeites"). So roda com DIGILAB_CAPTURAS_ENFEITES=1 e grava fora do git (o pet e um sprite do UP), em DIGILAB_CAPTURAS_ENFEITES_PASTA
   (padrao: D:\Trab\digilab\capturas_enfeites\<rotulo>\, com DIGILAB_CAPTURAS_ENFEITES_ROTULO). Os saves sao os da bola (saves_bola.json:
   o dia, 13:00, e a noite, 22:30), com o relogio parado. Por save, largura (390 e 1280) e cena: a tela inteira, uma volta da camera
   (a camera livre, a seta para a esquerda, para ver a moldura dos lados) e a M3 do jogo (?medir3d=1, 10 s). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_bola.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const ROTULO = process.env.DIGILAB_CAPTURAS_ENFEITES_ROTULO ?? "referencia";
const SAIDA = process.env.DIGILAB_CAPTURAS_ENFEITES_PASTA ?? join("D:\\Trab\\digilab\\capturas_enfeites", ROTULO);
const TELAS: [number, number][] = [[390, 844], [1280, 800]];
const CENAS: { nome: string; save: string; esquema: "light" | "dark" }[] = [{ nome: "claro", save: "dia", esquema: "light" }, { nome: "noite", save: "noite", esquema: "light" }];
test.skip(!process.env.DIGILAB_CAPTURAS_ENFEITES, "so com DIGILAB_CAPTURAS_ENFEITES=1");

for (const [w, h] of TELAS) for (const cena of CENAS) {
  test(`captura: os enfeites (${ROTULO}) em ${w} px, ${cena.nome}`, async ({ browser }) => {
    test.setTimeout(90_000);
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: w, height: h }, deviceScaleFactor: 1, colorScheme: cena.esquema });
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
    }, [CHAVE, JSON.stringify(SAVES[cena.save])] as const);
    await page.goto(APP + "?medir3d=1#/pet");
    await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
    await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
    await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 30_000 });
    await page.waitForTimeout(1500);
    mkdirSync(SAIDA, { recursive: true });
    const nome = `enfeites_${w}_${cena.nome}`;
    await page.screenshot({ path: join(SAIDA, `${nome}.png`) });
    await page.getByRole("button", { name: /Medir 10 s/ }).evaluate(b => (b as HTMLButtonElement).click());
    const txt = page.getByLabel("Medida M3");
    await expect(txt).toHaveValue(/draw_calls/, { timeout: 30_000 });
    writeFileSync(join(SAIDA, `${nome}_m3.json`), JSON.stringify({ save: cena.save, rotulo: ROTULO, m3: JSON.parse(await txt.inputValue()) }, null, 1) + "\n");
    await ctx.close();
  });
}
