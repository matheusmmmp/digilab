/* As capturas do saco de pancada na ilha (docs/TAREFA_V3_ITENS_3D.md, secao 12): o saco procedural de antes ("referencia") e o gerado
   ("gerada"), no treino. So roda com DIGILAB_CAPTURAS_ITENS=1 e grava fora do git (o pet e um sprite do UP), em
   DIGILAB_CAPTURAS_ITENS_PASTA (padrao: D:\Trab\digilab\capturas_itens3d\saco\<rotulo>\, com DIGILAB_CAPTURAS_ITENS_ROTULO).
   O save (saves_saco.json, de gerar_saves_saco.mjs) e um Rookie acordado de dia com o treino liberado; o relogio do jogo fica parado.
   Em 1280 px (a aba Treinar abre como painel a direita e a ilha fica atras), por cena (claro e escuro):
     - a ilha parada no Pet, a tela inteira e a M3 do jogo (?medir3d=1, 10 s), para os draw calls (G9);
     - o treino: um clique em Treinar e uma rajada de capturas da ilha durante a ida e os golpes (o saco balanca, gira e amassa). */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const SAVES: Record<string, { semente: number; versao: number; log: unknown[] }> = JSON.parse(readFileSync(new URL("./saves_saco.json", import.meta.url), "utf8"));
const REPO = fileURLToPath(new URL("../../..", import.meta.url)), PREFIXO = `/${basename(REPO)}`, APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const ROTULO = process.env.DIGILAB_CAPTURAS_ITENS_ROTULO ?? "referencia";
const SAIDA = process.env.DIGILAB_CAPTURAS_ITENS_PASTA ?? join("D:\\Trab\\digilab\\capturas_itens3d\\saco", ROTULO);
const W = 1280, H = 800, RAJADA_MS = 3400;
const CENAS: { nome: string; esquema: "light" | "dark" }[] = [{ nome: "claro", esquema: "light" }, { nome: "escuro", esquema: "dark" }];
test.skip(!process.env.DIGILAB_CAPTURAS_ITENS, "so com DIGILAB_CAPTURAS_ITENS=1");

async function abrir(browser: import("@playwright/test").Browser, esquema: "light" | "dark", hash: string) {
  const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: W, height: H }, deviceScaleFactor: 1, colorScheme: esquema });
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
  }, [CHAVE, JSON.stringify(SAVES.dia)] as const);
  await page.goto(APP + "?medir3d=1" + hash);
  await expect(page.locator(".pet-cena .cena3d")).toBeVisible();
  await expect(page.locator("[data-pronto='1']")).toHaveCount(1, { timeout: 30_000 });
  await expect(page.locator("[data-objetos='1']")).toHaveCount(1, { timeout: 30_000 });
  await page.waitForTimeout(1500);
  return { ctx, page };
}

for (const cena of CENAS) {
  test(`captura: o saco (${ROTULO}) parado e a M3, ${cena.nome}`, async ({ browser }) => {
    test.setTimeout(90_000);
    const { ctx, page } = await abrir(browser, cena.esquema, "#/pet");
    mkdirSync(SAIDA, { recursive: true });
    await page.screenshot({ path: join(SAIDA, `saco_${cena.nome}.png`) });
    await page.getByRole("button", { name: /Medir 10 s/ }).evaluate(b => (b as HTMLButtonElement).click());
    const txt = page.getByLabel("Medida M3");
    await expect(txt).toHaveValue(/draw_calls/, { timeout: 30_000 });
    writeFileSync(join(SAIDA, `saco_${cena.nome}_m3.json`), JSON.stringify({ esquema: cena.esquema, rotulo: ROTULO, m3: JSON.parse(await txt.inputValue()) }, null, 1) + "\n");
    await ctx.close();
  });

  test(`captura: o saco (${ROTULO}) no treino, ${cena.nome}`, async ({ browser }) => {
    test.setTimeout(90_000);
    const { ctx, page } = await abrir(browser, cena.esquema, "#/crescer/treinar");
    const dir = join(SAIDA, `treino_${cena.nome}`);
    mkdirSync(dir, { recursive: true });
    await page.locator("button.treino-ex:not(.forcar):not([disabled])").first().click();
    const t0 = Date.now(), tempos: number[] = [];
    while (Date.now() - t0 < RAJADA_MS) {
      const t = Date.now() - t0;
      await page.screenshot({ path: join(dir, `q${String(tempos.length).padStart(2, "0")}_${t}ms.png`), clip: { x: 0, y: 0, width: 760, height: H } });
      tempos.push(t);
    }
    writeFileSync(join(dir, "tempos.json"), JSON.stringify({ rotulo: ROTULO, tempos }) + "\n");
    await ctx.close();
  });
}
