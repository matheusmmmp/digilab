/* LUTA_EFEITOS, E5, o nocaute e a camera (docs/TAREFA_V3_LUTA_EFEITOS.md, secoes 3.4, 3.5 e 7).
   O Monochromon derruba o Gabumon v18 (o mesmo save da E3): a barra mostra o pedaco atrasado (luta-atraso-*), o palco escurece e o "K.O." sai
   no canvas (data-escuro, data-ko), com o texto para o leitor de tela; em 1280 px a camera chega perto, com o sprite em escala inteira maior
   que a de sempre (data-zoom, data-esc). Com prefers-reduced-motion o "K.O." e a barra continuam, sem tremida, e o "K.O." ja sai no tamanho
   final (sem o encolher). */
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
  /* o Monochromon (o agressivo) e o rival que ja vem escolhido */
  await expect(page.getByRole("radio", { name: /Monochromon/ })).toBeChecked();
  await page.locator(".lutar-grande").click();
  await expect(page).toHaveURL(/#\/lutar\/luta$/);
}
/** acompanha o palco a cada quadro ate o "K.O." ficar no tamanho final; devolve o que se viu */
const acompanhar = (page: Page) => page.evaluate(() => new Promise<{ atraso: boolean; branco: boolean; zoomMax: number; escs: number[]; kos: number[]; escuroMax: number; tremidaMax: number }>((res, rej) => {
  const r = { atraso: false, branco: false, zoomMax: 1, escs: [] as number[], kos: [] as number[], escuroMax: 0, tremidaMax: 0 }, t0 = performance.now();
  const f = () => {
    const cv = document.querySelector(".arena-cv") as HTMLElement | null;
    if (!cv) { rej(new Error("o palco sumiu antes do K.O.")); return; }
    const d = cv.dataset;
    if (document.querySelector("[data-testid^=luta-atraso-]")) r.atraso = true;
    if (document.querySelector(".hud-vida-atraso--branco")) r.branco = true;
    r.zoomMax = Math.max(r.zoomMax, Number(d.zoom ?? 1)); if (!r.escs.includes(Number(d.esc))) r.escs.push(Number(d.esc));
    r.escuroMax = Math.max(r.escuroMax, Number(d.escuro ?? 0)); r.tremidaMax = Math.max(r.tremidaMax, Number(d.tremidaMax ?? 0));
    if (d.ko) r.kos.push(Number(d.ko));
    if (r.kos.length >= 12) { res(r); return; }
    if (performance.now() - t0 > 150_000) { rej(new Error("sem K.O. em 150 s")); return; }
    requestAnimationFrame(f);
  };
  f();
}));

test("o nocaute: a barra atrasada, o escuro, o K.O. e a camera que chega perto", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await abrirLuta(page);
  const r = await acompanhar(page);
  expect(r.atraso).toBe(true); expect(r.branco).toBe(true);
  expect(r.escuroMax).toBeGreaterThan(0); expect(r.kos[0]).toBeGreaterThan(r.kos[r.kos.length - 1]);
  expect(r.zoomMax).toBeGreaterThan(1); for (const e of r.escs) expect(Number.isInteger(e)).toBe(true);
  expect(Math.max(...r.escs)).toBeGreaterThan(Math.min(...r.escs));
  await expect(page.getByRole("status").filter({ hasText: "NOCAUTE!" })).toBeAttached();
});

test("com prefers-reduced-motion o K.O. e a barra ficam, sem tremida e sem o K.O. encolher", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await abrirLuta(page);
  const r = await acompanhar(page);
  expect(r.atraso).toBe(true); expect(r.escuroMax).toBeGreaterThan(0); expect(r.tremidaMax).toBe(0);
  expect(new Set(r.kos).size).toBe(1);
});
