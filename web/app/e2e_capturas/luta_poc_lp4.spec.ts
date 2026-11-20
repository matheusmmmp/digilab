/* As capturas da LP4 (docs/TAREFA_V3_LUTA_POC.md, secao 5.1): a chave ligada para todos, sem ?luta_poc=1. Desktop (1920 x 950) e celular
   (390 x 844, 3 px por px de CSS), nas peles Vidro e Militar:
     1. o aviso do descarte (um pet v19 de antes no save, e o Tamer com uma medalha);
     2. o ovo novo v21, depois do brasao (o save gravado e conferido: versao 21);
     3. a Arena da luta nova (um Rookie v21) e a luta dela no palco.
   Roda com: npx playwright test -c e2e_capturas/luta_poc_lp4.config.ts, com DIGILAB_CAPTURAS_LP4=<pasta>. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const PASTA = process.env.DIGILAB_CAPTURAS_LP4 ?? "";
const CHAVE = "digilab-web-v21-sprites";
const TELAS = [{ nome: "1920", w: 1920, h: 950, dpr: 1 }, { nome: "390", w: 390, h: 844, dpr: 3 }];
const PELES = ["vidro", "xcom"];
const ANTIGO_V19 = { semente: 6100, versao: 19, log: [[480, "t", 300], [780, "d", "acariciar"], [780, "t", 120]] };
const TAMER_1 = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 6100, forma: "Agumon", tick: 900 }]] };
/* um Rookie v21 que conhece a primeira medalha, com a progressao do Lutar aberta (os marcos 1 a 4) */
const ROOKIE_V21 = { semente: 101, versao: 21, log: [[480, "u", { n: 1 }], [480, "t", 210]] };

async function semear(page: Page, save: object, tamer: object, descarte: string | null, nivel: object | null): Promise<void> {
  await page.goto("/motor/index.ts");
  await page.evaluate(([c, s, t, d, n]) => {
    localStorage.clear(); localStorage.setItem(c + "-boas-vindas", "1"); localStorage.setItem(c + "-dicas-ligadas", "0");
    localStorage.setItem(c, s); localStorage.setItem(c + "-guardados", "[]"); localStorage.setItem(c + "-tamer", t);
    if (d) localStorage.setItem(c + "-descarte", d);
    if (n) localStorage.setItem(c + "-nivel", n);
  }, [CHAVE, JSON.stringify(save), JSON.stringify(tamer), descarte, nivel ? JSON.stringify(nivel) : null] as const);
}

for (const t of TELAS) for (const pele of PELES) {
  test(`LP4 ${t.nome} ${pele}`, async ({ browser }) => {
    test.skip(!PASTA, "so com DIGILAB_CAPTURAS_LP4");
    test.setTimeout(300_000);
    mkdirSync(PASTA, { recursive: true });
    const ctx = await browser.newContext({ viewport: { width: t.w, height: t.h }, deviceScaleFactor: t.dpr }), page = await ctx.newPage();
    const erros: string[] = [];
    page.on("pageerror", e => erros.push(String(e)));
    page.on("console", m => { if (m.type() === "error" && !/favicon\.ico$|\/api\//.test(m.location().url ?? "")) erros.push("console: " + m.text()); });
    const foto = (x: string) => page.screenshot({ path: join(PASTA, `lp4_${t.nome}_${pele === "xcom" ? "militar" : "vidro"}_${x}.png`) });

    /* 1. o aviso do descarte: o pet v19 sai, sem ?luta_poc=1 */
    await semear(page, ANTIGO_V19, TAMER_1, "6", null);
    await page.goto(`/?pele=${pele}#/pet/estado`);
    const aviso = page.locator("dialog.aviso-poc[open]");
    await expect(aviso).toContainText("A luta agora é na arena");
    await page.waitForTimeout(800);
    await foto("1_aviso_descarte");

    /* 2. o ovo novo v21: o brasao e o ovo chocando na tela Pet */
    await aviso.getByRole("button", { name: "Escolher o brasão do ovo novo" }).click();
    await page.locator("dialog.brasao-tela[open] .br-card").first().click();
    await expect(page.locator("dialog.brasao-tela[open]")).toHaveCount(0);
    const save = await page.evaluate(c => JSON.parse(localStorage.getItem(c)!) as { versao: number; semente: number }, CHAVE);
    expect(save.versao).toBe(21);
    expect(save.semente).not.toBe(ANTIGO_V19.semente);
    expect(await page.evaluate(c => localStorage.getItem(c + "-descarte"), CHAVE)).toBe("8");
    await page.waitForTimeout(1500);
    await foto("2_ovo_v21");

    /* 3. a Arena da luta nova e a luta no palco (sem ?luta_poc=1) */
    await semear(page, ROOKIE_V21, TAMER_1, "8", { marcos: [1, 2, 3, 4, 5], cartoes: [1, 2, 3, 4, 5] });
    await page.goto(`/?pele=${pele}#/lutar/arena`);
    await expect(page.getByTestId("poc-arena")).toBeVisible({ timeout: 60_000 });
    await page.getByTestId("poc-mapa-floresta").click();
    await page.waitForTimeout(800);
    await foto("3_arena");
    await page.getByTestId("poc-lutar").click();
    await expect(page.getByTestId("luta-poc")).toBeVisible();
    await page.waitForFunction(() => { const cv = document.querySelector("[data-testid=poc-canvas]") as HTMLElement | null; return !!cv && (+(cv.dataset.impactos ?? 0) > 0 || +(cv.dataset.projeteisDesenho ?? 0) > 0); }, null, { timeout: 120_000 });
    await foto("4_arena_luta");
    await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 180_000 });
    await foto("5_arena_resultado");
    const l = await page.evaluate(c => (JSON.parse(localStorage.getItem(c)!) as { log: [number, string, { m?: string }][] }).log.filter(e => e[1] === "l"), CHAVE);
    expect(l.length).toBe(1); expect(l[0][2].m).toBe("floresta");
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
