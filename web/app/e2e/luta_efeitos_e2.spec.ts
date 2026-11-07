/* LUTA_EFEITOS, E2, os projeteis por elemento (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 7).
   O disparo do Tankmon (o bot atirador) contra o Gabumon aparece no palco (o canvas expoe data-projeteis, as cabecas desenhadas no quadro),
   e com prefers-reduced-motion continua aparecendo, sem a tremida (o circulo antigo podia nao sair em nenhum quadro). */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* o Gabumon v18 do GIF do empurrao, contra o Tankmon (o 4o card dos bots classicos: RIVAIS_CLASSICOS em src/luta.ts) */
const SAVE = { semente: 101, versao: 18, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };

async function abrirLuta(page: Page): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE), JSON.stringify(TAMER)] as const);
  await page.goto(`${APP}?clipes_up=1#/lutar/arena`);
  await page.locator(".rival-card:not(.rival-card--adulto)").nth(3).click();
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
}
const esperarProjetil = (page: Page) => page.waitForFunction(() => Number((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset.projeteis ?? 0) > 0, null, { timeout: 120_000, polling: "raf" });

test("o disparo aparece no palco", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await abrirLuta(page);
  await esperarProjetil(page);
});

test("com prefers-reduced-motion o disparo continua aparecendo, sem tremida", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await abrirLuta(page);
  await esperarProjetil(page);
  expect(await page.locator(".arena-cv").evaluate(c => (c as HTMLElement).dataset.tremidaMax ?? "0")).toBe("0");
});
