/* LUTA_EFEITOS, E1, o impacto (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4 e 7): a luta mostra a tremida do palco num acerto, e com
   prefers-reduced-motion nao mostra (o canvas expoe data-tremida-max e data-impactos so para este teste). Com DIGILAB_CAPTURAS_E1=<pasta>
   grava tambem as capturas do PR (um acerto em tela, 390 e 1280 px, vidro e xcom) e os quadros de um acerto para o GIF. */
import { expect, test, type Page } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXO = "/" + basename(fileURLToPath(new URL("../../..", import.meta.url)));
const APP = `${PREFIXO}/web/dist/`, CHAVE = "digilab-web-v21-sprites";
const PASTA = process.env.DIGILAB_CAPTURAS_E1 ?? "";
const SAVE = { semente: 101, versao: 13, log: [[480, "u", { n: 1 }], [480, "t", 210]] };
const TAMER = { versao: 7, log: [["medalha", { id: "campina", n: 1, quando: 1, pet: 101, forma: "Agumon", tick: 480 }]] };

async function abrirLuta(page: Page, pele: string): Promise<void> {
  await page.goto("/Assets/digilab_atlas_up.json");
  await page.evaluate(([chave, s, t]) => {
    localStorage.clear(); localStorage.setItem(chave + "-boas-vindas", "1"); localStorage.setItem(chave + "-tamer", t);
    localStorage.setItem(chave + "-descarte", "6"); localStorage.setItem(chave + "-dicas-ligadas", "0"); localStorage.setItem(chave + "-guardados", "[]");
    localStorage.setItem(chave, s);
  }, [CHAVE, JSON.stringify(SAVE), JSON.stringify(TAMER)] as const);
  await page.goto(`${APP}?pele=${pele}&clipes_up=1#/lutar/arena`);
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
  await expect(page.getByTestId("luta-relogio")).toHaveText(/^0:0[1-9]$/, { timeout: 10_000 });
}
/** espera o primeiro acerto e devolve o maior valor de tremida visto ate la */
const esperarAcerto = (page: Page) => page.waitForFunction(() => Number((document.querySelector(".arena-cv") as HTMLElement).dataset.impactos ?? 0) > 0, null, { timeout: 90_000, polling: 16 });

test("sem movimento reduzido, o acerto treme o palco", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await abrirLuta(page, "vidro");
  await esperarAcerto(page);
  await expect.poll(() => page.locator(".arena-cv").evaluate(c => Number((c as HTMLElement).dataset.tremidaMax ?? 0))).toBeGreaterThan(0);
});

test("com prefers-reduced-motion nao ha tremida, mas o acerto acontece", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 1280, height: 720 });
  await abrirLuta(page, "vidro");
  await esperarAcerto(page);
  await page.waitForTimeout(1500);
  expect(await page.locator(".arena-cv").evaluate(c => (c as HTMLElement).dataset.tremidaMax)).toBe("0");
  expect(await page.locator(".arena-cv").evaluate(c => (c as HTMLElement).dataset.tremida)).toBe("0,0");
});

test.describe("capturas da E1", () => {
  test.skip(!PASTA, "so com DIGILAB_CAPTURAS_E1");
  for (const pele of ["vidro", "xcom"]) for (const [w, h] of [[390, 844], [1280, 720]] as const) test(`acerto em tela: ${pele} ${w}`, async ({ page }) => {
    await page.setViewportSize({ width: w, height: h });
    await abrirLuta(page, pele);
    mkdirSync(PASTA, { recursive: true });
    const nome = `luta_e1_${w}_${pele === "xcom" ? "militar" : "vidro"}`;
    /* o screencast do Chrome (CDP) entrega os quadros da tela inteira a ~30 por segundo, sem o custo de um screenshot por quadro: grava os
       quadros ate 5 s depois do primeiro acerto; a escolha do melhor acerto e a montagem do GIF ficam fora do teste */
    const cdp = await page.context().newCDPSession(page);
    let n = 0; const gravar = async (ev: { data: string; sessionId: number }) => {
      writeFileSync(join(PASTA, `${nome}_f${String(n++).padStart(3, "0")}.jpg`), Buffer.from(ev.data, "base64")); await cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId });
    };
    cdp.on("Page.screencastFrame", gravar);
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, everyNthFrame: 1 });
    await esperarAcerto(page);
    await page.waitForTimeout(5000);
    await cdp.send("Page.stopScreencast");
    expect(n).toBeGreaterThan(20);
  });
});
