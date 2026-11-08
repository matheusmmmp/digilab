/* O cartao "O que [pet] faz" no celular (D-LE-E3-1; decisao do Matheus de 2026-11-07, faixa no alto): a 390 x 844 e a 375 x 667, nas duas
   peles, a faixa da regra fica sob o contexto e acima da cabeca mais alta que um lutador pode ter sem zoom, longe dos pes, da elipse e das
   marcas do piso. A linha dos pes e 0,8 da altura do palco (geometriaTR) e o sprite sem zoom tem no maximo 0,45 da altura (escalaBaseTR), entao
   a faixa inteira tem de ficar acima de 0,35 da altura; e o chao (pes, elipse, onda e marcas), que fica de 0,8 para baixo, fica livre. A 390 px
   a camera nao aproxima (D-LE-E5-2). Confere tambem que a faixa nao cobre o HUD nem o contexto, e que o texto da regra continua inteiro. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* o Rookie v13 da luta em tempo real (como em luta_layout.spec.ts) */
const SAVE = { semente: 101, versao: 13, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };
const PES = .8, ALTURA_MAX = .45;

async function abrirLuta(page: Page, pele: string): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE), JSON.stringify(TAMER)] as const);
  await page.goto(`${APP}?pele=${pele}#/lutar/arena`);
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
  await expect(page.getByTestId("luta-relogio")).toHaveText(/^0:0[1-9]$/, { timeout: 10_000 });
}
/** os retangulos que importam: o palco (canvas), a faixa da regra, o HUD e o contexto */
const medir = (page: Page) => page.evaluate(() => {
  const r = (s: string) => { const b = document.querySelector(s)!.getBoundingClientRect(); return { top: b.top, bottom: b.bottom, left: b.left, right: b.right }; };
  const txt = document.querySelector("[data-testid=luta-regra]") as HTMLElement;
  return { cv: r(".luta-arena--tr"), card: r(".luta-card"), hud: r(".luta-hud"), ctx: r(".luta-contexto"), inteiro: (() => { const t = txt.getBoundingClientRect(), c = document.querySelector(".luta-card")!.getBoundingClientRect(); return t.height > 0 && t.top >= c.top && t.bottom <= c.bottom + .5 && t.right <= c.right + .5; })() };
});

for (const pele of ["vidro", "xcom"]) for (const [w, h] of [[390, 844], [375, 667]] as const) {
  test(`a faixa da regra nao cobre os pes nem o chao: ${pele} ${w}x${h}`, async ({ page }) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele);
    /* seis amostras com a luta andando (a linha do turno aparece e some) */
    for (let k = 0; k < 6; k++) {
      const m = await medir(page), alt = m.cv.bottom - m.cv.top, pes = m.cv.top + PES * alt, cabeca = pes - ALTURA_MAX * alt;
      expect(m.cv.top).toBeLessThanOrEqual(0); expect(m.cv.bottom).toBeGreaterThanOrEqual(h);
      expect(m.card.bottom, `faixa (${m.card.bottom}) acima da cabeca mais alta (${cabeca})`).toBeLessThanOrEqual(cabeca);
      expect(m.card.bottom).toBeLessThan(pes);
      expect(m.card.top, "a faixa fica sob o contexto").toBeGreaterThanOrEqual(m.ctx.bottom);
      expect(m.ctx.top, "o contexto fica sob o HUD").toBeGreaterThanOrEqual(m.hud.bottom);
      expect(m.card.left).toBeGreaterThanOrEqual(0); expect(m.card.right).toBeLessThanOrEqual(w);
      expect(m.inteiro, "o texto da regra cabe inteiro na faixa").toBe(true);
      await page.waitForTimeout(400);
    }
    await expect(page.getByTestId("luta-regra")).not.toBeEmpty();
  });
}
