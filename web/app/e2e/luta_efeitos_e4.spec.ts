/* LUTA_EFEITOS, E4, as posturas como efeito (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 7).
   O Gabumon v18 contra o Zudomon (o Vigia): o Gabumon carrega (a aura e o icone do carregar) e o Zudomon usa a pele dura (o brilho e o icone).
   O icone e um desenho em pixel no canvas, com um elemento transparente por cima que leva o nome no title e no leitor de tela. Com
   prefers-reduced-motion os icones continuam, sem tremida e sem o escudo aceso nem o clarao do contra-golpe. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
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
  await page.locator(".rivais-mais").click();
  await page.locator(".rival-card--adulto", { hasText: "Zudomon" }).click();
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
}
const esperar = (page: Page, campo: string) => page.waitForFunction((c) => Number((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset[c] ?? 0) > 0, campo, { timeout: 120_000, polling: "raf" });

test("o carregar e a pele dura aparecem como efeito, com o icone nomeado no title e no leitor de tela", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await abrirLuta(page);
  await esperar(page, "auras");
  /* o icone do carregar do Gabumon: o nome no title e no aria-label, sobre o canvas */
  const carregar = page.getByRole("img", { name: "Gabumon: carregar" });
  await expect(carregar).toBeVisible();
  await expect(carregar).toHaveAttribute("title", "Gabumon: carregar");
  await esperar(page, "peles");
  await page.waitForFunction(() => ((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset.posturas ?? "").includes("pele_dura"), null, { timeout: 120_000, polling: "raf" });
  /* a etiqueta de texto de antes nao existe mais: so o icone (o nome so no title) */
  await expect(page.locator('.luta-postura[data-postura="pele_dura"]')).toHaveAttribute("title", /pele dura/);
});

test("com prefers-reduced-motion os icones ficam, sem tremida, escudo aceso nem clarao", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await abrirLuta(page);
  await esperar(page, "auras");
  await expect(page.locator(".luta-postura:not([hidden])").first()).toHaveAttribute("title", /: /);
  await esperar(page, "peles");
  const cv = page.locator(".arena-cv");
  expect(await cv.evaluate(c => (c as HTMLElement).dataset.tremidaMax ?? "0")).toBe("0");
  expect(await cv.evaluate(c => (c as HTMLElement).dataset.escudosAcesos ?? "0")).toBe("0");
  expect(await cv.evaluate(c => (c as HTMLElement).dataset.claroes ?? "0")).toBe("0");
});
