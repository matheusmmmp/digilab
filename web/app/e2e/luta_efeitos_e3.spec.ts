/* LUTA_EFEITOS, E3, a telegrafia e o chao (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 7).
   O Zudomon (o Vigia, rival adulto) prepara o pesado contra o Gabumon: a elipse aparece no palco (data-telegrafias) e, no acerto, a onda e a
   marca no piso (data-ondas, data-marcas). Com prefers-reduced-motion a elipse continua aparecendo, sem a tremida e sem poeira. */
import { expect, test, type Page } from "@playwright/test";
import { basename } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
/* o Gabumon v18 do GIF do empurrao, contra o Zudomon (o card do Vigia entre os rivais adultos). O Monochromon tambem prepara o pesado, mas
   derruba o Gabumon antes de o pesado acertar; os bots e o MetalGreymon e o Paildramon nao chegam a acertar um pesado na mesma luta */
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
  /* o Zudomon fica entre as formas adultas escondidas: o botao "+ N formas adultas" mostra todas */
  await page.locator(".rivais-mais").click();
  await page.locator(".rival-card--adulto", { hasText: "Zudomon" }).click();
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
}
const esperar = (page: Page, campo: string) => page.waitForFunction((c) => Number((document.querySelector(".arena-cv") as HTMLElement | null)?.dataset[c] ?? 0) > 0, campo, { timeout: 120_000, polling: "raf" });

test("a elipse do pesado, a onda e a marca no piso aparecem no palco", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await abrirLuta(page);
  await esperar(page, "telegrafias");
  await esperar(page, "ondas");
  await esperar(page, "marcas");
});

test("com prefers-reduced-motion a elipse continua aparecendo, sem tremida nem poeira", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await abrirLuta(page);
  await esperar(page, "telegrafias");
  const cv = page.locator(".arena-cv");
  expect(await cv.evaluate(c => (c as HTMLElement).dataset.tremidaMax ?? "0")).toBe("0");
  expect(await cv.evaluate(c => (c as HTMLElement).dataset.poeiras ?? "0")).toBe("0");
});
