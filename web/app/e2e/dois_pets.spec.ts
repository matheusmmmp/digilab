/* Os dois pets no jogo (docs/TAREFA_V3_COOPERACAO.md, etapa CO4d), a 390 e a 1280 px: do primeiro acesso ao brasao, os dois ovos chocam juntos
   (o save e o do grupo, v26), os dois pets aparecem na ilha, o retrato do irmao fica no topo e o toque nele troca o pet em foco (quem a tela
   mostra e quem recebe a acao do dono), o foco fica no save e volta ao reabrir, e a acao do dono vai ao pet em foco. Sem erro no console. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";

function vigiarErros(page: Page): string[] {
  const erros: string[] = [];
  page.on("pageerror", e => erros.push("pageerror: " + e.message));
  page.on("console", m => {
    if (m.type() !== "error") return;
    const url = m.location().url ?? "";
    /* o favicon da pagina de semear e o servidor local da fala (fora do e2e: 502 no /api) nao sao do app */
    if (/favicon\.ico$/.test(url) || /\/api\//.test(url) || /502|Bad Gateway/.test(m.text())) return;
    erros.push("console: " + m.text() + (url ? ` (${url})` : ""));
  });
  return erros;
}

const lerSave = (page: Page) => page.evaluate(c => JSON.parse(localStorage.getItem(c) ?? "null"), CHAVE) as Promise<{ versao: number; grupo?: boolean; foco?: string; log: unknown[][] } | null>;

for (const [largura, altura] of [[390, 844], [1280, 800]] as const) {
  test(`os dois ovos chocam juntos, o irmao fica no topo e o foco troca, ${largura} px`, async ({ browser }) => {
    const ctx = await browser.newContext({ baseURL: test.info().project.use.baseURL, viewport: { width: largura, height: altura } });
    const page = await ctx.newPage(), erros = vigiarErros(page);
    await page.goto("/Assets/digilab_atlas_up.json");
    await page.evaluate(c => { localStorage.clear(); localStorage.setItem(c + "-dicas-ligadas", "0"); }, CHAVE);
    await page.goto(APP + "#/inicio");
    await page.getByRole("button", { name: /começar/i }).click();
    /* o "Como jogar" pode vir antes do brasao (no celular, depois do Comecar): pula ate o brasao abrir */
    const brasao = page.locator("dialog.brasao-tela[open]"), pular = page.getByRole("button", { name: /^pular$/i });
    await expect(brasao.or(pular).first()).toBeVisible({ timeout: 20_000 });
    for (let k = 0; k < 3 && !(await brasao.isVisible()); k++) {
      if (await pular.isVisible()) await pular.click();
      await expect(brasao.or(pular).first()).toBeVisible({ timeout: 20_000 });
    }
    await brasao.locator(".br-card").first().click();
    await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);

    /* os dois ovos: o save do grupo, v36, com o primeiro em foco */
    await expect.poll(async () => (await lerSave(page))?.grupo).toBe(true);
    const s = (await lerSave(page))!;
    expect([s.versao, s.foco]).toEqual([36, "A"]);   // a v29 desde a LP6-4; a v31 (com o lance) desde a BB2; a v36 (a v31 com a TV) desde a TV no jogo
    const g = await page.evaluate(() => (window as unknown as { __digilab: { grupo(): { ids: string[]; foco: string; ticks: number[] } } }).__digilab.grupo());
    expect(g.ids).toEqual(["A", "B"]);
    expect(g.ticks[0]).toBe(g.ticks[1]);

    /* o retrato do irmao no topo; o toque troca o foco, e o foco fica no save */
    const irmao = page.getByRole("button", { name: /^Ver / });
    await expect(irmao).toBeVisible({ timeout: 20_000 });
    await irmao.click();
    await expect.poll(async () => (await lerSave(page))?.foco).toBe("B");
    await expect(page.getByRole("button", { name: /^Ver / })).toBeVisible();

    /* a acao do dono vai ao pet em foco: a racao no comedouro (o "dc") entra no registro do grupo com o B */
    /* o ovo chocou (o tempo so anda depois): antes disso a acao do dono nao vale */
    await expect.poll(async () => page.evaluate(() => (window as unknown as { __digilab: { tick(): number } }).__digilab.tick()), { timeout: 30_000 }).toBeGreaterThan(480);
    await page.getByRole("button", { name: /^Alimentar/ }).first().click();
    await expect.poll(async () => (await lerSave(page))!.log.filter(e => e[1] === "dc" && e[3] === "B").length).toBeGreaterThan(0);
    expect((await lerSave(page))!.log.filter(e => e[1] === "dc" && e[3] === "A")).toEqual([]);

    /* reabrir: o mesmo grupo, o mesmo foco */
    await page.reload();
    await expect.poll(async () => page.evaluate(() => (window as unknown as { __digilab: { grupo(): { foco: string } | null } }).__digilab.grupo()?.foco)).toBe("B");
    await expect(page.getByRole("button", { name: /^Ver / })).toBeVisible({ timeout: 20_000 });
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
