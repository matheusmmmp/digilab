/* As capturas da LP3 no jogo de verdade (docs/TAREFA_V3_LUTA_POC.md, secao 5.1): um pet v21 muito treinado, com as 6 medalhas (o mesmo dos
   torneios da LP2b, test/lp2b_torneios.ts), e o Tamer com as medalhas: a Arena (a escolha do rival e do mapa), a luta dela no palco, a
   Campanha, a Liga dos Lideres no palco (a serie sem cura) e a Fabrica. Desktop (1920 x 950) e celular (390 x 844, 3 px por px de CSS).
   Roda com: npx playwright test -c e2e_capturas/luta_poc_lp3.config.ts luta_poc_lp3_jogo, com DIGILAB_CAPTURAS_LP3=<pasta>. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { petDosTorneios, treinarMuito } from "../test/lp2b_torneios.ts";

const PASTA = process.env.DIGILAB_CAPTURAS_LP3 ?? "";
const CHAVE = "digilab-web-v21-sprites";
const MEDALHAS6 = ["campina", "torre", "floresta", "cidadela", "lago", "espiral"];
const TELAS = [{ nome: "1920", w: 1920, h: 950, dpr: 1 }, { nome: "390", w: 390, h: 844, dpr: 3 }].filter(t => !process.env.DIGILAB_LP3_TELA || process.env.DIGILAB_LP3_TELA === t.nome);
const PELES = (process.env.DIGILAB_LP3_PELES ?? "vidro").split(",");

let save = "";
function saveDoPet(): string {
  if (save) return save;
  const m = petDosTorneios(101); treinarMuito(m, 1500);
  if (m.lesionadoDesde !== null) m.observar("tratar_lesao");
  return save = JSON.stringify({ semente: m.semente, versao: m.versao, log: m.log });
}
async function semear(page: Page): Promise<void> {
  const s = saveDoPet(), tamer = JSON.stringify({ versao: 7, log: MEDALHAS6.map((id, i) => ["medalha", { id, n: i + 1, quando: 1, pet: 101, forma: "Garurumon", tick: 480 }]) });
  await page.goto("/motor/index.ts");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-descarte", "7"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]"); localStorage.setItem(chave, s);
  }, [CHAVE, s, tamer] as const);
}
const foto = (page: Page, nome: string) => page.screenshot({ path: join(PASTA, nome + ".png") });
/** espera a condicao sobre o dataset do canvas (d) e tira a foto */
async function momento(page: Page, nome: string, cond: string, timeout = 120_000): Promise<void> {
  await page.waitForFunction((c: string) => { const cv = document.querySelector("[data-testid=poc-canvas]") as HTMLElement | null; return !!cv && new Function("d", `return (${c})`)(cv.dataset); }, cond, { timeout, polling: "raf" });
  await foto(page, nome);
}
const fim = async (page: Page, nome: string) => { await expect(page.getByTestId("poc-resultado")).toBeVisible({ timeout: 240_000 }); await foto(page, nome); await page.getByTestId("poc-resultado").getByRole("button").click(); };

for (const t of TELAS) for (const pele of PELES) {
  test(`LP3 no jogo ${t.nome} ${pele}`, async ({ browser }) => {
    test.skip(!PASTA, "so com DIGILAB_CAPTURAS_LP3");
    test.setTimeout(900_000);
    mkdirSync(PASTA, { recursive: true });
    const ctx = await browser.newContext({ viewport: { width: t.w, height: t.h }, deviceScaleFactor: t.dpr }), page = await ctx.newPage();
    const erros: string[] = []; page.on("pageerror", e => erros.push(String(e)));
    const n = (x: string) => `lp3_jogo_${t.nome}_${pele === "xcom" ? "militar" : "vidro"}_${x}`;
    await semear(page);
    /* a Arena: a escolha do rival (o Gabumon, o do projetil nosso) e do mapa (a Floresta) */
    await page.goto(`/?luta_poc=1&pele=${pele}#/lutar/arena`);
    await expect(page.getByTestId("poc-arena")).toBeVisible({ timeout: 60_000 });
    const rival = page.locator("[data-testid^=poc-rival-]").nth(1); await rival.click();
    await page.getByTestId("poc-mapa-floresta").click();
    await foto(page, n("1_arena_escolha"));
    await page.getByTestId("poc-lutar").click();
    await momento(page, n("2_arena_luta"), "+d.impactos > 0 || +d.projeteisDesenho > 0");
    await fim(page, n("3_arena_resultado"));
    /* a Campanha */
    await page.goto(`/?luta_poc=1&pele=${pele}#/lutar/campanha`);
    await expect(page.getByTestId("poc-campanha")).toBeVisible({ timeout: 60_000 });
    await foto(page, n("4_campanha"));
    /* a Liga dos Lideres: a serie de 6, sem cura */
    await page.goto(`/?luta_poc=1&pele=${pele}#/lutar/fronteira`);
    await page.getByRole("button", { name: /Desafiar a Liga/ }).click();
    await page.waitForFunction(() => /Luta 3 de 6/.test(document.querySelector(".luta-modo")?.textContent ?? ""), null, { timeout: 240_000 });
    await momento(page, n("5_liga_luta3"), "+d.impactos > 0 || +d.projeteisDesenho > 0 || +d.nossos > 0");
    await fim(page, n("6_liga_resultado"));
    /* a Liga vencida conclui a jornada: o cartao "Campeao!" sai (continua com o pet), e a Fronteira abre de novo */
    const seguir = page.getByRole("button", { name: /Continuar com/ });
    if (await seguir.isVisible({ timeout: 5_000 }).catch(() => false)) await seguir.click();
    await page.goto(`/?luta_poc=1&pele=${pele}#/lutar/fronteira`);
    await page.reload();
    /* a Fabrica: aluga o primeiro e luta */
    const fb = page.locator(".fr-inst-card", { hasText: "Fábrica" });
    await fb.getByRole("button", { name: /Tentar/ }).click();
    await fb.locator("button").first().click();
    await fb.getByRole("button", { name: /Lutar/ }).click();
    await momento(page, n("7_fabrica_luta"), "+d.impactos > 0 || +d.projeteisDesenho > 0");
    await fim(page, n("8_fabrica_resultado"));
    await foto(page, n("9_fronteira"));
    expect(erros).toEqual([]);
    await ctx.close();
  });
}
